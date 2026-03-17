"""
Task 7.10 regression checks:
- N-25 activation DM wording anchors
- N-24 welcome DM mobile mental-model bridge
"""

import importlib
from unittest.mock import AsyncMock, Mock, patch

import pytest

from cis_controller.internal_api_server import _build_activation_dm_messages


def test_activation_dm_includes_affirmation_action_and_reminder():
    msg_1, msg_2 = _build_activation_dm_messages(
        enrollment_name="Grace Kamau",
        cluster_id="Cluster 2",
        first_session_date="2026-03-18",
        week1_start_date="2026-03-16",
    )

    assert "Grace - you're in." in msg_1
    assert "Step 4 complete - you're in!" in msg_1
    assert "You just did something most people talk about and never do." in msg_1
    assert "When you're ready to start: go to #welcome-and-rules." in msg_1
    assert "I'll remind you before each." in msg_1
    assert "Stop 1 - Welcome and orientation" in msg_2


@pytest.mark.asyncio
async def test_on_member_join_linked_welcome_dm_contains_mobile_guide(monkeypatch):
    monkeypatch.setenv("DISCORD_TOKEN", "test-token")
    monkeypatch.setenv("DISCORD_GUILD_ID", "777")
    monkeypatch.setenv("COHORT_1_START_DATE", "2026-03-16")

    main_module = importlib.import_module("main")
    main_module = importlib.reload(main_module)

    invite = Mock()
    invite.code = "invite-123"
    invite.uses = 1

    guest_role = Mock()
    guest_role.name = "Guest"

    guild = Mock()
    guild.id = 777
    guild.roles = [guest_role]
    guild.invites = AsyncMock(return_value=[invite])

    member = Mock()
    member.bot = False
    member.id = 123456789
    member.name = "grace_k"
    member.display_name = "Grace Kamau"
    member.guild = guild
    member.add_roles = AsyncMock()
    member.send = AsyncMock()

    store = Mock()
    store.get_student_by_invite_code = Mock(return_value={"enrollment_name": "Grace Kamau"})
    store.link_student_by_invite = Mock(return_value=True)
    store.log_observability_event = Mock()
    store.update_onboarding_stop = Mock()
    store.touch_student_last_active = Mock()
    store.get_student = Mock(return_value={"enrollment_name": "Grace Kamau"})

    main_module._guild_invite_snapshot[guild.id] = {"invite-123": 0}

    with patch.object(main_module, "_get_store", return_value=store):
        await main_module.on_member_join(member)

    member.add_roles.assert_awaited_once_with(guest_role)
    member.send.assert_awaited_once()

    dm_text = member.send.await_args.args[0]
    assert "Step 2 complete - here's Step 3." in dm_text
    assert "Quick Discord guide on mobile:" in dm_text
    assert "Tap the menu icon (top left) to see channels." in dm_text
    assert "Tap the inbox icon to see my messages." in dm_text
    assert "Swipe right to return to the channel list." in dm_text
    assert "DM with me (here)." in dm_text
