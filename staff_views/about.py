"""
About & Social Impact page for the Graduation Attendance System
"""
import streamlit as st
# Removed complex clock features

def render_about():
    """Render the about and social impact page"""
    
    # Track page visits for navigation state management
    import streamlit as st
    if "last_visited_page" not in st.session_state:
        st.session_state.last_visited_page = None
    
    st.session_state.last_visited_page = "About"
    # CSS for consistent styling
    st.markdown("""
    <style>
        .header-section { text-align: center; padding: 2.5rem 0; }
        .header-title { font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; }
        .header-subtitle { font-size: 1.1rem; color: #666666; }
        .section-header { font-size: 1.5rem; font-weight: 600; margin-bottom: 1.5rem; }
        .feature-card { 
            text-align: center; 
            padding: 1.5rem; 
            min-height: 200px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            border: 1px solid #e9ecef;
        }
        .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
        .feature-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; }
        .feature-desc { color: #666666; font-size: 1rem; line-height: 1.4; }
        .tech-card { 
            padding: 1.5rem; 
            min-height: 200px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            border: 1px solid #e9ecef;
        }
        .tech-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; }
        .tech-list { color: #666666; line-height: 1.6; font-size: 1rem; }
        .sdg-card { 
            padding: 1.5rem; 
            min-height: 200px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            border: 1px solid #e9ecef;
            text-align: center;
        }
        .sdg-icon { font-size: 2.5rem; margin-bottom: 1rem; }
        .sdg-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; }
        .sdg-desc { color: #666666; font-size: 1rem; line-height: 1.4; }
        .footer { text-align: center; padding: 2.5rem 0; color: #666666; }
        .spacing-section { margin: 2.5rem 0; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    st.markdown("""
    <div class="header-section">
        <h1 class="header-title">About This System</h1>
        <p class="header-subtitle">Learn about our graduation attendance solution</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Core Features Grid
    st.markdown('<h3 class="section-header">Core Features</h3>', unsafe_allow_html=True)
    
    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4, gap="medium")
    
    with feat_col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h4 class="feature-title">AI Recognition</h4>
            <p class="feature-desc">Smart ID card scanning with OCR technology</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">👤</div>
            <h4 class="feature-title">Face Verification</h4>
            <p class="feature-desc">Secure identity confirmation system</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h4 class="feature-title">Live Analytics</h4>
            <p class="feature-desc">Real-time attendance tracking and reports</p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h4 class="feature-title">Fast Processing</h4>
            <p class="feature-desc">Lightning-fast scanning and verification</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="spacing-section"></div>', unsafe_allow_html=True)
    
    # Technology Stack (centered layout)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h3 class="section-header" style="text-align: center;">Technology Stack</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.5rem 0;">
            <div class="tech-item">
                <div class="tech-icon">🐍</div>
                <div class="tech-name">Python & Streamlit</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">👁️</div>
                <div class="tech-name">OpenCV Vision</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">📝</div>
                <div class="tech-name">Tesseract OCR</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">🧠</div>
                <div class="tech-name">Face Recognition</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">📱</div>
                <div class="tech-name">QR Code System</div>
            </div>
            <div class="tech-item">
                <div class="tech-icon">💾</div>
                <div class="tech-name">JSON Database</div>
            </div>
        </div>
        
        <style>
        .tech-item {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            border: 1px solid #E8EEF1;
            box-shadow: 0 2px 8px rgba(45, 52, 54, 0.06);
            transition: all 0.2s ease;
        }
        .tech-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(45, 52, 54, 0.12);
        }
        .tech-icon {
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        .tech-name {
            font-size: 0.9rem;
            color: #2D3436;
            font-weight: 500;
            line-height: 1.3;
        }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="spacing-section"></div>', unsafe_allow_html=True)
    
    # SDG Alignment
    st.markdown('<h3 class="section-header">Impact Areas</h3>', unsafe_allow_html=True)
    
    sdg_col1, sdg_col2, sdg_col3 = st.columns(3, gap="medium")
    
    with sdg_col1:
        st.markdown("""
        <div class="sdg-card">
            <div class="sdg-icon" style="color: #34C759;">📚</div>
            <h4 class="sdg-title">Education</h4>
            <p class="sdg-desc">Streamlining academic ceremonies</p>
        </div>
        """, unsafe_allow_html=True)
    
    with sdg_col2:
        st.markdown("""
        <div class="sdg-card">
            <div class="sdg-icon" style="color: #007AFF;">💡</div>
            <h4 class="sdg-title">Innovation</h4>
            <p class="sdg-desc">Digital transformation technology</p>
        </div>
        """, unsafe_allow_html=True)
    
    with sdg_col3:
        st.markdown("""
        <div class="sdg-card">
            <div class="sdg-icon" style="color: #FF9500;">🤝</div>
            <h4 class="sdg-title">Community</h4>
            <p class="sdg-desc">Collaborative learning project</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="spacing-section"></div>', unsafe_allow_html=True)
    
    # Database Management Section
    st.markdown('<h3 class="section-header">🗃️ Database Management</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666666; text-align: center; margin-bottom: 2rem;">Manage student records and attendance data</p>', unsafe_allow_html=True)
    
    # Import required modules for database operations
    from core.database import load_database, delete_student_with_files, clear_all_students, clear_all_attendance
    import os
    
    # Create three columns for the management functions
    mgmt_col1, mgmt_col2, mgmt_col3 = st.columns(3, gap="medium")
    
    with mgmt_col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            border: 2px solid #ef4444;
            box-shadow: 0 4px 20px rgba(239, 68, 68, 0.1);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #ef4444;">👤</div>
            <h4 style="margin-bottom: 1rem; color: #1e293b; font-weight: 600;">Select Student Delete</h4>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Remove individual student and all related files</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Student selection and deletion
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        db = load_database()
        if db:
            student_options = [f"{s.get('student_id', 'Unknown')} - {s.get('name', 'Unknown')}" for s in db]
            selected_student = st.selectbox(
                "Select Student to Delete:",
                options=student_options,
                key="select_student_delete",
                help="Choose a student to permanently delete"
            )
            
            # Check if we're in confirmation mode
            if "delete_student_id" not in st.session_state:
                st.session_state.delete_student_id = None
                
            if st.session_state.delete_student_id is None:
                # Normal delete button
                if st.button("🗑️ Delete Selected Student", 
                            type="secondary", 
                            use_container_width=True, 
                            key="delete_selected_btn"):
                    if selected_student:
                        student_id = selected_student.split(" - ")[0]
                        st.session_state.delete_student_id = student_id
                        st.rerun()
            else:
                # Show confirmation dialog
                student_id = st.session_state.delete_student_id
                st.warning(f"⚠️ Are you sure you want to delete student {student_id}? This action cannot be undone!")
                
                col_confirm1, col_confirm2 = st.columns(2)
                with col_confirm1:
                    if st.button("✅ Confirm Delete", key="confirm_student_delete", type="primary"):
                        # Perform deletion
                        with st.spinner(f"Deleting student {student_id}..."):
                            success, message, files_deleted = delete_student_with_files(student_id)
                            
                        if success:
                            st.success(f"✅ {message}")
                            if files_deleted:
                                st.info(f"📁 Files removed: {len(files_deleted)}")
                        else:
                            st.error(f"❌ {message}")
                        
                        # Reset state
                        st.session_state.delete_student_id = None
                        st.rerun()
                        
                with col_confirm2:
                    if st.button("❌ Cancel", key="cancel_student_delete"):
                        st.session_state.delete_student_id = None
                        st.rerun()
        else:
            st.info("📭 No students found in database")
    
    with mgmt_col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            border: 2px solid #dc2626;
            box-shadow: 0 4px 20px rgba(220, 38, 38, 0.15);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #dc2626;">👥</div>
            <h4 style="margin-bottom: 1rem; color: #1e293b; font-weight: 600;">Delete All Students</h4>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Clear entire student database</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        # Show current student count
        student_count = len(db) if db else 0
        st.info(f"📊 Current students: {student_count}")
        
        # Check if we're in delete all students confirmation mode
        if "delete_all_students_confirm" not in st.session_state:
            st.session_state.delete_all_students_confirm = False
            
        if not st.session_state.delete_all_students_confirm:
            # Normal delete all button
            if st.button("🗑️ Delete All Students", 
                        type="secondary", 
                        use_container_width=True, 
                        key="delete_all_students_btn",
                        disabled=(student_count == 0)):
                st.session_state.delete_all_students_confirm = True
                st.rerun()
        else:
            # Show confirmation dialog
            st.error(f"⚠️ DANGER: This will permanently delete all {student_count} students! This action cannot be undone!")
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ Yes, Delete All", key="confirm_all_students_delete", type="primary"):
                    # Perform deletion
                    with st.spinner("Deleting all students..."):
                        success, message, deleted_count = clear_all_students()
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
                    
                    # Reset state
                    st.session_state.delete_all_students_confirm = False
                    st.rerun()
                    
            with col_confirm2:
                if st.button("❌ Cancel", key="cancel_all_students_delete"):
                    st.session_state.delete_all_students_confirm = False
                    st.rerun()
    
    with mgmt_col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            border: 2px solid #f59e0b;
            box-shadow: 0 4px 20px rgba(245, 158, 11, 0.15);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 1rem; color: #f59e0b;">📋</div>
            <h4 style="margin-bottom: 1rem; color: #1e293b; font-weight: 600;">Delete All Attendance</h4>
            <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Clear all attendance records</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        # Show current attendance count
        from core.database import load_attendance
        attendance_records = load_attendance()
        attendance_count = len(attendance_records) if attendance_records else 0
        st.info(f"📊 Current records: {attendance_count}")
        
        # Check if we're in delete all attendance confirmation mode
        if "delete_all_attendance_confirm" not in st.session_state:
            st.session_state.delete_all_attendance_confirm = False
            
        if not st.session_state.delete_all_attendance_confirm:
            # Normal delete all attendance button
            if st.button("🗑️ Delete All Attendance", 
                        type="secondary", 
                        use_container_width=True, 
                        key="delete_all_attendance_btn",
                        disabled=(attendance_count == 0)):
                st.session_state.delete_all_attendance_confirm = True
                st.rerun()
        else:
            # Show confirmation dialog
            st.warning(f"⚠️ This will permanently delete all {attendance_count} attendance records! This action cannot be undone!")
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ Confirm Delete", key="confirm_all_attendance_delete", type="primary"):
                    # Perform deletion
                    with st.spinner("Deleting all attendance records..."):
                        success, message, deleted_count = clear_all_attendance()
                    
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                    
                    # Reset state
                    st.session_state.delete_all_attendance_confirm = False
                    st.rerun()
                    
            with col_confirm2:
                if st.button("❌ Cancel", key="cancel_all_attendance_delete"):
                    st.session_state.delete_all_attendance_confirm = False
                    st.rerun()
    
    st.markdown('<div class="spacing-section"></div>', unsafe_allow_html=True)
    
