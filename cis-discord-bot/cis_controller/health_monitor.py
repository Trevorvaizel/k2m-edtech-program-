"""
CIS Bot Health Monitor
Story 4.7 Implementation: Bot Failure Handling + Health Checks
Task 4.5: Automated health monitoring every 5 minutes

Monitors:
- Discord API connectivity
- Active LLM provider API
- SQLite database connectivity
- Daily database backups
- Trevor notifications for failures
"""

import asyncio
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import discord
from discord.ext import commands

from cis_controller.llm_integration import check_provider_api_health
from database.backup import DatabaseBackup

# Configure logging
logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Continuous health monitoring for CIS bot.

    Runs health checks every 5 minutes and alerts Trevor to failures.
    """

    def __init__(
        self,
        bot: commands.Bot,
        db_path: str,
        facilitator_dashboard_id: int,
        trevor_discord_id: str,
        check_interval_seconds: int = 300,  # 5 minutes
    ):
        """
        Initialize health monitor.

        Args:
            bot: Discord bot instance
            db_path: Path to SQLite database
            facilitator_dashboard_id: Channel ID for Trevor notifications
            trevor_discord_id: Trevor's Discord user ID
            check_interval_seconds: Health check interval (default: 300s = 5 min)
        """
        self.bot = bot
        self.db_path_raw = str(db_path)
        self.db_path = Path(db_path)
        self.facilitator_dashboard_id = facilitator_dashboard_id
        self.trevor_discord_id = trevor_discord_id
        self.check_interval = check_interval_seconds

        self._running = False
        self._task: Optional[asyncio.Task] = None

        # Health status tracking
        self.last_health_check: Optional[datetime] = None
        self.health_status: Dict[str, bool] = {
            "discord": True,
            "llm_provider": True,
            "database": True,
        }

        # Backup manager for daily database backups
        self.backup_manager = DatabaseBackup(db_path=db_path, retention_days=30)

    async def start(self) -> None:
        """Start health monitoring loop."""
        if self._running:
            logger.warning("Health monitor already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Health monitor started (interval: %s seconds)", self.check_interval)

    async def stop(self) -> None:
        """Stop health monitoring loop."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Health monitor stopped")

    def stop_sync(self) -> None:
        """
        Best-effort synchronous stop for shutdown paths without an event loop.
        """
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None

    @property
    def is_running(self) -> bool:
        """Return True when monitor loop is active."""
        return self._running and self._task is not None and not self._task.done()

    async def _monitor_loop(self) -> None:
        """Continuous health monitoring loop."""
        while self._running:
            try:
                await self._run_health_checks()
                await self._run_daily_backup()
            except Exception as exc:
                logger.error("Health check error: %s", exc, exc_info=True)

            # Wait for next interval
            await asyncio.sleep(self.check_interval)

    async def _run_health_checks(self) -> Dict[str, Any]:
        """
        Run all health checks and notify Trevor of failures.

        Returns:
            Dict with health check results
        """
        self.last_health_check = datetime.now()

        results = {
            "timestamp": self.last_health_check.isoformat(),
            "checks": {},
        }

        # Check Discord connectivity
        discord_ok = await self._check_discord()
        results["checks"]["discord"] = {
            "status": "ok" if discord_ok else "failed",
            "latency_ms": round(self.bot.latency * 1000) if discord_ok else None,
        }

        # Check LLM provider
        llm_ok, llm_details = await check_provider_api_health(timeout_seconds=10)
        results["checks"]["llm_provider"] = {
            "status": "ok" if llm_ok else "failed",
            "details": llm_details,
        }

        # Check database
        db_ok, db_details = await self._check_database()
        results["checks"]["database"] = {
            "status": "ok" if db_ok else "failed",
            "details": db_details,
        }

        # Update status tracking
        self.health_status["discord"] = discord_ok
        self.health_status["llm_provider"] = llm_ok
        self.health_status["database"] = db_ok

        if not db_ok:
            await self._activate_database_backup_mode(db_details)

        # Check for status changes (failures)
        failures = []
        if not discord_ok:
            failures.append("Discord API")
        if not llm_ok:
            failures.append("LLM provider")
        if not db_ok:
            failures.append("Database")

        if failures:
            await self._notify_trevor_of_failure(failures, results)

        return results

    async def _check_discord(self) -> bool:
        """Check Discord API connectivity."""
        try:
            # Check if bot is connected
            if not self.bot.is_ready():
                return False

            # Check latency
            if self.bot.latency > 1.0:  # >1 second is problematic
                logger.warning("High Discord latency: %s seconds", self.bot.latency)
                return False

            return True
        except Exception as exc:
            logger.error("Discord health check failed: %s", exc)
            return False

    async def _check_database(self) -> Tuple[bool, str]:
        """Check database connectivity and schema availability."""
        try:
            db_target = self.db_path_raw
            is_uri = db_target.startswith("file:")

            # Guard against silent sqlite auto-creation on wrong paths.
            if not is_uri and not Path(db_target).exists():
                return False, f"Database file missing: {db_target}"

            conn = sqlite3.connect(db_target, uri=is_uri)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='students'"
            )
            table = cursor.fetchone()
            conn.close()
            if not table:
                return False, "Missing required table: students"

            return True, "SQLite reachable"
        except Exception as exc:
            logger.error("Database health check failed: %s", exc)
            return False, str(exc)

    async def _run_daily_backup(self) -> None:
        """Run daily database backup if needed."""
        try:
            now = datetime.now()

            # Check if backup already run today
            backups = self.backup_manager.list_backups()
            if backups:
                latest_backup = backups[0]["created_at"]
                if latest_backup.date() == now.date():
                    logger.debug("Daily backup already completed today at %s", latest_backup)
                    return

            # Run backup
            logger.info("Starting daily database backup...")
            backup_path = self.backup_manager.create_backup()
            deleted = self.backup_manager.cleanup_old_backups()

            logger.info(
                "Daily backup completed: %s (cleaned up %s old backups)",
                backup_path.name,
                len(deleted),
            )

            # Notify Trevor of successful backup
            await self._notify_backup_success(backup_path, len(deleted))

        except Exception as exc:
            logger.error("Daily backup failed: %s", exc, exc_info=True)
            await self._notify_backup_failure(str(exc))

    async def _activate_database_backup_mode(self, reason: str) -> None:
        """
        Switch process stores to shared in-memory mode on database failure.
        """
        try:
            from database.store import StudentStateStore

            if StudentStateStore.is_in_memory_fallback_active():
                return

            StudentStateStore.activate_in_memory_fallback(reason=reason)
            await self._notify_database_backup_mode(reason)
        except Exception as exc:
            logger.error("Failed to activate in-memory backup mode: %s", exc, exc_info=True)

    async def notify_llm_runtime_failure(self, provider: str, agent: str, error: str) -> None:
        """
        Send immediate Trevor alert when runtime LLM calls fail.
        """
        embed = discord.Embed(
            title=f"🚨 CIS Agents Offline - {provider} API issue",
            description=f"Runtime failure while handling `/{agent}`",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Provider", value=provider, inline=True)
        embed.add_field(name="Agent", value=agent, inline=True)
        embed.add_field(name="Error", value=(error or "Unknown error")[:300], inline=False)
        embed.add_field(
            name="Student Experience",
            value="Students receive a fallback Habit-practice response while recovery retries continue.",
            inline=False,
        )
        await self._send_trevor_alert(
            embed=embed,
            fallback_text=f"🚨 CIS Agents Offline - {provider} API issue ({agent}): {error}",
        )

    async def _notify_database_backup_mode(self, reason: str) -> None:
        """Alert Trevor that DB fallback mode has been activated."""
        embed = discord.Embed(
            title="🚨 Database Error - Switching to backup mode",
            description="Disk database failed health checks. In-memory backup mode is active.",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Failure Details", value=(reason or "Unknown error")[:300], inline=False)
        embed.add_field(
            name="Recovery",
            value="Restore the SQLite DB from the latest backup and restart bot services.",
            inline=False,
        )
        await self._send_trevor_alert(
            embed=embed,
            fallback_text=f"🚨 Database Error - Switching to backup mode: {reason}",
        )

    async def _send_trevor_alert(self, embed: discord.Embed, fallback_text: str) -> None:
        """
        Send alert to facilitator dashboard, with DM fallback to Trevor.
        """
        async def _call_maybe_await(func, *args, **kwargs):
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result

        channel = self.bot.get_channel(self.facilitator_dashboard_id)
        if channel:
            await _call_maybe_await(channel.send, embed=embed)
            return

        logger.error(
            "Facilitator dashboard channel not found: %s; attempting Trevor DM fallback",
            self.facilitator_dashboard_id,
        )

        try:
            trevor_id = int(self.trevor_discord_id)
        except (TypeError, ValueError):
            logger.error("Invalid Trevor Discord ID: %s", self.trevor_discord_id)
            return

        user = self.bot.get_user(trevor_id)
        if user is None:
            try:
                user = await self.bot.fetch_user(trevor_id)
            except Exception as exc:
                logger.error("Failed to fetch Trevor user for DM fallback: %s", exc)
                return

        try:
            await _call_maybe_await(user.send, fallback_text)
        except Exception as exc:
            logger.error("Failed to DM Trevor fallback alert: %s", exc, exc_info=True)

    async def _notify_trevor_of_failure(
        self, failed_systems: list, health_results: Dict[str, Any]
    ) -> None:
        """Send Trevor notification about system failures."""
        try:
            failed_list = ", ".join(failed_systems)

            embed = discord.Embed(
                title="🚨 CIS Bot Health Check Failed",
                description=f"**Failed Systems:** {failed_list}",
                color=discord.Color.red(),
                timestamp=datetime.now(),
            )

            # Add details for each failed check
            for system, details in health_results["checks"].items():
                if details["status"] == "failed":
                    field_value = details.get("details", "Unknown error")
                    if isinstance(field_value, str) and len(field_value) > 100:
                        field_value = field_value[:97] + "..."
                    embed.add_field(
                        name=system.replace("_", " ").title(),
                        value=field_value,
                        inline=False,
                    )

            embed.add_field(
                name="Action Required",
                value="Please investigate the failed systems above. Bot may be degraded.",
                inline=False,
            )

            await self._send_trevor_alert(
                embed=embed,
                fallback_text=f"🚨 CIS Bot Health Check Failed: {failed_list}",
            )
            logger.warning("Notified Trevor of health check failures: %s", failed_list)

        except Exception as exc:
            logger.error("Failed to notify Trevor: %s", exc, exc_info=True)

    async def _notify_backup_success(self, backup_path: Path, cleaned_count: int) -> None:
        """Notify Trevor of successful backup."""
        try:
            status = self.backup_manager.get_backup_status()

            embed = discord.Embed(
                title="✅ Daily Database Backup Complete",
                color=discord.Color.green(),
                timestamp=datetime.now(),
            )

            embed.add_field(name="Backup File", value=backup_path.name, inline=True)
            embed.add_field(name="Old Backups Cleaned", value=str(cleaned_count), inline=True)
            embed.add_field(
                name="Total Backups", value=str(status["total_backups"]), inline=True
            )
            embed.add_field(
                name="Total Size", value=f"{status['total_size_mb']} MB", inline=True
            )

            await self._send_trevor_alert(
                embed=embed,
                fallback_text=f"✅ Daily DB backup complete: {backup_path.name}",
            )
            logger.info("Notified Trevor of successful backup")

        except Exception as exc:
            logger.error("Failed to notify Trevor of backup success: %s", exc)

    async def _notify_backup_failure(self, error: str) -> None:
        """Notify Trevor of backup failure."""
        try:
            embed = discord.Embed(
                title="❌ Daily Database Backup Failed",
                description=f"**Error:** {error}",
                color=discord.Color.red(),
                timestamp=datetime.now(),
            )

            embed.add_field(
                name="Action Required",
                value="Please investigate backup failure. Data may be at risk.",
                inline=False,
            )

            await self._send_trevor_alert(
                embed=embed,
                fallback_text=f"❌ Daily DB backup failed: {error}",
            )
            logger.warning("Notified Trevor of backup failure")

        except Exception as exc:
            logger.error("Failed to notify Trevor of backup failure: %s", exc)


def get_llm_fallback_message(agent: str) -> str:
    """
    Return fallback message when LLM provider is down.

    Encourages Habit 1 practice independently.

    Args:
        agent: Agent name (frame, diverge, challenge, synthesize)

    Returns:
        Fallback message for students
    """
    habit_messages = {
        "frame": (
            "⏸️ **The Framer is taking a short break.**\n\n"
            "You can still practice **Habit 1 (PAUSE)** on your own:\n\n"
            "1. **Stop** before typing your question\n"
            "2. **Ask yourself:** What do I actually want to know?\n"
            "3. **Try framing:** 'My situation is [describe]. I want to [goal].'\n\n"
            "You're building the habit even without the bot! 💪"
        ),
        "diverge": (
            "🔄 **The Explorer is taking a short break.**\n\n"
            "You can still practice **Habit 3 (ITERATE)** on your own:\n\n"
            "1. **List 3 possibilities** for your question\n"
            "2. **Change one thing** about each option\n"
            "3. **Notice** what new options emerge\n\n"
            "Iteration works even without AI help! 🚀"
        ),
        "challenge": (
            "🧠 **The Challenger is taking a short break.**\n\n"
            "You can still practice **Habit 4 (THINK FIRST)** on your own:\n\n"
            "1. **Write down** your assumption\n"
            "2. **Ask:** What if the opposite is true?\n"
            "3. **Test:** What evidence would prove you wrong?\n\n"
            "Critical thinking starts with you! 💡"
        ),
        "synthesize": (
            "✨ **The Synthesizer is taking a short break.**\n\n"
            "You can still practice synthesis on your own:\n\n"
            "1. **Review** your past CIS conversations\n"
            "2. **Look for patterns** in your thinking\n"
            "3. **Write 2-3 sentences** about what changed\n\n"
            "Your insights matter - with or without the bot! 🌟"
        ),
    }

    return habit_messages.get(
        agent,
        "⏸️ **CIS agents are taking a short break.**\n\n"
        "You can still practice the 4 Habits on your own:\n"
        "⏸️ **Pause** before asking\n"
        "🎯 **Add context** to your situation\n"
        "🔄 **Change one thing** at a time\n"
        "🧠 **Think before** deciding\n\n"
        "These habits follow you everywhere! 💪",
    )
