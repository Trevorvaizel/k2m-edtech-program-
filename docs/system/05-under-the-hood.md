# Under the Hood — The Invisible Forces

> The systems that run silently in the background, doing work the student never sees. This document is for anyone who wants to understand what KIRA is actually doing at any moment.

---

## Overview

When a student types `/frame`, they see an AI response. What they don't see:

```
Student types /frame
        │
        ▼
  [1] Crisis Filter    ← Is this a mental health crisis signal? (input check)
        │
        ▼
  [2] Rate Limiter     ← Has this student hit their daily interaction cap?
        │
        ▼
  [3] Router           ← Is this a command? Which agent? Is it unlocked for this week?
        │
        ▼
  [4] Context Engine   ← Fetch personalised examples from Google Sheets
        │
        ▼
  [5] LLM Call         ← OpenAI gpt-4o-mini with student context injected
        │
        ▼
  [6] Output Filter    ← Does KIRA's response contain any comparison language? (output check)
        │
        ▼
  [7] State Machine    ← Update student state, increment habit count
        │
        ▼
  [8] Response → DM    ← Sent privately; never in public channel
        │
        ▼
  [9] Observability    ← Event logged; milestone check; escalation check updated
```

> **Note on pipeline order:** The rate limiter runs *before* the LLM call to avoid incurring API cost for a student who has already hit their cap. If you observe cost overruns per-student, verify this order holds in `router.py` — it is the intended design.

---

## 1 — Safety Filter (Two Separate Checks)

`safety_filter.py` runs two distinct checks at different points in the pipeline. They are not the same operation.

### 1a — Crisis Detection (INPUT check — runs on student's message)

KIRA scans every incoming student message for mental health crisis signals *before* any routing or LLM call.

**Detected signals include:** `want to die`, `suicidal`, `self-harm`, `hopeless`, `worthless`, `end it all`, `kill myself`, `no point`, `nothing matters`

**On detection:**
1. Normal routing stops immediately
2. Student receives crisis resources:
   - Kenya Crisis Hotline: 119 (free, 24/7)
   - Trevor's number: 0116 405604
   - Emergency: 999
3. Trevor receives an urgent DM (Level 4 escalation)

> **DM failure risk:** Crisis resources are delivered via DM. If the student has DMs disabled, they will not receive them. This is a known gap — see [Facilitator Guide](./03-facilitator-guide.md#student-has-dms-disabled).

### 1b — Anti-Comparison (OUTPUT check — runs on KIRA's generated response)

The programme is non-competitive by design. Before any KIRA response is sent, it is checked for comparison language. This runs *after* the LLM call, on the output.

**Blocked language includes (47 terms):**
- `top student`, `best student`, `worst student`
- `most active`, `least active`, `ahead of`, `behind`
- `rank`, `ranking`, `leaderboard`, `1st place`
- `better than`, `worse than`, `faster than`, `slower than`

**Blocked patterns (regex):**
- `student #1`, `top 5`, `ranked #2`
- `student faster than`, `student ahead of`

Any violation raises a `ComparisonViolationError`. The message is blocked and never sent.

---

## 2 — The Router

`router.py` is the dispatcher. It has 3 layers:

```
Layer 1: Is this a slash command or natural language?
          ↓ (command identified)
Layer 2: Is this agent unlocked for the student's current week?
          ↓ (agent allowed)
Layer 3: Route to correct handler
```

**Agent unlock schedule (from code):**

| Week | Available agents |
|------|----------------|
| 1–3 | frame |
| 4–5 | frame, diverge, challenge |
| 6–8 | frame, diverge, challenge, synthesize, create-artifact, save, review, edit, publish |

**Command aliases handled transparently:**
- `framer` → `frame`
- `create_artifact` → `create-artifact`

**Habit recorded per command:**
- `/frame` → Habit 1 (PAUSE) + Habit 2 (CONTEXT)
- `/diverge` → Habit 3 (ITERATE)
- `/challenge` → Habit 4 (THINK FIRST)
- `/synthesize` → Habit 4 (THINK FIRST)

**All agent responses are sent as DMs.** KIRA uses a `PrivateReplyMessage` adapter so interactions stay private even when initiated from a public channel.

---

## 3 — The Context Engine

KIRA connects to a Google Apps Script webhook to personalise agent responses.

**At interaction time, KIRA fetches:**
- Student's context profile (profession, goals, barriers)
- Profession-specific examples (e.g., different examples for a teacher vs. an entrepreneur)
- Recommended intervention if the student is stuck

**Profession categories:**
`teacher` · `entrepreneur` · `university_student` · `working_professional` · `gap_year_student` · `other`

**Webhook:** `CONTEXT_ENGINE_WEBHOOK_URL` (set in env)
**Auth:** Token-based (`CONTEXT_ENGINE_WEBHOOK_TOKEN` must match Apps Script Script Property)
**Timeout:** 2.5 seconds (configurable via `CONTEXT_ENGINE_TIMEOUT_SECONDS`)

> See CLAUDE.md for critical deployment rules around this webhook.

---

## 4 — The State Machine

`state_machine.py` tracks where each student is in their thinking journey. Think of it as a bookmark, not a prison — students can jump freely between states.

**6 states:**

```
none  ──┐
         ├──  framing     ←  entered by /frame
         │
         ├──  exploring   ←  entered by /diverge  ⚠️ state name ≠ command name
         │
         ├──  challenging ←  entered by /challenge
         │
         ├──  synthesizing ← entered by /synthesize
         │
         └──  complete

[students can jump freely between any active state]
```

> **Important:** The state `exploring` is entered by the `/diverge` command — not by a `/explore` command (which does not exist). The state name and command name deliberately differ. If you're debugging state transitions and searching for `"explore"`, look for `/diverge` calls in the code.

State transitions are written to the `students` table (`current_state` column) on every interaction.

**Habit milestones:** When a habit reaches 3, 7, 14, 21, or 30 uses, KIRA sends the student a celebration message. These are logged as observability events.

---

## 5 — The Scheduler

`scheduler.py` runs as a background task. It is the heartbeat of the programme.

**What it manages:**
- Daily prompt delivery (Mon–Thu)
- Friday reflection prompts
- Wednesday peer visibility snapshots
- Daily escalation checks
- Parent email scheduling
- Cluster session facilitation
- Welcome lounge refresh

**Week calculation:**
```python
current_week = (days_since_COHORT_1_START_DATE // 7) + 1  # capped at 8
```

This is calculated in EAT timezone every time the scheduler runs — no drift, no rounding errors.

**Prompts are loaded from:** `_bmad-output/cohort-design-artifacts/playbook-v2/03-sessions/daily-prompt-library.md`

Each prompt contains: week, day, title, emoji, context text, task, habit practice reminder, closing message.

---

## 6 — The Escalation System

`escalation_system.py` runs checks daily. It inspects every student's last post date and determines escalation level.

**Escalation flow:**

```
Days since last post:

  1 day ──────────────────────  Level 1 (Yellow)
                                KIRA sends student a nudge DM

  3+ days ─────────────────────  Level 2 (Orange)
                                Alert posted to #facilitator-dashboard

  7+ days ─────────────────────  Level 3 (Red)
                                KIRA DMs Trevor directly

  Crisis keyword (any time) ───  Level 4 (Crisis)
                                Trevor paged immediately
                                Student sent crisis resources
```

All escalations are logged to #moderation-logs with: timestamp, student zone, emotional state, escalation level.

---

## 7 — The LLM Integration

`llm_integration.py` abstracts all AI provider calls.

**Active runtime:** OpenAI `gpt-4o-mini`
**Supported alternatives (swap via `AI_PROVIDER` env var):** `anthropic` (Claude Sonnet), `zhipu` (GLM-5)

**Agent tiers:**

| Tier | Agents | Why |
|------|--------|-----|
| Fast | frame, diverge, dashboard_summary, profession_inference | High volume, simpler reasoning |
| Deep | challenge, synthesize, create-artifact | Heavier reasoning required |

**Parameters:** `MAX_TOKENS=1000` · `TEMPERATURE=1.0` · Prompt caching enabled by default

**Retry logic:** Up to 3 retries with 0.25s base delay on provider failures.

**System prompts** for all 4 agents are cached at bot startup to avoid repeated file reads.

---

## 8 — The Database Layer

**Dual-database architecture:**

| Environment | Database | Module |
|-------------|----------|--------|
| Production (Railway) | PostgreSQL | `pg_store.py` |
| Local dev / tests | SQLite | `store.py` |
| Emergency fallback | SQLite in-memory | `store.py` (auto-activates) |

**Selection logic (automatic):**
```python
if DATABASE_URL starts with "postgresql://" or "postgres://":
    use PgStudentStateStore
else:
    use StudentStateStore (SQLite)
```

**PostgreSQL compatibility layer:** `pg_store.py` transparently translates SQLite idioms → PostgreSQL:
- `?` → `%s` (placeholders)
- `datetime('now')` → `NOW()`
- `json_extract(col, '$.field')` → `col->>'field'`
- `PRAGMA ...` → silently skipped

**Key tables:**
- `students` — one row per student (identity, week, zone, state, artifact progress)
- `daily_participation` — one row per student per day
- `weekly_reflections` — reflection submissions and unlock status
- `habit_progress` — practice counts per habit per student
- `journey_events` — audit log of all meaningful events

---

## 9 — The Rate Limiter

`rate_limiter.py` enforces per-student cost controls.

**Controlled by env vars:**
- `MAX_INTERACTIONS_PER_DAY` — hard limit per student
- `DAILY_BUDGET_ALERT` — Trevor alert threshold (USD)
- `WEEKLY_BUDGET_CAP` — hard weekly spending cap (USD)

When a student hits their daily limit, KIRA sends them a friendly message and stops processing until midnight EAT.

---

## 10 — Parent Email System

`email_service.py` + `scheduler/parent_email_scheduler.py`

Sends weekly updates to parents/guardians via **Brevo (Sendinblue)** (`BREVO_API_KEY`).

Parents can unsubscribe via a dedicated endpoint (`parent_unsubscribe_server` started at bot launch).

---

## Startup Sequence (What Happens When Bot Starts)

```
1. Load .env
2. Validate required env vars (DISCORD_TOKEN, COHORT_1_START_DATE, DATABASE_URL)
3. Validate LLM provider config
4. Create Discord bot with intents (messages, DMs, members, message_content)
5. Connect to PostgreSQL (or fallback to SQLite)
6. Load and cache agent system prompts
7. on_ready():
   a. Start DailyPromptScheduler (background task)
   b. Start HealthMonitor
   c. Start parent unsubscribe server
   d. Start interest API server
   e. Start internal webhook server (HMAC-authenticated, for Apps Script → bot)
   f. Snapshot guild invite counts (for member join detection)
```