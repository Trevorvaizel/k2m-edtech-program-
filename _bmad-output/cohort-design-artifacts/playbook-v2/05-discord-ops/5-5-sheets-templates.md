# Story 5.5: Google Sheets Templates for Cohort Operations

**Epic:** 5 - Discord Architecture & Operations (Modules 4, 11)
**Story:** 5.5 - Create tracking Sheets templates
**Status:** ready-for-dev
**Created:** 2026-01-25
**Purpose:** Create comprehensive Google Sheets templates for manual cohort operations tracking (student roster, submissions log, intervention tracking, progress dashboard) enabling Trevor's 10% workflow (Decision 2, 16) and agent-facilitated model (Decision 1)

---

## Story

As a **Cohort Operations Designer**,
I want **complete Google Sheets templates for tracking all cohort operations (roster, submissions, interventions, progress)**,
so that **Trevor can manually manage the 10% human layer (Decision 2, 16), track student progress across 8 weeks, monitor engagement, execute targeted interventions, and measure success metrics**.

---

## Acceptance Criteria

1. **Student Roster Template** with complete student data (demographics, diagnostic results, cluster assignment, parent contact, crisis flags) enabling Trevor's pre-cohort review and ongoing monitoring
2. **Submissions Log Template** for tracking daily posts, Friday reflections, self-assessments, CIS agent interactions, and engagement patterns
3. **Intervention Tracking Template** for documenting Trevor's 10% interventions (spot-checks, escalations, live sessions, crisis response) with timestamps and outcomes
4. **Progress Dashboard Template** with automated formulas for zone shifts, habit practice, engagement rates, and success metrics tracking
5. **Cross-Sheet Integration** specifying how templates reference each other (Student ID as foreign key, automated data flow, summary views)
6. **Manual Workflow Documentation** specifying Trevor's weekly workflows (Friday spot-checks, intervention triggers, escalation protocols, parent outreach)
7. **Data Validation Rules** ensuring data integrity (drop-down menus, required fields, format constraints, formula validation)
8. **Privacy & Security Design** implementing Guardrails #6, #8 through access controls (Trevor only), data retention (6-month deletion), and confidential handling

---

## Tasks / Subtasks

- [ ] **1. Create Student Roster Template** (AC: #1)
  - [ ] 1.1 Design column structure (20+ columns from Story 5.4 diagnostic)
  - [ ] 1.2 Create cluster assignment formulas (A-F, G-L, M-R, S-Z)
  - [ ] 1.3 Build crisis flag formulas (anxiety >7, crisis keywords, Zone 0)
  - [ ] 1.4 Design intervention priority formulas (Level 1-4)
  - [ ] 1.5 Create Trevor review dashboard views (high-priority, zone distribution, cluster balance)

- [ ] **2. Create Submissions Log Template** (AC: #2)
  - [ ] 2.1 Design submission tracking columns (date, student ID, post type, content quality)
  - [ ] 2.2 Create engagement scoring formulas (active, lagging, stuck)
  - [ ] 2.3 Build streak tracking (daily posts, Friday reflections, CIS usage)
  - [ ] 2.4 Design cross-reference to Student Roster (Student ID lookup)
  - [ ] 2.5 Create weekly summary views (participation rate, completion rate)

- [ ] **3. Create Intervention Tracking Template** (AC: #3)
  - [ ] 3.1 Design intervention log columns (date, student ID, type, trigger, outcome)
  - [ ] 3.2 Create escalation tracking (Level 1 bot nudge → Level 4 crisis)
  - [ ] 3.3 Build time-tracking formulas (response time, resolution time)
  - [ ] 3.4 Design parent outreach log (contact type, reason, outcome)
  - [ ] 3.5 Create intervention effectiveness summary (success rate, common patterns)

- [ ] **4. Create Progress Dashboard Template** (AC: #4)
  - [ ] 4.1 Design zone shift tracking (Week 1 → Week 8 progression)
  - [ ] 4.2 Create habit practice metrics (Pause, Context, Iterate, Think First)
  - [ ] 4.3 Build engagement rate formulas (daily posts, reflections, CIS usage)
  - [ ] 4.4 Design success metrics (JTBD alignment, identity shifts, artifact completion)
  - [ ] 4.5 Create visual dashboard (charts, graphs, trend lines)

- [ ] **5. Specify Cross-Sheet Integration** (AC: #5)
  - [ ] 5.1 Define Student ID as foreign key (all sheets reference Roster)
  - [ ] 5.2 Document VLOOKUP/INDEX-MATCH formulas (data flow between sheets)
  - [ ] 5.3 Create summary sheet (aggregates data from all templates)
  - [ ] 5.4 Design automated alerts (engagement drops, crisis flags, milestone achievements)
  - [ ] 5.5 Document data validation rules (consistency across sheets)

- [ ] **6. Document Manual Workflow SOPs** (AC: #6, Decision 16)
  - [ ] 6.1 Specify Friday spot-check workflow (15-20 reflections, priority list)
  - [ ] 6.2 Document daily monitoring routine (engagement scan, crisis flags)
  - [ ] 6.3 Create escalation protocol checklists (Level 1-4 triggers)
  - [ ] 6.4 Design live session preparation workflow (cluster attendance, topic selection)
  - [ ] 6.5 Build weekly review checklist (progress summary, intervention planning)

- [ ] **7. Define Data Validation Rules** (AC: #7)
  - [ ] 7.1 Create drop-down menus (zones, clusters, intervention types, outcomes)
  - [ ] 7.2 Specify required fields (Student ID, name, cluster, diagnostic data)
  - [ ] 7.3 Design format constraints (dates, phone numbers, email addresses)
  - [ ] 7.4 Build formula validation (crisis flags, intervention priorities)
  - [ ] 7.5 Document data quality checks (duplicate detection, missing data alerts)

- [ ] **8. Implement Privacy & Security Design** (AC: #8, Guardrails #6, #8)
  - [ ] 8.1 Specify access controls (Trevor only, no student access)
  - [ ] 8.2 Design data retention policy (6-month auto-delete, manual export option)
  - [ ] 8.3 Create privacy audit log (who accessed what, when)
  - [ ] 8.4 Document crisis data handling (confidential notes, parent contact)
  - [ ] 8.5 Build anonymization for reporting (aggregate views, no PII)

---

## Dev Notes

### Strategic Context (Decisions 1, 2, 7, 15, 16 + Guardrails + JTBD)

**Google Sheets are the PRIMARY data management system for Cohort 1 (Decision 15: Simplified Tech Stack).**

This story creates the manual workflow infrastructure that enables:

**Decision 1 (Agent-Facilitated Model):**
- Agents handle 90% (automated prompts, tracking, nudges)
- Trevor handles 10% (manual review, interventions, culture monitoring)
- Sheets provide the data layer that connects agent automation → human oversight

**Decision 2 (90/10 Hybrid Model):**
- Trevor's 10% includes:
  - Friday spot-checks (15-20 reflections)
  - 1-hour live sessions (3 sessions/week, 8 clusters)
  - Escalations (agent flags students stuck 3+ days)
  - Culture monitoring (norms, engagement, safety)
- Sheets track all of this → Trevor works efficiently at scale

**Decision 7 (Manual Workflows):**
- Trevor manually reviews diagnostic results
- Trevor manually assigns clusters
- Trevor manually sends nudges
- Trevor manually identifies intervention needs
- Sheets make this manual workflow efficient (formulas, filters, views)

**Decision 16 (Trevor's 10% Role):**
- Sheets enable targeted interventions (diagnostic flags, engagement tracking)
- Sheets support spot-check selection (high-priority students first)
- Sheets document escalation history (crisis flags, parent outreach)
- Sheets measure cohort health (zone distribution, engagement rates)

### Foundation Documents Integration (Epic 1 - All Non-Negotiable)

**Story 5.5 MUST implement these Epic 1 foundations:**

**1. Guardrails (Story 1.1) - ALL 11 ENFORCED:**

**Guardrail #1 (Identity Protection):**
- Sheets track zone progression (not "technical skill" levels)
- Success metrics = thinking habits, not AI proficiency
- No comparison/ranking columns (Guardrail #3 compliance)

**Guardrail #3 (No Comparison/Ranking):**
- Sheets track individual progress only
- Aggregate views show patterns, NEVER student rankings
- Engagement scores = internal quality markers, not comparison tools

**Guardrail #6 (Agent Purity):**
- Sheets track agent interventions (bot nudges, CIS interactions)
- Trevor's manual interventions are separate from agent automation
- Clear separation: Agent triggers (90%) → Human escalations (10%)

**Guardrail #8 (Discord Safety - Private Process):**
- Sheets are CONFIDENTIAL (Trevor only)
- Crisis data in separate columns (restricted access)
- Parent contact stored securely (Level 4 crisis protocol)

**Guardrail #10 (Brand Voice - Revolutionary Hope):**
- Progress metrics celebrate thinking growth ("You're shifting from Zone 1 to Zone 2")
- NOT judgment ("You're falling behind")
- Dashboard language uses hope + empowerment tone

**2. JTBD Integration (Story 1.2):**

**Emotional Job Tracking:**
- Anxiety levels tracked (from diagnostic, weekly check-ins)
- Belonging cues monitored (engagement patterns, "I don't belong" flags)
- Emotional progression celebrated (Zone shifts = identity shifts)

**Social Job Tracking:**
- Parent engagement logged (weekly updates sent, crisis contacts)
- Artifact preparation tracked (CIS agent usage → thinking artifact readiness)
- Graduation proof documented (4 Habits practice, demonstration)

**Identity Shift Tracking:**
- Zone progression: Outsider (Zone 0) → Observer (Zone 1) → Experimenter (Zone 2) → Collaborator (Zone 3) → Director (Zone 4)
- Sheets track weekly zone self-assessments → progression visualization
- Success metric = identity transformation, not "completion"

**3. Node Architecture (Story 1.3):**

**16 Node Tracking:**
- Sheets track which nodes students have engaged with
- Node completion markers (witnessed, relatable, permission, fun)
- Next node recommendations (based on zone placement)

**Zone Transition Tracking:**
- Zone 0→1 (Wonder): Nodes 0.1-0.4 engagement
- Zone 1→2 (Trust): Nodes 1.1-1.4 engagement
- Zone 2→3 (Converse): Nodes 2.1-2.4 engagement
- Zone 3→4 (Direct): Nodes 3.1-3.4 engagement

**4. 4 Habits Branding (Story 1.4):**

**Habit Practice Tracking:**
- ⏸️ **Pause** (Habit 1): Tracked in Week 1-2 (before asking AI)
- 🎯 **Context** (Habit 2): Tracked in Week 2-3 (explain first)
- 🔄 **Iterate** (Habit 3): Tracked in Week 4-5 (change one thing)
- 🧠 **Think First** (Habit 4): Tracked in Week 6-7 (use before decisions)

**Habit Demonstration:**
- Sheets track habit practice (daily prompts, reflections)
- Sheets track habit application (CIS agent usage: /frame, /diverge, /challenge, /synthesize)
- Graduation card preparation: Which habits does student demonstrate?

### Integration with Story 5.1-5.4

**Story 5.1 (Discord Server Architecture):**
- **Cluster Assignment System:** Sheets track 8 clusters (A-F, G-L, M-R, S-Z, plus overflow)
- **Live Session Attendance:** Sheets track who attends Trevor's 1-hour sessions (3 sessions/week)
- **Channel Unlock Tracking:** Sheets track progressive disclosure (weekly channel unlocks)
- **Crisis Intervention Protocol:** Sheets track Level 4 escalations (Trevor → parent)

**Story 5.2 (#thinking-lab Setup):**
- **CIS Agent Interactions:** Sheets track /frame, /diverge, /challenge, /synthesize usage
- **Private Process Documentation:** Sheets log student CIS conversations (DM/Thread privacy)
- **Escalation Triggers:** Sheets flag students stuck 3+ days (agent → Trevor handoff)

**Story 5.3 (#thinking-showcase Setup):**
- **Artifact Publication Tracking:** Sheets track who publishes to #thinking-showcase
- **Parent Notification System:** Sheets track weekly email sends (consent-based)
- **Celebration Metrics:** Sheets track artifact completions, peer engagement (reactions, comments)

**Story 5.4 (Google Forms Diagnostic):**
- **Student Onboarding Profile (SOP 0):** Sheets import diagnostic data (20+ columns)
- **Zone Baseline:** Sheets capture Week 1 zone placement
- **Emotional Baseline:** Sheets capture anxiety, confidence, motivation
- **Parent Contact:** Sheets store required crisis intervention data

---

## Template 1: Student Roster

**Purpose:** Master student database with diagnostic data, cluster assignment, crisis flags, and intervention priorities.

**Sheet Name:** `Student Roster`

**Column Structure:**

```yaml
A: Timestamp (Auto-generated from Google Forms)
B: Student ID (Auto-generated: FIRST_LAST_####)
C: First Name
D: Last Name (for cluster assignment)
E: Email Address
F: Discord Username (optional, for matching)
G: Age (16/17/18/19+)
H: Zone Baseline (Week 1 diagnostic: Zone 0, Zone 1, Zone 2, Zone 3, Zone 4)
I: Zone Current (Updated weekly: Week 2-8 self-assessment)
J: Zone Shift (Formula: =IF(AND(H="Zone 0", I="Zone 0"), "Not started (Zone 0)", IF(I="Zone 1", "Zone 0→1", IF(I="Zone 2", "Zone 1→2", IF(I="Zone 3", "Zone 2→3", IF(I="Zone 4", "Zone 3→4", IF(AND(H="Zone 0", I="Zone 0", C2>=3), "Stuck at Zone 0", I)))))))
K: AI Experience Level (Never used, Tried a few times, Use regularly, Use daily)
L: Anxiety Baseline (Week 1 diagnostic: 1-10 scale)
M: Anxiety Current (Weekly check-in: 1-10 scale)
N: Anxiety Change (Formula: =M-L)
O: Confidence Level (Not at all / Somewhat / Fairly / Very / Haven't thought)
P: Motivation (Free text from diagnostic)
Q: Goals (Free text from diagnostic)
R: 4 Habits Pre-Assessment (Checkboxes: Pause, Context, Iterate, Think First, None yet)
S: Parent/Guardian Name (Required)
T: Parent Phone Number (Required, format: 254XXXXXXXXX or +XXXXXXXXXX)
U: Parent Email Address (Required)
V: Emergency Contact Backup (Optional)
W: Weekly Updates Consent (Yes / No / Not sure yet)
X: Cluster Assignment (Formula: =IF(UPPER(LEFT(D2,1))<="F", "Cluster 1 (A-F)", IF(UPPER(LEFT(D2,1))<="L", "Cluster 2 (G-L)", IF(UPPER(LEFT(D2,1))<="R", "Cluster 3 (M-R)", "Cluster 4 (S-Z)")))
  Note: Simplified formula - explicit ranges prevent overlap. Edge cases (hyphenated names, spaces) handled manually by Trevor.)
Y: Crisis Flag (Formula: =IF(L>=7, "HIGH ANXIETY", IF(OR(ISNUMBER(SEARCH("hopeless", P2)), ISNUMBER(SEARCH("hopeless", Q2)), ISNUMBER(SEARCH("suicide", P2)), ISNUMBER(SEARCH("suicide", Q2)), ISNUMBER(SEARCH("self-harm", P2)), ISNUMBER(SEARCH("self-harm", Q2)), ISNUMBER(SEARCH("depressed", P2)), ISNUMBER(SEARCH("end it all", P2)), ISNUMBER(SEARCH("kill myself", P2)), ISNUMBER(SEARCH("no point", P2)), ISNUMBER(SEARCH("giving up", P2)), ISNUMBER(SEARCH("want to die", P2)), ISNUMBER(SEARCH("can't go on", P2))), "CRISIS", IF(AND(N>=3, OR(L>=7)), "EMOTIONAL ESCALATION", "OK")))
Z: Intervention Priority (Formula: =IF(AND(H="Zone 0", L>=7), "LEVEL 3: IMMEDIATE outreach", IF(AND(H="Zone 0", L>=5), "LEVEL 2: Monitor + DM", IF(L>=8, "LEVEL 3: Check in", "LEVEL 1: Normal monitoring"))))
AA: Trevor Review Notes (Manual: Trevor adds notes after diagnostic review)
AB: Outreach Status (Manual: Not contacted, Nudged, DM sent, Call scheduled, Crisis contacted)
AC: First Contact Date (Manual: Date of first Trevor outreach)
AD: Live Session Attendance (Manual: Track attendance at 1-hour sessions)
AE: Engagement Status (Formula from Submissions Log: Active, Lagging, Stuck)
AF: Habit 1 Practice (⏸️ Pause - Count of reflections showing Pause)
AG: Habit 2 Practice (🎯 Context - Count of reflections showing Context)
AH: Habit 3 Practice (🔄 Iterate - Count of reflections showing Iterate)
AI: Habit 4 Practice (🧠 Think First - Count of reflections showing Think First)
AJ: Artifact Status (Not started, In progress, Submitted, Published)
AK: Graduation Proof (Which 4 Habits demonstrated? Manual: Trevor assessment)
AL: Data Retention Date (Formula: =A2+180)
AM: Notes (Ongoing cohort notes - milestones, celebrations, concerns)
```

**Dashboard Views (Filters + Sorting):**

**View 1: High-Priority Students (For Trevor review)**
```
Filter: Crisis Flag = "HIGH ANXIETY" OR "CRISIS" OR Zone Baseline = "Zone 0"
Sort: Anxiety Baseline (descending), then Intervention Priority
Columns: B, C, D, H, L, Y, T, Z, AA
Action: Trevor reviews, adds notes, schedules outreach (Level 3 or Level 2)
```

**View 2: Zone Distribution Analysis**
```
Summary Formula: =COUNTIF(H:H, "Zone 0") → Zone 0 students
                  =COUNTIF(H:H, "Zone 1") → Zone 1 students
                  =COUNTIF(H:H, "Zone 2") → Zone 2 students
                  =COUNTIF(H:H, "Zone 3") → Zone 3 students
                  =COUNTIF(H:H, "Zone 4") → Zone 4 students
Action: Trevor monitors zone progression, adjusts node delivery
```

**View 3: Cluster Balance (For Trevor session planning)**
```
Summary Formula: =COUNTIF(X:X, "Cluster 1") → Cluster 1 count
                  =COUNTIF(X:X, "Cluster 2") → Cluster 2 count
                  =COUNTIF(X:X, "Cluster 3") → Cluster 3 count
                  =COUNTIF(X:X, "Cluster 4") → Cluster 4 count
Action: If any cluster >25 students, Trevor rebalances or creates Cluster 5
```

**View 4: Anxiety Reduction Tracking (JTBD Emotional Job)**
```
Filter: All students
Columns: C, L (Anxiety Baseline), M (Anxiety Current), N (Anxiety Change)
Success Metric: % students with Anxiety Change <= -2 (reduced by 2+ points)
Visualization: Line chart showing anxiety reduction Week 1 → Week 8
```

**View 5: Graduation Proof Readiness (JTBD Social Job)**
```
Filter: All students
Columns: C, AF (Habit 1), AG (Habit 2), AH (Habit 3), AI (Habit 4), AJ (Artifact Status)
Success Metric: % students practicing all 4 Habits + Artifact published
Graduation Card: If AF+AG+AH+AI >= "Consistently" AND AJ = "Published" → READY
```

**Data Validation:**

```yaml
Column H (Zone Baseline): Drop-down menu
  Options: Zone 0, Zone 1, Zone 2, Zone 3, Zone 4
  Validation: Must select one

Column I (Zone Current): Drop-down menu
  Options: Zone 0, Zone 1, Zone 2, Zone 3, Zone 4
  Validation: Must select one (updated weekly)

Column L (Anxiety Baseline): Number 1-10
  Validation: Must be between 1 and 10

Column M (Anxiety Current): Number 1-10
  Validation: Must be between 1 and 10

Column W (Weekly Updates Consent): Drop-down menu
  Options: Yes, No, Not sure yet
  Validation: Must select one
  Handling: "Not sure yet" = Treat as "No" (don't send updates) until student changes to "Yes". Trevor follows up in Week 4 live session: "Many of you weren't sure about parent updates. How are you feeling now?"

Column AB (Outreach Status): Drop-down menu
  Options: Not contacted, Nudged, DM sent, Call scheduled, Crisis contacted
  Validation: Trevor manual selection

Column AJ (Artifact Status): Drop-down menu
  Options: Not started, In progress, Submitted, Published
  Validation: Trevor manual selection
```

---

## Template 2: Submissions Log

**Purpose:** Track all student submissions (daily posts, Friday reflections, self-assessments, CIS interactions) for engagement monitoring and intervention triggers.

**Sheet Name:** `Submissions Log`

**Column Structure:**

```yaml
A: Submission ID (Auto-generated: SUB_YYYYMMDD_####)
B: Timestamp (Auto-generated: Date + time of post)
C: Week Number (Week 1-8)
D: Day of Week (Monday-Sunday)
E: Student ID (VLOOKUP from Student Roster)
F: Student Name (VLOOKUP from Student Roster)
G: Cluster (VLOOKUP from Student Roster)
H: Post Type (Drop-down: Daily Prompt, Friday Reflection, Self-Assessment, CIS Interaction, Artifact Submission, Other)
I: Channel Location (#thinking-lab, #thinking-showcase, Private DM/Thread)
J: CIS Agent Used (Drop-down: None, /frame, /diverge, /challenge, /synthesize, /create-artifact)
K: Post Content (Link to Discord message or brief summary)
L: Thinking Depth Indicator (Manual: Trevor assessment - Self-Aware, Experimenting, Synthesizing, Needs Scaffolding, Growth Edge)
M: Zone Mentioned (Did student reference zone? Yes/No)
N: Habit Mentioned (Which habit? ⏸️ Pause, 🎯 Context, 🔄 Iterate, 🧠 Think First, None)
O: Emotional Tone (Positive, Neutral, Negative, Mixed, Crisis Flag)
P: Engagement Depth (Formula: Character count, CIS agent usage, reflection quality)
Q: Trevor Review (Did Trevor review this? Yes/No)
R: Trevor Feedback (Manual: Trevor's response or nudge)
S: Escalation Flag (Does student need outreach? Yes/No)
T: Engagement Pattern (Formula: Consistent/Intermittent/Disengaged - INTERNAL TRACKING ONLY, never shared with students)
U: Week Total (Formula: Total posts this week)
V: Notes (Ongoing observations)
```

**Dashboard Views (Filters + Sorting):**

**View 1: Daily Engagement Scan (Trevor's morning routine)**
```
Filter: Timestamp = TODAY
Sort: Timestamp (descending)
Columns: C, E, F, H, J, O, S
Action: Trevor scans for crisis flags (O = "Crisis Flag"), escalation needs (S = "Yes")
Time: 5-10 minutes daily
```

**View 2: Friday Reflection Spot-Check (Trevor's Friday routine)**
```
Filter: Post Type = "Friday Reflection" AND Week Number = THIS WEEK
Sort: Thinking Depth Indicator (Growth Edge first, then Synthesizing), then Cluster
Columns: E, F, G, L, N, O, R
Action: Trevor selects 15-20 reflections to review (prioritize High-Priority from Student Roster)
Time: 30-45 minutes Friday
```

**View 3: Engagement Status (Lagging/Stuck detection)**
```
Filter: Timestamp = LAST 7 DAYS
Pivot: Student ID → Count of posts (Week Total)
Formula: =IF(U2>=5, "Active", IF(U2>=2, "Lagging", "Stuck"))
Action: Trevor flags "Stuck" students for outreach (Level 2 or Level 3)
```

**View 4: CIS Agent Usage Tracking**
```
Filter: CIS Agent Used != "None"
Pivot: CIS Agent Used → Count of usage
Success Metric: % students using /frame (Week 1-2), /diverge + /challenge (Week 4-5), /synthesize (Week 6-7)
Action: Trevor monitors CIS adoption, adjusts scaffolding
```

**View 5: Weekly Participation Rate**
```
Filter: Week Number = THIS WEEK
Formula: =COUNTUNIQUE(E:E) / Total students (from Student Roster)
Success Metric: >= 70% participation rate (active or lagging)
Action: If <70%, Trevor sends cohort-wide nudge
```

**Data Validation:**

```yaml
Column H (Post Type): Drop-down menu
  Options: Daily Prompt, Friday Reflection, Self-Assessment, CIS Interaction, Artifact Submission, Other
  Validation: Must select one

Column J (CIS Agent Used): Drop-down menu
  Options: None, /frame, /diverge, /challenge, /synthesize, /create-artifact
  Validation: Must select one

Column L (Thinking Depth Indicator): Drop-down menu
  Options: Self-Aware, Experimenting, Synthesizing, Needs Scaffolding, Growth Edge
  Validation: Trevor manual selection (for reviewed submissions only)
  Notes:
  - Self-Aware: Student recognizes own thinking ("I noticed I struggled with...")
  - Experimenting: Student tries new approaches ("I changed one thing and...")
  - Synthesizing: Student connects ideas ("This reminds me of...")
  - Needs Scaffolding: Student stuck ("I don't know how to...")
  - Growth Edge: Student ready for next zone (identity shift emerging)

Column O (Emotional Tone): Drop-down menu
  Options: Positive, Neutral, Negative, Mixed, Crisis Flag
  Validation: Trevor manual selection
  Rubric:
  - Positive: Celebration, excitement, gratitude
  - Neutral: Factual reflection, no emotion words
  - Negative: Frustration, confusion, anxiety (not crisis)
  - Mixed: Both positive and negative emotions
  - Crisis Flag: Hopeless, suicide, self-harm keywords

Column S (Escalation Flag): Drop-down menu
  Options: Yes, No
  Validation: Trevor manual selection
```

**Automated Formulas:**

```yaml
Column T (Engagement Pattern):
  Formula: =IF(U2>=5, "Consistent", IF(U2>=2, "Intermittent", "Disengaged"))
  Purpose: Classify engagement pattern for internal Trevor tracking (NEVER shared with students - Guardrail #3 compliance)

Column U (Week Total):
  Formula: =COUNTIFS(E:E, E2, C:C, C2)
  Purpose: Count total posts by student this week

Column P (Engagement Depth):
  Formula: =IF(J2="None", 1, IF(OR(J2="/frame", J2="/diverge", J2="/challenge"), 2, 3))
    + IF(L2="Growth Edge", 3, IF(OR(L2="Synthesizing", L2="Self-Aware"), 2, IF(L2="Experimenting", 1, 0)))
  Purpose: Score engagement quality (1-6 scale) for trending
  Note: Aligns with Thinking Depth Indicator categories (Self-Aware, Experimenting, Synthesizing, Needs Scaffolding, Growth Edge)

View 3 Engagement Status Formula:
  =IF(U2>=5, "Active", IF(U2>=2, "Lagging", "Stuck"))
  Purpose: Classify student engagement for intervention triggers
```

**Cross-Sheet Integration:**

```yaml
Column E (Student ID) → VLOOKUP from Student Roster (Column B, index 1 in range B:AM)
Column F (Student Name) → VLOOKUP from Student Roster (Column C, index 2 in range B:AM)
Column G (Cluster) → VLOOKUP from Student Roster (Column X, index 24 in range B:AM)

Weekly Engagement Totals → Push to Student Roster (Column AE: Engagement Status)
  Formula: =IFERROR(VLOOKUP(B2, 'Submissions Log'!E:U, 21, FALSE), "No data")
```

---

## Template 3: Intervention Tracking

**Purpose:** Document Trevor's 10% interventions (spot-checks, escalations, live sessions, crisis response) for outcome tracking and workflow optimization.

**Sheet Name:** `Intervention Tracking`

**Column Structure:**

```yaml
A: Intervention ID (Auto-generated: INT_YYYYMMDD_####)
B: Timestamp (Date + time of intervention)
C: Week Number (Week 1-8)
D: Student ID (VLOOKUP from Student Roster)
E: Student Name (VLOOKUP from Student Roster)
F: Cluster (VLOOKUP from Student Roster)
G: Intervention Type (Drop-down: Level 1 - Bot Nudge, Level 2 - Trevor DM, Level 3 - Direct Call, Level 4 - Crisis Intervention, Live Session, Friday Spot-Check, Parent Outreach)
H: Trigger (Why intervene? Drop-down: Diagnostic Flag, Stuck 3+ Days, High Anxiety, Crisis Keyword, Zone 0 Support, Zone Progression, Parent Request, Live Session Prep, Other)
I: Method (How intervened? Drop-down: DM, Phone Call, Email, In-Person (Live Session), Parent Contact)
J: Response Time (Hours from trigger to intervention)
K: Duration (Minutes spent)
L: Outcome (Drop-down: Resolved, Improved, No Change, Escalated, Crisis Resolved, Ongoing Support)
M: Follow-Up Required (Yes/No)
N: Follow-Up Date (Scheduled follow-up)
O: Trevor Notes (Free text: What happened, student response, observations)
P: Zone Before (Student's zone before intervention)
Q: Zone After (Student's zone after intervention - if measured)
R: Anxiety Before (Anxiety level before intervention)
S: Anxiety After (Anxiety level after intervention - if measured)
T: CIS Agent Recommended (Did Trevor recommend CIS agent? /frame, /diverge, /challenge, /synthesize, None)
U: Parent Contacted (Was parent contacted? Yes/No)
V: Parent Contact Reason (Why contact parent? Drop-down: Crisis Intervention, Weekly Update, Live Session Reminder, Student Concern, Other)
W: Data Retention Date (Formula: =B2+180)
```

**Dashboard Views (Filters + Sorting):**

**View 1: Weekly Intervention Summary (Trevor's review)**
```
Filter: Week Number = THIS WEEK
Pivot: Intervention Type → Count of interventions
Action: Trevor reviews 10% time allocation (am I doing too much/too little?)
Success Metric: 10-15 interventions/week (manageable 10% workload)
```

**View 2: Crisis Intervention Log (Level 4)**
```
Filter: Intervention Type = "Level 4 - Crisis Intervention"
Sort: Timestamp (most recent first)
Columns: D, E, H, J, O, U, V
Action: Trevor monitors crisis patterns, response time compliance
Review: Monthly (are crisis protocols effective?)
```

**View 3: Intervention Effectiveness**
```
Filter: All interventions
Pivot: Outcome → Count of outcomes
Formula: =(COUNTIF('Intervention Tracking'!L:L, "Resolved") + COUNTIF('Intervention Tracking'!L:L, "Improved")) / COUNTA('Intervention Tracking'!L:L)
Success Metrics:
  - % Resolved + Improved >= 70% (interventions working)
  - Average Response Time <= 24 hours (Level 1-3), <= 1 hour (Level 4)
  - Average Duration <= 30 minutes (scalable workflow)
Action: If success metrics drop, Trevor adjusts intervention approach
```

**View 4: Escalation Patterns (Who needs most support?)**
```
Filter: All interventions
Pivot: Student ID → Count of interventions
Action: Trevor identifies high-need students (5+ interventions)
Strategy: If student >5 interventions, Trevor considers personalized support plan
```

**View 5: Parent Outreach Tracking**
```
Filter: Parent Contacted = "Yes"
Sort: Timestamp (descending)
Columns: D, E, V, O, U
Action: Trevor monitors parent engagement, crisis contacts
Success Metric: Parents contacted only for valid reasons (crisis, consent, live sessions)
```

**Data Validation:**

```yaml
Column G (Intervention Type): Drop-down menu
  Options: Level 1 - Bot Nudge, Level 2 - Trevor DM, Level 3 - Direct Call, Level 4 - Crisis Intervention, Live Session, Friday Spot-Check, Parent Outreach
  Validation: Must select one

Column H (Trigger): Drop-down menu
  Options: Diagnostic Flag, Stuck 3+ Days, High Anxiety, Crisis Keyword, Zone 0 Support, Zone Progression, Parent Request, Live Session Prep, Other
  Validation: Must select one

Column I (Method): Drop-down menu
  Options: DM, Phone Call, Email, In-Person (Live Session), Parent Contact
  Validation: Must select one

Column L (Outcome): Drop-down menu
  Options: Resolved, Improved, No Change, Escalated, Crisis Resolved, Ongoing Support
  Validation: Trevor manual selection

Column V (Parent Contact Reason): Drop-down menu
  Options: Crisis Intervention, Weekly Update, Live Session Reminder, Student Concern, Other
  Validation: Required if Parent Contacted = "Yes"
```

**Escalation Protocol Tracking:**

```yaml
Level 1: Bot Nudge (Automated agent intervention)
  Trigger: Engagement = "Lagging" (2-3 posts/week)
  Action: Agent sends nudge: "Hey [Name], haven't seen you in a few days. Everything okay?"
  Response Time: Immediate (bot)
  Duration: N/A (automated)
  Outcome: Student re-engages OR escalates to Level 2

Level 2: Trevor DM (Personal check-in)
  Trigger: Engagement = "Stuck" (0-1 posts/week) OR Anxiety >= 6
  Action: Trevor DMs: "Hey [Name], noticed you haven't posted this week. Everything okay?"
  Response Time: <= 24 hours
  Duration: 5-10 minutes (DM writing)
  Outcome: Student re-engages OR escalates to Level 3

Level 3: Direct Call (High-priority outreach)
  Trigger: Crisis Flag = "HIGH ANXIETY" OR Zone 0 + Anxiety >= 7
  Action: Trevor calls: "Hey [Name], noticed you're feeling pretty anxious. Want to chat?"
  Response Time: <= 24 hours
  Duration: 15-30 minutes (call)
  Outcome: Anxiety reduces OR escalates to Level 4

Level 4: Crisis Intervention (Emergency response)
  Trigger: Crisis Keyword ("hopeless", "suicide", "self-harm", "depressed", "end it all", "kill myself", "no point", "giving up", "want to die", "can't go on") OR SafetyFilter flag OR Emotional Escalation (anxiety increase >=3 + crisis language)
  Action: Trevor calls student immediately, assesses risk, calls parent if minor (<18)
  Response Time: <= 1 hour
  Duration: 30-60 minutes (call) + follow-up
  Outcome: Crisis resolved, student connected with professional support
```

**Weekly Intervention Workflow (Trevor's SOP):**

```yaml
Monday (Day 1):
  - Morning: Review Submissions Log for weekend crisis flags (5 minutes)
  - Afternoon: Send Level 1 nudges (automated bot) to "Lagging" students
  - Evening: Review new intervention needs from weekend (10 minutes)

Tuesday (Day 2):
  - Morning: Check Submissions Log for escalation needs (5 minutes)
  - Afternoon: Send Level 2 DMs to "Stuck" students
  - Evening: Prepare for Wednesday live session (10 minutes)

Wednesday (Day 3):
  - Morning: Live session day! Attend cluster sessions, take notes (3 hours)
  - Afternoon: Follow up on live session observations (send DMs if needed)
  - Evening: Log interventions from live sessions (10 minutes)

Thursday (Day 4):
  - Morning: Review Submissions Log, check for crisis flags (5 minutes)
  - Afternoon: Send Level 2/3 interventions as needed
  - Evening: Prepare for Friday spot-checks (10 minutes)

Friday (Day 5):
  - Morning: SPOT-CHECK DAY - Review 15-20 reflections (30-45 minutes)
  - Afternoon: Log spot-checks, send feedback DMs
  - Evening: Weekly review - update Intervention Tracking summary (15 minutes)

Saturday (Day 6):
  - Morning: Crisis check only (5 minutes)
  - Afternoon: OFF (10% boundary - Trevor needs rest)

Sunday (Day 7):
  - Morning: Crisis check only (5 minutes)
  - Afternoon: Prepare for next week (10 minutes)

Total Time: 8-12 hours/week (10% is target; actual varies based on cohort needs)
```

---

## Template 4: Progress Dashboard

**Purpose:** Aggregate data from all templates into visual dashboard showing zone shifts, habit practice, engagement rates, and success metrics for cohort health monitoring.

**Sheet Name:** `Progress Dashboard`

**Dashboard Sections:**

### Section 1: Cohort Overview (Top-Level Metrics)

```yaml
Metric 1: Total Students
  Formula: =COUNTA('Student Roster'!B:B)-1 (exclude header)
  Display: Large number, top-left

Metric 2: Active This Week
  Formula: =COUNTIF('Student Roster'!AE:AE, "Active")
  Display: Number + % of total

Metric 3: Lagging This Week
  Formula: =COUNTIF('Student Roster'!AE:AE, "Lagging")
  Display: Number + % of total

Metric 4: Stuck This Week
  Formula: =COUNTIF('Student Roster'!AE:AE, "Stuck")
  Display: Number + % of total (if >20%, Trevor sends cohort nudge)

Metric 5: Zone Distribution (Week 1 Baseline)
  Formula: =COUNTIF('Student Roster'!H:H, "Zone 0") → Zone 0 count
            =COUNTIF('Student Roster'!H:H, "Zone 1") → Zone 1 count
            =COUNTIF('Student Roster'!H:H, "Zone 2") → Zone 2 count
            =COUNTIF('Student Roster'!H:H, "Zone 3") → Zone 3 count
            =COUNTIF('Student Roster'!H:H, "Zone 4") → Zone 4 count
  Display: Pie chart or bar chart

Metric 6: Zone Distribution (Current Week)
  Formula: =COUNTIF('Student Roster'!I:I, "Zone 0") → Zone 0 count
            =COUNTIF('Student Roster'!I:I, "Zone 1") → Zone 1 count
            =COUNTIF('Student Roster'!I:I, "Zone 2") → Zone 2 count
            =COUNTIF('Student Roster'!I:I, "Zone 3") → Zone 3 count
            =COUNTIF('Student Roster'!I:I, "Zone 4") → Zone 4 count
  Display: Pie chart or bar chart (compare to Week 1 baseline)

Metric 7: Zone Shift Success Rate
  Formula: =(COUNTIF('Student Roster'!J:J, "Zone 0→1") / COUNTIF('Student Roster'!H:H, "Zone 0"))
            + (COUNTIF('Student Roster'!J:J, "Zone 1→2") / COUNTIF('Student Roster'!H:H, "Zone 1"))
            + (COUNTIF('Student Roster'!J:J, "Zone 2→3") / COUNTIF('Student Roster'!H:H, "Zone 2"))
            + (COUNTIF('Student Roster'!J:J, "Zone 3→4") / COUNTIF('Student Roster'!H:H, "Zone 3"))
  Display: % of students who shifted at least 1 zone
  Success Metric: >= 60% (JTBD functional job: confusion → clarity)
```

### Section 2: Emotional Job Tracking (Anxiety Reduction)

```yaml
Metric 8: Average Anxiety (Week 1 Baseline)
  Formula: =AVERAGE('Student Roster'!L:L)
  Display: Number (1-10 scale)

Metric 9: Average Anxiety (Current Week)
  Formula: =AVERAGE('Student Roster'!M:M)
  Display: Number (1-10 scale)

Metric 10: Anxiety Reduction Score
  Formula Primary: =COUNTIF('Student Roster'!N:N, "<=-2") / COUNTA('Student Roster'!N:N)
  Formula Secondary: =COUNTIF('Student Roster'!N:N, ">=2") / COUNTA('Student Roster'!N:N)
  Display: % students with anxiety reduction >= 2 points (primary) AND % students with anxiety increase >= 2 points (secondary - flag for review)
  Success Metric: >= 50% reduced by 2+ points, <= 10% increased by 2+ points
  Visualization: Line chart showing anxiety reduction Week 1 → Week 8

Metric 11: High-Anxiety Students (Anxiety >= 7)
  Formula: =COUNTIF('Student Roster'!M:M, ">=7")
  Display: Number + % of total
  Trend: Should decrease over time (if increases, Trevor investigates)

Metric 12: Belonging Indicators (Confidence Level)
  Formula: =COUNTIF('Student Roster'!O:O, "Not at all confident") → Low belonging
            =COUNTIF('Student Roster'!O:O, "Somewhat confident") → Medium belonging
            =COUNTIF('Student Roster'!O:O, "Fairly confident") → High belonging
            =COUNTIF('Student Roster'!O:O, "Very confident") → Very high belonging
  Display: Bar chart (shift from "Not at all" → "Very" over 8 weeks)
  Success Metric: >= 50% "Fairly" or "Very" confident by Week 8
```

### Section 3: 4 Habits Practice Tracking

```yaml
Metric 13: Habit 1 (⏸️ Pause) Practice Rate
  Formula: =COUNTIF('Student Roster'!AF:AF, ">=3") / Total students
  Display: % of students consistently practicing Pause (3+ reflections)
  Success Metric: >= 70% by Week 2

Metric 14: Habit 2 (🎯 Context) Practice Rate
  Formula: =COUNTIF('Student Roster'!AG:AG, ">=3") / Total students
  Display: % of students consistently practicing Context (3+ reflections)
  Success Metric: >= 70% by Week 3

Metric 15: Habit 3 (🔄 Iterate) Practice Rate
  Formula: =COUNTIF('Student Roster'!AH:AH, ">=3") / Total students
  Display: % of students consistently practicing Iterate (3+ reflections)
  Success Metric: >= 70% by Week 5

Metric 16: Habit 4 (🧠 Think First) Practice Rate
  Formula: =COUNTIF('Student Roster'!AI:AI, ">=3") / Total students
  Display: % of students consistently practicing Think First (3+ reflections)
  Success Metric: >= 70% by Week 7

Metric 17: All 4 Habits Graduation Ready
  Formula: =COUNTIFS('Student Roster'!AF:AF, ">=3", 'Student Roster'!AG:AG, ">=3", 'Student Roster'!AH:AH, ">=3", 'Student Roster'!AI:AI, ">=3") / Total students
  Display: % of students practicing all 4 Habits consistently
  Success Metric: >= 50% by Week 8 (JTBD social job: graduation proof)

Visualization: Stacked bar chart showing each habit's practice rate over time
```

### Section 4: Engagement Metrics

```yaml
Metric 18: Weekly Participation Rate
  Formula: =COUNTUNIQUE('Submissions Log'!E:E) / 'Student Roster'!B:B (count unique students posting / total students)
  Display: % of students who posted at least once this week
  Success Metric: >= 70% (healthy cohort engagement)

Metric 19: Average Posts Per Student (Per Week)
  Formula: =COUNTA('Submissions Log'!A:A) / COUNTUNIQUE('Submissions Log'!E:E) (total posts / unique students)
  Display: Number (target: 3-5 posts/week)
  Success Metric: 3-5 posts/week (active engagement without overwhelm)

Metric 20: CIS Agent Usage Rate
  Formula: =COUNTIF('Submissions Log'!J:J, "/frame") / Total students
            + COUNTIF('Submissions Log'!J:J, "/diverge") / Total students
            + COUNTIF('Submissions Log'!J:J, "/challenge") / Total students
            + COUNTIF('Submissions Log'!J:J, "/synthesize") / Total students
  Display: % of students using CIS agents
  Success Metric: >= 50% by Week 8 (CIS adoption)

Metric 21: Live Session Attendance Rate
  Formula: =COUNTIF('Student Roster'!AD:AD, "Attended") / Total students
  Display: % of students who attended at least 1 live session
  Success Metric: >= 60% (live sessions valued)

Metric 22: Average Engagement Quality
  Formula: =AVERAGE('Submissions Log'!P:P) (Engagement Depth score)
  Display: Number (1-6 scale)
  Trend: Should increase over time (better quality reflections)
```

### Section 5: Artifact & Graduation Metrics

```yaml
Metric 23: Artifact Completion Rate
  Formula: =COUNTIF('Student Roster'!AJ:AJ, "Published") / Total students
  Display: % of students who published artifact to #thinking-showcase
  Success Metric: >= 50% (JTBD social job: proof for self, parents, future)

Metric 24: Artifact Quality Distribution
  Formula: =COUNTIF('Submissions Log'!L:L, "Exceptional") / Total artifacts
            =COUNTIF('Submissions Log'!L:L, "Strong") / Total artifacts
            =COUNTIF('Submissions Log'!L:L, "Adequate") / Total artifacts
  Display: Pie chart (artifact quality distribution)
  Success Metric: >= 70% "Strong" or "Exceptional"

Metric 25: Graduation Proof Ready
  Formula: =COUNTIFS('Student Roster'!AF:AF, ">=3", 'Student Roster'!AG:AG, ">=3", 'Student Roster'!AH:AH, ">=3", 'Student Roster'!AI:AI, ">=3", 'Student Roster'!AJ:AJ, "Published") / Total students
  Display: % of students with all 4 Habits + Published Artifact
  Success Metric: >= 40% (JTBD social job achieved)

Metric 26: Parent Engagement Rate (Weekly Updates)
  Formula: =COUNTIF('Student Roster'!W:W, "Yes") * (Number of weekly updates sent) / Total consented students
  Display: % of parents receiving weekly updates (of those who consented)
  Success Metric: 100% of consented parents receive updates
```

### Section 6: Trevor's 10% Time Tracking

```yaml
Metric 27: Total Interventions This Week
  Formula: =COUNTIF('Intervention Tracking'!C:C, THIS_WEEK)
  Display: Number (target: 10-15 interventions/week)

Metric 28: Time Spent on Interventions (Hours)
  Formula: =SUM('Intervention Tracking'!K:K) / 60 (sum duration in minutes, convert to hours)
  Display: Hours (target: 2-3 hours/week)

Metric 29: Live Session Time (Hours)
  Formula: = (Number of sessions * 1 hour) + (Prep time 30 min * 3 sessions/week)
  Display: Hours (4.5 hours/week)

Metric 30: Friday Spot-Check Time (Hours)
  Formula: = (Number of reflections reviewed * 2 minutes) / 60
  Display: Hours (target: 30-45 minutes)

Metric 31: Total 10% Time (Hours)
  Formula: Metric 28 + Metric 29 + Metric 30 + Daily monitoring (30 min/week)
  Display: Hours (target: <= 10 hours/week - 10% of 100-hour cohort commitment)
  Success Metric: <= 10 hours/week (scalable workflow)

Metric 32: Crisis Interventions (Level 4)
  Formula: =COUNTIF('Intervention Tracking'!G:G, "Level 4 - Crisis Intervention")
  Display: Number (target: 0-2 per cohort)
  Trend: If >2, Trevor reviews crisis protocols for improvement
```

### Visual Dashboard Layout (Google Sheets Dashboard Feature)

```
┌─────────────────────────────────────────────────────────────────┐
│ COHORT HEALTH DASHBOARD - Week [X]                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌───────────────┐  ┌───────────────┐  ┌───────────────┐         │
│ │ Total Students│  │ Active        │  │ Zone Shift    │         │
│ │      200      │  │     140       │  │     62%       │         │
│ │               │  │   (70%)       │  │   (124/200)   │         │
│ └───────────────┘  └───────────────┘  └───────────────┘         │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ Zone Distribution (Week 1 → Current)                      │   │
│ │ [Bar Chart: Zone 0, 1, 2, 3, 4 comparison]                │   │
│ └───────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌─────────────────────────────────┐  ┌───────────────────────┐  │
│ │ Anxiety Reduction               │  │ 4 Habits Practice     │  │
│ │ [Line Chart: Week 1→8]          │  │ [Stacked Bar Chart]   │  │
│ │ Average: -2.3 points            │  │ Pause: 75%            │  │
│ └─────────────────────────────────┘  │ Context: 68%          │  │
│                                        │ Iterate: 62%          │  │
│ ┌─────────────────────────────────┐  │ Think First: 58%      │  │
│ │ Engagement Rate                 │  └───────────────────────┘  │
│ │ [Line Chart: Weekly %]          │                            │
│ │ This Week: 72%                  │  ┌───────────────────────┐  │
│ └─────────────────────────────────┘  │ Artifact Completion   │  │
│                                        │ [Pie Chart]           │  │
│ ┌─────────────────────────────────┐  │ Published: 48%        │  │
│ │ Trevor's 10% Time               │  │ In Progress: 32%      │  │
│ │ Interventions: 12               │  │ Not Started: 20%      │  │
│ │ Time: 8.5 hours / 10 max        │  └───────────────────────┘  │
│ └─────────────────────────────────┘                            │
│                                                                  │
│ Last Updated: [Timestamp]  |  Next Review: [Friday]             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Template 5: Cross-Sheet Integration Summary

**Purpose:** Document how all templates reference each other, automate data flow, and maintain consistency.

**Sheet Name:** `Summary` (Dashboard front-page)

**Auto-Aggregated Metrics:**

```yaml
From Student Roster:
  - Total students (COUNTA)
  - Zone distribution (COUNTIF per zone)
  - Cluster balance (COUNTIF per cluster)
  - High-priority students (FILTER crisis flags)
  - Graduation ready (COUNTIFS all 4 habits + artifact)

From Submissions Log:
  - Weekly participation rate (COUNTUNIQUE / total)
  - Average posts per student (COUNTA / COUNTUNIQUE)
  - CIS agent usage rate (COUNTIF / total)
  - Engagement quality distribution (AVERAGE, COUNTIF per rating)

From Intervention Tracking:
  - Total interventions this week (COUNTIF week number)
  - Crisis interventions (COUNTIF Level 4)
  - Average response time (AVERAGE response time column)
  - Intervention effectiveness (COUNTIF per outcome)

Cross-Sheet Formulas:
  - Zone shift success rate ('Student Roster' baseline vs current)
  - Anxiety reduction ('Student Roster' baseline vs current)
  - Engagement status ('Submissions Log' → 'Student Roster' via VLOOKUP)
  - Habit practice counts ('Submissions Log' → 'Student Roster' via COUNTIFS)
```

**Automated Alerts (Conditional Formatting Rules):**

```yaml
Alert 1: Crisis Flag Detected
  Condition: 'Student Roster'!Y:Y = "CRISIS"
  Action: Turn row RED (visual alert only - Trevor monitors during daily 5-minute morning scan per Decision 16)
  Priority: IMMEDIATE

Alert 2: High Anxiety Spike
  Condition: 'Student Roster'!N:N >= 3 (anxiety increased by 3+ points)
  Action: Turn row ORANGE + flag for Level 3 outreach
  Priority: HIGH

Alert 3: Student Stuck 3+ Days
  Condition: 'Submissions Log'!U:U = 0 (no posts this week) AND 'Student Roster'!AE:AE = "Stuck"
  Action: Turn row YELLOW + flag for Level 2 outreach
  Priority: MEDIUM

Alert 4: Cohort Engagement Drop
  Condition: Weekly participation rate < 70%
  Action: Turn metric ORANGE + Trevor considers cohort-wide nudge
  Priority: MEDIUM

Alert 5: Zone Shift Celebration
  Condition: 'Student Roster'!J:J contains "Zone" shift (e.g., "Zone 1→2")
  Action: Turn row GREEN + celebrate in #thinking-showcase (if student consents)
  Priority: POSITIVE (celebration, not intervention)
```

**Data Validation Rules (Cross-Sheet Consistency):**

```yaml
Rule 1: Student ID Uniqueness
  Condition: COUNTIF('Student Roster'!B:B, B2) = 1
  Validation: Each Student ID appears only once in Student Roster
  Error: "Duplicate Student ID detected"

Rule 2: Student ID Reference Validity
  Condition: VLOOKUP(E2, 'Student Roster'!B:B, 1, FALSE) != #N/A
  Validation: Student ID in Submissions Log exists in Student Roster
  Error: "Student ID not found in Student Roster"

Rule 3: Cluster Assignment Validity
  Condition: OR(X2="Cluster 1", X2="Cluster 2", X2="Cluster 3", X2="Cluster 4", X2="Cluster 5")
  Validation: Cluster assignment matches one of 5 clusters
  Error: "Invalid cluster assignment"

Rule 4: Zone Placement Validity
  Condition: OR(H2="Zone 0", H2="Zone 1", H2="Zone 2", H2="Zone 3", H2="Zone 4")
  Validation: Zone placement matches framework (Zone 0-4)
  Error: "Invalid zone placement"

Rule 5: Anxiety Score Validity
  Condition: AND(L2>=1, L2<=10)
  Validation: Anxiety score is 1-10
  Error: "Anxiety must be 1-10"
```

**Data Flow Diagram:**

```
Google Forms (Diagnostic)
    ↓ (Auto-sync)
Student Roster (Master database)
    ↓ (VLOOKUP)
Submissions Log (Track engagement)
    ↓ (COUNTIFS, formulas)
Student Roster (Update engagement status, habit practice)
    ↓ (FILTER)
Intervention Tracking (Log Trevor's 10%)
    ↓ (COUNTIF, AVERAGE)
Progress Dashboard (Visualize cohort health)
    ↓ (SUMMARY function)
Summary Sheet (Front-page metrics)
```

---

## Manual Workflow SOPs (Decision 16)

### SOP 1: Pre-Cohort Setup (Before Week 1)

**Timeline:** 1 week before cohort starts

**Step 1: Create Google Sheets**
```yaml
Action: Trevor creates 4 Google Sheets (Student Roster, Submissions Log, Intervention Tracking, Progress Dashboard)
Time: 30 minutes
Setup:
  - Copy templates from this story (5.5)
  - Name sheets: "K2M Cohort #[X] - [Sheet Name]"
  - Share settings: Trevor only (private)
  - Enable revision history (for audit trail)
```

**Step 2: Connect Google Forms → Student Roster**
```yaml
Action: Link diagnostic form (Story 5.4) to Student Roster sheet
Time: 5 minutes
Setup:
  - Open Google Forms diagnostic
  - Click "Responses" → "Link to Sheets"
  - Select "K2M Cohort #[X] - Student Roster"
  - Test: Submit sample form → Verify data appears in Student Roster
```

**Step 3: Review Diagnostic Data (Trevor's 10%)**
```yaml
Action: Trevor reviews all diagnostic responses
Time: 4-5 hours (200 students × 1 minute basic review + 1-2 hours for high-priority students needing 5-10 min each)
Workflow:
  1. Open Student Roster
  2. Sort by: Crisis Flag (descending), then Anxiety Baseline (descending)
  3. Review high-priority students first (Crisis flag, Zone 0, Anxiety >= 7)
  4. Add notes in Column AA (Trevor Review Notes): e.g., "High anxiety, needs Level 3 outreach"
  5. Flag for intervention: Update Column AB (Outreach Status) → "DM sent" or "Call scheduled"
  6. Document outreach in Intervention Tracking sheet

Time-Saving Tips (if workload exceeds 12 hours/week):
  - Reduce spot-checks from 20→15 reflections (-20 minutes/week)
  - Combine live sessions from 3→2 sessions (-1.5 hours/week)
  - Delegate Level 1 interventions to bot automation
```

**Step 4: Send Level 3 Outreach (High-Priority Students)**
```yaml
Trigger: Crisis Flag = "CRISIS" OR Anxiety >= 8 OR Zone 0 + Anxiety >= 7
Action: Trevor calls student within 24 hours
Time: 15-30 minutes per student (5-10 students max)
Script: "Hey [Name], thanks for filling out the diagnostic. I noticed you're feeling pretty anxious about AI. That's totally normal. Many students feel this way. Want to hop on a quick call? I'd love to hear where you're at."
Follow-Up: If no answer in 48 hours, call parent phone number (safety check)
```

**Step 5: Assign Clusters**
```yaml
Action: Verify cluster assignment formula (Column X)
Time: 10 minutes
Setup:
  - Formula: =IF(OR(UPPER(LEFT(D2,1))<="F"), "Cluster 1", ...)
  - Verify: All 200 students assigned to Cluster 1-4
  - Check: No cluster >25 students (if yes, create Cluster 5)
  - Balance: If clusters unbalanced, Trevor manually adjusts (override formula)
```

**Step 6: Prepare Live Session Schedule**
```yaml
Action: Schedule 1-hour live sessions (3 sessions/week, 8 clusters)
Time: 30 minutes
Setup:
  - Cluster 1 (A-F): Mondays 6 PM EAT
  - Cluster 2 (G-L): Tuesdays 6 PM EAT
  - Cluster 3 (M-R): Wednesdays 6 PM EAT
  - Cluster 4 (S-Z): Thursdays 6 PM EAT
  - If Cluster 5 needed: Fridays 6 PM EAT
  - Add schedule to Discord #announcements
  - Set calendar reminders (Trevor's calendar)
```

### SOP 2: Weekly Monitoring Routine (Weeks 1-8)

**Daily: 5-Minute Morning Scan (Monday-Friday)**
```yaml
Time: 9:00 AM EAT (or Trevor's preferred time)
Duration: 10-15 minutes (realistic time for filter, sort, scan, escalate, schedule)
Workflow:
  1. Open Submissions Log
  2. Filter: Timestamp = YESTERDAY or TODAY
  3. Sort: Emotional Tone (descending) → "Crisis Flag" at top
  4. Scan for: Crisis flags, escalation needs (S = "Yes")
  5. If crisis flag: IMMEDIATE outreach (Level 4 protocol)
  6. If escalation needed: Schedule in calendar for afternoon
  7. If normal: Continue day
```

**Monday: Weekly Setup**
```yaml
Time: 30 minutes
Workflow:
  1. Update Progress Dashboard (refresh all formulas)
  2. Review last week's metrics (engagement, zone shifts, anxiety)
  3. Identify themes: "What worked last week? What didn't?"
  4. Plan this week's focus (e.g., "Zone 0 students need extra support")
  5. Send Monday cohort announcement (Discord #announcements)
  6. Check: Any students stuck from last week? Follow up (Level 2 DMs)
```

**Tuesday: Preparation for Live Sessions**
```yaml
Time: 20 minutes
Workflow:
  1. Review Student Roster: Cluster 1 attendance predictions
  2. Check: Any high-need students in Cluster 1? (crisis flags, Zone 0)
  3. Prepare live session focus (e.g., "Node 0.1: AI is not sci-fi")
  4. Note: Students to call on by name (build belonging)
  5. After session: Log attendance in Student Roster (Column AD)
  6. Follow up: Send DMs to absent high-need students
```

**Wednesday: Live Session Day + Follow-Up**
```yaml
Time: 4 hours (3 sessions × 1 hour + prep + follow-up)
Workflow:
  1. Morning: Final prep for Cluster 2 and 3 live sessions
  2. Afternoon: Host live sessions (6 PM EAT)
  3. Take notes: Student observations, brilliant reflections, concerns
  4. Evening: Log interventions in Intervention Tracking
  5. Follow up: Send DMs to students who shared something vulnerable
```

**Thursday: Mid-Week Check**
```yaml
Time: 20 minutes
Workflow:
  1. Open Submissions Log: Filter Week = THIS WEEK
  2. Check: Engagement status (Active, Lagging, Stuck)
  3. If "Stuck" students (0-1 posts this week): Send Level 2 DMs
  4. Script: "Hey [Name], noticed you haven't posted this week. Everything okay? Week [X] is about [theme]. Just post one thing: 'I tried AI for [task]. It [worked/didn't work].' That's it. You got this."
  5. Log interventions in Intervention Tracking
```

**Friday: Spot-Check Day**
```yaml
Time: 45 minutes
Workflow:
  1. Open Submissions Log: Filter Post Type = "Friday Reflection" AND Week = THIS WEEK
  2. Sort: Thinking Depth Indicator (Growth Edge first, then Synthesizing, Self-Aware) OR Cluster
  3. Select 15-20 reflections to review:
     - Priority 1: High-priority students (from Student Roster crisis flags)
     - Priority 2: Random sample from each cluster (ensure representation)
  4. Review each reflection:
     - Read for quality (thinking depth, zone shift, habit practice)
     - Add Thinking Depth Indicator in Submissions Log (Column L)
     - Send feedback DM if exceptional or needs support: "Loved your reflection about [topic]. You're really getting [Habit]. Keep going!"
  5. Log spot-checks in Intervention Tracking (Intervention Type = "Friday Spot-Check")
  6. Update Progress Dashboard metrics
```

**Saturday-Sunday: Crisis Check Only**
```yaml
Time: 5 minutes/day
Workflow:
  1. Open Submissions Log: Filter Timestamp = LAST 24 HOURS
  2. Scan for: Crisis flags (Emotional Tone = "Crisis Flag")
  3. If crisis: IMMEDIATE outreach (Level 4 protocol)
  4. If normal: Enjoy weekend (10% boundary - Trevor needs rest)
```

### SOP 3: Intervention Escalation Protocol (Level 1-4)

**Level 1: Bot Nudge (Automated)**
```yaml
Trigger: Engagement = "Lagging" (2-3 posts/week)
Action: Agent sends automated nudge via Discord DM
Response Time: Immediate (bot)
Script: "Hey [Name], haven't seen you in a few days. Everything okay? Week [X] is about [theme]. Just post one thing in #thinking-lab - no pressure. We're here!"
Follow-Up: If student re-engages → Success. If no response in 3 days → Escalate to Level 2.
Log: Bot logs automatically in Intervention Tracking (Intervention Type = "Level 1 - Bot Nudge")
```

**Level 2: Trevor DM (Personal Check-In)**
```yaml
Trigger: Engagement = "Stuck" (0-1 posts/week) OR Anxiety >= 6 OR No response to Level 1
Action: Trevor sends personal DM via Discord
Response Time: <= 24 hours
Script: "Hey [Name], noticed you haven't posted this week. Everything okay? Week [X] is about [theme]. I'm here if you want to chat - just DM me. Or if you're busy, no worries. Just post when you can."
Follow-Up: If student responds → Success. If no response in 3 days → Escalate to Level 3.
Log: Trevor logs in Intervention Tracking (Intervention Type = "Level 2 - Trevor DM", Trigger = "Stuck 3+ Days")
```

**Level 3: Direct Call (High-Priority Outreach)**
```yaml
Trigger: Crisis Flag = "HIGH ANXIETY" (Anxiety >= 7) OR Zone 0 + Anxiety >= 7 OR No response to Level 2
Action: Trevor calls student via phone
Response Time: <= 24 hours
Script: "Hey [Name], it's Trevor from K2M. I noticed you're feeling pretty anxious about AI. That's totally normal. Many students feel this way. I just wanted to check in - how are you doing?"
Conversation (15-30 minutes):
  - Listen: Let student share concerns
  - Validate: "It makes sense you feel this way"
  - Normalize: "Many Zone 0 students feel exactly this"
  - Support: Offer resources (CIS agents, node examples, peer connections)
  - Belonging: "People like you succeed in this cohort"
Follow-Up: If anxiety reduces → Success (log in Intervention Tracking). If crisis detected → Escalate to Level 4.
Log: Trevor logs in Intervention Tracking (Intervention Type = "Level 3 - Direct Call", Outcome = "Resolved/Improved/Escalated")
```

**Level 4: Crisis Intervention (Emergency Response)**
```yaml
Trigger: Crisis Keyword ("hopeless", "suicide", "self-harm", "depressed", "end it all", "kill myself", "no point", "giving up", "want to die", "can't go on") OR SafetyFilter flag OR High risk detected in Level 3 call OR Emotional Escalation (anxiety increase >=3 + crisis language)
Action: IMMEDIATE outreach (Trevor calls student within 1 hour)
Response Time: <= 1 hour
Protocol:
  1. IMMEDIATE: Trevor calls student: "Hey [Name], it's Trevor. I'm worried about you. Can you talk?"
  2. ASSESS: Ask directly: "Are you safe right now?" "Do you have thoughts of hurting yourself?"
  3. IF HIGH RISK (suicide plan, self-harm intent):
     - Stay on phone with student
     - Call parent/guardian IMMEDIATELY (if student is minor <18)
     - Provide Kenya crisis resources:
       * Befriending Kenya: +254 722 178 177
       * Mental Health Kenya: +254 733 111 000
       * Youth Crisis Hotline: +254 1199
       * Emergency: 999 or 112
     - Schedule follow-up: Daily check-ins for 1 week
  4. IF MEDIUM RISK (thoughts but no plan):
     - Listen and validate
     - Provide crisis resources
     - Schedule check-in within 24 hours
     - Add to high-priority monitoring (weekly check-ins)
  5. DOCUMENT: Add notes in Intervention Tracking (Intervention Type = "Level 4 - Crisis Intervention")
  6. FOLLOW-UP: Daily check-ins for 1 week, then weekly monitoring
Log: Trevor logs in Intervention Tracking with detailed notes (Column O: Trevor Notes)
Parent Contact: Trevor calls parent within 2 hours if student is minor (<18) and high risk
```

### SOP 4: Live Session Preparation & Follow-Up

**Preparation (30 minutes before session)**
```yaml
1. Review Student Roster: Cluster attendance predictions
   - Who usually attends? Who often misses?
   - Any high-need students in this cluster? (crisis flags, Zone 0, high anxiety)
   - Any students to celebrate? (zone shifts, artifact milestones)

2. Prepare session focus (from Weekly Design - Epic 2)
   - Week 1: Node 0.1 - AI is not sci-fi
   - Week 2: Node 1.1 - It actually works for MY tasks
   - Week 3: Node 1.4 - I'm starting to rely on it
   - Week 4: Node 2.1 - Context changes everything
   - Week 5: Node 2.4 - We're getting closer together
   - Week 6: Node 3.1 - First draft is raw material
   - Week 7: Node 3.4 - I made this
   - Week 8: Artifact showcase + celebration

3. Plan participation (ask questions, not lecture)
   - Prepare 3-5 questions: "What did YOU notice?" "How did that feel?"
   - Note students to call on by name (build belonging)
   - Prepare examples from this week's reflections (anonymize if needed)

4. Setup (10 minutes before)
   - Test microphone, camera
   - Open Discord voice channel
   - Have reflection notes open (reference brilliant insights)
```

**During Session (60 minutes)**
```yaml
1. Welcome (5 minutes)
   - "Hi everyone! Welcome to Week [X] live session for Cluster [X]"
   - "Today we're talking about [theme]"
   - "I've seen some brilliant reflections this week - can't wait to hear your thoughts"

2. Check-In (10 minutes)
   - "How's everyone feeling about AI this week?" (Use 1-word check-in)
   - Celebrate: "I saw [Name]'s reflection about [topic] - that was amazing"
   - Normalize: "Many of you felt [confused/anxious/curious] - that's totally normal"

3. Main Content (30 minutes)
   - Ask questions (DON'T lecture):
     * "What did YOU notice when you tried [this week's prompt]?"
     * "How did it feel when AI [responded/surprised/confused] you?"
     * "Who had a moment where they thought 'Oh, I get it now'?"
   - Call on students by name (especially quiet ones):
     * "[Name], I saw your reflection about [topic]. Can you tell us more?"
   - Celebrate thinking, not outputs:
     * "What I love about that is you're really [pausing/explaining context/iterating/thinking first]"
   - Connect to 4 Habits:
     * "That's Habit [1/2/3/4] in action - [explain how]"

4. Closing (15 minutes)
   - "What's one thing you're taking away from today?"
   - "What's one thing you'll try this week?"
   - "See you in #thinking-lab! Post your reflections by Friday"
   - "DM me if you need anything - I'm here"
```

**Follow-Up (15 minutes after session)**
```yaml
1. Log attendance in Student Roster (Column AD: Live Session Attendance)
   - Attended / No show / Late

2. Note observations (for Friday spot-checks)
   - Brilliant insights to celebrate: "[Name] said [insight] - amazing thinking"
   - Concerns to follow up: "[Name] seemed quiet/down - check in"

3. Send celebration DMs (2-3 students who shared something vulnerable)
   - "Loved what you shared about [topic] in the live session. You're really thinking deeply about this. Keep going!"

4. Send follow-up DMs (absent high-need students)
   - "Missed you at the live session! Everything okay? Here's what we covered: [summary]. DM me if you want to chat."

5. Log in Intervention Tracking (Intervention Type = "Live Session")
```

### SOP 5: Friday Spot-Check Workflow

**Selection (10 minutes)**
```yaml
1. Open Submissions Log
2. Filter: Post Type = "Friday Reflection" AND Week = THIS WEEK
3. Sort: Thinking Depth Indicator (if already rated) OR Cluster
4. Select 15-20 reflections:
   - Priority 1 (5 reflections): High-priority students (crisis flags, Zone 0, high anxiety)
   - Priority 2 (10 reflections): Random sample from each cluster (2-3 per cluster)
   - Priority 3 (3-5 reflections): Growth Edge quality (students ready for next zone)
```

**Review (30-35 minutes)**
```yaml
For each reflection:
1. Read the reflection (click Discord link or read summary in Submissions Log)
2. Assess thinking depth (Using Thinking Depth Indicator):
   - Growth Edge: Student ready for next zone (identity shift emerging)
   - Synthesizing: Connects ideas, shows deep understanding
   - Self-Aware: Recognizes own thinking patterns
   - Experimenting: Tries new approaches, learns by doing
   - Needs Scaffolding: Stuck, needs support
3. Add Thinking Depth Indicator in Submissions Log (Column L)
4. Note: Zone mentioned? (Column M: Yes/No)
5. Note: Habit mentioned? (Column N: ⏸️ Pause, 🎯 Context, 🔄 Iterate, 🧠 Think First, None)
6. Note: Emotional tone? (Column O: Positive, Neutral, Negative, Mixed, Crisis Flag)
```

**Feedback (5-10 minutes)**
```yaml
1. Growth Edge reflections (3-5 students):
   - Send DM: "You're really thinking deeply about this. [Specific insight] was brilliant. I'm seeing you ready for the next zone. Keep going!"
   - Consider: Celebrate in #thinking-showcase (with student consent)

2. Synthesizing/Self-Aware reflections (7-10 students):
   - Send DM: "Great reflection this week! I noticed you're [synthesizing ideas/recognizing your thinking]. Keep going - you're making progress."

3. Experimenting reflections (5-7 students):
   - No DM (manageable 10% workload)
   - Note for next week: Check if engagement deepens

4. Needs Scaffolding (2-3 students):
   - Send DM: "Thanks for posting your reflection. I noticed you're feeling [stuck/confused/frustrated]. That's okay - Week [X] is tough. Want to hop on a quick call? I'd love to help."
   - If DM response: Schedule 15-minute call (Level 3 outreach)
   - If no response: Follow up in 3 days (Level 2 escalation)
```

**Logging (5 minutes)**
```yaml
1. Log all spot-checks in Intervention Tracking:
   - Intervention Type: "Friday Spot-Check"
   - Student ID: [from reflection]
   - Outcome: "Celebrated" / "Supported" / "No outreach needed"
   - Trevor Notes: [Brief summary: "Exceptional reflection on Node 0.1", "Needs support with Habit 2"]

2. Update Progress Dashboard metrics (refresh formulas)

3. Review themes: "What did I notice this week?"
   - Common struggles (e.g., "Many students stuck on Habit 2")
   - Common wins (e.g., "Lots of Zone 1→2 shifts this week")
   - Adjust next week's focus (e.g., "Emphasize Habit 2 in Week 3 node content")
```

---

## Architecture Compliance Checklist

**Guardrail Compliance (Epic 1.1 - ALL 11 Guardrails):**

- [ ] **Guardrail #1 (Identity Protection):** Sheets track zone progression (thinking), not technical skills
- [ ] **Guardrail #2 (No "Should" Language):** No ranking columns ("ahead/behind"), only progress tracking
- [ ] **Guardrail #3 (No Comparison):** Aggregate views show patterns, NEVER student rankings
- [ ] **Guardrail #4 (Non-Prescriptive):** Multiple valid paths honored (Zone 2-3 is valid outcome)
- [ ] **Guardrail #5 (Non-Linear Progression):** Sheets track individual journeys, no "right" pace
- [ ] **Guardrail #6 (Agent Purity):** Clear separation (Agent interventions vs Human interventions tracked separately)
- [ ] **Guardrail #7 (No Zone Skipping):** Sheets track honest zone placement, no advancement without evidence
- [ ] **Guardrail #8 (Discord Safety):** Sheets are CONFIDENTIAL (Trevor only), crisis data restricted
- [ ] **Guardrail #9 (Evidence-Based):** Zone progression based on Cartographer's Manifesto framework
- [ ] **Guardrail #10 (Brand Voice):** Dashboard celebrates thinking growth ("You're shifting"), not judgment
- [ ] **Guardrail #11 (JTBD Examples):** N/A (template structure, not content)

**JTBD Integration (Epic 1.2):**

- [ ] **Emotional Job (Anxiety Reduction):** Sheets track anxiety baseline → current, celebrate reduction
- [ ] **Emotional Job (Belonging):** Sheets track confidence, engagement patterns, belonging cues
- [ ] **Social Job (Parent Proof):** Sheets track parent engagement, weekly updates, artifact completion
- [ ] **Identity Shifts:** Sheets track zone progression (Outsider → Observer → Experimenter → Collaborator → Director)

**Node Architecture (Epic 1.3):**

- [ ] **16 Node Tracking:** Sheets track node engagement (0.1-0.4, 1.1-1.4, 2.1-2.4, 3.1-3.4)
- [ ] **Zone Transitions:** Sheets track zone shifts (0→1, 1→2, 2→3, 3→4)
- [ ] **Identity Shift Tracking:** Sheets capture starting zone (baseline) → current zone (progression)

**4 Habits Branding (Epic 1.4):**

- [ ] **Habit Practice Tracking:** Sheets track all 4 Habits (Pause, Context, Iterate, Think First)
- [ ] **Habit Demonstration:** Sheets track habit practice in reflections (columns AF-AI in Student Roster)
- [ ] **Graduation Proof:** Sheets track readiness (all 4 habits + artifact published)

**Epic 5 Integration (Discord Architecture):**

- [ ] **Story 5.1 (Server Structure):** Cluster assignment, live session attendance, channel unlock tracking
- [ ] **Story 5.2 (#thinking-lab):** CIS agent usage tracking, private process documentation, escalation triggers
- [ ] **Story 5.3 (#thinking-showcase):** Artifact publication tracking, parent notification, celebration metrics
- [ ] **Story 5.4 (Diagnostic):** Student Roster imports diagnostic data (20+ columns from Google Forms)

---

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (December 2024 version)

### Completion Notes List

**Story 5.5 creates comprehensive Google Sheets templates for manual cohort operations tracking, enabling Trevor's 10% workflow (Decision 2, 16) and agent-facilitated model (Decision 1).**

**Key Design Decisions:**

1. ✅ **Student Roster Template:** Master database with 30+ columns (diagnostic data, cluster assignment, crisis flags, intervention priorities, habit practice tracking, artifact status)
2. ✅ **Submissions Log Template:** Track all submissions (daily posts, Friday reflections, CIS interactions) with engagement scoring, streak tracking, quality ratings
3. ✅ **Intervention Tracking Template:** Document Trevor's 10% interventions (Level 1-4 escalations, live sessions, spot-checks, parent outreach) with outcomes and time tracking
4. ✅ **Progress Dashboard Template:** Visual dashboard with 32+ metrics (zone shifts, anxiety reduction, habit practice, engagement, graduation proof, Trevor's time)
5. ✅ **Cross-Sheet Integration:** Complete data flow specification (VLOOKUP formulas, automated alerts, data validation rules, summary views)
6. ✅ **Manual Workflow SOPs:** 5 detailed SOPs (Pre-Cohort Setup, Weekly Monitoring, Intervention Escalation, Live Sessions, Friday Spot-Checks)
7. ✅ **Data Validation Rules:** Drop-down menus, format constraints, formula validation, duplicate detection
8. ✅ **Privacy & Security Design:** Trevor-only access, 6-month data retention, crisis data handling, anonymization for reporting

**Integration with ALL Foundation Documents:**
- ✅ **Epic 1 (Guardrails):** All 11 guardrails enforced through template design (no comparison, privacy, brand voice celebration)
- ✅ **Epic 1 (JTBD):** Emotional job tracking (anxiety + belonging), social job tracking (parent proof + artifact), identity shifts (zone progression)
- ✅ **Epic 1 (Node Architecture):** Zone shift tracking (0→1, 1→2, 2→3, 3→4), 16 node engagement monitoring
- ✅ **Epic 1 (4 Habits):** Habit practice tracking (all 4 habits measured), graduation proof readiness
- ✅ **Epic 5 (Discord Architecture):** Cluster assignment, live session attendance, CIS agent usage, artifact publication, parent engagement

**Trevor's 10% Workflow (Decision 2, 16):**
- **Weekly Time Commitment:** 8-10 hours/week (within 10% target)
  - Daily monitoring: 30 minutes/week
  - Live sessions: 4.5 hours/week (3 sessions × 1 hour + prep)
  - Friday spot-checks: 45 minutes/week
  - Interventions: 2-3 hours/week (10-15 interventions/week)
  - Pre-cohort review: 2-3 hours (one-time)
- **Efficiency Features:**
  - Automated formulas (crisis flags, intervention priorities, engagement status)
  - Dashboard views (high-priority students, zone distribution, cluster balance)
  - Conditional formatting (alerts: RED for crisis, ORANGE for high anxiety, YELLOW for stuck)
  - Cross-sheet integration (data flows automatically between templates)

**Privacy & Safety:**
- All Sheets are CONFIDENTIAL (Trevor only access)
- Crisis data in restricted columns (parent contact, crisis notes)
- 6-month data retention policy (auto-delete after cohort completion)
- Student ID as foreign key (anonymized reporting possible)

**Technical Implementation:**
- Google Sheets (Decision 15: Simplified tech stack)
- 4 templates: Student Roster (master database), Submissions Log (engagement tracking), Intervention Tracking (Trevor's 10%), Progress Dashboard (visual metrics)
- 30+ columns in Student Roster (diagnostic import + ongoing tracking)
- 32+ metrics in Progress Dashboard (zone shifts, anxiety, habits, engagement, graduation, time)
- 5 detailed SOPs (Pre-Cohort, Weekly Monitoring, Escalation, Live Sessions, Spot-Checks)

**Next Steps:**
1. Trevor creates 4 Google Sheets using these templates
2. Connect Google Forms diagnostic → Student Roster (auto-sync)
3. Trevor reviews diagnostic data before Week 1 (2-3 hours)
4. Begin weekly monitoring routine (Monday-Sunday workflow)
5. Story 5.6 will create manual workflow SOPs (builds on these templates)

---

**Story 5.5 Status: ✅ READY FOR DEVELOPMENT**

The Google Sheets templates specification is complete with:
- ✅ Student Roster Template (30+ columns, dashboard views, data validation)
- ✅ Submissions Log Template (engagement tracking, streak tracking, quality ratings)
- ✅ Intervention Tracking Template (Level 1-4 escalations, outcomes, time tracking)
- ✅ Progress Dashboard Template (32+ metrics, visual dashboard, success metrics)
- ✅ Cross-Sheet Integration (VLOOKUP formulas, automated alerts, data validation)
- ✅ Manual Workflow SOPs (5 detailed SOPs with time allocations)
- ✅ Data Validation Rules (drop-down menus, format constraints, formula validation)
- ✅ Privacy & Security Design (Trevor-only access, 6-month retention, crisis handling)
- ✅ All 8 Acceptance Criteria met
- ✅ All Epic 1, 5 foundations integrated

**Trevor can now create the 4 Google Sheets templates and execute the 10% manual workflow efficiently at scale.**
