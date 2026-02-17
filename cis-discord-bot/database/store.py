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
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path


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
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name

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

    def get_student(self, discord_id: str) -> Optional[sqlite3.Row]:
        """
        Retrieve student by Discord ID

        Args:
            discord_id: Student's Discord user ID

        Returns:
            Student row or None if not found
        """
        cursor = self.conn.execute(
            "SELECT * FROM students WHERE discord_id = ?",
            (discord_id,)
        )
        return cursor.fetchone()

    def create_student(self, discord_id: str, cohort_id: str = "cohort-1") -> sqlite3.Row:
        """
        Create new student record

        Args:
            discord_id: Student's Discord user ID
            cohort_id: Cohort identifier

        Returns:
            Created student row
        """
        start_date = datetime.now().isoformat()

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
        self.conn.execute(
            "UPDATE students SET zone = ? WHERE discord_id = ?",
            (zone, discord_id)
        )
        self.conn.commit()

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

    def log_observability_event(
        self,
        discord_id: str,
        event_type: str,
        metadata: Dict
    ):
        """
        Log observability event for Trevor dashboard

        Args:
            discord_id: Student's Discord user ID
            event_type: Event type (agent_used, stuck_detected, etc.)
            metadata: Event metadata as dictionary
        """
        # Hash student ID for privacy
        student_id_hash = hashlib.sha256(discord_id.encode()).hexdigest()[:16]

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

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
