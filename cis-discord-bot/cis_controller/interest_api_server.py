"""
Interest Form API Server - Task 7.1 Implementation

Provides HTTP POST /api/interest endpoint for landing page enrollment.
Integrates with Google Sheets + Brevo email using existing infrastructure.

ENVIRONMENT VARIABLES REQUIRED:
    DATABASE_URL          - PostgreSQL URL (from Railway)
    GOOGLE_SHEETS_CREDS  - Google service account credentials (JSON)
    GOOGLE_SHEETS_ID     - Student Roster spreadsheet ID
    GOOGLE_SHEETS_RANGE  - Sheet range, default "Student Roster!A:Z"
    BREVO_API_KEY         - Brevo API key for sending emails
    ENROLLMENT_CAP        - Max paid enrollments (default: 30)

INTEGRATION:
    - Google Sheets API (from preload_students.py)
    - EmailService (cis_controller/email_service.py)
    - Pattern from ParentUnsubscribeServer (aiohttp)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from aiohttp import web
from dotenv import load_dotenv

# Load Sheets integration functions
import sys
from pathlib import Path

BOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BOT_DIR))

from preload_students import (
    _build_sheets_service,
    _load_json_source,
    _safe_get,
)

logger = logging.getLogger(__name__)

# Column indices (from preload_students.py)
COL_NAME = 0        # A
COL_EMAIL = 1       # B
COL_PHONE = 2       # C
COL_DISCORD_ID = 3  # D
COL_PROFESSION = 4  # E
COL_PAYMENT = 11    # L  (Payment status)
COL_INVITE = 17     # R  (invite_code)

ENROLLMENT_CAP = int(os.getenv("ENROLLMENT_CAP", "30").strip())


def _load_sheets_credentials(creds_path: Optional[str] = None) -> Dict:
    """Load Google Sheets credentials."""
    creds_source = creds_path or os.getenv("GOOGLE_SHEETS_CREDS", "")
    if not creds_source:
        raise ValueError("GOOGLE_SHEETS_CREDS env var not set")
    return _load_json_source(creds_source)


async def check_enrollment_cap(
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> Dict[str, int]:
    """
    Check current enrollment cap status by counting paid students.

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

        # Start from row 2 (skip header)
        for row in rows[1:]:
            payment = _safe_get(row, COL_PAYMENT).lower()
            if payment in ("paid", "confirmed", "yes"):
                paid_count += 1

        available = max(0, ENROLLMENT_CAP - paid_count)

        logger.info(
            f"Enrollment check: {paid_count}/{ENROLLMENT_CAP} paid, {available} available"
        )

        return {
            "paid_count": paid_count,
            "cap": ENROLLMENT_CAP,
            "available": available,
        }
    except Exception as exc:
        logger.error(f"Failed to check enrollment cap: {exc}")
        # On error, assume cap reached (fail-safe)
        return {"paid_count": ENROLLMENT_CAP, "cap": ENROLLMENT_CAP, "available": 0}


async def check_duplicate_email(
    email: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> bool:
    """
    Check if email already exists in Column B.

    Returns:
        True if duplicate found, False otherwise
    """
    try:
        service = _build_sheets_service(creds_path=creds_path, read_only=True)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
        ).execute()

        rows = result.get("values", [])
        email_lower = email.strip().lower()

        for row in rows[1:]:  # Skip header
            existing_email = _safe_get(row, COL_EMAIL).lower()
            if existing_email == email_lower:
                logger.info(f"Duplicate email found: {email}")
                return True

        return False
    except Exception as exc:
        logger.error(f"Failed to check duplicate email: {exc}")
        # On error, assume NOT duplicate (allow submission)
        return False


async def append_to_student_roster(
    name: str,
    email: str,
    phone: str,
    profession: str,
    invite_code: str,
    spreadsheet_id: str,
    creds_path: Optional[str] = None,
) -> bool:
    """
    Append new student to Google Sheets Student Roster.

    Returns:
        True if successful, False otherwise
    """
    try:
        service = _build_sheets_service(creds_path=creds_path, read_only=False)
        sheet = service.spreadsheets().values()

        # Prepare row data (A-R columns)
        # A=Name, B=Email, C=Phone, D=DiscordID, E=Profession, ..., R=invite_code
        row_data = [[
            name,              # A
            email,             # B
            phone,             # C
            "",                # D (Discord ID - filled later)
            profession,        # E
            "", "", "", "", "",  # F-J (empty for now)
            "", "", "", "",  # K-O (empty for now)
            "Pending",         # P (Payment status - empty)
            "",                # Q (empty)
            invite_code,       # R (invite_code placeholder)
        ]]

        # Append to sheet
        sheet_name = sheet_range.split("!", 1)[0] if "!" in sheet_range else "Student Roster"
        range_spec = f"{sheet_name}!A{len(row_data) + 2}:R{len(row_data) + 2}"

        body = {
            "values": row_data,
            "valueInputOption": "RAW",
        }

        service.append(
            spreadsheetId=spreadsheet_id,
            range=range_spec,
            body=body,
        ).execute()

        logger.info(f"Appended to Student Roster: {email} (invite_code={invite_code})")
        return True

    except Exception as exc:
        logger.error(f"Failed to append to Student Roster: {exc}")
        return False


async def send_brevo_email(
    to_email: str,
    first_name: str,
    waitlisted: bool,
    waitlist_number: Optional[int] = None,
    template_params: Optional[Dict] = None,
) -> bool:
    """
    Send Brevo email (Email #1 or Email #5) using EmailService.

    Args:
        to_email: Recipient email
        first_name: Student's first name
        waitlisted: True for Email #5, False for Email #1
        waitlist_number: Position in waitlist (if applicable)
        template_params: Additional template variables

    Returns:
        True if successful, False otherwise
    """
    try:
        from cis_controller.email_service import EmailService

        email_service = EmailService()

        # Extract first name from full name
        first_name_only = first_name.strip().split()[0] if first_name else "there"

        if waitlisted:
            # TODO: Replace with actual Brevo Email #5 template ID
            # For now, sending simple HTML email
            subject = "You're on our priority list! 🌟"
            waitlist_num = waitlist_number or (ENROLLMENT_CAP + 1)

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #050608; color: #13d7d0; padding: 20px; text-align: center; border-radius: 12px 12px 0 0; }}
                    .content {{ background: #0b0f14; color: #d1d5db; padding: 30px; border: 1px solid #1f2937; }}
                    .footer {{ background: #050608; color: #9ca3af; padding: 15px; text-align: center; font-size: 12px; border-radius: 0 0 12px 12px; }}
                    h1 {{ margin: 0; font-size: 32px; }}
                    .cta {{ display: inline-block; padding: 12px 24px; background: linear-gradient(90deg, #13d7d0 0%, #39e6de 100%); color: #041014; text-decoration: none; border-radius: 999px; font-weight: bold; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>You're on our priority list! 🌟</h1>
                    </div>
                    <div class="content">
                        <p>Hey {first_name_only},</p>
                        <p>This cohort filled up faster than expected — you're <strong>#{waitlist_num}</strong> on our priority list for the next cohort.</p>
                        <p>We cap each cohort at {ENROLLMENT_CAP} students to ensure the best experience. Your spot is secured, and you'll be the <strong>first to know</strong> when we open enrollment.</p>
                        <p>In the meantime, check out what past students have created!</p>
                        <p style="text-align: center;">
                            <a href="https://k2m-edtech.program" class="cta">Explore the Program</a>
                        </p>
                    </div>
                    <div class="footer">
                        <p>Questions? Just reply to this email.</p>
                        <p>&copy; {datetime.now().year} K2M Labs. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            # TODO: Replace with actual Brevo Email #1 template ID
            # For now, sending simple HTML email
            subject = "Your Discord invitation is ready! 🚀"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #050608; color: #13d7d0; padding: 20px; text-align: center; border-radius: 12px 12px 0 0; }}
                    .content {{ background: #0b0f14; color: #d1d5db; padding: 30px; border: 1px solid #1f2937; }}
                    .footer {{ background: #050608; color: #9ca3af; padding: 15px; text-align: center; font-size: 12px; border-radius: 0 0 12px 12px; }}
                    h1 {{ margin: 0; font-size: 32px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to K2M! 🚀</h1>
                    </div>
                    <div class="content">
                        <p>Hey {first_name_only},</p>
                        <p>Thanks for your interest in K2M's AI Thinking Skills Cohort!</p>
                        <p>We've received your submission and you're enrolled. Next steps will arrive in your email soon.</p>
                        <p>Check your inbox (and spam folder) for your Discord invitation.</p>
                    </div>
                    <div class="footer">
                        <p>Questions? Just reply to this email.</p>
                        <p>&copy; {datetime.now().year} K2M Labs. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

        result = await email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )

        if result.success:
            logger.info(f"Email sent successfully to {to_email} (waitlisted={waitlisted})")
        else:
            logger.warning(f"Email send failed: {result.error_message}")

        return result.success

    except Exception as exc:
        logger.error(f"Failed to send email: {exc}")
        return False


class InterestAPIServer:
    """HTTP API server for /api/interest endpoint."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8081,  # Different port than unsubscribe server
        spreadsheet_id: Optional[str] = None,
        creds_path: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEETS_ID", "")
        self.creds_path = creds_path or os.getenv("GOOGLE_SHEETS_CREDS", "")
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.BaseSite] = None

    async def _handle_cors(self, request: web.Request) -> web.Response:
        """Handle CORS preflight requests."""
        return web.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    async def _handle_interest(self, request: web.Request) -> web.Response:
        """Handle POST /api/interest - enrollment form submission."""
        try:
            # Parse JSON body
            data = await request.json()

            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            phone = data.get("phone", "").strip()
            profession = data.get("profession", "Other").strip()

            # Validation
            if not name or not email:
                return web.json_response(
                    {"success": False, "error": "Name and email are required"},
                    status=400,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                    },
                )

            # Check duplicate email
            is_duplicate = await check_duplicate_email(
                email=email,
                spreadsheet_id=self.spreadsheet_id,
                creds_path=self.creds_path,
            )

            if is_duplicate:
                return web.json_response(
                    {
                        "success": False,
                        "error": "We already have your submission! Check your email for your Discord invitation.",
                    },
                    status=409,  # Conflict
                    headers={
                        "Access-Control-Allow-Origin": "*",
                    },
                )

            # Check enrollment cap
            cap_status = await check_enrollment_cap(
                spreadsheet_id=self.spreadsheet_id,
                creds_path=self.creds_path,
            )

            waitlisted = cap_status["available"] <= 0

            # Generate invite code (placeholder for Task 7.2)
            invite_code = f"k2m-{email.split('@')[0][:12]}"

            # Append to Sheets
            appended = await append_to_student_roster(
                name=name,
                email=email,
                phone=phone,
                profession=profession,
                invite_code=invite_code,
                spreadsheet_id=self.spreadsheet_id,
                creds_path=self.creds_path,
            )

            # Send email
            waitlist_number = None
            if waitlisted:
                waitlist_number = cap_status["paid_count"] - ENROLLMENT_CAP + 1

            email_sent = await send_brevo_email(
                to_email=email,
                first_name=name,
                waitlisted=waitlisted,
                waitlist_number=waitlist_number,
            )

            return web.json_response(
                {
                    "success": True,
                    "waitlisted": waitlisted,
                    "message": "Check your email for your Discord invitation!" if not waitlisted else "You're on our priority list for the next cohort!",
                },
                status=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                },
            )

        except json.JSONDecodeError:
            return web.json_response(
                {"success": False, "error": "Invalid JSON"},
                status=400,
                headers={
                    "Access-Control-Allow-Origin": "*",
                },
            )
        except Exception as exc:
            logger.error(f"Error handling interest request: {exc}", exc_info=True)
            return web.json_response(
                {"success": False, "error": "Internal server error"},
                status=500,
                headers={
                    "Access-Control-Allow-Origin": "*",
                },
            )

    async def start(self) -> None:
        """Start the Interest API HTTP server."""
        if self._runner is not None:
            return

        if not self.spreadsheet_id:
            logger.warning("GOOGLE_SHEETS_ID not set - Interest API server not starting")
            return

        app = web.Application()
        app.router.add_options("/api/interest", self._handle_cors)
        app.router.add_post("/api/interest", self._handle_interest)

        self._runner = web.AppRunner(app)
        await self._runner.setup()

        self._site = web.TCPSite(self._runner, host=self.host, port=self.port)
        await self._site.start()
        logger.info(
            "Interest API server listening on http://%s:%s/api/interest",
            self.host,
            self.port,
        )

    async def stop(self) -> None:
        """Stop the Interest API HTTP server."""
        if self._runner is None:
            return
        await self._runner.cleanup()
        self._runner = None
        self._site = None
        logger.info("Interest API server stopped")

    def stop_sync(self) -> None:
        """Best-effort sync-safe stop helper."""
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
