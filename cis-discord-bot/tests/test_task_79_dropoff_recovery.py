"""
Task 7.9 tests: Stage 1->2 drop-off recovery emails.

Covers:
  - 48h nudge (Email #1.5) dispatch and Column V marker update
  - day-5 nudge (Email #1.75) dispatch from prior 1.5 marker
  - stop condition when Discord join already exists
  - WhatsApp fallback path on immediate bounce-like email failure
  - scheduler worker delegation and nightly 23:20 cadence
"""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cis_controller import interest_api_server as api
from scheduler.daily_prompts import WeekDay
from scheduler.scheduler import DailyPromptScheduler


def _iso_utc(delta: timedelta) -> str:
    return (datetime.now(api.timezone.utc) - delta).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _build_row(*, age: timedelta, marker: str = "", discord_identity: str = "", phone: str = "+254700000000") -> list[str]:
    row = [""] * (api.COL_STAGE1_NUDGE_EMAIL_SENT + 1)
    row[api.COL_NAME] = "Amina"
    row[api.COL_EMAIL] = "amina@example.com"
    row[api.COL_PHONE] = phone
    row[api.COL_DISCORD_ID] = discord_identity
    row[api.COL_CREATED_AT] = _iso_utc(age)
    row[api.COL_INVITE] = "abcInvite"
    row[api.COL_STAGE1_NUDGE_EMAIL_SENT] = marker
    return row


@pytest.mark.asyncio
async def test_check_stage1_dropoff_sends_email_1_5_and_updates_marker(monkeypatch):
    header = ["h"] * (api.COL_STAGE1_NUDGE_EMAIL_SENT + 1)
    row = _build_row(age=timedelta(hours=49))

    send_mock = AsyncMock(return_value={"success": True, "status_code": 201, "error": ""})
    update_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(api, "read_roster_rows", AsyncMock(return_value=[header, row]))
    monkeypatch.setattr(api, "send_stage1_dropoff_email", send_mock)
    monkeypatch.setattr(api, "update_roster_cells", update_mock)

    stats = await api.check_stage1_dropoff(spreadsheet_id="sheet-1")

    assert stats["email_1_5_sent"] == 1
    assert stats["email_1_75_sent"] == 0
    assert send_mock.await_count == 1
    assert send_mock.await_args.kwargs["stage"] == api.STAGE1_NUDGE_48H
    assert update_mock.await_args.kwargs["updates"] == {
        api.COL_STAGE1_NUDGE_EMAIL_SENT: api.STAGE1_NUDGE_48H
    }


@pytest.mark.asyncio
async def test_check_stage1_dropoff_sends_email_1_75_after_day_5(monkeypatch):
    header = ["h"] * (api.COL_STAGE1_NUDGE_EMAIL_SENT + 1)
    row = _build_row(age=timedelta(days=6), marker=api.STAGE1_NUDGE_48H)

    send_mock = AsyncMock(return_value={"success": True, "status_code": 201, "error": ""})
    update_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(api, "read_roster_rows", AsyncMock(return_value=[header, row]))
    monkeypatch.setattr(api, "send_stage1_dropoff_email", send_mock)
    monkeypatch.setattr(api, "update_roster_cells", update_mock)

    stats = await api.check_stage1_dropoff(spreadsheet_id="sheet-1")

    assert stats["email_1_75_sent"] == 1
    assert send_mock.await_args.kwargs["stage"] == api.STAGE1_NUDGE_5DAY
    assert update_mock.await_args.kwargs["updates"] == {
        api.COL_STAGE1_NUDGE_EMAIL_SENT: api.STAGE1_NUDGE_5DAY
    }


@pytest.mark.asyncio
async def test_check_stage1_dropoff_skips_students_already_joined(monkeypatch):
    header = ["h"] * (api.COL_STAGE1_NUDGE_EMAIL_SENT + 1)
    row = _build_row(age=timedelta(days=7), discord_identity="123456789|amina#0001")

    send_mock = AsyncMock()
    monkeypatch.setattr(api, "read_roster_rows", AsyncMock(return_value=[header, row]))
    monkeypatch.setattr(api, "send_stage1_dropoff_email", send_mock)

    stats = await api.check_stage1_dropoff(spreadsheet_id="sheet-1")

    assert stats["skipped_joined"] == 1
    assert send_mock.await_count == 0


@pytest.mark.asyncio
async def test_check_stage1_dropoff_uses_whatsapp_fallback_on_bounce(monkeypatch):
    header = ["h"] * (api.COL_STAGE1_NUDGE_EMAIL_SENT + 1)
    row = _build_row(age=timedelta(hours=60), phone="+254711222333")

    send_mock = AsyncMock(return_value={"success": False, "status_code": 400, "error": "hard bounce"})
    wa_mock = AsyncMock(return_value=True)
    update_mock = AsyncMock(return_value=True)
    monkeypatch.setattr(api, "read_roster_rows", AsyncMock(return_value=[header, row]))
    monkeypatch.setattr(api, "send_stage1_dropoff_email", send_mock)
    monkeypatch.setattr(api, "send_stage1_whatsapp_nudge", wa_mock)
    monkeypatch.setattr(api, "update_roster_cells", update_mock)

    stats = await api.check_stage1_dropoff(spreadsheet_id="sheet-1")

    assert stats["email_failures"] == 1
    assert stats["whatsapp_sent"] == 1
    wa_mock.assert_awaited_once()
    assert update_mock.await_args.kwargs["updates"] == {
        api.COL_STAGE1_NUDGE_EMAIL_SENT: api.STAGE1_NUDGE_48H
    }


@pytest.mark.asyncio
async def test_scheduler_post_stage1_dropoff_nudges_delegates(monkeypatch):
    scheduler = object.__new__(DailyPromptScheduler)
    scheduler.bot = MagicMock()
    scheduler._stage1_dropoff_check_today = False

    captured = {}

    async def _fake_worker(**kwargs):
        captured.update(kwargs)
        return {"scanned": 3, "email_1_5_sent": 1}

    with patch("cis_controller.interest_api_server.check_stage1_dropoff", _fake_worker), patch.dict(
        "os.environ", {"GOOGLE_SHEETS_ID": "sheet-123"}, clear=False
    ):
        await scheduler.post_stage1_dropoff_nudges()

    assert captured.get("spreadsheet_id") == "sheet-123"
    assert scheduler._stage1_dropoff_check_today is True


@pytest.mark.asyncio
async def test_scheduler_runs_stage1_dropoff_once_at_2320():
    bot = MagicMock()
    bot.get_guild = MagicMock(return_value=MagicMock())

    with patch("scheduler.scheduler.DailyPromptLibrary"):
        scheduler = DailyPromptScheduler(
            bot=bot,
            guild_id=123456,
            channel_mapping={},
            cohort_start_date="2026-02-01",
            store=MagicMock(),
        )

    scheduler.get_week_day = MagicMock(return_value=(1, WeekDay.MONDAY))

    async def _fake_post_stage1_dropoff_nudges():
        scheduler._stage1_dropoff_check_today = True

    scheduler.post_stage1_dropoff_nudges = AsyncMock(side_effect=_fake_post_stage1_dropoff_nudges)

    with patch("scheduler.scheduler.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(
            2026, 3, 5, 23, 20, tzinfo=scheduler.cohort_start_date.tzinfo
        )
        await scheduler.check_and_post()
        await scheduler.check_and_post()
        assert scheduler.post_stage1_dropoff_nudges.await_count == 1

        mock_datetime.now.return_value = datetime(
            2026, 3, 6, 23, 20, tzinfo=scheduler.cohort_start_date.tzinfo
        )
        await scheduler.check_and_post()

    assert scheduler.post_stage1_dropoff_nudges.await_count == 2
