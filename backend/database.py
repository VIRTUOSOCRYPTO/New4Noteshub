from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    async def connect_to_database(self):
        """Connect to MongoDB"""
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/noteshub")
        print(f"Connecting to MongoDB: {mongo_url}")
        self.client = AsyncIOMotorClient(mongo_url)
        # Extract database name from URL or use default
        if "/" in mongo_url:
            db_name = mongo_url.split("/")[-1].split("?")[0]
        else:
            db_name = "noteshub"
        self.db = self.client[db_name]
        print(f"Connected to database: {db_name}")
        
        # Create indexes for better performance
        await self.create_indexes()

    async def create_indexes(self):
        """Create database indexes"""
        if self.db is None:
            return
        
        # Users collection indexes
        await self.db.users.create_index("usn", unique=True)
        await self.db.users.create_index("email", unique=True)
        await self.db.users.create_index("department")
        await self.db.users.create_index("college")
        await self.db.users.create_index("year")
        
        # Notes collection indexes
        await self.db.notes.create_index("user_id")
        await self.db.notes.create_index("department")
        await self.db.notes.create_index("year")
        await self.db.notes.create_index("subject")
        await self.db.notes.create_index("is_approved")
        await self.db.notes.create_index("is_flagged")
        await self.db.notes.create_index("uploaded_at")
        
        # Bookmarks collection indexes
        await self.db.bookmarks.create_index([("user_id", 1), ("note_id", 1)], unique=True)
        
        # Messages collection indexes
        await self.db.messages.create_index("sender_id")
        await self.db.messages.create_index("receiver_id")
        await self.db.messages.create_index("sent_at")
        
        # Conversations collection indexes
        await self.db.conversations.create_index([("user1_id", 1), ("user2_id", 1)], unique=True)
        
        # Drawings collection indexes
        await self.db.drawings.create_index("user_id")
        await self.db.drawings.create_index("note_id")
        await self.db.drawings.create_index("is_public")
        
        print("Database indexes created successfully")

    async def close_database_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

# Global database instance
db = Database()

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if db.db is None:
        raise Exception("Database not initialized")
    return db.db
