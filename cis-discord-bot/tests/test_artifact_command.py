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
        if next_section <= 0:
            completed_count = 6
        else:
            completed_count = max(next_section - 1, 0)
        self.completed_sections = [f"section_{idx}" for idx in range(1, completed_count + 1)]

    def get_next_section(self) -> int:
        return self._next_section

    def days_since_activity(self) -> int:
        return self._inactive_days

    def is_complete(self) -> bool:
        return self._next_section == 0


@pytest.fixture(autouse=True)
def _clear_pending_edit_state():
    artifact._PENDING_SECTION_EDITS.clear()
    yield
    artifact._PENDING_SECTION_EDITS.clear()


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
async def test_edit_section_sets_pending_state_and_prompts():
    message = Mock(spec=discord.Message)
    message.content = "edit section 4"
    message.author = Mock()
    message.author.id = 33334
    message.reply = AsyncMock()
    student = {"current_week": 6}

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "completed"},
    ):
        handled = await artifact.handle_artifact_text_input(message, student)

    assert handled is True
    assert artifact._PENDING_SECTION_EDITS["33334"] == 4
    payload = message.reply.await_args_list[0].args[0]
    assert "Editing Section 4" in payload


@pytest.mark.asyncio
async def test_pending_edit_message_updates_requested_section():
    message = Mock(spec=discord.Message)
    message.content = "Rewritten content for section 4"
    message.author = Mock()
    message.author.id = 33335
    message.reply = AsyncMock()
    student = {"current_week": 6}
    artifact._PENDING_SECTION_EDITS["33335"] = 4

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "completed"},
    ), patch.object(
        artifact.store,
        "update_artifact_section",
    ) as mock_update, patch.object(
        artifact.store,
        "log_observability_event",
    ) as mock_log:
        handled = await artifact.handle_artifact_text_input(message, student)

    assert handled is True
    mock_update.assert_called_once_with("33335", 4, "Rewritten content for section 4")
    assert mock_log.call_args.args[1] == "artifact_section_saved"
    assert "33335" not in artifact._PENDING_SECTION_EDITS
    payload = message.reply.await_args_list[0].args[0]
    assert "Section 4 updated" in payload


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


@pytest.mark.asyncio
async def test_edit_command_requires_section_argument():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 44445
    message.reply = AsyncMock()
    student = {"current_week": 6}

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "completed"},
    ):
        await artifact.handle_artifact_commands(message, student, "edit", "")

    payload = message.reply.await_args_list[0].args[0]
    assert "Use `/edit <section-number>`" in payload


@pytest.mark.asyncio
async def test_edit_command_sets_pending_section():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 44446
    message.reply = AsyncMock()
    student = {"current_week": 6}

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "in_progress"},
    ):
        await artifact.handle_artifact_commands(message, student, "edit", "3")

    assert artifact._PENDING_SECTION_EDITS["44446"] == 3
    payload = message.reply.await_args_list[0].args[0]
    assert "Editing Section 3" in payload


@pytest.mark.asyncio
async def test_confirm_private_routes_to_private_visibility():
    message = Mock(spec=discord.Message)
    message.content = "confirm private"
    message.author = Mock()
    message.author.id = 55555
    message.reply = AsyncMock()

    student = {"current_week": 8}
    fake_bot = Mock()

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "completed"},
    ), patch(
        "commands.artifact.handle_confirm_publish",
        new_callable=AsyncMock,
    ) as mock_confirm:
        handled = await artifact.handle_artifact_text_input(message, student, bot=fake_bot)

    assert handled is True
    mock_confirm.assert_awaited_once_with(fake_bot, message, "55555", "private")


@pytest.mark.asyncio
async def test_confirm_anonymous_routes_to_anonymous_visibility():
    message = Mock(spec=discord.Message)
    message.content = "confirm anonymous"
    message.author = Mock()
    message.author.id = 66666
    message.reply = AsyncMock()

    student = {"current_week": 8}
    fake_bot = Mock()

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={"status": "completed"},
    ), patch(
        "commands.artifact.handle_confirm_publish",
        new_callable=AsyncMock,
    ) as mock_confirm:
        handled = await artifact.handle_artifact_text_input(message, student, bot=fake_bot)

    assert handled is True
    mock_confirm.assert_awaited_once_with(fake_bot, message, "66666", "anonymous")


@pytest.mark.asyncio
async def test_public_confirm_uses_safety_wrapper():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 77777
    message.reply = AsyncMock()

    posted_message = Mock()
    posted_message.add_reaction = AsyncMock()
    showcase_channel = Mock()

    guild = Mock()
    guild.fetch_member = AsyncMock(return_value=Mock(display_name="Student Name"))
    bot = Mock()
    bot.guilds = [guild]

    progress = ArtifactProgress(
        section_1_question="q1",
        section_2_reframed="q2",
        section_3_explored="q3",
        section_4_challenged="q4",
        section_5_concluded="q5",
        section_6_reflection="q6",
        status="completed",
    )

    with patch(
        "database.models._load_artifact_progress",
        return_value=progress,
    ), patch(
        "commands.artifact._find_showcase_channel",
        return_value=showcase_channel,
    ), patch(
        "cis_controller.safety_filter.post_to_discord_safe",
        new_callable=AsyncMock,
        return_value=posted_message,
    ) as mock_safe, patch.object(
        artifact.store,
        "create_showcase_publication",
    ) as mock_create, patch.object(
        artifact.store,
        "save_artifact_progress",
    ) as mock_save, patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={
            "started_at": "2026-03-12T12:00:00",
            "status": "completed",
            "current_section": 6,
        },
    ), patch.object(
        artifact.store,
        "log_observability_event",
    ) as mock_log:
        await artifact.handle_confirm_publish(bot, message, "77777", "public")

    mock_safe.assert_awaited_once()
    kwargs = mock_safe.await_args.kwargs
    assert kwargs["bot"] is bot
    assert kwargs["channel"] is showcase_channel
    assert kwargs["student_discord_id"] == 77777
    assert kwargs["is_showcase"] is True
    mock_create.assert_called_once()
    mock_save.assert_called_once()
    message.reply.assert_awaited()
    event_types = [call.args[1] for call in mock_log.call_args_list]
    assert "artifact_publish_confirmed" in event_types
    assert "artifact_published" in event_types


@pytest.mark.asyncio
async def test_private_confirm_delivers_to_trevor():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 88888
    message.reply = AsyncMock()

    guild = Mock()
    guild.fetch_member = AsyncMock(return_value=Mock(display_name="Student Name"))
    bot = Mock()
    bot.guilds = [guild]
    trevor_user = Mock()
    trevor_user.send = AsyncMock()
    bot.fetch_user = AsyncMock(return_value=trevor_user)

    progress = ArtifactProgress(
        section_1_question="q1",
        section_2_reframed="q2",
        section_3_explored="q3",
        section_4_challenged="q4",
        section_5_concluded="q5",
        section_6_reflection="q6",
        status="completed",
    )

    with patch.dict(os.environ, {"FACILITATOR_DISCORD_ID": "99999"}, clear=False), patch(
        "database.models._load_artifact_progress",
        return_value=progress,
    ), patch.object(
        artifact.store,
        "create_showcase_publication",
    ) as mock_create, patch.object(
        artifact.store,
        "save_artifact_progress",
    ) as mock_save, patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={
            "started_at": "2026-03-12T12:00:00",
            "status": "completed",
            "current_section": 6,
        },
    ), patch.object(
        artifact.store,
        "log_observability_event",
    ) as mock_log:
        await artifact.handle_confirm_publish(bot, message, "88888", "private")

    bot.fetch_user.assert_awaited_once_with(99999)
    trevor_user.send.assert_awaited_once()
    mock_create.assert_called_once()
    mock_save.assert_called_once()
    message.reply.assert_awaited()
    event_types = [call.args[1] for call in mock_log.call_args_list]
    assert "artifact_publish_confirmed" in event_types
    assert "artifact_published" in event_types


@pytest.mark.asyncio
async def test_weekly_aggregate_query_excludes_private_visibility():
    fake_cursor = Mock()
    fake_cursor.fetchone.return_value = {"count": 0}
    mock_conn = Mock()
    mock_conn.execute.return_value = fake_cursor

    with patch.object(artifact.store, "conn", mock_conn):
        celebration = await artifact.generate_weekly_artifact_celebration(bot=Mock())

    assert celebration is None
    query = mock_conn.execute.call_args.args[0]
    assert "visibility_level IN ('public', 'anonymous')" in query


@pytest.mark.asyncio
async def test_send_artifact_inactivity_nudges_sends_only_inactive_students():
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        {"discord_id": "1001"},
        {"discord_id": "1002"},
    ]
    mock_conn = Mock()
    mock_conn.execute.return_value = mock_cursor
    fake_bot = Mock()
    user = Mock()
    user.send = AsyncMock()
    fake_bot.fetch_user = AsyncMock(return_value=user)

    stale_progress = _FakeArtifactProgress(next_section=3, inactive_days=4)
    fresh_progress = _FakeArtifactProgress(next_section=2, inactive_days=1)

    with patch.object(artifact.store, "conn", mock_conn), patch(
        "database.models._load_artifact_progress",
        side_effect=[stale_progress, fresh_progress],
    ), patch.object(
        artifact.store,
        "log_observability_event",
    ) as mock_log:
        sent_count = await artifact.send_artifact_inactivity_nudges(fake_bot, inactive_days=3)

    assert sent_count == 1
    fake_bot.fetch_user.assert_awaited_once_with(1001)
    user.send.assert_awaited_once()
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_start_artifact_logs_lifecycle_event():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 12121
    message.reply = AsyncMock()
    student = {"current_week": 6}

    with patch.object(
        artifact.store,
        "save_artifact_progress",
    ), patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={
            "started_at": "2026-03-12T08:00:00",
            "status": "in_progress",
            "current_section": 0,
        },
    ), patch.object(
        artifact.store,
        "log_observability_event",
    ) as mock_log:
        await artifact.start_artifact(message, student)

    mock_log.assert_called_once()
    assert mock_log.call_args.args[1] == "artifact_started"
    metadata = mock_log.call_args.args[2]
    assert metadata["entrypoint"] == "create-artifact"
    assert metadata["week"] == 6
    assert metadata["artifact_session_id"] == "2026-03-12T08:00:00"


@pytest.mark.asyncio
async def test_section_input_logs_section_saved_event():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 23232
    message.reply = AsyncMock()

    with patch.object(
        artifact.store,
        "update_artifact_section",
    ), patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={
            "started_at": "2026-03-12T09:00:00",
            "status": "in_progress",
            "current_section": 3,
        },
    ), patch.object(
        artifact.store,
        "log_observability_event",
    ) as mock_log:
        await artifact.handle_section_3_input(message, "Exploration content")

    assert mock_log.call_args.args[1] == "artifact_section_saved"
    metadata = mock_log.call_args.args[2]
    assert metadata["section"] == 3
    assert metadata["artifact_status"] == "in_progress"


@pytest.mark.asyncio
async def test_publish_command_logs_publish_requested_event():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 34343
    message.reply = AsyncMock()
    student = {"current_week": 8}

    complete_progress = ArtifactProgress(
        section_1_question="q1",
        section_2_reframed="q2",
        section_3_explored="q3",
        section_4_challenged="q4",
        section_5_concluded="q5",
        section_6_reflection="q6",
        status="completed",
    )

    with patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={
            "status": "completed",
            "started_at": "2026-03-12T10:00:00",
            "current_section": 6,
        },
    ), patch(
        "database.models._load_artifact_progress",
        return_value=complete_progress,
    ), patch(
        "commands.artifact.publish_artifact_to_showcase",
        new_callable=AsyncMock,
    ) as mock_publish, patch.object(
        artifact.store,
        "log_observability_event",
    ) as mock_log:
        await artifact.handle_artifact_commands(message, student, "publish")

    mock_publish.assert_awaited_once()
    event_types = [call.args[1] for call in mock_log.call_args_list]
    assert "artifact_publish_requested" in event_types


@pytest.mark.asyncio
async def test_confirm_publish_missing_showcase_logs_failure():
    message = Mock(spec=discord.Message)
    message.author = Mock()
    message.author.id = 45454
    message.reply = AsyncMock()

    guild = Mock()
    guild.fetch_member = AsyncMock(return_value=Mock(display_name="Student Name"))
    bot = Mock()
    bot.guilds = [guild]

    progress = ArtifactProgress(
        section_1_question="q1",
        section_2_reframed="q2",
        section_3_explored="q3",
        section_4_challenged="q4",
        section_5_concluded="q5",
        section_6_reflection="q6",
        status="completed",
    )

    with patch(
        "database.models._load_artifact_progress",
        return_value=progress,
    ), patch(
        "commands.artifact._find_showcase_channel",
        return_value=None,
    ), patch.object(
        artifact.store,
        "get_artifact_progress_row",
        return_value={
            "started_at": "2026-03-12T11:00:00",
            "status": "completed",
            "current_section": 6,
        },
    ), patch.object(
        artifact.store,
        "log_observability_event",
    ) as mock_log:
        await artifact.handle_confirm_publish(bot, message, "45454", "public")

    assert message.reply.await_count >= 1
    event_types = [call.args[1] for call in mock_log.call_args_list]
    assert "artifact_publish_confirmed" in event_types
    assert "artifact_publish_failed" in event_types
    failed_call = next(call for call in mock_log.call_args_list if call.args[1] == "artifact_publish_failed")
    assert failed_call.args[2]["reason"] == "showcase_channel_not_found"
