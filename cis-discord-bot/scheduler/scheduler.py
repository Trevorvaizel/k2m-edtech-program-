"""
Daily Prompt Scheduler
Story 2.1 Implementation: Automated Content Delivery

Background task scheduler for posting daily nodes and prompts at 9:00 AM and 9:15 AM EAT.
"""

import asyncio
from collections import Counter
import logging
import os
import re
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytz

from discord.ext import tasks

from cis_controller.safety_filter import post_to_discord_safe
from cis_controller.facilitator_dashboard import FacilitatorDashboard
from scheduler.daily_prompts import DailyPromptLibrary, WeekDay
from scheduler.cluster_sessions import ClusterSessionScheduler
from scheduler.parent_email_scheduler import get_parent_email_scheduler
from database import get_store

logger = logging.getLogger(__name__)

# Timezone
EAT = pytz.timezone('Africa/Nairobi')

# Node mapping for 9:00 AM NotebookLM drops (Mon-Thu).
NODE_SCHEDULE = {
    1: [("0.1", WeekDay.MONDAY), ("0.2", WeekDay.TUESDAY), ("0.3", WeekDay.WEDNESDAY), ("0.4", WeekDay.THURSDAY)],
    2: [("1.1", WeekDay.MONDAY), ("1.2", WeekDay.TUESDAY), ("1.3", WeekDay.WEDNESDAY), ("1.4", WeekDay.THURSDAY)],
    3: [("1.1", WeekDay.MONDAY), ("1.2", WeekDay.TUESDAY), ("1.3", WeekDay.WEDNESDAY), ("1.4", WeekDay.THURSDAY)],
    4: [("2.1", WeekDay.MONDAY), ("2.2", WeekDay.TUESDAY), ("2.3", WeekDay.WEDNESDAY), ("2.4", WeekDay.THURSDAY)],
    5: [("2.1", WeekDay.MONDAY), ("2.2", WeekDay.TUESDAY), ("2.3", WeekDay.WEDNESDAY), ("2.4", WeekDay.THURSDAY)],
    6: [("3.1", WeekDay.MONDAY), ("3.2", WeekDay.TUESDAY), ("3.3", WeekDay.WEDNESDAY), ("3.4", WeekDay.THURSDAY)],
    7: [("3.1", WeekDay.MONDAY), ("3.2", WeekDay.TUESDAY), ("3.3", WeekDay.WEDNESDAY), ("3.4", WeekDay.THURSDAY)],
    8: [],
}

SNAPSHOT_STOP_WORDS = {
    "about", "after", "again", "also", "been", "before", "being", "between",
    "could", "did", "does", "doing", "from", "have", "just", "like", "make",
    "more", "most", "much", "really", "that", "them", "then", "they", "this",
    "today", "very", "what", "when", "with", "would", "your", "you're", "you",
    "into", "than", "want", "because", "using", "used", "tried", "trying",
}


class DailyPromptScheduler:
    """
    Manages automated posting of daily nodes and prompts.

    Schedule:
    - 9:00 AM EAT: Post NotebookLM node link
    - 9:15 AM EAT: Post daily prompt (Mon-Thu)
    - 6:00 PM EAT: Post peer visibility snapshot (Wed only)
    - 9:00 AM EAT: Post Friday reflection (Fri only)
    """

    def __init__(
        self,
        bot,
        guild_id: int,
        channel_mapping: Dict[int, int],
        cohort_start_date: str,
        escalation_system=None,
        participation_tracker=None,
        store=None,
    ):
        """
        Initialize the scheduler.

        Args:
            bot: Discord bot instance
            guild_id: Discord server ID
            channel_mapping: Week number â†’ Discord channel ID mapping
            cohort_start_date: Cohort start date (YYYY-MM-DD format)
            escalation_system: Optional EscalationSystem instance (Task 2.4)
            participation_tracker: Optional ParticipationTracker instance (Task 2.2/2.4)
            store: Optional StudentStateStore instance (Task 2.5)
        """
        self.bot = bot
        self.guild_id = guild_id
        self.channel_mapping = channel_mapping
        # Use pytz.localize to avoid incorrect historical offsets from replace().
        self.cohort_start_date = EAT.localize(datetime.strptime(cohort_start_date, "%Y-%m-%d"))
        self.escalation_system = escalation_system
        self.participation_tracker = participation_tracker
        self.store = store or get_store()  # Task 2.5: Database access
        self.dashboard = FacilitatorDashboard(self.store)  # Task 2.6: Dashboard automation
        self.parent_email_scheduler = get_parent_email_scheduler(store=self.store)

        # Task 4.4: Cluster session scheduler
        self.cluster_scheduler = ClusterSessionScheduler(
            bot=bot,
            store=self.store,
            guild_id=guild_id,
            channel_mapping=channel_mapping,
            cohort_start_date=cohort_start_date,
        )

        # Load prompt library
        self.library = DailyPromptLibrary()

        # Task state
        self._last_post_date = None
        self._node_posted_today = False
        self._prompt_posted_today = False
        self._escalations_checked_today = False
        self._reflection_posted_today = False  # Task 2.5
        self._week_unlock_today = False  # Task 2.5
        self._daily_summary_today = False  # Task 2.6: 9 AM daily summary
        self._peer_visibility_today = False  # Task 2.6: 6 PM peer visibility
        self._reflection_summary_today = False  # Task 2.6: Friday 5 PM reflection summary
        self._spot_check_today = False  # Task 2.6: Friday 5 PM spot-check list
        self._agent_unlock_today = False  # Task 3.4: Agent unlock announcements
        self._artifact_inactivity_nudges_today = False  # Task 4.1: proactive artifact nudges
        self._weekly_artifact_celebration_today = False  # Task 4.2
        self._weekly_parent_emails_today = False  # Task 4.6: Monday weekly parent updates
        self._week8_parent_reports_today = False  # Task 4.6: Week 8 Friday parent report batch
        self._sheets_sync_today = False  # Task 7.6: nightly PostgreSQL -> Sheets sync
        self._enroll_nudges_today = False  # Task 7.3: 48h enroll reminder DM
        self._enroll_email_queue_last_run = None  # Task 7.3: Email #2 deferred queue drain
        self._token_expiry_check_today = False  # Task 7.4: nightly M-Pesa token expiry warning

        logger.info(f"Scheduler initialized for guild {guild_id}")
        logger.info(f"Cohort start date: {cohort_start_date}")
        logger.info(f"Channel mapping: {channel_mapping}")
        if escalation_system:
            logger.info("Escalation system integrated")
        if participation_tracker:
            logger.info("Participation tracker integrated")
        logger.info("Facilitator dashboard integrated")
        logger.info("Agent unlock announcements enabled")
        logger.info("Parent email scheduler integrated")

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

    def get_week_day(self) -> Tuple[int, WeekDay]:
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

    def _habit_focus_for_week(self, week: int) -> Tuple[str, str]:
        """
        Return the habit label and self-check question for the provided week.
        """
        if week == 1:
            return ("Habit 1 (Pause)", "Did you pause before asking AI this week?")
        if week in (2, 3):
            return ("Habit 2 (Context)", "Did you explain your situation before asking AI this week?")
        if week in (4, 5):
            return ("Habit 3 (Iterate)", "Did you change one thing at a time while iterating this week?")
        if week in (6, 7):
            return ("Habit 4 (Think First)", "Did you use AI before decisions this week?")
        return ("This Week's Habit", "Did you practice this week's habit?")

    def _resolve_node_link(self, node_number: str) -> Optional[str]:
        """
        Resolve NotebookLM node link from environment.

        Priority:
        1) NODE_LINK_X_Y (e.g. NODE_LINK_0_1)
        2) NOTEBOOKLM_NODE_BASE_URL + /{node}
        """
        env_key = f"NODE_LINK_{node_number.replace('.', '_')}"
        direct_link = os.getenv(env_key, "").strip()
        if direct_link:
            return direct_link

        base_url = os.getenv("NOTEBOOKLM_NODE_BASE_URL", "").strip().rstrip("/")
        if base_url:
            return f"{base_url}/{node_number}"

        return None

    def _build_node_message(self, node_number: str, node_link: Optional[str]) -> str:
        """
        Build student-facing node drop message without placeholder text.
        """
        message = (
            f"ðŸ“š **Node {node_number}: NotebookLM Podcast**\n\n"
            f"Today's node is now available. Listen to the 8-12 minute podcast, "
            f"then respond to the daily prompt at 9:15 AM.\n\n"
        )
        if node_link:
            message += f"ðŸ”— **Node Link:** {node_link}"
        else:
            message += (
                "ðŸ”— **Node Link:** Not configured yet. Trevor will post it in "
                "#resources before the daily prompt."
            )
        return message

    @staticmethod
    def _sanitize_snapshot_excerpt(content: str, limit: int = 140) -> str:
        """
        Sanitize student content for anonymized public snapshots.
        """
        cleaned = re.sub(r"<@!?\d+>", "[student]", content or "")
        cleaned = re.sub(r"https?://\S+", "[link]", cleaned)
        cleaned = " ".join(cleaned.split()).strip()
        if len(cleaned) > limit:
            cleaned = f"{cleaned[: limit - 3]}..."
        return cleaned

    async def _collect_today_student_posts(self, channel: object, max_messages: int = 200) -> List[str]:
        """
        Collect today's student-authored posts from the target weekly channel.
        """
        if not hasattr(channel, "history"):
            return []

        start_of_day = datetime.now(EAT).replace(hour=0, minute=0, second=0, microsecond=0)
        collected: List[str] = []

        try:
            history_iter = channel.history(limit=max_messages, after=start_of_day)
            async for item in history_iter:
                author = getattr(item, "author", None)
                if getattr(author, "bot", False):
                    continue
                content = self._sanitize_snapshot_excerpt(getattr(item, "content", ""))
                if not content:
                    continue
                collected.append(content)
        except Exception as exc:
            logger.warning("Could not collect today's peer-visibility source posts: %s", exc)

        return collected

    def _derive_peer_visibility_patterns(self, messages: List[str], max_patterns: int = 3) -> List[str]:
        """
        Derive anonymized cohort-level patterns from today's student posts.
        """
        if not messages:
            return []

        theme_keywords = {
            "Students are adding context before asking AI": {"context", "situation", "specific", "details", "background"},
            "Students are iterating instead of accepting first drafts": {"iterate", "iteration", "version", "revise", "change", "improve"},
            "Students are pausing to think before prompting": {"pause", "paused", "think", "before", "reflect"},
            "Students are connecting AI practice to real life": {"school", "class", "project", "work", "business", "home", "family"},
        }

        theme_counts: Counter[str] = Counter()
        keyword_counts: Counter[str] = Counter()

        for message in messages:
            tokens = set(re.findall(r"[a-z']{3,}", message.lower()))
            if not tokens:
                continue

            for theme, keywords in theme_keywords.items():
                if tokens.intersection(keywords):
                    theme_counts[theme] += 1

            for token in tokens:
                if len(token) < 4 or token in SNAPSHOT_STOP_WORDS:
                    continue
                keyword_counts[token] += 1

        patterns: List[str] = []
        for theme, count in theme_counts.most_common(max_patterns):
            patterns.append(f"{theme} ({count})")

        if len(patterns) < max_patterns:
            for token, count in keyword_counts.most_common(max_patterns * 3):
                if count < 2:
                    continue
                candidate = f"'{token}' surfaced across multiple reflections ({count})"
                if candidate not in patterns:
                    patterns.append(candidate)
                if len(patterns) >= max_patterns:
                    break

        return patterns[:max_patterns]

    async def _set_student_channel_access(
        self,
        discord_id: str,
        channel: object,
        can_read: bool,
        can_post: bool,
        reason: str,
    ) -> None:
        """
        Set per-student channel access for progression gating.
        """
        if not channel:
            return

        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            logger.error(f"Guild {self.guild_id} not found for permission sync")
            return

        member = guild.get_member(int(discord_id))
        if member is None:
            try:
                member = await guild.fetch_member(int(discord_id))
            except Exception:
                logger.warning(f"Could not resolve member {discord_id} for permission sync")
                return

        if not hasattr(channel, "set_permissions"):
            logger.warning("Channel does not support set_permissions; skipping progression gate sync")
            return

        try:
            await channel.set_permissions(
                member,
                view_channel=can_read,
                send_messages=can_post,
                reason=reason,
            )
        except Exception as exc:
            logger.error(
                "Failed updating channel permissions for %s in channel %s: %s",
                discord_id,
                getattr(channel, "id", "unknown"),
                exc,
            )

    async def _apply_week_unlock_permissions(self, week: int) -> None:
        """
        Apply progressive-disclosure channel permissions after weekly unlock.
        """
        if week <= 0 or week >= 8:
            return

        current_channel = await self.get_target_channel(week)
        next_channel = await self.get_target_channel(week + 1)
        if current_channel is None or next_channel is None:
            logger.warning("Skipping permission sync: current/next week channels not configured")
            return

        same_channel = getattr(current_channel, "id", None) == getattr(next_channel, "id", None)

        submitted = self.store.get_submitted_reflections(week)
        for row in submitted:
            discord_id = str(row['discord_id'])

            await self._set_student_channel_access(
                discord_id=discord_id,
                channel=next_channel,
                can_read=True,
                can_post=True,
                reason=f"Week {week + 1} unlocked",
            )

            if not same_channel:
                await self._set_student_channel_access(
                    discord_id=discord_id,
                    channel=current_channel,
                    can_read=True,
                    can_post=False,
                    reason=f"Week {week} archived after unlock",
                )

        laggards = self.store.get_incomplete_reflections(week)
        for row in laggards:
            discord_id = str(row['discord_id'])

            await self._set_student_channel_access(
                discord_id=discord_id,
                channel=current_channel,
                can_read=True,
                can_post=True,
                reason=f"Week {week} remains open for catch-up",
            )

            if not same_channel:
                await self._set_student_channel_access(
                    discord_id=discord_id,
                    channel=next_channel,
                    can_read=False,
                    can_post=False,
                    reason=f"Week {week + 1} locked pending reflection",
                )

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

        node_number = None
        for node_num, node_day in NODE_SCHEDULE.get(week, []):
            if node_day == day:
                node_number = node_num
                break

        if not node_number:
            logger.info(f"No node scheduled for week {week} {day.name}")
            return

        node_link = self._resolve_node_link(node_number)
        message = self._build_node_message(node_number, node_link)

        try:
            await self._send_public_message(channel, message)
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
            message = f"ðŸŽ¯ **Today's Practice**\n\nCheck #resources for today's prompt!"
        else:
            message = prompt.format_for_discord()

        try:
            await self._send_public_message(channel, message)
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

        posts = await self._collect_today_student_posts(channel)
        patterns = self._derive_peer_visibility_patterns(posts, max_patterns=3)

        quote_lines = []
        seen_quotes = set()
        for post in posts:
            normalized = post.lower()
            if not normalized or normalized in seen_quotes:
                continue
            quote_lines.append(f'- "{post}"')
            seen_quotes.add(normalized)
            if len(quote_lines) >= 3:
                break

        if patterns:
            pattern_block = "\n".join(f"- {pattern}" for pattern in patterns)
        else:
            pattern_block = (
                "- Students are actively engaging with today's prompt\n"
                "- Posts show reflection and experimentation in progress\n"
                "- Students are connecting AI practice to their own context"
            )

        quote_block = "\n".join(quote_lines) if quote_lines else "- No additional excerpts captured today."
        message = (
            f"**TODAY'S PATTERNS (anonymized)**\n\n"
            f"Signals captured from {len(posts)} student posts today.\n\n"
            f"Shared patterns:\n{pattern_block}\n\n"
            f"Anonymized student lines:\n{quote_block}\n\n"
            f"Guardrail #3 check: No comparison detected"
        )

        try:
            await self._send_public_message(channel, message)
            logger.info(f"Posted peer visibility snapshot for week {week}")
        except Exception as e:
            logger.error(f"Failed to post peer visibility snapshot: {e}")

    async def post_friday_reflection(self, week: int):
        """
        Post Friday reflection prompt at 9:00 AM EAT (Task 2.5).

        Args:
            week: Current week number
        """
        if week == 0 or week > 8:
            logger.info("Skipping reflection post: cohort not active or week > 8")
            return

        channel = await self.get_target_channel(week)
        if not channel:
            logger.error(f"Cannot post reflection: no channel for week {week}")
            return

        # Ensure all active students in this week have a reflection record.
        self.store.ensure_weekly_reflection_records(week)
        habit_label, habit_prompt = self._habit_focus_for_week(week)

        message = (
            f"FRIDAY REFLECTION (Week {week})\n\n"
            f"Before you unlock next week, take 15 minutes to reflect:\n\n"
            f"Part 1: Self-Assessment\n"
            f"{habit_prompt}\n"
            f"- Yes | Sometimes | No\n\n"
            f"Part 2: Identity Shift\n"
            f"What changed this week?\n"
            f"(Example: \"I went from confused to getting it\")\n\n"
            f"Part 3: Proof-of-Work\n"
            f"Paste ONE sentence that shows AI understood YOU.\n"
            f"(Example: \"AI knew I'm interested in game design, not just coding\")\n\n"
            f"Submit with command:\n"
            f"`/submit-reflection habit-practice:[Yes/Sometimes/No] identity-shift:[your answer] proof-of-work:[one sentence]`\n\n"
            f"Tracking habit focus: {habit_label}\n\n"
            f"Due by Saturday 12 PM EAT.\n"
            f"Week {week + 1} unlocks after you submit your reflection.\n\n"
            f"Behind schedule? No pressure. Complete at your own pace. Week {week} stays open."
        )

        try:
            await self._send_public_message(channel, message)
            logger.info(f"Posted Friday reflection for week {week} to {channel.name}")
            self._reflection_posted_today = True
        except Exception as e:
            logger.error(f"Failed to post Friday reflection: {e}")

    async def batch_unlock_week(self, week: int):
        """
        Batch unlock next week for students who submitted reflections (Task 2.5).
        Runs Saturday at 12:00 PM EAT.

        Args:
            week: Week number to unlock (1-7)
        """
        if week == 0 or week > 7:
            logger.info(f"Skipping week unlock: invalid week {week}")
            return

        # Batch unlock all submitted reflections
        try:
            unlocked_count = self.store.batch_unlock_next_week(week)
            logger.info(f"Batch unlocked week {week} for {unlocked_count} students")
        except Exception as e:
            logger.error(f"Failed to batch unlock week {week}: {e}")
            return

        try:
            await self._apply_week_unlock_permissions(week)
        except Exception as e:
            logger.error(f"Failed to apply week unlock permissions: {e}")

        # Get summary stats
        try:
            summary = self.store.get_reflection_summary(week)
            logger.info(f"Week {week} reflection summary: {summary}")
        except Exception as e:
            logger.error(f"Failed to get reflection summary: {e}")
            summary = {'week_number': week, 'submitted_count': 0, 'pending_count': 0}

        # Post unlock announcement to current week channel
        channel = await self.get_target_channel(week)
        if not channel:
            logger.error(f"Cannot post unlock announcement: no channel for week {week}")
            return

        # Create unlock announcement
        if summary['submitted_count'] > 0:
            message = (
                f"ðŸ”“ **Week {week + 1} UNLOCKED!**\n\n"
                f"Congratulations! {summary['submitted_count']} students completed their Week {week} reflection.\n\n"
                f"âœ… **Week {week + 1} is now open** for those who submitted.\n\n"
                f"Still working on your reflection? No problem! Week {week} stays open.\n"
                f"Complete your reflection to unlock Week {week + 1}.\n\n"
                f"Continue your journey in the next week channel!"
            )
        else:
            message = (
                f"ðŸ”“ **Week {week + 1} Status**\n\n"
                f"Saturday 12 PM has passed. Week {week + 1} unlocks as you complete your Week {week} reflection.\n\n"
                f"No rush! Work at your own pace. Week {week} stays open."
            )

        try:
            await self._send_public_message(channel, message)
            logger.info(f"Posted week {week + 1} unlock announcement to {channel.name}")
        except Exception as e:
            logger.error(f"Failed to post unlock announcement: {e}")

        # Trevor notification: List students who haven't completed
        try:
            incomplete = self.store.get_incomplete_reflections(week)
            if incomplete:
                await self._notify_trevor_incomplete_reflections(week, incomplete)
        except Exception as e:
            logger.error(f"Failed to notify Trevor about incomplete reflections: {e}")

        self._week_unlock_today = True

    async def _notify_trevor_incomplete_reflections(self, week: int, incomplete_students: list):
        """
        Notify Trevor about students who haven't completed their reflection (Task 2.5).

        Args:
            week: Week number
            incomplete_students: List of reflection rows where submitted=0
        """
        # Get facilitator dashboard channel
        dashboard_channel_id = int(os.getenv('CHANNEL_FACILITATOR_DASHBOARD', 0))
        if not dashboard_channel_id:
            logger.warning("CHANNEL_FACILITATOR_DASHBOARD not set, skipping Trevor notification")
            return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                logger.error(f"Guild {self.guild_id} not found")
                return

            dashboard = guild.get_channel(dashboard_channel_id)
            if not dashboard or not hasattr(dashboard, "send"):
                logger.error(f"Dashboard channel {dashboard_channel_id} not found or not sendable")
                return
        except Exception as e:
            logger.error(f"Error getting dashboard channel: {e}")
            return

        # Build Trevor notification
        student_list = "\n".join([
            f"- <@{row['discord_id']}> (Zone: {row['zone']}, Week: {row['current_week']})"
            for row in incomplete_students[:20]  # Limit to first 20 to avoid message length issues
        ])

        if len(incomplete_students) > 20:
            student_list += f"\n- ... and {len(incomplete_students) - 20} more"

        message = (
            f"ðŸ“Š **FRIDAY REFLECTIONS (Week {week})**\n\n"
            f"**Completion Status:**\n"
            f"Pending: {len(incomplete_students)}\n\n"
            f"**Students who haven't completed:**\n"
            f"{student_list}\n\n"
            f"Trevor's decision: Personal outreach OR let student self-pace (Guardrail #5)."
        )

        try:
            await dashboard.send(message)
            logger.info(f"Notified Trevor about {len(incomplete_students)} incomplete reflections for week {week}")
        except Exception as e:
            logger.error(f"Failed to send Trevor notification: {e}")

    async def post_daily_summary(self, week: int):
        """
        Post 9:00 AM daily summary to #facilitator-dashboard (Task 2.6).

        Args:
            week: Current week number
        """
        if week == 0 or week > 8:
            logger.info("Skipping daily summary: cohort not active or week > 8")
            return

        # Get dashboard channel
        dashboard_channel_id = int(os.getenv('CHANNEL_FACILITATOR_DASHBOARD', 0))
        if not dashboard_channel_id:
            logger.warning("CHANNEL_FACILITATOR_DASHBOARD not set, skipping daily summary")
            return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                logger.error(f"Guild {self.guild_id} not found")
                return

            dashboard = guild.get_channel(dashboard_channel_id)
            if not dashboard or not hasattr(dashboard, "send"):
                logger.error(f"Dashboard channel {dashboard_channel_id} not found or not sendable")
                return
        except Exception as e:
            logger.error(f"Error getting dashboard channel: {e}")
            return

        # Generate and post summary
        try:
            message = self.dashboard.generate_daily_summary(week)
            await dashboard.send(message)
            logger.info(f"Posted daily summary to dashboard for week {week}")
            self._daily_summary_today = True
        except Exception as e:
            logger.error(f"Failed to post daily summary: {e}")

    async def post_peer_visibility_summary(self, week: int):
        """
        Post 6:00 PM peer visibility summary to #facilitator-dashboard (Task 2.6).

        Args:
            week: Current week number
        """
        if week == 0 or week > 8:
            return

        # Get dashboard channel
        dashboard_channel_id = int(os.getenv('CHANNEL_FACILITATOR_DASHBOARD', 0))
        if not dashboard_channel_id:
            logger.warning("CHANNEL_FACILITATOR_DASHBOARD not set, skipping peer visibility summary")
            return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return

            dashboard = guild.get_channel(dashboard_channel_id)
            if not dashboard or not hasattr(dashboard, "send"):
                return
        except Exception as e:
            logger.error(f"Error getting dashboard channel: {e}")
            return

        try:
            message = self.dashboard.generate_peer_visibility_summary(week)
            await dashboard.send(message)
            logger.info(f"Posted peer visibility summary to dashboard for week {week}")
            self._peer_visibility_today = True
        except Exception as e:
            logger.error(f"Failed to post peer visibility summary: {e}")

    async def post_friday_dashboard_summaries(self, week: int):
        """
        Post Friday 5:00 PM reflection summary + spot-check list (Task 2.6).

        Args:
            week: Current week number
        """
        if week == 0 or week > 8:
            logger.info("Skipping Friday dashboard summaries: cohort not active or week > 8")
            return

        # Get dashboard channel
        dashboard_channel_id = int(os.getenv('CHANNEL_FACILITATOR_DASHBOARD', 0))
        if not dashboard_channel_id:
            logger.warning("CHANNEL_FACILITATOR_DASHBOARD not set, skipping Friday summaries")
            return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                logger.error(f"Guild {self.guild_id} not found")
                return

            dashboard = guild.get_channel(dashboard_channel_id)
            if not dashboard or not hasattr(dashboard, "send"):
                logger.error(f"Dashboard channel {dashboard_channel_id} not found or not sendable")
                return
        except Exception as e:
            logger.error(f"Error getting dashboard channel: {e}")
            return

        # Post reflection summary
        try:
            summary_message = self.dashboard.generate_reflection_summary(week)
            await dashboard.send(summary_message)
            logger.info(f"Posted reflection summary to dashboard for week {week}")
            self._reflection_summary_today = True
        except Exception as e:
            logger.error(f"Failed to post reflection summary: {e}")

        # Post spot-check list
        try:
            spot_check_message = self.dashboard.generate_spot_check_list(week)
            await dashboard.send(spot_check_message)
            logger.info(f"Posted spot-check list to dashboard for week {week}")
            self._spot_check_today = True
        except Exception as e:
            logger.error(f"Failed to post spot-check list: {e}")

    async def _notify_parent_email_batch_result(
        self,
        batch_type: str,
        stats: dict,
    ):
        """
        Send a compact parent-email batch status to Trevor dashboard.
        """
        dashboard_channel_id = int(os.getenv('CHANNEL_FACILITATOR_DASHBOARD', 0))
        if not dashboard_channel_id:
            return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return
            dashboard = guild.get_channel(dashboard_channel_id)
            if not dashboard or not hasattr(dashboard, "send"):
                return

            message = (
                f"PARENT EMAIL BATCH: {batch_type}\n"
                f"- sent: {stats.get('sent', 0)}\n"
                f"- failed: {stats.get('failed', 0)}\n"
                f"- skipped: {stats.get('skipped', 0)}\n"
                f"- total: {stats.get('total', 0)}"
            )
            if stats.get('report_week'):
                message += f"\n- report_week: {stats['report_week']}"

            failures = stats.get('failures') or []
            if failures:
                first_failure = failures[0]
                message += (
                    f"\n- first_failure: {first_failure.get('parent_email', 'unknown')} "
                    f"({first_failure.get('error', 'unknown error')})"
                )

            await dashboard.send(message)
        except Exception as exc:
            logger.error("Failed to notify parent email batch result: %s", exc, exc_info=True)

    async def post_weekly_parent_emails(self, week: int):
        """
        Send Monday 9:00 AM parent updates (summarizes previous week).
        """
        stats = await self.parent_email_scheduler.send_weekly_parent_emails(week)
        await self._notify_parent_email_batch_result("weekly_update", stats)
        self._weekly_parent_emails_today = True

    async def post_week8_parent_reports(self, week: int):
        """
        Send Friday 9:00 AM Week 8 parent reports.
        """
        stats = await self.parent_email_scheduler.send_week8_parent_reports(week)
        await self._notify_parent_email_batch_result("week8_showcase", stats)
        self._week8_parent_reports_today = True

    async def post_weekly_artifact_celebration(self):
        """
        Post weekly artifact publication celebration summary (Task 4.2).
        """
        from commands.artifact import post_weekly_artifact_celebration

        try:
            posted = await post_weekly_artifact_celebration(self.bot)
            if posted:
                logger.info("Posted weekly artifact celebration summary")
            else:
                logger.info("No weekly artifact celebration post needed")
        except Exception as exc:
            logger.error("Failed to post weekly artifact celebration: %s", exc, exc_info=True)
        finally:
            self._weekly_artifact_celebration_today = True

    async def post_artifact_inactivity_nudges(self):
        """
        Send daily proactive artifact nudges for inactive students (Task 4.1).
        """
        from commands.artifact import send_artifact_inactivity_nudges

        try:
            sent_count = await send_artifact_inactivity_nudges(self.bot, inactive_days=3)
            logger.info("Artifact inactivity nudge run complete: sent=%s", sent_count)
        except Exception as exc:
            logger.error("Failed artifact inactivity nudge run: %s", exc, exc_info=True)
        finally:
            self._artifact_inactivity_nudges_today = True

    async def process_enrollment_email_queue(self) -> None:
        """
        Drain deferred Email #2 queue when discord_id linkage arrives (Task 7.3).
        """
        enabled = os.getenv("ENROLLMENT_EMAIL_QUEUE_ENABLED", "true").strip().lower() in {
            "1", "true", "yes", "on"
        }
        if not enabled:
            return

        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
        if not spreadsheet_id:
            logger.warning("Enrollment email queue drain skipped: GOOGLE_SHEETS_ID missing")
            return

        try:
            from cis_controller.interest_api_server import process_pending_enrollment_payment_emails

            stats = await process_pending_enrollment_payment_emails(
                spreadsheet_id=spreadsheet_id,
                sheet_range=os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z").strip(),
                creds_path=os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "").strip() or None,
            )
            logger.info("Enrollment email queue drain stats: %s", stats)
        except Exception as exc:
            logger.error("Enrollment email queue drain failed: %s", exc, exc_info=True)

    async def post_enroll_nudges(self) -> None:
        """
        Send 48h KIRA enroll nudges to linked students missing /api/enroll profile (Task 7.3).
        """
        enabled = os.getenv("ENROLL_NUDGE_ENABLED", "true").strip().lower() in {
            "1", "true", "yes", "on"
        }
        if not enabled:
            self._enroll_nudges_today = True
            return

        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
        if not spreadsheet_id:
            logger.warning("48h enroll nudge scan skipped: GOOGLE_SHEETS_ID missing")
            self._enroll_nudges_today = True
            return

        try:
            from cis_controller.interest_api_server import send_48h_enroll_nudges

            stats = await send_48h_enroll_nudges(
                bot=self.bot,
                spreadsheet_id=spreadsheet_id,
                sheet_range=os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z").strip(),
                creds_path=os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "").strip() or None,
                age_hours=48,
            )
            logger.info("48h enroll nudge stats: %s", stats)
        except Exception as exc:
            logger.error("48h enroll nudge scan failed: %s", exc, exc_info=True)
        finally:
            self._enroll_nudges_today = True

    async def post_token_expiry_warnings(self) -> None:
        """
        Nightly M-Pesa token expiry warning (Task 7.4, Decision H-01 + GAP FIX #4).

        Scans Google Sheets for students whose payment submit token (Column Q) expires
        within 48 hours. For each:
          - If discord_id is linked: sends a KIRA DM and marks token_warning_sent=True in PG.
          - If not yet on Discord: falls back to a Brevo warning email.
          - If token_warning_sent is already True: skips (idempotency guard).
        """
        enabled = os.getenv("TOKEN_EXPIRY_WARN_ENABLED", "true").strip().lower() in {
            "1", "true", "yes", "on"
        }
        if not enabled:
            return

        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
        if not spreadsheet_id:
            logger.warning("Token expiry check skipped: GOOGLE_SHEETS_ID missing")
            return

        try:
            from cis_controller.interest_api_server import send_token_expiry_warnings

            stats = await send_token_expiry_warnings(
                bot=self.bot,
                spreadsheet_id=spreadsheet_id,
                sheet_range=os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z").strip(),
                creds_path=os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "").strip() or None,
                warn_within_hours=48,
            )
            logger.info("Token expiry warning stats: %s", stats)
        except Exception as exc:
            logger.error("Token expiry warning check failed: %s", exc, exc_info=True)

    async def _send_public_message(self, channel, message_text: str):
        """Route student-facing public posts through Guardrail #3 safety checks."""
        await post_to_discord_safe(
            bot=self.bot,
            channel=channel,
            message_text=message_text,
            escalation_system=self.escalation_system,
        )

    async def post_agent_unlock_announcement(self, week: int):
        """
        Post agent unlock announcement to weekly channel (Task 3.4).

        Announcement messages:
        - Week 4: /diverge and /challenge unlocked
        - Week 6: /synthesize and /create-artifact unlocked

        Args:
            week: Current week number
        """
        # Skip if cohort not active or already announced
        if week == 0 or week > 8:
            return

        # Check if we already announced for this week
        if self.store.has_announced_unlock(week):
            logger.info(f"Agent unlock already announced for week {week}, skipping")
            return

        # Get current week's agents
        current_agents = self.store.get_unlocked_agents_for_week(week)

        # Get previous week's agents.
        # Week 1 is baseline (/frame), so it should not trigger a "new unlock" post.
        if week == 1:
            previous_agents = current_agents
        elif week > 1:
            previous_agents = self.store.get_unlocked_agents_for_week(week - 1)
        else:
            previous_agents = []

        # Find new agents (difference)
        new_agents = [a for a in current_agents if a not in previous_agents]

        # No new agents? Skip announcement
        if not new_agents:
            logger.info(f"No new agents unlocked for week {week}")
            # Still record that we checked (prevents repeated checks)
            self.store.record_unlock_announcement(week, current_agents, None)
            return

        # Create announcement message based on which agents unlocked
        if "diverge" in new_agents or "challenge" in new_agents:
            # Week 4: /diverge and /challenge unlock announcement
            message = (
                "🎉 **NEW THINKING PARTNERS UNLOCKED!**\n\n"
                "Your toolkit just expanded. Meet your new CIS agents:\n\n"
                "🔍 **/diverge** (The Explorer)\n"
                "Explores possibilities without judgment. Change one thing at a time.\n"
                "_Example: /diverge What are 3 different career paths I could consider?_\n\n"
                "⚡ **/challenge** (The Challenger)\n"
                "Stress-tests your assumptions. Question before you decide.\n"
                "_Example: /challenge Is university really the only path to success?_\n\n"
                "**Why now?**\n"
                "You've built confidence with Habit 1 ⏸️ Pause (Week 1) and Habit 2 🎯 Context (Weeks 2-3).\n"
                "Now it's time to practice Habit 3 🔄 Iterate - exploring options and testing assumptions.\n\n"
                "**Remember:** Use all three agents:\n"
                "- /frame to clarify what you want\n"
                "- /diverge to explore different angles\n"
                "- /challenge to test your assumptions\n\n"
                "These tools work together. Try them all this week! ✨"
            )
        elif "synthesize" in new_agents or "create-artifact" in new_agents:
            # Week 6: /synthesize and /create-artifact unlock announcement
            message = (
                "🚀 **FINAL TOOLS UNLOCKED!**\n\n"
                "You've reached the artifact creation phase. Two powerful additions:\n\n"
                "✨ **/synthesize** (The Synthesizer)\n"
                "Articulate your conclusions. Pull it all together.\n"
                "_Example: /synthesize Here's what I've learned about my thinking process..._\n\n"
                "📝 **/create-artifact** (Graduation Project)\n"
                "Start your 6-section artifact. Prove your transformation.\n"
                "_Example: /create-artifact to begin your graduation project_\n\n"
                "**Why now?**\n"
                "You've practiced all 4 Habits:\n"
                "- ⏸️ Pause (Week 1)\n"
                "- 🎯 Context (Weeks 2-3)\n"
                "- 🔄 Iterate (Weeks 4-5)\n"
                "- 🧠 Think First (Week 6)\n\n"
                "Now you're ready to direct AI toward YOUR standards. You're the director!\n\n"
                "**This Week:**\n"
                "Try /synthesize to reflect on what you've learned.\n"
                "Use /create-artifact when you're ready to start your graduation project.\n\n"
                "You've come so far. Time to prove your transformation! 🌟"
            )
        else:
            # Generic announcement (shouldn't happen with current schedule)
            agent_list = ", ".join([f"/{a}" for a in new_agents])
            message = (
                f"🎉 **NEW AGENTS UNLOCKED!**\n\n"
                f"New this week: {agent_list}\n\n"
                f"Try them out in #thinking-lab!"
            )

        # Get target channel
        channel = await self.get_target_channel(week)
        if not channel:
            logger.error(f"Cannot post agent unlock announcement: no channel for week {week}")
            return

        # Post announcement
        try:
            await self._send_public_message(channel, message)
            logger.info(f"Posted agent unlock announcement for week {week} to {channel.name}")
            self._agent_unlock_today = True

            # Record announcement in database
            channel_id = str(getattr(channel, "id", None))
            self.store.record_unlock_announcement(week, new_agents, channel_id)

        except Exception as e:
            logger.error(f"Failed to post agent unlock announcement for week {week}: {e}")

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
            self._reflection_posted_today = False  # Task 2.5
            self._week_unlock_today = False  # Task 2.5
            self._daily_summary_today = False  # Task 2.6
            self._peer_visibility_today = False  # Task 2.6
            self._reflection_summary_today = False  # Task 2.6
            self._spot_check_today = False  # Task 2.6
            self._agent_unlock_today = False  # Task 3.4
            self._artifact_inactivity_nudges_today = False  # Task 4.1
            self._weekly_artifact_celebration_today = False  # Task 4.2
            self._weekly_parent_emails_today = False  # Task 4.6
            self._week8_parent_reports_today = False  # Task 4.6
            self._sheets_sync_today = False  # Task 7.6
            self._enroll_nudges_today = False  # Task 7.3
            self._token_expiry_check_today = False  # Task 7.4

        week, day = self.get_week_day()

        # 9:00 AM EAT - Friday reflection or weekday node, plus dashboard summary.
        if current_time.hour == 9 and current_time.minute == 0:
            if day == WeekDay.FRIDAY and not self._reflection_posted_today:
                logger.info("Scheduled: 9:00 AM Friday reflection post")
                await self.post_friday_reflection(week)
            elif day != WeekDay.FRIDAY and not self._node_posted_today:
                logger.info("Scheduled: 9:00 AM node post")
                await self.post_node_link(week, day)

            if not self._daily_summary_today:
                logger.info("Scheduled: 9:00 AM daily summary to dashboard")
                await self.post_daily_summary(week)

            # Task 3.4: Agent unlock announcements (Monday only)
            if day == WeekDay.MONDAY and not self._agent_unlock_today:
                logger.info(f"Scheduled: 9:00 AM agent unlock announcement for week {week}")
                await self.post_agent_unlock_announcement(week)

            # Task 4.6 canonical cadence:
            # - Monday 9:00 AM weekly parent updates (reporting prior week)
            if day == WeekDay.MONDAY and not self._weekly_parent_emails_today:
                logger.info("Scheduled: 9:00 AM Monday weekly parent email batch")
                await self.post_weekly_parent_emails(week)

            # - Friday 9:00 AM Week 8 parent report batch
            if week == 8 and day == WeekDay.FRIDAY and not self._week8_parent_reports_today:
                logger.info("Scheduled: 9:00 AM Friday Week 8 parent report batch")
                await self.post_week8_parent_reports(week)

        # 9:15 AM EAT - Post daily prompt
        if current_time.hour == 9 and current_time.minute == 15 and not self._prompt_posted_today:
            logger.info("Scheduled: 9:15 AM prompt post")
            await self.post_daily_prompt(week, day)

        # 10:00 AM EAT - Check escalations (Task 2.4)
        if current_time.hour == 10 and current_time.minute == 0 and not self._escalations_checked_today:
            if self.escalation_system:
                logger.info("Scheduled: 10:00 AM escalation check")
                await self.escalation_system.check_escalations(week)
                self._escalations_checked_today = True

        # 10:05 AM EAT - Proactive artifact inactivity nudges (Task 4.1)
        if (
            current_time.hour == 10
            and current_time.minute == 5
            and not self._artifact_inactivity_nudges_today
        ):
            logger.info("Scheduled: 10:05 AM artifact inactivity nudges")
            await self.post_artifact_inactivity_nudges()

        # :12 every hour - drain deferred /api/enroll Email #2 queue (Task 7.3).
        if current_time.minute == 12:
            run_key = now.strftime("%Y-%m-%d-%H")
            if self._enroll_email_queue_last_run != run_key:
                logger.info("Scheduled: :12 enrollment email queue drain")
                await self.process_enrollment_email_queue()
                self._enroll_email_queue_last_run = run_key

        # 12:00 PM EAT Saturday - Batch unlock next week (Task 2.5)
        if current_time.hour == 12 and current_time.minute == 0 and day == WeekDay.SATURDAY and not self._week_unlock_today:
            logger.info(f"Scheduled: 12:00 PM week {week} batch unlock")
            await self.batch_unlock_week(week)

        # 5:00 PM EAT Friday - Post reflection summary + spot-check (Task 2.6)
        if current_time.hour == 17 and current_time.minute == 0 and day == WeekDay.FRIDAY and not self._reflection_summary_today:
            logger.info("Scheduled: 5:00 PM Friday dashboard summaries")
            await self.post_friday_dashboard_summaries(week)
            if not self._weekly_artifact_celebration_today:
                logger.info("Scheduled: 5:00 PM weekly artifact celebration post")
                await self.post_weekly_artifact_celebration()

        # 6:00 PM EAT - Level 1 inactive student nudges + dashboard summary
        if current_time.hour == 18 and current_time.minute == 0 and not self._peer_visibility_today:
            if self.participation_tracker:
                logger.info("Scheduled: 6:00 PM inactive student check")
                await self.participation_tracker.check_inactive_students(week)

            logger.info("Scheduled: 6:00 PM peer visibility summary to dashboard")
            await self.post_peer_visibility_summary(week)
            if day == WeekDay.WEDNESDAY:
                logger.info("Scheduled: 6:00 PM peer visibility snapshot to weekly channel")
                await self.post_peer_visibility_snapshot(week)

        # 6:05 PM EAT - 48h enroll nudge for linked-but-unenrolled students (Task 7.3)
        if current_time.hour == 18 and current_time.minute == 5 and not self._enroll_nudges_today:
            logger.info("Scheduled: 6:05 PM 48h enroll nudges")
            await self.post_enroll_nudges()

        # Task 4.4: Cluster session automation
        # 6:00 PM EAT (18:00) - Schedule 24-hour announcements for tomorrow's sessions
        if current_time.hour == 18 and current_time.minute == 0:
            logger.info("Scheduled: 6:00 PM cluster session 24h announcements")
            await self._schedule_cluster_announcements_24h()

        # 5:00 PM EAT (17:00) - Create voice channels + send 1-hour reminders for today's sessions
        if current_time.hour == 17 and current_time.minute == 0:
            logger.info("Scheduled: 5:00 PM cluster session 1h reminders")
            await self._send_cluster_reminders_1h()

        # 8:00 PM EAT (20:00) - Cleanup voice channels after sessions
        if current_time.hour == 20 and current_time.minute == 0:
            logger.info("Scheduled: 8:00 PM cluster voice channel cleanup")
            await self._cleanup_cluster_voice_channels()

        # 00:10 AM EAT - Nightly PostgreSQL -> Sheets engagement sync (Task 7.6)
        if current_time.hour == 0 and current_time.minute == 10 and not self._sheets_sync_today:
            logger.info("Scheduled: 00:10 AM nightly PostgreSQL -> Sheets sync")
            await self.run_nightly_sheets_sync()
            self._sheets_sync_today = True

        # 23:00 EAT - Nightly M-Pesa token expiry warning (Task 7.4, Decision H-01 + GAP FIX #4)
        if current_time.hour == 23 and current_time.minute == 0 and not self._token_expiry_check_today:
            logger.info("Scheduled: 23:00 nightly token expiry warning check")
            await self.post_token_expiry_warnings()
            self._token_expiry_check_today = True

    async def run_nightly_sheets_sync(self) -> None:
        """Run nightly engagement sync with dashboard alerting on failure."""
        enabled = os.getenv("SHEETS_SYNC_ENABLED", "false").strip().lower() in {
            "1", "true", "yes", "on"
        }
        if not enabled:
            logger.info("Nightly sheets sync disabled (SHEETS_SYNC_ENABLED=false)")
            return

        database_url = os.getenv("DATABASE_URL", "").strip()
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
        sheet_range = os.getenv("GOOGLE_SHEETS_RANGE", "Student Roster!A:Z").strip()
        creds_path = os.getenv("GOOGLE_SHEETS_CREDS", "").strip()

        if not database_url or not spreadsheet_id:
            message = (
                "Nightly sheets sync skipped: missing DATABASE_URL or GOOGLE_SHEETS_ID."
            )
            logger.error(message)
            await self._notify_dashboard_error(message)
            return

        try:
            from preload_students import sync_engagement_back_to_sheets

            result = await asyncio.to_thread(
                sync_engagement_back_to_sheets,
                database_url,
                spreadsheet_id,
                sheet_range,
                creds_path,
                False,
            )
            logger.info("Nightly sheets sync result: %s", result)
        except Exception as exc:
            logger.error("Nightly sheets sync failed: %s", exc, exc_info=True)
            await self._notify_dashboard_error(
                f"Nightly sheets sync failed: {exc}"
            )

    async def _notify_dashboard_error(self, message: str) -> None:
        """Best-effort dashboard alert for scheduler-level operational failures."""
        try:
            channel_id = int(os.getenv("CHANNEL_FACILITATOR_DASHBOARD", "0"))
        except ValueError:
            channel_id = 0

        if not channel_id:
            return

        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return

        channel = guild.get_channel(channel_id)
        if channel and hasattr(channel, "send"):
            await channel.send(f"⚠️ {message}")

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

    async def _schedule_cluster_announcements_24h(self):
        """
        Schedule 24-hour pre-session announcements for tomorrow's cluster sessions (Task 4.4).

        This runs at 6:00 PM EAT and announces sessions for the next day.
        """
        now = datetime.now(EAT)
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        # Map tomorrow's weekday to cluster IDs
        tomorrow_weekday = (weekday + 1) % 7
        cluster_ids = self.cluster_scheduler.get_clusters_for_weekday(tomorrow_weekday)

        for cluster_id in cluster_ids:
            try:
                await self.cluster_scheduler.announce_cluster_session_24h(cluster_id)
            except Exception as e:
                logger.error(f"Failed to announce cluster {cluster_id} session (24h): {e}")

    async def _send_cluster_reminders_1h(self):
        """
        Send 1-hour pre-session reminders and create voice channels (Task 4.4).

        This runs at 5:00 PM EAT (1 hour before sessions) and creates voice channels.
        """
        now = datetime.now(EAT)
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        cluster_ids = self.cluster_scheduler.get_clusters_for_weekday(weekday)

        for cluster_id in cluster_ids:
            try:
                await self.cluster_scheduler.send_session_reminder_1h(cluster_id)
            except Exception as e:
                logger.error(f"Failed to send 1h reminder for cluster {cluster_id}: {e}")

    async def _cleanup_cluster_voice_channels(self):
        """
        Cleanup voice channels after cluster sessions end (Task 4.4).

        This runs at 8:00 PM EAT (1 hour after sessions end) and deletes voice channels.
        """
        now = datetime.now(EAT)
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        cluster_ids = self.cluster_scheduler.get_clusters_for_weekday(weekday)

        for cluster_id in cluster_ids:
            try:
                await self.cluster_scheduler.cleanup_voice_channel(cluster_id)
            except Exception as e:
                logger.error(f"Failed to cleanup voice channel for cluster {cluster_id}: {e}")

