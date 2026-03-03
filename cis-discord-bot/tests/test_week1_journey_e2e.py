"""
Task 5.2 integration test: full Week 1 student journey.

This test validates the sprint flow end-to-end against Playbook-v2 behavior:
1) Student join -> welcome DM + cluster assignment
2) Monday node + prompt delivery
3) Student post -> bot reaction
4) /frame DM flow
5) Share to #thinking-showcase
6) Evening peer-visibility snapshot
7) Friday reflection prompt + submission
8) Saturday unlock + laggard handling
9) Facilitator dashboard summaries
"""

import importlib
from unittest.mock import AsyncMock, Mock, patch

import pytest

from cis_controller.participation_tracker import ParticipationTracker, WITNESS_EMOJI
from commands.frame import (
    PENDING_SHOWCASE_SHARES,
    handle_frame,
    handle_showcase_share_response,
    has_pending_showcase_share,
)
from commands.reflection import submit_reflection_handler
from database.store import StudentStateStore
from scheduler.daily_prompts import WeekDay
from scheduler.scheduler import DailyPromptScheduler


@pytest.fixture(autouse=True)
def clear_pending_showcase_shares():
    PENDING_SHOWCASE_SHARES.clear()
    yield
    PENDING_SHOWCASE_SHARES.clear()


@pytest.fixture
def store(tmp_path):
    db_path = tmp_path / "week1_e2e.db"
    state_store = StudentStateStore(str(db_path))
    yield state_store
    state_store.close()


def _build_mock_channel(channel_id: int, name: str):
    channel = Mock()
    channel.id = channel_id
    channel.name = name
    channel.send = AsyncMock()
    channel.fetch_message = AsyncMock()
    channel.set_permissions = AsyncMock()
    return channel


def _messages_from(channel) -> list[str]:
    return [call.args[0] for call in channel.send.await_args_list]


@pytest.mark.asyncio
async def test_week1_student_journey_end_to_end(monkeypatch, store):
    """
    Covers sprint Task 5.2 acceptance flow for Week 1.
    """
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_GUILD_ID", "777")
    monkeypatch.setenv("CHANNEL_FACILITATOR_DASHBOARD", "303")

    # Import main after env vars are set to safely access on_member_join.
    main_module = importlib.import_module("main")
    main_module = importlib.reload(main_module)

    week1_channel = _build_mock_channel(101, "week-1-wonder")
    week2_channel = _build_mock_channel(201, "week-2-3-trust")
    showcase_channel = _build_mock_channel(102, "thinking-showcase")
    dashboard_channel = _build_mock_channel(303, "facilitator-dashboard")
    showcase_post = Mock()
    showcase_post.add_reaction = AsyncMock()
    showcase_channel.send = AsyncMock(return_value=showcase_post)
    showcase_channel.last_message = lambda: showcase_post

    channels_by_id = {
        101: week1_channel,
        102: showcase_channel,
        201: week2_channel,
        303: dashboard_channel,
    }

    student_role = Mock()
    student_role.name = "Student"
    cluster_role = Mock()
    cluster_role.name = "Cluster-1"

    guild = Mock()
    guild.id = 777
    guild.roles = [student_role, cluster_role]
    guild.create_role = AsyncMock(return_value=cluster_role)
    guild.get_channel = Mock(side_effect=lambda channel_id: channels_by_id.get(channel_id))
    guild.text_channels = [week1_channel, week2_channel, showcase_channel, dashboard_channel]
    guild.get_member = Mock(return_value=Mock())
    guild.fetch_member = AsyncMock(return_value=Mock())

    bot = Mock()
    bot.get_guild = Mock(return_value=guild)
    bot.get_channel = Mock(side_effect=lambda channel_id: channels_by_id.get(channel_id))
    fetched_user = Mock()
    fetched_user.send = AsyncMock()
    bot.fetch_user = AsyncMock(return_value=fetched_user)

    # ---------------------------------------------------------------------
    # 1) Student joins -> welcome DM + cluster assignment
    # ---------------------------------------------------------------------
    joining_member = Mock()
    joining_member.bot = False
    joining_member.id = 111111
    joining_member.display_name = "John Anderson"
    joining_member.name = "John Anderson"
    joining_member.guild = guild
    joining_member.add_roles = AsyncMock()
    joining_member.send = AsyncMock()

    with patch("database.store.StudentStateStore", return_value=store):
        await main_module.on_member_join(joining_member)

    joined_student = store.get_student("111111")
    assert joined_student is not None
    assert joined_student["cluster_id"] == 1
    assert joining_member.send.await_count == 1
    welcome_message = joining_member.send.await_args.args[0]
    assert "Welcome to K2M Cohort #1" in welcome_message
    assert "Cluster 1" in welcome_message

    # Add one laggard student for Saturday unlock verification.
    laggard = store.create_student(discord_id="222222", last_name="Brown")
    assert laggard["current_week"] == 1

    # ---------------------------------------------------------------------
    # 2) Monday 9:00 node + 9:15 prompt
    # ---------------------------------------------------------------------
    async def safe_post_stub(*, channel, message_text, **_kwargs):
        return await channel.send(message_text)

    with patch("scheduler.scheduler.DailyPromptLibrary") as mock_library_cls, patch(
        "scheduler.scheduler.post_to_discord_safe",
        new_callable=AsyncMock,
    ) as mock_safe_post:
        library = mock_library_cls.return_value
        monday_prompt = Mock()
        monday_prompt.format_for_discord.return_value = "MONDAY 9:15 PROMPT"
        library.get_prompt.return_value = monday_prompt
        mock_safe_post.side_effect = safe_post_stub

        scheduler = DailyPromptScheduler(
            bot=bot,
            guild_id=777,
            channel_mapping={1: 101, 2: 201},
            cohort_start_date="2026-02-01",
            store=store,
        )

        await scheduler.post_node_link(1, WeekDay.MONDAY)
        await scheduler.post_daily_prompt(1, WeekDay.MONDAY)

        week_messages = _messages_from(week1_channel)
        assert any("Node 0.1" in message for message in week_messages)
        assert any("MONDAY 9:15 PROMPT" in message for message in week_messages)

        # -----------------------------------------------------------------
        # 3) Student responds -> bot reacts 👀
        # -----------------------------------------------------------------
        weekly_post = Mock()
        weekly_post.id = 9001
        weekly_post.author = Mock()
        weekly_post.author.id = 111111
        weekly_post.author.name = "John Anderson"
        weekly_post.author.bot = False
        weekly_post.guild = guild
        weekly_post.channel = week1_channel
        weekly_post.content = "I just realized I use AI when Spotify recommends songs."
        weekly_post.add_reaction = AsyncMock()
        week1_channel.fetch_message = AsyncMock(return_value=weekly_post)

        participation_tracker = ParticipationTracker(
            bot=bot,
            store=store,
            weekly_channel_ids=[101],
        )
        await participation_tracker.on_message(weekly_post)
        await participation_tracker._process_reaction_queue()
        weekly_post.add_reaction.assert_awaited_once_with(WITNESS_EMOJI)

        # -----------------------------------------------------------------
        # 4) Student uses /frame -> DM conversation works
        # -----------------------------------------------------------------
        dm_channel = Mock()
        dm_channel.send = AsyncMock()

        frame_message = Mock()
        frame_message.author = Mock()
        frame_message.author.id = 111111
        frame_message.author.display_name = "John Anderson"
        frame_message.author.mutual_guilds = [guild]
        frame_message.author.create_dm = AsyncMock(return_value=dm_channel)
        frame_message.content = "/frame I am deciding between engineering and design"
        frame_message.reply = AsyncMock()
        frame_message.guild = guild

        student_row = store.get_student("111111")
        with patch("commands.frame.store", store), patch(
            "commands.frame.call_agent_with_context",
            new_callable=AsyncMock,
            return_value=(
                "Let's frame that clearly before you ask AI.",
                {"total_tokens": 120, "total_cost_usd": 0.003},
            ),
        ), patch(
            "commands.frame.celebrate_habit",
            return_value=None,
        ), patch(
            "commands.frame.transition_state",
            return_value="framing",
        ), patch(
            "commands.frame.rate_limiter.check_rate_limit",
            return_value=(True, None),
        ), patch(
            "commands.frame.rate_limiter.track_interaction",
            return_value={"daily_total": 1.0, "weekly_total": 1.0},
        ), patch(
            "commands.frame._notify_budget_alerts",
            new_callable=AsyncMock,
        ), patch(
            "commands.frame.DISCORD_GUILD_ID",
            "",
        ), patch(
            "commands.frame.CHANNEL_THINKING_SHOWCASE",
            "",
        ):
            await handle_frame(frame_message, student_row)

        dm_messages = [call.args[0] for call in dm_channel.send.await_args_list]
        assert any("Yes / No / Anonymous" in message for message in dm_messages)
        assert has_pending_showcase_share("111111") is True

        # -----------------------------------------------------------------
        # 5) Student shares to #thinking-showcase -> celebration posts
        # -----------------------------------------------------------------
        share_decision = Mock()
        share_decision.author = frame_message.author
        share_decision.content = "Yes"
        share_decision.reply = AsyncMock()
        share_decision.guild = None
        share_decision.channel = dm_channel
        share_decision._state = Mock()
        share_decision._state._get_client = Mock(return_value=bot)

        with patch("commands.frame.store", store), patch(
            "commands.frame.DISCORD_GUILD_ID",
            "",
        ), patch(
            "commands.frame.CHANNEL_THINKING_SHOWCASE",
            "",
        ):
            handled = await handle_showcase_share_response(share_decision)

        assert handled is True
        assert showcase_channel.send.await_count >= 1
        share_decision.reply.assert_awaited_once()
        assert has_pending_showcase_share("111111") is False
        publications = store.get_student_publications("111111")
        assert any(row["visibility_level"] == "public" for row in publications)

        # -----------------------------------------------------------------
        # 6) Evening peer visibility snapshot posts (anonymized)
        # -----------------------------------------------------------------
        await scheduler.post_peer_visibility_snapshot(1)
        week_messages = _messages_from(week1_channel)
        assert any("anonymized" in message.lower() for message in week_messages)

        # -----------------------------------------------------------------
        # 7) Friday reflection prompt posts, student submits
        # -----------------------------------------------------------------
        await scheduler.post_friday_reflection(1)
        week_messages = _messages_from(week1_channel)
        assert any("FRIDAY REFLECTION" in message for message in week_messages)

        interaction = Mock()
        interaction.user = Mock()
        interaction.user.id = 111111
        interaction.user.name = "John Anderson"
        interaction.response = Mock()
        interaction.response.defer = AsyncMock()
        interaction.followup = Mock()
        interaction.followup.send = AsyncMock()

        await submit_reflection_handler(
            interaction=interaction,
            store=store,
            habit_practice="Sometimes",
            identity_shift="I moved from confused to curious.",
            proof_of_work=(
                "When I said I was choosing engineering or design, "
                "AI reflected that exact dilemma."
            ),
        )
        submitted_reflection = store.get_weekly_reflection("111111", 1)
        assert submitted_reflection is not None
        assert submitted_reflection["submitted"] == 1

        # -----------------------------------------------------------------
        # 8) Saturday unlocks next week, laggard handling works
        # -----------------------------------------------------------------
        await scheduler.batch_unlock_week(1)
        progressed = store.get_student("111111")
        still_laggard = store.get_student("222222")
        assert progressed["current_week"] == 2
        assert still_laggard["current_week"] == 1

        # Laggard notice should reach dashboard.
        dashboard_messages = _messages_from(dashboard_channel)
        assert any("<@222222>" in message for message in dashboard_messages)

        # -----------------------------------------------------------------
        # 9) Dashboard summaries fire correctly
        # -----------------------------------------------------------------
        await scheduler.post_daily_summary(1)
        await scheduler.post_peer_visibility_summary(1)
        await scheduler.post_friday_dashboard_summaries(1)

        dashboard_messages = _messages_from(dashboard_channel)
        assert any("SUMMARY" in message for message in dashboard_messages)
        assert any("EVENING SNAPSHOT" in message for message in dashboard_messages)
        assert any("FRIDAY REFLECTIONS" in message for message in dashboard_messages)
        assert any("SPOT-CHECK" in message for message in dashboard_messages)
