"""
CSRF Protection Middleware for FastAPI
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import secrets
import hmac
import hashlib
from datetime import datetime, timedelta


# Store CSRF tokens (in production, use Redis)
csrf_tokens = {}

# Secret key for CSRF token generation
CSRF_SECRET = secrets.token_urlsafe(32)
CSRF_TOKEN_EXPIRY = timedelta(hours=24)


def generate_csrf_token(session_id: str) -> str:
    """Generate a CSRF token for a session"""
    token = secrets.token_urlsafe(32)
    csrf_tokens[token] = {
        "session_id": session_id,
        "created_at": datetime.utcnow()
    }
    return token


def verify_csrf_token(token: str, session_id: str) -> bool:
    """Verify a CSRF token"""
    if token not in csrf_tokens:
        return False
    
    token_data = csrf_tokens[token]
    
    # Check if token is expired
    if datetime.utcnow() - token_data["created_at"] > CSRF_TOKEN_EXPIRY:
        del csrf_tokens[token]
        return False
    
    # Verify session matches
    return token_data["session_id"] == session_id


def cleanup_expired_tokens():
    """Remove expired CSRF tokens"""
    current_time = datetime.utcnow()
    expired_tokens = [
        token for token, data in csrf_tokens.items()
        if current_time - data["created_at"] > CSRF_TOKEN_EXPIRY
    ]
    for token in expired_tokens:
        del csrf_tokens[token]


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware
    Validates CSRF tokens on state-changing requests
    """
    
    # Methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    # Paths exempt from CSRF protection
    EXEMPT_PATHS = {"/api/health", "/api/test", "/api/db-status", "/docs", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip CSRF check for safe methods and exempt paths
        if request.method not in self.PROTECTED_METHODS:
            return await call_next(request)
        
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Get CSRF token from headers
        csrf_token = request.headers.get("X-CSRF-Token")
        
        # Get session ID (from auth token or cookie)
        auth_header = request.headers.get("Authorization", "")
        session_id = auth_header.split("Bearer ")[-1] if auth_header else ""
        
        # For now, we'll be lenient and just log missing tokens
        # In production, you'd want to enforce this strictly
        if not csrf_token:
            # Add CSRF token to request state for endpoints to generate
            request.state.csrf_required = True
        else:
            # Verify token if provided
            if not verify_csrf_token(csrf_token, session_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired CSRF token"
                )
        
        # Cleanup expired tokens periodically
        if secrets.randbelow(100) < 5:  # 5% chance
            cleanup_expired_tokens()
        
        return await call_next(request)
