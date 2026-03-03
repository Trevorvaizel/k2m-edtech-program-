"""
Task 5.5 integration tests: performance and cost validation.

Validates production-readiness criteria from sprint task 5.5:
1) CIS agent response SLA (<5 seconds)
2) 50+ concurrent conversation handling
3) Rate limiting under load
4) Cost tracking and budget threshold alerts
5) Backup automation + 5-minute health-check cadence
"""

import asyncio
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cis_controller.health_monitor import HealthMonitor  # noqa: E402
from cis_controller.llm_integration import call_agent_with_context  # noqa: E402
from cis_controller.rate_limiter import RateLimiter  # noqa: E402


@pytest.fixture
def rate_limit_db():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row

    db.execute(
        """
        CREATE TABLE students (
            discord_id TEXT PRIMARY KEY,
            cohort_id TEXT NOT NULL,
            start_date TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            agent TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        """
        CREATE TABLE api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            total_interactions INTEGER,
            total_tokens INTEGER,
            total_cost_usd REAL
        )
        """
    )
    db.commit()

    yield db
    db.close()


def _attach_limiter_to_db(db: sqlite3.Connection) -> RateLimiter:
    limiter = RateLimiter()
    limiter.store.db = db
    return limiter


@pytest.mark.asyncio
@pytest.mark.parametrize("agent", ["frame", "diverge", "challenge", "synthesize"])
async def test_cis_agent_response_time_under_five_seconds(agent):
    async def provider_stub(**_kwargs):
        await asyncio.sleep(0.05)
        return "ok", {"total_tokens": 120, "total_cost_usd": 0.0025}

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
        new=AsyncMock(side_effect=provider_stub),
    ):
        start = time.perf_counter()
        response, cost_data = await call_agent_with_context(
            agent=agent,
            student_context=SimpleNamespace(
                current_week=6,
                zone="zone_3",
                emotional_state="curious",
                jtbd_primary_concern="career_direction",
            ),
            user_message="Help me think this through.",
            conversation_history=[],
        )
        elapsed = time.perf_counter() - start

    assert response == "ok"
    assert cost_data["total_tokens"] == 120
    assert elapsed < 5.0


@pytest.mark.asyncio
async def test_supports_fifty_plus_concurrent_conversations():
    async def provider_stub(**_kwargs):
        await asyncio.sleep(0.05)
        return "ok", {"total_tokens": 100, "total_cost_usd": 0.001}

    async def run_conversation(i: int):
        return await call_agent_with_context(
            agent="frame",
            student_context=SimpleNamespace(
                current_week=2,
                zone="zone_1",
                emotional_state="curious",
                jtbd_primary_concern="university_application",
            ),
            user_message=f"Conversation {i}",
            conversation_history=[],
        )

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
        new=AsyncMock(side_effect=provider_stub),
    ):
        start = time.perf_counter()
        results = await asyncio.gather(*(run_conversation(i) for i in range(55)))
        elapsed = time.perf_counter() - start

    assert len(results) == 55
    assert all(response == "ok" for response, _ in results)
    assert elapsed < 5.0


def test_rate_limits_hold_under_load(rate_limit_db):
    limiter = _attach_limiter_to_db(rate_limit_db)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    heavy_user = "heavy-user"

    for i in range(50):
        rate_limit_db.execute(
            """
            INSERT INTO conversations (student_id, agent, role, content, created_at)
            VALUES (?, 'frame', 'user', ?, ?)
            """,
            (heavy_user, f"heavy message {i}", now),
        )

    for i in range(55):
        student_id = f"student-{i}"
        rate_limit_db.execute(
            """
            INSERT INTO conversations (student_id, agent, role, content, created_at)
            VALUES (?, 'frame', 'user', ?, ?)
            """,
            (student_id, "single interaction", now),
        )
    rate_limit_db.commit()

    allowed, error = limiter.check_rate_limit(heavy_user)
    assert allowed is False
    assert "50 CIS agent interactions" in error

    allowed_counts = [
        limiter.check_rate_limit(f"student-{i}")[0]
        for i in range(55)
    ]
    assert all(allowed_counts)


def test_cost_tracking_and_budget_alert_thresholds(rate_limit_db):
    limiter = _attach_limiter_to_db(rate_limit_db)
    limiter.DAILY_BUDGET_ALERT = 0.01
    limiter.WEEKLY_BUDGET_CAP = 0.02

    state_1 = limiter.track_interaction(
        discord_id="student-a",
        agent="frame",
        tokens=100,
        cost_usd=0.004,
    )
    assert state_1["daily_total"] == pytest.approx(0.004)
    assert state_1["daily_alert_triggered"] is False
    assert state_1["weekly_cap_exceeded"] is False

    state_2 = limiter.track_interaction(
        discord_id="student-b",
        agent="diverge",
        tokens=120,
        cost_usd=0.007,
    )
    assert state_2["daily_total"] == pytest.approx(0.011)
    assert state_2["daily_alert_triggered"] is True
    assert state_2["weekly_cap_exceeded"] is False

    state_3 = limiter.track_interaction(
        discord_id="student-c",
        agent="challenge",
        tokens=140,
        cost_usd=0.0105,
    )
    assert state_3["daily_total"] == pytest.approx(0.0215)
    assert state_3["weekly_alert_triggered"] is True
    assert state_3["weekly_cap_exceeded"] is True

    today = datetime.now().strftime("%Y-%m-%d")
    row = rate_limit_db.execute(
        "SELECT total_tokens, total_cost_usd, total_interactions FROM api_usage WHERE date = ?",
        (today,),
    ).fetchone()
    assert row is not None
    assert row["total_tokens"] == 360
    assert row["total_interactions"] == 3
    assert row["total_cost_usd"] == pytest.approx(0.0215)

    allowed, error = limiter.check_rate_limit("new-student")
    assert allowed is False
    assert "weekly cohort budget cap" in error


@pytest.mark.asyncio
async def test_health_monitor_cadence_and_backup_automation(tmp_path):
    db_path = tmp_path / "health_task_5_5.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE students (discord_id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

    bot = MagicMock()
    bot.is_ready.return_value = True
    bot.latency = 0.05

    monitor = HealthMonitor(
        bot=bot,
        db_path=str(db_path),
        facilitator_dashboard_id=12345,
        trevor_discord_id="987654321",
    )
    assert monitor.check_interval == 300

    with patch(
        "cis_controller.health_monitor.check_provider_api_health",
        new=AsyncMock(return_value=(True, "ok")),
    ):
        health_results = await monitor._run_health_checks()

    assert health_results["checks"]["discord"]["status"] == "ok"
    assert health_results["checks"]["llm_provider"]["status"] == "ok"
    assert health_results["checks"]["database"]["status"] == "ok"

    monitor.backup_manager.list_backups = MagicMock(return_value=[])
    monitor.backup_manager.create_backup = MagicMock(
        return_value=Path(str(tmp_path / "backup.sqlite"))
    )
    monitor.backup_manager.cleanup_old_backups = MagicMock(return_value=[])
    monitor._notify_backup_success = AsyncMock()

    await monitor._run_daily_backup()

    monitor.backup_manager.create_backup.assert_called_once()
    monitor.backup_manager.cleanup_old_backups.assert_called_once()
    monitor._notify_backup_success.assert_awaited_once()

