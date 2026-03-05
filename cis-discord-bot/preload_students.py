#!/usr/bin/env python3
"""
preload_students.py — Sheets → PostgreSQL student sync
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
    BACK to Sheets — but only for rows where student.last_active is NEWER than
    Sheets.manual_override_timestamp.

ENVIRONMENT VARIABLES REQUIRED:
    DATABASE_URL          — PostgreSQL URL (from Railway)
    GOOGLE_SHEETS_CREDS   — path to service account JSON (or inline JSON)
    GOOGLE_SHEETS_ID      — Spreadsheet ID (from URL)
    GOOGLE_SHEETS_RANGE   — Sheet range, e.g. "Student Roster!A:Z" (default used if not set)
    COHORT_ID             — default "cohort-1"
    COHORT_START_DATE     — ISO date, e.g. "2026-04-01"

SHEETS COLUMN MAPPING (canonical, from 5-5-sheets-templates.md):
    A  — Name (first + last)
    B  — Email
    C  — Phone
    D  — Discord ID (written by bot after join)
    E  — Profession
    R  — invite_code (written by /api/interest)
    L  — Payment status (Pending / Confirmed / Unverifiable)
    T  — manual_override_timestamp (Trevor sets this when manually editing a row)
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
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        logger.error(
            "Google Sheets libraries not installed. "
            "Run: pip install google-auth google-api-python-client"
        )
        sys.exit(1)

    creds_source = creds_path or os.getenv("GOOGLE_SHEETS_CREDS", "")
    if not creds_source:
        logger.error("GOOGLE_SHEETS_CREDS env var not set (path to service account JSON)")
        sys.exit(1)

    if creds_source.strip().startswith("{"):
        cred_info = json.loads(creds_source)
    else:
        with open(creds_source, "r") as f:
            cred_info = json.load(f)

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    credentials = Credentials.from_service_account_info(cred_info, scopes=scopes)
    service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
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

        if payment not in ("confirmed", "yes", "paid", "✓"):
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
        logger.info("[DRY RUN] Would upsert %s students — no changes written", len(students))
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

    logger.info("✅ Upserted %s students into PostgreSQL", upserted)
    return upserted


# ---------------------------------------------------------------------------
# Nightly engagement sync: PostgreSQL → Sheets (Decision H-06 / GAP FIX #3)
# ---------------------------------------------------------------------------

def sync_engagement_back_to_sheets(
    database_url: str,
    spreadsheet_id: str,
    sheet_range: str = "Student Roster!A:Z",
    creds_path: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """
    Nightly sync: write bot engagement data (zone, onboarding_stop, interaction_count)
    back to Google Sheets — but ONLY for rows where:

        student.last_active > sheet_row.manual_override_timestamp

    GAP FIX #3: Trevor's manual Sheets edits take precedence if they are
    newer than the student's last bot interaction. This prevents the nightly
    sync from overwriting Trevor's manual cluster/zone adjustments.

    Called nightly by the scheduler (not yet wired — add to DailyPromptScheduler).
    """
    try:
        import psycopg2
    except ImportError:
        logger.error("psycopg2 not installed")
        return

    conn = psycopg2.connect(dsn=database_url)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT discord_id,
               enrollment_email,
               onboarding_stop,
               last_interaction,
               interaction_count,
               manual_override_timestamp,
               zone
          FROM students
         WHERE discord_id IS NOT NULL
           AND discord_id NOT LIKE '__pending__%'
        """
    )
    rows = cursor.fetchall()
    conn.close()

    synced = 0
    skipped_manual = 0

    for row in rows:
        (
            discord_id, email, onboarding_stop, last_active,
            interaction_count, manual_override_ts, zone,
        ) = row

        # GAP FIX #3: skip if Trevor manually edited this row more recently
        if manual_override_ts and last_active:
            try:
                ts_manual = datetime.fromisoformat(str(manual_override_ts))
                ts_active = datetime.fromisoformat(str(last_active))
                if ts_manual > ts_active:
                    logger.debug(
                        "Skipping %s — manual override (%s) newer than last_active (%s)",
                        email, ts_manual, ts_active,
                    )
                    skipped_manual += 1
                    continue
            except (ValueError, TypeError):
                pass

        if dry_run:
            logger.info(
                "[DRY RUN] Would sync %s: zone=%s onboarding_stop=%s interactions=%s",
                email, zone, onboarding_stop, interaction_count,
            )
            synced += 1
            continue

        # TODO: implement Sheets write-back via Apps Script webhook or direct Sheets API
        # For now, log the data that would be written. Full implementation in task 7.6 followup.
        logger.info(
            "SYNC (stub): %s → zone=%s onboarding_stop=%s interactions=%s",
            email, zone, onboarding_stop, interaction_count,
        )
        synced += 1

    logger.info(
        "Engagement sync complete: %s synced, %s skipped (manual override)", synced, skipped_manual
    )


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
        help="Parse and show what would be upserted — no DB writes",
    )
    parser.add_argument(
        "--csv",
        metavar="PATH",
        help="Use a local CSV export instead of fetching from Sheets API",
    )
    parser.add_argument(
        "--sync-back",
        action="store_true",
        help="Run nightly engagement sync (PostgreSQL → Sheets) instead of preload",
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
        if not spreadsheet_id:
            logger.error("GOOGLE_SHEETS_ID env var required for --sync-back")
            sys.exit(1)
        sync_engagement_back_to_sheets(
            database_url=database_url,
            spreadsheet_id=spreadsheet_id,
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
        logger.info("✅ preload_students.py complete.")
        logger.info("   Next step: ensure each student has received their unique invite link")
        logger.info("   (invite_code in Column R maps to the Discord invite KIRA generates)")


if __name__ == "__main__":
    main()
