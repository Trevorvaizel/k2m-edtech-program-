#!/usr/bin/env python
"""
Task 7.14 - Brevo template lifecycle automation.

Creates/updates the 7 required transactional templates, runs optional test sends,
and writes an evidence report for sprint notes.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "_bmad-output/cohort-design-artifacts/operations/sprint/task-notes/7.14-brevo-templates.json"
)
DEFAULT_SCREENSHOT = (
    PROJECT_ROOT / "cis-discord-bot/assets/email/email-1/discord-orientation-annotated.png"
)


def iso_utc_now() -> str:
    return (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def png_data_uri(path: Path) -> str:
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def logo_url() -> str:
    value = os.getenv("BREVO_TEMPLATE_LOGO_URL", "").strip()
    if value:
        return value
    return "https://k2m-landing.vercel.app/k2m-logo.svg"


def html_shell(step_badge: str, title: str, subtitle: str, body_html: str) -> str:
    brand_logo_url = logo_url()
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background: #e5e7eb;
      font-family: Arial, Helvetica, sans-serif;
      color: #e5e7eb;
    }}
    .outer {{
      width: 100%;
      padding: 16px 0;
      background: #e5e7eb;
    }}
    .card {{
      width: 640px;
      max-width: 640px;
      margin: 0 auto;
      background: #050608;
      border: 1px solid #0f172a;
      border-radius: 12px;
      overflow: hidden;
    }}
    .hero {{
      padding: 26px 28px 12px;
      text-align: center;
    }}
    .logo-row {{
      margin: 0 auto 12px;
    }}
    .logo {{
      display: block;
      width: 84px;
      max-width: 84px;
      height: auto;
      margin: 0 auto;
      border: 0;
    }}
    .blue-line {{
      height: 1px;
      border: 0;
      margin: 0 0 14px;
      background: #13d7d0;
    }}
    .hero h1 {{
      margin: 0;
      font-size: 38px;
      line-height: 1.2;
      color: #f9fafb;
      font-weight: 800;
    }}
    .hero .subtitle {{
      margin: 8px 0 0;
      color: #2de2dc;
      font-size: 12px;
      letter-spacing: 1px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .preheader {{
      display: none;
      max-height: 0;
      overflow: hidden;
      opacity: 0;
      color: transparent;
    }}
    .body {{
      padding: 24px 30px 30px;
      font-size: 15px;
      line-height: 1.65;
      color: #d1d5db;
    }}
    .body p {{
      margin: 0 0 12px;
    }}
    .body strong {{
      color: #f9fafb;
    }}
    .panel {{
      border: 1px solid #1f2937;
      background: #0b0f14;
      border-radius: 10px;
      padding: 14px 16px;
      margin: 16px 0;
    }}
    .cta {{
      display: inline-block;
      background: #2de2dc;
      color: #041014 !important;
      text-decoration: none;
      border-radius: 999px;
      padding: 14px 30px;
      font-weight: 800;
      font-size: 16px;
      letter-spacing: 0.2px;
      margin: 10px 0 18px;
    }}
    .note {{
      color: #9ca3af;
      font-size: 13px;
    }}
    .footer-divider {{
      height: 1px;
      background: #111827;
      margin: 24px 0 18px;
      border: 0;
    }}
    .footer {{
      color: #9ca3af;
      font-size: 12px;
      text-align: center;
    }}
    .img {{
      width: 100%;
      max-width: 560px;
      border-radius: 10px;
      border: 1px solid #334155;
      display: block;
      margin: 10px auto;
      height: auto;
    }}
    .social {{
      margin: 16px 0 8px;
      text-align: center;
    }}
    .social a {{
      display: inline-block;
      width: 26px;
      height: 26px;
      line-height: 26px;
      text-align: center;
      border-radius: 999px;
      margin: 0 5px;
      text-decoration: none;
      font-weight: 700;
      font-size: 12px;
      color: #f8fafc;
      background: #1f2937;
    }}
    .social .ig {{ background: #e1306c; }}
    .social .x {{ background: #111827; border: 1px solid #374151; }}
    .social .wa {{ background: #16a34a; }}
    .social .dc {{ background: #5865f2; }}
    @media only screen and (max-width: 700px) {{
      .outer {{
        padding: 0;
      }}
      .card {{
        width: 100% !important;
        max-width: 100% !important;
        border-radius: 0 !important;
        border-left: 0;
        border-right: 0;
      }}
      .hero h1 {{
        font-size: 32px;
      }}
      .body {{
        padding: 20px 18px 24px;
        font-size: 14px;
      }}
    }}
  </style>
</head>
<body>
  <div class="preheader">{step_badge}</div>
  <div class="outer">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
      <tr>
        <td align="center">
          <div class="card">
            <div class="hero">
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" class="logo-row">
                <tr>
                  <td><img class="logo" src="{brand_logo_url}" alt="K2M logo" width="84" /></td>
                </tr>
              </table>
              <hr class="blue-line" />
              <h1>{title}</h1>
              <p class="subtitle">{subtitle}</p>
            </div>
            <div class="body">
              {body_html}
              <hr class="footer-divider" />
              <div class="footer">
                <div class="social">
                  <a class="ig" href="{{{{params.instagram_url}}}}">📸</a>
                  <a class="x" href="{{{{params.x_url}}}}">X</a>
                  <a class="wa" href="{{{{params.whatsapp_url}}}}">💬</a>
                  <a class="dc" href="{{{{params.discord_url}}}}">🎮</a>
                </div>
                <div>Nairobi, Kenya</div>
                Trevor from K2M &lt;trevor@k2mlabs.com&gt;
              </div>
            </div>
          </div>
        </td>
      </tr>
    </table>
  </div>
</body>
</html>"""


@dataclass
class TemplateSpec:
    key: str
    env_var: str
    name: str
    subject: str
    html_content: str
    test_params: Dict[str, Any]


def build_template_specs(screenshot_uri: str) -> List[TemplateSpec]:
    common_params = {
        "instagram_url": "https://instagram.com/k2mlabs",
        "x_url": "https://x.com/k2mlabs",
        "whatsapp_url": "https://wa.me/254700000000",
        "discord_url": "https://discord.gg/example-invite",
    }

    email_1_body = f"""
<p>Hey {{{{params.first_name}}}}! 👋</p>
<p>You completed Step 1. Join Discord to unlock Step 2 and keep momentum.</p>
<p><a class="cta" href="{{{{params.discord_invite_link}}}}">🚀 Join the Discord Now</a></p>
<div class="panel">
  <p><strong>New to Discord?</strong> Use this quick map before you click around.</p>
  <img class="img" src="{screenshot_uri}" alt="Annotated Discord orientation visual" />
  <p>✨ Your channels are in the left sidebar.</p>
  <p>✨ KIRA messages you in DMs.</p>
  <p>✨ Server name at the top: K2M Cohort #1.</p>
</div>
<p class="note">If the link expires, reply to this email for a fresh invite.</p>
"""

    email_15_body = """
<p>Hey {{params.first_name}}! ⏰</p>
<p>This is your 48-hour check-in. Most students need a second tap to complete Discord join.</p>
<p><a class="cta" href="{{params.discord_invite_link}}">🚀 Join Discord Now</a></p>
<div class="panel">
  <p><strong>Need help?</strong> Reply with "help" and a facilitator will walk you through it.</p>
</div>
"""

    email_175_body = """
<p>Hey {{params.first_name}}! ⏳</p>
<p>This is your 5-day final reminder for Step 2.</p>
<p><a class="cta" href="{{params.discord_invite_link}}">🚀 Final Discord Link</a></p>
<div class="panel">
  <p>Your invite may expire soon. Reply and a facilitator can refresh it.</p>
</div>
"""

    email_2_body = """
<p>Hey {{params.first_name}}! 💳</p>
<p>Your enrollment profile is complete. Next: submit payment and your M-Pesa code.</p>
<p><a class="cta" href="{{params.mpesa_submit_url}}">✅ Submit M-Pesa Code</a></p>
<div class="panel">
  <p><strong>M-Pesa tutorial:</strong> <a href="{{params.mpesa_tutorial_url}}">{{params.mpesa_tutorial_url}}</a></p>
  <p><strong>Refund policy:</strong> Full refund available if requested 7+ days before cohort start ({{params.week1_start_date}}). Contact a facilitator for help.</p>
</div>
"""

    email_3_body = """
<p>Hey {{params.first_name}}! ✅</p>
<p>We received your M-Pesa code and queued verification.</p>
<div class="panel">
  <p>Step 4 is now in facilitator review (usually within 24 hours).</p>
</div>
"""

    email_4_body = """
<p>Hey {{params.first_name}}! 🎉</p>
<p>Your payment is confirmed. You are fully activated in Cohort 1.</p>
<div class="panel">
  <p><strong>First live session:</strong> {{params.first_session_date}} at 6 PM EAT</p>
  <p><strong>Week 1 starts:</strong> {{params.week1_start_date}}</p>
  <p><strong>Your cluster:</strong> {{params.cluster_name}}</p>
</div>
<p><a class="cta" href="{{params.discord_invite_link}}">🚀 Open Discord</a></p>
"""

    email_5_body = """
<p>Hey {{params.first_name}}! 📝</p>
<p>Thanks for your interest. Cohort 1 is currently full.</p>
<div class="panel">
  <p>You are <strong>#{{params.waitlist_number}}</strong> on the priority waitlist.</p>
  <p>We will contact you first when the next intake opens.</p>
</div>
"""

    return [
        TemplateSpec(
            key="email_1",
            env_var="BREVO_TEMPLATE_EMAIL_1",
            name="K2M Cohort 1 - Email #1 Discord Invite",
            subject="K2M - Step 1 done! Join Discord (Step 2 of 4)",
            html_content=html_shell(
                step_badge="Step 2 of 4",
                title="Join Discord to Continue",
                subtitle="Your onboarding is in motion.",
                body_html=email_1_body,
            ),
            test_params={
                **common_params,
                "first_name": "Trevor",
                "discord_invite_link": "https://discord.gg/example-invite",
            },
        ),
        TemplateSpec(
            key="email_1_5",
            env_var="BREVO_TEMPLATE_EMAIL_1_5",
            name="K2M Cohort 1 - Email #1.5 48h Nudge",
            subject="K2M - Step 2 reminder (48h): Join Discord",
            html_content=html_shell(
                step_badge="Step 2 of 4",
                title="48h Reminder",
                subtitle="We are holding your spot while you join Discord.",
                body_html=email_15_body,
            ),
            test_params={
                **common_params,
                "first_name": "Trevor",
                "discord_invite_link": "https://discord.gg/example-invite",
            },
        ),
        TemplateSpec(
            key="email_1_75",
            env_var="BREVO_TEMPLATE_EMAIL_1_75",
            name="K2M Cohort 1 - Email #1.75 Day-5 Final Nudge",
            subject="K2M - Step 2 final reminder (Day 5)",
            html_content=html_shell(
                step_badge="Step 2 of 4",
                title="Day-5 Final Reminder",
                subtitle="Complete Discord join to keep momentum.",
                body_html=email_175_body,
            ),
            test_params={
                **common_params,
                "first_name": "Trevor",
                "discord_invite_link": "https://discord.gg/example-invite",
            },
        ),
        TemplateSpec(
            key="email_2",
            env_var="BREVO_TEMPLATE_EMAIL_2",
            name="K2M Cohort 1 - Email #2 Payment Instructions",
            subject="K2M - Step 3 of 4: Complete your payment",
            html_content=html_shell(
                step_badge="Step 3 of 4",
                title="Payment Instructions",
                subtitle="Submit your M-Pesa payment code.",
                body_html=email_2_body,
            ),
            test_params={
                **common_params,
                "first_name": "Trevor",
                "mpesa_submit_url": "https://k2m-edtech.program/mpesa-submit?token=example",
                "mpesa_tutorial_url": "https://k2m-edtech.program/m-pesa-payment",
                "week1_start_date": "March 16, 2026",
            },
        ),
        TemplateSpec(
            key="email_3",
            env_var="BREVO_TEMPLATE_EMAIL_3",
            name="K2M Cohort 1 - Email #3 M-Pesa Received",
            subject="K2M - Step 4 pending: M-Pesa code received",
            html_content=html_shell(
                step_badge="Step 4 of 4",
                title="M-Pesa Code Received",
                subtitle="Verification queue has started.",
                body_html=email_3_body,
            ),
            test_params={
                **common_params,
                "first_name": "Trevor",
            },
        ),
        TemplateSpec(
            key="email_4",
            env_var="BREVO_TEMPLATE_EMAIL_4",
            name="K2M Cohort 1 - Email #4 Activation Welcome",
            subject="K2M - Step 4 complete: You're in",
            html_content=html_shell(
                step_badge="Step 4 complete",
                title="Welcome to Cohort 1",
                subtitle="Your access is now active.",
                body_html=email_4_body,
            ),
            test_params={
                **common_params,
                "first_name": "Trevor",
                "first_session_date": "March 18, 2026",
                "week1_start_date": "March 16, 2026",
                "cluster_name": "Cluster 2",
                "discord_invite_link": "https://discord.gg/example-invite",
            },
        ),
        TemplateSpec(
            key="email_5",
            env_var="BREVO_TEMPLATE_EMAIL_5",
            name="K2M Cohort 1 - Email #5 Waitlist Confirmation",
            subject="K2M - Waitlist confirmation",
            html_content=html_shell(
                step_badge="Waitlist",
                title="You're on the Priority List",
                subtitle="We will notify you first when seats open.",
                body_html=email_5_body,
            ),
            test_params={
                **common_params,
                "first_name": "Trevor",
                "waitlist_number": "12",
            },
        ),
    ]


class BrevoClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=45.0) as client:
            response = client.request(
                method,
                url,
                headers=self.headers,
                json=json_payload,
                params=params,
            )
        return response

    def list_templates(self) -> List[Dict[str, Any]]:
        templates: List[Dict[str, Any]] = []
        offset = 0
        limit = 500

        while True:
            response = self._request(
                "GET",
                "/smtp/templates",
                params={"limit": limit, "offset": offset},
            )
            response.raise_for_status()
            payload = response.json()
            chunk = payload.get("templates", []) or []
            if not chunk:
                break
            templates.extend(chunk)
            if len(chunk) < limit:
                break
            offset += limit
        return templates

    def create_template(
        self,
        *,
        template_name: str,
        subject: str,
        html_content: str,
        sender_name: str,
        sender_email: str,
    ) -> int:
        payload = {
            "templateName": template_name,
            "subject": subject,
            "htmlContent": html_content,
            "sender": {"name": sender_name, "email": sender_email},
            "isActive": True,
        }
        response = self._request("POST", "/smtp/templates", json_payload=payload)
        if response.status_code not in (200, 201, 202, 204):
            raise RuntimeError(
                f"create_template failed ({response.status_code}): {response.text[:300]}"
            )
        data = response.json()
        template_id = data.get("id")
        if not isinstance(template_id, int):
            raise RuntimeError(f"Unexpected template create response: {data}")
        return template_id

    def update_template(
        self,
        template_id: int,
        *,
        template_name: str,
        subject: str,
        html_content: str,
        sender_name: str,
        sender_email: str,
    ) -> None:
        payload = {
            "templateName": template_name,
            "subject": subject,
            "htmlContent": html_content,
            "sender": {"name": sender_name, "email": sender_email},
            "isActive": True,
        }
        response = self._request(
            "PUT",
            f"/smtp/templates/{template_id}",
            json_payload=payload,
        )
        if response.status_code not in (200, 201, 202, 204):
            raise RuntimeError(
                f"update_template failed ({response.status_code}): {response.text[:300]}"
            )

    def send_test(
        self,
        *,
        template_id: int,
        to_email: str,
        sender_name: str,
        sender_email: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload = {
            "to": [{"email": to_email}],
            "sender": {"name": sender_name, "email": sender_email},
            "templateId": template_id,
            "params": params,
        }
        response = self._request("POST", "/smtp/email", json_payload=payload)
        data: Dict[str, Any]
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text[:500]}
        return {
            "status_code": response.status_code,
            "success": response.status_code in (200, 201, 202),
            "response": data,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Task 7.14 Brevo template automation")
    parser.add_argument("--env-file", default="cis-discord-bot/.env")
    parser.add_argument("--base-url", default=os.getenv("BREVO_BASE_URL", "https://api.brevo.com/v3"))
    parser.add_argument("--sender-email", default=os.getenv("EMAIL_FROM", "trevor@k2mlabs.com"))
    parser.add_argument("--sender-name", default=os.getenv("EMAIL_FROM_NAME", "Trevor from K2M"))
    parser.add_argument("--screenshot", default=str(DEFAULT_SCREENSHOT))
    parser.add_argument("--apply", action="store_true", help="Create/update templates in Brevo")
    parser.add_argument("--send-test", action="store_true", help="Send one test email per template")
    parser.add_argument("--test-to", default="k2m.labs@gmail.com")
    parser.add_argument(
        "--test-first-name",
        default="",
        help="Optional first_name override for test sends (e.g. Ibrahim)",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def find_template_by_name(
    templates: List[Dict[str, Any]],
    name: str,
) -> Optional[Dict[str, Any]]:
    for template in templates:
        template_name = str(template.get("name") or template.get("templateName") or "").strip()
        if template_name == name:
            return template
    return None


def main() -> int:
    args = parse_args()

    env_file = Path(args.env_file)
    load_env_file(env_file)

    api_key = os.getenv("BREVO_API_KEY", "").strip()
    if not api_key:
        print("ERROR: BREVO_API_KEY is not set (env or env-file).")
        return 2

    screenshot_path = Path(args.screenshot)
    if not screenshot_path.exists():
        print(f"ERROR: Required screenshot missing: {screenshot_path}")
        return 2

    screenshot_uri = png_data_uri(screenshot_path)
    specs = build_template_specs(screenshot_uri)
    if args.test_first_name:
        for spec in specs:
            if "first_name" in spec.test_params:
                spec.test_params["first_name"] = args.test_first_name
    client = BrevoClient(api_key=api_key, base_url=args.base_url)

    try:
        existing = client.list_templates()
    except Exception as exc:
        print(f"ERROR: Failed to list Brevo templates: {exc}")
        return 2

    report: Dict[str, Any] = {
        "timestamp_utc": iso_utc_now(),
        "task_id": "7.14",
        "mode": {
            "apply": bool(args.apply),
            "send_test": bool(args.send_test),
        },
        "sender": {"email": args.sender_email, "name": args.sender_name},
        "base_url": args.base_url,
        "templates": [],
        "railway_env_map": {},
    }

    all_ok = True

    for spec in specs:
        item: Dict[str, Any] = {
            "key": spec.key,
            "env_var": spec.env_var,
            "template_name": spec.name,
            "subject": spec.subject,
        }
        match = find_template_by_name(existing, spec.name)
        template_id: Optional[int] = None

        try:
            if args.apply:
                if match:
                    template_id = int(match["id"])
                    client.update_template(
                        template_id,
                        template_name=spec.name,
                        subject=spec.subject,
                        html_content=spec.html_content,
                        sender_name=args.sender_name,
                        sender_email=args.sender_email,
                    )
                    item["action"] = "updated"
                else:
                    template_id = client.create_template(
                        template_name=spec.name,
                        subject=spec.subject,
                        html_content=spec.html_content,
                        sender_name=args.sender_name,
                        sender_email=args.sender_email,
                    )
                    item["action"] = "created"
                item["template_id"] = template_id
            else:
                if match:
                    template_id = int(match["id"])
                    item["action"] = "found"
                    item["template_id"] = template_id
                else:
                    item["action"] = "missing"
                    all_ok = False

            if template_id is not None:
                report["railway_env_map"][spec.env_var] = template_id

            if args.send_test:
                if template_id is None:
                    item["test_send"] = {"success": False, "reason": "template_missing"}
                    all_ok = False
                else:
                    test_result = client.send_test(
                        template_id=template_id,
                        to_email=args.test_to,
                        sender_name=args.sender_name,
                        sender_email=args.sender_email,
                        params=spec.test_params,
                    )
                    item["test_send"] = test_result
                    if not test_result["success"]:
                        all_ok = False
        except Exception as exc:
            item["error"] = str(exc)
            all_ok = False

        report["templates"].append(item)

    report["overall_status"] = "pass" if all_ok else "fail"

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Output: {output_path}")
    print(f"Overall status: {report['overall_status']}")
    print("Railway env mappings:")
    for env_name, template_id in report["railway_env_map"].items():
        print(f"  {env_name}={template_id}")
    if args.send_test:
        print(f"Test recipient: {args.test_to}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

