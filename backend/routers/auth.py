"""
Authentication Routes
Handles user registration, login, logout, password reset, and 2FA
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime
import re

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

router = APIRouter(prefix="/api", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


def serialize_doc(doc):
    """Convert ObjectId to string"""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


@router.post("/register", response_model=UserResponse)
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
    
    # Create user
    user = {
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
    
    result = await database.users.insert_one(user)
    user["id"] = str(result.inserted_id)
    
    # Generate tokens
    access_token = create_access_token({"sub": str(result.inserted_id)})
    refresh_token = create_refresh_token({"sub": str(result.inserted_id)})
    
    return UserResponse(
        id=user["id"],
        usn=user["usn"],
        email=user["email"],
        department=user["department"],
        college=user["college"],
        year=user["year"],
        accessToken=access_token,
        refreshToken=refresh_token
    )


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
    
    # Generate tokens
    user_id = str(user["_id"])
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    return {
        "user": UserResponse(
            id=user_id,
            usn=user["usn"],
            email=user["email"],
            department=user["department"],
            college=user["college"],
            year=user["year"]
        ),
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
    
    # Store token with expiry (1 hour)
    await database.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
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
    
    # Update password and clear reset token
    await database.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "password": get_password_hash(data.newPassword),
            "resetToken": None,
            "resetTokenExpiry": None
        }}
    )
    
    return {"message": "Password has been reset successfully"}
