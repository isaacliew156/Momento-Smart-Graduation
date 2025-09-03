"""
Qr Management page for the Graduation Attendance System
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
# Interactive cropping removed for simplified deployment
from core.error_handler import *

# Import utils
from utils.config import *
from utils.session_manager import SessionManager, init_session_state, clear_capture
from utils.card_processing import *
from utils.ui_helpers import *

# Import email module
from core.email_module import send_qr_email, is_email_enabled


def render_qr_management():
    """Render the page"""
    
    # Track page visits for navigation state management
    if "last_visited_page" not in st.session_state:
        st.session_state.last_visited_page = None
    
    st.session_state.last_visited_page = "QR Management"
    
    st.title("🔐 QR Code Management Center")
    st.markdown('<p style="color: #2D3436; font-size: 1rem; margin-bottom: 1.5rem;">Manage, reprint, and track QR codes</p>', unsafe_allow_html=True)
    
    # Load database
    db = load_database()
    
    if not db:
        st.warning("📭 No students registered yet.")
        st.stop()
    
    # Create management tabs  
    tab1, tab2 = st.tabs([
        "🔍 Query & Reprint", 
        "📦 Bulk Management"
    ])
    
    # Query & Reprint Tab
    with tab1:
        st.markdown("### 🔍 Search and Reprint QR Codes")
        st.write("Search for a student and regenerate their QR code if needed.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Search method selection
            search_method = st.radio(
                "Search by:",
                ["Student ID", "Student Name", "View All Students"],
                horizontal=True
            )
            
            # Search input based on selected method
            if search_method == "Student ID":
                search_input = st.text_input(
                    "Enter Student ID:",
                    placeholder="e.g., 24WMR12345",
                    help="Enter the exact student ID"
                )
            elif search_method == "Student Name":
                search_input = st.text_input(
                    "Enter Student Name:",
                    placeholder="e.g., John Doe",
                    help="Enter full or partial name"
                )
            else:  # View All Students
                search_input = "VIEW_ALL"  # Special flag to show all students
        
        with col2:
            st.info("💡 **Quick Tips:**\n- Use exact ID for fastest search\n- Name search is case-insensitive\n- Reprint tracking is logged")
        
        # Search and display results
        if search_input:
            matches = []
            
            if search_input == "VIEW_ALL":
                # Show all students
                matches = db
                st.info(f"📋 Showing all {len(db)} registered students")
            else:
                # Search based on method
                search_lower = search_input.lower()
                
                # Find matching students (safe field access)
                for student in db:
                    student_id = student.get("student_id") or student.get("id", "")
                    student_name = student.get("name", "")
                    
                    if search_method == "Student ID":
                        if student_id.lower() == search_lower:
                            matches.append(student)
                    else:  # Student Name
                        if search_lower in student_name.lower():
                            matches.append(student)
            
            # Display search results
            if not matches and search_input != "VIEW_ALL":
                st.error(f"❌ No students found matching '{search_input}'")
            else:
                for match in matches:
                    # Safe field access for display
                    match_id = match.get('student_id') or match.get('id', 'Unknown')
                    match_name = match.get('name', 'Unknown')
                    match_image_path = normalize_path(match.get('image_path', ''))
                    
                    with st.expander(f"👤 {match_name} - {match_id}", expanded=True):
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.write("**Student Information:**")
                            st.write(f"🆔 **ID:** {match_id}")
                            st.write(f"👤 **Name:** {match_name}")
                            
                            # Display student photo if exists
                            if match_image_path and os.path.exists(match_image_path):
                                st.image(match_image_path, caption="Student Photo", width=150)
                            else:
                                st.warning("⚠️ Student photo file not found")
                        
                        with col2:
                            st.write("**QR Code Management:**")
                            
                            # Check if QR code exists
                            qr_path = os.path.join(QR_FOLDER, f"{match_id}_qr.png")
                            
                            if os.path.exists(qr_path):
                                st.image(qr_path, caption="Current QR Code", width=200)
                                
                                # Download current QR
                                with open(qr_path, "rb") as f:
                                    qr_bytes = f.read()
                                
                                st.download_button(
                                    "📥 Download Current QR",
                                    data=qr_bytes,
                                    file_name=f"{match_id}_qr.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                            else:
                                st.warning("⚠️ QR Code not found")
                            
                            # Regenerate QR button
                            if st.button(f"🔄 Regenerate QR Code", key=f"regen_{match_id}"):
                                with st.spinner("🔄 Regenerating QR code..."):
                                    new_qr_path, msg = generate_qr_code(match_id, match_name, QR_FOLDER)
                                    if new_qr_path:
                                        st.success(f"✅ QR code regenerated successfully!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {msg}")
                            
                            # Email QR code section
                            if os.path.exists(qr_path):
                                st.markdown("**📧 Email QR Code:**")
                                
                                # Email option checkbox - outside form for real-time updates
                                send_email_option = st.checkbox(
                                    "📨 Send QR code via email",
                                    key=f"send_email_check_{match_id}",
                                    help="Enable to send QR code to student's email"
                                )
                                
                                # Check if student has email on file
                                student_email = match.get('email', '')
                                
                                # Use form only for input and submit
                                with st.form(key=f"email_form_{match_id}"):
                                    # Email input - enable/disable based on checkbox
                                    email_input = st.text_input(
                                        "📧 Email Address:",
                                        value=student_email if student_email else "",
                                        placeholder="student@example.com",
                                        key=f"email_input_{match_id}",
                                        help="Enter email address to send QR code",
                                        disabled=not send_email_option
                                    )
                                    
                                    # Submit button
                                    submit_email = st.form_submit_button(
                                        "📧 Send QR via Email", 
                                        use_container_width=True,
                                        disabled=not send_email_option
                                    )
                                
                                # Handle email sending outside the form
                                if submit_email and send_email_option:
                                    if not email_input or not email_input.strip():
                                        st.error("❌ Please enter an email address")
                                    else:
                                        # Validate email format
                                        import re
                                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                                        if not re.match(email_pattern, email_input.strip()):
                                            st.error("❌ Please enter a valid email address")
                                        else:
                                            # Send email
                                            if is_email_enabled():
                                                with st.spinner("📧 Sending QR code via email..."):
                                                    try:
                                                        success, email_msg = send_qr_email(
                                                            email_input.strip(),
                                                            match_name,
                                                            match_id,
                                                            qr_path
                                                        )
                                                        if success:
                                                            st.success(f"✅ {email_msg}")
                                                        else:
                                                            st.error(f"❌ Email sending failed: {email_msg}")
                                                    except Exception as e:
                                                        st.error(f"❌ Email sending failed: {str(e)}")
                                            else:
                                                st.warning("📧 Email service not configured.")
                                                st.info("💡 Configure Gmail credentials in .env file to enable email functionality")
    
    # Bulk Management Tab
    with tab2:
        st.markdown("### 📦 Bulk QR Code Management")
        st.write("Download multiple QR codes at once or manage in bulk.")
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_students = len(db)
        # Safe field access for student ID
        qr_exists_count = sum(1 for student in db if os.path.exists(os.path.join(QR_FOLDER, f"{student.get('student_id') or student.get('id')}_qr.png")))
        
        with col1:
            st.metric("Total Students", total_students)
        with col2:
            st.metric("QR Codes Available", qr_exists_count)
        with col3:
            st.metric("Missing QR Codes", total_students - qr_exists_count)
        with col4:
            coverage_percent = (qr_exists_count / total_students) * 100 if total_students > 0 else 0
            st.metric("Coverage", f"{coverage_percent:.1f}%")
        
        st.markdown("---")
        
        # Bulk operations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Generate Missing QR Codes")
            
            # Find students without QR codes (safe field access)
            missing_qr_students = []
            for student in db:
                student_id = student.get('student_id') or student.get('id')
                if student_id and not os.path.exists(os.path.join(QR_FOLDER, f"{student_id}_qr.png")):
                    missing_qr_students.append(student)
            
            if missing_qr_students:
                st.write(f"Found {len(missing_qr_students)} students without QR codes:")
                for student in missing_qr_students[:5]:  # Show first 5
                    student_id = student.get('student_id') or student.get('id')
                    student_name = student.get('name', 'Unknown')
                    st.write(f"• {student_name} ({student_id})")
                if len(missing_qr_students) > 5:
                    st.write(f"... and {len(missing_qr_students) - 5} more")
                
                # Generate all missing QR codes button
                if st.button("🚀 Generate All Missing QR Codes", use_container_width=True):
                    with st.spinner("Generating QR codes..."):
                        for student in missing_qr_students:
                            student_id = student.get('student_id') or student.get('id')
                            student_name = student.get('name', 'Unknown')
                            generate_qr_code(student_id, student_name, QR_FOLDER)
                    
                    st.success(f"✅ Generated {len(missing_qr_students)} QR codes!")
                    st.rerun()
            else:
                st.success("✅ All students have QR codes!")
        
        with col2:
            st.markdown("#### 📥 Bulk Download Options")
            
            # Create ZIP package button
            if st.button("📦 Create QR Codes ZIP Package", use_container_width=True):
                import zipfile
                import io
                
                # Create ZIP buffer
                zip_buffer = io.BytesIO()
                
                # Add QR codes to ZIP (safe field access)
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for student in db:
                        student_id = student.get('student_id') or student.get('id')
                        student_name = student.get('name', 'Unknown')
                        if student_id:
                            qr_path = os.path.join(QR_FOLDER, f"{student_id}_qr.png")
                            if os.path.exists(qr_path):
                                zip_file.write(qr_path, f"{student_id}_{student_name}_qr.png")
                
                zip_buffer.seek(0)
                
                # Download button for ZIP
                st.download_button(
                    "📦 Download QR Codes ZIP",
                    data=zip_buffer.getvalue(),
                    file_name="graduation_qr_codes.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                st.success("✅ ZIP package created! Click download button above.")
            
            st.markdown("---")
            st.markdown("#### 📧 Bulk Email Options")
            
            if is_email_enabled():
                # Count students with email addresses
                students_with_email = []
                for student in db:
                    student_email = student.get('email', '')
                    if student_email and student_email.strip():
                        student_id = student.get('student_id') or student.get('id')
                        qr_path = os.path.join(QR_FOLDER, f"{student_id}_qr.png")
                        if os.path.exists(qr_path):
                            students_with_email.append(student)
                
                if students_with_email:
                    st.info(f"📊 Found {len(students_with_email)} students with email addresses and QR codes")
                    
                    if st.button("📧 Send QR Codes to All Students", use_container_width=True):
                        with st.spinner("Sending QR codes via email..."):
                            for student in students_with_email:
                                student_id = student.get('student_id') or student.get('id')
                                student_name = student.get('name', 'Unknown')
                                student_email = student.get('email', '')
                                qr_path = os.path.join(QR_FOLDER, f"{student_id}_qr.png")
                                
                                try:
                                    send_qr_email(student_email, student_name, student_id, qr_path)
                                except Exception:
                                    pass  # Continue with other emails
                        
                        st.success(f"✅ QR codes sent to {len(students_with_email)} students!")
                        st.info("💡 Check individual email inboxes for delivery status")
                        
                else:
                    st.info("📭 No students found with email addresses on file")
                    st.caption("Students need to register with email notifications enabled")
            else:
                st.warning("📧 Email service not configured")
                st.info("💡 Configure Gmail credentials in .env file to enable bulk email functionality")
    
