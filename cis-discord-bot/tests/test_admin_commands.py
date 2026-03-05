"""
Tests for Trevor admin observability commands.
"""

import os
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commands import admin  # noqa: E402


def _ctx(user_id: int):
    return SimpleNamespace(user=SimpleNamespace(id=user_id))


@pytest.fixture(autouse=True)
def _auth_defaults():
    original_id = admin.FACILITATOR_DISCORD_ID
    original_insecure = admin.ALLOW_INSECURE_ADMIN
    admin.FACILITATOR_DISCORD_ID = "42"
    admin.ALLOW_INSECURE_ADMIN = False
    yield
    admin.FACILITATOR_DISCORD_ID = original_id
    admin.ALLOW_INSECURE_ADMIN = original_insecure


class TestAdminAuth:
    def test_is_trevor_fails_closed_when_unconfigured(self):
        admin.FACILITATOR_DISCORD_ID = None
        admin.ALLOW_INSECURE_ADMIN = False
        assert admin.is_facilitator(SimpleNamespace(id=42)) is False

    def test_is_trevor_can_be_relaxed_in_dev(self):
        admin.FACILITATOR_DISCORD_ID = None
        admin.ALLOW_INSECURE_ADMIN = True
        assert admin.is_facilitator(SimpleNamespace(id=999)) is True


class TestInspectJourney:
    @pytest.mark.asyncio
    async def test_requires_active_student_consent(self):
        store = Mock()
        store.get_student.return_value = {"current_week": 2, "zone": "zone_1"}
        store.has_active_student_consent.return_value = False

        with patch("commands.admin.send_response", new_callable=AsyncMock) as mock_send:
            await admin.inspect_journey(_ctx(42), store, "<@123456789>")

        store.get_student.assert_called_once_with("123456789")
        store.has_active_student_consent.assert_called_once_with(
            "123456789", consent_type="journey_inspection"
        )
        store.get_student_journey_events.assert_not_called()
        assert "No active consent" in mock_send.call_args[0][1]
        assert mock_send.call_args.kwargs.get("ephemeral") is True

    @pytest.mark.asyncio
    async def test_supports_member_object_mentions(self):
        store = Mock()
        store.get_student.return_value = {"current_week": 2, "zone": "zone_1"}
        store.has_active_student_consent.return_value = True
        store.get_student_journey_events.return_value = []

        member = SimpleNamespace(id=123456789)

        with patch("commands.admin.send_response", new_callable=AsyncMock) as mock_send:
            await admin.inspect_journey(_ctx(42), store, member)

        store.get_student.assert_called_once_with("123456789")
        assert "No observability events found yet" in mock_send.call_args[0][1]
        assert mock_send.call_args.kwargs.get("ephemeral") is True


class TestAdminPrivacy:
    @pytest.mark.asyncio
    async def test_show_stuck_students_uses_private_delivery(self):
        store = Mock()
        store.get_stuck_students.return_value = [
            {
                "student_id_hash": "abc123",
                "discord_id": "987654321",
                "current_week": 2,
                "zone": "zone_1",
                "total_interactions": 3,
            }
        ]

        with patch("commands.admin.send_response", new_callable=AsyncMock) as mock_send:
            await admin.show_stuck_students(_ctx(42), store, inactive_days=3)

        assert mock_send.call_args.kwargs.get("ephemeral") is True
