# K2M EdTech System Documentation

> Living documentation of the KIRA Discord bot and K2M EdTech platform.
> Generated from brownfield code analysis — reflects actual runtime behaviour, not aspirational design.
> Last updated: 2026-03-17

---

## Documents

| Document | Audience | Description |
|----------|----------|-------------|
| [01 — System Overview](./01-system-overview.md) | Everyone | What this system is, how the two apps connect, tech stack |
| [02 — Student Journey](./02-student-journey.md) | Facilitators, Team | Enrollment → onboarding → 8 weeks → graduation |
| [03 — Facilitator Guide](./03-facilitator-guide.md) | Facilitators | What KIRA escalates to you, your dashboard, how to intervene |
| [04 — Super Admin & Ops](./04-super-admin-ops.md) | Trevor | Deployments, env vars, DB, scheduler, budget controls |
| [05 — Under the Hood](./05-under-the-hood.md) | Tech team | State machine, scheduler, safety filter, context engine, escalation |
| [06 — Observability](./06-observability.md) | Trevor, Tech team | What gets logged, where errors surface, how to find what went wrong |

---

## Quick Reference

**KIRA is running on:** Railway (bot) + PostgreSQL (database)
**Landing page is on:** Vercel (Next.js)
**AI Provider:** OpenAI `gpt-4o-mini` (swappable via `AI_PROVIDER` env var)
**Cohort timing:** Set via `COHORT_1_START_DATE` env var
**Context engine:** Google Apps Script webhook (see CLAUDE.md for deployment rules)

**To run tests:** `pytest cis-discord-bot/tests/ -q`
**Env var reference:** `cis-discord-bot/.env.template`
