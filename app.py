"""
Graduation Attendance System - Dual Portal Application
Main multipage launcher for Staff and Student portals
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import authentication
from utils.auth import AuthManager
from utils.config import setup_directories

# Page configuration - MUST be first
st.set_page_config(
    page_title="TARUMT Graduation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed for cleaner look
)

# Setup directories
setup_directories()

# Initialize authentication
AuthManager.init_session_states()

# Apply Momento Design System CSS
from utils.config import CUSTOM_CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Additional CSS for portal selection
st.markdown("""
<style>
/* Hide Streamlit elements completely */
.stDeployButton {display: none;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
section[data-testid="stSidebar"] {display: none !important;}

/* Hide multipage navigation completely */
.stPageLink, .stPageLink-nav, [data-testid="stPageLink-nav"] {display: none !important;}
.css-1vbkxwb, .css-1rs6os, .css-17lntkn {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
.css-1d391kg {display: none !important;}

/* Portal selection specific styles */
.portal-hero {
    text-align: center; 
    padding: 4rem 0 3rem 0;
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative; /* Enable positioning for decorative elements */
    overflow: hidden; /* Contain floating elements */
}

.portal-hero h1 {
    font-size: 5rem; /* Balanced size - not too big, not too small */
    font-weight: 300; 
    margin-bottom: 0.5rem; 
    background: linear-gradient(135deg, #2D3436 0%, #636E72 50%, #4A5557 100%); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    background-clip: text; 
    letter-spacing: -0.02em; 
    font-family: -apple-system, 'SF Pro Display', sans-serif; 
    text-align: center; 
    line-height: 1;
}

.portal-divider {
    width: 60px; 
    height: 2px; 
    background: linear-gradient(90deg, #74B9FF, #0984E3); 
    margin: 1.5rem auto; 
    border-radius: 2px;
}

/* High specificity selector to override Streamlit's default styles */
.stMarkdown .portal-subtitle,
.portal-subtitle {
    font-size: 1.4rem !important; /* Reduced from 1.6rem for better proportion */
    color: #2D3436 !important; /* Changed to darker color for better contrast */
    margin-bottom: 0.5rem !important; /* Added bottom margin for better spacing */
    font-weight: 600 !important; /* Increased from 500 for more prominence */
    letter-spacing: 0.3px !important; /* Reduced from 0.5px for better readability */
    text-transform: none !important; /* Removed uppercase for friendlier appearance */
    text-align: center !important;
    /* Add gradient text effect for visual enhancement */
    background: linear-gradient(135deg, #2D3436 0%, #636E72 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    text-shadow: 0 1px 2px rgba(45, 52, 54, 0.1) !important; /* Subtle shadow for depth */
}

/* High specificity selector to override Streamlit's default styles */
.stMarkdown .portal-description,
.portal-description {
    font-size: 1.1rem !important; /* Reduced from 1.3rem for better proportion */
    color: #636E72 !important; /* Changed from #A4A6A8 to darker color for better contrast */
    margin-top: 0.5rem !important; /* Reduced from 0.75rem for tighter spacing */
    font-weight: 400 !important; /* Increased from 300 for better legibility */
    text-align: center !important;
    line-height: 1.4 !important; /* Added line height for better readability */
    opacity: 0.9 !important; /* Slight transparency for visual hierarchy */
}

/* Portal button styling - Special portal card styles */
/* These will be applied via JavaScript classes */
.portal-button-wrapper {
    height: 350px !important;
    min-height: 350px !important;
    padding: 4rem 3rem !important;
    margin: 3rem 0 !important;
    background: #FFFFFF !important;
    border: 2px solid #E8EEF1 !important;
    border-radius: 16px !important;
    box-shadow: 0 12px 40px rgba(45, 52, 54, 0.15) !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    color: #2D3436 !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
    white-space: pre-line !important;
}

.portal-button-wrapper:hover {
    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%) !important;
    box-shadow: 0 20px 60px rgba(45, 52, 54, 0.25) !important;
    transform: translateY(-8px) scale(1.02) !important;
    border-color: #74B9FF !important;
    color: #2D3436 !important;
}

/* Portal button styles - using class selectors */
.portal-button-staff,
.portal-button-student {
    height: 240px !important;
    min-height: 240px !important;
    padding: 1.8rem 1.6rem !important;
    margin: 1rem 0 !important;
    background: linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%) !important;
    border: 1px solid rgba(116, 185, 255, 0.15) !important;
    border-radius: 20px !important;
    box-shadow: 
        0 4px 20px rgba(45, 52, 54, 0.08),
        0 1px 3px rgba(45, 52, 54, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
    font-size: 1.1rem !important;
    font-weight: 400 !important;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif !important;
    line-height: 1.4 !important;
    color: #2D3436 !important;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
    position: relative !important;
    overflow: hidden !important;
    white-space: pre-line !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
}

/* Style control for all text inside portal buttons - targeting p tags */
.portal-button-staff p,
.portal-button-student p {
    font-size: 1.25rem !important;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif !important;
    font-weight: 600 !important;
    color: #2D3436 !important;
    margin: 0 !important;
    line-height: 1.3 !important;
}

/* Removed broad emotion-cache override, let JavaScript handle intelligently */

/* Enhance overall card refinement */
.portal-button-staff,
.portal-button-student {
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
}

/* Universal portal button hover effects - Works on all buttons */
button:has([data-testid="stMarkdownContainer"]):hover {
    background: linear-gradient(135deg, #E8F4FD 0%, #D1E7DD 100%) !important;
    box-shadow: 0 16px 48px rgba(45, 52, 54, 0.2) !important;
    transform: translateY(-6px) scale(1.01) !important;
    border-color: #74B9FF !important;
    color: #2D3436 !important;
}


/* Ensure correct text color on hover */
.portal-button-staff:hover *,
.portal-button-student:hover * {
    color: #2D3436 !important;
}

/* Animation transition effects */
.portal-button-staff,
.portal-button-student {
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
}

.portal-icon {
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

.portal-title {
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 1rem 0 0.5rem 0;
}

/* Removed duplicate portal-subtitle definition that was overriding our main styles above */

@media (max-width: 768px) {
    .portal-hero h1 {
        font-size: 3.2rem; /* Proportionally adjusted for mobile - balanced sizing */
    }
    
    /* Mobile optimization for subtitle and description text */
    .portal-subtitle {
        font-size: 1.4rem; /* Slightly smaller for mobile screens */
        margin-bottom: 0.3rem; /* Tighter spacing on mobile */
        letter-spacing: 0.2px; /* Adjusted letter spacing for mobile */
    }
    
    .portal-description {
        font-size: 1.1rem; /* Slightly smaller for mobile screens */
        margin-top: 0.3rem; /* Tighter spacing on mobile */
        line-height: 1.5; /* Increased line height for better mobile readability */
        padding: 0 1rem; /* Add horizontal padding to prevent edge touching */
    }
    
    .portal-hero {
        padding: 3rem 0 2rem 0; /* Reduced vertical padding for mobile */
    }
    
    .portal-button-staff-mobile,
    .portal-button-student-mobile {
        height: 250px !important;
        padding: 3rem 2rem !important;
    }
}

/* Floating decorative elements for visual enhancement */
/* Removed decorative circular background elements for cleaner appearance */

/* Floating animations */
@keyframes float-right {
    0%, 100% { 
        transform: translateY(0px) translateX(0px) rotate(0deg);
        opacity: 0.6;
    }
    33% { 
        transform: translateY(-15px) translateX(-10px) rotate(2deg);
        opacity: 0.8;
    }
    66% { 
        transform: translateY(-5px) translateX(5px) rotate(-1deg);
        opacity: 0.7;
    }
}

@keyframes float-left {
    0%, 100% { 
        transform: translateY(0px) translateX(0px) rotate(0deg);
        opacity: 0.5;
    }
    50% { 
        transform: translateY(-20px) translateX(10px) rotate(3deg);
        opacity: 0.7;
    }
}

/* Fade-in animation for the hero section */
@keyframes fadeInUp {
    from { 
        opacity: 0; 
        transform: translateY(40px);
    }
    to { 
        opacity: 1; 
        transform: translateY(0);
    }
}

/* Apply fade-in animation to hero section */
.portal-hero {
    animation: fadeInUp 1s ease-out;
}

/* Staggered animation for child elements */
.portal-hero h1 {
    animation: fadeInUp 1s ease-out 0.2s both;
}

.portal-hero .portal-divider {
    animation: fadeInUp 1s ease-out 0.4s both;
}

.portal-hero .portal-subtitle {
    animation: fadeInUp 1s ease-out 0.6s both;
}

.portal-hero .portal-description {
    animation: fadeInUp 1s ease-out 0.8s both;
}

/* Welcome greeting styling - Modern redesign */
.welcome-greeting {
    margin-top: 1.8rem;
    padding: 0.9rem 1.8rem;
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.08), rgba(116, 185, 255, 0.12), rgba(162, 155, 254, 0.08));
    border: 1.5px solid transparent;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.7rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    animation: fadeInUp 1s ease-out 1s both;
    box-shadow: 
        0 4px 20px rgba(255, 107, 107, 0.1),
        0 8px 25px rgba(45, 52, 54, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    background-clip: padding-box;
}

/* Animated gradient border effect */
.welcome-greeting::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 14px;
    padding: 1.5px;
    background: linear-gradient(135deg, #ff6b6b, #74b9ff, #a29bfe);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.4s ease;
}

.welcome-greeting:hover::before {
    opacity: 1;
}

.welcome-greeting:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 
        0 6px 25px rgba(255, 107, 107, 0.15),
        0 12px 35px rgba(45, 52, 54, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.greeting-icon {
    font-size: 1.3rem;
    /* Removed gradient effect to show emoji properly */
    animation: gentle-pulse 3s ease-in-out infinite;
    display: inline-block;
    filter: drop-shadow(0 2px 4px rgba(45, 52, 54, 0.1));
}

.greeting-text {
    font-size: 1rem !important;
    font-weight: 600 !important;
    background: linear-gradient(135deg, #2D3436, #636E72) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif !important;
    margin: 0 !important;
    text-align: center !important;
    letter-spacing: 0.2px !important;
}

/* Refined pulse animation */
@keyframes gentle-pulse {
    0%, 100% { 
        opacity: 1; 
        transform: scale(1);
    }
    50% { 
        opacity: 0.8; 
        transform: scale(1.08);
    }
}

@keyframes pulse {
    0%, 100% { 
        opacity: 1; 
        transform: scale(1); 
    }
    50% { 
        opacity: 0.8; 
        transform: scale(1.05); 
    }
}

/* Mobile greeting adjustments */
@media (max-width: 768px) {
    .welcome-greeting {
        margin-top: 1.4rem;
        padding: 0.8rem 1.4rem;
        gap: 0.6rem;
        border-radius: 12px;
    }
    
    .greeting-icon {
        font-size: 1.1rem;
    }
    
    .greeting-text {
        font-size: 0.9rem !important;
        letter-spacing: 0.1px !important;
    }
}

/* Footer styling */
.portal-footer {
    margin-top: 10rem;
    padding: 2.5rem 0 3rem 0;
    text-align: center;
    position: relative;
}

.portal-footer::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 1px;
    background: linear-gradient(90deg, transparent, #E8EEF1, transparent);
}

.footer-content {
    animation: fadeInUp 1s ease-out 1s both;
}

.footer-title {
    font-size: 0.95rem !important;
    color: #636E72 !important;
    font-weight: 500 !important;
    margin-bottom: 0.25rem !important;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif !important;
}

.footer-subtitle {
    font-size: 0.85rem !important;
    color: #A4A6A8 !important;
    font-weight: 300 !important;
    margin: 0 !important;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif !important;
    opacity: 0.8 !important;
}

/* Mobile footer adjustments */
@media (max-width: 768px) {
    .portal-footer {
        margin-top: 4.5rem;
        padding: 1.5rem 0 2rem 0;
    }
    
    .footer-title {
        font-size: 0.9rem !important;
    }
    
    .footer-subtitle {
        font-size: 0.8rem !important;
    }
}

</style>

<script>
// Force apply portal button styling with JavaScript - Fixed version
function applyPortalButtonStyling() {
    console.log('🔍 Searching for portal buttons...');
    
    // Find all buttons on the page
    const allButtons = document.querySelectorAll('button');
    console.log(`Total buttons found: ${allButtons.length}`);
    
    allButtons.forEach((btn, index) => {
        // Check button text content
        const text = btn.textContent || btn.innerText || '';
        console.log(`Button ${index}: "${text.substring(0, 50)}..."`);
        
        // Check if this is a portal button
        const isStaffPortal = text.includes('Staff Portal');
        const isStudentPortal = text.includes('Student Portal');
        
        if (isStaffPortal || isStudentPortal) {
            console.log(`✅ Found portal button: "${text.substring(0, 30)}..."`);
            
            // Add appropriate class
            if (isStaffPortal) {
                btn.classList.add('portal-button-staff');
            } else {
                btn.classList.add('portal-button-student');
            }
            
            console.log(`🎨 Styling portal button ${index + 1}`);
            
            // Use setProperty to force override each property - refined compact version
            btn.style.setProperty('height', '240px', 'important');
            btn.style.setProperty('min-height', '240px', 'important');
            btn.style.setProperty('padding', '1.8rem 1.6rem', 'important');
            btn.style.setProperty('margin', '1rem 0', 'important');
            btn.style.setProperty('background', 'linear-gradient(135deg, #FFFFFF 0%, #FAFBFC 100%)', 'important');
            btn.style.setProperty('border', '1px solid rgba(116, 185, 255, 0.15)', 'important');
            btn.style.setProperty('border-radius', '20px', 'important');
            btn.style.setProperty('box-shadow', '0 4px 20px rgba(45, 52, 54, 0.08), 0 1px 3px rgba(45, 52, 54, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.9)', 'important');
            btn.style.setProperty('font-size', '1.1rem', 'important');
            btn.style.setProperty('font-weight', '400', 'important');
            btn.style.setProperty('font-family', '-apple-system, "SF Pro Display", "Helvetica Neue", sans-serif', 'important');
            btn.style.setProperty('line-height', '1.4', 'important');
            btn.style.setProperty('color', '#2D3436', 'important');
            btn.style.setProperty('transition', 'all 0.4s cubic-bezier(0.23, 1, 0.32, 1)', 'important');
            btn.style.setProperty('white-space', 'pre-line', 'important');
            btn.style.setProperty('width', '100%', 'important');
            btn.style.setProperty('cursor', 'pointer', 'important');
            btn.style.setProperty('display', 'flex', 'important');
            btn.style.setProperty('flex-direction', 'column', 'important');
            btn.style.setProperty('justify-content', 'center', 'important');
            btn.style.setProperty('align-items', 'center', 'important');
            btn.style.setProperty('text-align', 'center', 'important');
            btn.style.setProperty('backdrop-filter', 'blur(10px)', 'important');
            btn.style.setProperty('-webkit-backdrop-filter', 'blur(10px)', 'important');
            
            // Intelligently style internal text - distinguish titles and subtitles
            // Try both direct p tags and p tags inside markdown container
            let pTags = btn.querySelectorAll('p');
            if (pTags.length === 0) {
                // If no direct p tags, look inside markdown container
                const markdownContainer = btn.querySelector('[data-testid="stMarkdownContainer"]');
                if (markdownContainer) {
                    pTags = markdownContainer.querySelectorAll('p');
                }
            }
            console.log(`Found ${pTags.length} p tags in button ${index + 1}`);
            pTags.forEach((p, pIndex) => {
                const text = p.textContent.trim();
                console.log(`P tag ${pIndex}: "${text}"`);
                
                // If it's emoji paragraph, make it larger
                if (text.includes('👨‍💼') || text.includes('📱')) {
                    p.style.setProperty('font-size', '2.5rem', 'important');
                    p.style.setProperty('margin', '0 0 1rem 0', 'important');
                    p.style.setProperty('line-height', '1', 'important');
                }
                // If it's main title (exactly "Staff Portal" or "Student Portal")
                else if (text === 'Staff Portal' || text === 'Student Portal') {
                    console.log(`✅ Found main title: "${text}" - applying BOLD style`);
                    p.style.setProperty('font-size', '1.4rem', 'important');
                    p.style.setProperty('font-weight', '600', 'important');
                    p.style.setProperty('font-family', '-apple-system, "SF Pro Display", "Helvetica Neue", sans-serif', 'important');
                    p.style.setProperty('margin', '0 0 0.5rem 0', 'important');
                    p.style.setProperty('line-height', '1.2', 'important');
                    p.style.setProperty('color', '#2D3436', 'important');
                }
                // If it's subtitle (Complete System Access / Self-Service Interface)
                else if (text === 'Complete System Access' || text === 'Self-Service Interface') {
                    console.log(`✅ Found subtitle: "${text}" - applying normal weight`);
                    p.style.setProperty('font-size', '1rem', 'important');
                    p.style.setProperty('font-weight', '400', 'important');
                    p.style.setProperty('font-family', '-apple-system, "SF Pro Display", "Helvetica Neue", sans-serif', 'important');
                    p.style.setProperty('margin', '0', 'important');
                    p.style.setProperty('line-height', '1.4', 'important');
                    p.style.setProperty('color', '#636E72', 'important');
                }
                // Empty line handling
                else if (text === '') {
                    p.style.setProperty('margin', '0.5rem 0', 'important');
                    p.style.setProperty('line-height', '0.5', 'important');
                }
                // Other text
                else {
                    console.log(`⚠️ Unmatched text: "${text}" - applying default style`);
                    p.style.setProperty('font-size', '1.1rem', 'important');
                    p.style.setProperty('font-weight', '400', 'important');
                    p.style.setProperty('font-family', '-apple-system, "SF Pro Display", "Helvetica Neue", sans-serif', 'important');
                    p.style.setProperty('margin', '0', 'important');
                    p.style.setProperty('line-height', '1.3', 'important');
                    p.style.setProperty('color', '#2D3436', 'important');
                }
            });
            
            console.log(`✅ Styled portal button successfully`);
        }
    });
}

// Execute when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyPortalButtonStyling);
} else {
    // DOM is already loaded
    applyPortalButtonStyling();
}

// Also execute with delays to catch Streamlit updates
setTimeout(applyPortalButtonStyling, 500);
setTimeout(applyPortalButtonStyling, 1000);
setTimeout(applyPortalButtonStyling, 1500);
setTimeout(applyPortalButtonStyling, 2000);

// Re-apply on any Streamlit updates
const observer = new MutationObserver(function() {
    setTimeout(applyPortalButtonStyling, 100);
});

observer.observe(document.body, { childList: true, subtree: true });

// Debug: Log current time for troubleshooting (Python backend now handles greeting)
console.log('🕐 Current time:', new Date().toLocaleTimeString());
</script>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Get current time-based greeting (using Python backend - reliable)
    from datetime import datetime
    now = datetime.now()
    hour = now.hour
    
    if 6 <= hour < 12:
        greeting_icon = "🌅"
        greeting_text = "Good morning! Ready for a productive day?"
    elif 12 <= hour < 18:
        greeting_icon = "☀️"
        greeting_text = "Good afternoon! Let's get things done!"
    else:
        greeting_icon = "🌙" 
        greeting_text = "Good evening! Working late tonight?"
    
    # Hero section using Momento design
    st.markdown(f"""
    <div class="portal-hero">
        <h1>&nbsp;&nbsp;Momento</h1>
        <div class="portal-divider"></div>
        <p class="portal-subtitle">Dual Portal Access</p>
        <p class="portal-description">Choose your portal to access the graduation system</p>
        <div class="welcome-greeting">
            <span class="greeting-icon" id="time-icon">{greeting_icon}</span>
            <span class="greeting-text" id="time-greeting">{greeting_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Portal selection - Big beautiful buttons
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        if st.button("👨‍💼\n\n**Staff Portal**\n\nComplete System Access", key="staff_portal", use_container_width=True):
            st.switch_page("pages/2_👨‍💼_Staff_Portal.py")
    
    with col2:
        if st.button("📱\n\n**Student Portal**\n\nSelf-Service Interface", key="student_portal", use_container_width=True):
            st.switch_page("pages/3_📱_Student_Portal.py")
    
    # Footer section
    st.markdown("""
    <div class="portal-footer">
        <div class="footer-content">
            <p class="footer-title">🎓 TARUMT Graduation System</p>
            <p class="footer-subtitle">Education Project © 2025</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()