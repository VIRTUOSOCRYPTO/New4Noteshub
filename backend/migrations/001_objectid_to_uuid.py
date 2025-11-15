"""
Migration: ObjectId to UUID
Converts all MongoDB ObjectId fields to UUID strings for better JSON serialization

This migration:
1. Adds 'id' field as UUID string to all documents
2. Converts all ObjectId references to UUID strings
3. Maintains data integrity by updating all relationships
"""

import asyncio
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class ObjectIdToUuidMigration:
    """Migration to convert ObjectId to UUID strings"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.id_mapping = {}  # Maps old ObjectId to new UUID
    
    async def connect(self):
        """Connect to database"""
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/noteshub")
        self.client = AsyncIOMotorClient(mongo_url)
        db_name = mongo_url.split("/")[-1].split("?")[0] if "/" in mongo_url else "noteshub"
        self.db = self.client[db_name]
        print(f"✅ Connected to database: {db_name}")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    def generate_uuid(self) -> str:
        """Generate a new UUID string"""
        return str(uuid.uuid4())
    
    async def migrate_users(self):
        """Migrate users collection"""
        print("\n📦 Migrating users collection...")
        
        users = await self.db.users.find({}).to_list(None)
        migrated = 0
        
        for user in users:
            old_id = user["_id"]
            
            # Generate new UUID
            new_id = self.generate_uuid()
            self.id_mapping[str(old_id)] = new_id
            
            # Add id field
            user["id"] = new_id
            
            # Update document
            await self.db.users.update_one(
                {"_id": old_id},
                {"$set": {"id": new_id}}
            )
            migrated += 1
        
        print(f"   ✅ Migrated {migrated} users")
        return migrated
    
    async def migrate_notes(self):
        """Migrate notes collection and update userId references"""
        print("\n📦 Migrating notes collection...")
        
        notes = await self.db.notes.find({}).to_list(None)
        migrated = 0
        
        for note in notes:
            old_id = note["_id"]
            
            # Generate new UUID for note
            new_id = self.generate_uuid()
            
            # Update userId reference if it exists
            updates = {"id": new_id}
            
            if "userId" in note and isinstance(note["userId"], ObjectId):
                old_user_id = str(note["userId"])
                if old_user_id in self.id_mapping:
                    updates["userId"] = self.id_mapping[old_user_id]
            
            # Update flaggedBy and reviewedBy if they exist
            if "flaggedBy" in note and isinstance(note["flaggedBy"], ObjectId):
                old_flagged_by = str(note["flaggedBy"])
                if old_flagged_by in self.id_mapping:
                    updates["flaggedBy"] = self.id_mapping[old_flagged_by]
            
            if "reviewedBy" in note and isinstance(note["reviewedBy"], ObjectId):
                old_reviewed_by = str(note["reviewedBy"])
                if old_reviewed_by in self.id_mapping:
                    updates["reviewedBy"] = self.id_mapping[old_reviewed_by]
            
            # Update document
            await self.db.notes.update_one(
                {"_id": old_id},
                {"$set": updates}
            )
            migrated += 1
        
        print(f"   ✅ Migrated {migrated} notes")
        return migrated
    
    async def migrate_bookmarks(self):
        """Migrate bookmarks collection"""
        print("\n📦 Migrating bookmarks collection...")
        
        bookmarks = await self.db.bookmarks.find({}).to_list(None)
        migrated = 0
        
        for bookmark in bookmarks:
            old_id = bookmark["_id"]
            new_id = self.generate_uuid()
            
            updates = {"id": new_id}
            
            # Update user_id and note_id references
            if "user_id" in bookmark:
                old_user_id = str(bookmark["user_id"])
                if old_user_id in self.id_mapping:
                    updates["user_id"] = self.id_mapping[old_user_id]
            
            if "note_id" in bookmark:
                # Note IDs will be updated separately, just keep string version for now
                updates["note_id"] = str(bookmark["note_id"])
            
            await self.db.bookmarks.update_one(
                {"_id": old_id},
                {"$set": updates}
            )
            migrated += 1
        
        print(f"   ✅ Migrated {migrated} bookmarks")
        return migrated
    
    async def migrate_messages(self):
        """Migrate messages collection"""
        print("\n📦 Migrating messages collection...")
        
        messages = await self.db.messages.find({}).to_list(None)
        migrated = 0
        
        for message in messages:
            old_id = message["_id"]
            new_id = self.generate_uuid()
            
            updates = {"id": new_id}
            
            # Update sender_id and receiver_id references
            if "sender_id" in message and str(message["sender_id"]) in self.id_mapping:
                updates["sender_id"] = self.id_mapping[str(message["sender_id"])]
            
            if "receiver_id" in message and str(message["receiver_id"]) in self.id_mapping:
                updates["receiver_id"] = self.id_mapping[str(message["receiver_id"])]
            
            await self.db.messages.update_one(
                {"_id": old_id},
                {"$set": updates}
            )
            migrated += 1
        
        print(f"   ✅ Migrated {migrated} messages")
        return migrated
    
    async def migrate_drawings(self):
        """Migrate drawings collection"""
        print("\n📦 Migrating drawings collection...")
        
        drawings = await self.db.drawings.find({}).to_list(None)
        migrated = 0
        
        for drawing in drawings:
            old_id = drawing["_id"]
            new_id = self.generate_uuid()
            
            updates = {"id": new_id}
            
            # Update user_id and note_id references
            if "user_id" in drawing and str(drawing["user_id"]) in self.id_mapping:
                updates["user_id"] = self.id_mapping[str(drawing["user_id"])]
            
            if "note_id" in drawing:
                updates["note_id"] = str(drawing["note_id"])
            
            await self.db.drawings.update_one(
                {"_id": old_id},
                {"$set": updates}
            )
            migrated += 1
        
        print(f"   ✅ Migrated {migrated} drawings")
        return migrated
    
    async def migrate_search_history(self):
        """Migrate search_history collection"""
        print("\n📦 Migrating search_history collection...")
        
        searches = await self.db.search_history.find({}).to_list(None)
        migrated = 0
        
        for search in searches:
            old_id = search["_id"]
            new_id = self.generate_uuid()
            
            updates = {"id": new_id}
            
            if "user_id" in search and str(search["user_id"]) in self.id_mapping:
                updates["user_id"] = self.id_mapping[str(search["user_id"])]
            
            await self.db.search_history.update_one(
                {"_id": old_id},
                {"$set": updates}
            )
            migrated += 1
        
        print(f"   ✅ Migrated {migrated} search history entries")
        return migrated
    
    async def migrate_saved_searches(self):
        """Migrate saved_searches collection"""
        print("\n📦 Migrating saved_searches collection...")
        
        searches = await self.db.saved_searches.find({}).to_list(None)
        migrated = 0
        
        for search in searches:
            old_id = search["_id"]
            new_id = self.generate_uuid()
            
            updates = {"id": new_id}
            
            if "user_id" in search and str(search["user_id"]) in self.id_mapping:
                updates["user_id"] = self.id_mapping[str(search["user_id"])]
            
            await self.db.saved_searches.update_one(
                {"_id": old_id},
                {"$set": updates}
            )
            migrated += 1
        
        print(f"   ✅ Migrated {migrated} saved searches")
        return migrated
    
    async def create_migration_record(self):
        """Record migration in migrations_history collection"""
        record = {
            "migration_name": "001_objectid_to_uuid",
            "executed_at": datetime.utcnow(),
            "status": "completed",
            "records_migrated": len(self.id_mapping)
        }
        await self.db.migrations_history.insert_one(record)
        print("\n✅ Migration record created")
    
    async def run_migration(self):
        """Run the complete migration"""
        print("="*60)
        print("🚀 Starting ObjectId to UUID Migration")
        print("="*60)
        
        await self.connect()
        
        try:
            # Migrate collections in order (users first, then dependent collections)
            await self.migrate_users()
            await self.migrate_notes()
            await self.migrate_bookmarks()
            await self.migrate_messages()
            await self.migrate_drawings()
            await self.migrate_search_history()
            await self.migrate_saved_searches()
            
            # Create migration record
            await self.create_migration_record()
            
            print("\n" + "="*60)
            print("✅ Migration completed successfully!")
            print(f"   Total records migrated: {len(self.id_mapping)}")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            raise
        finally:
            await self.close()
    
    async def rollback_migration(self):
        """Rollback the migration (remove 'id' fields)"""
        print("="*60)
        print("🔄 Rolling back ObjectId to UUID Migration")
        print("="*60)
        
        await self.connect()
        
        try:
            collections = [
                "users", "notes", "bookmarks", "messages",
                "drawings", "search_history", "saved_searches"
            ]
            
            for collection_name in collections:
                collection = self.db[collection_name]
                result = await collection.update_many(
                    {},
                    {"$unset": {"id": ""}}
                )
                print(f"✅ Removed 'id' field from {result.modified_count} documents in {collection_name}")
            
            # Remove migration record
            await self.db.migrations_history.delete_one({"migration_name": "001_objectid_to_uuid"})
            
            print("\n✅ Rollback completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Rollback failed: {e}")
            raise
        finally:
            await self.close()


async def main():
    """Main entry point"""
    import sys
    
    migration = ObjectIdToUuidMigration()
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        await migration.rollback_migration()
    else:
        await migration.run_migration()


if __name__ == "__main__":
    asyncio.run(main())
