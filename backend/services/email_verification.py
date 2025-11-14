import secrets
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.email_service import email_service
import os


class EmailVerificationService:
    """
    Service for handling email verification
    """
    
    def __init__(self):
        self.verification_expiry_hours = 24
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    def generate_verification_token(self) -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    async def create_verification_token(self, db: AsyncIOMotorDatabase, user_id: str, email: str) -> str:
        """
        Create and store a verification token for a user
        """
        token = self.generate_verification_token()
        expiry = datetime.utcnow() + timedelta(hours=self.verification_expiry_hours)
        
        # Store token in database
        from bson import ObjectId
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "email_verification_token": token,
                "email_verification_expiry": expiry,
                "email_verified": False
            }}
        )
        
        return token
    
    async def send_verification_email(self, user_email: str, user_name: str, token: str) -> bool:
        """
        Send verification email to user
        """
        verification_link = f"{self.frontend_url}/verify-email?token={token}"
        
        subject = "Verify Your NotesHub Email Address"
        
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
                .warning {{ background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✉️ Verify Your Email</h1>
                </div>
                <div class="content">
                    <h2>Hi {user_name}!</h2>
                    <p>Thank you for registering with NotesHub. To complete your registration, please verify your email address.</p>
                    
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </div>
                    
                    <p>This verification link will expire in 24 hours for security reasons.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Note:</strong><br>
                        If you didn't create an account with NotesHub, please ignore this email.
                    </div>
                    
                    <p>For security reasons, this link can only be used once.</p>
                    
                    <p>Best regards,<br>The NotesHub Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NotesHub. All rights reserved.</p>
                    <p style="font-size: 12px;">If the button doesn't work, copy and paste this link:<br>{verification_link}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""Hi {user_name},
        
Thank you for registering with NotesHub. Please verify your email address by visiting:
{verification_link}

This link will expire in 24 hours.

Best regards,
The NotesHub Team
        """
        
        return await email_service.send_email(user_email, subject, html_body, text_body)
    
    async def verify_email_token(self, db: AsyncIOMotorDatabase, token: str) -> Optional[str]:
        """
        Verify email token and mark email as verified.
        Returns user_id if successful, None otherwise.
        """
        user = await db.users.find_one({
            "email_verification_token": token,
            "email_verification_expiry": {"$gt": datetime.utcnow()}
        })
        
        if not user:
            return None
        
        # Mark email as verified and clear token
        from bson import ObjectId
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "email_verified": True,
                "email_verification_token": None,
                "email_verification_expiry": None
            }}
        )
        
        return str(user["_id"])
    
    async def resend_verification_email(self, db: AsyncIOMotorDatabase, user_id: str) -> bool:
        """
        Resend verification email to user
        """
        from bson import ObjectId
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            return False
        
        if user.get("email_verified"):
            return False  # Already verified
        
        # Create new token
        token = await self.create_verification_token(db, user_id, user["email"])
        
        # Send email
        return await self.send_verification_email(
            user["email"],
            user["usn"],
            token
        )


# Global instance
email_verification_service = EmailVerificationService()
