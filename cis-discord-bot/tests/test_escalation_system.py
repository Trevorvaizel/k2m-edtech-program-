"""
Tests for Escalation System
Story 2.4 Implementation: 4-Level Escalation System

Test coverage for:
- Level 1 (Yellow): Bot auto-nudge (1 day no post)
- Level 2 (Orange): Trevor alert (3+ days stuck)
- Level 3 (Red): Trevor notified to DM student (7+ days stuck)
- Level 4 (Crisis): Instant Trevor DM (SafetyFilter integration)
- Database logging
- Trevor dashboard notifications
- Moderation logs channel
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import pytz

from cis_controller.escalation_system import (
    EAT,
    EscalationSystem,
    LEVEL_1_YELLOW,
    LEVEL_2_ORANGE,
    LEVEL_3_RED,
    LEVEL_4_CRISIS,
)
from database.store import StudentStateStore


@pytest.fixture
def mock_bot():
    """Mock Discord bot."""
    bot = Mock()
    bot.fetch_user = AsyncMock()
    bot.get_channel = Mock()
    return bot


@pytest.fixture
def mock_store():
    """Mock database store."""
    store = Mock(spec=StudentStateStore)
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    store.conn = conn
    return store


@pytest.fixture
def escalation_system(mock_bot, mock_store):
    """Create EscalationSystem instance with mocks."""
    system = EscalationSystem(
        bot=mock_bot,
        store=mock_store,
        facilitator_dashboard_id=123456789,
        moderation_logs_id=987654321,
        trevor_discord_id="999888777"
    )
    return system


class TestEscalationSystemInit:
    """Tests for EscalationSystem initialization."""

    def test_init(self, escalation_system):
        """Test system initializes with correct configuration."""
        assert escalation_system.facilitator_dashboard_id == 123456789
        assert escalation_system.moderation_logs_id == 987654321
        assert escalation_system.trevor_discord_id == "999888777"


class TestLevel2Escalation:
    """Tests for Level 2 (Orange Flag) escalations."""

    @pytest.mark.asyncio
    async def test_level_2_dashboard_alert(self, escalation_system, mock_bot, mock_store):
        """Test Level 2 posts alert to #facilitator-dashboard."""
        # Setup mocks
        dashboard_channel = Mock()
        dashboard_channel.send = AsyncMock()
        mock_bot.get_channel.return_value = dashboard_channel

        cursor = mock_store.conn.cursor()
        cursor.execute.return_value = None
        mock_store.conn.commit.return_value = None

        # Execute
        await escalation_system._escalate_level_2(
            discord_id="111222333",
            username="test_student",
            days_since_post=3,
            zone="zone_1",
            emotional_state="anxious"
        )

        # Verify dashboard message sent
        assert dashboard_channel.send.called
        first_message = dashboard_channel.send.call_args_list[0][0][0]
        assert "ORANGE FLAG" in first_message
        assert "test_student" in first_message
        assert "3+ days" in first_message
        assert "zone_1" in first_message

        # Verify moderation log call also happened
        last_message = dashboard_channel.send.call_args[0][0]
        assert "ORANGE FLAG" in last_message

    @pytest.mark.asyncio
    async def test_level_2_logs_to_database(self, escalation_system, mock_store):
        """Test Level 2 escalations are logged to database."""
        # Setup mocks
        dashboard_channel = Mock()
        dashboard_channel.send = AsyncMock()
        escalation_system.bot.get_channel.return_value = dashboard_channel

        cursor = mock_store.conn.cursor()
        cursor.execute.return_value = None
        mock_store.conn.commit.return_value = None

        # Execute
        await escalation_system._escalate_level_2(
            discord_id="111222333",
            username="test_student",
            days_since_post=5,
            zone="zone_2",
            emotional_state="stuck"
        )

        # Verify database insert called
        assert cursor.execute.called
        call_args = cursor.execute.call_args
        assert "INSERT INTO escalations" in call_args[0][0]
        assert "111222333" in call_args[0][1]
        assert LEVEL_2_ORANGE in call_args[0][1]


class TestLevel3Escalation:
    """Tests for Level 3 (Red Flag) escalations."""

    @pytest.mark.asyncio
    async def test_level_3_trevor_dm(self, escalation_system, mock_bot, mock_store):
        """Test Level 3 sends DM to Trevor for human-led outreach."""
        # Setup mocks
        trevor = Mock()
        trevor.send = AsyncMock()
        mock_bot.fetch_user.return_value = trevor

        logs_channel = Mock()
        logs_channel.send = AsyncMock()
        escalation_system.bot.get_channel.return_value = logs_channel

        cursor = mock_store.conn.cursor()
        cursor.execute.return_value = None
        mock_store.conn.commit.return_value = None

        # Execute
        await escalation_system._escalate_level_3(
            discord_id="111222333",
            username="test_student",
            days_since_post=7,
            zone="zone_0",
            emotional_state="disengaged"
        )

        # Verify Trevor notified
        assert trevor.send.called
        trevor_message = trevor.send.call_args[0][0]
        assert "RED FLAG" in trevor_message
        assert "test_student" in trevor_message

        # Trevor is the only DM target for level 3.
        mock_bot.fetch_user.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_level_3_logs_to_moderation(self, escalation_system, mock_bot, mock_store):
        """Test Level 3 logs moderation event after notifying Trevor."""
        # Setup mocks
        trevor = Mock()
        trevor.send = AsyncMock()
        mock_bot.fetch_user.return_value = trevor

        logs_channel = Mock()
        logs_channel.send = AsyncMock()
        escalation_system.bot.get_channel.return_value = logs_channel

        cursor = mock_store.conn.cursor()
        cursor.execute.return_value = None
        mock_store.conn.commit.return_value = None

        # Execute - should not raise exception
        await escalation_system._escalate_level_3(
            discord_id="111222333",
            username="test_student",
            days_since_post=10,
            zone="zone_0",
            emotional_state="disengaged"
        )

        # Verify Trevor notified and moderation log emitted.
        assert trevor.send.called
        assert logs_channel.send.called


class TestLevel4Crisis:
    """Tests for Level 4 (Crisis) escalations."""

    @pytest.mark.asyncio
    async def test_level_4_crisis_instant_trevor_alert(self, escalation_system, mock_bot, mock_store):
        """Test Level 4 sends instant Trevor DM with crisis context."""
        # Setup mocks
        trevor = Mock()
        trevor.send = AsyncMock()
        mock_bot.fetch_user.return_value = trevor

        logs_channel = Mock()
        logs_channel.send = AsyncMock()
        escalation_system.bot.get_channel.return_value = logs_channel

        cursor = mock_store.conn.cursor()
        cursor.execute.return_value = None
        mock_store.conn.commit.return_value = None

        # Execute
        await escalation_system.escalate_level_4_crisis(
            discord_id="111222333",
            username="crisis_student",
            crisis_type="mental_health_crisis",
            last_3_messages=["I feel hopeless", "I can't go on", "want to end it"],
            zone="zone_0",
            emotional_state="crisis"
        )

        # Verify Trevor notified instantly
        assert trevor.send.called
        trevor_message = trevor.send.call_args[0][0]
        assert "LEVEL 4 CRISIS" in trevor_message
        assert "IMMEDIATE ACTION REQUIRED" in trevor_message
        assert "crisis_student" in trevor_message
        assert "1 HOUR" in trevor_message

        # Verify last 3 messages included
        assert "I feel hopeless" in trevor_message
        assert "I can't go on" in trevor_message

    @pytest.mark.asyncio
    async def test_level_4_logs_to_moderation(self, escalation_system, mock_bot, mock_store):
        """Test Level 4 logs to #moderation-logs."""
        # Setup mocks
        trevor = Mock()
        trevor.send = AsyncMock()
        mock_bot.fetch_user.return_value = trevor

        logs_channel = Mock()
        logs_channel.send = AsyncMock()
        escalation_system.bot.get_channel.return_value = logs_channel

        cursor = mock_store.conn.cursor()
        cursor.execute.return_value = None
        mock_store.conn.commit.return_value = None

        # Execute
        await escalation_system.escalate_level_4_crisis(
            discord_id="111222333",
            username="crisis_student",
            crisis_type="mental_health_crisis",
            last_3_messages=["help me"],
            zone="zone_0",
            emotional_state="hopeless"
        )

        # Verify logged to moderation channel
        assert logs_channel.send.called
        log_message = logs_channel.send.call_args[0][0]
        assert "CRISIS" in log_message
        assert "crisis_student" in log_message


class TestEscalationChecks:
    """Tests for daily escalation checking logic."""

    @pytest.mark.asyncio
    async def test_checks_all_students(self, escalation_system, mock_store):
        """Test check_escalations iterates through all students."""
        # Setup mock database response
        cursor = mock_store.conn.cursor()

        # First query: get all students
        cursor.fetchall.side_effect = [
            [("111", "zone_1", "curious"),
             ("222", "zone_2", "stuck")]
        ]

        # Second query: get last post date
        cursor.fetchone.side_effect = [
            ("2026-02-15", 5),  # student1 posted 5 days ago
            (None, 0),          # student2 never posted
        ]

        # Mock _was_recently_escalated to return False
        with patch.object(escalation_system, '_was_recently_escalated', return_value=False):
            with patch.object(escalation_system, '_check_student_escalation', new_callable=AsyncMock) as mock_check:
                # Execute
                await escalation_system.check_escalations(current_week=2)

                # Verify checked for both students
                assert mock_check.call_count == 2

    @pytest.mark.asyncio
    async def test_skips_brand_new_students(self, escalation_system, mock_store):
        """Test check_escalations skips students who joined today (never posted)."""
        # Setup mock - student has NULL last post date (joined today)
        cursor = mock_store.conn.cursor()
        cursor.fetchall.return_value = [("111", "newbie", "zone_0", "curious")]
        cursor.fetchone.return_value = (None, 0)  # Never posted

        # Mock _was_recently_escalated
        with patch.object(escalation_system, '_was_recently_escalated', return_value=False):
            with patch.object(escalation_system, '_escalate_level_2', new_callable=AsyncMock) as mock_l2:
                with patch.object(escalation_system, '_escalate_level_3', new_callable=AsyncMock) as mock_l3:
                    # Execute
                    await escalation_system._check_student_escalation(
                        discord_id="111",
                        username="newbie",
                        zone="zone_0",
                        emotional_state="curious",
                        current_week=1
                    )

                    # Verify NO escalation for brand-new students
                    assert not mock_l2.called
                    assert not mock_l3.called


class TestRecentEscalationCheck:
    """Tests for _was_recently_escalated deduplication logic."""

    @pytest.mark.asyncio
    async def test_returns_true_if_escalated_recently(self, escalation_system, mock_store):
        """Test _was_recently_escalated returns True when recent escalation exists."""
        cursor = mock_store.conn.cursor()
        cursor.fetchone.return_value = (1,)  # 1 recent escalation found

        result = await escalation_system._was_recently_escalated(
            discord_id="111",
            level=LEVEL_2_ORANGE,
            days=7
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_if_no_recent_escalation(self, escalation_system, mock_store):
        """Test _was_recently_escalated returns False when no recent escalation."""
        cursor = mock_store.conn.cursor()
        cursor.fetchone.return_value = (0,)  # No recent escalations

        result = await escalation_system._was_recently_escalated(
            discord_id="111",
            level=LEVEL_3_RED,
            days=14
        )

        assert result is False


class TestEscalationSummary:
    """Tests for get_escalation_summary dashboard method."""

    @pytest.mark.asyncio
    async def test_summary_returns_counts_by_level(self, escalation_system, mock_store):
        """Test get_escalation_summary returns escalation counts."""
        cursor = mock_store.conn.cursor()

        # Mock database response
        cursor.fetchall.return_value = [
            (LEVEL_1_YELLOW, 15),
            (LEVEL_2_ORANGE, 3),
            (LEVEL_3_RED, 1),
            (LEVEL_4_CRISIS, 0)
        ]

        summary = await escalation_system.get_escalation_summary(days=7)

        assert "Level 1 (Yellow" in summary
        assert "15" in summary
        assert "Level 2 (Orange" in summary
        assert "3" in summary
        assert "Level 3 (Red" in summary
        assert "1" in summary

    @pytest.mark.asyncio
    async def test_summary_returns_no_escalations_message(self, escalation_system, mock_store):
        """Test get_escalation_summary returns friendly message when no escalations."""
        cursor = mock_store.conn.cursor()
        cursor.fetchall.return_value = []  # No escalations

        summary = await escalation_system.get_escalation_summary(days=7)

        assert "No escalations" in summary


class TestEscalationConstants:
    """Tests for escalation level constants."""

    def test_level_constants(self):
        """Test escalation level constants are correctly defined."""
        assert LEVEL_1_YELLOW == 1
        assert LEVEL_2_ORANGE == 2
        assert LEVEL_3_RED == 3
        assert LEVEL_4_CRISIS == 4


class TestEscalationRegression:
    """Regression coverage for inactivity date logic."""

    @pytest.mark.asyncio
    async def test_never_posted_student_uses_join_date_for_inactivity(self, tmp_path):
        db_path = tmp_path / "escalation_regression.db"
        store = StudentStateStore(str(db_path))
        store.create_student("424242")

        now = datetime.now(EAT)
        joined_at = (now - timedelta(days=4)).isoformat()
        yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

        # Simulate nudge-only activity row (has_posted=0), which should NOT reset
        # escalation inactivity counters.
        store.conn.execute(
            """
            INSERT INTO daily_participation
                (discord_id, date, week_number, day_of_week, has_posted, post_count, engagement_score, nudge_sent)
            VALUES (?, ?, 1, 'Monday', 0, 0, 0, 1)
            """,
            ("424242", yesterday),
        )
        store.conn.execute(
            "UPDATE students SET created_at = ?, current_week = 1 WHERE discord_id = ?",
            (joined_at, "424242"),
        )
        store.conn.commit()

        bot = Mock()
        bot.fetch_user = AsyncMock()
        bot.get_channel = Mock(return_value=Mock(send=AsyncMock()))

        escalation_system = EscalationSystem(
            bot=bot,
            store=store,
            facilitator_dashboard_id=123,
            moderation_logs_id=456,
            trevor_discord_id="999888777",
        )

        with patch.object(
            escalation_system,
            "_was_recently_escalated",
            new_callable=AsyncMock,
            return_value=False,
        ), patch.object(
            escalation_system,
            "_escalate_level_2",
            new_callable=AsyncMock,
        ) as mock_l2, patch.object(
            escalation_system,
            "_escalate_level_3",
            new_callable=AsyncMock,
        ) as mock_l3:
            await escalation_system._check_student_escalation(
                discord_id="424242",
                username="<@424242>",
                zone="zone_1",
                emotional_state="curious",
                current_week=1,
            )

        mock_l2.assert_awaited_once()
        mock_l3.assert_not_awaited()
        store.close()
