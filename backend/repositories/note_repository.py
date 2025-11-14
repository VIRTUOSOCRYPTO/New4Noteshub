"""
Note Repository
Data access layer for notes using repository pattern (DDD)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId


class NoteRepository:
    """Repository for note data access"""
    
    def __init__(self, database):
        self.db = database
        self.collection = database.notes
    
    async def create(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new note"""
        result = await self.collection.insert_one(note_data)
        note_data["_id"] = result.inserted_id
        return note_data
    
    async def find_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Find note by ID"""
        try:
            return await self.collection.find_one({"_id": ObjectId(note_id)})
        except Exception:
            return None
    
    async def find_many(
        self,
        query: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort_field: str = "uploaded_at",
        sort_order: int = -1
    ) -> List[Dict[str, Any]]:
        """Find multiple notes with filters"""
        cursor = self.collection.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def update_by_id(self, note_id: str, update_data: Dict[str, Any]) -> bool:
        """Update note by ID"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(note_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def increment_field(self, note_id: str, field: str, value: int = 1) -> bool:
        """Increment a numeric field"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(note_id)},
                {"$inc": {field: value}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def delete_by_id(self, note_id: str) -> bool:
        """Delete note by ID"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(note_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """Count notes matching query"""
        return await self.collection.count_documents(query or {})
    
    async def exists(self, note_id: str) -> bool:
        """Check if note exists"""
        try:
            count = await self.collection.count_documents({"_id": ObjectId(note_id)})
            return count > 0
        except Exception:
            return False


def get_note_repository(database) -> NoteRepository:
    """Get note repository instance"""
    return NoteRepository(database)
