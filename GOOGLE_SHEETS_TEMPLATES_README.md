# K2M Google Sheets Templates - Task 0.6

## Overview

This package creates 4 comprehensive Google Sheets templates for Discord cohort operations per Story 5.5 specification.

**Templates Created:**
1. **Student Roster** - Master database (30+ columns)
2. **Submissions Log** - Engagement tracking
3. **Intervention Tracking** - Trevor's 10% interventions
4. **Progress Dashboard** - 32+ metrics summary

**Source Specification:** `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-5-sheets-templates.md`

---

## Option 1: Automated Creation (Python Script)

### Prerequisites

1. **Install Python packages:**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

2. **Set up Google Cloud project:**
   - Go to https://console.cloud.google.com/
   - Create a new project (or use existing)
   - Enable Google Sheets API:
     - Navigate to "APIs & Services" > "Library"
     - Search for "Google Sheets API"
     - Click "Enable"

3. **Create OAuth 2.0 credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop application"
   - Name: "K2M Sheets Generator"
   - Click "Create"
   - Download the JSON file and rename it to `credentials.json`
   - Place `credentials.json` in this directory

### Usage

**Run the script:**
```bash
python create_google_sheets_templates.py
```

**First run only:**
1. Browser will open asking for Google account permission
2. Grant permission to access your Google Sheets
3. Token will be saved as `token_sheets.json` for future runs

**Enter cohort name when prompted:**
```
Enter cohort name (e.g., 'K2M Cohort #1'): K2M Cohort #1
```

**Output:**
- Script creates a new Google Spreadsheet with 5 sheets:
  - Student Roster
  - Submissions Log
  - Intervention Tracking
  - Progress Dashboard
  - Summary

- Spreadsheet URL is printed at completion

### What Gets Created

**Student Roster (30+ columns):**
- Diagnostic data import from Google Forms
- Zone tracking (baseline → current)
- Anxiety tracking with change calculation
- Cluster assignment formulas
- Crisis flag detection (HIGH ANXIETY, CRISIS keywords)
- Intervention priority levels (1-3)
- Habit practice tracking (all 4 habits)
- Artifact status tracking
- Graduation proof readiness
- Data retention (180-day auto-delete)

**Submissions Log (22 columns):**
- Daily post tracking
- Friday reflection logging
- CIS agent usage (/frame, /diverge, /challenge, /synthesize)
- Engagement depth scoring
- Thinking quality assessment
- Emotional tone classification
- Escalation flagging
- Streak tracking (consistent/intermittent/disengaged)

**Intervention Tracking (23 columns):**
- Level 1-4 escalation logging
- Response time tracking
- Outcome measurement
- Parent outreach documentation
- Zone/anxiety before/after comparison
- Crisis intervention notes
- Time spent tracking (Trevor's 10% monitoring)

**Progress Dashboard (6 sections, 32+ metrics):**
- Cohort overview (total students, active/lagging/stuck)
- Zone distribution (baseline vs current comparison)
- Emotional job tracking (anxiety reduction scores)
- 4 Habits practice rates
- Engagement metrics (participation, CIS usage, artifact completion)
- Trevor's 10% time tracking

### Manual Setup Required

After script runs, complete these manual steps:

**1. Set up Data Validation (Drop-down menus):**
- Open spreadsheet in Google Sheets
- For each sheet, select columns that need drop-downs
- Go to: Data > Data Validation
- Choose "Dropdown" from criteria
- Add options from specification

**Example for Student Roster > Zone Baseline:**
- Select column H (Zone Baseline)
- Data > Data Validation
- Criteria: Dropdown
- Options: Zone 0, Zone 1, Zone 2, Zone 3, Zone 4

**2. Set up Conditional Formatting (Alerts):**
- Format > Conditional formatting
- Create rules for:
  - Crisis flags → RED background
  - High anxiety spike → ORANGE background
  - Student stuck → YELLOW background
  - Zone shift → GREEN background

**3. Create Charts and Visualizations (Progress Dashboard):**
- Insert > Chart
- Use metrics from dashboard sections
- Create:
  - Zone distribution pie chart
  - Anxiety reduction line chart
  - 4 Habits practice stacked bar chart
  - Engagement rate line chart

**4. Test Formulas:**
- Add sample data to Student Roster (2-3 rows)
- Verify formulas calculate correctly
- Check cross-sheet references (VLOOKUPs)
- Test data validation rules

---

## Option 2: Manual Creation (No API)

If you prefer not to set up Google Sheets API, create sheets manually:

### Step 1: Create Spreadsheet

1. Go to https://sheets.google.com
2. Click "Blank" spreadsheet
3. Rename to "K2M Cohort #1 - Operations Templates"

### Step 2: Create 5 Sheets

1. Rename "Sheet1" to "Student Roster"
2. Click "+" to add sheets:
   - Submissions Log
   - Intervention Tracking
   - Progress Dashboard
   - Summary

### Step 3: Add Columns (Copy from Spec)

**Student Roster - Row 1 (Headers):**
```
Timestamp | Student ID | First Name | Last Name | Email Address | Discord Username | Age | Zone Baseline | Zone Current | Zone Shift | AI Experience Level | Anxiety Baseline | Anxiety Current | Anxiety Change | Confidence Level | Motivation | Goals | 4 Habits Pre-Assessment | Parent/Guardian Name | Parent Phone Number | Parent Email Address | Emergency Contact Backup | Weekly Updates Consent | Cluster Assignment | Crisis Flag | Intervention Priority | Trevor Review Notes | Outreach Status | First Contact Date | Live Session Attendance | Engagement Status | Habit 1 Practice | Habit 2 Practice | Habit 3 Practice | Habit 4 Practice | Artifact Status | Graduation Proof | Data Retention Date | Notes
```

**Student Roster - Row 2 (Formulas):**
- Zone Shift: `=IF(AND(H2="Zone 0", I2="Zone 0"), "Not started (Zone 0)", IF(I2="Zone 1", "Zone 0→1", IF(I2="Zone 2", "Zone 1→2", IF(I2="Zone 3", "Zone 2→3", IF(I2="Zone 4", "Zone 3→4", "Stuck")))))`
- Anxiety Change: `=M2-L2`
- Cluster Assignment: `=IF(UPPER(LEFT(D2,1))<="F", "Cluster 1 (A-F)", IF(UPPER(LEFT(D2,1))<="L", "Cluster 2 (G-L)", IF(UPPER(LEFT(D2,1))<="R", "Cluster 3 (M-R)", "Cluster 4 (S-Z)")))`
- Crisis Flag: `=IF(L2>=7, "HIGH ANXIETY", IF(OR(ISNUMBER(SEARCH("hopeless", P2)), ISNUMBER(SEARCH("suicide", Q2)), ISNUMBER(SEARCH("self-harm", P2))), "CRISIS", IF(AND(N2>=3, OR(L2>=7)), "EMOTIONAL ESCALATION", "OK")))`
- Intervention Priority: `=IF(AND(H2="Zone 0", L2>=7), "LEVEL 3: IMMEDIATE outreach", IF(AND(H2="Zone 0", L2>=5), "LEVEL 2: Monitor + DM", IF(L2>=8, "LEVEL 3: Check in", "LEVEL 1: Normal monitoring")))`
- Data Retention Date: `=A2+180`

**Submissions Log - Row 1 (Headers):**
```
Submission ID | Timestamp | Week Number | Day of Week | Student ID | Student Name | Cluster | Post Type | Channel Location | CIS Agent Used | Post Content | Thinking Depth Indicator | Zone Mentioned | Habit Mentioned | Emotional Tone | Engagement Depth | Trevor Review | Trevor Feedback | Escalation Flag | Engagement Pattern | Week Total | Notes
```

**Submissions Log - Row 2 (Formulas):**
- Engagement Depth: `=IF(J2="None", 1, IF(OR(J2="/frame", J2="/diverge", J2="/challenge"), 2, 3)) + IF(L2="Growth Edge", 3, IF(OR(L2="Synthesizing", L2="Self-Aware"), 2, IF(L2="Experimenting", 1, 0)))`
- Engagement Pattern: `=IF(U2>=5, "Consistent", IF(U2>=2, "Intermittent", "Disengaged"))`
- Week Total: `=COUNTIFS(E:E, E2, C:C, C2)`

**Intervention Tracking - Row 1 (Headers):**
```
Intervention ID | Timestamp | Week Number | Student ID | Student Name | Cluster | Intervention Type | Trigger | Method | Response Time | Duration | Outcome | Follow-Up Required | Follow-Up Date | Trevor Notes | Zone Before | Zone After | Anxiety Before | Anxiety After | CIS Agent Recommended | Parent Contacted | Parent Contact Reason | Data Retention Date
```

**Intervention Tracking - Row 2 (Formulas):**
- Data Retention Date: `=B2+180`

### Step 4: Set up Data Validation

For each column with drop-down options:

**Student Roster:**
- Zone Baseline: Zone 0, Zone 1, Zone 2, Zone 3, Zone 4
- Zone Current: Zone 0, Zone 1, Zone 2, Zone 3, Zone 4
- Weekly Updates Consent: Yes, No, Not sure yet
- Outreach Status: Not contacted, Nudged, DM sent, Call scheduled, Crisis contacted
- Artifact Status: Not started, In progress, Submitted, Published

**Submissions Log:**
- Post Type: Daily Prompt, Friday Reflection, Self-Assessment, CIS Interaction, Artifact Submission, Other
- CIS Agent Used: None, /frame, /diverge, /challenge, /synthesize, /create-artifact
- Thinking Depth Indicator: Self-Aware, Experimenting, Synthesizing, Needs Scaffolding, Growth Edge
- Emotional Tone: Positive, Neutral, Negative, Mixed, Crisis Flag
- Escalation Flag: Yes, No

**Intervention Tracking:**
- Intervention Type: Level 1 - Bot Nudge, Level 2 - Trevor DM, Level 3 - Direct Call, Level 4 - Crisis Intervention, Live Session, Friday Spot-Check, Parent Outreach
- Trigger: Diagnostic Flag, Stuck 3+ Days, High Anxiety, Crisis Keyword, Zone 0 Support, Zone Progression, Parent Request, Live Session Prep, Other
- Method: DM, Phone Call, Email, In-Person (Live Session), Parent Contact
- Outcome: Resolved, Improved, No Change, Escalated, Crisis Resolved, Ongoing Support
- Parent Contact Reason: Crisis Intervention, Weekly Update, Live Session Reminder, Student Concern, Other

### Step 5: Set up Conditional Formatting

**Crisis Alert (RED):**
- Apply to: Student Roster > Crisis Flag column
- Condition: Is "CRISIS"
- Format: Red background, white text

**High Anxiety Alert (ORANGE):**
- Apply to: Student Roster > Anxiety Change column
- Condition: Greater than or equal to 3
- Format: Orange background

**Student Stuck (YELLOW):**
- Apply to: Student Roster > Engagement Status column
- Condition: Is "Stuck"
- Format: Yellow background

**Zone Shift Celebration (GREEN):**
- Apply to: Student Roster > Zone Shift column
- Condition: Contains "Zone" (e.g., "Zone 0→1")
- Format: Green background

### Step 6: Create Progress Dashboard Charts

**Zone Distribution (Pie Chart):**
- Data: Student Roster > Zone Current column
- Create pivot table: COUNTIF per zone
- Insert > Chart > Pie chart

**Anxiety Reduction (Line Chart):**
- Data: Student Roster > Anxiety Baseline vs Anxiety Current
- Insert > Chart > Line chart
- Show progression Week 1 → Week 8

**4 Habits Practice (Stacked Bar Chart):**
- Data: Student Roster > Habit 1-4 columns
- Insert > Chart > Stacked bar chart
- Show % students practicing each habit

---

## Testing & Validation

**Test with Sample Data:**

1. **Add 3 sample students to Student Roster:**
   - Student 1: Zone 0, Anxiety 8, Cluster 1
   - Student 2: Zone 1, Anxiety 5, Cluster 2
   - Student 3: Zone 2, Anxiety 3, Cluster 3

2. **Verify formulas calculate:**
   - Crisis flags trigger correctly (Anxiety >= 7)
   - Cluster assignments match (A-F, G-L, M-R, S-Z)
   - Zone shifts show progression

3. **Add sample submissions to Submissions Log:**
   - 5 daily posts
   - 2 Friday reflections
   - 3 CIS agent interactions

4. **Check engagement patterns:**
   - Week Total calculates correctly
   - Engagement Pattern classifies (Consistent/Intermittent/Disengaged)

5. **Add sample interventions:**
   - 2 Level 1 (Bot Nudge)
   - 1 Level 2 (Trevor DM)
   - 1 Level 4 (Crisis)

6. **Verify Progress Dashboard:**
   - Metrics update from source sheets
   - Charts render correctly
   - Formulas reference correct ranges

---

## Deployment Workflow

**Before Cohort Launch:**

1. ✅ Create 4 Google Sheets templates (using Option 1 or 2)
2. ✅ Connect Google Forms diagnostic → Student Roster
3. ✅ Test all formulas with sample data
4. ✅ Set up data validation and conditional formatting
5. ✅ Share settings: Trevor only (private)
6. ✅ Enable revision history (for audit trail)

**Week 1:**
1. Import diagnostic data from Google Forms
2. Review Student Roster for crisis flags
3. Send Level 3 outreach (high-priority students)
4. Begin daily monitoring routine

**Weeks 2-8:**
1. Daily: Check Submissions Log for crisis flags (5-10 min)
2. Friday: Review 15-20 reflections (30-45 min)
3. Weekly: Update Progress Dashboard metrics (15 min)
4. Ongoing: Log interventions in Intervention Tracking

**After Cohort Completion:**
1. Archive sheets (move to "Past Cohorts" folder)
2. Data retention: Auto-delete after 180 days (or manual export)
3. Review metrics: What worked? What didn't?
4. Update templates for next cohort

---

## Privacy & Security

**Access Control:**
- ✅ Trevor only (no student access)
- ✅ Enable revision history (audit trail)
- ✅ Share settings: "Viewer" for external stakeholders (aggregated data only)

**Data Retention:**
- ✅ 180-day auto-delete formula (Data Retention Date column)
- ✅ Manual export option (for long-term storage, if needed)
- ✅ Crisis data: Separate restricted columns

**Crisis Protocol:**
- ✅ Crisis Flag column triggers RED alert
- ✅ Trevor notified immediately (daily morning scan)
- ✅ Level 4 protocol: Immediate outreach (<1 hour)
- ✅ Parent contact for minors (<18)

---

## Troubleshooting

**Issue: Formula errors (#REF!, #VALUE!)**
- Solution: Check cell references (e.g., H2 should be Zone Baseline)
- Verify sheet names match (Student Roster, Submissions Log, etc.)

**Issue: Data validation not working**
- Solution: Re-create drop-down using Data > Data Validation
- Ensure options match specification exactly

**Issue: Conditional formatting not triggering**
- Solution: Check formula syntax (e.g., =L2>=7 not L2>=7)
- Verify applied range covers all data rows

**Issue: Charts not updating**
- Solution: Refresh pivot tables (Data > Refresh)
- Check data ranges (expand to include new rows)

---

## Support

**Documentation:**
- Full specification: `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-5-sheets-templates.md`
- Discord architecture: `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-1-discord-server-structure.md`

**For Issues:**
- Check sprint status: `_bmad-output/cohort-design-artifacts/discord-implementation-sprint.yaml`
- Review task 0.6 completion notes
- Consult Story 5.5 specification for column details

**Next Steps:**
- Task 0.7: Deploy bot to production (after Sprint 1 completion)
- Task 1.1: Scaffold Python bot project
- Sprint 1: Bot Core Engine (4-5 days)

---

**Task 0.6 Status:** ✅ COMPLETE - 4 Google Sheets templates ready for deployment
