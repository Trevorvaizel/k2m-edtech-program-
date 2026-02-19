"""
Database CRUD and Index Verification Tests
Story 4.7 Implementation: StudentContext & Database Schema
Task 1.2: Test CRUD operations and verify indexes

Comprehensive tests for database operations, indexes, and multi-cohort support.
"""

import pytest
import sqlite3
import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.store import StudentStateStore
from database.models import ArtifactProgress, StudentContext, build_student_context


@pytest.fixture
def test_db_path(tmp_path):
    """Create temporary test database"""
    db_path = tmp_path / "test_cohort.db"
    yield str(db_path)

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def store(test_db_path):
    """Create test database store"""
    state_store = StudentStateStore(db_path=test_db_path)
    yield state_store
    state_store.close()


class TestStudentCRUD:
    """Test student CRUD operations"""

    def test_create_student(self, store):
        """Test creating a new student"""
        student = store.create_student(
            discord_id="123456789",
            cohort_id="test-cohort-1"
        )

        assert student is not None
        assert student["discord_id"] == "123456789"
        assert student["cohort_id"] == "test-cohort-1"
        assert student["current_week"] == 1
        assert student["zone"] == "zone_0"

    def test_get_existing_student(self, store):
        """Test retrieving an existing student"""
        # Create student
        store.create_student(discord_id="123456789")

        # Get student
        student = store.get_student("123456789")

        assert student is not None
        assert student["discord_id"] == "123456789"

    def test_get_nonexistent_student(self, store):
        """Test retrieving a non-existent student"""
        student = store.get_student("999999999")
        assert student is None

    def test_update_student_week(self, store):
        """Test updating student's current week"""
        store.create_student(discord_id="123456789")
        store.update_student_week("123456789", week=3)

        student = store.get_student("123456789")
        assert student["current_week"] == 3

    def test_update_student_zone(self, store):
        """Test updating student's zone"""
        store.create_student(discord_id="123456789")
        store.update_student_zone("123456789", zone="zone_2")

        student = store.get_student("123456789")
        assert student["zone"] == "zone_2"

        cursor = store.conn.execute(
            """
            SELECT event_type, metadata
            FROM observability_events
            WHERE student_id_hash = ?
              AND event_type = 'zone_shift'
            """,
            (hashlib.sha256("123456789".encode()).hexdigest()[:16],),
        )
        row = cursor.fetchone()
        assert row is not None
        payload = json.loads(row["metadata"])
        assert payload["from_zone"] == "zone_0"
        assert payload["to_zone"] == "zone_2"
        assert payload["week"] == 1

    def test_discord_id_normalization(self, store):
        """Test that Discord IDs are normalized to strings"""
        # Create with int ID (discord.py passes ints)
        store.create_student(discord_id=123456789)

        # Retrieve with string
        student = store.get_student("123456789")
        assert student is not None

        # Retrieve with int
        student = store.get_student(123456789)
        assert student is not None


class TestConversationCRUD:
    """Test conversation CRUD operations"""

    def test_save_conversation(self, store):
        """Test saving conversation message"""
        store.create_student(discord_id="123456789")

        store.save_conversation(
            discord_id="123456789",
            agent="frame",
            role="user",
            content="Help me frame my question"
        )

        student = store.get_student("123456789")
        assert student["interaction_count"] == 1

    def test_get_conversation_history(self, store):
        """Test retrieving conversation history"""
        store.create_student(discord_id="123456789")

        # Save multiple messages
        store.save_conversation("123456789", "frame", "user", "Message 1")
        store.save_conversation("123456789", "frame", "assistant", "Response 1")
        store.save_conversation("123456789", "frame", "user", "Message 2")

        # Get history
        history = store.get_conversation_history("123456789", "frame", limit=10)

        assert len(history) == 3
        assert history[0]["role"] == "user"  # First message
        assert history[1]["role"] == "assistant"


class TestHabitPracticeCRUD:
    """Test habit practice tracking"""

    def test_habit_practice_initialized(self, store):
        """Test that habit practice records are created for new student"""
        student = store.create_student(discord_id="123456789")

        # Check habit practice table
        cursor = store.conn.execute(
            "SELECT COUNT(*) FROM habit_practice WHERE student_id = ?",
            ("123456789",)
        )
        count = cursor.fetchone()[0]

        assert count == 4  # 4 habits initialized

    def test_update_habit_practice(self, store):
        """Test updating habit practice count"""
        store.create_student(discord_id="123456789")

        # Update habit 1 (Pause)
        store.update_habit_practice("123456789", habit_id=1)

        # Verify
        cursor = store.conn.execute(
            "SELECT practiced_count FROM habit_practice WHERE student_id = ? AND habit_id = ?",
            ("123456789", 1)
        )
        count = cursor.fetchone()[0]

        assert count == 1


class TestObservabilityEvents:
    """Test observability event logging"""

    def test_log_observability_event(self, store):
        """Test logging observability event"""
        store.log_observability_event(
            discord_id="123456789",
            event_type="agent_used",
            metadata={"agent": "frame", "week": 1}
        )

        # Verify event was logged
        cursor = store.conn.execute(
            "SELECT COUNT(*) FROM observability_events WHERE student_id_hash = ?",
            (hashlib.sha256("123456789".encode()).hexdigest()[:16],)
        )
        count = cursor.fetchone()[0]

        assert count == 1

    def test_get_stuck_students_logs_stuck_detected(self, store):
        """Students flagged as stuck should emit stuck_detected events."""
        store.create_student(discord_id="inactive-student")

        stuck = store.get_stuck_students(inactive_days=3)
        assert len(stuck) == 1

        student_hash = hashlib.sha256("inactive-student".encode()).hexdigest()[:16]
        cursor = store.conn.execute(
            """
            SELECT event_type, metadata
            FROM observability_events
            WHERE student_id_hash = ?
              AND event_type = 'stuck_detected'
            """,
            (student_hash,),
        )
        row = cursor.fetchone()
        assert row is not None
        payload = json.loads(row["metadata"])
        assert payload["inactive_days"] == 3

    def test_get_milestone_celebrations_supports_legacy_metadata(self, store):
        """Compatibility path: reads practice_count when milestone key is missing."""
        student_hash = hashlib.sha256("legacy-student".encode()).hexdigest()[:16]
        store.conn.execute(
            """
            INSERT INTO observability_events (student_id_hash, event_type, metadata, timestamp)
            VALUES (?, 'milestone_reached', ?, ?)
            """,
            (
                student_hash,
                '{"habit_id": 1, "practice_count": 7}',
                datetime.now().isoformat(),
            ),
        )
        store.conn.commit()

        milestones = store.get_milestone_celebrations(days=7)
        assert len(milestones) == 1
        assert milestones[0]["milestone"] == 7
        assert milestones[0]["practiced_count"] == 7


class TestConsentRecords:
    """Consent gates for Guardrail #8 journey inspection."""

    def test_record_and_verify_active_consent(self, store):
        store.record_student_consent("123456789", consent_type="journey_inspection", ttl_hours=24)
        assert store.has_active_student_consent("123456789", consent_type="journey_inspection") is True

    def test_revoke_consent(self, store):
        store.record_student_consent("123456789", consent_type="journey_inspection", ttl_hours=24)
        store.revoke_student_consent("123456789", consent_type="journey_inspection")
        assert store.has_active_student_consent("123456789", consent_type="journey_inspection") is False

    def test_expired_consent_is_inactive(self, store):
        store.record_student_consent("123456789", consent_type="journey_inspection", ttl_hours=1)
        student_hash = hashlib.sha256("123456789".encode()).hexdigest()[:16]
        store.conn.execute(
            """
            UPDATE student_consents
            SET expires_at = ?
            WHERE student_id_hash = ? AND consent_type = 'journey_inspection'
            """,
            ("2000-01-01T00:00:00", student_hash),
        )
        store.conn.commit()
        assert store.has_active_student_consent("123456789", consent_type="journey_inspection") is False


class TestStudentContextORM:
    """Test StudentContext ORM"""

    def test_build_student_context(self, store):
        """Test building StudentContext from database row"""
        store.create_student(discord_id="123456789")

        student = store.get_student("123456789")
        context = build_student_context(student, conn=store.conn)

        assert isinstance(context, StudentContext)
        assert context.discord_id == "123456789"
        assert context.current_week == 1
        assert context.zone == "zone_0"
        assert len(context.habit_journey) == 4
        assert context.habit_journey[1].name == "PAUSE"

    def test_student_context_loads_artifact_progress(self, store):
        """Test that artifact_progress is loaded from DB table."""
        store.create_student(discord_id="student-artifact")
        store.conn.execute(
            """
            INSERT INTO artifact_progress (
                student_id, section_1_question, completed_sections, current_section, status
            ) VALUES (?, ?, ?, ?, ?)
            """,
            ("student-artifact", "What should I build?", "[\"section_1_question\"]", 2, "in_progress"),
        )
        store.conn.commit()

        student = store.get_student("student-artifact")
        context = build_student_context(student, conn=store.conn)

        assert context.artifact_progress.section_1_question == "What should I build?"
        assert context.artifact_progress.current_section == 2
        assert context.artifact_progress.status == "in_progress"
        assert context.artifact_progress.completed_sections == ["section_1_question"]

    def test_update_artifact_section_tracks_unique_keys_and_next_section(self, store):
        """Artifact section updates should not duplicate completed keys."""
        discord_id = "artifact-tracking"
        store.create_student(discord_id=discord_id)
        store.save_artifact_progress(discord_id, ArtifactProgress(status="in_progress"))

        store.update_artifact_section(discord_id, 1, "First version")
        store.update_artifact_section(discord_id, 1, "Revised version")

        row = store.get_artifact_progress_row(discord_id)
        completed = json.loads(row["completed_sections"])

        assert completed == ["section_1_question"]
        assert row["current_section"] == 2

    def test_student_context_get_altitude(self, store):
        """Test altitude calculation based on week"""
        store.create_student(discord_id="123456789")

        student = store.get_student("123456789")

        # Week 1
        student_week1 = dict(student)
        student_week1["current_week"] = 1
        context1 = build_student_context(student_week1)
        assert "Ground" in context1.get_altitude()

        # Week 4
        student_week4 = dict(student)
        student_week4["current_week"] = 4
        context4 = build_student_context(student_week4)
        assert "Framework" in context4.get_altitude()


class TestDatabaseIndexes:
    """Verify database indexes exist and work"""

    @pytest.fixture
    def verify_indexes(self, test_db_path):
        """Helper to verify indexes exist"""
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
        )
        indexes = [row[0] for row in cursor.fetchall()]

        conn.close()
        return indexes

    def test_students_table_indexes(self, store, verify_indexes):
        """Verify students table indexes exist"""
        expected_indexes = [
            "idx_students_cohort",
            "idx_students_week",
            "idx_students_zone"
        ]

        for index in expected_indexes:
            assert index in verify_indexes, f"Missing index: {index}"

    def test_habit_practice_indexes(self, store, verify_indexes):
        """Verify habit_practice table indexes exist"""
        assert "idx_habit_student" in verify_indexes

    def test_conversations_indexes(self, store, verify_indexes):
        """Verify conversations table indexes exist"""
        expected_indexes = [
            "idx_conversations_student",
            "idx_conversations_agent",
            "idx_conversations_created"
        ]

        for index in expected_indexes:
            assert index in verify_indexes, f"Missing index: {index}"

    def test_observability_indexes(self, store, verify_indexes):
        """Verify observability_events table indexes exist"""
        expected_indexes = [
            "idx_observability_student",
            "idx_observability_type",
            "idx_observability_timestamp"
        ]

        for index in expected_indexes:
            assert index in verify_indexes, f"Missing index: {index}"

    def test_consent_indexes(self, store, verify_indexes):
        """Verify student_consents indexes exist"""
        expected_indexes = [
            "idx_consents_lookup",
            "idx_consents_expiry",
        ]

        for index in expected_indexes:
            assert index in verify_indexes, f"Missing index: {index}"

    def test_index_query_performance(self, store):
        """Test that indexes improve query performance"""
        import time

        # Create test data
        for i in range(100):
            store.create_student(discord_id=f"student_{i}")

        # Test indexed query
        start = time.time()
        for _ in range(10):
            store.conn.execute(
                "SELECT * FROM students WHERE cohort_id = ?",
                ("test-cohort-1",)
            )
        indexed_time = time.time() - start

        # Should be fast (< 0.1 seconds for 100 students)
        assert indexed_time < 0.1, f"Indexed query too slow: {indexed_time}s"


class TestMultiCohortSupport:
    """Test multi-cohort database support"""

    def test_separate_databases_per_cohort(self, tmp_path):
        """Test that each cohort has its own database"""
        cohort1_db = tmp_path / "cohort-1.db"
        cohort2_db = tmp_path / "cohort-2.db"

        store1 = StudentStateStore(db_path=str(cohort1_db))
        store2 = StudentStateStore(db_path=str(cohort2_db))

        # Create students in different cohorts
        store1.create_student(discord_id="student1")
        store2.create_student(discord_id="student2")

        # Verify isolation
        student_in_cohort1 = store1.get_student("student1")
        student_in_cohort2 = store2.get_student("student2")

        assert student_in_cohort1 is not None
        assert student_in_cohort2 is not None

        # Cross-cohort lookup should fail
        student_not_in_cohort1 = store1.get_student("student2")
        assert student_not_in_cohort1 is None

        store1.close()
        store2.close()

    def test_concurrent_access_simulation(self, tmp_path):
        """Test concurrent access to same database"""
        db_path = tmp_path / "test.db"

        # Create store instances (simulating concurrent access)
        store1 = StudentStateStore(db_path=str(db_path))
        store2 = StudentStateStore(db_path=str(db_path))

        # Both stores should be able to read/write
        store1.create_student(discord_id="student1")
        store2.create_student(discord_id="student2")

        # Both should see all students
        count1 = store1.get_student_count()
        count2 = store2.get_student_count()

        assert count1 == 2
        assert count2 == 2

        store1.close()
        store2.close()


class TestDataIntegrity:
    """Test data integrity and constraints"""

    def test_foreign_key_constraint(self, store):
        """Test foreign key constraints work"""
        # Try to create habit_practice without student (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            store.conn.execute(
                "INSERT INTO habit_practice (student_id, habit_id) VALUES (?, ?)",
                ("nonexistent_student", 1)
            )

    def test_unique_constraint(self, store):
        """Test unique constraints work"""
        store.create_student(discord_id="123456789")

        # Try to create duplicate student (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            store.create_student(discord_id="123456789")

    def test_on_delete_cascade(self, store):
        """Test ON DELETE CASCADE works"""
        # Create student with related records
        store.create_student(discord_id="123456789")
        store.save_conversation("123456789", "frame", "user", "Test")

        # Delete student
        store.conn.execute("DELETE FROM students WHERE discord_id = ?", ("123456789",))
        store.conn.commit()

        # Verify cascade delete
        cursor = store.conn.execute(
            "SELECT COUNT(*) FROM conversations WHERE student_id = ?",
            ("123456789",)
        )
        count = cursor.fetchone()[0]

        assert count == 0  # Conversations deleted


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
