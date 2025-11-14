"""
Virus Scanning Service
Integrates with ClamAV for file security scanning
"""
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging
import hashlib
import time

logger = logging.getLogger(__name__)


class VirusScanner:
    """
    Virus scanning service using ClamAV
    Falls back to basic file validation if ClamAV is unavailable
    """
    
    # Suspicious file signatures (basic fallback detection)
    SUSPICIOUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs',
        '.js', '.jar', '.msi', '.app', '.deb', '.rpm', '.sh'
    }
    
    # Maximum file size for scanning (100MB)
    MAX_SCAN_SIZE = 100 * 1024 * 1024
    
    def __init__(self):
        self.enabled = os.getenv("VIRUS_SCAN_ENABLED", "true").lower() == "true"
        self.clamav_available = self._check_clamav()
        self.quarantine_dir = os.getenv("QUARANTINE_DIR", "/app/quarantine")
        
        # Create quarantine directory
        Path(self.quarantine_dir).mkdir(parents=True, exist_ok=True)
        
        scan_mode = "ClamAV" if self.clamav_available else "basic validation"
        logger.info(f"Virus scanner initialized (enabled: {self.enabled}, mode: {scan_mode})")
    
    def _check_clamav(self) -> bool:
        """Check if ClamAV is installed and running"""
        try:
            result = subprocess.run(
                ["clamscan", "--version"],
                capture_output=True,
                timeout=5
            )
            available = result.returncode == 0
            if available:
                logger.info("ClamAV detected and available")
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("ClamAV not available, using basic file validation")
            return False
    
    async def scan_file(self, file_path: str) -> Dict[str, any]:
        """
        Scan a file for viruses and malware
        
        Args:
            file_path: Path to file to scan
        
        Returns:
            Dictionary with scan results
        """
        if not self.enabled:
            return {
                "safe": True,
                "scanned": False,
                "message": "Virus scanning disabled"
            }
        
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return {
                "safe": False,
                "scanned": False,
                "error": "File not found"
            }
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.MAX_SCAN_SIZE:
            logger.warning(f"File too large for scanning: {file_size} bytes")
            return {
                "safe": True,
                "scanned": False,
                "message": "File too large for scanning",
                "size_bytes": file_size
            }
        
        # Basic validation first
        basic_check = self._basic_validation(file_path)
        if not basic_check["safe"]:
            return basic_check
        
        # ClamAV scan if available
        if self.clamav_available:
            return await self._clamav_scan(file_path)
        else:
            return {
                "safe": True,
                "scanned": True,
                "method": "basic_validation",
                "message": "ClamAV not available, basic validation passed"
            }
    
    def _basic_validation(self, file_path: Path) -> Dict[str, any]:
        """
        Perform basic file validation
        
        Returns:
            Dictionary with validation results
        """
        # Check suspicious extensions
        if file_path.suffix.lower() in self.SUSPICIOUS_EXTENSIONS:
            logger.warning(f"Suspicious file extension detected: {file_path.suffix}")
            self._quarantine_file(file_path, "suspicious_extension")
            return {
                "safe": False,
                "scanned": True,
                "method": "basic_validation",
                "threat_type": "suspicious_extension",
                "message": f"File extension {file_path.suffix} is not allowed"
            }
        
        # Check for null bytes (potential exploit)
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Check first 1KB
                if b'\x00' in content and file_path.suffix in ['.txt', '.md', '.csv']:
                    logger.warning("Null bytes detected in text file")
                    self._quarantine_file(file_path, "null_bytes")
                    return {
                        "safe": False,
                        "scanned": True,
                        "method": "basic_validation",
                        "threat_type": "null_bytes",
                        "message": "Suspicious content detected"
                    }
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return {
                "safe": False,
                "scanned": False,
                "error": f"File read error: {str(e)}"
            }
        
        return {"safe": True, "scanned": True, "method": "basic_validation"}
    
    async def _clamav_scan(self, file_path: Path) -> Dict[str, any]:
        """
        Scan file using ClamAV
        
        Returns:
            Dictionary with scan results
        """
        try:
            start_time = time.time()
            
            # Run clamscan
            result = subprocess.run(
                ["clamscan", "--no-summary", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            scan_duration = time.time() - start_time
            
            # ClamAV returns:
            # 0 - No virus found
            # 1 - Virus found
            # 2 - Error
            
            if result.returncode == 0:
                return {
                    "safe": True,
                    "scanned": True,
                    "method": "clamav",
                    "scan_duration": round(scan_duration, 2),
                    "message": "No threats detected"
                }
            elif result.returncode == 1:
                # Virus detected
                threat_info = result.stdout.strip()
                logger.error(f"VIRUS DETECTED: {file_path} - {threat_info}")
                
                # Quarantine the file
                self._quarantine_file(file_path, "virus_detected")
                
                return {
                    "safe": False,
                    "scanned": True,
                    "method": "clamav",
                    "threat_type": "virus",
                    "threat_info": threat_info,
                    "scan_duration": round(scan_duration, 2),
                    "message": "Threat detected and quarantined"
                }
            else:
                # Scan error
                logger.error(f"ClamAV scan error: {result.stderr}")
                return {
                    "safe": False,
                    "scanned": False,
                    "error": result.stderr,
                    "message": "Scan error occurred"
                }
        
        except subprocess.TimeoutExpired:
            logger.error("ClamAV scan timeout")
            return {
                "safe": False,
                "scanned": False,
                "error": "Scan timeout"
            }
        except Exception as e:
            logger.error(f"ClamAV scan failed: {str(e)}", exc_info=True)
            return {
                "safe": False,
                "scanned": False,
                "error": str(e)
            }
    
    def _quarantine_file(self, file_path: Path, reason: str):
        """
        Move infected/suspicious file to quarantine
        
        Args:
            file_path: Path to file
            reason: Reason for quarantine
        """
        try:
            # Generate quarantine filename with hash
            file_hash = self._calculate_file_hash(file_path)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            quarantine_name = f"{timestamp}_{file_hash}_{reason}{file_path.suffix}"
            quarantine_path = Path(self.quarantine_dir) / quarantine_name
            
            # Move file to quarantine
            file_path.rename(quarantine_path)
            
            # Create metadata file
            metadata_path = quarantine_path.with_suffix(quarantine_path.suffix + ".meta")
            with open(metadata_path, 'w') as f:
                f.write(f"Original Path: {file_path}\n")
                f.write(f"Reason: {reason}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Hash: {file_hash}\n")
            
            logger.info(f"File quarantined: {quarantine_name}")
            
        except Exception as e:
            logger.error(f"Failed to quarantine file: {str(e)}", exc_info=True)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]
    
    def get_quarantine_stats(self) -> Dict[str, any]:
        """
        Get quarantine statistics
        
        Returns:
            Dictionary with quarantine stats
        """
        quarantine_dir = Path(self.quarantine_dir)
        
        if not quarantine_dir.exists():
            return {
                "total_files": 0,
                "total_size_mb": 0,
                "files": []
            }
        
        files = []
        total_size = 0
        
        for item in quarantine_dir.iterdir():
            if item.is_file() and not item.suffix == ".meta":
                stat = item.stat()
                total_size += stat.st_size
                files.append({
                    "name": item.name,
                    "size_bytes": stat.st_size,
                    "quarantined_at": time.ctime(stat.st_ctime)
                })
        
        return {
            "total_files": len(files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files": files
        }


# Global virus scanner instance
virus_scanner = VirusScanner()
