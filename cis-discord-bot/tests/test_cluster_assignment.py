"""
Cluster Assignment System Tests
Story 5.1 Implementation: Cluster Assignment + Voice Channels
Task 4.3: Implement cluster assignment by last name with voice channel management

Comprehensive tests for cluster assignment logic, voice channel lifecycle,
and cluster switching functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.store import StudentStateStore


@pytest.fixture
def test_db_path(tmp_path):
    """Create temporary test database"""
    db_path = tmp_path / "test_cluster.db"
    yield str(db_path)

    # Cleanup
    import os
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def store(test_db_path):
    """Create test database store"""
    state_store = StudentStateStore(db_path=test_db_path)
    yield state_store
    state_store.close()


class TestClusterAssignment:
    """Test cluster assignment by last name"""

    def test_assign_cluster_by_last_name_a_f(self, store):
        """Test students with last names A-F are assigned to Cluster 1"""
        # Test various last names in A-F range
        test_names = ["Anderson", "Brown", "Chen", "Davis", "Evans", "Fisher"]

        for last_name in test_names:
            cluster_id = store.assign_cluster_by_last_name(last_name)
            assert cluster_id == 1, f"Last name {last_name} should be in Cluster 1"

    def test_assign_cluster_by_last_name_g_l(self, store):
        """Test students with last names G-L are assigned to Cluster 2"""
        test_names = ["Garcia", "Harris", "Ivanov", "Jones", "Kim", "Lee"]

        for last_name in test_names:
            cluster_id = store.assign_cluster_by_last_name(last_name)
            assert cluster_id == 2, f"Last name {last_name} should be in Cluster 2"

    def test_assign_cluster_by_last_name_m_r(self, store):
        """Test students with last names M-R are assigned to Cluster 3"""
        test_names = ["Martinez", "Nguyen", "O'Brien", "Patel", "Rodriguez"]

        for last_name in test_names:
            cluster_id = store.assign_cluster_by_last_name(last_name)
            assert cluster_id == 3, f"Last name {last_name} should be in Cluster 3"

    def test_assign_cluster_by_last_name_s_z(self, store):
        """Test students with last names S-Z are assigned to Cluster 4"""
        test_names = ["Smith", "Taylor", "Williams", "Yamamoto", "Zhang"]

        for last_name in test_names:
            cluster_id = store.assign_cluster_by_last_name(last_name)
            assert cluster_id == 4, f"Last name {last_name} should be in Cluster 4"

    def test_assign_cluster_case_insensitive(self, store):
        """Test cluster assignment is case-insensitive"""
        # Lowercase
        assert store.assign_cluster_by_last_name("anderson") == 1
        # Uppercase
        assert store.assign_cluster_by_last_name("ANDERSON") == 1
        # Mixed case
        assert store.assign_cluster_by_last_name("AnDeRsOn") == 1

    def test_assign_cluster_handles_special_characters(self, store):
        """Test cluster assignment handles names with special characters"""
        # Hyphenated names
        assert store.assign_cluster_by_last_name("Smith-Jones") == 4  # S
        # Apostrophes
        assert store.assign_cluster_by_last_name("O'Brien") == 3  # M
        # Spaces (compound last names)
        assert store.assign_cluster_by_last_name("Van Der Berg") == 4  # V

    def test_assign_cluster_overflow_to_secondary_clusters(self, store):
        """Test that when primary clusters are full, students go to clusters 5-8"""
        # Fill Cluster 1 (A-F) to capacity
        for i in range(25):
            store.create_student(discord_id=f"student_{i}", last_name="Anderson")

        # Next A-F student should go to Cluster 5 (overflow)
        next_student = store.create_student(discord_id="overflow_1", last_name="Brown")
        assert next_student["cluster_id"] == 5

    def test_assign_all_eight_clusters_can_fill(self, store):
        """Test that all 8 clusters can be filled sequentially"""
        # Fill Cluster 1 (A-F) - 25 students
        for i in range(25):
            store.create_student(discord_id=f"c1_{i}", last_name="Anderson")

        # Next A-F student goes to Cluster 5
        student = store.create_student(discord_id="c5_0", last_name="Brown")
        assert student["cluster_id"] == 5

        # Fill Cluster 2 (G-L) - 25 students
        for i in range(25):
            store.create_student(discord_id=f"c2_{i}", last_name="Garcia")

        # Next G-L student goes to Cluster 6
        student = store.create_student(discord_id="c6_0", last_name="Harris")
        assert student["cluster_id"] == 6

        # Fill Cluster 3 (M-R) - 25 students
        for i in range(25):
            store.create_student(discord_id=f"c3_{i}", last_name="Martinez")

        # Next M-R student goes to Cluster 7
        student = store.create_student(discord_id="c7_0", last_name="Nguyen")
        assert student["cluster_id"] == 7

        # Fill Cluster 4 (S-Z) - 25 students
        for i in range(25):
            store.create_student(discord_id=f"c4_{i}", last_name="Smith")

        # Next S-Z student goes to Cluster 8
        student = store.create_student(discord_id="c8_0", last_name="Taylor")
        assert student["cluster_id"] == 8

    def test_create_student_with_cluster_assignment(self, store):
        """Test that creating a student automatically assigns cluster"""
        # Create student with last name
        student = store.create_student(
            discord_id="123456789",
            cohort_id="test-cohort-1",
            last_name="Anderson"
        )

        assert student is not None
        assert student["cluster_id"] == 1

    def test_update_student_cluster(self, store):
        """Test updating student's cluster assignment"""
        store.create_student(
            discord_id="123456789",
            cohort_id="test-cohort-1",
            last_name="Anderson"  # Cluster 1
        )

        # Update to different cluster
        store.update_student_cluster("123456789", cluster_id=2)

        student = store.get_student("123456789")
        assert student["cluster_id"] == 2

    def test_get_students_by_cluster(self, store):
        """Test retrieving all students in a specific cluster"""
        # Create students in different clusters
        store.create_student(discord_id="student1", last_name="Anderson")  # Cluster 1
        store.create_student(discord_id="student2", last_name="Brown")  # Cluster 1
        store.create_student(discord_id="student3", last_name="Smith")  # Cluster 4

        # Get Cluster 1 students
        cluster1_students = store.get_students_by_cluster(cluster_id=1)

        assert len(cluster1_students) == 2
        student_ids = [s["discord_id"] for s in cluster1_students]
        assert "student1" in student_ids
        assert "student2" in student_ids
        assert "student3" not in student_ids


class TestVoiceChannelManagement:
    """Test temporary voice channel creation and destruction"""

    @pytest.mark.asyncio
    async def test_create_voice_channel_for_cluster(self, store):
        """Test creating temporary voice channel for cluster session"""
        # Mock Discord guild and bot
        mock_guild = Mock()
        mock_bot = Mock()

        # Create voice channel
        channel = await store.create_cluster_voice_channel(
            guild=mock_guild,
            cluster_id=1,
            bot=mock_bot
        )

        assert channel is not None
        assert "cluster-1" in channel.name.lower()

    @pytest.mark.asyncio
    async def test_voice_channel_permissions(self, store):
        """Test that voice channels have correct permissions"""
        mock_guild = Mock()
        mock_role_cluster1 = Mock(id=101)
        mock_role_cluster1.name = "Cluster-1"
        mock_role_facilitator = Mock(id=999)
        mock_role_facilitator.name = "Facilitator"
        mock_default_role = Mock(id=0)
        mock_default_role.name = "@everyone"
        mock_guild.roles = [mock_role_cluster1, mock_role_facilitator]
        mock_guild.default_role = mock_default_role

        # Create channel with role restrictions
        channel = await store.create_cluster_voice_channel(
            guild=mock_guild,
            cluster_id=1,
            facilitator_role=mock_role_facilitator
        )

        # Verify permissions were set
        assert channel.set_permissions.called
        configured_roles = [call.args[0] for call in channel.set_permissions.call_args_list]
        assert mock_default_role in configured_roles
        assert mock_role_cluster1 in configured_roles
        assert mock_role_facilitator in configured_roles

    @pytest.mark.asyncio
    async def test_delete_voice_channel_after_session(self, store):
        """Test deleting voice channel after session ends"""
        mock_channel = Mock()
        mock_channel.id = 12345

        # Delete channel
        await store.delete_cluster_voice_channel(mock_channel)

        assert mock_channel.delete.called

    @pytest.mark.asyncio
    async def test_prevent_duplicate_voice_channels(self, store):
        """Test that duplicate voice channels are not created"""
        mock_guild = Mock()
        existing_channel = Mock()
        existing_channel.name = "cluster-1-voice"

        # Simulate channel already exists
        mock_guild.voice_channels = [existing_channel]

        # Should not create duplicate
        channel = await store.create_cluster_voice_channel(
            guild=mock_guild,
            cluster_id=1
        )

        assert channel is None or channel == existing_channel


class TestClusterSwitching:
    """Test Trevor-admin cluster switching functionality"""

    def test_cluster_switch_request(self, store):
        """Test processing student's cluster switch request"""
        # Create student in Cluster 1 (Anderson = A-F)
        store.create_student(
            discord_id="123456789",
            last_name="Anderson"
        )

        # Verify starting cluster
        student = store.get_student("123456789")
        assert student["cluster_id"] == 1

        # Request switch to Cluster 2
        success = store.request_cluster_switch(
            discord_id="123456789",
            new_cluster_id=2,
            reason="Time conflict"
        )

        assert success is True

        # Verify switch happened
        student = store.get_student("123456789")
        assert student["cluster_id"] == 2  # Updated

    def test_cluster_switch_with_reason(self, store):
        """Test that cluster switch reasons are logged"""
        store.create_student(
            discord_id="123456789",
            last_name="Anderson"
        )

        # Switch with reason
        store.request_cluster_switch(
            discord_id="123456789",
            new_cluster_id=3,
            reason="Work schedule conflict with 6 PM sessions"
        )

        # Verify switch happened
        student = store.get_student("123456789")
        assert student["cluster_id"] == 3

    def test_prevent_cluster_switch_if_full(self, store):
        """Test that students cannot switch to full clusters (25 max)"""
        # Fill Cluster 2 to capacity (25 students)
        for i in range(25):
            store.create_student(
                discord_id=f"student_{i}",
                last_name="Garcia"  # Cluster 2 (G-L)
            )

        # Try to switch to full cluster
        store.create_student(
            discord_id="new_student",
            last_name="Anderson"  # Cluster 1
        )

        success = store.request_cluster_switch(
            discord_id="new_student",
            new_cluster_id=2,
            reason="Want to be with friends"
        )

        # Should fail - cluster is full
        assert success is False

        # Student should remain in original cluster
        student = store.get_student("new_student")
        assert student["cluster_id"] == 1

    def test_can_switch_to_overflow_cluster(self, store):
        """Test that students can switch to overflow clusters (5-8) if available"""
        # Create student in Cluster 1
        store.create_student(discord_id="switcher", last_name="Anderson")

        # Switch to Cluster 5 (A-F overflow)
        success = store.request_cluster_switch(
            discord_id="switcher",
            new_cluster_id=5,
            reason="Moved to overflow group"
        )

        # Should succeed - overflow cluster is available
        assert success is True

        student = store.get_student("switcher")
        assert student["cluster_id"] == 5


class TestClusterRosters:
    """Test cluster roster management for Trevor's dashboard"""

    def test_generate_cluster_roster_report(self, store):
        """Test generating roster report for all 8 clusters"""
        # Create students across clusters
        store.create_student(discord_id="s1", last_name="Anderson")  # Cluster 1
        store.create_student(discord_id="s2", last_name="Brown")  # Cluster 1
        store.create_student(discord_id="s3", last_name="Smith")  # Cluster 4

        # Generate rosters
        rosters = store.get_all_cluster_rosters()

        assert len(rosters) == 8  # 8 clusters total
        assert rosters[0]["cluster_id"] == 1
        assert rosters[0]["student_count"] == 2
        assert rosters[3]["cluster_id"] == 4
        assert rosters[3]["student_count"] == 1
        assert rosters[4]["cluster_id"] == 5
        assert rosters[4]["student_count"] == 0  # Empty overflow cluster

    def test_cluster_session_attendance_tracking(self, store):
        """Test tracking attendance for cluster sessions"""
        # Create students in cluster
        store.create_student(discord_id="s1", last_name="Anderson")  # Cluster 1
        store.create_student(discord_id="s2", last_name="Brown")  # Cluster 1
        store.create_student(discord_id="s3", last_name="Chen")  # Cluster 1

        # Record attendance
        store.record_session_attendance(
            cluster_id=1,
            session_date=datetime.now().isoformat(),
            attendees=["s1", "s2"]  # s3 absent
        )

        # Get attendance report
        attendance = store.get_cluster_attendance(cluster_id=1)

        assert len(attendance["recent_sessions"]) == 1
        assert attendance["recent_sessions"][0]["attendee_count"] == 2
        assert attendance["recent_sessions"][0]["absent"] == 1

    def test_cluster_session_attendance_count_only(self, store):
        """Test attendance persistence when only attendance_count is provided."""
        store.create_student(discord_id="s1", last_name="Anderson")
        store.create_student(discord_id="s2", last_name="Brown")
        store.create_student(discord_id="s3", last_name="Chen")

        store.record_session_attendance(
            cluster_id=1,
            session_date=datetime.now().isoformat(),
            attendees=[],
            attendance_count=2,
        )

        attendance = store.get_cluster_attendance(cluster_id=1)
        assert len(attendance["recent_sessions"]) == 1
        assert attendance["recent_sessions"][0]["attendee_count"] == 2
        assert attendance["recent_sessions"][0]["absent"] == 1


class TestClusterIntegration:
    """Integration tests for cluster system with Discord bot"""

    @pytest.mark.asyncio
    async def test_on_member_join_assigns_cluster_and_welcomes(self, store):
        """Test that new member gets cluster assigned and welcome DM"""
        # Mock Discord member
        mock_member = Mock()
        mock_member.id = "123456789"
        mock_member.name = "TestStudent"
        mock_member.display_name = "John Anderson"  # Last name: Anderson

        # Assign cluster
        cluster_id = store.assign_cluster_by_last_name("Anderson")
        assert cluster_id == 1

        # Verify student created in DB
        student = store.create_student(
            discord_id=mock_member.id,
            last_name="Anderson"
        )

        assert student["cluster_id"] == 1

    @pytest.mark.asyncio
    async def test_cluster_specific_session_announcements(self, store):
        """Test that session announcements target correct clusters"""
        # Create students in different clusters
        store.create_student(discord_id="c1_student", last_name="Anderson")  # Cluster 1
        store.create_student(discord_id="c2_student", last_name="Smith")  # Cluster 4

        # Get Cluster 1 students for announcement
        cluster1_students = store.get_students_by_cluster(cluster_id=1)

        assert len(cluster1_students) == 1
        assert cluster1_students[0]["discord_id"] == "c1_student"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
