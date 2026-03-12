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

## TD-7.9-01 - WhatsApp Bounce Fallback Deferred (Africa's Talking Access Pending)

- **Date logged:** 2026-03-12
- **Source task:** 7.9 (Stage 1->2 drop-off recovery emails)
- **Status:** Open
- **Owner:** Trevor
- **Scope:** Production fallback path for `send_stage1_whatsapp_nudge()` in `cis-discord-bot/cis_controller/interest_api_server.py`
- **Reason for deferral:** WhatsApp API access is not yet available (Africa's Talking onboarding/credentials not complete).
- **Risk:** If Email #1.5 fails with bounce-like errors, no automated WhatsApp recovery message is sent.
- **Mitigation:** Primary Brevo email path (#1.5/#1.75) is live and tested; manual facilitator WhatsApp outreach remains available.
- **Due milestone:** Before Sprint 7.15 final deliverability sign-off.
- **Exit criteria:**
  1. [ ] `AFRICAS_TALKING_WHATSAPP_URL` set in Railway.
  2. [ ] `AFRICAS_TALKING_API_KEY` set in Railway.
  3. [ ] `AFRICAS_TALKING_USERNAME` set in Railway.
  4. [ ] Live fallback verification captured in `task-notes/7.9.md` (with evidence command/output summary).
