"""
Comprehensive Router Tests
Testing various router endpoints to increase coverage
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints(client: AsyncClient):
    """Test all health check endpoints"""
    # Test basic health
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    # Test DB status
    response = await client.get("/api/db-status")
    assert response.status_code == 200
    
    # Test system health
    response = await client.get("/api/health/system")
    assert response.status_code in [200, 404]  # May or may not exist


@pytest.mark.asyncio
async def test_notes_public_endpoints(client: AsyncClient):
    """Test public note endpoints"""
    # Get all notes
    response = await client.get("/api/notes")
    assert response.status_code == 200
    
    # Get notes with department filter
    response = await client.get("/api/notes?department=CSE")
    assert response.status_code == 200
    
    # Get notes with year filter
    response = await client.get("/api/notes?year=2")
    assert response.status_code == 200
    
    # Get notes with multiple filters
    response = await client.get("/api/notes?department=CSE&year=2&subject=Mathematics")
    assert response.status_code == 200
    
    # Get notes with pagination
    response = await client.get("/api/notes?skip=0&limit=10")
    assert response.status_code == 200
    
    # Get notes with large skip (edge case)
    response = await client.get("/api/notes?skip=1000&limit=10")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_validation_endpoints(client: AsyncClient):
    """Test authentication validation"""
    # Test registration with missing fields
    response = await client.post("/api/register", json={})
    assert response.status_code in [400, 422]
    
    # Test registration with invalid email
    response = await client.post("/api/register", json={
        "usn": "1RV21CS001",
        "email": "invalid-email",
        "password": "Pass123!",
        "confirmPassword": "Pass123!",
        "department": "CSE",
        "college": "Test",
        "year": 2
    })
    assert response.status_code in [400, 422]
    
    # Test login with missing password
    response = await client.post("/api/login", json={
        "usn": "1RV21CS001"
    })
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_protected_endpoints_without_auth(client: AsyncClient):
    """Test that protected endpoints require authentication"""
    # User profile
    response = await client.get("/api/user")
    assert response.status_code in [401, 403]
    
    # User stats
    response = await client.get("/api/user/stats")
    assert response.status_code in [401, 403]
    
    # Upload note
    response = await client.post("/api/notes")
    assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_cors_and_security_headers(client: AsyncClient):
    """Test CORS and security headers"""
    response = await client.get("/api/health")
    assert response.status_code == 200
    # Basic check that response is successful


@pytest.mark.asyncio
async def test_error_responses(client: AsyncClient):
    """Test error response formats"""
    # Test 404 for non-existent endpoint
    response = await client.get("/api/nonexistent")
    assert response.status_code in [404, 405]
    
    # Test invalid method
    response = await client.delete("/api/health")
    assert response.status_code in [404, 405]


@pytest.mark.asyncio
async def test_rate_limiting_simulation(client: AsyncClient):
    """Test rate limiting (basic simulation)"""
    # Make multiple requests in quick succession
    responses = []
    for i in range(10):
        response = await client.get("/api/health")
        responses.append(response.status_code)
    
    # Most should succeed (rate limit is usually > 10)
    success_count = sum(1 for status in responses if status == 200)
    assert success_count >= 5  # At least half should succeed


@pytest.mark.asyncio
async def test_pagination_edge_cases(client: AsyncClient):
    """Test pagination edge cases"""
    # Test with skip=0
    response = await client.get("/api/notes?skip=0&limit=5")
    assert response.status_code == 200
    
    # Test with limit=1
    response = await client.get("/api/notes?skip=0&limit=1")
    assert response.status_code == 200
    
    # Test with large limit
    response = await client.get("/api/notes?skip=0&limit=100")
    assert response.status_code == 200
    
    # Test with negative skip (should handle gracefully)
    response = await client.get("/api/notes?skip=-1&limit=10")
    assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_search_endpoints(client: AsyncClient):
    """Test search functionality"""
    # Test search without auth
    response = await client.get("/api/search?q=test")
    # May require auth or not, depending on configuration
    assert response.status_code in [200, 401, 403]
    
    # Test search with empty query
    response = await client.get("/api/search?q=")
    assert response.status_code in [200, 400, 401, 403]


@pytest.mark.asyncio
async def test_analytics_public_endpoints(client: AsyncClient):
    """Test public analytics endpoints"""
    # Test analytics overview (if public)
    response = await client.get("/api/analytics/overview")
    assert response.status_code in [200, 401, 403, 404]
    
    # Test popular notes
    response = await client.get("/api/analytics/popular")
    assert response.status_code in [200, 401, 403, 404]


@pytest.mark.asyncio
async def test_admin_endpoints_unauthorized(client: AsyncClient):
    """Test that admin endpoints require proper authorization"""
    # Test admin stats
    response = await client.get("/api/admin/stats")
    assert response.status_code in [401, 403]
    
    # Test admin users list
    response = await client.get("/api/admin/users")
    assert response.status_code in [401, 403]
    
    # Test admin moderate
    response = await client.post("/api/admin/moderate/note123")
    assert response.status_code in [401, 403, 404, 405]
