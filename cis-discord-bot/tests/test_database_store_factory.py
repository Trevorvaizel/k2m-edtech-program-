from __future__ import annotations

import database


def test_get_store_prefers_runtime_store_when_registered():
    original_runtime_store = database.get_runtime_store()
    sentinel = object()

    try:
        database.set_runtime_store(sentinel)
        assert database.get_store() is sentinel
    finally:
        database.set_runtime_store(original_runtime_store)
