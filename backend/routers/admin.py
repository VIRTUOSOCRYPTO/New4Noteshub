"""
Admin Routes
Management endpoints for backups, feature flags, A/B tests, and monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import logging

from middleware.admin_auth import require_admin
from database import get_database
from services.backup_service import backup_service
from services.feature_flags import feature_flags, FeatureFlagStatus
from services.ab_testing import ab_testing, ExperimentStatus
from services.log_aggregation import log_aggregation
from services.performance_monitoring import performance_monitoring
from services.virus_scanner import virus_scanner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ============================================================================
# BACKUP MANAGEMENT
# ============================================================================

@router.post("/backup/create")
async def create_backup(admin_id: str = Depends(require_admin)):
    """Create a new database backup"""
    result = backup_service.create_backup()
    
    if result["success"]:
        return {
            "message": "Backup created successfully",
            **result
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Backup failed"))


@router.get("/backup/list")
async def list_backups(admin_id: str = Depends(require_admin)):
    """List all available backups"""
    backups = backup_service.list_backups()
    return {
        "backups": backups,
        "count": len(backups)
    }


@router.post("/backup/restore/{backup_name}")
async def restore_backup(
    backup_name: str,
    admin_id: str = Depends(require_admin)
):
    """Restore from a backup (DANGEROUS - drops existing data)"""
    result = backup_service.restore_backup(backup_name)
    
    if result["success"]:
        return {
            "message": "Backup restored successfully",
            **result
        }
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Restore failed"))


@router.post("/backup/cleanup")
async def cleanup_backups(admin_id: str = Depends(require_admin)):
    """Cleanup old backups based on retention policy"""
    result = backup_service.cleanup_old_backups()
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Cleanup failed"))


# ============================================================================
# FEATURE FLAGS
# ============================================================================

@router.get("/feature-flags")
async def list_feature_flags(
    admin_id: str = Depends(require_admin),
    database = Depends(get_database)
):
    """List all feature flags"""
    if not feature_flags.db:
        feature_flags.db = database
    
    flags = await feature_flags.list_flags()
    return {"flags": flags, "count": len(flags)}


@router.post("/feature-flags")
async def create_feature_flag(
    name: str,
    description: str,
    status: FeatureFlagStatus = FeatureFlagStatus.DISABLED,
    rollout_percentage: int = 0,
    admin_id: str = Depends(require_admin),
    database = Depends(get_database)
):
    """Create a new feature flag"""
    if not feature_flags.db:
        feature_flags.db = database
    
    try:
        flag = await feature_flags.create_flag(
            name=name,
            description=description,
            status=status,
            rollout_percentage=rollout_percentage
        )
        return flag
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/feature-flags/{flag_name}")
async def update_feature_flag(
    flag_name: str,
    status: Optional[FeatureFlagStatus] = None,
    rollout_percentage: Optional[int] = None,
    admin_id: str = Depends(require_admin),
    database = Depends(get_database)
):
    """Update a feature flag"""
    if not feature_flags.db:
        feature_flags.db = database
    
    try:
        flag = await feature_flags.update_flag(
            name=flag_name,
            status=status,
            rollout_percentage=rollout_percentage
        )
        return flag
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/feature-flags/{flag_name}")
async def delete_feature_flag(
    flag_name: str,
    admin_id: str = Depends(require_admin),
    database = Depends(get_database)
):
    """Delete a feature flag"""
    if not feature_flags.db:
        feature_flags.db = database
    
    success = await feature_flags.delete_flag(flag_name)
    
    if success:
        return {"message": f"Feature flag '{flag_name}' deleted"}
    else:
        raise HTTPException(status_code=404, detail="Feature flag not found")


# ============================================================================
# A/B TESTING
# ============================================================================

@router.get("/experiments")
async def list_experiments(
    status: Optional[ExperimentStatus] = None,
    admin_id: str = Depends(require_admin),
    database = Depends(get_database)
):
    """List all A/B test experiments"""
    if not ab_testing.db:
        ab_testing.db = database
    
    experiments = await ab_testing.list_experiments(status=status)
    return {"experiments": experiments, "count": len(experiments)}


@router.post("/experiments")
async def create_experiment(
    name: str,
    description: str,
    variants: List[dict],
    metrics: List[str],
    admin_id: str = Depends(require_admin),
    database = Depends(get_database)
):
    """Create a new A/B test experiment"""
    if not ab_testing.db:
        ab_testing.db = database
    
    try:
        experiment = await ab_testing.create_experiment(
            name=name,
            description=description,
            variants=variants,
            metrics=metrics
        )
        return experiment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/experiments/{experiment_name}/status")
async def update_experiment_status(
    experiment_name: str,
    status: ExperimentStatus,
    admin_id: str = Depends(require_admin),
    database = Depends(get_database)
):
    """Update experiment status"""
    if not ab_testing.db:
        ab_testing.db = database
    
    try:
        experiment = await ab_testing.update_experiment_status(experiment_name, status)
        return experiment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/experiments/{experiment_name}/results")
async def get_experiment_results(
    experiment_name: str,
    admin_id: str = Depends(require_admin),
    database = Depends(get_database)
):
    """Get experiment results and statistics"""
    if not ab_testing.db:
        ab_testing.db = database
    
    results = await ab_testing.get_experiment_results(experiment_name)
    
    if "error" in results:
        raise HTTPException(status_code=404, detail=results["error"])
    
    return results


# ============================================================================
# LOGS & MONITORING
# ============================================================================

@router.get("/logs/search")
async def search_logs(
    log_file: str = "app.log",
    pattern: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100,
    admin_id: str = Depends(require_admin)
):
    """Search application logs"""
    logs = log_aggregation.search_logs(
        log_file=log_file,
        pattern=pattern,
        level=level,
        limit=limit
    )
    
    return {
        "logs": logs,
        "count": len(logs),
        "log_file": log_file
    }


@router.get("/logs/errors")
async def get_recent_errors(
    count: int = Query(50, ge=1, le=500),
    admin_id: str = Depends(require_admin)
):
    """Get recent error logs"""
    errors = log_aggregation.get_recent_errors(count=count)
    
    return {
        "errors": errors,
        "count": len(errors)
    }


@router.get("/logs/stats")
async def get_log_stats(admin_id: str = Depends(require_admin)):
    """Get log file statistics"""
    stats = log_aggregation.get_log_stats()
    return stats


@router.get("/performance/endpoints")
async def get_endpoint_performance(
    endpoint: Optional[str] = None,
    minutes: int = Query(60, ge=1, le=1440),
    admin_id: str = Depends(require_admin)
):
    """Get endpoint performance metrics"""
    stats = performance_monitoring.get_endpoint_stats(
        endpoint=endpoint,
        minutes=minutes
    )
    
    return {
        "stats": stats,
        "time_window_minutes": minutes
    }


@router.get("/performance/queries")
async def get_query_performance(
    collection: Optional[str] = None,
    minutes: int = Query(60, ge=1, le=1440),
    admin_id: str = Depends(require_admin)
):
    """Get database query performance metrics"""
    stats = performance_monitoring.get_query_stats(
        collection=collection,
        minutes=minutes
    )
    
    return {
        "stats": stats,
        "time_window_minutes": minutes
    }


@router.get("/performance/alerts")
async def get_performance_alerts(admin_id: str = Depends(require_admin)):
    """Get active performance alerts"""
    alerts = performance_monitoring.check_alerts()
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "has_critical": any(a["severity"] == "critical" for a in alerts)
    }


# ============================================================================
# SECURITY & VIRUS SCANNING
# ============================================================================

@router.get("/security/quarantine")
async def get_quarantine_stats(admin_id: str = Depends(require_admin)):
    """Get quarantined files statistics"""
    stats = virus_scanner.get_quarantine_stats()
    return stats


@router.get("/system/health")
async def system_health(admin_id: str = Depends(require_admin)):
    """Get overall system health status"""
    endpoint_stats = performance_monitoring.get_endpoint_stats(minutes=60)
    alerts = performance_monitoring.check_alerts()
    log_stats = log_aggregation.get_log_stats()
    
    # Calculate health score
    health_score = 100
    
    # Deduct for alerts
    critical_alerts = sum(1 for a in alerts if a["severity"] == "critical")
    warning_alerts = sum(1 for a in alerts if a["severity"] == "warning")
    health_score -= (critical_alerts * 20 + warning_alerts * 5)
    
    # Deduct for high error rates
    for stats in endpoint_stats.values():
        if stats["error_rate"] > 0.05:  # > 5%
            health_score -= 10
    
    health_score = max(0, health_score)
    
    return {
        "health_score": health_score,
        "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy",
        "alerts": {
            "critical": critical_alerts,
            "warning": warning_alerts
        },
        "log_stats": log_stats,
        "timestamp": datetime.utcnow().isoformat()
    }
