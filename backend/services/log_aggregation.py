"""
Log Aggregation Service
Centralized logging with rotation, filtering, and search capabilities
"""
import os
import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path
import re


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra attributes
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName',
                          'relativeCreated', 'thread', 'threadName', 'exc_info',
                          'exc_text', 'stack_info']:
                log_data[key] = value
        
        return json.dumps(log_data)


class LogAggregationService:
    """
    Centralized log aggregation with multiple handlers and search capabilities
    """
    
    def __init__(self):
        self.log_dir = os.getenv("LOG_DIR", "/app/logs")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.json_logging = os.getenv("JSON_LOGGING", "true").lower() == "true"
        
        # Create log directory
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize loggers
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Log aggregation service initialized")
    
    def _setup_logging(self):
        """Setup logging configuration with multiple handlers"""
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        if self.json_logging:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
        root_logger.addHandler(console_handler)
        
        # Application log (rotating by size)
        app_log_path = Path(self.log_dir) / "app.log"
        app_handler = RotatingFileHandler(
            app_log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        app_handler.setLevel(logging.INFO)
        if self.json_logging:
            app_handler.setFormatter(JSONFormatter())
        else:
            app_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
        root_logger.addHandler(app_handler)
        
        # Error log (only errors and critical)
        error_log_path = Path(self.log_dir) / "error.log"
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        if self.json_logging:
            error_handler.setFormatter(JSONFormatter())
        else:
            error_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s\n%(pathname)s:%(lineno)d\n%(message)s\n',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
        root_logger.addHandler(error_handler)
        
        # Access log (time-based rotation - daily)
        access_log_path = Path(self.log_dir) / "access.log"
        access_handler = TimedRotatingFileHandler(
            access_log_path,
            when='midnight',
            interval=1,
            backupCount=30  # Keep 30 days
        )
        access_handler.setLevel(logging.INFO)
        access_handler.addFilter(AccessLogFilter())
        if self.json_logging:
            access_handler.setFormatter(JSONFormatter())
        else:
            access_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
        root_logger.addHandler(access_handler)
        
        # Security log (authentication, authorization events)
        security_log_path = Path(self.log_dir) / "security.log"
        security_handler = TimedRotatingFileHandler(
            security_log_path,
            when='midnight',
            interval=1,
            backupCount=90  # Keep 90 days for compliance
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.addFilter(SecurityLogFilter())
        if self.json_logging:
            security_handler.setFormatter(JSONFormatter())
        else:
            security_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
        root_logger.addHandler(security_handler)
    
    def search_logs(
        self,
        log_file: str = "app.log",
        pattern: Optional[str] = None,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search logs with filters
        
        Args:
            log_file: Log file name to search
            pattern: Regex pattern to match
            level: Log level filter (INFO, ERROR, etc.)
            start_time: Start timestamp filter
            end_time: End timestamp filter
            limit: Maximum number of results
        
        Returns:
            List of matching log entries
        """
        log_path = Path(self.log_dir) / log_file
        
        if not log_path.exists():
            return []
        
        results = []
        pattern_regex = re.compile(pattern) if pattern else None
        
        try:
            with open(log_path, 'r') as f:
                for line in f:
                    # Parse JSON logs
                    if self.json_logging:
                        try:
                            log_entry = json.loads(line)
                            
                            # Apply filters
                            if level and log_entry.get("level") != level:
                                continue
                            
                            if pattern_regex and not pattern_regex.search(log_entry.get("message", "")):
                                continue
                            
                            if start_time:
                                entry_time = datetime.fromisoformat(log_entry.get("timestamp"))
                                if entry_time < start_time:
                                    continue
                            
                            if end_time:
                                entry_time = datetime.fromisoformat(log_entry.get("timestamp"))
                                if entry_time > end_time:
                                    continue
                            
                            results.append(log_entry)
                            
                        except json.JSONDecodeError:
                            continue
                    else:
                        # Parse plain text logs
                        if pattern_regex and not pattern_regex.search(line):
                            continue
                        
                        if level and f"[{level}]" not in line:
                            continue
                        
                        results.append({"raw": line.strip()})
                    
                    if len(results) >= limit:
                        break
        
        except Exception as e:
            self.logger.error(f"Error searching logs: {str(e)}")
        
        return results
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get statistics about log files
        
        Returns:
            Dictionary with log file stats
        """
        stats = {
            "log_dir": self.log_dir,
            "files": []
        }
        
        log_dir = Path(self.log_dir)
        
        if not log_dir.exists():
            return stats
        
        total_size = 0
        
        for log_file in log_dir.glob("*.log*"):
            if log_file.is_file():
                size = log_file.stat().st_size
                total_size += size
                
                stats["files"].append({
                    "name": log_file.name,
                    "size_bytes": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                })
        
        stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        stats["file_count"] = len(stats["files"])
        
        return stats
    
    def get_recent_errors(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent error log entries
        
        Args:
            count: Number of recent errors to retrieve
        
        Returns:
            List of recent error entries
        """
        return self.search_logs(
            log_file="error.log",
            level="ERROR",
            limit=count
        )
    
    def cleanup_old_logs(self, days: int = 30) -> Dict[str, Any]:
        """
        Remove log files older than specified days
        
        Args:
            days: Number of days to keep
        
        Returns:
            Dictionary with cleanup results
        """
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0
        freed_space = 0
        
        log_dir = Path(self.log_dir)
        
        for log_file in log_dir.glob("*.log.*"):
            if log_file.is_file():
                modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if modified_time < cutoff_time:
                    size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_count += 1
                    freed_space += size
        
        return {
            "deleted_count": deleted_count,
            "freed_space_mb": round(freed_space / (1024 * 1024), 2)
        }


class AccessLogFilter(logging.Filter):
    """Filter to only allow access log messages"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Only log messages containing HTTP method and path
        message = record.getMessage()
        return any(method in message for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])


class SecurityLogFilter(logging.Filter):
    """Filter to only allow security-related log messages"""
    
    SECURITY_KEYWORDS = [
        'login', 'logout', 'authentication', 'authorization',
        'password', 'token', 'permission', 'access denied',
        'unauthorized', 'forbidden', 'security', 'failed attempt'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage().lower()
        return any(keyword in message for keyword in self.SECURITY_KEYWORDS)


# Global log aggregation service instance
log_aggregation = LogAggregationService()
