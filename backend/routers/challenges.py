"""
Challenges & Competitions Router
Daily challenges, battles, department wars, college competitions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import random

from auth import get_current_user_id
from models import ChallengeCreate, ChallengeResponse, BattleCreate, BattleResponse
from database import get_database


router = APIRouter(prefix="/api/challenges", tags=["challenges"])


# Daily Challenges
DAILY_CHALLENGES = [
    {"type": "upload", "title": "Upload Master", "description": "Upload 3 notes today", "target": 3, "reward_points": 100},
    {"type": "help", "title": "Helper", "description": "Help 5 students today", "target": 5, "reward_points": 80},
    {"type": "download", "title": "Knowledge Seeker", "description": "Download 10 notes today", "target": 10, "reward_points": 50},
    {"type": "streak", "title": "Consistency King", "description": "Maintain your streak", "target": 1, "reward_points": 50},
    {"type": "social", "title": "Social Butterfly", "description": "Follow 3 new users", "target": 3, "reward_points": 30},
]


@router.get("/daily")
async def get_daily_challenges(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get today's daily challenges with progress"""
    
    today = datetime.utcnow().date()
    
    # Get user's progress for each challenge type today
    user = await db.users.find_one({"id": user_id})
    
    challenges_with_progress = []
    
    for challenge in DAILY_CHALLENGES:
        # Get user's progress for this challenge type
        progress = await db.challenge_progress.find_one({
            "user_id": user_id,
            "challenge_type": challenge["type"],
            "date": today.isoformat()
        })
        
        current_progress = progress["progress"] if progress else 0
        completed = current_progress >= challenge["target"]
        
        challenges_with_progress.append({
            **challenge,
            "id": f"{challenge['type']}-{today.isoformat()}",
            "current_progress": current_progress,
            "completed": completed,
            "date": today.isoformat()
        })
    
    # Count completed challenges
    completed_count = sum(1 for c in challenges_with_progress if c["completed"])
    
    return {
        "challenges": challenges_with_progress,
        "total": len(DAILY_CHALLENGES),
        "completed": completed_count,
        "date": today.isoformat()
    }


@router.post("/daily/{challenge_type}/progress")
async def update_challenge_progress(
    challenge_type: str,
    increment: int = 1,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Update progress for a daily challenge"""
    
    today = datetime.utcnow().date()
    
    # Find or create progress record
    progress = await db.challenge_progress.find_one({
        "user_id": user_id,
        "challenge_type": challenge_type,
        "date": today.isoformat()
    })
    
    if progress:
        # Update existing
        new_progress = progress["progress"] + increment
        await db.challenge_progress.update_one(
            {"_id": progress["_id"]},
            {"$set": {"progress": new_progress, "updated_at": datetime.utcnow()}}
        )
    else:
        # Create new
        await db.challenge_progress.insert_one({
            "user_id": user_id,
            "challenge_type": challenge_type,
            "date": today.isoformat(),
            "progress": increment,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        new_progress = increment
    
    # Check if challenge completed
    challenge = next((c for c in DAILY_CHALLENGES if c["type"] == challenge_type), None)
    if challenge and new_progress >= challenge["target"]:
        # Award points
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"points": challenge["reward_points"]}}
        )
        
        return {
            "success": True,
            "completed": True,
            "progress": new_progress,
            "reward_points": challenge["reward_points"],
            "message": f"Challenge completed! +{challenge['reward_points']} points 🎉"
        }
    
    return {
        "success": True,
        "completed": False,
        "progress": new_progress
    }


# 1v1 Battles
@router.post("/battle/create")
async def create_battle(
    opponent_id: str,
    challenge_type: str,
    duration_days: int = 7,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Create a 1v1 battle challenge"""
    
    # Validate opponent exists
    opponent = await db.users.find_one({"id": opponent_id})
    if not opponent:
        raise HTTPException(status_code=404, detail="Opponent not found")
    
    battle_id = str(uuid.uuid4())
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=duration_days)
    
    battle = {
        "id": battle_id,
        "challenger_id": user_id,
        "opponent_id": opponent_id,
        "challenge_type": challenge_type,
        "start_date": start_date,
        "end_date": end_date,
        "status": "active",
        "challenger_score": 0,
        "opponent_score": 0,
        "winner_id": None,
        "created_at": start_date
    }
    
    await db.battles.insert_one(battle)
    
    # Send notification to opponent
    await db.notifications.insert_one({
        "user_id": opponent_id,
        "type": "battle_challenge",
        "title": "Battle Challenge!",
        "message": f"You've been challenged to a {challenge_type} battle!",
        "data": {"battle_id": battle_id},
        "read": False,
        "created_at": datetime.utcnow()
    })
    
    return {
        "battle_id": battle_id,
        "message": "Battle created! Challenge sent to opponent 🔥",
        "end_date": end_date.isoformat()
    }


@router.get("/battles/my")
async def get_my_battles(
    status: Optional[str] = "active",
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's battles"""
    
    query = {
        "$or": [
            {"challenger_id": user_id},
            {"opponent_id": user_id}
        ]
    }
    
    if status:
        query["status"] = status
    
    battles = await db.battles.find(query).sort("created_at", -1).to_list(None)
    
    # Enrich with user data
    for battle in battles:
        # Get opponent data
        opponent_id = battle["opponent_id"] if battle["challenger_id"] == user_id else battle["challenger_id"]
        opponent = await db.users.find_one({"id": opponent_id})
        
        battle["opponent_usn"] = opponent.get("usn") if opponent else "Unknown"
        battle["is_challenger"] = battle["challenger_id"] == user_id
        
        # Calculate days remaining
        if battle["status"] == "active":
            days_left = (battle["end_date"] - datetime.utcnow()).days
            battle["days_remaining"] = max(0, days_left)
    
    return {"battles": battles}


# Department Competitions
@router.get("/department-war")
async def get_department_war(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get current department vs department competition"""
    
    # Get current month's competition
    now = datetime.utcnow()
    month_key = now.strftime("%Y-%m")
    
    # Aggregate points by department for this month
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": datetime(now.year, now.month, 1)}
            }
        },
        {
            "$group": {
                "_id": "$department",
                "total_points": {"$sum": "$points"},
                "upload_count": {"$sum": 1},
                "member_count": {"$sum": 1}
            }
        },
        {"$sort": {"total_points": -1}},
        {"$limit": 10}
    ]
    
    # This is a simplified version - in production, track department stats separately
    departments = await db.users.aggregate([
        {"$group": {
            "_id": "$department",
            "total_points": {"$sum": "$points"},
            "member_count": {"$sum": 1}
        }},
        {"$sort": {"total_points": -1}},
        {"$limit": 10}
    ]).to_list(None)
    
    rankings = []
    for idx, dept in enumerate(departments):
        rankings.append({
            "rank": idx + 1,
            "department": dept["_id"],
            "total_points": dept["total_points"],
            "member_count": dept["member_count"],
            "avg_points": dept["total_points"] / dept["member_count"] if dept["member_count"] > 0 else 0
        })
    
    # Get user's department rank
    user = await db.users.find_one({"id": user_id})
    user_dept_rank = next((r for r in rankings if r["department"] == user.get("department")), None)
    
    return {
        "month": month_key,
        "rankings": rankings,
        "user_department": user.get("department"),
        "user_department_rank": user_dept_rank["rank"] if user_dept_rank else None,
        "total_departments": len(rankings)
    }


# College Wars
@router.get("/college-war")
async def get_college_war(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get current college vs college competition"""
    
    # Aggregate by college
    colleges = await db.users.aggregate([
        {"$group": {
            "_id": "$college",
            "total_points": {"$sum": "$points"},
            "member_count": {"$sum": 1}
        }},
        {"$sort": {"total_points": -1}},
        {"$limit": 10}
    ]).to_list(None)
    
    rankings = []
    for idx, college in enumerate(colleges):
        rankings.append({
            "rank": idx + 1,
            "college": college["_id"],
            "total_points": college["total_points"],
            "member_count": college["member_count"],
            "avg_points": college["total_points"] / college["member_count"] if college["member_count"] > 0 else 0
        })
    
    # Get user's college rank
    user = await db.users.find_one({"id": user_id})
    user_college_rank = next((r for r in rankings if r["college"] == user.get("college")), None)
    
    return {
        "rankings": rankings,
        "user_college": user.get("college"),
        "user_college_rank": user_college_rank["rank"] if user_college_rank else None,
        "total_colleges": len(rankings)
    }


# Seasonal Events
@router.get("/seasonal-events")
async def get_seasonal_events(
    db = Depends(get_database)
):
    """Get current seasonal events"""
    
    now = datetime.utcnow()
    
    # Check for active events
    active_events = await db.seasonal_events.find({
        "start_date": {"$lte": now},
        "end_date": {"$gte": now},
        "active": True
    }).to_list(None)
    
    return {"events": active_events}


@router.get("/stats")
async def get_challenge_stats(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's challenge statistics"""
    
    # Count completed daily challenges
    completed_challenges = await db.challenge_progress.count_documents({
        "user_id": user_id,
        "progress": {"$gte": 1}  # Simplified - should check against target
    })
    
    # Count battle wins
    battle_wins = await db.battles.count_documents({
        "winner_id": user_id,
        "status": "completed"
    })
    
    # Count total battles
    total_battles = await db.battles.count_documents({
        "$or": [
            {"challenger_id": user_id},
            {"opponent_id": user_id}
        ]
    })
    
    return {
        "daily_challenges_completed": completed_challenges,
        "battle_wins": battle_wins,
        "total_battles": total_battles,
        "win_rate": (battle_wins / total_battles * 100) if total_battles > 0 else 0
    }
