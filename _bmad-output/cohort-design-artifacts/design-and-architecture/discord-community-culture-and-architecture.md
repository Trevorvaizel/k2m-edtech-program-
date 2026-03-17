# Discord Community Culture and Architecture
**K2M Cohort 1 — Mixed Profession Cross-Pollination Design**
**Produced by:** Party Mode Session (Victor + Sally + Maya + Carson + Dr. Quinn + Winston + Sophia)
**Date:** 2026-03-04
**Decision basis:** Strategic choice to build "K2M: Break Out of Your Professional Echo Chamber"
**Status:** DESIGN + EXECUTION SPEC (canonical community/channel contract; implementation tracked in sprint)

---

## TABLE OF CONTENTS

1. [STRATEGIC FOUNDATION](#1-strategic-foundation)
2. [CHANNEL ARCHITECTURE](#2-channel-architecture)
3. [PROGRESSIVE DISCLOSURE DESIGN](#3-progressive-disclosure-design)
4. [PERMISSION SYSTEM](#4-permission-system)
5. [COMMUNITY CULTURE DESIGN](#5-community-culture-design)
6. [THE WATERCOOLER: CROSS-POLLINATION ENGINE](#6-the-watercooler-cross-pollination-engine)
7. [FACILITATION PROTOCOLS](#7-facilitation-protocols)
8. [BOT AUTOMATION](#8-bot-automation)
9. [EXTENSIBILITY: NEW PROFESSIONS](#9-extensibility-new-professions)

---

## DOCUMENT CONTRACT (AUDIT + SOURCE OF TRUTH)

This document is the canonical behavior contract for:
- Channel architecture and progressive disclosure
- Permission model by role/week
- Community culture and facilitation norms

Execution and status tracking live in:
- `_bmad-output/cohort-design-artifacts/operations/sprint/discord-implementation-sprint.yaml`

Required companion reads for implementation:
- `_bmad-output/cohort-design-artifacts/design-and-architecture/student-onboarding-and-enrollment-flow.md`
- `_bmad-output/cohort-design-artifacts/design-and-architecture/context-engine-experience-design.md`
- `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/discord-architecture.md`

Conflict resolution order:
1. Enrollment flow doc for onboarding/payment gating
2. This document for channels/permissions/culture
3. Context engine doc for personalization logic
4. Sprint YAML for implementation status and sequencing

---

## 1. STRATEGIC FOUNDATION

### 1.1 The Strategic Choice

**Question:** Should K2M be "Thinking Skills for [Specific Profession]" or "Thinking Skills That Dissolve Professional Boundaries"?

**Decision:** **Option B — Mixed Cohorts**

**Why:**
- ✅ Anyone can copy "K2M for Teachers"
- ✅ NO ONE can copy "K2M: The First Program That Dissolves Professional Boundaries"
- ✅ Cross-pollination creates a defensible innovation moat
- ✅ Larger addressable market (100 students/cohort vs. 40 per profession)
- ✅ Lower CAC (one marketing campaign vs. profession-specific campaigns)

**Value Proposition:**
> "You're a teacher dealing with students who 'just don't get it.' You're an entrepreneur dealing with staff who 'just don't care.' You're a student dealing with group members who 'just don't contribute.'
>
> **Different context. Same thinking trap.**
>
> K2M is where you discover that your struggle isn't unique to your profession — it's universal. And the solution lives in cross-pollination, not silos."

---

### 1.2 The Mixing Promise

**80% Rule:**
- 80% of what students see will be profession-specific (their examples, their language, their world)
- 20% will be cross-profession exposure (the breakthrough zone)

**Why This Works:**
- The 80% builds TRUST ("this was built for me")
- The 20% creates BREAKTHROUGHS ("my patterns are universal")

**Example:**

```
Week 1-3: Mary (Teacher) sees only teacher-specific examples
→ Trust builds: "This program gets my world"

Week 4: Mary reads an artifact by a student stuck on research proposal
→ Student writes: "I kept writing introductions my supervisor rejected. I realized
                  I wasn't making an argument — just listing facts."

→ Mary thinks: "That's MY pattern. In lesson planning. In parent emails."

→ Breakthrough: "My patterns aren't unique to teaching. They're universal."
```

---

### 1.3 What Was Rejected

**❌ Rejected: Profession-Specific Cohorts**
- Why: Segregated servers for teachers, entrepreneurs, students
- Problem: No cross-pollination, competitive vulnerability, smaller market

**❌ Rejected: Affinity Spaces (Profession Corners)**
- Why: #teachers-corner, #entrepreneurs-lounge within mixed cohort
- Problem: Undermines cross-pollination strategy, creates "segregated mixing"
- Risk: Teachers retreat to corners, never engage in mixed spaces

**✅ Accepted: ONE Watercooler Model**
- Single social space (#the-watercooler) for ALL professions
- Cross-pollination happens ORGANICALLY, not in special channels
- Simple architecture, clean experience, true to strategy

---

## 2. CHANNEL ARCHITECTURE

### 2.1 Complete Channel List

| Category | Channels | Purpose | Unlock Timing |
|---|---|---|---|
| **Core** | #announcements | Admin updates (Trevor only posts) | Day 1 (@Guest can see) |
| | #info | FAQs, resources, policies | Day 1 (@Guest can see) |
| **Onboarding** | #welcome-and-onboarding | Orientation, house rules, tour guide | After payment |
| **Weekly Learning** | #week-1-wonder | Week 1 curriculum | Week 1 |
| | #week-2-clarity | Week 2 curriculum | Week 2 |
| | #week-3-focus | Week 3 curriculum | Week 3 |
| | #week-4-expand | Week 4 curriculum | Week 4 |
| | #week-5-synthesize | Week 5 curriculum | Week 5 |
| | #week-6-integrate | Week 6 curriculum | Week 6 |
| | #week-7-artifact | Week 7 curriculum | Week 7 |
| | #week-8-graduation | Week 8 curriculum | Week 8 |
| **CIS Tools** | #thinking-lab | AI thinking tools (/frame, /diverge, /challenge, /synthesize) | Week 4 |
| | #thinking-showcase | Public artifact sharing, cross-pollination zone | Week 4 |
| **Clusters** | #cluster-1 through #cluster-6 | Small group discussion, live session coordination | After placement |
| **Social** | #the-watercooler | ONE space for casual chat, venting, wins, cross-pollination | After payment |

**Total Channels: 19**
**Maximum Visible at Once (Week 8): 18 channels**
**Maximum Visible at Once (Week 1): 6 channels**

---

### 2.2 Channel Purposes

#### **#announcements**
- **Purpose:** Official program updates
- **Permissions:** @everyone can read, only Trevor can post
- **Typical content:** Schedule changes, important reminders, policy updates
- **Post frequency:** 2-3 times per week

#### **#info**
- **Purpose:** Static reference information
- **Permissions:** @everyone can read, Trevor can edit
- **Typical content:** FAQ, community guidelines, technical support links, schedule overview
- **Updates:** As needed (not a discussion channel)

#### **#welcome-and-onboarding**
- **Purpose:** New student orientation
- **Permissions:** @Student can read and post
- **Typical content:** Welcome messages, how-to guides, introductions
- **Active use:** Weeks 1-2 only (becomes read-only after Week 3)

#### **#week-N-[theme]**
- **Purpose:** Weekly curriculum channels
- **Permissions:** @Student role, unlocked progressively
- **Typical content:** Daily prompts, weekly challenge, discussion threads
- **Lifecycle:** Active for 1 week, then read-only archive

#### **#thinking-lab**
- **Purpose:** AI thinking tool interaction space
- **Permissions:** @Student role (Week 4+)
- **Commands:** `/frame`, `/diverge`, `/challenge`, `/synthesize`
- **Usage:** Private thinking sessions with KIRA

#### **#thinking-showcase**
- **Purpose:** Public artifact sharing
- **Permissions:** @Student role (Week 4+)
- **Purpose:** Share your thinking journey, discover patterns in others' work
- **Cross-pollination:** Primary zone for "that's my pattern too!" moments

#### **#cluster-1 through #cluster-6**
- **Purpose:** Small group discussion (40-50 students per cluster)
- **Permissions:** @Cluster-X role only
- **Activities:** Cluster-specific discussions, live session coordination, peer support
- **Why:** Smaller spaces create psychological safety within larger community

#### **#the-watercooler**
- **Purpose:** THE social space for EVERYONE
- **Permissions:** @Student role can read and post
- **Activities:** Casual chat, venting, celebration, resource sharing, advice-seeking, cross-pollination
- **Why it matters:** This is where cross-pollination HAPPENS (not in special channels)

---

### 2.3 Channel Descriptions (For Discord Setup)

```yaml
#announcements:
  description: "Official program updates and announcements from the K2M team"
  topic: "Check here 2-3x per week for important updates"

#info:
  description: "FAQs, community guidelines, schedules, and resources"
  topic: "Start here if you have questions about how the program works"

#welcome-and-onboarding:
  description: "New student orientation and introductions (Weeks 1-2)"
  topic: "Say hi, ask questions, get oriented!"

#the-watercooler:
  description: "Casual chat for everyone — teachers, entrepreneurs, students, professionals. Share wins, vent frustrations, ask for advice, discover you're not alone."
  topic: "How's your week? Small wins, big challenges, cross-profession conversations"

#thinking-lab:
  description: "AI-powered thinking tools. Use /frame, /diverge, /challenge, /synthesize to work through problems with KIRA."
  topic: "Private thinking space. Your sessions are 1-on-1 with KIRA."

#thinking-showcase:
  description: "Share your thinking journey with the cohort. Post artifacts, read others' work, discover patterns across professions."
  topic: "This is where cross-pollination happens. Read widely — you'll see your patterns in others' stories."
```

---

## 3. PROGRESSIVE DISCLOSURE DESIGN

### 3.1 The Principle

**Reveal, Don't Overwhelm**

New students see ONLY what they need NOW. New channels unlock as they progress.

**Why:**
- Reduces cognitive load (6 channels Day 1 vs. 19 all at once)
- Creates journey of discovery (new spaces = growth)
- Prevents "where do I start?" paralysis

---

### 3.2 Channel Visibility by Journey Stage

| Journey Stage | Channels Visible | Count | Experience |
|---|---|---|---|
| **@Guest (pre-payment)** | #announcements, #info | 2 | "Preview of what's coming" |
| **Day 1 (@Student)** | + #welcome-and-onboarding, #week-1-wonder, #the-watercooler, #[cluster-X] | 6 | "I can navigate this" |
| **Week 2** | + #week-2-clarity | 7 | "One week at a time" |
| **Week 3** | + #week-3-focus | 8 | "Growing with me" |
| **Week 4** | + #week-4-expand, #thinking-lab, #thinking-showcase | 11 | "New tools unlocked!" |
| **Week 5** | + #week-5-synthesize | 12 | "I'm in Week 5 now" |
| **Week 6** | + #week-6-integrate | 13 | "Advanced thinking" |
| **Week 7** | + #week-7-artifact | 14 | "Artifact creation" |
| **Week 8** | + #week-8-graduation | 15 | "Final stretch" |
| **Post-Graduation** | All channels remain accessible | 15 | "Alumni access for life" |

---

### 3.3 The Student Experience Over Time

**Week 1 (6 channels):**
```
Mary opens Discord:
📢 #announcements (1 🔴 unread)
📖 #info (read)
👋 #welcome-and-onboarding (completed ✅)
🎯 #week-1-wonder (5 🔴 unread)
💬 #the-watercooler (12 🔴 unread)
🏠 #cluster-1 (3 🔴 unread)

Mary thinks: "Okay, I know what to do. I'll check #week-1-wonder first."
```

**Week 4 (11 channels):**
```
Mary opens Discord:
📢 #announcements (read)
🎯 #week-1-wonder, #week-2-clarity, #week-3-focus, #week-4-expand (only week 4 has 🔴)
🧪 #thinking-lab (2 🔴 unread - someone mentioned her!)
🏆 #thinking-showcase (8 🔴 unread)
💬 #the-watercooler (read)
🏠 #cluster-1 (read)

Mary thinks: "I have my favorites now. I check #the-watercooler and #thinking-showcase
every day. The weekly channel for the daily prompt. The rest I browse when I have time."
```

---

## 4. PERMISSION SYSTEM

### 4.1 Discord Roles

| Role | Purpose | Permissions | Channels Visible |
|---|---|---|---|
| **@Guest** | Pre-payment access | Read-only #announcements, #info | 2 channels |
| **@Student** | Full program access | Read/post in all learning & social channels (unlocked progressively) | 6-15 channels depending on week |
| **@Cluster-X** | Cluster membership | Access to assigned cluster channel | +1 cluster channel |
| **@Facilitator** | Trevor, moderators | Full access, administrative privileges | All channels |

---

### 4.2 Permission Updates by Week

**Weekly Automation (via bot):**

```python
# Every Saturday at 9:00 AM EAT
@weekly_schedule(day="Saturday", time="09:00 EAT")
async def unlock_next_week():
    current_week = get_current_week()

    for student in students:
        if student.weeks_completed == current_week:
            # Grant permission to next week's channel
            discord.add_channel_permission(
                channel=f"week-{current_week+1}-{week_theme}",
                role="@Student",
                permission="VIEW_CHANNEL"
            )

            # Week 4: Unlock CIS tools
            if current_week == 3:
                discord.add_channel_permission("thinking-lab", "@Student", "VIEW_CHANNEL")
                discord.add_channel_permission("thinking-showcase", "@Student", "VIEW_CHANNEL")

                # Send DM notification
                await discord.send_dm(
                    student.discord_id,
                    f"🎉 Week 4 is here! Two new spaces unlocked:\n"
                    f"→ #thinking-lab (use /frame, /diverge, /challenge)\n"
                    f"→ #thinking-showcase (share your artifacts)\n\n"
                    f"These tools are where cross-pollination happens. You'll see patterns "
                    f"from teachers, entrepreneurs, and students. Some will feel familiar. "
                    f"That's not a coincidence. 💡"
                )
```

---

## 5. COMMUNITY CULTURE DESIGN

### 5.1 Community Norms

**Pinned in #welcome-and-onboarding:**

```
🤝 K2M Community Norms

1. **Assume Positive Intent** — Everyone here is learning. Ask questions before judging.

2. **Embrace Vulnerability** — Real growth happens when you share what's ACTUALLY hard,
   not what looks good.

3. **Cross-Profession Curiosity** — When someone from a different profession shares their
   challenge, ask: "How does this show up in my world?"

4. **Pattern Matching** — When you read an artifact and think "that's my pattern too,"
   SAY SO. Those moments are the point of this program.

5. **Constructive Disagreement** — It's okay to disagree. Do it with respect and curiosity,
   not dismissal.

6. **Celebrate Small Wins** — Did you pause before reacting? Frame a problem clearly?
   Share it. Small wins compound.

7. **Ask for Help** — Stuck? Overwhelmed? Not sure what to do? Ask in #the-watercooler or
   DM KIRA.

This community works because everyone contributes. Your voice matters.
```

---

### 5.2 Facilitation Approach

**KIRA's Role (via Bot):**

- **Welcome DMs:** Personalized onboarding (see context-engine-experience-design.md Section 6)
- **Weekly Reminders:** "Week 4 is here! New tools unlocked..."
- **Celebration:** "🎉 Mary just completed her first /frame session!"
- **Gentle Nudges:** "Haven't seen you in #week-3-focus this week. Everything okay?"
- **Cross-Pollination Highlights:** "🎯 PATTERN MATCH: Mary (teacher) and James (entrepreneur)
  both discovered they struggle with 'assuming instead of asking'"

**Trevor's Role (Human Facilitator):**

- **Model Vulnerability:** Share your own thinking challenges
- **Surface Patterns:** Point out cross-profession connections in #thinking-showcase
- **Host Live Sessions:** Cluster discussions, office hours
- **Intervene When Needed:** Address conflicts, redirect unproductive behavior
- **Celebrate Breakthroughs:** Highlight "aha moments" in #announcements

---

### 5.3 Safety Protocols

**When Someone Shares Something Vulnerable:**

```
[SAFE SPACE] Protocol (pinned in #the-watercooler):

When you share something sensitive, tag it [SAFE SPACE].

Example: "[SAFE SPACE] I'm struggling with a student who's failing, and I don't
know how to help them. I feel like I'm failing as a teacher."

Community Response Norm:
1. Validate first: "That sounds really hard. Thank you for sharing this."
2. Ask before advising: "Do you want empathy, or do you want suggestions?"
3. Share related experiences: "I felt something similar when..."
4. NO "just do X" advice unless they explicitly ask for it

This space only works if we hold space for each other's experiences.
```

---

## 6. THE WATERCOOLER: CROSS-POLLINATION ENGINE

### 6.1 Why One Space Is Enough

**The Principle:**

In a real office, cross-pollination doesn't happen in special "Collaboration Rooms." It happens in the **break room** — the ONE space where everyone from sales, marketing, engineering, and customer support bumps into each other.

**#the-watercooler IS that break room.**

---

### 6.2 What Happens in #the-watercooler

#### **Pattern 1: Shared Frustrations**

```
Teacher: "CBC documentation is overwhelming 😩"
Entrepreneur: "Same with county government permits"
Student: "Same with university bureaucracy"
→ Pattern: "Administrative overload" (universal challenge)
```

#### **Pattern 2: Shared Wins**

```
Entrepreneur: "I finally hired my first employee! 🎉"
Teacher: "I got my first student to pass Chemistry!"
Student: "I submitted my research proposal!"
→ Pattern: "First milestone celebration" (universal joy)
```

#### **Pattern 3: Shared Questions**

```
Teacher: "How do you deal with people who don't respond to messages?"
Entrepreneur: "I send M-Pesa reminders. What about you?"
Teacher: "I send handwritten notes to parents"
Student: "I tag them in WhatsApp groups"
→ Pattern: "Communication strategies across contexts" (cross-pollination)
```

#### **Pattern 4: Cross-Pollination Sparks**

```
Teacher: "I'm struggling with classroom management"
Entrepreneur: "What if you framed it like 'staff management'? Here's my system..."
Teacher: "Wait, that's BRILLIANT. Tell me more."
→ Innovation transfer: Business strategy applied to classroom
```

**ALL OF THIS happens organically in ONE space.**

---

### 6.3 #the-watercooler Description

**For Discord Channel Setup:**

```
Name: the-watercooler
Topic: Casual chat for everyone — teachers, entrepreneurs, students, professionals.
       Share wins, vent frustrations, ask for advice, discover you're not alone.
Description: This is where the magic happens. You'll meet people from different
             professions who are dealing with the SAME thinking patterns you are.
             Different contexts, same underlying struggles.

             What to share:
             • "How's everyone's week going?"
             • Small wins (paused before reacting! framed a problem!)
             • Frustrations (CBC stress, business pressure, exam anxiety)
             • Questions ("How do you deal with X?")
             • Resources (useful articles, tools, opportunities)

             What makes this work:
             • Assume positive intent
             • Embrace vulnerability
             • Be curious about other professions
             • Celebrate each other

             You're not alone. We're in this together.
```

---

### 6.4 Sample #the-watercooler Conversations

**Conversation A (Week 1):**

```
Mary (Teacher): "Hey everyone! Week 1 check-in — how's it going?"

James (Entrepreneur): "Overwhelmed but in a good way? The /frame tool already
helped me see I was solving the WRONG problem in my business."

Grace (Student): "Same! I used /frame on my research proposal and realized I
haven't actually defined my question yet."

Mary: "I feel seen. 😂 I've been running around like a headless chicken with
lesson planning. Used /frame yesterday and discovered I'm stressed because I'm
trying to do EVERYTHING instead of what matters."

James: "Wait. That's MY pattern too. I try to offer every product instead of
focusing on what sells."

Grace: "Can we all agree that Week 1 is about realizing we're all doing the
same overcommitment pattern just in different costumes? 😅"

→ Pattern match, humor, bonding
```

**Conversation B (Week 4):**

```
David (Working Professional): "I just had my mind BLOWN in #thinking-showcase.
Read an artifact by a teacher who was struggling with students 'not caring.'
She used /frame and discovered they were actually overwhelmed, not apathetic."

Mary (Teacher): "That was mine! 🙈"

David: "It hit me so hard. I have the SAME pattern with my team. I assume they
don't care about the project, but maybe they're overwhelmed by the scope."

Mary: "What did you do?"

David: "I asked them. Mary, your artifact gave me the courage to just ASK
instead of assume. Turns out... they ARE overwhelmed. We're adjusting the
timeline."

Grace (Student): "This is why I love this program. Mary's teaching struggle
became David's management breakthrough. We're all learning from each other."

→ Cross-pollination, application, celebration
```

---

## 7. FACILITATION PROTOCOLS

### 7.1 Weekly Facilitation Rhythm

**Monday (Week Start):**
- KIRA DM: "Week X is open! Check #week-X-[theme] for this week's prompt."
- #announcements: Week theme preview, special events, deadlines

**Wednesday (Mid-Week Check-In):**
- #announcements: "Mid-week nudge: Have you tried this week's /frame prompt?"
- #the-watercooler: KIRA posts conversation starter if it's quiet

**Friday (Week End):**
- #announcements: "Week X wraps up Sunday! Submit your artifacts to #thinking-showcase."
- #thinking-showcase: KIRA highlights 2-3 standout artifacts

**Saturday (Week Transition):**
- Bot automation: Unlock next week's channel
- Bot automation: Send DM notifications to all students

---

### 7.2 Intervention Triggers

**When KIRA Bot Intervenes:**

| Trigger | Action | Message |
|---|---|---|
| Student hasn't posted in 3+ days | DM nudge | "Haven't seen you in #week-X-[theme] this week. Everything okay?" |
| Student shares breakthrough in #thinking-showcase | Celebrate publicly | "🎉 [Name] just had a breakthrough! Read their artifact in #thinking-showcase" |
| Pattern match detected | Highlight | "🎯 PATTERN MATCH: [Teacher] and [Entrepreneur] both discovered they struggle with [pattern]" |
| Inappropriate behavior | DM warning | "Hey [Name], your post in [channel] violated our community norms. Please review the guidelines in #info." |
| Student asks for help | Route appropriately | "Great question! For technical issues, check #info. For thinking struggles, try /frame in #thinking-lab." |

---

### 7.3 Human Facilitator (Trevor) Responsibilities

**Daily (15 min):**
- Scan #thinking-showcase for standout artifacts (highlight in #announcements)
- Check #the-watercooler for flagging issues (intervene if needed)
- Respond to any @mentions or DMs

**Weekly (1 hour):**
- Review all artifacts posted to #thinking-showcase
- Identify cross-pollination moments to highlight
- Prepare for live sessions (if scheduled)

**Monthly (2 hours):**
- Review community health metrics (engagement, retention, satisfaction)
- Adjust facilitation approach based on data
- Plan special events or interventions

---

## 8. BOT AUTOMATION

### 8.1 Required Bot Commands

| Command | Channel | Purpose | Trigger |
|---|---|---|---|
| `/frame` | #thinking-lab | Personal framing session | Student types command |
| `/diverge` | #thinking-lab | Explore perspectives | Week 4+ |
| `/challenge` | #thinking-lab | Stress-test ideas | Week 4+ |
| `/synthesize` | #thinking-lab | Integrate learning | Week 6+ |
| `/create-artifact` | #thinking-lab | Start artifact creation | Week 6+ |
| `/myprofile` (planned) | Any DM | View your profile | Student types command |
| `/help` | Any | Get help links | Student types command |

---

### 8.2 Automated Workflows

**Workflow 1: Weekly Channel Unlock**
```python
# Every Saturday 9:00 AM EAT
@weekly_schedule(day="Saturday", time="09:00 EAT")
async def unlock_week_channel():
    current_week = get_current_week()

    # Grant @Student role permission to next week's channel
    discord.add_channel_permission(
        channel=f"week-{current_week+1}-{week_theme}",
        role="@Student",
        permission="VIEW_CHANNEL"
    )

    # DM all active students
    for student in students:
        if student.payment_status == "Confirmed":
            await discord.send_dm(
                student.discord_id,
                f"Week {current_week+1} is now open! 🎉\n"
                f"→ Check #{week-{current_week+1}-{week_theme}}\n"
                f"This week's focus: {week_theme_description}\n"
            )
```

**Workflow 2: Inactive Student Nudge**
```python
# Every Tuesday 10:00 AM EAT
@weekly_schedule(day="Tuesday", time="10:00 EAT")
async def nudge_inactive_students():
    for student in students:
        last_activity = get_last_activity_date(student.discord_id)

        if (datetime.now() - last_activity).days >= 3:
            await discord.send_dm(
                student.discord_id,
                f"Haven't seen you in #{get_current_week_channel()} this week. "
                f"Everything okay? Remember, even 5 minutes is enough. Just type /frame "
                f"in #thinking-lab and start where you are."
            )
```

**Workflow 3: Pattern Match Detection**
```python
# Daily scan of #thinking-showcase
@daily_schedule(time="16:00 EAT")
async def detect_pattern_matches():
    artifacts = get_artifacts_posted_last_24h()

    for artifact in artifacts:
        # Extract thinking patterns from artifact (via LLM)
        patterns = extract_thinking_patterns(artifact.content)

        # Find other students with same patterns
        matches = find_pattern_matches(patterns, artifact.profession)

        if len(matches) >= 2:
            # Post to #announcements
            discord.post_message(
                channel="#announcements",
                message=f"🎯 PATTERN MATCH DISCOVERED:\n\n"
                        f"{artifact.author} ({artifact.profession}) and "
                        f"{', '.join([m.author for m in matches])} "
                        f"all discovered they share the '{patterns[0]}' thinking pattern.\n\n"
                        f"Read their artifacts in #thinking-showcase to see how "
                        f"this shows up across different professions."
            )
```

---

## 9. EXTENSIBILITY: NEW PROFESSIONS

### 9.1 The Question

**"What if new professions emerge that we didn't anticipate? How do we add relevant examples for them without hard-coding everything?"**

---

### 9.2 Current Example Library Architecture

**What Exists:**

```python
# cis-discord-bot/database/example_library.db
CREATE TABLE profession_examples (
    id INTEGER PRIMARY KEY,
    profession TEXT,  -- 'teacher' | 'entrepreneur' | 'university_student' | 'working_professional' | 'gap_year_student' | 'other'
    example_text TEXT,
    week_relevant TEXT,  -- '1-2' | '3-4' | '5-6' | '7-8'
    habit_tag TEXT,  -- 'habit_1' | 'habit_2' | 'habit_3' | 'habit_4'
    created_at TIMESTAMP
);

# Current examples: 40 total (10 per profession × 4 base professions)
```

**How It Works:**

```python
# Context engine injection
student = get_student(discord_id)
profession = student.profession  # e.g., 'teacher'
week = get_current_week()

# Query RELEVANT examples
examples = db.query(
    "SELECT example_text FROM profession_examples "
    "WHERE profession = ? AND week_relevant LIKE ?",
    (profession, f"%{week}%")
)

# Inject into CIS agent prompt
context = {
    "profession_examples": random.choice(examples)
}
```

---

### 9.3 Adding New Professions: Three Approaches

#### **Approach A: Hard-Coded Examples (Current Method)**

**How:**
1. Trevor writes 10 new examples manually
2. Add to database: `INSERT INTO profession_examples VALUES (...)`
3. Deploy database update

**Pros:**
- ✅ Curated, high-quality examples
- ✅ Grounded in real Kenyan context
- ✅ Consistent with existing style

**Cons:**
- ❌ Time-consuming (1-2 hours per example set)
- ❌ Doesn't scale to 20+ professions
- ❌ Requires Trevor's domain expertise

**When to Use:** First 6 months, professions are well-known and stable

---

#### **Approach B: LLM-Generated Examples (Semi-Automated)**

**How:**
```python
# When new profession is added, generate examples via LLM
def generate_profession_examples(new_profession, existing_context):
    prompt = f"""
    You are generating thinking skill examples for K2M, a program serving Kenyan professionals.

    New profession: {new_profession}
    Context: {existing_context} (Kenyan ECONOMICS, CULTURE, DAILY LIFE)

    Generate 10 examples following this pattern:
    - Week 1-2 examples (Habit 1: Pause before acting)
    - Week 3-4 examples (Habit 2: Frame the right question)
    - Week 5-6 examples (Habit 3: Iterate, don't outsource)
    - Week 7-8 examples (Habit 4: Challenge assumptions)

    Each example should:
    1. Be grounded in Kenyan reality (M-Pesa, CBC curriculum, county gov, etc.)
    2. Show the BEFORE (old thinking) and AFTER (new thinking)
    3. Mention specific Kenyan contexts (cities, systems, challenges)
    4. Feel authentic to {new_profession}'s daily work

    Format: CSV output with columns: profession, example_text, week_relevant, habit_tag
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse CSV and insert into database
    examples = parse_csv(response.choices[0].message.content)
    db.batch_insert("profession_examples", examples)

    # Trevor reviews and approves
    return send_for_review(examples)
```

**Pros:**
- ✅ Scalable to 100+ professions
- ✅ Fast (minutes vs. hours)
- ✅ Consistent style (LLM follows pattern)

**Cons:**
- ❌ Requires human review (Trevor must approve)
- ❌ May lack authentic domain nuances
- ❌ LLM hallucination risk (mentions fake Kenyan contexts)

**When to Use:** After 6 months, when adding less common professions

---

#### **Approach C: Hybrid (Recommended Long-Term Strategy)**

**How:**
```python
# Tier 1 professions (common): Hard-coded, Trevor-written
PROFESSIONS_TIER_1 = [
    "teacher", "entrepreneur", "university_student",
    "working_professional", "gap_year_student"
]
# These get 10 hand-crafted examples each

# Tier 2 professions (less common): LLM-generated + Trevor review
PROFESSIONS_TIER_2 = [
    "nurse", "accountant", "engineer", "lawyer",
    "farmer", "journalist"
]
# These get LLM-generated examples (50% less total)
# Trevor reviews 20% as quality check

# Tier 3 professions (rare): Fallback to closest Tier 1
PROFESSIONS_TIER_3 = [
    "architect", "pharmacist", "social_worker", "designer"
]
# These map to: working_professional examples
# No new examples needed
```

**Implementation:**

```python
def get_profession_examples(student_profession, current_week):
    # Check tier
    if student_profession in PROFESSIONS_TIER_1:
        # Use hard-coded examples
        examples = db.query(
            "SELECT example_text FROM profession_examples "
            "WHERE profession = ? AND week_relevant LIKE ?",
            (student_profession, f"%{current_week}%")
        )

    elif student_profession in PROFESSIONS_TIER_2:
        # Use LLM-generated examples (cached after first generation)
        if not db.examples_exist(student_profession):
            # Generate on-the-fly with approval workflow
            examples = generate_profession_examples(student_profession, KENYAN_CONTEXT)
            send_to_trevor_for_approval(examples)

        examples = db.get_cached_examples(student_profession)

    else:  # Tier 3
        # Map to closest Tier 1 profession
        mapping = {
            "architect": "working_professional",
            "pharmacist": "working_professional",
            "social_worker": "teacher",
            "designer": "entrepreneur"
        }
        fallback_profession = mapping.get(student_profession, "working_professional")

        examples = db.query(
            "SELECT example_text FROM profession_examples "
            "WHERE profession = ? AND week_relevant LIKE ?",
            (fallback_profession, f"%{current_week}%")
        )

        # Notify student
        send_dm(
            student.discord_id,
            f"I've noted you're a {student_profession}. I'm using {fallback_profession} "
            f"examples for now — they're close enough to be useful. If you'd like to "
            f"help me craft {student_profession}-specific examples, let me know!"
        )

    return random.choice(examples)
```

**Pros:**
- ✅ Scalable (Tier 2 handles 90% of new professions)
- ✅ Quality-controlled (Tier 1 is hand-crafted)
- ✅ Efficient (Tier 3 requires no new work)
- ✅ Evolves with community (students can contribute examples)

**Cons:**
- ❌ More complex system
- ❌ Requires approval workflow for Tier 2

**When to Use:** After Year 1, when program has proven value and is scaling

---

### 9.4 Community-Sourced Examples (Future Enhancement)

**Idea:** Let students contribute their own examples

```python
# Command: /submit-example
# Student submits their own breakthrough story
async def submit_example(ctx, example_text):
    # Store in pending_examples table
    db.insert(
        "pending_examples",
        {
            "student_id": ctx.author.id,
            "profession": get_student(ctx.author.id).profession,
            "example_text": example_text,
            "status": "pending_review"
        }
    )

    await ctx.send("Thanks! Your example has been submitted for review. If approved, "
                   "it will be added to the example library for other [profession] students.")

# Trevor reviews weekly
# Approved examples → Added to profession_examples table
# Student gets notification: "Your example is now live! 🎉"
```

**Why This Works:**
- ✅ Authentic (real student breakthroughs)
- ✅ Scalable (community contributes)
- ✅ Engaging (students see their stories in the system)
- ✅ Kenyan-context-grounded (lived experience)

**When to Implement:** Year 2, after community culture is established

---

### 9.5 Recommendation: Start Simple, Evolve

**Phase 1 (Now - Month 6):**
- Use Approach A (hard-coded)
- Support 5 base professions
- Trevor writes 10 examples per profession

**Phase 2 (Month 6 - Month 12):**
- Add Approach C (Tier system)
- Tier 2 professions get LLM-generated examples
- Trevor approves 20% as quality check

**Phase 3 (Month 12+):**
- Add community-sourced examples
- Students can contribute and vote on examples
- System becomes self-sustaining

---

## 10. IMPLEMENTATION CHECKLIST

### 10.1 Discord Server Setup

- [ ] Create Discord server: `k2m-cohort-1`
- [ ] Create core channels: #announcements, #info
- [ ] Create onboarding channel: #welcome-and-onboarding
- [ ] Create weekly channels: #week-1-wonder through #week-8-graduation
- [ ] Create CIS tool channels: #thinking-lab, #thinking-showcase
- [ ] Create cluster channels: #cluster-1 through #cluster-6
- [ ] Create social channel: #the-watercooler
- [ ] Set up channel permissions (progressive disclosure)
- [ ] Write channel descriptions (see Section 2.3)
- [ ] Pin community norms in #welcome-and-onboarding
- [ ] Pin [SAFE SPACE] protocol in #the-watercooler

### 10.2 Bot Configuration

- [ ] Configure weekly channel unlock automation
- [ ] Set up inactive student nudge workflow
- [ ] Implement pattern match detection (optional, can start manual)
- [ ] Test role permissions (@Guest → @Student upgrade)
- [ ] Test CIS commands (/frame, /diverge, /challenge, /synthesize)
- [ ] Configure DM notifications for week unlocks

### 10.3 Content Preparation

- [ ] Write week 1-8 channel welcome messages
- [ ] Create community norms document
- [ ] Draft [SAFE SPACE] protocol
- [ ] Prepare first week's #the-watercooler conversation starters
- [ ] Create facilitator guidelines (Trevor's responsibilities)

### 10.4 Testing

- [ ] Test progressive disclosure with fake students
- [ ] Test @Guest → @Student permission upgrade
- [ ] Test bot DM notifications
- [ ] Test all CIS commands
- [ ] Load test: 100 students joining simultaneously

---

## 11. SUCCESS METRICS

### 11.1 Engagement Metrics

- **Weekly Active Rate:** % of students posting each week (target: 80%+)
- **Cross-Profession Interaction:** % of #the-watercooler convos with 2+ professions (target: 60%+)
- **Artifact Completion:** % of students publishing to #thinking-showcase (target: 70%+)
- **Pattern Match Detection:** # of cross-profession "that's my pattern too" moments (track qualitatively)

### 11.2 Retention Metrics

- **Week 1 Retention:** % who complete Week 1 activities (target: 90%+)
- **Week 4 Retention:** % still active at CIS tool unlock (target: 75%+)
- **Week 8 Retention:** % who graduate (target: 70%+)
- **Alumni Engagement:** % still in server 3 months post-graduation (target: 40%+)

### 11.3 Satisfaction Metrics

- **Net Promoter Score:** "Would you recommend K2M?" (target: +50)
- **Cross-Pollination Value:** "How much did you learn from other professions?" (1-10 scale, target: 8+)
- **Community Belonging:** "Do you feel part of this community?" (1-10 scale, target: 8+)

---

## 12. NEXT STEPS

1. **Review this document** with facilitation team
2. **Set up Discord server** following Section 10 checklist
3. **Test progressive disclosure** automation with small group
4. **Launch Cohort 1** with this architecture
5. **Iterate based on data** (adjust based on Weeks 1-4 learning)
6. **Decide on affinity spaces** after Week 4 data (see test-first approach in Section 5)
7. **Scale to Cohort 2** with refinements

---

**Produced by:** Party Mode Session — K2M Community Design Team
**Date:** 2026-03-04
**Status:** DESIGN + EXECUTION SPEC — canonical reference for community architecture and permissions
**Next Review:** After Cohort 1 Week 4 (data-driven adjustments)
