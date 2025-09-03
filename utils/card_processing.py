"""
Card processing functions for the Graduation Attendance System
Handles OCR, face extraction, and image processing
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import os
import json
import re
from datetime import datetime
from core.tesseract_ocr import TesseractOCR
from core.face_module import validate_image, generate_face_encoding, verify_face_encoding
# Interactive cropping removed for simplified deployment
from core.error_handler import error_handler, log_activity
from utils.config import normalize_path, UPLOAD_FOLDER, CAPTURES_FOLDER
from utils.loading_animations import show_ocr_processing_animation, create_simple_spinner, ocr_loader

def create_card_positioning_guide():
    """
    Create a visual guide for student card positioning
    Returns: numpy array representing the guide image
    """
    # Create white background canvas
    guide_width, guide_height = 600, 400
    img = np.ones((guide_height, guide_width, 3), dtype=np.uint8) * 255
    
    # Calculate card dimensions based on standard ID card ratio
    card_width = int(guide_width * 0.44)
    card_height = int(card_width * 54 / 85.6)
    
    # Center the card outline
    card_x = (guide_width - card_width) // 2
    card_y = (guide_height - card_height) // 2
    
    # Define face region (left 40% of card)
    face_width = int(card_width * 0.4)
    
    # Draw main card outline (green)
    cv2.rectangle(img, (card_x, card_y), 
                  (card_x + card_width, card_y + card_height), 
                  (34, 139, 34), 3)
    
    # Draw face region (blue)
    cv2.rectangle(img, (card_x, card_y), 
                  (card_x + face_width, card_y + card_height),
                  (30, 144, 255), 2)
    
    # Draw text region (orange)
    cv2.rectangle(img, (card_x + face_width, card_y), 
                  (card_x + card_width, card_y + card_height),
                  (255, 165, 0), 2)
    
    # Add labels
    cv2.putText(img, "FACE", (card_x + 10, card_y + 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 144, 255), 2)
    cv2.putText(img, "TEXT", (card_x + face_width + 10, card_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
    
    # Add instructions
    cv2.putText(img, "Position your student card within the green outline", 
                (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 60), 2)
    
    return img

def capture_card_with_guide():
    """Simple, working card capture with visual guide - supports both camera and upload"""
    
    st.markdown("### 📸 Student Card Scanner")
    
    # Mobile-friendly input method selection
    input_method = st.radio(
        "📱 Choose Input Method:",
        ["📸 Take Photo with Camera", "📁 Upload Image File"],
        horizontal=True,
        help="Select how to provide your student card image (mobile-friendly)",
        key="card_input_method"
    )
    
    if input_method == "📸 Take Photo with Camera":
        # Show clear instructions with example
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info("""
            **Position your card:**
            - Fill the camera frame with your card
            - Keep card straight and flat
            - Ensure good lighting
            - All text must be visible
            """)
            
            # Create a simple reference image
            reference_img = Image.new('RGB', (300, 200), 'white')
            draw = ImageDraw.Draw(reference_img)
            draw.rectangle([20, 20, 280, 180], outline='green', width=3)
            try:
                # Try to load a font, fallback to default if not available
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position for center alignment
            text1 = "STUDENT CARD HERE"
            text2 = "Fill this area"
            
            # Get text bounding boxes for centering
            bbox1 = draw.textbbox((0, 0), text1, font=font)
            bbox2 = draw.textbbox((0, 0), text2, font=font)
            text1_width = bbox1[2] - bbox1[0]
            text2_width = bbox2[2] - bbox2[0]
            
            draw.text((150 - text1_width//2, 90), text1, fill='black', font=font)
            draw.text((150 - text2_width//2, 120), text2, fill='gray', font=font)
            st.image(reference_img, caption="Position guide")
        
        with col2:
            # Simple camera input
            captured_photo = st.camera_input("📷 Take Photo", key="card_capture_simple")
            
            if captured_photo:
                # Direct conversion - no multiple formats!
                image = Image.open(captured_photo)
                return process_for_ocr(image)
    
    else:  # Upload Image File method
        st.markdown("#### 📁 Upload Student Card Image")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info("""
            **Upload requirements:**
            - Clear photo of student card
            - All text clearly visible
            - JPG, PNG, or JPEG format
            - Good lighting and focus
            """)
            
            uploaded_file = st.file_uploader(
                "Choose your student card image",
                type=['jpg', 'jpeg', 'png'],
                help="Upload a clear photo of your student card",
                key="card_upload_simple"
            )
        
        with col2:
            if uploaded_file is not None:
                # Display uploaded image with correct orientation
                image = Image.open(uploaded_file)
                image = fix_image_orientation(image)  # Fix orientation before display
                st.image(image, caption="📷 Uploaded Student Card", use_container_width=True)
                
                # Process button - store in session state and rerun
                if st.button("✅ Use This Image", type="primary", use_container_width=True):
                    processed_image = process_for_ocr(image)
                    # Store in session state for persistence
                    st.session_state.capture_state['uploaded_processed_image'] = processed_image
                    st.session_state.capture_state['upload_ready'] = True
                    st.rerun()
                
                # Show preview quality check
                st.caption("Please ensure all text is clearly visible before proceeding")
    
    # Check if we have a processed uploaded image ready
    if (st.session_state.capture_state.get('upload_ready') and 
        st.session_state.capture_state.get('uploaded_processed_image') is not None):
        # Return the stored processed image without clearing the flag
        # The flag will be cleared when user clicks "Clear and Start Over"
        processed = st.session_state.capture_state['uploaded_processed_image']
        return processed
    
    return None

def fix_image_orientation(image):
    """Fix image orientation based on EXIF data"""
    try:
        # Check if image has EXIF data
        if hasattr(image, '_getexif') and image._getexif() is not None:
            exif = dict(image._getexif().items())
            
            # Orientation tag
            orientation_key = 274  # Standard EXIF orientation tag
            
            if orientation_key in exif:
                orientation = exif[orientation_key]
                
                # Apply appropriate rotation based on orientation value
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # If no EXIF data or error, just return original image
        pass
    
    return image

def process_for_ocr(image, show_preview=False):
    """Optimized preprocessing for Tesseract OCR"""
    
    # Fix orientation first
    image = fix_image_orientation(image)
    
    # Convert ONCE to numpy array
    img_array = np.array(image)
    
    # If RGBA, convert to RGB
    if img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]
    
    # Auto-crop to remove borders (simple center crop)
    height, width = img_array.shape[:2]
    crop_margin = 0.05  # 5% margin
    
    y1 = int(height * crop_margin)
    y2 = int(height * (1 - crop_margin))
    x1 = int(width * crop_margin)
    x2 = int(width * (1 - crop_margin))
    
    cropped = img_array[y1:y2, x1:x2]
    
    # Only display preview if explicitly requested
    if show_preview:
        # Basic quality check
        mean_brightness = img_array.mean()
        if mean_brightness < 50:
            st.warning("⚠️ Image too dark, retaking recommended")
        elif mean_brightness > 200:
            st.warning("⚠️ Image too bright, retaking recommended")
        
        # Display what we're processing
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="Original capture", use_column_width=True)
        with col2:
            st.image(cropped, caption="Processed for OCR", use_column_width=True)
    
    return cropped

def extract_student_info_optimized(image_array, debug=True, use_stable_ocr=True):
    """
    Enhanced Tesseract extraction for TARUMT student cards with OCR error correction
    Now with stable OCR option for consistent results
    Expects numpy array from process_for_ocr()
    """
    
    # Try stable OCR first if enabled
    if use_stable_ocr:
        try:
            from core.stable_ocr import StableOCR
            stable_ocr = StableOCR()
            
            print("🔬 Using Stable OCR for consistent extraction...")
            
            # Try stable extraction with retry
            result = stable_ocr.extract_with_retry(image_array, max_retries=2)
            
            if result.get('success'):
                print(f"✅ Stable OCR successful! Confidence: {result.get('confidence', 0):.1%}")
                print(f"   Attempts: {result.get('attempts', 1)}, Retries: {result.get('retries', 0)}")
                
                # Add debug info
                if debug and result.get('vote_confidence'):
                    print(f"   Vote confidence: {result['vote_confidence']:.1%}")
                
                return result
            else:
                print(f"⚠️ Stable OCR failed, falling back to standard extraction...")
                print(f"   Error: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"⚠️ Stable OCR not available: {e}")
            print("   Falling back to standard extraction...")
    
    def fix_ocr_errors(text):
        """Fix common OCR mistakes for TARUMT student IDs with intelligent redundancy removal"""
        if not text:
            return text
            
        # Try multiple approaches for different OCR error patterns
        candidates = []
        
        # Approach 1: Handle extra character cases (e.g., 24WMRO12345 → 24WMR12345)
        # Support all years 21-25 and expanded department codes
        if text[:2] in ['21', '22', '23', '24', '25'] and len(text) == 11:
            # Expanded department codes list
            valid_dept_codes = ['WMR', 'WMD', 'WMT', 'WMS', 'WMA', 'WMB', 'WMC', 'WME', 'WMF', 'WMG']
            # Common pattern: extra O/0 after department code
            if text[2:5] in valid_dept_codes or text[2:6] in ['WMRO', 'WMDO', 'WMTO', 'WMSO']:
                # Handle 3-letter dept codes + extra O (e.g., WMRO -> WMR)
                if text[2:5] in valid_dept_codes and text[5] in ['O', '0'] and text[6:].replace('O', '0').isdigit():
                    # Remove the redundant character at position 5
                    candidate = text[:5] + text[6:]  # Skip position 5
                    candidate = candidate.replace('O', '0')  # Fix remaining O→0
                    if len(candidate) == 10:
                        candidates.append(candidate)
                # Handle case where OCR reads dept code + O as single unit
                elif text[2:6] in ['WMRO', 'WMDO', 'WMTO', 'WMSO']:
                    candidate = text[:2] + 'W' + text[3:5] + text[6:]  # Remove O from middle
                    candidate = candidate.replace('O', '0')  # Fix remaining O→0
                    if len(candidate) == 10:
                        candidates.append(candidate)
        
        # Approach 2: Standard character-by-character fixes (support all years 21-25)
        if text[:2] in ['21', '22', '23', '24', '25'] and len(text) >= 8:
            fixed = text
            
            # Truncate if longer than 11
            if len(fixed) > 11:
                fixed = fixed[:11]
            
            # Fix common OCR errors position by position
            # Positions 2-4: should be letters (WMR, WMD, etc.)
            for i in range(2, min(5, len(fixed))):
                char = fixed[i]
                if char.isdigit():
                    # Convert digits to letters in letter positions
                    replacements = {'0': 'O', '1': 'I', '5': 'S', '8': 'B'}
                    fixed = fixed[:i] + replacements.get(char, char) + fixed[i+1:]
            
            # Positions 5+: should be digits
            for i in range(5, len(fixed)):
                char = fixed[i]
                if char.isalpha():
                    # Convert letters to digits in digit positions
                    replacements = {'O': '0', 'I': '1', 'L': '1', 'S': '5', 'B': '8'}
                    fixed = fixed[:i] + replacements.get(char, char) + fixed[i+1:]
            
            # Add as candidate if valid (support all years 21-25)
            if (len(fixed) in [10, 11] and 
                fixed[:2] in ['21', '22', '23', '24', '25'] and 
                len(fixed) >= 5 and fixed[2:5].isalpha() and 
                len(fixed) >= 6 and fixed[5:].isdigit()):
                candidates.append(fixed)
        
        # Approach 3: Padding for short IDs (support all years 21-25)
        if len(text) < 11 and len(text) >= 8:
            if text[:2] in ['21', '22', '23', '24', '25'] and len(text) == 10:
                # Try direct O→0 conversion first
                potential = text.replace('O', '0')
                if (potential[:2] in ['21', '22', '23', '24', '25'] and 
                    potential[2:5].isalpha() and 
                    potential[5:].isdigit()):
                    candidates.append(potential)
        
        # Select best candidate (prefer 10-character IDs over 11-character)
        if candidates:
            # Sort by length (prefer 10) then by format
            candidates = list(set(candidates))  # Remove duplicates
            candidates.sort(key=lambda x: (len(x), x))  # Prefer shorter, then alphabetical
            
            # Return the best candidate
            best = candidates[0]
            if debug:
                st.text(f"🔧 OCR correction: {text} → {best} (selected from {len(candidates)} candidates)")
            return best
        
        # If no good candidates, return original with basic O→0 fix
        basic_fix = text.replace('O', '0')
        return basic_fix
    
    def extract_name_from_text(text):
        """Extract student name from OCR text with improved filtering and frequency analysis"""
        lines = text.split('\n')
        name_candidates = []
        
        # Expanded list of words to exclude (institutional terms, common OCR noise)
        exclude_words = {
            'TARUMT', 'TUNKU', 'ABDUL', 'RAHMAN', 'UNIVERSITY', 'MALAYSIA',
            'MANAGEMENT', 'TECHNOLOGY', 'STUDENT', 'CARD', 'ID', 'NAME',
            'EXPIRY', 'DATE', 'COLLEGE', 'FACULTY', 'DEPARTMENT', 'SCHOOL',
            'SEROMA', 'CY', 'GTARUMT', 'SM', 'NOY', 'ANNNCEMENT', 'RAE',
            'IM', 'NE', 'TO', 'UL', 'AN', 'AMMA', 'WIE', 'PP', 'NT', 'ATTN',
            'TAR', 'RUT', 'RUM', 'AND', 'GYD', 'CE', 'UO', 'NUOUGU', 'UT', 'TOON',
            'PAY', 'PEKAT', 'LAE', 'APEA', 'SCT', 'SEE', 'TARRUMAT'
        }
        
        # Count frequency of potential names
        name_frequency = {}
        
        for line in lines:
            # Clean the line: remove non-letter characters except spaces
            cleaned = re.sub(r'[^A-Za-z\s]', '', line).strip()
            if not cleaned:
                continue
                
            # Split into words
            words = cleaned.split()
            
            # Filter out institutional words and keep only potential name words
            filtered_words = []
            for word in words:
                word_upper = word.upper()
                # Skip institutional words and very short/long words
                if (word_upper not in exclude_words and 
                    2 <= len(word) <= 15 and 
                    word.isalpha()):  # Must be all letters
                    filtered_words.append(word_upper)
            
            # Names typically have 2-3 words (first, middle, last)
            if 2 <= len(filtered_words) <= 3:
                candidate_name = ' '.join(filtered_words)
                
                # Additional validation for reasonable name patterns
                total_chars = len(candidate_name.replace(' ', ''))
                if 6 <= total_chars <= 30:  # Reasonable name length
                    # Count frequency
                    if candidate_name not in name_frequency:
                        name_frequency[candidate_name] = 0
                    name_frequency[candidate_name] += 1
                    
                    # Score the candidate based on name-like characteristics
                    score = 0
                    
                    # Prefer 2-3 word names
                    if len(filtered_words) in [2, 3]:
                        score += 10
                    
                    # Prefer names with typical lengths
                    if 8 <= total_chars <= 20:
                        score += 5
                    
                    # Strong bonus for 3-word names (typical Malaysian format)
                    if len(filtered_words) == 3:
                        score += 5
                    
                    # Penalize if it contains suspected institutional fragments
                    suspicious_fragments = ['MANAGEMENT', 'TECHNOLOGY', 'SEROMA', 'GTARUMT']
                    if any(fragment in candidate_name for fragment in suspicious_fragments):
                        score -= 30
                    
                    # Bonus for common name patterns
                    common_patterns = ['LIEW', 'TAN', 'LIM', 'WONG', 'LEE', 'ONG', 'TEO', 'NG']
                    if any(pattern in candidate_name for pattern in common_patterns):
                        score += 15
                    
                    name_candidates.append((candidate_name, score))
        
        # Apply frequency bonus and debug output
        if debug:
            st.text("🔍 Name analysis:")
            for name, freq in name_frequency.items():
                st.text(f"  '{name}' appears {freq} times")
        
        # Adjust scores based on frequency
        frequency_adjusted_candidates = []
        for name, base_score in name_candidates:
            freq = name_frequency.get(name, 1)
            
            # Major bonus for names that appear multiple times
            frequency_bonus = (freq - 1) * 20  # Big bonus for repeated names
            final_score = base_score + frequency_bonus
            
            frequency_adjusted_candidates.append((name, final_score, freq))
            if debug:
                st.text(f"  '{name}': base_score={base_score}, freq={freq}, final_score={final_score}")
        
        # Sort by final score and return the best candidate
        if frequency_adjusted_candidates:
            # Sort by score (descending), then by frequency (descending), then by length (ascending)
            frequency_adjusted_candidates.sort(key=lambda x: (-x[1], -x[2], len(x[0])))
            best_name = frequency_adjusted_candidates[0][0]
            if debug:
                st.text(f"🎯 Selected name: '{best_name}' (score: {frequency_adjusted_candidates[0][1]})")
            return best_name
        
        return None
    
    # Convert to grayscale if needed
    if len(image_array.shape) == 3:
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_array
    
    # Enhanced preprocessing for better OCR
    height = gray.shape[0]
    if height < 800:
        scale = 1000 / height
        width = int(gray.shape[1] * scale)
        gray = cv2.resize(gray, (width, 1000), interpolation=cv2.INTER_CUBIC)
    
    # Multiple denoising approaches
    denoised = cv2.fastNlMeansDenoising(gray, h=8)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    
    # Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Add border
    bordered = cv2.copyMakeBorder(
        cleaned, 20, 20, 20, 20,
        cv2.BORDER_CONSTANT,
        value=255
    )
    
    # Multiple OCR attempts with different configurations
    import pytesseract
    configs = [
        r'--oem 3 --psm 6',  # Uniform block of text
        r'--oem 3 --psm 11', # Sparse text
        r'--oem 3 --psm 12', # Sparse text OSD
    ]
    
    all_texts = []
    for config in configs:
        try:
            text = pytesseract.image_to_string(bordered, config=config)
            if text.strip():
                all_texts.append(text.strip())
        except:
            continue
    
    # Combine all texts for analysis
    combined_text = '\n'.join(all_texts)
    
    if debug:
        st.text("🔍 Raw OCR Results:")
        st.code(combined_text)
    
    # Try to find student ID with flexible pattern matching
    import re
    student_id = None
    
    # Enhanced ID finding with more flexible patterns
    potential_ids = []
    
    # Pattern 1: Standard 11-character sequences
    potential_ids.extend(re.findall(r'[0-9A-Z]{11}', combined_text.upper()))
    potential_ids.extend(re.findall(r'24[0-9A-Z]{9}', combined_text.upper()))
    
    # Pattern 2: Flexible TARUMT pattern (24 W M R O/0 digits)
    # Allow spaces and common OCR mistakes
    flexible_patterns = [
        r'24\s*W\s*M\s*R\s*[O0]\s*\d{5}',  # Standard WMR format
        r'24\s*W\s*M\s*[DO]\s*[O0]\s*\d{5}',  # WMD format (D->M mistake)
        r'24\s*W\s*[MN]\s*R\s*[O0]\s*\d{5}',  # M->N mistake
    ]
    
    for pattern in flexible_patterns:
        matches = re.finditer(pattern, combined_text.upper())
        for match in matches:
            # Clean the match by removing spaces and normalizing
            cleaned = re.sub(r'\s+', '', match.group())
            if len(cleaned) >= 10:  # Must have at least the basic structure
                potential_ids.append(cleaned[:11] if len(cleaned) >= 11 else cleaned)
    
    # Pattern 3: Split by spaces and look for parts
    words = combined_text.upper().replace('\n', ' ').split()
    for i, word in enumerate(words):
        if word.startswith('24') and len(word) >= 8:
            # Look for next few words that might be part of the ID
            candidate = word
            for j in range(i+1, min(i+3, len(words))):
                next_word = re.sub(r'[^A-Z0-9]', '', words[j])
                if len(next_word) > 0 and len(candidate + next_word) <= 11:
                    candidate += next_word
                if len(candidate) >= 11:
                    break
            if len(candidate) >= 10:
                potential_ids.append(candidate[:11] if len(candidate) >= 11 else candidate)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ids = []
    for pid in potential_ids:
        if pid not in seen:
            seen.add(pid)
            unique_ids.append(pid)
    
    if debug:
        st.text(f"🔍 Potential IDs found: {unique_ids}")
    
    # Try to fix each potential ID
    for potential_id in unique_ids:
        if debug:
            st.text(f"🔧 Testing candidate: {potential_id}")
        fixed_id = fix_ocr_errors(potential_id)
        if debug:
            st.text(f"🔧 After fixing: {potential_id} → {fixed_id}")
        
        # Validate fixed ID format (allow both 10 and 11 character IDs)
        if (fixed_id and len(fixed_id) in [10, 11] and 
            fixed_id[:2] == '24' and 
            len(fixed_id) >= 5 and fixed_id[2:5].isalpha() and 
            len(fixed_id) >= 6 and fixed_id[5:].isdigit()):
            student_id = fixed_id
            if debug:
                st.text(f"✅ Valid ID confirmed: {fixed_id}")
            break
        else:
            if debug:
                st.text(f"❌ Invalid format: {fixed_id}")
    
    if not student_id:
        if debug:
            st.text("🔍 No valid ID found, trying direct text search...")
        # Last resort: direct search for known patterns
        direct_patterns = [
            r'24WMR[O0]\d{4}',  # Standard WMR with O/0 confusion
            r'24WM[RD][O0]\d{4}',  # WMR or WMD with O/0 confusion
            r'24[A-Z]{3}[O0]\d{4}',  # Any 3 letters with O/0 confusion
        ]
        
        for pattern in direct_patterns:
            direct_matches = re.findall(pattern, combined_text.upper())
            for match in direct_matches:
                # Fix common OCR errors
                fixed = match.replace('O', '0')  # Fix O->0
                if len(fixed) in [10, 11]:
                    # Validate the fixed ID  
                    if (fixed[:2] == '24' and 
                        len(fixed) >= 5 and fixed[2:5].isalpha() and 
                        len(fixed) >= 6 and fixed[5:].isdigit()):
                        student_id = fixed
                        if debug:
                            st.text(f"✅ Found via direct search: {match} → {fixed}")
                        break
            if student_id:
                break
    
    # Extract name
    extracted_name = extract_name_from_text(combined_text)
    
    # Prepare results
    if student_id:
        if debug:
            st.success(f"✅ Found Student ID: {student_id}")
            if extracted_name:
                st.success(f"✅ Found Name: {extracted_name}")
            else:
                st.warning("⚠️ Could not extract name clearly")
        
        return {
            'success': True,
            'student_id': student_id,
            'name': extracted_name,
            'raw_text': combined_text,
            'confidence': 0.9 if extracted_name else 0.7
        }
    else:
        if debug:
            st.error("❌ Could not find student ID in expected format")
            st.text("Extracted text:")
            st.code(combined_text)
        
        # Still try to extract name even if ID failed
        if extracted_name and debug:
            st.info(f"ℹ️ Found possible name: {extracted_name}")
        
        return {
            'success': False,
            'student_id': None,
            'name': extracted_name,
            'raw_text': combined_text,
            'confidence': 0.0
        }

def extract_face_from_card(image_array, debug=False):
    """
    Extract face region from student card image using OpenCV face detection and generate face encoding
    """
    try:
        # Convert to OpenCV format if needed
        if len(image_array.shape) == 3:
            card_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            card_image = image_array
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(card_image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Load face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        if face_cascade.empty():
            return {
                'success': False,
                'message': 'Face detector not loaded properly',
                'face_encoding': None,
                'face_image': None
            }
        
        # Detect faces with multiple scale factors for better coverage
        scales = [1.05, 1.1, 1.2, 1.3]  # Try different scale factors
        min_neighbors = [3, 4, 5]  # Try different neighbor thresholds
        
        faces = []
        for scale in scales:
            for neighbors in min_neighbors:
                detected = face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=scale, 
                    minNeighbors=neighbors,
                    minSize=(30, 30),  # Minimum face size
                    maxSize=(int(width*0.8), int(height*0.8))  # Maximum face size
                )
                if len(detected) > 0:
                    faces.extend(detected)
                    break
            if len(faces) > 0:
                break
        
        if debug:
            st.text(f"🔍 Face detection: Found {len(faces)} faces")
        
        if len(faces) == 0:
            # Fallback to region-based extraction for student cards
            if debug:
                st.text("👤 No face detected, trying region-based extraction...")
            return extract_face_from_card_region_fallback(card_image, debug=debug)
        
        # If multiple faces, select the largest one (likely the main student photo)
        if len(faces) > 1:
            areas = [(w * h, i) for i, (x, y, w, h) in enumerate(faces)]
            areas.sort(reverse=True)
            face_idx = areas[0][1]
            if debug:
                st.text(f"👤 Multiple faces detected, using largest one")
        else:
            face_idx = 0
        
        # Extract the selected face
        (x, y, w, h) = faces[face_idx]
        if debug:
            st.text(f"👤 Face region: ({x}, {y}, {w}, {h})")
        
        # Add some padding around the face
        padding = 20
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(width, x + w + padding)
        y2 = min(height, y + h + padding)
        
        # Extract face region
        face_region = card_image[y1:y2, x1:x2]
        
        # Convert back to RGB for face recognition
        face_rgb = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
        face_pil = Image.fromarray(face_rgb)
        
        # Generate face encoding using existing function
        from core.face_module import generate_face_encoding
        face_encoding, face_msg = generate_face_encoding(face_pil)
        
        if face_encoding is not None:
            return {
                'success': True,
                'message': f'Face detected and encoded successfully (size: {w}x{h})',
                'face_encoding': face_encoding,
                'face_image': face_pil
            }
        else:
            return {
                'success': False,
                'message': f'Face detected but encoding failed: {face_msg}',
                'face_encoding': None,
                'face_image': face_pil  # Still return image for display
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Face extraction error: {str(e)}',
            'face_encoding': None,
            'face_image': None
        }

def extract_face_from_card_region_fallback(card_image, debug=False):
    """
    Fallback method: Extract face using fixed region estimation for student cards
    """
    try:
        height, width = card_image.shape[:2]
        
        # Try multiple regions for better coverage
        regions_to_try = [
            # Region 1: Left side (standard student card layout)
            (0, 0, int(width * 0.4), int(height * 0.7)),
            # Region 2: Upper left quadrant  
            (0, 0, int(width * 0.5), int(height * 0.5)),
            # Region 3: Left half
            (0, 0, int(width * 0.5), height)
        ]
        
        if debug:
            st.text("🔍 Trying region-based face extraction...")
        
        for i, (x1, y1, x2, y2) in enumerate(regions_to_try):
            if debug:
                st.text(f"   Trying region {i+1}: ({x1}, {y1}) to ({x2}, {y2})")
            
            # Extract region
            face_region = card_image[y1:y2, x1:x2]
            
            # Convert to RGB for face recognition
            face_rgb = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            
            # Try face encoding
            from core.face_module import generate_face_encoding
            face_encoding, face_msg = generate_face_encoding(face_pil)
            
            if face_encoding is not None:
                return {
                    'success': True,
                    'message': f'Face extracted from region {i+1} (fallback method)',
                    'face_encoding': face_encoding,
                    'face_image': face_pil
                }
        
        # All regions failed
        return {
            'success': False,
            'message': 'No face detected in any region. Consider taking a separate face photo.',
            'face_encoding': None,
            'face_image': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Region fallback error: {str(e)}',
            'face_encoding': None,
            'face_image': None
        }

def process_ai_scanned_card(photo, manual_crop_region=None, processing_mode="auto"):
    """
    Process the student card photo captured by AI scan
    Args:
        photo: Streamlit camera_input photo object
        manual_crop_region: PIL Image of manually cropped text region (optional)
        processing_mode: "auto" or "manual" processing mode
    Returns:
        dict: Processing results including OCR and face encoding
    """
    try:
        # Convert photo to OpenCV format
        # Reset seek position if BytesIO
        if hasattr(photo, 'seek'):
            photo.seek(0)
        pil_image = Image.open(photo)
        pil_image = fix_image_orientation(pil_image)  # Fix orientation
        img_array = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3:
            frame = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            frame = img_array
        
        # Calculate card regions based on expected position
        height, width = frame.shape[:2]
        card_width = int(width * 0.44)
        card_height = int(card_width * 54 / 85.6)
        card_x = (width - card_width) // 2
        card_y = (height - card_height) // 2
        face_width = int(card_width * 0.4)
        
        # Extract face region (always the same)
        face_region = frame[card_y:card_y+card_height, card_x:card_x+face_width]
        
        # Initialize OCR
        tesseract_ocr = TesseractOCR()
        
        # Use automatic text region extraction (manual cropping removed for simplified deployment)
        text_region = frame[card_y:card_y+card_height, card_x+face_width:card_x+card_width]
        ocr_result = tesseract_ocr.extract_with_preprocessing(text_region)
        processing_method = "auto_region"
        
        # Process face region
        face_pil = Image.fromarray(cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB))
        face_encoding, face_msg = generate_face_encoding(face_pil)
        
        # Return processing results
        return {
            'success': True,
            'student_id': ocr_result.get('student_id', ''),
            'name': ocr_result.get('name', ''),
            'face_image': face_pil,
            'face_encoding': face_encoding,
            'confidence': ocr_result.get('confidence', 0.0),
            'ocr_success': ocr_result.get('success', False),
            'face_msg': face_msg,
            'full_frame': frame,
            'processing_method': processing_method,
            'processing_mode': processing_mode
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def student_card_workflow():
    """Complete student card capture and OCR workflow"""
    
    # Initialize
    from utils.session_manager import init_session_state, clear_capture
    from core.database import load_database, save_to_database
    from core.error_handler import validate_student_id, validate_name, ValidationError
    
    init_session_state()
    
    st.title("Student Card Registration")
    
    # Capture with guide
    captured_image = capture_card_with_guide()
    
    if captured_image is not None:
        # Store in session state
        st.session_state.capture_state['processed_image'] = captured_image
        
        # Extract info button with beautiful animation
        if st.button("📝 Extract Information", type="primary"):
            # Use the beautiful OCR loading animation
            result = show_ocr_processing_animation(
                extract_student_info_optimized, 
                captured_image, 
                debug=False,
                use_stable_ocr=True
            )
            
            if result['success']:
                    st.session_state.capture_state['ocr_result'] = result
                    st.balloons()
                    
                    # Display extracted info with confidence score
                    extracted_info = f"**Extracted Information:**\n- Student ID: {result['student_id']}"
                    if result.get('name'):
                        extracted_info += f"\n- Name: {result['name']}"
                    if result.get('confidence'):
                        extracted_info += f"\n- Confidence: {result['confidence']*100:.1f}%"
                    
                    st.success(extracted_info)
                    
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
                                value=result.get('name', ''),  # Auto-fill extracted name
                                help="Edit if detection was incorrect"
                            )
                            
                            program = st.selectbox(
                                "🎓 Program",
                                ["Computer Science", "Information Technology", "Software Engineering", 
                                 "Business Administration", "Accounting", "Marketing", "Other"]
                            )
                            
                            faculty = st.selectbox(
                                "🏛️ Faculty",
                                ["Faculty of Computing and Informatics", "Faculty of Business", 
                                 "Faculty of Engineering", "Faculty of Applied Sciences", "Other"]
                            )
                        
                        with col2:
                            st.markdown("#### 📊 Detection Results")
                            confidence_level = "High" if result.get('confidence', 0) > 0.8 else "Medium" if result.get('confidence', 0) > 0.5 else "Low"
                            st.metric("AI Confidence", confidence_level)
                            
                            st.markdown("#### 📸 Face Photo Required")
                            st.info("Take a clear photo for face recognition")
                            face_photo = st.camera_input("Take face photo", key="face_capture")
                            
                            if face_photo:
                                face_img = Image.open(face_photo)
                                face_img = fix_image_orientation(face_img)  # Fix orientation
                                st.image(face_img, caption="Face Photo", width=150)
                                
                                # Generate face encoding
                                with st.spinner("Processing face..."):
                                    encoding, msg = generate_face_encoding(face_img)
                                    if encoding:
                                        st.session_state.capture_state['face_encoding'] = encoding
                                        st.session_state.capture_state['face_image'] = face_img
                                        st.success("✅ Face processed successfully!")
                                    else:
                                        st.error(f"❌ Face processing failed: {msg}")
                        
                        # Submit buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            submitted = st.form_submit_button(
                                "✅ Register Student", 
                                type="primary",
                                use_container_width=True
                            )
                        with col2:
                            if st.form_submit_button("🔄 Retry Capture", use_container_width=True):
                                clear_capture()
                                st.rerun()
                        
                        if submitted:
                            try:
                                # Validate inputs
                                validate_student_id(student_id)
                                validate_name(student_name)
                                
                                # Check for duplicates (safe field access)
                                db = load_database()
                                if any((s.get('id') or s.get('student_id')) == student_id for s in db):
                                    st.error(f"❌ Student ID {student_id} already exists!")
                                else:
                                    face_image = st.session_state.capture_state.get('face_image')
                                    face_encoding = st.session_state.capture_state.get('face_encoding')
                                    
                                    if face_image and face_encoding:
                                        with st.spinner("Registering student..."):
                                            # Save face image
                                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                            image_filename = f"{student_id}_{timestamp}.jpg"
                                            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                                            face_image.save(image_path)
                                            
                                            # Normalize path for consistent storage
                                            normalized_path = normalize_path(image_path)
                                            
                                            # Create student record
                                            student_record = {
                                                'id': student_id,
                                                'name': student_name,
                                                'program': program,
                                                'faculty': faculty,
                                                'image_path': normalized_path,
                                                'encoding': face_encoding,
                                                'registration_date': datetime.now().isoformat(),
                                                'registered_via': 'ai_scan_enhanced',
                                                'ocr_confidence': result.get('confidence', 0.0)
                                            }
                                            
                                            # Save to database
                                            if save_to_database(student_record):
                                                st.session_state.registration_success = True
                                                st.session_state.student_data = student_record
                                                
                                                # Clear capture state
                                                clear_capture()
                                                
                                                st.success("🎉 Registration completed successfully!")
                                                st.rerun()
                                    else:
                                        st.error("❌ Please take a face photo before registering")
                                        
                            except ValidationError as e:
                                st.error(f"❌ Validation Error: {str(e)}")
                            except Exception as e:
                                st.error(f"❌ Registration failed: {str(e)}")
            else:
                if st.button("🔄 Retry Capture"):
                    clear_capture()
                    st.rerun()
    
    # Clear button
    if st.button("🗑️ Reset"):
        clear_capture()
        st.rerun()


