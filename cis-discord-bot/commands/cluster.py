"""
Cluster Management Commands (Task 4.3)
Trevor-admin commands for cluster assignment and switching
"""

import os
from typing import Dict

import discord
from discord import app_commands
from database.store import StudentStateStore


def _load_weekly_channel_mapping() -> Dict[int, int]:
    """Load week channel IDs from environment variables."""
    return {
        1: int(os.getenv("CHANNEL_WEEK_1", "0")),
        2: int(os.getenv("CHANNEL_WEEK_2_3", "0")),
        3: int(os.getenv("CHANNEL_WEEK_2_3", "0")),
        4: int(os.getenv("CHANNEL_WEEK_4_5", "0")),
        5: int(os.getenv("CHANNEL_WEEK_4_5", "0")),
        6: int(os.getenv("CHANNEL_WEEK_6_7", "0")),
        7: int(os.getenv("CHANNEL_WEEK_6_7", "0")),
        8: int(os.getenv("CHANNEL_WEEK_8", "0")),
    }


def _resolve_channel_mapping_with_fallback(interaction: discord.Interaction) -> Dict[int, int]:
    """Ensure there is always at least one usable target channel."""
    channel_mapping = _load_weekly_channel_mapping()
    if all(not value for value in channel_mapping.values()) and interaction.channel_id:
        channel_mapping[1] = interaction.channel_id
    return channel_mapping


async def switch_cluster(
    interaction: discord.Interaction,
    store: StudentStateStore,
    member: discord.Member,
    new_cluster_id: int,
    reason: str = None
):
    """
    Switch a student to a different cluster (Trevor only).

    Args:
        interaction: Discord interaction
        store: Database store
        member: Student to switch
        new_cluster_id: Target cluster ID (1-8)
        reason: Optional reason for the switch
    """
    # Verify Facilitator role
    facilitator_role = discord.utils.get(interaction.guild.roles, name="Facilitator")
    if not facilitator_role or facilitator_role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ This command requires the @Facilitator role.",
            ephemeral=True
        )
        return

    # Validate cluster ID
    if not 1 <= new_cluster_id <= 8:
        await interaction.response.send_message(
            "❌ Invalid cluster ID. Must be between 1 and 8.",
            ephemeral=True
        )
        return

    # Get student's current cluster
    student = store.get_student(str(member.id))
    if not student:
        await interaction.response.send_message(
            f"❌ {member.display_name} is not in the database yet.",
            ephemeral=True
        )
        return

    old_cluster_id = student["cluster_id"]

    # Attempt cluster switch
    success = store.request_cluster_switch(
        discord_id=str(member.id),
        new_cluster_id=new_cluster_id,
        reason=reason
    )

    if not success:
        await interaction.response.send_message(
            f"❌ Cannot switch {member.display_name} to Cluster {new_cluster_id}: Cluster is full (25 students max).",
            ephemeral=True
        )
        return

    # Update Discord roles
    old_cluster_role_name = f"Cluster-{old_cluster_id}"
    new_cluster_role_name = f"Cluster-{new_cluster_id}"

    old_cluster_role = discord.utils.get(interaction.guild.roles, name=old_cluster_role_name)
    new_cluster_role = discord.utils.get(interaction.guild.roles, name=new_cluster_role_name)

    if old_cluster_role and old_cluster_role in member.roles:
        await member.remove_roles(old_cluster_role)

    if new_cluster_role:
        await member.add_roles(new_cluster_role)

    # Notify student via DM
    try:
        from scheduler.cluster_sessions import ClusterSessionScheduler

        schedule_helper = ClusterSessionScheduler(
            bot=interaction.client,
            store=store,
            guild_id=interaction.guild.id,
            channel_mapping=_resolve_channel_mapping_with_fallback(interaction),
            cohort_start_date=os.getenv("COHORT_1_START_DATE", ""),
        )
        schedule_text = schedule_helper.get_cluster_schedule_text(new_cluster_id)

        cluster_names = {
            1: "A-F", 2: "G-L", 3: "M-R", 4: "S-Z",
            5: "A-F (overflow)", 6: "G-L (overflow)", 7: "M-R (overflow)", 8: "S-Z (overflow)"
        }

        dm_message = f"""🔄 **Cluster Switched**

You've been moved from **Cluster {old_cluster_id}** to **Cluster {new_cluster_id}** ({cluster_names.get(new_cluster_id, 'Unknown')})

📅 Your new session schedule:
Cluster {new_cluster_id} meets {schedule_text}

See you there!
"""

        await member.send(dm_message)
    except Exception:
        pass  # DM failed, but switch succeeded

    # Confirm to Trevor
    reason_text = f"\n**Reason:** {reason}" if reason else ""
    await interaction.response.send_message(
        f"✅ **Cluster Switch Complete**\n\n"
        f"Moved **{member.display_name}** from Cluster {old_cluster_id} → Cluster {new_cluster_id}{reason_text}",
        ephemeral=True
    )


async def show_cluster_roster(
    interaction: discord.Interaction,
    store: StudentStateStore,
    cluster_id: int
):
    """
    Show roster for a specific cluster (Trevor only).

    Args:
        interaction: Discord interaction
        store: Database store
        cluster_id: Cluster ID to show (1-8)
    """
    # Verify Facilitator role
    facilitator_role = discord.utils.get(interaction.guild.roles, name="Facilitator")
    if not facilitator_role or facilitator_role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ This command requires the @Facilitator role.",
            ephemeral=True
        )
        return

    # Validate cluster ID
    if not 1 <= cluster_id <= 8:
        await interaction.response.send_message(
            "❌ Invalid cluster ID. Must be between 1 and 8.",
            ephemeral=True
        )
        return

    # Get students in cluster
    students = store.get_students_by_cluster(cluster_id)

    if not students:
        await interaction.response.send_message(
            f"📋 **Cluster {cluster_id} Roster**\n\nNo students in this cluster yet.",
            ephemeral=True
        )
        return

    # Format roster
    cluster_names = {
        1: "A-F", 2: "G-L", 3: "M-R", 4: "S-Z",
        5: "A-F (overflow)", 6: "G-L (overflow)", 7: "M-R (overflow)", 8: "S-Z (overflow)"
    }

    embed = discord.Embed(
        title=f"📋 Cluster {cluster_id} Roster ({cluster_names.get(cluster_id, 'Unknown')})",
        description=f"Total students: **{len(students)}/25**",
        color=discord.Color.blue()
    )

    # Build student list
    student_list = []
    for i, student in enumerate(students, 1):
        last_name = student.get("last_name") or "Unknown"
        student_list.append(f"{i}. **{last_name}** (ID: {student['discord_id']})")

    # Split into chunks if too long (Discord embed field limit: 1024 chars)
    chunk_size = 20
    for i in range(0, len(student_list), chunk_size):
        chunk = student_list[i:i + chunk_size]
        field_name = "Students" if i == 0 else f"Students (cont.)"
        embed.add_field(
            name=field_name,
            value="\n".join(chunk),
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


async def show_all_cluster_rosters(
    interaction: discord.Interaction,
    store: StudentStateStore
):
    """
    Show summary of all clusters (Trevor only).

    Args:
        interaction: Discord interaction
        store: Database store
    """
    # Verify Facilitator role
    facilitator_role = discord.utils.get(interaction.guild.roles, name="Facilitator")
    if not facilitator_role or facilitator_role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ This command requires the @Facilitator role.",
            ephemeral=True
        )
        return

    # Get all cluster rosters
    rosters = store.get_all_cluster_rosters()

    embed = discord.Embed(
        title="📊 All Cluster Rosters",
        description=f"Total students across all clusters",
        color=discord.Color.blue()
    )

    total_students = 0
    for roster in rosters:
        cluster_id = roster["cluster_id"]
        student_count = roster["student_count"]

        total_students += student_count

        status_emoji = "✅" if student_count > 0 else "⚪"
        capacity_bar = "█" * (student_count // 5) + "░" * (5 - (student_count // 5))

        embed.add_field(
            name=f"{status_emoji} Cluster {cluster_id}",
            value=f"{student_count}/25 students\n[{capacity_bar}]",
            inline=True
        )

    embed.set_footer(text=f"Total students: {total_students}/200")

    await interaction.response.send_message(embed=embed, ephemeral=True)


async def post_session_summary(
    interaction: discord.Interaction,
    store: StudentStateStore,
    cluster_id: int,
    session_notes: str,
    attendance_count: int = None
):
    """
    Post session summary after Trevor completes a live session (Task 4.4).

    Args:
        interaction: Discord interaction
        store: Database store
        cluster_id: Cluster ID (1-8)
        session_notes: Session summary from Trevor
        attendance_count: Optional number of attendees
    """
    # Verify Facilitator role
    facilitator_role = discord.utils.get(interaction.guild.roles, name="Facilitator")
    if not facilitator_role or facilitator_role not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ This command requires the @Facilitator role.",
            ephemeral=True
        )
        return

    # Validate cluster ID
    if not 1 <= cluster_id <= 8:
        await interaction.response.send_message(
            "❌ Invalid cluster ID. Must be between 1 and 8.",
            ephemeral=True
        )
        return

    # Import ClusterSessionScheduler
    from scheduler.cluster_sessions import ClusterSessionScheduler

    channel_mapping = _resolve_channel_mapping_with_fallback(interaction)

    # Create scheduler instance
    cluster_scheduler = ClusterSessionScheduler(
        bot=interaction.client,
        store=store,
        guild_id=interaction.guild.id,
        channel_mapping=channel_mapping,
        cohort_start_date=os.getenv("COHORT_1_START_DATE", ""),
    )

    # Post session summary
    await cluster_scheduler.post_session_summary(
        cluster_id=cluster_id,
        session_notes=session_notes,
        attendance_count=attendance_count
    )

    # Confirm to Trevor
    week = cluster_scheduler.get_current_week()
    await interaction.response.send_message(
        f"✅ **Session Summary Posted**\n\n"
        f"Posted summary for Cluster {cluster_id} to week {week} channel.",
        ephemeral=True
    )
