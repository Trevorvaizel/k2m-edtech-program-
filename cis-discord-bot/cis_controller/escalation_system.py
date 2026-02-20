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

from database.store import StudentStateStore

logger = logging.getLogger(__name__)

# Timezone
EAT = pytz.timezone('Africa/Nairobi')

# Escalation levels (from escalation-playbook-v1.md)
LEVEL_1_YELLOW = 1  # Bot handles (automated nudge)
LEVEL_2_ORANGE = 2  # Trevor monitors (dashboard notification)
LEVEL_3_RED = 3     # Trevor intervenes (direct DM)
LEVEL_4_CRISIS = 4  # Emergency intervention (instant Trevor DM + resources)


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
                SELECT MAX(date) as last_post_date,
                       SUM(CASE WHEN has_posted = 1 THEN 1 ELSE 0 END) as total_posts
                FROM daily_participation
                WHERE discord_id = ?
                """,
                (discord_id,)
            )
            result = cursor.fetchone()
            last_post_date = result[0] if result and result[0] else None
            total_posts = result[1] if result and result[1] else 0

            # Calculate days since last post
            now = datetime.now(EAT)
            if last_post_date:
                last_post = datetime.strptime(last_post_date, "%Y-%m-%d").replace(tzinfo=EAT)
                days_since_post = (now - last_post).days
            else:
                # Student has never posted
                days_since_post = None  # Don't escalate brand-new students

            # Skip brand-new students (joined today, hasn't had chance to post yet)
            if days_since_post is None:
                return

            # Check escalation triggers
            escalation_triggered = False

            # Level 1: 1 day no post (bot nudge) - handled by ParticipationTracker
            # This is already done in participation_tracker.py:check_inactive_students()

            # Level 2: 3+ days no post (Trevor dashboard alert)
            if days_since_post >= 3:
                # Check if we already escalated this student recently
                if not await self._was_recently_escalated(discord_id, LEVEL_2_ORANGE, days=7):
                    await self._escalate_level_2(
                        discord_id, username, days_since_post, zone, emotional_state
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
        emotional_state: str
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
                f"**Emotional state:** {emotional_state}\n\n"
                f"**Action needed:** Trevor to review and reach out within 24 hours if needed.\n"
                f"**Offer:** Office hours (Tues/Thurs 6 PM) or 1:1 coaching session.\n\n"
                f"_Escalated at: {datetime.now(EAT).strftime('%Y-%m-%d %H:%M')} EAT_"
            )

            await dashboard.send(message)

            # Log to database
            await self._log_escalation(
                discord_id, LEVEL_2_ORANGE,
                f"Student stuck {days_since_post} days (Level 2 Orange Flag)"
            )

            # Log to moderation-logs
            await self._log_to_moderation_channel(
                f"**ORANGE FLAG** - {username} stuck {days_since_post} days"
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
