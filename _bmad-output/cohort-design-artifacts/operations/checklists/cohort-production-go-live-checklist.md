# Cohort 1 Production Go-Live Checklist (Task 5.7)

## Purpose
Canonical runbook for Task 5.7 production deployment and launch gating.
This checklist is intentionally grounded in playbook-v2 and Story 5.1/5.6 operations guidance.

## Design Bible Anchors
- `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-1-discord-server-structure.md`
  - `Deployment Checklist (Per New Cohort)`
  - `Server Handoff to Trevor`
  - `Copy-Paste Server Template`
- `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-6-manual-sops.md`
  - `SOP 2: Daily & Weekly Monitoring Routine`
  - `SOP 3: Intervention Escalation Protocols`
  - `SOP 4: Crisis Management`
- `_bmad-output/cohort-design-artifacts/operations/sprint/discord-implementation-sprint.yaml`
  - Sprint 5 Task `5.7`

## Go-Live Gates (as of 2026-02-20)

| Gate | Status | Evidence | Required Next Action |
| --- | --- | --- | --- |
| Bot deployed to Railway (production) | READY | Project + service created, linked, and deployed successfully (`service: kira-bot`, latest deployment status `SUCCESS`) | Keep monitoring runtime logs post-launch |
| Environment variables set (production tokens, API keys) | READY | Railway service variables set for Discord, provider keys, channels, cohort metadata, and runtime commands | Maintain in Railway variables as source-of-truth |
| Database initialized (clean `cohort-1.db`) | READY | Persistent volume mounted at `/data`, runtime uses `DATABASE_PATH=/data/cohort-1.db`, startup logs show `Tracking 0 students` | Continue daily backups (`/data/cohort-1.backups`) |
| Monitoring dashboard accessible | READY | `python check_discord_health.py` passes (`10/10`), and production logs show health monitor started | Keep 5-minute health checks active |
| Trevor has all credentials (token, API key, Railway URL, DB location) | READY | Credential handoff block completed below with live links/locations | Rotate secrets through Railway vars as needed |
| Student invite link generated | READY | Invite generated: `https://discord.gg/eMFecMq2Vu` | Share with student onboarding flow |
| `#announcements` updated with cohort start date | READY | Go-live message posted by Kira in announcements channel (`message_id=1474366903098282090`) with start date `Friday, February 20, 2026` | Keep future cohort updates in same channel |
| All SOPs in Trevor's hands | READY | Story 5.6 SOP artifact exists and was runtime-reconciled by Task 5.1 | Use SOP 2/3/4 for daily operations |

## Execution Order (No Improvisation)

1. Authenticate and link Railway project.
   - `cmd /c railway login`
   - `cmd /c railway link`
2. Deploy production bot service.
   - `cmd /c railway up`
3. Verify post-deploy runtime health.
   - `python check_discord_health.py`
   - Confirm `/ping`, `/frame`, and facilitator dashboard alert path in Discord.
4. Perform clean DB cutover (backup first, then initialize empty runtime DB).
5. Generate student invite link and record it in handoff credentials.
6. Post launch announcement in `#announcements` with exact cohort start date.
7. Complete go/no-go check below.

## Clean DB Cutover Procedure (Backup-First)

1. Stop bot process.
2. Backup current DB:
   - `Copy-Item cohort-1.db \"cohort-1.pre-go-live.$(Get-Date -Format 'yyyyMMdd-HHmmss').db\"`
3. Initialize clean runtime DB:
   - `Move-Item cohort-1.db \"cohort-1.pre-go-live.latest.db\"`
   - `@'`
     `from database.store import DatabaseStore`
     `DatabaseStore(\"cohort-1.db\")`
     `print(\"Initialized clean cohort-1.db\")`
     `'@ | python -`
4. Re-run health check:
   - `python check_discord_health.py`

## Credential Handoff Block (Completed)

- Railway project URL: `https://railway.com/project/1e7e5680-e8d6-4502-8621-6368896ef2f7`
- Railway service URL: `https://railway.com/project/1e7e5680-e8d6-4502-8621-6368896ef2f7/service/da51510b-1606-4ca1-8543-da00fc2e1362`
- Discord bot token location: Railway service variable `DISCORD_TOKEN` (masked)
- Provider API key location: Railway service variable `OPENAI_API_KEY` (masked)
- Runtime DB path: `/data/cohort-1.db`
- Student invite URL: `https://discord.gg/eMFecMq2Vu`
- SOP reference: `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-6-manual-sops.md`

## Go / No-Go Decision

GO only when every gate above is `READY`.

Current decision state (2026-02-20): `GO`.
