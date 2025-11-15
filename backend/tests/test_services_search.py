"""
Search Service Unit Tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from services.search_service import SearchService


@pytest.fixture
def search_service():
    """Create a SearchService instance with mocked database"""
    mock_db = MagicMock()
    return SearchService(mock_db)


@pytest.mark.asyncio
async def test_search_notes_by_title(search_service):
    """Test searching notes by title"""
    expected_notes = [
        {"_id": "note1", "title": "Data Structures"},
        {"_id": "note2", "title": "Data Analysis"}
    ]
    
    mock_cursor = MagicMock()
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=expected_notes)
    
    search_service.db.notes.find = MagicMock(return_value=mock_cursor)
    
    result = await search_service.search_notes("data", limit=10)
    
    assert len(result) == 2
    assert "Data" in result[0]["title"]


@pytest.mark.asyncio
async def test_search_notes_empty_query(search_service):
    """Test searching with empty query returns all notes"""
    expected_notes = [
        {"_id": "note1", "title": "Note 1"},
        {"_id": "note2", "title": "Note 2"}
    ]
    
    mock_cursor = MagicMock()
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=expected_notes)
    
    search_service.db.notes.find = MagicMock(return_value=mock_cursor)
    
    result = await search_service.search_notes("", limit=10)
    
    assert len(result) == 2


@pytest.mark.asyncio
async def test_search_with_filters(search_service):
    """Test searching notes with department and year filters"""
    expected_notes = [{"_id": "note1", "title": "Algorithms", "department": "CSE", "year": 2}]
    
    mock_cursor = MagicMock()
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=expected_notes)
    
    search_service.db.notes.find = MagicMock(return_value=mock_cursor)
    
    filters = {"department": "CSE", "year": 2}
    result = await search_service.search_notes("algorithm", filters=filters, limit=10)
    
    assert len(result) == 1
    assert result[0]["department"] == "CSE"


@pytest.mark.asyncio
async def test_ensure_text_indexes(search_service):
    """Test ensuring text indexes are created"""
    search_service.db.notes.create_index = AsyncMock()
    
    await search_service.ensure_text_indexes()
    
    # Should create text index on title and subject
    search_service.db.notes.create_index.assert_called_once()


@pytest.mark.asyncio
async def test_get_popular_searches(search_service):
    """Test getting popular search queries"""
    expected_searches = [
        {"query": "data structures", "count": 100},
        {"query": "algorithms", "count": 85}
    ]
    
    mock_cursor = MagicMock()
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.to_list = AsyncMock(return_value=expected_searches)
    
    search_service.db.search_logs.aggregate = MagicMock(return_value=mock_cursor)
    
    result = await search_service.get_popular_searches(limit=10)
    
    assert len(result) == 2
    assert result[0]["count"] >= result[1]["count"]  # Should be sorted by count
