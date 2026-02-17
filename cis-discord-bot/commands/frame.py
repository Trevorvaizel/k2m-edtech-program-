"""
Frame Command Handler
Story 4.7 Implementation: /frame command

This module handles the /frame Discord command.
Students use /frame to practice Habit 1 (Pause) and Habit 2 (Context).

NOTE: Full implementation in Task 1.4
This is a stub for Task 1.1 scaffold completion.
"""

import discord
from discord.ext import commands
from database.store import StudentStateStore

store = StudentStateStore()


async def handle_frame(message: discord.Message, student):
    """
    Handle /frame command.

    NOTE: Full implementation in Task 1.4 with Claude API integration

    For now (Task 1.1), just respond with a placeholder message.
    """
    response = """
**⏸️ The Framer** is coming soon!

You're practicing Habit 1 (Pause) - taking a moment to clarify what you actually want to know.

The Framer agent will be implemented in Task 1.4, where you'll be able to:
- Pause and clarify your questions before using AI
- Add context so AI responds to YOUR situation
- Practice Habit 2 (Context) scaffolding

For now, try typing `/status` to see bot information.
"""

    await message.reply(response)

    # Log interaction
    store.log_observability_event(
        message.author.id,
        "agent_used",
        {"agent": "frame", "week": student['current_week']}
    )
