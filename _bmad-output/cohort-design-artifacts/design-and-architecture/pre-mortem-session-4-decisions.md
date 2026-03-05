# Pre-Mortem Decisions Log — Session 4
**K2M Cohort 1 — Adversarial Review Session 4**
**Date:** 2026-03-04
**Session type:** Party Mode — Pre-mortem on customer journey (redesigned flow: Interest → Payment → Onboarding)
**Convened by:** Maya (Design Thinking Coach)
**Panel:** Maya · Sally (UX) · Winston (Architect) · Amelia (Dev) · Dr. Quinn (Adversarial/Problem Solver) · John (PM) · Mary (BA) · Murat (Test Architect)
**North Star:** Designing for someone who has NEVER used Discord, NEVER used M-Pesa Paybill, and NEVER enrolled in an online program. Maximum simplicity.
**UX Lenses applied:** 100 Things Every Designer Needs to Know About People (Weinschenk) · Don't Make Me Think (Krug) · Emotional Design (Norman) · Design for How People Think (Whalen) · The Design of Everyday Things (Norman)

**Status:** CANONICAL — all downstream documents and sprint tasks must treat this as authoritative for decisions made in this session.

---

## DOCUMENT CONTRACT

This file records all architectural, UX, and operational decisions made during Session 4. It supplements (does not replace) the Session 3 pre-mortem log (`pre-mortem-2026-03-04-decisions.md`).

Conflict resolution order:
1. This file (Session 4) for decisions N-01 through N-25
2. `pre-mortem-2026-03-04-decisions.md` (Session 3) for decisions B-01 through M-08 + Gap Fixes 1-8
3. `student-onboarding-and-enrollment-flow.md` for onboarding/payment behavior
4. `context-engine-experience-design.md` for personalization behavior
5. `discord-implementation-sprint.yaml` for task sequencing and status

---

## SESSION FRAMING (Maya)

The previous pre-mortem (Session 3) found **structural bugs** — things that architecturally couldn't work. This session found **experience gaps** — things that technically work but will feel broken to a first-time Discord user.

Three themes emerged:

1. **Context switches kill our north star user.** The journey crosses 8 surfaces (landing page → email → Discord install → KIRA DM → browser form → email → M-Pesa → token form) before activation. Every surface switch is a dropout risk.

2. **The waiting periods are undesigned.** We designed the active steps beautifully. We designed the waits terribly. The 24h payment wait and the Stage 1→2 limbo are where real people quietly give up.

3. **The activation moment needs to earn its emotional weight.** She paid KES 5,000, navigated a platform she's never used, answered 10 form questions. The payoff — *"you're in"* — needs to feel worthy of that effort.

---

## CRITICAL DECISIONS (🔴)

### DECISION N-01: Drop-off Recovery Email Sequence — Stage 1→2
**Agent:** Dr. Quinn
**Problem:** A student submits the interest form (Stage 1) and gets Brevo Email #1. If they don't click the Discord invite, they become a ghost lead in Google Sheets. There is NO follow-up. Email open-and-act rates are 10–30%; most students need a nudge.

**Decision:**
- **Email #1.5 (48h nudge):** Sent if Column D is still empty 48 hours after Column G (created_at). Subject: "K2M — Did you get in OK?" Body: "Just checking you got your Discord link. Here it is again: [invite_url]. Need help getting onto Discord? [tutorial_url]"
- **Email #1.75 (5-day final):** Sent if Column D still empty at day 5. Subject: "K2M — Last chance to secure your spot." Body: "We have limited spots for Cohort 1. Your invite link expires in 2 days. [invite_url]"
- **Scheduler job:** `check_stage1_dropoff()` — nightly, checks Column D empty + Column G > 48h. Sends appropriate nudge based on days elapsed.
- **Stop condition:** Once Column D is populated (student joined Discord), no further nudge emails.

**Sprint task:** 7.9 (new)

---

### DECISION N-02: M-Pesa Submit URL in KIRA DM (not email-only)
**Agent:** Sally
**Problem:** After /enroll form submission, the student must: close the browser tab → open email → find Email #2 → click the M-Pesa submit token URL. That's 3 context switches. On mobile, returning to a correct email is cognitively expensive. This is the highest-friction transition in the whole journey.

**Decision:** The KIRA DM sent on enrollment confirmation (Step 2→3 transition) must include the token URL inline:

```
KIRA DM (sent immediately after /api/enroll):
"Got your enrollment form, Grace! ✅

Next step: submit your M-Pesa code.

Pay via M-Pesa:
Paybill: XXXXX | Account: XXXXX | Amount: KES 5,000

After paying, submit your transaction code here:
→ [M-Pesa Submit Link — expires in 7 days]

(You'll also get this link by email as a backup.)

— KIRA"
```

**Implementation note:** The token URL is generated at /api/enroll time. The KIRA DM is triggered by the same event. Both must fire from the same handler.

**Sprint task:** 7.10 (new) — update enrollment DM template

---

### DECISION N-03: Webhook Authentication — Apps Script → Bot
**Agent:** Winston
**Problem:** The Apps Script calls `upgradeDiscordRoleById()` and `preloadStudentToCisBot()` via HTTP webhooks to the Railway-hosted bot. No authentication is specified. An attacker who discovers the Railway URL can POST arbitrary discord_ids and trigger role upgrades.

**Decision:** All Apps Script → bot webhooks must be authenticated using HMAC-SHA256:
- A shared secret (`WEBHOOK_SECRET`) stored as Railway environment variable and in Apps Script script properties (not in code)
- Apps Script signs the JSON payload: `signature = HMAC-SHA256(payload_json, WEBHOOK_SECRET)`
- Adds header: `X-K2M-Signature: sha256={signature}`
- Bot validates signature before executing any action. 401 on mismatch + logs to #facilitator-dashboard.

**Sprint task:** 7.11 (new)

---

### DECISION N-04: Cohort Launch Date as Required Config — Blocking
**Agent:** John
**Problem:** `cohort_launch_target: TBD` in the sprint YAML. Every email template has `{{week1_start_date}}` and `{{first_session_date}}` unpopulated. This blocks end-to-end testing, all email delivery, and the holding experience countdown.

**Decision:** Before any end-to-end pipeline test, Trevor must set:
- `COHORT_1_START_DATE` in Railway environment variables
- `COHORT_1_FIRST_SESSION_DATE` in Railway environment variables
- Update `cohort_launch_target` in sprint YAML

A missing `COHORT_1_START_DATE` at bot startup should throw a fatal configuration error and refuse to start.

**Sprint task:** 7.0 (new — pre-requisite for all Sprint 7 tasks)

---

## HIGH PRIORITY DECISIONS (🟠)

### DECISION N-05: Waiting Room UX During 24h Payment Verification
**Agent:** Dr. Quinn + Maya
**Problem:** After M-Pesa submission, the student waits 24h as @Guest. They see locked channels. Zero engagement, zero progress, zero evidence that anything is happening. Norman's "Emotional Design" visceral level: *"Did I get scammed? Why are all channels locked?"* — trust collapses silently.

**Decision:** Create `#welcome-lounge` channel:
- Visible to `@Guest` (read + write)
- Hidden from public (not a preview of program channels)
- Pinned message: "Your payment is being verified — usually within 24 hours. While you wait, get a taste of what's coming..."
- 3 posts from KIRA: anonymized examples of Week 1 student thinking (previews from the daily prompt library)
- Live student count: "14 students confirmed so far." (updated nightly by scheduler)
- KIRA listens in this channel and answers questions

**Sprint task:** 7.12 (new) + update Discord server setup (sprint 0.x)

---

### DECISION N-06: Stop 0 State Machine Contract
**Agent:** Amelia
**Problem:** The Stop 0 design (4-question profile DM) has no implementation contract. No specification for: timeouts, re-entry, multi-answer handling, question sequence.

**Decision — Stop 0 State Machine:**
- **Sequence:** Sequential. KIRA sends Q1, waits for response, parses, sends Q2, etc.
- **Per-question timeout:** 24 hours. If no response in 24h, KIRA uses default for that question and sends the next one.
- **Defaults:** `primary_device_context = "phone data"`, `study_hours_per_week = 5`, `confidence_level = 3`, `family_obligations_hint = "none specified"`
- **Skip signal:** Student sends "skip" at any point → `profile_complete = false`, all remaining questions skipped, proceed to Stop 1.
- **Multi-answer handling:** If student answers multiple questions in one message ("phone data, 5 hours, 3 out of 5"), use intent matching to extract all answers. Mark `profile_complete = true`. No need to re-ask.
- **DB field:** `onboarding_stop_0_q` (integer 0-4) tracks current question. 0 = not started, 4 = complete.
- **Re-entry:** `/onboarding` command sets `onboarding_stop_0_q` to last unanswered question and resends that question.
- **Placement:** Stop 0 runs AFTER Stops 1–3 (per Gap Fix #6 from Session 3). Framed as optional context-building: *"To personalize your experience, I'd like to know a few things. 2 minutes, or skip anytime."*

**Sprint task:** 7.7 (update existing task description)

---

### DECISION N-07: Invite Diff Concurrency — Async Lock
**Agent:** Winston + Murat
**Problem:** Concurrent `on_member_join` events from near-simultaneous joins cause unreliable invite diff results. (Note: Gap Fix #1 from Session 3 addressed the cache refresh. This decision addresses the missing mutex lock.)

**Decision:** Wrap the entire invite diff + student link logic in an `asyncio.Lock()`:

```python
_invite_diff_lock = asyncio.Lock()

@bot.event
async def on_member_join(member):
    async with _invite_diff_lock:
        invites_before = _invite_cache.copy()  # pre-fetched and cached
        invites_after = {i.code: i.uses for i in await member.guild.invites()}
        # ... diff and match logic ...
        _invite_cache.update(invites_after)
```

**Accepted risk:** At 30 students, the probability of truly simultaneous joins is low (~5%). The `!recover_member` command remains the fallback for edge cases. Document this as a known limitation.

**Sprint task:** 7.2 (update existing task)

---

### DECISION N-08: preload_students.py Failure Visibility
**Agent:** Winston
**Problem:** If Railway is cold when Apps Script calls the preload webhook (30s timeout), the PostgreSQL write fails silently. Student's Discord role is upgraded but KIRA has no context data. Failure invisible to Trevor and student.

**Decision:**
- Apps Script must receive `{success: true}` within 30s or treat as failure
- On failure: Apps Script writes `⚠️ PRELOAD FAILED` to Column M + calls `logToFacilitatorDashboard()`
- Bot `/health` endpoint must respond in < 2s (Railway keeps service warm if health checks hit frequently enough)
- Add Railway always-on configuration (`RAILWAY_RESTART_POLICY=always`)
- Manual recovery: Trevor runs `!preload @discord_user` command to manually trigger preload for a specific student

**Sprint task:** 7.8 (update existing task) + 7.6 (add health endpoint requirement)

---

### DECISION N-09: Progress Indicators Across the Journey
**Agent:** Sally
**UX basis:** Weinschenk #83 — People are motivated by progress. No progress = no momentum = dropout.

**Decision:** Add stage markers to all touch points:

| Touch Point | Progress Marker |
|-------------|----------------|
| Interest form success page | "Step 1 of 4 complete — check your email!" |
| Brevo Email #1 subject | "K2M — Step 1 done! Join Discord (Step 2 of 4)" |
| KIRA welcome DM | "You've completed Step 2 — here's Step 3" |
| /enroll form success | "Step 3 of 4 — check email for payment" |
| Brevo Email #2 subject | "K2M — Step 3: Complete your payment" |
| KIRA post-M-Pesa DM | "Payment received! Step 4: Trevor's review (usually 24h)" |
| Activation DM | "Step 4 complete — you're in!" |

**Sprint task:** 7.10 (include with enrollment DM update) + mark in Brevo template spec

---

### DECISION N-10: Refund Policy Disclosure — Move to Pre-Payment
**Agent:** Dr. Quinn
**UX basis:** Informed consent before financial commitment. Kenya Data Protection Act 2019.
**Problem:** Decision M-04 (Session 3) placed refund policy in #welcome pinned message and Brevo Email #4 (activation). By Email #4, the student has already paid. This is post-hoc disclosure.

**Decision:** Refund policy must appear in Brevo Email #2 (payment instructions), BEFORE the student pays:

```
Add to Email #2 footer:
"Refund policy: Full refund available if requested 7+ days before
cohort start ({{week1_start_date}}). Contact Trevor at [email/WhatsApp].
No refunds after cohort start."
```

Also update /enroll form: add a single line below the payment information section with the same text. Not buried in T&Cs.

**Sprint task:** 7.1 (update existing task — Email #2 template)

---

### DECISION N-11: discord_id URL Param Validation on /enroll
**Agent:** Winston
**Problem:** `/enroll?discord_id=123456789&discord_username=grace_k` — a technically aware user can modify the discord_id param and associate someone else's Discord account with their enrollment.

**Decision:** `/api/enroll` backend must cross-validate:
1. Look up the student row by email (from form field)
2. Check if Column D already has a discord_id written (from `on_member_join`)
3. If Column D has a value AND it doesn't match the discord_id in the URL param: reject with 400 + "Contact support: discord identity mismatch"
4. If Column D is empty (student enrolled via web before joining Discord — edge case): accept the URL param discord_id, write to Column D, flag for Trevor review in Column M

**Sprint task:** 7.3 (update existing task — /api/enroll endpoint)

---

### DECISION N-12: M-Pesa Code Format Validation
**Agent:** Amelia
**Problem:** No input validation on the M-Pesa code field. Students can submit whitespace, partial codes, or full SMS text instead of just the code. This creates "Unverifiable" payment status and support burden.

**Decision:**
- Frontend: trim whitespace, uppercase, validate regex `^[A-Z0-9]{10}$` before submit
- Show the formatted code back to the user before they submit: *"Your code: QGJ8YOAT3T — submit this?"*
- Backend: also validate regex on /api/mpesa-submit. Reject with 400 + helpful message: "M-Pesa codes are 10 characters (letters and numbers only, e.g. QGJ8YOAT3T). Check your M-Pesa SMS."
- Add M-Pesa code format example to the /mpesa-submit page: a screenshot or diagram showing where the code appears in the M-Pesa confirmation SMS.

**Sprint task:** 7.5 (update existing task — mpesa-submit form)

---

### DECISION N-13: Brevo Setup Sprint Tasks — Missing
**Agent:** Amelia
**Problem:** No sprint tasks exist for Brevo account setup, template creation, domain authentication, or deliverability testing. These are launch blockers.

**Decision — New Sprint 7 tasks:**
- **7.13:** Brevo account setup + domain authentication (DKIM/SPF for k2m.edtech). Verify sending domain is authenticated before first email.
- **7.14:** Create all 5 Brevo email templates (Email #1, #1.5, #1.75, #2, #3, #4, #5-waitlist). Use Brevo template variables matching `{{first_name}}`, `{{week1_start_date}}`, etc.
- **7.15:** Brevo deliverability test — send all templates to: Safaricom email, Gmail, Yahoo. Check spam classification. If Safaricom delivery fails, activate Africa's Talking SMS backup for Emails #1, #2, #4 (the critical path).

**Sprint task:** 7.13, 7.14, 7.15 (new)

---

### DECISION N-14: End-to-End Smoke Test — Required Pre-Launch
**Agent:** John + Murat
**Problem:** No sprint task exists for a full pipeline smoke test before cohort launch.

**Decision — Sprint 7 task 7.16:**
Create test accounts and run the complete enrollment pipeline:
1. Submit interest form with test email → verify Email #1 received
2. Join Discord via test invite → verify KIRA DM received + Column D written
3. Submit /enroll form → verify Email #2 received + KIRA DM with token URL received
4. Submit M-Pesa code (test code: `TESTTEST01`) → verify #facilitator-dashboard notification
5. Trevor confirms payment in test row → verify role upgrade + PostgreSQL preload + KIRA activation DM
6. Complete Stops 1-3 → verify onboarding_stop = 4 in DB
7. Complete Stop 0 → verify profile fields written to PostgreSQL

**Acceptance criteria:** All 7 steps succeed in a single run with zero manual interventions beyond Trevor's payment confirmation.

**Sprint task:** 7.16 (new)

---

## MEDIUM PRIORITY DECISIONS (🟡)

### DECISION N-15: Zone Self-Assessment Behavioral Anchors
**Agent:** Sally
**Problem:** Zone 1-4 descriptions use framework language. Students self-assess inaccurately because they can't map abstract zones to their own behavior.

**Decision:** Rewrite zone descriptions in the /enroll form with concrete behavioral anchors:
- **Zone 1:** "I've never used AI tools for my work or studies"
- **Zone 2:** "I've tried AI tools a few times but don't use them regularly"
- **Zone 3:** "I use AI tools most weeks — it's part of how I work"
- **Zone 4:** "AI thinking is automatic for me — I can't imagine working without it"

**Sprint task:** Update /enroll form (task 7.3)

---

### DECISION N-16: /enroll Deep Reflection Fields — KEEP REQUIRED, Improve UX
**Agent:** Sally (original proposal) → **REVISED by Trevor 2026-03-04**
**Problem:** Situation + Goals asked at peak cognitive-load moment. Risk of shallow answers or abandonment.

**Original proposal:** Make optional. **Trevor's call: Keep required.** "We need context, we gotta preload." Context must be in the system at activation for the personalization engine to work on Day 1. Null Situation/Goals = wrong barrier inference = wrong interventions from the start.

**Revised decision — Required fields, improved UX:**
- Both fields stay **required** (cannot submit without them)
- Better placeholders that reduce cognitive friction:
  - Situation: *"2-3 sentences about what you do most days — be specific. e.g. 'I teach Form 3 Chemistry in Nakuru, 35 students, KCSE prep'"*
  - Goals: *"One thing you hope to do differently. e.g. 'Stop just Googling things and actually think through problems first'"*
- Character minimum: 30 chars. If under minimum, gentle nudge: "A bit more detail helps KIRA personalize your experience"
- If profession was pre-filled from Step 1: show a profession-specific example below the textarea as inspiration

**Sprint task:** 7.3 (update /enroll form UX — better placeholders + min validation, keep required)

---

### DECISION N-17: Consent Checkbox Language (Kenya Data Protection Act 2019)
**Agent:** Mary
**Problem:** The consent checkbox on /enroll has no specified text. "I agree to the terms" is insufficient under Kenya's Data Protection Act 2019, which requires specific, informed, freely-given, unambiguous consent.

**Decision — Required consent checkbox text:**

```
"I agree that K2M may store my name, email, profession, and program
responses to personalize my learning experience through KIRA (our AI
thinking partner). My data is used only for this program, not shared
with third parties except Brevo (email delivery). I can request data
deletion by contacting Trevor at [email]. Data is retained for the
program duration plus 12 months."
```

Add a separate opt-in checkbox (unchecked by default) for:
```
"I'm happy to be contacted via WhatsApp for program updates (optional)"
```

**Sprint task:** 7.3 (update /enroll form spec)

---

### DECISION N-18: "Other" Profession — LLM Inference Sprint Task
**Agent:** Mary
**Problem:** Open Question #7 from context-engine-experience-design.md (LLM inference for "other" profession) has no sprint task. 16% of cohort could have mismatched personalization.

**Decision:** Add Sprint 6.5 task:
- On a student's first `/frame` session, if `profession = "other"`, fire a lightweight inference call (~200 tokens, Haiku)
- Prompt: "Based on this student's situation and goals, which of these professions is closest: teacher, entrepreneur, university_student, working_professional? Return only one word."
- Store result as `profession_inferred` in PostgreSQL
- CIS agents use `profession_inferred` for example injection if `profession = "other"`
- Never shown to the student; never overwrites `profession`

**Sprint task:** 6.7 (new, runs after Sprint 6.1 context engine build)

---

### DECISION N-19: Phone Number Field — Optional at Interest Form
**Agent:** Mary
**Problem:** No phone number = no WhatsApp fallback if Brevo email fails. In Kenya, Safaricom email spam filtering is unreliable. If Email #1 goes to spam, the student never joins Discord.

**Decision:** Add optional phone number field to /api/interest form and Google Sheets:
- Label: "WhatsApp number (optional — we'll only use this if email doesn't reach you)"
- Format: `+254XXXXXXXXX`
- Google Sheets Column S: `phone_number`
- If Email #1.5 (48h nudge) fails to deliver (Brevo bounce detected) AND phone number is present: send WhatsApp message via Africa's Talking: "K2M here — did you get our Discord invite? [invite_url]"

**Sprint task:** 7.1 (update /api/interest endpoint + Sheets column map) + 7.15 (Brevo deliverability)

---

### DECISION N-20: Bot Outage Manual Backup SOP
**Agent:** Dr. Quinn
**Problem:** If the bot goes down on Week 1 Day 1 at 9:14 AM (1 minute before first daily prompt), 30 students get nothing. No manual backup protocol exists.

**Decision — Add to manual SOPs (task 5.1 notes):**

"**Bot Outage Protocol:**
1. Check Railway dashboard — if bot is restarting, wait 3 minutes
2. If bot is not recovering: post daily prompt manually in #week-1-wonder (copy from daily-prompt-library.md)
3. DM Trevor's co-facilitator or tech backup to monitor
4. Post in #facilitator-dashboard: 'Bot is down — manually posting prompts until resolved'
5. After bot recovers: check #facilitator-dashboard for any missed events. Run `!recover_member` for any students who joined during downtime."

**Sprint task:** Update task 5.1 SOP documentation

---

### DECISION N-21: is_continue_signal() — Remove 15-char Heuristic
**Agent:** Murat
**Problem:** The `len(content) <= 15` heuristic advances onboarding for any short message: "hi", "what?", "no", "I'm lost", "wait". Students in active onboarding sessions will accidentally advance stops during confusion.

**Decision:** Remove the `len(content) <= 15` rule entirely. Trust only the explicit signal list:

```python
CONTINUE_SIGNALS = {
    'done', 'ready', 'finished', 'ok', 'yes', 'next',
    'read', 'back', 'went', 'seen', "i'm back", 'continue',
    'read it', 'seen it', 'got it', 'understood', 'check'
}

def is_continue_signal(message: discord.Message) -> bool:
    if message.channel.type != discord.ChannelType.private:
        return False
    if message.author.bot:
        return False
    content = message.content.lower().strip()
    return any(sig in content for sig in CONTINUE_SIGNALS)
    # REMOVED: `or len(content) <= 15`
```

Add a fallback: if student sends 3 messages in a row that don't match any signal while in onboarding, KIRA responds: "Still waiting for you — when you've checked the channel, just reply 'done' or 'ok' and I'll take you to the next step."

**Sprint task:** 7.7 (update is_continue_signal() spec)

---

### DECISION N-22: PostgreSQL Connection Pool — Specify Config
**Agent:** Murat
**Problem:** "Connection pool (asyncpg recommended)" is mentioned in Sprint 7.6 but pool size, timeout, and reconnect behavior are unspecified. Under enrollment surge (30 concurrent preloads + KIRA DMs + scheduler), an undersized pool causes connection timeouts.

**Decision — PostgreSQL pool config for production:**
```python
# database/store.py
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=5,       # always-ready connections
    max_size=20,      # peak surge capacity
    command_timeout=30,   # query timeout
    max_inactive_connection_lifetime=300  # recycle idle connections
)
```
Add connection health check on bot startup: if pool creation fails, bot refuses to start and logs error.

**Sprint task:** 7.6 (update PostgreSQL migration task)

---

### DECISION N-23: Backup Payment Verifier
**Agent:** John
**Problem:** Trevor is the sole payment verifier. No named backup if Trevor is traveling, sick, or unavailable. 30 students waiting 24h+ for verification during enrollment surge.

**Decision:**
- Name one backup person with Google Sheets access and M-Pesa verification capability before cohort launch
- Document their name in the manual SOPs (task 5.1)
- Add KIRA escalation: if any payment sits `Pending` > 8h during business hours (8 AM–8 PM EAT), KIRA DMs both Trevor AND the backup verifier

**Sprint task:** Update task 5.1 SOP + update KIRA escalation in scheduler (task 7.5)

---

### DECISION N-24: Discord Mental Model Bridge for First-Timers
**Agent:** Maya
**UX basis:** Weinschenk #52 — People have mental models. First-time Discord users will apply email/WhatsApp mental models and get confused.

**Decision:** Add a "What Discord looks like" visual to two touch points:

1. **Brevo Email #1:** Embed a single annotated screenshot showing:
   - The channel list in the left sidebar (annotated: "Your channels — like folders")
   - The DM icon (annotated: "KIRA will message you here")
   - The server name at top (annotated: "K2M Cohort #1")

2. **KIRA welcome DM:** Include a plain-text map:
```
KIRA: Quick guide to Discord on mobile:
📱 Tap ☰ (top left) → see all channels
💬 Tap the inbox icon → see my messages
⬅️  Swipe right → return to channel list

The most important channel right now: your DMs with me (here!).
I'll guide you through everything step by step.
```

**Sprint task:** 7.13 (include in Brevo template creation) + 7.10 (KIRA DM update)

---

### DECISION N-25: Activation DM Emotional Design — Celebration Moment
**Agent:** Maya
**UX basis:** Norman's "Emotional Design" — the visceral level of design creates the initial emotional response. The activation moment should feel like a door opening, not a system notification.

**Problem:** Current activation DM is an information delivery: here are your channels, here is your cluster, here are your dates. Clinical. No emotional resonance for someone who just navigated through 4 stages.

**Decision — Redesigned activation DM:**

```
KIRA: Grace — you're in. 🎉

Welcome to K2M Cohort 1.

You just did something most people talk about and never do.
You paid for it, figured out Discord, and showed up.
That already says something.

Your channels just unlocked. Explore at your own pace.

📍 When you're ready to start: go to #welcome-and-rules
   → [channel link]

I'll guide you through the rest.

Your cluster: Cluster 2
First live session: {{first_session_date}} at 6 PM EAT
Week 1 begins: {{week1_start_date}}

I'll remind you before each.

— KIRA
```

Key changes from current design:
- Opens with affirmation of what the student DID (not what they GET)
- Shorter. Less information dense.
- One clear action, not a list of 4 things
- Stops 1-3 intro moved to the NEXT message (after they reply "done" or "ready")

**Sprint task:** 7.10 (update KIRA DM templates)

---

## DECISIONS SUMMARY TABLE — SESSION 4

| ID | Decision | Agent | Severity | Sprint Task | Status |
|----|----------|-------|----------|-------------|--------|
| N-01 | Drop-off recovery email sequence (Stage 1→2) | Quinn | 🔴 CRITICAL | 7.9 (new) | DECIDED |
| N-02 | M-Pesa submit URL in KIRA DM (not email-only) | Sally | 🔴 CRITICAL | 7.10 (new) | DECIDED |
| N-03 | Webhook authentication (HMAC-SHA256) | Winston | 🔴 CRITICAL | 7.11 (new) | DECIDED |
| N-04 | Cohort launch date as required config — blocking | John | 🔴 CRITICAL | 7.0 (new) | DECIDED |
| N-05 | #welcome-lounge for @Guest during payment wait | Quinn+Maya | 🟠 HIGH | 7.12 (new) | DECIDED |
| N-06 | Stop 0 state machine contract | Amelia | 🟠 HIGH | 7.7 (update) | DECIDED |
| N-07 | Invite diff async lock | Winston+Murat | 🟠 HIGH | 7.2 (update) | DECIDED |
| N-08 | preload_students.py failure visibility | Winston | 🟠 HIGH | 7.8 (update) | DECIDED |
| N-09 | Progress indicators across the journey | Sally | 🟠 HIGH | 7.10 (update) | DECIDED |
| N-10 | Refund policy disclosure moved to pre-payment | Quinn | 🟠 HIGH | 7.1 (update) | DECIDED |
| N-11 | discord_id URL param validation on /enroll | Winston | 🟠 HIGH | 7.3 (update) | DECIDED |
| N-12 | M-Pesa code format validation | Amelia | 🟠 HIGH | 7.5 (update) | DECIDED |
| N-13 | Brevo setup — missing sprint tasks | Amelia | 🟠 HIGH | 7.13, 7.14, 7.15 (new) | DECIDED |
| N-14 | End-to-end smoke test task | John+Murat | 🟠 HIGH | 7.16 (new) | DECIDED |
| N-15 | Zone self-assessment behavioral anchors | Sally | 🟡 MEDIUM | 7.3 (update) | DECIDED |
| N-16 | /enroll Situation + Goals — keep required, improve UX (REVISED by Trevor) | Sally→Trevor | 🟡 MEDIUM | 7.3 (update) | DECIDED |
| N-17 | Consent checkbox language (Data Protection Act) | Mary | 🟡 MEDIUM | 7.3 (update) | DECIDED |
| N-18 | "Other" profession LLM inference sprint task | Mary | 🟡 MEDIUM | 6.7 (new) | DECIDED |
| N-19 | Phone number field — optional at interest form | Mary | 🟡 MEDIUM | 7.1 (update) | DECIDED |
| N-20 | Bot outage manual backup SOP | Quinn | 🟡 MEDIUM | 5.1 (update) | DECIDED |
| N-21 | is_continue_signal() — remove 15-char heuristic | Murat | 🟡 MEDIUM | 7.7 (update) | DECIDED |
| N-22 | PostgreSQL connection pool config | Murat | 🟡 MEDIUM | 7.6 (update) | DECIDED |
| N-23 | Backup payment verifier named in SOPs | John | 🟡 MEDIUM | 5.1 (update) | DECIDED |
| N-24 | Discord mental model bridge for first-timers | Maya | 🟡 MEDIUM | 7.10, 7.13 | DECIDED |
| N-25 | Activation DM redesign — emotional design | Maya | 🟡 MEDIUM | 7.10 (update) | DECIDED |
| N-26 | @Facilitator Discord role replaces hardcoded "Trevor" throughout bot | Trevor | 🟠 HIGH | 7.8 (update) | DECIDED |

---

## CUMULATIVE DECISIONS ACROSS ALL SESSIONS

| Session | Decisions | New Sprint Tasks Generated |
|---------|-----------|---------------------------|
| Session 3 | B-01 through M-08 (20 decisions) | Sprint 7.1–7.8 |
| Session 3 Gap Fixes | Fix #1 through Fix #8 (8 patches) | Updates to 7.2, 7.3, 7.4, 7.6, 7.7, 7.8 |
| Session 4 | N-01 through N-26 (26 decisions, 5 open Q answers locked) | Sprint 7.0, 7.9–7.16, Sprint 6.7 |
| **Total** | **54 decisions** | **Sprint 7 now has 17 tasks (7.0–7.16) + 1 new Sprint 6 task** |

---

## NEW GOOGLE SHEETS COLUMNS (Session 4)

| Column | Field | Type | Written By | Decision |
|--------|-------|------|-----------|---------|
| S | `phone_number` | VARCHAR(20) | /api/interest | N-19 |

(Note: Column R = `invite_code` from Session 3. Column T = `manual_override_timestamp` from Gap Fix #3. Column U = `token_warning_sent` from Gap Fix #4.)

---

## OPEN QUESTIONS — RESOLVED (2026-03-04)

| # | Question | Trevor's Answer | Status |
|---|----------|----------------|--------|
| N-04 | Cohort 1 start date? | **March 16, 2026** | ✅ LOCKED |
| N-23 | Backup payment verifiers? | **Bruce + Mkunzi** (both facilitators). 3-person verification team: Trevor, Bruce, Mkunzi. All need Sheets access. | ✅ LOCKED |
| N-16 | Situation + Goals optional? | **NO — keep required.** "We need context, we gotta preload." Required fields stay required. UX treatment can improve (better placeholders, hints) but data must be captured at enrollment. | ✅ LOCKED |
| N-19 | Phone number at interest form? | **YES — include it.** Optional field. Used for manual WhatsApp follow-up by facilitators if email fails. | ✅ LOCKED |
| N-13 | Africa's Talking SMS backup? | **DEFERRED to Cohort 2.** Trevor is not familiar with it yet. Phone number still collected (for manual facilitator WhatsApp) but no automated SMS in Cohort 1. | ✅ LOCKED |

**One open item remaining:** First live session date (Trevor's peer cluster call). Is it also March 16 or a different date?

### DECISION UPDATES FROM TREVOR'S ANSWERS

**N-04 UPDATE:** `COHORT_1_START_DATE = 2026-03-16`. All email templates with `{{week1_start_date}}` resolve to "March 16, 2026". Task 7.0 can now be executed.

**N-23 UPDATE — @Facilitator Role (Trevor decision 2026-03-04):**

Instead of hardcoding "Trevor" as the only facilitator, the Discord server uses a **`@Facilitator` role**. Anyone with this role:
- Sees `#facilitator-dashboard` channel
- Receives KIRA escalation DMs (payment queue, bot errors, student alerts)
- Has access to all admin/facilitator-only channels

Initial `@Facilitator` members: Trevor, Bruce, Mkunzi. Adding a new facilitator later = just assign the role, no code changes needed.

All references to "Trevor" in KIRA bot DMs and scheduler logic must be replaced with:
- Channel ping: `@Facilitator` (Discord role mention)
- Or: DM all users with `@Facilitator` role when direct message needed

All three facilitators also need Google Sheets "Student Roster" edit access + M-Pesa verification access (separate from Discord role — Trevor to grant manually).

**N-16 UPDATE:** Situation + Goals remain REQUIRED at /enroll. UX improvements allowed:
- Better placeholder text: "2-3 sentences about what you do day-to-day" (not abstract framework language)
- Character counter showing min/max
- Example below the textarea from the appropriate profession (if pre-filled from Step 1)
Decision N-16 in the table above is revised from "make optional" to "improve UX, keep required."

**N-19 UPDATE:** Phone number field added to /api/interest form. Usage for Cohort 1:
- Facilitators (Trevor/Bruce/Mkunzi) can manually WhatsApp students if email bounces
- No automated SMS (Africa's Talking deferred)
- Field: optional, labeled "WhatsApp number (optional)"

**N-13 UPDATE:** Africa's Talking deferred entirely. Remove from task 7.15 scope. Task 7.15 becomes: "Brevo deliverability test only."

---

*Produced by Party Mode Session — Maya + Sally + Winston + Amelia + Dr. Quinn + John + Mary + Murat*
*Date: 2026-03-04*
*Total new decisions: 25 | Total cumulative: 53*
*Next agents: Load this file + pre-mortem-2026-03-04-decisions.md BEFORE starting any Sprint 7 tasks.*
