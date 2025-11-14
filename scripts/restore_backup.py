#!/usr/bin/env python3
"""
Backup Restore Script
Restore MongoDB database from a backup
"""
import sys
import os
import argparse

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


def list_backups():
    """List available backups"""
    backups = backup_service.list_backups()
    
    if not backups:
        print("\nNo backups found.\n")
        return
    
    print("\n" + "="*80)
    print("Available Backups")
    print("="*80)
    
    for i, backup in enumerate(backups, 1):
        print(f"\n{i}. {backup['name']}")
        print(f"   Size: {backup['size_mb']}MB")
        print(f"   Created: {backup['created_at']}")
        print(f"   Type: {backup['type']}")
    
    print("\n" + "="*80 + "\n")


def restore_backup(backup_name: str, confirm: bool = False):
    """Restore from a backup"""
    # Check if backup exists
    backups = backup_service.list_backups()
    backup = next((b for b in backups if b['name'] == backup_name or backup_name in b['name']), None)
    
    if not backup:
        logger.error(f"Backup not found: {backup_name}")
        print("\nAvailable backups:")
        for b in backups:
            print(f"  - {b['name']}")
        return False
    
    # Confirm restore
    if not confirm:
        print("\n" + "⚠"*40)
        print("WARNING: This will DROP all existing data and restore from backup!")
        print("⚠"*40)
        print(f"\nBackup to restore: {backup['name']}")
        print(f"Size: {backup['size_mb']}MB")
        print(f"Created: {backup['created_at']}")
        
        response = input("\nAre you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("\nRestore cancelled.\n")
            return False
    
    logger.info(f"Starting restore from: {backup['name']}")
    
    result = backup_service.restore_backup(backup['name'])
    
    if result["success"]:
        logger.info(f"Restore completed successfully")
        print("\n✅ Database restored successfully!\n")
        return True
    else:
        logger.error(f"Restore failed: {result.get('error', 'Unknown error')}")
        print(f"\n❌ Restore failed: {result.get('error')}\n")
        return False


def main():
    parser = argparse.ArgumentParser(description='MongoDB Backup Restore Tool')
    parser.add_argument('action', choices=['list', 'restore'], help='Action to perform')
    parser.add_argument('--backup', help='Backup name to restore')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_backups()
    
    elif args.action == 'restore':
        if not args.backup:
            print("Error: --backup argument required for restore")
            print("\nUsage: python restore_backup.py restore --backup <backup_name>")
            list_backups()
            sys.exit(1)
        
        success = restore_backup(args.backup, args.yes)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
