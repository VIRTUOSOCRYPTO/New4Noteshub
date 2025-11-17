"""
FOMO Triggers Router
Limited offers, scarcity, urgency, social proof mechanics
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import random

from auth import get_current_user_id
from database import get_database


router = APIRouter(prefix="/api/fomo", tags=["fomo"])


@router.get("/triggers")
async def get_fomo_triggers(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get active FOMO triggers for user"""
    
    triggers = []
    now = datetime.utcnow()
    
    # 1. Limited Time Offers
    # Check if user eligible for flash premium trial
    user = await db.users.find_one({"id": user_id})
    if user and user.get("points", 0) >= 500 and not user.get("premium"):
        triggers.append({
            "type": "limited_offer",
            "title": "⚡ Flash Sale: Premium Trial",
            "message": "Only 3 hours left! Get 7 days of premium for 500 points",
            "urgency_level": "high",
            "expires_at": (now + timedelta(hours=3)).isoformat(),
            "action_url": "/premium/trial",
            "action_text": "Claim Now"
        })
    
    # 2. Scarcity Mechanics
    # Limited spots in exclusive group
    exclusive_groups = await db.study_groups.find({
        "is_exclusive": True,
        "member_count": {"$lt": "$max_members"}
    }).to_list(5)
    
    for group in exclusive_groups:
        spots_left = group.get("max_members", 50) - group.get("member_count", 0)
        if spots_left <= 10 and spots_left > 0:
            triggers.append({
                "type": "scarcity",
                "title": f"🔥 Only {spots_left} Spots Left!",
                "message": f"Join '{group['name']}' before it's full",
                "urgency_level": "medium",
                "data": {"group_id": group["id"]},
                "action_url": f"/groups/{group['id']}",
                "action_text": "Join Now"
            })
    
    # 3. Social Proof
    # Students active right now
    active_count = await db.users.count_documents({
        "last_active": {"$gte": now - timedelta(minutes=5)}
    })
    
    triggers.append({
        "type": "social_proof",
        "title": f"👥 {active_count} students online now!",
        "message": "Don't miss out - join the action",
        "urgency_level": "low",
        "data": {"active_count": active_count}
    })
    
    # 4. Trending Activity
    # Get trending notes in last hour
    trending_notes = await db.notes.find({
        "created_at": {"$gte": now - timedelta(hours=1)}
    }).sort("download_count", -1).limit(1).to_list(1)
    
    if trending_notes:
        note = trending_notes[0]
        triggers.append({
            "type": "trending",
            "title": "🔥 Trending Now",
            "message": f"'{note['title']}' - Downloaded by {note.get('download_count', 0)} students in last hour!",
            "urgency_level": "medium",
            "data": {"note_id": note["id"]},
            "action_url": f"/notes/{note['id']}",
            "action_text": "View Note"
        })
    
    # 5. Deadline Approaching
    # Get user's upcoming challenges ending soon
    user_challenges = await db.challenge_progress.find({
        "user_id": user_id,
        "date": datetime.utcnow().date().isoformat()
    }).to_list(None)
    
    incomplete_challenges = [c for c in user_challenges if c.get("progress", 0) < c.get("target", 100)]
    if incomplete_challenges:
        triggers.append({
            "type": "deadline",
            "title": "⏰ Daily Challenges Ending Soon!",
            "message": f"{len(incomplete_challenges)} challenges incomplete - Complete before midnight",
            "urgency_level": "high",
            "expires_at": now.replace(hour=23, minute=59, second=59).isoformat(),
            "action_url": "/challenges",
            "action_text": "View Challenges"
        })
    
    # 6. Exclusive Access
    # Check if user qualifies for early access
    if user and user.get("level", 0) >= 10:
        triggers.append({
            "type": "exclusive",
            "title": "🌟 VIP Early Access",
            "message": "You've unlocked early access to new AI features!",
            "urgency_level": "low",
            "action_url": "/ai-features",
            "action_text": "Explore Now"
        })
    
    return {"triggers": triggers, "count": len(triggers)}


@router.get("/live-stats")
async def get_live_stats(
    db = Depends(get_database)
):
    """Get live platform statistics for social proof"""
    
    now = datetime.utcnow()
    
    # Active users (last 5 minutes)
    active_users = await db.users.count_documents({
        "last_active": {"$gte": now - timedelta(minutes=5)}
    })
    
    # Notes uploaded today
    notes_today = await db.notes.count_documents({
        "created_at": {"$gte": datetime(now.year, now.month, now.day)}
    })
    
    # Downloads in last hour
    recent_downloads = await db.download_history.count_documents({
        "downloaded_at": {"$gte": now - timedelta(hours=1)}
    })
    
    # Study sessions active
    active_sessions = await db.study_sessions.count_documents({
        "status": "active",
        "updated_at": {"$gte": now - timedelta(minutes=30)}
    })
    
    return {
        "active_users_now": active_users,
        "notes_uploaded_today": notes_today,
        "downloads_last_hour": recent_downloads,
        "active_study_sessions": active_sessions,
        "timestamp": now.isoformat()
    }


@router.get("/limited-offers")
async def get_limited_offers(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get time-limited offers available to user"""
    
    offers = []
    now = datetime.utcnow()
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        return {"offers": []}
    
    # Offer 1: Double points weekend
    if now.weekday() >= 5:  # Saturday or Sunday
        offers.append({
            "id": "double-points-weekend",
            "title": "🎉 Weekend Bonus: 2x Points!",
            "description": "All uploads give double points this weekend",
            "type": "multiplier",
            "expires_at": (now + timedelta(days=(7 - now.weekday()))).replace(hour=23, minute=59).isoformat(),
            "active": True
        })
    
    # Offer 2: Streak recovery
    if user.get("streak", 0) == 0 and user.get("longest_streak", 0) > 7:
        offers.append({
            "id": "streak-recovery",
            "title": "🔥 Recover Your Streak!",
            "description": "Use 100 points to restore your streak",
            "type": "streak_recovery",
            "cost_points": 100,
            "expires_at": (now + timedelta(hours=24)).isoformat(),
            "active": user.get("points", 0) >= 100
        })
    
    # Offer 3: Bulk download bonus
    if user.get("download_count", 0) > 50:
        offers.append({
            "id": "power-user-bonus",
            "title": "⚡ Power User: Unlimited Downloads",
            "description": "Get unlimited downloads for 7 days - 500 points",
            "type": "unlimited_access",
            "cost_points": 500,
            "duration_days": 7,
            "expires_at": (now + timedelta(hours=48)).isoformat(),
            "active": user.get("points", 0) >= 500
        })
    
    return {"offers": offers, "count": len(offers)}


@router.post("/claim-offer/{offer_id}")
async def claim_limited_offer(
    offer_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Claim a limited-time offer"""
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already claimed
    existing_claim = await db.claimed_offers.find_one({
        "user_id": user_id,
        "offer_id": offer_id
    })
    if existing_claim:
        raise HTTPException(status_code=400, detail="Offer already claimed")
    
    # Process offer based on type
    if offer_id == "streak-recovery":
        if user.get("points", 0) < 100:
            raise HTTPException(status_code=400, detail="Insufficient points")
        
        # Restore streak
        await db.users.update_one(
            {"id": user_id},
            {
                "$inc": {"points": -100},
                "$set": {"streak": user.get("longest_streak", 0)}
            }
        )
        
        message = f"Streak restored to {user.get('longest_streak', 0)} days! 🔥"
    
    elif offer_id == "power-user-bonus":
        if user.get("points", 0) < 500:
            raise HTTPException(status_code=400, detail="Insufficient points")
        
        # Grant unlimited downloads
        await db.users.update_one(
            {"id": user_id},
            {
                "$inc": {"points": -500},
                "$set": {
                    "unlimited_downloads": True,
                    "unlimited_until": datetime.utcnow() + timedelta(days=7)
                }
            }
        )
        
        message = "Unlimited downloads activated for 7 days! 🚀"
    
    else:
        raise HTTPException(status_code=400, detail="Invalid offer")
    
    # Record claim
    await db.claimed_offers.insert_one({
        "user_id": user_id,
        "offer_id": offer_id,
        "claimed_at": datetime.utcnow()
    })
    
    return {
        "success": True,
        "message": message
    }


@router.get("/countdown/{event_type}")
async def get_countdown(
    event_type: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get countdown for specific event type"""
    
    now = datetime.utcnow()
    
    countdowns = {
        "daily_reset": {
            "title": "Daily Challenges Reset",
            "target_time": now.replace(hour=23, minute=59, second=59),
            "message": "Complete your challenges before they reset!"
        },
        "weekend_bonus": {
            "title": "Weekend 2x Points",
            "target_time": now + timedelta(days=(5 - now.weekday()) if now.weekday() < 5 else 0),
            "message": "Weekend bonus coming soon!"
        },
        "monthly_contest": {
            "title": "Monthly Contest Ends",
            "target_time": (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
            "message": "Submit your entry before month ends!"
        }
    }
    
    countdown = countdowns.get(event_type)
    if not countdown:
        raise HTTPException(status_code=404, detail="Event type not found")
    
    time_remaining = countdown["target_time"] - now
    
    return {
        **countdown,
        "seconds_remaining": int(time_remaining.total_seconds()),
        "days": time_remaining.days,
        "hours": time_remaining.seconds // 3600,
        "minutes": (time_remaining.seconds % 3600) // 60
    }



@router.get("/live-activity-feed")
async def get_live_activity_feed(db = Depends(get_database)):
    """Get live activity feed for floating ticker"""
    
    # Recent uploads (last 30 minutes)
    recent_uploads = await db.notes.find(
        {"created_at": {"$gte": datetime.utcnow() - timedelta(minutes=30)}}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    # Recent achievements
    recent_achievements = await db.user_achievements.find(
        {"unlocked_at": {"$gte": datetime.utcnow() - timedelta(minutes=30)}}
    ).sort("unlocked_at", -1).limit(5).to_list(5)
    
    # Recent referrals
    recent_referrals = await db.referrals.find(
        {"created_at": {"$gte": datetime.utcnow() - timedelta(minutes=30)}}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    activities = []
    
    # Process uploads
    for upload in recent_uploads:
        user = await db.users.find_one({"id": upload.get("user_id")})
        if user:
            activities.append({
                "type": "upload",
                "message": f"{user.get('usn', 'User')[:4]}*** uploaded {upload.get('subject', 'notes')}",
                "icon": "📚",
                "timestamp": upload.get("created_at", datetime.utcnow()).isoformat()
            })
    
    # Process achievements
    for achievement in recent_achievements:
        user = await db.users.find_one({"id": achievement.get("user_id")})
        if user:
            # Find achievement name
            from routers.achievements import ACHIEVEMENTS
            ach_data = None
            for ach in ACHIEVEMENTS:
                if ach["id"] == achievement.get("achievement_id"):
                    ach_data = ach
                    break
            
            if ach_data:
                activities.append({
                    "type": "achievement",
                    "message": f"{user.get('usn', 'User')[:4]}*** unlocked {ach_data['name']}",
                    "icon": ach_data["icon"],
                    "timestamp": achievement.get("unlocked_at", datetime.utcnow()).isoformat()
                })
    
    # Process referrals
    for referral in recent_referrals:
        user = await db.users.find_one({"id": referral.get("user_id")})
        if user:
            activities.append({
                "type": "referral",
                "message": f"{user.get('usn', 'User')[:4]}*** referred a new student",
                "icon": "🎯",
                "timestamp": referral.get("created_at", datetime.utcnow()).isoformat()
            })
    
    # Sort by timestamp and return latest 10
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {"activities": activities[:10]}
