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
    store_mock.log_observability_event = MagicMock()

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
    store_mock.log_observability_event.assert_called_once()
    _, kwargs = store_mock.log_observability_event.call_args
    assert kwargs["event_type"] == "token_expiry_warning_sent"
    assert kwargs["metadata"]["channel"] == "discord_dm"


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
    store_mock.log_observability_event = MagicMock()

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
    store_mock.log_observability_event.assert_called_once()
    _, kwargs = store_mock.log_observability_event.call_args
    assert kwargs["event_type"] == "token_expiry_warning_sent"
    assert kwargs["metadata"]["channel"] == "brevo_email"


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
# 8. pg_store: get/set_token_warning_sent contract (unit - real methods)
# ---------------------------------------------------------------------------

def test_pg_store_get_token_warning_sent_returns_false_when_missing():
    from database.pg_store import PgStudentStateStore

    class _Cursor:
        def __init__(self, row=None, rowcount=0):
            self._row = row
            self.rowcount = rowcount

        def fetchone(self):
            return self._row

    class _Conn:
        def __init__(self):
            self.last_sql = None
            self.last_params = None

        def execute(self, sql, params=()):
            self.last_sql = sql
            self.last_params = params
            return _Cursor(row=None, rowcount=0)

        def commit(self):
            raise AssertionError("commit should not be called by getter")

    store = PgStudentStateStore.__new__(PgStudentStateStore)
    store.conn = _Conn()

    assert store.get_token_warning_sent("Grace@Example.com") is False
    assert "LOWER(enrollment_email)" in store.conn.last_sql
    assert store.conn.last_params == ("grace@example.com",)


def test_pg_store_set_token_warning_sent_inserts_placeholder_when_missing():
    from database.pg_store import PgStudentStateStore

    class _Cursor:
        def __init__(self, rowcount=0):
            self.rowcount = rowcount

        def fetchone(self):
            return None

    class _Conn:
        def __init__(self):
            self.calls = []
            self.commits = 0
            self._seen_update = 0

        def execute(self, sql, params=()):
            self.calls.append((sql, params))
            if "UPDATE students SET token_warning_sent" in sql:
                self._seen_update += 1
                # First update simulates "row does not exist yet"
                if self._seen_update == 1:
                    return _Cursor(rowcount=0)
                return _Cursor(rowcount=1)
            if "INSERT INTO students" in sql:
                return _Cursor(rowcount=1)
            return _Cursor(rowcount=0)

        def commit(self):
            self.commits += 1

    store = PgStudentStateStore.__new__(PgStudentStateStore)
    store.conn = _Conn()

    store.set_token_warning_sent("Grace@Example.com", True)

    # Update attempted, then placeholder insert, then final update
    assert len(store.conn.calls) == 3
    assert "UPDATE students SET token_warning_sent" in store.conn.calls[0][0]
    assert "INSERT INTO students (discord_id, enrollment_email, token_warning_sent)" in store.conn.calls[1][0]
    assert store.conn.calls[1][1][0] == "__pending__grace@example.com"
    assert store.conn.calls[1][1][1] == "grace@example.com"
    assert store.conn.calls[1][1][2] is True
    assert store.conn.commits == 1
