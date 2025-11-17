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


# Achievement Definitions (50+ Achievements for Maximum Engagement)
ACHIEVEMENTS = [
    # Upload Achievements (10)
    {"id": "first_note", "name": "First Note", "description": "Upload your first note", "category": "upload", "icon": "📝", "criteria": {"uploads": 1}, "rarity": "common", "points": 50},
    {"id": "getting_started", "name": "Getting Started", "description": "Upload 5 notes", "category": "upload", "icon": "🚀", "criteria": {"uploads": 5}, "rarity": "common", "points": 100},
    {"id": "generous", "name": "Generous", "description": "Upload 10 notes", "category": "upload", "icon": "🎁", "criteria": {"uploads": 10}, "rarity": "uncommon", "points": 150},
    {"id": "contributor", "name": "Contributor", "description": "Upload 25 notes", "category": "upload", "icon": "📚", "criteria": {"uploads": 25}, "rarity": "uncommon", "points": 300},
    {"id": "scholar", "name": "Scholar", "description": "Upload 50 notes", "category": "upload", "icon": "🎓", "criteria": {"uploads": 50}, "rarity": "rare", "points": 500},
    {"id": "educator", "name": "Educator", "description": "Upload 75 notes", "category": "upload", "icon": "👨‍🏫", "criteria": {"uploads": 75}, "rarity": "rare", "points": 750},
    {"id": "professor", "name": "Professor", "description": "Upload 100 notes", "category": "upload", "icon": "🎯", "criteria": {"uploads": 100}, "rarity": "epic", "points": 1000},
    {"id": "master_educator", "name": "Master Educator", "description": "Upload 200 notes", "category": "upload", "icon": "👑", "criteria": {"uploads": 200}, "rarity": "epic", "points": 2000},
    {"id": "legendary_contributor", "name": "Legendary Contributor", "description": "Upload 500 notes", "category": "upload", "icon": "💎", "criteria": {"uploads": 500}, "rarity": "legendary", "points": 5000},
    {"id": "quality_contributor", "name": "Quality Contributor", "description": "Upload 10 notes with no flags", "category": "upload", "icon": "✨", "criteria": {"clean_uploads": 10}, "rarity": "rare", "points": 300},
    
    # Download Achievements (8)
    {"id": "curious_learner", "name": "Curious Learner", "description": "Download 5 notes", "category": "download", "icon": "👀", "criteria": {"downloads": 5}, "rarity": "common", "points": 25},
    {"id": "knowledge_seeker", "name": "Knowledge Seeker", "description": "Download 20 notes", "category": "download", "icon": "🔍", "criteria": {"downloads": 20}, "rarity": "common", "points": 50},
    {"id": "bookworm", "name": "Bookworm", "description": "Download 50 notes", "category": "download", "icon": "📖", "criteria": {"downloads": 50}, "rarity": "uncommon", "points": 100},
    {"id": "study_enthusiast", "name": "Study Enthusiast", "description": "Download 100 notes", "category": "download", "icon": "📚", "criteria": {"downloads": 100}, "rarity": "uncommon", "points": 150},
    {"id": "knowledge_collector", "name": "Knowledge Collector", "description": "Download 250 notes", "category": "download", "icon": "🗂️", "criteria": {"downloads": 250}, "rarity": "rare", "points": 300},
    {"id": "exam_prep", "name": "Exam Prep Master", "description": "Download 500 notes", "category": "download", "icon": "📅", "criteria": {"downloads": 500}, "rarity": "rare", "points": 500},
    {"id": "knowledge_hoarder", "name": "Knowledge Hoarder", "description": "Download 1000 notes", "category": "download", "icon": "🏆", "criteria": {"downloads": 1000}, "rarity": "epic", "points": 1000},
    {"id": "ultimate_learner", "name": "Ultimate Learner", "description": "Download 2500 notes", "category": "download", "icon": "🌟", "criteria": {"downloads": 2500}, "rarity": "legendary", "points": 2500},
    
    # Social Achievements (10)
    {"id": "helper", "name": "Helper", "description": "Your notes downloaded 50 times", "category": "social", "icon": "🤝", "criteria": {"note_downloads": 50}, "rarity": "uncommon", "points": 100},
    {"id": "popular", "name": "Popular", "description": "Your notes downloaded 200 times", "category": "social", "icon": "⭐", "criteria": {"note_downloads": 200}, "rarity": "rare", "points": 300},
    {"id": "influencer", "name": "Influencer", "description": "Your notes downloaded 500 times", "category": "social", "icon": "💫", "criteria": {"note_downloads": 500}, "rarity": "rare", "points": 500},
    {"id": "celebrity", "name": "Celebrity", "description": "Your notes downloaded 1000 times", "category": "social", "icon": "🌠", "criteria": {"note_downloads": 1000}, "rarity": "epic", "points": 1000},
    {"id": "legend", "name": "Legend", "description": "Your notes downloaded 5000 times", "category": "social", "icon": "🔥", "criteria": {"note_downloads": 5000}, "rarity": "legendary", "points": 5000},
    {"id": "first_follower", "name": "First Follower", "description": "Get your first follower", "category": "social", "icon": "👥", "criteria": {"followers": 1}, "rarity": "common", "points": 50},
    {"id": "social_butterfly", "name": "Social Butterfly", "description": "Get 10 followers", "category": "social", "icon": "🦋", "criteria": {"followers": 10}, "rarity": "uncommon", "points": 150},
    {"id": "crowd_favorite", "name": "Crowd Favorite", "description": "Get 50 followers", "category": "social", "icon": "👑", "criteria": {"followers": 50}, "rarity": "rare", "points": 500},
    {"id": "referral_starter", "name": "Referral Starter", "description": "Refer 3 friends", "category": "social", "icon": "🎯", "criteria": {"referrals": 3}, "rarity": "common", "points": 150},
    {"id": "referral_master", "name": "Referral Master", "description": "Refer 10 friends", "category": "social", "icon": "🏅", "criteria": {"referrals": 10}, "rarity": "epic", "points": 800},
    
    # Streak Achievements (8)
    {"id": "day_three", "name": "Three Days Strong", "description": "3-day streak", "category": "streak", "icon": "🔥", "criteria": {"streak": 3}, "rarity": "common", "points": 30},
    {"id": "week_warrior", "name": "Week Warrior", "description": "7-day streak", "category": "streak", "icon": "💪", "criteria": {"streak": 7}, "rarity": "common", "points": 100},
    {"id": "fortnight_fighter", "name": "Fortnight Fighter", "description": "14-day streak", "category": "streak", "icon": "⚔️", "criteria": {"streak": 14}, "rarity": "uncommon", "points": 200},
    {"id": "month_master", "name": "Month Master", "description": "30-day streak", "category": "streak", "icon": "📆", "criteria": {"streak": 30}, "rarity": "uncommon", "points": 300},
    {"id": "quarter_champion", "name": "Quarter Champion", "description": "90-day streak", "category": "streak", "icon": "🏆", "criteria": {"streak": 90}, "rarity": "rare", "points": 600},
    {"id": "hundred_days", "name": "Hundred Days", "description": "100-day streak", "category": "streak", "icon": "💯", "criteria": {"streak": 100}, "rarity": "rare", "points": 800},
    {"id": "half_year", "name": "Half Year Hero", "description": "180-day streak", "category": "streak", "icon": "🌟", "criteria": {"streak": 180}, "rarity": "epic", "points": 1500},
    {"id": "year_champion_streak", "name": "Year Champion", "description": "365-day streak", "category": "streak", "icon": "🎉", "criteria": {"streak": 365}, "rarity": "legendary", "points": 3000},
    
    # Level Achievements (6)
    {"id": "level_5", "name": "Level 5 Warrior", "description": "Reach Level 5", "category": "level", "icon": "🎖️", "criteria": {"level": 5}, "rarity": "common", "points": 100},
    {"id": "level_10", "name": "Level 10 Master", "description": "Reach Level 10", "category": "level", "icon": "🏅", "criteria": {"level": 10}, "rarity": "uncommon", "points": 200},
    {"id": "level_25", "name": "Level 25 Expert", "description": "Reach Level 25", "category": "level", "icon": "🏆", "criteria": {"level": 25}, "rarity": "rare", "points": 500},
    {"id": "level_50", "name": "Level 50 Champion", "description": "Reach Level 50", "category": "level", "icon": "👑", "criteria": {"level": 50}, "rarity": "epic", "points": 1000},
    {"id": "level_75", "name": "Level 75 Legend", "description": "Reach Level 75", "category": "level", "icon": "💎", "criteria": {"level": 75}, "rarity": "epic", "points": 2000},
    {"id": "level_100", "name": "Level 100 God", "description": "Reach Level 100", "category": "level", "icon": "⚡", "criteria": {"level": 100}, "rarity": "legendary", "points": 5000},
    
    # Study Group Achievements (6)
    {"id": "group_starter", "name": "Group Starter", "description": "Create your first study group", "category": "groups", "icon": "👥", "criteria": {"groups_created": 1}, "rarity": "common", "points": 100},
    {"id": "community_builder", "name": "Community Builder", "description": "Create 3 study groups", "category": "groups", "icon": "🏗️", "criteria": {"groups_created": 3}, "rarity": "uncommon", "points": 300},
    {"id": "group_joiner", "name": "Group Joiner", "description": "Join 3 study groups", "category": "groups", "icon": "🤗", "criteria": {"groups_joined": 3}, "rarity": "common", "points": 75},
    {"id": "social_learner", "name": "Social Learner", "description": "Join 10 study groups", "category": "groups", "icon": "📚", "criteria": {"groups_joined": 10}, "rarity": "uncommon", "points": 200},
    {"id": "group_leader", "name": "Group Leader", "description": "Create 5 study groups", "category": "groups", "icon": "👨‍🏫", "criteria": {"groups_created": 5}, "rarity": "rare", "points": 500},
    {"id": "super_connector", "name": "Super Connector", "description": "Join 25 study groups", "category": "groups", "icon": "🌐", "criteria": {"groups_joined": 25}, "rarity": "epic", "points": 1000},
    
    # Special Achievements (5)
    {"id": "early_bird", "name": "Early Bird", "description": "Upload before 8 AM", "category": "special", "icon": "🌅", "criteria": {"early_upload": 1}, "rarity": "common", "points": 50},
    {"id": "night_owl", "name": "Night Owl", "description": "Upload after 11 PM", "category": "special", "icon": "🦉", "criteria": {"late_upload": 1}, "rarity": "common", "points": 50},
    {"id": "weekend_warrior", "name": "Weekend Warrior", "description": "Upload 5 notes on weekends", "category": "special", "icon": "🎉", "criteria": {"weekend_uploads": 5}, "rarity": "uncommon", "points": 100},
    {"id": "diversity_champion", "name": "Diversity Champion", "description": "Upload notes from 5 different subjects", "category": "special", "icon": "🌈", "criteria": {"diverse_subjects": 5}, "rarity": "rare", "points": 300},
    {"id": "feedback_hero", "name": "Feedback Hero", "description": "Submit 10 feedback reports", "category": "special", "icon": "💬", "criteria": {"feedback_count": 10}, "rarity": "uncommon", "points": 200},
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



@router.get("/recent-unlock")
async def get_recent_achievement_unlock(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Check if user has unlocked achievement that hasn't been shown yet"""
    from datetime import timedelta
    
    recent = await db.user_achievements.find_one({
        "user_id": user_id,
        "celebration_shown": {"$ne": True},
        "unlocked_at": {"$gte": datetime.utcnow() - timedelta(minutes=5)}
    })
    
    if not recent:
        return {"achievement": None, "shown": True}
    
    # Find achievement details
    achievement = None
    for ach in ACHIEVEMENTS:
        if ach["id"] == recent["achievement_id"]:
            achievement = ach
            break
    
    if not achievement:
        return {"achievement": None, "shown": True}
    
    return {
        "achievement": {
            "id": achievement["id"],
            "name": achievement["name"],
            "description": achievement["description"],
            "icon": achievement["icon"],
            "rarity": achievement["rarity"],
            "points": achievement["points"]
        },
        "shown": False
    }


@router.post("/{achievement_id}/mark-shown")
async def mark_achievement_shown(
    achievement_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Mark achievement celebration as shown"""
    
    await db.user_achievements.update_one(
        {
            "user_id": user_id,
            "achievement_id": achievement_id
        },
        {"$set": {"celebration_shown": True}}
    )
    
    return {"success": True}


@router.post("/share-bonus")
async def award_share_bonus(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Award bonus points for sharing achievement"""
    
    bonus_points = 50
    
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"total_points": bonus_points}}
    )
    
    # Log the bonus
    await db.point_history.insert_one({
        "user_id": user_id,
        "points": bonus_points,
        "action": "achievement_share",
        "created_at": datetime.utcnow()
    })
    
    return {"success": True, "bonus_points": bonus_points}
