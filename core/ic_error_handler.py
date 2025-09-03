"""
Error Handling and Edge Case Management for IC Verification System
Provides comprehensive error handling, logging, and recovery mechanisms
"""
import os
import tempfile
import logging
import traceback
import time
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
import streamlit as st


class ICVerificationError(Exception):
    """Custom exception for IC verification errors"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code or "IC_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ICErrorHandler:
    """Centralized error handler for IC verification system"""
    
    ERROR_MESSAGES = {
        "IC_IMAGE_TOO_SMALL": "IC image is too small. Minimum size required: 300x200 pixels.",
        "IC_IMAGE_TOO_LARGE": "IC image is too large. Maximum size allowed: 5000x5000 pixels.",
        "IC_IMAGE_CORRUPTED": "IC image appears to be corrupted or unreadable.",
        "IC_NO_FACES": "No faces detected on the IC. Please ensure the IC is clear and well-lit.",
        "IC_ONE_FACE": "Only one face detected. Malaysian IC verification requires both main and ghost faces.",
        "IC_TOO_MANY_FACES": "Too many faces detected on the IC. Please ensure only the IC is visible in the image.",
        "IC_POOR_QUALITY": "IC image quality is too poor for verification. Please use better lighting and focus.",
        "IC_WRONG_ORIENTATION": "IC appears to be rotated or upside down. Please orient it correctly.",
        "FACE_SERVICE_UNAVAILABLE": "Face recognition service is temporarily unavailable. Please try again later.",
        "FACE_SERVICE_OVERLOADED": "Face recognition service is overloaded. Please wait and try again.",
        "MODEL_LOADING_FAILED": "Face recognition models failed to load. Please restart the application.",
        "DATABASE_UNAVAILABLE": "Student database is temporarily unavailable.",
        "DATABASE_CORRUPTED": "Student database appears to be corrupted.",
        "NETWORK_ERROR": "Network connection error occurred during verification.",
        "INSUFFICIENT_MEMORY": "Insufficient memory to process the IC image.",
        "PERMISSION_ERROR": "Permission denied accessing temporary files.",
        "CONCURRENT_ACCESS": "Another verification is in progress. Please wait.",
        "SIMILARITY_THRESHOLD_TOO_HIGH": "No matches found. Try lowering the similarity threshold.",
        "NO_STUDENTS_WITH_ENCODINGS": "No students with face encodings found in the database.",
        "VERIFICATION_TIMEOUT": "IC verification process timed out. Please try again.",
        "INVALID_FILE_FORMAT": "Invalid file format. Please upload JPG, PNG, or JPEG images only.",
        "FILE_SIZE_TOO_LARGE": "File size too large. Maximum allowed: 10MB.",
        "IMAGE_ORIENTATION_ISSUE": "IC image appears to have orientation issues. Please check if it's rotated or upside down.",
        "IMAGE_PROCESSING_FAILED": "Failed to process the uploaded image. Please try a different image.",
        "CAMERA_NOT_AVAILABLE": "Camera is not available or permission denied.",
        "CAMERA_CAPTURE_FAILED": "Failed to capture image from camera. Please try again."
    }
    
    RECOVERY_SUGGESTIONS = {
        "IC_IMAGE_TOO_SMALL": "Use a higher resolution camera or scanner.",
        "IC_IMAGE_TOO_LARGE": "Resize the image or reduce camera resolution.",
        "IC_IMAGE_CORRUPTED": "Re-capture or re-upload the IC image.",
        "IC_NO_FACES": "Ensure good lighting and the IC is clearly visible.",
        "IC_ONE_FACE": "This may be normal for some ICs. Use manual verification if needed.",
        "IC_TOO_MANY_FACES": "Crop the image to show only the IC card.",
        "IC_POOR_QUALITY": "Use better lighting, reduce shadows, and ensure the IC is in focus.",
        "IC_WRONG_ORIENTATION": "Rotate the IC image so text is readable from left to right.",
        "FACE_SERVICE_UNAVAILABLE": "Wait a moment and try again, or contact support.",
        "FACE_SERVICE_OVERLOADED": "Wait 10-30 seconds before retrying.",
        "MODEL_LOADING_FAILED": "Restart the application or contact technical support.",
        "DATABASE_UNAVAILABLE": "Check database connection or contact administrator.",
        "DATABASE_CORRUPTED": "Contact administrator to restore database backup.",
        "NETWORK_ERROR": "Check internet connection and try again.",
        "INSUFFICIENT_MEMORY": "Close other applications or use a smaller image.",
        "PERMISSION_ERROR": "Check file permissions or run as administrator.",
        "CONCURRENT_ACCESS": "Wait for the current verification to complete.",
        "SIMILARITY_THRESHOLD_TOO_HIGH": "Lower the similarity threshold in settings.",
        "NO_STUDENTS_WITH_ENCODINGS": "Ensure students are registered with face photos.",
        "VERIFICATION_TIMEOUT": "Try with a smaller image or better network connection.",
        "INVALID_FILE_FORMAT": "Convert image to JPG or PNG format.",
        "FILE_SIZE_TOO_LARGE": "Compress the image or use a smaller resolution.",
        "IMAGE_ORIENTATION_ISSUE": "Use the rotation controls to correct image orientation.",
        "IMAGE_PROCESSING_FAILED": "Try uploading a different image or use the camera capture option.",
        "CAMERA_NOT_AVAILABLE": "Check camera permissions in your browser or try uploading an image instead.",
        "CAMERA_CAPTURE_FAILED": "Ensure good lighting and try capturing again, or use upload option."
    }
    
    @staticmethod
    def log_error(error_code: str, message: str, details: Dict = None):
        """Log error with details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_code": error_code,
            "message": message,
            "details": details or {},
            "stack_trace": traceback.format_exc() if details and details.get("include_trace") else None
        }
        
        # Log to file if possible
        try:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"ic_verification_errors_{datetime.now().strftime('%Y%m%d')}.log")
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} - {error_code}: {message}\n")
                if details:
                    f.write(f"Details: {details}\n")
                f.write("-" * 50 + "\n")
                
        except Exception:
            pass  # Don't let logging errors break the application
    
    @staticmethod
    def handle_ic_image_validation(image, max_size_mb: float = 10.0) -> Dict[str, Any]:
        """Validate IC image and return validation result"""
        try:
            from PIL import Image as PILImage
            import io
            
            # Check if image is valid
            if image is None:
                return {
                    "valid": False,
                    "error_code": "IC_IMAGE_CORRUPTED",
                    "message": ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_CORRUPTED"],
                    "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_IMAGE_CORRUPTED"]
                }
            
            # Handle different image types and get actual file size when possible
            actual_file_size_mb = None
            width = height = None
            
            if hasattr(image, 'size'):  # PIL Image
                width, height = image.size
                # No direct file size info from PIL Image object
                estimated_size_mb = (width * height * 3) / (1024 * 1024)
            elif hasattr(image, 'shape'):  # Numpy array
                height, width = image.shape[:2]
                estimated_size_mb = (width * height * 3) / (1024 * 1024)
            elif hasattr(image, 'read'):  # File-like object (uploaded file)
                image.seek(0, 2)  # Go to end
                actual_file_size_mb = image.tell() / (1024 * 1024)
                image.seek(0)  # Reset to beginning
                
                # Use actual file size for validation (most accurate)
                if actual_file_size_mb > max_size_mb:
                    return {
                        "valid": False,
                        "error_code": "FILE_SIZE_TOO_LARGE",
                        "message": ICErrorHandler.ERROR_MESSAGES["FILE_SIZE_TOO_LARGE"],
                        "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["FILE_SIZE_TOO_LARGE"],
                        "details": {"actual_file_size_mb": actual_file_size_mb}
                    }
                
                # Try to load the image to get dimensions
                try:
                    pil_image = PILImage.open(image)
                    width, height = pil_image.size
                    estimated_size_mb = actual_file_size_mb  # Use actual size, not estimated
                    image.seek(0)  # Reset again after PIL.Image.open
                except Exception:
                    return {
                        "valid": False,
                        "error_code": "IC_IMAGE_CORRUPTED",
                        "message": ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_CORRUPTED"],
                        "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_IMAGE_CORRUPTED"]
                    }
            else:
                return {
                    "valid": False,
                    "error_code": "INVALID_FILE_FORMAT",
                    "message": ICErrorHandler.ERROR_MESSAGES["INVALID_FILE_FORMAT"],
                    "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["INVALID_FILE_FORMAT"]
                }
            
            if width is None or height is None:
                return {
                    "valid": False,
                    "error_code": "IC_IMAGE_CORRUPTED",
                    "message": ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_CORRUPTED"],
                    "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_IMAGE_CORRUPTED"]
                }
            
            # Check dimensions
            if width < 300 or height < 200:
                return {
                    "valid": False,
                    "error_code": "IC_IMAGE_TOO_SMALL",
                    "message": ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_TOO_SMALL"],
                    "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_IMAGE_TOO_SMALL"],
                    "details": {"width": width, "height": height}
                }
            
            if width > 5000 or height > 5000:
                return {
                    "valid": False,
                    "error_code": "IC_IMAGE_TOO_LARGE",
                    "message": ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_TOO_LARGE"],
                    "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_IMAGE_TOO_LARGE"],
                    "details": {"width": width, "height": height}
                }
            
            # Only check estimated size if we don't have actual file size
            # (for PIL Images or numpy arrays that don't have file size info)
            if actual_file_size_mb is None and estimated_size_mb > max_size_mb:
                return {
                    "valid": False,
                    "error_code": "FILE_SIZE_TOO_LARGE",
                    "message": ICErrorHandler.ERROR_MESSAGES["FILE_SIZE_TOO_LARGE"],
                    "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["FILE_SIZE_TOO_LARGE"],
                    "details": {"estimated_size_mb": estimated_size_mb, "note": "Estimated uncompressed size"}
                }
            
            return {
                "valid": True,
                "details": {
                    "width": width,
                    "height": height,
                    "actual_file_size_mb": actual_file_size_mb,
                    "estimated_memory_size_mb": estimated_size_mb,
                    "size_source": "actual_file" if actual_file_size_mb is not None else "estimated_memory"
                }
            }
            
        except Exception as e:
            ICErrorHandler.log_error("IMAGE_VALIDATION_ERROR", str(e), {"include_trace": True})
            return {
                "valid": False,
                "error_code": "IC_IMAGE_CORRUPTED",
                "message": ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_CORRUPTED"],
                "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_IMAGE_CORRUPTED"]
            }
    
    @staticmethod
    def handle_face_detection_result(faces_detected: int) -> Dict[str, Any]:
        """Handle different face detection outcomes"""
        if faces_detected == 0:
            return {
                "valid": False,
                "error_code": "IC_NO_FACES",
                "message": ICErrorHandler.ERROR_MESSAGES["IC_NO_FACES"],
                "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_NO_FACES"],
                "allow_manual_override": True
            }
        elif faces_detected == 1:
            return {
                "valid": False,
                "error_code": "IC_ONE_FACE",
                "message": ICErrorHandler.ERROR_MESSAGES["IC_ONE_FACE"],
                "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_ONE_FACE"],
                "allow_manual_override": True,
                "warning_only": True  # This might be acceptable for some ICs
            }
        elif faces_detected > 5:
            return {
                "valid": False,
                "error_code": "IC_TOO_MANY_FACES",
                "message": ICErrorHandler.ERROR_MESSAGES["IC_TOO_MANY_FACES"],
                "suggestion": ICErrorHandler.RECOVERY_SUGGESTIONS["IC_TOO_MANY_FACES"],
                "allow_manual_override": False
            }
        else:
            return {"valid": True}
    
    @staticmethod
    @contextmanager
    def safe_temp_file(suffix=".jpg"):
        """Safely create and clean up temporary files"""
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            yield temp_file.name
        except PermissionError:
            ICErrorHandler.log_error("PERMISSION_ERROR", "Cannot create temporary file")
            raise ICVerificationError(
                ICErrorHandler.ERROR_MESSAGES["PERMISSION_ERROR"],
                "PERMISSION_ERROR"
            )
        except OSError as e:
            ICErrorHandler.log_error("TEMP_FILE_ERROR", f"Temporary file error: {str(e)}")
            raise ICVerificationError(
                f"Temporary file error: {str(e)}",
                "TEMP_FILE_ERROR"
            )
        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass  # Don't fail if cleanup fails
    
    @staticmethod
    def with_retry(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """Execute function with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = delay * (backoff ** attempt)
                ICErrorHandler.log_error(
                    "RETRY_ATTEMPT", 
                    f"Attempt {attempt + 1} failed: {str(e)}, retrying in {wait_time}s",
                    {"attempt": attempt + 1, "max_retries": max_retries}
                )
                time.sleep(wait_time)
    
    @staticmethod
    def display_error_in_streamlit(error_code: str, message: str = None, suggestion: str = None, details: Dict = None):
        """Display user-friendly error message in Streamlit"""
        error_msg = message or ICErrorHandler.ERROR_MESSAGES.get(error_code, "An unexpected error occurred.")
        suggestion_msg = suggestion or ICErrorHandler.RECOVERY_SUGGESTIONS.get(error_code, "Please try again or contact support.")
        
        # Determine error level
        if error_code in ["IC_ONE_FACE", "SIMILARITY_THRESHOLD_TOO_HIGH"]:
            st.warning(f"⚠️ **Warning:** {error_msg}")
        else:
            st.error(f"❌ **Error:** {error_msg}")
        
        # Show suggestion
        st.info(f"💡 **Suggestion:** {suggestion_msg}")
        
        # Show details in expander if available
        if details:
            with st.expander("🔍 Technical Details"):
                for key, value in details.items():
                    if key not in ["include_trace", "stack_trace"]:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    @staticmethod
    def check_system_resources() -> Dict[str, Any]:
        """Check system resources and return status"""
        try:
            import psutil
            
            # Check available memory
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)
            
            # Check disk space in temp directory
            temp_dir = tempfile.gettempdir()
            disk_usage = psutil.disk_usage(temp_dir)
            available_gb = disk_usage.free / (1024 * 1024 * 1024)
            
            return {
                "sufficient_resources": True,
                "available_memory_mb": available_mb,
                "available_disk_gb": available_gb,
                "memory_ok": available_mb > 500,  # Need at least 500MB
                "disk_ok": available_gb > 1.0     # Need at least 1GB
            }
            
        except ImportError:
            # psutil not available, assume resources are OK
            return {"sufficient_resources": True, "psutil_available": False}
        except Exception:
            # Error checking resources, assume they're OK
            return {"sufficient_resources": True, "check_failed": True}


def safe_ic_verification(func):
    """Decorator for safe IC verification with comprehensive error handling"""
    def wrapper(*args, **kwargs):
        try:
            # Check system resources before starting
            resources = ICErrorHandler.check_system_resources()
            if not resources.get("memory_ok", True):
                raise ICVerificationError(
                    ICErrorHandler.ERROR_MESSAGES["INSUFFICIENT_MEMORY"],
                    "INSUFFICIENT_MEMORY"
                )
            
            # Execute the function with retry logic
            return ICErrorHandler.with_retry(lambda: func(*args, **kwargs))
            
        except ICVerificationError:
            raise  # Re-raise custom errors as-is
        except MemoryError:
            raise ICVerificationError(
                ICErrorHandler.ERROR_MESSAGES["INSUFFICIENT_MEMORY"],
                "INSUFFICIENT_MEMORY"
            )
        except PermissionError:
            raise ICVerificationError(
                ICErrorHandler.ERROR_MESSAGES["PERMISSION_ERROR"],
                "PERMISSION_ERROR"
            )
        except Exception as e:
            ICErrorHandler.log_error("UNEXPECTED_ERROR", str(e), {"include_trace": True})
            raise ICVerificationError(
                f"An unexpected error occurred: {str(e)}",
                "UNEXPECTED_ERROR",
                {"original_error": str(e)}
            )
    
    return wrapper


# Configuration for error handling
IC_VERIFICATION_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1.0,
    "retry_backoff": 2.0,
    "max_image_size_mb": 10.0,
    "min_image_width": 300,
    "min_image_height": 200,
    "max_image_width": 5000,
    "max_image_height": 5000,
    "verification_timeout": 60,  # seconds
    "face_detection_timeout": 30,  # seconds
    "similarity_threshold_default": 0.6,
    "similarity_threshold_min": 0.3,
    "similarity_threshold_max": 0.9
}