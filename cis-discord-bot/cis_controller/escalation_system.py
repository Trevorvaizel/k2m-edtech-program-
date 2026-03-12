"""
Escalation System
Story 2.4 Implementation: 4-Level Escalation System

Implements Trevor's 10% escalation workflow per Story 5.1 and escalation-playbook-v1.md.
Monitors student participation and triggers appropriate interventions based on stuckness patterns.

Escalation Levels:
- Level 1 (Yellow): Bot auto-nudge after 1 day no post
- Level 2 (Orange): Trevor alert after 3+ days stuck (notification in #facilitator-dashboard)
- Level 3 (Red): Trevor DM after 7+ days stuck
- Level 4 (Crisis): Instant Trevor DM for mental health emergency (from SafetyFilter)
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import discord
from discord.ext import commands

import pytz

from cis_controller.llm_integration import get_context_engine_intervention
from database.store import StudentStateStore

logger = logging.getLogger(__name__)

# Timezone
EAT = pytz.timezone('Africa/Nairobi')

# Escalation levels (from escalation-playbook-v1.md)
LEVEL_1_YELLOW = 1  # Bot handles (automated nudge)
LEVEL_2_ORANGE = 2  # Trevor monitors (dashboard notification)
LEVEL_3_RED = 3     # Trevor intervenes (direct DM)
LEVEL_4_CRISIS = 4  # Emergency intervention (instant Trevor DM + resources)

LOW_ENGAGEMENT_THRESHOLD = 2
LOW_ENGAGEMENT_LOOKBACK_DAYS = 2
DEFAULT_INTERVENTION_BY_BARRIER = {
    "identity": (
        "You belong in this room. Start with one real question from your day and run /frame."
    ),
    "time": (
        "Use a 10-minute sprint: one /frame pass on the decision already in front of you."
    ),
    "relevance": (
        "Pick one live work/school problem and test it with /diverge before deciding anything."
    ),
    "technical": (
        "Keep it simple: describe your situation in plain words and let KIRA handle the structure."
    ),
}


class EscalationSystem:
    """
    4-level escalation system for student stuckness patterns.

    Responsibilities:
    - Track student inactive days (Level 1-3 triggers)
    - Send Level 1 bot nudges (1 day no post)
    - Post Level 2 alerts to #facilitator-dashboard (3+ days stuck)
    - Send Level 3 Trevor DMs (7+ days stuck)
    - Log Level 4 crisis escalations (from SafetyFilter)
    - Log all escalations to #moderation-logs
    """

    def __init__(
        self,
        bot: commands.Bot,
        store: StudentStateStore,
        facilitator_dashboard_id: int,
        moderation_logs_id: int,
        trevor_discord_id: str
    ):
        """
        Initialize the escalation system.

        Args:
            bot: Discord bot instance
            store: StudentStateStore instance
            facilitator_dashboard_id: Channel ID for #facilitator-dashboard
            moderation_logs_id: Channel ID for #moderation-logs
            trevor_discord_id: Trevor's Discord user ID (as string)
        """
        self.bot = bot
        self.store = store
        self.facilitator_dashboard_id = facilitator_dashboard_id
        self.moderation_logs_id = moderation_logs_id
        self.trevor_discord_id = trevor_discord_id

        logger.info("Escalation system initialized")

    async def check_escalations(self, current_week: int):
        """
        Check all students for escalation triggers.

        Called daily by background scheduler.
        Checks for:
        - Level 1: 1 day no post (bot nudge)
        - Level 2: 3+ days no post (Trevor dashboard alert)
        - Level 3: 7+ days no post (Trevor DM)

        Args:
            current_week: Current cohort week (1-8)
        """
        logger.info(f"Checking escalations for week {current_week}")

        try:
            conn = self.store.conn
            cursor = conn.cursor()

            # Get all students in current cohort
            cursor.execute(
                """
                SELECT s.discord_id, s.zone, s.emotional_state
                FROM students s
                WHERE s.current_week = ?
                """,
                (current_week,)
            )
            students = cursor.fetchall()

            for discord_id, zone, emotional_state in students:
                username = self._student_label(discord_id)
                await self._check_student_escalation(
                    discord_id, username, zone, emotional_state, current_week
                )

        except Exception as e:
            logger.error(f"Error checking escalations: {e}", exc_info=True)

    def _student_label(self, discord_id: str) -> str:
        """
        Build a stable student identifier for human-facing escalation messages.

        We only persist Discord IDs in the current students schema, so use
        mention format as the canonical label.
        """
        return f"<@{discord_id}>"

    async def _check_student_escalation(
        self,
        discord_id: str,
        username: str,
        zone: str,
        emotional_state: str,
        current_week: int
    ):
        """
        Check a single student for escalation triggers and take appropriate action.

        Args:
            discord_id: Student's Discord ID (as string)
            username: Student's username
            zone: Student's current zone
            emotional_state: Student's current emotional state
            current_week: Current cohort week
        """
        try:
            # Get last post date from daily_participation
            conn = self.store.conn
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    MAX(CASE WHEN has_posted = 1 THEN date END) as last_post_date,
                    SUM(CASE WHEN has_posted = 1 THEN 1 ELSE 0 END) as total_posts
                FROM daily_participation
                WHERE discord_id = ?
                """,
                (discord_id,)
            )
            result = cursor.fetchone()
            last_post_date = result[0] if result and result[0] else None

            # Calculate days since last post
            now = datetime.now(EAT)
            if last_post_date:
                last_post = EAT.localize(datetime.strptime(last_post_date, "%Y-%m-%d"))
                days_since_post = max((now - last_post).days, 0)
            else:
                # Student has never posted. Use join date instead of nudge-only
                # activity rows, which are not real posts.
                cursor.execute(
                    "SELECT created_at FROM students WHERE discord_id = ?",
                    (discord_id,),
                )
                student_row = cursor.fetchone()
                created_at_raw = student_row[0] if student_row and student_row[0] else None
                if not created_at_raw:
                    return

                try:
                    joined_at = datetime.fromisoformat(str(created_at_raw).replace("Z", "+00:00"))
                except ValueError:
                    joined_at = datetime.strptime(str(created_at_raw)[:10], "%Y-%m-%d")

                if joined_at.tzinfo is None:
                    joined_at = EAT.localize(joined_at)
                else:
                    joined_at = joined_at.astimezone(EAT)

                days_since_post = max((now - joined_at).days, 0)

            # Skip brand-new students (joined today, hasn't had chance to post yet)
            if days_since_post <= 0:
                return

            # Check escalation triggers
            escalation_triggered = False

            # Level 1: 1 day no post (bot nudge) - handled by ParticipationTracker
            # This is already done in participation_tracker.py:check_inactive_students()

            low_engagement_signal, latest_engagement_score = self._detect_low_engagement_signal(
                discord_id=discord_id
            )
            level_2_trigger_reason = None
            if days_since_post >= 3:
                level_2_trigger_reason = "missed_3_days"
            elif low_engagement_signal:
                level_2_trigger_reason = "low_engagement_signal"

            # Task 6.4: Personalized barrier-type intervention before Trevor alert.
            if level_2_trigger_reason:
                if not await self._was_recently_escalated(discord_id, LEVEL_2_ORANGE, days=7):
                    await self._send_barrier_intervention_dm(
                        discord_id=discord_id,
                        username=username,
                        current_week=current_week,
                        trigger_reason=level_2_trigger_reason,
                        days_since_post=days_since_post,
                        engagement_score=latest_engagement_score,
                    )
                    await self._escalate_level_2(
                        discord_id,
                        username,
                        days_since_post,
                        zone,
                        emotional_state,
                        trigger_reason=level_2_trigger_reason,
                        engagement_score=latest_engagement_score,
                    )
                    escalation_triggered = True

            # Level 3: 7+ days no post (Trevor DM)
            if days_since_post >= 7:
                # Check if we already escalated this student recently
                if not await self._was_recently_escalated(discord_id, LEVEL_3_RED, days=14):
                    await self._escalate_level_3(
                        discord_id, username, days_since_post, zone, emotional_state
                    )
                    escalation_triggered = True

            if escalation_triggered:
                logger.info(f"Escalation triggered for {username}: {days_since_post} days since last post")

        except Exception as e:
            logger.error(f"Error checking student escalation for {username}: {e}", exc_info=True)

    def _detect_low_engagement_signal(self, discord_id: str) -> Tuple[bool, Optional[int]]:
        """
        Task 6.4 trigger: recent low-quality participation should route intervention.

        Low engagement signal:
        - latest posting record within LOW_ENGAGEMENT_LOOKBACK_DAYS
        - engagement_score <= LOW_ENGAGEMENT_THRESHOLD
        """
        try:
            cursor = self.store.conn.cursor()
            cursor.execute(
                """
                SELECT date, engagement_score
                FROM daily_participation
                WHERE discord_id = ? AND has_posted = 1
                ORDER BY date DESC
                LIMIT 1
                """,
                (discord_id,),
            )
            row = cursor.fetchone()
            if not row:
                return False, None

            if isinstance(row, dict):
                date_raw = row.get("date")
                engagement_score_raw = row.get("engagement_score")
            else:
                date_raw = row[0]
                engagement_score_raw = row[1]
            if not date_raw:
                return False, None

            last_post = EAT.localize(datetime.strptime(str(date_raw), "%Y-%m-%d"))
            days_since = max((datetime.now(EAT) - last_post).days, 0)
            if days_since > LOW_ENGAGEMENT_LOOKBACK_DAYS:
                return False, None

            engagement_score = int(engagement_score_raw or 0)
            return engagement_score <= LOW_ENGAGEMENT_THRESHOLD, engagement_score
        except Exception as exc:
            logger.error("Error detecting low engagement signal for %s: %s", discord_id, exc)
            return False, None

    async def _send_barrier_intervention_dm(
        self,
        discord_id: str,
        username: str,
        current_week: int,
        trigger_reason: str,
        days_since_post: int,
        engagement_score: Optional[int],
    ) -> None:
        """
        Send personalized barrier-type intervention DM (task 6.4).
        """
        if not str(discord_id).isdigit():
            logger.info("Skipping barrier intervention DM for unlinked user id: %s", discord_id)
            return

        intervention_payload = await get_context_engine_intervention(
            discord_id=discord_id,
            current_week=current_week,
        )
        profile = intervention_payload.get("profile") or {}
        first_name = str(profile.get("first_name") or "").strip()
        profession = str(intervention_payload.get("profession") or "student").strip()
        barrier_type = str(intervention_payload.get("barrier_type") or "general").strip().lower()
        intervention_text = str(intervention_payload.get("intervention_text") or "").strip()
        if not intervention_text:
            intervention_text = DEFAULT_INTERVENTION_BY_BARRIER.get(
                barrier_type,
                "Take one small next step today: run /frame on the question already on your desk.",
            )

        reason_line = (
            f"I noticed a low-engagement signal (score {engagement_score}/6)."
            if trigger_reason == "low_engagement_signal"
            else f"I noticed you've been quiet for {days_since_post} days."
        )

        try:
            student_user = await self.bot.fetch_user(int(discord_id))
            salutation = first_name or username
            dm_text = (
                f"Hey {salutation}, quick check-in from KIRA.\n\n"
                f"{reason_line}\n"
                f"For your **{profession}** context, I'm using the **{barrier_type}** support track this week.\n\n"
                f"{intervention_text}\n\n"
                "Reply here if you want me to break this into one tiny first step."
            )
            await student_user.send(dm_text)
        except Exception as exc:
            logger.error("Failed to send barrier intervention DM to %s: %s", discord_id, exc)
            return

        try:
            self.store.log_observability_event(
                discord_id=discord_id,
                event_type="barrier_intervention_sent",
                metadata={
                    "barrier_type": barrier_type or "unknown",
                    "profession": profession,
                    "week": current_week,
                    "trigger_reason": trigger_reason,
                    "engagement_score": engagement_score,
                    "days_since_post": days_since_post,
                },
            )
        except Exception as exc:
            logger.error(
                "Failed logging barrier intervention observability event for %s: %s",
                discord_id,
                exc,
            )

    async def _was_recently_escalated(self, discord_id: str, level: int, days: int = 7) -> bool:
        """
        Check if student was recently escalated at this level (to avoid spamming Trevor).

        Args:
            discord_id: Student's Discord ID (as string)
            level: Escalation level to check
            days: Lookback period in days

        Returns:
            True if escalated within lookback period, False otherwise
        """
        try:
            conn = self.store.conn
            cursor = conn.cursor()

            cutoff_date = (datetime.now(EAT) - timedelta(days=days)).strftime("%Y-%m-%d")

            cursor.execute(
                """
                SELECT COUNT(*) FROM escalations
                WHERE discord_id = ? AND escalation_level = ?
                AND escalated_at >= ?
                """,
                (discord_id, level, cutoff_date)
            )
            count = cursor.fetchone()[0]

            return count > 0

        except Exception as e:
            logger.error(f"Error checking recent escalations: {e}", exc_info=True)
            return False  # Fail safe - allow escalation if we can't check

    async def _escalate_level_2(
        self,
        discord_id: str,
        username: str,
        days_since_post: int,
        zone: str,
        emotional_state: str,
        trigger_reason: str = "missed_3_days",
        engagement_score: Optional[int] = None,
    ):
        """
        Level 2 (Orange Flag): Post alert to #facilitator-dashboard.

        Trevor monitors dashboard and reaches out within 24 hours if needed.

        Args:
            discord_id: Student's Discord ID (as string)
            username: Student's username
            days_since_post: Days since last post
            zone: Student's current zone
            emotional_state: Student's current emotional state
            trigger_reason: Trigger source (inactivity or low engagement)
            engagement_score: Latest engagement score when available
        """
        try:
            # Get facilitator dashboard channel
            dashboard = self.bot.get_channel(self.facilitator_dashboard_id)
            if not dashboard:
                logger.error(f"Facilitator dashboard channel {self.facilitator_dashboard_id} not found")
                return

            # Create alert message
            message = (
                f"⚠️ **ORANGE FLAG** - Student stuck 3+ days\n\n"
                f"**Student:** {username} (ID: {discord_id})\n"
                f"**Days since last post:** {days_since_post}\n"
                f"**Zone:** {zone}\n"
                f"**Emotional state:** {emotional_state}\n"
                f"**Trigger reason:** {trigger_reason}\n"
                f"**Latest engagement score:** {engagement_score if engagement_score is not None else 'n/a'}\n\n"
                f"**Action needed:** Trevor to review and reach out within 24 hours if needed.\n"
                f"**Offer:** Office hours (Tues/Thurs 6 PM) or 1:1 coaching session.\n\n"
                f"_Escalated at: {datetime.now(EAT).strftime('%Y-%m-%d %H:%M')} EAT_"
            )

            await dashboard.send(message)

            # Log to database
            await self._log_escalation(
                discord_id, LEVEL_2_ORANGE,
                f"Student stuck {days_since_post} days (Level 2 Orange Flag, trigger={trigger_reason}, engagement_score={engagement_score})"
            )

            # Log to moderation-logs
            await self._log_to_moderation_channel(
                f"**ORANGE FLAG** - {username} stuck {days_since_post} days (trigger: {trigger_reason})"
            )

            logger.info(f"Level 2 escalation sent for {username}")

        except Exception as e:
            logger.error(f"Error sending Level 2 escalation for {username}: {e}", exc_info=True)

    async def _escalate_level_3(
        self,
        discord_id: str,
        username: str,
        days_since_post: int,
        zone: str,
        emotional_state: str
    ):
        """
        Level 3 (Red Flag): Notify Trevor for direct human outreach.

        Trevor reaches out within 24 hours. Student is at risk of dropping out.

        Args:
            discord_id: Student's Discord ID (as string)
            username: Student's username
            days_since_post: Days since last post
            zone: Student's current zone
            emotional_state: Student's current emotional state
        """
        try:
            # Get Trevor
            trevor = await self.bot.fetch_user(int(self.trevor_discord_id))

            # Create Trevor DM message
            trevor_message = (
                f"🚨 **RED FLAG** - Immediate outreach needed\n\n"
                f"**Student:** {username} (ID: {discord_id})\n"
                f"**Days since last post:** {days_since_post}\n"
                f"**Zone:** {zone}\n"
                f"**Emotional state:** {emotional_state}\n\n"
                f"**Action needed:** Trevor DM student within 24 hours.\n\n"
                f"**Template:**\n"
                f"\"Hey {username}, haven't seen you in Discord this week. Everything okay?\n"
                f"You don't have to post, just wanted to check in.\"\n\n"
                f"If no response in 48 hours, offer phone call.\n\n"
                f"_Escalated at: {datetime.now(EAT).strftime('%Y-%m-%d %H:%M')} EAT_"
            )

            await trevor.send(trevor_message)


            # Log to database
            await self._log_escalation(
                discord_id, LEVEL_3_RED,
                f"Student stuck {days_since_post} days (Level 3 Red Flag)"
            )

            # Log to moderation-logs
            await self._log_to_moderation_channel(
                f"**RED FLAG** - {username} stuck {days_since_post} days (Trevor notified)"
            )

            logger.info(f"Level 3 escalation sent for {username}")

        except Exception as e:
            logger.error(f"Error sending Level 3 escalation for {username}: {e}", exc_info=True)

    async def escalate_level_4_crisis(
        self,
        discord_id: str,
        username: str,
        crisis_type: str,
        last_3_messages: List[str],
        zone: str,
        emotional_state: str
    ):
        """
        Level 4 (Crisis): Mental health emergency - instant Trevor DM with student context.

        Called by SafetyFilter when crisis keywords detected.

        Args:
            discord_id: Student's Discord ID (as string)
            username: Student's username
            crisis_type: Type of crisis detected (e.g., "mental_health_crisis")
            last_3_messages: Student's last 3 public messages (context)
            zone: Student's current zone
            emotional_state: Student's current emotional state
        """
        try:
            # Get Trevor
            trevor = await self.bot.fetch_user(int(self.trevor_discord_id))

            # Format last 3 messages
            messages_formatted = "\n".join([f"- {msg}" for msg in last_3_messages])

            # Create crisis alert message
            crisis_message = (
                f"🚨🚨 **LEVEL 4 CRISIS** - IMMEDIATE ACTION REQUIRED 🚨🚨\n\n"
                f"**Student:** {username} (ID: {discord_id})\n"
                f"**Crisis type:** {crisis_type}\n"
                f"**Zone:** {zone}\n"
                f"**Emotional state:** {emotional_state}\n\n"
                f"**Last 3 public messages:**\n{messages_formatted}\n\n"
                f"**IMMEDIATE ACTIONS:**\n"
                f"1. Trevor DM student within 1 HOUR\n"
                f"2. Assess risk and provide Kenya crisis resources\n"
                f"3. If student is minor (<18) and high risk, call parent within 2 hours\n"
                f"4. Follow up daily for 1 week\n\n"
                f"**Kenya Crisis Resources:**\n"
                f"- Kenya Crisis Hotline: 119 (free)\n"
                f"- Emergency: 999\n"
                f"- Trevor: 0116 405604\n\n"
                f"_Detected at: {datetime.now(EAT).strftime('%Y-%m-%d %H:%M')} EAT_"
            )

            await trevor.send(crisis_message)

            # Post crisis response to public channel (where crisis detected)
            # This is handled by SafetyFilter, so we just log here

            # Log to database
            await self._log_escalation(
                discord_id, LEVEL_4_CRISIS,
                f"Crisis detected: {crisis_type} (Level 4)"
            )

            # Log to moderation-logs
            await self._log_to_moderation_channel(
                f"**CRISIS** - {username} {crisis_type} (Trevor notified immediately)"
            )

            logger.critical(f"Level 4 crisis escalation sent for {username}: {crisis_type}")

        except Exception as e:
            logger.error(f"Error sending Level 4 crisis escalation for {username}: {e}", exc_info=True)

    async def _log_escalation(self, discord_id: str, level: int, notes: str):
        """
        Log escalation to database.

        Args:
            discord_id: Student's Discord ID (as string)
            level: Escalation level (1-4)
            notes: Escalation notes/details
        """
        try:
            conn = self.store.conn
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO escalations
                (discord_id, escalation_level, notes, escalated_at)
                VALUES (?, ?, ?, ?)
                """,
                (discord_id, level, notes, datetime.now(EAT).isoformat())
            )

            conn.commit()

        except Exception as e:
            logger.error(f"Error logging escalation to database: {e}", exc_info=True)

    async def _log_to_moderation_channel(self, message: str):
        """
        Log escalation to #moderation-logs channel.

        Args:
            message: Message to log
        """
        try:
            logs_channel = self.bot.get_channel(self.moderation_logs_id)
            if not logs_channel:
                logger.warning(f"Moderation logs channel {self.moderation_logs_id} not found")
                return

            await logs_channel.send(message)

        except Exception as e:
            logger.error(f"Error logging to moderation channel: {e}", exc_info=True)

    async def get_escalation_summary(self, days: int = 7) -> str:
        """
        Get summary of recent escalations for Trevor dashboard.

        Args:
            days: Number of days to look back

        Returns:
            Formatted escalation summary
        """
        try:
            conn = self.store.conn
            cursor = conn.cursor()

            cutoff_date = (datetime.now(EAT) - timedelta(days=days)).strftime("%Y-%m-%d")

            cursor.execute(
                """
                SELECT escalation_level, COUNT(*) as count
                FROM escalations
                WHERE escalated_at >= ?
                GROUP BY escalation_level
                ORDER BY escalation_level
                """,
                (cutoff_date,)
            )
            results = cursor.fetchall()

            if not results:
                return f"✅ No escalations in the last {days} days"

            # Build summary
            summary = f"📊 **Escalation Summary** (Last {days} days)\n\n"

            level_names = {
                LEVEL_1_YELLOW: "Level 1 (Yellow - Bot nudge)",
                LEVEL_2_ORANGE: "Level 2 (Orange - Trevor alert)",
                LEVEL_3_RED: "Level 3 (Red - Trevor DM)",
                LEVEL_4_CRISIS: "Level 4 (Crisis - Emergency)"
            }

            for level, count in results:
                level_name = level_names.get(level, f"Level {level}")
                summary += f"- {level_name}: {count}\n"

            return summary

        except Exception as e:
            logger.error(f"Error generating escalation summary: {e}", exc_info=True)
            return f"Error generating escalation summary: {e}"
