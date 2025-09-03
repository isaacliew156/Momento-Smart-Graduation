# 🔧 Setup Instructions for Momento

## ⚠️ Important: Environment Setup Required

This repository does not include sensitive configuration files. You need to set up your environment before running the application.

## 📋 Prerequisites

1. **Python 3.8+**
2. **Webcam/Camera** for face recognition and QR scanning
3. **Gmail Account** (for email notifications)

## 🚀 Setup Steps

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/Momento-Smart-Graduation.git
cd Momento-Smart-Graduation
pip install -r requirements.txt
```

### 2. Environment Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure Gmail SMTP (Optional):**
   - Enable 2-Step Verification in your Gmail account
   - Generate an App Password for "Mail" application
   - Edit `.env` file with your credentials:
   ```
   GMAIL_USERNAME=your_email@domain.com
   GMAIL_APP_PASSWORD=your_16_char_app_password
   ```

### 3. Create Data Directories

```bash
mkdir -p data/captures
mkdir -p data/uploads  
mkdir -p data/static
```

### 4. Initialize Database Files

The application will create these automatically on first run:
- `data/database.json` - Student records
- `data/attendance.json` - Attendance data
- `data/ic_verification_log.json` - Verification logs

### 5. Run the Application

```bash
streamlit run app.py
```

## 🛡️ Security Notes

- **Never commit `.env` files** - They contain sensitive credentials
- **Data files are excluded** - Personal student information is not included
- **Review .gitignore** - Ensure no sensitive files are tracked

## 📝 For Academic Use

This is an educational project. Replace placeholder data with your own institution's information:

1. Update course information in README.md
2. Modify institution branding in the UI
3. Adjust student ID formats for your system
4. Configure email templates as needed

## 🆘 Common Issues

### "No such file or directory" errors
- Run the data directory creation commands above
- Ensure `.env` file exists (copy from `.env.example`)

### Email functionality not working
- Check Gmail configuration in `.env`
- Verify App Password is correct (not regular Gmail password)
- Test with Gmail's 2-Step Verification enabled

### Camera not detected
- Grant camera permissions to your browser
- Ensure no other applications are using the camera
- Try restarting the application

## 📚 Additional Resources

- [Gmail App Password Setup](https://support.google.com/accounts/answer/185833)
- [Streamlit Documentation](https://docs.streamlit.io)
- [OpenCV Python Documentation](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)