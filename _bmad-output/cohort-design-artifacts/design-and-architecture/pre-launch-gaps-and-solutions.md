# K2M Cohort 1 — Pre-Launch Gaps & Solutions
**Date:** 2026-02-20
**Session:** Dev Agent (Amelia) + PM (Priya) + Architect (Kai) + CIS Council
**Status:** ACTIONABLE — gaps identified, solutions designed, ready to execute

---

## Overview

This document captures every gap identified in a deep-review session on 2026-02-20,
covering the final sprint of K2M Cohort 1 infrastructure. Each gap includes:
- What was designed vs what exists
- Root cause
- Recommended solution
- Who does what
- Effort estimate

Sprint is currently at **61% complete (30/49 tasks)**. These gaps are
**pre-launch blockers** — they must be resolved before students are invited.

---

## GAP 1: Google Forms — Not Yet Created

### What Was Designed
Story 5.4 is a complete, adversarial-reviewed spec for the student onboarding
diagnostic form. All 8 acceptance criteria met. 100% guardrail compliance.

### What Exists
The specification only. The actual Google Form has not been created.

### Root Cause
Story 5.4 is a design spec, not a dev task. Creating the form is a manual
Trevor action, not something the bot can build.

### Solution
**Trevor creates the Google Form manually** using the spec at:
`_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-4-google-forms-diagnostic.md`

**Steps:**
1. Go to forms.google.com → Create new form
2. Follow the 6-section structure in the spec exactly:
   - Section 0: Age verification
   - Section 1: Basic info (name, email, last name for cluster)
   - Section 2: Zone self-assessment + scenario verification
   - Section 3: Emotional baseline (all optional)
   - Section 4: Goals & expectations (optional)
   - Section 5: Parent/guardian contact (required)
   - Section 6: Consent & weekly updates
3. Set confirmation message to include Discord invite link + display name instruction
4. Link form to Student Roster sheet (Forms → Responses → Link to Sheets)
5. Add M-Pesa payment field to Section 5 (see Gap 3)

**Effort:** 60–90 minutes (Trevor)
**Blocker for:** Everything else (no students can join without the form)

---

## GAP 2: Cluster Assignment Uses Discord Display Name (Not Real Name)

### What Was Designed
Cluster assignment by last name (A-F, G-L, M-R, S-Z) per Story 5.1.
The design assumed the bot would know the student's real last name.

### What Exists
`main.py:754` — the bot extracts "last name" from Discord display name:
```python
last_name = display_name.split()[-1] if display_name else None
```
If a student's Discord name is "techkid_254", their cluster is wrong.

### Root Cause
There is no bridge between Google Form (real name) and Discord (display name).
The bot has no access to Sheets data. This was a Decision 7 (manual workflow) gap
that was never explicitly resolved.

### Solutions (Ranked)

**Option A — Immediate, no code (Cohort 1):**
In the Google Form confirmation message and Email #2 ("You're IN"), include:
> "IMPORTANT: Set your Discord display name to your full real name
> (e.g., 'John Kamau') before joining the server."

Add to #welcome channel as pinned message. Trevor uses `/assign-cluster`
override for any mismatches caught during diagnostic review.

**Option B — Quick code fix (1 day, recommended for Cohort 1):**
Add `/register` slash command:
```
/register last_name:Kamau
```
Student types this after joining. KIRA updates their last name in SQLite
and reassigns their cluster role automatically.

**Option C — Full integration (Cohort 2):**
Google Sheets → bot pre-load script. Trevor runs it after reviewing diagnostics.
Pre-populates SQLite with real names before students join Discord.

**Recommended:** Option A + Option B together.
**Effort:** Option A = 5 min (Trevor) | Option B = 1 day (Amelia)

---

## GAP 3: No Automated Student Signup Journey

### What Was Designed
Decision 7 (Manual Workflows) explicitly scoped this as manual for Cohort 1.
Trevor sends Discord invite links manually after reviewing diagnostics.

### What Exists
The current flow:
```
Student fills form → Sheets (auto) → Trevor reviews (manual, 4-5 hours)
→ Trevor sends Discord invite (manual, per student) → Student joins
→ Bot takes over (automated)
```

For 200 students, manually sending invite links is unsustainable.

### Solution — Zero-Code Fix (Immediate)

**Put the Discord invite link in the Google Form confirmation screen:**
```
"Thanks for sharing! Next steps:
 1. Join the Discord server: discord.gg/[your-invite]
 2. Set your Discord name to your FULL NAME (e.g., 'John Kamau')
 3. Check #welcome for orientation
 Week 1 starts [DATE]!"
```

Google Forms sends this as an automatic confirmation email too.
Cost: $0. Time: 5 minutes.

### Solution — Automated Pipeline (Phase 2, ~2 days)

**Stack:** Google Apps Script + Brevo (free tier, 300 emails/day)
**Trevor's custom domain emails:** Supported natively in Brevo.

**Flow:**
```
Form submitted → Apps Script triggers → Brevo sends Email #1 (Spot Reserved)
     ↓
Trevor marks "Confirmed" in Sheets dropdown
     ↓
Apps Script detects change → Brevo sends Email #2 (You're IN + Discord invite)
     ↓
Student joins Discord → KIRA welcome DM fires
```

**Email sequence (5 branded emails, Trevor's custom domain):**

| # | Trigger | Subject |
|---|---------|---------|
| 1 | Form submitted | "Your K2M spot is reserved, [Name]" |
| 2 | Trevor confirms payment | "Welcome to K2M Cohort #1, [Name] 🎉" |
| 3 | 24h before Week 1 | "Tomorrow is Day 1 — here's what to expect" |
| 4 | Friday Week 1 | "You made it through Week 1, [Name]" |
| 5 | Artifact published | "Your thinking is now visible to the world" |

**Effort:** Brevo setup 30 min (Trevor) | Apps Script 1 day (Amelia) | Email templates 3-4 hrs (Trevor content)

---

## GAP 4: M-Pesa Payment Gate Not Built

### What Was Designed
Not in the original design. Trevor identified this as a requirement:
students must confirm M-Pesa payment before receiving access.

### What Was Decided
M-Pesa verification stays **manual** (Trevor verifies codes).
Everything else (email delivery, Discord invite) gets automated around it.

### Solution

**In Google Form — add to Section 5:**
```
"Complete your registration:
 Send [KES XXXX] to M-Pesa Till: [XXXXX] (K2M EdTech)
 Reference: Your first name + last name (e.g., JohnKamau)

 Enter your M-Pesa confirmation code: [ _______________ ]

 Your spot is confirmed once Trevor verifies payment (within 24 hours)."
```

**In Google Sheets — add two columns:**
- Column AC: M-Pesa Code (auto-populated from form)
- Column AD: Payment Status (Trevor dropdown: Pending / Confirmed / Failed)

**Automation trigger:** Apps Script watches Column AD.
When Trevor changes to "Confirmed" → Email #2 fires automatically.

**Effort:** Form field 5 min | Sheets columns 10 min | Apps Script trigger 2 hours (Amelia)

---

## GAP 5: Discord Onboarding UX — Students Don't Know What To Do

### What Exists
Current KIRA welcome DM (main.py:804):
```
"👋 Welcome to K2M Cohort #1, {display_name}!
 You're in Cluster {cluster_id}
 📅 Cluster session: {schedule}
 🎯 What to do now:
 1. Introduce yourself in #week-1-wonder
 2. Check your daily prompts at 9:15 AM EAT
 3. Use /frame when you have a question
 — KIRA"
```

### The Problem
- 15 channels visible, no map of what they're for
- "Use /frame when you have a question" assumes students know what /frame is
- No immediate action that feels safe and easy
- Students join at unpredictable times (not just Monday 9 AM)

### Solution — Upgraded KIRA Welcome DM

Replace the current welcome message with:

```
Hey [FirstName]! I'm KIRA — your thinking partner for the next 8 weeks.

You're in Cluster [X] (sessions: [schedule])

📍 YOUR MAP — 5 channels, that's all you need:
  #week-1-wonder    → Post here daily. This is your main feed.
  #thinking-lab     → Private space to think WITH me (/frame)
  #thinking-showcase → Where finished thinking gets celebrated
  #resources        → Everything you need, always here
  #welcome          → If you feel lost, start here

🎯 YOUR FIRST STEP (takes 2 minutes):
Go to #thinking-lab and type:
  /frame I want to [your goal from the form]

I'll respond in a private DM — nobody else sees it.
That's it. You've started.

— KIRA
```

**Additional UX improvements:**

1. **Discord Native Server Onboarding** (Trevor configures, no code):
   - Welcome screen with K2M branding
   - 3-step checklist: "Read #welcome ✓" "Introduce yourself ✓" "Try /frame ✓"
   - Channel access gated until checklist complete

2. **Trevor's Day 1 seed post** (Trevor posts manually before students wake up):
   ```
   "I'll go first: I just realized I use AI when...
    Google Maps reroutes me around traffic without me asking.
    That's AI deciding on my behalf. Wild.
    — Trevor"
   ```

3. **Loom video** (Trevor records 3 min, pins in #welcome):
   "You're in. Watch this first." — answers every "what do I do?" question.

**Effort:** Welcome DM upgrade 2 hours (Amelia) | Discord onboarding config 30 min (Trevor) | Loom 30 min (Trevor)

---

## GAP 6: KIRA Contextual Coaching — Proactive Journey DMs Missing

### What Exists
KIRA is mostly **reactive** (student acts → KIRA responds) or **scheduled**
(9 AM prompts, escalation nudges, week unlock announcements).

### What's Missing — Proactive DMs at Journey Junctures

| Juncture | Trigger | What KIRA Should Send |
|----------|---------|----------------------|
| First /frame used | Student completes first session | "That was Habit 1 in action. Here's what I noticed..." |
| First share to showcase | Student shares publicly | "Your thinking is now visible. Here's what's next..." |
| Week N unlock | Saturday unlock fires | "Week [N] is about [theme]. Here's one thing to watch for..." |
| /diverge + /challenge unlock (Week 4) | Week 4 starts | "Two new thinking partners just unlocked. Here's when to use each..." |
| /synthesize + /create-artifact unlock (Week 6) | Week 6 starts | "Time to start your artifact. Here's what it looks like..." |
| Artifact creation started | /create-artifact first used | "Section 1 of 6. Here's how to approach it..." |
| Artifact published | /publish completes | "Your thinking is permanent now. Graduation DM..." |

### Solution — Task 5.8: KIRA Contextual Coaching

New sprint task covering all 7 missing juncture DMs.

**Design pattern (same structure for all):**
```
TRIGGER fires
  → KIRA DMs student
  → 3 elements: Context | What to do now | What's coming next
  → One clear action (never a list of options)
```

**Effort:** 1.5 days (Amelia) — implement all 7 juncture DMs + tests

---

## GAP 7: Pre-Cohort Content Never Created

### What Was Referenced
The #resources channel (loaded by setup script) contains placeholder links to:
- `[Complete Cohort Guide]` — Notion/PDF
- `[The 4 Habits Guide]` — one-pager
- `[CIS Agent Guide]` — how to use /frame, /diverge, /challenge, /synthesize
- `Artifact Examples` — sample completed artifacts
- `NotebookLM Podcasts` — 16 nodes

### What Exists
The channel structure and placeholder text. The actual content behind those links
does not exist.

### The Cohort 1 Problem
Since this is Cohort 1, there are no real previous student examples.
Everything must be fabricated but realistic before students arrive.

### Solution — Content Trevor Must Create Before Launch

**1. CIS Agent Guide** (Trevor writes, ~2 hours)
```
When to use each agent:
  /frame    → You have a fuzzy question in your head (Week 1+)
  /diverge  → You're stuck on one way of thinking (Week 4+)
  /challenge → You want to stress-test your idea (Week 4+)
  /synthesize → You want to pull your thinking together (Week 6+)

[Example /frame conversation — 5 realistic turns]
[Example /diverge conversation — 3 turns]
[Example /challenge conversation — 3 turns]
[Example /synthesize conversation — 3 turns]
```
Post to: Notion page linked from #resources

**2. Two Example Artifacts** (Trevor writes, ~3 hours)
```
Artifact A — "Developing" quality:
  Student: Brian | Zone 1→2 | Topic: Choosing between two university courses
  Shows: Basic use of 2/4 habits, honest reflection, clear personal voice

Artifact B — "Strong" quality:
  Student: Amina | Zone 2→3 | Topic: AI in university application decisions
  Shows: All 4 habits visible, identity shift clear, structured thinking
```
Post to: #thinking-showcase BEFORE cohort opens
Label: "From our pilot students — examples of what's possible"

**3. 4 Habits Quick Reference Card** (Trevor designs, ~1 hour)
One-image or one-page PDF showing all 4 habits with one-sentence explanations.
Pinned in #resources and sent in Email #2.

**4. Trevor's Day 1 Seed Post** (Trevor writes, 5 minutes)
Posts in #week-1-wonder before students wake up to model the behavior.

**5. Complete Cohort Guide** (Trevor writes or repurposes playbook, ~2 hours)
Week-by-week breakdown. Can be the playbook excerpts compiled into a Notion page.

**Total Trevor content effort:** ~8 hours before launch

---

## Summary: What Gets Built vs What Trevor Does

### Amelia (Dev) Builds:
| Task | Sprint ID | Effort |
|------|-----------|--------|
| /register command (last name fix) | New Task 5.8a | 1 day |
| Upgraded KIRA welcome DM | New Task 5.8b | 2 hours |
| Apps Script automation (form → email triggers) | New Task 0.7 | 1 day |
| M-Pesa column + payment status trigger | New Task 0.7 | 2 hours |
| KIRA contextual coaching (7 juncture DMs) | New Task 5.8c | 1.5 days |
| Bot pre-load from Sheets (Cohort 2) | Backlog | — |

### Trevor Does:
| Task | Effort |
|------|--------|
| Create Google Form (Story 5.4 spec) | 60-90 min |
| Set up Brevo account + custom domain | 30 min |
| Write 5 branded email templates | 3-4 hours |
| Configure Discord Server Onboarding | 30 min |
| Record Loom welcome video | 30 min |
| Write CIS Agent Guide | 2 hours |
| Write 2 example artifacts | 3 hours |
| Design 4 Habits quick reference card | 1 hour |
| Write Day 1 seed post | 5 min |
| Write Complete Cohort Guide | 2 hours |
| **Total Trevor pre-launch content** | **~13 hours** |

---

## Suggested New Sprint Tasks

Add these to `discord-implementation-sprint.yaml`:

```yaml
- id: "0.7"
  title: "Student onboarding automation (Apps Script + Brevo)"
  status: "pending"
  description: |
    - Google Sheets: Add M-Pesa code column + Payment Status dropdown
    - Apps Script: Form submission → Brevo Email #1 (Spot Reserved + M-Pesa)
    - Apps Script: Payment confirmed → Brevo Email #2 (You're IN + Discord invite)
    - Apps Script: Sunday before Week 1 → Brevo Email #3 (Week 1 preview)
    - Pre-load student real name into SQLite from Sheets before join
  effort: "1.5 days"

- id: "5.8"
  title: "Discord UX hardening + KIRA contextual coaching"
  status: "pending"
  description: |
    - Upgrade KIRA welcome DM (map + first action)
    - Add /register command (last name + cluster reassignment)
    - Implement 7 proactive juncture DMs (post-/frame, week unlocks,
      agent unlocks, post-publish graduation)
    - Update #resources channel with real content links
  effort: "2.5 days"
```

---

## Pre-Launch Checklist (For Trevor)

```
CONTENT (Trevor):
[ ] Google Form created and tested (Story 5.4 spec)
[ ] M-Pesa field added to form
[ ] Form linked to Student Roster sheet
[ ] Discord invite in form confirmation message
[ ] Brevo account set up, custom domain verified
[ ] 5 email templates written and tested in Brevo
[ ] Discord Server Onboarding configured (welcome screen + checklist)
[ ] Loom welcome video recorded and linked in #welcome
[ ] CIS Agent Guide written (Notion page)
[ ] 2 example artifacts written and posted to #thinking-showcase
[ ] 4 Habits quick reference card created
[ ] Complete Cohort Guide compiled (Notion page)
[ ] All #resources links updated to real content
[ ] Day 1 seed post written and ready to copy-paste

CODE (Amelia):
[ ] KIRA welcome DM upgraded
[ ] /register command implemented and tested
[ ] Apps Script automation built and tested
[ ] KIRA contextual coaching DMs implemented
[ ] Task 4.6 (parent email) completed
[ ] Tasks 5.4, 5.5, 5.6, 5.7 completed (remaining Sprint 5)

LAUNCH GATE:
[ ] All above complete
[ ] Bot live on Railway (Task 5.7)
[ ] Trevor has all credentials
[ ] Student invite link ready
[ ] Go/no-go decision made
```

---

*Document created by Dev Agent (Amelia) — 2026-02-20*
*Based on session with Trevor covering sprint gaps, architecture review, and CIS design council*
