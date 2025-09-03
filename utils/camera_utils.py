"""
Camera utility functions for supporting external cameras
"""
import streamlit as st
import cv2
import numpy as np
from typing import Optional, Tuple, List

def detect_available_cameras() -> List[int]:
    """
    Detect all available cameras on the system
    Returns list of camera indices that are working
    """
    available_cameras = []
    
    # Test cameras 0-5 (usually covers most setups)
    for i in range(6):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Try to read a frame to verify camera is working
                ret, frame = cap.read()
                if ret and frame is not None:
                    available_cameras.append(i)
            cap.release()
        except:
            continue
    
    return available_cameras

def get_camera_info() -> dict:
    """
    Get information about available cameras
    Returns dict with camera info
    """
    cameras = detect_available_cameras()
    
    camera_info = {
        'total_cameras': len(cameras),
        'default_camera': 0 if 0 in cameras else (cameras[0] if cameras else None),
        'external_camera': None,
        'available_cameras': cameras
    }
    
    # Try to identify external camera (usually index 1 or higher)
    for cam_idx in cameras:
        if cam_idx > 0:
            camera_info['external_camera'] = cam_idx
            break
    
    return camera_info

def create_camera_input_with_preference(
    label: str,
    use_external: bool = False,
    key: str = None,
    help: str = None
) -> Optional[np.ndarray]:
    """
    Create camera input with preference for external camera when available
    
    Note: Streamlit's camera_input doesn't support selecting specific cameras.
    This function provides helpful info about camera availability and usage tips.
    
    Args:
        label: Label for the camera input
        use_external: Whether to prefer external camera
        key: Unique key for the widget
        help: Help text
    
    Returns:
        Captured image array or None
    """
    
    # Simple info without expensive camera detection
    if use_external:
        st.info("📹 External camera preferred - Select external camera in browser if available")
    
    # Create the camera input
    captured_image = st.camera_input(
        label=label,
        key=key,
        help=help
    )
    
    return captured_image

def get_camera_selection_ui() -> int:
    """
    Create UI for manual camera selection (for testing/debugging)
    Returns selected camera index
    """
    camera_info = get_camera_info()
    
    if camera_info['total_cameras'] == 0:
        st.error("❌ No cameras detected")
        return None
    
    st.sidebar.markdown("### 📹 Camera Settings")
    
    camera_options = {}
    for cam_idx in camera_info['available_cameras']:
        if cam_idx == 0:
            camera_options[f"Default Camera (Camera {cam_idx})"] = cam_idx
        else:
            camera_options[f"External Camera (Camera {cam_idx})"] = cam_idx
    
    selected_camera_label = st.sidebar.selectbox(
        "Select Camera:",
        options=list(camera_options.keys()),
        index=0
    )
    
    selected_camera = camera_options[selected_camera_label]
    
    # Show camera info
    st.sidebar.info(f"""
    **Camera Information:**
    - Total cameras: {camera_info['total_cameras']}
    - Current selection: {selected_camera_label}
    - Available cameras: {', '.join(map(str, camera_info['available_cameras']))}
    """)
    
    return selected_camera