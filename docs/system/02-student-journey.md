# Student Journey — From Enrollment to Graduation

> The complete path a student takes through the K2M EdTech programme — every step, every gate, every invisible force working on their behalf.

---

## Journey at a Glance

```
ENROLL          ONBOARD              8-WEEK PROGRAMME              GRADUATE
   │                │                       │                          │
   ▼                ▼                       ▼                          ▼
Landing      Discord DM           Daily prompts + agents        Artifact
  Page       (4 Stops)            Weekly reflections           published
             + Profile            Habit tracking               in showcase
```

---

## Phase 1 — Enrollment (Landing Page)

The student fills out the enrollment form on the K2M Landing Page (Vercel).

**What is captured:**
- Name, contact, Discord handle
- Parent/guardian consent (for underage students)
- JTBD — "What is the decision or challenge you want to think through?"
- Interest and profession context

**What happens next:**
- Enrollment record written to Google Sheets (source of truth for enrollment)
- Trevor adds the student to the Discord server via a tracked invite link, or manually adds them
- KIRA detects the new member using an **invite snapshot diff** — it records invite use-counts on startup and on each member join, comparing before/after to identify which invite was used
- The cohort clock does NOT start here — it is set globally via `COHORT_1_START_DATE`

> **Operational note:** There is currently no automated bridge between the landing page and Discord. Trevor is the manual handoff. For a cohort of 200+, this is a bottleneck worth planning for.

---

## Phase 2 — Onboarding (Discord DM)

When KIRA detects a new member joining the server, it opens a private DM and guides them through **4 Stops** (plus an optional Stop 0 profile).

### Stop 0 — Optional Profile (2 min)

KIRA asks 4 short questions to personalise the experience. These never block progress — if the student skips or gives an unparseable answer, KIRA uses safe defaults and flags for manual review.

| Question | What KIRA stores | Default if unparsed |
|----------|-----------------|---------------------|
| Internet access type | `primary_device_context` | `"mixed"` |
| Hours per week available | `study_hours_per_week` | `4` |
| Tech confidence (1–5) | `confidence_level` | `3` |
| Family obligations | `family_obligations_hint` | `"none provided"` |

> **Failure mode — DMs disabled:** All onboarding happens over Discord DM. If a student has DMs disabled (a common privacy setting), KIRA cannot reach them and onboarding silently fails. KIRA has no fallback channel for this. See [Facilitator Guide](./03-facilitator-guide.md#student-has-dms-disabled) for how to handle this.

### Stop 1 — Orientation
KIRA opens the student's weekly channel and asks them to reply `continue` when ready.

### Stop 2 — Resources
KIRA points to #resources and asks them to reply `continue`.

### Stop 3 — First Interaction
KIRA invites the student to post their first `/frame` or drop a thought in #thinking-lab, then reply `continue`.

### Stop 4 — Complete
Onboarding is marked complete. The student's record is created in PostgreSQL with:
- `current_week = 1`
- `start_date = COHORT_1_START_DATE` (not their join date)
- `current_state = "none"`
- `zone = "zone_0"`

> **Note on DM safety:** KIRA's `continue` detection has a 3-layer guard — DM only, no bot-authored messages, bot instance ownership check — to prevent accidental triggers.

---

## Phase 3 — The 8-Week Programme

### The Cohort Clock

The week timer is **cohort-based, not individual**. All students share the same clock:

```
Week = (days since COHORT_1_START_DATE ÷ 7) + 1   [capped at week 8]
```

A student who joins mid-cohort always starts at `current_week = 1` in their personal record and must submit reflections to advance — even if the cohort is on week 4.

### Zone Progression

As students advance through weeks, they move through 5 zones:

| Zone | Weeks | What it means |
|------|-------|--------------|
| `zone_0` | Week 1 | Just arrived — orientation mode |
| `zone_1` | Weeks 2–3 | Building the habit of framing |
| `zone_2` | Weeks 4–5 | Exploring and challenging |
| `zone_3` | Weeks 6–7 | Synthesizing and building artifact |
| `zone_4` | Week 8 | Final reflection and showcase |

### Weekly Rhythm

Each week follows a fixed schedule (all times EAT, Africa/Nairobi):

| Time | Day | What happens |
|------|-----|-------------|
| 9:00 AM | Mon–Thu | NotebookLM node link posted |
| 9:15 AM | Mon–Thu | Daily prompt posted in weekly channel |
| 9:00 AM | Friday | Weekly reflection prompt posted |
| 6:00 PM | Wednesday | Peer visibility snapshot |

Week 8 has **no nodes scheduled** — it is reserved for final reflection only.

### Agent Unlock Schedule

Students do not have access to all agents at once. KIRA unlocks them progressively:

```
Week 1  ──────────────────────────────────────────  /frame
Week 4  ──────────────────────────  /diverge  /challenge
Week 6  ──────  /synthesize  /create-artifact  /save  /review  /edit  /publish
```

### Habit Tracking

Every agent interaction builds habits. KIRA tracks practice counts and celebrates milestones:

| Habit | ID | Command | Unlocks at | Milestones celebrated |
|-------|----|---------|-----------|----------------------|
| PAUSE | 1 | `/frame` | Week 1 | 3, 7, 14, 21, 30 uses |
| CONTEXT | 2 | `/frame` | Week 1 | 3, 7, 14, 21, 30 uses |
| ITERATE | 3 | `/diverge` | Week 4 | 3, 7, 14, 21, 30 uses |
| THINK FIRST | 4 | `/challenge` `/synthesize` | Week 4 | 3, 7, 14, 21, 30 uses |

### Week Progression Gate

**A student's week only advances when they submit a Friday reflection.** The scheduler posts the reflection prompt; the student submits it; KIRA unlocks week N+1 for that student individually.

This means two students in the same cohort can be on different weeks if one misses a reflection. See [Facilitator Guide](./03-facilitator-guide.md) for how Trevor manually advances students.

---

## Phase 4 — The Thinking Artifact

Starting at week 6, students build a **6-section Thinking Artifact** — a structured document of their thinking journey through the programme.

| Section | What the student captures |
|---------|--------------------------|
| 1 — Question | The real question they've been exploring |
| 2 — Reframed | How they reframed it after `/frame` |
| 3 — Explored | Perspectives surfaced via `/diverge` |
| 4 — Challenged | Assumptions tested via `/challenge` |
| 5 — Concluded | What they now think and why |
| 6 — Reflection | What changed in how they think |

**Artifact states:** `not_started` → `in_progress` → `completed` → `published`

Only completed artifacts can be published to #thinking-showcase.

---

## Phase 5 — Graduation (Week 8)

- Student publishes their artifact to #thinking-showcase
- KIRA posts a celebration message
- Parent receives a final email summary (via Brevo)
- Student's record marked `complete`

---

## What Happens to Incomplete Students (Week 8 End)

The cohort clock caps at week 8 regardless of where each student is personally. **There is no automated dropout or archival process.** Here is what actually happens:

| Student state at week 8 | What KIRA does | What Trevor should do |
|------------------------|---------------|----------------------|
| Artifact published | Posts celebration, marks complete | Nothing needed |
| Artifact in progress | Keeps state as `in_progress`, no auto-close | Reach out, offer extension or manual publish |
| Behind on weeks (e.g. still on week 4) | Scheduler stops posting week-specific content (week 8 has no nodes) | Decide whether to extend their access or close out |
| Completely inactive | Escalation system continues daily checks indefinitely | Mark inactive, close out manually |

> **There is currently no system-enforced end date or cohort close-out flow.** This is a known gap. Students who don't finish remain in an open state in the database until Trevor intervenes.

---

## What the Student Sees vs. What's Invisible

| Visible to student | Invisible (KIRA doing it) |
|-------------------|--------------------------|
| Daily prompts in weekly channel | Cohort week calculation from start date |
| Agent responses in DM | Habit tracking and milestone detection |
| Reflection prompt on Friday | Escalation checks running daily |
| "Unlock" message for new agent | Safety filter on every message |
| Celebration at habit milestones | Context engine fetching personalised examples |
| Artifact sections building up | Rate limiter controlling costs |
| Peer visibility snapshot Wednesday | Parent email scheduler |