"""
Redis Caching Service
Handles caching for notes, user profiles, and search results
"""
from typing import Optional, Any, Dict, List
import json
from datetime import timedelta
import hashlib


class CacheService:
    """
    Caching service with Redis backend
    Falls back to in-memory cache if Redis is unavailable
    """
    
    def __init__(self):
        self.redis_client = None
        self.in_memory_cache: Dict[str, Any] = {}
        self.cache_enabled = False
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio as redis
            # Try to connect to Redis
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.cache_enabled = True
            print("✓ Redis cache initialized successfully")
        except ImportError:
            print("⚠ Redis library not installed, using in-memory cache")
            self.cache_enabled = True
        except Exception as e:
            print(f"⚠ Redis connection failed: {e}, using in-memory cache")
            self.redis_client = None
            self.cache_enabled = True
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a cache key"""
        return f"{prefix}:{identifier}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.cache_enabled:
            return None
        
        try:
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.in_memory_cache.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 5 minutes)
        """
        if not self.cache_enabled:
            return False
        
        try:
            json_value = json.dumps(value, default=str)
            
            if self.redis_client:
                await self.redis_client.setex(key, ttl, json_value)
            else:
                self.in_memory_cache[key] = value
                # Simple in-memory expiration (would need background task for cleanup)
            
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.cache_enabled:
            return False
        
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
            else:
                self.in_memory_cache.pop(key, None)
            
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern
        
        Args:
            pattern: Pattern to match (e.g., "notes:*")
        
        Returns:
            Number of keys deleted
        """
        if not self.cache_enabled:
            return 0
        
        try:
            if self.redis_client:
                keys = []
                async for key in self.redis_client.scan_iter(match=pattern):
                    keys.append(key)
                
                if keys:
                    return await self.redis_client.delete(*keys)
                return 0
            else:
                # In-memory pattern matching
                keys_to_delete = [
                    k for k in self.in_memory_cache.keys()
                    if pattern.replace("*", "") in k
                ]
                for key in keys_to_delete:
                    del self.in_memory_cache[key]
                return len(keys_to_delete)
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return 0
    
    # Convenience methods for specific entities
    
    async def get_note(self, note_id: str) -> Optional[Dict]:
        """Get cached note by ID"""
        key = self._generate_key("note", note_id)
        return await self.get(key)
    
    async def set_note(self, note_id: str, note_data: Dict, ttl: int = 600) -> bool:
        """Cache note data (10 minutes default TTL)"""
        key = self._generate_key("note", note_id)
        return await self.set(key, note_data, ttl)
    
    async def invalidate_note(self, note_id: str) -> bool:
        """Invalidate cached note"""
        key = self._generate_key("note", note_id)
        return await self.delete(key)
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get cached user profile"""
        key = self._generate_key("user", user_id)
        return await self.get(key)
    
    async def set_user_profile(self, user_id: str, user_data: Dict, ttl: int = 900) -> bool:
        """Cache user profile (15 minutes default TTL)"""
        key = self._generate_key("user", user_id)
        return await self.set(key, user_data, ttl)
    
    async def invalidate_user_profile(self, user_id: str) -> bool:
        """Invalidate cached user profile"""
        key = self._generate_key("user", user_id)
        return await self.delete(key)
    
    async def get_notes_list(self, filters: Dict) -> Optional[List[Dict]]:
        """Get cached notes list"""
        # Create a unique key based on filters
        filter_str = json.dumps(filters, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()
        key = self._generate_key("notes_list", filter_hash)
        return await self.get(key)
    
    async def set_notes_list(self, filters: Dict, notes_data: List[Dict], ttl: int = 300) -> bool:
        """Cache notes list (5 minutes default TTL)"""
        filter_str = json.dumps(filters, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()
        key = self._generate_key("notes_list", filter_hash)
        return await self.set(key, notes_data, ttl)
    
    async def invalidate_all_notes_lists(self) -> int:
        """Invalidate all cached notes lists"""
        return await self.invalidate_pattern("notes_list:*")
    
    async def get_search_results(self, query: str, filters: Dict) -> Optional[List[Dict]]:
        """Get cached search results"""
        search_str = json.dumps({"query": query, **filters}, sort_keys=True)
        search_hash = hashlib.md5(search_str.encode()).hexdigest()
        key = self._generate_key("search", search_hash)
        return await self.get(key)
    
    async def set_search_results(self, query: str, filters: Dict, results: List[Dict], ttl: int = 600) -> bool:
        """Cache search results (10 minutes default TTL)"""
        search_str = json.dumps({"query": query, **filters}, sort_keys=True)
        search_hash = hashlib.md5(search_str.encode()).hexdigest()
        key = self._generate_key("search", search_hash)
        return await self.set(key, results, ttl)


# Global cache service instance
cache_service = CacheService()
