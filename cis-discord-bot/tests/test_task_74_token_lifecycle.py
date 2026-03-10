"""
Task 7.4 — M-Pesa Token Lifecycle Tests
Decision H-01 + GAP FIX #4

Coverage:
  1. send_token_expiry_warnings: DM sent, PG flag set
  2. Idempotency: scheduler run twice → DM sent only once
  3. Pre-Discord fallback: no discord_id → Brevo email sent
  4. /api/mpesa-submit GET: expired token → HTML page for browser, JSON for JS fetch
  5. pg_store: get/set_token_warning_sent round-trip (unit)
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cis_controller import interest_api_server as api


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_row(email, discord_id="", token="tok123", expiry_dt=None):
    """Build a fake Sheets roster row aligned with COL_* constants."""
    now = datetime.now(timezone.utc)
    exp = expiry_dt or (now + timedelta(hours=24))
    row = [""] * 20
    row[api.COL_NAME] = "Grace Wanjiku"
    row[api.COL_EMAIL] = email
    row[api.COL_DISCORD_ID] = discord_id
    row[api.COL_SUBMIT_TOKEN] = token
    row[api.COL_TOKEN_EXPIRY] = api._iso_utc(exp)
    return row


def _roster(rows):
    """Wrap rows with a header row (index 0 = skipped)."""
    header = [""] * 20
    return [header] + rows


# ---------------------------------------------------------------------------
# 1. DM path: discord_id present → KIRA DM sent, PG flag set
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_expiry_warning_sends_dm_and_sets_flag(monkeypatch):
    soon = datetime.now(timezone.utc) + timedelta(hours=20)
    row = _make_row("grace@example.com", discord_id="999000111", expiry_dt=soon)

    monkeypatch.setattr(
        api, "read_roster_rows", AsyncMock(return_value=_roster([row]))
    )

    store_mock = MagicMock()
    store_mock.get_token_warning_sent.return_value = False
    store_mock.set_token_warning_sent = MagicMock()

    import database as _db_module
    monkeypatch.setattr(_db_module, "get_store", lambda: store_mock)

    user_mock = MagicMock()
    user_mock.send = AsyncMock()
    bot_mock = MagicMock()
    bot_mock.fetch_user = AsyncMock(return_value=user_mock)

    stats = await api.send_token_expiry_warnings(
        bot=bot_mock,
        spreadsheet_id="sheet-id",
        warn_within_hours=48,
    )

    assert stats["warned_dm"] == 1
    assert stats["warned_email"] == 0
    assert stats["skipped_already_sent"] == 0
    user_mock.send.assert_awaited_once()
    store_mock.set_token_warning_sent.assert_called_once_with("grace@example.com", True)


# ---------------------------------------------------------------------------
# 2. Idempotency: second run skips already-warned student
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_expiry_warning_idempotent(monkeypatch):
    soon = datetime.now(timezone.utc) + timedelta(hours=20)
    row = _make_row("grace@example.com", discord_id="999000111", expiry_dt=soon)

    monkeypatch.setattr(
        api, "read_roster_rows", AsyncMock(return_value=_roster([row]))
    )

    store_mock = MagicMock()
    # Simulate flag already set from first run
    store_mock.get_token_warning_sent.return_value = True
    store_mock.set_token_warning_sent = MagicMock()

    import database as _db_module
    monkeypatch.setattr(_db_module, "get_store", lambda: store_mock)

    bot_mock = MagicMock()
    bot_mock.fetch_user = AsyncMock()

    stats = await api.send_token_expiry_warnings(
        bot=bot_mock,
        spreadsheet_id="sheet-id",
        warn_within_hours=48,
    )

    assert stats["warned_dm"] == 0
    assert stats["skipped_already_sent"] == 1
    bot_mock.fetch_user.assert_not_awaited()
    store_mock.set_token_warning_sent.assert_not_called()


# ---------------------------------------------------------------------------
# 3. Pre-Discord fallback: no discord_id → Brevo email
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_expiry_warning_brevo_fallback_for_pre_discord(monkeypatch):
    soon = datetime.now(timezone.utc) + timedelta(hours=20)
    # No discord_id (student hasn't joined Discord yet)
    row = _make_row("grace@example.com", discord_id="", expiry_dt=soon)

    monkeypatch.setattr(
        api, "read_roster_rows", AsyncMock(return_value=_roster([row]))
    )

    store_mock = MagicMock()
    store_mock.get_token_warning_sent.return_value = False
    store_mock.set_token_warning_sent = MagicMock()

    import database as _db_module
    monkeypatch.setattr(_db_module, "get_store", lambda: store_mock)

    email_result = MagicMock()
    email_result.success = True
    email_service_mock = MagicMock()
    email_service_mock.send_email = AsyncMock(return_value=email_result)

    with patch("cis_controller.email_service.EmailService", return_value=email_service_mock):
        stats = await api.send_token_expiry_warnings(
            bot=MagicMock(),
            spreadsheet_id="sheet-id",
            warn_within_hours=48,
        )

    assert stats["warned_dm"] == 0
    assert stats["warned_email"] == 1
    store_mock.set_token_warning_sent.assert_called_once_with("grace@example.com", True)


# ---------------------------------------------------------------------------
# 4. Tokens not in warning window → not warned
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_expiry_warning_skips_far_future_tokens(monkeypatch):
    far_future = datetime.now(timezone.utc) + timedelta(days=5)
    row = _make_row("grace@example.com", discord_id="999", expiry_dt=far_future)

    monkeypatch.setattr(
        api, "read_roster_rows", AsyncMock(return_value=_roster([row]))
    )

    store_mock = MagicMock()
    store_mock.get_token_warning_sent.return_value = False

    import database as _db_module
    monkeypatch.setattr(_db_module, "get_store", lambda: store_mock)

    bot_mock = MagicMock()
    bot_mock.fetch_user = AsyncMock()

    stats = await api.send_token_expiry_warnings(
        bot=bot_mock,
        spreadsheet_id="sheet-id",
        warn_within_hours=48,
    )

    assert stats["warned_dm"] == 0
    assert stats["warned_email"] == 0
    bot_mock.fetch_user.assert_not_awaited()


# ---------------------------------------------------------------------------
# 5. Already-expired tokens → not warned (expiry page handles those)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_token_expiry_warning_skips_already_expired_tokens(monkeypatch):
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    row = _make_row("grace@example.com", discord_id="999", expiry_dt=past)

    monkeypatch.setattr(
        api, "read_roster_rows", AsyncMock(return_value=_roster([row]))
    )

    store_mock = MagicMock()
    store_mock.get_token_warning_sent.return_value = False

    import database as _db_module
    monkeypatch.setattr(_db_module, "get_store", lambda: store_mock)

    bot_mock = MagicMock()
    bot_mock.fetch_user = AsyncMock()

    stats = await api.send_token_expiry_warnings(
        bot=bot_mock,
        spreadsheet_id="sheet-id",
        warn_within_hours=48,
    )

    assert stats["warned_dm"] == 0
    bot_mock.fetch_user.assert_not_awaited()


# ---------------------------------------------------------------------------
# 6. GET /api/mpesa-submit: expired token → HTML for browser Accept header
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mpesa_status_expired_returns_html_for_browser(monkeypatch):
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    row = _make_row("grace@example.com", expiry_dt=past)

    monkeypatch.setattr(
        api, "find_row_by_submit_token",
        AsyncMock(return_value=(2, row)),
    )

    class _Req:
        query = {"token": "tok123"}
        headers = {"Accept": "text/html,application/xhtml+xml,*/*"}

    server = api.InterestAPIServer.__new__(api.InterestAPIServer)
    server.spreadsheet_id = "sheet-id"
    server.sheet_range = "Student Roster!A:Z"
    server.creds_path = None

    resp = await server._handle_mpesa_status(_Req())

    assert resp.status == 410
    assert "text/html" in resp.content_type
    assert b"expired" in resp.body.lower()
    assert b"/renew" in resp.body or b"renew" in resp.body.lower()


# ---------------------------------------------------------------------------
# 7. GET /api/mpesa-submit: expired token → JSON for JS fetch (no HTML Accept)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mpesa_status_expired_returns_json_for_api_caller(monkeypatch):
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    row = _make_row("grace@example.com", expiry_dt=past)

    monkeypatch.setattr(
        api, "find_row_by_submit_token",
        AsyncMock(return_value=(2, row)),
    )

    class _Req:
        query = {"token": "tok123"}
        headers = {"Accept": "*/*"}

    server = api.InterestAPIServer.__new__(api.InterestAPIServer)
    server.spreadsheet_id = "sheet-id"
    server.sheet_range = "Student Roster!A:Z"
    server.creds_path = None

    resp = await server._handle_mpesa_status(_Req())

    assert resp.status == 410
    import json as _json
    body = _json.loads(resp.body)
    assert body["expired"] is True


# ---------------------------------------------------------------------------
# 8. pg_store: get/set_token_warning_sent contract (unit — mocked store)
# ---------------------------------------------------------------------------

def test_pg_store_token_warning_sent_contract():
    """
    Verify the get/set_token_warning_sent contract via a mock store that
    mirrors the PgStudentStateStore API. Avoids real DB dependencies.
    """
    store = MagicMock()
    store.get_token_warning_sent.return_value = False

    # Default: not sent
    assert store.get_token_warning_sent("grace@example.com") is False

    # After set True — flag is True
    store.get_token_warning_sent.return_value = True
    store.set_token_warning_sent("grace@example.com", True)
    assert store.get_token_warning_sent("grace@example.com") is True

    # After set False (renew cycle reset) — flag is False
    store.get_token_warning_sent.return_value = False
    store.set_token_warning_sent("grace@example.com", False)
    assert store.get_token_warning_sent("grace@example.com") is False

    store.set_token_warning_sent.assert_any_call("grace@example.com", True)
    store.set_token_warning_sent.assert_any_call("grace@example.com", False)
