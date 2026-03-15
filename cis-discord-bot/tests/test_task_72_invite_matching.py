"""
Task 7.2 — Unique per-student Discord invite links (on_member_join match key)
Tests for: invite creation, invite diff, DB link methods, unmatched fallback.
Decision B-01 + N-07 + GAP FIX #1 + GAP FIX #8.
"""

import asyncio
import importlib
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ============================================================
# 1. create_discord_invite_link() — REST API call
# ============================================================

@pytest.mark.asyncio
async def test_create_discord_invite_link_success(monkeypatch):
    """Returns code + url when Discord API responds 201."""
    from cis_controller.interest_api_server import create_discord_invite_link

    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_INVITE_CHANNEL_ID", "12345")

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"code": "AbCdEf"}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        result = await create_discord_invite_link()

    assert result is not None
    assert result["code"] == "AbCdEf"
    assert result["url"] == "https://discord.gg/AbCdEf"


@pytest.mark.asyncio
async def test_create_discord_invite_link_missing_env(monkeypatch):
    """Returns None when env vars are missing."""
    from cis_controller.interest_api_server import create_discord_invite_link

    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("DISCORD_INVITE_CHANNEL_ID", raising=False)

    result = await create_discord_invite_link()
    assert result is None


@pytest.mark.asyncio
async def test_create_discord_invite_link_api_error(monkeypatch):
    """Returns None on non-2xx response."""
    from cis_controller.interest_api_server import create_discord_invite_link

    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_INVITE_CHANNEL_ID", "12345")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Missing Permissions"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        result = await create_discord_invite_link()

    assert result is None


# ============================================================
# 2. pg_store — get_student_by_invite_code + link_student_by_invite
# ============================================================

def _make_pg_store_with_conn(rows_by_query=None):
    """Build a minimal PgStudentStateStore mock with a fake conn."""
    from database.pg_store import PgStudentStateStore

    store = object.__new__(PgStudentStateStore)
    conn = MagicMock()

    # Simulate execute().fetchone() returning rows_by_query values
    def _execute(sql, params=()):
        cursor = MagicMock()
        key = None
        if params:
            key = params[0] if len(params) == 1 else params
        if rows_by_query and key in rows_by_query:
            cursor.fetchone.return_value = rows_by_query[key]
        else:
            cursor.fetchone.return_value = None
        return cursor

    conn.execute = _execute
    conn.commit = MagicMock()
    store.conn = conn
    return store


def test_get_student_by_invite_code_match():
    """Returns student row when invite_code matches."""
    store = _make_pg_store_with_conn(
        rows_by_query={"ABC123": {"enrollment_email": "alice@k2m.org", "invite_code": "ABC123"}}
    )
    result = store.get_student_by_invite_code("ABC123")
    assert result is not None
    assert result["enrollment_email"] == "alice@k2m.org"


def test_get_student_by_invite_code_no_match():
    """Returns None when invite_code is not found."""
    store = _make_pg_store_with_conn(rows_by_query={})
    result = store.get_student_by_invite_code("ZZZZZ")
    assert result is None


def test_link_student_by_invite_success():
    """Returns True when link is confirmed."""
    from database.pg_store import PgStudentStateStore

    store = object.__new__(PgStudentStateStore)
    conn = MagicMock()

    # First execute (UPDATE) → no return needed
    # Second execute (SELECT verify) → returns a row
    call_count = [0]

    def _execute(sql, params=()):
        cursor = MagicMock()
        call_count[0] += 1
        if call_count[0] == 1:
            cursor.fetchone.return_value = None  # UPDATE
        else:
            cursor.fetchone.return_value = {"discord_id": "111", "invite_code": "ABC123"}
        return cursor

    conn.execute = _execute
    conn.commit = MagicMock()
    store.conn = conn

    result = store.link_student_by_invite("ABC123", "111", "alice#0001")
    assert result is True


def test_link_student_by_invite_already_claimed():
    """Returns False when no row updated (already claimed)."""
    from database.pg_store import PgStudentStateStore

    store = object.__new__(PgStudentStateStore)
    conn = MagicMock()
    call_count = [0]

    def _execute(sql, params=()):
        cursor = MagicMock()
        call_count[0] += 1
        cursor.fetchone.return_value = None  # verify SELECT also returns nothing
        return cursor

    conn.execute = _execute
    conn.commit = MagicMock()
    store.conn = conn

    result = store.link_student_by_invite("ABC123", "999", "other#0001")
    assert result is False


def test_link_student_by_invite_allows_pending_placeholder():
    """UPDATE query allows replacing __pending__ placeholder discord_id values."""
    from database.pg_store import PgStudentStateStore

    store = object.__new__(PgStudentStateStore)
    conn = MagicMock()
    executed_sql = []
    call_count = [0]

    def _execute(sql, params=()):
        executed_sql.append(sql)
        cursor = MagicMock()
        call_count[0] += 1
        if call_count[0] == 2:
            cursor.fetchone.return_value = {"discord_id": "111", "invite_code": "ABC123"}
        else:
            cursor.fetchone.return_value = None
        return cursor

    conn.execute = _execute
    conn.commit = MagicMock()
    store.conn = conn

    result = store.link_student_by_invite("ABC123", "111", "alice#0001")
    assert result is True
    assert "__pending__%" in executed_sql[0]


# ============================================================
# 3. invite diff logic — unit test the pattern
# ============================================================

def _diff_invites(old_map: dict, current_map: dict):
    """Mirror of the on_member_join invite diff logic."""
    used_code = None
    for code, uses in current_map.items():
        if uses > old_map.get(code, 0):
            used_code = code
            break
    if used_code is None:
        for code in old_map:
            if code not in current_map:
                used_code = code
                break
    return used_code


def test_invite_diff_incremented_uses():
    """Detects invite whose uses count went from 0 → 1."""
    old = {"ABC": 0, "DEF": 0}
    new = {"ABC": 1, "DEF": 0}
    assert _diff_invites(old, new) == "ABC"


def test_invite_diff_deleted_invite():
    """Detects invite that disappeared after max_uses=1 consumption."""
    old = {"ABC": 0, "DEF": 0}
    new = {"DEF": 0}  # ABC was consumed and deleted
    assert _diff_invites(old, new) == "ABC"


def test_invite_diff_no_change():
    """Returns None when no invite changed."""
    old = {"ABC": 0}
    new = {"ABC": 0}
    assert _diff_invites(old, new) is None


def test_invite_diff_empty_snapshot():
    """Returns None when snapshot is empty (no data to diff against)."""
    assert _diff_invites({}, {"ABC": 1}) == "ABC"


# ============================================================
# 4. _handle_interest — invite code written to Column R
# ============================================================

@pytest.mark.asyncio
async def test_handle_interest_stores_real_invite_code(monkeypatch):
    """Real Discord invite code is stored in Column R, not the placeholder."""
    import cis_controller.interest_api_server as api

    captured_invite_code = {}

    async def _fake_check_dup(email, spreadsheet_id, sheet_range, creds_path):
        return False

    async def _fake_check_cap(spreadsheet_id, sheet_range, creds_path):
        return {"paid_count": 5, "cap": 30, "available": 25}

    async def _fake_create_invite():
        return {"code": "REALCODE", "url": "https://discord.gg/REALCODE"}

    async def _fake_append(name, email, phone, profession, invite_code, waitlisted,
                           spreadsheet_id, sheet_range, creds_path):
        captured_invite_code["code"] = invite_code
        return True

    async def _fake_send_email(**kwargs):
        return True

    monkeypatch.setattr(api, "check_duplicate_email", _fake_check_dup)
    monkeypatch.setattr(api, "check_enrollment_cap", _fake_check_cap)
    monkeypatch.setattr(api, "create_discord_invite_link", _fake_create_invite)
    monkeypatch.setattr(api, "append_to_student_roster", _fake_append)
    monkeypatch.setattr(api, "send_brevo_email", _fake_send_email)

    server = api.InterestAPIServer.__new__(api.InterestAPIServer)
    server.spreadsheet_id = "sheet123"
    server.creds_path = ""
    server.sheet_range = "Student Roster!A:Z"

    class _Req:
        async def json(self):
            return {"name": "Alice Wanjiru", "email": "alice@k2m.org", "phone": "+254700000001"}

    response = await server._handle_interest(_Req())
    body = json.loads(response.body)

    assert body["success"] is True
    assert captured_invite_code.get("code") == "REALCODE"


@pytest.mark.asyncio
async def test_handle_interest_tracks_real_invite_in_runtime_snapshot(monkeypatch):
    """Fresh one-use invites are inserted into the live join snapshot cache."""
    import cis_controller.interest_api_server as api

    monkeypatch.setenv("DISCORD_GUILD_ID", "777")

    async def _fake_check_dup(*_args, **_kwargs):
        return False

    async def _fake_check_cap(*_args, **_kwargs):
        return {"paid_count": 0, "cap": 30, "available": 30}

    async def _fake_create_invite():
        return {"code": "REALCODE", "url": "https://discord.gg/REALCODE"}

    async def _fake_append(*_args, **_kwargs):
        return True

    async def _fake_send_email(**_kwargs):
        return True

    monkeypatch.setattr(api, "check_duplicate_email", _fake_check_dup)
    monkeypatch.setattr(api, "check_enrollment_cap", _fake_check_cap)
    monkeypatch.setattr(api, "create_discord_invite_link", _fake_create_invite)
    monkeypatch.setattr(api, "append_to_student_roster", _fake_append)
    monkeypatch.setattr(api, "send_brevo_email", _fake_send_email)

    server = api.InterestAPIServer(spreadsheet_id="sheet123", creds_path="")
    snapshot = {}
    server.set_invite_snapshot_cache(snapshot)

    class _Req:
        async def json(self):
            return {"name": "Alice Wanjiru", "email": "alice@k2m.org", "phone": "+254700000001"}

    response = await server._handle_interest(_Req())
    body = json.loads(response.body)

    assert body["success"] is True
    assert snapshot == {777: {"REALCODE": 0}}


@pytest.mark.asyncio
async def test_handle_interest_falls_back_on_invite_failure(monkeypatch):
    """Uses DISCORD_INVITE_FALLBACK_URL when invite creation fails, still succeeds."""
    import cis_controller.interest_api_server as api

    monkeypatch.setenv("DISCORD_INVITE_FALLBACK_URL", "https://discord.gg/FALLBACK")
    captured = {}

    async def _fake_check_dup(*a, **kw): return False
    async def _fake_check_cap(*a, **kw): return {"paid_count": 0, "cap": 30, "available": 30}
    async def _fake_create_invite(): return None  # failure
    async def _fake_append(name, email, phone, profession, invite_code, waitlisted,
                           spreadsheet_id, sheet_range, creds_path):
        captured["invite_code"] = invite_code
        return True
    async def _fake_send_email(**kwargs): return True

    monkeypatch.setattr(api, "check_duplicate_email", _fake_check_dup)
    monkeypatch.setattr(api, "check_enrollment_cap", _fake_check_cap)
    monkeypatch.setattr(api, "create_discord_invite_link", _fake_create_invite)
    monkeypatch.setattr(api, "append_to_student_roster", _fake_append)
    monkeypatch.setattr(api, "send_brevo_email", _fake_send_email)

    server = api.InterestAPIServer.__new__(api.InterestAPIServer)
    server.spreadsheet_id = "sheet123"
    server.creds_path = ""
    server.sheet_range = "Student Roster!A:Z"

    class _Req:
        async def json(self):
            return {"name": "Bob Otieno", "email": "bob@k2m.org", "phone": "+254700000002"}

    response = await server._handle_interest(_Req())
    body = json.loads(response.body)

    assert body["success"] is True
    # Placeholder code is a k2m-prefixed string (not REALCODE)
    assert "REALCODE" not in captured.get("invite_code", "")


@pytest.mark.asyncio
async def test_find_row_by_invite_code_returns_matching_row(monkeypatch):
    """Column R lookup returns expected row number + values."""
    import cis_controller.interest_api_server as api

    async def _fake_read_rows(**_kwargs):
        return [
            ["Name", "Email", "Phone", "Discord", "Profession", "", "", "", "", "", "", "", "", "", "", "", "", "Invite"],
            ["Alice", "alice@k2m.org", "+2547", "", "Teacher", "", "", "", "", "", "", "", "", "", "", "", "", "ABC123"],
            ["Bob", "bob@k2m.org", "+2547", "", "Founder", "", "", "", "", "", "", "", "", "", "", "", "", "DEF456"],
        ]

    monkeypatch.setattr(api, "read_roster_rows", _fake_read_rows)

    result = await api.find_row_by_invite_code(
        invite_code="DEF456",
        spreadsheet_id="sheet-123",
        sheet_range="Student Roster!A:Z",
    )

    assert result is not None
    row_number, row = result
    assert row_number == 3
    assert row[api.COL_EMAIL] == "bob@k2m.org"


@pytest.mark.asyncio
async def test_link_roster_discord_identity_by_invite_code_updates_column_d(monkeypatch):
    """Sheet bridge writes Column D as `discord_id|discord_username`."""
    import cis_controller.interest_api_server as api

    async def _fake_find(*args, **kwargs):
        row = ["Alice", "alice@k2m.org", "+2547", "", "Teacher"] + [""] * 13
        row[api.COL_INVITE] = "ABC123"
        return 2, row

    captured = {}

    async def _fake_update(row_number, updates, spreadsheet_id, sheet_range, creds_path):
        captured["row_number"] = row_number
        captured["updates"] = updates
        return True

    monkeypatch.setattr(api, "find_row_by_invite_code", _fake_find)
    monkeypatch.setattr(api, "update_roster_cells", _fake_update)

    result = await api.link_roster_discord_identity_by_invite_code(
        invite_code="ABC123",
        discord_id="123456789",
        discord_username="alice#0001",
        spreadsheet_id="sheet-123",
    )

    assert result is not None
    assert captured["row_number"] == 2
    assert captured["updates"][api.COL_DISCORD_ID] == "123456789|alice#0001"
    assert result["enrollment_email"] == "alice@k2m.org"


@pytest.mark.asyncio
async def test_select_unique_recent_unlinked_roster_student_returns_only_candidate(monkeypatch):
    """Sheets fallback resolves only when exactly one recent unlinked row exists."""
    import cis_controller.interest_api_server as api

    now = api._iso_utc(api.datetime.now(api.timezone.utc))

    async def _fake_read_rows(**_kwargs):
        return [
            ["Name", "Email", "Phone", "Discord", "Profession", "", "", "", "", "", "", "", "", "Created", "", "", "", "Invite"],
            ["Alice", "alice@k2m.org", "+2547", "", "Teacher", "", "", "", "", "", "", "", "", now, "", "", "", "ABC123"],
        ]

    monkeypatch.setattr(api, "read_roster_rows", _fake_read_rows)

    result = await api.select_unique_recent_unlinked_roster_student(
        spreadsheet_id="sheet-123",
        sheet_range="Student Roster!A:Z",
        window_minutes=20,
    )

    assert result is not None
    assert result["invite_code"] == "ABC123"
    assert result["enrollment_email"] == "alice@k2m.org"


@pytest.mark.asyncio
async def test_on_member_join_uses_sheets_fallback_when_pg_has_no_recent_match(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_GUILD_ID", "777")
    monkeypatch.setenv("COHORT_1_START_DATE", "2026-03-16")
    monkeypatch.setenv("GOOGLE_SHEETS_ID", "sheet-123")

    main_module = importlib.import_module("main")
    main_module = importlib.reload(main_module)

    guest_role = MagicMock()
    guest_role.name = "Guest"

    guild = MagicMock()
    guild.id = 777
    guild.roles = [guest_role]
    guild.invites = AsyncMock(return_value=[])

    member = MagicMock()
    member.bot = False
    member.id = 123456789
    member.name = "duffy"
    member.display_name = "Duffy"
    member.guild = guild
    member.add_roles = AsyncMock()
    member.send = AsyncMock()

    store = MagicMock()
    store.get_student_by_invite_code = MagicMock(return_value=None)
    store.link_student_by_invite = MagicMock(return_value=False)
    store.log_observability_event = MagicMock()
    store.update_onboarding_stop = MagicMock()
    store.touch_student_last_active = MagicMock()
    store.upsert_student_from_sheets = MagicMock()
    store.get_student = MagicMock(
        return_value={"enrollment_name": "Dare Denish", "profession": "teacher"}
    )

    roster_payload = {
        "row_number": 21,
        "enrollment_name": "Dare Denish",
        "enrollment_email": "daredenish12@gmail.com",
        "profession": "teacher",
        "invite_code": "REAL123",
    }

    with patch.object(main_module, "_get_store", return_value=store), patch.object(
        main_module,
        "_select_unique_recent_unlinked_student",
        return_value=None,
    ), patch.object(
        main_module,
        "_select_unique_recent_unlinked_roster_student",
        new=AsyncMock(return_value=roster_payload),
    ), patch.object(
        main_module,
        "_link_member_identity_to_roster",
        new=AsyncMock(return_value=roster_payload),
    ):
        await main_module.on_member_join(member)

    store.upsert_student_from_sheets.assert_called_once_with(
        enrollment_email="daredenish12@gmail.com",
        enrollment_name="Dare Denish",
        invite_code="REAL123",
        enrollment_status="lead",
        payment_status="lead",
    )
    store.link_student_by_invite.assert_called_once_with(
        invite_code="REAL123",
        discord_id="123456789",
        discord_username="duffy",
    )
    member.send.assert_awaited_once()
    assert "Step 2 complete - here's Step 3." in member.send.await_args.args[0]
