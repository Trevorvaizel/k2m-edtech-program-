"""
Tests for /frame command + private DM showcase workflow.
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
from commands.frame import (  # noqa: E402
    PENDING_SHOWCASE_SHARES,
    handle_frame,
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
        "current_week": 2,
        "current_state": "none",
        "zone": "zone_1",
        "jtbd_concern": "career_direction",
        "emotional_state": "curious",
    }


@pytest.fixture
def mock_student_context():
    return SimpleNamespace(
        current_week=2,
        zone="zone_1",
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
    message.content = "/frame I am confused about university pathways"
    message.reply = AsyncMock()
    message.guild = None
    return message


@pytest.fixture
def mock_dm_channel():
    channel = Mock(spec=discord.DMChannel)
    channel.send = AsyncMock()
    return channel


class TestFrameCommandFlow:
    @pytest.mark.asyncio
    async def test_handle_frame_happy_path(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        mock_message.author.create_dm.return_value = mock_dm_channel

        with patch("commands.frame.store") as mock_store, patch(
            "commands.frame.call_agent_with_context",
            new_callable=AsyncMock,
            return_value=(
                "Great framing question. Let's clarify your context.",
                {"total_tokens": 200, "total_cost_usd": 0.0042},
            ),
        ) as mock_call, patch(
            "commands.frame.celebrate_habit", return_value=None
        ), patch(
            "commands.frame.transition_state", return_value="framing"
        ), patch(
            "commands.frame.rate_limiter.check_rate_limit", return_value=(True, None)
        ), patch(
            "commands.frame.rate_limiter.track_interaction",
            return_value={"daily_total": 1.0, "weekly_total": 3.0},
        ) as mock_track, patch(
            "commands.frame._notify_budget_alerts", new_callable=AsyncMock
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []
            mock_store.get_student.return_value = {"discord_id": "123456789"}

            await handle_frame(mock_message, mock_student)

            mock_call.assert_awaited_once()
            mock_track.assert_called_once()
            assert mock_store.save_conversation.call_count == 2
            assert mock_dm_channel.send.await_count >= 2

            share_prompt = mock_dm_channel.send.await_args_list[-1].args[0]
            assert "Yes / No / Anonymous" in share_prompt
            assert has_pending_showcase_share("123456789") is True

    @pytest.mark.asyncio
    async def test_handle_frame_blocks_when_rate_limited(self, mock_message, mock_student):
        with patch(
            "commands.frame.rate_limiter.check_rate_limit",
            return_value=(False, "rate limited"),
        ):
            await handle_frame(mock_message, mock_student)

        mock_message.reply.assert_awaited_once_with("rate limited")
        mock_message.author.create_dm.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_frame_fallback_on_llm_error(
        self, mock_message, mock_student, mock_student_context, mock_dm_channel
    ):
        mock_message.author.create_dm.return_value = mock_dm_channel

        with patch("commands.frame.store") as mock_store, patch(
            "commands.frame.call_agent_with_context",
            new_callable=AsyncMock,
            side_effect=Exception("provider down"),
        ), patch(
            "commands.frame.rate_limiter.check_rate_limit", return_value=(True, None)
        ):
            mock_store.build_student_context.return_value = mock_student_context
            mock_store.get_conversation_history.return_value = []

            await handle_frame(mock_message, mock_student)

            assert mock_dm_channel.send.await_count == 1
            fallback = mock_dm_channel.send.await_args.args[0]
            assert "taking a short break" in fallback
            assert "PAUSE" in fallback


class TestShowcaseShareDecision:
    @pytest.mark.asyncio
    async def test_share_yes_publishes_to_showcase(self):
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "I am choosing between engineering and design",
            "week": 2,
            "zone": "zone_1",
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
            "commands.frame._find_showcase_channel", return_value=showcase_channel
        ), patch(
            "commands.frame.post_to_discord_safe",
            new_callable=AsyncMock,
        ) as mock_safe_send:
            handled = await handle_showcase_share_response(message)

        assert handled is True
        mock_safe_send.assert_awaited_once()
        kwargs = mock_safe_send.await_args.kwargs
        assert kwargs["channel"] is showcase_channel
        assert kwargs["is_showcase"] is True
        showcase_channel.send.assert_not_called()
        message.reply.assert_awaited_once()
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_share_no_keeps_private(self):
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "private thought",
            "week": 1,
            "zone": "zone_0",
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
        assert has_pending_showcase_share(discord_id) is False

    @pytest.mark.asyncio
    async def test_pending_share_invalid_choice_prompts_again(self):
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "private thought",
            "week": 1,
            "zone": "zone_0",
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
        assert "Yes" in prompt and "Anonymous" in prompt
        assert has_pending_showcase_share(discord_id) is True

    @pytest.mark.asyncio
    async def test_share_yes_blocks_unfinished_showcase_content(self):
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "I am still working on this artifact",
            "week": 2,
            "zone": "zone_1",
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
            "commands.frame._find_showcase_channel", return_value=showcase_channel
        ):
            handled = await handle_showcase_share_response(message)

        assert handled is True
        showcase_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_share_yes_keeps_private_when_safe_gateway_blocks(self):
        discord_id = "123456789"
        PENDING_SHOWCASE_SHARES[discord_id] = {
            "created_at": datetime.now(timezone.utc),
            "snippet": "I am choosing between engineering and design",
            "week": 2,
            "zone": "zone_1",
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
            "commands.frame._find_showcase_channel", return_value=showcase_channel
        ), patch(
            "commands.frame.post_to_discord_safe",
            new_callable=AsyncMock,
            side_effect=ComparisonViolationError("blocked"),
        ):
            handled = await handle_showcase_share_response(message)

        assert handled is True
        showcase_channel.send.assert_not_called()
        message.reply.assert_awaited_once()
        assert has_pending_showcase_share(discord_id) is False
        message.reply.assert_awaited_once()
        assert has_pending_showcase_share(discord_id) is False
