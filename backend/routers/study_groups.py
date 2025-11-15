"""
Study Groups Router - Collaborative Learning
Create groups, chat, share notes, assign tasks, compete
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional
from datetime import datetime
import uuid
import json

from auth import get_current_user_id
from models import (
    StudyGroupCreate, StudyGroupUpdate, StudyGroupResponse,
    GroupChatMessage, GroupChatMessageResponse,
    GroupTask, GroupTaskResponse
)
from database import get_database
from routers.gamification import update_user_points, check_and_update_streak


router = APIRouter(prefix="/api/study-groups", tags=["study_groups"])


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}  # group_id -> list of websockets
    
    async def connect(self, websocket: WebSocket, group_id: str):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, group_id: str):
        if group_id in self.active_connections:
            self.active_connections[group_id].remove(websocket)
    
    async def broadcast(self, group_id: str, message: dict):
        if group_id in self.active_connections:
            for connection in self.active_connections[group_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass


manager = ConnectionManager()


@router.post("/create", response_model=StudyGroupResponse)
async def create_study_group(
    group_data: StudyGroupCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Create a new study group"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create group
    group_id = str(uuid.uuid4())
    group = {
        "id": group_id,
        "name": group_data.name,
        "description": group_data.description,
        "subject": group_data.subject,
        "created_by": user_id,
        "created_at": datetime.utcnow(),
        "is_private": group_data.is_private,
        "max_members": group_data.max_members,
        "member_count": 1
    }
    
    await db.study_groups.insert_one(group)
    
    # Add creator as admin member
    await db.study_group_members.insert_one({
        "group_id": group_id,
        "user_id": user_id,
        "usn": user.get("usn"),
        "role": "admin",
        "joined_at": datetime.utcnow()
    })
    
    # Award points for creating group
    await update_user_points(db, user_id, "create_group", 50)
    
    # Return response
    members = [{
        "user_id": user_id,
        "usn": user.get("usn"),
        "role": "admin",
        "joined_at": datetime.utcnow()
    }]
    
    return StudyGroupResponse(
        id=group_id,
        name=group["name"],
        description=group["description"],
        subject=group["subject"],
        created_by=user_id,
        created_at=group["created_at"],
        is_private=group["is_private"],
        member_count=1,
        members=members,
        max_members=group["max_members"]
    )


@router.get("/my-groups")
async def get_my_groups(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get all groups user is a member of"""
    
    # Find all group memberships
    memberships = await db.study_group_members.find({"user_id": user_id}).to_list(None)
    group_ids = [m["group_id"] for m in memberships]
    
    # Get group details
    groups = await db.study_groups.find({"id": {"$in": group_ids}}).to_list(None)
    
    # Enrich with member info
    result = []
    for group in groups:
        members = await db.study_group_members.find({"group_id": group["id"]}).to_list(None)
        
        result.append({
            **group,
            "member_count": len(members),
            "members": members[:5]  # First 5 members for preview
        })
    
    return {"groups": result}


@router.get("/{group_id}", response_model=StudyGroupResponse)
async def get_group_details(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get detailed information about a study group"""
    
    # Check if group exists
    group = await db.study_groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user is member (for private groups)
    if group.get("is_private"):
        is_member = await db.study_group_members.find_one({
            "group_id": group_id,
            "user_id": user_id
        })
        if not is_member:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all members
    members = await db.study_group_members.find({"group_id": group_id}).to_list(None)
    
    return StudyGroupResponse(
        id=group["id"],
        name=group["name"],
        description=group.get("description"),
        subject=group.get("subject"),
        created_by=group["created_by"],
        created_at=group["created_at"],
        is_private=group["is_private"],
        member_count=len(members),
        members=members,
        max_members=group["max_members"]
    )


@router.post("/{group_id}/join")
async def join_group(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Join a study group"""
    
    # Check if group exists
    group = await db.study_groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if already a member
    existing = await db.study_group_members.find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already a member")
    
    # Check member limit
    member_count = await db.study_group_members.count_documents({"group_id": group_id})
    if member_count >= group["max_members"]:
        raise HTTPException(status_code=400, detail="Group is full")
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    
    # Add member
    await db.study_group_members.insert_one({
        "group_id": group_id,
        "user_id": user_id,
        "usn": user.get("usn"),
        "role": "member",
        "joined_at": datetime.utcnow()
    })
    
    # Update member count
    await db.study_groups.update_one(
        {"id": group_id},
        {"$inc": {"member_count": 1}}
    )
    
    # Award points
    await update_user_points(db, user_id, "join_group", 20)
    
    return {
        "success": True,
        "message": f"Joined {group['name']}! +20 points 🎉"
    }


@router.post("/{group_id}/leave")
async def leave_group(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Leave a study group"""
    
    # Check if member
    membership = await db.study_group_members.find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    if not membership:
        raise HTTPException(status_code=400, detail="Not a member")
    
    # Check if admin (can't leave if only admin)
    if membership["role"] == "admin":
        admin_count = await db.study_group_members.count_documents({
            "group_id": group_id,
            "role": "admin"
        })
        if admin_count == 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot leave - you're the only admin. Transfer admin rights first."
            )
    
    # Remove member
    await db.study_group_members.delete_one({
        "group_id": group_id,
        "user_id": user_id
    })
    
    # Update member count
    await db.study_groups.update_one(
        {"id": group_id},
        {"$inc": {"member_count": -1}}
    )
    
    return {"success": True, "message": "Left group successfully"}


@router.get("/{group_id}/messages")
async def get_group_messages(
    group_id: str,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get chat messages for a group"""
    
    # Check if user is member
    is_member = await db.study_group_members.find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member")
    
    # Get messages
    messages = await db.group_messages.find(
        {"group_id": group_id}
    ).sort("timestamp", -1).limit(limit).to_list(None)
    
    # Reverse to show oldest first
    messages.reverse()
    
    return {"messages": messages}


@router.post("/{group_id}/messages")
async def send_group_message(
    group_id: str,
    message: GroupChatMessage,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Send a chat message to the group"""
    
    # Check if user is member
    is_member = await db.study_group_members.find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member")
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    
    # Create message
    message_id = str(uuid.uuid4())
    message_doc = {
        "id": message_id,
        "group_id": group_id,
        "user_id": user_id,
        "usn": user.get("usn"),
        "message": message.message,
        "timestamp": datetime.utcnow()
    }
    
    await db.group_messages.insert_one(message_doc)
    
    # Broadcast to WebSocket connections
    await manager.broadcast(group_id, message_doc)
    
    # Award points for participation
    await update_user_points(db, user_id, "group_message", 2)
    
    return {
        "success": True,
        "message_id": message_id
    }


@router.websocket("/{group_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    group_id: str,
    db = Depends(get_database)
):
    """WebSocket endpoint for real-time chat"""
    
    await manager.connect(websocket, group_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Save message to database
            message_id = str(uuid.uuid4())
            message_doc = {
                "id": message_id,
                "group_id": group_id,
                "user_id": message_data["user_id"],
                "usn": message_data["usn"],
                "message": message_data["message"],
                "timestamp": datetime.utcnow()
            }
            
            await db.group_messages.insert_one(message_doc)
            
            # Broadcast to all connections
            await manager.broadcast(group_id, message_doc)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, group_id)


@router.post("/{group_id}/tasks", response_model=GroupTaskResponse)
async def create_group_task(
    group_id: str,
    task: GroupTask,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Create a task for the study group"""
    
    # Check if user is member
    membership = await db.study_group_members.find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member")
    
    # Only admins/moderators can create tasks
    if membership["role"] not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Only admins can create tasks")
    
    # Create task
    task_id = str(uuid.uuid4())
    task_doc = {
        "id": task_id,
        "group_id": group_id,
        "title": task.title,
        "description": task.description,
        "assigned_to": task.assigned_to,
        "due_date": task.due_date,
        "created_by": user_id,
        "created_at": datetime.utcnow(),
        "completed": False
    }
    
    await db.group_tasks.insert_one(task_doc)
    
    return GroupTaskResponse(**task_doc)


@router.get("/{group_id}/tasks")
async def get_group_tasks(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get all tasks for a group"""
    
    # Check if user is member
    is_member = await db.study_group_members.find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member")
    
    tasks = await db.group_tasks.find({"group_id": group_id}).to_list(None)
    
    return {"tasks": tasks}


@router.patch("/{group_id}/tasks/{task_id}/complete")
async def mark_task_complete(
    group_id: str,
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Mark a task as completed"""
    
    # Check if user is member
    is_member = await db.study_group_members.find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member")
    
    # Update task
    result = await db.group_tasks.update_one(
        {"id": task_id, "group_id": group_id},
        {"$set": {"completed": True, "completed_by": user_id, "completed_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Award points
    await update_user_points(db, user_id, "complete_task", 30)
    
    return {"success": True, "message": "Task completed! +30 points 🎉"}


@router.get("/discover")
async def discover_groups(
    subject: Optional[str] = None,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Discover public study groups"""
    
    # Build filter
    filter_query = {"is_private": False}
    if subject:
        filter_query["subject"] = subject
    
    # Get groups
    groups = await db.study_groups.find(filter_query).limit(limit).to_list(None)
    
    # Check which groups user is already in
    user_groups = await db.study_group_members.find({"user_id": user_id}).to_list(None)
    user_group_ids = {g["group_id"] for g in user_groups}
    
    # Enrich with member count and joined status
    result = []
    for group in groups:
        member_count = await db.study_group_members.count_documents({"group_id": group["id"]})
        
        result.append({
            **group,
            "member_count": member_count,
            "is_joined": group["id"] in user_group_ids
        })
    
    return {"groups": result}


@router.get("/{group_id}/stats")
async def get_group_stats(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_database)
):
    """Get statistics for a study group"""
    
    # Check if user is member
    is_member = await db.study_group_members.find_one({
        "group_id": group_id,
        "user_id": user_id
    })
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member")
    
    # Get stats
    member_count = await db.study_group_members.count_documents({"group_id": group_id})
    message_count = await db.group_messages.count_documents({"group_id": group_id})
    task_count = await db.group_tasks.count_documents({"group_id": group_id})
    completed_tasks = await db.group_tasks.count_documents({"group_id": group_id, "completed": True})
    
    # Get most active members
    pipeline = [
        {"$match": {"group_id": group_id}},
        {"$group": {"_id": "$user_id", "message_count": {"$sum": 1}}},
        {"$sort": {"message_count": -1}},
        {"$limit": 5}
    ]
    
    active_members = await db.group_messages.aggregate(pipeline).to_list(None)
    
    return {
        "member_count": member_count,
        "message_count": message_count,
        "task_count": task_count,
        "completed_tasks": completed_tasks,
        "completion_rate": (completed_tasks / task_count * 100) if task_count > 0 else 0,
        "most_active_members": active_members
    }
