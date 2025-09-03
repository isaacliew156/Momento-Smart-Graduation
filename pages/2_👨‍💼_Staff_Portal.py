"""
Staff Portal - Password Protected Access to Full System
Integrates all existing functionality with authentication
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import authentication and utilities
from utils.auth import AuthManager
from utils.config import (
    PAGE_TITLE, PAGE_ICON, LAYOUT, PAGES, CUSTOM_CSS,
    setup_directories, get_current_config
)
from utils.session_manager import SessionManager
from utils.ui_helpers import initialize_face_service, add_performance_monitor
from utils.simple_clock import render_nav_clock

# Page configuration
st.set_page_config(
    page_title="Staff Portal | TARUMT Graduation", 
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="collapsed"  # Force sidebar collapsed
)

# Initialize authentication
AuthManager.init_session_states()
setup_directories()

# Check if staff is authenticated
if not AuthManager.is_authenticated() or AuthManager.get_user_type() != "staff":
    
    # Apply Momento design system + login styles
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Additional styles for login and sidebar hiding
    st.markdown("""
    <style>
    /* Force hide sidebar completely */
    section[data-testid="stSidebar"] {display: none !important;}
    .css-1d391kg {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    
    /* Login container using Momento design */
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
    
    /* Remove the misaligned blue line from container */
    
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
    
    /* Ultra-specific selectors to override Streamlit's button styling */
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
        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.2) !important;
        background-color: #2D3436 !important;
        background: linear-gradient(135deg, #2D3436 0%, #636E72 100%) !important;
    }
    
    /* Integrated logout button styling - matches status bar */
    .stButton > button[type="secondary"] {
        background: linear-gradient(135deg, rgba(45, 52, 54, 0.03), rgba(99, 110, 114, 0.02)) !important;
        border: 1px solid rgba(45, 52, 54, 0.06) !important;
        border-left: none !important;
        border-radius: 0 12px 12px 0 !important;
        color: #2D3436 !important;
        padding: 0.6rem 0.8rem !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        height: 2.5rem !important;
        min-height: 2.5rem !important;
        transition: all 0.2s ease !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-sizing: border-box !important;
    }
    
    .stButton > button[type="secondary"]:hover {
        background: linear-gradient(135deg, rgba(45, 52, 54, 0.08), rgba(99, 110, 114, 0.05)) !important;
        transform: translateY(-1px) !important;
        border-color: rgba(45, 52, 54, 0.12) !important;
        border-left: none !important;
    }
    
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div class="login-icon">👨‍💼</div>
                <h2>Staff  Portal  Access</h2>
                <div class="login-divider"></div>
                <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.5;">Enter your password to access the complete graduation management system</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add testing guide using Streamlit native component
        st.success("🔑 **Test Password**: `admin123`")
        
        # Login form
        with st.form("staff_login"):
            password = st.text_input(
                "Staff Password",
                type="password",
                placeholder="Enter staff password",
                help="Contact system administrator if you don't have the password"
            )
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                login_button = st.form_submit_button("🔐 Login to Staff Portal", use_container_width=True, type="primary")
            
            if login_button:
                if password:
                    success, message = AuthManager.staff_login(password)
                    if success:
                        st.success(message)
                        # Brief delay to show success message before rerunning
                        import time
                        time.sleep(0.5)
                        st.rerun()  # Refresh to show authenticated content
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please enter the staff password")
        
        # Back to portal selection
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("← Back to Portal Selection", use_container_width=True):
                st.switch_page("app.py")
    
    st.stop()

# Create truly integrated status bar using absolute positioning
session_info = AuthManager.get_session_info()

# Create status bar with integrated logout using Streamlit columns
col1, col2 = st.columns([4, 1])

with col1:
    # Status bar container
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(45, 52, 54, 0.03), rgba(99, 110, 114, 0.02));
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(45, 52, 54, 0.06);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        height: 2.5rem;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    ">
        <span style="
            color: #2D3436;
            font-weight: 600;
            font-size: 0.95rem;
        ">🛡️ Staff Portal</span>
        <span style="
            color: rgba(45, 52, 54, 0.6);
            font-size: 0.85rem;
            font-weight: 400;
        ">Active since {session_info['login_time'].strftime('%H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Simple logout button aligned with status bar
    if st.button("👋 Logout", key="logout_btn", type="secondary", use_container_width=True):
        AuthManager.logout() 
        st.switch_page("app.py")

# Now integrate the existing staff system
# Import all the existing views
from staff_views.home import render_home
from staff_views.student_registration import render_student_registration
from staff_views.qr_management import render_qr_management
from staff_views.ceremony_attendance import render_ceremony_attendance
from staff_views.attendance_report import render_attendance_report
from staff_views.about import render_about

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize sidebar visibility state
if "sidebar_visible" not in st.session_state:
    st.session_state.sidebar_visible = True

# Add top navigation bar as backup
if "show_top_nav" not in st.session_state:
    st.session_state.show_top_nav = False

# Initialize current page if not exists (MUST be before top nav)
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Apply Momento design system
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Enhanced sidebar hiding + staff portal styling
st.markdown("""
<style>
/* Force hide sidebar completely */
section[data-testid="stSidebar"] {display: none !important;}
.css-1d391kg {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}
.css-17eq0hr {display: none !important;}

/* Remove sidebar margin */
.main {
    margin-left: 0 !important;
    padding-left: 2rem !important;
}

/* Staff portal clean styling */
</style>

<script>
// Additional JavaScript fallback for stubborn sidebar
setTimeout(() => {
    const elements = [
        'section[data-testid="stSidebar"]',
        '.css-1d391kg',
        '[data-testid="collapsedControl"]',
        '.css-17eq0hr'
    ];
    
    elements.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) {
            element.style.display = 'none';
            element.style.visibility = 'hidden';
        }
    });
    
    // Ensure main content uses full width
    const main = document.querySelector('.main');
    if (main) {
        main.style.marginLeft = '0';
        main.style.paddingLeft = '2rem';
        main.style.maxWidth = '100%';
    }
}, 100);
</script>
""", unsafe_allow_html=True)

# Simple centered navigation (after state updates)
with st.container():
    # Add navigation clock
    render_nav_clock()
    
    # Add some top spacing
    st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # Create navigation buttons
    pages = [
        ("Home", "Home"),
        ("Register", "Registration"), 
        ("QR Codes", "QR Management"),
        ("Attendance", "Attendance"),
        ("Reports", "Reports"),
        ("About", "About")
    ]
    
    # Center the buttons with spacer columns
    col1, col_nav, col2 = st.columns([1, 6, 1])
    
    with col_nav:
        button_cols = st.columns(len(pages), gap="small")
        
        for i, (display_name, page_key) in enumerate(pages):
            with button_cols[i]:
                # Check state after potential updates
                is_active = st.session_state.current_page == page_key
                button_type = "primary" if is_active else "secondary"
                
                if st.button(
                    display_name,
                    key=f"nav_{page_key.lower().replace(' ', '_')}",
                    type=button_type,
                    use_container_width=True
                ):
                    # Immediately update current page for instant visual feedback
                    st.session_state.current_page = page_key
                    st.rerun()

# Clean navigation button styling (from original app)
st.markdown("""
<style>
    /* Navigation container styling */
    .stButton > button {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(223, 230, 233, 0.6) !important;
        color: #636E72 !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        height: 44px !important;
        margin: 0 !important;
        box-shadow: 0 1px 3px rgba(45, 52, 54, 0.05) !important;
        backdrop-filter: blur(8px) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        min-width: fit-content !important;
    }
    
    .stButton > button:hover {
        background: rgba(245, 246, 250, 0.9) !important;
        border-color: rgba(45, 52, 54, 0.2) !important;
        color: #2D3436 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.1) !important;
    }
    
    /* Active button styling */
    .stButton > button[kind="primary"] {
        background: #2D3436 !important;
        border-color: #2D3436 !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(45, 52, 54, 0.15) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #636E72 !important;
        border-color: #636E72 !important;
        color: white !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 3px 12px rgba(45, 52, 54, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize face service
face_service = initialize_face_service()

# Initialize session states
SessionManager.init_all_states()

# ===========================
# NAVIGATION LOGIC (MOVED UP)
# ===========================

# Check if page was selected from horizontal navigation buttons FIRST
if "selected_page" in st.session_state:
    st.session_state.current_page = st.session_state["selected_page"]
    del st.session_state["selected_page"]

# ===========================
# PAGE ROUTING - Same as original app
# ===========================

# Use current page for routing
page = st.session_state.current_page

if page == "Home":
    render_home()

elif page == "Registration":
    render_student_registration(face_service)

elif page == "QR Management":
    render_qr_management()

elif page == "Attendance":
    render_ceremony_attendance(face_service)

elif page == "Reports":
    render_attendance_report()

elif page == "About":
    render_about()

# ===========================
# FOOTER - Same as original app
# ===========================

st.markdown("""
<div style="
    margin-top: 8rem; 
    padding: 2rem 0 2.5rem 0; 
    border-top: 1px solid rgba(116, 185, 255, 0.08); 
    text-align: center;
    background: transparent;
">
    <div style="color: #8E95A3; font-size: 0.75rem; line-height: 1.6;">
        <div style="font-weight: 600; margin-bottom: 0.25rem; color: #5A6B7D;">TARUMT Staff Portal</div>
        <div>Full System Access • 2025</div>
    </div>
</div>
""", unsafe_allow_html=True)