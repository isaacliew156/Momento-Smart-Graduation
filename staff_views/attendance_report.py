"""
Attendance Report page for the Graduation Attendance System
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


def render_attendance_report():
    """Render the page"""
    
    # Track page visits for navigation state management
    if "last_visited_page" not in st.session_state:
        st.session_state.last_visited_page = None
    
    st.session_state.last_visited_page = "Reports"
    
    st.title("📊 Real-Time Attendance Analytics")
    st.markdown('<p style="color: #2D3436; font-size: 1rem; margin-bottom: 1.5rem;">Comprehensive attendance tracking and analysis</p>', unsafe_allow_html=True)
    
    # Initialize data
    db = load_database()
    attendance_records = load_attendance()
    
    if not db:
        st.warning("📭 No students registered yet.")
        st.stop()
    
    # Simplified tabs - only 2 main tabs
    tab1, tab2 = st.tabs([
        "📊 Dashboard", 
        "📥 Export"
    ])
    
    # Dashboard Tab - Simplified and clean
    with tab1:
        # Get attendance statistics
        analysis = analyze_attendance_data()
        
        if analysis:
            # Simplified metrics - only 3 key cards
            st.markdown("""
            <style>
            .simple-metric-card {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #E8EEF1;
                box-shadow: 0 2px 8px rgba(45, 52, 54, 0.08);
                text-align: center;
                min-height: 100px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .simple-metric-title {
                font-size: 0.9rem;
                color: #636E72;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }
            .simple-metric-value {
                font-size: 2.2rem;
                font-weight: 700;
                color: #2D3436;
                margin-bottom: 0.25rem;
            }
            .simple-metric-subtitle {
                font-size: 0.8rem;
                color: #636E72;
                font-weight: 400;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Only 3 essential metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="simple-metric-card">
                    <div class="simple-metric-title">Total Students</div>
                    <div class="simple-metric-value">{analysis['total_registered']}</div>
                    <div class="simple-metric-subtitle">Registered</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="simple-metric-card">
                    <div class="simple-metric-title">Present Today</div>
                    <div class="simple-metric-value">{analysis['attended_count']}</div>
                    <div class="simple-metric-subtitle">Checked In</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                rate = analysis['attendance_rate']
                st.markdown(f"""
                <div class="simple-metric-card">
                    <div class="simple-metric-title">Attendance Rate</div>
                    <div class="simple-metric-value">{rate:.0f}%</div>
                    <div class="simple-metric-subtitle">Today</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("")  # Small spacing
            
            # Two-column main content layout
            col1, col2 = st.columns([3, 2], gap="medium")
            
            with col1:
                # Student list with search and toggle
                st.markdown("#### 👥 Students")
                
                # Search functionality
                search_term = st.text_input(
                    "🔍 Search students",
                    placeholder="Search by name or ID...",
                    key="student_search",
                    help="Filter students by name or ID"
                )
                
                # Toggle between present and absent
                view_mode = st.radio(
                    "View:",
                    ["✅ Present", "❌ Absent", "📋 All"],
                    horizontal=True,
                    key="view_mode"
                )
                
                # Show filtered student list
                if view_mode == "✅ Present":
                    if analysis['today_attended']:
                        filtered_students = analysis['today_attended']
                        if search_term:
                            search_lower = search_term.lower()
                            filtered_students = [s for s in filtered_students if search_lower in s.get('name', '').lower()]
                        
                        for record in filtered_students[:15]:  # Show up to 15
                            st.success(f"✅ {record.get('name', 'Unknown')} - {record.get('check_in_time', '')}")
                            
                        if len(filtered_students) > 15:
                            st.info(f"... and {len(filtered_students) - 15} more")
                    else:
                        st.info("No students checked in yet")
                
                elif view_mode == "❌ Absent":
                    if analysis['not_attended_names']:
                        filtered_absent = analysis['not_attended_names']
                        if search_term:
                            search_lower = search_term.lower()
                            filtered_absent = [name for name in filtered_absent if search_lower in name.lower()]
                        
                        for name in filtered_absent[:15]:  # Show up to 15
                            st.error(f"❌ {name}")
                            
                        if len(filtered_absent) > 15:
                            st.info(f"... and {len(filtered_absent) - 15} more")
                    else:
                        st.success("All students have checked in!")
                
                else:  # All students
                    all_students = []
                    # Add present students
                    for record in analysis['today_attended']:
                        all_students.append({"name": record.get('name', 'Unknown'), "status": "present", "time": record.get('check_in_time', '')})
                    # Add absent students
                    for name in analysis['not_attended_names']:
                        all_students.append({"name": name, "status": "absent", "time": ""})
                    
                    # Filter by search
                    if search_term:
                        search_lower = search_term.lower()
                        all_students = [s for s in all_students if search_lower in s['name'].lower()]
                    
                    for student in all_students[:15]:
                        if student['status'] == 'present':
                            st.success(f"✅ {student['name']} - {student['time']}")
                        else:
                            st.error(f"❌ {student['name']}")
                    
                    if len(all_students) > 15:
                        st.info(f"... and {len(all_students) - 15} more")
            
            with col2:
                # Simple timeline chart
                st.markdown("#### ⏰ Check-in Timeline")
                
                if analysis['today_attended']:
                    # Group by hour for chart
                    hourly_checkins = defaultdict(int)
                    
                    for record in analysis['today_attended']:
                        check_time = record.get('check_in_time', '')
                        if check_time and ' ' in check_time:
                            hour = check_time.split(' ')[1].split(':')[0]
                            hourly_checkins[f"{hour}:00"] += 1
                    
                    if hourly_checkins:
                        # Create simple bar chart
                        timeline_df = pd.DataFrame(
                            list(hourly_checkins.items()),
                            columns=['Hour', 'Check-ins']
                        ).sort_values('Hour')
                        
                        st.bar_chart(timeline_df.set_index('Hour'), height=250)
                    else:
                        st.info("No time data available")
                        
                    # Quick stats
                    st.write("")
                    st.markdown("**📊 Quick Stats**")
                    st.metric("Total Check-ins", len(analysis['today_attended']))
                    
                    if analysis['today_attended']:
                        latest_checkin = max(analysis['today_attended'], key=lambda x: x.get('check_in_time', ''))
                        st.metric("Latest Check-in", latest_checkin.get('check_in_time', 'N/A').split(' ')[1] if ' ' in latest_checkin.get('check_in_time', '') else 'N/A')
                        
                else:
                    st.info("No check-ins recorded today yet.")
                    st.metric("Total Check-ins", 0)
        else:
            st.warning("No attendance data available.")
    
    # Export Tab - Simplified
    with tab2:
        # Simplified Export Interface
        analysis = analyze_attendance_data()
        
        if analysis:
            # Quick export options
            st.markdown("### 📥 Export Today's Attendance")
            st.info(f"📊 Ready to export: **{analysis['attended_count']}** present, **{analysis['remaining_count']}** absent")
            
            # Export format selection
            col1, col2 = st.columns([1, 1])
            
            with col1:
                export_format = st.selectbox(
                    "📄 Format:",
                    ["CSV", "PDF", "TXT", "JSON"],
                    help="Choose export format"
                )
            
            with col2:
                include_timestamps = st.checkbox(
                    "⏰ Include check-in times",
                    value=True,
                    help="Include detailed check-in timestamps"
                )
            
            st.write("")
            
            # One-click export
            if st.button("📥 Export Today's Data", type="primary", use_container_width=True):
                try:
                    # Generate report data
                    export_data = generate_attendance_report_data()
                    
                    if export_data and export_data.get('attendance_records'):
                        # Prepare export records for all formats
                        export_records = []
                        for record in export_data['attendance_records']:
                            row = {
                                'Student Name': record.get('student_name', ''),
                                'Student ID': record.get('student_id', ''),
                                'Status': record.get('attendance_status', 'Absent')
                            }
                            if include_timestamps and record.get('attendance_status') == 'Present':
                                row['Check-in Time'] = record.get('check_in_time', 'N/A')
                                row['Verification Method'] = record.get('verification_method', 'N/A')
                            
                            export_records.append(row)
                        
                        today = datetime.now().strftime("%Y-%m-%d")
                        
                        if export_format == "CSV":
                            # CSV Export
                            df = pd.DataFrame(export_records)
                            csv_data = df.to_csv(index=False)
                            
                            st.download_button(
                                "📥 Download CSV",
                                data=csv_data,
                                file_name=f"attendance_{today}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        elif export_format == "PDF":
                            # PDF Export with charts and tables
                            try:
                                import matplotlib.pyplot as plt
                                import matplotlib
                                matplotlib.use('Agg')  # Use non-interactive backend
                                from matplotlib.backends.backend_pdf import PdfPages
                                import io
                                
                                # Create PDF in memory
                                pdf_buffer = io.BytesIO()
                                
                                with PdfPages(pdf_buffer) as pdf:
                                    # Page 1: Summary with chart
                                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8))
                                    fig.suptitle(f'Graduation Attendance Report - {today}', fontsize=16, fontweight='bold')
                                    
                                    # Pie chart
                                    present_count = analysis['attended_count']
                                    absent_count = analysis['remaining_count']
                                    
                                    ax1.pie([present_count, absent_count], 
                                           labels=['Present', 'Absent'],
                                           colors=['#00B894', '#E17055'],
                                           autopct='%1.1f%%',
                                           startangle=90)
                                    ax1.set_title('Attendance Overview')
                                    
                                    # Bar chart
                                    categories = ['Total\nRegistered', 'Present', 'Absent']
                                    values = [analysis['total_registered'], present_count, absent_count]
                                    colors = ['#74B9FF', '#00B894', '#E17055']
                                    
                                    ax2.bar(categories, values, color=colors)
                                    ax2.set_title('Attendance Statistics')
                                    ax2.set_ylabel('Number of Students')
                                    
                                    # Add summary text
                                    summary_text = f"""
                                    ATTENDANCE SUMMARY
                                    
                                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                                    
                                    Total Students: {analysis['total_registered']}
                                    Present: {present_count}
                                    Absent: {absent_count}
                                    Attendance Rate: {analysis['attendance_rate']:.1f}%
                                    """
                                    
                                    plt.figtext(0.02, 0.02, summary_text, fontsize=10, verticalalignment='bottom')
                                    plt.tight_layout()
                                    pdf.savefig(fig, bbox_inches='tight')
                                    plt.close(fig)
                                    
                                    # Page 2: Student Lists
                                    fig, ax = plt.subplots(figsize=(8.5, 11))
                                    ax.axis('off')
                                    
                                    present_students = [r for r in export_records if r['Status'] == 'Present']
                                    absent_students = [r for r in export_records if r['Status'] == 'Absent']
                                    
                                    y_pos = 0.95
                                    
                                    # Present students
                                    if present_students:
                                        ax.text(0.05, y_pos, f'PRESENT STUDENTS ({len(present_students)})', 
                                               fontsize=14, fontweight='bold', color='#00B894')
                                        y_pos -= 0.05
                                        ax.text(0.05, y_pos, '-' * 50, fontsize=10)
                                        y_pos -= 0.04
                                        
                                        for student in present_students:
                                            text = f"✓ {student['Student Name']} ({student['Student ID']})"
                                            if include_timestamps and 'Check-in Time' in student:
                                                text += f" - {student['Check-in Time']}"
                                            ax.text(0.05, y_pos, text, fontsize=10)
                                            y_pos -= 0.03
                                            if y_pos < 0.1:
                                                break
                                    
                                    # Absent students
                                    if absent_students and y_pos > 0.3:
                                        y_pos -= 0.05
                                        ax.text(0.05, y_pos, f'ABSENT STUDENTS ({len(absent_students)})', 
                                               fontsize=14, fontweight='bold', color='#E17055')
                                        y_pos -= 0.05
                                        ax.text(0.05, y_pos, '-' * 50, fontsize=10)
                                        y_pos -= 0.04
                                        
                                        for student in absent_students:
                                            if y_pos < 0.1:
                                                break
                                            ax.text(0.05, y_pos, f"✗ {student['Student Name']} ({student['Student ID']})", fontsize=10)
                                            y_pos -= 0.03
                                    
                                    pdf.savefig(fig, bbox_inches='tight')
                                    plt.close(fig)
                                
                                pdf_buffer.seek(0)
                                
                                st.download_button(
                                    "📥 Download PDF Report",
                                    data=pdf_buffer.getvalue(),
                                    file_name=f"attendance_report_{today}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                                
                            except ImportError:
                                # Fallback to text-based PDF if matplotlib not available
                                st.warning("📊 Charts not available. Generating text-based PDF...")
                                pdf_content = f"GRADUATION ATTENDANCE REPORT\n"
                                pdf_content += f"=" * 50 + "\n\n"
                                pdf_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                pdf_content += f"Date: {today}\n\n"
                                
                                pdf_content += f"SUMMARY:\n"
                                pdf_content += f"- Total Students: {analysis['total_registered']}\n"
                                pdf_content += f"- Present: {analysis['attended_count']}\n"
                                pdf_content += f"- Absent: {analysis['remaining_count']}\n"
                                pdf_content += f"- Attendance Rate: {analysis['attendance_rate']:.1f}%\n\n"
                                
                                # Present students
                                present_students = [r for r in export_records if r['Status'] == 'Present']
                                if present_students:
                                    pdf_content += f"PRESENT STUDENTS ({len(present_students)}):\n"
                                    pdf_content += "-" * 30 + "\n"
                                    for student in present_students:
                                        pdf_content += f"• {student['Student Name']} ({student['Student ID']})"
                                        if include_timestamps and 'Check-in Time' in student:
                                            pdf_content += f" - {student['Check-in Time']}"
                                        pdf_content += "\n"
                                    pdf_content += "\n"
                                
                                # Absent students
                                absent_students = [r for r in export_records if r['Status'] == 'Absent']
                                if absent_students:
                                    pdf_content += f"ABSENT STUDENTS ({len(absent_students)}):\n"
                                    pdf_content += "-" * 30 + "\n"
                                    for student in absent_students:
                                        pdf_content += f"• {student['Student Name']} ({student['Student ID']})\n"
                                
                                st.download_button(
                                    "📥 Download PDF Report (Text)",
                                    data=pdf_content,
                                    file_name=f"attendance_report_{today}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                        
                        elif export_format == "TXT":
                            # Simple TXT Export
                            txt_content = f"Attendance Report - {today}\n\n"
                            
                            for record in export_records:
                                status_icon = "✓" if record['Status'] == 'Present' else "✗"
                                txt_content += f"{status_icon} {record['Student Name']} ({record['Student ID']}) - {record['Status']}"
                                if include_timestamps and 'Check-in Time' in record:
                                    txt_content += f" at {record['Check-in Time']}"
                                txt_content += "\n"
                            
                            txt_content += f"\nSummary: {analysis['attended_count']}/{analysis['total_registered']} present ({analysis['attendance_rate']:.1f}%)"
                            
                            st.download_button(
                                "📥 Download TXT",
                                data=txt_content,
                                file_name=f"attendance_{today}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        else:  # JSON
                            # JSON Export
                            json_data = {
                                "report_date": today,
                                "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "summary": {
                                    "total_students": analysis['total_registered'],
                                    "present": analysis['attended_count'],
                                    "absent": analysis['remaining_count'],
                                    "attendance_rate": analysis['attendance_rate']
                                },
                                "students": export_records
                            }
                            
                            json_content = json.dumps(json_data, indent=2, default=str)
                            
                            st.download_button(
                                "📥 Download JSON",
                                data=json_content,
                                file_name=f"attendance_{today}.json",
                                mime="application/json",
                                use_container_width=True
                            )
                        
                        st.success("✅ Export generated successfully!")
                    else:
                        st.warning("No data available for export.")
                        
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
            
            # Additional note
            st.write("")
            st.info("💡 **Tip:** The export includes all registered students with their current attendance status.")
            
        else:
            st.warning("📭 No attendance data available for export.")
    
    # ===========================