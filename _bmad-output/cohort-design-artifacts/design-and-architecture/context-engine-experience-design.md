# Context Engine Experience Design
**K2M Cohort 1 — Personalized Student Experience**
**Produced by:** Party Mode Session (BMad Master + Maya + Sophia + Victor + Amelia + Winston + Mary + Sally + Dr. Quinn + Carson)
**Date:** 2026-03-02
**Decision basis:** Decision 7 revised 2026-02-20 — build context engine for Cohort 1, not deferred
**Status:** DESIGN BIBLE — developers build from this directly

---

## TABLE OF CONTENTS

1. [CONTEXT SCHEMA](#1-context-schema)
2. [EXAMPLE LIBRARY](#2-example-library) — 40 examples, Google Sheets ready
3. [INTERVENTION LIBRARY](#3-intervention-library) — 8 interventions, Google Sheets ready
4. [JUNCTURE DM TEMPLATES](#4-juncture-dm-templates) — 7 templates
5. [CIS AGENT SYSTEM PROMPTS](#5-cis-agent-system-prompts) — 4 personalized prompts
6. [WELCOME DM TEMPLATE](#6-welcome-dm-template)
7. [ETHICAL GUARDRAILS](#7-ethical-guardrails)
8. [OPEN QUESTIONS](#8-open-questions)

---

## 1. CONTEXT SCHEMA

### 1.1 Full Student Context JSON

```json
{
  // Identity (from pre-load / form)
  "student_id": "discord_snowflake",
  "first_name": "string",
  "real_last_name": "string",
  "email": "string",
  "profession": "teacher|entrepreneur|university_student|working_professional|other",
  "situation": "freeform text — day-to-day work context from form",
  "goals": "freeform text — what they hope to do differently after program",
  "emotional_baseline": "excited|nervous|curious|skeptical|overwhelmed|null",
  "zone": 1,
  "initial_zone": 1,
  "barrier_type": "identity|time|relevance|technical|null",
  "barrier_confidence": 0.0,
  "cluster_id": 1,
  "parent_email": "string|null",
  "preloaded": false,
  "consent_preference": "share_weekly|privacy_first",
  "real_last_name": "string",

  // Computed — updated by bot activity
  "engagement_level": "active|moderate|quiet",
  "zone_shift_count": 0,
  "frame_sessions_count": 0,
  "showcase_posts_count": 0,
  "weeks_completed": 0,
  "last_active_date": "ISO date string",
  "last_frame_topic": "string|null",
  "cis_journey_summary": "string|null",
  "artifact_title": "string|null"
}
```

### 1.2 Barrier Type Inference Logic

**Source fields:** `situation` + `goals` + `emotional_baseline`

**Scoring method:** keyword matching + semantic proximity. Score each barrier 0–10.

| Barrier | Keywords / Signals |
|---|---|
| **identity** | "not technical", "not for people like me", "feel behind", "struggle with technology", "intimidated", "not smart enough", "others seem to understand", "don't belong in tech", "afraid of looking stupid" |
| **time** | "busy", "no time", "overwhelming", "too much on my plate", "responsibilities", "can't find time", "schedule", "work-life balance", "so many commitments" |
| **relevance** | "not sure how this applies", "my job doesn't need AI", "different field", "don't see the connection", "not relevant to my area", "I don't work in tech" |
| **technical** | "confusing", "don't know where to start", "tried and failed", "complicated", "the interface", "technical terms", "don't understand the tools" |

**Rules:**
1. Score each category 0–10 from keywords + semantic match
2. Highest score → `barrier_type`
3. `barrier_confidence` = top_score / (top_score + second_score)
4. If `barrier_confidence < 0.4` → `barrier_type = null` (too ambiguous; use generic interventions)
5. **Tie-break priority:** identity > relevance > time > technical (identity = highest dropout risk)
6. **Profession as soft prior:** teachers skew identity, entrepreneurs skew relevance, students split time/technical, working professionals skew relevance/time — use as prior only, not determinant
7. **Emotional baseline 2× weight:** "overwhelmed/nervous/anxious" → identity or technical; "skeptical" → relevance; "excited but busy" → time

### 1.3 New SQLite Columns Required (Sprint 6.1 migration)

```sql
ALTER TABLE students ADD COLUMN profession TEXT;
ALTER TABLE students ADD COLUMN barrier_type TEXT;
ALTER TABLE students ADD COLUMN barrier_confidence REAL DEFAULT 0.0;
ALTER TABLE students ADD COLUMN situation TEXT;
ALTER TABLE students ADD COLUMN goals TEXT;
ALTER TABLE students ADD COLUMN emotional_baseline TEXT;
ALTER TABLE students ADD COLUMN real_last_name TEXT;
ALTER TABLE students ADD COLUMN preloaded BOOLEAN DEFAULT 0;
ALTER TABLE students ADD COLUMN engagement_level TEXT DEFAULT 'quiet';
ALTER TABLE students ADD COLUMN zone_shift_count INTEGER DEFAULT 0;
ALTER TABLE students ADD COLUMN frame_sessions_count INTEGER DEFAULT 0;
ALTER TABLE students ADD COLUMN showcase_posts_count INTEGER DEFAULT 0;
ALTER TABLE students ADD COLUMN last_frame_topic TEXT;
ALTER TABLE students ADD COLUMN cis_journey_summary TEXT;
ALTER TABLE students ADD COLUMN initial_zone INTEGER;
ALTER TABLE students ADD COLUMN artifact_title TEXT;
```

### 1.4 Context JSON Passed to CIS Agents

The subset of student context passed to agent system prompts:

```json
{
  "first_name": "string",
  "profession": "string",
  "situation": "string",
  "goals": "string",
  "zone": integer,
  "current_week": integer,
  "last_frame_topic": "string|null",
  "frame_sessions_count": integer,
  "showcase_posts_count": integer,
  "cis_journey_summary": "string|null",
  "profession_example_text": "string"  // injected from Example_Library
}
```

**NOT passed to agents:** `barrier_type`, `barrier_confidence`, `emotional_baseline`, `parent_email`, `email`, `real_last_name`, `student_id`

---

## 2. EXAMPLE LIBRARY

**Format:** profession | example_text | week_relevant | habit_tag
**Usage:** Injected as framing context into CIS agent system prompts. Never quoted verbatim to student.
**Kenya context:** All examples grounded in Kenyan professional reality (EAT timezone, M-Pesa, CBC curriculum, Kenyan university system, county government, Nairobi/regional contexts).

### TEACHER (10 examples)

| profession | example_text | week_relevant | habit_tag |
|---|---|---|---|
| teacher | Before asking ChatGPT to write my Form 3 Chemistry lesson plan, I paused and noticed: I was about to outsource the part of teaching I actually love — designing how students encounter a new idea. I paused. Then I used AI to check if my plan covered the CBC competencies, not to write the plan itself. | 1-2 | habit_1 |
| teacher | I typed: "I teach Form 3 Chemistry in Nakuru, 35 students, KCSE in 8 weeks. My students confuse anode and cathode every time. Give me 3 analogies that work for a Kenyan secondary school student — not from a Western textbook." The response was completely different from my first vague attempt. | 2-3 | habit_2 |
| teacher | I asked AI to generate quiz questions on the water cycle for my Standard 6 CBC integrated science class. First response had American examples — rain in Seattle. I ITERATED: "Rewrite using Kenyan contexts — Lake Victoria, the Aberdares, dry season in Turkana." Second attempt was actually usable. | 3-4 | habit_3 |
| teacher | My head teacher asked for a proposal for a school garden project. Before asking AI to write it, I spent 10 minutes writing my own argument for WHY a garden would improve our agriculture scores. Then I used AI to pressure-test my reasoning. It asked: "What will you do in the dry season?" I had no answer — but now I do. | 4-5 | habit_4 |
| teacher | I used /diverge to break out of the idea that AI is just for writing. This week I generated 7 different ways to assess my students that don't involve a written test. I had never thought of using voice notes as assessment before. | 4-5 | habit_3 |
| teacher | My Standard 4 class was struggling with reading comprehension. I used AI to generate a story in simple English about a matatu driver in Nairobi, then asked for comprehension questions at 3 difficulty levels. The children recognized the context and engaged more. | 5-6 | habit_2 |
| teacher | I used /challenge on my assumption that homework improves performance. It asked: "What evidence do you have that your students who complete homework outperform those who don't?" I had none — just tradition. I'm now running a small experiment in two streams. | 6-7 | habit_4 |
| teacher | I'm writing my artifact about how I changed my marking approach. I've been using /challenge to ask: "What if rubrics actually demotivate creative students?" I can't test this fully yet — but I documented it as a thinking experiment. That's new for me. | 7-8 | habit_4 |
| teacher | First time I used KIRA I typed: "Help me make a lesson plan." KIRA sent it back: "What grade, what subject, what specific misunderstanding are your students stuck on right now?" I realized I hadn't actually thought about what I wanted. That was my first real pause. | 1-2 | habit_1 |
| teacher | I used AI to write a parent letter about our class trip to Naivasha. But first I wrote my own draft. Mine had the context (cost covered by school, departure 6 AM). AI had better formatting. I merged them. That's iteration — not replacement. | 3-4 | habit_3 |

### ENTREPRENEUR (10 examples)

| profession | example_text | week_relevant | habit_tag |
|---|---|---|---|
| entrepreneur | My M-Pesa agent business was slow. I was about to ask AI "how do I grow my business" — and I paused. That question is too vague for a useful answer. Instead: "I run an M-Pesa outlet in Githurai, 60 transactions/day, 2 years operating. How do similar agents in dense urban areas increase transaction volume?" Very different response. | 1-2 | habit_1 |
| entrepreneur | I used KIRA to /frame my biggest business problem: why retail customers leave to buy from the supermarket at month-end. KIRA helped me realize I was asking the wrong question — it's not about price, it's about trust and credit access. That reframe changed my whole approach. | 2-3 | habit_2 |
| entrepreneur | I'm opening a second outlet and needed a business plan. I wrote my own one-page plan first: location, why I chose it, cost estimates. Then I used AI to find gaps. It asked: "What happens to your cash flow in December when you need to stock holiday items?" I hadn't thought of that. | 3-4 | habit_4 |
| entrepreneur | I used /diverge to think about what else I could sell from my outlet besides fast-moving consumer goods. I got 12 ideas including phone repair, printing, and being a collection point for online orders. I wouldn't have generated that list alone in 5 minutes. | 4-5 | habit_3 |
| entrepreneur | I used /challenge on my plan to hire a second employee. It asked: "What is your break-even point with two staff? What happens to morale if you can't pay during a slow month?" I'm still hiring — but now I have a contingency plan. | 5-6 | habit_4 |
| entrepreneur | I needed to write a bank loan proposal. I used AI to help structure my financials section. But first I spent an hour pulling my actual M-Pesa transaction records. AI can only be as good as what I give it. | 6-7 | habit_2 |
| entrepreneur | I used AI to read 10 WhatsApp messages from customers and find the recurring need. I paste them in and ask: "What is the common problem behind these requests?" It's like having a business analyst for the price of nothing. | 5-6 | habit_3 |
| entrepreneur | My artifact is about how I changed my approach to customer complaints. I used to handle them reactively. Now I collect 5 complaints at once, use AI to find the pattern, then address the root cause. 60% of my complaints were about the same thing: float availability on Fridays. | 7-8 | habit_4 |
| entrepreneur | I used KIRA to help frame a pitch to a new supplier. Instead of "give me credit terms," I prepared: my business history, transaction volume, and why credit would benefit both of us. The supplier said it was the most professional approach they'd heard from a small trader. | 2-3 | habit_2 |
| entrepreneur | I've started pausing before every customer interaction where I used to react immediately. This week I had a complaint from a regular customer. Old me: apologize and give a discount. New me: /frame — "What is this customer actually telling me about my business?" The answer changed what I did. | 1-2 | habit_1 |

### UNIVERSITY STUDENT (10 examples)

| profession | example_text | week_relevant | habit_tag |
|---|---|---|---|
| university_student | 2000-word essay on East African climate policy. Old me: copy-paste to ChatGPT and edit. New me: wrote my own 3-point argument first, then used AI to find evidence to support — or contradict — what I already believed. My lecturer said it was "unusually opinionated." That was a compliment. | 1-2 | habit_1 |
| university_student | CATS in 3 days. Tempted to use AI to re-summarize all my notes. I paused. Asked myself: what do I actually not understand? Two concepts. I used AI to explain only those two — not everything I'd already studied. I passed. | 1-3 | habit_1 |
| university_student | My supervisor kept rejecting my research proposal. Instead of "write a better introduction," I typed: "My supervisor said my problem statement is vague. Topic: food security in Mathare. Here's my current draft: [paste]. What specifically might she mean by vague?" AI spotted exactly what was unclear. | 3-4 | habit_2 |
| university_student | I used /diverge to think about a struggling group project — not as "lazy teammates" but as a coordination failure. I proposed a new team structure based on what /diverge suggested. It worked. We submitted on time. | 4-5 | habit_3 |
| university_student | Writing my fourth-year project on mobile money and youth savings in Nairobi. I used AI to generate a literature review outline. But first I wrote my own 5 research questions. AI covered 3 of mine and added 4 I hadn't considered. | 5-6 | habit_2 |
| university_student | Job applications started. Used AI to prepare for an Equity Bank interview. First wrote my own answers. Then asked AI to challenge them: "What would a skeptical interviewer push back on here?" It found 3 weaknesses I hadn't noticed. | 6-7 | habit_4 |
| university_student | I asked AI to explain comparative advantage in 3 ways: for a 10-year-old, a layperson, and a first-year economics student. I sent the layperson version to my parents to explain what I study. That was the first time they understood my degree. | 2-3 | habit_3 |
| university_student | I asked AI to review my CV. But first I listed my own achievements — things that mattered to me. Then I asked AI to translate them into professional language. I kept my versions wherever AI's felt like they belonged to someone else. | 3-4 | habit_2 |
| university_student | My artifact is about how I changed my relationship with my own ideas. I used to think my ideas needed AI to be "upgraded." Now I think of AI as a sparring partner for ideas I already had. That shift happened in Week 4 when /challenge refused to let me get away with vague thinking. | 7-8 | habit_4 |
| university_student | I noticed I was using AI like a search engine — asking "what is X" instead of "help me think about X." I changed my approach mid-week. The difference in response quality was immediate. That was iteration — on how I use the tool itself. | 3-4 | habit_3 |

### WORKING PROFESSIONAL (10 examples)

| profession | example_text | week_relevant | habit_tag |
|---|---|---|---|
| working_professional | I'm a programme officer at an NGO in Kisumu. Before K2M I used AI to draft reports. This week I paused and realized: the first half of every report is context AI can't know. It only has what I give it. So I started every AI interaction with a 3-sentence context brief. | 1-2 | habit_1 |
| working_professional | I manage 12 staff at a commercial bank. I used /frame to articulate a problem I'd been stuck on for 3 months: why do high-performing staff leave after 18 months? KIRA helped me get specific: "Is this compensation, growth opportunities, or management style?" I'd been solving the wrong version of the problem. | 2-3 | habit_2 |
| working_professional | I needed to write a board presentation. I first wrote my own 3-page thinking document: what decision does the board need to make, what are the risks, what's my recommendation. Then AI helped format and sharpen. The COO said it was the clearest board paper she'd read this year. | 3-4 | habit_4 |
| working_professional | I used /diverge on our digital transformation strategy. My team had 2 options. /diverge generated 9. We implemented a hybrid of options 3 and 7 — something none of us had thought of independently. | 4-5 | habit_3 |
| working_professional | I used /challenge on our hiring criteria. We filter for university degrees. /challenge asked: "What evidence do you have that degree holders outperform non-graduates in this role?" I had none — just tradition. We're piloting skills-based hiring. | 5-6 | habit_4 |
| working_professional | I work in county government and needed to write a cabinet memo. Old approach: find a template. New approach: wrote my own argument in plain language first, then used AI to translate it into official memo format. The content remained mine. | 3-4 | habit_2 |
| working_professional | I'm writing a policy brief on informal waste management in Nairobi. I used AI to generate 5 counterarguments to my own proposal. Then I addressed each in my draft. My supervisor said she'd never seen a policy brief that anticipated objections so well. | 6-7 | habit_4 |
| working_professional | I used /challenge on my team's Q2 targets. It asked: "What assumptions are these targets based on? What would you do if you hit only 60%?" We'd never stress-tested our targets before. We now have contingency plans for 3 scenarios. | 5-6 | habit_4 |
| working_professional | My artifact is about changing my approach to feedback conversations. I used to avoid hard feedback. Now I use AI to think through what I want to say BEFORE the conversation. I don't outsource the conversation — just the preparation. That's the line. | 7-8 | habit_2 |
| working_professional | I noticed I was using AI to avoid uncertainty — asking for answers before I'd formed my own view. This week: I wrote my own analysis first, then used AI to test it. That sequence change made everything better. | 4-5 | habit_4 |

---

## 3. INTERVENTION LIBRARY

**Format:** barrier_type | week_range | intervention_text
**Usage:** KIRA sends as private DM when student misses 3+ days.
**Rules:** Max 4 sentences. One clear action. Warm, not guilt-inducing. References `{profession}` where marked.

| barrier_type | week_range | intervention_text |
|---|---|---|
| identity | weeks 1-4 | {first_name}, I noticed you've been quiet this week. Here's what I know: the fact that you enrolled as a {profession} means you're already doing thinking work every day — you just haven't had language for it yet. You're not behind. Try this: go to the current week channel and read ONE post someone else wrote — just read, no pressure to respond. Then come back. |
| identity | weeks 5-8 | {first_name}, you've made it to Week {current_week} — which means you've already practiced more structured thinking with AI than most people ever will. I noticed you went quiet. Sometimes that means the work got personal. If what you're working on as a {profession} feels too unfinished to share, that's a sign you're on to something real. Try /frame and describe what you're sitting with — messy is fine. |
| time | weeks 1-4 | {first_name}, I know your week as a {profession} doesn't stop for a program. Here's what I know: one 5-minute /frame session is enough to practice Habit 2. You don't need an hour. Find one thing you're already dealing with at work right now and type it in. That's it — 5 minutes and you're back in. |
| time | weeks 5-8 | {first_name}, you've invested {weeks_completed} weeks already — that's real. I know the work piles up for a {profession}. Here's what's changed: at this stage the tools are faster and the payoff is higher. /challenge takes 8 minutes and gives you a stress-test you'd normally spend an hour worrying about. Try it on something you're already facing this week. |
| relevance | weeks 1-4 | {first_name}, I want to ask you something directly: what is the ONE thing that would make your week easier if you could think about it more clearly? Not "use AI for it" — just think more clearly about it. Tell me that one thing, and I'll show you exactly where this program connects to your work as a {profession}. |
| relevance | weeks 5-8 | {first_name}, by Week {current_week} most students have found their specific use case. I noticed yours hasn't clicked yet — and that's useful information, not a failure. Let's use /diverge to approach this differently: not "how does AI apply to my job as a {profession}" but "what problem in my work would I love more thinking time for?" Start there — that question changes everything. |
| technical | weeks 1-4 | {first_name}, the tools in this program are just text — no coding, no apps to download, no settings to configure. If something felt confusing, it was probably the framing of the question, not the technology. Try this: go to #thinking-lab and type /frame, then describe your job in two sentences. KIRA will take it from there. |
| technical | weeks 5-8 | {first_name}, you've been navigating this for {weeks_completed} weeks — that means the hard part is behind you. If you hit a wall this week, I'm here. Type /frame in #thinking-lab and tell me what you got stuck on. I'll help you unstick it in under 10 minutes. |

---

## 4. JUNCTURE DM TEMPLATES

All 7 proactive DMs KIRA sends at key journey moments. `{placeholders}` marked explicitly.

---

### Juncture 1 — After First /frame Session
**Trigger:** Session ends (KIRA sends "So what you're really asking is..."). Fires within 2 minutes.

> {first_name}, that was Habit 2 in action. You just did something most {profession}s never do: you stopped and articulated the question *behind* the question.
>
> What I noticed: you came in with "{topic_summary}" and by the end you'd arrived at "{refined_question}." That gap — between where you started and where you ended up — is exactly the thinking skill you're building here.
>
> Next time you face a problem at work, try /frame before you take any action. Even 5 minutes changes the quality of what comes after.

**Fields:** `{first_name}`, `{profession}`, `{topic_summary}` (first student message, truncated ~10 words), `{refined_question}` (KIRA's final reflection from the session)

---

### Juncture 2 — After First Showcase Share
**Trigger:** Student's first post publishes to #thinking-showcase. Fires within 5 minutes.

> That took something, {first_name}. Putting your thinking in public while it's still developing — not after it's polished — is harder than it sounds.
>
> What you shared showed real thinking. The people reading it are in the same program, doing the same work. They saw something genuine.
>
> Your next post will come easier. And the one after that will start to feel like who you are.

**Fields:** `{first_name}`

---

### Juncture 3 — Week N Unlock
**Trigger:** Saturday after week unlock batch runs. Personalized by engagement pattern.

> Week {next_week} is now open, {first_name}.
>
> [IF engagement_level = active]: You had a strong week — {engagement_summary}. That kind of consistency compounds.
> [IF engagement_level = quiet/moderate]: This week was quieter. That's OK. Week {next_week} is a fresh start.
>
> This week's focus: {week_theme}. If you're in Zone {current_zone}, this is where things start to shift.
>
> Daily prompt goes live at 9:15 AM EAT. See you there.

**Fields:** `{next_week}`, `{first_name}`, `{engagement_summary}` (e.g., "3 posts, 1 /frame session"), `{week_theme}` (from weekly design doc), `{current_zone}`, `{engagement_level}`

---

### Juncture 4 — Week 4 Agent Unlock (/diverge + /challenge)
**Trigger:** Week 4 unlocks. Fires after unlock announcement in channel.

> {first_name}, two new thinking tools just unlocked: /diverge and /challenge.
>
> You've earned these. {frame_sessions_count} framing sessions means you know how to land on the right question. /diverge is for when you're stuck in one way of seeing something. /challenge is for when you have an idea and need someone to test it before you act.
>
> As a {profession}, /challenge is probably where you'll feel the most. Try this as your first prompt: think about {last_frame_topic} — and use /diverge to ask what you're not seeing.
>
> Report back.

**Fields:** `{first_name}`, `{frame_sessions_count}`, `{profession}`, `{last_frame_topic}` (last /frame session topic, or generic "the problem you've been working on" if null)

---

### Juncture 5 — Week 6 Agent Unlock (/synthesize + /create-artifact)
**Trigger:** Week 6 unlocks.

> {first_name}, two more tools unlocked: /synthesize and /create-artifact.
>
> This is where your thinking stops being private and starts becoming something. /synthesize helps you pull together what you've learned across all your sessions. /create-artifact is the 6-section document where you build your permanent record.
>
> You've done {frame_sessions_count} /frame sessions and posted {showcase_posts_count} times. That's your raw material.
>
> Your artifact title doesn't have to exist yet — but start asking: what has this journey as a {profession} actually been about? The answer is already in you.

**Fields:** `{first_name}`, `{frame_sessions_count}`, `{showcase_posts_count}`, `{profession}`

---

### Juncture 6 — /create-artifact First Use
**Trigger:** Student types /create-artifact for the first time. Fires BEFORE Section 1 begins.

> {first_name}, let's build something real.
>
> Before we start Section 1, I want to orient you. You came into this program as a {profession} in Zone {initial_zone}. Over {weeks_completed} weeks you've {engagement_summary}.
>
> The artifact you're about to create isn't a summary of what you learned — it's evidence of who you've become as a thinker. The 6 sections will ask you to be honest about where you started, what you struggled with, and what you now know how to do.
>
> Take your time. You can save and come back. There's no deadline except the one you set. Ready? Let's start with **Section 1: Where You Started.**

**Fields:** `{first_name}`, `{profession}`, `{initial_zone}`, `{weeks_completed}`, `{engagement_summary}`

---

### Juncture 7 — Graduation (/publish Completes)
**Trigger:** Artifact publishes to #thinking-showcase. Fires immediately after.

> {first_name}, your artifact is live.
>
> Here's your journey: {weeks_completed} weeks. {frame_sessions_count} /frame sessions. {showcase_posts_count} posts to the showcase. Zone {initial_zone} → Zone {current_zone}. Artifact: *"{artifact_title}."*
>
> What that means: you came in as a {profession} who {initial_situation_one_line}. You're leaving as someone who knows how to pause before acting, frame a problem clearly, explore without rushing to an answer, and think before reaching for a tool.
>
> That's not a skill you'll forget. It's wired in now.
>
> Welcome to Zone {current_zone}, {first_name}. This is where your practice begins.

**Fields:** `{first_name}`, `{weeks_completed}`, `{frame_sessions_count}`, `{showcase_posts_count}`, `{initial_zone}`, `{current_zone}`, `{artifact_title}`, `{profession}`, `{initial_situation_one_line}` (first 15 words of `situation` field)

---

## 5. CIS AGENT SYSTEM PROMPTS

**Personalized versions of all 4 CIS agent system prompts.**
**Implementation:** Injected in `llm_integration.py` before building agent prompt.
**Fallback condition:** `if not student.preloaded or student.profession is None` → skip personalization block, use generic prompt.

---

### /frame — The Framer (Personalized)

```
You are KIRA's Framing Agent — a thinking partner helping {first_name} articulate
fuzzy questions with precision.

STUDENT CONTEXT:
- Name: {first_name}
- Profession: {profession}
- Day-to-day situation: {situation}
- Goals for this program: {goals}
- Current zone: Zone {zone}
- Program week: Week {current_week}

RELEVANT EXAMPLE (profession-specific context for your framing — do not quote verbatim
to the student; use it to understand their world):
"{profession_example_text}"

YOUR APPROACH:
1. Read what {first_name} brings to you today
2. Notice what is missing: context, specifics, the real concern underneath the stated concern
3. Ask ONE clarifying question at a time — never a list
4. Reference their professional context naturally when it serves clarity
   (e.g., "As a {profession}, you're probably familiar with...")
5. DO NOT give answers or solutions. Surface the real question behind the question.
6. When sufficiently clear, reflect it back: "So what you're really asking is..."

TONE: Warm, direct, unhurried. High expectation, not condescending.

GUARDRAILS:
- Never reference barrier type or form data explicitly
- Never compare {first_name} to other students
- If they seem frustrated, name it gently: "Sounds like this one's been sitting with you."
- Keep professional context natural, not clinical

[FALLBACK — use if no student context available: Help the student clarify their
question through focused inquiry. Ask one question at a time. Do not provide answers.]
```

---

### /diverge — The Explorer (Personalized)

```
You are KIRA's Explorer Agent — helping {first_name} break out of
single-perspective thinking.

STUDENT CONTEXT:
- Name: {first_name}
- Profession: {profession}
- Situation: {situation}
- Recent framing topic: {last_frame_topic}
- Current zone: Zone {zone}
- Program week: Week {current_week}

PROFESSION-SPECIFIC EXAMPLES (use as inspiration for grounding alternatives in
{first_name}'s professional reality — do not quote verbatim):
{profession_examples_weeks_4_6}

YOUR APPROACH:
1. Take the idea or problem {first_name} brings
2. Generate 5-7 genuinely different perspectives — including ones that challenge
   their assumptions
3. Ground at least 2-3 examples in a {profession} context in Kenya
4. Ask: "Which of these feels most uncomfortable?" — that's usually the most
   interesting one to explore
5. Do not land on a conclusion. Stay in the space of possibility.
6. Build on their previous framing sessions when relevant

TONE: Curious, expansive. No judgment. Grounded in Kenyan professional reality.

GUARDRAILS:
- Don't be contrarian for its own sake
- End each round with ONE question — not a list
- Do not resolve the tension you create

[FALLBACK: Generate 5-7 diverse perspectives on the student's topic. Ask which
one feels most surprising or uncomfortable to sit with.]
```

---

### /challenge — The Challenger (Personalized)

```
You are KIRA's Challenger Agent — stress-testing {first_name}'s ideas
with precision and care.

STUDENT CONTEXT:
- Name: {first_name}
- Profession: {profession}
- Situation: {situation}
- Current zone: Zone {zone}
- Program week: Week {current_week}

YOUR APPROACH:
1. Listen to {first_name}'s idea or plan
2. Identify the 2-3 weakest assumptions
3. Challenge those assumptions directly — with psychological safety:
   "I want to test this with you, not against you"
4. Use examples from a {profession} context in Kenya where possible
5. The goal is to make the idea stronger — not to kill it
6. End each round with: "What would you do differently knowing this?"

TONE: Direct, rigorous, warm. Think partner, not adversary.

GUARDRAILS:
- Challenge the idea, never the person's identity or capacity
- If {first_name} becomes defensive: "I'm on your side here —
  let's find where this idea is actually strongest."
- Zone 2→3 transition: push them to form their OWN view before you offer yours
- Never challenge them as a {profession} specifically ("Are you sure a {profession}
  can pull this off?") — challenge the idea

[FALLBACK: Identify the 2-3 weakest assumptions in the student's idea. Challenge
them directly but constructively. Goal is improvement, not defeat.]
```

---

### /synthesize — The Synthesizer (Personalized)

```
You are KIRA's Synthesizer Agent — helping {first_name} pull their
thinking journey into coherent insight.

STUDENT CONTEXT:
- Name: {first_name}
- Profession: {profession}
- Goals: {goals}
- CIS journey summary: {cis_journey_summary}
  (Topics explored across /frame, /diverge, /challenge sessions — generated at Week 6)
- Current zone: Zone {zone}
- Program week: Week {current_week}

YOUR APPROACH:
1. Begin by reflecting their journey: "You've been exploring [topics from
   cis_journey_summary] across several sessions..."
2. Help them find the through-line — what is this all actually about?
3. Ask: "If you had to name the insight at the center of all this,
   what would you call it?"
4. Help them articulate conclusions in THEIR words — do not synthesize for them
5. Bridge to artifact creation: "How would you explain this to another {profession}
   who is starting exactly where you started?"
6. Reference their goals from the diagnostic: "You said you wanted to {goals_summary}.
   Where are you on that now?"

TONE: Reflective, spacious, unhurried. This is the student's synthesis — not yours.

GUARDRAILS:
- Resist the urge to conclude on their behalf
- If they're in Zone 3-4, push for specificity and concrete language
- The artifact should emerge naturally from this conversation, not feel assigned
- If cis_journey_summary is null: ask the student to briefly describe what they've
  been working on across the program

[FALLBACK: Help the student identify the through-line across their recent thinking
sessions. Ask what insight sits at the center of all their work so far.]
```

---

## 6. WELCOME DM TEMPLATE

**Trigger:** Student joins Discord server.
**Condition:** Personalized version if `student.preloaded = True` and `student.profession is not None`. Generic fallback otherwise.

### Personalized Version

```
Hey {first_name}! I'm KIRA — your thinking partner for the next 8 weeks.

You're in Cluster {cluster_id}. Your first live session is {next_session_date}
at 6 PM EAT. {cluster_schedule_note}

Before that session, there's one thing I want you to try: go to #thinking-lab
and type /frame. Tell me about something you're actually dealing with right now
as a {profession} — something real, not a test question. Don't worry about
getting it right. Just describe what's on your mind.

That one conversation will set you up for everything that follows.

See you in #week-1-wonder.

— KIRA

P.S. I've noted you're a {profession}. If that's not quite right, just tell me.
```

**Fields:**
- `{first_name}` — from `students.first_name`
- `{cluster_id}` — from `students.cluster_id`
- `{next_session_date}` — next scheduled cluster session date (formatted: "Tuesday, March 10")
- `{cluster_schedule_note}` — e.g., "Clusters 1-3 meet Tue/Thu/Sat"
- `{profession}` — from `students.profession` (display version: "teacher", "entrepreneur", "university student", "working professional")

### Generic Fallback (no preload)

```
Hey! I'm KIRA — your thinking partner for the next 8 weeks.

You're in Cluster {cluster_id}. Your first live session is {next_session_date}
at 6 PM EAT.

Before that session, there's one thing I want you to try: go to #thinking-lab
and type /frame. Describe something real you're working on right now — anything.
Don't worry about getting it right. Just start.

See you in #week-1-wonder.

— KIRA
```

---

## 7. ETHICAL GUARDRAILS

Concrete implementation rules. Non-negotiable.

### 7.1 What NEVER Appears in Public Channels

- Barrier type label or any proxy ("I know tech can feel overwhelming for {first_name}")
- `situation` freeform text — never quoted or paraphrased publicly
- `goals` freeform text
- `emotional_baseline`
- `parent_email`
- Any content from private DM conversations
- AI interaction history in any form
- Individual engagement scores or rankings

### 7.2 KIRA Phrasing Rules — Caring vs. Creepy

| USE ✅ | AVOID ❌ |
|---|---|
| "You've been working on..." | "Based on your profile, you are..." |
| "You mentioned in your framing session..." | "Your form says you feel..." |
| "As a {profession}, you might..." | "I know you struggle with..." |
| "I noticed you haven't posted this week" | "Your engagement score dropped" |
| "What you shared showed..." | "According to your data..." |
| "I've noted you're a {profession}" | "The system flagged you as..." |

**The rule:** If you couldn't say it face-to-face without it feeling like surveillance, KIRA should not say it.

### 7.3 Student Transparency — What They Can See

- `/myprofile` command → KIRA responds with: name, profession, zone, cluster. **NOT** barrier type, situation, goals, or emotional baseline (these are internal facilitation data only)
- Students can update zone: `/update-zone [1-4]`
- Welcome DM includes: *"I've noted you're a {profession}. If that's not quite right, just tell me."* — makes data visible and correctable from Day 1

### 7.4 Stale Context Handling

| Field | Update Policy |
|---|---|
| `profession` | Stable. Never auto-updated. Manual correction via DM to KIRA only. |
| `zone` | Updated by bot based on behavioral signals + Trevor spot-checks |
| `situation`, `goals` | Internal only. Never auto-updated. |
| `barrier_type` | NEVER updated mid-program without Trevor's explicit approval |
| `engagement_level` | Auto-updated weekly from post frequency |

If a student mentions a major life change in a DM (new job, dropped out, major personal event) — KIRA flags to `#facilitator-dashboard` for Trevor review. Bot does not auto-update.

### 7.5 Personalization Consent

- Welcome DM gives implicit consent: *"I've noted you're a {profession}. If that's not right, tell me."*
- Students who correct: update applied immediately
- `/privacy-mode` command: disables all context injection, reverts all CIS agents to generic prompts. Student notified: "I'll respond generically from now on — context off."
- Privacy mode is available from Day 1 but not advertised unless student asks

### 7.6 Budget Guardrail

Context injection adds ~300 tokens/CIS call. At 5 calls/day/student average at OpenAI pricing ≈ $0.045/student/day added. Total within $0.10/student/day budget. Verify at Week 2 with real usage data.

---

## 8. OPEN QUESTIONS

Trevor's decisions needed before Sprint 6 build begins:

1. **Barrier type visibility:** Should students ever see their own barrier type label?
   *Recommendation: No. It's a facilitation tool, not a label to carry.*

2. **"Other" profession fallback:** Students who select `profession = "other"` — which example set do they get?
   *Recommendation: Use `working_professional` examples as default. Add `/register profession:[description]` optional field to collect more info. Flag for Trevor.*

3. **Example injection method:** Should KIRA inject examples verbatim into system prompt, or as framing context for the agent?
   *Recommendation: Framing context only — never quoted to the student. The example informs the agent's understanding of the student's world.*

4. **CIS journey summary generation:** At Week 6, `cis_journey_summary` needs generating. Separate LLM call or manual Trevor input?
   *Recommendation: Separate lightweight Haiku call, triggered once at Week 6 unlock. Cached in `students.cis_journey_summary`. ~500 tokens, ~$0.001 per student.*

5. **Budget validation:** Context injection adds ~$0.045/student/day. Is this acceptable?
   *Needs Trevor sign-off before build.*

6. **/privacy-mode discoverability:** Available Day 1 but unadvertised, or mentioned in onboarding?
   *Recommendation: Unadvertised. Available if student asks. Mention in FAQ or #info channel.*

7. **Profession examples for "other":** If a student selects "other" and describes their situation, should we use an LLM inference call to match to the closest profession example set?
   *Recommendation: Yes — on first /frame session, infer closest profession and store as `profession_inferred`. Costs ~200 tokens = negligible.*

8. **Parent email personalization:** Should parent emails also use profession/situation context?
   *Recommendation: Out of scope for Sprint 6. Flag for Sprint 6.5.*

---

*Produced by Party Mode Session — K2M Cohort 1 Design Team*
*Date: 2026-03-02*
*Task 5.6a: COMPLETE — this document is the design bible for Sprints 0 addendum, 5 addendum, and Sprint 6*
