# Super Admin & Ops Guide

> Everything Trevor needs to operate, deploy, and recover the system. Written for the person who holds the keys.

---

## Quick Health Checks

```bash
# Check bot health
python cis-discord-bot/check_discord_health.py

# Run test suite
pytest cis-discord-bot/tests/ -q

# Check Railway deployment logs
# → Railway dashboard → k2m-edtech → Deployments → View Logs
```

---

## Deployments

### Bot (KIRA) — Railway

The bot auto-deploys from the `main` branch on Railway. No manual action needed for normal code pushes.

**To force a redeploy:**
- Push a commit to `main`, or
- Trigger a manual deploy from the Railway dashboard

**Entry point:** `cis-discord-bot/main.py`
**Config file:** `cis-discord-bot/railway.toml`

### Landing Page — Vercel

Auto-deploys from `main`. No manual action needed.

**Built with:** Vite static frontend

### Apps Script (Context Engine) — CRITICAL

> **⚠️ READ THIS BEFORE TOUCHING APPS SCRIPT**

Never use `clasp deploy --deploymentId <id>` to update the Web app. It silently resets the deployment type from "Web app" to "Library" and breaks the webhook.

**Safe workflow for code changes:**
1. `clasp push -f` — push code to HEAD
2. `clasp version "description"` — create a new version
3. **Stop.** Go to the Apps Script UI → Deploy → Manage deployments → Edit → select new version → Save.

The current live URL is stored in `CONTEXT_ENGINE_WEBHOOK_URL` in Railway env vars and in `.env` locally. Do not hardcode it in documentation — it changes whenever a new Web app deployment is created.

If this URL breaks, create a NEW Web app deployment via the UI and update `CONTEXT_ENGINE_WEBHOOK_URL` in Railway. Never try to repair it with `clasp deploy`.

**Web app settings to preserve:**
- Execute as: Me (Trevor's account)
- Who has access: Anyone
- Type: Web app

---

## Environment Variables

Full reference: `cis-discord-bot/.env.template`

### Required at startup

| Variable | Example | Purpose |
|----------|---------|---------|
| `DISCORD_TOKEN` | `MTI3...` | Bot auth |
| `DISCORD_GUILD_ID` | `1234567890` | Your server ID |
| `COHORT_1_START_DATE` | `2026-02-01` | Sets the cohort clock |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL on Railway |
| `AI_PROVIDER` | `openai` | Active LLM provider |
| `OPENAI_API_KEY` | `sk-...` | Required if `AI_PROVIDER=openai` |
| `FACILITATOR_DISCORD_ID` | `987654321` | Your Discord ID (receives crisis DMs) |
| `CONTEXT_ENGINE_WEBHOOK_URL` | `https://script.google.com/...` | Apps Script endpoint |
| `CONTEXT_ENGINE_WEBHOOK_TOKEN` | `secret` | Must match Apps Script Script Property `CONTEXT_WEBHOOK_TOKEN` |
| `WEBHOOK_SECRET` | `secret` | Shared secret for Apps Script internal webhook calls into the bot |

### Enrollment and activation ops

| Variable | Purpose |
|----------|---------|
| `GOOGLE_SHEETS_ID` | Spreadsheet backing enrollment, payment, and recovery flows |
| `GOOGLE_SHEETS_RANGE` | Roster range, usually `Student Roster!A:Z` |
| `GOOGLE_SHEETS_CREDENTIALS_PATH` | Optional credentials path for Sheets sync / recovery scripts |
| `COHORT_1_FIRST_SESSION_DATE` | Used in activation DM messaging |

### Weekly channel mapping

| Variable | Maps to |
|----------|---------|
| `CHANNEL_WEEK_1` | Discord channel ID for week 1 |
| `CHANNEL_WEEK_2_3` | Discord channel ID for weeks 2–3 |
| `CHANNEL_WEEK_4_5` | Discord channel ID for weeks 4–5 |
| `CHANNEL_WEEK_6_7` | Discord channel ID for weeks 6–7 |
| `CHANNEL_WEEK_8` | Discord channel ID for week 8 |
| `CHANNEL_WELCOME_LOUNGE` | Waiting-room channel used before activation completes |

### Role mapping

| Variable | Purpose |
|----------|---------|
| `STUDENT_ROLE_ID` | Role granted after activation / payment verification |
| `GUEST_ROLE_ID` | Role used for newly joined, not-yet-activated students |
| `FACILITATOR_ROLE_ID` | Role expected for Trevor-only operational commands |

### Cost controls

| Variable | Purpose |
|----------|---------|
| `MAX_INTERACTIONS_PER_DAY` | Per-student daily interaction cap |
| `DAILY_BUDGET_ALERT` | Alert threshold (USD) |
| `WEEKLY_BUDGET_CAP` | Hard weekly spending cap (USD) |

### Feature toggles

| Variable | Default | Purpose |
|----------|---------|---------|
| `SYNC_GLOBAL_COMMANDS` | `false` | Set `true` only in prod (avoid dev duplicates) |
| `ENABLE_INTEREST_API` | `true` | Enable `/api/interest`, `/api/enroll`, and payment endpoints |
| `MOUNT_INTEREST_API_ON_PARENT_SERVER` | `true` | Mount interest/enroll routes on the shared parent unsubscribe server |
| `ENABLE_PARENT_UNSUBSCRIBE_SERVER` | `true` | Start the shared aiohttp listener on port 8080 |
| `SHEETS_SYNC_ENABLED` | `false` | Enable nightly PostgreSQL → Sheets engagement sync |
| `CLUSTER_SESSION_SCHEDULE_JSON` | unset | Optional override for the default cluster live-session schedule |

---

## Database

### Production (PostgreSQL on Railway)

Connection: set via `DATABASE_URL` in Railway env vars.

**To run schema migrations:**
```bash
python cis-discord-bot/database/migration.py
```

**To migrate from SQLite to PostgreSQL** (one-time, if needed):
```bash
python cis-discord-bot/migrate_to_pg.py
```

**Connection pool:** min=2, max=10 connections. Handles SSL closure gracefully.

### Local Development (SQLite)

If `DATABASE_URL` is not set (or doesn't start with `postgresql://`), the bot automatically uses SQLite at `cis-discord-bot/cohort-1.db`.

**Emergency fallback:** In PostgreSQL mode, the health monitor does **not** switch production traffic to SQLite. It alerts on degraded PostgreSQL connectivity and expects manual recovery. In-memory SQLite fallback only applies when the process is already running in SQLite mode.

---

## Scheduler

The scheduler runs as a background task inside the bot process. It posts to Discord channels on the following schedule (all times **EAT, Africa/Nairobi**):

| Time | Days | What posts |
|------|------|-----------|
| 9:00 AM | Mon–Thu | NotebookLM node link |
| 9:15 AM | Mon–Thu | Daily prompt |
| 6:00 PM | Wednesday | Peer visibility snapshot |
| 9:00 AM | Friday | Weekly reflection prompt |

**The scheduler reads prompts from:**
`_bmad-output/cohort-design-artifacts/playbook-v2/03-sessions/daily-prompt-library.md`

The scheduler also runs operational jobs beyond content posting:
- `10:00 AM` daily escalation checks
- `5:00 PM Friday` reflection summaries to `#facilitator-dashboard`
- `6-hour cadence at :05` payment feedback DM passes
- `7:00 PM` onboarding timeout and re-entry checks
- `11:00 PM` token expiry warning pass
- `11:10 PM` `#welcome-lounge` status refresh
- `11:20 PM` Stage 1 → 2 drop-off recovery nudges
- `12:10 AM` nightly PostgreSQL → Sheets engagement sync when `SHEETS_SYNC_ENABLED=true`

---

## Discord Server Setup

To spin up a fresh Discord server with the correct structure:
```bash
python setup_discord_server.py
```
This creates: 4 categories, 15 channels, 4 roles.

---

## Join to Activation Lifecycle

The built system has a real waiting-room state between "joined Discord" and "fully activated student":

1. A matched new join receives `@Guest`
2. `#welcome-lounge` stays open for Guest posting while payment / activation is pending
3. Apps Script can call `/api/internal/role-upgrade` to grant `@Student` and remove `@Guest`
4. Apps Script can call `/api/internal/activation-dm` to send final activation details, including first-session and week-1 timing

Operationally, this means a student can be inside Discord but not yet fully activated for the cohort.

---

## Adding a New Student Mid-Cohort

1. Add them to the Discord server (invite or manual add)
2. KIRA auto-detects the new member and starts onboarding in DM
3. Student is created with `current_week = 1` regardless of the cohort's current week
4. They progress by submitting weekly reflections
5. If they need to fast-track to the current cohort week, use `/unlock-week` for each week

---

## Support Recovery Commands

These commands are part of normal ops and should be in the runbook:

### Recover unmatched joins

```bash
/recover-member @member [invite_code]
```

Use this when invite matching failed on `on_member_join`:
- with `invite_code`, KIRA links the exact enrollment row
- without `invite_code`, KIRA tries the most recent unlinked enrolled student within 24 hours

This is the primary recovery path for "student is in Discord but not linked to their enrollment row."

### Renew expired payment links

```bash
/renew email@example.com
```

Use this when a student's payment submission link expired:
- generates a new 7-day token
- writes the new token + expiry back to Sheets
- resets token warning state in PostgreSQL when available
- sends a fresh payment email

---

## Cluster Session Operations

Cluster live-session support is built into the runtime:
- default session cadence is Monday / Wednesday / Friday at 6:00 PM EAT across 8 cluster buckets
- 24-hour announcements are automated
- 1-hour reminders are automated
- temporary voice-channel cleanup is automated after sessions

Trevor-facing cluster commands:

```bash
/switch-cluster @student cluster_id [reason]
/cluster-roster cluster_id
/all-cluster-rosters
/post-session-summary cluster_id session_notes [attendance_count]
```

If the default schedule needs to change, override it with `CLUSTER_SESSION_SCHEDULE_JSON`.

---

## Running a New Cohort

> **⚠️ Multi-cohort limitation:** The current system is built around a single cohort. The env var `COHORT_1_START_DATE` is hardcoded for cohort 1. While the database has a `cohort_id` field designed for future multi-cohort support, there is no `COHORT_2_START_DATE` or routing logic to separate cohorts in the scheduler or router. Running a second cohort simultaneously is not supported without code changes.

**For a sequential cohort (cohort 1 ends, cohort 2 begins):**

1. Ensure cohort 1 students have published or been manually closed out (see [Student Journey — Incomplete Students](./02-student-journey.md#what-happens-to-incomplete-students-week-8-end))
2. Update `COHORT_1_START_DATE` in Railway env vars to the new cohort start date (format: `YYYY-MM-DD`)
3. The scheduler will begin counting weeks from the new date
4. New students joining after this change will be assigned the new start date
5. Old student records remain in the database — they retain their old start date and week values but will no longer receive scheduler content as the global week clock has reset

**What "re-joining" means:** If a cohort 1 student joins the Discord again after being removed, KIRA detects them as a new member and starts onboarding from scratch. Their old record in PostgreSQL remains; a new `INSERT` may conflict depending on whether their Discord ID already exists. This edge case has no documented resolution — investigate before removing and re-adding students.

---

## Google Sheets — Context Engine

The context engine reads from spreadsheet ID: `16tLQbGUF9mI2z2cHxlwmGce6Npui0C5w8e1y46uanH0`

**Available actions (via `doPost`):**
| Action | Purpose |
|--------|---------|
| `getStudentContext` | Pull personalised context for a student |
| `getExamplesByProfession` | Fetch examples relevant to student's profession |
| `getIntervention` | Get recommended intervention by barrier type |
| `seedContextLibraryContent` | Seed example library (idempotent — safe to run multiple times) |
| `ensureContextLibraryTabs` | Create missing sheet tabs |
| `reviewOpsSheetHealth` | Check sheet health |
| `repairOpsSheetHealth` | Repair broken sheets |

---

## Known Gaps to Watch

| Gap | Risk | Priority | How to verify / remediate |
|-----|------|----------|--------------------------|
| **Sheets ↔ PostgreSQL reconciliation is partial** | Enrollment and engagement can still drift across systems even though some sync paths exist | High | Manually cross-reference enrollment rows, invite-linked Discord IDs, and `students` table records before each cohort launch. |
| **Profession inference incomplete** | `profession_inferred` field unpopulated for students who answered "other" at enrollment; context engine examples may not personalise correctly | Medium | Check a sample of student records: `SELECT discord_id, profession, profession_inferred FROM students WHERE profession = 'other'`. Follow up on Task 1.3 implementation. |
| **Context engine HTTP calls unverified** | Personalised examples may not be reaching students even though the webhook URL is configured | High | Test manually: trigger a `/frame` interaction and check Railway logs for outbound HTTP calls to the Apps Script URL. If no calls appear, the integration is not live. |
| **No cohort close-out flow** | Inactive/incomplete students accumulate in DB indefinitely after week 8 | Medium | Manually review and update student records at cohort end. Set `current_state = 'complete'` for students who should be closed out. |
| **DM disabled — no fallback** | Students with DMs off never receive onboarding or agent responses | Medium | Check for members who joined but have no `onboarding_complete` event after 48 hours, then confirm DM warnings in Railway logs and have the student run `/onboarding` after enabling DMs. |
| **Multi-cohort not supported** | Running two concurrent cohorts will break the scheduler and student routing | High (future) | Requires code changes to support `COHORT_2_START_DATE` and cohort-scoped scheduling before attempting. |
