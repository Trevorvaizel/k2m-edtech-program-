"""
Database package — factory for runtime store selection.

Task 7.6: PostgreSQL full migration.

Usage:
    from database import get_store
    store = get_store()          # returns PgStudentStateStore if DATABASE_URL is postgres://
                                  # returns StudentStateStore (SQLite) otherwise (tests/local)
"""

import logging
import os

logger = logging.getLogger(__name__)

# Cached runtime store instance (set by main.py on_ready)
_runtime_store = None


def get_store(database_url: str = None):
    """
    Return the appropriate store based on DATABASE_URL environment variable.

    - DATABASE_URL=postgresql://...  → PgStudentStateStore (asyncpg-compatible psycopg2 pool)
    - DATABASE_URL not set / sqlite  → StudentStateStore (SQLite, for tests and local dev)

    The returned instance is NOT cached here — callers may create their own
    instances. Use set_runtime_store / get_runtime_store for the shared bot instance.
    """
    url = database_url or os.getenv("DATABASE_URL", "").strip()

    if url.startswith("postgresql://") or url.startswith("postgres://"):
        from database.pg_store import get_pg_store
        return get_pg_store(database_url=url)

    # Local / test environment — use SQLite
    from database.store import StudentStateStore
    return StudentStateStore()


def set_runtime_store(store) -> None:
    """Register the shared bot runtime store (called from main.py on_ready)."""
    global _runtime_store
    _runtime_store = store


def get_runtime_store():
    """Return the shared bot runtime store. Returns None if not yet initialized."""
    return _runtime_store
