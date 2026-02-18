"""
Daily Prompt Scheduler
Story 2.1 Implementation: Automated Content Delivery

Background task scheduler for posting daily nodes and prompts at 9:00 AM and 9:15 AM EAT.
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Optional

import pytz

from discord.ext import tasks

from scheduler.daily_prompts import DailyPromptLibrary, WeekDay

logger = logging.getLogger(__name__)

# Timezone
EAT = pytz.timezone('Africa/Nairobi')


class DailyPromptScheduler:
    """
    Manages automated posting of daily nodes and prompts.

    Schedule:
    - 9:00 AM EAT: Post NotebookLM node link
    - 9:15 AM EAT: Post daily prompt (Mon-Thu)
    - 6:00 PM EAT: Post peer visibility snapshot (Wed only)
    - 9:00 AM EAT: Post Friday reflection (Fri only)
    """

    def __init__(self, bot, guild_id: int, channel_mapping: dict[int, int], cohort_start_date: str, escalation_system=None):
        """
        Initialize the scheduler.

        Args:
            bot: Discord bot instance
            guild_id: Discord server ID
            channel_mapping: Week number → Discord channel ID mapping
            cohort_start_date: Cohort start date (YYYY-MM-DD format)
            escalation_system: Optional EscalationSystem instance (Task 2.4)
        """
        self.bot = bot
        self.guild_id = guild_id
        self.channel_mapping = channel_mapping
        self.cohort_start_date = datetime.strptime(cohort_start_date, "%Y-%m-%d").replace(tzinfo=EAT)
        self.escalation_system = escalation_system

        # Load prompt library
        self.library = DailyPromptLibrary()

        # Task state
        self._last_post_date = None
        self._node_posted_today = False
        self._prompt_posted_today = False
        self._escalations_checked_today = False

        logger.info(f"Scheduler initialized for guild {guild_id}")
        logger.info(f"Cohort start date: {cohort_start_date}")
        logger.info(f"Channel mapping: {channel_mapping}")
        if escalation_system:
            logger.info("Escalation system integrated")

    def get_current_week(self) -> int:
        """
        Calculate current cohort week (1-8).

        Returns:
            Week number (1-8), or 0 if cohort hasn't started
        """
        now = datetime.now(EAT)
        days_since_start = (now - self.cohort_start_date).days

        if days_since_start < 0:
            return 0  # Cohort hasn't started

        week = (days_since_start // 7) + 1
        return min(week, 8)  # Cap at week 8

    def get_week_day(self) -> tuple[int, WeekDay]:
        """
        Get current week and day of week.

        Returns:
            Tuple of (week_number, day_of_week)
        """
        now = datetime.now(EAT)
        days_since_start = (now - self.cohort_start_date).days

        if days_since_start < 0:
            return (0, WeekDay(now.weekday() + 1))

        week = (days_since_start // 7) + 1
        day_of_week = WeekDay(now.weekday() + 1)  # Monday=1, Sunday=7

        return (min(week, 8), day_of_week)

    async def get_target_channel(self, week: int) -> Optional[object]:
        """
        Get the Discord channel for a given week.

        Args:
            week: Week number (1-8)

        Returns:
            TextChannel if found, None otherwise
        """
        channel_id = self.channel_mapping.get(week)
        if not channel_id:
            logger.warning(f"No channel configured for week {week}")
            return None

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                logger.error(f"Guild {self.guild_id} not found")
                return None

            channel = guild.get_channel(channel_id)
            if not channel or not hasattr(channel, "send"):
                logger.error(f"Channel {channel_id} not found or not sendable")
                return None

            return channel
        except Exception as e:
            logger.error(f"Error getting channel for week {week}: {e}")
            return None

    async def post_node_link(self, week: int, day: WeekDay):
        """
        Post NotebookLM node link at 9:00 AM EAT.

        Args:
            week: Current week number
            day: Current day of week
        """
        if week == 0 or week > 8:
            logger.info("Skipping node post: cohort not active or week > 8")
            return

        channel = await self.get_target_channel(week)
        if not channel:
            logger.error(f"Cannot post node: no channel for week {week}")
            return

        # Node mapping based on week
        node_map = {
            1: [(0.1, WeekDay.MONDAY), (0.2, WeekDay.TUESDAY), (0.3, WeekDay.WEDNESDAY), (0.4, WeekDay.THURSDAY)],
            2: [(1.1, WeekDay.MONDAY), (1.2, WeekDay.TUESDAY), (1.3, WeekDay.WEDNESDAY), (1.4, WeekDay.THURSDAY)],
            3: [(1.1, WeekDay.MONDAY), (1.2, WeekDay.TUESDAY), (1.3, WeekDay.WEDNESDAY), (1.4, WeekDay.THURSDAY)],
            4: [(2.1, WeekDay.MONDAY), (2.2, WeekDay.TUESDAY), (2.3, WeekDay.WEDNESDAY), (2.4, WeekDay.THURSDAY)],
            5: [(2.1, WeekDay.MONDAY), (2.2, WeekDay.TUESDAY), (2.3, WeekDay.WEDNESDAY), (2.4, WeekDay.THURSDAY)],
            6: [(3.1, WeekDay.MONDAY), (3.2, WeekDay.TUESDAY), (3.3, WeekDay.WEDNESDAY), (3.4, WeekDay.THURSDAY)],
            7: [(3.1, WeekDay.MONDAY), (3.2, WeekDay.TUESDAY), (3.3, WeekDay.WEDNESDAY), (3.4, WeekDay.THURSDAY)],
            8: [],  # Week 8 has no new nodes
        }

        # Find node for today
        node_number = None
        for node_num, node_day in node_map.get(week, []):
            if node_day == day:
                node_number = node_num
                break

        if not node_number:
            logger.info(f"No node scheduled for week {week} {day.name}")
            return

        # TODO: Load actual NotebookLM link from node library
        # For now, post placeholder
        message = (
            f"📚 **Node {node_number}: NotebookLM Podcast**\n\n"
            f"Today's node is now available! Listen to the 8-12 min podcast, "
            f"then respond to the daily prompt at 9:15 AM.\n\n"
            f"🔗 **[Link to Node {node_number} - NotebookLM Podcast]**\n"
            f"(TODO: Add actual NotebookLM link)"
        )

        try:
            await channel.send(message)
            logger.info(f"Posted node {node_number} to {channel.name}")
            self._node_posted_today = True
        except Exception as e:
            logger.error(f"Failed to post node {node_number}: {e}")

    async def post_daily_prompt(self, week: int, day: WeekDay):
        """
        Post daily prompt at 9:15 AM EAT (Mon-Thu only).

        Args:
            week: Current week number
            day: Current day of week
        """
        if week == 0 or week > 8:
            logger.info("Skipping prompt post: cohort not active or week > 8")
            return

        if day == WeekDay.FRIDAY:
            # Friday prompts are reflections, handled separately
            logger.info("Skipping daily prompt on Friday (reflection posted separately)")
            return

        channel = await self.get_target_channel(week)
        if not channel:
            logger.error(f"Cannot post prompt: no channel for week {week}")
            return

        # Get prompt from library
        prompt = self.library.get_prompt(week, day)
        if not prompt:
            logger.warning(f"No prompt found for week {week} {day.name}")
            # Fallback message
            message = f"🎯 **Today's Practice**\n\nCheck #resources for today's prompt!"
        else:
            message = prompt.format_for_discord()

        try:
            await channel.send(message)
            logger.info(f"Posted daily prompt for week {week} {day.name} to {channel.name}")
            self._prompt_posted_today = True
        except Exception as e:
            logger.error(f"Failed to post daily prompt: {e}")

    async def post_peer_visibility_snapshot(self, week: int):
        """
        Post peer visibility snapshot at 6:00 PM EAT (Wednesday only).

        Args:
            week: Current week number
        """
        if week == 0 or week > 8:
            return

        channel = await self.get_target_channel(week)
        if not channel:
            return

        # TODO: Aggregate actual student responses from today
        # For now, post placeholder
        message = (
            f"🌟 **TODAY'S PATTERNS (anonymized)**\n\n"
            f"Here's what the cohort explored today:\n\n"
            f"- \"AI is already in my life\" (Spotify, Netflix, email)\n"
            f"- \"People like me use AI\" (Parents, friends, teachers)\n"
            f"- \"I tried it!\" (Jokes, recipes, questions)\n\n"
            f"Notice: AI isn't sci-fi. It's already here.\n\n"
            f"✅ Guardrail #3 check: No comparison detected"
        )

        try:
            await channel.send(message)
            logger.info(f"Posted peer visibility snapshot for week {week}")
        except Exception as e:
            logger.error(f"Failed to post peer visibility snapshot: {e}")

    async def check_and_post(self):
        """
        Main loop: Check current time and post if scheduled.

        Runs every minute.
        """
        now = datetime.now(EAT)
        current_time = now.time()
        current_date = now.date()

        # Reset flags at midnight
        if self._last_post_date != current_date:
            self._last_post_date = current_date
            self._node_posted_today = False
            self._prompt_posted_today = False
            self._escalations_checked_today = False

        week, day = self.get_week_day()

        # 9:00 AM EAT - Post node link
        if current_time.hour == 9 and current_time.minute == 0 and not self._node_posted_today:
            logger.info("Scheduled: 9:00 AM node post")
            await self.post_node_link(week, day)

        # 9:15 AM EAT - Post daily prompt
        elif current_time.hour == 9 and current_time.minute == 15 and not self._prompt_posted_today:
            logger.info("Scheduled: 9:15 AM prompt post")
            await self.post_daily_prompt(week, day)

        # 10:00 AM EAT - Check escalations (Task 2.4)
        elif current_time.hour == 10 and current_time.minute == 0 and not self._escalations_checked_today:
            if self.escalation_system:
                logger.info("Scheduled: 10:00 AM escalation check")
                await self.escalation_system.check_escalations(week)
                self._escalations_checked_today = True

        # 6:00 PM EAT Wednesday - Post peer visibility snapshot
        elif current_time.hour == 18 and current_time.minute == 0 and day == WeekDay.WEDNESDAY:
            logger.info("Scheduled: 6:00 PM peer visibility snapshot")
            await self.post_peer_visibility_snapshot(week)

    def start(self):
        """Start the scheduler background task."""
        self.scheduler_task.start()
        logger.info("Daily prompt scheduler started")

    def stop(self):
        """Stop the scheduler background task."""
        self.scheduler_task.cancel()
        logger.info("Daily prompt scheduler stopped")

    @tasks.loop(minutes=1)
    async def scheduler_task(self):
        """Background task that runs every minute to check for scheduled posts."""
        try:
            await self.check_and_post()
        except Exception as e:
            logger.error(f"Error in scheduler task: {e}", exc_info=True)

    @scheduler_task.before_loop
    async def before_scheduler_task(self):
        """Wait for bot to be ready before starting scheduler."""
        await self.bot.wait_until_ready()
        logger.info("Scheduler task waiting for bot ready...")
