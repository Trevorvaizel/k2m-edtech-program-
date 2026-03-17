"""Task 7.12 tests for #welcome-lounge waiting-room behavior."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cis_controller.welcome_lounge import (
    STATUS_MARKER,
    classify_guest_question,
    handle_welcome_lounge_message,
    upsert_welcome_lounge_content,
)


def test_classify_guest_question_escalates_when_pending_too_long():
    reply, escalate = classify_guest_question(
        "My payment has been pending for over 24 hours, how long now?"
    )
    assert "24 hours" in reply
    assert escalate is True


@pytest.mark.asyncio
async def test_upsert_welcome_lounge_content_creates_status_pin_and_previews(monkeypatch):
    monkeypatch.setenv("CHANNEL_WELCOME_LOUNGE", "555")

    channel = MagicMock()
    channel.id = 555
    channel.name = "welcome-lounge"
    channel.set_permissions = AsyncMock()
    channel.pins = AsyncMock(return_value=[])

    status_message = MagicMock()
    status_message.pin = AsyncMock()
    channel.send = AsyncMock(
        side_effect=[status_message, MagicMock(), MagicMock(), MagicMock()]
    )

    async def _empty_history(*_args, **_kwargs):
        if False:
            yield None

    channel.history = _empty_history

    guild = MagicMock()
    guild.default_role = SimpleNamespace(name="@everyone")
    guild.roles = [
        SimpleNamespace(name="Guest"),
        SimpleNamespace(name="Student"),
        SimpleNamespace(name="Facilitator"),
        SimpleNamespace(name="Trevor"),
        SimpleNamespace(name="CIS Bot"),
    ]
    guild.text_channels = [channel]
    guild.get_channel = MagicMock(return_value=channel)

    bot = MagicMock()
    bot.get_guild = MagicMock(return_value=guild)
    store = MagicMock()
    store.get_confirmed_student_count.return_value = 9

    with patch(
        "cis_controller.welcome_lounge._week1_preview_posts",
        return_value=[
            ("[WELCOME_LOUNGE_PREVIEW_W1_MONDAY]", "Preview 1"),
            ("[WELCOME_LOUNGE_PREVIEW_W1_TUESDAY]", "Preview 2"),
            ("[WELCOME_LOUNGE_PREVIEW_W1_WEDNESDAY]", "Preview 3"),
        ],
    ):
        result = await upsert_welcome_lounge_content(
            bot=bot,
            store=store,
            guild_id=123,
            include_previews=True,
        )

    assert result["ok"] is True
    assert result["status_changed"] is True
    assert result["preview_posts_created"] == 3
    assert channel.send.await_count == 4
    first_message = channel.send.await_args_list[0].args[0]
    assert STATUS_MARKER in first_message
    status_message.pin.assert_awaited_once()


@pytest.mark.asyncio
async def test_upsert_welcome_lounge_content_denies_guest_outside_lounge(monkeypatch):
    monkeypatch.setenv("CHANNEL_WELCOME_LOUNGE", "555")

    lounge_channel = MagicMock()
    lounge_channel.id = 555
    lounge_channel.name = "welcome-lounge"
    lounge_channel.set_permissions = AsyncMock()
    lounge_channel.pins = AsyncMock(return_value=[])

    status_message = MagicMock()
    status_message.pin = AsyncMock()
    lounge_channel.send = AsyncMock(side_effect=[status_message])

    async def _empty_history(*_args, **_kwargs):
        if False:
            yield None

    lounge_channel.history = _empty_history

    non_lounge_channel = MagicMock()
    non_lounge_channel.id = 556
    non_lounge_channel.name = "week-1-wonder"
    non_lounge_channel.type = 0
    non_lounge_channel.set_permissions = AsyncMock()

    voice_channel = MagicMock()
    voice_channel.id = 557
    voice_channel.name = "cluster-2-voice"
    voice_channel.type = 2
    voice_channel.set_permissions = AsyncMock()

    category_with_lounge = SimpleNamespace(
        channels=[lounge_channel],
        set_permissions=AsyncMock(),
    )
    category_other = SimpleNamespace(
        channels=[non_lounge_channel],
        set_permissions=AsyncMock(),
    )

    guest_role = SimpleNamespace(name="Guest")
    guild = MagicMock()
    guild.default_role = SimpleNamespace(name="@everyone")
    guild.roles = [
        guest_role,
        SimpleNamespace(name="Student"),
        SimpleNamespace(name="Facilitator"),
        SimpleNamespace(name="Trevor"),
        SimpleNamespace(name="CIS Bot"),
    ]
    guild.channels = [lounge_channel, non_lounge_channel, voice_channel]
    guild.text_channels = [lounge_channel, non_lounge_channel]
    guild.categories = [category_with_lounge, category_other]
    guild.get_channel = MagicMock(return_value=lounge_channel)

    bot = MagicMock()
    bot.get_guild = MagicMock(return_value=guild)
    store = MagicMock()
    store.get_confirmed_student_count.return_value = 4

    result = await upsert_welcome_lounge_content(
        bot=bot,
        store=store,
        guild_id=123,
        include_previews=False,
    )

    assert result["ok"] is True

    non_lounge_guest_calls = [
        call
        for call in non_lounge_channel.set_permissions.await_args_list
        if call.args and getattr(call.args[0], "name", "") == "Guest"
    ]
    assert non_lounge_guest_calls, "Expected @Guest deny overwrite on non-lounge channels"
    deny_kwargs = non_lounge_guest_calls[-1].kwargs
    assert deny_kwargs["read_messages"] is False
    assert deny_kwargs["send_messages"] is False
    assert deny_kwargs["read_message_history"] is False

    voice_guest_calls = [
        call
        for call in voice_channel.set_permissions.await_args_list
        if call.args and getattr(call.args[0], "name", "") == "Guest"
    ]
    assert voice_guest_calls, "Expected @Guest deny overwrite on non-lounge voice channels"

    category_guest_calls = [
        call
        for call in category_other.set_permissions.await_args_list
        if call.args and getattr(call.args[0], "name", "") == "Guest"
    ]
    assert category_guest_calls, "Expected @Guest deny overwrite on non-lounge categories"


@pytest.mark.asyncio
async def test_handle_guest_message_replies_and_escalates(monkeypatch):
    monkeypatch.setenv("CHANNEL_WELCOME_LOUNGE", "777")

    message = MagicMock()
    message.content = "How long? I have been waiting 24 hours."
    message.reply = AsyncMock()
    message.channel = SimpleNamespace(id=777, name="welcome-lounge")
    message.author = SimpleNamespace(
        bot=False,
        roles=[SimpleNamespace(name="Guest")],
    )

    with patch(
        "cis_controller.welcome_lounge._forward_to_dashboard",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_forward:
        consumed = await handle_welcome_lounge_message(bot=MagicMock(), message=message)

    assert consumed is True
    message.reply.assert_awaited_once()
    mock_forward.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_student_message_in_welcome_lounge_redirects(monkeypatch):
    monkeypatch.setenv("CHANNEL_WELCOME_LOUNGE", "888")

    message = MagicMock()
    message.content = "test"
    message.reply = AsyncMock()
    message.channel = SimpleNamespace(id=888, name="welcome-lounge")
    message.author = SimpleNamespace(
        bot=False,
        roles=[SimpleNamespace(name="Student")],
    )

    consumed = await handle_welcome_lounge_message(bot=MagicMock(), message=message)

    assert consumed is True
    message.reply.assert_awaited_once()
    reply_text = message.reply.await_args_list[0].args[0]
    assert "full access is unlocked" in reply_text


@pytest.mark.asyncio
async def test_handle_student_with_stale_guest_role_is_treated_as_student(monkeypatch):
    monkeypatch.setenv("CHANNEL_WELCOME_LOUNGE", "889")

    guest_role = SimpleNamespace(name="Guest")
    student_role = SimpleNamespace(name="Student")

    author = SimpleNamespace(
        bot=False,
        id=42,
        roles=[student_role, guest_role],
        remove_roles=AsyncMock(),
    )

    message = MagicMock()
    message.content = "Can I still post here?"
    message.reply = AsyncMock()
    message.channel = SimpleNamespace(id=889, name="welcome-lounge")
    message.author = author

    with patch(
        "cis_controller.welcome_lounge._forward_to_dashboard",
        new_callable=AsyncMock,
        return_value=True,
    ) as mock_forward:
        consumed = await handle_welcome_lounge_message(bot=MagicMock(), message=message)

    assert consumed is True
    message.reply.assert_awaited_once()
    reply_text = message.reply.await_args_list[0].args[0]
    assert "full access is unlocked" in reply_text
    author.remove_roles.assert_awaited_once()
    assert author.remove_roles.await_args_list[0].args[0] is guest_role
    mock_forward.assert_not_awaited()
