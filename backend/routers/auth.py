"""
Authentication Routes
Handles user registration, login, logout, password reset, and 2FA
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime
import re
import uuid

from database import get_database
from auth import (
    get_password_hash, verify_password, create_access_token, create_refresh_token,
    verify_token, get_current_user_id, generate_reset_token
)
from models import (
    UserCreate, UserLogin, UserResponse, Token,
    ForgotPasswordRequest, ResetPasswordRequest,
    DEPARTMENT_CODES
)


async def initialize_user_gamification(database, user_id: str, usn: str):
    """Initialize gamification data for a new user"""
    import random
    import string
    
    # Generate referral code
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    referral_code = f"{usn[-4:]}{random_chars}".upper()
    
    # Ensure referral code uniqueness
    existing = await database.referrals.find_one({"referral_code": referral_code})
    while existing:
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        referral_code = f"{usn[-4:]}{random_chars}".upper()
        existing = await database.referrals.find_one({"referral_code": referral_code})
    
    # Initialize user_points
    await database.user_points.insert_one({
        "user_id": user_id,
        "total_points": 0,
        "level": 1,
        "level_name": "Newbie",
        "points_history": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    # Initialize streaks
    await database.streaks.insert_one({
        "user_id": user_id,
        "current_streak": 0,
        "longest_streak": 0,
        "last_activity_date": None,
        "total_activities": 0,
        "created_at": datetime.utcnow()
    })
    
    # Initialize referrals
    await database.referrals.insert_one({
        "user_id": user_id,
        "referral_code": referral_code,
        "referred_users": [],
        "total_referrals": 0,
        "rewards_earned": {
            "bonus_downloads": 0,
            "ai_access_days": 0,
            "premium_days": 0
        },
        "created_at": datetime.utcnow()
    })
    
    print(f"✅ Initialized gamification for user {user_id} with referral code {referral_code}")

router = APIRouter(prefix="/api", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


def serialize_doc(doc):
    """Convert MongoDB document to API response format"""
    if doc and "_id" in doc:
        del doc["_id"]
    # Ensure 'id' field exists
    if doc and "id" not in doc:
        doc["id"] = str(uuid.uuid4())
    return doc


@router.post("/register")
@limiter.limit("10/15minutes")
async def register(request: Request, user_data: UserCreate, database=Depends(get_database)):
    """Register a new user"""
    # Check if passwords match
    if user_data.password != user_data.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Validate USN department code matches selected department
    usn_upper = user_data.usn.upper()
    standard_pattern = re.compile(r'^[0-9][A-Za-z]{2}[0-9]{2}([A-Za-z]{2})[0-9]{3}$')
    short_pattern = re.compile(r'^[0-9]{2}([A-Za-z]{2})[0-9]{3}$')
    
    match = standard_pattern.match(usn_upper) or short_pattern.match(usn_upper)
    if match:
        usn_dept_code = match.group(1)
        expected_dept = DEPARTMENT_CODES.get(usn_dept_code)
        if expected_dept and expected_dept != user_data.department:
            raise HTTPException(
                status_code=400,
                detail=f"USN department code '{usn_dept_code}' doesn't match selected department '{user_data.department}'"
            )
    
    # Check if user already exists
    existing_user = await database.users.find_one({"usn": usn_upper})
    if existing_user:
        raise HTTPException(status_code=409, detail="USN already exists. Please login instead.")
    
    existing_email = await database.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered.")
    
    # Generate UUID for new user
    user_id = str(uuid.uuid4())
    
    # Create user
    user = {
        "id": user_id,
        "usn": usn_upper,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "department": user_data.department,
        "college": user_data.college,
        "year": user_data.year,
        "notifyNewNotes": True,
        "notifyDownloads": False,
        "createdAt": datetime.utcnow()
    }
    
    await database.users.insert_one(user)
    
    # Initialize gamification data (points, streaks, referrals)
    try:
        await initialize_user_gamification(database, user_id, usn_upper)
    except Exception as e:
        print(f"Warning: Failed to initialize gamification for {user_id}: {e}")
    
    # Generate tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    # Return user data with tokens separately
    return {
        "id": user_id,
        "usn": user["usn"],
        "email": user["email"],
        "department": user["department"],
        "college": user["college"],
        "year": user["year"],
        "accessToken": access_token,
        "refreshToken": refresh_token
    }


@router.post("/login")
@limiter.limit("10/15minutes")
async def login(request: Request, user_data: UserLogin, database=Depends(get_database)):
    """User login"""
    usn_upper = user_data.usn.upper()
    
    # Find user
    user = await database.users.find_one({"usn": usn_upper})
    if not user:
        raise HTTPException(status_code=401, detail="USN not registered. Please register first.")
    
    # Verify password
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")
    
    # Get user ID from 'id' field or generate if missing
    user_id = user.get("id")
    if not user_id:
        user_id = str(uuid.uuid4())
        await database.users.update_one(
            {"usn": usn_upper},
            {"$set": {"id": user_id}}
        )
    
    # Generate tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    return {
        "user": {
            "id": user_id,
            "usn": user["usn"],
            "email": user["email"],
            "department": user["department"],
            "college": user["college"],
            "year": user["year"]
        },
        "accessToken": access_token,
        "refreshToken": refresh_token
    }


@router.post("/logout")
async def logout():
    """User logout"""
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
@limiter.limit("5/hour")
async def forgot_password(request: Request, data: ForgotPasswordRequest, database=Depends(get_database)):
    """Initiate password reset"""
    user = await database.users.find_one({"email": data.email})
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If a matching account was found, a password reset link has been sent."}
    
    # Generate reset token
    reset_token = generate_reset_token()
    
    # Get user ID
    user_id = user.get("id")
    if not user_id:
        user_id = str(uuid.uuid4())
    
    # Store token with expiry (1 hour)
    query = {"id": user_id} if user_id else {"_id": user["_id"]}
    await database.users.update_one(
        query,
        {"$set": {
            "id": user_id,
            "resetToken": reset_token,
            "resetTokenExpiry": datetime.utcnow().timestamp() + 3600
        }}
    )
    
    # In production, send email with reset link
    # For demo, return the token
    return {
        "message": "Password reset email sent",
        "resetToken": reset_token  # Remove this in production
    }


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, database=Depends(get_database)):
    """Complete password reset"""
    # Find user with valid token
    user = await database.users.find_one({
        "resetToken": data.token,
        "resetTokenExpiry": {"$gt": datetime.utcnow().timestamp()}
    })
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Get user ID
    user_id = user.get("id")
    if not user_id:
        user_id = str(uuid.uuid4())
    
    # Update password and clear reset token
    query = {"id": user_id} if user_id else {"_id": user["_id"]}
    await database.users.update_one(
        query,
        {"$set": {
            "id": user_id,
            "password": get_password_hash(data.newPassword),
            "resetToken": None,
            "resetTokenExpiry": None
        }}
    )
    
    return {"message": "Password has been reset successfully"}
