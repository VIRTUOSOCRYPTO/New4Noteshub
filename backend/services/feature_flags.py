"""
Feature Flags Service
Database-backed feature toggles for controlled rollouts
"""
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FeatureFlagStatus(str, Enum):
    """Feature flag status"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ROLLOUT = "rollout"  # Gradual rollout


class FeatureFlagService:
    """
    Feature flag management service
    Supports percentage-based rollouts and user/role targeting
    """
    
    def __init__(self, database=None):
        self.db = database
        self.cache = {}  # In-memory cache for performance
        self.cache_ttl = 60  # Cache TTL in seconds
        self.last_cache_update = {}
        
        logger.info("Feature flags service initialized")
    
    async def is_enabled(
        self,
        flag_name: str,
        user_id: Optional[str] = None,
        user_role: Optional[str] = None,
        default: bool = False
    ) -> bool:
        """
        Check if a feature flag is enabled
        
        Args:
            flag_name: Name of the feature flag
            user_id: Optional user ID for targeting
            user_role: Optional user role for targeting
            default: Default value if flag not found
        
        Returns:
            True if feature is enabled
        """
        # Check cache first
        if flag_name in self.cache:
            cache_age = datetime.utcnow().timestamp() - self.last_cache_update.get(flag_name, 0)
            if cache_age < self.cache_ttl:
                flag = self.cache[flag_name]
                return self._evaluate_flag(flag, user_id, user_role)
        
        # Fetch from database
        if self.db:
            try:
                flag = await self.db.feature_flags.find_one({"name": flag_name})
                
                if flag:
                    # Update cache
                    self.cache[flag_name] = flag
                    self.last_cache_update[flag_name] = datetime.utcnow().timestamp()
                    
                    return self._evaluate_flag(flag, user_id, user_role)
            
            except Exception as e:
                logger.error(f"Error fetching feature flag {flag_name}: {str(e)}")
        
        # Return default if not found
        return default
    
    def _evaluate_flag(
        self,
        flag: Dict[str, Any],
        user_id: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> bool:
        """
        Evaluate if flag is enabled for specific user/role
        
        Args:
            flag: Feature flag document
            user_id: Optional user ID
            user_role: Optional user role
        
        Returns:
            True if enabled for this context
        """
        # Check if flag is globally disabled
        if flag.get("status") == FeatureFlagStatus.DISABLED:
            return False
        
        # Check if flag is globally enabled
        if flag.get("status") == FeatureFlagStatus.ENABLED:
            return True
        
        # Rollout mode - check targeting rules
        if flag.get("status") == FeatureFlagStatus.ROLLOUT:
            # Check user whitelist
            if user_id and user_id in flag.get("whitelist_users", []):
                return True
            
            # Check role whitelist
            if user_role and user_role in flag.get("whitelist_roles", []):
                return True
            
            # Check percentage rollout
            rollout_percentage = flag.get("rollout_percentage", 0)
            if rollout_percentage > 0 and user_id:
                # Use hash of user_id for consistent assignment
                user_hash = hash(user_id) % 100
                return user_hash < rollout_percentage
        
        return False
    
    async def create_flag(
        self,
        name: str,
        description: str,
        status: FeatureFlagStatus = FeatureFlagStatus.DISABLED,
        rollout_percentage: int = 0,
        whitelist_users: Optional[List[str]] = None,
        whitelist_roles: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new feature flag
        
        Args:
            name: Unique flag name
            description: Flag description
            status: Initial status
            rollout_percentage: Percentage for gradual rollout (0-100)
            whitelist_users: List of user IDs to always enable
            whitelist_roles: List of roles to always enable
            metadata: Additional metadata
        
        Returns:
            Created flag document
        """
        if not self.db:
            raise Exception("Database not configured")
        
        # Check if flag already exists
        existing = await self.db.feature_flags.find_one({"name": name})
        if existing:
            raise Exception(f"Feature flag '{name}' already exists")
        
        flag_doc = {
            "name": name,
            "description": description,
            "status": status,
            "rollout_percentage": max(0, min(100, rollout_percentage)),
            "whitelist_users": whitelist_users or [],
            "whitelist_roles": whitelist_roles or [],
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await self.db.feature_flags.insert_one(flag_doc)
        flag_doc["id"] = str(result.inserted_id)
        del flag_doc["_id"]
        
        # Clear cache
        self.cache.pop(name, None)
        
        logger.info(f"Feature flag created: {name} (status: {status})")
        return flag_doc
    
    async def update_flag(
        self,
        name: str,
        status: Optional[FeatureFlagStatus] = None,
        rollout_percentage: Optional[int] = None,
        whitelist_users: Optional[List[str]] = None,
        whitelist_roles: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing feature flag
        
        Args:
            name: Flag name to update
            status: New status
            rollout_percentage: New rollout percentage
            whitelist_users: New user whitelist
            whitelist_roles: New role whitelist
            metadata: New metadata
        
        Returns:
            Updated flag document
        """
        if not self.db:
            raise Exception("Database not configured")
        
        update_data = {"updated_at": datetime.utcnow()}
        
        if status is not None:
            update_data["status"] = status
        
        if rollout_percentage is not None:
            update_data["rollout_percentage"] = max(0, min(100, rollout_percentage))
        
        if whitelist_users is not None:
            update_data["whitelist_users"] = whitelist_users
        
        if whitelist_roles is not None:
            update_data["whitelist_roles"] = whitelist_roles
        
        if metadata is not None:
            update_data["metadata"] = metadata
        
        result = await self.db.feature_flags.find_one_and_update(
            {"name": name},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise Exception(f"Feature flag '{name}' not found")
        
        # Clear cache
        self.cache.pop(name, None)
        
        logger.info(f"Feature flag updated: {name}")
        
        result["id"] = str(result["_id"])
        del result["_id"]
        return result
    
    async def delete_flag(self, name: str) -> bool:
        """
        Delete a feature flag
        
        Args:
            name: Flag name to delete
        
        Returns:
            True if deleted successfully
        """
        if not self.db:
            raise Exception("Database not configured")
        
        result = await self.db.feature_flags.delete_one({"name": name})
        
        # Clear cache
        self.cache.pop(name, None)
        
        if result.deleted_count > 0:
            logger.info(f"Feature flag deleted: {name}")
            return True
        
        return False
    
    async def list_flags(self) -> List[Dict[str, Any]]:
        """
        List all feature flags
        
        Returns:
            List of all feature flags
        """
        if not self.db:
            return []
        
        cursor = self.db.feature_flags.find({})
        flags = await cursor.to_list(length=1000)
        
        for flag in flags:
            flag["id"] = str(flag["_id"])
            del flag["_id"]
        
        return flags
    
    async def get_flag(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific feature flag
        
        Args:
            name: Flag name
        
        Returns:
            Flag document or None
        """
        if not self.db:
            return None
        
        flag = await self.db.feature_flags.find_one({"name": name})
        
        if flag:
            flag["id"] = str(flag["_id"])
            del flag["_id"]
        
        return flag
    
    def clear_cache(self):
        """Clear the feature flag cache"""
        self.cache.clear()
        self.last_cache_update.clear()
        logger.info("Feature flag cache cleared")


# Global feature flag service instance (initialized with database later)
feature_flags = FeatureFlagService()
