"""
Student Portal - Mobile-Optimized Self-Service Interface
Features: Login, Face Registration, Self Check-in, Status Dashboard
"""
import streamlit as st
import os
import time
from datetime import datetime
from PIL import Image
import json

# Import required modules
from utils.auth import AuthManager
try:
    from utils.auth import rate_limiter
except ImportError:
    # Create a simple rate limiter if import fails
    class SimpleRateLimiter:
        def is_rate_limited(self, key, max_attempts=3, window_minutes=60):
            return False, 0
    rate_limiter = SimpleRateLimiter()
from utils.mobile_ui import MobileUI, init_mobile_ui
from utils.config import setup_directories, UPLOAD_FOLDER, CAPTURES_FOLDER
from core.database import *
from core.face_module import *
import utils.image_processing as img_proc

# Page configuration
st.set_page_config(
    page_title="Student Portal | TARUMT Graduation",
    page_icon="📱", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize mobile UI and authentication
init_mobile_ui()
AuthManager.init_session_states()
setup_directories()

# Ensure rate limiter is initialized
if "rate_limit_data" not in st.session_state:
    st.session_state.rate_limit_data = {}

# Apply consistent design system from config
from utils.config import CUSTOM_CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Add Student Portal specific styles including login container
st.markdown("""
<style>
/* Force hide sidebar completely */
section[data-testid="stSidebar"] {display: none !important;}
.css-1d391kg {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}

/* Login container using Momento design - SAME AS STAFF PORTAL */
.login-container {
    max-width: 450px;
    margin: 3rem auto;
    padding: 3rem 2.5rem;
    background: var(--surface-color);
    border-radius: var(--radius-medium);
    box-shadow: var(--shadow-medium);
    border: 1px solid var(--border-light);
    position: relative;
}

.login-header {
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
}

.login-header h2 {
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-weight: 600;
    font-size: 1.75rem;
}

/* Add centered blue divider line consistent with main portal */
.login-divider {
    width: 60px; 
    height: 2px; 
    background: linear-gradient(90deg, #74B9FF, #0984E3); 
    margin: 1.5rem auto; 
    border-radius: 2px;
}

.login-icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #E5E5E5, #F8F8F8);
    border-radius: 20px;
    margin: 0 auto 1.5rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    box-shadow: 0 4px 16px rgba(26, 26, 26, 0.08);
    color: #1A1A1A;
    border: 2px solid #E5E5E5;
}

/* Remove main padding when sidebar is hidden */
.main {
    margin-left: 0 !important;
    padding-left: 2rem !important;
}

/* Ultra-specific selectors to override Streamlit's button styling - SAME AS STAFF PORTAL */
.stButton > button[kind="primary"],
button[kind="primary"],
.st-emotion-cache-18wcnp,
button.st-emotion-cache-18wcnp,
.stForm button[kind="primary"],
.stForm .stButton > button[kind="primary"] {
    background-color: #2D3436 !important;
    background: linear-gradient(135deg, #2D3436 0%, #636E72 100%) !important;
    border: 1px solid rgba(99, 110, 114, 0.3) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 12px rgba(45, 52, 54, 0.15) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    height: 48px !important;
    min-height: 48px !important;
}

.stButton > button[kind="primary"]:hover,
button[kind="primary"]:hover,
.st-emotion-cache-18wcnp:hover,
button.st-emotion-cache-18wcnp:hover,
.stForm button[kind="primary"]:hover,
.stForm .stButton > button[kind="primary"]:hover {
    background-color: #636E72 !important;
    background: linear-gradient(135deg, #636E72 0%, #2D3436 100%) !important;
    border-color: rgba(99, 110, 114, 0.4) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(45, 52, 54, 0.25) !important;
    color: white !important;
}

.stButton > button[kind="primary"]:active,
button[kind="primary"]:active,
.st-emotion-cache-18wcnp:active,
button.st-emotion-cache-18wcnp:active,
.stForm button[kind="primary"]:active,
.stForm .stButton > button[kind="primary"]:active {
    transform: translateY(0px) !important;
    box-shadow: 0 4px 12px rgba(45, 52, 54, 0.15) !important;
}

/* Hide the radio button completely for tab navigation */
.stRadio { 
    display: none !important; 
}

/* Student Portal Header */
.student-header {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 12px rgba(45, 52, 54, 0.08);
    border: 1px solid #e9ecef;
}

.student-info h1 {
    color: #2d3436 !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

.student-info p {
    color: #636e72 !important;
    font-size: 0.9rem !important;
    margin: 0.25rem 0 0 0 !important;
}

/* Simple tab navigation */
.nav-pills {
    display: flex;
    background: #f1f3f5;
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 2rem;
    gap: 4px;
}

.nav-pill {
    flex: 1;
    padding: 12px 16px;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    border: none;
    background: transparent;
    color: #636e72;
    transition: all 0.2s ease;
}

.nav-pill.active {
    background: white;
    color: #2d3436;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Content cards */
.content-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(45, 52, 54, 0.08);
    border: 1px solid #e9ecef;
}

.card-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e9ecef;
}

.card-title {
    color: #2d3436 !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.metric-item {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    border: 1px solid #e9ecef;
}

.metric-label {
    color: #636e72 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 !important;
}

.metric-value {
    color: #2d3436 !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin: 0.5rem 0 0 0 !important;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}

.status-badge.success {
    background: rgba(0, 184, 148, 0.1);
    color: #00b894;
}

.status-badge.warning {
    background: rgba(255, 118, 117, 0.1);
    color: #ff7675;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #00b894, #00d084);
    border-radius: 4px;
}

/* Footer consistent with login */
.student-footer {
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
    border-top: 1px solid var(--border-color);
    background: var(--surface-color);
}

.footer-text {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    margin: 0 !important;
}

.footer-subtitle {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    margin: 0.25rem 0 0 0 !important;
}
</style>
""", unsafe_allow_html=True)

# Check authentication status
is_authenticated = AuthManager.is_authenticated() and AuthManager.get_user_type() == "student"

def student_login_form():
    """Display modern student login form - Momento design"""
    
    with st.container():
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div class="login-icon">📱</div>
                <h2>Student  Portal  Access</h2>
                <div class="login-divider"></div>
                <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.5;">Enter your Student ID to access your graduation portal</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form with modern styling
        with st.form("student_login_form"):
            student_id = st.text_input(
                "Student ID",
                placeholder="Enter your student ID (e.g., 24WMR12345)",
                help="Use your official student ID to log in",
                key="login_student_id"
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                login_submitted = st.form_submit_button("📱 Login to Student Portal", use_container_width=True, type="primary")
        
        if login_submitted:
            if not student_id:
                st.error("⚠️ Please enter your Student ID")
                return
            
            # Check rate limiting
            is_limited, remaining = rate_limiter.is_rate_limited(f"login_{student_id}", max_attempts=5, window_minutes=15)
            if is_limited:
                st.error("🔒 Too many login attempts. Please try again in 15 minutes.")
                return
            
            # Record attempt
            rate_limiter.record_attempt(f"login_{student_id}")
            
            # Attempt login
            success, message, student_data = AuthManager.student_login(student_id)
            
            if success:
                st.success(f"✅ {message}")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    # Back button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Portal Selection", use_container_width=True):
            st.switch_page("app.py")


def register_face_photo(image, student_data, method):
    """Process face registration"""
    student_id = student_data.get('student_id') or student_data.get('id')
    
    with st.spinner("🔄 Processing your photo..."):
        # Record rate limiting attempt
        rate_limiter.record_attempt(f"face_reg_{student_id}")
        
        # Validate image
        is_valid, validation_msg = validate_image(image)
        
        if not is_valid:
            MobileUI.mobile_alert(f"Photo validation failed: {validation_msg}", "error")
            return
        
        # Generate face encoding
        encoding, encoding_msg = generate_face_encoding(image)
        
        if not encoding:
            MobileUI.mobile_alert(f"Face processing failed: {encoding_msg}", "error")
            st.info("💡 Try taking another photo with better lighting and face positioning")
            return
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{student_id}_{timestamp}_student_reg.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        
        image.save(image_path)
        
        # Update student record
        updates = {
            'encoding': encoding,
            'image_path': image_path,
            'registration_method': f'Student Portal ({method})',
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        update_student(student_id, updates)
        
        # Success
        MobileUI.mobile_alert("🎉 Face registration successful!", "success")
        st.balloons()
        
        # Clear re-registration flag
        if 'allow_reregistration' in st.session_state:
            del st.session_state.allow_reregistration
        
        time.sleep(2)
        st.rerun()


def self_checkin_tab():
    """Self check-in functionality"""
    st.markdown("### ✅ Self Check-in")
    
    student_id = st.session_state.student_id
    student_data = get_student_by_id(student_id)
    
    if not student_data:
        MobileUI.mobile_alert("Student data not found", "error")
        return
    
    student_name = student_data.get('name', 'Student')
    
    # Check if already attended today
    has_attended, existing_record = check_already_attended(student_id)
    
    if has_attended:
        MobileUI.mobile_alert(f"You've already checked in today!", "success")
        
        st.markdown("#### 📋 Your Check-in Details:")
        check_time = existing_record.get('check_in_time', 'Unknown')
        method = existing_record.get('verification_method', 'Unknown')
        
        col1, col2 = st.columns(2)
        with col1:
            MobileUI.mobile_metric("Check-in Time", check_time.split(' ')[1] if ' ' in check_time else check_time, icon="⏰")
        with col2:
            MobileUI.mobile_metric("Method", method, icon="🔍")
        
        st.info("🎓 You're all set for the graduation ceremony!")
        return
    
    # Check if face is registered first
    if not student_data.get('encoding'):
        st.warning("⚠️ Face not registered. Please register your face first.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📸 Register Face Photo", use_container_width=True, type="primary"):
                st.session_state.student_tab = "📊 Dashboard"
                st.session_state.show_face_registration = True
                st.rerun()
        with col2:
            if st.button("🔄 Go to Dashboard", use_container_width=True):
                st.session_state.student_tab = "📊 Dashboard"
                st.rerun()
        return
    
    # Simple photo guide
    st.info("👤 **Upload Face Photo**: Take/upload a clear photo of your face for identity verification")
    
    # Simple upload interface
    st.markdown("**📂 Upload your photo for verification:**")
    
    uploaded_verify_file = MobileUI.mobile_file_uploader(
        "Choose photo",
        key="checkin_upload",
        help_text="Upload a clear photo of your face"
    )
    
    if uploaded_verify_file is not None:
        # Process uploaded image
        verify_pil = Image.open(uploaded_verify_file)
        
        # Fix orientation
        try:
            from utils.image_processing import fix_image_orientation
            verify_pil = fix_image_orientation(verify_pil)
        except:
            pass
        
        # Show uploaded image
        st.image(verify_pil, caption="Your verification photo", width=250)
        
        # Verify button
        if st.button("🔍 Verify & Check-in", use_container_width=True, type="primary"):
            perform_face_checkin(verify_pil, student_id, student_name, student_data)
        
        # Simple tips below
        st.caption("💡 Make sure your face is clearly visible and well-lit")


def perform_face_checkin(image, student_id, student_name, student_data):
    """Perform face verification check-in"""
    with st.spinner("🔍 Verifying your identity..."):
        # Convert PIL to numpy array
        import numpy as np
        img_array = np.array(image.convert('RGB'))
        
        # Perform face verification
        student_encoding = student_data.get('encoding')
        is_verified, confidence, message = verify_face_encoding(img_array, student_encoding)
        
        if is_verified:
            MobileUI.mobile_alert(f"Identity verified! Confidence: {confidence:.1f}%", "success")
            
            # Record attendance
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            attendance_record = {
                "student_id": student_id,
                "name": student_name,
                "check_in_time": current_time,
                "verification_method": "Student Portal - Face Verification",
                "device_id": "Student_Portal_Face_Verify",
                "face_verify_time": current_time,
                "confidence_score": float(confidence)
            }
            
            success = save_attendance_record(attendance_record)
            
            if success:
                st.balloons()
                st.success("🎉 Face verification check-in successful!")
                time.sleep(2)
                st.rerun()
            else:
                MobileUI.mobile_alert("Failed to record attendance", "error")
        else:
            MobileUI.mobile_alert(f"Face verification failed: {message}", "error")
            st.info("💡 Try taking another photo with better lighting or positioning")

def status_dashboard_tab():
    """Student status dashboard"""
    
    student_id = st.session_state.student_id
    student_data = get_student_by_id(student_id)
    
    if not student_data:
        st.error("Student data not found")
        return
    
    student_name = student_data.get('name', 'Student')
    has_face = student_data.get('encoding') is not None
    
    # Action buttons for quick access
    if not has_face:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📸 Register Face Photo", key="quick_face_reg", type="primary", use_container_width=True):
                st.session_state.show_face_registration = True
    
    # Graduation Checklist - Pure Streamlit components
    has_attended, attendance_record = check_already_attended(student_id)
    
    # Simple header
    st.subheader("📋 Graduation Checklist")
    st.markdown("")  # Add some space
    
    # Student Record
    col1, col2, col3 = st.columns([0.5, 4, 1.5])
    with col1:
        st.markdown("👤")
    with col2:
        st.markdown("**Student Record**")
        st.caption("Your record is in the system")
    with col3:
        st.success("Complete")
    
    # Face Photo
    col1, col2, col3 = st.columns([0.5, 4, 1.5])
    with col1:
        st.markdown("📸")
    with col2:
        st.markdown("**Face Photo**")
        if has_face:
            st.caption("Face photo registered")
        else:
            st.caption("Face photo required")
    with col3:
        if has_face:
            st.success("Complete")
        else:
            st.warning("Pending")
    
    # Check-in
    col1, col2, col3 = st.columns([0.5, 4, 1.5])
    with col1:
        st.markdown("✅")
    with col2:
        st.markdown("**Check-in**")
        if has_attended:
            st.caption("Attendance recorded")
        else:
            st.caption("Attendance pending")
    with col3:
        if has_attended:
            st.success("Complete")
        else:
            st.warning("Pending")
    
    st.markdown("---")
    
    # Overall status
    completed_items = sum([True, has_face, has_attended])
    total_items = 3
    
    if completed_items == total_items:
        st.success("🎉 Ready for graduation!")
    else:
        remaining = total_items - completed_items
        st.warning(f"⏳ {remaining} item(s) remaining")
    
    st.markdown("---")
    
    # Inline Face Registration (if requested)
    if st.session_state.get('show_face_registration', False) and not has_face:
        st.markdown("---")
        st.markdown("#### 📸 Face Registration")
        
        # Check rate limiting
        is_limited, remaining = rate_limiter.is_rate_limited(f"face_reg_{student_id}", max_attempts=3, window_minutes=60)
        if is_limited:
            MobileUI.mobile_alert("Face registration limit reached. Please try again in 1 hour.", "warning")
            if st.button("❌ Cancel Registration", key="cancel_face_reg"):
                st.session_state.show_face_registration = False
                st.rerun()
            return
        
        st.info("💡 **Tips**: Look directly at camera, ensure good lighting, remove glasses if possible")
        
        reg_method = st.radio(
            "📱 Registration Method",
            ["📸 Take Photo with Camera", "📂 Upload Photo File"],
            horizontal=True,
            help="Choose the most convenient method for you",
            key="dashboard_reg_method"
        )
        
        if reg_method == "📸 Take Photo with Camera":
            camera_image = MobileUI.mobile_camera_input(
                "Take your graduation photo",
                key="dashboard_face_reg_camera",
                help_text="Make sure your face is clearly visible and well-lit"
            )
            
            if camera_image is not None:
                # Process and validate image
                uploaded_img = Image.open(camera_image)
                
                # Fix orientation
                try:
                    from utils.image_processing import fix_image_orientation
                    uploaded_img = fix_image_orientation(uploaded_img)
                except:
                    pass
                
                # Display captured image
                st.image(uploaded_img, caption="📷 Captured Photo", width=300)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Register This Photo", use_container_width=True, type="primary", key="confirm_camera_reg"):
                        register_face_photo(uploaded_img, student_data, "camera")
                        st.session_state.show_face_registration = False
                with col2:
                    if st.button("❌ Cancel", use_container_width=True, key="cancel_camera_reg"):
                        st.session_state.show_face_registration = False
                        st.rerun()
        
        elif reg_method == "📂 Upload Photo File":
            uploaded_file = MobileUI.mobile_file_uploader(
                "Choose your graduation photo",
                key="dashboard_face_reg_upload",
                help_text="Upload a clear photo of your face (JPG, PNG)"
            )
            
            if uploaded_file is not None:
                # Process uploaded image
                uploaded_img = Image.open(uploaded_file)
                
                # Fix orientation
                try:
                    from utils.image_processing import fix_image_orientation
                    uploaded_img = fix_image_orientation(uploaded_img)
                except:
                    pass
                
                # Display uploaded image
                st.image(uploaded_img, caption="📂 Uploaded Photo", width=300)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Register This Photo", use_container_width=True, type="primary", key="confirm_upload_reg"):
                        register_face_photo(uploaded_img, student_data, "upload")
                        st.session_state.show_face_registration = False
                with col2:
                    if st.button("❌ Cancel", use_container_width=True, key="cancel_upload_reg"):
                        st.session_state.show_face_registration = False
                        st.rerun()
        
        # Cancel button at bottom
        st.markdown("---")
        if st.button("❌ Cancel Face Registration", use_container_width=True, key="cancel_face_reg_bottom"):
            st.session_state.show_face_registration = False
            st.rerun()

def qr_code_tab():
    """QR Code viewing and download functionality"""
    from core.qr_module import generate_qr_code
    from utils.config import QR_FOLDER
    
    student_id = st.session_state.student_id
    student_data = get_student_by_id(student_id)
    
    if not student_data:
        st.error("Student data not found")
        return
    
    student_name = student_data.get('name', 'Student')
    
    st.markdown("### 🔍 Your QR Code")
    st.markdown("Use this QR code for quick check-in at the graduation ceremony")
    
    # QR code path
    qr_filename = f"{student_id}_qr.png"
    qr_path = os.path.join(QR_FOLDER, qr_filename)
    
    # Check if QR code exists, generate if not
    if not os.path.exists(qr_path):
        with st.spinner("🔄 Generating your QR code..."):
            generated_path, message = generate_qr_code(student_id, student_name, QR_FOLDER)
            if generated_path:
                st.success(f"✅ {message}")
                qr_path = generated_path
            else:
                st.error(f"❌ {message}")
                return
    
    # Display QR code
    if os.path.exists(qr_path):
        try:
            # Load and display QR code image
            qr_image = Image.open(qr_path)
            
            # Create centered display
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(qr_image, caption=f"QR Code for {student_name}", width=300)
            
            st.markdown("---")
            
            # Instructions
            st.markdown("#### 📋 How to use your QR code:")
            st.markdown("""
            1. **Save to your phone**: Download the QR code image below
            2. **Keep it handy**: Have it ready on graduation day
            3. **Show at check-in**: Present the QR code to the scanning station
            4. **Wait for confirmation**: Look for the green light confirmation
            """)
            
            st.markdown("---")
            
            # Download functionality
            with open(qr_path, "rb") as file:
                qr_bytes = file.read()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📱 Download QR Code",
                    data=qr_bytes,
                    file_name=f"{student_id}_graduation_qr.png",
                    mime="image/png",
                    use_container_width=True,
                    type="primary"
                )
            
            # QR code info
            st.markdown("---")
            st.markdown("#### ℹ️ QR Code Information:")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Student ID", student_id)
            with col2:
                st.metric("Student Name", student_name)
            
            # Tips
            st.info("""
            💡 **Tips for best results:**
            - Save the QR code to your phone's photo gallery
            - Ensure your phone screen brightness is at maximum
            - Clean your phone screen before showing the QR code
            - Have a backup printed copy if possible
            """)
            
        except Exception as e:
            st.error(f"Error displaying QR code: {str(e)}")
    else:
        st.error("QR code not found and could not be generated")

def main():
    """Main student portal interface"""
    
    if not is_authenticated:
        student_login_form()
        return
    
    # Authenticated student interface
    student_name = st.session_state.user_name
    student_id = st.session_state.student_id
    
    # Enhanced header with better styling
    st.markdown("""
    <div style="
        background: white; 
        border-bottom: 1px solid #e9ecef; 
        padding: 2rem 0; 
        margin: -1rem -1rem 3rem -1rem;
        box-shadow: 0 2px 12px rgba(45, 52, 54, 0.08);
    ">
        <div style="text-align: center;">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 700; color: #2d3436; letter-spacing: 2px;">STUDENT PORTAL</h1>
            <div style="width: 60px; height: 3px; background: #74b9ff; margin: 1rem auto; border-radius: 2px;"></div>
            <p style="margin: 0.5rem 0 0 0; font-size: 1rem; color: #636e72; font-weight: 500;">TARUMT Graduation System</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Student info - wider and more prominent
    st.markdown(f"""
    <div class="content-card" style="margin-bottom: 2rem; padding: 2rem;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="flex: 1;">
                <h2 style="margin: 0; color: #2d3436; font-size: 1.5rem; font-weight: 600;">🎓 {student_name}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #636e72; font-size: 1rem;">Student ID: {student_id}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout button positioned better
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("🚪 Logout", key="student_logout", use_container_width=True):
            AuthManager.logout()
            st.success("👋 Logged out successfully!")
            time.sleep(1)
            st.switch_page("app.py")
    
    # Initialize tab state
    if "student_tab" not in st.session_state:
        st.session_state.student_tab = "📊 Dashboard"
    
    # Simple Navigation - Only functional buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
            st.session_state.student_tab = "📊 Dashboard"
            st.rerun()
    with col2:
        if st.button("🔍 My QR Code", key="nav_qr", use_container_width=True):
            st.session_state.student_tab = "🔍 My QR Code"
            st.rerun()
    with col3:
        if st.button("✅ Self Check-in", key="nav_checkin", use_container_width=True):
            st.session_state.student_tab = "✅ Self Check-in"
            st.rerun()
    
    selected_tab = st.session_state.student_tab
    
    # Update tab state if changed
    if selected_tab != st.session_state.student_tab:
        st.session_state.student_tab = selected_tab
        st.rerun()
    
    st.markdown("---")
    
    # Route to appropriate tab
    if selected_tab == "📊 Dashboard":
        status_dashboard_tab()
    elif selected_tab == "🔍 My QR Code":
        qr_code_tab()
    elif selected_tab == "✅ Self Check-in":
        self_checkin_tab()
    
    # Subtle Footer - blend with background
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; margin-top: 3rem; color: #a0a0a0; font-size: 0.75rem;">
        TARUMT Student Portal • 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()