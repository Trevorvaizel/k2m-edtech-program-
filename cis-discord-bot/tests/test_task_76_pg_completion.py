"""Task 7.6 reconciliation tests for PostgreSQL migration and sync behavior."""

from __future__ import annotations

import sys
import types
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import database
from scheduler.daily_prompts import WeekDay
from scheduler.scheduler import DailyPromptScheduler
from preload_students import sync_engagement_back_to_sheets
from database.pg_store import PgConnectionWrapper


def _make_fake_psycopg2(rows):
    class _Cursor:
        def execute(self, *_args, **_kwargs):
            return None

        def fetchall(self):
            return rows

    class _Conn:
        def cursor(self):
            return _Cursor()

        def close(self):
            return None

    return types.SimpleNamespace(connect=lambda dsn: _Conn())


def test_schema_pg_contains_task_76_required_columns():
    schema_path = Path(__file__).resolve().parents[1] / "database" / "schema_pg.sql"
    schema_text = schema_path.read_text(encoding="utf-8").lower()

    required_columns = [
        "cohort_id",
        "invite_code",
        "onboarding_stop_0_complete",
        "manual_override_timestamp",
        "profession",
        "barrier_type",
        "barrier_confidence",
        "situation",
        "goals",
        "emotional_baseline",
        "real_last_name",
        "preloaded",
        "engagement_level",
        "zone_shift_count",
        "frame_sessions_count",
        "showcase_posts_count",
        "last_frame_topic",
        "cis_journey_summary",
        "initial_zone",
        "artifact_title",
        "profile_complete",
        "primary_device_context",
        "family_obligations_hint",
    ]
    missing = [column for column in required_columns if column not in schema_text]
    assert not missing, f"schema_pg.sql missing required columns: {missing}"


def test_runtime_modules_do_not_directly_construct_studentstatestore():
    project_root = Path(__file__).resolve().parents[1]
    runtime_files = [
        project_root / "main.py",
        project_root / "cis_controller" / "router.py",
        project_root / "cis_controller" / "rate_limiter.py",
        project_root / "cis_controller" / "state_machine.py",
        project_root / "cis_controller" / "suggestions.py",
        project_root / "cis_controller" / "safety_filter.py",
        project_root / "cis_controller" / "parent_unsubscribe_server.py",
        project_root / "scheduler" / "scheduler.py",
        project_root / "scheduler" / "parent_email_scheduler.py",
    ]
    runtime_files.extend((project_root / "commands").glob("*.py"))

    offenders = []
    for file_path in runtime_files:
        text = file_path.read_text(encoding="utf-8")
        if "StudentStateStore(" in text:
            offenders.append(str(file_path))

    assert not offenders, (
        "Runtime modules must use database factory helpers; direct StudentStateStore() "
        f"construction found in: {offenders}"
    )


def test_sync_engagement_back_to_sheets_manual_override_guard(monkeypatch):
    db_rows = [
        ("123", "student@example.com", 2, "2026-03-05 10:00:00", 7, "zone_1"),
    ]
    monkeypatch.setitem(sys.modules, "psycopg2", _make_fake_psycopg2(db_rows))

    header = ["Name", "Email"] + [""] * 24
    row = ["Student Name", "student@example.com"] + [""] * 17 + ["2026-03-06 10:00:00"]
    monkeypatch.setattr(
        "preload_students.read_roster_from_sheets",
        lambda **_kwargs: [header, row],
    )

    result = sync_engagement_back_to_sheets(
        database_url="postgresql://test",
        spreadsheet_id="sheet-123",
        dry_run=True,
    )

    assert result["synced"] == 0
    assert result["skipped_manual"] == 1
    assert result["missing_sheet_row"] == 0


def test_sync_engagement_back_to_sheets_writes_expected_fields(monkeypatch):
    db_rows = [
        ("123", "student@example.com", 3, "2026-03-05 11:15:00", 9, "zone_2"),
    ]
    monkeypatch.setitem(sys.modules, "psycopg2", _make_fake_psycopg2(db_rows))

    header = ["Name", "Email"] + [""] * 24
    row = ["Student Name", "student@example.com"] + [""] * 24
    monkeypatch.setattr(
        "preload_students.read_roster_from_sheets",
        lambda **_kwargs: [header, row],
    )

    written = {}

    class _Values:
        def batchUpdate(self, spreadsheetId, body):
            written["spreadsheet_id"] = spreadsheetId
            written["body"] = body
            return self

        def execute(self):
            return {}

    class _Spreadsheets:
        def values(self):
            return _Values()

    class _Service:
        def spreadsheets(self):
            return _Spreadsheets()

    monkeypatch.setattr(
        "preload_students._build_sheets_service",
        lambda **_kwargs: _Service(),
    )

    result = sync_engagement_back_to_sheets(
        database_url="postgresql://test",
        spreadsheet_id="sheet-123",
        dry_run=False,
    )

    assert result == {"synced": 1, "skipped_manual": 0, "missing_sheet_row": 0}
    assert written["spreadsheet_id"] == "sheet-123"

    updates = written["body"]["data"]
    assert {"range": "Student Roster!AB2", "values": [["3"]]} in updates
    assert {"range": "Student Roster!AC2", "values": [["2026-03-05 11:15:00"]]} in updates
    assert {"range": "Student Roster!AD2", "values": [["9"]]} in updates


@pytest.mark.asyncio
async def test_scheduler_runs_nightly_sync_once_at_0010():
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
    scheduler.run_nightly_sheets_sync = AsyncMock()

    with patch("scheduler.scheduler.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(
            2026, 3, 5, 0, 10, tzinfo=scheduler.cohort_start_date.tzinfo
        )
        await scheduler.check_and_post()
        await scheduler.check_and_post()

        assert scheduler.run_nightly_sheets_sync.await_count == 1

        mock_datetime.now.return_value = datetime(
            2026, 3, 6, 0, 10, tzinfo=scheduler.cohort_start_date.tzinfo
        )
        await scheduler.check_and_post()

    assert scheduler.run_nightly_sheets_sync.await_count == 2


@pytest.mark.asyncio
async def test_scheduler_runs_welcome_lounge_refresh_once_at_2310():
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
    scheduler.post_welcome_lounge_status_refresh = AsyncMock()

    with patch("scheduler.scheduler.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(
            2026, 3, 5, 23, 10, tzinfo=scheduler.cohort_start_date.tzinfo
        )
        await scheduler.check_and_post()
        await scheduler.check_and_post()

        assert scheduler.post_welcome_lounge_status_refresh.await_count == 1

        mock_datetime.now.return_value = datetime(
            2026, 3, 6, 23, 10, tzinfo=scheduler.cohort_start_date.tzinfo
        )
        await scheduler.check_and_post()

    assert scheduler.post_welcome_lounge_status_refresh.await_count == 2


def test_database_factory_selects_pg_store_when_database_url_is_postgres():
    sentinel = object()
    with patch("database.pg_store.get_pg_store", return_value=sentinel) as mock_get_pg_store:
        store = database.get_store(database_url="postgresql://example.com/db")

    assert store is sentinel
    mock_get_pg_store.assert_called_once_with(database_url="postgresql://example.com/db")


def test_pg_connection_wrapper_cursor_supports_sqlite_style_calls():
    executed = {}

    class _FakeCursor:
        rowcount = 1

        def execute(self, sql, params=None):
            executed["sql"] = sql
            executed["params"] = params

        def fetchone(self):
            return {"ok": True}

        def fetchall(self):
            return [{"ok": True}]

    class _FakeConn:
        def cursor(self, cursor_factory=None):
            return _FakeCursor()

        def commit(self):
            return None

        def rollback(self):
            return None

    class _FakePool:
        def putconn(self, _conn):
            return None

    conn = PgConnectionWrapper(_FakeConn(), _FakePool())

    cursor = conn.cursor()
    row = cursor.execute("SELECT 1 WHERE id = ?", (7,)).fetchone()

    assert row == {"ok": True}
    assert executed["sql"] == "SELECT 1 WHERE id = %s"
    assert executed["params"] == (7,)


def test_pg_connection_wrapper_escapes_literal_percent_in_parameterized_queries():
    executed = {}

    class _FakeCursor:
        def execute(self, sql, params=None):
            executed["sql"] = sql
            executed["params"] = params

        def fetchone(self):
            return {"ok": True}

        def fetchall(self):
            return [{"ok": True}]

    class _FakeConn:
        def cursor(self, cursor_factory=None):
            return _FakeCursor()

        def commit(self):
            return None

        def rollback(self):
            return None

    class _FakePool:
        def putconn(self, _conn):
            return None

    conn = PgConnectionWrapper(_FakeConn(), _FakePool())

    conn.execute(
        "SELECT * FROM students WHERE discord_id LIKE '__pending__%' AND invite_code = ?",
        ("ABC123",),
    ).fetchone()

    assert executed["sql"] == (
        "SELECT * FROM students WHERE discord_id LIKE '__pending__%%' AND invite_code = %s"
    )
    assert executed["params"] == ("ABC123",)


def test_pg_connection_wrapper_rolls_back_failed_statement_before_next_query():
    executed = []

    class _FakeConn:
        def __init__(self):
            self.aborted = False
            self.rollback_calls = 0

        def cursor(self, cursor_factory=None):
            conn = self

            class _FakeCursor:
                rowcount = 1

                def execute(self, sql, params=None):
                    if sql == "SELECT broken":
                        conn.aborted = True
                        raise RuntimeError("boom")
                    if conn.aborted:
                        raise RuntimeError("current transaction is aborted")
                    executed.append((sql, params))

                def fetchone(self):
                    return {"ok": True}

            return _FakeCursor()

        def commit(self):
            return None

        def rollback(self):
            self.rollback_calls += 1
            self.aborted = False

    class _FakePool:
        def putconn(self, _conn, close=False):
            return None

    conn = PgConnectionWrapper(_FakeConn(), _FakePool())

    with pytest.raises(RuntimeError, match="boom"):
        conn.execute("SELECT broken")

    row = conn.execute("SELECT 1").fetchone()

    assert row == {"ok": True}
    assert executed == [("SELECT 1", None)]
    assert conn._conn.rollback_calls == 1


def test_pg_connection_wrapper_close_rolls_back_before_returning_to_pool():
    calls = {"rollback": 0, "putconn": []}

    class _FakeConn:
        closed = 0

        def rollback(self):
            calls["rollback"] += 1

    class _FakePool:
        def putconn(self, conn, close=False):
            calls["putconn"].append((conn, close))

    pg_conn = _FakeConn()
    pool = _FakePool()
    conn = PgConnectionWrapper(pg_conn, pool)

    conn.close()

    assert calls["rollback"] == 1
    assert calls["putconn"] == [(pg_conn, False)]
    assert conn._conn is None


def test_pg_store_realign_serial_sequences_advances_serials():
    from database.pg_store import PgStudentStateStore

    calls = []

    class _FakeCursor:
        def execute(self, query, params=None):
            calls.append((query, params))

        def fetchall(self):
            return [("observability_events", "id")]

    class _FakeConn:
        def cursor(self):
            return _FakeCursor()

    store = object.__new__(PgStudentStateStore)
    store.conn = types.SimpleNamespace(_conn=_FakeConn())

    realigned = store._realign_serial_sequences()

    assert realigned == 1
    assert len(calls) == 2
    assert calls[1][1] == ("observability_events", "id")


def test_pg_store_get_confirmed_student_count_uses_confirmed_and_linked_filters():
    from database.pg_store import PgStudentStateStore

    calls = []

    class _FakeResult:
        def fetchone(self):
            return {"count": 11}

    class _FakeConn:
        def execute(self, query, params=()):
            calls.append((query, params))
            return _FakeResult()

    store = object.__new__(PgStudentStateStore)
    store.conn = _FakeConn()

    count = store.get_confirmed_student_count()

    assert count == 11
    assert len(calls) == 1
    query = calls[0][0]
    assert "LOWER(COALESCE(payment_status" in query
    assert "discord_id NOT LIKE '__pending__%'" in query
