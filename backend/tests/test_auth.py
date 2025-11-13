"""
Authentication endpoint tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    user_data = {
        "usn": "1RV21CS999",
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "SecurePass123!",
        "department": "Computer Science",
        "college": "Test College",
        "year": 2
    }
    
    response = await client.post("/api/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["usn"] == user_data["usn"].upper()
    assert data["email"] == user_data["email"]
    assert "password" not in data  # Password should not be in response


@pytest.mark.asyncio
async def test_register_duplicate_usn(client: AsyncClient, test_user):
    """Test registration with duplicate USN"""
    user_data = {
        "usn": test_user["usn"],
        "email": "different@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "SecurePass123!",
        "department": "Computer Science",
        "college": "Test College",
        "year": 2
    }
    
    response = await client.post("/api/register", json=user_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_password_mismatch(client: AsyncClient):
    """Test registration with mismatched passwords"""
    user_data = {
        "usn": "1RV21CS888",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "DifferentPass123!",
        "department": "Computer Science",
        "college": "Test College",
        "year": 2
    }
    
    response = await client.post("/api/register", json=user_data)
    assert response.status_code == 400
    assert "do not match" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    login_data = {
        "usn": "1RV21CS001",
        "password": "TestPassword123!"
    }
    
    response = await client.post("/api/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "accessToken" in data
    assert "refreshToken" in data
    assert "user" in data


@pytest.mark.asyncio
async def test_login_invalid_usn(client: AsyncClient):
    """Test login with non-existent USN"""
    login_data = {
        "usn": "INVALID999",
        "password": "AnyPassword123!"
    }
    
    response = await client.post("/api/login", json=login_data)
    assert response.status_code == 401
    assert "not registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with wrong password"""
    login_data = {
        "usn": test_user["usn"],
        "password": "WrongPassword123!"
    }
    
    response = await client.post("/api/login", json=login_data)
    assert response.status_code == 401
    assert "incorrect password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user, auth_headers):
    """Test getting current user information"""
    response = await client.get("/api/user", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["usn"] == test_user["usn"]
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers):
    """Test user logout"""
    response = await client.post("/api/logout", headers=auth_headers)
    assert response.status_code == 200
    assert "success" in response.json()["message"].lower()
