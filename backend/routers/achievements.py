"""
Achievements Router - 50+ Achievements for Engagement
Gamification through achievement unlocking and progress tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import uuid

from auth import get_current_user_id
from models import (
    AchievementDefinition, AchievementResponse, 
    AchievementProgress, UserAchievement
)
from database import get_database
from routers.gamification import update_user_points


router = APIRouter(prefix="/api/achievements", tags=["achievements"])


# Achievement Definitions (15 Key Achievements - Simplified for clarity)
ACHIEVEMENTS = [
    # Upload Achievements (5)
    {"id": "first_note", "name": "First Note", "description": "Upload your first note", "category": "upload", "icon": "📝", "criteria": {"uploads": 1}, "rarity": "common", "points": 50},
    {"id": "generous", "name": "Generous", "description": "Upload 10 notes", "category": "upload", "icon": "🎁", "criteria": {"uploads": 10}, "rarity": "uncommon", "points": 150},
    {"id": "scholar", "name": "Scholar", "description": "Upload 50 notes", "category": "upload", "icon": "📚", "criteria": {"uploads": 50}, "rarity": "rare", "points": 500},
    {"id": "professor", "name": "Professor", "description": "Upload 100 notes", "category": "upload", "icon": "🎓", "criteria": {"uploads": 100}, "rarity": "epic", "points": 1000},
    {"id": "quality_contributor", "name": "Quality Contributor", "description": "Upload 10 notes with no flags", "category": "upload", "icon": "✨", "criteria": {"clean_uploads": 10}, "rarity": "rare", "points": 300},
    
    # Download Achievements (3)
    {"id": "knowledge_seeker", "name": "Knowledge Seeker", "description": "Download 20 notes", "category": "download", "icon": "🔍", "criteria": {"downloads": 20}, "rarity": "common", "points": 50},
    {"id": "bookworm", "name": "Bookworm", "description": "Download 100 notes", "category": "download", "icon": "📖", "criteria": {"downloads": 100}, "rarity": "uncommon", "points": 150},
    {"id": "exam_prep", "name": "Exam Prep Master", "description": "Download 50 notes before exam", "category": "download", "icon": "📅", "criteria": {"exam_downloads": 50}, "rarity": "uncommon", "points": 200},
    
    # Social Achievements (3)
    {"id": "helper", "name": "Helper", "description": "Your notes downloaded 100 times", "category": "social", "icon": "🤝", "criteria": {"note_downloads": 100}, "rarity": "uncommon", "points": 200},
    {"id": "popular", "name": "Popular", "description": "Your notes downloaded 500 times", "category": "social", "icon": "⭐", "criteria": {"note_downloads": 500}, "rarity": "rare", "points": 500},
    {"id": "referral_master", "name": "Referral Master", "description": "Refer 10 friends", "category": "social", "icon": "🎯", "criteria": {"referrals": 10}, "rarity": "epic", "points": 800},
    
    # Streak Achievements (4)
    {"id": "week_warrior", "name": "Week Warrior", "description": "7-day streak", "category": "streak", "icon": "🔥", "criteria": {"streak": 7}, "rarity": "common", "points": 100},
    {"id": "month_master", "name": "Month Master", "description": "30-day streak", "category": "streak", "icon": "📆", "criteria": {"streak": 30}, "rarity": "uncommon", "points": 300},
    {"id": "hundred_days", "name": "Hundred Days", "description": "100-day streak", "category": "streak", "icon": "💯", "criteria": {"streak": 100}, "rarity": "rare", "points": 800},
    {"id": "year_champion_streak", "name": "Year Champion", "description": "365-day streak", "category": "streak", "icon": "🎉", "criteria": {"streak": 365}, "rarity": "legendary", "points": 3000},
]


async def check_and_unlock_achievements(db, user_id: str):
    """Check user's progress and unlock eligible achievements"""
    
    # Get user data
    user = await db.users.find_one({"id": user_id})
    if not user:
        return []
    
    # Get user stats
    upload_count = await db.notes.count_documents({"userId": user_id, "is_approved": True})
    
    # Get download count from user's download history
    download_count = await db.downloads.count_documents({"user_id": user_id})
    
    # Get notes user uploaded and count total downloads
    user_notes = await db.notes.find({"userId": user_id}).to_list(None)
    total_note_downloads = sum(note.get("downloadCount", 0) for note in user_notes)
    
    # Get streak data
    streak_data = await db.streaks.find_one({"user_id": user_id})
    current_streak = streak_data.get("current_streak", 0) if streak_data else 0
    total_activities = streak_data.get("total_activities", 0) if streak_data else 0
    
    # Get referral data
    referral_data = await db.referrals.find_one({"user_id": user_id})
    total_referrals = referral_data.get("total_referrals", 0) if referral_data else 0
    
    # Get share count
    share_count = await db.share_actions.count_documents({"user_id": user_id})
    
    # Get followers count
    followers_count = await db.follows.count_documents({"following_id": user_id})
    following_count = await db.follows.count_documents({"follower_id": user_id})
    
    # Get groups
    groups_created = await db.study_groups.count_documents({"created_by": user_id})
    groups_joined = await db.study_group_members.count_documents({"user_id": user_id})
    
    # Get user points for level
    user_points = await db.user_points.find_one({"user_id": user_id})
    user_level = user_points.get("level", 1) if user_points else 1
    
    # Get already unlocked achievements
    unlocked = await db.user_achievements.find({"user_id": user_id}).to_list(None)
    unlocked_ids = {ach["achievement_id"] for ach in unlocked}
    
    # Build user stats for checking
    user_stats = {
        "uploads": upload_count,
        "downloads": download_count,
        "note_downloads": total_note_downloads,
        "streak": current_streak,
        "total_activities": total_activities,
        "referrals": total_referrals,
        "shares": share_count,
        "followers": followers_count,
        "following": following_count,
        "groups_created": groups_created,
        "groups_joined": groups_joined,
        "level": user_level,
    }
    
    # Check each achievement
    newly_unlocked = []
    
    for achievement in ACHIEVEMENTS:
        ach_id = achievement["id"]
        
        # Skip if already unlocked
        if ach_id in unlocked_ids:
            continue
        
        # Check criteria
        criteria = achievement["criteria"]
        unlocked = False
        
        for key, required_value in criteria.items():
            if key in user_stats:
                if isinstance(required_value, bool):
                    unlocked = user_stats[key] == required_value
                elif isinstance(required_value, int):
                    unlocked = user_stats[key] >= required_value
                else:
                    unlocked = False
                
                if unlocked:
                    break
        
        # Unlock achievement
        if unlocked:
            await db.user_achievements.insert_one({
                "user_id": user_id,
                "achievement_id": ach_id,
                "unlocked_at": datetime.utcnow()
            })
            
            # Award points
            await update_user_points(db, user_id, f"achievement_{ach_id}", achievement["points"])
            
            newly_unlocked.append(achievement)
    
    return newly_unlocked


@router.get("/all", response_model=List[AchievementResponse])
async def get_all_achievements(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get all achievements with user's unlock status"""
    
    # Get user's unlocked achievements
    unlocked = await db.user_achievements.find({"user_id": user_id}).to_list(None)
    unlocked_dict = {ach["achievement_id"]: ach for ach in unlocked}
    
    # Build response
    result = []
    for achievement in ACHIEVEMENTS:
        ach_id = achievement["id"]
        is_unlocked = ach_id in unlocked_dict
        
        result.append(AchievementResponse(
            id=ach_id,
            name=achievement["name"],
            description=achievement["description"],
            category=achievement["category"],
            icon=achievement["icon"],
            rarity=achievement["rarity"],
            points=achievement["points"],
            unlocked=is_unlocked,
            unlocked_at=unlocked_dict[ach_id]["unlocked_at"] if is_unlocked else None
        ))
    
    return result


@router.get("/unlocked")
async def get_unlocked_achievements(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get only unlocked achievements"""
    
    unlocked = await db.user_achievements.find({"user_id": user_id}).to_list(None)
    
    # Enrich with achievement details
    result = []
    unlocked_ids = {ach["achievement_id"] for ach in unlocked}
    
    for achievement in ACHIEVEMENTS:
        if achievement["id"] in unlocked_ids:
            ach_data = next(a for a in unlocked if a["achievement_id"] == achievement["id"])
            result.append({
                **achievement,
                "unlocked_at": ach_data["unlocked_at"]
            })
    
    # Sort by unlock date (most recent first)
    result.sort(key=lambda x: x["unlocked_at"], reverse=True)
    
    return {"achievements": result, "count": len(result)}


@router.post("/check")
async def check_achievements(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Manually trigger achievement check"""
    
    newly_unlocked = await check_and_unlock_achievements(db, user_id)
    
    return {
        "success": True,
        "newly_unlocked": newly_unlocked,
        "count": len(newly_unlocked)
    }


@router.get("/progress")
async def get_achievement_progress(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get progress towards locked achievements"""
    
    # Get user stats (same as check_and_unlock_achievements)
    upload_count = await db.notes.count_documents({"userId": user_id, "is_approved": True})
    download_count = await db.downloads.count_documents({"user_id": user_id})
    
    user_notes = await db.notes.find({"userId": user_id}).to_list(None)
    total_note_downloads = sum(note.get("downloadCount", 0) for note in user_notes)
    
    streak_data = await db.streaks.find_one({"user_id": user_id})
    current_streak = streak_data.get("current_streak", 0) if streak_data else 0
    
    user_stats = {
        "uploads": upload_count,
        "downloads": download_count,
        "note_downloads": total_note_downloads,
        "streak": current_streak,
    }
    
    # Get unlocked achievements
    unlocked = await db.user_achievements.find({"user_id": user_id}).to_list(None)
    unlocked_ids = {ach["achievement_id"] for ach in unlocked}
    
    # Calculate progress for locked achievements
    progress = []
    
    for achievement in ACHIEVEMENTS:
        if achievement["id"] in unlocked_ids:
            continue
        
        criteria = achievement["criteria"]
        
        # Get the first criteria (simplified)
        for key, required_value in criteria.items():
            if key in user_stats and isinstance(required_value, int):
                current = user_stats[key]
                percentage = min((current / required_value) * 100, 100)
                
                progress.append(AchievementProgress(
                    achievement_id=achievement["id"],
                    current=current,
                    required=required_value,
                    percentage=round(percentage, 1)
                ))
                break
    
    return {"progress": progress}


@router.get("/categories")
async def get_achievement_categories(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get achievements grouped by category"""
    
    unlocked = await db.user_achievements.find({"user_id": user_id}).to_list(None)
    unlocked_ids = {ach["achievement_id"] for ach in unlocked}
    
    categories = {}
    
    for achievement in ACHIEVEMENTS:
        category = achievement["category"]
        if category not in categories:
            categories[category] = {
                "total": 0,
                "unlocked": 0,
                "achievements": []
            }
        
        categories[category]["total"] += 1
        if achievement["id"] in unlocked_ids:
            categories[category]["unlocked"] += 1
        
        categories[category]["achievements"].append({
            **achievement,
            "unlocked": achievement["id"] in unlocked_ids
        })
    
    return {"categories": categories}


@router.get("/stats")
async def get_achievement_stats(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get overall achievement statistics"""
    
    unlocked = await db.user_achievements.find({"user_id": user_id}).to_list(None)
    
    total_achievements = len(ACHIEVEMENTS)
    unlocked_count = len(unlocked)
    completion_percentage = (unlocked_count / total_achievements) * 100
    
    # Count by rarity
    rarity_counts = {"common": 0, "uncommon": 0, "rare": 0, "epic": 0, "legendary": 0}
    unlocked_ids = {ach["achievement_id"] for ach in unlocked}
    
    for achievement in ACHIEVEMENTS:
        if achievement["id"] in unlocked_ids:
            rarity_counts[achievement["rarity"]] += 1
    
    return {
        "total_achievements": total_achievements,
        "unlocked": unlocked_count,
        "locked": total_achievements - unlocked_count,
        "completion_percentage": round(completion_percentage, 1),
        "rarity_breakdown": rarity_counts
    }
