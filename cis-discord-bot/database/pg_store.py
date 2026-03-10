"""
PostgreSQL Store — Task 7.6
Decision H-03: Full PostgreSQL migration (blocking, pre-launch)
Decision H-06: Dual source of truth — Sheets=enrollment, PG=runtime

Architecture:
  PgConnectionWrapper  — adapts psycopg2 to look like sqlite3 to store.py
  PgStudentStateStore  — subclasses StudentStateStore, overrides connection layer
  get_pg_store()       — factory, called from database/__init__.py

SQL translations applied transparently in PgConnectionWrapper.execute():
  ?              → %s          (placeholder dialect)
  datetime('now')→ NOW()       (timestamp functions)
  json_extract   → ->>         (JSON operators)
  PRAGMA ...     → skipped     (SQLite-only pragmas)
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Iterator, List, Optional

# Static import — no circular risk (store.py has no database package imports)
from database.store import StudentStateStore

logger = logging.getLogger(__name__)

try:
    import psycopg2
    import psycopg2.extras
    from psycopg2 import sql as psycopg2_sql
    from psycopg2.pool import ThreadedConnectionPool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2_sql = None
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 not installed — PostgreSQL store unavailable")


# ---------------------------------------------------------------------------
# SQL Translation
# ---------------------------------------------------------------------------

_JSON_EXTRACT_RE = re.compile(
    r"json_extract\s*\(\s*(\w+)\s*,\s*'\$\.(\w+)'\s*\)",
    re.IGNORECASE,
)
_DATETIME_NOW_INTERVAL_RE = re.compile(
    r"datetime\s*\(\s*'now'\s*,\s*'([^']+)'\s*\)",
    re.IGNORECASE,
)
_DATETIME_NOW_RE = re.compile(r"datetime\s*\(\s*'now'\s*\)", re.IGNORECASE)


def _translate_sql(sql: str) -> Optional[str]:
    """
    Translate SQLite SQL to PostgreSQL SQL.
    Returns None if the statement should be silently skipped (e.g. PRAGMA).
    """
    stripped = sql.strip()
    if not stripped:
        return None

    # Skip all SQLite PRAGMA statements — no PostgreSQL equivalent needed
    if stripped.upper().startswith("PRAGMA"):
        return None

    # json_extract(col, '$.field') → col->>'field'
    sql = _JSON_EXTRACT_RE.sub(r"\1->>'\2'", sql)

    # datetime('now', 'interval') → NOW() + INTERVAL 'interval'
    sql = _DATETIME_NOW_INTERVAL_RE.sub(
        lambda m: f"(NOW() + INTERVAL '{m.group(1)}')", sql
    )

    # datetime('now') → NOW()
    sql = _DATETIME_NOW_RE.sub("NOW()", sql)

    # ? → %s  (parameterized placeholder)
    sql = sql.replace("?", "%s")

    # sqlite_master is used only in _table_exists / _column_exists which we override
    # but translate just in case it leaks through
    sql = sql.replace("sqlite_master", "pg_class")

    # Remove AUTOINCREMENT (PG uses SERIAL/BIGSERIAL in DDL, handled in schema_pg.sql)
    sql = sql.replace("AUTOINCREMENT", "")

    return sql


# ---------------------------------------------------------------------------
# Null cursor — returned when a statement is skipped
# ---------------------------------------------------------------------------

class _NullCursor:
    """Returned when a SQL statement is silently skipped (e.g. PRAGMA)."""

    def fetchone(self) -> None:
        return None

    def fetchall(self) -> list:
        return []

    def __iter__(self) -> Iterator:
        return iter([])

    @property
    def rowcount(self) -> int:
        return 0

    @property
    def lastrowid(self) -> None:
        return None


# ---------------------------------------------------------------------------
# Cursor wrapper — makes psycopg2 RealDictCursor look like sqlite3.Cursor
# ---------------------------------------------------------------------------

class PgCursorWrapper:
    """Thin wrapper around a psycopg2 RealDictCursor."""

    def __init__(self, cursor: Any) -> None:
        self._cursor = cursor

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self) -> list:
        return self._cursor.fetchall()

    def __iter__(self) -> Iterator:
        return iter(self._cursor)

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    @property
    def lastrowid(self) -> Optional[int]:
        # psycopg2 doesn't set lastrowid; caller should use RETURNING if needed
        return None


# ---------------------------------------------------------------------------
# Connection wrapper — makes psycopg2 connection look like sqlite3.Connection
# ---------------------------------------------------------------------------

class PgCursorCompat:
    """
    sqlite-like cursor object for legacy callsites that do:
      cursor = conn.cursor()
      cursor.execute(...)
      cursor.fetchone()
    """

    def __init__(self, conn_wrapper: "PgConnectionWrapper") -> None:
        self._conn_wrapper = conn_wrapper
        self._last_result: Any = _NullCursor()

    def execute(self, sql: str, params=()):
        self._last_result = self._conn_wrapper.execute(sql, params)
        return self

    def executemany(self, sql: str, params_list):
        self._conn_wrapper.executemany(sql, params_list)
        self._last_result = _NullCursor()
        return self

    def fetchone(self):
        return self._last_result.fetchone()

    def fetchall(self) -> list:
        return self._last_result.fetchall()

    def __iter__(self) -> Iterator:
        return iter(self._last_result)

    @property
    def rowcount(self) -> int:
        return getattr(self._last_result, "rowcount", 0)

    @property
    def lastrowid(self) -> Optional[int]:
        return getattr(self._last_result, "lastrowid", None)


class PgConnectionWrapper:
    """
    Adapts a psycopg2 connection to the sqlite3.Connection interface used
    throughout store.py, so that PgStudentStateStore inherits ~95% of the
    store logic unchanged.
    """

    def __init__(self, pg_conn: Any, pool: Any) -> None:
        self._conn = pg_conn
        self._pool = pool
        # Mimic sqlite3 attribute — ignored in PG mode but prevents AttributeErrors
        self.row_factory = None

    def execute(self, sql: str, params=()) -> Any:
        translated = _translate_sql(sql)
        if translated is None:
            return _NullCursor()

        cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(translated, params if params else None)
        return PgCursorWrapper(cursor)

    def cursor(self) -> PgCursorCompat:
        """
        Compatibility cursor for sqlite-style usage patterns in legacy modules.
        """
        return PgCursorCompat(self)

    def executemany(self, sql: str, params_list) -> None:
        translated = _translate_sql(sql)
        if translated is None:
            return
        cursor = self._conn.cursor()
        cursor.executemany(translated, params_list)

    def executescript(self, script: str) -> None:
        """Execute a multi-statement SQL script (schema init path)."""
        cursor = self._conn.cursor()
        for stmt in _split_sql_statements(script):
            stmt = stmt.strip()
            if stmt:
                translated = _translate_sql(stmt)
                if translated:
                    cursor.execute(translated)
        self._conn.commit()

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        """Return connection to pool instead of closing it."""
        if self._pool and self._conn:
            try:
                self._pool.putconn(self._conn)
            except Exception as exc:
                logger.warning("Error returning connection to pool: %s", exc)
        self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_sql_statements(sql: str) -> List[str]:
    """
    Split a SQL script into individual statements on semicolons.
    Strips comment-only lines before splitting.
    """
    cleaned_lines = []
    for line in sql.split("\n"):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    # Split on ; followed by whitespace/newline
    stmts = re.split(r";\s*\n", cleaned)
    return [s.strip() for s in stmts if s.strip()]


# ---------------------------------------------------------------------------
# PgStudentStateStore
# ---------------------------------------------------------------------------

class PgStudentStateStore(StudentStateStore):
    """
    PostgreSQL-backed store. Inherits StudentStateStore for backward compat
    with all callers, overriding only the connection/schema layer.

    Pool: ThreadedConnectionPool(minconn=2, maxconn=10) per spec (task 7.6).
    __init__ does NOT call super().__init__() — we skip SQLite setup entirely.
    """

    _pg_pool: Optional[Any] = None  # Class-level shared pool

    def __init__(self, database_url: str = None) -> None:
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2-binary is required for PostgreSQL mode. "
                "Run: pip install psycopg2-binary"
            )

        database_url = database_url or os.getenv("DATABASE_URL", "")
        if not (database_url.startswith("postgresql://") or database_url.startswith("postgres://")):
            raise ValueError(
                f"PgStudentStateStore requires a PostgreSQL DATABASE_URL. Got: {database_url[:30]!r}"
            )

        self._database_url = database_url
        self.db_path = database_url  # Store compat attribute
        self.conn = None
        self._using_uri = False
        self._pg_mode = True
        # Register with parent class instance tracker (bypasses super().__init__)
        StudentStateStore._instances.add(self)

        # Build shared pool (min=2, max=10 per spec)
        if PgStudentStateStore._pg_pool is None:
            PgStudentStateStore._pg_pool = ThreadedConnectionPool(
                minconn=2,
                maxconn=10,
                dsn=database_url,
            )
            logger.info("DB: PostgreSQL pool created (min=2, max=10)")

        self._connect()
        self._initialize_schema()
        logger.info("DB: PostgreSQL connected")

    # ------------------------------------------------------------------
    # Connection management overrides
    # ------------------------------------------------------------------

    def _connect(self, target_db_path=None, force_uri=False) -> None:
        """Get a connection from the PostgreSQL pool."""
        pg_conn = PgStudentStateStore._pg_pool.getconn()
        pg_conn.autocommit = False
        self.conn = PgConnectionWrapper(pg_conn, pool=PgStudentStateStore._pg_pool)

    def _apply_connection_pragmas(self, conn, db_target=None) -> None:
        """PostgreSQL has no PRAGMA equivalents — no-op."""
        pass

    def _initialize_schema(self) -> None:
        """Run schema_pg.sql to create/verify all PostgreSQL tables."""
        schema_path = Path(__file__).parent / "schema_pg.sql"
        if not schema_path.exists():
            logger.error(
                "schema_pg.sql not found at %s — schema NOT initialized", schema_path
            )
            return

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        pg_conn = self.conn._conn
        cursor = pg_conn.cursor()
        for stmt in _split_sql_statements(schema_sql):
            if stmt:
                cursor.execute(stmt)
        sequence_count = self._realign_serial_sequences(cursor)
        pg_conn.commit()
        logger.info(
            "DB: PostgreSQL schema initialized/verified (sequences realigned: %s)",
            sequence_count,
        )

    def _realign_serial_sequences(self, cursor: Any = None) -> int:
        """
        Self-heal serial sequences after bulk imports with explicit IDs.
        """
        if not psycopg2_sql:
            return 0

        local_cursor = cursor or self.conn._conn.cursor()
        local_cursor.execute(
            """
            SELECT table_name, column_name
              FROM information_schema.columns
             WHERE table_schema = 'public'
               AND column_default LIKE 'nextval(%'
               AND data_type IN ('integer', 'bigint')
            """
        )
        sequence_columns = local_cursor.fetchall() or []

        realigned = 0
        for row in sequence_columns:
            if isinstance(row, dict):
                table_name = row.get("table_name")
                column_name = row.get("column_name")
            else:
                table_name, column_name = row[0], row[1]

            if not table_name or not column_name:
                continue

            local_cursor.execute(
                psycopg2_sql.SQL(
                    "SELECT setval(pg_get_serial_sequence(%s, %s), "
                    "COALESCE(MAX({col}), 0) + 1, false) FROM {tbl}"
                ).format(
                    col=psycopg2_sql.Identifier(column_name),
                    tbl=psycopg2_sql.Identifier(table_name),
                ),
                (table_name, column_name),
            )
            realigned += 1

        return realigned

    def _table_exists(self, table_name: str) -> bool:
        cursor = self.conn._conn.cursor()
        cursor.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = %s",
            (table_name,),
        )
        return cursor.fetchone() is not None

    def _column_exists(self, table_name: str, column_name: str) -> bool:
        cursor = self.conn._conn.cursor()
        cursor.execute(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = %s AND column_name = %s",
            (table_name, column_name),
        )
        return cursor.fetchone() is not None

    def _apply_legacy_schema_migrations(self) -> None:
        """Schema is managed entirely by schema_pg.sql — no legacy migrations needed."""
        pass

    # ------------------------------------------------------------------
    # Fallback / lifecycle
    # ------------------------------------------------------------------

    @classmethod
    def activate_in_memory_fallback(cls, reason: str = "") -> None:
        """PostgreSQL mode does not use SQLite in-memory fallback."""
        logger.critical(
            "In-memory SQLite fallback is NOT available in PostgreSQL mode. "
            "Reason: %s. Bot continues with PostgreSQL — check Railway logs.",
            reason or "(no reason given)",
        )

    @classmethod
    def is_in_memory_fallback_active(cls) -> bool:
        return False

    def close(self) -> None:
        """Return connection to pool."""
        if self.conn:
            try:
                self.conn.close()
            except Exception as exc:
                logger.warning("Error closing PG connection: %s", exc)
            finally:
                self.conn = None

    def __del__(self) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Sprint 7 new methods (Decision B-01, H-06, GAP FIX #3)
    # ------------------------------------------------------------------

    def get_student_by_invite_code(self, invite_code: str):
        """
        Match student by unique invite link code (Decision B-01).
        Called from on_member_join to link Discord ID to enrollment row.
        """
        return self.conn.execute(
            "SELECT * FROM students WHERE invite_code = ?",
            (invite_code,),
        ).fetchone()

    def link_student_by_invite(
        self,
        invite_code: str,
        discord_id: str,
        discord_username: str,
    ) -> bool:
        """
        Write discord_id + discord_username into the student row matched by invite_code.
        Returns True if a row was updated, False if no match found (unmatched join).
        Decision B-01.
        """
        self.conn.execute(
            """
            UPDATE students
               SET discord_id = ?,
                   discord_username = ?
             WHERE invite_code = ?
               AND (
                    discord_id IS NULL
                    OR discord_id = ''
                    OR discord_id LIKE '__pending__%'
               )
            """,
            (discord_id, discord_username, invite_code),
        )
        self.conn.commit()

        # Verify the link landed
        updated = self.conn.execute(
            "SELECT 1 FROM students WHERE discord_id = ? AND invite_code = ?",
            (discord_id, invite_code),
        ).fetchone()
        return updated is not None

    def get_recent_unlinked_student(self, hours: int = 24):
        """
        Task 7.2 temporal fallback for !recover_member.
        Returns the most recently created student who has no real discord_id
        (still has the __pending__ placeholder) enrolled within the last N hours.
        Decision B-01 + GAP FIX #8.
        """
        return self.conn.execute(
            """
            SELECT * FROM students
             WHERE (discord_id IS NULL
                    OR discord_id = ''
                    OR discord_id LIKE '__pending__%')
               AND created_at >= NOW() - (? * INTERVAL '1 hour')
             ORDER BY created_at DESC
             LIMIT 1
            """,
            (hours,),
        ).fetchone()

    def update_onboarding_stop(self, discord_id: str, stop: int) -> None:
        """Advance student through KIRA onboarding stops 0-4 (Decision H-05)."""
        self.conn.execute(
            "UPDATE students SET onboarding_stop = ? WHERE discord_id = ?",
            (stop, discord_id),
        )
        self.conn.commit()

    def complete_onboarding_stop_0(self, discord_id: str) -> None:
        """Mark Stop 0 profile questions complete after GAP FIX #6 resequencing."""
        self.conn.execute(
            "UPDATE students SET onboarding_stop_0_complete = TRUE WHERE discord_id = ?",
            (discord_id,),
        )
        self.conn.commit()

    def get_engagement_sync_data(self, discord_id: str):
        """
        Return fields needed for nightly Sheets→PG sync (Decision H-06 / GAP FIX #3).
        Caller checks manual_override_timestamp before overwriting Sheets values.
        """
        return self.conn.execute(
            """
            SELECT onboarding_stop,
                   last_interaction,
                   interaction_count,
                   manual_override_timestamp,
                   zone
              FROM students
             WHERE discord_id = ?
            """,
            (discord_id,),
        ).fetchone()

    def get_students_for_engagement_sync(self):
        """
        Return all active students for nightly engagement sync back to Sheets.
        Only returns students with a discord_id (i.e. have joined Discord).
        Decision H-06.
        """
        return self.conn.execute(
            """
            SELECT discord_id,
                   enrollment_email,
                   onboarding_stop,
                   last_interaction,
                   interaction_count,
                   manual_override_timestamp
              FROM students
             WHERE discord_id IS NOT NULL
               AND discord_id != ''
            """
        ).fetchall()

    def upsert_student_from_sheets(
        self,
        enrollment_email: str,
        enrollment_name: str,
        invite_code: str,
        cohort_id: str = "cohort-1",
        **extra_fields,
    ) -> None:
        """
        Idempotent upsert of a student row from Google Sheets data.
        Called by preload_students.py before cohort start. Decision H-06.

        Sheets is the enrollment source of truth — this writes ALL enrollment
        fields. Runtime fields (zone, interaction_count, etc.) are NOT touched
        if the row already exists (ON CONFLICT DO UPDATE skips them).
        """
        fields = {
            "enrollment_email": enrollment_email,
            "enrollment_name": enrollment_name,
            "invite_code": invite_code,
            "cohort_id": cohort_id,
            "start_date": extra_fields.get("start_date", "2026-01-01"),
            "enrollment_status": extra_fields.get("enrollment_status", "enrolled"),
            "payment_status": extra_fields.get("payment_status", "confirmed"),
            "last_name": extra_fields.get("last_name", ""),
        }

        # discord_id may not exist yet — use email as the anchor key for upsert
        # We use enrollment_email as a secondary unique key for the upsert.
        self.conn._conn.cursor().execute(
            """
            INSERT INTO students (
                discord_id, enrollment_email, enrollment_name,
                invite_code, cohort_id, start_date,
                enrollment_status, payment_status, last_name
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s
            )
            ON CONFLICT (discord_id) DO UPDATE SET
                enrollment_email   = EXCLUDED.enrollment_email,
                enrollment_name    = EXCLUDED.enrollment_name,
                invite_code        = EXCLUDED.invite_code,
                cohort_id          = EXCLUDED.cohort_id,
                enrollment_status  = EXCLUDED.enrollment_status,
                payment_status     = EXCLUDED.payment_status,
                last_name          = EXCLUDED.last_name
            """,
            (
                # Use email as placeholder discord_id until on_member_join fires
                f"__pending__{enrollment_email}",
                enrollment_email,
                enrollment_name,
                invite_code,
                cohort_id,
                fields["start_date"],
                fields["enrollment_status"],
                fields["payment_status"],
                fields["last_name"],
            ),
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # Sprint 7.4 — M-Pesa token warning flag (Decision H-01, GAP FIX #4)
    # ------------------------------------------------------------------

    def get_token_warning_sent(self, enrollment_email: str) -> bool:
        """
        Return True if a token expiry warning DM/email was already sent for
        this student in the current token cycle. Prevents duplicate warnings.
        Lookup by enrollment_email (student may not have a Discord ID yet).
        """
        row = self.conn.execute(
            "SELECT token_warning_sent FROM students WHERE enrollment_email = ?",
            (enrollment_email,),
        ).fetchone()
        if row is None:
            return False
        val = row["token_warning_sent"] if isinstance(row, dict) else row[0]
        return bool(val)

    def set_token_warning_sent(self, enrollment_email: str, value: bool) -> None:
        """
        Set the token_warning_sent flag for a student (by enrollment_email).
        Call with value=True after sending the warning, value=False on /renew.
        """
        self.conn.execute(
            "UPDATE students SET token_warning_sent = ? WHERE enrollment_email = ?",
            (value, enrollment_email),
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # Health check helper (used by health_monitor.py)
    # ------------------------------------------------------------------

    def check_pg_connectivity(self) -> bool:
        """
        Verify PostgreSQL connection is live. Returns True if healthy.
        Called by HealthMonitor every 5 minutes (task 7.6 acceptance criterion).
        """
        try:
            cursor = self.conn._conn.cursor()
            cursor.execute("SELECT 1")
            return True
        except Exception as exc:
            logger.error("PostgreSQL connectivity check failed: %s", exc)
            return False

    @classmethod
    def get_pool_status(cls) -> dict:
        """Return connection pool diagnostics for health monitoring."""
        if cls._pg_pool is None:
            return {"pool": "not_initialized"}
        pool = cls._pg_pool
        return {
            "pool": "ok",
            "minconn": pool.minconn,
            "maxconn": pool.maxconn,
        }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_pg_store(database_url: str = None) -> "PgStudentStateStore":
    """
    Instantiate a PgStudentStateStore, importing StudentStateStore at call time
    to avoid circular imports at module load.
    """
    from database.store import StudentStateStore

    # Inject StudentStateStore as base class dynamically so PgStudentStateStore
    # inherits all 80+ methods from store.py without duplicating them.
    if StudentStateStore not in PgStudentStateStore.__bases__:
        PgStudentStateStore.__bases__ = (StudentStateStore,)

    return PgStudentStateStore(database_url=database_url)
