"""
Pytest configuration and fixtures for backend tests
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Import app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import app
from database import db


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    """Create a test database"""
    # Use a separate test database
    test_db_name = "noteshub_test"
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    test_database = client[test_db_name]
    
    yield test_database
    
    # Cleanup: Drop test database after tests
    await client.drop_database(test_db_name)
    client.close()


@pytest.fixture(scope="function")
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing"""
    # Override database to use test database
    db.db = test_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clean up
    db.db = None


@pytest.fixture
async def test_user(client: AsyncClient, test_db):
    """Create a test user"""
    user_data = {
        "usn": "1RV21CS001",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "confirmPassword": "TestPassword123!",
        "department": "CSE",  # Valid department
        "college": "Test College",
        "year": 3
    }
    
    response = await client.post("/api/register", json=user_data)
    if response.status_code == 200:
        return response.json()
    else:
        # Fallback: create user directly in database
        from auth import hash_password
        user_id = str(uuid.uuid4())
        await test_db.users.insert_one({
            "_id": user_id,
            "usn": user_data["usn"],
            "email": user_data["email"],
            "password": hash_password(user_data["password"]),
            "department": user_data["department"],
            "college": user_data["college"],
            "year": user_data["year"],
            "role": "user"
        })
        return {"id": user_id, "usn": user_data["usn"], "email": user_data["email"]}


@pytest.fixture
async def auth_token(client: AsyncClient, test_user):
    """Get authentication token for test user"""
    login_data = {
        "usn": "1RV21CS001",
        "password": "TestPassword123!"
    }
    
    response = await client.post("/api/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data.get("accessToken", "")
    return None


@pytest.fixture
async def auth_headers(auth_token):
    """Get authentication headers for test user"""
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}
