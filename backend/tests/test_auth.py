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
        "department": "CSE",  # Valid department
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
async def test_register_invalid_department(client: AsyncClient):
    """Test registration with invalid department"""
    user_data = {
        "usn": "1RV21CS888",
        "email": "invalid@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "SecurePass123!",
        "department": "INVALID",  # Invalid department
        "college": "Test College",
        "year": 2
    }
    
    response = await client.post("/api/register", json=user_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_password_mismatch(client: AsyncClient):
    """Test registration with password mismatch"""
    user_data = {
        "usn": "1RV21CS777",
        "email": "mismatch@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "DifferentPass123!",
        "department": "CSE",
        "college": "Test College",
        "year": 2
    }
    
    response = await client.post("/api/register", json=user_data)
    assert response.status_code == 422  # Validation error


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
    assert "user" in data
    assert data["user"]["usn"] == login_data["usn"].upper()


@pytest.mark.asyncio
async def test_login_invalid_usn(client: AsyncClient):
    """Test login with non-existent USN"""
    login_data = {
        "usn": "1RV21CS000",
        "password": "SomePassword123!"
    }
    
    response = await client.post("/api/login", json=login_data)
    assert response.status_code in [401, 404]  # Unauthorized or not found


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user):
    """Test login with wrong password"""
    login_data = {
        "usn": "1RV21CS001",
        "password": "WrongPassword123!"
    }
    
    response = await client.post("/api/login", json=login_data)
    assert response.status_code == 401  # Unauthorized


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers):
    """Test getting current user with valid token"""
    if not auth_headers:
        pytest.skip("No auth token available")
    
    response = await client.get("/api/user", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "usn" in data
    assert "email" in data


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers):
    """Test logout endpoint"""
    if not auth_headers:
        pytest.skip("No auth token available")
    
    response = await client.post("/api/logout", headers=auth_headers)
    assert response.status_code in [200, 204]  # Success
