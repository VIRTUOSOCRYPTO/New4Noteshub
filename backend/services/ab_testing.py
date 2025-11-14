"""
A/B Testing Service
Experiment management and variant assignment
"""
import os
import hashlib
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Experiment status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class ABTestingService:
    """
    A/B testing service for controlled experiments
    Supports multiple variants and metric tracking
    """
    
    def __init__(self, database=None):
        self.db = database
        self.cache = {}  # Cache experiment assignments
        
        logger.info("A/B testing service initialized")
    
    async def get_variant(
        self,
        experiment_name: str,
        user_id: str,
        default_variant: str = "control"
    ) -> str:
        """
        Get experiment variant for a user
        
        Args:
            experiment_name: Name of the experiment
            user_id: User ID
            default_variant: Default variant if experiment not found
        
        Returns:
            Variant name
        """
        # Check cache first
        cache_key = f"{experiment_name}:{user_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if not self.db:
            return default_variant
        
        try:
            # Get experiment
            experiment = await self.db.experiments.find_one({
                "name": experiment_name,
                "status": ExperimentStatus.RUNNING
            })
            
            if not experiment:
                return default_variant
            
            # Check if user already has an assignment
            assignment = await self.db.experiment_assignments.find_one({
                "experiment_id": str(experiment["_id"]),
                "user_id": user_id
            })
            
            if assignment:
                variant = assignment["variant"]
                self.cache[cache_key] = variant
                return variant
            
            # Assign new variant using consistent hashing
            variant = self._assign_variant(experiment, user_id)
            
            # Store assignment
            await self.db.experiment_assignments.insert_one({
                "experiment_id": str(experiment["_id"]),
                "experiment_name": experiment_name,
                "user_id": user_id,
                "variant": variant,
                "assigned_at": datetime.utcnow()
            })
            
            # Cache assignment
            self.cache[cache_key] = variant
            
            return variant
        
        except Exception as e:
            logger.error(f"Error getting variant for {experiment_name}: {str(e)}")
            return default_variant
    
    def _assign_variant(self, experiment: Dict[str, Any], user_id: str) -> str:
        """
        Assign a variant to a user using consistent hashing
        
        Args:
            experiment: Experiment document
            user_id: User ID
        
        Returns:
            Assigned variant name
        """
        # Get variants and their traffic percentages
        variants = experiment.get("variants", [])
        
        if not variants:
            return "control"
        
        # Use MD5 hash for consistent assignment
        hash_input = f"{experiment['name']}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100  # 0-99
        
        # Assign based on traffic allocation
        cumulative = 0
        for variant in variants:
            cumulative += variant.get("traffic_percentage", 0)
            if bucket < cumulative:
                return variant["name"]
        
        # Fallback to first variant
        return variants[0]["name"]
    
    async def track_metric(
        self,
        experiment_name: str,
        user_id: str,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track a metric for an experiment
        
        Args:
            experiment_name: Name of the experiment
            user_id: User ID
            metric_name: Metric name to track
            value: Metric value
            metadata: Additional metadata
        
        Returns:
            True if tracked successfully
        """
        if not self.db:
            return False
        
        try:
            # Get user's variant
            variant = await self.get_variant(experiment_name, user_id)
            
            # Store metric
            await self.db.experiment_metrics.insert_one({
                "experiment_name": experiment_name,
                "user_id": user_id,
                "variant": variant,
                "metric_name": metric_name,
                "value": value,
                "metadata": metadata or {},
                "tracked_at": datetime.utcnow()
            })
            
            return True
        
        except Exception as e:
            logger.error(f"Error tracking metric: {str(e)}")
            return False
    
    async def create_experiment(
        self,
        name: str,
        description: str,
        variants: List[Dict[str, Any]],
        metrics: List[str],
        status: ExperimentStatus = ExperimentStatus.DRAFT
    ) -> Dict[str, Any]:
        """
        Create a new A/B test experiment
        
        Args:
            name: Unique experiment name
            description: Experiment description
            variants: List of variants with traffic percentages
                     [{'name': 'control', 'traffic_percentage': 50}, ...]
            metrics: List of metric names to track
            status: Initial status
        
        Returns:
            Created experiment document
        """
        if not self.db:
            raise Exception("Database not configured")
        
        # Validate traffic percentages sum to 100
        total_traffic = sum(v.get("traffic_percentage", 0) for v in variants)
        if total_traffic != 100:
            raise Exception(f"Traffic percentages must sum to 100, got {total_traffic}")
        
        # Check if experiment exists
        existing = await self.db.experiments.find_one({"name": name})
        if existing:
            raise Exception(f"Experiment '{name}' already exists")
        
        experiment_doc = {
            "name": name,
            "description": description,
            "variants": variants,
            "metrics": metrics,
            "status": status,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None
        }
        
        result = await self.db.experiments.insert_one(experiment_doc)
        experiment_doc["id"] = str(result.inserted_id)
        del experiment_doc["_id"]
        
        logger.info(f"Experiment created: {name}")
        return experiment_doc
    
    async def update_experiment_status(
        self,
        name: str,
        status: ExperimentStatus
    ) -> Dict[str, Any]:
        """
        Update experiment status
        
        Args:
            name: Experiment name
            status: New status
        
        Returns:
            Updated experiment document
        """
        if not self.db:
            raise Exception("Database not configured")
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        # Set timestamps based on status
        if status == ExperimentStatus.RUNNING:
            update_data["started_at"] = datetime.utcnow()
        elif status == ExperimentStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        
        result = await self.db.experiments.find_one_and_update(
            {"name": name},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise Exception(f"Experiment '{name}' not found")
        
        # Clear cache if paused or completed
        if status in [ExperimentStatus.PAUSED, ExperimentStatus.COMPLETED]:
            self.cache = {k: v for k, v in self.cache.items() if not k.startswith(f"{name}:")}
        
        result["id"] = str(result["_id"])
        del result["_id"]
        
        logger.info(f"Experiment status updated: {name} -> {status}")
        return result
    
    async def get_experiment_results(self, experiment_name: str) -> Dict[str, Any]:
        """
        Get experiment results with statistics
        
        Args:
            experiment_name: Name of the experiment
        
        Returns:
            Dictionary with experiment results
        """
        if not self.db:
            return {}
        
        try:
            # Get experiment
            experiment = await self.db.experiments.find_one({"name": experiment_name})
            if not experiment:
                return {"error": "Experiment not found"}
            
            # Get assignment counts
            pipeline = [
                {"$match": {"experiment_name": experiment_name}},
                {"$group": {
                    "_id": "$variant",
                    "count": {"$sum": 1}
                }}
            ]
            
            assignment_counts = {}
            async for result in self.db.experiment_assignments.aggregate(pipeline):
                assignment_counts[result["_id"]] = result["count"]
            
            # Get metrics by variant
            metrics_by_variant = {}
            
            for metric_name in experiment.get("metrics", []):
                pipeline = [
                    {
                        "$match": {
                            "experiment_name": experiment_name,
                            "metric_name": metric_name
                        }
                    },
                    {
                        "$group": {
                            "_id": "$variant",
                            "count": {"$sum": 1},
                            "sum": {"$sum": "$value"},
                            "avg": {"$avg": "$value"},
                            "min": {"$min": "$value"},
                            "max": {"$max": "$value"}
                        }
                    }
                ]
                
                variant_metrics = {}
                async for result in self.db.experiment_metrics.aggregate(pipeline):
                    variant_metrics[result["_id"]] = {
                        "count": result["count"],
                        "sum": result["sum"],
                        "avg": result["avg"],
                        "min": result["min"],
                        "max": result["max"]
                    }
                
                metrics_by_variant[metric_name] = variant_metrics
            
            return {
                "experiment_name": experiment_name,
                "status": experiment.get("status"),
                "variants": experiment.get("variants", []),
                "assignment_counts": assignment_counts,
                "metrics": metrics_by_variant,
                "started_at": experiment.get("started_at"),
                "completed_at": experiment.get("completed_at")
            }
        
        except Exception as e:
            logger.error(f"Error getting experiment results: {str(e)}")
            return {"error": str(e)}
    
    async def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[Dict[str, Any]]:
        """
        List all experiments
        
        Args:
            status: Optional status filter
        
        Returns:
            List of experiments
        """
        if not self.db:
            return []
        
        query = {}
        if status:
            query["status"] = status
        
        cursor = self.db.experiments.find(query)
        experiments = await cursor.to_list(length=1000)
        
        for exp in experiments:
            exp["id"] = str(exp["_id"])
            del exp["_id"]
        
        return experiments


# Global A/B testing service instance
ab_testing = ABTestingService()
