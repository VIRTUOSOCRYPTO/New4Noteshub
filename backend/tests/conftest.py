"""
Pytest configuration and fixtures for backend tests
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

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
    
    # Override database dependency
    from database import get_database
    
    async def override_get_database():
        return test_db
    
    app.dependency_overrides[get_database] = override_get_database
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(client: AsyncClient, test_db):
    """Create a test user"""
    user_data = {
        "usn": "1RV21CS001",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "confirmPassword": "TestPassword123!",
        "department": "Computer Science",
        "college": "Test College",
        "year": 3
    }
    
    response = await client.post("/api/register", json=user_data)
    assert response.status_code == 200
    
    return response.json()


@pytest.fixture
async def auth_headers(test_user):
    """Get authentication headers for test user"""
    # Extract token from test_user response
    # This will depend on your actual response structure
    return {
        "Authorization": f"Bearer {test_user.get('accessToken', '')}"
    }
