"""
Enhanced Authentication Security Service
Handles account lockout, session timeout, and refresh token rotation
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import secrets


class AuthSecurityService:
    """Service for enhanced authentication security features"""
    
    # Configuration
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=30)
    SESSION_TIMEOUT = timedelta(hours=24)
    REFRESH_TOKEN_ROTATION_THRESHOLD = timedelta(days=1)
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
    
    async def record_login_attempt(self, usn: str, success: bool) -> Dict:
        """
        Record a login attempt and check if account should be locked
        
        Returns:
            dict with 'locked' boolean and 'unlock_at' timestamp if locked
        """
        user = await self.db.users.find_one({"usn": usn.upper()})
        if not user:
            return {"locked": False}
        
        now = datetime.utcnow()
        
        # Initialize security fields if they don't exist
        if "login_attempts" not in user:
            user["login_attempts"] = 0
            user["last_login_attempt"] = None
            user["account_locked_until"] = None
        
        # Check if account is currently locked
        if user.get("account_locked_until") and user["account_locked_until"] > now:
            return {
                "locked": True,
                "unlock_at": user["account_locked_until"],
                "reason": "Too many failed login attempts"
            }
        
        # If account was locked but lockout period expired, reset
        if user.get("account_locked_until") and user["account_locked_until"] <= now:
            await self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "login_attempts": 0,
                    "account_locked_until": None
                }}
            )
            user["login_attempts"] = 0
        
        if success:
            # Reset login attempts on successful login
            await self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "login_attempts": 0,
                    "last_login_attempt": now,
                    "last_successful_login": now,
                    "account_locked_until": None
                }}
            )
            return {"locked": False}
        else:
            # Increment failed attempts
            new_attempts = user.get("login_attempts", 0) + 1
            update_data = {
                "login_attempts": new_attempts,
                "last_login_attempt": now
            }
            
            # Lock account if max attempts exceeded
            if new_attempts >= self.MAX_LOGIN_ATTEMPTS:
                lockout_until = now + self.LOCKOUT_DURATION
                update_data["account_locked_until"] = lockout_until
                
                await self.db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": update_data}
                )
                
                return {
                    "locked": True,
                    "unlock_at": lockout_until,
                    "reason": "Too many failed login attempts"
                }
            else:
                await self.db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": update_data}
                )
                
                return {
                    "locked": False,
                    "remaining_attempts": self.MAX_LOGIN_ATTEMPTS - new_attempts
                }
    
    async def check_session_timeout(self, user_id: str) -> bool:
        """
        Check if user session has timed out
        
        Returns:
            True if session is valid, False if timed out
        """
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return False
        
        last_activity = user.get("last_activity")
        if not last_activity:
            # If no last activity, set it to now
            await self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_activity": datetime.utcnow()}}
            )
            return True
        
        # Check if session has timed out
        if datetime.utcnow() - last_activity > self.SESSION_TIMEOUT:
            return False
        
        return True
    
    async def update_last_activity(self, user_id: str):
        """Update user's last activity timestamp"""
        await self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
    
    async def rotate_refresh_token(self, user_id: str, current_refresh_token: str) -> Optional[str]:
        """
        Rotate refresh token if it's old enough
        
        Returns:
            New refresh token if rotated, None otherwise
        """
        from auth import create_refresh_token
        
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        
        # Check if refresh token needs rotation
        refresh_token_created = user.get("refresh_token_created_at")
        if not refresh_token_created:
            # If no creation timestamp, assume it's old and rotate
            new_token = create_refresh_token(data={"sub": user["usn"], "user_id": user_id})
            
            await self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "refresh_token": new_token,
                    "refresh_token_created_at": datetime.utcnow(),
                    "refresh_token_expiry": datetime.utcnow() + timedelta(days=7)
                }}
            )
            
            return new_token
        
        # Rotate if token is older than threshold
        if datetime.utcnow() - refresh_token_created > self.REFRESH_TOKEN_ROTATION_THRESHOLD:
            new_token = create_refresh_token(data={"sub": user["usn"], "user_id": user_id})
            
            await self.db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "refresh_token": new_token,
                    "refresh_token_created_at": datetime.utcnow(),
                    "refresh_token_expiry": datetime.utcnow() + timedelta(days=7)
                }}
            )
            
            return new_token
        
        return None
    
    async def get_session_info(self, user_id: str) -> Dict:
        """Get session information for user"""
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {}
        
        last_activity = user.get("last_activity", datetime.utcnow())
        time_until_timeout = self.SESSION_TIMEOUT - (datetime.utcnow() - last_activity)
        
        return {
            "last_activity": last_activity,
            "session_expires_at": last_activity + self.SESSION_TIMEOUT,
            "time_until_timeout_seconds": max(0, int(time_until_timeout.total_seconds())),
            "session_valid": time_until_timeout.total_seconds() > 0
        }
