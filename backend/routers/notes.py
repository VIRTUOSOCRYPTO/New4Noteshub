"""
Notes Routes
Handles note upload, download, search, and moderation
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
import os
import shutil
import secrets
from pathlib import Path
import filetype
from bson import ObjectId

from database import get_database
from auth import get_current_user_id
from models import (
    NoteCreate, NoteResponse, NoteInDB, NotesSearchParams,
    FlagNoteRequest, ReviewNoteRequest
)

router = APIRouter(prefix="/api/notes", tags=["Notes"])

# Upload directory
UPLOAD_DIR = "uploads/notes"
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def serialize_doc(doc):
    """Convert ObjectId to string"""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    if doc and "userId" in doc:
        doc["userId"] = str(doc["userId"])
    return doc


@router.get("", response_model=List[NoteResponse])
async def get_notes(
    department: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    database=Depends(get_database)
):
    """Get notes with optional filters"""
    query = {}
    
    if department:
        query["department"] = department
    if subject:
        query["subject"] = subject
    if year:
        query["year"] = year
    
    notes = await database.notes.find(query).sort("uploadedAt", -1).to_list(100)
    return [serialize_doc(note) for note in notes]


@router.post("", response_model=NoteResponse, status_code=201)
async def upload_note(
    title: str = Form(...),
    subject: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Upload a new note"""
    # Get user info
    user = await database.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file and check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    unique_filename = f"{secrets.token_urlsafe(16)}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create note record
    note = {
        "title": title,
        "subject": subject,
        "department": user["department"],
        "year": user["year"],
        "usn": user["usn"],
        "userId": ObjectId(user_id),
        "filename": unique_filename,
        "originalFilename": file.filename,
        "uploadedAt": datetime.utcnow(),
        "viewCount": 0,
        "downloadCount": 0,
        "isFlagged": False
    }
    
    result = await database.notes.insert_one(note)
    note["id"] = str(result.inserted_id)
    note["userId"] = str(note["userId"])
    
    return serialize_doc(note)


@router.get("/{note_id}/download")
async def download_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Download a note file"""
    # Find note
    note = await database.notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if file exists
    file_path = os.path.join(UPLOAD_DIR, note["filename"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Increment download count
    await database.notes.update_one(
        {"_id": ObjectId(note_id)},
        {"$inc": {"downloadCount": 1}}
    )
    
    return FileResponse(
        path=file_path,
        filename=note["originalFilename"],
        media_type="application/octet-stream"
    )


@router.get("/{note_id}/view")
async def view_note(
    note_id: str,
    database=Depends(get_database)
):
    """Increment view count"""
    result = await database.notes.update_one(
        {"_id": ObjectId(note_id)},
        {"$inc": {"viewCount": 1}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"success": True}


@router.post("/{note_id}/flag")
async def flag_note(
    note_id: str,
    data: FlagNoteRequest,
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Flag a note for review"""
    # Check if note exists
    note = await database.notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update note
    await database.notes.update_one(
        {"_id": ObjectId(note_id)},
        {"$set": {
            "isFlagged": True,
            "flagReason": data.reason,
            "flaggedBy": ObjectId(user_id),
            "flaggedAt": datetime.utcnow()
        }}
    )
    
    return {"message": "Note has been flagged for review"}


@router.get("/flagged")
async def get_flagged_notes(
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Get all flagged notes"""
    notes = await database.notes.find({"isFlagged": True}).to_list(100)
    return [serialize_doc(note) for note in notes]


@router.post("/{note_id}/review")
async def review_note(
    note_id: str,
    data: ReviewNoteRequest,
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Review a flagged note"""
    note = await database.notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if not note.get("isFlagged"):
        raise HTTPException(status_code=400, detail="Note is not flagged")
    
    if data.approved:
        # Unflag the note
        await database.notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": {
                "isFlagged": False,
                "flagReason": None,
                "reviewedAt": datetime.utcnow(),
                "reviewedBy": ObjectId(user_id)
            }}
        )
        return {"message": "Note has been approved"}
    else:
        # Delete the note and file
        file_path = os.path.join(UPLOAD_DIR, note["filename"])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        await database.notes.delete_one({"_id": ObjectId(note_id)})
        return {"message": "Note has been rejected and deleted"}
