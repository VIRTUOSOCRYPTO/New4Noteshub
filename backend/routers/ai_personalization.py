"""
AI-Powered Personalization API
Smart recommendations and insights using Emergent LLM
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
import os
from dotenv import load_dotenv
from auth import get_current_user_id
from database import get_database

load_dotenv()

router = APIRouter(prefix="/api/ai", tags=["AI Personalization"])

# Import AI chat library
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False
    print("Warning: emergentintegrations not installed. AI features disabled.")


def get_ai_chat():
    """Initialize AI chat with Emergent LLM key"""
    if not AI_ENABLED:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="AI API key not configured")
    
    chat = LlmChat(
        api_key=api_key,
        session_id="noteshub-ai",
        system_message="You are an AI study assistant for NotesHub. Provide concise, helpful recommendations for students. Keep responses under 150 words."
    ).with_model("openai", "gpt-4o-mini")
    
    return chat


@router.get("/recommendations/notes")
async def get_ai_note_recommendations(
    limit: int = 10,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """AI-powered note recommendations based on user behavior"""
    
    # Get user's download history
    user_downloads = await db.note_downloads.find({
        "user_id": user_id
    }).sort("downloaded_at", -1).limit(20).to_list(20)
    
    downloaded_note_ids = [d.get("note_id") for d in user_downloads]
    
    # Get subjects from downloaded notes
    downloaded_notes = await db.notes.find({
        "id": {"$in": downloaded_note_ids}
    }).to_list(100)
    
    subjects = list(set([n.get("subject") for n in downloaded_notes]))
    departments = list(set([n.get("department") for n in downloaded_notes]))
    
    # Get user profile
    user = await db.users.find_one({"user_id": user_id})
    user_department = user.get("department", "")
    user_year = user.get("year", "")
    
    # Build AI prompt
    chat = get_ai_chat()
    prompt = f"""
User Profile:
- Department: {user_department}
- Year: {user_year}
- Recently studied: {', '.join(subjects[:5]) if subjects else 'No history yet'}
- Downloaded {len(user_downloads)} notes

Recommend 5 specific subjects or topics this student should study next. 
Format: Just list 5 subjects, one per line, no explanations.
"""
    
    try:
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse AI response to get subjects
        recommended_subjects = [s.strip() for s in response.split('\n') if s.strip()]
        recommended_subjects = recommended_subjects[:5]
        
    except Exception as e:
        print(f"AI error: {e}")
        # Fallback: recommend based on department and popularity
        recommended_subjects = subjects[:3] if subjects else []
    
    # Find notes matching recommendations
    if recommended_subjects:
        # Create regex pattern for flexible matching
        subject_pattern = "|".join(recommended_subjects)
        recommended_notes = await db.notes.find({
            "$or": [
                {"subject": {"$in": recommended_subjects}},
                {"title": {"$regex": subject_pattern, "$options": "i"}}
            ],
            "id": {"$nin": downloaded_note_ids},  # Exclude already downloaded
            "department": user_department
        }).sort("download_count", -1).limit(limit).to_list(limit)
    else:
        # Fallback: popular notes in user's department
        recommended_notes = await db.notes.find({
            "department": user_department,
            "id": {"$nin": downloaded_note_ids}
        }).sort("download_count", -1).limit(limit).to_list(limit)
    
    return {
        "recommendations": recommended_notes,
        "reason": "AI-powered based on your study behavior",
        "recommended_subjects": recommended_subjects,
        "personalized": True
    }


@router.get("/insights/study-pattern")
async def get_study_insights(
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """AI-generated insights about user's study patterns"""
    
    # Gather user activity data
    user_points = await db.user_points.find_one({"user_id": user_id})
    streak = await db.streaks.find_one({"user_id": user_id})
    
    # Upload stats
    uploads = await db.notes.count_documents({"uploaded_by": user_id})
    
    # Download stats
    downloads_count = await db.note_downloads.count_documents({"user_id": user_id})
    
    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_activity = await db.note_downloads.count_documents({
        "user_id": user_id,
        "downloaded_at": {"$gte": week_ago}
    })
    
    # Study groups
    groups_count = await db.study_group_members.count_documents({
        "user_id": user_id
    })
    
    # Build AI prompt
    chat = get_ai_chat()
    prompt = f"""
Analyze this student's study pattern and provide 3 actionable insights:

Stats:
- Level: {user_points.get('level', 1) if user_points else 1}
- Points: {user_points.get('total_points', 0) if user_points else 0}
- Current Streak: {streak.get('current_streak', 0) if streak else 0} days
- Notes Uploaded: {uploads}
- Notes Downloaded: {downloads_count}
- Active last 7 days: {recent_activity} downloads
- Study Groups: {groups_count}

Provide exactly 3 insights:
1. Study habit strength (engagement level)
2. One specific recommendation to improve
3. One motivational insight

Format: 3 bullet points, each under 30 words.
"""
    
    try:
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse insights
        insights = [s.strip() for s in response.split('\n') if s.strip() and (s.strip().startswith('-') or s.strip()[0].isdigit())]
        
    except Exception as e:
        print(f"AI error: {e}")
        # Fallback insights
        insights = [
            f"You're at Level {user_points.get('level', 1) if user_points else 1} with {streak.get('current_streak', 0) if streak else 0} day streak - keep it up!",
            f"Try joining more study groups to boost collaboration (currently in {groups_count} groups).",
            "Regular activity leads to better learning - maintain your daily streak!"
        ]
    
    return {
        "insights": insights[:3],
        "stats": {
            "level": user_points.get('level', 1) if user_points else 1,
            "points": user_points.get('total_points', 0) if user_points else 0,
            "streak": streak.get('current_streak', 0) if streak else 0,
            "uploads": uploads,
            "downloads": downloads_count,
            "groups": groups_count
        },
        "personalized": True
    }


@router.get("/study-plan")
async def generate_study_plan(
    days: int = 7,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate AI-powered personalized study plan"""
    
    # Get upcoming exams
    upcoming_exams = await db.exams.find({
        "department": user_id,
        "exam_date": {"$gte": datetime.now()}
    }).sort("exam_date", 1).limit(5).to_list(5)
    
    # Get user's weak subjects (subjects with fewer downloads)
    user_downloads = await db.note_downloads.aggregate([
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "notes",
            "localField": "note_id",
            "foreignField": "id",
            "as": "note_info"
        }},
        {"$unwind": "$note_info"},
        {"$group": {
            "_id": "$note_info.subject",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": 1}}
    ]).to_list(10)
    
    weak_subjects = [s["_id"] for s in user_downloads[:3]] if user_downloads else []
    
    # Build AI prompt
    chat = get_ai_chat()
    exam_info = "\n".join([f"- {e.get('subject')} on {e.get('exam_date').strftime('%b %d')}" for e in upcoming_exams]) if upcoming_exams else "No upcoming exams"
    weak_info = ", ".join(weak_subjects) if weak_subjects else "None identified"
    
    prompt = f"""
Create a {days}-day study plan for this student:

Upcoming Exams:
{exam_info}

Subjects needing attention: {weak_info}

Provide a day-by-day plan with:
- Subject to focus on
- Study duration (hours)
- Specific task

Format: Day X: [Subject] - [Hours]h - [Task]
Example: Day 1: Mathematics - 2h - Review calculus fundamentals
"""
    
    try:
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse plan
        plan_lines = [s.strip() for s in response.split('\n') if s.strip() and 'Day' in s]
        
    except Exception as e:
        print(f"AI error: {e}")
        # Fallback plan
        plan_lines = [
            f"Day 1: {weak_subjects[0] if weak_subjects else 'Core Subject'} - 2h - Review fundamentals",
            f"Day 2: {weak_subjects[1] if len(weak_subjects) > 1 else 'Practice'} - 2h - Solve problems",
            f"Day 3: {upcoming_exams[0].get('subject') if upcoming_exams else 'Important Topic'} - 3h - Exam prep"
        ]
    
    return {
        "study_plan": plan_lines[:days],
        "duration_days": days,
        "upcoming_exams": upcoming_exams,
        "focus_subjects": weak_subjects,
        "personalized": True
    }


@router.post("/summarize-note/{note_id}")
async def summarize_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Generate AI summary of a note (for premium/unlocked users)"""
    
    note = await db.notes.find_one({"id": note_id})
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check if user has access (implement your unlock logic here)
    # For now, we'll allow all authenticated users
    
    chat = get_ai_chat()
    
    # Create a summary prompt
    note_title = note.get("title", "")
    note_subject = note.get("subject", "")
    note_description = note.get("description", "")
    
    prompt = f"""
Summarize this academic note in 3-5 bullet points:

Title: {note_title}
Subject: {note_subject}
Description: {note_description}

Provide key concepts and main topics covered.
Format: Bullet points, each under 25 words.
"""
    
    try:
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse summary
        summary_points = [s.strip() for s in response.split('\n') if s.strip() and (s.strip().startswith('-') or s.strip().startswith('•'))]
        
    except Exception as e:
        print(f"AI error: {e}")
        summary_points = [
            f"Covers key concepts in {note_subject}",
            "Comprehensive study material",
            "Helpful for exam preparation"
        ]
    
    # Track AI usage
    await db.ai_usage.insert_one({
        "user_id": user_id,
        "action": "summarize_note",
        "note_id": note_id,
        "timestamp": datetime.now()
    })
    
    return {
        "note_id": note_id,
        "summary": summary_points,
        "note_title": note_title,
        "generated_at": datetime.now().isoformat()
    }


@router.get("/similar-students")
async def find_similar_students(
    limit: int = 10,
    user_id: str = Depends(get_current_user_id), db = Depends(get_database)
):
    """Find students with similar study patterns using AI"""
    
    # Get user's subjects and activity
    user_downloads = await db.note_downloads.aggregate([
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "notes",
            "localField": "note_id",
            "foreignField": "id",
            "as": "note_info"
        }},
        {"$unwind": "$note_info"},
        {"$group": {
            "_id": "$note_info.subject",
            "count": {"$sum": 1}
        }}
    ]).to_list(20)
    
    user_subjects = [s["_id"] for s in user_downloads]
    
    # Find users who downloaded similar subjects
    similar_users = await db.note_downloads.aggregate([
        {"$lookup": {
            "from": "notes",
            "localField": "note_id",
            "foreignField": "id",
            "as": "note_info"
        }},
        {"$unwind": "$note_info"},
        {"$match": {
            "note_info.subject": {"$in": user_subjects},
            "user_id": {"$ne": user_id}
        }},
        {"$group": {
            "_id": "$user_id",
            "common_subjects": {"$sum": 1}
        }},
        {"$sort": {"common_subjects": -1}},
        {"$limit": limit}
    ]).to_list(limit)
    
    # Get user details
    similar_user_ids = [u["_id"] for u in similar_users]
    user_profiles = await db.users.find({
        "user_id": {"$in": similar_user_ids}
    }).to_list(limit)
    
    return {
        "similar_students": user_profiles,
        "match_reason": "Similar study interests",
        "common_subjects": user_subjects[:5]
    }


@router.get("/health")
async def ai_health():
    """Check AI service health"""
    return {
        "ai_enabled": AI_ENABLED,
        "api_key_configured": bool(os.getenv("EMERGENT_LLM_KEY")),
        "service": "Emergent LLM (OpenAI GPT-4o-mini)"
    }
