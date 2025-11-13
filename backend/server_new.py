"""
NotesHub API - Main Application
Modular FastAPI application with organized routers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import os

from database import db

# Import routers
from routers import health, auth, notes, users


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    print("🚀 Starting NotesHub API...")
    await db.connect_to_database()
    
    # Create upload directories
    os.makedirs("uploads/notes", exist_ok=True)
    os.makedirs("uploads/profile", exist_ok=True)
    
    print("✅ NotesHub API started successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down NotesHub API...")
    await db.close_database_connection()
    print("✅ Database connections closed")


# Initialize FastAPI app
app = FastAPI(
    title="NotesHub API",
    version="1.0.0",
    description="A collaborative note-sharing platform for students",
    lifespan=lifespan
)

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
# TODO: In production, specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(users.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions"""
    print(f"❌ Unhandled exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
