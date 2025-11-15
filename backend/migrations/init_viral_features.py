"""
Migration Script: Initialize Viral Growth Features for Existing Users
- Generate referral codes
- Initialize streaks
- Calculate initial points based on existing activity
- Initialize leaderboards
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import random
import string
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def generate_referral_code(usn: str) -> str:
    """Generate a unique referral code"""
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    code = f"{usn[-4:]}{random_chars}".upper()
    return code


async def migrate():
    """Run migration"""
    
    # Connect to MongoDB
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/noteshub")
    client = AsyncIOMotorClient(mongo_url)
    
    # Get database name
    if "/" in mongo_url:
        db_name = mongo_url.split("/")[-1].split("?")[0]
    else:
        db_name = "noteshub"
    
    db = client[db_name]
    
    print("🚀 Starting viral features migration...")
    print(f"📊 Connected to database: {db_name}")
    
    # Get all users
    users = await db.users.find({}).to_list(None)
    total_users = len(users)
    
    print(f"👥 Found {total_users} users to migrate")
    
    migrated_count = 0
    
    for user in users:
        user_id = str(user["_id"])
        usn = user.get("usn", "")
        
        # 1. Create referral code
        existing_referral = await db.referrals.find_one({"user_id": user_id})
        if not existing_referral:
            referral_code = generate_referral_code(usn)
            
            # Ensure uniqueness
            while await db.referrals.find_one({"referral_code": referral_code}):
                referral_code = generate_referral_code(usn)
            
            await db.referrals.insert_one({
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
            print(f"  ✅ Created referral code for {usn}: {referral_code}")
        
        # 2. Initialize streak (starting from 0)
        existing_streak = await db.streaks.find_one({"user_id": user_id})
        if not existing_streak:
            await db.streaks.insert_one({
                "user_id": user_id,
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None,
                "total_activities": 0,
                "created_at": datetime.utcnow()
            })
            print(f"  ✅ Initialized streak for {usn}")
        
        # 3. Calculate initial points based on existing activity
        existing_points = await db.user_points.find_one({"user_id": user_id})
        if not existing_points:
            # Count uploads
            upload_count = await db.notes.count_documents({
                "user_id": user_id,
                "is_approved": True
            })
            
            # Count total downloads of user's notes
            user_notes = await db.notes.find({"user_id": user_id}).to_list(None)
            total_downloads = sum(note.get("download_count", 0) for note in user_notes)
            
            # Calculate initial points
            points = (upload_count * 100) + (total_downloads * 5)
            
            # Calculate level
            level = 1
            if points >= 500000:
                level = 50
            elif points >= 200000:
                level = 40
            elif points >= 100000:
                level = 30
            elif points >= 50000:
                level = 20
            elif points >= 10000:
                level = 10
            elif points >= 2500:
                level = 5
            
            level_names = {
                1: "Newbie",
                5: "Helper",
                10: "Expert",
                20: "Master",
                30: "Champion",
                40: "Elite",
                50: "Legend"
            }
            
            await db.user_points.insert_one({
                "user_id": user_id,
                "total_points": points,
                "level": level,
                "level_name": level_names.get(level, "Newbie"),
                "points_history": [
                    {
                        "action": "migration_initial",
                        "points": points,
                        "timestamp": datetime.utcnow()
                    }
                ],
                "created_at": datetime.utcnow()
            })
            
            print(f"  ✅ Initialized points for {usn}: {points} points (Level {level})")
        
        migrated_count += 1
        
        # Progress indicator
        if migrated_count % 10 == 0:
            print(f"  📊 Progress: {migrated_count}/{total_users} users migrated")
    
    print(f"\n✨ Migration completed successfully!")
    print(f"✅ {migrated_count} users migrated")
    print(f"✅ Referral codes generated")
    print(f"✅ Streaks initialized")
    print(f"✅ Points calculated")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
