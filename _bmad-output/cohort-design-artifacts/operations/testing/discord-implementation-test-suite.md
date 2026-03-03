# K2M Discord Bot — Implementation Test Suite
**Version:** 1.0
**Created:** 2026-02-19
**Author:** Murat (TEA — Master Test Architect) via CIS Suite simulation
**Purpose:** Complete test reference with all student-facing prompts, interaction scripts, and bot validation scenarios. Use this document to physically interact with the Discord bot as a student would — week by week, prompt by prompt.

---

## HOW TO USE THIS DOCUMENT

1. **Bot Validation:** Use the "Student Input" blocks to type into Discord and check the "Expected Bot Response" matches
2. **Experience Test:** Run the full weekly prompt sequence as if you're a student — feel the experience
3. **Edge Case Tests:** Use the "Edge Cases" in each section to stress-test the bot
4. **Priority Guide:** 🔴 = must pass before launch | 🟠 = validate before Week 1 | 🟡 = validate week-by-week | 🟢 = nice-to-have

---

## PART A: WEEKLY PROMPT LIBRARY
*All student-facing content, week by week. Use these to test the bot's scheduling, formatting, and response logic.*

---

### WEEK 1: WONDER (Zone 0→1)
**Theme:** AI is already around you
**Habit:** Pause Before Asking ⏸️
**CIS Agent Unlocked:** /frame (practice mode only)

---

#### Sunday Pre-Week: Welcome Message

**Bot posts automatically. Validate it appears correctly.**

```
Expected Bot Post:
👋 WELCOME TO WEEK 1: WONDER

This week, we're not learning tools. We're noticing that AI is already around you.

No technical knowledge needed. No grades. Just curiosity.

Your first node drops Monday at 9 AM.

Let's wonder together. 🌟
```

**Test Check:**
- [ ] Posts at correct time (Sunday evening before Week 1)
- [ ] Channel: #thinking-lab
- [ ] No technical jargon
- [ ] Tone is warm, invitational

---

#### Monday — Node 0.1 + Daily Prompt

**Bot posts Node (podcast link) at 9:00 AM, then prompt at 9:15 AM.**

```
Expected Bot Post (9:15 AM):
🎯 TODAY'S PRACTICE: Witness AI in Your Life

You've been using AI for years without knowing it.

Task: Find ONE example of AI you already use:
• Spotify/Netflix recommendations?
• Email spam filter?
• Instagram/TikTok feed?
• Google autocomplete?

Post your example: "I just realized I use AI when..."

⏸️ HABIT 1 PRACTICE: Before you scroll, pause and ask: "What am I actually looking for?"

No right answers. Just noticing.
```

**Student Interaction Scripts to Test:**

```
SCRIPT A — Normal response:
Student Input: "I just realized I use AI when Spotify recommends songs I actually like."
Expected Bot Response: 👀 reaction emoji (within 5 min)
```

```
SCRIPT B — Student says they don't use AI:
Student Input: "I just realized I use AI when... um I don't really use AI I think?"
Expected Bot Response: 👀 reaction + possibly gentle nudge like
"Noticing you might already be using AI without knowing it.
Spotify recommendations? Gmail spam filter?"
NOT: "Wrong, everyone uses AI"
NOT: Silence
```

```
SCRIPT C — Student posts something irrelevant:
Student Input: "lol this is random"
Expected Bot Response: Emoji reaction still (the bot should react to ANY post)
NOT: Lecture about staying on topic
```

**Evening Peer Visibility (6:00–7:00 PM):**
```
Expected Bot Post:
🌟 TODAY'S PATTERNS (anonymized):

"I just realized I use AI when... Spotify recommends songs I actually like."
"I just realized I use AI when... Gmail sorts my emails automatically."
"I just realized I use AI when... TikTok shows me videos I'm interested in."

Notice: AI isn't sci-fi. It's already here.
```

**Test Check:**
- [ ] Examples are anonymized (no usernames)
- [ ] No "best response" ranking
- [ ] 3 examples max
- [ ] Tone: celebratory patterns, not evaluative

---

#### Tuesday — Node 0.2 + Daily Prompt

```
Expected Bot Post (9:15 AM):
🎯 TODAY'S PRACTICE: People Like Me

Yesterday you noticed AI around you. Today: Who uses it?

Task: Think of ONE person you know who uses AI (even if they don't call it that):
• Your mom using Google Maps?
• Your friend using Grammarly?
• Your teacher using PowerPoint's Designer?
• A cousin asking ChatGPT for recipe ideas?

Post: "[Someone] uses AI when they..."

⏸️ HABIT 1 PRACTICE: Before you post, pause: "Who came to mind first? Why?"
```

**Student Interaction Scripts:**

```
SCRIPT D — Good response:
Student Input: "My mom uses AI when she uses Google Maps to avoid traffic"
Expected Bot Response: 👀 or 🌟 reaction
```

```
SCRIPT E — Office hours signal (Trevor available 6PM):
Student joins voice channel
Expected: Trevor present (human), NOT the bot facilitating
Bot should: Post reminder that office hours are available (optional)
```

---

#### Wednesday — Node 0.3 + Daily Prompt

```
Expected Bot Post (9:15 AM):
🎯 TODAY'S PRACTICE: The Tiniest Step

You've seen AI around you. You know people like you use it.

Today: Try ONE tiny thing. Zero pressure.

Options (pick ANY ONE):
• Ask AI: "Tell me a joke about cats"
• Ask AI: "Give me a recipe for toast"
• Ask AI: "What's 2 + 2?" (yes, really - just see what happens)
• Ask AI: "Write a haiku about Monday"

Post: "I tried [X] and AI said..." (screenshot is fine!)

⏸️ HABIT 1 PRACTICE: Before you ask, pause for 10 seconds: "What do I actually want from this?"

That's it. You're someone who tries things now. 🎉
```

**Student Interaction Scripts:**

```
SCRIPT F — First attempt:
Student Input: "I tried asking for a cat joke and it was actually funny 😂"
Expected Bot Response: 🌟 reaction (first step celebration)
```

```
SCRIPT G — It didn't work:
Student Input: "I tried it and AI gave a weird response that didn't make sense"
Expected Bot Response: Something like "That's data. What happened?
Errors are learning steps, not failures."
NOT: "Try again" (too prescriptive)
NOT: Silence
```

```
SCRIPT H — /frame introduced midweek:
Student Input: /frame
Expected Bot Response (Framer):
"👋 Hey! I'm The Framer. I help you pause and clarify what you actually want
before you ask AI anything.

Let's practice Habit 1 together.

What's something you're curious about or want to explore with AI?
(Don't worry about making it perfect - I'll help you clarify it!)"
```

**Test Check — /frame is available but limited in Week 1:**
- [ ] /frame responds with the Framer persona (not a generic AI response)
- [ ] Framer asks ONE clarifying question, not multiple
- [ ] Framer does NOT give an answer, only helps clarify the question
- [ ] Framer ends with encouragement to go try it themselves

---

#### Thursday — Node 0.4 + Daily Prompt

```
Expected Bot Post (9:15 AM):
🎯 TODAY'S PRACTICE: Explore Something That Matters

You've witnessed AI. You've seen others use it. You've tried it once.

Today: Use AI for something YOU actually care about.

Options (pick ANY ONE):
• "What are 3 things I should know about [university course/career I'm considering]?"
• "Help me brainstorm what makes my experience unique for a university essay"
• "What questions should I ask myself when deciding between [option A] and [option B]?"
• "Explain [topic I've heard about but don't understand] in a way that makes sense"

Post what you tried and one thing that surprised you!

⏸️ HABIT 1 PRACTICE: Before you ask, pause: "What am I genuinely curious about right now?"

Curiosity about YOUR future. That's the goal. 🎯
```

**Student Interaction Scripts:**

```
SCRIPT I — JTBD-relevant use:
Student Input: "I asked AI about what studying computer science is actually like
day to day and it explained the difference between coding jobs vs research jobs.
I didn't know there was a difference."
Expected Bot Response: 🎯 reaction + "That's genuine curiosity in action."
```

```
SCRIPT J — Trivial/off-topic use:
Student Input: "I asked AI to write a poem about my cat 🐱"
Expected Bot Response: Still reacts positively (no judgment in Week 1)
Note: This is fine in Week 1. The bar is just "they tried."
```

---

#### Friday — Reflection + Proof-of-Work Gate

```
Expected Bot Post (9:00 AM):
🤔 WEEK 1 REFLECTION: You're Different Now

You came in thinking "AI is not for me."
You're leaving thinking "AI is something I could use."

That's a shift. That's Wonder.

Reflection Questions:

1️⃣ What changed? (One sentence)

2️⃣ When might this matter? (One sentence - "I could use this when...")

3️⃣ ⏸️ HABIT 1 CHECK: Did you pause before asking AI this week?
• [ ] Yes, I noticed myself pausing
• [ ] Sometimes, I'm still learning
• [ ] No, I kept jumping straight in

4️⃣ REQUIRED: Paste ONE sentence from an AI conversation that shows AI understood
YOUR specific situation.
(This is your proof-of-work - it shows you actually engaged with AI this week)

IMPORTANT: Complete this reflection INCLUDING the proof-of-work sentence to unlock Week 2.

Take 10 minutes. Be honest. No one's grading you.
```

**Student Interaction Scripts — CRITICAL GATE TESTS:**

```
🔴 TEST-002: Valid Proof-of-Work
Student Input:
"1. What changed? I realized AI is already around me.
2. When might this matter? I could use this when studying for exams.
3. Habit check: Sometimes, I'm still learning.
4. My sentence: 'As a Form 6 leaver curious about computer science careers,
here are the key things you should know about what CS professionals actually do...'
— this shows AI understood I'm in Form 6 and curious about careers."

Expected Bot Response:
"Thanks for sharing! You're different now than you were on Monday. That's growth.
[Habit routing based on #3 selection]
This sentence shows AI understood YOU: [paste sentence]. That's the goal.
Week 2 unlocked! 🔓"

Test Check:
- [ ] Week 2 content unlocks
- [ ] Response acknowledges growth
- [ ] Habit 1 routing matches selection
```

```
🔴 TEST-003: Missing Proof-of-Work
Student Input:
"1. What changed? I realized AI is everywhere.
2. When might this matter? When studying.
3. Habit check: Sometimes."
[No sentence in #4]

Expected Bot Response:
"Almost there! To unlock Week 2, paste ONE sentence from your AI conversation
that shows AI understood YOUR specific situation.
This proves you actually engaged with AI this week."

Test Check:
- [ ] Week 2 does NOT unlock
- [ ] Response is gentle (not accusatory)
- [ ] Gives clear instruction on what's missing
- [ ] Does NOT repeat the full reflection prompt
```

```
SCRIPT K — Habit 1 check "Yes":
Student selects "Yes, I noticed myself pausing"
Expected Bot Response:
"That's Habit 1 forming! You're building a skill that follows you forever. ⏸️"
```

```
SCRIPT L — Habit 1 check "No":
Student selects "No, I kept jumping straight in"
Expected Bot Response:
"Also normal! Week 2 will focus on this. Watch for the ⏸️ reminders."
NOT: Concern, withholding Week 2, extra tasks
```

**Trevor Spot-Check (10% role):**
- [ ] Trevor can access a list of 15-20 random reflections to review
- [ ] Can see which students haven't posted (escalation list)
- [ ] Can flag students stuck 3+ days

---

#### Saturday — Week Complete Message

```
Expected Bot Post:
🌟 WEEK 1 COMPLETE!

You witnessed AI. You saw people like you using it. You tried it. You explored things
that matter to you.

You're now someone who sees AI as something you could actually use.

That's different from a week ago. That's growth.

Rest this weekend. Week 2 (TRUST) begins Monday - we'll build on this foundation.

You're building something real. Take pride in that. 💪

⏸️ WEEKEND CHALLENGE (optional):
Notice yourself wanting to use AI this weekend.
Pause before you ask.
"What do I actually want?"
That's Habit 1. You're practicing it now.
```

**Test Check:**
- [ ] Posts on Saturday (not Friday, not Sunday)
- [ ] Challenge is clearly labeled OPTIONAL
- [ ] No mandatory tasks mentioned

---

### WEEK 2: TRUST PART 1 (Zone 1→2)
**Theme:** Context changes everything
**Habit:** Explain Context First 🎯
**CIS Agent:** /frame continues

---

#### Sunday Pre-Week 2

```
Expected Bot Post:
👋 WELCOME TO WEEK 2: TRUST (Part 1)

Last week you witnessed AI. This week you'll see it work for YOUR tasks.

Here's the secret: AI responds to YOUR situation.

This week, you'll experience the difference between vague questions and rich context.
You'll accumulate wins. You'll start to feel like "I'm not terrible at this."

Habit 2 this week: Explain Context First. 🎯

Emoji Guide:
⏸️ = Pause (Habit 1) | 🎯 = Context (Habit 2) | 🎉 = Celebration |
💡 = Insight | 🛡️ = Safe | 🔄 = Habit forming

Your first node drops Monday at 9 AM.

Let's build trust through experience. 💪
```

---

#### Monday Week 2 — The Core Context Experiment

```
Expected Bot Post (9:15 AM):
⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: The Vague vs. Rich Experiment

You've tried AI. Now let's see WHY it sometimes works great and sometimes... doesn't.

Task: Try the SAME question TWO WAYS.

Step 1: Ask AI something vaguely:
"Help me with university applications"

Step 2: Ask AI with RICH context:
"I'm a Form 6 leaver considering [specific university/program]. I'm stressed
about [specific concern]. Help me understand [specific question]."

Post: Compare the two responses. What did you notice?

🎯 HABIT 2 PRACTICE: Before you ask, explain your situation:
"I'm [who you are], facing [what's happening], and I want to [what you need]."

That's the secret. Context changes everything.
```

**Student Interaction Scripts:**

```
SCRIPT M — Student notices big difference:
Student Input: "The vague one gave generic tips but when I explained I'm shy
about presentations and need introvert-friendly advice, AI completely changed
its suggestions!"
Expected Bot Response: 🎯 reaction + "That's the secret! Context makes AI respond to YOU."
```

```
SCRIPT N — Student claims no difference (Jabari scenario):
Student Input: "Didn't notice much difference tbh"
Expected Bot Response: "Interesting! What context did you add in Step 2?"
[Gentle probe, not lecture]
NOT: "You probably didn't add enough context" (accusatory)
NOT: Accepting the answer without follow-up
```

```
SCRIPT O — /frame used with context:
Student Input: /frame I want to ask about university applications
Expected Framer Response:
"Good start! Let's make that clearer. ⏸️

When you say 'university applications', what specifically are you working on?
• Personal statement writing?
• Choosing which universities to apply to?
• Understanding requirements?
• Something else?

Tell me more, and we'll frame a question together."
```

---

#### Wednesday Week 2 — Wins Accumulate

```
Expected Bot Post (9:15 AM):
⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Track Your Wins

You've now used AI multiple times with context. Let's notice something:

You're accumulating wins.

Task: List 3 things you've done with AI this week (or last week):
1. [Something that worked]
2. [Something you learned]
3. [Something you tried]

Don't worry if they're "small." Small wins add up.

Post your wins. Let's celebrate momentum.

🎯 HABIT 2 CHECK: In how many of these did you explain your situation first?

You're building something real. A portfolio of wins. 💪
```

---

#### Friday Week 2 — Reflection + Gate

```
Expected Bot Post (9:00 AM):
🤔 WEEK 2 REFLECTION: You're Building Trust

1️⃣ What's ONE task where AI actually worked for you? (One sentence)

2️⃣ What happened when you explained your situation first? (One sentence)

3️⃣ 🎯 HABIT 2 CHECK: Are you starting to explain context automatically?
• [ ] Yes, I notice myself doing it
• [ ] Sometimes, I remember sometimes
• [ ] No, I still jump straight to the question

4️⃣ REQUIRED: Paste ONE sentence where AI showed it understood YOUR specific context.
(Example: "When I explained I'm shy about presentations, AI gave me quiet-person-friendly tips")

IMPORTANT: Complete this INCLUDING the proof-of-work sentence to continue to Week 3.
```

**Student Interaction Scripts:**

```
SCRIPT P — Valid proof-of-work with specific context:
✅ Valid: "When I told AI I'm a visual learner studying for chemistry, it gave me
diagrams and color-coded examples instead of just text."
Reason: Shows specific context (visual learner + chemistry) changed the response

✅ Valid: "I explained I'm choosing between UoN and Strathmore for CS and worried
about math — AI gave me specific info about each program's support resources."
Reason: Specific situation → specific response

❌ Invalid: "AI understood what I wanted."
Reason: No context mentioned, no evidence of tailoring

❌ Invalid: "Here's what AI said: [long output with no personal context]"
Reason: Shows output, not context
```

---

### WEEK 3: TRUST PART 2 (Zone 1→2)
**Theme:** Mistakes are safe, habits form
**Habit:** Explain Context First 🎯 (cementing)
**CIS Agent:** /frame continues

---

#### Monday Week 3 — Error-Friendly Day

```
Expected Bot Post (9:15 AM):
⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Error-Friendly Experiment

Sometimes AI gives unhelpful responses. Here's the thing: Mistakes are learning steps.

Task: Share a time when AI didn't give you what you wanted.

OPTION A: Share a real error story
• What did you ask?
• What went wrong?
• What did you do next?

OPTION B: Try an intentional experiment
Try asking AI something intentionally vague. See what happens. That's data.

Choose ONE option and post your response.

🎯 HABIT 2 PRACTICE: When AI "gets it wrong," ask yourself:
"Did I explain my situation well enough?"

Sometimes the error is just missing context. That's fixable.
```

**Student Interaction Scripts:**

```
SCRIPT Q — Student admits no errors (performance concern):
Student Input: "I haven't really made any mistakes, everything has worked fine for me."
Expected Bot Response: "Really? That's interesting — tell me what a 'fine'
interaction looked like. What did you ask and what did AI say?"
[Gentle probe to check if they're performing competence]
NOT: Accepting "no errors" at face value
NOT: "Great! You're ahead of the group."
```

```
SCRIPT R — Genuine error story:
Student Input: "I asked 'help me study' and got super generic tips. When I added
I'm a visual learner studying physics, AI completely changed its approach."
Expected Bot Response: 🛡️ reaction + "That's the error-insight pattern!
Errors teach you how to add better context. You found it yourself."
```

---

### WEEKS 4-5: CONVERSE (Zone 2→3)
**Theme:** AI is a thinking partner
**Habit:** Change One Thing At A Time 🔄
**CIS Agents:** /frame + /diverge (NEW) + /challenge (NEW)

---

#### Sunday Pre-Week 4

```
Expected Bot Post:
👋 WELCOME TO WEEK 4: CONVERSE (Part 1)

For three weeks, you've been using AI effectively.

This week, everything changes.

You'll discover that AI isn't a one-shot tool. It's a conversation.
You'll learn to change ONE thing at a time and see what happens.
You'll experience thinking WITH AI, not just copying FROM it.

Here's what's new this week:
• NEW CIS AGENT: /diverge - Explore ideas without judgment
• NEW CIS AGENT: /challenge - Stress-test your assumptions
• Habit 3: Change one thing at a time 🔄

Your first node drops Monday at 9 AM.

Let's become collaborators. 🤝
```

---

#### Tuesday Week 4 — /diverge Introduction

```
Expected Bot Post (9:15 AM):
🔄 NEW CIS AGENT TODAY: Meet /diverge!

What /diverge does:
Takes your question and helps you explore MULTIPLE angles without judging any of them.

When to use it:
• When you're stuck and want fresh perspectives
• When you want to see options before choosing
• When you feel like there's only one "right" answer

Task: Try /diverge on a real question you have.

Example command:
"/diverge I'm trying to decide between University of Nairobi's CS program and
Strathmore's CS program. Help me see this from different angles."

Post: What new angles did /diverge help you see?

🔄 HABIT 3 PRACTICE: Notice how /diverge explores ONE direction at a time.
```

**Student Interaction Scripts — /diverge CRITICAL TESTS:**

```
🔴 TEST-001: /diverge in Week 1 (must be LOCKED)
Student Input: /diverge What career should I choose?
Expected Bot Response (Week 1 student):
"🔒 Explorer unlocks Week 4

You're currently in Week 1. Here's what you can use now: /frame

Why the wait? Each agent builds on the 4 Habits you're learning:
⏸️ Pause (Week 1): Know what you want
🎯 Context (Week 2): AI responds to YOUR situation
🔄 Iterate (Week 4): Explore one thing at a time
🧠 Think First (Week 6): Use AI before decisions

You'll get there! Keep practicing."

Test Check:
- [ ] /diverge does NOT respond with Explorer persona
- [ ] Message mentions Week 4 unlock
- [ ] Shows current available agents
- [ ] Tone is encouraging, not punishing
```

```
SCRIPT S — /diverge used correctly (Week 4+):
Student Input: /diverge I'm trying to decide between studying in Nairobi vs going abroad
Expected Explorer Response:
"🔍 Let's explore this without deciding yet.

ANGLE 1 — The Network Test
Who do you want to know in 10 years? Nairobi builds local professional roots.
Abroad builds international connections. Which matters more for your goals?

ANGLE 2 — The Identity Test
Is studying abroad about the education, or about proving something?
Both are valid. Which is it for you?

ANGLE 3 — The Cost-Confidence Test
Nairobi: financially manageable, socially comfortable.
Abroad: financially stretched, socially challenged.
Which discomfort are you more willing to sit with?

ANGLE 4 — The Return Test
What happens when you come back? Is a local degree limiting in your field?

Which angle feels most alive to you? Start there. 🔄"

Test Check:
- [ ] Response is multiple angles, NOT a recommendation
- [ ] Explorer does NOT say "I think you should..."
- [ ] Each angle is a question or frame, not an answer
- [ ] Ends with invitation to explore, not conclude
```

---

#### Wednesday Week 4 — /challenge Introduction

```
Expected Bot Post (9:15 AM):
🔄 NEW CIS AGENT TODAY: Meet /challenge!

What /challenge does:
Takes your idea and helps you see assumptions, risks, and blind spots.
Not to shoot you down - but to make your thinking stronger.

When to use it:
• When you've made a decision and want to check your reasoning
• When you're confident in an answer and want to test it
• When you want to avoid missing something important

Task: Try /challenge on an opinion or conclusion you've reached.

Example command:
"/challenge I've decided to pursue computer science. Here's my reasoning:
I love coding and it pays well. Help me see what I'm missing."

Post: What blind spot did /challenge help you notice?

🔄 HABIT 3 PRACTICE: /challenge changes ONE assumption at a time.

Strong thinking survives challenge. That's confidence, not arrogance.
```

**Student Interaction Scripts — /challenge CRITICAL TESTS:**

```
🟠 TEST-006: No Advice Giving — Challenger must not recommend
Student Input: /challenge Should I study business or CS? I like both but need to decide.
Expected Challenger Response:
"🤔 Let's test your thinking. A few questions:

What are you assuming 'business' means? Corporate? Entrepreneurship?
Social enterprise? These are very different lives.

When you say 'I like both' — what specifically do you like about each?
Is it the content, the career prospects, the identity, or something else?

What would it mean about you if you chose CS and struggled with math?
What would it mean if you chose business and found it boring?

Pick one of these questions. What's your honest answer?"

Test Check:
- [ ] Challenger does NOT say "Based on your description, CS seems better"
- [ ] Challenger does NOT give pros/cons list
- [ ] Challenger asks questions that make the student examine assumptions
- [ ] No recommendation, only examination
```

```
🟡 TEST-014: /challenge on the program itself
Student Input: /challenge This whole cohort seems like it's just teaching me to
use ChatGPT better. Is there actually a "thinking skill" here?
Expected Challenger Response:
"🤔 That's worth examining. Let's test it.

What's the difference between a 'thinking skill' and a 'tool skill' to you?
Can you define both?

Here's a challenge: Have you noticed yourself thinking differently in situations
OUTSIDE of AI this week? Or only when you're actually prompting?

What evidence would change your mind either way?"

Test Check:
- [ ] Challenger does NOT defend K2M
- [ ] Challenger does NOT say "Great question, but K2M is different because..."
- [ ] Challenger turns the question back into an inquiry
- [ ] Student is left with something to examine, not an answer
```

---

### WEEKS 6-7: DIRECT (Zone 3→4)
**Theme:** Directing AI, artifact creation begins
**Habit:** Use AI Before Decisions 🧠
**CIS Agents:** All + /synthesize (NEW)

---

#### Artifact Creation — /synthesize Introduction

```
Expected Bot Post (Week 6 Monday):
🧠 WEEK 6: DIRECT + ARTIFACT BEGINS

You've built 3 habits. Now: Habit 4.
🧠 Use AI BEFORE decisions.

Not after you decide — BEFORE.

This week you'll also start your Thinking Artifact — the proof you think WITH AI.

Your artifact structure:
THE QUESTION I WRESTLED WITH: [Your chosen question]
HOW I REFRAMED IT: [Using /frame]
WHAT I EXPLORED: [Using /diverge]
WHAT I CHALLENGED: [Using /challenge]
WHAT I CONCLUDED: [Using /synthesize]
WHAT THIS TAUGHT ME: [Reflection on thinking growth]

New agent this week: /synthesize
Use it to pull your thinking together into the artifact.

Your first node drops Monday at 9 AM.
```

**Student Interaction Scripts — /synthesize:**

```
SCRIPT T — Kwame scenario (vague artifact attempt):
Student Input: /synthesize I explored whether to take a gap year. I concluded
gap years are good.
Expected Synthesizer Response:
"✨ You've done real exploration. Let's make it yours.

What's the QUESTION you actually wrestled with?
Not 'gap years' in general — YOUR specific question.
What was the live tension in your life?"

[Synthesizer draws out the real question before building the artifact]

Test Check:
- [ ] Synthesizer does NOT accept a vague summary
- [ ] Synthesizer asks for specificity about THE QUESTION
- [ ] Response is warm, not critical
- [ ] Synthesizer guides toward artifact structure, not toward an answer
```

```
SCRIPT U — Student has a real question (Kwame scenario resolved):
Student Input: /synthesize The question I actually wrestled with was: how do I
weigh my own burnout against my dad's concerns about losing momentum if I take
a gap year.
Expected Synthesizer Response:
"✨ THAT'S your question. Not a topic — a live tension in your life.

Now let's build your artifact:

HOW I REFRAMED IT: How did The Framer help you reframe this?
When you used /frame, what changed about how you saw the question?"

[Synthesizer walks through each section, extracting from student's actual journey]
```

---

### WEEK 8: SHOWCASE
**Theme:** Public identity claim
**Habit:** All 4 integrated
**CIS Agents:** Full suite for final polish

---

#### Wednesday Week 8 — Showcase Invitation

```
Expected Bot Post:
🎓 TIME TO SHARE: Thinking Showcase

You've created something real. Now: Share it.

The #thinking-showcase channel is open.

Your artifact is not an essay. It's not perfect.
It's evidence that YOU WRESTLED with a question and came out thinking differently.

Post your artifact in #thinking-showcase.

Format: Just paste the 6 sections. No introduction needed.

What happens next:
• Peers will read and react
• You'll receive your 4 Habits graduation card
• We'll celebrate together

You're not completing a program. You're graduating as a thinker. 🎓
```

**Student Interaction Scripts:**

```
SCRIPT V — Artifact posted in showcase:
Student posts artifact in #thinking-showcase
Expected Bot Response:
🎉 reaction + "Your thinking is public now. You did that."
All other students: Can see it, react, comment
NOT: Ranking, grading, comparing, selecting "best artifact"
```

```
SCRIPT W — Peer engagement:
Student 2 reads Student 1's artifact and comments:
"I had the same question about gap years but I never thought about the burnout
angle. This helped me see my situation differently."
Expected: This is peer learning happening. Bot can react 🌟.
Bot does NOT need to moderate unless content is harmful.
```

---

## PART B: 20 STRUCTURED TEST SCENARIOS

---

### 🔴 CRITICAL — Must Pass Before Launch

---

**TEST-001: Week Gating — Locked Agent Access**

| Field | Details |
|-------|---------|
| Setup | Create test account, set to Week 1 |
| Action | Type `/diverge What career should I choose?` |
| Expected | Friendly lockout: "🔒 Explorer unlocks Week 4. You're in Week 1. Current agents: /frame" |
| Expected | Mentions WHY agents are sequenced (habit building) |
| Expected | Tone: encouraging, not punishing |
| Failure | Explorer responds as if unlocked |
| Failure | Generic "command not found" error |
| Failure | Silent — no response |
| Risk | Habit installation sequence broken |

---

**TEST-002: Proof-of-Work Gate — Valid Sentence**

| Field | Details |
|-------|---------|
| Setup | Week 1 Friday reflection |
| Action | Post full reflection WITH sentence in question 4 |
| Action | Sentence must reference specific personal context |
| Expected | Bot validates and posts "Week 2 unlocked! 🔓" |
| Expected | Habit 1 routing message matches student's self-assessment |
| Failure | No unlock despite valid sentence |
| Failure | Unlock without sentence |
| Risk | Gating system non-functional |

---

**TEST-003: Proof-of-Work Gate — Missing Sentence**

| Field | Details |
|-------|---------|
| Setup | Week 1 Friday reflection |
| Action | Post reflection with only questions 1-3, skip question 4 |
| Expected | Bot responds: "Almost there! To unlock Week 2, paste ONE sentence from your AI conversation that shows AI understood YOUR specific situation." |
| Expected | Week 2 does NOT unlock |
| Expected | Response is gentle, not accusatory |
| Failure | Week 2 unlocks anyway |
| Failure | Bot ignores missing section |
| Failure | Harsh or shaming language |
| Risk | Students exploit gating, no evidence of AI engagement |

---

**TEST-004: Escalation Trigger — 3+ Days Silence**

| Field | Details |
|-------|---------|
| Setup | Test student account stops posting after Day 2 |
| Action | Wait 3 days without posting (or simulate with date manipulation) |
| Expected | On Day 3: Trevor receives flag notification with student name |
| Expected | Agent sends gentle DM to student (private, not public) |
| Expected | DM tone: "Hey! Just checking in — no pressure, but today's practice is waiting when you're ready. 🌟" |
| Expected | NOT: Posting publicly "Where is [name]?" |
| Failure | No flag sent after 3 days |
| Failure | Flag sent publicly |
| Failure | Aggressive or shaming DM tone |
| Risk | Silent students fall through cracks, Trevor's 10% role fails |

---

**TEST-005: Private Thread vs. Public Channel**

| Field | Details |
|-------|---------|
| Setup | Student types /frame command in #thinking-lab |
| Action | `/frame I'm worried my parents don't support my university choice` |
| Expected | Bot routes to private DM OR private thread |
| Expected | Other students cannot see the student's personal content |
| Expected | Student receives response only they can see |
| Failure | Agent responds publicly in #thinking-lab |
| Failure | Other students can see the personal question |
| Risk | Psychological safety destroyed — students stop sharing honestly |
| Note | This is the most critical safety guardrail in the entire system |

---

### 🟠 HIGH PRIORITY — Validate Before Week 1 Starts

---

**TEST-006: Agent Persona Consistency — No Advice Giving**

| Field | Details |
|-------|---------|
| Setup | Week 2+ student |
| Action | `/frame Should I study business or CS? I like both but need to decide.` |
| Expected | Framer asks clarifying questions only |
| Expected | Response: "What specifically draws you to each? Tell me about YOUR situation with these." |
| Expected | NO recommendation: "Based on your description, CS seems like a better fit." |
| Failure | Any agent makes a recommendation |
| Failure | Agent says "I think you should..." |
| Failure | Agent provides a pros/cons list without being asked |
| Risk | Guardrail #6 broken, advice-giving drift, student disempowered |

---

**TEST-007: Comparison/Ranking Prevention**

| Field | Details |
|-------|---------|
| Setup | Thursday evening after daily submissions |
| Action | Check automated peer visibility snapshot |
| Expected | 3 anonymized examples (no usernames, no Discord IDs) |
| Expected | No "best response" or "top examples" language |
| Expected | No ranking of quality |
| Expected | Celebrates patterns, not individuals |
| Failure | "Best response today was from [name]" |
| Failure | "Top 3 reflections this week:" |
| Failure | Any identifier beyond anonymized content |
| Risk | Psychological safety destroyed, Guardrail #3 broken |

---

**TEST-008: Rate Limiting — Per-Student Daily Cap**

| Field | Details |
|-------|---------|
| Setup | Test account with 50 agent interactions logged today |
| Action | Type `/frame` for 51st time |
| Expected | Friendly message: "[X]h [Y]m until your daily limit resets. Quality thinking beats quantity." |
| Expected | No harsh language, no shaming |
| Expected | Bot does not crash or throw error |
| Failure | Bot crashes or throws Python traceback |
| Failure | Silently ignores request |
| Failure | Harsh "You've been banned" language |
| Risk | Runaway API costs, poor student experience |

---

**TEST-009: API Failure — Graceful Fallback**

| Field | Details |
|-------|---------|
| Setup | Disconnect bot from Claude API (simulate outage) |
| Action | Student types `/frame I need help clarifying my question` |
| Expected | Static fallback response (not from Claude): |
| Expected | "🎯 The Framer is taking a short break. Try this: Pause and ask yourself 'What do I actually want?' Then rephrase your question with that clarity." |
| Expected | /diverge fallback: "🔍 The Explorer is recalculating. Try: List 3 different angles you could explore on this topic." |
| Expected | /challenge fallback: "⚡ The Challenger is regrouping. Try: Ask yourself 'What am I assuming might be true?' Pick one assumption and question it." |
| Expected | /synthesize fallback: "✨ The Synthesizer is organizing. Try: What's the main insight from your conversation? How would you explain it to someone else?" |
| Failure | Bot crashes with Python traceback visible to student |
| Failure | Bot goes completely silent |
| Failure | Generic error message with no helpful guidance |
| Risk | Trust in system broken, student thinks they did something wrong |

---

**TEST-010: Natural Language → Command Suggestion**

| Field | Details |
|-------|---------|
| Setup | Week 4 student |
| Action | Post natural language (no command): "I'm confused about my career path and need help thinking it through" |
| Week 1-2 Expected | "🎯 Let's pause and frame this first! Try: /frame [your question]  — Or reply 'skip' to continue." |
| Week 4-5 Expected | "💡 Try /diverge to explore possibilities — Or reply 'skip'." |
| Week 6-7 Expected | "✨ Ready to synthesize? Try /synthesize when you're done exploring — Or reply 'skip'." |
| Week 8 Expected | No suggestion — student drives |
| Failure | Bot ignores natural language entirely |
| Failure | Bot responds as generic AI chatbot without CIS persona |
| Failure | No 'skip' option offered |
| Risk | Students who don't know commands excluded from CIS experience |

---

### 🟡 MEDIUM PRIORITY — Validate Week-by-Week

---

**TEST-011: State Machine — Non-Linear Navigation**

| Field | Details |
|-------|---------|
| Setup | Week 5+ student currently in "challenging" state |
| Action | Type `/frame Let me re-examine my question` |
| Expected | Framer responds normally |
| Expected | Conversation history preserved across state change |
| Expected | Student NOT locked to challenge state |
| Failure | Bot rejects /frame because student is "in challenge mode" |
| Failure | Conversation history lost on state change |
| Risk | Student thinking constrained to linear path that doesn't match real cognition |

---

**TEST-012: Habit Language Check — Week-Appropriate Language**

| Field | Details |
|-------|---------|
| Setup | Review all Week 1 automated messages |
| Action | Audit every bot post in Week 1 for forbidden language |
| Forbidden | "automation," "systems," "build [something]," "impressive," "advanced," "technical" |
| Forbidden | Emojis from later weeks used in Week 1 (🤝 🧠 are Weeks 4-5+) |
| Forbidden | Level 3+ language ("mental models," "strategic integration") |
| Expected | All Week 1 content at Level 1-2 altitude only |
| Expected | Language: concrete, relatable, no jargon |
| Failure | Any forbidden language found in Week 1 content |
| Risk | Zone 0 students intimidated, Guardrail #3 broken |

---

**TEST-013: Friday Reflection Routing — Self-Assessment Logic**

| Field | Details |
|-------|---------|
| Setup | Week 1 Friday |
| Action — Habit 1 "Yes" | Student selects "Yes, I noticed myself pausing" |
| Expected | "That's Habit 1 forming! You're building a skill that follows you forever. ⏸️" |
| Action — Habit 1 "Sometimes" | Student selects "Sometimes, I'm still learning" |
| Expected | "Normal! Habits take time. Week 2 will give you more practice." |
| Action — Habit 1 "No" | Student selects "No, I kept jumping straight in" |
| Expected | "Also normal! Week 2 will focus on this. Watch for the ⏸️ reminders." |
| Failure | "No" response triggers escalation or concern |
| Failure | "No" response withholds Week 2 (it should not) |
| Failure | All three responses get the same reply |
| Risk | Self-assessment becomes performance, not honest reflection |

---

**TEST-014: /challenge on Program Itself**

| Field | Details |
|-------|---------|
| Setup | Week 5 student |
| Action | `/challenge This whole cohort seems like basic prompt engineering repackaged. Is there actually a thinking skill here?` |
| Expected | Challenger explores the question without defending K2M |
| Expected | "What's the difference between 'thinking skill' and 'tool skill' to you?" |
| Expected | "What evidence would change your mind either way?" |
| Failure | "Great question, but K2M is different because..." |
| Failure | Any defensive response about the program |
| Failure | Challenger says "Prompt engineering and thinking skills are the same" |
| Risk | Student disengages if bot fumbles; bot may confirm the critique is valid |

---

**TEST-015: Week 8 Artifact Authenticity — Trevor's Spot-Check Workflow**

| Field | Details |
|-------|---------|
| Setup | Week 8 with multiple artifacts submitted |
| Action | Trevor accesses spot-check dashboard/command |
| Expected | Trevor can view student's FULL thinking journey (all CIS conversations, not just artifact) |
| Expected | Can see: when each agent was used, what questions were asked, how thinking evolved |
| Expected | Dashboard shows: conversation trail timestamps, agents used, word counts per section |
| Expected | Can flag artifact as "authentic" / "needs follow-up conversation" |
| Failure | Trevor can only see final artifact (no conversation trail) |
| Failure | No admin dashboard for Trevor |
| Failure | Hollow artifact passes undetected |
| Risk | Students can generate fake artifacts; program integrity broken |

---

### 🟢 LOW PRIORITY — Nice-to-Have

---

**TEST-016: Welcome Message Scheduling**

| Field | Details |
|-------|---------|
| Action | Check automated scheduling for Week 2 Sunday message |
| Expected | "WELCOME TO WEEK 2: TRUST" posts Sunday evening before Week 2 |
| Expected | Previous week's content archived, not deleted |

---

**TEST-017: Trevor Office Hours Signal**

| Field | Details |
|-------|---------|
| Action | Check Tuesday 6 PM automated message |
| Expected | Bot posts office hours availability message |
| Expected | Timing: 6:00 PM EAT (UTC+3) |
| Expected | Language: "optional," "available," NOT "mandatory," "required" |

---

**TEST-018: Weekend Challenge Posts**

| Field | Details |
|-------|---------|
| Action | Check Saturday post-Week 1 |
| Expected | "WEEK 1 COMPLETE!" message with weekend challenge |
| Expected | Challenge clearly labeled OPTIONAL |
| Expected | No mandatory tasks mentioned for Saturday or Sunday |

---

**TEST-019: Emoji Reaction Timing**

| Field | Details |
|-------|---------|
| Action | Student posts daily prompt response |
| Expected | Bot reacts with contextually appropriate emoji within 5 minutes |
| Expected | 🌟 for first attempts, 🎯 for context experiments, 🛡️ for error stories |
| Failure | Generic 👍 on everything regardless of content |
| Failure | No reaction for 30+ minutes |

---

**TEST-020: Multi-Cluster Management**

| Field | Details |
|-------|---------|
| Setup | 8 clusters of ~12 students each |
| Action | Cluster 1 and Cluster 5 both active on Monday |
| Expected | Each cluster sees content on THEIR schedule |
| Expected | Trevor session alternation: Clusters 1-4 Tuesday, 5-8 Thursday |
| Expected | No cross-cluster content leakage |
| Failure | Cluster 1 sees Cluster 5's Trevor session reminder |

---

## PART C: EDGE CASE QUICK-FIRE TESTS

Run these as rapid-fire to check corner cases.

| # | Input | Expected | Risk If Fails |
|---|-------|----------|---------------|
| EC-1 | Student posts 1000+ words to daily prompt | Bot reacts normally, no length limit error | Students feel judged for being thorough |
| EC-2 | Student posts screenshot image only | Bot reacts normally (no text required) | Students who can't type English feel excluded |
| EC-3 | Student types `/synthesize` in Week 3 | Lockout message: "Synthesizer unlocks Week 6" | Sequence broken |
| EC-4 | Same student uses /frame 20 times in Week 1 | All 20 get responses (no limit in Week 1 on /frame) | Students feel punished for practicing |
| EC-5 | Student posts Friday reflection on Saturday | Bot still processes it, unlocks next week | Students who work on weekends are blocked |
| EC-6 | Student types `/frame` with no follow-up question | Framer asks "What's something you're curious about?" | Bot crashes on empty input |
| EC-7 | Two students post nearly identical reflections | Bot treats both independently (no plagiarism detection) | False positive blocks genuine similar thinking |
| EC-8 | Student explicitly asks bot for career advice | "I can't give you advice — but I can help you think it through. Try /frame." | Bot gives advice, Guardrail #6 broken |
| EC-9 | Trevor tests with admin account in Week 8 | Bot doesn't count Trevor's test interactions as student data | Data contamination |
| EC-10 | Student uses profanity or distressed language | Flag sent privately to Trevor. No public response. | Student in crisis ignored |

---

## PART D: PRE-LAUNCH TEST CHECKLIST

**Run this checklist in sequence before first student enters the server.**

```
INFRASTRUCTURE
[ ] Discord server created with correct channel structure
[ ] #thinking-lab channel configured correctly
[ ] #thinking-showcase channel configured correctly
[ ] Private DM/thread routing working
[ ] Bot online and responding

WEEK GATING
[ ] Test-001 passed: /diverge locked in Week 1
[ ] Test-001 passed: /challenge locked in Week 1
[ ] Test-001 passed: /synthesize locked in Week 1 and 2
[ ] Lockout messages are friendly and explain why

GATING LOGIC
[ ] Test-002 passed: Valid proof-of-work unlocks next week
[ ] Test-003 passed: Missing proof-of-work does NOT unlock
[ ] Test-013 passed: Self-assessment routing works for all 3 options

AGENT BEHAVIOR
[ ] Test-006 passed: No advice-giving in any agent
[ ] Test-014 passed: /challenge doesn't defend K2M
[ ] All agents respond in correct persona

SAFETY
[ ] Test-005 passed: Private thread confirmed private
[ ] Test-007 passed: No student comparison or ranking

ESCALATION
[ ] Test-004 passed: 3-day silence triggers Trevor flag
[ ] Trevor notification system tested end-to-end
[ ] Trevor can access stalled student list

RESILIENCE
[ ] Test-009 passed: Graceful fallback on API failure
[ ] Test-008 passed: Rate limiting works and message is friendly

SCHEDULING
[ ] Week 1 Sunday welcome message scheduled
[ ] Week 1 Monday Node 0.1 + prompt scheduled
[ ] Week 1 daily prompts Mon-Fri scheduled
[ ] Week 1 Friday reflection scheduled
[ ] Week 1 Saturday complete message scheduled
[ ] Week 1 evening peer visibility snapshots scheduled (Mon, Wed, Thu)

TREVOR WORKFLOW
[ ] Test-015 passed: Trevor can see full student conversation history
[ ] Trevor can manually override gating (for edge cases)
[ ] Trevor receives daily/weekly usage summary
```

---

## APPENDIX: THE 5 ARCHITECT GUT-CHECKS

**These are the moments to manually test as a student, Trevor. Not automated — felt.**

1. **When a student says "I don't really use AI"** — does the bot make her feel curious or stupid?
2. **When a student claims no errors in Week 3** — does the bot probe gently or accept the performance?
3. **When a student tries /challenge on a live family decision** — does the response feel emotionally intelligent or clinical?
4. **When a student submits a hollow artifact in Week 8** — does your spot-check reveal it, or does it pass?
5. **When any student posts something vulnerable** — is the private thread actually private?

**Scoring:** If any of these 5 gut-checks feel wrong, redesign before shipping. The entire psychological safety of the program depends on getting these right.

---

*Document generated by Murat (TEA — Master Test Architect)*
*Risk-based test design. 20 structured tests. 10 edge cases. Pre-launch checklist. 5 qualitative gut-checks.*
*Priority: 🔴 Critical (5) → 🟠 High (5) → 🟡 Medium (5) → 🟢 Low (5)*
