#!/usr/bin/env python
"""
MongoDB Migration Runner
Usage:
    python run_migrations.py migrate      # Apply all pending migrations
    python run_migrations.py rollback     # Rollback last migration
    python run_migrations.py status       # Show migration status
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

from migrations.migration_manager import MigrationManager

async def main():
    # Get command
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    # Connect to database
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/noteshub")
    client = AsyncIOMotorClient(mongo_url)
    
    # Get database name from URL or use default
    db_name = "noteshub"
    if "/" in mongo_url:
        db_name = mongo_url.split("/")[-1].split("?")[0]
    
    db = client[db_name]
    
    # Create migration manager
    manager = MigrationManager(db)
    
    try:
        if command == "migrate":
            print("🔄 Applying migrations...")
            await manager.migrate()
            print("✅ Migrations completed successfully")
            
        elif command == "rollback":
            print("⏪ Rolling back last migration...")
            await manager.rollback()
            print("✅ Rollback completed successfully")
            
        elif command == "status":
            print("📊 Migration Status:")
            status = await manager.status()
            print(f"\nTotal migrations: {status['total_migrations']}")
            print(f"Applied: {status['applied_count']}")
            print(f"Pending: {status['pending_count']}")
            
            if status['applied_migrations']:
                print("\n✅ Applied migrations:")
                for m in status['applied_migrations']:
                    print(f"  - {m['version']}: {m['description']}")
            
            if status['pending_migrations']:
                print("\n⏳ Pending migrations:")
                for m in status['pending_migrations']:
                    print(f"  - {m['version']}: {m['description']}")
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python run_migrations.py [migrate|rollback|status]")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
