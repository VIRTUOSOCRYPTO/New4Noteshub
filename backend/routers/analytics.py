"""
Analytics Router for NotesHub

Provides endpoints for:
- Dashboard statistics
- Popular notes tracking
- Department and subject statistics
- Upload trends and predictions
- User engagement metrics
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from datetime import datetime

from database import get_database
from auth import get_current_user_id, verify_token
from middleware.admin_auth import get_admin_status
from services.analytics_service import get_analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Optional auth - returns None if not authenticated
security = HTTPBearer(auto_error=False)

async def get_optional_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Get current user ID from JWT token, returns None if not authenticated"""
    if not credentials:
        return None
    
    token_data = verify_token(credentials.credentials)
    if token_data is None or token_data.user_id is None:
        return None
    
    return token_data.user_id


@router.get("/dashboard")
async def get_dashboard(
    department: Optional[str] = None,
    user_id: Optional[str] = Depends(get_optional_user_id),
    database = Depends(get_database)
):
    """Get comprehensive dashboard statistics - Public endpoint"""
    analytics = get_analytics_service(database)
    stats = await analytics.get_dashboard_stats(user_id=None, department=department)
    return stats


@router.get("/user/{user_id}")
async def get_user_analytics(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get analytics for a specific user"""
    # Users can only view their own analytics unless admin
    if user_id != current_user_id:
        # Check if current user is admin
        is_admin = await get_admin_status(current_user_id, database)
        if not is_admin:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own analytics"
            )
    
    analytics = get_analytics_service(database)
    user_stats = await analytics.get_user_analytics(user_id)
    
    if not user_stats:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_stats


@router.get("/popular-notes")
async def get_popular_notes(
    limit: int = 10,
    department: Optional[str] = None,
    user_id: Optional[str] = Depends(get_optional_user_id),
    database = Depends(get_database)
):
    """Get most popular notes - Public endpoint"""
    analytics = get_analytics_service(database)
    popular = await analytics.get_popular_notes(limit=limit, department=department)
    return {"notes": popular}


@router.get("/departments")
async def get_department_statistics(
    user_id: Optional[str] = Depends(get_optional_user_id),
    database = Depends(get_database)
):
    """Get statistics by department - Public endpoint"""
    analytics = get_analytics_service(database)
    stats = await analytics.get_department_statistics()
    return {"departments": stats}


@router.get("/subjects")
async def get_subject_statistics(
    department: Optional[str] = None,
    user_id: Optional[str] = Depends(get_optional_user_id),
    database = Depends(get_database)
):
    """Get statistics by subject - Public endpoint"""
    analytics = get_analytics_service(database)
    stats = await analytics.get_subject_statistics(department=department)
    return {"subjects": stats}


@router.get("/trends/uploads")
async def get_upload_trends(
    days: int = 30,
    user_id: Optional[str] = Depends(get_optional_user_id),
    database = Depends(get_database)
):
    """Get upload trends over time - Public endpoint"""
    if days > 365:
        raise HTTPException(status_code=400, detail="Days cannot exceed 365")
    
    analytics = get_analytics_service(database)
    trends = await analytics.get_upload_trends(days=days)
    return {"trends": trends, "days": days}


@router.get("/trends/predictions")
async def get_trend_predictions(
    days_ahead: int = 7,
    user_id: Optional[str] = Depends(get_optional_user_id),
    database = Depends(get_database)
):
    """Get predicted upload trends - Public endpoint"""
    if days_ahead > 30:
        raise HTTPException(status_code=400, detail="Prediction days cannot exceed 30")
    
    analytics = get_analytics_service(database)
    predictions = await analytics.predict_trends(days_ahead=days_ahead)
    return {"predictions": predictions, "days_ahead": days_ahead}


@router.get("/engagement")
async def get_engagement_metrics(
    days: int = 7,
    user_id: Optional[str] = Depends(get_optional_user_id),
    database = Depends(get_database)
):
    """Get user engagement metrics - Public endpoint"""
    if days > 90:
        raise HTTPException(status_code=400, detail="Days cannot exceed 90")
    
    analytics = get_analytics_service(database)
    metrics = await analytics.get_engagement_metrics(days=days)
    return metrics
