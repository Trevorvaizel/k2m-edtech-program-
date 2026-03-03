# Story 4.6: Design Artifact Creation Flow (/create-artifact)

Status: pending

**Epic:** 4 - CIS Agent System
**Story:** 4.6 - Design artifact creation flow (/create-artifact)
**Created:** 2026-01-25
**Purpose:** System Design - Design the complete artifact creation workflow that guides students through producing their Thinking Artifact using all four CIS agents

---

## Story

As a **Cohort Facilitation System Designer**,
I want **a complete artifact creation flow that guides students through using all four CIS agents (/frame, /diverge, /challenge, /synthesize) to produce their Thinking Artifact**,
so that **students can demonstrate their identity transformation through concrete evidence of structured thinking**.

---

## Acceptance Criteria

1. **Complete Artifact Creation Flow Document** specifying the `/create-artifact` command workflow from start to finish
2. **Six-Section Artifact Structure** (Decision 13) with templates and examples for each section
3. **Week-Based Progression Protocol** specifying when to introduce artifact creation (Week 6) and how to scaffold through Week 8
4. **CIS Agent Integration Guide** documenting how each agent contributes to specific artifact sections
5. **Private→Public Flow Architecture** (Decision 12) specifying #thinking-lab → #thinking-showcase transition
6. **Identity Transformation Evidence Framework** showing how artifact proves JTBD social job ("Give me proof I can show")
7. **Graduation Requirement Compliance Checklist** verifying artifact meets all Epic 6 requirements
8. **Controller Integration Specifications** for artifact creation state tracking and milestone management

---

## Tasks / Subtasks

- [ ] **1. Design Complete Artifact Creation Flow** (AC: #1)
  - [ ] 1.1 Define `/create-artifact` command entry point and initial guidance
  - [ ] 1.2 Specify 6-step creation process (one per artifact section)
  - [ ] 1.3 Design state tracking system (which sections completed, which remain)
  - [ ] 1.4 Create save/resume functionality (artifact creation is multi-day process)
  - [ ] 1.5 Specify completion validation (all 6 sections present, quality gates)

- [ ] **2. Create Six-Section Artifact Templates** (AC: #2)
  - [ ] 2.1 Section 1: "THE QUESTION I WRESTLED WITH" template + examples
  - [ ] 2.2 Section 2: "HOW I REFRAMED IT" (/frame integration) template + examples
  - [ ] 2.3 Section 3: "WHAT I EXPLORED" (/diverge integration) template + examples
  - [ ] 2.4 Section 4: "WHAT I CHALLENGED" (/challenge integration) template + examples
  - [ ] 2.5 Section 5: "WHAT I CONCLUDED" (/synthesize integration) template + examples
  - [ ] 2.6 Section 6: "WHAT THIS TAUGHT ME" (reflection) template + examples

- [ ] **3. Design Week-Based Progression Protocol** (AC: #3)
  - [ ] 3.1 Week 6: Artifact introduction and question selection (Section 1)
  - [ ] 3.2 Week 6-7: CIS agent workthrough (Sections 2-5)
  - [ ] 3.3 Week 7: Reflection section (Section 6)
  - [ ] 3.4 Week 8: Polish, formatting, and showcase preparation
  - [ ] 3.5 Create gentle reminder system (nudges for students stuck mid-artifact)

- [ ] **4. Document CIS Agent Integration Guide** (AC: #4)
  - [ ] 4.1 Specify /frame usage for Section 2 (reframing questions)
  - [ ] 4.2 Specify /diverge usage for Section 3 (exploring angles)
  - [ ] 4.3 Specify /challenge usage for Section 4 (stress-testing assumptions)
  - [ ] 4.4 Specify /synthesize usage for Section 5 (crystalizing insights)
  - [ ] 4.5 Create agent → section mapping with prompts and templates

- [ ] **5. Design Private→Public Flow Architecture** (AC: #5)
  - [ ] 5.1 Specify #thinking-lab private workspace for artifact creation
  - [ ] 5.2 Design DM/thread system for individual student progress
  - [ ] 5.3 Create #thinking-showcase posting protocol for Week 8
  - [ ] 5.4 Specify celebration and peer interaction patterns
  - [ ] 5.5 Design privacy controls (students choose what to make public)

- [ ] **6. Create Identity Transformation Evidence Framework** (AC: #6)
  - [ ] 6.1 Map artifact sections to identity shifts (outsider→observer→experimenter→collaborator→director)
  - [ ] 6.2 Create "before vs after" comparison framework
  - [ ] 6.3 Design 4 Habits visibility markers in artifact
  - [ ] 6.4 Specify social job fulfillment (proof for parents, future, self)
  - [ ] 6.5 Create artifact quality rubric (not assessment - guidance)

- [ ] **7. Verify Graduation Requirement Compliance** (AC: #7)
  - [ ] 7.1 Cross-reference with Epic 6 stories (6.1: artifact template, 6.2: showcase format)
  - [ ] 7.2 Ensure artifact serves JTBD social job: "Give me proof I can show"
  - [ ] 7.3 Verify artifact demonstrates all 4 Habits visibly
  - [ ] 7.4 Confirm artifact honors Guardrail #10 (authentic student voice, not AI generation)
  - [ ] 7.5 Validate artifact supports 4 Habits graduation card (Story 6.6)

- [ ] **8. Specify Controller Integration** (AC: #8)
  - [ ] 8.1 Define artifact_progress data structure in StudentContext
  - [ ] 8.2 Specify state machine for artifact creation stages
  - [ ] 8.3 Design milestone tracking (Section 1 complete, Sections 2-5 in progress, etc.)
  - [ ] 8.4 Create reminder nudges based on inactivity (3+ days no progress)
  - [ ] 8.5 Specify Week 8 showcase automation (create polished showcase post)

---

## Dev Notes

### Strategic Context (Decision 13 + Decision 14 + Epic 6)

**The Thinking Artifact is the graduation deliverable that proves identity transformation.**

From Decision 13:
- **OLD Artifact:** "How I Work With AI Now" (abstract, vague)
- **NEW Artifact:** Thinking Artifact (concrete, structured, proves thinking growth)

**Artifact Structure (Decision 13):**
```
THE QUESTION I WRESTLED WITH:
[Student's chosen question]

HOW I REFRAMED IT:
[Using /frame with The Framer]

WHAT I EXPLORED:
[Using /diverge with The Explorer]

WHAT I CHALLENGED:
[Using /challenge with The Challenger]

WHAT I CONCLUDED:
[Using /synthesize with The Synthesizer]

WHAT THIS TAUGHT ME:
[Reflection on thinking growth]
```

**Timeline (Decision 14):**
- Week 6-7: Artifact creation begins (all CIS agents available)
- Week 8: Artifact completion, polish, and public showcase

**Key Insight (Decision 13):**
> "They don't want help answering questions. They want help becoming the kind of person who answers well."

This means the artifact isn't about "using AI tools" - it's about demonstrating "I've become someone who thinks more clearly now."

### Foundation Documents (Epic 1 + Epic 4 Stories - ALL Non-Negotiable)

**Story 4.6 MUST build upon these Epic 1 foundations:**

**1. Guardrails (Story 1.1):**
- Guardrail #3 (No tech jargon): Artifact templates accessible to Zone 2-3 students
- Guardrail #4 (Always clarity): Clear instructions, not clever or confusing
- Guardrail #10 (Artifact Authenticity): Artifact must be student's own voice, not AI-generated
- Guardrail #11 (JTBD Examples): All artifact examples serve real student jobs

**2. JTBD Integration (Story 1.2):**
- Zone 3→4 identity shift: **collaborator → director**
- Social job: **Proof** ("Give me evidence I can show to myself, my parents, and my future")
- Philosophy principle: **Identity before competence** - artifact proves transformation, not technical skill
- Target identity: "I'm someone who can think through complex problems using AI as a thinking partner"

**3. Node Architecture (Story 1.3):**
- Zone 3→4 Nodes (Direct) - Weeks 6-7:
  - Node 3.1: "First draft is raw material" → Iteration mindset (artifact drafting)
  - Node 3.2: "I have opinions about quality" → Ownership emergence (artifact ownership)
  - Node 3.3: "Direction techniques work" → Skill acquisition (CIS agent mastery shown in artifact)
  - Node 3.4: "I made this" → Identity shift to director (artifact as proof of director identity)
- Artifact creation reinforces all 4 nodes

**4. 4 Habits Branding (Story 1.4):**
- **Habit 1 ⏸️ Pause**: Visible in "THE QUESTION I WRESTLED WITH" (thoughtful question selection)
- **Habit 2 🎯 Context**: Visible in "HOW I REFRAMED IT" (/frame usage)
- **Habit 3 🔄 Iterate**: Visible in "WHAT I EXPLORED" (/diverge usage)
- **Habit 4 🧠 Think First**: Visible in "WHAT I CHALLENGED" (/challenge usage)
- **All 4 Habits**: Visible in "WHAT I CONCLUDED" (/synthesize usage + crystalizing insights)
- Graduation proof: Artifact IS the proof they earned all 4 Habits badges

**Story 4.6 MUST integrate with Epic 4 CIS Agent System:**

**5. CIS Controller Logic (Story 4.1):**
- Controller tracks artifact_progress in StudentContext
- Controller manages state machine for artifact creation stages
- Controller provides reminders based on inactivity
- Controller validates artifact completion before Week 8 showcase

**6. The Framer Agent (Story 4.2):**
- /frame scaffolds Section 2: "HOW I REFRAMED IT"
- Framer helps students clarify their original question
- Habit 1 (Pause) and Habit 2 (Context) visible in this section

**7. The Explorer Agent (Story 4.3):**
- /diverge scaffolds Section 3: "WHAT I EXPLORED"
- Explorer helps students explore multiple angles
- Habit 3 (Iterate) visible in this section

**8. The Challenger Agent (Story 4.4):**
- /challenge scaffolds Section 4: "WHAT I CHALLENGED"
- Challenger helps students stress-test assumptions
- Habit 4 (Think First) visible in this section

**9. The Synthesizer Agent (Story 4.5):**
- /synthesize scaffolds Section 5: "WHAT I CONCLUDED"
- Synthesizer helps students crystalize insights into clear conclusions
- All 4 Habits integrated in this section

### Private → Public Flow Architecture (Decision 12)

**From Decision 12: Hybrid Discord Model:**

```
#thinking-lab (instructions + entry point)
    ↓
Private DM/Thread (CIS agent interactions + artifact creation)
    ↓ (safe, messy thinking documented)
    ↓
#thinking-showcase (finished artifacts celebrated)
```

**Rationale:**
- **Process is private** (safe to be messy, no public comparison during creation)
- **Product is public** (peer learning from finished thinking, social proof)
- **Journey is documented** (DM/thread becomes evidence of thinking process)
- **Celebration is visible** (motivation for completion, pride in finished work)

**Architecture for Story 4.6:**

**Phase 1: Private Artifact Creation (Weeks 6-7)**
- Location: Student's private DM/Thread with CIS bot
- Workflow:
  1. Student types `/create-artifact` in DM
  2. Bot guides them through 6 sections (one at a time)
  3. Each section uses relevant CIS agent(s) for development
  4. Bot saves work-in-progress artifact to StudentContext
  5. Student can save/resume at any time (artifact creation takes days/weeks)
  6. Bot provides gentle nudges if inactive for 3+ days

**Phase 2: Polish and Finalize (Week 8)**
- Location: Still private DM/Thread
- Workflow:
  1. Bot alerts: "All sections complete! Time to polish and finalize."
  2. Bot provides polish checklist:
     - Read through for clarity
     - Add specific details from your CIS conversations
     - Make sure YOUR voice comes through (not AI)
  3. Student makes final edits
  4. Bot generates formatted showcase post (markdown with proper structure)
  5. Student reviews and confirms: "Ready to publish"

**Phase 3: Public Showcase (Week 8)**
- Location: #thinking-showcase channel
- Workflow:
  1. Bot posts formatted artifact to #thinking-showcase
  2. Post includes:
     - Student's name (or anonymous if preferred)
     - Complete artifact (all 6 sections)
     - Celebration message from bot
     - 4 Habits badges earned (⏸️ 🎯 🔄 🧠)
  3. Peers can react and comment (celebration, not comparison)
  4. Trevor spots exceptional artifacts for Friday live session recognition

### Artifact Creation Flow Design

**Command: `/create-artifact`**

**Entry Point (Week 6+ only):**

When student types `/create-artifact` in DM:

```markdown
**Thinking Artifact Creation** 🎯

Your Thinking Artifact shows your thinking journey - where you started, what you explored, and how you think differently now.

**What it is:**
- A 6-section document showing your thinking process
- A snapshot of how you've grown as a thinker
- A chance to see how the 4 Habits helped you work through a real question

**What it's NOT:**
- An essay about "how I use AI"
- AI-generated content (this must be YOUR voice)
- A test or assessment (there's no grading, no "wrong answers")

**Feeling nervous? That's normal.** 🌟

Many students feel anxious about sharing their thinking. That's okay. This artifact isn't about being impressive - it's about being real. Honest thinking beats polished perfection every time.

**You'll create this over Weeks 6-8:**
- **Week 6:** Choose your question and start working through it
- **Weeks 6-7:** Work through CIS agent sections (at your own pace)
- **Week 8:** Polish and publish to #thinking-showcase

**Ready to start?** This will take 30-60 minutes to complete all 6 sections. You can save at any time and resume later.

Type: **start** to begin, or **show-example** to see a complete artifact first.
```

**If student types "show-example":**

```markdown
**Example: Complete Thinking Artifact**

*This is just an example format. Your artifact will be about YOUR question and YOUR thinking.*

---

**THE QUESTION I WRESTLED WITH:**

"I need to decide what to study at university, but I feel stuck between my parents' expectations (medicine) and what I'm actually interested in (computer science)."

**HOW I REFRAMED IT:**

Using /frame, I realized my question wasn't "What should I study?" but "What do I value?" I discovered I care about: solving real problems, creative work, and having options - not just "helping people" (medicine) or "being good at tech" (CS).

**WHAT I EXPLORED:**

Using /diverge, I explored 3 angles:
1. **What if I combined them?** (Medical technology, health tech startups)
2. **What if I questioned the binary?** (Maybe neither medicine nor CS - what about data science for public health?)
3. **What if I tried before committing?** (Volunteer at hospital, build a health app, see what I actually enjoy)

**WHAT I CHALLENGED:**

Using /challenge, I tested my assumptions:
- "My parents will be disappointed if I don't do medicine" → *Challenge:* What if they want me to be happy, not just be a doctor?
- "I need to decide now" → *Challenge:* What if the first year is FOR exploration? I don't have to commit forever.
- "Computer science isn't helping people" → *Challenge:* What if health tech helps more people than one doctor ever could?

**WHAT I CONCLUDED:**

Using /synthesize, I crystalized my insight: The real question isn't medicine vs CS - it's "How do I want to help people?" I'm going to:
1. **Try both:** Volunteer at a hospital AND build a small health project this year
2. **Keep options open:** Apply to both, but look for programs that combine tech + health
3. **Decide later:** I don't need to know now. The first year is for exploration.

**WHAT THIS TAUGHT ME:**

Before K2M, I thought I had to choose between making my parents happy and being happy myself. Now I realize:
- **Habit 1 (Pause):** I stopped rushing to decide and really thought about what I value
- **Habit 2 (Context):** I explained my full situation instead of just "medicine vs CS"
- **Habit 3 (Iterate):** I explored multiple angles instead of picking the first "good enough" answer
- **Habit 4 (Think First):** I questioned my assumptions instead of accepting them as true

I'm not someone who "made the right choice." I'm someone who learned HOW to think through choices. That skill will follow me forever, even if I change my mind later.

---

*Notice how this artifact shows thinking growth, not just "I used AI tools." The focus is on "I became someone who thinks clearly" not "I learned to use ChatGPT."*

**Ready to create your own?** Type **start** to begin.
```

**Before You Start: Artifact Agent Practice (Optional but Recommended)** 🔥

**New to CIS agents?** Let's warm up! This is **practice** - nothing you do here counts toward your artifact. Think of it like stretching before exercise.

**Quick Practice Round (10 minutes):**

1. **Try /frame** with any question:
   ```
   /frame I need to choose between pizza or burgers for dinner
   ```
   See how The Framer helps you clarify what you really want.

2. **Try /diverge** to explore options:
   ```
   /diverge What are 3 types of pizza I haven't tried?
   ```
   See how The Explorer helps you see angles you missed.

3. **Try /challenge** to test an assumption:
   ```
   /challenge I assume pizza is always better than burgers
   ```
   See how The Challenger helps you question your beliefs.

**Why practice?** Working with CIS agents is like any skill - easier when you've tried it once. This practice makes the actual artifact much smoother.

**Ready for the real thing?** Type **start** to begin your artifact.

**If student types "start":**

```markdown
**Section 1 of 6: THE QUESTION I WRESTLED WITH** ⏸️

Your artifact starts with a real question you're facing. It could be about:
- University/career decisions
- Academic challenges
- Personal dilemmas
- Future uncertainty
- Anything you're genuinely wrestling with

**What makes a good artifact question:**
✅ It's REAL (you're actually facing this)
✅ It's COMPLEX (no easy answers)
✅ It matters TO YOU (you genuinely want clarity)
✅ You haven't fully solved it yet (room to explore)

**Examples:**
- "I need to choose between [two universities/programs/careers]"
- "I'm struggling with [subject/skill] and don't know how to improve"
- "I feel pressure to [do X] but I'm not sure it's right for me"
- "I'm worried about [future concern] and don't know how to prepare"

**Your turn:**

In 1-2 sentences, describe the question you're wrestling with.

This doesn't have to be perfectly phrased. We'll refine it in the next section using /frame.

Type your question when ready:
```

**Student Input Processing:**

When student submits their question:

1. **Save to StudentContext.artifact_progress["section_1_question"]**
2. **Acknowledge and guide to next section:**

```markdown
✅ **Got it!** Your question is saved.

**Your Question:**
"[Student's question]"

**Next Step: Refine Your Question**

Now we'll use /frame to clarify what you're really asking. Sometimes our first question isn't the TRUE question - it's just the surface.

Type: **/frame [your question]** to work with The Framer on refining your question.

Example: /frame I need to choose between medicine and computer science but I feel stuck

**If you're new to /frame:**
The Framer helps you see what you're REALLY asking - not just the surface question. Just type your question and see what happens. The Framer will ask clarifying questions that help you dig deeper.

**No pressure** - this conversation helps you clarify. There's no "wrong" answer.

This will open a conversation with The Framer to help you clarify what you're really wrestling with.
```

**Section 2: HOW I REFRAMED IT (Integration with /frame)**

After student works with /frame:

```markdown
**Section 2 of 6: HOW I REFRAMED IT** 🎯

Great work using /frame! Now let's capture what you discovered.

**What to include in this section:**
- Your original question (from Section 1)
- What /frame helped you see about your question
- Your refined/clarity question (if it changed)
- What made the question clearer

**Example:**

"I originally thought I was choosing between medicine and computer science. But using /frame, I realized I'm actually asking 'What do I value?' I care about solving real problems, creative work, and having options - not just 'helping people' vs 'being good at tech.'"

**Your turn:**

Based on your /frame conversation, write 2-3 sentences about:
1. What you originally thought you were asking
2. What /frame helped you see
3. How your question clarified (if it changed)

Type your response when ready, or type **/frame** again if you want to keep refining.
```

**Save to StudentContext.artifact_progress["section_2_reframed"]**

**Section 3: WHAT I EXPLORED (Integration with /diverge)**

```markdown
**Section 3 of 6: WHAT I EXPLORED** 🔄

Now let's explore! Using /diverge, you'll examine multiple angles on your question.

**Type: /diverge [your clarified question]** to work with The Explorer.

The Explorer will help you:
- Try different angles
- See options you haven't considered
- Discover what you didn't know you were looking for

**If you're new to /diverge:**
The Explorer helps you see options you haven't considered. Think of it like brainstorming - no idea is too crazy. Share your question and see what angles emerge. You might be surprised what you discover.

**If you feel stuck:** Try "What are 3 angles I haven't considered?" as a starting prompt.

After your /diverge conversation, come back here and we'll capture what you explored.
```

**After /diverge conversation:**

```markdown
**Section 3: WHAT I EXPLORED** 🔄

Great exploration! Now let's document it.

**What to include:**
- 2-3 angles you explored (not just one - show breadth)
- What each angle revealed (insights, surprises)
- What you discovered that you didn't expect

**Example:**

"Using /diverge, I explored 3 angles:
1. **What if I combined them?** Medical technology, health tech startups - fields that blend medicine and CS
2. **What if I questioned the binary?** Maybe neither medicine nor CS - what about data science for public health?
3. **What if I tried before committing?** Volunteer at hospital, build a health app, see what I actually enjoy

The big surprise: I don't have to choose forever. I can explore both before committing."

**Your turn:**

Based on your /diverge conversation, write 3-4 sentences about what you explored and what you discovered.

Type your response when ready, or type **/diverge** again to explore more angles.
```

**Save to StudentContext.artifact_progress["section_3_explored"]**

**Section 4: WHAT I CHALLENGED (Integration with /challenge)**

```markdown
**Section 4 of 6: WHAT I CHALLENGED** 🧠

Now let's stress-test your thinking! Using /challenge, you'll examine your assumptions.

**Type: /challenge [what you're assuming about your question]** to work with The Challenger.

The Challenger will help you:
- Identify what you're taking for granted
- Question beliefs you haven't examined
- Test your assumptions before committing

**If you're new to /challenge:**
The Challenger helps you question what you assume is true. Challenging your own thinking feels uncomfortable - that's normal! Start with "What if I'm wrong about..." and see what happens. You don't have to change your mind - just test your thinking.

**If challenging feels scary:** Start SMALL. Challenge something minor, not your core belief. Remember: Challenging ≠ changing your mind. It just means testing.

After your /challenge conversation, come back here and we'll capture what you challenged.
```

**After /challenge conversation:**

```markdown
**Section 4: WHAT I CHALLENGED** 🧠

Great critical thinking! Now let's document it.

**What to include:**
- 2-3 assumptions you questioned
- What testing each assumption revealed
- How challenging changed your thinking

**Example:**

"Using /challenge, I tested my assumptions:
1. **'My parents will be disappointed if I don't do medicine'** → *Challenge:* What if they want me to be happy, not just be a doctor? I realized I haven't actually talked to them about what they want FOR me (not what they want FROM me).
2. **'I need to decide now'** → *Challenge:* What if the first year is FOR exploration? I'm 17 - how could I be certain about a 40-year career?
3. **'Computer science isn't helping people'** → *Challenge:* What if health tech helps more people than one doctor ever could?

Challenging these assumptions made me realize I'm operating on fear and pressure, not my own values."

**Your turn:**

Based on your /challenge conversation, write 3-4 sentences about what you challenged and what you discovered.

Type your response when ready, or type **/challenge** again to test more assumptions.
```

**Save to StudentContext.artifact_progress["section_4_challenged"]**

**Section 5: WHAT I CONCLUDED (Integration with /synthesize)**

```markdown
**Section 5 of 6: WHAT I CONCLUDED** ✨

Now let's bring it all together! Using /synthesize, you'll crystalize your insights into clear conclusions.

**Type: /synthesize [what you've learned from all sections so far]** to work with The Synthesizer.

The Synthesizer will help you:
- Integrate insights from all previous sections
- Find the through-line in your thinking
- Crystalize what you've concluded

After your /synthesize conversation, come back here and we'll capture your conclusion.
```

**After /synthesize conversation:**

```markdown
**Section 5: WHAT I CONCLUDED** ✨

Beautiful synthesis! Now let's document your conclusion.

🔗 **Node 3.1 Connection:** Remember - "First draft is raw material" (from Week 6)
Your conclusion isn't final! It's your current best thinking. You can always iterate later. Think of this as a snapshot, not a permanent decision.

**What to include:**
- Your core insight (what you learned through this whole process)
- Your conclusion or decision (if you made one)
- What you're taking forward (even if you don't have a final answer)

**Example:**

"Using /synthesize, I crystalized my insight: The real question isn't medicine vs CS - it's 'How do I want to help people?'

**My conclusion:**
I'm going to:
1. **Try both:** Volunteer at a hospital AND build a small health project this year
2. **Keep options open:** Apply to both, but look for programs that combine tech + health
3. **Decide later:** I don't need to know now. The first year is for exploration.

The big shift: I'm not looking for 'the right choice' anymore. I'm looking for 'the right next step' - and that's much less pressure."

**Your turn:**

Based on your /synthesize conversation, write 3-4 sentences about what you concluded and what you're taking forward.

Type your response when ready, or type **/synthesize** again to refine your conclusion.
```

**Save to StudentContext.artifact_progress["section_5_concluded"]**

**Section 6: WHAT THIS TAUGHT ME (Reflection)**

```markdown
**Section 6 of 6: WHAT THIS TAUGHT ME** 🌟

This is the most important section! It's where you show how you've grown as a thinker.

🔗 **Node 3.2 Connection:** Remember - "I have opinions about quality" (from Week 6)
What standards do you now hold for your own thinking? What do you consider "good thinking"?

**What to include:**
- How you thought BEFORE this process (your "before" self)
- How you think NOW (your "after" self)
- Which 4 Habits you used (⏸️ 🎯 🔄 🧠) and how
- **How you'll use these thinking habits in university, your career, or your life** (Future Application)

**Example:**

"Before K2M, I thought I had to choose between making my parents happy and being happy myself. I rushed to decisions, accepted assumptions without questioning, and felt overwhelmed by options.

Now I realize:
- **Habit 1 (Pause):** I stopped rushing to decide and really thought about what I value. I took 3 minutes before big choices instead of reacting.
- **Habit 2 (Context):** I explained my full situation instead of just 'medicine vs CS.' The right context made the question clearer.
- **Habit 3 (Iterate):** I explored multiple angles instead of picking the first 'good enough' answer. I discovered options I didn't know existed.
- **Habit 4 (Think First):** I questioned my assumptions instead of accepting them as true. I realized I was operating on fear, not my own values.

🚀 **Future Application:**
When I get to university, I'll use Habit 2 (Context) when I'm confused about assignments - I'll explain my full situation instead of staying stuck. I'll use Habit 4 (Think First) before choosing my courses. These habits aren't just for AI - they're how I'll approach decisions in my life.

I'm not someone who 'made the right choice.' I'm someone who learned HOW to think through choices. That skill will follow me forever, even if I change my mind later."

**Your turn:**

Write 5-7 sentences reflecting on:
1. How you thought before (your "before" self)
2. How you think now (your "after" self)
3. Which 4 Habits you used and how
4. **How you'll apply these thinking habits in university, your career, or your life** (be specific - which habits will you use when?)

Type your reflection when ready. This is the final section!
```

**Save to StudentContext.artifact_progress["section_6_reflection"]**

**Completion Validation:**

After all 6 sections complete:

```markdown
🎉 **Congratulations! Your Thinking Artifact is Complete!** 🎉

**What you've created:**
✅ Section 1: THE QUESTION I WRESTLED WITH
✅ Section 2: HOW I REFRAMED IT (🎯 Habit 2: Context)
✅ Section 3: WHAT I EXPLORED (🔄 Habit 3: Iterate)
✅ Section 4: WHAT I CHALLENGED (🧠 Habit 4: Think First)
✅ Section 5: WHAT I CONCLUDED
✅ Section 6: WHAT THIS TAUGHT ME (⏸️ Habit 1: Pause)

**What this proves:**
You've become someone who can think clearly with AI. You didn't just "use tools" - you transformed how you approach problems.

**Next Steps:**

**Week 8: Polish and Publish**

This week, you'll:
1. Review your artifact for clarity and voice
2. Make any final edits
3. Publish to #thinking-showcase for your peers to see
4. Earn your 4 Habits graduation badge!

**Want to review now?** Type **review** to see your complete artifact and make edits.

**Ready to polish later?** Type **save** and come back in Week 8. I'll remind you!

---

**You should be proud of this.** This artifact proves real growth. 🌟
```

### Artifact Quality Guidance Framework

**Purpose:** This guide helps you understand what makes your artifact strongest. It's NOT grading - there's no "wrong" artifact. This is about making your artifact most meaningful for YOU.

**The #1 Principle:** **Honest > Perfect**

A messy authentic artifact is better than a polished generic one. Parents want to hear YOU, not ChatGPT.

**Four Quality Dimensions:**

**1. Depth of Thinking**
- **Strong:** "I explored 3 different angles and discovered X, Y, and Z"
- **Developing:** "I tried one angle and it helped"
- **Guidance:** Deeper exploration = more meaningful artifact for YOU

**2. Authentic Voice**
- **Strong:** Sounds like YOU - honest, maybe even messy
- **Developing:** Sounds generic or AI-written
- **Guidance:** Parents should hear YOU in this, not ChatGPT

**3. Habit Visibility**
- **Strong:** Specific examples ("When I paused, I realized I was rushing...")
- **Developing:** "I used all 4 habits" (no specifics)
- **Guidance:** Show, don't just tell

**4. Before/After Clarity**
- **Strong:** "I used to think X. Now I see Y. Here's what changed..."
- **Developing:** "I learned a lot" (vague)
- **Guidance:** Make your growth visible to yourself

**Remember:** The best artifact is HONEST, not perfect. This isn't about impressing anyone - it's about showing YOUR real thinking journey.

### State Tracking and Save/Resume System

**StudentContext.artifact_progress Data Structure:**

```python
class ArtifactProgress:
    """Tracks student's artifact creation progress"""

    # Which sections completed
    completed_sections: List[str] = []
    # Options: ["section_1", "section_2", "section_3", "section_4", "section_5", "section_6"]

    # Content for each section
    section_1_question: str = ""  # Original question
    section_2_reframed: str = ""  # How /frame clarified it
    section_3_explored: str = ""  # What /diverge revealed
    section_4_challenged: str = ""  # What /challenge tested
    section_5_concluded: str = ""  # What /synthesize crystalized
    section_6_reflection: str = ""  # Identity transformation proof

    # State tracking
    current_section: int = 0  # Which section student is working on (1-6)
    started_at: datetime = None
    last_activity: datetime = None  # For reminder nudges
    completed_at: datetime = None
    published_at: datetime = None  # When posted to #thinking-showcase

    # State machine: "not_started" | "in_progress" | "completed" | "published"
    status: str = "not_started"

    def is_complete(self) -> bool:
        """Check if all 6 sections have content"""
        return all([
            self.section_1_question,
            self.section_2_reframed,
            self.section_3_explored,
            self.section_4_challenged,
            self.section_5_concluded,
            self.section_6_reflection
        ])

    def get_next_section(self) -> int:
        """Return the next section to work on"""
        if not self.section_1_question:
            return 1
        elif not self.section_2_reframed:
            return 2
        elif not self.section_3_explored:
            return 3
        elif not self.section_4_challenged:
            return 4
        elif not self.section_5_concluded:
            return 5
        elif not self.section_6_reflection:
            return 6
        else:
            return 0  # All complete

    def days_since_activity(self) -> int:
        """For reminder nudges"""
        if not self.last_activity:
            return 999
        return (datetime.now() - self.last_activity).days
```

**Save/Resume Functionality:**

When student types "/create-artifact" at any point:

```python
# Controller logic

artifact_progress = student_context.artifact_progress

if artifact_progress.status == "not_started":
    # Show introduction (as above)
    pass

elif artifact_progress.status == "in_progress":
    # Resume from where they left off
    next_section = artifact_progress.get_next_section()

    message = f"""
**Welcome back to your Thinking Artifact!** 📝

**Progress: {len(artifact_progress.completed_sections)}/6 sections complete**

**Where you left off:**
{get_progress_summary(artifact_progress)}

**Next step:**
{get_next_section_prompt(next_section)}

**Options:**
- Type **continue** to work on Section {next_section}
- Type **review** to see what you've written so far
- Type **start-over** (not recommended - you'll lose your work)
"""
    # Send to student
    await post_to_discord_safe(channel, message)

elif artifact_progress.status == "completed":
    # Already done all sections - prompt to polish/publish
    message = """
**Your Thinking Artifact is complete!** ✅

**Ready for Week 8: Polish and Publish**

This week (Week 8), you'll:
1. Review your artifact
2. Make final edits
3. Publish to #thinking-showcase

**Want to review early?** Type **review** to see your complete artifact.

**Ready to publish now?** Type **publish** if you're happy with it (note: Week 8 showcase is when most students publish, but you can publish earlier if ready).
"""
    await post_to_discord_safe(channel, message)
```

### Reminder Nudges (Inactivity Detection)

**Controller Background Job:**

```python
# Runs daily
async def check_artifact_inactivity():
    """Send gentle reminders to students stuck mid-artifact"""

    for student in all_students():
        artifact_progress = student.artifact_progress

        # Only remind if:
        # - Student is in Weeks 6-8
        # - Artifact is "in_progress" (not completed)
        # - No activity for 3+ days

        if (student.current_week in [6, 7, 8] and
            artifact_progress.status == "in_progress" and
            artifact_progress.days_since_activity() >= 3):

            # Send gentle reminder
            await send_reminder_nudge(student)


async def send_reminder_nudge(student):
    """Send non-pressuring reminder to continue artifact"""

    days_inactive = student.artifact_progress.days_since_activity()
    next_section = student.artifact_progress.get_next_section()

    message = f"""
**Hey! Just checking in on your Thinking Artifact** 👋

You started {days_inactive} days ago. You've completed {len(student.artifact_progress.completed_sections)}/6 sections.

**No pressure** - this takes time! But if you're stuck, I'm here to help.

**Where you left off:**
{get_progress_summary(student.artifact_progress)}

**Next:** Section {next_section}

**Options:**
- Type **continue** to keep going
- Type **help** if you're stuck on something
- Type **not-yet** if you need more time (I'll check back in a few days)

You've got this. 🌟
"""

    await post_to_discord_safe(student.dm_channel, message)


### Stuck Pattern Detection (Targeted Interventions)

**Enhanced Controller Background Job:**

```python
# Runs daily - checks for specific stuck patterns
async def check_artifact_stuck_patterns():
    """Detect students stuck on specific sections and send targeted help"""

    for student in all_students():
        artifact_progress = student.artifact_progress

        # Only check if student is in Weeks 6-8 and artifact is in_progress
        if student.current_week not in [6, 7, 8]:
            continue
        if artifact_progress.status != "in_progress":
            continue

        # Pattern 1: Stuck on Section 3 (WHAT I EXPLORED) - 2+ days inactive
        if (artifact_progress.section_2_reframed and
            not artifact_progress.section_3_explored and
            artifact_progress.days_since_activity() >= 2):

            await send_section_3_stuck_nudge(student)

        # Pattern 2: Stuck on Section 4 (WHAT I CHALLENGED) - 2+ days inactive
        if (artifact_progress.section_3_explored and
            not artifact_progress.section_4_challenged and
            artifact_progress.days_since_activity() >= 2):

            await send_section_4_stuck_nudge(student)

        # Pattern 3: Stuck on Section 5 (WHAT I CONCLUDED) - 2+ days inactive
        if (artifact_progress.section_4_challenged and
            not artifact_progress.section_5_concluded and
            artifact_progress.days_since_activity() >= 2):

            await send_section_5_stuck_nudge(student)


async def send_section_3_stuck_nudge(student):
    """Targeted help for exploration stuck"""

    message = """
**Hey! Noticing you're on Section 3** 👋

Exploration feels hard sometimes. Here's help:

**If you're stuck on "what to explore":**
- Try /diverge with "What are 3 angles I haven't considered?"
- Pick the WILDEST option first (nothing is too crazy)

**If you feel like "there's nothing to explore":**
- Challenge that feeling! Is it true there's nothing?
- Try /challenge on "there's nothing to explore about my question"

**If you explored but can't put it into words:**
- Just list bullet points: "Angle 1: X. Angle 2: Y."
- You can refine later - imperfect is okay!

**Type:** **continue** to keep going, or **help** for more specific guidance.
"""
    await post_to_discord_safe(student.dm_channel, message)


async def send_section_4_stuck_nudge(student):
    """Targeted help for challenge stuck"""

    message = """
**Checking in on Section 4** 🧠

Challenging your own thinking is... uncomfortable. That's normal!

**If you're stuck on "what to challenge":**
- What do you ASSUME is true? (challenge that)
- What do you take for granted? (question that)
- What would happen if the opposite was true?

**If you feel like "I have no assumptions":**
- Try /challenge with "What if I'm wrong about [central belief]?"
- Example: "What if I'm wrong about medicine being the only way to help people?"

**If challenging feels scary:**
- Start SMALL: challenge something minor, not your core question
- Remember: Challenging ≠ changing your mind. It just means testing.

**Type:** **continue** or **help**
"""
    await post_to_discord_safe(student.dm_channel, message)


async def send_section_5_stuck_nudge(student):
    """Targeted help for synthesis stuck"""

    message = """
**Section 5 - Almost there!** ✨

Synthesis feels overwhelming when you have SO MUCH thinking to integrate.

**If you're stuck on "what did I conclude?":**
- You don't need a final answer. You need a "current best thinking."
- Try: "Based on everything, right now I think..."

**If you feel like "I didn't conclude anything":**
- That's okay! Your conclusion might be "I need more time to explore"
- Or: "I'm less certain than before, but I have better questions"

**If you can't see the through-line:**
- Look for patterns across sections 2-4
- What showed up multiple times? That's your through-line

**Type:** **continue** or **help**
"""
    await post_to_discord_safe(student.dm_channel, message)
```

### Week 8: Polish and Publish Flow

**When student types "review" (Week 8 or any time after completion):**

```markdown
**Your Complete Thinking Artifact** 📝

---

**THE QUESTION I WRESTLED WITH:**

{artifact_progress.section_1_question}

**HOW I REFRAMED IT:**

{artifact_progress.section_2_reframed}

**WHAT I EXPLORED:**

{artifact_progress.section_3_explored}

**WHAT I CHALLENGED:**

{artifact_progress.section_4_challenged}

**WHAT I CONCLUDED:**

{artifact_progress.section_5_concluded}

**WHAT THIS TAUGHT ME:**

{artifact_progress.section_6_reflection}

---

**Polish Checklist:** ✅

🔗 **Node 3.3 Connection:** Remember - "Direction techniques work" (from Week 6)
You've learned to steer AI toward quality. As you polish, ask: "Does this reflect the quality standards I now hold?"

Before publishing, review your artifact:

- [ ] **Clarity:** Does each section make sense to someone who doesn't know your story?
- [ ] **Voice:** Is this YOUR voice? (Not AI-written - parents should hear YOU in this)
- [ ] **Specifics:** Did you include concrete details from your CIS conversations? (Not just "I explored" but "I explored X, Y, and Z")
- [ ] **4 Habits:** Are all 4 habits visible in your reflection? (⏸️ Pause, 🎯 Context, 🔄 Iterate, 🧠 Think First)
- [ ] **Quality Standards:** Does this reflect the thinking quality YOU now expect from yourself?

**Want to edit?**

Type: **edit section [1-6]** to revise any section

Example: edit section 3

**Ready to publish?**

Type: **publish** to post to #thinking-showcase

**Need more time?**

Type: **save** and come back later
```

**When student types "publish":**

```markdown
**Publish Your Thinking Artifact** 🚀

**Before I post this to #thinking-showcase, confirm:**

1. **Your name (or anonymous):**
   Type: **name [your name]** or **anonymous**

2. **Public or private:**
   - **Public** (recommended): Peers can see and celebrate your work
   - **Private**: Only Trevor can see (for shy students, but you miss peer celebration)

   Type: **public** or **private**

**What happens next:**
- I'll post your formatted artifact to #thinking-showcase
- Peers can react and celebrate (not compare - celebrate!)
- Trevor may select exceptional artifacts for Friday live session recognition
- You'll officially earn your 4 Habits graduation badge 🎓

**Ready to confirm?**
- Type: **confirm public** or **confirm private**
- Or type: **cancel** to review more
```

**After confirmation:**

```markdown
✅ **Publishing your Thinking Artifact to #thinking-showcase!**

Your artifact is now live. Your peers can see your thinking growth and celebrate with you.

**You've officially earned:**
⏸️ **PAUSE** - Habit 1 Badge
🎯 **CONTEXT** - Habit 2 Badge
🔄 **ITERATE** - Habit 3 Badge
🧠 **THINK FIRST** - Habit 4 Badge

🔗 **Node 3.4: "I Made This"**

You're not just someone who "used AI." You're someone who directed AI to create something meaningful.

That's the Zone 4 director identity - you own your thinking and your outcomes. You didn't just use tools - you learned to THINK WITH AI.

That skill will follow you forever. Tools change - thinking lasts.

**Congratulations!** 🎉🌟

---

*(Your artifact has been posted to #thinking-showcase)*
```

**Controller then posts to #thinking-showcase:**

```python
formatted_artifact = f"""
**Thinking Artifact: {student.name or 'Anonymous'}** 🌟

*Completed: Week 8*

---

**THE QUESTION I WRESTLED WITH:**

{artifact_progress.section_1_question}

**HOW I REFRAMED IT:** 🎯

{artifact_progress.section_2_reframed}

**WHAT I EXPLORED:** 🔄

{artifact_progress.section_3_explored}

**WHAT I CHALLENGED:** 🧠

{artifact_progress.section_4_challenged}

**WHAT I CONCLUDED:** ✨

{artifact_progress.section_5_concluded}

**WHAT THIS TAUGHT ME:** ⏸️

{artifact_progress.section_6_reflection}

---

**4 Habits Earned:** ⏸️ 🎯 🔄 🧠

*Celebrate with reactions below! 👇*
"""

await bot.get_channel(THINKING_SHOWCASE_CHANNEL).send(formatted_artifact)
```

### Identity Transformation Evidence Framework

**How the Artifact Proves JTBD Social Job: "Give me proof I can show"**

**Social Job Breakdown (Decision 13):**

The artifact provides proof for three audiences:

**1. Proof for THEMSELVES:**
- "I can see my own growth" (Section 6: "WHAT THIS TAUGHT ME")
- Before/After comparison makes transformation visible to student
- Concrete evidence: "I used Habit 1, Habit 2, Habit 3, Habit 4"

**2. Proof for PARENTS:**
- Shows real thinking, not just "using AI"
- Demonstrates maturity: "My child can make decisions thoughtfully"
- Tangible outcome: Specific question worked through, not vague "I learned AI"
- 4 Habits badges visible (⏸️ 🎯 🔄 🧠)

**3. Proof for FUTURE:**
- Artifact becomes portfolio piece
- Shows: "I can think through complex problems"
- Shows: "I use AI as a thinking partner, not a crutch"
- Universities/employers value: Structured thinking > technical skills

**Identity Shift Mapping (Zone 3→4: Collaborator → Director):**

**Collaborator Identity (Zone 3 - Before Artifact):**
- "I work WITH AI to explore"
- "AI helps me see options"
- "We think together"

**Director Identity (Zone 4 - After Artifact):**
- "I direct my thinking process"
- "I choose which tools to use and when"
- "I own the outcome - AI doesn't decide for me"

**How Artifact Shows This Shift:**

**Section 5 (WHAT I CONCLUDED) demonstrates director identity:**
- "I decided to..." (ownership, not "AI told me to")
- "I'm going to..." (agency, not "ChatGPT suggested")
- "My conclusion..." (authorship, not "we came up with")

**Section 6 (WHAT THIS TAUGHT ME) explicitly states identity transformation:**
- "Before K2M, I thought..." (collaborator/experimenter identity)
- "Now I realize..." (director identity)
- "I'm someone who..." (identity statement)

### Graduation Requirement Compliance Checklist

**Cross-Reference with Epic 6 Requirements:**

**Story 6.1: Thinking Artifact Template** ✅
- Story 4.6 creates the complete 6-section template
- Story 4.6 provides examples for each section
- Story 6.1 will build upon this foundation (formatting, design)

**Story 6.2: Artifact Showcase Format** ✅
- Story 4.6 specifies #thinking-showcase posting format
- Story 4.6 specifies celebration patterns
- Story 6.2 will build upon this (showcase event design, peer interaction)

**Story 6.3: New Success Metrics** ✅
- Artifact demonstrates "thinking demonstration" metrics
- Story 4.6 provides identity transformation evidence framework
- Story 6.3 will define measurement rubrics

**Story 6.5: Parent Reporting Format** ✅
- Artifact serves as tangible outcome for parent reports
- Section 6 (WHAT THIS TAUGHT ME) is parent-friendly
- Story 6.5 will reference artifacts as evidence

**Story 6.6: 4 Habits Graduation Card** ✅
- Artifact proves all 4 Habits earned
- Section 6 makes each habit visible
- Story 6.6 will issue badges after artifact completion

**Guardrail Compliance:**

**Guardrail #3 (No Tech Jargon):** ✅
- All section titles are everyday language
- Instructions use clear, relatable examples
- No technical terms like "prompt engineering" or "AI literacy"

**Guardrail #4 (Always Clarity):** ✅
- Step-by-step guidance for each section
- "What to include" examples provided
- Clear prompts for student responses

**Guardrail #10 (Artifact Authenticity):** ✅
- Explicit warning: "This must be YOUR voice, not AI-generated"
- Polish checklist includes: "Is this YOUR voice?"
- Examples show authentic student voice, not polished essays
- Section 6 reflection cannot be AI-generated (too personal)

**Guardrail #11 (JTBD Examples):** ✅
- All artifact examples serve real student jobs (university, career, homework, anxiety)
- No abstract or juvenile scenarios
- Examples age-appropriate for pre-university students

### Controller Integration Specifications

**Data Structure (in StudentContext from Story 4.1):**

```python
# Add to StudentContext class

@dataclass
class ArtifactProgress:
    """Tracks Thinking Artifact creation progress (Weeks 6-8)"""

    # Section content
    section_1_question: str = ""
    section_2_reframed: str = ""
    section_3_explored: str = ""
    section_4_challenged: str = ""
    section_5_concluded: str = ""
    section_6_reflection: str = ""

    # State tracking
    completed_sections: List[str] = field(default_factory=list)
    current_section: int = 0
    status: str = "not_started"  # "not_started" | "in_progress" | "completed" | "published"

    # Timestamps
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    # Helper methods
    def is_complete(self) -> bool: ...
    def get_next_section(self) -> int: ...
    def days_since_activity(self) -> int: ...

# Add to StudentContext
artifact_progress: ArtifactProgress = ArtifactProgress()
```

**State Machine:**

```
┌──────────────┐
│ not_started  │  (Week 6 begins)
└──────┬───────┘
       │ /create-artifact command
       ▼
┌──────────────┐
│ in_progress  │  (Working through sections 1-6)
└──────┬───────┘
       │ All 6 sections complete
       ▼
┌──────────────┐
│ completed    │  (Ready for polish/publish)
└──────┬───────┘
       │ /publish command (Week 8)
       ▼
┌──────────────┐
│ published    │  (Posted to #thinking-showcase)
└──────────────┘
```

**Controller Commands:**

```python
# Command handlers

@bot.command(name='create-artifact')
async def create_artifact(ctx):
    """Entry point for artifact creation flow"""
    student = get_student(ctx.author.id)

    # Check week (only available Week 6+)
    if student.current_week < 6:
        await post_to_discord_safe(ctx.channel,
            "The Thinking Artifact is a Week 6-8 project. You'll get access when Week 6 begins!")
        return

    # Delegate to artifact creation flow
    await handle_artifact_creation(ctx, student)


@bot.command(name='save')
async def save_artifact(ctx):
    """Save current artifact progress"""
    student = get_student(ctx.author.id)
    student.artifact_progress.last_activity = datetime.now()
    student.save()

    await post_to_discord_safe(ctx.channel,
        "✅ **Artifact saved!** Type `/create-artifact` anytime to continue.")


@bot.command(name='review')
async def review_artifact(ctx):
    """Show complete artifact for review"""
    student = get_student(ctx.author.id)

    if not student.artifact_progress.is_complete():
        await post_to_discord_safe(ctx.channel,
            "You haven't completed all 6 sections yet. Type `/create-artifact` to continue.")
        return

    # Show formatted artifact (as above in "Week 8: Polish and Publish Flow")
    await show_artifact_for_review(ctx, student)


@bot.command(name='edit')
async def edit_section(ctx, section_number: int):
    """Edit a specific section"""
    student = get_student(ctx.author.id)

    # Prompt for new content
    await post_to_discord_safe(ctx.channel,
        f"**Editing Section {section_number}**\n\nPaste your new version:")

    # Wait for response and update
    response = await bot.wait_for('message', check=...)

    # Update section
    if section_number == 1:
        student.artifact_progress.section_1_question = response.content
    # ... (etc for all 6 sections)

    student.artifact_progress.last_activity = datetime.now()
    student.save()

    await post_to_discord_safe(ctx.channel,
        f"✅ **Section {section_number} updated!** Type `/review` to see your complete artifact.")


@bot.command(name='publish')
async def publish_artifact(ctx):
    """Publish artifact to #thinking-showcase"""
    student = get_student(ctx.author.id)

    if not student.artifact_progress.is_complete():
        await post_to_discord_safe(ctx.channel,
            "Complete all 6 sections before publishing. Type `/create-artifact` to continue.")
        return

    # Confirm publish (as shown in "Week 8: Polish and Publish Flow")
    await confirm_publish(ctx, student)
```

**Background Jobs:**

```python
# Daily job: Check for inactivity and send reminders
@tasks.loop(hours=24)
async def check_artifact_reminders():
    """Send gentle reminders to students inactive for 3+ days"""
    for student in all_students():
        if (student.current_week in [6, 7, 8] and
            student.artifact_progress.status == "in_progress" and
            student.artifact_progress.days_since_activity() >= 3):

            await send_artifact_reminder(student)

# Run during Week 8: Publish celebration posts
@tasks.loop(hours=24)
async def celebrate_artifact_completions():
    """Post daily celebration of new artifacts to #general"""
    yesterday = datetime.now() - timedelta(days=1)

    new_artifacts = StudentContext.objects.filter(
        artifact_progress__published_at__gte=yesterday
    )

    if new_artifacts.count() > 0:
        message = f"""
🎉 **Yesterday's Thinking Artifacts!** 🎉

{new_artifacts.count()} students published their artifacts to #thinking-showcase!

These artifacts prove real growth. Each student showed how they've become someone who can think clearly with AI.

**Check out #thinking-showcase** to celebrate your peers' thinking growth!

**Want to publish yours?** Type `/publish` to complete your artifact.
"""
        await bot.get_channel(GENERAL_CHANNEL).send(message)
```

### Testing & Validation

**Acceptance Criteria Validation:**

**AC #1: Complete Artifact Creation Flow Document** ✅
- /create-artifact command specified from entry to completion
- 6-step creation process documented
- Save/resume functionality designed
- Completion validation specified

**AC #2: Six-Section Artifact Structure** ✅
- All 6 sections from Decision 13 implemented
- Templates provided for each section
- Examples given for each section
- CIS agent integration specified

**AC #3: Week-Based Progression Protocol** ✅
- Week 6: Introduction and Section 1
- Week 6-7: Sections 2-5 (CIS agent workthrough)
- Week 7: Section 6 (reflection)
- Week 8: Polish and publish
- Reminder nudges specified

**AC #4: CIS Agent Integration Guide** ✅
- /frame → Section 2 (HOW I REFRAMED IT)
- /diverge → Section 3 (WHAT I EXPLORED)
- /challenge → Section 4 (WHAT I CHALLENGED)
- /synthesize → Section 5: (WHAT I CONCLUDED)
- Clear mapping provided

**AC #5: Private→Public Flow Architecture** ✅
- #thinking-lab private workspace specified
- DM/thread system designed
- #thinking-showcase posting protocol specified
- Celebration patterns documented
- Privacy controls included

**AC #6: Identity Transformation Evidence Framework** ✅
- Artifact sections mapped to identity shifts
- Before/after comparison framework created
- 4 Habits visibility markers specified
- Social job fulfillment addressed
- Quality rubric provided (guidance, not assessment)

**AC #7: Graduation Requirement Compliance Checklist** ✅
- Cross-referenced with Epic 6 stories (6.1, 6.2, 6.3, 6.5, 6.6)
- JTBD social job served
- 4 Habits graduation card supported
- Guardrail #10 (authenticity) enforced
- Guardrail #3 (no jargon) enforced

**AC #8: Controller Integration Specifications** ✅
- artifact_progress data structure defined
- State machine specified
- Milestone tracking designed
- Reminder nudges specified
- Week 8 showcase automation designed

### References

**Source Documents:**
- Decision 11: CIS Agent System → `_bmad-output/cohort-design-artifacts/cohort-playbook-v2-requirements.md` lines 242-275
- Decision 12: Hybrid Discord Model → `_bmad-output/cohort-design-artifacts/cohort-playbook-v2-requirements.md` lines 273-292
- Decision 13: Thinking Artifact → `_bmad-output/cohort-design-artifacts/cohort-playbook-v2-requirements.md` lines 293-327
- Decision 14: Artifact Timeline → `_bmad-output/cohort-design-artifacts/cohort-playbook-v2-requirements.md` lines 328-335
- Story 4.1: CIS Controller Logic → `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-1-cis-controller-logic.md`
- Story 4.2: The Framer Agent Prompt → `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-2-framer-agent-prompt.md`
- Story 4.3: The Explorer Agent Prompt → `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-3-explorer-agent-prompt.md`
- Story 4.4: The Challenger Agent Prompt → `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-4-challenger-agent-prompt.md`
- Story 4.5: The Synthesizer Agent Prompt → `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-5-synthesizer-agent-prompt.md`
- Epic 1 Foundations → `_bmad-output/cohort-design-artifacts/playbook-v2/01-philosophy/`

**Brand Framework:**
- "Think WITH AI" positioning → Artifact proves this transformation
- JTBD Altitude System → Level 2-3 language in all templates
- Revolutionary Hope Tone → Celebratory, not pressuring
- 4 Habits Branding → All 4 habits visible in Section 6

**Technical Standards:**
- Discord.py → DM/thread system, command handlers
- State machine design → Artifact progression states
- Background jobs → Reminder nudges, celebration posts

---

## Dev Agent Record

### Completion Summary

**Story 4.6 designs the complete artifact creation flow that guides students through producing their Thinking Artifact - the graduation deliverable that proves identity transformation.**

**Key Design Decisions:**

1. ✅ **/create-artifact Command:** Entry point with clear introduction, example artifact, and step-by-step guidance
2. ✅ **6-Section Structure:** Implements Decision 13 structure with templates and examples for each section
3. ✅ **CIS Agent Integration:** Each section maps to specific CIS agents (/frame, /diverge, /challenge, /synthesize)
4. ✅ **Week-Based Progression:** Week 6 introduction, Week 6-7 workthrough, Week 8 polish/publish
5. ✅ **Private→Public Flow:** DM creation → #thinking-showcase publication (Decision 12)
6. ✅ **Identity Evidence:** Artifact proves JTBD social job for self, parents, future
7. ✅ **4 Habits Visibility:** All 4 habits visible in Section 6 (WHAT THIS TAUGHT ME)
8. ✅ **Save/Resume System:** artifact_progress data structure with state tracking
9. ✅ **Reminder Nudges:** Gentle 3+ day inactivity reminders
10. ✅ **Controller Integration:** Complete state machine, commands, and background jobs specified

**Integration with Epic 4 CIS Agent System:**
- Builds on Stories 4.1 (Controller), 4.2 (Framer), 4.3 (Explorer), 4.4 (Challenger), 4.5 (Synthesizer)
- Artifact creation is the culminating use case for all CIS agents
- Shows how agents work together to produce graduation deliverable

**Foundation Compliance:**
- All Epic 1 foundations honored (Guardrails, JTBD, Node Architecture, 4 Habits)
- Decisions 11, 12, 13, 14 fully implemented
- Epic 6 requirements cross-referenced and supported

**Next Stories (Dependencies):**
- Story 4.7: Discord bot technical specification (implements this design)
- Epic 6: Artifact System & Measurement (builds upon this foundation)

### File List

**Output File:**
- `_bmad-output/implementation-artifacts/4-6-artifact-creation-flow.md` (this file)

**Referenced Foundation Documents:**
- `_bmad-output/cohort-design-artifacts/cohort-playbook-v2-requirements.md` (Decisions 11-14)
- `_bmad-output/cohort-design-artifacts/playbook-v2/01-philosophy/` (Epic 1 foundations)
- `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/` (Epic 4 CIS agent stories)

**Integration Points:**
- Epic 6 stories (6.1, 6.2, 6.3, 6.5, 6.6) will build upon this artifact creation flow
- Story 4.7 (Discord bot) will implement the technical specifications

---

**Story 4.6 Status: ✅ READY FOR IMPLEMENTATION**

The artifact creation flow is fully designed with:
- ✅ Complete 6-section workflow with templates and examples
- ✅ CIS agent integration for each section
- ✅ Private→Public architecture (Decision 12)
- ✅ Identity transformation evidence framework
- ✅ Week-based progression protocol (Weeks 6-8)
- ✅ Controller integration specifications (state tracking, commands, background jobs)
- ✅ All 8 Acceptance Criteria met

Developer can now implement the /create-artifact command using this design and the CIS Controller architecture from Story 4.1.
