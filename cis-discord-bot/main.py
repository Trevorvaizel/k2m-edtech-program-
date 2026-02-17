"""
K2M CIS Discord Bot - Main Entry Point
Story 4.7 Implementation: Discord Bot Technical Specification

This bot implements the complete CIS Agent System for Discord-based cohort facilitation.
Bot Name: KIRA (K2M Interactive Reasoning Agent)
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
COHORT_START_DATE = os.getenv('COHORT_START_DATE', '2026-02-01')

# Validate required environment variables
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required. Copy .env.template to .env and add your token.")

if not ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY not set. CIS agents will not work.")

# Discord bot configuration
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required for slash commands
intents.dm_messages = True  # Required for private DM interactions
intents.members = True  # Required for member tracking

bot = commands.Bot(
    command_prefix='/',  # Slash commands preferred
    intents=intents,
    help_command=None  # Custom help in #thinking-lab
)


@bot.event
async def on_ready():
    """Bot startup initialization"""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Serving {len(bot.guilds)} guilds')

    # Log server information
    for guild in bot.guilds:
        logger.info(f'Connected to: {guild.name} (ID: {guild.id})')

    # Initialize database (will be implemented in Task 1.2)
    try:
        from database.store import StudentStateStore
        store = StudentStateStore()
        student_count = store.get_student_count()
        logger.info(f'Tracking {student_count} students')
    except Exception as e:
        logger.warning(f'Database not initialized yet: {e}')
        logger.info('Database will be created automatically in Task 1.2')

    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="students think | /frame to start"
        )
    )

    logger.info('Bot is ready!')


@bot.event
async def on_message(message: discord.Message):
    """Handle incoming messages"""
    # Ignore bot's own messages
    if message.author.bot:
        return

    # Process commands first
    await bot.process_commands(message)

    # Additional message handling will be added in CIS Controller (Task 1.3)


@bot.command(name='ping')
async def ping(ctx):
    """Health check command - test bot connectivity"""
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! `{latency_ms}ms`')


@bot.command(name='status')
async def status(ctx):
    """Display bot status information"""
    embed = discord.Embed(
        title="K2M CIS Bot Status",
        description="K2M Interactive Reasoning Agent",
        color=discord.Color.blue()
    )

    embed.add_field(name="Connected Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Cohort Start", value=COHORT_START_DATE, inline=True)

    embed.add_field(
        name="Available Commands",
        value="/ping, /status, /frame (more coming in Sprint 1)",
        inline=False
    )

    await ctx.send(embed=embed)


# Error handler
@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        # Will be handled by natural language fallback in Task 1.3
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument: {str(error)}")
    else:
        logger.error(f"Command error: {error}", exc_info=True)
        await ctx.send("❌ An error occurred. Please try again.")


def main():
    """Run the bot"""
    try:
        logger.info('Starting K2M CIS Discord Bot...')
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        logger.error('Failed to login. Check DISCORD_TOKEN in .env file.')
    except Exception as e:
        logger.error(f'Error starting bot: {e}', exc_info=True)


if __name__ == '__main__':
    main()
