"""
internal_api_server.py — Task 7.11: HMAC-authenticated internal webhook endpoints.

DECISION N-03 (Session 4): Apps Script → Railway webhooks are unauthenticated.
This module provides:
  POST /api/internal/role-upgrade    — grant @Student role via discord_id
  POST /api/internal/preload-student — upsert one student row to PostgreSQL

Both endpoints require a valid X-K2M-Signature header (HMAC-SHA256).
401 events are logged to #facilitator-dashboard with source IP.

Apps Script signing code (paste into activateStudent()):
  var payloadJson = JSON.stringify(payload);
  var secret = PropertiesService.getScriptProperties().getProperty('WEBHOOK_SECRET');
  var sig = Utilities.computeHmacSha256Signature(payloadJson, secret, Utilities.Charset.UTF_8);
  var sigHex = sig.map(function(b){ return ('0' + (b & 0xff).toString(16)).slice(-2); }).join('');
  var options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'X-K2M-Signature': 'sha256=' + sigHex },
    payload: payloadJson,
    muteHttpExceptions: true
  };
  UrlFetchApp.fetch(BOT_URL + '/api/internal/role-upgrade', options);
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

import httpx
from aiohttp import web

from cis_controller.webhook_auth import get_client_ip, require_webhook_signature

logger = logging.getLogger(__name__)

# ── Discord REST constants ──────────────────────────────────────────────────
DISCORD_API = "https://discord.com/api/v10"


def _discord_headers() -> dict:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    return {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }


async def _grant_student_role(discord_id: str) -> tuple[bool, str]:
    """
    PUT /guilds/{guild_id}/members/{user_id}/roles/{role_id} to assign @Student.
    Returns (success, error_message).
    """
    guild_id = os.getenv("DISCORD_GUILD_ID", "").strip()
    role_id = os.getenv("STUDENT_ROLE_ID", "").strip()
    if not guild_id or not role_id:
        return False, "DISCORD_GUILD_ID or STUDENT_ROLE_ID not configured"

    url = f"{DISCORD_API}/guilds/{guild_id}/members/{discord_id}/roles/{role_id}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.put(url, headers=_discord_headers())

        # 204 No Content = success; 404 = member not in server yet
        if resp.status_code == 204:
            return True, ""
        return False, f"Discord returned {resp.status_code}: {resp.text[:200]}"
    except Exception as exc:
        return False, f"Discord REST error: {exc}"


def _upsert_single_student(row: dict) -> tuple[bool, str]:
    """
    Upsert one student row to PostgreSQL.
    Accepts the same field names that Apps Script sends from the Sheets roster.
    Returns (success, error_message).
    """
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        return False, "DATABASE_URL not configured"

    try:
        import psycopg2

        conn = psycopg2.connect(dsn=database_url)
        cursor = conn.cursor()

        enrollment_email = row.get("enrollment_email") or row.get("email", "")
        enrollment_name = row.get("enrollment_name") or row.get("name", "")
        last_name = row.get("last_name", "")
        invite_code = row.get("invite_code", "")
        discord_id = row.get("discord_id") or f"__pending__{enrollment_email}"
        cohort_id = row.get("cohort_id") or os.getenv("COHORT_ID", "cohort-1")
        start_date = row.get("start_date") or os.getenv("COHORT_START_DATE", "")
        enrollment_status = row.get("enrollment_status", "enrolled")
        payment_status = row.get("payment_status", "Confirmed")

        cursor.execute(
            """
            INSERT INTO students (
                discord_id, enrollment_email, enrollment_name, last_name,
                invite_code, cohort_id, start_date, enrollment_status, payment_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (discord_id) DO UPDATE SET
                enrollment_email  = EXCLUDED.enrollment_email,
                enrollment_name   = EXCLUDED.enrollment_name,
                last_name         = EXCLUDED.last_name,
                invite_code       = EXCLUDED.invite_code,
                cohort_id         = EXCLUDED.cohort_id,
                enrollment_status = EXCLUDED.enrollment_status,
                payment_status    = EXCLUDED.payment_status
            """,
            (
                discord_id, enrollment_email, enrollment_name, last_name,
                invite_code, cohort_id, start_date, enrollment_status, payment_status,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, ""
    except Exception as exc:
        return False, f"DB upsert error: {exc}"


async def _log_401_to_dashboard(bot, source_ip: str, endpoint: str, reason: str) -> None:
    """Post a 401 alert to #facilitator-dashboard (best-effort)."""
    try:
        channel_id = os.getenv("FACILITATOR_DASHBOARD_CHANNEL_ID", "").strip()
        if not bot or not channel_id:
            logger.warning(
                "401 on %s from %s (%s) — dashboard channel not configured",
                endpoint, source_ip, reason,
            )
            return
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            channel = await bot.fetch_channel(int(channel_id))
        await channel.send(
            f"🚨 **401 Unauthorized webhook** on `{endpoint}`\n"
            f"Source IP: `{source_ip}`\n"
            f"Reason: {reason}"
        )
    except Exception as exc:
        logger.error("Failed to log 401 to dashboard: %s", exc)


class InternalWebhookServer:
    """
    Lightweight aiohttp server for HMAC-authenticated Apps Script → bot webhooks.

    Endpoints:
      POST /api/internal/role-upgrade    — body: {"discord_id": "..."}
      POST /api/internal/preload-student — body: {<student row fields>}
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8081,
        bot=None,
        interest_api_server=None,
    ):
        self.host = host
        self.port = port
        self._bot = bot
        self._interest_api_server = interest_api_server
        self._runner: Optional[web.AppRunner] = None
        self._site = None

    def set_bot(self, bot) -> None:
        """Inject bot reference after startup (called from main.py on_ready)."""
        self._bot = bot

    # ── Handlers ──────────────────────────────────────────────────────────

    async def _handle_role_upgrade(self, request: web.Request) -> web.Response:
        """
        POST /api/internal/role-upgrade
        Body: {"discord_id": "<numeric Discord user ID>"}
        Header: X-K2M-Signature: sha256=<hmac>
        """
        source_ip = get_client_ip(request)
        ok, body, reason = await require_webhook_signature(request)
        if not ok:
            logger.warning("401 role-upgrade from %s: %s", source_ip, reason)
            await _log_401_to_dashboard(self._bot, source_ip, "/api/internal/role-upgrade", reason)
            return web.json_response({"success": False, "error": reason}, status=401)

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError) as exc:
            return web.json_response(
                {"success": False, "error": f"Invalid JSON: {exc}"}, status=400
            )

        discord_id = str(data.get("discord_id", "")).strip()
        if not discord_id or not discord_id.isdigit():
            return web.json_response(
                {"success": False, "error": "discord_id must be a numeric Discord user ID"},
                status=400,
            )

        success, error = await _grant_student_role(discord_id)
        if not success:
            logger.error("role-upgrade failed for %s: %s", discord_id, error)
            return web.json_response({"success": False, "error": error}, status=500)

        logger.info("role-upgrade granted @Student to discord_id=%s", discord_id)
        return web.json_response({"success": True, "discord_id": discord_id})

    async def _handle_preload_student(self, request: web.Request) -> web.Response:
        """
        POST /api/internal/preload-student
        Body: {<student row fields>}
        Header: X-K2M-Signature: sha256=<hmac>
        """
        source_ip = get_client_ip(request)
        ok, body, reason = await require_webhook_signature(request)
        if not ok:
            logger.warning("401 preload-student from %s: %s", source_ip, reason)
            await _log_401_to_dashboard(
                self._bot, source_ip, "/api/internal/preload-student", reason
            )
            return web.json_response({"success": False, "error": reason}, status=401)

        try:
            row = json.loads(body)
        except (json.JSONDecodeError, ValueError) as exc:
            return web.json_response(
                {"success": False, "error": f"Invalid JSON: {exc}"}, status=400
            )

        if not isinstance(row, dict):
            return web.json_response(
                {"success": False, "error": "Body must be a JSON object"}, status=400
            )

        success, error = _upsert_single_student(row)
        if not success:
            logger.error("preload-student upsert failed: %s", error)
            return web.json_response({"success": False, "error": error}, status=500)

        logger.info(
            "preload-student upserted: %s <%s>",
            row.get("enrollment_name", "?"),
            row.get("enrollment_email", "?"),
        )
        return web.json_response({"success": True})

    # ── Route registration ─────────────────────────────────────────────────

    def register_routes(self, app: web.Application) -> None:
        """
        Register internal webhook routes on an existing aiohttp app.

        Call this when mounting onto a shared server (e.g. parent_unsubscribe_server).
        """
        app.router.add_post("/api/internal/role-upgrade", self._handle_role_upgrade)
        app.router.add_post("/api/internal/preload-student", self._handle_preload_student)

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def start(self) -> None:
        if self._runner is not None:
            return

        app = web.Application()

        # Mount interest API routes if a shared server is provided.
        if self._interest_api_server is not None:
            self._interest_api_server.register_routes(app)

        self.register_routes(app)

        self._runner = web.AppRunner(app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, host=self.host, port=self.port)
        await self._site.start()
        logger.info(
            "Internal webhook server listening on http://%s:%s "
            "(role-upgrade, preload-student)",
            self.host,
            self.port,
        )

    async def stop(self) -> None:
        if self._runner is None:
            return
        await self._runner.cleanup()
        self._runner = None
        self._site = None
        logger.info("Internal webhook server stopped")

    def stop_sync(self) -> None:
        """Synchronous shutdown for use in finally blocks (mirrors InterestAPIServer pattern)."""
        if self._runner is None:
            return
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.stop())
            else:
                loop.run_until_complete(self.stop())
        except Exception:
            pass
