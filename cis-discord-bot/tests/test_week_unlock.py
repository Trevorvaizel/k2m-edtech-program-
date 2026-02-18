"""
Week Unlock System Tests (Task 2.5)

Test Friday reflection gating, Saturday batch unlock, laggard handling,
and Trevor manual override.
"""

import pytest
import sqlite3
from datetime import datetime
from database.store import StudentStateStore


class TestWeeklyReflections:
    """Test weekly reflection database operations."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    @pytest.fixture
    def student(self, store):
        """Create test student."""
        student = store.create_student("123456", cohort_id="test-cohort")
        return student

    def test_create_weekly_reflection_record(self, store, student):
        """Test creating a new weekly reflection record."""
        reflection = store.create_weekly_reflection_record("123456", 1)

        assert reflection is not None
        assert reflection['discord_id'] == "123456"
        assert reflection['week_number'] == 1
        assert reflection['submitted'] == 0
        assert reflection['next_week_unlocked'] == 0

    def test_get_weekly_reflection(self, store, student):
        """Test retrieving a weekly reflection record."""
        store.create_weekly_reflection_record("123456", 1)
        reflection = store.get_weekly_reflection("123456", 1)

        assert reflection is not None
        assert reflection['week_number'] == 1

    def test_submit_weekly_reflection(self, store, student):
        """Test submitting a weekly reflection."""
        store.create_weekly_reflection_record("123456", 1)

        reflection = store.submit_weekly_reflection(
            discord_id="123456",
            week_number=1,
            reflection_content="Habit Practice: yes\nIdentity Shift: I feel more confident",
            proof_of_work="AI knew I wanted to learn about game design"
        )

        assert reflection['submitted'] == 1
        assert reflection['reflection_content'] is not None
        assert reflection['proof_of_work'] is not None
        assert reflection['submitted_at'] is not None

    def test_get_incomplete_reflections(self, store):
        """Test getting list of students who haven't submitted."""
        # Create multiple students
        store.create_student("111111", cohort_id="test-cohort")
        store.create_student("222222", cohort_id="test-cohort")
        store.create_student("333333", cohort_id="test-cohort")

        # Create reflection records for Week 1
        store.create_weekly_reflection_record("111111", 1)
        store.create_weekly_reflection_record("222222", 1)
        store.create_weekly_reflection_record("333333", 1)

        # Only student 222222 submits
        store.submit_weekly_reflection(
            discord_id="222222",
            week_number=1,
            reflection_content="Test reflection",
            proof_of_work="Test proof"
        )

        incomplete = store.get_incomplete_reflections(1)

        assert len(incomplete) == 2
        discord_ids = [r['discord_id'] for r in incomplete]
        assert "111111" in discord_ids
        assert "333333" in discord_ids
        assert "222222" not in discord_ids


class TestWeekUnlock:
    """Test week unlock logic."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    @pytest.fixture
    def student(self, store):
        """Create test student."""
        student = store.create_student("123456", cohort_id="test-cohort")
        return student

    def test_unlock_next_week(self, store, student):
        """Test unlocking next week for a student."""
        store.create_weekly_reflection_record("123456", 1)

        reflection = store.unlock_next_week(
            discord_id="123456",
            current_week=1
        )

        assert reflection['next_week_unlocked'] == 1
        assert reflection['unlocked_at'] is not None

        # Check student's current_week was updated
        updated_student = store.get_student("123456")
        assert updated_student['current_week'] == 2

    def test_manual_unlock_tracking(self, store, student):
        """Test that manual unlocks are tracked."""
        store.create_weekly_reflection_record("123456", 1)

        reflection = store.unlock_next_week(
            discord_id="123456",
            current_week=1,
            manually_unlocked=True,
            unlocked_by="999999",
            unlock_reason="Illness - family emergency"
        )

        assert reflection['manually_unlocked'] == 1
        assert reflection['unlocked_by'] == "999999"
        assert reflection['unlock_reason'] == "Illness - family emergency"

    def test_batch_unlock_next_week(self, store):
        """Test batch unlock for multiple students."""
        # Create multiple students
        for i in range(5):
            discord_id = f"{i:06d}"
            store.create_student(discord_id, cohort_id="test-cohort")
            store.create_weekly_reflection_record(discord_id, 1)

        # Submit reflections for students 0, 1, 2
        for i in range(3):
            store.submit_weekly_reflection(
                discord_id=f"{i:06d}",
                week_number=1,
                reflection_content=f"Reflection {i}",
                proof_of_work=f"Proof {i}"
            )

        # Batch unlock
        unlocked_count = store.batch_unlock_next_week(1)

        assert unlocked_count == 3

        # Verify unlocked students
        for i in range(3):
            reflection = store.get_weekly_reflection(f"{i:06d}", 1)
            assert reflection['next_week_unlocked'] == 1

        # Verify non-submitted students remain locked
        for i in range(3, 5):
            reflection = store.get_weekly_reflection(f"{i:06d}", 1)
            assert reflection['next_week_unlocked'] == 0

    def test_has_unlocked_next_week(self, store, student):
        """Test checking if student has unlocked next week."""
        store.create_weekly_reflection_record("123456", 1)

        # Initially not unlocked
        assert not store.has_unlocked_next_week("123456", 1)

        # Unlock
        store.unlock_next_week(discord_id="123456", current_week=1)

        # Now unlocked
        assert store.has_unlocked_next_week("123456", 1)


class TestReflectionSummary:
    """Test reflection summary statistics."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    def test_get_reflection_summary(self, store):
        """Test getting reflection summary for a week."""
        # Create 10 students
        for i in range(10):
            discord_id = f"{i:06d}"
            store.create_student(discord_id, cohort_id="test-cohort")
            store.create_weekly_reflection_record(discord_id, 1)

        # 7 students submit reflections
        for i in range(7):
            store.submit_weekly_reflection(
                discord_id=f"{i:06d}",
                week_number=1,
                reflection_content=f"Reflection {i}",
                proof_of_work=f"Proof {i}"
            )

        # 5 students unlock next week
        for i in range(5):
            store.unlock_next_week(discord_id=f"{i:06d}", current_week=1)

        summary = store.get_reflection_summary(1)

        assert summary['week_number'] == 1
        assert summary['total_students'] == 10
        assert summary['submitted_count'] == 7
        assert summary['unlocked_count'] == 5
        assert summary['pending_count'] == 3


class TestWeekUnlockIntegration:
    """Integration tests for week unlock workflow."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    def test_complete_reflection_workflow(self, store):
        """Test complete workflow: submit → unlock → verify."""
        # Create student
        student = store.create_student("123456", cohort_id="test-cohort")
        assert student['current_week'] == 1

        # Create reflection record
        store.create_weekly_reflection_record("123456", 1)

        # Submit reflection
        store.submit_weekly_reflection(
            discord_id="123456",
            week_number=1,
            reflection_content="I learned so much!",
            proof_of_work="AI understood my interest in biology"
        )

        # Verify submitted
        reflection = store.get_weekly_reflection("123456", 1)
        assert reflection['submitted'] == 1

        # Unlock next week
        store.unlock_next_week(discord_id="123456", current_week=1)

        # Verify unlocked
        assert store.has_unlocked_next_week("123456", 1)

        # Verify student advanced
        updated_student = store.get_student("123456")
        assert updated_student['current_week'] == 2

    def test_laggard_scenario(self, store):
        """Test laggard handling: student doesn't submit, stays in current week."""
        # Create student
        student = store.create_student("123456", cohort_id="test-cohort")
        assert student['current_week'] == 1

        # Create reflection record but don't submit
        store.create_weekly_reflection_record("123456", 1)

        # Batch unlock (simulates Saturday 12 PM)
        unlocked_count = store.batch_unlock_next_week(1)

        # Student not counted in unlock
        assert unlocked_count == 0

        # Verify still locked
        assert not store.has_unlocked_next_week("123456", 1)

        # Verify student stays in Week 1
        updated_student = store.get_student("123456")
        assert updated_student['current_week'] == 1

    def test_manual_override_scenario(self, store):
        """Test Trevor manually unlocking a student who didn't submit."""
        # Create student
        student = store.create_student("123456", cohort_id="test-cohort")

        # Create reflection record but don't submit
        store.create_weekly_reflection_record("123456", 1)

        # Trevor manually unlocks (illness exception)
        store.unlock_next_week(
            discord_id="123456",
            current_week=1,
            manually_unlocked=True,
            unlocked_by="999999",
            unlock_reason="Medical emergency - student in hospital"
        )

        # Verify unlocked despite no submission
        assert store.has_unlocked_next_week("123456", 1)

        # Verify manual unlock tracked
        reflection = store.get_weekly_reflection("123456", 1)
        assert reflection['manually_unlocked'] == 1
        assert reflection['unlock_reason'] == "Medical emergency - student in hospital"

        # Verify student advanced
        updated_student = store.get_student("123456")
        assert updated_student['current_week'] == 2
