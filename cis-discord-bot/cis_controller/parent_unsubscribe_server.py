"""
Lightweight HTTP endpoint for parent unsubscribe links.

This provides GET /parent/unsubscribe?token=... so links sent in parent emails
can be processed immediately without manual database intervention.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from aiohttp import web

from database import get_store

logger = logging.getLogger(__name__)


class ParentUnsubscribeServer:
    """Minimal aiohttp server for parent unsubscribe token handling."""

    def __init__(
        self,
        store: Optional[object] = None,
        interest_api_server: Optional[object] = None,
        internal_webhook_server: Optional[object] = None,
        host: str = "0.0.0.0",
        port: int = 8080,
        path: str = "/parent/unsubscribe",
        health_probe_timeout_seconds: float = 5.0,
    ):
        self.store = store or get_store()
        self.interest_api_server = interest_api_server
        self.internal_webhook_server = internal_webhook_server  # Task 7.11
        self.host = host
        self.port = port
        self.path = path
        self.health_probe_timeout_seconds = max(
            0.1, float(health_probe_timeout_seconds)
        )
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.BaseSite] = None

    def _check_db_connectivity(self) -> tuple[bool, str]:
        """
        Health probe for the runtime store.

        Prefers PostgreSQL native connectivity checks when available, then falls
        back to a lightweight SELECT 1 on the underlying SQLite connection.
        """
        try:
            if self.store is None:
                return False, "store_not_initialized"

            if hasattr(self.store, "check_pg_connectivity"):
                ok = bool(self.store.check_pg_connectivity())
                return ok, "postgresql"

            conn = getattr(self.store, "conn", None) or getattr(self.store, "db", None)
            if conn is None or not hasattr(conn, "execute"):
                return False, "store_connection_unavailable"

            conn.execute("SELECT 1")
            return True, "sqlite"
        except Exception as exc:
            logger.error("Health DB check failed: %s", exc, exc_info=True)
            return False, str(exc)

    def _check_discord_connectivity(self) -> tuple[bool, str]:
        """
        Health probe for Discord connectivity.
        """
        try:
            bot = None
            if self.internal_webhook_server is not None:
                bot = getattr(self.internal_webhook_server, "_bot", None)
            if bot is None and self.interest_api_server is not None:
                bot = getattr(self.interest_api_server, "_bot", None)
            if bot is None:
                return False, "bot_not_available"

            return (True, "ready") if bot.is_ready() else (False, "not_ready")
        except Exception as exc:
            logger.error("Health Discord check failed: %s", exc, exc_info=True)
            return False, str(exc)

    async def _handle_health(self, request: web.Request) -> web.Response:
        """
        Task 7.8: Railway health endpoint.

        Railway startup probes require a 2xx liveness response to keep the
        deployment alive. We still expose dependency readiness via payload
        fields (`status`, `db`, `discord`) so degraded state is observable.
        """
        try:
            db_ok, db_probe = await asyncio.wait_for(
                asyncio.to_thread(self._check_db_connectivity),
                timeout=self.health_probe_timeout_seconds,
            )
        except asyncio.TimeoutError:
            db_ok = False
            db_probe = f"timeout_after_{self.health_probe_timeout_seconds:g}s"
            logger.error(
                "Health DB check timed out after %.2fs",
                self.health_probe_timeout_seconds,
            )
        discord_ok, discord_probe = self._check_discord_connectivity()
        healthy = db_ok and discord_ok

        payload = {
            "status": "healthy" if healthy else "degraded",
            "db": "connected" if db_ok else "disconnected",
            "discord": "connected" if discord_ok else "disconnected",
            "details": {
                "db_probe": db_probe,
                "discord_probe": discord_probe,
            },
            "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        return web.json_response(payload, status=200)

    async def _handle_unsubscribe(self, request: web.Request) -> web.Response:
        token = (request.query.get("token") or "").strip()
        if not token:
            return web.Response(
                text="<h3>Invalid unsubscribe link</h3><p>Missing token.</p>",
                content_type="text/html",
                status=400,
            )

        revoked = self.store.revoke_parent_consent_by_token(token)
        if revoked:
            return web.Response(
                text=(
                    "<h3>Unsubscribed successfully</h3>"
                    "<p>You will no longer receive K2M parent emails for this student.</p>"
                ),
                content_type="text/html",
                status=200,
            )

        return web.Response(
            text="<h3>Link expired or invalid</h3><p>No active subscription matched this token.</p>",
            content_type="text/html",
            status=404,
        )

    async def start(self) -> None:
        """Start the unsubscribe HTTP server."""
        if self._runner is not None:
            return

        app = web.Application()
        app.router.add_get("/health", self._handle_health)
        app.router.add_get(self.path, self._handle_unsubscribe)
        if self.interest_api_server is not None:
            if hasattr(self.interest_api_server, "register_routes"):
                self.interest_api_server.register_routes(app)
                logger.info(
                    "Enrollment API mounted on parent unsubscribe server "
                    "at /api/interest, /api/enroll, /api/mpesa-submit"
                )
            else:
                app.router.add_options("/api/interest", self.interest_api_server._handle_cors)
                app.router.add_post("/api/interest", self.interest_api_server._handle_interest)
                logger.info("Interest API mounted on parent unsubscribe server at /api/interest")

        # Task 7.11: mount HMAC-authenticated internal webhook routes on the same port
        if self.internal_webhook_server is not None:
            if hasattr(self.internal_webhook_server, "register_routes"):
                self.internal_webhook_server.register_routes(app)
                logger.info(
                    "Internal webhook API mounted on parent unsubscribe server "
                    "at /api/internal/role-upgrade, /api/internal/preload-student, /api/internal/apps-script-error"
                )
        self._runner = web.AppRunner(app)
        await self._runner.setup()

        self._site = web.TCPSite(self._runner, host=self.host, port=self.port)
        await self._site.start()
        logger.info(
            "Parent unsubscribe server listening on http://%s:%s%s",
            self.host,
            self.port,
            self.path,
        )

    async def stop(self) -> None:
        """Stop the unsubscribe HTTP server."""
        if self._runner is None:
            return
        await self._runner.cleanup()
        self._runner = None
        self._site = None
        logger.info("Parent unsubscribe server stopped")

    def stop_sync(self) -> None:
        """Best-effort sync-safe stop helper for process shutdown paths."""
        if self._runner is None:
            return
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.stop())
            else:
                loop.run_until_complete(self.stop())
        except Exception:
            # Last-resort shutdown path should never crash process exit.
            pass
