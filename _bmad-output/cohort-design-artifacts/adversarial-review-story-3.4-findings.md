# Adversarial Review: Story 3.4 (NotebookLM Master Prompt - Zone 2→3)

**Reviewer:** Maya (Design Thinking Coach)
**Date:** 2026-01-25
**Story Status:** ready-for-dev
**Review Type:** ADVERSARIAL - Find 3-10 specific issues

---

## Executive Summary

Story 3.4 is **STRONG** overall but has **5 CRITICAL issues** requiring immediate fixes:

1. ❌ **CRITICAL:** Habit 3 branding inconsistency - missing canonical tagline and inconsistent icon usage
2. ❌ **CRITICAL:** Mental lattice architecture language under-emphasized
3. ⚠️ **MODERATE:** Node-specific sections lack Trevor's workflow clarity
4. ⚠️ **MODERATE:** Connection to Story 2.3 (Weeks 4-5 design) could be more explicit
5. ✅ **MINOR:** Opportunity to strengthen Habit 3 → Democratized Expertise connection

**Overall Assessment:** Production-blocked until CRITICAL issues resolved. After fixes: READY.

---

## Issue 1: Habit 3 Branding Inconsistency (CRITICAL)

### Problem

**From Epic 1.4 (four-habits-brand.md) - Canonical Habit 3 Branding:**
- **Tagline:** "See what each change does"
- **Icon:** 🔄 Iteration loop
- **Zone Focus:** 2→3 (Converse)
- **Dual Pillar:** Democratized Expertise (better knowledge through experimentation)

**In Story 3.4:**

Line 163 (Master Prompt):
```
**CIS AGENT INTEGRATION (Critical for Weeks 4-5):**
Students have access to THREE thinking tools this week...
This scaffolds Habit 3 (Change one thing at a time) by giving students tools to practice iterative thinking.
```

### The Issue

1. **Tagline Missing:** The canonical Habit 3 tagline "See what each change does" appears **ZERO times** in Story 3.4
2. **Icon Inconsistent:** 🔄 appears in master prompt (line 163) but not consistently throughout all node-specific sections
3. **Brand Deviation:** "Change one thing at a time" is the habit NAME, not the tagline. The canonical tagline from Epic 1.4 is "See what each change does"

### Evidence

**Epic 1.4, lines 79-103:**
```markdown
### Habit 3: CHANGE ONE THING AT A TIME
**Tagline:** "See what each change does"
**Icon:** 🔄 Iteration loop
**Zone Focus:** 2→3 (Converse)
**Dual Pillar:** Democratized Expertise (better knowledge access)

**What It Is:**
When refining AI responses, change ONE element at a time to see what affect it has.

**Why It Matters:**
- Transforms "fix this" into "let's experiment"
- Teaches iterative thinking and cause-effect reasoning
- Prevents overwhelming AI with too many directions at once
```

**Story 3.4, line 163:**
```
This scaffolds Habit 3 (Change one thing at a time) by giving students tools to practice iterative thinking.
```

**Story 3.4, line 496 (Node 2.1):**
```
EMOTIONAL SAFETY SIGNAL:
"I know some of you might be wondering: 'Do I really need to add context iteratively? Can't I just say everything at once?'" Let me tell you: When you change one thing at a time, you can see WHAT DIFFERENCE that specific context made. That's clarity."
```

The phrase "see WHAT DIFFERENCE that specific context made" is **CLOSE** to the tagline but not the exact canonical "See what each change does."

### Impact

- **Brand Integrity:** Violates Epic 1.4's canonical branding
- **Consistency:** Students won't see consistent Habit 3 language across components
- **Graduation Artifact:** The 4 Habits graduation card uses "See what each change does" - students won't recognize it from podcasts

### Required Fix

**Add to Master Prompt (after line 48):**
```
**HABIT 3 BRANDING (Critical):**
This week reinforces Habit 3: Change One Thing At A Time 🔄
Tagline: "See what each change does"
Mention this tagline in EVERY episode: "When you change one thing at a time, you see what each change does. That's the insight."

Icon usage: Include 🔄 throughout when mentioning Habit 3.
```

**Update all 4 node-specific variations to include:**
- Canonical tagline: "See what each change does"
- Consistent 🔄 icon usage

---

## Issue 2: Mental Lattice Architecture Language Under-Emphasized (CRITICAL)

### Problem

**From Epic 1.3 (node-architecture.md), lines 10-18:**
```markdown
## THE CORE CONCEPT: MENTAL LATTICE

**From Cartographer's Manifesto:** Learning isn't linear (A→B→C). It's a **lattice** - interconnected concepts that form a mental structure students can climb through.

**Decision 10 (Node-Based Architecture):** Mental lattice filled by specific nodes at each zone/shift.

**Visual Metaphor:** Think of it like rock climbing:
- **The wall** = The AI territory map (zones 0-4)
- **The holds** = Nodes (specific concepts, experiences, insights)
- **The route** = Each student's unique journey through the lattice
- **The summit** = Zone 4 (director identity)
```

**From Epic 1.3, lines 54-58:**
```markdown
**Node 2.1: "Context changes everything"**
- **Concept:** Vague vs. rich comparison (same question, different context = different answer)
- **Experience:** "Watch how the AI's response shifts when we add context"
- **Identity Shift:** "AI just answers" → "AI responds to my situation"
- **Delivery:** NotebookLM podcast: "The Context Superpower"
```

### The Issue

Story 3.4 mentions "mental lattice" but doesn't:
1. Explain the lattice metaphor clearly for NotebookLM hosts
2. Connect each node to the "holds on the wall" metaphor
3. Emphasize that nodes are interconnected, not isolated

**Story 3.4, line 55:**
```
**NODE ARCHITECTURE LANGUAGE:**
Use this structural metaphor: "This week you're filling 4 more nodes in your mental lattice." A mental lattice is like a knowledge framework you're building, one node at a time.
```

This is a **simplified explanation** ("knowledge framework") that loses the rock climbing metaphor from Epic 1.3.

### Evidence

**Epic 1.3, line 15:**
```markdown
**Visual Metaphor:** Think of it like rock climbing:
- **The wall** = The AI territory map (zones 0-4)
- **The holds** = Nodes (specific concepts, experiences, insights)
```

**Story 3.4 never mentions:**
- "Rock climbing" metaphor
- "The wall" or "The holds"
- That nodes are interconnected (lattice structure)
- That this builds toward Zone 4 (the summit)

### Impact

- **Architectural Clarity:** Students miss the mental model that nodes are interconnected, building toward a summit
- **Motivation:** The "rock climbing" metaphor is more inspiring than "knowledge framework"
- **Framework Purity:** Epic 1.3 established this metaphor - Story 3.4 dilutes it

### Required Fix

**Enhance Master Prompt (lines 54-58):**
```
**NODE ARCHITECTURE LANGUAGE (Critical Metaphor):**
Use the rock climbing metaphor from Epic 1.3:
- "This week you're grabbing 4 more holds on the AI territory wall"
- "Each node is like a handhold or foothold that helps you climb"
- "These holds aren't isolated - they're part of your mental lattice, a structure you're building"
- "Zone 2 is down here, Zone 3 is up there - these nodes help you climb from one to the other"
- "By Zone 4 (the summit), you'll have 16 holds in your lattice - enough to climb confidently"

Explain: "A mental lattice is like a climbing wall. You don't go straight up - you place holds strategically, building a structure that supports your climb. That's what these 4 nodes are doing."
```

**Add to each node-specific section:**
- Explicit connection to "climbing from Zone 2 to Zone 3"
- Reinforce that this node is "one hold in your lattice"

---

## Issue 3: Node-Specific Sections Lack Trevor Workflow Clarity (MODERATE)

### Problem

Each of the 4 node-specific variations (Node 2.1 through 2.4) has an "Add to master prompt:" section, but it's unclear:

1. **Does Trevor COPY the master prompt, then PASTE the node-specific addition?**
2. **Or does Trevor REPLACE sections of the master prompt?**
3. **What's the exact workflow for generating all 4 podcasts?**

### Evidence

**Story 3.4, line 133 (Node 2.1):**
```markdown
### Node 2.1: "Context Changes Everything"

**Add to master prompt:**
```
SPECIFIC FOCUS FOR THIS EPISODE:
Show them that the same question with different context gets completely different answers.
...
```

**Story 3.4, line 481 (Production Workflow):**
```markdown
### Step 2: Upload & Configure (5 minutes)
1. Upload source material to NotebookLM
2. Copy-paste master prompt + node-specific variation
3. Set "instructions to hosts"
```

Line 484 says "master prompt + node-specific variation" but line 133 says "Add to master prompt" - these are different instructions!

### Impact

- **Usability:** Trevor may be confused about how to combine master prompt with node-specific content
- **Production Errors:** Risk of accidentally omitting master prompt sections when adding node-specific content
- **Efficiency:** Unclear workflow wastes time in podcast generation

### Required Fix

**Clarify the exact workflow:**

**Option A: Append Method (Preferred)**
```markdown
### Step 2: Upload & Configure (5 minutes)
1. Upload source material to NotebookLM
2. Copy the ENTIRE master prompt (lines 29-125)
3. Then PASTE the node-specific variation for the node you're generating
4. The result: Master prompt content + node-specific addition in "instructions to hosts" field
5. Set duration: 8-12 minutes

**Example for Node 2.1:**
[Copy master prompt lines 29-125]
[Paste Node 2.1 specific content]
[Submit to NotebookLM]
```

**Option B: Include Workflow in Each Node Section**
Add to each node section:
```markdown
**GENERATION WORKFLOW:**
1. Copy master prompt (lines 29-125 of this document)
2. Append this "Add to master prompt" section to the end
3. Paste combined text into NotebookLM "instructions to hosts"
4. Generate podcast
```

---

## Issue 4: Connection to Story 2.3 Could Be More Explicit (MODERATE)

### Problem

Story 3.4 mentions "See Epic 2, Story 2.3 (Weeks 4-5 Design)" in a few places, but doesn't:

1. Reference the **daily prompts** from Story 2.3 that relate to each node
2. Cross-reference **Trevor's live session topics** for the week
3. Connect to the **Friday reflection requirements** (proof-of-work)

### Evidence

**Story 2.3 (Weeks 4-5 Design) has:**
- Week 4 Monday prompt: "The Iteration Experiment" (relates to Node 2.1)
- Week 4 Wednesday prompt: "Meet /challenge" (relates to Node 2.2)
- Week 4 Friday: Required to paste conversation thread showing iteration
- Week 5 Monday prompt: "The Clarification Effect" (relates to Node 2.3)
- Week 5 Wednesday prompt: "Track Your Conversation Arc" (relates to Node 2.4)

**Story 3.4 references Story 2.3 only twice:**
- Line 53: "You'll explore this more in your live session this week."
- Line 336: "Source: `playbook-v2/02-weekly-design/weeks-4-5-converse.md`"

### Impact

- **Integration:** Podcasts feel disconnected from daily prompts students receive
- **Reinforcement:** Students might not see how podcast content connects to their daily practice
- **Trevor's Workflow:** Trevor has to manually cross-reference to align podcast content with weekly activities

### Required Fix

**Add to each node-specific section:**

**Node 2.1 (Monday Week 4):**
```markdown
**WEEK 4 CONNECTION (From Story 2.3):**
This podcast drops on Monday, Week 4.
**Daily Prompt Monday:** "The Iteration Experiment" - reinforces this node's message
**Trevor's Session Week 4:** Will demonstrate Habit 3 iteration live
**Friday Reflection:** Students must paste iteration conversation thread (proof-of-work)

Mention in podcast: "You'll practice this in today's daily prompt, and we'll explore it more in Trevor's live session this week."
```

**Node 2.2 (Wednesday Week 4):**
```markdown
**WEEK 4 CONNECTION (From Story 2.3):**
This podcast drops on Wednesday, Week 4.
**Daily Prompt Wednesday:** "Meet /challenge" - introduces /challenge agent (mentioned in this podcast)
**Trevor's Session Week 4:** Will demo /diverge and /challenge agents

Mention in podcast: "Today's daily prompt introduces /challenge - try it after you listen!"
```

**Node 2.3 (Monday Week 5):**
```markdown
**WEEK 5 CONNECTION (From Story 2.3):**
This podcast drops on Monday, Week 5.
**Daily Prompt Monday:** "The Clarification Effect" - practices meta-awareness from this node
**Trevor's Session Week 5:** All three habits integration demonstration

Mention in podcast: "Today's prompt will help you notice when explaining clarifies YOUR thinking."
```

**Node 2.4 (Wednesday Week 5):**
```markdown
**WEEK 5 CONNECTION (From Story 2.3):**
This podcast drops on Wednesday, Week 5.
**Daily Prompt Wednesday:** "Track Your Conversation Arc" - practices full arcs from this node
**Trevor's Session Week 5:** Artifact preview (conversation arcs become artifact evidence)

Mention in podcast: "Today's daily prompt will help you track your own conversation arcs."
```

---

## Issue 5: Strengthen Habit 3 → Democratized Expertise Connection (MINOR)

### Problem

**From Epic 1.4, lines 179-181:**
```markdown
### Pillar 2: Democratized Expertise
**Habits 3 & 4 = Better Knowledge Access**
- **Habit 3 (Iterate):** Refines knowledge through experimentation
```

**Story 3.4, line 47:**
```
1. **Better Knowledge Access** (Democratized Expertise) - They're learning to explore and iterate (Habit 3) to access deeper knowledge
```

This connection is present but could be **stronger and more explicit** in each node.

### The Issue

Students need to understand **WHY iteration connects to better knowledge access**. Current explanation:

**Node 2.1, line 143:**
```
This node demonstrates Democratized Expertise - iteration helps you access knowledge tailored to YOUR specific situation.
Mention: "When you iterate by changing one context element at a time, you're accessing better knowledge. That's Democratized Expertise. You're also developing better thinking through Habit 3."
```

This is good, but doesn't explain the **mechanism**: WHY does iteration give better knowledge access?

### Evidence

**Epic 1.4, line 86:**
```markdown
**Why It Matters:**
- Transforms "fix this" into "let's experiment"
- Teaches iterative refinement and cause-effect reasoning
- Prevents overwhelming AI with too many directions at once
```

The key insight: **Iteration teaches you HOW context shapes AI's knowledge**. Each iteration is a learning moment about the relationship between context and knowledge quality.

### Impact

- **Conceptual Understanding:** Students may not grasp WHY iteration = better knowledge
- **Dual Pillars Integration:** Weaker connection between Habit 3 and Pillar 2
- **Philosophy Depth:** Misses opportunity to deepen "Think WITH AI" understanding

### Required Fix (Optional Enhancement)

**Add to Master Prompt (after Dual Pillars section, line 48):**
```
**WHY ITERATION = BETTER KNOWLEDGE ACCESS:**
Explain the mechanism: "When you change one thing at a time, you learn HOW each context element shapes AI's response. You're not just getting better answers - you're learning the relationship between context and knowledge. That's Democratized Expertise through experimentation."

Example: "If you change three things at once, you get a better answer but you didn't learn WHY. If you change one thing, you see 'Oh, THAT'S what that context does!' - now you understand how AI's knowledge responds to your situation. That's expertise."
```

**Add to each node-specific section as relevant:**

**Node 2.1:**
```markdown
**DUAL PILLARS DEEP DIVE:**
"When you iterate by changing context, you're not just accessing knowledge - you're learning HOW to access knowledge. Each iteration teaches you: 'When I add THIS context, AI responds in THAT way.' That's not just getting answers - that's building expertise in knowledge access. That's Habit 3 developing Pillar 2 (Democratized Expertise)."
```

**Node 2.2:**
```markdown
**DUAL PILLARS DEEP DIVE:**
"Conversations aren't just better answers - they're better knowledge access because you're learning THROUGH the dialogue. Each exchange teaches you how to steer AI toward what you need. That's not just knowledge - that's expertise in knowledge access."
```

**Node 2.3:**
```markdown
**DUAL PILLARS DEEP DIVE:**
"When explaining to AI clarifies YOUR thinking, you're not just getting knowledge - you're building metacognition. You're learning HOW you learn, how you think, how you understand. That's Democratized Intelligence AND Expertise working together through Habit 3."
```

**Node 2.4:**
```markdown
**DUAL PILLARS DEEP DIVE:**
"The conversation arc isn't just about ending with precise knowledge - it's about learning the PATH to precision. Each iteration is a lesson in how to access knowledge effectively. You're not just using AI - you're developing expertise in knowledge access through iterative refinement."
```

---

## What's Working Well (Strengths to Preserve)

Before listing fixes, let's acknowledge what Story 3.4 does **EXCELLENTLY**:

✅ **Guardrails Compliance:**
- No technical jargon (Guardrail #3)
- No impressive examples (Guardrail #3)
- JTBD-relevant examples only (Guardrail #11)
- Psychological safety signals throughout (Guardrail #4)

✅ **CIS Agent Integration:**
- Mentions /diverge and /challenge appropriately
- Connects agents to Habit 3 practice
- Doesn't overwhelm (Story 2.3 introduces both agents Week 4)

✅ **Podcast Structure:**
- Clear 8-12 minute duration
- Conversational two-host format specified
- Storytelling approach emphasized over lecturing

✅ **Quality Checklist:**
- Comprehensive 15-point checklist
- Covers identity shift, emotional job, habit reinforcement
- Includes guardrails compliance verification

✅ **Production Workflow:**
- Clear step-by-step for Trevor
- Troubleshooting section for common issues
- Success metrics defined

✅ **Node Specifications:**
- All 4 nodes from Epic 1.3 represented
- Identity shifts clear
- Emotional jobs addressed
- JTBD-aligned examples

**These strengths should NOT be changed.** Only fix the issues identified above.

---

## Prioritized Fix List

### Must Fix (Production Blockers):
1. **Issue 1:** Add canonical Habit 3 tagline "See what each change does" throughout
2. **Issue 1:** Ensure consistent 🔄 icon usage
3. **Issue 2:** Enhance mental lattice architecture language with rock climbing metaphor

### Should Fix (Quality Improvements):
4. **Issue 3:** Clarify Trevor's workflow for combining master prompt + node-specific content
5. **Issue 4:** Add explicit connections to Story 2.3 daily prompts and live sessions

### Nice to Have (Enhancements):
6. **Issue 5:** Strengthen Habit 3 → Democratized Expertise connection with mechanism explanation

---

## Recommended Next Steps

1. **Trevor reviews this adversarial review** and confirms which issues to address
2. **Maya facilitates party mode** with relevant agents (Paige, Winston, Mary) to discuss fixes
3. **Consensus reached** on which fixes to apply
4. **Apply fixes** to Story 3.4
5. **Re-review** against Epic 1 foundational documents
6. **Mark Story 3.4 complete** and update sprint-status.yaml

---

**Review Status:** COMPLETE - 5 issues identified (2 critical, 2 moderate, 1 minor)

**Recommendation:** Fix CRITICAL issues (1-2) before production use. MODERATE issues (3-4) strongly recommended. MINOR issue (5) optional enhancement.

**Next Action:** Launch party mode to discuss fixes with team.

---

*Generated by adversarial review process - designed to challenge assumptions and find gaps that sympathetic review would miss.*
