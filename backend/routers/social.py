"""
Social Router - Follow System & Activity Feed
Build connections, follow top contributors, see activity feed
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from auth import get_current_user_id
from models import (
    FollowAction, FollowResponse, FollowStats,
    ActivityFeedItem, ActivityFeedResponse
)
from database import get_database
from routers.gamification import update_user_points


router = APIRouter(prefix="/api/social", tags=["social"])


@router.post("/follow/{following_id}")
async def follow_user(
    following_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Follow a user"""
    
    # Can't follow yourself
    if user_id == following_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if user exists
    following_user = await db.users.find_one({"id": following_id})
    if not following_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    existing = await db.follows.find_one({
        "follower_id": user_id,
        "following_id": following_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already following")
    
    # Create follow relationship
    await db.follows.insert_one({
        "follower_id": user_id,
        "following_id": following_id,
        "followed_at": datetime.utcnow()
    })
    
    # Award points
    await update_user_points(db, user_id, "follow_user", 5)
    
    # Create notification for followed user
    await db.notifications.insert_one({
        "user_id": following_id,
        "type": "new_follower",
        "data": {"follower_id": user_id},
        "created_at": datetime.utcnow(),
        "read": False
    })
    
    return {
        "success": True,
        "message": f"Now following {following_user.get('usn')}!"
    }


@router.delete("/unfollow/{following_id}")
async def unfollow_user(
    following_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Unfollow a user"""
    
    # Check if following
    result = await db.follows.delete_one({
        "follower_id": user_id,
        "following_id": following_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=400, detail="Not following this user")
    
    return {
        "success": True,
        "message": "Unfollowed successfully"
    }


@router.get("/followers")
async def get_followers(
    limit: int = Query(50, le=200),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get list of users who follow current user"""
    
    # Get follower relationships
    follows = await db.follows.find(
        {"following_id": user_id}
    ).sort("followed_at", -1).limit(limit).to_list(None)
    
    # Get user details for each follower
    result = []
    for follow in follows:
        follower = await db.users.find_one({"id": follow["follower_id"]})
        if follower:
            # Get follower's level
            user_points = await db.user_points.find_one({"user_id": follow["follower_id"]})
            level = user_points.get("level", 1) if user_points else 1
            
            result.append({
                "user_id": follower["id"],
                "usn": follower.get("usn"),
                "department": follower.get("department"),
                "college": follower.get("college"),
                "profile_picture": follower.get("profile_picture"),
                "level": level,
                "followed_at": follow["followed_at"]
            })
    
    return {"followers": result, "count": len(result)}


@router.get("/following")
async def get_following(
    limit: int = Query(50, le=200),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get list of users current user is following"""
    
    # Get following relationships
    follows = await db.follows.find(
        {"follower_id": user_id}
    ).sort("followed_at", -1).limit(limit).to_list(None)
    
    # Get user details for each followed user
    result = []
    for follow in follows:
        followed_user = await db.users.find_one({"id": follow["following_id"]})
        if followed_user:
            # Get user's level
            user_points = await db.user_points.find_one({"user_id": follow["following_id"]})
            level = user_points.get("level", 1) if user_points else 1
            
            result.append({
                "user_id": followed_user["id"],
                "usn": followed_user.get("usn"),
                "department": followed_user.get("department"),
                "college": followed_user.get("college"),
                "profile_picture": followed_user.get("profile_picture"),
                "level": level,
                "followed_at": follow["followed_at"]
            })
    
    return {"following": result, "count": len(result)}


@router.get("/stats/{user_id}", response_model=FollowStats)
async def get_follow_stats(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get follow statistics for a user"""
    
    # Count followers
    followers_count = await db.follows.count_documents({"following_id": user_id})
    
    # Count following
    following_count = await db.follows.count_documents({"follower_id": user_id})
    
    # Check if current user is following this user
    is_following = False
    if current_user_id != user_id:
        follow = await db.follows.find_one({
            "follower_id": current_user_id,
            "following_id": user_id
        })
        is_following = follow is not None
    
    return FollowStats(
        followers_count=followers_count,
        following_count=following_count,
        is_following=is_following
    )


@router.get("/feed", response_model=ActivityFeedResponse)
async def get_activity_feed(
    limit: int = Query(50, le=100),
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get activity feed from followed users"""
    
    # Get list of users current user is following
    follows = await db.follows.find({"follower_id": user_id}).to_list(None)
    following_ids = [f["following_id"] for f in follows]
    
    if not following_ids:
        return ActivityFeedResponse(activities=[], has_more=False)
    
    # Collect activities from followed users
    activities = []
    
    # 1. Recent note uploads from followed users
    recent_notes = await db.notes.find({
        "userId": {"$in": following_ids},
        "is_approved": True,
        "uploaded_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
    }).sort("uploaded_at", -1).limit(limit).to_list(None)
    
    for note in recent_notes:
        user = await db.users.find_one({"id": note["userId"]})
        if user:
            activities.append(ActivityFeedItem(
                user_id=note["userId"],
                usn=user.get("usn"),
                activity_type="upload",
                details={
                    "note_id": note["id"],
                    "title": note["title"],
                    "subject": note["subject"]
                },
                timestamp=note["uploaded_at"],
                profile_picture=user.get("profile_picture")
            ))
    
    # 2. Recent achievements from followed users
    recent_achievements = await db.user_achievements.find({
        "user_id": {"$in": following_ids},
        "unlocked_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
    }).sort("unlocked_at", -1).limit(20).to_list(None)
    
    for ach in recent_achievements:
        user = await db.users.find_one({"id": ach["user_id"]})
        if user:
            activities.append(ActivityFeedItem(
                user_id=ach["user_id"],
                usn=user.get("usn"),
                activity_type="achievement",
                details={
                    "achievement_id": ach["achievement_id"]
                },
                timestamp=ach["unlocked_at"],
                profile_picture=user.get("profile_picture")
            ))
    
    # 3. Level ups from followed users
    level_ups = await db.user_points.find({
        "user_id": {"$in": following_ids},
        "updated_at": {"$gte": datetime.utcnow() - timedelta(days=7)},
        "level": {"$gte": 5}  # Only show level 5+
    }).sort("updated_at", -1).limit(20).to_list(None)
    
    for level_up in level_ups:
        user = await db.users.find_one({"id": level_up["user_id"]})
        if user:
            activities.append(ActivityFeedItem(
                user_id=level_up["user_id"],
                usn=user.get("usn"),
                activity_type="level_up",
                details={
                    "level": level_up["level"],
                    "level_name": level_up.get("level_name", "")
                },
                timestamp=level_up["updated_at"],
                profile_picture=user.get("profile_picture")
            ))
    
    # 4. Milestone streaks from followed users
    streaks = await db.streaks.find({
        "user_id": {"$in": following_ids},
        "current_streak": {"$in": [7, 30, 100, 365]},  # Milestones
        "last_activity_date": {"$gte": datetime.utcnow() - timedelta(days=1)}
    }).limit(10).to_list(None)
    
    for streak in streaks:
        user = await db.users.find_one({"id": streak["user_id"]})
        if user:
            activities.append(ActivityFeedItem(
                user_id=streak["user_id"],
                usn=user.get("usn"),
                activity_type="streak",
                details={
                    "streak": streak["current_streak"]
                },
                timestamp=streak["last_activity_date"],
                profile_picture=user.get("profile_picture")
            ))
    
    # Sort all activities by timestamp
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Paginate
    paginated = activities[offset:offset + limit]
    has_more = len(activities) > offset + limit
    
    return ActivityFeedResponse(
        activities=paginated,
        has_more=has_more
    )


@router.get("/suggested-users")
async def get_suggested_users(
    limit: int = Query(10, le=50),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get suggested users to follow based on activity and department"""
    
    # Get current user
    current_user = await db.users.find_one({"id": user_id})
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get users already following
    follows = await db.follows.find({"follower_id": user_id}).to_list(None)
    following_ids = {f["following_id"] for f in follows}
    following_ids.add(user_id)  # Exclude self
    
    # Find top contributors from same department
    same_dept_users = await db.users.find({
        "department": current_user.get("department"),
        "id": {"$nin": list(following_ids)}
    }).limit(limit * 2).to_list(None)
    
    # Score users by activity
    suggestions = []
    
    for user in same_dept_users:
        user_id_check = user.get("id")
        if not user_id_check:
            continue
        
        # Get upload count
        upload_count = await db.notes.count_documents({"userId": user_id_check, "is_approved": True})
        
        # Get points
        user_points = await db.user_points.find_one({"user_id": user_id_check})
        points = user_points.get("total_points", 0) if user_points else 0
        level = user_points.get("level", 1) if user_points else 1
        
        # Get followers count
        followers = await db.follows.count_documents({"following_id": user_id_check})
        
        # Calculate score
        score = upload_count * 10 + points + followers * 5
        
        if score > 0:  # Only suggest active users
            suggestions.append({
                "user_id": user_id_check,
                "usn": user.get("usn"),
                "department": user.get("department"),
                "college": user.get("college"),
                "profile_picture": user.get("profile_picture"),
                "level": level,
                "upload_count": upload_count,
                "followers": followers,
                "score": score
            })
    
    # Sort by score and limit
    suggestions.sort(key=lambda x: x["score"], reverse=True)
    suggestions = suggestions[:limit]
    
    return {"suggested_users": suggestions}


@router.get("/trending-users")
async def get_trending_users(
    limit: int = Query(10, le=50),
    db = Depends(get_database)
):
    """Get trending users based on recent activity"""
    
    # Get users with recent high activity
    recent_date = datetime.utcnow() - timedelta(days=7)
    
    # Find users with most uploads in last week
    pipeline = [
        {"$match": {
            "uploaded_at": {"$gte": recent_date},
            "is_approved": True
        }},
        {"$group": {
            "_id": "$userId",
            "upload_count": {"$sum": 1},
            "total_downloads": {"$sum": "$downloadCount"}
        }},
        {"$sort": {"upload_count": -1}},
        {"$limit": limit}
    ]
    
    trending = await db.notes.aggregate(pipeline).to_list(None)
    
    # Enrich with user data
    result = []
    for item in trending:
        user_id = item["_id"]
        if not user_id:
            continue
            
        user = await db.users.find_one({"id": user_id})
        if user:
            # Get user stats
            user_points = await db.user_points.find_one({"user_id": user_id})
            level = user_points.get("level", 1) if user_points else 1
            
            followers = await db.follows.count_documents({"following_id": user_id})
            
            result.append({
                "user_id": user_id,
                "usn": user.get("usn"),
                "department": user.get("department"),
                "college": user.get("college"),
                "profile_picture": user.get("profile_picture"),
                "level": level,
                "recent_uploads": item["upload_count"],
                "total_downloads": item["total_downloads"],
                "followers": followers
            })
    
    return {"trending_users": result}


@router.get("/user-profile/{user_id}")
async def get_user_public_profile(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get public profile of a user with stats"""
    
    # Get user
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get stats
    upload_count = await db.notes.count_documents({"userId": user_id, "is_approved": True})
    
    user_notes = await db.notes.find({"userId": user_id}).to_list(None)
    total_downloads = sum(note.get("downloadCount", 0) for note in user_notes)
    
    # Get points and level
    user_points = await db.user_points.find_one({"user_id": user_id})
    points = user_points.get("total_points", 0) if user_points else 0
    level = user_points.get("level", 1) if user_points else 1
    level_name = user_points.get("level_name", "Newbie") if user_points else "Newbie"
    
    # Get streak
    streak_data = await db.streaks.find_one({"user_id": user_id})
    current_streak = streak_data.get("current_streak", 0) if streak_data else 0
    
    # Get follow stats
    followers = await db.follows.count_documents({"following_id": user_id})
    following = await db.follows.count_documents({"follower_id": user_id})
    
    # Check if current user follows this user
    is_following = await db.follows.find_one({
        "follower_id": current_user_id,
        "following_id": user_id
    }) is not None
    
    # Get achievements count
    achievements_count = await db.user_achievements.count_documents({"user_id": user_id})
    
    # Get recent uploads
    recent_uploads = await db.notes.find(
        {"userId": user_id, "is_approved": True}
    ).sort("uploaded_at", -1).limit(5).to_list(None)
    
    return {
        "user_id": user_id,
        "usn": user.get("usn"),
        "department": user.get("department"),
        "college": user.get("college"),
        "year": user.get("year"),
        "profile_picture": user.get("profile_picture"),
        "stats": {
            "upload_count": upload_count,
            "total_downloads": total_downloads,
            "points": points,
            "level": level,
            "level_name": level_name,
            "current_streak": current_streak,
            "followers": followers,
            "following": following,
            "achievements": achievements_count
        },
        "is_following": is_following,
        "recent_uploads": recent_uploads
    }
