# Onboarding + Context Canonical V3
**Program:** K2M Cohort 1  
**Effective date:** 2026-03-04  
**Status:** Canonical merged contract for enrollment, onboarding, context, and Sprint execution

---

## 1. Purpose
This document resolves conflicts across:
- `student-onboarding-and-enrollment-flow.md`
- `context-engine-experience-design.md`
- `discord-implementation-sprint.yaml`
- Session 3 and Session 4 pre-mortem decision logs

Use this as the first source when documents disagree.

---

## 2. Precedence
When conflicts exist, apply this order:
1. This Canonical V3 document
2. `discord-implementation-sprint.yaml` for task status and acceptance criteria
3. `student-onboarding-and-enrollment-flow.md` for journey detail
4. `context-engine-experience-design.md` for personalization detail
5. `discord-community-culture-and-architecture.md` for channel/culture behavior

---

## 3. Resolved Conflicts
1. **Identity match key**
   - Canonical: unique per-student Discord invite links.
   - Storage: Column R = `invite_code`.
   - `on_member_join` linkage uses `invite_code`.
2. **Intermediary 6-digit link token**
   - Canonical: deprecated for Cohort 1 production.
   - Historical references remain for audit only.
3. **Stage 1 entry**
   - Canonical: landing page form is Stage 1.
   - `/join` slash command removed from bot path.
4. **KIRA pre-join messaging**
   - Canonical: pre-join messaging is Brevo-only.
   - KIRA DMs start after successful `on_member_join` linkage.
5. **Stop 0 sequencing**
   - Canonical: value-first order.
   - Order: Stop 1 -> Stop 2 -> Stop 3 -> Stop 0 -> Stop 4+.
6. **Storage engine**
   - Canonical: PostgreSQL runtime storage.
   - SQLite references are legacy and non-authoritative.
7. **Forms**
   - Canonical: custom web forms (`/join`, `/enroll`, `/mpesa-submit`), not Google Forms.

---

## 4. Canonical Journey Contract
1. Interest form (`/api/interest`) appends row, generates unique invite, stores `invite_code`, sends Brevo Email #1.
2. Student joins Discord via invite link, `on_member_join` resolves student, writes identity bridge to Column D.
3. Enrollment form (`/api/enroll`) captures profile details and emits payment instructions with tokenized submit URL.
4. Payment submit (`/api/mpesa-submit`) records code, sets queue state, sends immediate confirmation comms.
5. Facilitator verifies payment, activation pipeline upgrades role and preloads profile to PostgreSQL.
6. Onboarding starts in Discord with Stops 1-3, then Stop 0 contextual profile DM.

---

## 5. Canonical Sprint Execution Order
Run this sequence for production readiness:
1. `7.0` launch-date/environment gate
2. `7.6` PostgreSQL production migration
3. `7.1` Stage 1 redesign and cap/waitlist behavior
4. `7.2` unique invite linkage and recovery path
5. `7.3` DM architecture gating (Brevo pre-join, KIRA post-join)
6. `7.11` webhook auth (HMAC)
7. `7.4` token lifecycle and renew path
8. `7.5` payment feedback and unverifiable handling
9. `7.7` Stop 0 + onboarding intent safeguards + re-entry
10. `7.8` bot reliability and operational alerts
11. `7.10` KIRA DM copy/progress redesign
12. `7.12` `#welcome-lounge` waiting-room UX
13. `7.13` Brevo domain/auth setup
14. `7.14` Brevo templates
15. `7.9` drop-off recovery emails
16. `7.15` deliverability validation
17. `7.16` end-to-end smoke test
18. Rebased Sprint 6 tasks: `6.1 -> 6.2 -> 6.3 -> 6.4 -> 6.7 -> 6.5` (`6.6` is superseded by `7.6`)

---

## 6. Superseded and Rebased Items
1. `sprint_0_7_patch.0.7.1` intermediary token path is superseded by `7.2`.
2. `sprint_6.6` PostgreSQL preparation is superseded by `7.6` full migration.
3. Any SQLite-specific runtime requirement in design docs is superseded by PostgreSQL contract.
4. Any Stop 0 sequence placing Stop 0 before Stop 1 is superseded by value-first order.

---

## 7. Open Item
`COHORT_1_FIRST_SESSION_DATE` is still not locked. This must be set before final Brevo template publish and final launch smoke test.
