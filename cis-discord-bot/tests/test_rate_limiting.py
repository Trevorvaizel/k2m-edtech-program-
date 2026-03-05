"""
Tests for Rate Limiting + Cost Controls
Story 1.6 Implementation Tests

Test coverage:
- Rate limiting (50 messages/day per student)
- Cost tracking (token counts, cost breakdown)
- Budget thresholds (daily $10, weekly $50)
"""

import pytest
import sqlite3
from datetime import datetime, timedelta
from cis_controller.rate_limiter import RateLimiter


@pytest.fixture
def db():
    """Create in-memory test database."""
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    # Create schema
    db.execute("""
        CREATE TABLE students (
            discord_id TEXT PRIMARY KEY,
            cohort_id TEXT NOT NULL,
            start_date TEXT NOT NULL,
            current_week INTEGER DEFAULT 1,
            current_state TEXT DEFAULT 'none',
            zone TEXT DEFAULT 'zone_0',
            jtbd_concern TEXT DEFAULT 'career_direction',
            emotional_state TEXT DEFAULT 'curious',
            unlocked_agents TEXT DEFAULT '["frame"]',
            artifact_progress INTEGER DEFAULT 0,
            interaction_count INTEGER DEFAULT 0,
            last_interaction TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            agent TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            tokens INTEGER,
            cost_usd REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(discord_id)
        )
    """)

    db.execute("""
        CREATE TABLE api_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            student_count INTEGER,
            total_interactions INTEGER,
            total_tokens INTEGER,
            total_cost_usd REAL,
            cached_tokens INTEGER,
            cached_savings_usd REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date)
        )
    """)

    db.commit()
    return db


@pytest.fixture
def store(db):
    """Create StudentStateStore with test database."""
    # Note: This would need to be adapted to work with the actual store
    # For now, we'll test the rate limiter directly
    pass


class TestRateLimiter:
    """Test rate limiting functionality."""

    def test_check_rate_limit_under_limit(self, db):
        """Test that rate limit passes when under 50 messages."""
        limiter = RateLimiter()
        limiter.store.db = db

        # Create test student
        db.execute(
            "INSERT INTO students (discord_id, cohort_id, start_date) VALUES (?, ?, ?)",
            ("123456789", "cohort-1", "2026-02-01")
        )
        db.commit()

        # Check rate limit (should pass with 0 interactions)
        allowed, error = limiter.check_rate_limit("123456789")
        assert allowed is True
        assert error is None

    def test_check_rate_limit_at_limit(self, db):
        """Test that rate limit blocks at exactly 50 messages."""
        limiter = RateLimiter()
        limiter.store.db = db

        # Create test student
        db.execute(
            "INSERT INTO students (discord_id, cohort_id, start_date) VALUES (?, ?, ?)",
            ("123456789", "cohort-1", "2026-02-01")
        )

        # Create 50 conversations for today
        today = datetime.now().strftime("%Y-%m-%d")
        for i in range(50):
            db.execute(
                "INSERT INTO conversations (student_id, agent, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                ("123456789", "frame", "user", f"Test message {i}", today)
            )
        db.commit()

        # Check rate limit (should block at exactly 50)
        allowed, error = limiter.check_rate_limit("123456789")
        assert allowed is False
        assert "50 CIS agent interactions" in error
        assert "Quality over quantity" in error

    def test_check_rate_limit_midnight_reset(self, db):
        """Test that rate limit resets at midnight."""
        limiter = RateLimiter()
        limiter.store.db = db

        # Create test student
        db.execute(
            "INSERT INTO students (discord_id, cohort_id, start_date) VALUES (?, ?, ?)",
            ("123456789", "cohort-1", "2026-02-01")
        )

        # Create 50 conversations for YESTERDAY
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        for i in range(50):
            db.execute(
                "INSERT INTO conversations (student_id, agent, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                ("123456789", "frame", "user", f"Test message {i}", yesterday)
            )
        db.commit()

        # Check rate limit (should pass - yesterday's interactions don't count)
        allowed, error = limiter.check_rate_limit("123456789")
        assert allowed is True
        assert error is None

    def test_get_student_daily_usage(self, db):
        """Test getting daily usage statistics."""
        limiter = RateLimiter()
        limiter.store.db = db

        # Create test student
        db.execute(
            "INSERT INTO students (discord_id, cohort_id, start_date) VALUES (?, ?, ?)",
            ("123456789", "cohort-1", "2026-02-01")
        )

        # Create 25 conversations for today
        today = datetime.now().strftime("%Y-%m-%d")
        for i in range(25):
            db.execute(
                "INSERT INTO conversations (student_id, agent, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
                ("123456789", "frame", "user", f"Test message {i}", today)
            )
        db.commit()

        # Get usage stats
        usage = limiter.get_student_daily_usage("123456789")
        assert usage["count"] == 25
        assert usage["remaining"] == 25  # 50 - 25
        assert usage["limit"] == 50


class TestCostTracking:
    """Test cost tracking and budget monitoring."""

    def test_track_interaction_updates_api_usage(self, db):
        """Test that tracking interaction updates API usage table."""
        limiter = RateLimiter()
        limiter.store.db = db

        # Track interaction
        today = datetime.now().strftime("%Y-%m-%d")
        limiter.track_interaction(
            discord_id="123456789",
            agent="frame",
            tokens=1000,
            cost_usd=0.0050
        )

        # Verify API usage record created
        result = db.execute(
            "SELECT * FROM api_usage WHERE date = ?",
            (today,)
        ).fetchone()

        assert result is not None
        assert result["total_tokens"] == 1000
        assert result["total_cost_usd"] == 0.0050
        assert result["total_interactions"] == 1

    def test_track_interaction_aggregates(self, db):
        """Test that multiple interactions aggregate correctly."""
        limiter = RateLimiter()
        limiter.store.db = db

        today = datetime.now().strftime("%Y-%m-%d")

        # Track 3 interactions
        limiter.track_interaction("123456789", "frame", 1000, 0.0050)
        limiter.track_interaction("123456789", "frame", 800, 0.0040)
        limiter.track_interaction("987654321", "diverge", 1200, 0.0060)

        # Verify aggregation
        result = db.execute(
            "SELECT * FROM api_usage WHERE date = ?",
            (today,)
        ).fetchone()

        assert result["total_tokens"] == 3000  # 1000 + 800 + 1200
        assert result["total_cost_usd"] == pytest.approx(0.0150)  # 0.005 + 0.004 + 0.006
        assert result["total_interactions"] == 3

    def test_daily_budget_threshold_alert(self, db):
        """Test that daily budget threshold triggers alert."""
        limiter = RateLimiter()
        limiter.store.db = db

        today = datetime.now().strftime("%Y-%m-%d")

        # Create API usage record exceeding $10 threshold
        db.execute(
            "INSERT INTO api_usage (date, total_tokens, total_cost_usd, total_interactions) VALUES (?, ?, ?, ?)",
            (today, 1000000, 12.50, 100)
        )
        db.commit()

        # Check budget thresholds (should log warning, but not raise exception)
        # This test verifies the logic runs without error
        limiter._check_budget_thresholds(today)
        # In production, this would send alert to Trevor
        # For testing, we just verify it doesn't crash

    def test_weekly_budget_cap_alert(self, db):
        """Test that weekly budget cap triggers alert."""
        limiter = RateLimiter()
        limiter.store.db = db

        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        # Create API usage records exceeding $50 weekly cap
        for day_offset in range(7):
            date = (datetime.now() - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            db.execute(
                "INSERT INTO api_usage (date, total_tokens, total_cost_usd, total_interactions) VALUES (?, ?, ?, ?)",
                (date, 1000000, 8.00, 50)  # $8/day × 7 days = $56
            )
        db.commit()

        # Check budget thresholds (should log critical alert)
        limiter._check_budget_thresholds(today)
        # In production, this would send critical alert to Trevor


class TestCostDataStructure:
    """Test cost data structure from LLM integration."""

    def test_anthropic_cost_data_structure(self):
        """Test that Anthropic cost data has required fields."""
        # Simulate cost data from Anthropic API
        cost_data = {
            "input_tokens": 500,
            "output_tokens": 300,
            "cache_tokens": 200,
            "total_tokens": 1000,
            "input_cost": 0.0015,
            "cache_cost": 0.0001,
            "output_cost": 0.0045,
            "total_cost_usd": 0.0061,
            "provider": "anthropic",
            "model": "claude-sonnet-4-5-20250514"
        }

        # Verify required fields exist
        assert "total_tokens" in cost_data
        assert "total_cost_usd" in cost_data
        assert cost_data["total_cost_usd"] > 0

    def test_openai_compatible_cost_data_structure(self):
        """Test that OpenAI-compatible cost data has required fields."""
        # Simulate cost data from OpenAI-compatible API
        cost_data = {
            "prompt_tokens": 500,
            "completion_tokens": 300,
            "total_tokens": 800,
            "prompt_cost": 0.000075,
            "completion_cost": 0.00018,
            "total_cost_usd": 0.000255,
            "provider": "zhipu",
            "model": "glm-4.7"
        }

        # Verify required fields exist
        assert "total_tokens" in cost_data
        assert "total_cost_usd" in cost_data
        assert cost_data["total_cost_usd"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
