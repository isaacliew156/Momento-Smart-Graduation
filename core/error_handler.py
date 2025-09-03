"""
Error handling and validation module for the Graduation Attendance System
"""
import logging
import traceback
from functools import wraps
import streamlit as st
from datetime import datetime
import os

# Configure logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/graduation_scanner_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

class CameraError(Exception):
    """Custom exception for camera-related errors"""
    pass

class QRCodeError(Exception):
    """Custom exception for QR code operations"""
    pass

def error_handler(func):
    """
    Decorator for handling errors in functions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error in {func.__name__}: {str(e)}")
            st.error(f"❌ Validation Error: {str(e)}")
            return None
        except DatabaseError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            st.error(f"❌ Database Error: {str(e)}")
            return None
        except CameraError as e:
            logger.error(f"Camera error in {func.__name__}: {str(e)}")
            st.error(f"❌ Camera Error: {str(e)}")
            return None
        except QRCodeError as e:
            logger.error(f"QR Code error in {func.__name__}: {str(e)}")
            st.error(f"❌ QR Code Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            return None
    return wrapper

def validate_student_id(student_id):
    """
    Validate student ID format
    """
    if not student_id:
        raise ValidationError("Student ID cannot be empty")
    
    if len(student_id) < 5:
        raise ValidationError("Student ID must be at least 5 characters long")
    
    if not student_id.replace("_", "").replace("-", "").isalnum():
        raise ValidationError("Student ID can only contain letters, numbers, hyphens, and underscores")
    
    return True

def validate_name(name):
    """
    Validate student name
    """
    if not name:
        raise ValidationError("Name cannot be empty")
    
    if len(name) < 2:
        raise ValidationError("Name must be at least 2 characters long")
    
    if not all(c.isalpha() or c.isspace() or c in ".-'" for c in name):
        raise ValidationError("Name can only contain letters, spaces, hyphens, dots, and apostrophes")
    
    return True

def validate_image_file(file_path):
    """
    Validate image file exists and is readable
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"Image file not found: {file_path}")
    
    if not os.access(file_path, os.R_OK):
        raise ValidationError(f"Cannot read image file: {file_path}")
    
    # Check file size (max 10MB)
    file_size = os.path.getsize(file_path)
    if file_size > 10 * 1024 * 1024:
        raise ValidationError("Image file size exceeds 10MB limit")
    
    return True

def validate_date_range(start_date, end_date):
    """
    Validate date range
    """
    if start_date > end_date:
        raise ValidationError("Start date must be before or equal to end date")
    
    # Check if dates are not too far in the future
    from datetime import datetime, timedelta
    max_future_date = datetime.now().date() + timedelta(days=365)
    
    if end_date > max_future_date:
        raise ValidationError("Date range cannot extend more than 1 year into the future")
    
    return True

def safe_json_load(json_str):
    """
    Safely load JSON data with error handling
    """
    import json
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {str(e)}")

def safe_file_operation(operation, *args, **kwargs):
    """
    Safely perform file operations with error handling
    """
    try:
        return operation(*args, **kwargs)
    except PermissionError:
        raise DatabaseError("Permission denied accessing file")
    except IOError as e:
        raise DatabaseError(f"File operation failed: {str(e)}")
    except Exception as e:
        raise DatabaseError(f"Unexpected file error: {str(e)}")

def log_activity(activity_type, details):
    """
    Log system activities
    """
    logger.info(f"Activity: {activity_type} - {details}")

def create_error_report():
    """
    Create a summary of recent errors for admin review
    """
    try:
        log_file = f'{log_dir}/graduation_scanner_{datetime.now().strftime("%Y%m%d")}.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            errors = [line for line in lines if 'ERROR' in line]
            
            return {
                'total_errors': len(errors),
                'recent_errors': errors[-10:] if errors else [],
                'log_file': log_file
            }
    except Exception as e:
        logger.error(f"Failed to create error report: {str(e)}")
        return None

def camera_availability_check():
    """
    Check if camera is available
    """
    import cv2
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise CameraError("Camera is not available or in use by another application")
        cap.release()
        return True
    except Exception as e:
        raise CameraError(f"Camera check failed: {str(e)}")

def validate_attendance_record(record):
    """
    Validate attendance record structure
    """
    required_fields = ['student_id', 'name', 'check_in_time']
    
    for field in required_fields:
        if field not in record:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate student ID
    validate_student_id(record['student_id'])
    
    # Validate name
    validate_name(record['name'])
    
    # Validate timestamp format
    try:
        datetime.strptime(record['check_in_time'], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise ValidationError("Invalid check-in time format. Expected: YYYY-MM-DD HH:MM:SS")
    
    return True

def handle_streamlit_error(error_message, suggestion=None):
    """
    Display user-friendly error message in Streamlit
    """
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.markdown("# ⚠️")
    
    with col2:
        st.error(error_message)
        
        if suggestion:
            st.info(f"💡 Suggestion: {suggestion}")
        
        with st.expander("🔧 Need help?"):
            st.markdown("""
            **Common solutions:**
            1. Refresh the page and try again
            2. Check your camera/webcam connection
            3. Ensure you have proper lighting
            4. Verify your internet connection
            5. Contact administrator if issue persists
            """)
    
    # Log the error
    logger.error(f"User-facing error: {error_message}")

# Export functions and classes
__all__ = [
    'ValidationError',
    'DatabaseError', 
    'CameraError',
    'QRCodeError',
    'error_handler',
    'validate_student_id',
    'validate_name',
    'validate_image_file',
    'validate_date_range',
    'safe_json_load',
    'safe_file_operation',
    'log_activity',
    'create_error_report',
    'camera_availability_check',
    'validate_attendance_record',
    'handle_streamlit_error'
]