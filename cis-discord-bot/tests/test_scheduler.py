"""
Test Suite for Daily Prompt Scheduler
Story 2.1 Implementation: Daily Prompt Scheduling
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scheduler.daily_prompts import DailyPrompt, DailyPromptLibrary, WeekDay
from scheduler.scheduler import DailyPromptScheduler


# ============================================================
# TEST DAILY PROMPT LIBRARY
# ============================================================

class TestDailyPromptLibrary:
    """Test daily prompt library loading and parsing"""

    @pytest.fixture
    def sample_library_content(self):
        """Create a sample daily prompt library markdown file"""
        return """# Story 3.6: Daily Async Prompt Library

#### **Monday (Week 1): Witness AI in Your Life**

🎯 TODAY'S PRACTICE: Witness AI in Your Life

You've been using AI for years without knowing it.

**Task:**
Find ONE example of AI you already use:
• Spotify/Netflix recommendations?
• Email spam filter?

Post your example: "I just realized I use AI when..."

⏸️ HABIT 1 PRACTICE: Before you scroll, pause and ask: "What am I actually looking for?"

No right answers. Just noticing.

#### **Tuesday (Week 1): People Like Me**

🎯 TODAY'S PRACTICE: People Like Me

Yesterday you noticed AI around you. Today: Who uses it?

**Task:**
Think of ONE person you know who uses AI:
• Your mom using Google Maps?

Post: "[Someone] uses AI when they..."

🎯 HABIT 2 PRACTICE: Start with "I'm [situation]..." before you explain what you need.

---

#### **Wednesday (Week 1): The Tiniest Step**

🎯 TODAY'S PRACTICE: The Tiniest Step

**Task:**
Try ONE tiny thing.

Post: "I tried [X] and AI said..."

⏸️ HABIT 1 PRACTICE: Before you ask, pause for 10 seconds.

**Peer Visibility Moment:** Agent will aggregate anonymized responses in evening message.
"""

    @pytest.fixture
    def temp_library_file(self, sample_library_content):
        """Create a temporary library file for testing"""
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            newline='\n',
            delete=False,
            suffix='.md',
        ) as f:
            f.write(sample_library_content)
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    def test_load_library_from_file(self, temp_library_file):
        """Test loading library from markdown file"""
        library = DailyPromptLibrary(temp_library_file)

        # Should have loaded 3 prompts (Monday, Tuesday, Wednesday of Week 1)
        assert len(library.prompts) == 3

    def test_get_prompt_by_week_and_day(self, temp_library_file):
        """Test retrieving specific prompt"""
        library = DailyPromptLibrary(temp_library_file)

        prompt = library.get_prompt(1, WeekDay.MONDAY)
        assert prompt is not None
        assert prompt.week == 1
        assert prompt.day == WeekDay.MONDAY
        assert "Witness AI in Your Life" in prompt.title

    def test_get_nonexistent_prompt(self, temp_library_file):
        """Test retrieving prompt that doesn't exist"""
        library = DailyPromptLibrary(temp_library_file)

        prompt = library.get_prompt(5, WeekDay.FRIDAY)
        assert prompt is None

    def test_prompt_formatting(self, temp_library_file):
        """Test prompt formatting for Discord"""
        library = DailyPromptLibrary(temp_library_file)

        prompt = library.get_prompt(1, WeekDay.MONDAY)
        formatted = prompt.format_for_discord()

        assert "🎯" in formatted
        assert "**TODAY'S PRACTICE:**" in formatted
        assert "**Task:**" in formatted
        assert "⏸️ **HABIT PRACTICE:**" in formatted

    def test_peer_visibility_flag(self, temp_library_file):
        """Test peer visibility moment detection"""
        library = DailyPromptLibrary(temp_library_file)

        # Monday prompt should not have peer visibility
        monday_prompt = library.get_prompt(1, WeekDay.MONDAY)
        assert not monday_prompt.has_peer_visibility

        # Wednesday prompt should have peer visibility
        wednesday_prompt = library.get_prompt(1, WeekDay.WEDNESDAY)
        assert wednesday_prompt.has_peer_visibility

    def test_get_week_prompts(self, temp_library_file):
        """Test getting all prompts for a week"""
        library = DailyPromptLibrary(temp_library_file)

        week_1_prompts = library.get_week_prompts(1)
        assert len(week_1_prompts) == 3


# ============================================================
# TEST SCHEDULER WEEK CALCULATION
# ============================================================

class TestWeekCalculation:
    """Test week calculation logic"""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock Discord bot"""
        bot = MagicMock()
        bot.get_guild = MagicMock()
        bot.wait_until_ready = AsyncMock()
        return bot

    @pytest.fixture
    def channel_mapping(self):
        """Create a test channel mapping"""
        return {
            1: 123456789,
            2: 123456790,
            3: 123456791,
            4: 123456792,
            5: 123456793,
            6: 123456794,
            7: 123456795,
            8: 123456796,
        }

    @pytest.fixture
    def scheduler(self, mock_bot, channel_mapping):
        """Create a scheduler instance"""
        with patch('scheduler.scheduler.DailyPromptLibrary'):
            return DailyPromptScheduler(
                bot=mock_bot,
                guild_id=123456,
                channel_mapping=channel_mapping,
                cohort_start_date="2026-02-01"
            )

    def test_week_calculation_before_cohort_starts(self, scheduler):
        """Test week calculation before cohort start date"""
        # Mock current date to be before cohort start
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026, 1, 15, tzinfo=scheduler.cohort_start_date.tzinfo
            )

            week = scheduler.get_current_week()
            assert week == 0  # Should return 0 for "before start"

    def test_week_calculation_week_1(self, scheduler):
        """Test week calculation for week 1"""
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # Feb 2, 2026 is a Monday (day 1 of week 1)
            mock_datetime.now.return_value = datetime(
                2026, 2, 2, tzinfo=scheduler.cohort_start_date.tzinfo
            )

            week = scheduler.get_current_week()
            assert week == 1

    def test_week_calculation_week_2(self, scheduler):
        """Test week calculation for week 2"""
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # Feb 9, 2026 is a Monday (day 1 of week 2)
            mock_datetime.now.return_value = datetime(
                2026, 2, 9, tzinfo=scheduler.cohort_start_date.tzinfo
            )

            week = scheduler.get_current_week()
            assert week == 2

    def test_week_calculation_cap_at_8(self, scheduler):
        """Test that week number caps at 8"""
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # April 1, 2026 is well beyond week 8
            mock_datetime.now.return_value = datetime(
                2026, 4, 1, tzinfo=scheduler.cohort_start_date.tzinfo
            )

            week = scheduler.get_current_week()
            assert week == 8  # Should cap at week 8

    def test_week_day_calculation(self, scheduler):
        """Test week and day calculation together"""
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # Feb 3, 2026 is a Tuesday of week 1
            mock_datetime.now.return_value = datetime(
                2026, 2, 3, tzinfo=scheduler.cohort_start_date.tzinfo
            )

            week, day = scheduler.get_week_day()
            assert week == 1
            assert day == WeekDay.TUESDAY


# ============================================================
# TEST CHANNEL ROUTING
# ============================================================

class TestChannelRouting:
    """Test week-aware channel routing"""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock Discord bot"""
        bot = MagicMock()
        guild = MagicMock()
        channel = MagicMock()

        bot.get_guild.return_value = guild
        guild.get_channel.return_value = channel

        return bot

    @pytest.fixture
    def channel_mapping(self):
        """Create a test channel mapping"""
        return {
            1: 123456789,
            2: 123456790,
            3: 123456791,
        }

    @pytest.fixture
    def scheduler(self, mock_bot, channel_mapping):
        """Create a scheduler instance"""
        with patch('scheduler.scheduler.DailyPromptLibrary'):
            return DailyPromptScheduler(
                bot=mock_bot,
                guild_id=123456,
                channel_mapping=channel_mapping,
                cohort_start_date="2026-02-01"
            )

    @pytest.mark.asyncio
    async def test_get_target_channel_week_1(self, scheduler):
        """Test getting channel for week 1"""
        channel = await scheduler.get_target_channel(1)

        assert channel is not None
        scheduler.bot.get_guild.assert_called_once_with(123456)

    @pytest.mark.asyncio
    async def test_get_target_channel_week_not_configured(self, scheduler):
        """Test getting channel for week not in mapping"""
        channel = await scheduler.get_target_channel(5)

        assert channel is None  # Week 5 not configured

    @pytest.mark.asyncio
    async def test_get_target_channel_guild_not_found(self, scheduler):
        """Test handling when guild is not found"""
        scheduler.bot.get_guild.return_value = None

        channel = await scheduler.get_target_channel(1)

        assert channel is None


# ============================================================
# TEST SCHEDULING LOGIC
# ============================================================

class TestSchedulingLogic:
    """Test scheduler timing and posting logic"""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock Discord bot"""
        bot = MagicMock()
        guild = MagicMock()
        channel = MagicMock()

        bot.get_guild.return_value = guild
        guild.get_channel.return_value = channel
        channel.send = AsyncMock()

        return bot

    @pytest.fixture
    def channel_mapping(self):
        """Create a test channel mapping"""
        return {
            1: 123456789,
            2: 123456790,
            3: 123456791,
            4: 123456792,
            5: 123456793,
            6: 123456794,
            7: 123456795,
            8: 123456796,
        }

    @pytest.fixture
    def scheduler(self, mock_bot, channel_mapping):
        """Create a scheduler instance"""
        with patch('scheduler.scheduler.DailyPromptLibrary'):
            return DailyPromptScheduler(
                bot=mock_bot,
                guild_id=123456,
                channel_mapping=channel_mapping,
                cohort_start_date="2026-02-01"
            )

    @pytest.mark.asyncio
    async def test_post_node_link_at_9am(self, scheduler):
        """Test posting node link at 9:00 AM"""
        await scheduler.post_node_link(1, WeekDay.MONDAY)

        # Verify channel was retrieved and message sent
        scheduler.bot.get_guild.assert_called()
        channel = scheduler.bot.get_guild.return_value.get_channel.return_value
        channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_daily_prompt_at_915am(self, scheduler):
        """Test posting daily prompt at 9:15 AM"""
        mock_prompt = MagicMock()
        mock_prompt.format_for_discord.return_value = "Test prompt content"
        scheduler.library.get_prompt.return_value = mock_prompt

        await scheduler.post_daily_prompt(1, WeekDay.MONDAY)

        # Verify message was sent
        channel = scheduler.bot.get_guild.return_value.get_channel.return_value
        channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_skip_prompt_on_friday(self, scheduler):
        """Test that daily prompt is skipped on Friday"""
        with patch('scheduler.scheduler.DailyPromptLibrary'):
            await scheduler.post_daily_prompt(1, WeekDay.FRIDAY)

            # Should not send any message on Friday (reflections are separate)
            channel = scheduler.bot.get_guild.return_value.get_channel.return_value
            channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_post_peer_visibility_wednesday_6pm(self, scheduler):
        """Test posting peer visibility snapshot on Wednesday at 6 PM"""
        await scheduler.post_peer_visibility_snapshot(1)

        # Verify message was sent
        channel = scheduler.bot.get_guild.return_value.get_channel.return_value
        channel.send.assert_called_once()
        call_args = channel.send.call_args[0][0]
        assert "TODAY'S PATTERNS" in call_args
        assert "anonymized" in call_args


class TestCheckAndPostTiming:
    """Validate check_and_post runs the intended handlers per schedule slot."""

    @pytest.fixture
    def scheduler(self):
        bot = MagicMock()
        bot.get_guild.return_value = MagicMock()
        with patch('scheduler.scheduler.DailyPromptLibrary'):
            return DailyPromptScheduler(
                bot=bot,
                guild_id=123456,
                channel_mapping={1: 111, 2: 222},
                cohort_start_date="2026-02-01",
            )

    @pytest.mark.asyncio
    async def test_friday_9am_runs_reflection_and_dashboard_summary(self, scheduler):
        scheduler.post_friday_reflection = AsyncMock()
        scheduler.post_node_link = AsyncMock()
        scheduler.post_daily_summary = AsyncMock()
        scheduler.post_week8_parent_reports = AsyncMock()

        with patch('scheduler.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026, 2, 6, 9, 0, tzinfo=scheduler.cohort_start_date.tzinfo
            )
            with patch.object(scheduler, "get_week_day", return_value=(1, WeekDay.FRIDAY)):
                await scheduler.check_and_post()

        scheduler.post_friday_reflection.assert_awaited_once_with(1)
        scheduler.post_daily_summary.assert_awaited_once_with(1)
        scheduler.post_node_link.assert_not_called()
        scheduler.post_week8_parent_reports.assert_not_called()

    @pytest.mark.asyncio
    async def test_weekday_9am_runs_node_and_dashboard_summary(self, scheduler):
        scheduler.post_friday_reflection = AsyncMock()
        scheduler.post_node_link = AsyncMock()
        scheduler.post_daily_summary = AsyncMock()
        scheduler.post_agent_unlock_announcement = AsyncMock()
        scheduler.post_weekly_parent_emails = AsyncMock()

        with patch('scheduler.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026, 2, 2, 9, 0, tzinfo=scheduler.cohort_start_date.tzinfo
            )
            with patch.object(scheduler, "get_week_day", return_value=(1, WeekDay.MONDAY)):
                await scheduler.check_and_post()

        scheduler.post_node_link.assert_awaited_once_with(1, WeekDay.MONDAY)
        scheduler.post_daily_summary.assert_awaited_once_with(1)
        scheduler.post_friday_reflection.assert_not_called()
        scheduler.post_agent_unlock_announcement.assert_awaited_once_with(1)
        scheduler.post_weekly_parent_emails.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_week8_friday_9am_runs_parent_reports(self, scheduler):
        scheduler.post_friday_reflection = AsyncMock()
        scheduler.post_daily_summary = AsyncMock()
        scheduler.post_week8_parent_reports = AsyncMock()

        with patch('scheduler.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026, 3, 27, 9, 0, tzinfo=scheduler.cohort_start_date.tzinfo
            )
            with patch.object(scheduler, "get_week_day", return_value=(8, WeekDay.FRIDAY)):
                await scheduler.check_and_post()

        scheduler.post_friday_reflection.assert_awaited_once_with(8)
        scheduler.post_daily_summary.assert_awaited_once_with(8)
        scheduler.post_week8_parent_reports.assert_awaited_once_with(8)

    @pytest.mark.asyncio
    async def test_1005am_runs_artifact_inactivity_nudges(self, scheduler):
        scheduler.post_artifact_inactivity_nudges = AsyncMock()

        with patch("scheduler.scheduler.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026, 2, 2, 10, 5, tzinfo=scheduler.cohort_start_date.tzinfo
            )
            with patch.object(scheduler, "get_week_day", return_value=(1, WeekDay.MONDAY)):
                await scheduler.check_and_post()

        scheduler.post_artifact_inactivity_nudges.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_friday_5pm_runs_dashboard_summaries(self, scheduler):
        scheduler.post_friday_dashboard_summaries = AsyncMock()
        scheduler.post_weekly_artifact_celebration = AsyncMock()

        with patch('scheduler.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026, 2, 6, 17, 0, tzinfo=scheduler.cohort_start_date.tzinfo
            )
            with patch.object(scheduler, "get_week_day", return_value=(1, WeekDay.FRIDAY)):
                await scheduler.check_and_post()

        scheduler.post_friday_dashboard_summaries.assert_awaited_once_with(1)
        scheduler.post_weekly_artifact_celebration.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_6pm_runs_dashboard_summary_and_wednesday_snapshot(self, scheduler):
        scheduler.participation_tracker = MagicMock()
        scheduler.participation_tracker.check_inactive_students = AsyncMock()
        scheduler.post_peer_visibility_summary = AsyncMock()
        scheduler.post_peer_visibility_snapshot = AsyncMock()

        with patch('scheduler.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026, 2, 4, 18, 0, tzinfo=scheduler.cohort_start_date.tzinfo
            )
            with patch.object(scheduler, "get_week_day", return_value=(1, WeekDay.WEDNESDAY)):
                await scheduler.check_and_post()

        scheduler.participation_tracker.check_inactive_students.assert_awaited_once_with(1)
        scheduler.post_peer_visibility_summary.assert_awaited_once_with(1)
        scheduler.post_peer_visibility_snapshot.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_6pm_non_wednesday_skips_public_snapshot(self, scheduler):
        scheduler.participation_tracker = MagicMock()
        scheduler.participation_tracker.check_inactive_students = AsyncMock()
        scheduler.post_peer_visibility_summary = AsyncMock()
        scheduler.post_peer_visibility_snapshot = AsyncMock()

        with patch('scheduler.scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(
                2026, 2, 2, 18, 0, tzinfo=scheduler.cohort_start_date.tzinfo
            )
            with patch.object(scheduler, "get_week_day", return_value=(1, WeekDay.MONDAY)):
                await scheduler.check_and_post()

        scheduler.participation_tracker.check_inactive_students.assert_awaited_once_with(1)
        scheduler.post_peer_visibility_summary.assert_awaited_once_with(1)
        scheduler.post_peer_visibility_snapshot.assert_not_called()


# ============================================================
# EGRESS CONTRACT TESTS
# ============================================================

class TestPublicSendContracts:
    """Ensure student-facing public posts use the safety gateway."""

    @pytest.fixture
    def mock_bot(self):
        bot = MagicMock()
        guild = MagicMock()
        channel = MagicMock()

        bot.get_guild.return_value = guild
        guild.get_channel.return_value = channel
        channel.send = AsyncMock()
        return bot

    @pytest.fixture
    def scheduler(self, mock_bot):
        with patch('scheduler.scheduler.DailyPromptLibrary'):
            return DailyPromptScheduler(
                bot=mock_bot,
                guild_id=123456,
                channel_mapping={1: 123456789},
                cohort_start_date="2026-02-01",
            )

    @pytest.mark.asyncio
    async def test_node_post_uses_safe_gateway(self, scheduler):
        channel = scheduler.bot.get_guild.return_value.get_channel.return_value

        with patch('scheduler.scheduler.post_to_discord_safe', new_callable=AsyncMock) as mock_safe:
            await scheduler.post_node_link(1, WeekDay.MONDAY)

        mock_safe.assert_awaited_once()
        kwargs = mock_safe.await_args.kwargs
        assert kwargs["bot"] is scheduler.bot
        assert kwargs["channel"] is channel
        assert "Node 0.1" in kwargs["message_text"]
        channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_daily_prompt_uses_safe_gateway(self, scheduler):
        channel = scheduler.bot.get_guild.return_value.get_channel.return_value
        prompt = MagicMock()
        prompt.format_for_discord.return_value = "Test prompt content"
        scheduler.library.get_prompt.return_value = prompt

        with patch('scheduler.scheduler.post_to_discord_safe', new_callable=AsyncMock) as mock_safe:
            await scheduler.post_daily_prompt(1, WeekDay.MONDAY)

        mock_safe.assert_awaited_once()
        kwargs = mock_safe.await_args.kwargs
        assert kwargs["bot"] is scheduler.bot
        assert kwargs["channel"] is channel
        assert kwargs["message_text"] == "Test prompt content"
        channel.send.assert_not_called()


# ============================================================
# TEST INTEGRATION
# ============================================================

class TestSchedulerIntegration:
    """Integration tests for scheduler"""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock Discord bot"""
        bot = MagicMock()
        guild = MagicMock()
        channel = MagicMock()

        bot.get_guild.return_value = guild
        guild.get_channel.return_value = channel
        channel.send = AsyncMock()

        bot.wait_until_ready = AsyncMock()

        return bot

    @pytest.fixture
    def channel_mapping(self):
        """Create a test channel mapping"""
        return {
            1: 123456789,
            2: 123456790,
        }

    def test_scheduler_initialization(self, mock_bot, channel_mapping):
        """Test scheduler initialization"""
        with patch('scheduler.scheduler.DailyPromptLibrary'):
            scheduler = DailyPromptScheduler(
                bot=mock_bot,
                guild_id=123456,
                channel_mapping=channel_mapping,
                cohort_start_date="2026-02-01"
            )

            assert scheduler.guild_id == 123456
            assert scheduler.channel_mapping == channel_mapping
            assert scheduler.get_current_week() >= 0

    @pytest.mark.asyncio
    async def test_scheduler_task_loop(self, mock_bot, channel_mapping):
        """Test that scheduler task runs in a loop"""
        with patch('scheduler.scheduler.DailyPromptLibrary'):
            scheduler = DailyPromptScheduler(
                bot=mock_bot,
                guild_id=123456,
                channel_mapping=channel_mapping,
                cohort_start_date="2026-02-01"
            )

            # Verify task object is configured
            assert scheduler.scheduler_task is not None
            assert hasattr(scheduler.scheduler_task, "start")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
