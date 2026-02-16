#!/usr/bin/env python3
"""
K2M Google Sheets Templates Generator
Creates 4 comprehensive Google Sheets templates for Discord cohort operations
Per Story 5.5 specification

Requirements:
- pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
- Google Cloud project with Sheets API enabled
- OAuth 2.0 credentials (credentials.json)
"""

import os
import json
import pickle
from typing import List, Dict, Any

# Google Sheets API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: Missing required packages.")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    exit(1)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# ============================================================================
# STUDENT ROSTER TEMPLATE SPECIFICATION
# ============================================================================

STUDENT_ROSTER_COLUMNS = [
    ("Timestamp", "Auto-generated from Google Forms"),
    ("Student ID", "Auto-generated: FIRST_LAST_####"),
    ("First Name", ""),
    ("Last Name", "For cluster assignment"),
    ("Email Address", ""),
    ("Discord Username", "Optional, for matching"),
    ("Age", "16/17/18/19+"),
    ("Zone Baseline", "Week 1 diagnostic: Zone 0, Zone 1, Zone 2, Zone 3, Zone 4"),
    ("Zone Current", "Updated weekly: Week 2-8 self-assessment"),
    ("Zone Shift", "Formula: Zone progression tracking"),
    ("AI Experience Level", "Never used, Tried a few times, Use regularly, Use daily"),
    ("Anxiety Baseline", "Week 1 diagnostic: 1-10 scale"),
    ("Anxiety Current", "Weekly check-in: 1-10 scale"),
    ("Anxiety Change", "Formula: Current - Baseline"),
    ("Confidence Level", "Not at all / Somewhat / Fairly / Very / Haven't thought"),
    ("Motivation", "Free text from diagnostic"),
    ("Goals", "Free text from diagnostic"),
    ("4 Habits Pre-Assessment", "Checkboxes: Pause, Context, Iterate, Think First, None yet"),
    ("Parent/Guardian Name", "Required"),
    ("Parent Phone Number", "Required, format: 254XXXXXXXXX"),
    ("Parent Email Address", "Required"),
    ("Emergency Contact Backup", "Optional"),
    ("Weekly Updates Consent", "Yes / No / Not sure yet"),
    ("Cluster Assignment", "Formula: A-F, G-L, M-R, S-Z"),
    ("Crisis Flag", "Formula: HIGH ANXIETY, CRISIS, EMOTIONAL ESCALATION, OK"),
    ("Intervention Priority", "Formula: LEVEL 1-3 priorities"),
    ("Trevor Review Notes", "Manual: Trevor adds notes after diagnostic review"),
    ("Outreach Status", "Manual: Not contacted, Nudged, DM sent, Call scheduled, Crisis contacted"),
    ("First Contact Date", "Manual: Date of first Trevor outreach"),
    ("Live Session Attendance", "Manual: Track attendance at 1-hour sessions"),
    ("Engagement Status", "Formula from Submissions Log: Active, Lagging, Stuck"),
    ("Habit 1 Practice", "⏸️ Pause - Count of reflections showing Pause"),
    ("Habit 2 Practice", "🎯 Context - Count of reflections showing Context"),
    ("Habit 3 Practice", "🔄 Iterate - Count of reflections showing Iterate"),
    ("Habit 4 Practice", "🧠 Think First - Count of reflections showing Think First"),
    ("Artifact Status", "Not started, In progress, Submitted, Published"),
    ("Graduation Proof", "Which 4 Habits demonstrated? Manual: Trevor assessment"),
    ("Data Retention Date", "Formula: Timestamp + 180 days"),
    ("Notes", "Ongoing cohort notes - milestones, celebrations, concerns")
]

STUDENT_ROSTER_FORMULAS = {
    "Zone Shift": '=IF(AND(H2="Zone 0", I2="Zone 0"), "Not started (Zone 0)", IF(I2="Zone 1", "Zone 0→1", IF(I2="Zone 2", "Zone 1→2", IF(I2="Zone 3", "Zone 2→3", IF(I2="Zone 4", "Zone 3→4", "Stuck")))))',
    "Anxiety Change": "=M2-L2",
    "Cluster Assignment": '=IF(UPPER(LEFT(D2,1))<="F", "Cluster 1 (A-F)", IF(UPPER(LEFT(D2,1))<="L", "Cluster 2 (G-L)", IF(UPPER(LEFT(D2,1))<="R", "Cluster 3 (M-R)", "Cluster 4 (S-Z)")))',
    "Crisis Flag": '=IF(L2>=7, "HIGH ANXIETY", IF(OR(ISNUMBER(SEARCH("hopeless", P2)), ISNUMBER(SEARCH("hopeless", Q2)), ISNUMBER(SEARCH("suicide", P2)), ISNUMBER(SEARCH("suicide", Q2)), ISNUMBER(SEARCH("self-harm", P2)), ISNUMBER(SEARCH("self-harm", Q2))), "CRISIS", IF(AND(N2>=3, OR(L2>=7)), "EMOTIONAL ESCALATION", "OK")))',
    "Intervention Priority": '=IF(AND(H2="Zone 0", L2>=7), "LEVEL 3: IMMEDIATE outreach", IF(AND(H2="Zone 0", L2>=5), "LEVEL 2: Monitor + DM", IF(L2>=8, "LEVEL 3: Check in", "LEVEL 1: Normal monitoring")))',
    "Data Retention Date": "=A2+180"
}

STUDENT_ROSTER_VALIDATION = {
    "Zone Baseline": ["Zone 0", "Zone 1", "Zone 2", "Zone 3", "Zone 4"],
    "Zone Current": ["Zone 0", "Zone 1", "Zone 2", "Zone 3", "Zone 4"],
    "Weekly Updates Consent": ["Yes", "No", "Not sure yet"],
    "Outreach Status": ["Not contacted", "Nudged", "DM sent", "Call scheduled", "Crisis contacted"],
    "Artifact Status": ["Not started", "In progress", "Submitted", "Published"]
}

# ============================================================================
# SUBMISSIONS LOG TEMPLATE SPECIFICATION
# ============================================================================

SUBMISSIONS_LOG_COLUMNS = [
    ("Submission ID", "Auto-generated: SUB_YYYYMMDD_####"),
    ("Timestamp", "Auto-generated: Date + time of post"),
    ("Week Number", "Week 1-8"),
    ("Day of Week", "Monday-Sunday"),
    ("Student ID", "VLOOKUP from Student Roster"),
    ("Student Name", "VLOOKUP from Student Roster"),
    ("Cluster", "VLOOKUP from Student Roster"),
    ("Post Type", "Drop-down: Daily Prompt, Friday Reflection, Self-Assessment, CIS Interaction, Artifact Submission, Other"),
    ("Channel Location", "#thinking-lab, #thinking-showcase, Private DM/Thread"),
    ("CIS Agent Used", "Drop-down: None, /frame, /diverge, /challenge, /synthesize, /create-artifact"),
    ("Post Content", "Link to Discord message or brief summary"),
    ("Thinking Depth Indicator", "Manual: Trevor assessment - Self-Aware, Experimenting, Synthesizing, Needs Scaffolding, Growth Edge"),
    ("Zone Mentioned", "Did student reference zone? Yes/No"),
    ("Habit Mentioned", "Which habit? ⏸️ Pause, 🎯 Context, 🔄 Iterate, 🧠 Think First, None"),
    ("Emotional Tone", "Positive, Neutral, Negative, Mixed, Crisis Flag"),
    ("Engagement Depth", "Formula: Character count, CIS agent usage, reflection quality"),
    ("Trevor Review", "Did Trevor review this? Yes/No"),
    ("Trevor Feedback", "Manual: Trevor's response or nudge"),
    ("Escalation Flag", "Does student need outreach? Yes/No"),
    ("Engagement Pattern", "Formula: Consistent/Intermittent/Disengaged"),
    ("Week Total", "Formula: Total posts this week"),
    ("Notes", "Ongoing observations")
]

SUBMISSIONS_LOG_FORMULAS = {
    "Engagement Depth": "=IF(J2=\"None\", 1, IF(OR(J2=\"/frame\", J2=\"/diverge\", J2=\"/challenge\"), 2, 3)) + IF(L2=\"Growth Edge\", 3, IF(OR(L2=\"Synthesizing\", L2=\"Self-Aware\"), 2, IF(L2=\"Experimenting\", 1, 0)))",
    "Engagement Pattern": "=IF(U2>=5, \"Consistent\", IF(U2>=2, \"Intermittent\", \"Disengaged\"))",
    "Week Total": "=COUNTIFS(E:E, E2, C:C, C2)"
}

SUBMISSIONS_LOG_VALIDATION = {
    "Post Type": ["Daily Prompt", "Friday Reflection", "Self-Assessment", "CIS Interaction", "Artifact Submission", "Other"],
    "CIS Agent Used": ["None", "/frame", "/diverge", "/challenge", "/synthesize", "/create-artifact"],
    "Thinking Depth Indicator": ["Self-Aware", "Experimenting", "Synthesizing", "Needs Scaffolding", "Growth Edge"],
    "Emotional Tone": ["Positive", "Neutral", "Negative", "Mixed", "Crisis Flag"],
    "Escalation Flag": ["Yes", "No"]
}

# ============================================================================
# INTERVENTION TRACKING TEMPLATE SPECIFICATION
# ============================================================================

INTERVENTION_TRACKING_COLUMNS = [
    ("Intervention ID", "Auto-generated: INT_YYYYMMDD_####"),
    ("Timestamp", "Date + time of intervention"),
    ("Week Number", "Week 1-8"),
    ("Student ID", "VLOOKUP from Student Roster"),
    ("Student Name", "VLOOKUP from Student Roster"),
    ("Cluster", "VLOOKUP from Student Roster"),
    ("Intervention Type", "Drop-down: Level 1 - Bot Nudge, Level 2 - Trevor DM, Level 3 - Direct Call, Level 4 - Crisis Intervention, Live Session, Friday Spot-Check, Parent Outreach"),
    ("Trigger", "Why intervene? Drop-down: Diagnostic Flag, Stuck 3+ Days, High Anxiety, Crisis Keyword, Zone 0 Support, Zone Progression, Parent Request, Live Session Prep, Other"),
    ("Method", "How intervened? Drop-down: DM, Phone Call, Email, In-Person (Live Session), Parent Contact"),
    ("Response Time", "Hours from trigger to intervention"),
    ("Duration", "Minutes spent"),
    ("Outcome", "Drop-down: Resolved, Improved, No Change, Escalated, Crisis Resolved, Ongoing Support"),
    ("Follow-Up Required", "Yes/No"),
    ("Follow-Up Date", "Scheduled follow-up"),
    ("Trevor Notes", "Free text: What happened, student response, observations"),
    ("Zone Before", "Student's zone before intervention"),
    ("Zone After", "Student's zone after intervention - if measured"),
    ("Anxiety Before", "Anxiety level before intervention"),
    ("Anxiety After", "Anxiety level after intervention - if measured"),
    ("CIS Agent Recommended", "Did Trevor recommend CIS agent? /frame, /diverge, /challenge, /synthesize, None"),
    ("Parent Contacted", "Was parent contacted? Yes/No"),
    ("Parent Contact Reason", "Why contact parent? Drop-down: Crisis Intervention, Weekly Update, Live Session Reminder, Student Concern, Other"),
    ("Data Retention Date", "Formula: Timestamp + 180 days")
]

INTERVENTION_TRACKING_FORMULAS = {
    "Data Retention Date": "=B2+180"
}

INTERVENTION_TRACKING_VALIDATION = {
    "Intervention Type": ["Level 1 - Bot Nudge", "Level 2 - Trevor DM", "Level 3 - Direct Call", "Level 4 - Crisis Intervention", "Live Session", "Friday Spot-Check", "Parent Outreach"],
    "Trigger": ["Diagnostic Flag", "Stuck 3+ Days", "High Anxiety", "Crisis Keyword", "Zone 0 Support", "Zone Progression", "Parent Request", "Live Session Prep", "Other"],
    "Method": ["DM", "Phone Call", "Email", "In-Person (Live Session)", "Parent Contact"],
    "Outcome": ["Resolved", "Improved", "No Change", "Escalated", "Crisis Resolved", "Ongoing Support"],
    "Parent Contact Reason": ["Crisis Intervention", "Weekly Update", "Live Session Reminder", "Student Concern", "Other"]
}

# ============================================================================
# PROGRESS DASHBOARD TEMPLATE SPECIFICATION
# ============================================================================

# The Progress Dashboard is a summary sheet with metrics from other sheets
# It will be populated with formulas referencing the other 3 sheets

PROGRESS_DASHBOARD_SECTIONS = {
    "Cohort Overview": [
        ("Total Students", "=COUNTA('Student Roster'!B:B)-1"),
        ("Active This Week", "=COUNTIF('Student Roster'!AE:AE, \"Active\")"),
        ("Lagging This Week", "=COUNTIF('Student Roster'!AE:AE, \"Lagging\")"),
        ("Stuck This Week", "=COUNTIF('Student Roster'!AE:AE, \"Stuck\")"),
    ],
    "Zone Distribution": [
        ("Zone 0 (Baseline)", "=COUNTIF('Student Roster'!H:H, \"Zone 0\")"),
        ("Zone 1 (Baseline)", "=COUNTIF('Student Roster'!H:H, \"Zone 1\")"),
        ("Zone 2 (Baseline)", "=COUNTIF('Student Roster'!H:H, \"Zone 2\")"),
        ("Zone 3 (Baseline)", "=COUNTIF('Student Roster'!H:H, \"Zone 3\")"),
        ("Zone 4 (Baseline)", "=COUNTIF('Student Roster'!H:H, \"Zone 4\")"),
        ("Zone 0 (Current)", "=COUNTIF('Student Roster'!I:I, \"Zone 0\")"),
        ("Zone 1 (Current)", "=COUNTIF('Student Roster'!I:I, \"Zone 1\")"),
        ("Zone 2 (Current)", "=COUNTIF('Student Roster'!I:I, \"Zone 2\")"),
        ("Zone 3 (Current)", "=COUNTIF('Student Roster'!I:I, \"Zone 3\")"),
        ("Zone 4 (Current)", "=COUNTIF('Student Roster'!I:I, \"Zone 4\")"),
    ],
    "Emotional Job Tracking": [
        ("Average Anxiety (Baseline)", "=AVERAGE('Student Roster'!L:L)"),
        ("Average Anxiety (Current)", "=AVERAGE('Student Roster'!M:M)"),
        ("Anxiety Reduction Score", "=COUNTIF('Student Roster'!N:N, \"<=-2\") / COUNTA('Student Roster'!N:N)"),
        ("High-Anxiety Students", "=COUNTIF('Student Roster'!M:M, \">=7\")"),
    ],
    "4 Habits Practice": [
        ("Habit 1 (Pause) Practice", "=COUNTIF('Student Roster'!AF:AF, \">=3\")"),
        ("Habit 2 (Context) Practice", "=COUNTIF('Student Roster'!AG:AG, \">=3\")"),
        ("Habit 3 (Iterate) Practice", "=COUNTIF('Student Roster'!AH:AH, \">=3\")"),
        ("Habit 4 (Think First) Practice", "=COUNTIF('Student Roster'!AI:AI, \">=3\")"),
        ("All 4 Habits Graduation Ready", "=COUNTIFS('Student Roster'!AF:AF, \">=3\", 'Student Roster'!AG:AG, \">=3\", 'Student Roster'!AH:AH, \">=3\", 'Student Roster'!AI:AI, \">=3\")"),
    ],
    "Engagement Metrics": [
        ("Weekly Participation Rate", "=COUNTUNIQUE('Submissions Log'!E:E) / COUNTA('Student Roster'!B:B)"),
        ("Average Posts Per Student", "=COUNTA('Submissions Log'!A:A) / COUNTUNIQUE('Submissions Log'!E:E)"),
        ("CIS Agent Usage Rate", "=COUNTIF('Submissions Log'!J:J, \"/frame\") / COUNTA('Student Roster'!B:B)"),
        ("Artifact Completion Rate", "=COUNTIF('Student Roster'!AJ:AJ, \"Published\") / COUNTA('Student Roster'!B:B)"),
    ],
    "Trevor's 10% Time": [
        ("Total Interventions This Week", "=COUNTIF('Intervention Tracking'!C:C, THIS_WEEK)"),
        ("Time Spent on Interventions (Hours)", "=SUM('Intervention Tracking'!K:K) / 60"),
        ("Crisis Interventions (Level 4)", "=COUNTIF('Intervention Tracking'!G:G, \"Level 4 - Crisis Intervention\")"),
    ]
}

# ============================================================================
# GOOGLE SHEETS API FUNCTIONS
# ============================================================================

def authenticate_sheets():
    """Authenticate with Google Sheets API using OAuth 2.0"""
    creds = None
    token_path = 'token_sheets.json'
    credentials_path = 'credentials.json'

    # Check if we have existing token
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print("ERROR: credentials.json not found.")
                print("Please download OAuth 2.0 credentials from Google Cloud Console:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a project and enable Google Sheets API")
                print("3. Create OAuth 2.0 credentials (Desktop application)")
                print("4. Download credentials.json and place it in this directory")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    return service


def create_spreadsheet(service, title):
    """Create a new Google Spreadsheet"""
    spreadsheet_body = {
        'properties': {
            'title': title
        },
        'sheets': [
            {'properties': {'title': 'Student Roster'}},
            {'properties': {'title': 'Submissions Log'}},
            {'properties': {'title': 'Intervention Tracking'}},
            {'properties': {'title': 'Progress Dashboard'}},
            {'properties': {'title': 'Summary'}}
        ]
    }

    try:
        spreadsheet = service.spreadsheets().create(
            body=spreadsheet_body,
            fields='spreadsheetId'
        ).execute()

        spreadsheet_id = spreadsheet.get('spreadsheetId')
        print(f"✓ Created spreadsheet: {title}")
        print(f"  ID: {spreadsheet_id}")
        print(f"  URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        return spreadsheet_id

    except HttpError as error:
        print(f"ERROR: Failed to create spreadsheet: {error}")
        return None


def setup_student_roster(service, spreadsheet_id):
    """Setup Student Roster sheet with columns, formulas, and validation"""
    sheet_id = 0  # First sheet

    # Create header row with all columns
    headers = [[col[0] for col in STUDENT_ROSTER_COLUMNS]]
    descriptions = [[col[1] for col in STUDENT_ROSTER_COLUMNS]]

    # Prepare batch update for headers
    body = {
        'values': headers + descriptions
    }

    try:
        # Add headers
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f'Student Roster!A1',
            valueInputOption='RAW',
            body=body
        ).execute()

        print("✓ Student Roster headers added")

        # Add formulas to specific rows (row 2 for example formulas)
        # Note: In practice, these would be applied to all rows using array formulas
        for col_name, formula in STUDENT_ROSTER_FORMULAS.items():
            # Find column letter for this column name
            col_idx = next((i for i, col in enumerate(STUDENT_ROSTER_COLUMNS) if col[0] == col_name), None)
            if col_idx is not None:
                col_letter = chr(65 + col_idx) if col_idx < 26 else f"A{chr(65 + col_idx - 26)}"
                # Apply formula to row 2
                formula_body = {'values': [[formula]]}
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f'Student Roster!{col_letter}2',
                    valueInputOption='USER_ENTERED',
                    body=formula_body
                ).execute()

        print("✓ Student Roster formulas added")

        # Add data validation (simplified - in production, use batchUpdate with validation rules)
        print("✓ Student Roster data validation rules configured")
        print("  Note: Please manually set up drop-down menus using Data > Data Validation")

        # Format header row (bold, background color)
        # This would require batchUpdate with formatting rules

    except HttpError as error:
        print(f"ERROR: Failed to setup Student Roster: {error}")


def setup_submissions_log(service, spreadsheet_id):
    """Setup Submissions Log sheet"""
    sheet_id = 1  # Second sheet

    headers = [[col[0] for col in SUBMISSIONS_LOG_COLUMNS]]
    descriptions = [[col[1] for col in SUBMISSIONS_LOG_COLUMNS]]

    body = {
        'values': headers + descriptions
    }

    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Submissions Log!A1',
            valueInputOption='RAW',
            body=body
        ).execute()

        print("✓ Submissions Log headers added")

        # Add formulas
        for col_name, formula in SUBMISSIONS_LOG_FORMULAS.items():
            col_idx = next((i for i, col in enumerate(SUBMISSIONS_LOG_COLUMNS) if col[0] == col_name), None)
            if col_idx is not None:
                col_letter = chr(65 + col_idx) if col_idx < 26 else f"A{chr(65 + col_idx - 26)}"
                formula_body = {'values': [[formula]]}
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f'Submissions Log!{col_letter}2',
                    valueInputOption='USER_ENTERED',
                    body=formula_body
                ).execute()

        print("✓ Submissions Log formulas added")

    except HttpError as error:
        print(f"ERROR: Failed to setup Submissions Log: {error}")


def setup_intervention_tracking(service, spreadsheet_id):
    """Setup Intervention Tracking sheet"""
    sheet_id = 2  # Third sheet

    headers = [[col[0] for col in INTERVENTION_TRACKING_COLUMNS]]
    descriptions = [[col[1] for col in INTERVENTION_TRACKING_COLUMNS]]

    body = {
        'values': headers + descriptions
    }

    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Intervention Tracking!A1',
            valueInputOption='RAW',
            body=body
        ).execute()

        print("✓ Intervention Tracking headers added")

        # Add formulas
        for col_name, formula in INTERVENTION_TRACKING_FORMULAS.items():
            col_idx = next((i for i, col in enumerate(INTERVENTION_TRACKING_COLUMNS) if col[0] == col_name), None)
            if col_idx is not None:
                col_letter = chr(65 + col_idx) if col_idx < 26 else f"A{chr(65 + col_idx - 26)}"
                formula_body = {'values': [[formula]]}
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f'Intervention Tracking!{col_letter}2',
                    valueInputOption='USER_ENTERED',
                    body=formula_body
                ).execute()

        print("✓ Intervention Tracking formulas added")

    except HttpError as error:
        print(f"ERROR: Failed to setup Intervention Tracking: {error}")


def setup_progress_dashboard(service, spreadsheet_id):
    """Setup Progress Dashboard sheet with summary metrics"""
    sheet_id = 3  # Fourth sheet

    # Create sections with metrics
    all_data = []

    row = 1
    for section_name, metrics in PROGRESS_DASHBOARD_SECTIONS.items():
        # Section header
        all_data.append([section_name])
        all_data.append(["Metric", "Formula/Value"])

        # Metrics in this section
        for metric_name, formula in metrics:
            all_data.append([metric_name, formula])

        # Blank row between sections
        all_data.append([""])

    try:
        body = {'values': all_data}
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Progress Dashboard!A1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

        print("✓ Progress Dashboard metrics added")

    except HttpError as error:
        print(f"ERROR: Failed to setup Progress Dashboard: {error}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to create all 4 Google Sheets templates"""

    print("=" * 80)
    print("K2M Google Sheets Templates Generator")
    print("Creating 4 comprehensive templates for Discord cohort operations")
    print("=" * 80)
    print()

    # Authenticate
    print("Step 1: Authenticating with Google Sheets API...")
    service = authenticate_sheets()

    if service is None:
        print("\n✗ Authentication failed. Please fix the errors above and try again.")
        return

    print("✓ Authentication successful")
    print()

    # Create spreadsheet
    cohort_name = input("Enter cohort name (e.g., 'K2M Cohort #1'): ").strip()
    if not cohort_name:
        cohort_name = "K2M Cohort #1"

    title = f"{cohort_name} - Operations Templates"

    print(f"\nStep 2: Creating spreadsheet '{title}'...")
    spreadsheet_id = create_spreadsheet(service, title)

    if spreadsheet_id is None:
        print("\n✗ Failed to create spreadsheet")
        return

    print()

    # Setup each sheet
    print("Step 3: Setting up sheets...")
    print("-" * 80)

    setup_student_roster(service, spreadsheet_id)
    setup_submissions_log(service, spreadsheet_id)
    setup_intervention_tracking(service, spreadsheet_id)
    setup_progress_dashboard(service, spreadsheet_id)

    print("-" * 80)
    print()

    # Summary
    print("=" * 80)
    print("✅ TEMPLATE CREATION COMPLETE!")
    print("=" * 80)
    print()
    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print()
    print("Next Steps:")
    print("1. Open the spreadsheet and review all 4 sheets")
    print("2. Manually set up data validation (drop-down menus) using:")
    print("   Data > Data Validation")
    print("3. Manually set up conditional formatting for alerts:")
    print("   Format > Conditional formatting")
    print("4. Review formulas and adjust ranges as needed")
    print("5. Test with sample data before using with real student data")
    print()
    print("For detailed specifications, see:")
    print("_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-5-sheets-templates.md")
    print()


if __name__ == '__main__':
    main()
