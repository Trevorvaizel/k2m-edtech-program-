"""
Rate Limiting Module
Story 1.6 Implementation: Rate limiting + cost controls

This module implements per-student rate limiting for CIS agent interactions.
Prevents API abuse and manages Claude API costs effectively.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from database.store import StudentStateStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

store = StudentStateStore()


class RateLimiter:
    """
    Rate limiting for CIS agent interactions.

    Enforces:
    - 50 messages/day per student in #thinking-lab
    - Per-student API interaction limits
    - Daily budget tracking ($10 threshold alert)
    - Weekly budget cap ($50)
    """

    # Rate limits from Story 4.7 spec
    MAX_INTERACTIONS_PER_DAY = 50

    # Budget thresholds
    DAILY_BUDGET_ALERT = 10.00  # Alert Trevor when daily cost exceeds $10
    WEEKLY_BUDGET_CAP = 50.00   # Hard cap at $50/week

    def __init__(self):
        """Initialize rate limiter with database store."""
        self.store = store

    def check_rate_limit(self, discord_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if student has exceeded daily rate limit.

        Args:
            discord_id: Student's Discord ID

        Returns:
            (allowed: bool, error_message: Optional[str])
            - If allowed=True, student can proceed with interaction
            - If allowed=False, error_message contains user-friendly explanation
        """
        discord_id = str(discord_id)

        # Get today's interaction count
        today = datetime.now().strftime("%Y-%m-%d")
        count = self._get_daily_interaction_count(discord_id, today)

        if count >= self.MAX_INTERACTIONS_PER_DAY:
            logger.warning(f"Rate limit exceeded for {discord_id}: {count}/{self.MAX_INTERACTIONS_PER_DAY}")
            return False, (
                f"⏸️ **You've used {self.MAX_INTERACTIONS_PER_DAY} CIS agent interactions today.**\n\n"
                f"That's a lot of practice! Great work building your habits.\n\n"
                f"You can practice again tomorrow when the counter resets.\n\n"
                f"**Remember:** Quality over quantity. The habits you build today will be here tomorrow. 💪"
            )

        logger.info(f"Rate limit check passed for {discord_id}: {count}/{self.MAX_INTERACTIONS_PER_DAY}")
        return True, None

    def _get_daily_interaction_count(self, discord_id: str, date: str) -> int:
        """
        Get student's interaction count for a specific date.

        Args:
            discord_id: Student's Discord ID
            date: Date string (YYYY-MM-DD format)

        Returns:
            Number of interactions on that date
        """
        # Query conversations table for today's interactions
        query = """
            SELECT COUNT(*) as count
            FROM conversations
            WHERE student_id = ?
            AND DATE(created_at) = ?
        """

        result = self.store.db.execute(query, (discord_id, date)).fetchone()
        return result['count'] if result else 0

    def track_interaction(self, discord_id: str, agent: str, tokens: int, cost_usd: float):
        """
        Track interaction for rate limiting and cost monitoring.

        This is called AFTER a successful API interaction to:
        1. Increment daily interaction counter
        2. Track API usage costs
        3. Check budget thresholds
        4. Alert Trevor if needed

        Args:
            discord_id: Student's Discord ID
            agent: Which agent was used (frame, diverge, challenge, synthesize)
            tokens: Total tokens used (input + output)
            cost_usd: Cost in USD for this interaction
        """
        discord_id = str(discord_id)
        today = datetime.now().strftime("%Y-%m-%d")

        # Update daily usage stats
        self._update_api_usage(today, tokens, cost_usd)

        # Check budget thresholds
        self._check_budget_thresholds(today)

        logger.info(
            f"Tracked interaction for {discord_id}: agent={agent}, "
            f"tokens={tokens}, cost=${cost_usd:.4f}"
        )

    def _update_api_usage(self, date: str, tokens: int, cost_usd: float):
        """
        Update daily API usage statistics.

        Args:
            date: Date string (YYYY-MM-DD)
            tokens: Total tokens used
            cost_usd: Cost in USD
        """
        # Check if usage record exists for today
        existing = self.store.db.execute(
            "SELECT * FROM api_usage WHERE date = ?",
            (date,)
        ).fetchone()

        if existing:
            # Update existing record
            self.store.db.execute("""
                UPDATE api_usage
                SET total_tokens = total_tokens + ?,
                    total_cost_usd = total_cost_usd + ?,
                    total_interactions = total_interactions + 1
                WHERE date = ?
            """, (tokens, cost_usd, date))
        else:
            # Create new record
            self.store.db.execute("""
                INSERT INTO api_usage (
                    date, total_tokens, total_cost_usd, total_interactions
                ) VALUES (?, ?, ?, 1)
            """, (date, tokens, cost_usd))

        self.store.db.commit()

    def _check_budget_thresholds(self, date: str):
        """
        Check if daily/weekly budget thresholds are exceeded.

        Alerts Trevor if:
        - Daily cost exceeds $10 (warning threshold)
        - Weekly cost exceeds $50 (hard cap)

        Args:
            date: Date string (YYYY-MM-DD)
        """
        # Check daily budget
        daily_usage = self.store.db.execute(
            "SELECT total_cost_usd FROM api_usage WHERE date = ?",
            (date,)
        ).fetchone()

        if daily_usage and daily_usage['total_cost_usd'] > self.DAILY_BUDGET_ALERT:
            logger.warning(
                f"Daily budget alert: ${daily_usage['total_cost_usd']:.2f} "
                f"exceeds ${self.DAILY_BUDGET_ALERT}"
            )
            # TODO: Send alert to #facilitator-dashboard
            # This would be implemented in Task 1.7 (Observability)

        # Check weekly budget (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        weekly_usage = self.store.db.execute("""
            SELECT SUM(total_cost_usd) as weekly_total
            FROM api_usage
            WHERE date >= ? AND date <= ?
        """, (week_ago, date)).fetchone()

        if weekly_usage and weekly_usage['weekly_total'] > self.WEEKLY_BUDGET_CAP:
            logger.critical(
                f"Weekly budget cap exceeded: ${weekly_usage['weekly_total']:.2f} "
                f"exceeds ${self.WEEKLY_BUDGET_CAP}"
            )
            # TODO: Send critical alert to Trevor immediately
            # This would be implemented in Task 1.7 (Observability)

    def get_student_daily_usage(self, discord_id: str) -> Dict[str, int]:
        """
        Get student's daily usage statistics.

        Args:
            discord_id: Student's Discord ID

        Returns:
            Dict with 'count' and 'remaining' interactions
        """
        discord_id = str(discord_id)
        today = datetime.now().strftime("%Y-%m-%d")
        count = self._get_daily_interaction_count(discord_id, today)
        remaining = max(0, self.MAX_INTERACTIONS_PER_DAY - count)

        return {
            "count": count,
            "remaining": remaining,
            "limit": self.MAX_INTERACTIONS_PER_DAY
        }


# Singleton instance
rate_limiter = RateLimiter()
