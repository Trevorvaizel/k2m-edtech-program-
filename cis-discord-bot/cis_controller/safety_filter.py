"""
CIS Controller - Safety Filter
Story 4.7 Implementation: SafetyFilter anti-comparison validation

Guardrail #3 compliance infrastructure.
EVERY public Discord message must pass through this filter.
Prevents comparison/ranking language from ever reaching students.

Task 2.3 Enhancement: Crisis detection and Level 4 intervention
"""

import re
import logging
import os
from typing import List, Optional, Dict, Any
import discord

from database import store

logger = logging.getLogger(__name__)


class ComparisonViolationError(Exception):
    """Raised when message contains forbidden comparison/ranking."""
    pass


class CrisisDetectedError(Exception):
    """Raised when crisis keywords are detected."""
    def __init__(self, message: str, crisis_type: str):
        self.crisis_type = crisis_type
        super().__init__(message)


class SafetyFilter:
    """
    Anti-comparison validation layer (Guardrail #3).
    Crisis detection and Level 4 intervention (Task 2.3).

    EVERY public Discord message passes through this filter.
    Prevents Guardrail #3 violations from ever shipping.
    Detects crisis keywords and triggers Level 4 intervention protocol.
    """

    # Guardrail #3: Comparison/Ranking keywords
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

    # Task 2.3: Level 4 Crisis Intervention keywords
    CRISIS_KEYWORDS = [
        "self-harm", "self harm", "self injury",
        "suicide", "suicidal",
        "want to die", "want to end it", "want to kill myself",
        "can't go on", "cannot go on", "cant go on",
        "hopeless", "hopelessness", "worthless",
        "end it all", "ending it all",
        "kill myself", "kill myself",
        "no point", "nothing matters", "give up"
    ]

    FORBIDDEN_PATTERNS = [
        r"student.*?#\d+",                            # "student #1", "student #2"
        r"top\s+\d+",                                 # "top 5", "top 10"
        r"\d+\s*(st|nd|rd|th)\s+place",              # "1st place", "2nd place"
        r"student.*?(better|worse|faster|slower).*?than",  # Comparisons
    ]

    # Task 2.3: Kenya Crisis Response Message
    KENYA_CRISIS_RESPONSE = """💚 **You matter.**

If you're in crisis, help is available right now:

📞 **Kenya Crisis Hotline:** 119 (free, 24/7)
📱 **Trevor:** 0116 405604 (reaching out within 1 hour)
🆘 **Emergency:** Go to nearest hospital or call 999

You are not alone. Help is here."""

    def validate_no_comparison(self, message_text: str) -> bool:
        """
        Validate message contains NO comparison/ranking.

        Raises ComparisonViolationError if violation detected.
        Returns True if safe.
        """
        message_lower = message_text.lower()

        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in message_lower:
                logger.error(f"Comparison violation: keyword '{keyword}' in message")
                raise ComparisonViolationError(
                    f"Message contains forbidden comparison keyword: '{keyword}'\n"
                    f"Full message: {message_text[:100]}..."
                )

        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, message_lower):
                logger.error(f"Comparison violation: pattern '{pattern}' matched")
                raise ComparisonViolationError(
                    f"Message matches forbidden comparison pattern: {pattern}\n"
                    f"Full message: {message_text[:100]}..."
                )

        logger.info(f"Safety check PASSED: {message_text[:50]}...")
        return True

    def detect_crisis(self, message_text: str) -> Optional[str]:
        """
        Task 2.3: Detect crisis keywords in message.

        Returns crisis_type if detected, None otherwise.
        Triggers Level 4 intervention protocol.
        """
        # Normalize whitespace and case so variations like
        # "I can't  go   on" still match crisis keywords.
        message_lower = " ".join(message_text.lower().split())

        for keyword in self.CRISIS_KEYWORDS:
            if keyword in message_lower:
                logger.critical(f"CRISIS DETECTED: keyword '{keyword}' in message")
                return "mental_health_crisis"

        return None

    def validate_showcase_content(self, message_text: str) -> bool:
        """
        Task 2.3: Validate #thinking-showcase content.

        Blocks unfinished work and process drafts.
        Only allows polished, complete artifacts.
        """
        message_lower = message_text.lower()

        # Block phrases indicating unfinished work
        unfinished_phrases = [
            "still working on",
            "not sure yet",
            "need to add",
            "draft",
            "work in progress",
            "wip",
            "to be continued",
            "incomplete",
            "not finished"
        ]

        for phrase in unfinished_phrases:
            if phrase in message_lower:
                logger.warning(f"Showcase validation blocked: unfinished work phrase '{phrase}'")
                raise ComparisonViolationError(
                    f"#thinking-showcase is for finished work only. "
                    f"Detected unfinished work phrase: '{phrase}'\n"
                    f"Please complete your artifact before sharing."
                )

        return True

    def validate_aggregate_message(self, message_text: str, mentioned_students: List[str]) -> bool:
        """
        Additional validation for aggregate visibility messages.

        Ensures aggregate messages are non-comparative:
        ALLOWED: "15 students practiced /frame this week" ✅
        FORBIDDEN: "Sarah, John, and Mary practiced /frame" ❌
        """
        if mentioned_students and len(mentioned_students) > 0:
            if any(keyword in message_text.lower() for keyword in ["practiced", "completed", "used"]):
                raise ComparisonViolationError(
                    "Aggregate message mentions specific student names with action verbs. "
                    "This creates implicit comparison. Use counts only, no names."
                )
        return True


# Singleton instance
safety_filter = SafetyFilter()


def _resolve_channel_by_id_or_slug(
    bot: discord.Client,
    configured_id: str,
    slug: str,
) -> Optional[discord.abc.Messageable]:
    """Find a channel by configured ID or slug fallback."""
    if configured_id:
        try:
            target_id = int(configured_id)
            for guild in getattr(bot, "guilds", []):
                channel = guild.get_channel(target_id)
                if channel:
                    return channel
        except ValueError:
            logger.warning("Invalid channel ID configured for %s: %s", slug, configured_id)

    for guild in getattr(bot, "guilds", []):
        for channel in getattr(guild, "text_channels", []):
            channel_name = getattr(channel, "name", "").lower()
            if (
                channel_name == slug
                or channel_name.endswith(slug)
                or slug in channel_name
            ):
                return channel
    return None


def _load_crisis_context(student_discord_id: Optional[int]) -> Dict[str, Any]:
    """
    Build crisis context payload required by Level 4 protocol:
    - student's last 3 stored messages
    - current emotional state flag
    """
    if student_discord_id is None:
        return {"emotional_state": "unknown", "last_messages": []}

    student_id = str(student_discord_id)
    db = None
    try:
        db = store.StudentStateStore()
        student = db.get_student(student_id)
        emotional_state = (
            student["emotional_state"] if student and student["emotional_state"] else "unknown"
        )

        cursor = db.conn.execute(
            """
            SELECT role, content
            FROM conversations
            WHERE student_id = ?
            ORDER BY created_at DESC
            LIMIT 3
            """,
            (student_id,),
        )

        messages = []
        for row in cursor.fetchall():
            role = row["role"] if row["role"] else "unknown"
            content = " ".join((row["content"] or "").split())
            if len(content) > 140:
                content = f"{content[:137]}..."
            messages.append(f"{role}: {content}")

        return {"emotional_state": emotional_state, "last_messages": messages}
    except Exception as exc:
        logger.error("Failed to load crisis context for %s: %s", student_id, exc)
        return {"emotional_state": "unknown", "last_messages": []}
    finally:
        if db:
            db.close()


async def _log_to_moderation_logs(
    bot: discord.Client,
    violation_type: str,
    message: str,
    student_discord_id: Optional[int] = None,
    emotional_state: Optional[str] = None,
):
    """Log safety events to #moderation-logs channel if available."""
    configured_channel_id = os.getenv("CHANNEL_MODERATION_LOGS", "").strip()
    channel = _resolve_channel_by_id_or_slug(bot, configured_channel_id, "moderation-logs")
    if channel is None:
        logger.warning("Could not resolve #moderation-logs channel for safety logging")
        return

    trimmed = " ".join((message or "").split())
    if len(trimmed) > 180:
        trimmed = f"{trimmed[:177]}..."

    try:
        if violation_type == "crisis":
            log_message = (
                "🚨 **Level 4 Crisis Logged**\n"
                f"Student ID: `{student_discord_id}`\n"
                f"Emotional State: `{emotional_state or 'unknown'}`\n"
                f"Detected Message: \"{trimmed}\""
            )
        else:
            log_message = (
                "⚠️ **Guardrail #3 Violation Logged**\n"
                f"Student ID: `{student_discord_id}`\n"
                f"Blocked Message: \"{trimmed}\""
            )
        await channel.send(log_message)
    except discord.DiscordException as exc:
        logger.error("Failed to post to #moderation-logs: %s", exc)


async def notify_trevor_safety_violation(
    bot: discord.Client,
    violation_type: str,
    message: str,
    student_discord_id: Optional[int] = None
):
    """
    Task 2.3: Send Trevor alert for safety violations.

    Level 4: Crisis - INSTANT DM with last 3 messages
    Level 3: Comparison - Log to #moderation-logs
    """
    # Get Trevor's Discord ID from environment
    trevor_discord_id = os.getenv('TREVOR_DISCORD_ID')

    if not trevor_discord_id:
        logger.error("TREVOR_DISCORD_ID not set in environment variables")
        return

    try:
        # Get Trevor user object
        trevor_user = await bot.fetch_user(int(trevor_discord_id))

        if violation_type == "crisis":
            crisis_context = _load_crisis_context(student_discord_id)
            emotional_state = crisis_context.get("emotional_state", "unknown")
            last_messages = crisis_context.get("last_messages", [])
            if last_messages:
                last_messages_block = "\n".join(f"- {line}" for line in last_messages)
            else:
                last_messages_block = "- No prior stored messages available."

            # Level 4: INSTANT crisis alert
            alert_message = f"""🚨 **LEVEL 4 CRISIS INTERVENTION**

**Crisis Detected** in student message:
"{message[:100]}..."

**Student ID:** {student_discord_id}
**Emotional State Flag:** {emotional_state}

**Last 3 messages:**
{last_messages_block}

**Action Required:**
⚠️ DM student within 1 hour
⚠️ Assess risk level
⚠️ If minor (<18) and high risk: call parent within 2 hours
⚠️ Provide Kenya crisis resources
"""

            await trevor_user.send(alert_message)
            logger.critical(f"CRISIS ALERT sent to Trevor for student {student_discord_id}")
            await _log_to_moderation_logs(
                bot=bot,
                violation_type="crisis",
                message=message,
                student_discord_id=student_discord_id,
                emotional_state=emotional_state,
            )

        elif violation_type == "comparison":
            # Level 3: Comparison violation (less urgent)
            alert_message = f"""⚠️ **Guardrail #3 Violation Blocked**

**Violation Type:** Comparison/Ranking Language

**Message Blocked:**
"{message[:100]}..."

**Student ID:** {student_discord_id}

Logged to #moderation-logs"""

            await trevor_user.send(alert_message)
            logger.warning(f"Comparison violation alert sent to Trevor for student {student_discord_id}")
            await _log_to_moderation_logs(
                bot=bot,
                violation_type="comparison",
                message=message,
                student_discord_id=student_discord_id,
            )

    except discord.DiscordException as e:
        logger.error(f"Failed to send Trevor alert: {e}")


async def post_to_discord_safe(
    bot: discord.Client,
    channel,
    message_text: str,
    student_discord_id: Optional[int] = None,
    is_showcase: bool = False
):
    """
    Wrapper for Discord posting with safety validation.

    Task 2.3 Enhancement:
    - Validates comparison language (Guardrail #3)
    - Detects crisis keywords (Level 4 intervention)
    - Validates showcase content (blocks unfinished work)
    - Alerts Trevor on violations

    ALL public messages MUST use this function.
    """
    try:
        # 1. Crisis detection (highest priority - Level 4)
        crisis_type = safety_filter.detect_crisis(message_text)
        if crisis_type:
            # Send crisis response immediately
            await channel.send(safety_filter.KENYA_CRISIS_RESPONSE)
            # Alert Trevor instantly
            await notify_trevor_safety_violation(bot, "crisis", message_text, student_discord_id)
            # Log to moderation logs
            logger.critical(f"CRISIS: {message_text[:100]}... | Student: {student_discord_id}")
            raise CrisisDetectedError(message_text, crisis_type)

        # 2. Comparison validation (Guardrail #3)
        safety_filter.validate_no_comparison(message_text)

        # 3. Showcase content validation (if applicable)
        if is_showcase:
            safety_filter.validate_showcase_content(message_text)

        # All checks passed - post to Discord
        await channel.send(message_text)
        logger.info(f"Message posted safely: {message_text[:50]}...")

    except ComparisonViolationError as e:
        # Log violation and alert Trevor
        logger.critical(f"COMPARISON VIOLATION BLOCKED: {e}")
        await notify_trevor_safety_violation(bot, "comparison", message_text, student_discord_id)
        # Do NOT post message
        raise

    except CrisisDetectedError:
        # Already handled above (crisis response sent, Trevor alerted)
        raise
