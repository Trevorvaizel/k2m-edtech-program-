"""
Share to Showcase Command (Task 3.5)
Decision 12 implementation: Private DM → Public showcase publication flow

After CIS conversation, bot asks if student wants to share their learning to #thinking-showcase.
Options: Yes (public), Anonymous, No (private)
"""

import discord
from discord.ext import commands
from database.store import StudentStateStore
from cis_controller.celebration_generator import generate_celebration_message
from cis_controller.safety_filter import SafetyFilter, ComparisonViolationError
import logging
import asyncio

logger = logging.getLogger(__name__)
store = StudentStateStore()
safety_filter = SafetyFilter()

# Habit icons for celebration messages
HABIT_ICONS = {
    1: "⏸️",  # Pause
    2: "🎯",   # Context
    3: "🔄",   # Iterate
    4: "🧠"    # Think First
}


async def prompt_share_to_showcase(
    bot: commands.Bot,
    message: discord.Message,
    student_discord_id: str,
    agent_used: str,
    habits_practiced: list = None
):
    """
    Prompt student to share their CIS conversation to #thinking-showcase.

    Called after CIS agent conversation completes.

    Args:
        bot: Discord bot instance
        message: Original message that triggered the agent
        student_discord_id: Student's Discord user ID
        agent_used: Which CIS agent they just used (frame, diverge, challenge, synthesize)
        habits_practiced: List of habit IDs practiced (1-4)
    """
    # Check student's publication preference
    preference = store.get_publication_preference(student_discord_id)

    # Auto-share based on preference (reduce decision fatigue)
    if preference == 'always_no':
        # Student opted out - save conversation only, no prompt
        logger.info(f"Student {student_discord_id} has 'always_no' preference - skipping share prompt")
        return

    elif preference == 'always_yes':
        # Auto-publish as public
        await publish_to_showcase(
            bot=bot,
            student_discord_id=student_discord_id,
            agent_used=agent_used,
            visibility='public',
            habits_practiced=habits_practiced
        )
        return

    elif preference == 'week8_only':
        # Save for Week 8 artifact only
        await message.reply(
            "**Saved for your Week 8 artifact!** ✨\n\n"
            "Your conversation is saved. You'll share it during Week 8 when creating your graduation artifact.\n\n"
            f"**Habit practiced:** {' '.join([HABIT_ICONS.get(h, '') for h in (habits_practiced or [1, 2])])}"
        )
        return

    # Default: always_ask - show the share prompt
    share_prompt = (
        f"**Want to share your learning to #thinking-showcase?** 🌟\n\n"
        f"You just practiced with **/{agent_used}**. Celebrate your growth!\n\n"
        f"**Choose your privacy level:**\n"
        f"**[1] Public** - Your name is shown (recommended for social proof)\n"
        f"**[2] Anonymous** - Shared without your name (psychological safety)\n"
        f"**[3] Not now** - Keep this conversation private (saved for artifact later)\n\n"
        f"**Tip:** You can set a permanent preference with `/showcase-preference`"
    )

    share_message = await message.reply(share_prompt)

    # Wait for user response (using reaction buttons for simplicity)
    await share_message.add_reaction("1️⃣")  # Public
    await share_message.add_reaction("2️⃣")  # Anonymous
    await share_message.add_reaction("3️⃣")  # Not now

    def check_reaction(reaction, user):
        return (
            user.id == int(student_discord_id) and
            reaction.message.id == share_message.id and
            str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣"]
        )

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check_reaction)

        if str(reaction.emoji) == "1️⃣":
            # Public share
            await publish_to_showcase(
                bot=bot,
                student_discord_id=student_discord_id,
                agent_used=agent_used,
                visibility='public',
                habits_practiced=habits_practiced,
                original_message=message
            )

        elif str(reaction.emoji) == "2️⃣":
            # Anonymous share
            await publish_to_showcase(
                bot=bot,
                student_discord_id=student_discord_id,
                agent_used=agent_used,
                visibility='anonymous',
                habits_practiced=habits_practiced,
                original_message=message
            )

        elif str(reaction.emoji) == "3️⃣":
            # Not now - save privately
            await message.reply(
                "**Conversation saved privately.** 🔒\n\n"
                "Your learning is saved for your Week 8 artifact. You can share anytime with `/share-showcase`.\n\n"
                f"**Habit practiced:** {' '.join([HABIT_ICONS.get(h, '') for h in (habits_practiced or [1, 2])])}"
            )

        # Clean up reactions
        await share_message.clear_reactions()

    except asyncio.TimeoutError:
        await share_message.clear_reactions()
        logger.info(f"Share prompt timeout for student {student_discord_id}")


async def publish_to_showcase(
    bot: commands.Bot,
    student_discord_id: str,
    agent_used: str,
    visibility: str,
    habits_practiced: list = None,
    original_message: discord.Message = None
):
    """
    Publish a celebration message to #thinking-showcase.

    Args:
        bot: Discord bot instance
        student_discord_id: Student's Discord user ID
        agent_used: Which CIS agent was used
        visibility: 'public', 'anonymous', or 'private'
        habits_practiced: List of habit IDs practiced
        original_message: Original message (for reply)
    """
    try:
        # Get student data
        student = store.get_student(student_discord_id)
        if not student:
            logger.error(f"Student {student_discord_id} not found")
            return

        # Get #thinking-showcase channel
        guild = bot.guilds[0] if bot.guilds else None
        if not guild:
            logger.error("Bot not in any guild")
            return

        showcase_channel = discord.utils.get(guild.channels, name="thinking-showcase")
        if not showcase_channel:
            logger.error("#thinking-showcase channel not found")
            return

        # Generate celebration message using Claude API
        celebration = await generate_celebration_message(
            student_id=student_discord_id,
            agent_used=agent_used,
            visibility=visibility,
            habits_practiced=habits_practiced or [1, 2],
            zone=student['zone'],
            week=student['current_week']
        )

        # Validate with SafetyFilter (Guardrail #3)
        try:
            safety_filter.validate_no_comparison(celebration)
        except ComparisonViolationError as e:
            logger.error(f"SafetyFilter blocked celebration: {e}")
            if original_message:
                await original_message.reply(
                    "**Your celebration is being reviewed.** ⏳\n\n"
                    "It will be posted shortly. In the meantime, your growth is saved!"
                )
            return

        # Post to #thinking-showcase
        await showcase_channel.send(celebration)

        # Add ⭐ reaction (models celebration behavior)
        message = await showcase_channel.last_message()
        if message:
            await message.add_reaction("⭐")

        # Record publication in database
        store.create_showcase_publication(
            discord_id=student_discord_id,
            publication_type='habit_practice',
            visibility_level=visibility,
            celebration_message=celebration,
            habits_demonstrated=[HABIT_ICONS.get(h, '') for h in (habits_practiced or [1, 2])],
            nodes_mastered=[],  # TODO: Calculate from student data
            parent_email_included=False  # TODO: Implement parent email system
        )

        # DM confirmation to student
        if original_message:
            if visibility == 'public':
                confirm_msg = f"**Posted to #thinking-showcase!** 🌟\n\n{celebration[:100]}..."
            elif visibility == 'anonymous':
                confirm_msg = "**Posted anonymously to #thinking-showcase!** 🌟\n\nYour identity is protected. Your growth inspires others!"
            else:
                confirm_msg = "**Saved for your artifact!** 🔒"

            await original_message.reply(confirm_msg)

        logger.info(f"Published {agent_used} practice for {student_discord_id} as {visibility}")

    except Exception as e:
        logger.error(f"Error publishing to showcase: {e}")
        if original_message:
            await original_message.reply(
                "**Something went wrong.** 😕\n\n"
                "Your growth is saved! Try sharing later with `/share-showcase`"
            )


async def set_showcase_preference(message: discord.Message, preference: str):
    """
    Set student's permanent showcase publication preference.

    Args:
        message: Discord message
        preference: 'always_ask', 'always_yes', 'always_no', 'week8_only'
    """
    valid_preferences = ['always_ask', 'always_yes', 'always_no', 'week8_only']

    if preference not in valid_preferences:
        await message.reply(
            f"**Invalid preference.**\n\n"
            f"Valid options: {', '.join(valid_preferences)}\n\n"
            f"**always_ask** - Ask me every time (default)\n"
            f"**always_yes** - Auto-publish all my celebrations\n"
            f"**always_no** - Never publish (private only)\n"
            f"**week8_only** - Only publish during Week 8 artifact"
        )
        return

    store.set_publication_preference(message.author.id, preference)

    preference_desc = {
        'always_ask': "I'll ask you every time you complete a CIS conversation",
        'always_yes': "All your celebrations will be auto-published publicly",
        'always_no': "Your conversations will stay private (saved for artifact only)",
        'week8_only': "Your celebrations will be saved for Week 8 artifact publication"
    }

    await message.reply(
        f"**Showcase preference updated!** ✅\n\n"
        f"**Setting:** {preference}\n"
        f"**What this means:** {preference_desc[preference]}\n\n"
        f"You can change this anytime with `/showcase-preference [preference]`"
    )

    logger.info(f"Student {message.author.id} set showcase preference to {preference}")
