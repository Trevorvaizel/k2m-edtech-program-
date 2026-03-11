from __future__ import annotations

from typing import Any, Dict, List, Tuple

import check_discord_health as health


HealthResult = Tuple[bool, int | None, Dict[str, Any] | None, str | None]


def test_discord_get_with_retry_recovers_after_timeout() -> None:
    responses: List[HealthResult] = [
        (False, None, None, "The read operation timed out"),
        (True, 200, {"ok": True}, None),
    ]
    calls: List[Tuple[str, str, float]] = []
    sleeps: List[float] = []

    def fake_getter(path: str, token: str, timeout_seconds: float) -> HealthResult:
        calls.append((path, token, timeout_seconds))
        return responses.pop(0)

    result = health.discord_get_with_retry(
        path="/users/@me",
        token="token",
        retries=2,
        retry_backoff_seconds=1.5,
        timeout_seconds=20.0,
        sleeper=sleeps.append,
        getter=fake_getter,
    )

    assert result[0] is True
    assert len(calls) == 2
    assert sleeps == [1.5]


def test_discord_get_with_retry_does_not_retry_non_transient_http_error() -> None:
    calls: List[Tuple[str, str, float]] = []
    sleeps: List[float] = []

    def fake_getter(path: str, token: str, timeout_seconds: float) -> HealthResult:
        calls.append((path, token, timeout_seconds))
        return False, 403, None, "Missing Access"

    result = health.discord_get_with_retry(
        path="/guilds/1/channels",
        token="token",
        retries=3,
        retry_backoff_seconds=1.0,
        timeout_seconds=20.0,
        sleeper=sleeps.append,
        getter=fake_getter,
    )

    assert result[0] is False
    assert result[1] == 403
    assert len(calls) == 1
    assert sleeps == []


def test_discord_get_with_retry_exhausts_retries_on_transient_server_error() -> None:
    calls: List[Tuple[str, str, float]] = []
    sleeps: List[float] = []

    def fake_getter(path: str, token: str, timeout_seconds: float) -> HealthResult:
        calls.append((path, token, timeout_seconds))
        return False, 503, None, "Service Unavailable"

    result = health.discord_get_with_retry(
        path="/applications/1/guilds/2/commands",
        token="token",
        retries=2,
        retry_backoff_seconds=1.0,
        timeout_seconds=20.0,
        sleeper=sleeps.append,
        getter=fake_getter,
    )

    assert result[0] is False
    assert result[1] == 503
    assert len(calls) == 3
    assert sleeps == [1.0, 2.0]
