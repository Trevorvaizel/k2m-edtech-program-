# System Overview — K2M EdTech Platform

> What is this system, how do the pieces connect, and what is each part responsible for?

---

## The Big Picture

K2M runs two applications that work together to deliver an 8-week cohort-based critical thinking programme over Discord.

```
┌─────────────────────────────────────────────────────────────────┐
│                        STUDENTS & PARENTS                        │
└───────────┬──────────────────────────────────┬──────────────────┘
            │ enrol                            │ use daily
            ▼                                  ▼
┌─────────────────────┐            ┌───────────────────────────────┐
│   K2M Landing Page  │            │     Discord (KIRA Bot)        │
│   (Vercel/Next.js)  │            │     (Railway + PostgreSQL)    │
│                     │            │                               │
│ • Enrollment form   │            │ • 4 CIS thinking agents       │
│ • Parent consent    │            │ • 8-week structured journey   │
│ • Interest capture  │            │ • Daily prompts + scheduler   │
│                     │            │ • Facilitator escalation      │
└─────────────────────┘            │ • Safety & crisis handling    │
                                   └───────────┬───────────────────┘
                                               │ reads/writes
                                               ▼
                                   ┌───────────────────────────────┐
                                   │  Google Sheets (Context       │
                                   │  Engine via Apps Script)      │
                                   │                               │
                                   │ • Student enrollment records  │
                                   │ • Profession-based examples   │
                                   │ • Intervention library        │
                                   └───────────────────────────────┘
```

---

## Application 1 — K2M Landing Page

**Location:** `k2m-landing/`
**Deployed on:** Vercel
**Built with:** Next.js

**Responsibilities:**
- Student enrollment form
- Parent/guardian consent capture
- Interest and JTBD (Jobs-to-be-Done) feedback collection

**Does NOT:**
- Run the programme (that's Discord)
- Talk to the bot directly

---

## Application 2 — KIRA Discord Bot

**Location:** `cis-discord-bot/`
**Deployed on:** Railway
**Built with:** Python + discord.py
**Database:** PostgreSQL (Railway-managed)

KIRA is the heart of the programme. It is a multi-agent AI coach that guides students through a structured critical-thinking process called **CIS (Critical Inquiry System)**.

### The 4 CIS Agents

| Agent | Command | Habit | Unlocks at |
|-------|---------|-------|------------|
| **Frame** | `/frame` | PAUSE (Habit 1) | Week 1 |
| **Diverge** | `/diverge` | ITERATE (Habit 3) | Week 4 |
| **Challenge** | `/challenge` | THINK FIRST (Habit 4) | Week 4 |
| **Synthesize** | `/synthesize` | THINK FIRST (Habit 4) | Week 6 |

There is also `/create-artifact` (Week 6) which assembles the student's 6-section thinking artifact from their work across the 8 weeks.

### Core Subsystems

| Subsystem | What it does |
|-----------|-------------|
| **State machine** | Tracks where each student is in their thinking journey |
| **Scheduler** | Posts daily prompts, reflection prompts, peer visibility snapshots on a fixed EAT timezone schedule |
| **Onboarding** | Guided 4-stop setup that runs in DM when a student joins |
| **Escalation system** | Watches for inactivity and crisis signals; pings Trevor at the right level |
| **Safety filter** | Blocks comparison language and detects mental health crisis keywords |
| **Context engine** | Fetches personalised examples from Google Sheets via Apps Script webhook |
| **Rate limiter** | Controls cost per student per day |
| **Email service** | Sends weekly parent updates via Brevo (Sendinblue) |

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Bot runtime | Python 3 + discord.py 2.3.2 | Hosted on Railway |
| AI provider | OpenAI `gpt-4o-mini` | Swappable via `AI_PROVIDER` env var |
| Database (prod) | PostgreSQL | Railway-managed, connection pooling min=2 max=10 |
| Database (dev/test) | SQLite | Automatic fallback if no `DATABASE_URL` set |
| Landing page | Next.js | Hosted on Vercel |
| Context engine | Google Apps Script | Webhook at `CONTEXT_ENGINE_WEBHOOK_URL` |
| Email | Brevo (Sendinblue) | Parent notifications |
| Timezone | EAT (Africa/Nairobi) | All scheduler times in EAT |

---

## Environment Variables — Key Ones

Full list is in `cis-discord-bot/.env.template`. The most important:

| Variable | Purpose |
|----------|---------|
| `DISCORD_TOKEN` | Bot authentication |
| `COHORT_1_START_DATE` | YYYY-MM-DD — sets the cohort clock for all students |
| `DATABASE_URL` | PostgreSQL connection string (required in prod) |
| `AI_PROVIDER` | `openai` \| `anthropic` \| `zhipu` (default: `openai`) |
| `CONTEXT_ENGINE_WEBHOOK_URL` | Apps Script endpoint |
| `CONTEXT_ENGINE_WEBHOOK_TOKEN` | Must match Apps Script Script Property |
| `FACILITATOR_DISCORD_ID` | Trevor's Discord ID — receives crisis and escalation DMs |
| `BREVO_API_KEY` | Parent email delivery |

---

## Repository Structure

```
k2m-edtech-program-/
├── cis-discord-bot/        ← Main bot (Python)
│   ├── agents/             ← CIS agent system prompts
│   ├── commands/           ← Slash command handlers
│   ├── cis_controller/     ← Core logic (router, onboarding, LLM, safety, etc.)
│   ├── database/           ← Models, SQLite store, PostgreSQL store
│   ├── scheduler/          ← Daily prompts, cluster sessions, parent emails
│   └── tests/              ← 80+ test files
├── k2m-landing/            ← Enrollment landing page (Next.js)
├── docs/
│   ├── system/             ← You are here
│   └── [curriculum docs]   ← AI framework, territory maps, etc.
├── _bmad-output/           ← Design artifacts, sprint tracking, playbook
└── CLAUDE.md               ← CRITICAL agent rules (read before deploying)
```