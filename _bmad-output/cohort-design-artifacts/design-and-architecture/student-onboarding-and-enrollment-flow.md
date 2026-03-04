# Student Onboarding and Enrollment Flow
**K2M Cohort 1 â€” Complete Journey from Interest to Active Student**
**Designed by:** Party Mode Session (PM John + UX Designer Sally + Architect Winston + Business Analyst Mary + Problem Solver Dr. Quinn)
**Date:** 2026-03-04
**Status:** DESIGN + EXECUTION SPEC (canonical onboarding/payment contract; implementation tracked in sprint)

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [The 4-Step Enrollment Journey](#the-4-step-enrollment-journey)
3. [Discord Role Progression System](#discord-role-progression-system)
4. [Post-Activation Onboarding Experience](#post-activation-onboarding-experience)
5. [Technical Architecture](#technical-architecture)
6. [Google Sheets Integration](#google-sheets-integration)
7. [Email Templates](#email-templates)
8. [KIRA Bot Automation](#kira-bot-automation)
9. [Build Requirements](#build-requirements)
10. [Automation Roadmap](#automation-roadmap)

---

## Canonical Merge V3 - Amendments (Sessions 3 + 4)

**Session basis:** Session 3 (`B-01` through `M-08`) + Session 4 (`N-01` through `N-26`) merged.
**Primary decision logs:**
- `_bmad-output/cohort-design-artifacts/design-and-architecture/pre-mortem-2026-03-04-decisions.md`
- `_bmad-output/cohort-design-artifacts/design-and-architecture/pre-mortem-session-4-decisions.md`

**Canonical document for merged execution:**
- `_bmad-output/cohort-design-artifacts/design-and-architecture/onboarding-context-canonical-v3.md`

**Canonical V3 conflict resolutions (effective immediately):**
1. Identity linking uses unique per-student Discord invite links (`invite_code`, Column R). The intermediary 6-digit `link_token` path is deprecated.
2. Stop 0 runs after Stops 1-3 (value-first sequence), not before Stop 1.
3. PostgreSQL is runtime storage; SQLite references are legacy.
4. Sprint 7 is the launch-blocking implementation lane.

The following amendments are retained for traceability, but Canonical V3 decisions above take precedence when conflicts appear.

---

### AMENDMENT A-01 â€” Stage 1 Redesigned: `/join` REMOVED (Decision B-02)

**Previous design:** Stage 1 = student types `/join` in Discord. INVALID â€” Discord first-timers cannot discover slash commands.

**New Stage 1:** Landing page form at `k2m-landing` is Stage 1. No Discord knowledge required at entry.

**Revised 4-Step Journey:**
1. **Express Interest** â€” student submits form at landing page (`/join` page) â†’ `/api/interest` â†’ Google Sheets row appended â†’ unique Discord invite link generated (Column R) â†’ **Brevo Email #1** sent (invite link + next steps)
2. **Join Discord** â€” student clicks invite link â†’ `on_member_join` fires â†’ invite code matched â†’ Column D written (discord_id + discord_username) â†’ KIRA welcome DM sent â†’ `/enroll` form link delivered via DM
3. **Pay** â€” student completes `/enroll` form â†’ **Brevo Email #2** sent (M-Pesa token URL) â†’ student submits M-Pesa code â†’ KIRA immediate DM confirmation â†’ payment queue
4. **Activate** -> Trevor verifies payment -> Apps Script `activateStudent()` -> role upgrade -> **Brevo Email #4** -> KIRA activation DM -> Stops 1-3 -> Onboarding Stop 0

The `/join` Discord slash command is **removed from the bot entirely** (Sprint 7 task 7.1).

---

### AMENDMENT A-02 â€” `on_member_join` Match Key: Unique Invite Links (Decision B-01)

**Previous design:** `on_member_join` had no defined mechanism to match a joining Discord member to their enrollment row in Google Sheets. This was a build blocker.

**New mechanism:**
- `/api/interest` generates a **unique, single-use Discord invite link per student** via Discord API (`max_uses=1, unique=True`)
- Invite code stored in **Google Sheets Column R** (`invite_code`)
- `on_member_join` diffs guild invite list before/after join to identify which invite was used
- Query: `SELECT * FROM students WHERE invite_code = used_invite.code`
- On match: write `discord_id` + `discord_username` to Column D, log `student_linked`
- On no match: assign `@Guest` only, log `student_unmatched`, no automation runs

**Bonus:** Invite link metadata carries `referral_channel` (e.g., `?ref=pastor_john`) â€” referral tracking now built-in.

**Google Sheets column map update:** Add Column R = `invite_code` (VARCHAR 20, written by `/api/interest`).

---

### AMENDMENT A-03 â€” KIRA DM Architecture: Pre-join = Brevo Only (Decision B-03)

**Previous design:** KIRA sent "confirmation DMs" before student joined Discord. Architecturally impossible â€” Discord bots cannot DM non-members.

**New rule:** All communications before `on_member_join` fires = **Brevo email only**. KIRA DMs begin ONLY after `on_member_join` successfully matches the student.

**Communication split:**
| Stage | Channel |
|-------|---------|
| Interest confirmation | Brevo Email #1 (Discord invite + next steps) |
| Post-join welcome | KIRA DM (personalized, after `on_member_join`) |
| 48h enroll nudge | KIRA DM (if Column E empty after 48h in Discord) |
| Payment instructions | Brevo Email #2 (after `/api/enroll`, if discord_id present) |
| Payment received | KIRA DM + Brevo Email #3 |
| Activation | KIRA DM + Brevo Email #4 |

**`/api/enroll` gating rule:** Only send Brevo Email #2 if `discord_id` is already populated in Column D. If not yet set, queue Email #2 for delivery when `on_member_join` fires.

---

### AMENDMENT A-04 â€” M-Pesa Token Lifecycle (Decision H-01)

**Previous design:** 7-day token with no warning, no recovery, no user-facing expiry message.

**New lifecycle:**
- **Day 5:** Nightly scheduler sends KIRA DM warning: "Your enrollment link expires in 2 days: [URL]"
- **Expiry page:** Friendly HTML (not error): "Your link has expired. Type `/renew` in a DM to KIRA or visit #help."
- **`/renew` command:** Trevor/admin can extend any student's token by 7 days; sends fresh Brevo Email #2

---

### AMENDMENT A-05 â€” Payment Feedback DMs (Decision H-02)

**Previous design:** After M-Pesa submission, student entered silent waiting period with no feedback.

**New flow:**
1. **Immediate DM** (< 30s after `/api/mpesa-submit`): "Got your M-Pesa code! Trevor reviews within 24 hours. I'll DM you the moment you're activated."
2. **24h silence DM** (if Column L = Pending > 24h): "Still reviewing â€” if urgent, post in #help."
3. **Unverifiable DM** (if Trevor sets Column L = `Unverifiable`): "We had trouble verifying your payment. Send a screenshot to #help or DM Trevor."

**Column L new value:** Add `Unverifiable` to Column L enum (alongside `Pending` and `Confirmed`).

---

### AMENDMENT A-06 â€” Database: PostgreSQL (Decision H-03)

**Previous design:** SQLite. Unsuitable for concurrent writes during enrollment surge.

**New:** PostgreSQL (Railway plugin). Full migration in Sprint 7 task 7.6.
- Replaces ALL SQLite references in codebase
- Google Sheets Column map and Apps Script contract unchanged (Sheets is still enrollment truth)
- `preload_students.py` writes to PostgreSQL, not SQLite

---

### AMENDMENT A-07 — Onboarding Stop 0 (Decision H-05, updated by Session 4)

**Previous design:** Onboarding began at Stop 1 (KIRA intro DM). 14 context fields had no collection mechanism.

**Canonical V3 update:** Keep Stop 0, but run it **after Stops 1-3** (value-first sequencing from Session 4).
- 4 conversational DM questions: internet access type, study hours/week, tech confidence (1-5), off-limits times
- Answers populate: `primary_device_context`, `study_hours_per_week`, `confidence_level`, `family_obligations_hint`
- Skippable (student types "skip") -> `profile_complete = false` -> proceeds to Stop 4+
- 48h timeout -> proceed to Stop 4+ with defaults
- Stop 0 never blocks cohort access

**Canonical onboarding sequence:** Stop 1 (KIRA intro) -> Stop 2 (channels) -> Stop 3 (first /frame) -> Stop 0 (profile DM) -> Stop 4+
---

### AMENDMENT A-08 â€” Enrollment Cap + Refund Policy (Decisions M-04, M-05)

- **Enrollment cap:** 30 students maximum for Cohort 1. `/api/interest` checks confirmed enrollment count. If â‰¥ 30: send Brevo waitlist email (Email #5, new template) and set `waitlisted = true` in Sheets.
- **Refund policy:** Available up to 7 days before cohort start for verifiable reasons. Contact Trevor directly. Add to Brevo Email #4 and #welcome pinned message.

---

### AMENDMENT A-09 — Deprecated in Canonical V3

This intermediary token proposal is retained as historical context only.

**Canonical V3 rule:** keep Amendment A-02 (`invite_code` via unique Discord invite links) as the match key for `on_member_join`.

**Status:** superseded by Session 3 + Session 4 merged decisions and Sprint 7 task 7.2.
---

### AMENDMENT A-10 â€” URL Parameter Cryptographic Signing (Decision D-02)

**Previous design:** Enrollment form URL passed `discord_id` and `discord_username` as plaintext hidden params.

**Security vulnerability (Critical #2):** Student can modify URL params to hijack another student's enrollment.

**New mechanism:** All URL parameters must be cryptographically signed.

**Implementation:**

```python
import hmac
import hashlib

def generate_signed_params(discord_id, discord_username):
    payload = f"{discord_id}|{discord_username}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()[:16]

    return f"{ENROLL_URL}?data={payload}&sig={signature}"

def verify_signed_params(data, signature):
    expected = hmac.new(
        SECRET_KEY.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:16]

    return hmac.compare_digest(expected, signature)
```

**Backend validation:** `/api/enroll` must verify signature before processing. If tampering detected â†’ reject with error.

**Implementation:** See Sprint 0.7 task 0.7.2

---

### AMENDMENT A-11 â€” Transactional State Machine for Activation (Decision D-02)

**Previous design:** Apps Script `activateStudent()` ran all steps atomically with no rollback.

**Problem (Critical #3):** Partial activations leave users in broken state with no recovery path.

**New mechanism:** Explicit activation states with error handling and recovery.

**States:**
- `activation_started` â€” Payment confirmed, beginning process
- `role_upgraded` â€” @Student role assigned
- `db_preloaded` â€” Context written to PostgreSQL
- `email_sent` â€” Activation email delivered
- `dm_sent` â€” KIRA DM delivered
- `fully_activated` â€” All steps complete âœ…
- `activation_partial` â€” One or more steps failed â†’ manual review

**Error handling:**

```javascript
function activateStudent(rowNumber) {
    var state = 'activation_started';
    var errors = [];

    try {
        // Step 1: Role upgrade
        if (!upgradeDiscordRoleById(discordId, 'Student')) {
            throw new Error('Role upgrade failed');
        }
        state = 'role_upgraded';

        // Step 2: Database preload
        var dbResult = preloadStudentToCisBot(row);
        if (!dbResult.success) {
            throw new Error('DB preload failed: ' + dbResult.error);
        }
        state = 'db_preloaded';

        // Step 3: Email
        MailApp.sendEmail({ ... });
        state = 'email_sent';

        // Step 4: DM
        if (!sendKiraActivationDmById(discordId, firstName)) {
            throw new Error('DM failed');
        }
        state = 'fully_activated';

    } catch (err) {
        errors.push(err.message);
        sheet.getRange(row, 13).setValue(`âš ï¸ PARTIAL: ${state} - ${errors.join(' | ')}`);
        logToFacilitatorDashboard(`âš ï¸ PARTIAL: ${firstName} stuck at ${state}`);

        // Do NOT send user email/DM if incomplete
        if (state !== 'db_preloaded') {
            MailApp.sendEmail({
                to: 'trevor@k2m.edtech',
                subject: `âš ï¸ Manual Fix: ${firstName}`,
                body: `Activation failed at ${state}. Errors: ${errors.join(' | ')}`
            });
        }
    }
}
```

**Recovery command:** `/retry-activation @student` (see Amendment A-15)

**Implementation:** See Sprint 0.7 task 0.7.3

---

### AMENDMENT A-12 â€” Error Communications Matrix (Critical #4)

**Previous design:** 5 defined failure modes with ZERO user-facing error messages.

**New requirement:** Every failure mode must have user-facing message + admin notification + recovery action.

**Failure Modes Matrix:**

| Failure Mode | User Sees | Trevor Sees | Recovery |
|--------------|-----------|-------------|----------|
| `student_unmatched` | KIRA DM: *"Having trouble linking your account. Email Trevor with your Discord username"* | Dashboard post with student details | `/link-student` command |
| `activation_partial` | Nothing (broken experience) | Email: *"Manual fix required: [Name] stuck at [state]"* | `/retry-activation` command |
| `payment_unverifiable` | KIRA DM: *"Had trouble verifying payment. Send screenshot to #help"* | Dashboard log | Trevor manually verifies screenshot |
| `token_expired` | Friendly HTML: *"Link expired. Type `/renew` in DM to KIRA"* | Nothing | `/renew-token` command |
| `role_upgrade_failed` | Nothing (silent failure) | Dashboard log + Trevor email | `/force-role` command |

**Implementation requirement:** All error messages must be:
- Warm, not technical
- Actionable (tell them what to do)
- Offer a clear next step

**Implementation:** See Sprint 0.7 task 0.7.4

---

### AMENDMENT A-13 â€” Discord Orientation Mini-Course (High Priority #1)

**Previous design:** Email #1 said "New to Discord? Watch this 2-minute setup video."

**Problem (High #1):** 20-30% of first-time Discord users are confused. They don't understand:
- What a DM is
- How to find DMs
- How to navigate channels
- How to return to DMs from channels

**New Email #1 content:**

```
Subject: Welcome to K2M â€” Your Discord Setup Guide

Hi Grace!

Click here to join our Discord server:
[DISCORD INVITE LINK]

**NEW TO DISCORD?** 90% of your cohort is too.

Watch this 60-second video before you join:
[VIDEO: "Finding KIRA's DM on Discord (for first-time users)"]

Key things to know:
â€¢ KIRA will message you privately (DM)
â€¢ On mobile: Tap the Discord icon (bottom left) â†’ Tap your profile picture
â€¢ On desktop: Click the Discord icon (top left) â†’ Look for "Message Requests"

Need help? WhatsApp us: +254 XXX XXX XXX

See you inside!

â€” Trevor
```

**KIRA Welcome DM â€” Updated:**

```
KIRA: Hey Grace! Welcome to K2M! ðŸ‘‹

I'm KIRA, your thinking partner for this program.

**ðŸ“± ON YOUR PHONE?**
Tap the â˜° icon (top left) to see channels.
To come back here: Tap Discord icon â†’ DMs â†’ KIRA

**ðŸ’» ON DESKTOP?**
Channels are in the left sidebar.
To come back here: Click Discord icon â†’ Click "Direct Messages" â†’ Click KIRA

**FIRST TIME ON DISCORD?**
Most of your cohort is too. You're in good company.

Let's get you enrolled. Click here:
[ENROLLMENT FORM LINK]

â€” KIRA
```

**Video script (60 seconds):** Create screen recording showing:
- Discord app opens
- How to find DMs
- How to click channel links
- How to return to DMs

**Expected impact:** Reduce first-time user drop-off from 20-30% to <10%

**Implementation:** See Sprint 0.7 Patch task 0.7.5

---

### AMENDMENT A-14 â€” Stop 0 Relocated After First /frame (Decision D-03)

**Previous design:** Amendment A-07 placed Stop 0 (profile questions) immediately after activation DM, before Stop 1.

**Problem (High #2):** Asking questions BEFORE value delivery feels like a test, not support. Violates emotional design principles.

**New sequence:** Value-first onboarding

**Old order:** Stop 0 (questions) â†’ Stop 1 (KIRA intro) â†’ Stop 2 (optional intro) â†’ Stop 3 (first /frame)

**New order:** Stop 1 (KIRA intro) â†’ Stop 3 (first /frame) â†’ **VALUE DELIVERED** â†’ Stop 0 (questions, now framed as support) â†’ Stop 2 (optional intro)

**Reframed Stop 0 Script (after first /frame):**

```
KIRA: Grace, that was Habit 1 in action! âœ…

You just did something most teachers never do:
you paused to notice the real question behind the request.

I want to make sure I can give you the best support possible.
Can I ask you 4 quick questions to personalize your experience?

This helps me understand:
â€¢ What tech support you might need
â€¢ When to schedule your cluster sessions
â€¢ How to adapt examples to your context

[Continue with Stop 0 questions]

**Question 1:** How do you usually access the internet?
(phone data / home wifi / office wifi / mixed)

**Question 2:** How many hours per week can you realistically dedicate?
(rough guess is fine)

**Question 3:** On a scale of 1â€“5, how confident are you with tech tools?
(1=nervous, 5=comfortable)

**Question 4:** Any times that are completely off-limits for you?
(e.g. Sunday mornings, late evenings)

[After collection]

Thanks Grace! This helps me:
â€¢ Schedule your cluster sessions at times that work
â€¢ Give you the right tech support
â€¢ Adapt examples to your context

You're all set. Head over to #week-1-wonder for your first daily prompt!
```

**Benefits:**
- âœ… Value-first psychology
- âœ… Reciprocity (KIRA gave value first)
- âœ… Higher completion rates
- âœ… Better data quality

**Expected impact:** Increase Stop 0 completion rate from ~60% to >90%

**Implementation:** See Sprint 0.7 Patch task 0.7.6

---

### AMENDMENT A-15 â€” Explicit Intent Matching for Onboarding (High Priority #4)

**Previous design:** Amendment CE-03 used `is_continue_signal()` which treats ANY short message (â‰¤15 chars) as a completion signal.

**Problem (High #4):** False positives. Student asks *"Where is it?"* (13 chars) â†’ bot advances to next stop instead of providing help.

**New mechanism:** Explicit intent detection with 3 paths.

**Implementation:**

```python
def detect_onboarding_intent(message_content: str) -> str:
    """Returns: 'complete' | 'skip' | 'help' | 'ambiguous'"""
    content = message_content.lower().strip()

    # Explicit completion signals
    if any(word in content for word in ['done', 'ready', 'finished', 'complete', 'next']):
        return 'complete'

    # Explicit skip signals
    if 'skip' in content:
        return 'skip'

    # Explicit help signals
    if any(word in content for word in ['help', 'confused', 'lost', "don't see", 'where', 'how', '?', '???']):
        return 'help'

    # Ambiguous â€” ask for clarification
    return 'ambiguous'

async def handle_onboarding_dm(student, message_content: str):
    intent = detect_onboarding_intent(message_content)

    if intent == 'complete':
        await advance_onboarding(student)

    elif intent == 'skip':
        await advance_onboarding(student, skipped=True)

    elif intent == 'help':
        await student.send(
            "No problem! Let me help.\n\n"
            "[Contextual help based on current stop]\n\n"
            "Reply 'done' when you're ready to continue."
        )

    else:  # ambiguous
        await student.send(
            "I'm not sure if you're ready to continue. "
            "Reply 'done' to move on, or 'help' if you need assistance."
        )
```

**Benefits:**
- âœ… No false advancement
- âœ… Clear help path
- âœ… Better user experience

**Implementation:** See Sprint 0.7 Patch task 0.7.7

---

### AMENDMENT A-16 â€” Admin Command Suite (Medium Priority #2)

**Previous design:** No manual override commands for when automation fails.

**New requirement:** Every automated system needs manual override capability.

**Commands:**

```python
@bot.command(name='manual-activate')
async def manual_activate(ctx, student: discord.Member, email: str):
    """Manually trigger full activation for a student."""
    # Usage: /manual-activate @grace_k email=grace@example.com
    # Bypasses invite matching, directly activates from email lookup

@bot.command(name='link-student')
async def link_student(ctx, discord_id: int, email: str):
    """Manually link Discord account to enrollment row."""
    # Usage: /link-student 123456789 email=grace@example.com
    # Writes discord_id to Google Sheets Column D

@bot.command(name='renew-token')
async def renew_token(ctx, email: str, days: int = 7):
    """Extend a student's M-Pesa submission token."""
    # Usage: /renew-token email=grace@example.com days=7
    # Regenerates token, updates expiry, sends new email

@bot.command(name='retry-activation')
async def retry_activation(ctx, student: discord.Member):
    """Retry activation for a partially-activated student."""
    # Usage: /retry-activation @grace_k
    # Reads activation state, retries from failed step

@bot.command(name='force-role')
async def force_role(ctx, student: discord.Member, role: str):
    """Manually assign a role to a student."""
    # Usage: /force-role @grace_k @Student
    # Bypasses normal role upgrade logic
```

**Security requirements:**
- All commands verify caller is Trevor
- All commands log to #facilitator-dashboard
- All commands require confirmation before executing

**Implementation:** See Sprint 0.7 Patch task 0.7.8

---

**End of amendments. Sections below include legacy narrative and examples. When conflicts appear, apply Canonical V3 (`onboarding-context-canonical-v3.md`) first, then these amendments.**

---

## DOCUMENT CONTRACT (AUDIT + SOURCE OF TRUTH)

This document is the canonical behavior contract for:
- Enrollment journey stages
- Payment collection and verification flow
- Discord role progression (`@Guest` -> `@Student`)
- Google Sheets field contract for onboarding/payment

Execution and status tracking live in:
- `_bmad-output/cohort-design-artifacts/operations/sprint/discord-implementation-sprint.yaml`

Required companion reads for implementation:
- `_bmad-output/cohort-design-artifacts/design-and-architecture/onboarding-context-canonical-v3.md`
- `_bmad-output/cohort-design-artifacts/design-and-architecture/context-engine-experience-design.md`
- `_bmad-output/cohort-design-artifacts/design-and-architecture/discord-community-culture-and-architecture.md`

Conflict resolution order:
1. `onboarding-context-canonical-v3.md` (merged overrides)
2. This document for onboarding/payment behavior
3. Sprint YAML for implementation status and sequencing
4. Context engine doc for personalization logic
5. Discord community doc for channel/culture/permissions

---

## EXECUTIVE SUMMARY

This document defines the complete student onboarding and enrollment flow for K2M Cohort 1. The design emerged from an adversarial review session that identified critical gaps in the initial approach and redesigned the entire journey to eliminate friction while maintaining manual payment verification for Cohort 1.

**Key Design Decisions:**
- **Google Sheets as the interface** â€” No custom dashboard needed
- **Progressive data collection** â€” 3 fields first, full enrollment after commitment
- **Discord as the experience center** â€” Students join before payment, upgrade after
- **Manual payment verification for Cohort 1** â€” Easy automation path for later cohorts
- **KIRA-guided onboarding** â€” Post-activation orientation in Discord DM
- **Tutorial support** â€” Discord setup and M-Pesa payment tutorials to reduce friction

**Critical Fix from Adversarial Review (session 1 â€” 2026-03-04):**
- **Initial wrong assumption:** "Form is too long" (no data to support)
- **Real problem identified:** Discord username REQUIRED field blocks 60% of users (teachers, entrepreneurs, professionals without Discord)
- **Solution:** Capture Discord username + Discord ID automatically via `on_member_join` event â€” NOT collected in any form. Bot embeds `discord_username` + `discord_id` into the enrollment form URL when it DMs the student the link.

**Adversarial Review 2 decisions (2026-03-04):**
- **Form technology:** Custom web forms (NOT Google Forms) â€” `/join`, `/enroll`, `/mpesa-submit`
- **Discord username:** Auto-captured only. Removed from all form fields. Passed as URL param in KIRA's DM enrollment link.
- **Cluster assignment:** Decision 3 CLOSED â€” Option F (stratified diversity + Trevor override)
- **Source of truth for enrollment journey:** This document

---

## THE 4-STEP ENROLLMENT JOURNEY

### **STEP 1: Express Interest (30 seconds)**

**Form Location:** `/join` (k2m-landing site)

**Fields (3 only):**
1. First name
2. Email address
3. Profession dropdown: `teacher | entrepreneur | university_student | working_professional | gap_year_student | other`

**What happens when they submit:**

```javascript
POST /api/interest
{
  "first_name": "Grace",
  "email": "grace@example.com",
  "profession": "teacher"
}
```

**Backend actions:**
1. **Check for duplicate email** â€” if email already exists in Sheets with Status != "Lead", return: "You're already registered! Check your email for next steps or WhatsApp us." Do not append a second row.
2. **If new:** Append row to Google Sheets (Student Roster tab) with Status = "Lead"
3. Send immediate Discord invite email
4. No Discord info collected yet â€” captured automatically at join time via `on_member_join`

**Email sent immediately:**

```
Subject: Welcome to K2M â€” Join the Discord!

Hi Grace,

Click here to join our Discord server:
[DISCORD INVITE LINK]

New to Discord? Watch this 2-minute setup video:
[How to Create a Discord Account â€” Video Tutorial]

Need help? WhatsApp us: +254 XXX XXX XXX

Once you're in Discord, KIRA (our AI bot) will reach out with next steps.

See you inside!

â€” Trevor
K2M Team
```

**Status captured in Google Sheets:**
- Column A: First name
- Column B: Last name (blank)
- Column C: Email
- Column D: Discord identity (`discord_id|discord_username`) (blank until `on_member_join`)
- Column E: Profession
- Column F: Status = "Lead"
- Column G: Created timestamp

---

### **STEP 2: Join Discord + Full Enrollment (5-10 minutes)**

**Student clicks Discord invite link â†’ Joins server**

**Role assigned:** `@Guest` (automatic on join)

**What @Guest can see:**
- âœ… #announcements (read-only)
- âœ… #welcome-and-rules (read-only)
- âœ… #info (read-only)
- âŒ #week-1-wonder (HIDDEN)
- âŒ #thinking-lab (HIDDEN)
- âŒ All program channels (HIDDEN)

**KIRA welcome DM (triggers immediately):**

```
KIRA: Hey Grace! Welcome to K2M ðŸŽ‰

Let's get you enrolled. Fill out the enrollment form here:
[ENROLLMENT FORM LINK]

This takes about 5 minutes.

After you submit, you'll receive payment instructions.

â€” KIRA
```

**Student clicks enrollment form link** â†’ `/enroll`

**Form fields (10 fields â€” NO M-PESA CODE, NO DISCORD USERNAME):**

> **NOTE:** Discord username and Discord ID are auto-captured via `on_member_join` event and passed as hidden URL parameters in the KIRA enrollment DM link (`/enroll?discord_id=123456789&discord_username=grace_k`). They are NOT shown in the form or collected manually.

| Field | Type | Required? | Pre-filled? | Notes |
|-------|------|-----------|-------------|-------|
| First name | Text | âœ… | âœ… (from Step 1 via URL param) | |
| Last name | Text | âœ… | âŒ | Used for cluster assignment |
| Email | Email | âœ… | âœ… (from Step 1 via URL param) | Primary lookup key |
| Profession | Dropdown | âœ… | âœ… (from Step 1 via URL param) | `teacher\|entrepreneur\|university_student\|working_professional\|gap_year_student\|other` |
| Zone self-assessment | Radio (1-4) | âœ… | âŒ | Show zone descriptions (see below) |
| Situation | Textarea | âœ… | âŒ | Placeholder: "Describe your day-to-day work in 2-3 sentences" |
| Goals | Textarea | âœ… | âŒ | Placeholder: "What do you hope to do differently after this program?" |
| Emotional baseline | Dropdown | âœ… | âŒ | Options with labels (see below) |
| Parent email | Email | Conditional (if <18) | âŒ | Hidden unless age indicates minor |
| Consent checkbox | Checkbox | âœ… | âŒ | |

**Emotional baseline dropdown options (with display labels):**
- `excited` â†’ "I'm excited and ready to go"
- `curious` â†’ "I'm curious but not sure what to expect"
- `nervous` â†’ "I'm a little nervous or unsure"
- `skeptical` â†’ "I'm not convinced this will be useful yet"
- `overwhelmed` â†’ "I'm already feeling like there's a lot going on"

**Hidden fields (passed via URL params, not shown to user):**
- `discord_id` â€” numeric Discord snowflake from `on_member_join`
- `discord_username` â€” Discord username from `on_member_join`

**Zone descriptions in form:**
- **Zone 1:** I'm just starting â€” this is all new to me
- **Zone 2:** I'm experimenting â€” trying things out
- **Zone 3:** I'm practicing â€” doing this regularly
- **Zone 4:** This is who I am now â€” it's automatic

**What happens when they submit:**

```javascript
POST /api/enroll
{
  "first_name": "Grace",
  "last_name": "Kamau",
  "email": "grace@example.com",
  "discord_id": "123456789",
  "discord_username": "grace_k", // hidden URL params set by bot
  "profession": "teacher",
  "zone": 1,
  "situation": "I teach Form 3 Chemistry in Nakuru...",
  "goals": "I want to learn how to use AI without feeling like I'm cheating...",
  "emotional_baseline": "nervous",
  "parent_email": "",
  "consent": true
}
```

**Backend actions:**
1. Append to Google Sheets (Student Roster tab)
2. Send payment instructions email with M-Pesa submit link
3. KIRA sends confirmation DM

**Payment email sent immediately:**

```
Subject: K2M Payment Instructions (Next Step)

Hi Grace,

Thanks for enrolling in K2M Cohort 1.

**TO COMPLETE YOUR ENROLLMENT:**

Pay KES 5,000 via M-Pesa:

Paybill: XXXXX
Account: XXXXX
Amount: 5000

[How to Pay via M-Pesa â€” Tutorial Video]

**AFTER PAYING:**

Submit your M-Pesa transaction code here:
[SUBMIT M-PESA CODE LINK]

This confirms your payment and unlocks your full Discord access.

Questions? WhatsApp: +254 XXX XXX XXX

â€” Trevor
K2M Team
```

**KIRA confirmation DM:**

```
KIRA: Got your enrollment form, Grace! âœ…

Next step: Check your email for payment instructions.

After you pay, you'll submit your M-Pesa code in the link from the email.

Once I confirm your payment, your Discord access will be fully activated.

Sit tight â€” you're almost there!

â€” KIRA
```

**Status captured in Google Sheets:**
- Column A-E: Personal info
- Column F: Zone
- Column G: Situation
- Column H: Goals
- Column I: Emotional baseline
- Column J: Parent email
- Column K: M-Pesa Code (blank - awaiting submission)
- Column L: Payment Status = "Enrolled"
- Column M: Created timestamp

---

### **STEP 3: Payment + M-Pesa Code Submission**

**Student pays via M-Pesa:**
- Opens M-Pesa app
- Lipa na M-Pesa â†’ Paybill
- Enters paybill, account, amount
- Receives SMS with transaction code: `ABC1234567`

**Student clicks "Submit M-Pesa Code" link from email**

> **Fix applied 2026-03-04:** Previous URL was `/mpesa-submit?email=grace@example.com` â€” email exposed in URL, visible in browser history and server logs, and spoofable. Replaced with a short-lived token generated at enrollment time and stored in Sheets (Column P). Token is single-use and expires after 7 days.

**Opens:** `/mpesa-submit?token=a3f9c2e1b8d7` *(token generated at enrollment, emailed in payment link)*

**Simple form:**

```
M-PESA CODE SUBMISSION

Hi Grace!

After paying via M-Pesa, enter your 10-digit transaction code below.

[M-Pesa Transaction Code] ____________

(Example: ABC1234567)

This is on your M-Pesa confirmation SMS.

[SUBMIT]
```

**Token generation (at Step 2 form submission):**

```python
# POST /api/enroll â€” runs when student submits enrollment form
import secrets

submit_token = secrets.token_urlsafe(12)   # e.g. "a3f9c2e1b8d7"
token_expiry = datetime.utcnow() + timedelta(days=7)

# Write to Google Sheets Column P (Submit Token) and Column Q (Token Expiry)
# Include in payment email as: /mpesa-submit?token=a3f9c2e1b8d7
```

**What happens when they submit:**

```javascript
POST /api/mpesa-submit
{
  "token": "a3f9c2e1b8d7",
  "mpesa_code": "ABC1234567"
}
```

**Backend actions:**
1. Look up student row by token in Google Sheets Column P
2. Verify token not expired (Column Q) â€” if expired: show "Link expired, WhatsApp us: +254 XXX"
3. Update row with M-Pesa code (Column K)
4. Change Payment Status to "Pending" (Column L)
5. Invalidate token (clear Column P so it can't be reused)
6. Send confirmation email
7. KIRA posts notification to #facilitator-dashboard

**Immediate email:**

```
Subject: We received your M-Pesa code!

Hi Grace!

Thanks for submitting your M-Pesa code.

We'll verify your payment within 24 hours and send your Discord activation.

You'll receive an email when you're fully activated.

â€” Trevor
K2M Team
```

**KIRA posts to #facilitator-dashboard:**

```
ðŸ”” **M-PESA CODE SUBMITTED**

Student: Grace Kamau
Email: grace@example.com
M-Pesa Code: `ABC1234567`

Please verify in M-Pesa app and confirm payment in Google Sheets.
```

**Status captured in Google Sheets:**
- Column K: M-Pesa Code = `ABC1234567`
- Column L: Payment Status = "Pending"

---

### **STEP 4: Trevor Verifies â†’ Activates Student**

**Trevor's workflow (manual for Cohort 1):**

1. **Check #facilitator-dashboard** â€” KIRA posts a payment queue summary every time a new M-Pesa code is submitted (see payment queue bot behavior below)
2. **Open Google Sheets** â†’ "Student Roster" tab
3. **Filter** Column L (Payment Status) = "Pending" (or use the KIRA dashboard summary link)
4. **For each student:**
   - Copy M-Pesa code from Column K
   - Open M-Pesa app
   - Search transaction code
   - Verify:
     - âœ… Correct amount? (KES 5,000)
     - âœ… Correct recipient? (K2M Paybill)
     - âœ… Transaction successful?
   - **If confirmed:** Change Column L dropdown: "Pending" â†’ "Confirmed"
   - **If failed:** Change to "Failed" + add note in Column M (Notes)

**Payment Queue Bot Behavior (added 2026-03-04):**

KIRA posts to #facilitator-dashboard whenever a new M-Pesa code is submitted **and** every 4 hours if there are unverified payments during business hours (8 AM â€“ 8 PM EAT):

```
ðŸ”” PAYMENT QUEUE UPDATE

Pending verification: 3 students
â”œâ”€â”€ Grace Kamau â€” submitted 2h ago â€” M-Pesa: ABC1234567
â”œâ”€â”€ Brian Otieno â€” submitted 4h ago â€” M-Pesa: DEF7891011
â””â”€â”€ Joyce Wanjiku â€” submitted 6h ago â€” M-Pesa: GHI1121314

âš ï¸ Joyce Wanjiku has been waiting 6+ hours.

[Open Google Sheets â†’]
```

**SLA rule:** Any payment sitting Pending > 4 hours during business hours triggers a Trevor alert with escalating urgency emoji (ðŸ”” â†’ âš ï¸ â†’ ðŸš¨ at 4h, 8h, 24h).

**Implementation:** `scheduler.py` runs `check_payment_queue()` every hour. Only posts if there are Pending rows. Uses Sheets API to read Column L.

**Apps Script trigger fires (when Column L = "Confirmed"):**

> **Fix applied 2026-03-04:**
> - Previous version passed `discordUsername` (from form column D) to role upgrade and DM functions. Discord username is no longer collected in the form â€” it's auto-captured by the bot at join time and stored in Column D via a bot webhook. Apps Script now reads Column D for discord_id (numeric) not username.
> - Added error handling: if role upgrade or DM fails, flags the row and alerts Trevor rather than failing silently.
> - Added duplicate payment confirmation guard.

```javascript
function onEdit(e) {
    var range = e.range;
    var sheet = range.getSheet();

    if (sheet.getName() !== "Student Roster") return;
    if (range.getColumn() !== 12) return;      // Column L: Payment Status
    if (range.getValue() !== "Confirmed") return;

    var row = range.getRow();

    // Guard: prevent double-activation if this row was already activated
    var activatedAt = sheet.getRange(row, 15).getValue(); // Column O: Activated At
    if (activatedAt) {
        Logger.log("Row " + row + " already activated at " + activatedAt + ". Skipping.");
        return;
    }

    var firstName    = sheet.getRange(row, 1).getValue();  // Column A
    var email        = sheet.getRange(row, 3).getValue();  // Column C
    var discordId    = sheet.getRange(row, 4).getValue();  // Column D: discord_id (bot-written, numeric)

    var errors = [];

    // 1. Upgrade Discord role via bot webhook (uses discord_id, not username)
    if (discordId) {
        var roleResult = upgradeDiscordRoleById(discordId, 'Student');
        if (!roleResult.success) {
            errors.push("Role upgrade failed: " + roleResult.error);
        }
    } else {
        errors.push("discord_id missing â€” student has not joined Discord yet. Role upgrade skipped.");
    }

    // 2. Pre-load to CIS bot database
    var preloadResult = preloadStudentToCisBot(row);
    if (!preloadResult.success) {
        errors.push("Pre-load failed: " + preloadResult.error);
    }

    // 3. Send activation email (always â€” even if Discord steps failed)
    try {
        MailApp.sendEmail({
            to: email,
            subject: "Welcome to K2M Cohort 1! ðŸŽ‰",
            htmlBody: generateActivationEmail(firstName, row)
        });
    } catch (err) {
        errors.push("Activation email failed: " + err.message);
    }

    // 4. KIRA activation DM (only if discord_id is available)
    if (discordId && errors.length === 0) {
        var dmResult = sendKiraActivationDmById(discordId, firstName);
        if (!dmResult.success) {
            errors.push("KIRA DM failed: " + dmResult.error);
        }
    }

    // 5. Log to dashboard â€” always fires
    if (errors.length > 0) {
        // Partial activation â€” flag for Trevor
        sheet.getRange(row, 13).setValue("âš ï¸ ACTIVATION ERRORS: " + errors.join(" | ")); // Column M: Notes
        logToFacilitatorDashboard("âš ï¸ " + firstName + " PARTIAL ACTIVATION â€” manual action needed: " + errors.join(", "));
    } else {
        // Full activation
        sheet.getRange(row, 15).setValue(new Date()); // Column O: Activated At
        logToFacilitatorDashboard("âœ… " + firstName + " FULLY ACTIVATED");
    }
}
```

**What happens AUTOMATICALLY when Trevor confirms:**

#### **A) Discord Role Upgrade**

**Role changes:** `@Guest` â†’ `@Student`

**What @Student can NOW see (that @Guest couldn't):**
- âœ… #week-1-wonder (VISIBLE)
- âœ… #thinking-lab (VISIBLE â€” can use /frame)
- âœ… #thinking-showcase (VISIBLE)
- âœ… #week-2-curiosity (VISIBLE)
- âœ… All other week channels (UNLOCK progressively)
- âœ… Cluster voice channel (VISIBLE)
- âœ… Bot commands: /frame (Week 1), /diverge + /challenge (Week 4), /synthesize (Week 6)

#### **B) Activation Email**

```
Subject: Welcome to K2M Cohort 1! ðŸŽ‰

Hi Grace!

Your payment is confirmed and you're now a full student.

**YOUR DISCORD ACCESS IS NOW FULLY ACTIVATED**

Go to Discord â€” you'll see new channels:
â€¢ #week-1-wonder (daily prompts start here)
â€¢ #thinking-lab (try /frame!)
â€¢ #thinking-showcase (share your work)

**YOUR CLUSTER:**
Cluster 2

**FIRST LIVE SESSION:**
March 10th at 6 PM EAT

**WEEK 1 STARTS:**
March 13th

I'll post your first daily prompt at 9:15 AM EAT.

See you in Discord!

â€” Trevor
K2M Team
```

#### **C) KIRA Activation DM**

```
KIRA: Grace, you're in! ðŸŽ‰

Your payment is confirmed and your access is now fully activated.

**Here's what you can do now:**

â€¢ Visit #week-1-wonder â€” your Week 1 daily prompts will be posted here
â€¢ Try /frame in #thinking-lab â€” your first thinking skill practice
â€¢ Introduce yourself in #week-1-wonder â€” say hi to your cohort!

**YOUR CLUSTER:**
You're in Cluster 2
[View cluster schedule]

**FIRST LIVE SESSION:**
March 10th at 6 PM EAT

I'll send you a reminder 1 hour before.

**WEEK 1 STARTS:**
March 13th

I'll post your first daily prompt at 9:15 AM EAT.

Ready? Let's do this! ðŸ’ª

â€” KIRA
```

#### **D) Database Pre-load (automatic, invisible to student)**

> **Fix applied 2026-03-04:**
> - Previous version missing 9 context-engine columns: `barrier_type`, `barrier_confidence`, `initial_zone`, `real_last_name`, `discord_username`, `consent_preference`, `zone_shift_count`, `frame_sessions_count`, `showcase_posts_count`.
> - `discord_id` now read from Column D (bot-written at join time via `on_member_join`). Not assumed to be in the form.
> - Upsert pattern (INSERT OR REPLACE) makes it idempotent â€” safe to re-run.
> - `barrier_type` inferred here at pre-load time (keyword scoring per context-engine-experience-design.md Â§1.2). Lives in `cis-discord-bot/scripts/preload_students.py`.

```python
# cis-discord-bot/scripts/preload_students.py
# Called by: Apps Script webhook on payment confirmation
# Upserts one student row from Google Sheets into SQLite

def preload_student(sheet_row: dict) -> dict:
    """
    Upserts student into SQLite from Sheets data.
    Returns {"success": True} or {"success": False, "error": str}.
    """
    try:
        conn = sqlite3.connect('cohort-1.db')
        cursor = conn.cursor()

        zone = int(sheet_row.get('zone', 1))

        barrier_type, barrier_confidence = infer_barrier_type(
            situation=sheet_row.get('situation', ''),
            goals=sheet_row.get('goals', ''),
            emotional_baseline=sheet_row.get('emotional_baseline', ''),
            profession=sheet_row.get('profession', '')
        )

        cursor.execute("""
            INSERT INTO students (
                discord_id, discord_username, first_name, real_last_name,
                email, profession, zone, initial_zone,
                situation, goals, emotional_baseline,
                barrier_type, barrier_confidence,
                cluster_id, parent_email, consent_preference,
                preloaded, engagement_level,
                zone_shift_count, frame_sessions_count, showcase_posts_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET
                discord_username   = excluded.discord_username,
                first_name         = excluded.first_name,
                real_last_name     = excluded.real_last_name,
                email              = excluded.email,
                profession         = excluded.profession,
                zone               = excluded.zone,
                initial_zone       = COALESCE(students.initial_zone, excluded.initial_zone),
                situation          = excluded.situation,
                goals              = excluded.goals,
                emotional_baseline = excluded.emotional_baseline,
                barrier_type       = excluded.barrier_type,
                barrier_confidence = excluded.barrier_confidence,
                cluster_id         = excluded.cluster_id,
                parent_email       = excluded.parent_email,
                consent_preference = excluded.consent_preference,
                preloaded          = 1
        """, (
            sheet_row.get('discord_id'),        # Column D â€” bot-written at on_member_join
            sheet_row.get('discord_username'),  # Column D alongside discord_id
            sheet_row.get('first_name'),
            sheet_row.get('last_name'),         # stored as real_last_name
            sheet_row.get('email'),
            sheet_row.get('profession'),
            zone,
            zone,                               # initial_zone = zone at enrollment
            sheet_row.get('situation'),
            sheet_row.get('goals'),
            sheet_row.get('emotional_baseline'),
            barrier_type,
            barrier_confidence,
            sheet_row.get('cluster_id'),        # Optional if cluster assignment has not run yet
            sheet_row.get('parent_email') or None,
            sheet_row.get('consent_preference', 'share_weekly'),
            True, 'quiet', 0, 0, 0
        ))

        conn.commit()
        conn.close()
        return {"success": True}

    except Exception as e:
        return {"success": False, "error": str(e)}


def infer_barrier_type(situation: str, goals: str, emotional_baseline: str, profession: str):
    """Keyword scoring per context-engine-experience-design.md Â§1.2."""
    text = f"{situation} {goals}".lower()
    scores = {
        'identity':  _score(text, ['not technical','not for people like me','feel behind',
                                   'intimidated','not smart enough','afraid','don\'t belong',
                                   'struggle with technology']),
        'time':      _score(text, ['busy','no time','overwhelming','too much','responsibilities',
                                   'can\'t find time','schedule','work-life','so many commitments']),
        'relevance': _score(text, ['not sure how this applies','my job doesn\'t need',
                                   'different field','don\'t see the connection','not relevant']),
        'technical': _score(text, ['confusing','don\'t know where to start','tried and failed',
                                   'complicated','technical terms','don\'t understand the tools'])
    }
    eb = (emotional_baseline or '').lower()
    if eb in ('nervous', 'overwhelmed'):
        scores['identity']  = min(10, scores['identity'] + 2)
        scores['technical'] = min(10, scores['technical'] + 2)
    elif eb == 'skeptical':
        scores['relevance'] = min(10, scores['relevance'] + 2)

    if profession == 'teacher':        scores['identity']  = min(10, scores['identity'] + 1)
    elif profession == 'entrepreneur': scores['relevance'] = min(10, scores['relevance'] + 1)

    top_score = max(scores.values())
    if top_score == 0:
        return (None, 0.0)

    sorted_vals = sorted(scores.values(), reverse=True)
    second = sorted_vals[1] if len(sorted_vals) > 1 else 0
    confidence = round(top_score / (top_score + second), 2) if (top_score + second) > 0 else 1.0
    if confidence < 0.4:
        return (None, confidence)

    for barrier in ['identity', 'relevance', 'time', 'technical']:
        if scores[barrier] == top_score:
            return (barrier, confidence)

    return (None, 0.0)


def _score(text: str, keywords: list) -> int:
    return min(10, sum(1 for kw in keywords if kw in text))
```

**Result:** KIRA knows profession, zone, and barrier type for every student at the moment they first type `/frame`. Context engine fully populated at activation time.

---

## DISCORD ROLE PROGRESSION SYSTEM

### **Role Hierarchy:**

| Role | Access Level | When Assigned |
|------|-------------|---------------|
| `@Guest` | Read-only: #announcements, #welcome-and-rules, #info | On Discord join (before payment) |
| `@Student` | Full access to all program channels, bot commands | After payment confirmation |
| `@Cluster-1` through `@Cluster-8` | Cluster voice channel access | Assigned during activation |

### **Permission Boundaries:**

**@Guest cannot:**
- Post in any channels
- Use any bot commands (/frame, /diverge, etc.)
- See any week channels
- See #thinking-lab or #thinking-showcase

**@Student can:**
- Post in all week channels
- Use /frame (available Week 1)
- Use /diverge and /challenge (unlock Week 4)
- Use /synthesize (unlocks Week 6)
- Access cluster voice channel

### **Channel Visibility by Role:**

| Channel | @Guest | @Student |
|---------|--------|----------|
| #announcements | âœ… Read | âœ… Read |
| #welcome-and-rules | âœ… Read | âœ… Read |
| #info | âœ… Read | âœ… Read |
| #week-1-wonder | âŒ Hidden | âœ… Read + Write |
| #week-2-curiosity | âŒ Hidden | âœ… Read + Write (unlocks Week 2) |
| #thinking-lab | âŒ Hidden | âœ… Read + Write + /frame |
| #thinking-showcase | âŒ Hidden | âœ… Read + Write |
| Cluster Voice | âŒ Hidden | âœ… Join + Speak |
| #facilitator-dashboard | âŒ Hidden | âŒ Hidden (Trevor only) |

---

## PRE-COHORT HOLDING EXPERIENCE

> **Added 2026-03-04 (adversarial review 2):** Students activate on a rolling basis before cohort start. Without a holding experience, they land in an empty-looking Discord server with nothing happening. For a first-time Discord user, an empty server = broken or inactive. This section defines the experience for the gap between activation and Week 1.

### **The Problem:**
Students who activate 3-7 days before Week 1 have no prompts, no peers active, no content. Excitement window closes. Churn happens before the program even starts.

### **Holding Experience Design:**

**A) #pre-launch channel (visible to @Student, active before Week 1)**

Pinned message posted by KIRA when the first student activates:

```
ðŸš€ YOU'RE EARLY â€” COHORT 1 HASN'T STARTED YET

Week 1 kicks off on {{week1_start_date}} at 9:15 AM EAT.

While you wait:

â†’ Introduce yourself in #week-1-wonder if you haven't already
â†’ Try /frame in #thinking-lab â€” it's live now
â†’ Explore the channels so you know where everything is

Who else is here early? Say hi below ðŸ‘‡
```

KIRA posts a daily countdown starting 3 days before Week 1:

```
3 days until Week 1. {{n}} students confirmed so far.
Daily prompts begin {{week1_start_date}} at 9:15 AM EAT.
```

**B) KIRA DM for early activations (fires if activation > 48h before Week 1)**

```
KIRA: Grace, you're one of the first to arrive â€” Week 1 starts on {{week1_start_date}}.

Here's what you can do right now while you wait:

â†’ Try /frame in #thinking-lab â€” the agents are live and ready
â†’ Introduce yourself in #week-1-wonder
â†’ Explore #welcome-and-rules

I'll DM you the night before Week 1 starts with what to expect on Day 1.

â€” KIRA
```

**C) Night-before Week 1 DM (fires Saturday evening, EAT, before Monday start)**

```
KIRA: Week 1 starts tomorrow, {first_name}.

Monday 9:00 AM EAT: Your first node (a short podcast/video) goes live in #week-1-wonder
Monday 9:15 AM EAT: Your first daily prompt

The prompt will ask you one question. You'll respond in the channel.
That's it. The whole program begins with one question.

â€” KIRA
```

**Implementation:**
- `scheduler.py` handles the countdown posts and night-before DM
- `onboarding_stop = 4` (complete) gates the night-before DM â€” only students who finished onboarding receive it
- Students who activated but haven't completed onboarding get: "Week 1 starts tomorrow â€” finish your setup here: /onboarding"

---

## POST-ACTIVATION ONBOARDING EXPERIENCE

### **Design Philosophy:**

**KIRA-Guided Onboarding** (Option B from adversarial review)

KIRA sends a sequential DM flow that guides students through their first experience in Discord, helping them discover channels and try their first /frame session.

> **Fix applied 2026-03-04 (adversarial review 2):**
> - **Stop 2 (public intro post) is now OPTIONAL.** Requiring a public post in the first 5 minutes of joining is a high-anxiety ask for teachers, professionals, and nervous first-timers. Students who skip it are flagged for a gentle Juncture 1 DM in Week 1 â€” not blocked.
> - **"done" keyword replaced with intent matching.** Bot now accepts any of: "done", "ready", "finished", "ok", "next", "yes", or any message in the DM while onboarding is active. Timeout extended to 7 days (not 24 hours). Sequence is re-enterable via `/onboarding` command at any time.
> - **Mobile navigation note added** to all onboarding DMs â€” Discord mobile sidebar is not visible by default.

### **Onboarding Flow (3 Stops):**

#### **Activation Happens â†’ KIRA Sends Onboarding DM:**

```
KIRA: Grace, you're in! ðŸŽ‰

Let's get you oriented. This takes about 5 minutes.

ðŸ“ On your phone? Tap the â˜° icon (top left) to find channels.
ðŸ“ On desktop? Channels are in the left sidebar.

**3 QUICK STOPS:**

1ï¸âƒ£ #welcome-and-rules â€” What channels are for
   â†’ [Open Channel]

2ï¸âƒ£ #week-1-wonder â€” Meet your cohort (optional â€” whenever you're ready)
   â†’ [Open Channel]

3ï¸âƒ£ #thinking-lab â€” Your first thinking practice
   â†’ [Open Channel]

Start with Stop 1. When you're back here, just reply anything â€” "done",
"ready", "ok" â€” and I'll walk you to the next stop.

Take your time. I'll be here. ðŸš€

â€” KIRA
```

#### **Navigation Mechanics:**

**DM â†’ Channel:** Student clicks hyperlink â†’ Opens channel in Discord app/browser

**Returning to DM on mobile:** Tap the Discord icon (bottom left) â†’ tap your profile picture or the DM inbox icon â†’ tap KIRA.

**DM back-navigation note** â€” included in all onboarding DMs as a one-liner:
> *"To come back here: tap the Discord icon â†’ DMs â†’ KIRA"*

**Technical implementation:**

```python
def channel_link(channel_id):
    return f"https://discord.com/channels/{SERVER_ID}/{channel_id}"

# Completion detection â€” intent matching, not exact keyword
ONBOARDING_CONTINUE_SIGNALS = {
    'done', 'ready', 'finished', 'ok', 'yes', 'next',
    'read it', 'read', 'seen it', 'i\'m back', 'back', 'went'
}

def is_continue_signal(message_content: str) -> bool:
    content = message_content.lower().strip()
    # Any of the known signals, OR any short message (â‰¤15 chars) in an active session
    return (
        any(signal in content for signal in ONBOARDING_CONTINUE_SIGNALS)
        or len(content) <= 15
    )
```

**Re-entry:** Student can type `/onboarding` at any time to restart the flow from their current stop.

#### **Step 1: #welcome-and-rules (30 seconds) â€” REQUIRED**

**Pinned message in channel:**

```
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘   WELCOME TO K2M COHORT 1! ðŸŽ‰            â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

You're now part of a community of teachers, entrepreneurs,
students, and professionals learning AI-powered thinking skills.

**YOUR 5 KEY CHANNELS:**

ðŸ“ #announcements â€” Important updates from Trevor
ðŸ“ #week-1-wonder â€” Your daily prompts and peer discussions
ðŸ“ #thinking-lab â€” Your private AI thinking practice (type /frame here)
ðŸ“ #thinking-showcase â€” Published insights from the cohort
ðŸ“ KIRA DMs â€” Your personal guide (check your DMs)

**3 SIMPLE RULES:**

1ï¸âƒ£ Be respectful â€” We're all learning together
2ï¸âƒ£ Do your best work â€” This is what you make it
3ï¸âƒ£ Ask for help â€” KIRA and Trevor are here for you

ðŸ“Œ IN YOUR ONBOARDING?

â†’ To return to KIRA: tap the Discord icon â†’ DMs â†’ KIRA
â†’ Then just type anything â€” "done", "ok", "back" â€” to continue
```

**Bot detects any continue signal in the DM â†’ KIRA responds:**

```
KIRA: Great â€” you know where everything is. âœ…

Stop 2 is optional but worth it when you're ready:

Go to #week-1-wonder and read a few posts â€” you'll see who else
is in your cohort.

You can introduce yourself too: "I'm [Name], I'm a [profession],
and I'm here because..."

No pressure â€” whenever you feel like it. Or skip it and
go straight to Stop 3.

â†’ [Open #week-1-wonder]
â†’ Or type "skip" to go straight to #thinking-lab

â€” KIRA
```

#### **Step 2: #week-1-wonder â€” OPTIONAL**

**If student posts an introduction:**

KIRA reacts ðŸ‘€ within 1 minute. No public announcement from KIRA (avoids pressure on others).

KIRA DMs privately:
```
KIRA: Saw your intro! âœ…

Now for the main event â€” your first thinking practice.

â†’ [Open #thinking-lab]

Type /frame in that channel. I'll be right there.

(To get back here: Discord icon â†’ DMs â†’ KIRA)
```

**If student types "skip" or any continue signal without posting:**

```
KIRA: No problem â€” you can always introduce yourself later.

â†’ [Open #thinking-lab]

Type /frame in that channel. I'll be right there.

(To get back here: Discord icon â†’ DMs â†’ KIRA)
```

**Bot detection for Stop 2 completion:** `on_message` event in #week-1-wonder checks if author has `onboarding_stop=2` pending. If they post â†’ mark Stop 2 complete, send above DM. If they type "skip" in DM â†’ advance to Stop 3.

#### **Step 3: #thinking-lab â€” First /frame (5-7 minutes)**

**Student goes to #thinking-lab â†’ Types:** `/frame`

â€” KIRA
```

#### **Step 3: #thinking-lab â€” First /frame (5-7 minutes)**

**Student goes to #thinking-lab â†’ Types:** `/frame`

**KIRA starts DM conversation (first-time simplified prompt):**

```
KIRA: Hey Grace! I'm KIRA's Framing Agent.

Habit 1 is PAUSE â€” before you act, stop and articulate the real question.

Let's practice with something real.

**What's one thing you're dealing with right now â€” at work, in life,
any situation where you're not sure what to do next?**

Just describe it in 1-2 sentences.
```

**Student replies:** "My head teacher wants me to start using AI in my lesson planning, but I feel like I'm cheating my students if I do."

**KIRA continues (guided /frame session):**
- Asks clarifying questions
- Helps surface the real question
- Ends with reflection: "So what you're really asking is..."

**After /frame completes:**

```
KIRA: Grace, that was Habit 1 in action. âœ…

You just did something most teachers never do:
you paused to notice the real question behind the request.

What you started with: "How do I use AI in lesson planning?"
What we uncovered: "How do I use AI without betraying my profession?"

That gap? That's where real thinking happens.

**Next time you face a problem, try /frame before you act.**

Even 5 minutes changes what comes after.

---

**You've completed onboarding! ðŸŽ‰**

What's next:

â€¢ Week 1 starts on March 13th â€” daily prompts in #week-1-wonder
â€¢ Your first live session: March 10th at 6 PM EAT
â€¢ Practice /frame anytime in #thinking-lab

Questions? Just ask me in any channel!

â€” KIRA
```

**KIRA posts in #thinking-lab:**

```
KIRA: @Grace just completed their first /frame session! âœ…

If you've just joined, your onboarding is:

1ï¸âƒ£ Read #welcome-and-rules
2ï¸âƒ£ Introduce yourself in #week-1-wonder
3ï¸âƒ£ Try /frame here in #thinking-lab

I'll guide you through it! ðŸš€

â€” KIRA
```

---

## TECHNICAL ARCHITECTURE

### **System Components:**

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Landing Page Site  â”‚
â”‚  (k2m-landing)      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
           â”‚
           â”œâ”€â”€ POST /api/interest
           â”‚   â””â”€â”€> Google Sheets
           â”‚   â””â”€â”€> Email service (Discord invite)
           â”‚
           â”œâ”€â”€ POST /api/enroll
           â”‚   â””â”€â”€> Google Sheets
           â”‚   â””â”€â”€> Email service (Payment instructions)
           â”‚
           â””â”€â”€ POST /api/mpesa-submit
               â””â”€â”€> Google Sheets
               â””â”€â”€> Email service (Confirmation)

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Google Sheets      â”‚
â”‚  (Student Roster)   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
           â”‚
           â”œâ”€â”€> Apps Script trigger (onEdit)
           â”‚   â””â”€â”€> Discord bot API (role upgrade)
           â”‚   â””â”€â”€> Email service (Activation)
           â”‚   â””â”€â”€> Pre-load script (SQLite)
           â”‚
           â””â”€â”€> Manual Trevor access

â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  CIS Discord Bot    â”‚
â”‚  (cis-discord-bot)  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
           â”‚
           â”œâ”€â”€> on_member_join (welcome DM)
           â”œâ”€â”€> KIRA onboarding flow
           â”œâ”€â”€> /frame, /diverge, etc.
           â””â”€â”€> Notifications to #facilitator-dashboard
```

---

## GOOGLE SHEETS INTEGRATION

### **Student Roster Sheet Structure:**

| Column | Field Name | Type | Example |
|--------|-----------|------|---------|
| A | First Name | Text | Grace |
| B | Last Name | Text | Kamau |
| C | Email | Text | grace@example.com |
| D | Discord ID + Username | Text | 123456789\|grace_k |
| E | Profession | Dropdown | teacher |
| F | Zone | Number (1-4) | 1 |
| G | Situation | Long Text | I teach Form 3... |
| H | Goals | Long Text | I want to learn... |
| I | Emotional Baseline | Dropdown | nervous |
| J | Parent Email | Text | (blank if adult) |
| K | M-Pesa Code | Text | ABC1234567 |
| L | Payment Status | Dropdown | Enrolled â†’ Pending â†’ Confirmed |
| M | Notes | Text | (for failed payments) |
| N | Created At | DateTime | 2026-03-04 14:32:00 |
| O | Activated At | DateTime | 2026-03-04 16:45:00 |

### **Apps Script Triggers:**

**Trigger 1: onEdit (Payment Status Change)**

```javascript
function onEdit(e) {
    var range = e.range;
    var sheet = range.getSheet();

    if (sheet.getName() === "Student Roster" &&
        range.getColumn() === 12 && // Column L
        range.getValue() === "Confirmed") {

        activateStudent(e.range.getRow());
    }
}

function activateStudent(rowNumber) {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Student Roster");
    var row = sheet.getRange(rowNumber, 1, 1, 16).getValues()[0];

    var firstName = row[0];
    var email = row[2];
    var discordUsername = row[3];

    // 1. Upgrade Discord role
    upgradeDiscordRole(discordUsername, 'Student');

    // 2. Pre-load to database
    preloadToDatabase(row);

    // 3. Send activation email
    sendActivationEmail(email, firstName);

    // 4. KIRA DM
    sendKiraActivation(discordUsername, firstName);
}
```

---

## EMAIL TEMPLATES

### **Email 1: Discord Invite (after Step 1)**

**Subject:** Welcome to K2M â€” Join the Discord!

```
Hi {{first_name}},

Click here to join our Discord server:
{{discord_invite_url}}

New to Discord? Watch this 2-minute setup video:
{{discord_tutorial_url}}

Need help? WhatsApp us: {{whatsapp_number}}

Once you're in Discord, KIRA (our AI bot) will reach out with next steps.

See you inside!

â€” Trevor
K2M Team
```

### **Email 2: Payment Instructions (after Step 2)**

**Subject:** K2M Payment Instructions (Next Step)

```
Hi {{first_name}},

Thanks for enrolling in K2M Cohort 1.

**TO COMPLETE YOUR ENROLLMENT:**

Pay KES {{amount}} via M-Pesa:

Paybill: {{mpesa_paybill}}
Account: {{mpesa_account}}
Amount: {{amount}}

{{mpesa_tutorial_url}}

**AFTER PAYING:**

Submit your M-Pesa transaction code here:
{{mpesa_submit_url}}

This confirms your payment and unlocks your full Discord access.

Questions? WhatsApp: {{whatsapp_number}}

â€” Trevor
K2M Team
```

### **Email 3: M-Pesa Code Received (after Step 3)**

**Subject:** We received your M-Pesa code!

```
Hi {{first_name}},

Thanks for submitting your M-Pesa code.

We'll verify your payment within 24 hours and send your Discord activation.

You'll receive an email when you're fully activated.

â€” Trevor
K2M Team
```

### **Email 4: Welcome to Cohort 1! (after Step 4)**

**Subject:** Welcome to K2M Cohort 1! ðŸŽ‰

```
Hi {{first_name}}!

Your payment is confirmed and you're now a full student.

**YOUR DISCORD ACCESS IS NOW FULLY ACTIVATED**

Go to Discord â€” you'll see new channels:
â€¢ #week-1-wonder (daily prompts start here)
â€¢ #thinking-lab (try /frame!)
â€¢ #thinking-showcase (share your work)

**YOUR CLUSTER:**
Cluster {{cluster_number}}

**FIRST LIVE SESSION:**
{{first_session_date}} at 6 PM EAT
{{add_to_calendar_link}}

**WEEK 1 STARTS:**
{{week1_start_date}}

I'll post your first daily prompt at 9:15 AM EAT.

See you in Discord!

â€” Trevor
K2M Team
```

---

## KIRA BOT AUTOMATION

### **Event Handlers:**

#### **on_member_join (Step 2)**

> **Fix applied 2026-03-04:** Previous version had a critical bug: `db.get_lead_by_email(discord_username)` used the discord username as an email lookup key â€” these are completely different values and will never match. Fixed below.
>
> **Linking approach:** Discord username + ID are auto-captured here and embedded into the enrollment form URL as hidden params. The enrollment form backend then uses email (entered by the student) to find the Google Sheets record and update it with the captured discord_id + discord_username.

```python
@bot.event
async def on_member_join(member):
    discord_username = member.name   # e.g. "grace_k"
    discord_id = str(member.id)      # e.g. "123456789012345678"

    # Build enrollment form URL with discord identity embedded
    # The /enroll form backend will match on email, then write discord_id + discord_username to Sheets
    enroll_url = f"{ENROLLMENT_FORM_URL}?discord_id={discord_id}&discord_username={discord_username}"

    # Check if they have a preloaded student record (already enrolled + paid â€” rejoining scenario)
    existing = db.get_student_by_discord_id(discord_id)
    if existing and existing.get('payment_status') == 'Confirmed':
        # Already a confirmed student â€” they may have left and rejoined
        await member.send(
            f"Welcome back, {existing['first_name']}! Your access is still active.\n\n"
            f"Head to #week-1-wonder to pick up where you left off."
        )
        # Re-apply @Student role in case it was lost
        await _apply_student_role(member)
        return

    # Check if they have a preloaded record with unconfirmed payment
    pending = db.get_student_by_discord_id(discord_id)
    if pending and pending.get('payment_status') in ('Enrolled', 'Pending'):
        await member.send(
            f"Hey {pending['first_name']}! Great to see you here.\n\n"
            f"Your enrollment is recorded. Next step: complete payment.\n\n"
            f"Check your email for M-Pesa instructions, then submit your code here:\n"
            f"{MPESA_SUBMIT_URL}?token={pending['submit_token']}\n\n"
            f"Questions? Just reply here.\n\nâ€” KIRA"
        )
        return

    # New join â€” no record found yet
    # Send enrollment form link with their discord identity pre-embedded
    await member.send(
        f"Hey! Welcome to K2M Cohort 1 ðŸ‘‹\n\n"
        f"I'm KIRA, your thinking partner for this program.\n\n"
        f"Let's get you enrolled. This takes about 5 minutes:\n"
        f"{enroll_url}\n\n"
        f"New to Discord? That's completely fine â€” most of your cohort is too.\n\n"
        f"After you submit the form, I'll send you payment instructions.\n\n"
        f"â€” KIRA"
    )

    # Log unmatched join for Trevor dashboard visibility
    await _log_event('student_unmatched_join', {
        'discord_username': discord_username,
        'discord_id': discord_id
    })


async def _apply_student_role(member):
    """Applies @Student role. Separate helper for reuse and error isolation."""
    guild = member.guild
    student_role = discord.utils.get(guild.roles, name='Student')
    if student_role and student_role not in member.roles:
        await member.add_roles(student_role)
```

#### **KIRA Onboarding Flow (post-activation)**

> **Fix applied 2026-03-04:**
> - Previous version used `bot.wait_for('message', timeout=86400)` â€” 24-hour timeout, after which the onboarding sequence terminated permanently. Students returning after 25+ hours had no recovery path.
> - "done" exact keyword replaced with intent matching (`is_continue_signal()`).
> - Stop 2 (public intro post) is now optional â€” student can type "skip" to proceed.
> - Onboarding state persisted in SQLite (`students.onboarding_stop`) so it survives bot restarts.
> - `/onboarding` command re-enters the flow at the student's current stop.

```python
# Onboarding stop values: 0=not started, 1=sent Stop 1, 2=sent Stop 2, 3=sent Stop 3, 4=complete
CONTINUE_SIGNALS = {'done','ready','finished','ok','yes','next','read','back','went','seen','i\'m back'}

class OnboardingFlow:
    def __init__(self, bot):
        self.bot = bot

    def channel_link(self, channel_id):
        return f"https://discord.com/channels/{SERVER_ID}/{channel_id}"

    def is_continue_signal(self, content: str) -> bool:
        content = content.lower().strip()
        return any(sig in content for sig in CONTINUE_SIGNALS) or len(content) <= 15

    async def start_onboarding(self, student, first_name: str):
        """Send initial onboarding DM and record stop=1 in DB."""
        db.update_student(student.id, {'onboarding_stop': 1})

        mobile_tip = "ðŸ“ On your phone? Tap â˜° (top left) to find channels. To return here: Discord icon â†’ DMs â†’ KIRA."

        await student.send(
            f"{first_name}, you're in! ðŸŽ‰\n\n"
            f"{mobile_tip}\n\n"
            "**3 QUICK STOPS:**\n\n"
            f"1ï¸âƒ£ #welcome-and-rules â€” What channels are for\n"
            f"   â†’ {self.channel_link(WELCOME_RULES_ID)}\n\n"
            f"2ï¸âƒ£ #week-1-wonder â€” Meet your cohort (optional)\n"
            f"   â†’ {self.channel_link(WEEK1_WONDER_ID)}\n\n"
            f"3ï¸âƒ£ #thinking-lab â€” Your first thinking practice\n"
            f"   â†’ {self.channel_link(THINKING_LAB_ID)}\n\n"
            "Start with Stop 1. When you're back, just reply anything â€” "
            "\"done\", \"ok\", \"back\" â€” and I'll walk you to the next stop.\n\n"
            "â€” KIRA"
        )

    async def handle_dm(self, student, message_content: str):
        """
        Called on every DM from a student with onboarding_stop in (1, 2, 3).
        Routes to the correct next step.
        """
        stop = db.get_student(student.id).get('onboarding_stop', 0)
        content = message_content.lower().strip()

        if stop == 1 and self.is_continue_signal(content):
            # Advance to Stop 2
            db.update_student(student.id, {'onboarding_stop': 2})
            await student.send(
                "âœ… You know where everything is.\n\n"
                "Stop 2 is optional â€” whenever you're ready:\n\n"
                f"â†’ {self.channel_link(WEEK1_WONDER_ID)}\n\n"
                "You can post an intro: \"I'm [Name], I'm a [profession], and I'm here because...\"\n\n"
                "No pressure. Type \"skip\" to go straight to #thinking-lab, or head there whenever.\n\n"
                "â€” KIRA"
            )

        elif stop == 2 and ('skip' in content or self.is_continue_signal(content)):
            # Advance to Stop 3 (skipped or completed Stop 2)
            await self._send_stop_3(student)

        elif stop == 3 and self.is_continue_signal(content):
            # They completed /frame â€” mark onboarding complete
            db.update_student(student.id, {'onboarding_stop': 4})
            await student.send(
                "âœ… Onboarding complete.\n\n"
                "Week 1 starts with daily prompts in #week-1-wonder. "
                "Your first prompt goes live at 9:15 AM EAT.\n\n"
                "â€” KIRA"
            )

    async def _send_stop_3(self, student):
        db.update_student(student.id, {'onboarding_stop': 3})
        await student.send(
            f"Now for the main event â€” your first thinking practice.\n\n"
            f"â†’ {self.channel_link(THINKING_LAB_ID)}\n\n"
            "Type /frame in that channel. I'll be right there.\n\n"
            "(To come back here: Discord icon â†’ DMs â†’ KIRA)\n\n"
            "â€” KIRA"
        )

    async def on_week1_wonder_post(self, student):
        """Called when a student with onboarding_stop=2 posts in #week-1-wonder."""
        db.update_student(student.id, {'onboarding_stop': 2, 'intro_posted': True})
        # React ðŸ‘€ â€” handled by participation tracker, not here
        await student.send(
            "Saw your intro! âœ…\n\n"
            f"â†’ {self.channel_link(THINKING_LAB_ID)}\n\n"
            "Type /frame in that channel. I'll be right there.\n\n"
            "â€” KIRA"
        )

    def channel_link(self, channel_id):
        return f"https://discord.com/channels/{SERVER_ID}/{channel_id}"
```

#### **Payment Notifications (Step 3)**

```python
async def notify_payment_pending(studentData):
    dashboard_channel = bot.get_channel(DASHBOARD_CHANNEL_ID)

    embed = discord.Embed(
        title="ðŸ”” M-PESA CODE SUBMITTED",
        color=0xFFFF00
    )
    embed.add_field(name="Student", value=f"{studentData['first_name']} {studentData['last_name']}")
    embed.add_field(name="Email", value=studentData['email'])
    embed.add_field(name="M-Pesa Code", value=f"`{studentData['mpesa_code']}`")

    await dashboard_channel.send(
        content="ðŸ”” **PAYMENT PENDING VALIDATION**\n\nPlease check M-Pesa and confirm payment.",
        embed=embed
    )
```

#### **Activation DM (Step 4)**

```python
async def send_activation_dm(studentData):
    discord_user = bot.get_user(studentData['discord_id'])

    await discord_user.send(
        f"{studentData['first_name']}, you're in! ðŸŽ‰\n\n"
        "Your payment is confirmed and your access is now fully activated.\n\n"
        "**Here's what you can do now:**\n\n"
        "â€¢ Visit #week-1-wonder â€” your Week 1 daily prompts will be posted here\n"
        "â€¢ Try /frame in #thinking-lab â€” your first thinking skill practice\n"
        "â€¢ Introduce yourself in #week-1-wonder â€” say hi to your cohort!\n\n"
        f"**YOUR CLUSTER:** Cluster {studentData['cluster_id']}\n"
        f"**FIRST LIVE SESSION:** {studentData['first_session_date']} at 6 PM EAT\n"
        f"**WEEK 1 STARTS:** {studentData['week1_start_date']}\n\n"
        "I'll post your first daily prompt at 9:15 AM EAT.\n\n"
        "Ready? Let's do this! ðŸ’ª\n\n"
        "â€” KIRA"
    )

    # Also start onboarding flow
    onboarding = OnboardingFlow(bot)
    await onboarding.start_onboarding(discord_user)
```

---

## BUILD REQUIREMENTS

### **Frontend (k2m-landing site):**

1. **Interest Form Page** (`/join`)
   - 3 fields: first name, email, profession
   - Simple, clean design
   - Mobile-optimized

2. **Enrollment Form Page** (`/enroll`)
   - 11 fields (no M-Pesa code)
   - Zone self-assessment with descriptions
   - Situation/goals textareas
   - Emotional baseline dropdown

3. **M-Pesa Submit Page** (`/mpesa-submit`)
   - Single field: M-Pesa code
   - Email parameter (pre-filled)
   - Tutorial link embedded

4. **Tutorial Pages:**
   - `/discord-setup` (embedded video)
   - `/m-pesa-payment` (embedded video or screenshots)

### **Backend (API endpoints):**

1. **POST /api/interest**
   - Writes to Google Sheets (Student Roster)
   - Sends Discord invite email
   - Returns success/error

2. **POST /api/enroll**
   - Writes to Google Sheets (Student Roster)
   - Sends payment instructions email
   - Triggers KIRA confirmation DM
   - Returns success/error

3. **POST /api/mpesa-submit**
   - Finds row by email in Google Sheets
   - Updates M-Pesa code + Payment Status
   - Sends confirmation email
   - Triggers KIRA payment notification

### **Google Sheets:**

1. **Student Roster tab**
   - Columns A-O defined above
   - Data validation on dropdowns
   - Conditional formatting for Payment Status

2. **Apps Script**
   - onEdit trigger (watches Payment Status column)
   - activateStudent() function
   - External API calls (Discord bot, email service)

### **CIS Discord Bot:**

1. **Event handlers:**
   - on_member_join (welcome DM)
   - on_message (track channel visits for onboarding)

2. **KIRA systems:**
   - OnboardingFlow class
   - Payment notification system
   - Activation DM system

3. **Role management:**
   - upgradeDiscordRole() function
   - Cluster assignment logic

### **Email Templates:**

1. Discord invite email
2. Payment instructions email
3. M-Pesa code received email
4. Activation email

### **Database (SQLite):**

1. **New columns for students table:**
   - All 17 columns from context-engine-experience-design.md
   - discord_username (linking field)
   - preloaded (boolean)
   - orientation_completed (boolean)

2. **Pre-load script:**
   - preload_students.py called by Apps Script
   - Reads from Google Sheets
   - Writes to cis-discord-bot/cohort-1.db

---

## AUTOMATION ROADMAP

### **Cohort 1 (Current): Manual Payment Verification**

- Trevor manually checks M-Pesa app
- Updates Google Sheets dropdown
- Apps Script triggers activation
- **Effort:** ~2 minutes per student

### **Cohort 2 (Semi-Automated):**

**Apps Script + M-Pesa API:**

```javascript
function checkPayments() {
    var sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName("Student Roster");
    var data = sheet.getDataRange().getValues();

    for (var i = 1; i < data.length; i++) {
        var row = data[i];
        var paymentStatus = row[11]; // Column L
        var mpesaCode = row[10]; // Column K

        if (paymentStatus === "Pending" && mpesaCode) {
            // Call M-Pesa API to verify
            var transaction = verifyMpesaTransaction(mpesaCode);

            if (transaction.valid && transaction.amount === 5000) {
                sheet.getRange(i + 1, 12).setValue("Confirmed");
                // Trigger fires automatically
            } else if (transaction.invalid) {
                sheet.getRange(i + 1, 12).setValue("Failed");
                sheet.getRange(i + 1, 13).setValue(transaction.reason);
                // Alert Trevor
            }
        }
    }
}

// Run every 15 minutes
ScriptApp.newTrigger('checkPayments')
    .timeBased()
    .everyMinutes(15)
    .create();
```

- **Effort:** ~30 seconds per day (review exceptions only)
- **Trevor only handles:** Failed payments, edge cases

### **Cohort 3+ (Fully Automated):**

- M-Pesa API integration for instant verification
- Auto-confirmation on valid payment
- Trevor only gets alert emails for exceptions
- **Effort:** ~5 minutes per day (review alerts)

---

## APPENDIX: Decision Log

**Decision 1: Discord Username Collection**
- **Initial design:** REQUIRED field in enrollment form
- **Problem identified:** Blocks 60% of users (teachers, entrepreneurs, professionals without Discord)
- **Solution:** Capture automatically via `on_member_join` event. Embedded as URL param in enrollment form link so the form backend can write it to Sheets.
- **Impact:** Eliminates major signup friction. No form field needed.
- **Status:** âœ… Confirmed 2026-03-04 (adversarial review 2)

**Decision 2: Form Progression**
- **Initial design:** Single 12-field form
- **Problem:** Too many fields upfront
- **Solution:** Split into 2 forms (3 fields â†’ 10 fields, now 10 not 11 â€” discord_username removed)
- **Impact:** Higher conversion rate
- **Status:** âœ… Confirmed

**Decision 3: Payment Flow Order**
- **Initial design:** Form includes M-Pesa code field
- **Problem:** Can't submit code before getting payment instructions
- **Solution:** Enrollment â†’ Payment email â†’ Separate M-Pesa submit form (token-based URL)
- **Impact:** Logical flow, less confusion, secure
- **Status:** âœ… Confirmed + token security fix applied 2026-03-04

**Decision 4: Payment Verification Method**
- **Cohort 1:** Manual (Trevor checks each payment in Google Sheets, aided by KIRA payment queue dashboard)
- **Cohort 2:** Semi-automated (Apps Script + M-Pesa API)
- **Cohort 3+:** Fully automated (API only)
- **Rationale:** Start simple, automate based on volume
- **Status:** âœ… Confirmed

**Decision 5: Post-Activation Onboarding**
- **Chosen approach:** KIRA-guided sequential DM flow with intent matching (not exact keyword)
- **Alternative considered:** Email-only with links
- **Rationale:** Higher engagement, personalized, builds KIRA rapport
- **Update 2026-03-04:** Stop 2 (public intro post) made optional. Timeout extended to 7 days. `/onboarding` re-entry command added.
- **Status:** âœ… Confirmed with updates

**Decision 6: Discord Role System**
- **Design:** @Guest (before payment) â†’ @Student (after payment)
- **Channels hidden from @Guest:** All program channels, bot commands
- **Impact:** Creates "moment of delight" when channels unlock
- **Status:** âœ… Confirmed

**Decision 7: Form Technology**
- **Decision:** Custom web forms at `/join`, `/enroll`, `/mpesa-submit` â€” NOT Google Forms
- **Rationale:** Custom forms allow URL parameter pre-filling, token-based M-Pesa submit, duplicate detection, and integration with the landing site
- **Status:** âœ… Confirmed 2026-03-04 (adversarial review 2)

**Decision 8: Cluster Assignment**
- **Decision:** Option F â€” Stratified diversity auto-assignment + Trevor override
- **Status:** âœ… CONFIRMED 2026-03-04
- **Algorithm:**
  - Target cluster size: 6â€“8 students
  - Cluster count: `ceil(total_enrolled / 7)`, max 8 (matches @Cluster-1 through @Cluster-8 Discord roles)
  - Assignment order: sort enrolled students by profession â†’ within each profession, sort by zone â†’ assign round-robin across clusters
  - Goal: every cluster gets a spread of professions and zones
  - Late joiners: assigned to the cluster with fewest members at time of activation
- **Trevor override:**
  - Trevor sees all cluster assignments in #facilitator-dashboard before Discord invites go out
  - Command: `/move-cluster @Student [cluster_number]` â€” bot reassigns role, updates SQLite, confirms in dashboard
  - No time limit on override â€” can adjust anytime during Week 1
- **Column U:** No longer a Sheets formula. Written by `preload_student()` webhook at activation time.
- **Activation email:** Now includes cluster field â€” unblocked.

**Cluster assignment Python (in preload_students.py):**

```python
def assign_cluster(students: list[dict]) -> list[dict]:
    """
    Stratified diversity assignment.
    Input: list of student dicts with 'profession' and 'zone'.
    Output: same list with 'cluster_id' populated (1-indexed).
    """
    # Sort: profession alphabetically, then zone ascending (1=newest, get variety)
    sorted_students = sorted(students, key=lambda s: (s.get('profession', ''), s.get('zone', 1)))

    cluster_count = max(1, min(8, math.ceil(len(sorted_students) / 7)))

    # Round-robin assignment
    for i, student in enumerate(sorted_students):
        student['cluster_id'] = (i % cluster_count) + 1  # 1-indexed

    return sorted_students


def assign_cluster_single(new_student: dict, db_conn) -> int:
    """
    Assign a late-joining student to the cluster with fewest members.
    """
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT cluster_id, COUNT(*) as size
        FROM students
        WHERE cluster_id IS NOT NULL
        GROUP BY cluster_id
        ORDER BY size ASC
        LIMIT 1
    """)
    row = cursor.fetchone()
    return row['cluster_id'] if row else 1
```

**Decision 9: Apps Script role upgrade method**
- **Decision:** Apps Script calls bot webhook with `discord_id` (numeric snowflake), not `discord_username`
- **Rationale:** discord_username is no longer in the form. discord_id is written to Column D by the bot at `on_member_join` time.
- **Failure handling:** If discord_id missing at activation time (student hasn't joined Discord yet), row is flagged in Column M and Trevor is alerted. No silent failures.
- **Status:** âœ… Confirmed 2026-03-04

---

## GOOGLE SHEETS COLUMN MAP (Updated)

| Column | Field | Written by | Notes |
|--------|-------|-----------|-------|
| A | First Name | /api/interest form | |
| B | Last Name | /api/enroll form | Used for cluster (Decision 3 closed: Option F stratified assignment) |
| C | Email | /api/interest form | Primary lookup key |
| D | Discord ID + Username | Bot (`on_member_join`) | Bot writes `discord_id|discord_username`. Never from form. |
| E | Profession | /api/interest form | Structured dropdown |
| F | Zone | /api/enroll form | Self-assessed (1-4) |
| G | Situation | /api/enroll form | Freeform |
| H | Goals | /api/enroll form | Freeform |
| I | Emotional Baseline | /api/enroll form | Structured dropdown with labels |
| J | Parent Email | /api/enroll form | Conditional |
| K | M-Pesa Code | /api/mpesa-submit | Submitted by student |
| L | Payment Status | Manual (Trevor) / Apps Script | Lead â†’ Enrolled â†’ Pending â†’ Confirmed / Failed |
| M | Notes | Apps Script (errors) | Activation error log |
| N | Created At | /api/interest | Auto-timestamp |
| O | Activated At | Apps Script | Set on successful activation |
| P | Submit Token | /api/enroll | Short-lived token for M-Pesa submit URL |
| Q | Token Expiry | /api/enroll | 7 days from enrollment |

---

*Document prepared by Party Mode Session*
*Contributors: PM John, UX Designer Sally, Architect Winston, Business Analyst Mary, Problem Solver Dr. Quinn*
*Date: 2026-03-04*
*Updated: 2026-03-04 â€” Adversarial review 2 fixes applied (Maya + Dev + Winston + CIS Team)*
*Status: âœ… UPDATED â€” canonical onboarding/payment contract (implementation tracked in sprint tasks 0.7a-0.7d)*


