# K2M CIS Discord Bot

**KIRA** (K2M Interactive Reasoning Agent) - CIS Agent System for Discord-based Cohort Facilitation

## Story 4.7 Implementation

This bot implements the complete CIS Agent System specified in Story 4.7 of the K2M EdTech Program.

## Project Status

**Sprint 1, Task 1.1: Scaffold Python Bot Project** ✅ COMPLETE

### Completed Tasks
- ✅ Project structure created
- ✅ Dependencies configured (requirements.txt)
- ✅ Environment variables template (.env.template)
- ✅ Main bot entry point (main.py)
- ✅ Database schema (SQLite)
- ✅ Database operations layer (store.py)
- ✅ CIS Controller router stub
- ✅ Framer agent system prompt
- ✅ Frame command handler stub

### Next Tasks (Sprint 1)
- [ ] Task 1.2: Implement StudentContext + SQLite schema operations
- [ ] Task 1.3: Implement CIS Controller routing logic
- [ ] Task 1.4: Implement /frame agent (The Framer)
- [ ] Task 1.5: Implement private DM workflow
- [ ] Task 1.6: Implement rate limiting + cost controls
- [ ] Task 1.7: Implement Observability Infrastructure

## Quick Start

### 1. Install Dependencies

```bash
cd cis-discord-bot
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the template
cp .env.template .env

# Edit .env with your credentials
# Required:
# - DISCORD_TOKEN (from Discord Developer Portal)
# - AI_PROVIDER (openai active default; also supports anthropic | zhipu)
# - Matching provider key (OPENAI_API_KEY for default runtime)
# Optional but recommended:
# - DISCORD_GUILD_ID (for fast slash command sync in your server)
# - SYNC_GLOBAL_COMMANDS=false (avoid duplicate global+guild command listings)
# - CHANNEL_FACILITATOR_DASHBOARD (budget + escalation alerts)
# Required for admin observability commands:
# - FACILITATOR_DISCORD_ID (only this user can run admin commands)
# Development only:
# - ALLOW_INSECURE_ADMIN=true (do not enable in production)
# Parent email system (Task 4.6):
# - BREVO_API_KEY (preferred) or SENDGRID_API_KEY or MAILGUN_API_KEY (+ MAILGUN_DOMAIN if using Mailgun)
# - EMAIL_FROM / EMAIL_FROM_NAME
# - PARENT_EMAIL_FROM / PARENT_EMAIL_FROM_NAME / PARENT_EMAIL_REPLY_TO
# - Optional template styling links: PARENT_EMAIL_LOGO_URL, PARENT_EMAIL_LOGO_SVG_PATH,
#   PARENT_EMAIL_LOGO_SIZE_PX, PARENT_EMAIL_CTA_URL,
#   PARENT_EMAIL_SOCIAL_INSTAGRAM_URL, PARENT_EMAIL_SOCIAL_X_URL,
#   PARENT_EMAIL_SOCIAL_WHATSAPP_URL, PARENT_EMAIL_SOCIAL_DISCORD_URL
# - PARENT_UNSUBSCRIBE_BASE (optional override)
# - EMAIL_DRY_RUN=true for non-production testing
```

Optional secure Brevo key setup (hidden prompt, no key echo):

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\set-brevo-key.ps1
```

### 3. Run the Bot

```bash
python main.py
```

### 4. Test Bot Connectivity

In Discord, type:
```
/ping
```

Expected response: `Pong! {latency}ms`

### 5. Run Full Discord Health Check

```bash
python check_discord_health.py
```

What it verifies:
- Discord token auth (`/users/@me`)
- Guild access (`DISCORD_GUILD_ID`)
- Required channels (`CHANNEL_*`)
- Required slash commands registered in guild
- Active LLM provider configuration

## Project Structure

```
cis-discord-bot/
├── main.py                      # Bot entry point
├── requirements.txt             # Python dependencies
├── .env.template               # Environment variables template
├── .gitignore                   # Security (excludes .env, *.db)
├── README.md                    # This file
│
├── cis_controller/             # CIS Controller (Task 1.3)
│   ├── router.py               # Intent recognition & routing
│   ├── state_machine.py        # Student state management
│   ├── llm_integration.py      # Active LLM Provider calls
│   ├── suggestions.py          # "Did you mean...?" system
│   └── safety_filter.py        # Anti-comparison validation
│
├── agents/                     # CIS Agent Prompts
│   ├── framer_prompt.py        # The Framer (Habit 1 & 2)
│   ├── explorer_prompt.py      # The Explorer (Habit 3)
│   ├── challenger_prompt.py    # The Challenger (Habit 4)
│   └── synthesizer_prompt.py   # The Synthesizer (Habit 4)
│
├── database/                   # Database Layer
│   ├── schema.sql              # SQLite schema
│   ├── models.py               # StudentContext ORM (Task 1.2)
│   └── store.py                # Database operations
│
├── commands/                   # Discord Command Handlers
│   ├── frame.py                # /frame command
│   ├── diverge.py              # /diverge command
│   ├── challenge.py            # /challenge command
│   ├── synthesize.py           # /synthesize command
│   └── artifact.py             # /create-artifact command
│
└── tests/                      # Test Suite
    ├── test_router.py
    ├── test_state_machine.py
    └── test_store.py
```

## Technical Stack

| Component | Tool | Version | Purpose |
|-----------|------|---------|---------|
| **Language** | Python | 3.10+ | Bot implementation |
| **Discord Library** | discord.py | 2.3.2 | Discord API wrapper |
| **LLM Provider** | OpenAI (active) / Anthropic / Zhipu | Env-swappable | CIS agent intelligence |
| **Database** | SQLite | 3.38+ | State persistence |
| **Environment** | python-dotenv | 1.0.0 | Configuration management |

## Architecture

```
Discord Events → Intent Recognition → State Machine → Agent Router → Active LLM Provider → SafetyFilter → Discord Response
```

### Three-Layer Controller

1. **Layer 1: Intent Recognition** - Parse commands, extract context, check permissions
2. **Layer 2: State Machine** - Track student progress, conversation state, habit journey
3. **Layer 3: Agent Router** - Route to appropriate CIS agent (/frame, /diverge, etc.)

## Four CIS Agents

| Agent | Command | Habits | Week Available |
|-------|---------|--------|----------------|
| The Framer | /frame | Habit 1 (Pause), Habit 2 (Context) | Week 1 |
| The Explorer | /diverge | Habit 3 (Iterate) | Week 4 |
| The Challenger | /challenge | Habit 4 (Think First) | Week 4 |
| The Synthesizer | /synthesize | Habit 4 (Think First) | Week 6 |

## Deployment

### Local Development
```bash
python main.py
```

### Production (Railway)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

## Cost Management

- **Budget:** $100/week conservative
- **Expected:** $5-33/week with prompt caching
- **Rate Limiting:** 50 interactions/day per student
- **Monitoring:** Daily budget alerts at $10
- **Dashboard Alerts:** Daily/weekly budget alerts posted to #facilitator-dashboard

## Security Notes

⚠️ **NEVER commit .env file** - Contains Discord token and API keys
⚠️ **NEVER commit *.db files** - Contains student data
⚠️ **Always use .gitignore** - Already configured for security

## Documentation

- [Story 4.7: Discord Bot Technical Specification](../_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-7-discord-bot-spec.md)
- [CIS Controller Logic](../_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-1-cis-controller-logic.md)
- [Agent Prompts](../_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/)

## Sprint Progress

See [discord-implementation-sprint.yaml](../_bmad-output/cohort-design-artifacts/operations/sprint/discord-implementation-sprint.yaml) for complete implementation status.

**Sprint 0:** ✅ COMPLETE (Discord server + bot setup)
**Sprint 1:** 🔄 IN PROGRESS (Bot Core Engine)

---

**Bot Name:** KIRA (K2M Interactive Reasoning Agent)
**Cohort:** K2M Cohort #1 - AI Thinking Skills
**Developer:** Trevor (with BMAD agents)


