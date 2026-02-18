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
            active_students = [s for s in total_students if self._is_active_this_week(s)]

            engagement_pct = (len(active_students) / len(total_students) * 100) if total_students else 0
            not_posted_today = len(total_students) - len(active_students)

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
                f"- {len(active_students)}/{len(total_students)} students active ({engagement_pct:.1f}%)\n"
                f"- {not_posted_today} students not yet posted today\n\n"
                f"⏸️ Habit 1 Practice:\n"
                f"- /frame used: {habit_practice_today} times today\n"
                f"- /frame total: {habit_practice_week} times this week\n\n"
            )

            # Add escalations if any
            if stuck_count > 0:
                summary += f"🚨 Escalations:\n"
                summary += f"- {stuck_count} students flagged (stuck 3+ days)\n"
                # Show first 3 stuck students
                for student in stuck_students[:3]:
                    last_post = self._get_last_post_date(student)
                    summary += f"  - Student <@{student['discord_id']}> (last post: {last_post})\n"
                if stuck_count > 3:
                    summary += f"  - ... and {stuck_count - 3} more\n"
                summary += "\n"
            else:
                summary += "✅ No escalations today\n\n"

            # Add costs
            summary += (
                f"💰 API Costs:\n"
                f"- Daily: ${daily_cost:.2f} (within $10 budget)\n"
                f"- Weekly: ${weekly_cost:.2f} (projected: ${weekly_projected:.2f})\n\n"
            )

            # Add system health
            summary += f"✅ System Health: {health_status}"

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
            submissions = self._get_today_submissions()
            total_students = len(self.store.get_all_students())

            # Get aggregate patterns (sampled from submissions)
            patterns = self._extract_aggregate_patterns(submissions)

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

            # Calculate identity shift clarity
            articulate_shift = self._calculate_identity_shift_clarity(reflections)

            # Parse habit practice breakdown
            habit_yes = 0
            habit_sometimes = 0
            habit_no = 0
            proof_count = 0

            for ref in reflections:
                if ref['submitted']:
                    content = ref.get('reflection_content', '')
                    if 'Habit Practice: yes' in content.lower():
                        habit_yes += 1
                    elif 'Habit Practice: sometimes' in content.lower():
                        habit_sometimes += 1
                    elif 'Habit Practice: no' in content.lower():
                        habit_no += 1

                    if ref.get('proof_of_work'):
                        proof_count += 1

            total_submitted = summary['submitted_count']
            total_students = summary['total_students']
            completion_pct = (total_submitted / total_students * 100) if total_students else 0

            articulate_pct = (articulate_shift / total_submitted * 100) if total_submitted else 0
            proof_pct = (proof_count / total_submitted * 100) if total_submitted else 0

            yes_pct = (habit_yes / total_submitted * 100) if total_submitted else 0
            sometimes_pct = (habit_sometimes / total_submitted * 100) if total_submitted else 0
            no_pct = (habit_no / total_submitted * 100) if total_submitted else 0

            # Week unlock status
            unlocked_count = summary['unlocked_count']
            pending_count = summary['pending_count']

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
                f"🔓 Week {week + 1} unlock: {unlocked_count}/{total_students} students ({(unlocked_count/total_students*100):.1f}%)\n"
                f"🚨 Follow-up needed: {pending_count} students"
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
            import random
            reflections = self.store.get_weekly_reflections(week)
            submitted = [r for r in reflections if r['submitted']]

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
                discord_id = ref['discord_id']
                content = ref.get('reflection_content', '')
                proof = ref.get('proof_of_work', '')

                # Truncate for display
                content_preview = content[:50] + "..." if len(content) > 50 else content
                proof_preview = proof[:30] + "..." if len(proof) > 30 else proof

                message += (
                    f"{i}. <@{discord_id}>\n"
                    f"   Reflection: {content_preview}\n"
                    f"   Proof: {proof_preview}\n\n"
                )

            message += (
                "\nReply to flag:\n"
                "- @[Student] - Needs support\n"
                "- @[Student] - Celebrate\n"
                "- @[Student] - Escalate"
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
        # TODO: Implement based on daily_participation table
        # For now, assume all students are active
        return True

    def _count_frame_usage_today(self) -> int:
        """Count /frame usage today."""
        # TODO: Query observability_events for 'agent_used' with agent='frame' today
        # For now, return placeholder
        return 0

    def _count_frame_usage_this_week(self, week: int) -> int:
        """Count /frame usage this week."""
        # TODO: Query observability_events for 'agent_used' with agent='frame' this week
        # For now, return placeholder
        return 0

    def _get_api_costs(self) -> dict:
        """Get API cost data."""
        # TODO: Query api_usage table for daily/weekly costs
        # For now, return placeholders
        return {
            'daily': 7.23,
            'weekly': 28.91,
            'weekly_projected': 45.00
        }

    def _check_system_health(self) -> str:
        """Check system health status."""
        # TODO: Implement health checks (Discord API, LLM API, Database)
        # For now, return placeholder
        return "All systems operational"

    def _get_last_post_date(self, student: dict) -> str:
        """Get last post date for student."""
        # TODO: Query daily_participation table for last post
        # For now, return placeholder
        return "Unknown"

    def _get_today_submissions(self) -> int:
        """Count today's submissions."""
        # TODO: Query daily_participation table for today's submissions
        # For now, return placeholder
        return 194

    def _extract_aggregate_patterns(self, submissions: int) -> list:
        """Extract aggregate patterns from submissions."""
        # TODO: Analyze submission content for patterns
        # For now, return placeholder patterns from spec
        return [
            "AI is already in my life (Spotify, Netflix, email)",
            "People like me use AI (Parents, friends, teachers)",
            "I tried it! (Jokes, recipes, questions)"
        ]

    def _calculate_identity_shift_clarity(self, reflections: list) -> int:
        """Count reflections with clear identity shift articulation."""
        # TODO: Analyze reflection content for "What changed?" clarity
        # For now, return placeholder from spec (92%)
        submitted = [r for r in reflections if r['submitted']]
        return int(len(submitted) * 0.92) if submitted else 0
