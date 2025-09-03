"""
Session state management for the Graduation Attendance System
"""
import streamlit as st

class SessionManager:
    """Centralized session state management"""
    
    @staticmethod
    def init_all_states():
        """Initialize all session states in one place"""
        
        # Single source of truth for camera captures
        if 'capture_state' not in st.session_state:
            st.session_state.capture_state = {
                'current_image': None,
                'processed_image': None,
                'ocr_result': None,
                'mode': None,  # 'registration' or 'scan'
                'uploaded_processed_image': None,
                'upload_ready': False
            }
        
        # Keep essential states for other functionality
        if "registration_success" not in st.session_state:
            st.session_state.registration_success = False
        if "generated_qr_path" not in st.session_state:
            st.session_state.generated_qr_path = None
        if "student_data" not in st.session_state:
            st.session_state.student_data = {}
        
        # Ceremony states
        if "ceremony_stage" not in st.session_state:
            st.session_state.ceremony_stage = "waiting"
        if "current_student" not in st.session_state:
            st.session_state.current_student = None
        if "qr_scan_time" not in st.session_state:
            st.session_state.qr_scan_time = None
        if "verification_result" not in st.session_state:
            st.session_state.verification_result = None
        
        
        # IC Verification states
        if "ic_verification_step" not in st.session_state:
            st.session_state.ic_verification_step = "upload"
        if "ic_verification_result" not in st.session_state:
            st.session_state.ic_verification_result = None
        if "ic_matched_student" not in st.session_state:
            st.session_state.ic_matched_student = None
        if "ic_similarity_score" not in st.session_state:
            st.session_state.ic_similarity_score = 0.0
    
    @staticmethod
    def clear_capture():
        """Clear capture state properly"""
        st.session_state.capture_state = {
            'current_image': None,
            'processed_image': None,
            'ocr_result': None,
            'mode': None,
            'uploaded_processed_image': None,
            'upload_ready': False
        }
    
    @staticmethod
    def get_capture_state():
        """Get current capture state"""
        if 'capture_state' not in st.session_state:
            SessionManager.init_all_states()
        return st.session_state.capture_state
    
    @staticmethod
    def update_capture_state(updates):
        """Update capture state with provided dictionary"""
        if 'capture_state' not in st.session_state:
            SessionManager.init_all_states()
        st.session_state.capture_state.update(updates)
    
    @staticmethod
    def get_state(key, default=None):
        """Get a session state value with optional default"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set_state(key, value):
        """Set a session state value"""
        st.session_state[key] = value
    
    @staticmethod
    def has_state(key):
        """Check if a session state key exists"""
        return key in st.session_state
    
    @staticmethod
    def delete_state(key):
        """Delete a session state key if it exists"""
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def reset_ceremony_states():
        """Reset ceremony-related states"""
        st.session_state.ceremony_stage = "waiting"
        st.session_state.current_student = None
        st.session_state.qr_scan_time = None
        st.session_state.verification_result = None
        
        # Reset IC verification states
        st.session_state.ic_verification_step = "upload"
        st.session_state.ic_verification_result = None
        st.session_state.ic_matched_student = None
        st.session_state.ic_similarity_score = 0.0
    
    @staticmethod
    def reset_registration_states():
        """Reset registration-related states"""
        st.session_state.registration_success = False
        st.session_state.generated_qr_path = None
        st.session_state.student_data = {}
        SessionManager.clear_capture()
    

# Legacy compatibility functions
def init_session_state():
    """Initialize all session states (legacy compatibility)"""
    SessionManager.init_all_states()

def clear_capture():
    """Clear capture state (legacy compatibility)"""
    SessionManager.clear_capture()

def initialize_session_states():
    """Initialize all required session state variables (legacy compatibility)"""
    SessionManager.init_all_states()