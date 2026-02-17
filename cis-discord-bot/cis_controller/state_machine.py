"""
CIS Controller - State Machine
Story 4.7 Implementation: Student state management

Manages student state transitions through the CIS interaction lifecycle.

States (non-linear progression):
- none: Initial state
- framing: Using /frame agent
- exploring: Using /diverge agent
- challenging: Using /challenge agent
- synthesizing: Using /synthesize agent
- complete: Finished all CIS interactions

Key Features:
- Non-linear transitions: Students can revisit any agent
- Habit milestone detection: Celebrate practice at 3, 7, 14 times
- State persistence: Track progress in database
"""

from typing import Optional
from database.store import StudentStateStore
import logging

logger = logging.getLogger(__name__)

# State constants
STATE_NONE = 'none'
STATE_FRAMING = 'framing'
STATE_EXPLORING = 'exploring'
STATE_CHALLENGING = 'challenging'
STATE_SYNTHESIZING = 'synthesizing'
STATE_COMPLETE = 'complete'

VALID_STATES = {
    STATE_NONE, STATE_FRAMING, STATE_EXPLORING,
    STATE_CHALLENGING, STATE_SYNTHESIZING, STATE_COMPLETE
}

# Habit names and icons per spec (Story 1.4)
HABIT_NAMES = {
    1: ("PAUSE", "⏸️"),
    2: ("CONTEXT", "🎯"),
    3: ("ITERATE", "🔄"),
    4: ("THINK FIRST", "🧠"),
}

# Command → State mapping
COMMAND_STATES = {
    'frame': STATE_FRAMING,
    'diverge': STATE_EXPLORING,
    'challenge': STATE_CHALLENGING,
    'synthesize': STATE_SYNTHESIZING,
}

# Habit milestone thresholds (Story 4.7: celebrate practice)
MILESTONES = [3, 7, 14, 21, 30]

# Initialize store
store = StudentStateStore()


def celebrate_habit(student, habit_id: int) -> Optional[str]:
    """
    Generate celebration message if student hit a practice milestone.

    Args:
        student: Student database row (or None)
        habit_id: Habit ID (1-4)

    Returns:
        Celebration message string if milestone hit, None otherwise

    Milestones celebrate habit practice:
    - 3 times: "You're building momentum!"
    - 7 times: "This is becoming a habit!"
    - 14 times: "You're demonstrating consistency!"
    - 21 times: "Habit strength: STRONG!"
    - 30 times: "Habit mastery level!"
    """
    if habit_id not in HABIT_NAMES:
        return None

    if student is None:
        return None

    discord_id = str(student['discord_id'])

    # Get habit practice data
    habit_data = store.get_habit_journey(discord_id)
    habit_row = None
    for row in habit_data:
        if row['habit_id'] == habit_id:
            habit_row = row
            break

    if not habit_row:
        return None

    practice_count = habit_row['practiced_count']

    # Check if this practice hits a milestone
    if practice_count in MILESTONES:
        habit_name, habit_icon = HABIT_NAMES[habit_id]

        # Milestone messages (Guardrail #4: confidence over competence)
        milestone_messages = {
            3: f"**{habit_icon} Habit Practice #3!**\n\nYou're building momentum with {habit_name}! Keep practicing.",
            7: f"**{habit_icon} Habit Practice #7!**\n\nThis is becoming a habit! {habit_name} is feeling more natural.",
            14: f"**{habit_icon} Habit Practice #14!**\n\nYou're demonstrating consistency! {habit_name} is part of your thinking process now.",
            21: f"**{habit_icon} Habit Practice #21!**\n\nHabit strength: **STRONG!** You've practiced {habit_name} 21 times!",
            30: f"**{habit_icon} Habit Practice #30!**\n\nHabit mastery level! You've integrated {habit_name} into your thinking.",
        }

        message = milestone_messages.get(practice_count)

        # Log milestone for observability
        store.log_observability_event(
            discord_id,
            "milestone_reached",
            {"habit_id": habit_id, "practice_count": practice_count}
        )

        return message

    return None


def get_student_state(student) -> str:
    """
    Get current state from student record.

    Args:
        student: Student database row (or None)

    Returns:
        Current state string, STATE_NONE if student is None
    """
    if student is None:
        return STATE_NONE

    if isinstance(student, dict):
        return student.get('current_state') or STATE_NONE

    try:
        return student['current_state'] or STATE_NONE
    except (TypeError, KeyError, IndexError):
        return getattr(student, 'current_state', STATE_NONE) or STATE_NONE


def transition_state(
    current_state: str,
    command: str,
    student=None,
    store: Optional[StudentStateStore] = None,
) -> str:
    """
    Determine next state based on current state and command.

    NON-LINEAR TRANSITIONS: Students can revisit any agent.
    - No lock-in: Can go from challenge back to frame
    - State is a bookmark, not a prison
    - Respects messy, real thinking processes

    Args:
        current_state: Student's current interaction state
        command: Command being executed (frame, diverge, challenge, synthesize)
        student: Student database row (optional)
        store: Database store for persistence (optional)

    Returns:
        New state string
    """
    current_state = current_state or STATE_NONE
    new_state = COMMAND_STATES.get(command, current_state)
    db_store = store or globals().get("store")

    # Persist state to database
    if student is not None and db_store is not None:
        try:
            discord_id = str(student['discord_id'])
            db_store.conn.execute(
                "UPDATE students SET current_state = ? WHERE discord_id = ?",
                (new_state, discord_id)
            )
            db_store.conn.commit()

            logger.info(f"Student {discord_id}: {current_state} → {new_state} (/{command})")
        except Exception as e:
            logger.warning(f"Failed to persist state transition for /{command}: {e}")

    return new_state


def is_valid_state(state: str) -> bool:
    """Check if state string is a valid CIS state."""
    return state in VALID_STATES


def get_unlocked_agents(current_week: int) -> list:
    """
    Get list of unlocked agents for given week.

    Used by router for temporal awareness checks.

    Args:
        current_week: Current cohort week (1-8)

    Returns:
        List of agent names available this week
    """
    from cis_controller.router import AGENTS_BY_WEEK
    return AGENTS_BY_WEEK.get(current_week, ["frame"])
