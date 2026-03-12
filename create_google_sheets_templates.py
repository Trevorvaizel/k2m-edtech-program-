#!/usr/bin/env python3
"""
K2M Google Sheets Templates Generator
Creates 5 comprehensive Google Sheets templates for Discord cohort operations
Per Story 5.5 specification

Requirements:
- pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
- Google Cloud project with Sheets API enabled
- OAuth 2.0 credentials (credentials.json)

L2 FIX: INTERACTIVE REQUIREMENTS:
- First run: opens a browser window for Google OAuth authentication
- Prompts for cohort name via stdin
- Must be run in an interactive terminal (not piped non-interactively)
- Re-runs use saved token_sheets.json (no browser needed)
"""

import os
import json
import re

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

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# M2 FIX: Cover 200 students + 1 header row
MAX_DATA_ROWS = 201

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
    ("Habit 1 Practice", "Pause - Count of reflections showing Pause"),
    ("Habit 2 Practice", "Context - Count of reflections showing Context"),
    ("Habit 3 Practice", "Iterate - Count of reflections showing Iterate"),
    ("Habit 4 Practice", "Think First - Count of reflections showing Think First"),
    ("Artifact Status", "Not started, In progress, Submitted, Published"),
    ("Graduation Proof", "Which 4 Habits demonstrated? Manual: Trevor assessment"),
    ("Data Retention Date", "Formula: Timestamp + 180 days"),
    ("Notes", "Ongoing cohort notes - milestones, celebrations, concerns"),
]

STUDENT_ROSTER_FORMULAS = {
    # M1 FIX: Added "Stuck at Zone 0" case per spec
    "Zone Shift": (
        '=IF(AND(H2="Zone 0",I2="Zone 0"),"Not started (Zone 0)",'
        'IF(I2="Zone 1","Zone 0\u21921",'
        'IF(I2="Zone 2","Zone 1\u21922",'
        'IF(I2="Zone 3","Zone 2\u21923",'
        'IF(I2="Zone 4","Zone 3\u21924",'
        'IF(AND(H2="Zone 0",I2="Zone 0"),"Stuck at Zone 0","Stuck"))))))'
    ),
    "Anxiety Change": "=M2-L2",
    "Cluster Assignment": (
        '=IF(UPPER(LEFT(D2,1))<="F","Cluster 1 (A-F)",'
        'IF(UPPER(LEFT(D2,1))<="L","Cluster 2 (G-L)",'
        'IF(UPPER(LEFT(D2,1))<="R","Cluster 3 (M-R)","Cluster 4 (S-Z)")))'
    ),
    # H1 FIX: All 10 crisis keywords from spec
    # L1 FIX: Removed redundant OR() wrapper on single condition
    "Crisis Flag": (
        '=IF(L2>=7,"HIGH ANXIETY",'
        'IF(OR('
        'ISNUMBER(SEARCH("hopeless",P2)),ISNUMBER(SEARCH("hopeless",Q2)),'
        'ISNUMBER(SEARCH("suicide",P2)),ISNUMBER(SEARCH("suicide",Q2)),'
        'ISNUMBER(SEARCH("self-harm",P2)),ISNUMBER(SEARCH("self-harm",Q2)),'
        'ISNUMBER(SEARCH("depressed",P2)),'
        'ISNUMBER(SEARCH("end it all",P2)),'
        'ISNUMBER(SEARCH("kill myself",P2)),'
        'ISNUMBER(SEARCH("no point",P2)),'
        'ISNUMBER(SEARCH("giving up",P2)),'
        'ISNUMBER(SEARCH("want to die",P2)),'
        'ISNUMBER(SEARCH("can\'t go on",P2))'
        '),"CRISIS",'
        'IF(AND(N2>=3,L2>=7),"EMOTIONAL ESCALATION","OK")))'
    ),
    "Intervention Priority": (
        '=IF(AND(H2="Zone 0",L2>=7),"LEVEL 3: IMMEDIATE outreach",'
        'IF(AND(H2="Zone 0",L2>=5),"LEVEL 2: Monitor + DM",'
        'IF(L2>=8,"LEVEL 3: Check in","LEVEL 1: Normal monitoring")))'
    ),
    "Data Retention Date": "=A2+180",
}

STUDENT_ROSTER_VALIDATION = {
    "Zone Baseline": ["Zone 0", "Zone 1", "Zone 2", "Zone 3", "Zone 4"],
    "Zone Current": ["Zone 0", "Zone 1", "Zone 2", "Zone 3", "Zone 4"],
    "Weekly Updates Consent": ["Yes", "No", "Not sure yet"],
    "Outreach Status": ["Not contacted", "Nudged", "DM sent", "Call scheduled", "Crisis contacted"],
    "Artifact Status": ["Not started", "In progress", "Submitted", "Published"],
    "Engagement Status": ["Active", "Lagging", "Stuck"],
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
    ("Habit Mentioned", "Which habit? Pause, Context, Iterate, Think First, None"),
    ("Emotional Tone", "Positive, Neutral, Negative, Mixed, Crisis Flag"),
    ("Engagement Depth", "Formula: CIS agent usage + reflection quality score"),
    ("Trevor Review", "Did Trevor review this? Yes/No"),
    ("Trevor Feedback", "Manual: Trevor's response or nudge"),
    ("Escalation Flag", "Does student need outreach? Yes/No"),
    ("Engagement Pattern", "Formula: Consistent/Intermittent/Disengaged (INTERNAL - Guardrail #3, never shared)"),
    ("Week Total", "Formula: Total posts this week"),
    ("Notes", "Ongoing observations"),
]

SUBMISSIONS_LOG_FORMULAS = {
    "Engagement Depth": (
        '=IF(J2="None",1,IF(OR(J2="/frame",J2="/diverge",J2="/challenge"),2,3))'
        '+IF(L2="Growth Edge",3,IF(OR(L2="Synthesizing",L2="Self-Aware"),2,IF(L2="Experimenting",1,0)))'
    ),
    "Engagement Pattern": '=IF(U2>=5,"Consistent",IF(U2>=2,"Intermittent","Disengaged"))',
    "Week Total": "=COUNTIFS(E:E,E2,C:C,C2)",
}

SUBMISSIONS_LOG_VALIDATION = {
    "Post Type": ["Daily Prompt", "Friday Reflection", "Self-Assessment", "CIS Interaction", "Artifact Submission", "Other"],
    "CIS Agent Used": ["None", "/frame", "/diverge", "/challenge", "/synthesize", "/create-artifact"],
    "Thinking Depth Indicator": ["Self-Aware", "Experimenting", "Synthesizing", "Needs Scaffolding", "Growth Edge"],
    "Emotional Tone": ["Positive", "Neutral", "Negative", "Mixed", "Crisis Flag"],
    "Escalation Flag": ["Yes", "No"],
    "Trevor Review": ["Yes", "No"],
    "Zone Mentioned": ["Yes", "No"],
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
    ("Data Retention Date", "Formula: Timestamp + 180 days"),
]

INTERVENTION_TRACKING_FORMULAS = {
    "Data Retention Date": "=B2+180",
}

INTERVENTION_TRACKING_VALIDATION = {
    "Intervention Type": ["Level 1 - Bot Nudge", "Level 2 - Trevor DM", "Level 3 - Direct Call", "Level 4 - Crisis Intervention", "Live Session", "Friday Spot-Check", "Parent Outreach"],
    "Trigger": ["Diagnostic Flag", "Stuck 3+ Days", "High Anxiety", "Crisis Keyword", "Zone 0 Support", "Zone Progression", "Parent Request", "Live Session Prep", "Other"],
    "Method": ["DM", "Phone Call", "Email", "In-Person (Live Session)", "Parent Contact"],
    "Outcome": ["Resolved", "Improved", "No Change", "Escalated", "Crisis Resolved", "Ongoing Support"],
    "Parent Contact Reason": ["Crisis Intervention", "Weekly Update", "Live Session Reminder", "Student Concern", "Other"],
    "Follow-Up Required": ["Yes", "No"],
    "Parent Contacted": ["Yes", "No"],
}

# ============================================================================
# PROGRESS DASHBOARD TEMPLATE SPECIFICATION
# H5 FIX: THIS_WEEK replaced with reference to control cell $B$1 (current week)
# H6 FIX: Added Artifact & Graduation Metrics section (metrics 23-26 from spec)
# M4 FIX: Added Live Session Time, Spot-Check Time, Total 10% Time (metrics 29-31)
# ============================================================================

PROGRESS_DASHBOARD_SECTIONS = {
    "_control": [],  # populated manually in setup_progress_dashboard
    "Cohort Overview": [
        ("Total Students", "=COUNTA('Student Roster'!B:B)-1"),
        ("Active This Week", "=COUNTIF('Student Roster'!AE:AE,\"Active\")"),
        ("Lagging This Week", "=COUNTIF('Student Roster'!AE:AE,\"Lagging\")"),
        ("Stuck This Week", "=COUNTIF('Student Roster'!AE:AE,\"Stuck\")"),
    ],
    "Zone Distribution": [
        ("Zone 0 (Baseline)", "=COUNTIF('Student Roster'!H:H,\"Zone 0\")"),
        ("Zone 1 (Baseline)", "=COUNTIF('Student Roster'!H:H,\"Zone 1\")"),
        ("Zone 2 (Baseline)", "=COUNTIF('Student Roster'!H:H,\"Zone 2\")"),
        ("Zone 3 (Baseline)", "=COUNTIF('Student Roster'!H:H,\"Zone 3\")"),
        ("Zone 4 (Baseline)", "=COUNTIF('Student Roster'!H:H,\"Zone 4\")"),
        ("Zone 0 (Current)", "=COUNTIF('Student Roster'!I:I,\"Zone 0\")"),
        ("Zone 1 (Current)", "=COUNTIF('Student Roster'!I:I,\"Zone 1\")"),
        ("Zone 2 (Current)", "=COUNTIF('Student Roster'!I:I,\"Zone 2\")"),
        ("Zone 3 (Current)", "=COUNTIF('Student Roster'!I:I,\"Zone 3\")"),
        ("Zone 4 (Current)", "=COUNTIF('Student Roster'!I:I,\"Zone 4\")"),
        (
            "Zone Shift Success Rate",
            "=IFERROR("
            "(COUNTIF('Student Roster'!J:J,\"Zone 0\u21921\")/COUNTIF('Student Roster'!H:H,\"Zone 0\"))"
            "+(COUNTIF('Student Roster'!J:J,\"Zone 1\u21922\")/COUNTIF('Student Roster'!H:H,\"Zone 1\"))"
            "+(COUNTIF('Student Roster'!J:J,\"Zone 2\u21923\")/COUNTIF('Student Roster'!H:H,\"Zone 2\"))"
            "+(COUNTIF('Student Roster'!J:J,\"Zone 3\u21924\")/COUNTIF('Student Roster'!H:H,\"Zone 3\"))"
            ",0)",
        ),
    ],
    "Emotional Job Tracking": [
        ("Average Anxiety (Baseline)", "=AVERAGE('Student Roster'!L:L)"),
        ("Average Anxiety (Current)", "=AVERAGE('Student Roster'!M:M)"),
        ("Anxiety Reduction Score (% reduced by 2+)", "=IFERROR(COUNTIF('Student Roster'!N:N,\"<=-2\")/COUNTA('Student Roster'!N:N),0)"),
        ("Anxiety Increase Alert (% increased by 2+)", "=IFERROR(COUNTIF('Student Roster'!N:N,\">=2\")/COUNTA('Student Roster'!N:N),0)"),
        ("High-Anxiety Students (Anxiety >=7)", "=COUNTIF('Student Roster'!M:M,\">=7\")"),
        ("Belonging: Not at all confident", "=COUNTIF('Student Roster'!O:O,\"Not at all\")"),
        ("Belonging: Somewhat confident", "=COUNTIF('Student Roster'!O:O,\"Somewhat\")"),
        ("Belonging: Fairly confident", "=COUNTIF('Student Roster'!O:O,\"Fairly\")"),
        ("Belonging: Very confident", "=COUNTIF('Student Roster'!O:O,\"Very\")"),
    ],
    "4 Habits Practice": [
        ("Habit 1 (Pause) Practice Rate", "=IFERROR(COUNTIF('Student Roster'!AF:AF,\">=3\")/(COUNTA('Student Roster'!B:B)-1),0)"),
        ("Habit 2 (Context) Practice Rate", "=IFERROR(COUNTIF('Student Roster'!AG:AG,\">=3\")/(COUNTA('Student Roster'!B:B)-1),0)"),
        ("Habit 3 (Iterate) Practice Rate", "=IFERROR(COUNTIF('Student Roster'!AH:AH,\">=3\")/(COUNTA('Student Roster'!B:B)-1),0)"),
        ("Habit 4 (Think First) Practice Rate", "=IFERROR(COUNTIF('Student Roster'!AI:AI,\">=3\")/(COUNTA('Student Roster'!B:B)-1),0)"),
        ("All 4 Habits Graduation Ready", "=IFERROR(COUNTIFS('Student Roster'!AF:AF,\">=3\",'Student Roster'!AG:AG,\">=3\",'Student Roster'!AH:AH,\">=3\",'Student Roster'!AI:AI,\">=3\")/(COUNTA('Student Roster'!B:B)-1),0)"),
    ],
    "Engagement Metrics": [
        ("Weekly Participation Rate", "=IFERROR(COUNTUNIQUE('Submissions Log'!E:E)/(COUNTA('Student Roster'!B:B)-1),0)"),
        ("Average Posts Per Student", "=IFERROR(COUNTA('Submissions Log'!A:A)/COUNTUNIQUE('Submissions Log'!E:E),0)"),
        ("CIS Agent Usage Rate (/frame)", "=IFERROR(COUNTIF('Submissions Log'!J:J,\"/frame\")/(COUNTA('Student Roster'!B:B)-1),0)"),
        ("Artifact Completion Rate", "=IFERROR(COUNTIF('Student Roster'!AJ:AJ,\"Published\")/(COUNTA('Student Roster'!B:B)-1),0)"),
    ],
    # H6 FIX: Artifact & Graduation Metrics section (metrics 23-26 from spec)
    "Artifact & Graduation Metrics": [
        ("Artifact Published", "=COUNTIF('Student Roster'!AJ:AJ,\"Published\")"),
        ("Artifact In Progress", "=COUNTIF('Student Roster'!AJ:AJ,\"In progress\")"),
        ("Artifact Not Started", "=COUNTIF('Student Roster'!AJ:AJ,\"Not started\")"),
        ("Graduation Proof Ready (All 4 Habits + Published)", "=IFERROR(COUNTIFS('Student Roster'!AF:AF,\">=3\",'Student Roster'!AG:AG,\">=3\",'Student Roster'!AH:AH,\">=3\",'Student Roster'!AI:AI,\">=3\",'Student Roster'!AJ:AJ,\"Published\")/(COUNTA('Student Roster'!B:B)-1),0)"),
        ("Parents Consented to Weekly Updates", "=COUNTIF('Student Roster'!W:W,\"Yes\")"),
    ],
    "Trevor's 10% Time": [
        # H5 FIX: References $B$1 (control cell where Trevor sets current week)
        ("Total Interventions This Week", "=COUNTIF('Intervention Tracking'!C:C,\"Week \"&'Progress Dashboard'!$B$1)"),
        ("Time Spent on Interventions (Hours)", "=IFERROR(SUMIF('Intervention Tracking'!C:C,\"Week \"&'Progress Dashboard'!$B$1,'Intervention Tracking'!K:K)/60,0)"),
        ("Crisis Interventions (Level 4)", "=COUNTIF('Intervention Tracking'!G:G,\"Level 4 - Crisis Intervention\")"),
        # M4 FIX: Added metrics 29-31
        ("Live Session Time This Week (Hours)", "=IFERROR(COUNTIFS('Intervention Tracking'!G:G,\"Live Session\",'Intervention Tracking'!C:C,\"Week \"&'Progress Dashboard'!$B$1)*1.5,0)"),
        ("Friday Spot-Check Time (Hours)", "=IFERROR(COUNTIFS('Intervention Tracking'!G:G,\"Friday Spot-Check\",'Intervention Tracking'!C:C,\"Week \"&'Progress Dashboard'!$B$1)*0.75,0)"),
        ("Total 10% Time This Week (Hours)", "__TOTAL_10PCT_PLACEHOLDER__"),
    ],
}

# ============================================================================
# SUMMARY SHEET (H4 FIX: Cross-Sheet Integration + Privacy + Crisis resources)
# ============================================================================

SUMMARY_DATA = [
    ["K2M COHORT OPERATIONS - SUMMARY DASHBOARD"],
    ["Last Updated", "=NOW()"],
    [""],
    ["DATA FLOW", "Source", "Destination", "Method"],
    ["Student diagnostics", "Google Forms", "Student Roster", "Auto-sync: Forms > Responses > Link to Sheets"],
    ["Engagement status", "Submissions Log", "Student Roster col AE", "=IFERROR(VLOOKUP(B2,'Submissions Log'!E:T,15,FALSE),\"No data\")"],
    ["Participation metrics", "Submissions Log", "Progress Dashboard", "COUNTUNIQUE, COUNTIFS formulas"],
    ["Intervention metrics", "Intervention Tracking", "Progress Dashboard", "COUNTIF, SUMIF formulas"],
    ["Zone/habit progress", "Student Roster", "Progress Dashboard", "COUNTIF per zone/habit column"],
    [""],
    ["AUTOMATED ALERTS (Conditional Formatting - Student Roster)"],
    ["Color", "Condition", "Column", "Required Action"],
    ["RED", "Crisis Flag = CRISIS", "Col Y", "IMMEDIATE Level 4 outreach (<=1 hour)"],
    ["ORANGE", "Anxiety Current >=7", "Col M", "Level 3 outreach within 24h"],
    ["YELLOW", "Engagement Status = Stuck", "Col AE", "Level 2 DM within 24h"],
    ["GREEN", "Zone Shift contains arrow", "Col J", "Celebrate in #thinking-showcase (with consent)"],
    [""],
    ["DATA VALIDATION RULES"],
    ["Rule", "Condition", "Error Message"],
    ["Student ID Uniqueness", "=COUNTIF('Student Roster'!B:B,B2)=1", "Duplicate Student ID detected"],
    ["Student ID Reference Validity", "=NOT(ISNA(VLOOKUP(E2,'Student Roster'!B:B,1,FALSE)))", "Student ID not found in Student Roster"],
    ["Zone Placement Validity", "=OR(H2=\"Zone 0\",H2=\"Zone 1\",H2=\"Zone 2\",H2=\"Zone 3\",H2=\"Zone 4\")", "Invalid zone placement"],
    ["Anxiety Score Validity", "=AND(L2>=1,L2<=10)", "Anxiety must be 1-10"],
    ["Cluster Validity", "=OR(X2=\"Cluster 1 (A-F)\",X2=\"Cluster 2 (G-L)\",X2=\"Cluster 3 (M-R)\",X2=\"Cluster 4 (S-Z)\")", "Invalid cluster assignment"],
    [""],
    ["PRIVACY & SECURITY (AC#8 - Guardrails #6, #8)"],
    ["Access Control", "Trevor ONLY - do NOT share this spreadsheet with students or parents"],
    ["Data Retention", "Delete ALL data 180 days after cohort end date (check col AL)"],
    ["Crisis Data", "Cols Y-Z (Crisis Flag, Intervention Priority) are CONFIDENTIAL"],
    ["Parent Contact", "Col U (Parent Email) used ONLY for crisis + consented weekly updates"],
    ["Anonymization", "Use Student ID (not name) in any external reporting or aggregates"],
    [""],
    ["CRISIS KEYWORDS MONITORED - ALL trigger Level 4 protocol (from Story 5.5 spec)"],
    ["hopeless", "suicide", "self-harm", "depressed", "end it all", "kill myself"],
    ["no point", "giving up", "want to die", "can't go on", "", ""],
    [""],
    ["KENYA CRISIS RESOURCES (Level 4 response protocol)"],
    ["Befriending Kenya", "+254 722 178 177", "", ""],
    ["Mental Health Kenya", "+254 733 111 000", "", ""],
    ["Youth Crisis Hotline", "+254 1199", "", ""],
    ["Emergency", "999 or 112", "", ""],
    [""],
    ["WEEKLY MAINTENANCE"],
    ["Every Monday", "Update Progress Dashboard cell B1 with current cohort week number"],
    ["Every Friday", "Run spot-check on 15-20 reflections per SOP 5 in Story 5.5 spec"],
    ["Daily (5 min)", "Scan Submissions Log for Crisis Flag entries (Emotional Tone = Crisis Flag)"],
]


# ============================================================================
# GOOGLE SHEETS API HELPER FUNCTIONS
# ============================================================================

def col_letter(col_idx):
    """Convert 0-based column index to column letter(s). Handles A-AZ (52 cols)."""
    if col_idx < 26:
        return chr(65 + col_idx)
    return f"A{chr(65 + col_idx - 26)}"


def authenticate_sheets():
    """Authenticate with Google Sheets API using OAuth 2.0."""
    creds = None
    token_path = 'token_sheets.json'
    credentials_path = 'credentials.json'

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_info(
            json.load(open(token_path)), SCOPES
        )

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

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('sheets', 'v4', credentials=creds)


def get_sheet_ids(service, spreadsheet_id):
    """Return dict of {sheet_title: sheetId} for all sheets in the spreadsheet."""
    response = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return {s['properties']['title']: s['properties']['sheetId']
            for s in response['sheets']}


def create_spreadsheet(service, title):
    """Create a new Google Spreadsheet with 5 tabs."""
    body = {
        'properties': {'title': title},
        'sheets': [
            {'properties': {'title': 'Student Roster'}},
            {'properties': {'title': 'Submissions Log'}},
            {'properties': {'title': 'Intervention Tracking'}},
            {'properties': {'title': 'Progress Dashboard'}},
            {'properties': {'title': 'Summary'}},
        ],
    }
    try:
        result = service.spreadsheets().create(body=body, fields='spreadsheetId').execute()
        sid = result.get('spreadsheetId')
        print(f"Created spreadsheet: {title}")
        print(f"  ID: {sid}")
        print(f"  URL: https://docs.google.com/spreadsheets/d/{sid}")
        print("  Privacy: accessible by your Google account only (AC#8 Trevor-only)")
        return sid
    except HttpError as e:
        print(f"ERROR: Failed to create spreadsheet: {e}")
        return None


# H2 FIX: Actual data validation applied via batchUpdate API
def apply_data_validation(service, spreadsheet_id, sheet_id, columns_def, validation_map):
    """Apply dropdown data validation to columns via Sheets batchUpdate API."""
    requests = []
    for col_name, options in validation_map.items():
        col_idx = next((i for i, col in enumerate(columns_def) if col[0] == col_name), None)
        if col_idx is None:
            continue
        requests.append({
            "setDataValidation": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "endRowIndex": MAX_DATA_ROWS,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": v} for v in options],
                    },
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        })
    if requests:
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
        ).execute()


# H3 FIX: Conditional formatting applied via batchUpdate API
def apply_conditional_formatting(service, spreadsheet_id, sheet_id):
    """Apply RED/ORANGE/YELLOW/GREEN row-level conditional formatting to Student Roster."""

    def rgb(r, g, b):
        return {"red": r / 255, "green": g / 255, "blue": b / 255}

    num_cols = len(STUDENT_ROSTER_COLUMNS)

    def row_range():
        return {
            "sheetId": sheet_id,
            "startRowIndex": 1,
            "endRowIndex": MAX_DATA_ROWS,
            "startColumnIndex": 0,
            "endColumnIndex": num_cols,
        }

    rules = [
        # RED: Crisis Flag = "CRISIS" (col Y = index 24)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [row_range()],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": '=$Y2="CRISIS"'}],
                        },
                        "format": {"backgroundColor": rgb(255, 102, 102)},
                    },
                },
                "index": 0,
            }
        },
        # ORANGE: Anxiety Current >= 7 (col M = index 12)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [row_range()],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": "=$M2>=7"}],
                        },
                        "format": {"backgroundColor": rgb(255, 165, 0)},
                    },
                },
                "index": 1,
            }
        },
        # YELLOW: Engagement Status = "Stuck" (col AE = index 30)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [row_range()],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": '=$AE2="Stuck"'}],
                        },
                        "format": {"backgroundColor": rgb(255, 255, 153)},
                    },
                },
                "index": 2,
            }
        },
        # GREEN: Zone Shift contains arrow (col J = index 9)
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [row_range()],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{"userEnteredValue": '=ISNUMBER(SEARCH("\u2192",$J2))'}],
                        },
                        "format": {"backgroundColor": rgb(144, 238, 144)},
                    },
                },
                "index": 3,
            }
        },
    ]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": rules},
    ).execute()


# M2 FIX: Formulas written to rows 2-200, not just row 2
def write_formulas_to_range(service, spreadsheet_id, sheet_name, columns_def, formulas_dict):
    """
    Write each formula to rows 2 through MAX_DATA_ROWS.
    Uses regex to adjust row numbers in cell references (e.g. H2 -> H5)
    while leaving string literals like "Zone 2" untouched.
    """
    for col_name, formula_row2 in formulas_dict.items():
        col_idx = next((i for i, col in enumerate(columns_def) if col[0] == col_name), None)
        if col_idx is None:
            continue
        letter = col_letter(col_idx)
        values = []
        for row in range(2, MAX_DATA_ROWS + 1):
            if row == 2:
                adjusted = formula_row2
            else:
                # Only replace uppercase column letter refs (e.g. H2, L2) not string content
                adjusted = re.sub(
                    r'([A-Z]+)2\b',
                    lambda m, r=row: f"{m.group(1)}{r}",
                    formula_row2,
                )
            values.append([adjusted])
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!{letter}2",
            valueInputOption='USER_ENTERED',
            body={'values': values},
        ).execute()


# ============================================================================
# SHEET SETUP FUNCTIONS
# ============================================================================

def setup_student_roster(service, spreadsheet_id, sheet_id):
    """Setup Student Roster: headers, formulas (rows 2-200), validation, formatting."""
    headers = [[col[0] for col in STUDENT_ROSTER_COLUMNS]]
    descriptions = [[col[1] for col in STUDENT_ROSTER_COLUMNS]]
    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Student Roster!A1',
            valueInputOption='RAW',
            body={'values': headers + descriptions},
        ).execute()
        print("  Student Roster: headers added")

        write_formulas_to_range(
            service, spreadsheet_id, 'Student Roster',
            STUDENT_ROSTER_COLUMNS, STUDENT_ROSTER_FORMULAS,
        )
        print("  Student Roster: formulas applied to rows 2-200")

        apply_data_validation(
            service, spreadsheet_id, sheet_id,
            STUDENT_ROSTER_COLUMNS, STUDENT_ROSTER_VALIDATION,
        )
        print("  Student Roster: data validation applied via API (H2 fix)")

        apply_conditional_formatting(service, spreadsheet_id, sheet_id)
        print("  Student Roster: RED/ORANGE/YELLOW/GREEN formatting applied via API (H3 fix)")

    except HttpError as e:
        print(f"  ERROR in Student Roster: {e}")


def setup_submissions_log(service, spreadsheet_id, sheet_id):
    """Setup Submissions Log: headers, formulas (rows 2-200), validation."""
    headers = [[col[0] for col in SUBMISSIONS_LOG_COLUMNS]]
    descriptions = [[col[1] for col in SUBMISSIONS_LOG_COLUMNS]]
    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Submissions Log!A1',
            valueInputOption='RAW',
            body={'values': headers + descriptions},
        ).execute()
        print("  Submissions Log: headers added")

        write_formulas_to_range(
            service, spreadsheet_id, 'Submissions Log',
            SUBMISSIONS_LOG_COLUMNS, SUBMISSIONS_LOG_FORMULAS,
        )
        print("  Submissions Log: formulas applied to rows 2-200")

        apply_data_validation(
            service, spreadsheet_id, sheet_id,
            SUBMISSIONS_LOG_COLUMNS, SUBMISSIONS_LOG_VALIDATION,
        )
        print("  Submissions Log: data validation applied via API")

    except HttpError as e:
        print(f"  ERROR in Submissions Log: {e}")


def setup_intervention_tracking(service, spreadsheet_id, sheet_id):
    """Setup Intervention Tracking: headers, formulas (rows 2-200), validation."""
    headers = [[col[0] for col in INTERVENTION_TRACKING_COLUMNS]]
    descriptions = [[col[1] for col in INTERVENTION_TRACKING_COLUMNS]]
    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Intervention Tracking!A1',
            valueInputOption='RAW',
            body={'values': headers + descriptions},
        ).execute()
        print("  Intervention Tracking: headers added")

        write_formulas_to_range(
            service, spreadsheet_id, 'Intervention Tracking',
            INTERVENTION_TRACKING_COLUMNS, INTERVENTION_TRACKING_FORMULAS,
        )
        print("  Intervention Tracking: formulas applied to rows 2-200")

        apply_data_validation(
            service, spreadsheet_id, sheet_id,
            INTERVENTION_TRACKING_COLUMNS, INTERVENTION_TRACKING_VALIDATION,
        )
        print("  Intervention Tracking: data validation applied via API")

    except HttpError as e:
        print(f"  ERROR in Intervention Tracking: {e}")


def setup_progress_dashboard(service, spreadsheet_id):
    """Setup Progress Dashboard: control cell, all 7 sections, fixed Total 10% Time formula."""
    all_data = []
    current_row = 1

    # H5 FIX: Control cell - Trevor sets current week here each Monday
    # Formulas in Trevor's 10% Time section reference $B$1
    all_data.append(["CURRENT COHORT WEEK (update each Monday)", 1])
    current_row += 1
    all_data.append([""])
    current_row += 1

    # Track rows needed to compute Total 10% Time formula
    intervention_hours_row = None
    live_session_row = None
    spot_check_row = None

    for section_name, metrics in PROGRESS_DASHBOARD_SECTIONS.items():
        if section_name == "_control":
            continue

        all_data.append([section_name])
        current_row += 1
        all_data.append(["Metric", "Value"])
        current_row += 1

        for metric_name, formula in metrics:
            if metric_name == "Time Spent on Interventions (Hours)":
                intervention_hours_row = current_row
            elif metric_name == "Live Session Time This Week (Hours)":
                live_session_row = current_row
            elif metric_name == "Friday Spot-Check Time (Hours)":
                spot_check_row = current_row

            all_data.append([metric_name, formula])
            current_row += 1

        all_data.append([""])
        current_row += 1

    # Resolve Total 10% Time formula placeholder with actual computed row references
    if all(x is not None for x in [intervention_hours_row, live_session_row, spot_check_row]):
        total_formula = f"=B{intervention_hours_row}+B{live_session_row}+B{spot_check_row}+0.5"
        for i, row in enumerate(all_data):
            if len(row) > 1 and "__TOTAL_10PCT_PLACEHOLDER__" in str(row[1]):
                all_data[i][1] = total_formula
                break

    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Progress Dashboard!A1',
            valueInputOption='USER_ENTERED',
            body={'values': all_data},
        ).execute()
        print("  Progress Dashboard: 7 sections added (Artifact & Graduation, Trevor 10% complete)")
        print(f"  Progress Dashboard: Total 10% Time formula = =B{intervention_hours_row}+B{live_session_row}+B{spot_check_row}+0.5")
    except HttpError as e:
        print(f"  ERROR in Progress Dashboard: {e}")


# H4 FIX: Summary sheet now fully populated
def setup_summary_sheet(service, spreadsheet_id):
    """Setup Summary: cross-sheet integration, alert docs, privacy, crisis resources."""
    try:
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Summary!A1',
            valueInputOption='USER_ENTERED',
            body={'values': SUMMARY_DATA},
        ).execute()
        print("  Summary: cross-sheet integration + privacy + crisis keywords + Kenya resources added")
    except HttpError as e:
        print(f"  ERROR in Summary: {e}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Create all 5 Google Sheets templates for K2M cohort operations.

    INTERACTIVE: requires terminal input for cohort name + browser OAuth on first run.
    """
    print("=" * 80)
    print("K2M Google Sheets Templates Generator (v2 - all review fixes applied)")
    print("=" * 80)
    print()

    print("Step 1: Authenticating...")
    service = authenticate_sheets()
    if service is None:
        print("Authentication failed.")
        return
    print("Authentication successful")
    print()

    cohort_name = input("Enter cohort name (e.g., 'K2M Cohort #1'): ").strip()
    if not cohort_name:
        cohort_name = "K2M Cohort #1"
    title = f"{cohort_name} - Operations Templates"

    print(f"\nStep 2: Creating spreadsheet '{title}'...")
    spreadsheet_id = create_spreadsheet(service, title)
    if spreadsheet_id is None:
        return
    print()

    print("Step 3: Getting sheet IDs...")
    sheet_ids = get_sheet_ids(service, spreadsheet_id)
    print()

    print("Step 4: Setting up sheets...")
    print("-" * 80)
    setup_student_roster(service, spreadsheet_id, sheet_ids['Student Roster'])
    setup_submissions_log(service, spreadsheet_id, sheet_ids['Submissions Log'])
    setup_intervention_tracking(service, spreadsheet_id, sheet_ids['Intervention Tracking'])
    setup_progress_dashboard(service, spreadsheet_id)
    setup_summary_sheet(service, spreadsheet_id)
    print("-" * 80)
    print()

    print("=" * 80)
    print("COMPLETE!")
    print("=" * 80)
    print()
    print(f"Spreadsheet URL:")
    print(f"  https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print()
    print("What was created:")
    print("  - Student Roster: 38 cols, formulas rows 2-200, dropdowns, RED/ORANGE/YELLOW/GREEN alerts")
    print("  - Submissions Log: 22 cols, formulas rows 2-200, dropdowns")
    print("  - Intervention Tracking: 23 cols, formulas rows 2-200, dropdowns")
    print("  - Progress Dashboard: 7 sections, 32+ metrics, current-week control cell (B1)")
    print("  - Summary: cross-sheet integration, privacy docs, crisis keywords, Kenya resources")
    print()
    print("Weekly maintenance:")
    print("  - Every Monday: update Progress Dashboard cell B1 with current cohort week number")
    print()
    print("Privacy reminder:")
    print("  - Keep Trevor-only (do NOT share)")
    print("  - Delete all data 180 days after cohort ends")
    print()
    print("For full SOPs:")
    print("  _bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-5-sheets-templates.md")
    print()


if __name__ == '__main__':
    main()
