"""
Referrals Router - Viral Growth Through Friend Invitations
Instant rewards system for maximum viral spread
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime, timedelta
import random
import string

from auth import get_current_user_id
from models import UserInDB, ReferralResponse, ReferralReward
from database import get_database
from routers.gamification import update_user_points


router = APIRouter(prefix="/api/referrals", tags=["referrals"])


def generate_referral_code(usn: str) -> str:
    """Generate a unique referral code based on USN"""
    # Take last 4 chars of USN + 3 random chars
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    code = f"{usn[-4:]}{random_chars}".upper()
    return code


@router.get("/my-referral", response_model=ReferralResponse)
async def get_my_referral_data(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get current user's referral information"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create referral record
    referral = await db.referrals.find_one({"user_id": user_id})
    
    if not referral:
        # Generate referral code
        referral_code = generate_referral_code(user.get("usn", "USER"))
        
        # Ensure uniqueness
        existing = await db.referrals.find_one({"referral_code": referral_code})
        while existing:
            referral_code = generate_referral_code(current_user.usn)
            existing = await db.referrals.find_one({"referral_code": referral_code})
        
        # Create referral record
        referral = {
            "user_id": user_id,
            "referral_code": referral_code,
            "referred_users": [],
            "total_referrals": 0,
            "rewards_earned": {
                "bonus_downloads": 0,
                "ai_access_days": 0,
                "premium_days": 0
            },
            "created_at": datetime.utcnow()
        }
        
        await db.referrals.insert_one(referral)
    
    # Generate referral link (you can customize the base URL)
    base_url = "https://noteshub.app"  # Change to your actual domain
    referral_link = f"{base_url}?ref={referral['referral_code']}"
    
    return ReferralResponse(
        referral_code=referral["referral_code"],
        total_referrals=referral.get("total_referrals", 0),
        rewards_earned=referral.get("rewards_earned", {}),
        referral_link=referral_link
    )


@router.post("/apply-code/{referral_code}")
async def apply_referral_code(
    referral_code: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Apply a referral code when signing up"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user already used a referral code
    user_referral = await db.referrals.find_one({"user_id": user_id})
    if user_referral and user_referral.get("referred_by"):
        raise HTTPException(
            status_code=400,
            detail="You have already used a referral code"
        )
    
    # Find the referrer
    referrer_data = await db.referrals.find_one({"referral_code": referral_code.upper()})
    if not referrer_data:
        raise HTTPException(
            status_code=404,
            detail="Invalid referral code"
        )
    
    referrer_id = referrer_data["user_id"]
    
    # Can't refer yourself
    if referrer_id == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot use your own referral code"
        )
    
    # Update referrer's data - give instant rewards
    await db.referrals.update_one(
        {"user_id": referrer_id},
        {
            "$inc": {
                "total_referrals": 1,
                "rewards_earned.bonus_downloads": 10
            },
            "$push": {
                "referred_users": {
                    "user_id": user_id,
                    "usn": user.get("usn"),
                    "joined_at": datetime.utcnow()
                }
            }
        }
    )
    
    # Award points to referrer
    await update_user_points(db, referrer_id, "referral_signup", 50)
    
    # Update current user's referral record
    if not user_referral:
        referral_code_new = generate_referral_code(user.get("usn", "USER"))
        await db.referrals.insert_one({
            "user_id": user_id,
            "referral_code": referral_code_new,
            "referred_by": referral_code.upper(),
            "referred_users": [],
            "total_referrals": 0,
            "rewards_earned": {
                "bonus_downloads": 20  # New user gets 20 downloads vs 5 normally
            },
            "created_at": datetime.utcnow()
        })
    else:
        await db.referrals.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "referred_by": referral_code.upper()
                },
                "$inc": {
                    "rewards_earned.bonus_downloads": 20
                }
            }
        )
    
    return {
        "success": True,
        "message": "Referral code applied! You got 20 bonus downloads! 🎉",
        "bonus_downloads": 20
    }


@router.get("/referred-users")
async def get_referred_users(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get list of users referred by current user"""
    
    referral = await db.referrals.find_one({"user_id": user_id})
    
    if not referral or not referral.get("referred_users"):
        return {"referred_users": []}
    
    return {"referred_users": referral["referred_users"]}


@router.post("/reward-for-upload")
async def reward_referrer_for_upload(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Give referrer extra reward when referred user uploads their first note"""
    
    # Check if this is user's first upload
    upload_count = await db.notes.count_documents({"user_id": user_id})
    
    if upload_count != 1:
        return {
            "success": False,
            "message": "Reward only for first upload"
        }
    
    # Find who referred this user
    user_referral = await db.referrals.find_one({"user_id": user_id})
    
    if not user_referral or not user_referral.get("referred_by"):
        return {
            "success": False,
            "message": "User was not referred"
        }
    
    # Find referrer
    referrer_data = await db.referrals.find_one({"referral_code": user_referral["referred_by"]})
    
    if not referrer_data:
        return {
            "success": False,
            "message": "Referrer not found"
        }
    
    referrer_id = referrer_data["user_id"]
    
    # Give bonus to referrer
    await db.referrals.update_one(
        {"user_id": referrer_id},
        {
            "$inc": {
                "rewards_earned.bonus_downloads": 5
            }
        }
    )
    
    # Award points
    await update_user_points(db, referrer_id, "referral_upload", 25)
    
    return {
        "success": True,
        "message": "Referrer rewarded for your first upload!"
    }


@router.get("/stats")
async def get_referral_stats(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get detailed referral statistics"""
    
    referral = await db.referrals.find_one({"user_id": user_id})
    
    if not referral:
        return {
            "total_referrals": 0,
            "rewards_earned": {},
            "milestones": {
                "next_milestone": 3,
                "reward": "Unlock AI assistant (1 month)"
            }
        }
    
    total_referrals = referral.get("total_referrals", 0)
    
    # Define milestones
    milestones = {
        3: {"reward": "Unlock AI assistant (1 month)", "bonus_downloads": 15},
        10: {"reward": "Lifetime premium access", "bonus_downloads": 50},
        50: {"reward": "Cash payout ₹500", "bonus_downloads": 100}
    }
    
    # Find next milestone
    next_milestone = None
    for count, reward in sorted(milestones.items()):
        if total_referrals < count:
            next_milestone = {
                "count": count,
                "reward": reward["reward"],
                "progress": total_referrals,
                "needed": count - total_referrals
            }
            break
    
    return {
        "total_referrals": total_referrals,
        "rewards_earned": referral.get("rewards_earned", {}),
        "next_milestone": next_milestone,
        "all_milestones": milestones
    }


@router.get("/leaderboard")
async def get_referral_leaderboard(
    limit: int = 20,
    db = Depends(get_database)
):
    """Get top referrers leaderboard"""
    
    # Get top referrers
    pipeline = [
        {"$sort": {"total_referrals": -1}},
        {"$limit": limit}
    ]
    
    top_referrers = await db.referrals.aggregate(pipeline).to_list(None)
    
    # Enrich with user data
    result = []
    for idx, item in enumerate(top_referrers, 1):
        user = await db.users.find_one({"_id": item["user_id"]})
        if user:
            result.append({
                "rank": idx,
                "usn": user.get("usn"),
                "department": user.get("department"),
                "total_referrals": item.get("total_referrals", 0),
                "profile_picture": user.get("profile_picture")
            })
    
    return {
        "top_referrers": result
    }
