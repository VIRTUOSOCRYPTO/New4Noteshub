"""
Analytics Service for NotesHub

Provides comprehensive analytics tracking and aggregation:
- Upload/download statistics
- User engagement metrics
- Popular notes tracking
- Trend analysis and predictions
- Department-wise statistics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
import math
from collections import defaultdict


class AnalyticsService:
    """Service for tracking and analyzing user and note statistics"""
    
    def __init__(self, database):
        self.db = database
    
    async def track_event(self, event_type: str, user_id: str, metadata: Dict = None):
        """Track an analytics event"""
        event = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        await self.db.analytics_events.insert_one(event)
    
    async def get_dashboard_stats(self, user_id: Optional[str] = None, department: Optional[str] = None) -> Dict:
        """Get comprehensive dashboard statistics"""
        
        # Time ranges
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Build query filters
        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
        if department:
            query_filter["department"] = department
        
        # Total counts
        total_notes = await self.db.notes.count_documents(query_filter)
        total_users = await self.db.users.count_documents({}) if not user_id else 1
        
        # Upload statistics
        uploads_24h = await self.db.notes.count_documents({
            **query_filter,
            "uploaded_at": {"$gte": last_24h}
        })
        uploads_7d = await self.db.notes.count_documents({
            **query_filter,
            "uploaded_at": {"$gte": last_7d}
        })
        uploads_30d = await self.db.notes.count_documents({
            **query_filter,
            "uploaded_at": {"$gte": last_30d}
        })
        
        # Download statistics
        download_stats = await self.db.notes.aggregate([
            {"$match": query_filter},
            {"$group": {
                "_id": None,
                "total_downloads": {"$sum": "$download_count"},
                "avg_downloads": {"$avg": "$download_count"}
            }}
        ]).to_list(length=1)
        
        total_downloads = download_stats[0]["total_downloads"] if download_stats else 0
        avg_downloads = download_stats[0]["avg_downloads"] if (download_stats and download_stats[0]["avg_downloads"] is not None) else 0
        
        # View statistics
        view_stats = await self.db.notes.aggregate([
            {"$match": query_filter},
            {"$group": {
                "_id": None,
                "total_views": {"$sum": "$view_count"},
                "avg_views": {"$avg": "$view_count"}
            }}
        ]).to_list(length=1)
        
        total_views = view_stats[0]["total_views"] if view_stats else 0
        avg_views = view_stats[0]["avg_views"] if (view_stats and view_stats[0]["avg_views"] is not None) else 0
        
        # Active users (users who uploaded in last 7 days)
        active_users_pipeline = [
            {"$match": {"uploaded_at": {"$gte": last_7d}}},
            {"$group": {"_id": "$user_id"}},
            {"$count": "count"}
        ]
        
        if department:
            active_users_pipeline[0]["$match"]["department"] = department
        
        active_users_result = await self.db.notes.aggregate(active_users_pipeline).to_list(length=1)
        active_users = active_users_result[0]["count"] if active_users_result else 0
        
        return {
            "total_notes": total_notes,
            "total_users": total_users,
            "active_users": active_users,
            "total_downloads": total_downloads,
            "total_views": total_views,
            "avg_downloads_per_note": round(avg_downloads, 2) if avg_downloads else 0,
            "avg_views_per_note": round(avg_views, 2) if avg_views else 0,
            "uploads": {
                "last_24h": uploads_24h,
                "last_7d": uploads_7d,
                "last_30d": uploads_30d
            }
        }
    
    async def get_popular_notes(self, limit: int = 10, department: Optional[str] = None) -> List[Dict]:
        """Get most popular notes by downloads and views"""
        
        # Don't filter by is_approved if it's null - show all notes
        query = {}
        if department:
            query["department"] = department
        
        # Calculate popularity score: downloads * 2 + views (handle null values)
        pipeline = [
            {"$match": query},
            {"$addFields": {
                "download_count": {"$ifNull": ["$download_count", 0]},
                "view_count": {"$ifNull": ["$view_count", 0]},
                "popularity_score": {
                    "$add": [
                        {"$multiply": [{"$ifNull": ["$download_count", 0]}, 2]},
                        {"$ifNull": ["$view_count", 0]}
                    ]
                }
            }},
            {"$sort": {"popularity_score": -1, "uploaded_at": -1}},
            {"$limit": limit}
        ]
        
        notes = await self.db.notes.aggregate(pipeline).to_list(length=limit)
        
        # Serialize ObjectId
        for note in notes:
            note["id"] = str(note["_id"])
            del note["_id"]
        
        return notes
    
    async def get_department_statistics(self) -> List[Dict]:
        """Get statistics by department"""
        
        pipeline = [
            {"$group": {
                "_id": "$department",
                "total_notes": {"$sum": 1},
                "total_downloads": {"$sum": "$download_count"},
                "total_views": {"$sum": "$view_count"},
                "avg_downloads": {"$avg": "$download_count"},
                "avg_views": {"$avg": "$view_count"}
            }},
            {"$sort": {"total_notes": -1}}
        ]
        
        stats = await self.db.notes.aggregate(pipeline).to_list(length=None)
        
        return [
            {
                "department": stat["_id"],
                "total_notes": stat["total_notes"],
                "total_downloads": stat["total_downloads"],
                "total_views": stat["total_views"],
                "avg_downloads": round(stat["avg_downloads"], 2) if stat["avg_downloads"] is not None else 0,
                "avg_views": round(stat["avg_views"], 2) if stat["avg_views"] is not None else 0
            }
            for stat in stats
        ]
    
    async def get_subject_statistics(self, department: Optional[str] = None) -> List[Dict]:
        """Get statistics by subject"""
        
        match_stage = {}
        if department:
            match_stage["department"] = department
        
        pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {"$group": {
                "_id": "$subject",
                "total_notes": {"$sum": 1},
                "total_downloads": {"$sum": "$download_count"},
                "total_views": {"$sum": "$view_count"}
            }},
            {"$sort": {"total_notes": -1}},
            {"$limit": 20}
        ]
        
        stats = await self.db.notes.aggregate(pipeline).to_list(length=20)
        
        return [
            {
                "subject": stat["_id"],
                "total_notes": stat["total_notes"],
                "total_downloads": stat["total_downloads"],
                "total_views": stat["total_views"]
            }
            for stat in stats
        ]
    
    async def get_upload_trends(self, days: int = 30) -> List[Dict]:
        """Get upload trends over time"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get trends only for notes with valid uploaded_at dates
        pipeline = [
            {"$match": {
                "uploaded_at": {"$ne": None, "$gte": start_date}
            }},
            {"$group": {
                "_id": {
                    "year": {"$year": "$uploaded_at"},
                    "month": {"$month": "$uploaded_at"},
                    "day": {"$dayOfMonth": "$uploaded_at"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        trends_data = await self.db.notes.aggregate(pipeline).to_list(length=None)
        
        # Create a map of dates to counts
        trends_map = {}
        for trend in trends_data:
            date_str = f"{trend['_id']['year']}-{trend['_id']['month']:02d}-{trend['_id']['day']:02d}"
            trends_map[date_str] = trend["count"]
        
        # Fill in all days in the range with zeros for missing dates
        result = []
        current_date = start_date
        end_date = datetime.utcnow()
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            result.append({
                "date": date_str,
                "uploads": trends_map.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return result
    
    async def get_engagement_metrics(self, days: int = 7) -> Dict:
        """Get user engagement metrics"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Active users per day
        daily_active_pipeline = [
            {"$match": {"uploaded_at": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$uploaded_at"},
                    "month": {"$month": "$uploaded_at"},
                    "day": {"$dayOfMonth": "$uploaded_at"},
                    "user_id": "$user_id"
                }
            }},
            {"$group": {
                "_id": {
                    "year": "$_id.year",
                    "month": "$_id.month",
                    "day": "$_id.day"
                },
                "active_users": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        daily_active = await self.db.notes.aggregate(daily_active_pipeline).to_list(length=None)
        
        engagement_data = [
            {
                "date": f"{day['_id']['year']}-{day['_id']['month']:02d}-{day['_id']['day']:02d}",
                "active_users": day["active_users"]
            }
            for day in daily_active
        ]
        
        return {
            "daily_active_users": engagement_data,
            "period_days": days
        }
    
    async def predict_trends(self, metric: str = "uploads", days_ahead: int = 7) -> List[Dict]:
        """Simple linear prediction for trends"""
        
        # Get historical data (last 30 days)
        trends = await self.get_upload_trends(days=30)
        
        if len(trends) < 7:
            return []  # Not enough data for prediction
        
        # Simple moving average prediction
        recent_values = [t["uploads"] for t in trends[-7:]]
        avg_value = sum(recent_values) / len(recent_values)
        
        # Calculate trend (linear)
        trend_slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
        
        # Generate predictions
        last_date = datetime.strptime(trends[-1]["date"], "%Y-%m-%d")
        predictions = []
        
        for i in range(1, days_ahead + 1):
            pred_date = last_date + timedelta(days=i)
            pred_value = max(0, avg_value + (trend_slope * i))  # Ensure non-negative
            
            predictions.append({
                "date": pred_date.strftime("%Y-%m-%d"),
                "predicted_uploads": round(pred_value, 1),
                "confidence": "medium"  # Simple prediction has medium confidence
            })
        
        return predictions
    
    async def get_user_analytics(self, user_id: str) -> Dict:
        """Get detailed analytics for a specific user"""
        
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return {}
        
        # User's notes
        user_notes = await self.db.notes.find({"user_id": user_id}).to_list(length=None)
        
        # Calculate statistics
        total_uploads = len(user_notes)
        total_downloads = sum(note.get("download_count", 0) for note in user_notes)
        total_views = sum(note.get("view_count", 0) for note in user_notes)
        
        # Most popular note
        most_popular = max(user_notes, key=lambda n: n.get("download_count", 0)) if user_notes else None
        
        # Subjects covered
        subjects = list(set(note["subject"] for note in user_notes))
        
        # Upload frequency (uploads per week)
        if user_notes:
            oldest_upload = min(note["uploaded_at"] for note in user_notes)
            weeks_active = max(1, (datetime.utcnow() - oldest_upload).days / 7)
            upload_frequency = total_uploads / weeks_active
        else:
            upload_frequency = 0
        
        return {
            "user_id": user_id,
            "usn": user["usn"],
            "department": user["department"],
            "total_uploads": total_uploads,
            "total_downloads": total_downloads,
            "total_views": total_views,
            "subjects_covered": len(subjects),
            "upload_frequency": round(upload_frequency, 2),
            "most_popular_note": {
                "id": str(most_popular["_id"]),
                "title": most_popular["title"],
                "downloads": most_popular.get("download_count", 0)
            } if most_popular else None
        }


analytics_service: Optional[AnalyticsService] = None


def get_analytics_service(database) -> AnalyticsService:
    """Get or create analytics service instance"""
    global analytics_service
    if analytics_service is None:
        analytics_service = AnalyticsService(database)
    return analytics_service
