"""
User-Generated Contests Router
Monthly contests, voting system, winners, creative challenges
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from auth import get_current_user_id
from models import ContestCreate, ContestResponse, ContestEntryCreate
from database import get_database


router = APIRouter(prefix="/api/contests", tags=["contests"])


@router.get("/active")
async def get_active_contests(
    db = Depends(get_database)
):
    """Get currently active contests"""
    
    now = datetime.utcnow()
    
    contests = await db.contests.find({
        "start_date": {"$lte": now},
        "end_date": {"$gte": now},
        "status": "active"
    }).sort("created_at", -1).to_list(None)
    
    # Get entry counts
    for contest in contests:
        entry_count = await db.contest_entries.count_documents({"contest_id": contest["id"]})
        contest["entry_count"] = entry_count
        
        # Calculate days remaining
        days_left = (contest["end_date"] - now).days
        contest["days_remaining"] = max(0, days_left)
    
    return {"contests": contests}


@router.get("/past")
async def get_past_contests(
    limit: int = 10,
    db = Depends(get_database)
):
    """Get past contests with winners"""
    
    now = datetime.utcnow()
    
    contests = await db.contests.find({
        "end_date": {"$lt": now},
        "status": "completed"
    }).sort("end_date", -1).limit(limit).to_list(None)
    
    # Get winner details
    for contest in contests:
        if contest.get("winner_id"):
            winner = await db.users.find_one({"id": contest["winner_id"]})
            contest["winner_usn"] = winner.get("usn") if winner else "Unknown"
    
    return {"contests": contests}


@router.post("/create")
async def create_contest(
    title: str,
    description: str,
    category: str,
    duration_days: int = 30,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Create a new contest (admin only in production)"""
    
    contest_id = str(uuid.uuid4())
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=duration_days)
    
    contest = {
        "id": contest_id,
        "title": title,
        "description": description,
        "category": category,
        "start_date": start_date,
        "end_date": end_date,
        "status": "active",
        "created_by": user_id,
        "winner_id": None,
        "created_at": start_date
    }
    
    await db.contests.insert_one(contest)
    
    return {
        "contest_id": contest_id,
        "message": "Contest created successfully!",
        "end_date": end_date.isoformat()
    }


@router.post("/enter/{contest_id}")
async def enter_contest(
    contest_id: str,
    note_id: str,
    description: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Submit an entry to a contest"""
    
    # Verify contest exists and is active
    contest = await db.contests.find_one({"id": contest_id, "status": "active"})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found or ended")
    
    # Check if user already entered
    existing_entry = await db.contest_entries.find_one({
        "contest_id": contest_id,
        "user_id": user_id
    })
    if existing_entry:
        raise HTTPException(status_code=400, detail="You've already entered this contest")
    
    # Verify note exists
    note = await db.notes.find_one({"id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    entry_id = str(uuid.uuid4())
    
    entry = {
        "id": entry_id,
        "contest_id": contest_id,
        "user_id": user_id,
        "note_id": note_id,
        "description": description,
        "votes": 0,
        "created_at": datetime.utcnow()
    }
    
    await db.contest_entries.insert_one(entry)
    
    # Award participation points
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"points": 50}}
    )
    
    return {
        "entry_id": entry_id,
        "message": "Entry submitted! +50 points 🎉",
        "points_awarded": 50
    }


@router.get("/entries/{contest_id}")
async def get_contest_entries(
    contest_id: str,
    sort_by: str = "votes",  # votes or date
    db = Depends(get_database)
):
    """Get all entries for a contest"""
    
    sort_field = "votes" if sort_by == "votes" else "created_at"
    sort_direction = -1
    
    entries = await db.contest_entries.find(
        {"contest_id": contest_id}
    ).sort(sort_field, sort_direction).to_list(None)
    
    # Enrich with user and note data
    for entry in entries:
        user = await db.users.find_one({"id": entry["user_id"]})
        note = await db.notes.find_one({"id": entry["note_id"]})
        
        entry["user_usn"] = user.get("usn") if user else "Unknown"
        entry["note_title"] = note.get("title") if note else "Unknown"
        entry["note_subject"] = note.get("subject") if note else "Unknown"
    
    return {"entries": entries}


@router.post("/vote/{entry_id}")
async def vote_for_entry(
    entry_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Vote for a contest entry"""
    
    # Get entry
    entry = await db.contest_entries.find_one({"id": entry_id})
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Check if user already voted for this entry
    existing_vote = await db.contest_votes.find_one({
        "entry_id": entry_id,
        "user_id": user_id
    })
    if existing_vote:
        raise HTTPException(status_code=400, detail="You've already voted for this entry")
    
    # Can't vote for own entry
    if entry["user_id"] == user_id:
        raise HTTPException(status_code=400, detail="You can't vote for your own entry")
    
    # Record vote
    await db.contest_votes.insert_one({
        "entry_id": entry_id,
        "user_id": user_id,
        "contest_id": entry["contest_id"],
        "created_at": datetime.utcnow()
    })
    
    # Increment vote count
    await db.contest_entries.update_one(
        {"id": entry_id},
        {"$inc": {"votes": 1}}
    )
    
    return {
        "success": True,
        "message": "Vote recorded! 🗳️"
    }


@router.get("/my-entries")
async def get_my_entries(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's contest entries"""
    
    entries = await db.contest_entries.find(
        {"user_id": user_id}
    ).sort("created_at", -1).to_list(None)
    
    # Enrich with contest data
    for entry in entries:
        contest = await db.contests.find_one({"id": entry["contest_id"]})
        entry["contest_title"] = contest.get("title") if contest else "Unknown"
        entry["contest_status"] = contest.get("status") if contest else "unknown"
    
    return {"entries": entries}


@router.get("/leaderboard/{contest_id}")
async def get_contest_leaderboard(
    contest_id: str,
    limit: int = 10,
    db = Depends(get_database)
):
    """Get top entries in a contest"""
    
    entries = await db.contest_entries.find(
        {"contest_id": contest_id}
    ).sort("votes", -1).limit(limit).to_list(None)
    
    leaderboard = []
    for idx, entry in enumerate(entries):
        user = await db.users.find_one({"id": entry["user_id"]})
        note = await db.notes.find_one({"id": entry["note_id"]})
        
        leaderboard.append({
            "rank": idx + 1,
            "entry_id": entry["id"],
            "user_usn": user.get("usn") if user else "Unknown",
            "note_title": note.get("title") if note else "Unknown",
            "votes": entry["votes"],
            "description": entry.get("description")
        })
    
    return {"leaderboard": leaderboard}


@router.post("/finalize/{contest_id}")
async def finalize_contest(
    contest_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Finalize contest and declare winner (admin only)"""
    
    contest = await db.contests.find_one({"id": contest_id})
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    # Get winning entry (highest votes)
    winning_entry = await db.contest_entries.find_one(
        {"contest_id": contest_id},
        sort=[("votes", -1)]
    )
    
    if not winning_entry:
        raise HTTPException(status_code=400, detail="No entries in contest")
    
    # Update contest
    await db.contests.update_one(
        {"id": contest_id},
        {"$set": {
            "status": "completed",
            "winner_id": winning_entry["user_id"],
            "winner_entry_id": winning_entry["id"],
            "finalized_at": datetime.utcnow()
        }}
    )
    
    # Award winner
    winner_points = 1000
    await db.users.update_one(
        {"id": winning_entry["user_id"]},
        {"$inc": {"points": winner_points}}
    )
    
    # Send notification to winner
    await db.notifications.insert_one({
        "user_id": winning_entry["user_id"],
        "type": "contest_winner",
        "title": "🏆 You Won!",
        "message": f"Congratulations! You won the '{contest['title']}' contest! +{winner_points} points",
        "data": {"contest_id": contest_id},
        "read": False,
        "created_at": datetime.utcnow()
    })
    
    return {
        "winner_id": winning_entry["user_id"],
        "votes": winning_entry["votes"],
        "message": "Contest finalized! Winner notified 🎉"
    }
