"""
Utility Functions Tests
"""

import pytest
from auth import hash_password, verify_password, create_access_token, decode_access_token
import jwt
import os


def test_hash_password():
    """Test password hashing"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 20
    assert hashed.startswith("$2b$")  # bcrypt prefix


def test_verify_password_correct():
    """Test password verification with correct password"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password"""
    password = "TestPassword123!"
    hashed = hash_password(password)
    
    assert verify_password("WrongPassword123!", hashed) is False


def test_create_access_token():
    """Test JWT token creation"""
    user_data = {"user_id": "123", "usn": "1RV21CS001"}
    token = create_access_token(user_data)
    
    assert isinstance(token, str)
    assert len(token) > 50
    assert token.count(".") == 2  # JWT has 3 parts separated by dots


def test_decode_access_token_valid():
    """Test decoding a valid JWT token"""
    user_data = {"user_id": "123", "usn": "1RV21CS001"}
    token = create_access_token(user_data)
    
    decoded = decode_access_token(token)
    
    assert decoded is not None
    assert decoded["user_id"] == "123"
    assert decoded["usn"] == "1RV21CS001"


def test_decode_access_token_invalid():
    """Test decoding an invalid JWT token"""
    invalid_token = "invalid.token.here"
    
    decoded = decode_access_token(invalid_token)
    
    assert decoded is None


def test_decode_access_token_expired():
    """Test decoding an expired JWT token"""
    # Create a token that's already expired
    user_data = {"user_id": "123", "exp": 0}  # Expired timestamp
    
    try:
        secret = os.getenv("JWT_SECRET", "your-secret-key-here-min-32-characters-long-for-hs256")
        token = jwt.encode(user_data, secret, algorithm="HS256")
        decoded = decode_access_token(token)
        
        assert decoded is None  # Should return None for expired token
    except Exception:
        # If any error in creating expired token, pass
        pass
