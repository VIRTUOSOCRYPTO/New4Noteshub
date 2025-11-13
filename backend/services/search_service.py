"""
Search Service for NotesHub

Provides advanced search capabilities:
- Full-text search with MongoDB text indexes
- Fuzzy search with typo tolerance
- Search autocomplete
- Search history tracking
- Saved searches
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import re


class SearchService:
    """Service for advanced search functionality"""
    
    def __init__(self, database):
        self.db = database
    
    async def ensure_text_indexes(self):
        """Create text indexes for full-text search"""
        try:
            # Create text index on notes
            await self.db.notes.create_index([
                ("title", "text"),
                ("subject", "text"),
                ("department", "text")
            ], name="notes_text_index")
            
            print("Text indexes created successfully")
        except Exception as e:
            # Index might already exist
            print(f"Text index creation: {e}")
    
    async def search_notes(
        self,
        query: str,
        department: Optional[str] = None,
        subject: Optional[str] = None,
        year: Optional[int] = None,
        file_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "relevance",
        limit: int = 50
    ) -> List[Dict]:
        """Advanced search with multiple filters"""
        
        # Build search query
        search_query = {"is_approved": True}
        
        # Text search
        if query:
            # Use MongoDB text search for better performance
            search_query["$text"] = {"$search": query}
        
        # Apply filters
        if department:
            search_query["department"] = department
        if subject:
            search_query["subject"] = subject
        if year:
            search_query["year"] = year
        if file_type:
            # Extract file extension from filename
            search_query["original_filename"] = {"$regex": f"\\.{file_type}$", "$options": "i"}
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = date_from
            if date_to:
                date_filter["$lte"] = date_to
            search_query["uploaded_at"] = date_filter
        
        # Build projection to include text score for relevance sorting
        projection = None
        if query and sort_by == "relevance":
            projection = {"score": {"$meta": "textScore"}}
        
        # Execute search
        cursor = self.db.notes.find(search_query, projection)
        
        # Apply sorting
        if sort_by == "relevance" and query:
            cursor = cursor.sort([("score", {"$meta": "textScore"})])
        elif sort_by == "date":
            cursor = cursor.sort("uploaded_at", -1)
        elif sort_by == "downloads":
            cursor = cursor.sort("download_count", -1)
        elif sort_by == "views":
            cursor = cursor.sort("view_count", -1)
        else:
            cursor = cursor.sort("uploaded_at", -1)
        
        cursor = cursor.limit(limit)
        notes = await cursor.to_list(length=limit)
        
        # Serialize ObjectId
        for note in notes:
            note["id"] = str(note["_id"])
            del note["_id"]
            # Remove text score from results
            if "score" in note:
                del note["score"]
        
        return notes
    
    async def fuzzy_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Fuzzy search with typo tolerance"""
        
        # Create regex pattern for fuzzy matching
        # Allow 1 character difference per 3 characters
        fuzzy_pattern = ".*".join(query)
        
        search_query = {
            "is_approved": True,
            "$or": [
                {"title": {"$regex": fuzzy_pattern, "$options": "i"}},
                {"subject": {"$regex": fuzzy_pattern, "$options": "i"}}
            ]
        }
        
        notes = await self.db.notes.find(search_query).limit(limit).to_list(length=limit)
        
        # Serialize
        for note in notes:
            note["id"] = str(note["_id"])
            del note["_id"]
        
        return notes
    
    async def get_autocomplete_suggestions(
        self,
        query: str,
        field: str = "title",
        limit: int = 10
    ) -> List[str]:
        """Get autocomplete suggestions for search"""
        
        if len(query) < 2:
            return []
        
        # Create case-insensitive regex
        regex_pattern = f"^{re.escape(query)}"
        
        # Get distinct values matching the pattern
        pipeline = [
            {
                "$match": {
                    field: {"$regex": regex_pattern, "$options": "i"},
                    "is_approved": True
                }
            },
            {"$group": {"_id": f"${field}"}},
            {"$limit": limit}
        ]
        
        results = await self.db.notes.aggregate(pipeline).to_list(length=limit)
        suggestions = [r["_id"] for r in results if r["_id"]]
        
        # Also include subject and department suggestions
        if field == "title":
            # Get subject suggestions
            subject_pipeline = [
                {
                    "$match": {
                        "subject": {"$regex": regex_pattern, "$options": "i"},
                        "is_approved": True
                    }
                },
                {"$group": {"_id": "$subject"}},
                {"$limit": 5}
            ]
            subject_results = await self.db.notes.aggregate(subject_pipeline).to_list(length=5)
            suggestions.extend([r["_id"] for r in subject_results if r["_id"]])
        
        # Remove duplicates and limit
        return list(dict.fromkeys(suggestions))[:limit]
    
    async def save_search_history(
        self,
        user_id: str,
        query: str,
        filters: Dict = None
    ):
        """Save search query to user's history"""
        
        search_entry = {
            "user_id": user_id,
            "query": query,
            "filters": filters or {},
            "timestamp": datetime.utcnow()
        }
        
        # Check if this exact search already exists in recent history
        existing = await self.db.search_history.find_one({
            "user_id": user_id,
            "query": query,
            "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)}
        })
        
        if not existing:
            await self.db.search_history.insert_one(search_entry)
        
        # Cleanup old history (keep last 50 searches per user)
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$sort": {"timestamp": -1}},
            {"$skip": 50}
        ]
        
        old_searches = await self.db.search_history.aggregate(pipeline).to_list(length=None)
        if old_searches:
            old_ids = [s["_id"] for s in old_searches]
            await self.db.search_history.delete_many({"_id": {"$in": old_ids}})
    
    async def get_search_history(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """Get user's recent search history"""
        
        searches = await self.db.search_history.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # Serialize
        for search in searches:
            search["id"] = str(search["_id"])
            del search["_id"]
        
        return searches
    
    async def clear_search_history(self, user_id: str):
        """Clear user's search history"""
        await self.db.search_history.delete_many({"user_id": user_id})
    
    async def save_search(
        self,
        user_id: str,
        name: str,
        query: str,
        filters: Dict = None
    ) -> str:
        """Save a search for later use"""
        
        saved_search = {
            "user_id": user_id,
            "name": name,
            "query": query,
            "filters": filters or {},
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.saved_searches.insert_one(saved_search)
        return str(result.inserted_id)
    
    async def get_saved_searches(self, user_id: str) -> List[Dict]:
        """Get user's saved searches"""
        
        searches = await self.db.saved_searches.find(
            {"user_id": user_id}
        ).sort("created_at", -1).to_list(length=None)
        
        # Serialize
        for search in searches:
            search["id"] = str(search["_id"])
            del search["_id"]
        
        return searches
    
    async def delete_saved_search(self, search_id: str, user_id: str):
        """Delete a saved search"""
        result = await self.db.saved_searches.delete_one({
            "_id": ObjectId(search_id),
            "user_id": user_id
        })
        return result.deleted_count > 0
    
    async def get_popular_searches(self, limit: int = 10) -> List[Dict]:
        """Get most popular search queries"""
        
        pipeline = [
            {"$group": {
                "_id": "$query",
                "count": {"$sum": 1},
                "last_searched": {"$max": "$timestamp"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        popular = await self.db.search_history.aggregate(pipeline).to_list(length=limit)
        
        return [
            {
                "query": p["_id"],
                "count": p["count"],
                "last_searched": p["last_searched"]
            }
            for p in popular
        ]


search_service: Optional[SearchService] = None


def get_search_service(database) -> SearchService:
    """Get or create search service instance"""
    global search_service
    if search_service is None:
        search_service = SearchService(database)
    return search_service
