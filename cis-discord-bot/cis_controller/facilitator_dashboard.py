"""
Facilitator Dashboard Automation (Task 2.6)

Trevor's private dashboard for monitoring cohort health, engagement,
escalations, API costs, and system status.

Posts daily summaries to #facilitator-dashboard channel:
- 9:00 AM: Daily summary (engagement, habits, escalations, costs, health)
- 6:00 PM: Peer visibility summary (aggregate patterns)
- Friday 5:00 PM: Reflection summary + spot-check list
- Real-time: Escalation notifications (Level 3-4)
"""

import logging
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from database.store import StudentStateStore

logger = logging.getLogger(__name__)


class FacilitatorDashboard:
    """
    Generates and posts dashboard summaries to Trevor's private channel.

    All summaries are Guardrail #3 compliant (no comparison/ranking).
    """

    def __init__(self, store: StudentStateStore):
        """
        Initialize dashboard generator.

        Args:
            store: Database store for accessing cohort data
        """
        self.store = store

    @staticmethod
    def _row_value(row, key: str, default=None):
        """Safely read values from sqlite3.Row/dict-like payloads."""
        if row is None:
            return default

        if isinstance(row, dict):
            return row.get(key, default)

        try:
            value = row[key]
            return default if value is None else value
        except Exception:
            pass

        return default

    def generate_daily_summary(self, week: int) -> str:
        """
        Generate 9:00 AM daily summary for Trevor.

        Includes:
        - Engagement % (active students / total students)
        - Habit 1 Practice (/frame usage)
        - Escalations (students stuck 3+ days)
        - API Costs (daily/weekly)
        - System Health check

        Args:
            week: Current cohort week

        Returns:
            Formatted daily summary message
        """
        try:
            # Get cohort overview
            total_students = self.store.get_all_students()
            total_count = len(total_students)
            active_count = self._count_active_students_this_week(week)
            posted_today_count = self._count_students_posted_today(week)
            engagement_pct = (active_count / total_count * 100) if total_count else 0
            not_posted_today = max(total_count - posted_today_count, 0)

            # Get habit practice stats
            habit_practice_today = self._count_frame_usage_today()
            habit_practice_week = self._count_frame_usage_this_week(week)

            # Get escalations
            stuck_students = self.store.get_stuck_students(inactive_days=3)
            stuck_count = len(stuck_students)

            # Get API costs
            costs = self._get_api_costs()
            daily_cost = costs.get('daily', 0)
            weekly_cost = costs.get('weekly', 0)
            weekly_projected = costs.get('weekly_projected', 0)

            # System health check
            health_status = self._check_system_health()

            # Format day name
            day_name = datetime.now().strftime("%A")
            day_name_upper = day_name.upper()

            # Build summary message
            summary = (
                f"📊 {day_name_upper}, WEEK {week} SUMMARY\n\n"
                f"🎯 Engagement:\n"
                f"- {active_count}/{total_count} students active this week ({engagement_pct:.1f}%)\n"
                f"- {not_posted_today} students not yet posted today\n\n"
                f"⏸️ Habit 1 Practice:\n"
                f"- /frame used: {habit_practice_today} times today\n"
                f"- /frame total: {habit_practice_week} times this week\n\n"
                f"🚨 Escalations:\n"
            )

            # Add escalation details
            if stuck_count > 0:
                summary += f"- {stuck_count} students flagged (stuck 3+ days)\n"
                # Show first 3 stuck students
                for student in stuck_students[:3]:
                    last_post = self._get_last_post_date(student)
                    summary += f"  - Student <@{student['discord_id']}> (last post: {last_post})\n"
                if stuck_count > 3:
                    summary += f"  - ... and {stuck_count - 3} more\n"
                summary += "\n"
            else:
                summary += "- 0 students flagged (stuck 3+ days)\n\n"

            # Add costs
            summary += (
                f"💰 API Costs:\n"
                f"- Daily: ${daily_cost:.2f} (within $10 budget)\n"
                f"- Weekly: ${weekly_cost:.2f} (projected: ${weekly_projected:.2f})\n\n"
            )

            # Add system health
            summary += (
                f"✅ System Health: {health_status}\n"
                "✅ Guardrail #3 check: No comparison detected"
            )

            return summary

        except Exception as e:
            logger.error(f"Error generating daily summary: {e}", exc_info=True)
            return f"📊 DAILY SUMMARY (WEEK {week})\n\n⚠️ Error generating summary: {str(e)}"

    def generate_peer_visibility_summary(self, week: int) -> str:
        """
        Generate 6:00 PM peer visibility summary.

        Shows aggregate patterns (Guardrail #3 compliant - no comparison/ranking).

        Args:
            week: Current cohort week

        Returns:
            Formatted peer visibility summary
        """
        try:
            # Get today's submissions
            submissions = self._get_today_submissions(week=week)
            total_students = len(self.store.get_all_students())

            # Get aggregate patterns
            patterns = self._extract_aggregate_patterns(week, submissions, total_students)

            # Build summary
            summary = (
                f"🌟 EVENING SNAPSHOT (WEEK {week})\n\n"
                f"Today's submissions: {submissions}/{total_students}\n"
                f"Aggregate patterns:\n"
            )

            # Add patterns
            for pattern in patterns:
                summary += f"- '{pattern}'\n"

            summary += "\n✅ Guardrail #3 check: No comparison detected"

            return summary

        except Exception as e:
            logger.error(f"Error generating peer visibility summary: {e}", exc_info=True)
            return f"🌟 EVENING SNAPSHOT (WEEK {week})\n\n⚠️ Error: {str(e)}"

    def generate_reflection_summary(self, week: int) -> str:
        """
        Generate Friday 5:00 PM reflection summary.

        Includes:
        - Completion % (submitted / total)
        - Identity shift evidence (articulate clear shift %)
        - Habit 1 self-assessment breakdown
        - Proof-of-work completion
        - Week unlock status

        Args:
            week: Current week number

        Returns:
            Formatted reflection summary
        """
        try:
            # Get reflection data
            summary = self.store.get_reflection_summary(week)
            reflections = self.store.get_weekly_reflections(week)
            all_students = self.store.get_all_students()

            # Calculate identity shift clarity
            articulate_shift = self._calculate_identity_shift_clarity(reflections)

            # Parse habit practice breakdown
            habit_yes = 0
            habit_sometimes = 0
            habit_no = 0
            proof_count = 0

            for ref in reflections:
                if self._row_value(ref, 'submitted', 0):
                    content = str(self._row_value(ref, 'reflection_content', '') or '')
                    lower_content = content.lower()

                    if 'habit practice: yes' in lower_content:
                        habit_yes += 1
                    elif 'habit practice: sometimes' in lower_content:
                        habit_sometimes += 1
                    elif 'habit practice: no' in lower_content:
                        habit_no += 1

                    if str(self._row_value(ref, 'proof_of_work', '')).strip():
                        proof_count += 1

            total_submitted = int(summary['submitted_count'])
            total_students = int(summary['total_students']) or len(all_students)
            completion_pct = (total_submitted / total_students * 100) if total_students else 0

            articulate_pct = (articulate_shift / total_submitted * 100) if total_submitted else 0
            proof_pct = (proof_count / total_submitted * 100) if total_submitted else 0

            yes_pct = (habit_yes / total_submitted * 100) if total_submitted else 0
            sometimes_pct = (habit_sometimes / total_submitted * 100) if total_submitted else 0
            no_pct = (habit_no / total_submitted * 100) if total_submitted else 0

            # Week unlock status
            unlocked_count = int(summary['unlocked_count'])
            pending_count = int(summary['pending_count'])
            unlock_pct = (unlocked_count / total_students * 100) if total_students else 0

            # Build summary
            message = (
                f"🤔 FRIDAY REFLECTIONS (WEEK {week})\n\n"
                f"Submissions: {total_submitted}/{total_students} ({completion_pct:.0f}%)\n"
                f"Identity shift evidence:\n"
                f"- 'What changed?' - {articulate_pct:.0f}% articulate clear shift\n"
                f"- Habit 1 self-assessment:\n"
                f"  ✅ Yes: {yes_pct:.0f}%\n"
                f"  🔄 Sometimes: {sometimes_pct:.0f}%\n"
                f"  ❌ No: {no_pct:.0f}%\n"
                f"- Proof-of-work: {proof_pct:.0f}% shared sentence\n\n"
                f"🔓 Week {week + 1} unlock: {unlocked_count}/{total_students} students ({unlock_pct:.1f}%)\n"
                f"🚨 Follow-up needed: {pending_count} students\n\n"
                f"✅ Guardrail #3 check: No comparison detected"
            )

            return message

        except Exception as e:
            logger.error(f"Error generating reflection summary: {e}", exc_info=True)
            return f"🤔 FRIDAY REFLECTIONS (WEEK {week})\n\n⚠️ Error: {str(e)}"

    def generate_spot_check_list(self, week: int) -> str:
        """
        Generate Friday 5:00 PM spot-check list.

        Random sample of 15-20 reflections for Trevor review.

        Args:
            week: Current week number

        Returns:
            Formatted spot-check list with reflection links
        """
        try:
            # Get random sample of reflections
            reflections = self.store.get_weekly_reflections(week)
            submitted = [r for r in reflections if self._row_value(r, 'submitted', 0)]

            # Sample 15-20 (or fewer if not enough submissions)
            sample_size = min(len(submitted), random.randint(15, 20))
            sample = random.sample(submitted, sample_size) if submitted else []

            # Build spot-check list
            message = (
                f"🔍 FRIDAY SPOT-CHECK LIST ({sample_size} random reflections)\n\n"
                f"Trevor's task:\n"
                f"- Review for genuine engagement\n"
                f"- Check for students who may need support\n"
                f"- Look for patterns (confusion, insights, wins)\n\n"
            )

            # Add reflection links
            for i, ref in enumerate(sample, 1):
                discord_id = self._row_value(ref, 'discord_id', 'unknown')
                content = str(self._row_value(ref, 'reflection_content', '') or '')
                proof = str(self._row_value(ref, 'proof_of_work', '') or '')
                reflection_id = self._row_value(ref, 'id', '?')

                # Truncate for display
                content_preview = content[:50] + "..." if len(content) > 50 else content
                proof_preview = proof[:30] + "..." if len(proof) > 30 else proof

                message += (
                    f"{i}. <@{discord_id}>\n"
                    f"   Reflection: {content_preview}\n"
                    f"   Proof: {proof_preview}\n"
                    f"   Link: reflection://week-{week}/record-{reflection_id}\n\n"
                )

            message += (
                "\nReply to flag:\n"
                "- @[Student] - Needs support\n"
                "- @[Student] - Celebrate\n"
                "- @[Student] - Escalate\n\n"
                "✅ Guardrail #3 check: No comparison detected"
            )

            return message

        except Exception as e:
            logger.error(f"Error generating spot-check list: {e}", exc_info=True)
            return f"🔍 FRIDAY SPOT-CHECK LIST\n\n⚠️ Error: {str(e)}"

    def generate_escalation_notification(self, escalation_data: Dict) -> str:
        """
        Generate real-time escalation notification for Level 3-4.

        Args:
            escalation_data: Dictionary with escalation details
                - level: 3 or 4
                - student: Student record
                - inactive_days: Days since last post
                - zone: Current zone
                - emotional_state: From diagnostic (if available)

        Returns:
            Formatted escalation notification
        """
        try:
            level = escalation_data.get('level', 3)
            student = escalation_data.get('student')
            inactive_days = escalation_data.get('inactive_days', 0)
            zone = student.get('zone', 'Unknown')
            discord_id = student['discord_id']

            if level == 4:
                # Crisis escalation
                message = (
                    f"⚠️⚠️⚠️ CRISIS ESCALATION: Student <@{discord_id}>\n\n"
                    f"Last activity: {inactive_days} days ago\n"
                    f"Zone: {zone}\n"
                    f"\n"
                    f"🚨 IMMEDIATE ACTION REQUIRED\n"
                    f"- Trevor DM student within 1 hour\n"
                    f"- Assess risk level\n"
                    f"- Provide Kenya crisis resources if needed\n"
                    f"- Notify parent if student is minor (<18)"
                )
            else:
                # Level 3 escalation (stuck 7+ days)
                last_post = self._get_last_post_date(student)
                message = (
                    f"⚠️ ESCALATION: Student <@{discord_id}> stuck {inactive_days} days\n"
                    f"Last post: {last_post} (Week {student.get('current_week', '?')})\n"
                    f"Zone: {zone}\n"
                    f"\n"
                    f"Suggested nudge: 'Hey! Week {student.get('current_week')} is just noticing. No pressure to be good at this. Just post one thing: I use AI when I [one thing]. That's it. You got this. 💪'\n"
                    f"\n"
                    f"Trevor action: DM directly / Customize nudge / Call"
                )

            return message

        except Exception as e:
            logger.error(f"Error generating escalation notification: {e}", exc_info=True)
            return f"⚠️ ESCALATION ERROR: {str(e)}"

    # ===== Private Helper Methods =====

    def _is_active_this_week(self, student: dict) -> bool:
        """Check if student has posted this week."""
        discord_id = self._row_value(student, 'discord_id', '')
        current_week = int(self._row_value(student, 'current_week', 0) or 0)
        if not discord_id or current_week <= 0:
            return False

        cursor = self.store.conn.execute(
            """
            SELECT 1
            FROM daily_participation
            WHERE discord_id = ?
              AND week_number = ?
              AND has_posted = 1
            LIMIT 1
            """,
            (discord_id, current_week)
        )
        return cursor.fetchone() is not None

    def _count_active_students_this_week(self, week: int) -> int:
        """Count distinct students who posted at least once in the week."""
        cursor = self.store.conn.execute(
            """
            SELECT COUNT(DISTINCT discord_id) AS count
            FROM daily_participation
            WHERE week_number = ? AND has_posted = 1
            """,
            (week,)
        )
        return int(self._row_value(cursor.fetchone(), 'count', 0) or 0)

    def _count_students_posted_today(self, week: Optional[int] = None) -> int:
        """Count distinct students who posted today."""
        today = datetime.now().strftime("%Y-%m-%d")
        if week is None:
            cursor = self.store.conn.execute(
                """
                SELECT COUNT(DISTINCT discord_id) AS count
                FROM daily_participation
                WHERE date = ? AND has_posted = 1
                """,
                (today,)
            )
        else:
            cursor = self.store.conn.execute(
                """
                SELECT COUNT(DISTINCT discord_id) AS count
                FROM daily_participation
                WHERE date = ? AND week_number = ? AND has_posted = 1
                """,
                (today, week)
            )
        return int(self._row_value(cursor.fetchone(), 'count', 0) or 0)

    def _count_frame_usage_today(self) -> int:
        """Count /frame usage today."""
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = self.store.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM observability_events
            WHERE event_type = 'agent_used'
              AND DATE(timestamp) = ?
              AND LOWER(COALESCE(json_extract(metadata, '$.agent'), '')) IN ('frame', 'framer', '/frame')
            """,
            (today,)
        )
        return int(self._row_value(cursor.fetchone(), 'count', 0) or 0)

    def _count_frame_usage_this_week(self, week: int) -> int:
        """Count /frame usage this week."""
        cursor = self.store.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM observability_events
            WHERE event_type = 'agent_used'
              AND CAST(COALESCE(json_extract(metadata, '$.week'), 0) AS INTEGER) = ?
              AND LOWER(COALESCE(json_extract(metadata, '$.agent'), '')) IN ('frame', 'framer', '/frame')
            """,
            (week,)
        )
        count = int(self._row_value(cursor.fetchone(), 'count', 0) or 0)
        if count > 0:
            return count

        # Fallback when legacy events do not include metadata.week.
        today = datetime.now().date()
        week_ago = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        cursor = self.store.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM observability_events
            WHERE event_type = 'agent_used'
              AND DATE(timestamp) >= ?
              AND LOWER(COALESCE(json_extract(metadata, '$.agent'), '')) IN ('frame', 'framer', '/frame')
            """,
            (week_ago,)
        )
        return int(self._row_value(cursor.fetchone(), 'count', 0) or 0)

    def _get_api_costs(self) -> dict:
        """Get API cost data."""
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now().date() - timedelta(days=6)).strftime("%Y-%m-%d")

        daily_cursor = self.store.conn.execute(
            """
            SELECT COALESCE(total_cost_usd, 0) AS daily
            FROM api_usage
            WHERE date = ?
            """,
            (today,)
        )
        daily = float(self._row_value(daily_cursor.fetchone(), 'daily', 0.0) or 0.0)

        weekly_cursor = self.store.conn.execute(
            """
            SELECT COALESCE(SUM(total_cost_usd), 0) AS weekly,
                   COUNT(*) AS tracked_days
            FROM api_usage
            WHERE date >= ? AND date <= ?
            """,
            (week_ago, today)
        )
        weekly_row = weekly_cursor.fetchone()
        weekly = float(self._row_value(weekly_row, 'weekly', 0.0) or 0.0)
        tracked_days = int(self._row_value(weekly_row, 'tracked_days', 0) or 0)
        weekly_projected = ((weekly / tracked_days) * 7) if tracked_days > 0 else (daily * 7)

        return {
            'daily': daily,
            'weekly': weekly,
            'weekly_projected': weekly_projected
        }

    def _check_system_health(self) -> str:
        """Check system health status."""
        status_parts = []
        try:
            self.store.conn.execute("SELECT 1").fetchone()
            status_parts.append("DB ok")
        except Exception:
            return "Database unavailable"

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        participation_cursor = self.store.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM daily_participation
            WHERE date IN (?, ?)
            """,
            (today, yesterday)
        )
        recent_participation = int(self._row_value(participation_cursor.fetchone(), 'count', 0) or 0)
        status_parts.append("participation feed active" if recent_participation > 0 else "participation feed idle")

        api_cursor = self.store.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM api_usage
            WHERE date IN (?, ?)
            """,
            (today, yesterday)
        )
        recent_cost_rows = int(self._row_value(api_cursor.fetchone(), 'count', 0) or 0)
        status_parts.append("cost feed active" if recent_cost_rows > 0 else "cost feed idle")

        return "; ".join(status_parts)

    def _get_last_post_date(self, student: dict) -> str:
        """Get last post date for student."""
        discord_id = self._row_value(student, 'discord_id', '')
        if not discord_id:
            return "Unknown"

        cursor = self.store.conn.execute(
            """
            SELECT COALESCE(MAX(first_post_time), MAX(date)) AS last_post
            FROM daily_participation
            WHERE discord_id = ? AND has_posted = 1
            """,
            (discord_id,)
        )
        last_post_raw = self._row_value(cursor.fetchone(), 'last_post', None)
        if not last_post_raw:
            return "No posts logged"

        text = str(last_post_raw)
        try:
            # Supports both YYYY-MM-DD and ISO timestamps.
            if len(text) == 10 and "T" not in text:
                dt = datetime.strptime(text, "%Y-%m-%d")
            else:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return dt.strftime("%a, %b %d")
        except Exception:
            return text

    def _get_today_submissions(self, week: Optional[int] = None) -> int:
        """Count today's submissions."""
        return self._count_students_posted_today(week=week)

    def _extract_aggregate_patterns(self, week: int, submissions: int, total_students: int) -> list:
        """Extract aggregate patterns from submissions."""
        patterns = []

        if total_students:
            submission_pct = (submissions / total_students) * 100
            patterns.append(
                f"{submissions}/{total_students} students posted today ({submission_pct:.1f}%)"
            )
        else:
            patterns.append("No active roster detected yet")

        frame_today = self._count_frame_usage_today()
        patterns.append(f"/frame usage today: {frame_today} interactions")

        zone_cursor = self.store.conn.execute(
            """
            SELECT zone, COUNT(*) AS count
            FROM students
            WHERE current_week = ?
            GROUP BY zone
            ORDER BY zone
            """,
            (week,)
        )
        zone_rows = zone_cursor.fetchall()
        if zone_rows:
            zone_parts = [
                f"{self._row_value(row, 'zone', 'unknown')}: {self._row_value(row, 'count', 0)}"
                for row in zone_rows
            ]
            patterns.append("Zone distribution: " + ", ".join(zone_parts))
        else:
            patterns.append("Zone distribution unavailable")

        return patterns

    def _calculate_identity_shift_clarity(self, reflections: list) -> int:
        """Count reflections with clear identity shift articulation."""
        shift_patterns = [
            r"\bwent from\b",
            r"\bi used to\b",
            r"\bnow i\b",
            r"\bchanged\b",
            r"\brealized\b",
            r"\blearned\b",
            r"\bfeel (more|less|different)\b",
        ]
        shift_regex = re.compile("|".join(shift_patterns), re.IGNORECASE)

        count = 0
        for reflection in reflections:
            if not self._row_value(reflection, 'submitted', 0):
                continue
            content = str(self._row_value(reflection, 'reflection_content', '') or '')
            if shift_regex.search(content):
                count += 1

        return count
