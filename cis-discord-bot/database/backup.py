"""
Database Backup Utility
Story 4.7 Implementation: StudentContext & Database Schema
Task 1.2: Database backup automation

Provides automated backup with retention policy for SQLite databases.
Supports multi-cohort deployments (cohort-1.db, cohort-2.db, etc.)
"""

import os
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Automated database backup with retention policy"""

    def __init__(
        self,
        db_path: str,
        backup_dir: str = None,
        retention_days: int = 30
    ):
        """
        Initialize backup manager

        Args:
            db_path: Path to SQLite database file
            backup_dir: Directory for backups (default: {db_path}.backups/)
            retention_days: Number of days to retain backups (default: 30)
        """
        self.db_path = Path(db_path)
        self.retention_days = retention_days

        if backup_dir is None:
            self.backup_dir = self.db_path.parent / f"{self.db_path.stem}.backups"
        else:
            self.backup_dir = Path(backup_dir)

        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Backup manager initialized: {self.db_path} -> {self.backup_dir}")

    def create_backup(self, backup_name: str = None) -> Path:
        """
        Create a timestamped backup of the database

        Args:
            backup_name: Optional custom backup name (default: auto-generated timestamp)

        Returns:
            Path to created backup file
        """
        # Verify database exists
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

        # Generate backup filename
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.db_path.stem}_{timestamp}.db"

        backup_path = self.backup_dir / backup_name

        # Create backup using SQLite backup API (more reliable than file copy)
        try:
            # Connect to source database
            source_conn = sqlite3.connect(str(self.db_path))

            # Create backup
            backup_conn = sqlite3.connect(str(backup_path))

            # Use SQLite online backup API
            source_conn.backup(backup_conn)

            # Close connections
            backup_conn.close()
            source_conn.close()

            logger.info(f"Backup created: {backup_path}")
            return backup_path

        except Exception as e:
            # Clean up failed backup
            if backup_path.exists():
                backup_path.unlink()
            logger.error(f"Backup failed: {e}")
            raise

    def cleanup_old_backups(self) -> List[Path]:
        """
        Remove backups older than retention period

        Returns:
            List of deleted backup paths
        """
        if not self.backup_dir.exists():
            return []

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted = []

        for backup_file in self.backup_dir.glob("*.db"):
            try:
                # Extract timestamp from filename
                # Format: cohort-1_20260217_143022.db
                parts = backup_file.stem.split("_")
                if len(parts) >= 3:
                    date_str = f"{parts[1]}_{parts[2]}"
                    backup_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")

                    if backup_date < cutoff_date:
                        backup_file.unlink()
                        deleted.append(backup_file)
                        logger.info(f"Deleted old backup: {backup_file}")

            except (ValueError, IndexError) as e:
                # Skip files that don't match expected format
                logger.warning(f"Skipping unparseable backup file: {backup_file}")
                continue

        return deleted

    def list_backups(self) -> List[dict]:
        """
        List all backups with metadata

        Returns:
            List of backup info dicts (path, size, created_at)
        """
        if not self.backup_dir.exists():
            return []

        backups = []

        for backup_file in sorted(self.backup_dir.glob("*.db"), reverse=True):
            try:
                stat = backup_file.stat()

                # Extract timestamp from filename
                parts = backup_file.stem.split("_")
                if len(parts) >= 3:
                    date_str = f"{parts[1]}_{parts[2]}"
                    created_at = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                else:
                    created_at = datetime.fromtimestamp(stat.st_mtime)

                backups.append({
                    "path": str(backup_file),
                    "name": backup_file.name,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": created_at,
                })

            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping unparseable backup file: {backup_file}")
                continue

        return backups

    def restore_backup(self, backup_path: str, target_path: str = None) -> Path:
        """
        Restore database from backup

        Args:
            backup_path: Path to backup file to restore
            target_path: Optional target path (default: original database path)

        Returns:
            Path to restored database
        """
        backup_file = Path(backup_path)

        if not backup_file.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        if target_path is None:
            target_path = self.db_path
        else:
            target_path = Path(target_path)

        # Verify backup is valid SQLite database
        try:
            test_conn = sqlite3.connect(str(backup_file))
            test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            test_conn.close()
        except sqlite3.DatabaseError as e:
            raise ValueError(f"Invalid SQLite database: {backup_path}") from e

        # Perform restore
        shutil.copy2(backup_file, target_path)

        logger.info(f"Database restored from: {backup_file} -> {target_path}")
        return target_path

    def get_backup_status(self) -> dict:
        """
        Get backup status summary

        Returns:
            Dict with backup status info
        """
        backups = self.list_backups()

        if not backups:
            return {
                "database": str(self.db_path),
                "backup_dir": str(self.backup_dir),
                "total_backups": 0,
                "total_size_mb": 0,
                "latest_backup": None,
                "oldest_backup": None,
            }

        total_size = sum(b["size_mb"] for b in backups)

        return {
            "database": str(self.db_path),
            "backup_dir": str(self.backup_dir),
            "total_backups": len(backups),
            "total_size_mb": round(total_size, 2),
            "latest_backup": backups[0]["created_at"],
            "oldest_backup": backups[-1]["created_at"],
        }


def backup_all_cohorts(
    project_root: Path = None,
    retention_days: int = 30
) -> dict:
    """
    Backup all cohort databases in project

    Args:
        project_root: Project root directory (default: current directory)
        retention_days: Backup retention period

    Returns:
        Dict mapping cohort names to backup results
    """
    if project_root is None:
        project_root = Path.cwd()

    results = {}

    # Find all cohort databases (cohort-*.db pattern)
    for db_file in project_root.glob("cohort-*.db"):
        try:
            backup_mgr = DatabaseBackup(
                db_path=str(db_file),
                retention_days=retention_days
            )

            backup_path = backup_mgr.create_backup()
            deleted = backup_mgr.cleanup_old_backups()

            results[db_file.name] = {
                "status": "success",
                "backup_path": str(backup_path),
                "cleaned_up": len(deleted),
            }

        except Exception as e:
            logger.error(f"Backup failed for {db_file.name}: {e}")
            results[db_file.name] = {
                "status": "failed",
                "error": str(e),
            }

    return results


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "cohort-1.db"

    backup_mgr = DatabaseBackup(db_path=db_path)

    print("Creating backup...")
    backup = backup_mgr.create_backup()
    print(f"Backup created: {backup}")

    print("\nCleaning up old backups...")
    deleted = backup_mgr.cleanup_old_backups()
    print(f"Deleted {len(deleted)} old backups")

    print("\nBackup status:")
    status = backup_mgr.get_backup_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
