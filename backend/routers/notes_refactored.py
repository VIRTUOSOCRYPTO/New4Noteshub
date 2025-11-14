"""
Notes Routes (Refactored)
Clean route handlers that delegate to service layer
Follows Single Responsibility Principle
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional

from database import get_database
from auth import get_current_user_id
from models import NoteResponse, FlagNoteRequest, ReviewNoteRequest
from services.note_service import NoteService
from services.file_service import get_file_service
from repositories.note_repository import get_note_repository
from utils.serializers import serialize_doc, serialize_docs
from exceptions import NotFoundError, FileUploadError, AuthorizationError

router = APIRouter(prefix="/api/notes", tags=["Notes"])


def get_note_service(database=Depends(get_database)) -> NoteService:
    """Dependency injection for note service"""
    return NoteService(database)


@router.get("", response_model=List[NoteResponse])
async def get_notes(
    department: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    note_service: NoteService = Depends(get_note_service)
):
    """Get notes with optional filters"""
    notes = await note_service.get_notes(
        department=department,
        subject=subject,
        year=year,
        skip=skip,
        limit=limit
    )
    return serialize_docs(notes)


@router.post("", response_model=NoteResponse, status_code=201)
async def upload_note(
    title: str = Form(...),
    subject: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    database=Depends(get_database)
):
    """Upload a new note"""
    note_service = NoteService(database)
    file_service = get_file_service()
    
    # Get user info
    user = await database.users.find_one({"_id": user_id})
    if not user:
        raise NotFoundError("User", user_id)
    
    # Save file (file service handles validation)
    unique_filename, original_filename = await file_service.save_file(file)
    
    # Create note record
    note_data = {
        "user_id": user_id,
        "usn": user.get("usn"),
        "title": title,
        "subject": subject,
        "department": user.get("department"),
        "year": user.get("year"),
        "filename": unique_filename,
        "original_filename": original_filename
    }
    
    note = await note_service.create_note(note_data)
    return serialize_doc(note)


@router.get("/{note_id}/download")
async def download_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id),
    note_service: NoteService = Depends(get_note_service)
):
    """Download a note file"""
    file_service = get_file_service()
    
    # Get note
    note = await note_service.get_note_by_id(note_id)
    if not note:
        raise NotFoundError("Note", note_id)
    
    # Check if file exists
    if not file_service.file_exists(note["filename"]):
        raise NotFoundError("File", note["filename"])
    
    # Increment download count
    await note_service.increment_download_count(note_id)
    
    # Return file
    file_path = file_service.get_file_path(note["filename"])
    return FileResponse(
        path=file_path,
        filename=note.get("original_filename", note["filename"]),
        media_type="application/octet-stream"
    )


@router.get("/{note_id}/view")
async def view_note(
    note_id: str,
    note_service: NoteService = Depends(get_note_service)
):
    """Increment view count"""
    success = await note_service.increment_view_count(note_id)
    if not success:
        raise NotFoundError("Note", note_id)
    
    return {"success": True}


@router.post("/{note_id}/flag")
async def flag_note(
    note_id: str,
    data: FlagNoteRequest,
    user_id: str = Depends(get_current_user_id),
    note_service: NoteService = Depends(get_note_service)
):
    """Flag a note for review"""
    # Check if note exists
    note = await note_service.get_note_by_id(note_id)
    if not note:
        raise NotFoundError("Note", note_id)
    
    # Flag the note
    success = await note_service.flag_note(note_id, data.reason)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to flag note")
    
    return {"message": "Note has been flagged for review"}


@router.get("/flagged", response_model=List[NoteResponse])
async def get_flagged_notes(
    user_id: str = Depends(get_current_user_id),
    note_service: NoteService = Depends(get_note_service)
):
    """Get all flagged notes (admin only)"""
    notes = await note_service.get_flagged_notes()
    return serialize_docs(notes)


@router.post("/{note_id}/review")
async def review_note(
    note_id: str,
    data: ReviewNoteRequest,
    user_id: str = Depends(get_current_user_id),
    note_service: NoteService = Depends(get_note_service)
):
    """Review a flagged note (admin only)"""
    file_service = get_file_service()
    
    # Get note
    note = await note_service.get_note_by_id(note_id)
    if not note:
        raise NotFoundError("Note", note_id)
    
    if not note.get("is_flagged", False):
        raise HTTPException(status_code=400, detail="Note is not flagged")
    
    if data.approved:
        # Approve the note
        success = await note_service.approve_note(note_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to approve note")
        return {"message": "Note has been approved"}
    else:
        # Reject and delete
        file_service.delete_file(note["filename"])
        success = await note_service.delete_note(note_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete note")
        return {"message": "Note has been rejected and deleted"}
