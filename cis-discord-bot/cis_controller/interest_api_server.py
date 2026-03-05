"""
Interest Form API Server - Task 7.1 reconciliation.

Provides HTTP POST /api/interest for landing-page enrollment.
Integrates with Google Sheets and Brevo email delivery.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from aiohttp import web

BOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOT_DIR))

from preload_students import _build_sheets_service, _safe_get

logger = logging.getLogger(__name__)

# Column indices (0-based, canonical runtime mapping)
COL_NAME = 0        # A
COL_EMAIL = 1       # B
COL_PHONE = 2       # C
COL_DISCORD_ID = 3  # D
COL_PROFESSION = 4  # E
COL_ZONE = 5        # F
COL_SITUATION = 6   # G
COL_GOALS = 7       # H
COL_EMOTIONAL = 8   # I
COL_PARENT_EMAIL = 9  # J
COL_MPESA_CODE = 10   # K
COL_PAYMENT = 11    # L
COL_NOTES = 12      # M
COL_CREATED_AT = 13  # N
COL_ACTIVATED_AT = 14  # O
COL_SUBMIT_TOKEN = 15  # P
COL_TOKEN_EXPIRY = 16  # Q
COL_INVITE = 17     # R

ENROLLMENT_CAP = int(os.getenv("ENROLLMENT_CAP", "30").strip())
TOKEN_TTL_DAYS = int(os.getenv("MPESA_SUBMIT_TOKEN_TTL_DAYS", "7").strip())


def _cors_headers() -> Dict[str, str]:
    return {"Access-Control-Allow-Origin": "*"}


def _sheet_name_from_range(sheet_range: str) -> str:
    return sheet_range.split("!", 1)[0] if "!" in sheet_range else "Student Roster"


def _column_letter(col_idx: int) -> str:
    if col_idx < 0:
        raise ValueError("Column index must be >= 0")
    letters = ""
    value = col_idx + 1
    while value > 0:
        value, remainder = divmod(value - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso_utc(raw: str) -> Optional[datetime]:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _generate_submit_token() -> str:
    return secrets.token_urlsafe(12)


def _generate_placeholder_invite_code(email: str) -> str:
    """
    Short fallback invite code used when Discord invite API is unavailable.
    Task 7.2 introduces full invite lifecycle/linkage.
    """
    local_part = "".join(ch for ch in email.split("@")[0].lower() if ch.isalnum())[:6] or "user"
    ts_suffix = format(int(datetime.now(timezone.utc).timestamp()), "x")[-8:]
    return f"k2m{local_part}{ts_suffix}"[:20]


async def create_discord_invite_link() -> Optional[Dict[str, str]]:
    """
    Create a unique Discord invite via API.

    Required env:
      - DISCORD_TOKEN
      - DISCORD_INVITE_CHANNEL_ID

    Returns:
      {"code": "...", "url": "https://discord.gg/..."} or None.
    """
    token = os.getenv("DISCORD_TOKEN", "").strip()
    channel_id = os.getenv("DISCORD_INVITE_CHANNEL_ID", "").strip()

    if not token or not channel_id:
        return None

    url = f"https://discord.com/api/v10/channels/{channel_id}/invites"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "max_age": 604800,  # 7 days
        "max_uses": 1,
        "unique": True,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code not in (200, 201):
            logger.warning(
                "Discord invite creation failed: status=%s body=%s",
                response.status_code,
                response.text[:300],
            )
            return None

        body = response.json()
        code = str(body.get("code", "")).strip()
        if not code:
            logger.warning("Discord invite creation returned empty code")
            return None

        return {"code": code, "url": f"https://discord.gg/{code}"}
    except Exception as exc:
        logger.warning("Discord invite creation error: %s", exc)
        return None


async def check_enrollment_cap(
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> Dict[str, int]:
    """
    Count confirmed/paid enrollments against the cap.

    Returns:
      {"paid_count": int, "cap": int, "available": int}
    """
    try:
        service = _build_sheets_service(creds_path=creds_path, read_only=True)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
        ).execute()

        rows = result.get("values", [])
        paid_count = 0
        for row in rows[1:]:
            payment = _safe_get(row, COL_PAYMENT).lower()
            if payment in ("paid", "confirmed", "yes", "check"):
                paid_count += 1

        available = max(0, ENROLLMENT_CAP - paid_count)
        logger.info(
            "Enrollment check: %s/%s paid, %s available",
            paid_count,
            ENROLLMENT_CAP,
            available,
        )
        return {"paid_count": paid_count, "cap": ENROLLMENT_CAP, "available": available}
    except Exception as exc:
        logger.error("Failed to check enrollment cap: %s", exc)
        # Fail-safe: do not over-enroll when sheet read fails.
        return {"paid_count": ENROLLMENT_CAP, "cap": ENROLLMENT_CAP, "available": 0}


async def check_duplicate_email(
    email: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> bool:
    """Return True if the email already exists in Column B."""
    try:
        service = _build_sheets_service(creds_path=creds_path, read_only=True)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
        ).execute()

        rows = result.get("values", [])
        email_lower = email.strip().lower()

        for row in rows[1:]:
            existing_email = _safe_get(row, COL_EMAIL).lower()
            if existing_email == email_lower:
                logger.info("Duplicate email found: %s", email)
                return True

        return False
    except Exception as exc:
        logger.error("Failed to check duplicate email: %s", exc)
        # Allow submissions when duplicate check is unavailable.
        return False


async def append_to_student_roster(
    name: str,
    email: str,
    phone: str,
    profession: str,
    invite_code: str,
    waitlisted: bool,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> bool:
    """Append a new lead row to Student Roster."""
    try:
        service = _build_sheets_service(creds_path=creds_path, read_only=False)
        values_api = service.spreadsheets().values()

        payment_status = "Waitlisted" if waitlisted else "Lead"
        created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

        # Canonical row: A-R
        row_data = [[
            name,              # A
            email,             # B
            phone,             # C
            "",                # D
            profession,        # E
            "",                # F
            "",                # G
            "",                # H
            "",                # I
            "",                # J
            "",                # K
            payment_status,    # L
            "",                # M
            created_at,        # N
            "",                # O
            "",                # P
            "",                # Q
            invite_code,       # R
        ]]

        sheet_name = sheet_range.split("!", 1)[0] if "!" in sheet_range else "Student Roster"
        range_spec = f"{sheet_name}!A:R"

        values_api.append(
            spreadsheetId=spreadsheet_id,
            range=range_spec,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": row_data},
        ).execute()

        logger.info(
            "Appended roster row: email=%s invite_code=%s waitlisted=%s",
            email,
            invite_code,
            waitlisted,
        )
        return True
    except Exception as exc:
        logger.error("Failed to append to Student Roster: %s", exc)
        return False


async def read_roster_rows(
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> List[List[str]]:
    """Read roster rows from Google Sheets."""
    service = _build_sheets_service(creds_path=creds_path, read_only=True)
    values_api = service.spreadsheets().values()
    result = values_api.get(
        spreadsheetId=spreadsheet_id,
        range=sheet_range,
    ).execute()
    return result.get("values", [])


async def find_row_by_email(
    email: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> Optional[Tuple[int, List[str]]]:
    """Find a roster row by email (Column B). Returns (row_number, row_values)."""
    rows = await read_roster_rows(
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    email_lower = email.strip().lower()
    for row_num, row in enumerate(rows[1:], start=2):
        if _safe_get(row, COL_EMAIL).lower() == email_lower:
            return row_num, row
    return None


async def find_row_by_submit_token(
    token: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> Optional[Tuple[int, List[str]]]:
    """Find a roster row by submit token (Column P). Returns (row_number, row_values)."""
    rows = await read_roster_rows(
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    needle = token.strip()
    for row_num, row in enumerate(rows[1:], start=2):
        if _safe_get(row, COL_SUBMIT_TOKEN) == needle:
            return row_num, row
    return None


async def find_row_by_invite_code(
    invite_code: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> Optional[Tuple[int, List[str]]]:
    """Find a roster row by invite code (Column R). Returns (row_number, row_values)."""
    needle = (invite_code or "").strip()
    if not needle:
        return None

    rows = await read_roster_rows(
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    for row_num, row in enumerate(rows[1:], start=2):
        if _safe_get(row, COL_INVITE).strip() == needle:
            return row_num, row
    return None


async def link_roster_discord_identity_by_invite_code(
    invite_code: str,
    discord_id: str,
    discord_username: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Write Column D identity bridge (`discord_id|discord_username`) for a given invite code.

    Returns a minimal row payload when updated, otherwise None.
    """
    match = await find_row_by_invite_code(
        invite_code=invite_code,
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    if not match:
        return None

    row_number, row = match
    identity_value = f"{discord_id}|{discord_username}"
    existing = _safe_get(row, COL_DISCORD_ID).strip()

    # Idempotent update; avoid overwriting a claimed row with a different identity.
    if existing and existing != identity_value:
        logger.warning(
            "Invite %s already linked in roster row %s: existing=%s attempted=%s",
            invite_code,
            row_number,
            existing,
            identity_value,
        )
        return None

    updated = await update_roster_cells(
        row_number=row_number,
        updates={COL_DISCORD_ID: identity_value},
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    if not updated:
        return None

    return {
        "row_number": row_number,
        "enrollment_name": _safe_get(row, COL_NAME),
        "enrollment_email": _safe_get(row, COL_EMAIL),
        "profession": _safe_get(row, COL_PROFESSION),
        "invite_code": invite_code,
        "discord_identity": identity_value,
    }


async def update_roster_cells(
    row_number: int,
    updates: Dict[int, Any],
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> bool:
    """
    Update specific roster cells for one row.

    updates maps `column_index` (0-based) -> `value`.
    """
    if not updates:
        return True

    try:
        service = _build_sheets_service(creds_path=creds_path, read_only=False)
        values_api = service.spreadsheets().values()
        sheet_name = _sheet_name_from_range(sheet_range)

        data = []
        for col_idx, value in sorted(updates.items(), key=lambda item: item[0]):
            cell_ref = f"{sheet_name}!{_column_letter(col_idx)}{row_number}"
            data.append({"range": cell_ref, "values": [["" if value is None else str(value)]]})

        values_api.batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "RAW",
                "data": data,
            },
        ).execute()
        return True
    except Exception as exc:
        logger.error("Failed to update roster row %s: %s", row_number, exc)
        return False


def build_mpesa_submit_url(token: str) -> str:
    """
    Build public payment submission URL from env base + token.
    """
    base = os.getenv(
        "MPESA_SUBMIT_FORM_URL",
        "https://kira-bot-production.up.railway.app/mpesa-submit",
    ).strip().rstrip("/")
    return f"{base}?token={token}"


def _mask_email(email: str) -> str:
    """
    Return lightly-masked email for UI/status responses.
    """
    text = (email or "").strip()
    if "@" not in text:
        return ""
    local, domain = text.split("@", 1)
    if len(local) <= 2:
        local_masked = local[0] + "*"
    else:
        local_masked = local[0] + ("*" * (len(local) - 2)) + local[-1]
    return f"{local_masked}@{domain}"


async def send_brevo_email(
    to_email: str,
    first_name: str,
    waitlisted: bool,
    invite_link: Optional[str] = None,
    waitlist_number: Optional[int] = None,
) -> bool:
    """Send Email #1 (invite) or Email #5 (waitlist)."""
    try:
        from cis_controller.email_service import EmailService

        email_service = EmailService()
        first_name_only = first_name.strip().split()[0] if first_name else "there"

        if waitlisted:
            subject = "You're on our priority list!"
            waitlist_num = waitlist_number or (ENROLLMENT_CAP + 1)
            html_content = f"""
            <!DOCTYPE html>
            <html><body style="font-family:Arial,sans-serif;line-height:1.6;">
              <h2>You're on our priority list</h2>
              <p>Hey {first_name_only},</p>
              <p>This cohort is full. You're <strong>#{waitlist_num}</strong> on the priority list for the next cohort.</p>
              <p>We'll email you first when enrollment opens.</p>
            </body></html>
            """
        else:
            if not invite_link:
                logger.error("Cannot send Email #1 without invite_link")
                return False

            subject = "Your Discord invitation is ready"
            html_content = f"""
            <!DOCTYPE html>
            <html><body style="font-family:Arial,sans-serif;line-height:1.6;">
              <h2>Welcome to K2M</h2>
              <p>Hey {first_name_only},</p>
              <p>Thanks for your interest. Join Discord using your personal invite:</p>
              <p><a href="{invite_link}">{invite_link}</a></p>
              <p>After you join, KIRA will DM your next step.</p>
              <p>If this link does not work, reply to this email for a fresh invite.</p>
            </body></html>
            """

        result = await email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )

        if result.success:
            logger.info("Email sent: to=%s waitlisted=%s", to_email, waitlisted)
        else:
            logger.warning("Email send failed: %s", result.error)

        return result.success
    except Exception as exc:
        logger.error("Failed to send email: %s", exc)
        return False


async def send_enrollment_payment_email(
    to_email: str,
    first_name: str,
    submit_url: str,
) -> bool:
    """Send Email #2 after /api/enroll with payment instructions."""
    try:
        from cis_controller.email_service import EmailService

        email_service = EmailService()
        first_name_only = first_name.strip().split()[0] if first_name else "there"
        subject = "Step 3 of 4: Complete your M-Pesa payment"
        html_content = f"""
        <!DOCTYPE html>
        <html><body style="font-family:Arial,sans-serif;line-height:1.6;">
          <h2>Enrollment received</h2>
          <p>Hey {first_name_only},</p>
          <p>Your enrollment form is complete.</p>
          <p><strong>Next step (Step 3 of 4):</strong> pay via M-Pesa, then submit your code using this secure link:</p>
          <p><a href="{submit_url}">{submit_url}</a></p>
          <p>This link expires in {TOKEN_TTL_DAYS} days.</p>
        </body></html>
        """
        result = await email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )
        return result.success
    except Exception as exc:
        logger.error("Failed to send enrollment payment email: %s", exc)
        return False


async def send_mpesa_received_email(
    to_email: str,
    first_name: str,
) -> bool:
    """Send Email #3 confirmation after M-Pesa code submission."""
    try:
        from cis_controller.email_service import EmailService

        email_service = EmailService()
        first_name_only = first_name.strip().split()[0] if first_name else "there"
        subject = "Step 4 of 4: M-Pesa code received"
        html_content = f"""
        <!DOCTYPE html>
        <html><body style="font-family:Arial,sans-serif;line-height:1.6;">
          <h2>M-Pesa code received</h2>
          <p>Hey {first_name_only},</p>
          <p>We've received your M-Pesa code and queued it for verification.</p>
          <p>Trevor reviews payments within 24 hours. You'll get your activation email once confirmed.</p>
        </body></html>
        """
        result = await email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )
        return result.success
    except Exception as exc:
        logger.error("Failed to send M-Pesa received email: %s", exc)
        return False


class InterestAPIServer:
    """HTTP server hosting /api/interest."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8081,
        spreadsheet_id: Optional[str] = None,
        creds_path: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEETS_ID", "")
        self.creds_path = creds_path or os.getenv("GOOGLE_SHEETS_CREDS", "")
        self.sheet_range = os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z")
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.BaseSite] = None

    async def _handle_cors(self, request: web.Request) -> web.Response:
        return web.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    async def _handle_interest(self, request: web.Request) -> web.Response:
        try:
            data = await request.json()

            name = data.get("name", "").strip()
            email = data.get("email", "").strip().lower()
            phone = data.get("phone", "").strip()
            profession = data.get("profession", "Other").strip() or "Other"

            if not self.spreadsheet_id:
                return web.json_response(
                    {"success": False, "error": "Enrollment backend is not configured"},
                    status=503,
                    headers=_cors_headers(),
                )

            if not name or not email or not phone:
                return web.json_response(
                    {"success": False, "error": "Name, email, and phone are required"},
                    status=400,
                    headers=_cors_headers(),
                )

            is_duplicate = await check_duplicate_email(
                email=email,
                spreadsheet_id=self.spreadsheet_id,
                sheet_range=self.sheet_range,
                creds_path=self.creds_path,
            )
            if is_duplicate:
                return web.json_response(
                    {
                        "success": False,
                        "error": "We already have your submission. Check your email for your Discord invitation.",
                    },
                    status=409,
                    headers=_cors_headers(),
                )

            cap_status = await check_enrollment_cap(
                spreadsheet_id=self.spreadsheet_id,
                sheet_range=self.sheet_range,
                creds_path=self.creds_path,
            )
            waitlisted = cap_status["available"] <= 0

            invite_code = _generate_placeholder_invite_code(email)
            invite_link = os.getenv("DISCORD_INVITE_FALLBACK_URL", "").strip()

            if not waitlisted:
                invite_data = await create_discord_invite_link()
                if invite_data:
                    invite_code = invite_data["code"]
                    invite_link = invite_data["url"]
                elif not invite_link:
                    return web.json_response(
                        {
                            "success": False,
                            "error": "Unable to create Discord invite right now. Please retry shortly.",
                        },
                        status=503,
                        headers=_cors_headers(),
                    )

            appended = await append_to_student_roster(
                name=name,
                email=email,
                phone=phone,
                profession=profession,
                invite_code=invite_code,
                waitlisted=waitlisted,
                spreadsheet_id=self.spreadsheet_id,
                sheet_range=self.sheet_range,
                creds_path=self.creds_path,
            )
            if not appended:
                return web.json_response(
                    {"success": False, "error": "Could not save your enrollment. Please try again."},
                    status=500,
                    headers=_cors_headers(),
                )

            waitlist_number = None
            if waitlisted:
                waitlist_number = max(1, cap_status["paid_count"] - ENROLLMENT_CAP + 1)

            email_sent = await send_brevo_email(
                to_email=email,
                first_name=name,
                waitlisted=waitlisted,
                invite_link=invite_link,
                waitlist_number=waitlist_number,
            )
            if not email_sent:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Enrollment saved, but email delivery failed. Contact support for your invite.",
                    },
                    status=502,
                    headers=_cors_headers(),
                )

            return web.json_response(
                {
                    "success": True,
                    "waitlisted": waitlisted,
                    "message": (
                        "Check your email for your Discord invitation!"
                        if not waitlisted
                        else "You're on our priority list for the next cohort!"
                    ),
                },
                status=200,
                headers=_cors_headers(),
            )

        except json.JSONDecodeError:
            return web.json_response(
                {"success": False, "error": "Invalid JSON"},
                status=400,
                headers=_cors_headers(),
            )
        except Exception as exc:
            logger.error("Error handling interest request: %s", exc, exc_info=True)
            return web.json_response(
                {"success": False, "error": "Internal server error"},
                status=500,
                headers=_cors_headers(),
            )

    async def _handle_enroll(self, request: web.Request) -> web.Response:
        """
        Handle /api/enroll submissions.

        Writes profile data (F-J), generates payment submit token (P/Q),
        and sends Email #2 with payment URL.
        """
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response(
                {"success": False, "error": "Invalid JSON"},
                status=400,
                headers=_cors_headers(),
            )

        try:
            if not self.spreadsheet_id:
                return web.json_response(
                    {"success": False, "error": "Enrollment backend is not configured"},
                    status=503,
                    headers=_cors_headers(),
                )

            email = str(data.get("email", "")).strip().lower()
            zone = str(data.get("zone", "")).strip()
            situation = str(data.get("situation", "")).strip()
            goals = str(data.get("goals", "")).strip()
            emotional_baseline = str(data.get("emotional_baseline", "")).strip()
            parent_email = str(data.get("parent_email", "")).strip().lower()
            name_override = str(data.get("name", "")).strip()

            if not email or not zone or not situation or not goals or not emotional_baseline:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Email, zone, situation, goals, and emotional_baseline are required",
                    },
                    status=400,
                    headers=_cors_headers(),
                )

            row_match = await find_row_by_email(
                email=email,
                spreadsheet_id=self.spreadsheet_id,
                sheet_range=self.sheet_range,
                creds_path=self.creds_path,
            )
            if not row_match:
                return web.json_response(
                    {"success": False, "error": "No interest submission found for this email"},
                    status=404,
                    headers=_cors_headers(),
                )

            row_number, row = row_match
            token = _generate_submit_token()
            token_expiry = _iso_utc(datetime.now(timezone.utc) + timedelta(days=TOKEN_TTL_DAYS))
            submit_url = build_mpesa_submit_url(token)

            current_payment = _safe_get(row, COL_PAYMENT)
            current_payment_lc = current_payment.lower()
            next_payment_status = current_payment
            if current_payment_lc in {"", "lead", "waitlisted"}:
                next_payment_status = "Enrolled"

            updated = await update_roster_cells(
                row_number=row_number,
                updates={
                    COL_ZONE: zone,
                    COL_SITUATION: situation,
                    COL_GOALS: goals,
                    COL_EMOTIONAL: emotional_baseline,
                    COL_PARENT_EMAIL: parent_email,
                    COL_PAYMENT: next_payment_status,
                    COL_SUBMIT_TOKEN: token,
                    COL_TOKEN_EXPIRY: token_expiry,
                },
                spreadsheet_id=self.spreadsheet_id,
                sheet_range=self.sheet_range,
                creds_path=self.creds_path,
            )
            if not updated:
                return web.json_response(
                    {"success": False, "error": "Could not save your enrollment details"},
                    status=500,
                    headers=_cors_headers(),
                )

            student_name = _safe_get(row, COL_NAME) or name_override or email.split("@")[0]
            email_sent = await send_enrollment_payment_email(
                to_email=email,
                first_name=student_name,
                submit_url=submit_url,
            )
            if not email_sent:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Enrollment saved, but payment email could not be delivered.",
                    },
                    status=502,
                    headers=_cors_headers(),
                )

            return web.json_response(
                {
                    "success": True,
                    "message": "Enrollment complete. Check your email for payment instructions.",
                    "submit_url": submit_url,
                    "expires_at": token_expiry,
                },
                status=200,
                headers=_cors_headers(),
            )
        except Exception as exc:
            logger.error("Error handling enroll request: %s", exc, exc_info=True)
            return web.json_response(
                {"success": False, "error": "Internal server error"},
                status=500,
                headers=_cors_headers(),
            )

    async def _handle_mpesa_status(self, request: web.Request) -> web.Response:
        """
        Validate M-Pesa token status for frontend preflight checks.
        """
        try:
            if not self.spreadsheet_id:
                return web.json_response(
                    {"success": False, "error": "Enrollment backend is not configured"},
                    status=503,
                    headers=_cors_headers(),
                )

            token = (request.query.get("token") or "").strip()
            if not token:
                return web.json_response(
                    {"success": False, "error": "Missing token"},
                    status=400,
                    headers=_cors_headers(),
                )

            row_match = await find_row_by_submit_token(
                token=token,
                spreadsheet_id=self.spreadsheet_id,
                sheet_range=self.sheet_range,
                creds_path=self.creds_path,
            )
            if not row_match:
                return web.json_response(
                    {"success": False, "valid": False, "error": "Invalid token"},
                    status=404,
                    headers=_cors_headers(),
                )

            _, row = row_match
            expiry_text = _safe_get(row, COL_TOKEN_EXPIRY)
            expiry_dt = _parse_iso_utc(expiry_text)
            if expiry_dt and expiry_dt < datetime.now(timezone.utc):
                return web.json_response(
                    {
                        "success": False,
                        "valid": False,
                        "expired": True,
                        "error": "Token expired",
                    },
                    status=410,
                    headers=_cors_headers(),
                )

            return web.json_response(
                {
                    "success": True,
                    "valid": True,
                    "email_hint": _mask_email(_safe_get(row, COL_EMAIL)),
                    "expires_at": expiry_text,
                },
                status=200,
                headers=_cors_headers(),
            )
        except Exception as exc:
            logger.error("Error handling mpesa status request: %s", exc, exc_info=True)
            return web.json_response(
                {"success": False, "error": "Internal server error"},
                status=500,
                headers=_cors_headers(),
            )

    async def _handle_mpesa_submit(self, request: web.Request) -> web.Response:
        """
        Handle /api/mpesa-submit submissions.

        Matches token (P), validates expiry (Q), stores M-Pesa code (K),
        and marks payment status as Pending (L).
        """
        try:
            data = await request.json()
        except json.JSONDecodeError:
            return web.json_response(
                {"success": False, "error": "Invalid JSON"},
                status=400,
                headers=_cors_headers(),
            )

        try:
            if not self.spreadsheet_id:
                return web.json_response(
                    {"success": False, "error": "Enrollment backend is not configured"},
                    status=503,
                    headers=_cors_headers(),
                )

            token = str(data.get("token", "")).strip() or (request.query.get("token") or "").strip()
            mpesa_code = str(data.get("mpesa_code", "")).strip().upper()
            if not token or not mpesa_code:
                return web.json_response(
                    {"success": False, "error": "Token and mpesa_code are required"},
                    status=400,
                    headers=_cors_headers(),
                )

            row_match = await find_row_by_submit_token(
                token=token,
                spreadsheet_id=self.spreadsheet_id,
                sheet_range=self.sheet_range,
                creds_path=self.creds_path,
            )
            if not row_match:
                return web.json_response(
                    {"success": False, "error": "Invalid or unknown token"},
                    status=404,
                    headers=_cors_headers(),
                )

            row_number, row = row_match
            expiry_text = _safe_get(row, COL_TOKEN_EXPIRY)
            expiry_dt = _parse_iso_utc(expiry_text)
            if expiry_dt and expiry_dt < datetime.now(timezone.utc):
                return web.json_response(
                    {
                        "success": False,
                        "expired": True,
                        "error": "Your payment link has expired. Request a fresh link in Discord.",
                    },
                    status=410,
                    headers=_cors_headers(),
                )

            updated = await update_roster_cells(
                row_number=row_number,
                updates={
                    COL_MPESA_CODE: mpesa_code,
                    COL_PAYMENT: "Pending",
                },
                spreadsheet_id=self.spreadsheet_id,
                sheet_range=self.sheet_range,
                creds_path=self.creds_path,
            )
            if not updated:
                return web.json_response(
                    {"success": False, "error": "Could not record your M-Pesa code"},
                    status=500,
                    headers=_cors_headers(),
                )

            student_email = _safe_get(row, COL_EMAIL)
            student_name = _safe_get(row, COL_NAME) or student_email.split("@")[0]
            email_sent = await send_mpesa_received_email(
                to_email=student_email,
                first_name=student_name,
            )
            if not email_sent:
                return web.json_response(
                    {
                        "success": False,
                        "error": "M-Pesa code recorded, but confirmation email failed.",
                    },
                    status=502,
                    headers=_cors_headers(),
                )

            return web.json_response(
                {
                    "success": True,
                    "message": "M-Pesa code received. Verification usually takes up to 24 hours.",
                },
                status=200,
                headers=_cors_headers(),
            )
        except Exception as exc:
            logger.error("Error handling mpesa submit request: %s", exc, exc_info=True)
            return web.json_response(
                {"success": False, "error": "Internal server error"},
                status=500,
                headers=_cors_headers(),
            )

    def register_routes(self, app: web.Application) -> None:
        """Register all enrollment-related API routes on an aiohttp app."""
        app.router.add_options("/api/interest", self._handle_cors)
        app.router.add_post("/api/interest", self._handle_interest)

        app.router.add_options("/api/enroll", self._handle_cors)
        app.router.add_post("/api/enroll", self._handle_enroll)

        app.router.add_options("/api/mpesa-submit", self._handle_cors)
        app.router.add_get("/api/mpesa-submit", self._handle_mpesa_status)
        app.router.add_post("/api/mpesa-submit", self._handle_mpesa_submit)

    async def start(self) -> None:
        if self._runner is not None:
            return

        if not self.spreadsheet_id:
            logger.warning("GOOGLE_SHEETS_ID not set - Interest API server not starting")
            return

        app = web.Application()
        self.register_routes(app)

        self._runner = web.AppRunner(app)
        await self._runner.setup()

        self._site = web.TCPSite(self._runner, host=self.host, port=self.port)
        await self._site.start()
        logger.info(
            "Enrollment API server listening on http://%s:%s (interest/enroll/mpesa)",
            self.host,
            self.port,
        )

    async def stop(self) -> None:
        if self._runner is None:
            return
        await self._runner.cleanup()
        self._runner = None
        self._site = None
        logger.info("Interest API server stopped")

    def stop_sync(self) -> None:
        if self._runner is None:
            return
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.stop())
            else:
                loop.run_until_complete(self.stop())
        except Exception:
            pass
