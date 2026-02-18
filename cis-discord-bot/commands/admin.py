"""
Trevor admin commands for observability dashboards.

Guardrail focus:
- Guardrail #3: aggregate patterns, no ranking language.
- Guardrail #8: private process protected by explicit consent gates.
"""

import logging
import os
import re
from typing import Optional

import discord
from discord.ext import commands

from database.store import StudentStateStore

logger = logging.getLogger(__name__)

# Only this user can run admin commands in production.
TREVOR_DISCORD_ID = os.getenv("TREVOR_DISCORD_ID")
ALLOW_INSECURE_ADMIN = os.getenv("ALLOW_INSECURE_ADMIN", "false").strip().lower() == "true"


def is_trevor(user: discord.User | discord.Member) -> bool:
    """Check if the caller is authorized for admin commands."""
    if TREVOR_DISCORD_ID is None:
        if ALLOW_INSECURE_ADMIN:
            return True
        logger.warning("Admin command denied: TREVOR_DISCORD_ID is not configured.")
        return False
    return str(user.id) == str(TREVOR_DISCORD_ID)


def extract_discord_id(student_mention: Optional[object]) -> Optional[str]:
    """Extract a Discord id from mention text, raw id, or Discord user/member object."""
    if student_mention is None:
        return None

    if hasattr(student_mention, "id"):
        return str(student_mention.id)

    raw = str(student_mention).strip()
    if raw.isdigit():
        return raw

    match = re.match(r"^<@!?(\d+)>$", raw)
    if match:
        return match.group(1)

    return None


async def send_response(ctx_or_interaction, content: str, ephemeral: bool = True):
    """Send to either command context or interaction; defaults to private delivery."""
    if isinstance(ctx_or_interaction, commands.Context):
        if ephemeral:
            try:
                await ctx_or_interaction.author.send(content)
            except Exception:
                await ctx_or_interaction.send("Could not send private admin output. Enable DMs and retry.")
        else:
            await ctx_or_interaction.send(content)
        return

    if isinstance(ctx_or_interaction, discord.Interaction):
        if ctx_or_interaction.response.is_done():
            await ctx_or_interaction.followup.send(content, ephemeral=ephemeral)
        else:
            await ctx_or_interaction.response.send_message(content, ephemeral=ephemeral)
        return

    raise TypeError(f"Expected Context or Interaction, got {type(ctx_or_interaction)}")


async def show_aggregate_patterns(
    ctx: commands.Context | discord.Interaction,
    store: StudentStateStore,
    days: int = 7,
):
    """Show aggregate cohort patterns (Guardrail #3 compliant)."""
    author = ctx.author if isinstance(ctx, commands.Context) else ctx.user

    if not is_trevor(author):
        await send_response(ctx, "This command is for Trevor only.", ephemeral=True)
        return

    try:
        patterns = store.get_aggregate_patterns(days=days)

        response = (
            f"Aggregate Patterns - Last {days} Days\n\n"
            f"Cohort Overview\n"
            f"- Total Students: {patterns['total_students']}\n"
            f"- Active Students: {patterns['active_students']}\n\n"
            "Agent Usage (aggregate only)\n"
        )

        for agent, count in patterns["agent_usage"].items():
            if agent:
                response += f"- /{agent}: {count} uses\n"

        response += "\nZone Distribution\n"
        for zone, count in patterns["zone_distribution"].items():
            response += f"- {zone}: {count} students\n"

        if patterns["milestone_celebrations"]:
            response += "\nMilestone Celebrations\n"
            for milestone, count in patterns["milestone_celebrations"].items():
                label = milestone if milestone is not None else "unknown"
                response += f"- {label} practices: {count} students\n"

        response += "\nEvent Distribution\n"
        for event_type, count in patterns["event_distribution"].items():
            response += f"- {event_type}: {count}\n"

        await send_response(ctx, response, ephemeral=True)

    except Exception as exc:
        await send_response(ctx, f"Error fetching aggregate patterns: {str(exc)}", ephemeral=True)


async def inspect_journey(
    ctx: commands.Context | discord.Interaction,
    store: StudentStateStore,
    student_mention: Optional[object] = None,
):
    """Inspect individual student journey with explicit consent gate (Guardrail #8)."""
    author = ctx.author if isinstance(ctx, commands.Context) else ctx.user

    if not is_trevor(author):
        await send_response(ctx, "This command is for Trevor only.", ephemeral=True)
        return

    if student_mention is None:
        await send_response(
            ctx,
            (
                "Journey Inspection - Consent Required\n\n"
                "Usage: /inspect-journey [@student]\n\n"
                "Steps:\n"
                "1. Student DMs KIRA: I consent to journey inspection\n"
                "2. Trevor runs /inspect-journey [@student]\n"
                "3. Bot returns event-level journey data only\n\n"
                "Consent validity: 24 hours. Student can revoke at any time."
            ),
            ephemeral=True,
        )
        return

    discord_id = extract_discord_id(student_mention)
    if discord_id is None:
        await send_response(ctx, "Invalid student mention. Use: /inspect-journey [@student]", ephemeral=True)
        return

    student = store.get_student(discord_id)
    if not student:
        await send_response(ctx, "Student not found in database.", ephemeral=True)
        return

    if not store.has_active_student_consent(discord_id, consent_type="journey_inspection"):
        await send_response(
            ctx,
            (
                f"No active consent for <@{discord_id}>.\n\n"
                "Ask the student to DM KIRA exactly: `I consent to journey inspection`.\n"
                "Consent is valid for 24 hours and can be revoked by the student."
            ),
            ephemeral=True,
        )
        return

    try:
        events = store.get_student_journey_events(discord_id, limit=50)

        if not events:
            await send_response(ctx, f"Journey: <@{discord_id}>\n\nNo observability events found yet.", ephemeral=True)
            return

        response = (
            f"Journey Inspection: <@{discord_id}>\n\n"
            f"- Total Events: {len(events)}\n"
            f"- Current Week: {student['current_week']}\n"
            f"- Current Zone: {student['zone']}\n\n"
            "Recent Journey:\n"
        )

        for event in events[:20]:
            response += f"\n- {event['event_type']} ({event['timestamp']})\n"
            metadata = event["metadata"]

            if event["event_type"] == "agent_used":
                response += f"  agent: /{metadata.get('agent', 'unknown')}\n"
            elif event["event_type"] == "milestone_reached":
                milestone = metadata.get("milestone", metadata.get("practiced_count", metadata.get("practice_count")))
                response += f"  habit {metadata.get('habit_id')}: {milestone} practices\n"
            elif event["event_type"] == "zone_shift":
                response += (
                    f"  {metadata.get('from_zone')} -> {metadata.get('to_zone')} "
                    f"(Week {metadata.get('week')})\n"
                )
            elif event["event_type"] == "stuck_detected":
                response += f"  inactive_days: {metadata.get('inactive_days')}\n"

        if len(events) > 20:
            response += f"\n... and {len(events) - 20} more events\n"

        await send_response(ctx, response, ephemeral=True)

    except Exception as exc:
        await send_response(ctx, f"Error inspecting journey: {str(exc)}", ephemeral=True)


async def show_stuck_students(
    ctx: commands.Context | discord.Interaction,
    store: StudentStateStore,
    inactive_days: int = 3,
):
    """Show students with no recent agent activity."""
    author = ctx.author if isinstance(ctx, commands.Context) else ctx.user

    if not is_trevor(author):
        await send_response(ctx, "This command is for Trevor only.", ephemeral=True)
        return

    try:
        stuck = store.get_stuck_students(inactive_days=inactive_days)

        if not stuck:
            await send_response(ctx, f"No stuck students detected (inactive {inactive_days}+ days).", ephemeral=True)
            return

        response = (
            f"Potentially Stuck Students (inactive {inactive_days}+ days)\n\n"
            f"Found {len(stuck)} students who have not used CIS agents recently:\n"
        )

        for student in stuck[:20]:
            response += (
                f"\n- hash: `{student['student_id_hash']}`\n"
                f"  week: {student['current_week']}, zone: {student['zone']}\n"
                f"  total_interactions: {student['total_interactions']}\n"
                f"  action: check in privately\n"
                f"  student: <@{student['discord_id']}>\n"
            )

        if len(stuck) > 20:
            response += f"\n... and {len(stuck) - 20} more students\n"

        await send_response(ctx, response, ephemeral=True)

    except Exception as exc:
        await send_response(ctx, f"Error identifying stuck students: {str(exc)}", ephemeral=True)


async def show_zone_shifts(
    ctx: commands.Context | discord.Interaction,
    store: StudentStateStore,
    days: int = 30,
):
    """Show zone shift events for identity transformation tracking."""
    author = ctx.author if isinstance(ctx, commands.Context) else ctx.user

    if not is_trevor(author):
        await send_response(ctx, "This command is for Trevor only.", ephemeral=True)
        return

    try:
        shifts = store.get_zone_shifts(days=days)

        if not shifts:
            await send_response(ctx, f"No zone shifts in the last {days} days.", ephemeral=True)
            return

        response = (
            f"Zone Shifts - Last {days} Days\n\n"
            f"Identity transformation events: {len(shifts)}\n\n"
            "Recent shifts:\n"
        )

        for shift in shifts[:30]:
            response += (
                f"\n- hash: `{shift['student_id_hash']}`\n"
                f"  {shift['from_zone']} -> {shift['to_zone']} (Week {shift['week']})\n"
                f"  {shift['timestamp']}\n"
            )

        if len(shifts) > 30:
            response += f"\n... and {len(shifts) - 30} more shifts\n"

        await send_response(ctx, response, ephemeral=True)

    except Exception as exc:
        await send_response(ctx, f"Error fetching zone shifts: {str(exc)}", ephemeral=True)


async def show_milestones(
    ctx: commands.Context | discord.Interaction,
    store: StudentStateStore,
    days: int = 7,
):
    """Show habit milestone celebrations."""
    author = ctx.author if isinstance(ctx, commands.Context) else ctx.user

    if not is_trevor(author):
        await send_response(ctx, "This command is for Trevor only.", ephemeral=True)
        return

    try:
        milestones = store.get_milestone_celebrations(days=days)

        if not milestones:
            await send_response(ctx, f"No milestone celebrations in the last {days} days.", ephemeral=True)
            return

        by_milestone: dict[int | str, list] = {}
        for milestone in milestones:
            milestone_num = milestone.get("milestone")
            if milestone_num is None:
                key: int | str = "unknown"
            else:
                try:
                    key = int(milestone_num)
                except (TypeError, ValueError):
                    key = str(milestone_num)
            by_milestone.setdefault(key, []).append(milestone)

        response = (
            f"Habit Milestone Celebrations - Last {days} Days\n\n"
            f"Total celebrations: {len(milestones)}\n"
        )

        def _milestone_sort_key(value: int | str):
            if isinstance(value, int):
                return (0, value)
            return (1, str(value))

        for milestone_num in sorted(by_milestone.keys(), key=_milestone_sort_key):
            count = len(by_milestone[milestone_num])
            response += f"\n- {milestone_num} practices milestone: {count} students\n"

        response += "\nRecent celebrations:\n"

        for milestone in milestones[:15]:
            habit_names = {1: "PAUSE", 2: "CONTEXT", 3: "ITERATE", 4: "THINK FIRST"}
            habit_name = habit_names.get(milestone["habit_id"], f"Habit {milestone['habit_id']}")
            response += (
                f"\n- hash: `{milestone['student_id_hash']}`\n"
                f"  {habit_name}: {milestone['milestone']} practices\n"
                f"  total_practices: {milestone['practiced_count']}\n"
                f"  {milestone['timestamp']}\n"
            )

        if len(milestones) > 15:
            response += f"\n... and {len(milestones) - 15} more celebrations\n"

        await send_response(ctx, response, ephemeral=True)

    except Exception as exc:
        await send_response(ctx, f"Error fetching milestones: {str(exc)}", ephemeral=True)


async def unlock_week(
    ctx: commands.Context | discord.Interaction,
    store: StudentStateStore,
    student_mention: object,
    week_number: int,
    reason: str = "Manual override by Trevor",
):
    """
    Manually unlock next week for a student (Task 2.5).

    Use cases: illness, emergency, accelerated pacing, special circumstances.

    Args:
        ctx: Command context or interaction
        store: Database store
        student_mention: Student to unlock (@mention)
        week_number: Week number to unlock (1-7)
        reason: Override reason (logged for culture monitoring)
    """
    author = ctx.author if isinstance(ctx, commands.Context) else ctx.user

    if not is_trevor(author):
        await send_response(ctx, "This command is for Trevor only.", ephemeral=True)
        return

    discord_id = extract_discord_id(student_mention)
    if discord_id is None:
        await send_response(ctx, "Invalid student mention. Use: /unlock-week [@student] [week] [reason]", ephemeral=True)
        return

    if week_number < 1 or week_number > 7:
        await send_response(ctx, "Invalid week number. Must be between 1 and 7.", ephemeral=True)
        return

    student = store.get_student(discord_id)
    if not student:
        await send_response(ctx, "Student not found in database.", ephemeral=True)
        return

    current_week = student['current_week']

    # Check if already unlocked
    if store.has_unlocked_next_week(discord_id, current_week):
        await send_response(
            ctx,
            f"<@{discord_id}> has already unlocked Week {current_week + 1}.\n\n"
            f"Current week: {current_week}",
            ephemeral=True
        )
        return

    try:
        # Perform manual unlock
        trevor_id = str(author.id)
        store.unlock_next_week(
            discord_id=discord_id,
            current_week=week_number,
            manually_unlocked=True,
            unlocked_by=trevor_id,
            unlock_reason=reason
        )

        await send_response(
            ctx,
            f"✅ **Week Unlocked**\n\n"
            f"Student: <@{discord_id}>\n"
            f"Week {week_number} → Week {week_number + 1} unlocked\n\n"
            f"Reason: {reason}\n\n"
            f"Logged to culture monitoring.",
            ephemeral=True
        )

        logger.info(f"Trevor manually unlocked Week {week_number} for <@{discord_id}> (reason: {reason})")

    except Exception as exc:
        await send_response(ctx, f"Error unlocking week: {str(exc)}", ephemeral=True)

