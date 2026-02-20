"""
Test Agent Unlock Announcement System (Task 3.4)

Tests for graduated agent unlock announcements per Decision 11:
- Week 4: /diverge and /challenge unlock announcement
- Week 6: /synthesize and /create-artifact unlock announcement
- Database tracking of announcements
- Scheduler integration
"""

import pytest
import sqlite3
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, MagicMock, patch

from scheduler.scheduler import DailyPromptScheduler
from scheduler.daily_prompts import WeekDay
from database.store import StudentStateStore


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test_cohort.db"
    store = StudentStateStore(str(db_path))
    yield store
    store.close()


@pytest.fixture
def mock_bot():
    """Create mock Discord bot."""
    bot = Mock()
    bot.get_guild = Mock()
    return bot


@pytest.fixture
def mock_guild(mock_bot):
    """Create mock Discord guild."""
    guild = Mock()
    mock_bot.get_guild.return_value = guild
    return guild


@pytest.fixture
def mock_channel(mock_guild):
    """Create mock Discord channel."""
    channel = Mock()
    channel.id = 123456789
    channel.name = "week-4-5-converse"
    channel.send = AsyncMock()
    mock_guild.get_channel.return_value = channel
    return channel


# ============================================================
# TEST SUITE 1: Database Tracking Methods
# ============================================================

class TestAgentUnlockDatabaseTracking:
    """Test database methods for tracking unlock announcements."""

    def test_has_announced_unlock_no_announcement(self, temp_db):
        """Test has_announced_unlock returns False when no announcement."""
        result = temp_db.has_announced_unlock(week_number=4)
        assert result is False

    def test_has_announced_unlock_after_announcement(self, temp_db):
        """Test has_announced_unlock returns True after announcement recorded."""
        temp_db.record_unlock_announcement(
            week_number=4,
            agents_unlocked=["diverge", "challenge"],
            channel_id="123456789"
        )
        result = temp_db.has_announced_unlock(week_number=4)
        assert result is True

    def test_record_unlock_announcement(self, temp_db):
        """Test record_unlock_announcement creates database record."""
        temp_db.record_unlock_announcement(
            week_number=4,
            agents_unlocked=["diverge", "challenge"],
            channel_id="123456789"
        )

        # Verify record exists
        cursor = temp_db.conn.execute(
            "SELECT * FROM agent_unlock_announcements WHERE week_number = ?",
            (4,)
        )
        row = cursor.fetchone()

        assert row is not None
        assert row['week_number'] == 4
        assert json.loads(row['agents_unlocked']) == ["diverge", "challenge"]
        assert row['channel_id'] == "123456789"

    def test_record_unlock_announcement_idempotent(self, temp_db):
        """Test record_unlock_announcement updates existing record (idempotent)."""
        # First announcement
        temp_db.record_unlock_announcement(
            week_number=4,
            agents_unlocked=["diverge", "challenge"],
            channel_id="123456789"
        )

        # Update with different data
        temp_db.record_unlock_announcement(
            week_number=4,
            agents_unlocked=["diverge", "challenge", "frame"],
            channel_id="987654321"
        )

        # Verify only one record exists with updated data
        cursor = temp_db.conn.execute(
            "SELECT COUNT(*) as count FROM agent_unlock_announcements WHERE week_number = ?",
            (4,)
        )
        count = cursor.fetchone()['count']
        assert count == 1

        cursor = temp_db.conn.execute(
            "SELECT * FROM agent_unlock_announcements WHERE week_number = ?",
            (4,)
        )
        row = cursor.fetchone()
        assert json.loads(row['agents_unlocked']) == ["diverge", "challenge", "frame"]
        assert row['channel_id'] == "987654321"

    def test_get_unlocked_agents_for_week_all_weeks(self, temp_db):
        """Test get_unlocked_agents_for_week returns correct agents for all weeks."""
        # Week 1: /frame only
        assert temp_db.get_unlocked_agents_for_week(1) == ["frame"]

        # Week 2-3: /frame only
        assert temp_db.get_unlocked_agents_for_week(2) == ["frame"]
        assert temp_db.get_unlocked_agents_for_week(3) == ["frame"]

        # Week 4-5: /frame, /diverge, /challenge
        assert temp_db.get_unlocked_agents_for_week(4) == ["frame", "diverge", "challenge"]
        assert temp_db.get_unlocked_agents_for_week(5) == ["frame", "diverge", "challenge"]

        # Week 6-8: All agents
        week_6_agents = temp_db.get_unlocked_agents_for_week(6)
        assert "frame" in week_6_agents
        assert "diverge" in week_6_agents
        assert "challenge" in week_6_agents
        assert "synthesize" in week_6_agents
        assert "create-artifact" in week_6_agents
        assert "edit" in week_6_agents

    def test_get_announced_agents_no_announcement(self, temp_db):
        """Test get_announced_agents returns empty list when no announcement."""
        result = temp_db.get_announced_agents(week_number=4)
        assert result == []

    def test_get_announced_agents_after_announcement(self, temp_db):
        """Test get_announced_agents returns announced agents."""
        temp_db.record_unlock_announcement(
            week_number=4,
            agents_unlocked=["diverge", "challenge"],
            channel_id="123456789"
        )
        result = temp_db.get_announced_agents(week_number=4)
        assert result == ["diverge", "challenge"]


# ============================================================
# TEST SUITE 2: Announcement Message Generation
# ============================================================

class TestAgentUnlockAnnouncementMessages:
    """Test announcement message generation for different unlock scenarios."""

    @pytest.mark.asyncio
    async def test_week_4_announcement_diverge_challenge_unlock(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test Week 4 announcement: /diverge and /challenge unlocked."""
        # Create scheduler with test configuration
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        # Mock get_target_channel to return our mock channel
        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        # Post announcement
        await scheduler.post_agent_unlock_announcement(week=4)

        # Verify announcement was posted
        mock_channel.send.assert_called_once()
        call_args = mock_channel.send.call_args
        message = call_args[0][0]

        # Verify message contains key elements
        assert "NEW THINKING PARTNERS UNLOCKED" in message
        assert "/diverge" in message
        assert "/challenge" in message
        assert "🔍" in message  # Explorer emoji
        assert "⚡" in message  # Challenger emoji
        assert "⏸️ Pause" in message  # Habit 1 reference
        assert "🎯 Context" in message  # Habit 2 reference
        assert "🔄 Iterate" in message  # Habit 3 reference
        assert "Try them all this week" in message

    @pytest.mark.asyncio
    async def test_week_6_announcement_synthesize_artifact_unlock(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test Week 6 announcement: /synthesize and /create-artifact unlocked."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={6: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        # Post announcement
        await scheduler.post_agent_unlock_announcement(week=6)

        # Verify announcement was posted
        mock_channel.send.assert_called_once()
        call_args = mock_channel.send.call_args
        message = call_args[0][0]

        # Verify message contains key elements
        assert "FINAL TOOLS UNLOCKED" in message
        assert "/synthesize" in message
        assert "/create-artifact" in message
        assert "✨" in message  # Synthesizer emoji
        assert "📝" in message  # Artifact emoji
        assert "artifact creation phase" in message
        assert "Graduation Project" in message
        assert "You're the director" in message

        # Verify all 4 Habits are listed
        assert "⏸️ Pause" in message
        assert "🎯 Context" in message
        assert "🔄 Iterate" in message
        assert "🧠 Think First" in message

    @pytest.mark.asyncio
    async def test_week_1_no_announcement(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test Week 1: No announcement (no new agents)."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={1: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        # Post announcement
        await scheduler.post_agent_unlock_announcement(week=1)

        # Verify nothing was posted (no new agents)
        mock_channel.send.assert_not_called()

        # Verify record was created to prevent repeated checks
        assert temp_db.has_announced_unlock(week_number=1) is True

    @pytest.mark.asyncio
    async def test_week_2_3_no_announcement(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test Weeks 2-3: No announcement (same agents as Week 1)."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={2: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        # Test Week 2
        await scheduler.post_agent_unlock_announcement(week=2)
        mock_channel.send.assert_not_called()

        # Test Week 3
        await scheduler.post_agent_unlock_announcement(week=3)
        mock_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_week_8_no_announcement(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test Week 8: No announcement (same agents as Week 6-7)."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={8: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        # Post announcement
        await scheduler.post_agent_unlock_announcement(week=8)

        # Verify nothing was posted
        mock_channel.send.assert_not_called()


# ============================================================
# TEST SUITE 3: Idempotency and Deduplication
# ============================================================

class TestAgentUnlockIdempotency:
    """Test that announcements are idempotent and don't spam."""

    @pytest.mark.asyncio
    async def test_announcement_only_once_per_week(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test announcement only posts once, even if called multiple times."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        # Call announcement twice
        await scheduler.post_agent_unlock_announcement(week=4)
        await scheduler.post_agent_unlock_announcement(week=4)

        # Verify only one announcement was posted
        assert mock_channel.send.call_count == 1

        # Verify database shows announcement
        assert temp_db.has_announced_unlock(week_number=4) is True

    @pytest.mark.asyncio
    async def test_cohort_not_active_no_announcement(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test no announcement when cohort not active (week 0)."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={0: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        # Attempt announcement for week 0
        await scheduler.post_agent_unlock_announcement(week=0)

        # Verify nothing was posted
        mock_channel.send.assert_not_called()

        # Verify no record was created
        assert temp_db.has_announced_unlock(week_number=0) is False

    @pytest.mark.asyncio
    async def test_week_9_no_announcement(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test no announcement after cohort ends (week > 8)."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={9: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        # Attempt announcement for week 9
        await scheduler.post_agent_unlock_announcement(week=9)

        # Verify nothing was posted
        mock_channel.send.assert_not_called()


# ============================================================
# TEST SUITE 4: Scheduler Integration
# ============================================================

class TestAgentUnlockSchedulerIntegration:
    """Test that unlock announcements integrate with scheduler timing."""

    def test_agent_unlock_flag_initialized(self, mock_bot, temp_db):
        """Test that _agent_unlock_today flag is initialized."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: 123456789},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        assert scheduler._agent_unlock_today is False

    @pytest.mark.asyncio
    async def test_agent_unlock_flag_set_after_announcement(self, mock_bot, mock_channel, temp_db):
        """Test that _agent_unlock_today flag is set after announcement."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        # Post announcement
        await scheduler.post_agent_unlock_announcement(week=4)

        # Verify flag was set
        assert scheduler._agent_unlock_today is True

    @pytest.mark.asyncio
    async def test_agent_unlock_flag_resets_at_midnight(self, mock_bot, temp_db):
        """Test that _agent_unlock_today flag resets at midnight."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: 123456789},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        # Set flag to True
        scheduler._agent_unlock_today = True
        scheduler._last_post_date = (datetime.now() - timedelta(days=1)).date()

        # Trigger check_and_post (should reset flags)
        with patch.object(scheduler, 'get_week_day', return_value=(4, WeekDay.MONDAY)):
            with patch.object(scheduler, 'get_current_week', return_value=4):
                await scheduler.check_and_post()

        # Verify flag was reset
        assert scheduler._agent_unlock_today is False


# ============================================================
# TEST SUITE 5: Revolutionary Hope Brand Voice
# ============================================================

class TestAgentUnlockBrandVoice:
    """Test that announcements use Revolutionary Hope tone."""

    @pytest.mark.asyncio
    async def test_celebratory_tone(self, mock_bot, mock_channel, temp_db):
        """Test announcements are celebratory, not prescriptive."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        await scheduler.post_agent_unlock_announcement(week=4)

        call_args = mock_channel.send.call_args
        message = call_args[0][0]

        # Verify celebratory language
        assert "🎉" in message or "🚀" in message or "✨" in message

        # Verify NO prescriptive language (Guardrail #4)
        assert "must" not in message.lower()
        assert "should" not in message.lower()
        assert "have to" not in message.lower()

        # Verify empowering language
        assert "your toolkit" in message.lower() or "you're ready" in message.lower()

    @pytest.mark.asyncio
    async def test_explains_why_sequence_matters(self, mock_bot, mock_channel, temp_db):
        """Test announcements explain why agents unlock in sequence."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        await scheduler.post_agent_unlock_announcement(week=4)

        call_args = mock_channel.send.call_args
        message = call_args[0][0]

        # Verify explanation of sequence
        assert "Why now?" in message
        assert "built confidence" in message
        assert "Habit" in message

    @pytest.mark.asyncio
    async def test_includes_examples(self, mock_bot, mock_channel, temp_db):
        """Test announcements include usage examples."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        await scheduler.post_agent_unlock_announcement(week=4)

        call_args = mock_channel.send.call_args
        message = call_args[0][0]

        # Verify examples are included
        assert "/diverge" in message
        assert "/challenge" in message
        assert "Example:" in message


# ============================================================
# TEST SUITE 6: Error Handling
# ============================================================

class TestAgentUnlockErrorHandling:
    """Test error handling in unlock announcement system."""

    @pytest.mark.asyncio
    async def test_channel_not_found(self, mock_bot, mock_guild, temp_db):
        """Test graceful handling when channel not found."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: None},  # No channel configured
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        # Mock get_target_channel to return None
        scheduler.get_target_channel = AsyncMock(return_value=None)

        # Should not raise exception
        await scheduler.post_agent_unlock_announcement(week=4)

        # Verify no database record was created (failed before recording)
        assert temp_db.has_announced_unlock(week_number=4) is False

    @pytest.mark.asyncio
    async def test_channel_send_error(self, mock_bot, mock_guild, mock_channel, temp_db):
        """Test graceful handling when channel send fails."""
        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={4: mock_channel.id},
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        scheduler.get_target_channel = AsyncMock(return_value=mock_channel)

        # Mock channel.send to raise exception
        mock_channel.send = AsyncMock(side_effect=Exception("Discord API error"))

        # Should not raise exception
        await scheduler.post_agent_unlock_announcement(week=4)

        # Verify no database record was created (failed before recording)
        assert temp_db.has_announced_unlock(week_number=4) is False


# ============================================================
# TEST SUITE 7: Integration with Existing System
# ============================================================

class TestAgentUnlockIntegration:
    """Test integration with existing Decision 11 unlock schedule."""

    def test_unlock_schedule_matches_router_spec(self, temp_db):
        """Test that unlock schedule matches router.py AGENTS_BY_WEEK."""
        # Week 1
        assert temp_db.get_unlocked_agents_for_week(1) == ["frame"]

        # Week 2-3
        assert temp_db.get_unlocked_agents_for_week(2) == ["frame"]
        assert temp_db.get_unlocked_agents_for_week(3) == ["frame"]

        # Week 4-5
        assert temp_db.get_unlocked_agents_for_week(4) == ["frame", "diverge", "challenge"]
        assert temp_db.get_unlocked_agents_for_week(5) == ["frame", "diverge", "challenge"]

        # Week 6-8
        assert "synthesize" in temp_db.get_unlocked_agents_for_week(6)
        assert "create-artifact" in temp_db.get_unlocked_agents_for_week(7)
        assert "edit" in temp_db.get_unlocked_agents_for_week(7)
        assert "synthesize" in temp_db.get_unlocked_agents_for_week(8)

    @pytest.mark.asyncio
    async def test_announcement_posts_to_correct_week_channel(self, mock_bot, mock_guild, temp_db):
        """Test announcements post to the correct week's channel."""
        # Create mock channels for different weeks
        week_3_channel = Mock()
        week_3_channel.id = 111
        week_3_channel.name = "week-2-3-trust"
        week_3_channel.send = AsyncMock()

        week_4_channel = Mock()
        week_4_channel.id = 222
        week_4_channel.name = "week-4-5-converse"
        week_4_channel.send = AsyncMock()

        scheduler = DailyPromptScheduler(
            bot=mock_bot,
            guild_id=12345,
            channel_mapping={
                3: week_3_channel.id,
                4: week_4_channel.id
            },
            cohort_start_date="2026-02-01",
            store=temp_db
        )

        # Mock get_target_channel to return correct channel per week
        async def mock_get_target_channel(week):
            if week == 3:
                return week_3_channel
            elif week == 4:
                return week_4_channel
            return None

        scheduler.get_target_channel = mock_get_target_channel

        # Post Week 4 announcement
        await scheduler.post_agent_unlock_announcement(week=4)

        # Verify announcement posted to Week 4 channel, not Week 3
        week_4_channel.send.assert_called_once()
        week_3_channel.send.assert_not_called()

        # Verify database recorded correct channel
        announced_agents = temp_db.get_announced_agents(week_number=4)
        assert "diverge" in announced_agents
        assert "challenge" in announced_agents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
