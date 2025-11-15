"""
Exception Handling Tests
"""

import pytest
from exceptions import (
    AuthenticationError,
    ValidationError as CustomValidationError,
    NotFoundError,
    PermissionError as CustomPermissionError
)


def test_authentication_error():
    """Test AuthenticationError"""
    error = AuthenticationError("Invalid credentials")
    assert str(error) == "Invalid credentials"
    assert error.status_code == 401


def test_validation_error():
    """Test ValidationError"""
    error = CustomValidationError("Invalid input")
    assert str(error) == "Invalid input"
    assert error.status_code == 400


def test_not_found_error():
    """Test NotFoundError"""
    error = NotFoundError("Resource not found")
    assert str(error) == "Resource not found"
    assert error.status_code == 404


def test_permission_error():
    """Test PermissionError"""
    error = CustomPermissionError("Access denied")
    assert str(error) == "Access denied"
    assert error.status_code == 403
