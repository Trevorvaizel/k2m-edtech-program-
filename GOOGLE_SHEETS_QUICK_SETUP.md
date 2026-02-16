# Quick Setup: Google Sheets Templates

## Fastest Path (10 minutes - Manual)

If you don't want to set up Google Sheets API, use this manual approach:

### Step 1: Create Spreadsheet (1 min)
1. Go to https://sheets.google.com
2. Click "Blank"
3. Rename to: "K2M Cohort #1 - Operations Templates"

### Step 2: Create 5 Sheets (1 min)
1. Double-click "Sheet1" → Rename to "Student Roster"
2. Click "+" → Rename to "Submissions Log"
3. Click "+" → Rename to "Intervention Tracking"
4. Click "+" → Rename to "Progress Dashboard"
5. Click "+" → Rename to "Summary"

### Step 3: Copy Column Headers (3 min)

**Student Roster - Row 1:**
Copy this entire line and paste into A1:
```
Timestamp	Student ID	First Name	Last Name	Email	Address	Discord	Age	Zone Baseline	Zone Current	Zone Shift	AI Exp	Anxiety Baseline	Anxiety Current	Anxiety Change	Confidence	Motivation	Goals	4 Habits	Parent Name	Parent Phone	Parent Email	Emergency Contact	Consent	Cluster	Crisis Flag	Priority	Review Notes	Outreach	First Contact	Attendance	Engagement	H1	H2	H3	H4	Artifact	Graduation	Retention	Notes
```

**Submissions Log - Row 1:**
```
Submission ID	Timestamp	Week	Day	Student ID	Name	Cluster	Post Type	Channel	CIS Agent	Content	Depth Indicator	Zone	Habit	Emotional Tone	Engagement Depth	Trevor Review	Feedback	Escalation	Pattern	Week Total	Notes
```

**Intervention Tracking - Row 1:**
```
Intervention ID	Timestamp	Week	Student ID	Name	Cluster	Type	Trigger	Method	Response Time	Duration	Outcome	Follow-up	Follow-up Date	Notes	Zone Before	Zone After	Anxiety Before	Anxiety After	CIS Recommended	Parent Contact	Parent Reason	Retention
```

### Step 4: Add Key Formulas (3 min)

**Student Roster - Add these formulas to Row 2:**
- J2 (Zone Shift): `=IF(AND(I2="Zone 0", J2="Zone 0"), "Not started", IF(J2="Zone 1", "Zone 0→1", IF(J2="Zone 2", "Zone 1→2", IF(J2="Zone 3", "Zone 2→3", IF(J2="Zone 4", "Zone 3→4", "Stuck")))))`
- N2 (Anxiety Change): `=M2-L2`
- AA2 (Cluster): `=IF(UPPER(LEFT(D2,1))<="F", "Cluster 1", IF(UPPER(LEFT(D2,1))<="L", "Cluster 2", IF(UPPER(LEFT(D2,1))<="R", "Cluster 3", "Cluster 4")))`
- AB2 (Crisis Flag): `=IF(L2>=7, "HIGH ANXIETY", "OK")`
- AC2 (Priority): `=IF(AND(I2="Zone 0", L2>=7), "LEVEL 3", IF(AND(I2="Zone 0", L2>=5), "LEVEL 2", "LEVEL 1"))`
- AJ2 (Retention): `=A2+180`

**Submissions Log - Add to Row 2:**
- P2 (Engagement Depth): `=IF(J2="None", 1, IF(OR(J2="/frame", J2="/diverge"), 2, 3))`
- T2 (Pattern): `=IF(U2>=5, "Consistent", IF(U2>=2, "Intermittent", "Disengaged"))`
- U2 (Week Total): `=COUNTIFS(E:E, E2, C:C, C2)`

**Intervention Tracking - Add to Row 2:**
- W2 (Retention): `=B2+180`

### Step 5: Set Up Basic Conditional Formatting (2 min)

**Student Roster > Crisis Flag Column (AB):**
1. Select AB2:AB1000
2. Format > Conditional formatting
3. Format rules > Single color
4. Format cells if: "Is equal to" → "HIGH ANXIETY" or "CRISIS"
5. Formatting style: Red background, white text
6. Done

**Student Roster > Engagement Status Column (AG):**
1. Select AG2:AG1000
2. Format > Conditional formatting
3. Add rule: "Is equal to" → "Stuck" → Yellow background
4. Add rule: "Is equal to" → "Active" → Green background
5. Done

### Step 6: Freeze Header Rows (1 min)
- Student Roster: View > Freeze > 2 rows
- Submissions Log: View > Freeze > 2 rows
- Intervention Tracking: View > Freeze > 2 rows

### ✅ Done!

Your templates are ready. Test with sample data:

**Test Student Roster:**
- Row 2: John | Doe | Zone 1 | Anxiety 5 | A-F
- Row 3: Jane | Smith | Zone 0 | Anxiety 8 | M-R
- Verify: Cluster assignments calculate, Crisis flag triggers for Jane

**Test Submissions Log:**
- Row 2: SUB_001 | Week 1 | John Doe | Daily Prompt | /frame | Positive
- Verify: Engagement Depth calculates

**Test Intervention Tracking:**
- Row 2: INT_001 | Week 1 | John Doe | Level 1 | Bot Nudge | Resolved
- Verify: Retention date calculates

---

## Next Steps

**When Ready:**
1. Connect Google Forms → Student Roster ( Responses > Link to Sheets )
2. Import diagnostic data
3. Review crisis flags
4. Start daily monitoring routine

**For Full Spec:**
See: `GOOGLE_SHEETS_TEMPLATES_README.md` (detailed formulas, data validation, SOPs)

**For Story 5.5 Spec:**
See: `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-5-sheets-templates.md`

---

**Time Required:** 10 minutes
**Skill Level:** Beginner (no coding required)
**Result:** 4 working templates ready for cohort launch
