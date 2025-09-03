"""
Image processing utilities for the Graduation Attendance System
Handles image orientation, EXIF data, and preprocessing
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageOps
import streamlit as st
from typing import Tuple, Optional


def fix_image_orientation(image: Image.Image) -> Image.Image:
    """
    Fix image orientation based on EXIF data
    Args:
        image: PIL Image object
    Returns:
        PIL Image with corrected orientation
    """
    try:
        # Use ImageOps.exif_transpose to automatically handle EXIF orientation
        corrected_image = ImageOps.exif_transpose(image)
        return corrected_image
    except Exception as e:
        print(f"⚠️ Could not fix image orientation: {str(e)}")
        return image


def rotate_image(image: Image.Image, angle: int) -> Image.Image:
    """
    Manually rotate image by specified angle
    Args:
        image: PIL Image object
        angle: Rotation angle in degrees (90, 180, 270, or -90, -180, -270)
    Returns:
        Rotated PIL Image
    """
    try:
        if angle == 0:
            return image
        
        # Normalize angle to standard values
        angle = angle % 360
        if angle == 90:
            return image.rotate(-90, expand=True)
        elif angle == 180:
            return image.rotate(180, expand=True)
        elif angle == 270:
            return image.rotate(90, expand=True)
        else:
            return image.rotate(-angle, expand=True)
    except Exception as e:
        print(f"❌ Error rotating image: {str(e)}")
        return image


def preprocess_uploaded_image(uploaded_file, max_size_mb: float = 10.0) -> Tuple[Optional[Image.Image], dict]:
    """
    Comprehensive preprocessing of uploaded image files
    Args:
        uploaded_file: Streamlit uploaded file object
        max_size_mb: Maximum allowed file size in MB
    Returns:
        Tuple of (processed_image, processing_info)
    """
    processing_info = {
        "success": False,
        "original_size": None,
        "processed_size": None,
        "orientation_fixed": False,
        "file_size_mb": 0,
        "format": None,
        "errors": []
    }
    
    try:
        if uploaded_file is None:
            processing_info["errors"].append("No file uploaded")
            return None, processing_info
        
        # Check actual file size (most accurate)
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        processing_info["file_size_mb"] = file_size_mb
        processing_info["file_size_source"] = "actual_file_size"
        
        if file_size_mb > max_size_mb:
            processing_info["errors"].append(f"File size ({file_size_mb:.1f}MB) exceeds maximum ({max_size_mb}MB)")
            return None, processing_info
        
        # Reset file position
        uploaded_file.seek(0)
        
        # Load image
        try:
            image = Image.open(uploaded_file)
            processing_info["format"] = image.format
            processing_info["original_size"] = image.size
        except Exception as e:
            processing_info["errors"].append(f"Cannot open image: {str(e)}")
            return None, processing_info
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            processing_info["converted_to_rgb"] = True
        
        # Fix orientation based on EXIF data
        original_size = image.size
        image = fix_image_orientation(image)
        
        if image.size != original_size:
            processing_info["orientation_fixed"] = True
        
        processing_info["processed_size"] = image.size
        processing_info["success"] = True
        
        return image, processing_info
        
    except Exception as e:
        processing_info["errors"].append(f"Unexpected error: {str(e)}")
        return None, processing_info


def create_image_rotation_controls(image: Image.Image, key_prefix: str = "img") -> Tuple[Image.Image, bool]:
    """
    Create Streamlit controls for manual image rotation
    Args:
        image: PIL Image to rotate
        key_prefix: Prefix for Streamlit component keys
    Returns:
        Tuple of (rotated_image, rotation_applied)
    """
    st.markdown("#### 🔄 Adjust Image Orientation")
    
    col1, col2, col3, col4 = st.columns(4)
    
    rotated_image = image
    rotation_applied = False
    
    with col1:
        if st.button("↻ 90°", key=f"{key_prefix}_rotate_90", help="Rotate 90° counterclockwise"):
            rotated_image = rotate_image(image, 90)
            rotation_applied = True
    
    with col2:
        if st.button("↻ 180°", key=f"{key_prefix}_rotate_180", help="Rotate 180°"):
            rotated_image = rotate_image(image, 180)
            rotation_applied = True
    
    with col3:
        if st.button("↻ 270°", key=f"{key_prefix}_rotate_270", help="Rotate 270° counterclockwise"):
            rotated_image = rotate_image(image, 270)
            rotation_applied = True
    
    with col4:
        if st.button("🔄 Reset", key=f"{key_prefix}_reset", help="Reset to original orientation"):
            rotated_image = image
            rotation_applied = True
    
    return rotated_image, rotation_applied


def enhance_ic_image_quality(image: Image.Image) -> Tuple[Image.Image, dict]:
    """
    Enhance IC image quality for better face detection
    Args:
        image: PIL Image of IC card
    Returns:
        Tuple of (enhanced_image, enhancement_info)
    """
    enhancement_info = {
        "brightness_adjusted": False,
        "contrast_adjusted": False,
        "sharpness_adjusted": False,
        "original_size": image.size,
        "final_size": image.size
    }
    
    try:
        from PIL import ImageEnhance
        
        # Convert to numpy for analysis
        img_array = np.array(image)
        
        # Check if image is too dark or too bright
        brightness = np.mean(img_array)
        
        enhanced_image = image
        
        # Adjust brightness if needed
        if brightness < 80:  # Too dark
            brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = brightness_enhancer.enhance(1.3)
            enhancement_info["brightness_adjusted"] = True
        elif brightness > 200:  # Too bright
            brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = brightness_enhancer.enhance(0.8)
            enhancement_info["brightness_adjusted"] = True
        
        # Adjust contrast
        contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
        enhanced_image = contrast_enhancer.enhance(1.1)
        enhancement_info["contrast_adjusted"] = True
        
        # Slight sharpening
        sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
        enhanced_image = sharpness_enhancer.enhance(1.1)
        enhancement_info["sharpness_adjusted"] = True
        
        return enhanced_image, enhancement_info
        
    except Exception as e:
        print(f"⚠️ Image enhancement failed: {str(e)}")
        return image, enhancement_info


def detect_and_correct_text_skew(image: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Detect and correct text skew in image using Hough transform
    Args:
        image: OpenCV image (numpy array)
    Returns:
        Tuple of (corrected_image, detected_angle)
    """
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Apply Hough transform to detect lines
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        
        if lines is not None:
            # Calculate angles
            angles = []
            for rho, theta in lines[:, 0]:
                angle = np.degrees(theta) - 90
                # Filter out extreme angles (likely not text)
                if -45 < angle < 45:
                    angles.append(angle)
            
            if angles:
                # Use median angle to avoid outliers
                median_angle = np.median(angles)
                
                # Only correct if skew is significant
                if abs(median_angle) > 2:
                    print(f"📐 Detected text skew: {median_angle:.1f}°, correcting...")
                    
                    # Get image center
                    height, width = image.shape[:2]
                    center = (width // 2, height // 2)
                    
                    # Create rotation matrix
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    
                    # Rotate image
                    corrected = cv2.warpAffine(image, rotation_matrix, (width, height),
                                             borderMode=cv2.BORDER_CONSTANT,
                                             borderValue=(255, 255, 255))
                    
                    return corrected, median_angle
        
        # No significant skew detected
        return image, 0.0
        
    except Exception as e:
        print(f"⚠️ Skew correction failed: {str(e)}")
        return image, 0.0


def detect_image_orientation_issues(image: Image.Image) -> dict:
    """
    Detect potential orientation issues with the IC image
    Args:
        image: PIL Image of IC card
    Returns:
        Dict with orientation analysis
    """
    orientation_info = {
        "likely_upside_down": False,
        "likely_rotated": False,
        "confidence": 0.0,
        "suggestions": []
    }
    
    try:
        # Convert to grayscale for analysis
        gray = image.convert('L')
        img_array = np.array(gray)
        
        # Simple heuristics to detect orientation issues
        height, width = img_array.shape
        
        # Check if image is wider than tall (landscape vs portrait)
        aspect_ratio = width / height
        
        # For IC cards, we expect landscape orientation (wider than tall)
        if aspect_ratio < 0.8:  # Portrait orientation
            orientation_info["likely_rotated"] = True
            orientation_info["confidence"] = 0.7
            orientation_info["suggestions"].append("IC appears to be rotated. Try rotating 90°.")
        
        # Check brightness distribution (top vs bottom)
        # Many ICs have darker areas at the bottom
        top_half = img_array[:height//2, :]
        bottom_half = img_array[height//2:, :]
        
        top_brightness = np.mean(top_half)
        bottom_brightness = np.mean(bottom_half)
        
        # If bottom is significantly brighter than top, might be upside down
        if bottom_brightness > top_brightness * 1.3:
            orientation_info["likely_upside_down"] = True
            orientation_info["confidence"] = max(orientation_info["confidence"], 0.6)
            orientation_info["suggestions"].append("IC might be upside down. Try rotating 180°.")
        
        return orientation_info
        
    except Exception as e:
        print(f"⚠️ Orientation detection failed: {str(e)}")
        return orientation_info


def create_image_preview_with_controls(uploaded_file, key_prefix: str = "ic") -> Tuple[Optional[Image.Image], dict]:
    """
    Create image preview with rotation controls and enhancement options
    Args:
        uploaded_file: Streamlit uploaded file
        key_prefix: Prefix for component keys
    Returns:
        Tuple of (final_image, processing_info)
    """
    if uploaded_file is None:
        return None, {"success": False, "message": "No file uploaded"}
    
    # Process uploaded image
    processed_image, processing_info = preprocess_uploaded_image(uploaded_file)
    
    if not processing_info["success"]:
        st.error("❌ **Image Processing Failed**")
        for error in processing_info["errors"]:
            st.error(f"• {error}")
        return None, processing_info
    
    # Display processing info
    if processing_info.get("orientation_fixed"):
        st.success("✅ Image orientation automatically corrected based on EXIF data")
    
    # Display original image
    st.markdown("#### 📷 Uploaded Image")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        current_image = processed_image
        
        # Show current image
        st.image(current_image, caption=f"Current Image - {current_image.size[0]}×{current_image.size[1]}", width=300)
        
        # Rotation controls
        if st.expander("🔄 Manual Rotation Controls", expanded=False):
            rotated_image, rotation_applied = create_image_rotation_controls(processed_image, key_prefix)
            if rotation_applied:
                current_image = rotated_image
                st.image(current_image, caption=f"Rotated Image - {current_image.size[0]}×{current_image.size[1]}", width=300)
                st.success("✅ Rotation applied!")
    
    with col2:
        # Display image info
        st.markdown("##### 📊 Image Info")
        st.write(f"**Format:** {processing_info.get('format', 'Unknown')}")
        st.write(f"**Dimensions:** {current_image.size[0]}×{current_image.size[1]}")
        
        # Show actual file size (most accurate)
        actual_file_size = processing_info.get('file_size_mb', 0)
        st.write(f"**Actual File Size:** {actual_file_size:.1f}MB")
        
        # Calculate and show memory usage estimation  
        width, height = current_image.size
        estimated_memory_mb = (width * height * 3) / (1024 * 1024)
        if estimated_memory_mb != actual_file_size:
            st.write(f"**Memory Usage:** ~{estimated_memory_mb:.1f}MB (uncompressed)")
        
        # Orientation analysis
        orientation_info = detect_image_orientation_issues(current_image)
        if orientation_info["suggestions"]:
            st.markdown("##### ⚠️ Orientation Tips")
            for suggestion in orientation_info["suggestions"]:
                st.info(f"💡 {suggestion}")
        
        # Enhancement option
        if st.button("✨ Enhance Quality", key=f"{key_prefix}_enhance", help="Auto-adjust brightness and contrast"):
            enhanced_image, enhancement_info = enhance_ic_image_quality(current_image)
            current_image = enhanced_image
            
            if any(enhancement_info.values()):
                st.success("✅ Image enhanced!")
                st.image(current_image, caption="Enhanced Image", width=300)
    
    final_processing_info = processing_info.copy()
    final_processing_info["final_image_size"] = current_image.size
    
    return current_image, final_processing_info