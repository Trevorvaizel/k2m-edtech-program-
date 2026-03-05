"""
Task 5.3 integration test: CIS agent graduated introduction.

Validates:
1) Week 1 lockouts with helpful guidance
2) Week 4 unlock announcements + command routing
3) Week 6 unlock announcements + command routing
4) Full artifact flow: 6 sections -> publish -> showcase -> badge confirmation
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from cis_controller.router import handle_command
from commands.artifact import (
    handle_artifact_commands,
    handle_artifact_text_input,
    handle_create_artifact,
)
from database.store import StudentStateStore
from scheduler.scheduler import DailyPromptScheduler


@pytest.fixture
def store(tmp_path):
    db_path = tmp_path / "task_5_3_e2e.db"
    state_store = StudentStateStore(str(db_path))
    yield state_store
    state_store.close()


def _build_message(discord_id: int = 111111, content: str = ""):
    message = Mock()
    message.author = Mock()
    message.author.id = discord_id
    message.author.display_name = "Test Student"
    message.author.create_dm = AsyncMock()
    message.content = content
    message.reply = AsyncMock()
    message.guild = None
    message.channel = Mock()
    return message


def _build_channel(channel_id: int, name: str):
    channel = Mock()
    channel.id = channel_id
    channel.name = name
    channel.send = AsyncMock()
    return channel


def _messages_from(channel):
    return [call.args[0] for call in channel.send.await_args_list]


@pytest.mark.asyncio
async def test_cis_graduated_introduction_end_to_end(monkeypatch, store):
    monkeypatch.setenv("DISCORD_GUILD_ID", "777")

    store.create_student("111111", cohort_id="cohort-test")

    # ------------------------------------------------------------------
    # Week 1: only /frame works; other commands are locked with guidance.
    # ------------------------------------------------------------------
    week1_message = _build_message(content="/test")
    week1_student = store.get_student("111111")

    with patch("cis_controller.router.store", store):
        # Week 1 positive path: /frame is available and routes correctly.
        week1_message.reply.reset_mock()
        with patch(
            "commands.frame.handle_frame", new_callable=AsyncMock
        ) as mocked_frame:
            await handle_command(week1_message, week1_student, "frame")
            mocked_frame.assert_awaited_once_with(week1_message, week1_student)

        # Locked-agent guidance should not appear for /frame in Week 1.
        assert week1_message.reply.await_count == 0

        lockout_cases = [
            ("diverge", "Week 4", "commands.diverge.handle_diverge"),
            ("challenge", "Week 4", "commands.challenge.handle_challenge"),
            ("synthesize", "Week 6", "commands.synthesize.handle_synthesize"),
            (
                "create-artifact",
                "Week 6",
                "commands.artifact.handle_create_artifact",
            ),
        ]

        for command, unlock_week, handler_path in lockout_cases:
            week1_message.reply.reset_mock()
            with patch(handler_path, new_callable=AsyncMock) as mocked_handler:
                await handle_command(week1_message, week1_student, command)
                mocked_handler.assert_not_awaited()

            reply_text = week1_message.reply.await_args.args[0]
            assert "unlocks" in reply_text
            assert unlock_week in reply_text
            assert "/frame" in reply_text
            assert "You're on track" in reply_text

    # ------------------------------------------------------------------
    # Week 4 and Week 6: unlock announcements post correctly.
    # ------------------------------------------------------------------
    week4_channel = _build_channel(401, "week-4-5-converse")
    week6_channel = _build_channel(601, "week-6-7-direct")
    guild = Mock()
    guild.get_channel = Mock(
        side_effect=lambda channel_id: {
            401: week4_channel,
            601: week6_channel,
        }.get(channel_id)
    )
    bot = Mock()
    bot.get_guild = Mock(return_value=guild)

    async def safe_post_stub(*, channel, message_text, **_kwargs):
        return await channel.send(message_text)

    with patch(
        "scheduler.scheduler.post_to_discord_safe",
        new_callable=AsyncMock,
    ) as mock_safe_post:
        mock_safe_post.side_effect = safe_post_stub
        scheduler = DailyPromptScheduler(
            bot=bot,
            guild_id=777,
            channel_mapping={4: 401, 6: 601},
            cohort_start_date="2026-02-01",
            store=store,
        )

        await scheduler.post_agent_unlock_announcement(week=4)
        await scheduler.post_agent_unlock_announcement(week=6)

    week4_messages = _messages_from(week4_channel)
    week6_messages = _messages_from(week6_channel)
    assert any("/diverge" in text and "/challenge" in text for text in week4_messages)
    assert any(
        "/synthesize" in text and "/create-artifact" in text for text in week6_messages
    )

    announced_week4 = store.get_announced_agents(4)
    announced_week6 = store.get_announced_agents(6)
    assert "diverge" in announced_week4 and "challenge" in announced_week4
    assert "synthesize" in announced_week6 and "create-artifact" in announced_week6

    # ------------------------------------------------------------------
    # Week 4 and Week 6 routing checks: commands execute when unlocked.
    # ------------------------------------------------------------------
    store.update_student_week("111111", 4)
    week4_student = store.get_student("111111")
    week4_route_message = _build_message(content="/route")

    with patch("cis_controller.router.store", store), patch(
        "commands.diverge.handle_diverge", new_callable=AsyncMock
    ) as mock_diverge, patch(
        "commands.challenge.handle_challenge", new_callable=AsyncMock
    ) as mock_challenge:
        await handle_command(week4_route_message, week4_student, "diverge")
        await handle_command(week4_route_message, week4_student, "challenge")
        mock_diverge.assert_awaited_once_with(week4_route_message, week4_student)
        mock_challenge.assert_awaited_once_with(week4_route_message, week4_student)

    store.update_student_week("111111", 6)
    week6_student = store.get_student("111111")
    week6_route_message = _build_message(content="/route")

    with patch("cis_controller.router.store", store), patch(
        "commands.synthesize.handle_synthesize", new_callable=AsyncMock
    ) as mock_synthesize, patch(
        "commands.artifact.handle_create_artifact", new_callable=AsyncMock
    ) as mock_create_artifact:
        await handle_command(week6_route_message, week6_student, "synthesize")
        await handle_command(week6_route_message, week6_student, "create-artifact")
        mock_synthesize.assert_awaited_once_with(week6_route_message, week6_student)
        mock_create_artifact.assert_awaited_once_with(
            week6_route_message, week6_student
        )

    # ------------------------------------------------------------------
    # Artifact flow: 6 sections -> publish -> showcase celebration -> badge.
    # ------------------------------------------------------------------
    artifact_message = _build_message(content="/create-artifact")
    artifact_message.author.id = 111111
    artifact_message.author.display_name = "Student One"

    showcase_channel = _build_channel(102, "thinking-showcase")
    posted_message = Mock()
    posted_message.add_reaction = AsyncMock()
    showcase_channel.send = AsyncMock(return_value=posted_message)

    guild_for_publish = Mock()
    guild_for_publish.fetch_member = AsyncMock(
        return_value=Mock(display_name="Student One")
    )
    publish_bot = Mock()
    publish_bot.guilds = [guild_for_publish]

    async def publish_safe_post(*, channel, message_text, **_kwargs):
        return await channel.send(message_text)

    with patch("commands.artifact.store", store):
        await handle_create_artifact(artifact_message, week6_student)
        intro_messages = [call.args[0] for call in artifact_message.reply.await_args_list]
        assert any("Thinking Artifact Creation" in text for text in intro_messages)

        # Start and complete all 6 sections using DM plain-text flow.
        artifact_message.content = "start"
        handled = await handle_artifact_text_input(artifact_message, week6_student)
        assert handled is True

        section_inputs = [
            "I am deciding between two university programs.",
            "I reframed from choice anxiety to values clarity.",
            "I explored three paths and what each would teach me.",
            "I challenged the assumption that prestige equals fit.",
            "I concluded that fit and direction matter more than status.",
            "I learned to pause, add context, iterate, and think first.",
        ]
        for text in section_inputs:
            artifact_message.content = text
            handled = await handle_artifact_text_input(artifact_message, week6_student)
            assert handled is True

        completed_row = store.get_artifact_progress_row("111111")
        assert completed_row is not None
        assert completed_row["status"] == "completed"

        # Publishing opens in Week 8.
        store.update_student_week("111111", 8)
        week8_student = store.get_student("111111")
        artifact_message.reply.reset_mock()

        await handle_artifact_commands(artifact_message, week8_student, "publish")
        publish_prompt = artifact_message.reply.await_args.args[0]
        assert "confirm public" in publish_prompt
        assert "confirm anonymous" in publish_prompt
        assert "confirm private" in publish_prompt

        artifact_message.reply.reset_mock()
        artifact_message.content = "confirm public"

        with patch(
            "commands.artifact._find_showcase_channel",
            return_value=showcase_channel,
        ), patch(
            "cis_controller.safety_filter.post_to_discord_safe",
            new_callable=AsyncMock,
        ) as mock_publish_safe:
            mock_publish_safe.side_effect = publish_safe_post
            handled = await handle_artifact_text_input(
                artifact_message,
                week8_student,
                bot=publish_bot,
            )
            assert handled is True

        # Showcase publication contains full artifact structure and 4-habit badge line.
        showcase_post_text = showcase_channel.send.await_args.args[0]
        assert "THE QUESTION I WRESTLED WITH" in showcase_post_text
        assert "HOW I REFRAMED IT" in showcase_post_text
        assert "WHAT I EXPLORED" in showcase_post_text
        assert "WHAT I CHALLENGED" in showcase_post_text
        assert "WHAT I CONCLUDED" in showcase_post_text
        assert "WHAT THIS TAUGHT ME" in showcase_post_text
        assert "4 Habits Earned" in showcase_post_text

        confirmation_texts = [
            call.args[0] for call in artifact_message.reply.await_args_list
        ]
        assert any("You've officially earned" in text for text in confirmation_texts)
        assert any("Habit 1 Badge" in text for text in confirmation_texts)
        assert any("Habit 4 Badge" in text for text in confirmation_texts)

        publications = store.get_student_publications("111111")
        assert any(
            row["publication_type"] == "artifact_completion"
            and row["visibility_level"] == "public"
            for row in publications
        )

        published_row = store.get_artifact_progress_row("111111")
        assert published_row["status"] == "published"
