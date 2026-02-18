"""
Reflection submission flow (Task 2.5).

Handles Friday reflection submissions and week unlock gating.
"""

import logging

from discord import Interaction
from discord.app_commands import command, describe
from discord.ext import commands

from database.store import StudentStateStore

logger = logging.getLogger(__name__)


def habit_focus_label_for_week(week: int) -> str:
    """Return the week-specific habit label."""
    if week == 1:
        return "Habit 1 (Pause)"
    if week in (2, 3):
        return "Habit 2 (Context)"
    if week in (4, 5):
        return "Habit 3 (Iterate)"
    if week in (6, 7):
        return "Habit 4 (Think First)"
    return "This week's habit"


async def submit_reflection_handler(
    interaction: Interaction,
    store: StudentStateStore,
    habit_practice: str,
    identity_shift: str,
    proof_of_work: str,
) -> None:
    """Shared reflection submission implementation used by slash command wiring."""
    await interaction.response.defer()

    try:
        discord_id = str(interaction.user.id)
        student = store.get_student(discord_id)
        if not student:
            await interaction.followup.send(
                "You are not registered in the cohort yet. Use /frame first."
            )
            return

        current_week = student["current_week"]
        if current_week > 7:
            await interaction.followup.send(
                "You have reached Week 8. No reflection required now; continue artifact work."
            )
            return

        existing = store.get_weekly_reflection(discord_id, current_week)
        if existing and existing["submitted"]:
            await interaction.followup.send(
                f"You already submitted Week {current_week} reflection. "
                "Next unlock runs Saturday 12 PM EAT."
            )
            return

        normalized_habit = habit_practice.strip().lower()
        if normalized_habit not in {"yes", "sometimes", "no"}:
            await interaction.followup.send(
                "Habit practice must be one of: Yes, Sometimes, No."
            )
            return

        identity_shift = identity_shift.strip()
        proof_of_work = proof_of_work.strip()
        if not identity_shift:
            await interaction.followup.send("Identity shift cannot be empty.")
            return
        if not proof_of_work:
            await interaction.followup.send(
                "Proof-of-work is required. Paste one sentence showing AI understood your situation."
            )
            return

        if not existing:
            store.create_weekly_reflection_record(discord_id, current_week)

        reflection_content = (
            f"Habit Focus: {habit_focus_label_for_week(current_week)}\n"
            f"Habit Practice: {normalized_habit}\n"
            f"Identity Shift: {identity_shift}"
        )
        store.submit_weekly_reflection(
            discord_id=discord_id,
            week_number=current_week,
            reflection_content=reflection_content,
            proof_of_work=proof_of_work,
        )

        await interaction.followup.send(
            f"Reflection submitted for Week {current_week}.\n"
            f"Habit focus tracked: {habit_focus_label_for_week(current_week)}.\n"
            f"Week {current_week + 1} unlocks on Saturday at 12 PM EAT."
        )
        logger.info("%s submitted Week %s reflection", interaction.user.name, current_week)
    except Exception as exc:
        logger.error("Error submitting reflection: %s", exc, exc_info=True)
        await interaction.followup.send(
            "There was an error submitting your reflection. Please retry or contact Trevor."
        )


class ReflectionCog(commands.Cog):
    """Reflection submission command."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.store = StudentStateStore()

    @command(name="submit-reflection", description="Submit Friday reflection to unlock next week")
    @describe(
        habit_practice="Did you practice this week's habit? (Yes/Sometimes/No)",
        identity_shift="What changed this week?",
        proof_of_work="One sentence showing AI understood you",
    )
    async def submit_reflection(
        self,
        interaction: Interaction,
        habit_practice: str,
        identity_shift: str,
        proof_of_work: str,
    ) -> None:
        await submit_reflection_handler(
            interaction=interaction,
            store=self.store,
            habit_practice=habit_practice,
            identity_shift=identity_shift,
            proof_of_work=proof_of_work,
        )


async def setup(bot: commands.Bot):
    """Register the reflection cog."""
    await bot.add_cog(ReflectionCog(bot))
    logger.info("Reflection command registered")
