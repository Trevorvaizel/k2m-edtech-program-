# Technical Debt Register (Sprint Execution)

## TD-7.13-01 - Deferred Email #1 Discord Orientation Screenshot Asset

- **Date logged:** 2026-03-11
- **Source task:** 7.13 (Brevo account setup + domain authentication)
- **Status:** Closed (resolved in task 7.14 on 2026-03-11)
- **Owner:** Trevor
- **Scope:** `cis-discord-bot/assets/email/email-1/discord-orientation-annotated.png`
- **Reason for deferral:** Infrastructure-critical work for task 7.13 is complete (domain/auth/sender/runtime/deliverability). The remaining item is a manual visual asset capture and annotation.
- **Risk:** Closed; mitigated by completed template embed.
- **Mitigation:** Completed in task 7.14.
- **Due milestone:** Completed before task 7.14 closeout.
- **Exit criteria:**
  1. [x] `discord-orientation-annotated.png` exists at the required path.
  2. [x] Labels are readable on mobile-width preview.
  3. [x] Asset is embedded in Brevo Email #1 template.

## TD-7.9-01 - WhatsApp Fallback Activation Deferred (Africa's Talking Access Pending)

- **Date logged:** 2026-03-12
- **Source task:** 7.9 (Stage 1->2 drop-off recovery emails)
- **Status:** Open
- **Owner:** Trevor
- **Scope:** Production activation of `send_stage1_whatsapp_nudge()` in `cis-discord-bot/cis_controller/interest_api_server.py`
- **Reason for deferral:** WhatsApp API access is not yet available in production (Africa's Talking onboarding/credentials not complete).
- **Risk:** If Email #1.5 fails with bounce-like errors, no automated WhatsApp recovery message is sent.
- **Mitigation:** Primary Brevo email path (#1.5/#1.75) is live and tested; manual facilitator WhatsApp outreach remains available.
- **Due milestone:** Before Sprint 7.15 final deliverability sign-off.
- **Exit criteria:**
  1. [ ] `AFRICAS_TALKING_WHATSAPP_URL` set in Railway.
  2. [ ] `AFRICAS_TALKING_API_KEY` set in Railway.
  3. [ ] `AFRICAS_TALKING_USERNAME` set in Railway.
  4. [ ] Live fallback verification captured in `task-notes/7.9.md` (with evidence command/output summary).

## TD-7.15-01 - Provider Inbox Classification Gap (Safaricom/Airtel/Yahoo)

- **Date logged:** 2026-03-12
- **Source task:** 7.15 (Brevo deliverability matrix)
- **Status:** Open
- **Owner:** Trevor
- **Scope:** Manual inbox-vs-spam classification and provider-specific matrix completion.
- **Reason for deferral:** No Safaricom/Airtel/Yahoo test inboxes are currently configured in the automation context.
- **Risk:** Launch-day provider placement risk remains unknown outside Gmail/domain mailbox checks.
- **Mitigation:** Automated event-level delivery proof exists for 21/21 sends to active Gmail + k2mlabs inboxes; manual fallback playbook remains active.
- **Due milestone:** Before Sprint 7.15 final sign-off and Sprint 7.16 final launch gate.
- **Exit criteria:**
  1. [ ] Execute all 7 template sends to Safaricom mailbox and record inbox/spam placement.
  2. [ ] Execute all 7 template sends to Airtel mailbox (if available) and record inbox/spam placement.
  3. [ ] Execute all 7 template sends to Yahoo mailbox and record inbox/spam placement.
  4. [ ] Append manual evidence to `task-notes/7.15.md`.

## TD-7.16-01 - Full Human Walkthrough Gap (Discord Join -> Stop 0 Completion)

- **Date logged:** 2026-03-12
- **Source task:** 7.16 (end-to-end smoke)
- **Status:** Open
- **Owner:** Trevor
- **Scope:** One complete human-in-the-loop production run from invite join through Stop 0 completion.
- **Reason for deferral:** Bot-side automation and live API/webhook probes are complete, but final happy-path proof requires a real Discord participant and facilitator payment-confirm step.
- **Risk:** Final UX/ops validation for join linkage, role transition, and onboarding DM progression remains unproven in one continuous production run.
- **Mitigation:** Live API smoke passed; webhook auth passed; 134 targeted tests passed including invite matching, preload, onboarding, token lifecycle, and failure paths.
- **Due milestone:** Before Sprint 7 launch go/no-go.
- **Exit criteria:**
  1. [ ] Real Discord invite join performed for a fresh test student and Column D linkage confirmed.
  2. [ ] Facilitator payment-confirm action executed for that row.
  3. [ ] `@Guest -> @Student` role change and activation DM confirmed for that student.
  4. [ ] Stops 1-3 and Stop 0 completed; runtime profile fields verified.
  5. [ ] Evidence appended to `task-notes/7.16.md`.
