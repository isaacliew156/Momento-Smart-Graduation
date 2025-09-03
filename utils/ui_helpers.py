"""
UI helper functions for the Graduation Attendance System
"""
import streamlit as st
from functools import wraps
import time

def check_face_service_health(face_service):
    """Check if face recognition service is healthy and provide recovery options"""
    
    if face_service is None or not face_service.is_ready():
        st.error("⚠️ Face recognition service is not ready!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reload Face Recognition Service"):
                try:
                    with st.spinner("Reloading face recognition service..."):
                        from core.face_module import get_face_service
                        face_service = initialize_face_service()
                        if face_service and face_service.is_ready():
                            st.success("✅ Face recognition service reloaded successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to reload service")
                except Exception as e:
                    st.error(f"❌ Reload error: {str(e)}")
        
        with col2:
            if st.button("🔧 Force Model Reload"):
                try:
                    with st.spinner("Force reloading models..."):
                        if face_service:
                            face_service.reload_models()
                            st.success("✅ Models reloaded successfully!")
                            st.rerun()
                        else:
                            from core.face_module import get_face_service
                            face_service = initialize_face_service()
                except Exception as e:
                    st.error(f"❌ Force reload error: {str(e)}")
        
        return False
    return True

@st.cache_resource
def initialize_face_service():
    """
    Initialize the face recognition service with model caching
    This runs only once per Streamlit session and dramatically improves performance
    """
    try:
        with st.spinner("🤖 Initializing AI system..."):
            from core.face_module import get_face_service
            service = get_face_service()
            if service.is_ready():
                return service
            else:
                return None
    except Exception as e:
        st.error(f"❌ Face recognition initialization error: {str(e)}")
        return None

def add_performance_monitor(face_service):
    """Add subtle performance monitoring sidebar"""
    with st.sidebar:
        st.markdown("---")
        
        # Simple status indicator
        if face_service and face_service.is_ready():
            st.caption("🟢 AI System Ready")
        else:
            st.caption("🔴 AI System Loading...")
        
        # Minimal details in expander
        with st.expander("System Details", expanded=False):
            if face_service and face_service.is_ready():
                st.caption("Face Recognition: Ready")
                st.caption("Processing: Optimized")
            else:
                st.caption("Initializing AI components...")
            
            if st.button("Refresh Status", key="refresh_status"):
                st.rerun()

def with_spinner(message="Processing..."):
    """Decorator to add spinner to functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def show_success_message(message, duration=3):
    """Show a success message that disappears after duration"""
    placeholder = st.empty()
    placeholder.success(message)
    time.sleep(duration)
    placeholder.empty()

def show_error_message(message, duration=5):
    """Show an error message that disappears after duration"""
    placeholder = st.empty()
    placeholder.error(message)
    time.sleep(duration)
    placeholder.empty()

def create_download_button(data, filename, label, key=None):
    """Create a standardized download button"""
    return st.download_button(
        label=f"📥 {label}",
        data=data,
        file_name=filename,
        key=key
    )

def create_info_box(title, content, type="info"):
    """Create an information box with consistent styling"""
    if type == "info":
        st.info(f"**{title}**\n\n{content}")
    elif type == "success":
        st.success(f"**{title}**\n\n{content}")
    elif type == "warning":
        st.warning(f"**{title}**\n\n{content}")
    elif type == "error":
        st.error(f"**{title}**\n\n{content}")

def create_metric_card(label, value, delta=None, delta_color="normal"):
    """Create a metric card with consistent styling"""
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def create_progress_bar(current, total, text="Progress"):
    """Create a progress bar with text"""
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{text}: {current}/{total}")

def confirm_action(message, key=None):
    """Create a confirmation dialog for critical actions"""
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm", key=f"{key}_confirm" if key else None):
            return True
    with col2:
        if st.button("❌ Cancel", key=f"{key}_cancel" if key else None):
            return False
    return None

def create_tabs(tab_names):
    """Create tabs with consistent styling"""
    return st.tabs(tab_names)

def create_columns(weights=None, gap="medium"):
    """Create columns with consistent spacing"""
    if weights:
        return st.columns(weights, gap=gap)
    return st.columns(2, gap=gap)

def format_timestamp(timestamp):
    """Format timestamp consistently across the app"""
    from datetime import datetime
    if isinstance(timestamp, str):
        return timestamp
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename