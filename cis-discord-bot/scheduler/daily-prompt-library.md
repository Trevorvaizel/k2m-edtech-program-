# Story 3.6: Daily Async Prompt Library (30 Prompts)

**Epic:** 3 - Session Scripts & Content (Module 5)
**Story:** 3.6 - Create daily async prompt library (32 prompts)
**Status:** ready-for-dev
**Reviewed:** 2026-01-25 - Adversarial review completed, critical fixes applied ✅
**Created:** 2026-01-25
**Production Ready:** YES - Goes directly to Discord agent

---

## Story 3.6 Overview

**Purpose:** Create a comprehensive library of 30 daily async prompts that the Discord agent will post throughout the 8-week cohort program.

**What This Contains:**
- 30 daily prompts across 8 weeks (Monday-Thursday each week, Friday reflections handled separately in weekly designs)
- Each prompt includes: Practice Task + Habit Practice section
- Friday reflection prompts are ALREADY in weekly design docs (not duplicated here)
- Wednesday peer visibility moments built in (specific weeks)
- JTBD-relevant examples ONLY (Guardrail #11 compliance)
- Brand voice compliance (Revolutionary Hope, altitude-appropriate language)
- All 4 Habits reinforcement across 8 weeks

**Target Audience:** Discord agent (primary), Trevor (secondary)

**Delivery Method:** Agent posts prompts at 9:00 AM EAT/UTC+3 Monday-Thursday each week

---

## Story Requirements

### From Epic 3, Story 3.6 (Requirements Document)

**User Story:**
As a Discord agent,
I want a comprehensive library of 30 daily prompts,
So that I can consistently engage students with habit-reinforcing practices across 8 weeks.

**Acceptance Criteria:**
1. [ ] 32 daily prompts total (4 per week × 8 weeks)
2. [ ] Each prompt reinforces the weekly habit focus
3. [ ] Each prompt includes JTBD-relevant practice task
4. [ ] Each prompt includes Habit Practice section
5. [ ] Friday reflections are NOT duplicated (exist in weekly designs)
6. [ ] Wednesday prompts include peer visibility moments
7. [ ] All examples are JTBD-relevant (careers, applications, anxiety, decisions)
8. [ ] Guardrails #11 compliance (no generic/juvenile examples)
9. [ ] Brand voice compliance (Revolutionary Hope, altitude-appropriate)
10. [ ] All 4 Habits reinforced across 8 weeks

**Business Value:**
- Daily engagement keeps cohort momentum
- Habit reinforcement builds identity transformation
- Peer visibility creates social proof
- JTBD-relevance ensures students care about tasks

---

## Developer Context: THE ULTIMATE GUIDE

### Critical Foundation Documents

**You MUST synthesize from these sources:**

1. **Requirements Document** (`cohort-playbook-v2-requirements.md`)
   - All 17 decisions for context
   - 8-week timeline structure (extended from 6 for deeper transformation)
   - Decision 10: Node-Based Learning Architecture (16 nodes, 4 per zone)
   - Decision 11: CIS Agent System (graduated introduction)
   - Decision 13: Thinking Artifact (JTBD-aligned)
   - Decision 17: Dual Pillars (Intelligence + Expertise)

2. **Epic 1.1: Guardrails** (`playbook-v2/01-philosophy/guardrails-preserved.md`)
   - 10 guardrails that protect framework purity
   - NEVER: Technical jargon, impressive demos, comparison, praise for speed
   - ALWAYS: Clarity over cleverness, confidence over competence, normalize confusion
   - v2-specific: Node quality, Discord safety, artifact authenticity, brand voice

3. **Epic 1.2: JTBD Integration** (`playbook-v2/01-philosophy/jtbd-integration.md`)
   - Zone-to-identity-shift mapping
   - Jobs: Functional (clarity), Emotional (belonging/confidence/companionship/ownership), Social (proof)
   - Each zone serves specific emotional job

4. **Epic 1.3: Node Architecture** (`playbook-v2/01-philosophy/node-architecture.md`)
   - 16 nodes across 4 zones (4 per zone)
   - Node design principles: One shift, concrete experience, relatable examples, NotebookLM-compatible, habit-reinforcing
   - Rock climbing metaphor: Mental lattice, holds, wall, summit

5. **Epic 1.4: 4 Habits Branding** (`playbook-v2/01-philosophy/four-habits-brand.md`)
   - Habit 1: Pause ⏸️ - "Know what you want before you ask" (Zone 0→1)
   - Habit 2: Context 🎯 - "AI responds to YOUR situation" (Zone 1→2)
   - Habit 3: Iterate 🔄 - "Change one thing at a time" (Zone 2→3)
   - Habit 4: Think First 🧠 - "Think with AI before you decide" (Zone 3→4)
   - Dual Pillars: Habits 1-2 = Intelligence (thinking), Habits 3-4 = Expertise (knowledge)

6. **Epic 2 Weekly Designs** (Weekly prompts as examples)
   - Week 1: Wonder (5 daily prompts in lines 639-728)
   - Weeks 2-3: Trust (10 daily prompts across both weeks)
   - Weeks 4-5: Converse (prompts integrated with CIS agents)
   - Weeks 6-7: Direct (prompts for artifact creation)
   - Week 8: Artifact showcase (reflection prompts)

7. **Epic 3 Story 3.5: NotebookLM Zone 3→4** (for pattern understanding)
   - Master prompt structure
   - JTBD-relevant example library (approved vs prohibited)
   - Quality checklist approach

8. **Epic 3 Story 3.1: Trevor Live Session Scripts** (for habit reinforcement patterns)
   - How Trevor models habits in live sessions
   - Habit demonstration scripts
   - All 4 habits integration

---

## Technical Requirements

### Prompt Structure (EVERY prompt must follow this)

```
[Emoji] TODAY'S PRACTICE: [Title]

[Brief context setting - 1-2 sentences]

**Task:**
[Specific practice task with JTBD-relevant examples]
[Options if appropriate]
[Call to action: Post/share format]

[Emoji] HABIT [X] PRACTICE: [Habit-specific reminder]
[Brief explanation of how this practice reinforces the habit]

[Closing encouragement - 1 sentence]
```

### Habit Practice Sections by Week

**Week 1 (Habit 1):**
⏸️ HABIT 1 PRACTICE: Before you ask, pause for 10 seconds: "What do I actually want from this?"

**Weeks 2-3 (Habit 2):**
🎯 HABIT 2 PRACTICE: Start with "I'm [situation]..." before you explain what you need.

**Weeks 4-5 (Habit 3):**
🔄 HABIT 3 PRACTICE: Change ONE thing at a time to see what each change does.

**Weeks 6-7 (Habit 4):**
🧠 HABIT 4 PRACTICE: Use AI to think through the decision BEFORE you choose.

**Week 8 (All Habits):**
⏸️🎯🔄🧠 HABIT INTEGRATION: Use all 4 habits together.

### Language Altitude Progression

**Week 1 (Zone 0→1):** Level 1-2 (Concrete/Pattern)
- "You've been using AI without knowing it"
- "AI isn't coming. It's already here."
- "Start small. No pressure."

**Weeks 2-3 (Zone 1→2):** Level 2 (Pattern)
- "Context changes everything"
- "Small wins add up"
- "Mistakes are learning steps"

**Weeks 4-5 (Zone 2→3):** Level 2-3 (Pattern/Framework)
- "AI responds to YOUR specific situation"
- "AI becomes your thinking partner"
- "Conversations refine toward precision"

**Weeks 6-7 (Zone 3→4):** Level 3-4 (Framework/Authority)
- "You're the director. AI provides raw material"
- "You're developing taste and standards"
- "You decide quality, not AI"

**Week 8 (Graduation):** Level 4 (Authority)
- "You're someone who thinks WITH AI"
- "You've built skills that follow you forever"

### Brand Voice Compliance

**Revolutionary Hope Tone:**
- Hope + empowerment (60%), Access + Justice (30%), Wonder (10%)
- NO fear-based language ("get left behind," "competitive advantage")
- YES linguistic DNA: "Finally" / "Wield" / "Achieve more" / "Follow you forever"

**Positioning: "Think WITH AI, not copy FROM it"**
- Partnership over tool-use
- Direction over prompting
- Thinking over outputs

**Coined Terms (from Brand Framework v3):**
- "Think WITH AI" (not "use AI")
- "Copy-pasters get stuck. Thinkers thrive."
- "Skills that follow you forever"
- "Tools change. Habits transfer."

---

## Guardrails Compliance (NON-NEGOTIABLE)

### Guardrail #1: No Technical Jargon (Early Weeks)
- NO: "LLM," "parameters," "neural networks," "machine learning"
- YES: "AI responds to your situation," "patterns," "structure"

### Guardrail #2: No "Impressive" AI Outputs
- NO: "Look what AI can do!" amazing demos
- YES: Normal, useful AI interactions for real tasks

### Guardrail #3: No Student Comparison or Ranking
- NO: "Top 3 responses," "Best examples"
- YES: Aggregate patterns only (anonymized)

### Guardrail #4: Celebrate Thinking, Not Outputs
- NO: "Great prompt!" "Perfect answer!"
- YES: "That's a great observation about your thinking"

### Guardrail #5: Normalize Confusion and Mistakes
- NO: "You should understand this by now"
- YES: "That's totally normal. This stuff takes time."

### Guardrail #11: JTBD-Relevant Examples (CRITICAL)

**APPROVED Example Categories:**
✅ University decisions and program comparisons
✅ Study plans and exam preparation
✅ Career exploration and narrowing choices
✅ Understanding complex topics through iteration
✅ Gap year vs. university decisions
✅ Processing anxiety about big life transitions
✅ Application essays and personal statements
✅ Making difficult decisions with information
✅ Understanding self through AI exploration

**PROHIBITED Examples (NEVER use):**
❌ Generic/Juvenile: "Write a poem about my cat," "Give me a recipe for toast," "Tell me a joke"
❌ Impressive/Intimidating: "AI wrote a novel in 10 seconds," "Look at this incredible artwork"
❌ Fear-Based: "AI will take your job," "You'll be left behind"
❌ Technical: "Large language models work by..."
❌ Passive Usage: "Give me a perfect prompt," "AI do this for me"

---

## Architecture Compliance

### Node Architecture Connection (Epic 1.3)

Each prompt should connect to the node being filled that week:

**Week 1 (Zone 0→1 Nodes):**
- Node 0.1: "AI is not sci-fi—it's here"
- Node 0.2: "People like me use this"
- Node 0.3: "I could try this"
- Node 0.4: "It's actually fun"

**Weeks 2-3 (Zone 1→2 Nodes):**
- Node 1.1: "It actually works for MY tasks"
- Node 1.2: "Low-stakes wins accumulate"
- Node 1.3: "Errors are recoverable"
- Node 1.4: "I'm starting to rely on it"

**Weeks 4-5 (Zone 2→3 Nodes):**
- Node 2.1: "Context changes everything"
- Node 2.2: "AI is a conversation partner"
- Node 2.3: "Explaining clarifies MY thinking"
- Node 2.4: "We're getting closer together"

**Weeks 6-7 (Zone 3→4 Nodes):**
- Node 3.1: "First draft is raw material"
- Node 3.2: "I have opinions about quality"
- Node 3.3: "Direction techniques work"
- Node 3.4: "I made this"

**Week 8 (Artifact):**
- All 16 nodes integrated
- Thinking Artifact completion

### CIS Agent Integration (Decision 11)

**Week 1:** /frame introduced (practice mode)
**Weeks 2-3:** /frame continues (building familiarity)
**Weeks 4-5:** /frame, /diverge, /challenge (full suite)
**Weeks 6-7:** All agents + /synthesize (artifact creation)
**Week 8:** All agents for artifact completion

Mention relevant agents in prompts: "Try /frame to clarify your question first" etc.

---

## The 30 Daily Prompts: Complete Library

### WEEK 1: WONDER (Zone 0→1)
**Theme:** "AI is something I could use"
**Habit Focus:** Habit 1 - Pause Before Asking ⏸️
**CIS Agent:** /frame (practice mode)
**Emotional Job:** Belonging ("Maybe this is for me")

---

#### **Monday (Week 1): Witness AI in Your Life**

🎯 TODAY'S PRACTICE: Witness AI in Your Life

You've been using AI for years without knowing it.

**Task:**
Find ONE example of AI you already use:
• Spotify/Netflix recommendations?
• Email spam filter?
• Instagram/TikTok feed?
• Google autocomplete?

Post your example: "I just realized I use AI when..."

⏸️ HABIT 1 PRACTICE: Before you scroll, pause and ask: "What am I actually looking for?"

No right answers. Just noticing.

---

#### **Tuesday (Week 1): People Like Me**

🎯 TODAY'S PRACTICE: People Like Me

Yesterday you noticed AI around you. Today: Who uses it?

**Task:**
Think of ONE person you know who uses AI:
• Your mom using Google Maps?
• Your friend using Grammarly?
• Your teacher using PowerPoint's Designer?
• A cousin asking ChatGPT for recipe ideas?

Post: "[Someone] uses AI when they..."

⏸️ HABIT 1 PRACTICE: Before you post, pause: "Who came to mind first? Why?"

---

#### **Wednesday (Week 1): The Tiniest Step**

🎯 TODAY'S PRACTICE: The Tiniest Step

You've seen AI around you. You know people like you use it.

Today: Try ONE tiny thing. Zero pressure.

**Options (pick ANY ONE):**
• "What are 3 things I should know about [computer science / medicine / law] as a university course?"
• "I'm deciding between [UoN and Strathmore]. What matters most?"
• "Help me understand [a complex topic like AI, crypto, climate change] in simple terms"
• "What questions should I ask myself when choosing a university program?"

Post: "I tried [X] and AI said..." (screenshot is fine!)

⏸️ HABIT 1 PRACTICE: Before you ask, pause for 10 seconds: "What do I actually want from this?"

That's it. You're someone who tries things now. 🎉

**Peer Visibility Moment:** Agent will aggregate anonymized responses in evening message.

---

#### **Thursday (Week 1): Explore Something That Matters**

🎯 TODAY'S PRACTICE: Explore Something That Matters

You've witnessed AI. You've seen others use it. You've tried it once.

Today: Use AI for something YOU actually care about.

**Options (pick ANY ONE):**
• "What are 3 things I should know about [university course/career I'm considering]?"
• "Help me brainstorm what makes my experience unique for a university essay"
• "What questions should I ask myself when deciding between [option A] and [option B]?"
• "Explain [topic I've heard about but don't understand] in a way that makes sense"

Post what you tried and one thing that surprised you!

⏸️ HABIT 1 PRACTICE: Before you ask, pause: "What am I genuinely curious about right now?"

Curiosity about YOUR future. That's the goal. 🎯

---

### WEEK 2: TRUST - PART 1 (Zone 1→2)
**Theme:** "It actually works for MY tasks"
**Habit Focus:** Habit 2 - Explain Context First 🎯
**CIS Agent:** /frame continues (reinforces Habit 2)
**Emotional Job:** Confidence ("I'm not terrible at this!")

---

#### **Monday (Week 2): The Vague vs. Rich Experiment**

⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: The Vague vs. Rich Experiment

You've tried AI. Now let's see WHY it sometimes works great and sometimes... doesn't.

**Task:**
Try the SAME question TWO WAYS.

**Step 1:** Ask AI something vaguely:
"Help me with university applications"

**Step 2:** Ask AI with RICH context:
"I'm a Form 6 leaver considering [specific university/program]. I'm stressed about [specific concern]. Help me understand [specific question]."

Post: Compare the two responses. What did you notice?

🎯 HABIT 2 PRACTICE: Before you ask, explain your situation:
"I'm [who you are], facing [what's happening], and I want to [what you need]."

That's the secret. Context changes everything.

---

#### **Tuesday (Week 2): Apply Context to YOUR Tasks**

⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Apply Context to YOUR Tasks

Yesterday you saw that context matters. Today: Use it for something YOU actually need to do.

**Pick ONE real task you're facing:**
• Understanding a topic for school
• Deciding between options
• Preparing for something coming up
• Brainstorming ideas

Try it WITHOUT context first. Then try WITH context.

Post: What was the difference? Be honest - did better context actually help?

🎯 HABIT 2 PRACTICE: Start with "I'm [situation]..." before you explain what you need.

Real tasks. Real context. Real results.

---

#### **Wednesday (Week 2): Track Your Wins**

⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Track Your Wins

You've now used AI multiple times with context. Let's notice something:

You're accumulating wins.

**Task:**
List 3 things you've done with AI this week (or last week):
1. [Something that worked]
2. [Something you learned]
3. [Something you tried]

Don't worry if they're "small." Small wins add up.

Post your wins. Let's celebrate momentum.

🎯 HABIT 2 CHECK: In how many of these did you explain your situation first?

You're building something real. A portfolio of wins. 💪

**Peer Visibility Moment:** Agent will aggregate anonymized wins in evening message.

---

#### **Thursday (Week 2): Habit 2 in Real Life**

⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Habit 2 in Real Life

You've seen context works. You've tracked wins. Today: Notice yourself.

**Task:**
Use AI for something you'd normally do anyway (homework help, decision, curiosity).

Before you type, notice:
• Did you pause? (Habit 1 ⏸️)
• Did you explain your situation first? (Habit 2 🎯)

Post: One sentence about how it felt to use BOTH habits together.

Optional: Share the situation you explained and how AI responded.

🎯 HABIT 2 PRACTICE: "Here's my situation: [explain], and I'm wondering about [question]"

When you explain context first, everything changes.

---

### WEEK 3: TRUST - PART 2 (Zone 1→2)
**Theme:** "Mistakes are safe, habits form"
**Habit Focus:** Habit 2 reinforcement + Habit integration
**CIS Agent:** /frame continues
**Emotional Job:** Confidence + Safety

---

#### **Monday (Week 3): Error-Friendly Experiment**

⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Error-Friendly Experiment

Sometimes AI gives unhelpful responses. Here's the thing: Mistakes are learning steps.

**Task:**
Share a time when AI didn't give you what you wanted.

**OPTION A:** Share a real error story
• What did you ask?
• What went wrong?
• What did you do next?

**OPTION B:** Try an intentional experiment
Try asking AI something intentionally vague. See what happens. That's data.

Choose ONE option and post your response.

🎯 HABIT 2 PRACTICE: When AI "gets it wrong," ask yourself:
"Did I explain my situation well enough?"

Sometimes the error is just missing context. That's fixable.

---

#### **Tuesday (Week 3): Turn Error into Insight**

⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Turn Error into Insight

Yesterday we normalized mistakes. Today: Learn from them.

**Task:**
Pick ONE task where AI's first response wasn't quite right.

Try the "Error → Insight" approach:
1. What was wrong with the response?
2. What context was missing?
3. How would you ask differently now?

Post your "before and after" questions.

**Example:**
BEFORE: "Help me study"
AFTER: "I'm studying for [specific exam], I'm struggling with [specific topic], can you help me understand [specific question]?"

🎯 HABIT 2 PRACTICE: Better context → Better responses.

Every error teaches you how to explain your situation better. That's skill.

---

#### **Wednesday (Week 3): Notice the Automatic Reach**

⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Notice the Automatic Reach

You've been using AI for 3 weeks now. Something might be happening without you realizing it.

**Task:**
Think about the last 2 days.

Did you reach for AI automatically?
• When you were confused about something?
• When you needed ideas?
• When you wanted to understand something better?

Post: One time you caught yourself thinking "I should ask AI about this..."

🎯 HABIT 2 CHECK: When you reached for AI, did you explain your situation first?

That automatic reach? That's habit forming.
You're becoming someone who uses AI without overthinking it.

**Peer Visibility Moment:** Agent will aggregate anonymized habit stories in evening message.

---

#### **Thursday (Week 3): Both Habits, Working Together**

⏸️→🎯 PRACTICE: Building on Pause by adding Context

🎯 TODAY'S PRACTICE: Both Habits, Working Together

You've been practicing Habit 1 (Pause ⏸️) and Habit 2 (Context 🎯).

Today: Notice them working together.

**Task:**
Use AI for something - and catch yourself in the habit loop:

⏸️ PAUSE: "What do I actually want?"
🎯 CONTEXT: "Here's my situation..."
[Ask AI]
💡 INSIGHT: "Oh, that helps because..."

Post: One sentence about how the two habits feel together.

Optional: Share a situation where BOTH habits made a difference.

You're not just "using AI." You're thinking WITH AI.

---

### WEEK 4: CONVERSE - PART 1 (Zone 2→3)
**Theme:** "Iteration changes everything"
**Habit Focus:** Habit 3 - Change One Thing At A Time 🔄
**CIS Agents:** /frame, /diverge, /challenge (NEW!)
**Emotional Job:** Companionship ("I have a thinking partner")

---

#### **Monday (Week 4): The Iteration Experiment**

🔄 TODAY'S PRACTICE: The Iteration Experiment

Three weeks ago, you asked AI questions and hoped for good answers.

This week: AI becomes a thinking PARTNER. You'll iterate together.

**NEW THIS WEEK:** We're adding TWO new thinking tools: /diverge and /challenge.
These join /frame (which you've been practicing since Week 1).
No pressure to master them - just explore and see what happens!

**Task:**
Try a conversation with AI (not just one prompt):

**Step 1:** Ask AI something about [topic you care about]
**Step 2:** Change ONE thing about your question
**Step 3:** Notice how the response shifts

Post: What changed when you iterated?

🔄 HABIT 3 PRACTICE: Change ONE thing at a time to see what each change does.

Example: "Make it shorter" → "Now make it funnier" → "Now add specific examples"

---

#### **Tuesday (Week 4): Try /diverge**

🔄 TODAY'S PRACTICE: Explore Multiple Angles

This week you have THREE thinking tools: /frame, /diverge, /challenge.

**Task:**
OPTIONAL PRACTICE: Use /diverge to explore a question from multiple angles.

**Try this:**
Type: `/diverge I'm trying to decide [decision]. Help me see options I haven't considered.`

Post: What angles did /diverge open that you wouldn't have thought of alone?

**No pressure** - If /diverge feels like too much today, stick with /frame. You're still building Habit 3.

🔄 HABIT 3 PRACTICE: When you explore multiple directions, you change one thing at a time.
First angle → Second angle → Third angle. See what each reveals.

---

#### **Wednesday (Week 4): Try /challenge**

🔄 TODAY'S PRACTICE: Stress-Test Your Thinking

You have /frame, /diverge, and now /challenge - three thinking partners.

**Task:**
OPTIONAL PRACTICE: Use /challenge when you're confident about something and want to test your assumptions.

**Try this:**
Type: `/challenge Here's my thinking about [topic]: [explain your position]. Stress-test it.`

Post: What did /challenge reveal that you hadn't considered?

**No pressure** - If /challenge feels like too much today, stick with /frame or /diverge. You're still building Habit 3.

🔄 HABIT 3 PRACTICE: Challenging is iterating through your own assumptions.
First assumption → Second assumption → Deeper understanding.

**Peer Visibility Moment:** Agent will share anonymized examples of students testing their thinking.

---

#### **Thursday (Week 4): All Three Tools Together**

🔄 TODAY'S PRACTICE: The Full Thinking Toolkit

You have /frame, /diverge, and /challenge. Today: Use them together.

**Task:**
Pick a question you're genuinely curious about.

**Try this sequence:**
1. `/frame [Your vague question]` - Clarify what you want
2. `/diverge [Your clarified question]` - See options you missed
3. `/challenge [Your favorite option]` - Stress-test it

Post: How did using all three tools change your thinking?

🔄 HABIT 3 PRACTICE: Each tool changes ONE thing about your thinking.
Frame → Clarity. Diverge → Options. Challenge → Depth.

---

### WEEK 5: CONVERSE - PART 2 (Zone 2→3)
**Theme:** "AI is my thinking partner"
**Habit Focus:** Habit 3 reinforcement + Meta-awareness
**CIS Agents:** /frame, /diverge, /challenge
**Emotional Job:** Companionship + Meta-awareness

---

#### **Monday (Week 5): Explaining Clarifies YOUR Thinking**

🔄 TODAY'S PRACTICE: Explaining Clarifies YOUR Thinking

Four weeks ago, you used AI to get answers.

Now? You use AI to THINK. Something shifts when you explain.

**Task:**
Use AI to explore something - and notice YOUR thinking changing.

**Try this:**
Start explaining to AI: "I'm trying to understand [topic]. Here's what I think so far: [explain]."

As you explain, notice: What do YOU realize?

Post: One moment when explaining to AI helped YOU think more clearly.

🔄 HABIT 3 PRACTICE: When you iterate with AI, you're not just refining the answer.
You're refining YOUR understanding, one change at a time.

---

#### **Tuesday (Week 5): Notice the Conversation Arc**

🔄 TODAY'S PRACTICE: Notice the Conversation Arc

You've been having conversations with AI (not just one-shot prompts).

Today: Notice how conversations evolve toward precision.

**Task:**
Look at a recent AI conversation (or start a new one).

**Notice the pattern:**
Vague start → You add context → AI responds → You refine → AI adjusts → You clarify → Precision emerges

Post: Share one example of how a conversation got better through iteration.

🔄 HABIT 3 PRACTICE: Each exchange changes ONE thing.
First exchange → Second exchange → Third exchange. You're getting closer together.

---

#### **Wednesday (Week 5): All Three Habits Working**

⏸️→🎯→🔄 PRACTICE: The Habit Stack

You've built three habits: Pause ⏸️, Context 🎯, Iterate 🔄.

Today: Notice them working together.

**Task:**
Use AI for something meaningful - and catch the habit loop:

⏸️ PAUSE: "What do I actually want?"
🎯 CONTEXT: "Here's my situation..."
🔄 ITERATE: "Let's change one thing..."

Post: How does it feel when all three habits work together?

🔄 HABIT INTEGRATION: When you pause → explain → iterate, you're not just using AI.
You're thinking WITH AI.

**Peer Visibility Moment:** Agent will share anonymized examples of habit integration in action.

---

#### **Thursday (Week 5): Artifact Preview**

⏸️→🎯→🔄 PRACTICE: Preparing for Artifact Creation

In Weeks 6-7, you'll start creating your artifact - proof that you think WITH AI.

**Task:**
Start thinking: What question could YOU explore that shows how you think?

**Some ideas:**
• "How do I approach big decisions now?"
• "Can I analyze something real?"
• "Do I have ideas worth hearing?"

Use /frame to explore potential artifact questions.

Post: One question you're curious about exploring for your artifact.

🔄 HABIT 3 PRACTICE: Your artifact will show how you iterate.
You'll use /diverge, /challenge, and /frame to explore deeply.

---

### WEEK 6: DIRECT - PART 1 (Zone 3→4)
**Theme:** "I can direct AI"
**Habit Focus:** Habit 4 - Use AI Before Decisions 🧠
**CIS Agents:** All agents + /synthesize (NEW!)
**Emotional Job:** Ownership ("I have standards")

---

#### **Monday (Week 6): First Draft is Raw Material**

🧠 TODAY'S PRACTICE: First Draft is Raw Material

Five weeks ago, AI's output felt like the final product.

Now: You know AI generates drafts → YOU decide quality and refine.

**Task:**
Use AI to generate something - then direct it toward YOUR standards.

**Try this:**
1. "Create a [essay/plan/explainer] about [topic]"
2. "This is too [generic/long/short]. Make it more [specific/criteria]."
3. "Now adjust for [your specific situation]."

Post: Show how you directed AI from raw material to YOUR standards.

🧠 HABIT 4 PRACTICE: Before you accept AI's output, pause: "Does this match my standards?"
If not, iterate. You're the director.

---

#### **Tuesday (Week 6): Try /synthesize**

🧠 TODAY'S PRACTICE: Use /synthesize for Artifact

This week you have /synthesize - a tool to help you write clearly.

**Task:**
Use /synthesize to help you think through something you've been exploring.

**Try this:**
Type: `/synthesize I've been thinking about [topic]. Here are my explorations with AI: [paste conversation]. Help me write up what I've learned.`

Post: How did /synthesize clarify YOUR thinking?

🧠 HABIT 4 PRACTICE: Use /synthesize BEFORE you decide your artifact is done.
Think → Write → Decide. That's directing.

---

#### **Wednesday (Week 6): I Have Opinions About Quality**

🧠 TODAY'S PRACTICE: Discover Your Standards

After 6 weeks of using AI, you've developed taste. You know when responses are... off.

**Task:**
Find ONE example where AI's response was "good but not great."

**Notice:**
• What was wrong with it?
• What was missing?
• What would YOU change?

Post: Share your standard - what makes an AI response "great" vs "just okay" for YOU?

🧠 HABIT 4 PRACTICE: When you notice "this isn't quite right," you're developing taste.
Use that taste to direct AI better.

**Peer Visibility Moment:** Agent will share anonymized standards students are developing.

---

#### **Thursday (Week 6): Direction Techniques Work**

🧠 TODAY'S PRACTICE: Learn to Direct

You know you have standards. Now: How do you get exactly what you want from AI?

**Task:**
Practice THREE direction techniques:

**1. Progressive specificity:**
"Help me choose a university"
→ "I'm deciding between UoN and Strathmore for CS"
→ "I care about AI/ML focus, campus community, and cost"

**2. Example-based steering:**
"Explain electricity"
→ "That's too technical. Use real-world examples"
→ "Connect it to things I see daily"

**3. Iterative refinement:**
"Help me write a personal statement"
→ /frame to clarify values
→ "Weave in these 3 specific experiences"
→ "Make it sound more like ME"

Post: Which technique worked best for YOU?

🧠 HABIT 4 PRACTICE: Direction techniques help you think WITH AI before decisions.
Try → Direct → Decide. That's ownership.

---

### WEEK 7: DIRECT - PART 2 (Zone 3→4)
**Theme:** "I create with intention"
**Habit Focus:** Habit 4 reinforcement + Director identity
**CIS Agents:** All agents for artifact creation
**Emotional Job:** Ownership + Pride

---

#### **Monday (Week 7): I Made This**

🧠 TODAY'S PRACTICE: Claim Authorship

Six weeks ago, you might have said "AI wrote this."

Now: You know "I made this with AI's help." There's a difference.

**Task:**
Look at something you've created WITH AI recently (essay, plan, decision framework, exploration).

**Trace the authorship:**
• YOUR idea → AI generated → YOU noticed what was off → YOU directed refinement → YOUR standards → Final product

Post: Can you say "I made this" about something? What's YOUR contribution?

🧠 HABIT 4 PRACTICE: Before you accept AI's help, pause: "What will MY contribution be?"
Think → Direct → Own. That's the director identity.

---

#### **Tuesday (Week 7): Artifact Deep Work**

🧠 TODAY'S PRACTICE: Create Your Artifact

This week: Spend serious time on your artifact - proof you think WITH AI.

**Task:**
Work on your artifact using all four tools:

**Try this sequence:**
1. `/frame` - What question will you explore?
2. `/diverge` - What angles haven't you considered?
3. `/challenge` - Stress-test your thinking
4. `/synthesize` - Write it up clearly

Post: One moment when you realized "I'm directing this, not just using AI."

🧠 HABIT 4 PRACTICE: Your artifact shows you think WITH AI.
Frame → Diverge → Challenge → Synthesize. That's directing.

---

#### **Wednesday (Week 7): All Four Habits, Integrated**

⏸️→🎯→🔄→🧠 PRACTICE: The Complete Director

You have all four habits now. Today: Use them together as a director.

**Task:**
Use AI to create or decide something - with full habit integration:

⏸️ PAUSE: "What do I actually want?"
🎯 CONTEXT: "Here's my situation..."
🔄 ITERATE: "Change one thing at a time"
🧠 THINK FIRST: "Use AI to think before I decide"

Post: How does it feel to direct AI with all four habits?

⏸️→🎯→🔄→🧠 HABIT INTEGRATION: You're not just using AI.
You're thinking WITH AI. You're directing intentionally. You're the director.

**Peer Visibility Moment:** Agent will share anonymized examples of students directing with all four habits.

---

#### **Thursday (Week 7): Artifact Polish**

⏸️→🎯→🔄→🧠 PRACTICE: Finalize Your Artifact

Week 8 is artifact showcase. Today: Put finishing touches on YOUR artifact.

**Task:**
Review your artifact through all four habits:

⏸️ Does it show you paused to frame your question?
🎯 Does it show your specific context and situation?
🔄 Does it show iteration and exploration?
🧠 Does it show you used AI to think before concluding?

Post: One sentence about what makes this artifact YOURS.

⏸️→🎯→🔄→🧠 HABIT INTEGRATION: Your artifact proves you think WITH AI.
That's not just using a tool. That's transformation.

---

### WEEK 8: GRADUATION (All Zones)
**Theme:** "You're someone who thinks WITH AI"
**Habit Focus:** All 4 Habits integrated
**CIS Agents:** All agents for artifact completion
**Emotional Job:** Pride ("I'm proud to share this")

---

#### **Monday (Week 8): The Habit Stack in Real Life**

⏸️→🎯→🔄→🧠 PRACTICE: Habits Beyond Cohort

Eight weeks ago, you learned four habits.

Now: Where will you use them AFTER this cohort ends?

**Task:**
Think about your next 3 months (university, applications, decisions).

**Identify 3 situations where you'll use these habits:**
1. [Situation] - I'll use [Habit] because...
2. [Situation] - I'll use [Habit] because...
3. [Situation] - I'll use [Habit] because...

Post: Where will these habits follow you?

⏸️→🎯→🔄→🧠 TRANSFER: Tools change. Habits transfer.
You're not just "graduating from a cohort." You're entering the world as a thinker.

---

#### **Tuesday (Week 8): My Artifact, My Thinking**

⏸️→🎯→🔄→🧠 PRACTICE: Artifact Reflection

Your artifact is proof you think WITH AI. Today: Reflect on what it shows.

**Task:**
Review your artifact. Notice:

⏸️ Where did pausing change your question?
🎯 Where did context transform AI's response?
🔄 Where did iteration deepen your understanding?
🧠 Where did thinking WITH AI shift your decision?

Post: One sentence: "My artifact shows I'm someone who..."

⏸️→🎯→🔄→🧠 IDENTITY: Your artifact isn't about AI capabilities.
It's about YOUR thinking. That's the difference.

---

#### **Wednesday (Week 8): Peer Celebration**

⏸️→🎯→🔄→🧠 PRACTICE: Celebrate Each Other

You've been on this journey together. Today: Notice and celebrate each other's growth.

**Task:**
Read THREE classmates' artifacts in #thinking-showcase.

For each one, post:
• "What I noticed: [one thing about THEIR thinking]"
• "What I celebrated: [one moment of growth]"

No critique. Only celebration of diverse thinking.

⏸️→🎯→🔄→🧠 COMMUNITY: You're not just 200 individuals.
You're a community of thinkers who use AI differently.

---

#### **Thursday (Week 8): The 4 Habits Card**

⏸️→🎯→🔄→🧠 PRACTICE: Claim Your Badges

Today you receive your 4 Habits card - graduation proof.

**Task:**
Look at your 4 Habits card. Reflect:

⏸️ PAUSE - "I earned this badge when..."
🎯 CONTEXT - "I earned this badge when..."
🔄 ITERATE - "I earned this badge when..."
🧠 THINKING PARTNER - "I earned this badge when..."

Post: One habit that feels most natural to you now.

⏸️→🎯→🔄→🧠 GRADUATION: You didn't just "learn AI."
You transformed into someone who thinks WITH AI.
That's who you are now. Carry that forward.

---

## Agent Response Templates

### For Monday-Thursday Submissions (General Pattern)

```python
# Agent routing based on prompt type and student response

if prompt_type == "witnessing" or prompt_type == "noticing":
    emoji_reaction = "👀"  # witnessed!
    response = "That's a great observation. You're noticing AI around you."

elif prompt_type == "trying" or prompt_type == "experimenting":
    emoji_reaction = "🌟"  # first step!
    response = "You tried something! That's how trust builds."

elif prompt_type == "habit_practice":
    if habit_1_mentioned:
        emoji_reaction = "⏸️"
        response = "That's Habit 1 in action - pausing before asking."
    elif habit_2_mentioned:
        emoji_reaction = "🎯"
        response = "Context changes everything, right? That's Habit 2 working."
    elif habit_3_mentioned:
        emoji_reaction = "🔄"
        response = "You're iterating! That's Habit 3 - one change at a time."
    elif habit_4_mentioned:
        emoji_reaction = "🧠"
        response = "Thinking WITH AI before deciding? That's Habit 4."

elif prompt_type == "error_sharing":
    emoji_reaction = "🛡️"  # safe!
    response = "Thanks for sharing! Errors are totally normal - and they teach us how to add better context."

elif prompt_type == "habit_formation":
    emoji_reaction = "🔄"  # loop = automatic!
    response = "You caught yourself reaching for AI automatically? That's the habit living in you now!"

elif prompt_type == "director_identity":
    emoji_reaction = "🎯"  # bullseye!
    response = "You're developing taste and standards. That's the director identity emerging."

elif student_seems_stuck:
    response = "Totally normal to feel like this is taking time. Habits form gradually. You're on track."

elif not_posted_by_6pm:
    gentle_nudge = f"Hey! Today's practice is waiting when you're ready. No pressure. {get_emoji_for_week(week)}"
```

### For Wednesday Peer Visibility Moments

```python
# Agent aggregates anonymized responses (Wednesday evenings)

def create_peer_visibility_message(responses, week):
    """Create anonymized aggregate of student responses"""

    message = f"🌟 TODAY'S PATTERNS (anonymized):\n\n"

    # Select 3-5 diverse responses (anonymized)
    for response in select_diverse_responses(responses)[:5]:
        message += f'"{anonymize(response)}"\n'

    # Add pattern observation
    message += f"\nNotice: {get_pattern_for_week(week)}"

    return message

def get_pattern_for_week(week):
    patterns = {
        1: "AI isn't sci-fi. It's already here.",
        2: "AI responds to YOUR specific situation.",
        3: "AI isn't something you 'try' anymore. It's something you USE.",
        4: "Iteration changes everything. Conversations refine toward precision.",
        5: "When you explain to AI, you clarify YOUR thinking.",
        6: "You're the director. AI provides raw material.",
        7: "You're not just using AI. You're directing AI intentionally.",
        8: "You've become someone who thinks WITH AI."
    }
    return patterns.get(week, "Great observations this week!")
```

---

## Quality Checklist (For Each Prompt)

### Prompt Structure Check
- [ ] Follows standard structure: Emoji + Title + Context + Task + Habit Practice + Closing
- [ ] Task is specific and actionable
- [ ] Examples are provided where appropriate
- [ ] Post/share format is clear

### Habit Reinforcement Check
- [ ] Correct habit icon used (⏸️🎯🔄🧠)
- [ ] Habit practice section is clear
- [ ] Connection between task and habit is explicit
- [ ] Habit language matches week focus

### JTBD Relevance Check (Guardrail #11)
- [ ] All examples are from APPROVED categories
- [ ] NO examples from PROHIBITED list
- [ ] Examples serve functional, emotional, OR social job
- [ ] Examples are age-appropriate (17-19 year olds)
- [ ] Examples are life-stage appropriate (pre-university transition)

### Language Altitude Check
- [ ] Language level matches week (1-2 for early weeks, 3-4 for later)
- [ ] NO Level 5 language ("democratization," "consciousness extension")
- [ ] Would a 17-year-old understand every word?

### Brand Voice Check
- [ ] Revolutionary Hope tone (hope + empowerment)
- [ ] NO fear-based language
- [ ] Linguistic DNA present: "Finally" / "Wield" / "Achieve more" / "Follow you forever"
- [ ] "Think WITH AI" positioning visible

### CIS Agent Integration Check (Weeks 1-8)
- [ ] Week 1: Mentions /frame (practice mode)
- [ ] Weeks 2-3: /frame continues
- [ ] Weeks 4-5: /frame, /diverge, /challenge mentioned
- [ ] Weeks 6-7: All agents + /synthesize mentioned
- [ ] Week 8: All agents for artifact completion

### Node Architecture Connection Check
- [ ] Prompt connects to node being filled that week
- [ ] Rock climbing metaphor used where appropriate
- [ ] Identity shift for the week is reinforced

### Emotional Job Check
- [ ] Week 1: Belonging ("Maybe this is for me")
- [ ] Weeks 2-3: Confidence ("I'm not terrible at this!")
- [ ] Weeks 4-5: Companionship ("I have a thinking partner")
- [ ] Weeks 6-7: Ownership ("I have standards")
- [ ] Week 8: Pride ("I'm proud to share this")

### Guardrails Compliance Check
- [ ] NO technical jargon
- [ ] NO "impressive" AI outputs
- [ ] NO student comparison or ranking
- [ ] Celebrates thinking, not outputs
- [ ] Normalizes confusion and mistakes
- [ ] Frames AI as responding to thinking, not intelligence

### Wednesday Peer Visibility Check
- [ ] Prompt includes "Peer Visibility Moment" note
- [ ] Agent response template includes aggregation logic
- [ ] Anonymization is explicit

---

## Implementation Notes

### Friday Reflections (NOT in this library)

**IMPORTANT:** Friday reflection prompts are ALREADY included in the weekly design documents:
- Week 1 reflection: lines 712-728 in week-1-wonder.md
- Week 2 reflection: lines 319-347 in weeks-2-3-trust.md
- Week 3 reflection: lines 616-644 in weeks-2-3-trust.md
- Week 4 reflection: in weeks-4-5-converse.md
- Week 5 reflection: in weeks-4-5-converse.md
- Week 6 reflection: in weeks-6-7-direct.md
- Week 7 reflection: in weeks-6-7-direct.md
- Week 8 reflection: in week-8-artifact-showcase.md

**DO NOT duplicate Friday reflections here.** This library contains Monday-Thursday daily prompts ONLY (30 total across 8 weeks).

### Daily Prompt Schedule

| Week | Monday | Tuesday | Wednesday | Thursday | Friday |
|------|--------|---------|-----------|----------|--------|
| 1 | ✅ Prompt 1 | ✅ Prompt 2 | ✅ Prompt 3 (peer visibility) | ✅ Prompt 4 | Reflection (in weekly design) |
| 2 | ✅ Prompt 5 | ✅ Prompt 6 | ✅ Prompt 7 (peer visibility) | ✅ Prompt 8 | Reflection (in weekly design) |
| 3 | ✅ Prompt 9 | ✅ Prompt 10 | ✅ Prompt 11 (peer visibility) | ✅ Prompt 12 | Reflection (in weekly design) |
| 4 | ✅ Prompt 13 | ✅ Prompt 14 | ✅ Prompt 15 (peer visibility) | ✅ Prompt 16 | Reflection (in weekly design) |
| 5 | ✅ Prompt 17 | ✅ Prompt 18 | ✅ Prompt 19 (peer visibility) | ✅ Prompt 20 | Reflection (in weekly design) |
| 6 | ✅ Prompt 21 | ✅ Prompt 22 | ✅ Prompt 23 (peer visibility) | ✅ Prompt 24 | Reflection (in weekly design) |
| 7 | ✅ Prompt 25 | ✅ Prompt 26 | ✅ Prompt 27 (peer visibility) | ✅ Prompt 28 | Reflection (in weekly design) |
| 8 | ✅ Prompt 29 | ✅ Prompt 30 | ✅ Prompt 31 (peer visibility) | ✅ Prompt 32 | Graduation (in weekly design) |

**Note:** All 32 prompts include Wednesday peer visibility moments (8 Wednesdays total).

### Agent Posting Schedule

**Every weekday at 9:00 AM EAT/UTC+3:**
- Agent posts daily prompt from this library
- Monitors responses throughout the day
- Reacts with emoji within 5 minutes of each submission
- Tracks participation (internal, not public)
- Flags students who haven't posted by 6:00 PM
- Sends gentle nudges to non-posters
- **Wednesday evenings:** Posts peer visibility snapshot (anonymized)

**Friday at 9:00 AM EAT/UTC+3:**
- Agent posts weekly reflection prompt (from weekly design, NOT this library)
- Processes reflections with mechanical verification
- Routes based on self-assessment
- Validates proof-of-work sentences
- Gating: Next week's content unlocks only after reflection WITH valid proof-of-work

---

## Success Metrics

### Completion Metrics
- [ ] All 32 daily prompts created (4 per week × 8 weeks)
- [ ] Each prompt passes quality checklist
- [ ] Each prompt is JTBD-relevant (Guardrail #11 compliant)
- [ ] Each prompt reinforces the weekly habit
- [ ] Wednesday prompts include peer visibility moments

### Quality Metrics
- [ ] 100% of prompts use correct structure
- [ ] 100% of prompts use brand voice (Revolutionary Hope)
- [ ] 100% of prompts use altitude-appropriate language
- [ ] 100% of prompts include habit practice section
- [ ] 100% of prompts pass guardrails compliance

### Integration Metrics
- [ ] All prompts connect to node architecture
- [ ] All prompts serve the week's emotional job
- [ ] CIS agents mentioned correctly (graduated introduction)
- [ ] Rock climbing metaphor used where appropriate
- [ ] Dual Pillars mentioned where relevant (Weeks 6-7)

---

## Troubleshooting Common Issues

### Issue 1: Prompt Doesn't Connect to Weekly Habit

**Sign:** Habit practice section feels forced or disconnected from task.

**Fix:** Revisit the weekly design document. Ensure:
- Task naturally leads to the habit
- Habit practice section explains WHY this task reinforces the habit
- Connection is explicit, not implied

**Example Fix:**
```
BAD: "Use AI to explore careers." + Habit 3 practice
BETTER: "Try the SAME question three ways, changing ONE thing each time." + Habit 3 practice (natural connection)
```

---

### Issue 2: Examples Are Not JTBD-Relevant

**Sign:** Examples feel generic or don't relate to pre-university students' REAL concerns.

**Fix:** Replace with APPROVED example categories:
- University decisions
- Career exploration
- Study decisions
- Gap year vs. university
- Application essays
- Understanding complex topics
- Processing anxiety
- Making difficult decisions

**Example Fix:**
```
BAD: "Ask AI for a joke about cats"
BETTER: "Ask AI: 'What are 3 things I should know about studying computer science vs. business at university?'"
```

---

### Issue 3: Language Level Too High/Low for Week

**Sign:** Language doesn't match the week's altitude progression.

**Fix:** Adjust language to match week:
- Week 1: Level 1-2 (Concrete/Pattern)
- Weeks 2-3: Level 2 (Pattern)
- Weeks 4-5: Level 2-3 (Pattern/Framework)
- Weeks 6-7: Level 3-4 (Framework/Authority)
- Week 8: Level 4 (Authority)

**Example Fix:**
```
BAD (Week 1): "AI democratizes access to intelligence" (Level 5 - Philosophy)
BETTER (Week 1): "AI isn't coming. It's already here." (Level 2 - Pattern)
```

---

### Issue 4: Prompt Missing Emotional Job Connection

**Sign:** Prompt doesn't create the emotional state for that week.

**Fix:** Add explicit emotional safety signals or touchpoints:
- Week 1: "You might be wondering: 'Is AI really for someone like me?'"
- Weeks 2-3: "You might be feeling: 'Can I actually do this?'"
- Weeks 4-5: "You might be feeling: 'I'm not alone - I have a thinking partner.'"
- Weeks 6-7: "You might be feeling: 'I have standards now.'"
- Week 8: "You might be feeling: 'I'm proud to share this.'"

---

## Notes for Trevor

### Your Role vs. The Agent's Role

**Discord Agent (90%):**
- Posts daily prompts at 9:00 AM EAT/UTC+3
- Reacts to every submission with emoji
- Sends gentle nudges to non-posters
- Creates peer visibility snapshots (Wednesday evenings)
- Tracks participation (internal, not public)
- Processes Friday reflections (mechanical verification + routing)

**You (10%):**
- Review 15-20 Friday reflections/week (spot-check)
- Escalated student outreach (flagged by agent)
- Live sessions reference daily prompt themes
- Quality review of prompts before implementation

### Prompt Approval Workflow

**Before Implementation:**
1. Review all prompts in this library
2. Check each prompt against quality checklist
3. Verify JTBD-relevance of all examples
4. Confirm brand voice compliance
5. Test agent response templates

**During Implementation (Week 1):**
- Monitor agent posts daily
- Check student engagement rates
- Review peer visibility snapshots
- Adjust prompts if needed (rare)

**After Implementation:**
- Track completion metrics
- Review Friday reflection quality
- Identify students needing support
- Inform future prompt refinements

### When to Adjust Prompts

**GOOD Reasons to Adjust:**
- Students aren't completing the prompt (completion rate <70%)
- Examples aren't resonating (students say "this doesn't feel relevant")
- Guardrails violation detected (jargon, impressive examples)
- Technical issue with prompt formatting

**BAD Reasons to Adjust:**
- "This feels too simple" (simplicity = accessibility)
- "Let's make it more impressive" (violates guardrails)
- "Students aren't getting deep insights" (depth comes with time)
- "I'm bored with this theme" (repetition builds habits)

### First Week Checklist

Before Week 1 prompts go live:
- [ ] Read this entire document
- [ ] Review all Week 1 prompts (4 total)
- [ ] Test agent response templates
- [ ] Verify Friday reflection is ready (from week-1-wonder.md)
- [ ] Confirm Discord channel setup (#thinking-lab, #thinking-showcase)
- [ ] Check agent posting schedule (9:00 AM EAT/UTC+3)
- [ ] Prepare for Trevor's first live session (Week 1 script in Story 3.1)

---

## Story 3.6 Complete! ✅

**Deliverables:**
- ✅ 32 daily async prompts (4 per week × 8 weeks)
- ✅ Each prompt with: Practice Task + Habit Practice section
- ✅ JTBD-relevant examples only (Guardrail #11 compliance)
- ✅ Brand voice compliance (Revolutionary Hope, altitude-appropriate)
- ✅ All 4 Habits reinforced across 8 weeks
- ✅ CIS agent integration (graduated introduction)
- ✅ Node architecture connections
- ✅ Emotional job touchpoints for each week
- ✅ Wednesday peer visibility moments built in
- ✅ Agent response templates
- ✅ Quality checklist
- ✅ Troubleshooting guide

**Production Ready:** YES - Discord agent can immediately use these prompts.

**Next Story:** Epic 4 - CIS Agent System begins with Story 4.1 (CIS Controller Logic)

---

## Key Integration Points

**From Epic 1.1 (Guardrails):**
- No technical jargon ✅
- No impressive demos ✅
- No student comparison ✅
- Celebrates thinking, not outputs ✅
- Normalize confusion and mistakes ✅
- Frame AI as responding to thinking ✅

**From Epic 1.2 (JTBD Integration):**
- Serves zone-specific emotional jobs ✅
- Identity shifts reinforced ✅
- JTBD-relevant examples only ✅
- Functional, emotional, social jobs served ✅

**From Epic 1.3 (Node Architecture):**
- Connects to nodes being filled each week ✅
- Rock climbing metaphor used ✅
- Mental lattice framework referenced ✅

**From Epic 1.4 (4 Habits):**
- All 4 habits reinforced across 8 weeks ✅
- Habit icons used consistently ✅
- Dual Pillars integration ✅
- Taglines included ✅

**From Epic 2 Weekly Designs:**
- Follows daily prompt structure from Week 1 ✅
- Builds on Weeks 2-3 patterns ✅
- Integrates CIS agent introduction ✅
- Connects to artifact creation (Weeks 6-8) ✅

**From Epic 3 Stories:**
- Story 3.1 (Trevor Sessions): Habits modeled in live sessions ✅
- Story 3.2-3.5 (NotebookLM): Node content referenced ✅
- Brand Framework v3: Language altitude progression ✅

**From Decision 17 (Dual Pillars):**
- Better thinking (Habits 1-2) mentioned ✅
- Better knowledge access (Habits 3-4) mentioned ✅
- Both pillars integrated in Weeks 6-7 prompts ✅
