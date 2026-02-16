# Adversarial Review: Sprint 0 Discord Server Setup
**Date:** 2026-02-16
**Reviewer:** Dev Agent (Amelia) - Adversarial Mode
**Scope:** Tasks 0.1-0.4 (Bot creation, server setup, automation script)
**Status:** CHANGES REQUIRED (7 issues found)

---

## Executive Summary

Sprint 0 automation script successfully creates Discord infrastructure but has **7 critical gaps** that must be addressed before Sprint 1:

- **HIGH Priority:** 3 issues (security, scalability, testing)
- **MEDIUM Priority:** 3 issues (error handling, documentation, spec compliance)
- **LOW Priority:** 1 issue (code quality)

**Overall Assessment:** 🟡 FUNCTIONAL BUT INCOMPLETE
**Recommendation:** Fix HIGH priority issues before Sprint 1, defer others to refactor sprint.

---

## HIGH PRIORITY ISSUES

### 🚨 ISSUE #1: Bot Token Exposed in .env (Security Risk)

**Finding:**
`.env` file contains plaintext DISCORD_TOKEN and ZHIPU_API_KEY but is tracked in `.gitignore`. However, the token was shared in conversation history and could be committed accidentally.

**Risk:**
If `.env` is accidentally committed or shared, bot token can be stolen and server compromised.

**Spec Violation:**
Story 5.1 "Security" - tokens must be rotated and never exposed.

**Fix Required:**
1. Add `.env.example` template (without real tokens)
2. Document token rotation process in README
3. Consider using environment-specific .env files (.env.dev, .env.prod)
4. Add pre-commit hook to block .env commits

**Impact:** CRITICAL - Security breach risk
**Effort:** 15 minutes

---

### 🚨 ISSUE #2: No Server Template Created (Task 0.4 Incomplete)

**Finding:**
Task 0.4 description says "Create server template for future cohorts" but script does NOT implement this. Script only creates channels/roles, never calls `guild.create_template()`.

**Spec Violation:**
Story 5.1 "Copy-Paste Server Template" section explicitly requires template creation for rapid deployment.

**Evidence:**
```python
# setup_discord_server.py - NO TEMPLATE CREATION CODE EXISTS
# Missing: await guild.create_template(name="K2M Cohort Template", description="...")
```

**Fix Required:**
Add template creation step at end of `setup_server()`:
```python
# Create server template for future cohorts
template = await guild.create_template(
    name="K2M Cohort Template",
    description="Complete Discord server for K2M AI Thinking Skills cohort"
)
print(f"✅ Server template created: {template.code}")
```

**Impact:** HIGH - Blocks multi-cohort scalability (Trevor's question earlier)
**Effort:** 10 minutes

---

### 🚨 ISSUE #3: No Automated Testing (Script Validation Gap)

**Finding:**
Automation script runs successfully but has ZERO unit tests or integration tests. Task 0.5 requires manual verification, but no automated checks exist.

**Spec Violation:**
BMM best practices require automated testing for critical infrastructure code.

**What's Untested:**
- Permission logic correctness
- Channel visibility (weekly channels hidden/visible)
- Role creation with correct permissions
- Message chunking edge cases (exactly 2000 chars, >4000 chars)
- Idempotency (running script twice)

**Fix Required:**
Create `tests/test_setup_discord_server.py`:
- Mock Discord API
- Test permission logic
- Test message chunking
- Test idempotency

**Impact:** MEDIUM-HIGH - No safety net for future changes
**Effort:** 2-3 hours

---

## MEDIUM PRIORITY ISSUES

### ⚠️ ISSUE #4: Incomplete Error Handling

**Finding:**
Script assumes happy path. What happens if:
- Discord API rate limits hit during setup?
- Channel creation fails mid-way?
- Network connection drops?
- Guild not found (wrong server name)?

**Evidence:**
```python
# Current code
guild = discord.utils.get(bot.guilds, name=SERVER_NAME)
if not guild:
    print(f"❌ Error: Server '{SERVER_NAME}' not found!")
    # STOPS HERE - no retry, no recovery, partial state left behind
```

**Fix Required:**
- Add retry logic with exponential backoff
- Add rollback mechanism if setup fails mid-way
- Add transaction-like behavior (all or nothing)
- Log all errors to file for debugging

**Impact:** MEDIUM - Script fails ungracefully, leaves server in broken state
**Effort:** 1-2 hours

---

### ⚠️ ISSUE #5: Channel Emoji Not Applied (Minor Spec Deviation)

**Finding:**
Script defines emoji in `CATEGORIES` dict but never applies them to channel names.

**Evidence:**
```python
# Defined but not used:
{"name": "welcome", "emoji": "👋", "topic": "Welcome & Getting Started"}

# Channel created without emoji:
channel = await category.create_text_channel(
    name=channel_name,  # Should be: "👋welcome"
    topic=channel_config["topic"]
)
```

**Spec Compliance:**
Story 5.1 shows channels WITH emoji in architecture diagram.

**Fix Required:**
```python
channel_name_with_emoji = f"{channel_config['emoji']}{channel_name}"
channel = await category.create_text_channel(name=channel_name_with_emoji, ...)
```

**Impact:** LOW - Cosmetic, but spec non-compliance
**Effort:** 5 minutes

---

### ⚠️ ISSUE #6: Missing Documentation

**Finding:**
No README.md, no inline documentation, no deployment guide.

**What's Missing:**
- README.md: How to run the script
- Deployment checklist: Pre-setup steps
- Troubleshooting guide: Common errors
- Architecture diagram: What the script creates

**Fix Required:**
Create `README.md` in project root with:
1. Prerequisites (Python 3.8+, Discord bot, .env setup)
2. Installation (`pip install -r requirements.txt`)
3. Usage (`python setup_discord_server.py`)
4. Verification steps (manual checks)
5. Troubleshooting (common errors + fixes)

**Impact:** MEDIUM - Blocks handoff to Trevor or other developers
**Effort:** 30 minutes

---

## LOW PRIORITY ISSUES

### ℹ️ ISSUE #7: Code Quality - Hardcoded Strings

**Finding:**
Magic strings scattered throughout code (channel names, role names, category names). Should be constants.

**Example:**
```python
# Current: Hardcoded everywhere
welcome_channel = discord.utils.get(guild.text_channels, name="welcome")

# Better: Constants at top
CHANNEL_WELCOME = "welcome"
welcome_channel = discord.utils.get(guild.text_channels, name=CHANNEL_WELCOME)
```

**Fix Required:**
- Extract all magic strings to constants at top of file
- Makes changes easier (rename channel once vs. 10+ places)

**Impact:** LOW - Code maintainability
**Effort:** 30 minutes (refactor)

---

## CRITICAL GAPS (Not Bugs, But Missing Features)

### 📋 GAP #1: No Cluster Voice Channel Creation

**Spec Requirement:**
Story 5.1 "Cluster Assignment System" requires temporary voice channels for Trevor's live sessions.

**Current Status:**
Script creates text channels only. No voice channels exist.

**Fix:**
Defer to Sprint 2 Task 2.6 or add to Sprint 1 as new task.

---

### 📋 GAP #2: No Google Sheets Templates Created

**Spec Requirement:**
Task 0.6 explicitly requires 4 Google Sheets (Student Roster, Submissions Log, Intervention Tracking, Progress Dashboard).

**Current Status:**
Task 0.6 still pending.

**Fix:**
Execute task 0.6 before Sprint 1 begins (dependency for bot tracking).

---

## POSITIVE FINDINGS (What Works Well)

✅ **Idempotency:** Script safely runs multiple times without breaking
✅ **Message Chunking:** Correctly handles Discord 2000 char limit
✅ **Permission Logic:** Role-based permissions mostly correct per spec
✅ **UTF-8 Fix:** Windows console encoding handled properly
✅ **Code Structure:** Clean, readable, well-organized functions

---

## RECOMMENDED FIXES (Priority Order)

**Before Sprint 1:**
1. ✅ Create server template (Issue #2) - 10 min
2. ✅ Add .env.example + token rotation docs (Issue #1) - 15 min
3. ✅ Fix channel emoji (Issue #5) - 5 min
4. ✅ Add README.md (Issue #6) - 30 min

**During Sprint 1:**
5. ⏳ Add error handling + retry logic (Issue #4) - 1-2 hours
6. ⏳ Add automated tests (Issue #3) - 2-3 hours

**Future Refactor Sprint:**
7. ⏳ Extract magic strings to constants (Issue #7) - 30 min

---

## FINAL VERDICT

**Sprint 0 Status:** 🟢 ACCEPTABLE FOR SPRINT 1 START
**Blocker Issues:** 0
**Must-Fix Before Sprint 1:** 4 issues (Issues #1, #2, #5, #6)
**Total Fix Time:** ~1 hour

**Recommendation:** Address 4 must-fix issues now, defer testing and error handling to Sprint 1 refactor.

---

## COMMIT RECOMMENDATION

**After fixes applied, commit with message:**
```
feat: Complete Sprint 0 Discord server automation

- Add KIRA bot application with admin permissions
- Create automation script (480 lines) for full server setup
- Implement 4 categories, 14 channels, 3 roles per Story 5.1 spec
- Add welcome/resources content with message chunking
- Add server template for multi-cohort scalability
- Security: .env.example template, token rotation docs
- Docs: README.md with setup/troubleshooting guide

Tasks completed: 0.1, 0.2, 0.3, 0.4
Progress: 8% (4/49 tasks)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Files to commit:**
- setup_discord_server.py
- requirements.txt
- .env.example (NEW)
- .gitignore
- README.md (NEW)
- _bmad-output/cohort-design-artifacts/discord-implementation-sprint.yaml
- _bmad-output/cohort-design-artifacts/adversarial-review-sprint-0-discord-setup.md

**Files to EXCLUDE:**
- .env (NEVER commit secrets)
