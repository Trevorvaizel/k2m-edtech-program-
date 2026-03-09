"""
webhook_auth.py — Task 7.11: HMAC-SHA256 signature validation for Apps Script → bot webhooks.

DECISION N-03 (Session 4): All inbound Apps Script webhooks must be authenticated
to prevent arbitrary role upgrades via URL discovery.

Protocol:
  Apps Script computes:
    signature = Utilities.computeHmacSha256Signature(payload_json, WEBHOOK_SECRET)
    header: X-K2M-Signature: sha256=<hex_signature>

  Bot validates:
    expected = hmac.new(WEBHOOK_SECRET, payload_bytes, sha256).hexdigest()
    compare_digest(received, "sha256=" + expected) or return 401
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from typing import Optional, Tuple

from aiohttp import web

logger = logging.getLogger(__name__)

SIGNATURE_HEADER = "X-K2M-Signature"
SIGNATURE_PREFIX = "sha256="


def _get_secret() -> Optional[bytes]:
    """Return the WEBHOOK_SECRET bytes, or None if not configured."""
    raw = os.getenv("WEBHOOK_SECRET", "").strip()
    if not raw:
        return None
    return raw.encode()


def validate_signature(body: bytes, received_header: Optional[str]) -> Tuple[bool, str]:
    """
    Validate an HMAC-SHA256 signature from an inbound Apps Script webhook.

    Args:
        body: Raw request body bytes (must be the exact bytes the sender signed).
        received_header: Value of the X-K2M-Signature header, e.g. "sha256=abc123".

    Returns:
        (True, "") on success.
        (False, reason_string) on failure.
    """
    secret = _get_secret()
    if secret is None:
        logger.error("WEBHOOK_SECRET not configured — rejecting all signed webhook calls")
        return False, "WEBHOOK_SECRET not set on server"

    if not received_header:
        return False, "Missing X-K2M-Signature header"

    if not received_header.startswith(SIGNATURE_PREFIX):
        return False, f"Signature header must start with '{SIGNATURE_PREFIX}'"

    received_hex = received_header[len(SIGNATURE_PREFIX):]

    expected_hex = hmac.new(secret, body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(received_hex, expected_hex):
        return False, "Signature mismatch"

    return True, ""


async def require_webhook_signature(request: web.Request) -> Tuple[bool, bytes, str]:
    """
    aiohttp helper: read body, validate signature, return (ok, body, error_reason).

    Usage in a handler:
        ok, body, reason = await require_webhook_signature(request)
        if not ok:
            return web.json_response({"success": False, "error": reason}, status=401)
    """
    body = await request.read()
    header = request.headers.get(SIGNATURE_HEADER)
    ok, reason = validate_signature(body, header)
    return ok, body, reason


def get_client_ip(request: web.Request) -> str:
    """Best-effort client IP extraction (handles Railway/proxy forwarding)."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote or "unknown"
