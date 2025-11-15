"""
Forced Virality Mechanics API
Ethical unlock mechanisms to drive viral growth
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Optional
from auth import get_current_user_id
from database import get_database

router = APIRouter(prefix="/api/virality", tags=["Forced Virality"])


@router.get("/locked-content/{note_id}")
async def check_content_lock(
    note_id: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Check if content is locked and unlock requirements"""
    
    note = await db.notes.find_one({"id": note_id})
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if note is premium/locked
    is_premium = note.get("is_premium", False)
    
    if not is_premium:
        return {
            "locked": False,
            "note_id": note_id,
            "access": "free"
        }
    
    # Check if user has unlocked this note
    unlock = await db.unlocked_content.find_one({
        "user_id": user_id,
        "note_id": note_id
    })
    
    if unlock:
        return {
            "locked": False,
            "note_id": note_id,
            "access": "unlocked",
            "unlocked_at": unlock.get("unlocked_at"),
            "unlock_method": unlock.get("method")
        }
    
    # Check user's level for auto-unlock
    user_points = await db.user_points.find_one({"user_id": user_id})
    user_level = user_points.get("level", 1) if user_points else 1
    
    if user_level >= 10:  # Level 10+ gets premium access
        return {
            "locked": False,
            "note_id": note_id,
            "access": "premium_member"
        }
    
    # Return unlock options
    return {
        "locked": True,
        "note_id": note_id,
        "unlock_options": [
            {
                "method": "share",
                "requirement": "Share to 3 platforms",
                "description": "Share this note on WhatsApp, Instagram, and one more platform",
                "points_reward": 50
            },
            {
                "method": "referral",
                "requirement": "Invite 1 friend",
                "description": "Invite a friend who signs up with your referral code",
                "points_reward": 100
            },
            {
                "method": "upload",
                "requirement": "Upload 2 notes",
                "description": "Contribute by uploading 2 quality notes",
                "points_reward": 200
            },
            {
                "method": "level",
                "requirement": "Reach Level 10",
                "description": "Get to Level 10 for unlimited premium access",
                "current_level": user_level
            }
        ]
    }


@router.post("/unlock/{note_id}")
async def unlock_content(
    note_id: str,
    method: str,
    proof: Optional[dict] = None,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Unlock premium content by completing viral action"""
    
    note = await db.notes.find_one({"id": note_id})
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if already unlocked
    existing_unlock = await db.unlocked_content.find_one({
        "user_id": user_id,
        "note_id": note_id
    })
    
    if existing_unlock:
        return {
            "success": True,
            "message": "Already unlocked",
            "unlocked_at": existing_unlock.get("unlocked_at")
        }
    
    # Verify unlock requirements based on method
    verified = False
    points_earned = 0
    
    if method == "share":
        # Check if user has shared to 3 platforms
        recent_shares = await db.share_actions.count_documents({
            "user_id": user_id,
            "note_id": note_id,
            "timestamp": {"$gte": datetime.now() - timedelta(hours=1)}
        })
        
        if recent_shares >= 3:
            verified = True
            points_earned = 50
        else:
            raise HTTPException(status_code=400, detail=f"Share to {3 - recent_shares} more platforms")
    
    elif method == "referral":
        # Check if user has made a successful referral
        referral = await db.referrals.find_one({"user_id": user_id})
        
        if referral and referral.get("total_referrals", 0) > 0:
            verified = True
            points_earned = 100
        else:
            raise HTTPException(status_code=400, detail="No successful referrals yet")
    
    elif method == "upload":
        # Check upload count
        uploads = await db.notes.count_documents({"uploaded_by": user_id})
        
        if uploads >= 2:
            verified = True
            points_earned = 200
        else:
            raise HTTPException(status_code=400, detail=f"Upload {2 - uploads} more notes")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid unlock method")
    
    # Unlock content
    if verified:
        await db.unlocked_content.insert_one({
            "user_id": user_id,
            "note_id": note_id,
            "method": method,
            "unlocked_at": datetime.now()
        })
        
        # Award points
        await db.user_points.update_one(
            {"user_id": user_id},
            {
                "$inc": {"total_points": points_earned},
                "$push": {
                    "points_history": {
                        "action": f"unlock_{method}",
                        "points": points_earned,
                        "timestamp": datetime.now()
                    }
                }
            }
        )
        
        return {
            "success": True,
            "message": f"Content unlocked via {method}!",
            "points_earned": points_earned,
            "unlocked_at": datetime.now().isoformat()
        }


@router.get("/ai-summary-lock/{note_id}")
async def check_ai_summary_lock(
    note_id: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Check if AI summary is locked for a note"""
    
    note = await db.notes.find_one({"id": note_id})
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if user has unlocked AI summary
    unlock = await db.feature_unlocks.find_one({
        "user_id": user_id,
        "feature": "ai_summary",
        "item_id": note_id
    })
    
    if unlock:
        return {
            "locked": False,
            "feature": "ai_summary",
            "access": "unlocked"
        }
    
    # Check user level
    user_points = await db.user_points.find_one({"user_id": user_id})
    user_level = user_points.get("level", 1) if user_points else 1
    
    if user_level >= 5:  # Level 5+ gets AI features
        return {
            "locked": False,
            "feature": "ai_summary",
            "access": "level_unlock"
        }
    
    return {
        "locked": True,
        "feature": "ai_summary",
        "unlock_options": [
            {
                "method": "tag_friends",
                "requirement": "Tag 2 friends",
                "description": "Share on social media and tag 2 friends to unlock AI summary"
            },
            {
                "method": "study_group",
                "requirement": "Join a study group",
                "description": "Join any study group to unlock AI features"
            },
            {
                "method": "level",
                "requirement": "Reach Level 5",
                "description": "Get to Level 5 for AI assistant access",
                "current_level": user_level
            }
        ]
    }


@router.post("/unlock-ai-summary/{note_id}")
async def unlock_ai_summary(
    note_id: str,
    method: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Unlock AI summary feature for a note"""
    
    verified = False
    
    if method == "tag_friends":
        # In real implementation, verify social media share with tags
        # For now, we'll accept user confirmation
        verified = True
    
    elif method == "study_group":
        # Check if user is in any study group
        group_membership = await db.study_group_members.find_one({
            "user_id": user_id
        })
        
        if group_membership:
            verified = True
        else:
            raise HTTPException(status_code=400, detail="Join a study group first")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid unlock method")
    
    if verified:
        await db.feature_unlocks.insert_one({
            "user_id": user_id,
            "feature": "ai_summary",
            "item_id": note_id,
            "method": method,
            "unlocked_at": datetime.now()
        })
        
        return {
            "success": True,
            "message": "AI summary unlocked!",
            "feature": "ai_summary"
        }


@router.get("/group-features-lock")
async def check_group_features_lock(
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Check if advanced group features are locked"""
    
    # Check referrals
    referral = await db.referrals.find_one({"user_id": user_id})
    referral_count = referral.get("total_referrals", 0) if referral else 0
    
    # Advanced features unlock at 3 referrals
    if referral_count >= 3:
        return {
            "locked": False,
            "features": ["private_groups", "group_voice_chat", "file_sharing"],
            "access": "unlocked"
        }
    
    return {
        "locked": True,
        "features": ["private_groups", "group_voice_chat", "file_sharing"],
        "unlock_requirement": {
            "method": "referrals",
            "needed": 3 - referral_count,
            "current": referral_count,
            "description": f"Invite {3 - referral_count} more friends to unlock advanced group features"
        }
    }


@router.post("/share-to-unlock")
async def track_share_for_unlock(
    note_id: str,
    platform: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Track a share action for unlock requirements"""
    
    # Record the share
    await db.share_actions.insert_one({
        "user_id": user_id,
        "note_id": note_id,
        "platform": platform,
        "timestamp": datetime.now()
    })
    
    # Count recent shares for this note
    shares_count = await db.share_actions.count_documents({
        "user_id": user_id,
        "note_id": note_id,
        "timestamp": {"$gte": datetime.now() - timedelta(hours=1)}
    })
    
    # Get unique platforms
    platforms = await db.share_actions.distinct("platform", {
        "user_id": user_id,
        "note_id": note_id,
        "timestamp": {"$gte": datetime.now() - timedelta(hours=1)}
    })
    
    platforms_count = len(platforms)
    
    # Check if unlock requirement met
    unlock_achieved = platforms_count >= 3
    
    return {
        "shares_recorded": shares_count,
        "unique_platforms": platforms_count,
        "platforms": platforms,
        "unlock_achieved": unlock_achieved,
        "remaining": max(0, 3 - platforms_count),
        "message": "Unlocked!" if unlock_achieved else f"Share to {3 - platforms_count} more platforms"
    }


@router.get("/my-unlocks")
async def get_my_unlocks(
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Get all content user has unlocked"""
    
    # Get unlocked notes
    unlocked_notes = await db.unlocked_content.find({
        "user_id": user_id
    }).to_list(100)
    
    # Get unlocked features
    unlocked_features = await db.feature_unlocks.find({
        "user_id": user_id
    }).to_list(100)
    
    return {
        "unlocked_notes": len(unlocked_notes),
        "unlocked_features": len(unlocked_features),
        "details": {
            "notes": unlocked_notes,
            "features": unlocked_features
        }
    }


@router.get("/stats")
async def get_virality_stats(
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Get user's virality statistics"""
    
    # Count shares
    total_shares = await db.share_actions.count_documents({
        "user_id": user_id
    })
    
    # Count unlocks
    unlocked_count = await db.unlocked_content.count_documents({
        "user_id": user_id
    })
    
    # Get referral count
    referral = await db.referrals.find_one({"user_id": user_id})
    referral_count = referral.get("total_referrals", 0) if referral else 0
    
    return {
        "total_shares": total_shares,
        "content_unlocked": unlocked_count,
        "friends_invited": referral_count,
        "viral_score": (total_shares * 2) + (unlocked_count * 10) + (referral_count * 20)
    }
