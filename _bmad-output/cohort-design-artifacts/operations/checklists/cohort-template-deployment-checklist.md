# Cohort Template Deployment Checklist (Task 5.6)

## Purpose
Canonical runbook for spinning up a new K2M cohort server from the existing Discord template while staying aligned to playbook-v2 Story 5.1 "Copy-Paste Server Template".

## Source of Truth
- `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/5-1-discord-server-structure.md`
  - Section: `Copy-Paste Server Template`
  - Section: `Deployment Checklist (Per New Cohort)`
  - Constraint: `Time to Deploy: ~30 minutes (with template)`
- `_bmad-output/cohort-design-artifacts/operations/sprint/discord-implementation-sprint.yaml` (Task `5.6`)

## Template Artifact
- Template URL: `https://discord.new/Eqz6DMNHuVHU`
- Template code: `Eqz6DMNHuVHU`
- Creation path: `setup_discord_server.py` -> `create_server_template(guild)`

## 30-Minute Deployment Checklist

### 1. Copy server template (2 min)
- Open `https://discord.new/Eqz6DMNHuVHU`
- Create new server from template

### 2. Rename server (2 min)
- Server Settings -> Overview
- Rename to: `K2M Cohort #X - AI Thinking Skills`

### 3. Update cohort dates and announcements (5 min)
- Set cohort start date in run operations notes
- Post cohort start date in `#announcements`
- Confirm live-session schedule dates are current

### 4. Prepare cohort-specific bot runtime (8 min)
- In `cis-discord-bot`, create/update `.env` from `.env.template`
- Set at minimum:
  - `DISCORD_TOKEN`
  - `DISCORD_GUILD_ID` (new server ID)
  - `CHANNEL_THINKING_LAB`
  - `CHANNEL_THINKING_SHOWCASE`
  - `CHANNEL_FACILITATOR_DASHBOARD`
  - `CHANNEL_MODERATION_LOGS`
  - `COHORT_ID` (for example `cohort-2`)
  - `COHORT_START_DATE` (`YYYY-MM-DD`)
  - `AI_PROVIDER` and provider key (`OPENAI_API_KEY` for active runtime)
- Create cohort DB:
  - Preferred: fresh file (for example `cohort-2.db`)
  - Alternative: clone then sanitize baseline data before opening cohort

### 5. Invite and permission checks (4 min)
- Ensure KIRA bot is present in new server with admin-level setup permissions
- Ensure Trevor has `@Trevor` role and access to admin channels
- Generate student invite link

### 6. Test bot connectivity and privacy boundaries (6 min)
- Start bot from `cis-discord-bot`:
  - `python main.py`
- In `#bot-testing` and `#thinking-lab`, verify:
  - Bot comes online
  - `/frame` triggers DM flow
  - Private process remains in DM (no leakage to public channels)

### 7. Final launch checks (3 min)
- Confirm weekly channel visibility baseline:
  - Week 1 visible
  - Future weeks hidden
- Confirm `#welcome` and `#resources` content is present
- Confirm student invite link is ready for distribution

## Time Budget
- Estimated total: `30 minutes` (2 + 2 + 5 + 8 + 4 + 6 + 3)

## Verification Notes
- This checklist is intentionally operational and includes manual Discord actions.
- Use this as the required pre-go-live gate for each future cohort deployment.
