# K2M EdTech Program — Agent Instructions

This file is loaded automatically by every Claude agent working in this repository.
Read it fully before taking any action involving infrastructure, deployments, or environment variables.

---

## Apps Script Deployment Rules (CRITICAL)

**NEVER use `clasp deploy --deploymentId <id>` to update an existing Web app deployment.**

Doing so silently resets the deployment type from "Web app" back to "Library" and revokes public access. This breaks the context engine webhook and requires Trevor to manually recreate the deployment via the UI.

### Correct workflow for Apps Script code changes:

1. `clasp push -f` — push updated Code.gs to HEAD
2. `clasp version "description"` — create a new saved version
3. **Stop here.** Do NOT run `clasp deploy` against the Web app deployment ID.
4. The existing Web app deployment automatically serves the latest pushed code once the version is pointed to it — OR Trevor updates the version via the Apps Script UI (Deploy → Manage deployments → Edit → select new version → Save).

### Web app deployment settings (must be preserved):
- **Execute as:** Me (Trevor's account)
- **Who has access:** Anyone
- **Type:** Web app (not Library, not API executable)

### Current live Web app URL (context engine):
```
CONTEXT_ENGINE_WEBHOOK_URL=https://script.google.com/macros/s/AKfycbxJjQz00JTa6RXkU2LmWKG8cn-VaKy78HAG3bvdfUE0ubYMwFGxYxeGOuZkRR85BQ5VZA/exec
```
If this URL stops working, Trevor must create a NEW Web app deployment via the UI and share the new `/macros/s/.../exec` URL. Never try to fix it by running `clasp deploy`.

---

## Context Engine

- Token auth: `CONTEXT_ENGINE_WEBHOOK_TOKEN` in `.env` must match `CONTEXT_WEBHOOK_TOKEN` in Apps Script Script Properties.
- Actions available via `doPost`: `getStudentContext`, `getExamplesByProfession`, `getIntervention`, `seedContextLibraryContent`, `ensureContextLibraryTabs`, `reviewOpsSheetHealth`, `repairOpsSheetHealth`.
- `seedContextLibraryContent` is idempotent — safe to call multiple times; skips if data rows already present.
- Sheets are bound to spreadsheet `16tLQbGUF9mI2z2cHxlwmGce6Npui0C5w8e1y46uanH0`.

---

## Environment Variables

- `.env` is the local dev env file. Railway holds production env vars.
- `.env.template` is the canonical reference for all supported variables — keep it in sync when adding new vars.
- Never commit `.env` to git.

---

## Bot Runtime

- Discord bot (KIRA) runs on Railway.
- AI provider: OpenAI (`gpt-4o-mini`). Swap via `AI_PROVIDER` env var without code changes.
- Python project root: `cis-discord-bot/`
- Run tests: `pytest cis-discord-bot/tests/ -q`
- Sprint tracker: `_bmad-output/cohort-design-artifacts/operations/sprint/discord-implementation-sprint.yaml`
