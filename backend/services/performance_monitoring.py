"""
Enhanced Performance Monitoring Service
Extends Sentry with custom metrics and database query tracking
"""
import os
import time
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
import logging
from collections import defaultdict

try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

logger = logging.getLogger(__name__)


class PerformanceMonitoringService:
    """
    Enhanced performance monitoring with custom metrics
    """
    
    def __init__(self):
        self.enabled = os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true"
        self.slow_query_threshold = float(os.getenv("SLOW_QUERY_THRESHOLD_MS", "100"))
        self.slow_endpoint_threshold = float(os.getenv("SLOW_ENDPOINT_THRESHOLD_MS", "1000"))
        
        # Metrics storage
        self.endpoint_metrics = defaultdict(list)
        self.query_metrics = defaultdict(list)
        self.custom_metrics = defaultdict(list)
        
        # Alert thresholds
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5%
            "p95_response_time": 2000,  # 2 seconds
            "memory_usage_percent": 90,
        }
        
        logger.info(f"Performance monitoring initialized (enabled: {self.enabled})")
    
    def track_endpoint(
        self,
        method: str,
        path: str,
        duration_ms: float,
        status_code: int,
        user_id: Optional[str] = None
    ):
        """
        Track API endpoint performance
        
        Args:
            method: HTTP method
            path: Endpoint path
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
            user_id: Optional user ID
        """
        endpoint_key = f"{method} {path}"
        
        self.endpoint_metrics[endpoint_key].append({
            "duration_ms": duration_ms,
            "status_code": status_code,
            "timestamp": datetime.utcnow(),
            "user_id": user_id
        })
        
        # Check for slow endpoints
        if duration_ms > self.slow_endpoint_threshold:
            logger.warning(
                f"Slow endpoint detected: {endpoint_key} took {duration_ms}ms",
                extra={
                    "endpoint": endpoint_key,
                    "duration_ms": duration_ms,
                    "status_code": status_code
                }
            )
            
            if SENTRY_AVAILABLE and self.enabled:
                sentry_sdk.capture_message(
                    f"Slow endpoint: {endpoint_key}",
                    level="warning",
                    extras={
                        "duration_ms": duration_ms,
                        "threshold_ms": self.slow_endpoint_threshold
                    }
                )
        
        # Send to Sentry if available
        if SENTRY_AVAILABLE and self.enabled:
            with sentry_sdk.start_transaction(op="http.server", name=endpoint_key) as transaction:
                transaction.set_measurement("duration", duration_ms, "millisecond")
                transaction.set_tag("status_code", status_code)
                if user_id:
                    transaction.set_tag("user_id", user_id)
    
    def track_database_query(
        self,
        collection: str,
        operation: str,
        duration_ms: float,
        query: Optional[Dict[str, Any]] = None
    ):
        """
        Track database query performance
        
        Args:
            collection: Database collection name
            operation: Operation type (find, insert, update, etc.)
            duration_ms: Query duration in milliseconds
            query: Optional query details
        """
        query_key = f"{collection}.{operation}"
        
        self.query_metrics[query_key].append({
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow(),
            "query": str(query) if query else None
        })
        
        # Check for slow queries
        if duration_ms > self.slow_query_threshold:
            logger.warning(
                f"Slow query detected: {query_key} took {duration_ms}ms",
                extra={
                    "query": query_key,
                    "duration_ms": duration_ms,
                    "query_details": str(query)[:200] if query else None
                }
            )
            
            if SENTRY_AVAILABLE and self.enabled:
                sentry_sdk.capture_message(
                    f"Slow database query: {query_key}",
                    level="warning",
                    extras={
                        "duration_ms": duration_ms,
                        "threshold_ms": self.slow_query_threshold,
                        "query": str(query)[:500] if query else None
                    }
                )
    
    def track_custom_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ):
        """
        Track custom application metrics
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for filtering
        """
        self.custom_metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.utcnow(),
            "tags": tags or {}
        })
        
        # Send to Sentry if available
        if SENTRY_AVAILABLE and self.enabled:
            sentry_sdk.set_measurement(metric_name, value)
    
    def get_endpoint_stats(
        self,
        endpoint: Optional[str] = None,
        minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get endpoint performance statistics
        
        Args:
            endpoint: Optional specific endpoint
            minutes: Time window in minutes
        
        Returns:
            Dictionary with performance statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        stats = {}
        
        endpoints = [endpoint] if endpoint else self.endpoint_metrics.keys()
        
        for ep in endpoints:
            metrics = self.endpoint_metrics.get(ep, [])
            
            # Filter by time window
            recent_metrics = [
                m for m in metrics
                if m["timestamp"] > cutoff_time
            ]
            
            if not recent_metrics:
                continue
            
            durations = [m["duration_ms"] for m in recent_metrics]
            durations.sort()
            
            error_count = sum(1 for m in recent_metrics if m["status_code"] >= 400)
            
            stats[ep] = {
                "count": len(recent_metrics),
                "avg_duration_ms": sum(durations) / len(durations),
                "p50_duration_ms": durations[len(durations) // 2],
                "p95_duration_ms": durations[int(len(durations) * 0.95)],
                "p99_duration_ms": durations[int(len(durations) * 0.99)],
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "error_count": error_count,
                "error_rate": error_count / len(recent_metrics) if recent_metrics else 0
            }
        
        return stats
    
    def get_query_stats(
        self,
        collection: Optional[str] = None,
        minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Get database query performance statistics
        
        Args:
            collection: Optional specific collection
            minutes: Time window in minutes
        
        Returns:
            Dictionary with query statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        stats = {}
        
        queries = self.query_metrics.keys()
        if collection:
            queries = [q for q in queries if q.startswith(f"{collection}.")]
        
        for query in queries:
            metrics = self.query_metrics.get(query, [])
            
            # Filter by time window
            recent_metrics = [
                m for m in metrics
                if m["timestamp"] > cutoff_time
            ]
            
            if not recent_metrics:
                continue
            
            durations = [m["duration_ms"] for m in recent_metrics]
            durations.sort()
            
            stats[query] = {
                "count": len(recent_metrics),
                "avg_duration_ms": sum(durations) / len(durations),
                "p95_duration_ms": durations[int(len(durations) * 0.95)],
                "max_duration_ms": max(durations),
                "slow_query_count": sum(1 for d in durations if d > self.slow_query_threshold)
            }
        
        return stats
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """
        Check for performance alerts
        
        Returns:
            List of active alerts
        """
        alerts = []
        endpoint_stats = self.get_endpoint_stats()
        
        for endpoint, stats in endpoint_stats.items():
            # Check error rate
            if stats["error_rate"] > self.alert_thresholds["error_rate"]:
                alerts.append({
                    "type": "high_error_rate",
                    "endpoint": endpoint,
                    "value": stats["error_rate"],
                    "threshold": self.alert_thresholds["error_rate"],
                    "severity": "critical"
                })
            
            # Check p95 response time
            if stats["p95_duration_ms"] > self.alert_thresholds["p95_response_time"]:
                alerts.append({
                    "type": "slow_response_time",
                    "endpoint": endpoint,
                    "value": stats["p95_duration_ms"],
                    "threshold": self.alert_thresholds["p95_response_time"],
                    "severity": "warning"
                })
        
        # Send alerts to Sentry
        if alerts and SENTRY_AVAILABLE and self.enabled:
            for alert in alerts:
                sentry_sdk.capture_message(
                    f"Performance Alert: {alert['type']}",
                    level=alert['severity'],
                    extras=alert
                )
        
        return alerts
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.endpoint_metrics.clear()
        self.query_metrics.clear()
        self.custom_metrics.clear()
        logger.info("Performance metrics reset")


# Decorator for automatic endpoint tracking
def track_performance(endpoint_name: Optional[str] = None):
    """Decorator to automatically track function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                name = endpoint_name or func.__name__
                performance_monitoring.track_custom_metric(
                    f"function.{name}.duration",
                    duration_ms
                )
                
                return result
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"Function {func.__name__} failed after {duration_ms}ms: {str(e)}")
                raise
        
        return wrapper
    return decorator


# Global performance monitoring instance
performance_monitoring = PerformanceMonitoringService()
