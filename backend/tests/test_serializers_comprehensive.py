"""
Comprehensive tests for serializers
"""

import pytest
from bson import ObjectId

import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils.serializers import (
    serialize_doc,
    serialize_docs,
    remove_sensitive_fields
)


class TestSerializeDoc:
    """Test serialize_doc function"""
    
    def test_serialize_doc_with_objectid(self):
        """Test document with ObjectId gets converted"""
        doc = {
            "_id": ObjectId(),
            "title": "Test Note",
            "content": "Sample content"
        }
        
        result = serialize_doc(doc)
        
        assert "id" in result
        assert "_id" not in result
        assert result["title"] == "Test Note"
        assert isinstance(result["id"], str)
    
    def test_serialize_doc_without_objectid(self):
        """Test document without _id field"""
        doc = {
            "title": "Test Note",
            "content": "Sample content"
        }
        
        result = serialize_doc(doc)
        
        assert "_id" not in result
        assert "id" not in result
        assert result["title"] == "Test Note"
    
    def test_serialize_doc_with_none(self):
        """Test serialize_doc with None returns None"""
        result = serialize_doc(None)
        assert result is None
    
    def test_serialize_doc_with_empty_dict(self):
        """Test serialize_doc with empty dict"""
        doc = {}
        result = serialize_doc(doc)
        # serialize_doc returns None for empty dict based on the implementation
        assert result is None or result == {}
    
    def test_serialize_doc_preserves_other_fields(self):
        """Test that other fields are preserved during serialization"""
        doc = {
            "_id": ObjectId(),
            "title": "Test",
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "number": 42
        }
        
        result = serialize_doc(doc)
        
        assert result["title"] == "Test"
        assert result["nested"] == {"key": "value"}
        assert result["list"] == [1, 2, 3]
        assert result["number"] == 42


class TestSerializeDocs:
    """Test serialize_docs function"""
    
    def test_serialize_docs_multiple(self):
        """Test serializing multiple documents"""
        docs = [
            {"_id": ObjectId(), "title": "Note 1"},
            {"_id": ObjectId(), "title": "Note 2"},
            {"_id": ObjectId(), "title": "Note 3"}
        ]
        
        results = serialize_docs(docs)
        
        assert len(results) == 3
        for result in results:
            assert "id" in result
            assert "_id" not in result
    
    def test_serialize_docs_empty_list(self):
        """Test serializing empty list"""
        docs = []
        results = serialize_docs(docs)
        assert results == []
    
    def test_serialize_docs_mixed_content(self):
        """Test serializing docs with and without _id"""
        docs = [
            {"_id": ObjectId(), "title": "Note 1"},
            {"title": "Note 2"}  # No _id
        ]
        
        results = serialize_docs(docs)
        
        assert len(results) == 2
        assert "id" in results[0]
        assert "id" not in results[1]


class TestRemoveSensitiveFields:
    """Test remove_sensitive_fields function"""
    
    def test_remove_password_hash(self):
        """Test password_hash is removed"""
        user = {
            "id": "123",
            "email": "test@example.com",
            "password_hash": "hashed_password"
        }
        
        result = remove_sensitive_fields(user)
        
        assert "password_hash" not in result
        assert result["email"] == "test@example.com"
    
    def test_remove_two_factor_secret(self):
        """Test two_factor_secret is removed"""
        user = {
            "id": "123",
            "email": "test@example.com",
            "two_factor_secret": "secret123"
        }
        
        result = remove_sensitive_fields(user)
        
        assert "two_factor_secret" not in result
        assert result["id"] == "123"
    
    def test_remove_multiple_sensitive_fields(self):
        """Test multiple sensitive fields are removed"""
        user = {
            "id": "123",
            "email": "test@example.com",
            "password_hash": "hashed",
            "two_factor_secret": "secret",
            "refresh_token": "token123",
            "reset_token": "reset123",
            "reset_token_expiry": "2025-12-31"
        }
        
        result = remove_sensitive_fields(user)
        
        assert "password_hash" not in result
        assert "two_factor_secret" not in result
        assert "refresh_token" not in result
        assert "reset_token" not in result
        assert "reset_token_expiry" not in result
        assert result["email"] == "test@example.com"
    
    def test_remove_sensitive_fields_preserves_safe_fields(self):
        """Test that safe fields are preserved"""
        user = {
            "id": "123",
            "email": "test@example.com",
            "usn": "1RV21CS001",
            "department": "CSE",
            "role": "user",
            "password_hash": "hashed"
        }
        
        result = remove_sensitive_fields(user)
        
        assert result["id"] == "123"
        assert result["email"] == "test@example.com"
        assert result["usn"] == "1RV21CS001"
        assert result["department"] == "CSE"
        assert result["role"] == "user"
        assert "password_hash" not in result
    
    def test_remove_sensitive_fields_nonexistent(self):
        """Test removing fields that don't exist"""
        user = {
            "id": "123",
            "email": "test@example.com"
        }
        
        result = remove_sensitive_fields(user)
        
        assert result["id"] == "123"
        assert result["email"] == "test@example.com"
        # Should not raise error for nonexistent fields
    
    def test_remove_sensitive_fields_empty_user(self):
        """Test with empty user dict"""
        user = {}
        result = remove_sensitive_fields(user)
        assert result == {}
