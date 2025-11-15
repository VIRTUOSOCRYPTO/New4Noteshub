"""
Surprise Rewards Router
Lucky draws, mystery boxes, random rewards, milestone celebrations
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import random

from auth import get_current_user_id
from database import get_database


router = APIRouter(prefix="/api/rewards", tags=["rewards"])


# Reward pools
REWARD_TIERS = {
    "common": [
        {"type": "points", "amount": 50, "name": "50 Points", "weight": 40},
        {"type": "points", "amount": 100, "name": "100 Points", "weight": 30},
        {"type": "downloads", "amount": 5, "name": "5 Free Downloads", "weight": 20},
        {"type": "streak_freeze", "amount": 1, "name": "1-Day Streak Freeze", "weight": 10},
    ],
    "rare": [
        {"type": "points", "amount": 500, "name": "500 Points", "weight": 30},
        {"type": "downloads", "amount": 20, "name": "20 Free Downloads", "weight": 25},
        {"type": "premium_trial", "amount": 3, "name": "3-Day Premium Trial", "weight": 25},
        {"type": "multiplier", "amount": 2, "name": "2x Points (24h)", "weight": 20},
    ],
    "legendary": [
        {"type": "points", "amount": 2000, "name": "2000 Points", "weight": 30},
        {"type": "premium_trial", "amount": 30, "name": "30-Day Premium", "weight": 25},
        {"type": "unlimited_downloads", "amount": 7, "name": "Unlimited Downloads (7 days)", "weight": 25},
        {"type": "level_boost", "amount": 1, "name": "Instant Level Up", "weight": 20},
    ]
}


def weighted_random_choice(items):
    """Choose item based on weight"""
    weights = [item["weight"] for item in items]
    return random.choices(items, weights=weights)[0]


@router.get("/mystery-box")
async def get_mystery_box_info(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get mystery box availability"""
    
    # Check last opened
    last_opened = await db.mystery_boxes.find_one(
        {"user_id": user_id},
        sort=[("opened_at", -1)]
    )
    
    now = datetime.utcnow()
    
    # Can open once per day
    if last_opened:
        next_available = last_opened["opened_at"] + timedelta(days=1)
        can_open = now >= next_available
        time_until = (next_available - now).total_seconds() if not can_open else 0
    else:
        can_open = True
        time_until = 0
        next_available = now
    
    # Get total boxes opened
    total_opened = await db.mystery_boxes.count_documents({"user_id": user_id})
    
    return {
        "can_open": can_open,
        "next_available_at": next_available.isoformat() if not can_open else now.isoformat(),
        "time_until_seconds": int(time_until),
        "total_opened": total_opened,
        "cost_points": 0  # Free once per day
    }


@router.post("/mystery-box/open")
async def open_mystery_box(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Open a mystery box and get random reward"""
    
    # Check if can open
    last_opened = await db.mystery_boxes.find_one(
        {"user_id": user_id},
        sort=[("opened_at", -1)]
    )
    
    now = datetime.utcnow()
    
    if last_opened:
        next_available = last_opened["opened_at"] + timedelta(days=1)
        if now < next_available:
            raise HTTPException(status_code=400, detail="Mystery box not available yet")
    
    # Determine tier (weighted random)
    tier_weights = {"common": 70, "rare": 25, "legendary": 5}
    tier = random.choices(
        list(tier_weights.keys()),
        weights=list(tier_weights.values())
    )[0]
    
    # Select reward from tier
    reward = weighted_random_choice(REWARD_TIERS[tier])
    
    # Apply reward
    user = await db.users.find_one({"id": user_id})
    reward_message = ""
    
    if reward["type"] == "points":
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"points": reward["amount"]}}
        )
        reward_message = f"You got {reward['amount']} points!"
    
    elif reward["type"] == "downloads":
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"free_downloads": reward["amount"]}}
        )
        reward_message = f"You got {reward['amount']} free downloads!"
    
    elif reward["type"] == "premium_trial":
        premium_until = now + timedelta(days=reward["amount"])
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"premium_until": premium_until, "premium": True}}
        )
        reward_message = f"You got {reward['amount']}-day premium trial!"
    
    elif reward["type"] == "multiplier":
        multiplier_until = now + timedelta(hours=24)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"points_multiplier": reward["amount"], "multiplier_until": multiplier_until}}
        )
        reward_message = f"{reward['amount']}x points for 24 hours!"
    
    elif reward["type"] == "unlimited_downloads":
        unlimited_until = now + timedelta(days=reward["amount"])
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"unlimited_downloads": True, "unlimited_until": unlimited_until}}
        )
        reward_message = f"Unlimited downloads for {reward['amount']} days!"
    
    elif reward["type"] == "level_boost":
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"level": 1}}
        )
        reward_message = "Instant level up!"
    
    # Record opening
    await db.mystery_boxes.insert_one({
        "user_id": user_id,
        "tier": tier,
        "reward_type": reward["type"],
        "reward_amount": reward["amount"],
        "reward_name": reward["name"],
        "opened_at": now
    })
    
    return {
        "tier": tier,
        "reward": reward,
        "message": f"🎁 {tier.upper()} REWARD! {reward_message}"
    }


@router.get("/lucky-draw")
async def get_lucky_draw_status(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get lucky draw information"""
    
    now = datetime.utcnow()
    
    # Check user's tickets
    user = await db.users.find_one({"id": user_id})
    tickets = user.get("lucky_draw_tickets", 0)
    
    # Get current draw info
    current_draw = await db.lucky_draws.find_one(
        {"status": "active"},
        sort=[("draw_date", -1)]
    )
    
    if not current_draw:
        # Create weekly draw
        draw_date = now + timedelta(days=(6 - now.weekday()))  # Next Sunday
        draw_id = str(uuid.uuid4())
        current_draw = {
            "id": draw_id,
            "draw_date": draw_date,
            "prizes": [
                {"rank": 1, "prize": "5000 Points + 30-Day Premium", "winner_id": None},
                {"rank": 2, "prize": "2000 Points + 7-Day Premium", "winner_id": None},
                {"rank": 3, "prize": "1000 Points", "winner_id": None},
            ],
            "total_tickets": 0,
            "status": "active",
            "created_at": now
        }
        await db.lucky_draws.insert_one(current_draw)
    
    # Get user's entries
    user_entries = await db.lucky_draw_entries.count_documents({
        "draw_id": current_draw["id"],
        "user_id": user_id
    })
    
    return {
        "draw_id": current_draw["id"],
        "draw_date": current_draw["draw_date"].isoformat(),
        "prizes": current_draw["prizes"],
        "user_tickets": tickets,
        "user_entries": user_entries,
        "total_entries": current_draw.get("total_tickets", 0)
    }


@router.post("/lucky-draw/enter")
async def enter_lucky_draw(
    tickets: int = 1,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Enter the lucky draw with tickets"""
    
    user = await db.users.find_one({"id": user_id})
    available_tickets = user.get("lucky_draw_tickets", 0)
    
    if tickets > available_tickets:
        raise HTTPException(status_code=400, detail="Insufficient tickets")
    
    # Get current draw
    current_draw = await db.lucky_draws.find_one({"status": "active"})
    if not current_draw:
        raise HTTPException(status_code=404, detail="No active draw")
    
    # Create entries
    for _ in range(tickets):
        await db.lucky_draw_entries.insert_one({
            "draw_id": current_draw["id"],
            "user_id": user_id,
            "entry_number": current_draw.get("total_tickets", 0) + 1,
            "created_at": datetime.utcnow()
        })
    
    # Update user tickets
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"lucky_draw_tickets": -tickets}}
    )
    
    # Update draw total
    await db.lucky_draws.update_one(
        {"id": current_draw["id"]},
        {"$inc": {"total_tickets": tickets}}
    )
    
    return {
        "success": True,
        "tickets_used": tickets,
        "message": f"Entered {tickets} ticket(s) into the draw! 🎫"
    }


@router.get("/birthday-special")
async def check_birthday_special(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Check if user has birthday special available"""
    
    user = await db.users.find_one({"id": user_id})
    if not user or not user.get("birthday"):
        return {"available": False}
    
    today = datetime.utcnow().date()
    birthday = user["birthday"].date() if isinstance(user["birthday"], datetime) else user["birthday"]
    
    is_birthday = (today.month == birthday.month and today.day == birthday.day)
    
    if is_birthday:
        # Check if already claimed this year
        claimed = await db.birthday_rewards.find_one({
            "user_id": user_id,
            "year": today.year
        })
        
        return {
            "available": not bool(claimed),
            "is_birthday": True,
            "rewards": {
                "points": 1000,
                "premium_days": 7,
                "special_badge": "Birthday Star 🎂"
            }
        }
    
    return {"available": False, "is_birthday": False}


@router.post("/birthday-special/claim")
async def claim_birthday_special(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Claim birthday special rewards"""
    
    user = await db.users.find_one({"id": user_id})
    if not user or not user.get("birthday"):
        raise HTTPException(status_code=400, detail="Birthday not set")
    
    today = datetime.utcnow().date()
    birthday = user["birthday"].date() if isinstance(user["birthday"], datetime) else user["birthday"]
    
    if not (today.month == birthday.month and today.day == birthday.day):
        raise HTTPException(status_code=400, detail="Not your birthday")
    
    # Check if already claimed
    claimed = await db.birthday_rewards.find_one({
        "user_id": user_id,
        "year": today.year
    })
    
    if claimed:
        raise HTTPException(status_code=400, detail="Already claimed this year")
    
    # Grant rewards
    premium_until = datetime.utcnow() + timedelta(days=7)
    await db.users.update_one(
        {"id": user_id},
        {
            "$inc": {"points": 1000},
            "$set": {"premium_until": premium_until, "premium": True}
        }
    )
    
    # Record claim
    await db.birthday_rewards.insert_one({
        "user_id": user_id,
        "year": today.year,
        "claimed_at": datetime.utcnow()
    })
    
    return {
        "success": True,
        "message": "🎉 Happy Birthday! You got 1000 points + 7-day premium!"
    }


@router.get("/milestone-rewards")
async def check_milestone_rewards(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Check for unclaimed milestone rewards"""
    
    user = await db.users.find_one({"id": user_id})
    
    milestones = [
        {"type": "uploads", "threshold": 10, "reward_points": 500, "name": "10 Uploads"},
        {"type": "uploads", "threshold": 50, "reward_points": 2000, "name": "50 Uploads"},
        {"type": "uploads", "threshold": 100, "reward_points": 5000, "name": "100 Uploads"},
        {"type": "downloads_given", "threshold": 100, "reward_points": 1000, "name": "100 Downloads Given"},
        {"type": "downloads_given", "threshold": 500, "reward_points": 3000, "name": "500 Downloads Given"},
        {"type": "followers", "threshold": 50, "reward_points": 1500, "name": "50 Followers"},
        {"type": "level", "threshold": 20, "reward_points": 2500, "name": "Level 20"},
    ]
    
    unclaimed = []
    
    for milestone in milestones:
        user_value = user.get(milestone["type"], 0)
        
        if user_value >= milestone["threshold"]:
            # Check if already claimed
            claimed = await db.milestone_rewards.find_one({
                "user_id": user_id,
                "milestone_type": milestone["type"],
                "threshold": milestone["threshold"]
            })
            
            if not claimed:
                unclaimed.append(milestone)
    
    return {"unclaimed_milestones": unclaimed, "count": len(unclaimed)}


@router.post("/milestone-rewards/claim")
async def claim_milestone_reward(
    milestone_type: str,
    threshold: int,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Claim a milestone reward"""
    
    user = await db.users.find_one({"id": user_id})
    user_value = user.get(milestone_type, 0)
    
    if user_value < threshold:
        raise HTTPException(status_code=400, detail="Milestone not reached")
    
    # Check if already claimed
    claimed = await db.milestone_rewards.find_one({
        "user_id": user_id,
        "milestone_type": milestone_type,
        "threshold": threshold
    })
    
    if claimed:
        raise HTTPException(status_code=400, detail="Already claimed")
    
    # Determine reward
    milestone_rewards = {
        ("uploads", 10): 500,
        ("uploads", 50): 2000,
        ("uploads", 100): 5000,
        ("downloads_given", 100): 1000,
        ("downloads_given", 500): 3000,
        ("followers", 50): 1500,
        ("level", 20): 2500,
    }
    
    reward_points = milestone_rewards.get((milestone_type, threshold), 0)
    
    # Grant reward
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"points": reward_points}}
    )
    
    # Record claim
    await db.milestone_rewards.insert_one({
        "user_id": user_id,
        "milestone_type": milestone_type,
        "threshold": threshold,
        "reward_points": reward_points,
        "claimed_at": datetime.utcnow()
    })
    
    return {
        "success": True,
        "message": f"🎉 Milestone reached! +{reward_points} points!",
        "points_awarded": reward_points
    }
