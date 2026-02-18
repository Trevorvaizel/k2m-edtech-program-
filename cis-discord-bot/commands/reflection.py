"""
Reflection Submission Command (Task 2.5)

Handles student Friday reflection submissions and week unlock gating.
"""

import logging
import re
from discord import Interaction
from discord.app_commands import command, describe
from discord.ext import commands

from database.store import StudentStateStore

logger = logging.getLogger(__name__)


class ReflectionCog(commands.Cog):
    """Reflection submission command."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.store = StudentStateStore()

    @command(name="submit-reflection", description="Submit your Friday reflection to unlock next week")
    @describe(habit_practice="Did you practice Habit 1? (Yes/Sometimes/No)", identity_shift="What changed this week?", proof_of_work="One sentence showing AI understood you")
    async def submit_reflection(
        self,
        interaction: Interaction,
        habit_practice: str,
        identity_shift: str,
        proof_of_work: str
    ):
        """
        Submit Friday reflection for week unlock gating.

        Format:
        1. Habit practice: Yes/Sometimes/No
        2. What changed: Student's reflection
        3. Proof-of-work: One sentence

        Args:
            interaction: Discord interaction
            habit_practice: Habit 1 practice self-assessment
            identity_shift: Student's reflection on what changed
            proof_of_work: Proof sentence
        """
        await interaction.response.defer()  # Defer since database operations may take time

        try:
            # Get student's current week
            discord_id = str(interaction.user.id)
            student = self.store.get_student(discord_id)

            if not student:
                await interaction.followup.send(
                    "❌ You're not registered in the cohort yet. Try using any CIS command first (/frame)."
                )
                return

            current_week = student['current_week']

            # Week 8 doesn't have reflections (graduation week)
            if current_week > 7:
                await interaction.followup.send(
                    f"🎉 You've reached Week 8! No reflections needed - work on your artifact instead."
                )
                return

            # Check if reflection already submitted
            existing = self.store.get_weekly_reflection(discord_id, current_week)
            if existing and existing['submitted']:
                await interaction.followup.send(
                    f"✅ You've already submitted your Week {current_week} reflection!\n\n"
                    f"Your next week unlocks on Saturday at 12 PM EAT."
                )
                return

            # Validate habit_practice format
            habit_practice = habit_practice.strip().lower()
            if habit_practice not in ['yes', 'sometimes', 'no']:
                await interaction.followup.send(
                    "❌ Habit practice must be one of: **Yes**, **Sometimes**, or **No**\n\n"
                    f"Try again: `/submit-reflection habit-practice:Yes identity-shift:Your answer proof-of-work:Your sentence`"
                )
                return

            # Create reflection record if needed
            if not existing:
                existing = self.store.create_weekly_reflection_record(discord_id, current_week)

            # Submit reflection
            reflection_content = f"Habit Practice: {habit_practice}\nIdentity Shift: {identity_shift}"
            self.store.submit_weekly_reflection(
                discord_id=discord_id,
                week_number=current_week,
                reflection_content=reflection_content,
                proof_of_work=proof_of_work
            )

            # Success message
            await interaction.followup.send(
                f"✅ **Reflection Submitted!**\n\n"
                f"**Habit Practice:** {habit_practice.capitalize()}\n"
                f"**Identity Shift:** {identity_shift[:100]}{'...' if len(identity_shift) > 100 else ''}\n\n"
                f"Week {current_week + 1} unlocks on Saturday at 12 PM EAT.\n\n"
                f"You'll get a notification when it's ready! 🚀"
            )

            logger.info(f"{interaction.user.name} submitted Week {current_week} reflection")

        except Exception as e:
            logger.error(f"Error submitting reflection: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ There was an error submitting your reflection. Please try again or contact Trevor."
            )


async def setup(bot: commands.Bot):
    """Register the reflection cog."""
    await bot.add_cog(ReflectionCog(bot))
    logger.info("Reflection command registered")
