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
import re
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus

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
COL_ZONE_VERIFY = 18  # S — scenario cross-check (facilitator review only)
COL_ANXIETY = 19      # T — anxiety level 1-10 (crisis threshold)
COL_HABITS = 20       # U — habits pre-assessment (comma-joined)
COL_STAGE1_NUDGE_EMAIL_SENT = 21  # V — Stage 1->2 recovery marker (1.5 | 1.75 | blank)

ENROLLMENT_CAP = int(os.getenv("ENROLLMENT_CAP", "30").strip())
TOKEN_TTL_DAYS = int(os.getenv("MPESA_SUBMIT_TOKEN_TTL_DAYS", "7").strip())
MPESA_CODE_PATTERN = re.compile(r"^[A-Z0-9]{10}$")
CANONICAL_PROFESSIONS = {
    "teacher",
    "entrepreneur",
    "university_student",
    "working_professional",
    "gap_year_student",
    "other",
}
ENROLL_EMAIL_QUEUE_PATH = Path(
    os.getenv(
        "ENROLL_EMAIL_QUEUE_PATH",
        str(BOT_DIR / "logs" / "pending_enroll_email_queue.json"),
    ).strip()
)
DISCORD_JOINED_AT_NOTE_KEY = "k2m_discord_joined_at"
ENROLL_NUDGE_SENT_NOTE_KEY = "k2m_enroll_nudge_sent_at"
STAGE1_NUDGE_48H = "1.5"
STAGE1_NUDGE_5DAY = "1.75"


def _template_id_from_env(env_var: str) -> Optional[int]:
    raw_value = os.getenv(env_var, "").strip()
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except ValueError:
        logger.warning("Ignoring non-integer template id in %s", env_var)
        return None


def _canonical_email_shell_params() -> Dict[str, str]:
    """
    Shared visual-shell params for Brevo template rendering.
    """
    return {
        "instagram_url": os.getenv(
            "PARENT_EMAIL_SOCIAL_INSTAGRAM_URL",
            "https://instagram.com/k2mlabs",
        ).strip(),
        "x_url": os.getenv(
            "PARENT_EMAIL_SOCIAL_X_URL",
            "https://x.com/k2mlabs",
        ).strip(),
        "whatsapp_url": os.getenv(
            "PARENT_EMAIL_SOCIAL_WHATSAPP_URL",
            "https://wa.me/254700000000",
        ).strip(),
        "discord_url": os.getenv(
            "PARENT_EMAIL_SOCIAL_DISCORD_URL",
            "https://discord.gg/example-invite",
        ).strip(),
    }


def _resolve_store():
    """
    Prefer the already-initialized runtime store from main.py.
    Fallback to get_store() only when running standalone/test contexts.
    """
    from database import get_runtime_store, get_store

    runtime_store = get_runtime_store()
    if runtime_store is not None:
        return runtime_store
    return get_store()


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


def _is_valid_mpesa_code(raw_code: str) -> bool:
    """Validate M-Pesa transaction code format (10 alphanumeric chars)."""
    return bool(MPESA_CODE_PATTERN.fullmatch((raw_code or "").strip().upper()))


def _normalize_profession(raw_value: str) -> str:
    """
    Normalize profession/status into canonical sheet values.

    Canonical set:
      - teacher
      - entrepreneur
      - university_student
      - working_professional
      - gap_year_student
      - other
    """
    raw = (raw_value or "").strip().lower()
    if not raw:
        return "other"
    if raw in CANONICAL_PROFESSIONS:
        return raw

    normalized = re.sub(r"\s+", " ", raw.replace("-", " ").replace("_", " ")).strip()
    alias_map = {
        "teacher": "teacher",
        "teacher / educator": "teacher",
        "educator": "teacher",
        "entrepreneur": "entrepreneur",
        "business owner": "entrepreneur",
        "founder": "entrepreneur",
        "university student": "university_student",
        "college student": "university_student",
        "student": "university_student",
        "working professional": "working_professional",
        "professional": "working_professional",
        "engineer": "working_professional",
        "recent graduate": "gap_year_student",
        "recent grad": "gap_year_student",
        "gap year": "gap_year_student",
        "gap year student": "gap_year_student",
        "other": "other",
    }
    if normalized in alias_map:
        return alias_map[normalized]

    # Best-effort fallback by keyword to avoid invalid sheet values.
    if "teacher" in normalized or "educator" in normalized:
        return "teacher"
    if "entrepreneur" in normalized or "business" in normalized or "founder" in normalized:
        return "entrepreneur"
    if "student" in normalized or "university" in normalized or "college" in normalized:
        return "university_student"
    if "professional" in normalized or "engineer" in normalized or "employee" in normalized:
        return "working_professional"
    if "graduate" in normalized or "gap" in normalized:
        return "gap_year_student"
    return "other"


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

    joined_at = _iso_utc(datetime.now(timezone.utc))
    existing_notes = _safe_get(row, COL_NOTES)
    notes_with_joined_at = _upsert_note_marker(
        existing_notes,
        DISCORD_JOINED_AT_NOTE_KEY,
        joined_at,
    )

    updated = await update_roster_cells(
        row_number=row_number,
        updates={
            COL_DISCORD_ID: identity_value,
            COL_NOTES: notes_with_joined_at,
        },
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


def _extract_discord_id(identity_cell: str) -> str:
    """
    Extract a Discord snowflake from Column D identity (`discord_id|discord_username`).
    Returns empty string for blank/pending/invalid values.
    """
    raw = (identity_cell or "").strip()
    if not raw:
        return ""
    discord_id = raw.split("|", 1)[0].strip()
    if not discord_id or discord_id.startswith("__pending__"):
        return ""
    return discord_id if discord_id.isdigit() else ""


def _extract_note_marker(notes: str, key: str) -> Optional[str]:
    """
    Extract `key=value` markers from free-text notes column.
    """
    if not notes:
        return None
    pattern = rf"(?:^|\|\s*){re.escape(key)}=([^|]+)"
    match = re.search(pattern, notes)
    if not match:
        return None
    return match.group(1).strip()


def _upsert_note_marker(notes: str, key: str, value: str) -> str:
    """
    Add/replace a `key=value` marker in Column M notes text.
    """
    existing = (notes or "").strip()
    marker = f"{key}={value}"
    pattern = rf"(?:^|\|\s*){re.escape(key)}=([^|]+)"
    if re.search(pattern, existing):
        return re.sub(pattern, f" | {marker}", existing).strip(" |")
    if not existing:
        return marker
    return f"{existing} | {marker}"


def _is_enrollment_profile_complete(row: List[str]) -> bool:
    """
    Enrollment is considered complete when core /api/enroll fields are present.
    """
    return all(
        _safe_get(row, col_idx).strip()
        for col_idx in (COL_ZONE, COL_SITUATION, COL_GOALS, COL_EMOTIONAL)
    )


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
            subject = "K2M - Waitlist confirmation"
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

            subject = "K2M - Step 1 done! Join Discord (Step 2 of 4)"
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

        template_env = "BREVO_TEMPLATE_EMAIL_5" if waitlisted else "BREVO_TEMPLATE_EMAIL_1"
        template_id = _template_id_from_env(template_env)
        shell_params = _canonical_email_shell_params()
        if template_id is not None:
            template_params: Dict[str, Any]
            if waitlisted:
                template_params = {
                    **shell_params,
                    "first_name": first_name_only,
                    "waitlist_number": str(waitlist_num),
                }
            else:
                template_params = {
                    **shell_params,
                    "first_name": first_name_only,
                    "discord_invite_link": invite_link or "",
                }
            result = await email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                template_id=template_id,
                template_params=template_params,
            )
        else:
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
    discord_id: Optional[str] = None,
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
          <p>Discord account linked: <code>{discord_id or "pending-sync"}</code></p>
          <p><strong>Next step (Step 3 of 4):</strong> pay via M-Pesa, then submit your code using this secure link:</p>
          <p><a href="{submit_url}">{submit_url}</a></p>
          <p>This link expires in {TOKEN_TTL_DAYS} days.</p>
        </body></html>
        """
        template_id = _template_id_from_env("BREVO_TEMPLATE_EMAIL_2")
        shell_params = _canonical_email_shell_params()
        if template_id is not None:
            template_params = {
                **shell_params,
                "first_name": first_name_only,
                "mpesa_submit_url": submit_url,
                "mpesa_tutorial_url": os.getenv(
                    "MPESA_TUTORIAL_URL",
                    "https://k2m-edtech.program/m-pesa-payment",
                ).strip(),
                "week1_start_date": os.getenv(
                    "COHORT_1_START_DATE",
                    "",
                ).strip(),
            }
            result = await email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                template_id=template_id,
                template_params=template_params,
            )
        else:
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
          <p>A facilitator reviews payments within 24 hours. You'll get your activation email once confirmed.</p>
        </body></html>
        """
        template_id = _template_id_from_env("BREVO_TEMPLATE_EMAIL_3")
        shell_params = _canonical_email_shell_params()
        if template_id is not None:
            result = await email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                template_id=template_id,
                template_params={
                    **shell_params,
                    "first_name": first_name_only,
                },
            )
        else:
            result = await email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
            )
        return result.success
    except Exception as exc:
        logger.error("Failed to send M-Pesa received email: %s", exc)
        return False


def _build_discord_invite_link(invite_value: str) -> str:
    """
    Normalize roster invite values to a full Discord invite URL.
    """
    raw = (invite_value or "").strip()
    if not raw:
        return os.getenv("DISCORD_FALLBACK_INVITE_URL", "").strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    return f"https://discord.gg/{raw}"


def _normalize_kenyan_phone(phone_number: str) -> Optional[str]:
    """
    Normalize common Kenyan phone formats to E.164 (+254XXXXXXXXX).
    """
    raw = (phone_number or "").strip()
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None

    if raw.startswith("+") and len(digits) >= 10:
        return f"+{digits}"
    if digits.startswith("0") and len(digits) == 10:
        return f"+254{digits[1:]}"
    if digits.startswith("254") and len(digits) == 12:
        return f"+{digits}"
    return None


def _looks_like_bounce(error_text: Optional[str], status_code: Optional[int]) -> bool:
    """
    Best-effort bounce detector from synchronous send response.

    True bounce events are often asynchronous; this matcher catches immediate
    provider rejects (invalid/unknown recipient style failures).
    """
    if status_code in {400, 404, 422, 550, 551, 552, 553, 554}:
        return True
    text = (error_text or "").lower()
    indicators = (
        "bounce",
        "bounced",
        "invalid",
        "unknown recipient",
        "mailbox",
        "does not exist",
        "hardbounce",
        "recipient rejected",
    )
    return any(indicator in text for indicator in indicators)


async def send_stage1_dropoff_email(
    *,
    to_email: str,
    first_name: str,
    invite_link: str,
    stage: str,
) -> Dict[str, Any]:
    """
    Send Stage 1->2 recovery email:
      - 1.5 at 48h
      - 1.75 at 5 days

    Returns a compact result dict with success/status/error.
    """
    if stage not in {STAGE1_NUDGE_48H, STAGE1_NUDGE_5DAY}:
        return {"success": False, "status_code": None, "error": f"Unsupported stage: {stage}"}

    try:
        from cis_controller.email_service import EmailService

        email_service = EmailService()
        first_name_only = first_name.strip().split()[0] if first_name else "there"
        tutorial_url = os.getenv(
            "DISCORD_ONBOARDING_TUTORIAL_URL",
            "https://support.discord.com/hc/en-us/articles/360045138571-Beginner-s-Guide-to-Discord",
        ).strip()

        if stage == STAGE1_NUDGE_48H:
            subject = "K2M - Did you get in OK?"
            template_env = "BREVO_TEMPLATE_EMAIL_1_5"
            html_content = f"""
            <!DOCTYPE html>
            <html><body style="font-family:Arial,sans-serif;line-height:1.6;">
              <h2>Quick check-in</h2>
              <p>Hey {first_name_only},</p>
              <p>Many students need a second tap to complete Discord join. Here is your link again:</p>
              <p><a href="{invite_link}">{invite_link}</a></p>
              <p>Need help getting onto Discord? <a href="{tutorial_url}">{tutorial_url}</a></p>
            </body></html>
            """
        else:
            subject = "K2M - Last chance to secure your spot"
            template_env = "BREVO_TEMPLATE_EMAIL_1_75"
            html_content = f"""
            <!DOCTYPE html>
            <html><body style="font-family:Arial,sans-serif;line-height:1.6;">
              <h2>Final reminder</h2>
              <p>Hey {first_name_only},</p>
              <p>We have limited spots for Cohort 1. Your invite link expires soon.</p>
              <p><a href="{invite_link}">{invite_link}</a></p>
            </body></html>
            """

        template_id = _template_id_from_env(template_env)
        shell_params = _canonical_email_shell_params()
        if template_id is not None:
            result = await email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                template_id=template_id,
                template_params={
                    **shell_params,
                    "first_name": first_name_only,
                    "discord_invite_link": invite_link,
                    "discord_tutorial_url": tutorial_url,
                },
            )
        else:
            result = await email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
            )

        return {
            "success": bool(result.success),
            "status_code": result.status_code,
            "error": result.error or "",
        }
    except Exception as exc:
        logger.error("Failed to send stage1 drop-off email: %s", exc)
        return {"success": False, "status_code": None, "error": str(exc)}


async def send_stage1_whatsapp_nudge(
    *,
    phone_number: str,
    first_name: str,
    invite_link: str,
) -> bool:
    """
    Send Stage 1->2 recovery fallback via Africa's Talking WhatsApp endpoint.

    Required env:
      - AFRICAS_TALKING_WHATSAPP_URL
      - AFRICAS_TALKING_API_KEY
      - AFRICAS_TALKING_USERNAME (optional, defaults to "sandbox")
    """
    endpoint = os.getenv("AFRICAS_TALKING_WHATSAPP_URL", "").strip()
    api_key = os.getenv("AFRICAS_TALKING_API_KEY", "").strip()
    username = os.getenv("AFRICAS_TALKING_USERNAME", "sandbox").strip() or "sandbox"
    normalized_phone = _normalize_kenyan_phone(phone_number)

    if not endpoint or not api_key or not normalized_phone:
        return False

    first_name_only = first_name.strip().split()[0] if first_name else "there"
    message = (
        f"K2M check-in: Hi {first_name_only}, here is your Discord link again: "
        f"{invite_link} . Reply HELP if you are stuck and a facilitator will assist."
    )

    headers = {
        "apiKey": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "username": username,
        "to": normalized_phone,
        "message": message,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
        if 200 <= response.status_code < 300:
            logger.info("Task 7.9: WhatsApp fallback sent to %s", normalized_phone)
            return True
        logger.warning(
            "Task 7.9: WhatsApp fallback failed status=%s body=%s",
            response.status_code,
            response.text[:200],
        )
    except Exception as exc:
        logger.warning("Task 7.9: WhatsApp fallback error: %s", exc)

    return False


def _load_pending_enroll_email_queue() -> List[Dict[str, Any]]:
    """
    Read persisted Email #2 queue entries from local JSON storage.
    """
    try:
        if not ENROLL_EMAIL_QUEUE_PATH.exists():
            return []
        payload = json.loads(ENROLL_EMAIL_QUEUE_PATH.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
    except Exception as exc:
        logger.warning("Could not read enroll email queue: %s", exc)
    return []


def _save_pending_enroll_email_queue(entries: List[Dict[str, Any]]) -> bool:
    """
    Persist Email #2 queue entries to local JSON storage.
    """
    try:
        ENROLL_EMAIL_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
        ENROLL_EMAIL_QUEUE_PATH.write_text(
            json.dumps(entries, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception as exc:
        logger.error("Could not persist enroll email queue: %s", exc)
        return False


def queue_enrollment_payment_email(
    *,
    to_email: str,
    first_name: str,
    submit_url: str,
) -> bool:
    """
    Queue Email #2 for later scheduler delivery when Column D is linked.
    """
    queue = _load_pending_enroll_email_queue()
    email_lc = (to_email or "").strip().lower()
    if not email_lc:
        return False

    # Deduplicate by recipient while keeping latest token URL.
    queue = [
        item for item in queue
        if str(item.get("to_email", "")).strip().lower() != email_lc
    ]
    queue.append(
        {
            "to_email": email_lc,
            "first_name": first_name,
            "submit_url": submit_url,
            "queued_at": _iso_utc(datetime.now(timezone.utc)),
            "attempts": 0,
        }
    )
    return _save_pending_enroll_email_queue(queue)


async def _get_linked_discord_id_for_email(
    email: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> str:
    """
    Return a linked Discord ID from Column D when available, else empty string.
    """
    match = await find_row_by_email(
        email=email,
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    if not match:
        return ""
    _, row = match
    return _extract_discord_id(_safe_get(row, COL_DISCORD_ID))


async def wait_for_linked_discord_id(
    email: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
    retry_delays_seconds: Tuple[int, int, int] = (1, 2, 4),
) -> str:
    """
    Poll Column D for linked discord_id with exponential backoff.
    """
    discord_id = await _get_linked_discord_id_for_email(
        email=email,
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    if discord_id:
        return discord_id

    for delay in retry_delays_seconds:
        if delay > 0 and not os.getenv("PYTEST_CURRENT_TEST"):
            await asyncio.sleep(delay)
        discord_id = await _get_linked_discord_id_for_email(
            email=email,
            spreadsheet_id=spreadsheet_id,
            sheet_range=sheet_range,
            creds_path=creds_path,
        )
        if discord_id:
            return discord_id

    return ""


async def process_pending_enrollment_payment_emails(
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
    max_batch: int = 50,
) -> Dict[str, int]:
    """
    Process queued Email #2 records once discord_id linkage appears in Column D.
    """
    queue = _load_pending_enroll_email_queue()
    if not queue:
        return {"queued": 0, "sent": 0, "deferred": 0, "failed": 0}

    sent = 0
    failed = 0
    remaining: List[Dict[str, Any]] = []

    for item in queue[:max_batch]:
        email = str(item.get("to_email", "")).strip().lower()
        if not email:
            continue

        discord_id = await _get_linked_discord_id_for_email(
            email=email,
            spreadsheet_id=spreadsheet_id,
            sheet_range=sheet_range,
            creds_path=creds_path,
        )
        if not discord_id:
            remaining.append(item)
            continue

        ok = await send_enrollment_payment_email(
            to_email=email,
            first_name=str(item.get("first_name", "")).strip() or email.split("@")[0],
            submit_url=str(item.get("submit_url", "")).strip(),
            discord_id=discord_id,
        )
        if ok:
            sent += 1
            continue

        failed += 1
        item["attempts"] = int(item.get("attempts", 0)) + 1
        remaining.append(item)

    # Keep untouched tail entries.
    if len(queue) > max_batch:
        remaining.extend(queue[max_batch:])

    _save_pending_enroll_email_queue(remaining)
    return {
        "queued": len(queue),
        "sent": sent,
        "deferred": len(remaining),
        "failed": failed,
    }


def build_enroll_form_url(email: str) -> str:
    """
    Build enroll form link for 48h DM nudges.
    """
    base = os.getenv(
        "ENROLL_FORM_URL",
        "https://kira-bot-production.up.railway.app/enroll",
    ).strip().rstrip("/")
    email_lc = (email or "").strip().lower()
    if not email_lc:
        return base
    return f"{base}?email={quote_plus(email_lc)}"


async def send_48h_enroll_nudges(
    *,
    bot: Any,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
    age_hours: int = 48,
    max_nudges: int = 25,
) -> Dict[str, int]:
    """
    Send KIRA DM nudges to linked students who joined but have not enrolled.
    """
    rows = await read_roster_rows(
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    now = datetime.now(timezone.utc)
    nudged = 0
    scanned = 0

    for row_number, row in enumerate(rows[1:], start=2):
        scanned += 1
        if nudged >= max_nudges:
            break

        discord_id = _extract_discord_id(_safe_get(row, COL_DISCORD_ID))
        if not discord_id:
            continue
        if _is_enrollment_profile_complete(row):
            continue

        notes = _safe_get(row, COL_NOTES)
        if _extract_note_marker(notes, ENROLL_NUDGE_SENT_NOTE_KEY):
            continue

        joined_at = _extract_note_marker(notes, DISCORD_JOINED_AT_NOTE_KEY)
        joined_at_dt = _parse_iso_utc(joined_at or "") or _parse_iso_utc(_safe_get(row, COL_CREATED_AT))
        if not joined_at_dt:
            continue
        if now - joined_at_dt < timedelta(hours=age_hours):
            continue

        email = _safe_get(row, COL_EMAIL)
        first_name = (_safe_get(row, COL_NAME) or "there").split(" ")[0]
        enroll_url = build_enroll_form_url(email)
        message = (
            f"Hey {first_name} — ready to enroll?\n\n"
            f"Here is your enrollment form link:\n{enroll_url}\n\n"
            "Reply here if anything is unclear and I can help."
        )

        try:
            user = await bot.fetch_user(int(discord_id))
            await user.send(message)
        except Exception as exc:
            logger.warning("48h enroll nudge failed for %s: %s", discord_id, exc)
            continue

        updated_notes = _upsert_note_marker(
            notes,
            ENROLL_NUDGE_SENT_NOTE_KEY,
            _iso_utc(now),
        )
        await update_roster_cells(
            row_number=row_number,
            updates={COL_NOTES: updated_notes},
            spreadsheet_id=spreadsheet_id,
            sheet_range=sheet_range,
            creds_path=creds_path,
        )
        nudged += 1

    return {"scanned": scanned, "nudged": nudged}


async def check_stage1_dropoff(
    *,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
    first_nudge_after_hours: int = 48,
    final_nudge_after_days: int = 5,
    max_nudges: int = 50,
) -> Dict[str, int]:
    """
    Task 7.9 nightly worker: Stage 1->2 drop-off recovery.

    Rules:
      - Student has not joined Discord yet (Column D empty)
      - Age measured from created_at (Column N)
      - At 48h: send Email #1.5 once
      - At 5 days: send Email #1.75 once
      - Idempotency marker stored in Column V as: 1.5 | 1.75 | blank
      - If Email #1.5 hard-fails like a bounce and phone exists, attempt
        Africa's Talking WhatsApp fallback.
    """
    rows = await read_roster_rows(
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )

    now = datetime.now(timezone.utc)
    first_nudge_delta = timedelta(hours=first_nudge_after_hours)
    final_nudge_delta = timedelta(days=final_nudge_after_days)

    stats: Dict[str, int] = {
        "scanned": 0,
        "email_1_5_sent": 0,
        "email_1_75_sent": 0,
        "whatsapp_sent": 0,
        "email_failures": 0,
        "marker_updates": 0,
        "marker_update_failures": 0,
        "skipped_joined": 0,
        "skipped_not_due": 0,
        "skipped_already_sent": 0,
    }
    dispatched = 0

    for row_number, row in enumerate(rows[1:], start=2):
        if dispatched >= max_nudges:
            break
        stats["scanned"] += 1

        email = _safe_get(row, COL_EMAIL).strip().lower()
        if not email:
            continue

        # Stop condition: once joined, no Stage 1->2 nudges.
        if _extract_discord_id(_safe_get(row, COL_DISCORD_ID)):
            stats["skipped_joined"] += 1
            continue

        created_at_dt = _parse_iso_utc(_safe_get(row, COL_CREATED_AT))
        if not created_at_dt:
            stats["skipped_not_due"] += 1
            continue

        age = now - created_at_dt
        if age < first_nudge_delta:
            stats["skipped_not_due"] += 1
            continue

        marker = _safe_get(row, COL_STAGE1_NUDGE_EMAIL_SENT).strip().lower()
        stage_to_send: Optional[str] = None

        if age >= final_nudge_delta:
            if marker == STAGE1_NUDGE_5DAY:
                stats["skipped_already_sent"] += 1
                continue
            stage_to_send = STAGE1_NUDGE_5DAY
        else:
            # 48h <= age < 5 days
            if marker in {STAGE1_NUDGE_48H, STAGE1_NUDGE_5DAY}:
                stats["skipped_already_sent"] += 1
                continue
            stage_to_send = STAGE1_NUDGE_48H

        invite_link = _build_discord_invite_link(_safe_get(row, COL_INVITE))
        first_name = (_safe_get(row, COL_NAME) or "there").split(" ")[0]

        result = await send_stage1_dropoff_email(
            to_email=email,
            first_name=first_name,
            invite_link=invite_link,
            stage=stage_to_send,
        )

        delivered = bool(result.get("success"))
        if delivered:
            dispatched += 1
            if stage_to_send == STAGE1_NUDGE_48H:
                stats["email_1_5_sent"] += 1
            else:
                stats["email_1_75_sent"] += 1
        else:
            stats["email_failures"] += 1

            # Task 7.9 fallback: WhatsApp nudge if Email #1.5 bounced/rejected.
            if (
                stage_to_send == STAGE1_NUDGE_48H
                and _looks_like_bounce(result.get("error"), result.get("status_code"))
            ):
                wa_ok = await send_stage1_whatsapp_nudge(
                    phone_number=_safe_get(row, COL_PHONE),
                    first_name=first_name,
                    invite_link=invite_link,
                )
                if wa_ok:
                    dispatched += 1
                    stats["whatsapp_sent"] += 1
                    delivered = True

        if delivered:
            updated = await update_roster_cells(
                row_number=row_number,
                updates={COL_STAGE1_NUDGE_EMAIL_SENT: stage_to_send},
                spreadsheet_id=spreadsheet_id,
                sheet_range=sheet_range,
                creds_path=creds_path,
            )
            if updated:
                stats["marker_updates"] += 1
            else:
                stats["marker_update_failures"] += 1

    return stats


async def send_token_expiry_warnings(
    *,
    bot: Any,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
    warn_within_hours: int = 48,
    max_warnings: int = 50,
) -> Dict[str, int]:
    """
    Nightly M-Pesa token expiry warning job (Task 7.4, Decision H-01 + GAP FIX #4).

    Scans Google Sheets for students whose Column Q (token_expiry) falls within
    warn_within_hours from now. For each:
      - If token_warning_sent flag is already True in PG → skip (idempotency).
      - If student has a linked Discord ID → send KIRA DM.
      - If not yet on Discord → fall back to Brevo warning email.
      - After sending: set token_warning_sent = True in PG and log the event.
    """
    rows = await read_roster_rows(
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(hours=warn_within_hours)

    warned_dm = 0
    warned_email = 0
    skipped_already_sent = 0
    skipped_no_token = 0
    scanned = 0

    store = _resolve_store()

    for _row_number, row in enumerate(rows[1:], start=2):
        scanned += 1
        if warned_dm + warned_email >= max_warnings:
            break

        # Only warn students who have a payment token in Sheets
        token = _safe_get(row, COL_SUBMIT_TOKEN).strip()
        expiry_text = _safe_get(row, COL_TOKEN_EXPIRY).strip()
        if not token or not expiry_text:
            skipped_no_token += 1
            continue

        expiry_dt = _parse_iso_utc(expiry_text)
        if not expiry_dt:
            skipped_no_token += 1
            continue

        # Already expired — not our job to warn (show expiry page handles this)
        if expiry_dt <= now:
            continue

        # Not expiring within warn window
        if expiry_dt > deadline:
            continue

        email = _safe_get(row, COL_EMAIL).strip()
        if not email:
            continue

        # Idempotency: skip if warning already sent this cycle
        try:
            already_sent = store.get_token_warning_sent(email)
        except Exception:
            already_sent = False
        if already_sent:
            skipped_already_sent += 1
            continue

        first_name = (_safe_get(row, COL_NAME) or "there").split()[0]
        submit_url = build_mpesa_submit_url(token)
        dm_text = (
            f"Hey {first_name} — your enrollment payment link expires soon.\n\n"
            f"Your secure M-Pesa submission link:\n{submit_url}\n\n"
            "If your link expires, type `/renew` in a DM to KIRA or visit #help."
        )

        discord_id = _extract_discord_id(_safe_get(row, COL_DISCORD_ID))
        sent = False
        send_channel = "unknown"

        if discord_id:
            # Path A: Discord DM
            try:
                user = await bot.fetch_user(int(discord_id))
                await user.send(dm_text)
                sent = True
                send_channel = "discord_dm"
                warned_dm += 1
                logger.info("token_expiry_warning_sent discord_id=%s email=%s", discord_id, email)
            except Exception as exc:
                logger.warning(
                    "Token expiry DM failed for discord_id=%s: %s — falling back to email",
                    discord_id,
                    exc,
                )

        if not sent:
            # Path B: Brevo fallback email for pre-Discord or DM-failed students
            try:
                from cis_controller.email_service import EmailService

                email_service = EmailService()
                subject = "Your K2M payment link expires soon"
                html_content = f"""
                <!DOCTYPE html>
                <html><body style="font-family:Arial,sans-serif;line-height:1.6;">
                  <h2>Action needed: payment link expiring</h2>
                  <p>Hey {first_name},</p>
                  <p>Your secure M-Pesa submission link will expire soon. Please use it before it does:</p>
                  <p><a href="{submit_url}">{submit_url}</a></p>
                  <p>If your link expires, reply to this email or contact a facilitator for a renewal.</p>
                </body></html>
                """
                result = await email_service.send_email(
                    to_email=email,
                    subject=subject,
                    html_content=html_content,
                )
                if result.success:
                    sent = True
                    send_channel = "brevo_email"
                    warned_email += 1
                    logger.info("token_expiry_warning_sent email=%s (Brevo fallback)", email)
            except Exception as exc:
                logger.warning("Token expiry Brevo fallback failed for %s: %s", email, exc)

        if sent:
            try:
                store.set_token_warning_sent(email, True)
            except Exception as exc:
                logger.warning("Could not set token_warning_sent for %s: %s", email, exc)

            try:
                if hasattr(store, "log_observability_event"):
                    store.log_observability_event(
                        discord_id=str(discord_id or email),
                        event_type="token_expiry_warning_sent",
                        metadata={
                            "email": email,
                            "channel": send_channel,
                            "expires_at": _iso_utc(expiry_dt),
                        },
                    )
            except Exception as exc:
                logger.warning("Could not log token_expiry_warning_sent for %s: %s", email, exc)

    return {
        "scanned": scanned,
        "warned_dm": warned_dm,
        "warned_email": warned_email,
        "skipped_already_sent": skipped_already_sent,
        "skipped_no_token": skipped_no_token,
    }


async def send_payment_feedback_dms(
    *,
    bot: Any,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
    silence_after_hours: int = 24,
    escalation_after_hours: int = 8,
    business_hours_start_eat: int = 8,
    business_hours_end_eat: int = 20,
    max_per_pass: int = 50,
) -> Dict[str, int]:
    """
    6h scheduler worker for Task 7.5 (Decisions H-02, M-01, N-23).

    Three scan passes over the Sheets roster:

    Pass A — 24h silence check:
        Column L = 'Pending' AND payment pending age > silence_after_hours.
        Uses PostgreSQL payment_pending_since anchor when available; falls back
        to Column N (created_at) only for backward compatibility.
        Sends KIRA DM once (guarded by payment_silence_dm_sent PG flag).
        Message: "Still reviewing your payment. If urgent, post in #help channel."

    Pass B — Unverifiable DM:
        Column L = 'Unverifiable'.
        Sends student KIRA DM once (guarded by unverifiable_dm_sent PG flag).
        Also posts red-X alert to #facilitator-dashboard.
        Message: "We had trouble verifying your payment. Please send a screenshot
                  of your M-Pesa confirmation to #help or DM a facilitator directly."

    Pass C — N-23 facilitator escalation:
        Column L = 'Pending' AND age > escalation_after_hours during business hours (EAT).
        DMs ALL members of the @Facilitator role once per payment submission
        (guarded by payment_escalation_dm_sent PG flag, reset when payment resolves).
    """
    import pytz

    EAT = pytz.timezone("Africa/Nairobi")
    store = _resolve_store()
    get_payment_silence_dm_sent = getattr(store, "get_payment_silence_dm_sent", lambda _email: False)
    set_payment_silence_dm_sent = getattr(store, "set_payment_silence_dm_sent", lambda _email, _value: None)
    get_unverifiable_dm_sent = getattr(store, "get_unverifiable_dm_sent", lambda _email: False)
    set_unverifiable_dm_sent = getattr(store, "set_unverifiable_dm_sent", lambda _email, _value: None)
    get_payment_escalation_dm_sent = getattr(store, "get_payment_escalation_dm_sent", lambda _email: False)
    set_payment_escalation_dm_sent = getattr(store, "set_payment_escalation_dm_sent", lambda _email, _value: None)
    get_payment_pending_since = getattr(store, "get_payment_pending_since", None)
    set_payment_pending_since = getattr(store, "set_payment_pending_since", None)
    clear_payment_pending_since = getattr(store, "clear_payment_pending_since", None)
    now_utc = datetime.now(timezone.utc)
    now_eat = now_utc.astimezone(EAT)
    eat_hour = now_eat.hour

    rows = await read_roster_rows(
        spreadsheet_id=spreadsheet_id,
        sheet_range=sheet_range,
        creds_path=creds_path,
    )

    stats: Dict[str, int] = {
        "scanned": 0,
        "silence_dm_sent": 0,
        "unverifiable_dm_sent": 0,
        "escalation_dm_sent": 0,
        "dashboard_alerts": 0,
    }

    # Pre-fetch facilitator role members for Pass C (N-23).
    facilitator_members: List[Any] = []
    facilitator_role_id_str = os.getenv("FACILITATOR_ROLE_ID", "").strip()
    guild_id_str = os.getenv("DISCORD_GUILD_ID", "").strip()
    if bot and facilitator_role_id_str and guild_id_str:
        try:
            guild = bot.get_guild(int(guild_id_str))
            if guild:
                role = guild.get_role(int(facilitator_role_id_str))
                if role:
                    facilitator_members = list(role.members)
        except Exception as exc:
            logger.warning("Task 7.5: could not fetch facilitator role members: %s", exc)

    dashboard_channel_id = 0
    for env_key in ("CHANNEL_FACILITATOR_DASHBOARD", "FACILITATOR_DASHBOARD_CHANNEL_ID"):
        value = os.getenv(env_key, "").strip()
        if not value:
            continue
        try:
            dashboard_channel_id = int(value)
            break
        except ValueError:
            logger.warning("Task 7.5: invalid %s value '%s' (must be int)", env_key, value)

    for row_number, row in rows:
        if stats["scanned"] >= max_per_pass:
            break
        stats["scanned"] += 1

        email = _safe_get(row, COL_EMAIL)
        if not email:
            continue

        name = (_safe_get(row, COL_NAME) or "there").split(" ")[0]
        payment_status = (_safe_get(row, COL_PAYMENT) or "").strip()
        created_at_raw = _safe_get(row, COL_CREATED_AT)
        created_at_dt = _parse_iso_utc(created_at_raw)
        discord_id = _extract_discord_id(_safe_get(row, COL_DISCORD_ID))

        payment_pending_since: Optional[datetime] = None
        if callable(get_payment_pending_since):
            try:
                payment_pending_since = get_payment_pending_since(email)
            except Exception as exc:
                logger.warning("Task 7.5: could not load payment_pending_since for %s: %s", email, exc)

        # If this row is pending but lacks a pending-since anchor, initialize one now
        # to avoid using stale lead creation timestamps as the payment clock.
        if (
            payment_status == "Pending"
            and payment_pending_since is None
            and callable(set_payment_pending_since)
        ):
            try:
                payment_pending_since = now_utc
                set_payment_pending_since(email, payment_pending_since)
                logger.info("Task 7.5: initialized payment_pending_since for %s", email)
            except Exception as exc:
                logger.warning("Task 7.5: failed to initialize payment_pending_since for %s: %s", email, exc)

        # Clear stale anchors once payment leaves Pending state.
        if (
            payment_status != "Pending"
            and payment_pending_since is not None
            and callable(clear_payment_pending_since)
        ):
            try:
                clear_payment_pending_since(email)
            except Exception as exc:
                logger.warning("Task 7.5: could not clear payment_pending_since for %s: %s", email, exc)

        age_anchor = payment_pending_since or created_at_dt
        age_hours: float = 0.0
        if age_anchor:
            age_hours = (now_utc - age_anchor).total_seconds() / 3600

        # ── Pass A: 24h silence DM ───────────────────────────────────────
        if payment_status == "Pending" and age_hours >= silence_after_hours and discord_id and bot:
            if not get_payment_silence_dm_sent(email):
                try:
                    user = await bot.fetch_user(int(discord_id))
                    await user.send(
                        f"Hey {name} — still reviewing your payment. "
                        "If it's urgent, post in **#help** and a facilitator will assist."
                    )
                    set_payment_silence_dm_sent(email, True)
                    stats["silence_dm_sent"] += 1
                    logger.info("Task 7.5: silence DM sent to %s (age=%.1fh)", email, age_hours)
                except Exception as exc:
                    logger.warning("Task 7.5: silence DM failed for %s: %s", email, exc)

        # ── Pass B: Unverifiable DM + dashboard alert ────────────────────
        if payment_status == "Unverifiable":
            if discord_id and bot and not get_unverifiable_dm_sent(email):
                try:
                    user = await bot.fetch_user(int(discord_id))
                    await user.send(
                        f"Hey {name} — we had trouble verifying your payment. "
                        "Please send a screenshot of your M-Pesa confirmation to **#help** "
                        "or DM a facilitator directly."
                    )
                    set_unverifiable_dm_sent(email, True)
                    stats["unverifiable_dm_sent"] += 1
                    logger.info("Task 7.5: unverifiable DM sent to %s", email)
                except Exception as exc:
                    logger.warning("Task 7.5: unverifiable DM failed for %s: %s", email, exc)

            # Dashboard red-X alert (fires every pass so Trevor always sees it)
            if bot and dashboard_channel_id:
                try:
                    ch = bot.get_channel(dashboard_channel_id) or await bot.fetch_channel(dashboard_channel_id)
                    await ch.send(
                        f"🔴 **UNVERIFIABLE PAYMENT** — {name} ({email}). "
                        "Manual action required."
                    )
                    stats["dashboard_alerts"] += 1
                except Exception as exc:
                    logger.warning("Task 7.5: dashboard unverifiable alert failed: %s", exc)

        # ── Pass C: N-23 facilitator escalation at 8h+ (business hours EAT) ──
        if (
            payment_status == "Pending"
            and age_hours >= escalation_after_hours
            and business_hours_start_eat <= eat_hour < business_hours_end_eat
            and facilitator_members
            and not get_payment_escalation_dm_sent(email)
        ):
            sent_count = 0
            for member in facilitator_members:
                try:
                    await member.send(
                        f"⚠️ Payment pending >8h — **{name}** ({email}). "
                        f"Age: {age_hours:.0f}h. Please verify in Google Sheets."
                    )
                    sent_count += 1
                except Exception as exc:
                    logger.warning("Task 7.5: escalation DM to facilitator %s failed: %s", member, exc)
            if sent_count > 0:
                set_payment_escalation_dm_sent(email, True)
                stats["escalation_dm_sent"] += sent_count
                logger.info("Task 7.5: N-23 escalation sent to %d facilitators for %s", sent_count, email)

    return stats


class InterestAPIServer:
    """HTTP server hosting /api/interest."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8081,
        spreadsheet_id: Optional[str] = None,
        creds_path: Optional[str] = None,
        bot=None,
    ):
        self.host = host
        self.port = port
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEETS_ID", "")
        self.creds_path = creds_path or os.getenv("GOOGLE_SHEETS_CREDS", "")
        self.sheet_range = os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z")
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.BaseSite] = None
        self._bot = bot

    def set_bot(self, bot) -> None:
        """Inject bot reference after startup (called from main.py on_ready)."""
        self._bot = bot

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
            profession = _normalize_profession(str(data.get("profession", "")))

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
                        "Step 1 of 4 complete - check your email for your Discord invitation."
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
            # Normalise zone — accept "Zone 0" or raw "0" from legacy clients
            zone_raw = str(data.get("zone", "")).strip()
            zone = zone_raw if zone_raw.startswith("Zone ") else f"Zone {zone_raw}" if zone_raw else ""

            situation = str(data.get("situation", "")).strip()
            goals = str(data.get("goals", "")).strip()
            emotional_baseline = str(data.get("emotional_baseline", "")).strip()
            parent_email = str(data.get("parent_email", "")).strip().lower()
            name_override = str(data.get("name", "")).strip()

            # New optional diagnostic fields (additive — no breaking change)
            zone_verification = str(data.get("zone_verification", "")).strip()
            anxiety_raw = data.get("anxiety_level", None)
            anxiety_level = str(int(anxiety_raw)) if anxiety_raw is not None else ""
            habits_baseline = str(data.get("habits_baseline", "")).strip()

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
                    # Diagnostic fields — written only if provided
                    **({COL_ZONE_VERIFY: zone_verification} if zone_verification else {}),
                    **({COL_ANXIETY: anxiety_level} if anxiety_level else {}),
                    **({COL_HABITS: habits_baseline} if habits_baseline else {}),
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
            discord_id = _extract_discord_id(_safe_get(row, COL_DISCORD_ID))
            if not discord_id:
                discord_id = await wait_for_linked_discord_id(
                    email=email,
                    spreadsheet_id=self.spreadsheet_id,
                    sheet_range=self.sheet_range,
                    creds_path=self.creds_path,
                    retry_delays_seconds=(1, 2, 4),
                )

            if discord_id:
                email_sent = await send_enrollment_payment_email(
                    to_email=email,
                    first_name=student_name,
                    submit_url=submit_url,
                    discord_id=discord_id,
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
                message = "Step 3 of 4 - enrollment complete. Check your email for payment instructions."
                if self._bot:
                    async def _send_post_enroll_dm(discord_id_value: str, name: str, token_url: str) -> None:
                        try:
                            user = await self._bot.fetch_user(int(discord_id_value))
                            await user.send(
                                f"Got your enrollment form, {name}!\n\n"
                                "Step 3 of 4 - payment next.\n\n"
                                "Pay via M-Pesa, then submit your code here:\n"
                                f"{token_url}\n"
                                f"(Link expires in {TOKEN_TTL_DAYS} days.)\n\n"
                                "Check your email too for a backup copy.\n\n"
                                "- KIRA"
                            )
                            logger.info("Task 7.10: post-enroll DM sent to discord_id=%s", discord_id_value)
                        except Exception as exc:
                            logger.warning(
                                "Task 7.10: post-enroll DM failed for %s: %s",
                                discord_id_value,
                                exc,
                            )

                    first_name = student_name.strip().split()[0] if student_name.strip() else "there"
                    asyncio.create_task(_send_post_enroll_dm(discord_id, first_name, submit_url))
            else:
                logger.warning("discord_id not found after 3 retries for %s", email)
                queued = queue_enrollment_payment_email(
                    to_email=email,
                    first_name=student_name,
                    submit_url=submit_url,
                )
                if not queued:
                    return web.json_response(
                        {
                            "success": False,
                            "error": "Enrollment saved, but payment email queueing failed. Contact support.",
                        },
                        status=500,
                        headers=_cors_headers(),
                    )
                message = (
                    "Step 3 of 4 - enrollment complete. We will send payment instructions as soon as "
                    "your Discord join is detected."
                )

            return web.json_response(
                {
                    "success": True,
                    "message": message,
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
                # Return HTML for browser direct navigation; JSON for JS fetch (form preflight)
                accept = request.headers.get("Accept", "")
                if "text/html" in accept:
                    _expired_html = (
                        "<!DOCTYPE html>"
                        "<html><head><meta charset='utf-8'>"
                        "<title>Link Expired | K2M</title>"
                        "<style>body{font-family:Arial,sans-serif;max-width:540px;margin:80px auto;"
                        "padding:20px;text-align:center;color:#333}"
                        "h2{color:#c0392b}p{line-height:1.6}code{background:#f4f4f4;padding:2px 6px;"
                        "border-radius:3px}</style></head>"
                        "<body>"
                        "<h2>Your payment link has expired</h2>"
                        "<p>This enrollment payment link is no longer valid.</p>"
                        "<p>To get a fresh link, open Discord and type "
                        "<code>/renew</code> in a DM to KIRA, or visit the <strong>#help</strong> channel.</p>"
                        "<p>If you need further assistance, contact your facilitator directly.</p>"
                        "</body></html>"
                    )
                    return web.Response(
                        text=_expired_html,
                        content_type="text/html",
                        status=410,
                    )
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
            if not _is_valid_mpesa_code(mpesa_code):
                return web.json_response(
                    {
                        "success": False,
                        "error": (
                            "M-Pesa codes are 10 characters (letters and numbers only, "
                            "for example QGJ8YOAT3T). Check your M-Pesa SMS and try again."
                        ),
                    },
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
            student_email = _safe_get(row, COL_EMAIL)
            student_name = _safe_get(row, COL_NAME) or student_email.split("@")[0]
            first_name = student_name.split(" ")[0]
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

            # Task 7.5 anchor/state reset: start pending timer from M-Pesa submission moment.
            try:
                store = _resolve_store()
                if hasattr(store, "set_payment_pending_since"):
                    store.set_payment_pending_since(student_email, datetime.now(timezone.utc))
                if hasattr(store, "set_payment_silence_dm_sent"):
                    store.set_payment_silence_dm_sent(student_email, False)
                if hasattr(store, "set_payment_escalation_dm_sent"):
                    store.set_payment_escalation_dm_sent(student_email, False)
                if hasattr(store, "set_unverifiable_dm_sent"):
                    store.set_unverifiable_dm_sent(student_email, False)
            except Exception as exc:
                logger.warning("Task 7.5: failed to update payment pending anchors for %s: %s", student_email, exc)

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

            # Task 7.5 (Decision H-02): Immediate KIRA DM — fire-and-forget, never block 200.
            student_discord_id = _extract_discord_id(_safe_get(row, COL_DISCORD_ID))
            if student_discord_id and self._bot:
                async def _send_immediate_payment_dm(discord_id: str, name: str) -> None:
                    try:
                        user = await self._bot.fetch_user(int(discord_id))
                        await user.send(
                            f"Hey {name} - payment received! "
                            "Step 4 of 4: facilitator verifies (usually 24 hours). "
                            "I will DM you when you are activated."
                        )
                        logger.info("Task 7.5: immediate payment DM sent to discord_id=%s", discord_id)
                    except Exception as exc:
                        logger.warning("Task 7.5: immediate payment DM failed for %s: %s", discord_id, exc)

                asyncio.create_task(_send_immediate_payment_dm(student_discord_id, first_name))

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
