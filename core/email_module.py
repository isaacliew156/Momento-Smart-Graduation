"""
Email Module for Graduation Attendance System
Handles sending QR codes and notifications via Gmail SMTP
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import re
import streamlit as st
from typing import Optional, Tuple, List


class EmailService:
    """Service for sending emails via Gmail SMTP"""
    
    def __init__(self):
        # Gmail SMTP configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = None
        self.sender_password = None
        self.sender_name = "TARUMT Graduation System"
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Gmail credentials from environment variables"""
        self.sender_email = os.getenv('GMAIL_USERNAME')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not self.sender_email or not self.sender_password:
            st.warning("⚠️ Gmail credentials not configured. Email functionality will be disabled.")
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.sender_email and self.sender_password)
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def create_qr_email_template(self, student_name: str, student_id: str, qr_path: str) -> str:
        """Create HTML email template for QR code delivery"""
        template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Graduation QR Code</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    background: linear-gradient(135deg, #2D3436 0%, #636E72 100%);
                    color: white;
                    padding: 35px 25px;
                    border-radius: 12px;
                    margin-bottom: 35px;
                    box-shadow: 0 4px 16px rgba(45, 52, 54, 0.15);
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 0 20px;
                }}
                .student-info {{
                    background-color: #f8f9fa;
                    padding: 25px;
                    border-left: 4px solid #74B9FF;
                    margin: 25px 0;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(45, 52, 54, 0.08);
                }}
                .qr-section {{
                    text-align: center;
                    margin: 30px 0;
                    padding: 20px;
                    background-color: #f0f7ff;
                    border-radius: 8px;
                }}
                .important-note {{
                    background-color: #f0f7ff;
                    border: 1px solid #74B9FF;
                    border-left: 4px solid #74B9FF;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 25px 0;
                    box-shadow: 0 2px 8px rgba(116, 185, 255, 0.1);
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 14px;
                    color: #666;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 25px;
                    background: linear-gradient(135deg, #74B9FF 0%, #0984E3 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>TARUMT Graduation Ceremony</h1>
                    <p>Your QR Code for Attendance</p>
                </div>
                
                <div class="content">
                    <h2>Dear {student_name},</h2>
                    
                    <p>Congratulations on your upcoming graduation! 🎉</p>
                    
                    <div class="student-info">
                        <h3>📋 Student Information</h3>
                        <p><strong>Name:</strong> {student_name}</p>
                        <p><strong>Student ID:</strong> {student_id}</p>
                        <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    </div>
                    
                    <div class="qr-section">
                        <h3>📱 Your Personal QR Code</h3>
                        <p>Please find your personalized QR code attached to this email.</p>
                        <p><strong>Attachment:</strong> {student_id}_qr.png</p>
                    </div>
                    
                    <div class="important-note">
                        <h4>⚠️ Important Instructions:</h4>
                        <ul>
                            <li>Save this QR code image to your phone</li>
                            <li>Present it at the graduation ceremony for quick check-in</li>
                            <li>Make sure your phone screen is clean and bright</li>
                            <li>Arrive early to avoid queues</li>
                        </ul>
                    </div>
                    
                    <h3>🎯 How to Use Your QR Code:</h3>
                    <ol>
                        <li>Download and save the QR code image from the attachment</li>
                        <li>On graduation day, open the image on your phone</li>
                        <li>Show the QR code to the scanning station</li>
                        <li>Wait for the green confirmation light</li>
                        <li>Proceed to the ceremony venue</li>
                    </ol>
                    
                    <p>If you encounter any issues, please contact the graduation committee or IT support.</p>
                    
                    <p><strong>We look forward to celebrating your achievement!</strong> 🎉</p>
                </div>
                
                <div class="footer">
                    <p>© 2025 TARUMT Graduation System</p>
                    <p>This is an automated email. Please do not reply directly to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return template
    
    def send_qr_code_email(self, recipient_email: str, student_name: str, 
                          student_id: str, qr_path: str) -> Tuple[bool, str]:
        """
        Send QR code to student via email
        
        Args:
            recipient_email (str): Student's email address
            student_name (str): Student's name
            student_id (str): Student ID
            qr_path (str): Path to QR code image file
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.is_configured():
                return False, "Email service not configured. Please set up Gmail credentials."
            
            if not self.validate_email(recipient_email):
                return False, f"Invalid email address: {recipient_email}"
            
            if not os.path.exists(qr_path):
                return False, f"QR code file not found: {qr_path}"
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = f"🎓 Your Graduation QR Code - {student_name}"
            
            # HTML body
            html_body = self.create_qr_email_template(student_name, student_id, qr_path)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach QR code image
            with open(qr_path, "rb") as attachment:
                # Create MIMEBase object
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)
            
            # Add header as key/value pair to attachment part
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {student_id}_qr.png',
            )
            
            # Attach the part to message
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS encryption
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True, f"QR code sent successfully to {recipient_email}"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Gmail authentication failed. Please check your app password."
        except smtplib.SMTPRecipientsRefused:
            return False, f"Invalid recipient email address: {recipient_email}"
        except smtplib.SMTPException as e:
            return False, f"SMTP error occurred: {str(e)}"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def send_bulk_emails(self, email_list: List[dict]) -> dict:
        """
        Send QR codes to multiple students
        
        Args:
            email_list (List[dict]): List of student email data
            Format: [{"email": "...", "name": "...", "id": "...", "qr_path": "..."}, ...]
            
        Returns:
            dict: Summary of results
        """
        results = {
            "success": [],
            "failed": [],
            "total": len(email_list)
        }
        
        for student in email_list:
            success, message = self.send_qr_code_email(
                student["email"], 
                student["name"], 
                student["id"], 
                student["qr_path"]
            )
            
            if success:
                results["success"].append({
                    "name": student["name"], 
                    "email": student["email"]
                })
            else:
                results["failed"].append({
                    "name": student["name"], 
                    "email": student["email"], 
                    "error": message
                })
        
        return results
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test Gmail SMTP connection"""
        try:
            if not self.is_configured():
                return False, "Email credentials not configured"
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                
            return True, "Gmail connection successful"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Check your Gmail app password."
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def send_test_email(self, recipient_email: str) -> Tuple[bool, str]:
        """Send a test email to verify functionality"""
        try:
            if not self.is_configured():
                return False, "Email service not configured"
            
            if not self.validate_email(recipient_email):
                return False, f"Invalid email address: {recipient_email}"
            
            # Create test message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = "🧪 TARUMT Email Service Test"
            
            html_body = """
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>🧪 Email Service Test</h2>
                    <p>This is a test email from the TARUMT Graduation System.</p>
                    <p>If you receive this message, the email service is working correctly!</p>
                    <hr>
                    <p><small>Time: {}</small></p>
                </body>
            </html>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True, f"Test email sent successfully to {recipient_email}"
            
        except Exception as e:
            return False, f"Test email failed: {str(e)}"


# Global email service instance
_email_service = None

def get_email_service() -> EmailService:
    """Get singleton email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

def send_qr_email(recipient_email: str, student_name: str, student_id: str, qr_path: str) -> Tuple[bool, str]:
    """Convenience function to send QR code email"""
    email_service = get_email_service()
    return email_service.send_qr_code_email(recipient_email, student_name, student_id, qr_path)

def is_email_enabled() -> bool:
    """Check if email functionality is available"""
    email_service = get_email_service()
    return email_service.is_configured()