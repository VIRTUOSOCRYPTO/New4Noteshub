"""
Serialization utilities
"""

from typing import Any, Dict, List, Optional


def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Convert MongoDB ObjectId to string"""
    if not doc:
        return None
    
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    
    return doc


def serialize_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert list of MongoDB documents"""
    return [serialize_doc(doc) for doc in docs]


def remove_sensitive_fields(user: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive fields from user object"""
    sensitive_fields = [
        "password_hash",
        "two_factor_secret",
        "refresh_token",
        "reset_token",
        "reset_token_expiry"
    ]
    
    for field in sensitive_fields:
        user.pop(field, None)
    
    return user
