"""
Lightweight HTTP endpoint for parent unsubscribe links.

This provides GET /parent/unsubscribe?token=... so links sent in parent emails
can be processed immediately without manual database intervention.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from aiohttp import web

from database import get_store

logger = logging.getLogger(__name__)


class ParentUnsubscribeServer:
    """Minimal aiohttp server for parent unsubscribe token handling."""

    def __init__(
        self,
        store: Optional[StudentStateStore] = None,
        interest_api_server: Optional[object] = None,
        internal_webhook_server: Optional[object] = None,
        host: str = "0.0.0.0",
        port: int = 8080,
        path: str = "/parent/unsubscribe",
    ):
        self.store = store or get_store()
        self.interest_api_server = interest_api_server
        self.internal_webhook_server = internal_webhook_server  # Task 7.11
        self.host = host
        self.port = port
        self.path = path
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.BaseSite] = None

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
                    "at /api/internal/role-upgrade, /api/internal/preload-student"
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

