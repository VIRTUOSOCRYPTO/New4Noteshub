"""
Enhanced Server with Security, Caching, and Storage Integrations
This file adds all the missing features to the NotesHub API
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
import os

# Import existing modules
from database import db, get_database
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user_id
)
from models import UserCreate, UserLogin
from bson import ObjectId

# Import new security and service modules
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.csrf_protection import CSRFProtectionMiddleware, generate_csrf_token
from middleware.rate_limit_per_user import PerUserRateLimitMiddleware, cleanup_rate_limits
from services.auth_security import AuthSecurityService
from services.cache_service import cache_service
from services.email_service import email_service
from services.storage_service import storage_service

import asyncio


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect_to_database()
    
    # Create upload directories
    os.makedirs("uploads/notes", exist_ok=True)
    os.makedirs("uploads/profile", exist_ok=True)
    
    # Start background tasks
    cleanup_task = asyncio.create_task(cleanup_rate_limits())
    
    print("✓ NotesHub API started successfully!")
    print("✓ Security headers enabled")
    print("✓ CSRF protection enabled")
    print("✓ Per-user rate limiting enabled")
    print("✓ Caching service initialized")
    print("✓ Email service initialized")
    print("✓ Storage service initialized")
    
    yield
    
    # Shutdown
    cleanup_task.cancel()
    await db.close_database_connection()
    print("✓ NotesHub API shut down gracefully")


# Initialize FastAPI app
app = FastAPI(
    title="NotesHub API",
    version="2.0.0",
    description="Academic Notes Sharing Platform with Enhanced Security",
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFProtectionMiddleware)
app.add_middleware(PerUserRateLimitMiddleware)

# Rate limiter (IP-based as backup)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-CSRF-Token"]
)

# Helper function
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


# ============================================================================
# HEALTH & SYSTEM ROUTES
# ============================================================================

@app.get("/")
@app.get("/api/health")
async def health_check():
    """Enhanced health check with system status"""
    return {
        "status": "ok",
        "message": "NotesHub API is running",
        "version": "2.0.0",
        "features": {
            "security_headers": True,
            "csrf_protection": True,
            "per_user_rate_limiting": True,
            "caching": cache_service.cache_enabled,
            "email": email_service.enabled,
            "cloud_storage": storage_service.storage_enabled
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/csrf-token")
async def get_csrf_token(request: Request):
    """Get CSRF token for authenticated requests"""
    auth_header = request.headers.get("Authorization", "")
    session_id = auth_header.split("Bearer ")[-1] if auth_header else ""
    
    token = generate_csrf_token(session_id)
    
    return {"csrfToken": token}


@app.get("/api/session-info")
async def get_session_info(
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get session information for timeout warnings"""
    auth_security = AuthSecurityService(database)
    session_info = await auth_security.get_session_info(user_id)
    
    return session_info


# ============================================================================
# ENHANCED AUTHENTICATION ROUTES
# ============================================================================

@app.post("/api/register")
@limiter.limit("10/15minutes")
async def register(
    request: Request,
    user_data: UserCreate,
    database = Depends(get_database)
):
    """Enhanced registration with welcome email"""
    # Existing validation logic...
    if user_data.password != user_data.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    usn_upper = user_data.usn.upper()
    
    # Check if user exists
    existing_user = await database.users.find_one({"usn": usn_upper})
    if existing_user:
        raise HTTPException(status_code=409, detail="USN already exists")
    
    existing_email = await database.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_doc = {
        "usn": usn_upper,
        "email": user_data.email,
        "department": user_data.department,
        "college": user_data.college,
        "year": user_data.year,
        "password_hash": hashed_password,
        "profile_picture": None,
        "notify_new_notes": True,
        "notify_downloads": False,
        "created_at": datetime.utcnow(),
        "two_factor_enabled": False,
        "login_attempts": 0,
        "account_locked_until": None,
        "last_activity": datetime.utcnow()
    }
    
    result = await database.users.insert_one(user_doc)
    user_doc = await database.users.find_one({"_id": result.inserted_id})
    
    # Send welcome email (async, non-blocking)
    asyncio.create_task(
        email_service.send_welcome_email(user_data.email, usn_upper)
    )
    
    return serialize_doc(user_doc)


@app.post("/api/login")
@limiter.limit("10/15minutes")
async def login(
    request: Request,
    login_data: UserLogin,
    database = Depends(get_database)
):
    """Enhanced login with account lockout and security checks"""
    auth_security = AuthSecurityService(database)
    
    # Check if account is locked
    lockout_check = await auth_security.record_login_attempt(login_data.usn, success=False)
    if lockout_check.get("locked"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked due to too many failed attempts. Try again after {lockout_check['unlock_at']}"
        )
    
    # Find user
    user = await database.users.find_one({"usn": login_data.usn.upper()})
    if not user:
        raise HTTPException(status_code=401, detail="USN not registered")
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        # Record failed attempt
        await auth_security.record_login_attempt(login_data.usn, success=False)
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # Record successful login
    await auth_security.record_login_attempt(login_data.usn, success=True)
    
    # Create tokens
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user["usn"], "user_id": user_id})
    
    # Check if refresh token needs rotation
    new_refresh_token = await auth_security.rotate_refresh_token(user_id, "")
    if not new_refresh_token:
        # Create new refresh token if none exists
        from auth import create_refresh_token
        new_refresh_token = create_refresh_token(data={"sub": user["usn"], "user_id": user_id})
        
        await database.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "refresh_token": new_refresh_token,
                "refresh_token_created_at": datetime.utcnow()
            }}
        )
    
    # Update last activity
    await auth_security.update_last_activity(user_id)
    
    user_data = serialize_doc(user)
    del user_data["password_hash"]
    
    return {
        "user": user_data,
        "accessToken": access_token,
        "refreshToken": new_refresh_token
    }


@app.post("/api/forgot-password")
@limiter.limit("5/15minutes")
async def forgot_password(
    request: Request,
    data: dict,
    database = Depends(get_database)
):
    """Enhanced password reset with email"""
    email = data.get("email")
    user = await database.users.find_one({"email": email})
    
    if user:
        from auth import generate_reset_token
        reset_token = generate_reset_token()
        reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        await database.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_expiry": reset_token_expiry
            }}
        )
        
        # Send reset email
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        asyncio.create_task(
            email_service.send_password_reset_email(
                email,
                user["usn"],
                reset_link
            )
        )
        
        return {"message": "Password reset email sent"}
    
    return {"message": "If account exists, reset email has been sent"}


# ============================================================================
# ENHANCED NOTES ROUTES WITH CACHING
# ============================================================================

@app.get("/api/notes")
async def get_notes(
    department: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    page: int = 1,
    limit: int = 20,
    database = Depends(get_database)
):
    """Get notes with pagination and caching"""
    # Build cache key
    filters = {
        "department": department,
        "subject": subject,
        "year": year,
        "page": page,
        "limit": limit
    }
    
    # Try to get from cache
    cached_notes = await cache_service.get_notes_list(filters)
    if cached_notes:
        return {
            "notes": cached_notes,
            "from_cache": True,
            "page": page,
            "limit": limit
        }
    
    # Build query
    query = {"is_approved": True}
    if department:
        query["department"] = department
    if subject:
        query["subject"] = subject
    if year:
        query["year"] = year
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Fetch with pagination
    notes_cursor = database.notes.find(query).sort("uploaded_at", -1).skip(skip).limit(limit)
    notes = await notes_cursor.to_list(length=limit)
    
    # Get total count
    total = await database.notes.count_documents(query)
    
    serialized_notes = [serialize_doc(note) for note in notes]
    
    # Cache the results
    await cache_service.set_notes_list(filters, serialized_notes)
    
    return {
        "notes": serialized_notes,
        "from_cache": False,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit
    }


print("✓ Enhanced server module loaded successfully")
