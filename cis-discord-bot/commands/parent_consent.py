"""
Parent consent management (Task 4.6).

Handles student parent email consent preferences.
"""

import logging

from discord import Interaction
from discord.app_commands import command, describe
from discord.ext import commands

from database.store import StudentStateStore

logger = logging.getLogger(__name__)


async def set_parent_consent_handler(
    interaction: Interaction,
    store: StudentStateStore,
    parent_email: str,
    consent_preference: str,
) -> None:
    """Shared parent consent implementation used by slash command wiring."""
    await interaction.response.defer()

    try:
        discord_id = str(interaction.user.id)
        student = store.get_student(discord_id)
        if not student:
            await interaction.followup.send(
                "You are not registered in the cohort yet. Use /frame first."
            )
            return

        # Validate email format (basic validation)
        if '@' not in parent_email or '.' not in parent_email.split('@')[1]:
            await interaction.followup.send(
                "Invalid email format. Please provide a valid email address."
            )
            return

        # Validate consent preference
        if consent_preference not in ('share_weekly', 'privacy_first'):
            await interaction.followup.send(
                "Invalid preference. Choose: Share weekly updates OR Privacy first (until Week 8)."
            )
            return

        # Set parent consent
        store.set_parent_consent(
            discord_id=discord_id,
            parent_email=parent_email,
            consent_preference=consent_preference,
        )

        if consent_preference == 'share_weekly':
            message = (
                f"Parent consent saved!\n\n"
                f"Email: {parent_email}\n"
                f"Preference: Weekly updates enabled\n\n"
                f"Your parents will receive weekly emails every Monday showing:\n"
                f"- Which habits you practiced\n"
                f"- How many conversations you had\n"
                f"- Reflection highlights (no private DM content shared)\n\n"
                f"You can change this anytime with /update-parent-consent"
            )
        else:  # privacy_first
            message = (
                f"Parent consent saved!\n\n"
                f"Email: {parent_email}\n"
                f"Preference: Privacy first\n\n"
                f"Your parents will NOT receive weekly updates.\n"
                f"They will only receive an email in Week 8 when your artifact is ready.\n\n"
                f"You can change this anytime with /update-parent-consent"
            )

        await interaction.followup.send(message)
        logger.info(
            "%s set parent consent to %s for %s",
            interaction.user.name,
            consent_preference,
            parent_email,
        )

    except Exception as exc:
        logger.error("Error setting parent consent: %s", exc, exc_info=True)
        await interaction.followup.send(
            "There was an error saving your parent consent. Please retry or contact Trevor."
        )


async def update_parent_consent_handler(
    interaction: Interaction,
    store: StudentStateStore,
    consent_preference: str,
) -> None:
    """Update existing parent consent preference."""
    await interaction.response.defer()

    try:
        discord_id = str(interaction.user.id)
        existing = store.get_parent_consent(discord_id)

        if not existing:
            await interaction.followup.send(
                "You have not set up parent consent yet. Use /parent-consent with email first."
            )
            return

        # Validate consent preference
        if consent_preference not in ('share_weekly', 'privacy_first'):
            await interaction.followup.send(
                "Invalid preference. Choose: share_weekly OR privacy_first."
            )
            return

        # Update consent preference
        store.update_parent_consent(
            discord_id=discord_id,
            consent_preference=consent_preference,
        )

        if consent_preference == 'share_weekly':
            message = (
                f"Parent consent updated!\n\n"
                f"Preference: Weekly updates enabled\n\n"
                f"Your parents will receive weekly emails every Monday.\n"
                f"Previous preference was: {existing['consent_preference']}"
            )
        else:  # privacy_first
            message = (
                f"Parent consent updated!\n\n"
                f"Preference: Privacy first\n\n"
                f"Your parents will not receive weekly updates.\n"
                f"They will only receive an email in Week 8 if enabled.\n"
                f"Previous preference was: {existing['consent_preference']}"
            )

        await interaction.followup.send(message)
        logger.info(
            "%s updated parent consent to %s",
            interaction.user.name,
            consent_preference,
        )

    except Exception as exc:
        logger.error("Error updating parent consent: %s", exc, exc_info=True)
        await interaction.followup.send(
            "There was an error updating your parent consent. Please retry or contact Trevor."
        )


async def view_parent_consent_handler(
    interaction: Interaction,
    store: StudentStateStore,
) -> None:
    """View current parent consent settings."""
    await interaction.response.defer()

    try:
        discord_id = str(interaction.user.id)
        existing = store.get_parent_consent(discord_id)

        if not existing:
            message = (
                "You have not set up parent consent yet.\n\n"
                "Use /parent-consent to:\n"
                "- Add your parent email\n"
                "- Choose weekly updates OR privacy first\n\n"
                "This controls whether parents receive progress emails."
            )
        else:
            # Mask email for privacy
            email_parts = existing['parent_email'].split('@')
            masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}"

            preference_desc = {
                'share_weekly': 'Weekly updates enabled (every Monday)',
                'privacy_first': 'Privacy first (no updates until Week 8)',
            }

            message = (
                f"Your current parent consent settings:\n\n"
                f"Email: {masked_email}\n"
                f"Preference: {preference_desc.get(existing['consent_preference'], 'Unknown')}\n"
                f"Parent opted out: {'Yes' if existing['parent_opted_out'] else 'No'}\n\n"
                f"Set on: {existing['consent_date'][:10]}\n\n"
                f"Use /update-parent-consent to change these settings."
            )

        await interaction.followup.send(message)

    except Exception as exc:
        logger.error("Error viewing parent consent: %s", exc, exc_info=True)
        await interaction.followup.send(
            "There was an error retrieving your parent consent. Please retry or contact Trevor."
        )


class ParentConsentCog(commands.Cog):
    """Parent consent management commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.store = StudentStateStore()

    @command(name="parent-consent", description="Set parent email consent preferences")
    @describe(
        parent_email="Parent email address",
        consent_preference="Share weekly updates OR Privacy first (until Week 8)",
    )
    async def parent_consent(
        self,
        interaction: Interaction,
        parent_email: str,
        consent_preference: str,
    ) -> None:
        await set_parent_consent_handler(
            interaction=interaction,
            store=self.store,
            parent_email=parent_email,
            consent_preference=consent_preference,
        )

    @command(name="update-parent-consent", description="Update parent email consent preference")
    @describe(
        consent_preference="Share weekly updates OR Privacy first (until Week 8)",
    )
    async def update_parent_consent(
        self,
        interaction: Interaction,
        consent_preference: str,
    ) -> None:
        await update_parent_consent_handler(
            interaction=interaction,
            store=self.store,
            consent_preference=consent_preference,
        )

    @command(name="view-parent-consent", description="View your current parent consent settings")
    async def view_parent_consent(
        self,
        interaction: Interaction,
    ) -> None:
        await view_parent_consent_handler(
            interaction=interaction,
            store=self.store,
        )


async def setup(bot: commands.Bot):
    """Register the parent consent cog."""
    await bot.add_cog(ParentConsentCog(bot))
    logger.info("Parent consent commands registered")
