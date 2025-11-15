#!/usr/bin/env python3
"""
Migration Script - Add uploaded_at timestamps to existing notes
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


async def main():
    """Fix missing uploaded_at timestamps for notes"""
    print("=" * 60)
    print("NotesHub - Fix Note Timestamps Migration")
    print("=" * 60)
    print()
    
    # Connect to database
    print("🔌 Connecting to database...")
    await db.connect_to_database()
    print("✓ Database connected")
    print()
    
    # Get all notes without uploaded_at
    print("📝 Finding notes without uploaded_at timestamps...")
    notes = await db.db.notes.find({
        "$or": [
            {"uploaded_at": {"$exists": False}},
            {"uploaded_at": None}
        ]
    }).to_list(None)
    
    print(f"✓ Found {len(notes)} notes to update")
    print()
    
    if len(notes) == 0:
        print("✨ All notes already have uploaded_at timestamps!")
        await db.close_database_connection()
        return
    
    # Update each note
    updated_count = 0
    now = datetime.utcnow()
    
    for note in notes:
        note_id = note.get("_id")
        
        # Use existing createdAt if available, otherwise use current time
        uploaded_at = note.get("createdAt") or now
        
        result = await db.db.notes.update_one(
            {"_id": note_id},
            {"$set": {"uploaded_at": uploaded_at}}
        )
        
        if result.modified_count > 0:
            updated_count += 1
            print(f"  ✓ Updated note {note_id} with uploaded_at: {uploaded_at}")
    
    print()
    print("=" * 60)
    print("📊 Migration Summary:")
    print(f"   Total notes processed: {len(notes)}")
    print(f"   Successfully updated: {updated_count}")
    print("=" * 60)
    print()
    
    # Close database connection
    await db.close_database_connection()
    print("✓ Database connection closed")
    print("✅ Migration complete!")


if __name__ == "__main__":
    asyncio.run(main())
