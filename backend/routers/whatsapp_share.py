"""
WhatsApp Share Integration Router
Deep links, pre-formatted messages, QR codes, one-click sharing
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
import urllib.parse
import qrcode
import io
import base64

from auth import get_current_user_id
from database import get_database


router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


def generate_whatsapp_link(text: str, phone: Optional[str] = None) -> str:
    """Generate WhatsApp deep link"""
    encoded_text = urllib.parse.quote(text)
    
    if phone:
        # Direct message to specific number
        return f"https://wa.me/{phone}?text={encoded_text}"
    else:
        # Share to WhatsApp (opens share sheet)
        return f"https://api.whatsapp.com/send?text={encoded_text}"


def generate_qr_code(data: str) -> str:
    """Generate QR code as base64 image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


@router.get("/share-note/{note_id}")
async def get_share_note_link(
    note_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get WhatsApp share link for a note"""
    
    # Get note details
    note = await db.notes.find_one({"id": note_id})
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Get user info for referral tracking
    user = await db.users.find_one({"id": user_id})
    referral_code = user.get("referral_code", "")
    
    # Create app deep link
    app_url = f"https://noteshub.app/notes/{note_id}?ref={referral_code}"
    
    # Pre-formatted message
    message = f"""📚 *{note['title']}*

Subject: {note.get('subject', 'N/A')}
Uploaded by: {user.get('usn', 'Student')}

Get this note and thousands more on NotesHub! 🚀

{app_url}

#NotesHub #StudyNotes #ExamPrep"""
    
    whatsapp_link = generate_whatsapp_link(message)
    
    # Generate QR code
    qr_code = generate_qr_code(whatsapp_link)
    
    # Track share intent
    await db.share_analytics.insert_one({
        "user_id": user_id,
        "note_id": note_id,
        "platform": "whatsapp",
        "created_at": datetime.utcnow()
    })
    
    return {
        "whatsapp_link": whatsapp_link,
        "qr_code": qr_code,
        "message_preview": message,
        "app_url": app_url
    }


@router.get("/share-achievement")
async def get_share_achievement_link(
    achievement_name: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get WhatsApp share link for achievement unlock"""
    
    user = await db.users.find_one({"id": user_id})
    referral_code = user.get("referral_code", "")
    
    app_url = f"https://noteshub.app?ref={referral_code}"
    
    message = f"""🏆 *Achievement Unlocked!*

I just unlocked "{achievement_name}" on NotesHub! 🎉

Join me and unlock 50+ achievements while studying together!

{app_url}

#NotesHub #Achievement #StudyGoals"""
    
    whatsapp_link = generate_whatsapp_link(message)
    qr_code = generate_qr_code(whatsapp_link)
    
    return {
        "whatsapp_link": whatsapp_link,
        "qr_code": qr_code,
        "message_preview": message
    }


@router.get("/share-group/{group_id}")
async def get_share_group_link(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get WhatsApp share link for study group invitation"""
    
    # Get group details
    group = await db.study_groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    user = await db.users.find_one({"id": user_id})
    
    app_url = f"https://noteshub.app/groups/{group_id}/join"
    
    message = f"""👥 *Join My Study Group!*

{group['name']}
{group.get('description', '')}

Subject: {group.get('subject', 'General')}
Members: {group.get('member_count', 0)}/{group.get('max_members', 50)}

Let's study together on NotesHub! 📚

{app_url}

#NotesHub #StudyGroup #CollaborativeLearning"""
    
    whatsapp_link = generate_whatsapp_link(message)
    qr_code = generate_qr_code(whatsapp_link)
    
    return {
        "whatsapp_link": whatsapp_link,
        "qr_code": qr_code,
        "message_preview": message,
        "group_name": group['name']
    }


@router.get("/share-streak")
async def get_share_streak_link(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get WhatsApp share link for streak milestone"""
    
    user = await db.users.find_one({"id": user_id})
    streak = user.get("streak", 0)
    referral_code = user.get("referral_code", "")
    
    app_url = f"https://noteshub.app?ref={referral_code}"
    
    message = f"""🔥 *{streak}-Day Streak on NotesHub!*

I've been studying consistently for {streak} days straight! 💪

Join me on NotesHub and build your study streak too!

{app_url}

#NotesHub #StudyStreak #Consistency"""
    
    whatsapp_link = generate_whatsapp_link(message)
    qr_code = generate_qr_code(whatsapp_link)
    
    return {
        "whatsapp_link": whatsapp_link,
        "qr_code": qr_code,
        "message_preview": message,
        "streak_days": streak
    }


@router.get("/share-leaderboard-rank")
async def get_share_leaderboard_link(
    rank: int,
    leaderboard_type: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get WhatsApp share link for leaderboard achievement"""
    
    user = await db.users.find_one({"id": user_id})
    referral_code = user.get("referral_code", "")
    
    app_url = f"https://noteshub.app?ref={referral_code}"
    
    leaderboard_names = {
        "all-india": "All-India",
        "college": "College",
        "department": "Department"
    }
    
    board_name = leaderboard_names.get(leaderboard_type, "Leaderboard")
    
    message = f"""🏆 *Ranked #{rank} on {board_name} Leaderboard!*

I'm now #{rank} on NotesHub's {board_name} leaderboard! 🎉

Compete with students across India!

{app_url}

#NotesHub #Leaderboard #TopStudent"""
    
    whatsapp_link = generate_whatsapp_link(message)
    qr_code = generate_qr_code(whatsapp_link)
    
    return {
        "whatsapp_link": whatsapp_link,
        "qr_code": qr_code,
        "message_preview": message,
        "rank": rank
    }


@router.get("/share-referral")
async def get_share_referral_link(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get WhatsApp share link for referral program"""
    
    user = await db.users.find_one({"id": user_id})
    referral_code = user.get("referral_code", "")
    total_referrals = user.get("total_referrals", 0)
    
    app_url = f"https://noteshub.app?ref={referral_code}"
    
    message = f"""🎁 *Join NotesHub with My Referral!*

Hey! I'm using NotesHub - the best platform for college notes and study resources! 📚

✅ 1000+ quality notes
✅ AI-powered features
✅ Study groups & challenges
✅ Earn rewards while studying

Join with my link and get *20 FREE downloads*! 🎉

{app_url}

Use code: {referral_code}

#NotesHub #Referral #StudyTogether"""
    
    whatsapp_link = generate_whatsapp_link(message)
    qr_code = generate_qr_code(whatsapp_link)
    
    return {
        "whatsapp_link": whatsapp_link,
        "qr_code": qr_code,
        "message_preview": message,
        "referral_code": referral_code,
        "total_referrals": total_referrals
    }


@router.get("/group-invite-template")
async def get_group_invite_template(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get template message for inviting class to WhatsApp group"""
    
    user = await db.users.find_one({"id": user_id})
    referral_code = user.get("referral_code", "")
    
    app_url = f"https://noteshub.app?ref={referral_code}"
    
    template = f"""📢 *Hey Class! Check this out!*

I found this amazing app called NotesHub! 🚀

Features:
📚 Download notes from all subjects
✍️ Upload and share your own notes
🏆 Earn points and rewards
👥 Join study groups
🔥 Track your study streaks
🎯 Compete on leaderboards

*Join our class on NotesHub!*

{app_url}

Let's help each other ace our exams! 💯

#NotesHub #ClassNotes #StudyBuddy"""
    
    whatsapp_link = generate_whatsapp_link(template)
    
    return {
        "whatsapp_link": whatsapp_link,
        "template": template,
        "instructions": "Copy this message and share to your class WhatsApp group!"
    }


@router.get("/exam-reminder-template")
async def get_exam_reminder_template(
    subject: str,
    days_left: int,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get template for exam reminder to share in groups"""
    
    # Get trending notes for subject
    notes = await db.notes.find({
        "subject": subject
    }).sort("download_count", -1).limit(3).to_list(3)
    
    urgency = "🚨 URGENT!" if days_left <= 3 else "⚠️ REMINDER"
    
    note_list = "\n".join([f"• {note['title']}" for note in notes[:3]])
    
    app_url = f"https://noteshub.app/find?subject={urllib.parse.quote(subject)}"
    
    template = f"""{urgency} *{subject} Exam in {days_left} Days!*

Quick! Get these trending notes:

{note_list}

And many more on NotesHub!

{app_url}

Let's ace this exam together! 💪📚

#NotesHub #ExamPrep #{subject.replace(' ', '')}"""
    
    whatsapp_link = generate_whatsapp_link(template)
    
    return {
        "whatsapp_link": whatsapp_link,
        "template": template,
        "subject": subject,
        "days_left": days_left
    }


@router.post("/track-share")
async def track_share_action(
    share_type: str,
    item_id: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Track when user shares content to WhatsApp"""
    
    # Record share
    await db.whatsapp_shares.insert_one({
        "user_id": user_id,
        "share_type": share_type,
        "item_id": item_id,
        "platform": "whatsapp",
        "shared_at": datetime.utcnow()
    })
    
    # Award points for sharing
    points = 10
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"points": points}}
    )
    
    return {
        "success": True,
        "points_earned": points,
        "message": f"Shared! +{points} points"
    }


@router.get("/share-stats")
async def get_share_stats(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get user's WhatsApp sharing statistics"""
    
    total_shares = await db.whatsapp_shares.count_documents({"user_id": user_id})
    
    # Shares by type
    shares_by_type = await db.whatsapp_shares.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$share_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(None)
    
    # Referrals from WhatsApp shares
    referrals = await db.referrals.count_documents({
        "referrer_id": user_id,
        "source": "whatsapp"
    })
    
    return {
        "total_shares": total_shares,
        "shares_by_type": {item["_id"]: item["count"] for item in shares_by_type},
        "referrals_from_shares": referrals,
        "points_earned": total_shares * 10
    }
