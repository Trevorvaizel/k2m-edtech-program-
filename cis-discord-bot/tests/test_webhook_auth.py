"""
test_webhook_auth.py — Task 7.11: HMAC-SHA256 webhook authentication tests.

Coverage:
  - validate_signature: valid, missing header, wrong prefix, tampered payload
  - /api/internal/role-upgrade: valid sig → 200, invalid sig → 401, bad discord_id → 400
  - /api/internal/preload-student: valid sig → 200, invalid sig → 401, bad body → 400
  - 401 dashboard logging
  - get_client_ip: forwarded header + direct
  - _grant_student_role: success 204, non-204, missing env vars
"""

from __future__ import annotations

import hashlib
import hmac
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Secret used by all tests — plain string, matches how WEBHOOK_SECRET env var is set.
SECRET_STR = "test-webhook-secret-string"
SECRET_BYTES = SECRET_STR.encode()  # what _get_secret() returns for this env value


def _sign(payload: bytes, key: bytes = SECRET_BYTES) -> str:
    """Produce 'sha256=<hex>' signature matching the server's validation logic."""
    sig = hmac.new(key, payload, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


def _make_request(
    body: bytes,
    headers: dict | None = None,
    remote: str = "1.2.3.4",
) -> MagicMock:
    """Build a mock aiohttp web.Request that supports read() and headers."""
    req = MagicMock()
    req.remote = remote
    req.headers = headers or {}

    async def _read():
        return body

    req.read = _read
    return req


# ── webhook_auth.validate_signature ───────────────────────────────────────

class TestValidateSignature:
    def _call(self, body: bytes, header: str | None, secret: str = SECRET_STR):
        from cis_controller.webhook_auth import validate_signature
        with patch.dict("os.environ", {"WEBHOOK_SECRET": secret}):
            return validate_signature(body, header)

    def test_valid_signature_passes(self):
        body = b'{"discord_id":"123456"}'
        header = _sign(body)
        ok, reason = self._call(body, header)
        assert ok is True
        assert reason == ""

    def test_missing_header_rejected(self):
        body = b'{"discord_id":"123456"}'
        ok, reason = self._call(body, None)
        assert ok is False
        assert "Missing" in reason

    def test_empty_header_rejected(self):
        body = b'{"discord_id":"123456"}'
        ok, reason = self._call(body, "")
        assert ok is False

    def test_wrong_prefix_rejected(self):
        body = b'{"discord_id":"123456"}'
        raw_hex = hmac.new(SECRET_BYTES, body, hashlib.sha256).hexdigest()
        ok, reason = self._call(body, f"md5={raw_hex}")
        assert ok is False
        assert "sha256=" in reason

    def test_tampered_payload_rejected(self):
        original = b'{"discord_id":"123456"}'
        tampered = b'{"discord_id":"999999"}'
        header = _sign(original)
        ok, reason = self._call(tampered, header)
        assert ok is False
        assert "mismatch" in reason.lower()

    def test_missing_secret_env_rejected(self):
        from cis_controller.webhook_auth import validate_signature
        with patch.dict("os.environ", {"WEBHOOK_SECRET": ""}):
            ok, reason = validate_signature(b"payload", "sha256=abc")
        assert ok is False
        assert "WEBHOOK_SECRET" in reason

    def test_different_secret_rejected(self):
        body = b'{"test": true}'
        header = _sign(body, key=b"wrong-secret")
        ok, reason = self._call(body, header)
        assert ok is False


# ── get_client_ip ──────────────────────────────────────────────────────────

class TestGetClientIp:
    def test_forwarded_header_used_first(self):
        from cis_controller.webhook_auth import get_client_ip
        req = MagicMock()
        req.headers = {"X-Forwarded-For": "1.2.3.4, 5.6.7.8"}
        req.remote = "10.0.0.1"
        assert get_client_ip(req) == "1.2.3.4"

    def test_falls_back_to_remote(self):
        from cis_controller.webhook_auth import get_client_ip
        req = MagicMock()
        req.headers = {}
        req.remote = "10.0.0.1"
        assert get_client_ip(req) == "10.0.0.1"

    def test_unknown_when_no_ip(self):
        from cis_controller.webhook_auth import get_client_ip
        req = MagicMock()
        req.headers = {}
        req.remote = None
        assert get_client_ip(req) == "unknown"


# ── /api/internal/role-upgrade ────────────────────────────────────────────

class TestRoleUpgradeEndpoint:
    def _server(self):
        from cis_controller.internal_api_server import InternalWebhookServer
        return InternalWebhookServer(bot=MagicMock())

    @pytest.mark.asyncio
    async def test_valid_signature_calls_discord(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"discord_id": "123456789012345678"}).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        with patch(
            "cis_controller.internal_api_server._grant_student_role",
            new_callable=AsyncMock,
            return_value=(True, ""),
        ) as mock_grant:
            resp = await self._server()._handle_role_upgrade(req)

        assert resp.status == 200
        payload = json.loads(resp.body)
        assert payload["success"] is True
        mock_grant.assert_awaited_once_with("123456789012345678")

    @pytest.mark.asyncio
    async def test_role_upgrade_sends_post_upgrade_dm(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"discord_id": "123456789012345678"}).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        from cis_controller.internal_api_server import InternalWebhookServer

        bot = MagicMock()
        user = MagicMock()
        user.send = AsyncMock()
        bot.fetch_user = AsyncMock(return_value=user)
        server = InternalWebhookServer(bot=bot)

        with patch(
            "cis_controller.internal_api_server._grant_student_role",
            new_callable=AsyncMock,
            return_value=(True, ""),
        ):
            resp = await server._handle_role_upgrade(req)

        assert resp.status == 200
        payload = json.loads(resp.body)
        assert payload["post_upgrade_dm_sent"] is True
        user.send.assert_awaited_once()
        sent_text = user.send.await_args_list[0].args[0]
        assert "#welcome-lounge served its purpose" in sent_text

    @pytest.mark.asyncio
    async def test_role_upgrade_attempts_guest_role_removal_when_configured(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        monkeypatch.setenv("GUEST_ROLE_ID", "444555666")
        body = json.dumps({"discord_id": "123456789012345678"}).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        with patch(
            "cis_controller.internal_api_server._grant_student_role",
            new_callable=AsyncMock,
            return_value=(True, ""),
        ), patch(
            "cis_controller.internal_api_server._remove_guest_role",
            new_callable=AsyncMock,
            return_value=(True, ""),
        ) as mock_remove_guest, patch(
            "cis_controller.internal_api_server._send_role_upgrade_dm",
            new_callable=AsyncMock,
            return_value=(True, ""),
        ):
            resp = await self._server()._handle_role_upgrade(req)

        assert resp.status == 200
        mock_remove_guest.assert_awaited_once_with("123456789012345678")

    @pytest.mark.asyncio
    async def test_role_upgrade_applies_welcome_lounge_lock_when_guest_removal_fails(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        monkeypatch.setenv("GUEST_ROLE_ID", "444555666")
        body = json.dumps({"discord_id": "123456789012345678"}).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        from cis_controller.internal_api_server import InternalWebhookServer

        server = InternalWebhookServer(bot=MagicMock())

        with patch(
            "cis_controller.internal_api_server._grant_student_role",
            new_callable=AsyncMock,
            return_value=(True, ""),
        ), patch(
            "cis_controller.internal_api_server._remove_guest_role",
            new_callable=AsyncMock,
            return_value=(False, "remove failed"),
        ), patch(
            "cis_controller.internal_api_server._lock_welcome_lounge_for_member",
            new_callable=AsyncMock,
            return_value=(True, ""),
        ) as mock_lock, patch(
            "cis_controller.internal_api_server._send_role_upgrade_dm",
            new_callable=AsyncMock,
            return_value=(True, ""),
        ):
            resp = await server._handle_role_upgrade(req)

        assert resp.status == 200
        payload = json.loads(resp.body)
        assert payload["guest_role_removed"] is False
        assert payload["welcome_lounge_member_lock_applied"] is True
        mock_lock.assert_awaited_once_with(server._bot, "123456789012345678")

    @pytest.mark.asyncio
    async def test_missing_signature_returns_401(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"discord_id": "123456789012345678"}).encode()
        req = _make_request(body, {})

        with patch("cis_controller.internal_api_server._log_401_to_dashboard", new_callable=AsyncMock):
            resp = await self._server()._handle_role_upgrade(req)

        assert resp.status == 401
        assert json.loads(resp.body)["success"] is False

    @pytest.mark.asyncio
    async def test_tampered_payload_returns_401(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        original = json.dumps({"discord_id": "123456789012345678"}).encode()
        tampered = json.dumps({"discord_id": "999999999999999999"}).encode()
        req = _make_request(tampered, {"X-K2M-Signature": _sign(original)})

        with patch("cis_controller.internal_api_server._log_401_to_dashboard", new_callable=AsyncMock):
            resp = await self._server()._handle_role_upgrade(req)

        assert resp.status == 401

    @pytest.mark.asyncio
    async def test_non_numeric_discord_id_returns_400(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"discord_id": "not-a-number"}).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        resp = await self._server()._handle_role_upgrade(req)

        assert resp.status == 400
        assert "numeric" in json.loads(resp.body)["error"]

    @pytest.mark.asyncio
    async def test_missing_discord_id_returns_400(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"wrong_key": "value"}).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        resp = await self._server()._handle_role_upgrade(req)

        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_discord_api_failure_returns_500(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"discord_id": "123456789012345678"}).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        with patch(
            "cis_controller.internal_api_server._grant_student_role",
            new_callable=AsyncMock,
            return_value=(False, "Discord returned 404"),
        ):
            resp = await self._server()._handle_role_upgrade(req)

        assert resp.status == 500
        assert json.loads(resp.body)["success"] is False

    @pytest.mark.asyncio
    async def test_401_logs_dashboard_with_endpoint_name(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"discord_id": "123456789012345678"}).encode()
        req = _make_request(body, {}, remote="9.8.7.6")

        with patch(
            "cis_controller.internal_api_server._log_401_to_dashboard",
            new_callable=AsyncMock,
        ) as mock_log:
            await self._server()._handle_role_upgrade(req)

        mock_log.assert_awaited_once()
        call_args = mock_log.call_args_list[0].args
        assert any("/api/internal/role-upgrade" in str(a) for a in call_args)


# ── /api/internal/preload-student ─────────────────────────────────────────

class TestPreloadStudentEndpoint:
    def _server(self):
        from cis_controller.internal_api_server import InternalWebhookServer
        return InternalWebhookServer(bot=MagicMock())

    def _row(self) -> dict:
        return {
            "enrollment_email": "test@example.com",
            "enrollment_name": "Test Student",
            "last_name": "Student",
            "invite_code": "abc123",
            "discord_id": "__pending__test@example.com",
            "cohort_id": "cohort-1",
            "start_date": "2026-04-01",
            "enrollment_status": "enrolled",
            "payment_status": "Confirmed",
        }

    @pytest.mark.asyncio
    async def test_valid_signature_upserts_student(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        row = self._row()
        body = json.dumps(row).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        with patch(
            "cis_controller.internal_api_server._upsert_single_student",
            return_value=(True, ""),
        ) as mock_upsert:
            resp = await self._server()._handle_preload_student(req)

        assert resp.status == 200
        assert json.loads(resp.body)["success"] is True
        mock_upsert.assert_called_once_with(row)

    @pytest.mark.asyncio
    async def test_missing_signature_returns_401(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps(self._row()).encode()
        req = _make_request(body, {})

        with patch("cis_controller.internal_api_server._log_401_to_dashboard", new_callable=AsyncMock):
            resp = await self._server()._handle_preload_student(req)

        assert resp.status == 401

    @pytest.mark.asyncio
    async def test_tampered_payload_returns_401(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        original = json.dumps(self._row()).encode()
        tampered = json.dumps({"enrollment_email": "hacker@evil.com"}).encode()
        req = _make_request(tampered, {"X-K2M-Signature": _sign(original)})

        with patch("cis_controller.internal_api_server._log_401_to_dashboard", new_callable=AsyncMock):
            resp = await self._server()._handle_preload_student(req)

        assert resp.status == 401

    @pytest.mark.asyncio
    async def test_non_dict_body_returns_400(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps(["list", "not", "dict"]).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        resp = await self._server()._handle_preload_student(req)

        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_invalid_json_returns_400(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = b"not valid json {"
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        resp = await self._server()._handle_preload_student(req)

        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_db_failure_returns_500(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps(self._row()).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        with patch(
            "cis_controller.internal_api_server._upsert_single_student",
            return_value=(False, "DB connection error"),
        ):
            resp = await self._server()._handle_preload_student(req)

        assert resp.status == 500

    @pytest.mark.asyncio
    async def test_401_logs_dashboard_with_endpoint_name(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps(self._row()).encode()
        req = _make_request(body, {}, remote="9.8.7.6")

        with patch(
            "cis_controller.internal_api_server._log_401_to_dashboard",
            new_callable=AsyncMock,
        ) as mock_log:
            await self._server()._handle_preload_student(req)

        mock_log.assert_awaited_once()
        call_args = mock_log.call_args_list[0].args
        assert any("/api/internal/preload-student" in str(a) for a in call_args)


# ── /api/internal/apps-script-error ───────────────────────────────────────

class TestAppsScriptErrorEndpoint:
    def _server(self):
        from cis_controller.internal_api_server import InternalWebhookServer
        return InternalWebhookServer(bot=MagicMock())

    def _payload(self) -> dict:
        return {
            "type": "apps_script_error",
            "fn": "activateStudent",
            "error": "ReferenceError: preloadToDatabase is not defined",
        }

    @pytest.mark.asyncio
    async def test_valid_signature_posts_apps_script_error(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        payload = self._payload()
        body = json.dumps(payload).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)}, remote="10.20.30.40")

        with patch(
            "cis_controller.internal_api_server._log_apps_script_error_to_dashboard",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_log:
            resp = await self._server()._handle_apps_script_error(req)

        assert resp.status == 200
        response_payload = json.loads(resp.body)
        assert response_payload["success"] is True
        assert response_payload["dashboard_posted"] is True

        mock_log.assert_awaited_once()
        kwargs = mock_log.call_args.kwargs
        assert kwargs["function_name"] == "activateStudent"
        assert "ReferenceError" in kwargs["error_message"]
        assert kwargs["source_ip"] == "10.20.30.40"

    @pytest.mark.asyncio
    async def test_missing_signature_returns_401(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps(self._payload()).encode()
        req = _make_request(body, {}, remote="9.8.7.6")

        with patch(
            "cis_controller.internal_api_server._log_401_to_dashboard",
            new_callable=AsyncMock,
        ) as mock_log:
            resp = await self._server()._handle_apps_script_error(req)

        assert resp.status == 401
        mock_log.assert_awaited_once()
        call_args = mock_log.call_args_list[0].args
        assert any("/api/internal/apps-script-error" in str(a) for a in call_args)

    @pytest.mark.asyncio
    async def test_invalid_type_returns_400(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        payload = self._payload()
        payload["type"] = "unexpected_type"
        body = json.dumps(payload).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        resp = await self._server()._handle_apps_script_error(req)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_missing_function_name_returns_400(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        payload = self._payload()
        payload.pop("fn")
        body = json.dumps(payload).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        resp = await self._server()._handle_apps_script_error(req)
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_missing_error_message_returns_400(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        payload = self._payload()
        payload.pop("error")
        body = json.dumps(payload).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        resp = await self._server()._handle_apps_script_error(req)
        assert resp.status == 400


# ── /api/internal/activation-dm ───────────────────────────────────────────

class TestActivationDmEndpoint:
    def _server(self):
        from cis_controller.internal_api_server import InternalWebhookServer
        bot = MagicMock()
        user = MagicMock()
        user.send = AsyncMock()
        bot.fetch_user = AsyncMock(return_value=user)
        return InternalWebhookServer(bot=bot), bot, user

    @pytest.mark.asyncio
    async def test_valid_signature_sends_two_activation_messages(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        monkeypatch.setenv("COHORT_1_FIRST_SESSION_DATE", "2026-03-18")
        monkeypatch.setenv("COHORT_1_START_DATE", "2026-03-16")
        payload = {
            "discord_id": "123456789012345678",
            "enrollment_name": "Grace Kamau",
        }
        body = json.dumps(payload).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})
        server, bot, user = self._server()

        resp = await server._handle_activation_dm(req)

        assert resp.status == 200
        response_payload = json.loads(resp.body)
        assert response_payload["success"] is True
        bot.fetch_user.assert_awaited_once_with(123456789012345678)
        assert user.send.await_count == 2
        msg_1 = user.send.await_args_list[0].args[0]
        msg_2 = user.send.await_args_list[1].args[0]
        assert "Step 4 complete - you're in!" in msg_1
        assert "First live session: 2026-03-18 at 6 PM EAT" in msg_1
        assert "Stop 1 - Welcome and orientation" in msg_2

    @pytest.mark.asyncio
    async def test_missing_signature_returns_401(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"discord_id": "123456789012345678"}).encode()
        req = _make_request(body, {}, remote="9.8.7.6")
        server, _bot, _user = self._server()

        with patch(
            "cis_controller.internal_api_server._log_401_to_dashboard",
            new_callable=AsyncMock,
        ) as mock_log:
            resp = await server._handle_activation_dm(req)

        assert resp.status == 401
        mock_log.assert_awaited_once()
        call_args = mock_log.call_args_list[0].args
        assert any("/api/internal/activation-dm" in str(a) for a in call_args)

    @pytest.mark.asyncio
    async def test_non_numeric_discord_id_returns_400(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        body = json.dumps({"discord_id": "not-a-number"}).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})
        server, _bot, _user = self._server()

        resp = await server._handle_activation_dm(req)

        assert resp.status == 400
        assert "numeric" in json.loads(resp.body)["error"]

    @pytest.mark.asyncio
    async def test_returns_503_when_bot_unavailable(self, monkeypatch):
        monkeypatch.setenv("WEBHOOK_SECRET", SECRET_STR)
        payload = {"discord_id": "123456789012345678", "enrollment_name": "Grace"}
        body = json.dumps(payload).encode()
        req = _make_request(body, {"X-K2M-Signature": _sign(body)})

        from cis_controller.internal_api_server import InternalWebhookServer

        server = InternalWebhookServer(bot=None)
        resp = await server._handle_activation_dm(req)

        assert resp.status == 503
        assert json.loads(resp.body)["success"] is False


# ── _grant_student_role unit ───────────────────────────────────────────────

class TestGrantStudentRole:
    @pytest.mark.asyncio
    async def test_success_on_204(self, monkeypatch):
        monkeypatch.setenv("DISCORD_GUILD_ID", "111222333")
        monkeypatch.setenv("STUDENT_ROLE_ID", "999888777")
        monkeypatch.setenv("DISCORD_TOKEN", "fake-token")

        from cis_controller.internal_api_server import _grant_student_role

        mock_resp = MagicMock()
        mock_resp.status_code = 204

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.put = AsyncMock(return_value=mock_resp)

        with patch("cis_controller.internal_api_server.httpx.AsyncClient", return_value=mock_client):
            ok, error = await _grant_student_role("123456789")

        assert ok is True
        assert error == ""

    @pytest.mark.asyncio
    async def test_discord_returns_non_204_is_error(self, monkeypatch):
        monkeypatch.setenv("DISCORD_GUILD_ID", "111222333")
        monkeypatch.setenv("STUDENT_ROLE_ID", "999888777")
        monkeypatch.setenv("DISCORD_TOKEN", "fake-token")

        from cis_controller.internal_api_server import _grant_student_role

        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Unknown Member"

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.put = AsyncMock(return_value=mock_resp)

        with patch("cis_controller.internal_api_server.httpx.AsyncClient", return_value=mock_client):
            ok, error = await _grant_student_role("123456789")

        assert ok is False
        assert "404" in error

    @pytest.mark.asyncio
    async def test_missing_env_vars_returns_error(self, monkeypatch):
        monkeypatch.setenv("DISCORD_GUILD_ID", "")
        monkeypatch.setenv("STUDENT_ROLE_ID", "")
        from cis_controller.internal_api_server import _grant_student_role
        ok, error = await _grant_student_role("123456789")
        assert ok is False
        assert "not configured" in error


# ── dashboard logging env compatibility ─────────────────────────────────────

class TestDashboard401Logging:
    @pytest.mark.asyncio
    async def test_uses_channel_facilitator_dashboard_when_specific_id_missing(self, monkeypatch):
        """
        Task 7.11 acceptance requires visible 401 alerts in #facilitator-dashboard.
        Runtime config commonly uses CHANNEL_FACILITATOR_DASHBOARD, so fallback
        must work when FACILITATOR_DASHBOARD_CHANNEL_ID is unset.
        """
        monkeypatch.setenv("FACILITATOR_DASHBOARD_CHANNEL_ID", "")
        monkeypatch.setenv("CHANNEL_FACILITATOR_DASHBOARD", "12345")

        from cis_controller.internal_api_server import _log_401_to_dashboard

        channel = MagicMock()
        channel.send = AsyncMock()

        bot = MagicMock()
        bot.get_channel.return_value = channel
        bot.fetch_channel = AsyncMock(return_value=channel)

        await _log_401_to_dashboard(
            bot=bot,
            source_ip="9.8.7.6",
            endpoint="/api/internal/role-upgrade",
            reason="Missing X-K2M-Signature header",
        )

        bot.get_channel.assert_called_once_with(12345)
        channel.send.assert_awaited_once()
        sent_text = channel.send.await_args.args[0]
        assert "User-Agent:" in sent_text
        assert "unknown" in sent_text

    @pytest.mark.asyncio
    async def test_includes_user_agent_when_provided(self, monkeypatch):
        monkeypatch.setenv("FACILITATOR_DASHBOARD_CHANNEL_ID", "12345")
        monkeypatch.setenv("CHANNEL_FACILITATOR_DASHBOARD", "")

        from cis_controller.internal_api_server import _log_401_to_dashboard

        channel = MagicMock()
        channel.send = AsyncMock()

        bot = MagicMock()
        bot.get_channel.return_value = channel
        bot.fetch_channel = AsyncMock(return_value=channel)

        await _log_401_to_dashboard(
            bot=bot,
            source_ip="9.8.7.6",
            endpoint="/api/internal/role-upgrade",
            reason="Missing X-K2M-Signature header",
            user_agent="Python-urllib/3.12",
        )

        sent_text = channel.send.await_args.args[0]
        assert "Python-urllib/3.12" in sent_text
