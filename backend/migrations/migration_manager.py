"""
MongoDB Migration Manager
Handles database schema changes and data migrations
"""

import os
import importlib
import inspect
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class Migration:
    """Base class for migrations"""
    
    version: str = "0.0.0"
    description: str = ""
    
    async def up(self, db: AsyncIOMotorDatabase):
        """Apply migration"""
        raise NotImplementedError("Migration must implement 'up' method")
    
    async def down(self, db: AsyncIOMotorDatabase):
        """Rollback migration"""
        raise NotImplementedError("Migration must implement 'down' method")


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, db: AsyncIOMotorDatabase, migrations_dir: str = "migrations/versions"):
        self.db = db
        self.migrations_dir = Path(migrations_dir)
        self.migrations_collection = db.migrations
    
    async def initialize(self):
        """Initialize migrations collection"""
        # Create migrations collection if it doesn't exist
        collections = await self.db.list_collection_names()
        if "migrations" not in collections:
            await self.db.create_collection("migrations")
            logger.info("Created migrations collection")
        
        # Create index on version
        await self.migrations_collection.create_index("version", unique=True)
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        cursor = self.migrations_collection.find({}, {"version": 1})
        migrations = await cursor.to_list(length=1000)
        return [m["version"] for m in migrations]
    
    async def mark_migration_applied(self, version: str, description: str):
        """Mark a migration as applied"""
        await self.migrations_collection.insert_one({
            "version": version,
            "description": description,
            "applied_at": datetime.utcnow()
        })
        logger.info(f"Marked migration {version} as applied")
    
    async def mark_migration_reverted(self, version: str):
        """Mark a migration as reverted"""
        await self.migrations_collection.delete_one({"version": version})
        logger.info(f"Marked migration {version} as reverted")
    
    def discover_migrations(self) -> List[Migration]:
        """Discover all migration files"""
        migrations = []
        
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return migrations
        
        # Find all Python files in migrations directory
        for file_path in sorted(self.migrations_dir.glob("*.py")):
            if file_path.name.startswith("_"):
                continue
            
            # Import migration module
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find Migration subclasses
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, Migration) and 
                        obj is not Migration):
                        migrations.append(obj())
        
        # Sort by version
        migrations.sort(key=lambda m: m.version)
        return migrations
    
    async def migrate(self, target_version: str = None):
        """
        Apply migrations up to target version
        If target_version is None, apply all pending migrations
        """
        await self.initialize()
        
        applied_migrations = await self.get_applied_migrations()
        all_migrations = self.discover_migrations()
        
        pending_migrations = [
            m for m in all_migrations 
            if m.version not in applied_migrations
        ]
        
        if target_version:
            pending_migrations = [
                m for m in pending_migrations 
                if m.version <= target_version
            ]
        
        if not pending_migrations:
            logger.info("No pending migrations to apply")
            return
        
        logger.info(f"Found {len(pending_migrations)} pending migrations")
        
        for migration in pending_migrations:
            logger.info(f"Applying migration {migration.version}: {migration.description}")
            
            try:
                await migration.up(self.db)
                await self.mark_migration_applied(migration.version, migration.description)
                logger.info(f"✅ Successfully applied migration {migration.version}")
            except Exception as e:
                logger.error(f"❌ Failed to apply migration {migration.version}: {e}")
                raise
    
    async def rollback(self, target_version: str = None):
        """
        Rollback migrations to target version
        If target_version is None, rollback the last migration
        """
        await self.initialize()
        
        applied_migrations = await self.get_applied_migrations()
        applied_migrations.sort(reverse=True)
        
        if not applied_migrations:
            logger.info("No migrations to rollback")
            return
        
        all_migrations = self.discover_migrations()
        migrations_dict = {m.version: m for m in all_migrations}
        
        migrations_to_revert = []
        
        if target_version:
            # Rollback to specific version
            migrations_to_revert = [
                v for v in applied_migrations 
                if v > target_version
            ]
        else:
            # Rollback last migration only
            migrations_to_revert = [applied_migrations[0]]
        
        for version in migrations_to_revert:
            if version not in migrations_dict:
                logger.warning(f"Migration {version} not found, skipping rollback")
                continue
            
            migration = migrations_dict[version]
            logger.info(f"Rolling back migration {version}: {migration.description}")
            
            try:
                await migration.down(self.db)
                await self.mark_migration_reverted(version)
                logger.info(f"✅ Successfully rolled back migration {version}")
            except Exception as e:
                logger.error(f"❌ Failed to rollback migration {version}: {e}")
                raise
    
    async def status(self) -> Dict[str, Any]:
        """Get migration status"""
        await self.initialize()
        
        applied_migrations = await self.get_applied_migrations()
        all_migrations = self.discover_migrations()
        
        pending_migrations = [
            {"version": m.version, "description": m.description}
            for m in all_migrations 
            if m.version not in applied_migrations
        ]
        
        applied_info = [
            {"version": m.version, "description": m.description}
            for m in all_migrations 
            if m.version in applied_migrations
        ]
        
        return {
            "total_migrations": len(all_migrations),
            "applied_count": len(applied_migrations),
            "pending_count": len(pending_migrations),
            "applied_migrations": applied_info,
            "pending_migrations": pending_migrations
        }


# Example migration
class InitialMigration(Migration):
    """Initial database setup"""
    
    version = "1.0.0"
    description = "Create initial collections and indexes"
    
    async def up(self, db: AsyncIOMotorDatabase):
        """Create collections and indexes"""
        # Create indexes for users collection
        await db.users.create_index("usn", unique=True)
        await db.users.create_index("email", unique=True)
        await db.users.create_index("created_at")
        
        # Create indexes for notes collection
        await db.notes.create_index([("department", 1), ("year", 1)])
        await db.notes.create_index("uploaded_at")
        await db.notes.create_index("is_approved")
        await db.notes.create_index("user_id")
        
        # Create text index for search
        await db.notes.create_index([
            ("title", "text"),
            ("subject", "text")
        ])
        
        logger.info("Created all indexes")
    
    async def down(self, db: AsyncIOMotorDatabase):
        """Drop indexes"""
        await db.users.drop_indexes()
        await db.notes.drop_indexes()
        logger.info("Dropped all indexes")
