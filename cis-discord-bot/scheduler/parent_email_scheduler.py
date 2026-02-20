"""
Parent Email Scheduler (Task 4.6)

Weekly parent communication orchestration:
- Monday 9:00 AM EAT weekly updates for opted-in students
- Friday 9:00 AM EAT Week 8 artifact reports
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import pytz

from cis_controller.email_service import EmailResult, EmailService, get_email_service
from cis_controller.email_templates import ParentEmailTemplates
from database.store import StudentStateStore

logger = logging.getLogger(__name__)

EAT = pytz.timezone("Africa/Nairobi")


class ParentEmailScheduler:
    """
    Parent email batch scheduler.

    Weekly updates: Mondays at 9:00 AM EAT (summarize previous week).
    Week 8 parent reports: Fridays at 9:00 AM EAT.
    """

    def __init__(
        self,
        store: Optional[StudentStateStore] = None,
        email_service: Optional[EmailService] = None,
        templates: Optional[ParentEmailTemplates] = None,
        retry_delays_seconds: Optional[List[int]] = None,
    ):
        self.store = store or StudentStateStore()
        self.email_service = email_service or get_email_service()
        self.templates = templates or ParentEmailTemplates()
        self.retry_delays_seconds = retry_delays_seconds or self._load_retry_delays()
        self.parent_from_email = (
            os.getenv("PARENT_EMAIL_FROM", "").strip()
            or "trevor@k2mlabs.com"
        )
        self.parent_from_name = (
            os.getenv("PARENT_EMAIL_FROM_NAME", "").strip()
            or "Trevor from K2M"
        )
        self.parent_reply_to = (
            os.getenv("PARENT_EMAIL_REPLY_TO", "").strip()
            or self.parent_from_email
        )
        logger.info(
            "Parent email sender configured as %s <%s> (reply-to: %s)",
            self.parent_from_name,
            self.parent_from_email,
            self.parent_reply_to,
        )

    @staticmethod
    def _load_retry_delays() -> List[int]:
        raw = os.getenv("PARENT_EMAIL_RETRY_DELAYS_SECONDS", "60,300,900")
        values: List[int] = []
        for chunk in raw.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                values.append(max(0, int(chunk)))
            except ValueError:
                logger.warning("Invalid retry delay value in PARENT_EMAIL_RETRY_DELAYS_SECONDS: %s", chunk)
        return values or [60, 300, 900]

    @staticmethod
    def _build_habit_counts(reflection: Dict[str, Optional[str]]) -> Dict[str, int]:
        """
        Build weekly habit count map from reflection status.

        Reflection data is one weekly snapshot, so values are intentionally lightweight
        and non-cumulative (0/1) instead of lifetime counters.
        """
        habit_focus = (reflection.get("habit_focus") or "").lower()
        habit_practice = (reflection.get("habit_practice") or "").lower()

        if not habit_focus:
            return {}

        count = 1 if habit_practice == "yes" else 0
        if "habit 1" in habit_focus or "pause" in habit_focus:
            return {"Pause": count}
        if "habit 2" in habit_focus or "context" in habit_focus:
            return {"Context": count}
        if "habit 3" in habit_focus or "iterate" in habit_focus:
            return {"Iterate": count}
        if "habit 4" in habit_focus or "think first" in habit_focus:
            return {"Think First": count}
        return {habit_focus.title(): count}

    async def _send_with_retry(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> EmailResult:
        attempt = 0
        result = await self.email_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_email=self.parent_from_email,
            from_name=self.parent_from_name,
            reply_to=self.parent_reply_to,
        )
        while not result.success and attempt < len(self.retry_delays_seconds):
            delay = self.retry_delays_seconds[attempt]
            attempt += 1
            logger.warning(
                "Email send failed for %s (attempt %s). Retrying in %ss. Error: %s",
                to_email,
                attempt,
                delay,
                result.error,
            )
            if delay > 0:
                await asyncio.sleep(delay)
            result = await self.email_service.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                from_email=self.parent_from_email,
                from_name=self.parent_from_name,
                reply_to=self.parent_reply_to,
            )
        return result

    async def send_weekly_parent_emails(self, current_week: int) -> Dict[str, object]:
        """
        Send Monday weekly parent emails summarizing the previous week.

        Args:
            current_week: Current cohort week (1-8)

        Returns:
            Dict with stats and failure list.
        """
        if current_week <= 1:
            logger.info("Skipping weekly parent email batch: no prior week to summarize")
            return {"sent": 0, "failed": 0, "skipped": 0, "total": 0, "report_week": 0, "failures": []}

        report_week = current_week - 1
        logger.info("Starting weekly parent email batch for report week %s", report_week)

        recipients = self.store.get_weekly_email_recipients()
        if not recipients:
            logger.info("No opted-in recipients for weekly parent emails")
            return {
                "sent": 0,
                "failed": 0,
                "skipped": 0,
                "total": 0,
                "report_week": report_week,
                "failures": [],
            }

        stats = {
            "sent": 0,
            "failed": 0,
            "skipped": 0,
            "total": len(recipients),
            "report_week": report_week,
            "failures": [],
        }

        for recipient in recipients:
            try:
                status = await self._send_weekly_email_to_recipient(recipient, report_week)
                stats[status] += 1
            except Exception as exc:
                stats["failed"] += 1
                stats["failures"].append({
                    "student_id": recipient.get("student_id"),
                    "parent_email": recipient.get("parent_email"),
                    "error": str(exc),
                })
                logger.error(
                    "Failed to send weekly email to %s: %s",
                    recipient.get("parent_email"),
                    exc,
                    exc_info=True,
                )

        logger.info(
            "Weekly parent email batch complete (report week %s): %s sent, %s failed",
            report_week,
            stats["sent"],
            stats["failed"],
        )
        return stats

    async def _send_weekly_email_to_recipient(self, recipient: Dict, report_week: int) -> str:
        discord_id = str(recipient["student_id"])
        parent_email = recipient["parent_email"]
        unsubscribe_token = recipient["unsubscribe_token"]

        if self.store.has_weekly_update_sent(discord_id, report_week):
            logger.info(
                "Skipping duplicate weekly parent email for student %s report week %s",
                discord_id,
                report_week,
            )
            return "skipped"

        student_row = self.store.get_student(discord_id)
        if not student_row:
            raise ValueError(f"Student {discord_id} not found")

        student = dict(student_row)
        student_name = student.get("discord_id", discord_id)

        reflection = self.store.get_weekly_reflection_highlight(discord_id, report_week)
        habits_practiced = self._build_habit_counts(reflection)
        interaction_count = self.store.get_weekly_conversation_count(discord_id, report_week)

        zone = student.get("zone", "zone_0")
        jtbd_focus = student.get("jtbd_concern", "career_direction")

        html_content = self.templates.weekly_update_email(
            student_name=student_name,
            week_number=report_week,
            habits_practiced=habits_practiced,
            interaction_count=interaction_count,
            zone=zone,
            jtbd_focus=jtbd_focus,
            unsubscribe_token=unsubscribe_token,
            reflection_highlight=reflection.get("identity_shift"),
            proof_of_work=reflection.get("proof_of_work"),
        )
        text_content = self.templates.plain_text_fallback(html_content)
        subject = f"{student_name} thinking growth update - Week {report_week}"

        result = await self._send_with_retry(
            to_email=parent_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

        status = "sent"
        if not result.success:
            error_text = (result.error or "").lower()
            status = "bounced" if "bounce" in error_text or "invalid recipient" in error_text else "failed"
        self.store.log_parent_email(
            discord_id=discord_id,
            parent_email=parent_email,
            email_type="weekly_update",
            subject=subject,
            status=status,
            error_message=result.error if not result.success else None,
        )

        if result.success:
            self.store.update_parent_email_sent(discord_id)
            return "sent"

        if status == "bounced":
            self.store.update_parent_email_status(discord_id, "bounced")

        raise RuntimeError(result.error or "Unknown email send error")

    async def send_week8_parent_reports(self, week_number: int) -> Dict[str, object]:
        """
        Send Friday Week 8 parent reports for students with published artifacts.

        Args:
            week_number: Current cohort week

        Returns:
            Dict with stats and failure details.
        """
        if week_number != 8:
            return {"sent": 0, "failed": 0, "skipped": 0, "total": 0, "failures": []}

        recipients = self.store.get_week8_email_recipients()
        if not recipients:
            logger.info("No eligible Week 8 parent report recipients")
            return {"sent": 0, "failed": 0, "skipped": 0, "total": 0, "failures": []}

        stats = {"sent": 0, "failed": 0, "skipped": 0, "total": len(recipients), "failures": []}

        for recipient in recipients:
            try:
                status = await self._send_week8_email_to_recipient(recipient)
                stats[status] += 1
            except Exception as exc:
                stats["failed"] += 1
                stats["failures"].append({
                    "student_id": recipient.get("student_id"),
                    "parent_email": recipient.get("parent_email"),
                    "error": str(exc),
                })
                logger.error(
                    "Failed Week 8 parent report for %s: %s",
                    recipient.get("parent_email"),
                    exc,
                    exc_info=True,
                )

        logger.info(
            "Week 8 parent report batch complete: %s sent, %s skipped, %s failed",
            stats["sent"],
            stats["skipped"],
            stats["failed"],
        )
        return stats

    @staticmethod
    def _summarize_artifact(recipient: Dict) -> str:
        parts = [
            recipient.get("section_2_reframed"),
            recipient.get("section_3_explored"),
            recipient.get("section_4_challenged"),
            recipient.get("section_5_concluded"),
            recipient.get("section_6_reflection"),
        ]
        cleaned = [p.strip() for p in parts if p and p.strip()]
        if not cleaned:
            return "They completed their artifact and demonstrated meaningful thinking growth across the 4 habits."

        summary = " ".join(cleaned)
        # Keep this parent-facing summary compact.
        if len(summary) > 900:
            summary = summary[:897].rstrip() + "..."
        return summary

    async def _send_week8_email_to_recipient(self, recipient: Dict) -> str:
        discord_id = str(recipient["student_id"])
        parent_email = recipient["parent_email"]
        unsubscribe_token = recipient["unsubscribe_token"]
        visibility = (recipient.get("visibility_level") or "private").lower()

        # Respect private publication unless explicit parent-sharing workflow is added.
        if visibility == "private":
            self.store.log_parent_email(
                discord_id=discord_id,
                parent_email=parent_email,
                email_type="week8_showcase",
                subject="Week 8 parent report skipped (private artifact)",
                status="skipped",
                error_message="Student selected private publication; explicit parent-share consent required.",
            )
            return "skipped"

        student_name = recipient.get("student_id", discord_id)
        artifact_question = recipient.get("section_1_question") or "Their final Week 8 thinking question"
        artifact_summary = self._summarize_artifact(recipient)
        zone = recipient.get("zone", "zone_0")
        is_anonymous = visibility == "anonymous"

        habits_demonstrated = [
            "Pause - Clarified what they wanted before asking",
            "Context - Explained their real situation",
            "Iterate - Explored options before deciding",
            "Think First - Challenged assumptions before conclusions",
        ]

        html_content = self.templates.week8_showcase_email(
            student_name=student_name,
            artifact_question=artifact_question,
            artifact_summary=artifact_summary,
            habits_demonstrated=habits_demonstrated,
            zone=zone,
            unsubscribe_token=unsubscribe_token,
            is_anonymous=is_anonymous,
        )
        text_content = self.templates.plain_text_fallback(html_content)
        subject = f"{student_name} Week 8 artifact report"

        result = await self._send_with_retry(
            to_email=parent_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

        status = "sent"
        if not result.success:
            error_text = (result.error or "").lower()
            status = "bounced" if "bounce" in error_text or "invalid recipient" in error_text else "failed"
        self.store.log_parent_email(
            discord_id=discord_id,
            parent_email=parent_email,
            email_type="week8_showcase",
            subject=subject,
            status=status,
            error_message=result.error if not result.success else None,
        )

        if result.success:
            self.store.update_parent_email_sent(discord_id)
            return "sent"

        if status == "bounced":
            self.store.update_parent_email_status(discord_id, "bounced")

        raise RuntimeError(result.error or "Unknown email send error")

    def should_send_weekly_emails(self, current_time: Optional[datetime] = None) -> bool:
        """
        Check weekly parent update slot: Monday 9:00 AM EAT.
        """
        if current_time is None:
            current_time = datetime.now(EAT)
        return current_time.weekday() == 0 and current_time.hour == 9 and current_time.minute == 0

    def should_send_week8_reports(
        self,
        week_number: int,
        current_time: Optional[datetime] = None,
    ) -> bool:
        """
        Check Week 8 report slot: Friday 9:00 AM EAT.
        """
        if week_number != 8:
            return False
        if current_time is None:
            current_time = datetime.now(EAT)
        return current_time.weekday() == 4 and current_time.hour == 9 and current_time.minute == 0


# Singleton instance
_parent_email_scheduler_instance: Optional[ParentEmailScheduler] = None


def get_parent_email_scheduler(
    store: Optional[StudentStateStore] = None,
    retry_delays_seconds: Optional[List[int]] = None,
) -> ParentEmailScheduler:
    """Get or create parent email scheduler singleton instance."""
    global _parent_email_scheduler_instance
    if _parent_email_scheduler_instance is None:
        _parent_email_scheduler_instance = ParentEmailScheduler(
            store=store,
            retry_delays_seconds=retry_delays_seconds,
        )
    elif store is not None:
        _parent_email_scheduler_instance.store = store
    return _parent_email_scheduler_instance
