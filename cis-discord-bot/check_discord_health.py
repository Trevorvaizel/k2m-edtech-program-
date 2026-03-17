#!/usr/bin/env python3
"""
Discord health check for KIRA.

Checks:
- Environment + LLM provider configuration
- Discord bot authentication
- Guild visibility
- Required channel visibility
- Required slash command registration

Exit codes:
- 0: all required checks passed
- 1: one or more required checks failed
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from dotenv import load_dotenv

from cis_controller.llm_integration import (
    get_active_model,
    get_active_provider,
    validate_provider_configuration,
)

BOT_DIR = Path(__file__).resolve().parent
if not load_dotenv(dotenv_path=BOT_DIR / ".env", override=False):
    load_dotenv()

API_BASE = "https://discord.com/api/v10"

REQUIRED_CHANNELS = {
    "CHANNEL_THINKING_LAB": "thinking-lab",
    "CHANNEL_BOT_TESTING": "bot-testing",
    "CHANNEL_THINKING_SHOWCASE": "thinking-showcase",
    "CHANNEL_FACILITATOR_DASHBOARD": "facilitator-dashboard",
    "CHANNEL_WELCOME_LOUNGE": "welcome-lounge",
}

REQUIRED_SLASH_COMMANDS = [
    "ping",
    "status",
    "frame",
    "framer",
    "diverge",
    "challenge",
    "synthesize",
    "create-artifact",
    "save",
    "review",
    "edit",
    "publish",
    "show-aggregate-patterns",
    "inspect-journey",
    "show-stuck-students",
    "show-zone-shifts",
    "show-milestones",
]


def discord_get(
    path: str,
    token: str,
    timeout_seconds: float = 20.0,
) -> Tuple[bool, int | None, Dict[str, Any] | None, str | None]:
    url = f"{API_BASE}{path}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "k2m-discord-healthcheck/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body) if body else {}
            return True, response.status, data, None
    except urllib.error.HTTPError as exc:
        payload = ""
        try:
            payload = exc.read().decode("utf-8", errors="ignore")
        except Exception:
            payload = str(exc)
        message = payload
        try:
            err_json = json.loads(payload)
            code = err_json.get("code")
            detail = err_json.get("message", payload)
            message = f"{detail} (code={code})" if code is not None else detail
        except Exception:
            pass
        return False, exc.code, None, message
    except Exception as exc:
        return False, None, None, str(exc)


def _is_transient_discord_error(status: int | None, error: str | None) -> bool:
    if status in {429, 500, 502, 503, 504}:
        return True
    if not error:
        return False

    lowered = error.lower()
    transient_markers = (
        "timed out",
        "temporary failure",
        "temporarily unavailable",
        "connection reset",
        "connection aborted",
        "connection refused",
        "remote end closed connection",
        "name resolution",
        "network is unreachable",
    )
    return any(marker in lowered for marker in transient_markers)


def discord_get_with_retry(
    path: str,
    token: str,
    retries: int = 2,
    retry_backoff_seconds: float = 1.5,
    timeout_seconds: float = 20.0,
    sleeper: Callable[[float], None] = time.sleep,
    getter: Callable[[str, str, float], Tuple[bool, int | None, Dict[str, Any] | None, str | None]] = discord_get,
) -> Tuple[bool, int | None, Dict[str, Any] | None, str | None]:
    max_attempts = max(1, retries + 1)
    last_result: Tuple[bool, int | None, Dict[str, Any] | None, str | None] = (
        False,
        None,
        None,
        "unknown error",
    )

    for attempt in range(1, max_attempts + 1):
        result = getter(path, token, timeout_seconds)
        last_result = result
        ok, status, data, error = result

        if ok:
            return ok, status, data, error
        if attempt >= max_attempts:
            return ok, status, data, error
        if not _is_transient_discord_error(status, error):
            return ok, status, data, error

        backoff = max(0.0, retry_backoff_seconds) * (2 ** (attempt - 1))
        sleeper(backoff)

    return last_result


def _line(kind: str, name: str, detail: str) -> str:
    return f"[{kind}] {name}: {detail}"


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        safe = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
        print(safe)


def run_health_check(
    retries: int = 2,
    retry_backoff_seconds: float = 1.5,
    timeout_seconds: float = 20.0,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "passes": [],
        "warnings": [],
        "failures": [],
        "provider": {},
        "discord": {},
        "probe_config": {
            "retries": max(0, retries),
            "retry_backoff_seconds": retry_backoff_seconds,
            "timeout_seconds": timeout_seconds,
        },
    }

    def mark_pass(name: str, detail: str) -> None:
        result["passes"].append(_line("PASS", name, detail))

    def mark_warn(name: str, detail: str) -> None:
        result["warnings"].append(_line("WARN", name, detail))

    def mark_fail(name: str, detail: str) -> None:
        result["failures"].append(_line("FAIL", name, detail))

    token = os.getenv("DISCORD_TOKEN", "").strip()
    guild_id = os.getenv("DISCORD_GUILD_ID", "").strip()

    provider = get_active_provider()
    model = get_active_model(provider)
    provider_ok, provider_detail = validate_provider_configuration()
    result["provider"] = {
        "name": provider,
        "model": model,
        "ok": provider_ok,
        "details": provider_detail,
    }
    if provider_ok:
        mark_pass("provider", f"{provider} / {model}")
    else:
        mark_fail("provider", provider_detail)

    if not token:
        mark_fail("DISCORD_TOKEN", "not set")
        return result
    mark_pass("DISCORD_TOKEN", "configured")

    def fetch(path: str) -> Tuple[bool, int | None, Dict[str, Any] | None, str | None]:
        return discord_get_with_retry(
            path=path,
            token=token,
            retries=max(0, retries),
            retry_backoff_seconds=retry_backoff_seconds,
            timeout_seconds=timeout_seconds,
        )

    ok, status, me, error = fetch("/users/@me")
    if not ok or not me:
        mark_fail("discord_auth", f"status={status}, error={error}")
        return result
    bot_name = me.get("username", "<unknown>")
    app_id = me.get("id", "")
    result["discord"]["bot_user"] = bot_name
    mark_pass("discord_auth", f"bot={bot_name}, status={status}")

    if not guild_id:
        mark_fail("DISCORD_GUILD_ID", "not set")
        return result
    mark_pass("DISCORD_GUILD_ID", guild_id)

    ok, status, guild_data, error = fetch(f"/guilds/{guild_id}")
    if not ok or not guild_data:
        mark_fail("guild_access", f"status={status}, error={error}")
        return result
    guild_name = guild_data.get("name", guild_id)
    result["discord"]["guild"] = {"id": guild_id, "name": guild_name}
    mark_pass("guild_access", f"{guild_name} ({guild_id})")

    ok, status, guild_channels, error = fetch(f"/guilds/{guild_id}/channels")
    if not ok or not isinstance(guild_channels, list):
        mark_fail("guild_channels", f"status={status}, error={error}")
        return result

    channels_by_slug = {}
    for channel in guild_channels:
        channel_name = str(channel.get("name", "")).lower()
        channels_by_slug[channel_name] = channel

    for env_key, slug in REQUIRED_CHANNELS.items():
        configured_id = os.getenv(env_key, "").strip()
        if configured_id:
            ok, status, channel_data, error = fetch(f"/channels/{configured_id}")
            if not ok or not channel_data:
                mark_fail(env_key, f"id={configured_id}, status={status}, error={error}")
                continue
            channel_name = channel_data.get("name", configured_id)
            channel_guild_id = str(channel_data.get("guild_id", ""))
            if channel_guild_id and channel_guild_id != guild_id:
                mark_fail(
                    env_key,
                    (
                        f"id={configured_id} resolved to #{channel_name} "
                        f"in different guild ({channel_guild_id})"
                    ),
                )
                continue
            mark_pass(env_key, f"id={configured_id}, name=#{channel_name}")
        else:
            matches = [
                c for c in guild_channels if slug in str(c.get("name", "")).lower()
            ]
            if matches:
                sample = matches[0]
                mark_warn(
                    env_key,
                    (
                        f"missing env value; found likely match "
                        f"id={sample.get('id')} name=#{sample.get('name')}"
                    ),
                )
            else:
                mark_fail(env_key, "missing env value and no matching channel found")

    ok, status, commands, error = fetch(f"/applications/{app_id}/guilds/{guild_id}/commands")
    if not ok or not isinstance(commands, list):
        mark_fail("slash_commands", f"status={status}, error={error}")
        return result

    command_names = sorted(str(cmd.get("name", "")) for cmd in commands)
    missing = [name for name in REQUIRED_SLASH_COMMANDS if name not in command_names]
    if missing:
        mark_fail("slash_commands", f"missing={', '.join(missing)}")
    else:
        mark_pass("slash_commands", f"all {len(REQUIRED_SLASH_COMMANDS)} required commands present")

    result["discord"]["registered_commands"] = command_names
    return result


def print_human_summary(result: Dict[str, Any]) -> None:
    for line in result["passes"]:
        _safe_print(line)
    for line in result["warnings"]:
        _safe_print(line)
    for line in result["failures"]:
        _safe_print(line)

    status = "HEALTHCHECK PASSED" if not result["failures"] else "HEALTHCHECK FAILED"
    _safe_print("")
    _safe_print(status)
    _safe_print(
        f"passes={len(result['passes'])} "
        f"warnings={len(result['warnings'])} "
        f"failures={len(result['failures'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Discord + provider health for KIRA bot.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output instead of human-readable output.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=int(os.getenv("DISCORD_HEALTH_RETRIES", "2")),
        help="Number of retry attempts for transient Discord API failures (default: 2).",
    )
    parser.add_argument(
        "--retry-backoff-seconds",
        type=float,
        default=float(os.getenv("DISCORD_HEALTH_RETRY_BACKOFF_SECONDS", "1.5")),
        help="Base backoff for retries in seconds; exponential per retry (default: 1.5).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=float(os.getenv("DISCORD_HEALTH_TIMEOUT_SECONDS", "20")),
        help="Per-request timeout in seconds for Discord API calls (default: 20).",
    )
    args = parser.parse_args()

    result = run_health_check(
        retries=max(0, args.retries),
        retry_backoff_seconds=max(0.0, args.retry_backoff_seconds),
        timeout_seconds=max(1.0, args.timeout_seconds),
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_summary(result)

    return 0 if not result["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
