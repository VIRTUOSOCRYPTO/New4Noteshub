"""
Instagram Story Templates API
Generate beautiful story templates for viral sharing
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional
import os
from auth import get_current_user_id
from database import get_database

router = APIRouter(prefix="/api/instagram", tags=["Instagram Stories"])

# Story template configurations
STORY_TEMPLATES = {
    "achievement_unlock": {
        "title": "Achievement Unlocked! 🏆",
        "gradient": "from-amber-400 via-orange-500 to-red-500",
        "emoji": "🏆",
        "format": "{achievement_name}\n{rarity} Achievement\n+{points} Points"
    },
    "streak_milestone": {
        "title": "Streak Milestone! 🔥",
        "gradient": "from-orange-500 via-red-500 to-pink-500",
        "emoji": "🔥",
        "format": "{streak_days} Day Streak!\nKeep the fire burning!"
    },
    "leaderboard_rank": {
        "title": "Leaderboard Rank 📊",
        "gradient": "from-yellow-400 via-amber-500 to-orange-600",
        "emoji": "👑",
        "format": "Rank #{rank}\n{leaderboard_type}\nScore: {score}"
    },
    "level_up": {
        "title": "Level Up! ⭐",
        "gradient": "from-purple-500 via-pink-500 to-red-500",
        "emoji": "⭐",
        "format": "Level {level}\n{level_name}\n{total_points} Points"
    },
    "exam_countdown": {
        "title": "Exam Alert! ⏰",
        "gradient": "from-red-500 via-orange-500 to-yellow-500",
        "emoji": "⚠️",
        "format": "{subject} Exam\nin {days} days!\nGet ready!"
    },
    "study_group": {
        "title": "Study Together 👥",
        "gradient": "from-blue-500 via-purple-500 to-pink-500",
        "emoji": "👥",
        "format": "{group_name}\n{member_count} Members\nJoin us!"
    },
    "notes_shared": {
        "title": "Shared Notes 📚",
        "gradient": "from-green-500 via-teal-500 to-blue-500",
        "emoji": "📚",
        "format": "{note_title}\n{subject}\nHelping {download_count}+ students"
    },
    "referral_success": {
        "title": "Growing Together 🎁",
        "gradient": "from-pink-500 via-purple-500 to-indigo-500",
        "emoji": "🎁",
        "format": "{referral_count} Friends Joined!\nThanks for sharing NotesHub"
    },
    "contest_winner": {
        "title": "Contest Winner! 🎉",
        "gradient": "from-yellow-400 via-amber-500 to-orange-500",
        "emoji": "🎉",
        "format": "Won: {contest_name}\n{vote_count} votes\nChampion!"
    },
    "mystery_reward": {
        "title": "Mystery Reward! 🎁",
        "gradient": "from-purple-600 via-pink-600 to-red-600",
        "emoji": "✨",
        "format": "Unlocked: {reward_name}\n{reward_value}\nLucky day!"
    }
}


@router.get("/templates")
async def get_templates():
    """Get all available story templates"""
    return {
        "templates": list(STORY_TEMPLATES.keys()),
        "template_details": STORY_TEMPLATES
    }


@router.get("/generate/achievement/{achievement_id}")
async def generate_achievement_story(
    achievement_id: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate Instagram story data for achievement unlock"""
    
    # Get achievement details
    achievement = await db.user_achievements.find_one({
        "user_id": user_id,
        "achievement_id": achievement_id
    })
    
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Get achievement definition
    from routers.achievements import ACHIEVEMENTS
    achievement_def = next((a for a in ACHIEVEMENTS if a["id"] == achievement_id), None)
    
    if not achievement_def:
        raise HTTPException(status_code=404, detail="Achievement definition not found")
    
    template = STORY_TEMPLATES["achievement_unlock"]
    
    return {
        "template_type": "achievement_unlock",
        "template": template,
        "data": {
            "achievement_name": achievement_def["name"],
            "rarity": achievement_def["rarity"],
            "points": achievement_def["points"],
            "description": achievement_def["description"],
            "unlocked_at": achievement.get("unlocked_at", datetime.now()).isoformat()
        },
        "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/viral?tab=achievements",
        "hashtags": ["NotesHub", "Achievement", "StudyGoals", achievement_def["rarity"]]
    }


@router.get("/generate/streak")
async def generate_streak_story(
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate Instagram story for streak milestone"""
    
    streak = await db.streaks.find_one({"user_id": user_id})
    
    if not streak:
        raise HTTPException(status_code=404, detail="Streak data not found")
    
    template = STORY_TEMPLATES["streak_milestone"]
    
    return {
        "template_type": "streak_milestone",
        "template": template,
        "data": {
            "streak_days": streak.get("current_streak", 0),
            "longest_streak": streak.get("longest_streak", 0),
            "total_activities": streak.get("total_activities", 0)
        },
        "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/viral",
        "hashtags": ["NotesHub", "StudyStreak", "Consistency", "StudyMotivation"]
    }


@router.get("/generate/leaderboard")
async def generate_leaderboard_story(
    leaderboard_type: str = "all_india",
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate Instagram story for leaderboard ranking"""
    
    # Get user's leaderboard data
    user_points = await db.user_points.find_one({"user_id": user_id})
    
    if not user_points:
        raise HTTPException(status_code=404, detail="Points data not found")
    
    # Calculate rank (simplified - in production, query leaderboard)
    total_users = await db.user_points.count_documents({})
    users_above = await db.user_points.count_documents({
        "total_points": {"$gt": user_points.get("total_points", 0)}
    })
    rank = users_above + 1
    
    template = STORY_TEMPLATES["leaderboard_rank"]
    
    return {
        "template_type": "leaderboard_rank",
        "template": template,
        "data": {
            "rank": rank,
            "leaderboard_type": leaderboard_type.replace("_", " ").title(),
            "score": user_points.get("total_points", 0),
            "level": user_points.get("level", 1),
            "total_users": total_users
        },
        "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/viral?tab=ranks",
        "hashtags": ["NotesHub", "Leaderboard", "TopStudent", "StudyChampion"]
    }


@router.get("/generate/level-up")
async def generate_level_up_story(
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate Instagram story for level up"""
    
    user_points = await db.user_points.find_one({"user_id": user_id})
    
    if not user_points:
        raise HTTPException(status_code=404, detail="Points data not found")
    
    template = STORY_TEMPLATES["level_up"]
    
    return {
        "template_type": "level_up",
        "template": template,
        "data": {
            "level": user_points.get("level", 1),
            "level_name": user_points.get("level_name", "Newbie"),
            "total_points": user_points.get("total_points", 0)
        },
        "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/viral",
        "hashtags": ["NotesHub", "LevelUp", "StudyProgress", "Achievement"]
    }


@router.get("/generate/exam/{exam_id}")
async def generate_exam_story(
    exam_id: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate Instagram story for exam countdown"""
    
    exam = await db.exams.find_one({"id": exam_id})
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam_date = exam.get("exam_date")
    days_until = (exam_date - datetime.now()).days
    
    template = STORY_TEMPLATES["exam_countdown"]
    
    return {
        "template_type": "exam_countdown",
        "template": template,
        "data": {
            "subject": exam.get("subject"),
            "days": days_until,
            "exam_type": exam.get("exam_type", "Semester"),
            "department": exam.get("department")
        },
        "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/viral?tab=exams",
        "hashtags": ["NotesHub", "ExamPrep", exam.get("subject", "").replace(" ", ""), "StudyMode"]
    }


@router.get("/generate/group/{group_id}")
async def generate_study_group_story(
    group_id: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate Instagram story for study group"""
    
    group = await db.study_groups.find_one({"id": group_id})
    
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found")
    
    template = STORY_TEMPLATES["study_group"]
    
    return {
        "template_type": "study_group",
        "template": template,
        "data": {
            "group_name": group.get("name"),
            "member_count": group.get("member_count", 0),
            "subject": group.get("subject"),
            "description": group.get("description")
        },
        "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/viral?tab=groups",
        "hashtags": ["NotesHub", "StudyGroup", "StudyTogether", group.get("subject", "").replace(" ", "")]
    }


@router.get("/generate/note/{note_id}")
async def generate_note_story(
    note_id: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate Instagram story for shared notes"""
    
    note = await db.notes.find_one({"id": note_id})
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    template = STORY_TEMPLATES["notes_shared"]
    
    return {
        "template_type": "notes_shared",
        "template": template,
        "data": {
            "note_title": note.get("title"),
            "subject": note.get("subject"),
            "download_count": note.get("download_count", 0),
            "college": note.get("college")
        },
        "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/notes/{note_id}",
        "hashtags": ["NotesHub", "StudyNotes", note.get("subject", "").replace(" ", ""), "FreeNotes"]
    }


@router.get("/generate/referral")
async def generate_referral_story(
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate Instagram story for referral success"""
    
    referral = await db.referrals.find_one({"user_id": user_id})
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral data not found")
    
    template = STORY_TEMPLATES["referral_success"]
    
    return {
        "template_type": "referral_success",
        "template": template,
        "data": {
            "referral_count": referral.get("total_referrals", 0),
            "referral_code": referral.get("referral_code"),
            "rewards_earned": referral.get("rewards_earned", {})
        },
        "share_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/viral?tab=referrals&code={referral.get('referral_code')}",
        "hashtags": ["NotesHub", "Referral", "StudyTogether", "JoinUs"]
    }


@router.post("/track-story-share")
async def track_story_share(
    template_type: str,
    platform: str = "instagram",
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Track Instagram story shares for analytics"""
    
    # Record the share
    await db.instagram_shares.insert_one({
        "user_id": user_id,
        "usn": user_id,
        "template_type": template_type,
        "platform": platform,
        "shared_at": datetime.now()
    })
    
    # Award points for sharing
    await db.user_points.update_one(
        {"user_id": user_id},
        {
            "$inc": {"total_points": 10},
            "$push": {
                "points_history": {
                    "action": f"instagram_story_{template_type}",
                    "points": 10,
                    "timestamp": datetime.now()
                }
            }
        }
    )
    
    return {
        "success": True,
        "points_earned": 10,
        "message": "Thanks for sharing! 🎉"
    }


@router.get("/stats")
async def get_story_stats(
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Get user's Instagram story sharing statistics"""
    
    total_shares = await db.instagram_shares.count_documents({
        "user_id": user_id
    })
    
    # Get shares by template type
    shares_by_type = await db.instagram_shares.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$template_type",
            "count": {"$sum": 1}
        }}
    ]).to_list(100)
    
    return {
        "total_shares": total_shares,
        "shares_by_type": shares_by_type,
        "points_earned": total_shares * 10
    }
