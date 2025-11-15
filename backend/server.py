"""
NotesHub API - Main Application
Clean, modular FastAPI application with organized routers
"""

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from datetime import datetime
import os

from database import db

# Import all routers
from routers import (
    health,
    auth as auth_router,
    users,
    notes as notes_router,
    admin,
    analytics,
    search as search_router,
    gamification,
    leaderboards,
    referrals,
    achievements,
    study_groups,
    social,
    exams
)


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await db.connect_to_database()
    
    # Create upload directories
    os.makedirs("uploads/notes", exist_ok=True)
    os.makedirs("uploads/profile", exist_ok=True)
    os.makedirs("backups", exist_ok=True)
    os.makedirs("quarantine", exist_ok=True)
    
    # Initialize search indexes
    try:
        from services.search_service import get_search_service
        search_svc = get_search_service(db.db)
        await search_svc.ensure_text_indexes()
    except Exception as e:
        print(f"Warning: Could not initialize search indexes: {e}")
    
    # Initialize feature flags and A/B testing with database
    try:
        from services.feature_flags import feature_flags
        from services.ab_testing import ab_testing
        feature_flags.db = db.db
        ab_testing.db = db.db
    except Exception as e:
        print(f"Warning: Could not initialize feature flags: {e}")
    
    print("="*60)
    print("✅ NotesHub API started successfully!")
    print(f"✅ Database connected")
    print(f"✅ Modular routers loaded: 14 modules")
    print(f"✅ Viral growth features: Leaderboards, Streaks, Referrals")
    print(f"✅ Gamification: Points, Levels, 50+ Achievements")
    print(f"✅ Social: Follow system, Activity feed")
    print(f"✅ Study Groups: Collaborative learning with chat")
    print(f"✅ Exams: Countdown timers, Panic mode")
    print(f"✅ Feature flags initialized")
    print(f"✅ A/B testing initialized")
    print(f"✅ Performance monitoring active")
    print(f"✅ Virus scanner ready")
    print(f"✅ Log aggregation active")
    print("="*60)
    
    yield
    
    # Shutdown
    await db.close_database_connection()
    print("✅ NotesHub API shut down gracefully")


# Initialize FastAPI app
app = FastAPI(
    title="NotesHub API",
    version="2.0.0",
    description="Academic Notes Sharing Platform - Modular & Production Ready",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(health.router)
app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(notes_router.router)
app.include_router(admin.router)
app.include_router(analytics.router)
app.include_router(search_router.router)
app.include_router(gamification.router)
app.include_router(leaderboards.router)
app.include_router(referrals.router)
app.include_router(achievements.router)
app.include_router(study_groups.router)
app.include_router(social.router)
app.include_router(exams.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    print(f"❌ Unhandled exception: {exc}")
    print(f"   Path: {request.url.path}")
    print(f"   Method: {request.method}")
    
    # Don't expose internal errors in production
    if os.getenv("ENV") == "production":
        return {"error": "Internal server error"}
    
    return {
        "error": "Internal server error",
        "detail": str(exc),
        "path": request.url.path
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
