"""
Cluster Session Automation Tests (Task 4.4)
Story 5.1 Implementation: Live Session Scheduling + Voice Channel Management

Comprehensive tests for cluster session automation:
- 24-hour pre-session announcements
- 1-hour reminders with voice channel creation
- Voice channel cleanup after sessions
- Post-session summaries
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scheduler.cluster_sessions import ClusterSessionScheduler, EAT
from database.store import StudentStateStore


@pytest.fixture
def test_db_path(tmp_path):
    """Create temporary test database"""
    db_path = tmp_path / "test_cluster_sessions.db"
    yield str(db_path)

    # Cleanup
    import os
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def store(test_db_path):
    """Create test database store"""
    state_store = StudentStateStore(db_path=test_db_path)
    yield state_store
    state_store.close()


@pytest.fixture
def mock_bot():
    """Create mock Discord bot"""
    bot = Mock()
    bot.get_guild = Mock(return_value=Mock())
    return bot


@pytest.fixture
def mock_guild():
    """Create mock Discord guild"""
    guild = Mock()
    guild.get_channel = Mock(return_value=Mock())
    return guild


@pytest.fixture
def cluster_scheduler(mock_bot, store):
    """Create ClusterSessionScheduler instance for testing"""
    channel_mapping = {
        1: 1234567890,  # Week 1 channel ID
        2: 1234567891,  # Week 2 channel ID
    }

    scheduler = ClusterSessionScheduler(
        bot=mock_bot,
        store=store,
        guild_id=123456789,
        channel_mapping=channel_mapping
    )
    return scheduler


class TestClusterSchedule:
    """Test cluster session schedule configuration"""

    def test_cluster_schedule_mapping(self, cluster_scheduler):
        """Test that all 8 clusters have correct schedule mappings"""
        # Monday clusters
        assert cluster_scheduler.CLUSTER_SCHEDULE[1] == (0, 18, 0)
        assert cluster_scheduler.CLUSTER_SCHEDULE[4] == (0, 18, 0)
        assert cluster_scheduler.CLUSTER_SCHEDULE[7] == (0, 18, 0)

        # Wednesday clusters
        assert cluster_scheduler.CLUSTER_SCHEDULE[2] == (2, 18, 0)
        assert cluster_scheduler.CLUSTER_SCHEDULE[5] == (2, 18, 0)
        assert cluster_scheduler.CLUSTER_SCHEDULE[8] == (2, 18, 0)

        # Friday clusters
        assert cluster_scheduler.CLUSTER_SCHEDULE[3] == (4, 18, 0)
        assert cluster_scheduler.CLUSTER_SCHEDULE[6] == (4, 18, 0)

    def test_get_clusters_for_weekday(self, cluster_scheduler):
        assert cluster_scheduler.get_clusters_for_weekday(0) == [1, 4, 7]
        assert cluster_scheduler.get_clusters_for_weekday(2) == [2, 5, 8]
        assert cluster_scheduler.get_clusters_for_weekday(4) == [3, 6]

    def test_get_session_time_for_monday_cluster(self, cluster_scheduler):
        """Test getting next session time for a Monday cluster."""
        # Mock current time: Friday at noon
        friday_noon = datetime(2026, 2, 20, 12, 0)  # Friday

        with patch('scheduler.cluster_sessions.datetime') as mock_datetime:
            mock_datetime.now.return_value = friday_noon
            # Get session time for Cluster 1 (Monday)
            session_time = cluster_scheduler.get_session_time(1)
            # Should be next Monday at 6 PM
            assert session_time.weekday() == 0  # Monday
            assert session_time.hour == 18
            assert session_time.minute == 0

    def test_get_current_week_uses_cohort_start_date(self, mock_bot, store):
        """Current week should derive from configured cohort start date."""
        scheduler = ClusterSessionScheduler(
            bot=mock_bot,
            store=store,
            guild_id=123456789,
            channel_mapping={1: 111, 2: 222},
            cohort_start_date="2026-02-01",
        )

        with patch("scheduler.cluster_sessions.datetime") as mock_datetime:
            mock_datetime.now.return_value = EAT.localize(datetime(2026, 2, 10, 12, 0))
            week = scheduler.get_current_week()

        assert week == 2


class Test24HourAnnouncements:
    """Test 24-hour pre-session announcements"""

    @pytest.mark.asyncio
    async def test_announce_cluster_session_24h(self, cluster_scheduler, mock_guild):
        """Test posting 24-hour pre-session announcement"""
        # Mock channel
        mock_channel = Mock()
        mock_channel.send = AsyncMock()
        mock_channel.name = "week-1-wonder"

        mock_guild.get_channel = Mock(return_value=mock_channel)
        cluster_scheduler.bot.get_guild = Mock(return_value=mock_guild)

        # Post 24h announcement for Cluster 1
        await cluster_scheduler.announce_cluster_session_24h(cluster_id=1, topic="Habit 1 Practice")

        # Verify message was sent
        assert mock_channel.send.called
        sent_message = mock_channel.send.call_args[0][0]
        assert "Cluster 1" in sent_message
        assert "Tomorrow" in sent_message
        assert "Habit 1 Practice" in sent_message

    @pytest.mark.asyncio
    async def test_prevent_duplicate_announcements(self, cluster_scheduler, mock_guild):
        """Test that duplicate 24h announcements are prevented"""
        mock_channel = Mock()
        mock_channel.send = AsyncMock()

        mock_guild.get_channel = Mock(return_value=mock_channel)
        cluster_scheduler.bot.get_guild = Mock(return_value=mock_guild)

        # Post first announcement
        await cluster_scheduler.announce_cluster_session_24h(cluster_id=1)

        # Try to post again (should be skipped)
        await cluster_scheduler.announce_cluster_session_24h(cluster_id=1)

        # Should only be called once due to duplicate check
        assert mock_channel.send.call_count == 1


class Test1HourReminders:
    """Test 1-hour pre-session reminders with voice channel creation"""

    @pytest.mark.asyncio
    async def test_send_session_reminder_1h(self, cluster_scheduler, mock_guild):
        """Test sending 1-hour reminder and creating voice channel"""
        # Mock text channel
        mock_text_channel = Mock()
        mock_text_channel.send = AsyncMock()

        # Mock voice channel
        mock_voice_channel = Mock()
        mock_voice_channel.id = 999
        mock_voice_channel.name = "cluster-1-voice"
        mock_voice_channel.create_invite = AsyncMock(return_value=Mock(url="https://discord.gg/abc123"))
        mock_voice_channel.mention = "#cluster-1-voice"

        mock_guild.get_channel = Mock(return_value=mock_text_channel)
        cluster_scheduler.bot.get_guild = Mock(return_value=mock_guild)

        # Mock store's create_cluster_voice_channel
        cluster_scheduler.store.create_cluster_voice_channel = AsyncMock(return_value=mock_voice_channel)

        # Send 1h reminder
        await cluster_scheduler.send_session_reminder_1h(cluster_id=1)

        # Verify voice channel was created
        cluster_scheduler.store.create_cluster_voice_channel.assert_called_once()
        assert mock_voice_channel.create_invite.call_args.kwargs.get("max_age") == 7200

        # Verify reminder was sent
        assert mock_text_channel.send.called
        sent_message = mock_text_channel.send.call_args[0][0]
        assert "Cluster 1" in sent_message
        assert "Voice channel is NOW OPEN" in sent_message

    @pytest.mark.asyncio
    async def test_prevent_duplicate_reminders(self, cluster_scheduler, mock_guild):
        """Test that duplicate 1h reminders are prevented"""
        mock_text_channel = Mock()
        mock_text_channel.send = AsyncMock()
        mock_voice_channel = Mock()
        mock_voice_channel.id = 999
        mock_voice_channel.create_invite = AsyncMock(return_value=Mock(url="https://discord.gg/abc123"))
        mock_voice_channel.mention = "#cluster-1-voice"

        mock_guild.get_channel = Mock(return_value=mock_text_channel)
        cluster_scheduler.bot.get_guild = Mock(return_value=mock_guild)
        cluster_scheduler.store.create_cluster_voice_channel = AsyncMock(return_value=mock_voice_channel)

        # Send first reminder
        await cluster_scheduler.send_session_reminder_1h(cluster_id=1)

        # Try to send again (should be skipped)
        await cluster_scheduler.send_session_reminder_1h(cluster_id=1)

        # Should only be called once due to duplicate check
        assert mock_text_channel.send.call_count == 1


class TestVoiceChannelCleanup:
    """Test voice channel cleanup after sessions"""

    @pytest.mark.asyncio
    async def test_cleanup_voice_channel(self, cluster_scheduler, mock_guild):
        """Test cleaning up voice channel after session"""
        # Create and track voice channel
        mock_voice_channel = Mock()
        mock_voice_channel.id = 999
        cluster_scheduler._voice_channels[1] = 999

        # Mock guild and channel
        mock_guild.get_channel = Mock(return_value=mock_voice_channel)
        cluster_scheduler.bot.get_guild = Mock(return_value=mock_guild)

        # Mock store's delete_cluster_voice_channel
        cluster_scheduler.store.delete_cluster_voice_channel = AsyncMock()

        # Cleanup voice channel
        await cluster_scheduler.cleanup_voice_channel(cluster_id=1)

        # Verify channel was deleted
        cluster_scheduler.store.delete_cluster_voice_channel.assert_called_once_with(mock_voice_channel)

        # Verify tracking was removed
        assert 1 not in cluster_scheduler._voice_channels

    @pytest.mark.asyncio
    async def test_cleanup_nonexistent_channel(self, cluster_scheduler):
        """Test cleanup when no voice channel exists"""
        # Try to cleanup channel that wasn't created
        await cluster_scheduler.cleanup_voice_channel(cluster_id=1)

        # Should not raise error, just log warning
        # No channel to cleanup
        assert 1 not in cluster_scheduler._voice_channels

    @pytest.mark.asyncio
    async def test_cleanup_recovers_channel_from_database(self, cluster_scheduler, mock_guild):
        """Cleanup should recover active voice channel IDs after bot restart."""
        mock_voice_channel = Mock()
        mock_voice_channel.id = 999
        mock_guild.get_channel = Mock(return_value=mock_voice_channel)
        cluster_scheduler.bot.get_guild = Mock(return_value=mock_guild)

        cluster_scheduler.store.get_active_voice_channel_id = Mock(return_value="999")
        cluster_scheduler.store.delete_cluster_voice_channel = AsyncMock()

        await cluster_scheduler.cleanup_voice_channel(cluster_id=1)

        cluster_scheduler.store.delete_cluster_voice_channel.assert_called_once_with(mock_voice_channel)


class TestSessionSummaries:
    """Test post-session summaries"""

    @pytest.mark.asyncio
    async def test_post_session_summary(self, cluster_scheduler, mock_guild):
        """Test posting session summary after Trevor completes session"""
        # Mock channel
        mock_channel = Mock()
        mock_channel.send = AsyncMock()
        mock_channel.name = "week-1-wonder"

        mock_guild.get_channel = Mock(return_value=mock_channel)
        cluster_scheduler.bot.get_guild = Mock(return_value=mock_guild)

        # Mock store's record_session_attendance
        cluster_scheduler.store.record_session_attendance = Mock()

        # Post session summary
        await cluster_scheduler.post_session_summary(
            cluster_id=1,
            session_notes="Great discussion on Habit 1 practice! Students shared real examples.",
            attendance_count=20
        )

        # Verify message was sent
        assert mock_channel.send.called
        sent_message = mock_channel.send.call_args[0][0]
        assert "Cluster 1" in sent_message
        assert "Session Summary" in sent_message
        assert "Great discussion on Habit 1 practice!" in sent_message
        assert "20 students" in sent_message
        cluster_scheduler.store.record_session_attendance.assert_called_once()
        assert (
            cluster_scheduler.store.record_session_attendance.call_args.kwargs["attendance_count"]
            == 20
        )

    @pytest.mark.asyncio
    async def test_post_session_summary_without_attendance(self, cluster_scheduler, mock_guild):
        """Test posting session summary without attendance count"""
        mock_channel = Mock()
        mock_channel.send = AsyncMock()

        mock_guild.get_channel = Mock(return_value=mock_channel)
        cluster_scheduler.bot.get_guild = Mock(return_value=mock_guild)

        cluster_scheduler.store.record_session_attendance = Mock()

        # Post summary without attendance
        await cluster_scheduler.post_session_summary(
            cluster_id=1,
            session_notes="Good session today!"
        )

        # Verify message was sent
        assert mock_channel.send.called
        sent_message = mock_channel.send.call_args[0][0]
        assert "Good session today!" in sent_message
        # Should not include attendance count
        assert "students" not in sent_message.lower()

    @pytest.mark.asyncio
    async def test_post_session_summary_targets_current_week_channel(self, mock_bot, store):
        """Session summary should route to the current week's mapped channel."""
        week1_channel = Mock()
        week1_channel.send = AsyncMock()
        week2_channel = Mock()
        week2_channel.send = AsyncMock()

        mock_guild = Mock()
        mock_guild.get_channel = Mock(
            side_effect=lambda cid: week2_channel if cid == 222 else week1_channel
        )
        mock_bot.get_guild = Mock(return_value=mock_guild)

        scheduler = ClusterSessionScheduler(
            bot=mock_bot,
            store=store,
            guild_id=123456789,
            channel_mapping={1: 111, 2: 222},
            cohort_start_date="2026-02-01",
        )
        scheduler.store.record_session_attendance = Mock()

        with patch("scheduler.cluster_sessions.datetime") as mock_datetime:
            mock_datetime.now.return_value = EAT.localize(datetime(2026, 2, 10, 12, 0))
            await scheduler.post_session_summary(
                cluster_id=1,
                session_notes="Week 2 summary check",
                attendance_count=12,
            )

        assert week2_channel.send.called
        assert not week1_channel.send.called


class TestSchedulerIntegration:
    """Test scheduler integration with DailyPromptScheduler"""

    def test_check_and_post_sessions_returns_early_for_no_time_match(self, cluster_scheduler):
        """Test that check_and_post_sessions returns early when no time match"""
        # Mock time: 3:00 PM (15:00) - no session times match
        test_time = datetime(2026, 2, 19, 15, 0)  # 3 PM

        # Should not trigger any automation
        cluster_scheduler.check_and_post_sessions(current_time=test_time)

        # No announcements or reminders should be logged
        # (just verifying no errors are raised)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
