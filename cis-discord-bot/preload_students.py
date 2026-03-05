#!/usr/bin/env python3
"""
preload_students.py â€” Sheets â†’ PostgreSQL student sync
Task 7.6 / Decision H-06: Google Sheets is the enrollment source of truth.
                            PostgreSQL is the runtime source of truth.

USAGE (Trevor runs manually):
    python preload_students.py [--dry-run]

RUN TWICE:
    1. 48 hours before cohort start (SOP M-03)
    2. After every late enrollment

WHAT IT DOES:
    - Reads the student roster from Google Sheets via the Sheets API
    - Upserts each enrolled/confirmed student into PostgreSQL
    - Idempotent: safe to run multiple times (ON CONFLICT DO UPDATE)
    - Respects manual_override_timestamp: does NOT overwrite Trevor's
      manual Sheets edits for runtime fields (GAP FIX #3)

NIGHTLY ENGAGEMENT SYNC (Decision H-06 / GAP FIX #3):
    After cohort launch, a nightly job should call sync_engagement_back_to_sheets()
    which writes bot-generated runtime fields (zone, interaction_count, onboarding_stop)
    BACK to Sheets â€” but only for rows where student.last_active is NEWER than
    Sheets.manual_override_timestamp.

ENVIRONMENT VARIABLES REQUIRED:
    DATABASE_URL          â€” PostgreSQL URL (from Railway)
    GOOGLE_SHEETS_CREDS   â€” path to service account JSON (or inline JSON)
    GOOGLE_SHEETS_ID      â€” Spreadsheet ID (from URL)
    GOOGLE_SHEETS_RANGE   â€” Sheet range, e.g. "Student Roster!A:Z" (default used if not set)
    COHORT_ID             â€” default "cohort-1"
    COHORT_START_DATE     â€” ISO date, e.g. "2026-04-01"

SHEETS COLUMN MAPPING (canonical, from 5-5-sheets-templates.md):
    A  â€” Name (first + last)
    B  â€” Email
    C  â€” Phone
    D  â€” Discord ID (written by bot after join)
    E  â€” Profession
    R  â€” invite_code (written by /api/interest)
    L  â€” Payment status (Pending / Confirmed / Unverifiable)
    T  â€” manual_override_timestamp (Trevor sets this when manually editing a row)
"""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load .env from the bot directory
BOT_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BOT_DIR / ".env", override=False)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("preload_students")


# ---------------------------------------------------------------------------
# Column indices (0-based, from Sheets A=0)
# ---------------------------------------------------------------------------

COL_NAME = 0        # A
COL_EMAIL = 1       # B
COL_PHONE = 2       # C
COL_DISCORD_ID = 3  # D
COL_PROFESSION = 4  # E
COL_PAYMENT = 11    # L  (Pending / Confirmed / Unverifiable)
COL_INVITE = 17     # R  (invite_code)
COL_MANUAL_TS = 19  # T  (manual_override_timestamp)


def _load_json_source(source: str) -> Dict[str, Any]:
    """Load JSON from inline payload or filesystem path."""
    if source.strip().startswith("{"):
        return json.loads(source)
    with open(source, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_sheets_credentials_config(creds_path: Optional[str] = None) -> Dict[str, Any]:
    """Load Google credentials config from env or explicit path."""
    creds_source = creds_path or os.getenv("GOOGLE_SHEETS_CREDS", "")
    if not creds_source:
        raise ValueError("GOOGLE_SHEETS_CREDS env var not set (path or inline JSON)")
    return _load_json_source(creds_source)


def _build_sheets_service(
    creds_path: Optional[str] = None,
    read_only: bool = True,
):
    """Create an authenticated Google Sheets API client."""
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Google Sheets libraries not installed. "
            "Run: pip install google-auth google-api-python-client"
        ) from exc

    scopes = (
        ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        if read_only
        else ["https://www.googleapis.com/auth/spreadsheets"]
    )
    cred_info = _load_sheets_credentials_config(creds_path=creds_path)

    if cred_info.get("type") == "service_account":
        credentials = Credentials.from_service_account_info(cred_info, scopes=scopes)
    elif "installed" in cred_info:
        # OAuth desktop credentials + refresh token payload fallback.
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials as UserCredentials

        token_source = os.getenv("GOOGLE_SHEETS_TOKEN", "").strip()
        if not token_source:
            raise ValueError(
                "GOOGLE_SHEETS_TOKEN is required when GOOGLE_SHEETS_CREDS is OAuth client JSON"
            )
        token_info = _load_json_source(token_source)
        installed = cred_info["installed"]
        token_scopes = token_info.get("scopes")
        if isinstance(token_scopes, str):
            token_scopes = [token_scopes]
        effective_scopes = token_scopes or scopes
        credentials = UserCredentials(
            token=token_info.get("token"),
            refresh_token=token_info.get("refresh_token"),
            token_uri=token_info.get("token_uri") or installed.get("token_uri"),
            client_id=token_info.get("client_id") or installed.get("client_id"),
            client_secret=token_info.get("client_secret") or installed.get("client_secret"),
            scopes=effective_scopes,
        )
        if not credentials.valid and credentials.refresh_token:
            credentials.refresh(Request())
    else:
        raise ValueError(
            "Unsupported GOOGLE_SHEETS_CREDS format. Provide service-account JSON or OAuth client JSON."
        )

    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


def _parse_timestamp(value: Any) -> Optional[datetime]:
    """Parse a timestamp from DB/Sheets string values."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None


def _format_timestamp_for_sheet(value: Any) -> str:
    """Format DB timestamps for deterministic sheet writes."""
    ts = _parse_timestamp(value)
    if ts is None:
        return ""
    return ts.isoformat(sep=" ", timespec="seconds")


# ---------------------------------------------------------------------------
# Sheets reader
# ---------------------------------------------------------------------------

def read_roster_from_sheets(
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
) -> List[List[str]]:
    """
    Fetch student roster rows from Google Sheets.
    Requires google-auth + google-api-python-client in environment.
    Returns list of rows (each row is a list of cell values).
    """
    service = _build_sheets_service(creds_path=creds_path, read_only=True)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=sheet_range,
    ).execute()

    rows = result.get("values", [])
    logger.info("Fetched %s rows from Sheets (range: %s)", len(rows), sheet_range)
    return rows


def read_roster_from_csv(csv_path: str) -> List[List[str]]:
    """
    Fallback: read student roster from a CSV export of the Google Sheet.
    Useful for offline testing or when Sheets API is unavailable.
    """
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    logger.info("Loaded %s rows from CSV: %s", len(rows), csv_path)
    return rows


def _safe_get(row: List[str], idx: int, default: str = "") -> str:
    """Safely get cell value from a row, returning default if out of bounds."""
    if idx < len(row):
        return (row[idx] or "").strip()
    return default


def parse_student_rows(
    rows: List[List[str]],
    cohort_id: str = "cohort-1",
    cohort_start_date: str = "2026-04-01",
    skip_header: bool = True,
) -> List[Dict[str, Any]]:
    """
    Parse raw Sheets rows into structured student dicts.
    Only returns rows where payment status is 'Confirmed'.
    """
    students = []
    start_idx = 1 if skip_header else 0

    for i, row in enumerate(rows[start_idx:], start=start_idx + 1):
        if not row:
            continue

        name = _safe_get(row, COL_NAME)
        email = _safe_get(row, COL_EMAIL)
        payment = _safe_get(row, COL_PAYMENT).lower()
        invite_code = _safe_get(row, COL_INVITE)

        if not email:
            logger.debug("Row %s: skipping (no email)", i)
            continue

        if payment not in ("confirmed", "yes", "paid", "âœ“"):
            logger.debug("Row %s: skipping %s (payment=%s)", i, email, payment)
            continue

        # Split name into first/last (best effort)
        name_parts = name.strip().split()
        last_name = name_parts[-1] if len(name_parts) > 1 else ""

        students.append({
            "enrollment_email": email,
            "enrollment_name": name,
            "last_name": last_name,
            "invite_code": invite_code or f"k2m-{email.split('@')[0][:12]}",
            "cohort_id": cohort_id,
            "start_date": cohort_start_date,
            "enrollment_status": "enrolled",
            "payment_status": "confirmed",
        })

    logger.info("Parsed %s confirmed students from roster", len(students))
    return students


# ---------------------------------------------------------------------------
# PostgreSQL upsert
# ---------------------------------------------------------------------------

def upsert_students_to_pg(
    students: List[Dict[str, Any]],
    database_url: str,
    dry_run: bool = False,
) -> int:
    """
    Upsert student records into PostgreSQL.
    Returns count of upserted rows.
    Decision H-06: idempotent, safe to run multiple times.
    """
    try:
        import psycopg2
    except ImportError:
        logger.error("psycopg2 not installed. Run: pip install psycopg2-binary")
        sys.exit(1)

    if dry_run:
        logger.info("[DRY RUN] Would upsert %s students â€” no changes written", len(students))
        for s in students:
            logger.info("  [DRY RUN] %s <%s> invite=%s", s["enrollment_name"], s["enrollment_email"], s["invite_code"])
        return 0

    conn = psycopg2.connect(dsn=database_url)
    cursor = conn.cursor()
    upserted = 0

    for student in students:
        # Use invite_code as the stable upsert anchor (not discord_id, which may not exist yet)
        cursor.execute(
            """
            INSERT INTO students (
                discord_id,
                enrollment_email,
                enrollment_name,
                last_name,
                invite_code,
                cohort_id,
                start_date,
                enrollment_status,
                payment_status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (discord_id) DO UPDATE SET
                enrollment_email   = EXCLUDED.enrollment_email,
                enrollment_name    = EXCLUDED.enrollment_name,
                last_name          = EXCLUDED.last_name,
                invite_code        = EXCLUDED.invite_code,
                cohort_id          = EXCLUDED.cohort_id,
                enrollment_status  = EXCLUDED.enrollment_status,
                payment_status     = EXCLUDED.payment_status
            """,
            (
                # Placeholder discord_id until on_member_join fires and links real ID
                f"__pending__{student['enrollment_email']}",
                student["enrollment_email"],
                student["enrollment_name"],
                student["last_name"],
                student["invite_code"],
                student["cohort_id"],
                student["start_date"],
                student["enrollment_status"],
                student["payment_status"],
            ),
        )
        upserted += 1
        logger.info(
            "Upserted: %s <%s> invite=%s",
            student["enrollment_name"],
            student["enrollment_email"],
            student["invite_code"],
        )

    conn.commit()
    cursor.close()
    conn.close()

    logger.info("âœ… Upserted %s students into PostgreSQL", upserted)
    return upserted


# ---------------------------------------------------------------------------
# Nightly engagement sync: PostgreSQL â†’ Sheets (Decision H-06 / GAP FIX #3)
# ---------------------------------------------------------------------------

def sync_engagement_back_to_sheets(
    database_url: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Nightly sync: write bot engagement data (zone, onboarding_stop, interaction_count)
    back to Google Sheets - but ONLY for rows where:

        student.last_active > sheet_row.manual_override_timestamp

    GAP FIX #3: Trevor's manual Sheets edits take precedence if they are
    newer than the student's last bot interaction. This prevents the nightly
    sync from overwriting Trevor's manual cluster/zone adjustments.

    Called nightly by the scheduler.
    """
    try:
        import psycopg2
    except ImportError:
        logger.error("psycopg2 not installed")
        return {"synced": 0, "skipped_manual": 0, "missing_sheet_row": 0}

    col_onboarding_stop = os.getenv("SHEETS_SYNC_ONBOARDING_STOP_COL", "AB").strip().upper() or "AB"
    col_last_active = os.getenv("SHEETS_SYNC_LAST_ACTIVE_COL", "AC").strip().upper() or "AC"
    col_frame_sessions = os.getenv("SHEETS_SYNC_FRAME_SESSIONS_COL", "AD").strip().upper() or "AD"
    sheet_name = sheet_range.split("!", 1)[0] if "!" in sheet_range else "Student Roster"

    conn = psycopg2.connect(dsn=database_url)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT discord_id,
               enrollment_email,
               onboarding_stop,
               last_interaction,
               COALESCE(frame_sessions_count, interaction_count, 0) AS frame_sessions_count,
               zone
          FROM students
         WHERE discord_id IS NOT NULL
           AND discord_id NOT LIKE '__pending__%'
        """
    )
    db_rows = cursor.fetchall()
    conn.close()

    try:
        sheet_rows = read_roster_from_sheets(
            spreadsheet_id=spreadsheet_id,
            sheet_range=sheet_range,
            creds_path=creds_path,
        )
    except Exception as exc:
        logger.error("Failed to read roster for sync-back: %s", exc)
        return {"synced": 0, "skipped_manual": 0, "missing_sheet_row": 0}

    email_to_sheet_row: Dict[str, tuple[int, List[str]]] = {}
    for idx, row in enumerate(sheet_rows[1:], start=2):
        email = _safe_get(row, COL_EMAIL).lower()
        if email and email not in email_to_sheet_row:
            email_to_sheet_row[email] = (idx, row)

    synced = 0
    skipped_manual = 0
    missing_sheet_row = 0
    updates: List[Dict[str, Any]] = []

    for row in db_rows:
        (
            discord_id, email, onboarding_stop, last_active,
            frame_sessions_count, zone,
        ) = row

        email_key = (email or "").strip().lower()
        if not email_key:
            continue

        sheet_lookup = email_to_sheet_row.get(email_key)
        if not sheet_lookup:
            logger.warning("Skipping %s: no matching row in sheet", email_key)
            missing_sheet_row += 1
            continue

        sheet_row_num, sheet_row = sheet_lookup
        manual_override_raw = _safe_get(sheet_row, COL_MANUAL_TS)
        ts_manual = _parse_timestamp(manual_override_raw)
        ts_active = _parse_timestamp(last_active)

        # GAP FIX #3: skip if Trevor manually edited this row more recently
        if ts_manual and ts_active and ts_manual > ts_active:
            logger.debug(
                "Skipping %s - manual override (%s) newer than last_active (%s)",
                email_key, ts_manual, ts_active,
            )
            skipped_manual += 1
            continue

        if dry_run:
            logger.info(
                "[DRY RUN] Would sync %s: zone=%s onboarding_stop=%s last_active=%s frame_sessions_count=%s",
                email_key,
                zone,
                onboarding_stop,
                _format_timestamp_for_sheet(last_active),
                frame_sessions_count,
            )
            synced += 1
            continue

        updates.extend(
            [
                {
                    "range": f"{sheet_name}!{col_onboarding_stop}{sheet_row_num}",
                    "values": [[str(onboarding_stop or 0)]],
                },
                {
                    "range": f"{sheet_name}!{col_last_active}{sheet_row_num}",
                    "values": [[_format_timestamp_for_sheet(last_active)]],
                },
                {
                    "range": f"{sheet_name}!{col_frame_sessions}{sheet_row_num}",
                    "values": [[str(frame_sessions_count or 0)]],
                },
            ]
        )
        synced += 1

    if updates:
        try:
            write_service = _build_sheets_service(creds_path=creds_path, read_only=False)
            write_service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={
                    "valueInputOption": "RAW",
                    "data": updates,
                },
            ).execute()
        except Exception as exc:
            logger.error("Sheets write-back failed: %s", exc)
            return {
                "synced": 0,
                "skipped_manual": skipped_manual,
                "missing_sheet_row": missing_sheet_row,
            }

    logger.info(
        "Engagement sync complete: %s synced, %s skipped (manual override), %s missing rows",
        synced,
        skipped_manual,
        missing_sheet_row,
    )
    return {
        "synced": synced,
        "skipped_manual": skipped_manual,
        "missing_sheet_row": missing_sheet_row,
    }

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preload K2M student roster from Google Sheets into PostgreSQL"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and show what would be upserted â€” no DB writes",
    )
    parser.add_argument(
        "--csv",
        metavar="PATH",
        help="Use a local CSV export instead of fetching from Sheets API",
    )
    parser.add_argument(
        "--sync-back",
        action="store_true",
        help="Run nightly engagement sync (PostgreSQL â†’ Sheets) instead of preload",
    )
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        logger.error("DATABASE_URL env var is required")
        sys.exit(1)

    if not (database_url.startswith("postgresql://") or database_url.startswith("postgres://")):
        logger.error("DATABASE_URL must be a PostgreSQL URL (got: %s...)", database_url[:30])
        sys.exit(1)

    if args.sync_back:
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID", "")
        sheet_range = os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z")
        creds_path = os.getenv("GOOGLE_SHEETS_CREDS", "")
        if not spreadsheet_id:
            logger.error("GOOGLE_SHEETS_ID env var required for --sync-back")
            sys.exit(1)
        sync_engagement_back_to_sheets(
            database_url=database_url,
            spreadsheet_id=spreadsheet_id,
            sheet_range=sheet_range,
            creds_path=creds_path,
            dry_run=args.dry_run,
        )
        return

    # --- Preload path ---
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID", "")
    sheet_range = os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z")
    cohort_id = os.getenv("COHORT_ID", "cohort-1")
    cohort_start_date = os.getenv("COHORT_START_DATE", "2026-04-01")

    if args.csv:
        raw_rows = read_roster_from_csv(args.csv)
    elif spreadsheet_id:
        raw_rows = read_roster_from_sheets(
            spreadsheet_id=spreadsheet_id,
            sheet_range=sheet_range,
        )
    else:
        logger.error(
            "Provide either --csv PATH or set GOOGLE_SHEETS_ID env var"
        )
        sys.exit(1)

    students = parse_student_rows(
        raw_rows,
        cohort_id=cohort_id,
        cohort_start_date=cohort_start_date,
    )

    if not students:
        logger.warning("No confirmed students found in roster. Check payment status column.")
        sys.exit(0)

    upsert_students_to_pg(students, database_url=database_url, dry_run=args.dry_run)

    if not args.dry_run:
        logger.info("")
        logger.info("âœ… preload_students.py complete.")
        logger.info("   Next step: ensure each student has received their unique invite link")
        logger.info("   (invite_code in Column R maps to the Discord invite KIRA generates)")


if __name__ == "__main__":
    main()


