"""
Logging Middleware
Adds request ID tracking and performance monitoring
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

# Configure structured logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request logging and performance monitoring
    Adds request ID to all requests for tracing
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to headers
        request.state.start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - Started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - request.state.start_time
            duration_ms = round(duration * 1000, 2)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            log_level = logging.INFO
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING
            
            logger.log(
                log_level,
                f"[{request_id}] {request.method} {request.url.path} - "
                f"{response.status_code} ({duration_ms}ms)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
            
            return response
            
        except Exception as e:
            # Log exception
            duration = time.time() - request.state.start_time
            duration_ms = round(duration * 1000, 2)
            
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"Exception: {str(e)} ({duration_ms}ms)",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": duration_ms,
                }
            )
            raise


class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.request_times = []
        self.slow_requests = []
        self.error_count = 0
        self.request_count = 0
    
    def record_request(self, duration_ms: float, status_code: int, path: str):
        """Record request metrics"""
        self.request_count += 1
        self.request_times.append(duration_ms)
        
        # Track errors
        if status_code >= 400:
            self.error_count += 1
        
        # Track slow requests (> 1 second)
        if duration_ms > 1000:
            self.slow_requests.append({
                "path": path,
                "duration_ms": duration_ms,
                "status_code": status_code
            })
            
            # Keep only last 100 slow requests
            if len(self.slow_requests) > 100:
                self.slow_requests.pop(0)
    
    def get_stats(self) -> dict:
        """Get performance statistics"""
        if not self.request_times:
            return {
                "request_count": 0,
                "avg_duration_ms": 0,
                "p95_duration_ms": 0,
                "p99_duration_ms": 0,
                "error_count": 0,
                "error_rate": 0,
                "slow_request_count": len(self.slow_requests)
            }
        
        sorted_times = sorted(self.request_times)
        count = len(sorted_times)
        
        return {
            "request_count": self.request_count,
            "avg_duration_ms": round(sum(sorted_times) / count, 2),
            "p95_duration_ms": sorted_times[int(count * 0.95)] if count > 0 else 0,
            "p99_duration_ms": sorted_times[int(count * 0.99)] if count > 0 else 0,
            "error_count": self.error_count,
            "error_rate": round(self.error_count / self.request_count, 4) if self.request_count > 0 else 0,
            "slow_request_count": len(self.slow_requests)
        }
    
    def reset(self):
        """Reset metrics"""
        self.request_times = []
        self.slow_requests = []
        self.error_count = 0
        self.request_count = 0


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
