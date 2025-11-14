"""
Custom Exceptions
Standardized exception classes for better error handling
"""

from fastapi import HTTPException, status
from typing import Any, Optional, Dict


class NotesHubException(Exception):
    """Base exception for NotesHub"""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(NotesHubException):
    """Resource not found exception"""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)}
        )


class ValidationError(NotesHubException):
    """Data validation exception"""
    
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error on field '{field}': {message}",
            code="VALIDATION_ERROR",
            status_code=400,
            details={"field": field, "message": message}
        )


class AuthenticationError(NotesHubException):
    """Authentication failed exception"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationError(NotesHubException):
    """Authorization failed exception"""
    
    def __init__(self, message: str = "You don't have permission to perform this action"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403
        )


class DuplicateResourceError(NotesHubException):
    """Duplicate resource exception"""
    
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} with {field}='{value}' already exists",
            code="DUPLICATE_RESOURCE",
            status_code=409,
            details={"resource": resource, "field": field, "value": str(value)}
        )


class FileUploadError(NotesHubException):
    """File upload exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"File upload error: {message}",
            code="FILE_UPLOAD_ERROR",
            status_code=400,
            details=details or {}
        )


class FileNotFoundError(NotesHubException):
    """File not found exception"""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"File '{filename}' not found",
            code="FILE_NOT_FOUND",
            status_code=404,
            details={"filename": filename}
        )


class DatabaseError(NotesHubException):
    """Database operation exception"""
    
    def __init__(self, operation: str, message: str):
        super().__init__(
            message=f"Database {operation} failed: {message}",
            code="DATABASE_ERROR",
            status_code=500,
            details={"operation": operation}
        )


class ServiceUnavailableError(NotesHubException):
    """Service unavailable exception"""
    
    def __init__(self, service: str, message: str = ""):
        super().__init__(
            message=f"Service '{service}' is unavailable. {message}".strip(),
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            details={"service": service}
        )


class RateLimitError(NotesHubException):
    """Rate limit exceeded exception"""
    
    def __init__(self, limit: int, window: str):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window}",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"limit": limit, "window": window}
        )


def convert_to_http_exception(exc: NotesHubException) -> HTTPException:
    """Convert custom exception to FastAPI HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )
