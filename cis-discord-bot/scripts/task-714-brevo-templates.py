#!/usr/bin/env python
"""
Task 7.14 - Brevo template lifecycle automation.

Creates/updates the 7 required transactional templates, runs optional test sends,
and writes an evidence report for sprint notes.

2026-03-12 premium redesign: inline-CSS table layout matching K2M dark brand,
human copy across all 7 templates, Email #4 refund policy gap fixed.
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


# ---------------------------------------------------------------------------
# Premium dark visual shell — fully inline CSS for inbox compatibility
# ---------------------------------------------------------------------------

def _cta_button(href_param: str, label: str) -> str:
    """Table-based CTA button. href_param is the Brevo {{params.xxx}} token."""
    return f"""<table cellpadding="0" cellspacing="0" border="0" style="margin:24px 0 8px;">
  <tr>
    <td align="center" bgcolor="#2de2dc" style="border-radius:999px;">
      <a href="{href_param}"
         style="display:inline-block;padding:16px 40px;font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:800;color:#041014;text-decoration:none;border-radius:999px;letter-spacing:0.2px;">{label}</a>
    </td>
  </tr>
</table>"""


def _bullet(bold: str, rest: str) -> str:
    return (
        f'<p style="margin:0 0 10px;font-family:Arial,Helvetica,sans-serif;font-size:15px;'
        f'line-height:1.6;color:#d1d5db;">'
        f'<span style="color:#2de2dc;font-weight:700;">&#10022;</span>&nbsp;'
        f'<strong style="color:#f9fafb;">{bold}</strong> {rest}</p>'
    )


def html_shell(
    step_badge: str,
    title: str,
    title_accent: str,
    subtitle: str,
    body_html: str,
) -> str:
    """
    Premium dark-brand email shell.

    title       — white first line  e.g. "Welcome to the"
    title_accent — teal second line e.g. "AI Confidence Cohort"
    subtitle    — small grey caps   e.g. "COHORT 1 · MARCH 2026"
    body_html   — pre-rendered HTML inserted into the body cell
    step_badge  — used as preheader text (hidden from visual render)
    """
    brand_logo = logo_url()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  <title>{title} {title_accent}</title>
</head>
<body style="margin:0;padding:0;background:#ffffff;">
  <!-- preheader -->
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;font-size:1px;color:transparent;">{step_badge}</div>

  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;">
    <tr>
      <td align="center" style="padding:32px 12px;">

        <!-- card — dark background, rounded, no outer dark container -->
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="background:#0a0a0a;border-radius:16px;overflow:hidden;max-width:600px;width:100%;">

          <!-- ── HEADER ── -->
          <tr>
            <td align="center" style="padding:52px 40px 32px;">
              <img src="{brand_logo}" width="96" alt="K2M"
                   style="display:block;margin:0 auto 28px;width:96px;height:auto;border:0;" />
              <!-- separator with gradient fade at both ends -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td height="1" style="background:linear-gradient(to right,transparent,#2de2dc 25%,#2de2dc 75%,transparent);font-size:1px;line-height:1px;">&nbsp;</td>
                </tr>
              </table>
              <p style="margin:24px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:36px;
                         font-weight:800;color:#f9fafb;line-height:1.15;text-align:center;">{title}</p>
              <p style="margin:4px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:36px;
                         font-weight:800;color:#2de2dc;line-height:1.15;text-align:center;">{title_accent}</p>
              <p style="margin:16px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:11px;
                         font-weight:700;letter-spacing:2.5px;color:#6b7280;text-transform:uppercase;
                         text-align:center;">{subtitle}</p>
            </td>
          </tr>

          <!-- ── BODY ── -->
          <tr>
            <td style="padding:8px 44px 44px;font-family:Arial,Helvetica,sans-serif;
                        font-size:15px;line-height:1.75;color:#e5e7eb;">
              {body_html}

              <!-- ── FOOTER ── -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr><td height="1" style="background:#1f2937;font-size:1px;line-height:1px;margin:28px 0;">&nbsp;</td></tr>
              </table>
              <br />

              <!-- social icons — glassmorphism circles + simpleicons CDN brand marks -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" style="padding-bottom:14px;">
                    <table cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <!-- Instagram — rose glass -->
                        <td style="padding:0 7px;">
                          <a href="{{{{params.instagram_url}}}}"
                             style="display:inline-block;width:34px;height:34px;border-radius:50%;background:rgba(225,48,108,0.14);border:1.5px solid rgba(225,48,108,0.55);text-decoration:none;text-align:center;line-height:34px;">
                            <img src="https://cdn.simpleicons.org/instagram/ffffff" width="16" height="16" alt="Instagram"
                                 style="vertical-align:middle;display:inline;border:0;" />
                          </a>
                        </td>
                        <!-- X / Twitter — white glass -->
                        <td style="padding:0 7px;">
                          <a href="{{{{params.x_url}}}}"
                             style="display:inline-block;width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,0.07);border:1.5px solid rgba(255,255,255,0.22);text-decoration:none;text-align:center;line-height:34px;">
                            <img src="https://cdn.simpleicons.org/x/ffffff" width="16" height="16" alt="X"
                                 style="vertical-align:middle;display:inline;border:0;" />
                          </a>
                        </td>
                        <!-- WhatsApp — green glass -->
                        <td style="padding:0 7px;">
                          <a href="{{{{params.whatsapp_url}}}}"
                             style="display:inline-block;width:34px;height:34px;border-radius:50%;background:rgba(37,211,102,0.13);border:1.5px solid rgba(37,211,102,0.55);text-decoration:none;text-align:center;line-height:34px;">
                            <img src="https://cdn.simpleicons.org/whatsapp/ffffff" width="16" height="16" alt="WhatsApp"
                                 style="vertical-align:middle;display:inline;border:0;" />
                          </a>
                        </td>
                        <!-- Discord — blurple glass -->
                        <td style="padding:0 7px;">
                          <a href="{{{{params.discord_url}}}}"
                             style="display:inline-block;width:34px;height:34px;border-radius:50%;background:rgba(88,101,242,0.14);border:1.5px solid rgba(88,101,242,0.55);text-decoration:none;text-align:center;line-height:34px;">
                            <img src="https://cdn.simpleicons.org/discord/ffffff" width="16" height="16" alt="Discord"
                                 style="vertical-align:middle;display:inline;border:0;" />
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <p style="text-align:center;font-family:Arial,Helvetica,sans-serif;font-size:12px;
                          color:#6b7280;margin:0 0 4px;">Nairobi, Kenya</p>
              <p style="text-align:center;font-family:Arial,Helvetica,sans-serif;font-size:11px;
                          color:#4b5563;margin:0;">
                &#169; 2026 K2M Labs. All rights reserved.<br />
                You're receiving this because you enrolled in the AI Confidence Cohort.
              </p>
            </td>
          </tr>

        </table>
        <!-- /card -->

      </td>
    </tr>
  </table>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Template specs
# ---------------------------------------------------------------------------

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

    # ── Email #1 — Discord Invite ────────────────────────────────────────────
    email_1_body = f"""<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Hey {{{{params.first_name}}}}! &#128075;
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  You've just taken the first step toward <strong style="color:#f9fafb;">wielding AI with real confidence.</strong>
  Over the next 8 weeks, you'll move from copying prompts to actually <em>thinking</em> with AI &#8212;
  guided by mentors, frameworks, and a community that has your back.
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Here's what to expect:
</p>
{_bullet("Pause &#8594; Context &#8594; Iterate", "&#8212; the thinking habits that change everything")}
{_bullet("Live weekly sessions", "with AI practitioners and mentors")}
{_bullet("A private Discord community", "for support, accountability &amp; collaboration")}
<p style="margin:14px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Your first move? <strong style="color:#f9fafb;">Join our Discord</strong> &#8212; it's where everything happens.
</p>
<table align="center" cellpadding="0" cellspacing="0" border="0" style="margin:24px auto 8px;">
  <tr>
    <td align="center" bgcolor="#2de2dc" style="border-radius:999px;">
      <a href="{{{{params.discord_invite_link}}}}"
         style="display:inline-block;padding:16px 40px;font-family:Arial,Helvetica,sans-serif;
                font-size:16px;font-weight:800;color:#041014;text-decoration:none;
                border-radius:999px;letter-spacing:0.2px;">&#128640; Join the Discord Now</a>
    </td>
  </tr>
</table>
<p style="margin:24px 0 10px;font-family:Arial,Helvetica,sans-serif;font-size:14px;
           line-height:1.6;color:#9ca3af;">
  <strong style="color:#d1d5db;">New to Discord?</strong> Here's a quick map of the server to help you find your way.
</p>
<img src="{screenshot_uri}" alt="Annotated Discord server map" width="520"
     style="display:block;width:100%;max-width:520px;height:auto;border-radius:10px;
            border:1px solid #1f2937;margin:0 auto 14px;" />
<p style="margin:0 0 6px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6;color:#9ca3af;">
  &#10024; Your channels are in the left sidebar.
</p>
<p style="margin:0 0 6px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6;color:#9ca3af;">
  &#10024; KIRA &#8212; our AI mentor &#8212; will message you directly in DMs.
</p>
<p style="margin:0 0 20px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6;color:#9ca3af;">
  &#10024; Look for the server named: <strong style="color:#d1d5db;">K2M Cohort #1</strong>.
</p>
<p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.6;color:#6b7280;">
  If the invite link expires before you get a chance to join, just reply to this email and we'll send you a fresh one.
</p>"""

    # ── Email #1.5 — 48h Nudge ───────────────────────────────────────────────
    email_15_body = """<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Hey {{params.first_name}}! &#9200;
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  It's been 48 hours since you registered, and I just wanted to make sure nothing slipped through the cracks.
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Your spot in the <strong style="color:#f9fafb;">AI Confidence Cohort</strong> is still reserved &#8212;
  but the next step is joining our Discord, where the real journey begins. It only takes two minutes.
</p>
<table align="center" cellpadding="0" cellspacing="0" border="0" style="margin:24px auto 8px;">
  <tr>
    <td align="center" bgcolor="#2de2dc" style="border-radius:999px;">
      <a href="{{params.discord_invite_link}}"
         style="display:inline-block;padding:16px 40px;font-family:Arial,Helvetica,sans-serif;
                font-size:16px;font-weight:800;color:#041014;text-decoration:none;
                border-radius:999px;letter-spacing:0.2px;">&#128640; Join Discord Now</a>
    </td>
  </tr>
</table>
<p style="margin:20px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.6;color:#6b7280;">
  Need a hand? Just reply to this email with &#8220;help&#8221; and someone from our team will walk you through it personally.
</p>"""

    # ── Email #1.75 — Day-5 Final Nudge ─────────────────────────────────────
    email_175_body = """<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Hey {{params.first_name}}! &#9203;
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  This is your final reminder. It's been 5 days since you registered for the
  <strong style="color:#f9fafb;">AI Confidence Cohort</strong>, and your Discord invite is about to expire.
</p>
<p style="margin:0 0 20px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  We'd hate for you to miss out on what we've built for you.
</p>
<table align="center" cellpadding="0" cellspacing="0" border="0" style="margin:0 auto 8px;">
  <tr>
    <td align="center" bgcolor="#2de2dc" style="border-radius:999px;">
      <a href="{{params.discord_invite_link}}"
         style="display:inline-block;padding:16px 40px;font-family:Arial,Helvetica,sans-serif;
                font-size:16px;font-weight:800;color:#041014;text-decoration:none;
                border-radius:999px;letter-spacing:0.2px;">&#128640; Join Discord &#8212; Final Link</a>
    </td>
  </tr>
</table>
<p style="margin:20px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.6;color:#6b7280;">
  If the link has already expired, just reply and a facilitator will send you a fresh one within a few hours.
</p>"""

    # ── Email #2 — Payment Instructions ─────────────────────────────────────
    email_2_body = """<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Hey {{params.first_name}}! &#128179;
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  You're almost there. Your enrollment profile is complete, and there's just one thing left to do:
  submit your M-Pesa payment to lock in your spot.
</p>
<p style="margin:0 0 6px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  <strong style="color:#f9fafb;">Amount:</strong> KES 5,000
</p>
<p style="margin:0 0 20px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  <strong style="color:#f9fafb;">Deadline:</strong> Before the cohort starts on {{params.week1_start_date}}
</p>
<table align="center" cellpadding="0" cellspacing="0" border="0" style="margin:0 auto 8px;">
  <tr>
    <td align="center" bgcolor="#2de2dc" style="border-radius:999px;">
      <a href="{{params.mpesa_submit_url}}"
         style="display:inline-block;padding:16px 40px;font-family:Arial,Helvetica,sans-serif;
                font-size:16px;font-weight:800;color:#041014;text-decoration:none;
                border-radius:999px;letter-spacing:0.2px;">&#9989; Submit M-Pesa Payment</a>
    </td>
  </tr>
</table>
<p style="margin:20px 0 6px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6;color:#9ca3af;">
  Need help completing the payment? We've put together a short tutorial to walk you through it:
  <a href="{{params.mpesa_tutorial_url}}"
     style="color:#2de2dc;text-decoration:none;">M-Pesa Payment Guide &#8250;</a>
</p>
<p style="margin:16px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.6;color:#6b7280;">
  <strong style="color:#9ca3af;">Refund policy:</strong> You're eligible for a full refund if you request it
  at least 7 days before the cohort starts ({{params.week1_start_date}}). Just reply to this email or reach out
  to a facilitator and we'll sort it out &#8212; no questions asked.
</p>"""

    # ── Email #3 — M-Pesa Received ───────────────────────────────────────────
    email_3_body = """<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Hey {{params.first_name}}! &#9989;
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  We've got your M-Pesa code and it's now in our verification queue.
  Our team typically confirms payments within <strong style="color:#f9fafb;">24 hours</strong>.
</p>
<p style="margin:0 0 20px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  You don't need to do anything right now &#8212; we'll send you a confirmation email the moment
  your payment clears and your spot is officially activated.
</p>
<p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Sit tight, you're almost in! &#127919;
</p>"""

    # ── Email #4 — Activation Welcome ───────────────────────────────────────
    # GAP FIX: Sprint spec requires refund policy in Email #4. Added below.
    email_4_body = """<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Hey {{params.first_name}}! &#127881;
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Your payment is confirmed and your spot is <strong style="color:#f9fafb;">officially activated.</strong>
  Welcome to the AI Confidence Cohort &#8212; we're genuinely excited to have you.
</p>
<p style="margin:0 0 10px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Here's what's coming up:
</p>
<p style="margin:0 0 8px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#d1d5db;">
  <span style="color:#2de2dc;font-weight:700;">&#10022;</span>&nbsp;
  <strong style="color:#f9fafb;">First live session:</strong> {{params.first_session_date}} at 6 PM EAT
</p>
<p style="margin:0 0 8px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#d1d5db;">
  <span style="color:#2de2dc;font-weight:700;">&#10022;</span>&nbsp;
  <strong style="color:#f9fafb;">Week 1 begins:</strong> {{params.week1_start_date}}
</p>
<p style="margin:0 0 20px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#d1d5db;">
  <span style="color:#2de2dc;font-weight:700;">&#10022;</span>&nbsp;
  <strong style="color:#f9fafb;">Your cluster:</strong> {{params.cluster_name}}
</p>
<p style="margin:0 0 20px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Everything happens in Discord. Your KIRA mentor will DM you with your personalised
  onboarding journey as soon as you're in.
</p>
<table align="center" cellpadding="0" cellspacing="0" border="0" style="margin:0 auto 8px;">
  <tr>
    <td align="center" bgcolor="#2de2dc" style="border-radius:999px;">
      <a href="{{params.discord_invite_link}}"
         style="display:inline-block;padding:16px 40px;font-family:Arial,Helvetica,sans-serif;
                font-size:16px;font-weight:800;color:#041014;text-decoration:none;
                border-radius:999px;letter-spacing:0.2px;">&#128640; Open Discord</a>
    </td>
  </tr>
</table>
<p style="margin:20px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.6;color:#6b7280;">
  <strong style="color:#9ca3af;">Cancellation reminder:</strong> You're entitled to a full refund if
  requested at least 7 days before the start date ({{params.week1_start_date}}). After that, all payments
  are final. If anything comes up, just reply here and we'll take care of you.
</p>"""

    # ── Email #5 — Waitlist ──────────────────────────────────────────────────
    email_5_body = """<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Hey {{params.first_name}}! &#128203;
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Cohort 1 is currently full, but we've added you to our
  <strong style="color:#f9fafb;">priority waitlist</strong>.
  You're <strong style="color:#2de2dc;">&#35;{{params.waitlist_number}}</strong> on the list.
</p>
<p style="margin:0 0 14px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  When a spot opens up &#8212; or when we open Cohort 2 &#8212; you'll be the first to know.
  We'll also give you priority access before we open registration to the public.
</p>
<p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.7;color:#d1d5db;">
  Keep an eye on your inbox. We'll be in touch. &#128075;<br />
  <span style="color:#9ca3af;">&#8212; Trevor &amp; the K2M team</span>
</p>"""

    # ── Assemble TemplateSpec list ───────────────────────────────────────────
    return [
        TemplateSpec(
            key="email_1",
            env_var="BREVO_TEMPLATE_EMAIL_1",
            name="K2M Cohort 1 - Email #1 Discord Invite",
            subject="Your spot in the AI Confidence Cohort is waiting \U0001f680",
            html_content=html_shell(
                step_badge="Step 2 of 4",
                title="Welcome to the",
                title_accent="AI Confidence Cohort",
                subtitle="COHORT 1 \u00b7 MARCH 2026",
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
            subject="We're holding your spot \u2014 join Discord to continue (Step 2 of 4)",
            html_content=html_shell(
                step_badge="Step 2 of 4",
                title="We're Holding Your",
                title_accent="Spot for You",
                subtitle="STEP 2 OF 4",
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
            subject="Last chance \u2014 your Discord invite expires soon (Step 2 of 4)",
            html_content=html_shell(
                step_badge="Step 2 of 4",
                title="Your Invite",
                title_accent="Expires Soon",
                subtitle="STEP 2 OF 4 \u00b7 FINAL REMINDER",
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
            subject="One step left \u2014 complete your payment to lock in your spot (Step 3 of 4)",
            html_content=html_shell(
                step_badge="Step 3 of 4",
                title="One Step Away",
                title_accent="From Your Cohort",
                subtitle="STEP 3 OF 4",
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
            subject="Payment received \u2014 verification in progress (Step 4 of 4)",
            html_content=html_shell(
                step_badge="Step 4 of 4",
                title="Payment",
                title_accent="Received \u2713",
                subtitle="STEP 4 OF 4",
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
            subject="You're in \u2014 Welcome to Cohort 1! \U0001f389",
            html_content=html_shell(
                step_badge="Step 4 complete",
                title="Welcome to",
                title_accent="Cohort 1",
                subtitle="YOU\u2019RE OFFICIALLY IN",
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
            subject="You're on the priority list \u2014 we'll notify you first",
            html_content=html_shell(
                step_badge="Waitlist",
                title="You're on the",
                title_accent="Priority List",
                subtitle="COHORT 1 WAITLIST",
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
