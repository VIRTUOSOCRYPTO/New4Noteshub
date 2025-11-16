from fastapi import HTTPException, status, Depends
from typing import Optional
from auth import get_current_user_id
from database import get_database
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Admin user IDs - configure these in environment
import os

ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "admin@noteshub.app").split(",")
ADMIN_USNS = os.getenv("ADMIN_USNS", "").split(",")

# Debug logging
print(f"🔐 Admin Auth Module Loaded - ADMIN_EMAILS: {ADMIN_EMAILS}")


async def require_admin(user_id: str = Depends(get_current_user_id), database = Depends(get_database)):
    """
    Dependency that ensures the current user is an admin.
    Raises 403 if user is not an admin.
    """
    # Try to find user by UUID id field first, then by ObjectId
    user = await database.users.find_one({"id": user_id})
    if not user:
        try:
            user = await database.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is admin by email or USN
    is_admin = (
        user.get("email") in ADMIN_EMAILS or
        user.get("usn") in ADMIN_USNS or
        user.get("is_admin", False)  # Database flag
    )
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user_id


async def get_admin_status(user_id: str = Depends(get_current_user_id), database = Depends(get_database)) -> bool:
    """
    Check if current user is an admin.
    Returns True if admin, False otherwise.
    """
    try:
        # Try to find user by UUID id field first, then by ObjectId
        user = await database.users.find_one({"id": user_id})
        if not user:
            try:
                user = await database.users.find_one({"_id": ObjectId(user_id)})
            except:
                pass
        
        if not user:
            return False
        
        return (
            user.get("email") in ADMIN_EMAILS or
            user.get("usn") in ADMIN_USNS or
            user.get("is_admin", False)
        )
    except:
        return False
