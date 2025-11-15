"""
Leaderboards Router - College, Department, All-India Rankings
Creates viral competition and social proof
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta

from auth import get_current_user_id
from models import UserInDB, LeaderboardEntry, LeaderboardResponse, LeaderboardQuery
from database import get_database


router = APIRouter(prefix="/api/leaderboards", tags=["leaderboards"])


async def calculate_user_score(db, user_id: str) -> int:
    """Calculate user's leaderboard score based on contributions"""
    
    # Get user points
    user_points = await db.user_points.find_one({"user_id": user_id})
    points = user_points.get("total_points", 0) if user_points else 0
    
    # Get upload count (notes use 'userId' field, not 'user_id')
    upload_count = await db.notes.count_documents({"userId": user_id, "is_approved": True})
    
    # Get total downloads of user's notes (use 'downloadCount' not 'download_count')
    user_notes = await db.notes.find({"userId": user_id}).to_list(None)
    total_downloads = sum(note.get("downloadCount", 0) for note in user_notes)
    
    # Get streak
    streak_data = await db.streaks.find_one({"user_id": user_id})
    current_streak = streak_data.get("current_streak", 0) if streak_data else 0
    
    # Calculate weighted score
    score = (
        points +  # Points from gamification
        (upload_count * 100) +  # 100 points per upload
        (total_downloads * 5) +  # 5 points per download
        (current_streak * 10)  # 10 points per streak day
    )
    
    return score


async def get_leaderboard_data(
    db,
    leaderboard_type: str,
    college: Optional[str] = None,
    department: Optional[str] = None,
    limit: int = 100
) -> List[LeaderboardEntry]:
    """Generate leaderboard rankings"""
    
    # Build user filter
    user_filter = {}
    if leaderboard_type == "college" and college:
        user_filter["college"] = college
    elif leaderboard_type == "department" and department:
        user_filter["department"] = department
    # all_india has no filter
    
    # Get all users matching filter
    users = await db.users.find(user_filter).to_list(None)
    
    # Calculate scores for all users
    leaderboard_entries = []
    
    for user in users:
        # Use the 'id' field, not MongoDB's '_id'
        user_id = user.get("id")
        if not user_id:
            # Skip users without proper ID
            continue
            
        score = await calculate_user_score(db, user_id)
        
        # Get streak
        streak_data = await db.streaks.find_one({"user_id": user_id})
        current_streak = streak_data.get("current_streak", 0) if streak_data else 0
        
        # Get level
        user_points = await db.user_points.find_one({"user_id": user_id})
        level = user_points.get("level", 1) if user_points else 1
        
        leaderboard_entries.append({
            "user_id": user_id,
            "usn": user.get("usn"),
            "score": score,
            "college": user.get("college"),
            "department": user.get("department"),
            "profile_picture": user.get("profile_picture"),
            "streak": current_streak,
            "level": level
        })
    
    # Sort by score descending
    leaderboard_entries.sort(key=lambda x: x["score"], reverse=True)
    
    # Add ranks
    for idx, entry in enumerate(leaderboard_entries[:limit]):
        entry["rank"] = idx + 1
    
    return [LeaderboardEntry(**entry) for entry in leaderboard_entries[:limit]]


@router.get("/all-india", response_model=LeaderboardResponse)
async def get_all_india_leaderboard(
    limit: int = Query(100, le=1000),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get All-India leaderboard (top contributors across all colleges)"""
    
    # Check cache first (refresh every 1 hour)
    cache_key = "all_india"
    cached = await db.leaderboards.find_one({
        "type": "all_india",
        "updated_at": {"$gte": datetime.utcnow() - timedelta(hours=1)}
    })
    
    if cached and cached.get("rankings"):
        rankings = [LeaderboardEntry(**entry) for entry in cached["rankings"]]
    else:
        # Generate fresh leaderboard
        rankings = await get_leaderboard_data(db, "all_india", limit=limit)
        
        # Cache it
        await db.leaderboards.update_one(
            {"type": "all_india"},
            {
                "$set": {
                    "rankings": [entry.dict() for entry in rankings],
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    # Find current user's rank
    user_rank = None
    for entry in rankings:
        if entry.user_id == user_id:
            user_rank = entry.rank
            break
    
    # If user not in top rankings, calculate their actual rank
    if user_rank is None:
        user_score = await calculate_user_score(db, user_id)
        users_ahead = await db.users.count_documents({})
        # Simplified rank calculation
        user_rank = users_ahead + 1
    
    return LeaderboardResponse(
        type="all_india",
        rankings=rankings,
        user_rank=user_rank,
        total_users=len(rankings),
        updated_at=datetime.utcnow()
    )


@router.get("/college", response_model=LeaderboardResponse)
async def get_college_leaderboard(
    college: Optional[str] = None,
    limit: int = Query(100, le=500),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get College-specific leaderboard"""
    
    # Use current user's college if not specified
    if not college:
        user = await db.users.find_one({"id": user_id})
        college = user.get("college")
    
    if not college:
        raise HTTPException(
            status_code=400,
            detail="College not specified and user has no college set"
        )
    
    # Check cache
    cache_key = f"college_{college}"
    cached = await db.leaderboards.find_one({
        "type": "college",
        "filter.college": college,
        "updated_at": {"$gte": datetime.utcnow() - timedelta(minutes=30)}
    })
    
    if cached and cached.get("rankings"):
        rankings = [LeaderboardEntry(**entry) for entry in cached["rankings"]]
    else:
        # Generate fresh leaderboard
        rankings = await get_leaderboard_data(db, "college", college=college, limit=limit)
        
        # Cache it
        await db.leaderboards.update_one(
            {"type": "college", "filter.college": college},
            {
                "$set": {
                    "rankings": [entry.dict() for entry in rankings],
                    "filter": {"college": college},
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    # Find current user's rank
    user_rank = None
    for entry in rankings:
        if entry.user_id == user_id:
            user_rank = entry.rank
            break
    
    return LeaderboardResponse(
        type="college",
        filter={"college": college},
        rankings=rankings,
        user_rank=user_rank,
        total_users=len(rankings),
        updated_at=datetime.utcnow()
    )


@router.get("/department", response_model=LeaderboardResponse)
async def get_department_leaderboard(
    department: Optional[str] = None,
    limit: int = Query(100, le=500),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get Department-specific leaderboard"""
    
    # Use current user's department if not specified
    if not department:
        user = await db.users.find_one({"id": user_id})
        department = user.get("department")
    
    if not department:
        raise HTTPException(
            status_code=400,
            detail="Department not specified"
        )
    
    # Check cache
    cached = await db.leaderboards.find_one({
        "type": "department",
        "filter.department": department,
        "updated_at": {"$gte": datetime.utcnow() - timedelta(minutes=30)}
    })
    
    if cached and cached.get("rankings"):
        rankings = [LeaderboardEntry(**entry) for entry in cached["rankings"]]
    else:
        # Generate fresh leaderboard
        rankings = await get_leaderboard_data(db, "department", department=department, limit=limit)
        
        # Cache it
        await db.leaderboards.update_one(
            {"type": "department", "filter.department": department},
            {
                "$set": {
                    "rankings": [entry.dict() for entry in rankings],
                    "filter": {"department": department},
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    # Find current user's rank
    user_rank = None
    for entry in rankings:
        if entry.user_id == user_id:
            user_rank = entry.rank
            break
    
    return LeaderboardResponse(
        type="department",
        filter={"department": department},
        rankings=rankings,
        user_rank=user_rank,
        total_users=len(rankings),
        updated_at=datetime.utcnow()
    )


@router.get("/top-contributors")
async def get_top_contributors(
    timeframe: str = Query("all_time", pattern="^(today|week|month|all_time)$"),
    limit: int = Query(10, le=50),
    db = Depends(get_database)
):
    """Get top contributors for a specific timeframe"""
    
    # Calculate date filter
    now = datetime.utcnow()
    date_filter = {}
    
    if timeframe == "today":
        date_filter = {"uploaded_at": {"$gte": datetime(now.year, now.month, now.day)}}
    elif timeframe == "week":
        date_filter = {"uploaded_at": {"$gte": now - timedelta(days=7)}}
    elif timeframe == "month":
        date_filter = {"uploaded_at": {"$gte": now - timedelta(days=30)}}
    
    # Aggregate top uploaders (notes use 'userId' field)
    pipeline = [
        {"$match": {**date_filter, "is_approved": True}},
        {"$group": {
            "_id": "$userId",
            "upload_count": {"$sum": 1},
            "total_downloads": {"$sum": "$downloadCount"}
        }},
        {"$sort": {"upload_count": -1}},
        {"$limit": limit}
    ]
    
    top_uploaders = await db.notes.aggregate(pipeline).to_list(None)
    
    # Enrich with user data
    result = []
    for item in top_uploaders:
        # item["_id"] is the userId from the notes
        user_id = item["_id"]
        if not user_id:
            continue
            
        user = await db.users.find_one({"id": user_id})
        if user:
            result.append({
                "user_id": user_id,
                "usn": user.get("usn"),
                "department": user.get("department"),
                "college": user.get("college"),
                "upload_count": item["upload_count"],
                "total_downloads": item["total_downloads"],
                "profile_picture": user.get("profile_picture")
            })
    
    return {
        "timeframe": timeframe,
        "contributors": result
    }


@router.post("/refresh")
async def refresh_leaderboards(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Force refresh all leaderboards (admin or for testing)"""
    
    # Delete all cached leaderboards
    await db.leaderboards.delete_many({})
    
    return {
        "success": True,
        "message": "All leaderboard caches cleared. They will be regenerated on next request."
    }
