"""
IC Verification Module for Graduation Attendance System
Ported from ICVerifyBackupPlan Jupyter notebook
Provides Malaysian IC authenticity verification and face matching capabilities
"""
import cv2
import numpy as np
import base64
import tempfile
import os
from PIL import Image
from deepface import DeepFace
import streamlit as st
from typing import Tuple, Dict, List, Optional
from datetime import datetime
import json

from core.face_module import get_face_service
from core.database import load_database
from core.ic_error_handler import ICErrorHandler, ICVerificationError, safe_ic_verification
from PIL import ImageDraw, ImageFont


class ICVerificationService:
    """Service for Malaysian IC verification and face matching"""
    
    def __init__(self):
        self.custom_thresholds = {
            'Facenet': 0.80, 
            'VGG-Face': 0.95, 
            'ArcFace': 1.0, 
            'OpenFace': 0.85
        }
        self.models = ['Facenet', 'VGG-Face', 'ArcFace', 'OpenFace']
    
    def preload_models(self):
        """
        Preload all DeepFace models to avoid downloading during verification
        This ensures all models are available before starting IC verification
        """
        print("🔄 Preloading DeepFace models...")
        
        for model in self.models:
            try:
                print(f"📦 Loading {model} model...")
                # Force model initialization which triggers download if needed
                DeepFace.build_model(model)
                print(f"✅ {model} model loaded successfully")
            except Exception as e:
                print(f"⚠️ Warning: Could not preload {model} model: {str(e)}")
                # Continue with other models even if one fails
                continue
        
        print("🎉 Model preloading completed!")
    
    
    def preprocess_ic_image(self, image_input) -> Optional[np.ndarray]:
        """
        Preprocess IC image for verification with comprehensive validation
        Args:
            image_input: PIL Image or numpy array
        Returns:
            Preprocessed image as numpy array or None if error
        """
        try:
            # For PIL Images (already preprocessed), skip file size validation
            # Only validate structure and dimensions
            if isinstance(image_input, Image.Image):
                # Basic validation for PIL Images
                if image_input.size[0] < 300 or image_input.size[1] < 200:
                    raise ICVerificationError(
                        ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_TOO_SMALL"],
                        "IC_IMAGE_TOO_SMALL",
                        {"width": image_input.size[0], "height": image_input.size[1]}
                    )
                if image_input.size[0] > 5000 or image_input.size[1] > 5000:
                    raise ICVerificationError(
                        ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_TOO_LARGE"],
                        "IC_IMAGE_TOO_LARGE",
                        {"width": image_input.size[0], "height": image_input.size[1]}
                    )
            else:
                # For file objects and numpy arrays, do full validation
                validation_result = ICErrorHandler.handle_ic_image_validation(image_input)
                if not validation_result["valid"]:
                    raise ICVerificationError(
                        validation_result["message"],
                        validation_result["error_code"],
                        validation_result.get("details")
                    )
            
            if isinstance(image_input, Image.Image):
                img_array = np.array(image_input.convert('RGB'))
            elif isinstance(image_input, np.ndarray):
                img_array = image_input
            else:
                raise ICVerificationError(
                    ICErrorHandler.ERROR_MESSAGES["INVALID_FILE_FORMAT"],
                    "INVALID_FILE_FORMAT"
                )
            
            # Resize if too large
            height, width = img_array.shape[:2]
            if max(height, width) > 1500:
                scale = 1500 / max(height, width)
                new_size = (int(width * scale), int(height * scale))
                img_array = cv2.resize(img_array, new_size, interpolation=cv2.INTER_AREA)
            
            return img_array
            
        except ICVerificationError:
            raise  # Re-raise custom errors
        except Exception as e:
            ICErrorHandler.log_error("IC_PREPROCESSING_ERROR", str(e), {"include_trace": True})
            raise ICVerificationError(
                ICErrorHandler.ERROR_MESSAGES["IC_IMAGE_CORRUPTED"],
                "IC_IMAGE_CORRUPTED",
                {"original_error": str(e)}
            )
    
    def _enhance_ic_image(self, img_array: np.ndarray) -> np.ndarray:
        """Enhanced preprocessing for IC images to improve face recognition accuracy"""
        try:
            # Convert to 8-bit if needed
            if img_array.dtype != 'uint8':
                img_array = (img_array * 255).astype('uint8')
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) for better contrast
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            enhanced_lab = cv2.merge((cl, a, b))
            enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
            
            # Apply slight brightness and contrast adjustment
            alpha = 1.1  # Contrast control (1.0-3.0)
            beta = 10    # Brightness control (0-100)
            enhanced_img = cv2.convertScaleAbs(enhanced_img, alpha=alpha, beta=beta)
            
            # Apply gentle gaussian blur to reduce noise
            enhanced_img = cv2.GaussianBlur(enhanced_img, (3, 3), 0)
            
            print(f"✅ Applied enhanced IC preprocessing (contrast: {alpha}, brightness: +{beta})")
            return enhanced_img
            
        except Exception as e:
            print(f"❌ IC enhancement error: {str(e)}")
            return img_array

    def enhance_face_region(self, face_region: np.ndarray) -> np.ndarray:
        """Apply contrast enhancement to a face region"""
        try:
            # Convert to 8-bit image if it's not
            if face_region.dtype != 'uint8':
                face_region = (face_region * 255).astype('uint8')

            lab = cv2.cvtColor(face_region, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            enhanced_lab = cv2.merge((cl, a, b))
            enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
            return enhanced_rgb
        except Exception as e:
            print(f"❌ Face enhancement error: {str(e)}")
            return face_region
    
    def create_ic_with_bounding_boxes(self, ic_image: np.ndarray, detected_faces: List[Dict]) -> Image.Image:
        """
        Create IC image with colored bounding boxes around detected faces
        Args:
            ic_image: Original IC image as numpy array
            detected_faces: List of detected face data with facial_area info
        Returns:
            PIL Image with bounding boxes drawn
        """
        try:
            # Convert to PIL Image if needed
            if isinstance(ic_image, np.ndarray):
                pil_image = Image.fromarray(ic_image)
            else:
                pil_image = ic_image.copy()
            
            # Create drawing object
            draw = ImageDraw.Draw(pil_image)
            
            # Try to load a font (fallback to default if not available)
            try:
                font_size = max(20, min(pil_image.width // 30, 40))  # Responsive font size
                font = ImageFont.load_default()
            except Exception:
                font = ImageFont.load_default()
            
            # Color scheme for faces
            colors = {
                'main': {'color': 'cyan', 'label': 'Main Face'},
                'ghost': {'color': 'red', 'label': 'Ghost Face'}
            }
            
            # Draw bounding boxes
            for i, face_data in enumerate(detected_faces):
                if 'facial_area' not in face_data:
                    continue
                    
                # Get facial area coordinates
                facial_area = face_data['facial_area']
                x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
                
                # Determine face type (main = largest, ghost = second largest)
                face_type = 'main' if i == 0 else 'ghost'
                if face_type not in colors:
                    continue
                
                color_info = colors[face_type]
                color = color_info['color']
                label = color_info['label']
                
                # Draw rectangle border
                border_width = max(2, pil_image.width // 200)  # Responsive border width
                for offset in range(border_width):
                    draw.rectangle(
                        [x - offset, y - offset, x + w + offset, y + h + offset], 
                        outline=color, 
                        width=1
                    )
                
                # Draw label background
                label_bbox = draw.textbbox((0, 0), label, font=font)
                label_width = label_bbox[2] - label_bbox[0]
                label_height = label_bbox[3] - label_bbox[1]
                
                # Position label above the box
                label_x = x
                label_y = max(10, y - label_height - 5)
                
                # Draw label background rectangle
                draw.rectangle([
                    label_x - 3, label_y - 3,
                    label_x + label_width + 6, label_y + label_height + 3
                ], fill=color, outline=color)
                
                # Draw label text
                draw.text((label_x, label_y), label, fill='white', font=font)
                
                # Optional: Draw area information
                area_text = f"{face_data.get('area', 0):.0f}px²"
                area_y = label_y + label_height + 8
                draw.text((label_x, area_y), area_text, fill=color, font=font)
            
            return pil_image
            
        except Exception as e:
            print(f"❌ Error creating IC with bounding boxes: {str(e)}")
            # Return original image if annotation fails
            if isinstance(ic_image, np.ndarray):
                return Image.fromarray(ic_image)
            return ic_image
    
    @safe_ic_verification
    def verify_ic_authenticity(self, ic_image: np.ndarray) -> Dict:
        """
        Verify Malaysian IC authenticity using main face vs ghost face detection
        Args:
            ic_image: Preprocessed IC image as numpy array
        Returns:
            Dict with verification results
        """
        try:
            # Step 1: Detect all faces in the image
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                Image.fromarray(ic_image).save(tmp.name)
                temp_path = tmp.name
            
            try:
                detected_faces = DeepFace.extract_faces(
                    img_path=temp_path, 
                    detector_backend='retinaface',
                    enforce_detection=False
                )
                
                # Handle face detection results with proper error codes
                face_detection_result = ICErrorHandler.handle_face_detection_result(len(detected_faces))
                
                # Sort faces by area (for displaying detected faces even if verification fails)
                for face in detected_faces:
                    facial_area = face['facial_area']
                    face['area'] = facial_area['w'] * facial_area['h']
                detected_faces.sort(key=lambda x: x['area'], reverse=True)
                
                # Extract face images for display (even if verification will fail)
                face_images = {}
                if len(detected_faces) >= 1:
                    main_face_img = detected_faces[0]['face']
                    main_face_display = Image.fromarray((main_face_img * 255).astype('uint8'))
                    face_images["main_face_image"] = main_face_display
                    face_images["detected_faces_info"] = [{"area": detected_faces[0]['area'], "type": "main"}]
                    
                if len(detected_faces) >= 2:
                    ghost_face_img = detected_faces[1]['face']
                    enhanced_ghost_face = self.enhance_face_region(ghost_face_img)
                    ghost_face_display = Image.fromarray((enhanced_ghost_face * 255).astype('uint8'))
                    face_images["ghost_face_image"] = ghost_face_display
                    face_images["detected_faces_info"].append({"area": detected_faces[1]['area'], "type": "ghost"})
                
                if not face_detection_result["valid"]:
                    result = {
                        "status": "FAILED",
                        "verified": False,
                        "message": face_detection_result["message"],
                        "faces_detected": len(detected_faces),
                        "error_code": face_detection_result["error_code"],
                        "allow_manual_override": face_detection_result.get("allow_manual_override", False),
                        "warning_only": face_detection_result.get("warning_only", False)
                    }
                    # Add face images for demo even if verification failed
                    result.update(face_images)
                    
                    # Create IC with bounding boxes even for failed cases (demo purposes)
                    ic_with_boxes = self.create_ic_with_bounding_boxes(ic_image, detected_faces)
                    result["ic_with_bounding_boxes"] = ic_with_boxes
                    
                    return result
                
                # Continue with verification since face detection was valid
                main_face_data = detected_faces[0]
                ghost_face_data = detected_faces[1]
                
                # Step 3: Compare main and ghost faces
                main_face_img = main_face_data['face']
                ghost_face_img = ghost_face_data['face']
                
                # Enhance ghost face for better comparison
                enhanced_ghost_face = self.enhance_face_region(ghost_face_img)
                
                # Perform verification across multiple models
                verification_results = []
                verified_count = 0
                
                for model in self.models:
                    def verify_faces_with_model(main_path, ghost_path):
                        """Internal function for model verification"""
                        result = DeepFace.verify(
                            img1_path=main_path,
                            img2_path=ghost_path,
                            model_name=model,
                            distance_metric='cosine',
                            enforce_detection=False
                        )
                        return result
                    
                    try:
                        # Create temp files for both faces
                        main_temp_path = tempfile.mktemp(suffix=f'_main_{model}.jpg')
                        ghost_temp_path = tempfile.mktemp(suffix=f'_ghost_{model}.jpg')
                        
                        try:
                            # Save images
                            Image.fromarray((main_face_img * 255).astype('uint8')).save(main_temp_path, quality=95)
                            Image.fromarray((enhanced_ghost_face * 255).astype('uint8')).save(ghost_temp_path, quality=95)
                            
                            # Brief pause to ensure files are written
                            import time
                            time.sleep(0.1)
                            
                            # Perform verification
                            result_main = verify_faces_with_model(main_temp_path, ghost_temp_path)
                            
                        finally:
                            # Safe cleanup with retries
                            for temp_path in [main_temp_path, ghost_temp_path]:
                                if os.path.exists(temp_path):
                                    for attempt in range(3):
                                        try:
                                            time.sleep(0.05)
                                            os.unlink(temp_path)
                                            break
                                        except (PermissionError, OSError):
                                            if attempt < 2:
                                                time.sleep(0.2)
                                            else:
                                                print(f"Warning: Could not delete {temp_path}")
                        
                        if result_main:
                            distance = result_main['distance']
                            threshold = self.custom_thresholds.get(model)
                            is_match = distance <= threshold
                            
                            verification_results.append({
                                'model': model,
                                'verified': is_match,
                                'distance': distance,
                                'threshold': threshold
                            })
                            
                            if is_match:
                                verified_count += 1
                        else:
                            # Failed to process
                            verification_results.append({
                                'model': model,
                                'verified': False,
                                'error': 'Failed to create temporary files'
                            })
                            
                    except Exception as e:
                        verification_results.append({
                            'model': model,
                            'verified': False,
                            'error': str(e)
                        })
                
                # Final verdict based on majority agreement
                final_verdict = verified_count >= len(self.models) / 2
                
                # Convert face arrays to PIL Images for display
                main_face_display = Image.fromarray((main_face_img * 255).astype('uint8'))
                ghost_face_display = Image.fromarray((enhanced_ghost_face * 255).astype('uint8'))
                
                # Create IC image with bounding boxes for demo
                ic_with_boxes = self.create_ic_with_bounding_boxes(ic_image, detected_faces)
                
                return {
                    "status": "SUCCESS",
                    "verified": final_verdict,
                    "message": f"IC verification completed ({verified_count}/{len(self.models)} models agree)",
                    "faces_detected": len(detected_faces),
                    "main_face": main_face_data,
                    "ghost_face": ghost_face_data,
                    "main_face_image": main_face_display,  # For display in demo
                    "ghost_face_image": ghost_face_display,  # For display in demo
                    "ic_with_bounding_boxes": ic_with_boxes,  # Complete IC with face boxes
                    "verification_results": verification_results,
                    "verification_count": verified_count,
                    "confidence_score": (verified_count / len(self.models)) * 100
                }
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            return {
                "status": "ERROR",
                "verified": False,
                "message": f"IC verification error: {str(e)}",
                "error": str(e)
            }
    
    def extract_main_face(self, ic_image: np.ndarray, existing_verification: Dict = None) -> Optional[Tuple[np.ndarray, Dict]]:
        """
        Extract the main face from IC for database matching
        Args:
            ic_image: Preprocessed IC image
            existing_verification: Optional pre-existing verification result to avoid re-verification
        Returns:
            Tuple of (main_face_array, face_info) or None if failed
        """
        try:
            # Use existing verification result if provided, otherwise perform verification
            if existing_verification:
                verification_result = existing_verification
            else:
                verification_result = self.verify_ic_authenticity(ic_image)
            
            if not verification_result.get("verified"):
                return None
            
            main_face_data = verification_result.get("main_face")
            if not main_face_data:
                return None
            
            main_face_img = main_face_data['face']
            # Convert to uint8 format for consistency
            main_face_array = (main_face_img * 255).astype('uint8')
            
            face_info = {
                "facial_area": main_face_data['facial_area'],
                "area": main_face_data['area'],
                "ic_verification": verification_result
            }
            
            return main_face_array, face_info
            
        except Exception as e:
            print(f"❌ Main face extraction error: {str(e)}")
            return None
    
    @safe_ic_verification
    def find_student_by_face(self, ic_face_array: np.ndarray, similarity_threshold: float = 0.5) -> Tuple[Optional[Dict], float, List]:
        """
        Find student in database by comparing IC main face with registered photos
        Args:
            ic_face_array: Main face extracted from IC
            similarity_threshold: Minimum similarity score to consider a match
        Returns:
            Tuple of (student_data, similarity_score, similarity_scores_debug)
            student_data is None if no match found
        """
        try:
            # Get face service
            face_service = get_face_service()
            if not face_service.is_ready():
                raise ICVerificationError(
                    ICErrorHandler.ERROR_MESSAGES["FACE_SERVICE_UNAVAILABLE"],
                    "FACE_SERVICE_UNAVAILABLE"
                )
            
            # Generate embedding for IC face
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                Image.fromarray(ic_face_array).save(tmp.name)
                temp_path = tmp.name
            
            try:
                ic_embedding_result = face_service.generate_embedding(
                    img_path=temp_path,
                    enforce_detection=False
                )
                
                if not ic_embedding_result:
                    return None
                
                ic_embedding = np.array(ic_embedding_result[0]['embedding'], dtype=np.float32)
                
                # Load database and find matches
                database = load_database()
                students_with_encodings = [s for s in database if s.get('encoding')]
                
                if not students_with_encodings:
                    raise ICVerificationError(
                        ICErrorHandler.ERROR_MESSAGES["NO_STUDENTS_WITH_ENCODINGS"],
                        "NO_STUDENTS_WITH_ENCODINGS"
                    )
                
                best_match = None
                best_similarity = 0.0
                similarity_scores = []  # For debugging
                
                for student in students_with_encodings:
                    
                    try:
                        # Decode stored student encoding
                        stored_bytes = base64.b64decode(student['encoding'])
                        stored_embedding = np.frombuffer(stored_bytes, dtype=np.float32)
                        
                        # Calculate cosine similarity
                        cosine_sim = np.dot(ic_embedding, stored_embedding) / (
                            np.linalg.norm(ic_embedding) * np.linalg.norm(stored_embedding)
                        )
                        
                        # Store for debugging
                        similarity_scores.append({
                            'student': student.get('name', 'Unknown'),
                            'student_id': student.get('student_id', student.get('id', 'Unknown')),
                            'similarity': cosine_sim
                        })
                        
                        if cosine_sim > best_similarity and cosine_sim >= similarity_threshold:
                            best_similarity = cosine_sim
                            best_match = student
                            
                    except Exception as e:
                        continue  # Skip this student if encoding is invalid
                
                if best_match:
                    return best_match, best_similarity, similarity_scores
                    
                return None, 0.0, similarity_scores
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"❌ Student face matching error: {str(e)}")
            return None, 0.0, []


# Global instance
_ic_verification_service = None

def get_ic_verification_service() -> ICVerificationService:
    """Get singleton IC verification service"""
    global _ic_verification_service
    if _ic_verification_service is None:
        _ic_verification_service = ICVerificationService()
    return _ic_verification_service


@safe_ic_verification
def verify_ic_and_find_student(ic_image_input, similarity_threshold: float = 0.5) -> Dict:
    """
    Complete IC verification and student matching workflow
    Args:
        ic_image_input: PIL Image or numpy array of IC
        similarity_threshold: Minimum similarity for student matching
    Returns:
        Dict with complete verification results
    """
    service = get_ic_verification_service()
    
    # Step 0: Preload models to ensure they're all downloaded
    try:
        service.preload_models()
    except Exception as e:
        print(f"Warning: Model preloading failed: {e}")
        # Continue anyway, models will be downloaded on-demand
    
    # Step 1: Preprocess image
    processed_image = service.preprocess_ic_image(ic_image_input)
    if processed_image is None:
        return {
            "status": "ERROR",
            "step": "preprocessing",
            "message": "Failed to preprocess IC image"
        }
    
    # Step 2: Verify IC authenticity
    ic_verification = service.verify_ic_authenticity(processed_image)
    if not ic_verification.get("verified"):
        return {
            "status": "IC_INVALID",
            "step": "ic_verification",
            "message": ic_verification.get("message", "IC verification failed"),
            "ic_verification": ic_verification
        }
    
    # Step 3: Extract main face (pass existing verification result to avoid re-verification)
    main_face_result = service.extract_main_face(processed_image, existing_verification=ic_verification)
    if not main_face_result:
        return {
            "status": "ERROR",
            "step": "face_extraction",
            "message": "Failed to extract main face from IC",
            "ic_verification": ic_verification
        }
    
    main_face_array, face_info = main_face_result
    
    # Step 4: Find matching student
    student_data, similarity_score, similarity_scores = service.find_student_by_face(main_face_array, similarity_threshold)
    
    if not student_data:
        return {
            "status": "NO_MATCH",
            "step": "student_matching",
            "message": f"No student found with similarity >= {similarity_threshold:.0%}",
            "ic_verification": ic_verification,
            "main_face_extracted": True,
            "similarity_threshold": similarity_threshold,
            "similarity_scores": similarity_scores  # Include debug info
        }
    
    return {
        "status": "SUCCESS",
        "step": "completed",
        "message": f"Student matched with {similarity_score:.1%} similarity",
        "ic_verification": ic_verification,
        "student_found": True,  # Add this field for frontend
        "matched_student": student_data,  # Add this field for frontend
        "similarity": similarity_score,  # Add this field for frontend display
        "student_match": {
            "student": student_data,
            "similarity_score": similarity_score,
            "confidence": similarity_score * 100
        },
        "main_face_info": face_info,
        "similarity_threshold": similarity_threshold,
        "similarity_scores": similarity_scores  # Include debug info
    }