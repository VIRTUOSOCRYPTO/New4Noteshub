"""
MongoDB Backup Service
Handles automated backups with rotation and cloud storage
"""
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import shutil
import tarfile
import logging

logger = logging.getLogger(__name__)


class BackupService:
    """
    MongoDB backup service with automated scheduling and rotation
    Supports local and cloud storage backends
    """
    
    def __init__(self):
        self.backup_dir = os.getenv("BACKUP_DIR", "/app/backups")
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/noteshub")
        self.retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))
        self.compression_enabled = os.getenv("BACKUP_COMPRESSION", "true").lower() == "true"
        
        # Cloud storage config (S3-compatible)
        self.cloud_enabled = os.getenv("BACKUP_CLOUD_ENABLED", "false").lower() == "true"
        self.s3_bucket = os.getenv("BACKUP_S3_BUCKET")
        self.s3_endpoint = os.getenv("BACKUP_S3_ENDPOINT")
        self.s3_access_key = os.getenv("BACKUP_S3_ACCESS_KEY")
        self.s3_secret_key = os.getenv("BACKUP_S3_SECRET_KEY")
        
        # Create backup directory
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Backup service initialized (retention: {self.retention_days} days, cloud: {self.cloud_enabled})")
    
    def create_backup(self, backup_name: Optional[str] = None) -> Dict[str, any]:
        """
        Create a full MongoDB backup
        
        Returns:
            Dictionary with backup details
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_name or f"noteshub_backup_{timestamp}"
            backup_path = Path(self.backup_dir) / backup_name
            
            logger.info(f"Starting backup: {backup_name}")
            
            # Create backup using mongodump
            dump_command = [
                "mongodump",
                f"--uri={self.mongo_url}",
                f"--out={backup_path}",
                "--gzip" if self.compression_enabled else ""
            ]
            
            # Remove empty strings from command
            dump_command = [cmd for cmd in dump_command if cmd]
            
            result = subprocess.run(
                dump_command,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Backup failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "backup_name": backup_name
                }
            
            # Get backup size
            backup_size = self._get_directory_size(backup_path)
            
            # Create tarball if compression enabled
            if self.compression_enabled:
                tar_path = f"{backup_path}.tar.gz"
                self._create_tarball(backup_path, tar_path)
                backup_size = os.path.getsize(tar_path)
                # Remove uncompressed directory
                shutil.rmtree(backup_path)
                backup_path = Path(tar_path)
            
            backup_info = {
                "success": True,
                "backup_name": backup_name,
                "path": str(backup_path),
                "size_bytes": backup_size,
                "size_mb": round(backup_size / (1024 * 1024), 2),
                "timestamp": timestamp,
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Backup completed: {backup_name} ({backup_info['size_mb']}MB)")
            
            # Upload to cloud if enabled
            if self.cloud_enabled:
                cloud_result = self._upload_to_cloud(backup_path)
                backup_info["cloud_uploaded"] = cloud_result
            
            return backup_info
            
        except subprocess.TimeoutExpired:
            logger.error("Backup timeout exceeded")
            return {"success": False, "error": "Backup timeout exceeded"}
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def restore_backup(self, backup_name: str) -> Dict[str, any]:
        """
        Restore from a backup
        
        Args:
            backup_name: Name of backup to restore
        
        Returns:
            Dictionary with restore details
        """
        try:
            backup_path = Path(self.backup_dir) / backup_name
            
            # Check if it's a tarball
            if not backup_path.exists():
                tar_path = Path(f"{backup_path}.tar.gz")
                if tar_path.exists():
                    logger.info(f"Extracting tarball: {tar_path}")
                    self._extract_tarball(tar_path, backup_path)
                else:
                    return {"success": False, "error": "Backup not found"}
            
            logger.info(f"Starting restore from: {backup_name}")
            
            # Restore using mongorestore
            restore_command = [
                "mongorestore",
                f"--uri={self.mongo_url}",
                f"{backup_path}",
                "--gzip" if self.compression_enabled else "",
                "--drop"  # Drop existing collections before restore
            ]
            
            # Remove empty strings
            restore_command = [cmd for cmd in restore_command if cmd]
            
            result = subprocess.run(
                restore_command,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                logger.error(f"Restore failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
            
            logger.info(f"Restore completed: {backup_name}")
            return {
                "success": True,
                "backup_name": backup_name,
                "restored_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def list_backups(self) -> List[Dict[str, any]]:
        """
        List all available backups
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        backup_dir = Path(self.backup_dir)
        
        if not backup_dir.exists():
            return backups
        
        for item in backup_dir.iterdir():
            if item.is_dir() or item.suffix == ".gz":
                stat = item.stat()
                backups.append({
                    "name": item.name,
                    "path": str(item),
                    "size_bytes": stat.st_size if item.is_file() else self._get_directory_size(item),
                    "size_mb": round(stat.st_size / (1024 * 1024), 2) if item.is_file() else round(self._get_directory_size(item) / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "type": "compressed" if item.suffix == ".gz" else "directory"
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups
    
    def cleanup_old_backups(self) -> Dict[str, any]:
        """
        Remove backups older than retention period
        
        Returns:
            Dictionary with cleanup details
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            deleted_count = 0
            freed_space = 0
            
            backup_dir = Path(self.backup_dir)
            
            for item in backup_dir.iterdir():
                if item.is_dir() or item.suffix == ".gz":
                    created_time = datetime.fromtimestamp(item.stat().st_ctime)
                    
                    if created_time < cutoff_date:
                        size = item.stat().st_size if item.is_file() else self._get_directory_size(item)
                        
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                        
                        deleted_count += 1
                        freed_space += size
                        logger.info(f"Deleted old backup: {item.name}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "freed_space_mb": round(freed_space / (1024 * 1024), 2),
                "retention_days": self.retention_days
            }
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory"""
        total = 0
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
        return total
    
    def _create_tarball(self, source_dir: Path, tar_path: str):
        """Create compressed tarball"""
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(source_dir, arcname=source_dir.name)
    
    def _extract_tarball(self, tar_path: Path, dest_dir: Path):
        """Extract tarball"""
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(dest_dir.parent)
    
    def _upload_to_cloud(self, backup_path: Path) -> bool:
        """
        Upload backup to S3-compatible cloud storage
        
        Returns:
            True if upload successful
        """
        if not self.cloud_enabled:
            return False
        
        try:
            import boto3
            from botocore.client import Config
            
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                endpoint_url=self.s3_endpoint,
                aws_access_key_id=self.s3_access_key,
                aws_secret_access_key=self.s3_secret_key,
                config=Config(signature_version='s3v4')
            )
            
            # Upload file
            s3_key = f"backups/{backup_path.name}"
            s3_client.upload_file(
                str(backup_path),
                self.s3_bucket,
                s3_key
            )
            
            logger.info(f"Backup uploaded to cloud: {s3_key}")
            return True
            
        except ImportError:
            logger.warning("boto3 not installed, skipping cloud upload")
            return False
        except Exception as e:
            logger.error(f"Cloud upload failed: {str(e)}")
            return False


# Global backup service instance
backup_service = BackupService()
