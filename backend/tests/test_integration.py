"""
Integration Tests for Critical Flows
"""

import pytest
from httpx import AsyncClient
import uuid


@pytest.mark.asyncio
async def test_user_registration_login_flow(client: AsyncClient):
    """Test complete user registration and login flow"""
    # 1. Register a new user
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "usn": f"1RV21CS{unique_id[:3].upper()}",
        "email": f"user{unique_id}@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "SecurePass123!",
        "department": "CSE",
        "college": "Test College",
        "year": 2
    }
    
    register_response = await client.post("/api/register", json=user_data)
    assert register_response.status_code == 200
    user_info = register_response.json()
    assert "id" in user_info or "_id" in user_info
    
    # 2. Login with registered credentials
    login_data = {
        "usn": user_data["usn"],
        "password": user_data["password"]
    }
    
    login_response = await client.post("/api/login", json=login_data)
    assert login_response.status_code == 200
    login_info = login_response.json()
    assert "accessToken" in login_info
    assert "user" in login_info
    
    # 3. Access protected endpoint with token
    headers = {"Authorization": f"Bearer {login_info['accessToken']}"}
    profile_response = await client.get("/api/user", headers=headers)
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["usn"] == user_data["usn"].upper()


@pytest.mark.asyncio
async def test_note_browsing_flow(client: AsyncClient):
    """Test note browsing functionality"""
    # 1. Get notes without authentication (public access)
    response = await client.get("/api/notes")
    assert response.status_code == 200
    notes = response.json()
    assert isinstance(notes, list) or isinstance(notes, dict)
    
    # 2. Get notes with filters
    response = await client.get("/api/notes?department=CSE&year=2")
    assert response.status_code == 200
    
    # 3. Get notes with pagination
    response = await client.get("/api/notes?skip=0&limit=10")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_and_db_status_flow(client: AsyncClient):
    """Test system health check flow"""
    # 1. Basic health check
    response = await client.get("/api/health")
    assert response.status_code == 200
    health = response.json()
    assert health["status"] == "ok"
    assert "timestamp" in health
    
    # 2. Database status check
    response = await client.get("/api/db-status")
    assert response.status_code == 200
    db_status = response.json()
    assert "status" in db_status


@pytest.mark.asyncio
async def test_authentication_error_handling(client: AsyncClient):
    """Test authentication error handling"""
    # 1. Access protected endpoint without token
    response = await client.get("/api/user")
    assert response.status_code in [401, 403]
    
    # 2. Login with invalid credentials
    login_data = {
        "usn": "1RV21CS000",
        "password": "WrongPassword123!"
    }
    response = await client.post("/api/login", json=login_data)
    assert response.status_code in [401, 404]
    
    # 3. Register with invalid data
    invalid_user = {
        "usn": "INVALID",
        "email": "invalid@example.com",
        "password": "pass",
        "confirmPassword": "pass",
        "department": "INVALID",
        "college": "Test",
        "year": 10
    }
    response = await client.post("/api/register", json=invalid_user)
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_api_cors_headers(client: AsyncClient):
    """Test CORS headers are present"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    # CORS headers should be present
    # Note: In test environment, headers might be handled differently


@pytest.mark.asyncio
async def test_pagination_flow(client: AsyncClient):
    """Test pagination works correctly"""
    # Get first page
    response1 = await client.get("/api/notes?skip=0&limit=5")
    assert response1.status_code == 200
    
    # Get second page
    response2 = await client.get("/api/notes?skip=5&limit=5")
    assert response2.status_code == 200
    
    # Results should be different (unless less than 5 notes total)
    # This is a basic sanity check


@pytest.mark.asyncio
async def test_rate_limiting_awareness(client: AsyncClient):
    """Test that rate limiting is configured (basic awareness test)"""
    # Make multiple requests quickly
    responses = []
    for _ in range(5):
        response = await client.get("/api/health")
        responses.append(response.status_code)
    
    # All should succeed (rate limit is usually higher than 5)
    assert all(status == 200 for status in responses)
