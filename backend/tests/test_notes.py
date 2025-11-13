"""
Notes endpoint tests
"""

import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_get_notes_empty(client: AsyncClient):
    """Test getting notes when database is empty"""
    response = await client.get("/api/notes")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_upload_note(client: AsyncClient, auth_headers):
    """Test uploading a note"""
    # Create a test file
    test_file_content = b"This is a test PDF content"
    test_file = ("test.pdf", BytesIO(test_file_content), "application/pdf")
    
    form_data = {
        "title": "Test Note",
        "subject": "Mathematics"
    }
    
    response = await client.post(
        "/api/notes",
        data=form_data,
        files={"file": test_file},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["subject"] == "Mathematics"
    assert "filename" in data


@pytest.mark.asyncio
async def test_upload_note_invalid_file_type(client: AsyncClient, auth_headers):
    """Test uploading a note with invalid file type"""
    # Create a test file with .exe extension
    test_file = ("virus.exe", BytesIO(b"malicious content"), "application/x-msdownload")
    
    form_data = {
        "title": "Bad Note",
        "subject": "Hacking"
    }
    
    response = await client.post(
        "/api/notes",
        data=form_data,
        files={"file": test_file},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_notes_with_filters(client: AsyncClient, test_user, auth_headers):
    """Test getting notes with department filter"""
    # First upload a note
    test_file = ("test.pdf", BytesIO(b"Test content"), "application/pdf")
    form_data = {"title": "Filtered Note", "subject": "Physics"}
    
    await client.post(
        "/api/notes",
        data=form_data,
        files={"file": test_file},
        headers=auth_headers
    )
    
    # Get notes with filter
    response = await client.get(
        "/api/notes",
        params={"department": test_user["department"]}
    )
    
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) > 0
    assert all(note["department"] == test_user["department"] for note in notes)


@pytest.mark.asyncio
async def test_increment_view_count(client: AsyncClient, test_user, auth_headers):
    """Test incrementing note view count"""
    # Upload a note first
    test_file = ("test.pdf", BytesIO(b"Test content"), "application/pdf")
    form_data = {"title": "View Test Note", "subject": "Chemistry"}
    
    upload_response = await client.post(
        "/api/notes",
        data=form_data,
        files={"file": test_file},
        headers=auth_headers
    )
    note_id = upload_response.json()["id"]
    
    # Increment view count
    response = await client.get(f"/api/notes/{note_id}/view")
    assert response.status_code == 200
    assert response.json()["success"] == True


@pytest.mark.asyncio
async def test_flag_note(client: AsyncClient, test_user, auth_headers):
    """Test flagging a note"""
    # Upload a note first
    test_file = ("test.pdf", BytesIO(b"Test content"), "application/pdf")
    form_data = {"title": "Flag Test Note", "subject": "Biology"}
    
    upload_response = await client.post(
        "/api/notes",
        data=form_data,
        files={"file": test_file},
        headers=auth_headers
    )
    note_id = upload_response.json()["id"]
    
    # Flag the note
    flag_data = {"reason": "Inappropriate content"}
    response = await client.post(
        f"/api/notes/{note_id}/flag",
        json=flag_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "flagged" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_download_note_unauthorized_year(client: AsyncClient, test_db):
    """Test downloading note from different year (should fail)"""
    # This test would require creating users from different years
    # and testing the year restriction logic
    pass  # Placeholder for more complex test


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, auth_headers):
    """Test note pagination"""
    # Upload multiple notes
    for i in range(5):
        test_file = (f"test{i}.pdf", BytesIO(f"Test content {i}".encode()), "application/pdf")
        form_data = {"title": f"Test Note {i}", "subject": "Math"}
        
        await client.post(
            "/api/notes",
            data=form_data,
            files={"file": test_file},
            headers=auth_headers
        )
    
    # Test pagination
    response = await client.get("/api/notes", params={"skip": 0, "limit": 3})
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) <= 3
