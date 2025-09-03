# 📧 Email Functionality Setup Guide

## ✨ Feature Overview
Your graduation scanning system now supports sending QR codes via email! Students can choose to receive emails containing their personal QR codes during registration.

### 🎯 Key Features
- **Registration Email Option**: Students can opt to receive QR code emails
- **Professional HTML Templates**: Beautifully designed email layouts
- **QR Code Attachments**: QR codes sent as image attachments
- **Resend Capability**: Resend emails from QR Management page
- **Bulk Sending**: One-click send to all students with email addresses
- **Email Testing**: Test Gmail configuration functionality

## 🛠️ Configuration Steps

### 1. Enable Gmail 2-Step Verification
1. Log in to your Gmail account
2. Go to [Google Account Security Settings](https://myaccount.google.com/security)
3. Enable "2-Step Verification" (if not already enabled)

### 2. Generate App-Specific Password
1. In Google Account, go to "Security" > "2-Step Verification"
2. Click "App passwords"
3. Select "Mail" application
4. Copy the generated 16-character password

### 3. Configure Environment Variables
1. Copy `.env.example` file in project root directory
2. Rename to `.env`
3. Enter your Gmail credentials:
```bashGMAIL_USERNAME=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password

### 4. Restart Application
```bashstreamlit run app_new.py

## 🎮 Usage Guide

### 📋 Student Registration
1. Navigate to Student Registration page
2. Complete student information
3. Check "📨 Send QR code via email"
4. Enter student email address
5. Click Register - email will be sent automatically

### 🔐 QR Code Management
1. Go to QR Code Management page
2. **Individual Sending**:
   - Search for student
   - Enter email address
   - Click "📧 Send QR via Email"
3. **Bulk Sending**:
   - Go to "Bulk Management" tab
   - Click "📧 Send QR Codes to All Students"

### 🧪 Test Email Functionality
1. Go to QR Code Management > Status Tracking tab
2. Use "📡 Connection Test" to test Gmail connection
3. Use "📧 Test Email" to send test email

## 📧 Email Template Contents
Students will receive professional emails containing:
- Personalized greeting
- Student information confirmation
- QR code usage instructions
- Graduation ceremony guidelines
- QR code image attachment

## 🔧 Troubleshooting

### Common Errors and Solutions

#### ❌ "Authentication failed"
- Ensure using app-specific password, not regular password
- Verify username and password are correct
- Confirm 2-Step Verification is enabled

#### ❌ "Email service not configured"
- Check if `.env` file exists in project root
- Confirm environment variable names are correct
- Restart Streamlit application

#### ❌ "Invalid email address"
- Check email format is correct
- Ensure no extra spaces

#### ❌ "Connection refused"
- Check network connection
- Confirm firewall isn't blocking SMTP connections

### 📊 Gmail Sending Limits
- Gmail has daily sending limits
- For bulk sending, consider batching
- Business accounts typically have higher limits

## 🔒 Security Considerations
- Never share your app-specific password
- Don't commit `.env` file to version control
- Regularly rotate app-specific passwords
- If password is compromised, revoke and generate new one immediately

## 🧪 Test Script
Run test script to verify configuration:
```bashcd scripts
python test_email_functionality.py

## 📝 Technical Details

### Email Service Features
- Uses Gmail SMTP (smtp.gmail.com:587)
- TLS encrypted connection
- Supports HTML email format
- Automatic attachment handling

### Database Updates
Student records now include:
- `email`: Student email address
- `email_notifications`: Email notification preference

### New Files Added
- `core/email_module.py`: Core email functionality module
- `.env.example`: Environment variable template
- `scripts/test_email_functionality.py`: Test script

## 🎉 Enjoy the New Feature!
Students can now receive QR codes directly on their phones, making graduation ceremony check-in more convenient!

---
© 2025 TAR UMT Graduation System - Email Enhanced Edition
