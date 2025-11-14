"""
Query Profiler Middleware
Monitors and logs slow database queries
"""

import time
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)

# Configuration
SLOW_QUERY_THRESHOLD_MS = 100  # Log queries slower than 100ms
VERY_SLOW_QUERY_THRESHOLD_MS = 1000  # Alert for queries slower than 1s


class QueryProfiler:
    """Profile database queries and detect slow queries"""
    
    def __init__(self):
        self.slow_queries = []
        self.query_stats = {}
    
    def profile_query(self, collection: str, operation: str):
        """Decorator to profile database queries"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    execution_time_ms = (time.time() - start_time) * 1000
                    
                    # Log slow queries
                    self._log_query(collection, operation, execution_time_ms, success=True)
                    
                    return result
                    
                except Exception as e:
                    execution_time_ms = (time.time() - start_time) * 1000
                    self._log_query(collection, operation, execution_time_ms, success=False, error=str(e))
                    raise
            
            return wrapper
        return decorator
    
    def _log_query(
        self,
        collection: str,
        operation: str,
        execution_time_ms: float,
        success: bool = True,
        error: str = None
    ):
        """Log query execution details"""
        query_key = f\"{collection}.{operation}\"
        
        # Update stats
        if query_key not in self.query_stats:
            self.query_stats[query_key] = {
                \"count\": 0,
                \"total_time\": 0,
                \"min_time\": float('inf'),
                \"max_time\": 0,
                \"slow_count\": 0,
                \"error_count\": 0
            }
        
        stats = self.query_stats[query_key]
        stats[\"count\"] += 1
        stats[\"total_time\"] += execution_time_ms
        stats[\"min_time\"] = min(stats[\"min_time\"], execution_time_ms)
        stats[\"max_time\"] = max(stats[\"max_time\"], execution_time_ms)
        
        if not success:
            stats[\"error_count\"] += 1
        
        # Check if slow query
        if execution_time_ms >= SLOW_QUERY_THRESHOLD_MS:
            stats[\"slow_count\"] += 1
            
            log_entry = {
                \"collection\": collection,
                \"operation\": operation,
                \"execution_time_ms\": round(execution_time_ms, 2),
                \"success\": success
            }
            
            if error:
                log_entry[\"error\"] = error
            
            # Log warning for slow queries
            if execution_time_ms >= VERY_SLOW_QUERY_THRESHOLD_MS:
                logger.warning(f\"Very slow query detected: {query_key} took {execution_time_ms:.2f}ms\", extra=log_entry)
            else:
                logger.info(f\"Slow query: {query_key} took {execution_time_ms:.2f}ms\", extra=log_entry)
            
            # Store for reporting
            self.slow_queries.append(log_entry)
            
            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]
    
    def get_stats(self):
        """Get query statistics"""
        stats_summary = []
        
        for query_key, stats in self.query_stats.items():
            avg_time = stats[\"total_time\"] / stats[\"count\"] if stats[\"count\"] > 0 else 0
            
            stats_summary.append({
                \"query\": query_key,
                \"count\": stats[\"count\"],
                \"avg_time_ms\": round(avg_time, 2),
                \"min_time_ms\": round(stats[\"min_time\"], 2) if stats[\"min_time\"] != float('inf') else 0,
                \"max_time_ms\": round(stats[\"max_time\"], 2),
                \"slow_count\": stats[\"slow_count\"],
                \"error_count\": stats[\"error_count\"],
                \"slow_percentage\": round((stats[\"slow_count\"] / stats[\"count\"]) * 100, 2) if stats[\"count\"] > 0 else 0
            })
        
        # Sort by average time (slowest first)
        stats_summary.sort(key=lambda x: x[\"avg_time_ms\"], reverse=True)
        
        return {
            \"queries\": stats_summary,
            \"total_queries\": sum(s[\"count\"] for s in stats_summary),
            \"total_slow_queries\": sum(s[\"slow_count\"] for s in stats_summary),
            \"recent_slow_queries\": self.slow_queries[-20:]  # Last 20 slow queries
        }
    
    def get_recommendations(self):
        """Get query optimization recommendations"""
        recommendations = []
        
        for query_key, stats in self.query_stats.items():
            avg_time = stats[\"total_time\"] / stats[\"count\"] if stats[\"count\"] > 0 else 0
            slow_percentage = (stats[\"slow_count\"] / stats[\"count\"]) * 100 if stats[\"count\"] > 0 else 0
            
            # Recommend indexing for consistently slow queries
            if avg_time > SLOW_QUERY_THRESHOLD_MS and stats[\"count\"] > 10:
                recommendations.append({
                    \"query\": query_key,
                    \"issue\": \"Consistently slow query\",
                    \"avg_time_ms\": round(avg_time, 2),
                    \"recommendation\": \"Consider adding an index or optimizing the query\",
                    \"priority\": \"high\" if avg_time > VERY_SLOW_QUERY_THRESHOLD_MS else \"medium\"
                })
            
            # Recommend optimization for frequently slow queries
            if slow_percentage > 50 and stats[\"count\"] > 5:
                recommendations.append({
                    \"query\": query_key,
                    \"issue\": f\"{slow_percentage:.1f}% of queries are slow\",
                    \"recommendation\": \"Query is frequently slow, review and optimize\",
                    \"priority\": \"high\"
                })
        
        return recommendations


# Global profiler instance
query_profiler = QueryProfiler()


def get_query_profiler() -> QueryProfiler:
    """Get the global query profiler instance"""
    return query_profiler
