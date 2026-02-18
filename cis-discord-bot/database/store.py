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
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Consent records are short-lived to preserve student control over private process.
DEFAULT_JOURNEY_CONSENT_TTL_HOURS = 24

class StudentStateStore:
    """Database operations for student state and conversations"""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file. Defaults to cohort-1.db
        """
        if db_path is None:
            # Default: database in project root
            project_root = Path(__file__).parent.parent
            db_path = project_root / "cohort-1.db"

        self.db_path = db_path
        self.conn = None
        self._connect()
        self._initialize_schema()

    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        # SQLite does not enforce foreign keys unless explicitly enabled per connection.
        self.conn.execute("PRAGMA foreign_keys = ON")

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
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                self.conn.executescript(schema_sql)
                self.conn.commit()
        else:
            # Fallback: create tables directly
            self._create_tables_fallback()

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
        start_date = os.getenv('COHORT_START_DATE', datetime.now().strftime('%Y-%m-%d'))

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
        cursor = self.conn.execute(
            """
            SELECT r.*, s.current_week, s.zone
            FROM weekly_reflections r
            JOIN students s ON r.discord_id = s.discord_id
            WHERE r.week_number = ? AND r.submitted = 0
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

        # Update student's current week
        self.update_student_week(discord_id, current_week + 1)

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

        # Unlock all submitted reflections
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

        # Update all students' current_week
        self.conn.execute(
            """
            UPDATE students
            SET current_week = current_week + 1
            WHERE discord_id IN (
                SELECT discord_id FROM weekly_reflections
                WHERE week_number = ? AND submitted = 1 AND next_week_unlocked = 1
            )
            """,
            (week_number,)
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

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
