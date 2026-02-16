# K2M Cohort Discord Server Template

## Quick Deploy: Instant Cohort Server Setup

**Template URL:** `https://discord.new/Eqz6DMNHuVHU`

This template instantly clones the complete K2M cohort server structure:
- ✅ 4 channel categories
- ✅ 15 channels (with emoji prefixes)
- ✅ 3 roles (@Student, @Trevor, @CIS Bot)
- ✅ Permission boundaries configured
- ✅ Welcome & resources content

---

## Deploy New Cohort (2-Minute Process)

### Step 1: Create Server from Template
1. Open template URL: `https://discord.new/Eqz6DMNHuVHU`
2. Click "Create" to generate instant copy
3. Server created with all channels, roles, and permissions ✅

### Step 2: Rename Server
1. Go to Server Settings
2. Change name to: `K2M Cohort #2 - AI Thinking Skills` (or #3, #4, etc.)
3. Save changes

### Step 3: Invite Bot (Optional if using same bot)
1. If using a separate bot instance per cohort:
   - Create new bot application in Discord Developer Portal
   - Get new bot token
   - Invite to new server with admin permissions
2. If using shared bot:
   - Invite existing KIRA bot to new server
   - Update bot code to handle multiple guild IDs

### Step 4: Configure Environment
1. Create new `.env` file or update existing:
   ```bash
   COHORT_ID=cohort-2
   COHORT_START_DATE=2026-03-15
   # If separate bot per cohort:
   DISCORD_TOKEN=<new_bot_token>
   ZHIPU_API_KEY=<api_key>
   ```

2. Create cohort-specific database:
   ```bash
   cp cohort-1.db cohort-2.db  # Or start fresh
   ```

### Step 5: Launch Bot
```bash
python bot.py  # When Sprint 1 is complete
```

**Total deployment time:** ~2 minutes (vs. 30 minutes manual setup)

---

## Server Structure (What Gets Cloned)

### 📚 INFORMATION & ONBOARDING
- 👋welcome - Welcome message and program overview
- 📢announcements - Facilitator announcements (Trevor only posts)
- 📚resources - Reference materials, links, guides
- 🤝introductions - Student self-introductions

### 💬 CORE INTERACTION SPACES
- 🧪thinking-lab - Primary CIS agent interaction (DM-like experience)
- ✨thinking-showcase - Public artifact sharing and peer feedback
- 💬general - Informal peer chat and community building

### 🗓️ WEEK-SPECIFIC PROGRESSION
- 🌟week-1-wonder - Week 1 discussions (visible at start)
- 🤝week-2-3-trust - Weeks 2-3 discussions (unlocks Week 2)
- 💭week-4-5-converse - Weeks 4-5 discussions (unlocks Week 4)
- 🎯week-6-7-direct - Weeks 6-7 discussions (unlocks Week 6)
- 🎊week-8-showcase - Final showcase preparation (unlocks Week 8)

### 🔧 ADMIN & OPERATIONS
- 📊facilitator-dashboard - Trevor's monitoring and intervention space
- 🤖bot-testing - Safe space for testing bot features
- 🛡️moderation-logs - Automated moderation records

---

## Customization Checklist

After deploying from template, customize:

- [ ] **Server name** - Change to correct cohort number
- [ ] **Welcome message** - Update cohort-specific dates in #welcome
- [ ] **Announcements** - Pin cohort start date announcement
- [ ] **Resources** - Add cohort-specific Notion links
- [ ] **Bot database** - Create fresh `cohort-X.db` or clone previous
- [ ] **Environment variables** - Set `COHORT_ID` and `COHORT_START_DATE`
- [ ] **Weekly unlocks** - Verify week 1 visible, others hidden
- [ ] **Facilitator access** - Assign @Trevor role to facilitator(s)

---

## Multi-Cohort Strategies

### Option A: Shared Bot Instance (Recommended)
**Best for:** Sequential cohorts with same facilitator

- One bot instance handles multiple servers
- Bot tracks which server = which cohort via guild ID
- Student data separated by database tables (`cohort_1_students`, `cohort_2_students`)
- Cost-effective (one LLM API subscription)

**Pros:**
- Lower operational cost
- Centralized monitoring
- Shared conversation history for analysis

**Cons:**
- Single point of failure
- Rate limits shared across cohorts

---

### Option B: Separate Bot per Cohort
**Best for:** Overlapping cohorts or different facilitators

- Each cohort gets dedicated bot instance
- Separate API keys and databases
- Independent rate limits and monitoring

**Pros:**
- Isolated failure domains
- Cohort-specific customization
- Easier access control

**Cons:**
- Higher operational cost (multiple API subscriptions)
- More deployment overhead

---

## Template Maintenance

### Updating the Template
If you make improvements to the server structure:

1. Make changes to the original server (K2M Cohort #1)
2. Go to Server Settings → Server Template
3. Click "Sync Template" to update with latest changes
4. New deployments will use updated structure

### Template Includes:
✅ Channel structure and emoji
✅ Categories and organization
✅ Role hierarchy (but NOT role assignments)
✅ Permission overrides
✅ Channel topics

### Template Does NOT Include:
❌ Messages (welcome content must be re-posted)
❌ Role assignments (students must be assigned @Student role)
❌ Server icon/banner
❌ Bot presence (must re-invite bot)

---

## Troubleshooting

**Template link doesn't work:**
- Check if template is synced in Server Settings → Server Template
- Verify you have "Manage Server" permissions
- Try regenerating template code

**Channels missing after deployment:**
- Template may have desync'd - check original server
- Manually create missing channels using `setup_discord_server.py`

**Permissions not working:**
- Re-check role hierarchy in new server
- Verify @CIS Bot role is above @Student role
- Re-run permission setup from setup script if needed

---

## Original Server Template Creation

This template was created via:
```bash
python setup_discord_server.py  # Initial automation
python fix_channel_emojis.py    # Emoji fix
# Manual: Server Settings → Server Template → Create
```

Template code: `Eqz6DMNHuVHU`

---

**Built with BMAD (Boyd's Method for Agile Design)**
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
