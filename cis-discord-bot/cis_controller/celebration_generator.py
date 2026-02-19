"""
Celebration Message Generator (Task 3.5)

Provider-swappable implementation:
- Uses the active provider configured in cis_controller.llm_integration
- Never hard-requires anthropic at import time
- Falls back to deterministic templates on provider/network failure
"""

import logging
from typing import Dict, List, Tuple

from cis_controller.llm_integration import (
    _call_anthropic,
    _call_openai_compatible,
    get_active_model,
    get_active_provider,
)

logger = logging.getLogger(__name__)

HABIT_NAMES: Dict[int, str] = {
    1: "PAUSE",
    2: "CONTEXT",
    3: "ITERATE",
    4: "THINK FIRST",
}

HABIT_ICONS: Dict[int, str] = {
    1: "⏸️",
    2: "🎯",
    3: "🔄",
    4: "🧠",
}

CELEBRATION_SYSTEM_PROMPT = """
You are a celebration bot for K2M AI Thinking Skills Cohort.
Generate celebration messages for students who practiced thinking habits.

STRICT RULES (NEVER VIOLATE):
1. Never use comparison language:
   best, top, better than, most, least, ranking, leaderboard,
   faster, slower, ahead, behind.
2. Always use revolutionary hope tone: empowering, specific, no pressure.
3. Use JTBD-relevant context only: university choices, study pressure, career clarity.
4. Focus on identity shifts and habits, not talent labels.
5. Keep habit celebrations to 3-5 sentences.
6. Include relevant habit icons.

Output format (habit practice):
🌟 [Student/Anonymous student] practiced [habit names] today!
[specific behavior]
[identity-growth line]
Tools change. Habits transfer. [icons]
"""


def _format_habits(habits_practiced: List[int]) -> Tuple[str, str]:
    unique_habits = sorted(set(habits_practiced or []))
    names = [HABIT_NAMES[h] for h in unique_habits if h in HABIT_NAMES]
    icons = [HABIT_ICONS[h] for h in unique_habits if h in HABIT_ICONS]
    habit_names = " + ".join(names) if names else "thinking habits"
    habit_icons = " ".join(icons) if icons else ""
    return habit_names, habit_icons


def _student_display_for_visibility(visibility: str) -> str:
    return "Anonymous student" if visibility == "anonymous" else "[Student]"


def _fallback_celebration(
    visibility: str,
    habits_practiced: List[int],
    zone: str,
    week: int,
) -> str:
    student_display = _student_display_for_visibility(visibility)
    habit_names, habit_icons = _format_habits(habits_practiced)
    zone_label = (zone or "zone_0").replace("_", " ").title()
    return (
        f"\N{GLOWING STAR} {student_display} practiced {habit_names} today!\n\n"
        f"They completed a focused thinking session in Week {week} ({zone_label}).\n"
        "They are becoming someone who thinks clearly with AI.\n"
        f"Tools change. Habits transfer. {habit_icons}".strip()
    )


async def _call_celebration_llm(user_prompt: str) -> str:
    provider = get_active_provider()
    model = get_active_model(provider)
    messages = [{"role": "user", "content": user_prompt}]

    if provider == "anthropic":
        response_text, _ = await _call_anthropic(
            agent="celebration",
            model=model,
            system_prompt=CELEBRATION_SYSTEM_PROMPT,
            messages=messages,
        )
        return response_text

    if provider in {"openai", "zhipu", "openai-compatible"}:
        response_text, _ = await _call_openai_compatible(
            provider=provider,
            agent="celebration",
            model=model,
            system_prompt=CELEBRATION_SYSTEM_PROMPT,
            messages=messages,
        )
        return response_text

    raise ValueError(f"Unsupported AI_PROVIDER for celebration generation: {provider}")


async def generate_celebration_message(
    student_id: str,
    agent_used: str,
    visibility: str,
    habits_practiced: List[int],
    zone: str,
    week: int,
) -> str:
    """
    Generate a showcase celebration message using the active provider.
    """
    student_display = _student_display_for_visibility(visibility)
    habit_names, _ = _format_habits(habits_practiced)
    week_number = int(week or 0)
    zone_value = zone or "zone_0"

    user_prompt = (
        f"Student: {student_display}\n"
        f"Agent used: /{agent_used}\n"
        f"Habits practiced: {habit_names}\n"
        f"Week: {week_number}\n"
        f"Zone: {zone_value}\n"
        f"Visibility: {visibility}\n\n"
        "Write one celebration post now."
    )

    try:
        generated = (await _call_celebration_llm(user_prompt)).strip()
        if generated:
            logger.info(
                "Generated celebration for %s via provider %s",
                student_id,
                get_active_provider(),
            )
            return generated
    except Exception as exc:
        logger.error("Celebration generation failed for %s: %s", student_id, exc)

    return _fallback_celebration(
        visibility=visibility,
        habits_practiced=habits_practiced,
        zone=zone_value,
        week=week_number,
    )


def generate_artifact_celebration(
    student_id: str,
    visibility: str,
    artifact_data: dict,
) -> str:
    """
    Generate celebration message for completed artifact.
    """
    student_display = _student_display_for_visibility(visibility)

    question = artifact_data.get("section_1_question", "")
    reframed = artifact_data.get("section_2_reframed", "")
    explored = artifact_data.get("section_3_explored", "")
    challenged = artifact_data.get("section_4_challenged", "")
    concluded = artifact_data.get("section_5_concluded", "")
    learned = artifact_data.get("section_6_reflection", "")

    return (
        f"\N{GLOWING STAR} {student_display} completed their Thinking Artifact!\n\n"
        f"They wrestled with: {question[:50]}...\n"
        f"They reframed it: {reframed[:50]}...\n"
        f"They explored: {explored[:50]}...\n"
        f"They challenged: {challenged[:50]}...\n"
        f"They concluded: {concluded[:50]}...\n"
        f"They learned: {learned[:50]}...\n\n"
        "They are becoming someone who thinks clearly with AI.\n"
        "Tools change. Habits transfer forever. "
        "⏸️ 🎯 🔄 🧠"
    )


def generate_graduation_celebration(
    student_id: str,
    visibility: str,
) -> str:
    """
    Generate Week 8 graduation celebration message.
    """
    student_display = _student_display_for_visibility(visibility)

    return (
        f"\N{GRADUATION CAP} {student_display} earned the 4 Habits Card!\n\n"
        "⏸️ PAUSE - They know what they want\n"
        "🎯 CONTEXT - They explain their situation\n"
        "🔄 ITERATE - "
        "They change one thing at a time\n"
        "🧠 THINK FIRST - They decide with AI\n\n"
        'Their artifact proves: "I am someone who thinks WITH AI!"\n\n'
        "Tools change. These 4 habits transfer forever.\n\n"
        "You're ready for university. You're ready for life. "
        "\N{GLOWING STAR}"
    )
