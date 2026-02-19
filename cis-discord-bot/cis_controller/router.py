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
from cis_controller.safety_filter import (
    ComparisonViolationError,
    safety_filter,
    notify_trevor_safety_violation,
)
import logging

logger = logging.getLogger(__name__)

# Initialize state store
store = StudentStateStore()
_escalation_system = None
_participation_tracker = None

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

# Student-controlled consent gate for Guardrail #8 deep journey inspection.
JOURNEY_CONSENT_PHRASE = "i consent to journey inspection"
JOURNEY_CONSENT_REVOKE_PHRASE = "revoke journey inspection consent"

# Commands that belong to discord.py bot command handlers in main.py.
BYPASS_CONTROLLER_COMMANDS = {"ping", "status"}

# User-facing command aliases.
COMMAND_ALIASES = {
    "framer": "frame",
    "create_artifact": "create-artifact",
}

# Habit mapping for milestone tracking.
HABIT_BY_COMMAND = {
    "frame": 1,      # Pause
    "diverge": 3,    # Iterate
    "challenge": 4,  # Think First
    "synthesize": 4, # Think First
}

# Commands that already persist state/habit changes inside their handlers.
SELF_MANAGED_COMMANDS = {"frame", "diverge", "challenge", "synthesize"}

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
        self.guild = getattr(source_message, "guild", None)

    async def reply(self, content=None, **kwargs):
        return await self.channel.send(content, **kwargs)


class SlashInteractionMessage:
    """
    Adapter that lets slash-command interactions reuse message-based routing.
    """

    def __init__(self, interaction: discord.Interaction, content: str):
        self._interaction = interaction
        self.author = interaction.user
        self.content = content
        self.channel = interaction.channel
        self.guild = interaction.guild
        self.did_reply = False

    async def reply(self, content=None, **kwargs):
        self.did_reply = True
        kwargs.pop("mention_author", None)
        ephemeral = kwargs.pop("ephemeral", self._interaction.guild is not None)

        if self._interaction.response.is_done():
            return await self._interaction.followup.send(
                content, ephemeral=ephemeral, **kwargs
            )
        return await self._interaction.response.send_message(
            content, ephemeral=ephemeral, **kwargs
        )

    async def add_reaction(self, emoji):
        # Interactions are not tied to a message object we can react to.
        return None


def normalize_command_name(raw_command: str, remainder: str = "") -> str:
    """
    Normalize user-entered command names to canonical controller commands.
    """
    command = (raw_command or "").strip().lower()
    trailing = (remainder or "").strip().lower()

    # Handle legacy spaced variant: "/create artifact ..."
    if command == "create" and trailing.startswith("artifact"):
        command = "create-artifact"

    return COMMAND_ALIASES.get(command, command)


async def _send_interaction_feedback(
    interaction: discord.Interaction, content: str, ephemeral: bool | None = None
):
    """
    Send an interaction-safe response, regardless of response state.
    """
    if ephemeral is None:
        ephemeral = interaction.guild is not None

    if interaction.response.is_done():
        return await interaction.followup.send(content, ephemeral=ephemeral)
    return await interaction.response.send_message(content, ephemeral=ephemeral)


async def route_slash_command(
    interaction: discord.Interaction, command: str, prompt: str = ""
):
    """
    Entry point for Discord application slash commands.

    Converts the interaction into a message-like object so existing controller
    logic (DM routing, week unlock checks, handlers) stays centralized.
    """
    channel = interaction.channel
    if channel is None:
        await _send_interaction_feedback(
            interaction,
            "I could not detect this channel. Please try again.",
        )
        return

    is_dm = isinstance(channel, discord.DMChannel) or interaction.guild is None
    if not is_dm and not _is_designated_channel(channel):
        await _send_interaction_feedback(
            interaction,
            "Use this command in #thinking-lab, #bot-testing, or in DM.",
            ephemeral=True,
        )
        return

    prompt_text = (prompt or "").strip()
    normalized = normalize_command_name(command, prompt_text)
    synthetic_content = f"/{normalized}"
    if prompt_text:
        synthetic_content += f" {prompt_text}"

    synthetic_message = SlashInteractionMessage(interaction, synthetic_content)

    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=not is_dm, thinking=True)

    try:
        await route_student_interaction(synthetic_message, bot=interaction.client)
    except Exception as exc:
        logger.error("Error routing slash command %s: %s", normalized, exc, exc_info=True)
        if not synthetic_message.did_reply:
            await _send_interaction_feedback(
                interaction,
                "Something went wrong. Try again in a moment.",
                ephemeral=not is_dm,
            )
        return

    # Acknowledge slash invocation even when response is delivered in DM.
    if not synthetic_message.did_reply:
        if is_dm:
            await interaction.followup.send("Command received. Check this DM thread.")
        else:
            await interaction.followup.send(
                "Command received. Check your DMs from KIRA.",
                ephemeral=True,
            )


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
        try:
            dm_channel = await message.author.create_dm()
        except discord.Forbidden:
            await message.reply(
                "I can't DM you yet. Please enable direct messages and try again."
            )
            return None

    try:
        await message.add_reaction("\U0001F4E9")
    except Exception:
        # Best-effort signal; reaction failure should not block routing.
        pass

    return PrivateReplyMessage(message, dm_channel)


async def route_student_interaction(message: discord.Message, bot=None):
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
    if response_message is None:
        return

    # LAYER 1: INTENT RECOGNITION
    # Check if message is a slash command
    if message.content.startswith('/'):
        # Extract command name (e.g., "/frame what is ai" -> "frame")
        parts = message.content.split(maxsplit=1)
        trailing = parts[1] if len(parts) > 1 else ""
        command = normalize_command_name(parts[0][1:], trailing)

        # Let core bot command handlers in main.py handle these commands.
        if command in BYPASS_CONTROLLER_COMMANDS:
            return

        await handle_command(response_message, student, command)
    else:
        # Handle pending showcase share decisions in DM before NL intent suggestions.
        if isinstance(message.channel, discord.DMChannel):
            normalized_dm = " ".join(message.content.lower().strip().split())
            if normalized_dm == JOURNEY_CONSENT_PHRASE:
                store.record_student_consent(
                    discord_id=discord_id,
                    consent_type="journey_inspection",
                    source="student_dm_phrase",
                )
                await message.reply(
                    "✅ Consent recorded for journey inspection (valid for 24 hours). "
                    "You can revoke anytime by sending: `revoke journey inspection consent`."
                )
                return

            if normalized_dm == JOURNEY_CONSENT_REVOKE_PHRASE:
                store.revoke_student_consent(
                    discord_id=discord_id,
                    consent_type="journey_inspection",
                )
                await message.reply("✅ Journey inspection consent revoked.")
                return

            from commands.frame import (
                handle_showcase_share_response as frame_handle_showcase_share_response,
                has_pending_showcase_share as frame_has_pending_showcase_share,
            )
            from commands.diverge import (
                handle_showcase_share_response as diverge_handle_showcase_share_response,
                has_pending_showcase_share as diverge_has_pending_showcase_share,
            )
            from commands.challenge import (
                handle_showcase_share_response as challenge_handle_showcase_share_response,
                has_pending_showcase_share as challenge_has_pending_showcase_share,
            )
            from commands.synthesize import (
                handle_showcase_share_response as synthesize_handle_showcase_share_response,
                has_pending_showcase_share as synthesize_has_pending_showcase_share,
            )

            share_handlers = (
                (frame_has_pending_showcase_share, frame_handle_showcase_share_response),
                (diverge_has_pending_showcase_share, diverge_handle_showcase_share_response),
                (challenge_has_pending_showcase_share, challenge_handle_showcase_share_response),
                (synthesize_has_pending_showcase_share, synthesize_handle_showcase_share_response),
            )
            for has_pending_share, handle_share_response in share_handlers:
                if has_pending_share(discord_id):
                    handled = await handle_share_response(message)
                    if handled:
                        return

            # Route artifact workflow plain-text progression in DM before NL suggestions.
            from commands.artifact import handle_artifact_text_input

            artifact_handled = await handle_artifact_text_input(message, student, bot=bot)
            if artifact_handled:
                return

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

        # Some handlers already own lifecycle persistence to avoid double-counting.
        if command not in SELF_MANAGED_COMMANDS:
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

        # Track participation/reactions for weekly channels when enabled.
        if _participation_tracker:
            try:
                await _participation_tracker.on_message(message)
            except Exception as tracker_error:
                logger.error(
                    "Participation tracker failed for message from %s: %s",
                    message.author.id,
                    tracker_error,
                    exc_info=True,
                )

        # Task 2.3: SafetyFilter validation for ALL public channel messages
        # DMs are private spaces and don't go through SafetyFilter
        is_public_channel = not isinstance(message.channel, discord.DMChannel)

        if is_public_channel:
            try:
                # Check for crisis keywords (Level 4 intervention)
                crisis_type = safety_filter.detect_crisis(message.content)
                if crisis_type:
                    recent_messages = await _collect_recent_public_messages(message, limit=3)
                    student = store.get_student(str(message.author.id))
                    # Send crisis response and trigger Trevor alert immediately.
                    await message.channel.send(safety_filter.KENYA_CRISIS_RESPONSE)
                    await notify_trevor_safety_violation(
                        bot=bot,
                        violation_type="crisis",
                        message=message.content,
                        student_discord_id=message.author.id,
                        escalation_system=_escalation_system,
                        last_messages=recent_messages,
                        emotional_state=(
                            student["emotional_state"] if student and student["emotional_state"] else "unknown"
                        ),
                    )
                    # Message already handled (crisis response sent, Trevor alerted)
                    return

                # Check for comparison/ranking language (Guardrail #3)
                # Only validates, doesn't block (we want the bot to still process commands)
                safety_filter.validate_no_comparison(message.content)

            except ComparisonViolationError as safety_error:
                # Safety violation detected - log and notify Trevor
                logger.critical(f"Safety violation in message from {message.author.id}: {safety_error}")
                await notify_trevor_safety_violation(
                    bot=bot,
                    violation_type="comparison",
                    message=message.content,
                    student_discord_id=message.author.id,
                )
                # Don't process the message further if it has safety violations
                return
            except Exception as safety_error:
                logger.error(
                    "Safety filter processing failed for message from %s: %s",
                    message.author.id,
                    safety_error,
                    exc_info=True,
                )
                return

        # Only process DMs or messages in designated channels
        if isinstance(message.channel, discord.DMChannel) or _is_designated_channel(message.channel):
            await route_student_interaction(message, bot=bot)

        # Always process prefix commands (e.g. /ping, /status)
        await bot.process_commands(message)


def set_runtime_services(escalation_system=None, participation_tracker=None):
    """
    Inject runtime services created in main.py after bot startup.
    """
    global _escalation_system, _participation_tracker
    _escalation_system = escalation_system
    _participation_tracker = participation_tracker


async def _collect_recent_public_messages(
    message: discord.Message, limit: int = 3
) -> list[str]:
    """
    Collect the author's most recent public channel messages for Level 4 context.
    """
    collected = []

    current_text = " ".join((message.content or "").split())
    if current_text:
        collected.append(f"user: {current_text[:160]}")

    try:
        async for prior in message.channel.history(limit=50):
            if prior.id == message.id or prior.author.id != message.author.id:
                continue
            if prior.author.bot:
                continue
            text = " ".join((prior.content or "").split())
            if not text:
                continue
            collected.append(f"user: {text[:160]}")
            if len(collected) >= limit:
                break
    except Exception as exc:
        logger.warning("Could not collect recent public messages: %s", exc)

    return collected[:limit]
