# KIRA — K2M EdTech Discord Bot

**KIRA** (K2M Interactive Reasoning Agent) is an AI thinking-skills coach that runs an 8-week cohort-based critical thinking programme on Discord.

> **Full system documentation → [`docs/system/`](./docs/system/README.md)**

---

## What This System Does

- 4 CIS thinking agents (`/frame`, `/diverge`, `/challenge`, `/synthesize`) guide students through structured problem-solving
- Automated daily prompts, weekly reflections, and habit tracking across an 8-week cohort
- Progressive agent unlocks tied to weekly reflections — not just time
- Facilitator escalation system with 4 levels (nudge → dashboard → DM → crisis)
- Safety filter blocks all comparison language and detects mental health crisis signals
- Bot-hosted HTTP APIs power landing-page interest capture, enrollment, payment submission, and activation flows
- Scales to 200+ students with 10% human oversight

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Bot runtime | Python 3 + discord.py 2.3.2 (Railway) |
| AI provider | OpenAI by default (model selection is env-configured and swappable via `AI_PROVIDER`) |
| Database (prod) | PostgreSQL on Railway |
| Database (dev) | SQLite (local/test runtime when `DATABASE_URL` is unset) |
| Landing page | Vite static frontend on Vercel (`k2m-landing/`) |
| Context engine | Google Apps Script webhook |
| Email | Brevo for parent notifications |

---

## Quick Start (Local Dev)

### 1. Install dependencies

```bash
pip install -r cis-discord-bot/requirements.txt
```

### 2. Configure environment

```bash
cp cis-discord-bot/.env.template cis-discord-bot/.env
# Edit .env — required: DISCORD_TOKEN, COHORT_1_START_DATE, OPENAI_API_KEY
```

### 3. Run the bot

```bash
python cis-discord-bot/main.py
```

### 4. Run tests

```bash
pytest cis-discord-bot/tests/ -q
```

---

## Project Structure

```
k2m-edtech-program-/
├── cis-discord-bot/              ← Bot (Python) — main application
│   ├── agents/                   ← CIS agent system prompts
│   ├── commands/                 ← Slash command handlers
│   ├── cis_controller/           ← Core logic (router, LLM, safety, onboarding…)
│   ├── database/                 ← Models + SQLite/PostgreSQL stores
│   ├── scheduler/                ← Daily prompts, emails, escalation checks
│   ├── tests/                    ← 80+ test files
│   ├── .env.template             ← Canonical env var reference
│   └── main.py                   ← Entry point
├── k2m-landing/                  ← Enrollment landing page (Vite/Vercel)
├── docs/
│   └── system/                   ← System documentation (start here)
├── _bmad-output/                 ← Design artifacts, playbook, sprint tracker
├── setup_discord_server.py       ← Automates Discord server creation
└── CLAUDE.md                     ← CRITICAL: deployment rules for AI agents
```

---

## Discord Server Structure

| Category | Channels |
|----------|---------|
| Information & Onboarding | #welcome, #announcements, #resources, #introductions |
| Core Interaction | #thinking-lab, #thinking-showcase, #general |
| Weekly Progression | #week-1-wonder, #week-2-3-trust, #week-4-5-converse, #week-6-7-direct, #week-8-showcase |
| Admin | #facilitator-dashboard, #bot-testing, #moderation-logs |

---

## Key Environment Variables

Full reference: `cis-discord-bot/.env.template`

| Variable | Required | Notes |
|----------|---------|-------|
| `DISCORD_TOKEN` | Yes | Bot auth token |
| `COHORT_1_START_DATE` | Yes | `YYYY-MM-DD` — sets cohort clock |
| `DATABASE_URL` | Prod | PostgreSQL connection string |
| `AI_PROVIDER` | No | `openai` (default) \| `anthropic` \| `zhipu` |
| `OPENAI_API_KEY` | Yes (default) | Required for default provider |
| `FACILITATOR_DISCORD_ID` | Yes | Receives crisis + red-level escalation DMs |
| `CONTEXT_ENGINE_WEBHOOK_URL` | Yes | Apps Script endpoint |
| `CONTEXT_ENGINE_WEBHOOK_TOKEN` | Yes | Must match Apps Script Script Property |

---

## ⚠️ Critical: Apps Script Deployment

Never use `clasp deploy --deploymentId <id>` — it silently breaks the webhook.
See [`CLAUDE.md`](./CLAUDE.md) for the correct deployment workflow.

---

## Documentation

| Document | Description |
|----------|-------------|
| [System Overview](./docs/system/01-system-overview.md) | Architecture, tech stack, two-app design |
| [Student Journey](./docs/system/02-student-journey.md) | Enrollment → onboarding → 8 weeks → graduation |
| [Facilitator Guide](./docs/system/03-facilitator-guide.md) | Escalations, dashboard, manual interventions |
| [Super Admin & Ops](./docs/system/04-super-admin-ops.md) | Deployments, env vars, database, scheduler |
| [Under the Hood](./docs/system/05-under-the-hood.md) | State machine, scheduler, safety filter, context engine |
| [Observability](./docs/system/06-observability.md) | Where errors go, what gets logged, how to find what broke |
| [CLAUDE.md](./CLAUDE.md) | Rules for AI agents operating in this repo |
