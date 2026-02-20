"""
Parent email system tests (Task 4.6 hardening).
"""

import os
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import cis_controller.email_service as email_service_module
from cis_controller.email_service import EmailResult, EmailService
from cis_controller.email_templates import ParentEmailTemplates
from database.models import ArtifactProgress
from database.store import StudentStateStore
from scheduler.parent_email_scheduler import ParentEmailScheduler


class StubEmailService:
    """Deterministic async email stub."""

    def __init__(self, success: bool = True, error: str | None = None):
        self.success = success
        self.error = error
        self.calls = []

    async def send_email(self, **kwargs):
        self.calls.append(kwargs)
        return EmailResult(
            success=self.success,
            message_id="stub-message-id" if self.success else None,
            error=self.error,
        )


class _FakeHttpResponse:
    def __init__(self, status_code: int, headers=None, text: str = "", json_data=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.text = text
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


class _FakeAsyncClient:
    def __init__(self, calls: list, response: _FakeHttpResponse):
        self._calls = calls
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, **kwargs):
        self._calls.append({"url": url, **kwargs})
        return self._response


@pytest.fixture
def test_db_path(tmp_path):
    db_path = tmp_path / "parent_email_test.db"
    yield str(db_path)
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def store(test_db_path):
    state_store = StudentStateStore(db_path=test_db_path)
    yield state_store
    state_store.close()


def _insert_conversation_for_week(store: StudentStateStore, student_id: str, week_number: int):
    week_start, _ = store._get_week_time_window(week_number)
    store.conn.execute(
        """
        INSERT INTO conversations (student_id, agent, role, content, created_at)
        VALUES (?, 'frame', 'user', 'test message', ?)
        """,
        (student_id, week_start),
    )
    store.conn.commit()


class TestParentConsentPersistence:
    def test_revoke_token_sets_opt_out_state(self, store):
        student_id = "1001"
        store.create_student(student_id)
        store.set_parent_consent(student_id, "parent@example.com", "share_weekly")

        consent = store.get_parent_consent(student_id)
        assert consent is not None
        token = consent["unsubscribe_token"]

        revoked = store.revoke_parent_consent_by_token(token)
        assert revoked is True

        updated = store.get_parent_consent(student_id)
        assert updated["parent_opted_out"] == 1
        assert updated["consent_preference"] == "privacy_first"
        assert updated["parent_email_status"] == "opted_out"


class TestWeeklySchedulerFlow:
    @pytest.mark.asyncio
    async def test_monday_batch_sends_previous_week_summary(self, store):
        student_id = "2001"
        store.create_student(student_id)
        store.set_parent_consent(student_id, "guardian@example.com", "share_weekly")
        store.create_weekly_reflection_record(student_id, 1)
        store.submit_weekly_reflection(
            student_id,
            1,
            reflection_content=(
                "Habit Focus: Habit 1 (Pause)\n"
                "Habit Practice: yes\n"
                "Identity Shift: I now pause before asking."
            ),
            proof_of_work="AI understood my actual situation.",
        )
        _insert_conversation_for_week(store, student_id, week_number=1)

        email_stub = StubEmailService(success=True)
        scheduler = ParentEmailScheduler(
            store=store,
            email_service=email_stub,
            retry_delays_seconds=[0],
        )

        stats = await scheduler.send_weekly_parent_emails(current_week=2)
        assert stats["sent"] == 1
        assert stats["failed"] == 0
        assert stats["report_week"] == 1
        assert len(email_stub.calls) == 1
        assert "Week 1" in email_stub.calls[0]["subject"]

        cursor = store.conn.execute(
            "SELECT status, email_type FROM parent_email_log WHERE student_id = ?",
            (student_id,),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row["status"] == "sent"
        assert row["email_type"] == "weekly_update"

    @pytest.mark.asyncio
    async def test_weekly_batch_is_idempotent_for_same_report_week(self, store):
        student_id = "2004"
        store.create_student(student_id)
        store.set_parent_consent(student_id, "guardian4@example.com", "share_weekly")
        store.create_weekly_reflection_record(student_id, 1)
        store.submit_weekly_reflection(
            student_id,
            1,
            reflection_content="Habit Focus: Habit 1 (Pause)\nHabit Practice: yes",
            proof_of_work="proof",
        )
        _insert_conversation_for_week(store, student_id, week_number=1)

        email_stub = StubEmailService(success=True)
        scheduler = ParentEmailScheduler(
            store=store,
            email_service=email_stub,
            retry_delays_seconds=[0],
        )

        first = await scheduler.send_weekly_parent_emails(current_week=2)
        second = await scheduler.send_weekly_parent_emails(current_week=2)

        assert first["sent"] == 1
        assert second["sent"] == 0
        assert second["skipped"] == 1
        assert len(email_stub.calls) == 1

    @pytest.mark.asyncio
    async def test_parent_sender_override_defaults_to_trevor(self, store, monkeypatch):
        student_id = "2002"
        store.create_student(student_id)
        store.set_parent_consent(student_id, "guardian2@example.com", "share_weekly")
        store.create_weekly_reflection_record(student_id, 1)
        store.submit_weekly_reflection(
            student_id,
            1,
            reflection_content="Habit Focus: Habit 1 (Pause)\nHabit Practice: yes",
            proof_of_work="proof",
        )
        _insert_conversation_for_week(store, student_id, week_number=1)

        # Simulate global sender configured to a different address.
        monkeypatch.setenv("EMAIL_FROM", "support@k2mlabs.com")
        monkeypatch.setenv("EMAIL_FROM_NAME", "Support")
        monkeypatch.delenv("PARENT_EMAIL_FROM", raising=False)
        monkeypatch.delenv("PARENT_EMAIL_FROM_NAME", raising=False)
        monkeypatch.delenv("PARENT_EMAIL_REPLY_TO", raising=False)

        email_stub = StubEmailService(success=True)
        scheduler = ParentEmailScheduler(
            store=store,
            email_service=email_stub,
            retry_delays_seconds=[0],
        )

        stats = await scheduler.send_weekly_parent_emails(current_week=2)
        assert stats["sent"] == 1
        assert len(email_stub.calls) == 1
        assert email_stub.calls[0]["from_email"] == "trevor@k2mlabs.com"
        assert email_stub.calls[0]["from_name"] == "Trevor from K2M"
        assert email_stub.calls[0]["reply_to"] == "trevor@k2mlabs.com"

    @pytest.mark.asyncio
    async def test_week8_batch_skips_private_visibility(self, store):
        private_student = "3001"
        public_student = "3002"

        store.create_student(private_student)
        store.create_student(public_student)
        store.set_parent_consent(private_student, "private-parent@example.com", "privacy_first")
        store.set_parent_consent(public_student, "public-parent@example.com", "share_weekly")

        private_artifact = ArtifactProgress(
            section_1_question="Private question",
            section_2_reframed="Reframed",
            section_3_explored="Explored",
            section_4_challenged="Challenged",
            section_5_concluded="Concluded",
            section_6_reflection="Reflected",
            status="published",
        )
        public_artifact = ArtifactProgress(
            section_1_question="Public question",
            section_2_reframed="Reframed",
            section_3_explored="Explored",
            section_4_challenged="Challenged",
            section_5_concluded="Concluded",
            section_6_reflection="Reflected",
            status="published",
        )
        store.save_artifact_progress(private_student, private_artifact)
        store.save_artifact_progress(public_student, public_artifact)

        store.create_showcase_publication(
            discord_id=private_student,
            publication_type="artifact_completion",
            visibility_level="private",
            celebration_message="private",
        )
        store.create_showcase_publication(
            discord_id=public_student,
            publication_type="artifact_completion",
            visibility_level="public",
            celebration_message="public",
        )

        email_stub = StubEmailService(success=True)
        scheduler = ParentEmailScheduler(
            store=store,
            email_service=email_stub,
            retry_delays_seconds=[0],
        )
        stats = await scheduler.send_week8_parent_reports(week_number=8)

        assert stats["sent"] == 1
        assert stats["skipped"] == 1
        assert stats["failed"] == 0
        assert len(email_stub.calls) == 1
        assert "public-parent@example.com" == email_stub.calls[0]["to_email"]

        cursor = store.conn.execute(
            """
            SELECT student_id, status, email_type
            FROM parent_email_log
            WHERE email_type = 'week8_showcase'
            ORDER BY student_id
            """
        )
        rows = cursor.fetchall()
        assert len(rows) == 2
        assert rows[0]["status"] == "skipped"
        assert rows[1]["status"] == "sent"

    @pytest.mark.asyncio
    async def test_bounce_marks_parent_email_status(self, store):
        student_id = "3003"
        store.create_student(student_id)
        store.set_parent_consent(student_id, "bounce-parent@example.com", "share_weekly")
        store.create_weekly_reflection_record(student_id, 1)
        store.submit_weekly_reflection(
            student_id,
            1,
            reflection_content="Habit Focus: Habit 2 (Context)\nHabit Practice: yes",
            proof_of_work="context evidence",
        )
        _insert_conversation_for_week(store, student_id, week_number=1)

        email_stub = StubEmailService(success=False, error="Invalid recipient address")
        scheduler = ParentEmailScheduler(
            store=store,
            email_service=email_stub,
            retry_delays_seconds=[0],
        )

        stats = await scheduler.send_weekly_parent_emails(current_week=2)
        assert stats["sent"] == 0
        assert stats["failed"] == 1

        row = store.conn.execute(
            "SELECT status FROM parent_email_log WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        assert row is not None
        assert row["status"] == "bounced"

        consent = store.get_parent_consent(student_id)
        assert consent is not None
        assert consent["parent_email_status"] == "bounced"


class TestEmailServiceSemantics:
    @pytest.mark.asyncio
    async def test_no_provider_is_failure_without_dry_run(self, monkeypatch):
        monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
        monkeypatch.delenv("MAILGUN_API_KEY", raising=False)
        monkeypatch.setenv("EMAIL_DRY_RUN", "false")

        service = EmailService()
        result = await service.send_email(
            to_email="x@example.com",
            subject="Subject",
            html_content="<p>body</p>",
        )
        assert result.success is False
        assert "No email provider configured" in (result.error or "")

    @pytest.mark.asyncio
    async def test_no_provider_can_run_in_dry_run_mode(self, monkeypatch):
        monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
        monkeypatch.delenv("MAILGUN_API_KEY", raising=False)
        monkeypatch.setenv("EMAIL_DRY_RUN", "true")

        service = EmailService()
        result = await service.send_email(
            to_email="x@example.com",
            subject="Subject",
            html_content="<p>body</p>",
        )
        assert result.success is True
        assert result.message_id is not None

    @pytest.mark.asyncio
    async def test_sendgrid_reply_to_is_top_level_payload(self, monkeypatch):
        monkeypatch.setenv("SENDGRID_API_KEY", "SG.test")
        monkeypatch.delenv("MAILGUN_API_KEY", raising=False)
        monkeypatch.delenv("MAILGUN_DOMAIN", raising=False)
        monkeypatch.setenv("EMAIL_DRY_RUN", "false")

        calls = []
        fake_response = _FakeHttpResponse(
            status_code=202,
            headers={"X-Message-Id": "sg-msg-1"},
        )
        monkeypatch.setattr(
            email_service_module.httpx,
            "AsyncClient",
            lambda *args, **kwargs: _FakeAsyncClient(calls, fake_response),
        )

        service = EmailService()
        result = await service.send_email(
            to_email="parent@example.com",
            subject="Subject",
            html_content="<p>Body</p>",
            text_content="Body",
            reply_to="trevor@k2mlabs.com",
        )

        assert result.success is True
        assert len(calls) == 1
        payload = calls[0]["json"]
        assert payload["reply_to"]["email"] == "trevor@k2mlabs.com"
        assert "reply_to" not in payload["personalizations"][0]

    @pytest.mark.asyncio
    async def test_mailgun_uses_configured_domain_override(self, monkeypatch):
        monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
        monkeypatch.setenv("MAILGUN_API_KEY", "mg-key")
        monkeypatch.setenv("MAILGUN_DOMAIN", "mg.k2mlabs.com")
        monkeypatch.setenv("EMAIL_DRY_RUN", "false")

        calls = []
        fake_response = _FakeHttpResponse(
            status_code=200,
            json_data={"id": "<mailgun-msg-1>"},
        )
        monkeypatch.setattr(
            email_service_module.httpx,
            "AsyncClient",
            lambda *args, **kwargs: _FakeAsyncClient(calls, fake_response),
        )

        service = EmailService()
        result = await service.send_email(
            to_email="parent@example.com",
            subject="Subject",
            html_content="<p>Body</p>",
            from_email="trevor@k2mlabs.com",
        )

        assert result.success is True
        assert len(calls) == 1
        assert calls[0]["url"] == "https://api.mailgun.net/v3/mg.k2mlabs.com/messages"


class TestTemplateLinks:
    def test_unsubscribe_url_uses_env_base(self, monkeypatch):
        monkeypatch.setenv("PARENT_UNSUBSCRIBE_BASE", "https://example.com/unsub")

        html = ParentEmailTemplates.weekly_update_email(
            student_name="Student",
            week_number=3,
            habits_practiced={"Pause": 1},
            interaction_count=4,
            zone="zone_2",
            jtbd_focus="career_direction",
            unsubscribe_token="abc123",
            reflection_highlight="I became clearer",
            proof_of_work="AI reflected my context.",
        )

        assert "https://example.com/unsub?token=abc123" in html
