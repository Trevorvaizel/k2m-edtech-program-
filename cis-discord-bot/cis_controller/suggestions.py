"""
CIS Controller - Natural Language Suggestions
Story 4.7 Implementation: "Did you mean...?" system

When students use natural language instead of slash commands,
this module classifies intent and suggests the correct command.

GRADUATED INTENSITY SYSTEM (Story 4.1):
- Week 1-2: Explicit guidance ("Try /frame to clarify...")
- Week 4-5: Gentle nudges ("Have you considered...?")
- Week 6-7: Minimal prompts ("Ready to synthesize?")
- Week 8: None (students should drive)

Examples:
  "I need help figuring out my question"  -> "Did you mean /frame?"
  "I want to explore different options"   -> "Did you mean /diverge?"
  "I want to challenge my assumption"     -> "Did you mean /challenge?"
"""

import discord
from typing import Optional
from cis_controller.router import is_agent_unlocked, get_unlocked_agents
from database.store import StudentStateStore
import logging

logger = logging.getLogger(__name__)

store = StudentStateStore()

# Keyword hints for natural language classification
INTENT_KEYWORDS = {
    "frame": [
        "help", "clarify", "understand", "confused", "question", "what", "how",
        "figure out", "not sure", "unclear", "stuck", "don't know"
    ],
    "diverge": [
        "explore", "options", "possibilities", "alternatives", "different",
        "what if", "could be", "might work", "various", "multiple"
    ],
    "challenge": [
        "challenge", "assume", "assumption", "test", "doubt", "push back", "question",
        "really true", "why", "but what if", "critique", "taking for granted"
    ],
    "synthesize": [
        "conclude", "summary", "summarize", "wrap up", "wrap this up", "articulate", "final", "pull together",
        "bring together", "so what", "main point", "takeaway"
    ],
}

# Graduated suggestion templates (Story 4.1)
SUGGESTION_TEMPLATES = {
    "week_1_2": {
        "intensity": "explicit",
        "frame": "**🎯 Let's pause and frame this first!**\n\nTry: `/frame {question}`\n\nThis helps you clarify what you actually want to know.",
        "diverge": "**💡 Try exploring possibilities!**\n\nUse: `/diverge {topic}`\n\nWhat different angles could you explore?",
        "challenge": "**⚡ Ready to stress-test your thinking?**\n\nUse: `/challenge {assumption}`\n\nWhat might you be taking for granted?",
        "synthesize": "**✨ Ready to pull it all together?**\n\nUse: `/synthesize {insights}`\n\nWhat are your main conclusions?",
    },
    "week_4_5": {
        "intensity": "gentle",
        "frame": "**💭 Have you framed your question?**\n\n`/frame {your question}` helps you get clarity before diving in.",
        "diverge": "**🔍 Want to explore different options?**\n\n`/diverge {topic}` opens up new possibilities.",
        "challenge": "**🧠 Ready to challenge your assumptions?**\n\n`/challenge {assumption}` stress-tests your thinking.",
        "synthesize": "**✨ Ready to synthesize?**\n\n`/synthesize {insights}` helps you articulate your conclusions.",
    },
    "week_6_7": {
        "intensity": "minimal",
        "frame": "Try `/frame` to clarify your question.",
        "diverge": "`/diverge` can explore options.",
        "challenge": "`/challenge` stress-tests assumptions.",
        "synthesize": "`/synthesize` pulls it together.",
    },
    "week_8": {
        "intensity": "none",
        # Week 8: No suggestions - students should drive
    },
}


def classify_intent(message_text: str) -> Optional[str]:
    """
    Classify natural language message to the most likely CIS command.

    Uses keyword matching with scoring. Returns highest-scoring command.

    Args:
        message_text: Student's message content

    Returns:
        Suggested command name or None if no clear match
    """
    message_lower = message_text.lower()
    scores = {cmd: 0 for cmd in INTENT_KEYWORDS}

    # Score each command by keyword matches
    for cmd, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message_lower:
                # Longer phrase matches are usually more specific than short tokens.
                scores[cmd] += len(keyword)

    # Find best match
    best_score = max(scores.values())
    if best_score == 0:
        return None

    tied = [cmd for cmd, score in scores.items() if score == best_score]
    if len(tied) == 1:
        return tied[0]

    # If frame ties with a more specific non-frame intent, prefer non-frame.
    if "frame" in tied:
        non_frame = [cmd for cmd in tied if cmd != "frame"]
        if non_frame:
            return non_frame[0]

    return tied[0]


async def suggest_explicit_command(message: discord.Message, student) -> None:
    """
    Classify natural language and suggest correct slash command.

    Uses graduated intensity based on current week (Story 4.1).

    Args:
        message: Discord message
        student: Student database row
    """
    # Classify intent
    message_text = message.content
    suggested_command = classify_intent(message_text)

    if not suggested_command:
        # No clear intent detected - ignore
        return

    current_week = student['current_week']

    # Check if suggested agent is unlocked
    if not is_agent_unlocked(suggested_command, current_week):
        # Don't suggest locked agents
        return

    # Get template based on week intensity
    template = get_suggestion_template(current_week, suggested_command)

    if template is None:
        # Week 8: No suggestions
        return

    # Send suggestion
    await message.reply(template)

    # Log suggestion for observability
    discord_id = str(message.author.id)
    store.log_observability_event(
        discord_id,
        "suggestion_shown",
        {
            "suggested_command": suggested_command,
            "week": current_week,
            "original_message": message_text[:100]
        }
    )


def get_suggestion_template(week: int, command: str) -> Optional[str]:
    """
    Get suggestion template based on week and command.

    Implements graduated intensity (Story 4.1):
    - Week 1-2: Explicit
    - Week 4-5: Gentle
    - Week 6-7: Minimal
    - Week 8: None

    Args:
        week: Current cohort week
        command: Suggested command name

    Returns:
        Suggestion template string or None (Week 8)
    """
    if week == 8:
        return None  # Week 8: No suggestions

    # Determine intensity level
    if week <= 2:
        level = "week_1_2"
    elif week <= 5:
        level = "week_4_5"
    else:  # week 6-7
        level = "week_6_7"

    templates = SUGGESTION_TEMPLATES.get(level, {})
    return templates.get(command)
