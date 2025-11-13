"""
Validation utilities
"""

import re
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException

from models import DEPARTMENT_CODES

# File validation constants
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']


def validate_file(file: UploadFile, allowed_extensions: set = ALLOWED_EXTENSIONS) -> bool:
    """Validate file extension"""
    if not file.filename:
        return False
    
    file_ext = Path(file.filename).suffix.lower()
    return file_ext in allowed_extensions


def validate_file_size(content: bytes, max_size: int = MAX_FILE_SIZE) -> bool:
    """Validate file size"""
    return len(content) <= max_size


def validate_image_type(content_type: str) -> bool:
    """Validate image content type"""
    return content_type in ALLOWED_IMAGE_TYPES


def validate_usn_department(usn: str, department: str) -> Optional[str]:
    """
    Validate that USN department code matches selected department
    Returns error message if invalid, None if valid
    """
    usn_upper = usn.upper()
    standard_pattern = re.compile(r'^[0-9][A-Za-z]{2}[0-9]{2}([A-Za-z]{2})[0-9]{3}$')
    short_pattern = re.compile(r'^[0-9]{2}([A-Za-z]{2})[0-9]{3}$')
    
    match = standard_pattern.match(usn_upper) or short_pattern.match(usn_upper)
    if match:
        usn_dept_code = match.group(1)
        expected_dept = DEPARTMENT_CODES.get(usn_dept_code)
        if expected_dept and expected_dept != department:
            return f"USN department code '{usn_dept_code}' doesn't match selected department '{department}'"
    
    return None


def validate_filename_format(filename: str, pattern: str) -> bool:
    """Validate filename against a regex pattern"""
    return bool(re.match(pattern, filename, re.IGNORECASE))
