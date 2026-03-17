# Facilitator Guide — Working with KIRA

> You don't need to watch every conversation. KIRA handles 90% autonomously. This guide tells you what KIRA escalates to you, what it looks like, and what to do.

---

## Your Role in the System

KIRA is designed to handle the majority of student interactions autonomously — daily prompts, agent responses, habit tracking, and routine escalations all run without your involvement. Your job is to:
1. Respond to escalations KIRA sends you
2. Monitor the #facilitator-dashboard channel
3. Manually advance students who need it
4. Intervene in crises (KIRA pages you immediately)

---

## The Escalation System — 4 Levels

KIRA monitors every student daily. When it detects a problem, it escalates through levels:

```
Level 1 (Yellow)  ──  1 day no post     ──  KIRA sends student a nudge DM
Level 2 (Orange)  ──  3+ days stuck     ──  Alert posted to #facilitator-dashboard
Level 3 (Red)     ──  7+ days stuck     ──  KIRA sends YOU a direct DM
Level 4 (Crisis)  ──  Crisis keywords   ──  KIRA pages you immediately + sends student resources
```

Level 2-4 escalations and safety events are logged to #moderation-logs.

### What triggers "stuck"?

KIRA looks at the student's last post date in `daily_participation`. If they've never posted, it uses their account creation date.

---

## Level 4 — Crisis Protocol

If a student sends a message containing any mental health crisis signal, KIRA:
1. Immediately sends the student crisis resources (Kenya hotline 119, Trevor's number)
2. Sends you a direct DM — **you are expected to reach out within 1 hour**

**Crisis keywords KIRA detects (examples):** "want to die", "suicidal", "self-harm", "hopeless", "worthless", "end it all", "kill myself"

> The crisis response is hardcoded and cannot be turned off. It is intentional.

---

## Intervention Playbook by Barrier Type

When KIRA escalates a student, it will tell you their **barrier type**. Here's the default intervention approach:

| Barrier | What to say |
|---------|------------|
| **Identity** ("I don't belong here") | "You belong in this room. Start with one real question from your day and run /frame." |
| **Time** ("I'm too busy") | "Use a 10-minute sprint: one /frame pass on the decision already in front of you." |
| **Relevance** ("This isn't useful to me") | "Pick one live work/school problem and test it with /diverge before deciding anything." |
| **Technical** ("I don't understand how to use this") | "Keep it simple: describe your situation in plain words and let KIRA handle the structure." |

**How does KIRA determine barrier type?**
Barrier type is inferred from enrollment and context data, including situation, goals, and emotional baseline passed through the Apps Script context engine. If that inference is missing or stale, use your own judgement based on what you know about the student.

---

## The Facilitator Dashboard

KIRA posts to **#facilitator-dashboard** with cohort-level stats. You can also run `/show-aggregate-patterns` to pull an aggregate report.

**What the dashboard shows (by design — Guardrail #3):**
- Total students / active students
- Agent usage counts
- Zone distribution across cohort
- Milestone celebrations

**What it deliberately does NOT show:**
- Individual student rankings or comparisons
- "Top student" or "most active" lists
- Any form of leaderboard

This is intentional. The programme is non-competitive.

---

## Manually Advancing a Student

If a student missed a reflection but should move to the next week, Trevor can manually advance them.

Use the admin command (in Discord, as facilitator):
```
/unlock-week @student week_number
```

This:
1. Updates the student's `current_week` in the database
2. Syncs their Discord channel permissions so they can access the correct week channel
3. Unlocks the appropriate agents for that week

---

## Viewing a Student's Journey

Students can consent to journey inspection for 24 hours. A student must say:
> `"i consent to journey inspection"`

After consent, Trevor can pull their full journey context. The consent expires after 24 hours and the student can revoke it at any time with:
> `"revoke journey inspection consent"`

This is **Guardrail #8** — student data is never surfaced without explicit consent.

Use the admin command after consent:
```
/inspect-journey @student
```

---

## Aggregate Patterns Command

```
/show-aggregate-patterns [days=7]
```

Returns cohort-level stats for the past N days. Safe to run at any time. Output is always aggregate — no individual student data.

---

## Student Has DMs Disabled

All KIRA communication happens via Discord DM — onboarding, agent responses, nudges, and crisis resources. If a student has DMs disabled (a common Discord privacy setting), KIRA cannot reach them.

**How to spot it:** A new member joined but never completed onboarding, and Railway logs show DM-delivery warnings or the student never reaches `onboarding_complete`.

**What to do:**
1. Reach out to the student directly in a public channel or via another channel
2. Ask them to enable DMs from server members (Discord Settings → Privacy & Safety → Allow direct messages from server members)
3. Once enabled, ask the student to run `/onboarding` in Discord so KIRA can restart the DM flow

> This is a known gap with no automated fix currently in place.

---

## Channel Structure Reference

Students are placed in week-specific channels as they advance:

| Weeks | Channel |
|-------|---------|
| Week 1 | `CHANNEL_WEEK_1` |
| Weeks 2–3 | `CHANNEL_WEEK_2_3` |
| Weeks 4–5 | `CHANNEL_WEEK_4_5` |
| Weeks 6–7 | `CHANNEL_WEEK_6_7` |
| Week 8 | `CHANNEL_WEEK_8` |

Channel IDs are set as environment variables (see [Super Admin Guide](./04-super-admin-ops.md)).
