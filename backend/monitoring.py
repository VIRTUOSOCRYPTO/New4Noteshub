"""
Error Monitoring and Tracking
Integrates with Sentry for production error tracking
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from functools import wraps

# Try to import sentry_sdk, but make it optional
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    print("⚠️  Sentry SDK not installed. Error monitoring disabled.")
    print("   Install with: pip install sentry-sdk")


class ErrorMonitor:
    """Centralized error monitoring and tracking"""
    
    def __init__(self):
        self.enabled = False
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.environment = os.getenv("NODE_ENV", "development")
        
        # Initialize Sentry if available and configured
        if SENTRY_AVAILABLE and self.sentry_dsn:
            self._init_sentry()
        else:
            self._init_fallback()
    
    def _init_sentry(self):
        """Initialize Sentry SDK"""
        try:
            sentry_sdk.init(
                dsn=self.sentry_dsn,
                environment=self.environment,
                traces_sample_rate=0.1 if self.environment == "production" else 1.0,
                profiles_sample_rate=0.1 if self.environment == "production" else 1.0,
                integrations=[
                    FastApiIntegration(),
                    LoggingIntegration(
                        level=logging.INFO,
                        event_level=logging.ERROR
                    )
                ],
                # Set release version if available
                release=os.getenv("APP_VERSION", "unknown"),
                # Enable performance monitoring
                enable_tracing=True,
                # Send default PII (Personally Identifiable Information)
                send_default_pii=False,
                # Set sample rate for error events
                sample_rate=1.0,
            )
            self.enabled = True
            print("✅ Sentry error monitoring initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Sentry: {e}")
            self._init_fallback()
    
    def _init_fallback(self):
        """Initialize fallback logging when Sentry is not available"""
        self.enabled = False
        print("📝 Using fallback error logging (file-based)")
        
        # Configure file-based error logging
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(f"{log_dir}/errors.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def capture_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        level: str = "error"
    ):
        """
        Capture an exception with context
        
        Args:
            exception: The exception to capture
            context: Additional context information
            user_id: User ID if available
            level: Severity level (error, warning, info)
        """
        if self.enabled and SENTRY_AVAILABLE:
            # Set context in Sentry
            if context:
                sentry_sdk.set_context("additional_info", context)
            
            if user_id:
                sentry_sdk.set_user({"id": user_id})
            
            # Capture the exception
            sentry_sdk.capture_exception(exception)
        else:
            # Fallback to logging
            logger = logging.getLogger(__name__)
            log_msg = f"Exception: {str(exception)}"
            if context:
                log_msg += f" | Context: {context}"
            if user_id:
                log_msg += f" | User: {user_id}"
            
            logger.error(log_msg, exc_info=True)
    
    def capture_message(
        self,
        message: str,
        level: str = "info",
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Capture a message without an exception
        
        Args:
            message: The message to capture
            level: Severity level (error, warning, info, debug)
            context: Additional context information
        """
        if self.enabled and SENTRY_AVAILABLE:
            if context:
                sentry_sdk.set_context("additional_info", context)
            
            sentry_sdk.capture_message(message, level=level)
        else:
            logger = logging.getLogger(__name__)
            log_msg = message
            if context:
                log_msg += f" | Context: {context}"
            
            if level == "error":
                logger.error(log_msg)
            elif level == "warning":
                logger.warning(log_msg)
            elif level == "debug":
                logger.debug(log_msg)
            else:
                logger.info(log_msg)
    
    def set_user(self, user_id: str, email: Optional[str] = None, username: Optional[str] = None):
        """Set user context for error tracking"""
        if self.enabled and SENTRY_AVAILABLE:
            user_data = {"id": user_id}
            if email:
                user_data["email"] = email
            if username:
                user_data["username"] = username
            sentry_sdk.set_user(user_data)
    
    def set_tag(self, key: str, value: str):
        """Set a tag for filtering errors"""
        if self.enabled and SENTRY_AVAILABLE:
            sentry_sdk.set_tag(key, value)
    
    def start_transaction(self, name: str, op: str = "http.server"):
        """Start a performance transaction"""
        if self.enabled and SENTRY_AVAILABLE:
            return sentry_sdk.start_transaction(name=name, op=op)
        return None
    
    def add_breadcrumb(
        self,
        message: str,
        category: str = "default",
        level: str = "info",
        data: Optional[Dict[str, Any]] = None
    ):
        """Add a breadcrumb for debugging"""
        if self.enabled and SENTRY_AVAILABLE:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data or {}
            )


# Global instance
error_monitor = ErrorMonitor()


def monitor_errors(func):
    """Decorator to automatically monitor function errors"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_monitor.capture_exception(
                e,
                context={
                    "function": func.__name__,
                    "args": str(args)[:200],  # Limit size
                }
            )
            raise
    return wrapper


# Performance monitoring decorator
def monitor_performance(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            transaction = error_monitor.start_transaction(
                name=operation_name,
                op="function"
            )
            
            try:
                result = await func(*args, **kwargs)
                if transaction:
                    transaction.set_status("ok")
                return result
            except Exception as e:
                if transaction:
                    transaction.set_status("error")
                raise
            finally:
                if transaction:
                    transaction.finish()
        
        return wrapper
    return decorator


# Request tracking
class RequestTracker:
    """Track requests for monitoring"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.start_time = datetime.utcnow()
    
    def track_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Track a request"""
        self.request_count += 1
        
        if status_code >= 400:
            self.error_count += 1
        
        # Add breadcrumb for Sentry
        error_monitor.add_breadcrumb(
            message=f"{method} {path}",
            category="request",
            level="info" if status_code < 400 else "error",
            data={
                "status_code": status_code,
                "duration_ms": duration_ms,
                "method": method,
                "path": path
            }
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracking statistics"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "uptime_seconds": uptime
        }


request_tracker = RequestTracker()
