"""
Health Check Routes
Provides endpoints for system health monitoring
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import os
import psutil
from database import get_database

router = APIRouter(tags=["Health"])

# Store startup time
STARTUP_TIME = datetime.utcnow()


@router.get("/")
@router.get("/api/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "ok",
        "message": "NotesHub API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/test")
@router.get("/api/test")
async def test_cors():
    """Test CORS configuration"""
    return {
        "message": "CORS is working!",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/api/db-status")
async def database_status(database=Depends(get_database)):
    """Check database connection status"""
    try:
        # Try to ping the database
        await database.command("ping")
        return {
            "status": "connected",
            "message": "Database connection is healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "message": f"Database connection failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/api/health/detailed")
async def detailed_health_check(database=Depends(get_database)):
    """Comprehensive health check with system metrics"""
    
    # Database check
    db_status = "healthy"
    db_message = "Connected"
    try:
        await database.command("ping")
    except Exception as e:
        db_status = "unhealthy"
        db_message = str(e)
    
    # System metrics
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # Uptime calculation
    uptime_seconds = (datetime.utcnow() - STARTUP_TIME).total_seconds()
    uptime_str = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
    
    # Check upload directories
    upload_dirs_ok = (
        os.path.exists("uploads/notes") and 
        os.path.exists("uploads/profile")
    )
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": {
            "seconds": int(uptime_seconds),
            "formatted": uptime_str,
            "started_at": STARTUP_TIME.isoformat()
        },
        "database": {
            "status": db_status,
            "message": db_message,
            "type": "MongoDB"
        },
        "system": {
            "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "threads": process.num_threads()
        },
        "storage": {
            "upload_directories": "ok" if upload_dirs_ok else "missing"
        },
        "environment": os.getenv("NODE_ENV", "development")
    }
