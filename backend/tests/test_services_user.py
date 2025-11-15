"""
User Service Unit Tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

from services.user_service import UserService


@pytest.fixture
def user_service():
    """Create a UserService instance with mocked database"""
    mock_db = MagicMock()
    return UserService(mock_db)


@pytest.mark.asyncio
async def test_get_user_by_id_found(user_service):
    """Test getting a user by ID when it exists"""
    expected_user = {
        "_id": "user123",
        "usn": "1RV21CS001",
        "email": "test@example.com",
        "department": "CSE"
    }
    
    user_service.db.users.find_one = AsyncMock(return_value=expected_user)
    
    result = await user_service.get_user_by_id("user123")
    
    assert result == expected_user
    user_service.db.users.find_one.assert_called_once_with({"_id": "user123"})


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service):
    """Test getting a user by ID when it doesn't exist"""
    user_service.db.users.find_one = AsyncMock(return_value=None)
    
    result = await user_service.get_user_by_id("nonexistent")
    
    assert result is None


@pytest.mark.asyncio
async def test_get_user_by_usn_found(user_service):
    """Test getting a user by USN when it exists"""
    expected_user = {
        "_id": "user123",
        "usn": "1RV21CS001",
        "email": "test@example.com"
    }
    
    user_service.db.users.find_one = AsyncMock(return_value=expected_user)
    
    result = await user_service.get_user_by_usn("1RV21CS001")
    
    assert result == expected_user
    user_service.db.users.find_one.assert_called_once_with({"usn": "1RV21CS001"})


@pytest.mark.asyncio
async def test_get_user_by_email_found(user_service):
    """Test getting a user by email when it exists"""
    expected_user = {
        "_id": "user123",
        "usn": "1RV21CS001",
        "email": "test@example.com"
    }
    
    user_service.db.users.find_one = AsyncMock(return_value=expected_user)
    
    result = await user_service.get_user_by_email("test@example.com")
    
    assert result == expected_user


@pytest.mark.asyncio
async def test_create_user(user_service):
    """Test creating a new user"""
    user_service.db.users.insert_one = AsyncMock(return_value=MagicMock(inserted_id="user123"))
    
    user_data = {
        "usn": "1RV21CS999",
        "email": "newuser@example.com",
        "password": "hashed_password",
        "department": "CSE",
        "year": 2
    }
    
    result = await user_service.create_user(user_data)
    
    assert result == "user123"
    user_service.db.users.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_update_user(user_service):
    """Test updating user data"""
    user_service.db.users.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    
    update_data = {"email": "newemail@example.com"}
    result = await user_service.update_user("user123", update_data)
    
    assert result is True
    user_service.db.users.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user(user_service):
    """Test deleting a user"""
    user_service.db.users.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    
    result = await user_service.delete_user("user123")
    
    assert result is True
    user_service.db.users.delete_one.assert_called_once_with({"_id": "user123"})


@pytest.mark.asyncio
async def test_get_user_stats(user_service):
    """Test getting user statistics"""
    # Mock notes count
    user_service.db.notes.count_documents = AsyncMock(return_value=5)
    # Mock bookmarks count
    user_service.db.bookmarks.count_documents = AsyncMock(return_value=3)
    
    stats = await user_service.get_user_stats("user123")
    
    assert stats["notes_count"] == 5
    assert stats["bookmarks_count"] == 3
