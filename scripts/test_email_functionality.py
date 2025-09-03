#!/usr/bin/env python3
"""
Test script for email functionality
Tests the email module without running the full Streamlit application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from core.email_module import EmailService, get_email_service, is_email_enabled
from core.qr_module import generate_qr_code
import tempfile
import shutil

def test_email_configuration():
    """Test if email is properly configured"""
    print("🧪 Testing Email Configuration...")
    
    load_dotenv()
    
    gmail_user = os.getenv('GMAIL_USERNAME')
    gmail_pass = os.getenv('GMAIL_APP_PASSWORD')
    
    if not gmail_user:
        print("❌ GMAIL_USERNAME not found in environment variables")
        return False
    
    if not gmail_pass:
        print("❌ GMAIL_APP_PASSWORD not found in environment variables")
        return False
    
    print(f"✅ Gmail Username: {gmail_user}")
    print(f"✅ Gmail App Password: {'*' * len(gmail_pass)}")
    return True

def test_email_service():
    """Test email service initialization"""
    print("\n🧪 Testing Email Service...")
    
    service = get_email_service()
    
    if not service.is_configured():
        print("❌ Email service not configured")
        return False
    
    print("✅ Email service initialized successfully")
    return True

def test_gmail_connection():
    """Test Gmail SMTP connection"""
    print("\n🧪 Testing Gmail Connection...")
    
    service = get_email_service()
    success, msg = service.test_connection()
    
    if success:
        print(f"✅ {msg}")
        return True
    else:
        print(f"❌ {msg}")
        return False

def test_qr_generation():
    """Test QR code generation for email testing"""
    print("\n🧪 Testing QR Code Generation...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        qr_path, msg = generate_qr_code("TEST001", "Test Student", temp_dir)
        
        if qr_path and os.path.exists(qr_path):
            print(f"✅ QR code generated: {qr_path}")
            return qr_path
        else:
            print(f"❌ QR generation failed: {msg}")
            return None
    except Exception as e:
        print(f"❌ QR generation error: {str(e)}")
        return None

def test_email_sending(test_email_address):
    """Test sending actual email"""
    print(f"\n🧪 Testing Email Sending to {test_email_address}...")
    
    # Generate test QR code
    qr_path = test_qr_generation()
    if not qr_path:
        print("❌ Cannot test email sending without QR code")
        return False
    
    try:
        service = get_email_service()
        
        # Test email validation
        if not service.validate_email(test_email_address):
            print(f"❌ Invalid email format: {test_email_address}")
            return False
        
        # Send test QR email
        success, msg = service.send_qr_code_email(
            test_email_address,
            "Test Student",
            "TEST001",
            qr_path
        )
        
        if success:
            print(f"✅ {msg}")
            return True
        else:
            print(f"❌ {msg}")
            return False
    
    except Exception as e:
        print(f"❌ Email sending error: {str(e)}")
        return False
    finally:
        # Clean up temp directory
        if os.path.exists(os.path.dirname(qr_path)):
            shutil.rmtree(os.path.dirname(qr_path))

def test_template_generation():
    """Test HTML email template generation"""
    print("\n🧪 Testing Email Template Generation...")
    
    try:
        service = get_email_service()
        template = service.create_qr_email_template(
            "Test Student",
            "TEST001",
            "/path/to/test_qr.png"
        )
        
        if template and len(template) > 100:
            print("✅ Email template generated successfully")
            print(f"📊 Template size: {len(template)} characters")
            return True
        else:
            print("❌ Email template generation failed")
            return False
    
    except Exception as e:
        print(f"❌ Template generation error: {str(e)}")
        return False

def main():
    """Run all email functionality tests"""
    print("🎓 TARUMT Graduation System - Email Functionality Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    tests = [
        ("Configuration", test_email_configuration),
        ("Service Initialization", test_email_service),
        ("Template Generation", test_template_generation),
        ("Gmail Connection", test_gmail_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"🚫 {test_name} test failed")
        except Exception as e:
            print(f"🚫 {test_name} test crashed: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Email functionality is working correctly.")
        
        # Offer to test actual email sending
        test_email = input("\n📧 Enter an email address to test actual email sending (or press Enter to skip): ").strip()
        if test_email:
            if test_email_sending(test_email):
                print("🎉 Email sending test completed successfully!")
            else:
                print("❌ Email sending test failed")
    else:
        print("❌ Some tests failed. Please check your configuration.")
        print("\n💡 Common issues:")
        print("   1. Make sure .env file exists with correct Gmail credentials")
        print("   2. Enable 2-Step Verification in your Gmail account")
        print("   3. Generate and use an App Password (not your regular password)")
        print("   4. Check your internet connection")

if __name__ == "__main__":
    main()