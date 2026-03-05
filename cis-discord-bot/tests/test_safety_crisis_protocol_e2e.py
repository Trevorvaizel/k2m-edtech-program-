"""
Task 5.4 integration test: safety and crisis protocol validation.

Validates sprint task 5.4 acceptance criteria from playbook-v2:
1) Comparison language in public channels is blocked by SafetyFilter.
2) Crisis keywords trigger Level 4 protocol (instant Trevor alert + Kenya resources).
3) 3-day inactivity triggers escalation.
4) 7-day inactivity triggers Trevor DM prompt.
5) #moderation-logs captures safety/escalation events.
6) Private DM responses do not leak to public channels.
"""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

import cis_controller.router as router
from cis_controller.escalation_system import EAT, EscalationSystem
from database.store import StudentStateStore


class _RouterTestBot:
    def __init__(self):
        self.process_commands = AsyncMock()
        self.fetch_user = AsyncMock()
        self.get_channel = Mock()
        self.guilds = []

    def event(self, fn):
        setattr(self, fn.__name__, fn)
        return fn


def _build_public_message(*, author_id: int, content: str, channel, guild):
    message = Mock()
    message.id = author_id * 1000
    message.author = Mock()
    message.author.bot = False
    message.author.id = author_id
    message.author.display_name = f"student-{author_id}"
    message.author.name = f"student-{author_id}"
    message.author.dm_channel = None
    message.author.create_dm = AsyncMock()
    message.content = content
    message.channel = channel
    message.guild = guild
    message.reply = AsyncMock()
    message.add_reaction = AsyncMock()
    return message


def _sent_texts(channel):
    return [call.args[0] for call in channel.send.await_args_list]


@pytest.fixture
def store():
    db_dir = Path(__file__).resolve().parent / ".tmp-task-5-4-db"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / f"task_5_4_e2e_{uuid4().hex}.db"
    state_store = StudentStateStore(str(db_path))
    yield state_store
    state_store.close()
    try:
        db_path.unlink(missing_ok=True)
    except PermissionError:
        pass


@pytest.mark.asyncio
async def test_safety_and_crisis_protocol_end_to_end(monkeypatch, store):
    monkeypatch.setenv("FACILITATOR_DISCORD_ID", "999888777")
    monkeypatch.setenv("CHANNEL_MODERATION_LOGS", "902")

    dashboard_channel = Mock()
    dashboard_channel.id = 901
    dashboard_channel.name = "facilitator-dashboard"
    dashboard_channel.send = AsyncMock()

    moderation_logs_channel = Mock()
    moderation_logs_channel.id = 902
    moderation_logs_channel.name = "moderation-logs"
    moderation_logs_channel.send = AsyncMock()

    thinking_lab_channel = Mock()
    thinking_lab_channel.id = 903
    thinking_lab_channel.name = "thinking-lab"
    thinking_lab_channel.send = AsyncMock()

    channels = {
        901: dashboard_channel,
        902: moderation_logs_channel,
        903: thinking_lab_channel,
    }

    guild = Mock()
    guild.id = 777
    guild.get_channel = Mock(side_effect=lambda channel_id: channels.get(channel_id))
    guild.text_channels = [thinking_lab_channel, moderation_logs_channel, dashboard_channel]

    trevor_user = Mock()
    trevor_user.send = AsyncMock()

    bot = _RouterTestBot()
    bot.get_channel.side_effect = lambda channel_id: channels.get(channel_id)
    bot.fetch_user.return_value = trevor_user
    bot.guilds = [guild]

    escalation_system = EscalationSystem(
        bot=bot,
        store=store,
        facilitator_dashboard_id=901,
        moderation_logs_id=902,
        trevor_discord_id="999888777",
    )

    # Seed one student for safety/crisis flows.
    store.create_student("111111", cohort_id="cohort-test")
    store.conn.execute(
        "UPDATE students SET emotional_state = ? WHERE discord_id = ?",
        ("overwhelmed", "111111"),
    )
    store.conn.commit()

    with patch.object(router, "store", store):
        router.set_runtime_services(escalation_system=escalation_system, participation_tracker=None)
        router.setup_bot_events(bot)

        # ------------------------------------------------------------------
        # 1) Comparison language in public channel -> blocked.
        # ------------------------------------------------------------------
        comparison_message = _build_public_message(
            author_id=111111,
            content="I am better than everyone else in this cohort.",
            channel=thinking_lab_channel,
            guild=guild,
        )
        await bot.on_message(comparison_message)

        # Blocked means no public post was emitted for the comparison content.
        assert thinking_lab_channel.send.await_count == 0
        moderation_texts = _sent_texts(moderation_logs_channel)
        assert any("Guardrail #3 Violation Logged" in text for text in moderation_texts)

        # ------------------------------------------------------------------
        # 2) Crisis keyword in public channel -> Kenya response + Trevor alert.
        # ------------------------------------------------------------------
        crisis_message = _build_public_message(
            author_id=111111,
            content="I feel hopeless. I can't go on anymore.",
            channel=thinking_lab_channel,
            guild=guild,
        )
        with patch(
            "cis_controller.router._collect_recent_public_messages",
            new_callable=AsyncMock,
            return_value=[
                "user: I feel hopeless.",
                "user: I can't go on anymore.",
                "user: Nothing is working.",
            ],
        ):
            await bot.on_message(crisis_message)

        public_texts = _sent_texts(thinking_lab_channel)
        assert any(
            "Kenya Crisis Hotline" in text and "119" in text
            for text in public_texts
        )

        trevor_texts = [call.args[0] for call in trevor_user.send.await_args_list]
        assert any("LEVEL 4" in text for text in trevor_texts)
        assert any("1 hour" in text.lower() for text in trevor_texts)

        level4_count = store.conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM escalations
            WHERE discord_id = ? AND escalation_level = 4
            """,
            ("111111",),
        ).fetchone()["c"]
        assert level4_count >= 1

        # ------------------------------------------------------------------
        # 3) 3-day inactive + 7-day inactive -> escalation checks fire.
        # ------------------------------------------------------------------
        store.create_student("333333", cohort_id="cohort-test")
        store.create_student("777777", cohort_id="cohort-test")

        date_3_days = (datetime.now(EAT) - timedelta(days=3)).strftime("%Y-%m-%d")
        date_7_days = (datetime.now(EAT) - timedelta(days=7)).strftime("%Y-%m-%d")

        store.conn.execute(
            """
            INSERT INTO daily_participation
                (discord_id, date, week_number, day_of_week, has_posted, post_count, engagement_score)
            VALUES (?, ?, 1, 'Monday', 1, 1, 3)
            """,
            ("333333", date_3_days),
        )
        store.conn.execute(
            """
            INSERT INTO daily_participation
                (discord_id, date, week_number, day_of_week, has_posted, post_count, engagement_score)
            VALUES (?, ?, 1, 'Monday', 1, 1, 3)
            """,
            ("777777", date_7_days),
        )
        store.conn.commit()

        await escalation_system.check_escalations(current_week=1)

        dashboard_texts = _sent_texts(dashboard_channel)
        assert any("ORANGE FLAG" in text for text in dashboard_texts)

        trevor_texts = [call.args[0] for call in trevor_user.send.await_args_list]
        assert any("RED FLAG" in text for text in trevor_texts)
        assert any("haven't seen you in Discord this week. Everything okay?" in text for text in trevor_texts)

        level2_count = store.conn.execute(
            "SELECT COUNT(*) AS c FROM escalations WHERE escalation_level = 2"
        ).fetchone()["c"]
        level3_count = store.conn.execute(
            "SELECT COUNT(*) AS c FROM escalations WHERE escalation_level = 3"
        ).fetchone()["c"]
        assert level2_count >= 2  # 3-day + 7-day students
        assert level3_count >= 1  # 7-day student

        # ------------------------------------------------------------------
        # 4) Moderation logs include safety + escalation events.
        # ------------------------------------------------------------------
        moderation_texts = _sent_texts(moderation_logs_channel)
        assert any("Guardrail #3 Violation Logged" in text for text in moderation_texts)
        assert any("Level 4 Crisis Logged" in text for text in moderation_texts)
        assert any("ORANGE FLAG" in text for text in moderation_texts)
        assert any("RED FLAG" in text for text in moderation_texts)

        # ------------------------------------------------------------------
        # 5) No private DM response leaks to public channels.
        # ------------------------------------------------------------------
        dm_channel = Mock()
        dm_channel.send = AsyncMock()

        frame_message = _build_public_message(
            author_id=555555,
            content="/frame Help me frame my question.",
            channel=thinking_lab_channel,
            guild=guild,
        )
        frame_message.author.create_dm = AsyncMock(return_value=dm_channel)
        frame_message.author.dm_channel = None

        private_payload = "PRIVATE FRAME RESPONSE (DM ONLY)"

        async def _fake_frame_handler(routed_message, _student):
            await routed_message.reply(private_payload)

        with patch("commands.frame.handle_frame", new=AsyncMock(side_effect=_fake_frame_handler)):
            await bot.on_message(frame_message)

        dm_texts = _sent_texts(dm_channel)
        assert any(private_payload in text for text in dm_texts)
        assert frame_message.reply.await_count == 0
        assert all(private_payload not in text for text in _sent_texts(thinking_lab_channel))

        # Avoid leaking runtime service state into unrelated tests.
        router.set_runtime_services(escalation_system=None, participation_tracker=None)
