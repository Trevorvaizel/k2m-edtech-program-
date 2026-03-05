"""
Showcase workflow helpers.

Task 3.5 (Decision 12):
- Private DM process stays private
- Student chooses Yes / Anonymous / No
- Public celebration posts to #thinking-showcase only after safety validation
"""

import asyncio
import logging
import os
from typing import Optional

import discord
from discord.ext import commands

from cis_controller.celebration_generator import generate_celebration_message
from cis_controller.safety_filter import ComparisonViolationError, SafetyFilter
from database import get_store

logger = logging.getLogger(__name__)
store = get_store()
safety_filter = SafetyFilter()

VALID_PREFERENCES = {"always_ask", "always_yes", "always_no", "week8_only"}
CHANNEL_THINKING_SHOWCASE = os.getenv("CHANNEL_THINKING_SHOWCASE", "").strip()

HABIT_ICONS = {
    1: "\N{DOUBLE VERTICAL BAR}",  # Pause
    2: "\N{DIRECT HIT}",  # Context
    3: "\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}",  # Iterate
    4: "\N{BRAIN}",  # Think First
}


def _find_showcase_channel(bot: commands.Bot):
    guild = bot.guilds[0] if bot.guilds else None
    if not guild:
        return None

    if CHANNEL_THINKING_SHOWCASE:
        try:
            configured_id = int(CHANNEL_THINKING_SHOWCASE)
            by_id = guild.get_channel(configured_id)
            # Guard against loose mocks in tests; ensure resolved channel ID matches.
            if by_id is not None and getattr(by_id, "id", None) == configured_id:
                return by_id
        except ValueError:
            logger.warning(
                "Invalid CHANNEL_THINKING_SHOWCASE id: %s",
                CHANNEL_THINKING_SHOWCASE,
            )

    channels = getattr(guild, "text_channels", None)
    if not isinstance(channels, (list, tuple)):
        channels = getattr(guild, "channels", []) or []

    for channel in channels:
        name = str(getattr(channel, "name", "")).lower()
        if name == "thinking-showcase" or name.endswith("thinking-showcase") or "thinking-showcase" in name:
            return channel
    return None


def _normalize_visibility_from_reaction(emoji: str) -> Optional[str]:
    mapping = {
        "1\ufe0f\u20e3": "public",
        "2\ufe0f\u20e3": "anonymous",
        "3\ufe0f\u20e3": "private",
    }
    return mapping.get(emoji)


def set_showcase_preference_for_student(discord_id: str, preference: str) -> None:
    """Programmatic preference setter (used by slash command handlers)."""
    preference = (preference or "").strip().lower()
    if preference not in VALID_PREFERENCES:
        raise ValueError(f"Invalid preference: {preference}")
    store.set_publication_preference(str(discord_id), preference)


async def prompt_share_to_showcase(
    bot: commands.Bot,
    message: discord.Message,
    student_discord_id: str,
    agent_used: str,
    habits_practiced: list = None,
):
    """
    Ask the student whether to share a completed thinking milestone publicly.
    """
    student_discord_id = str(student_discord_id)
    habits_practiced = habits_practiced or [1, 2]
    preference = store.get_publication_preference(student_discord_id)
    student_row = store.get_student(student_discord_id) or store.create_student(student_discord_id)
    current_week = int(student_row["current_week"])

    if preference == "always_no":
        logger.info("Student %s has always_no preference; skipped showcase prompt.", student_discord_id)
        return

    if preference == "always_yes":
        await publish_to_showcase(
            bot=bot,
            student_discord_id=student_discord_id,
            agent_used=agent_used,
            visibility="public",
            habits_practiced=habits_practiced,
            original_message=message,
        )
        return

    if preference == "week8_only" and current_week < 8:
        await message.reply(
            "**Saved for your Week 8 artifact.**\n\n"
            "Your learning stays private for now and can be shared at graduation."
        )
        return

    share_prompt = (
        "**Want to share your learning to #thinking-showcase?**\n\n"
        f"You just practiced with **/{agent_used}**.\n\n"
        "**Choose one:**\n"
        "**[1] Public** - Share with your name\n"
        "**[2] Anonymous** - Share without your name\n"
        "**[3] Not now** - Keep private\n\n"
        "Tip: set a permanent preference with `/showcase-preference`."
    )
    share_message = await message.reply(share_prompt)
    await share_message.add_reaction("1\ufe0f\u20e3")
    await share_message.add_reaction("2\ufe0f\u20e3")
    await share_message.add_reaction("3\ufe0f\u20e3")

    def check_reaction(reaction, user):
        return (
            str(user.id) == student_discord_id
            and reaction.message.id == share_message.id
            and str(reaction.emoji) in {"1\ufe0f\u20e3", "2\ufe0f\u20e3", "3\ufe0f\u20e3"}
        )

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check_reaction)
        visibility = _normalize_visibility_from_reaction(str(reaction.emoji))
        if visibility:
            await publish_to_showcase(
                bot=bot,
                student_discord_id=student_discord_id,
                agent_used=agent_used,
                visibility=visibility,
                habits_practiced=habits_practiced,
                original_message=message,
            )
    except asyncio.TimeoutError:
        logger.info("Share prompt timeout for %s", student_discord_id)
    finally:
        try:
            await share_message.clear_reactions()
        except Exception:
            pass


async def publish_to_showcase(
    bot: commands.Bot,
    student_discord_id: str,
    agent_used: str,
    visibility: str,
    habits_practiced: list = None,
    original_message: discord.Message = None,
):
    """
    Publish a celebration message to #thinking-showcase or keep it private.
    """
    try:
        student_discord_id = str(student_discord_id)
        habits_practiced = habits_practiced or [1, 2]
        student = store.get_student(student_discord_id) or store.create_student(student_discord_id)

        if visibility == "private":
            private_message = (
                "**Conversation saved privately.**\n\n"
                "Your learning is saved for your Week 8 artifact."
            )
            store.create_showcase_publication(
                discord_id=student_discord_id,
                publication_type="habit_practice",
                visibility_level="private",
                celebration_message=private_message,
                habits_demonstrated=[HABIT_ICONS.get(h, "") for h in habits_practiced],
                nodes_mastered=[],
                parent_email_included=False,
            )
            if original_message:
                await original_message.reply(private_message)
            return

        showcase_channel = _find_showcase_channel(bot)
        if not showcase_channel:
            logger.error("#thinking-showcase channel not found")
            return

        celebration = await generate_celebration_message(
            student_id=student_discord_id,
            agent_used=agent_used,
            visibility=visibility,
            habits_practiced=habits_practiced,
            zone=student["zone"],
            week=student["current_week"],
        )

        safety_filter.validate_no_comparison(celebration)
        safety_filter.validate_showcase_content(celebration)

        posted_message = await showcase_channel.send(celebration)
        if posted_message and hasattr(posted_message, "add_reaction"):
            try:
                reaction_result = posted_message.add_reaction("\N{WHITE MEDIUM STAR}")
                if asyncio.iscoroutine(reaction_result):
                    await reaction_result
            except Exception:
                logger.debug("Could not add star reaction for showcase message.", exc_info=True)

        store.create_showcase_publication(
            discord_id=student_discord_id,
            publication_type="habit_practice",
            visibility_level=visibility,
            celebration_message=celebration,
            habits_demonstrated=[HABIT_ICONS.get(h, "") for h in habits_practiced],
            nodes_mastered=[],
            parent_email_included=False,
        )

        if original_message:
            if visibility == "public":
                confirm = "**Posted to #thinking-showcase.** Nice work."
            else:
                confirm = "**Posted anonymously to #thinking-showcase.** Nice work."
            await original_message.reply(confirm)

        logger.info("Published showcase celebration for %s as %s", student_discord_id, visibility)

    except ComparisonViolationError as exc:
        logger.error("SafetyFilter blocked celebration for %s: %s", student_discord_id, exc)
        if original_message:
            await original_message.reply(
                "I kept this private for now. #thinking-showcase only accepts finished work."
            )
    except Exception as exc:
        logger.error("Error publishing to showcase for %s: %s", student_discord_id, exc)
        if original_message:
            await original_message.reply(
                "**Something went wrong.** Your growth is saved; try sharing again later."
            )


async def set_showcase_preference(message: discord.Message, preference: str):
    """
    Set student's permanent showcase publication preference.
    """
    preference = (preference or "").strip().lower()
    if preference not in VALID_PREFERENCES:
        await message.reply(
            "**Invalid preference.**\n\n"
            "Valid options: always_ask, always_yes, always_no, week8_only\n\n"
            "- always_ask: ask every time (default)\n"
            "- always_yes: auto-publish celebrations\n"
            "- always_no: keep conversations private\n"
            "- week8_only: publish during Week 8 artifact only"
        )
        return

    store.set_publication_preference(message.author.id, preference)

    descriptions = {
        "always_ask": "I will ask you every time.",
        "always_yes": "I will auto-publish your celebrations publicly.",
        "always_no": "I will keep your conversations private.",
        "week8_only": "I will save celebrations for Week 8 publication.",
    }
    await message.reply(
        "**Showcase preference updated.**\n\n"
        f"Setting: `{preference}`\n"
        f"What this means: {descriptions[preference]}"
    )
    logger.info("Student %s set showcase preference to %s", message.author.id, preference)

