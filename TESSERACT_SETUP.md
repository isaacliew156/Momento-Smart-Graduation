# 🔄 Tesseract OCR Setup Guide

This guide explains how to set up and use the new Tesseract OCR integration for the Graduation Attendance System.

## 🚀 What's Changed

1. **Replaced Gemini OCR with Tesseract OCR** - No more API keys needed!
2. **Added face encoding from card photos** - Automatically extracts and encodes faces from student ID cards
3. **Enhanced error handling** - Manual entry option when OCR fails

## 📋 Prerequisites

### 1. Install Tesseract OCR

**Windows:**
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- The system will automatically detect this path

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 🧪 Testing the Integration

Run the test script to verify everything is working:

```bash
python test_tesseract_ocr.py
```

This will:
- Check Tesseract installation
- Test OCR functionality
- Optionally test camera capture

## 🎯 How It Works

### AI Card Scanning Process

1. **Image Capture**: 
   - Camera captures the student ID card
   - Card is divided into face region (left 35%) and text region (right 65%)

2. **Text Extraction (Tesseract OCR)**:
   - Applies image enhancement (CLAHE)
   - Extracts name region (30-50% of card height)
   - Extracts ID region (50-70% of card height)
   - Attempts multiple OCR configurations
   - Fixes common OCR mistakes (O/0, I/1, etc.)

3. **Face Processing**:
   - Extracts face from the card's photo region
   - Generates face encoding using DeepFace (Facenet512)
   - Stores encoding for later verification

4. **Error Handling**:
   - If OCR fails, still captures the face image
   - Allows manual entry of student details
   - Shows appropriate warnings and guidance

## 📝 Key Features

### Adaptive OCR Processing
- Different preprocessing for name vs ID regions
- Multiple PSM (Page Segmentation Mode) attempts
- Character substitution for common OCR errors

### Smart ID Validation
- Pattern matching for TARUMT format: `24WMR#####`
- Automatic correction of common misreads
- Fallback to manual entry

### Face Encoding Integration
- Automatically generates face encoding during scan
- Reuses encoding instead of regenerating
- Works even when OCR fails

## 🔧 Configuration

### Custom Tesseract Path (Optional)

If Tesseract is installed in a non-standard location, you can specify the path:

```python
# In core/tesseract_ocr.py
ocr = TesseractOCR(tesseract_path=r'C:\Custom\Path\tesseract.exe')
```

### Environment Settings

The system still respects environment-based image validation:

```bash
# For low light conditions
export GRAD_ENV=low_light

# For outdoor/bright conditions  
export GRAD_ENV=outdoor
```

## ⚠️ Troubleshooting

### "Tesseract not found" Error
- Ensure Tesseract is installed
- Windows: Check if installed to `C:\Program Files\Tesseract-OCR\`
- Linux/Mac: Ensure `tesseract` is in PATH

### Poor OCR Results
- Ensure good lighting
- Hold card steady and flat
- Keep card 6-12 inches from camera
- Clean camera lens

### Face Encoding Failures
- Ensure face is clearly visible in card photo
- Card photo should take up ~35% of card width
- Avoid reflections on card surface

## 🎓 Usage Tips

1. **Best Scanning Practices**:
   - Use bright, even lighting
   - Avoid shadows on the card
   - Keep card parallel to camera
   - Center card in the green guide box

2. **When OCR Fails**:
   - System will still capture the face
   - Manually enter student ID and name
   - Face verification will still work

3. **Verification Process**:
   - Face encoding from card is compared with live capture
   - No internet connection required
   - All processing happens locally

## 📊 Comparison: Gemini vs Tesseract

| Feature | Gemini OCR | Tesseract OCR |
|---------|-----------|---------------|
| API Key | Required ❌ | Not needed ✅ |
| Internet | Required ❌ | Offline ✅ |
| Cost | Pay per use 💰 | Free 🆓 |
| Speed | Slower (API call) | Faster (local) |
| Accuracy | Higher | Good with preprocessing |
| Privacy | Data sent to cloud ☁️ | Local processing 🔒 |

## 🛡️ Security Benefits

- **No API keys** to leak or manage
- **Offline processing** - student data stays local
- **No cloud dependencies** - works without internet
- **Full control** over data processing

---

Happy scanning! 🎓📸