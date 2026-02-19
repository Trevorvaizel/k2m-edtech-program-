"""
Challenge Command Handler
Story 4.4 + Task 3.2 implementation: /challenge agent (The Challenger)

Students use /challenge to stress-test assumptions (Habit 4: Think First).
Available from Week 4 onwards (Decision 11).
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import discord

from cis_controller.llm_integration import call_agent_with_context
from cis_controller.rate_limiter import rate_limiter
from cis_controller.safety_filter import (
    ComparisonViolationError,
    post_to_discord_safe,
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
    """Check if student has pending share decision."""
    _evict_expired_pending_shares()
    return str(discord_id) in PENDING_SHOWCASE_SHARES


def _evict_expired_pending_shares() -> None:
    """Remove expired pending share records."""
    now = datetime.now(timezone.utc)
    expired = [
        discord_id
        for discord_id, payload in PENDING_SHOWCASE_SHARES.items()
        if now - payload.get("created_at", now) > PENDING_SHARE_TTL
    ]
    for discord_id in expired:
        PENDING_SHOWCASE_SHARES.pop(discord_id, None)


def _normalize_share_choice(raw_text: str) -> Optional[str]:
    """Normalize user's share decision to standard value."""
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
    """Iterate through potential guilds for channel resolution."""
    guild = getattr(message, "guild", None)
    if guild is not None:
        yield guild

    author = getattr(message, "author", None)
    for candidate in getattr(author, "mutual_guilds", []) or []:
        yield candidate


def _filter_guild(guild) -> bool:
    """Filter guild by configured ID if set."""
    if not DISCORD_GUILD_ID:
        return True
    return str(getattr(guild, "id", "")) == DISCORD_GUILD_ID


def _find_channel_by_id_or_slug(guild, configured_id: str, slug: str):
    """Find Discord channel by ID or name slug."""
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
    """Find #thinking-showcase channel across guilds."""
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
    """Find #facilitator-dashboard channel across guilds."""
    for guild in _iter_candidate_guilds(message):
        if not _filter_guild(guild):
            continue
        channel = _find_channel_by_id_or_slug(
            guild, CHANNEL_FACILITATOR_DASHBOARD, "facilitator-dashboard"
        )
        if channel:
            return channel
    return None


def _resolve_bot_client(message: discord.Message):
    """Best-effort bot resolver for safe public posting."""
    state = getattr(message, "_state", None)
    get_client = getattr(state, "_get_client", None)
    if callable(get_client):
        try:
            return get_client()
        except Exception:
            return None
    return None


def _register_pending_share(discord_id: str, user_message: str, student_context):
    """Register a pending share decision with context."""
    snippet = " ".join(user_message.split())
    if len(snippet) > 180:
        snippet = f"{snippet[:177]}..."

    PENDING_SHOWCASE_SHARES[str(discord_id)] = {
        "created_at": datetime.now(timezone.utc),
        "snippet": snippet,
        "week": getattr(student_context, "current_week", None),
        "zone": getattr(student_context, "zone", None),
        "agent": "challenge",
        "habits": ["PAUSE", "CONTEXT", "THINK FIRST"],
    }


async def _try_add_showcase_reaction(showcase_channel) -> None:
    """Best effort: add a star reaction to the latest showcase post."""
    try:
        posted_message = getattr(showcase_channel, "last_message", None)
        if callable(posted_message):
            posted_message = posted_message()
        if asyncio.iscoroutine(posted_message):
            posted_message = await posted_message
        if posted_message and hasattr(posted_message, "add_reaction"):
            await posted_message.add_reaction("\N{WHITE MEDIUM STAR}")
    except Exception:
        logger.debug("Could not add star reaction on showcase message.", exc_info=True)


def _record_showcase_publication(discord_id: str, decision: str, payload: Dict, post_text: str) -> None:
    visibility = "anonymous" if decision == "anonymous" else "public"
    try:
        store.create_showcase_publication(
            discord_id=str(discord_id),
            publication_type="habit_practice",
            visibility_level=visibility,
            celebration_message=post_text,
            habits_demonstrated=payload.get("habits", ["PAUSE", "CONTEXT", "THINK FIRST"]),
            nodes_mastered=[],
            parent_email_included=False,
        )
    except Exception as exc:
        logger.error("Failed to record showcase publication for %s: %s", discord_id, exc)


def _build_showcase_post(author: discord.abc.User, decision: str, payload: Dict) -> str:
    """Build showcase celebration post from share decision."""
    week = payload.get("week")
    zone = payload.get("zone")
    context = []
    if week is not None:
        context.append(f"Week {week}")
    if zone:
        context.append(zone.replace("_", " ").title())
    context_text = f" ({', '.join(context)})" if context else ""

    if decision == "anonymous":
        lead = "**A student** shared a thinking milestone from #thinking-lab"
    else:
        lead = (
            f"**{author.display_name}** shared a thinking milestone from "
            "#thinking-lab"
        )

    return (
        f"{lead}{context_text}.\n"
        "Challenged assumptions in a private session.\n"
        "Practiced habits: Pause + Context + Think First.\n"
        "Process stayed private. Celebration only."
    )


async def _notify_budget_alerts(message: discord.Message, budget_state: Dict[str, float]):
    """Post budget alerts to facilitator dashboard if triggered."""
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
            "ðŸ’° **Daily Budget Alert**\n"
            f"Current daily spend: ${budget_state.get('daily_total', 0.0):.2f} "
            f"(threshold: ${rate_limiter.DAILY_BUDGET_ALERT:.2f})"
        )

    if budget_state.get("weekly_alert_triggered") or budget_state.get(
        "weekly_cap_exceeded"
    ):
        lines.append(
            "ðŸš¨ **Weekly Budget Cap Reached**\n"
            f"Current weekly spend: ${budget_state.get('weekly_total', 0.0):.2f} "
            f"(cap: ${rate_limiter.WEEKLY_BUDGET_CAP:.2f})"
        )

    if lines:
        await dashboard_channel.send("\n\n".join(lines))


async def handle_showcase_share_response(message: discord.Message) -> bool:
    """
    Handle Yes/No/Anonymous decision after /challenge showcase prompt.
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

    # Keep DM details private in the published post, but still enforce
    # finished-work requirements against the underlying private snippet.
    try:
        safety_filter.validate_showcase_content(payload.get("snippet", ""))
    except ComparisonViolationError:
        PENDING_SHOWCASE_SHARES.pop(discord_id, None)
        await message.reply(
            "I kept this private for now. #thinking-showcase only accepts finished work."
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
        await post_to_discord_safe(
            bot=_resolve_bot_client(message),
            channel=showcase_channel,
            message_text=post_text,
            student_discord_id=message.author.id,
            is_showcase=True,
        )
    except ComparisonViolationError:
        PENDING_SHOWCASE_SHARES.pop(discord_id, None)
        await message.reply(
            "I kept this private for now. #thinking-showcase only accepts finished work."
        )
        return True
    except Exception as exc:
        logger.error("Failed to publish showcase post for %s: %s", discord_id, exc)
        PENDING_SHOWCASE_SHARES.pop(discord_id, None)
        await message.reply(
            "I couldn't publish to #thinking-showcase right now, so I kept this private."
        )
        return True

    await _try_add_showcase_reaction(showcase_channel)
    _record_showcase_publication(discord_id, decision, payload, post_text)
    PENDING_SHOWCASE_SHARES.pop(discord_id, None)
    await message.reply("Shared to #thinking-showcase. Nice work.")
    return True


async def handle_challenge(message: discord.Message, student):
    """
    Handle /challenge command end-to-end:
    command -> DM -> private conversation -> optional showcase share.
    """
    discord_id = str(message.author.id)

    allowed, error_message = rate_limiter.check_rate_limit(discord_id)
    if not allowed:
        await message.reply(error_message)
        logger.warning("Rate limit blocked /challenge for %s", discord_id)
        return

    try:
        dm_channel = await message.author.create_dm()
    except discord.Forbidden:
        await message.reply(
            "ðŸš« **Cannot start DM** - I need permission to send you private messages. "
            "Please enable DMs in your privacy settings, then try /challenge again."
        )
        return

    student_context = store.build_student_context(discord_id)
    if not student_context:
        await message.reply("âŒ Error loading your profile. Please try again.")
        logger.error("Failed to build StudentContext for %s", discord_id)
        return

    conversation_history = store.get_conversation_history(discord_id, "challenge", limit=10)
    user_message = message.content.replace("/challenge", "").strip()
    if not user_message:
        user_message = "I want to challenge my assumptions."

    try:
        logger.info("Calling Challenger agent for %s", discord_id)

        challenger_response, cost_data = await call_agent_with_context(
            agent="challenge",
            student_context=student_context,
            user_message=user_message,
            conversation_history=conversation_history,
        )

        budget_state = rate_limiter.track_interaction(
            discord_id=discord_id,
            agent="challenge",
            tokens=cost_data.get("total_tokens", 0),
            cost_usd=cost_data.get("total_cost_usd", 0.0),
        )
        await _notify_budget_alerts(message, budget_state)

        safety_filter.validate_no_comparison(challenger_response)

        store.save_conversation(
            discord_id=discord_id,
            agent="challenge",
            role="user",
            content=user_message,
        )
        store.save_conversation(
            discord_id=discord_id,
            agent="challenge",
            role="assistant",
            content=challenger_response,
        )

        store.update_habit_practice(discord_id, habit_id=4)

        refreshed_student = store.get_student(discord_id)
        celebration = celebrate_habit(refreshed_student, habit_id=4)
        full_response = (
            f"{challenger_response}\n\n{celebration}" if celebration else challenger_response
        )
        await dm_channel.send(full_response)

        current_state = student_context.current_state
        transition_state(current_state, "challenge", student=student, store=store)

        store.log_observability_event(
            discord_id,
            "agent_used",
            {
                "agent": "challenge",
                "week": student_context.current_week,
                "zone": student_context.zone,
                "cost_usd": cost_data.get("total_cost_usd", 0.0),
            },
        )

        preference = store.get_publication_preference(discord_id)
        if preference == "always_no":
            await dm_channel.send(
                "Kept private based on your showcase preference (`always_no`)."
            )
            return
        if preference == "week8_only" and getattr(student_context, "current_week", 0) < 8:
            await dm_channel.send(
                "Saved privately for Week 8 based on your showcase preference (`week8_only`)."
            )
            return
        if preference == "always_yes":
            payload = {
                "week": getattr(student_context, "current_week", None),
                "zone": getattr(student_context, "zone", None),
                "agent": "challenge",
                "habits": ["PAUSE", "CONTEXT", "THINK FIRST"],
            }
            showcase_channel = _find_showcase_channel(message)
            if showcase_channel is None:
                await dm_channel.send(
                    "I couldn't find #thinking-showcase right now, so I kept this private."
                )
                return

            post_text = _build_showcase_post(message.author, "yes", payload)
            try:
                await post_to_discord_safe(
                    bot=_resolve_bot_client(message),
                    channel=showcase_channel,
                    message_text=post_text,
                    student_discord_id=message.author.id,
                    is_showcase=True,
                )
                await _try_add_showcase_reaction(showcase_channel)
                _record_showcase_publication(discord_id, "yes", payload, post_text)
                await dm_channel.send(
                    "Shared to #thinking-showcase automatically (preference: `always_yes`)."
                )
            except Exception as exc:
                logger.error(
                    "Failed auto-publish showcase post for %s: %s",
                    discord_id,
                    exc,
                )
                await dm_channel.send(
                    "I couldn't publish to #thinking-showcase right now, so I kept this private."
                )
            return

        _register_pending_share(discord_id, user_message, student_context)
        await dm_channel.send(
            "\n---\n"
            "ðŸ’¡ **Want to share this to #thinking-showcase?**\n\n"
            "Choose one:\n"
            "- **Yes** (share with your name)\n"
            "- **Anonymous** (share without your name)\n"
            "- **No** (keep private)\n\n"
            "Reply with: **Yes / No / Anonymous / Maybe later**"
        )

        logger.info(
            "Handled /challenge for %s | Tokens: %s | Cost: $%.4f",
            discord_id,
            cost_data.get("total_tokens", 0),
            cost_data.get("total_cost_usd", 0.0),
        )

    except Exception as exc:
        logger.error("Error in handle_challenge for %s: %s", discord_id, exc)
        await dm_channel.send(
            "**ðŸ§  The Challenger is taking a short break.**\n\n"
            "Try this on your own:\n"
            "1. **IDENTIFY**: What are you assuming is true?\n"
            "2. **QUESTION**: What if the opposite were true?\n"
            "3. **EXAMINE**: Is this actually true, or just familiar?\n\n"
            f"Your assumption: _{user_message}_\n\n"
            "**You're practicing Habit 4 (ðŸ§  THINK FIRST) - question assumptions before deciding!**\n\n"
            "Try /challenge again in a moment."
        )

