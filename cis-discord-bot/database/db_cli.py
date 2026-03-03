#!/usr/bin/env python3
"""
Database Utility CLI
Story 4.7 Implementation: StudentContext & Database Schema
Task 1.2: Database utility CLI (backup, restore, migrate commands)

Unified command-line interface for database operations:
- Backup: Create automated backups with retention
- Restore: Restore from backup files
- Migrate: SQLite → PostgreSQL migration
- Status: View database and backup status
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from database.backup import DatabaseBackup, backup_all_cohorts
from database.migration import DatabaseMigration, migrate_all_cohorts


def cmd_backup(args):
    """Create database backup"""
    backup_mgr = DatabaseBackup(
        db_path=args.database,
        backup_dir=args.backup_dir,
        retention_days=args.retention
    )

    print(f"Creating backup of: {args.database}")

    if args.all:
        # Backup all cohorts
        print("Backing up all cohort databases...")
        results = backup_all_cohorts(
            project_root=Path(args.database).parent,
            retention_days=args.retention
        )

        for db_name, result in results.items():
            if result["status"] == "success":
                print(f"  ✅ {db_name}: {result['backup_path']}")
                if result.get("cleaned_up", 0) > 0:
                    print(f"     Cleaned up {result['cleaned_up']} old backups")
            else:
                print(f"  ❌ {db_name}: {result.get('error', 'Unknown error')}")
    else:
        # Backup single database
        backup_path = backup_mgr.create_backup()
        print(f"  ✅ Backup created: {backup_path}")

        # Cleanup old backups
        if args.cleanup:
            deleted = backup_mgr.cleanup_old_backups()
            print(f"  🗑️  Cleaned up {len(deleted)} old backups")


def cmd_restore(args):
    """Restore database from backup"""
    backup_mgr = DatabaseBackup(
        db_path=args.database,
        backup_dir=args.backup_dir
    )

    print(f"Restoring {args.database} from: {args.backup}")

    try:
        target = backup_mgr.restore_backup(args.backup, args.target)
        print(f"  ✅ Database restored: {target}")
    except Exception as e:
        print(f"  ❌ Restore failed: {e}")
        sys.exit(1)


def cmd_status(args):
    """Show database and backup status"""
    backup_mgr = DatabaseBackup(
        db_path=args.database,
        backup_dir=args.backup_dir
    )

    # Database info
    db_path = Path(args.database)
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"📦 Database: {args.database}")
        print(f"   Size: {size_mb:.2f} MB")
    else:
        print(f"❌ Database not found: {args.database}")
        sys.exit(1)

    # Backup status
    status = backup_mgr.get_backup_status()

    print(f"\n💾 Backups: {status['backup_dir']}")
    print(f"   Total: {status['total_backups']} backups ({status['total_size_mb']:.2f} MB)")

    if status['latest_backup']:
        print(f"   Latest: {status['latest_backup'].strftime('%Y-%m-%d %H:%M:%S')}")
    if status['oldest_backup']:
        print(f"   Oldest: {status['oldest_backup'].strftime('%Y-%m-%d %H:%M:%S')}")

    # List recent backups
    if args.verbose:
        print(f"\n📋 Recent backups:")
        backups = backup_mgr.list_backups()[:10]  # Last 10

        for backup in backups:
            print(f"  • {backup['name']}")
            print(f"    Size: {backup['size_mb']:.2f} MB | Created: {backup['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")


def cmd_migrate(args):
    """Migrate SQLite to PostgreSQL"""
    if not args.postgres_url:
        print("❌ PostgreSQL URL required (use --postgres-url or POSTGRES_URL env var)")
        sys.exit(1)

    print(f"Migrating: {args.database} -> PostgreSQL")

    try:
        migrator = DatabaseMigration(
            sqlite_path=args.database,
            postgres_url=args.postgres_url
        )

        # Perform migration
        results = migrator.migrate(
            tables=args.tables,
            skip_data=args.schema_only,
            batch_size=args.batch_size
        )

        print("\n✅ Migration completed:")
        for table, count in results.items():
            print(f"  • {table}: {count} rows")

        # Verify
        if args.verify:
            print("\n🔍 Verifying migration...")
            verification = migrator.verify_migration()

            all_verified = all(verification.values())
            for table, status in verification.items():
                symbol = "✅" if status else "❌"
                print(f"  {symbol} {table}")

            if not all_verified:
                print("\n⚠️  Verification failed - some tables have row count mismatches")
                sys.exit(1)

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


def cmd_migrate_all(args):
    """Migrate all cohort databases"""
    if not args.postgres_url:
        print("❌ PostgreSQL URL required (use --postgres-url or POSTGRES_URL env var)")
        sys.exit(1)

    print("Migrating all cohort databases to PostgreSQL...")

    results = migrate_all_cohorts(
        project_root=Path(args.project_root) if args.project_root else None,
        postgres_url=args.postgres_url
    )

    for cohort, result in results.items():
        if result["status"] == "success":
            print(f"✅ {cohort}:")
            for table, count in result["rows_migrated"].items():
                print(f"    • {table}: {count} rows")
        else:
            print(f"❌ {cohort}: {result.get('error', 'Unknown error')}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="K2M CIS Bot Database Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backup single database
  python db_cli.py backup cohort-1.db

  # Backup all cohorts
  python db_cli.py backup --all

  # Restore from backup
  python db_cli.py restore cohort-1.db backups/cohort-1_20260217_143022.db

  # View backup status
  python db_cli.py status cohort-1.db

  # Migrate to PostgreSQL
  python db_cli.py migrate cohort-1.db --postgres-url "postgresql://user:pass@host:5432/db"

  # Migrate all cohorts
  python db_cli.py migrate-all --postgres-url "$POSTGRES_URL"
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ============================================================
    # BACKUP COMMAND
    # ============================================================
    backup_parser = subparsers.add_parser(
        "backup",
        help="Create database backup"
    )

    backup_parser.add_argument(
        "database",
        nargs="?",
        default="cohort-1.db",
        help="Database file to backup (default: cohort-1.db)"
    )

    backup_parser.add_argument(
        "--backup-dir", "-b",
        help="Backup directory (default: {database}.backups/)"
    )

    backup_parser.add_argument(
        "--retention", "-r",
        type=int,
        default=30,
        help="Backup retention period in days (default: 30)"
    )

    backup_parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Backup all cohort databases (cohort-*.db)"
    )

    backup_parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up old backups after creating new one"
    )

    backup_parser.set_defaults(func=cmd_backup)

    # ============================================================
    # RESTORE COMMAND
    # ============================================================
    restore_parser = subparsers.add_parser(
        "restore",
        help="Restore database from backup"
    )

    restore_parser.add_argument(
        "database",
        help="Target database file"
    )

    restore_parser.add_argument(
        "backup",
        help="Backup file to restore from"
    )

    restore_parser.add_argument(
        "--target", "-t",
        help="Optional target path (default: original database path)"
    )

    restore_parser.add_argument(
        "--backup-dir", "-b",
        help="Backup directory (default: {database}.backups/)"
    )

    restore_parser.set_defaults(func=cmd_restore)

    # ============================================================
    # STATUS COMMAND
    # ============================================================
    status_parser = subparsers.add_parser(
        "status",
        help="Show database and backup status"
    )

    status_parser.add_argument(
        "database",
        nargs="?",
        default="cohort-1.db",
        help="Database file to check (default: cohort-1.db)"
    )

    status_parser.add_argument(
        "--backup-dir", "-b",
        help="Backup directory (default: {database}.backups/)"
    )

    status_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed backup listing"
    )

    status_parser.set_defaults(func=cmd_status)

    # ============================================================
    # MIGRATE COMMAND
    # ============================================================
    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Migrate SQLite database to PostgreSQL"
    )

    migrate_parser.add_argument(
        "database",
        help="SQLite database file to migrate"
    )

    migrate_parser.add_argument(
        "--postgres-url", "-p",
        default=None,
        help="PostgreSQL connection URL (or set POSTGRES_URL env var)"
    )

    migrate_parser.add_argument(
        "--tables", "-t",
        nargs="+",
        help="Specific tables to migrate (default: all tables)"
    )

    migrate_parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Migrate schema only, skip data"
    )

    migrate_parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Rows per batch (default: 1000)"
    )

    migrate_parser.add_argument(
        "--verify",
        action="store_true",
        default=True,
        help="Verify migration after completion"
    )

    migrate_parser.set_defaults(func=cmd_migrate)

    # ============================================================
    # MIGRATE-ALL COMMAND
    # ============================================================
    migrate_all_parser = subparsers.add_parser(
        "migrate-all",
        help="Migrate all cohort databases to PostgreSQL"
    )

    migrate_all_parser.add_argument(
        "--postgres-url", "-p",
        default=None,
        help="PostgreSQL connection URL (or set POSTGRES_URL env var)"
    )

    migrate_all_parser.add_argument(
        "--project-root", "-r",
        default=None,
        help="Project root directory (default: current directory)"
    )

    migrate_all_parser.set_defaults(func=cmd_migrate_all)

    # Parse arguments
    args = parser.parse_args()

    # Show help if no command
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
