# Adversarial Review: Story 2.4 (Weeks 6-7 Direct)

**Reviewer:** Maya - Design Thinking Maestro
**Date:** 2026-01-24
**Review Type:** ADVERSARIAL - Finding gaps, weaknesses, and violations
**Severity Framework:**
- 🔴 CRITICAL - Must fix before deployment
- 🟡 MAJOR - Should fix to prevent student failure
- 🟢 MINOR - Nice to have improvements

---

## Executive Summary

**Overall Assessment:** Story 2.4 is 75% production-ready but has SEVERAL critical gaps that will cause student failure in Weeks 6-7.

**Key Findings:**
- 🔴 4 Critical issues (guardrail violations, missing scaffolding)
- 🟡 7 Major issues (weak examples, inadequate support systems)
- 🟢 5 Minor issues (language refinements, consistency)

**Deployment Recommendation:** PAUSE - Fix critical issues before student deployment.

---

## 🔴 CRITICAL ISSUES (Must Fix)

### 1. Guardrail #11 Violations - Examples Not JTBD-Relevant

**Location:** Throughout Node 3.1-3.4, Daily Prompts

**Guardrail #11 Requirements (from Story 1.1 + 1.3):**
> "Every node example must pass the 'Would this matter to them?' test"
> "APPROVED: University applications, study techniques, career exploration, decision-making, understanding complex topics, processing anxiety"
> "PROHIBITED: Pet poems, random jokes, silly scenarios, middle school level examples"

**Violations Found:**

**Node 3.1 (Line 779-869):**
- Line 811-816: Essay direction example - GOOD (JTBD-relevant)
- Line 819-831: Decision example - TOO GENERIC. Mentions universities but doesn't show student's actual anxiety/context
- Line 853-856: Lists "personal statements, study decisions, difficult conversations" but doesn't show concrete examples WITH student's real situation

**Daily Prompts - Week 6:**
- Line 161-178: "Ask AI to create something for you" - What something? Too vague for pre-university students who don't know what to create
- Line 152-154: Task instructions don't give concrete examples relevant to their life transition

**Impact:** Students will feel disconnected from content. Examples feel fabricated, not lived.

**Fix Required:**
- Rewrite ALL examples to show specific pre-university student situations
- Include student's actual anxiety, context, constraints
- Show examples like: "I'm choosing between computer science and business but I'm worried I'll struggle with the math in CS while feeling bored in business"

---

### 2. Artifact Launch Lacks Critical Scaffolding

**Location:** Week 6 Wednesday (Line 252-304), Artifact structure (Line 628-648)

**Problem:** Artifact is introduced but students get ZERO help with the hardest part: "What question should I wrestle with?"

**Current Design:**
```markdown
Task: Use AI to think through a real decision you're facing.

Post: One insight AI helped you see about your decision.
```

**Missing Components:**
1. NO brainstorming prompts to help students identify a meaningful question
2. NO examples of good artifact questions vs. bad ones
3. NO connection to their actual JTBD (anxiety about university, career, identity)
4. NO scaffold for students who say "I don't know what to choose"

**From JTBD Integration (Story 1.2, Line 366-376):**
> "Emotional Job: Help me stop feeling anxious and start feeling like I belong"
> "Functional Job: Help me move from confusion to clarity"

The artifact should SERVE these jobs. Current design doesn't.

**Impact:** 30-40% of students will freeze at "I don't know what to write about." High failure risk.

**Fix Required:**
- Add "Question Discovery Prompts" BEFORE artifact launch
- Give 5-10 example questions modeled from real student situations
- Show "good question" vs "weak question" comparison
- Scaffold: Start with → "What's a decision you're avoiding?" → "What makes it hard?" → "Turn it into a question"

---

### 3. Week 6 Wednesday Overload - Too Much New Content

**Location:** Week 6 Wednesday (Line 252-304)

**Problem:** Wednesday introduces:
1. Node 3.2 ("I Have Opinions About Quality")
2. Habit 4 full decision-making pattern (6 steps!)
3. Artifact creation (major new ask)
4. Self-direction with all 4 CIS agents

**Cognitive Load Analysis:**
- Week 6 Monday-Tuesday: Node 3.1 + /synthesize introduction (manageable)
- Week 6 Wednesday: Node 3.2 + Habit 4 pattern + artifact kickoff (OVERWHELMING)

**From Guardrails (Story 1.1, Line 92-96):**
> "Normalize confusion ('this is normal')"
> "Celebrate thinking, not speed/accuracy"
> "Create psychological safety"

This design creates pressure, not safety.

**Impact:** Students will feel overwhelmed. Many will skip steps. Habit 4 won't stick.

**Fix Required:**
- Move Node 3.2 to Thursday
- Make Wednesday ONLY about Habit 4 decision pattern
- Keep artifact kickoff on Wednesday but simplify: "Just identify your question today"
- Spread the load across the week

---

### 4. /synthesize Introduction Doesn't Show Value

**Location:** Week 6 Tuesday (Line 198-249)

**Problem:** Students won't understand WHY they need /synthesize. The explanation is abstract.

**Current Description:**
```markdown
What /synthesize does:
Takes your rough ideas and AI conversations, then helps you write them clearly.
```

**Missing:**
- NO concrete before/after example showing /synthesize in action
- NO connection to artifact (which they'll need /synthesize for)
- NO differentiation from just "asking AI to summarize"

**From Node Architecture (Story 1.3, Line 131-136):**
> "Concept:** Meta-awareness (explaining to AI helps you think)"
> "Experience:** 'When I explained this to AI, I realized I actually meant...'"

/synthesize should show this meta-awareness. Current description doesn't.

**Impact:** Students will ignore /synthesize, then struggle with artifact writing.

**Fix Required:**
- Add explicit before/after: "Here's my messy thinking → /synthesize → Here's my clarified thinking"
- Show artifact section example: "Rough AI conversation → /synthesize → Clear artifact section"
- Emphasize: "/synthesize doesn't ADD ideas. It clarifies YOUR ideas"

---

## 🟡 MAJOR ISSUES (Should Fix)

### 5. Weak Connection to Habits 1-3

**Location:** Throughout Weeks 6-7

**Problem:** Habit 4 is introduced but there's NO explicit acknowledgment that Habits 1-3 are the foundation.

**From 4 Habits Branding (Story 1.4, Line 70):**
> "**Key Insight:** Habit 1 (Pause) + Habit 2 (Context) + Habit 3 (Iterate) → Habit 4 (Think First). You pause, explain, iterate, THEN you direct AI to help you decide."

**Current Design:**
- Line 276-281: Lists all 4 habits in decision pattern
- But doesn't EXPLAIN how they build on each other
- Doesn't celebrate that students already have Habits 1-3

**Impact:** Habit 4 feels like "one more thing" instead of "capstone of what you've built."

**Fix Required:**
- Add explicit celebration: "You've already built Pause, Context, Iterate. Habit 4 ties them together."
- Show visual: How Habits 1-3 feed into Habit 4
- Reinforce: "You're not learning 4 separate things. You're building one integrated thinking system"

---

### 6. No Examples of Completed Artifacts

**Location:** Artifact structure (Line 628-648), Artifact Sprint (Line 620-674)

**Problem:** Students see the structure but have NO model of what "good" looks like.

**What's Missing:**
- NO complete artifact example (even a fictional one)
- NO "good artifact" vs "weak artifact" comparison
- NO rubric for quality (beyond "shows YOUR thinking")

**From Guardrails (Story 1.1, Line 99-100):**
> "Example is relatable, not impressive"
> "Show specific before/after comparisons"

**Impact:** Students will either:
- Freeze: "I don't know if mine is good enough"
- Perform: "Make it sound smart/impressive" (violates guardrails)
- Copy: Follow the template exactly without authentic thinking

**Fix Required:**
- Add 2 complete example artifacts (fictional but realistic)
- Show artifact from student who "gets it" (shows thinking, not AI output)
- Show weak artifact example (template-filling, generic insights)
- Add quality guide: "Signs your artifact shows YOUR thinking"

---

### 7. Daily Prompts Lack Specificity

**Location:** Daily prompts throughout Weeks 6-7

**Problem:** Many prompts give vague instructions without concrete examples.

**Examples:**

**Week 6 Monday (Line 152-178):**
```markdown
Task: Ask AI to create something for you - then actively direct it.
```
- What something? Too vague.

**Week 6 Thursday (Line 310-335):**
```markdown
Task: Use ALL FOUR tools to work through something real.
```
- What something real? No examples given.

**Week 7 Monday (Line 465-494):**
```markdown
Task: Try ONE direction technique with AI today.
```
- No example of what "try" looks like in practice.

**From Node Architecture (Story 1.3, Line 194-200):**
> "Concrete Experience, Not Abstract Concept"
> "Use 'try this' examples, not 'here's a principle'"
> "Show specific before/after comparisons"

**Impact:** Students will skip tasks or do them superficially. Low engagement.

**Fix Required:**
- Add concrete example to EVERY daily prompt
- Format: "Here's what this looks like: [specific 2-3 line example]"
- Model the output you want from them

---

### 8. Trevor's Session Scripts Don't Model Guardrails

**Location:** Week 6 Session (Line 1251-1337), Week 7 Session (Line 1339-1437)

**Problem:** Scripts are lecture-heavy, don't model the "what did YOU notice?" framework enough.

**From Guardrails (Story 1.1, Line 126-128):**
> "Trevor live session scripts follow 'no jargon Week 1' rule"
> "Models the framework ('what did YOU notice?')"

**Current Issues:**
- Week 6: Trevor demonstrates Habit 4 (Line 1274-1297) but it's a DEMO, not student exploration
- Week 7: Trevor demonstrates all 4 habits (Line 1358-1396) but again, it's showing, not asking
- Only 20 minutes for "Student Sharing" (Line 1268) vs 15-30 minutes of Trevor content

**Impact:** Sessions feel like lectures, not collaborative exploration. Violates "design WITH students not FOR them" principle.

**Fix Required:**
- Flip ratio: 30-35 min student sharing, 10-15 min Trevor modeling
- Add more "What did YOU notice?" prompts
- Have students demonstrate to each other, not just Trevor demonstrating
- Make Trevor's demos shorter and more interactive

---

### 9. Success Metrics Are Superficial

**Location:** Success Metrics (Line 1528-1574)

**Problem:** Metrics focus on COMPLETION, not TRANSFORMATION.

**Current Metrics:**
- "90%+ students complete daily prompts"
- "70%+ try /synthesize at least once"
- "60%+ can describe directing AI"

**What's Missing:**
- NO measure of actual director identity formation
- NO measure of ownership standards developing
- NO quality check on artifact depth of thinking
- NO emotional job check: Do they feel less anxious? More capable?

**From JTBD Integration (Story 1.2, Line 366-376):**
> "Emotional Job: 'Help me stop feeling anxious and start feeling like I belong'"
> "Functional Job: 'Help me move from confusion to clarity'"

**Impact:** Success looks like "they did the tasks" not "they transformed." False positive.

**Fix Required:**
- Add transformation metrics:
  - "% who can say 'I made this' and mean it"
  - "% who report feeling less anxious about AI decisions"
  - "% who demonstrate ALL 4 habits in artifact (not just mention them)"
  - "% whose artifact shows unique thinking (not template-filling)

---

### 10. No Support for Struggling Students

**Location:** Entire Weeks 6-7 design

**Problem:** Design assumes all students are progressing at same pace. NO safety net for students who say "I don't get it."

**What's Missing:**
- NO escalation triggers beyond "3 days silent" (already in design)
- NO "stuck" patterns to watch for
- NO optional remedial content for students struggling with direction
- NO peer support system (buddies, small groups)

**From Guardrails (Story 1.1, Line 124-125):**
> "Create psychological safety"
> "Private process, public product (Discord hybrid model)"

**Impact:** Students who fall behind will just disengage. High attrition risk.

**Fix Required:**
- Add "Stuck Student Patterns" section to agent behavior specs:
  - "If student posts generic output 3x in a row → Send private encouragement: 'Let's make this about YOUR situation'"
  - "If student never uses direction techniques → Offer 1:1 support"
- Add optional "direction practice" exercises for students wanting more scaffolding
- Create peer support system: "Direction buddy pairs" for Week 7

---

### 11. Node Content Language Inconsistencies

**Location:** Node 3.1-3.4 host guides (Line 794-1243)

**Problem:** Language sometimes drifts to Level 4-5 (too abstract) when it should be Level 3 (Framework) for pre-university students.

**Examples:**

**Node 3.2 (Line 937-938):**
```markdown
Host A: "You're developing taste. Standards. Judgment."
```
- "Judgment" is abstract. Better: "You're learning to say 'this isn't good enough for me'"

**Node 3.4 (Line 1198-1199):**
```markdown
Host A: "You're saying 'I'm a director. I think WITH AI.'"
```
- "I think WITH AI" is Level 5 philosophy language. Too abstract for Week 6-7.

**From JTBD Altitude System (Story 1.2, Line 355-357):**
> "Level 3 (Framework - System/Structure): 'Mental models for WHEN/HOW/WHY to use AI'"
> "Level 4 (Transformation): 'Students learn to think WITH AI'"

**Problem:** Pre-uniformity students are in Zone 3→4. They need Level 3 language, not Level 4-5 philosophy.

**Impact:** Content will feel disconnected. Students will tune out.

**Fix Required:**
- Review all host guide dialogue through JTBD altitude lens
- Replace abstract terms with concrete equivalents:
  - "Judgment" → "Knowing what you want"
  - "Think WITH AI" → "Use AI to help you think"
  - "Director identity" → "You're in charge of the outcome"

---

## 🟢 MINOR ISSUES (Nice to Have)

### 12. Peer Visibility Moments Could Be Richer

**Location:** Throughout daily prompts

**Enhancement:** Current anonymized quotes are good (follows guardrails). Could add brief "what this shows" to make learning explicit.

**Example enhancement:**
```markdown
"Asked for a study schedule → Got generic plan → Directed toward my learning style → Got something actually usable"

**What this shows:** You didn't accept generic. You directed toward YOUR needs. That's the director mindset.
```

### 13. Weekend Challenges Could Be More Invitational

**Location:** Week 6 Saturday (Line 398-423), Week 7 Saturday (Line 732-771)

**Current:** Weekend challenges feel like one more task.

**Enhancement:** Make them truly optional and playful:
```markdown
🧠 WEEKEND REFLECTION (totally optional, just for fun):

Notice yourself this weekend making any choice or decision.

Just observe: "Could I use AI to think through this?"

No need to actually DO it. Just NOTICE your thinking.

That mental rehearsal? That's Habit 4 becoming part of how you approach the world.

💭 OR: Take the weekend off! Integration happens when you rest too.
```

### 14. Agent Response Templates Could Be More Personalized

**Location:** Agent behavior specs (Line 1449-1524)

**Enhancement:** Templates are good but could acknowledge student's individual journey more:

**Current:**
```markdown
"You're directing AI toward your vision! That's the director mindset."
```

**Enhanced:**
```markdown
"You're directing AI toward YOUR vision [specific thing they mentioned]. That's the director mindset forming - you know what you want."
```

### 15. No Closure Ritual for Weeks 6-7

**Location:** End of Week 7 (Line 730-771)

**Enhancement:** Add a brief ritual marking the transition from "building skills" to "showcasing growth":

```markdown
🎉 WEEKS 6-7 CLOSING RITUAL:

You've spent 7 weeks building.
Pause for 30 seconds and acknowledge:

"I'm different than I was in Week 1."

What's ONE way you're different?

Post it (or just say it to yourself).

Then rest. Week 8 is about celebration, not building. You're ready.
```

### 16. Trevor Session Closing Scripts Could Be More Memorable

**Location:** Week 6 closing (Line 1322-1337), Week 7 closing (Line 1422-1437)

**Enhancement:** Add a memorable hook or phrase students can take away:

**Week 6 closing enhancement:**
```markdown
"For now: Notice when you direct AI naturally.

That's the director identity forming.

Here's your Week 6 takeaway:

'First drafts are raw material. I direct until it matches my vision.'

Carry that with you. See you in Discord. 🧠"
```

---

## Summary of Required Actions

### Before Deployment (Must Fix):
1. ✅ Rewrite ALL examples to be JTBD-relevant (show actual pre-university student situations with anxiety/context)
2. ✅ Add artifact scaffolding (question discovery prompts, example artifacts, quality guide)
3. ✅ Redistribute Week 6 Wednesday cognitive load (move Node 3.2 to Thursday)
4. ✅ Add concrete before/after examples to /synthesize introduction

### High Priority (Should Fix):
5. ✅ Explicitly connect Habit 4 to Habits 1-3 (show how they build)
6. ✅ Add complete example artifacts (good vs. weak comparison)
7. ✅ Add concrete examples to ALL daily prompts
8. ✅ Flip Trevor sessions to more student sharing, less Trevor demo
9. ✅ Add transformation metrics (not just completion metrics)
10. ✅ Add support system for struggling students
11. ✅ Review and lower language altitude (replace Level 4-5 terms with concrete Level 3 language)

### Nice to Have (Future Improvements):
12. Enhance peer visibility moments with explicit learning
13. Make weekend challenges truly optional and playful
14. Personalize agent response templates more
15. Add Weeks 6-7 closure ritual
16. Add memorable takeaway phrases to Trevor sessions

---

## Design Thinking Reflection

**As a design thinking coach, I'm asking:**

**Empathy:** Who is being left out of this design?
- Students who don't know what to write about for artifact
- Students overwhelmed by Wednesday's cognitive load
- Students who don't see themselves in generic examples

**Ideation:** What if we tried...
- Artifact question discovery starts in Week 5 (not Week 6)
- Daily prompts ALL include "Here's what this looks like" examples
- Peer support system from Week 1 (not just escalation when stuck)

**Prototyping:** Test this with 5-10 real students:
- "Show me where you'd get stuck in Week 6"
- "What question would you choose for your artifact?"
- "Does this example feel real or fake?"

**Testing:** After fixes, validate:
- Do students see themselves in the examples?
- Can they identify an artifact question without scaffolding?
- Does Habit 4 feel like capstone or "one more thing"?

---

## Final Recommendation

**Story 2.4 has strong bones.** The two-week structure, node progression, and CIS agent integration are all well-designed.

**BUT:** The critical issues around example quality and artifact scaffolding will cause student failure. Pre-university students facing real anxiety about their future need content that speaks to THEIR lived experience, not generic placeholders.

**Deployment Decision:** PAUSE deployment. Fix the 4 critical issues, then reassess. With fixes, this could be excellent. Without them, we risk alienating the students we most want to serve.

---

**Reviewer Sign-off:**
Maya - Design Thinking Maestro
"Design is about THEM, not us. These students are facing real transitions. Our examples must honor that reality."

**Next Steps:**
1. Team review of critical issues
2. Prioritization discussion
3. Revision of Story 2.4
4. Re-review before deployment
