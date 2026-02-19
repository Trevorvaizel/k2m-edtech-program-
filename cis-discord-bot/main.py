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
from cis_controller.router import route_slash_command, setup_bot_events, set_runtime_services

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
        value="/frame, /diverge, /challenge, /synthesize, /create-artifact, /showcase-preference",
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

    runtime_store = None
    runtime_participation_tracker = None
    runtime_escalation_system = None

    # Initialize database
    try:
        from database.store import StudentStateStore

        runtime_store = StudentStateStore()
        student_count = runtime_store.get_student_count()
        logger.info("Tracking %s students", student_count)
    except Exception as exc:
        logger.warning("Database not initialized yet: %s", exc)
        logger.info("Database will be created automatically in Task 1.2")

    # Initialize participation tracker for weekly channels (Task 2.2 / 2.4 Level 1).
    try:
        if runtime_store:
            from cis_controller.participation_tracker import ParticipationTracker

            weekly_channel_ids = sorted({cid for cid in WEEKLY_CHANNEL_MAPPING.values() if cid})
            if weekly_channel_ids:
                runtime_participation_tracker = ParticipationTracker(
                    bot=bot,
                    store=runtime_store,
                    weekly_channel_ids=weekly_channel_ids,
                )
            else:
                logger.warning("Participation tracker not started: no weekly channels configured")
    except Exception as exc:
        logger.error("Failed to initialize participation tracker: %s", exc, exc_info=True)

    # Initialize escalation system (Task 2.4).
    try:
        if runtime_store:
            from cis_controller.escalation_system import EscalationSystem

            dashboard_channel_id = int(os.getenv("CHANNEL_FACILITATOR_DASHBOARD", "0"))
            moderation_logs_id = int(os.getenv("CHANNEL_MODERATION_LOGS", "0"))
            trevor_discord_id = os.getenv("TREVOR_DISCORD_ID", "").strip()

            if dashboard_channel_id and moderation_logs_id and trevor_discord_id:
                runtime_escalation_system = EscalationSystem(
                    bot=bot,
                    store=runtime_store,
                    facilitator_dashboard_id=dashboard_channel_id,
                    moderation_logs_id=moderation_logs_id,
                    trevor_discord_id=trevor_discord_id,
                )
            else:
                logger.warning(
                    "Escalation system not started: set CHANNEL_FACILITATOR_DASHBOARD, "
                    "CHANNEL_MODERATION_LOGS, and TREVOR_DISCORD_ID"
                )
    except Exception as exc:
        logger.error("Failed to initialize escalation system: %s", exc, exc_info=True)

    # Inject runtime services for router-level safety and tracking hooks.
    set_runtime_services(
        escalation_system=runtime_escalation_system,
        participation_tracker=runtime_participation_tracker,
    )

    # Initialize health monitor (Task 4.5: Bot failure handling + health checks)
    health_monitor = None
    try:
        if runtime_store:
            from cis_controller.health_monitor import HealthMonitor

            db_path = os.getenv("DATABASE_PATH", "cohort-1.db")
            dashboard_channel_id = int(os.getenv("CHANNEL_FACILITATOR_DASHBOARD", "0"))
            trevor_discord_id = os.getenv("TREVOR_DISCORD_ID", "").strip()

            if dashboard_channel_id and trevor_discord_id:
                health_monitor = HealthMonitor(
                    bot=bot,
                    db_path=db_path,
                    facilitator_dashboard_id=dashboard_channel_id,
                    trevor_discord_id=trevor_discord_id,
                    check_interval_seconds=300,  # 5 minutes
                )
                await health_monitor.start()
                logger.info("Health monitor started (5-minute interval)")
            else:
                logger.warning(
                    "Health monitor not started: set CHANNEL_FACILITATOR_DASHBOARD and TREVOR_DISCORD_ID"
                )
    except Exception as exc:
        logger.error("Failed to start health monitor: %s", exc, exc_info=True)

    # Initialize daily prompt scheduler (Story 2.1)
    try:
        if DISCORD_GUILD_ID:
            from scheduler.scheduler import DailyPromptScheduler

            guild_id_int = int(DISCORD_GUILD_ID)
            daily_prompt_scheduler = DailyPromptScheduler(
                bot=bot,
                guild_id=guild_id_int,
                channel_mapping=WEEKLY_CHANNEL_MAPPING,
                cohort_start_date=COHORT_START_DATE,
                escalation_system=runtime_escalation_system,
                participation_tracker=runtime_participation_tracker,
                store=runtime_store,
            )
            daily_prompt_scheduler.start()
            logger.info("Daily prompt scheduler started")

            missing_weeks = [week for week, channel_id in WEEKLY_CHANNEL_MAPPING.items() if not channel_id]
            if missing_weeks:
                logger.warning(
                    "Weekly channel mappings missing for weeks: %s. "
                    "Escalations/dashboard remain active; content posts may skip those weeks.",
                    missing_weeks,
                )
        else:
            logger.warning("Daily prompt scheduler not started: missing DISCORD_GUILD_ID")
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


@bot.tree.command(
    name="showcase-preference",
    description="Set your default share-to-showcase preference.",
)
@app_commands.describe(preference="How KIRA should handle your showcase sharing choice.")
@app_commands.choices(
    preference=[
        app_commands.Choice(name="Always ask me", value="always_ask"),
        app_commands.Choice(name="Always share publicly", value="always_yes"),
        app_commands.Choice(name="Never share publicly", value="always_no"),
        app_commands.Choice(name="Week 8 only", value="week8_only"),
    ]
)
async def showcase_preference_slash(
    interaction: discord.Interaction,
    preference: app_commands.Choice[str],
):
    from commands.showcase import set_showcase_preference_for_student

    try:
        set_showcase_preference_for_student(str(interaction.user.id), preference.value)
    except ValueError as exc:
        await interaction.response.send_message(str(exc), ephemeral=True)
        return

    labels = {
        "always_ask": "Always ask me",
        "always_yes": "Always share publicly",
        "always_no": "Never share publicly",
        "week8_only": "Week 8 only",
    }
    await interaction.response.send_message(
        f"Showcase preference saved: **{labels[preference.value]}**.",
        ephemeral=True,
    )


@bot.tree.command(name="save", description="Artifact workflow command (Week 6+).")
async def save_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "save")


@bot.tree.command(name="review", description="Artifact workflow command (Week 6+).")
async def review_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "review")


@bot.tree.command(name="publish", description="Artifact workflow command (Week 6+).")
async def publish_slash(interaction: discord.Interaction):
    await route_slash_command(interaction, "publish")


@bot.tree.command(name="submit-reflection", description="Submit Friday reflection to unlock next week.")
@app_commands.describe(
    habit_practice="Did you practice this week's habit? (Yes/Sometimes/No)",
    identity_shift="What changed this week?",
    proof_of_work="One sentence showing AI understood you",
)
async def submit_reflection_slash(
    interaction: discord.Interaction,
    habit_practice: str,
    identity_shift: str,
    proof_of_work: str,
):
    from database.store import StudentStateStore
    from commands.reflection import submit_reflection_handler

    store = StudentStateStore()
    await submit_reflection_handler(
        interaction=interaction,
        store=store,
        habit_practice=habit_practice,
        identity_shift=identity_shift,
        proof_of_work=proof_of_work,
    )


@bot.tree.command(name="unlock-week", description="Manually unlock a student's next week (Trevor only).")
@app_commands.describe(
    student="Student mention",
    week_number="Week number to unlock (1-7)",
    reason="Reason for manual override",
)
async def unlock_week_slash(
    interaction: discord.Interaction,
    student: discord.Member,
    week_number: int,
    reason: str = "Manual override by Trevor",
):
    from database.store import StudentStateStore
    from commands.admin import unlock_week

    store = StudentStateStore()
    await unlock_week(interaction, store, student, week_number, reason)


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


# ============================================================
# CLUSTER MANAGEMENT COMMANDS (Task 4.3)
# Trevor-admin commands for cluster assignment and switching
# ============================================================

@bot.tree.command(name="switch-cluster", description="Switch student to different cluster (Trevor only).")
@app_commands.describe(
    student="Student to switch (@mention)",
    cluster_id="Target cluster (1-8)",
    reason="Reason for switch (optional)"
)
async def switch_cluster_slash(
    interaction: discord.Interaction,
    student: discord.Member,
    cluster_id: int,
    reason: str = None
):
    """Switch a student to a different cluster."""
    from database.store import StudentStateStore
    from commands.cluster import switch_cluster

    store = StudentStateStore()
    await switch_cluster(interaction, store, student, cluster_id, reason)


@bot.tree.command(name="cluster-roster", description="Show roster for a cluster (Trevor only).")
@app_commands.describe(cluster_id="Cluster ID to show (1-8)")
async def cluster_roster_slash(interaction: discord.Interaction, cluster_id: int):
    """Show roster for a specific cluster."""
    from database.store import StudentStateStore
    from commands.cluster import show_cluster_roster

    store = StudentStateStore()
    await show_cluster_roster(interaction, store, cluster_id)


@bot.tree.command(name="all-cluster-rosters", description="Show all cluster summaries (Trevor only).")
async def all_cluster_rosters_slash(interaction: discord.Interaction):
    """Show summary of all clusters."""
    from database.store import StudentStateStore
    from commands.cluster import show_all_cluster_rosters

    store = StudentStateStore()
    await show_all_cluster_rosters(interaction, store)


@bot.tree.command(name="post-session-summary", description="Post session summary after cluster session (Trevor only).")
@app_commands.describe(
    cluster_id="Cluster ID (1-8)",
    session_notes="Session summary from Trevor",
    attendance_count="Number of attendees (optional)"
)
async def post_session_summary_slash(
    interaction: discord.Interaction,
    cluster_id: int,
    session_notes: str,
    attendance_count: int = None
):
    """Post session summary after completing a cluster session (Task 4.4)."""
    from database.store import StudentStateStore
    from commands.cluster import post_session_summary

    store = StudentStateStore()
    await post_session_summary(interaction, store, cluster_id, session_notes, attendance_count)


@bot.event
async def on_member_join(member: discord.Member):
    """
    Handle new member joining - auto-assign cluster (Task 4.3).

    Per Story 5.1:
    1. Extract last name from display_name
    2. Auto-assign to cluster based on last name (8 clusters)
    3. Assign @Student role
    4. Assign @Cluster-X role
    5. Send welcome DM with cluster info
    """
    from database.store import StudentStateStore

    # Skip bots
    if member.bot:
        return

    try:
        # Initialize store
        store = StudentStateStore()

        # Extract last name from display_name
        # Format: "John Anderson" or "Anderson" or "John"
        display_name = member.display_name or member.name
        last_name = display_name.split()[-1] if display_name else None

        # Create student with cluster assignment
        student = store.create_student(
            discord_id=str(member.id),
            last_name=last_name
        )

        cluster_id = student["cluster_id"]

        # Assign @Student role
        student_role = discord.utils.get(member.guild.roles, name="Student")
        if student_role:
            await member.add_roles(student_role)
            logger.info(f"Assigned @Student role to {member.display_name}")
        else:
            logger.warning(f"@Student role not found for {member.display_name}")

        # Assign @Cluster-X role
        cluster_role_name = f"Cluster-{cluster_id}"
        cluster_role = discord.utils.get(member.guild.roles, name=cluster_role_name)
        if cluster_role:
            await member.add_roles(cluster_role)
            logger.info(f"Assigned @{cluster_role_name} to {member.display_name}")
        else:
            logger.warning(f"@{cluster_role_name} role not found for {member.display_name}; creating role")
            try:
                cluster_role = await member.guild.create_role(name=cluster_role_name, mentionable=False)
                await member.add_roles(cluster_role)
                logger.info(f"Created and assigned @{cluster_role_name} to {member.display_name}")
            except Exception as role_exc:
                logger.error("Failed to create %s role: %s", cluster_role_name, role_exc, exc_info=True)

        from scheduler.cluster_sessions import ClusterSessionScheduler

        schedule_helper = ClusterSessionScheduler(
            bot=bot,
            store=store,
            guild_id=member.guild.id,
            channel_mapping=WEEKLY_CHANNEL_MAPPING,
            cohort_start_date=COHORT_START_DATE,
        )
        schedule_text = schedule_helper.get_cluster_schedule_text(cluster_id)

        # Send welcome DM
        cluster_names = {
            1: "A-F", 2: "G-L", 3: "M-R", 4: "S-Z",
            5: "A-F (overflow)", 6: "G-L (overflow)", 7: "M-R (overflow)", 8: "S-Z (overflow)"
        }

        welcome_message = f"""👋 Welcome to K2M Cohort #1, **{member.display_name}**!

You're in **Cluster {cluster_id}** (Last names: {cluster_names.get(cluster_id, 'Unknown')})

📅 **Cluster Session Schedule:**
Cluster {cluster_id} meets **{schedule_text}**

🎯 **What to do now:**
1. Introduce yourself in #week-1-wonder
2. Check your daily prompts at 9:15 AM EAT
3. Use `/frame` when you have a question to think through

See you Monday! Let's build some thinking skills together 🚀

— KIRA (K2M Interactive Reasoning Agent)
"""

        await member.send(welcome_message)
        logger.info(f"Sent welcome DM to {member.display_name} (Cluster {cluster_id})")

    except Exception as exc:
        logger.error(f"Error handling member join for {member.display_name}: {exc}", exc_info=True)


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


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    """
    Global slash-command error handler.

    Prevents "The application did not respond" by always returning a fallback
    interaction response when command callbacks raise.
    """
    logger.error("Slash command error: %s", error, exc_info=True)

    fallback = "I hit an error while processing that command. Please try again."
    try:
        if interaction.response.is_done():
            await interaction.followup.send(fallback, ephemeral=True)
        else:
            await interaction.response.send_message(fallback, ephemeral=True)
    except Exception as response_error:
        logger.error(
            "Failed to send slash command error fallback: %s",
            response_error,
            exc_info=True,
        )


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

        # Stop health monitor when bot shuts down
        health_monitor = None  # Will be cleaned up by bot closure


if __name__ == "__main__":
    main()
