"""
Configuration and constants for the Graduation Attendance System
"""
import os

# ===========================
# DIRECTORY CONFIGURATION
# ===========================

UPLOAD_FOLDER = 'data/uploads'
QR_FOLDER = 'data/static'
CAPTURES_FOLDER = 'data/captures'

# Ensure directories exist
def setup_directories():
    """Create necessary directories if they don't exist"""
    for folder in [UPLOAD_FOLDER, QR_FOLDER, CAPTURES_FOLDER]:
        os.makedirs(folder, exist_ok=True)

# ===========================
# ENVIRONMENT CONFIGURATION
# ===========================

ENVIRONMENT = os.getenv('GRAD_ENV', 'normal')  # normal, low_light, outdoor

VALIDATION_CONFIGS = {
    'normal': {
        'blur_threshold': 45,
        'min_face_size': 80,
        'min_brightness': 35,
        'max_brightness': 230,
        'description': 'Standard indoor conditions'
    },
    'low_light': {
        'blur_threshold': 30,
        'min_face_size': 70,
        'min_brightness': 25,
        'max_brightness': 240,
        'description': 'Dimly lit indoor environments'
    },
    'outdoor': {
        'blur_threshold': 55,
        'min_face_size': 85,
        'min_brightness': 40,
        'max_brightness': 250,
        'description': 'Bright outdoor conditions'
    }
}

# Get current configuration based on environment
def get_current_config():
    """Get validation configuration for current environment"""
    return VALIDATION_CONFIGS.get(ENVIRONMENT, VALIDATION_CONFIGS['normal'])

# ===========================
# UI CONFIGURATION
# ===========================

CUSTOM_CSS = """
    <style>
    /* Momento Modern Design System */
    :root {
        --primary-color: #2D3436;
        --secondary-color: #636E72;
        --accent-color: #74B9FF;
        --success-color: #00B894;
        --warning-color: #E17055;
        --error-color: #D63031;
        --background-color: #F5F6FA;
        --surface-color: #FFFFFF;
        --text-primary: #2D3436;
        --text-secondary: #636E72;
        --text-muted: #A4A6A8;
        --border-color: #DFE6E9;
        --border-light: #E8EEF1;
        --shadow-light: 0 2px 8px rgba(45, 52, 54, 0.08);
        --shadow-medium: 0 8px 24px rgba(45, 52, 54, 0.12);
        --shadow-hover: 0 4px 16px rgba(45, 52, 54, 0.15);
        --radius-small: 8px;
        --radius-medium: 16px;
        --radius-large: 24px;
        --transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        --gradient-primary: linear-gradient(135deg, #2D3436 0%, #636E72 100%);
        --gradient-accent: linear-gradient(135deg, #74B9FF 0%, #0984E3 100%);
        --gradient-subtle: linear-gradient(135deg, #F5F6FA 0%, #FFFFFF 100%);
    }

    /* Global Styles */
    .stApp {
        background: 
            linear-gradient(180deg, #F8F9FA 0%, #F6F8FB 50%, #F4F6F8 100%);
        background-attachment: fixed;
        position: relative;
        font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif;
        min-height: 100vh;
    }

    .main > div {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    /* Typography */
    h1 {
        color: var(--text-primary);
        font-weight: 700;
        font-size: 2.5rem;
        line-height: 1.2;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }

    h2 {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.75rem;
        line-height: 1.3;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }

    h3 {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 1.25rem;
        line-height: 1.4;
        margin-bottom: 0.75rem;
    }

    .stMarkdown p {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    /* Card Components */
    .feature-card {
        background: var(--surface-color);
        border-radius: var(--radius-medium);
        box-shadow: var(--shadow-light);
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-light);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .feature-card:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-4px);
        border-color: var(--border-color);
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: var(--transition);
    }

    .feature-card:hover::before {
        opacity: 1;
    }

    /* Buttons */
    .stButton > button {
        background: #F8F9FA;
        color: var(--text-primary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-small);
        padding: 0.875rem 2rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: var(--transition);
        box-shadow: var(--shadow-light);
        letter-spacing: 0.025em;
        min-height: 44px;
    }

    .stButton > button:hover {
        background: var(--accent-color);
        color: white;
        border-color: var(--accent-color);
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-light);
    }

    /* Secondary Button Style */
    .stButton[data-testid="secondary"] > button {
        background: transparent;
        color: var(--primary-color);
        border: 1.5px solid var(--border-color);
    }

    .stButton[data-testid="secondary"] > button:hover {
        background: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
    }

    /* Enhanced Divider Styles */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E8EEF1, transparent);
        margin: 2rem 0;
    }
    
    /* Custom elegant divider */
    .elegant-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #74B9FF, transparent);
        margin: 2.5rem 0;
        border-radius: 1px;
    }
    
    /* Section spacing */
    .section-spacing {
        margin: 3rem 0 1.5rem 0;
    }

    /* Hide Sidebar Completely - Multiple selectors for compatibility */
    .css-1d391kg,
    .css-1y4p8pa,
    [data-testid="stSidebar"],
    .stSidebar {
        display: none !important;
    }
    
    /* Hide sidebar toggle button */
    [data-testid="collapsedControl"],
    .css-1rs6os {
        display: none !important;
    }
    
    /* Adjust main content when sidebar is hidden */
    .main .block-container {
        padding-left: 2rem;
        max-width: none;
    }
    
    /* Remove sidebar space completely */
    .css-1y4p8pa {
        width: 0 !important;
    }

    .css-17eq0hr {
        color: var(--text-primary);
    }

    /* Sidebar Navigation Enhancements */
    .sidebar-nav-header {
        background: var(--gradient-subtle);
        border-radius: var(--radius-medium);
        margin-bottom: 1.5rem;
        padding: 1rem;
        border: 1px solid var(--border-light);
    }

    /* Fixed Navigation Toggle Button */
    .nav-toggle {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 1001;
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-small);
        padding: 0.75rem;
        cursor: pointer;
        box-shadow: var(--shadow-medium);
        transition: var(--transition);
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        backdrop-filter: blur(10px);
    }

    .nav-toggle:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
        background: var(--primary-color);
        color: white;
    }

    /* Ensure main content doesn't overlap with toggle */
    .main .block-container {
        padding-left: 4rem;
    }

    /* Hide toggle when sidebar is visible */
    .css-1d391kg:not([data-testid="stSidebarNav"]) ~ .main .nav-toggle {
        display: none;
    }

    /* Select Box */
    .stSelectbox > div > div {
        background-color: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-small);
        transition: var(--transition);
    }

    .stSelectbox > div > div:hover {
        box-shadow: var(--shadow-light);
    }

    /* Tabs - Fixed Red Underline Issue */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        border-bottom: 1px solid var(--border-color);
        gap: 0;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        color: var(--text-secondary);
        font-weight: 500;
        border-radius: var(--radius-small) var(--radius-small) 0 0;
        transition: var(--transition);
        background: transparent;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        margin-bottom: -1px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(26, 26, 26, 0.05);
        color: var(--text-primary);
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--surface-color);
        color: var(--text-primary);
        border-bottom: 2px solid var(--primary-color) !important;
        font-weight: 600;
        box-shadow: 0 -2px 8px rgba(26, 26, 26, 0.05);
    }

    /* Remove any red underlines from Streamlit default */
    .stTabs [role="tab"]::after,
    .stTabs [role="tab"]::before {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Info/Success/Warning boxes - Updated for Gray Theme */
    .stInfo {
        background-color: rgba(58, 58, 58, 0.08);
        border: 1px solid rgba(58, 58, 58, 0.15);
        border-radius: var(--radius-medium);
        padding: 1.5rem;
        color: var(--text-primary);
        border-left: 4px solid var(--secondary-color);
    }

    .stSuccess {
        background-color: rgba(39, 174, 96, 0.08);
        border: 1px solid rgba(39, 174, 96, 0.15);
        border-radius: var(--radius-medium);
        padding: 1.5rem;
        color: var(--text-primary);
        border-left: 4px solid var(--success-color);
    }

    .stWarning {
        background-color: rgba(243, 156, 18, 0.08);
        border: 1px solid rgba(243, 156, 18, 0.15);
        border-radius: var(--radius-medium);
        padding: 1.5rem;
        color: var(--text-primary);
        border-left: 4px solid var(--warning-color);
    }

    .stError {
        background-color: rgba(231, 76, 60, 0.08);
        border: 1px solid rgba(231, 76, 60, 0.15);
        border-radius: var(--radius-medium);
        padding: 1.5rem;
        color: var(--text-primary);
        border-left: 4px solid var(--error-color);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom spacing and layout improvements */
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Columns spacing */
    .row-widget.stHorizontal > div {
        padding-right: 1rem;
    }

    .row-widget.stHorizontal > div:last-child {
        padding-right: 0;
    }

    /* Metrics styling */
    .stMetric {
        background: var(--surface-color);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-medium);
        padding: 1.5rem;
        box-shadow: var(--shadow-light);
        transition: var(--transition);
    }

    .stMetric:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }

    .stMetric [data-testid="metric-container"] {
        border: none;
        padding: 0;
    }

    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1.5px solid var(--border-color);
        border-radius: var(--radius-small);
        background-color: var(--surface-color);
        color: var(--text-primary);
        transition: var(--transition);
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--secondary-color);
        box-shadow: 0 0 0 3px rgba(58, 58, 58, 0.1);
    }

    /* Enhanced hover and focus states */
    .stSelectbox:hover,
    .stButton:hover,
    .feature-card:hover {
        cursor: pointer;
    }

    /* Responsive improvements */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .feature-card {
            min-height: 180px;
            padding: 1.5rem;
        }
        
        .stButton > button {
            width: 100%;
        }
    }
    </style>
"""

# ===========================
# PATH HELPERS
# ===========================

def normalize_path(path):
    """
    Normalize file paths to use forward slashes consistently.
    This fixes issues with mixed slashes on Windows/WSL systems.
    """
    if path:
        # Replace backslashes with forward slashes
        return path.replace('\\', '/')
    return path

# ===========================
# PAGE CONFIGURATION
# ===========================

PAGE_TITLE = "Graduation Attendance System"
PAGE_ICON = "🎓"
LAYOUT = "wide"

# Navigation pages
PAGES = [
    "Home",
    "Registration", 
    "QR Management",
    "Attendance",
    "Reports",
    "About"
]