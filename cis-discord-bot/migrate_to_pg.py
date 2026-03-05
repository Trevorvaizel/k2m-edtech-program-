"""
SQLite → PostgreSQL migration script for cohort-1.db
Fixes: case-insensitive column matching, correct FK dependency order,
       reserved-word quoting, sqlite_sequence skip.

Usage:
    PYTHONIOENCODING=utf-8 python migrate_to_pg.py [--dry-run]

ENV:
    DATABASE_URL  — PostgreSQL connection string (public proxy URL)
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# ── Config ────────────────────────────────────────────────────────────────────

SQLITE_DB = "cohort-1.db"
SCHEMA_SQL = "database/schema_pg.sql"
DRY_RUN = "--dry-run" in sys.argv

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:BdegWUlsgkLRYwgysRLjicFmaWveydUx@shinkansen.proxy.rlwy.net:19981/railway",
)

# Tables to skip entirely (internal SQLite tables with no PG equivalent)
SKIP_TABLES = {"sqlite_sequence"}

# Migration order — FK parents before children.
# Tables not listed here will be migrated last (0-row tables, order irrelevant).
MIGRATION_ORDER = [
    "students",                      # root: no FK deps
    "api_usage",                     # no FK deps
    "agent_unlock_announcements",    # no FK deps
    "cluster_assignments",           # discord_id (no strict FK in PG schema)
    "voice_channels",                # cluster_id
    "conversations",                 # student_id → students
    "habit_practice",                # student_id → students
    "daily_participation",           # discord_id
    "weekly_reflections",            # discord_id
    "showcase_publications",         # student_id → students
    "observability_events",          # student_id_hash (no strict FK)
    "artifact_progress",
    "cluster_session_attendance",
    "escalations",
    "parent_email_log",
    "parent_engagement",
    "student_consents",
    "student_publication_preferences",
]


def pg_cols_for_table(pg_cur, table_name: str) -> set[str]:
    """Return lowercase column names that exist in PostgreSQL for a given table."""
    pg_cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
        """,
        (table_name,),
    )
    return {row[0].lower() for row in pg_cur.fetchall()}


def quote_col(col: str) -> str:
    """Double-quote a column name (handles reserved words like 'timestamp')."""
    return f'"{col}"'


def migrate_table(sqlite_conn, pg_conn, table_name: str) -> int:
    """
    Migrate all rows from SQLite table → PostgreSQL table.
    Returns number of rows inserted.
    """
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.row_factory = None  # reset

    # Use Row factory on a fresh cursor
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    sqlite_cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    total = sqlite_cur.fetchone()[0]
    if total == 0:
        print(f"  {table_name}: 0 rows — skip")
        return 0

    sqlite_cur.execute(f'SELECT * FROM "{table_name}"')
    rows = sqlite_cur.fetchall()

    # Get SQLite columns (lowercase)
    sqlite_col_names = [desc[0].lower() for desc in sqlite_cur.description]

    pg_cur = pg_conn.cursor()
    pg_available = pg_cols_for_table(pg_cur, table_name)

    if not pg_available:
        print(f"  {table_name}: WARNING — table not found in PostgreSQL, skipping")
        return 0

    # Intersection: only columns that exist in both SQLite and PostgreSQL
    shared_cols = [c for c in sqlite_col_names if c in pg_available]

    if not shared_cols:
        print(f"  {table_name}: WARNING — no shared columns (sqlite={sqlite_col_names}, pg={sorted(pg_available)})")
        return 0

    # Build column index map: shared_col → position in sqlite row
    col_indices = {c: sqlite_col_names.index(c) for c in shared_cols}

    quoted_cols = ", ".join(quote_col(c) for c in shared_cols)
    placeholders = ", ".join(["%s"] * len(shared_cols))
    sql = f'INSERT INTO "{table_name}" ({quoted_cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'

    inserted = 0
    errors = 0
    batch = []

    for row in rows:
        values = tuple(row[col_indices[c]] for c in shared_cols)
        batch.append(values)

    if DRY_RUN:
        print(f"  [DRY RUN] {table_name}: would insert {len(batch)} rows | cols={shared_cols}")
        return len(batch)

    try:
        pg_cur.executemany(sql, batch)
        inserted = pg_cur.rowcount if pg_cur.rowcount >= 0 else len(batch)
        pg_conn.commit()
        print(f"  {table_name}: {inserted}/{total} rows migrated | cols={shared_cols}")
    except Exception as e:
        pg_conn.rollback()
        print(f"  {table_name}: ERROR — {e}")
        # Try row-by-row to isolate bad data
        for values in batch:
            try:
                pg_cur.execute(sql, values)
                pg_conn.commit()
                inserted += 1
            except Exception as row_err:
                pg_conn.rollback()
                errors += 1
                if errors <= 3:
                    print(f"    row error: {row_err} | values={values}")
        print(f"  {table_name}: recovered {inserted}/{total} rows ({errors} errors)")

    return inserted


def apply_schema(pg_conn):
    """Apply schema_pg.sql — create tables/indexes if not exist."""
    print("\n[1/3] Applying schema_pg.sql ...")
    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        schema = f.read()

    pg_conn.autocommit = True
    cur = pg_conn.cursor()

    # Split on semicolons. Each chunk may be: blank, comment-only, or actual SQL.
    # We strip comment lines and blank lines, then check if any real SQL remains.
    ok = 0
    fail = 0
    for raw_chunk in schema.split(";"):
        # Strip comment lines and blank lines to find actual SQL
        lines = raw_chunk.splitlines()
        sql_lines = [l for l in lines if l.strip() and not l.strip().startswith("--")]
        stmt = "\n".join(sql_lines).strip()
        if not stmt:
            continue  # chunk was blank or comment-only
        try:
            cur.execute(stmt)
            ok += 1
        except Exception as e:
            err_str = str(e).split("\n")[0]
            print(f"  schema stmt error: {err_str}")
            print(f"  stmt: {stmt[:80]}")
            fail += 1

    pg_conn.autocommit = False
    print(f"  Schema applied: {ok} statements OK, {fail} failed")


def verify_pg_tables(pg_conn):
    """List all tables now in PostgreSQL."""
    cur = pg_conn.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
    )
    tables = [r[0] for r in cur.fetchall()]
    print(f"\n[2/3] PostgreSQL tables ({len(tables)}): {tables}")
    return set(tables)


def main():
    print(f"SQLite → PostgreSQL migration {'[DRY RUN] ' if DRY_RUN else ''}starting...")
    print(f"  Source: {SQLITE_DB}")
    print(f"  Target: {DATABASE_URL[:40]}...")

    # Connect
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row

    pg_conn = psycopg2.connect(DATABASE_URL)
    pg_conn.autocommit = False

    # Step 1: Apply schema
    apply_schema(pg_conn)

    # Step 2: Verify PG tables
    pg_tables = verify_pg_tables(pg_conn)

    # Step 3: Migrate data
    print("\n[3/3] Migrating data ...")

    # Disable FK checks for bulk migration (autocommit must be off)
    fk_cur = pg_conn.cursor()
    fk_cur.execute("SET session_replication_role = 'replica'")
    pg_conn.commit()

    # Get all SQLite tables
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_sqlite_tables = {r[0] for r in sqlite_cur.fetchall()}

    # Ordered + remaining
    tables_to_migrate = []
    for t in MIGRATION_ORDER:
        if t in all_sqlite_tables and t not in SKIP_TABLES:
            tables_to_migrate.append(t)
    for t in sorted(all_sqlite_tables):
        if t not in tables_to_migrate and t not in SKIP_TABLES:
            tables_to_migrate.append(t)

    total_rows = 0
    for table in tables_to_migrate:
        n = migrate_table(sqlite_conn, pg_conn, table)
        total_rows += n

    # Re-enable FK checks
    fk_cur2 = pg_conn.cursor()
    fk_cur2.execute("SET session_replication_role = 'origin'")
    pg_conn.commit()

    print(f"\nDONE: {total_rows} total rows migrated")
    sqlite_conn.close()
    pg_conn.close()


if __name__ == "__main__":
    main()
