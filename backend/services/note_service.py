"""
Note Service
Business logic for note operations
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

from repositories.note_repository import get_note_repository
from exceptions import NotFoundError, ValidationError


class NoteService:
    """Service for note-related operations"""
    
    def __init__(self, database):
        self.db = database
        self.repository = get_note_repository(database)
    
    async def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new note"""
        note_doc = {
            "user_id": note_data["user_id"],
            "usn": note_data["usn"],
            "title": note_data["title"],
            "department": note_data["department"],
            "year": note_data["year"],
            "subject": note_data["subject"],
            "filename": note_data["filename"],
            "original_filename": note_data["original_filename"],
            "uploaded_at": datetime.utcnow(),
            "is_flagged": False,
            "flag_reason": None,
            "reviewed_at": None,
            "is_approved": True,
            "download_count": 0,
            "view_count": 0
        }
        
        result = await self.db.notes.insert_one(note_doc)
        note_doc["_id"] = result.inserted_id
        return note_doc
    
    async def get_notes(
        self,
        department: Optional[str] = None,
        subject: Optional[str] = None,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get notes with optional filters and pagination"""
        query = {"is_approved": True}
        
        if department:
            query["department"] = department
        if subject:
            query["subject"] = subject
        if year:
            query["year"] = year
        
        cursor = self.db.notes.find(query).sort("uploaded_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get note by ID"""
        return await self.db.notes.find_one({"_id": ObjectId(note_id)})
    
    async def increment_download_count(self, note_id: str) -> bool:
        """Increment note download count"""
        result = await self.db.notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$inc": {"download_count": 1}}
        )
        return result.modified_count > 0
    
    async def increment_view_count(self, note_id: str) -> bool:
        """Increment note view count"""
        result = await self.db.notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$inc": {"view_count": 1}}
        )
        return result.modified_count > 0
    
    async def flag_note(self, note_id: str, reason: str) -> bool:
        """Flag a note for review"""
        result = await self.db.notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": {
                "is_flagged": True,
                "flag_reason": reason
            }}
        )
        return result.modified_count > 0
    
    async def get_flagged_notes(self) -> List[Dict[str, Any]]:
        """Get all flagged notes"""
        cursor = self.db.notes.find({"is_flagged": True})
        return await cursor.to_list(length=100)
    
    async def approve_note(self, note_id: str) -> bool:
        """Approve a flagged note"""
        result = await self.db.notes.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": {
                "is_flagged": False,
                "is_approved": True,
                "reviewed_at": datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    async def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        result = await self.db.notes.delete_one({"_id": ObjectId(note_id)})
        return result.deleted_count > 0
    
    async def search_notes(
        self,
        search_text: str,
        department: Optional[str] = None,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search notes by title or subject"""
        query = {
            "is_approved": True,
            "$or": [
                {"title": {"$regex": search_text, "$options": "i"}},
                {"subject": {"$regex": search_text, "$options": "i"}}
            ]
        }
        
        if department:
            query["department"] = department
        if year:
            query["year"] = year
        
        cursor = self.db.notes.find(query).sort("uploaded_at", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_note_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total count of notes matching filters"""
        query = filters or {}
        return await self.db.notes.count_documents(query)
