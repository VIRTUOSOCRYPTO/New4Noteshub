"""
User Routes
Handles user profile, settings, and statistics
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from fastapi.responses import FileResponse
import os
import secrets
from pathlib import Path
import uuid

from database import get_database
from auth import get_current_user_id, get_password_hash, verify_password
from models import UserResponse, UserSettingsUpdate, PasswordUpdate, UserStats

router = APIRouter(prefix="/api/user", tags=["Users"])

# Upload directory for profile pictures
PROFILE_DIR = "uploads/profile"
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def serialize_doc(doc):
    """Convert MongoDB document to API response format"""
    if doc and "_id" in doc:
        del doc["_id"]
    # Ensure 'id' field exists
    if doc and "id" not in doc:
        doc["id"] = str(uuid.uuid4())
    return doc


@router.get("")
async def get_user(
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Get current user information"""
    user = await database.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["id"],
        "usn": user["usn"],
        "email": user["email"],
        "department": user["department"],
        "college": user["college"],
        "year": user["year"],
        "profile_picture": user.get("profilePicture"),
        "created_at": user.get("createdAt", user.get("created_at")),
        "notify_new_notes": user.get("notify_new_notes", False),
        "notify_downloads": user.get("notify_downloads", False),
        "two_factor_enabled": user.get("two_factor_enabled", False)
    }


@router.patch("/settings")
async def update_settings(
    settings: UserSettingsUpdate,
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Update user settings"""
    update_data = settings.dict(exclude_unset=True)
    
    await database.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    user = await database.users.find_one({"id": user_id})
    return {
        "id": user["id"],
        "usn": user["usn"],
        "email": user["email"],
        "department": user["department"],
        "college": user["college"],
        "year": user["year"],
        "profile_picture": user.get("profilePicture"),
        "created_at": user.get("createdAt", user.get("created_at")),
        "notify_new_notes": user.get("notify_new_notes", False),
        "notify_downloads": user.get("notify_downloads", False),
        "two_factor_enabled": user.get("two_factor_enabled", False)
    }


@router.patch("/password")
async def update_password(
    data: PasswordUpdate,
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Update user password"""
    user = await database.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(data.currentPassword, user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    await database.users.update_one(
        {"id": user_id},
        {"$set": {"password": get_password_hash(data.newPassword)}}
    )
    
    return {"message": "Password updated successfully"}


@router.post("/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Upload user profile picture"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = f"profile_{secrets.token_urlsafe(16)}{file_ext}"
    file_path = os.path.join(PROFILE_DIR, unique_filename)
    
    # Save file
    os.makedirs(PROFILE_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update user record
    await database.users.update_one(
        {"id": user_id},
        {"$set": {"profilePicture": unique_filename}}
    )
    
    user = await database.users.find_one({"id": user_id})
    return {
        "id": user["id"],
        "usn": user["usn"],
        "email": user["email"],
        "department": user["department"],
        "college": user["college"],
        "year": user["year"],
        "profile_picture": user.get("profilePicture"),
        "created_at": user.get("createdAt", user.get("created_at")),
        "notify_new_notes": user.get("notify_new_notes", False),
        "notify_downloads": user.get("notify_downloads", False),
        "two_factor_enabled": user.get("two_factor_enabled", False)
    }


@router.get("/profile-picture/{filename}")
async def get_profile_picture(filename: str):
    """Get user profile picture"""
    file_path = os.path.join(PROFILE_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Profile picture not found")
    
    return FileResponse(path=file_path)


@router.get("/stats")
async def get_user_stats(
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Get user statistics"""
    # Count user's uploaded notes using 'userId' field
    upload_count = await database.notes.count_documents({"userId": user_id})
    
    # Get user creation date for days since joined
    user = await database.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from datetime import datetime
    created_at = user.get("createdAt", datetime.utcnow())
    days_since_joined = (datetime.utcnow() - created_at).days
    
    # Mock data for other stats (would need proper tracking in production)
    return {
        "uploadCount": upload_count,
        "downloadCount": 0,  # Would track in production
        "viewCount": 0,  # Would track in production
        "daysSinceJoined": days_since_joined,
        "previewCount": 0,  # Would track in production
        "uniqueSubjectsCount": 0,  # Would calculate in production
        "pagesVisited": 0  # Would track in production
    }
