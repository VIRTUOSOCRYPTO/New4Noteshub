"""
Model Validation Tests
"""

import pytest
from pydantic import ValidationError
from models import (
    UserRegistration,
    UserLogin,
    NoteUpload,
    NoteFilter
)


def test_user_registration_valid():
    """Test valid user registration data"""
    data = {
        "usn": "1RV21CS001",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "SecurePass123!",
        "department": "CSE",
        "college": "Test College",
        "year": 2
    }
    
    user = UserRegistration(**data)
    assert user.usn == "1RV21CS001"
    assert user.email == "test@example.com"
    assert user.department == "CSE"


def test_user_registration_invalid_department():
    """Test user registration with invalid department"""
    data = {
        "usn": "1RV21CS001",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "SecurePass123!",
        "department": "INVALID",
        "college": "Test College",
        "year": 2
    }
    
    with pytest.raises(ValidationError):
        UserRegistration(**data)


def test_user_registration_invalid_year():
    """Test user registration with invalid year"""
    data = {
        "usn": "1RV21CS001",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "confirmPassword": "SecurePass123!",
        "department": "CSE",
        "college": "Test College",
        "year": 10  # Invalid year
    }
    
    with pytest.raises(ValidationError):
        UserRegistration(**data)


def test_user_login_valid():
    """Test valid login data"""
    data = {
        "usn": "1RV21CS001",
        "password": "SecurePass123!"
    }
    
    login = UserLogin(**data)
    assert login.usn == "1RV21CS001"
    assert login.password == "SecurePass123!"


def test_note_filter_valid():
    """Test valid note filter"""
    filter_data = {
        "department": "CSE",
        "year": 2,
        "subject": "Mathematics"
    }
    
    note_filter = NoteFilter(**filter_data)
    assert note_filter.department == "CSE"
    assert note_filter.year == 2
    assert note_filter.subject == "Mathematics"


def test_note_filter_optional_fields():
    """Test note filter with optional fields"""
    # All fields are optional in filter
    filter_data = {}
    
    note_filter = NoteFilter(**filter_data)
    assert note_filter.department is None
    assert note_filter.year is None
