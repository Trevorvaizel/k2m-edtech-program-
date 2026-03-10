"""
Onboarding helpers for Task 7.7.

Implements:
- Continue/skip intent detection with DM recipient safeguards
- Stop 0 profile parsing with non-blocking fallback defaults
- Shared onboarding message templates
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import discord

# Decision M-06 + GAP FIX #7: continue intent is restricted to explicit low-risk terms.
CONTINUE_SIGNALS = {
    "continue",
    "done",
    "ready",
    "next",
    "yes",
    "ok",
    "okay",
    "finished",
    "go",
}

SKIP_SIGNALS = {"skip", "later", "not now", "skip for now"}

DEFAULT_STOP0_PROFILE = {
    "primary_device_context": "mixed",
    "study_hours_per_week": 4,
    "confidence_level": 3,
    "family_obligations_hint": "none provided",
}

STOP0_QUESTIONS = [
    "How do you usually access the internet? Reply in your own words.",
    "How many hours per week can you dedicate? (Just a rough guess)",
    "On a scale of 1-5, how confident are you with tech tools? (1=nervous, 5=comfortable)",
    "Any times that are completely off-limits? (e.g., Sunday mornings, late evenings)",
]


def _normalize_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _is_private_channel(message: discord.Message) -> bool:
    channel = getattr(message, "channel", None)
    if channel is None:
        return False
    if isinstance(channel, discord.DMChannel):
        return True
    return getattr(channel, "type", None) == discord.ChannelType.private


def is_continue_signal(
    message: discord.Message,
    bot_user: Optional[discord.abc.User],
    expected_discord_id: Optional[str] = None,
) -> bool:
    """
    GAP FIX #7 three-layer guard + expected-student guard.
    """
    # GUARD 1: DM only
    if not _is_private_channel(message):
        return False

    # GUARD 2: Ignore all bot-authored messages
    if getattr(message.author, "bot", False):
        return False

    # GUARD 3: Ensure this DM thread belongs to THIS bot instance.
    # In discord.py, DMChannel.recipient is typically the student and
    # DMChannel.me is the current bot user.
    if bot_user is None:
        return False
    channel_me = getattr(message.channel, "me", None)
    if channel_me is not None:
        if str(getattr(channel_me, "id", "")) != str(getattr(bot_user, "id", "")):
            return False
    else:
        # Compatibility fallback for tests/mocks that omit `channel.me`.
        recipient = getattr(message.channel, "recipient", None)
        if recipient is None:
            return False
        if str(getattr(recipient, "id", "")) != str(getattr(bot_user, "id", "")):
            return False

    # Expected student guard for onboarding progression
    if expected_discord_id is not None:
        if str(getattr(message.author, "id", "")) != str(expected_discord_id):
            return False

    content = _normalize_text(getattr(message, "content", ""))
    if not content:
        return False

    if content in CONTINUE_SIGNALS:
        return True

    return bool(set(content.split()).intersection(CONTINUE_SIGNALS))


def is_skip_signal(content: str) -> bool:
    normalized = _normalize_text(content)
    if not normalized:
        return False
    if normalized in SKIP_SIGNALS:
        return True
    return bool(set(normalized.split()).intersection(SKIP_SIGNALS))


def _parse_device_context(raw: str) -> Optional[str]:
    text = _normalize_text(raw)
    if not text:
        return None
    if "mix" in text or "both" in text:
        return "mixed"
    if "phone" in text or "mobile" in text or "data" in text:
        return "phone data"
    if "home" in text and ("wifi" in text or "wi-fi" in text):
        return "home wifi"
    if (
        ("office" in text or "school" in text or "work" in text)
        and ("wifi" in text or "wi-fi" in text)
    ):
        return "office wifi"
    if "wifi" in text or "wi-fi" in text:
        return "mixed"
    return None


def _parse_hours_per_week(raw: str) -> Optional[int]:
    text = _normalize_text(raw)
    if not text:
        return None

    range_match = re.search(r"(\d{1,2})\s*[-to]+\s*(\d{1,2})", text)
    if range_match:
        a = int(range_match.group(1))
        b = int(range_match.group(2))
        return max(1, min(80, round((a + b) / 2)))

    num_match = re.search(r"\d{1,2}", text)
    if num_match:
        return max(1, min(80, int(num_match.group(0))))

    word_to_num = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "twelve": 12,
        "fifteen": 15,
        "twenty": 20,
    }
    for word, number in word_to_num.items():
        if word in text:
            return number
    return None


def _parse_confidence_level(raw: str) -> Optional[int]:
    text = _normalize_text(raw)
    if not text:
        return None

    digit_match = re.search(r"[1-5]", text)
    if digit_match:
        return int(digit_match.group(0))

    if any(token in text for token in ("nervous", "very low", "beginner")):
        return 1
    if any(token in text for token in ("low", "not confident", "struggle")):
        return 2
    if any(token in text for token in ("moderate", "okay", "average")):
        return 3
    if any(token in text for token in ("confident", "comfortable")):
        return 4
    if any(token in text for token in ("very confident", "expert", "advanced")):
        return 5
    return None


def parse_stop0_profile_answers(answers: List[str]) -> Tuple[Dict[str, object], List[Dict[str, str]]]:
    """
    Parse Stop 0 free-text answers into canonical fields.
    Parse failures are non-blocking and must be flagged for manual review.
    """
    padded_answers = list(answers or [])[:4]
    while len(padded_answers) < 4:
        padded_answers.append("")

    q1_raw, q2_raw, q3_raw, q4_raw = [str(item or "").strip() for item in padded_answers]

    parse_flags: List[Dict[str, str]] = []

    device_context = _parse_device_context(q1_raw)
    if device_context is None:
        device_context = DEFAULT_STOP0_PROFILE["primary_device_context"]
        parse_flags.append(
            {
                "question": "q1_primary_device_context",
                "raw_response": q1_raw,
                "reason": "device_context_unparsed",
            }
        )

    study_hours = _parse_hours_per_week(q2_raw)
    if study_hours is None:
        study_hours = int(DEFAULT_STOP0_PROFILE["study_hours_per_week"])
        parse_flags.append(
            {
                "question": "q2_study_hours_per_week",
                "raw_response": q2_raw,
                "reason": "study_hours_unparsed",
            }
        )

    confidence_level = _parse_confidence_level(q3_raw)
    if confidence_level is None:
        confidence_level = int(DEFAULT_STOP0_PROFILE["confidence_level"])
        parse_flags.append(
            {
                "question": "q3_confidence_level",
                "raw_response": q3_raw,
                "reason": "confidence_level_unparsed",
            }
        )

    family_hint = q4_raw or str(DEFAULT_STOP0_PROFILE["family_obligations_hint"])

    return (
        {
            "primary_device_context": device_context,
            "study_hours_per_week": study_hours,
            "confidence_level": confidence_level,
            "family_obligations_hint": family_hint,
        },
        parse_flags,
    )


def build_stop_message(stop: int) -> str:
    if stop == 1:
        return (
            "**Stop 1/4 - Welcome setup**\n"
            "Open #start-here and #thinking-lab so you can see where everything lives.\n"
            "Reply `continue` here when ready."
        )
    if stop == 2:
        return (
            "**Stop 2/4 - Channel orientation**\n"
            "Check #resources and #help so you know where to find updates and support.\n"
            "Reply `continue` when done."
        )
    if stop == 3:
        return (
            "**Stop 3/4 - First action**\n"
            "Post a short intro in #thinking-lab or run your first `/frame` prompt.\n"
            "Reply `continue` after you do it."
        )
    return (
        "Your setup status is active. Reply `/onboarding` if you want me to replay the flow."
    )


def build_stop0_intro() -> str:
    return (
        "**Stop 0 (optional profile, 2 minutes)**\n"
        "To support you better, I need four quick profile answers.\n"
        "You can type `skip` at any point and I will use defaults.\n\n"
        f"Q1. {STOP0_QUESTIONS[0]}"
    )


def build_stop0_question(index: int) -> str:
    safe_index = max(0, min(index, len(STOP0_QUESTIONS) - 1))
    return f"Q{safe_index + 1}. {STOP0_QUESTIONS[safe_index]}"


def build_reentry_dm(name: str) -> str:
    first_name = (name or "there").strip().split()[0]
    return (
        f"Hey {first_name}, your setup is still waiting! "
        "Reply continue to pick up where you left off."
    )
