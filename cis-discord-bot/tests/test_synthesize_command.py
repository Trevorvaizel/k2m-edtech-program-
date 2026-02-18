"""
Tests for /synthesize command + private DM showcase workflow.
Story 4.5 + Task 3.3 implementation.
"""

import os
import sys
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cis_controller.safety_filter import ComparisonViolationError  # noqa: E402
from commands.synthesize import (  # noqa: E402
    PENDING_SHOWCASE_SHARES,
    handle_synthesize,
    handle_showcase_share_response,
    has_pending_showcase_share,
)


@pytest.fixture(autouse=True)
def clear_pending_shares():
    PENDING_SHOWCASE_SHARES.clear()
    yield
    PENDING_SHOWCASE_SHARES.clear()


@pytest.fixture
def mock_student():
    return {
        "discord_id": "123456789",
        "current_week": 6,  # Week 6 - /synthesize unlocked
        "current_state": "none",
        "zone": "zone_3",  # Zone 3 for Synthesizer
        "jtbd_concern": "career_direction",
        "emotional_state": "focused",
    }


@pytest.fixture
def mock_student_context():
    return SimpleNamespace(
        current_week=6,
        zone="zone_3",
        current_state="none",
        emotional_state="focused",
        jtbd_primary_concern="career_direction",
    )


@pytest.fixture
def mock_message():
    message = Mock(spec=discord.Message)
    message.author = Mock(spec=discord.User)
    message.author.id = 123456789
    message.author.display_name = "Trevor"
    message.author.create_dm = AsyncMock()
    message.content = "/synthesize I want to articulate my conclusions about university"
    message.reply = AsyncMock()
    message.guild = None
    return message


@pytest.fixture
def mock_dm_channel():
    channel = Mock(spec=discord.DMChannel)
    channel.send = AsyncMock()
    return channel


class TestSynthesizeCommandFlow:
    @pytest.mark.asyncio
    async def test_handle_synthesize_happy_path(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        """Test complete /synthesize flow with LLM integration and showcase prompt."""
        mock_message.author.create_dm.return_value = mock_dm_channel

        with patch("commands.synthesize.store") as mock_store, patch(
            "commands.synthesize.call_agent_with_context",
            new_callable=AsyncMock,
            return_value=(
                "Looking at what you've explored and challenged, what stands out most? "
                "You framed your question about university, explored options, and challenged assumptions. "
                "Putting it all together: what's YOUR conclusion?",
                {"total_tokens": 250, "total_cost_usd": 0.0052},
            ),
        ) as mock_call, patch(
            "commands.synthesize.celebrate_habit", return_value=None
        ), patch(
            "commands.synthesize.transition_state", return_value="synthesizing"
        ), patch(
            "commands.synthesize.rate_limiter.check_rate_limit", return_value=(True, None)
        ), patch(
            "commands.synthesize.rate_limiter.track_interaction",
            return_value={"daily_total": 1.0, "weekly_total": 3.0},
        ) as mock_track, patch(
            "commands.synthesize._notify_budget_alerts", new_callable=AsyncMock
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []
            mock_store.get_student.return_value = {"discord_id": "123456789"}

            await handle_synthesize(mock_message, mock_student)

            # Verify LLM was called
            mock_call.assert_awaited_once()
            call_args = mock_call.call_args
            assert call_args[1]["agent"] == "synthesize"
            assert call_args[1]["user_message"] == "I want to articulate my conclusions about university"

            # Verify rate tracking
            mock_track.assert_called_once()

            # Verify conversation saved (user + assistant)
            assert mock_store.save_conversation.call_count == 2
            save_calls = mock_store.save_conversation.call_args_list
            assert save_calls[0][1]["agent"] == "synthesize"
            assert save_calls[0][1]["role"] == "user"
            assert save_calls[1][1]["role"] == "assistant"

            # Verify DM sent with response + showcase prompt
            assert mock_dm_channel.send.await_count >= 2

            share_prompt = mock_dm_channel.send.await_args_list[-1].args[0]
            assert "Yes / No / Anonymous" in share_prompt
            assert has_pending_showcase_share("123456789") is True

            # Verify Habit 4 practice tracked
            mock_store.update_habit_practice.assert_called_once_with("123456789", habit_id=4)

    @pytest.mark.asyncio
    async def test_handle_synthesize_blocks_when_rate_limited(self, mock_message, mock_student):
        """Test that rate limiting blocks /synthesize command."""
        with patch(
            "commands.synthesize.rate_limiter.check_rate_limit",
            return_value=(False, "Rate limit exceeded. Try again tomorrow."),
        ):
            await handle_synthesize(mock_message, mock_student)

        mock_message.reply.assert_awaited_once_with("Rate limit exceeded. Try again tomorrow.")
        mock_message.author.create_dm.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_synthesize_fallback_on_llm_error(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        """Test graceful fallback when LLM provider fails."""
        mock_message.author.create_dm.return_value = mock_dm_channel

        with patch("commands.synthesize.store") as mock_store, patch(
            "commands.synthesize.call_agent_with_context",
            new_callable=AsyncMock,
            side_effect=Exception("LLM provider down"),
        ), patch(
            "commands.synthesize.rate_limiter.check_rate_limit", return_value=(True, None)
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []

            await handle_synthesize(mock_message, mock_student)

            # Verify fallback message sent
            assert mock_dm_channel.send.await_count == 1
            fallback = mock_dm_channel.send.await_args.args[0]
            assert "taking a short break" in fallback
            assert "THINK FIRST" in fallback
            assert "articulate your thinking clearly" in fallback

    @pytest.mark.asyncio
    async def test_handle_synthesize_blocks_dm_forbidden(
        self, mock_message, mock_student, mock_student_context
    ):
        """Test handling when user has DMs disabled."""
        response = Mock()
        response.status = 403
        response.reason = "Forbidden"
        mock_message.author.create_dm.side_effect = discord.Forbidden(
            response=response,
            message="Forbidden",
        )

        with patch("commands.synthesize.store") as mock_store, patch(
            "commands.synthesize.rate_limiter.check_rate_limit", return_value=(True, None)
        ):
            mock_store.build_student_context.return_value = mock_student_context

            await handle_synthesize(mock_message, mock_student)

        mock_message.reply.assert_awaited_once()
        reply_arg = mock_message.reply.await_args.args[0]
        assert "Cannot start DM" in reply_arg
        assert "enable DMs" in reply_arg

    @pytest.mark.asyncio
    async def test_handle_synthesize_empty_message_uses_default(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        """Test that empty /synthesize uses default articulation prompt."""
        mock_message.author.create_dm.return_value = mock_dm_channel
        mock_message.content = "/synthesize"  # No conclusion topic

        with patch("commands.synthesize.store") as mock_store, patch(
            "commands.synthesize.call_agent_with_context",
            new_callable=AsyncMock,
            return_value=(
                "Let's articulate your conclusions together.",
                {"total_tokens": 150, "total_cost_usd": 0.0031},
            ),
        ) as mock_call, patch(
            "commands.synthesize.safety_filter.validate_no_comparison",
            return_value=True,
        ), patch(
            "commands.synthesize.celebrate_habit", return_value=None
        ), patch(
            "commands.synthesize.transition_state", return_value="synthesizing"
        ), patch(
            "commands.synthesize.rate_limiter.check_rate_limit", return_value=(True, None)
        ), patch(
            "commands.synthesize.rate_limiter.track_interaction",
            return_value={"daily_total": 1.0, "weekly_total": 3.0},
        ), patch(
            "commands.synthesize._notify_budget_alerts", new_callable=AsyncMock
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []
            mock_store.get_student.return_value = {"discord_id": "123456789"}

            await handle_synthesize(mock_message, mock_student)

            # Verify default message was used
            call_args = mock_call.call_args
            assert call_args[1]["user_message"] == "Help me articulate my conclusions."


class TestSynthesizeWeekUnlock:
    @pytest.mark.asyncio
    async def test_synthesize_locked_before_week_6(
        self, mock_message, mock_student, mock_student_context
    ):
        """Test /synthesize is locked before Week 6."""
        mock_student_context.current_week = 5  # Week 5 - too early

        with patch("commands.synthesize.store") as mock_store, patch(
            "commands.synthesize.rate_limiter.check_rate_limit", return_value=(True, None)
        ):
            mock_store.build_student_context.return_value = mock_student_context

            await handle_synthesize(mock_message, mock_student)

        mock_message.reply.assert_awaited_once()
        reply_arg = mock_message.reply.await_args.args[0]
        assert "unlocks in Week 6" in reply_arg
        assert "Current week: 5" in reply_arg
        mock_message.author.create_dm.assert_not_called()

    @pytest.mark.asyncio
    async def test_synthesize_unlocked_week_6(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        """Test /synthesize is unlocked in Week 6."""
        mock_student_context.current_week = 6  # Week 6 - unlocked
        mock_message.author.create_dm.return_value = mock_dm_channel

        with patch("commands.synthesize.store") as mock_store, patch(
            "commands.synthesize.call_agent_with_context",
            new_callable=AsyncMock,
            return_value=(
                "Let's synthesize your thinking.",
                {"total_tokens": 150, "total_cost_usd": 0.0031},
            ),
        ), patch(
            "commands.synthesize.safety_filter.validate_no_comparison"
        ), patch(
            "commands.synthesize.celebrate_habit", return_value=None
        ), patch(
            "commands.synthesize.transition_state"
        ), patch(
            "commands.synthesize.rate_limiter.check_rate_limit", return_value=(True, None)
        ), patch(
            "commands.synthesize.rate_limiter.track_interaction",
            return_value={},
        ), patch(
            "commands.synthesize._notify_budget_alerts", new_callable=AsyncMock
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []
            mock_store.get_student.return_value = {"discord_id": "123456789"}

            await handle_synthesize(mock_message, mock_student)

            # Verify DM was created and agent was called (unlocked)
            mock_message.author.create_dm.assert_awaited_once()
            mock_dm_channel.send.assert_awaited()

    @pytest.mark.asyncio
    async def test_synthesize_unlocked_week_7(self):
        """Test /synthesize remains unlocked in Week 7+."""
        from cis_controller.router import is_agent_unlocked

        assert is_agent_unlocked("synthesize", 6) is True
        assert is_agent_unlocked("synthesize", 7) is True
        assert is_agent_unlocked("synthesize", 8) is True

    @pytest.mark.asyncio
    async def test_synthesize_locked_before_week_6_router(self):
        """Test router locks /synthesize before Week 6."""
        from cis_controller.router import is_agent_unlocked

        assert is_agent_unlocked("synthesize", 1) is False
        assert is_agent_unlocked("synthesize", 4) is False
        assert is_agent_unlocked("synthesize", 5) is False

    @pytest.mark.asyncio
    async def test_get_unlocked_agents_includes_synthesize_week_6(self):
        """Test get_unlocked_agents returns /synthesize from Week 6 onwards."""
        from cis_controller.router import get_unlocked_agents

        week_5_agents = get_unlocked_agents(5)
        assert "synthesize" not in week_5_agents

        week_6_agents = get_unlocked_agents(6)
        assert "synthesize" in week_6_agents

        week_8_agents = get_unlocked_agents(8)
        assert "synthesize" in week_8_agents


class TestShowcaseShareDecision:
    @pytest.mark.asyncio
    async def test_share_yes_publishes_to_showcase(self):
        """Test Yes decision publishes synthesis to showcase."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "Articulated my conclusion about university choice",
            "week": 6,
            "zone": "zone_3",
        }

        message = Mock(spec=discord.Message)
        message.author = Mock(spec=discord.User)
        message.author.id = int(discord_id)
        message.author.display_name = "Trevor"
        message.author.mutual_guilds = []
        message.content = "Yes"
        message.reply = AsyncMock()
        message.guild = None
        message.channel = Mock(spec=discord.DMChannel)

        showcase_channel = Mock(spec=discord.TextChannel)
        showcase_channel.send = AsyncMock()

        with patch(
            "commands.synthesize._find_showcase_channel", return_value=showcase_channel
        ), patch(
            "commands.synthesize.post_to_discord_safe",
            new_callable=AsyncMock,
        ) as mock_safe_send:
            handled = await handle_showcase_share_response(message)

        assert handled is True
        mock_safe_send.assert_awaited_once()
        kwargs = mock_safe_send.await_args.kwargs
        assert kwargs["channel"] is showcase_channel
        assert kwargs["is_showcase"] is True

        # Verify showcase post is celebration-only and keeps DM details private.
        post_text = kwargs["message_text"]
        assert "Articulated their thinking clearly in a private session." in post_text
        assert "Pause + Context + Iterate + Think First" in post_text
        assert "Articulated my conclusion about university choice" not in post_text

        showcase_channel.send.assert_not_called()
        message.reply.assert_awaited_once()
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_share_anonymous_publishes_without_name(self):
        """Test Anonymous decision publishes without student name."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "Synthesized my thinking about career",
            "week": 6,
            "zone": "zone_3",
        }

        message = Mock(spec=discord.Message)
        message.author = Mock(spec=discord.User)
        message.author.id = int(discord_id)
        message.author.mutual_guilds = []
        message.content = "anonymous"
        message.reply = AsyncMock()
        message.guild = None
        message.channel = Mock(spec=discord.DMChannel)

        showcase_channel = Mock(spec=discord.TextChannel)
        showcase_channel.send = AsyncMock()

        with patch(
            "commands.synthesize._find_showcase_channel", return_value=showcase_channel
        ), patch(
            "commands.synthesize.post_to_discord_safe",
            new_callable=AsyncMock,
        ) as mock_safe_send:
            handled = await handle_showcase_share_response(message)

        assert handled is True
        post_text = mock_safe_send.await_args.kwargs["message_text"]
        assert "A student" in post_text  # Anonymous
        assert "Trevor" not in post_text
        assert "Synthesized my thinking about career" not in post_text
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_share_no_keeps_private(self):
        """Test No decision keeps synthesis private."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "private synthesis",
            "week": 6,
            "zone": "zone_3",
        }

        message = Mock(spec=discord.Message)
        message.author = Mock(spec=discord.User)
        message.author.id = int(discord_id)
        message.content = "No"
        message.reply = AsyncMock()
        message.channel = Mock(spec=discord.DMChannel)

        handled = await handle_showcase_share_response(message)

        assert handled is True
        message.reply.assert_awaited_once()
        reply_text = message.reply.await_args.args[0]
        assert "private" in reply_text.lower()
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_share_maybe_later_saves_progress(self):
        """Test Maybe Later decision saves progress for future sharing."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "synthesis in progress",
            "week": 6,
            "zone": "zone_3",
        }

        message = Mock(spec=discord.Message)
        message.author = Mock(spec=discord.User)
        message.author.id = int(discord_id)
        message.content = "maybe later"
        message.reply = AsyncMock()
        message.channel = Mock(spec=discord.DMChannel)

        handled = await handle_showcase_share_response(message)

        assert handled is True
        message.reply.assert_awaited_once()
        reply_text = message.reply.await_args.args[0]
        assert "saved your progress" in reply_text.lower()
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_pending_share_invalid_choice_prompts_again(self):
        """Test invalid share choice prompts user to choose valid option."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "synthesis thought",
            "week": 6,
            "zone": "zone_3",
        }

        message = Mock(spec=discord.Message)
        message.author = Mock(spec=discord.User)
        message.author.id = int(discord_id)
        message.content = "hmm maybe"
        message.reply = AsyncMock()
        message.channel = Mock(spec=discord.DMChannel)

        handled = await handle_showcase_share_response(message)

        assert handled is True
        prompt = message.reply.await_args.args[0]
        assert "Yes" in prompt and "Anonymous" in prompt and "No" in prompt
        assert has_pending_showcase_share(discord_id) is True

    @pytest.mark.asyncio
    async def test_share_yes_blocks_unfinished_showcase_content(self):
        """Test that unfinished work phrases are blocked from showcase."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "I am still synthesizing this draft",
            "week": 6,
            "zone": "zone_3",
        }

        message = Mock(spec=discord.Message)
        message.author = Mock(spec=discord.User)
        message.author.id = int(discord_id)
        message.author.display_name = "Trevor"
        message.author.mutual_guilds = []
        message.content = "Yes"
        message.reply = AsyncMock()
        message.guild = None
        message.channel = Mock(spec=discord.DMChannel)

        showcase_channel = Mock(spec=discord.TextChannel)
        showcase_channel.send = AsyncMock()

        with patch(
            "commands.synthesize._find_showcase_channel", return_value=showcase_channel
        ), patch(
            "commands.synthesize.post_to_discord_safe",
            new_callable=AsyncMock,
            side_effect=ComparisonViolationError("Unfinished work detected"),
        ):
            handled = await handle_showcase_share_response(message)

        assert handled is True
        showcase_channel.send.assert_not_called()
        message.reply.assert_awaited_once()
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_share_yes_handles_showcase_channel_not_found(self):
        """Test graceful handling when showcase channel can't be found."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "Synthesis complete",
            "week": 6,
            "zone": "zone_3",
        }

        message = Mock(spec=discord.Message)
        message.author = Mock(spec=discord.User)
        message.author.id = int(discord_id)
        message.content = "Yes"
        message.reply = AsyncMock()
        message.guild = None
        message.channel = Mock(spec=discord.DMChannel)

        with patch(
            "commands.synthesize._find_showcase_channel", return_value=None
        ):
            handled = await handle_showcase_share_response(message)

        assert handled is True
        message.reply.assert_awaited_once()
        reply_text = message.reply.await_args.args[0]
        assert "kept this private" in reply_text.lower()
        assert has_pending_showcase_share(discord_id) is False
