"""
Ceremony Attendance page for the Graduation Attendance System
Fixed version with optimized half-screen verification mode
"""
import streamlit as st
import pandas as pd
import os
import io
import json
import time
import numpy as np
from datetime import datetime
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

# Import core modules
from core.database import *
from core.face_module import *
from core.qr_module import *
from core.tesseract_ocr import TesseractOCR
from core.tts_module import *
# Interactive cropping removed for simplified deployment
from core.error_handler import *
from core.ic_error_handler import ICErrorHandler, ICVerificationError
from core.ic_verification import verify_ic_and_find_student

# Import utils
from utils.config import *
from utils.session_manager import SessionManager, init_session_state, clear_capture
from utils.card_processing import *
from utils.camera_utils import create_camera_input_with_preference
from utils.ui_helpers import *
from utils.loading_animations import create_simple_spinner, ocr_loader


def render_ceremony_attendance(face_service):
    """Render the ceremony attendance page"""
    
    # Clear previous states when navigating to this page
    if "last_visited_page" not in st.session_state:
        st.session_state.last_visited_page = None
    
    current_page = "Ceremony"
    # Check if user just navigated to this page from another page
    if st.session_state.last_visited_page != current_page:
        # User navigated to this page, clear all ceremony states
        ceremony_states_to_clear = [
            'ic_verification_result', 'verification_result', 
            'current_student',
            'selected_student', 'face_verification_result'
        ]
        
        for state in ceremony_states_to_clear:
            if hasattr(st.session_state, state):
                delattr(st.session_state, state)
        
        # Reset to initial ceremony stage
        st.session_state.ceremony_stage = "waiting"
    
    st.session_state.last_visited_page = current_page
    
    # Initialize ceremony stage if not exists
    if "ceremony_stage" not in st.session_state:
        st.session_state.ceremony_stage = "waiting"
    
    st.title("🎓 Graduation Ceremony Check-in System")
    st.markdown('<p style="color: #2D3436; font-size: 1rem; margin-bottom: 1.5rem;">Real-time QR scanning and face verification with audio announcements</p>', unsafe_allow_html=True)
    
    # Check face service health before proceeding
    if not check_face_service_health(face_service):
        st.warning("⚠️ Face recognition service is required for ceremony attendance.")
        st.stop()
    
    # Check if students are registered
    db = load_database()
    if not db:
        st.warning("📭 No students registered yet. Please register students first.")
        st.stop()
    
    # Enhanced CSS for better visual transitions
    st.markdown("""
    <style>
        /* Success animation styling */
        .success-panel {
            animation: fadeInUp 0.5s ease-out;
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            border-radius: 12px;
            padding: 1rem;
            color: white;
            box-shadow: 0 4px 20px rgba(0, 184, 148, 0.3);
        }
        
        /* Verification stage indicators with glow */
        .stage-active {
            box-shadow: 0 0 15px rgba(116, 185, 255, 0.6);
            animation: pulse 2s infinite;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 15px rgba(116, 185, 255, 0.6); }
            50% { box-shadow: 0 0 25px rgba(116, 185, 255, 0.8); }
            100% { box-shadow: 0 0 15px rgba(116, 185, 255, 0.6); }
        }
        
        .compact-student-card {
            background: rgba(116, 185, 255, 0.05);
            border-left: 4px solid #74b9ff;
            border-radius: 8px;
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs for different functionality
    tab1, tab2 = st.tabs(["🎯 Quick Check-in", "📊 Live Status"])
    
    # Quick Check-in Tab
    with tab1:
        st.markdown("### 🎯 Ceremony Check-in System")
        
        # Simple progress indicator
        current_stage = st.session_state.ceremony_stage
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if current_stage in ["waiting", "qr_scanning"]:
                st.markdown("""
                <div style="text-align: center;">
                    <div style="
                        width: 50px; height: 50px; border-radius: 50%; 
                        background: #74B9FF; border: 3px solid #74B9FF;
                        display: flex; align-items: center; justify-content: center;
                        margin: 0 auto 0.5rem; color: white; font-size: 1.2rem;
                        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.1);
                    ">📱</div>
                    <div style="font-weight: 600; color: #74B9FF; margin-bottom: 0.25rem;">Scan QR</div>
                    <div style="font-size: 0.75rem; color: #636E72;">Scan student code</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center;">
                    <div style="
                        width: 50px; height: 50px; border-radius: 50%; 
                        background: #00B894; border: 3px solid #00B894;
                        display: flex; align-items: center; justify-content: center;
                        margin: 0 auto 0.5rem; color: white; font-size: 1.2rem;
                        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.1);
                    ">✓</div>
                    <div style="font-weight: 600; color: #00B894; margin-bottom: 0.25rem;">Scan QR</div>
                    <div style="font-size: 0.75rem; color: #636E72;">Completed</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if current_stage == "face_verifying":
                st.markdown("""
                <div style="text-align: center;">
                    <div class="stage-active" style="
                        width: 50px; height: 50px; border-radius: 50%; 
                        background: #74B9FF; border: 3px solid #74B9FF;
                        display: flex; align-items: center; justify-content: center;
                        margin: 0 auto 0.5rem; color: white; font-size: 1.2rem;
                        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.1);
                    ">👤</div>
                    <div style="font-weight: 600; color: #74B9FF; margin-bottom: 0.25rem;">Verify ID</div>
                    <div style="font-size: 0.75rem; color: #636E72;">Confirm identity</div>
                </div>
                """, unsafe_allow_html=True)
            elif current_stage == "completed":
                st.markdown("""
                <div style="text-align: center;">
                    <div style="
                        width: 50px; height: 50px; border-radius: 50%; 
                        background: #00B894; border: 3px solid #00B894;
                        display: flex; align-items: center; justify-content: center;
                        margin: 0 auto 0.5rem; color: white; font-size: 1.2rem;
                        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.1);
                    ">✓</div>
                    <div style="font-weight: 600; color: #00B894; margin-bottom: 0.25rem;">Verify ID</div>
                    <div style="font-size: 0.75rem; color: #636E72;">Completed</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center;">
                    <div style="
                        width: 50px; height: 50px; border-radius: 50%; 
                        background: #F5F6FA; border: 3px solid #DFE6E9;
                        display: flex; align-items: center; justify-content: center;
                        margin: 0 auto 0.5rem; color: #A4A6A8; font-size: 1.2rem;
                        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.1);
                    ">👤</div>
                    <div style="font-weight: 600; color: #A4A6A8; margin-bottom: 0.25rem;">Verify ID</div>
                    <div style="font-size: 0.75rem; color: #636E72;">Pending</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if current_stage == "completed":
                st.markdown("""
                <div style="text-align: center;">
                    <div style="
                        width: 50px; height: 50px; border-radius: 50%; 
                        background: #00B894; border: 3px solid #00B894;
                        display: flex; align-items: center; justify-content: center;
                        margin: 0 auto 0.5rem; color: white; font-size: 1.2rem;
                        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.1);
                    ">🎉</div>
                    <div style="font-weight: 600; color: #00B894; margin-bottom: 0.25rem;">Complete</div>
                    <div style="font-size: 0.75rem; color: #636E72;">Check-in done</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center;">
                    <div style="
                        width: 50px; height: 50px; border-radius: 50%; 
                        background: #F5F6FA; border: 3px solid #DFE6E9;
                        display: flex; align-items: center; justify-content: center;
                        margin: 0 auto 0.5rem; color: #A4A6A8; font-size: 1.2rem;
                        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.1);
                    ">🎉</div>
                    <div style="font-weight: 600; color: #A4A6A8; margin-bottom: 0.25rem;">Complete</div>
                    <div style="font-size: 0.75rem; color: #636E72;">Pending</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        
        # DYNAMIC LAYOUT - optimize for verification stage but keep context
        if st.session_state.ceremony_stage == "face_verifying":
            col_left, col_right = st.columns([1, 3])  # Compact left, expanded right for verification
        else:
            col_left, col_right = st.columns([1, 1])  # Normal split for other stages
        
        # LEFT PANEL: QR Code Scanner / Compact Student Info
        with col_left:
            if st.session_state.ceremony_stage == "face_verifying":
                # Compact student info during verification
                if st.session_state.current_student:
                    student = st.session_state.current_student
                    student_id = student.get('student_id') or student.get('id', 'Unknown')
                    student_name = student.get('name', 'Unknown')
                    
                    st.markdown("### 👤 Verifying")
                    
                    # Compact student card
                    st.markdown(f"""
                    <div class="compact-student-card">
                        <div style="display: flex; align-items: center;">
                            <div style="margin-right: 1rem;">
                                <div style="
                                    width: 50px; height: 50px; 
                                    border-radius: 50%; 
                                    background: #74b9ff; 
                                    display: flex; 
                                    align-items: center; 
                                    justify-content: center;
                                    color: white; 
                                    font-size: 1.2rem;
                                ">👤</div>
                            </div>
                            <div>
                                <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.25rem;">{student_name}</div>
                                <div style="color: #636e72; font-size: 0.8rem;">ID: {student_id}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    
                    # Back button
                    if st.button("⬅️ Back", use_container_width=True, key="verification_back"):
                        st.session_state.ceremony_stage = "waiting"
                        st.session_state.current_student = None
                        st.session_state.verification_result = None
                        st.rerun()
            else:
                # Full QR scanner interface for other stages
                st.markdown("### 📱 QR Code Scanner")
                
                
                # QR Scanning section
                if st.session_state.ceremony_stage == "waiting":
                    st.info("🔍 **Ready to scan QR codes**")
                    
                    # Show manual mode suggestion if flag is set
                    if st.session_state.get("switch_to_manual"):
                        st.info("💡 **Please select 'Manual Student Selection' below to continue after IC verification failure.**")
                        # Clear the flag after showing the message
                        st.session_state.switch_to_manual = False
                    
                    # Student Check-in Options
                    scan_method = st.radio(
                        "📱 Choose check-in method:",
                        ["🔄 Auto QR Scanning", "🆔 IC Verification", "📝 Manual Student Selection"],
                        horizontal=True,
                        key="ceremony_scan_method",
                        help="QR Code: Standard method | IC Card: Backup when QR unavailable | Manual: For testing"
                    )
                    
                    # Clear IC verification states when switching to other methods
                    if scan_method != "🆔 IC Verification":
                        if "ic_verification_step" in st.session_state:
                            del st.session_state.ic_verification_step
                        if "ic_verification_result" in st.session_state:
                            del st.session_state.ic_verification_result
                        if "ic_matched_student" in st.session_state:
                            del st.session_state.ic_matched_student
                        if "ic_rotation_angle" in st.session_state:
                            del st.session_state.ic_rotation_angle
                        if "ic_flipped" in st.session_state:
                            del st.session_state.ic_flipped
                    
                    # Handle different scanning methods
                    if scan_method == "🔄 Auto QR Scanning":
                        # Auto QR scanning mode
                        if st.button("🚀 Start QR Scanning", use_container_width=True, type="primary"):
                            with st.spinner("🔄 Activating QR scanner..."):
                                qr_result = continuous_qr_scan()
                                
                                if qr_result:
                                    try:
                                        # Parse QR code data
                                        import json
                                        qr_data = json.loads(qr_result)
                                        student_id = qr_data.get("student_id")
                                        
                                        # Find student in database
                                        student_match = get_student_by_id(student_id)
                                        
                                        if not student_match:
                                            st.error(f"❌ Student ID '{student_id}' not found in database")
                                        else:
                                            # Check if already attended today
                                            already_attended, existing_record = check_already_attended(student_id)
                                            
                                            if already_attended:
                                                st.warning(f"⚠️ Student already checked in today at {existing_record['check_in_time']}")
                                                if st.button("🔄 Continue Anyway (Override)", key="override"):
                                                    st.session_state.current_student = student_match
                                                    st.session_state.ceremony_stage = "face_verifying"
                                                    st.session_state.qr_scan_time = time.time()
                                                    st.rerun()
                                            else:
                                                # Proceed to face verification
                                                st.session_state.current_student = student_match
                                                st.session_state.ceremony_stage = "face_verifying"
                                                st.session_state.qr_scan_time = time.time()
                                                st.rerun()
                                                
                                    except json.JSONDecodeError:
                                        st.error("❌ Invalid QR code format")
                                else:
                                    st.error("❌ QR code scanning failed or cancelled")
                    
                    elif scan_method == "🆔 IC Verification":
                        # IC Verification mode - complete implementation restored
                        
                        st.markdown("#### 🆔 IC Verification System")
                        st.info("💡 **Three-Step Verification Process:**\n"
                               "1. **IC Authenticity Check** - Verify IC is genuine\n"
                               "2. **Database Matching** - Find student by face\n"
                               "3. **Live Face Verification** - Confirm identity")
                        
                        # Initialize IC verification session states only if not already set
                        if "ic_verification_step" not in st.session_state:
                            st.session_state.ic_verification_step = "upload"
                        
                        # Initialize other IC states if needed
                        if "ic_verification_result" not in st.session_state:
                            st.session_state.ic_verification_result = None
                        
                        if "ic_matched_student" not in st.session_state:
                            st.session_state.ic_matched_student = None
                        
                        # Debug info (for development - can be removed in production)
                        if st.session_state.get("show_debug_info", False):
                            with st.expander("🐛 Debug Info"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    if st.button("🔄 Reset Demo", help="Start IC verification from the beginning"):
                                        st.session_state.ic_verification_step = "upload"
                                        st.session_state.ic_verification_result = None
                                        st.session_state.ic_matched_student = None
                                        # Reset image transformation states
                                        st.session_state.ic_rotation_angle = 0
                                        st.session_state.ic_flipped = False
                                        st.rerun()
                                
                                with col2:
                                    st.write("**Current States:**")
                                    st.write(f"**Current Step:** {st.session_state.ic_verification_step}")
                                    st.write(f"**Has Result:** {'Yes' if st.session_state.ic_verification_result else 'No'}")
                            
                            st.info("💡 Use 'Reset Demo' to restart the IC verification process for repeated demonstrations.")
                        
                        # Step 1: IC Upload and Authenticity Verification
                        if st.session_state.ic_verification_step == "upload":
                            st.markdown("**Step 1: Upload IC Card** 🆔")
                            
                            # Upload method selection
                            ic_upload_method = st.radio(
                                "📷 Choose upload method:",
                                ["📂 Upload Image File", "📸 Take IC Photo"],
                                horizontal=True,
                                key="ic_upload_method",
                                help="Upload File: Use existing image | Take Photo: Use device camera"
                            )
                            
                            ic_image = None
                            
                            if ic_upload_method == "📂 Upload Image File":
                                st.markdown("##### 📂 File Upload")
                                uploaded_ic = st.file_uploader(
                                    "Choose IC image file",
                                    type=['jpg', 'jpeg', 'png'],
                                    help="Upload a clear image of the Malaysian IC card"
                                )
                                
                                if uploaded_ic is not None:
                                    from utils.image_processing import create_image_preview_with_controls
                                    
                                    # Process uploaded image
                                    ic_image, processing_info = create_image_preview_with_controls(
                                        uploaded_ic, 
                                        key_prefix="ic_upload"
                                    )
                                    
                                    if not processing_info.get("success", False):
                                        st.error("❌ Failed to process uploaded image. Please try a different image.")
                                        ic_image = None
                            
                            elif ic_upload_method == "📸 Take IC Photo":
                                st.markdown("##### 📸 Camera Capture")
                                st.info("💡 **Tips:** Ensure good lighting, hold IC card steady, and keep it in landscape orientation")
                                
                                # Streamlit camera input with external camera preference
                                camera_image = create_camera_input_with_preference(
                                    label="Take a photo of the Malaysian IC card",
                                    use_external=True,
                                    key="ic_camera_input",
                                    help="Use external camera to capture Malaysian IC card, ensure card is clearly visible in camera frame"
                                )
                                
                                if camera_image is not None:
                                    from utils.image_processing import create_image_preview_with_controls
                                    
                                    # Process camera captured image
                                    ic_image, processing_info = create_image_preview_with_controls(
                                        camera_image, 
                                        key_prefix="ic_camera"
                                    )
                                    
                                    if not processing_info.get("success", False):
                                        st.error("❌ Failed to process camera image. Please try taking another photo.")
                                        ic_image = None
                                    else:
                                        st.success("✅ Camera image captured successfully!")
                                        
                                        # Additional camera-specific tips
                                        with st.expander("📸 Camera Capture Tips", expanded=False):
                                            st.markdown("""
                                            **For better results:**
                                            - 💡 Ensure bright, even lighting
                                            - 📏 Keep IC card flat and parallel to camera
                                            - 🔍 Make sure all corners of IC are visible
                                            - 📱 Hold camera steady when capturing
                                            - 🔄 Use rotation controls below if image appears sideways
                                            """)
                                else:
                                    ic_image = None
                            
                            # Continue with verification if IC image is loaded
                            if ic_image is not None:
                                    
                                    # Only show verify button if no result yet
                                    if not st.session_state.ic_verification_result:
                                        if st.button("🔍 Verify IC Authenticity", use_container_width=True, type="primary"):
                                            # Beautiful IC verification loading animation
                                            from utils.loading_animations import ocr_loader
                                            loading_info = ocr_loader.create_loading_container("🆔 IC Verification System")
                                            
                                            # Clear any stray characters that might appear
                                            st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)
                                            
                                            # Define IC verification steps
                                            ic_steps = [
                                                {'icon': '🔍', 'title': 'Face Detection', 'description': 'Detecting faces on IC card'},
                                                {'icon': '👻', 'title': 'Ghost Face Analysis', 'description': 'Analyzing security features'},
                                                {'icon': '🤖', 'title': 'AI Authentication', 'description': 'Verifying IC authenticity with AI models'},
                                                {'icon': '🎯', 'title': 'Student Matching', 'description': 'Finding matching student in database'},
                                                {'icon': '✅', 'title': 'Verification Complete', 'description': 'IC verification process complete'}
                                            ]
                                            
                                            try:
                                                # Import additional IC verification functions
                                                from core.database import save_ic_verification_log
                                                
                                                # Optimize image size for faster processing
                                                if ic_image.size[0] > 1500 or ic_image.size[1] > 1500:
                                                    # Resize large images to improve processing speed
                                                    max_size = 1500
                                                    ratio = min(max_size/ic_image.size[0], max_size/ic_image.size[1])
                                                    new_size = (int(ic_image.size[0] * ratio), int(ic_image.size[1] * ratio))
                                                    ic_image_optimized = ic_image.resize(new_size, Image.Resampling.LANCZOS)
                                                    st.info(f"🔧 **Image optimized for faster processing**: {ic_image.size} → {ic_image_optimized.size}")
                                                    ic_image_for_processing = ic_image_optimized
                                                else:
                                                    ic_image_for_processing = ic_image
                                                
                                                # Step-by-step processing with animation
                                                for i, step in enumerate(ic_steps):
                                                    # Skip animation calls that cause errors, just sleep for visual effect
                                                    time.sleep(0.8)  # Visual effect timing
                                                    
                                                    # Execute actual verification on the last step
                                                    if i == len(ic_steps) - 1:
                                                        verification_result = verify_ic_and_find_student(ic_image_for_processing, similarity_threshold=0.5)
                                                
                                                # Complete the animation
                                                ocr_loader.complete_loading(loading_info, success=True, 
                                                                          final_message="🎉 IC verification completed!")
                                                
                                                # Brief pause for visual effect
                                                time.sleep(1)
                                                
                                                # Log the verification attempt
                                                try:
                                                    save_ic_verification_log({
                                                        "timestamp": datetime.now().isoformat(),
                                                        "success": verification_result.get("success", False),
                                                        "student_found": verification_result.get("student_found", False),
                                                        "faces_detected": verification_result.get("ic_verification", {}).get("faces_detected", 0),
                                                        "method": "upload"
                                                    })
                                                except Exception as log_error:
                                                    print(f"Warning: Could not save verification log: {log_error}")
                                                
                                                # Store result and advance to next step
                                                st.session_state.ic_verification_result = verification_result
                                                st.rerun()  # Rerun to display results
                                            
                                            except ICVerificationError as e:
                                                # Complete animation with error state
                                                ocr_loader.complete_loading(loading_info, success=False, 
                                                                          final_message=f"❌ IC Verification Error: {e.message}")
                                                
                                                # Display user-friendly error message
                                                ICErrorHandler.display_error_in_streamlit(
                                                    e.error_code, 
                                                    e.message, 
                                                    details=e.details
                                                )
                                                
                                            except Exception as e:
                                                # Complete animation with general error
                                                ocr_loader.complete_loading(loading_info, success=False, 
                                                                          final_message=f"❌ Unexpected error occurred")
                                                
                                                st.error(f"❌ **Unexpected Error**: {str(e)}")
                                                st.info("💡 Please try again with a different image or contact support if the issue persists.")
                                                
                                                # Log the error for debugging
                                                ICErrorHandler.log_error("UNEXPECTED_ERROR", str(e), {"include_trace": True})
                                    
                                    # Display results if available
                                    if st.session_state.ic_verification_result:
                                        verification_result = st.session_state.ic_verification_result
                                        
                                        st.markdown("---")
                                        st.markdown("#### 🎯 IC Verification Results")
                                        
                                        # Check if IC verification was successful or has student match
                                        ic_success = (verification_result.get("status") == "SUCCESS" or 
                                                     verification_result.get("status") == "NO_MATCH" or
                                                     verification_result.get("ic_verification", {}).get("verified"))
                                        
                                        if ic_success:
                                            st.success("✅ **IC Authentication Successful!**")
                                            
                                            # Access the nested ic_verification data
                                            ic_info = verification_result.get("ic_verification", verification_result)
                                            
                                            # Show IC with bounding boxes
                                            if "ic_with_bounding_boxes" in ic_info:
                                                st.markdown("#### 🎯 IC Card with Face Detection")
                                                face_count = ic_info.get("faces_detected", 0)
                                                
                                                if face_count >= 2:
                                                    st.success(f"🎉 **{face_count} faces detected** - IC appears authentic!")
                                                elif face_count == 1:
                                                    st.warning("⚠️ **1 face detected** - This may be normal for some IC types")
                                                else:
                                                    st.error("❌ **No faces detected** - IC may not be valid")
                                                
                                                # Display the IC with bounding boxes
                                                st.image(
                                                    ic_info["ic_with_bounding_boxes"], 
                                                    caption=f"IC Card with {face_count} detected face(s)",
                                                    use_container_width=True
                                                )
                                                
                                                # Show individual face crops if available
                                                if "detected_faces_info" in ic_info and ic_info["detected_faces_info"]:
                                                    st.markdown("##### 👤 Detected Faces")
                                                    
                                                    # Create columns for face display
                                                    if len(ic_info["detected_faces_info"]) > 1:
                                                        face_col1, face_col2 = st.columns(2)
                                                        
                                                        with face_col1:
                                                            st.markdown("**Main Face**")
                                                            if "main_face_image" in ic_info:
                                                                st.image(ic_info["main_face_image"], caption="Main face", width=150)
                                                            st.write(f"**Area:** {ic_info['detected_faces_info'][0]['area']:.0f} pixels")
                                                        
                                                        with face_col2:
                                                            st.markdown("**Ghost Face**") 
                                                            if "ghost_face_image" in ic_info:
                                                                st.image(ic_info["ghost_face_image"], caption="Ghost face", width=150)
                                                            if len(ic_info["detected_faces_info"]) > 1:
                                                                st.write(f"**Area:** {ic_info['detected_faces_info'][1]['area']:.0f} pixels")
                                                    else:
                                                        face_col1, face_col2 = st.columns([1, 2])
                                                        
                                                        with face_col1:
                                                            if "main_face_image" in ic_info:
                                                                st.image(ic_info["main_face_image"], caption="Face detected", width=150)
                                                            st.write(f"**Area:** {ic_info['detected_faces_info'][0]['area']:.0f} pixels")
                                                    
                                                        with face_col2:
                                                            st.info("🔍 **Only 1 face detected**\n\nFor full IC verification, 2 faces are needed (main + ghost). This shows the detected face for demo purposes.")
                                                
                                                # Show verification details
                                                with st.expander("🔍 Verification Details"):
                                                    if "verification_results" in ic_info:
                                                        st.markdown("##### 🤖 AI Model Results")
                                                        verification_results = ic_info["verification_results"]
                                                        
                                                        col1, col2 = st.columns(2)
                                                        for i, result in enumerate(verification_results):
                                                            with col1 if i % 2 == 0 else col2:
                                                                model = result.get('model', 'Unknown')
                                                                verified = result.get('verified', False)
                                                                distance = result.get('distance', 'N/A')
                                                                threshold = result.get('threshold', 'N/A')
                                                                
                                                                if verified:
                                                                    st.success(f"✅ **{model}**")
                                                                    st.write(f"Distance: {distance:.3f} ≤ {threshold}")
                                                                else:
                                                                    st.error(f"❌ **{model}**") 
                                                                    if 'error' in result:
                                                                        st.write(f"Error: {result['error']}")
                                                                    else:
                                                                        st.write(f"Distance: {distance:.3f} > {threshold}")
                                                        
                                                        verified_count = ic_info.get("verification_count", 0)
                                                        total_models = len(verification_results)
                                                        confidence = ic_info.get("confidence_score", 0)
                                                        
                                                        st.markdown("---")
                                                        st.write(f"**Overall Result:** {verified_count}/{total_models} models agree")
                                                        st.write(f"**Confidence:** {confidence:.1f}%")
                                                        required_majority = total_models / 2  # Use same logic as IC verification core
                                                        st.write(f"**Required:** At least {int(required_majority)} models must agree (majority)")
                                                        
                                                        if verified_count < required_majority:
                                                            st.warning("⚠️ **Insufficient model agreement** - Main face and ghost face may not be similar enough")
                                                    else:
                                                        st.json(ic_info.get("verification_details", {}))
                                            
                                            # Show student matching results
                                            if verification_result.get("student_found"):
                                                st.success("🎯 **Student Match Found!**")
                                                
                                                matched_student = verification_result.get("matched_student", {})
                                                st.session_state.ic_matched_student = matched_student
                                                
                                                # Display matched student info
                                                student_col1, student_col2 = st.columns([1, 2])
                                                
                                                with student_col1:
                                                    # Show student photo if available
                                                    image_path = matched_student.get('image_path', '')
                                                    if image_path and os.path.exists(image_path):
                                                        st.image(image_path, caption="Student Photo", width=120)
                                                    else:
                                                        st.warning("📷 Photo not found")
                                                
                                                with student_col2:
                                                    student_name = matched_student.get('name', 'Unknown')
                                                    student_id = matched_student.get('student_id') or matched_student.get('id', 'Unknown')
                                                    similarity = verification_result.get("similarity", 0.0)
                                                    
                                                    st.write(f"**👤 Name:** {student_name}")
                                                    st.write(f"**🆔 Student ID:** {student_id}")
                                                    st.write(f"**🎯 Similarity:** {similarity:.1%}")
                                                    
                                                    # Show confidence level
                                                    if similarity > 0.8:
                                                        st.success("🟢 High confidence match")
                                                    elif similarity > 0.6:
                                                        st.warning("🟡 Medium confidence match")
                                                    else:
                                                        st.error("🔴 Low confidence match")
                                                
                                                # Proceed to live verification
                                                st.markdown("---")
                                                if st.button("▶️ Proceed to Live Face Verification", use_container_width=True, type="primary"):
                                                    st.session_state.current_student = matched_student
                                                    st.session_state.ceremony_stage = "face_verifying"
                                                    st.session_state.qr_scan_time = time.time()
                                                    # Reset IC verification state
                                                    st.session_state.ic_verification_step = "upload"
                                                    st.session_state.ic_verification_result = None
                                                    st.session_state.ic_matched_student = None
                                                    # Reset image transformation states
                                                    st.session_state.ic_rotation_angle = 0
                                                    st.session_state.ic_flipped = False
                                                    st.rerun()
                                            else:
                                                st.warning("⚠️ **No Student Match Found**")
                                                st.info("The IC appears authentic, but no matching student was found in the database.")
                                                
                                                similarity_threshold = verification_result.get("similarity_threshold", 0.5)
                                                st.write(f"**Similarity threshold used:** {similarity_threshold:.1%}")
                                                
                                                # Show actual similarity scores for debugging
                                                similarity_scores = verification_result.get("similarity_scores", [])
                                                if similarity_scores:
                                                    st.markdown("##### 🔍 **Actual Similarity Scores**")
                                                    for score_info in similarity_scores:
                                                        student_name = score_info.get('student', 'Unknown')
                                                        student_id = score_info.get('student_id', 'Unknown')
                                                        similarity = score_info.get('similarity', 0.0)
                                                        
                                                        if similarity >= similarity_threshold:
                                                            st.success(f"✅ **{student_name}** ({student_id}): {similarity:.1%}")
                                                        elif similarity >= 0.2:
                                                            st.warning(f"⚠️ **{student_name}** ({student_id}): {similarity:.1%} (below threshold)")
                                                        else:
                                                            st.error(f"❌ **{student_name}** ({student_id}): {similarity:.1%} (too low)")
                                                    
                                                    # Show suggestion based on highest score
                                                    if similarity_scores:
                                                        best_score = max(similarity_scores, key=lambda x: x.get('similarity', 0))
                                                        best_similarity = best_score.get('similarity', 0.0)
                                                        if best_similarity >= 0.2:
                                                            st.info(f"💡 **Suggestion:** The closest match is **{best_score.get('student', 'Unknown')}** with {best_similarity:.1%} similarity. Consider lowering the threshold to {max(0.20, best_similarity-0.02):.0%} or try manual selection.")
                                                
                                                st.info("💡 You may need to register this student first, or try manual selection.")
                                                
                                                # Option to proceed with manual verification
                                                if st.button("📝 Try Manual Student Selection", key="ic_to_manual"):
                                                    # Reset IC verification states
                                                    st.session_state.ic_verification_step = "upload"
                                                    st.session_state.ic_verification_result = None
                                                    st.session_state.ic_matched_student = None
                                                    # Reset image transformation states
                                                    st.session_state.ic_rotation_angle = 0
                                                    st.session_state.ic_flipped = False
                                                    # Set flag to switch to manual mode
                                                    st.session_state.switch_to_manual = True
                                                    st.info("💡 Please select 'Manual Student Selection' from the dropdown above to continue.")
                                                    st.rerun()
                                        else:
                                            # Verification failed - show detailed error info
                                            st.error("❌ **IC Authentication Failed!**")
                                            
                                            # Check both in ic_verification dict and in direct result
                                            ic_info = verification_result.get("ic_verification", verification_result)
                                            
                                            # Show IC with bounding boxes first (even if verification failed)
                                            if "ic_with_bounding_boxes" in ic_info:
                                                st.markdown("#### 🎯 IC Card with Face Detection")
                                                face_count = ic_info.get("faces_detected", 0)
                                                
                                                if face_count >= 2:
                                                    st.info(f"ℹ️ **{face_count} faces detected** - but verification criteria not met")
                                                elif face_count == 1:
                                                    st.warning(f"⚠️ **Only {face_count} face detected** - IC verification requires 2 faces")
                                                else:
                                                    st.error("❌ **No faces detected** - please ensure IC is clearly visible")
                                                
                                                # Display the IC with bounding boxes
                                                st.image(
                                                    ic_info["ic_with_bounding_boxes"], 
                                                    caption=f"IC Card with {face_count} detected face(s)",
                                                    use_container_width=True
                                                )
                                                
                                                # Show individual face crops if available
                                                if "detected_faces_info" in ic_info and ic_info["detected_faces_info"]:
                                                    st.markdown("##### 👤 Detected Faces")
                                                    
                                                    face_col1, face_col2 = st.columns([1, 2])
                                                    
                                                    with face_col1:
                                                        if "main_face_image" in ic_info:
                                                            st.image(ic_info["main_face_image"], caption="Face detected", width=150)
                                                        
                                                        with face_col2:
                                                            st.info("🔍 **Only 1 face detected**\n\nIC verification requires 2 faces for authentication.")
                                            
                                            # Show detailed verification failure analysis
                                            if "verification_results" in ic_info:
                                                st.markdown("#### 🔍 Why Verification Failed")
                                                
                                                with st.expander("🤖 AI Model Analysis", expanded=True):
                                                    verification_results = ic_info["verification_results"]
                                                    
                                                    col1, col2 = st.columns(2)
                                                    for i, result in enumerate(verification_results):
                                                        with col1 if i % 2 == 0 else col2:
                                                            model = result.get('model', 'Unknown')
                                                            verified = result.get('verified', False)
                                                            distance = result.get('distance', 'N/A')
                                                            threshold = result.get('threshold', 'N/A')
                                                            
                                                            if verified:
                                                                st.success(f"✅ **{model}**")
                                                                st.write(f"Distance: {distance:.3f} ≤ {threshold}")
                                                            else:
                                                                st.error(f"❌ **{model}**") 
                                                                if 'error' in result:
                                                                    st.write(f"Error: {result['error']}")
                                                                else:
                                                                    st.write(f"Distance: {distance:.3f} > {threshold}")
                                                    
                                                    verified_count = ic_info.get("verification_count", 0)
                                                    total_models = len(verification_results)
                                                    confidence = ic_info.get("confidence_score", 0)
                                                    required_majority = total_models / 2  # Use same logic as IC verification core
                                                    
                                                    st.markdown("---")
                                                    st.error(f"**Result:** {verified_count}/{total_models} models agree (need {int(required_majority)})")
                                                    st.write(f"**Confidence:** {confidence:.1f}%")
                                                    
                                                    st.warning("""
                                                    **Possible reasons for failure:**
                                                    - 💡 Poor lighting conditions
                                                    - 🔍 Ghost face too faint or unclear  
                                                    - 📐 IC card at wrong angle
                                                    - 🌅 Shadows on the IC surface
                                                    - 📱 Image quality too low
                                                    """)
                                            
                                            # Use error handler for consistent display
                                            error_code = verification_result.get("error_code", "IC_INVALID")
                                            error_message = verification_result.get("error_message", "IC verification failed")
                                            error_details = verification_result.get("details", {})
                                            
                                            # Show error with recovery suggestions  
                                            ICErrorHandler.display_error_in_streamlit(
                                                error_code, 
                                                error_message, 
                                                details=error_details
                                            )
                                            
                                            # Add Try Again button for IC verification
                                            st.markdown("---")
                                            col1, col2 = st.columns(2)
                                            
                                            with col1:
                                                if st.button("🔄 Try Again", use_container_width=True, type="primary", key="ic_try_again"):
                                                    # Reset IC verification state to allow retry
                                                    st.session_state.ic_verification_step = "upload"
                                                    st.session_state.ic_verification_result = None
                                                    st.session_state.ic_matched_student = None
                                                    # Reset image transformation states
                                                    st.session_state.ic_rotation_angle = 0
                                                    st.session_state.ic_flipped = False
                                                    st.success("🔄 Resetting IC verification... Please upload a new IC image.")
                                                    st.rerun()
                                            
                                            with col2:
                                                if st.button("📝 Manual Selection", use_container_width=True, key="ic_to_manual_fallback"):
                                                    # Reset IC verification states
                                                    st.session_state.ic_verification_step = "upload"
                                                    st.session_state.ic_verification_result = None
                                                    st.session_state.ic_matched_student = None
                                                    # Reset image transformation states
                                                    st.session_state.ic_rotation_angle = 0
                                                    st.session_state.ic_flipped = False
                                                    # Set flag to switch to manual mode
                                                    st.session_state.switch_to_manual = True
                                                    st.info("💡 Please select 'Manual Student Selection' from the dropdown above to continue.")
                                                    st.rerun()
                                            
                                            if verification_result.get("allow_manual_override"):
                                                st.info("💡 You can proceed with manual verification if needed.")
                                                
                                                if st.button("🔄 Proceed with Manual Verification", key="manual_override_ic"):
                                                    st.info("📝 Manual IC verification - please verify student identity manually.")
                                    
                        
                        elif st.session_state.ic_verification_step == "confirm":
                            # Step 2: Confirm the matched student
                            st.markdown("**Step 2: Confirm Student Match** ✅")
                            
                            if st.session_state.ic_matched_student:
                                matched_student = st.session_state.ic_matched_student
                                
                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    image_path = matched_student.get('image_path', '')
                                    if image_path and os.path.exists(image_path):
                                        st.image(image_path, caption="Matched Student", width=150)
                                    else:
                                        st.warning("📷 Photo not found")
                                
                                with col2:
                                    st.write(f"**Name:** {matched_student.get('name', 'Unknown')}")
                                    st.write(f"**Student ID:** {matched_student.get('student_id', 'Unknown')}")
                                
                                col_confirm1, col_confirm2 = st.columns(2)
                                
                                with col_confirm1:
                                    if st.button("✅ Confirm Match", use_container_width=True, type="primary"):
                                        # Proceed to live face verification
                                        st.session_state.current_student = matched_student
                                        st.session_state.ceremony_stage = "face_verifying"
                                        st.session_state.qr_scan_time = time.time()
                                        # Reset IC verification state
                                        st.session_state.ic_verification_step = "upload"
                                        st.session_state.ic_verification_result = None
                                        st.session_state.ic_matched_student = None
                                        # Reset image transformation states
                                        st.session_state.ic_rotation_angle = 0
                                        st.session_state.ic_flipped = False
                                        st.rerun()
                                
                                with col_confirm2:
                                    if st.button("❌ Wrong Match", use_container_width=True):
                                        # Go back to upload step
                                        st.session_state.ic_verification_step = "upload"
                                        st.session_state.ic_verification_result = None
                                        st.session_state.ic_matched_student = None
                                        # Reset image transformation states
                                        st.session_state.ic_rotation_angle = 0
                                        st.session_state.ic_flipped = False
                                        st.rerun()
                    
                    elif scan_method == "📝 Manual Student Selection":
                        # Manual selection for demo/testing
                        student_options = [f"{s.get('name', 'Unknown')} ({s.get('student_id') or s.get('id', 'Unknown')})" for s in db]
                        selected_student_display = st.selectbox(
                            "🧑‍🎓 Select Student for Check-in",
                            student_options,
                            help="Select a registered student to simulate check-in"
                        )
                        
                        if selected_student_display:
                            # Extract student ID from selection
                            selected_id = selected_student_display.split('(')[1].replace(')', '')
                            selected_student = get_student_by_id(selected_id)
                            
                            if selected_student:
                                # Display student info
                                student_name = selected_student.get('name', 'Unknown')
                                student_id = selected_student.get('student_id') or selected_student.get('id')
                                st.markdown(f"**Selected:** {student_name}")
                                st.markdown(f"**ID:** {student_id}")
                                
                                # Check if already attended
                                has_attended, existing_record = check_already_attended(selected_id)
                                
                                if has_attended:
                                    st.warning(f"⚠️ Student already checked in today")
                                    st.info(f"Check-in time: {existing_record.get('check_in_time', 'Unknown')}")
                                    if st.button("🔄 Continue Anyway (Override)", key="manual_override"):
                                        st.session_state.current_student = selected_student
                                        st.session_state.ceremony_stage = "face_verifying"
                                        st.session_state.qr_scan_time = time.time()
                                        st.rerun()
                                else:
                                    # Proceed to verification
                                    if st.button(
                                        f"✅ Proceed to Verification", 
                                        use_container_width=True,
                                        type="primary"
                                    ):
                                        st.session_state.current_student = selected_student
                                        st.session_state.ceremony_stage = "face_verifying"
                                        st.session_state.qr_scan_time = time.time()
                                        st.rerun()
                
                elif st.session_state.ceremony_stage == "completed":
                    # Show completed student information
                    if st.session_state.current_student:
                        student = st.session_state.current_student
                        
                        st.success("✅ **Check-in Complete!**")
                        
                        # Student info card
                        with st.container():
                            st.markdown("#### 👤 Student Information")
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                image_path = normalize_path(student.get('image_path', ''))
                                if image_path and os.path.exists(image_path):
                                    st.image(image_path, width=120, caption="Registered Photo")
                                else:
                                    st.warning("📷 Photo not found")
                            
                            with col2:
                                # Safe field access
                                student_id = student.get('student_id') or student.get('id')
                                student_name = student.get('name', 'Unknown')
                                st.write(f"**🆔 Student ID:** {student_id}")
                                st.write(f"**👤 Name:** {student_name}")
                        
        
        # RIGHT PANEL: Face Verification / Status
        with col_right:
            if st.session_state.ceremony_stage in ["waiting", "qr_scanning"]:
                # Waiting state - show instructions
                st.markdown("### 🧍 Face Verification")
                st.markdown("""
                    <div style='text-align: center; padding: 40px; background-color: #f0f0f0; border-radius: 10px; opacity: 0.6;'>
                        <h2>🔒 Ready</h2>
                        <p>Please select student first</p>
                    </div>
                """, unsafe_allow_html=True)
            
            elif st.session_state.ceremony_stage == "face_verifying":
                # MAIN VERIFICATION INTERFACE - REAL IMAGE PROCESSING
                st.markdown("### 🔍 Face Verification")
                
                student = st.session_state.current_student
                if not student:
                    st.error("❌ No student data available")
                else:
                    student_id = student.get('student_id') or student.get('id')
                    student_name = student.get('name', 'Unknown')
                    
                    # Check if student has encoding
                    if not student.get('encoding'):
                        st.error("❌ Cannot verify: No face encoding found for this student")
                        st.info("💡 Please register this student's face first")
                        
                        # Manual override option
                        if st.button("⏭️ Manual Override", use_container_width=True, type="secondary"):
                            # Manual attendance entry
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            attendance_record = {
                                "student_id": student_id,
                                "name": student_name,
                                "check_in_time": current_time,
                                "verification_method": "Manual Override - No Encoding",
                                "device_id": "MANUAL_OVERRIDE",
                                "qr_scan_time": datetime.fromtimestamp(st.session_state.qr_scan_time).strftime("%Y-%m-%d %H:%M:%S"),
                                "face_verify_time": "MANUAL_OVERRIDE",
                                "confidence_score": 0.0
                            }
                            
                            success = save_attendance_record(attendance_record)
                            
                            if success:
                                st.session_state.verification_result = {
                                    "verified": True,
                                    "confidence": 0.0,
                                    "message": "Manual override - no face encoding",
                                    "timestamp": current_time
                                }
                                
                                # TTS announcement moved to completed stage to avoid rerun interruption
                                
                                st.session_state.ceremony_stage = "completed"
                                st.rerun()
                            else:
                                st.error("❌ Failed to record attendance")
                        return
                    
                    # FULL VERIFICATION INTERFACE
                    st.info(f"🎯 **Ready to verify:** {student_name}")
                    
                    # Verification method selection
                    verify_method = st.radio(
                        "📱 Choose Verification Method:",
                        ["📸 Take Photo with Camera", "📁 Upload Photo File"],
                        horizontal=True,
                        help="Choose the most convenient method for you"
                    )
                    
                    if verify_method == "📸 Take Photo with Camera":
                        st.markdown("#### 📸 Camera Verification")
                        st.info("💡 **Tips:** Look directly at the camera and ensure good lighting")
                        
                        if st.button("🚀 Start Camera Verification", use_container_width=True, type="primary"):
                            # Create verification animation
                            create_simple_spinner("🔄 Preparing camera verification...")
                            
                            # REAL IMAGE PROCESSING - Capture and verify face
                            face_img, captured_frame, capture_path = guided_face_capture(
                                target_student=student,
                                mode="verification",
                                save_path=CAPTURES_FOLDER
                            )
                            
                            if face_img is not None and captured_frame is not None:
                                create_simple_spinner("🧠 Analyzing face with AI...")
                                
                                # REAL FACE VERIFICATION - Perform face verification
                                student_encoding = student.get('encoding')
                                is_verified, confidence, msg = verify_face_encoding(
                                    captured_frame, student_encoding)
                                
                                # Store verification result and save attendance
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                                verification_data = {
                                    "verified": is_verified,
                                    "confidence": confidence,
                                    "message": msg,
                                    "capture_path": capture_path,
                                    "timestamp": current_time
                                }
                                
                                st.session_state.verification_result = verification_data
                                
                                # Save attendance record immediately if verification was successful
                                if is_verified:
                                    attendance_record = {
                                        "student_id": student_id,
                                        "name": student_name,
                                        "check_in_time": current_time,
                                        "qr_scan_time": datetime.fromtimestamp(st.session_state.qr_scan_time).strftime("%Y-%m-%d %H:%M:%S"),
                                        "face_verify_time": current_time,
                                        "confidence_score": float(confidence),
                                        "verify_photo": capture_path,
                                        "device_id": "Ceremony_Station_01",
                                        "verification_method": "Face Recognition"
                                    }
                                    
                                    save_attendance_record(attendance_record)
                                    
                                    # TTS announcement moved to completed stage to avoid rerun interruption
                                
                                st.session_state.ceremony_stage = "completed"
                                st.rerun()
                            else:
                                st.error("❌ Face capture failed. Please try again.")
                    
                    elif verify_method == "📁 Upload Photo File":
                        st.markdown("#### 📁 Photo Upload Verification")
                        st.info("💡 **Tips:** Upload a clear, well-lit photo of your face")
                        
                        # Upload interface
                        uploaded_file = st.file_uploader(
                            "Choose a photo file to upload:",
                            type=['jpg', 'jpeg', 'png'],
                            help="Upload a clear face photo for verification",
                            key="main_verify_upload"
                        )
                        
                        if uploaded_file is not None:
                            # Display uploaded image
                            uploaded_img = Image.open(uploaded_file)
                            uploaded_img = fix_image_orientation(uploaded_img)
                            st.image(uploaded_img, caption="📷 Uploaded Photo", width=200)
                            
                            if st.button("✅ Verify This Photo", use_container_width=True, type="primary"):
                                # Create verification animation
                                create_simple_spinner("🔄 Processing uploaded photo...")
                                
                                # REAL IMAGE PROCESSING - Convert PIL image to numpy array for verification
                                img_array = np.array(uploaded_img.convert('RGB'))
                                
                                create_simple_spinner("🧠 Comparing faces with AI...")
                                
                                # REAL FACE VERIFICATION - Perform face verification
                                student_encoding = student.get('encoding')
                                is_verified, confidence, msg = verify_face_encoding(
                                    img_array, student_encoding
                                )
                                
                                # Save uploaded image for record
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                capture_path = os.path.join(CAPTURES_FOLDER, f"{student_id}_{timestamp}_upload.jpg")
                                uploaded_img.save(capture_path)
                                
                                # Store verification result
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                                verification_data = {
                                    "verified": is_verified,
                                    "confidence": confidence,
                                    "message": msg,
                                    "capture_path": capture_path,
                                    "timestamp": current_time,
                                    "method": "upload"
                                }
                                
                                st.session_state.verification_result = verification_data
                                
                                # Save attendance record immediately if verification was successful
                                if is_verified:
                                    attendance_record = {
                                        "student_id": student_id,
                                        "name": student_name,
                                        "check_in_time": current_time,
                                        "qr_scan_time": datetime.fromtimestamp(st.session_state.qr_scan_time).strftime("%Y-%m-%d %H:%M:%S"),
                                        "face_verify_time": current_time,
                                        "confidence_score": float(confidence),
                                        "verify_photo": capture_path,
                                        "device_id": "Ceremony_Station_01",
                                        "verification_method": "Face Recognition (Upload)"
                                    }
                                    
                                    save_attendance_record(attendance_record)
                                    
                                    # TTS announcement moved to completed stage to avoid rerun interruption
                                
                                st.session_state.ceremony_stage = "completed"
                                st.rerun()
                    
                    # Manual override option at bottom
                    st.markdown("---")
                    st.markdown("#### 🛠️ Manual Override")
                    st.caption("Administrator can manually approve attendance if needed")
                    
                    if st.button("⚡ Manual Override", use_container_width=True, type="secondary"):
                        # Manual attendance entry without face verification
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        attendance_record = {
                            "student_id": student_id,
                            "name": student_name,
                            "check_in_time": current_time,
                            "verification_method": "Manual Override",
                            "device_id": "MANUAL_OVERRIDE",
                            "qr_scan_time": datetime.fromtimestamp(st.session_state.qr_scan_time).strftime("%Y-%m-%d %H:%M:%S"),
                            "face_verify_time": "MANUAL_OVERRIDE",
                            "confidence_score": 100.0
                        }
                        
                        success = save_attendance_record(attendance_record)
                        
                        if success:
                            st.session_state.verification_result = {
                                "verified": True,
                                "confidence": 100.0,
                                "message": "Manual override by administrator",
                                "timestamp": current_time
                            }
                            
                            # TTS announcement moved to completed stage to avoid rerun interruption
                            
                            st.session_state.ceremony_stage = "completed"
                            st.rerun()
                        else:
                            st.error("❌ Failed to record attendance")
            
            elif st.session_state.ceremony_stage == "completed":
                # Show completion status with enhanced feedback and 3-second pause
                result = st.session_state.verification_result
                student = st.session_state.current_student
                
                if not result or not student:
                    st.error("❌ No verification data available")
                else:
                    student_id = student.get('student_id') or student.get('id')
                    student_name = student.get('name', 'Unknown')
                    
                    if result["verified"]:
                        # Success case with enhanced visual feedback
                        # Initialize or reset states for this completion
                        # Use verification timestamp to detect fresh completion
                        current_verification_time = result.get('timestamp', '')
                        
                        if "last_verification_time" not in st.session_state or st.session_state.last_verification_time != current_verification_time:
                            # This is a new verification, not a rerun
                            st.session_state.completion_shown_time = time.time()
                            st.session_state.tts_played = False
                            st.session_state.last_verification_time = current_verification_time
                            st.balloons()
                        
                        # Enhanced success display
                        st.markdown(f"""
                        <div class="success-panel">
                            <h2 style="margin: 0; text-align: center;">🎉 Check-in Successful!</h2>
                            <p style="text-align: center; margin: 0.5rem 0; opacity: 0.9;">
                                Welcome to the ceremony, {student_name}!
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("#### ✅ Verification Details")
                        
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Display captured photo if available
                            if result.get("capture_path") and os.path.exists(result["capture_path"]):
                                st.image(result["capture_path"], caption="Verification Photo", width=120)
                            else:
                                st.info("📷")
                        
                        with col2:
                            st.write(f"**👤 Student:** {student_name}")
                            st.write(f"**🆔 ID:** {student_id}")
                            st.write(f"**🎯 Confidence:** {result['confidence']:.1f}%")
                            st.write(f"**⏰ Time:** {result['timestamp']}")
                        
                        # Manual progression - show next button after 2 seconds
                        elapsed = time.time() - st.session_state.completion_shown_time
                        if elapsed > 2.0:
                            # Play TTS announcement after countdown completes to avoid rerun interruption
                            # TTS is played only once after the 2-second countdown
                            if not st.session_state.get('tts_played', False):
                                announce_student_attendance(
                                    student_name,
                                    language='en',
                                    auto_mode=False
                                )
                                st.session_state.tts_played = True
                            
                            if st.button("👥 Next Student", use_container_width=True, type="primary", key="next_student_completion"):
                                st.session_state.ceremony_stage = "waiting"
                                st.session_state.current_student = None
                                st.session_state.qr_scan_time = None
                                st.session_state.verification_result = None
                                # Clean up all completion-related states
                                if "completion_shown_time" in st.session_state:
                                    del st.session_state.completion_shown_time
                                if "tts_played" in st.session_state:
                                    del st.session_state.tts_played
                                if "last_verification_time" in st.session_state:
                                    del st.session_state.last_verification_time
                                st.rerun()
                        else:
                            st.info(f"🎉 Enjoy the moment... ({2.0 - elapsed:.1f}s)")
                            time.sleep(0.1)
                            st.rerun()
                    else:
                        # Failure case
                        st.error("❌ **Verification Failed**")
                        
                        st.markdown("#### ⚠️ Verification Details")
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Display captured photo if available
                            if result.get("capture_path") and os.path.exists(result["capture_path"]):
                                st.image(result["capture_path"], caption="Attempted Photo", width=120)
                            else:
                                st.info("📷")
                        
                        with col2:
                            st.write(f"**👤 Student:** {student_name}")
                            st.write(f"**🆔 ID:** {student_id}")
                            st.write(f"**🎯 Confidence:** {result['confidence']:.1f}%")
                            st.write(f"**❌ Reason:** {result['message']}")
                        
                        # Options for failed verification
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("🔄 Try Again", use_container_width=True):
                                st.session_state.ceremony_stage = "face_verifying"
                                st.session_state.verification_result = None
                                # Clean up completion states when trying again
                                if "completion_shown_time" in st.session_state:
                                    del st.session_state.completion_shown_time
                                if "tts_played" in st.session_state:
                                    del st.session_state.tts_played
                                if "last_verification_time" in st.session_state:
                                    del st.session_state.last_verification_time
                                st.rerun()
                        
                        with col2:
                            if st.button("⏭️ Manual Override", use_container_width=True):
                                # Manual attendance entry
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                attendance_record = {
                                    "student_id": student_id,
                                    "name": student_name,
                                    "check_in_time": current_time,
                                    "qr_scan_time": datetime.fromtimestamp(st.session_state.qr_scan_time).strftime("%Y-%m-%d %H:%M:%S"),
                                    "face_verify_time": "MANUAL_OVERRIDE",
                                    "confidence_score": 0.0,
                                    "verify_photo": result.get("capture_path", ""),
                                    "device_id": "Ceremony_Station_01_MANUAL",
                                    "verification_method": "Manual Override"
                                }
                                success = save_attendance_record(attendance_record)
                                if success:
                                    # Update result to show success
                                    st.session_state.verification_result = {
                                        "verified": True,
                                        "confidence": 0.0,
                                        "message": "Manual override by administrator",
                                        "timestamp": current_time,
                                        "capture_path": result.get("capture_path", "")
                                    }
                                    
                                    # TTS announcement moved to completed stage to avoid rerun interruption
                                    
                                    
                                    st.success("📝 Manual attendance recorded!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to record manual attendance")
        
        # BOTTOM STATUS PANEL
        st.markdown("---")
        st.markdown("### 📊 Today's Status")
        
        # Load today's attendance
        today_attendance = load_attendance()
        today = datetime.now().strftime("%Y-%m-%d")
        today_records = [r for r in today_attendance if r.get("check_in_time", "").startswith(today)]
        
        # Status metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Registered", len(db))
        with col2:
            st.metric("Checked In Today", len(today_records))
        with col3:
            remaining = len(db) - len(today_records)
            st.metric("Remaining", remaining)
        with col4:
            completion_rate = (len(today_records) / len(db)) * 100 if len(db) > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Live Status Tab
    with tab2:
        st.markdown("### 📊 Live Attendance Status")
        
        # Refresh button
        if st.button("🔄 Refresh Status"):
            st.rerun()
        
        # Display attendance analysis
        analysis = analyze_attendance_data()
        
        if analysis:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Students", analysis['total_registered'])
            with col2:
                st.metric("Present", analysis['attended_count'])
            with col3:
                st.metric("Absent", analysis['remaining_count'])
            with col4:
                st.metric("Attendance Rate", f"{analysis['attendance_rate']:.1f}%")
            
            st.markdown("---")
            
            # Recent check-ins
            st.markdown("#### 📝 Recent Check-ins")
            
            recent_checkins = analysis['today_attended'][-5:]  # Last 5 check-ins
            
            if recent_checkins:
                for record in reversed(recent_checkins):  # Show most recent first
                    check_time = record.get('check_in_time', 'Unknown')
                    student_name = record.get('name', 'Unknown')
                    st.write(f"✅ **{student_name}** - {check_time}")
            else:
                st.info("No check-ins recorded today yet.")
        else:
            st.info("No attendance data available.")