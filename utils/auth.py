"""
Authentication system for the Graduation Attendance System
Handles both staff and student authentication
"""
import streamlit as st
import hashlib
import time
from datetime import datetime
import os
from core.database import load_database, get_student_by_id

class AuthManager:
    """Central authentication manager for the dual-portal system"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def init_session_states():
        """Initialize authentication-related session states"""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user_type" not in st.session_state:
            st.session_state.user_type = None
        if "student_id" not in st.session_state:
            st.session_state.student_id = None
        if "user_name" not in st.session_state:
            st.session_state.user_name = None
        if "login_time" not in st.session_state:
            st.session_state.login_time = None
    
    @staticmethod
    def staff_login(password):
        """
        Authenticate staff user
        Returns: (success: bool, message: str)
        """
        try:
            # Get staff password from Streamlit secrets or environment
            staff_password = st.secrets.get("staff_password", os.getenv("STAFF_PASSWORD", "admin123"))
            
            if password == staff_password:
                st.session_state.authenticated = True
                st.session_state.user_type = "staff"
                st.session_state.user_name = "Staff"
                st.session_state.login_time = datetime.now()
                return True, "Staff authentication successful!"
            else:
                return False, "Invalid staff password"
                
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    
    @staticmethod
    def student_login(student_id, password=None):
        """
        Authenticate student user
        Args:
            student_id: Student ID
            password: Optional password (can be None for ID-only login)
        Returns: (success: bool, message: str, student_data: dict)
        """
        try:
            # Check if student exists in database
            student = get_student_by_id(student_id)
            
            if not student:
                return False, f"Student ID '{student_id}' not found in database", None
            
            # For now, allow login with just valid student ID
            # In future, can add password requirement
            if password is not None:
                stored_hash = student.get('password_hash')
                if stored_hash and not AuthManager.verify_password(password, stored_hash):
                    return False, "Invalid password", None
            
            # Successful login
            st.session_state.authenticated = True
            st.session_state.user_type = "student"
            st.session_state.student_id = student_id
            st.session_state.user_name = student.get('name', 'Student')
            st.session_state.login_time = datetime.now()
            
            return True, f"Welcome back, {student.get('name', 'Student')}!", student
            
        except Exception as e:
            return False, f"Login error: {str(e)}", None
    
    @staticmethod
    def logout():
        """Clear authentication session"""
        st.session_state.authenticated = False
        st.session_state.user_type = None
        st.session_state.student_id = None
        st.session_state.user_name = None
        st.session_state.login_time = None
    
    @staticmethod
    def is_authenticated():
        """Check if user is authenticated"""
        return st.session_state.get("authenticated", False)
    
    @staticmethod
    def get_user_type():
        """Get current user type"""
        return st.session_state.get("user_type")
    
    @staticmethod
    def require_authentication(required_type=None):
        """
        Decorator/helper to require authentication
        Args:
            required_type: "staff" or "student" or None (any authenticated user)
        Returns: bool - True if authorized, False otherwise
        """
        if not AuthManager.is_authenticated():
            return False
        
        if required_type and st.session_state.user_type != required_type:
            return False
            
        return True
    
    @staticmethod
    def get_session_info():
        """Get current session information"""
        if not AuthManager.is_authenticated():
            return None
        
        return {
            "user_type": st.session_state.user_type,
            "user_name": st.session_state.user_name,
            "student_id": st.session_state.get("student_id"),
            "login_time": st.session_state.get("login_time"),
            "session_duration": (datetime.now() - st.session_state.login_time).seconds if st.session_state.get("login_time") else 0
        }
    
    @staticmethod
    def session_timeout_check(timeout_minutes=30):
        """
        Check if session has timed out
        Args:
            timeout_minutes: Session timeout in minutes
        Returns: bool - True if session is still valid
        """
        if not st.session_state.get("login_time"):
            return False
        
        session_age = (datetime.now() - st.session_state.login_time).seconds
        if session_age > timeout_minutes * 60:
            AuthManager.logout()
            return False
        
        return True

# Rate limiting for security
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        if "rate_limit_data" not in st.session_state:
            st.session_state.rate_limit_data = {}
    
    def is_rate_limited(self, key, max_attempts=5, window_minutes=15):
        """
        Check if key is rate limited
        Args:
            key: Unique identifier (IP, student_id, etc.)
            max_attempts: Maximum attempts allowed
            window_minutes: Time window in minutes
        Returns: (is_limited: bool, remaining_attempts: int)
        """
        current_time = time.time()
        window_seconds = window_minutes * 60
        
        if key not in st.session_state.rate_limit_data:
            st.session_state.rate_limit_data[key] = []
        
        # Clean old attempts
        attempts = st.session_state.rate_limit_data[key]
        attempts = [t for t in attempts if current_time - t < window_seconds]
        st.session_state.rate_limit_data[key] = attempts
        
        remaining = max(0, max_attempts - len(attempts))
        is_limited = len(attempts) >= max_attempts
        
        return is_limited, remaining
    
    def record_attempt(self, key):
        """Record an attempt for the given key"""
        current_time = time.time()
        
        if key not in st.session_state.rate_limit_data:
            st.session_state.rate_limit_data[key] = []
        
        st.session_state.rate_limit_data[key].append(current_time)

# Global rate limiter instance
rate_limiter = RateLimiter()