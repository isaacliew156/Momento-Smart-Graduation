# 🎓 Momento - Smart Graduation Recognition System

An intelligent graduation ceremony management system combining QR code scanning with facial recognition for automated student identification and announcement during convocation ceremonies.

## ✨ Features

- **📱 QR Code Detection**: Real-time QR code scanning with Pyzbar (36ms processing speed)
- **👤 Face Recognition**: Dual-factor authentication using DeepFace (Facenet512) with 96% accuracy
- **🔄 Multiple Verification Methods**: QR → Face → IC → Manual override fallback chain
- **🔊 Automated Announcement**: Text-to-speech for graduate name announcement
- **📊 Real-time Processing**: Live attendance tracking with duplicate prevention
- **🛡️ Security Features**: 60-second duplicate prevention window, cosine distance threshold 0.4

## 🎯 Objectives

1. Develop QR code scanning module for varying lighting conditions
2. Implement facial recognition for biometric identity verification  
3. Build integrated display and audio announcement system
4. Ensure no student is excluded through comprehensive fallback mechanisms

## 👥 Team Members

- **Chew Jia Min** - QR Detection Module
- **Choong Kai Feng** - Face Recognition System
- **Liew Yi Shen** - System Backend Integration
- **Lim Huan Qian** - User Interface Design

## 🛠️ Technology Stack

### Core Technologies
- **Language**: Python 3.8+
- **QR Detection**: Pyzbar (wrapper for ZBar), OpenCV
- **Face Recognition**: DeepFace (Facenet512 model)
- **Face Detection**: OpenCV detector backend
- **OCR**: Tesseract (for IC verification fallback)
- **Image Enhancement**: CLAHE, Bilateral Filtering
- **UI Framework**: Streamlit

### Multi-Model Verification (IC Fallback)
- Facenet
- VGG-Face
- ArcFace
- OpenFace

## 📁 Project Structure

```
Momento-Smart-Graduation/
├── app.py                  # Main Streamlit application
├── core/                   # Core modules
│   ├── face_module.py     # Face recognition (Facenet512)
│   ├── qr_module.py       # QR scanning (Pyzbar)
│   ├── database.py        # JSON database operations
│   ├── ic_verification.py # Multi-model IC verification
│   └── tts_module.py      # Text-to-speech announcements
├── data/
│   ├── captures/          # Face verification photos
│   ├── static/            # Generated QR codes
│   └── uploads/           # IC images
├── database.json          # Student registration data
├── attendance.json        # Attendance records
├── ic_verification_log.json # IC verification logs
├── requirements.txt       # Dependencies
├── .env.example           # Email configuration template
└── secrets.toml.example   # Streamlit configuration template
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Webcam/Camera for QR scanning and face recognition
- Gmail account with 2-factor authentication (optional, for email features)

### Step 1: Clone the Repository
```bash
git clone https://github.com/isaacliew156/Momento-Smart-Graduation.git
cd Momento-Smart-Graduation
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Application Settings

The project includes configuration templates for reference:
- `secrets.toml.example` - Template for Streamlit configuration
- `.env.example` - Template for email configuration

#### Streamlit Configuration
1. Copy `secrets.toml.example` as a reference
2. Create `.streamlit` folder in your user directory:
   - Windows: `C:\Users\[YourUsername]\.streamlit\`
   - Mac/Linux: `~/.streamlit/`
3. Create `secrets.toml` file based on the example:

```toml
# Copy from secrets.toml.example and modify
[app]
staff_password = "your_secure_password_here"  # Change this!
debug_mode = false
show_confidence = true
auto_save_scans = true

[performance]
max_face_size = 1024
min_face_confidence = 0.8
qr_scan_timeout = 10
```

#### Email Configuration (Optional)
If using email features:
1. Copy `.env.example` as a reference
2. Create `.env` file in project root
3. Fill in your Gmail credentials:

```env
# Gmail SMTP Configuration
GMAIL_USERNAME=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx_xxxx_xxxx_xxxx  # 16-character app password
```

### Step 4: Gmail App Password Setup (Optional)

If using email features:
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Select "Mail" and generate password
5. Copy 16-character password to `.env` file

### Step 5: Run the Application
```bash
streamlit run app.py
```
The application will open in your default browser at `http://localhost:8501`

## ⚠️ Security Important Notes

**NEVER commit these files to GitHub:**
- `.env` - Contains email credentials
- `secrets.toml` - Contains application passwords
- `.streamlit/` folder - Contains sensitive configuration
- Any file with actual passwords or API keys

**Use example files for reference:**
- `secrets.toml.example` - Template for Streamlit configuration
- `.env.example` - Template for email configuration

## 📊 System Performance

- **QR Detection**: 300 iterations (~10 seconds timeout)
- **Face Verification Threshold**: 0.4 cosine distance
- **IC Matching Threshold**: 0.5 similarity score
- **Processing Speed**: Real-time at 30 FPS
- **Face Recognition Accuracy**: 96% under controlled conditions

## 🔧 Algorithm Implementation

### QR Detection Pipeline
Pyzbar continuously scans video frames for QR codes. The system converts camera frames to grayscale and uses pyzbar's decode function to detect QR patterns within a designated scan area. A 2-second stable detection requirement ensures accuracy before accepting the QR code.

### Face Recognition Pipeline 
The system employs a two-stage approach: OpenCV detector first detects face regions in captured frames, reducing the search space. Valid face regions are then processed by FaceNet (via DeepFace) to generate 512-dimensional embeddings using the Facenet512 model. These embeddings are compared with stored templates using cosine similarity (threshold: 0.4) to verify identity.

### Image Enhancement
CLAHE (Contrast Limited Adaptive Histogram Equalization) is applied to face images and OCR text regions before processing to normalize lighting variations. Bilateral filtering is used in OCR preprocessing to reduce noise while preserving text edges. This preprocessing step is crucial for maintaining consistent recognition performance across different ceremony venues and lighting conditions.

### IC Verification Fallback
When primary verification fails, the system activates multi-model verification using four different face recognition models (Facenet, VGG-Face, ArcFace, OpenFace). A consensus mechanism requiring agreement from at least 2 models ensures reliable fallback verification.

### Integration Workflow
The algorithms work in sequence: QR scanning initiates the process, triggering face capture and verification. If both succeed, attendance is recorded. Failed verifications activate the IC fallback mechanism, ensuring no student is excluded due to technical limitations.

## 🌟 Key Innovations

- **Dual-Factor Authentication**: Combines QR and biometric verification
- **Robust Fallback Chain**: Ensures no student is excluded
- **Real-time Feedback**: Visual and audio confirmations
- **Staff Override**: Manual control for edge cases
- **Flexible ID Format Support**: Accommodates multiple student ID formats (19-25 years, various program codes)

## 📚 Course Information

**Course**: BMDS2133 Image Processing  
**Institution**: Tunku Abdul Rahman University of Management and Technology (TAR UMT)  
**Semester**: 202505  
**Lecturer**: Ts. Dr Tan Chi Wee

## 🎯 SDG Alignment

- **SDG 4**: Quality Education - Enhancing graduation ceremony experience
- **SDG 9**: Industry, Innovation and Infrastructure - Applying Industry 4.0 technologies
- **SDG 8**: Decent Work and Economic Growth - Creating technology development opportunities

## 📝 Academic Use

This project was developed for educational purposes as part of the BMDS2133 Image Processing course at TAR UMT. The system demonstrates practical applications of computer vision, machine learning, and real-time image processing techniques in an academic setting.

## 🤝 Acknowledgments

- TAR UMT for providing the learning opportunity
- Ts. Dr Tan Chi Wee for guidance and support
- Open-source communities of OpenCV, DeepFace, and Pyzbar
- DeepFace library for state-of-the-art face recognition capabilities
- Tesseract OCR engine for text recognition functionality