import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import collections

# File paths
DB_FILE = 'data/database.json'
ATTENDANCE_FILE = 'data/attendance.json'

def load_database():
    """Load student database from JSON file"""
    if not os.path.exists(DB_FILE):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        with open(DB_FILE, "w") as f:
            json.dump([], f)
        return []
    
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_to_database(entry):
    """Add new student entry to database"""
    db = load_database()
    db.append(entry)
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def load_attendance():
    """Load attendance records"""
    if not os.path.exists(ATTENDANCE_FILE):
        os.makedirs(os.path.dirname(ATTENDANCE_FILE), exist_ok=True)
        return []
    
    try:
        with open(ATTENDANCE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def save_attendance_record(record):
    """Save attendance record with duplicate prevention and numpy type conversion"""
    attendance = load_attendance()
    
    # Check for duplicate within same minute
    student_id = record.get("student_id")
    check_time = record.get("check_in_time", "")
    
    # Prevent duplicate entries within 60 seconds
    if check_time and student_id:
        try:
            current_time = datetime.strptime(check_time, "%Y-%m-%d %H:%M:%S")
            
            for existing in attendance:
                if existing.get("student_id") == student_id:
                    existing_time_str = existing.get("check_in_time", "")
                    if existing_time_str:
                        try:
                            existing_time = datetime.strptime(existing_time_str, "%Y-%m-%d %H:%M:%S")
                            time_diff = abs((current_time - existing_time).total_seconds())
                            
                            # If same student checked in within 60 seconds, skip
                            if time_diff < 60:
                                print(f"Duplicate entry prevented for {student_id} - {time_diff}s apart")
                                return False  # Return False to indicate duplicate
                        except ValueError:
                            continue  # Skip malformed timestamps
        except ValueError:
            pass  # Continue if timestamp format is invalid
    
    # Convert numpy types and save
    clean_record = convert_numpy_types(record)
    attendance.append(clean_record)
    
    with open(ATTENDANCE_FILE, "w") as f:
        json.dump(attendance, f, indent=4)
    
    return True  # Return True to indicate successful save

def check_already_attended(student_id):
    """
    Check if student already attended today
    Returns: (has_attended, existing_record)
    """
    attendance = load_attendance()
    today = datetime.now().strftime("%Y-%m-%d")
    
    for record in attendance:
        record_date = record.get("check_in_time", "").split(" ")[0]
        if record.get("student_id") == student_id and record_date == today:
            return True, record
    
    return False, None

def analyze_attendance_data():
    """Comprehensive attendance analysis"""
    db = load_database()
    attendance = load_attendance()
    
    if not db:
        return None
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Basic stats
    total_registered = len(db)
    today_attended = [r for r in attendance if r.get("check_in_time", "").startswith(today)]
    attended_count = len(today_attended)
    remaining_count = total_registered - attended_count
    attendance_rate = (attended_count / total_registered * 100) if total_registered > 0 else 0
    
    # Build complete student status list
    attended_ids = [r.get("student_id") for r in today_attended]
    student_status_list = []
    
    for student in db:
        student_id = student.get("student_id")
        attendance_record = next((r for r in today_attended if r.get("student_id") == student_id), None)
        
        if attendance_record:
            # Student present
            check_time = attendance_record.get("check_in_time", "")
            
            # Determine verification method
            if "MANUAL" in attendance_record.get("device_id", ""):
                verification_method = "Manual Entry"
            elif attendance_record.get("face_verify_time") == "MANUAL_OVERRIDE":
                verification_method = "Manual Override"
            else:
                verification_method = "Normal Verification"
            
            student_status_list.append({
                "student_id": student_id,
                "name": student.get("name", "Unknown"),
                "status": "Present",
                "check_in_time": check_time,
                "verification_method": verification_method,
                "confidence_score": attendance_record.get("confidence_score", 0),
                "verify_photo": attendance_record.get("verify_photo", ""),
                "image_path": student.get("image_path", ""),
                "device_id": attendance_record.get("device_id", ""),
                "qr_scan_time": attendance_record.get("qr_scan_time", ""),
                "face_verify_time": attendance_record.get("face_verify_time", "")
            })
        else:
            # Student absent
            student_status_list.append({
                "student_id": student_id,
                "name": student.get("name", "Unknown"),
                "status": "Absent",
                "check_in_time": "",
                "verification_method": "",
                "confidence_score": 0,
                "verify_photo": "",
                "image_path": student.get("image_path", ""),
                "device_id": "",
                "qr_scan_time": "",
                "face_verify_time": ""
            })
    
    # Time-based analysis
    hourly_checkins = collections.defaultdict(int)
    verification_methods = collections.defaultdict(int)
    
    for record in today_attended:
        # Hourly distribution
        check_time = record.get("check_in_time", "")
        if check_time and " " in check_time:
            hour = check_time.split(" ")[1].split(":")[0]
            hourly_checkins[hour] += 1
        
        # Verification method distribution
        device = record.get("device_id", "")
        if "MANUAL" in device:
            verification_methods["Manual Entry"] += 1
        elif record.get("face_verify_time") == "MANUAL_OVERRIDE":
            verification_methods["Manual Override"] += 1
        else:
            verification_methods["Normal Verification"] += 1
    
    # Get list of absent student names
    not_attended_names = []
    for student in db:
        if student.get("student_id") not in attended_ids:
            not_attended_names.append(student.get("name", "Unknown"))
    
    return {
        "total_registered": total_registered,
        "attended_count": attended_count,
        "remaining_count": remaining_count,
        "attendance_rate": attendance_rate,
        "student_status_list": student_status_list,
        "hourly_checkins": dict(hourly_checkins),
        "verification_methods": dict(verification_methods),
        "today_attended": today_attended,
        "not_attended_names": not_attended_names
    }

def generate_attendance_report_data(filter_status="All", filter_method="All", search_term=""):
    """Generate filtered attendance report data"""
    analysis = analyze_attendance_data()
    
    if not analysis:
        return None
    
    # Get all student records with attendance status
    all_records = []
    db = load_database()
    attendance = load_attendance()
    today = datetime.now().strftime("%Y-%m-%d")
    today_attended = [r for r in attendance if r.get("check_in_time", "").startswith(today)]
    attended_ids = [r.get("student_id") for r in today_attended]
    
    for student in db:
        student_id = student.get("student_id")
        attendance_record = next((r for r in today_attended if r.get("student_id") == student_id), None)
        
        if attendance_record:
            # Present student
            record = {
                "student_id": student_id,
                "student_name": student.get("name", "Unknown"),
                "attendance_status": "Present",
                "check_in_time": attendance_record.get("check_in_time", ""),
                "verification_method": attendance_record.get("verification_method", "Face Recognition"),
                "confidence_score": attendance_record.get("confidence_score", 0),
                "photo_path": student.get("image_path", "")
            }
        else:
            # Absent student
            record = {
                "student_id": student_id,
                "student_name": student.get("name", "Unknown"),
                "attendance_status": "Absent",
                "check_in_time": "",
                "verification_method": "",
                "confidence_score": 0,
                "photo_path": student.get("image_path", "")
            }
        
        all_records.append(record)
    
    # Apply filters
    filtered_records = all_records
    
    if filter_status != "All":
        filtered_records = [r for r in filtered_records if r["attendance_status"] == filter_status]
    
    if filter_method != "All" and filter_method:
        filtered_records = [r for r in filtered_records if r.get("verification_method") == filter_method]
    
    if search_term:
        search_lower = search_term.lower()
        # Safe field access for search
        filtered_records = [
            r for r in filtered_records 
            if search_lower in r.get("student_name", "").lower() or search_lower in (r.get("student_id") or r.get("id") or "").lower()
        ]
    
    # Calculate summary statistics
    total_students = len(db)
    present_count = len([r for r in all_records if r["attendance_status"] == "Present"])
    absent_count = total_students - present_count
    attendance_percentage = (present_count / total_students * 100) if total_students > 0 else 0
    
    return {
        "attendance_records": filtered_records,
        "summary": {
            "total_students": total_students,
            "present_count": present_count,
            "absent_count": absent_count,
            "attendance_percentage": attendance_percentage,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

def get_student_by_id(student_id):
    """Get student data by ID (safe field access)"""
    db = load_database()
    return next((s for s in db if (s.get("student_id") or s.get("id")) == student_id), None)

def update_student(student_id, updates):
    """Update student data (safe field access)"""
    db = load_database()
    
    for i, student in enumerate(db):
        if (student.get("student_id") or student.get("id")) == student_id:
            db[i].update(updates)
            break
    
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def delete_student(student_id):
    """Delete student from database (safe field access)"""
    db = load_database()
    db = [s for s in db if (s.get("student_id") or s.get("id")) != student_id]
    
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# === ATTENDANCE RECORD DELETION FUNCTIONS ===

def delete_attendance_record(student_id, check_time=None):
    """
    Delete specific attendance record(s) for a student
    Args:
        student_id (str): Student ID to delete records for
        check_time (str, optional): Specific check-in time to delete. If None, deletes all records for student.
    Returns:
        tuple: (success: bool, message: str, deleted_count: int)
    """
    try:
        attendance = load_attendance()
        original_count = len(attendance)
        
        if check_time:
            # Delete specific record
            attendance = [r for r in attendance if not (
                r.get("student_id") == student_id and 
                r.get("check_in_time") == check_time
            )]
        else:
            # Delete all records for this student
            attendance = [r for r in attendance if r.get("student_id") != student_id]
        
        deleted_count = original_count - len(attendance)
        
        if deleted_count > 0:
            with open(ATTENDANCE_FILE, "w") as f:
                json.dump(attendance, f, indent=4)
            return True, f"Successfully deleted {deleted_count} attendance record(s) for {student_id}", deleted_count
        else:
            return False, f"No attendance records found for {student_id}", 0
            
    except Exception as e:
        return False, f"Error deleting attendance record: {str(e)}", 0

def delete_today_attendance():
    """
    Delete all attendance records for today
    Returns:
        tuple: (success: bool, message: str, deleted_count: int)
    """
    try:
        attendance = load_attendance()
        today = datetime.now().strftime("%Y-%m-%d")
        original_count = len(attendance)
        
        # Filter out today's records
        attendance = [r for r in attendance if not r.get("check_in_time", "").startswith(today)]
        
        deleted_count = original_count - len(attendance)
        
        if deleted_count > 0:
            with open(ATTENDANCE_FILE, "w") as f:
                json.dump(attendance, f, indent=4)
            return True, f"Successfully deleted {deleted_count} attendance records for today ({today})", deleted_count
        else:
            return False, f"No attendance records found for today ({today})", 0
            
    except Exception as e:
        return False, f"Error deleting today's attendance: {str(e)}", 0

def clear_all_attendance():
    """
    Clear all attendance records (DANGEROUS OPERATION)
    Returns:
        tuple: (success: bool, message: str, deleted_count: int)
    """
    try:
        attendance = load_attendance()
        deleted_count = len(attendance)
        
        # Clear all records
        with open(ATTENDANCE_FILE, "w") as f:
            json.dump([], f, indent=4)
        
        return True, f"Successfully cleared all {deleted_count} attendance records", deleted_count
        
    except Exception as e:
        return False, f"Error clearing attendance records: {str(e)}", 0

def delete_attendance_batch(record_ids):
    """
    Delete multiple attendance records by their unique identifiers
    Args:
        record_ids (list): List of record identifiers (student_id + check_in_time combinations)
    Returns:
        tuple: (success: bool, message: str, deleted_count: int)
    """
    try:
        attendance = load_attendance()
        original_count = len(attendance)
        
        # Create identifiers for existing records
        filtered_attendance = []
        for record in attendance:
            record_id = f"{record.get('student_id', '')}_{record.get('check_in_time', '')}"
            if record_id not in record_ids:
                filtered_attendance.append(record)
        
        deleted_count = original_count - len(filtered_attendance)
        
        if deleted_count > 0:
            with open(ATTENDANCE_FILE, "w") as f:
                json.dump(filtered_attendance, f, indent=4)
            return True, f"Successfully deleted {deleted_count} attendance records", deleted_count
        else:
            return False, "No matching records found to delete", 0
            
    except Exception as e:
        return False, f"Error deleting batch attendance records: {str(e)}", 0

def backup_attendance(backup_suffix="backup"):
    """
    Create a backup of current attendance data
    Args:
        backup_suffix (str): Suffix for backup filename
    Returns:
        tuple: (success: bool, backup_path: str)
    """
    try:
        import shutil
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"data/attendance_{backup_suffix}_{timestamp}.json"
        
        if os.path.exists(ATTENDANCE_FILE):
            shutil.copy2(ATTENDANCE_FILE, backup_path)
            return True, backup_path
        else:
            return False, "No attendance file to backup"
            
    except Exception as e:
        return False, f"Error creating backup: {str(e)}"

def clear_all_students():
    """
    Clear all student records (DANGEROUS OPERATION)
    Returns:
        tuple: (success: bool, message: str, deleted_count: int)
    """
    try:
        db = load_database()
        deleted_count = len(db)
        
        # Clear all student records
        with open(DB_FILE, "w") as f:
            json.dump([], f, indent=4)
        
        return True, f"Successfully cleared all {deleted_count} student records", deleted_count
        
    except Exception as e:
        return False, f"Error clearing student database: {str(e)}", 0

def delete_student_with_files(student_id):
    """
    Delete student from database and remove associated files
    Args:
        student_id (str): Student ID to delete
    Returns:
        tuple: (success: bool, message: str, files_deleted: list)
    """
    try:
        import shutil
        
        # Get student data before deletion
        student = get_student_by_id(student_id)
        if not student:
            return False, f"Student {student_id} not found", []
        
        files_deleted = []
        
        # Delete student image file
        if student.get('image_path') and os.path.exists(student['image_path']):
            try:
                os.remove(student['image_path'])
                files_deleted.append(student['image_path'])
            except Exception as e:
                print(f"Warning: Could not delete image file: {e}")
        
        # Delete QR code files
        qr_files = [
            f"data/static/{student_id}_qr.png",
            f"data/static/{student_id}_custom_qr.png"
        ]
        
        for qr_file in qr_files:
            if os.path.exists(qr_file):
                try:
                    os.remove(qr_file)
                    files_deleted.append(qr_file)
                except Exception as e:
                    print(f"Warning: Could not delete QR file: {e}")
        
        # Delete capture images
        capture_dir = "data/captures"
        if os.path.exists(capture_dir):
            for filename in os.listdir(capture_dir):
                if filename.startswith(student_id):
                    capture_file = os.path.join(capture_dir, filename)
                    try:
                        os.remove(capture_file)
                        files_deleted.append(capture_file)
                    except Exception as e:
                        print(f"Warning: Could not delete capture file: {e}")
        
        # Delete student from database
        delete_student(student_id)
        
        # Delete attendance records for this student
        delete_attendance_record(student_id)
        
        return True, f"Successfully deleted student {student_id} and {len(files_deleted)} associated files", files_deleted
        
    except Exception as e:
        return False, f"Error deleting student with files: {str(e)}", []


# ==============================
# IC VERIFICATION DATABASE FUNCTIONS
# ==============================

IC_VERIFICATION_LOG = 'data/ic_verification_log.json'

def load_ic_verification_log():
    """Load IC verification log"""
    if not os.path.exists(IC_VERIFICATION_LOG):
        os.makedirs(os.path.dirname(IC_VERIFICATION_LOG), exist_ok=True)
        return []
    
    try:
        with open(IC_VERIFICATION_LOG, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_ic_verification_log(log_entry):
    """Save IC verification attempt to log"""
    log = load_ic_verification_log()
    
    # Add timestamp and convert numpy types
    log_entry['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_entry = convert_numpy_types(log_entry)
    
    log.append(clean_entry)
    
    with open(IC_VERIFICATION_LOG, "w") as f:
        json.dump(log, f, indent=4)

def get_ic_verification_stats():
    """Get IC verification statistics"""
    log = load_ic_verification_log()
    
    if not log:
        return {
            "total_attempts": 0,
            "successful_verifications": 0,
            "successful_matches": 0,
            "success_rate": 0.0,
            "match_rate": 0.0
        }
    
    total_attempts = len(log)
    successful_verifications = len([entry for entry in log if entry.get('ic_verified', False)])
    successful_matches = len([entry for entry in log if entry.get('student_matched', False)])
    
    return {
        "total_attempts": total_attempts,
        "successful_verifications": successful_verifications,
        "successful_matches": successful_matches,
        "success_rate": (successful_verifications / total_attempts * 100) if total_attempts > 0 else 0.0,
        "match_rate": (successful_matches / successful_verifications * 100) if successful_verifications > 0 else 0.0
    }

def get_students_with_face_encodings():
    """Get all students that have face encodings for IC matching"""
    db = load_database()
    return [student for student in db if student.get('encoding')]

def find_similar_students_by_encoding(target_encoding, top_k=5, min_similarity=0.3):
    """
    Find students with similar face encodings (for debugging/analytics)
    Args:
        target_encoding: Base64 encoded face embedding
        top_k: Number of top matches to return
        min_similarity: Minimum similarity threshold
    Returns:
        List of (student, similarity_score) tuples
    """
    try:
        import base64
        import numpy as np
        
        # Decode target encoding
        target_bytes = base64.b64decode(target_encoding)
        target_embedding = np.frombuffer(target_bytes, dtype=np.float32)
        
        # Get all students with encodings
        students_with_encodings = get_students_with_face_encodings()
        similarities = []
        
        for student in students_with_encodings:
            try:
                # Decode student encoding
                stored_bytes = base64.b64decode(student['encoding'])
                stored_embedding = np.frombuffer(stored_bytes, dtype=np.float32)
                
                # Calculate cosine similarity
                cosine_sim = np.dot(target_embedding, stored_embedding) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(stored_embedding)
                )
                
                if cosine_sim >= min_similarity:
                    similarities.append((student, float(cosine_sim)))
                    
            except Exception as e:
                continue  # Skip invalid encodings
        
        # Sort by similarity (highest first) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
        
    except Exception as e:
        print(f"❌ Error finding similar students: {str(e)}")
        return []

def save_attendance_record_with_ic_info(record, ic_verification_info=None):
    """
    Save attendance record with IC verification information
    Extended version of save_attendance_record for IC verification flow
    """
    # Add IC verification info to the record
    if ic_verification_info:
        record['verification_method'] = 'IC Verification'
        record['ic_verification_info'] = convert_numpy_types(ic_verification_info)
    
    # Use existing save_attendance_record function
    return save_attendance_record(record)

def get_ic_verification_history_for_student(student_id, limit=10):
    """Get IC verification history for a specific student"""
    log = load_ic_verification_log()
    student_entries = [
        entry for entry in log 
        if entry.get('matched_student_id') == student_id
    ]
    
    # Sort by timestamp (most recent first)
    student_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return student_entries[:limit]

def clean_old_ic_verification_logs(days_to_keep=30):
    """Clean IC verification logs older than specified days"""
    try:
        log = load_ic_verification_log()
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        filtered_log = []
        for entry in log:
            try:
                entry_date = datetime.strptime(entry.get('timestamp', ''), "%Y-%m-%d %H:%M:%S")
                if entry_date >= cutoff_date:
                    filtered_log.append(entry)
            except ValueError:
                # Keep entries with invalid timestamps
                filtered_log.append(entry)
        
        with open(IC_VERIFICATION_LOG, "w") as f:
            json.dump(filtered_log, f, indent=4)
        
        return len(log) - len(filtered_log)  # Number of entries removed
        
    except Exception as e:
        print(f"❌ Error cleaning IC verification logs: {str(e)}")
        return 0


# ==============================
# DUAL PORTAL DATABASE SCHEMA UPDATES
# ==============================

def update_database_schema_for_dual_portal():
    """
    Update existing student records to support dual portal system
    Adds password_hash, last_login, self_registered fields
    """
    try:
        db = load_database()
        updated_count = 0
        
        for i, student in enumerate(db):
            needs_update = False
            
            # Add password_hash field if not exists (optional for students)
            if 'password_hash' not in student:
                student['password_hash'] = None  # Students can login with just ID initially
                needs_update = True
            
            # Add last_login timestamp
            if 'last_login' not in student:
                student['last_login'] = None
                needs_update = True
            
            # Add self_registered flag
            if 'self_registered' not in student:
                student['self_registered'] = False  # Existing students were staff-registered
                needs_update = True
            
            # Add portal_enabled flag
            if 'portal_enabled' not in student:
                student['portal_enabled'] = True  # Enable portal access by default
                needs_update = True
            
            # Add creation timestamp if not exists
            if 'created_date' not in student:
                student['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                needs_update = True
            
            # Add last_updated timestamp
            if 'last_updated' not in student:
                student['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                needs_update = True
            
            if needs_update:
                db[i] = student
                updated_count += 1
        
        if updated_count > 0:
            # Save updated database
            with open(DB_FILE, "w") as f:
                json.dump(db, f, indent=4)
            
            print(f"✅ Database schema updated! {updated_count} student records updated.")
        else:
            print("ℹ️ Database schema is already up to date.")
        
        return True, f"Schema update completed. {updated_count} records updated."
        
    except Exception as e:
        print(f"❌ Error updating database schema: {str(e)}")
        return False, f"Schema update failed: {str(e)}"

def add_student_password(student_id, password):
    """
    Add or update password for a student (optional feature)
    Args:
        student_id: Student ID
        password: Plain text password (will be hashed)
    Returns:
        (success: bool, message: str)
    """
    try:
        from utils.auth import AuthManager
        
        student = get_student_by_id(student_id)
        if not student:
            return False, f"Student {student_id} not found"
        
        # Hash password
        password_hash = AuthManager.hash_password(password)
        
        # Update student record
        updates = {
            'password_hash': password_hash,
            'password_set_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        update_student(student_id, updates)
        
        return True, f"Password set for student {student_id}"
        
    except Exception as e:
        return False, f"Error setting password: {str(e)}"

def log_student_login(student_id, login_method="portal"):
    """
    Log student login activity
    Args:
        student_id: Student ID
        login_method: Login method (portal, qr_scan, face_verify, etc.)
    """
    try:
        # Update last_login in student record
        updates = {
            'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_login_method': login_method
        }
        
        update_student(student_id, updates)
        
        # Log to separate login log file (optional)
        login_log_file = 'data/student_login_log.json'
        
        login_entry = {
            'student_id': student_id,
            'login_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'login_method': login_method,
            'timestamp': datetime.now().timestamp()
        }
        
        # Load existing log
        if os.path.exists(login_log_file):
            with open(login_log_file, 'r') as f:
                login_log = json.load(f)
        else:
            login_log = []
        
        # Add new entry
        login_log.append(login_entry)
        
        # Keep only last 1000 entries to prevent log from growing too large
        if len(login_log) > 1000:
            login_log = login_log[-1000:]
        
        # Save log
        with open(login_log_file, 'w') as f:
            json.dump(login_log, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"Warning: Could not log student login: {str(e)}")
        return False

def get_student_login_history(student_id, limit=10):
    """
    Get login history for a student
    Args:
        student_id: Student ID
        limit: Number of recent logins to return
    Returns:
        List of login records
    """
    try:
        login_log_file = 'data/student_login_log.json'
        
        if not os.path.exists(login_log_file):
            return []
        
        with open(login_log_file, 'r') as f:
            login_log = json.load(f)
        
        # Filter for this student and sort by timestamp (most recent first)
        student_logins = [
            entry for entry in login_log 
            if entry.get('student_id') == student_id
        ]
        
        student_logins.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return student_logins[:limit]
        
    except Exception as e:
        print(f"Error getting login history: {str(e)}")
        return []

def get_portal_statistics():
    """
    Get statistics about portal usage
    Returns:
        Dictionary with portal usage stats
    """
    try:
        db = load_database()
        
        if not db:
            return {
                'total_students': 0,
                'portal_enabled': 0,
                'has_face_encoding': 0,
                'self_registered': 0,
                'has_password': 0,
                'recent_logins': 0
            }
        
        stats = {
            'total_students': len(db),
            'portal_enabled': len([s for s in db if s.get('portal_enabled', True)]),
            'has_face_encoding': len([s for s in db if s.get('encoding')]),
            'self_registered': len([s for s in db if s.get('self_registered', False)]),
            'has_password': len([s for s in db if s.get('password_hash')]),
            'recent_logins': 0
        }
        
        # Count recent logins (last 24 hours)
        cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours ago
        
        try:
            login_log_file = 'data/student_login_log.json'
            if os.path.exists(login_log_file):
                with open(login_log_file, 'r') as f:
                    login_log = json.load(f)
                
                recent_logins = len([
                    entry for entry in login_log 
                    if entry.get('timestamp', 0) > cutoff_time
                ])
                
                stats['recent_logins'] = recent_logins
        except:
            pass  # Login log may not exist yet
        
        return stats
        
    except Exception as e:
        print(f"Error getting portal statistics: {str(e)}")
        return {}

def enable_disable_student_portal(student_id, enabled=True):
    """
    Enable or disable portal access for a student
    Args:
        student_id: Student ID
        enabled: True to enable, False to disable
    Returns:
        (success: bool, message: str)
    """
    try:
        student = get_student_by_id(student_id)
        if not student:
            return False, f"Student {student_id} not found"
        
        updates = {
            'portal_enabled': enabled,
            'portal_status_changed': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        update_student(student_id, updates)
        
        status_text = "enabled" if enabled else "disabled"
        return True, f"Portal access {status_text} for student {student_id}"
        
    except Exception as e:
        return False, f"Error updating portal access: {str(e)}"

# Auto-update schema on import (if needed)
def auto_update_schema():
    """Automatically update schema if needed"""
    try:
        db = load_database()
        if db and len(db) > 0:
            # Check if schema update is needed
            sample_student = db[0]
            needs_update = (
                'portal_enabled' not in sample_student or
                'last_updated' not in sample_student
            )
            
            if needs_update:
                print("🔄 Auto-updating database schema for dual portal system...")
                success, message = update_database_schema_for_dual_portal()
                if success:
                    print("✅ Schema auto-update completed")
                else:
                    print(f"⚠️ Schema auto-update failed: {message}")
    except Exception as e:
        print(f"Warning: Schema auto-update check failed: {str(e)}")

# Run auto-update when module is imported
# auto_update_schema()  # Uncomment this line to enable auto-update