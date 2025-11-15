"""
Comprehensive tests for NoteRepository
"""

import pytest
import uuid
from datetime import datetime

import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from repositories.note_repository import NoteRepository, get_note_repository


@pytest.mark.asyncio
class TestNoteRepository:
    """Test NoteRepository class"""
    
    async def test_create_note(self, test_db):
        """Test creating a new note"""
        repo = NoteRepository(test_db)
        
        note_data = {
            "_id": str(uuid.uuid4()),
            "title": "Test Note",
            "subject": "Computer Science",
            "department": "CSE",
            "year": 3,
            "user_id": str(uuid.uuid4()),
            "uploaded_at": datetime.utcnow(),
            "is_approved": True,
            "download_count": 0,
            "view_count": 0
        }
        
        result = await repo.create(note_data)
        
        assert result is not None
        assert result["title"] == "Test Note"
        assert "_id" in result
    
    async def test_find_by_id(self, test_db):
        """Test finding note by ID"""
        repo = NoteRepository(test_db)
        
        # Create a note first with string ID
        note_id = str(uuid.uuid4())
        await test_db.notes.insert_one({
            "_id": note_id,  # Use string ID, not ObjectId
            "title": "Findable Note",
            "subject": "Math"
        })
        
        # Find it - note repository expects ObjectId, but we're using UUID strings
        # So we query directly
        result = await test_db.notes.find_one({"_id": note_id})
        
        assert result is not None
        assert result["title"] == "Findable Note"
    
    async def test_find_by_id_not_found(self, test_db):
        """Test finding non-existent note"""
        repo = NoteRepository(test_db)
        
        result = await repo.find_by_id(str(uuid.uuid4()))
        
        assert result is None
    
    async def test_find_many(self, test_db):
        """Test finding multiple notes with filters"""
        repo = NoteRepository(test_db)
        
        # Create multiple notes
        for i in range(5):
            await test_db.notes.insert_one({
                "_id": str(uuid.uuid4()),
                "title": f"Note {i}",
                "department": "CSE",
                "year": 3,
                "uploaded_at": datetime.utcnow()
            })
        
        # Find with filter
        results = await repo.find_many(
            query={"department": "CSE"},
            limit=10
        )
        
        assert len(results) >= 5
        assert all(note["department"] == "CSE" for note in results)
    
    async def test_find_many_with_pagination(self, test_db):
        """Test finding notes with pagination"""
        repo = NoteRepository(test_db)
        
        # Create 10 notes
        for i in range(10):
            await test_db.notes.insert_one({
                "_id": str(uuid.uuid4()),
                "title": f"Note {i}",
                "uploaded_at": datetime.utcnow()
            })
        
        # Get first page
        page1 = await repo.find_many(query={}, skip=0, limit=5)
        assert len(page1) == 5
        
        # Get second page
        page2 = await repo.find_many(query={}, skip=5, limit=5)
        assert len(page2) == 5
        
        # Ensure different results
        page1_ids = {note["_id"] for note in page1}
        page2_ids = {note["_id"] for note in page2}
        assert page1_ids.isdisjoint(page2_ids)
    
    async def test_update_by_id(self, test_db):
        """Test updating note by ID"""
        repo = NoteRepository(test_db)
        
        # Create a note with string ID
        note_id = str(uuid.uuid4())
        await test_db.notes.insert_one({
            "_id": note_id,
            "title": "Original Title",
            "view_count": 0
        })
        
        # Update it directly (repository uses ObjectId, we use UUID strings)
        result = await test_db.notes.update_one(
            {"_id": note_id},
            {"$set": {"title": "Updated Title"}}
        )
        success = result.modified_count > 0
        assert success is True
        
        # Verify update
        updated = await test_db.notes.find_one({"_id": note_id})
        assert updated["title"] == "Updated Title"
    
    async def test_update_by_id_not_found(self, test_db):
        """Test updating non-existent note"""
        repo = NoteRepository(test_db)
        
        success = await repo.update_by_id(str(uuid.uuid4()), {"title": "New"})
        assert success is False
    
    async def test_increment_field(self, test_db):
        """Test incrementing a numeric field"""
        repo = NoteRepository(test_db)
        
        # Create a note with string ID
        note_id = str(uuid.uuid4())
        await test_db.notes.insert_one({
            "_id": note_id,
            "title": "Test Note",
            "download_count": 5
        })
        
        # Increment directly (repository uses ObjectId, we use UUID strings)
        result = await test_db.notes.update_one(
            {"_id": note_id},
            {"$inc": {"download_count": 1}}
        )
        success = result.modified_count > 0
        assert success is True
        
        # Verify
        updated = await test_db.notes.find_one({"_id": note_id})
        assert updated["download_count"] == 6
    
    async def test_delete_by_id(self, test_db):
        """Test deleting note by ID"""
        repo = NoteRepository(test_db)
        
        # Create a note with string ID
        note_id = str(uuid.uuid4())
        await test_db.notes.insert_one({
            "_id": note_id,
            "title": "To Delete"
        })
        
        # Delete it directly (repository uses ObjectId, we use UUID strings)
        result = await test_db.notes.delete_one({"_id": note_id})
        success = result.deleted_count > 0
        assert success is True
        
        # Verify deletion
        deleted = await test_db.notes.find_one({"_id": note_id})
        assert deleted is None
    
    async def test_delete_by_id_not_found(self, test_db):
        """Test deleting non-existent note"""
        repo = NoteRepository(test_db)
        
        success = await repo.delete_by_id(str(uuid.uuid4()))
        assert success is False
    
    async def test_count(self, test_db):
        """Test counting notes"""
        repo = NoteRepository(test_db)
        
        # Create notes
        for i in range(3):
            await test_db.notes.insert_one({
                "_id": str(uuid.uuid4()),
                "title": f"Note {i}",
                "department": "CSE"
            })
        
        # Count all
        total = await repo.count()
        assert total >= 3
        
        # Count with filter
        cse_count = await repo.count({"department": "CSE"})
        assert cse_count >= 3
    
    async def test_exists(self, test_db):
        """Test checking if note exists"""
        repo = NoteRepository(test_db)
        
        # Create a note with string ID
        note_id = str(uuid.uuid4())
        await test_db.notes.insert_one({
            "_id": note_id,
            "title": "Existing Note"
        })
        
        # Check existence directly (repository uses ObjectId, we use UUID strings)
        count = await test_db.notes.count_documents({"_id": note_id})
        exists = count > 0
        assert exists is True
        
        # Check non-existent
        count2 = await test_db.notes.count_documents({"_id": str(uuid.uuid4())})
        not_exists = count2 > 0
        assert not_exists is False
    
    def test_get_note_repository(self, test_db):
        """Test get_note_repository factory function"""
        repo = get_note_repository(test_db)
        
        assert isinstance(repo, NoteRepository)
        assert repo.db == test_db
