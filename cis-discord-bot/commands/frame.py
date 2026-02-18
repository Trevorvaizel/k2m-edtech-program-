"""
Frame Command Handler
Story 4.7 + Task 1.5/1.6 implementation
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import discord

from cis_controller.llm_integration import call_agent_with_context
from cis_controller.rate_limiter import rate_limiter
from cis_controller.safety_filter import (
    ComparisonViolationError,
    safety_filter,
)
from cis_controller.state_machine import celebrate_habit, transition_state
from database.store import StudentStateStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

store = StudentStateStore()

CHANNEL_THINKING_SHOWCASE = os.getenv("CHANNEL_THINKING_SHOWCASE", "").strip()
CHANNEL_FACILITATOR_DASHBOARD = os.getenv(
    "CHANNEL_FACILITATOR_DASHBOARD", ""
).strip()
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID", "").strip()

# Pending student choices for the "share to showcase?" prompt.
PENDING_SHOWCASE_SHARES: Dict[str, Dict] = {}
PENDING_SHARE_TTL = timedelta(hours=24)


def has_pending_showcase_share(discord_id: str) -> bool:
    _evict_expired_pending_shares()
    return str(discord_id) in PENDING_SHOWCASE_SHARES


def _evict_expired_pending_shares() -> None:
    now = datetime.now(timezone.utc)
    expired = [
        discord_id
        for discord_id, payload in PENDING_SHOWCASE_SHARES.items()
        if now - payload.get("created_at", now) > PENDING_SHARE_TTL
    ]
    for discord_id in expired:
        PENDING_SHOWCASE_SHARES.pop(discord_id, None)


def _normalize_share_choice(raw_text: str) -> Optional[str]:
    text = (raw_text or "").strip().lower()
    if text in {"yes", "y", "share", "publish"}:
        return "yes"
    if text in {"no", "n", "keep private", "private"}:
        return "no"
    if text in {"anonymous", "anon"}:
        return "anonymous"
    if text in {"maybe later", "later", "not now"}:
        return "maybe_later"
    return None


def _iter_candidate_guilds(message: discord.Message):
    guild = getattr(message, "guild", None)
    if guild is not None:
        yield guild

    author = getattr(message, "author", None)
    for candidate in getattr(author, "mutual_guilds", []) or []:
        yield candidate


def _filter_guild(guild) -> bool:
    if not DISCORD_GUILD_ID:
        return True
    return str(getattr(guild, "id", "")) == DISCORD_GUILD_ID


def _find_channel_by_id_or_slug(guild, configured_id: str, slug: str):
    if configured_id:
        try:
            target_id = int(configured_id)
            channel = guild.get_channel(target_id)
            if channel:
                return channel
        except ValueError:
            logger.warning("Invalid channel id in env: %s", configured_id)

    for channel in getattr(guild, "text_channels", []):
        name = getattr(channel, "name", "").lower()
        if name == slug or name.endswith(slug) or slug in name:
            return channel
    return None


def _find_showcase_channel(message: discord.Message):
    for guild in _iter_candidate_guilds(message):
        if not _filter_guild(guild):
            continue
        channel = _find_channel_by_id_or_slug(
            guild, CHANNEL_THINKING_SHOWCASE, "thinking-showcase"
        )
        if channel:
            return channel
    return None


def _find_dashboard_channel(message: discord.Message):
    for guild in _iter_candidate_guilds(message):
        if not _filter_guild(guild):
            continue
        channel = _find_channel_by_id_or_slug(
            guild, CHANNEL_FACILITATOR_DASHBOARD, "facilitator-dashboard"
        )
        if channel:
            return channel
    return None


def _register_pending_share(discord_id: str, user_message: str, student_context):
    snippet = " ".join(user_message.split())
    if len(snippet) > 180:
        snippet = f"{snippet[:177]}..."

    PENDING_SHOWCASE_SHARES[str(discord_id)] = {
        "created_at": datetime.now(timezone.utc),
        "snippet": snippet,
        "week": getattr(student_context, "current_week", None),
        "zone": getattr(student_context, "zone", None),
    }


def _build_showcase_post(author: discord.abc.User, decision: str, payload: Dict) -> str:
    snippet = payload.get("snippet") or "a framing session"
    week = payload.get("week")
    zone = payload.get("zone")
    context = []
    if week is not None:
        context.append(f"Week {week}")
    if zone:
        context.append(zone.replace("_", " ").title())
    context_text = f" ({', '.join(context)})" if context else ""

    if decision == "anonymous":
        lead = "🌟 **A student** shared a thinking milestone from #thinking-lab"
    else:
        lead = f"🌟 **{author.display_name}** shared a thinking milestone from #thinking-lab"

    return (
        f"{lead}{context_text}.\n"
        f"🧠 Framed focus: \"{snippet}\"\n"
        "⏸️🎯 Practiced habits: Pause + Context\n"
        "Process stayed private. Celebration only."
    )


async def _notify_budget_alerts(message: discord.Message, budget_state: Dict[str, float]):
    if not budget_state:
        return

    if not (
        budget_state.get("daily_alert_triggered")
        or budget_state.get("weekly_alert_triggered")
        or budget_state.get("weekly_cap_exceeded")
    ):
        return

    dashboard_channel = _find_dashboard_channel(message)
    if dashboard_channel is None:
        logger.warning(
            "Budget alert triggered but #facilitator-dashboard could not be resolved."
        )
        return

    lines = []
    if budget_state.get("daily_alert_triggered"):
        lines.append(
            "💰 **Daily Budget Alert**\n"
            f"Current daily spend: ${budget_state.get('daily_total', 0.0):.2f} "
            f"(threshold: ${rate_limiter.DAILY_BUDGET_ALERT:.2f})"
        )

    if budget_state.get("weekly_alert_triggered") or budget_state.get(
        "weekly_cap_exceeded"
    ):
        lines.append(
            "🚨 **Weekly Budget Cap Reached**\n"
            f"Current weekly spend: ${budget_state.get('weekly_total', 0.0):.2f} "
            f"(cap: ${rate_limiter.WEEKLY_BUDGET_CAP:.2f})"
        )

    if lines:
        await dashboard_channel.send("\n\n".join(lines))


async def handle_showcase_share_response(message: discord.Message) -> bool:
    """
    Handle Yes/No/Anonymous decision after /frame showcase prompt.
    """
    discord_id = str(message.author.id)
    if not has_pending_showcase_share(discord_id):
        return False

    decision = _normalize_share_choice(message.content)
    if decision is None:
        await message.reply(
            "Please choose one: **Yes**, **No**, **Anonymous**, or **Maybe later**."
        )
        return True

    payload = PENDING_SHOWCASE_SHARES.get(discord_id, {})

    if decision in {"no", "maybe_later"}:
        PENDING_SHOWCASE_SHARES.pop(discord_id, None)
        if decision == "maybe_later":
            await message.reply(
                "No problem. I saved your progress and we can share later if you choose."
            )
        else:
            await message.reply(
                "Kept private. Your process stays between you and KIRA."
            )
        return True

    showcase_channel = _find_showcase_channel(message)
    if showcase_channel is None:
        PENDING_SHOWCASE_SHARES.pop(discord_id, None)
        await message.reply(
            "I couldn't find #thinking-showcase right now, so I kept this private."
        )
        return True

    post_text = _build_showcase_post(message.author, decision, payload)
    try:
        safety_filter.validate_no_comparison(post_text)
        # #thinking-showcase is finished-work only (Story 5.3).
        safety_filter.validate_showcase_content(post_text)
    except ComparisonViolationError:
        PENDING_SHOWCASE_SHARES.pop(discord_id, None)
        await message.reply(
            "I kept this private for now. #thinking-showcase only accepts finished work."
        )
        return True

    await showcase_channel.send(post_text)

    PENDING_SHOWCASE_SHARES.pop(discord_id, None)
    await message.reply("Shared to #thinking-showcase. Nice work.")
    return True


async def handle_frame(message: discord.Message, student):
    """
    Handle /frame command end-to-end:
    command -> DM -> private conversation -> optional showcase share.
    """
    discord_id = str(message.author.id)

    allowed, error_message = rate_limiter.check_rate_limit(discord_id)
    if not allowed:
        await message.reply(error_message)
        logger.warning("Rate limit blocked /frame for %s", discord_id)
        return

    try:
        dm_channel = await message.author.create_dm()
    except discord.Forbidden:
        await message.reply(
            "🚫 **Cannot start DM** - I need permission to send you private messages. "
            "Please enable DMs in your privacy settings, then try /frame again."
        )
        return

    student_context = store.build_student_context(discord_id)
    if not student_context:
        await message.reply("❌ Error loading your profile. Please try again.")
        logger.error("Failed to build StudentContext for %s", discord_id)
        return

    conversation_history = store.get_conversation_history(discord_id, "frame", limit=10)
    user_message = message.content.replace("/frame", "").strip()
    if not user_message:
        user_message = "I want to practice framing a question."

    try:
        logger.info("Calling Framer agent for %s", discord_id)

        framer_response, cost_data = await call_agent_with_context(
            agent="frame",
            student_context=student_context,
            user_message=user_message,
            conversation_history=conversation_history,
        )

        budget_state = rate_limiter.track_interaction(
            discord_id=discord_id,
            agent="frame",
            tokens=cost_data.get("total_tokens", 0),
            cost_usd=cost_data.get("total_cost_usd", 0.0),
        )
        await _notify_budget_alerts(message, budget_state)

        safety_filter.validate_no_comparison(framer_response)

        store.save_conversation(
            discord_id=discord_id,
            agent="frame",
            role="user",
            content=user_message,
        )
        store.save_conversation(
            discord_id=discord_id,
            agent="frame",
            role="assistant",
            content=framer_response,
        )

        store.update_habit_practice(discord_id, habit_id=1)

        refreshed_student = store.get_student(discord_id)
        celebration = celebrate_habit(refreshed_student, habit_id=1)
        full_response = (
            f"{framer_response}\n\n{celebration}" if celebration else framer_response
        )
        await dm_channel.send(full_response)

        current_state = student_context.current_state
        transition_state(current_state, "frame", student=student, store=store)

        store.log_observability_event(
            discord_id,
            "agent_used",
            {
                "agent": "frame",
                "week": student_context.current_week,
                "zone": student_context.zone,
                "cost_usd": cost_data.get("total_cost_usd", 0.0),
            },
        )

        _register_pending_share(discord_id, user_message, student_context)
        await dm_channel.send(
            "\n---\n"
            "💡 **Want to share this to #thinking-showcase?**\n\n"
            "Choose one:\n"
            "- **Yes** (share with your name)\n"
            "- **Anonymous** (share without your name)\n"
            "- **No** (keep private)\n\n"
            "Reply with: **Yes / No / Anonymous / Maybe later**"
        )

        logger.info(
            "Handled /frame for %s | Tokens: %s | Cost: $%.4f",
            discord_id,
            cost_data.get("total_tokens", 0),
            cost_data.get("total_cost_usd", 0.0),
        )

    except Exception as exc:
        logger.error("Error in handle_frame for %s: %s", discord_id, exc)
        await dm_channel.send(
            "**⏸️ The Framer is taking a short break.**\n\n"
            "Try this on your own:\n"
            "1. **PAUSE**: What do you actually want to know?\n"
            "2. **ADD CONTEXT**: What's your situation?\n\n"
            f"Your question: _{user_message}_\n\n"
            "**You're practicing Habit 1 (⏸️ PAUSE) - you've got this!**\n\n"
            "Try /frame again in a moment."
        )
