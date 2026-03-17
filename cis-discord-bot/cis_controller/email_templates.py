"""
Parent Email Templates (Task 4.6)

Generates parent email content from Story 5.3 and Story 6.5 specifications.
Implements privacy-compliant weekly updates (no DM content, aggregate patterns only).
"""

import logging
import os
import re
from datetime import datetime
from pathlib import Path
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
    def _default_logo_svg_markup() -> str:
        """
        Embedded fallback SVG logo (sourced from k2m-landing/public/k2m-logo.svg).

        Kept inline so email templates still render correctly when only the bot
        service is deployed and static site assets are not present on disk.
        """
        return """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-label="K2M Logo" role="img">
  <line x1="50" y1="50" x2="28" y2="32" stroke="#3b82f6" stroke-width="3" stroke-linecap="round"/>
  <line x1="50" y1="50" x2="22" y2="48" stroke="#2563eb" stroke-width="3" stroke-linecap="round"/>
  <line x1="50" y1="50" x2="28" y2="68" stroke="#60a5fa" stroke-width="3" stroke-linecap="round"/>
  <line x1="50" y1="50" x2="38" y2="78" stroke="#3b82f6" stroke-width="2" stroke-linecap="round"/>
  <line x1="50" y1="50" x2="72" y2="32" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
  <line x1="50" y1="50" x2="78" y2="48" stroke="#059669" stroke-width="3" stroke-linecap="round"/>
  <line x1="50" y1="50" x2="72" y2="68" stroke="#34d399" stroke-width="3" stroke-linecap="round"/>
  <line x1="50" y1="50" x2="62" y2="78" stroke="#10b981" stroke-width="2" stroke-linecap="round"/>
  <circle cx="28" cy="32" r="5" fill="#3b82f6"/>
  <circle cx="22" cy="48" r="4" fill="#2563eb"/>
  <circle cx="28" cy="68" r="5" fill="#60a5fa"/>
  <circle cx="38" cy="78" r="3" fill="#93c5fd"/>
  <circle cx="72" cy="32" r="5" fill="#10b981"/>
  <circle cx="78" cy="48" r="4" fill="#059669"/>
  <circle cx="72" cy="68" r="5" fill="#34d399"/>
  <circle cx="62" cy="78" r="3" fill="#6ee7b7"/>
  <line x1="50" y1="50" x2="50" y2="22" stroke="#06b6d4" stroke-width="2" stroke-linecap="round"/>
  <circle cx="50" cy="18" r="4" fill="#22d3ee"/>
  <circle cx="50" cy="50" r="10" fill="#06b6d4"/>
  <circle cx="50" cy="50" r="5" fill="#0891b2"/>
</svg>
        """.strip()

    @staticmethod
    def _logo_size_px() -> int:
        raw = os.getenv("PARENT_EMAIL_LOGO_SIZE_PX", "88").strip()
        try:
            size = int(raw)
        except ValueError:
            logger.warning("Invalid PARENT_EMAIL_LOGO_SIZE_PX '%s'; using default 88", raw)
            return 88
        return max(40, min(size, 180))

    @staticmethod
    def _size_svg_markup(svg_markup: str, size_px: int) -> str:
        """
        Force explicit logo sizing on the first <svg ...> tag for consistent email render.
        """
        match = re.search(r"<svg\b([^>]*)>", svg_markup, flags=re.IGNORECASE)
        if not match:
            return svg_markup

        attrs = match.group(1)
        attrs = re.sub(r'\s(width|height)="[^"]*"', "", attrs, flags=re.IGNORECASE)
        attrs = re.sub(r"\sstyle='[^']*'", "", attrs, flags=re.IGNORECASE)
        attrs = re.sub(r'\sstyle="[^"]*"', "", attrs, flags=re.IGNORECASE)
        new_open = (
            f'<svg{attrs} width="{size_px}" height="{size_px}" '
            f'style="display:block;margin:0 auto;width:{size_px}px;height:{size_px}px;'
            f'max-width:{size_px}px;max-height:{size_px}px;">'
        )
        return svg_markup[:match.start()] + new_open + svg_markup[match.end():]

    @staticmethod
    def _resolve_logo_svg_markup(size_px: int) -> str:
        """
        Load brand SVG markup from disk when available, else use embedded fallback.
        """
        configured_logo_svg_path = os.getenv("PARENT_EMAIL_LOGO_SVG_PATH", "").strip()
        if configured_logo_svg_path:
            candidate_paths = [Path(configured_logo_svg_path)]
        else:
            repo_root = Path(__file__).resolve().parents[2]
            candidate_paths = [repo_root / "k2m-landing" / "public" / "k2m-logo.svg"]

        for candidate in candidate_paths:
            try:
                if candidate.exists() and candidate.is_file():
                    svg_markup = candidate.read_text(encoding="utf-8").strip()
                    if "<svg" in svg_markup and "</svg>" in svg_markup:
                        return ParentEmailTemplates._size_svg_markup(svg_markup, size_px)
            except Exception:
                logger.warning("Failed to load SVG logo from %s", candidate, exc_info=True)

        return ParentEmailTemplates._size_svg_markup(
            ParentEmailTemplates._default_logo_svg_markup(),
            size_px,
        )

    @staticmethod
    def _brand_logo_html() -> str:
        size_px = ParentEmailTemplates._logo_size_px()
        logo_url = os.getenv("PARENT_EMAIL_LOGO_URL", "").strip()
        if logo_url:
            return (
                f"<img src=\"{logo_url}\" alt=\"K2M\" width=\"{size_px}\" "
                f"style=\"display:block;margin:0 auto;width:{size_px}px;max-width:{size_px}px;"
                f"height:auto;border:0;\">"
            )
        return ParentEmailTemplates._resolve_logo_svg_markup(size_px)

    @staticmethod
    def _cta_url() -> str:
        return os.getenv("PARENT_EMAIL_CTA_URL", "https://discord.com").strip()

    @staticmethod
    def _social_links_html() -> str:
        links = [
            ("Instagram", os.getenv("PARENT_EMAIL_SOCIAL_INSTAGRAM_URL", "").strip()),
            ("X", os.getenv("PARENT_EMAIL_SOCIAL_X_URL", "").strip()),
            ("WhatsApp", os.getenv("PARENT_EMAIL_SOCIAL_WHATSAPP_URL", "").strip()),
            ("Discord", os.getenv("PARENT_EMAIL_SOCIAL_DISCORD_URL", "").strip()),
        ]
        items = []
        for label, url in links:
            if not url:
                continue
            items.append(
                f"<a href=\"{url}\" style=\"display:inline-block;margin:0 6px;padding:6px 10px;"
                f"border:1px solid #1f2937;border-radius:999px;color:#e5e7eb;text-decoration:none;"
                f"font-size:12px;font-family:Arial,sans-serif;\">{label}</a>"
            )
        return "".join(items)

    @staticmethod
    def _base_styles() -> str:
        return """
<style>
body {
  margin: 0;
  padding: 0;
  background-color: #e5e7eb;
  font-family: Arial, Helvetica, sans-serif;
  color: #e5e7eb;
}
a { color: #13d7d0; }
.outer { width: 100%; background: #e5e7eb; padding: 20px 0; }
.card {
  width: 640px;
  max-width: 640px;
  margin: 0 auto;
  background: #050608;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #111827;
}
.inner { padding: 28px 30px; }
.divider { height: 1px; background: #0f172a; margin: 18px 0 24px; }
.kicker {
  margin: 0;
  font-size: 12px;
  letter-spacing: 1px;
  color: #13d7d0;
  font-weight: 700;
  text-transform: uppercase;
}
.title {
  margin: 8px 0 0;
  font-size: 38px;
  line-height: 1.2;
  color: #f9fafb;
  font-weight: 800;
}
.title-accent { color: #13d7d0; }
.subdate {
  margin: 8px 0 0;
  font-size: 12px;
  letter-spacing: 1px;
  color: #67e8f9;
  text-transform: uppercase;
  font-weight: 700;
}
.copy { color: #d1d5db; font-size: 17px; line-height: 1.7; margin: 0 0 14px; }
.copy strong { color: #f9fafb; }
.section-title {
  margin: 20px 0 10px;
  color: #f9fafb;
  font-size: 20px;
  line-height: 1.3;
  font-weight: 700;
}
.list { margin: 0; padding: 0; list-style: none; }
.list li {
  margin: 0 0 12px;
  padding-left: 22px;
  position: relative;
  color: #d1d5db;
  font-size: 16px;
  line-height: 1.6;
}
.list li:before {
  content: "+";
  position: absolute;
  left: 0;
  top: 0;
  color: #13d7d0;
  font-weight: 700;
}
.panel {
  margin: 18px 0;
  padding: 16px;
  border: 1px solid #1f2937;
  border-radius: 10px;
  background: #0b0f14;
}
.panel p { margin: 0 0 8px; color: #d1d5db; font-size: 15px; line-height: 1.6; }
.panel p:last-child { margin-bottom: 0; }
.cta-wrap { text-align: center; margin: 26px 0 10px; }
.cta-btn {
  display: inline-block;
  padding: 14px 26px;
  border-radius: 999px;
  background: linear-gradient(90deg, #13d7d0 0%, #39e6de 100%);
  color: #041014 !important;
  text-decoration: none;
  font-weight: 800;
  font-size: 16px;
  letter-spacing: 0.2px;
}
.footer {
  border-top: 1px solid #0f172a;
  text-align: center;
  padding: 18px 0 8px;
}
.footer p { margin: 8px 0; color: #9ca3af; font-size: 12px; line-height: 1.6; }
.meta { color: #6b7280; font-size: 11px !important; }
@media only screen and (max-width: 700px) {
  .card { width: 100% !important; border-radius: 0; }
  .inner { padding: 22px 18px !important; }
  .title { font-size: 32px !important; }
  .copy { font-size: 16px !important; }
}
</style>
        """.strip()

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
                "<h2 class=\"section-title\">Reflection highlights</h2>"
                "<div class=\"panel\">"
                f"{identity_line}{proof_line}"
                "</div>"
            )

        unsubscribe_url = ParentEmailTemplates._unsubscribe_url(unsubscribe_token)
        logo_html = ParentEmailTemplates._brand_logo_html()
        cta_url = ParentEmailTemplates._cta_url()
        social_links = ParentEmailTemplates._social_links_html()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Welcome to the AI Confidence Cohort</title>
    {ParentEmailTemplates._base_styles()}
</head>
<body>
  <div class=\"outer\">
    <table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" width=\"100%\">
      <tr>
        <td align=\"center\">
          <div class=\"card\">
            <div class=\"inner\">
              <div style=\"text-align:center;\">{logo_html}</div>
              <div class=\"divider\"></div>

              <p class=\"kicker\">Welcome to the</p>
              <h1 class=\"title\">AI Confidence <span class=\"title-accent\">Cohort</span></h1>
              <p class=\"subdate\">Week {week_number} update - {datetime.now().strftime('%B %Y')}</p>

              <p class=\"copy\">Hey there!</p>
              <p class=\"copy\">
                Your child just took another step toward <strong>wielding AI with real confidence</strong>.
                This update summarizes progress from Week {week_number}.
              </p>

              <h2 class=\"section-title\">Here is what to expect</h2>
              <ul class=\"list\">
                <li><strong>Habits practiced:</strong> {habits_display}</li>
                <li><strong>AI thinking interactions:</strong> {interaction_count}</li>
                <li><strong>Current stage:</strong> {zone_message}</li>
                <li><strong>Focus area:</strong> {jtbd_focus.replace('_', ' ').title()}</li>
              </ul>

              <div class=\"panel\">
                <p><strong>Dual-pillar growth</strong></p>
                <p>1) Access expertise they do not yet have</p>
                <p>2) Think clearly with that expertise</p>
                <p>These are durable habits that transfer beyond any single tool.</p>
              </div>

              {reflection_html}

              <p class=\"copy\">
                Your first move this week: check in with your child about one thing they learned and one
                habit they want to strengthen next.
              </p>

              <div class=\"cta-wrap\">
                <a class=\"cta-btn\" href=\"{cta_url}\">Join the Discord Now</a>
              </div>

              <div class=\"footer\">
                {social_links}
                <p>Nairobi, Kenya</p>
                <p>You are receiving this because your child chose to share progress updates.</p>
                <p><a href=\"{unsubscribe_url}\">Unsubscribe from future parent emails</a></p>
                <p class=\"meta\">&copy; {datetime.now().year} K2M Labs. All rights reserved.</p>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </table>
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
            "<p class=\"copy\"><strong>Privacy note:</strong> Your child chose anonymous peer publication. "
            "Their progress is still shared with you as parent/guardian.</p>"
            if is_anonymous
            else ""
        )
        unsubscribe_url = ParentEmailTemplates._unsubscribe_url(unsubscribe_token)
        logo_html = ParentEmailTemplates._brand_logo_html()
        cta_url = ParentEmailTemplates._cta_url()
        social_links = ParentEmailTemplates._social_links_html()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Week 8 Parent Report</title>
    {ParentEmailTemplates._base_styles()}
</head>
<body>
  <div class=\"outer\">
    <table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" width=\"100%\">
      <tr>
        <td align=\"center\">
          <div class=\"card\">
            <div class=\"inner\">
              <div style=\"text-align:center;\">{logo_html}</div>
              <div class=\"divider\"></div>

              <p class=\"kicker\">Final milestone</p>
              <h1 class=\"title\">Week 8 <span class=\"title-accent\">Parent Report</span></h1>
              <p class=\"subdate\">{datetime.now().strftime('%B %Y')}</p>

              <p class=\"copy\">
                <strong>{student_name}</strong> completed their artifact and demonstrated
                practical AI thinking growth.
              </p>

              <h2 class=\"section-title\">The question they wrestled with</h2>
              <div class=\"panel\">
                <p><em>{artifact_question}</em></p>
              </div>

              <h2 class=\"section-title\">Their thinking journey</h2>
              <div class=\"panel\">
                <p>{artifact_summary}</p>
              </div>

              <h2 class=\"section-title\">Habits demonstrated</h2>
              <div class=\"panel\">
                <p>{habits_text}</p>
                <p><strong>Final stage:</strong> {zone}</p>
              </div>

              {anonymous_note}

              <h2 class=\"section-title\">Why this matters</h2>
              <ul class=\"list\">
                <li>They can access expertise they did not have before.</li>
                <li>They can think clearly with that expertise for real decisions.</li>
                <li>These habits transfer to university, career, and life.</li>
              </ul>

              <div class=\"cta-wrap\">
                <a class=\"cta-btn\" href=\"{cta_url}\">Join the Discord Now</a>
              </div>

              <div class=\"footer\">
                {social_links}
                <p>This update was sent after Week 8 artifact completion.</p>
                <p><a href=\"{unsubscribe_url}\">Unsubscribe from future parent emails</a></p>
                <p class=\"meta\">&copy; {datetime.now().year} K2M Labs. All rights reserved.</p>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </table>
  </div>
</body>
</html>
        """
        return html.strip()

    @staticmethod
    def student_activation_email(
        student_name: str,
        cohort_start_date: str,
        discord_invite_url: str,
    ) -> str:
        """
        Brevo Email #4: Student activation/welcome email after payment verification.
        Sent after Trevor verifies payment and activates the student.

        Args:
            student_name: Student's first name
            cohort_start_date: Cohort start date (ISO format or human-readable)
            discord_invite_url: Direct Discord invite link

        Returns:
            HTML email content with refund policy
        """
        # Parse and format date if ISO format
        try:
            from datetime import datetime
            if 'T' in cohort_start_date:
                parsed_date = datetime.fromisoformat(cohort_start_date.replace('Z', '+00:00'))
                formatted_date = parsed_date.strftime('%B %d, %Y')
            else:
                formatted_date = cohort_start_date
        except Exception:
            formatted_date = cohort_start_date

        logo_html = ParentEmailTemplates._brand_logo_html()
        cta_url = ParentEmailTemplates._cta_url()
        social_links = ParentEmailTemplates._social_links_html()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>You're In! Welcome to K2M</title>
    {ParentEmailTemplates._base_styles()}
</head>
<body>
  <div class="outer">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
      <tr>
        <td align="center">
          <div class="card">
            <div class="inner">
              <div style="text-align:center;">{logo_html}</div>
              <div class="divider"></div>

              <p class="kicker">Payment confirmed</p>
              <h1 class="title">You're In! <span class="title-accent">Welcome to K2M</span></h1>
              <p class="subdate">Cohort starts {formatted_date}</p>

              <p class="copy">
                Hey <strong>{student_name}</strong>!
              </p>

              <p class="copy">
                Great news — your payment has been verified and your spot in the cohort is officially <strong>confirmed</strong>.
              </p>

              <p class="copy">
                You now have full access to the Discord server and can join your fellow students in the <code>#welcome-lounge</code> channel.
              </p>

              <h2 class="section-title">What happens next</h2>
              <ul class="list">
                <li><strong>Join Discord:</strong> Use the link below to access the full server</li>
                <li><strong>Introduce yourself:</strong> Share a quick hello in <code>#introductions</code></li>
                <li><strong>Start exploring:</strong> Check out <code>#welcome-lounge</code> for previews of what's coming</li>
                <li><strong>Mark your calendar:</strong> Cohort starts on {formatted_date}</li>
              </ul>

              <div class="panel">
                <p><strong>Your Discord invite link</strong></p>
                <p>This single-use link grants you full access to the cohort server:</p>
                <p style="text-align:center; margin:16px 0;">
                  <a href="{discord_invite_url}" style="color:#13d7d0; word-break:break-all;">{discord_invite_url}</a>
                </p>
                <p style="font-size:13px; color:#9ca3af;">Link expires in 7 days. If you need a fresh one, just reply to this email.</p>
              </div>

              <h2 class="section-title">Before the cohort begins</h2>
              <div class="panel">
                <p><strong>In the meantime:</strong></p>
                <p>1. Explore the <code>#welcome-lounge</code> — get a taste of the thinking practices you'll develop</p>
                <p>2. Connect with fellow students in <code>#introductions</code></p>
                <p>3. Review the <code>#program-guide</code> channel for the full schedule and expectations</p>
              </div>

              <h2 class="section-title">Refund policy</h2>
              <div class="panel">
                <p><strong>100% refund guarantee — no questions asked</strong></p>
                <p>If you decide this program isn't right for you, you can request a full refund:</p>
                <p>• <strong>Before cohort start:</strong> Full refund, 100%</p>
                <p>• <strong>Week 1:</strong> Full refund, no questions asked</p>
                <p>• <strong>After Week 1:</strong> Refunds reviewed case-by-case</p>
                <p style="margin-top:12px; font-size:14px; color:#9ca3af;">
                  To request a refund, simply reply to this email or DM <strong>@Trevor</strong> on Discord.
                  Refunds are processed within 5 business days via M-Pesa.
                </p>
              </div>

              <div class="cta-wrap">
                <a class="cta-btn" href="{discord_invite_url}">Join Discord Now</a>
              </div>

              <p class="copy">
                Questions? Just reply to this email — I read every message personally.
              </p>

              <div class="footer">
                {social_links}
                <p>Nairobi, Kenya</p>
                <p>You're receiving this because you enrolled in K2M's AI Thinking Skills Cohort.</p>
                <p class="meta">&copy; {datetime.now().year} K2M Labs. All rights reserved.</p>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </table>
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
