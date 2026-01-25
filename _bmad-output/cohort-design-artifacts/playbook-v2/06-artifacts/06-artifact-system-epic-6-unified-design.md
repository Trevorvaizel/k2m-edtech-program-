# Epic 6: Artifact System & Measurement - Unified Module Design

**Epic:** 6 - Artifact System & Measurement (Modules 10, 12)
**Status:** Design Document - Unified Architecture
**Created:** 2026-01-25
**Design Approach:** Holistic System Design (all 6 stories designed together for cross-story consistency)
**Purpose:** Complete specification for multi-stakeholder artifact system serving JTBD social job

---

## Executive Summary

**The Core Problem:**

Story 4.6 designed the artifact CREATION workflow (the /create-artifact command, CIS agent integration, state tracking). Story 2.5 designed the Week 8 showcase event. Epic 1 established the philosophical foundation (Guardrails, JTBD, Node Architecture, 4 Habits).

**What Epic 6 Provides:**

Epic 6 designs the **ARTIFACT OUTPUT ECOSYSTEM** - four stakeholder-facing views that render the same artifact data for different audiences:
1. **Student Creation View** (6.1) - Editable template with prompts, examples, CIS integration
2. **Public Showcase View** (6.2) - Read-only celebration format for peer community
3. **Parent Report View** (6.5) - Translated format emphasizing outcomes and maturity
4. **Credential View** (6.6) - Portfolio-ready graduation card with 4 Habits badges

Plus the supporting systems:
5. **Success Metrics** (6.3) - Thinking demonstration rubric and quality dimensions
6. **Verification System** (6.4) - Proof-of-work validation and authenticity checks

**Architectural Pattern:**

```
┌─────────────────────────────────────────────────────────┐
│              MODEL (Data Layer)                          │
│  Artifact Data Schema (from Story 4.6)                  │
│  - section_1_question through section_6_reflection      │
│  - Progress tracking, timestamps, state management      │
└────────────┬────────────────────────────────────────────┘
             │
             │ Shared Data Model
             │
      ┌──────┴──────┐──────────────┐──────────────┐
      │              │              │              │
┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
│   VIEW    │ │   VIEW    │ │   VIEW    │ │   VIEW    │
│ Student   │ │ Showcase  │ │  Parent   │ │Credential │
│ Creation  │ │ Public    │ │  Report   │ │  Card     │
│  Template │ │  Format   │ │  Format   │ │  Design   │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │            │            │            │
      │ Renderers for Different Stakeholders            │
      └────────────┴────────────┴────────────┴──────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│            CONTROLLER (Workflow Layer)                   │
│  /create-artifact command (from Story 4.6)              │
│  - State tracking, save/resume, reminder nudges         │
│  - Polish flow, publish flow, celebration automation    │
└─────────────────────────────────────────────────────────┘
```

**Design Philosophy:**

The same artifact data serves different emotional needs through different renderers:
- **Students** → Safety + Clarity (private creation space, clear guidance)
- **Peers** → Celebration + Learning (gallery-style showcase, not competition)
- **Parents** → Validation + Proof (outcomes emphasized, not abstract "AI skills")
- **Universities** → Credibility + Evidence (structured thinking demonstrated)

All views maintain:
- ✅ Consistent 4 Habits branding (⏸️ 🎯 🔄 🧠)
- ✅ Unified brand voice (Revolutionary Hope tone)
- ✅ JTBD altitude appropriateness (Level 2-3 for students/parents, Level 4 for credential)
- ✅ Authentic student voice (not AI-generated)

---

## Foundation Documents (All Non-Negotiable)

### Epic 0 & Epic 1 Foundations

**Epic 0.1: Requirements Document** (`cohort-playbook-v2-requirements.md`)
- Source of truth for all decisions (Decisions 11-14 directly inform Epic 6)

**Epic 1.1: Core Guardrails** (`playbook-v2/01-philosophy/guardrails-preserved.md`)
- Guardrail #3: No tech jargon
- Guardrail #4: Always clarity
- Guardrail #10: Artifact authenticity (student's own voice, not AI)
- Guardrail #11: JTBD examples (real student concerns, not generic scenarios)

**Epic 1.2: JTBD Integration** (`playbook-v2/01-philosophy/jtbd-integration.md`)
- Social Job: "Give me proof I can show to myself, my parents, and my future"
- Target identity: "I am someone who thinks WITH AI"
- Emotional Job: Pride ("I'm proud to share this")

**Epic 1.3: Node Architecture** (`playbook-v2/01-philosophy/node-architecture.md`)
- Zone 3→4 Nodes: "First draft is raw material", "I have opinions about quality", "Direction techniques work", "I made this"

**Epic 1.4: 4 Habits Branding** (`playbook-v2/01-philosophy/four-habits-brand.md`)
- Habit 1 ⏸️ Pause
- Habit 2 🎯 Context
- Habit 3 🔄 Iterate
- Habit 4 🧠 Think First

### Related Stories (Integration Points)

**Story 4.6: Artifact Creation Flow** (`playbook-v2/04-cis-agents/4-6-artifact-creation-flow.md`)
- ✅ COMPLETE: /create-artifact command workflow
- ✅ COMPLETE: CIS agent integration (/frame, /diverge, /challenge, /synthesize)
- ✅ COMPLETE: State tracking system (artifact_progress data structure)
- ✅ COMPLETE: Save/resume functionality
- ✅ COMPLETE: Reminder nudges (3+ day inactivity detection)

**Story 2.5: Week 8 Showcase** (`playbook-v2/02-weekly-design/week-8-artifact-showcase.md`)
- ✅ COMPLETE: Week 8 daily prompts (Monday-Friday)
- ✅ COMPLETE: Graduation ceremony script
- ✅ COMPLETE: 4 Habits graduation card design
- ✅ COMPLETE: Privacy choice system (public/anonymous/private)

### Decisions (Requirements)

**Decision 11: CIS Agent System** (`cohort-playbook-v2-requirements.md` lines 243-275)
- Gradual introduction from Week 1
- All 4 agents active by Week 6

**Decision 12: Hybrid Discord Model** (`cohort-playbook-v2-requirements.md` lines 273-292)
- Private process (#thinking-lab) → Public showcase (#thinking-showcase)

**Decision 13: Thinking Artifact** (`cohort-playbook-v2-requirements.md` lines 293-327)
- 6-section structure defined
- Artifact types: Personal Thinking Map, Problem Exploration Brief, Future-Facing Concept
- Key quote: "They don't want help answering questions. They want help becoming the kind of person who answers well."

**Decision 14: Artifact Timeline** (`cohort-playbook-v2-requirements.md` lines 328-335)
- Weeks 6-7: Artifact creation begins
- Week 8: Artifact completion, polish, and showcase

---

## Cross-Story Design System

**Shared Components Used Across All Epic 6 Stories:**

### 1. Data Model (Unified)

All 6 stories use the same artifact data structure from Story 4.6:

```python
class ArtifactProgress:
    # Section content (from Story 4.6 lines 733-795)
    section_1_question: str = ""      # THE QUESTION I WRESTLED WITH
    section_2_reframed: str = ""      # HOW I REFRAMED IT (/frame)
    section_3_explored: str = ""      # WHAT I EXPLORED (/diverge)
    section_4_challenged: str = ""    # WHAT I CHALLENGED (/challenge)
    section_5_concluded: str = ""     # WHAT I CONCLUDED (/synthesize)
    section_6_reflection: str = ""    # WHAT THIS TAUGHT ME

    # Metadata (from Story 4.6)
    completed_sections: List[str] = []
    status: str = "not_started"        # "not_started" | "in_progress" | "completed" | "published"
    started_at: datetime = None
    completed_at: datetime = None
    published_at: datetime = None

    # Student info
    student_id: str
    student_name: str (optional, for showcase)
    privacy_choice: str = "public"     # "public" | "anonymous" | "private"
```

**Design Principle:** Single source of truth. All views render the same data, never duplicate or diverge.

### 2. Brand Voice (Unified)

**Tone:** Revolutionary Hope (celebration + empowerment)

**Language Levels:**
- Student/Parent Views: Level 2-3 (practical, accessible, warm)
- Credential View: Level 4 (identity-focused, professional)

**Key Phrases (Consistent Across All Views):**
- "I am someone who thinks WITH AI" (identity statement)
- "Tools change. Habits transfer." (transferability)
- "Copy-pasters get stuck. Thinkers thrive." (positioning)

**Prohibited Phrases (Guardrail #3):**
- No "prompt engineering"
- No "AI literacy"
- No technical jargon

### 3. 4 Habits Branding (Unified)

**Icons (Consistent Across All Views):**
- ⏸️ Pause
- 🎯 Context
- 🔄 Iterate
- 🧠 Think First

**Visibility Pattern:**
- Student View: All 4 habits emphasized in Section 6 template
- Showcase View: All 4 badges displayed at bottom
- Parent View: All 4 habits translated to parent-language outcomes
- Credential View: All 4 badges earned + certificate

### 4. Quality Dimensions (Unified)

**From Story 4.6 lines 700-730 (Artifact Quality Guidance Framework) + Epic 6 Enhancement:**

All Epic 6 stories use these same 5 quality dimensions:

1. **Depth of Thinking** - "I explored 3 angles" vs "I tried one thing"
2. **Authentic Voice** - Sounds like the student, not ChatGPT
3. **Habit Visibility** - Specific examples, not just "I used all 4 habits"
4. **Before/After Clarity** - "I used to think X. Now I see Y."
5. **Zone Shift Evidence (Identity Transformation)** - "I made this" ownership language vs "AI helped me" collaboration language (Zone 3→4 director identity, Node 3.4)

**Design Principle:** These dimensions apply to ALL views, not just student creation.

**Dual-Pillar Integration (Decision 17):**
All quality dimensions should demonstrate BOTH capabilities:
- **Pillar 1 (Democratized Intelligence):** Enhanced thinking - "I can think clearly"
- **Pillar 2 (Democratized Expertise):** Accessed knowledge - "I can access expert knowledge I don't have"

### 5. Design Tokens (Visual Consistency)

**Colors (for credential card and showcase formatting):**
- Pause: Blue (#2196F3)
- Context: Green (#4CAF50)
- Iterate: Orange (#FF9800)
- Think First: Purple (#9C27B0)

**Typography:**
- Headings: Bold, larger size
- Section dividers: Horizontal rules (---)
- Emphasis: Bold or CAPS for key phrases

**Layout Patterns:**
- Student View: Clean, ample whitespace, clear section headers
- Showcase View: Gallery-style, celebratory framing
- Parent View: Outcome-focused, summary at top
- Credential View: Professional, certificate formatting

---

## Story 6.1: Thinking Artifact Template (Student Creation View)

**Status:** Design Specification
**Purpose:** Editable template students use to create their artifact
**View Type:** Creation/Edit Interface
**Primary Stakeholder:** Students (Zone 3→4, Weeks 6-8)
**Emotional Need:** Safety + Clarity (not intimidation)

---

### Acceptance Criteria (8 Total)

**AC1: Foundation Integration**
- ✅ All 11 Guardrails from Epic 1.1 enforced (see Guardrails Compliance section)
- ✅ JTBD Integration from Epic 1.2 (Functional, Emotional, Social jobs served)
- ✅ Node Architecture from Epic 1.3 (Zone 3→4 nodes 3.1-3.4 mapped to sections)
- ✅ 4 Habits Branding from Epic 1.4 (all 4 habits visible in Section 6)

**AC2: Decision Alignment**
- ✅ Decision 13 (6-section artifact structure implemented)
- ✅ Decision 14 (Weeks 6-7 creation, Week 8 showcase timeline)
- ✅ Decision 17 (Dual-Pillar integration: Intelligence + Expertise in Section 6)

**AC3: Cross-Story Integration**
- ✅ Story 4.6 (Artifact creation flow, CIS agent scaffolding, state tracking)
- ✅ Story 2.5 (Week 8 showcase event, privacy options, graduation card)
- ✅ Story 5.3 (Parent email delivery infrastructure for parent report)

**AC4: Technical Completeness**
- ✅ All 6 template sections specified with prompts, examples, quality checks
- ✅ Voice check prompts after every section (Guardrail #10 enforcement)
- ✅ Stuck pattern interventions from Story 4.6 lines 673-698 integrated
- ✅ Save/resume functionality from Story 4.6 artifact_progress schema

**AC5: Stakeholder Needs Met**
- ✅ Student emotional need: Safety + Clarity (psychological safety maintained)
- ✅ Parent emotional need: Proof of value (artifact demonstrates growth)
- ✅ University/employer need: Evidence of structured thinking capability

**AC6: Brand Voice Compliance**
- ✅ JTBD Altitude Level 2-3 throughout (accessible, practical, warm)
- ✅ Revolutionary Hope tone (celebration + empowerment, not pressure)
- ✅ Key taglines: "Tools change. Habits transfer." consistently applied

**AC7: Quality Framework Defined**
- ✅ 5 Quality Dimensions specified (Depth, Voice, Habits, Before/After, Zone Shift Evidence)
- ✅ Student self-assessment rubric (not grading - guidance only)
- ✅ "Honest > Perfect" philosophy enforced throughout

**AC8: Implementation-Ready**
- ✅ Clear handoff to Story 6.2 (showcase format uses same data model)
- ✅ Clear handoff to Story 6.5 (parent report translates from this template)
- ✅ Clear handoff to Story 6.6 (graduation card awarded after completion)

---

### Template Design Specification

**Document Format:** Markdown (for Discord rendering) + optional PDF export

**Template Structure:**

```markdown
# Thinking Artifact: [Your Name]

**Week 8 - K2M Cohort**

---

## THE QUESTION I WRESTLED WITH ⏸️

[Your question here - 1-2 sentences]

*Guidance: Pick a real question you're facing - university choice, career direction, personal dilemma, academic challenge, anything you're genuinely wrestling with.*

---

## HOW I REFRAMED IT 🎯

[Using /frame with The Framer, I realized...]

*Guidance: What did /frame help you see? Did your question clarify? Did you discover what you were really asking?*

---

## WHAT I EXPLORED 🔄

[Using /diverge with The Explorer, I explored...]

*Guidance: What angles did you explore? What options did you discover? What surprised you?*

---

## WHAT I CHALLENGED 🧠

[Using /challenge with The Challenger, I tested...]

*Guidance: What assumptions did you question? What did challenging reveal? How did your thinking shift?*

---

## WHAT I CONCLUDED ✨

[Using /synthesize with The Synthesizer, I crystalized...]

*Guidance: What's your current best thinking? What are you taking forward? You don't need final answers - just honest conclusions.*

---

## WHAT THIS TAUGHT ME 🌟

**Before K2M, I felt...**
[What anxiety did you feel about AI and your future? Did you feel behind? Like you didn't know enough?]

**The shift happened when I realized...**
[What expertise could you access that you didn't have before? What knowledge opened up to you?]

**Now I can:**
- **Access expertise I don't have** (I'm no longer limited by what I know today)
- **Think clearly with that expertise** (I can use knowledge effectively, not just collect it)

**How I'll use these habits going forward:**

- **Habit 1 ⏸️ Pause:** [When will you pause before asking?]
- **Habit 2 🎯 Context:** [When will you explain your situation first?]
- **Habit 3 🔄 Iterate:** [When will you explore multiple angles?]
- **Habit 4 🧠 Think First:** [When will you use AI to access expertise before decisions?]

**What changed for me:**
[Compare your Week 1 self to Week 8 self. What's different? Do you feel like you belong in AI conversations now?]

*Guidance: This is the most important section. Show your emotional journey (anxiety→confidence), your dual capabilities (access expertise + think clearly), and how you've transformed. Be honest.*

---

**I can access expert knowledge I don't have—and think clearly with it.**

*Completed: [Date]*
```

### Section-Specific Guidance

**Section 1: THE QUESTION I WRESTLED WITH**

*Purpose:* Establish the real question (Habit 1: Pause)

*Prompts (from Story 4.6 lines 373-400):*
- "What's a decision you're facing?"
- "What's confusing you right now?"
- "What do you wish you had clarity on?"

*Examples (Decision 13 lines 300-306):*
- "I need to choose between medicine and computer science"
- "I'm struggling with math and don't know how to improve"
- "I feel pressure to study engineering but I'm not sure it's right"

*Quality Check:*
- ✅ It's REAL (student actually faces this)
- ✅ It's COMPLEX (no easy answers)
- ✅ It matters TO THEM
- ✅ Room to explore (not already solved)

**Section 2: HOW I REFRAMED IT**

*Purpose:* Show Habit 2 (Context) in action

*CIS Agent Integration:* /frame helps clarify what they're really asking

*Prompts:*
- "What did you originally think you were asking?"
- "What did /frame help you see?"
- "How did your question change?"

*Example (Story 4.6 lines 447-458):*
"Originally I thought I was choosing between medicine and CS. Using /frame, I realized I'm actually asking 'What do I value?' I care about solving real problems, creative work, and having options."

*Quality Check:*
- ✅ Shows /frame was used
- ✅ Demonstrates question clarifying
- ✅ Habit 2 (Context) visible

**Section 3: WHAT I EXPLORED**

*Purpose:* Show Habit 3 (Iterate) in action

*CIS Agent Integration:* /diverge explores multiple angles

*Prompts:*
- "What angles did you explore?"
- "What options did you discover?"
- "What surprised you?"

*Example (Story 4.6 lines 497-509):*
"Using /diverge, I explored 3 angles:
1. What if I combined them? (Medical technology)
2. What if I questioned the binary? (Data science for public health)
3. What if I tried before committing? (Volunteer + build app)"

*Quality Check:*
- ✅ Shows breadth (2-3 angles minimum)
- ✅ Uses /diverge
- ✅ Habit 3 (Iterate) visible

**Section 4: WHAT I CHALLENGED**

*Purpose:* Show Habit 4 (Think First) in action

*CIS Agent Integration:* /challenge stress-tests assumptions

*Prompts:*
- "What assumptions did you question?"
- "What did challenging reveal?"
- "How did your thinking shift?"

*Example (Story 4.6 lines 549-561):*
"Using /challenge, I tested my assumptions:
1. 'My parents will be disappointed' → Challenge: What if they want me to be happy?
2. 'I need to decide now' → Challenge: What if first year is FOR exploration?
3. 'CS isn't helping people' → Challenge: What if health tech helps more?"

*Quality Check:*
- ✅ Shows 2-3 assumptions challenged
- ✅ Uses /challenge
- ✅ Habit 4 (Think First) visible

**Section 5: WHAT I CONCLUDED**

*Purpose:* Synthesis and ownership

*CIS Agent Integration:* /synthesize crystalizes insights

*Prompts:*
- "What's your core insight?"
- "What are you concluding (if anything)?"
- "What are you taking forward?"

*Example (Story 4.6 lines 599-608):*
"Using /synthesize, I crystalized: The real question isn't medicine vs CS - it's 'How do I want to help people?'
My conclusion:
1. Try both (volunteer + build app)
2. Keep options open (apply to both)
3. Decide later (first year is for exploration)"

*Quality Check:*
- ✅ Shows synthesis
- ✅ Ownership language ("I decided", "I'm going to")
- ✅ Honest (not pretending certainty)

**Section 6: WHAT THIS TAUGHT ME**

*Purpose:* Identity transformation proof + Emotional journey (anxiety→belonging) + Dual capabilities demonstration

*Structure:*
1. "Before K2M, I felt..." (emotional state: anxiety, feeling behind)
2. "The shift happened when I realized..." (expertise access unlock - Decision 17 Pillar 2)
3. "Now I can..." (dual capabilities: access expertise + think clearly - Decision 17 Both Pillars)
4. 4 Habits Future Application (specific situations)
5. "What changed for me" (emotional transformation: anxiety→confidence, outsider→belonging)

*Node Architecture Integration (Epic 1.3):*
- Node 3.1 "First draft is raw material" → Visible in Section 4 (challenging process)
- Node 3.2 "I have opinions about quality" → Visible in Section 5 (synthesis ownership)
- Node 3.3 "Direction techniques work" → Visible in all 4 CIS agent uses
- Node 3.4 "I made this" → Visible in Section 6 (ownership language)

*Example (Updated with Dual-Pillar + Emotional Job):*
"**Before K2M, I felt...**
I felt anxious about university and my future. Everyone else seemed to know things I didn't—about courses, careers, how to make smart decisions. I felt behind, like I was faking it.

**The shift happened when I realized...**
I could access expert knowledge I didn't have. I didn't need to know everything about medicine AND computer science—I could tap into that expertise through AI and use it to think clearly.

**Now I can:**
- **Access expertise I don't have** (Medical knowledge, CS concepts, career guidance—I'm not limited by what I know today)
- **Think clearly with that expertise** (I don't just copy answers—I use knowledge to make my own decisions)

**How I'll use these habits going forward:**
- Habit 1 (Pause): When I'm confused in university lectures, I'll pause before asking—what do I actually want to understand?
- Habit 2 (Context): I'll explain my full situation to AI, not just 'help me with this assignment'
- Habit 3 (Iterate): I'll explore multiple approaches to problems instead of accepting the first solution
- Habit 4 (Think First): Before choosing courses or career paths, I'll use AI to access expert perspectives I don't have

**What changed for me:**
Week 1: I felt like an outsider in AI conversations, anxious I'd be left behind.
Week 8: I feel like I belong. I'm not someone who 'mastered AI'—I'm someone who learned how to access knowledge and think with it clearly.

I can access expert knowledge I don't have—and think clearly with it."

*Quality Check:*
- ✅ Emotional journey visible (anxiety→confidence, outsider→belonging) - Epic 1.2 JTBD Emotional Job
- ✅ Dual capabilities demonstrated (Pillar 1: Intelligence + Pillar 2: Expertise) - Decision 17
- ✅ Before/after comparison clear
- ✅ All 4 Habits visible with SPECIFIC examples
- ✅ Zone 3→4 identity shift (collaborator→director, "I made this" Node 3.4)
- ✅ Future application specific (not vague "I'll use these habits")

### Template Features

**From Story 4.6 Integration:**

- ✅ Save/resume functionality (artifact_progress state tracking)
- ✅ Section-by-section completion (can't skip ahead)
- ✅ CIS agent integration (/frame, /diverge, /challenge, /synthesize)
- ✅ Gentle reminders if inactive 3+ days
- ✅ Quality guidance (not grading) - "Honest > Perfect"
- ✅ Stuck pattern interventions (Story 4.6 lines 673-698 - see section below)

**Additional Features (Epic 6.1 Enhancements):**

- ✅ Printable PDF export option (for offline work)
- ✅ Example artifacts linked (for inspiration, not copying)
- ✅ Voice check prompts after EVERY section ("Does this sound like YOU?")
- ✅ Completion checklist (all 6 sections, quality dimensions)

### Stuck Pattern Interventions (H12 Fix - Story 4.6 Integration)

**From Story 4.6 lines 673-698 (Stuck Pattern Detection & Targeted Interventions):**

When students get stuck during artifact creation, the agent detects specific patterns and triggers targeted help:

**Pattern 1: Can't Think of a Question (Section 1)**
```markdown
**Feeling stuck on choosing your question?**

Try this:
- What decision are you facing right now? (university, career, study method)
- What's confusing you about your future?
- What do you wish you had clarity on?

Don't overthink it. Pick something REAL you're wrestling with.
Type: **help** for more guidance, or **continue** when ready.
```

**Pattern 2: Question Too Small/Obvious (Section 1)**
```markdown
**Your question feels too simple?**

That's okay! The depth comes from HOW you think through it, not the question itself.

Try reframing: Instead of "Should I study harder?" ask "What study approach works for MY brain?"
Type: **reframe** to try /frame, or **continue** if you're happy with it.
```

**Pattern 3: Exploration Feels Forced (Section 3)**
```markdown
**Stuck on Section 3 (WHAT I EXPLORED)?**

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

Type: **continue** to keep going, or **help** for more guidance.
```

**Pattern 4: Challenging Feels Harsh (Section 4)**
```markdown
**Checking in on Section 4 (WHAT I CHALLENGED)** 🧠

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

Type: **continue** or **help**
```

**Pattern 5: Can't Synthesize (Section 5)**
```markdown
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

Type: **continue** or **help**
```

**Pattern 6: Reflection Feels Fake (Section 6)**
```markdown
**Section 6 - The Most Important Section** 🌟

If reflection feels fake or forced, here's why:

**You're trying to sound impressive instead of being honest.**

Parents want to hear YOU, not a polished essay.

Try this:
1. What did you ACTUALLY feel before K2M? (Anxiety? Confusion? Pressure?)
2. What changed for you? (Even small shifts matter)
3. Write like you're explaining to a friend, not writing an essay

**Voice Check:**
- Does this sound like YOU talking?
- Or does it sound like ChatGPT?

If it sounds fake, start over with ONE honest sentence. Build from there.

Type: **continue** when ready, or **help** if still stuck.
```

**Agent Detection Logic (from Story 4.6):**
- Section 1 stuck (2+ days inactive) → Pattern 1 or Pattern 2 intervention
- Section 3 stuck (2+ days inactive) → Pattern 3 intervention
- Section 4 stuck (2+ days inactive) → Pattern 4 intervention
- Section 5 stuck (2+ days inactive) → Pattern 5 intervention
- Section 6 stuck (2+ days inactive) → Pattern 6 intervention

**Reference:** Story 4.6 lines 673-698 for complete stuck pattern library and detection logic.

### Guardrails Compliance (ALL 11 - Epic 1.1)

**Guardrail #1 (Never Give Advice):** ✅
- Template uses invitational prompts ("What did you explore?" not "You should explore...")
- No directive language in guidance sections
- Student discovers their own answers through reflection

**Guardrail #2 (Always Invite Student Discovery):** ✅
- All prompts are questions, not statements
- "What did YOU notice?" framing throughout
- Guidance invites exploration, doesn't prescribe answers

**Guardrail #3 (No Tech Jargon):** ✅
- All section titles use everyday language
- No "prompt engineering" or "AI literacy" terms
- CIS agents described as "thinking tools" in student-facing language

**Guardrail #4 (Always Clarity):** ✅
- Step-by-step guidance for each section
- Clear examples provided for every section
- Quality checks explain expectations without grading

**Guardrail #5 (Never Compare Students):** ✅
- No rankings or "best artifact" language
- Quality dimensions for self-assessment, not comparison
- "Honest > Perfect" philosophy prevents competition

**Guardrail #6 (Always Psychological Safety):** ✅
- Privacy options (public/anonymous/private) respect student comfort
- "Honest uncertainty > Fake certainty" messaging
- No judgment for incomplete or messy thinking

**Guardrail #7 (Node Quality Over Quantity):** ✅
- Zone 3→4 nodes (3.1-3.4) integrated into template design
- Focus on depth (Node 3.2 "opinions about quality") not speed
- Reflection prioritized over rapid completion

**Guardrail #8 (Agent Model Consistency):** ✅
- CIS agents integrated exactly as designed in Story 4.6
- No human facilitator advice-giving
- Agent scaffolds discovery, doesn't direct answers

**Guardrail #9 (Discord Safety):** ✅
- Private creation in #thinking-lab (Decision 12)
- Public showcase celebrates, never critiques
- Privacy controls prevent unwanted exposure

**Guardrail #10 (Artifact Authenticity):** ✅
- Explicit warning: "This must be YOUR voice, not AI-generated"
- Voice check prompts after every section
- Section 6 cannot be AI-generated (too personal)
- Proof-of-work verification (paste sentence from CIS interaction)

**Guardrail #11 (JTBD Examples):** ✅
- All examples serve real pre-university student concerns
- Medicine vs CS (career anxiety), university preparation (future readiness)
- No generic "business use cases" - age-appropriate scenarios only

---

## Story 6.2: Artifact Showcase Format (Public Peer View)

**Status:** Design Specification
**Purpose:** Read-only format for public display in #thinking-showcase
**View Type:** Gallery/Showcase Interface
**Primary Stakeholder:** Peers (fellow students in cohort)
**Emotional Need:** Celebration + Learning (NOT comparison!)

---

### Acceptance Criteria (8 Total)

**AC1: Foundation Integration**
- ✅ Guardrail #5 (Never Compare Students) enforced - no rankings or "best artifact" language
- ✅ Guardrail #8 (Discord Safety) implemented - privacy options respected
- ✅ JTBD Social Job served - peer learning through finished work visibility
- ✅ 4 Habits Branding visible - all 4 badges displayed at bottom

**AC2: Decision Alignment**
- ✅ Decision 12 (Hybrid Discord Model) - public showcase of private work
- ✅ Decision 13 (6-section artifact) - complete structure displayed
- ✅ Decision 17 (Dual-Pillar) - Both Intelligence + Expertise visible in showcased artifacts

**AC3: Cross-Story Integration**
- ✅ Story 6.1 (Student Template) - uses same artifact_progress data model
- ✅ Story 2.5 (Week 8 Showcase) - privacy controls aligned, celebration patterns match
- ✅ Story 5.3 (#thinking-showcase) - publication workflow, SafetyFilter validation

**AC4: Technical Completeness**
- ✅ Privacy options specified (Public/Anonymous/Private) with display formats
- ✅ Celebration design prevents comparison (aggregate visibility only, no rankings)
- ✅ Peer engagement prompts defined (specific, concrete, celebration-focused)
- ✅ Agent behavior for showcase week automated (posting, highlights, tracking)

**AC5: Stakeholder Needs Met**
- ✅ Peer emotional need: Inspiration + Belonging (not competition)
- ✅ Student emotional need: Validation + Pride (social proof)
- ✅ Facilitator need: Celebration culture monitoring (Trevor's 10% workflow)

**AC6: Brand Voice Compliance**
- ✅ Revolutionary Hope tone throughout (celebration, not pressure)
- ✅ No comparison language enforced (SafetyFilter blocks violations)
- ✅ Taglines consistent: "That's someone who thinks WITH AI!"

**AC7: Quality Framework Defined**
- ✅ Celebration quality rules specified (no "best", "top", comparative language)
- ✅ Diverse thinking highlighted (not output quality)
- ✅ Daily highlight selection criteria (diverse artifacts, not rankings)

**AC8: Implementation-Ready**
- ✅ Showcase format template ready for Discord rendering
- ✅ Agent automation spec ready for Story 4.7 (bot implementation)
- ✅ Privacy control logic ready for implementation

---

### Showcase Format Specification

**Location:** Discord #thinking-showcase channel (from Decision 12)

**Display Format:**

```markdown
**Thinking Artifact: {Student Name or "Anonymous"}** 🌟

*Completed: Week 8*

---

## THE QUESTION I WRESTLED WITH ⏸️

{section_1_question}

---

## HOW I REFRAMED IT 🎯

{section_2_reframed}

---

## WHAT I EXPLORED 🔄

{section_3_explored}

---

## WHAT I CHALLENGED 🧠

{section_4_challenged}

---

## WHAT I CONCLUDED ✨

{section_5_concluded}

---

## WHAT THIS TAUGHT ME 🌟

{section_6_reflection}

---

**4 Habits Earned:** ⏸️ 🎯 🔄 🧠

*Celebrate with reactions below! 👇*
```

### Showcase Features

**Privacy Options (from Story 2.5 lines 124-153):**

1. **Public Showcase:**
   - Student's name attached
   - Full artifact visible
   - Peers can react and comment
   - Best for social proof

2. **Anonymous Showcase (M8 Fix - Anonymous Display Format):**
   - **Display Format:** "🌟 Anonymous Graduate 🌟" (generic, no numbers/distinguishers)
   - **Timing:** All anonymous artifacts posted simultaneously (Friday Week 8 batch) to prevent timing identification
   - **Content Check:** Agent checks anonymous artifacts for identifying details before posting (removes specific school names, unique circumstances)
   - Full artifact visible
   - Peers can react and comment
   - Privacy protected - no way to identify student from post timing or content
   - **Rationale:** True anonymity prevents identification by timing, content patterns, or writing style

3. **Private Submission:**
   - Only Trevor sees artifact
   - Still receives 4 Habits card
   - Valid choice for sensitive topics
   - No public showcase entry

**Celebration Design (from Story 2.5):**

- ✅ No rankings or "best artifact" awards
- ✅ No critique or feedback (this is celebration, not improvement)
- ✅ Focus on thinking diversity, not output quality
- ✅ Peer engagement prompts: "Celebrate ONE thing that shows their thinking"
- ✅ Daily highlights showcasing diverse artifacts (see M3 Fix below)

**M3 Fix - Daily Highlight Selection Criteria (Showcase Diversity):**

**Purpose:** Celebrate diverse thinking approaches, NOT output quality or "best" artifacts.

**Selection Process:**
- **Frequency:** 3 artifacts highlighted per day (Monday-Friday Week 8)
- **Selection Method:** Trevor or agent randomly selects from completed artifacts using diversity criteria below
- **Highlight Format:** Pinned message with "🌟 Today's Thinking Diversity 🌟" header

**Diversity Criteria (Rotate through these):**
1. **Different Question Domains:**
   - Career decisions (medicine vs CS, engineering vs arts)
   - Academic challenges (study methods, subject confusion)
   - Personal dilemmas (identity, values, relationships)
   - Social pressure (parent expectations, peer influence)

2. **Different Thinking Approaches:**
   - Analytical (logical, systematic, structured)
   - Creative (imaginative, unconventional, experimental)
   - Values-driven (ethical, purpose-focused, identity-based)
   - Exploratory (questioning, uncertain, open-ended)

3. **Different Conclusion Types:**
   - Certain conclusions ("I decided X")
   - Uncertain explorations ("I'm still figuring this out")
   - New questions emerged ("This led me to ask Y")
   - Perspective shifts ("I used to think X, now I see Y")

**Highlight Message Template:**
```markdown
🌟 **Today's Thinking Diversity** 🌟

Today we're celebrating 3 different ways students think:

1. [Student/Anonymous] - Career exploration through challenging assumptions
2. [Student/Anonymous] - Academic problem-solving with iterative experiments
3. [Student/Anonymous] - Identity questions explored with openness to uncertainty

Each shows thinking WITH AI, not copying FROM it.

Diverse paths. Same growth. 🌟
```

**What We DON'T Highlight:**
- ❌ "Best" or "top" quality artifacts (no quality judgment)
- ❌ Longest or most detailed artifacts (not a word count contest)
- ❌ Most polished writing (authenticity > polish)
- ❌ "Correct" conclusions (no right answers in thinking)

**Rationale:** Celebrating diversity prevents implicit comparison, normalizes different thinking styles, honors Guardrail #5.

**Peer Engagement Prompts (from Story 2.5 lines 367-385):**

```markdown
**Today's Task: Engage with 2-3 peers' artifacts**

For each artifact, share:

1️⃣ ONE thing that shows their thinking:
   "Their 'What I Challenged' section shows they can spot their own assumptions"

2️⃣ ONE thing you found interesting:
   "I never thought about [topic] that way - their exploration gave me a new angle"

3️⃣ Celebrate THEIR journey:
   "It's clear they've grown from Week 1 - this artifact shows someone who thinks WITH AI"

🌟 CELEBRATION RULES:
• No comparisons ("better than" / "worse than")
• No critique (this is celebration, not feedback)
• Focus on thinking, not outputs
• Be specific (not "great job", but "I loved how they...")
```

### Agent Behavior (Showcase Week)

**From Story 2.5 lines 1083-1131:**

- ✅ Automatic posting of completed artifacts
- ✅ Daily celebration highlights (diverse artifacts, not "best")
- ✅ Peer engagement tracking (for celebration metrics)
- ✅ No rankings or quality comparisons
- ✅ Models celebration language: "That's someone who thinks WITH AI!"

### Guardrails Compliance

**Guardrail Rankings Prohibited:** ✅
- No "best artifact" awards
- No quality comparisons
- No tiered recognition

**Celebration Focus:** ✅
- All artifacts celebrated equally
- Diverse thinking highlighted
- Peer learning emphasized

**Privacy Respected:** ✅
- Public/Anonymous/Private choices all equal
- No judgment for private submissions
- Sensitive topics protected

---

## Story 6.3: Success Metrics (Thinking Demonstration)

**Status:** Design Specification
**Purpose:** Define what "success" means for artifact quality
**Measurement Focus:** Thinking demonstration, not output quality
**Stakeholder:** Trevor (facilitator), students (self-assessment), parents (understanding outcomes)

---

### Acceptance Criteria (8 Total)

**AC1: Foundation Integration**
- ✅ Guardrail #5 (No Comparison) - metrics for guidance, not grading/ranking
- ✅ JTBD Emotional Job - Before/After Clarity dimension measures anxiety→confidence
- ✅ Node Architecture - Zone Shift Evidence dimension measures Node 3.4 "I made this"
- ✅ 4 Habits Branding - Habit Visibility dimension ensures all 4 habits demonstrated

**AC2: Decision Alignment**
- ✅ Decision 13 (Artifact demonstrates thinking, not "AI usage") - metrics focus on thinking growth
- ✅ Decision 17 (Dual-Pillar) - Quality dimensions measure BOTH Intelligence + Expertise

**AC3: Cross-Story Integration**
- ✅ Story 6.1 (Student Template) - rubric supports self-assessment during creation
- ✅ Story 6.4 (Verification) - quality dimensions inform verification questions
- ✅ Story 6.5 (Parent Report) - metrics translate to parent-language outcomes

**AC4: Technical Completeness**
- ✅ 5 Quality Dimensions specified (Depth, Voice, Habits, Before/After, Zone Shift)
- ✅ Student self-assessment rubric (checklist format, not scoring)
- ✅ Cohort-level success metrics (completion, engagement, transformation)
- ✅ Parent satisfaction metrics added (M5 fix)

**AC5: Stakeholder Needs Met**
- ✅ Student need: Self-assessment clarity (no grading anxiety)
- ✅ Trevor need: Quality guidance framework (not subjective judgment)
- ✅ Parent need: Understanding outcomes (metrics translate to value)

**AC6: Brand Voice Compliance**
- ✅ "Honest > Perfect" philosophy embedded in all quality dimensions
- ✅ Growth mindset language throughout ("Strong" vs "Developing", not "Pass/Fail")
- ✅ No comparison/ranking enabled by metrics

**AC7: Quality Framework Defined**
- ✅ All 5 dimensions have "Strong" vs "Developing" examples
- ✅ Guidance for students (not assessment criteria)
- ✅ Metrics serve improvement, not judgment

**AC8: Implementation-Ready**
- ✅ Rubric ready for student-facing template integration (Story 6.1)
- ✅ Metrics ready for cohort tracking dashboard (Story 5.1)
- ✅ Parent satisfaction survey ready for Week 8 deployment

---

### Metrics Framework

**Core Philosophy (from Story 4.6 lines 700-730):**

"The #1 Principle: **Honest > Perfect**

A messy authentic artifact is better than a polished generic one. Parents want to hear YOU, not ChatGPT."

### Five Quality Dimensions (Updated with Zone Shift Evidence)

**1. Depth of Thinking (Decision 17 Pillar 1: Intelligence)**

*What It Measures:* breadth and depth of exploration

*Strong:*
- "I explored 3 different angles and discovered X, Y, Z"
- Specific insights from exploration
- Connections between sections visible

*Developing:*
- "I tried one angle and it helped"
- Surface-level exploration
- Sections feel disconnected

*Guidance for Students:*
"Deeper exploration = more meaningful artifact for YOU. Don't rush. Explore multiple angles before concluding."

**2. Authentic Voice (Guardrail #10)**

*What It Measures:* Does it sound like the student?

*Strong:*
- Sounds like YOU - honest, maybe even messy
- Personal voice ("I'm not sure yet", "I'm still figuring this out")
- Specific to their life/circumstances

*Developing:*
- Sounds generic or AI-written
- Template language without personalization
- Vague statements that could apply to anyone

*Guidance for Students:*
"Parents should hear YOU in this artifact, not ChatGPT. Be honest. Be real. Be yourself."

**3. Habit Visibility (Epic 1.4)**

*What It Measures:* Are the 4 Habits visible with specific examples?

*Strong:*
- Specific examples ("When I paused, I realized I was rushing...")
- Each habit has concrete evidence
- Clear connection between habit and outcome

*Developing:*
- "I used all 4 habits" (no specifics)
- Habits listed but not demonstrated
- Generic statements without evidence

*Guidance for Students:*
"Show, don't just tell. Don't say 'I used Habit 3' - show HOW you used it with a specific example."

**4. Before/After Clarity (Epic 1.2 JTBD Emotional Job)**

*What It Measures:* Is emotional and capability growth visible?

*Strong:*
- "I used to feel X (anxious, behind). Now I feel Y (confident, belonging)."
- "I used to think I needed to know everything. Now I realize I can access expertise."
- Clear emotional journey (anxiety→confidence) + capability shift (Decision 17 Both Pillars)
- Specific moments of transformation

*Developing:*
- "I learned a lot" (vague)
- No before emotional state described
- Growth claimed but not shown

*Guidance for Students:*
"Make your emotional journey visible. Week 1 you vs Week 8 you—what changed? How do you FEEL now about AI and your future?"

**5. Zone Shift Evidence / Identity Transformation (Epic 1.3 Node 3.4)**

*What It Measures:* Zone 3→4 shift from collaborator to director

*Strong:*
- **Director ownership language:** "I made this", "I have opinions about quality" (Node 3.2), "I decided"
- Claims agency and expertise access: "I can access expert knowledge I don't have"
- Identity statement: "I can access expert knowledge and think clearly with it" (not "I think WITH AI" - that's Level 4)

*Developing:*
- **Collaborator language:** "AI helped me", "ChatGPT showed me"
- Passive voice: "I was shown", "It made me realize"
- No ownership claims

*Guidance for Students:*
"Show YOUR ownership. Not 'AI helped me' but 'I used AI to access expertise and made my own decision.' YOU are the director now."

### Success Metrics (Cohort Level)

**From Story 2.5 lines 1151-1174:**

**Completion Metrics:**
- 95%+ students submit complete artifact (all 6 sections)
- 90%+ artifacts demonstrate all 4 Habits clearly
- 95%+ students complete completion checklist (self-assessed)

**Showcase Engagement:**
- 90%+ students share artifact (public or anonymous) OR complete private submission
- 80%+ students engage with 2-3 peer artifacts
- 200+ total peer celebration posts (average 1+ per student)

**Identity Transformation:**
- 80%+ can say "I'm someone who thinks WITH AI" and mean it
- 70%+ report at least one habit feels "very natural"
- 60%+ can describe specific situations where they'll use habits going forward

**Emotional Indicators:**
- Students express pride and ownership (not relief to be done)
- Students share artifacts with pride (not reluctance)
- Specific commitments to use habits forward (not vague "I learned a lot")

**M5 Fix - Parent Satisfaction Metrics (JTBD Social Job Validation):**

**Purpose:** Validate that JTBD Social Job is served - "Give me proof I can show to myself, my parents, and my future"

If parents receive report but don't understand value, Social Job FAILS for "parents" audience.

**Parent Satisfaction Survey (Week 8, sent with parent report):**

**Survey Questions:**
1. **Understanding:** "After reading your child's artifact, do you understand what they learned in K2M?" (Yes/Somewhat/No)
2. **Growth Visibility:** "Can you see clear evidence of your child's thinking growth?" (Strongly Agree/Agree/Neutral/Disagree)
3. **Value Perception:** "Was this program worth your child's time?" (Definitely/Probably/Maybe/No)
4. **Recommendation:** "Would you recommend K2M to other parents?" (Yes/Maybe/No)
5. **Sharing Behavior:** "Have you shared your child's artifact with family/friends?" (Yes/Planning to/No)

**Target Metrics:**
- 90%+ parents understand what their child learned (Question 1: Yes/Somewhat)
- 85%+ parents report artifact demonstrates clear thinking growth (Question 2: Strongly Agree/Agree)
- 80%+ parents would recommend K2M based on artifact quality (Question 4: Yes/Maybe)
- 75%+ parents share artifact with family/friends (Question 5: Yes/Planning to) - social proof validation

**Survey Delivery:**
- **When:** Embedded in parent report email (Week 8)
- **Method:** Google Forms link in email footer
- **Incentive:** Optional (raffle for future cohort discount)
- **Privacy:** Anonymous unless parent opts in to share feedback

**Failure Indicators (Require Action):**
- <70% parents understand → Parent report translation needs improvement
- <60% parents see growth → Artifact template needs stronger before/after prompts
- <50% parents would recommend → Value proposition misalignment (serious issue)

**Use Cases:**
- **Product Iteration:** Improve parent report format based on feedback
- **Marketing:** Use satisfaction data for testimonials, case studies
- **Cohort Validation:** Confirm JTBD Social Job served for ALL stakeholders (self, parents, future)

### Rubric Format (For Student Self-Assessment)

**Not for grading - For guidance only:**

```markdown
**Artifact Quality Check** ✅

Before finalizing, ask yourself:

**Depth of Thinking:**
☐ I explored 2-3 angles, not just one
☐ My exploration revealed specific insights
☐ My sections connect to each other

**Authentic Voice:**
☐ This sounds like ME, not ChatGPT
☐ I'm honest about what I don't know yet
☐ My specific circumstances come through

**Habit Visibility:**
☐ Habit 1 (Pause ⏸️): I show HOW I paused
☐ Habit 2 (Context 🎯): I show HOW I explained context
☐ Habit 3 (Iterate 🔄): I show HOW I explored angles
☐ Habit 4 (Think First 🧠): I show HOW I challenged assumptions

**Before/After Clarity:**
☐ I describe my "before" emotional state (anxiety, feeling behind)
☐ I describe my "after" state (confidence, belonging)
☐ I show what changed emotionally AND in capability (access expertise + think clearly)

**Zone Shift Evidence (Ownership):**
☐ I use director language ("I made this", "I decided") not collaborator language ("AI helped me")
☐ I claim expertise access ("I can access knowledge I don't have")
☐ I demonstrate Zone 3→4 shift (from working WITH AI to DIRECTING AI)

**Remember:** Honest > Perfect. Real > Polished. YOU > Generic.
**Dual capabilities:** You can access expertise AND think clearly with it.
```

### Guardrails Compliance

**No Grading:** ✅
- Metrics used for guidance, not assessment
- No pass/fail judgment
- Quality dimensions, not scoring

**Student-Focused:** ✅
- Self-assessment emphasized
- Growth mindset language
- "Honest > Perfect" philosophy

---

## Story 6.4: Shift Verification Questions (Proof-of-Work Validation)

**Status:** Design Specification
**Purpose:** Validate artifact authenticity and transformation
**From:** Decision 5 (Proof-of-Work to Self-Assessment)
**Stakeholder:** Trevor (facilitator verification)

---

### Acceptance Criteria (8 Total)

**AC1: Foundation Integration**
- ✅ Guardrail #10 (Artifact Authenticity) enforced through voice checks
- ✅ Decision 5 (Proof-of-Work) implemented - paste sentence from CIS conversation
- ✅ JTBD Social Job validated - artifact serves as genuine proof

**AC2: Decision Alignment**
- ✅ Decision 2 (90/10 Model) - automated verification + Trevor spot-checks
- ✅ Decision 5 (Proof-of-Work) - mechanical checks for authenticity

**AC3: Cross-Story Integration**
- ✅ Story 6.1 (Template) - verification questions support quality checks
- ✅ Story 6.3 (Metrics) - verification uses 5 Quality Dimensions
- ✅ Story 4.6 (Artifact Flow) - CIS conversation logs validate proof-of-work

**AC4: Technical Completeness**
- ✅ Automated verification checks specified (completion, authenticity, habit visibility)
- ✅ Manual verification criteria for Trevor (voice, growth, habits)
- ✅ False positive detection added (M4 fix - catch performers vs genuine shifters)
- ✅ Escalation protocol documented (stuck students, AI-generated content)

**AC5: Stakeholder Needs Met**
- ✅ Student need: Clear guidance on "ready to publish" (verification as support)
- ✅ Trevor need: Efficient spot-check workflow (15-20 reflections Friday)
- ✅ Cohort need: Authentic artifact showcase (no AI-generated spam)

**AC6: Brand Voice Compliance**
- ✅ Verification framed as "Honest Check" not "Assessment"
- ✅ Growth mindset language ("refine", "add more voice" vs "failed")
- ✅ No grading/judgment tone

**AC7: Quality Framework Defined**
- ✅ Verification aligned with 5 Quality Dimensions from Story 6.3
- ✅ Escalation criteria clear (when to prompt for improvement vs accept as-is)

**AC8: Implementation-Ready**
- ✅ Automated checks ready for bot implementation (mechanical validation)
- ✅ Trevor workflow ready (Friday spot-check, escalation handling)
- ✅ Student-facing verification prompts ready for template integration

---

### Verification Framework

**From Decision 5 (lines 168-177):**

> "After self-assessment, require:
> > 'Paste ONE sentence from Response 2 that shows AI understood YOUR specific situation.'
>
> Rationale:
> - Easy for genuine shifters (they have the sentence)
> - Hard for performers (they'd have to fake it)
> - Agent can mechanically verify"

### Verification Questions

**Automated Verification (Mechanical):**

1. **Completion Check:**
   - All 6 sections have content? (Yes/No)
   - Each section meets minimum length? (Yes/No)

2. **Authenticity Check (Decision 5):**
   - "Paste ONE sentence from Section 2 (HOW I REFRAMED IT) that shows the AI understood YOUR specific situation."
   - Mechanical check: Does response contain a sentence from their artifact?

3. **4 Habits Visibility Check:**
   - Section 6 mentions all 4 habits? (Yes/No)
   - Each habit has specific example? (Mechanical check for keyword presence)

**Manual Verification (Trevor's Friday Spot-Check):**

From Decision 2 (lines 143-148):
> "Friday spot-check: 15-20 student reflections"

**Spot-Check Criteria:**

1. **Voice Check:**
   - Does this sound like the student?
   - Or could this be AI-generated?

2. **Growth Check:**
   - Is before/after comparison visible?
   - Does identity transformation feel genuine?

3. **Habit Check:**
   - Are 4 Habits visible with specifics?
   - Or just listed without evidence?

**Escalation Protocol (from Decision 2):**

> "Escalations: Agent flags students stuck 3+ days"

For verification concerns:
- If artifact feels AI-generated → Agent prompts: "This sounds generic. Can you add more of YOUR voice?"
- If artifact lacks depth → Agent nudges: "You explored one angle. What about [alternative]?"
- If artifact incomplete → Reminder: "You've completed X/6 sections. Type /create-artifact to continue."

### Verification Questions (For Student Reflection)

**Before Publishing:**

```markdown
**Before You Publish - Honest Check** ✨

1️⃣ **Voice Check:**
"Would my parents read this and say 'this sounds like [my name]'?"
If no → Add more of your voice, your specific circumstances, your honesty

2️⃣ **Depth Check:**
"Did I explore multiple angles, or just one?"
If just one → Use /diverge to explore more

3️⃣ **Growth Check:**
"Can I point to specific moments where my thinking changed?"
If no → Refine Section 6 to show your journey

4️⃣ **Honesty Check:**
"Am I being real about where I am, or pretending to be more confident than I am?"
If pretending → It's okay to not have all answers. Honest uncertainty is better than fake certainty.

**Remember:** This isn't about perfection. It's about showing YOUR real thinking journey.
```

### M4 Fix - False Positive Detection (Catch Performers vs Genuine Shifters)

**Problem:** Verification questions above focus on mechanical checks, but miss "false positives" - students who complete checklist but lack genuine transformation.

**False Positive Indicators:**

**1. CIS Agent Usage Verification (Cross-Reference with Logs)**
- **Check:** Did student actually USE CIS agents or just claim they did?
- **Method:** Cross-reference artifact content with CIS conversation logs (timestamps match? Content aligns?)
- **Red Flag:** Student claims "/frame helped me see X" but no /frame conversation in logs
- **Action:** Agent prompts: "I don't see a /frame conversation in your history. Can you try /frame now or remove that claim?"

**2. AI-Generated Prose Detection (Authenticity Check)**
- **Check:** Does artifact sound like student or AI-generated?
- **Red Flags:**
  - Generic language patterns: "In conclusion", "Therefore", "It is evident that"
  - Overly polished prose (no contractions, formal tone)
  - Abstract language instead of specific examples
  - No personal pronouns ("one might consider" vs "I realized")
- **Method:** Agent flags suspicious patterns, Trevor reviews
- **Action:** Agent prompts: "This section sounds generic. Can you add more of YOUR voice? Be specific about YOUR situation."

**3. Generic Growth Claims Detection (Before/After Authenticity)**
- **Check:** Is before/after comparison real or generic template response?
- **Red Flags:**
  - "I learned a lot" (vague)
  - "AI is helpful" (generic claim)
  - "Now I understand better" (no specifics)
  - No emotional language (anxiety, confusion, relief, confidence)
- **Method:** Agent detects template language, prompts for specifics
- **Action:** Agent prompts: "Can you be more specific? What did you FEEL before K2M? What CHANGED for you emotionally?"

**Automated False Positive Detection Workflow:**

```python
def detect_false_positives(artifact, student_cis_logs):
    """Run automated checks for performer patterns"""

    flags = []

    # Check 1: CIS Agent Usage Verification
    if "/frame" in artifact.section_2_reframed:
        if not has_frame_conversation(student_cis_logs):
            flags.append("NO_FRAME_LOG")

    if "/diverge" in artifact.section_3_explored:
        if not has_diverge_conversation(student_cis_logs):
            flags.append("NO_DIVERGE_LOG")

    # Check 2: AI-Generated Prose Patterns
    ai_patterns = ["in conclusion", "therefore", "it is evident", "one might consider"]
    for pattern in ai_patterns:
        if pattern in artifact.section_6_reflection.lower():
            flags.append("AI_PATTERN_DETECTED")

    # Check 3: Generic Growth Claims
    generic_claims = ["i learned a lot", "ai is helpful", "now i understand better"]
    for claim in generic_claims:
        if claim in artifact.section_6_reflection.lower():
            flags.append("GENERIC_CLAIM")

    # Check 4: Emotional Language Presence
    emotional_words = ["anxious", "confused", "scared", "excited", "confident", "relieved"]
    if not any(word in artifact.section_6_reflection.lower() for word in emotional_words):
        flags.append("NO_EMOTIONAL_LANGUAGE")

    return flags

# Agent Response Based on Flags
if flags:
    agent_prompts = {
        "NO_FRAME_LOG": "I don't see a /frame conversation in your history. Can you try /frame now or remove that claim?",
        "AI_PATTERN_DETECTED": "This sounds a bit formal. Can you rewrite in your own words, like you're explaining to a friend?",
        "GENERIC_CLAIM": "Can you be more specific? What exactly did you learn? What changed?",
        "NO_EMOTIONAL_LANGUAGE": "What did you FEEL before K2M? Anxiety? Confusion? Add that emotional journey."
    }

    send_improvement_prompts(student, agent_prompts)
```

**Trevor Manual Review (Spot-Check for False Positives):**

**Friday Spot-Check Process (15-20 artifacts):**
1. Read Section 6 (WHAT THIS TAUGHT ME) only (most revealing section)
2. Ask: "Does this feel genuine or performative?"
3. Red flags:
   - Too polished (no honest struggle visible)
   - Generic claims (could apply to anyone)
   - No specific examples (vague "I learned X")
4. If suspicious: Read full artifact + check CIS conversation logs
5. If performer detected: DM student for revision (private, supportive tone)

**Rationale:** Catch performers before Week 8 showcase, preserve artifact authenticity (Guardrail #10), honor JTBD Social Job (proof must be genuine).

### Guardrails Compliance

**Guardrail #10 (Artifact Authenticity):** ✅
- Proof-of-work verification (Decision 5)
- Voice checks emphasized
- "Honest > Perfect" philosophy

**No Assessment Language:** ✅
- Verification, not grading
- Guidance, not judgment
- Growth mindset framing

---

## Story 6.5: Parent Reporting Format (Translated Outcome View)

**Status:** Design Specification
**Purpose:** Translate artifact for parent understanding
**View Type:** Summary/Report Format
**Primary Stakeholder:** Parents (outcome-focused, want proof of value)
**Emotional Need:** Validation + Proof ("Was this worth it?")

---

### Acceptance Criteria (8 Total)

**AC1: Foundation Integration**
- ✅ JTBD Social Job served - provides proof parents can understand and share
- ✅ JTBD Emotional Job translated - anxiety→confidence visible to parents
- ✅ 4 Habits Branding - all 4 habits translated to parent-language outcomes
- ✅ Decision 17 (Dual-Pillar) - Both Intelligence + Expertise demonstrated in translation

**AC2: Decision Alignment**
- ✅ Decision 13 (Artifact demonstrates thinking) - parent report shows HOW child thinks now
- ✅ Decision 17 (Dual-Pillar) - Report shows child can access expertise + think clearly

**AC3: Cross-Story Integration**
- ✅ Story 6.1 (Student Template) - translates from same artifact_progress data
- ✅ Story 5.3 (Parent Email Infrastructure) - uses SendGrid/Mailgun delivery system
- ✅ Story 6.3 (Success Metrics) - parent satisfaction survey embedded in report

**AC4: Technical Completeness**
- ✅ Parent report format specified (PDF attachment + HTML email)
- ✅ Translation guidelines defined (student voice → parent language)
- ✅ Email delivery system integrated with Story 5.3 (SendGrid, timing, consent)
- ✅ Template variable specifications added (M2 fix - automated translation)

**AC5: Stakeholder Needs Met**
- ✅ Parent emotional need: Validation ("my child grew") + Proof ("I can show this")
- ✅ Student need: Parent understanding (no jargon, accessible language)
- ✅ Trevor need: Automated delivery (90% workflow, not manual sending)

**AC6: Brand Voice Compliance**
- ✅ JTBD Altitude Level 2-3 for parents (practical, accessible, warm)
- ✅ Revolutionary Hope tone (celebration + empowerment, not pressure)
- ✅ Taglines: "Tools change. Habits transfer." parent-accessible

**AC7: Quality Framework Defined**
- ✅ Translation quality rules (student voice preserved, not replaced)
- ✅ Parent-language outcomes mapped to 4 Habits
- ✅ Dual-Pillar language integrated (child can access expertise + think clearly)

**AC8: Implementation-Ready**
- ✅ Email template ready for Story 5.3 delivery system
- ✅ PDF generation spec ready (template engine, formatting)
- ✅ Parent satisfaction survey ready (Google Forms embedded)

---

### Parent Report Design Philosophy

**Key Insight (from JTBD Social Job):**

Parents don't care about "AI literacy" or "prompt engineering." They care about:
- "Is my child more prepared for university?"
- "Did they mature?"
- "Can they think clearly now?"
- "Was this worth the time/money?"

**Translation Strategy:**

- FROM: Student's voice ("I explored, I challenged, I concluded")
- TO: Parent-language outcomes ("Your child developed critical thinking, learned to question assumptions, gained decision-making clarity")

### Parent Report Format

**Document Format:** PDF (email attachment) + optional web view

**Report Structure:**

```markdown
# K2M Cohort: Thinking Transformation Report

**Student:** [Student Name]
**Cohort:** [Dates]
**Completed:** Week 8

---

## Executive Summary: Your Child's Transformation

[Student Name] completed the K2M AI Transformation cohort with a **Thinking Artifact** - a demonstration of how they've learned to think clearly and work through complex questions using AI as a thinking partner.

**Key Outcome:** Your child has become someone who thinks WITH AI - not just copies from it.

---

## What They Worked Through

**Their Question:**
{section_1_question - translated to parent-language}

[Example: "Your child explored whether to study medicine or computer science - a complex decision with significant implications for their future."]

---

## How Their Thinking Developed

**Before K2M:** [1-2 sentences from their "before" self in Section 6]
**After K2M:** [1-2 sentences from their "after" self in Section 6]

[Example: "Before: They felt pressured to make a permanent choice and rushed to decisions. After: They learned to explore options, question assumptions, and make thoughtful next steps rather than final decisions."]

---

## The 4 Thinking Habits They Developed

⏸️ **Habit 1: Pause** - They now know what they want before asking
*Your child's example:* [specific example from Section 6]
*Parent translation:* "Before making big decisions, they pause to clarify what they actually want instead of reacting impulsively."

🎯 **Habit 2: Context** - They explain their situation first
*Your child's example:* [specific example from Section 6]
*Parent translation:* "They've learned that AI responds better when they explain their full circumstances, not just ask vague questions."

🔄 **Habit 3: Iterate** - They change one thing at a time
*Your child's example:* [specific example from Section 6]
*Parent translation:* "Instead of trying to fix everything at once, they experiment and learn from each change systematically."

🧠 **Habit 4: Think First** - They use AI before decisions
*Your child's example:* [specific example from Section 6]
*Parent translation:* "They now think through problems WITH AI before making important decisions, rather than deciding alone and then asking for validation."

---

## How They'll Use These Going Forward

**University:**
"[Specific commitment from Section 6 - Habit 1/2 applications]"

**Career/Life:**
"[Specific commitment from Section 6 - Habit 3/4 applications]"

---

## Complete Thinking Artifact

*Below is your child's complete artifact in their own words. This shows their authentic thinking journey.*

[Full artifact sections 1-6, student's original voice preserved]

---

## What This Means for Their Future

**University Readiness:**
Your child has developed structured thinking skills that universities value - the ability to analyze questions from multiple angles, challenge assumptions, and reach thoughtful conclusions.

**Career Preparation:**
Employers don't want "prompt engineers" - they want thinkers. Your child has learned to use AI as a thinking partner, not a crutch.

**Life Skill:**
These 4 thinking habits transfer beyond AI. They're now better equipped to make decisions, solve problems, and think clearly in any situation.

---

**Tools change. These habits follow them forever.**

**Completed:** [Date]
**4 Habits Graduation Card:** Attached ✅

_K2M EdTech Program - www.k2m-edtech.program_
```

### Translation Guidelines

**Student Voice → Parent Language:**

| Student Says | Parent Report Says |
|--------------|-------------------|
| "I used /frame to clarify my question" | "They learned to pause and clarify what they're really asking before seeking answers" |
| "I explored 3 angles with /diverge" | "They systematically explored multiple options instead of rushing to the first solution" |
| "I challenged my assumptions with /challenge" | "They learned to question their own beliefs and test their assumptions before committing" |
| "I synthesized my insights with /synthesize" | "They can now bring together complex information and reach thoughtful conclusions" |

**Technical → Accessible:**

| Technical Term | Parent Translation |
|----------------|-------------------|
| "CIS agents" | "structured thinking tools" |
| "Artifact creation flow" | "step-by-step reflection process" |
| "Identity transformation" | "developed mature thinking skills" |
| "Zone 3→4" | (omit - internal framework) |

### H7 + H10 Fix - Parent Email Delivery System (Story 5.3 Integration)

**Complete Technical Specification:**

**Infrastructure (from Story 5.3 lines 95-145):**
- **Service:** SendGrid (recommended) OR Mailgun OR AWS SES
- **API Key:** Stored in environment variable `SENDGRID_API_KEY`
- **Sender:** "Trevor <trevor@k2m-edtech.com>" (verified sender)
- **Reply-to:** trevor@k2m-edtech.com

**Delivery Timing:**
- **When:** Friday Week 8, after student completes artifact
- **Trigger:** Automatic if parent email exists + consent given (from Story 5.3 parent_engagement table)
- **Batch Send:** All Week 8 parent reports sent Friday 9:00 AM (batched for efficiency)

**Privacy Handling (Critical):**
- **If student chose "Public" artifact:** Report sent with full artifact attached
- **If student chose "Anonymous" artifact:** Report sent with "Your child submitted an anonymous artifact" note
- **If student chose "Private to Trevor":** Report still sent BUT asks student first: "Share artifact with parents? [Yes/No]"
- **If parent opted out (Story 5.3):** NO EMAIL SENT (respects parent unsubscribe preference)

**Error Handling (from Story 5.3 lines 524-541):**
- **Failed email:** Retry 3 times with exponential backoff (1min, 5min, 15min)
- **Bounced email:** Alert Trevor, mark `parent_email_status = 'bounced'`
- **Unsubscribe:** Process parent opt-out link immediately (Story 5.3 consent system)
- **Rate limiting:** SendGrid free tier (100 emails/day) - sufficient for 200 students

**Database Integration (Story 5.3 schema):**
```sql
-- Parent email addresses come from this table (Story 5.3)
SELECT parent_email, consent_preference
FROM parent_engagement
WHERE student_id = :student_id
AND consent_preference = 'share_weekly';  -- or 'privacy_first' (Week 8 only)
```

**Consent Verification (Story 5.3):**
- Parent email address sourced from Story 5.4 diagnostic (via Story 5.3 database)
- Email delivery uses Story 5.3 SendGrid infrastructure
- Privacy consent verified via Story 5.3 privacy controls
- If parent opted out of emails, report NOT sent (respect privacy choice)

**Cross-Reference:** See Story 5.3 lines 95-145 for complete email infrastructure specification.

### M2 Fix - Template Variable Specifications (Automated Translation)

**Problem:** Parent report uses template variables like `{section_1_question - translated to parent-language}` but doesn't specify HOW translation happens.

**Solution: Semi-Automated Translation System**

**Template Variable Types:**

**1. Direct Variables (No Translation Needed):**
```python
{student_name}           # Student's name from StudentContext
{completion_date}        # artifact_progress.completed_at
{section_1_question}     # artifact_progress.section_1_question (student's words)
```

**2. Translated Variables (Automated Level 2-3 Conversion):**

**Translation Method:** Claude API call to convert student language (Level 2-3) to parent language (Level 2-3, outcome-focused)

**Example Translation Prompt:**
```
System: You are translating a student's artifact for their parents.

Rules:
1. Keep the student's VOICE (use quotes for direct student language)
2. Convert abstract to concrete outcomes (show WHAT changed, not HOW they did it)
3. Use parent-language (no "CIS agents", "prompt engineering", technical jargon)
4. Maintain Level 2-3 altitude (practical, accessible, warm)

Input: {section_1_question}
"I need to decide between medicine and computer science but I feel stuck"

Output (parent translation):
"Your child explored a complex career decision - whether to study medicine or computer science. They felt stuck between options and wanted clarity on the right path."
```

**Template Variables Requiring Translation:**

```python
{section_1_question_parent}     # Automated: Claude API translates to parent-language
{section_2_reframed_parent}     # Automated: Translate "/frame" to "clarified what they're really asking"
{section_3_explored_parent}     # Automated: Translate "/diverge" to "explored multiple angles"
{section_4_challenged_parent}   # Automated: Translate "/challenge" to "questioned their assumptions"
{section_5_concluded_parent}    # Automated: Translate "/synthesize" to "reached thoughtful conclusions"
```

**3. Extracted Variables (Manual Trevor Selection During Friday Spot-Check):**

```python
{habit_1_example}  # Manual: Trevor selects specific example from Section 6 during Friday review
{habit_2_example}  # Manual: Trevor selects specific example from Section 6
{habit_3_example}  # Manual: Trevor selects specific example from Section 6
{habit_4_example}  # Manual: Trevor selects specific example from Section 6
```

**Trevor's Friday Workflow (15-20 artifacts):**
1. Read artifact Section 6
2. Highlight 1 specific example per habit (copy-paste into template)
3. If examples insufficient: Flag student for improvement (before publishing)

**Fallback:** If Trevor doesn't select examples, automated system extracts first mention of each habit from Section 6.

**4. Conditional Variables (Privacy-Dependent):**

```python
if student.privacy_choice == "public":
    {full_artifact_attached} = True
    {artifact_display} = "Full artifact attached below"
elif student.privacy_choice == "anonymous":
    {full_artifact_attached} = False
    {artifact_display} = "Your child submitted an anonymous artifact. They're building confidence!"
elif student.privacy_choice == "private":
    {full_artifact_attached} = False
    {artifact_display} = "Your child chose to keep their artifact private. That's okay!"
```

**Implementation Spec:**
- **Translation Service:** Claude API (same system as CIS agents)
- **Caching:** Cache translations for efficiency (same question translated once)
- **Manual Override:** Trevor can edit any automated translation during Friday spot-check
- **Validation:** All translations checked by SafetyFilter (Guardrail #3: no jargon)

### Email Delivery Format

**Subject:** "[Student Name]'s Thinking Transformation - K2M Cohort Complete!"

**Email Body:**

```markdown
Dear Parent,

Congratulations! Your child, [Student Name], has completed the K2M AI Transformation cohort.

**The Big Outcome:**

They've become someone who thinks WITH AI - not just copies from it.

I've attached:
1. Their complete Thinking Artifact (shows their real thinking journey)
2. Their 4 Habits Graduation Card (proof of skills developed)

**What Changed:**

Before K2M: [Before summary from Section 6]
After K2M: [After summary from Section 6]

**The 4 Thinking Habits They Earned:**

⏸️ Pause - They know what they want before asking
🎯 Context - They explain their situation first
🔄 Iterate - They change one thing at a time
🧠 Think First - They use AI before decisions

These habits will serve them in university, their career, and life.

**Their Complete Artifact is Below** (shows their authentic voice)

[Full artifact]

**Tools change. Habits transfer.**

With gratitude,
Trevor
K2M EdTech Program
```

### Guardrails Compliance

**JTBD Altitude:** ✅
- Level 2-3 language (practical, parent-accessible)
- No technical jargon
- Outcome-focused messaging

**Brand Voice:** ✅
- Revolutionary Hope tone (celebration + empowerment)
- "Tools change. Habits transfer."
- "Copy-pasters get stuck. Thinkers thrive."

**Authentic Student Voice Preserved:** ✅
- Parent report includes full artifact in student's words
- Translation is summary, not replacement
- Parents see BOTH: translated outcomes + authentic artifact

---

## Story 6.6: 4 Habits Graduation Card (Credential View)

**Status:** Design Specification
**Purpose:** Portfolio-ready credential proving transformation
**View Type:** Professional Certificate + Digital Badge
**Primary Stakeholder:** Students (credential), Universities (verification), Parents (proof)
**Emotional Need:** Credibility + Evidence ("I have proof I can show")

---

### Acceptance Criteria (8 Total)

**AC1: Foundation Integration**
- ✅ JTBD Social Job served - provides proof for "future" (universities/employers)
- ✅ 4 Habits Branding - all 4 habits (⏸️🎯🔄🧠) prominently displayed
- ✅ Decision 17 (Dual-Pillar) - Card shows capability to access expertise + think clearly
- ✅ JTBD Altitude Level 4 - Identity-focused language ("I am someone who...")

**AC2: Decision Alignment**
- ✅ Decision 13 (Artifact proves transformation) - card awarded after artifact completion
- ✅ Decision 14 (Week 8 graduation) - card delivered during Week 8 showcase
- ✅ Decision 17 (Dual-Pillar) - Tagline demonstrates both capabilities

**AC3: Cross-Story Integration**
- ✅ Story 6.1 (Template) - card awarded after all 6 sections complete
- ✅ Story 2.5 (Week 8 Showcase) - card design aligns with graduation ceremony
- ✅ Story 6.4 (Verification) - card only awarded after verification passes

**AC4: Technical Completeness**
- ✅ Digital image format specified (PNG, 1080x1080px, shareable)
- ✅ Printable PDF format specified (certificate paper, portfolio-ready)
- ✅ Verification system specified (H8 fix - lightweight Google Sheet + QR + static page)
- ✅ Delivery mechanism specified (DM after artifact published)

**AC5: Stakeholder Needs Met**
- ✅ Student need: Shareable credential (LinkedIn, resume, university applications)
- ✅ University need: Evidence of structured thinking capability
- ✅ Parent need: Tangible proof of program value
- ✅ Employer need: Verification system ensures authenticity

**AC6: Brand Voice Compliance**
- ✅ JTBD Altitude Level 4 throughout ("I am someone who thinks WITH AI")
- ✅ Revolutionary Hope tone (empowerment, not hype)
- ✅ Transferability messaging added (M6 fix - "habits follow you beyond AI")

**AC7: Quality Framework Defined**
- ✅ Binary completion (all 4 habits earned OR not - no partial cards)
- ✅ No zone labeling (prevents hierarchy/comparison)
- ✅ Inclusive language ("I am someone who..." not "I mastered AI")

**AC8: Implementation-Ready**
- ✅ Card design ready for graphic creation
- ✅ Verification page ready for static HTML deployment
- ✅ QR code generation spec ready for implementation
- ✅ Google Sheet schema ready for credential tracking

---

### Graduation Card Design

**From Story 2.5 lines 823-876 (4 Habits Graduation Card: Full Specifications):**

**Visual Layout:**

```
┌─────────────────────────────────────────────────────────┐
│          🎓 K2M AI TRANSFORMATION GRADUATE 🎓            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Student Name]                                         │
│                                                          │
│  ⏸️  PAUSE BADGE           - Earned                   │
│     "I know what I want before asking"                  │
│                                                          │
│  🎯  CONTEXT BADGE         - Earned                   │
│     "I explain my situation first"                      │
│                                                          │
│  🔄  ITERATE BADGE         - Earned                   │
│     "I change one thing at a time"                      │
│                                                          │
│  🧠  THINKING BADGE        - Earned                   │
│     "I use AI to think before decisions"                │
│                                                          │
│  ═════════════════════════════════════════════════════  │
│                                                          │
│  "I am someone who thinks WITH AI"                      │
│                                                          │
│  ═════════════════════════════════════════════════════  │
│                                                          │
│  Journey: COMPLETE ✅                                    │
│  Graduated: [Date]                                       │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│     Tools change. Habits transfer.                      │
│     Copy-pasters get stuck. Thinkers thrive.            │
│                                                          │
│     M6 FIX - TRANSFERABILITY LANGUAGE ADDED:            │
│     These habits follow you beyond AI—                  │
│     through university, careers, and life.              │
│                                                          │
│     k2m-edtech.program                                   │
│     Verify: [QR Code] → k2m.verify/[ID]                 │
└─────────────────────────────────────────────────────────┘
```

**Personalization Elements:**
- Student name (or "Anonymous Graduate" if privacy chosen)
- Graduation date
- Unique graduation ID (for verification - see H8 Fix below)

### M6 Fix - Transferability Language (Graduation Card Enhancement)

**Problem:** Current taglines focus on AI context, but miss explicit transferability message.

**Why Transferability Matters (from Epic 1.4 - 4 Habits Branding):**
- Habit 1 (Pause): Applies to all decisions, not just AI
- Habit 2 (Context): Applies to all communication, not just prompts
- Habit 3 (Iterate): Applies to all problem-solving, not just AI
- Habit 4 (Think First): Applies to all choices, not just AI usage

**Solution: Add Transferability Tagline**

**New Card Footer (replaces existing taglines):**
```
Tools change. Habits transfer.
Copy-pasters get stuck. Thinkers thrive.

These habits follow you beyond AI—through university, careers, and life.
```

**Alternative Shorter Version:**
```
AI skills expire. Thinking habits last forever.
```

**Rationale:** Makes explicit that 4 Habits aren't "AI skills" but transferable thinking capabilities.

### H8 Fix - Credential Verification System (Lightweight Implementation)

**Problem:** Verification system mentioned but under-specified. Need complete implementation spec.

**Solution: Lightweight Verification System (Google Sheet + QR Code + Static Page)**

**Why Lightweight:**
- Cohort 1 = 200 students max → Simple verification sufficient
- No blockchain/complex database needed (overkill for MVP)
- Trevor can manually update Google Sheet (90/10 workflow)
- Static HTML page = no hosting costs, infinite scalability

**Complete Implementation Specification:**

**1. Google Sheet Schema (Credential Database):**

```
Sheet Name: "K2M_Graduates_Cohort_1"

Columns:
A: Credential_ID (format: K2M-C1-001, K2M-C1-002, ...)
B: Student_Name (or "Anonymous Graduate")
C: Graduation_Date (YYYY-MM-DD)
D: Habits_Earned (always "⏸️🎯🔄🧠" for graduates)
E: Artifact_Submitted (Yes/No)
F: Week_8_Complete (Yes/No)
G: Verification_Status (Active/Revoked)
H: QR_Code_URL (k2m.verify/{Credential_ID})
I: Notes (Trevor's internal notes - not public)

Example Row:
K2M-C1-001 | John Smith | 2026-02-15 | ⏸️🎯🔄🧠 | Yes | Yes | Active | k2m.verify/K2M-C1-001 | Graduated with distinction
```

**Sheet Access:**
- Trevor: Full edit access (manual updates after Friday spot-checks)
- Public: Read-only access via static page API (see below)

**2. QR Code Generation:**

**Method:** Use free QR code library (e.g., `qrcode` Python library)

```python
import qrcode

credential_id = "K2M-C1-001"
verification_url = f"https://k2m-edtech.program/verify/{credential_id}"

qr = qrcode.make(verification_url)
qr.save(f"graduation_cards/{credential_id}_qr.png")
```

**Placement:** Bottom-right corner of graduation card image (embedded in PNG/PDF)

**3. Static Verification Page (HTML):**

**URL Pattern:** `k2m-edtech.program/verify/{Credential_ID}`

**Page Content:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>K2M Graduation Verification</title>
    <style>
        /* Simple, clean CSS - certificate-style formatting */
    </style>
</head>
<body>
    <div class="verification-container">
        <h1>K2M GRADUATION VERIFICATION</h1>

        <div class="status-badge">✅ VERIFIED</div>

        <div class="credential-details">
            <p><strong>Student:</strong> [Name from Google Sheet]</p>
            <p><strong>Graduation Date:</strong> [Date from Google Sheet]</p>
            <p><strong>Credential ID:</strong> [Credential_ID]</p>
        </div>

        <div class="habits-earned">
            <h2>Habits Earned:</h2>
            <ul>
                <li>⏸️ Pause ✅</li>
                <li>🎯 Context ✅</li>
                <li>🔄 Iterate ✅</li>
                <li>🧠 Think First ✅</li>
            </ul>
        </div>

        <div class="completion-status">
            <p><strong>Artifact Submitted:</strong> Yes</p>
            <p><strong>Week 8 Complete:</strong> Yes</p>
        </div>

        <div class="verification-footer">
            <p>This credential was issued by K2M EdTech Program.</p>
            <p>For questions, contact: trevor@k2m-edtech.com</p>
        </div>
    </div>
</body>
</html>
```

**Data Source:** JavaScript fetch from Google Sheets API (public read-only)

```javascript
// Fetch credential data from Google Sheets API
const SHEET_ID = "1234567890abcdef";  // Google Sheet ID
const API_KEY = "AIza...";  // Google Sheets API key (public read-only)

async function verifyCredential(credentialId) {
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/Sheet1?key=${API_KEY}`;
    const response = await fetch(url);
    const data = await response.json();

    // Find row matching credentialId
    const row = data.values.find(r => r[0] === credentialId);

    if (row && row[6] === "Active") {  // Verification_Status column
        displayVerified(row);
    } else {
        displayInvalid();
    }
}
```

**4. Security & Fraud Prevention:**

**Credential ID Format:**
- `K2M-C{cohort_number}-{student_number}`
- Example: `K2M-C1-042` = Cohort 1, Student #42
- Sequential numbering prevents ID guessing

**Revocation System:**
- If credential needs revocation (fraud detected): Trevor changes `Verification_Status` to "Revoked"
- Static page shows "❌ REVOKED" status
- Reason displayed: "This credential was revoked. Contact trevor@k2m-edtech.com"

**Data Retention:**
- Keep all graduation data for 5 years (university verification needs)
- Backup Google Sheet weekly to Trevor's local storage

**5. Alternative: If Google Sheets Insufficient (Future Enhancement)**

If Cohort 2+ scales beyond 200 students:
- **Option A:** Migrate to Airtable (more robust, same simplicity)
- **Option B:** Build simple database (SQLite or Firebase)
- **Option C:** Use blockchain (overkill but future-proof)

**Rationale for Lightweight Approach:**
- MVP-appropriate: 200 students = simple verification sufficient
- Zero hosting costs: Static HTML + Google Sheets = free
- Trevor-manageable: Manual updates during Friday spot-checks
- Instantly verifiable: QR code → static page (no delays)

**Badge Details:**
- Each badge icon is color-coded:
  - Pause: Blue (#2196F3)
  - Context: Green (#4CAF50)
  - Iterate: Orange (#FF9800)
  - Thinking: Purple (#9C27B0)
- Each badge shows the habit tagline
- "Earned" status for all 4 (binary: all complete or not)

### Formats

**1. Digital Image (PNG)**
- For sharing on social media, WhatsApp with parents
- High-resolution, shareable
- Includes K2M branding + verification URL

**2. Printable PDF**
- For including in university applications
- Portfolio-ready
- Certificate paper formatting

**3. LinkedIn Badge (Optional)**
- Verified credential for professional profiles
- Scannable QR code linking to verification page
- Blockchain verification (optional, future enhancement)

**4. Verification System (Optional)**

*From Story 2.5 lines 880-884:*

> "Unique QR code on card linking to verification page
> Verification page shows: Student name, graduation date, habits earned
> Allows employers/universities to verify credential authenticity"

**Verification Page:**
```
┌─────────────────────────────────────┐
│  K2M GRADUATION VERIFICATION        │
├─────────────────────────────────────┤
│                                     │
│  Student: [Name]                    │
│  Graduation Date: [Date]            │
│  Credential ID: [Unique ID]         │
│                                     │
│  Status: ✅ VERIFIED                │
│                                     │
│  Habits Earned:                     │
│  ⏸️ Pause ✅                        │
│  🎯 Context ✅                      │
│  🔄 Iterate ✅                      │
│  🧠 Think First ✅                  │
│                                     │
│  Artifact Submitted: Yes            │
│  Week 8 Complete: Yes               │
│                                     │
└─────────────────────────────────────┘
```

### Award Ceremony (From Story 2.5)

**When Student Completes Final Reflection (Friday Week 8):**

Agent sends personalized graduation card via DM:

```markdown
🎓 CONGRATULATIONS - YOU'VE EARNED YOUR 4 HABITS CARD

[Image of personalized 4 Habits graduation card]

Dear [Student Name],

After 8 weeks of practice, reflection, and growth, you've earned:

⏸️ PAUSE BADGE: You know what you want before asking
🎯 CONTEXT BADGE: You explain your situation first
🔄 ITERATE BADGE: You change one thing at a time
🧠 THINKING PARTNER BADGE: You use AI to think before decisions

You are now someone who thinks WITH AI.

Tools change. These habits follow you forever.
Through university, internships, jobs, and life.

Graduated: [Date]
Journey: COMPLETE ✅

Share this card with pride. You earned it. 🎓

With gratitude,
Trevor + the K2M team
```

### Credential Value Proposition

**For Students:**
- Proof of transformation ("I'm someone who thinks WITH AI")
- Portfolio piece for university applications
- Shareable achievement with parents/peers
- Confidence in their new identity

**For Parents:**
- Tangible outcome (not abstract "they learned AI")
- Evidence of maturity and critical thinking
- Proof of investment value
- Credential they can share with family

**For Universities/Employers:**
- Evidence of structured thinking (hot skill!)
- Not just "AI literacy" but "thinking WITH AI"
- Verification system ensures authenticity
- Real demonstration of capability

### Guardrails Compliance

**No Zone Labeling:** ✅
- Binary complete/not complete (no "reached Zone 4" labeling)
- Prevents comparison/hierarchy
- All graduates equal

**Inclusive Language:** ✅
- "I am someone who thinks WITH AI" (identity statement)
- Not "I mastered AI" (unrealistic)
- Not "I'm an AI expert" (exclusionary)

**Brand Voice:** ✅
- Revolutionary Hope tone
- "Tools change. Habits transfer."
- "Copy-pasters get stuck. Thinkers thrive."

---

## Implementation Roadmap

### Recommended Execution Order

**Phase 1: Core Template (Week 1)**
- **Story 6.1:** Student Creation Template
- Deliverable: Editable markdown template with prompts, examples, CIS integration
- Dependencies: Story 4.6 (complete - provides data model and workflow)

**Phase 2: Public Formats (Week 2)**
- **Story 6.2:** Artifact Showcase Format
- Deliverable: Read-only showcase format for #thinking-showcase
- Dependencies: Story 6.1 (uses same artifact data)

**Phase 3: Supporting Systems (Week 3)**
- **Story 6.3:** Success Metrics
- **Story 6.4:** Shift Verification Questions
- Deliverable: Quality framework and validation system
- Dependencies: Stories 6.1, 6.2 (metrics apply to both)

**Phase 4: Stakeholder Views (Week 4)**
- **Story 6.5:** Parent Reporting Format
- **Story 6.6:** 4 Habits Graduation Card
- Deliverable: Translated parent report + credential design
- Dependencies: Story 6.1 (uses same artifact data)

### Cross-Story Dependencies

```
Story 4.6 (COMPLETE)
    ↓
    ├─→ Provides: Artifact data schema, workflow engine
    ↓
Story 6.1 (Student Template)
    ↓
    ├─→ Provides: Creation interface, section structure
    ↓
Story 6.2 (Showcase Format)
    ├─→ Uses: Same artifact data from 6.1
    ↓
Story 6.3 (Metrics) + Story 6.4 (Verification)
    ├─→ Apply to: Both 6.1 and 6.2
    ↓
Story 6.5 (Parent Report) + Story 6.6 (Credential)
    ├─→ Use: Same artifact data from 6.1
    └─→ Translate: For different stakeholders
```

### Implementation Handoff

**For Each Story:**

1. **Design Document** (this Epic 6 document)
   - Complete specifications
   - Examples and templates
   - Guardrails compliance verified

2. **Story File** (BMAD workflow)
   - User story with acceptance criteria
   - Tasks/subtasks
   - Dev execution ready

3. **Integration Points**
   - References to Story 4.6 data model
   - References to Epic 1 foundations
   - References to Story 2.5 Week 8 design

---

## Success Criteria

**Epic 6 Complete When:**

1. [ ] All 6 stories have complete design specifications
2. [ ] All 4 stakeholder views designed (Student, Showcase, Parent, Credential)
3. [ ] Cross-story consistency verified (shared design system, brand voice, 4 Habits branding)
4. [ ] All stories reference Story 4.6 data model correctly
5. [ ] All stories honor Epic 1 foundations (Guardrails, JTBD, Node Architecture, 4 Habits)
6. [ ] Integration with Story 2.5 Week 8 design confirmed
7. [ ] Implementation roadmap documented
8. [ ] Ready for dev execution (story files can be created)

---

## Appendix: Example Artifact (Complete)

**From Story 4.6 lines 286-338 (Example: Complete Thinking Artifact):**

```markdown
**Example: Complete Thinking Artifact**

*This is just an example format. Your artifact will be about YOUR question and YOUR thinking.*

---

**THE QUESTION I WRESTLED WITH:**

"I need to decide what to study at university, but I feel stuck between my parents' expectations (medicine) and what I'm actually interested in (computer science)."

---

**HOW I REFRAMED IT:**

Using /frame, I realized my question wasn't "What should I study?" but "What do I value?" I discovered I care about: solving real problems, creative work, and having options - not just "helping people" (medicine) or "being good at tech" (CS).

---

**WHAT I EXPLORED:**

Using /diverge, I explored 3 angles:
1. **What if I combined them?** (Medical technology, health tech startups)
2. **What if I questioned the binary?** (Maybe neither medicine nor CS - what about data science for public health?)
3. **What if I tried before committing?** (Volunteer at hospital, build a health app, see what I actually enjoy)

---

**WHAT I CHALLENGED:**

Using /challenge, I tested my assumptions:
- "My parents will be disappointed if I don't do medicine" → *Challenge:* What if they want me to be happy, not just be a doctor?
- "I need to decide now" → *Challenge:* What if the first year is FOR exploration? I don't have to commit forever.
- "Computer science isn't helping people" → *Challenge:* What if health tech helps more people than one doctor ever could?

---

**WHAT I CONCLUDED:**

Using /synthesize, I crystalized my insight: The real question isn't medicine vs CS - it's "How do I want to help people?" I'm going to:
1. **Try both:** Volunteer at a hospital AND build a small health project this year
2. **Keep options open:** Apply to both, but look for programs that combine tech + health
3. **Decide later:** I don't need to know now. The first year is for exploration.

---

**WHAT THIS TAUGHT ME:**

**M1 FIX - Enhanced with Emotional Job Demonstration (Anxiety → Confidence + Belonging):**

**Before K2M, I felt...**
I felt anxious about university and my future. Everyone else seemed to know things I didn't—about courses, careers, how to make smart decisions. I felt behind, like I was faking it. I thought I had to choose between making my parents happy and being happy myself.

**The shift happened when I realized...**
I could access expert knowledge I didn't have. I didn't need to know everything about medicine AND computer science—I could tap into that expertise through AI and use it to think clearly. That unlocked everything for me.

**Now I can:**
- **Access expertise I don't have** (Medical knowledge, CS concepts, career guidance—I'm not limited by what I know today)
- **Think clearly with that expertise** (I don't just copy answers—I use knowledge to make my own decisions)

Now I realize:
- **Habit 1 ⏸️ Pause:** I stopped rushing to decide and really thought about what I value. When I'm confused in university lectures, I'll pause before asking—what do I actually want to understand?
- **Habit 2 🎯 Context:** I explained my full situation instead of just "medicine vs CS." I'll explain my full situation to AI, not just "help me with this assignment."
- **Habit 3 🔄 Iterate:** I explored multiple angles instead of picking the first "good enough" answer. I'll explore multiple approaches to problems instead of accepting the first solution.
- **Habit 4 🧠 Think First:** I questioned my assumptions instead of accepting them as true. Before choosing courses or career paths, I'll use AI to access expert perspectives I don't have.

**What changed for me:**
Week 1: I felt like an outsider in AI conversations, anxious I'd be left behind.
Week 8: I feel like I belong. I'm not someone who "mastered AI"—I'm someone who learned how to access knowledge and think with it clearly.

I can access expert knowledge I don't have—and think clearly with it.

---

*Notice how this artifact shows thinking growth, not just "I used AI tools." The focus is on "I became someone who thinks clearly" not "I learned to use ChatGPT."*
```

---

## H9 Fix - Brand Voice Altitude Audit & Consistency Enforcement

**Problem:** Inconsistent brand voice altitude across Stories 6.1-6.6 can confuse students and dilute messaging.

**Solution: Complete Altitude Consistency Framework**

### Altitude Standards by Story

**Story 6.1 (Student Template):**
- **Target Altitude:** Level 2-3 (Pattern + Action)
- **Why:** Students need accessible, practical guidance during creation
- **Examples:**
  - ✅ Level 2-3: "What were you confused about? Be specific."
  - ❌ Level 0-1: "Enter your question here" (too ground-level)
  - ❌ Level 4-5: "Identify the epistemic tension underlying your inquiry" (too abstract)

**Story 6.2 (Showcase Format):**
- **Target Altitude:** Level 3-4 (Action + Identity)
- **Why:** Celebration needs to honor identity transformation
- **Examples:**
  - ✅ Level 3-4: "That's someone who thinks WITH AI!"
  - ✅ Level 4: "They're becoming someone who directs AI intentionally"
  - ❌ Level 1-2: "They completed their artifact" (too mechanical)

**Story 6.3 (Success Metrics):**
- **Target Altitude:** Level 2-3 (Pattern + Action)
- **Why:** Metrics need to be concrete and measurable
- **Examples:**
  - ✅ Level 2-3: "Strong: Before/After contrast is specific and honest"
  - ❌ Level 4-5: "Demonstrates epistemic growth" (too abstract)

**Story 6.4 (Verification):**
- **Target Altitude:** Level 2-3 (Pattern + Action)
- **Why:** Verification must be mechanically clear
- **Examples:**
  - ✅ Level 2-3: "Does this sound like YOU?"
  - ❌ Level 0-1: "Is this your artifact?" (too ground-level)

**Story 6.5 (Parent Report):**
- **Target Altitude:** Level 2-3 (Pattern + Action) with Level 4 identity moments
- **Why:** Parents need concrete outcomes with identity transformation visible
- **Examples:**
  - ✅ Level 2-3: "Your child can now access knowledge they don't have and think clearly with it"
  - ✅ Level 4 (moments): "They're becoming someone who thinks WITH AI"
  - ❌ Level 5: "Metacognitive capability development" (too academic for parents)

**Story 6.6 (Graduation Card):**
- **Target Altitude:** Level 4-5 (Identity + Purpose)
- **Why:** Credential needs to assert identity shift
- **Examples:**
  - ✅ Level 4: "I am someone who thinks WITH AI"
  - ✅ Level 5: "Tools change. Habits transfer." (universal truth)
  - ❌ Level 2-3: "I completed 8 weeks of AI training" (too ground-level for credential)

### M7 Fix - Voice Check Prompts Throughout Student Template

**Add voice check prompts after EVERY section (not just Section 6):**

**After Section 1 (Question):**
```markdown
🎯 Voice Check: Is this YOUR question or a generic version?
- ✅ "I'm confused about medicine vs CS because my parents want one but I like the other"
- ❌ "I need to choose a university major"
```

**After Section 2 (Reframed):**
```markdown
🎯 Voice Check: Did you actually use /frame or just claim you did?
- Check your conversation history - is there a /frame conversation?
- If not, try /frame now or be honest about what you actually did
```

**After Section 3 (Explored):**
```markdown
🎯 Voice Check: Is this specific exploration or vague claims?
- ✅ "I asked AI about 5 different career paths and compared salary vs fulfillment"
- ❌ "I explored different options"
```

**After Section 4 (Challenged):**
```markdown
🎯 Voice Check: Did challenging feel real or forced?
- ✅ "I realized I assumed medicine = helping people, but CS can help too"
- ❌ "I challenged my assumptions about my question"
```

**After Section 5 (Concluded):**
```markdown
🎯 Voice Check: Is this conclusion honest or what you think we want to hear?
- ✅ "I still don't know, but now I have better questions"
- ❌ "I learned that AI is helpful for decision-making"
```

**After Section 6 (Reflection):**
```markdown
🎯 Voice Check: Would your friend recognize this as YOUR voice?
- Read it out loud. Does it sound like you explaining to a friend?
- If not, start with ONE honest sentence about what changed for you
```

**Rationale:** Catching voice drift EARLY (not just at the end) prevents students from writing entire sections in generic/AI-generated voice.

### Brand Voice Guidelines Reference

**From Epic 1 - JTBD Altitude Framework:**

| Level | Description | When to Use | Example |
|-------|-------------|-------------|---------|
| 0 | Ground | Never (too mechanical) | "Complete the template" |
| 1 | Individual Action | Rarely (instructions only) | "Write your question here" |
| 2 | Pattern | Primary (guidance) | "What were you confused about?" |
| 3 | Action | Primary (reflection) | "Pause before asking AI" |
| 4 | Identity | Celebration moments | "You're someone who thinks WITH AI" |
| 5 | Purpose/Universal | Taglines only | "Tools change. Habits transfer." |

**Epic 6 Default Altitude: Level 2-3** (Pattern + Action)
**Elevation Points:** Story 6.2 (celebration), Story 6.6 (credential)

### Audit Checklist (Applied to ALL Stories)

**Pre-Publishing Audit:**

```markdown
For EACH story (6.1-6.6), check:

1. ✅ Is target altitude appropriate for stakeholder?
   - Students (creation) → Level 2-3
   - Students (celebration) → Level 3-4
   - Parents (outcomes) → Level 2-3
   - Credentials (identity) → Level 4-5

2. ✅ Is language consistent within story?
   - No altitude jumps within same section
   - Gradual elevation if needed (Level 2→3→4, not 2→5)

3. ✅ Are taglines consistent across stories?
   - "Tools change. Habits transfer." (Level 5 - universal)
   - "That's someone who thinks WITH AI!" (Level 4 - identity)
   - Used appropriately for context

4. ✅ Is Decision 17 (Dual-Pillar) integrated?
   - Both "access expertise" + "think clearly" visible
   - Not just "AI skills" but thinking capabilities
```

### Consistency Enforcement Workflow

**Trevor's Role (10% Workflow):**
- Friday spot-checks: Read 15-20 artifacts Section 6
- Flag altitude inconsistencies (too formal = Level 5, too vague = Level 0-1)
- DM students for voice revision if needed

**Agent's Role (90% Workflow):**
- Voice check prompts after EVERY section (M7 fix applied)
- SafetyFilter checks for formal/generic language patterns
- Automatic flagging: "This sounds too formal. Can you rewrite in your own words?"

**Result:** Consistent Level 2-3 altitude throughout artifacts, with intentional Level 4 elevation for celebration/credentials.

---

**Epic 6 Design Document: COMPLETE ✅ (ALL ADVERSARIAL REVIEW FIXES APPLIED)**

**Next Step:** Execute stories sequentially using BMAD dev-story workflow, or implement all together as unified module.

**Dependencies Met:**
- ✅ Story 4.6 (data model, workflow engine)
- ✅ Story 2.5 (Week 8 showcase design)
- ✅ Epic 1 (Guardrails, JTBD, Node Architecture, 4 Habits)
- ✅ Decisions 11-14 (CIS agents, Discord model, artifact structure, timeline)

**Ready for:** Dev execution, story file creation, sprint planning integration.

---

## ADVERSARIAL REVIEW FIXES APPLIED - COMPLETE SUMMARY

### HIGH Priority Fixes (ALL 12 Applied)

**✅ H1:** All 11 Guardrails compliance checklist added to Story 6.1 AC1
**✅ H2:** Decision 17 (Dual-Pillar) integration - Section 6 template updated (ALREADY APPLIED)
**✅ H3:** JTBD Emotional Job integration - Section 6 template updated (ALREADY APPLIED)
**✅ H4:** Node Architecture references added to Section 6 guidance (ALREADY APPLIED)
**✅ H5:** 8 Acceptance Criteria added to ALL stories (6.1-6.6)
**✅ H6:** Technical Implementation Specs added to ALL stories (verification system, delivery system, translation system)
**✅ H7:** Parent email delivery system specified (Story 5.3 integration, SendGrid infrastructure)
**✅ H8:** Credential verification system specified (Google Sheet + QR code + static page)
**✅ H9:** Brand voice altitude audit + consistency enforcement framework added
**✅ H10:** Story 5.3 cross-references added to Story 6.5 (parent email infrastructure)
**✅ H11:** 5th Quality Dimension (Zone Shift Evidence) added (ALREADY APPLIED)
**✅ H12:** Stuck pattern interventions from Story 4.6 lines 673-698 integrated into Story 6.1

### MEDIUM Priority Fixes (ALL 8 Applied)

**✅ M1:** Enhanced example artifact with Emotional Job demonstration (anxiety→confidence + belonging)
**✅ M2:** Parent report template variable specifications added (automated translation system)
**✅ M3:** Showcase diversity highlight selection criteria added (Story 6.2 - celebrate diverse thinking)
**✅ M4:** False positive detection added to verification (Story 6.4 - catch performers vs genuine shifters)
**✅ M5:** Parent satisfaction metrics added (Story 6.3 - JTBD Social Job validation)
**✅ M6:** Transferability language added to graduation card (Story 6.6 - habits follow beyond AI)
**✅ M7:** Voice check prompts added throughout student template (after EVERY section, not just Section 6)
**✅ M8:** Anonymous display format specifications added (Story 6.2 - batch posting, timing protection)

### Integration Completeness

**Epic 1 Foundations:**
- ✅ All 11 Guardrails enforced across all stories
- ✅ JTBD Integration (Functional, Emotional, Social jobs served)
- ✅ Node Architecture (Zone 3→4 progression, all 16 nodes referenced)
- ✅ 4 Habits Branding (all 4 habits visible, graduation card awarded)
- ✅ Decision 17 (Dual-Pillar) - Both Intelligence + Expertise demonstrated

**Cross-Story Dependencies:**
- ✅ Story 4.6 (Artifact creation flow, CIS scaffolding, stuck patterns)
- ✅ Story 2.5 (Week 8 showcase, privacy controls, graduation ceremony)
- ✅ Story 5.3 (Parent email infrastructure, SendGrid delivery, consent system)
- ✅ Story 6.3 (5 Quality Dimensions including Zone Shift Evidence)

**Technical Specifications:**
- ✅ Complete database schema (artifact_progress, parent_engagement, verification)
- ✅ Complete email delivery system (SendGrid, templates, error handling)
- ✅ Complete verification system (Google Sheet, QR codes, static HTML page)
- ✅ Complete translation system (Claude API, caching, SafetyFilter validation)
- ✅ Complete automation specs (agent workflows, Trevor 10% spot-checks)

### Implementation Readiness

**All Stories Now Have:**
1. ✅ 8 Acceptance Criteria each (Foundation, Decision Alignment, Cross-Story Integration, Technical Completeness, Stakeholder Needs, Brand Voice, Quality Framework, Implementation-Ready)
2. ✅ Complete technical specifications (database, API, infrastructure)
3. ✅ Clear cross-references to dependencies (Story 4.6, 5.3, 2.5, etc.)
4. ✅ Brand voice altitude consistency enforced (Level 2-3 default, Level 4 for celebration/credentials)
5. ✅ All Decision 17 (Dual-Pillar) language integrated throughout

**Developer Handoff Ready:**
- Story 6.1: Student template ready for Discord bot integration
- Story 6.2: Showcase format ready for #thinking-showcase channel
- Story 6.3: Success metrics ready for cohort dashboard
- Story 6.4: Verification system ready for implementation (lightweight approach)
- Story 6.5: Parent report ready for Week 8 email automation
- Story 6.6: Graduation card ready for graphic design + QR code generation

**No Outstanding Issues:**
- ✅ All HIGH priority fixes applied (12/12)
- ✅ All MEDIUM priority fixes applied (8/8)
- ✅ All acceptance criteria defined (8 per story × 6 stories = 48 total)
- ✅ All technical specs complete (database, email, verification, translation)
- ✅ All cross-story integrations documented
- ✅ All brand voice consistency enforced

**Epic 6 Status:** READY FOR IMPLEMENTATION ✅

---

_Document Created: 2026-01-25_
_Design Approach: Holistic System Design (all 6 stories unified)_
_Architectural Pattern: Model-View-Controller_
_Primary Designer: Winston (Architect) + Maya (Design Thinking Coach) + John (PM) via Party Mode_
