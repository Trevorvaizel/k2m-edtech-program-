"""
CIS Controller - Router Module
Story 4.7 Implementation: CIS Controller routing logic

This module handles:
- Intent Recognition (Layer 1)
- State Machine (Layer 2)
- Agent Router (Layer 3)

NOTE: Full implementation will be completed in Task 1.3
This is a stub for Task 1.1 scaffold completion.
"""

import discord
from discord.ext import commands
from database.store import StudentStateStore

# Initialize state store
store = StudentStateStore()


async def route_student_interaction(message: discord.Message):
    """
    Main routing function for all student interactions.

    LAYER 1: INTENT RECOGNITION

    NOTE: Full implementation in Task 1.3
    """
    # Get or create student
    student = store.get_student(message.author.id)
    if not student:
        student = store.create_student(message.author.id)

    # For now, just log the interaction
    print(f"Interaction from {message.author.id}: {message.content[:50]}...")


def setup_bot_events(bot: commands.Bot):
    """
    Attach routing to Discord bot events

    NOTE: Full implementation in Task 1.3
    """
    @bot.event
    async def on_message(message: discord.Message):
        # Ignore bot's own messages
        if message.author.bot:
            return

        # Only process DMs or messages in designated channels
        if isinstance(message.channel, discord.DMChannel) or \
           message.channel.name in ['thinking-lab', 'bot-testing']:
            await route_student_interaction(message)
