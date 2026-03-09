"""
K2M CIS Discord Bot - Main Entry Point
Story 4.7 Implementation: Discord Bot Technical Specification

This bot implements the complete CIS Agent System for Discord-based cohort facilitation.
Bot Name: KIRA (K2M Interactive Reasoning Agent)
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from cis_controller.llm_integration import (
    get_active_model,
    get_active_provider,
    load_system_prompts,
    set_runtime_failure_notifier,
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
COHORT_1_START_DATE = os.getenv("COHORT_1_START_DATE", "2026-02-01")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
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
health_monitor = None
parent_unsubscribe_server = None
interest_api_server = None
internal_webhook_server = None  # Task 7.11: HMAC-authenticated Apps Script → bot endpoints

# Task 7.2 — Decision N-07: asyncio.Lock + invite snapshot for on_member_join diff
# Dict shape: { guild_id: { invite_code: uses_count } }
_guild_invite_snapshot: dict = {}
_member_join_lock = asyncio.Lock()

# Validate required environment variables
if not DISCORD_TOKEN:
    raise ValueError(
        "DISCORD_TOKEN environment variable is required. "
        "Copy .env.template to .env and add your token."
    )

if not os.environ.get("COHORT_1_START_DATE"):
    raise EnvironmentError("COHORT_1_START_DATE not set - bot refusing to start")

if not os.environ.get("COHORT_1_FIRST_SESSION_DATE"):
    logger.warning(
        "COHORT_1_FIRST_SESSION_DATE not set - using COHORT_1_START_DATE as fallback"
    )

if ENVIRONMENT in {"production", "prod"} and not (
    DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")
):
    raise EnvironmentError(
        "DATABASE_URL must be set to a PostgreSQL DSN in production mode."
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


def _get_store():
    """Resolve runtime store (preferred) or factory store fallback."""
    from database import get_runtime_store, get_store

    return get_runtime_store() or get_store()


def _is_facilitator_member(member: Optional[discord.Member]) -> bool:
    """Role gate for facilitator-only slash commands."""
    if member is None or member.guild is None:
        return False
    facilitator_role = discord.utils.get(member.guild.roles, name="Facilitator")
    if facilitator_role is None:
        return False
    return facilitator_role in getattr(member, "roles", [])


async def _link_member_identity_to_roster(
    invite_code: str,
    member: discord.Member,
) -> Optional[dict]:
    """
    Best-effort Sheets bridge update for Column D (discord_id|discord_username).
    Returns roster payload when updated, else None.
    """
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
    if not spreadsheet_id:
        return None

    from cis_controller.interest_api_server import (
        link_roster_discord_identity_by_invite_code,
    )

    return await link_roster_discord_identity_by_invite_code(
        invite_code=invite_code,
        discord_id=str(member.id),
        discord_username=str(member.name),
        spreadsheet_id=spreadsheet_id,
        sheet_range=os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z").strip(),
        creds_path=os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "").strip() or None,
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
    embed.add_field(name="Cohort Start", value=COHORT_1_START_DATE, inline=True)
    embed.add_field(
        name="Provider / Model",
        value=f"{AI_PROVIDER} / {LLM_MODEL}",
        inline=False,
    )
    embed.add_field(
        name="Core Commands",
        value=(
            "/frame, /diverge, /challenge, /synthesize, /create-artifact, "
            "/save, /review, /edit, /publish, /showcase-preference, /parent-consent"
        ),
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
    global _slash_synced, daily_prompt_scheduler, health_monitor, parent_unsubscribe_server, interest_api_server, internal_webhook_server

    logger.info("%s has connected to Discord!", bot.user)
    logger.info("Serving %s guilds", len(bot.guilds))

    # Log server information
    for guild in bot.guilds:
        logger.info("Connected to: %s (ID: %s)", guild.name, guild.id)

    runtime_store = None
    runtime_participation_tracker = None
    runtime_escalation_system = None

    # Initialize database — PostgreSQL is the production primary.
    # SQLite is retained only as a local/test fallback when DATABASE_URL is absent.
    try:
        from database import get_store, set_runtime_store

        runtime_store = get_store()
        set_runtime_store(runtime_store)
        student_count = runtime_store.get_student_count()

        db_url = os.getenv("DATABASE_URL", "")
        if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
            logger.info("DB: PostgreSQL connected on startup")
        else:
            logger.info("DB: SQLite connected on startup (set DATABASE_URL for PostgreSQL)")
        logger.info("Tracking %s students", student_count)
    except Exception as exc:
        logger.warning("Database not initialized yet: %s", exc)
        logger.warning("Switching to in-memory backup mode until disk DB is restored.")
        try:
            from database.store import StudentStateStore
            from database import get_store, set_runtime_store

            StudentStateStore.activate_in_memory_fallback(
                reason=f"Startup DB initialization failed: {exc}"
            )
            runtime_store = get_store(database_url="")
            set_runtime_store(runtime_store)
        except Exception as fallback_exc:
            logger.error(
                "Failed to initialize in-memory backup store: %s",
                fallback_exc,
                exc_info=True,
            )

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
                    cohort_start_date=COHORT_1_START_DATE,
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
            facilitator_discord_id = os.getenv("FACILITATOR_DISCORD_ID", "").strip()

            if dashboard_channel_id and moderation_logs_id and facilitator_discord_id:
                runtime_escalation_system = EscalationSystem(
                    bot=bot,
                    store=runtime_store,
                    facilitator_dashboard_id=dashboard_channel_id,
                    moderation_logs_id=moderation_logs_id,
                    trevor_discord_id=facilitator_discord_id,
                )
            else:
                logger.warning(
                    "Escalation system not started: set CHANNEL_FACILITATOR_DASHBOARD, "
                    "CHANNEL_MODERATION_LOGS, and FACILITATOR_DISCORD_ID"
                )
    except Exception as exc:
        logger.error("Failed to initialize escalation system: %s", exc, exc_info=True)

    # Inject runtime services for router-level safety and tracking hooks.
    set_runtime_services(
        escalation_system=runtime_escalation_system,
        participation_tracker=runtime_participation_tracker,
    )

    # Initialize health monitor (Task 4.5: Bot failure handling + health checks)
    try:
        from cis_controller.health_monitor import HealthMonitor

        db_path = os.getenv("DATABASE_PATH", "cohort-1.db")
        dashboard_channel_id = int(os.getenv("CHANNEL_FACILITATOR_DASHBOARD", "0"))
        facilitator_discord_id = os.getenv("FACILITATOR_DISCORD_ID", "").strip()

        if dashboard_channel_id and facilitator_discord_id:
            if health_monitor is None:
                health_monitor = HealthMonitor(
                    bot=bot,
                    db_path=db_path,
                    facilitator_dashboard_id=dashboard_channel_id,
                    trevor_discord_id=facilitator_discord_id,
                    check_interval_seconds=300,  # 5 minutes
                )

            if not health_monitor.is_running:
                await health_monitor.start()
                logger.info("Health monitor started (5-minute interval)")

            set_runtime_failure_notifier(health_monitor.notify_llm_runtime_failure)
        else:
            set_runtime_failure_notifier(None)
            logger.warning(
                "Health monitor not started: set CHANNEL_FACILITATOR_DASHBOARD and FACILITATOR_DISCORD_ID"
            )
    except Exception as exc:
        set_runtime_failure_notifier(None)
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
                cohort_start_date=COHORT_1_START_DATE,
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

    # Optional lightweight unsubscribe endpoint for parent email links.
    enable_interest_api = os.getenv(
        "ENABLE_INTEREST_API",
        "true",
    ).strip().lower() in {"1", "true", "yes", "on"}
    mount_interest_on_parent = os.getenv(
        "MOUNT_INTEREST_API_ON_PARENT_SERVER",
        "true",
    ).strip().lower() in {"1", "true", "yes", "on"}

    if enable_interest_api and interest_api_server is None:
        from cis_controller.interest_api_server import InterestAPIServer

        interest_api_server = InterestAPIServer()

    try:
        enable_unsubscribe_server = os.getenv(
            "ENABLE_PARENT_UNSUBSCRIBE_SERVER",
            "true",
        ).strip().lower() in {"1", "true", "yes", "on"}

        if enable_unsubscribe_server and runtime_store:
            from cis_controller.parent_unsubscribe_server import ParentUnsubscribeServer

            host = os.getenv("PARENT_UNSUBSCRIBE_HOST", "0.0.0.0")
            port = int(os.getenv("PARENT_UNSUBSCRIBE_PORT", "8080"))
            path = os.getenv("PARENT_UNSUBSCRIBE_PATH", "/parent/unsubscribe")

            if parent_unsubscribe_server is None:
                mountable_interest_api = (
                    interest_api_server
                    if (enable_interest_api and mount_interest_on_parent)
                    else None
                )
                parent_unsubscribe_server = ParentUnsubscribeServer(
                    store=runtime_store,
                    interest_api_server=mountable_interest_api,
                    host=host,
                    port=port,
                    path=path,
                )
            await parent_unsubscribe_server.start()
        elif not enable_unsubscribe_server:
            logger.info("Parent unsubscribe server disabled by ENABLE_PARENT_UNSUBSCRIBE_SERVER=false")
    except Exception as exc:
        logger.error("Failed to start parent unsubscribe server: %s", exc, exc_info=True)

    # Initialize Interest API server (Task 7.1 - landing page enrollment endpoint)
    try:
        if enable_interest_api:
            mounted_on_parent = bool(
                parent_unsubscribe_server
                and getattr(parent_unsubscribe_server, "interest_api_server", None) is not None
            )
            if mounted_on_parent:
                logger.info(
                    "Interest API mounted on parent unsubscribe server; standalone listener skipped."
                )
            elif interest_api_server is not None:
                await interest_api_server.start()
        elif not enable_interest_api:
            logger.info("Interest API server disabled by ENABLE_INTEREST_API=false")
    except Exception as exc:
        logger.error("Failed to start interest API server: %s", exc, exc_info=True)

    # Task 7.11 — Decision N-03: HMAC-authenticated internal webhook endpoints for Apps Script
    try:
        if internal_webhook_server is None:
            from cis_controller.internal_api_server import InternalWebhookServer

            internal_host = os.getenv("INTERNAL_WEBHOOK_HOST", "0.0.0.0")
            internal_port = int(os.getenv("INTERNAL_WEBHOOK_PORT", "8082"))
            internal_webhook_server = InternalWebhookServer(
                host=internal_host,
                port=internal_port,
                bot=bot,
            )
        else:
            internal_webhook_server.set_bot(bot)

        await internal_webhook_server.start()
    except Exception as exc:
        logger.error("Failed to start internal webhook server: %s", exc, exc_info=True)

    # Task 7.2 — Decision B-01: snapshot guild invites for on_member_join diff matching
    for guild in bot.guilds:
        try:
            invites = await guild.invites()
            _guild_invite_snapshot[guild.id] = {inv.code: inv.uses for inv in invites}
            logger.info(
                "Invite snapshot: %d invites cached for guild %s", len(invites), guild.id
            )
        except discord.Forbidden:
            logger.warning(
                "Missing Manage Guild permission — invite tracking unavailable for guild %s",
                guild.id,
            )
        except Exception as exc:
            logger.warning("Could not snapshot invites for guild %s: %s", guild.id, exc)

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


@bot.tree.command(name="edit", description="Edit one artifact section (Week 6+).")
@app_commands.describe(section="Section number to edit (1-6).")
async def edit_slash(interaction: discord.Interaction, section: int):
    await route_slash_command(interaction, "edit", str(section))


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
    from commands.reflection import submit_reflection_handler

    store = _get_store()
    await submit_reflection_handler(
        interaction=interaction,
        store=store,
        habit_practice=habit_practice,
        identity_shift=identity_shift,
        proof_of_work=proof_of_work,
    )


@bot.tree.command(name="parent-consent", description="Set parent email consent preferences.")
@app_commands.describe(
    parent_email="Parent or guardian email address",
    consent_preference="Share weekly updates, or keep private until Week 8",
)
@app_commands.choices(
    consent_preference=[
        app_commands.Choice(name="Share weekly updates", value="share_weekly"),
        app_commands.Choice(name="Privacy first (until Week 8)", value="privacy_first"),
    ]
)
async def parent_consent_slash(
    interaction: discord.Interaction,
    parent_email: str,
    consent_preference: app_commands.Choice[str],
):
    from commands.parent_consent import set_parent_consent_handler

    store = _get_store()
    await set_parent_consent_handler(
        interaction=interaction,
        store=store,
        parent_email=parent_email,
        consent_preference=consent_preference.value,
    )


@bot.tree.command(name="update-parent-consent", description="Update parent email consent preference.")
@app_commands.describe(
    consent_preference="Share weekly updates, or keep private until Week 8",
)
@app_commands.choices(
    consent_preference=[
        app_commands.Choice(name="Share weekly updates", value="share_weekly"),
        app_commands.Choice(name="Privacy first (until Week 8)", value="privacy_first"),
    ]
)
async def update_parent_consent_slash(
    interaction: discord.Interaction,
    consent_preference: app_commands.Choice[str],
):
    from commands.parent_consent import update_parent_consent_handler

    store = _get_store()
    await update_parent_consent_handler(
        interaction=interaction,
        store=store,
        consent_preference=consent_preference.value,
    )


@bot.tree.command(name="view-parent-consent", description="View your current parent consent settings.")
async def view_parent_consent_slash(interaction: discord.Interaction):
    from commands.parent_consent import view_parent_consent_handler

    store = _get_store()
    await view_parent_consent_handler(
        interaction=interaction,
        store=store,
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
    from commands.admin import unlock_week

    store = _get_store()
    await unlock_week(interaction, store, student, week_number, reason)


# ============================================================
# TREVOR ADMIN COMMANDS (Task 1.7 - Observability Infrastructure)
# Guardrail-compliant dashboard for cohort facilitation
# ============================================================

@bot.tree.command(name="show-aggregate-patterns", description="Show cohort metrics (Trevor only).")
@app_commands.describe(days="Number of days to look back (default: 7)")
async def show_aggregate_patterns_slash(interaction: discord.Interaction, days: int = 7):
    """Show aggregate patterns - Guardrail #3 compliant (no comparison/ranking)."""
    from commands.admin import show_aggregate_patterns

    store = _get_store()
    await show_aggregate_patterns(interaction, store, days)


@bot.tree.command(name="inspect-journey", description="Inspect student journey (Trevor only, requires consent).")
@app_commands.describe(student="Student to inspect (@mention)")
async def inspect_journey_slash(interaction: discord.Interaction, student: Optional[discord.Member] = None):
    """Inspect individual student journey - REQUIRES student consent (Guardrail #8)."""
    from commands.admin import inspect_journey

    store = _get_store()
    await inspect_journey(interaction, store, student)


@bot.tree.command(name="show-stuck-students", description="Show inactive students (Trevor only).")
@app_commands.describe(inactive_days="Days since last interaction (default: 3)")
async def show_stuck_students_slash(interaction: discord.Interaction, inactive_days: int = 3):
    """Show students who may be stuck (intervention opportunities)."""
    from commands.admin import show_stuck_students

    store = _get_store()
    await show_stuck_students(interaction, store, inactive_days)


@bot.tree.command(name="show-zone-shifts", description="Show zone transformation events (Trevor only).")
@app_commands.describe(days="Number of days to look back (default: 30)")
async def show_zone_shifts_slash(interaction: discord.Interaction, days: int = 30):
    """Show zone shift events (identity transformation tracking)."""
    from commands.admin import show_zone_shifts

    store = _get_store()
    await show_zone_shifts(interaction, store, days)


@bot.tree.command(name="show-milestones", description="Show habit celebrations (Trevor only).")
@app_commands.describe(days="Number of days to look back (default: 7)")
async def show_milestones_slash(interaction: discord.Interaction, days: int = 7):
    """Show habit milestone celebrations."""
    from commands.admin import show_milestones

    store = _get_store()
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
    from commands.cluster import switch_cluster

    store = _get_store()
    await switch_cluster(interaction, store, student, cluster_id, reason)


@bot.tree.command(name="cluster-roster", description="Show roster for a cluster (Trevor only).")
@app_commands.describe(cluster_id="Cluster ID to show (1-8)")
async def cluster_roster_slash(interaction: discord.Interaction, cluster_id: int):
    """Show roster for a specific cluster."""
    from commands.cluster import show_cluster_roster

    store = _get_store()
    await show_cluster_roster(interaction, store, cluster_id)


@bot.tree.command(name="all-cluster-rosters", description="Show all cluster summaries (Trevor only).")
async def all_cluster_rosters_slash(interaction: discord.Interaction):
    """Show summary of all clusters."""
    from commands.cluster import show_all_cluster_rosters

    store = _get_store()
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
    from commands.cluster import post_session_summary

    store = _get_store()
    await post_session_summary(interaction, store, cluster_id, session_notes, attendance_count)


# ============================================================
# Task 7.2 — !recover_member (Decision B-01, GAP FIX #8)
# Temporal fallback for members who joined without their invite
# ============================================================

@bot.tree.command(
    name="recover-member",
    description="Manually link a member who joined without their unique invite (Trevor only).",
)
@app_commands.describe(
    member="The Discord member to recover",
    invite_code="Invite code from their enrollment email (Column R). Omit to use 24h temporal fallback.",
)
async def recover_member_slash(
    interaction: discord.Interaction,
    member: discord.Member,
    invite_code: Optional[str] = None,
):
    """
    Task 7.2 Decision B-01 + GAP FIX #8: Temporal fallback for unmatched joins.
    - With invite_code: exact match against students table
    - Without invite_code: finds most recently enrolled unlinked student within 24h
    Trevor-only.
    """
    await interaction.response.defer(ephemeral=True)

    caller = interaction.user if isinstance(interaction.user, discord.Member) else None
    if not _is_facilitator_member(caller):
        await interaction.followup.send(
            "This command requires the @Facilitator role.",
            ephemeral=True,
        )
        return

    store = _get_store()
    student = None

    if not hasattr(store, "get_student_by_invite_code") or not hasattr(store, "link_student_by_invite"):
        await interaction.followup.send(
            "Invite recovery requires PostgreSQL runtime store methods (`get_student_by_invite_code`, `link_student_by_invite`).",
            ephemeral=True,
        )
        return

    if invite_code:
        student = store.get_student_by_invite_code(invite_code.strip())
        if not student:
            await interaction.followup.send(
                f"No enrolled student found with invite code `{invite_code}`.",
                ephemeral=True,
            )
            return
    else:
        # Temporal fallback: most recent unlinked student enrolled within 24h
        try:
            student = store.get_recent_unlinked_student(hours=24)
        except Exception as exc:
            logger.error("recover_member temporal fallback failed: %s", exc, exc_info=True)
            student = None
        if not student:
            await interaction.followup.send(
                "No unlinked student found enrolled within the last 24 hours. "
                "Provide the `invite_code` to match explicitly.",
                ephemeral=True,
            )
            return

    used_code = student.get("invite_code", "") or ""
    linked = store.link_student_by_invite(
        invite_code=used_code,
        discord_id=str(member.id),
        discord_username=str(member.name),
    )

    if linked:
        roster_payload = None
        if used_code:
            try:
                roster_payload = await _link_member_identity_to_roster(used_code, member)
            except Exception as roster_exc:
                logger.warning("recover_member: roster sync failed: %s", roster_exc)

        guest_role = discord.utils.get(member.guild.roles, name="Guest")
        if guest_role and guest_role not in member.roles:
            try:
                await member.add_roles(guest_role)
            except Exception as role_exc:
                logger.warning("recover_member: could not assign @Guest: %s", role_exc)

        logger.info(
            "recover_member: linked discord_id=%s to email=%s invite=%s",
            member.id,
            student.get("enrollment_email", "?"),
            used_code,
        )
        if roster_payload:
            logger.info(
                "recover_member: roster row %s linked for invite=%s",
                roster_payload.get("row_number"),
                used_code,
            )
        await interaction.followup.send(
            f"**Member recovered.**\n"
            f"Linked {member.mention} → `{student.get('enrollment_email', '?')}` "
            f"(invite: `{used_code}`)",
            ephemeral=True,
        )
    else:
        await interaction.followup.send(
            "Link failed — the student row may already be claimed by another Discord account. "
            "Check the database or contact Trevor.",
            ephemeral=True,
        )


@bot.event
async def on_member_join(member: discord.Member):
    """
    Task 7.2 — Decision B-01 + N-07.

    Invite diff matching with asyncio.Lock:
    1. Snapshot guild invites before/after diff to find which invite was used
    2. Match invite_code → enrolled student in PostgreSQL
    3. Assign @Guest only (Guardrail #8: @Student granted after payment)
    4. Log student_linked or student_unmatched observability events
    5. Send personalised DM if matched, generic DM if unmatched
    """
    if member.bot:
        return

    async with _member_join_lock:
        try:
            # Fetch current invites (post-join state)
            try:
                current_invites = await member.guild.invites()
            except discord.Forbidden:
                logger.warning(
                    "Missing Manage Guild permission — invite diff unavailable for %s",
                    member.name,
                )
                current_invites = []

            current_map = {inv.code: inv.uses for inv in current_invites}
            old_map = _guild_invite_snapshot.get(member.guild.id, {})

            # Find the invite that was consumed:
            # Case 1 — invite still exists but uses count incremented
            # Case 2 — invite disappeared (max_uses=1 consumed and deleted by Discord)
            used_code = None
            for code, uses in current_map.items():
                if uses > old_map.get(code, 0):
                    used_code = code
                    break
            if used_code is None:
                for code in old_map:
                    if code not in current_map:
                        used_code = code
                        break

            # Refresh snapshot for the next join event
            _guild_invite_snapshot[member.guild.id] = current_map

            # --- DB match ---
            store = _get_store()
            student = None
            student_linked = False
            has_invite_methods = hasattr(store, "get_student_by_invite_code") and hasattr(
                store, "link_student_by_invite"
            )

            if used_code:
                if has_invite_methods:
                    student = store.get_student_by_invite_code(used_code)
                    if student:
                        student_linked = store.link_student_by_invite(
                            invite_code=used_code,
                            discord_id=str(member.id),
                            discord_username=str(member.name),
                        )

                # Fallback bridge: if DB lookup/link fails, still write Column D in Sheets
                # and hydrate runtime store from roster data when possible.
                if not student_linked:
                    roster_payload = await _link_member_identity_to_roster(used_code, member)
                    if roster_payload:
                        student_linked = True
                        try:
                            if hasattr(store, "upsert_student_from_sheets"):
                                store.upsert_student_from_sheets(
                                    enrollment_email=roster_payload.get("enrollment_email", ""),
                                    enrollment_name=roster_payload.get("enrollment_name", ""),
                                    invite_code=used_code,
                                    enrollment_status="lead",
                                    payment_status="lead",
                                )
                                store.link_student_by_invite(
                                    invite_code=used_code,
                                    discord_id=str(member.id),
                                    discord_username=str(member.name),
                                )
                                student = store.get_student_by_invite_code(used_code)
                        except Exception as hydrate_exc:
                            logger.warning(
                                "Could not hydrate runtime store from roster invite %s: %s",
                                used_code,
                                hydrate_exc,
                            )

                        if not student:
                            student = {
                                "enrollment_name": roster_payload.get("enrollment_name", ""),
                                "enrollment_email": roster_payload.get("enrollment_email", ""),
                                "profession": roster_payload.get("profession", ""),
                            }

            # --- Observability ---
            event_type = "student_linked" if student_linked else "student_unmatched"
            logger.info(
                "%s: discord_id=%s invite_code=%s",
                event_type, member.id, used_code,
            )
            try:
                store.log_observability_event(
                    discord_id=str(member.id),
                    event_type=event_type,
                    metadata={"invite_code": used_code, "guild_id": str(member.guild.id)},
                )
            except Exception:
                pass  # Observability must not block onboarding

            # --- Role assignment: @Guest only (Guardrail #8) ---
            guest_role = discord.utils.get(member.guild.roles, name="Guest")
            if guest_role:
                await member.add_roles(guest_role)
                logger.info("Assigned @Guest to %s", member.display_name)
            else:
                logger.warning("@Guest role not found for %s", member.display_name)

            # --- Welcome DM ---
            if student_linked:
                enrollment_name = (
                    student.get("enrollment_name") or member.display_name
                )
                first_name = enrollment_name.strip().split()[0] if enrollment_name else member.display_name
                welcome_message = (
                    f"Hey **{first_name}** — welcome to K2M Cohort #1!\n\n"
                    "Your enrollment is confirmed. I'm KIRA, your AI guide for this cohort.\n\n"
                    "Head to **#start-here** to complete your onboarding profile and "
                    "I'll take it from there.\n\n"
                    "— KIRA (K2M Interactive Reasoning Agent)"
                )
            else:
                welcome_message = (
                    f"Hey **{member.display_name}** — welcome!\n\n"
                    "It looks like you joined without a personal invite link. "
                    "To get full access, contact the program coordinator or use "
                    "the invite link from your enrollment confirmation email.\n\n"
                    "— KIRA"
                )

            try:
                await member.send(welcome_message)
                logger.info("Sent welcome DM to %s (linked=%s)", member.display_name, student_linked)
            except discord.Forbidden:
                logger.warning("Could not DM %s — DMs disabled", member.display_name)

        except Exception as exc:
            logger.error("Error in on_member_join for %s: %s", member.display_name, exc, exc_info=True)


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
    global health_monitor, parent_unsubscribe_server
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
        if health_monitor:
            health_monitor.stop_sync()
            health_monitor = None

        # Stop unsubscribe endpoint when bot shuts down
        if parent_unsubscribe_server:
            parent_unsubscribe_server.stop_sync()
            parent_unsubscribe_server = None

        # Stop Interest API server when bot shuts down
        if interest_api_server:
            interest_api_server.stop_sync()
            interest_api_server = None

        # Stop internal webhook server when bot shuts down (Task 7.11)
        if internal_webhook_server:
            internal_webhook_server.stop_sync()
            internal_webhook_server = None

        set_runtime_failure_notifier(None)


if __name__ == "__main__":
    main()


