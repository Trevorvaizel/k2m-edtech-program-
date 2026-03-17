"""
Tests for /api/enroll endpoint — diagnostic fields (zone_verification, anxiety_level, habits_baseline).

Verifies:
  1. New columns S/T/U are written when provided
  2. Optional fields are omitted from the update dict when absent
  3. Zone normalization: "0" → "Zone 0", "Zone 2" stays "Zone 2"
  4. anxiety_level is coerced to string int (int or float input)
  5. Missing required fields → 400
  6. Full payload with all diagnostic fields writes to correct column indices
"""

import json

import pytest

from cis_controller import interest_api_server as api


class _Request:
    def __init__(self, payload=None):
        self._payload = payload or {}

    async def json(self):
        return self._payload


def _make_enroll_server():
    return api.InterestAPIServer(spreadsheet_id="sheet-123", creds_path="creds")


def _base_row():
    """18-cell roster row (A-R) with minimum required data."""
    row = [""] * 21
    row[api.COL_NAME] = "Test Student"
    row[api.COL_EMAIL] = "student@example.com"
    row[api.COL_PAYMENT] = "Lead"
    return row


# ── Zone normalisation ────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("raw,expected", [
    ("0",      "Zone 0"),
    ("1",      "Zone 1"),
    ("4",      "Zone 4"),
    ("Zone 0", "Zone 0"),
    ("Zone 3", "Zone 3"),
])
async def test_zone_normalisation(raw, expected, monkeypatch):
    """Zone submitted as raw digit or 'Zone N' both stored as 'Zone N'."""
    captured = {}

    async def _find(email, **_kw):
        return 2, _base_row()

    async def _update(row_number, updates, **_kw):
        captured.update(updates)
        return True

    async def _email(**_kw):
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find)
    monkeypatch.setattr(api, "update_roster_cells", _update)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda t: f"https://k2m.io?token={t}")

    server = _make_enroll_server()
    response = await server._handle_enroll(_Request({
        "email": "student@example.com",
        "zone": raw,
        "situation": "University student preparing for future",
        "goals": "Build AI skills to stay competitive",
        "emotional_baseline": "Curious",
    }))

    assert response.status == 200
    assert captured[api.COL_ZONE] == expected


# ── Diagnostic fields written to correct columns ──────────────────────────────

@pytest.mark.asyncio
async def test_all_diagnostic_fields_written_to_correct_columns(monkeypatch):
    """zone_verification→S, anxiety_level→T, habits_baseline→U."""
    captured = {}

    async def _find(email, **_kw):
        return 2, _base_row()

    async def _update(row_number, updates, **_kw):
        captured.update(updates)
        return True

    async def _email(**_kw):
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find)
    monkeypatch.setattr(api, "update_roster_cells", _update)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda t: f"https://k2m.io?token={t}")

    server = _make_enroll_server()
    response = await server._handle_enroll(_Request({
        "email": "student@example.com",
        "zone": "Zone 2",
        "situation": "Gap year student from rural Kenya",
        "goals": "Use AI for small business ideas",
        "emotional_baseline": "Curious,Nervous",
        "zone_verification": "scenario-b",
        "anxiety_level": 7,
        "habits_baseline": "chatgpt-daily,journaling",
        "parent_email": "parent@example.com",
    }))

    assert response.status == 200
    # Core fields
    assert captured[api.COL_ZONE] == "Zone 2"
    assert captured[api.COL_SITUATION] == "Gap year student from rural Kenya"
    assert captured[api.COL_GOALS] == "Use AI for small business ideas"
    assert captured[api.COL_EMOTIONAL] == "Curious,Nervous"
    assert captured[api.COL_PARENT_EMAIL] == "parent@example.com"
    # Diagnostic fields — column indices 18, 19, 20
    assert api.COL_ZONE_VERIFY == 18
    assert api.COL_ANXIETY == 19
    assert api.COL_HABITS == 20
    assert captured[api.COL_ZONE_VERIFY] == "scenario-b"
    assert captured[api.COL_ANXIETY] == "7"
    assert captured[api.COL_HABITS] == "chatgpt-daily,journaling"


# ── Optional fields omitted when absent ──────────────────────────────────────

@pytest.mark.asyncio
async def test_diagnostic_fields_omitted_when_not_provided(monkeypatch):
    """zone_verification, anxiety_level, habits_baseline absent → not in update dict."""
    captured = {}

    async def _find(email, **_kw):
        return 2, _base_row()

    async def _update(row_number, updates, **_kw):
        captured.update(updates)
        return True

    async def _email(**_kw):
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find)
    monkeypatch.setattr(api, "update_roster_cells", _update)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda t: f"https://k2m.io?token={t}")

    server = _make_enroll_server()
    await server._handle_enroll(_Request({
        "email": "student@example.com",
        "zone": "Zone 1",
        "situation": "Recent graduate",
        "goals": "Land first tech job",
        "emotional_baseline": "Hopeful",
        # no zone_verification, anxiety_level, or habits_baseline
    }))

    assert api.COL_ZONE_VERIFY not in captured
    assert api.COL_ANXIETY not in captured
    assert api.COL_HABITS not in captured


# ── anxiety_level coercion ────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("raw_anxiety,expected_str", [
    (5,    "5"),
    (10,   "10"),
    (1,    "1"),
    (7.9,  "7"),   # float truncated via int()
])
async def test_anxiety_level_coerced_to_string_integer(raw_anxiety, expected_str, monkeypatch):
    captured = {}

    async def _find(email, **_kw):
        return 2, _base_row()

    async def _update(row_number, updates, **_kw):
        captured.update(updates)
        return True

    async def _email(**_kw):
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find)
    monkeypatch.setattr(api, "update_roster_cells", _update)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda t: f"https://k2m.io?token={t}")

    server = _make_enroll_server()
    await server._handle_enroll(_Request({
        "email": "student@example.com",
        "zone": "Zone 3",
        "situation": "Working professional",
        "goals": "Automate my workflow",
        "emotional_baseline": "Excited",
        "anxiety_level": raw_anxiety,
    }))

    assert captured[api.COL_ANXIETY] == expected_str


# ── Required field validation ─────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("missing_field", [
    "email", "zone", "situation", "goals", "emotional_baseline"
])
async def test_enroll_returns_400_when_required_field_missing(missing_field, monkeypatch):
    """Each required field, when absent, should produce a 400."""
    async def _find(email, **_kw):
        return 2, _base_row()

    monkeypatch.setattr(api, "find_row_by_email", _find)

    full_payload = {
        "email": "student@example.com",
        "zone": "Zone 2",
        "situation": "University student",
        "goals": "Learn AI basics",
        "emotional_baseline": "Curious",
    }
    del full_payload[missing_field]

    server = _make_enroll_server()
    response = await server._handle_enroll(_Request(full_payload))
    payload = json.loads(response.text)

    assert response.status == 400
    assert payload["success"] is False


# ── Payment status promotion ──────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("initial_status,expected_status", [
    ("Lead",      "Enrolled"),
    ("",          "Enrolled"),
    ("Waitlisted","Enrolled"),
    ("Enrolled",  "Enrolled"),   # idempotent
    ("Paid",      "Paid"),       # do not downgrade paid students
])
async def test_payment_status_promoted_correctly(initial_status, expected_status, monkeypatch):
    captured = {}
    row = _base_row()
    row[api.COL_PAYMENT] = initial_status

    async def _find(email, **_kw):
        return 2, row

    async def _update(row_number, updates, **_kw):
        captured.update(updates)
        return True

    async def _email(**_kw):
        return True

    monkeypatch.setattr(api, "find_row_by_email", _find)
    monkeypatch.setattr(api, "update_roster_cells", _update)
    monkeypatch.setattr(api, "send_enrollment_payment_email", _email)
    monkeypatch.setattr(api, "_generate_submit_token", lambda: "tok")
    monkeypatch.setattr(api, "build_mpesa_submit_url", lambda t: f"https://k2m.io?token={t}")

    server = _make_enroll_server()
    await server._handle_enroll(_Request({
        "email": "student@example.com",
        "zone": "Zone 1",
        "situation": "Student",
        "goals": "Learn",
        "emotional_baseline": "Curious",
    }))

    assert captured[api.COL_PAYMENT] == expected_status


# ── Column letter helper ──────────────────────────────────────────────────────

def test_column_letter_mapping():
    """Verify column index → letter mapping for our new columns."""
    assert api._column_letter(api.COL_ZONE_VERIFY) == "S"   # index 18
    assert api._column_letter(api.COL_ANXIETY) == "T"       # index 19
    assert api._column_letter(api.COL_HABITS) == "U"        # index 20
    # Spot-check known columns
    assert api._column_letter(api.COL_NAME) == "A"
    assert api._column_letter(api.COL_EMAIL) == "B"
    assert api._column_letter(api.COL_ZONE) == "F"
    assert api._column_letter(api.COL_INVITE) == "R"
