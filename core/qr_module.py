import cv2
import qrcode
import json
import numpy as np
import streamlit as st
from pyzbar.pyzbar import decode
import time
import os
from PIL import Image, ImageDraw, ImageFont

def generate_qr_code(student_id, name, output_dir="static"):
    """
    Generate QR code for student
    Returns: (qr_path, message)
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        qr_data = {
            "student_id": student_id,
            "name": name
        }
        
        qr_path = os.path.join(output_dir, f"{student_id}_qr.png")
        
        # Create QR code
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        img_qr = qr.make_image(fill_color="black", back_color="white")
        img_qr.save(qr_path)
        
        return qr_path, "QR code generated successfully!"
        
    except Exception as e:
        return None, f"Error generating QR code: {str(e)}"

def continuous_qr_scan():
    """
    Continuous QR scanning with visual feedback
    Returns: Decoded QR data string or None
    """
    cap = cv2.VideoCapture(0)
    stframe = st.empty()
    qr_data = None
    
    # Frame dimensions and scan area
    w, h = 640, 480
    center_box = (int(w * 0.3), int(h * 0.3), int(w * 0.4), int(h * 0.4))
    
    scan_start_time = None
    countdown_start = None
    
    with st.spinner("📷 Position QR code in the yellow frame..."):
        for _ in range(300):  # 10 seconds max scan time
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Draw scan guide with pulse effect
            (cx, cy, cw, ch) = center_box
            pulse = int(20 * (0.5 + 0.5 * np.sin(time.time() * 3)))
            cv2.rectangle(frame, 
                         (cx - pulse//4, cy - pulse//4), 
                         (cx + cw + pulse//4, cy + ch + pulse//4), 
                         (0, 255, 255), 3)
            
            # Instruction text
            cv2.putText(frame, "Place QR code in yellow frame", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            stframe.image(frame, channels="BGR")
            
            # Decode QR codes
            qrs = decode(gray)
            qr_in_frame = False
            
            for qr in qrs:
                x, y, w_qr, h_qr = qr.rect
                
                # Check if QR center is in scan area
                qr_center_x = x + w_qr // 2
                qr_center_y = y + h_qr // 2
                
                if (cx < qr_center_x < cx + cw) and (cy < qr_center_y < cy + ch):
                    qr_in_frame = True
                    
                    # Draw detection box
                    cv2.rectangle(frame, (x, y), (x + w_qr, y + h_qr), (0, 255, 0), 2)
                    
                    if scan_start_time is None:
                        scan_start_time = time.time()
                        countdown_start = time.time()
                    
                    # 2-second stable read requirement
                    elapsed = time.time() - countdown_start
                    remaining = max(0, 2.0 - elapsed)
                    
                    if remaining > 0:
                        cv2.putText(frame, f"Hold still... {remaining:.1f}s", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        # Successfully captured
                        qr_data = qr.data.decode("utf-8")
                        cv2.putText(frame, "QR Code Captured!", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        stframe.image(frame, channels="BGR")
                        cap.release()
                        return qr_data
            
            if not qr_in_frame:
                scan_start_time = None
                countdown_start = None
    
    cap.release()
    return None

def create_custom_qr(student_id, name, output_dir="static", size=(300, 300), border=4, 
                     add_label=True, label_position="below"):
    """
    Create customized QR code with optional label
    Returns: (custom_qr_path, message)
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        qr_data = {
            "student_id": student_id,
            "name": name
        }
        
        # Calculate box size based on requested dimensions
        box_size = size[0] // 25
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        if add_label:
            # Create image with space for label
            label_height = 50
            total_height = qr_img.height + label_height
            
            if label_position == "above":
                final_img = Image.new('RGB', (qr_img.width, total_height), 'white')
                final_img.paste(qr_img, (0, label_height))
                text_y = 10
            else:  # below
                final_img = Image.new('RGB', (qr_img.width, total_height), 'white')
                final_img.paste(qr_img, (0, 0))
                text_y = qr_img.height + 10
            
            # Add text label
            draw = ImageDraw.Draw(final_img)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            text = f"{name} ({student_id})"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (final_img.width - text_width) // 2
            
            draw.text((text_x, text_y), text, fill="black", font=font)
            
            custom_qr = final_img
        else:
            custom_qr = qr_img
        
        # Save custom QR
        custom_path = os.path.join(output_dir, f"{student_id}_custom_qr.png")
        custom_qr.save(custom_path)
        
        return custom_path, "Custom QR code generated successfully!"
        
    except Exception as e:
        return None, f"Error generating custom QR: {str(e)}"