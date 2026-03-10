import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from cis_controller import interest_api_server as api


class _Request:
    def __init__(self, payload=None, query=None):
        self._payload = payload
        self.query = query or {}

    async def json(self):
        return self._payload or {}


@pytest.mark.asyncio
async def test_append_to_student_roster_writes_canonical_columns(monkeypatch):
    captured = {}

    class _Values:
        def append(self, **kwargs):
            captured.update(kwargs)
            return self

        def execute(self):
            return {}

    class _Spreadsheets:
        def values(self):
            return _Values()

    class _Service:
        def spreadsheets(self):
            return _Spreadsheets()

    monkeypatch.setattr(api, "_build_sheets_service", lambda **_kwargs: _Service())

    ok = await api.append_to_student_roster(
        name="Test Student",
        email="student@example.com",
        phone="+254700000000",
        profession="Professional",
        invite_code="abc123",
        waitlisted=False,
        spreadsheet_id="sheet-123",
        sheet_range="Student Roster!A:Z",
    )

    assert ok is True
    row = captured["body"]["values"][0]
    assert len(row) == 18
    assert row[api.COL_EMAIL] == "student@example.com"
    assert row[api.COL_PAYMENT] == "Lead"
    assert row[api.COL_INVITE] == "abc123"


@pytest.mark.asyncio
async def test_interest_endpoint_returns_500_when_sheet_append_fails(monkeypatch):
    async def _not_duplicate(**_kwargs):
        return False

    async def _cap(**_kwargs):
        return {"paid_count": 0, "cap": 30, "available": 30}

    async def _invite():
        return {"code": "abc123", "url": "https://discord.gg/abc123"}

    async def _append(**_kwargs):
        return False

    async def _email(**_kwargs):
        pytest.fail("email should not be sent when append fails")

    monkeypatch.setattr(api, "check_duplicate_email", _not_duplicate)
    monkeypatch.setattr(api, "check_enrollment_cap", _cap)
    monkeypatch.setattr(api, "create_discord_invite_link", _invite)
    monkeypatch.setattr(api, "append_to_student_roster", _append)
    monkeypatch.setattr(api, "send_brevo_email", _email)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request(
        {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+254700000000",
            "profession": "Professional",
        }
    )

    response = await server._handle_interest(request)
    payload = json.loads(response.text)

    assert response.status == 500
    assert payload["success"] is False


@pytest.mark.asyncio
async def test_interest_endpoint_returns_502_when_email_fails(monkeypatch):
    async def _not_duplicate(**_kwargs):
        return False

    async def _cap(**_kwargs):
        return {"paid_count": 0, "cap": 30, "available": 30}

    async def _invite():
        return {"code": "abc123", "url": "https://discord.gg/abc123"}

    async def _append(**_kwargs):
        return True

    async def _email(**_kwargs):
        return False

    monkeypatch.setattr(api, "check_duplicate_email", _not_duplicate)
    monkeypatch.setattr(api, "check_enrollment_cap", _cap)
    monkeypatch.setattr(api, "create_discord_invite_link", _invite)
    monkeypatch.setattr(api, "append_to_student_roster", _append)
    monkeypatch.setattr(api, "send_brevo_email", _email)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request(
        {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+254700000000",
            "profession": "Professional",
        }
    )

    response = await server._handle_interest(request)
    payload = json.loads(response.text)

    assert response.status == 502
    assert payload["success"] is False


@pytest.mark.asyncio
async def test_interest_endpoint_waitlists_when_cap_reached(monkeypatch):
    async def _not_duplicate(**_kwargs):
        return False

    async def _cap(**_kwargs):
        return {"paid_count": 30, "cap": 30, "available": 0}

    async def _invite():
        pytest.fail("invite should not be created for waitlisted leads")

    captured = {"waitlisted": None}

    async def _append(**kwargs):
        captured["waitlisted"] = kwargs["waitlisted"]
        return True

    async def _email(**_kwargs):
        return True

    monkeypatch.setattr(api, "check_duplicate_email", _not_duplicate)
    monkeypatch.setattr(api, "check_enrollment_cap", _cap)
    monkeypatch.setattr(api, "create_discord_invite_link", _invite)
    monkeypatch.setattr(api, "append_to_student_roster", _append)
    monkeypatch.setattr(api, "send_brevo_email", _email)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request(
        {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+254700000000",
            "profession": "Professional",
        }
    )

    response = await server._handle_interest(request)
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["success"] is True
    assert payload["waitlisted"] is True
    assert captured["waitlisted"] is True


@pytest.mark.asyncio
async def test_interest_endpoint_success_message_includes_step_marker(monkeypatch):
    async def _not_duplicate(**_kwargs):
        return False

    async def _cap(**_kwargs):
        return {"paid_count": 0, "cap": 30, "available": 30}

    async def _invite():
        return {"code": "abc123", "url": "https://discord.gg/abc123"}

    async def _append(**_kwargs):
        return True

    async def _email(**_kwargs):
        return True

    monkeypatch.setattr(api, "check_duplicate_email", _not_duplicate)
    monkeypatch.setattr(api, "check_enrollment_cap", _cap)
    monkeypatch.setattr(api, "create_discord_invite_link", _invite)
    monkeypatch.setattr(api, "append_to_student_roster", _append)
    monkeypatch.setattr(api, "send_brevo_email", _email)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request(
        {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+254700000000",
            "profession": "Professional",
        }
    )

    response = await server._handle_interest(request)
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["success"] is True
    assert "Step 1 of 4 complete" in payload["message"]


@pytest.mark.asyncio
async def test_enroll_endpoint_returns_submit_url_on_success(monkeypatch):
    row = ["Test Student", "test@example.com", "+254700000000"] + [""] * 15
    captured_updates = {}

    async def _find_row(**_kwargs):
        return 2, row

    async def _update_row(**kwargs):
        captured_updates.update(kwargs["updates"])
        return True

    async def _send_email(**_kwargs):
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find_row)
    monkeypatch.setattr(api, "update_roster_cells", _update_row)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _send_email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok123")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda token: f"https://k2m.edtech/mpesa-submit?token={token}")

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request(
        {
            "email": "test@example.com",
            "zone": "2",
            "situation": "University student",
            "goals": "Build AI skills",
            "emotional_baseline": "Curious",
            "parent_email": "parent@example.com",
        }
    )
    response = await server._handle_enroll(request)
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["success"] is True
    assert "Step 3 of 4" in payload["message"]
    assert payload["submit_url"] == "https://k2m.edtech/mpesa-submit?token=tok123"
    assert captured_updates[api.COL_SUBMIT_TOKEN] == "tok123"
    assert captured_updates[api.COL_PAYMENT] == "Enrolled"


@pytest.mark.asyncio
async def test_enroll_endpoint_returns_404_when_email_not_found(monkeypatch):
    async def _find_row(**_kwargs):
        return None

    monkeypatch.setattr(api, "find_row_by_email", _find_row)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request(
        {
            "email": "missing@example.com",
            "zone": "2",
            "situation": "University student",
            "goals": "Build AI skills",
            "emotional_baseline": "Curious",
        }
    )
    response = await server._handle_enroll(request)
    payload = json.loads(response.text)

    assert response.status == 404
    assert payload["success"] is False


@pytest.mark.asyncio
async def test_mpesa_submit_returns_410_when_token_expired(monkeypatch):
    expired = (datetime.now(timezone.utc) - timedelta(days=1)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    row = [""] * 18
    row[api.COL_NAME] = "Test Student"
    row[api.COL_EMAIL] = "test@example.com"
    row[api.COL_SUBMIT_TOKEN] = "token-1"
    row[api.COL_TOKEN_EXPIRY] = expired
    row[api.COL_INVITE] = "invite"

    async def _find_row(**_kwargs):
        return 2, row

    monkeypatch.setattr(api, "find_row_by_submit_token", _find_row)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request({"token": "token-1", "mpesa_code": "TESTTEST01"})
    response = await server._handle_mpesa_submit(request)
    payload = json.loads(response.text)

    assert response.status == 410
    assert payload["success"] is False
    assert payload["expired"] is True


@pytest.mark.asyncio
async def test_mpesa_submit_updates_pending_and_returns_success(monkeypatch):
    future = (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    row = [""] * 18
    row[api.COL_NAME] = "Test Student"
    row[api.COL_EMAIL] = "test@example.com"
    row[api.COL_SUBMIT_TOKEN] = "token-1"
    row[api.COL_TOKEN_EXPIRY] = future
    row[api.COL_INVITE] = "invite"
    captured_updates = {}

    async def _find_row(**_kwargs):
        return 2, row

    async def _update_row(**kwargs):
        captured_updates.update(kwargs["updates"])
        return True

    async def _send_email(**_kwargs):
        return True

    monkeypatch.setattr(api, "find_row_by_submit_token", _find_row)
    monkeypatch.setattr(api, "update_roster_cells", _update_row)
    monkeypatch.setattr(api, "send_mpesa_received_email", _send_email)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request({"token": "token-1", "mpesa_code": "qgj8yoat3t"})
    response = await server._handle_mpesa_submit(request)
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["success"] is True
    assert captured_updates[api.COL_MPESA_CODE] == "QGJ8YOAT3T"
    assert captured_updates[api.COL_PAYMENT] == "Pending"


@pytest.mark.asyncio
async def test_mpesa_submit_rejects_invalid_code_format(monkeypatch):
    async def _find_row(**_kwargs):
        pytest.fail("Token lookup should not run when mpesa_code format is invalid")

    monkeypatch.setattr(api, "find_row_by_submit_token", _find_row)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request({"token": "token-1", "mpesa_code": "ABC123"})
    response = await server._handle_mpesa_submit(request)
    payload = json.loads(response.text)

    assert response.status == 400
    assert payload["success"] is False
    assert "10 characters" in payload["error"]


@pytest.mark.asyncio
async def test_enroll_endpoint_queues_email_when_discord_not_linked(monkeypatch):
    row = ["Test Student", "test@example.com", "+254700000000"] + [""] * 18
    captured_queue = {}

    async def _find_row(**_kwargs):
        return 2, row

    async def _update_row(**_kwargs):
        return True

    async def _await_discord(**_kwargs):
        return ""

    async def _send_email(**_kwargs):
        pytest.fail("Email #2 should be queued when discord_id is still missing")

    def _queue_email(**kwargs):
        captured_queue.update(kwargs)
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find_row)
    monkeypatch.setattr(api, "update_roster_cells", _update_row)
    monkeypatch.setattr(api, "wait_for_linked_discord_id", _await_discord)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _send_email)
    monkeypatch.setattr(api, "queue_enrollment_payment_email", _queue_email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok123")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda token: f"https://k2m.edtech/mpesa-submit?token={token}")

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request(
        {
            "email": "test@example.com",
            "zone": "2",
            "situation": "University student",
            "goals": "Build AI skills",
            "emotional_baseline": "Curious",
        }
    )
    response = await server._handle_enroll(request)
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["success"] is True
    assert "Step 3 of 4" in payload["message"]
    assert "detected" in payload["message"].lower()
    assert captured_queue["to_email"] == "test@example.com"


@pytest.mark.asyncio
async def test_enroll_endpoint_sends_email_when_discord_links_after_retry(monkeypatch):
    row = ["Test Student", "test@example.com", "+254700000000"] + [""] * 18
    captured_email = {}

    async def _find_row(**_kwargs):
        return 2, row

    async def _update_row(**_kwargs):
        return True

    async def _await_discord(**_kwargs):
        return "123456789"

    async def _send_email(**kwargs):
        captured_email.update(kwargs)
        return True

    def _queue_email(**_kwargs):
        pytest.fail("Queue should not be used when discord_id appears during retries")

    monkeypatch.setattr(api, "find_row_by_email", _find_row)
    monkeypatch.setattr(api, "update_roster_cells", _update_row)
    monkeypatch.setattr(api, "wait_for_linked_discord_id", _await_discord)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _send_email)
    monkeypatch.setattr(api, "queue_enrollment_payment_email", _queue_email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok123")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda token: f"https://k2m.edtech/mpesa-submit?token={token}")

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")
    request = _Request(
        {
            "email": "test@example.com",
            "zone": "2",
            "situation": "University student",
            "goals": "Build AI skills",
            "emotional_baseline": "Curious",
        }
    )
    response = await server._handle_enroll(request)
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["success"] is True
    assert "Step 3 of 4" in payload["message"]
    assert captured_email["discord_id"] == "123456789"


@pytest.mark.asyncio
async def test_enroll_endpoint_sends_post_enroll_dm_with_inline_submit_url(monkeypatch):
    row = ["Test Student", "test@example.com", "+254700000000"] + [""] * 18
    row[api.COL_DISCORD_ID] = "123456789|test_user"
    dm_user = AsyncMock()
    dm_user.send = AsyncMock()
    bot = AsyncMock()
    bot.fetch_user = AsyncMock(return_value=dm_user)

    async def _find_row(**_kwargs):
        return 2, row

    async def _update_row(**_kwargs):
        return True

    async def _send_email(**_kwargs):
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find_row)
    monkeypatch.setattr(api, "update_roster_cells", _update_row)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _send_email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok123")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda token: f"https://k2m.edtech/mpesa-submit?token={token}")

    tasks = []
    original_create_task = asyncio.create_task

    def _capture_task(coro):
        task = original_create_task(coro)
        tasks.append(task)
        return task

    monkeypatch.setattr(asyncio, "create_task", _capture_task)

    server = api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds", bot=bot)
    request = _Request(
        {
            "email": "test@example.com",
            "zone": "2",
            "situation": "University student",
            "goals": "Build AI skills",
            "emotional_baseline": "Curious",
        }
    )
    response = await server._handle_enroll(request)
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["success"] is True
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    bot.fetch_user.assert_awaited_once_with(123456789)
    dm_user.send.assert_awaited_once()
    dm_text = dm_user.send.call_args.args[0]
    assert "Step 3 of 4" in dm_text
    assert "https://k2m.edtech/mpesa-submit?token=tok123" in dm_text


@pytest.mark.asyncio
async def test_process_pending_enrollment_payment_emails_drains_queue_when_linked(monkeypatch, tmp_path):
    queue_file = tmp_path / "enroll-email-queue.json"
    monkeypatch.setattr(api, "ENROLL_EMAIL_QUEUE_PATH", Path(queue_file))
    assert api.queue_enrollment_payment_email(
        to_email="queued@example.com",
        first_name="Queued",
        submit_url="https://k2m.edtech/mpesa-submit?token=tok123",
    )

    async def _find_row(**_kwargs):
        row = ["Queued", "queued@example.com", "+254700000000"] + [""] * 18
        row[api.COL_DISCORD_ID] = "123456789|queued#0001"
        return 2, row

    async def _send_email(**_kwargs):
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find_row)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _send_email)

    stats = await api.process_pending_enrollment_payment_emails(
        spreadsheet_id="sheet-123",
        sheet_range="Student Roster!A:Z",
        creds_path="creds",
    )

    assert stats["queued"] == 1
    assert stats["sent"] == 1
    assert stats["deferred"] == 0


@pytest.mark.asyncio
async def test_send_48h_enroll_nudges_targets_linked_unenrolled_students(monkeypatch):
    old_ts = (datetime.now(timezone.utc) - timedelta(hours=49)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    recent_ts = (datetime.now(timezone.utc) - timedelta(hours=12)).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    header = ["Name", "Email", "Phone", "Discord", "Profession", "Zone", "Situation", "Goals", "Emotional", "Parent", "Mpesa", "Payment", "Notes", "Created At", "Activated", "Token", "Expiry", "Invite", "S", "T", "U"]
    due_row = ["Alice", "alice@example.com", "+254700", "123456789|alice#0001", "Teacher", "", "", "", "", "", "", "Lead", "", old_ts, "", "", "", "INVITE1", "", "", ""]
    recent_row = ["Bob", "bob@example.com", "+254701", "987654321|bob#0001", "Teacher", "", "", "", "", "", "", "Lead", "", recent_ts, "", "", "", "INVITE2", "", "", ""]
    already_nudged_row = ["Carol", "carol@example.com", "+254702", "555555555|carol#0001", "Teacher", "", "", "", "", "", "", "Lead", f"{api.ENROLL_NUDGE_SENT_NOTE_KEY}={old_ts}", old_ts, "", "", "", "INVITE3", "", "", ""]
    completed_row = ["Dan", "dan@example.com", "+254703", "444444444|dan#0001", "Teacher", "Zone 1", "S", "G", "Curious", "", "", "Enrolled", "", old_ts, "", "", "", "INVITE4", "", "", ""]

    async def _read_rows(**_kwargs):
        return [header, due_row, recent_row, already_nudged_row, completed_row]

    captured_updates = []

    async def _update_row(**kwargs):
        captured_updates.append(kwargs)
        return True

    dm_user = AsyncMock()
    dm_user.send = AsyncMock()
    bot = AsyncMock()
    bot.fetch_user = AsyncMock(return_value=dm_user)

    monkeypatch.setattr(api, "read_roster_rows", _read_rows)
    monkeypatch.setattr(api, "update_roster_cells", _update_row)

    stats = await api.send_48h_enroll_nudges(
        bot=bot,
        spreadsheet_id="sheet-123",
        sheet_range="Student Roster!A:Z",
        creds_path="creds",
        age_hours=48,
    )

    assert stats["nudged"] == 1
    bot.fetch_user.assert_awaited_once_with(123456789)
    dm_user.send.assert_awaited_once()
    assert len(captured_updates) == 1
    assert api.COL_NOTES in captured_updates[0]["updates"]
