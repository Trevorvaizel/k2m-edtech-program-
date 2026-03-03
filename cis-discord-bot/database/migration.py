"""
Database Migration Utility
Story 4.7 Implementation: StudentContext & Database Schema
Task 1.2: Migration strategy (SQLite → PostgreSQL for Cohort 2+)

Provides automated migration from SQLite to PostgreSQL.
Maintains data integrity with transaction rollback on failure.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, Dict, List
import logging

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseMigration:
    """SQLite to PostgreSQL migration with transaction safety"""

    def __init__(
        self,
        sqlite_path: str,
        postgres_url: str,
        postgres_schema: str = "public"
    ):
        """
        Initialize migration manager

        Args:
            sqlite_path: Path to SQLite database file
            postgres_url: PostgreSQL connection URL (postgresql://user:pass@host:port/db)
            postgres_schema: Target schema (default: public)
        """
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for PostgreSQL migration. "
                "Install it with: pip install psycopg2-binary"
            )

        self.sqlite_path = Path(sqlite_path)
        self.postgres_url = postgres_url
        self.postgres_schema = postgres_schema

        # Validate SQLite database exists
        if not self.sqlite_path.exists():
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")

        logger.info(f"Migration initialized: {self.sqlite_path} -> PostgreSQL")

    def _get_sqlite_tables(self) -> List[str]:
        """Get list of tables in SQLite database"""
        conn = sqlite3.connect(str(self.sqlite_path))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]

        conn.close()
        return tables

    def _get_sqlite_schema(self, table_name: str) -> str:
        """Get CREATE TABLE statement from SQLite"""
        conn = sqlite3.connect(str(self.sqlite_path))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE type='table' AND name = ?",
            (table_name,)
        )
        result = cursor.fetchone()

        conn.close()
        return result[0] if result else ""

    def _get_sqlite_data(self, table_name: str) -> List[sqlite3.Row]:
        """Get all data from SQLite table"""
        conn = sqlite3.connect(str(self.sqlite_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        conn.close()
        return rows

    def _convert_sqlite_to_postgres_schema(
        self,
        create_sql: str,
        table_name: str
    ) -> str:
        """
        Convert SQLite CREATE TABLE to PostgreSQL-compatible schema

        Args:
            create_sql: SQLite CREATE TABLE statement
            table_name: Table name

        Returns:
            PostgreSQL CREATE TABLE statement
        """
        # SQLite type mappings to PostgreSQL
        type_mappings = {
            "INTEGER": "INTEGER",
            "TEXT": "TEXT",
            "REAL": "DOUBLE PRECISION",
            "BLOB": "BYTEA",
            "NUMERIC": "NUMERIC",
        }

        # Parse and convert CREATE TABLE statement
        postgres_sql = create_sql

        # Remove SQLite-specific clauses
        postgres_sql = postgres_sql.replace("AUTOINCREMENT", "")
        postgres_sql = postgres_sql.replace("PRIMARY KEY", "PRIMARY KEY")

        # Convert types (simple replacement, works for our schema)
        for sqlite_type, pg_type in type_mappings.items():
            postgres_sql = postgres_sql.replace(f" {sqlite_type}", f" {pg_type}")

        return postgres_sql

    def _create_postgres_table(self, pg_conn, table_name: str):
        """Create table in PostgreSQL"""
        # Get SQLite schema
        sqlite_schema = self._get_sqlite_schema(table_name)

        if not sqlite_schema:
            raise ValueError(f"No schema found for table: {table_name}")

        # Convert to PostgreSQL
        pg_schema = self._convert_sqlite_to_postgres_schema(sqlite_schema, table_name)

        # Execute CREATE TABLE
        cursor = pg_conn.cursor()
        cursor.execute(pg_schema)

        logger.info(f"Created PostgreSQL table: {table_name}")

    def _migrate_table_data(
        self,
        pg_conn,
        table_name: str,
        batch_size: int = 1000
    ):
        """
        Migrate data from SQLite to PostgreSQL

        Args:
            pg_conn: PostgreSQL connection
            table_name: Table to migrate
            batch_size: Rows per batch (default: 1000)
        """
        # Get data from SQLite
        rows = self._get_sqlite_data(table_name)

        if not rows:
            logger.info(f"No data to migrate in table: {table_name}")
            return

        # Get column names
        columns = list(rows[0].keys())

        # Build INSERT statement
        cursor = pg_conn.cursor()

        # Migrate in batches
        total_rows = len(rows)
        migrated = 0

        while migrated < total_rows:
            batch = rows[migrated:migrated + batch_size]

            # Convert rows to list of tuples
            values = [tuple(row[col] for col in columns) for row in batch]

            # Build INSERT query
            placeholders = [sql.Placeholder() for _ in columns]
            insert_query = sql.SQL(
                "INSERT INTO {} ({}) VALUES ({})"
            ).format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(map(sql.Identifier, columns)),
                sql.SQL(", ").join(placeholders)
            )

            # Execute batch insert
            cursor.executemany(insert_query, values)

            migrated += len(batch)
            logger.info(f"Migrated {migrated}/{total_rows} rows in {table_name}")

    def _prepare_postgres_schema(self, pg_conn):
        """Create/select target PostgreSQL schema for migration."""
        cursor = pg_conn.cursor()
        if self.postgres_schema and self.postgres_schema != "public":
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    sql.Identifier(self.postgres_schema)
                )
            )

        cursor.execute(
            sql.SQL("SET search_path TO {}").format(
                sql.Identifier(self.postgres_schema or "public")
            )
        )

    def migrate(
        self,
        tables: Optional[List[str]] = None,
        skip_data: bool = False,
        batch_size: int = 1000
    ) -> Dict[str, int]:
        """
        Perform full migration from SQLite to PostgreSQL

        Args:
            tables: List of tables to migrate (default: all tables)
            skip_data: If True, only migrate schema (default: False)
            batch_size: Rows per batch for data migration

        Returns:
            Dict mapping table names to row counts migrated
        """
        results = {}

        try:
            # Connect to PostgreSQL
            pg_conn = psycopg2.connect(self.postgres_url)
            pg_conn.autocommit = False  # Transactional
            self._prepare_postgres_schema(pg_conn)

            # Get tables to migrate
            if tables is None:
                tables = self._get_sqlite_tables()

            logger.info(f"Migrating {len(tables)} tables: {', '.join(tables)}")

            # Migrate each table
            for table_name in tables:
                logger.info(f"Migrating table: {table_name}")

                # Create table
                self._create_postgres_table(pg_conn, table_name)

                # Migrate data (if not skipped)
                if not skip_data:
                    self._migrate_table_data(
                        pg_conn,
                        table_name,
                        batch_size=batch_size
                    )

                    # Count migrated rows
                    cursor = pg_conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    results[table_name] = row_count

                else:
                    results[table_name] = 0

            # Create indexes
            self._create_indexes(pg_conn, tables)

            # Commit transaction
            pg_conn.commit()
            logger.info("Migration completed successfully")

            return results

        except Exception as e:
            # Rollback on error
            if 'pg_conn' in locals():
                pg_conn.rollback()
            logger.error(f"Migration failed: {e}")
            raise

        finally:
            if 'pg_conn' in locals():
                pg_conn.close()

    def _create_indexes(self, pg_conn, tables: List[str]):
        """Create indexes from SQLite schema"""
        # For our schema, indexes are simple
        # This is a simplified version - production would parse SQLite index definitions

        index_definitions = {
            "students": [
                "CREATE INDEX IF NOT EXISTS idx_students_cohort ON students(cohort_id)",
                "CREATE INDEX IF NOT EXISTS idx_students_week ON students(current_week)",
                "CREATE INDEX IF NOT EXISTS idx_students_zone ON students(zone)",
            ],
            "habit_practice": [
                "CREATE INDEX IF NOT EXISTS idx_habit_student ON habit_practice(student_id)",
            ],
            "conversations": [
                "CREATE INDEX IF NOT EXISTS idx_conversations_student ON conversations(student_id)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(student_id, agent)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at)",
            ],
            "observability_events": [
                "CREATE INDEX IF NOT EXISTS idx_observability_student ON observability_events(student_id_hash)",
                "CREATE INDEX IF NOT EXISTS idx_observability_type ON observability_events(event_type)",
                "CREATE INDEX IF NOT EXISTS idx_observability_timestamp ON observability_events(timestamp)",
            ],
        }

        cursor = pg_conn.cursor()

        for table in tables:
            if table in index_definitions:
                for index_sql in index_definitions[table]:
                    try:
                        cursor.execute(index_sql)
                        logger.info(f"Created index: {index_sql[:50]}...")
                    except psycopg2.Error as e:
                        logger.warning(f"Index creation failed (may exist): {e}")

    def verify_migration(self) -> Dict[str, bool]:
        """
        Verify migration success by comparing row counts

        Returns:
            Dict mapping table names to verification status
        """
        results = {}

        # Get SQLite row counts
        sqlite_conn = sqlite3.connect(str(self.sqlite_path))
        tables = self._get_sqlite_tables()

        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(self.postgres_url)
        pg_cursor = pg_conn.cursor()
        if self.postgres_schema:
            pg_cursor.execute(
                sql.SQL("SET search_path TO {}").format(
                    sql.Identifier(self.postgres_schema)
                )
            )

        for table_name in tables:
            # SQLite count
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            sqlite_count = sqlite_cursor.fetchone()[0]

            # PostgreSQL count
            pg_cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            pg_count = pg_cursor.fetchone()[0]

            # Compare
            results[table_name] = (sqlite_count == pg_count)

            if not results[table_name]:
                logger.warning(
                    f"Row count mismatch in {table_name}: "
                    f"SQLite={sqlite_count}, PostgreSQL={pg_count}"
                )

        sqlite_conn.close()
        pg_conn.close()

        return results


def migrate_all_cohorts(
    project_root: Path = None,
    postgres_url: str = None
) -> Dict[str, dict]:
    """
    Migrate all cohort databases to PostgreSQL

    Args:
        project_root: Project root directory
        postgres_url: PostgreSQL connection URL

    Returns:
        Dict mapping cohort names to migration results
    """
    if postgres_url is None:
        postgres_url = os.getenv("POSTGRES_URL")

    if not postgres_url:
        raise ValueError(
            "PostgreSQL URL required. Set POSTGRES_URL env var or pass postgres_url parameter"
        )

    if project_root is None:
        project_root = Path.cwd()

    results = {}

    # Find all SQLite cohort databases
    for sqlite_db in project_root.glob("cohort-*.db"):
        cohort_name = sqlite_db.stem

        try:
            # Create schema for this cohort
            schema_name = cohort_name.replace("-", "_")  # PostgreSQL schema naming

            logger.info(f"Migrating {cohort_name} to PostgreSQL schema: {schema_name}")

            migrator = DatabaseMigration(
                sqlite_path=str(sqlite_db),
                postgres_url=postgres_url,
                postgres_schema=schema_name
            )

            result = migrator.migrate()
            verification = migrator.verify_migration()

            results[cohort_name] = {
                "status": "success",
                "rows_migrated": result,
                "verification": verification,
            }

        except Exception as e:
            logger.error(f"Migration failed for {cohort_name}: {e}")
            results[cohort_name] = {
                "status": "failed",
                "error": str(e),
            }

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python migration.py <sqlite_db> <postgres_url>")
        sys.exit(1)

    sqlite_db = sys.argv[1]
    postgres_url = sys.argv[2]

    migrator = DatabaseMigration(
        sqlite_path=sqlite_db,
        postgres_url=postgres_url
    )

    print("Starting migration...")
    results = migrator.migrate()

    print("\nMigration results:")
    for table, count in results.items():
        print(f"  {table}: {count} rows")

    print("\nVerifying migration...")
    verification = migrator.verify_migration()

    all_verified = all(verification.values())
    if all_verified:
        print("✅ All tables verified successfully")
    else:
        print("❌ Verification failed:")
        for table, status in verification.items():
            if not status:
                print(f"  {table}: FAILED")
