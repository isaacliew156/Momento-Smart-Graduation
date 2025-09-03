"""
Mobile UI helpers for the Student Portal
Provides responsive, touch-friendly components
"""
import streamlit as st
import os
from PIL import Image

class MobileUI:
    """Mobile-optimized UI components"""
    
    @staticmethod
    def get_mobile_css():
        """Returns CSS for mobile optimization"""
        return """
        <style>
        /* Mobile-first responsive design */
        @media screen and (max-width: 768px) {
            /* Make the main container full width on mobile */
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                max-width: 100% !important;
            }
            
            /* Larger touch targets for mobile */
            .stButton > button {
                min-height: 50px !important;
                font-size: 16px !important;
                padding: 12px 24px !important;
                border-radius: 12px !important;
                font-weight: 600 !important;
            }
            
            /* Mobile-optimized input fields */
            .stTextInput input {
                font-size: 16px !important;
                min-height: 50px !important;
                border-radius: 12px !important;
                padding: 12px !important;
            }
            
            /* Mobile file uploader */
            .stFileUploader {
                border: 2px dashed #ccc !important;
                border-radius: 12px !important;
                padding: 20px !important;
                text-align: center !important;
            }
            
            /* Mobile-friendly metrics */
            .metric-container {
                text-align: center !important;
                padding: 1rem !important;
                background: #f8f9fa !important;
                border-radius: 12px !important;
                margin: 0.5rem 0 !important;
            }
        }
        
        /* Touch-friendly buttons for all sizes */
        .mobile-button {
            width: 100% !important;
            min-height: 50px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            margin: 8px 0 !important;
            padding: 16px 20px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
        }
        
        .mobile-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }
        
        /* Card-like containers for mobile */
        .mobile-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #e1e5e9;
        }
        
        /* Mobile navigation */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #e1e5e9;
            padding: 0.5rem;
            z-index: 1000;
        }
        
        /* Mobile header */
        .mobile-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem 1rem;
            text-align: center;
            border-radius: 0 0 20px 20px;
            margin: -1rem -1rem 2rem -1rem;
        }
        
        /* Hide sidebar on mobile */
        @media screen and (max-width: 768px) {
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        }
        
        /* QR Code display optimization */
        .mobile-qr-container {
            text-align: center;
            padding: 2rem;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        .mobile-qr-container img {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
        }
        
        /* Status indicators */
        .status-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin: 0.25rem;
        }
        
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        .status-info {
            background: #cce5ff;
            color: #004085;
            border: 1px solid #b3d4fc;
        }
        </style>
        """
    
    @staticmethod
    def mobile_header(title, subtitle=None, icon="🎓"):
        """Create mobile-optimized header"""
        header_html = f"""
        <div class="mobile-header">
            <h1 style="margin: 0; font-size: 24px;">
                <span style="font-size: 28px;">{icon}</span> {title}
            </h1>
            {f'<p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 16px;">{subtitle}</p>' if subtitle else ''}
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    
    @staticmethod
    def mobile_button(text, key=None, button_type="primary", icon=None, disabled=False):
        """Create mobile-optimized button"""
        button_text = f"{icon} {text}" if icon else text
        
        return st.button(
            button_text,
            key=key,
            type=button_type,
            use_container_width=True,
            disabled=disabled
        )
    
    @staticmethod
    def mobile_card(content_func, title=None):
        """Create mobile-optimized card container"""
        if title:
            st.markdown(f"### {title}")
        
        with st.container():
            st.markdown('<div class="mobile-card">', unsafe_allow_html=True)
            content_func()
            st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def mobile_metric(label, value, delta=None, icon=None):
        """Mobile-optimized metric display"""
        metric_html = f"""
        <div class="metric-container">
            {f'<div style="font-size: 24px; margin-bottom: 0.5rem;">{icon}</div>' if icon else ''}
            <div style="font-size: 14px; color: #666; margin-bottom: 0.25rem;">{label}</div>
            <div style="font-size: 24px; font-weight: 600; color: #333;">{value}</div>
            {f'<div style="font-size: 12px; color: #666; margin-top: 0.25rem;">{delta}</div>' if delta else ''}
        </div>
        """
        st.markdown(metric_html, unsafe_allow_html=True)
    
    @staticmethod
    def mobile_status_badge(text, status_type="info"):
        """Create status badge"""
        badge_html = f"""
        <span class="status-badge status-{status_type}">
            {text}
        </span>
        """
        st.markdown(badge_html, unsafe_allow_html=True)
    
    @staticmethod
    def mobile_input(label, input_type="text", key=None, placeholder=None, help_text=None):
        """Mobile-optimized input field"""
        if input_type == "text":
            return st.text_input(
                label,
                key=key,
                placeholder=placeholder,
                help=help_text
            )
        elif input_type == "password":
            return st.text_input(
                label,
                type="password",
                key=key,
                placeholder=placeholder,
                help=help_text
            )
    
    @staticmethod
    def mobile_image_display(image_path, caption=None, width=None):
        """Mobile-optimized image display"""
        if os.path.exists(image_path):
            image = Image.open(image_path)
            
            # Auto-resize for mobile
            if width is None:
                # Use responsive width
                st.image(image, caption=caption, use_container_width=True)
            else:
                st.image(image, caption=caption, width=width)
        else:
            st.warning(f"📷 Image not found: {caption or 'Image'}")
    
    @staticmethod
    def mobile_file_uploader(label, accepted_types=None, key=None, help_text=None):
        """Mobile-optimized file uploader"""
        return st.file_uploader(
            label,
            type=accepted_types or ['jpg', 'jpeg', 'png'],
            key=key,
            help=help_text
        )
    
    @staticmethod
    def mobile_camera_input(label, key=None, help_text=None):
        """Mobile-optimized camera input"""
        return st.camera_input(
            label,
            key=key,
            help=help_text
        )
    
    @staticmethod
    def mobile_progress_bar(progress, text=None):
        """Mobile-optimized progress display"""
        if text:
            st.write(text)
        st.progress(progress)
    
    @staticmethod
    def mobile_alert(message, alert_type="info", icon=None):
        """Mobile-optimized alert"""
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        display_icon = icon or icons.get(alert_type, "ℹ️")
        
        if alert_type == "success":
            st.success(f"{display_icon} {message}")
        elif alert_type == "error":
            st.error(f"{display_icon} {message}")
        elif alert_type == "warning":
            st.warning(f"{display_icon} {message}")
        else:
            st.info(f"{display_icon} {message}")
    
    @staticmethod
    def mobile_qr_display(qr_path, student_name=None, student_id=None):
        """Mobile-optimized QR code display"""
        if os.path.exists(qr_path):
            st.markdown('<div class="mobile-qr-container">', unsafe_allow_html=True)
            
            if student_name:
                st.markdown(f"**{student_name}**")
            if student_id:
                st.markdown(f"ID: {student_id}")
            
            # Display QR code
            qr_image = Image.open(qr_path)
            st.image(qr_image, use_container_width=True)
            
            # Download button
            with open(qr_path, "rb") as f:
                qr_bytes = f.read()
            
            st.download_button(
                "📱 Download QR Code",
                data=qr_bytes,
                file_name=f"{student_id}_qr.png" if student_id else "qr_code.png",
                mime="image/png",
                use_container_width=True
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("❌ QR code not found")
    
    @staticmethod
    def apply_mobile_css():
        """Apply mobile CSS to the page"""
        st.markdown(MobileUI.get_mobile_css(), unsafe_allow_html=True)

# Helper function for easy import
def init_mobile_ui():
    """Initialize mobile UI for a page"""
    MobileUI.apply_mobile_css()