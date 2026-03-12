"""
Task 7.8 reliability tests.

Covers:
  - /health endpoint reports healthy when DB + Discord are connected
  - /health endpoint reports degraded payload when Discord is unavailable
  - /health endpoint performs SQLite fallback connectivity probe via SELECT 1
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from cis_controller.parent_unsubscribe_server import ParentUnsubscribeServer


class _PgHealthyStore:
    def check_pg_connectivity(self) -> bool:
        return True


class _PgUnhealthyStore:
    def check_pg_connectivity(self) -> bool:
        return False


class _SqliteConn:
    def __init__(self) -> None:
        self.executed = []

    def execute(self, sql: str):
        self.executed.append(sql)
        return None


class _SqliteStore:
    def __init__(self) -> None:
        self.conn = _SqliteConn()


def _bot(ready: bool) -> MagicMock:
    bot = MagicMock()
    bot.is_ready.return_value = ready
    return bot


@pytest.mark.asyncio
async def test_health_returns_200_when_all_systems_connected():
    server = ParentUnsubscribeServer(
        store=_PgHealthyStore(),
        internal_webhook_server=SimpleNamespace(_bot=_bot(True)),
    )

    resp = await server._handle_health(MagicMock())
    payload = json.loads(resp.body)

    assert resp.status == 200
    assert payload["status"] == "healthy"
    assert payload["db"] == "connected"
    assert payload["discord"] == "connected"


@pytest.mark.asyncio
async def test_health_reports_degraded_when_discord_not_ready():
    server = ParentUnsubscribeServer(
        store=_PgHealthyStore(),
        internal_webhook_server=SimpleNamespace(_bot=_bot(False)),
    )

    resp = await server._handle_health(MagicMock())
    payload = json.loads(resp.body)

    assert resp.status == 200
    assert payload["status"] == "degraded"
    assert payload["db"] == "connected"
    assert payload["discord"] == "disconnected"


@pytest.mark.asyncio
async def test_health_uses_sqlite_probe_when_pg_check_absent():
    store = _SqliteStore()
    server = ParentUnsubscribeServer(
        store=store,
        internal_webhook_server=SimpleNamespace(_bot=_bot(True)),
    )

    resp = await server._handle_health(MagicMock())
    payload = json.loads(resp.body)

    assert resp.status == 200
    assert payload["status"] == "healthy"
    assert "SELECT 1" in store.conn.executed


@pytest.mark.asyncio
async def test_health_reports_degraded_when_db_probe_fails():
    server = ParentUnsubscribeServer(
        store=_PgUnhealthyStore(),
        internal_webhook_server=SimpleNamespace(_bot=_bot(True)),
    )

    resp = await server._handle_health(MagicMock())
    payload = json.loads(resp.body)

    assert resp.status == 200
    assert payload["status"] == "degraded"
    assert payload["db"] == "disconnected"
    assert payload["discord"] == "connected"
