"""
Tests for CIS Bot Health Monitor (Task 4.5).

Focus:
- Health check detection for Discord, LLM provider, Database
- Trevor notifications for failures
- LLM provider failure handling with fallback messages
- Daily backup integration
- Health monitor lifecycle (start/stop)
- No network required (all mocks)
"""

import asyncio
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cis_controller.health_monitor import (  # noqa: E402
    HealthMonitor,
    get_llm_fallback_message,
)


def _create_sqlite_test_db(db_path: Path) -> None:
    """Create a minimal DB schema expected by health checks."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS students (discord_id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()


class TestHealthMonitorInitialization:
    def test_initializes_with_bot_instance(self):
        bot = MagicMock()
        bot.latency = 0.1

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        assert monitor.bot == bot
        assert monitor.db_path == Path("/tmp/test.db")
        assert monitor.facilitator_dashboard_id == 12345
        assert monitor.trevor_discord_id == "987654321"
        assert monitor.check_interval == 300  # 5 minutes
        assert not monitor._running
        assert monitor._task is None

    def test_initializes_health_status_dict(self):
        bot = MagicMock()

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        assert "discord" in monitor.health_status
        assert "llm_provider" in monitor.health_status
        assert "database" in monitor.health_status
        assert all(monitor.health_status.values())


class TestDiscordHealthCheck:
    @pytest.mark.asyncio
    async def test_discord_healthy_when_connected(self):
        bot = MagicMock()
        bot.is_ready.return_value = True
        bot.latency = 0.05

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        result = await monitor._check_discord()
        assert result is True

    @pytest.mark.asyncio
    async def test_discord_unhealthy_when_not_ready(self):
        bot = MagicMock()
        bot.is_ready.return_value = False
        bot.latency = 0.05

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        result = await monitor._check_discord()
        assert result is False

    @pytest.mark.asyncio
    async def test_discord_unhealthy_when_high_latency(self):
        bot = MagicMock()
        bot.is_ready.return_value = True
        bot.latency = 1.5  # > 1 second

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        result = await monitor._check_discord()
        assert result is False

    @pytest.mark.asyncio
    async def test_discord_unhealthy_on_exception(self):
        bot = MagicMock()
        bot.is_ready.side_effect = Exception("Discord connection error")

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        result = await monitor._check_discord()
        assert result is False


class TestDatabaseHealthCheck:
    @pytest.mark.asyncio
    async def test_database_healthy_when_connected(self, tmp_path):
        bot = MagicMock()
        db_path = tmp_path / "health.db"
        _create_sqlite_test_db(db_path)

        monitor = HealthMonitor(
            bot=bot,
            db_path=str(db_path),
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        result, details = await monitor._check_database()
        assert result is True
        assert "reachable" in details

    @pytest.mark.asyncio
    async def test_database_unhealthy_when_file_missing(self, tmp_path):
        bot = MagicMock()
        db_path = tmp_path / "missing.db"

        monitor = HealthMonitor(
            bot=bot,
            db_path=str(db_path),
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        result, details = await monitor._check_database()
        assert result is False
        assert "missing" in details.lower()

    @pytest.mark.asyncio
    async def test_database_unhealthy_on_connection_error(self):
        bot = MagicMock()

        # Mock sqlite3.connect to raise exception
        with patch("sqlite3.connect", side_effect=Exception("Database connection error")):
            monitor = HealthMonitor(
                bot=bot,
                db_path="/tmp/test.db",
                facilitator_dashboard_id=12345,
                trevor_discord_id="987654321",
            )

            result, _details = await monitor._check_database()
            assert result is False


class TestHealthCheckExecution:
    @pytest.mark.asyncio
    async def test_run_health_checks_updates_status(self):
        bot = MagicMock()
        bot.is_ready.return_value = True
        bot.latency = 0.05

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        with patch(
            "cis_controller.health_monitor.check_provider_api_health",
            new=AsyncMock(return_value=(True, "ok")),
        ), patch.object(
            monitor, "_check_database", new=AsyncMock(return_value=(True, "ok"))
        ):
            results = await monitor._run_health_checks()

        assert "timestamp" in results
        assert "checks" in results
        assert "discord" in results["checks"]
        assert "llm_provider" in results["checks"]
        assert "database" in results["checks"]
        assert monitor.last_health_check is not None

    @pytest.mark.asyncio
    async def test_health_check_detects_failures(self):
        bot = MagicMock()
        bot.is_ready.return_value = False  # Discord failure
        bot.latency = 2.0

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        # Mock Trevor notification
        monitor._notify_trevor_of_failure = AsyncMock()

        with patch(
            "cis_controller.health_monitor.check_provider_api_health",
            new=AsyncMock(return_value=(True, "ok")),
        ), patch.object(
            monitor, "_check_database", new=AsyncMock(return_value=(True, "ok"))
        ):
            results = await monitor._run_health_checks()

        # Should detect Discord failure
        assert results["checks"]["discord"]["status"] == "failed"
        # Should notify Trevor
        monitor._notify_trevor_of_failure.assert_awaited_once()


class TestTrevorNotifications:
    @pytest.mark.asyncio
    async def test_notifies_trevor_of_discord_failure(self):
        bot = MagicMock()
        channel = MagicMock()
        bot.get_channel.return_value = channel

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        await monitor._notify_trevor_of_failure(
            ["Discord API"],
            {"checks": {"discord": {"status": "failed", "details": "Connection timeout"}}},
        )

        bot.get_channel.assert_called_once_with(12345)
        channel.send.assert_called_once()
        call_args = channel.send.call_args
        embed = call_args.kwargs.get("embed")
        assert embed is not None
        assert "Failed Systems:" in embed.description or "Failed Systems" in str(embed.title)

    @pytest.mark.asyncio
    async def test_notifies_trevor_of_multiple_failures(self):
        bot = MagicMock()
        channel = MagicMock()
        bot.get_channel.return_value = channel

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        await monitor._notify_trevor_of_failure(
            ["Discord API", "LLM provider", "Database"],
            {
                "checks": {
                    "discord": {"status": "failed"},
                    "llm_provider": {"status": "failed"},
                    "database": {"status": "failed"},
                }
            },
        )

        channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_notification_failure_is_logged_gracefully(self):
        bot = MagicMock()
        bot.get_channel.return_value = None  # Channel not found
        bot.get_user.return_value = None
        bot.fetch_user = AsyncMock(side_effect=Exception("user not found"))

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        # Should not raise exception
        await monitor._notify_trevor_of_failure(
            ["Discord API"],
            {"checks": {"discord": {"status": "failed"}}},
        )


class TestFailureFallbackControls:
    @pytest.mark.asyncio
    async def test_runtime_llm_failure_alerts_trevor(self):
        bot = MagicMock()
        channel = MagicMock()
        bot.get_channel.return_value = channel

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        await monitor.notify_llm_runtime_failure(
            provider="openai",
            agent="frame",
            error="API timeout",
        )

        channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_failure_activates_in_memory_mode(self):
        from database.store import StudentStateStore

        bot = MagicMock()
        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )
        monitor._notify_database_backup_mode = AsyncMock()

        with patch.object(
            StudentStateStore,
            "is_in_memory_fallback_active",
            return_value=False,
        ), patch.object(StudentStateStore, "activate_in_memory_fallback") as activate:
            await monitor._activate_database_backup_mode("disk IO error")

        activate.assert_called_once_with(reason="disk IO error")
        monitor._notify_database_backup_mode.assert_awaited_once()


class TestDailyBackups:
    @pytest.mark.asyncio
    async def test_runs_daily_backup_when_needed(self):
        bot = MagicMock()

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        # Mock backup manager to simulate no backup today
        monitor.backup_manager.list_backups = MagicMock(return_value=[])
        monitor.backup_manager.create_backup = MagicMock(return_value=Path("/tmp/backup.sqlite"))
        monitor.backup_manager.cleanup_old_backups = MagicMock(return_value=[])

        # Mock Trevor notification
        monitor._notify_backup_success = AsyncMock()

        await monitor._run_daily_backup()

        monitor.backup_manager.create_backup.assert_called_once()
        monitor.backup_manager.cleanup_old_backups.assert_called_once()
        monitor._notify_backup_success.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_backup_if_already_run_today(self):
        bot = MagicMock()

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        # Mock backup manager to simulate backup already done today
        today = datetime.now()
        monitor.backup_manager.list_backups = MagicMock(
            return_value=[{"created_at": today, "path": "/tmp/backup.sqlite"}]
        )
        monitor.backup_manager.create_backup = MagicMock(return_value=Path("/tmp/backup.sqlite"))

        await monitor._run_daily_backup()

        # Should not create another backup
        monitor.backup_manager.create_backup.assert_not_called()

    @pytest.mark.asyncio
    async def test_notifies_trevor_on_backup_success(self):
        bot = MagicMock()
        channel = MagicMock()
        bot.get_channel.return_value = channel

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        monitor.backup_manager.get_backup_status = MagicMock(
            return_value={
                "total_backups": 5,
                "total_size_mb": 10.5,
            }
        )

        await monitor._notify_backup_success(Path("/tmp/backup.sqlite"), 2)

        channel.send.assert_called_once()
        call_args = channel.send.call_args
        embed = call_args.kwargs.get("embed")
        assert embed is not None

    @pytest.mark.asyncio
    async def test_notifies_trevor_on_backup_failure(self):
        bot = MagicMock()
        channel = MagicMock()
        bot.get_channel.return_value = channel

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
        )

        await monitor._notify_backup_failure("Permission denied")

        channel.send.assert_called_once()
        call_args = channel.send.call_args
        embed = call_args.kwargs.get("embed")
        assert embed is not None
        assert "Permission denied" in embed.description


class TestHealthMonitorLifecycle:
    @pytest.mark.asyncio
    async def test_start_creates_monitoring_task(self):
        bot = MagicMock()

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
            check_interval_seconds=1,  # Short interval for testing
        )

        # Mock the monitoring loop to prevent infinite loop
        async def mock_monitor_loop():
            monitor._running = True
            await asyncio.sleep(0.1)
            monitor._running = False

        monitor._monitor_loop = mock_monitor_loop

        await monitor.start()

        assert monitor._running is True
        assert monitor._task is not None

    @pytest.mark.asyncio
    async def test_stop_cancels_monitoring_task(self):
        bot = MagicMock()

        monitor = HealthMonitor(
            bot=bot,
            db_path="/tmp/test.db",
            facilitator_dashboard_id=12345,
            trevor_discord_id="987654321",
            check_interval_seconds=1,
        )

        # Create a fake running task
        monitor._running = True
        monitor._task = asyncio.create_task(asyncio.sleep(10))

        await monitor.stop()

        assert monitor._running is False


class TestLLMFallbackMessages:
    def test_frame_fallback_encourages_habit_1(self):
        message = get_llm_fallback_message("frame")

        assert "Habit 1" in message or "PAUSE" in message
        assert "practice" in message.lower()
        assert "without the bot" in message or "on your own" in message

    def test_diverge_fallback_encourages_habit_3(self):
        message = get_llm_fallback_message("diverge")

        assert "Habit 3" in message or "ITERATE" in message
        assert "3 possibilities" in message or "options" in message

    def test_challenge_fallback_encourages_habit_4(self):
        message = get_llm_fallback_message("challenge")

        assert "Habit 4" in message or "THINK FIRST" in message
        assert "assumption" in message or "evidence" in message

    def test_synthesize_fallback_encourages_reflection(self):
        message = get_llm_fallback_message("synthesize")

        assert "synthesis" in message.lower() or "patterns" in message.lower()
        assert "past CIS conversations" in message or "thinking" in message

    def test_unknown_agent_returns_generic_message(self):
        message = get_llm_fallback_message("unknown-agent")

        assert "4 Habits" in message or "CIS agents" in message
        assert "practice" in message.lower()


class TestLLMProviderFailureHandling:
    @pytest.mark.asyncio
    async def test_llm_failure_returns_fallback_message(self):
        from cis_controller.llm_integration import call_agent_with_context

        # Mock provider to raise exception
        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="openai",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="gpt-4o-mini",
        ), patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            side_effect=Exception("API connection error"),
        ):
            response, cost_data = await call_agent_with_context("frame", None, "test", [])

            # Should return fallback message
            assert "Framer" in response or "PAUSE" in response
            assert cost_data["fallback"] is True
            assert cost_data["total_cost_usd"] == 0.0
            assert cost_data["total_tokens"] == 0

    @pytest.mark.asyncio
    async def test_anthropic_failure_returns_fallback_message(self):
        from cis_controller.llm_integration import call_agent_with_context

        # Mock Anthropic to raise exception
        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="anthropic",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="claude-sonnet-4-5",
        ), patch(
            "cis_controller.llm_integration._call_anthropic",
            new_callable=AsyncMock,
            side_effect=Exception("Anthropic API error"),
        ):
            response, cost_data = await call_agent_with_context("diverge", None, "test", [])

            # Should return fallback message
            assert "Explorer" in response or "ITERATE" in response
            assert cost_data["fallback"] is True
            assert cost_data["total_cost_usd"] == 0.0

    @pytest.mark.asyncio
    async def test_zhipu_failure_returns_fallback_message(self):
        from cis_controller.llm_integration import call_agent_with_context

        # Mock Zhipu to raise exception
        with patch(
            "cis_controller.llm_integration._ensure_system_prompt_loaded",
            return_value="SYSTEM PROMPT",
        ), patch(
            "cis_controller.llm_integration.get_active_provider",
            return_value="zhipu",
        ), patch(
            "cis_controller.llm_integration.get_active_model",
            return_value="glm-4.7",
        ), patch(
            "cis_controller.llm_integration._call_openai_compatible",
            new_callable=AsyncMock,
            side_effect=Exception("Zhipu API timeout"),
        ):
            response, cost_data = await call_agent_with_context("challenge", None, "test", [])

            # Should return fallback message
            assert "Challenger" in response or "THINK FIRST" in response
            assert cost_data["fallback"] is True
            assert cost_data["total_cost_usd"] == 0.0
