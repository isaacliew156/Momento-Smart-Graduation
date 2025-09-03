"""
Student Registration page for the Graduation Attendance System
Auto-migrated from app.py
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
# from core.interactive_crop import *  # Removed - streamlit-cropper dependency removed
from core.error_handler import *

# Import utils
from utils.config import *
from utils.session_manager import SessionManager, init_session_state, clear_capture
from utils.card_processing import *
from utils.ui_helpers import *
from utils.loading_animations import show_ocr_processing_animation, create_simple_spinner
from utils.camera_utils import create_camera_input_with_preference


def render_student_card(student, download_key_suffix=""):
    """
    Render a single student card using pure Streamlit native components
    Args:
        student: Student data dictionary
    download_key_suffix: Unique suffix for download button key
    """
    try:
        # Extract student data safely
        student_id = student.get('student_id') or student.get('id', 'Unknown')
        student_name = student.get('name', 'Unknown')
        image_path = normalize_path(student.get('image_path', ''))
        has_face = student.get('encoding') is not None
        registration_method = student.get('registration_method', 'Unknown')
        
        # Use pure Streamlit container with border styling
        with st.container(border=True):
            # Student avatar using emoji/initial - centered
            student_initial = student_name[0].upper() if student_name and len(student_name) > 0 else '?'
            
            # Center the content
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # Simple text-based avatar (no HTML needed)
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="
                        display: inline-block;
                        width: 60px;
                        height: 60px;
                        background: #667eea;
                        color: white;
                        border-radius: 50%;
                        line-height: 60px;
                        font-size: 24px;
                        font-weight: bold;
                    ">{student_initial}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Student name (centered)
            st.markdown(f"<h4 style='text-align: center; margin: 0.5rem 0;'>{student_name}</h4>", unsafe_allow_html=True)
            
            # Student ID (centered)
            st.markdown(f"<p style='text-align: center; color: #666; margin: 0.5rem 0;'>🆔 {student_id}</p>", unsafe_allow_html=True)
            
            # Face recognition status using native components
            if has_face:
                st.success("👤 Face ID Available", icon="✅")
            else:
                st.warning("❌ No Face Recognition", icon="⚠️")
            
            # Small spacing
            st.write("")
            
            # Download QR button
            qr_path = os.path.join(QR_FOLDER, f"{student_id}_qr.png")
            if os.path.exists(qr_path):
                try:
                    with open(qr_path, "rb") as f:
                        qr_bytes = f.read()
                    st.download_button(
                        "📱 Download QR",
                        data=qr_bytes,
                        file_name=f"{student_id}_qr.png",
                        mime="image/png",
                        key=f"download_{download_key_suffix}_{student_id}",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"❌ QR Error: {str(e)}")
            else:
                st.button("⚠️ No QR Code", disabled=True, use_container_width=True)
            
    except Exception as e:
        # Pure Streamlit fallback - no HTML at all
        st.error(f"⚠️ Error displaying student card")
        
        with st.expander("📋 Student Details"):
            st.write("**Student Information:**")
            st.write(f"**ID:** {student.get('student_id', 'Unknown')}")
            st.write(f"**Name:** {student.get('name', 'Unknown')}")
            st.write(f"**Face Recognition:** {'✅ Available' if student.get('encoding') else '❌ Not Available'}")
            
            # QR download fallback
            qr_path = os.path.join(QR_FOLDER, f"{student.get('student_id', 'unknown')}_qr.png")
            if os.path.exists(qr_path):
                try:
                    with open(qr_path, "rb") as f:
                        qr_bytes = f.read()
                    st.download_button(
                        "📱 Download QR (Fallback)",
                        data=qr_bytes,
                        file_name=f"{student.get('student_id', 'unknown')}_qr.png",
                        mime="image/png",
                        key=f"fallback_download_{download_key_suffix}",
                        use_container_width=True
                    )
                except:
                    st.info("QR code not available")


def render_student_registration(face_service):
    """Render the page"""
    
    # Clear capture state if user navigates back to this page
    if "last_visited_page" not in st.session_state:
        st.session_state.last_visited_page = None
    
    current_page = "Registration"
    # Check if user just navigated to this page from another page
    if st.session_state.last_visited_page != current_page:
        # User navigated to this page, clear everything and go back to mode selection
        clear_capture()
        st.session_state.registration_success = False  # Clear success state
        if 'student_data' in st.session_state:
            del st.session_state.student_data
        # Clear registration method to return to method selection
        if 'registration_method' in st.session_state:
            del st.session_state.registration_method
    
    st.session_state.last_visited_page = current_page
    
    # Header Section
    st.markdown("""
    <div style="margin-bottom: 2rem;">
    <h1 style="font-size: 2.75rem; font-weight: 700; margin-bottom: 0.25rem;">Student Registration</h1>
    <p style="font-size: 1rem; color: #2D3436; margin-top: 0;">Register students with AI-powered face recognition</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check face service health before proceeding
    if not check_face_service_health(face_service):
        st.markdown("""
        <div style="background: rgba(255, 59, 48, 0.1); border: 1px solid rgba(255, 59, 48, 0.3); 
                    border-radius: 12px; padding: 1.5rem; margin: 2rem 0;">
            <h4 style="color: #FF3B30; margin-bottom: 0.5rem;">⚠️ Service Required</h4>
            <p style="color: #8E8E93; margin: 0;">Face recognition service is required for student registration.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Registration section
    # Removed "View Students" tab - functionality moved to QR Management page
    st.markdown("<div style='margin-bottom: 2rem; text-align: center;'><h2 style='font-size: 2.5rem; font-weight: 600; margin-bottom: 1rem;'>Choose Registration Method</h2><p style='font-size: 1.2rem; color: #8E8E93;'>Select the method that works best for you</p></div>", unsafe_allow_html=True)
    
    # Registration method selection with big cards
    col1, spacer, col2 = st.columns([5, 1, 5])
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FC 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            color: #2D3436;
            box-shadow: 0 4px 20px rgba(45, 52, 54, 0.08), 0 1px 4px rgba(45, 52, 54, 0.04);
            border: 2px solid rgba(45, 52, 54, 0.1);
            transition: all 0.2s ease;
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.9;">🎯</div>
            <h3 style="margin-bottom: 1rem; font-weight: 700; font-size: 1.4rem; letter-spacing: -0.02em; color: #2D3436;">Smart Card Scanner</h3>
            <p style="margin: 0; opacity: 0.8; font-size: 1.0rem; line-height: 1.5; font-weight: 500; color: #636E72;">Point camera at student ID card<br/>AI extracts all information automatically</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add some spacing and style the button
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        smart_scan = st.button("🎯 Use Smart Scanner", key="smart_scan", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FBFF 100%);
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            color: #2D3436;
            box-shadow: 0 4px 20px rgba(116, 185, 255, 0.12), 0 1px 4px rgba(116, 185, 255, 0.08);
            border: 2px solid rgba(116, 185, 255, 0.15);
            transition: all 0.2s ease;
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.9;">✏️</div>
            <h3 style="margin-bottom: 1rem; font-weight: 700; font-size: 1.4rem; letter-spacing: -0.02em; color: #2D3436;">Quick Input</h3>
            <p style="margin: 0; opacity: 0.8; font-size: 1.0rem; line-height: 1.5; font-weight: 500; color: #636E72;">Take a photo and fill in details<br/>Perfect for manual registration</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add some spacing and style the button  
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        quick_input = st.button("✏️ Use Quick Input", key="quick_input", type="primary", use_container_width=True)
    
    # Set registration method based on button clicks
    if smart_scan:
        st.session_state.registration_method = "AI Auto-Scan Student Card"
    elif quick_input:
        st.session_state.registration_method = "Manual Entry"
    
    # Get current method from session state
    registration_method = st.session_state.get('registration_method', None)
    
    # Enhanced button styling to match card design - only for registration cards
    st.markdown("""
    <style>
        /* Registration card buttons only - use specific selectors */
        div[data-testid="column"] .stButton > button[kind="primary"]:not([data-testid*="nav"]) {
            background: linear-gradient(135deg, #2D3436 0%, #636E72 100%) !important;
            border: 2px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 16px !important;
            color: white !important;
            font-weight: 600 !important;
            font-size: 1.0rem !important;
            padding: 0.75rem 1.5rem !important;
            height: auto !important;
            min-height: 48px !important;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
            box-shadow: 0 4px 16px rgba(45, 52, 54, 0.15) !important;
            letter-spacing: -0.01em !important;
            backdrop-filter: blur(8px) !important;
        }
        
        div[data-testid="column"] .stButton > button[kind="primary"]:hover:not([data-testid*="nav"]) {
            background: linear-gradient(135deg, #636E72 0%, #2D3436 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(45, 52, 54, 0.2) !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
        }
        
        div[data-testid="column"] .stButton > button[kind="primary"]:active:not([data-testid*="nav"]) {
            transform: translateY(0) !important;
            box-shadow: 0 2px 8px rgba(45, 52, 54, 0.15) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # AI Auto-Scan Method - Simplified
    if registration_method == "AI Auto-Scan Student Card":
        st.markdown("<div style='margin: 2rem 0; text-align: center;'><div style='display: inline-block; background: rgba(45, 52, 54, 0.08); padding: 0.75rem 1.5rem; border-radius: 24px; color: #2D3436; font-weight: 600; box-shadow: 0 2px 8px rgba(45, 52, 54, 0.08); border: 2px solid rgba(45, 52, 54, 0.1);'>🎯 Smart Scanner Active</div></div>", unsafe_allow_html=True)
        # Step progress indicator for AI scan with modern blue gradient
        if st.session_state.capture_state.get('processed_image') is None:
            step_indicator = "Step 1 of 3: Capture Card"
            step_color = "#3b82f6"  # Modern blue
            step_bg = "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"
        elif st.session_state.capture_state.get('ocr_result') is None:
            step_indicator = "Step 2 of 3: Extract Information"
            step_color = "#8b5cf6"  # Purple accent
            step_bg = "linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)"
        else:
            step_indicator = "Step 3 of 3: Complete Registration"
            step_color = "#10b981"  # Success green
            step_bg = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
            
        st.markdown(f"""
        <div style="
            background: {step_bg};
            color: white;
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin: 1.5rem 0;
            text-align: center;
            box-shadow: 0 8px 25px {step_color}30;
        ">
            <h3 style="margin: 0; font-weight: 600; font-size: 1.2rem;">{step_indicator}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if we already have a processed image in session state
        if (st.session_state.capture_state.get('processed_image') is not None or
            st.session_state.capture_state.get('uploaded_processed_image') is not None):
                # Use existing processed image (handle numpy arrays properly)
            if st.session_state.capture_state.get('processed_image') is not None:
                captured_image = st.session_state.capture_state.get('processed_image')
            else:
                captured_image = st.session_state.capture_state.get('uploaded_processed_image')
            
            # Show success message with modern styling
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: #ffffff;
                padding: 2rem;
                border-radius: 16px;
                text-align: center;
                margin: 1.5rem 0;
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
            ">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">✅</div>
                <h4 style="margin: 0 0 0.5rem 0; font-weight: 700; font-size: 1.3rem; color: #ffffff; text-shadow: 0 1px 3px rgba(0,0,0,0.3);">Card Captured Successfully!</h4>
                <p style="margin: 0; font-size: 1.1rem; color: #ffffff; font-weight: 500; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">Ready to extract student information</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show clear button to start over
            col_clear1, col_clear2, col_clear3 = st.columns([1, 2, 1])
            with col_clear2:
                if st.button("🔄 Start Over", key="clear_capture_btn", use_container_width=True):
                    clear_capture()
                    st.rerun()
        else:
            # No existing image, show capture interface with modern design
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                color: #1e293b;
                padding: 2.5rem;
                border-radius: 20px;
                text-align: center;
                margin: 1.5rem 0;
                border: 2px solid #3b82f6;
                box-shadow: 0 10px 40px rgba(59, 130, 246, 0.1);
            ">
                <div style="font-size: 3.5rem; margin-bottom: 1.5rem;">🎯</div>
                <h3 style="margin-bottom: 1rem; font-weight: 600; color: #1e293b;">Capture Your Student Card</h3>
                <p style="margin: 0; color: #64748b; font-size: 1.1rem;">Position your student ID card clearly in the camera frame</p>
            </div>
            """, unsafe_allow_html=True)
            
            captured_image = capture_card_with_guide()
            
            if captured_image is not None:
                # Store in session state
                st.session_state.capture_state['processed_image'] = captured_image
                st.session_state.capture_state['mode'] = 'registration'
                st.rerun()  # Rerun to show the image and button
        
        # Extract info button (show if we have an image)
        if (st.session_state.capture_state.get('processed_image') is not None or
            st.session_state.capture_state.get('uploaded_processed_image') is not None):
            
            # Get the captured image (handle numpy arrays properly)
            if st.session_state.capture_state.get('processed_image') is not None:
                captured_image = st.session_state.capture_state.get('processed_image')
            else:
                captured_image = st.session_state.capture_state.get('uploaded_processed_image')
            
            col_extract1, col_extract2, col_extract3 = st.columns([1, 2, 1])
            with col_extract2:
                if st.button("📝 Extract Information", type="primary", key="extract_btn", use_container_width=True):
                    # Use beautiful OCR animation for student registration
                    result = show_ocr_processing_animation(
                        extract_student_info_optimized, 
                        captured_image, 
                        debug=False, 
                        use_stable_ocr=True
                    )
                    
                    if result['success']:
                        # Extract face from student card automatically
                        # st.text("👤 Extracting face from student card...")  # Removed to prevent interference
                        face_result = extract_face_from_card(captured_image, debug=False)
                        
                        if face_result['success']:
                            result['face_encoding'] = face_result['face_encoding']
                            result['face_image'] = face_result['face_image']
                            # st.text("✅ Face extracted successfully!")  # Removed to prevent interference
                        else:
                            pass  # st.text(f"⚠️ Face extraction: {face_result['message']}")  # Removed
                        
                        st.session_state.capture_state['ocr_result'] = result
                        st.balloons()
                        
                        # Display extracted info with better styling
                        face_status = "✅ Extracted" if face_result.get('success') else "⚠️ Failed"
                        face_color = "#4ecdc4" if face_result.get('success') else "#ff6b6b"
                        
                        # Display extracted info without HTML
                        st.success("✨ **Information Extracted!**")
                        
                        # Use columns for better layout
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.write("**🆔 Student ID:**")
                            st.write("**👤 Name:**")
                            st.write("**👤 Face Recognition:**")
                        with col2:
                            st.write(f"**{result['student_id']}**")
                            st.write(f"**{result.get('name', 'Not detected')}**")
                            st.write(f"**{face_status}**")
                    else:
                        # Show more detailed failure info with quality warning if present
                        quality_warning = result.get('quality_warning', '')
                        confidence = result.get('confidence', 0)
                        retries = result.get('retries', 0)
                        
                        st.markdown("""
                        <div style="
                            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                            color: #ffffff;
                            padding: 2.5rem;
                            border-radius: 16px;
                            text-align: center;
                            margin: 1.5rem 0;
                            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3);
                        ">
                            <div style="font-size: 2.5rem; margin-bottom: 1rem;">❌</div>
                            <h4 style="margin: 0 0 0.5rem 0; font-weight: 700; font-size: 1.3rem; color: #ffffff; text-shadow: 0 1px 3px rgba(0,0,0,0.4);">Could not extract information</h4>
                            <p style="margin: 0; font-size: 1.1rem; color: #ffffff; font-weight: 500; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Try repositioning your card or use better lighting</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show debug info if available
                        if quality_warning:
                            st.warning(f"⚠️ {quality_warning}")
                        
                        if confidence > 0:
                            st.info(f"📊 Extraction confidence was only {confidence:.1%}")
                        
                        if retries > 0:
                            st.info(f"🔄 Attempted {retries + 1} times with different strategies")
                        
                        col_retry1, col_retry2, col_retry3 = st.columns([1, 2, 1])
                        with col_retry2:
                            if st.button("🔄 Try Again", use_container_width=True, type="primary"):
                                clear_capture()
                                st.rerun()
            
            # ✅ Show registration form if OCR result exists (INDEPENDENT of button click)
            if ('ocr_result' in st.session_state.capture_state and 
                st.session_state.capture_state['ocr_result'] and 
                st.session_state.capture_state['ocr_result']['success']):
                
                result = st.session_state.capture_state['ocr_result']
                
                # Registration form with extracted data
                st.markdown("---")
                st.markdown("### ✅ Complete Registration")
                
                with st.form("simplified_registration"):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        student_id = st.text_input(
                            "🆔 Student ID *", 
                            value=result.get('student_id', ''),
                            help="Edit if detection was incorrect"
                        )
                        
                        student_name = st.text_input(
                            "👤 Full Name *", 
                            value=result.get('name', ''),
                            help="Enter student's full name"
                        )
                    
                    with col2:
                        # AI Confidence card with modern colors
                        confidence_level = "High" if result.get('confidence', 0) > 0.8 else "Medium" if result.get('confidence', 0) > 0.5 else "Low"
                        confidence_color = "#10b981" if confidence_level == "High" else "#f59e0b" if confidence_level == "Medium" else "#ef4444"
                        
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                            border: 2px solid {confidence_color};
                            border-radius: 16px;
                            padding: 2rem;
                            text-align: center;
                            margin-bottom: 1.5rem;
                            box-shadow: 0 4px 20px {confidence_color}20;
                        ">
                            <div style="font-size: 2rem; margin-bottom: 1rem; color: {confidence_color};">📊</div>
                            <h4 style="margin: 0 0 0.5rem 0; color: #1e293b; font-weight: 600;">AI Confidence</h4>
                            <div style="font-size: 1.3rem; font-weight: 700; color: {confidence_color};">{confidence_level}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Face extraction status card with modern design
                        if result.get('face_encoding') is not None:
                            st.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                                border: 2px solid #10b981;
                                border-radius: 16px;
                                padding: 2rem;
                                text-align: center;
                                box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15);
                            ">
                                <div style="font-size: 2rem; margin-bottom: 1rem; color: #10b981;">✅</div>
                                <h4 style="margin: 0 0 0.5rem 0; color: #1e293b; font-weight: 600;">Face Recognition</h4>
                                <div style="color: #10b981; font-weight: 600; font-size: 1.1rem;">Ready for Check-in</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add spacing before face image
                            if result.get('face_image'):
                                st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
                                st.image(result['face_image'], caption="Extracted Face", width=150)
                        else:
                            st.markdown("""
                            <div style="
                                background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                                border: 2px solid #ef4444;
                                border-radius: 16px;
                                padding: 2rem;
                                text-align: center;
                                box-shadow: 0 4px 20px rgba(239, 68, 68, 0.15);
                            ">
                                <div style="font-size: 2rem; margin-bottom: 1rem; color: #ef4444;">⚠️</div>
                                <h4 style="margin: 0 0 0.5rem 0; color: #1e293b; font-weight: 600;">Face Recognition</h4>
                                <div style="color: #ef4444; font-weight: 600; font-size: 1.1rem;">Not Available</div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.info("📝 Registration will proceed without face recognition")
                    
                    # Submit button
                    submitted = st.form_submit_button(
                        "✅ Register Student", 
                        type="primary",
                        use_container_width=True
                    )
                
                # Email notification option - OUTSIDE the form to avoid state issues
                st.markdown("#### 📧 Email Notification")
                send_email = st.checkbox("📨 Send QR code via email", help="Get your QR code delivered to your email")
                
                student_email = ""
                if send_email:
                    student_email = st.text_input(
                        "📧 Email Address *",
                        placeholder="student@example.com",
                        help="Enter your email to receive the QR code"
                    )
                
                # Handle form submission - OUTSIDE email conditional
                if submitted:
                    try:
                        # Simple validation
                        if not student_id or not student_id.strip():
                            st.error("❌ Student ID is required!")
                            st.stop()
                        
                        if not student_name or not student_name.strip():
                            st.error("❌ Student name is required!")
                            st.stop()
                        
                        # Validate ID format (basic)
                        if len(student_id.strip()) < 8:
                            st.error("❌ Student ID too short!")
                            st.stop()
                        
                        # Validate email if sending email is selected
                        if send_email:
                            if not student_email or not student_email.strip():
                                st.error("❌ Email address is required when email notification is selected!")
                                st.stop()
                            
                            # Basic email format validation
                            import re
                            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                            if not re.match(email_pattern, student_email.strip()):
                                st.error("❌ Please enter a valid email address!")
                                st.stop()
                        
                        # Check for duplicates (safe access to handle different record formats)
                        db = load_database()
                        existing_ids = []
                        for record in db:
                            if isinstance(record, dict):
                                # Try different possible field names
                                record_id = record.get('id') or record.get('student_id') or record.get('ID')
                                if record_id:
                                    existing_ids.append(str(record_id).strip())
                        
                        if student_id.strip() in existing_ids:
                            st.error(f"❌ Student ID {student_id} already exists!")
                            st.stop()
                        
                        # Get face data from OCR result (extracted from card)
                        face_image = result.get('face_image')
                        face_encoding = result.get('face_encoding')
                        
                        # Register student with or without face data
                        with st.spinner("Registering student..."):
                            try:
                                # Save face image if available
                                image_path = None
                                if face_image:
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    image_filename = f"{student_id}_{timestamp}.jpg"
                                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                                    face_image.save(image_path)
                                    # Normalize path for consistent storage
                                    image_path = normalize_path(image_path)
                                
                                # Create student record
                                student_record = {
                                    'id': student_id,
                                    'student_id': student_id,  # Ensure both fields for compatibility
                                    'name': student_name,
                                    'image_path': image_path,
                                    'encoding': face_encoding,  # May be None
                                    'email': student_email.strip() if send_email else None,
                                    'email_notifications': send_email,
                                    'registration_date': datetime.now().isoformat(),
                                    'registered_via': 'ai_scan_auto_face' if face_encoding else 'ai_scan_text_only'
                                }
                                
                                # Save to database (function doesn't return value, so assume success)
                                save_to_database(student_record)
                                
                                # Generate QR code for the student
                                qr_path, qr_msg = generate_qr_code(student_id, student_name, QR_FOLDER)
                                if qr_path is None:
                                    st.warning(f"⚠️ QR generation failed: {qr_msg}")
                                    st.info("💡 You can generate QR manually from QR Management page")
                                    # Continue registration even if QR fails
                                    st.session_state.generated_qr_path = None  # Clear QR path since generation failed
                                else:
                                    st.session_state.generated_qr_path = qr_path  # Set QR path only when generation succeeds
                                    
                                    # Send email if requested and QR generation successful
                                    if send_email and student_email:
                                        from core.email_module import send_qr_email, is_email_enabled
                                        
                                        if is_email_enabled():
                                            try:
                                                success, email_msg = send_qr_email(
                                                    student_email.strip(),
                                                    student_name,
                                                    student_id,
                                                    qr_path
                                                )
                                                if success:
                                                    st.success(f"📧 {email_msg}")
                                                else:
                                                    st.warning(f"📧 Email sending failed: {email_msg}")
                                                    st.info("💡 You can resend the QR code from QR Management page")
                                            except Exception as e:
                                                st.warning(f"📧 Email sending failed: {str(e)}")
                                                st.info("💡 You can resend the QR code from QR Management page")
                                        else:
                                            st.warning("📧 Email service not configured. QR code not sent via email.")
                                            st.info("💡 Configure Gmail credentials in .env file to enable email notifications")
                                
                                # ✅ Clear OCR result to hide form and show success
                                st.session_state.capture_state['ocr_result'] = None
                                st.session_state.registration_success = True
                                st.session_state.student_data = student_record
                                
                                # Show success message
                                st.success("🎉 Registration completed successfully!")
                                st.balloons()
                                
                                # Force rerun to show success state
                                st.rerun()
                                
                            except Exception as save_error:
                                st.error(f"❌ Failed to save student record: {str(save_error)}")
                                raise save_error
                    
                    except Exception as e:
                        st.error(f"❌ Registration failed: {str(e)}")
                        st.error(f"Debug info: {type(e).__name__}: {str(e)}")
                
            
            # ✅ Show success state if registration completed
            if st.session_state.get('registration_success') and st.session_state.get('student_data'):
                student_data = st.session_state.student_data
                
                # Display registered student information
                st.markdown("### ✅ Registration Details")
                st.info(f"""
                **Student ID:** {student_data['id']}
                **Name:** {student_data['name']}
                **Face Recognition:** {'✅ Enabled' if student_data.get('encoding') else '❌ Not available'}
                **Registered:** {student_data['registration_date']}
                """)
                
                # Provide option to register new student
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🆕 Register Another Student", type="primary"):
                        # Clear all states
                        st.session_state.registration_success = False
                        st.session_state.student_data = None
                        clear_capture()
                        st.rerun()
                with col2:
                    st.info("💡 View all students in QR Management page")
        
        # Clear button
        if st.button("🗑️ Reset Scanner"):
            clear_capture()
            st.rerun()
        
        # ✅ NEW SIMPLIFIED WORKFLOW COMPLETE
        # The old complex logic below this line has been replaced
        # TODO: Clean up remaining legacy code manually if needed
        
    # OLD COMPLEX LOGIC DISABLED - Using new simplified workflow above
    # Commenting out for reference but should be removed in future cleanup
    if False:  # Disable this entire block
        if not st.session_state.ai_scan_complete:
            # Stage 1: Capture Photo
            if st.session_state.ai_scan_stage == "capture":
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("#### 📐 Positioning Guide")
                    # Display the positioning guide
                    guide_img = create_card_positioning_guide()
                    st.image(cv2.cvtColor(guide_img, cv2.COLOR_BGR2RGB), 
                            caption="Align your card with the green outline",
                            use_column_width=True)
                    
                    # Quick tips for users
                    st.markdown("""
                    **✅ Quick Checklist:**
                    - Card aligned with green box
                    - Good lighting (no shadows)
                    - Card flat and steady
                    - Text clearly visible
                    """)
                
                with col2:
                    st.markdown("#### 📸 Capture Card")
                    
                    # Camera input with external camera preference for card scanning
                    captured_photo = create_camera_input_with_preference(
                        label="Click to capture when card is positioned",
                        use_external=True,
                        key=f"ai_scan_camera_{st.session_state.scan_counter}",
                        help="Use external camera for better card scanning results"
                    )
                    
                    # Save captured photo and move to mode selection
                    if captured_photo is not None:
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.button("📋 Choose Processing Mode", type="primary", use_container_width=True):
                                # Convert to bytes to persist across reruns
                                if captured_photo is not None:
                                    import io
                                    bytes_data = captured_photo.getvalue()
                                    st.session_state.captured_photo = io.BytesIO(bytes_data)
                                    st.session_state.ai_scan_stage = "mode_select"
                                    st.rerun()
                        
                        with col_btn2:
                            if st.button("🔄 Retake", use_container_width=True):
                                st.session_state.scan_counter += 1
                                st.rerun()
            
            # Stage 2: Mode Selection
            elif st.session_state.ai_scan_stage == "mode_select":
                # Show captured image
                if st.session_state.captured_photo is not None:
                    st.markdown("#### 📸 Captured Image")
                    pil_image = Image.open(st.session_state.captured_photo)
                    pil_image = fix_image_orientation(pil_image)  # Fix orientation
                    st.image(pil_image, caption="Captured Student Card", width=400)
                    
                    st.markdown("---")
                    st.markdown("### 🎯 Choose OCR Processing Mode")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🤖 Auto Mode", use_container_width=True, type="primary"):
                            st.session_state.scan_processing_mode = "auto"
                            st.session_state.ai_scan_stage = "processing"
                            st.rerun()
                        st.markdown("**Quick & Smart Recognition**")
                        st.markdown("- ✅ Fast processing")
                        st.markdown("- ✅ No manual input needed")
                        st.markdown("- ❓ May miss some text positioning")
                    
                    with col2:
                        if st.button("🎯 Manual Mode", use_container_width=True):
                            st.session_state.scan_processing_mode = "manual"
                            st.session_state.ai_scan_stage = "manual_crop"
                            st.rerun()
                        st.markdown("**Precise Text Selection**")
                        st.markdown("- ✅ Precise text region control")
                        st.markdown("- ✅ Higher recognition accuracy")
                        st.markdown("- ⏱️ Requires manual selection")
                    
                    # Navigation buttons
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📸 Retake Photo", use_container_width=True):
                            st.session_state.ai_scan_stage = "capture"
                            st.session_state.captured_photo = None
                            st.session_state.scan_counter += 1
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            # Reset all AI scan states
                            st.session_state.ai_scan_stage = "capture"
                            st.session_state.captured_photo = None
                            st.session_state.scan_processing_mode = "auto"
                            st.session_state.manual_crop_result = None
                            st.rerun()
            
            # Stage 3: Manual Crop (if manual mode selected)
            elif st.session_state.ai_scan_stage == "manual_crop":
                if st.session_state.captured_photo is not None:
                    st.markdown("#### 🎯 Manual Text Region Selection")
                    st.info("Select the text region on your student card for accurate OCR recognition")
                    
                    try:
                        # Convert photo to PIL Image for cropping
                        # Reset seek position for BytesIO
                        st.session_state.captured_photo.seek(0)
                        pil_image = Image.open(st.session_state.captured_photo)
                        pil_image = fix_image_orientation(pil_image)  # Fix orientation
                        
                        # Interactive cropping removed for simplified deployment
                        CROPPER_AVAILABLE = False
                        
                        # Use the full image without cropping (simplified deployment)
                        crop_result = pil_image
                        crop_success = True
                        
                        if crop_success is True:
                            # User accepted the crop
                            st.session_state.manual_crop_result = crop_result
                            st.session_state.ai_scan_stage = "processing"
                            st.rerun()
                        elif crop_success is False:
                            # User canceled manual crop, go back to mode selection
                            st.session_state.ai_scan_stage = "mode_select"
                            st.session_state.manual_crop_result = None
                            st.rerun()
                        # If crop_success is None, continue showing the interface (no rerun)
                        
                    except Exception as e:
                        st.error(f"❌ Error in manual crop mode: {str(e)}")
                        st.error("Please try again or use auto mode.")
                        if st.button("🔄 Back to Mode Selection", key="error_back_to_mode"):
                            st.session_state.ai_scan_stage = "mode_select"
                            st.session_state.manual_crop_result = None
                            st.rerun()
            
            # Stage 4: Processing
            elif st.session_state.ai_scan_stage == "processing":
                if st.session_state.captured_photo is not None:
                    st.markdown(f"#### 🔄 Processing with {st.session_state.scan_processing_mode.title()} Mode")
                    
                    with st.spinner(f"🤖 Analyzing student card using {st.session_state.scan_processing_mode} mode..."):
                        # Process the card based on selected mode
                        if st.session_state.scan_processing_mode == "manual":
                            result = process_ai_scanned_card(
                                st.session_state.captured_photo,
                                manual_crop_region=st.session_state.manual_crop_result,
                                processing_mode="manual"
                            )
                        else:
                            result = process_ai_scanned_card(
                                st.session_state.captured_photo,
                                processing_mode="auto"
                            )
                        
                        if result['success']:
                            # Save results to session state
                            st.session_state.scanned_data = result
                            st.session_state.ai_scan_complete = True
                            
                            # Show success message based on processing mode
                            if result['ocr_success']:
                                st.success(f"✅ Card processed successfully using {result.get('processing_mode', 'unknown')} mode!")
                            else:
                                st.warning("⚠️ OCR partially failed. Please verify information below.")
                            
                            # Reset scan states for next use
                            st.session_state.ai_scan_stage = "capture"
                            st.session_state.captured_photo = None
                            st.session_state.scan_processing_mode = "auto"
                            st.session_state.manual_crop_result = None
                            
                            st.rerun()
                        else:
                            st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                            
                            # Show retry options
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("🔄 Try Different Mode", use_container_width=True):
                                    st.session_state.ai_scan_stage = "mode_select"
                                    st.session_state.manual_crop_result = None
                                    st.rerun()
                            with col2:
                                if st.button("📸 Retake Photo", use_container_width=True):
                                    st.session_state.ai_scan_stage = "capture"
                                    st.session_state.captured_photo = None
                                    st.session_state.scan_counter += 1
                                    st.rerun()
                            with col3:
                                if st.button("❌ Cancel", use_container_width=True):
                                    # Reset all states
                                    st.session_state.ai_scan_stage = "capture"
                                    st.session_state.captured_photo = None
                                    st.session_state.scan_processing_mode = "auto"
                                    st.session_state.manual_crop_result = None
                                    st.rerun()
        
        # Show confirmation form after successful scan
        if st.session_state.ai_scan_complete and st.session_state.scanned_data:
            st.markdown("---")
            st.markdown("### ✅ Confirm Scanned Information")
            
            # Display scanned data
            scanned_data = st.session_state.scanned_data
            
            with st.form("ai_scan_confirmation"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Editable fields with scanned data
                    student_id = st.text_input(
                        "🆔 Student ID",
                        value=scanned_data.get('student_id', ''),
                        help="Verify and edit if needed"
                    )
                    name = st.text_input(
                        "👤 Full Name",
                        value=scanned_data.get('name', ''),
                        help="Verify and edit if needed"
                    )
                    
                    # Show confidence score and processing mode
                    if scanned_data.get('ocr_success'):
                        confidence = scanned_data.get('confidence', 0.0)
                        processing_mode = scanned_data.get('processing_mode', 'auto')
                        mode_icon = "🎯" if processing_mode == "manual" else "🤖"
                        st.info(f"{mode_icon} Processing Mode: {processing_mode.title()}")
                        st.info(f"🤖 AI Confidence: {confidence*100:.1f}%")
                
                with col2:
                    # Display extracted face
                    if scanned_data.get('face_image'):
                        st.image(scanned_data['face_image'], 
                                caption="Extracted Face Photo", 
                                width=200)
                        
                        # Validate face image
                        is_valid, validation_msg = validate_image(scanned_data['face_image'])
                        if is_valid:
                            st.success(f"✅ {validation_msg}")
                        else:
                            st.error(f"❌ {validation_msg}")
                
                # Form buttons
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    submitted = st.form_submit_button(
                        "✅ Confirm & Register",
                        use_container_width=True,
                        type="primary"
                    )
                
                with col_btn2:
                    if st.form_submit_button("🔄 Scan Again", use_container_width=True):
                        # Reset all scan states
                        st.session_state.ai_scan_complete = False
                        st.session_state.scanned_data = {}
                        st.session_state.scan_counter += 1
                        st.session_state.ai_scan_stage = "capture"
                        st.session_state.captured_photo = None
                        st.session_state.scan_processing_mode = "auto"
                        st.session_state.manual_crop_result = None
                        st.rerun()
                
                # Handle form submission
                if submitted:
                    if not student_id or not name:
                        st.error("❌ Please fill in all required fields.")
                    else:
                        try:
                            # Validate inputs
                            validate_student_id(student_id)
                            validate_name(name)
                            
                            # Check if student already exists (safe field access)
                            db = load_database()
                            if any((entry.get("student_id") or entry.get("id")) == student_id for entry in db):
                                st.warning(f"⚠️ Student ID '{student_id}' already exists.")
                            else:
                                # Process registration
                                with st.spinner("🔄 Registering student..."):
                                    # Save face image
                                    img_path = os.path.join(UPLOAD_FOLDER, f"{student_id}.jpg")
                                    scanned_data['face_image'].save(img_path)
                                    
                                    # Generate QR code
                                    qr_path, qr_msg = generate_qr_code(student_id, name, QR_FOLDER)
                                    if qr_path is None:
                                        st.error(f"❌ QR generation failed: {qr_msg}")
                                        st.stop()
                                    
                                    # Save to database
                                    entry = {
                                        "student_id": student_id,
                                        "name": name,
                                        "image_path": img_path,
                                        "encoding": scanned_data.get('face_encoding'),
                                        "registration_method": "AI_SCAN",
                                        "ai_confidence": scanned_data.get('confidence', 0.0)
                                    }
                                    save_to_database(entry)
                                    
                                    # Log activity
                                    log_activity("REGISTRATION", f"AI scan registration for {name} ({student_id})")
                                    
                                    # Update session state
                                    st.session_state.registration_success = True
                                    st.session_state.generated_qr_path = qr_path
                                    st.session_state.student_data = {
                                        "student_id": student_id,
                                        "name": name,
                                        "img_path": img_path
                                    }
                                    
                                    # Reset all AI scan states
                                    st.session_state.ai_scan_complete = False
                                    st.session_state.scanned_data = {}
                                    st.session_state.ai_scan_stage = "capture"
                                    st.session_state.captured_photo = None
                                    st.session_state.scan_processing_mode = "auto"
                                    st.session_state.manual_crop_result = None
                                    
                                    st.success("🎉 Registration completed successfully!")
                                    st.rerun()
                                    
                        except ValidationError as e:
                            st.error(f"❌ Validation Error: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Registration failed: {str(e)}")
    # END OF OLD COMPLEX LOGIC - Now using simplified workflow above
    
    # Manual Entry Method
    elif registration_method == "Manual Entry":
        st.markdown("<div style='margin: 2rem 0; text-align: center;'><div style='display: inline-block; background: rgba(116, 185, 255, 0.08); padding: 0.75rem 1.5rem; border-radius: 24px; color: #74B9FF; font-weight: 600; box-shadow: 0 2px 8px rgba(116, 185, 255, 0.08); border: 2px solid rgba(116, 185, 255, 0.1);'>✏️ Quick Input Active</div></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="feature-card">
            <h4 style="margin-bottom: 0.5rem;">📝 Manual Registration</h4>
            <p style="color: #8E8E93; margin: 0;">Traditional registration with photo capture</p>
        </div>
        """, unsafe_allow_html=True)
        
        captured_image = None
        
        # Camera capture method - simplified for mobile
        st.markdown("#### 📷 Take Student Photo")
        st.markdown("""
        <div style="background: rgba(0, 122, 255, 0.1); border: 1px solid rgba(0, 122, 255, 0.3); 
                    border-radius: 12px; padding: 1rem; margin: 1rem 0;">
            <p style="color: #007AFF; margin: 0; font-weight: 500;">📱 Your device camera will open for a clear front-facing photo</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Streamlit camera input for better mobile compatibility - using external camera
            camera_photo = create_camera_input_with_preference(
                label="📷 Take a clear photo",
                use_external=True,
                key="manual_entry_camera",
                help="Use external camera for student card capture, works on all mobile browsers"
            )
            
            if camera_photo:
                # Convert and store in session state with correct orientation
                captured_image = Image.open(camera_photo)
                captured_image = fix_image_orientation(captured_image)  # Fix orientation
                st.session_state["registration_captured_image"] = captured_image
                
                # Retake button
                if st.button("🔄 Retake Photo", key="retake_mobile", use_container_width=True):
                    del st.session_state["registration_captured_image"]
                    st.rerun()
        
        with col2:
            # Display captured image
            if "registration_captured_image" in st.session_state:
                captured_image = st.session_state["registration_captured_image"]
                st.image(captured_image, caption="📷 Captured Photo", width=200)
                
                # Validate captured image
                with st.spinner("🔍 Validating photo quality..."):
                    is_valid, validation_msg = validate_image(captured_image)
                    
                    if is_valid:
                        st.success(f"✅ {validation_msg}")
                    else:
                        st.error(f"❌ {validation_msg}")
                        st.info("💡 Use 'Retake Photo' to capture a better image")
            else:
                st.info("📷 Click 'Open Camera' to take a photo")
        
        # Use captured image
        final_image = captured_image
        
        st.markdown("---")
        
        # Registration form (basic info only)
        with st.form("manual_registration"):
            st.markdown("#### 📝 Student Information")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                student_id = st.text_input(
                    "🆔 Student ID", 
                    placeholder="e.g. 24WMR12345",
                    help="Enter unique student ID"
                )
            
            with col2:
                name = st.text_input(
                    "👤 Full Name", 
                    placeholder="e.g. John Doe",
                    help="Enter full name as in ID"
                )
            
            # Photo status indicator
            if final_image is not None:
                st.success("✅ Photo ready for registration")
            else:
                st.warning("⚠️ Please take a photo using the camera above")
            
            # Submit button
            submitted = st.form_submit_button(
                "🚀 Register Student", 
                use_container_width=True,
                type="primary"
            )
        
        # Email notification section - OUTSIDE form for real-time updates
        st.markdown("#### 📧 Email Notification")
        send_email = st.checkbox(
            "📨 Send QR code via email", 
            help="Get your QR code delivered to your email", 
            key="manual_email_checkbox"
        )
        
        student_email = ""
        if send_email:
            student_email = st.text_input(
                "📧 Email Address",
                placeholder="student@example.com",
                help="Enter your email to receive the QR code",
                key="manual_email_input"
            )
        
        # Handle form submission - can access all variables
        if submitted:
            # Basic validation
            if not student_id or not name or final_image is None:
                st.error("❌ Please fill all fields and provide a photo.")
            elif send_email and (not student_email or not student_email.strip()):
                st.error("❌ Email address is required when email notification is selected!")
            elif send_email and student_email:
                # Validate email format
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, student_email.strip()):
                    st.error("❌ Please enter a valid email address!")
                else:
                    # Continue with registration
                    process_manual_registration = True
            else:
                # Continue without email
                process_manual_registration = True
            
            if 'process_manual_registration' in locals() and process_manual_registration:
                # Check if student already exists (safe field access)
                db = load_database()
                existing_student = any((entry.get("student_id") or entry.get("id")) == student_id for entry in db)
                
                if existing_student:
                    st.warning(f"⚠️ Student ID '{student_id}' already exists.")
                else:
                    # Process registration
                    with st.spinner("🔄 Processing registration..."):
                        try:
                            # Validate image
                            is_valid, validation_msg = validate_image(final_image)
                            if not is_valid:
                                st.error(f"❌ {validation_msg}")
                                st.stop()
                            
                            # Generate face encoding
                            encoding, encoding_msg = generate_face_encoding(final_image)
                            if encoding is None:
                                st.error(f"❌ {encoding_msg}")
                                st.stop()
                            
                            # Save image
                            img_path = os.path.join(UPLOAD_FOLDER, f"{student_id}.jpg")
                            final_image.save(img_path)
                            
                            # Generate QR code
                            qr_path, qr_msg = generate_qr_code(student_id, name, QR_FOLDER)
                            if qr_path is None:
                                st.error(f"❌ {qr_msg}")
                                st.stop()
                            
                            # Save to database
                            entry = {
                                "student_id": student_id,
                                "id": student_id,  # Ensure compatibility
                                "name": name,
                                "image_path": img_path,
                                "encoding": encoding,
                                "email": student_email.strip() if send_email else None,
                                "email_notifications": send_email,
                                "registration_date": datetime.now().isoformat(),
                                "registration_method": "MANUAL_ENTRY"
                            }
                            save_to_database(entry)
                            
                            # Send email if requested and QR generation successful
                            if send_email and student_email and qr_path:
                                from core.email_module import send_qr_email, is_email_enabled
                                
                                if is_email_enabled():
                                    try:
                                        success, email_msg = send_qr_email(
                                            student_email.strip(),
                                            name,
                                            student_id,
                                            qr_path
                                        )
                                        if success:
                                            st.success(f"📧 {email_msg}")
                                        else:
                                            st.warning(f"📧 Email sending failed: {email_msg}")
                                            st.info("💡 You can resend the QR code from QR Management page")
                                    except Exception as e:
                                        st.warning(f"📧 Email sending failed: {str(e)}")
                                        st.info("💡 You can resend the QR code from QR Management page")
                                else:
                                    st.warning("📧 Email service not configured. QR code not sent via email.")
                                    st.info("💡 Configure Gmail credentials in .env file to enable email notifications")
                            
                            # Clear captured image from session
                            if "registration_captured_image" in st.session_state:
                                del st.session_state["registration_captured_image"]
                            
                            # Update session state
                            st.session_state.registration_success = True
                            st.session_state.generated_qr_path = qr_path
                            st.session_state.student_data = {
                                "student_id": student_id,
                                "name": name,
                                "img_path": img_path
                            }
                            
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Registration failed: {str(e)}")
    
    # Show registration results
    if st.session_state.registration_success:
        st.success("🎉 Student registered successfully!")
        st.balloons()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Registered Student")
            # Check if image path exists and display accordingly
            image_path = st.session_state.student_data.get("img_path") or st.session_state.student_data.get("image_path")
            # Normalize path to fix mixed slashes issue
            image_path = normalize_path(image_path)
            if image_path and os.path.exists(image_path):
                st.image(
                    image_path, 
                    caption=f"📷 {st.session_state.student_data['name']}", 
                    width=300
                )
            else:
                st.info("📷 No student photo available")
            # Handle different field name formats
            student_id = st.session_state.student_data.get('student_id') or st.session_state.student_data.get('id')
            student_name = st.session_state.student_data.get('name')
            st.info(f"🆔 **Student ID:** {student_id}")
            st.info(f"👤 **Name:** {student_name}")
        
        with col2:
            st.subheader("🔐 Generated QR Code")
            
            # Safe QR code display with comprehensive error handling
            qr_path = getattr(st.session_state, 'generated_qr_path', None)
            
            if qr_path is not None and qr_path != "" and os.path.exists(qr_path):
                try:
                    # Verify the file is readable and not corrupted
                    with open(qr_path, 'rb') as f:
                        f.read(1)  # Try to read at least 1 byte
                    
                    st.image(
                        qr_path, 
                        caption="QR Code for Check-in", 
                        width=300
                    )
                    
                    # Download QR code button
                    try:
                        with open(qr_path, "rb") as f:
                            qr_bytes = f.read()
                        
                        st.download_button(
                            label="📥 Download QR Code",
                            data=qr_bytes,
                            file_name=f"{student_id}_qr.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    except Exception as download_error:
                        st.error(f"❌ Cannot download QR code: {str(download_error)}")
                        
                except Exception as img_error:
                    st.error(f"❌ Cannot display QR code: {str(img_error)}")
                    st.info("💡 Try generating QR manually from QR Management page")
            else:
                # More specific error messages
                if qr_path is None:
                    st.warning("⚠️ QR Code generation failed during registration")
                elif qr_path == "":
                    st.warning("⚠️ QR Code path is empty")
                elif not os.path.exists(qr_path):
                    st.warning(f"⚠️ QR Code file not found: {qr_path}")
                else:
                    st.error("❌ QR Code generation failed")
                
                st.info("💡 You can generate QR manually from QR Management page")
        
        # Reset button for new registration
        if st.button("🔄 Register Another Student", use_container_width=True):
            # Reset all registration states
            st.session_state.registration_success = False
            st.session_state.generated_qr_path = None
            st.session_state.student_data = {}
            if "registration_captured_image" in st.session_state:
                del st.session_state["registration_captured_image"]
            if "ai_scan_complete" in st.session_state:
                st.session_state.ai_scan_complete = False
            if "scanned_data" in st.session_state:
                st.session_state.scanned_data = {}
            st.rerun()
    # ===========================
