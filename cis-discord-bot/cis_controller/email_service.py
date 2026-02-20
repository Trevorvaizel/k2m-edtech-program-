"""
Email Service Integration (Task 4.6)

Handles sending emails via SendGrid or Mailgun for parent updates.
Implements Story 5.3 parent email delivery system.
"""

import logging
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


@dataclass
class EmailResult:
    """Result of email send operation."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


class EmailService:
    """
    Email service abstraction supporting SendGrid and Mailgun.

    Environment variables:
        SENDGRID_API_KEY: SendGrid API key (preferred)
        MAILGUN_API_KEY: Mailgun private API key (fallback)
        MAILGUN_DOMAIN: Optional Mailgun sending domain override
        EMAIL_FROM: Default sender email (default: trevor@k2mlabs.com)
    """

    def __init__(self):
        self.sendgrid_key = os.getenv('SENDGRID_API_KEY')
        self.mailgun_key = os.getenv('MAILGUN_API_KEY')
        self.mailgun_domain = os.getenv('MAILGUN_DOMAIN', '').strip()
        self.from_email = os.getenv('EMAIL_FROM', 'trevor@k2mlabs.com')
        self.from_name = os.getenv('EMAIL_FROM_NAME', 'Trevor from K2M')
        self.dry_run = os.getenv('EMAIL_DRY_RUN', 'false').strip().lower() in {"1", "true", "yes", "on"}

        # Determine active provider
        if self.sendgrid_key:
            self.provider = 'sendgrid'
            logger.info("EmailService initialized with SendGrid provider")
        elif self.mailgun_key:
            self.provider = 'mailgun'
            logger.info("EmailService initialized with Mailgun provider")
        else:
            self.provider = None
            if self.dry_run:
                logger.warning("EmailService initialized without provider in dry-run mode")
            else:
                logger.error("EmailService initialized without provider keys (set SENDGRID_API_KEY or MAILGUN_API_KEY)")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> EmailResult:
        """
        Send an email using the configured provider.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML email body
            text_content: Plain text fallback (optional)
            from_email: Sender email (default from env)
            from_name: Sender name (default from env)
            reply_to: Reply-to address (optional)

        Returns:
            EmailResult with success status and details
        """
        from_email = from_email or self.from_email
        from_name = from_name or self.from_name

        # Log email for debugging
        logger.info(f"Email to {to_email}: {subject[:50]}...")

        # If no provider configured, only succeed in explicit dry-run mode.
        if not self.provider:
            if self.dry_run:
                logger.info(
                    f"[EMAIL DRY RUN]\n"
                    f"To: {to_email}\n"
                    f"Subject: {subject}\n"
                    f"HTML length: {len(html_content)} chars"
                )
                return EmailResult(
                    success=True,
                    message_id=f"dryrun_{datetime.now().isoformat()}",
                    error="Dry-run mode enabled (EMAIL_DRY_RUN=true)"
                )
            logger.error("Email send aborted: no provider configured and dry-run disabled")
            return EmailResult(
                success=False,
                error="No email provider configured. Set SENDGRID_API_KEY or MAILGUN_API_KEY (or EMAIL_DRY_RUN=true)."
            )

        try:
            if self.provider == 'sendgrid':
                return await self._send_via_sendgrid(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=from_email,
                    from_name=from_name,
                    reply_to=reply_to,
                )
            elif self.provider == 'mailgun':
                return await self._send_via_mailgun(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    from_email=from_email,
                    from_name=from_name,
                    reply_to=reply_to,
                )
            else:
                return EmailResult(
                    success=False,
                    error=f"Unknown provider: {self.provider}"
                )

        except Exception as exc:
            logger.error(f"Failed to send email to {to_email}: {exc}", exc_info=True)
            return EmailResult(
                success=False,
                error=str(exc)
            )

    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: str,
        from_name: str,
        reply_to: Optional[str],
    ) -> EmailResult:
        """Send email via SendGrid API."""
        url = "https://api.sendgrid.com/v3/mail/send"

        headers = {
            "Authorization": f"Bearer {self.sendgrid_key}",
            "Content-Type": "application/json",
        }

        # Build SendGrid API payload
        personalizations = [{
            "to": [{"email": to_email}],
            "subject": subject,
        }]

        content = []
        content.append({
            "type": "text/html",
            "value": html_content
        })

        if text_content:
            content.append({
                "type": "text/plain",
                "value": text_content
            })

        payload = {
            "personalizations": personalizations,
            "from": {
                "email": from_email,
                "name": from_name
            },
            "content": content,
        }
        if reply_to:
            payload["reply_to"] = {"email": reply_to}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=30.0
            )

            # SendGrid returns 202 for success
            if response.status_code in (200, 202):
                message_id = response.headers.get('X-Message-Id')
                logger.info(f"SendGrid email sent to {to_email}: {message_id}")
                return EmailResult(
                    success=True,
                    message_id=message_id,
                    status_code=response.status_code
                )
            else:
                logger.error(
                    f"SendGrid error {response.status_code}: {response.text[:200]}"
                )
                return EmailResult(
                    success=False,
                    status_code=response.status_code,
                    error=response.text[:500]
                )

    async def _send_via_mailgun(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: str,
        from_name: str,
        reply_to: Optional[str],
    ) -> EmailResult:
        """Send email via Mailgun API."""
        # Use explicit Mailgun domain when configured; fallback to sender domain.
        domain = self.mailgun_domain or (
            from_email.split('@')[-1] if '@' in from_email else 'mg.k2mlabs.com'
        )
        url = f"https://api.mailgun.net/v3/{domain}/messages"

        auth = ("api", self.mailgun_key)

        data = {
            "from": f"{from_name} <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }

        if text_content:
            data["text"] = text_content
        if reply_to:
            data["h:Reply-To"] = reply_to

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                auth=auth,
                data=data,
                timeout=30.0
            )

            # Mailgun returns 200 for success
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('id', '')
                logger.info(f"Mailgun email sent to {to_email}: {message_id}")
                return EmailResult(
                    success=True,
                    message_id=message_id,
                    status_code=response.status_code
                )
            else:
                logger.error(
                    f"Mailgun error {response.status_code}: {response.text[:200]}"
                )
                return EmailResult(
                    success=False,
                    status_code=response.status_code,
                    error=response.text[:500]
                )

    async def send_batch_emails(
        self,
        emails: List[Dict[str, str]],
    ) -> List[EmailResult]:
        """
        Send multiple emails in sequence.

        Args:
            emails: List of dicts with keys:
                - to_email: recipient email
                - subject: email subject
                - html_content: HTML body
                - text_content: optional text body

        Returns:
            List of EmailResult in same order as input
        """
        results = []

        for email_data in emails:
            result = await self.send_email(
                to_email=email_data['to_email'],
                subject=email_data['subject'],
                html_content=email_data['html_content'],
                text_content=email_data.get('text_content'),
            )
            results.append(result)

            # Brief pause between sends to avoid rate limiting
            if email_data != emails[-1]:  # Not the last one
                import asyncio
                await asyncio.sleep(0.5)

        return results


# Singleton instance for reuse
_email_service_instance: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create email service singleton instance."""
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
