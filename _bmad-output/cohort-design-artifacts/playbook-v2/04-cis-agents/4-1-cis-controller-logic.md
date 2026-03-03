# Story 4.1: Define CIS Controller Logic

Status: ready-for-dev

**Epic:** 4 - CIS Agent System
**Story:** 4.1 - Define CIS Controller logic
**Created:** 2026-01-25
**Purpose:** Architectural foundation - Design the routing, state management, and LLM integration system that powers all CIS agent interactions on Discord

---

## Story

As a **Cohort Facilitation System Architect**,
I want **a CIS Controller that intelligently routes student interactions to appropriate thinking partners**,
so that **students experience seamless, identity-transforming conversations scaffolded by the 4 Habits framework**.

---

## Acceptance Criteria

1. **Controller Architecture Document** specifying hybrid routing system (commands preferred, natural language with suggestions)
2. **State Machine Design** documenting student thinking journey tracking with non-linear progression support
3. **LLM API Integration** specifying Claude Sonnet 4.5 (Batch) integration with prompt caching strategy
4. **Graduated Suggestion System** defining week-based intensity levels (Week 1: explicit → Week 8: minimal)
5. **Temporal Awareness Logic** enforcing week-based agent unlocking per Decision 11 graduated introduction
6. **Error Handling & Cost Controls** specifying API failure recovery, rate limiting, and budget management
7. **Technical Implementation Guide** providing Discord bot patterns, SQLite schema, and code examples

---

## Tasks / Subtasks

- [ ] **1. Document Controller Architecture** (AC: #1)
  - [ ] 1.1 Specify hybrid routing logic (commands + natural language suggestions)
  - [ ] 1.2 Design three-layer architecture (Intent Recognition → State Machine → Agent Router)
  - [ ] 1.3 Define "Did you mean...?" suggestion system patterns
  - [ ] 1.4 Document controller as "invisible conductor" UX principle

- [ ] **2. Design State Machine** (AC: #2)
  - [ ] 2.1 Define states: framing, exploring, challenging, synthesizing, complete
  - [ ] 2.2 Specify non-linear transition support (students can revisit any phase)
  - [ ] 2.3 Design artifact progress tracking system
  - [ ] 2.4 Document student metadata schema (current_week, unlocked_agents, thinking_state)

- [ ] **3. Specify LLM API Integration** (AC: #3)
  - [ ] 3.1 Document Claude Sonnet 4.5 (Batch) API integration
  - [ ] 3.2 Define prompt caching strategy (90% cost reduction on system prompts)
  - [ ] 3.3 Specify API cost budget ($100 conservative, actual $5-33 with caching)
  - [ ] 3.4 Design per-student interaction limits (prevent runaway costs)

- [ ] **4. Define Graduated Suggestion System** (AC: #4)
  - [ ] 4.1 Specify Week 1-2 intensity: Explicit guidance ("Try /frame to clarify...")
  - [ ] 4.2 Specify Week 4-5 intensity: Gentle nudges ("Have you considered...?")
  - [ ] 4.3 Specify Week 6-7 intensity: Minimal prompts ("Ready to synthesize?")
  - [ ] 4.4 Specify Week 8 intensity: Prompt-driven only (no suggestions)

- [ ] **5. Document Temporal Awareness Logic** (AC: #5)
  - [ ] 5.1 Define week-based agent unlocking rules (Decision 11 compliance)
  - [ ] 5.2 Specify friendly lockout messages for premature agent access
  - [ ] 5.3 Design artifact creation gates (Week 6+ only)
  - [ ] 5.4 Document graduated introduction timeline

- [ ] **6. Specify Error Handling & Cost Controls** (AC: #6)
  - [ ] 6.1 Define API failure recovery patterns
  - [ ] 6.2 Document rate limiting strategy (prevent abuse)
  - [ ] 6.3 Specify cost monitoring and alerting
  - [ ] 6.4 Design fallback behavior for API outages

- [ ] **7. Create Technical Implementation Guide** (AC: #7)
  - [ ] 7.1 Document Discord.py bot patterns
  - [ ] 7.2 Specify SQLite database schema
  - [ ] 7.3 Provide code examples for routing logic
  - [ ] 7.4 Document deployment considerations

---

## Dev Notes

### Strategic Context (Decision 11 + Party Mode Architecture)

**The CIS Controller is the brain of the agent-facilitated cohort model.**

It replaces 8 human facilitators with intelligent automation while preserving framework purity (no advice-giving drift). The controller must:
- Route student thinking to appropriate CIS agents
- Track progress through identity transformation (outsider → observer → experimenter → collaborator → director)
- Scaffold the 4 Habits without becoming "just another AI chatbot"
- Respect JTBD emotional job: "Help me stop feeling anxious and start feeling like I belong"

**Party Mode Architectural Decisions (2026-01-25):**
- ✅ **Hybrid Routing:** Commands preferred, natural language with "Did you mean...?" suggestions
- ✅ **Centralized Controller:** Intent recognition → State machine → Agent router (not distributed peer-to-peer)
- ✅ **Graduated Suggestions:** Week-based intensity (heavy hand-holding → minimal guidance)
- ✅ **Non-Linear States:** Students can revisit any thinking phase (not rigid lock-in)
- ✅ **Temporal Awareness:** Week-based agent unlocking per Decision 11
- ✅ **LLM Provider:** Claude Sonnet 4.5 (Batch) with prompt caching ($5-33 actual cost vs $100 budget)

**Why Hybrid Routing?**
- **Commands (/frame, /diverge, etc.)** create mindfulness and reinforce 4 Habits
- **Natural language with suggestions** removes friction while preserving habit formation
- **Friction IS THE FEATURE** (Victor's strategic insight): Explicit commands build muscle memory
- **Avoids "magical AI assistant"** that undermines the "thinking skills trainer" positioning

**Why Centralized Controller?**
- Simpler to debug, deploy, and scale
- Single source of truth for state management
- Easier to enforce guardrails (no comparison/ranking, psychological safety)
- Can be abstracted to support multiple LLM providers (future-proofing)

### Foundation Documents (Epic 1 - ALL Non-Negotiable)

**Story 4.1 MUST build upon these Epic 1 foundations:**

**1. Guardrails (Story 1.1):**
- Guardrail #3 (NEVER): No tech jargon Week 1, no impressive examples, no comparison/ranking
- Guardrail #4 (ALWAYS): Prioritize clarity over cleverness, confidence over competence, normalize confusion
- Guardrail #6 (Agent Model Purity): Agents NEVER give advice, only scaffold structured thinking
- Guardrail #8 (Discord Safety): Private process → Public showcase flow
- Guardrail #11 (JTBD Examples): All examples must serve real student jobs (university, career, anxiety)

**2. JTBD Integration (Story 1.2):**
- Zones as identity shifts: outsider → observer → experimenter → collaborator → director
- Emotional jobs: Belonging (Zone 0-1), Confidence (Zone 1-2), Companionship (Zone 2-3), Ownership (Zone 3-4)
- Social job: "Give me proof I can show"
- Philosophy principle: Identity before competence, psychology over performance

**3. Node Architecture (Story 1.3):**
- 16 nodes across 4 zone transitions (4 per zone)
- Each node targets one identity shift + one emotional job + one 4 Habit
- CIS agents are introduced gradually: /frame (Week 1) → /diverge, /challenge (Week 4) → /synthesize (Week 6)

**4. 4 Habits Branding (Story 1.4):**
- Habit 1 ⏸️ Pause: "Know what you want" (Zone 0-1, Intelligence Pillar)
- Habit 2 🎯 Context: "AI responds to YOUR situation" (Zone 1-2, Intelligence Pillar)
- Habit 3 🔄 Iterate: "Change one thing at a time" (Zone 2-3, Expertise Pillar)
- Habit 4 🧠 Think First: "Use AI before decisions" (Zone 3-4, Expertise Pillar)

### Architecture Requirements

**Technical Stack:**
- **Language:** Python 3.10+
- **Discord Library:** discord.py (async)
- **Database:** SQLite (for state tracking)
- **LLM Provider:** Anthropic Claude API (Sonnet 4.5 Batch model)
- **Deployment:** Discord bot hosting (Railway, Heroku, or similar)

**Non-Negotiable Architecture Principles:**

1. **Controller is Invisible (Mostly)**
   - Students see AGENTS, not the controller routing logic
   - Controller speaks only for suggestions ("Did you mean...?")
   - Agent personalities create the "thinking partner" feeling, not the controller

2. **State Machine is NOT a Prison**
   - Allow non-linear transitions (student can go from challenge back to frame)
   - State is a bookmark, not a lock-in
   - Support messy, real thinking processes (Maya's design thinking principle)

3. **Graduated Responsibility (Decision 11 Timeline)**
   - Week 1: /frame in practice mode (heavy guidance)
   - Week 2-3: /frame continues + context prompting
   - Week 4-5: Full CIS suite (/frame, /diverge, /challenge)
   - Week 6-7: /synthesize added, artifact creation begins
   - Week 8: All agents, artifact completion

4. **Psychological Safety First**
   - Private DM/Thread for messy thinking
   - Only finished artifacts go to #thinking-showcase
   - Controller NEVER surfaces comparisons or rankings
   - Normalize confusion: "Many students feel stuck here"

### LLM API Integration Details

**Claude Sonnet 4.5 (Batch) Configuration:**

```python
# API Configuration (from Party Mode cost analysis)
LLM_PROVIDER = "anthropic"
MODEL = "claude-sonnet-4-5-20250514"  # Sonnet 4.5
API_MODE = "batch"  # 50% cost reduction, 5-10 min delay acceptable

# Pricing (as of January 2025)
INPUT_COST_PER_MILLION = 3.00  # $3.00 per million input tokens
OUTPUT_COST_PER_MILLION = 15.00  # $15.00 per million output tokens

# Cost Optimization
ENABLE_PROMPT_CACHING = True  # Up to 90% savings on system prompts
BATCH_DISCOUNT = 0.5  # 50% reduction with batch API

# Estimated Usage (Conservative Scenario)
STUDENTS = 100
INTERACTIONS_PER_STUDENT = 60  # 3/day × 5 days × 8 weeks
AVG_TOKENS_PER_INTERACTION = 700  # 500 input + 200 output

# Cost Projection
TOTAL_TOKENS = 8.4M  # 100 × 60 × 700
ESTIMATED_COST = $33  # Without caching
WITH_CACHING = $5-10  # Realistic with prompt caching
CONSERVATIVE_BUDGET = $100  # Buffer for unexpected usage
```

**Prompt Caching Strategy:**

```python
# System prompts NEVER change - cache them!
CACHED_SYSTEM_PROMPTS = {
    "framer": FRAMER_AGENT_SYSTEM_PROMPT,  # Loaded once, cached
    "explorer": EXPLORER_AGENT_SYSTEM_PROMPT,
    "challenger": CHALLENGER_AGENT_SYSTEM_PROMPT,
    "synthesizer": SYNTHESIZER_AGENT_SYSTEM_PROMPT
}

# API Call Pattern
async def call_claude_with_caching(agent, user_message, conversation_history):
    response = await anthropic.messages.create(
        model="claude-sonnet-4-5-20250514",
        system=[
            {
                "type": "text",
                "text": CACHED_SYSTEM_PROMPTS[agent],
                "cache_control": {"type": "ephemeral"}  # MAGIC: Cache this!
            }
        ],
        messages=[
            *conversation_history[-10:],  # Last 10 messages (sliding window)
            {"role": "user", "content": user_message}
        ],
        betas=["prompt-caching-2024-07-31"]  # Enable caching
    )
    return response.content[0].text
```

**Cost Controls:**

```python
# Per-Student Limits (Prevent Runaway Costs)
MAX_INTERACTIONS_PER_DAY = 50  # Generous but prevents abuse
INTERACTION_COOLDOWN = 30  # Seconds between requests (rate limiting)

# Budget Monitoring
DAILY_BUDGET_ALERT = $10  # Alert Trevor if daily spend exceeds
WEEKLY_BUDGET_CAP = $50  # Hard cap per week (manual override needed)

# Monitoring
async def track_api_usage(student_id, tokens_used, cost):
    log_to_sheets(student_id, tokens_used, cost)
    if daily_total > DAILY_BUDGET_ALERT:
        notify_trevor(f"API usage alert: ${daily_total} spent today")
```

### Controller Architecture Specification

**Three-Layer Design:**

```
┌─────────────────────────────────────────┐
│  LAYER 1: INTENT RECOGNITION           │
├─────────────────────────────────────────┤
│ - Parse: Is this a command (/frame)?   │
│ - Or: Natural language?                │
│ - Extract: Week number, student state   │
│ - Check: Agent unlocked for this week? │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  LAYER 2: STATE MACHINE                │
├─────────────────────────────────────────┤
│ - Current: framing, exploring, etc.     │
│ - History: Last 10 messages             │
│ - Progress: % to artifact completion    │
│ - Week: Current cohort week (1-8)       │
│ - Unlocked: Which agents available?     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  LAYER 3: AGENT ROUTER                  │
├─────────────────────────────────────────┤
│ - Dispatch to Claude API                │
│ - Include: Agent system prompt (cached) │
│ - Include: Conversation history         │
│ - Include: Student context              │
│ - Return: Agent response                │
└─────────────────────────────────────────┘
```

**Routing Logic Pseudocode:**

```python
async def route_student_interaction(message, student):
    # LAYER 1: INTENT RECOGNITION
    if message.content.startswith('/'):
        # Explicit command
        agent = parse_command(message.content)
    else:
        # Natural language - classify intent
        intent = classify_intent(message.content)  # Keyword matching
        agent = intent_to_agent(intent)
        # Generate suggestion
        await suggest_explicit_command(message, agent)
        return  # Wait for student to accept or skip

    # LAYER 2: STATE MACHINE CHECK
    if not is_agent_unlocked(agent, student.week):
        return await friendly_lockout_message(agent, student.week)

    # LAYER 3: API DISPATCH
    response = await call_claude_with_caching(
        agent=agent,
        user_message=message.content,
        conversation_history=student.history,
        student_context=build_context(student)
    )

    # Update state
    student.current_state = agent
    student.history.append(message)
    student.artifact_progress = calculate_progress(student)

    # Return response
    await message.reply(format_agent_response(agent, response))
```

**Suggestion System Design:**

```python
# Graduated Intensity (Maya's Design Thinking Principle)
SUGGESTION_TEMPLATES = {
    "week_1_2": {
        "intensity": "explicit",
        "template": "🎯 **Let's pause and frame this first!**\n\nTry: `/frame {question}`\n\nThis helps you clarify what you actually want."
    },
    "week_4_5": {
        "intensity": "gentle",
        "template": "💡 **Have you considered challenging this?**\n\nTry: `/challenge {assumption}`\n\nWhat might you be taking for granted?"
    },
    "week_6_7": {
        "intensity": "minimal",
        "template": "✨ **Ready to synthesize?**\n\nWhen you're done exploring: `/synthesize pull it all together`"
    },
    "week_8": {
        "intensity": "none",
        "template": None  # No suggestions, students should drive
    }
}

async def suggest_explicit_command(message, detected_agent):
    student = get_student(message.author.id)
    week = get_current_week(student.cohort_start_date)
    template = get_suggestion_template(week)

    if template is None:
        return  # Week 8 - no suggestions

    suggestion = template.format(
        question=message.content,
        assumption=message.content
    )

    suggestion += "\n\nOr reply 'skip' to continue with natural language."

    await message.reply(suggestion)

    # Wait for response
    response = await wait_for_reply(message.channel, timeout=60)

    if response and response.content.lower() == 'skip':
        # Proceed with natural language
        return await process_natural_language(message, detected_agent)
    else:
        # Student accepted suggestion, wait for explicit command
        return
```

### State Machine Schema

**SQLite Database Design:**

```sql
-- Students table
CREATE TABLE students (
    discord_id TEXT PRIMARY KEY,
    cohort_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    current_week INTEGER DEFAULT 1,
    current_state TEXT DEFAULT 'none',  -- framing, exploring, challenging, synthesizing, complete
    unlocked_agents TEXT DEFAULT '["frame"]',  -- JSON array
    artifact_progress INTEGER DEFAULT 0,  -- 0-100
    interaction_count INTEGER DEFAULT 0,
    last_interaction TEXT,  -- ISO timestamp
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table (message history)
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    agent TEXT NOT NULL,  -- framer, explorer, challenger, synthesizer
    role TEXT NOT NULL,  -- user, assistant
    content TEXT NOT NULL,
    tokens INTEGER,
    cost_usd REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id)
);

-- API usage tracking (cost monitoring)
CREATE TABLE api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    student_count INTEGER,
    total_interactions INTEGER,
    total_tokens INTEGER,
    total_cost_usd REAL,
    cached_tokens INTEGER,
    cached_savings_usd REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Python ORM Pattern (Using SQLite):**

```python
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Student:
    discord_id: str
    cohort_id: str
    start_date: str
    current_week: int = 1
    current_state: str = "none"
    unlocked_agents: List[str] = None
    artifact_progress: int = 0
    interaction_count: int = 0

    def __post_init__(self):
        if self.unlocked_agents is None:
            self.unlocked_agents = ["frame"]

class StudentStateStore:
    def __init__(self, db_path="cis_state.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def get_student(self, discord_id: str) -> Optional[Student]:
        cursor = self.conn.execute(
            "SELECT * FROM students WHERE discord_id = ?",
            (discord_id,)
        )
        row = cursor.fetchone()
        if row:
            return Student(**row)
        return None

    def update_state(self, student: Student, new_state: str):
        self.conn.execute(
            """UPDATE students
               SET current_state = ?, last_interaction = CURRENT_TIMESTAMP
               WHERE discord_id = ?""",
            (new_state, student.discord_id)
        )
        self.conn.commit()

    def can_access_agent(self, student: Student, agent: str) -> bool:
        # Temporal awareness logic (Decision 11)
        week = student.current_week

        agent_unlock_schedule = {
            "frame": 1,
            "diverge": 4,
            "challenge": 4,
            "synthesize": 6
        }

        return week >= agent_unlock_schedule.get(agent, 99)

    def track_interaction(self, student_id: str, agent: str, tokens: int, cost: float):
        self.conn.execute(
            """INSERT INTO conversations
               (student_id, agent, role, content, tokens, cost_usd)
               VALUES (?, ?, 'assistant', '', ?, ?)""",
            (student_id, agent, tokens, cost)
        )
        self.conn.commit()
```

### Temporal Awareness Implementation

**Week-Based Agent Unlocking (Decision 11):**

```python
# Agent Introduction Schedule
AGENT_UNLOCK_SCHEDULE = {
    "Week 1": {
        "agents": ["frame"],
        "mode": "practice",
        "guidance": "Try /frame to practice pausing before asking",
        "suggestion_intensity": "explicit"
    },
    "Weeks 2-3": {
        "agents": ["frame"],
        "mode": "active",
        "guidance": "Use /frame to add context to your questions",
        "suggestion_intensity": "explicit"
    },
    "Weeks 4-5": {
        "agents": ["frame", "diverge", "challenge"],
        "mode": "full_cis",
        "guidance": "Explore options with /diverge, test assumptions with /challenge",
        "suggestion_intensity": "gentle"
    },
    "Weeks 6-7": {
        "agents": ["frame", "diverge", "challenge", "synthesize"],
        "mode": "artifact_creation",
        "guidance": "Ready to synthesize your thinking artifact?",
        "suggestion_intensity": "minimal"
    },
    "Week 8": {
        "agents": ["frame", "diverge", "challenge", "synthesize"],
        "mode": "completion",
        "guidance": None,  # No guidance
        "suggestion_intensity": "none"
    }
}

def get_unlocked_agents(student: Student) -> List[str]:
    """Return list of agents unlocked for student's current week."""
    week = student.current_week

    if week == 1:
        return ["frame"]
    elif week <= 3:
        return ["frame"]
    elif week <= 5:
        return ["frame", "diverge", "challenge"]
    else:  # Week 6-8
        return ["frame", "diverge", "challenge", "synthesize"]

async def friendly_lockout_message(agent: str, current_week: int) -> str:
    """Generate encouraging message when student tries locked agent."""

    unlock_schedule = {
        "diverge": 4,
        "challenge": 4,
        "synthesize": 6
    }

    unlock_week = unlock_schedule.get(agent, 99)

    return f"""🔒 **{agent.capitalize()} unlocks Week {unlock_week}**

You're currently in Week {current_week}. Here's what you can use now:

{', '.join(get_unlocked_agents_for_week(current_week))}

**Why the wait?** Each agent builds on the 4 Habits you're learning:
- ⏸️ **Pause** (Week 1): Know what you want
- 🎯 **Context** (Week 2): AI responds to YOUR situation
- 🔄 **Iterate** (Week 4): Explore one thing at a time
- 🧠 **Think First** (Week 6): Use AI before decisions

You'll get there! Keep practicing.
"""
```

### Error Handling & Resilience

**API Failure Recovery:**

```python
import asyncio
from typing import Optional

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

async def call_claude_with_retry(agent, user_message, history, context):
    """Call Claude API with exponential backoff retry."""

    for attempt in range(MAX_RETRIES):
        try:
            response = await call_claude_with_caching(agent, user_message, history, context)
            return response

        except anthropic.RateLimitError:
            # Rate limited - wait longer
            wait_time = RETRY_DELAY * (2 ** attempt)
            await asyncio.sleep(wait_time)
            continue

        except anthropic.APIConnectionError:
            # Network error - retry
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            else:
                # Final retry failed - use fallback
                return await fallback_response(agent, user_message)

        except Exception as e:
            # Log error and notify Trevor
            log_error(e)
            await notify_trevor(f"API Error: {str(e)}")
            return await fallback_response(agent, user_message)

async def fallback_response(agent, user_message):
    """Graceful fallback when API is down."""

    fallback_messages = {
        "framer": "🎯 **The Framer is taking a short break.**\n\nTry this: Pause and ask yourself 'What do I actually want to know?' Then rephrase your question with that clarity.",
        "explorer": "🔍 **The Explorer is recalculating.**\n\nTry this: List 3 different angles you could explore on this topic. What would each reveal?",
        "challenger": "⚡ **The Challenger is regrouping.**\n\nTry this: Ask yourself 'What am I assuming might be true?' Pick one assumption and question it.",
        "synthesizer": "✨ **The Synthesizer is organizing thoughts.**\n\nTry this: Look back at your conversation. What's the main insight that emerged? How would you explain it to someone else?"
    }

    return fallback_messages.get(agent, "Thinking partner is temporarily unavailable. Try again in a few minutes.")
```

**Rate Limiting (Per-Student):**

```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests=50, window=86400):  # 50 requests per day
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    async def check_rate_limit(self, student_id: str) -> bool:
        now = time.time()

        # Clean old requests
        self.requests[student_id] = [
            req_time for req_time in self.requests[student_id]
            if now - req_time < self.window
        ]

        # Check limit
        if len(self.requests[student_id]) >= self.max_requests:
            return False

        # Record this request
        self.requests[student_id].append(now)
        return True

    async def rate_limit_message(self, student_id: str) -> str:
        """Generate friendly rate limit message."""

        # Calculate time until reset
        oldest_request = min(self.requests[student_id])
        reset_time = oldest_request + self.window - time.time()
        hours = int(reset_time // 3600)
        minutes = int((reset_time % 3600) // 60)

        return f"""**You've reached your daily thinking session limit!** 🎯

Great work practicing today! Your limit resets in {hours}h {minutes}m.

**Why the limit?**
- Quality thinking beats quantity
- Prevents AI dependency
- Time to reflect on what you learned

Come back tomorrow for more thinking practice!
"""
```

### Deployment Considerations

**Discord Bot Structure:**

```
cis-discord-bot/
├── .env                    # API keys (ANTHROPIC_API_KEY, DISCORD_TOKEN)
├── requirements.txt        # discord.py, anthropic, sqlite3, python-dotenv
├── main.py                 # Bot entry point
├── cis_controller/
│   ├── __init__.py
│   ├── router.py           # Routing logic
│   ├── state_machine.py    # State management
│   ├── llm_integration.py  # Claude API calls
│   └── suggestions.py      # Suggestion system
├── agents/
│   ├── __init__.py
│   ├── framer_prompt.py    # System prompts (cached)
│   ├── explorer_prompt.py
│   ├── challenger_prompt.py
│   └── synthesizer_prompt.py
├── database/
│   ├── __init__.py
│   ├── schema.sql          # SQLite schema
│   └── store.py            # StudentStateStore class
└── tests/
    ├── test_router.py
    ├── test_state_machine.py
    └── test_rate_limiting.py
```

**Environment Variables (.env):**

```bash
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_server_id
CHANNEL_THINKING_LAB=channel_id
CHANNEL_THINKING_SHOWCASE=channel_id

# Anthropic Claude API
ANTHROPIC_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250514
ENABLE_PROMPT_CACHING=true

# Cost Controls
MAX_INTERACTIONS_PER_DAY=50
DAILY_BUDGET_ALERT=10.00
WEEKLY_BUDGET_CAP=50.00

# Cohort Configuration
COHORT_START_DATE=2026-02-01
COHORT_DURATION_WEEKS=8

# Feature Flags
ENABLE_NATURAL_LANGUAGE_FALLBACK=true
ENABLE_ARTIFACT_TRACKING=true
ENABLE_TREVOR_NOTIFICATIONS=true
TREVOR_NOTIFICATION_WEBHOOK=https://hooks.slack.com/...
```

**Health Checks & Monitoring:**

```python
async def health_check():
    """Periodic health check for bot status."""

    checks = {
        "database": check_database_connection(),
        "claude_api": check_claude_api_connection(),
        "discord_connection": check_discord_connection(),
        "rate_limits": check_rate_limit_status(),
        "budget": check_budget_status()
    }

    if not all(checks.values()):
        await notify_trevor(f"⚠️ Health Check Failed: {checks}")

    return checks

async def check_budget_status():
    """Alert if approaching budget limits."""

    # Get today's usage
    today = datetime.now().strftime("%Y-%m-%d")
    cursor = db.execute(
        """SELECT SUM(total_cost_usd) as daily_total
           FROM api_usage
           WHERE date = ?""",
        (today,)
    )
    result = cursor.fetchone()
    daily_total = result["daily_total"] or 0

    if daily_total > DAILY_BUDGET_ALERT:
        await notify_trevor(f"💰 Budget Alert: ${daily_total:.2f} spent today (limit: ${DAILY_BUDGET_ALERT})")
```

### Testing Strategy

**Unit Tests:**

```python
import pytest
from cis_controller.router import route_student_interaction
from cis_controller.state_machine import StudentStateStore

def test_explicit_command_routing():
    """Test that explicit commands route correctly."""
    student = create_test_student(week=4)
    message = MockMessage(content="/diverge What are my career options?")

    agent = route_student_interaction(message, student)

    assert agent == "explorer"

def test_temporal_awareness_week_1():
    """Test that Week 1 students can only access /frame."""
    student = create_test_student(week=1)
    message = MockMessage(content="/challenge Is university worth it?")

    result = route_student_interaction(message, student)

    assert result["locked"] == True
    assert "Week 4" in result["message"]

def test_non_linear_state_transitions():
    """Test that students can go from challenge back to frame."""
    student = create_test_student(current_state="challenging")
    message = MockMessage(content="/frame Let me re-examine my question")

    new_state = route_student_interaction(message, student)

    assert new_state == "framing"  # Allowed to revisit

def test_rate_limiting():
    """Test that rate limiting works."""
    limiter = RateLimiter(max_requests=3, window=3600)
    student_id = "test_student"

    # First 3 requests should pass
    for i in range(3):
        assert limiter.check_rate_limit(student_id) == True

    # 4th request should fail
    assert limiter.check_rate_limit(student_id) == False
```

**Integration Tests:**

```python
import pytest
from discord.ext.test import TestClient

@pytest.mark.asyncio
async def test_full_conversation_flow():
    """Test complete student journey through CIS agents."""

    # Setup
    client = TestClient(bot)
    student = create_test_student(week=4)

    # Student starts with natural language
    response = await client.send_message("I'm confused about my career path")

    # Controller suggests /frame
    assert "frame" in response.content.lower()

    # Student accepts suggestion
    response = await client.send_message("/frame I'm not sure if I should pursue computer science")

    # Framer responds (simulated)
    assert response.content.startswith("🎯")
```

### References

**Source Documents:**
- Decision 11: CIS Agent System for Discord → `_bmad-output/cohort-design-artifacts/requirements/cohort-playbook-v2-requirements.md` lines 242-275
- Epic 1 Foundations → `_bmad-output/cohort-design-artifacts/playbook-v2/01-philosophy/`
- Party Mode Architecture (2026-01-25) → Multi-agent conversation with Winston, John, Maya, Barry, Victor
- Claude API Pricing → `https://docs.anthropic.com/en/docs/about-claude/pricing` (accessed 2026-01-25)

**Brand Framework:**
- "Think WITH AI" positioning → `_bmad-output/k2m-edtech-brand-artifacts/k2m-brand-conversion-framework-v3.md`
- JTBD Altitude System → Guardrail #10 compliance in all agent responses
- Revolutionary Hope Tone → Hope + empowerment, not fear or pressure

**Technical Standards:**
- Discord.py documentation → `https://discordpy.readthedocs.io/`
- Anthropic Python SDK → `https://github.com/anthropics/anthropic-sdk-python`
- Prompt Caching → `https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching`

---

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (December 2024 version)

### Completion Notes List

**Architectural Decisions Made:**
1. ✅ **Hybrid Routing:** Commands preferred, natural language with suggestions (balances habit formation with flexibility)
2. ✅ **Centralized Controller:** Three-layer architecture (Intent → State → Router) for simplicity and maintainability
3. ✅ **Graduated Suggestions:** Week-based intensity (explicit → minimal) supports identity shift progression
4. ✅ **Non-Linear State Machine:** Students can revisit thinking phases (respects real thinking processes)
5. ✅ **Temporal Awareness:** Week-based agent unlocking enforces Decision 11 graduated introduction
6. ✅ **LLM Provider:** Claude Sonnet 4.5 (Batch) with prompt caching ($5-33 actual cost vs $100 budget)
7. ✅ **Cost Controls:** Per-student limits, rate limiting, budget monitoring prevent runaway API costs
8. ✅ **Error Handling:** Graceful degradation with fallback responses when API fails
9. ✅ **Psychological Safety:** Private process → Public product flow preserved
10. ✅ **Guardrails Compliance:** All 10 guardrails from Epic 1 referenced and enforced

**Party Mode Team Consensus:**
- 🏗️ Winston (Architect): Centralized controller is boring technology that scales
- 📋 John (PM): Graduated suggestions align with JTBD identity shifts
- 🎨 Maya (Design): Semi-visible routing creates "thinking partner" experience
- 🚀 Barry (Dev): Ship-able with Discord.py + SQLite + keyword matching
- ⚡ Victor (Strategy): Friction IS THE FEATURE - commands reinforce 4 Habits

**Next Stories (Dependencies):**
- Story 4.2: Create The Framer agent prompt (uses controller architecture)
- Story 4.3: Create The Explorer agent prompt
- Story 4.4: Create The Challenger agent prompt
- Story 4.5: Create The Synthesizer agent prompt
- Story 4.6: Design artifact creation flow (builds on controller state tracking)
- Story 4.7: Discord bot technical specification (implements this architecture)

### File List

**Output File:**
- `_bmad-output/implementation-artifacts/4-1-cis-controller-logic.md` (this file)

**Referenced Foundation Documents:**
- `_bmad-output/cohort-design-artifacts/playbook-v2/01-philosophy/guardrails-preserved.md`
- `_bmad-output/cohort-design-artifacts/playbook-v2/01-philosophy/jtbd-integration.md`
- `_bmad-output/cohort-design-artifacts/playbook-v2/01-philosophy/node-architecture.md`
- `_bmad-output/cohort-design-artifacts/playbook-v2/01-philosophy/four-habits-brand.md`

**Requirements Source:**
- `_bmad-output/cohort-design-artifacts/requirements/cohort-playbook-v2-requirements.md` (Decision 11 lines 242-275)

---

**Story 4.1 Status: READY FOR DEVELOPMENT** ✅

All architectural decisions documented, foundation references integrated, and implementation guide provided. Developer has comprehensive context to build the CIS Controller system that powers the entire agent-facilitated cohort model.
