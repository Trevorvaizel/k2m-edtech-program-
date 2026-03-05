import json
from datetime import datetime, timedelta, timezone

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
    request = _Request({"token": "token-1", "mpesa_code": "abc12345"})
    response = await server._handle_mpesa_submit(request)
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["success"] is True
    assert captured_updates[api.COL_MPESA_CODE] == "ABC12345"
    assert captured_updates[api.COL_PAYMENT] == "Pending"
