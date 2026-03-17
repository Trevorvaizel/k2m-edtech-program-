"""
internal_api_server.py â€” Task 7.11: HMAC-authenticated internal webhook endpoints.

DECISION N-03 (Session 4): Apps Script â†’ Railway webhooks are unauthenticated.
This module provides:
  POST /api/internal/role-upgrade    â€” grant @Student role via discord_id
  POST /api/internal/preload-student â€” upsert one student row to PostgreSQL
  POST /api/internal/apps-script-error â€” post Apps Script failures to #facilitator-dashboard
  POST /api/internal/activation-dm â€” send activation DM(s) to activated student

All endpoints require a valid X-K2M-Signature header (HMAC-SHA256).
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

# â”€â”€ Discord REST constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DISCORD_API = "https://discord.com/api/v10"
ROLE_UPGRADE_DM_TEXT = (
    "#welcome-lounge served its purpose - your full access is now unlocked!\n\n"
    "Continue in #welcome-and-rules and your week channels.\n\n"
    "- KIRA"
)


def _discord_headers() -> dict:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    return {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }


def _dashboard_channel_id() -> str:
    """
    Resolve configured facilitator dashboard channel id.
    """
    channel_id = os.getenv("FACILITATOR_DASHBOARD_CHANNEL_ID", "").strip()
    if not channel_id:
        channel_id = os.getenv("CHANNEL_FACILITATOR_DASHBOARD", "").strip()
    return channel_id


def _first_name(name: str) -> str:
    clean = (name or "").strip()
    if not clean:
        return "there"
    return clean.split()[0]


def _build_activation_dm_messages(
    *,
    enrollment_name: str,
    cluster_id: str = "",
    first_session_date: str = "",
    week1_start_date: str = "",
) -> tuple[str, str]:
    """
    Task 7.10 / Decision N-25 activation DM redesign.
    First message is celebration + one clear action.
    Second message carries stops 1-3 intro.
    """
    first_name = _first_name(enrollment_name)

    detail_lines = []
    if cluster_id:
        detail_lines.append(f"Your cluster: {cluster_id}")
    if first_session_date:
        detail_lines.append(f"First live session: {first_session_date} at 6 PM EAT")
    if week1_start_date:
        detail_lines.append(f"Week 1 begins: {week1_start_date}")
    details_block = ("\n" + "\n".join(detail_lines) + "\n") if detail_lines else ""

    message_1 = (
        f"{first_name} - you're in.\n\n"
        "Step 4 complete - you're in!\n\n"
        "Welcome to K2M Cohort 1.\n\n"
        "You just did something most people talk about and never do.\n"
        "You paid for it, figured out Discord, and showed up.\n"
        "That already says something.\n\n"
        "Your channels just unlocked. Explore at your own pace.\n\n"
        "When you're ready to start: go to #welcome-and-rules.\n"
        "I'll guide you through the rest."
        f"{details_block}"
        "I'll remind you before each.\n\n"
        "- KIRA"
    )

    message_2 = (
        "Next message: your stop-by-stop onboarding path.\n\n"
        "Stop 1 - Welcome and orientation\n"
        "Stop 2 - Channel navigation\n"
        "Stop 3 - First /frame walkthrough\n\n"
        "After each stop, reply \"done\" and I will guide you forward.\n\n"
        "- KIRA"
    )
    return message_1, message_2


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


async def _remove_guest_role(discord_id: str) -> tuple[bool, str]:
    """
    DELETE /guilds/{guild_id}/members/{user_id}/roles/{role_id} to remove @Guest.
    Returns (success, error_message).
    """
    guild_id = os.getenv("DISCORD_GUILD_ID", "").strip()
    role_id = os.getenv("GUEST_ROLE_ID", "").strip()
    if not guild_id or not role_id:
        return False, "DISCORD_GUILD_ID or GUEST_ROLE_ID not configured"

    url = f"{DISCORD_API}/guilds/{guild_id}/members/{discord_id}/roles/{role_id}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.delete(url, headers=_discord_headers())

        if resp.status_code == 204:
            return True, ""
        return False, f"Discord returned {resp.status_code}: {resp.text[:200]}"
    except Exception as exc:
        return False, f"Discord REST error: {exc}"


async def _send_role_upgrade_dm(bot, discord_id: str) -> tuple[bool, str]:
    """
    Send post-upgrade DM after @Guest -> @Student transition.
    Returns (success, error_message).
    """
    if bot is None:
        return False, "Bot unavailable"

    try:
        user = await bot.fetch_user(int(discord_id))
        await user.send(ROLE_UPGRADE_DM_TEXT)
        return True, ""
    except Exception as exc:
        return False, f"DM delivery failed: {exc}"


async def _lock_welcome_lounge_for_member(bot, discord_id: str) -> tuple[bool, str]:
    """
    Fallback boundary guard:
    apply a member-specific send deny in #welcome-lounge when @Guest removal fails.
    """
    if bot is None:
        return False, "Bot unavailable"

    channel_id = os.getenv("CHANNEL_WELCOME_LOUNGE", "").strip()
    guild_id = os.getenv("DISCORD_GUILD_ID", "").strip()
    if not channel_id or not guild_id or not channel_id.isdigit() or not guild_id.isdigit():
        return False, "CHANNEL_WELCOME_LOUNGE or DISCORD_GUILD_ID not configured"

    try:
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            channel = await bot.fetch_channel(int(channel_id))
        if channel is None or not hasattr(channel, "set_permissions"):
            return False, "welcome lounge channel unavailable"

        guild = bot.get_guild(int(guild_id))
        member = guild.get_member(int(discord_id)) if guild is not None else None
        if member is None and guild is not None and hasattr(guild, "fetch_member"):
            try:
                member = await guild.fetch_member(int(discord_id))
            except Exception:
                member = None
        if member is None:
            return False, "member not found in guild"

        await channel.set_permissions(
            member,
            read_messages=True,
            send_messages=False,
            read_message_history=True,
            reason="Task 7.12 fallback: lock lounge posting when @Guest removal fails",
        )
        return True, ""
    except Exception as exc:
        return False, f"Welcome lounge member lock failed: {exc}"


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


async def _log_401_to_dashboard(
    bot,
    source_ip: str,
    endpoint: str,
    reason: str,
    user_agent: str = "",
) -> None:
    """Post a 401 alert to #facilitator-dashboard (best-effort)."""
    try:
        channel_id = _dashboard_channel_id()
        if not bot or not channel_id:
            logger.warning(
                "401 on %s from %s (%s) ua=%s â€” dashboard channel not configured",
                endpoint, source_ip, reason, (user_agent or "-"),
            )
            return
        channel = bot.get_channel(int(channel_id))
        if channel is None:
            channel = await bot.fetch_channel(int(channel_id))
        ua_preview = (user_agent or "").strip()
        if len(ua_preview) > 120:
            ua_preview = ua_preview[:117] + "..."
        await channel.send(
            f"ðŸš¨ **401 Unauthorized webhook** on `{endpoint}`\n"
            f"Source IP: `{source_ip}`\n"
            f"Reason: {reason}\n"
            f"User-Agent: `{ua_preview or 'unknown'}`"
        )
    except Exception as exc:
        logger.error("Failed to log 401 to dashboard: %s", exc)


async def _log_apps_script_error_to_dashboard(
    bot,
    *,
    function_name: str,
    error_message: str,
    source_ip: str,
    payload: Optional[dict] = None,
) -> bool:
    """
    Post an Apps Script runtime error to #facilitator-dashboard.
    """
    try:
        channel_id = _dashboard_channel_id()
        if not bot or not channel_id:
            logger.warning(
                "Apps Script error from %s could not be posted: dashboard channel not configured",
                source_ip,
            )
            return False

        channel = bot.get_channel(int(channel_id))
        if channel is None:
            channel = await bot.fetch_channel(int(channel_id))

        error_preview = (error_message or "").strip()[:1200] or "Unknown error"
        text = (
            "ðŸš¨ **Apps Script error**\n"
            f"Function: `{function_name}`\n"
            f"Error: {error_preview}\n"
            f"Source IP: `{source_ip}`"
        )

        extra_type = (payload or {}).get("type")
        if extra_type:
            text += f"\nType: `{extra_type}`"

        await channel.send(text)
        return True
    except Exception as exc:
        logger.error("Failed to log Apps Script error to dashboard: %s", exc, exc_info=True)
        return False


class InternalWebhookServer:
    """
    Lightweight aiohttp server for HMAC-authenticated Apps Script â†’ bot webhooks.

    Endpoints:
      POST /api/internal/role-upgrade    â€” body: {"discord_id": "..."}
      POST /api/internal/preload-student â€” body: {<student row fields>}
      POST /api/internal/apps-script-error â€” body: {"type":"apps_script_error","fn":"...","error":"..."}
      POST /api/internal/activation-dm â€” body: {"discord_id":"...","enrollment_name":"..."}
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

    # â”€â”€ Handlers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def _handle_role_upgrade(self, request: web.Request) -> web.Response:
        """
        POST /api/internal/role-upgrade
        Body: {"discord_id": "<numeric Discord user ID>"}
        Header: X-K2M-Signature: sha256=<hmac>
        """
        source_ip = get_client_ip(request)
        user_agent = str(request.headers.get("User-Agent", "")).strip()
        ok, body, reason = await require_webhook_signature(request)
        if not ok:
            logger.warning("401 role-upgrade from %s: %s", source_ip, reason)
            await _log_401_to_dashboard(
                self._bot,
                source_ip,
                "/api/internal/role-upgrade",
                reason,
                user_agent=user_agent,
            )
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

        guest_role_removed = None
        lounge_member_lock_applied = None
        if os.getenv("GUEST_ROLE_ID", "").strip():
            guest_role_removed, guest_error = await _remove_guest_role(discord_id)
            if not guest_role_removed:
                logger.warning(
                    "role-upgrade could not remove @Guest for %s: %s",
                    discord_id,
                    guest_error,
                )
                lounge_member_lock_applied, lounge_error = await _lock_welcome_lounge_for_member(
                    self._bot,
                    discord_id,
                )
                if not lounge_member_lock_applied:
                    logger.warning(
                        "role-upgrade fallback could not lock welcome-lounge for %s: %s",
                        discord_id,
                        lounge_error,
                    )

        dm_sent, dm_error = await _send_role_upgrade_dm(self._bot, discord_id)
        if not dm_sent:
            logger.warning(
                "role-upgrade post-DM failed for %s: %s",
                discord_id,
                dm_error,
            )

        logger.info(
            "role-upgrade granted @Student to discord_id=%s (guest_removed=%s, lounge_lock=%s, dm_sent=%s)",
            discord_id,
            guest_role_removed,
            lounge_member_lock_applied,
            dm_sent,
        )
        return web.json_response(
            {
                "success": True,
                "discord_id": discord_id,
                "guest_role_removed": guest_role_removed,
                "welcome_lounge_member_lock_applied": lounge_member_lock_applied,
                "post_upgrade_dm_sent": dm_sent,
            }
        )

    async def _handle_preload_student(self, request: web.Request) -> web.Response:
        """
        POST /api/internal/preload-student
        Body: {<student row fields>}
        Header: X-K2M-Signature: sha256=<hmac>
        """
        source_ip = get_client_ip(request)
        user_agent = str(request.headers.get("User-Agent", "")).strip()
        ok, body, reason = await require_webhook_signature(request)
        if not ok:
            logger.warning("401 preload-student from %s: %s", source_ip, reason)
            await _log_401_to_dashboard(
                self._bot,
                source_ip,
                "/api/internal/preload-student",
                reason,
                user_agent=user_agent,
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

    async def _handle_apps_script_error(self, request: web.Request) -> web.Response:
        """
        POST /api/internal/apps-script-error
        Body: {"type":"apps_script_error","fn":"activateStudent","error":"message"}
        Header: X-K2M-Signature: sha256=<hmac>
        """
        source_ip = get_client_ip(request)
        user_agent = str(request.headers.get("User-Agent", "")).strip()
        ok, body, reason = await require_webhook_signature(request)
        if not ok:
            logger.warning("401 apps-script-error from %s: %s", source_ip, reason)
            await _log_401_to_dashboard(
                self._bot,
                source_ip,
                "/api/internal/apps-script-error",
                reason,
                user_agent=user_agent,
            )
            return web.json_response({"success": False, "error": reason}, status=401)

        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, ValueError) as exc:
            return web.json_response(
                {"success": False, "error": f"Invalid JSON: {exc}"},
                status=400,
            )

        if not isinstance(payload, dict):
            return web.json_response(
                {"success": False, "error": "Body must be a JSON object"},
                status=400,
            )

        event_type = str(payload.get("type", "")).strip().lower()
        function_name = (
            str(payload.get("fn") or payload.get("function_name") or "").strip()
        )
        error_message = str(payload.get("error") or payload.get("message") or "").strip()

        if event_type and event_type != "apps_script_error":
            return web.json_response(
                {
                    "success": False,
                    "error": "type must be 'apps_script_error' when provided",
                },
                status=400,
            )
        if not function_name:
            return web.json_response(
                {"success": False, "error": "Missing function name (fn)"},
                status=400,
            )
        if not error_message:
            return web.json_response(
                {"success": False, "error": "Missing error message (error)"},
                status=400,
            )

        dashboard_posted = await _log_apps_script_error_to_dashboard(
            self._bot,
            function_name=function_name,
            error_message=error_message,
            source_ip=source_ip,
            payload=payload,
        )

        logger.error(
            "apps-script-error: fn=%s source=%s error=%s",
            function_name,
            source_ip,
            error_message,
        )
        return web.json_response(
            {
                "success": True,
                "dashboard_posted": bool(dashboard_posted),
            }
        )

    async def _handle_activation_dm(self, request: web.Request) -> web.Response:
        """
        POST /api/internal/activation-dm
        Body: {
          "discord_id": "<numeric Discord user ID>",
          "enrollment_name": "<student name>",
          "cluster_id": "<optional cluster label>",
          "first_session_date": "<optional date>",
          "week1_start_date": "<optional date>"
        }
        Header: X-K2M-Signature: sha256=<hmac>
        """
        source_ip = get_client_ip(request)
        user_agent = str(request.headers.get("User-Agent", "")).strip()
        ok, body, reason = await require_webhook_signature(request)
        if not ok:
            logger.warning("401 activation-dm from %s: %s", source_ip, reason)
            await _log_401_to_dashboard(
                self._bot,
                source_ip,
                "/api/internal/activation-dm",
                reason,
                user_agent=user_agent,
            )
            return web.json_response({"success": False, "error": reason}, status=401)

        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, ValueError) as exc:
            return web.json_response(
                {"success": False, "error": f"Invalid JSON: {exc}"},
                status=400,
            )

        if not isinstance(payload, dict):
            return web.json_response(
                {"success": False, "error": "Body must be a JSON object"},
                status=400,
            )

        discord_id = str(payload.get("discord_id", "")).strip()
        if not discord_id or not discord_id.isdigit():
            return web.json_response(
                {"success": False, "error": "discord_id must be a numeric Discord user ID"},
                status=400,
            )
        if not self._bot:
            return web.json_response(
                {"success": False, "error": "Bot is not available for DM delivery"},
                status=503,
            )

        enrollment_name = str(payload.get("enrollment_name") or payload.get("name") or "").strip()
        cluster_id = str(payload.get("cluster_id") or "").strip()
        first_session_date = str(
            payload.get("first_session_date")
            or os.getenv("COHORT_1_FIRST_SESSION_DATE", "")
        ).strip()
        week1_start_date = str(
            payload.get("week1_start_date")
            or os.getenv("COHORT_1_START_DATE", "")
        ).strip()

        message_1, message_2 = _build_activation_dm_messages(
            enrollment_name=enrollment_name,
            cluster_id=cluster_id,
            first_session_date=first_session_date,
            week1_start_date=week1_start_date,
        )

        try:
            user = await self._bot.fetch_user(int(discord_id))
            await user.send(message_1)
            await user.send(message_2)
        except Exception as exc:
            logger.error("activation-dm failed for %s: %s", discord_id, exc, exc_info=True)
            return web.json_response(
                {"success": False, "error": f"Activation DM failed: {exc}"},
                status=500,
            )

        logger.info("Task 7.10: activation DM sent to discord_id=%s", discord_id)
        return web.json_response({"success": True, "discord_id": discord_id})

    # â”€â”€ Route registration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def register_routes(self, app: web.Application) -> None:
        """
        Register internal webhook routes on an existing aiohttp app.

        Call this when mounting onto a shared server (e.g. parent_unsubscribe_server).
        """
        app.router.add_post("/api/internal/role-upgrade", self._handle_role_upgrade)
        app.router.add_post("/api/internal/preload-student", self._handle_preload_student)
        app.router.add_post("/api/internal/apps-script-error", self._handle_apps_script_error)
        app.router.add_post("/api/internal/activation-dm", self._handle_activation_dm)

    # â”€â”€ Lifecycle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
            "(role-upgrade, preload-student, apps-script-error, activation-dm)",
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
