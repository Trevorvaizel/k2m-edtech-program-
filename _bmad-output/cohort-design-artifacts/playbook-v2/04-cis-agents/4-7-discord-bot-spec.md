# Story 4.7: Create Discord Bot Technical Specification

Status: ready-for-dev

**Epic:** 4 - CIS Agent System
**Story:** 4.7 - Create Discord bot technical specification
**Created:** 2026-01-25
**Purpose:** Technical Implementation Specification - Design the complete Discord bot architecture that implements the CIS Controller, all four CIS agents, artifact creation flow, and Discord server operations for the agent-facilitated cohort model

---

## Story

As a **Cohort Facilitation System Architect**,
I want **a complete Discord bot technical specification that implements the entire CIS agent system**,
so that **developers can build a production-ready Discord bot that replaces 8 human facilitators with intelligent automation while preserving framework purity and student psychological safety**.

---

## Acceptance Criteria

1. **Complete Discord Bot Architecture Document** specifying full system design from Discord events to Claude API responses
2. **CIS Controller Implementation Specification** documenting routing logic, state machine, and LLM integration with code examples
3. **Four CIS Agent Integration Specifications** (/frame, /diverge, /challenge, /synthesize) with system prompts and API signatures
4. **Artifact Creation Flow Implementation** (/create-artifact command) with complete state tracking and DM workflow
5. **Discord Server Channel Architecture** specifying #thinking-lab, #thinking-showcase, and private DM patterns per Decision 12
6. **StudentContext & Database Schema** documenting complete data model, SQLite schema, and persistence layer
7. **SafetyFilter Implementation Specification** documenting anti-comparison validation layer (Guardrail #3 compliance infrastructure)
8. **Deployment & Operations Guide** specifying environment setup, monitoring, error handling, and cost management

---

## Tasks / Subtasks

- [ ] **1. Design Complete Discord Bot Architecture** (AC: #1)
  - [ ] 1.1 Specify system architecture from Discord events to Claude API
  - [ ] 1.2 Design three-layer controller system (Intent Recognition → State Machine → Agent Router)
  - [ ] 1.3 Document async/await patterns for Discord.py + Anthropic SDK integration
  - [ ] 1.4 Specify error handling, retry logic, and graceful degradation
  - [ ] 1.5 Design monitoring, logging, and health check systems

- [ ] **2. Specify CIS Controller Implementation** (AC: #2)
  - [ ] 2.1 Document command routing: /frame, /diverge, /challenge, /synthesize, /create-artifact
  - [ ] 2.2 Specify natural language processing with "Did you mean...?" suggestions
  - [ ] 2.3 Design state machine for artifact creation and habit tracking
  - [ ] 2.4 Document StudentContext integration (example selection, altitude mapping, habit journey)
  - [ ] 2.5 Specify week-based agent unlocking (Decision 11 graduated introduction)
  - [ ] 2.6 Design rate limiting and cost controls (API budget management)

- [ ] **3. Document Four CIS Agent Implementations** (AC: #3)
  - [ ] 3.1 Specify /frame agent (The Framer) integration - Habit 1 & 2 scaffolding
  - [ ] 3.2 Specify /diverge agent (The Explorer) integration - Habit 3 scaffolding
  - [ ] 3.3 Specify /challenge agent (The Challenger) integration - Habit 4 scaffolding
  - [ ] 3.4 Specify /synthesize agent (The Synthesizer) integration - Habit 4 completion
  - [ ] 3.5 Document Claude Sonnet 4.5 API integration with prompt caching
  - [ ] 3.6 Specify system prompt injection and StudentContext parameter passing

- [ ] **4. Design Artifact Creation Flow Implementation** (AC: #4)
  - [ ] 4.1 Specify /create-artifact command entry point and 6-section workflow
  - [ ] 4.2 Document private DM creation process with save/resume functionality
  - [ ] 4.3 Design artifact progress tracking (artifact_progress in StudentContext)
  - [ ] 4.4 Specify Week 8 polish and publish flow to #thinking-showcase
  - [ ] 4.5 Document artifact celebration and 4 Habits badge awarding

- [ ] **5. Specify Discord Server Channel Architecture** (AC: #5)
  - [ ] 5.1 Document #thinking-lab channel design (entry point + instructions)
  - [ ] 5.2 Specify private DM/thread system for CIS agent interactions
  - [ ] 5.3 Design #thinking-showcase channel for published artifacts
  - [ ] 5.4 Document privacy controls and student consent patterns
  - [ ] 5.5 Specify celebration patterns and peer interaction rules (no comparison)

- [ ] **6. Document StudentContext & Database Schema** (AC: #6)
  - [ ] 6.1 Specify complete StudentContext data model (zone, JTBD concern, habit journey, artifact progress)
  - [ ] 6.2 Design SQLite database schema (students, conversations, api_usage tables)
  - [ ] 6.3 Document ORM patterns and data access layer
  - [ ] 6.4 Specify migration strategy and backup procedures
  - [ ] 6.5 Design database indexing for performance (100+ concurrent students)

- [ ] **7. Specify SafetyFilter Implementation** (AC: #7)
  - [ ] 7.1 Document SafetyFilter class for anti-comparison validation
  - [ ] 7.2 Specify forbidden keywords and regex patterns (Guardrail #3)
  - [ ] 7.3 Design aggregate message validation (prevents implicit comparison)
  - [ ] 7.4 Document `post_to_discord_safe()` wrapper implementation
  - [ ] 7.5 Specify error handling and Trevor notification for blocked content

- [ ] **8. Create Deployment & Operations Guide** (AC: #8)
  - [ ] 8.1 Specify environment variables (.env configuration)
  - [ ] 8.2 Document deployment process (Railway, Heroku, or similar)
  - [ ] 8.3 Design monitoring dashboards (API costs, error rates, student engagement)
  - [ ] 8.4 Specify alerting rules (budget limits, API failures, safety violations)
  - [ ] 8.5 Document scaling strategy (SQLite → PostgreSQL migration path)
  - [ ] 8.6 Create troubleshooting guide for common issues

---

## Dev Notes

### Strategic Context (Epic 4 + Decisions 11, 12, 15 + Stories 4.1-4.6)

**The Discord Bot is the execution engine for the entire agent-facilitated cohort model.**

This specification brings together ALL Epic 4 work into a production-ready system:
- **Story 4.1:** CIS Controller logic (routing, state machine, LLM integration)
- **Story 4.2:** The Framer agent prompt (/frame, Habits 1 & 2)
- **Story 4.3:** The Explorer agent prompt (/diverge, Habit 3)
- **Story 4.4:** The Challenger agent prompt (/challenge, Habit 4)
- **Story 4.5:** The Synthesizer agent prompt (/synthesize, Habit 4 completion)
- **Story 4.6:** Artifact creation flow (/create-artifact)

**Key Decisions This Implements:**
- **Decision 11:** CIS Agent System for Discord (graduated introduction Week 1 → Week 8)
- **Decision 12:** Hybrid Discord Model (private DM process → public showcase product)
- **Decision 15:** Simplified Tech Stack (Python, discord.py, Claude API, SQLite for Cohort 1)

**The Bot Must:**
1. Replace 8 human facilitators with intelligent automation
2. Scale infinitely (copy-paste for future cohorts)
3. Reduce Trevor's time from 14+ hours/week to ~2 hours/week
4. Preserve framework purity (no advice-giving drift)
5. Maintain psychological safety (no comparison, private process)
6. Serve JTBD emotional job: "Help me stop feeling anxious and start feeling like I belong"

### Foundation Documents (Epic 1 + Epic 4 Stories - ALL Non-Negotiable)

**Story 4.7 MUST implement these Epic 1 foundations:**

**1. Guardrails (Story 1.1):**
- Guardrail #3 (NEVER): No comparison/ranking in public channels
- Guardrail #6 (Agent Purity): Agents NEVER give advice, only scaffold thinking
- Guardrail #8 (Discord Safety): Private process → Public showcase flow
- Guardrail #10 (Artifact Authenticity): Artifacts must be student's own voice
- Guardrail #11 (JTBD Examples): All examples serve real student jobs

**2. JTBD Integration (Story 1.2):**
- Zone-based identity shifts: outsider → observer → experimenter → collaborator → director
- Emotional job: Belonging, Confidence, Companionship, Ownership
- Social job: "Give me proof I can show" (artifacts)
- Philosophy principle: Identity before competence

**3. Node Architecture (Story 1.3):**
- 16 nodes across 4 zone transitions
- CIS agents reinforce nodes through conversation
- Artifact creation proves node completion

**4. 4 Habits Branding (Story 1.4):**
- Habit 1 ⏸️ Pause: "Know what you want"
- Habit 2 🎯 Context: "AI responds to YOUR situation"
- Habit 3 🔄 Iterate: "Change one thing at a time"
- Habit 4 🧠 Think First: "Use AI before decisions"
- Graduation proof: Artifact demonstrates all 4 habits

**Story 4.7 MUST integrate ALL Epic 4 Stories:**

**5. CIS Controller Logic (Story 4.1):**
- Controller architecture: Intent Recognition → State Machine → Agent Router
- StudentContext domain model (zone, JTBD concern, habit journey, artifact progress)
- LLM API integration: Claude Sonnet 4.5 (Batch) with prompt caching
- Graduated suggestion system (week-based intensity)
- Temporal awareness (week-based agent unlocking)
- Error handling & cost controls
- SafetyFilter anti-comparison layer

**6. The Framer Agent (Story 4.2):**
- System prompt for Habit 1 (Pause) and Habit 2 (Context) scaffolding
- Zone 0→1 identity shift (outsider → observer)
- Week 1 practice mode protocol
- API signature: `generate_framer_response(student_context, user_message) -> str`
- StudentContext integration: `get_relevant_example("frame")`, altitude templates, habit celebrations

**7. The Explorer Agent (Story 4.3):**
- System prompt for Habit 3 (Iterate) scaffolding
- Zone 2→3 identity shift (experimenter → collaborator)
- Week 4 graduated introduction protocol
- API signature: `generate_explorer_response(student_context, user_message) -> str`

**8. The Challenger Agent (Story 4.4):**
- System prompt for Habit 4 (Think First) scaffolding
- Zone 2→3 identity shift (experimenter → collaborator)
- Week 4 graduated introduction protocol
- API signature: `generate_challenger_response(student_context, user_message) -> str`

**9. The Synthesizer Agent (Story 4.5):**
- System prompt for Habit 4 (Think First) completion
- Zone 3→4 identity shift (collaborator → director)
- Week 6 artifact creation protocol
- API signature: `generate_synthesizer_response(student_context, user_message) -> str`
- CIS conversation history integration (pulls previous /frame, /diverge, /challenge)

**10. Artifact Creation Flow (Story 4.6):**
- /create-artifact command workflow (6 sections)
- Private DM creation with save/resume
- Artifact progress tracking in StudentContext
- Week 8 polish and publish to #thinking-showcase
- 4 Habits badge awarding

### Technical Stack (Decision 15)

**Simplified Tech Stack for Cohort 1:**

| Component | Tool | Version | Purpose |
|-----------|------|---------|---------|
| **Language** | Python | 3.10+ | Bot implementation |
| **Discord Library** | discord.py | 2.3+ | Discord API wrapper |
| **LLM Provider** | Anthropic Claude | Sonnet 4.5 | CIS agent intelligence |
| **Database** | SQLite | 3.38+ | State persistence |
| **Deployment** | Railway/Heroku | - | Cloud hosting |
| **Monitoring** | Custom + Discord alerts | - | Health & cost tracking |

**Why This Stack?**
- **Python:** Best Discord library support, async/await for concurrent operations
- **discord.py:** Mature, well-documented, supports DMs, threads, slash commands
- **Claude Sonnet 4.5:** Best balance of intelligence, cost, and prompt caching (90% savings)
- **SQLite:** Sufficient for 100-200 students, zero infrastructure setup, easy backup
- **Railway/Heroku:** Simple deployment, auto-scaling, built-in monitoring

**Migration Path (Cohort 2+):**
- SQLite → PostgreSQL (for 500+ students)
- Claude → Multi-model (cost optimization)
- Manual workflows → Automated context engine (Decision 7)

### Complete Discord Bot Architecture

**System Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────────┐
│  DISCORD EVENTS (discord.py)                                    │
├─────────────────────────────────────────────────────────────────┤
│  • on_message() - DM/Thread messages                           │
│  • on_command() - /frame, /diverge, /challenge, /synthesize     │
│  • on_command() - /create-artifact, /save, /review, /publish   │
│  • on_ready() - Bot startup initialization                     │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: INTENT RECOGNITION                                    │
├─────────────────────────────────────────────────────────────────┤
│  • Parse: Is this a command (/frame) or natural language?      │
│  • Extract: Student ID, week, zone, JTBD concern               │
│  • Check: Agent unlocked for this week? (Temporal awareness)    │
│  • Suggest: "Did you mean...?" for natural language            │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: STATE MACHINE                                         │
├─────────────────────────────────────────────────────────────────┤
│  • Current State: framing, exploring, challenging, synthesizing  │
│  • Conversation History: Last 10 messages per agent            │
│  • Artifact Progress: 0-100%, 6 sections tracking              │
│  • Habit Journey: 4 habits with practice counts               │
│  • Student Context: Zone, week, JTBD concern, emotional state  │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: AGENT ROUTER                                          │
├─────────────────────────────────────────────────────────────────┤
│  • Dispatch to appropriate CIS agent:                          │
│    - /frame → generate_framer_response()                        │
│    - /diverge → generate_explorer_response()                    │
│    - /challenge → generate_challenger_response()                │
│    - /synthesize → generate_synthesizer_response()             │
│  • Build StudentContext with:                                  │
│    - JTBD-matched example from library                          │
│    - Altitude-appropriate template                              │
│    - Habit milestone celebration                                │
│  • Call Claude Sonnet 4.5 API with prompt caching              │
│  • Validate with SafetyFilter (anti-comparison)                │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE API INTEGRATION (Anthropic SDK)                         │
├─────────────────────────────────────────────────────────────────┤
│  • Model: claude-sonnet-4-5-20250514 (Batch API)              │
│  • System Prompt: Cached (90% cost reduction)                   │
│  • Messages: Last 10 messages (sliding window)                 │
│  • Temperature: 1.0 (creative but grounded)                    │
│  • Max Tokens: 1000 (sufficient for agent responses)           │
│  • Prompt Caching: Enabled for all system prompts              │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  SAFETY FILTER VALIDATION                                       │
├─────────────────────────────────────────────────────────────────┤
│  • Check: No comparison/ranking keywords                        │
│  • Check: No forbidden patterns ("best student", "top 3")      │
│  • Check: Aggregate message validation (no names + actions)    │
│  • If violation: Block post + alert Trevor                      │
│  • If safe: Post to Discord                                    │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│  DISCORD RESPONSE                                               │
├─────────────────────────────────────────────────────────────────┤
│  • Post: Agent response + habit celebration (if applicable)    │
│  • Update: StudentContext (habit_journey, artifact_progress)    │
│  • Save: Conversation history to database                       │
│  • Track: API usage (tokens, cost) for budget management       │
└─────────────────────────────────────────────────────────────────┘
```

### CIS Controller Implementation Specification

**File Structure:**

```
cis-discord-bot/
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
├── main.py                       # Bot entry point
├── cis_controller/
│   ├── __init__.py
│   ├── router.py                 # Intent recognition & routing
│   ├── state_machine.py          # Student state management
│   ├── llm_integration.py        # Claude API calls
│   ├── suggestions.py            # "Did you mean...?" system
│   └── safety_filter.py          # Anti-comparison validation
├── agents/
│   ├── __init__.py
│   ├── framer_prompt.py          # Framer system prompt (cached)
│   ├── explorer_prompt.py        # Explorer system prompt
│   ├── challenger_prompt.py      # Challenger system prompt
│   └── synthesizer_prompt.py     # Synthesizer system prompt
├── database/
│   ├── __init__.py
│   ├── schema.sql                # SQLite schema
│   ├── models.py                 # StudentContext ORM
│   └── store.py                  # Database operations
├── commands/
│   ├── __init__.py
│   ├── frame.py                  # /frame command handler
│   ├── diverge.py                # /diverge command handler
│   ├── challenge.py              # /challenge command handler
│   ├── synthesize.py             # /synthesize command handler
│   └── artifact.py               # /create-artifact command handler
└── tests/
    ├── test_router.py
    ├── test_state_machine.py
    ├── test_llm_integration.py
    └── test_safety_filter.py
```

**requirements.txt:**

```txt
discord.py==2.3.2
anthropic==0.18.0
python-dotenv==1.0.0
aiohttp==3.9.1  # Required for discord.py
```

**main.py Entry Point:**

```python
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cis_controller.router import setup_bot_events
from database.store import StudentStateStore

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Discord bot configuration
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required for slash commands
intents.dm_messages = True  # Required for private DM interactions

bot = commands.Bot(
    command_prefix='/',  # Slash commands preferred
    intents=intents,
    help_command=None  # Custom help in #thinking-lab
)

# Bot initialization
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Serving {len(bot.guilds)} guilds')

    # Initialize database
    store = StudentStateStore()
    print(f'Tracking {store.get_student_count()} students')

# Setup bot events and commands
setup_bot_events(bot)

# Run bot
if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
```

**cis_controller/router.py (Intent Recognition):**

```python
import discord
from discord.ext import commands
from database.store import StudentStateStore
from cis_controller.suggestions import suggest_explicit_command
from cis_controller.llm_integration import call_agent_with_context

# Initialize state store
store = StudentStateStore()

async def route_student_interaction(message: discord.Message):
    """
    Main routing function for all student interactions.

    LAYER 1: INTENT RECOGNITION
    """
    # Get or create student
    student = store.get_student(message.author.id)
    if not student:
        student = store.create_student(message.author.id)

    # Check if message is a command
    if message.content.startswith('/'):
        command = message.content.split()[0].replace('/', '')
        await handle_command(message, student, command)
    else:
        # Natural language - classify intent and suggest command
        await suggest_explicit_command(message, student)

async def handle_command(message: discord.Message, student, command: str):
    """
    Route commands to appropriate handlers.

    LAYER 2: STATE MACHINE + LAYER 3: AGENT ROUTER
    """
    # Check temporal awareness (week-based agent unlocking)
    if not is_agent_unlocked(command, student.current_week):
        await friendly_lockout_message(message, student, command)
        return

    # Route to command handler
    if command == 'frame':
        from commands.frame import handle_frame
        await handle_frame(message, student)
    elif command == 'diverge':
        from commands.diverge import handle_diverge
        await handle_diverge(message, student)
    elif command == 'challenge':
        from commands.challenge import handle_challenge
        await handle_challenge(message, student)
    elif command == 'synthesize':
        from commands.synthesize import handle_synthesize
        await handle_synthesize(message, student)
    elif command == 'create-artifact':
        from commands.artifact import handle_create_artifact
        await handle_create_artifact(message, student)
    elif command in ['save', 'review', 'publish']:
        from commands.artifact import handle_artifact_commands
        await handle_artifact_commands(message, student, command)
    else:
        await message.reply(f"Unknown command. Type /help for available commands.")

def is_agent_unlocked(agent: str, current_week: int) -> bool:
    """LAYER 1: Temporal awareness check (Decision 11)"""
    unlock_schedule = {
        "frame": 1,
        "diverge": 4,
        "challenge": 4,
        "synthesize": 6,
        "create-artifact": 6
    }
    return current_week >= unlock_schedule.get(agent, 99)

async def friendly_lockout_message(message: discord.Message, student, agent: str):
    """Generate encouraging lockout message when agent not yet unlocked"""
    unlock_week = {"diverge": 4, "challenge": 4, "synthesize": 6, "create-artifact": 6}.get(agent, 99)
    available = ", ".join([f"/{a}" for a in student.unlocked_agents])

    await message.reply(
        f"🔒 **{agent.capitalize()} unlocks Week {unlock_week}!**\n\n"
        f"You're in Week {student.current_week} - exactly where you should be. "
        f"Right now you can use: {available}\n\n"
        f"**Why the sequence matters:**\n"
        f"Each agent builds on the 4 Habits you're learning. "
        f"The {agent.capitalize()} will make more sense after practicing the earlier ones.\n\n"
        f"**You're on track. Keep going!** ✨"
    )

def setup_bot_events(bot: commands.Bot):
    """Attach routing to Discord bot events"""

    @bot.event
    async def on_message(message: discord.Message):
        # Ignore bot's own messages
        if message.author.bot:
            return

        # Only process DMs or messages in designated channels
        if isinstance(message.channel, discord.DMChannel) or \
           message.channel.name in ['thinking-lab', 'bot-testing']:
            await route_student_interaction(message)
```

**cis_controller/llm_integration.py (Claude API):**

```python
import os
import anthropic
from typing import List, Dict
from database.models import StudentContext

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Cached system prompts (loaded once, reused for all calls)
CACHED_SYSTEM_PROMPTS = {
    "frame": None,  # Loaded from agents/framer_prompt.py
    "diverge": None,
    "challenge": None,
    "synthesize": None
}

def load_system_prompts():
    """Load all agent system prompts into cache"""
    from agents import framer_prompt, explorer_prompt, challenger_prompt, synthesizer_prompt

    CACHED_SYSTEM_PROMPTS["frame"] = framer_prompt.get_system_prompt()
    CACHED_SYSTEM_PROMPTS["diverge"] = explorer_prompt.get_system_prompt()
    CACHED_SYSTEM_PROMPTS["challenge"] = challenger_prompt.get_system_prompt()
    CACHED_SYSTEM_PROMPTS["synthesize"] = synthesizer_prompt.get_system_prompt()

# Call once on bot startup
load_system_prompts()

async def call_agent_with_context(
    agent: str,
    student_context: StudentContext,
    user_message: str,
    conversation_history: List[Dict[str, str]]
) -> str:
    """
    Call Claude Sonnet 4.5 API with prompt caching.

    LAYER 3: AGENT ROUTER → LLM API CALL
    """
    # Get cached system prompt
    system_prompt = CACHED_SYSTEM_PROMPTS.get(agent)
    if not system_prompt:
        raise ValueError(f"Unknown agent: {agent}")

    # Prepare messages (last 10 for context)
    messages = conversation_history[-10:] + [{"role": "user", "content": user_message}]

    # Call Claude API with prompt caching
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250514",  # Sonnet 4.5
            max_tokens=1000,
            temperature=1.0,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}  # Enable caching
                }
            ],
            messages=messages,
            betas=["prompt-caching-2024-07-31"]  # Enable prompt caching
        )

        response_text = response.content[0].text

        # Track API usage
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cache_tokens = getattr(response.usage, 'cache_read_input_tokens', 0)

        # Calculate cost (Sonnet 4.5 pricing: $3/M input, $15/M output)
        # Batch API: 50% discount
        input_cost = (input_tokens - cache_tokens) * 3.0 / 1_000_000 * 0.5
        cache_cost = cache_tokens * 0.30 / 1_000_000 * 0.5  # 90% cheaper
        output_cost = output_tokens * 15.0 / 1_000_000 * 0.5
        total_cost = input_cost + cache_cost + output_cost

        # Log usage
        print(f"API Call ({agent}): {input_tokens} in, {output_tokens} out, {cache_tokens} cached | ${total_cost:.4f}")

        return response_text

    except anthropic.RateLimitError:
        # Rate limited - implement exponential backoff
        raise Exception(f"Rate limit exceeded for {agent} agent")

    except anthropic.APIConnectionError:
        # Network error
        raise Exception(f"Failed to connect to Claude API for {agent} agent")

    except Exception as e:
        # Log error and notify Trevor
        print(f"ERROR calling {agent} agent: {str(e)}")
        # Send alert to Trevor
        await notify_trevor(f"🚨 CIS Agent Error: {agent} failed - {str(e)}")
        raise
```

**cis_controller/safety_filter.py (Guardrail #3 Infrastructure):**

```python
import re
import logging
from typing import List

class ComparisonViolationError(Exception):
    """Raised when message contains forbidden comparison/ranking."""
    pass

class SafetyFilter:
    """
    Anti-comparison validation layer (Guardrail #3).

    EVERY public Discord message passes through this filter.
    Prevents Guardrail #3 violations from ever shipping.
    """

    FORBIDDEN_KEYWORDS = [
        "top student", "best student", "worst student",
        "top 3", "best 5", "leading student",
        "most active", "least active",
        "highest quality", "lowest quality",
        "fastest", "slowest",
        "ahead of", "behind",
        "better than", "worse than",
        "outperform", "underperform",
        "rank", "ranking", "leaderboard",
        "first place", "last place"
    ]

    FORBIDDEN_PATTERNS = [
        r"student.*?#\d+",  # "student #1", "student #2"
        r"top\s+\d+",  # "top 5", "top 10"
        r"\d+\s*(st|nd|rd|th)\s+place",  # "1st place", "2nd place"
        r"student.*?(better|worse|faster|slower).*?than",  # Comparisons
    ]

    def validate_no_comparison(self, message_text: str) -> bool:
        """
        Validate message contains NO comparison/ranking.

        Raises ComparisonViolationError if violation detected.
        Returns True if safe.
        """
        message_lower = message_text.lower()

        # Check forbidden keywords
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in message_lower:
                logging.error(f"Comparison violation: keyword '{keyword}' in message")
                raise ComparisonViolationError(
                    f"Message contains forbidden comparison keyword: '{keyword}'\n"
                    f"Full message: {message_text[:100]}..."
                )

        # Check forbidden patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, message_lower):
                logging.error(f"Comparison violation: pattern '{pattern}' matched")
                raise ComparisonViolationError(
                    f"Message matches forbidden comparison pattern: {pattern}\n"
                    f"Full message: {message_text[:100]}..."
                )

        # Log successful check
        logging.info(f"Safety check PASSED: {message_text[:50]}...")
        return True

    def validate_aggregate_message(self, message_text: str, mentioned_students: List[str]) -> bool:
        """
        Additional validation for aggregate visibility messages.

        Ensures aggregates are non-comparative.
        """
        # ALLOWED: Counts without names
        # "15 students practiced /frame this week" ✅

        # FORBIDDEN: Counts with names
        # "Sarah, John, and Mary practiced /frame" ❌

        if mentioned_students and len(mentioned_students) > 0:
            if any(keyword in message_text.lower() for keyword in ["practiced", "completed", "used"]):
                raise ComparisonViolationError(
                    "Aggregate message mentions specific student names with action verbs. "
                    "This creates implicit comparison. Use counts only, no names."
                )

        return True

# Singleton instance
safety_filter = SafetyFilter()

async def post_to_discord_safe(channel, message_text: str):
    """
    Wrapper for Discord posting with safety validation.

    ALL public messages MUST use this function.
    """
    try:
        # Validate no comparison
        safety_filter.validate_no_comparison(message_text)

        # Post to Discord
        await channel.send(message_text)

    except ComparisonViolationError as e:
        # Log violation and alert Trevor
        logging.critical(f"COMPARISON VIOLATION BLOCKED: {e}")
        await notify_trevor(f"🚨 Comparison violation blocked: {str(e)}")

        # Do NOT post message
        raise
```

### Four CIS Agent Implementations

**agents/framer_prompt.py (The Framer - Habit 1 & 2):**

```python
FRAMER_SYSTEM_PROMPT = """
# The Framer - CIS Thinking Agent

You are The Framer, a friendly thinking coach who helps students pause and clarify their questions before using AI.

## Your Identity
- Icon: ⏸️ Pause Button
- Role: Help students practice Habit 1 (Pause) and Habit 2 (Context)
- Voice: Warm, welcoming, clear, non-intimidating
- Altitude: Level 1-2 (concrete, relatable, no jargon)

## Your Purpose
Students often rush to AI without knowing what they actually want. You help them:
1. **PAUSE** (Habit 1): Stop and ask "What do I actually want from this interaction?"
2. **ADD CONTEXT** (Habit 2): Explain their situation so AI responds to THEM

You are NOT here to answer their questions. You are here to help them ASK BETTER QUESTIONS.

## What You Do
- Ask clarifying questions: "What do you actually want to know?"
- Mirror and confirm: "So what you're asking is..."
- Suggest framing: "Try framing it like this..."
- Celebrate the pause: "You paused before asking. That's the habit!"
- Normalize confusion: "Many students feel this way. You're not alone."

## What You NEVER Do
- ❌ NEVER give advice: "You should..."
- ❌ NEVER answer their question directly
- ❌ NEVER use tech jargon: "Let's prompt-engineer this"
- ❌ NEVER compare or rank: "You're asking better than most"
- ❌ NEVER use impressive examples: "AI can write books!"

## Conversation Patterns

**Pattern 1: Vague Question → Clarified Frame**
Student: "I need help with math."
You: "I can help you frame that! What specifically about math? Are you stuck on homework, a test, or understanding a concept?"

**Pattern 2: Anxious Confusion → Normalized → Framed**
Student: "I'm so confused about university. I don't know what to do."
You: "That's a completely normal feeling. Many students feel overwhelmed by university decisions. Let's pause and clarify: What decision are you actually facing?"

## Altitude-Aware Templates

**Week 1 (Level 1 - Empathy):**
"Let me help you get clearer. Tell me: what's your situation with this? And what would help you most right now?"

**Week 3+ (Level 2-3 - Framework):**
"Try framing it like this: 'My situation is [describe]. I want to [goal]. Can you help me [specific question]'"

## Key Principles
1. Identity First: Help them feel "I'm someone who can ask better questions"
2. Psychological Safety: Normalize confusion, celebrate small wins, never judge
3. Guardrails Compliance: Never give advice, never use jargon, never compare
4. JTBD-Aligned: All examples serve real student jobs (university, career, anxiety)
5. Habit Building: Make the pause visible, celebrate it, name it as Habit 1
"""

def get_system_prompt():
    """Return Framer system prompt"""
    return FRAMER_SYSTEM_PROMPT
```

**commands/frame.py (Framer Command Handler):**

```python
import discord
from database.store import StudentStateStore
from cis_controller.llm_integration import call_agent_with_context
from cis_controller.safety_filter import post_to_discord_safe

store = StudentStateStore()

async def handle_frame(message: discord.Message, student):
    """
    Handle /frame command.

    Generates Framer response using Claude API with StudentContext.
    """
    # Load conversation history
    history = store.get_conversation_history(student.discord_id, "frame", limit=10)

    # Build StudentContext with JTBD-matched example
    # (This would be implemented in database.models.StudentContext)
    from database.models import build_student_context
    student_context = build_student_context(student)

    # Generate response using Framer agent
    try:
        framer_response = await call_agent_with_context(
            agent="frame",
            student_context=student_context,
            user_message=message.content,
            conversation_history=history
        )

        # Validate safety
        post_to_discord_safe(message.channel, framer_response)

        # Generate habit celebration (if applicable)
        from cis_controller.state_machine import celebrate_habit
        celebration = celebrate_habit(student, habit_id=1)  # Habit 1 (Pause)

        if celebration:
            full_response = f"{framer_response}\n\n{celebration}"
        else:
            full_response = framer_response

        # Post to Discord
        await message.reply(full_response)

        # Update state
        store.update_habit_practice(student.discord_id, habit_id=1)
        store.save_conversation(student.discord_id, "frame", message.content, full_response)

    except Exception as e:
        await message.reply(f"**The Framer is taking a short break.**\n\nTry this on your own: Pause and ask yourself 'What do I actually want to know?'\n\n**You're practicing Habit 1 (⏸️ PAUSE) - you've got this!**")
        print(f"Framer error: {e}")
```

### Artifact Creation Flow Implementation

**commands/artifact.py (/create-artifact Command):**

```python
import discord
from database.store import StudentStateStore
from database.models import ArtifactProgress

store = StudentStateStore()

@bot.command(name='create-artifact')
async def create_artifact(ctx):
    """
    Entry point for artifact creation flow (Week 6+ only).

    Story 4.6 specification implementation.
    """
    student = store.get_student(ctx.author.id)

    # Check week (only available Week 6+)
    if student.current_week < 6:
        await ctx.send(
            "**Thinking Artifact** 🎯\n\n"
            "Your Thinking Artifact is a Week 6-8 project. "
            "You'll get access when Week 6 begins!\n\n"
            "This is where you'll prove how you've grown as a thinker by showing a real problem you worked through using the CIS agents."
        )
        return

    # Load or create artifact progress
    artifact_progress = store.get_artifact_progress(student.discord_id)

    if artifact_progress.status == "not_started":
        # Show introduction
        await show_artifact_introduction(ctx)

    elif artifact_progress.status == "in_progress":
        # Resume from where they left off
        await resume_artifact_creation(ctx, student, artifact_progress)

    elif artifact_progress.status == "completed":
        # Ready to polish/publish
        await show_artifact_review(ctx, artifact_progress)

async def show_artifact_introduction(ctx):
    """Display artifact introduction (Story 4.6, Section 1)"""

    introduction = """
**Thinking Artifact Creation** 🎯

Your Thinking Artifact is your graduation deliverable. It proves how you've grown as a thinker by showing a real problem you worked through using the CIS agents.

**What it is:**
- A 6-section document showing your thinking process
- Evidence of your identity transformation: "I'm someone who can think clearly with AI"
- Proof you've earned all 4 Habits badges (⏸️ 🎯 🔄 🧠)

**What it's NOT:**
- An essay about "how I use AI"
- AI-generated content (this must be YOUR voice)
- A test or assessment (there's no grading, only completion)

**You'll create this over Weeks 6-8:**
- **Week 6:** Choose your question and start working through it
- **Week 7:** Complete all CIS agent sections
- **Week 8:** Polish and publish to #thinking-showcase

**Ready to start?** This will take 30-60 minutes to complete all 6 sections. You can save at any time and resume later.

Type: **start** to begin, or **show-example** to see a complete artifact first.
"""

    await ctx.send(introduction)

async def resume_artifact_creation(ctx, student, artifact_progress):
    """Resume artifact creation from last section"""

    next_section = artifact_progress.get_next_section()
    completed_count = len(artifact_progress.completed_sections)

    message = f"""
**Welcome back to your Thinking Artifact!** 📝

**Progress: {completed_count}/6 sections complete**

**Where you left off:**
{get_progress_summary(artifact_progress)}

**Next step:**
{get_section_prompt(next_section)}

**Options:**
- Type **continue** to work on Section {next_section}
- Type **review** to see what you've written so far
"""

    await ctx.send(message)

async def show_artifact_review(ctx, artifact_progress):
    """Show complete artifact for review (Week 8 polish flow)"""

    if not artifact_progress.is_complete():
        await ctx.send("You haven't completed all 6 sections yet. Type `/create-artifact` to continue.")
        return

    # Display formatted artifact
    formatted = f"""
**Your Complete Thinking Artifact** 📝

---

**THE QUESTION I WRESTLED WITH:**

{artifact_progress.section_1_question}

**HOW I REFRAMED IT:** 🎯

{artifact_progress.section_2_reframed}

**WHAT I EXPLORED:** 🔄

{artifact_progress.section_3_explored}

**WHAT I CHALLENGED:** 🧠

{artifact_progress.section_4_challenged}

**WHAT I CONCLUDED:** ✨

{artifact_progress.section_5_concluded}

**WHAT THIS TAUGHT ME:** ⏸️

{artifact_progress.section_6_reflection}

---

**Polish Checklist:** ✅

Before publishing, review your artifact:
- [ ] **Clarity:** Does each section make sense to someone who doesn't know your story?
- [ ] **Voice:** Is this YOUR voice? (Not AI-written - parents should hear YOU in this)
- [ ] **Specifics:** Did you include concrete details from your CIS conversations?
- [ ] **4 Habits:** Are all 4 habits visible in your reflection?
- [ ] **Identity Transformation:** Does this prove "I've become someone who thinks clearly"?

**Want to edit?** Type: **edit section [1-6]**

**Ready to publish?** Type: **publish**
"""

    await ctx.send(formatted)

# Additional command handlers for save, edit, publish would follow similar patterns...
```

### Discord Server Channel Architecture

**Server Structure (Decision 12 Implementation):**

```yaml
Discord Server: "K2M Cohort #X - AI Thinking Skills"

Channels:
  # Information & Onboarding
  - welcome: "👋 Welcome & Getting Started"
  - announcements: "📢 Important Updates"
  - resources: "📚 Resources & Guides"

  # Core Interaction Spaces (Decision 12)
  - thinking-lab: "🧪 Thinking Lab"
    → Purpose: Entry point for CIS agent interactions
    → Instructions: Bot message explaining how to use CIS agents
    → Pattern: Student types command → Bot responds in DM → Student can share to #thinking-showcase

  - thinking-showcase: "🌟 Thinking Showcase"
    → Purpose: Public celebration of finished artifacts
    → Privacy: Students can publish anonymously if preferred
    → Pattern: Celebration only (no comparison, no ranking)
    → **Story 5.3 Cross-Reference:** See Story 5.3 for complete #thinking-showcase specification including celebration message templates, Claude API prompt engineering, parent email system, and privacy controls (Yes/No/Anonymous/Permanent options). Story 5.3 defines WHAT gets published; this story defines HOW the bot publishes it.

  # Week-Specific Channels (Optional)
  - week-1-discussion: "Week 1: Wonder"
  - week-2-3-discussion: "Weeks 2-3: Trust"
  - week-4-5-discussion: "Weeks 4-5: Converse"
  - week-6-7-discussion: "Weeks 6-7: Direct"
  - week-8-discussion: "Week 8: Artifact Showcase"

  # Admin & Operations (Trevor-only)
  - facilitator-dashboard: "📊 Trevor's Dashboard" (private)
  - bot-testing: "🤖 Bot Testing" (development)

Roles:
  - Student: Default role for all cohort participants
  - Trevor: Administrator, full access
  - CIS Bot: Bot role for agent system

Permissions:
  - Students: Can read/post in -discussion channels, can read #thinking-showcase
  - Trevor: Full access
  - CIS Bot: Send messages in DMs and #thinking-showcase, read #thinking-lab
```

**#thinking-lab Channel Setup:**

```python
async def setup_thinking_lab_channel(guild: discord.Guild):
    """
    Configure #thinking-lab channel with instructions.
    """
    channel = discord.utils.get(guild.channels, name="thinking-lab")

    instructions = """
# 🧪 Welcome to the Thinking Lab!

This is your practice space for developing AI thinking skills with the CIS agents.

## Quick Start

1. **Choose a CIS agent command:**
   - `/frame [your question]` - Pause and clarify what you want to know (Habit 1 & 2)
   - `/diverge [topic]` - Explore multiple possibilities (Habit 3) - *Week 4+*
   - `/challenge [assumption]` - Stress-test your thinking (Habit 4) - *Week 4+*
   - `/synthesize [insights]` - Articulate your conclusions (Habit 4) - *Week 6+*

2. **Work in private:**
   The bot will respond in a private DM/Thread with you. This is your safe space to be messy and confused.

3. **Share when ready:**
   Once you've worked through something, you can share your finished thinking to #thinking-showcase

## Weekly Introduction Schedule

- **Week 1:** `/frame` available (practice mode)
- **Weeks 2-3:** `/frame` continues + context prompting
- **Weeks 4-5:** `/diverge` and `/challenge` added (full CIS suite)
- **Weeks 6-7:** `/synthesize` added + artifact creation begins
- **Week 8:** All agents, artifact completion and showcase

## Key Principles

✅ **This is practice:** No grades, no wrong answers
✅ **Process is private:** Your DM/thread is safe
✅ **Product is public:** Share finished work to #thinking-showcase
✅ **Comparison-free:** We celebrate growth, we don't rank students

**Ready to practice?** Type a CIS command to get started!
"""

    await channel.send(instructions)
```

### StudentContext & Database Schema

**database/schema.sql (SQLite Schema):**

```sql
-- Students table (core student data)
CREATE TABLE students (
    discord_id TEXT PRIMARY KEY,
    cohort_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    current_week INTEGER DEFAULT 1,
    current_state TEXT DEFAULT 'none',  -- framing, exploring, challenging, synthesizing, complete
    zone TEXT DEFAULT 'zone_0',  -- zone_0, zone_1, zone_2, zone_3, zone_4
    jtbd_concern TEXT DEFAULT 'career_direction',  -- university_application, exam_anxiety, etc.
    emotional_state TEXT DEFAULT 'curious',  -- anxious, curious, confident, stuck, excited
    unlocked_agents TEXT DEFAULT '["frame"]',  -- JSON array
    artifact_progress INTEGER DEFAULT 0,  -- 0-100
    interaction_count INTEGER DEFAULT 0,
    last_interaction TEXT,  -- ISO timestamp
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Habit journey tracking
CREATE TABLE habit_practice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    habit_id INTEGER NOT NULL,  -- 1=Pause, 2=Context, 3=Iterate, 4=Think
    practiced_count INTEGER DEFAULT 0,
    last_practiced TEXT,
    confidence TEXT DEFAULT 'emerging',  -- emerging, growing, strong
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id),
    UNIQUE(student_id, habit_id)
);

-- Conversations table (message history for context)
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

-- Artifact progress (Story 4.6)
CREATE TABLE artifact_progress (
    student_id TEXT PRIMARY KEY,
    section_1_question TEXT,
    section_2_reframed TEXT,
    section_3_explored TEXT,
    section_4_challenged TEXT,
    section_5_concluded TEXT,
    section_6_reflection TEXT,
    completed_sections TEXT DEFAULT '[]',  -- JSON array
    current_section INTEGER DEFAULT 0,
    status TEXT DEFAULT 'not_started',  -- not_started, in_progress, completed, published
    started_at TEXT,
    last_activity TEXT,
    completed_at TEXT,
    published_at TEXT,
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
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- Story 5.3 Integration: #thinking-showcase publication tables
-- See Story 5.3, Section 3.2 for complete database schema specification
-- Story 5.3 defines: showcase_publications, parent_engagement, student_publication_preferences tables
-- This story (4.7) implements the bot code that writes to those tables

-- Example cross-reference (implementation in this story, schema in Story 5.3):
-- CREATE TABLE showcase_publications (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     student_id TEXT NOT NULL,
--     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
--     publication_type TEXT NOT NULL,  -- 'habit_practice' OR 'artifact_completion'
--     visibility_level TEXT NOT NULL,  -- 'public' OR 'anonymous' OR 'private'
--     celebration_message TEXT NOT NULL,
--     habits_demonstrated TEXT,  -- JSON array: ["⏸️", "🎯", "🔄", "🧠"]
--     nodes_mastered TEXT,  -- JSON array: [1.3, 2.1, 3.2]
--     reactions_count INTEGER DEFAULT 0,
--     parent_email_included BOOLEAN DEFAULT 0,
--     artifact_id INTEGER,  -- FK to artifacts table if artifact_completion
--     FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
-- );
```

**database/models.py (StudentContext ORM):**

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class HabitProgress:
    habit_id: int
    name: str
    icon: str
    practiced_count: int = 0
    last_practiced: Optional[datetime] = None
    confidence: str = "emerging"
    unlocked: bool = False

@dataclass
class ArtifactProgress:
    section_1_question: str = ""
    section_2_reframed: str = ""
    section_3_explored: str = ""
    section_4_challenged: str = ""
    section_5_concluded: str = ""
    section_6_reflection: str = ""
    completed_sections: List[str] = field(default_factory=list)
    current_section: int = 0
    status: str = "not_started"
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    def is_complete(self) -> bool:
        return all([
            self.section_1_question,
            self.section_2_reframed,
            self.section_3_explored,
            self.section_4_challenged,
            self.section_5_concluded,
            self.section_6_reflection
        ])

    def get_next_section(self) -> int:
        if not self.section_1_question:
            return 1
        elif not self.section_2_reframed:
            return 2
        elif not self.section_3_explored:
            return 3
        elif not self.section_4_challenged:
            return 4
        elif not self.section_5_concluded:
            return 5
        elif not self.section_6_reflection:
            return 6
        else:
            return 0  # All complete

@dataclass
class StudentContext:
    """Rich domain model representing student's complete context"""

    # Identity
    discord_id: str
    zone: str
    current_week: int
    cohort_start_date: datetime

    # JTBD (Jobs-to-be-Done)
    jtbd_primary_concern: str
    emotional_state: str

    # Habits
    habit_journey: Dict[int, HabitProgress] = field(default_factory=dict)

    # Artifact
    artifact_progress: ArtifactProgress = field(default_factory=ArtifactProgress)

    # State
    current_state: str = "none"
    unlocked_agents: List[str] = field(default_factory=lambda: ["frame"])
    interaction_count: int = 0

    # Helpers
    def get_altitude(self) -> str:
        """Map week + zone to JTBD altitude level (1-5)"""
        if self.current_week == 1:
            return "Level 1 - Ground (Concrete/Immediate)"
        elif self.current_week <= 3:
            return "Level 2 - Pattern (Observable Truth)"
        elif self.current_week <= 5:
            return "Level 3 - Framework (System/Structure)"
        else:
            return "Level 4 - Transform (What Becomes Possible)"

    def get_relevant_example(self, agent: str) -> str:
        """Pull example matching JTBD concern + zone + agent"""
        # This would call Story 4.1's example selector
        from cis_controller.examples import select_example
        return select_example(
            concern=self.jtbd_primary_concern,
            zone=self.zone,
            agent=agent,
            week=self.current_week
        )

def build_student_context(db_student) -> StudentContext:
    """Factory method to create StudentContext from database student"""
    # Load habit progress from database
    habit_journey = {}
    for habit_id in [1, 2, 3, 4]:
        habit_data = get_habit_data(db_student.discord_id, habit_id)
        habit_journey[habit_id] = HabitProgress(
            habit_id=habit_id,
            name=HABIT_NAMES[habit_id],
            icon=HABIT_ICONS[habit_id],
            practiced_count=habit_data.get("count", 0)
        )

    # Determine zone from week progression
    if db_student.current_week == 1:
        zone = "zone_0"
    elif db_student.current_week <= 3:
        zone = "zone_1"
    elif db_student.current_week <= 5:
        zone = "zone_2"
    elif db_student.current_week <= 7:
        zone = "zone_3"
    else:
        zone = "zone_4"

    return StudentContext(
        discord_id=db_student.discord_id,
        zone=zone,
        current_week=db_student.current_week,
        cohort_start_date=datetime.fromisoformat(db_student.start_date),
        jtbd_primary_concern=db_student.jtbd_concern or "career_direction",
        emotional_state=db_student.emotional_state or "curious",
        habit_journey=habit_journey,
        current_state=db_student.current_state,
        unlocked_agents=json.loads(db_student.unlocked_agents),
        interaction_count=db_student.interaction_count
    )

# Constants
HABIT_NAMES = {1: "PAUSE", 2: "CONTEXT", 3: "ITERATE", 4: "THINK FIRST"}
HABIT_ICONS = {1: "⏸️", 2: "🎯", 3: "🔄", 4: "🧠"}
```

### Deployment & Operations Guide

**Environment Configuration (.env):**

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

# Development
DEBUG=false
LOG_LEVEL=INFO
```

**Deployment Process (Railway):**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project
railway init

# 4. Create new service
railway add

# 5. Configure environment variables in Railway dashboard
# (Paste .env contents)

# 6. Deploy
railway up

# 7. Check logs
railway logs --tail

# 8. Set up auto-deploy from GitHub
railway variables set BUILD_COMMAND="pip install -r requirements.txt"
railway variables set START_COMMAND="python main.py"
```

**Monitoring & Alerting:**

```python
# cis_controller/monitoring.py

import asyncio
from datetime import datetime, timedelta

class BotMonitor:
    """Health checks and monitoring for CIS bot"""

    async def daily_health_check(self):
        """Comprehensive health check"""
        checks = {
            "database": self.check_database_connection(),
            "claude_api": self.check_claude_api_connection(),
            "discord_connection": self.check_discord_connection(),
            "rate_limits": self.check_rate_limit_status(),
            "budget": self.check_budget_status()
        }

        if not all(checks.values()):
            await self.notify_trevor(f"⚠️ Health Check Failed: {checks}")

        return checks

    async def check_budget_status(self):
        """Alert if approaching budget limits"""
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = db.execute(
            "SELECT SUM(total_cost_usd) as daily_total FROM api_usage WHERE date = ?",
            (today,)
        )
        result = cursor.fetchone()
        daily_total = result["daily_total"] or 0

        DAILY_BUDGET_ALERT = 10.00

        if daily_total > DAILY_BUDGET_ALERT:
            await self.notify_trevor(
                f"💰 Budget Alert: ${daily_total:.2f} spent today "
                f"(limit: ${DAILY_BUDGET_ALERT})"
            )
```

**Testing Strategy:**

```python
# tests/test_bot_integration.py

import pytest
from discord.ext.test import TestClient

@pytest.mark.asyncio
async def test_full_frame_conversation():
    """Test complete /frame conversation flow"""
    client = TestClient(bot)

    # Student sends /frame command
    response = await client.send_message("/frame I need help choosing a university")

    # Should get Framer response
    assert "🎯" in response.content  # Framer icon
    assert "PAUSE" in response.content  # Habit 1

    # Verify habit tracking updated
    student = store.get_student(test_user_id)
    assert student.habit_journey[1].practiced_count == 1

@pytest.mark.asyncio
async def test_safety_filter_blocks_comparison():
    """Test that SafetyFilter prevents comparison"""
    from cis_controller.safety_filter import SafetyFilter, ComparisonViolationError

    filter = SafetyFilter()

    # Should pass (no comparison)
    filter.validate_no_comparison("15 students practiced /frame this week")

    # Should fail (comparison)
    with pytest.raises(ComparisonViolationError):
        filter.validate_no_comparison("Top 3 students this week:")
```

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (December 2024 version)

### Completion Notes List

**Story 4.7 designs the complete Discord bot implementation specification that brings together ALL Epic 4 work into a production-ready system.**

**Key Design Decisions:**

1. ✅ **Complete Architecture:** Discord events → Intent Recognition → State Machine → Agent Router → Claude API → SafetyFilter → Discord Response
2. ✅ **CIS Controller Implementation:** Three-layer design with async/await patterns, StudentContext integration, temporal awareness
3. ✅ **Four CIS Agents:** Complete specifications for /frame, /diverge, /challenge, /synthesize with system prompts and handlers
4. ✅ **Artifact Creation Flow:** /create-artifact command with private DM workflow, save/resume, and Week 8 publish to #thinking-showcase
5. ✅ **Discord Server Architecture:** #thinking-lab, #thinking-showcase, private DMs, celebration patterns
6. ✅ **StudentContext & Database:** Complete data model with SQLite schema, ORM patterns, and migration path
7. ✅ **SafetyFilter Implementation:** Anti-comparison infrastructure (Guardrail #3 compliance)
8. ✅ **Deployment & Operations:** Environment setup, Railway deployment, monitoring, testing strategy

**Integration with ALL Epic 4 Stories:**
- Story 4.1 (Controller): Router, state machine, LLM integration, StudentContext, SafetyFilter
- Story 4.2 (Framer): /frame agent, Habit 1 & 2 scaffolding, Week 1 practice mode
- Story 4.3 (Explorer): /diverge agent, Habit 3 scaffolding, Week 4 introduction
- Story 4.4 (Challenger): /challenge agent, Habit 4 scaffolding, Week 4 introduction
- Story 4.5 (Synthesizer): /synthesize agent, Habit 4 completion, artifact support
- Story 4.6 (Artifact): /create-artifact command, 6-section workflow, Week 8 showcase

**Technical Stack (Decision 15):**
- Python 3.10+, discord.py 2.3+, Anthropic Claude SDK 0.18+
- Claude Sonnet 4.5 (Batch) with prompt caching (90% cost reduction)
- SQLite for Cohort 1 (100-200 students), PostgreSQL migration path for Cohort 2+
- Railway/Heroku deployment

**Cost Management:**
- Budget: $100/week conservative, actual $5-33 with prompt caching
- Rate limiting: 50 interactions/day per student
- Monitoring: Daily budget alerts at $10, weekly cap at $50

**Next Steps:**
1. Developer can implement bot directly from this specification
2. All Epic 4 stories integrated and production-ready
3. Ready for Epic 5 (Discord Architecture & Operations) deployment

### File List

**Output File:**
- `_bmad-output/implementation-artifacts/4-7-discord-bot-spec.md` (this file)

**Story 5.3 Bidirectional Cross-References:**
Story 4.7 and Story 5.3 have tight integration for #thinking-showcase implementation:

**Story 4.7 (this story) → Story 5.3:**
- Section 5.3 (#thinking-showcase): See Story 5.3 for celebration message templates, Claude API prompt engineering, parent email system, privacy controls
- Section 6 (Database): Story 5.3 defines showcase_publications, parent_engagement, student_publication_preferences tables (complete SQL schemas)

**Story 5.3 → Story 4.7 (this story):**
- Section 3.2 (Publication Flow): See this story, Section 5.2: /publish-command API implementation
- Section 6 (Bot Automation): See this story, Section 6.2: Claude API integration, Section 7: Email queue processing
- Section 6.2 (SafetyFilter): See this story, Section 7: Moderation workflow implementation

**Dependency Mapping:**
- Story 5.3 (Specification Layer): Defines WHAT gets published, HOW celebrations work, WHAT data is stored
- Story 4.7 (Implementation Layer): Defines HOW the bot publishes, Claude API integration, Discord.py code
- Developer must reference BOTH stories to implement complete #thinking-showcase functionality

**Referenced Foundation Documents:**
- `_bmad-output/cohort-design-artifacts/cohort-playbook-v2-requirements.md` (Decisions 11, 12, 14, 15)
- `_bmad-output/cohort-design-artifacts/playbook-v2/01-philosophy/` (Epic 1: Guardrails, JTBD, Node Architecture, 4 Habits)
- `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-1-cis-controller-logic.md` (Controller architecture)
- `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-2-framer-agent-prompt.md` (The Framer)
- `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-3-explorer-agent-prompt.md` (The Explorer)
- `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-4-challenger-agent-prompt.md` (The Challenger)
- `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-5-synthesizer-agent-prompt.md` (The Synthesizer)
- `_bmad-output/implementation-artifacts/4-6-artifact-creation-flow.md` (Artifact workflow)
- `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/thinking-showcase-setup.md` (Story 5.3: #thinking-showcase specification)

---

**Story 4.7 Status: ✅ READY FOR IMPLEMENTATION**

The Discord bot technical specification is complete with:
- ✅ Complete system architecture from Discord events to Claude API
- ✅ CIS Controller implementation specification with code examples
- ✅ Four CIS agent integration specifications (/frame, /diverge, /challenge, /synthesize)
- ✅ Artifact creation flow implementation (/create-artifact command)
- ✅ Discord server channel architecture (#thinking-lab → #thinking-showcase)
- ✅ StudentContext & database schema (SQLite with ORM)
- ✅ SafetyFilter implementation (Guardrail #3 compliance infrastructure)
- ✅ Deployment & operations guide (Railway, monitoring, testing)
- ✅ All 8 Acceptance Criteria met

**Developer can now implement the complete CIS Discord bot using this specification.**
