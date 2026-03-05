"""
Database Store Module
Story 4.7 Implementation: StudentContext & Database Schema

Provides database operations for the CIS bot.
Uses SQLite for Cohort 1 (100-200 students).
"""

import sqlite3
import json
import hashlib
import os
import inspect
import weakref
from datetime import datetime, timedelta
from typing import Tuple
from typing import Optional, List, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Consent records are short-lived to preserve student control over private process.
DEFAULT_JOURNEY_CONSENT_TTL_HOURS = 24
VALID_PUBLICATION_PREFERENCES = {
    "always_ask",
    "always_yes",
    "always_no",
    "week8_only",
}

class StudentStateStore:
    """Database operations for student state and conversations"""

    IN_MEMORY_FALLBACK_URI = "file:k2m-backup-mode?mode=memory&cache=shared"
    _fallback_mode_active = False
    _fallback_anchor_conn = None
    _fallback_reason = ""
    _instances = weakref.WeakSet()

    def __init__(self, db_path: str = None):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file. Defaults to cohort-1.db
        """
        if db_path is None:
            env_db_path = os.getenv("DATABASE_PATH", "").strip()
            if env_db_path:
                db_path = env_db_path
            else:
                # Default: database in project root
                project_root = Path(__file__).parent.parent
                db_path = project_root / "cohort-1.db"

        self.db_path = str(db_path)
        self.conn = None
        self._using_uri = False
        StudentStateStore._instances.add(self)

        if StudentStateStore._fallback_mode_active:
            self._connect(StudentStateStore.IN_MEMORY_FALLBACK_URI, force_uri=True)
        else:
            self._connect()
        self._initialize_schema()

    def _connect(self, target_db_path: Optional[str] = None, force_uri: bool = False):
        """Establish database connection"""
        db_target = str(target_db_path or self.db_path)
        self._using_uri = force_uri or db_target.startswith("file:")
        self.conn = sqlite3.connect(
            db_target,
            check_same_thread=False,
            uri=self._using_uri,
        )
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self._apply_connection_pragmas(self.conn, db_target=db_target)

    def _apply_connection_pragmas(self, conn: sqlite3.Connection, db_target: str) -> None:
        """
        Apply SQLite pragmas for integrity and write-contention resilience.
        """
        # SQLite does not enforce foreign keys unless explicitly enabled per connection.
        conn.execute("PRAGMA foreign_keys = ON")
        # Let writers wait briefly instead of instantly failing under burst writes.
        conn.execute("PRAGMA busy_timeout = 10000")
        # Lower fsync pressure while keeping crash consistency suitable for this workload.
        conn.execute("PRAGMA synchronous = NORMAL")

        # WAL is best for concurrent readers/writers on file-backed DBs.
        is_in_memory_uri = db_target.startswith("file:") and "mode=memory" in db_target
        if not is_in_memory_uri and db_target != ":memory:":
            try:
                conn.execute("PRAGMA journal_mode = WAL")
            except sqlite3.DatabaseError as exc:
                logger.warning("Could not enable WAL mode for %s: %s", db_target, exc)

    @classmethod
    def is_in_memory_fallback_active(cls) -> bool:
        """Return True when all stores should run in backup in-memory mode."""
        return cls._fallback_mode_active

    @classmethod
    def activate_in_memory_fallback(cls, reason: str = "") -> None:
        """
        Switch all StudentStateStore instances to a shared in-memory SQLite backend.

        This keeps command routing alive during disk DB failures while Trevor restores
        from backups.
        """
        if not cls._fallback_mode_active:
            cls._fallback_mode_active = True
            cls._fallback_reason = reason or ""

        if cls._fallback_anchor_conn is None:
            cls._fallback_anchor_conn = sqlite3.connect(
                cls.IN_MEMORY_FALLBACK_URI,
                check_same_thread=False,
                uri=True,
            )
            cls._fallback_anchor_conn.row_factory = sqlite3.Row
            cls._fallback_anchor_conn.execute("PRAGMA foreign_keys = ON")
            cls._fallback_anchor_conn.execute("PRAGMA busy_timeout = 10000")

        for instance in list(cls._instances):
            instance._switch_to_in_memory_fallback()

        if reason:
            logger.critical("Database fallback mode activated: %s", reason)
        else:
            logger.critical("Database fallback mode activated")

    def _switch_to_in_memory_fallback(self) -> None:
        """Reconnect this store instance to the shared in-memory fallback DB."""
        if (
            self.conn
            and self._using_uri
            and str(self.db_path) == StudentStateStore.IN_MEMORY_FALLBACK_URI
        ):
            return

        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass

        self.db_path = StudentStateStore.IN_MEMORY_FALLBACK_URI
        self._connect(StudentStateStore.IN_MEMORY_FALLBACK_URI, force_uri=True)
        self._initialize_schema()

    @property
    def db(self):
        """
        Backward-compat alias for legacy code/tests that expect ``store.db``.
        """
        return self.conn

    @db.setter
    def db(self, value):
        self.conn = value

    def _initialize_schema(self):
        """Create database tables from schema.sql if not exists"""
        schema_path = Path(__file__).parent / "schema.sql"

        if schema_path.exists():
            # Legacy DB compatibility: old `students` tables may miss newer columns.
            # Add required columns before running schema indexes that reference them.
            self._apply_legacy_schema_migrations()

            # Force UTF-8 because schema comments include Unicode symbols.
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                self.conn.executescript(schema_sql)
                self.conn.commit()
        else:
            # Fallback: create tables directly
            self._create_tables_fallback()

    def _table_exists(self, table_name: str) -> bool:
        """Return True when the given table exists in the SQLite database."""
        cursor = self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,)
        )
        return cursor.fetchone() is not None

    def _column_exists(self, table_name: str, column_name: str) -> bool:
        """Return True when the given column exists on the target table."""
        cursor = self.conn.execute(f"PRAGMA table_info({table_name})")
        return any(row["name"] == column_name for row in cursor.fetchall())

    def _apply_legacy_schema_migrations(self) -> None:
        """
        Apply compatibility migrations before executing the full schema script.

        This prevents startup failures when existing tables were created by older
        schema versions that did not yet include newer columns.
        """
        if not self._table_exists("students"):
            return

        if not self._column_exists("students", "cluster_id"):
            logger.info("Applying legacy migration: adding students.cluster_id")
            self.conn.execute(
                "ALTER TABLE students ADD COLUMN cluster_id INTEGER DEFAULT 1"
            )

        if not self._column_exists("students", "last_name"):
            logger.info("Applying legacy migration: adding students.last_name")
            self.conn.execute("ALTER TABLE students ADD COLUMN last_name TEXT")

        if self._table_exists("parent_engagement"):
            if not self._column_exists("parent_engagement", "parent_opted_out"):
                logger.info("Applying legacy migration: adding parent_engagement.parent_opted_out")
                self.conn.execute(
                    "ALTER TABLE parent_engagement ADD COLUMN parent_opted_out INTEGER DEFAULT 0"
                )

            if not self._column_exists("parent_engagement", "parent_opted_out_at"):
                logger.info("Applying legacy migration: adding parent_engagement.parent_opted_out_at")
                self.conn.execute(
                    "ALTER TABLE parent_engagement ADD COLUMN parent_opted_out_at TEXT"
                )

            if not self._column_exists("parent_engagement", "parent_email_status"):
                logger.info("Applying legacy migration: adding parent_engagement.parent_email_status")
                self.conn.execute(
                    "ALTER TABLE parent_engagement ADD COLUMN parent_email_status TEXT DEFAULT 'active'"
                )

        self.conn.commit()

    def _create_tables_fallback(self):
        """Fallback table creation if schema.sql not found"""
        # Students table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                discord_id TEXT PRIMARY KEY,
                cohort_id TEXT NOT NULL,
                start_date TEXT NOT NULL,
                current_week INTEGER DEFAULT 1,
                current_state TEXT DEFAULT 'none',
                zone TEXT DEFAULT 'zone_0',
                jtbd_concern TEXT DEFAULT 'career_direction',
                emotional_state TEXT DEFAULT 'curious',
                unlocked_agents TEXT DEFAULT '["frame"]',
                artifact_progress INTEGER DEFAULT 0,
                interaction_count INTEGER DEFAULT 0,
                last_interaction TEXT,
                cluster_id INTEGER DEFAULT 1,
                last_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Conversations table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tokens INTEGER,
                cost_usd REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(discord_id)
            )
        """)

        self.conn.commit()

        # Consent records table (Guardrail #8)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS student_consents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id_hash TEXT NOT NULL,
                consent_type TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                source TEXT,
                UNIQUE(student_id_hash, consent_type)
            )
        """)
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_consents_lookup ON student_consents(student_id_hash, consent_type)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_consents_expiry ON student_consents(expires_at)"
        )
        self.conn.commit()

    @staticmethod
    def _hash_student_id(discord_id: str) -> str:
        """Create privacy-preserving student identifier used in observability tables."""
        return hashlib.sha256(str(discord_id).encode()).hexdigest()[:16]

    def get_student(self, discord_id) -> Optional[sqlite3.Row]:
        """
        Retrieve student by Discord ID

        Args:
            discord_id: Student's Discord user ID (int or str)

        Returns:
            Student row or None if not found
        """
        discord_id = str(discord_id)  # Normalize: discord.py passes int IDs
        cursor = self.conn.execute(
            "SELECT * FROM students WHERE discord_id = ?",
            (discord_id,)
        )
        return cursor.fetchone()

    def create_student(self, discord_id, cohort_id: str = None) -> sqlite3.Row:
        """
        Create new student record

        Args:
            discord_id: Student's Discord user ID (int or str)
            cohort_id: Cohort identifier (defaults to COHORT_ID env var)

        Returns:
            Created student row
        """
        discord_id = str(discord_id)  # Normalize: discord.py passes int IDs
        cohort_id = cohort_id or os.getenv('COHORT_ID', 'cohort-1')
        # Use cohort start date from env (not student join time)
        start_date = os.getenv('COHORT_1_START_DATE', datetime.now().strftime('%Y-%m-%d'))

        self.conn.execute(
            """
            INSERT INTO students (
                discord_id, cohort_id, start_date, current_week,
                current_state, zone, jtbd_concern, emotional_state
            ) VALUES (?, ?, ?, 1, 'none', 'zone_0', 'career_direction', 'curious')
            """,
            (discord_id, cohort_id, start_date)
        )
        self.conn.commit()

        # Initialize habit practice records
        for habit_id in [1, 2, 3, 4]:
            self.conn.execute(
                """
                INSERT INTO habit_practice (student_id, habit_id, practiced_count, confidence)
                VALUES (?, ?, 0, 'emerging')
                """,
                (discord_id, habit_id)
            )

        self.conn.commit()

        return self.get_student(discord_id)

    def _ensure_student_record(self, discord_id: str) -> None:
        """
        Ensure a student row exists before writing FK-backed records.

        Showcase preference/publication writes can happen from async handlers
        that may race initial student creation in other paths.
        """
        discord_id = str(discord_id)
        if self.get_student(discord_id) is None:
            self.create_student(discord_id)

    def update_student_week(self, discord_id: str, week: int):
        """
        Update student's current week

        Args:
            discord_id: Student's Discord user ID
            week: New week number (1-8)
        """
        discord_id = str(discord_id)
        self.conn.execute(
            "UPDATE students SET current_week = ? WHERE discord_id = ?",
            (week, discord_id)
        )
        self.conn.commit()

    def update_student_zone(self, discord_id: str, zone: str):
        """
        Update student's zone progression

        Args:
            discord_id: Student's Discord user ID
            zone: New zone (zone_0 through zone_4)
        """
        discord_id = str(discord_id)
        existing = self.get_student(discord_id)
        if existing is None:
            return

        previous_zone = existing["zone"]
        self.conn.execute(
            "UPDATE students SET zone = ? WHERE discord_id = ?",
            (zone, discord_id)
        )
        self.conn.commit()

        if previous_zone != zone:
            self.log_observability_event(
                discord_id=discord_id,
                event_type="zone_shift",
                metadata={
                    "from_zone": previous_zone,
                    "to_zone": zone,
                    "week": existing["current_week"],
                },
            )

    def record_student_consent(
        self,
        discord_id,
        consent_type: str = "journey_inspection",
        ttl_hours: int = DEFAULT_JOURNEY_CONSENT_TTL_HOURS,
        source: str = "student_dm_phrase",
    ):
        """
        Record/refresh student consent for a bounded time window.
        """
        discord_id = str(discord_id)
        student_id_hash = self._hash_student_id(discord_id)
        granted_at = datetime.now()
        expires_at = granted_at + timedelta(hours=max(ttl_hours, 1))

        self.conn.execute(
            """
            INSERT INTO student_consents (
                student_id_hash, consent_type, granted_at, expires_at, revoked_at, source
            ) VALUES (?, ?, ?, ?, NULL, ?)
            ON CONFLICT(student_id_hash, consent_type)
            DO UPDATE SET
                granted_at = excluded.granted_at,
                expires_at = excluded.expires_at,
                revoked_at = NULL,
                source = excluded.source
            """,
            (
                student_id_hash,
                consent_type,
                granted_at.isoformat(),
                expires_at.isoformat(),
                source,
            ),
        )
        self.conn.commit()

    def revoke_student_consent(self, discord_id, consent_type: str = "journey_inspection"):
        """
        Revoke an active consent grant immediately.
        """
        discord_id = str(discord_id)
        student_id_hash = self._hash_student_id(discord_id)

        self.conn.execute(
            """
            UPDATE student_consents
            SET revoked_at = ?
            WHERE student_id_hash = ? AND consent_type = ?
            """,
            (datetime.now().isoformat(), student_id_hash, consent_type),
        )
        self.conn.commit()

    def has_active_student_consent(
        self,
        discord_id,
        consent_type: str = "journey_inspection",
    ) -> bool:
        """
        Check if a student has valid, unrevoked consent for a specific use.
        """
        discord_id = str(discord_id)
        student_id_hash = self._hash_student_id(discord_id)
        now_iso = datetime.now().isoformat()

        cursor = self.conn.execute(
            """
            SELECT 1
            FROM student_consents
            WHERE student_id_hash = ?
              AND consent_type = ?
              AND revoked_at IS NULL
              AND expires_at >= ?
            LIMIT 1
            """,
            (student_id_hash, consent_type, now_iso),
        )
        return cursor.fetchone() is not None

    def save_conversation(
        self,
        discord_id: str,
        agent: str,
        role: str,
        content: str,
        tokens: int = None,
        cost_usd: float = None
    ):
        """
        Save conversation message to database

        Args:
            discord_id: Student's Discord user ID
            agent: Agent name (framer, explorer, challenger, synthesizer)
            role: Message role (user, assistant)
            content: Message content
            tokens: Number of tokens (optional)
            cost_usd: Cost in USD (optional)
        """
        discord_id = str(discord_id)
        self.conn.execute(
            """
            INSERT INTO conversations (
                student_id, agent, role, content, tokens, cost_usd
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (discord_id, agent, role, content, tokens, cost_usd)
        )
        self.conn.commit()

        # Update student interaction count
        self.conn.execute(
            "UPDATE students SET interaction_count = interaction_count + 1, last_interaction = ? WHERE discord_id = ?",
            (datetime.now().isoformat(), discord_id)
        )
        self.conn.commit()

    def get_conversation_history(
        self,
        discord_id: str,
        agent: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve conversation history for context window

        Args:
            discord_id: Student's Discord user ID
            agent: Agent name
            limit: Maximum number of messages (default 10)

        Returns:
            List of conversation messages
        """
        discord_id = str(discord_id)
        cursor = self.conn.execute(
            """
            SELECT role, content
            FROM conversations
            WHERE student_id = ? AND agent = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (discord_id, agent, limit)
        )

        # Reverse to get chronological order
        messages = [dict(row) for row in cursor.fetchall()]
        messages.reverse()

        return messages

    def update_habit_practice(self, discord_id: str, habit_id: int):
        """
        Increment habit practice count

        Args:
            discord_id: Student's Discord user ID
            habit_id: Habit ID (1-4)
        """
        discord_id = str(discord_id)
        self.conn.execute(
            """
            UPDATE habit_practice
            SET practiced_count = practiced_count + 1,
                last_practiced = ?
            WHERE student_id = ? AND habit_id = ?
            """,
            (datetime.now().isoformat(), discord_id, habit_id)
        )
        self.conn.commit()

    def get_student_count(self) -> int:
        """
        Get total number of students in database

        Returns:
            Student count
        """
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM students")
        result = cursor.fetchone()
        return result['count'] if result else 0

    def build_student_context(self, discord_id: str):
        """
        Build a full StudentContext domain model from stored data.

        Args:
            discord_id: Student's Discord user ID

        Returns:
            StudentContext or None if student does not exist
        """
        from database.models import build_student_context

        student = self.get_student(discord_id)
        if student is None:
            return None

        return build_student_context(student, conn=self.conn)

    def get_habit_journey(self, discord_id: str) -> List[sqlite3.Row]:
        """
        Retrieve habit journey rows for a student.

        Args:
            discord_id: Student's Discord user ID

        Returns:
            List of habit_practice rows
        """
        discord_id = str(discord_id)
        cursor = self.conn.execute(
            """
            SELECT habit_id, practiced_count, last_practiced, confidence
            FROM habit_practice
            WHERE student_id = ?
            ORDER BY habit_id
            """,
            (discord_id,)
        )
        return cursor.fetchall()

    def get_artifact_progress_row(self, discord_id: str) -> Optional[sqlite3.Row]:
        """
        Retrieve artifact progress row for a student.

        Args:
            discord_id: Student's Discord user ID

        Returns:
            artifact_progress row or None
        """
        discord_id = str(discord_id)
        cursor = self.conn.execute(
            "SELECT * FROM artifact_progress WHERE student_id = ?",
            (discord_id,)
        )
        return cursor.fetchone()

    def save_artifact_progress(
        self,
        discord_id: str,
        artifact_progress
    ) -> None:
        """
        Save or update artifact progress for a student.

        Args:
            discord_id: Student's Discord user ID
            artifact_progress: ArtifactProgress dataclass instance
        """
        from database.models import ArtifactProgress

        discord_id = str(discord_id)
        now = datetime.now().isoformat()

        # Ensure student record exists
        self._ensure_student_record(discord_id)

        # Check if this is a new artifact or update
        existing = self.get_artifact_progress_row(discord_id)
        if existing is None:
            # Create new artifact progress record
            started_at = artifact_progress.started_at.isoformat() if artifact_progress.started_at else now
            self.conn.execute(
                """
                INSERT INTO artifact_progress (
                    student_id, section_1_question, section_2_reframed, section_3_explored,
                    section_4_challenged, section_5_concluded, section_6_reflection,
                    completed_sections, current_section, status, started_at, last_activity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    discord_id,
                    artifact_progress.section_1_question,
                    artifact_progress.section_2_reframed,
                    artifact_progress.section_3_explored,
                    artifact_progress.section_4_challenged,
                    artifact_progress.section_5_concluded,
                    artifact_progress.section_6_reflection,
                    json.dumps(artifact_progress.completed_sections),
                    artifact_progress.current_section,
                    artifact_progress.status,
                    started_at,
                    now
                )
            )
        else:
            # Update existing artifact progress
            self.conn.execute(
                """
                UPDATE artifact_progress SET
                    section_1_question = ?,
                    section_2_reframed = ?,
                    section_3_explored = ?,
                    section_4_challenged = ?,
                    section_5_concluded = ?,
                    section_6_reflection = ?,
                    completed_sections = ?,
                    current_section = ?,
                    status = ?,
                    last_activity = ?,
                    completed_at = CASE WHEN ? = 'completed' THEN ? ELSE completed_at END,
                    published_at = CASE WHEN ? = 'published' THEN ? ELSE published_at END
                WHERE student_id = ?
                """,
                (
                    artifact_progress.section_1_question,
                    artifact_progress.section_2_reframed,
                    artifact_progress.section_3_explored,
                    artifact_progress.section_4_challenged,
                    artifact_progress.section_5_concluded,
                    artifact_progress.section_6_reflection,
                    json.dumps(artifact_progress.completed_sections),
                    artifact_progress.current_section,
                    artifact_progress.status,
                    now,
                    artifact_progress.status, now,  # Set completed_at if status is 'completed'
                    artifact_progress.status, now,  # Set published_at if status is 'published'
                    discord_id
                )
            )

        self.conn.commit()

    def update_artifact_section(
        self,
        discord_id: str,
        section_number: int,
        content: str
    ) -> None:
        """
        Update a specific section of the artifact.

        Args:
            discord_id: Student's Discord user ID
            section_number: Section number (1-6)
            content: Section content to save
        """
        discord_id = str(discord_id)
        section_columns = {
            1: ("section_1_question", "section_1_question"),
            2: ("section_2_reframed", "section_2_reframed"),
            3: ("section_3_explored", "section_3_explored"),
            4: ("section_4_challenged", "section_4_challenged"),
            5: ("section_5_concluded", "section_5_concluded"),
            6: ("section_6_reflection", "section_6_reflection"),
        }

        if section_number not in section_columns:
            raise ValueError(f"Invalid section_number: {section_number}. Must be 1-6.")

        column, completed_key = section_columns[section_number]
        now = datetime.now().isoformat()

        # Update the specific section
        self.conn.execute(
            f"UPDATE artifact_progress SET {column} = ?, last_activity = ? WHERE student_id = ?",
            (content, now, discord_id)
        )

        # Update completed_sections list
        existing = self.get_artifact_progress_row(discord_id)
        if existing:
            completed = json.loads(existing['completed_sections'] or '[]')
            if completed_key not in completed:
                completed.append(completed_key)
            next_section = section_number + 1 if section_number < 6 else 6
            self.conn.execute(
                "UPDATE artifact_progress SET completed_sections = ?, current_section = ? WHERE student_id = ?",
                (json.dumps(completed), next_section, discord_id)
            )

        self.conn.commit()

    def log_observability_event(
        self,
        discord_id,
        event_type: str,
        metadata: Dict
    ):
        """
        Log observability event for Trevor dashboard

        Args:
            discord_id: Student's Discord user ID (int or str)
            event_type: Event type (agent_used, stuck_detected, etc.)
            metadata: Event metadata as dictionary
        """
        discord_id = str(discord_id)  # Normalize
        # Hash student ID for privacy (Task 1.7 Guardrail #8)
        student_id_hash = self._hash_student_id(discord_id)

        self.conn.execute(
            """
            INSERT INTO observability_events (
                student_id_hash, event_type, metadata, timestamp
            ) VALUES (?, ?, ?, ?)
            """,
            (
                student_id_hash,
                event_type,
                json.dumps(metadata),
                datetime.now().isoformat()
            )
        )
        self.conn.commit()

    # ============================================================
    # OBSERVABILITY QUERY METHODS (Task 1.7)
    # Trevor admin dashboard - Guardrail compliant
    # ============================================================

    def get_aggregate_patterns(self, days: int = 7) -> Dict:
        """
        Get aggregate patterns (Guardrail #3: no comparison/ranking).

        Always-on metrics - no consent needed.

        Args:
            days: Number of days to look back (default 7)

        Returns:
            Dict with aggregate metrics
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Agent usage distribution
        cursor = self.conn.execute(
            """
            SELECT event_type, COUNT(*) as count
            FROM observability_events
            WHERE timestamp >= ?
            GROUP BY event_type
            """,
            (cutoff_date,)
        )
        event_counts = {row['event_type']: row['count'] for row in cursor.fetchall()}

        # Agent usage breakdown
        cursor = self.conn.execute(
            """
            SELECT json_extract(metadata, '$.agent') as agent, COUNT(*) as count
            FROM observability_events
            WHERE event_type = 'agent_used' AND timestamp >= ?
            GROUP BY agent
            """,
            (cutoff_date,)
        )
        agent_usage = {row['agent']: row['count'] for row in cursor.fetchall()}

        # Zone distribution (current)
        cursor = self.conn.execute(
            "SELECT zone, COUNT(*) as count FROM students GROUP BY zone"
        )
        zone_distribution = {row['zone']: row['count'] for row in cursor.fetchall()}

        # Milestone celebrations
        cursor = self.conn.execute(
            """
            SELECT COALESCE(
                json_extract(metadata, '$.milestone'),
                json_extract(metadata, '$.practiced_count'),
                json_extract(metadata, '$.practice_count')
            ) as milestone,
            COUNT(*) as count
            FROM observability_events
            WHERE event_type = 'milestone_reached' AND timestamp >= ?
            GROUP BY milestone
            """,
            (cutoff_date,)
        )
        milestones = {row['milestone']: row['count'] for row in cursor.fetchall()}

        # Total students and active students
        cursor = self.conn.execute(
            f"""
            SELECT COUNT(*) as total FROM students
            """
        )
        total_students = cursor.fetchone()['total']

        cursor = self.conn.execute(
            f"""
            SELECT COUNT(DISTINCT student_id_hash) as active
            FROM observability_events
            WHERE timestamp >= ?
            """,
            (cutoff_date,)
        )
        active_students = cursor.fetchone()['active']

        return {
            'period_days': days,
            'total_students': total_students,
            'active_students': active_students,
            'event_distribution': event_counts,
            'agent_usage': agent_usage,
            'zone_distribution': zone_distribution,
            'milestone_celebrations': milestones
        }

    def get_student_journey_events(self, discord_id: str, limit: int = 50) -> List[Dict]:
        """
        Get individual student's observability events.

        REQUIRES STUDENT CONSENT (Guardrail #8).

        Args:
            discord_id: Student's Discord user ID
            limit: Maximum events to return

        Returns:
            List of observability events
        """
        discord_id = str(discord_id)
        student_id_hash = self._hash_student_id(discord_id)

        cursor = self.conn.execute(
            """
            SELECT event_type, metadata, timestamp
            FROM observability_events
            WHERE student_id_hash = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (student_id_hash, limit)
        )

        events = []
        for row in cursor.fetchall():
            events.append({
                'event_type': row['event_type'],
                'metadata': json.loads(row['metadata']),
                'timestamp': row['timestamp']
            })

        return events

    def get_stuck_students(self, inactive_days: int = 3) -> List[Dict]:
        """
        Identify students who may be stuck (intervention opportunities).

        Args:
            inactive_days: Days since last interaction (default 3)

        Returns:
            List of potentially stuck students (hashed IDs for privacy)
        """
        cutoff_date = (datetime.now() - timedelta(days=inactive_days)).strftime("%Y-%m-%d %H:%M:%S")

        # Python-side filtering keeps hash logic explicit and correct.
        all_students = self.conn.execute("SELECT discord_id, current_week, zone, interaction_count FROM students").fetchall()

        # Get all active student hashes in the period
        active_hashes = set()
        cursor = self.conn.execute(
            """
            SELECT DISTINCT student_id_hash
            FROM observability_events
            WHERE event_type = 'agent_used' AND timestamp >= ?
            """,
            (cutoff_date,)
        )
        for row in cursor.fetchall():
            active_hashes.add(row['student_id_hash'])

        stuck = []
        for student in all_students:
            student_hash = self._hash_student_id(student["discord_id"])
            if student_hash not in active_hashes:
                self._log_stuck_detected_if_needed(
                    student_hash=student_hash,
                    inactive_days=inactive_days,
                    current_week=student["current_week"],
                    zone=student["zone"],
                    total_interactions=student["interaction_count"],
                )
                stuck.append({
                    'student_id_hash': student_hash,
                    'discord_id': student['discord_id'],  # For Trevor's reference only
                    'current_week': student['current_week'],
                    'zone': student['zone'],
                    'total_interactions': student['interaction_count'],
                    'last_active_cutoff': cutoff_date
                })

        return stuck

    def _log_stuck_detected_if_needed(
        self,
        student_hash: str,
        inactive_days: int,
        current_week: int,
        zone: str,
        total_interactions: int,
    ):
        """
        Emit `stuck_detected` once per student per day to avoid noisy duplicates.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        already_logged = self.conn.execute(
            """
            SELECT 1
            FROM observability_events
            WHERE student_id_hash = ?
              AND event_type = 'stuck_detected'
              AND timestamp >= ?
            LIMIT 1
            """,
            (student_hash, today),
        ).fetchone()
        if already_logged:
            return

        self.conn.execute(
            """
            INSERT INTO observability_events (
                student_id_hash, event_type, metadata, timestamp
            ) VALUES (?, ?, ?, ?)
            """,
            (
                student_hash,
                "stuck_detected",
                json.dumps(
                    {
                        "inactive_days": inactive_days,
                        "week": current_week,
                        "zone": zone,
                        "total_interactions": total_interactions,
                    }
                ),
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()

    def get_zone_shifts(self, days: int = 30) -> List[Dict]:
        """
        Get zone shift events for identity transformation tracking.

        Args:
            days: Number of days to look back

        Returns:
            List of zone shift events
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        cursor = self.conn.execute(
            """
            SELECT student_id_hash, metadata, timestamp
            FROM observability_events
            WHERE event_type = 'zone_shift' AND timestamp >= ?
            ORDER BY timestamp DESC
            """,
            (cutoff_date,)
        )

        shifts = []
        for row in cursor.fetchall():
            metadata = json.loads(row['metadata'])
            shifts.append({
                'student_id_hash': row['student_id_hash'],
                'from_zone': metadata.get('from_zone'),
                'to_zone': metadata.get('to_zone'),
                'week': metadata.get('week'),
                'timestamp': row['timestamp']
            })

        return shifts

    def get_milestone_celebrations(self, days: int = 7) -> List[Dict]:
        """
        Get recent habit milestone celebrations.

        Args:
            days: Number of days to look back

        Returns:
            List of milestone events
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        cursor = self.conn.execute(
            """
            SELECT student_id_hash, metadata, timestamp
            FROM observability_events
            WHERE event_type = 'milestone_reached' AND timestamp >= ?
            ORDER BY timestamp DESC
            """,
            (cutoff_date,)
        )

        milestones = []
        for row in cursor.fetchall():
            metadata = json.loads(row['metadata'])
            milestone = metadata.get("milestone", metadata.get("practiced_count", metadata.get("practice_count")))
            practiced_count = metadata.get("practiced_count", metadata.get("practice_count", milestone))
            milestones.append({
                'student_id_hash': row['student_id_hash'],
                'habit_id': metadata.get('habit_id'),
                'milestone': milestone,
                'practiced_count': practiced_count,
                'timestamp': row['timestamp']
            })

        return milestones

    # ============================================================
    # WEEKLY REFLECTIONS METHODS (Task 2.5)
    # Friday reflection gating + week unlock system
    # ============================================================

    def ensure_weekly_reflection_records(self, week_number: int) -> int:
        """
        Ensure every student in the target week has a reflection row.

        Args:
            week_number: Week number to initialize records for

        Returns:
            Number of records inserted
        """
        cursor = self.conn.execute(
            """
            INSERT INTO weekly_reflections (discord_id, week_number)
            SELECT s.discord_id, ?
            FROM students s
            WHERE s.current_week = ?
              AND NOT EXISTS (
                SELECT 1
                FROM weekly_reflections r
                WHERE r.discord_id = s.discord_id
                  AND r.week_number = ?
              )
            """,
            (week_number, week_number, week_number)
        )
        self.conn.commit()
        return cursor.rowcount

    def create_weekly_reflection_record(self, discord_id: str, week_number: int) -> sqlite3.Row:
        """
        Create a new weekly reflection record for a student.

        Args:
            discord_id: Student's Discord user ID
            week_number: Week number (1-8)

        Returns:
            Created reflection row
        """
        discord_id = str(discord_id)
        self.conn.execute(
            """
            INSERT INTO weekly_reflections (discord_id, week_number)
            VALUES (?, ?)
            """,
            (discord_id, week_number)
        )
        self.conn.commit()

        return self.get_weekly_reflection(discord_id, week_number)

    def get_weekly_reflection(self, discord_id: str, week_number: int) -> Optional[sqlite3.Row]:
        """
        Get weekly reflection record for a student.

        Args:
            discord_id: Student's Discord user ID
            week_number: Week number (1-8)

        Returns:
            Reflection row or None if not found
        """
        discord_id = str(discord_id)
        cursor = self.conn.execute(
            """
            SELECT * FROM weekly_reflections
            WHERE discord_id = ? AND week_number = ?
            """,
            (discord_id, week_number)
        )
        return cursor.fetchone()

    def submit_weekly_reflection(
        self,
        discord_id: str,
        week_number: int,
        reflection_content: str,
        proof_of_work: str
    ) -> sqlite3.Row:
        """
        Submit Friday reflection for a student.

        Args:
            discord_id: Student's Discord user ID
            week_number: Week number (1-8)
            reflection_content: Student's reflection text
            proof_of_work: One sentence showing AI understood them

        Returns:
            Updated reflection row
        """
        discord_id = str(discord_id)
        now = datetime.now().isoformat()

        self.conn.execute(
            """
            UPDATE weekly_reflections
            SET reflection_content = ?,
                proof_of_work = ?,
                submitted = 1,
                submitted_at = ?,
                updated_at = ?
            WHERE discord_id = ? AND week_number = ?
            """,
            (reflection_content, proof_of_work, now, now, discord_id, week_number)
        )
        self.conn.commit()

        return self.get_weekly_reflection(discord_id, week_number)

    def get_incomplete_reflections(self, week_number: int) -> List[sqlite3.Row]:
        """
        Get all students who haven't submitted reflection for a week.

        Args:
            week_number: Week number to check

        Returns:
            List of reflection rows where submitted=0
        """
        # Include students with no reflection row yet (LEFT JOIN) so Trevor sees true laggards.
        cursor = self.conn.execute(
            """
            SELECT
                COALESCE(r.id, 0) AS id,
                s.discord_id,
                ? AS week_number,
                r.reflection_content,
                r.proof_of_work,
                COALESCE(r.submitted, 0) AS submitted,
                r.submitted_at,
                COALESCE(r.next_week_unlocked, 0) AS next_week_unlocked,
                r.unlocked_at,
                COALESCE(r.manually_unlocked, 0) AS manually_unlocked,
                r.unlocked_by,
                r.unlock_reason,
                r.created_at,
                r.updated_at,
                s.current_week,
                s.zone
            FROM students s
            LEFT JOIN weekly_reflections r
              ON r.discord_id = s.discord_id
             AND r.week_number = ?
            WHERE s.current_week = ?
              AND COALESCE(r.submitted, 0) = 0
            """,
            (week_number, week_number, week_number)
        )
        return cursor.fetchall()

    def get_submitted_reflections(self, week_number: int) -> List[sqlite3.Row]:
        """
        Get students who submitted reflection for a week.

        Args:
            week_number: Week number to check

        Returns:
            List of reflection rows where submitted=1
        """
        cursor = self.conn.execute(
            """
            SELECT r.*, s.current_week, s.zone
            FROM weekly_reflections r
            JOIN students s ON r.discord_id = s.discord_id
            WHERE r.week_number = ? AND r.submitted = 1
            """,
            (week_number,)
        )
        return cursor.fetchall()

    def unlock_next_week(
        self,
        discord_id: str,
        current_week: int,
        manually_unlocked: bool = False,
        unlocked_by: str = None,
        unlock_reason: str = None
    ) -> sqlite3.Row:
        """
        Unlock next week for a student.

        Args:
            discord_id: Student's Discord user ID
            current_week: Current week number (1-7)
            manually_unlocked: Whether this is a manual override
            unlocked_by: Trevor's discord_id (if manual)
            unlock_reason: Reason for manual unlock

        Returns:
            Updated reflection row
        """
        discord_id = str(discord_id)
        now = datetime.now().isoformat()

        existing = self.get_weekly_reflection(discord_id, current_week)
        if existing is None:
            existing = self.create_weekly_reflection_record(discord_id, current_week)

        if existing and existing['next_week_unlocked'] == 1:
            return existing

        self.conn.execute(
            """
            UPDATE weekly_reflections
            SET next_week_unlocked = 1,
                unlocked_at = ?,
                manually_unlocked = ?,
                unlocked_by = ?,
                unlock_reason = ?,
                updated_at = ?
            WHERE discord_id = ? AND week_number = ?
            """,
            (now, 1 if manually_unlocked else 0, unlocked_by, unlock_reason, now, discord_id, current_week)
        )
        self.conn.commit()

        # Update student's current week if this unlock advances them.
        student = self.get_student(discord_id)
        if student is not None:
            target_week = current_week + 1
            if student['current_week'] < target_week:
                self.update_student_week(discord_id, target_week)

        return self.get_weekly_reflection(discord_id, current_week)

    def batch_unlock_next_week(self, week_number: int) -> int:
        """
        Batch unlock next week for all students who submitted reflections.

        Args:
            week_number: Week number (1-7)

        Returns:
            Number of students unlocked
        """
        now = datetime.now().isoformat()

        # Keep reflection rows complete for all students still in this week.
        self.ensure_weekly_reflection_records(week_number)

        # Capture the exact set that should unlock now to keep the operation idempotent.
        to_unlock_cursor = self.conn.execute(
            """
            SELECT discord_id
            FROM weekly_reflections
            WHERE week_number = ? AND submitted = 1 AND next_week_unlocked = 0
            """,
            (week_number,)
        )
        to_unlock = [row['discord_id'] for row in to_unlock_cursor.fetchall()]
        if not to_unlock:
            return 0

        cursor = self.conn.execute(
            """
            UPDATE weekly_reflections
            SET next_week_unlocked = 1,
                unlocked_at = ?,
                updated_at = ?
            WHERE week_number = ? AND submitted = 1 AND next_week_unlocked = 0
            """,
            (now, now, week_number)
        )
        self.conn.commit()
        unlocked_count = cursor.rowcount

        placeholders = ",".join(["?"] * len(to_unlock))
        target_week = week_number + 1
        self.conn.execute(
            f"""
            UPDATE students
            SET current_week = CASE
                WHEN current_week < ? THEN ?
                ELSE current_week
            END
            WHERE discord_id IN ({placeholders})
            """,
            [target_week, target_week, *to_unlock]
        )
        self.conn.commit()

        return unlocked_count

    def has_unlocked_next_week(self, discord_id: str, week_number: int) -> bool:
        """
        Check if student has unlocked next week.

        Args:
            discord_id: Student's Discord user ID
            week_number: Week number to check

        Returns:
            True if unlocked, False otherwise
        """
        discord_id = str(discord_id)
        cursor = self.conn.execute(
            """
            SELECT next_week_unlocked FROM weekly_reflections
            WHERE discord_id = ? AND week_number = ?
            """,
            (discord_id, week_number)
        )
        row = cursor.fetchone()
        return row and row['next_week_unlocked'] == 1

    def get_reflection_summary(self, week_number: int) -> Dict:
        """
        Get summary of reflection submissions for a week.

        Args:
            week_number: Week number to summarize

        Returns:
            Dict with submission stats
        """
        cursor = self.conn.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(submitted) as submitted_count,
                SUM(next_week_unlocked) as unlocked_count
            FROM weekly_reflections
            WHERE week_number = ?
            """,
            (week_number,)
        )
        row = cursor.fetchone()

        return {
            'week_number': week_number,
            'total_students': row['total'] or 0,
            'submitted_count': row['submitted_count'] or 0,
            'unlocked_count': row['unlocked_count'] or 0,
            'pending_count': (row['total'] or 0) - (row['submitted_count'] or 0)
        }

    def get_all_students(self) -> List[sqlite3.Row]:
        """
        Get all students in the cohort.

        Returns:
            List of student rows
        """
        cursor = self.conn.execute(
            """
            SELECT * FROM students
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()

    def get_weekly_reflections(self, week_number: int) -> List[sqlite3.Row]:
        """
        Get all weekly reflections for a specific week.

        Args:
            week_number: Week number to retrieve

        Returns:
            List of reflection rows
        """
        cursor = self.conn.execute(
            """
            SELECT wr.*, s.zone, s.current_week
            FROM weekly_reflections wr
            JOIN students s ON wr.discord_id = s.discord_id
            WHERE wr.week_number = ?
            ORDER BY wr.submitted_at DESC
            """,
            (week_number,)
        )
        return cursor.fetchall()

    # ============================================================
    # AGENT UNLOCK ANNOUNCEMENTS (Task 3.4)
    # Track graduated agent unlock announcements per Decision 11
    # ============================================================

    def has_announced_unlock(self, week_number: int) -> bool:
        """
        Check if agent unlock announcement has been made for a week.

        Args:
            week_number: Week number to check (1-8)

        Returns:
            True if announcement was made, False otherwise
        """
        cursor = self.conn.execute(
            "SELECT 1 FROM agent_unlock_announcements WHERE week_number = ?",
            (week_number,)
        )
        return cursor.fetchone() is not None

    def record_unlock_announcement(
        self,
        week_number: int,
        agents_unlocked: list,
        channel_id: str = None
    ) -> None:
        """
        Record that an agent unlock announcement was made for a week.

        Args:
            week_number: Week number (1-8)
            agents_unlocked: List of agent names unlocked this week
            channel_id: Discord channel ID where announcement was posted
        """
        now = datetime.now().isoformat()
        agents_json = json.dumps(agents_unlocked)

        self.conn.execute(
            """
            INSERT INTO agent_unlock_announcements (
                week_number, agents_unlocked, announced_at, channel_id
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(week_number) DO UPDATE SET
                agents_unlocked = excluded.agents_unlocked,
                announced_at = excluded.announced_at,
                channel_id = excluded.channel_id
            """,
            (week_number, agents_json, now, str(channel_id) if channel_id else None)
        )
        self.conn.commit()

    def get_unlocked_agents_for_week(self, week_number: int) -> list:
        """
        Get list of agent names unlocked for a given week.

        This replicates the logic from router.py AGENTS_BY_WEEK for database access.

        Args:
            week_number: Week number (1-8)

        Returns:
            List of agent names available this week
        """
        # Agent unlock schedule from Decision 11
        if week_number == 1:
            return ["frame"]
        elif week_number <= 3:
            return ["frame"]
        elif week_number <= 5:
            return ["frame", "diverge", "challenge"]
        elif week_number <= 8:
            return ["frame", "diverge", "challenge", "synthesize", "create-artifact", "save", "review", "edit", "publish"]
        else:
            return ["frame"]  # Default

    def get_announced_agents(self, week_number: int) -> list:
        """
        Get the list of agents that were announced as unlocked for a week.

        Args:
            week_number: Week number (1-8)

        Returns:
            List of agent names (empty list if no announcement made)
        """
        cursor = self.conn.execute(
            "SELECT agents_unlocked FROM agent_unlock_announcements WHERE week_number = ?",
            (week_number,)
        )
        row = cursor.fetchone()
        if row and row['agents_unlocked']:
            return json.loads(row['agents_unlocked'])
        return []

    # ============================================================
    # SHOWCASE PUBLICATIONS (Task 3.5)
    # Track publications to #thinking-showcase (Decision 12)
    # ============================================================

    def create_showcase_publication(
        self,
        discord_id: str,
        publication_type: str,
        visibility_level: str,
        celebration_message: str,
        habits_demonstrated: List[str] = None,
        nodes_mastered: List[float] = None,
        artifact_id: int = None,
        parent_email_included: bool = False
    ) -> int:
        """
        Record a showcase publication to #thinking-showcase.

        Args:
            discord_id: Student's Discord user ID
            publication_type: 'habit_practice' OR 'artifact_completion'
            visibility_level: 'public', 'anonymous', OR 'private'
            celebration_message: The published celebration text
            habits_demonstrated: List of habit icons practiced
            nodes_mastered: List of node numbers mastered
            artifact_id: Foreign key to artifact_progress (if artifact)
            parent_email_included: Whether included in parent email

        Returns:
            Publication record ID
        """
        discord_id = str(discord_id)
        self._ensure_student_record(discord_id)
        habits_json = json.dumps(habits_demonstrated) if habits_demonstrated else None
        nodes_json = json.dumps(nodes_mastered) if nodes_mastered else None

        cursor = self.conn.execute(
            """
            INSERT INTO showcase_publications (
                student_id, publication_type, visibility_level, celebration_message,
                habits_demonstrated, nodes_mastered, artifact_id, parent_email_included
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                discord_id, publication_type, visibility_level, celebration_message,
                habits_json, nodes_json, artifact_id, 1 if parent_email_included else 0
            )
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_student_publications(
        self,
        discord_id: str,
        publication_type: str = None
    ) -> List[sqlite3.Row]:
        """
        Get all publications for a student.

        Args:
            discord_id: Student's Discord user ID
            publication_type: Filter by type (optional)

        Returns:
            List of publication rows
        """
        discord_id = str(discord_id)

        if publication_type:
            cursor = self.conn.execute(
                """
                SELECT * FROM showcase_publications
                WHERE student_id = ? AND publication_type = ?
                ORDER BY timestamp DESC
                """,
                (discord_id, publication_type)
            )
        else:
            cursor = self.conn.execute(
                """
                SELECT * FROM showcase_publications
                WHERE student_id = ?
                ORDER BY timestamp DESC
                """,
                (discord_id,)
            )
        return cursor.fetchall()

    def get_publication_count(self, discord_id: str, publication_type: str = None) -> int:
        """
        Get count of publications for a student.

        Args:
            discord_id: Student's Discord user ID
            publication_type: Filter by type (optional)

        Returns:
            Number of publications
        """
        discord_id = str(discord_id)

        if publication_type:
            cursor = self.conn.execute(
                """
                SELECT COUNT(*) as count FROM showcase_publications
                WHERE student_id = ? AND publication_type = ?
                """,
                (discord_id, publication_type)
            )
        else:
            cursor = self.conn.execute(
                """
                SELECT COUNT(*) as count FROM showcase_publications
                WHERE student_id = ?
                """,
                (discord_id,)
            )
        row = cursor.fetchone()
        return row['count'] if row else 0

    # ============================================================
    # CLUSTER ASSIGNMENT METHODS (Task 4.3)
    # Implement cluster assignment by last name + voice channels
    # ============================================================

    def assign_cluster_by_last_name(self, last_name: str) -> int:
        """
        Assign cluster based on last name with capacity checking (Story 5.1 spec).

        Cluster assignments (8 clusters total):
        - Cluster 1: A-F (first 25 students)
        - Cluster 2: G-L (first 25 students)
        - Cluster 3: M-R (first 25 students)
        - Cluster 4: S-Z (first 25 students)
        - Cluster 5: A-F (26th-50th students)
        - Cluster 6: G-L (26th-50th students)
        - Cluster 7: M-R (26th-50th students)
        - Cluster 8: S-Z (26th-50th students)

        Args:
            last_name: Student's last name

        Returns:
            Cluster ID (1-8)
        """
        if not last_name:
            return 1  # Default to Cluster 1 if no last name

        # Normalize: case-insensitive, get first letter
        last_name = last_name.strip().upper()
        first_char = last_name[0] if last_name else 'A'

        # Determine base cluster group (1-4) by first letter
        if 'A' <= first_char <= 'F':
            base_cluster = 1
        elif 'G' <= first_char <= 'L':
            base_cluster = 2
        elif 'M' <= first_char <= 'R':
            base_cluster = 3
        else:  # S-Z and everything else
            base_cluster = 4

        # Check if base cluster is at capacity (25 students max)
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM students WHERE cluster_id = ?",
            (base_cluster,)
        )
        row = cursor.fetchone()
        current_count = row['count'] if row else 0

        # If base cluster is full, assign to overflow cluster (5-8)
        if current_count >= 25:
            return base_cluster + 4  # Cluster 1→5, 2→6, 3→7, 4→8

        return base_cluster

    def create_student(
        self,
        discord_id,
        cohort_id: str = None,
        last_name: str = None
    ) -> sqlite3.Row:
        """
        Create new student record with cluster assignment (Task 4.3).

        Args:
            discord_id: Student's Discord user ID (int or str)
            cohort_id: Cohort identifier (defaults to COHORT_ID env var)
            last_name: Student's last name for cluster assignment

        Returns:
            Created student row
        """
        discord_id = str(discord_id)  # Normalize: discord.py passes int IDs
        cohort_id = cohort_id or os.getenv('COHORT_ID', 'cohort-1')
        start_date = os.getenv('COHORT_1_START_DATE', datetime.now().strftime('%Y-%m-%d'))

        # Determine cluster from last name
        cluster_id = self.assign_cluster_by_last_name(last_name) if last_name else 1

        self.conn.execute(
            """
            INSERT INTO students (
                discord_id, cohort_id, start_date, current_week,
                current_state, zone, jtbd_concern, emotional_state, cluster_id, last_name
            ) VALUES (?, ?, ?, 1, 'none', 'zone_0', 'career_direction', 'curious', ?, ?)
            """,
            (discord_id, cohort_id, start_date, cluster_id, last_name)
        )
        self.conn.commit()

        # Initialize habit practice records
        for habit_id in [1, 2, 3, 4]:
            self.conn.execute(
                """
                INSERT INTO habit_practice (student_id, habit_id, practiced_count, confidence)
                VALUES (?, ?, 0, 'emerging')
                """,
                (discord_id, habit_id)
            )

        self.conn.commit()

        # Record cluster assignment
        self.conn.execute(
            """
            INSERT INTO cluster_assignments (discord_id, cluster_id, last_name)
            VALUES (?, ?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET
                cluster_id = excluded.cluster_id,
                last_name = excluded.last_name
            """,
            (discord_id, cluster_id, last_name)
        )
        self.conn.commit()

        return self.get_student(discord_id)

    def update_student_cluster(self, discord_id: str, cluster_id: int) -> None:
        """
        Update student's cluster assignment (for Trevor-admin switches).

        Args:
            discord_id: Student's Discord user ID
            cluster_id: New cluster ID (1-8)
        """
        discord_id = str(discord_id)

        # Update students table
        self.conn.execute(
            "UPDATE students SET cluster_id = ? WHERE discord_id = ?",
            (cluster_id, discord_id)
        )

        # Update cluster_assignments table
        self.conn.execute(
            """
            UPDATE cluster_assignments
            SET cluster_id = ?
            WHERE discord_id = ?
            """,
            (cluster_id, discord_id)
        )
        self.conn.commit()

    def request_cluster_switch(
        self,
        discord_id: str,
        new_cluster_id: int,
        reason: str = None
    ) -> bool:
        """
        Process student cluster switch request (Task 4.3).

        Args:
            discord_id: Student's Discord user ID
            new_cluster_id: Desired cluster ID (1-8)
            reason: Reason for switch (optional)

        Returns:
            True if switch successful, False if cluster is full
        """
        discord_id = str(discord_id)

        # Check if new cluster is at capacity (25 students max per spec)
        cursor = self.conn.execute(
            """
            SELECT COUNT(*) as count FROM students
            WHERE cluster_id = ?
            """,
            (new_cluster_id,)
        )
        row = cursor.fetchone()
        current_count = row['count'] if row else 0

        if current_count >= 25:
            return False  # Cluster is full

        # Update cluster assignment
        self.update_student_cluster(discord_id, new_cluster_id)

        # Log the switch reason for Trevor's review
        if reason:
            self.log_observability_event(
                discord_id=discord_id,
                event_type="cluster_switch",
                metadata={
                    "new_cluster_id": new_cluster_id,
                    "reason": reason
                }
            )

        return True

    def get_students_by_cluster(self, cluster_id: int) -> List[sqlite3.Row]:
        """
        Get all students assigned to a specific cluster.

        Args:
            cluster_id: Cluster ID (1-8)

        Returns:
            List of student rows
        """
        cursor = self.conn.execute(
            """
            SELECT * FROM students
            WHERE cluster_id = ?
            ORDER BY last_name ASC
            """,
            (cluster_id,)
        )
        return cursor.fetchall()

    def get_all_cluster_rosters(self) -> List[Dict]:
        """
        Generate roster report for all clusters (Trevor dashboard).

        Returns:
            List of cluster roster dicts with student counts
        """
        rosters = []
        for cluster_id in range(1, 9):  # Clusters 1-8
            cursor = self.conn.execute(
                """
                SELECT
                    c.cluster_id,
                    COUNT(s.discord_id) as student_count,
                    GROUP_CONCAT(s.last_name, ', ') as student_names
                FROM cluster_assignments c
                LEFT JOIN students s ON c.discord_id = s.discord_id
                WHERE c.cluster_id = ?
                GROUP BY c.cluster_id
                """,
                (cluster_id,)
            )
            row = cursor.fetchone()

            rosters.append({
                'cluster_id': cluster_id,
                'student_count': row['student_count'] if row else 0,
                'student_names': row['student_names'] if row and row['student_names'] else ''
            })

        return rosters

    @staticmethod
    async def _call_maybe_async(func, *args, **kwargs):
        """Call a function that may return an awaitable (discord.py mocks or real API)."""
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    async def create_cluster_voice_channel(
        self,
        guild,
        cluster_id: int,
        bot=None,
        facilitator_role=None
    ):
        """
        Create a temporary voice channel for a cluster live session.

        Returns:
            Created channel object, existing channel if one already exists, or None on failure.
        """
        channel_prefix = f"cluster-{cluster_id}"
        channel_name = f"{channel_prefix}-voice"

        # Prevent duplicate channels for the same cluster.
        voice_channels = getattr(guild, "voice_channels", [])
        if not isinstance(voice_channels, (list, tuple, set)):
            voice_channels = []

        channel = None
        for existing in voice_channels:
            existing_name = str(getattr(existing, "name", "")).lower()
            if channel_prefix in existing_name:
                channel = existing
                break

        if channel is None:
            create_channel = getattr(guild, "create_voice_channel", None)
            if callable(create_channel):
                try:
                    channel = await self._call_maybe_async(create_channel, channel_name)
                except Exception as exc:
                    logger.warning(
                        "Failed to create Discord voice channel for cluster %s: %s",
                        cluster_id,
                        exc,
                    )

        if channel is None:
            # Test-friendly fallback when guild mocks do not implement channel creation.
            from unittest.mock import Mock
            channel = Mock()
            channel.name = channel_name

        channel_current_name = getattr(channel, "name", None)
        if not isinstance(channel_current_name, str) or not channel_current_name.strip():
            channel.name = channel_name

        channel_current_id = getattr(channel, "id", None)
        if not isinstance(channel_current_id, (str, int)) or channel_current_id in ("", 0):
            channel.id = int(datetime.now().timestamp() * 1000)

        # Apply role permissions if available.
        set_permissions = getattr(channel, "set_permissions", None)
        if callable(set_permissions):
            guild_roles = getattr(guild, "roles", []) or []
            cluster_role = None
            if isinstance(guild_roles, (list, tuple, set)):
                for role in guild_roles:
                    if str(getattr(role, "name", "")) == f"Cluster-{cluster_id}":
                        cluster_role = role
                        break

                if facilitator_role is None:
                    for role in guild_roles:
                        if str(getattr(role, "name", "")) == "Facilitator":
                            facilitator_role = role
                            break

            default_role = getattr(guild, "default_role", None)
            if default_role is not None:
                await self._call_maybe_async(
                    set_permissions,
                    default_role,
                    connect=False,
                    speak=False,
                    view_channel=False,
                )

            if cluster_role is not None:
                await self._call_maybe_async(
                    set_permissions,
                    cluster_role,
                    connect=True,
                    speak=True,
                    view_channel=True,
                )

            if facilitator_role is not None:
                await self._call_maybe_async(
                    set_permissions,
                    facilitator_role,
                    connect=True,
                    speak=True,
                    view_channel=True,
                )

        # Track active voice channel in DB.
        self.conn.execute(
            """
            INSERT INTO voice_channels (
                cluster_id, channel_id, channel_name, session_date, is_active
            ) VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(channel_id) DO UPDATE SET
                cluster_id = excluded.cluster_id,
                channel_name = excluded.channel_name,
                session_date = excluded.session_date,
                deleted_at = NULL,
                is_active = 1
            """,
            (
                cluster_id,
                str(channel.id),
                channel_name,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()

        return channel

    async def delete_cluster_voice_channel(self, channel) -> None:
        """Delete a cluster voice channel and mark it inactive in DB."""
        delete_method = getattr(channel, "delete", None)
        if callable(delete_method):
            await self._call_maybe_async(delete_method)

        channel_id = str(getattr(channel, "id", ""))
        if channel_id:
            self.conn.execute(
                """
                UPDATE voice_channels
                SET deleted_at = ?, is_active = 0
                WHERE channel_id = ?
                """,
                (datetime.now().isoformat(), channel_id),
            )
            self.conn.commit()

    def get_active_voice_channel_id(self, cluster_id: int) -> Optional[str]:
        """
        Return the most recently tracked active voice channel for a cluster.

        Used to recover cleanup state after bot restarts.
        """
        cursor = self.conn.execute(
            """
            SELECT channel_id
            FROM voice_channels
            WHERE cluster_id = ? AND is_active = 1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (cluster_id,),
        )
        row = cursor.fetchone()
        return row["channel_id"] if row else None

    def mark_voice_channel_deleted(self, channel_id: str) -> None:
        """Mark a voice channel inactive when it no longer exists in Discord."""
        self.conn.execute(
            """
            UPDATE voice_channels
            SET deleted_at = ?, is_active = 0
            WHERE channel_id = ?
            """,
            (datetime.now().isoformat(), str(channel_id)),
        )
        self.conn.commit()

    def record_session_attendance(
        self,
        cluster_id: int,
        session_date: str,
        attendees: List[str] = None,
        attendance_count: Optional[int] = None,
    ) -> None:
        """
        Record attendance for a cluster live session.

        Args:
            cluster_id: Cluster ID (1-8)
            session_date: ISO timestamp of session
            attendees: List of discord_id strings who attended
            attendance_count: Optional numeric attendance when only count is known
        """
        attendees = attendees or []
        attendees_json = json.dumps(attendees)

        # Get total students in cluster
        cursor = self.conn.execute(
            "SELECT COUNT(*) as count FROM students WHERE cluster_id = ?",
            (cluster_id,)
        )
        total_students = cursor.fetchone()['count']
        attendee_count = len(attendees)

        # If caller only provides an attendance count, persist accurate absent totals.
        if attendee_count == 0 and attendance_count is not None:
            attendee_count = max(0, min(int(attendance_count), total_students))

        absent_count = max(total_students - attendee_count, 0)

        self.conn.execute(
            """
            INSERT INTO cluster_session_attendance (
                cluster_id, session_date, attendees, total_students, absent_count
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(cluster_id, session_date) DO UPDATE SET
                attendees = excluded.attendees,
                total_students = excluded.total_students,
                absent_count = excluded.absent_count
            """,
            (cluster_id, session_date, attendees_json, total_students, absent_count)
        )
        self.conn.commit()

    def get_cluster_attendance(self, cluster_id: int, limit: int = 10) -> Dict:
        """
        Get attendance history for a cluster.

        Args:
            cluster_id: Cluster ID (1-8)
            limit: Maximum sessions to return

        Returns:
            Dict with attendance stats and recent sessions
        """
        cursor = self.conn.execute(
            """
            SELECT * FROM cluster_session_attendance
            WHERE cluster_id = ?
            ORDER BY session_date DESC
            LIMIT ?
            """,
            (cluster_id, limit)
        )

        sessions = []
        for row in cursor.fetchall():
            attendees = json.loads(row['attendees']) if row['attendees'] else []
            attendee_count = len(attendees)
            if attendee_count == 0 and row['total_students'] is not None and row['absent_count'] is not None:
                attendee_count = max(row['total_students'] - row['absent_count'], 0)
            sessions.append({
                'session_date': row['session_date'],
                'attendees': attendees,
                'attendee_count': attendee_count,
                'absent': row['absent_count'],
                'total': row['total_students']
            })

        return {
            'cluster_id': cluster_id,
            'recent_sessions': sessions
        }

    # ============================================================
    # STUDENT PUBLICATION PREFERENCES (Task 3.5)
    # Manage default sharing settings to reduce decision fatigue
    # ============================================================

    def get_publication_preference(self, discord_id: str) -> str:
        """
        Get student's default publication preference.

        Args:
            discord_id: Student's Discord user ID

        Returns:
            Preference: 'always_ask', 'always_yes', 'always_no', 'week8_only'
        """
        discord_id = str(discord_id)
        cursor = self.conn.execute(
            "SELECT default_preference FROM student_publication_preferences WHERE student_id = ?",
            (discord_id,)
        )
        row = cursor.fetchone()
        return row['default_preference'] if row else 'always_ask'

    def set_publication_preference(
        self,
        discord_id: str,
        preference: str
    ) -> None:
        """
        Set student's default publication preference.

        Args:
            discord_id: Student's Discord user ID
            preference: 'always_ask', 'always_yes', 'always_no', 'week8_only'
        """
        discord_id = str(discord_id)
        if preference not in VALID_PUBLICATION_PREFERENCES:
            raise ValueError(
                f"Invalid publication preference '{preference}'. "
                f"Valid options: {sorted(VALID_PUBLICATION_PREFERENCES)}"
            )
        self._ensure_student_record(discord_id)
        now = datetime.now().isoformat()

        self.conn.execute(
            """
            INSERT INTO student_publication_preferences (student_id, default_preference, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                default_preference = excluded.default_preference,
                updated_at = excluded.updated_at
            """,
            (discord_id, preference, now)
        )
        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Cleanup on deletion"""
        self.close()

    # ============================================================
    # PARENT ENGAGEMENT METHODS (Task 4.6)
    # Parent consent tracking and email communication
    # ============================================================

    def set_parent_consent(
        self,
        discord_id: str,
        parent_email: str,
        consent_preference: str = 'privacy_first'
    ) -> None:
        """
        Set parent email consent preference for a student.

        Args:
            discord_id: Student's Discord user ID
            parent_email: Parent's email address
            consent_preference: 'share_weekly' OR 'privacy_first'
        """
        discord_id = str(discord_id)
        if consent_preference not in ('share_weekly', 'privacy_first'):
            raise ValueError(
                f"Invalid consent_preference '{consent_preference}'. "
                "Must be 'share_weekly' or 'privacy_first'."
            )

        self._ensure_student_record(discord_id)
        import secrets
        now = datetime.now().isoformat()

        # Generate unsubscribe token if not exists
        cursor = self.conn.execute(
            "SELECT unsubscribe_token FROM parent_engagement WHERE student_id = ?",
            (discord_id,)
        )
        existing = cursor.fetchone()

        unsubscribe_token = existing['unsubscribe_token'] if existing else secrets.token_urlsafe(32)

        self.conn.execute(
            """
            INSERT INTO parent_engagement (
                student_id,
                parent_email,
                consent_preference,
                consent_date,
                unsubscribe_token,
                parent_opted_out,
                parent_opted_out_at,
                parent_email_status
            ) VALUES (?, ?, ?, ?, ?, 0, NULL, 'active')
            ON CONFLICT(student_id) DO UPDATE SET
                parent_email = excluded.parent_email,
                consent_preference = excluded.consent_preference,
                consent_date = excluded.consent_date,
                unsubscribe_token = excluded.unsubscribe_token,
                parent_opted_out = 0,
                parent_opted_out_at = NULL,
                parent_email_status = 'active'
            """,
            (discord_id, parent_email, consent_preference, now, unsubscribe_token)
        )
        self.conn.commit()

    def get_parent_consent(self, discord_id: str) -> Optional[sqlite3.Row]:
        """
        Get parent consent record for a student.

        Args:
            discord_id: Student's Discord user ID

        Returns:
            Parent engagement row or None if not found
        """
        discord_id = str(discord_id)
        cursor = self.conn.execute(
            "SELECT * FROM parent_engagement WHERE student_id = ?",
            (discord_id,)
        )
        return cursor.fetchone()

    def update_parent_consent(
        self,
        discord_id: str,
        consent_preference: str
    ) -> None:
        """
        Update parent consent preference.

        Args:
            discord_id: Student's Discord user ID
            consent_preference: 'share_weekly' OR 'privacy_first'
        """
        discord_id = str(discord_id)
        if consent_preference not in ('share_weekly', 'privacy_first'):
            raise ValueError(
                f"Invalid consent_preference '{consent_preference}'. "
                "Must be 'share_weekly' or 'privacy_first'."
            )

        self.conn.execute(
            """
            UPDATE parent_engagement
            SET consent_preference = ?,
                consent_date = ?,
                parent_opted_out = 0,
                parent_opted_out_at = NULL,
                parent_email_status = 'active'
            WHERE student_id = ?
            """,
            (consent_preference, datetime.now().isoformat(), discord_id)
        )
        self.conn.commit()

    def get_weekly_email_recipients(self) -> List[Dict]:
        """
        Get all students whose parents opted in for weekly updates.

        Returns:
            List of dicts with student_id, parent_email, student_name, etc.
        """
        cursor = self.conn.execute(
            """
            SELECT
                pe.student_id,
                pe.parent_email,
                pe.unsubscribe_token,
                s.discord_id,
                s.current_week,
                s.zone,
                s.interaction_count
            FROM parent_engagement pe
            JOIN students s ON pe.student_id = s.discord_id
            WHERE pe.consent_preference = 'share_weekly'
              AND COALESCE(pe.parent_opted_out, 0) = 0
            ORDER BY s.current_week DESC
            """
        )

        return [dict(row) for row in cursor.fetchall()]

    def _get_week_time_window(self, week_number: int) -> Tuple[str, str]:
        """
        Build ISO date window for a cohort week.

        Args:
            week_number: Cohort week number (1-8)

        Returns:
            Tuple of (week_start_iso, week_end_iso) for SQL filtering.
        """
        start_date_str = os.getenv('COHORT_1_START_DATE', datetime.now().strftime('%Y-%m-%d'))
        cohort_start = datetime.strptime(start_date_str, '%Y-%m-%d')
        week_index = max(week_number - 1, 0)
        week_start = cohort_start + timedelta(days=week_index * 7)
        week_end = week_start + timedelta(days=7)
        return (week_start.isoformat(), week_end.isoformat())

    def get_weekly_conversation_count(self, discord_id: str, week_number: int) -> int:
        """
        Count student conversations within a specific cohort week.

        Args:
            discord_id: Student's Discord user ID
            week_number: Cohort week number (1-8)

        Returns:
            Number of conversation messages in the target week window.
        """
        discord_id = str(discord_id)
        week_start, week_end = self._get_week_time_window(week_number)
        cursor = self.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM conversations
            WHERE student_id = ?
              AND created_at >= ?
              AND created_at < ?
            """,
            (discord_id, week_start, week_end)
        )
        row = cursor.fetchone()
        return row['count'] if row else 0

    def get_weekly_reflection_highlight(self, discord_id: str, week_number: int) -> Dict[str, Optional[str]]:
        """
        Fetch reflection context for parent weekly highlights.

        Args:
            discord_id: Student's Discord user ID
            week_number: Cohort week number (1-8)

        Returns:
            Dict containing habit_focus, habit_practice, identity_shift, proof_of_work.
        """
        row = self.get_weekly_reflection(discord_id, week_number)
        result = {
            'habit_focus': None,
            'habit_practice': None,
            'identity_shift': None,
            'proof_of_work': None,
        }

        if not row:
            return result

        reflection_content = row['reflection_content'] or ''
        for raw_line in reflection_content.splitlines():
            line = raw_line.strip()
            if line.lower().startswith('habit focus:'):
                result['habit_focus'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('habit practice:'):
                result['habit_practice'] = line.split(':', 1)[1].strip().lower()
            elif line.lower().startswith('identity shift:'):
                result['identity_shift'] = line.split(':', 1)[1].strip()

        result['proof_of_work'] = row['proof_of_work']
        return result

    def get_week8_email_recipients(self) -> List[Dict]:
        """
        Get recipients for Week 8 parent report emails.

        Includes students with published artifacts and active (non-opted-out) parent records.
        Includes both share_weekly and privacy_first students so "privacy until Week 8"
        can still receive the final report when allowed.

        Returns:
            List of recipient/context dictionaries.
        """
        cursor = self.conn.execute(
            """
            SELECT
                pe.student_id,
                pe.parent_email,
                pe.unsubscribe_token,
                pe.consent_preference,
                s.discord_id,
                s.zone,
                ap.section_1_question,
                ap.section_2_reframed,
                ap.section_3_explored,
                ap.section_4_challenged,
                ap.section_5_concluded,
                ap.section_6_reflection,
                ap.status AS artifact_status,
                COALESCE(pub.visibility_level, 'private') AS visibility_level
            FROM parent_engagement pe
            JOIN students s ON pe.student_id = s.discord_id
            JOIN artifact_progress ap ON ap.student_id = s.discord_id
            LEFT JOIN (
                SELECT sp.student_id, sp.visibility_level
                FROM showcase_publications sp
                JOIN (
                    SELECT student_id, MAX(timestamp) AS max_ts
                    FROM showcase_publications
                    WHERE publication_type = 'artifact_completion'
                    GROUP BY student_id
                ) latest
                  ON latest.student_id = sp.student_id
                 AND latest.max_ts = sp.timestamp
            ) pub ON pub.student_id = s.discord_id
            WHERE COALESCE(pe.parent_opted_out, 0) = 0
              AND ap.status = 'published'
              AND NOT EXISTS (
                  SELECT 1
                  FROM parent_email_log pel
                  WHERE pel.student_id = s.discord_id
                    AND pel.email_type = 'week8_showcase'
                    AND pel.status = 'sent'
              )
            ORDER BY s.discord_id
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def has_weekly_update_sent(self, discord_id: str, report_week: int) -> bool:
        """
        Return True if this student already received a successful weekly update for report_week.

        Used to make weekly sends idempotent across process restarts.
        """
        discord_id = str(discord_id)
        subject_pattern = f"%Week {report_week}"
        cursor = self.conn.execute(
            """
            SELECT 1
            FROM parent_email_log
            WHERE student_id = ?
              AND email_type = 'weekly_update'
              AND status = 'sent'
              AND subject LIKE ?
            LIMIT 1
            """,
            (discord_id, subject_pattern),
        )
        return cursor.fetchone() is not None

    def log_parent_email(
        self,
        discord_id: str,
        parent_email: str,
        email_type: str,
        subject: str,
        status: str = 'sent',
        error_message: str = None
    ) -> int:
        """
        Log a parent email sent for monitoring and debugging.

        Args:
            discord_id: Student's Discord user ID
            parent_email: Parent's email address
            email_type: 'weekly_update', 'week8_showcase', 'artifact_completion'
            subject: Email subject line
            status: 'sent', 'failed', 'bounced', 'skipped'
            error_message: Error details if failed

        Returns:
            Email log ID
        """
        discord_id = str(discord_id)
        cursor = self.conn.execute(
            """
            INSERT INTO parent_email_log (
                student_id, parent_email, email_type, subject, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (discord_id, parent_email, email_type, subject, status, error_message)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_parent_email_sent(self, discord_id: str) -> None:
        """
        Update last_email_sent timestamp after successful send.

        Args:
            discord_id: Student's Discord user ID
        """
        discord_id = str(discord_id)
        self.conn.execute(
            """
            UPDATE parent_engagement
            SET last_email_sent = ?,
                parent_email_status = 'active'
            WHERE student_id = ?
            """,
            (datetime.now().isoformat(), discord_id)
        )
        self.conn.commit()

    def update_parent_email_status(self, discord_id: str, status: str) -> None:
        """
        Update parent email deliverability status.

        Args:
            discord_id: Student's Discord user ID
            status: 'active', 'bounced', or 'opted_out'
        """
        if status not in ("active", "bounced", "opted_out"):
            raise ValueError(f"Invalid parent email status: {status}")

        discord_id = str(discord_id)
        self.conn.execute(
            """
            UPDATE parent_engagement
            SET parent_email_status = ?
            WHERE student_id = ?
            """,
            (status, discord_id)
        )
        self.conn.commit()

    def get_parent_email_stats(self, days: int = 7) -> Dict:
        """
        Get parent email statistics for Trevor dashboard.

        Args:
            days: Number of days to look back

        Returns:
            Dict with email stats (sent, failed, bounced counts)
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        cursor = self.conn.execute(
            """
            SELECT
                email_type,
                status,
                COUNT(*) as count
            FROM parent_email_log
            WHERE sent_at >= ?
            GROUP BY email_type, status
            """,
            (cutoff_date,)
        )

        stats = {
            'period_days': days,
            'total_sent': 0,
            'total_failed': 0,
            'by_type': {}
        }

        for row in cursor.fetchall():
            email_type = row['email_type']
            status = row['status']
            count = row['count']

            if email_type not in stats['by_type']:
                stats['by_type'][email_type] = {'sent': 0, 'failed': 0, 'bounced': 0, 'skipped': 0}

            if status not in stats['by_type'][email_type]:
                stats['by_type'][email_type][status] = 0

            stats['by_type'][email_type][status] = count

            if status == 'sent':
                stats['total_sent'] += count
            elif status in ('failed', 'bounced'):
                stats['total_failed'] += count

        return stats

    def revoke_parent_consent_by_token(self, unsubscribe_token: str) -> bool:
        """
        Revoke parent consent via unsubscribe token.

        Args:
            unsubscribe_token: Unique unsubscribe token from email

        Returns:
            True if revoked, False if token not found
        """
        cursor = self.conn.execute(
            """
            UPDATE parent_engagement
            SET consent_preference = 'privacy_first',
                parent_opted_out = 1,
                parent_opted_out_at = ?,
                parent_email_status = 'opted_out'
            WHERE unsubscribe_token = ?
            """,
            (datetime.now().isoformat(), unsubscribe_token)
        )
        self.conn.commit()
        return cursor.rowcount > 0
