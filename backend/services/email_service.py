"""
Email Service
Handles sending emails for welcome, password reset, and notifications
Currently mocked - logs to console instead of sending real emails
"""
from typing import Optional, Dict, List
from datetime import datetime
import os


class EmailService:
    """
    Email service for sending transactional emails
    Currently mocked for development
    """
    
    def __init__(self):
        self.enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        self.from_email = os.getenv("EMAIL_FROM", "noreply@noteshub.app")
        self.provider = os.getenv("EMAIL_PROVIDER", "mock")  # mock, sendgrid, resend, etc.
        
        print(f"📧 Email service initialized (provider: {self.provider}, enabled: {self.enabled})")
    
    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)
        
        Returns:
            True if email sent successfully
        """
        if not self.enabled or self.provider == "mock":
            # Mock: Just log to console
            print("\n" + "="*80)
            print(f"📧 MOCK EMAIL")
            print("="*80)
            print(f"To: {to}")
            print(f"From: {self.from_email}")
            print(f"Subject: {subject}")
            print("-"*80)
            print(html_body)
            print("="*80 + "\n")
            return True
        
        # Real email sending would go here
        # Example for SendGrid, Resend, etc.
        return False
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to NotesHub! 🎉"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to NotesHub!</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name}! 👋</h2>
                    <p>Thank you for joining NotesHub - your collaborative platform for sharing academic notes.</p>
                    
                    <h3>Get Started:</h3>
                    <ul>
                        <li>📤 Upload your notes to share with classmates</li>
                        <li>📥 Download notes from your department</li>
                        <li>🤝 Collaborate in real-time with drawing tools</li>
                        <li>🎯 Track your contributions and engagement</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:3000" class="button">Start Exploring</a>
                    </div>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Happy learning!<br>The NotesHub Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NotesHub. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_body)
    
    async def send_password_reset_email(
        self,
        user_email: str,
        user_name: str,
        reset_link: str
    ) -> bool:
        """Send password reset email"""
        subject = "Reset Your NotesHub Password 🔐"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #ef4444; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #ef4444; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name},</h2>
                    <p>We received a request to reset your NotesHub password.</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>This link will expire in 1 hour for security reasons.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Note:</strong><br>
                        If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
                    </div>
                    
                    <p>For security reasons, this link can only be used once.</p>
                    
                    <p>Best regards,<br>The NotesHub Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NotesHub. All rights reserved.</p>
                    <p style="font-size: 12px;">If the button doesn't work, copy and paste this link:<br>{reset_link}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, html_body)
    
    async def send_note_upload_notification(
        self,
        recipient_email: str,
        uploader_name: str,
        note_title: str,
        department: str,
        subject_name: str
    ) -> bool:
        """Notify users about new note uploads in their department"""
        subject = f"New Note Available: {note_title}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .note-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📚 New Note Available!</h1>
                </div>
                <div class="content">
                    <p>A new note has been uploaded to your department:</p>
                    
                    <div class="note-info">
                        <h3>{note_title}</h3>
                        <p><strong>Subject:</strong> {subject_name}</p>
                        <p><strong>Department:</strong> {department}</p>
                        <p><strong>Uploaded by:</strong> {uploader_name}</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:3000/find-notes" class="button">View Note</a>
                    </div>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        You're receiving this email because you have note notifications enabled. 
                        You can change your notification preferences in your account settings.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 NotesHub. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(recipient_email, subject, html_body)
    
    async def send_download_notification(
        self,
        uploader_email: str,
        note_title: str,
        downloader_name: str
    ) -> bool:
        """Notify note uploader when someone downloads their note"""
        subject = f"Your note '{note_title}' was downloaded"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #3b82f6; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .stats {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📥 Note Downloaded!</h1>
                </div>
                <div class="content">
                    <p>Great news! Your note is helping other students.</p>
                    
                    <div class="stats">
                        <h3>{note_title}</h3>
                        <p>Downloaded by: <strong>{downloader_name}</strong></p>
                        <p style="color: #6b7280; margin-top: 10px;">🎉 Keep sharing valuable content!</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:3000/profile" class="button">View Your Stats</a>
                    </div>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        You're receiving this email because you have download notifications enabled. 
                        You can change your notification preferences in your account settings.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2025 NotesHub. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(uploader_email, subject, html_body)


# Global email service instance
email_service = EmailService()
