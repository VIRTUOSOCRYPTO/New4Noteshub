"""
Quick tests to boost coverage
"""

import pytest
from httpx import AsyncClient
from auth import get_password_hash, verify_password, create_access_token
from models import TokenData, UserResponse
from exceptions import BaseAPIException
import uuid


# Auth utility tests
def test_password_hashing():
    """Test password hashing and verification"""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_token_creation():
    """Test JWT token creation"""
    data = {"user_id": "123", "usn": "1RV21CS001"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 50


# Model tests
def test_token_data_model():
    """Test TokenData model"""
    token = TokenData(user_id="123", usn="1RV21CS001")
    assert token.user_id == "123"
    assert token.usn == "1RV21CS001"


def test_user_response_model():
    """Test UserResponse model"""
    user_data = {
        "id": str(uuid.uuid4()),
        "usn": "1RV21CS001",
        "email": "test@example.com",
        "department": "CSE",
        "year": 2,
        "college": "Test College",
        "role": "user",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    
    user = UserResponse(**user_data)
    assert user.usn == "1RV21CS001"
    assert user.email == "test@example.com"


# Exception tests
def test_base_exception():
    """Test base API exception"""
    exc = BaseAPIException("Test error")
    assert str(exc) == "Test error"
    assert exc.status_code == 500


# More integration tests
@pytest.mark.asyncio
async def test_various_note_queries(client: AsyncClient):
    """Test various note query combinations"""
    queries = [
        "/api/notes?skip=0",
        "/api/notes?limit=5",
        "/api/notes?department=EEE",
        "/api/notes?year=3",
        "/api/notes?subject=Physics",
        "/api/notes?department=CSE&year=2",
    ]
    
    for query in queries:
        response = await client.get(query)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_http_methods_on_endpoints(client: AsyncClient):
    """Test different HTTP methods on endpoints"""
    # GET on health
    response = await client.get("/api/health")
    assert response.status_code == 200
    
    # OPTIONS (for CORS)
    response = await client.options("/api/health")
    assert response.status_code in [200, 405]


@pytest.mark.asyncio
async def test_query_parameter_validation(client: AsyncClient):
    """Test query parameter validation"""
    # Valid pagination
    response = await client.get("/api/notes?skip=0&limit=10")
    assert response.status_code == 200
    
    # Invalid pagination values (should handle gracefully)
    response = await client.get("/api/notes?skip=abc&limit=xyz")
    assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_empty_responses(client: AsyncClient):
    """Test empty response handling"""
    # Get notes with non-existent filter combination
    response = await client.get("/api/notes?department=NONEXISTENT&year=99")
    assert response.status_code == 200
    data = response.json()
    # Should return empty list or empty result
    assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_content_type_headers(client: AsyncClient):
    """Test content type handling"""
    # JSON request
    response = await client.post("/api/register", 
                                 json={"test": "data"},
                                 headers={"Content-Type": "application/json"})
    assert response.status_code in [400, 422]  # Should validate and reject


@pytest.mark.asyncio
async def test_large_pagination_values(client: AsyncClient):
    """Test pagination with large values"""
    # Very large skip
    response = await client.get("/api/notes?skip=10000&limit=100")
    assert response.status_code == 200
    
    # Very large limit
    response = await client.get("/api/notes?skip=0&limit=1000")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_multiple_filter_combinations(client: AsyncClient):
    """Test multiple filter combinations"""
    filters = [
        "?department=CSE&year=2&subject=Math",
        "?department=EEE&year=3",
        "?year=1&subject=Physics",
    ]
    
    for f in filters:
        response = await client.get(f"/api/notes{f}")
        assert response.status_code == 200
