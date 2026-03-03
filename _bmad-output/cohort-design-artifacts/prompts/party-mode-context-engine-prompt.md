# Party Mode Session: Context Engine Experience Design
**Prompt for:** `/bmad:core:workflows:party-mode`
**Output file:** `_bmad-output/cohort-design-artifacts/design-and-architecture/context-engine-experience-design.md`
**Date created:** 2026-02-20
**Decision basis:** Decision 7 revised — build context engine for Cohort 1, not deferred to Cohort 2

---

## HOW TO RUN THIS SESSION

1. Open Claude Code
2. Type `/bmad:core:workflows:party-mode`
3. When prompted for a topic, paste the FULL PROMPT below (everything after the divider)
4. The agents will debate and design together
5. At the end, ask them to produce `context-engine-experience-design.md`

---

---

## THE PROMPT (paste this into party mode)

We are designing the **personalized student experience** for the K2M Cohort 1 Discord learning program. A critical architectural decision has just been revised: **the context engine will be built now, not deferred.**

**What this means:** KIRA (our Discord bot / thinking partner) will know each student's profession, their barrier to AI adoption, their situation, and their goals from the moment they fill the Google Form. Every CIS agent interaction (/frame, /diverge, /challenge, /synthesize) will use this context to personalize its response.

**Your job today:** Design the full personalized experience — every beat, every message, every system prompt shape. The developers will build exactly what you design.

---

### The Program Context (read before designing)

**What K2M is:**
- 8-week AI thinking skills program for Kenyan youth + young professionals
- Students progress through 4 zones: Zone 1 (Wonder) → Zone 2 (Trust) → Zone 3 (Converse) → Zone 4 (Direct)
- Weekly structure: daily prompts (9:15 AM EAT) + 3 live cluster sessions/week + CIS agent DMs
- Cohort size: 100-200 students
- Platform: Discord + Python bot (KIRA) + Claude API

**The 4 Habits students are building:**
1. PAUSE before using AI (notice the moment)
2. FRAME clearly (describe context before asking)
3. ITERATE deliberately (treat first response as raw material)
4. THINK FIRST (form your own view, then use AI to pressure-test)

**The 4 CIS Agents (available progressively):**
- `/frame` (Week 1+): Framing Agent — helps students articulate fuzzy questions clearly
- `/diverge` (Week 4+): Explorer Agent — breaks students out of single-perspective thinking
- `/challenge` (Week 4+): Challenger Agent — stress-tests ideas before action
- `/synthesize` (Week 6+): Synthesizer Agent — pulls thinking together into coherent insight
- `/create-artifact` (Week 6+): 6-section artifact documenting zone journey

**The diagnostic form captures (from Google Form):**
- Real name (first + last)
- Email
- Zone self-assessment (Zone 1-4 scale + scenario verification)
- Profession: teacher / entrepreneur / university student / working professional / other
- Situation: freeform — "what does your day-to-day work/study look like?"
- Goals: freeform — "what do you hope to be able to do differently after this program?"
- Emotional baseline: how does AI make you feel right now? (optional)
- Parent/guardian contact

**Known barrier types (from facilitation research):**
- **Identity barrier:** "I'm not technical / AI isn't for people like me"
- **Time barrier:** "I'm too busy / I don't have time to figure this out"
- **Relevance barrier:** "I don't see how this applies to my actual work"
- **Technical barrier:** "The tools are confusing / I don't know where to start"

---

### What We Need Designed

#### Design Task 1: The Context Schema

What student context fields does the bot actually need to store and use?
We have: `profession`, `barrier_type`, `situation`, `goals`, `zone`, `real_last_name`.

- Are these enough? What's missing?
- How should `barrier_type` be inferred from form responses? (The form doesn't explicitly ask "what is your barrier type" — it asks about feelings and goals. How do we infer?)
- Should we add any computed fields (e.g., engagement_level, zone_shift_count)?
- What does the full student context JSON look like that gets passed to CIS agents?

#### Design Task 2: The Example Library

We need 40+ rows in the Example_Library (10 per profession × 4 professions).
Design the structure and write the actual examples.

Format needed:
```
profession | example_text | week_relevant | habit_tag
teacher    | [real example of a teacher using AI in classroom context] | 1-3 | habit_1
```

For each profession (teacher, entrepreneur, university student, working professional):
- Write 10 examples across the 8 weeks
- Examples should feel real and specific (not generic "I used AI to write an email")
- Examples should map to specific habits being built that week
- They should feel like something a real Kenyan professional would do

#### Design Task 3: The Intervention Library

We need at least 8 rows (4 barrier types × 2 week ranges: early/late).
Write the actual intervention text for each.

Format needed:
```
barrier_type | week_range | intervention_text
identity     | weeks 1-4  | [full text KIRA sends as DM when student with identity barrier goes quiet]
identity     | weeks 5-8  | [different intervention as they're deeper in the program]
```

Interventions must:
- Address the SPECIFIC barrier (not generic "come back, we miss you")
- Reference the student's profession where possible (use placeholder: {profession})
- Be warm, not guilt-inducing
- Give ONE clear next action (not a list)
- Be max 4 sentences

#### Design Task 4: The 7 KIRA Juncture DM Templates

At 7 journey junctures, KIRA proactively reaches out. Design the full message for each.

**Juncture 1 — After first /frame session:**
Student just completed their very first /frame conversation with KIRA.
What does KIRA DM them within 2 minutes of the conversation ending?
Must: name what habit they just practiced, what it revealed, and one invitation for next time.

**Juncture 2 — After first showcase share:**
Student just posted their first piece of thinking publicly.
What does KIRA DM them?
Must: acknowledge the vulnerability of going public, name what was strong, and point to what's next.

**Juncture 3 — Week N unlock message (template for all weeks):**
Every Saturday, the next week unlocks.
Design a template that personalizes the unlock message based on:
- Student's current zone
- Their engagement pattern this week (active vs quiet)
- What the next week is about
What's the structure? What fields does it reference?

**Juncture 4 — Week 4 agent unlock (/diverge + /challenge):**
These two agents unlock. What does KIRA tell this specific student about:
- Why NOW (what have they demonstrated that shows they're ready)?
- When to use /diverge vs /challenge?
- A personalized first prompt to try with /diverge based on something they've been working on?

**Juncture 5 — Week 6 agent unlock (/synthesize + /create-artifact):**
The synthesis tools unlock. Artifact creation begins.
How does KIRA introduce these? What does it say about the student's journey so far?
What's the one thing they should know before starting their artifact?

**Juncture 6 — /create-artifact first use:**
Student types /create-artifact for the first time.
Before Section 1 begins, KIRA sends a framing message.
What does it say? It has access to: their zone shift, their /frame history topics, their profession.

**Juncture 7 — Graduation (/publish completes):**
Student's artifact is live.
Design the graduation DM. It has access to: their zone journey, total /frame sessions, showcase posts, profession, artifact title.
Must include their journey arc in concrete terms.

#### Design Task 5: Personalized CIS Agent System Prompt Templates

For each of the 4 CIS agents, design the system prompt that includes student context.

Current /frame system prompt (generic):
```
You are a Framing Agent. Help the student think clearly about their question.
Ask clarifying questions. Don't give answers. Surface the real question behind their question.
```

Design the PERSONALIZED version for each agent:
- What student context fields go in?
- How do examples get injected (before student speaks, or as agent responds)?
- What guardrails does the personalization need (student shouldn't feel surveilled)?
- Write the actual system prompt template with {placeholder} variables

#### Design Task 6: The Personalized Welcome DM

KIRA's first message to every student after joining Discord.
Current version is generic. Design the personalized version.

It has access to: first_name, profession, situation, cluster_id, session_schedule.
It must: feel warm and specific, give exactly ONE action, make #thinking-lab feel safe.

Write the full message template. Mark every personalized field with {curly_braces}.

#### Design Task 7: Ethical Guardrails

With this much student data, what are the boundaries?

- What data should NEVER appear in public channels (even indirectly)?
- How do we prevent KIRA from feeling creepy/surveilled vs. caring/seen?
- What's the right phrasing when KIRA references student context? ("I remember you mentioned..." vs "You told me that..." vs "Based on your profile...")?
- Should students be able to see what KIRA knows about them? How?
- What happens if a student's situation changes mid-program and the context is stale?

---

### Constraints the Design Must Respect

1. **Budget:** Claude API calls per student per day ≤ $0.10. Examples library query must be lightweight.
2. **Privacy:** Barrier type and situation are never shared publicly. Only Trevor can see them.
3. **Fallback:** If context unavailable (student not pre-loaded), every CIS agent must still work generically.
4. **Kenya context:** All examples must be grounded in Kenyan professional reality (EAT timezone, M-Pesa, Kenyan university system, Kenyan teaching context).
5. **Tone:** K2M brand voice is warm, direct, high-expectation, non-condescending. Not American corporate positivity. Not generic edtech encouragement.
6. **Guardian rules:** No private DM content ever referenced in public channels. Never compare students to each other.
7. **Agency:** Students should feel KIRA is a thinking partner, not a surveillance system. Context should enhance, not constrain.

---

### Output Required

By the end of this session, produce a document called `context-engine-experience-design.md` with:

```
1. CONTEXT SCHEMA — Full JSON structure + barrier type inference logic
2. EXAMPLE LIBRARY — All 40+ examples (ready to paste into Google Sheets)
3. INTERVENTION LIBRARY — All 8+ interventions (ready to paste into Google Sheets)
4. JUNCTURE DM TEMPLATES — All 7, with {placeholders} clearly marked
5. CIS AGENT SYSTEM PROMPTS — All 4, personalized versions
6. WELCOME DM TEMPLATE — Full message with {placeholders}
7. ETHICAL GUARDRAILS — Concrete rules for implementation
8. OPEN QUESTIONS — Anything that needs Trevor's decision before build begins
```

This document is the design bible. Developers will build from it directly.

---

*Created by Dev Agent (Amelia) — 2026-02-20*
*To be run with: `/bmad:core:workflows:party-mode`*
