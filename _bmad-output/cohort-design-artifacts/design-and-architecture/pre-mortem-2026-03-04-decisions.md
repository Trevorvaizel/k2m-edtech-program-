# Pre-Mortem Decisions Log — 2026-03-04
**K2M Cohort 1 — Adversarial Review Session 3**
**Session type:** Party Mode — Pre-mortem on customer journey (Interest → Payment → Onboarding)
**Produced by:** Maya (Design Thinking Coach) + Sally (UX) + John (PM) + Winston (Architect) + Amelia (Dev) + Dr. Quinn (Problem Solver) + Murat (Test Architect) + Mary (Business Analyst)
**North star:** Designing for people who have NEVER used Discord before. Maximum simplicity.
**Status:** CANONICAL — all downstream documents and agents MUST treat this as authoritative

---

## DOCUMENT CONTRACT

This file is the authoritative record of all architectural decisions made during the 2026-03-04 adversarial pre-mortem session. It supersedes any conflicting assumptions in prior sprint entries.

Conflict resolution order:
1. This decisions log (for decisions dated 2026-03-04 onwards)
2. `student-onboarding-and-enrollment-flow.md` (for onboarding/payment behavior)
3. `context-engine-experience-design.md` (for personalization behavior)
4. `discord-implementation-sprint.yaml` (for task sequencing and status)

---

## BLOCKERS RESOLVED (required before any Sprint 0 Addendum build)

### DECISION B-01: on_member_join Match Key
**Problem:** When a student joins the Discord server, the bot's `on_member_join` event has no way to identify WHICH row in Google Sheets to update. The Discord member object contains `discord_id` and `discord_username` but NOT the student's enrollment email. This was a silent build blocker.

**Decision:** Use **unique per-student Discord invite links** as the match key.
- `/api/interest` (landing page) generates a unique invite link per student via Discord API
- Link is stored in Google Sheets **Column R** (`invite_code`)
- When `on_member_join` fires, KIRA calls `link_student_by_invite(invite_code, discord_id, discord_username)`
- Lookup query: `SELECT * FROM students WHERE invite_code = $1`
- On match: write `discord_id` + `discord_username` to Column D, log `student_linked` event
- On no match (student joined via direct link, not enrolled): log `student_unmatched`, assign @Guest, no automation runs

**Bonus:** Unique invite links simultaneously solve referral source tracking (B-01 + Mary's Gap #4). Add `referral_channel` field to invite link metadata (e.g., `pastor_john`, `school_nairobi`, `direct`).

**Implementation target:** Sprint 7, task 7.2. Requires Discord API `create_invite()` per student in `/api/interest`.

---

### DECISION B-02: Stage 1 Redesign — Eliminate `/join`
**Problem:** The previous design had `/join` (a Discord slash command) as Stage 1 of enrollment. A student who has never used Discord before cannot discover slash commands, navigate to the right channel, or know to type this command. This creates immediate drop-off before any automation runs.

**Decision:** Eliminate `/join` as Stage 1. The **landing page form IS Stage 1**.
- Student submits interest form at `k2m-landing/src` (name, email, phone, profession)
- Landing site calls `/api/interest` → appends to Google Sheets → generates unique invite link → sends Brevo Email #1 (Discord invitation)
- Student joins Discord via their unique invite link
- `on_member_join` fires → matches invite link → Column D written → welcome DM sent
- The `/join` Discord command is REMOVED from the bot

**Revised 4-step journey:**
1. **Express Interest** — landing page form → Brevo email with Discord invite
2. **Join Discord** — click invite → `on_member_join` → `/api/enroll` form link in welcome DM
3. **Pay** — enroll form → Brevo Email #2 with M-Pesa token URL → M-Pesa submit
4. **Activate** — Trevor verifies → Apps Script → role upgrade → KIRA onboarding

**Note:** Students now receive the enroll form link via KIRA welcome DM (post-join) and/or Brevo Email #1. The enroll form at `/enroll` is accessed AFTER joining Discord, not before.

**Implementation target:** Sprint 7, task 7.1. Requires updating `/api/interest` + removing `/join` command from main.py.

---

### DECISION B-03: KIRA DM Architecture Fix
**Problem:** The previous design sent "confirmation DMs" from KIRA BEFORE the student joined the Discord server. Discord bots cannot DM users who are not members of their server. This was architecturally impossible.

**Decision:** All pre-Discord-join communications are via **Brevo email only**. KIRA DMs begin ONLY after `on_member_join`.

**Communication split:**
| Stage | Channel |
|-------|---------|
| Interest confirmation | Brevo Email #1 (Discord invite + next steps) |
| Post-Discord-join | KIRA welcome DM (personalized, map-first) |
| Enroll form reminder | KIRA DM (if not enrolled within 48h of joining) |
| Payment instructions | Brevo Email #2 (after /api/enroll, with M-Pesa token URL) |
| Payment received confirmation | KIRA DM + Brevo Email #3 |
| Activation | KIRA DM + Brevo Email #4 |

**Implementation target:** Sprint 7, task 7.3. Requires audit of all KIRA DM trigger points to ensure none fire before `on_member_join`.

---

## HIGH PRIORITY DECISIONS

### DECISION H-01: M-Pesa Token Lifecycle
**Problem:** The 7-day M-Pesa submit token had no warning, no self-service renewal, and no user-facing expiry message. Students who waited 8+ days were silently locked out.

**Decision:**
1. **Day 5 warning DM:** KIRA sends proactive DM 5 days after token generation: "Your enrollment link expires in 2 days. Click here to complete payment: [token URL]"
2. **Token expiry page:** When a student visits an expired token URL, they see: "Your link has expired. In Discord, type `/renew` or message [#help channel] and we'll send you a new link."
3. **`/renew` command:** Trevor (or bot admin) can extend a student's token by 7 days. Writes new token to Column P, new expiry to Column Q, sends fresh Brevo Email #2.
4. **Scheduler check:** Nightly job scans Column Q for tokens expiring within 48h → fires Day-5 DM proactively.

**Implementation target:** Sprint 7, task 7.4.

---

### DECISION H-02: Payment Feedback DMs
**Problem:** After submitting M-Pesa code, the student entered a silent waiting period with no feedback. If Trevor was slow to verify, the student had no idea if their payment was received.

**Decision:**
1. **Immediate DM on payment submission** (after `/api/mpesa-submit` success): KIRA DM: "Got your M-Pesa code! Trevor usually reviews within 24 hours. I'll DM you the moment you're activated. 🎉"
2. **24h silence check:** Scheduler checks for students with Column L = "Pending" for >24h → KIRA DM: "Still reviewing your payment — Trevor will confirm soon. Message [#help] if urgent."
3. **Payment not verified path (new):** If Trevor manually flags a payment as unverifiable (wrong amount, code not found), KIRA sends: "We had trouble verifying your payment. Please DM Trevor at [handle] or send a screenshot to [#help]."

**Implementation target:** Sprint 7, task 7.5. The "not verified" path requires a new Column L value (e.g., "Unverifiable") and a matching KIRA DM trigger.

---

### DECISION H-03: PostgreSQL Migration — PROMOTED, NOW BLOCKING
**Problem:** SQLite is not suitable for concurrent writes during enrollment period. Concurrent form submissions, scheduler jobs, and bot events could cause SQLITE_BUSY errors or corruption. The previous plan deferred full PostgreSQL migration to Sprint 6 (a preparation task). Trevor has decided to migrate now.

**Decision:** **Full PostgreSQL migration is now Sprint 7, task 7.6 — blocking, must complete before cohort launch.**
- Provision PostgreSQL instance (Railway Postgres recommended — already on Railway)
- Migrate all existing schema to PostgreSQL (students, conversations, api_usage, observability_events)
- Add all context-engine columns (Sprint 6.1 requirement) in same migration
- Add `cohort_id` for multi-cohort isolation
- Serialize all writes via connection pool (asyncpg recommended for discord.py async context)
- Remove SQLite dependency from requirements.txt
- Update all database/store.py connection logic
- Run migration against copy of cohort-1.db before switching production

**Previous task 6.6** (PostgreSQL preparation) is now absorbed into Sprint 7, task 7.6 and marked `needs_update`.

**Implementation target:** Sprint 7, task 7.6.

---

### DECISION H-04: Bot Hosting Platform — Confirmed
**Problem:** Bot hosting and uptime were undefined. `on_member_join` events are permanently lost if bot is down during enrollment.

**Decision:**
- **Hosting:** Railway (already deployed per task 5.7) — CONFIRMED
- **Uptime monitoring:** Add Railway health check endpoint (`GET /health → 200 OK`) — KIRA bot already has health_monitor.py; add HTTP server thread for Railway health probe
- **Discord event replay:** Discord does NOT replay missed events. Add a **manual recovery command**: `!recover_member @username` that Trevor can run to manually trigger `on_member_join` logic for a student who joined during downtime
- **Restart strategy:** Railway auto-restarts on crash. Add `RAILWAY_RESTART_POLICY=on_failure` to config.

**Implementation target:** Part of Sprint 7, task 7.8.

---

### DECISION H-05: Post-Activation Profile — Onboarding Stop 0
**Problem:** The enrollment form captures 7 fields. The context engine requires 21+ fields. 14 fields (primary_device, internet_reliability, has_data_bundle, study_hours_per_week, family_obligations, financial_stress_indicator, etc.) cannot be inferred from form text responses.

**Decision:** Add **Onboarding Stop 0** — a brief profile step before the existing 3-stop onboarding sequence.
- Triggered immediately after activation DM
- KIRA asks 4 questions in a conversational DM sequence (not a form):
  1. "How do you usually access the internet? (phone data / home WiFi / school/office WiFi / mixed)"
  2. "How many hours per week do you realistically have for this program? (just a rough guess)"
  3. "On a scale of 1-5, how confident are you with technology right now?"
  4. "Any days/times that are completely off-limits for you? (e.g., Sunday mornings, late evenings)"
- KIRA stores answers to: `primary_device_context`, `study_hours_per_week`, `confidence_level`, `family_obligations_hint`
- Stop 0 can be skipped; KIRA uses defaults if skipped (marks `profile_complete = false`)
- Existing Stops 1-3 unchanged; Stop 0 precedes Stop 1

**Implementation target:** Sprint 7, task 7.7.

---

### DECISION H-06: Dual Source of Truth — Resolution
**Problem:** Google Sheets (Trevor's truth) and SQLite/PostgreSQL (bot's truth) were two independent data stores with no sync. They would diverge rapidly once enrollment begins.

**Decision:** **Google Sheets is the enrollment source of truth. PostgreSQL is the runtime source of truth.**
- **Sheets → PostgreSQL:** `preload_students.py` is the bridge. Runs on activation (triggered by Apps Script). Upserts ALL enrollment fields into PostgreSQL. Re-runnable (idempotent).
- **PostgreSQL → Sheets:** Bot writes observability data back to Sheets via Apps Script webhook: `updateStudentEngagement(discord_id, {onboarding_stop, last_active, frame_sessions_count})` — called nightly by scheduler
- **Conflict rule:** If the same field exists in both, Sheets wins at activation time. After activation, PostgreSQL wins for runtime fields (zone, engagement, etc.).

**Implementation target:** Part of Sprint 7, task 7.6 (PostgreSQL migration includes the sync hooks).

---

## MEDIUM PRIORITY DECISIONS

### DECISION M-01: Payment Not Verified Flow
Add `Unverifiable` as a Column L value. KIRA DM template: "We had trouble matching your payment. Please send a screenshot of your M-Pesa confirmation to #help or DM Trevor directly." (See H-02 above — combined with payment feedback DMs.)

### DECISION M-02: Apps Script Error Surfacing
Apps Script errors should post to `#facilitator-dashboard` via bot webhook AND email Trevor. Add `try/catch` wrapper around all Apps Script functions with `Logger.log(error)` + `UrlFetchApp.fetch(dashboard_webhook, {error: e.message})`.

### DECISION M-03: preload_students.py SOP
Trevor must run `preload_students.py` 48 hours before cohort start AND re-run after every late enrollment. Document in manual SOPs (update task 5.1 notes).

### DECISION M-04: Refund Policy
KES 5,000 refund policy: refunds available up to 7 days before cohort start for verifiable reasons. Contact Trevor directly. No automated refund mechanism for Cohort 1. Add to #welcome channel pinned message and Brevo Email #4.

### DECISION M-05: Enrollment Cap
**Cohort 1 target: 30 students max.** If interest form submissions exceed 30, add Column S (`waitlisted: true/false`). `/api/interest` checks count before appending; if ≥30 confirmed enrollments, return `waitlist: true` and send Brevo waitlist email (new Email #5 template). Trevor reviews waitlist manually.

### DECISION M-06: is_continue_signal() Scope Fix
KIRA's `is_continue_signal()` listener for onboarding progression must be scoped to **KIRA DM thread only** (direct message context = the bot's DM channel with the student). It must NOT listen to general public channel messages. Add channel type check: `if message.channel.type != discord.ChannelType.private: return`.

### DECISION M-07: /onboarding Re-entry Discoverability
For students who time out of onboarding (>7 days inactive), KIRA should:
1. Post a gentle reminder in `#welcome` channel (public, @mention the student): "Looks like you haven't finished setup yet! Type `/onboarding` in a DM to me to continue."
2. OR send a re-entry DM automatically at day 7+1: "Hey [name], your setup is still waiting. Want to continue? Reply 'yes' to pick up where you left off."

### DECISION M-08: Brevo Deliverability Pre-test
Before cohort launch, send test emails from Brevo to: Safaricom email, Airtel Kenya email, Gmail, Yahoo. Check spam folders. If Safaricom/Airtel delivery is problematic, add SMS via Africa's Talking as backup for critical comms (activation, payment confirmation).

---

## ARCHITECTURAL DECISIONS SUMMARY TABLE

| ID | Decision | Severity | Sprint | Status |
|----|----------|----------|--------|--------|
| B-01 | Unique per-student invite links as on_member_join match key | 🔴 CRITICAL | 7.2 | DECIDED |
| B-02 | Remove /join, landing page = Stage 1 | 🔴 CRITICAL | 7.1 | DECIDED |
| B-03 | Pre-join comms = Brevo only | 🔴 CRITICAL | 7.3 | DECIDED |
| H-01 | M-Pesa token day-5 warning + renewal + expiry page | 🟠 HIGH | 7.4 | DECIDED |
| H-02 | Payment feedback DMs (immediate + 24h + not-verified) | 🟠 HIGH | 7.5 | DECIDED |
| H-03 | PostgreSQL migration NOW (promoted, blocking) | 🟠 HIGH | 7.6 | DECIDED |
| H-04 | Bot hosting Railway + health endpoint + recovery command | 🟠 HIGH | 7.8 | DECIDED |
| H-05 | Onboarding Stop 0 (4-question profile DM) | 🟠 HIGH | 7.7 | DECIDED |
| H-06 | Dual source of truth: Sheets=enrollment, PG=runtime | 🟠 HIGH | 7.6 | DECIDED |
| M-01 | Payment not verified KIRA DM | 🟡 MEDIUM | 7.5 | DECIDED |
| M-02 | Apps Script error surfacing | 🟡 MEDIUM | 7.8 | DECIDED |
| M-03 | preload SOP documented | 🟡 MEDIUM | SOPs | DECIDED |
| M-04 | Refund policy in #welcome + Email #4 | 🟡 MEDIUM | 7.1 | DECIDED |
| M-05 | Enrollment cap 30 + waitlist | 🟡 MEDIUM | 7.1 | DECIDED |
| M-06 | is_continue_signal() scoped to DM only | 🟡 MEDIUM | 7.7 | DECIDED |
| M-07 | /onboarding re-entry DM at day 8 | 🟡 MEDIUM | 7.7 | DECIDED |
| M-08 | Brevo deliverability pre-test | 🟡 MEDIUM | Pre-launch | DECIDED |

---

## GAP FIXES — VALIDATION ROUND 2 (2026-03-04)

**Session:** Second adversarial pass — validating that decisions B-01 through M-08 actually fix the original issues.
**Panel:** Winston (Architect) + Amelia (Dev) + Sally (UX) + Murat (Test Architect)
**Finding:** All 20 original decisions are VALID fixes, but 8 NEW gaps emerged from the changes themselves.
**Action:** All 8 gaps fixed below with patches to original decisions.

---

### GAP FIX #1: Invite Diff Concurrency Bug (Decision B-01)

**New problem identified:** If 2 students join within 100ms, invite cache isn't refreshed between joins. Student B's invite goes undetected.

**Patch to Decision B-01:**

Add to `on_member_join` implementation:

```python
@bot.event
async def on_member_join(member):
    guild = member.guild

    # CRITICAL: ALWAYS refresh invites before AND after each join
    # to catch concurrent joins within the same event loop tick
    invites_before = {invite.code: invite.uses for invite in await guild.invites()}

    # ... process join, match invite code ...

    invites_after = {invite.code: invite.uses for invite in await guild.invites()}

    for code, uses_before in invites_before.items():
        uses_after = invites_after.get(code, 0)
        if uses_after > uses_before:
            used_invite_code = code
            break
```

**Why this works:** Discord API increments `invite.uses` atomically. By fetching AFTER the join, we guarantee concurrent joins are detected even if the first fetch was stale.

**Implementation:** Add to Sprint 7 task 7.2 acceptance criteria.

---

### GAP FIX #2: Email #2 Race Condition (Decision B-03)

**New problem identified:** `/api/enroll` checks Column D for `discord_id` while `on_member_join` is still writing it. Race condition = Email #2 doesn't send.

**Patch to Decision B-03:**

Add to `/api/enroll` implementation:

```python
# /api/enroll endpoint
async def send_enrollment_email(email: str, discord_id_placeholder: str):
    for attempt in range(3):
        row = sheets.get_row_by_email(email)
        if row.get('discord_id'):
            # Found it! proceed with Email #2
            break
        if attempt < 2:
            await asyncio.sleep(1 * (2 ** attempt))  # 1s, 2s, 4s backoff
        else:
            # Last attempt failed
            logger.warning(f"discord_id not found after 3 retries for {email}")
            # Queue Email #2 for later delivery (don't fail)
            queue_email_for_later_delivery(email, discord_id_placeholder)
```

**Why this works:** `on_member_join` write takes ~500ms. 3 retries with exponential backoff = 7 seconds total window. If still not found, queue for background retry.

**Implementation:** Add to Sprint 7 task 7.3 acceptance criteria.

---

### GAP FIX #3: Engagement Sync Overwrites Manual Edits (Decision H-06)

**New problem identified:** Trevor manually edits a field in Sheets (e.g., changes zone). Nightly sync overwrites it with PostgreSQL value.

**Patch to Decision H-06:**

Add **Column T: `manual_override_timestamp`** to Google Sheets Student Roster.

**Sync rule update:**

When nightly sync writes back to Sheets:
```python
if sheet_row.get('manual_override_timestamp'):
    if student.last_active > sheet_row['manual_override_timestamp']:
        # Student activity after Trevor's edit → safe to sync
        sheet_row['zone'] = student.zone
    else:
        # Trevor's edit was more recent → preserve it, skip sync
        logger.info(f"Skipping {student.email} due to manual override")
else:
    # No manual override → sync normally
    sheet_row['zone'] = student.zone
```

**Trevor workflow:** If you manually edit a student's zone, ALSO set `manual_override_timestamp = NOW()` in the same row.

**Why this works:** Last-write-wins with a human-override guard. Trevor's edits are respected unless student activity happens after.

**Implementation:** Add to Sprint 7 task 7.6 description.

---

### GAP FIX #4: Token Warning DM Idempotency (Decision H-01)

**New problem identified:** Nightly scheduler runs at 11 PM, sends warning for token expiring in 47h. Runs again at 1 AM, sends DUPLICATE warning for same token (now expiring in 45h, still < 48h).

**Patch to Decision H-01:**

Add **Column U: `token_warning_sent`** (boolean) to Google Sheets Student Roster.

**Scheduler update:**

```python
def token_expiry_warning_check():
    rows = sheets.get_rows_where(
        Column Q < NOW() + timedelta(hours=48),
        Column U == False  # ONLY if warning not sent yet
    )
    for row in rows:
        send_kira_dm(row['discord_id'], "Your enrollment link expires in 2 days...")
        row['token_warning_sent'] = True  # Mark as sent
        sheets.update_row(row)
```

**Reset rule:** When `/renew` generates a new token, also reset `token_warning_sent = False`.

**Why this works:** Boolean guard prevents duplicate warnings. Reset on renew allows warnings for future tokens.

**Implementation:** Add to Sprint 7 task 7.4 description.

---

### GAP FIX #5: Free-Text Parsing Failure (Decision H-05)

**New problem identified:** Stop 0 Question 4 ('Any times off-limits?') accepts free text. Answers like 'Sunday mornings', 'Weekends', 'After 8 PM', 'Shift work varies' cannot be parsed reliably for automation.

**Patch to Decision H-05:**

**Option A (Recommended):** Remove Question 4. Keep Stop 0 to 3 questions.

**Option B:** Make Question 4 structured checkboxes:
```
[Any times that are completely off-limits?]
☐ Sunday mornings
☐ Weekends
☐ Evenings after 6 PM
☐ Mornings before 10 AM
```

**Option C:** Keep free text, but document in Trevor's SOP:

> *"Column W: `family_obligations_hint` — Free-text field for Trevor's manual review only. NOT used by automation. If a student mentions specific constraints, Trevor may adjust their cluster assignment or session timing manually."*

**Recommendation:** Go with Option C (free text + SOP). This preserves conversational tone while setting expectations. Add to Sprint 5.1 SOP documentation.

**Implementation:** Add to Sprint 7 task 7.7 description + SOP notes.

---

### GAP FIX #6: Stop 0 Kills Excitement Moment (Decision H-05)

**New problem identified:** Student just paid KES 5,000, activated, expecting to see channels and meet cohort. Instead, KIRA hits them with 4 questions. Kills the delight moment.

**Patch to Decision H-05:**

**Resequence onboarding stops:**

**OLD order (from H-05):**
1. Activation DM → Stop 0 (profile questions)
2. Stop 1 (KIRA intro, channel tour)
3. Stop 2 (optional public intro)
4. Stop 3 (cluster intro)

**NEW order (excitement-preserving):**
1. Activation DM → Stop 1 (KIRA intro, channel tour, see the community!)
2. Stop 2 (optional public intro — meet peers!)
3. Stop 3 (cluster intro)
4. **Stop 0 (profile questions)** — FRAMED as: *"To make your experience better, I'd like to know a few things. Takes 2 minutes, or skip and answer later."*

**Why this works:** Student gets the dopamine hit ('I'm in! This is real!') BEFORE the cognitive load. Stop 0 becomes optional context-building, not a gate.

**Stop 0 behavioral update:**
- Trigger after Stop 3 (when they've seen everything)
- Add: *"You can skip this and I'll use defaults — no pressure."*
- 48h timeout (not 24h) — more generous since it's now later in the flow

**Implementation:** Update Sprint 7 task 7.7 description.

---

### GAP FIX #7: Multi-DM Bot Confusion (Decision M-06)

**New problem identified:** Student DMs a music bot 'done'. KIRA's `is_continue_signal()` fires, advances onboarding stop. Wrong bot's DM triggered our automation.

**Patch to Decision M-06:**

Add additional guards to `is_continue_signal()`:

```python
def is_continue_signal(message: discord.Message) -> bool:
    # GUARD 1: Must be a DM (private channel)
    if message.channel.type != discord.ChannelType.private:
        return False

    # GUARD 2: Must not be from another bot
    if message.author.bot:
        return False

    # GUARD 3: Must be sent to THIS bot (not another bot's DM thread)
    if message.channel.recipient != bot.user:
        return False

    # Original intent matching
    content = message.content.lower().strip()
    return any(sig in content for sig in CONTINUE_SIGNALS) or len(content) <= 15
```

**Why this works:** Three-layer guard prevents false positives from:
- Public channels (Guard 1)
- Other bots' messages (Guard 2)
- DMs sent to other bots (Guard 3)

**Implementation:** Update Sprint 7 task 7.7 description.

---

### GAP FIX #8: !recover_member Has No Invite Code (Decision H-04)

**New problem identified:** Student joins during bot downtime. Invite was already used. Bot wasn't running to cache which invite. Trevor runs `!recover_member @student`... but invite code is unknown.

**Patch to Decision H-04:**

Add manual fallback lookup to `!recover_member`:

```python
@commands.command(name='recover_member')
async def recover_member(ctx, member: discord.Member):
    # Try invite code match first (normal case)
    student = db.get_student_by_invite_code(get_last_used_invite())

    if not student:
        # Downtime fallback: try email lookup from last 24h
        logger.info(f"Invite match failed for {member.name}. Trying email fallback.")
        student = db.get_student_by_recent_join(hours=24)

    if student:
        link_student(student, member.id, member.name)
        await ctx.send(f"✅ Recovered {member.name} → {student.email}")
    else:
        await ctx.send(f"⚠️ Could not recover {member.name}. Manual enrollment needed.")
```

**Why this works:** Falls back to temporal matching ('who enrolled in the last 24h?') when invite code is unknown. Trevor can then manually confirm the match.

**Manual edge case:** If multiple students enrolled in last 24h, Trevor manually picks the right one. Better than total blocker.

**Implementation:** Update Sprint 7 task 7.8 description.

---

## UPDATED ARCHITECTURAL DECISIONS SUMMARY

| ID | Decision | Severity | Sprint | Status | Gap Fixes Applied |
|----|----------|----------|--------|--------|-------------------|
| B-01 | Unique per-student invite links | 🔴 CRITICAL | 7.2 | DECIDED | +Fix #1 (concurrency cache refresh) |
| B-02 | Remove /join, landing page = Stage 1 | 🔴 CRITICAL | 7.1 | DECIDED | None needed |
| B-03 | Pre-join comms = Brevo only | 🔴 CRITICAL | 7.3 | DECIDED | +Fix #2 (retry with backoff) |
| H-01 | M-Pesa token lifecycle | 🟠 HIGH | 7.4 | DECIDED | +Fix #4 (idempotency guard) |
| H-02 | Payment feedback DMs | 🟠 HIGH | 7.5 | DECIDED | None needed |
| H-03 | PostgreSQL migration | 🟠 HIGH | 7.6 | DECIDED | None needed |
| H-04 | Bot hosting + recovery command | 🟠 HIGH | 7.8 | DECIDED | +Fix #8 (email fallback) |
| H-05 | Onboarding Stop 0 | 🟠 HIGH | 7.7 | DECIDED | +Fix #5 (SOP documentation) +Fix #6 (resequence timing) |
| H-06 | Dual source of truth | 🟠 HIGH | 7.6 | DECIDED | +Fix #3 (manual override guard) |
| M-01 | Payment not verified DM | 🟡 MEDIUM | 7.5 | DECIDED | None needed |
| M-02 | Apps Script error surfacing | 🟡 MEDIUM | 7.8 | DECIDED | None needed |
| M-03 | preload SOP | 🟡 MEDIUM | SOPs | DECIDED | None needed |
| M-04 | Refund policy | 🟡 MEDIUM | 7.1 | DECIDED | None needed |
| M-05 | Enrollment cap 30 | 🟡 MEDIUM | 7.1 | DECIDED | None needed |
| M-06 | is_continue_signal() scope | 🟡 MEDIUM | 7.7 | DECIDED | +Fix #7 (bot recipient checks) |
| M-07 | /onboarding re-entry DM | 🟡 MEDIUM | 7.7 | DECIDED | None needed |
| M-08 | Brevo deliverability | 🟡 MEDIUM | Pre-launch | DECIDED | None needed |

---

## NEW COLUMNS ADDED (Google Sheets Student Roster)

| Column | Field | Type | Added By |
|--------|-------|------|----------|
| R | `invite_code` | VARCHAR(20) | B-01 |
| T | `manual_override_timestamp` | DateTime | Fix #3 |
| U | `token_warning_sent` | Boolean | Fix #4 |

---

*Document updated: 2026-03-04 — Second adversarial pass complete. All 8 gaps patched.*
*Next agents: Load this file + gap fixes before Sprint 7 implementation.*
*Total decisions: 20 original + 8 gap fixes = 28 decisions resolved.*
