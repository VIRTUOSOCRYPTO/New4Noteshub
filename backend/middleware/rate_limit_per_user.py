"""
Per-User Rate Limiting Middleware
More granular than IP-based rate limiting
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio


class RateLimitStore:
    """In-memory rate limit store (use Redis in production)"""
    
    def __init__(self):
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def add_request(self, key: str, window: timedelta) -> int:
        """Add a request and return current count in window"""
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - window
            
            # Remove old requests outside the window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            # Add current request
            self.requests[key].append(now)
            
            return len(self.requests[key])
    
    async def get_count(self, key: str, window: timedelta) -> int:
        """Get current request count in window"""
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - window
            
            # Remove old requests
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
            
            return len(self.requests[key])
    
    async def cleanup(self):
        """Cleanup old entries"""
        async with self.lock:
            now = datetime.utcnow()
            keys_to_delete = []
            
            for key, requests in self.requests.items():
                # Remove requests older than 1 hour
                cutoff = now - timedelta(hours=1)
                self.requests[key] = [
                    req_time for req_time in requests
                    if req_time > cutoff
                ]
                
                # Mark empty keys for deletion
                if not self.requests[key]:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.requests[key]


# Global rate limit store
rate_limit_store = RateLimitStore()


class PerUserRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-User Rate Limiting
    Applies different rate limits based on user authentication status
    """
    
    # Rate limit configurations
    RATE_LIMITS = {
        # Authenticated users: 100 requests per minute
        "authenticated": {"max_requests": 100, "window": timedelta(minutes=1)},
        # Anonymous users: 20 requests per minute
        "anonymous": {"max_requests": 20, "window": timedelta(minutes=1)},
    }
    
    # Paths exempt from rate limiting
    EXEMPT_PATHS = {"/api/health", "/api/test", "/docs", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Determine user identity
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            # Authenticated user
            user_id = auth_header.split("Bearer ")[1][:32]  # Use first 32 chars of token
            rate_limit_key = f"user:{user_id}"
            limit_config = self.RATE_LIMITS["authenticated"]
        else:
            # Anonymous user (fall back to IP)
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_key = f"ip:{client_ip}"
            limit_config = self.RATE_LIMITS["anonymous"]
        
        # Check rate limit
        current_count = await rate_limit_store.add_request(
            rate_limit_key,
            limit_config["window"]
        )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit_config["max_requests"])
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, limit_config["max_requests"] - current_count)
        )
        
        # Check if limit exceeded
        if current_count > limit_config["max_requests"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "Retry-After": str(int(limit_config["window"].total_seconds()))
                }
            )
        
        return response


# Cleanup task (run periodically)
async def cleanup_rate_limits():
    """Periodic cleanup of old rate limit data"""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        await rate_limit_store.cleanup()
