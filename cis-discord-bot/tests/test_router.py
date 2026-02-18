"""
Tests for CIS Controller Router
Story 4.7 Implementation

Tests the temporal awareness and agent unlock schedule (Decision 11):
  Week 1:   /frame only
  Week 4+:  /frame + /diverge + /challenge
  Week 6+:  all agents + /synthesize + /create-artifact
"""

import sys
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord

from cis_controller.router import (
    is_agent_unlocked,
    normalize_command_name,
    setup_bot_events,
)
from cis_controller.safety_filter import ComparisonViolationError


class TestFrameUnlockSchedule:
    """/frame available from Week 1 through all 8 weeks"""

    def test_frame_unlocks_week_1(self):
        assert is_agent_unlocked("frame", 1) is True

    def test_frame_available_week_2(self):
        assert is_agent_unlocked("frame", 2) is True

    def test_frame_available_week_8(self):
        assert is_agent_unlocked("frame", 8) is True


class TestDivergeUnlockSchedule:
    """/diverge locked before Week 4, unlocks at Week 4"""

    def test_diverge_locked_week_1(self):
        assert is_agent_unlocked("diverge", 1) is False

    def test_diverge_locked_week_2(self):
        assert is_agent_unlocked("diverge", 2) is False

    def test_diverge_locked_week_3(self):
        assert is_agent_unlocked("diverge", 3) is False

    def test_diverge_unlocks_week_4(self):
        assert is_agent_unlocked("diverge", 4) is True

    def test_diverge_available_week_8(self):
        assert is_agent_unlocked("diverge", 8) is True


class TestChallengeUnlockSchedule:
    """/challenge locked before Week 4, unlocks at Week 4"""

    def test_challenge_locked_week_1(self):
        assert is_agent_unlocked("challenge", 1) is False

    def test_challenge_locked_week_3(self):
        assert is_agent_unlocked("challenge", 3) is False

    def test_challenge_unlocks_week_4(self):
        assert is_agent_unlocked("challenge", 4) is True

    def test_challenge_available_week_8(self):
        assert is_agent_unlocked("challenge", 8) is True


class TestSynthesizeUnlockSchedule:
    """/synthesize locked before Week 6, unlocks at Week 6"""

    def test_synthesize_locked_week_1(self):
        assert is_agent_unlocked("synthesize", 1) is False

    def test_synthesize_locked_week_4(self):
        assert is_agent_unlocked("synthesize", 4) is False

    def test_synthesize_locked_week_5(self):
        assert is_agent_unlocked("synthesize", 5) is False

    def test_synthesize_unlocks_week_6(self):
        assert is_agent_unlocked("synthesize", 6) is True

    def test_synthesize_available_week_8(self):
        assert is_agent_unlocked("synthesize", 8) is True


class TestCreateArtifactUnlockSchedule:
    """/create-artifact locked before Week 6, unlocks at Week 6"""

    def test_create_artifact_locked_week_1(self):
        assert is_agent_unlocked("create-artifact", 1) is False

    def test_create_artifact_locked_week_5(self):
        assert is_agent_unlocked("create-artifact", 5) is False

    def test_create_artifact_unlocks_week_6(self):
        assert is_agent_unlocked("create-artifact", 6) is True

    def test_create_artifact_available_week_8(self):
        assert is_agent_unlocked("create-artifact", 8) is True


class TestUnknownCommands:
    """Unknown commands must always be locked"""

    def test_unknown_command_locked_week_1(self):
        assert is_agent_unlocked("unknown-command", 1) is False

    def test_unknown_command_locked_week_8(self):
        assert is_agent_unlocked("unknown-command", 8) is False

    def test_empty_command_locked(self):
        assert is_agent_unlocked("", 8) is False


class TestWeekBoundaries:
    """Test exact boundary weeks for unlock schedule"""

    def test_all_agents_available_week_6(self):
        """At Week 6, all 5 commands must be unlocked"""
        for cmd in ["frame", "diverge", "challenge", "synthesize", "create-artifact"]:
            assert is_agent_unlocked(cmd, 6) is True, f"{cmd} should be unlocked at Week 6"

    def test_only_frame_available_week_1(self):
        """At Week 1, only /frame is available"""
        assert is_agent_unlocked("frame", 1) is True
        assert is_agent_unlocked("diverge", 1) is False
        assert is_agent_unlocked("challenge", 1) is False
        assert is_agent_unlocked("synthesize", 1) is False
        assert is_agent_unlocked("create-artifact", 1) is False

    def test_three_agents_available_week_4(self):
        """At Week 4, /frame + /diverge + /challenge are available"""
        assert is_agent_unlocked("frame", 4) is True
        assert is_agent_unlocked("diverge", 4) is True
        assert is_agent_unlocked("challenge", 4) is True
        assert is_agent_unlocked("synthesize", 4) is False
        assert is_agent_unlocked("create-artifact", 4) is False


class TestCommandNormalization:
    def test_alias_framer_maps_to_frame(self):
        assert normalize_command_name("framer") == "frame"

    def test_spaced_create_artifact_maps_to_hyphenated(self):
        assert normalize_command_name("create", "artifact now") == "create-artifact"

    def test_underscore_create_artifact_maps_to_hyphenated(self):
        assert normalize_command_name("create_artifact") == "create-artifact"


class _FakeBot:
    def __init__(self):
        self.process_commands = AsyncMock()

    def event(self, fn):
        setattr(self, fn.__name__, fn)
        return fn


class TestPublicMessageSafetyFlow:
    @pytest.mark.asyncio
    async def test_crisis_message_triggers_immediate_response_and_alert(self):
        bot = _FakeBot()
        setup_bot_events(bot)

        message = Mock(spec=discord.Message)
        message.author = Mock()
        message.author.bot = False
        message.author.id = 123456
        message.content = "I want to die"
        message.channel = Mock()
        message.channel.send = AsyncMock()

        with patch(
            "cis_controller.router.safety_filter.detect_crisis",
            return_value="mental_health_crisis",
        ), patch(
            "cis_controller.router.notify_trevor_safety_violation",
            new_callable=AsyncMock,
        ) as mock_notify, patch(
            "cis_controller.router.route_student_interaction",
            new_callable=AsyncMock,
        ) as mock_route:
            await bot.on_message(message)

        message.channel.send.assert_awaited_once()
        mock_notify.assert_awaited_once()
        mock_route.assert_not_awaited()
        bot.process_commands.assert_not_awaited()


class TestRouterIngressContracts:
    @pytest.mark.asyncio
    async def test_dm_bypasses_safety_filter_and_routes(self):
        bot = _FakeBot()
        setup_bot_events(bot)

        message = Mock(spec=discord.Message)
        message.author = Mock()
        message.author.bot = False
        message.author.id = 777
        message.content = "/frame help me"
        message.channel = Mock(spec=discord.DMChannel)

        with patch(
            "cis_controller.router.safety_filter.detect_crisis"
        ) as mock_detect, patch(
            "cis_controller.router.safety_filter.validate_no_comparison"
        ) as mock_validate, patch(
            "cis_controller.router.route_student_interaction",
            new_callable=AsyncMock,
        ) as mock_route:
            await bot.on_message(message)

        mock_detect.assert_not_called()
        mock_validate.assert_not_called()
        mock_route.assert_awaited_once_with(message)
        bot.process_commands.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def test_public_designated_channel_runs_safety_then_routes(self):
        bot = _FakeBot()
        setup_bot_events(bot)

        message = Mock(spec=discord.Message)
        message.author = Mock()
        message.author.bot = False
        message.author.id = 888
        message.content = "/frame help me"
        message.channel = Mock()
        message.channel.name = "thinking-lab"
        message.channel.send = AsyncMock()

        with patch(
            "cis_controller.router.safety_filter.detect_crisis",
            return_value=None,
        ) as mock_detect, patch(
            "cis_controller.router.safety_filter.validate_no_comparison",
            return_value=True,
        ) as mock_validate, patch(
            "cis_controller.router.route_student_interaction",
            new_callable=AsyncMock,
        ) as mock_route:
            await bot.on_message(message)

        mock_detect.assert_called_once_with("/frame help me")
        mock_validate.assert_called_once_with("/frame help me")
        mock_route.assert_awaited_once_with(message)
        bot.process_commands.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def test_comparison_violation_triggers_alert_and_stops_processing(self):
        bot = _FakeBot()
        setup_bot_events(bot)

        message = Mock(spec=discord.Message)
        message.author = Mock()
        message.author.bot = False
        message.author.id = 123456
        message.content = "Top student this week..."
        message.channel = Mock()
        message.channel.send = AsyncMock()

        with patch(
            "cis_controller.router.safety_filter.detect_crisis",
            return_value=None,
        ), patch(
            "cis_controller.router.safety_filter.validate_no_comparison",
            side_effect=ComparisonViolationError("comparison"),
        ), patch(
            "cis_controller.router.notify_trevor_safety_violation",
            new_callable=AsyncMock,
        ) as mock_notify, patch(
            "cis_controller.router.route_student_interaction",
            new_callable=AsyncMock,
        ) as mock_route:
            await bot.on_message(message)

        mock_notify.assert_awaited_once()
        mock_route.assert_not_awaited()
        bot.process_commands.assert_not_awaited()
