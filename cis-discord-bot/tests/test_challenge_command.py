"""
Tests for /challenge command + private DM showcase workflow.
Story 4.4 + Task 3.2 implementation.
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
from commands.challenge import (  # noqa: E402
    PENDING_SHOWCASE_SHARES,
    handle_challenge,
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
        "current_week": 4,  # Week 4 - /challenge unlocked
        "current_state": "none",
        "zone": "zone_2",  # Zone 2 for Challenger
        "jtbd_concern": "career_direction",
        "emotional_state": "curious",
    }


@pytest.fixture
def mock_student_context():
    return SimpleNamespace(
        current_week=4,
        zone="zone_2",
        current_state="none",
        emotional_state="curious",
        jtbd_primary_concern="career_direction",
    )


@pytest.fixture
def mock_message():
    message = Mock(spec=discord.Message)
    message.author = Mock(spec=discord.User)
    message.author.id = 123456789
    message.author.display_name = "Trevor"
    message.author.create_dm = AsyncMock()
    message.content = "/challenge I need to choose between medicine and engineering"
    message.reply = AsyncMock()
    message.guild = None
    return message


@pytest.fixture
def mock_dm_channel():
    channel = Mock(spec=discord.DMChannel)
    channel.send = AsyncMock()
    return channel


class TestChallengeCommandFlow:
    @pytest.mark.asyncio
    async def test_handle_challenge_happy_path(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        """Test complete /challenge flow with LLM integration and showcase prompt."""
        mock_message.author.create_dm.return_value = mock_dm_channel

        with patch("commands.challenge.store") as mock_store, patch(
            "commands.challenge.call_agent_with_context",
            new_callable=AsyncMock,
            return_value=(
                "Let's examine this assumption: What if 'medicine or engineering' isn't an either/or choice? "
                "What if there are fields that combine both? What are you actually optimizing for?",
                {"total_tokens": 250, "total_cost_usd": 0.0052},
            ),
        ) as mock_call, patch(
            "commands.challenge.celebrate_habit", return_value=None
        ), patch(
            "commands.challenge.transition_state", return_value="challenging"
        ), patch(
            "commands.challenge.rate_limiter.check_rate_limit", return_value=(True, None)
        ), patch(
            "commands.challenge.rate_limiter.track_interaction",
            return_value={"daily_total": 1.0, "weekly_total": 3.0},
        ) as mock_track, patch(
            "commands.challenge._notify_budget_alerts", new_callable=AsyncMock
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []
            mock_store.get_student.return_value = {"discord_id": "123456789"}

            await handle_challenge(mock_message, mock_student)

            # Verify LLM was called
            mock_call.assert_awaited_once()
            call_args = mock_call.call_args
            assert call_args[1]["agent"] == "challenge"
            assert call_args[1]["user_message"] == "I need to choose between medicine and engineering"

            # Verify rate tracking
            mock_track.assert_called_once()

            # Verify conversation saved (user + assistant)
            assert mock_store.save_conversation.call_count == 2
            save_calls = mock_store.save_conversation.call_args_list
            assert save_calls[0][1]["agent"] == "challenge"
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
    async def test_handle_challenge_blocks_when_rate_limited(self, mock_message, mock_student):
        """Test that rate limiting blocks /challenge command."""
        with patch(
            "commands.challenge.rate_limiter.check_rate_limit",
            return_value=(False, "Rate limit exceeded. Try again tomorrow."),
        ):
            await handle_challenge(mock_message, mock_student)

        mock_message.reply.assert_awaited_once_with("Rate limit exceeded. Try again tomorrow.")
        mock_message.author.create_dm.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_challenge_fallback_on_llm_error(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        """Test graceful fallback when LLM provider fails."""
        mock_message.author.create_dm.return_value = mock_dm_channel

        with patch("commands.challenge.store") as mock_store, patch(
            "commands.challenge.call_agent_with_context",
            new_callable=AsyncMock,
            side_effect=Exception("LLM provider down"),
        ), patch(
            "commands.challenge.rate_limiter.check_rate_limit", return_value=(True, None)
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []

            await handle_challenge(mock_message, mock_student)

            # Verify fallback message sent
            assert mock_dm_channel.send.await_count == 1
            fallback = mock_dm_channel.send.await_args.args[0]
            assert "taking a short break" in fallback
            assert "THINK FIRST" in fallback
            assert "question assumptions before deciding" in fallback

    @pytest.mark.asyncio
    async def test_handle_challenge_blocks_dm_forbidden(
        self, mock_message, mock_student
    ):
        """Test handling when user has DMs disabled."""
        response = Mock()
        response.status = 403
        response.reason = "Forbidden"
        mock_message.author.create_dm.side_effect = discord.Forbidden(
            response=response,
            message="Forbidden",
        )

        with patch("commands.challenge.store") as mock_store, patch(
            "commands.challenge.rate_limiter.check_rate_limit", return_value=(True, None)
        ):
            mock_store.build_student_context.return_value = None

            await handle_challenge(mock_message, mock_student)

        mock_message.reply.assert_awaited_once()
        reply_arg = mock_message.reply.await_args.args[0]
        assert "Cannot start DM" in reply_arg
        assert "enable DMs" in reply_arg

    @pytest.mark.asyncio
    async def test_handle_challenge_empty_message_uses_default(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        """Test that empty /challenge uses default challenging prompt."""
        mock_message.author.create_dm.return_value = mock_dm_channel
        mock_message.content = "/challenge"  # No assumption to challenge

        with patch("commands.challenge.store") as mock_store, patch(
            "commands.challenge.call_agent_with_context",
            new_callable=AsyncMock,
            return_value=(
                "Let's examine your assumptions together.",
                {"total_tokens": 150, "total_cost_usd": 0.0031},
            ),
        ) as mock_call, patch(
            "commands.challenge.safety_filter.validate_no_comparison",
            return_value=True,
        ), patch(
            "commands.challenge.celebrate_habit", return_value=None
        ), patch(
            "commands.challenge.transition_state", return_value="challenging"
        ), patch(
            "commands.challenge.rate_limiter.check_rate_limit", return_value=(True, None)
        ), patch(
            "commands.challenge.rate_limiter.track_interaction",
            return_value={"daily_total": 1.0, "weekly_total": 3.0},
        ), patch(
            "commands.challenge._notify_budget_alerts", new_callable=AsyncMock
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []
            mock_store.get_student.return_value = {"discord_id": "123456789"}

            await handle_challenge(mock_message, mock_student)

            # Verify default message was used
            call_args = mock_call.call_args
            assert call_args[1]["user_message"] == "I want to challenge my assumptions."


class TestShowcaseShareDecision:
    @pytest.mark.asyncio
    async def test_share_yes_publishes_to_showcase(self):
        """Test Yes decision publishes challenging to showcase."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "Challenged the assumption that I must choose between medicine and engineering",
            "week": 4,
            "zone": "zone_2",
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
            "commands.challenge._find_showcase_channel", return_value=showcase_channel
        ), patch(
            "commands.challenge.post_to_discord_safe",
            new_callable=AsyncMock,
        ) as mock_safe_send:
            handled = await handle_showcase_share_response(message)

        assert handled is True
        mock_safe_send.assert_awaited_once()
        kwargs = mock_safe_send.await_args.kwargs
        assert kwargs["channel"] is showcase_channel
        assert kwargs["is_showcase"] is True

        # Verify Habit 4 shown in showcase post
        post_text = kwargs["message_text"]
        assert "Challenged assumptions in a private session." in post_text
        assert "Pause + Context + Think First" in post_text

        showcase_channel.send.assert_not_called()
        message.reply.assert_awaited_once()
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_share_anonymous_publishes_without_name(self):
        """Test Anonymous decision publishes without student name."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "Questioned the assumption that I'm bad at math",
            "week": 4,
            "zone": "zone_2",
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
            "commands.challenge._find_showcase_channel", return_value=showcase_channel
        ), patch(
            "commands.challenge.post_to_discord_safe",
            new_callable=AsyncMock,
        ) as mock_safe_send:
            handled = await handle_showcase_share_response(message)

        assert handled is True
        post_text = mock_safe_send.await_args.kwargs["message_text"]
        assert "A student" in post_text  # Anonymous
        assert "Trevor" not in post_text
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_share_no_keeps_private(self):
        """Test No decision keeps challenging private."""
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "private challenging",
            "week": 4,
            "zone": "zone_2",
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
            "snippet": "challenging in progress",
            "week": 4,
            "zone": "zone_2",
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
            "snippet": "challenging thought",
            "week": 4,
            "zone": "zone_2",
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
            "snippet": "I am still challenging this draft assumption",
            "week": 4,
            "zone": "zone_2",
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
            "commands.challenge._find_showcase_channel", return_value=showcase_channel
        ), patch(
            "commands.challenge.post_to_discord_safe",
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
            "snippet": "Challenging complete",
            "week": 4,
            "zone": "zone_2",
        }

        message = Mock(spec=discord.Message)
        message.author = Mock(spec=discord.User)
        message.author.id = int(discord_id)
        message.content = "Yes"
        message.reply = AsyncMock()
        message.guild = None
        message.channel = Mock(spec=discord.DMChannel)

        with patch(
            "commands.challenge._find_showcase_channel", return_value=None
        ):
            handled = await handle_showcase_share_response(message)

        assert handled is True
        message.reply.assert_awaited_once()
        reply_text = message.reply.await_args.args[0]
        assert "kept this private" in reply_text.lower()
        assert has_pending_showcase_share(discord_id) is False


class TestChallengeWeekUnlock:
    @pytest.mark.asyncio
    async def test_challenge_unlocked_week_4(self):
        """Test /challenge is unlocked in Week 4."""
        from cis_controller.router import is_agent_unlocked

        assert is_agent_unlocked("challenge", 4) is True
        assert is_agent_unlocked("challenge", 5) is True
        assert is_agent_unlocked("challenge", 6) is True

    @pytest.mark.asyncio
    async def test_challenge_locked_before_week_4(self):
        """Test /challenge is locked before Week 4."""
        from cis_controller.router import is_agent_unlocked

        assert is_agent_unlocked("challenge", 1) is False
        assert is_agent_unlocked("challenge", 2) is False
        assert is_agent_unlocked("challenge", 3) is False

    @pytest.mark.asyncio
    async def test_get_unlocked_agents_includes_challenge_week_4(self):
        """Test get_unlocked_agents returns /challenge from Week 4 onwards."""
        from cis_controller.router import get_unlocked_agents

        week_3_agents = get_unlocked_agents(3)
        assert "challenge" not in week_3_agents

        week_4_agents = get_unlocked_agents(4)
        assert "challenge" in week_4_agents

        week_6_agents = get_unlocked_agents(6)
        assert "challenge" in week_6_agents

