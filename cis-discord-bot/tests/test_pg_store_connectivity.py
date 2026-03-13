from __future__ import annotations

from types import SimpleNamespace

from database.pg_store import PgConnectionWrapper, PgStudentStateStore


class _FakeCursor:
    def __init__(self, conn: "_FakeConn") -> None:
        self._conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql: str, params=None) -> None:
        self._conn.executed.append((sql, params))
        if self._conn.fail_execute:
            raise Exception(self._conn.fail_message)

    def close(self) -> None:
        return None

    def fetchone(self):
        return None

    def fetchall(self):
        return []


class _FakeConn:
    def __init__(
        self,
        *,
        closed: int = 0,
        fail_execute: bool = False,
        fail_message: str = "query failed",
    ) -> None:
        self.closed = closed
        self.fail_execute = fail_execute
        self.fail_message = fail_message
        self.autocommit = False
        self.executed = []

    def cursor(self, cursor_factory=None):
        return _FakeCursor(self)


class _FakePool:
    def __init__(self, conns: list[_FakeConn]) -> None:
        self._conns = list(conns)
        self.put_calls: list[tuple[_FakeConn, bool]] = []

    def getconn(self):
        if not self._conns:
            raise RuntimeError("no fake connections left")
        return self._conns.pop(0)

    def putconn(self, conn, close=False):
        self.put_calls.append((conn, bool(close)))


def test_check_pg_connectivity_refreshes_closed_primary_connection():
    old_pool = PgStudentStateStore._pg_pool
    try:
        closed_primary = _FakeConn(closed=1)
        probe_conn = _FakeConn()
        fresh_primary = _FakeConn()
        pool = _FakePool([probe_conn, fresh_primary])
        PgStudentStateStore._pg_pool = pool

        store = PgStudentStateStore.__new__(PgStudentStateStore)
        store.conn = SimpleNamespace(_conn=closed_primary)

        assert store.check_pg_connectivity() is True
        assert isinstance(store.conn, PgConnectionWrapper)
        assert store.conn._conn is fresh_primary
        assert probe_conn.executed and probe_conn.executed[0][0] == "SELECT 1"
        assert (closed_primary, True) in pool.put_calls
    finally:
        PgStudentStateStore._pg_pool = old_pool


def test_check_pg_connectivity_recovers_after_ssl_probe_failure():
    old_pool = PgStudentStateStore._pg_pool
    try:
        primary = _FakeConn()
        failing_probe = _FakeConn(
            fail_execute=True,
            fail_message="SSL connection has been closed unexpectedly",
        )
        fresh_primary = _FakeConn()
        pool = _FakePool([failing_probe, fresh_primary])
        PgStudentStateStore._pg_pool = pool

        store = PgStudentStateStore.__new__(PgStudentStateStore)
        store.conn = SimpleNamespace(_conn=primary)

        assert store.check_pg_connectivity() is True
        assert isinstance(store.conn, PgConnectionWrapper)
        assert store.conn._conn is fresh_primary
        assert fresh_primary.executed and fresh_primary.executed[0][0] == "SELECT 1"
    finally:
        PgStudentStateStore._pg_pool = old_pool


def test_connection_wrapper_retries_execute_after_connection_closed_error():
    broken_conn = _FakeConn(
        fail_execute=True,
        fail_message="SSL connection has been closed unexpectedly",
    )
    fresh_conn = _FakeConn()
    pool = _FakePool([fresh_conn])

    wrapper = PgConnectionWrapper(broken_conn, pool=pool)
    wrapper.execute("SELECT 1")

    assert fresh_conn.executed and fresh_conn.executed[0][0] == "SELECT 1"
    assert (broken_conn, True) in pool.put_calls
