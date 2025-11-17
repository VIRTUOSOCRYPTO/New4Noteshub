"""
Feedback Routes
Beta feedback collection system
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import uuid

from database import get_database
from auth import get_current_user_id
from models import (
    FeedbackCreate, 
    FeedbackResponse, 
    FeedbackStatusUpdate,
    FeedbackStatus
)

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackCreate,
    current_user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Submit beta feedback"""
    
    # Get user info
    user = await database.users.find_one({"id": current_user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create feedback document
    feedback_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user_id,
        "usn": user["usn"],
        "type": feedback.type.value,
        "title": feedback.title,
        "description": feedback.description,
        "rating": feedback.rating,
        "status": FeedbackStatus.NEW.value,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "admin_response": None
    }
    
    # Insert into database
    await database.feedback.insert_one(feedback_doc)
    
    # Award points for feedback
    try:
        from services.gamification_service import GamificationService
        gamification = GamificationService(database)
        await gamification.award_points(
            user_id=current_user_id,
            action="feedback_submitted",
            points=10
        )
    except Exception as e:
        print(f"Warning: Could not award feedback points: {e}")
    
    return FeedbackResponse(**feedback_doc)


@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
    current_user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get current user's feedback submissions"""
    
    cursor = database.feedback.find({"user_id": current_user_id}).sort("created_at", -1)
    feedback_list = await cursor.to_list(length=100)
    
    return [FeedbackResponse(**fb) for fb in feedback_list]


@router.get("/all", response_model=List[FeedbackResponse])
async def get_all_feedback(
    status_filter: str = None,
    current_user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get all feedback (admin only)"""
    
    # Get user info
    user = await database.users.find_one({"id": current_user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    admin_emails = ["tortoor8@gmail.com"]  # Should match ADMIN_EMAILS from .env
    if user["email"] not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Build query
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    cursor = database.feedback.find(query).sort("created_at", -1)
    feedback_list = await cursor.to_list(length=500)
    
    return [FeedbackResponse(**fb) for fb in feedback_list]


@router.patch("/{feedback_id}/status", response_model=FeedbackResponse)
async def update_feedback_status(
    feedback_id: str,
    update: FeedbackStatusUpdate,
    current_user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Update feedback status (admin only)"""
    
    # Get user info
    user = await database.users.find_one({"id": current_user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    admin_emails = ["tortoor8@gmail.com"]
    if user["email"] not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Find feedback
    feedback = await database.feedback.find_one({"id": feedback_id})
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Update feedback
    update_data = {
        "status": update.status.value,
        "updated_at": datetime.utcnow()
    }
    if update.admin_response:
        update_data["admin_response"] = update.admin_response
    
    await database.feedback.update_one(
        {"id": feedback_id},
        {"$set": update_data}
    )
    
    # Get updated feedback
    updated_feedback = await database.feedback.find_one({"id": feedback_id})
    return FeedbackResponse(**updated_feedback)


@router.get("/stats")
async def get_feedback_stats(
    current_user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get feedback statistics (admin only)"""
    
    # Get user info
    user = await database.users.find_one({"id": current_user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is admin
    admin_emails = ["tortoor8@gmail.com"]
    if user["email"] not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Count by status
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    
    status_counts = {}
    async for doc in database.feedback.aggregate(pipeline):
        status_counts[doc["_id"]] = doc["count"]
    
    # Count by type
    type_pipeline = [
        {
            "$group": {
                "_id": "$type",
                "count": {"$sum": 1}
            }
        }
    ]
    
    type_counts = {}
    async for doc in database.feedback.aggregate(type_pipeline):
        type_counts[doc["_id"]] = doc["count"]
    
    # Get total
    total_feedback = await database.feedback.count_documents({})
    
    # Get average rating
    rating_pipeline = [
        {
            "$match": {"rating": {"$ne": None}}
        },
        {
            "$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"}
            }
        }
    ]
    
    avg_rating = None
    async for doc in database.feedback.aggregate(rating_pipeline):
        avg_rating = round(doc["avg_rating"], 2)
    
    return {
        "total_feedback": total_feedback,
        "by_status": status_counts,
        "by_type": type_counts,
        "average_rating": avg_rating
    }
