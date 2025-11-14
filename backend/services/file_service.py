"""
File Service
Handles file upload, validation, and storage operations
"""

import os
import secrets
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile

from exceptions import FileUploadError, ValidationError


class FileService:
    """Service for file-related operations"""
    
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.md'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, upload_dir: str = "uploads/notes"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def validate_file(self, file: UploadFile) -> None:
        """Validate file type and prepare for upload"""
        if not file.filename:
            raise FileUploadError("No filename provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise FileUploadError(
                f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}",
                details={"allowed_types": list(self.ALLOWED_EXTENSIONS)}
            )
    
    async def save_file(self, file: UploadFile) -> Tuple[str, str]:
        """
        Save uploaded file and return (unique_filename, original_filename)
        
        Args:
            file: The uploaded file
            
        Returns:
            Tuple of (unique_filename, original_filename)
            
        Raises:
            FileUploadError: If file is too large or save fails
        """
        # Validate file type
        self.validate_file(file)
        
        # Read file content
        contents = await file.read()
        
        # Check file size
        if len(contents) > self.MAX_FILE_SIZE:
            raise FileUploadError(
                f"File too large. Maximum size: {self.MAX_FILE_SIZE / 1024 / 1024}MB",
                details={"max_size_mb": self.MAX_FILE_SIZE / 1024 / 1024}
            )
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{secrets.token_urlsafe(16)}{file_ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        try:
            with open(file_path, "wb") as f:
                f.write(contents)
        except Exception as e:
            raise FileUploadError(f"Failed to save file: {str(e)}")
        
        return unique_filename, file.filename
    
    def get_file_path(self, filename: str) -> str:
        """Get full path to a file"""
        return os.path.join(self.upload_dir, filename)
    
    def file_exists(self, filename: str) -> bool:
        """Check if file exists"""
        return os.path.exists(self.get_file_path(filename))
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file
        
        Returns:
            True if file was deleted, False if file didn't exist
        """
        file_path = self.get_file_path(filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False


# Singleton instance
_file_service = None

def get_file_service(upload_dir: str = "uploads/notes") -> FileService:
    """Get file service instance"""
    global _file_service
    if _file_service is None:
        _file_service = FileService(upload_dir)
    return _file_service
