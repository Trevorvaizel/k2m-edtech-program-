"""
Celebration Message Generator (Task 3.5)
Generates celebration messages for #thinking-showcase using Claude API

Implements Story 5.3 celebration message templates with:
- Guardrail #3 compliance (no comparison)
- Revolutionary Hope brand voice
- JTBD-relevant examples
"""

import os
import anthropic
import logging
from typing import List

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

HABIT_NAMES = {
    1: "PAUSE",
    2: "CONTEXT",
    3: "ITERATE",
    4: "THINK FIRST"
}

HABIT_ICONS = {
    1: "⏸️",
    2: "🎯",
    3: "🔄",
    4: "🧠"
}

CELEBRATION_SYSTEM_PROMPT = """
You are a celebration bot for K2M AI Thinking Skills Cohort.
Generate celebration messages for students who practiced thinking habits.

**STRICT RULES (NEVER VIOLATE):**

1. **NEVER use comparison language:**
   - Forbidden: "best", "top", "better than", "most", "least", "ranking", "leaderboard", "faster", "slower", "ahead", "behind"

2. **ALWAYS use Revolutionary Hope tone:**
   - Empowerment, celebration, no pressure
   - Focus on identity growth: "becoming someone who thinks clearly"
   - NOT fear-based: NOT "get left behind", "don't miss out"

3. **ONLY use JTBD-relevant examples:**
   - University choices, career clarity, study pressure, future planning
   - NO cat poems, silly scenarios, trivial puzzles

4. **Focus on identity shifts:**
   - "becoming someone who thinks clearly"
   - "building habits"
   - NOT "you're smart" or "you're good at this"

5. **Keep to 3-5 sentences** (habit practice celebrations)

6. **Use Habit icons:** ⏸️🎯🔄🧠

7. **Celebrate DIVERSE paths:**
   - Different students practice differently (no 'ideal' path)
   - Short practice (2 min) is valid. Long practice (20 min) is valid.

**OUTPUT TEMPLATE (Habit Practice):**

🌟 [Student/Anonymous] practiced Habit [X] & [Y] today!

[1 specific example of what they did - concrete, JTBD-relevant]
[1 sentence about identity shift observed]

That's thinking WITH AI, not copying FROM it.
Tools change. Habits transfer. [Habit icons]

**FEW-SHOT EXAMPLES:**

*Example 1 (Habit 1 & 2 - University):*
🌟 [Student] practiced Habits 1 & 2 today!

They paused to clarify what they want (⏸️ PAUSE).
They explained their situation first (🎯 CONTEXT).
Instead of "help me with AI", they asked:
"I'm a high school student confused about engineering or medicine. Can you help me think through this?"

That's thinking WITH AI. Skills that follow you forever. ⏸️🎯

*Example 2 (Habit 1 only - Study pressure):*
🌟 [Student] practiced Habit 1 today!

They stopped when they felt confused about an assignment.
Instead of rushing to AI, they asked: "What do I actually need help with?"

They're becoming someone who pauses before asking.
That's clarity first, answers second. ⏸️

*Example 3 (Habit 3 - Career exploration):*
🌟 [Student] practiced Habit 3 (🔄 ITERATE) today!

They explored 8 different career possibilities using /diverge.
They changed one thing at a time: "What if I tried healthcare? What about tech?"

They're building Node 3.1: "I have opinions about quality".
Skills that follow you forever. 🔄

**ANTI-PATTERNS (NEVER GENERATE THESE):**
❌ "Best artifact this week!" (comparison)
❌ "You're ahead of the cohort!" (ranking)
❌ "Most active student!" (competition)
❌ "You should practice more!" (pressure)
❌ "Here's a cat who learned to pause" (non-JTBD example)
❌ "Solve this riddle about AI" (trivial content)
"""


async def generate_celebration_message(
    student_id: str,
    agent_used: str,
    visibility: str,
    habits_practiced: List[int],
    zone: str,
    week: int
) -> str:
    """
    Generate a celebration message using Claude API.

    Args:
        student_id: Student's Discord ID (for display name if public)
        agent_used: Which CIS agent was used
        visibility: 'public', 'anonymous', or 'private'
        habits_practiced: List of habit IDs practiced
        zone: Student's current zone
        week: Current week number

    Returns:
        Celebration message text
    """
    # Determine student display
    if visibility == 'anonymous':
        student_display = "Anonymous student"
    else:
        # In real implementation, fetch student's actual name from Discord
        student_display = "[Student]"

    # Build habit icons list
    habit_icons = " ".join([HABIT_ICONS.get(h, '') for h in habits_practiced])
    habit_names = " & ".join([HABIT_NAMES.get(h, '') for h in sorted(set(habits_practiced))])

    # Create context-specific prompt
    user_prompt = f"""
Generate a celebration message for a student who just practiced with /{agent_used}.

**Student:** {student_display}
**Habits practiced:** {habit_names}
**Zone:** {zone}
**Week:** {week}

**Context:**
- This is a {visibility} publication
- The student just completed a CIS conversation
- Focus on identity growth and habit building
- Use the template from the system prompt

**Generate the celebration message now:**"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=300,
            temperature=0.7,
            system=CELEBRATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )

        celebration_text = response.content[0].text.strip()

        logger.info(f"Generated celebration for {student_id}: {celebration_text[:50]}...")

        return celebration_text

    except Exception as e:
        logger.error(f"Error generating celebration: {e}")

        # Fallback template if Claude API fails
        fallback = f"""🌟 {student_display} practiced {habit_names} today!

They're becoming someone who thinks clearly with AI.
That's thinking WITH AI, not copying FROM it.
Tools change. Habits transfer. {habit_icons}"""

        return fallback


def generate_artifact_celebration(
    student_id: str,
    visibility: str,
    artifact_data: dict
) -> str:
    """
    Generate celebration message for completed artifact.

    Args:
        student_id: Student's Discord ID
        visibility: 'public', 'anonymous', or 'private'
        artifact_data: Dictionary with artifact sections

    Returns:
        Artifact celebration message
    """
    if visibility == 'anonymous':
        student_display = "Anonymous student"
    else:
        student_display = "[Student]"

    # Extract artifact content
    question = artifact_data.get('section_1_question', '')
    reframed = artifact_data.get('section_2_reframed', '')
    explored = artifact_data.get('section_3_explored', '')
    challenged = artifact_data.get('section_4_challenged', '')
    concluded = artifact_data.get('section_5_concluded', '')
    learned = artifact_data.get('section_6_reflection', '')

    celebration = f"""🌟 {student_display} completed their Thinking Artifact!

They wrestled with: {question[:50]}...
They reframed it: {reframed[:50]}...
They explored: {explored[:50]}...
They challenged: {challenged[:50]}...
They concluded: {concluded[:50]}...
They learned: {learned[:50]}...

They're becoming someone who thinks clearly with AI!
Tools change. Habits transfer forever. ⏸️🎯🔄🧠"""

    return celebration


def generate_graduation_celebration(
    student_id: str,
    visibility: str
) -> str:
    """
    Generate Week 8 graduation celebration message.

    Args:
        student_id: Student's Discord ID
        visibility: 'public', 'anonymous', or 'private'

    Returns:
        Graduation celebration message
    """
    if visibility == 'anonymous':
        student_display = "Anonymous student"
    else:
        student_display = "[Student]"

    celebration = f"""🎓 {student_display} earned the 4 Habits Card!

⏸️ PAUSE - They know what they want
🎯 CONTEXT - They explain their situation
🔄 ITERATE - They change one thing at a time
🧠 THINK FIRST - They decide with AI

Their artifact proves: "I am someone who thinks WITH AI!"

Tools change. These 4 habits transfer forever.

You're ready for university. You're ready for life. 🌟"""

    return celebration
