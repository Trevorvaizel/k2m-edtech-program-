# KIRA Discord Bot - K2M AI Thinking Skills Cohort

**KIRA** (K2M Interactive Reasoning Agent) - AI thinking skills coach for cohort-based learning programs.

## Overview

This project implements a Discord-based learning platform for the K2M AI Thinking Skills Cohort featuring:
- **4 CIS Agents:** Frame, Explore, Challenge, Synthesize (creative thinking coaches)
- **8-Week Journey:** Zone-based progression with habit formation
- **200-Student Scalability:** Automated facilitation with 10% human oversight
- **Artifact Creation:** Guided creation of thinking artifacts as proof-of-learning

## Prerequisites

- **Python 3.8+**
- **Discord Bot Application** (create at https://discord.com/developers/applications)
- **AI Provider API Key:**
  - Temporary: Zhipu AI GLM-5 (https://open.bigmodel.cn)
  - Future: Anthropic Claude API (https://console.anthropic.com)
- **Discord Server** (empty server ready for setup)

## Quick Start

### 1. Clone & Install

```bash
# Navigate to project directory
cd k2m-edtech-program-

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your actual tokens
# Required: DISCORD_TOKEN, ZHIPU_API_KEY (or ANTHROPIC_API_KEY)
```

### 3. Run Server Setup Automation

```bash
# Creates complete Discord server structure (4 categories, 14 channels, 3 roles)
python setup_discord_server.py
```

**Expected output:**
```
✅ Found server: K2M Cohort #1 - AI Thinking Skills
✅ Created 14 channels in 4 categories
✅ Created 3 roles (Student, Trevor, CIS Bot)
✅ Posted welcome content
✅ Server template created
🎉 Server ready for Cohort #1!
```

### 4. Verify Setup

Check your Discord server for:
- ✅ 4 categories: Information, Core Interaction, Weekly Progression, Admin
- ✅ 14 channels with correct permissions
- ✅ 3 roles: @Student, @Trevor, @CIS Bot
- ✅ Welcome content in #welcome channel
- ✅ Resources content in #resources channel
- ✅ Week 1 channel visible, others hidden

## Project Structure

```
k2m-edtech-program-/
├── setup_discord_server.py    # Discord server automation script
├── fix_channel_emojis.py      # Utility to add emoji to channel names
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .env                        # Your actual tokens (DO NOT COMMIT)
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── _bmad-output/               # Design documents & planning artifacts
│   └── cohort-design-artifacts/
│       ├── playbook-v2/        # Complete cohort playbook (Epics 1-6)
│       ├── discord-implementation-sprint.yaml  # Implementation tracker
│       └── adversarial-review-sprint-0-discord-setup.md
│
└── (Sprint 1: Bot code will go here)
```

## Sprint Status

**Current Progress:** Sprint 0 Complete (8%, 4/49 tasks)

### Sprint 0: Automated Discord Server Setup ✅
- [x] 0.1 - Create Discord bot application
- [x] 0.2 - Create empty Discord server
- [x] 0.3 - Invite bot with admin permissions
- [x] 0.4 - Write automation script
- [ ] 0.5 - Manual verification
- [ ] 0.6 - Build Google Sheets templates

### Sprint 1: Bot Core Engine (Next)
- [ ] 1.1 - Scaffold Python bot project
- [ ] 1.2 - Implement StudentContext + SQLite schema
- [ ] 1.3 - Implement CIS Controller routing logic
- [ ] 1.4 - Implement /frame agent (The Framer)
- [ ] 1.5 - Implement private DM workflow
- [ ] 1.6 - Implement rate limiting + cost controls
- [ ] 1.7 - Implement observability infrastructure

See `_bmad-output/cohort-design-artifacts/discord-implementation-sprint.yaml` for full sprint plan.

## Architecture

**Discord Server Structure:**
- **Information & Onboarding:** Welcome, announcements, resources, introductions
- **Core Interaction:** Thinking Lab (CIS agent entry), Thinking Showcase (public artifacts), General chat
- **Weekly Progression:** 8 week-specific channels (progressive unlock)
- **Admin:** Facilitator dashboard, bot testing, moderation logs

**CIS Agent System:**
- **/frame** (Week 1+): Pause and clarify questions (Habits 1 & 2)
- **/diverge** (Week 4+): Explore possibilities (Habit 3)
- **/challenge** (Week 4+): Test assumptions (Habit 4)
- **/synthesize** (Week 6+): Articulate conclusions (Habit 4)
- **/create-artifact** (Week 6+): 6-section artifact creation

**Tech Stack:**
- Discord.py (Discord API wrapper)
- Zhipu AI GLM-5 (temporary LLM provider)
- SQLite (student context, conversation history)
- Python 3.8+ (async/await patterns)

## Troubleshooting

### Error: "Privileged intents not enabled"

**Fix:** Go to Discord Developer Portal → Your App → Bot → Enable:
- ✅ Presence Intent
- ✅ Server Members Intent
- ✅ Message Content Intent

### Error: "Server not found"

**Fix:** Check `setup_discord_server.py` line 29:
```python
SERVER_NAME = "K2M Cohort #1 - AI Thinking Skills"  # Must match exactly
```

### Error: "Invalid Form Body: content too long"

**Fix:** Script automatically chunks messages >2000 chars. If error persists, check `split_message()` function.

### Error: "use_slash_commands is not a valid permission"

**Fix:** Already fixed in v1.1. Use `use_application_commands` instead (discord.py 2.6.4+).

### Unicode encoding errors on Windows

**Fix:** Script automatically configures UTF-8 encoding (line 23-24). Ensure Python 3.8+.

## Security

**⚠️ NEVER commit `.env` file!**

**Token Rotation:**
If bot token is compromised:
1. Go to Discord Developer Portal → Your App → Bot → "Regenerate" token
2. Update `.env` with new token
3. Restart bot

**Best Practices:**
- Use `.env.example` for documentation
- Store production tokens in secure environment (Railway, Heroku)
- Rotate tokens every 90 days
- Use different tokens for dev/prod environments

## Deployment (Future)

**Local Development:**
```bash
python setup_discord_server.py  # One-time server setup
python bot.py                   # Run bot (Sprint 1+)
```

**Production (Railway/Heroku):**
- Set environment variables in platform dashboard
- Deploy `bot.py` as main process
- Enable auto-restart on crash
- Monitor logs for errors

## Multi-Cohort Deployment

**Server Template Created:**
After running `setup_discord_server.py`, a template is created automatically.

**Deploy New Cohort:**
1. Use server template link (output from script)
2. Rename server: "K2M Cohort #2 - AI Thinking Skills"
3. Update `.env`: `COHORT_ID=cohort-2`
4. Create new database: `cohort-2.db`
5. Update start date in bot config
6. Deploy in ~30 minutes

**Template Link:** Check script output for `https://discord.new/XXXXX` link.

## Documentation

**Complete Playbook:**
- `_bmad-output/cohort-design-artifacts/playbook-v2/` (Epics 1-6 design documents)
- Story 5.1: Discord Server Architecture
- Story 4.7: Bot Technical Specification

**Implementation Tracker:**
- `_bmad-output/cohort-design-artifacts/discord-implementation-sprint.yaml`

**Adversarial Review:**
- `_bmad-output/cohort-design-artifacts/adversarial-review-sprint-0-discord-setup.md`

## Support

**Issues:** Report at project repo issues tracker
**Questions:** DM Trevor or check `#bot-testing` channel

## License

Proprietary - K2M EdTech

---

**Built with BMAD (Boyd's Method for Agile Design)**
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
