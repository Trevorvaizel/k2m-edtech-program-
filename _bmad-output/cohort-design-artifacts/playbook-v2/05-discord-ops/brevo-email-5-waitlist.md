# Brevo Email #5: Waitlist Notification

**Purpose:** Warm waitlist email when enrollment cap (30 students) is reached
**Trigger:** `/api/interest` endpoint detects ≥30 paid enrollments
**Tone:** Warm, priority positioning, not "rejected"
**Brand:** K2M dark theme + cyan accent (from email_templates.py aesthetic)

---

## Email Template

**Subject:** You're on our priority list! 🌟

**HTML Body:**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>You're on our priority list!</title>
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
</head>
<body>
    <div class="outer">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr>
                <td align="center">
                    <div class="card">
                        <div class="inner">
                            <!-- Logo (SVG from email_templates.py) -->
                            <div style="text-align:center;">
                                <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-label="K2M Logo" role="img" width="88" height="88" style="display:block;margin:0 auto;">
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
                            </div>

                            <div class="divider"></div>

                            <p class="kicker">Great news!</p>
                            <h1 class="title">You're on our <span class="title-accent">priority list</span> 🌟</h1>
                            <p class="subdate">{{first_name}}, we've saved your spot</p>

                            <p class="copy">Hey {{first_name}},</p>

                            <p class="copy">
                                This cohort filled up faster than expected — you're <strong>#{{waitlist_number}}</strong> on our priority list for the next cohort.
                            </p>

                            <p class="copy">
                                We cap each cohort at 30 students to ensure the best experience for everyone. Your spot is secured, and you'll be the <strong>first to know</strong> when we open enrollment for the next cohort.
                            </p>

                            <div class="panel">
                                <p><strong>What happens next:</strong></p>
                                <p>1. We'll email you 48 hours before the next cohort opens</p>
                                <p>2. You'll get priority access to enroll (no waiting this time!)</p>
                                <p>3. You'll still get the early-bird pricing if you enroll within 7 days</p>
                            </div>

                            <p class="copy">
                                In the meantime, here's a preview of what you'll experience:
                            </p>

                            <p class="copy">
                                <a href="{{artifact_showcase_url}}" style="color: #13d7d0;">See Week 8 artifacts from past students →</a>
                            </p>

                            <p class="copy">
                                These show the kind of thinking transformation our students achieve in 8 weeks. This could be you!
                            </p>

                            <div class="cta-wrap">
                                <a class="cta-btn" href="{{landing_page_url}}">Explore the Program</a>
                            </div>

                            <p class="copy">
                                Questions? Just reply to this email. I read every message personally.
                            </p>

                            <div class="footer">
                                <p>Nairobi, Kenya</p>
                                <p>You're receiving this because you submitted an interest form for K2M's AI Thinking Skills Cohort.</p>
                                <p class="meta">&copy; {{current_year}} K2M Labs. All rights reserved.</p>
                                <p><a href="{{unsubscribe_url}}">Unsubscribe from waitlist updates</a></p>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
```

---

## Template Variables (Brevo Template Parameters)

| Variable | Example Value | Source |
|----------|---------------|--------|
| `{{first_name}}` | "Trevor" | Google Sheets Column C |
| `{{waitlist_number}}` | "31" | Computed: Count of waitlisted students before this one |
| `{{artifact_showcase_url}}` | "https://k2m-edtech.program/showcase" | Landing page URL |
| `{{landing_page_url}}` | "https://k2m-edtech.program" | Landing page URL |
| `{{current_year}}` | "2026" | Current year |
| `{{unsubscribe_url}}` | Brevo unsubscribe link | Brevo system |

---

## Brevo Setup Instructions

1. **Create Template in Brevo:**
   - Login to Brevo
   - Go to "Campaigns" → "Email Templates" → "Create Template"
   - Name: "Email #5 - Waitlist Notification"
   - Copy-paste the HTML above
   - Add template variables: `{{first_name}}`, `{{waitlist_number}}`, `{{artifact_showcase_url}}`, `{{landing_page_url}}`, `{{current_year}}`, `{{unsubscribe_url}}`

2. **Store Template ID:**
   - After creating, note the Template ID (e.g., 123)
   - Add to Railway env: `BREVO_TEMPLATE_EMAIL_5=123`

3. **Test Send:**
   - Send test email to verify rendering
   - Check dark theme, cyan accent, mobile responsiveness

---

## Implementation Notes

**Used in:** `/api/interest` endpoint when `paid_count >= 30`

**Pseudo-code:**
```python
if paid_count >= ENROLLMENT_CAP:
    waitlist_number = paid_count - ENROLLMENT_CAP + 1
    send_brevo_email(
        template_id=BREVO_TEMPLATE_EMAIL_5,
        to=email,
        params={
            "first_name": first_name,
            "waitlist_number": waitlist_number,
            "artifact_showcase_url": "https://k2m-edtech.program/showcase",
            "landing_page_url": "https://k2m-edtech.program",
            "current_year": datetime.now().year,
        }
    )
    return {"success": True, "waitlisted": True}
```

---

**Status:** ✅ Template created - Ready for Brevo setup