"""
User Service
Business logic for user operations
"""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from auth import get_password_hash, verify_password


class UserService:
    """Service for user-related operations"""
    
    def __init__(self, database):
        self.db = database
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        
        user_doc = {
            "id": user_id,
            "usn": user_data["usn"].upper(),
            "email": user_data["email"],
            "department": user_data["department"],
            "college": user_data["college"],
            "year": user_data["year"],
            "password_hash": get_password_hash(user_data["password"]),
            "profile_picture": None,
            "notify_new_notes": True,
            "notify_downloads": False,
            "created_at": datetime.utcnow(),
            "two_factor_enabled": False,
            "two_factor_secret": None,
            "refresh_token": None,
            "refresh_token_expiry": None,
            "reset_token": None,
            "reset_token_expiry": None
        }
        
        await self.db.users.insert_one(user_doc)
        return user_doc
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return await self.db.users.find_one({"id": user_id})
    
    async def get_user_by_usn(self, usn: str) -> Optional[Dict[str, Any]]:
        """Get user by USN"""
        return await self.db.users.find_one({"usn": usn.upper()})
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return await self.db.users.find_one({"email": email})
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password"""
        hashed_password = get_password_hash(new_password)
        return await self.update_user(user_id, {"password_hash": hashed_password})
    
    async def verify_user_password(self, user: Dict[str, Any], password: str) -> bool:
        """Verify user password"""
        return verify_password(password, user["password_hash"])
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return {}
        
        # Count user's uploads using 'userId' field
        upload_count = await self.db.notes.count_documents({"userId": user_id})
        
        # Calculate days since joined
        days_since_joined = (datetime.utcnow() - user["created_at"]).days
        
        # Get total downloads and views for user's notes
        pipeline = [
            {"$match": {"userId": user_id}},
            {"$group": {
                "_id": None,
                "total_downloads": {"$sum": "$download_count"},
                "total_views": {"$sum": "$view_count"}
            }}
        ]
        
        result = await self.db.notes.aggregate(pipeline).to_list(1)
        stats = result[0] if result else {"total_downloads": 0, "total_views": 0}
        
        return {
            "uploadCount": upload_count,
            "downloadCount": stats.get("total_downloads", 0),
            "viewCount": stats.get("total_views", 0),
            "daysSinceJoined": days_since_joined,
            "previewCount": 0,
            "uniqueSubjectsCount": 0,
            "pagesVisited": 0
        }
