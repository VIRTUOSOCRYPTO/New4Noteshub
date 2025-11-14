#!/usr/bin/env python3
"""
Automated Backup Scheduler
Schedules and runs database backups with rotation
"""
import sys
import os
import asyncio
from datetime import datetime
import schedule
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.backup_service import backup_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def run_backup():
    """Run backup job"""
    logger.info("Starting scheduled backup...")
    
    try:
        # Run backup
        result = backup_service.create_backup()
        
        if result["success"]:
            logger.info(f"Backup completed successfully: {result['backup_name']} ({result['size_mb']}MB)")
            
            # Cleanup old backups
            cleanup_result = backup_service.cleanup_old_backups()
            if cleanup_result["success"]:
                logger.info(f"Cleanup completed: {cleanup_result['deleted_count']} old backups removed")
        else:
            logger.error(f"Backup failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"Backup job failed: {str(e)}", exc_info=True)


def main():
    """Main scheduler loop"""
    # Get schedule from environment (default: daily at 2 AM)
    backup_time = os.getenv("BACKUP_TIME", "02:00")
    
    logger.info(f"Backup scheduler started (scheduled time: {backup_time})")
    
    # Schedule daily backup
    schedule.every().day.at(backup_time).do(run_backup)
    
    # Also allow manual trigger via BACKUP_ON_START env var
    if os.getenv("BACKUP_ON_START", "false").lower() == "true":
        logger.info("Running initial backup...")
        run_backup()
    
    # Run scheduler
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Backup scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
