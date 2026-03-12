"""
Task 7.12 helpers: #welcome-lounge waiting-room UX.

Implements:
- channel resolution and permission hardening
- pinned status message + week-1 preview seeding
- nightly status refresh helper
- guest FAQ responses + facilitator escalation forwarding
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from typing import Any, List, Optional, Tuple

import pytz

logger = logging.getLogger(__name__)

EAT = pytz.timezone("Africa/Nairobi")

WELCOME_LOUNGE_SLUG = "welcome-lounge"
STATUS_MARKER = "[WELCOME_LOUNGE_STATUS]"


def _normalize_slug(name: str) -> str:
    return re.sub(r"^[^a-zA-Z0-9]+", "", name or "").lower()


def _is_matching_channel_name(name: str) -> bool:
    normalized = _normalize_slug(name)
    return normalized == WELCOME_LOUNGE_SLUG or normalized.endswith(WELCOME_LOUNGE_SLUG)


def is_welcome_lounge_channel(channel: Any) -> bool:
    """
    True when channel is configured welcome lounge by ID or slug.
    """
    configured_id = os.getenv("CHANNEL_WELCOME_LOUNGE", "").strip()
    if configured_id and str(getattr(channel, "id", "")) == configured_id:
        return True
    return _is_matching_channel_name(getattr(channel, "name", ""))


def _get_role(guild: Any, role_name: str) -> Optional[Any]:
    for role in getattr(guild, "roles", []):
        if str(getattr(role, "name", "")).lower() == role_name.lower():
            return role
    return None


async def _set_permissions_safe(channel: Any, target: Any, **permissions: Any) -> None:
    if target is None:
        return
    try:
        await channel.set_permissions(target, **permissions)
    except Exception as exc:
        logger.warning(
            "welcome-lounge: failed setting permissions on %s for %s: %s",
            getattr(channel, "name", "<unknown>"),
            getattr(target, "name", "<unknown>"),
            exc,
        )


def resolve_welcome_lounge_channel(guild: Any) -> Optional[Any]:
    """
    Resolve #welcome-lounge channel from env ID, then fallback to slug matching.
    """
    configured_id = os.getenv("CHANNEL_WELCOME_LOUNGE", "").strip()
    if configured_id and configured_id.isdigit():
        configured_channel = guild.get_channel(int(configured_id))
        if configured_channel is not None and hasattr(configured_channel, "send"):
            return configured_channel

    for channel in getattr(guild, "text_channels", []):
        if _is_matching_channel_name(getattr(channel, "name", "")):
            return channel
    return None


def _confirmed_student_count(store: Any) -> int:
    if store is None:
        return 0
    getter = getattr(store, "get_confirmed_student_count", None)
    if callable(getter):
        try:
            return max(int(getter()), 0)
        except Exception as exc:
            logger.warning("welcome-lounge: confirmed count lookup failed: %s", exc)
    return 0


def _build_status_message(confirmed_count: int) -> str:
    timestamp = datetime.now(EAT).strftime("%Y-%m-%d %H:%M EAT")
    return (
        f"{STATUS_MARKER}\n"
        "Your payment is being verified - usually within 24 hours. While you wait, this is your active lounge.\n\n"
        "You can ask KIRA anything about the next steps, Discord, or payment status.\n"
        f"Confirmed students so far: **{confirmed_count}**\n"
        f"Last updated: {timestamp}\n\n"
        "If your payment has been pending longer than 24 hours, ask here and KIRA will escalate to @Facilitator."
    )


def _preview_marker(day_name: str) -> str:
    return f"[WELCOME_LOUNGE_PREVIEW_W1_{day_name}]"


def _truncate_text(text: str, max_chars: int = 260) -> str:
    compact = " ".join((text or "").split()).strip()
    if len(compact) <= max_chars:
        return compact
    return f"{compact[: max_chars - 3]}..."


def _default_preview_posts() -> List[Tuple[str, str]]:
    return [
        (
            _preview_marker("MONDAY"),
            "Week 1 preview: notice where AI already shows up in your daily life.",
        ),
        (
            _preview_marker("TUESDAY"),
            "Week 1 preview: map how people like you use AI for practical decisions.",
        ),
        (
            _preview_marker("WEDNESDAY"),
            "Week 1 preview: try one tiny AI-assisted step on a real school or career question.",
        ),
    ]


def _week1_preview_posts() -> List[Tuple[str, str]]:
    """
    Build 3 week-1 previews from the canonical daily prompt library.
    Falls back to static text if prompt parsing fails.
    """
    try:
        from scheduler.daily_prompts import DailyPromptLibrary, WeekDay

        library = DailyPromptLibrary()
        preview_days = [WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY]
        posts: List[Tuple[str, str]] = []
        for idx, day in enumerate(preview_days, start=1):
            prompt = library.get_prompt(week=1, day=day)
            if prompt is None:
                continue
            task_line = prompt.task.splitlines()[0] if prompt.task else prompt.context
            body = (
                f"Preview {idx}/3 - Week 1 {day.name.title()}: {prompt.title}\n"
                f"{_truncate_text(task_line)}\n"
                f"Habit focus: {_truncate_text(prompt.habit_practice, max_chars=180)}"
            )
            posts.append((_preview_marker(day.name), body))
        return posts or _default_preview_posts()
    except Exception as exc:
        logger.warning("welcome-lounge: could not load prompt previews: %s", exc)
        return _default_preview_posts()


async def _collect_recent_channel_text(channel: Any, limit: int = 200) -> List[str]:
    messages: List[str] = []
    try:
        async for item in channel.history(limit=limit):
            text = getattr(item, "content", "")
            if text:
                messages.append(text)
    except Exception as exc:
        logger.warning("welcome-lounge: history read failed: %s", exc)
    return messages


async def ensure_welcome_lounge_permissions(guild: Any, channel: Any) -> None:
    """
    Enforce Task 7.12 permission model:
    - @Guest can read+post
    - @Student cannot post
    """
    guest_role = _get_role(guild, "Guest")
    student_role = _get_role(guild, "Student")
    facilitator_role = _get_role(guild, "Facilitator")
    trevor_role = _get_role(guild, "Trevor")
    bot_role = _get_role(guild, "CIS Bot")

    await _set_permissions_safe(
        channel,
        getattr(guild, "default_role", None),
        read_messages=False,
        send_messages=False,
        read_message_history=False,
    )
    await _set_permissions_safe(
        channel,
        guest_role,
        read_messages=True,
        send_messages=True,
        read_message_history=True,
    )
    await _set_permissions_safe(
        channel,
        student_role,
        read_messages=True,
        send_messages=False,
        read_message_history=True,
    )
    await _set_permissions_safe(
        channel,
        facilitator_role,
        read_messages=True,
        send_messages=True,
        read_message_history=True,
        manage_messages=True,
    )
    await _set_permissions_safe(
        channel,
        trevor_role,
        read_messages=True,
        send_messages=True,
        read_message_history=True,
        manage_messages=True,
    )
    await _set_permissions_safe(
        channel,
        bot_role,
        read_messages=True,
        send_messages=True,
        read_message_history=True,
        manage_messages=True,
    )

    # Defense-in-depth boundary hardening:
    # keep @Guest confined to #welcome-lounge even if role/category drift exists.
    if guest_role is not None:
        lounge_channel_id = str(getattr(channel, "id", ""))

        for other in getattr(guild, "channels", []):
            if str(getattr(other, "id", "")) == lounge_channel_id:
                continue
            # Category-level overwrites handled separately below.
            if str(getattr(other, "type", "")) == "4":
                continue
            await _set_permissions_safe(
                other,
                guest_role,
                read_messages=False,
                send_messages=False,
                read_message_history=False,
            )

        for category in getattr(guild, "categories", []):
            channels_in_category = getattr(category, "channels", [])
            includes_lounge = any(
                str(getattr(item, "id", "")) == lounge_channel_id
                for item in channels_in_category
            )
            if includes_lounge:
                continue
            await _set_permissions_safe(
                category,
                guest_role,
                read_messages=False,
                send_messages=False,
                read_message_history=False,
            )


async def _upsert_status_pin(channel: Any, status_text: str) -> bool:
    """
    Ensure the status pin exists and reflects current confirmed count.
    Returns True when changed.
    """
    try:
        for pinned in await channel.pins():
            content = getattr(pinned, "content", "")
            if STATUS_MARKER in content:
                if content != status_text:
                    await pinned.edit(content=status_text)
                    return True
                return False
    except Exception as exc:
        logger.warning("welcome-lounge: pin inspection failed: %s", exc)

    try:
        status_message = await channel.send(status_text)
        await status_message.pin(reason="Task 7.12 waiting-room status pin")
        return True
    except Exception as exc:
        logger.warning("welcome-lounge: failed creating status pin: %s", exc)
        return False


async def upsert_welcome_lounge_content(
    *,
    bot: Any,
    store: Any,
    guild_id: Optional[int] = None,
    include_previews: bool = True,
) -> dict:
    """
    Ensure welcome-lounge status pin + previews exist.
    """
    guild = bot.get_guild(int(guild_id)) if guild_id else None
    if guild is None:
        guilds = getattr(bot, "guilds", [])
        guild = guilds[0] if guilds else None
    if guild is None:
        return {"ok": False, "reason": "guild_not_found"}

    channel = resolve_welcome_lounge_channel(guild)
    if channel is None:
        return {"ok": False, "reason": "channel_not_found"}

    await ensure_welcome_lounge_permissions(guild, channel)

    confirmed_count = _confirmed_student_count(store)
    status_changed = await _upsert_status_pin(channel, _build_status_message(confirmed_count))

    preview_posts_created = 0
    if include_previews:
        existing_text = await _collect_recent_channel_text(channel)
        for marker, preview_text in _week1_preview_posts():
            if any(marker in text for text in existing_text):
                continue
            try:
                await channel.send(f"{marker}\n{preview_text}")
                preview_posts_created += 1
            except Exception as exc:
                logger.warning("welcome-lounge: failed posting preview %s: %s", marker, exc)

    return {
        "ok": True,
        "channel_id": getattr(channel, "id", None),
        "confirmed_count": confirmed_count,
        "status_changed": status_changed,
        "preview_posts_created": preview_posts_created,
    }


async def refresh_welcome_lounge_status(
    *,
    bot: Any,
    store: Any,
    guild_id: Optional[int] = None,
) -> dict:
    """
    Nightly count refresh helper (Task 7.12 requirement #4).
    """
    return await upsert_welcome_lounge_content(
        bot=bot,
        store=store,
        guild_id=guild_id,
        include_previews=False,
    )


def _looks_like_question(content: str) -> bool:
    text = (content or "").strip().lower()
    if not text:
        return False
    if "?" in text:
        return True
    starts = ("how", "what", "when", "where", "why", "can", "do", "is", "help")
    return text.startswith(starts)


def classify_guest_question(content: str) -> Tuple[str, bool]:
    """
    Return (reply_text, needs_escalation).
    """
    text = " ".join((content or "").lower().split())
    if not text:
        return ("", False)

    if any(k in text for k in ("how long", "when", "verify", "verification", "confirm", "pending", "wait")):
        return (
            "Payment verification usually completes within 24 hours. "
            "If you are already past that window, I will escalate this to @Facilitator.",
            "24" in text or "long" in text or "past" in text,
        )

    if any(k in text for k in ("mpesa", "m-pesa", "transaction", "code", "submit")):
        return (
            "If you already paid, submit your M-Pesa code using your secure payment-submit link from email/DM. "
            "After submission, KIRA confirms receipt and Trevor verifies.",
            False,
        )

    if any(k in text for k in ("locked", "can't access", "cant access", "unlock", "channel")):
        return (
            "Locked channels are expected while your role is @Guest. "
            "Once payment is verified, @Student unlocks your full program channels.",
            False,
        )

    if any(k in text for k in ("scam", "fraud", "stuck", "urgent", "problem", "error")):
        return (
            "I hear you. I am escalating this to @Facilitator now so a human can follow up quickly.",
            True,
        )

    if _looks_like_question(text):
        return (
            "Good question. I have forwarded this to @Facilitator so you get a precise human follow-up.",
            True,
        )

    return ("", False)


async def _forward_to_dashboard(bot: Any, message: Any, reason: str) -> bool:
    channel_id = os.getenv("CHANNEL_FACILITATOR_DASHBOARD", "").strip() or os.getenv(
        "FACILITATOR_DASHBOARD_CHANNEL_ID",
        "",
    ).strip()
    if not channel_id or not channel_id.isdigit():
        return False

    dashboard_channel = bot.get_channel(int(channel_id))
    if dashboard_channel is None:
        try:
            dashboard_channel = await bot.fetch_channel(int(channel_id))
        except Exception:
            return False
    if dashboard_channel is None or not hasattr(dashboard_channel, "send"):
        return False

    author = getattr(message, "author", None)
    await dashboard_channel.send(
        "[welcome-lounge escalation]\n"
        f"reason: {reason}\n"
        f"user: {getattr(author, 'display_name', getattr(author, 'name', 'unknown'))} "
        f"(id={getattr(author, 'id', 'unknown')})\n"
        f"message: {getattr(message, 'content', '')[:900]}"
    )
    return True


async def handle_welcome_lounge_message(*, bot: Any, message: Any) -> bool:
    """
    Handle guest messages in #welcome-lounge with FAQ or escalation.
    Returns True when consumed.
    """
    channel = getattr(message, "channel", None)
    author = getattr(message, "author", None)
    if channel is None or author is None:
        return False
    if not is_welcome_lounge_channel(channel):
        return False
    if getattr(author, "bot", False):
        return False

    role_names = {
        str(getattr(role, "name", "")).lower()
        for role in getattr(author, "roles", [])
    }
    is_student = "student" in role_names
    is_guest = "guest" in role_names

    if is_student:
        if is_guest and hasattr(author, "remove_roles"):
            guest_role_obj = next(
                (
                    role
                    for role in getattr(author, "roles", [])
                    if str(getattr(role, "name", "")).lower() == "guest"
                ),
                None,
            )
            if guest_role_obj is not None:
                try:
                    await author.remove_roles(
                        guest_role_obj,
                        reason="Task 7.12: remove stale @Guest on @Student lounge message",
                    )
                except Exception as exc:
                    logger.warning(
                        "welcome-lounge: could not remove stale @Guest for student %s: %s",
                        getattr(author, "id", "unknown"),
                        exc,
                    )

        if hasattr(message, "reply"):
            await message.reply(
                "Your full access is unlocked now. Continue in #welcome-and-rules and your week channels.",
                mention_author=False,
            )
        else:
            await channel.send(
                "Your full access is unlocked now. Continue in #welcome-and-rules and your week channels."
            )
        return True

    reply_text, needs_escalation = classify_guest_question(getattr(message, "content", ""))
    if reply_text:
        if hasattr(message, "reply"):
            await message.reply(reply_text, mention_author=False)
        else:
            await channel.send(reply_text)

    if needs_escalation:
        await _forward_to_dashboard(bot, message, reason="guest_question")

    return bool(reply_text or needs_escalation or _looks_like_question(getattr(message, "content", "")))
