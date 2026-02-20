"""
Parent Email Templates (Task 4.6)

Generates parent email content from Story 5.3 and Story 6.5 specifications.
Implements privacy-compliant weekly updates (no DM content, aggregate patterns only).
"""

import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ParentEmailTemplates:
    """
    Generate HTML emails for parent updates per Story 5.3 + Story 6.5 specs.

    Privacy Rules (Guardrail #8):
        - NO private DM content
        - NO raw conversation transcripts
        - ONLY aggregate patterns and student-approved highlights
        - NO comparison to other students
    """

    @staticmethod
    def _unsubscribe_url(unsubscribe_token: str) -> str:
        base = os.getenv(
            "PARENT_UNSUBSCRIBE_BASE",
            "https://k2m-edtech.program/parent/unsubscribe",
        ).rstrip("/")
        return f"{base}?token={unsubscribe_token}"

    @staticmethod
    def weekly_update_email(
        student_name: str,
        week_number: int,
        habits_practiced: Dict[str, int],
        interaction_count: int,
        zone: str,
        jtbd_focus: str,
        unsubscribe_token: str,
        reflection_highlight: Optional[str] = None,
        proof_of_work: Optional[str] = None,
    ) -> str:
        """
        Generate weekly parent email update.

        Args:
            student_name: Student's name
            week_number: Report week number (the week being summarized)
            habits_practiced: Dict with habit label -> weekly count
            interaction_count: Weekly interaction count
            zone: Current zone (zone_0 through zone_4)
            jtbd_focus: Student's JTBD concern topic
            unsubscribe_token: Unique unsubscribe token
            reflection_highlight: Student identity-shift summary from reflection
            proof_of_work: Student proof-of-work excerpt from reflection

        Returns:
            HTML email content
        """
        habit_items = []
        for habit_label, count in habits_practiced.items():
            if count > 0:
                habit_items.append(f"{habit_label} ({count}x)")

        habits_display = " | ".join(habit_items) if habit_items else "Starting practice this week"

        zone_messages = {
            "zone_0": "Getting oriented",
            "zone_1": "Building awareness",
            "zone_2": "Exploring possibilities",
            "zone_3": "Gaining confidence",
            "zone_4": "Directing their own learning",
        }
        zone_message = zone_messages.get(zone, "Making progress")

        reflection_html = ""
        if reflection_highlight or proof_of_work:
            identity_line = (
                f"<p><strong>Identity shift:</strong> {reflection_highlight}</p>"
                if reflection_highlight
                else ""
            )
            proof_line = (
                f"<p><strong>Proof of work:</strong> \"{proof_of_work}\"</p>"
                if proof_of_work
                else ""
            )
            reflection_html = (
                "<div class=\"section\">"
                "<h2>Reflection Highlights</h2>"
                f"{identity_line}{proof_line}"
                "</div>"
            )

        unsubscribe_url = ParentEmailTemplates._unsubscribe_url(unsubscribe_token)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{student_name} thinking growth update</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 640px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1f6feb 0%, #0ea5e9 100%); color: #fff; padding: 24px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8fafc; padding: 24px; border-radius: 0 0 10px 10px; }}
        .section {{ margin-bottom: 20px; }}
        .section h2 {{ color: #1f6feb; font-size: 20px; margin-bottom: 8px; }}
        .summary {{ background: #fff; padding: 12px; border-radius: 8px; border-left: 4px solid #1f6feb; }}
        .footer {{ text-align: center; margin-top: 24px; font-size: 14px; color: #6b7280; }}
        .footer a {{ color: #6b7280; text-decoration: none; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <div class=\"header\">
            <h1>{student_name} Weekly Thinking Growth</h1>
            <p>Week {week_number} summary - {datetime.now().strftime('%B %d, %Y')}</p>
        </div>

        <div class=\"content\">
            <div class=\"section\">
                <h2>What they practiced this week</h2>
                <div class=\"summary\">
                    <p><strong>Habits:</strong> {habits_display}</p>
                    <p><strong>AI thinking interactions:</strong> {interaction_count}</p>
                </div>
            </div>

            <div class=\"section\">
                <h2>How they are growing</h2>
                <p><strong>Current stage:</strong> {zone_message}</p>
                <p><strong>Focus area:</strong> {jtbd_focus.replace('_', ' ').title()}</p>
            </div>

            {reflection_html}

            <div class=\"section\">
                <h2>Dual-Pillar progress</h2>
                <p>Your child is building both capabilities:</p>
                <ul>
                    <li><strong>Access expertise they do not yet have</strong></li>
                    <li><strong>Think clearly with that expertise</strong></li>
                </ul>
                <p>These are durable thinking habits that transfer beyond any single tool.</p>
            </div>

            <div class=\"section\">
                <h2>Next week</h2>
                <p>Week {week_number + 1} continues this growth through daily practice and reflection.</p>
            </div>

            <div class=\"section\">
                <p><strong>Best,</strong><br>Trevor<br>K2M Founder</p>
            </div>
        </div>

        <div class=\"footer\">
            <p>You are receiving this because your child chose to share progress updates.</p>
            <p><a href=\"{unsubscribe_url}\">Unsubscribe from future parent emails</a></p>
        </div>
    </div>
</body>
</html>
        """
        return html.strip()

    @staticmethod
    def week8_showcase_email(
        student_name: str,
        artifact_question: str,
        artifact_summary: str,
        habits_demonstrated: List[str],
        zone: str,
        unsubscribe_token: str,
        is_anonymous: bool = False,
    ) -> str:
        """
        Generate Week 8 artifact showcase email per Story 6.5 template.

        Args:
            student_name: Student's name
            artifact_question: Student's thinking question
            artifact_summary: Summary of artifact journey
            habits_demonstrated: List of habits shown
            zone: Final zone achieved
            unsubscribe_token: Unique unsubscribe token
            is_anonymous: Whether student published anonymously

        Returns:
            HTML email content
        """
        habits_text = "<br>".join(habits_demonstrated) if habits_demonstrated else "All 4 habits demonstrated"
        anonymous_note = (
            "<p><strong>Privacy note:</strong> Your child chose anonymous peer publication. "
            "Their progress is still shared with you as parent/guardian.</p>"
            if is_anonymous
            else ""
        )
        unsubscribe_url = ParentEmailTemplates._unsubscribe_url(unsubscribe_token)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{student_name} Week 8 artifact report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f3f4f6; }}
        .container {{ max-width: 700px; margin: 0 auto; background: #fff; }}
        .header {{ background: linear-gradient(135deg, #1f6feb 0%, #0ea5e9 100%); color: #fff; padding: 28px; }}
        .content {{ padding: 28px; }}
        .section {{ background: #f8fafc; border-left: 4px solid #1f6feb; border-radius: 6px; padding: 16px; margin-bottom: 16px; }}
        .footer {{ text-align: center; padding: 20px; font-size: 14px; color: #6b7280; }}
        .footer a {{ color: #6b7280; text-decoration: none; }}
    </style>
</head>
<body>
    <div class=\"container\">
        <div class=\"header\">
            <h1>Week 8 Parent Report: {student_name}</h1>
            <p>{datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        <div class=\"content\">
            <div class=\"section\">
                <h2>The question they wrestled with</h2>
                <p><em>{artifact_question}</em></p>
            </div>

            <div class=\"section\">
                <h2>Their thinking journey</h2>
                <p>{artifact_summary}</p>
            </div>

            <div class=\"section\">
                <h2>Habits demonstrated</h2>
                <p>{habits_text}</p>
                <p><strong>Final stage:</strong> {zone}</p>
            </div>

            {anonymous_note}

            <div class=\"section\">
                <h2>Why this matters</h2>
                <p>Your child can now access expertise they did not have before and think clearly with it in real decisions.</p>
                <p>These are transfer-ready habits for university, career, and life.</p>
            </div>

            <p><strong>Best,</strong><br>Trevor<br>K2M Founder</p>
        </div>
        <div class=\"footer\">
            <p>This update was sent after Week 8 artifact completion.</p>
            <p><a href=\"{unsubscribe_url}\">Unsubscribe from future parent emails</a></p>
        </div>
    </div>
</body>
</html>
        """
        return html.strip()

    @staticmethod
    def plain_text_fallback(html_content: str) -> str:
        """
        Extract plain text from HTML for email clients that do not render HTML.
        """
        text = re.sub(r"<[^>]+>", "\n", html_content)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
