"""
Database Connection Tests
"""

import pytest
from database import Database


@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    db = Database()
    await db.connect_to_database()
    
    assert db.client is not None
    assert db.db is not None
    
    await db.close_database_connection()


@pytest.mark.asyncio
async def test_database_indexes_created():
    """Test that database indexes are created"""
    db = Database()
    await db.connect_to_database()
    
    # Check if users collection has indexes
    indexes = await db.db.users.index_information()
    assert len(indexes) > 1  # At least _id and one custom index
    
    # Check if notes collection has indexes
    indexes = await db.db.notes.index_information()
    assert len(indexes) > 1
    
    await db.close_database_connection()
