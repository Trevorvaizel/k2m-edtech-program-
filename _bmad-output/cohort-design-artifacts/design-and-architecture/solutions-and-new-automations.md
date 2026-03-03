# K2M Cohort 1 — Solutions & New Automations
## Design Proposals + Implementation Specs

**Date:** 2026-02-20
**Session:** Dev Agent (Amelia) + PM (Priya) + Architect (Kai) + CIS Council
**Companion doc:** `pre-launch-gaps-and-solutions.md` (the gaps)
**Purpose:** Full design specs for every new automation and solution decided in session.
           Detailed enough for immediate implementation.

---

## SOLUTION 1: Student Signup Journey Automation

### Overview
Replace manual Discord invite distribution with a zero-touch automated pipeline.
The ONLY manual step is Trevor clicking "Confirmed" in Google Sheets after
verifying the M-Pesa payment code.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STUDENT JOURNEY                          │
│                                                             │
│  Landing Page CTA                                           │
│       ↓                                                     │
│  Google Form (diagnostic + M-Pesa code)                     │
│       ↓ auto-sync                                           │
│  Google Sheets (Student Roster)                             │
│       ↓ Apps Script trigger                                 │
│  Brevo API → Email #1 "Spot Reserved" (M-Pesa instructions) │
│       ↓                                                     │
│  [MANUAL: Trevor marks "Confirmed" in Column AD]            │
│       ↓ Apps Script detects change                          │
│  Brevo API → Email #2 "You're IN" (Discord invite)          │
│       ↓                                                     │
│  Student joins Discord                                      │
│       ↓ on_member_join fires                                │
│  KIRA upgraded welcome DM                                   │
│       ↓                                                     │
│  Apps Script scheduled (Sunday night before Week 1)         │
│  Brevo API → Email #3 "Week 1 Starts Tomorrow"              │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack
- **Automation engine:** Google Apps Script (free, lives inside Google Sheets)
- **Email delivery:** Brevo (free tier: 300 emails/day, custom domain from)
- **Data source:** Google Sheets (Student Roster, auto-populated from Form)
- **Cost:** $0

### Google Sheets Changes Required

Add to Student Roster sheet (after existing columns):

```
Column AC: M-Pesa Confirmation Code
  Source: Auto-populated from Google Form response
  Type: Short text
  Purpose: Trevor manually verifies this matches M-Pesa records

Column AD: Payment Status
  Source: Trevor manual dropdown
  Type: Data validation dropdown
  Options: Pending | Confirmed | Failed | Refunded
  Default: Pending
  Purpose: TRIGGER for Apps Script automation
```

### Apps Script — Full Implementation Spec

**Script location:** Google Sheets → Extensions → Apps Script

**Trigger 1: On Form Submit**
```javascript
// Fires when student submits the diagnostic form
function onFormSubmit(e) {
  const row = e.range.getRow();
  const sheet = SpreadsheetApp.getActiveSheet();

  // Read student data
  const firstName = sheet.getRange(row, 3).getValue();  // Col C
  const lastName  = sheet.getRange(row, 4).getValue();  // Col D
  const email     = sheet.getRange(row, 5).getValue();  // Col E
  const mpesaCode = sheet.getRange(row, 29).getValue(); // Col AC

  // Send Email #1 via Brevo API
  sendBrevoEmail({
    to: email,
    template_id: 1,  // "Spot Reserved" template in Brevo
    params: {
      firstName: firstName,
      lastName: lastName,
      mpesa_till: "[YOUR_TILL_NUMBER]",
      mpesa_amount: "[COHORT_FEE_KES]",
      mpesa_reference: firstName + lastName,
      mpesa_code_entered: mpesaCode
    }
  });

  // Set Payment Status to "Pending"
  sheet.getRange(row, 30).setValue("Pending"); // Col AD
}
```

**Trigger 2: On Edit (Payment Confirmation)**
```javascript
// Fires when Trevor edits any cell in the sheet
function onEdit(e) {
  const sheet = e.range.getSheet();
  const col   = e.range.getColumn();
  const row   = e.range.getRow();
  const value = e.value;

  // Only act when Column AD (Payment Status) changes to "Confirmed"
  if (col !== 30 || value !== "Confirmed") return;
  if (row < 2) return; // Skip header

  // Read student data
  const firstName     = sheet.getRange(row, 3).getValue();
  const email         = sheet.getRange(row, 5).getValue();
  const clusterName   = sheet.getRange(row, 26).getValue(); // Col Z (cluster)
  const sessionTime   = getSessionTime(clusterName);

  // Send Email #2 via Brevo API
  sendBrevoEmail({
    to: email,
    template_id: 2,  // "You're IN" template in Brevo
    params: {
      firstName: firstName,
      cluster: clusterName,
      session_time: sessionTime,
      discord_invite: "[YOUR_PERMANENT_DISCORD_INVITE]",
      week1_start_date: "[WEEK_1_DATE]"
    }
  });
}
```

**Trigger 3: Scheduled (Sunday night before Week 1)**
```javascript
// Set this up as a time-based trigger in Apps Script
function sendWeek1Preview() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const lastRow = sheet.getLastRow();

  for (let row = 2; row <= lastRow; row++) {
    const paymentStatus = sheet.getRange(row, 30).getValue();
    if (paymentStatus !== "Confirmed") continue;

    const firstName = sheet.getRange(row, 3).getValue();
    const email     = sheet.getRange(row, 5).getValue();

    sendBrevoEmail({
      to: email,
      template_id: 3,  // "Week 1 Starts Tomorrow" template
      params: {
        firstName: firstName,
        node_title: "AI is already around you — you just haven't noticed",
        prompt_time: "9:15 AM EAT",
        session_date: "[CLUSTER_SESSION_DATE]"
      }
    });
  }
}
```

**Brevo API helper:**
```javascript
function sendBrevoEmail(options) {
  const BREVO_API_KEY = PropertiesService.getScriptProperties()
                          .getProperty("BREVO_API_KEY");
  const url = "https://api.brevo.com/v3/smtp/email";

  const payload = {
    to: [{ email: options.to }],
    templateId: options.template_id,
    params: options.params
  };

  UrlFetchApp.fetch(url, {
    method: "POST",
    contentType: "application/json",
    headers: { "api-key": BREVO_API_KEY },
    payload: JSON.stringify(payload)
  });
}
```

### Brevo Setup (Trevor does this)

1. Create account at brevo.com (free)
2. Settings → Senders & IP → Add your custom domain
3. Add DNS records they give you to your domain registrar
4. Create 5 email templates (see Email Design section below)
5. Copy API key → paste into Apps Script Properties

### Email Template Designs

---

**EMAIL #1 — "Spot Reserved"**
```
FROM:    trevor@[yourdomain]
SUBJECT: Your K2M spot is reserved, {firstName} ✓

[K2M LOGO HEADER]

Hi {firstName},

Thanks for applying to K2M Cohort #1 — AI Thinking Skills.

Your spot is reserved. Here's how to complete your registration:

─────────────────────────────────
  STEP 1: Send your payment

  Amount:    KES {mpesa_amount}
  M-Pesa Till: {mpesa_till}  (K2M EdTech)
  Reference:  {mpesa_reference}

  You entered confirmation code: {mpesa_code_entered}
  Trevor will verify this within 24 hours.
─────────────────────────────────

  STEP 2: Wait for your confirmation email

  Once your payment is verified, you'll receive a second email
  with your Discord server invite and everything you need to
  get started.

─────────────────────────────────

Questions? Reply to this email or WhatsApp Trevor:
+254 [YOUR_NUMBER]

See you soon,
Trevor
K2M EdTech

[FOOTER: Unsubscribe | Privacy Policy]
```

---

**EMAIL #2 — "You're IN"**
```
FROM:    trevor@[yourdomain]
SUBJECT: Welcome to K2M Cohort #1, {firstName} 🎉

[K2M LOGO HEADER — celebratory version]

Hi {firstName},

Your payment is confirmed. You're officially in.

─────────────────────────────────
  JOIN THE DISCORD SERVER

  [BIG BUTTON: Join K2M Discord →]
  discord.gg/[your-invite]

  IMPORTANT: When you join, set your Discord display name
  to your FULL NAME (e.g., "John Kamau")
  This is how KIRA (your AI thinking partner) will know who you are.
─────────────────────────────────

  YOU'RE IN CLUSTER {cluster}
  Your live sessions: {session_time}

─────────────────────────────────

  WHAT HAPPENS NEXT

  • Week 1 starts: {week1_start_date}
  • KIRA will DM you when you join Discord
  • Monday 9:00 AM EAT — your first podcast node drops
  • Monday 9:15 AM EAT — your first daily prompt posts

─────────────────────────────────

  YOUR FIRST STEP (takes 2 minutes)

  After joining Discord, go to #thinking-lab and type:
  /frame I want to [your goal for this cohort]

  KIRA responds in a private DM. Nobody else sees it.
  That's your start.

─────────────────────────────────

See you Monday,
Trevor
K2M EdTech

P.S. You'll learn 4 thinking habits over 8 weeks:
⏸️ Pause  🎯 Context  🔄 Iterate  🧠 Think First
By Week 8, you'll have proof you use all of them.

[FOOTER]
```

---

**EMAIL #3 — "Week 1 Starts Tomorrow"**
```
FROM:    trevor@[yourdomain]
SUBJECT: Tomorrow is Day 1, {firstName} — here's what to expect

[K2M HEADER]

Hi {firstName},

Week 1 starts tomorrow. Here's exactly what will happen:

─────────────────────────────────
  MONDAY MORNING

  9:00 AM EAT
  KIRA posts your first NotebookLM podcast in your week channel.
  Topic: "{node_title}"
  Listen before the prompt drops (15-20 min).

  9:15 AM EAT
  KIRA posts your daily practice prompt.
  One question. No right answers. Just notice.

─────────────────────────────────

  YOUR CLUSTER SESSION
  {session_date} at 6:00 PM EAT
  I'll be there live. Bring questions.

─────────────────────────────────

  ONE THING TO DO BEFORE TOMORROW

  Go to #thinking-lab in Discord.
  Type: /frame I want to...
  [BUTTON: Open Discord →]

─────────────────────────────────

It's okay if you feel unsure about this. Most students do.
Week 1 is just about noticing. You can't do it wrong.

See you tomorrow,
Trevor

[FOOTER]
```

---

**EMAIL #4 — "End of Week 1"**
```
FROM:    trevor@[yourdomain]
SUBJECT: You made it through Week 1, {firstName}

[K2M HEADER]

Hi {firstName},

Week 1 is done. You showed up. That matters.

This week was about one thing: noticing AI is already in your life.
That noticing IS the skill. You've started building it.

─────────────────────────────────

  THIS WEEK'S REFLECTION

  Friday prompt is live in your Discord channel.
  Your response unlocks Week 2.
  Takes 5 minutes.

  [BUTTON: Go to Discord →]

─────────────────────────────────

  WHAT'S COMING IN WEEK 2

  Week 2 is about trust — learning to give AI enough context
  to actually help you. Habit 2: 🎯 Explain Context First.

─────────────────────────────────

One week in. Seven to go.

Trevor

[FOOTER]
```

---

**EMAIL #5 — "Artifact Published" (to parent if consent given)**
```
FROM:    trevor@[yourdomain]
SUBJECT: {firstName} just published their AI Thinking Artifact 🌟

[K2M HEADER — celebratory]

Hi {parentName},

{firstName} has completed the K2M Cohort #1 program and published
their AI Thinking Artifact.

This artifact represents 8 weeks of structured thinking practice —
a permanent record of how {firstName} learned to think alongside AI.

─────────────────────────────────

  [BUTTON: View {firstName}'s Artifact →]

─────────────────────────────────

What you're seeing is real. {firstName} wrote every word.
The artifact shows:
  ⏸️ Pausing before jumping to conclusions
  🎯 Explaining context to get better results
  🔄 Iterating until something works
  🧠 Using AI to think through decisions

These aren't AI skills. These are thinking skills.
They apply everywhere.

─────────────────────────────────

Congratulations to {firstName} — and to you.

Trevor
K2M EdTech

[FOOTER]
```

---

## SOLUTION 2: Upgraded KIRA Welcome DM

### Current (main.py:804) — Replace With:

```python
async def build_welcome_message(member, cluster_id, schedule_text):
    """
    Upgraded welcome DM — map + one clear first action.
    Pulls first name from display_name for warmth.
    """
    first_name = member.display_name.split()[0] if member.display_name else "there"

    cluster_names = {
        1: "A-F", 2: "G-L", 3: "M-R", 4: "S-Z",
        5: "A-F (overflow)", 6: "G-L (overflow)",
        7: "M-R (overflow)", 8: "S-Z (overflow)"
    }

    return f"""Hey {first_name}! I'm KIRA — your thinking partner for the next 8 weeks.

You're in **Cluster {cluster_id}** (Last names: {cluster_names.get(cluster_id, 'Unknown')})
📅 Your live sessions: **{schedule_text}**

━━━━━━━━━━━━━━━━━━━━━━━━
📍 **YOUR MAP — 5 channels, that's all you need:**

  `#week-1-wonder`       → Post here daily. Your main feed.
  `#thinking-lab`        → Think WITH me in private. Use `/frame` here.
  `#thinking-showcase`   → Where finished thinking gets celebrated.
  `#resources`           → Guides, examples, everything you need.
  `#welcome`             → If you ever feel lost, start here.

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 **YOUR FIRST STEP (takes 2 minutes):**

Go to `#thinking-lab` and type:
> `/frame I want to [your goal for this cohort]`

I'll respond in a private DM — nobody else sees it.
That's it. You've started.

━━━━━━━━━━━━━━━━━━━━━━━━
💡 **Not sure what to type?** Try:
> `/frame I want to stop feeling behind with AI`
> `/frame I want to use AI for my university applications`
> `/frame I'm not sure what I want but I'm here`

Any of those works. I'll take it from there.

— KIRA (K2M Interactive Reasoning Agent)"""
```

### Also Add: /register Command

```python
@bot.tree.command(
    name="register",
    description="Set your last name so KIRA can assign you to the right cluster"
)
@app_commands.describe(last_name="Your real last name (e.g. Kamau)")
async def register(interaction: discord.Interaction, last_name: str):
    """
    Student types /register last_name:Kamau
    Bot updates SQLite + reassigns cluster role.
    """
    store = StudentStateStore()
    discord_id = str(interaction.user.id)

    # Update last name and recalculate cluster
    new_cluster_id = store.assign_cluster_by_last_name(last_name)
    old_student = store.get_student(discord_id)
    old_cluster_id = old_student["cluster_id"] if old_student else None

    # Update database
    store.update_student_last_name(discord_id, last_name, new_cluster_id)

    # Update Discord roles
    member = interaction.guild.get_member(interaction.user.id)
    if member and old_cluster_id != new_cluster_id:
        # Remove old cluster role
        old_role = discord.utils.get(
            interaction.guild.roles, name=f"Cluster-{old_cluster_id}"
        )
        if old_role:
            await member.remove_roles(old_role)

        # Add new cluster role
        new_role = discord.utils.get(
            interaction.guild.roles, name=f"Cluster-{new_cluster_id}"
        )
        if new_role:
            await member.add_roles(new_role)

    cluster_schedule = {
        1: "Monday + Wednesday 6 PM EAT",
        2: "Monday + Thursday 6 PM EAT",
        3: "Tuesday + Wednesday 6 PM EAT",
        4: "Tuesday + Thursday 6 PM EAT",
    }

    await interaction.response.send_message(
        f"Got it! Registered as **{last_name}** → "
        f"**Cluster {new_cluster_id}** "
        f"({cluster_schedule.get(new_cluster_id, 'schedule TBD')})\n"
        f"Your cluster role has been updated. See you in the live sessions!",
        ephemeral=True  # Only visible to the student
    )
```

---

## SOLUTION 3: KIRA Contextual Coaching — 7 Proactive Journey DMs

### Design Pattern (same for all 7)
```
TRIGGER event fires
  → Check: has student already received this DM? (prevent duplicates)
  → KIRA DMs student
  → 3 elements: Context | What to do now | What's coming next
  → One clear action
  → Log juncture_dm_sent event to observability_events
```

### New observability_events types needed:
```
"juncture_dm_sent"    — metadata: {juncture: "post_first_frame", week: 1}
"first_frame_complete" — metadata: {agent: "framer", week: 1}
"first_showcase_share" — metadata: {week: 2}
```

---

### Juncture DM #1: Post-First /frame

**Trigger:** Student completes their first /frame session (state transitions to "complete")
**Where to hook:** `cis_controller/state_machine.py` — on state → "complete" transition,
                   check if it's the student's first ever completion.

```python
POST_FIRST_FRAME_DM = """
⏸️ **That was Habit 1 in action.**

You just paused, framed a question, and thought it through.
Most people never do that. You just did.

Here's what happened in that conversation:
→ You identified what you actually wanted to think about
→ You let AI help you see it more clearly
→ You kept control of where the thinking went

**This is /frame.** Use it whenever your head feels fuzzy
about something — a decision, a question, a feeling you
can't quite name.

━━━━━━━━━━━━━━━━━━
**What's next:**
The daily prompt is in `#{week_channel}`.
Post your observation for today — anything you noticed
about AI in your life. One sentence is enough.

— KIRA
"""
```

---

### Juncture DM #2: Post-First Showcase Share

**Trigger:** Student shares to #thinking-showcase for the first time
**Where to hook:** `commands/showcase.py` — after successful publish

```python
POST_FIRST_SHARE_DM = """
🌟 **Your thinking is now visible.**

You just shared something you worked out privately — publicly.
That takes courage. And it helps everyone who reads it.

In `#thinking-showcase`, your post is now a reference point
for other students. Someone will read it and think:
*"Oh, that's what this week is about."*

━━━━━━━━━━━━━━━━━━
**What's next:**
Keep doing what you're doing. The artifact at Week 8
is built from moments exactly like this one.

Every /frame conversation you have is raw material.
Every post you share is proof.

— KIRA
"""
```

---

### Juncture DM #3: Week N Context DM (Weeks 2-8)

**Trigger:** Saturday unlock fires for the student (they completed Friday reflection)
**Where to hook:** `cis_controller/state_machine.py` — after week unlock

```python
WEEK_CONTEXT_DMS = {
    2: {
        "theme": "Trust",
        "habit": "🎯 Context",
        "one_thing": "Give AI your full situation before asking anything.",
        "watch_for": "Notice when AI gives a generic answer — it's because you didn't give context yet."
    },
    3: {
        "theme": "Trust (deepening)",
        "habit": "🎯 Context",
        "one_thing": "Try giving MORE context than feels necessary. See what happens.",
        "watch_for": "The moment AI says something that surprises you — that's the habit working."
    },
    4: {
        "theme": "Converse",
        "habit": "🔄 Iterate",
        "one_thing": "Two new thinking partners unlocked: /diverge and /challenge.",
        "watch_for": "When you feel stuck on one idea — that's when /diverge helps."
    },
    5: {
        "theme": "Converse (deepening)",
        "habit": "🔄 Iterate",
        "one_thing": "Use /challenge to stress-test your best idea.",
        "watch_for": "The moment a challenge makes your idea stronger, not weaker."
    },
    6: {
        "theme": "Direct",
        "habit": "🧠 Think First",
        "one_thing": "/synthesize and /create-artifact are now unlocked.",
        "watch_for": "This week: start pulling your thinking together. The artifact begins here."
    },
    7: {
        "theme": "Direct (deepening)",
        "habit": "🧠 Think First",
        "one_thing": "Your artifact has 6 sections. Aim to draft 2-3 this week.",
        "watch_for": "Sections where you think 'I actually know this' — that's your Zone 3 emerging."
    },
    8: {
        "theme": "Showcase",
        "habit": "All 4 habits",
        "one_thing": "This week: finish, polish, and publish.",
        "watch_for": "The moment you read your artifact and think 'I wrote this' — that's the identity shift."
    }
}

def build_week_context_dm(week_number: int, first_name: str) -> str:
    ctx = WEEK_CONTEXT_DMS.get(week_number)
    if not ctx:
        return None

    return f"""Hey {first_name} — **Week {week_number} is open.**

━━━━━━━━━━━━━━━━━━
**This week's theme:** {ctx['theme']}
**Habit focus:** {ctx['habit']}

**One thing to try:**
{ctx['one_thing']}

**One thing to watch for:**
{ctx['watch_for']}

━━━━━━━━━━━━━━━━━━
The week channel is now open. See you in there.

— KIRA"""
```

---

### Juncture DM #4: Agent Unlock — Week 4 (/diverge + /challenge)

**Trigger:** Week 4 unlock fires
**Where to hook:** `cis_controller/state_machine.py` — week 4 specifically

```python
WEEK_4_AGENT_UNLOCK_DM = """
🔓 **Two new thinking partners just unlocked.**

━━━━━━━━━━━━━━━━━━
**/diverge** — The Explorer
  *Use when:* You feel stuck on one way of thinking.
  *What it does:* Opens up possibilities without judgment.
  *How to start:* `/diverge` in `#thinking-lab`

**/challenge** — The Challenger
  *Use when:* You have an idea and want to know if it's solid.
  *What it does:* Stress-tests your thinking with questions.
  *How to start:* `/challenge` in `#thinking-lab`

━━━━━━━━━━━━━━━━━━
**Which one first?**

If you've been thinking about one thing a lot this week
→ use **/challenge** (test if your thinking holds up)

If you feel stuck or want fresh angles
→ use **/diverge** (see what else is possible)

Both are waiting in `#thinking-lab`.

— KIRA
"""
```

---

### Juncture DM #5: Agent Unlock — Week 6 (/synthesize + /create-artifact)

**Trigger:** Week 6 unlock fires

```python
WEEK_6_AGENT_UNLOCK_DM = """
🔓 **Your final two agents are unlocked. This is where it gets real.**

━━━━━━━━━━━━━━━━━━
**/synthesize** — The Synthesizer
  *Use when:* You want to pull scattered thinking into something clear.
  *What it does:* Helps you articulate what you've actually concluded.
  *How to start:* `/synthesize` in `#thinking-lab`

**/create-artifact** — Your Artifact Workspace
  *Use when:* You're ready to start building your Week 8 artifact.
  *What it does:* Opens a private 6-section workspace. Save and resume anytime.
  *How to start:* `/create-artifact` in `#thinking-lab`

━━━━━━━━━━━━━━━━━━
**What is the artifact?**

It's a written record of how your thinking changed over 8 weeks.
6 sections. Your voice. Your evidence. No template filling.

Here's what it looks like:
  1. The question I started with
  2. What I used to believe
  3. What I explored (with AI)
  4. What challenged me
  5. What I now conclude
  6. How my thinking changed

You have 2 weeks. Start this week with sections 1-2.

— KIRA
"""
```

---

### Juncture DM #6: Artifact Creation Started

**Trigger:** Student uses /create-artifact for the first time
**Where to hook:** `commands/artifact.py` — first invocation check

```python
ARTIFACT_STARTED_DM = """
📝 **Your artifact workspace is open.**

You're building something permanent. Here's how to approach each section:

━━━━━━━━━━━━━━━━━━
**Section 1 — The Question I Started With**
What brought you to this cohort? What did you want to figure out?
*Don't overthink it. A sentence or two is enough.*

**Section 2 — What I Used to Believe**
Before Week 1, what was your honest take on AI?
*"AI was not for me" is a valid answer. So is "I thought AI would replace me."*

**Section 3 — What I Explored**
Pick 2-3 /frame or /diverge conversations that stuck with you.
*Use /synthesize to pull these together if they feel scattered.*

**Section 4 — What Challenged Me**
What made you rethink something you thought you knew?
*Could be a prompt, a conversation, a session moment.*

**Section 5 — What I Now Conclude**
What do you actually think now? Not what you're supposed to think.
*This is your voice. KIRA can't write this for you.*

**Section 6 — How My Thinking Changed**
One before/after. How did your relationship with AI shift?
*The more specific, the more powerful.*

━━━━━━━━━━━━━━━━━━
Type anything in your DM workspace to begin Section 1.
I'll be here the whole way through.

— KIRA
"""
```

---

### Juncture DM #7: Post-Artifact Publication (Graduation)

**Trigger:** Student successfully publishes artifact via /publish
**Where to hook:** `commands/showcase.py` — after publish_artifact_to_showcase completes

```python
GRADUATION_DM = """
🎓 **Your artifact is published. Your thinking is permanent.**

━━━━━━━━━━━━━━━━━━
Eight weeks ago, you joined a server you didn't fully understand,
used a command you'd never heard of, and wrote about something
you weren't sure you could articulate.

And now it's there. Public. Yours.

**What you built:**
✅ 4 thinking habits you can use anywhere
✅ A written record of your identity shift
✅ Proof — for yourself, your parents, your future

━━━━━━━━━━━━━━━━━━
**What's next?**

Your artifact lives at `#thinking-showcase` permanently.
Share the link anywhere you want.

If you want to use this as evidence for university applications,
interviews, or personal statements — it's yours. Cite it.

━━━━━━━━━━━━━━━━━━
It was a privilege to think alongside you.

— KIRA
"""
```

---

## SOLUTION 4: Pre-Cohort Content Scaffolds

### CIS Agent Guide — Structure for Trevor to Fill

Trevor creates this as a Notion page and links from #resources.

```markdown
# How to Think With KIRA — Your Agent Guide

## The 4 Agents

### /frame — The Framer (Available Week 1)
**Use when:** You have a fuzzy thought, question, or decision in your head.
**What it does:** Helps you slow down and articulate what you actually want to think about.
**Habit:** ⏸️ Pause

Example conversation:
  You: /frame
  KIRA: "What's on your mind? Start with: 'I want to think about...'"
  You: "I want to think about whether I should switch from Science to Commerce"
  KIRA: [scaffolds the thinking — asks what you already know, what's pulling you each way]
  ...5 turns later...
  You: Clearer on what's actually driving the decision

### /diverge — The Explorer (Available Week 4)
**Use when:** You feel stuck on one way of looking at something.
**What it does:** Opens up 3-5 different angles you haven't considered.
**Habit:** 🔄 Iterate

Example conversation:
  You: /diverge
  KIRA: "What's the situation you're stuck on?"
  You: "I keep thinking the only way to use AI is for writing essays"
  KIRA: [offers 5 completely different use cases relevant to student life]

### /challenge — The Challenger (Available Week 4)
**Use when:** You have an idea and want to know if it's solid.
**What it does:** Asks hard questions about your assumptions. Not to break you — to strengthen your thinking.
**Habit:** 🧠 Think First

### /synthesize — The Synthesizer (Available Week 6)
**Use when:** You've been thinking about something for a while and want to pull it together.
**What it does:** Helps you articulate a clear conclusion from scattered thinking.
**Habit:** 🧠 Think First

---

## Which Agent When?

| Situation | Use |
|-----------|-----|
| Head feels fuzzy, not sure what to think | /frame |
| Stuck on one perspective, want new angles | /diverge |
| Have an idea, want to test it | /challenge |
| Have been thinking a lot, want clarity | /synthesize |
| Ready to document your thinking | /create-artifact |
```

---

### Example Artifact A — "Developing" Quality

Trevor posts to #thinking-showcase before cohort opens.
Label: `📌 Example from our pilot — what a developing artifact looks like`

```
THE QUESTION I STARTED WITH:
I came in wondering if AI was actually useful for someone like me,
or if it was only for tech people.

WHAT I USED TO BELIEVE:
AI was for people who know how to code. I assumed I'd just type things in
and get bad answers back. I didn't think it would understand my situation.

WHAT I EXPLORED:
I used /frame to think through my university subject choices.
I didn't expect it to actually help — but it asked me questions I hadn't
thought to ask myself. Like: "What would you regret NOT studying?"

I also tried /diverge when I was stuck on whether to take a gap year.
It gave me 4 angles I hadn't considered, including one I didn't like
but knew was true.

WHAT CHALLENGED ME:
Week 4 prompt: "Find a decision you've been avoiding."
I realized I'd been avoiding thinking about what I actually want
vs. what I think I'm supposed to want. That was uncomfortable.

WHAT I NOW CONCLUDE:
AI is useful when you know what question to ask.
The hard part isn't the AI — it's clarifying the question.
That's what this cohort taught me.

HOW MY THINKING CHANGED:
Before: "AI gives me answers."
After: "AI helps me think better questions."

— Brian K. | Zone 1→2 | Week 8 Cohort Pilot
```

---

### Example Artifact B — "Strong" Quality

Label: `📌 Example from our pilot — what a strong artifact looks like`

```
THE QUESTION I STARTED WITH:
Should I pursue medicine because I want to, or because my parents want me to?
I couldn't tell the difference anymore.

WHAT I USED TO BELIEVE:
I thought AI would tell me what to do.
I opened my first /frame session expecting an answer.
Instead, KIRA asked: "What does choosing medicine feel like in your body?"
I didn't know how to answer that. But I started.

WHAT I EXPLORED:
Over 6 weeks I had 11 /frame sessions, 4 /diverge sessions,
and 2 /challenge sessions — all on variations of this one question.

The /challenge session in Week 5 was the hardest:
KIRA asked: "If your parents fully supported ANY choice,
what would you pick?" I sat with that for three days.

WHAT CHALLENGED ME:
Week 3, Node 2.1: "AI doesn't know what you want. Neither do you, yet."
That line broke something open. I had been asking AI to decide for me
instead of using it to help me think.

WHAT I NOW CONCLUDE:
I want medicine because I'm drawn to complexity and to people in crisis.
Those are my reasons — not my parents'.
The evidence: every time I /framed this question, I kept coming back to
specific moments in hospitals I'd visited. That's data.

HOW MY THINKING CHANGED:
Before: "I can't tell what I want vs. what they want."
After: "I can notice the difference now. It feels different in my body."

Habit I use most: ⏸️ Pause — before I ask anyone anything,
I ask myself first.

— Amina W. | Zone 2→3 | Week 8 Cohort Pilot
```

---

## Implementation Order (Priority Sequence)

```
WEEK 1 (Do immediately — no code):
  [ ] Trevor: Create Google Form (Story 5.4 spec)
  [ ] Trevor: Add M-Pesa field to form
  [ ] Trevor: Add Discord invite to form confirmation screen
  [ ] Trevor: Configure Discord Server Onboarding (native)
  [ ] Trevor: Post 2 example artifacts to #thinking-showcase
  [ ] Trevor: Set up Brevo account + custom domain

WEEK 2 (Quick code — 2 days):
  [ ] Amelia: Upgrade KIRA welcome DM
  [ ] Amelia: Add /register command
  [ ] Amelia: Apps Script + Brevo integration (Emails 1-3)
  [ ] Trevor: Write 5 email templates in Brevo

WEEK 3 (Full automation — 3 days):
  [ ] Amelia: All 7 KIRA juncture DMs
  [ ] Amelia: Task 4.6 (parent email system)
  [ ] Trevor: Write CIS Agent Guide (Notion)
  [ ] Trevor: Record Loom welcome video

LAUNCH GATE:
  [ ] All above + Sprint 5 remaining tasks (5.4, 5.5, 5.6, 5.7)
  [ ] Bot live on Railway
  [ ] Go/no-go decision
```

---

*Document created by Dev Agent (Amelia) — 2026-02-20*
*Companion to: `pre-launch-gaps-and-solutions.md`*
*These are the full design specs. Implementation follows on Trevor's approval.*
