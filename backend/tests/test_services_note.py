"""
Note Service Unit Tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
from datetime import datetime

from services.note_service import NoteService


@pytest.fixture
def note_service():
    """Create a NoteService instance with mocked database"""
    mock_db = MagicMock()
    return NoteService(mock_db)


@pytest.mark.asyncio
async def test_create_note(note_service):
    """Test creating a new note"""
    note_service.db.notes.insert_one = AsyncMock(return_value=MagicMock(inserted_id="note123"))
    
    note_data = {
        "title": "Test Note",
        "subject": "Mathematics",
        "department": "CSE",
        "year": 2,
        "file_path": "/uploads/test.pdf",
        "user_id": "user123"
    }
    
    result = await note_service.create_note(note_data)
    
    assert result == "note123"
    note_service.db.notes.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_note_by_id_found(note_service):
    """Test getting a note by ID when it exists"""
    expected_note = {
        "_id": "note123",
        "title": "Test Note",
        "subject": "Mathematics"
    }
    
    note_service.db.notes.find_one = AsyncMock(return_value=expected_note)
    
    result = await note_service.get_note_by_id("note123")
    
    assert result == expected_note
    note_service.db.notes.find_one.assert_called_once_with({"_id": "note123"})


@pytest.mark.asyncio
async def test_get_note_by_id_not_found(note_service):
    """Test getting a note by ID when it doesn't exist"""
    note_service.db.notes.find_one = AsyncMock(return_value=None)
    
    result = await note_service.get_note_by_id("nonexistent")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_notes_with_filters(note_service):
    """Test getting notes with filters"""
    expected_notes = [
        {"_id": "note1", "title": "Note 1"},
        {"_id": "note2", "title": "Note 2"}
    ]
    
    mock_cursor = MagicMock()
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=expected_notes)
    
    note_service.db.notes.find = MagicMock(return_value=mock_cursor)
    
    filters = {"department": "CSE", "year": 2}
    result = await note_service.get_notes(filters, skip=0, limit=10)
    
    assert len(result) == 2
    assert result[0]["title"] == "Note 1"


@pytest.mark.asyncio
async def test_increment_view_count(note_service):
    """Test incrementing note view count"""
    note_service.db.notes.update_one = AsyncMock()
    
    await note_service.increment_view_count("note123")
    
    note_service.db.notes.update_one.assert_called_once()
    call_args = note_service.db.notes.update_one.call_args
    assert call_args[0][0] == {"_id": "note123"}
    assert "$inc" in call_args[0][1]


@pytest.mark.asyncio
async def test_delete_note(note_service):
    """Test deleting a note"""
    note_service.db.notes.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    
    result = await note_service.delete_note("note123")
    
    assert result is True
    note_service.db.notes.delete_one.assert_called_once_with({"_id": "note123"})


@pytest.mark.asyncio
async def test_update_note_approval_status(note_service):
    """Test updating note approval status"""
    note_service.db.notes.update_one = AsyncMock()
    
    await note_service.update_approval_status("note123", is_approved=True)
    
    note_service.db.notes.update_one.assert_called_once()
    call_args = note_service.db.notes.update_one.call_args
    assert call_args[0][0] == {"_id": "note123"}
    assert "is_approved" in str(call_args[0][1])
