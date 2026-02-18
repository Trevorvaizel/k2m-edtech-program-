"""
K2M CIS Discord Bot - Main Entry Point
Story 4.7 Implementation: Discord Bot Technical Specification

This bot implements the complete CIS Agent System for Discord-based cohort facilitation.
Bot Name: KIRA (K2M Interactive Reasoning Agent)
"""

import logging
import os
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from cis_controller.llm_integration import (
    get_active_model,
    get_active_provider,
    load_system_prompts,
    validate_provider_configuration,
)
from cis_controller.router import route_slash_command, setup_bot_events

# Load environment variables
BOT_DIR = Path(__file__).resolve().parent
if not load_dotenv(dotenv_path=BOT_DIR / ".env", override=False):
    # Fallback for environments that inject vars differently.
    load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID", "").strip()
SYNC_GLOBAL_COMMANDS = os.getenv(
    "SYNC_GLOBAL_COMMANDS",
    "false" if DISCORD_GUILD_ID else "true",
).strip().lower() in {"1", "true", "yes", "on"}
AI_PROVIDER = get_active_provider()
LLM_MODEL = get_active_model(AI_PROVIDER)
COHORT_START_DATE = os.getenv("COHORT_START_DATE", "2026-02-01")
_slash_synced = False

# Weekly channel mapping for daily prompt scheduler (Story 2.1)
WEEKLY_CHANNEL_MAPPING = {
    1: int(os.getenv("CHANNEL_WEEK_1", "0")),
    2: int(os.getenv("CHANNEL_WEEK_2_3", "0")),
    3: int(os.getenv("CHANNEL_WEEK_2_3", "0")),  # Same channel for weeks 2-3
    4: int(os.getenv("CHANNEL_WEEK_4_5", "0")),
    5: int(os.getenv("CHANNEL_WEEK_4_5", "0")),  # Same channel for weeks 4-5
    6: int(os.getenv("CHANNEL_WEEK_6_7", "0")),
    7: int(os.getenv("CHANNEL_WEEK_6_7", "0")),  # Same channel for weeks 6-7
    8: int(os.getenv("CHANNEL_WEEK_8", "0")),
}

# Daily prompt scheduler instance (initialized in on_ready)
daily_prompt_scheduler = None

# Validate required environment variables
if not DISCORD_TOKEN:
    raise ValueError(
        "DISCORD_TOKEN environment variable is required. "
        "Copy .env.template to .env and add your token."
    )

provider_ok, provider_details = validate_provider_configuration()
if not provider_ok:
    logger.warning("LLM provider config invalid: %s", provider_details)
else:
    logger.info("LLM provider ready: %s", provider_details)

# Discord bot configuration
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Required for prefix parsing and NL fallback
intents.dm_messages = True  # Required for private DM interactions
intents.members = True  # Required for member tracking

bot = commands.Bot(
    command_prefix="/",  # Keeps legacy message command support
    intents=intents,
    help_command=None,  # Custom help in #thinking-lab
)


def build_status_embed() -> discord.Embed:
    """Build a shared status embed for both prefix and slash commands."""
    embed = discord.Embed(
        title="K2M CIS Bot Status",
        description="K2M Interactive Reasoning Agent",
        color=discord.Color.blue(),
    )

    embed.add_field(name="Connected Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Cohort Start", value=COHORT_START_DATE, inline=True)
    embed.add_field(
        name="Provider / Model",
        value=f"{AI_PROVIDER} / {LLM_MODEL}",
        inline=False,
    )
    embed.add_field(
        name="Core Commands",
        value="/frame, /diverge, /challenge, /synthesize, /create-artifact",
        inline=False,
    )
    return embed


async def sync_slash_commands() -> None:
    """
    Sync application slash commands.

    If DISCORD_GUILD_ID is set, sync there first for immediate availability.
    """
    synced_any_guild = False

    if DISCORD_GUILD_ID:
        try:
            guild_obj = discord.Object(id=int(DISCORD_GUILD_ID))
            bot.tree.copy_global_to(guild=guild_obj)
            guild_synced = await bot.tree.sync(guild=guild_obj)
            logger.info(
                "Synced %s slash command(s) to guild %s.",
                len(guild_synced),
                DISCORD_GUILD_ID,
            )
            synced_any_guild = True
        except ValueError:
            logger.warning("DISCORD_GUILD_ID is not a valid integer: %s", DISCORD_GUILD_ID)
    else:
        # Fast-path sync for every connected guild so commands appear immediately.
        for guild in bot.guilds:
            try:
                bot.tree.copy_global_to(guild=guild)
                guild_synced = await bot.tree.sync(guild=guild)
                logger.info(
                    "Synced %s slash command(s) to guild %s (%s).",
                    len(guild_synced),
                    guild.name,
                    guild.id,
                )
                synced_any_guild = True
            except Exception as exc:
                logger.warning(
                    "Failed guild slash sync for %s (%s): %s",
                    guild.name,
                    guild.id,
                    exc,
                )

    if SYNC_GLOBAL_COMMANDS:
        global_synced = await bot.tree.sync()
        logger.info("Synced %s global slash command(s).", len(global_synced))
    else:
        logger.info("Global slash sync disabled (SYNC_GLOBAL_COMMANDS=false).")

    if not synced_any_guild and SYNC_GLOBAL_COMMANDS:
        logger.warning(
            "No guild-level slash sync completed. Global command propagation may take longer."
        )
    elif not synced_any_guild and not SYNC_GLOBAL_COMMANDS:
        logger.warning(
            "No guild-level slash sync completed and global sync is disabled."
        )


@bot.event
async def on_ready():
    """Bot startup initialization."""
    global _slash_synced, daily_prompt_scheduler

    logger.info("%s has connected to Discord!", bot.user)
    logger.info("Serving %s guilds", len(bot.guilds))

    # Log server information
    for guild in bot.guilds:
        logger.info("Connected to: %s (ID: %s)", guild.name, guild.id)

    # Initialize database
    try:
        from database.store import StudentStateStore

        store = StudentStateStore()
        student_count = store.get_student_count()
        logger.info("Tracking %s students", student_count)
    except Exception as exc:
        logger.warning("Database not initialized yet: %s", exc)
        logger.info("Database will be created automatically in Task 1.2")

    # Initialize daily prompt scheduler (Story 2.1)
    try:
        if DISCORD_GUILD_ID and all(WEEKLY_CHANNEL_MAPPING.values()):
            from scheduler.scheduler import DailyPromptScheduler

            guild_id_int = int(DISCORD_GUILD_ID)
            daily_prompt_scheduler = DailyPromptScheduler(
                bot=bot,
                guild_id=guild_id_int,
                channel_mapping=WEEKLY_CHANNEL_MAPPING,
                cohort_start_date=COHORT_START_DATE,
            )
            daily_prompt_scheduler.start()
            logger.info("Daily prompt scheduler started")
        else:
            logger.warning("Daily prompt scheduler not started: missing guild_id or channel mapping")
    except Exception as exc:
        logger.error("Failed to start daily prompt scheduler: %s", exc, exc_info=True)

    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="students think | /frame to start",
        )
    )

    if not _slash_synced:
        await sync_slash_commands()
        _slash_synced = True

    logger.info("Bot is ready!")


@bot.command(name="ping")
async def ping_prefix(ctx):
    """Health check command - test bot connectivity."""
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f"Pong! `{latency_ms}ms`")


@bot.command(name="status")
async def status_prefix(ctx):
    """Display bot status information."""
    await ctx.send(embed=build_status_embed())


@bot.tree.command(name="ping", description="Health check bot connectivity.")
async def ping_slash(interaction: discord.Interaction):
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! `{latency_ms}ms`", ephemeral=True)


@bot.tree.command(name="status", description="Show bot status details.")
async def status_slash(interaction: discord.Interaction):
    await interaction.response.send_message(embed=build_status_embed(), ephemeral=True)


@bot.tree.command(
    name="frame",
    description="Use The Framer in a private DM (Habit 1 + Habit 2).",
)
@app_commands.describe(prompt="What do you want to frame?")
async def frame_slash(interaction: discord.Interaction, prompt: str):
    await route_slash_command(interaction, "frame", prompt)


@bot.tree.command(
    name="framer",
    description="Alias for /frame.",
)
@app_commands.describe(prompt="What do you want to frame?")
async def framer_slash(interaction: discord.Interaction, prompt: str):
    await route_slash_command(interaction, "framer", prompt)


@bot.tree.command(name="diverge", description="Use The Explorer (Week 4+).")
async def diverge_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "diverge")


@bot.tree.command(name="challenge", description="Use The Challenger (Week 4+).")
async def challenge_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "challenge")


@bot.tree.command(name="synthesize", description="Use The Synthesizer (Week 6+).")
async def synthesize_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "synthesize")


@bot.tree.command(name="create-artifact", description="Start artifact workflow (Week 6+).")
async def create_artifact_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "create-artifact")


@bot.tree.command(name="save", description="Artifact workflow command (Week 6+).")
async def save_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "save")


@bot.tree.command(name="review", description="Artifact workflow command (Week 6+).")
async def review_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "review")


@bot.tree.command(name="publish", description="Artifact workflow command (Week 6+).")
async def publish_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "publish")


# ============================================================
# TREVOR ADMIN COMMANDS (Task 1.7 - Observability Infrastructure)
# Guardrail-compliant dashboard for cohort facilitation
# ============================================================

@bot.tree.command(name="show-aggregate-patterns", description="Show cohort metrics (Trevor only).")
@app_commands.describe(days="Number of days to look back (default: 7)")
async def show_aggregate_patterns_slash(interaction: discord.Interaction, days: int = 7):
    """Show aggregate patterns - Guardrail #3 compliant (no comparison/ranking)."""
    from database.store import StudentStateStore
    from commands.admin import show_aggregate_patterns

    store = StudentStateStore()
    await show_aggregate_patterns(interaction, store, days)


@bot.tree.command(name="inspect-journey", description="Inspect student journey (Trevor only, requires consent).")
@app_commands.describe(student="Student to inspect (@mention)")
async def inspect_journey_slash(interaction: discord.Interaction, student: discord.Member | None = None):
    """Inspect individual student journey - REQUIRES student consent (Guardrail #8)."""
    from database.store import StudentStateStore
    from commands.admin import inspect_journey

    store = StudentStateStore()
    await inspect_journey(interaction, store, student)


@bot.tree.command(name="show-stuck-students", description="Show inactive students (Trevor only).")
@app_commands.describe(inactive_days="Days since last interaction (default: 3)")
async def show_stuck_students_slash(interaction: discord.Interaction, inactive_days: int = 3):
    """Show students who may be stuck (intervention opportunities)."""
    from database.store import StudentStateStore
    from commands.admin import show_stuck_students

    store = StudentStateStore()
    await show_stuck_students(interaction, store, inactive_days)


@bot.tree.command(name="show-zone-shifts", description="Show zone transformation events (Trevor only).")
@app_commands.describe(days="Number of days to look back (default: 30)")
async def show_zone_shifts_slash(interaction: discord.Interaction, days: int = 30):
    """Show zone shift events (identity transformation tracking)."""
    from database.store import StudentStateStore
    from commands.admin import show_zone_shifts

    store = StudentStateStore()
    await show_zone_shifts(interaction, store, days)


@bot.tree.command(name="show-milestones", description="Show habit celebrations (Trevor only).")
@app_commands.describe(days="Number of days to look back (default: 7)")
async def show_milestones_slash(interaction: discord.Interaction, days: int = 7):
    """Show habit milestone celebrations."""
    from database.store import StudentStateStore
    from commands.admin import show_milestones

    store = StudentStateStore()
    await show_milestones(interaction, store, days)


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        # Handled by natural language fallback in controller.
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid argument: {str(error)}")
        return

    logger.error("Command error: %s", error, exc_info=True)
    await ctx.send("An error occurred. Please try again.")


def main():
    """Run the bot."""
    setup_bot_events(bot)
    load_system_prompts()

    try:
        if not provider_ok:
            raise ValueError(f"Invalid LLM provider configuration: {provider_details}")

        logger.info("Starting K2M CIS Discord Bot...")
        logger.info("Active provider/model: %s / %s", AI_PROVIDER, LLM_MODEL)
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Failed to login. Check DISCORD_TOKEN in .env file.")
    except Exception as exc:
        logger.error("Error starting bot: %s", exc, exc_info=True)
    finally:
        # Stop scheduler when bot shuts down
        if daily_prompt_scheduler:
            daily_prompt_scheduler.stop()


if __name__ == "__main__":
    main()
