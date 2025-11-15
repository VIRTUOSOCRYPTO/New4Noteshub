"""
Exams Router - Exam Countdown & Panic Mode
Create urgency, show trending notes, countdown timers
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from auth import get_current_user_id
from models import ExamCreate, ExamResponse, ExamCountdown
from database import get_database


router = APIRouter(prefix="/api/exams", tags=["exams"])


@router.post("/create", response_model=ExamResponse)
async def create_exam(
    exam_data: ExamCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Create an exam schedule (for admins or self)"""
    
    # Create exam
    exam_id = str(uuid.uuid4())
    days_until = (exam_data.exam_date - datetime.utcnow()).days
    
    exam = {
        "id": exam_id,
        "subject": exam_data.subject,
        "department": exam_data.department,
        "year": exam_data.year,
        "exam_date": exam_data.exam_date,
        "exam_type": exam_data.exam_type,
        "days_until": days_until,
        "created_by": user_id,
        "created_at": datetime.utcnow()
    }
    
    await db.exams.insert_one(exam)
    
    return ExamResponse(**exam)


@router.get("/my-exams")
async def get_my_exams(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get upcoming exams for current user based on department and year"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find exams for user's department and year
    now = datetime.utcnow()
    exams = await db.exams.find({
        "department": user.get("department"),
        "year": user.get("year"),
        "exam_date": {"$gte": now}
    }).sort("exam_date", 1).to_list(None)
    
    # Calculate days until each exam
    for exam in exams:
        exam["days_until"] = (exam["exam_date"] - now).days
    
    return {"exams": exams}


@router.get("/countdown", response_model=ExamCountdown)
async def get_exam_countdown(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get exam countdown with next exam and trending notes"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find upcoming exams
    now = datetime.utcnow()
    upcoming_exams = await db.exams.find({
        "department": user.get("department"),
        "year": user.get("year"),
        "exam_date": {"$gte": now}
    }).sort("exam_date", 1).to_list(None)
    
    # Calculate days until
    for exam in upcoming_exams:
        exam["days_until"] = (exam["exam_date"] - now).days
    
    # Get next exam
    next_exam = None
    if upcoming_exams:
        next_exam_data = upcoming_exams[0]
        next_exam = ExamResponse(**next_exam_data)
    
    # Get trending notes for upcoming exam subjects
    trending_notes = []
    if upcoming_exams:
        # Get subjects of exams in next 7 days
        urgent_subjects = [
            exam["subject"] for exam in upcoming_exams 
            if exam["days_until"] <= 7
        ]
        
        if urgent_subjects:
            # Find most downloaded notes for these subjects
            trending = await db.notes.find({
                "subject": {"$in": urgent_subjects},
                "is_approved": True
            }).sort("downloadCount", -1).limit(10).to_list(None)
            
            trending_notes = [note["id"] for note in trending]
    
    return ExamCountdown(
        next_exam=next_exam,
        upcoming_exams=[ExamResponse(**e) for e in upcoming_exams[:5]],
        trending_notes=trending_notes
    )


@router.get("/trending-notes/{subject}")
async def get_trending_notes_for_subject(
    subject: str,
    limit: int = Query(20, le=50),
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get trending notes for a specific subject (exam prep)"""
    
    # Get user info for department filter
    user = await db.users.find_one({"id": user_id})
    
    # Find most downloaded notes for subject
    filter_query = {
        "subject": subject,
        "is_approved": True
    }
    
    # Optionally filter by department
    if user and user.get("department"):
        filter_query["department"] = user.get("department")
    
    trending = await db.notes.find(filter_query).sort("downloadCount", -1).limit(limit).to_list(None)
    
    return {"notes": trending}


@router.get("/exam-pack/{exam_id}")
async def get_exam_pack(
    exam_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get a curated pack of best notes for an exam"""
    
    # Get exam details
    exam = await db.exams.find_one({"id": exam_id})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Find top notes for this exam's subject
    notes = await db.notes.find({
        "subject": exam["subject"],
        "department": exam["department"],
        "year": exam["year"],
        "is_approved": True
    }).sort("downloadCount", -1).limit(15).to_list(None)
    
    # Get statistics
    days_until = (exam["exam_date"] - datetime.utcnow()).days
    students_studying = await db.downloads.count_documents({
        "note_id": {"$in": [note["id"] for note in notes]},
        "downloaded_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
    })
    
    return {
        "exam": exam,
        "days_until": days_until,
        "notes": notes,
        "total_notes": len(notes),
        "students_studying": students_studying,
        "urgency_level": "high" if days_until <= 3 else "medium" if days_until <= 7 else "low"
    }


@router.get("/department-schedule")
async def get_department_schedule(
    department: Optional[str] = None,
    year: Optional[int] = None,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get full exam schedule for department and year"""
    
    # Get user info if filters not provided
    if not department or not year:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        department = department or user.get("department")
        year = year or user.get("year")
    
    # Get all exams for this department and year
    now = datetime.utcnow()
    exams = await db.exams.find({
        "department": department,
        "year": year,
        "exam_date": {"$gte": now}
    }).sort("exam_date", 1).to_list(None)
    
    # Calculate days until
    for exam in exams:
        exam["days_until"] = (exam["exam_date"] - now).days
    
    return {
        "department": department,
        "year": year,
        "exams": exams,
        "total_exams": len(exams)
    }


@router.delete("/{exam_id}")
async def delete_exam(
    exam_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Delete an exam (only creator can delete)"""
    
    # Check if exam exists and user is creator
    exam = await db.exams.find_one({"id": exam_id})
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    if exam.get("created_by") != user_id:
        raise HTTPException(status_code=403, detail="Only creator can delete")
    
    await db.exams.delete_one({"id": exam_id})
    
    return {"success": True, "message": "Exam deleted"}


@router.get("/stats")
async def get_exam_stats(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get exam-related statistics"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count upcoming exams
    now = datetime.utcnow()
    total_exams = await db.exams.count_documents({
        "department": user.get("department"),
        "year": user.get("year"),
        "exam_date": {"$gte": now}
    })
    
    # Count urgent exams (within 7 days)
    urgent_exams = await db.exams.count_documents({
        "department": user.get("department"),
        "year": user.get("year"),
        "exam_date": {
            "$gte": now,
            "$lte": now + timedelta(days=7)
        }
    })
    
    # Get study progress (notes downloaded for upcoming exams)
    upcoming = await db.exams.find({
        "department": user.get("department"),
        "year": user.get("year"),
        "exam_date": {"$gte": now}
    }).to_list(None)
    
    exam_subjects = [exam["subject"] for exam in upcoming]
    
    notes_downloaded = await db.downloads.count_documents({
        "user_id": user_id,
        "subject": {"$in": exam_subjects}
    }) if exam_subjects else 0
    
    return {
        "total_upcoming_exams": total_exams,
        "urgent_exams": urgent_exams,
        "notes_downloaded_for_exams": notes_downloaded,
        "days_until_next_exam": upcoming[0]["days_until"] if upcoming else None
    }


@router.post("/bulk-create")
async def bulk_create_exams(
    exams: List[ExamCreate],
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Bulk create exam schedules (for admins)"""
    
    created_exams = []
    
    for exam_data in exams:
        exam_id = str(uuid.uuid4())
        days_until = (exam_data.exam_date - datetime.utcnow()).days
        
        exam = {
            "id": exam_id,
            "subject": exam_data.subject,
            "department": exam_data.department,
            "year": exam_data.year,
            "exam_date": exam_data.exam_date,
            "exam_type": exam_data.exam_type,
            "days_until": days_until,
            "created_by": user_id,
            "created_at": datetime.utcnow()
        }
        
        await db.exams.insert_one(exam)
        created_exams.append(exam)
    
    return {
        "success": True,
        "created_count": len(created_exams),
        "exams": created_exams
    }


@router.get("/panic-mode")
async def get_panic_mode_data(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get data for exam panic mode UI (urgent exams within 3 days)"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find exams within 3 days
    now = datetime.utcnow()
    panic_deadline = now + timedelta(days=3)
    
    urgent_exams = await db.exams.find({
        "department": user.get("department"),
        "year": user.get("year"),
        "exam_date": {
            "$gte": now,
            "$lte": panic_deadline
        }
    }).sort("exam_date", 1).to_list(None)
    
    if not urgent_exams:
        return {
            "panic_mode": False,
            "message": "No urgent exams! You're doing great! 🎉"
        }
    
    # For each exam, get top notes and stats
    panic_data = []
    
    for exam in urgent_exams:
        days_until = (exam["exam_date"] - now).days
        hours_until = int((exam["exam_date"] - now).total_seconds() / 3600)
        
        # Get top notes for this subject
        top_notes = await db.notes.find({
            "subject": exam["subject"],
            "department": exam["department"],
            "year": exam["year"],
            "is_approved": True
        }).sort("downloadCount", -1).limit(10).to_list(None)
        
        # Count students currently studying
        studying_now = await db.downloads.count_documents({
            "subject": exam["subject"],
            "downloaded_at": {"$gte": now - timedelta(hours=1)}
        })
        
        panic_data.append({
            "exam": exam,
            "days_until": days_until,
            "hours_until": hours_until,
            "top_notes": top_notes,
            "students_studying_now": studying_now,
            "urgency": "critical" if days_until <= 1 else "high"
        })
    
    return {
        "panic_mode": True,
        "urgent_exams": panic_data,
        "total_urgent": len(urgent_exams),
        "message": f"🚨 {len(urgent_exams)} exam(s) in the next 3 days! Time to study! 📚"
    }
