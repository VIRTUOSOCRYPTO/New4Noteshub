from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime, timedelta
import os
import shutil
import secrets
from pathlib import Path
import filetype
import re

from database import db, get_database
from auth import (
    get_password_hash, verify_password, create_access_token, create_refresh_token,
    verify_token, get_current_user_id, generate_2fa_secret, generate_2fa_qr_code,
    verify_2fa_token, generate_reset_token
)
from models import (
    UserCreate, UserLogin, UserResponse, UserInDB, Token,
    NoteCreate, NoteResponse, NoteInDB, NotesSearchParams,
    UserSettingsUpdate, PasswordUpdate, ForgotPasswordRequest,
    ResetPasswordRequest, FlagNoteRequest, ReviewNoteRequest,
    TwoFactorSetup, TwoFactorVerify, GoogleAuthRequest,
    UserStats, BookmarkCreate, MessageCreate, DrawingCreate,
    VALID_DEPARTMENTS, DEPARTMENT_CODES
)
from bson import ObjectId

# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect_to_database()
    
    # Create upload directories
    os.makedirs("uploads/notes", exist_ok=True)
    os.makedirs("uploads/profile", exist_ok=True)
    
    print("NotesHub API started successfully!")
    
    yield
    
    # Shutdown
    await db.close_database_connection()

# Initialize FastAPI app
app = FastAPI(title="NotesHub API", version="1.0.0", lifespan=lifespan)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# ============================================================================
# HEALTH CHECK ROUTES
# ============================================================================

@app.get("/")
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "message": "NotesHub API is running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/test")
@app.get("/api/test")
async def test_cors():
    return {
        "message": "CORS is working!",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.post("/api/register", response_model=UserResponse)
@limiter.limit("10/15minutes")
async def register(request: Request, user_data: UserCreate, database = Depends(get_database)):
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
        "two_factor_secret": None,
        "refresh_token": None,
        "refresh_token_expiry": None,
        "reset_token": None,
        "reset_token_expiry": None
    }
    
    result = await database.users.insert_one(user_doc)
    user_doc = await database.users.find_one({"_id": result.inserted_id})
    
    return serialize_doc(user_doc)

@app.post("/api/login")
@limiter.limit("10/15minutes")
async def login(request: Request, login_data: UserLogin, database = Depends(get_database)):
    # Find user
    user = await database.users.find_one({"usn": login_data.usn.upper()})
    if not user:
        raise HTTPException(status_code=401, detail="USN not registered. Please register first.")
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")
    
    # Check if 2FA is enabled
    if user.get("two_factor_enabled"):
        return {
            "twoFactorRequired": True,
            "message": "Two-factor authentication required",
            "tempUserId": str(user["_id"])
        }
    
    # Create tokens
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user["usn"], "user_id": user_id})
    refresh_token = create_refresh_token(data={"sub": user["usn"], "user_id": user_id})
    
    # Store refresh token
    await database.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "refresh_token": refresh_token,
            "refresh_token_expiry": datetime.utcnow() + timedelta(days=7)
        }}
    )
    
    user_data = serialize_doc(user)
    del user_data["password_hash"]
    
    return {
        "user": user_data,
        "accessToken": access_token,
        "refreshToken": refresh_token
    }

@app.post("/api/logout")
async def logout(user_id: str = Depends(get_current_user_id), database = Depends(get_database)):
    # Clear refresh token
    await database.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"refresh_token": None, "refresh_token_expiry": None}}
    )
    return {"message": "Logged out successfully"}

@app.get("/api/user", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(get_current_user_id), database = Depends(get_database)):
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = serialize_doc(user)
    del user_data["password_hash"]
    return user_data

# ============================================================================
# PASSWORD RESET ROUTES
# ============================================================================

@app.post("/api/forgot-password")
@limiter.limit("5/15minutes")
async def forgot_password(request: Request, data: ForgotPasswordRequest, database = Depends(get_database)):
    user = await database.users.find_one({"email": data.email})
    
    if user:
        # Generate reset token
        reset_token = generate_reset_token()
        reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        await database.users.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_expiry": reset_token_expiry
            }}
        )
        
        # In production, send email here
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        print(f"Password reset link: {reset_link}")
        
        return {
            "message": "Password reset email sent",
            "resetLink": reset_link  # Remove in production
        }
    
    # Don't reveal if email exists
    return {"message": "If a matching account was found, a password reset link has been sent."}

@app.post("/api/reset-password")
async def reset_password(data: ResetPasswordRequest, database = Depends(get_database)):
    if data.newPassword != data.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Find user with valid token
    user = await database.users.find_one({
        "reset_token": data.token,
        "reset_token_expiry": {"$gt": datetime.utcnow()}
    })
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Update password and clear token
    hashed_password = get_password_hash(data.newPassword)
    await database.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "password_hash": hashed_password,
            "reset_token": None,
            "reset_token_expiry": None
        }}
    )
    
    return {"message": "Password has been reset successfully"}

# ============================================================================
# NOTES ROUTES
# ============================================================================

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadFile) -> bool:
    # Check extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    return True

@app.get("/api/notes", response_model=List[NoteResponse])
async def get_notes(
    department: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    showAllDepartments: bool = False,
    showAllColleges: bool = False,
    showAllYears: bool = False,
    user_id: Optional[str] = Depends(lambda: None),
    database = Depends(get_database)
):
    # Build query
    query = {"is_approved": True}
    
    if department:
        query["department"] = department
    if subject:
        query["subject"] = subject
    if year:
        query["year"] = year
    
    # Fetch notes
    notes_cursor = database.notes.find(query).sort("uploaded_at", -1)
    notes = await notes_cursor.to_list(length=100)
    
    return [serialize_doc(note) for note in notes]

@app.post("/api/notes", response_model=NoteResponse, status_code=201)
@limiter.limit("20/hour")
async def upload_note(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    subject: str = Form(...),
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    # Validate file
    if not validate_file(file):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Get user
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix
    unique_filename = f"{secrets.token_urlsafe(16)}{file_ext}"
    file_path = f"uploads/notes/{unique_filename}"
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create note document
    note_doc = {
        "user_id": user_id,
        "usn": user["usn"],
        "title": title,
        "department": user["department"],
        "year": user["year"],
        "subject": subject,
        "filename": unique_filename,
        "original_filename": file.filename,
        "uploaded_at": datetime.utcnow(),
        "is_flagged": False,
        "flag_reason": None,
        "reviewed_at": None,
        "is_approved": True,
        "download_count": 0,
        "view_count": 0
    }
    
    result = await database.notes.insert_one(note_doc)
    note_doc = await database.notes.find_one({"_id": result.inserted_id})
    
    return serialize_doc(note_doc)

@app.get("/api/notes/{note_id}/download")
async def download_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    # Get note
    note = await database.notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if user's year matches note's year
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if user["year"] != note["year"]:
        raise HTTPException(
            status_code=403,
            detail="You can only download notes from your academic year"
        )
    
    # Increment download count
    await database.notes.update_one(
        {"_id": ObjectId(note_id)},
        {"$inc": {"download_count": 1}}
    )
    
    file_path = f"uploads/notes/{note['filename']}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=note["original_filename"],
        media_type="application/octet-stream"
    )

@app.get("/api/notes/{note_id}/view")
async def view_note(note_id: str, database = Depends(get_database)):
    # Increment view count
    await database.notes.update_one(
        {"_id": ObjectId(note_id)},
        {"$inc": {"view_count": 1}}
    )
    return {"success": True}

# ============================================================================
# CONTENT MODERATION ROUTES
# ============================================================================

@app.post("/api/notes/{note_id}/flag")
async def flag_note(
    note_id: str,
    flag_data: FlagNoteRequest,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    note = await database.notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if user["department"] != note["department"]:
        raise HTTPException(
            status_code=403,
            detail="You can only flag notes from your own department"
        )
    
    await database.notes.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {
            "is_flagged": True,
            "flag_reason": flag_data.reason
        }}
    )
    
    return {"message": "Note has been flagged for review"}

@app.get("/api/notes/flagged")
async def get_flagged_notes(
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    notes_cursor = database.notes.find({"is_flagged": True})
    notes = await notes_cursor.to_list(length=100)
    return [serialize_doc(note) for note in notes]

@app.post("/api/notes/{note_id}/review")
async def review_note(
    note_id: str,
    review_data: ReviewNoteRequest,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    note = await database.notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if not note.get("is_flagged"):
        raise HTTPException(status_code=400, detail="This note is not flagged for review")
    
    if review_data.approved:
        await database.notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": {
                "is_flagged": False,
                "is_approved": True,
                "reviewed_at": datetime.utcnow()
            }}
        )
        return {"message": "Note has been approved and is now available"}
    else:
        # Delete the file
        file_path = f"uploads/notes/{note['filename']}"
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the note
        await database.notes.delete_one({"_id": ObjectId(note_id)})
        return {"message": "Note has been rejected and removed from the system"}

# ============================================================================
# USER SETTINGS ROUTES
# ============================================================================

@app.patch("/api/user/settings", response_model=UserResponse)
async def update_settings(
    settings: UserSettingsUpdate,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    update_data = {}
    if settings.notify_new_notes is not None:
        update_data["notify_new_notes"] = settings.notify_new_notes
    if settings.notify_downloads is not None:
        update_data["notify_downloads"] = settings.notify_downloads
    
    await database.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    user_data = serialize_doc(user)
    del user_data["password_hash"]
    return user_data

@app.patch("/api/user/password")
async def update_password(
    password_data: PasswordUpdate,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    if password_data.newPassword != password_data.confirmNewPassword:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not verify_password(password_data.currentPassword, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    hashed_password = get_password_hash(password_data.newPassword)
    await database.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": hashed_password}}
    )
    
    return {"message": "Password updated successfully"}

# ============================================================================
# PROFILE PICTURE ROUTES
# ============================================================================

@app.post("/api/user/profile-picture", response_model=UserResponse)
async def upload_profile_picture(
    profilePicture: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if profilePicture.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Read file content
    file_content = await profilePicture.read()
    if len(file_content) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File too large")
    
    # Generate unique filename
    file_ext = Path(profilePicture.filename).suffix
    unique_filename = f"profile_{secrets.token_urlsafe(16)}{file_ext}"
    file_path = f"uploads/profile/{unique_filename}"
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Update user
    await database.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"profile_picture": unique_filename}}
    )
    
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    user_data = serialize_doc(user)
    del user_data["password_hash"]
    return user_data

@app.get("/api/user/profile-picture/{filename}")
async def get_profile_picture(filename: str):
    # Validate filename format
    if not re.match(r'^profile_[\w\-]+\.(jpg|jpeg|png|gif|webp)$', filename, re.IGNORECASE):
        raise HTTPException(status_code=400, detail="Invalid filename format")
    
    file_path = f"uploads/profile/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Profile picture not found")
    
    return FileResponse(path=file_path)

# ============================================================================
# USER STATS ROUTES
# ============================================================================

@app.get("/api/user/stats", response_model=UserStats)
async def get_user_stats(
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get upload count
    upload_count = await database.notes.count_documents({"user_id": user_id})
    
    # Calculate days since joined
    days_since_joined = (datetime.utcnow() - user["created_at"]).days
    
    # Mock data for demo (in production, track these properly)
    return {
        "uploadCount": upload_count,
        "downloadCount": 0,
        "viewCount": 0,
        "daysSinceJoined": days_since_joined,
        "previewCount": 0,
        "uniqueSubjectsCount": 0,
        "pagesVisited": 0
    }

# ============================================================================
# WEBSOCKET FOR DRAWING COLLABORATION
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, drawing_id: str):
        await websocket.accept()
        if drawing_id not in self.active_connections:
            self.active_connections[drawing_id] = []
        self.active_connections[drawing_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, drawing_id: str):
        if drawing_id in self.active_connections:
            self.active_connections[drawing_id].remove(websocket)
            if not self.active_connections[drawing_id]:
                del self.active_connections[drawing_id]
    
    async def broadcast(self, message: dict, drawing_id: str, exclude: WebSocket = None):
        if drawing_id in self.active_connections:
            for connection in self.active_connections[drawing_id]:
                if connection != exclude:
                    await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    drawing_id = None
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "join" and data.get("drawingId"):
                drawing_id = data["drawingId"]
                if drawing_id not in manager.active_connections:
                    manager.active_connections[drawing_id] = []
                manager.active_connections[drawing_id].append(websocket)
                
                await websocket.send_json({
                    "type": "joined",
                    "drawingId": drawing_id,
                    "clients": len(manager.active_connections[drawing_id])
                })
            
            elif data.get("type") == "draw" and drawing_id:
                await manager.broadcast(
                    {"type": "draw", "drawData": data.get("drawData")},
                    drawing_id,
                    exclude=websocket
                )
    
    except WebSocketDisconnect:
        if drawing_id:
            manager.disconnect(websocket, drawing_id)
            await manager.broadcast(
                {"type": "clientLeft", "clients": len(manager.active_connections.get(drawing_id, []))},
                drawing_id
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
