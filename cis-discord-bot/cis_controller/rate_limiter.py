"""
Rate Limiting Module
Story 1.6 Implementation: rate limiting + cost controls
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from database import get_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

store = get_store()


class RateLimiter:
    """
    Rate limiting for CIS agent interactions.

    Enforces:
    - 50 interactions/day per student
    - Daily budget tracking ($10 threshold)
    - Weekly budget cap ($50 hard cap)
    """

    def __init__(self):
        self.store = store
        self.MAX_INTERACTIONS_PER_DAY = int(
            os.getenv("MAX_INTERACTIONS_PER_DAY", "50")
        )
        self.DAILY_BUDGET_ALERT = float(os.getenv("DAILY_BUDGET_ALERT", "10.00"))
        self.WEEKLY_BUDGET_CAP = float(os.getenv("WEEKLY_BUDGET_CAP", "50.00"))

        # Best-effort anti-spam guards for notifications.
        self._daily_alert_sent = set()
        self._weekly_alert_sent = set()

    def _get_connection(self):
        conn = getattr(self.store, "conn", None) or getattr(self.store, "db", None)
        if conn is None:
            raise RuntimeError("RateLimiter store has no active database connection.")
        return conn

    @staticmethod
    def _row_value(row, key: str, fallback_index: int = 0):
        if row is None:
            return None

        try:
            return row[key]
        except Exception:
            pass

        try:
            return row[fallback_index]
        except Exception:
            return None

    def check_rate_limit(self, discord_id: str) -> Tuple[bool, Optional[str]]:
        """
        Check if student can proceed with an interaction.

        Returns:
            (allowed, error_message)
        """
        discord_id = str(discord_id)
        today = datetime.now().strftime("%Y-%m-%d")

        if self._is_weekly_budget_exceeded(today):
            weekly_total = self._get_weekly_total_cost(today)
            return False, (
                "ðŸ’° **CIS interactions are temporarily paused.**\n\n"
                f"The weekly cohort budget cap (${self.WEEKLY_BUDGET_CAP:.2f}) has been reached "
                f"(current: ${weekly_total:.2f}).\n\n"
                "Trevor has been notified. Please continue practicing the 4 Habits manually for now."
            )

        count = self._get_daily_interaction_count(discord_id, today)
        if count >= self.MAX_INTERACTIONS_PER_DAY:
            logger.warning(
                "Rate limit exceeded for %s: %s/%s",
                discord_id,
                count,
                self.MAX_INTERACTIONS_PER_DAY,
            )
            return False, (
                f"â¸ï¸ **You've used {self.MAX_INTERACTIONS_PER_DAY} CIS agent interactions today.**\n\n"
                "That's a lot of practice! Great work building your habits.\n\n"
                "You can practice again tomorrow when the counter resets.\n\n"
                "**Remember:** Quality over quantity. The habits you build today will be here tomorrow."
            )

        logger.info(
            "Rate limit check passed for %s: %s/%s",
            discord_id,
            count,
            self.MAX_INTERACTIONS_PER_DAY,
        )
        return True, None

    def _get_daily_interaction_count(self, discord_id: str, date: str) -> int:
        """
        Count student-authored interactions for the day.
        """
        conn = self._get_connection()
        query = """
            SELECT COUNT(*) as count
            FROM conversations
            WHERE student_id = ?
            AND role = 'user'
            AND DATE(created_at) = ?
        """
        row = conn.execute(query, (discord_id, date)).fetchone()
        value = self._row_value(row, "count", 0)
        return int(value or 0)

    def track_interaction(
        self, discord_id: str, agent: str, tokens: int, cost_usd: float
    ) -> Dict[str, float]:
        """
        Track successful interaction cost and return budget state.
        """
        discord_id = str(discord_id)
        today = datetime.now().strftime("%Y-%m-%d")

        self._update_api_usage(today, tokens, cost_usd)
        budget_state = self._check_budget_thresholds(today)

        logger.info(
            "Tracked interaction for %s: agent=%s tokens=%s cost=$%.4f",
            discord_id,
            agent,
            tokens,
            cost_usd,
        )
        return budget_state

    def _update_api_usage(self, date: str, tokens: int, cost_usd: float):
        conn = self._get_connection()
        existing = conn.execute(
            "SELECT id FROM api_usage WHERE date = ?",
            (date,),
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE api_usage
                SET total_tokens = COALESCE(total_tokens, 0) + ?,
                    total_cost_usd = COALESCE(total_cost_usd, 0) + ?,
                    total_interactions = COALESCE(total_interactions, 0) + 1
                WHERE date = ?
                """,
                (tokens, cost_usd, date),
            )
        else:
            conn.execute(
                """
                INSERT INTO api_usage (
                    date, total_tokens, total_cost_usd, total_interactions
                ) VALUES (?, ?, ?, 1)
                """,
                (date, tokens, cost_usd),
            )

        conn.commit()

    def _get_daily_total_cost(self, date: str) -> float:
        conn = self._get_connection()
        row = conn.execute(
            "SELECT COALESCE(total_cost_usd, 0) as daily_total FROM api_usage WHERE date = ?",
            (date,),
        ).fetchone()
        value = self._row_value(row, "daily_total", 0)
        return float(value or 0.0)

    def _get_weekly_total_cost(self, date: str) -> float:
        conn = self._get_connection()
        anchor = datetime.strptime(date, "%Y-%m-%d")
        week_ago = (anchor - timedelta(days=7)).strftime("%Y-%m-%d")
        row = conn.execute(
            """
            SELECT COALESCE(SUM(total_cost_usd), 0) as weekly_total
            FROM api_usage
            WHERE date >= ? AND date <= ?
            """,
            (week_ago, date),
        ).fetchone()
        value = self._row_value(row, "weekly_total", 0)
        return float(value or 0.0)

    def _week_window_key(self, date: str) -> str:
        anchor = datetime.strptime(date, "%Y-%m-%d")
        week_start = (anchor - timedelta(days=7)).strftime("%Y-%m-%d")
        week_end = anchor.strftime("%Y-%m-%d")
        return f"{week_start}:{week_end}"

    def _check_budget_thresholds(self, date: str) -> Dict[str, float]:
        """
        Compute current budget state and alert trigger booleans.
        """
        daily_total = self._get_daily_total_cost(date)
        weekly_total = self._get_weekly_total_cost(date)

        daily_alert_triggered = False
        if daily_total > self.DAILY_BUDGET_ALERT and date not in self._daily_alert_sent:
            self._daily_alert_sent.add(date)
            daily_alert_triggered = True
            logger.warning(
                "Daily budget alert: $%.2f exceeds $%.2f",
                daily_total,
                self.DAILY_BUDGET_ALERT,
            )

        weekly_cap_exceeded = weekly_total > self.WEEKLY_BUDGET_CAP
        weekly_alert_triggered = False
        week_key = self._week_window_key(date)
        if weekly_cap_exceeded and week_key not in self._weekly_alert_sent:
            self._weekly_alert_sent.add(week_key)
            weekly_alert_triggered = True
            logger.critical(
                "Weekly budget cap exceeded: $%.2f exceeds $%.2f",
                weekly_total,
                self.WEEKLY_BUDGET_CAP,
            )

        return {
            "daily_total": daily_total,
            "weekly_total": weekly_total,
            "daily_alert_triggered": daily_alert_triggered,
            "weekly_alert_triggered": weekly_alert_triggered,
            "weekly_cap_exceeded": weekly_cap_exceeded,
        }

    def _is_weekly_budget_exceeded(self, date: str) -> bool:
        # Hard cap: block new interactions once cap is reached.
        return self._get_weekly_total_cost(date) >= self.WEEKLY_BUDGET_CAP

    def get_student_daily_usage(self, discord_id: str) -> Dict[str, int]:
        discord_id = str(discord_id)
        today = datetime.now().strftime("%Y-%m-%d")
        count = self._get_daily_interaction_count(discord_id, today)
        remaining = max(0, self.MAX_INTERACTIONS_PER_DAY - count)

        return {
            "count": count,
            "remaining": remaining,
            "limit": self.MAX_INTERACTIONS_PER_DAY,
        }


rate_limiter = RateLimiter()


