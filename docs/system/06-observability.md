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
        │      ├── #facilitator-dashboard          ← ops alerts, cohort health, Level 2 escalations
        │      └── #moderation-logs               ← Level 2-4 escalation posts, safety events
        │
        └──► Trevor's DM                          ← Level 3 (Red) + Level 4 (Crisis) + dashboard-fallback alerts
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
| `CRITICAL` | Fatal or near-fatal failure | "PostgreSQL connectivity degraded — manual recovery required" |

**How to access:**
Railway dashboard → your project → Deployments → View Logs

**Limitations:**
- Logs are unstructured (plain text, not JSON)
- No centralized collection or alerting — you must check manually
- Logs do not persist indefinitely on Railway's free tier

---

## 2 — PostgreSQL: Observability Events

`store.log_observability_event(discord_id, event_type, data_dict)` is called whenever something meaningful happens to a student. These are stored in the database and queryable.

**Common events logged:**

| Event type | Triggered by | Data stored |
|-----------|-------------|-------------|
| `agent_used` | Student successfully runs an agent | agent name, week, state context |
| `milestone_reached` | Habit reaches 3, 7, 14, 21, or 30 uses | habit_id, practiced_count |
| `zone_shift` | Student changes zone | from/to zone |
| `artifact_section_saved` | Artifact section written | section_number, status |
| `artifact_published` | Artifact published to showcase | artifact_id |
| `agent_locked_attempt` | Student tries an agent before unlock | agent, current week, unlock week |
| `student_linked` / `student_unmatched` | Invite-based Discord join reconciliation | invite code, guild ID |
| `profile_parse_flagged` | Stop 0 answers parse poorly | parse flags, raw response summary |
| `barrier_intervention_sent` | Personalized Level 2 intervention DM fires | barrier_type, trigger_reason, engagement_score |
| `onboarding_stop_0_timeout_defaulted` | Optional profile defaults are applied | defaulted flag |
| `onboarding_reentry_dm_sent` | Day-8 onboarding re-entry reminder fires | onboarding stop, inactive days |
| `token_expiry_warning_sent` | Enrollment/payment token is near expiry | token timing metadata |

**Querying events:**

```python
# Via admin command
/show-aggregate-patterns days=7

# Via store method (code)
store.get_student_journey_events(discord_id, limit=50)
```

---

## 3 — Discord: #facilitator-dashboard

**What appears here:**
- Level 2 (Orange) escalation alerts — students stuck 3+ days
- Health monitor alerts for LLM/runtime and database degradation
- Daily cohort health summary (posted by scheduler)
- Aggregate patterns from `/show-aggregate-patterns`

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

This channel captures the moderation-facing audit trail for:
- Timestamp
- Student Discord ID
- Escalation level (2–4)
- Student zone and emotional state
- Action taken by KIRA

**Also logged here:**
- Safety filter violations (comparison language blocked)
- Crisis keyword detections (with redacted context)

**Not logged here:**
- Level 1 inactivity nudges
- Journey inspection consent grant/revoke events
- Ordinary DM-delivery failures

This channel is an important audit trail, but it is not the complete system of record by itself.

---

## 5 — Trevor's DM (Direct Alerts)

KIRA DMs Trevor directly for:

| Trigger | What you receive |
|---------|-----------------|
| **Level 3 (Red)** — 7+ days inactive | Student name, zone, last activity, suggested intervention |
| **Level 4 (Crisis)** — mental health signal | Immediate page — student name only (no message content) |
| **Infrastructure alert fallback** | Direct DM only if `#facilitator-dashboard` cannot be resolved for health-monitor alerts |

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
| No centralized alerting (e.g. PagerDuty, Sentry) | Health alerts still depend on Discord channel delivery and manual monitoring | Watch `#facilitator-dashboard` and Railway logs |
| No dashboard query for "events this week" | No single view of cohort health over time | Run `/show-aggregate-patterns days=7` |
| No Sheets ↔ PostgreSQL sync monitoring | Enrollment drift between Sheets and DB is silent | Manual reconciliation |
| No per-student cost tracking dashboard | Budget alerts fire at threshold, no per-student breakdown | Check Railway env for `DAILY_BUDGET_ALERT` |

---

## 8 — Error Escalation Path (Summary)

When something breaks, here is the order of places to check:

```
1. #facilitator-dashboard  ← Health monitor + cohort-level operational alerts
2. Trevor's DM             ← Level 3/4 pages and dashboard-fallback alerts
3. #moderation-logs        ← Level 2-4 + safety audit trail
4. Railway Logs            ← Python-level errors and stack traces
5. PostgreSQL events       ← /show-aggregate-patterns or direct DB query
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

For runtime LLM failures, the existing notifier wiring calls `health_monitor.notify_llm_runtime_failure(provider, agent, error)` from `main.py`.

```python
# Current pattern
await health_monitor.notify_llm_runtime_failure(
    provider="openai",
    agent="frame",
    error=str(exc),
)
```

That alert path posts to `#facilitator-dashboard` first and only falls back to a Trevor DM if the dashboard channel cannot be found. `FACILITATOR_DISCORD_ID` still needs to be set in production for that fallback path.
