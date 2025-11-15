"""
Comprehensive tests for validators
"""

import pytest
from unittest.mock import Mock
from pathlib import Path

import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from utils.validators import (
    validate_file,
    validate_file_size,
    validate_image_type,
    validate_usn_department,
    validate_filename_format,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    MAX_IMAGE_SIZE,
    ALLOWED_IMAGE_TYPES
)


class TestFileValidation:
    """Test file validation functions"""
    
    def test_validate_file_with_allowed_extension(self):
        """Test file with allowed extension passes validation"""
        mock_file = Mock()
        mock_file.filename = "document.pdf"
        
        result = validate_file(mock_file)
        assert result is True
    
    def test_validate_file_with_disallowed_extension(self):
        """Test file with disallowed extension fails validation"""
        mock_file = Mock()
        mock_file.filename = "virus.exe"
        
        result = validate_file(mock_file)
        assert result is False
    
    def test_validate_file_with_no_filename(self):
        """Test file with no filename fails validation"""
        mock_file = Mock()
        mock_file.filename = None
        
        result = validate_file(mock_file)
        assert result is False
    
    def test_validate_file_with_custom_extensions(self):
        """Test file validation with custom allowed extensions"""
        mock_file = Mock()
        mock_file.filename = "image.jpg"
        
        custom_extensions = {'.jpg', '.png'}
        result = validate_file(mock_file, allowed_extensions=custom_extensions)
        assert result is True
    
    def test_validate_file_case_insensitive(self):
        """Test file extension validation is case insensitive"""
        mock_file = Mock()
        mock_file.filename = "document.PDF"
        
        result = validate_file(mock_file)
        assert result is True
    
    def test_validate_file_size_within_limit(self):
        """Test file size within limit passes validation"""
        content = b"a" * (5 * 1024 * 1024)  # 5MB
        
        result = validate_file_size(content)
        assert result is True
    
    def test_validate_file_size_exceeds_limit(self):
        """Test file size exceeding limit fails validation"""
        content = b"a" * (15 * 1024 * 1024)  # 15MB (exceeds 10MB limit)
        
        result = validate_file_size(content)
        assert result is False
    
    def test_validate_file_size_custom_limit(self):
        """Test file size validation with custom limit"""
        content = b"a" * (2 * 1024 * 1024)  # 2MB
        custom_limit = 1 * 1024 * 1024  # 1MB limit
        
        result = validate_file_size(content, max_size=custom_limit)
        assert result is False


class TestImageValidation:
    """Test image validation functions"""
    
    def test_validate_image_type_jpeg(self):
        """Test JPEG image type passes validation"""
        result = validate_image_type("image/jpeg")
        assert result is True
    
    def test_validate_image_type_png(self):
        """Test PNG image type passes validation"""
        result = validate_image_type("image/png")
        assert result is True
    
    def test_validate_image_type_invalid(self):
        """Test invalid image type fails validation"""
        result = validate_image_type("image/bmp")
        assert result is False
    
    def test_validate_image_type_non_image(self):
        """Test non-image content type fails validation"""
        result = validate_image_type("application/pdf")
        assert result is False


class TestUSNDepartmentValidation:
    """Test USN and department validation"""
    
    def test_validate_usn_matching_department(self):
        """Test USN with matching department code"""
        usn = "1RV21CS001"
        department = "CSE"
        
        result = validate_usn_department(usn, department)
        assert result is None  # No error
    
    def test_validate_usn_mismatched_department(self):
        """Test USN with mismatched department code"""
        usn = "1RV21CS001"
        department = "ECE"
        
        result = validate_usn_department(usn, department)
        assert result is not None  # Error message returned
        assert "CS" in result
        assert "ECE" in result
    
    def test_validate_usn_case_insensitive(self):
        """Test USN validation is case insensitive"""
        usn = "1rv21cs001"  # lowercase
        department = "CSE"
        
        result = validate_usn_department(usn, department)
        assert result is None
    
    def test_validate_usn_short_format(self):
        """Test USN in short format (e.g., 22CS001)"""
        usn = "22CS001"
        department = "CSE"
        
        result = validate_usn_department(usn, department)
        assert result is None
    
    def test_validate_usn_invalid_format(self):
        """Test USN with invalid format returns None (no validation)"""
        usn = "INVALID"
        department = "CSE"
        
        result = validate_usn_department(usn, department)
        assert result is None  # Invalid format doesn't trigger department check
    
    def test_validate_usn_unknown_department_code(self):
        """Test USN with unknown department code"""
        usn = "1RV21XX001"  # XX is not in DEPARTMENT_CODES
        department = "CSE"
        
        result = validate_usn_department(usn, department)
        assert result is None  # Unknown codes don't trigger error


class TestFilenameFormatValidation:
    """Test filename format validation"""
    
    def test_validate_filename_simple_pattern(self):
        """Test filename matches simple pattern"""
        filename = "document.pdf"
        pattern = r".*\.pdf$"
        
        result = validate_filename_format(filename, pattern)
        assert result is True
    
    def test_validate_filename_complex_pattern(self):
        """Test filename matches complex pattern"""
        filename = "CS101_Notes_2023.pdf"
        pattern = r"^[A-Z]{2}\d{3}_.*\.pdf$"
        
        result = validate_filename_format(filename, pattern)
        assert result is True
    
    def test_validate_filename_pattern_mismatch(self):
        """Test filename doesn't match pattern"""
        filename = "document.txt"
        pattern = r".*\.pdf$"
        
        result = validate_filename_format(filename, pattern)
        assert result is False
    
    def test_validate_filename_case_insensitive(self):
        """Test filename validation is case insensitive"""
        filename = "DOCUMENT.PDF"
        pattern = r".*\.pdf$"
        
        result = validate_filename_format(filename, pattern)
        assert result is True
