"""
Stable OCR processor with multiple strategies to ensure consistent results
Handles edge cases and provides reliable extraction even in varying conditions
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter
import hashlib
from PIL import Image
import re

from core.tesseract_ocr import TesseractOCR


class StableOCR:
    """Stable OCR processor that uses multiple strategies for consistent results"""
    
    def __init__(self):
        self.ocr = TesseractOCR()
        self.result_cache = {}
        self.cache_size = 20
        self.last_successful_params = None
        
    def stable_extract(self, image: np.ndarray, num_attempts: int = 3, 
                      enable_cache: bool = True) -> Dict:
        """
        Extract student info with multiple attempts and voting mechanism
        
        Args:
            image: Input image (numpy array)
            num_attempts: Number of extraction attempts
            enable_cache: Whether to use result caching
            
        Returns:
            Dict with extraction results
        """
        # Check cache first
        if enable_cache:
            image_hash = self._compute_image_hash(image)
            if image_hash in self.result_cache:
                print(f"📦 Using cached result for image hash: {image_hash[:8]}...")
                cached = self.result_cache[image_hash]
                cached['from_cache'] = True
                return cached
        
        # Perform multiple extraction attempts
        all_results = []
        extraction_methods = []
        
        for attempt in range(num_attempts):
            print(f"\n🔄 Extraction attempt {attempt + 1}/{num_attempts}")
            
            # Apply different strategies for each attempt
            if attempt == 0:
                # Original image
                processed = image
                method = "original"
            elif attempt == 1:
                # Slightly adjusted brightness
                processed = self._adjust_brightness(image, 1.1)
                method = "brightness_1.1"
            elif attempt == 2:
                # Slightly adjusted contrast
                processed = self._adjust_contrast(image, 1.05)
                method = "contrast_1.05"
            else:
                # Micro rotation
                angle = 0.5 if attempt % 2 == 0 else -0.5
                processed = self._micro_rotate(image, angle)
                method = f"rotate_{angle}"
            
            # Extract with current processing
            result = self.ocr.extract_student_info(processed)
            
            if result.get('success'):
                all_results.append(result)
                extraction_methods.append(method)
                print(f"  ✅ Attempt {attempt + 1} successful - Method: {method}")
                print(f"     ID: {result.get('student_id', 'None')}, Name: {result.get('name', 'None')}")
        
        # Vote on best result
        final_result = self._vote_best_result(all_results, extraction_methods)
        
        # Add metadata
        final_result['attempts'] = num_attempts
        final_result['successful_attempts'] = len(all_results)
        final_result['extraction_methods'] = extraction_methods
        
        # Cache successful result
        if enable_cache and final_result.get('success'):
            self._add_to_cache(image_hash, final_result)
        
        return final_result
    
    def stable_extract_with_augmentation(self, image: np.ndarray) -> Dict:
        """
        Extract with image augmentation for maximum stability
        
        Args:
            image: Input image
            
        Returns:
            Extraction results
        """
        augmented_images = self._generate_augmentations(image)
        all_results = []
        
        print(f"🔬 Testing {len(augmented_images)} augmented versions")
        
        for aug_name, aug_image in augmented_images:
            result = self.ocr.extract_student_info(aug_image)
            if result.get('success'):
                result['augmentation'] = aug_name
                all_results.append(result)
                print(f"  ✅ {aug_name}: ID={result.get('student_id')}")
        
        # Vote for best result
        final_result = self._vote_best_result(all_results, 
                                             [r['augmentation'] for r in all_results])
        
        print(f"📊 Final result from {len(all_results)} successful extractions")
        
        return final_result
    
    def _generate_augmentations(self, image: np.ndarray) -> List[Tuple[str, np.ndarray]]:
        """Generate augmented versions of the image"""
        augmentations = [
            ("original", image),
        ]
        
        # Brightness variations
        for factor in [0.95, 1.05]:
            aug = self._adjust_brightness(image, factor)
            augmentations.append((f"brightness_{factor}", aug))
        
        # Contrast variations
        for factor in [0.98, 1.02]:
            aug = self._adjust_contrast(image, factor)
            augmentations.append((f"contrast_{factor}", aug))
        
        # Micro rotations
        for angle in [-0.3, 0.3]:
            aug = self._micro_rotate(image, angle)
            augmentations.append((f"rotate_{angle}", aug))
        
        # Slight scale changes
        for scale in [0.99, 1.01]:
            aug = self._micro_scale(image, scale)
            augmentations.append((f"scale_{scale}", aug))
        
        # Different denoising levels
        for h in [5, 8, 10]:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            denoised = cv2.fastNlMeansDenoising(gray, h=h)
            # Convert back to BGR if needed
            if len(image.shape) == 3:
                denoised = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
            augmentations.append((f"denoise_{h}", denoised))
        
        return augmentations
    
    def _vote_best_result(self, results: List[Dict], methods: List[str]) -> Dict:
        """Vote for the best result from multiple attempts"""
        if not results:
            return {
                'success': False,
                'error': 'No successful extractions',
                'confidence': 0.0
            }
        
        # If only one result, return it
        if len(results) == 1:
            result = results[0].copy()
            result['vote_confidence'] = 1.0 / 3.0  # Low confidence with single result
            return result
        
        # Vote on student IDs
        id_votes = Counter()
        name_votes = Counter()
        
        for result in results:
            if result.get('student_id'):
                id_votes[result['student_id']] += 1
            if result.get('name'):
                name_votes[result['name']] += 1
        
        # Get most common ID and name with quality-based tie-breaking
        best_id = id_votes.most_common(1)[0][0] if id_votes else None
        
        # For names, use quality scoring when votes are tied
        best_name = self._select_best_name_by_quality(name_votes, results) if name_votes else None
        
        # Calculate vote confidence
        vote_confidence = 0.0
        if best_id and id_votes[best_id] > 1:
            vote_confidence = id_votes[best_id] / len(results)
        
        # Find the result that matches the voted ID
        for result in results:
            if result.get('student_id') == best_id:
                final_result = result.copy()
                final_result['vote_confidence'] = vote_confidence
                final_result['id_votes'] = dict(id_votes)
                final_result['name_votes'] = dict(name_votes)
                
                # Override name with most voted if different
                if best_name and best_name != result.get('name'):
                    final_result['name'] = best_name
                    final_result['name_corrected'] = True
                
                print(f"🗳️ Voting result: ID={best_id} ({id_votes[best_id]}/{len(results)} votes)")
                
                return final_result
        
        # Fallback to first successful result
        result = results[0].copy()
        result['vote_confidence'] = 1.0 / len(results)
        return result
    
    def _select_best_name_by_quality(self, name_votes: Counter, results: List[Dict]) -> str:
        """Select best name using quality scoring when votes are tied"""
        if not name_votes:
            return None
            
        # Get all names with the highest vote count
        max_votes = name_votes.most_common(1)[0][1]
        top_voted_names = [name for name, count in name_votes.items() if count == max_votes]
        
        # If only one name has the highest votes, return it
        if len(top_voted_names) == 1:
            return top_voted_names[0]
        
        # Multiple names tied - use quality scoring to break tie
        print(f"🗳️ Name vote tie detected: {len(top_voted_names)} names with {max_votes} votes each")
        print(f"🎯 Using quality scoring to resolve tie: {top_voted_names}")
        
        # Score each tied name using TesseractOCR's quality function
        scored_names = []
        for name in top_voted_names:
            score = self.ocr._score_name_quality(name)
            scored_names.append((score, name))
            print(f"   '{name}' -> Quality score: {score}")
        
        # Sort by score (highest first) and return best
        scored_names.sort(key=lambda x: x[0], reverse=True)
        best_score, best_name = scored_names[0]
        
        print(f"🏆 Quality-based winner: '{best_name}' (score: {best_score})")
        return best_name
    
    def _adjust_brightness(self, image: np.ndarray, factor: float) -> np.ndarray:
        """Adjust image brightness"""
        return cv2.convertScaleAbs(image, alpha=factor, beta=0)
    
    def _adjust_contrast(self, image: np.ndarray, factor: float) -> np.ndarray:
        """Adjust image contrast"""
        return cv2.convertScaleAbs(image, alpha=factor, beta=128 * (1 - factor))
    
    def _micro_rotate(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Apply micro rotation to image"""
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (w, h), 
                             borderMode=cv2.BORDER_CONSTANT,
                             borderValue=(255, 255, 255))
    
    def _micro_scale(self, image: np.ndarray, scale: float) -> np.ndarray:
        """Apply micro scaling to image"""
        h, w = image.shape[:2]
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Scale image
        scaled = cv2.resize(image, (new_w, new_h))
        
        # Pad or crop to original size
        if scale > 1:
            # Crop center
            x_offset = (new_w - w) // 2
            y_offset = (new_h - h) // 2
            return scaled[y_offset:y_offset+h, x_offset:x_offset+w]
        else:
            # Pad with white
            pad_x = (w - new_w) // 2
            pad_y = (h - new_h) // 2
            padded = np.ones((h, w, 3), dtype=np.uint8) * 255
            padded[pad_y:pad_y+new_h, pad_x:pad_x+new_w] = scaled
            return padded
    
    def _compute_image_hash(self, image: np.ndarray) -> str:
        """Compute hash of image for caching"""
        # Resize to small size for hashing
        small = cv2.resize(image, (32, 32))
        # Convert to bytes and hash
        return hashlib.md5(small.tobytes()).hexdigest()
    
    def _add_to_cache(self, image_hash: str, result: Dict):
        """Add result to cache with size limit"""
        # Remove oldest if cache is full
        if len(self.result_cache) >= self.cache_size:
            # Remove first (oldest) item
            oldest_key = list(self.result_cache.keys())[0]
            del self.result_cache[oldest_key]
        
        # Add new result
        self.result_cache[image_hash] = result.copy()
        print(f"📦 Cached result for hash: {image_hash[:8]}...")
    
    def extract_with_retry(self, image: np.ndarray, max_retries: int = 3) -> Dict:
        """
        Extract with automatic retry on failure
        
        Args:
            image: Input image
            max_retries: Maximum number of retries
            
        Returns:
            Extraction results
        """
        for retry in range(max_retries):
            print(f"\n🔁 Retry {retry + 1}/{max_retries}")
            
            # Try with progressively different parameters
            if retry == 0:
                result = self.stable_extract(image, num_attempts=2)
            elif retry == 1:
                # Try with augmentation
                result = self.stable_extract_with_augmentation(image)
            else:
                # Last resort - try with aggressive preprocessing
                enhanced = self._aggressive_preprocess(image)
                result = self.ocr.extract_student_info(enhanced)
            
            if result.get('success'):
                result['retries'] = retry
                return result
        
        # All retries failed
        return {
            'success': False,
            'error': f'Failed after {max_retries} retries',
            'retries': max_retries,
            'confidence': 0.0
        }
    
    def _aggressive_preprocess(self, image: np.ndarray) -> np.ndarray:
        """Apply aggressive preprocessing for difficult images"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Strong denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=15)
        
        # Strong CLAHE
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(denoised)
        
        # Bilateral filter for edge preservation
        bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Convert back to BGR
        return cv2.cvtColor(bilateral, cv2.COLOR_GRAY2BGR)