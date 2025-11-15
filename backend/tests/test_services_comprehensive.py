"""
Comprehensive tests for service layer (analytics, cache, email, file services)
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from services.analytics_service import AnalyticsService
from services.cache_service import CacheService
from services.email_service import EmailService
from services.file_service import FileService
from exceptions import FileUploadError


@pytest.mark.asyncio
class TestAnalyticsService:
    """Test AnalyticsService class"""
    
    async def test_track_event(self, test_db):
        """Test tracking an analytics event"""
        service = AnalyticsService(test_db)
        
        user_id = str(uuid.uuid4())
        await service.track_event(
            event_type="note_view",
            user_id=user_id,
            metadata={"note_id": str(uuid.uuid4())}
        )
        
        # Verify event was stored
        event = await test_db.analytics_events.find_one({"user_id": user_id})
        assert event is not None
        assert event["event_type"] == "note_view"
    
    async def test_get_dashboard_stats(self, test_db):
        """Test getting dashboard statistics"""
        service = AnalyticsService(test_db)
        
        # Create test data
        user_id = str(uuid.uuid4())
        for i in range(5):
            await test_db.notes.insert_one({
                "_id": str(uuid.uuid4()),
                "title": f"Note {i}",
                "user_id": user_id,
                "department": "CSE",
                "uploaded_at": datetime.utcnow(),
                "download_count": i * 2,
                "view_count": i * 3
            })
        
        stats = await service.get_dashboard_stats(user_id=user_id)
        
        assert stats["total_notes"] == 5
        assert "total_downloads" in stats
        assert "total_views" in stats
        assert "uploads" in stats
    
    async def test_get_popular_notes(self, test_db):
        """Test getting popular notes"""
        service = AnalyticsService(test_db)
        
        # Create notes with different popularity
        for i in range(3):
            await test_db.notes.insert_one({
                "_id": str(uuid.uuid4()),
                "title": f"Note {i}",
                "is_approved": True,
                "download_count": (3 - i) * 10,
                "view_count": (3 - i) * 5
            })
        
        popular = await service.get_popular_notes(limit=2)
        
        assert len(popular) <= 2
        if len(popular) >= 2:
            # First should be more popular than second
            score1 = popular[0]["download_count"] * 2 + popular[0]["view_count"]
            score2 = popular[1]["download_count"] * 2 + popular[1]["view_count"]
            assert score1 >= score2
    
    async def test_get_department_statistics(self, test_db):
        """Test getting department statistics"""
        service = AnalyticsService(test_db)
        
        # Create notes for different departments
        departments = ["CSE", "ECE", "ME"]
        for dept in departments:
            for i in range(2):
                await test_db.notes.insert_one({
                    "_id": str(uuid.uuid4()),
                    "title": f"{dept} Note {i}",
                    "department": dept,
                    "download_count": 10,
                    "view_count": 20
                })
        
        stats = await service.get_department_statistics()
        
        assert len(stats) >= 3
        dept_names = [s["department"] for s in stats]
        assert "CSE" in dept_names


@pytest.mark.asyncio
class TestCacheService:
    """Test CacheService class"""
    
    async def test_set_and_get(self):
        """Test setting and getting cache value"""
        cache = CacheService()
        
        key = "test_key"
        value = {"data": "test_value"}
        
        await cache.set(key, value, ttl=60)
        result = await cache.get(key)
        
        assert result == value
    
    async def test_get_nonexistent(self):
        """Test getting non-existent key returns None"""
        cache = CacheService()
        
        result = await cache.get("nonexistent_key")
        assert result is None
    
    async def test_delete(self):
        """Test deleting cache key"""
        cache = CacheService()
        
        key = "test_key"
        await cache.set(key, {"data": "value"}, ttl=60)
        
        success = await cache.delete(key)
        assert success is True
        
        result = await cache.get(key)
        assert result is None
    
    async def test_set_note(self):
        """Test caching a note"""
        cache = CacheService()
        
        note_id = str(uuid.uuid4())
        note_data = {
            "id": note_id,
            "title": "Test Note",
            "subject": "Math"
        }
        
        await cache.set_note(note_id, note_data, ttl=600)
        result = await cache.get_note(note_id)
        
        assert result["title"] == "Test Note"
    
    async def test_invalidate_note(self):
        """Test invalidating cached note"""
        cache = CacheService()
        
        note_id = str(uuid.uuid4())
        note_data = {"id": note_id, "title": "Test"}
        
        await cache.set_note(note_id, note_data)
        await cache.invalidate_note(note_id)
        
        result = await cache.get_note(note_id)
        assert result is None


@pytest.mark.asyncio
class TestEmailService:
    """Test EmailService class"""
    
    async def test_send_email_mock_mode(self):
        """Test sending email in mock mode"""
        service = EmailService()
        service.provider = "mock"
        service.enabled = True
        
        result = await service.send_email(
            to="test@example.com",
            subject="Test Email",
            html_body="<p>Test content</p>"
        )
        
        assert result is True
    
    async def test_send_welcome_email(self):
        """Test sending welcome email"""
        service = EmailService()
        service.provider = "mock"
        service.enabled = True
        
        result = await service.send_welcome_email(
            user_email="new@example.com",
            user_name="Test User"
        )
        
        assert result is True
    
    async def test_send_password_reset_email(self):
        """Test sending password reset email"""
        service = EmailService()
        service.provider = "mock"
        service.enabled = True
        
        result = await service.send_password_reset_email(
            user_email="user@example.com",
            user_name="Test User",
            reset_link="http://example.com/reset?token=abc123"
        )
        
        assert result is True
    
    async def test_send_note_upload_notification(self):
        """Test sending note upload notification"""
        service = EmailService()
        service.provider = "mock"
        service.enabled = True
        
        result = await service.send_note_upload_notification(
            recipient_email="student@example.com",
            uploader_name="John Doe",
            note_title="CS101 Notes",
            department="CSE",
            subject_name="Computer Science"
        )
        
        assert result is True


class TestFileService:
    """Test FileService class"""
    
    def test_validate_file_success(self):
        """Test file validation with allowed extension"""
        service = FileService(upload_dir="/tmp/test_uploads")
        
        mock_file = Mock()
        mock_file.filename = "document.pdf"
        
        # Should not raise exception
        service.validate_file(mock_file)
    
    def test_validate_file_invalid_extension(self):
        """Test file validation with disallowed extension"""
        service = FileService(upload_dir="/tmp/test_uploads")
        
        mock_file = Mock()
        mock_file.filename = "virus.exe"
        
        with pytest.raises(FileUploadError):
            service.validate_file(mock_file)
    
    def test_validate_file_no_filename(self):
        """Test file validation with no filename"""
        service = FileService(upload_dir="/tmp/test_uploads")
        
        mock_file = Mock()
        mock_file.filename = None
        
        with pytest.raises(FileUploadError):
            service.validate_file(mock_file)
    
    def test_get_file_path(self):
        """Test getting full file path"""
        service = FileService(upload_dir="/tmp/test_uploads")
        
        path = service.get_file_path("test.pdf")
        
        assert "/tmp/test_uploads" in path
        assert "test.pdf" in path
    
    def test_file_exists(self, tmp_path):
        """Test checking if file exists"""
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        
        service = FileService(upload_dir=str(upload_dir))
        
        # Create a test file
        test_file = upload_dir / "test.pdf"
        test_file.write_text("test content")
        
        assert service.file_exists("test.pdf") is True
        assert service.file_exists("nonexistent.pdf") is False
    
    def test_delete_file(self, tmp_path):
        """Test deleting a file"""
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        
        service = FileService(upload_dir=str(upload_dir))
        
        # Create a test file
        test_file = upload_dir / "test.pdf"
        test_file.write_text("test content")
        
        success = service.delete_file("test.pdf")
        
        assert success is True
        assert not test_file.exists()
    
    def test_delete_nonexistent_file(self, tmp_path):
        """Test deleting non-existent file"""
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        
        service = FileService(upload_dir=str(upload_dir))
        
        success = service.delete_file("nonexistent.pdf")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_save_file_too_large(self, tmp_path):
        """Test saving file that exceeds size limit"""
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        
        service = FileService(upload_dir=str(upload_dir))
        
        # Create mock file that's too large
        mock_file = Mock()
        mock_file.filename = "large.pdf"
        mock_file.read = AsyncMock(return_value=b"a" * (15 * 1024 * 1024))  # 15MB
        
        with pytest.raises(FileUploadError) as exc_info:
            await service.save_file(mock_file)
        
        assert "too large" in str(exc_info.value).lower()
