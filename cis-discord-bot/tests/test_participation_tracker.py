"""
Unit tests for participation tracker reaction behavior.
"""

import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cis_controller.participation_tracker import EAT, ParticipationTracker, WITNESS_EMOJI
from database.store import StudentStateStore


def _build_tracker(bot=None, store=None):
    return ParticipationTracker(
        bot=bot or Mock(),
        store=store or Mock(),
        weekly_channel_ids=[101],
        cohort_start_date="2026-02-20",
    )


def _build_message(channel_id: int = 101, message_id: int = 9001):
    message = Mock()
    message.id = message_id
    message.guild = Mock()
    message.channel = Mock()
    message.channel.id = channel_id
    message.author = Mock()
    message.author.bot = False
    message.author.id = 12345
    message.content = "I just realized I use AI when recommendations appear."
    return message


@pytest.mark.asyncio
async def test_on_message_reacts_immediately_for_single_post():
    tracker = _build_tracker()
    message = _build_message()
    message.add_reaction = AsyncMock()

    with patch.object(tracker, "_track_participation", new_callable=AsyncMock) as mock_track:
        await tracker.on_message(message)

    message.add_reaction.assert_awaited_once_with(WITNESS_EMOJI)
    mock_track.assert_awaited_once_with(message)
    assert tracker._reaction_queue == []


@pytest.mark.asyncio
async def test_on_message_queues_retry_when_immediate_reaction_fails():
    bot = Mock()
    tracker = _build_tracker(bot=bot)
    message = _build_message(channel_id=101, message_id=9002)
    message.add_reaction = AsyncMock(side_effect=RuntimeError("transient failure"))

    fetched_message = Mock()
    fetched_message.add_reaction = AsyncMock()
    channel = Mock()
    channel.fetch_message = AsyncMock(return_value=fetched_message)
    bot.get_channel = Mock(return_value=channel)

    with patch.object(tracker, "_track_participation", new_callable=AsyncMock):
        await tracker.on_message(message)

    assert tracker._reaction_queue == [(9002, 101)]

    await tracker._process_reaction_queue()

    fetched_message.add_reaction.assert_awaited_once_with(WITNESS_EMOJI)
    assert tracker._reaction_queue == []


def test_tracker_uses_provided_cohort_start_date():
    tracker = _build_tracker()
    assert tracker.cohort_start.strftime("%Y-%m-%d") == "2026-02-20"


@pytest.mark.asyncio
async def test_check_inactive_students_handles_current_students_schema(tmp_path):
    """
    Regression: students table has no `username` column.
    Inactive nudge scan should still run and upsert participation rows.
    """
    db_path = tmp_path / "participation_tracker_schema.db"
    store = StudentStateStore(str(db_path))
    store.create_student("111111")

    tracker = _build_tracker(bot=Mock(), store=store)
    tracker._send_nudge_dm = AsyncMock()

    with patch("cis_controller.participation_tracker.datetime") as mock_datetime:
        mock_datetime.now.return_value = EAT.localize(datetime(2026, 2, 20, 18, 0))
        await tracker.check_inactive_students(week=1)

    tracker._send_nudge_dm.assert_awaited_once_with("111111", 1)
    row = store.conn.execute(
        """
        SELECT nudge_sent
        FROM daily_participation
        WHERE discord_id = ? AND date = ?
        """,
        ("111111", "2026-02-20"),
    ).fetchone()
    assert row is not None
    assert row["nudge_sent"] == 1

    store.close()
