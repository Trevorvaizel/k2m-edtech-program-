"""
Test Suite for Daily Prompt Scheduler
Story 2.1 Implementation: Daily Prompt Scheduling
"""

import asyncio
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

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
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
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
            mock_datetime.now.return_value = datetime(2026, 1, 15)
            mock_datetime.now.return_value.weekday.return_value = 0  # Monday

            week = scheduler.get_current_week()
            assert week == 0  # Should return 0 for "before start"

    def test_week_calculation_week_1(self, scheduler):
        """Test week calculation for week 1"""
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # Feb 2, 2026 is a Monday (day 1 of week 1)
            mock_datetime.now.return_value = datetime(2026, 2, 2)
            mock_datetime.now.return_value.weekday.return_value = 0

            week = scheduler.get_current_week()
            assert week == 1

    def test_week_calculation_week_2(self, scheduler):
        """Test week calculation for week 2"""
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # Feb 9, 2026 is a Monday (day 1 of week 2)
            mock_datetime.now.return_value = datetime(2026, 2, 9)
            mock_datetime.now.return_value.weekday.return_value = 0

            week = scheduler.get_current_week()
            assert week == 2

    def test_week_calculation_cap_at_8(self, scheduler):
        """Test that week number caps at 8"""
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # April 1, 2026 is well beyond week 8
            mock_datetime.now.return_value = datetime(2026, 4, 1)
            mock_datetime.now.return_value.weekday.return_value = 0

            week = scheduler.get_current_week()
            assert week == 8  # Should cap at week 8

    def test_week_day_calculation(self, scheduler):
        """Test week and day calculation together"""
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # Feb 3, 2026 is a Tuesday of week 1
            mock_datetime.now.return_value = datetime(2026, 2, 3)
            mock_datetime.now.return_value.weekday.return_value = 1  # Tuesday

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
        with patch('scheduler.scheduler.datetime') as mock_datetime:
            # Feb 2, 2026 at 9:00 AM (Monday, Week 1)
            mock_datetime.now.return_value = datetime(2026, 2, 2, 9, 0)
            mock_datetime.now.return_value.weekday.return_value = 0  # Monday
            mock_datetime.now.return_value.date.return_value = datetime(2026, 2, 2).date()
            mock_datetime.now.return_value.time.return_value = time(9, 0)

            await scheduler.post_node_link(1, WeekDay.MONDAY)

            # Verify channel was retrieved and message sent
            scheduler.bot.get_guild.assert_called()
            channel = scheduler.bot.get_guild.return_value.get_channel.return_value
            channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_daily_prompt_at_915am(self, scheduler):
        """Test posting daily prompt at 9:15 AM"""
        with patch('scheduler.scheduler.DailyPromptLibrary') as mock_library:
            mock_prompt = MagicMock()
            mock_prompt.format_for_discord.return_value = "Test prompt content"
            mock_library.return_value.get_prompt.return_value = mock_prompt

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

            # Verify task is configured
            assert scheduler.scheduler_task.is_running() or scheduler.scheduler_task.is_looping()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
