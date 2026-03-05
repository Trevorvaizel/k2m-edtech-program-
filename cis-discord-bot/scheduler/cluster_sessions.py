"""
Cluster Live Session Automation (Task 4.4)
Story 5.1 Implementation: Live Session Scheduling + Voice Channel Management

Handles:
- 24-hour pre-session announcements (cluster-targeted)
- 1-hour reminders
- Voice channel creation/deletion
- Post-session summaries
Session schedule: 3 sessions/week, 60 min, 6 PM EAT
"""

import logging
import os
from datetime import datetime, timedelta

import pytz

EAT = pytz.timezone('Africa/Nairobi')

logger = logging.getLogger(__name__)


class ClusterSessionScheduler:
    """
    Manages automated cluster session announcements and voice channels.

    Session Schedule (Story 5.1):
    - 3 live-session days per week at 6:00 PM EAT
    - Clusters alternate across those days
    """

    # Default session schedule: 3 sessions/week (MWF), alternating clusters.
    DEFAULT_CLUSTER_SCHEDULE = {
        1: (0, 18, 0),  # Monday 6:00 PM EAT
        2: (2, 18, 0),  # Wednesday 6:00 PM EAT
        3: (4, 18, 0),  # Friday 6:00 PM EAT
        4: (0, 18, 0),  # Monday 6:00 PM EAT
        5: (2, 18, 0),  # Wednesday 6:00 PM EAT
        6: (4, 18, 0),  # Friday 6:00 PM EAT
        7: (0, 18, 0),  # Monday 6:00 PM EAT
        8: (2, 18, 0),  # Wednesday 6:00 PM EAT
    }

    CLUSTER_NAMES = {
        1: "A-F",
        2: "G-L",
        3: "M-R",
        4: "S-Z",
        5: "A-F (overflow)",
        6: "G-L (overflow)",
        7: "M-R (overflow)",
        8: "S-Z (overflow)",
    }

    WEEKDAY_NAMES = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    def __init__(self, bot, store, guild_id, channel_mapping, cohort_start_date=None):
        """
        Initialize cluster session scheduler.

        Args:
            bot: Discord bot instance
            store: StudentStateStore instance
            guild_id: Discord server ID
            channel_mapping: Week number → Discord channel ID mapping
            cohort_start_date: Cohort start date (YYYY-MM-DD); falls back to env
        """
        self.bot = bot
        self.store = store
        self.guild_id = guild_id
        self.channel_mapping = channel_mapping
        self.cohort_start_date = self._parse_cohort_start_date(
            cohort_start_date or os.getenv("COHORT_1_START_DATE", "")
        )
        self.CLUSTER_SCHEDULE = self._load_cluster_schedule()

        # Track announcements to prevent duplicates
        self._announced_24h = set()  # {(cluster_id, date)}
        self._announced_1h = set()   # {(cluster_id, date)}
        self._voice_channels = {}      # {cluster_id: voice_channel_id}

    def _parse_cohort_start_date(self, value):
        """Parse YYYY-MM-DD into a timezone-aware EAT datetime."""
        if not value:
            return None

        try:
            return EAT.localize(datetime.strptime(value, "%Y-%m-%d"))
        except ValueError:
            logger.warning("Invalid COHORT_1_START_DATE '%s'; defaulting current week to 1", value)
            return None

    def _load_cluster_schedule(self):
        """
        Load schedule override from env when available.

        Env format (optional): CLUSTER_SESSION_SCHEDULE_JSON
        {"1":[0,18,0],"2":[2,18,0],...,"8":[2,18,0]}
        """
        raw = os.getenv("CLUSTER_SESSION_SCHEDULE_JSON", "").strip()
        if not raw:
            return dict(self.DEFAULT_CLUSTER_SCHEDULE)

        try:
            import json

            parsed = json.loads(raw)
            schedule = {}
            for cluster_id in range(1, 9):
                value = parsed.get(str(cluster_id))
                if not isinstance(value, list) or len(value) != 3:
                    raise ValueError(f"Missing/invalid schedule entry for cluster {cluster_id}")

                weekday, hour, minute = value
                if not (
                    isinstance(weekday, int)
                    and isinstance(hour, int)
                    and isinstance(minute, int)
                    and 0 <= weekday <= 6
                    and 0 <= hour <= 23
                    and 0 <= minute <= 59
                ):
                    raise ValueError(f"Invalid schedule tuple for cluster {cluster_id}: {value}")

                schedule[cluster_id] = (weekday, hour, minute)

            return schedule
        except Exception as exc:
            logger.warning(
                "Invalid CLUSTER_SESSION_SCHEDULE_JSON; using default schedule: %s",
                exc,
            )
            return dict(self.DEFAULT_CLUSTER_SCHEDULE)

    def get_current_week(self) -> int:
        """Return current cohort week (1-8), defaulting to week 1."""
        if self.cohort_start_date is None:
            return 1

        now = datetime.now(EAT)
        days_since_start = (now - self.cohort_start_date).days
        if days_since_start < 0:
            return 1

        return min((days_since_start // 7) + 1, 8)

    def get_clusters_for_weekday(self, weekday: int):
        """Return all cluster IDs that meet on the given weekday."""
        return [
            cluster_id
            for cluster_id, schedule in self.CLUSTER_SCHEDULE.items()
            if schedule[0] == weekday
        ]

    def get_cluster_schedule_text(self, cluster_id: int) -> str:
        """Return human-readable schedule text for a cluster."""
        if cluster_id not in self.CLUSTER_SCHEDULE:
            return "Unknown schedule"

        weekday, hour, minute = self.CLUSTER_SCHEDULE[cluster_id]
        hour_12 = hour % 12 or 12
        am_pm = "AM" if hour < 12 else "PM"
        day_name = self.WEEKDAY_NAMES.get(weekday, "Unknown day")
        return f"{day_name} {hour_12}:{minute:02d} {am_pm} EAT"

    def get_session_time(self, cluster_id: int) -> datetime:
        """
        Get next scheduled session time for a cluster.

        Args:
            cluster_id: Cluster ID (1-8)

        Returns:
            datetime of next session
        """
        if cluster_id not in self.CLUSTER_SCHEDULE:
            raise ValueError(f"Invalid cluster_id: {cluster_id}")

        weekday, hour, minute = self.CLUSTER_SCHEDULE[cluster_id]
        now = datetime.now(EAT)

        # Calculate next session
        days_ahead = (weekday - now.weekday()) % 7
        if days_ahead == 0 and now.hour >= hour:
            days_ahead = 7  # Next week if already passed today

        session_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        session_time = session_time + timedelta(days=days_ahead)

        return session_time

    async def announce_cluster_session_24h(self, cluster_id: int, topic: str = None):
        """
        Post 24-hour pre-session announcement to week channel.

        Args:
            cluster_id: Cluster ID (1-8)
            topic: Optional session topic
        """
        now = datetime.now(EAT)
        date_key = now.strftime('%Y-%m-%d')

        # Check if already announced
        if (cluster_id, date_key) in self._announced_24h:
            logger.info(f"Already posted 24h announcement for cluster {cluster_id} today")
            return

        # Get current week for channel targeting
        week = self.get_current_week()

        # Get target channel (week-specific)
        channel_id = self.channel_mapping.get(week)
        if not channel_id:
            logger.error(f"No channel configured for week {week}")
            return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                logger.error(f"Guild {self.guild_id} not found")
                return

            channel = guild.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel {channel_id} not found")
                return

            # Build announcement
            session_time = self.get_session_time(cluster_id)
            session_time_str = session_time.strftime("%A, %B %d at %I:%M %p EAT")

            topic_text = f"\n🎯 **Topic:** {topic}" if topic else ""

            message = f"""📅 **Cluster {cluster_id} Live Session Tomorrow!** 🚀

You're invited to Cluster {cluster_id} (Last names: {self.CLUSTER_NAMES.get(cluster_id, 'Unknown')})

🗓️ **When:** {session_time_str}
📍 **Where:** Voice channel will open 1 hour before session

{topic_text}

**What to bring:**
• Your questions about this week's content
• Examples from your practice this week
• Open mind and curious energy! 🧠

See you there!
"""

            await channel.send(message)
            logger.info(f"Posted 24h announcement for cluster {cluster_id} to {channel.name}")
            self._announced_24h.add((cluster_id, date_key))

        except Exception as e:
            logger.error(f"Failed to announce cluster {cluster_id} session (24h): {e}")

    async def send_session_reminder_1h(self, cluster_id: int):
        """
        Send 1-hour pre-session reminder and create voice channel.

        Args:
            cluster_id: Cluster ID (1-8)
        """
        now = datetime.now(EAT)
        date_key = now.strftime('%Y-%m-%d')

        # Check if already announced
        if (cluster_id, date_key) in self._announced_1h:
            logger.info(f"Already posted 1h reminder for cluster {cluster_id} today")
            return

        # Get current week
        week = self.get_current_week()

        # Get target channel
        channel_id = self.channel_mapping.get(week)
        if not channel_id:
            logger.error(f"No channel configured for week {week}")
            return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return

            channel = guild.get_channel(channel_id)
            if not channel:
                return

            # Create voice channel
            facilitator_role = None
            roles = getattr(guild, "roles", []) or []
            if isinstance(roles, (list, tuple, set)):
                for role in roles:
                    if str(getattr(role, "name", "")) == "Facilitator":
                        facilitator_role = role
                        break

            voice_channel = await self.store.create_cluster_voice_channel(
                guild=guild,
                cluster_id=cluster_id,
                bot=self.bot,
                facilitator_role=facilitator_role,
            )

            if voice_channel:
                self._voice_channels[cluster_id] = voice_channel.id
                logger.info(f"Created voice channel for cluster {cluster_id}: {voice_channel.name}")

                # Send reminder with voice channel link
                invite = None
                create_invite = getattr(voice_channel, "create_invite", None)
                if callable(create_invite):
                    invite = await create_invite(max_age=7200, max_uses=0, unique=False)

                message = f"""⏰ **Cluster {cluster_id} Session Starting Soon!** 🔥

Voice channel is NOW OPEN!

🎤 **Join Voice Channel:** {invite.url if invite else voice_channel.mention}

Session starts at 6:00 PM EAT.

Bring your thinking caps! 🧠✨
"""

                await channel.send(message)
                logger.info(f"Posted 1h reminder for cluster {cluster_id} with voice channel link")
                self._announced_1h.add((cluster_id, date_key))

        except Exception as e:
            logger.error(f"Failed to send 1h reminder for cluster {cluster_id}: {e}")

    async def cleanup_voice_channel(self, cluster_id: int):
        """
        Delete voice channel after session ends.

        Args:
            cluster_id: Cluster ID (1-8)
        """
        if cluster_id not in self._voice_channels:
            persisted_channel_id = self.store.get_active_voice_channel_id(cluster_id)
            if persisted_channel_id:
                try:
                    self._voice_channels[cluster_id] = int(persisted_channel_id)
                except (TypeError, ValueError):
                    logger.warning(
                        "Invalid persisted voice channel id '%s' for cluster %s",
                        persisted_channel_id,
                        cluster_id,
                    )
                    return
            else:
                logger.warning(f"No active voice channel found for cluster {cluster_id}")
                return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return

            voice_channel_id = self._voice_channels[cluster_id]
            voice_channel = guild.get_channel(voice_channel_id)

            if voice_channel:
                await self.store.delete_cluster_voice_channel(voice_channel)
                del self._voice_channels[cluster_id]
                logger.info(f"Deleted voice channel for cluster {cluster_id}")
            else:
                logger.warning(f"Voice channel {voice_channel_id} not found for cleanup")
                self.store.mark_voice_channel_deleted(str(voice_channel_id))
                if cluster_id in self._voice_channels:
                    del self._voice_channels[cluster_id]

        except Exception as e:
            logger.error(f"Failed to cleanup voice channel for cluster {cluster_id}: {e}")

    async def post_session_summary(
        self,
        cluster_id: int,
        session_notes: str,
        attendance_count: int = None
    ):
        """
        Post session summary after Trevor completes session (Task 4.4).

        Args:
            cluster_id: Cluster ID (1-8)
            session_notes: Session summary from Trevor
            attendance_count: Optional number of attendees
        """
        # Get current week
        week = self.get_current_week()

        # Get target channel
        channel_id = self.channel_mapping.get(week)
        if not channel_id:
            logger.error(f"No channel configured for week {week}")
            return

        try:
            guild = self.bot.get_guild(self.guild_id)
            if not guild:
                return

            channel = guild.get_channel(channel_id)
            if not channel:
                return

            # Build summary
            effective_attendance_count = attendance_count
            attendees = []

            if effective_attendance_count is None:
                voice_channel_id = self._voice_channels.get(cluster_id)
                if voice_channel_id is None:
                    persisted = self.store.get_active_voice_channel_id(cluster_id)
                    if persisted:
                        try:
                            voice_channel_id = int(persisted)
                        except (TypeError, ValueError):
                            voice_channel_id = None

                if voice_channel_id:
                    voice_channel = guild.get_channel(voice_channel_id)
                    members = getattr(voice_channel, "members", []) if voice_channel else []
                    attendees = [
                        str(member.id)
                        for member in members
                        if not getattr(member, "bot", False)
                    ]
                    if attendees:
                        effective_attendance_count = len(attendees)

            attendance_text = (
                f"\n**Attendance:** {effective_attendance_count} students"
                if effective_attendance_count is not None
                else ""
            )

            message = f"""📚 **Cluster {cluster_id} Session Summary** 🎓

{session_notes}
{attendance_text}

Great session everyone! See you next week! 🚀
"""

            await channel.send(message)
            logger.info(f"Posted session summary for cluster {cluster_id} to {channel.name}")

            # Record attendance in database
            if effective_attendance_count is not None or attendees:
                now = datetime.now(EAT).isoformat()
                self.store.record_session_attendance(
                    cluster_id=cluster_id,
                    session_date=now,
                    attendees=attendees,
                    attendance_count=effective_attendance_count,
                )

        except Exception as e:
            logger.error(f"Failed to post session summary for cluster {cluster_id}: {e}")

    def check_and_post_sessions(self, current_time: datetime = None):
        """
        Main loop: Check time and trigger session automation.

        Args:
            current_time: Current datetime (for testing)
        """
        if current_time is None:
            current_time = datetime.now(EAT)

        hour = current_time.hour
        minute = current_time.minute
        weekday = current_time.weekday()

        # 5:00 PM EAT (17:00) - 1 hour before session: Create voice channel + send reminder
        if hour == 17 and minute == 0:
            for cluster_id in self.get_clusters_for_weekday(weekday):
                logger.info(f"Triggering 1-hour reminder for cluster {cluster_id}")
                # Note: This would need to be awaited in an async context

        # 8:00 PM EAT (20:00) - 1 hour after session: Cleanup voice channel
        if hour == 20 and minute == 0:
            for cluster_id in self.get_clusters_for_weekday(weekday):
                logger.info(f"Triggering voice channel cleanup for cluster {cluster_id}")
                # Note: This would need to be awaited in an async context

        # 6:00 PM EAT (18:00) previous day: 24-hour announcement
        if hour == 18 and minute == 0:
            next_day = current_time + timedelta(days=1)
            next_weekday = next_day.weekday()

            for cluster_id in self.get_clusters_for_weekday(next_weekday):
                logger.info(f"Scheduling 24h announcement for cluster {cluster_id} tomorrow")
                # Note: This would need to be awaited in an async context
