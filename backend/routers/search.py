"""
Search Router for NotesHub

Provides endpoints for:
- Advanced search with filters
- Fuzzy search
- Autocomplete suggestions
- Search history
- Saved searches
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from database import get_database
from auth import get_current_user_id
from services.search_service import get_search_service

router = APIRouter(prefix="/api/search", tags=["search"])


class SaveSearchRequest(BaseModel):
    name: str
    query: str
    filters: Optional[dict] = None


@router.get("/")
async def search_notes(
    q: str = Query(..., min_length=1),
    department: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    file_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort_by: str = "relevance",
    limit: int = 50,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Advanced search with multiple filters - respects user's college"""
    
    # Get current user to filter by college
    user = await database.users.find_one({"id": user_id})
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    
    user_college = user.get("college")
    user_department = user.get("department")
    user_year = user.get("year")
    
    search_svc = get_search_service(database)
    
    # Parse dates if provided
    date_from_obj = datetime.fromisoformat(date_from) if date_from else None
    date_to_obj = datetime.fromisoformat(date_to) if date_to else None
    
    # Perform search with user context
    results = await search_svc.search_notes(
        query=q,
        department=department,
        subject=subject,
        year=year,
        file_type=file_type,
        date_from=date_from_obj,
        date_to=date_to_obj,
        sort_by=sort_by,
        limit=limit,
        user_college=user_college,
        user_department=user_department,
        user_year=user_year
    )
    
    # Save to search history
    filters = {
        "department": department,
        "subject": subject,
        "year": year,
        "file_type": file_type,
        "sort_by": sort_by
    }
    await search_svc.save_search_history(user_id, q, filters)
    
    return {
        "results": results,
        "count": len(results),
        "query": q
    }


@router.get("/fuzzy")
async def fuzzy_search(
    q: str = Query(..., min_length=2),
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Fuzzy search with typo tolerance"""
    
    search_svc = get_search_service(database)
    results = await search_svc.fuzzy_search(q, limit=limit)
    
    return {
        "results": results,
        "count": len(results),
        "query": q
    }


@router.get("/autocomplete")
async def get_autocomplete(
    q: str = Query(..., min_length=2),
    field: str = "title",
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get autocomplete suggestions"""
    
    if field not in ["title", "subject", "department"]:
        raise HTTPException(status_code=400, detail="Invalid field for autocomplete")
    
    search_svc = get_search_service(database)
    suggestions = await search_svc.get_autocomplete_suggestions(q, field, limit)
    
    return {
        "suggestions": suggestions,
        "count": len(suggestions)
    }


@router.get("/history")
async def get_search_history(
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get user's search history"""
    
    search_svc = get_search_service(database)
    history = await search_svc.get_search_history(user_id, limit)
    
    return {
        "history": history,
        "count": len(history)
    }


@router.delete("/history")
async def clear_search_history(
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Clear user's search history"""
    
    search_svc = get_search_service(database)
    await search_svc.clear_search_history(user_id)
    
    return {"message": "Search history cleared"}


@router.post("/saved")
async def save_search(
    request: SaveSearchRequest,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Save a search for later use"""
    
    search_svc = get_search_service(database)
    search_id = await search_svc.save_search(
        user_id,
        request.name,
        request.query,
        request.filters
    )
    
    return {
        "message": "Search saved successfully",
        "search_id": search_id
    }


@router.get("/saved")
async def get_saved_searches(
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get user's saved searches"""
    
    search_svc = get_search_service(database)
    saved = await search_svc.get_saved_searches(user_id)
    
    return {
        "searches": saved,
        "count": len(saved)
    }


@router.delete("/saved/{search_id}")
async def delete_saved_search(
    search_id: str,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Delete a saved search"""
    
    search_svc = get_search_service(database)
    deleted = await search_svc.delete_saved_search(search_id, user_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Saved search not found")
    
    return {"message": "Saved search deleted"}


@router.get("/popular")
async def get_popular_searches(
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    database = Depends(get_database)
):
    """Get most popular search queries"""
    
    search_svc = get_search_service(database)
    popular = await search_svc.get_popular_searches(limit)
    
    return {
        "searches": popular,
        "count": len(popular)
    }
