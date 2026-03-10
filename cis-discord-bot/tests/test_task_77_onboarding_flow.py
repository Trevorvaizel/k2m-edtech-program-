"""Task 7.7 tests: Stop 0 flow, continue-signal guard, and day-8 re-entry checks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from cis_controller.onboarding import (
    DEFAULT_STOP0_PROFILE,
    is_continue_signal,
    parse_stop0_profile_answers,
)
from database.store import StudentStateStore
from scheduler.scheduler import DailyPromptScheduler


def _message(
    content: str,
    *,
    private: bool,
    author_bot: bool,
    recipient_id: int,
    author_id: int = 111,
    me_id: int | None = None,
):
    channel_type = discord.ChannelType.private if private else discord.ChannelType.text
    channel = SimpleNamespace(type=channel_type, recipient=SimpleNamespace(id=recipient_id))
    if me_id is not None:
        channel.me = SimpleNamespace(id=me_id)
    author = SimpleNamespace(id=author_id, bot=author_bot)
    return SimpleNamespace(content=content, channel=channel, author=author)


def test_schema_includes_task_77_profile_columns():
    root = Path(__file__).resolve().parents[1] / "database"
    schema_pg = (root / "schema_pg.sql").read_text(encoding="utf-8").lower()
    schema_sqlite = (root / "schema.sql").read_text(encoding="utf-8").lower()

    for column in (
        "onboarding_stop_0_started_at",
        "study_hours_per_week",
        "confidence_level",
    ):
        assert column in schema_pg
        assert column in schema_sqlite


def test_is_continue_signal_enforces_three_layer_guard_and_expected_student():
    bot_user = SimpleNamespace(id=999)

    # Realistic DM shape in discord.py: recipient=student, me=bot
    good = _message(
        "continue",
        private=True,
        author_bot=False,
        recipient_id=111,
        author_id=111,
        me_id=999,
    )
    assert is_continue_signal(good, bot_user, expected_discord_id="111") is True

    not_dm = _message(
        "continue", private=False, author_bot=False, recipient_id=111, author_id=111, me_id=999
    )
    assert is_continue_signal(not_dm, bot_user, expected_discord_id="111") is False

    from_bot = _message(
        "continue", private=True, author_bot=True, recipient_id=111, author_id=111, me_id=999
    )
    assert is_continue_signal(from_bot, bot_user, expected_discord_id="111") is False

    wrong_me = _message(
        "continue", private=True, author_bot=False, recipient_id=111, author_id=111, me_id=123
    )
    assert is_continue_signal(wrong_me, bot_user, expected_discord_id="111") is False

    # Fallback path for mocks that do not expose channel.me.
    wrong_recipient = _message(
        "continue", private=True, author_bot=False, recipient_id=123, author_id=111, me_id=None
    )
    assert is_continue_signal(wrong_recipient, bot_user, expected_discord_id="111") is False

    wrong_student = _message(
        "continue", private=True, author_bot=False, recipient_id=111, author_id=222, me_id=999
    )
    assert is_continue_signal(wrong_student, bot_user, expected_discord_id="111") is False


def test_parse_stop0_profile_answers_flags_unparsed_inputs_non_blocking():
    profile, flags = parse_stop0_profile_answers(
        [
            "satellite terminal",
            "whenever I can",
            "high confidence",
            "Sunday mornings and late evenings",
        ]
    )

    assert profile["primary_device_context"] == DEFAULT_STOP0_PROFILE["primary_device_context"]
    assert profile["study_hours_per_week"] == DEFAULT_STOP0_PROFILE["study_hours_per_week"]
    assert profile["family_obligations_hint"] == "Sunday mornings and late evenings"
    assert len(flags) >= 2
    assert any(flag["question"] == "q1_primary_device_context" for flag in flags)
    assert any(flag["question"] == "q2_study_hours_per_week" for flag in flags)


def test_store_queries_reentry_and_stop0_timeout_candidates(tmp_path):
    store = StudentStateStore(str(tmp_path / "task77.db"))
    store.create_student("111")
    store.create_student("222")
    store.create_student("333")

    old_ts = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
    fresh_ts = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    stop0_old = (datetime.now(timezone.utc) - timedelta(hours=49)).isoformat()

    store.conn.execute(
        "UPDATE students SET onboarding_stop = 2, last_interaction = ? WHERE discord_id = ?",
        (old_ts, "111"),
    )
    store.conn.execute(
        "UPDATE students SET onboarding_stop = 2, last_interaction = ? WHERE discord_id = ?",
        (fresh_ts, "222"),
    )
    store.conn.execute(
        """
        UPDATE students
           SET onboarding_stop = 4,
               onboarding_stop_0_complete = FALSE,
               onboarding_stop_0_started_at = ?
         WHERE discord_id = ?
        """,
        (stop0_old, "333"),
    )
    store.conn.commit()

    reentry_ids = {row["discord_id"] for row in store.get_students_pending_onboarding_reentry(7)}
    assert "111" in reentry_ids
    assert "222" not in reentry_ids

    timeout_ids = {row["discord_id"] for row in store.get_stop_0_timeout_candidates(48)}
    assert timeout_ids == {"333"}

    store.apply_stop_0_timeout_defaults(
        discord_id="333",
        primary_device_context=str(DEFAULT_STOP0_PROFILE["primary_device_context"]),
        study_hours_per_week=int(DEFAULT_STOP0_PROFILE["study_hours_per_week"]),
        confidence_level=int(DEFAULT_STOP0_PROFILE["confidence_level"]),
        family_obligations_hint=str(DEFAULT_STOP0_PROFILE["family_obligations_hint"]),
    )
    row = store.get_student("333")
    assert row["onboarding_stop_0_complete"] in (1, True)
    assert row["profile_complete"] in (0, False)

    store.close()


@pytest.mark.asyncio
async def test_scheduler_onboarding_timeout_check_runs_reentry_and_defaults():
    bot = MagicMock()
    bot.get_guild = MagicMock(return_value=MagicMock())
    bot.fetch_user = AsyncMock()

    user_111 = MagicMock()
    user_111.send = AsyncMock()
    user_333 = MagicMock()
    user_333.send = AsyncMock()

    async def _fetch_user(user_id: int):
        if user_id == 111:
            return user_111
        if user_id == 333:
            return user_333
        raise ValueError("unexpected id")

    bot.fetch_user.side_effect = _fetch_user

    store = MagicMock()
    store.get_stop_0_timeout_candidates.return_value = [{"discord_id": "333"}]
    store.get_students_pending_onboarding_reentry.return_value = [
        {
            "discord_id": "111",
            "onboarding_stop": 2,
            "enrollment_name": "Alice Achieng",
        }
    ]

    with patch("scheduler.scheduler.DailyPromptLibrary"):
        scheduler = DailyPromptScheduler(
            bot=bot,
            guild_id=123,
            channel_mapping={},
            cohort_start_date="2026-02-01",
            store=store,
        )

    await scheduler.onboarding_timeout_check()

    store.apply_stop_0_timeout_defaults.assert_called_once()
    assert user_111.send.await_count == 1
    assert user_333.send.await_count == 1
    assert scheduler._onboarding_timeout_check_today is True
