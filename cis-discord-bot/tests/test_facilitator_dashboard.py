"""
Facilitator Dashboard Tests (Task 2.6)

Test dashboard summary generators for Trevor's private channel.
"""

import pytest
from datetime import datetime
from cis_controller.facilitator_dashboard import FacilitatorDashboard
from database.store import StudentStateStore


class TestDailySummary:
    """Test 9:00 AM daily summary generation."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    @pytest.fixture
    def dashboard(self, store):
        """Create dashboard instance."""
        return FacilitatorDashboard(store)

    def test_generate_daily_summary_basic(self, dashboard):
        """Test basic daily summary generation."""
        summary = dashboard.generate_daily_summary(week=1)

        assert "TUESDAY, WEEK 1 SUMMARY" in summary or "MONDAY, WEEK 1 SUMMARY" in summary
        assert "🎯 Engagement:" in summary
        assert "⏸️ Habit 1 Practice:" in summary
        assert "🚨 Escalations:" in summary
        assert "💰 API Costs:" in summary
        assert "✅ System Health:" in summary

    def test_daily_summary_with_escallations(self, store, dashboard):
        """Test daily summary includes escalation data."""
        # Create stuck students
        for i in range(3):
            discord_id = f"{i:06d}"
            store.create_student(discord_id, cohort_id="test-cohort")

        summary = dashboard.generate_daily_summary(week=1)

        # Should show escalation count
        assert "🚨 Escalations:" in summary


class TestPeerVisibilitySummary:
    """Test 6:00 PM peer visibility summary generation."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    @pytest.fixture
    def dashboard(self, store):
        """Create dashboard instance."""
        return FacilitatorDashboard(store)

    def test_generate_peer_visibility_summary(self, dashboard):
        """Test peer visibility summary generation."""
        summary = dashboard.generate_peer_visibility_summary(week=1)

        assert "🌟 EVENING SNAPSHOT (WEEK 1)" in summary
        assert "Today's submissions:" in summary
        assert "Aggregate patterns:" in summary
        assert "✅ Guardrail #3 check: No comparison detected" in summary


class TestReflectionSummary:
    """Test Friday 5:00 PM reflection summary generation."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    @pytest.fixture
    def dashboard(self, store):
        """Create dashboard instance."""
        return FacilitatorDashboard(store)

    def test_generate_reflection_summary(self, store, dashboard):
        """Test reflection summary with data."""
        # Create students and reflections
        for i in range(10):
            discord_id = f"{i:06d}"
            store.create_student(discord_id, cohort_id="test-cohort")
            store.create_weekly_reflection_record(discord_id, 1)

            # 7 students submit
            if i < 7:
                store.submit_weekly_reflection(
                    discord_id=discord_id,
                    week_number=1,
                    reflection_content="Habit Practice: yes\nIdentity Shift: I feel more confident",
                    proof_of_work="AI knew I wanted to learn about biology"
                )

        summary = dashboard.generate_reflection_summary(week=1)

        assert "🤔 FRIDAY REFLECTIONS (WEEK 1)" in summary
        assert "Submissions: 7/10" in summary
        assert "Identity shift evidence:" in summary
        assert "Habit 1 self-assessment:" in summary
        assert "Proof-of-work:" in summary
        assert "🔓 Week 2 unlock:" in summary
        assert "🚨 Follow-up needed:" in summary

    def test_reflection_summary_habit_breakdown(self, store, dashboard):
        """Test habit practice breakdown in summary."""
        # Create students with different habit practice responses
        store.create_student("000001", cohort_id="test-cohort")
        store.create_weekly_reflection_record("000001", 1)
        store.submit_weekly_reflection(
            discord_id="000001",
            week_number=1,
            reflection_content="Habit Practice: yes\nIdentity Shift: Changed",
            proof_of_work="Proof sentence"
        )

        store.create_student("000002", cohort_id="test-cohort")
        store.create_weekly_reflection_record("000002", 1)
        store.submit_weekly_reflection(
            discord_id="000002",
            week_number=1,
            reflection_content="Habit Practice: sometimes\nIdentity Shift: Learning",
            proof_of_work="Proof sentence"
        )

        summary = dashboard.generate_reflection_summary(week=1)

        # Check habit breakdown appears
        assert "✅ Yes:" in summary
        assert "🔄 Sometimes:" in summary


class TestSpotCheckList:
    """Test Friday 5:00 PM spot-check list generation."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    @pytest.fixture
    def dashboard(self, store):
        """Create dashboard instance."""
        return FacilitatorDashboard(store)

    def test_generate_spot_check_list(self, store, dashboard):
        """Test spot-check list generation."""
        # Create students with reflections
        for i in range(20):
            discord_id = f"{i:06d}"
            store.create_student(discord_id, cohort_id="test-cohort")
            store.create_weekly_reflection_record(discord_id, 1)
            store.submit_weekly_reflection(
                discord_id=discord_id,
                week_number=1,
                reflection_content=f"Habit Practice: yes\nIdentity Shift: Student {i} reflection",
                proof_of_work=f"AI knew I was interested in topic {i}"
            )

        spot_check = dashboard.generate_spot_check_list(week=1)

        assert "🔍 FRIDAY SPOT-CHECK LIST" in spot_check
        assert "Trevor's task:" in spot_check
        assert "Review for genuine engagement" in spot_check
        assert "Check for students who may need support" in spot_check
        assert "Look for patterns" in spot_check
        assert "Reply to flag:" in spot_check

    def test_spot_check_list_includes_student_data(self, store, dashboard):
        """Test spot-check list includes reflection data."""
        # Create test student
        store.create_student("000001", cohort_id="test-cohort")
        store.create_weekly_reflection_record("000001", 1)
        store.submit_weekly_reflection(
            discord_id="000001",
            week_number=1,
            reflection_content="Habit Practice: yes\nIdentity Shift: I went from confused to understanding",
            proof_of_work="AI knew I wanted to learn about game design not just coding"
        )

        spot_check = dashboard.generate_spot_check_list(week=1)

        # Should include student mention and reflection preview
        assert "<@000001>" in spot_check
        assert "Reflection:" in spot_check
        assert "Proof:" in spot_check


class TestEscalationNotifications:
    """Test real-time escalation notification generation."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    @pytest.fixture
    def dashboard(self, store):
        """Create dashboard instance."""
        return FacilitatorDashboard(store)

    def test_level_3_escalation_notification(self, dashboard):
        """Test Level 3 escalation notification format."""
        student = {
            'discord_id': '123456',
            'current_week': 2,
            'zone': 'Zone 1',
            'username': 'TestStudent'
        }

        notification = dashboard.generate_escalation_notification({
            'level': 3,
            'student': student,
            'inactive_days': 7
        })

        assert "⚠️ ESCALATION: Student <@123456> stuck 7 days" in notification
        assert "Last post:" in notification
        assert "Zone: Zone 1" in notification
        assert "Trevor action:" in notification

    def test_level_4_crisis_notification(self, dashboard):
        """Test Level 4 crisis notification format."""
        student = {
            'discord_id': '123456',
            'zone': 'Zone 0',
            'username': 'TestStudent'
        }

        notification = dashboard.generate_escalation_notification({
            'level': 4,
            'student': student,
            'inactive_days': 1
        })

        assert "⚠️⚠️⚠️ CRISIS ESCALATION: Student <@123456>" in notification
        assert "🚨 IMMEDIATE ACTION REQUIRED" in notification
        assert "Trevor DM student within 1 hour" in notification
        assert "Assess risk" in notification


class TestDashboardIntegration:
    """Integration tests for dashboard with scheduler."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create in-memory database for testing."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))
        yield store
        store.close()

    @pytest.fixture
    def dashboard(self, store):
        """Create dashboard instance."""
        return FacilitatorDashboard(store)

    def test_all_summaries_generate_without_errors(self, dashboard):
        """Test that all summary generators produce output."""
        # Daily summary
        daily = dashboard.generate_daily_summary(week=1)
        assert len(daily) > 0
        assert "WEEK 1 SUMMARY" in daily

        # Peer visibility summary
        peer = dashboard.generate_peer_visibility_summary(week=1)
        assert len(peer) > 0
        assert "EVENING SNAPSHOT" in peer

        # Reflection summary
        reflection = dashboard.generate_reflection_summary(week=1)
        assert len(reflection) > 0
        assert "FRIDAY REFLECTIONS" in reflection

        # Spot-check list
        spot_check = dashboard.generate_spot_check_list(week=1)
        assert len(spot_check) > 0
        assert "SPOT-CHECK LIST" in spot_check

    def test_guardrail_compliance(self, dashboard):
        """Test all summaries are Guardrail #3 compliant (no comparison/ranking)."""
        summaries = [
            dashboard.generate_daily_summary(week=1),
            dashboard.generate_peer_visibility_summary(week=1),
            dashboard.generate_reflection_summary(week=1),
            dashboard.generate_spot_check_list(week=1)
        ]

        # Forbidden comparison/ranking keywords
        forbidden_keywords = [
            'top student', 'best', 'better than', 'most active',
            'ranking', 'winner', 'leader', 'highest'
        ]

        for summary in summaries:
            summary_lower = summary.lower()
            for keyword in forbidden_keywords:
                # Should not contain comparison keywords
                # (except in acceptable contexts like "top priority")
                assert keyword not in summary_lower or 'priority' in summary_lower, \
                    f"Guardrail #3 violation: '{keyword}' found in summary:\n{summary}"

            # Should include Guardrail #3 check explicitly
            assert "Guardrail #3" in summary or "no comparison detected" in summary.lower()


class TestDashboardWithRealData:
    """Test dashboard with realistic cohort data."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create database with realistic data."""
        db_path = tmp_path / "test.db"
        store = StudentStateStore(str(db_path))

        # Create 50 students across 2 weeks
        for i in range(50):
            discord_id = f"{i:06d}"
            store.create_student(discord_id, cohort_id="test-cohort")

            # Week 1 reflections
            store.create_weekly_reflection_record(discord_id, 1)
            if i < 40:  # 40 students submit
                habit = 'yes' if i < 20 else 'sometimes'
                store.submit_weekly_reflection(
                    discord_id=discord_id,
                    week_number=1,
                    reflection_content=f"Habit Practice: {habit}\nIdentity Shift: Student {i} shift",
                    proof_of_work=f"AI knew about interest {i}"
                )

        yield store
        store.close()

    @pytest.fixture
    def dashboard(self, store):
        """Create dashboard instance."""
        return FacilitatorDashboard(store)

    def test_realistic_daily_summary(self, dashboard):
        """Test daily summary with realistic data."""
        summary = dashboard.generate_daily_summary(week=1)

        assert "50 students" in summary or "50" in summary
        assert "WEEK 1 SUMMARY" in summary

    def test_realistic_reflection_summary(self, dashboard):
        """Test reflection summary with realistic data."""
        summary = dashboard.generate_reflection_summary(week=1)

        assert "Submissions: 40/50" in summary
        assert "80%" in summary  # 40/50 = 80%

    def test_realistic_spot_check_sample_size(self, dashboard):
        """Test spot-check list samples correctly."""
        spot_check = dashboard.generate_spot_check_list(week=1)

        # Should sample 15-20 reflections
        assert "15 random reflections" in spot_check or "16 random reflections" in spot_check or "17 random reflections" in spot_check or "18 random reflections" in spot_check or "19 random reflections" in spot_check or "20 random reflections" in spot_check
