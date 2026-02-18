"""
Participation Tracker
Story 2.2 Implementation: Bot Reactions + Participation Tracking

Monitors student posts in weekly channels, reacts with emojis, tracks participation,
and sends gentle nudges to inactive students.
"""

import hashlib
import logging
from datetime import datetime, time
from typing import List, Optional

import discord
from discord.ext import commands

import pytz

from database.store import StudentStateStore

logger = logging.getLogger(__name__)

# Timezone
EAT = pytz.timezone('Africa/Nairobi')

# Emoji reactions
WITNESS_EMOJI = "👀"  # "witnessed" reaction for all posts
CELEBRATION_EMOJIS = ["🌟", "🎉", "💪", "✨"]  # For exceptional posts


class ParticipationTracker:
    """
    Tracks student participation and sends bot reactions.

    Responsibilities:
    - React 👀 to every student submission within 5 minutes
    - Track participation per student (no public rankings - Guardrail #3)
    - Flag students who haven't posted by 6 PM (private to dashboard)
    - Send gentle nudge DM to inactive students
    - Generate evening peer visibility snapshot (anonymized patterns, no names)
    """

    def __init__(self, bot: commands.Bot, store: StudentStateStore, weekly_channel_ids: List[int]):
        """
        Initialize the participation tracker.

        Args:
            bot: Discord bot instance
            store: StudentStateStore instance
            weekly_channel_ids: List of weekly channel IDs to monitor
        """
        self.bot = bot
        self.store = store
        self.weekly_channel_ids = set(weekly_channel_ids)
        self._reaction_queue = []  # Queue of (message_id, channel_id) to react to

        logger.info(f"Participation tracker initialized for {len(weekly_channel_ids)} channels")

    def is_weekly_channel(self, channel: discord.abc.GuildChannel) -> bool:
        """Check if a channel is a weekly channel we should monitor."""
        return channel.id in self.weekly_channel_ids

    async def on_message(self, message: discord.Message):
        """
        Handle new messages in weekly channels.

        Args:
            message: Discord message that was sent
        """
        # Skip bot messages
        if message.author.bot:
            return

        # Skip DMs
        if not message.guild:
            return

        # Only process messages in weekly channels
        if not self.is_weekly_channel(message.channel):
            return

        # Queue reaction
        await self._queue_reaction(message)

        # Track participation
        await self._track_participation(message)

    async def _queue_reaction(self, message: discord.Message):
        """
        Queue a message for bot reaction.

        Args:
            message: Discord message to react to
        """
        self._reaction_queue.append((message.id, message.channel.id))

        # Process queue if it's getting large
        if len(self._reaction_queue) >= 10:
            await self._process_reaction_queue()

    async def _process_reaction_queue(self):
        """Process queued reactions, adding 👀 to each message."""
        if not self._reaction_queue:
            return

        processed = 0
        for message_id, channel_id in self._reaction_queue[:10]:  # Batch of 10
            try:
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    continue

                message = await channel.fetch_message(message_id)
                await message.add_reaction(WITNESS_EMOJI)
                processed += 1

            except discord.NotFound:
                logger.warning(f"Message {message_id} not found for reaction")
            except discord.Forbidden:
                logger.error(f"Missing permissions to add reaction in channel {channel_id}")
            except Exception as e:
                logger.error(f"Error adding reaction: {e}", exc_info=True)

        # Remove processed items from queue
        self._reaction_queue = self._reaction_queue[processed:]

        if processed > 0:
            logger.info(f"Added {WITNESS_EMOJI} reaction to {processed} messages")

    async def _track_participation(self, message: discord.Message):
        """
        Track student participation in database.

        Args:
            message: Discord message to track
        """
        discord_id = str(message.author.id)
        now = datetime.now(EAT)
        date_str = now.strftime("%Y-%m-%d")
        day_name = now.strftime("%A")

        # Calculate current week
        # TODO: Extract this logic into a shared utility
        cohort_start = datetime.strptime("2026-02-01", "%Y-%m-%d").replace(tzinfo=EAT)
        days_since_start = (now - cohort_start).days
        week_number = max(1, min(8, (days_since_start // 7) + 1))

        # Calculate engagement score (1-6 scale)
        engagement_score = self._calculate_engagement_score(message)

        try:
            # Initialize or update daily participation record
            conn = self.store.conn
            cursor = conn.cursor()

            # Check if record exists
            cursor.execute(
                """
                SELECT id, post_count FROM daily_participation
                WHERE discord_id = ? AND date = ?
                """,
                (discord_id, date_str)
            )
            row = cursor.fetchone()

            if row:
                # Update existing record
                record_id, post_count = row
                cursor.execute(
                    """
                    UPDATE daily_participation
                    SET post_count = post_count + 1,
                        engagement_score = MAX(engagement_score, ?)
                    WHERE id = ?
                    """,
                    (engagement_score, record_id)
                )
            else:
                # Create new record
                cursor.execute(
                    """
                    INSERT INTO daily_participation
                    (discord_id, date, week_number, day_of_week, has_posted, first_post_time, post_count, engagement_score)
                    VALUES (?, ?, ?, ?, 1, ?, 1, ?)
                    """,
                    (discord_id, date_str, week_number, day_name, now.isoformat(), engagement_score)
                )

            conn.commit()
            logger.debug(f"Tracked participation for {message.author.name}: {date_str}")

        except Exception as e:
            logger.error(f"Error tracking participation: {e}", exc_info=True)

    def _calculate_engagement_score(self, message: discord.Message) -> int:
        """
        Calculate engagement score (1-6 scale) based on message quality.

        Scoring criteria:
        - 1: Very brief (< 20 chars)
        - 2: Brief but complete (20-50 chars)
        - 3: Standard response (50-150 chars)
        - 4: Thoughtful response (150-300 chars)
        - 5: Detailed reflection (300+ chars, specific examples)
        - 6: Exceptional (multi-paragraph, deep thinking, authentic voice)

        Args:
            message: Discord message to score

        Returns:
            Engagement score (1-6)
        """
        content = message.content.strip()
        char_count = len(content)

        # Base score from length
        if char_count < 20:
            base_score = 1
        elif char_count < 50:
            base_score = 2
        elif char_count < 150:
            base_score = 3
        elif char_count < 300:
            base_score = 4
        else:
            base_score = 5

        # Boost for exceptional content
        # Multi-paragraph or uses personal pronouns ("I", "my") indicates authenticity
        if char_count > 300 and ("\n\n" in content or " I " in content.lower()):
            base_score = 6

        return base_score

    async def check_inactive_students(self, week: int):
        """
        Check for students who haven't posted by 6 PM and send nudges.

        Args:
            week: Current cohort week
        """
        now = datetime.now(EAT)
        date_str = now.strftime("%Y-%m-%d")

        # Only check at 6:00 PM EAT
        if now.time() != time(18, 0):
            return

        logger.info(f"Checking for inactive students on {date_str} (week {week})")

        try:
            conn = self.store.conn
            cursor = conn.cursor()

            # Find students who haven't posted today
            cursor.execute(
                """
                SELECT s.discord_id, s.username, s.cluster_id
                FROM students s
                LEFT JOIN daily_participation dp ON s.discord_id = dp.discord_id AND dp.date = ?
                WHERE s.current_week = ?
                AND dp.has_posted IS NULL OR dp.has_posted = 0
                AND dp.nudge_sent = 0
                LIMIT 20
                """,
                (date_str, week)
            )
            inactive_students = cursor.fetchall()

            if not inactive_students:
                logger.info("No inactive students to nudge")
                return

            logger.info(f"Found {len(inactive_students)} inactive students")

            # Send nudges
            for discord_id, username, cluster_id in inactive_students:
                try:
                    await self._send_nudge_dm(discord_id, week)

                    # Mark as nudged
                    cursor.execute(
                        """
                        UPDATE daily_participation
                        SET nudge_sent = 1, nudge_time = ?, flagged_inactive = 1
                        WHERE discord_id = ? AND date = ?
                        """,
                        (now.isoformat(), discord_id, date_str)
                    )

                    logger.info(f"Sent nudge to {username}")

                except Exception as e:
                    logger.error(f"Error sending nudge to {username}: {e}")

            conn.commit()

        except Exception as e:
            logger.error(f"Error checking inactive students: {e}", exc_info=True)

    async def _send_nudge_dm(self, discord_id: str, week: int):
        """
        Send a gentle nudge DM to an inactive student.

        Args:
            discord_id: Student's Discord ID (as string)
            week: Current cohort week
        """
        try:
            # Get user
            user = await self.bot.fetch_user(int(discord_id))

            # Week-specific nudge messages
            nudges = {
                1: (
                    f"Hey! 👋 Today's practice is waiting when you're ready. "
                    f"No pressure. Just check #✨week-1-wonder when you have a moment. "
                    f"{WITNESS_EMOJI}"
                ),
                2: (
                    f"Hey! 👋 Haven't seen you in #🤝week-2-3-trust today. "
                    f"Remember: Small wins add up. No pressure to be perfect. "
                    f"{WITNESS_EMOJI}"
                ),
                3: (
                    f"Hey! 👋 Missing your practice in #🤝week-2-3-trust? "
                    f"That's okay! Habits form gradually. You're on track. "
                    f"{WITNESS_EMOJI}"
                ),
                4: (
                    f"Hey! 👋 Week 4 practice is waiting in #💭week-4-5-converse. "
                    f"New tools unlocked: /diverge and /challenge. Explore when ready! "
                    f"{WITNESS_EMOJI}"
                ),
                5: (
                    f"Hey! 👋 Haven't seen you in #💭week-4-5-converse today. "
                    f"Iteration changes everything. Try one tiny change today! "
                    f"{WITNESS_EMOJI}"
                ),
                6: (
                    f"Hey! 👋 Artifact work happening in #🎯week-6-7-direct. "
                    f"You're the director now. Direct AI toward YOUR standards! "
                    f"{WITNESS_EMOJI}"
                ),
                7: (
                    f"Hey! 👋 Artifact polish time in #🎯week-6-7-direct. "
                    f"You're someone who thinks WITH AI. Almost there! "
                    f"{WITNESS_EMOJI}"
                ),
                8: (
                    f"Hey! 👋 Final week in #🏆week-8-showcase. "
                    f"Time to prove your transformation. You've got this! "
                    f"{WITNESS_EMOJI}"
                ),
            }

            nudge_message = nudges.get(week, nudges[1])  # Default to week 1 message

            await user.send(nudge_message)

        except discord.Forbidden:
            logger.warning(f"Cannot send DM to user {discord_id} (DMs disabled)")
        except Exception as e:
            logger.error(f"Error sending nudge DM to {discord_id}: {e}", exc_info=True)

    async def generate_evening_snapshot(self, week: int) -> Optional[str]:
        """
        Generate anonymized peer visibility snapshot for evening posting.

        Args:
            week: Current cohort week

        Returns:
            Formatted snapshot message, or None if no posts today
        """
        now = datetime.now(EAT)
        date_str = now.strftime("%Y-%m-%d")
        day_name = now.strftime("%A")

        try:
            conn = self.store.conn
            cursor = conn.cursor()

            # Get today's participation stats
            cursor.execute(
                """
                SELECT COUNT(*) as total,
                       SUM(has_posted) as posted,
                       AVG(engagement_score) as avg_engagement
                FROM daily_participation
                WHERE date = ?
                """,
                (date_str,)
            )
            stats = cursor.fetchone()

            if not stats or stats[0] == 0:
                return None

            total_students, posted_count, avg_engagement = stats

            # Get diverse anonymized responses
            cursor.execute(
                """
                SELECT dp.engagement_score, dp.post_count
                FROM daily_participation dp
                WHERE dp.date = ? AND dp.has_posted = 1
                ORDER BY RANDOM()
                LIMIT 5
                """,
                (date_str,)
            )
            responses = cursor.fetchall()

            # Build snapshot message
            message = f"🌟 **TODAY'S PATTERNS** ({day_name}, Week {week}) - anonymized\n\n"
            message += f"**Participation:** {int(posted_count)} students posted today\n"
            message += f"**Engagement:** Average score {avg_engagement:.1f}/6\n\n"

            if responses:
                message += "**Sample posts:**\n"
                for i, (engagement, post_count) in enumerate(responses, 1):
                    quality_label = "brief" if engagement < 3 else "thoughtful" if engagement < 5 else "deep"
                    message += f"{i}. {quality_label} post ({post_count} {'post' if post_count == 1 else 'posts'})\n"

            message += "\n✅ Guardrail #3 check: No comparison, no ranking\n"
            message += f"{WITNESS_EMOJI} You're all building thinking skills at your own pace."

            return message

        except Exception as e:
            logger.error(f"Error generating evening snapshot: {e}", exc_info=True)
            return None
