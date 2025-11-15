"""
Gamification Router - Streaks, Points, Levels
Handles viral growth mechanics for user engagement
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime, timedelta
import math
import random
import string

from auth import get_current_user_id
from models import (
    UserInDB, StreakResponse, PointsResponse, 
    PointsHistoryItem, ShareAction, ShareStats
)
from database import get_database


router = APIRouter(prefix="/api/gamification", tags=["gamification"])


# Level configuration
LEVEL_CONFIG = {
    1: {"name": "Newbie", "points": 0},
    5: {"name": "Helper", "points": 2500},
    10: {"name": "Expert", "points": 10000},
    20: {"name": "Master", "points": 50000},
    30: {"name": "Champion", "points": 100000},
    40: {"name": "Elite", "points": 200000},
    50: {"name": "Legend", "points": 500000}
}

# Points for actions
POINTS_CONFIG = {
    "upload_note": 100,
    "note_downloaded": 5,
    "note_rated_5_star": 20,
    "daily_streak": 5,
    "referral_signup": 50,
    "referral_upload": 25,
    "share_note": 10,
    "help_user": 10,
    "verify_note": 15
}

# Streak milestones
STREAK_MILESTONES = [7, 30, 100, 365]


def calculate_level_from_points(points: int) -> tuple[int, str, int, float]:
    """Calculate level, level name, points to next level, and progress percentage"""
    level = 1
    level_name = "Newbie"
    
    # Find current level
    sorted_levels = sorted(LEVEL_CONFIG.keys())
    for lvl in sorted_levels:
        if points >= LEVEL_CONFIG[lvl]["points"]:
            level = lvl
            level_name = LEVEL_CONFIG[lvl]["name"]
    
    # Calculate points to next level
    next_level_idx = sorted_levels.index(level) + 1 if level in sorted_levels else 0
    if next_level_idx < len(sorted_levels):
        next_level = sorted_levels[next_level_idx]
        points_to_next = LEVEL_CONFIG[next_level]["points"] - points
        
        # Calculate progress percentage
        current_level_points = LEVEL_CONFIG[level]["points"]
        next_level_points = LEVEL_CONFIG[next_level]["points"]
        progress = ((points - current_level_points) / (next_level_points - current_level_points)) * 100
    else:
        points_to_next = 0
        progress = 100.0
    
    return level, level_name, points_to_next, round(progress, 2)


async def update_user_points(db, user_id: str, action: str, points: int = None):
    """Add points for a user action"""
    if points is None:
        points = POINTS_CONFIG.get(action, 0)
    
    if points == 0:
        return
    
    # Get or create user points record
    user_points = await db.user_points.find_one({"user_id": user_id})
    
    if not user_points:
        user_points = {
            "user_id": user_id,
            "total_points": 0,
            "created_at": datetime.utcnow()
        }
    
    # Update points
    new_total = user_points.get("total_points", 0) + points
    level, level_name, points_to_next, progress = calculate_level_from_points(new_total)
    
    await db.user_points.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "total_points": new_total,
                "level": level,
                "level_name": level_name,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "points_history": {
                    "action": action,
                    "points": points,
                    "timestamp": datetime.utcnow()
                }
            }
        },
        upsert=True
    )
    
    return new_total, level


async def check_and_update_streak(db, user_id: str, activity_type: str = "general"):
    """Check and update user's daily streak"""
    now = datetime.utcnow()
    today = now.date()
    
    # Get streak record
    streak_data = await db.streaks.find_one({"user_id": user_id})
    
    if not streak_data:
        # Create new streak
        await db.streaks.insert_one({
            "user_id": user_id,
            "current_streak": 1,
            "longest_streak": 1,
            "last_activity_date": now,
            "total_activities": 1,
            "created_at": now
        })
        
        # Award points for first activity
        await update_user_points(db, user_id, "daily_streak")
        return 1
    
    last_activity = streak_data.get("last_activity_date")
    if last_activity:
        last_date = last_activity.date() if isinstance(last_activity, datetime) else last_activity
        days_diff = (today - last_date).days
        
        current_streak = streak_data.get("current_streak", 0)
        longest_streak = streak_data.get("longest_streak", 0)
        
        if days_diff == 0:
            # Same day, just increment activity count
            await db.streaks.update_one(
                {"user_id": user_id},
                {
                    "$inc": {"total_activities": 1},
                    "$set": {"last_activity_date": now}
                }
            )
            return current_streak
        
        elif days_diff == 1:
            # Consecutive day, increment streak
            new_streak = current_streak + 1
            new_longest = max(longest_streak, new_streak)
            
            await db.streaks.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "current_streak": new_streak,
                        "longest_streak": new_longest,
                        "last_activity_date": now
                    },
                    "$inc": {"total_activities": 1}
                }
            )
            
            # Award streak points
            await update_user_points(db, user_id, "daily_streak")
            
            return new_streak
        
        else:
            # Streak broken, reset to 1
            await db.streaks.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "current_streak": 1,
                        "last_activity_date": now
                    },
                    "$inc": {"total_activities": 1}
                }
            )
            return 1
    
    return streak_data.get("current_streak", 0)


@router.get("/streak", response_model=StreakResponse)
async def get_user_streak(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's current streak information"""
    
    streak_data = await db.streaks.find_one({"user_id": user_id})
    
    if not streak_data:
        return StreakResponse(
            current_streak=0,
            longest_streak=0,
            last_activity_date=None,
            days_until_next_milestone=7,
            next_milestone=7
        )
    
    current_streak = streak_data.get("current_streak", 0)
    
    # Find next milestone
    next_milestone = 7
    for milestone in STREAK_MILESTONES:
        if current_streak < milestone:
            next_milestone = milestone
            break
    
    days_until_next = next_milestone - current_streak
    
    return StreakResponse(
        current_streak=current_streak,
        longest_streak=streak_data.get("longest_streak", 0),
        last_activity_date=streak_data.get("last_activity_date"),
        days_until_next_milestone=days_until_next,
        next_milestone=next_milestone
    )


@router.post("/streak/activity")
async def record_activity(
    activity_type: str = "general",
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Record a user activity to maintain streak"""
    
    new_streak = await check_and_update_streak(db, user_id, activity_type)
    
    return {
        "success": True,
        "current_streak": new_streak,
        "message": f"Streak updated! You're on a {new_streak} day streak! 🔥"
    }


@router.get("/points", response_model=PointsResponse)
async def get_user_points(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's points and level information"""
    
    user_points = await db.user_points.find_one({"user_id": user_id})
    
    if not user_points:
        return PointsResponse(
            total_points=0,
            level=1,
            level_name="Newbie",
            points_to_next_level=2500,
            progress_percentage=0.0
        )
    
    total_points = user_points.get("total_points", 0)
    level, level_name, points_to_next, progress = calculate_level_from_points(total_points)
    
    return PointsResponse(
        total_points=total_points,
        level=level,
        level_name=level_name,
        points_to_next_level=points_to_next,
        progress_percentage=progress
    )


@router.get("/points/history")
async def get_points_history(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's recent points history"""
    
    user_points = await db.user_points.find_one({"user_id": user_id})
    
    if not user_points or "points_history" not in user_points:
        return {"history": []}
    
    history = user_points.get("points_history", [])
    
    # Return last N items
    return {"history": history[-limit:]}


@router.post("/share")
async def record_share_action(
    share_data: ShareAction,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Record a note share action"""
    
    # Record share action
    await db.share_actions.insert_one({
        "user_id": user_id,
        "note_id": share_data.note_id,
        "platform": share_data.platform,
        "shared_at": datetime.utcnow()
    })
    
    # Award points for sharing
    await update_user_points(db, user_id, "share_note")
    
    # Update streak
    await check_and_update_streak(db, user_id, "share")
    
    return {
        "success": True,
        "message": f"Thanks for sharing on {share_data.platform}! +10 points 🎉"
    }


@router.get("/share/stats", response_model=ShareStats)
async def get_share_stats(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's sharing statistics"""
    
    # Count total shares
    total_shares = await db.share_actions.count_documents({"user_id": user_id})
    
    # Platform breakdown
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$platform",
            "count": {"$sum": 1}
        }}
    ]
    
    platform_data = await db.share_actions.aggregate(pipeline).to_list(None)
    platform_breakdown = {item["_id"]: item["count"] for item in platform_data}
    
    # Most shared note
    most_shared_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$note_id",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    
    most_shared = await db.share_actions.aggregate(most_shared_pipeline).to_list(1)
    most_shared_note = most_shared[0]["_id"] if most_shared else None
    
    return ShareStats(
        total_shares=total_shares,
        platform_breakdown=platform_breakdown,
        most_shared_note=most_shared_note
    )


# Helper function to be called from other routers
async def award_points_for_action(db, user_id: str, action: str):
    """Award points and update streak for user actions"""
    await update_user_points(db, user_id, action)
    await check_and_update_streak(db, user_id, action)
