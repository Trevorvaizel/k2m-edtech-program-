"""
Tests for artifact command workflow (Task 4.1).
"""

import os
import sys
from unittest.mock import AsyncMock, Mock, patch

import discord
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commands import artifact
from database.models import ArtifactProgress


class _FakeArtifactProgress:
    def __init__(self, next_section: int, inactive_days: int = 0):
        self._next_section = next_section
        self._inactive_days = inactive_days

    def get_next_section(self) -> int:
        return self._next_section

    def days_since_activity(self) -> int:
        return self._inactive_days

    def is_complete(self) -> bool:
        return self._next_section == 0


@pytest.mark.asyncio
async def test_text_start_routes_not_started_artifact():
    message = Mock(spec=discord.Message)
    message.content = "start"
    message.author = Mock()
    message.author.id = 12345
    message.reply = AsyncMock()

    student = {"current_week": 6}

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "not_started"},
    ), patch(
        "commands.artifact.start_artifact",
        new_callable=AsyncMock,
    ) as mock_start:
        handled = await artifact.handle_artifact_text_input(message, student)

    assert handled is True
    mock_start.assert_awaited_once_with(message, student)


@pytest.mark.asyncio
async def test_text_section_input_routes_to_next_section_handler():
    message = Mock(spec=discord.Message)
    message.content = "Here is my reframed question."
    message.author = Mock()
    message.author.id = 22222
    message.reply = AsyncMock()

    student = {"current_week": 6}

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "in_progress"},
    ), patch(
        "database.models._load_artifact_progress",
        return_value=_FakeArtifactProgress(next_section=2),
    ), patch(
        "commands.artifact.handle_section_2_input",
        new_callable=AsyncMock,
    ) as mock_section_2:
        handled = await artifact.handle_artifact_text_input(message, student)

    assert handled is True
    mock_section_2.assert_awaited_once_with(message, "Here is my reframed question.")


@pytest.mark.asyncio
async def test_continue_sends_stuck_nudge_and_prompt():
    message = Mock(spec=discord.Message)
    message.content = "continue"
    message.author = Mock()
    message.author.id = 33333
    message.reply = AsyncMock()

    student = {"current_week": 6}
    fake_progress = _FakeArtifactProgress(next_section=3, inactive_days=3)

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "in_progress"},
    ), patch(
        "database.models._load_artifact_progress",
        return_value=fake_progress,
    ):
        handled = await artifact.handle_artifact_text_input(message, student)

    assert handled is True
    sent_payloads = [call.args[0] for call in message.reply.await_args_list]
    assert any("Section 3 nudge" in payload for payload in sent_payloads)
    assert artifact.SECTION_3_PROMPT in sent_payloads


@pytest.mark.asyncio
async def test_save_command_persists_last_activity():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 44444
    message.reply = AsyncMock()

    student = {"current_week": 6}
    progress = ArtifactProgress(status="in_progress")

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "in_progress"},
    ), patch(
        "database.models._load_artifact_progress",
        return_value=progress,
    ), patch.object(
        artifact.store,
        "save_artifact_progress",
    ) as mock_save:
        await artifact.handle_artifact_commands(message, student, "save")

    assert progress.last_activity is not None
    mock_save.assert_called_once()
    message.reply.assert_awaited()
