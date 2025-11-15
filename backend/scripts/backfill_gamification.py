#!/usr/bin/env python3
"""
Backfill Script - Initialize Gamification Data for Existing Users
This script adds gamification data (points, streaks, referrals) for users who don't have it yet
"""

import asyncio
import sys
import os
from datetime import datetime
import random
import string

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


def generate_referral_code(usn: str) -> str:
    """Generate a unique referral code based on USN"""
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    code = f"{usn[-4:]}{random_chars}".upper()
    return code


async def backfill_user_gamification(user):
    """Initialize gamification data for a single user"""
    user_id = user.get("id")
    usn = user.get("usn", "USER")
    
    if not user_id:
        print(f"⚠️  Skipping user with no ID: {usn}")
        return False
    
    # Check if user already has gamification data
    has_points = await db.db.user_points.find_one({"user_id": user_id})
    has_streaks = await db.db.streaks.find_one({"user_id": user_id})
    has_referrals = await db.db.referrals.find_one({"user_id": user_id})
    
    if has_points and has_streaks and has_referrals:
        print(f"✓ User {usn} already has all gamification data")
        return False
    
    print(f"📝 Initializing gamification for {usn} (ID: {user_id})...")
    
    # Initialize user_points if missing
    if not has_points:
        await db.db.user_points.insert_one({
            "user_id": user_id,
            "total_points": 0,
            "level": 1,
            "level_name": "Newbie",
            "points_history": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        print(f"  ✓ Created user_points")
    
    # Initialize streaks if missing
    if not has_streaks:
        await db.db.streaks.insert_one({
            "user_id": user_id,
            "current_streak": 0,
            "longest_streak": 0,
            "last_activity_date": None,
            "total_activities": 0,
            "created_at": datetime.utcnow()
        })
        print(f"  ✓ Created streaks")
    
    # Initialize referrals if missing
    if not has_referrals:
        # Generate unique referral code
        referral_code = generate_referral_code(usn)
        existing = await db.db.referrals.find_one({"referral_code": referral_code})
        
        while existing:
            referral_code = generate_referral_code(usn)
            existing = await db.db.referrals.find_one({"referral_code": referral_code})
        
        await db.db.referrals.insert_one({
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
        })
        print(f"  ✓ Created referrals (code: {referral_code})")
    
    return True


async def main():
    """Main backfill script"""
    print("=" * 60)
    print("NotesHub - Gamification Data Backfill Script")
    print("=" * 60)
    print()
    
    # Connect to database
    print("🔌 Connecting to database...")
    await db.connect_to_database()
    print("✓ Database connected")
    print()
    
    # Get all users
    print("👥 Fetching all users...")
    users = await db.db.users.find({}).to_list(None)
    print(f"✓ Found {len(users)} users")
    print()
    
    # Process each user
    updated_count = 0
    skipped_count = 0
    
    for user in users:
        was_updated = await backfill_user_gamification(user)
        if was_updated:
            updated_count += 1
        else:
            skipped_count += 1
    
    print()
    print("=" * 60)
    print("📊 Backfill Summary:")
    print(f"   Total users: {len(users)}")
    print(f"   Updated: {updated_count}")
    print(f"   Skipped (already had data): {skipped_count}")
    print("=" * 60)
    print()
    
    # Close database connection
    await db.close_database_connection()
    print("✓ Database connection closed")
    print("✅ Backfill complete!")


if __name__ == "__main__":
    asyncio.run(main())
