"""
Cloud Storage Service using Supabase Storage
Handles file uploads with security and validation
"""
from typing import Optional, Dict, BinaryIO
import os
import secrets
from pathlib import Path
import mimetypes


class StorageService:
    """
    Cloud storage service with Supabase backend
    Falls back to local storage if Supabase is not configured
    """
    
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.md'}
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.storage_enabled = False
        self.client = None
        
        if self.supabase_url and self.supabase_key:
            self._initialize_supabase()
        else:
            print("⚠ Supabase not configured, using local file storage")
    
    def _initialize_supabase(self):
        """Initialize Supabase client"""
        try:
            from supabase import create_client, Client
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            self.storage_enabled = True
            print("✓ Supabase storage initialized successfully")
        except ImportError:
            print("⚠ Supabase library not installed, using local storage")
            self.storage_enabled = False
        except Exception as e:
            print(f"⚠ Supabase initialization failed: {e}, using local storage")
            self.storage_enabled = False
    
    def validate_file(
        self,
        filename: str,
        file_size: int,
        allowed_extensions: set = None,
        max_size: int = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate file before upload
        
        Returns:
            (is_valid, error_message)
        """
        if allowed_extensions is None:
            allowed_extensions = self.ALLOWED_EXTENSIONS
        
        if max_size is None:
            max_size = self.MAX_FILE_SIZE
        
        # Check extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check size
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_size_mb}MB"
        
        # Check for suspicious patterns in filename
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename"
        
        return True, None
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename"""
        file_ext = Path(original_filename).suffix.lower()
        unique_id = secrets.token_urlsafe(16)
        return f"{unique_id}{file_ext}"
    
    async def upload_note(
        self,
        file_content: bytes,
        original_filename: str,
        user_id: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Upload a note file
        
        Returns:
            (success, file_path_or_url, error_message)
        """
        # Validate file
        is_valid, error = self.validate_file(
            original_filename,
            len(file_content),
            self.ALLOWED_EXTENSIONS,
            self.MAX_FILE_SIZE
        )
        
        if not is_valid:
            return False, None, error
        
        unique_filename = self.generate_unique_filename(original_filename)
        
        if self.storage_enabled and self.client:
            try:
                # Upload to Supabase Storage
                bucket_name = "notes"
                file_path = f"{user_id}/{unique_filename}"
                
                # Create bucket if it doesn't exist
                try:
                    self.client.storage.create_bucket(bucket_name, {"public": False})
                except:
                    pass  # Bucket likely already exists
                
                # Upload file
                result = self.client.storage.from_(bucket_name).upload(
                    file_path,
                    file_content,
                    {"content-type": mimetypes.guess_type(original_filename)[0] or "application/octet-stream"}
                )
                
                # Get public URL (for signed URLs in production)
                file_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
                
                return True, file_url, None
                
            except Exception as e:
                print(f"Supabase upload failed: {e}, falling back to local storage")
                # Fall back to local storage
        
        # Local storage fallback
        try:
            local_path = f"uploads/notes/{unique_filename}"
            os.makedirs("uploads/notes", exist_ok=True)
            
            with open(local_path, "wb") as f:
                f.write(file_content)
            
            return True, unique_filename, None
            
        except Exception as e:
            return False, None, f"Upload failed: {str(e)}"
    
    async def upload_profile_picture(
        self,
        file_content: bytes,
        original_filename: str,
        user_id: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Upload a profile picture
        
        Returns:
            (success, file_path_or_url, error_message)
        """
        # Validate file
        is_valid, error = self.validate_file(
            original_filename,
            len(file_content),
            self.ALLOWED_IMAGE_EXTENSIONS,
            self.MAX_IMAGE_SIZE
        )
        
        if not is_valid:
            return False, None, error
        
        unique_filename = f"profile_{secrets.token_urlsafe(16)}{Path(original_filename).suffix}"
        
        if self.storage_enabled and self.client:
            try:
                # Upload to Supabase Storage
                bucket_name = "profile-pictures"
                file_path = f"{user_id}/{unique_filename}"
                
                # Create bucket if it doesn't exist
                try:
                    self.client.storage.create_bucket(bucket_name, {"public": True})
                except:
                    pass  # Bucket likely already exists
                
                # Upload file
                result = self.client.storage.from_(bucket_name).upload(
                    file_path,
                    file_content,
                    {"content-type": mimetypes.guess_type(original_filename)[0] or "image/jpeg"}
                )
                
                # Get public URL
                file_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
                
                return True, file_url, None
                
            except Exception as e:
                print(f"Supabase upload failed: {e}, falling back to local storage")
                # Fall back to local storage
        
        # Local storage fallback
        try:
            local_path = f"uploads/profile/{unique_filename}"
            os.makedirs("uploads/profile", exist_ok=True)
            
            with open(local_path, "wb") as f:
                f.write(file_content)
            
            return True, unique_filename, None
            
        except Exception as e:
            return False, None, f"Upload failed: {str(e)}"
    
    async def delete_file(self, file_path: str, bucket: str = "notes") -> bool:
        """Delete a file from storage"""
        if self.storage_enabled and self.client:
            try:
                self.client.storage.from_(bucket).remove([file_path])
                return True
            except Exception as e:
                print(f"Supabase delete failed: {e}")
                return False
        else:
            # Local storage
            try:
                local_path = f"uploads/{bucket}/{file_path}"
                if os.path.exists(local_path):
                    os.remove(local_path)
                return True
            except Exception as e:
                print(f"Local delete failed: {e}")
                return False
    
    async def get_signed_url(
        self,
        file_path: str,
        bucket: str = "notes",
        expires_in: int = 3600
    ) -> Optional[str]:
        """
        Get a signed URL for secure file access
        
        Args:
            file_path: Path to file in storage
            bucket: Bucket name
            expires_in: URL expiration time in seconds (default: 1 hour)
        """
        if self.storage_enabled and self.client:
            try:
                result = self.client.storage.from_(bucket).create_signed_url(
                    file_path,
                    expires_in
                )
                return result.get("signedURL")
            except Exception as e:
                print(f"Failed to generate signed URL: {e}")
                return None
        else:
            # For local storage, just return the file path
            return f"/api/files/{bucket}/{file_path}"


# Global storage service instance
storage_service = StorageService()
