# Observability — What Gets Logged, Where, and How to Find It

> When something goes wrong (or right), where does that information go? This document maps every signal, every log, and every alert in the system — so you always know where to look.

---

## The Observability Stack at a Glance

```
EVENT HAPPENS IN BOT
        │
        ├──► Railway Logs (stdout/stderr)         ← all Python log calls
        │
        ├──► PostgreSQL (observability_events)    ← milestone & journey events
        │
        ├──► Discord Channels                     ← human-readable alerts
        │      ├── #facilitator-dashboard          ← cohort health, Level 2 escalations
        │      └── #moderation-logs               ← all escalations, safety events
        │
        └──► Trevor's DM                          ← Level 3 (Red) + Level 4 (Crisis)
```

---

## 1 — Railway Logs (Operational)

Every log call in the bot goes to Railway's log stream (stdout/stderr). This is your first stop when debugging.

**Log levels used:**

| Level | When used | Example |
|-------|-----------|---------|
| `INFO` | Normal operation | "Student 12345 transitioned to framing state" |
| `WARNING` | Unexpected but non-fatal | "Parse failure for Stop 0 Q1 — using default" |
| `ERROR` | Something failed, bot continues | "LLM provider timeout — retrying (1/3)" |
| `CRITICAL` | Fatal or near-fatal failure | "Database connection lost — activating fallback" |

**How to access:**
Railway dashboard → your project → Deployments → View Logs

**Limitations:**
- Logs are unstructured (plain text, not JSON)
- No centralized collection or alerting — you must check manually
- Logs do not persist indefinitely on Railway's free tier

---

## 2 — PostgreSQL: Observability Events

`store.log_observability_event(discord_id, event_type, data_dict)` is called whenever something meaningful happens to a student. These are stored in the database and queryable.

**Events logged:**

| Event type | Triggered by | Data stored |
|-----------|-------------|-------------|
| `milestone_celebration` | Habit reaches 3, 7, 14, 21, or 30 uses | habit_id, count, message |
| `state_transition` | Student moves between CIS states | old_state, new_state |
| `agent_unlocked` | Week advance unlocks a new agent | agent_name, week |
| `week_advanced` | Student's week incremented | old_week, new_week |
| `onboarding_complete` | All 4 stops completed | stop timestamps |
| `escalation_triggered` | Any escalation level | level, days_inactive, zone |
| `crisis_detected` | Safety filter Level 4 | escalation level, zone, emotional state (message content is NOT stored) |
| `artifact_section_saved` | Artifact section written | section_number, status |
| `artifact_published` | Artifact published to showcase | artifact_id |

**Querying events:**

```python
# Via admin command
/admin patterns days=7

# Via store method (code)
store.get_student_journey_events(discord_id, limit=50)
```

---

## 3 — Discord: #facilitator-dashboard

**What appears here:**
- Level 2 (Orange) escalation alerts — students stuck 3+ days
- Daily cohort health summary (posted by scheduler)
- Aggregate patterns from `/admin patterns`

**Format of an escalation alert:**
```
⚠️ ORANGE ALERT — @student_name
Inactive for 4 days | Zone: zone_2 | Barrier: time
Last seen: Tuesday
Suggested: "Use a 10-minute sprint: one /frame pass on the decision already in front of you."
```

**What does NOT appear here:**
- Individual student rankings or comparisons (Guardrail #3)
- Individual message content
- Any personally identifying information beyond Discord handle

---

## 4 — Discord: #moderation-logs

Every escalation at every level is logged here with:
- Timestamp
- Student Discord ID
- Escalation level (1–4)
- Student zone and emotional state
- Action taken by KIRA

**Also logged here:**
- Safety filter violations (comparison language blocked)
- Crisis keyword detections (with redacted context)
- Consent events (journey inspection granted/revoked)

This channel is the **audit trail**. If anything goes wrong and you need to reconstruct what happened, start here.

---

## 5 — Trevor's DM (Direct Alerts)

KIRA DMs Trevor directly for:

| Trigger | What you receive |
|---------|-----------------|
| **Level 3 (Red)** — 7+ days inactive | Student name, zone, last activity, suggested intervention |
| **Level 4 (Crisis)** — mental health signal | Immediate page — student name only (no message content) |
| **LLM provider failure** | Alert via `_runtime_failure_notifier` (if configured) |
| **Database fallback activated** | Alert that SQLite fallback is running |

> **For crisis DMs:** You are expected to reach out to the student within 1 hour. KIRA has already sent them crisis resources (Kenya hotline 119 + your number).

---

## 6 — Health Monitor

`health_monitor.py` runs as a background task and checks:
- Discord connection status
- Database connectivity
- Scheduler job status
- LLM provider reachability

**Manual health check:**
```bash
python cis-discord-bot/check_discord_health.py
```

This script has retry logic — it will attempt multiple checks before reporting failure.

See also: `cis-discord-bot/DISCORD_HEALTHCHECK.md`

---

## 7 — What Is NOT Observable Right Now (Known Gaps)

| Gap | Impact | Workaround |
|-----|--------|-----------|
| No structured JSON logging | Hard to filter/search Railway logs by student or event type | Use Discord channels + DB queries |
| No centralized alerting (e.g. PagerDuty, Sentry) | LLM/DB failures only surface if you check logs manually | `_runtime_failure_notifier` DMs Trevor |
| No dashboard query for "events this week" | No single view of cohort health over time | Run `/admin patterns days=7` |
| No Sheets ↔ PostgreSQL sync monitoring | Enrollment drift between Sheets and DB is silent | Manual reconciliation |
| No per-student cost tracking dashboard | Budget alerts fire at threshold, no per-student breakdown | Check Railway env for `DAILY_BUDGET_ALERT` |

---

## 8 — Error Escalation Path (Summary)

When something breaks, here is the order of places to check:

```
1. Trevor's DM             ← Did KIRA page you? Start here.
2. #moderation-logs        ← Full audit trail of what KIRA detected
3. #facilitator-dashboard  ← Cohort-level health at a glance
4. Railway Logs            ← Python-level errors and stack traces
5. PostgreSQL events       ← /admin patterns or direct DB query
6. Health check script     ← python cis-discord-bot/check_discord_health.py
```

---

## 9 — Adding New Observability

To log a new meaningful event from anywhere in the bot:

```python
store.log_observability_event(
    discord_id=student.discord_id,
    event_type="your_event_name",
    data={
        "key": "value",
        "another_key": 123
    }
)
```

To send Trevor an immediate DM alert for a critical failure, use the runtime failure notifier. This is wired up in `main.py` during bot startup — it sends a Discord DM to `FACILITATOR_DISCORD_ID`. No extra configuration is needed as long as that env var is set.

```python
# Call from anywhere that has access to the notifier callback
if self._runtime_failure_notifier:
    await self._runtime_failure_notifier(
        f"Critical failure: {description}"
    )
```

If `FACILITATOR_DISCORD_ID` is not set, this call is silently skipped — which means critical failures go unnoticed. **Always set `FACILITATOR_DISCORD_ID` in production.**
