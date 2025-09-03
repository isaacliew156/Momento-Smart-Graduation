"""
Test script for Tesseract OCR integration
"""
import sys
import os
import cv2
from PIL import Image

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tesseract_ocr import TesseractOCR

def test_tesseract_import():
    """Test if Tesseract OCR can be imported and initialized"""
    print("🔍 Testing Tesseract OCR import...")
    try:
        ocr = TesseractOCR()
        print("✅ Tesseract OCR imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Tesseract OCR import failed: {e}")
        return False

def test_tesseract_installation():
    """Test if Tesseract is properly installed"""
    print("\n🔍 Testing Tesseract installation...")
    try:
        import pytesseract
        # Try to get version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract not properly installed: {e}")
        print("\n📋 Installation instructions:")
        print("   Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Linux: sudo apt-get install tesseract-ocr")
        print("   macOS: brew install tesseract")
        return False

def test_sample_image():
    """Test OCR on the sample image if available"""
    print("\n🔍 Testing OCR on sample image...")
    
    sample_path = "test_student_card_synthetic.jpg"
    if not os.path.exists(sample_path):
        print(f"⚠️ Sample image not found: {sample_path}")
        return False
    
    try:
        # Initialize OCR
        ocr = TesseractOCR()
        
        # Load image
        image = cv2.imread(sample_path)
        if image is None:
            print("❌ Failed to load image")
            return False
        
        print(f"📷 Image loaded: {image.shape}")
        
        # Test OCR
        result = ocr.extract_student_info(image)
        
        print("\n📋 OCR Results:")
        print(f"   Success: {result['success']}")
        print(f"   Student ID: {result.get('student_id', 'Not detected')}")
        print(f"   Name: {result.get('name', 'Not detected')}")
        print(f"   Confidence: {result.get('confidence', 0.0)*100:.1f}%")
        print(f"   Sharpness: {result.get('sharpness', 0):.1f}")
        
        if 'error' in result:
            print(f"   Error: {result['error']}")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_camera_capture():
    """Test camera capture with live preview"""
    print("\n🔍 Testing camera capture...")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open camera")
            return False
        
        print("✅ Camera opened successfully!")
        print("📸 Press 'SPACE' to capture or 'Q' to quit")
        
        ocr = TesseractOCR()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Calculate ROI
            h, w = frame.shape[:2]
            roi_scale = 0.5
            roi_w = int(w * roi_scale)
            roi_h = int(roi_w / ocr.card_ratio)
            x1 = (w - roi_w) // 2
            y1 = (h - roi_h) // 2
            x2 = x1 + roi_w
            y2 = y1 + roi_h
            
            # Draw ROI
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "Place Card Here", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.imshow('Tesseract OCR Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                # Extract card region
                card = frame[y1:y2, x1:x2]
                
                print("\n📸 Captured! Processing...")
                result = ocr.extract_student_info(card)
                
                print("\n📋 OCR Results:")
                print(f"   Success: {result['success']}")
                print(f"   Student ID: {result.get('student_id', 'Not detected')}")
                print(f"   Name: {result.get('name', 'Not detected')}")
                print(f"   Sharpness: {result.get('sharpness', 0):.1f}")
                
                if 'error' in result:
                    print(f"   Error: {result['error']}")
        
        cap.release()
        cv2.destroyAllWindows()
        return True
        
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 Tesseract OCR Integration Test")
    print("=" * 50)
    
    # Test 1: Import
    test_import = test_tesseract_import()
    
    # Test 2: Installation
    test_install = test_tesseract_installation()
    
    if not test_import or not test_install:
        print("\n❌ Basic tests failed. Please install Tesseract OCR first.")
        return
    
    # Test 3: Sample image
    test_sample_image()
    
    # Test 4: Camera (optional)
    print("\n" + "=" * 50)
    response = input("Do you want to test camera capture? (y/n): ")
    if response.lower() == 'y':
        test_camera_capture()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()