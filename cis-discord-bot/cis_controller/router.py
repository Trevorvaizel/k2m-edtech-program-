"""
CIS Controller - Router Module
Story 4.7 Implementation: CIS Controller routing logic

This module handles:
- Layer 1: Intent Recognition (commands vs natural language)
- Layer 2: State Machine (temporal awareness, agent unlocking)
- Layer 3: Agent Router (dispatch to command handlers)

Three-Layer Architecture:
  1. Parse: Is this a command or natural language?
  2. Check: Agent unlocked for this week?
  3. Route: Dispatch to correct handler
"""

import os
import discord
from discord.ext import commands
from database.store import StudentStateStore
from cis_controller.state_machine import (
    transition_state,
    celebrate_habit,
    get_student_state,
)
import logging

logger = logging.getLogger(__name__)

# Initialize state store
store = StudentStateStore()

# Commands managed by CIS Controller (non-core bot commands like /ping bypass this).
CONTROLLED_COMMANDS = {
    "frame",
    "diverge",
    "challenge",
    "synthesize",
    "create-artifact",
    "save",
    "review",
    "publish",
}

# Commands that belong to discord.py bot command handlers in main.py.
BYPASS_CONTROLLER_COMMANDS = {"ping", "status"}

# Habit mapping for milestone tracking.
HABIT_BY_COMMAND = {
    "frame": 1,      # Pause
    "diverge": 3,    # Iterate
    "challenge": 4,  # Think First
    "synthesize": 4, # Think First
}

# Designated public channels where students can trigger CIS routing.
ALLOWED_CHANNEL_SLUGS = ("thinking-lab", "bot-testing")
THINKING_LAB_CHANNEL_ID = os.getenv("CHANNEL_THINKING_LAB", "").strip()
BOT_TESTING_CHANNEL_ID = os.getenv("CHANNEL_BOT_TESTING", "").strip()

# Agent unlock schedule (Decision 11)
UNLOCK_SCHEDULE = {
    "frame": 1,
    "diverge": 4,
    "challenge": 4,
    "synthesize": 6,
    "create-artifact": 6,
    "save": 6,
    "review": 6,
    "publish": 6,
}

# Available agents by week
AGENTS_BY_WEEK = {
    1: ["frame"],
    2: ["frame"],
    3: ["frame"],
    4: ["frame", "diverge", "challenge"],
    5: ["frame", "diverge", "challenge"],
    6: ["frame", "diverge", "challenge", "synthesize", "create-artifact", "save", "review", "publish"],
    7: ["frame", "diverge", "challenge", "synthesize", "create-artifact", "save", "review", "publish"],
    8: ["frame", "diverge", "challenge", "synthesize", "create-artifact", "save", "review", "publish"],
}


class PrivateReplyMessage:
    """
    Lightweight adapter that keeps command parsing fields from the original
    message but routes replies to a private DM channel.
    """

    def __init__(self, source_message: discord.Message, private_channel: discord.abc.Messageable):
        self._source = source_message
        self.author = source_message.author
        self.content = source_message.content
        self.channel = private_channel

    async def reply(self, content=None, **kwargs):
        return await self.channel.send(content, **kwargs)


def _is_designated_channel(channel) -> bool:
    """Allow configured channel IDs or slug-based names (with or without emoji prefixes)."""
    channel_id = str(getattr(channel, "id", ""))
    if THINKING_LAB_CHANNEL_ID and channel_id == THINKING_LAB_CHANNEL_ID:
        return True
    if BOT_TESTING_CHANNEL_ID and channel_id == BOT_TESTING_CHANNEL_ID:
        return True

    channel_name = getattr(channel, "name", "").lower()
    return any(
        channel_name == slug or channel_name.endswith(slug) or slug in channel_name
        for slug in ALLOWED_CHANNEL_SLUGS
    )


async def _prepare_response_message(message: discord.Message):
    """
    For public channel triggers, move all bot replies to DM to preserve
    private-process flow (Decision 12 / Guardrail #8).
    """
    if isinstance(message.channel, discord.DMChannel):
        return message

    dm_channel = message.author.dm_channel
    if dm_channel is None:
        dm_channel = await message.author.create_dm()

    try:
        await message.add_reaction("\U0001F4E9")
    except Exception:
        # Best-effort signal; reaction failure should not block routing.
        pass

    return PrivateReplyMessage(message, dm_channel)


async def route_student_interaction(message: discord.Message):
    """
    Main routing function for all student interactions.

    LAYER 1: INTENT RECOGNITION
    - Parse: command vs natural language
    - Extract: student context

    LAYER 2: STATE MACHINE
    - Check: agent unlocked for current week?
    - Block or proceed based on temporal awareness

    LAYER 3: AGENT ROUTER
    - Dispatch to appropriate command handler

    Args:
        message: Discord message from student
    """
    # Normalize discord_id to str (Discord IDs are int in discord.py)
    discord_id = str(message.author.id)

    # Get or create student
    student = store.get_student(discord_id)
    if not student:
        student = store.create_student(discord_id)
        logger.info(f"Created new student: {discord_id}")

    response_message = await _prepare_response_message(message)

    # LAYER 1: INTENT RECOGNITION
    # Check if message is a slash command
    if message.content.startswith('/'):
        # Extract command name (e.g., "/frame what is ai" -> "frame")
        parts = message.content.split(maxsplit=1)
        command = parts[0][1:].lower()  # Remove leading slash

        # Handle artifact command with hyphen
        if command == "create" and len(parts) > 1 and parts[1].startswith("artifact"):
            command = "create-artifact"

        # Let core bot command handlers in main.py handle these commands.
        if command in BYPASS_CONTROLLER_COMMANDS:
            return

        await handle_command(response_message, student, command)
    else:
        # Natural language - classify intent and suggest command
        # Delayed import prevents circular dependency during module load.
        from cis_controller.suggestions import suggest_explicit_command

        await suggest_explicit_command(response_message, student)


async def handle_command(message: discord.Message, student, command: str):
    """
    Route command to appropriate handler with temporal awareness check.

    LAYER 2: STATE MACHINE - Temporal Awareness
    LAYER 3: AGENT ROUTER - Dispatch to handler

    Args:
        message: Discord message
        student: Student database row
        command: Command name (frame, diverge, challenge, synthesize, create-artifact)
    """
    try:
        current_week = int(student['current_week'])
    except (TypeError, ValueError, KeyError):
        current_week = 1

    # Unknown command - show available commands first (don't treat as lockout).
    if command not in CONTROLLED_COMMANDS:
        available = get_unlocked_agents(current_week)
        available_cmds = ", ".join([f"/{cmd}" for cmd in available])
        await message.reply(
            f"**Unknown command:** `/{command}`\n\n"
            f"**Available this week (Week {current_week}):**\n{available_cmds}\n\n"
            f"Type `/status` to check bot status."
        )
        return

    # Check temporal awareness (Decision 11: Week-based agent unlocking)
    if not is_agent_unlocked(command, current_week):
        await friendly_lockout_message(message, student, command)
        return

    # LAYER 3: AGENT ROUTER - Dispatch to command handler
    try:
        previous_state = get_student_state(student)

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

        elif command in {'save', 'review', 'publish'}:
            from commands.artifact import handle_artifact_commands
            await handle_artifact_commands(message, student, command)

        # LAYER 2: STATE MACHINE PERSISTENCE
        transition_state(previous_state, command, student=student, store=store)

        # Habit tracking + milestone celebration for relevant commands.
        habit_id = HABIT_BY_COMMAND.get(command)
        if habit_id is not None:
            discord_id = str(message.author.id)
            store.update_habit_practice(discord_id, habit_id)
            refreshed_student = store.get_student(discord_id)
            milestone_message = celebrate_habit(refreshed_student, habit_id)
            if milestone_message:
                await message.reply(milestone_message)

    except Exception as e:
        logger.error(f"Error handling command {command}: {e}")
        await message.reply(
            "**⚠️ Something went wrong.**\n\n"
            "The bot encountered an error. Try again in a moment."
        )


def is_agent_unlocked(agent: str, current_week: int) -> bool:
    """
    LAYER 1: Temporal awareness check (Decision 11).

    Week-based agent unlock schedule:
      Week 1:   /frame
      Week 4+:  /frame, /diverge, /challenge
      Week 6+:  all agents + /synthesize + /create-artifact

    Args:
        agent: Command name (frame, diverge, challenge, synthesize, create-artifact, save, review, publish)
        current_week: Student's current cohort week (1-8)

    Returns:
        True if agent is available this week, False if locked
    """
    unlock_week = UNLOCK_SCHEDULE.get(agent, 99)
    return current_week >= unlock_week


def get_unlocked_agents(current_week: int) -> list:
    """
    Get list of unlocked agents for given week.

    Args:
        current_week: Current cohort week (1-8)

    Returns:
        List of agent names available this week
    """
    return AGENTS_BY_WEEK.get(current_week, ["frame"])


async def friendly_lockout_message(message: discord.Message, student, agent: str):
    """
    Generate encouraging lockout message when agent not yet unlocked.

    Maintains psychological safety while enforcing Decision 11 schedule.

    Args:
        message: Discord message
        student: Student database row
        agent: Agent name that was tried
    """
    current_week = student['current_week']
    unlock_week = UNLOCK_SCHEDULE.get(agent, 99)
    available = get_unlocked_agents(current_week)
    available_cmds = ", ".join([f"/{cmd}" for cmd in available])

    response = f"""🔒 **{agent.capitalize()} unlocks Week {unlock_week}!**

You're currently in Week {current_week} - exactly where you should be.

**Available now:**
{available_cmds}

**Why the sequence matters:**
Each agent builds on the 4 Habits you're learning:
- ⏸️ **Pause** (Week 1): Know what you want
- 🎯 **Context** (Week 2): AI responds to YOUR situation
- 🔄 **Iterate** (Week 4): Explore one thing at a time
- 🧠 **Think First** (Week 6): Use AI before decisions

The {agent.capitalize()} will make more sense after practicing the earlier ones.

**You're on track. Keep going!** ✨"""

    await message.reply(response)

    # Log locked agent attempt for Trevor's awareness
    discord_id = str(message.author.id)
    store.log_observability_event(
        discord_id,
        "agent_locked_attempt",
        {"agent": agent, "current_week": current_week, "unlock_week": unlock_week}
    )


def setup_bot_events(bot: commands.Bot):
    """
    Attach routing to Discord bot events.

    Configures the bot to:
    - Ignore own messages
    - Process interactions in DMs and designated channels
    - Route to CIS Controller for command handling
    """
    @bot.event
    async def on_message(message: discord.Message):
        # Ignore bot's own messages
        if message.author.bot:
            return

        # Only process DMs or messages in designated channels
        if isinstance(message.channel, discord.DMChannel) or _is_designated_channel(message.channel):
            await route_student_interaction(message)

        # Always process prefix commands (e.g. /ping, /status)
        await bot.process_commands(message)
