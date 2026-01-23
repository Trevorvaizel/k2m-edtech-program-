# Cohort Playbook v2 - Consolidated Requirements Document

**Created:** 2026-01-22
**Status:** MASTER REQUIREMENTS - Source of Truth for Sprint Execution
**Purpose:** Captures ALL decisions, context, and requirements for Cohort Playbook v2 creation

---

## Executive Summary

This document consolidates all decisions from the Cohort Facilitation Redesign process into a single requirements document that will drive the creation of Cohort Playbook v2. It serves as the PRD-equivalent for epic/story creation using BMAD workflows.

**The Core Transformation:**
- FROM: 8 human facilitators managing 200 students
- TO: Agent-facilitated model with Trevor as 10% human layer + CIS thinking agents + node-based content

**The Product Being Built:**
A complete, shippable Cohort Playbook v2 that includes:
1. Updated philosophy and guardrails
2. New 8-week design with zone nodes (extended from 6 weeks for deeper transformation)
3. CIS agent system for Discord (introduced gradually from Week 1)
4. Thinking Artifact graduation requirement
5. All support documents, prompts, and templates

**Timeline Decision (Locked 2026-01-23):**
- Original proposal: 6 weeks (compressed transformation)
- **APPROVED:** 8 weeks (deeper transformation, aligns with node architecture)
- Rationale: JTBD emotional job ("stop feeling anxious") requires adequate dwell time for identity shifts to stabilize

---

## Source Documents

### External Source Documents (Pre-Existing)

| Document | Location | Purpose |
|----------|----------|---------|
| Decisions Document | `_bmad-output/cohort-design-artifacts/cohort-facilitation-redesign-decisions.md` | All approved decisions |
| Playbook v1 | `_bmad-output/COMPLETE-COHORT-OPERATIONAL-PLAYBOOK/` | Current system to update |
| Cartographer's Manifesto | `docs/cartographers_manifesto/` | Philosophy foundation |
| AI Territory Map | `docs/ai_proficiency_territory_map/` | Zone framework |
| Brand Conversion Framework V3 | `_bmad-output/k2m-edtech-brand-artifacts/k2m-brand-conversion-framework-v3.md` | Voice/altitude guidance for all content |

### Foundation Documents (Epic 0 & Epic 1 Outputs)

**CRITICAL:** All subsequent epics (2-7) MUST reference and build upon these foundational documents. These are not optional context—they are the load-bearing walls that define the entire v2 system.

| Epic | Story | Document | Location | Purpose |
|------|-------|----------|----------|---------|
| **Epic 0** | 0.1 | Requirements Document (this file) | `_bmad-output/cohort-design-artifacts/cohort-playbook-v2-requirements.md` | Master requirements - single source of truth |
| **Epic 0** | 0.2 | Sprint Status Tracker | `_bmad-output/cohort-design-artifacts/sprint-status.yaml` | Progress tracking across all epics |
| **Epic 1** | 1.1 | Core Guardrails - Preserved & Enhanced | `playbook-v2/01-philosophy/guardrails-preserved.md` | 10 guardrails that protect framework purity, student safety, and scalability |
| **Epic 1** | 1.2 | JTBD Identity Transformation Integration | `playbook-v2/01-philosophy/jtbd-integration.md` | Zones as identity shifts, emotional/social jobs, philosophy principles |
| **Epic 1** | 1.3 | Node-Based Learning Architecture | `playbook-v2/01-philosophy/node-architecture.md` | Mental lattice framework, 16 nodes (4 per zone), node design principles |
| **Epic 1** | 1.4 | The 4 Habits Branding | `playbook-v2/01-philosophy/four-habits-brand.md` | 4 Habits as graduation proof, icons/taglines, Dual Pillars integration |

**Foundation Summary:**

**Epic 0 (Foundation & Decision Lock)** ✅ COMPLETE:
- Created the project infrastructure and requirements tracking
- Established single source of truth (this document)
- Set up sprint-status.yaml for progress monitoring

**Epic 1 (Philosophy & Framework)** ✅ COMPLETE:
- **Guardrails (10 total):** Define what we NEVER do, what we ALWAYS do, and v2-specific rules for agent model, node quality, Discord safety, artifact authenticity, and brand voice compliance
- **JTBD Integration:** Maps zones to identity shifts (outsider→observer→experimenter→collaborator→director), connects to functional/emotional/social jobs
- **Node Architecture:** 16 nodes across 4 zone transitions (0→1, 1→2, 2→3, 3→4), each targeting one identity shift + one emotional job + one 4 Habit
- **4 Habits Branding:** Pause ⏸️, Context 🎯, Iterate 🔄, Think First 🧠 - visible, tangible graduation-proof that serves JTBD social job

**All Future Work (Epics 2-7) Must:**
1. Reference relevant guardrails from Epic 1.1
2. Honor zone-to-identity-shift mapping from Epic 1.2
3. Use node architecture from Epic 1.3 for all content design
4. Reinforce 4 Habits from Epic 1.4 across all touchpoints
5. Track progress in Epic 0's sprint-status.yaml

**These documents are NON-NEGOTIABLE foundation.** Any design decision that contradicts these foundations without explicit update to Epic 1 outputs is invalid.

---

## Core Brand Philosophy: The Dual Pillars

### Decision 17: Dual-Pillar Brand Foundation
**Status:** APPROVED
**Summary:** K2M's brand rests on two complementary concepts that together define the opportunity AI creates

**Pillar 1: Democratized Intelligence**
- AI makes powerful *thinking capabilities* available to everyone
- Previously, sophisticated reasoning required years of training or innate talent
- Now anyone can access structured thinking, analysis, synthesis
- *Student experience:* "I can think through complex problems now"

**Pillar 2: Democratized Expertise**
- AI collapses the *knowledge gap* across domains
- Previously, expertise required years of study in specific fields
- Now anyone can tap into specialized knowledge instantly
- *Student experience:* "I can access knowledge I don't have"

**The Unifying Skill: Thinking WITH AI**
- This is what K2M teaches - the capability that unlocks both pillars
- Not just using AI, but developing a *thinking partnership*
- The 4 Habits are the practical expression of this skill

**Application Across Content:**

| Content Type | How Both Pillars Apply |
|--------------|------------------------|
| Zone Nodes | Each node can emphasize intelligence (thinking) or expertise (knowledge) aspects |
| CIS Agents | Framer/Challenger = intelligence; Explorer/Synthesizer = expertise |
| Daily Prompts | Alternate between "think better" and "know more" angles |
| NotebookLM Pods | Frame each zone shift in terms of both capabilities gained |
| Artifact | Demonstrate both enhanced thinking AND accessed expertise |

**Why Both Matter:**
- Intelligence alone = powerful thinking but limited scope
- Expertise alone = broad knowledge but shallow application
- Together = students become genuinely more capable across any domain

---

## Decision Inventory (NO LOSSES)

### Decisions from Decisions Document

#### Decision 1: Adopt Agent-Facilitated Model
**Status:** APPROVED
**Summary:** Replace 8 human facilitators with agent automation
**Rationale:**
- Preserves framework purity (no advice-giving drift)
- Scales infinitely (copy-paste for future cohorts)
- Reduces Trevor's time from 14+ hours/week to ~2 hours/week
- Trade-off accepted: Lower per-cohort shift rate, but higher total impact through scale

#### Decision 2: Accept 90/10 Hybrid Model
**Status:** APPROVED
**Summary:** Agents handle 90%, Trevor handles 10%

**Agent handles (90%):**
- All mechanical tasks (prompts, tracking, nudges, reactions)
- All template interventions
- All gating/progression
- Peer visibility aggregation

**Trevor handles (10%):**
- Friday spot-check: 15-20 student reflections
- 1-hour live sessions (alternating days per cluster)
- Escalations: Agent flags students stuck 3+ days
- Culture monitoring: Are norms being followed?

#### Decision 3: Accept Shift Rate Trade-off
**Status:** ACKNOWLEDGED
**Expected outcomes:**

| Metric | With 8 Facilitators | With Agent System |
|--------|---------------------|-------------------|
| Reach Zone 4 | 40% (80 students) | 25-35% (50-70 students) |
| Reach Zone 2-3 | 30% (60 students) | 35-40% (70-80 students) |
| Drop/Perform | 30% (60 students) | 25-40% (50-80 students) |
| Your time/week | 14+ hours | 2 hours |
| Scalability | Limited | Infinite |

**Strategic rationale:** Scale wins even at lower per-cohort rates.

#### Decision 4: Zone 2-3 is Valid Outcome
**Status:** AFFIRMED
**Summary:** Journey A completion (Zone 0→2) is a valid stopping point.

#### Decision 5: Add Proof-of-Work to Self-Assessment
**Status:** APPROVED
**Implementation:** After self-assessment, require:
> "Paste ONE sentence from Response 2 that shows AI understood YOUR specific situation."

**Rationale:**
- Easy for genuine shifters (they have the sentence)
- Hard for performers (they'd have to fake it)
- Agent can mechanically verify

#### Decision 6: The Explainer (Altitude Moment)
**Status:** APPROVED - NOW EVOLVED TO NODE SYSTEM
**Original:** Single 10-minute video at end of Week 2
**Evolution:** Node-based content system across all zones (see Decision 10)

---

### Decisions from Party Mode Session (2026-01-22)

#### Decision 7: Defer Context Engine
**Status:** APPROVED
**Summary:** Manual workflows for Cohort 1. No automated personalization.
**Implementation:**
- Diagnostic via Google Forms → Sheets
- Trevor manually reviews and decides interventions
- Context engine automation deferred to Cohort 2+

#### Decision 8: NotebookLM for Node Content Production
**Status:** APPROVED
**Summary:** Trevor produces zone-specific podcasts using NotebookLM
**Rationale:** NotebookLM excels at conversational perspective-shifting
**Requirement:** Create master prompts to guide podcast approach per zone

#### Decision 9: Trevor as Live Facilitator
**Status:** APPROVED
**Implementation:**
- 1-hour sessions
- Alternating days
- Per cluster (not whole cohort)
- Models the framework ("what did YOU notice?")

**Estimated time:** ~12-15 hours across 6 weeks (3 sessions/week × 4-5 active weeks)

#### Decision 10: Node-Based Learning Architecture
**Status:** APPROVED
**Summary:** Mental lattice filled by specific nodes at each zone/shift
**Framework:** Based on Cartographer's Manifesto lattice method

**Nodes per Zone Shift:**

**Zone 0→1 (Wonder) Nodes:**
1. "AI is not sci-fi—it's here" → Witnessed experience
2. "People like me use this" → Relatability mirror
3. "I could try this" → Permission + low-stakes entry
4. "It's actually fun" → Emotional engagement

**Zone 1→2 (Trust) Nodes:**
1. "It actually works for MY tasks" → Contrast experience
2. "Low-stakes wins accumulate" → Progressive confidence
3. "Errors are recoverable" → Failure safety
4. "I'm starting to rely on it" → Habit formation

**Zone 2→3 (Converse) Nodes:**
1. "Context changes everything" → Vague vs. rich comparison
2. "AI is a conversation partner" → Mental model shift
3. "Explaining clarifies MY thinking" → Meta-awareness
4. "We're getting closer together" → Iterative refinement

**Zone 3→4 (Direct) Nodes:**
1. "First draft is raw material" → Iteration mindset
2. "I have opinions about quality" → Ownership emergence
3. "Direction techniques work" → Skill acquisition
4. "I made this" → Identity shift to director

#### Decision 11: CIS Agent System for Discord
**Status:** APPROVED (Updated 2026-01-23)
**Summary:** Structured thinking agents introduced GRADUALLY from Week 1, not just for artifact creation

**Agent Roles:**
| Role | Command | Function | Introduction Week |
|------|---------|----------|-------------------|
| The Framer | /frame | Clarifies the question | Week 1 (practice mode) |
| The Explorer | /diverge | Pushes ideas without judgment | Week 4 |
| The Challenger | /challenge | Stress-tests assumptions | Week 4 |
| The Synthesizer | /synthesize | Helps write clearly | Week 6 |

**Graduated Introduction Plan (NEW):**
- **Week 1:** `/frame` available in "practice mode" - scaffolds Habit 1 (Pause before asking)
- **Weeks 2-3:** `/frame` continues + introduces context prompting - scaffolds Habit 2
- **Weeks 4-5:** Full CIS suite (`/frame`, `/diverge`, `/challenge`) - scaffolds Habit 3
- **Weeks 6-7:** `/synthesize` added - scaffolds Habit 4, artifact creation begins
- **Week 8:** Full artifact completion using all four agents

**Rationale for Early Introduction:**
- CIS agents scaffold the 4 Habits as students learn them (not just at artifact time)
- Reduces facilitator burden from Week 1 (aligned with automation goals)
- Students practice with tools before high-stakes artifact creation
- Creates familiar "thinking partners" by the time artifact matters

**Controller Logic:**
- Interprets student input
- Routes to appropriate CIS role
- Enforces conversation structure
- Tracks progress toward artifact

#### Decision 12: Hybrid Discord Model
**Status:** APPROVED
**Summary:** Private process → Public showcase

**Architecture:**
```
#thinking-lab (instructions + entry point)
    ↓
Private DM/Thread (CIS agent interactions)
    ↓ (safe, messy thinking documented)
    ↓
#thinking-showcase (finished artifacts celebrated)
```

**Rationale:**
- Process is private (safe to be messy)
- Product is public (peer learning from finished thinking)
- Journey is documented (thread becomes evidence)
- Celebration is visible (social proof, motivation)

#### Decision 13: Thinking Artifact (JTBD-Aligned)
**Status:** APPROVED
**Summary:** Artifact proves identity transformation, not AI usage

**OLD Artifact:** "How I Work With AI Now" (abstract)
**NEW Artifact:** Thinking Artifact (concrete demonstration of structured thinking)

**Artifact Types Students Can Create:**
1. **Personal Thinking Map** - "How do I approach problems now?"
2. **Problem Exploration Brief** - "Can I analyze something real?"
3. **Future-Facing Concept** - "Do I have ideas worth hearing?"

**Key Quote:** "They don't want help answering questions. They want help becoming the kind of person who answers well."

**Artifact Structure:**
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

#### Decision 14: Artifact Timeline
**Status:** APPROVED (Updated 2026-01-23 for 8-week timeline)
**Summary:** Artifact creation in Weeks 6-7, completion and showcase in Week 8
**Nature:** Required graduation deliverable
**Updated Timeline:**
- Weeks 6-7: Artifact creation begins (all CIS agents available)
- Week 8: Artifact completion, polish, and public showcase

---

### Technical Architecture Decisions

#### Decision 15: Simplified Tech Stack for Cohort 1
**Status:** APPROVED (simplified from original hybrid proposal)

| Component | Tool | Purpose |
|-----------|------|---------|
| Diagnostic | Google Forms → Sheets | SOP 0 capture |
| Student Roster | Google Sheets | Track clusters, progress |
| Submissions Log | Google Sheets | Track posts, self-assessments |
| Discord Server | Discord | Delivery platform |
| Prompt Bot | Simple bot or MEE6 | Scheduled daily prompts |
| CIS Agents | Discord bot (custom) | Thinking scaffold |

#### Decision 16: Manual Workflows for Cohort 1
**Status:** APPROVED
- Trevor manually reviews diagnostic results
- Trevor manually assigns clusters
- Trevor manually sends nudges
- Trevor manually identifies intervention needs

**Automation deferred to Cohort 2+**

---

## JTBD Framework Integration

### The Real Job Being Hired

**Functional Job:**
> "Help me move from confusion to clarity in AI before university starts."

**Emotional Job:**
> "Help me stop feeling anxious and start feeling like I belong."

**Social Job:**
> "Give me proof I can show to myself, my parents, and my future."

### Strategic Position: Dominant Strategy
K2M occupies the Dominant Strategy quadrant:
- Gets job done significantly BETTER (perception shifts + emotional safety)
- Charges significantly LESS (3,500 KES vs $1,000+)
- Competition cannot defend this position

### The Product IS the Cohort
- The 200 students learning together ARE the product
- Cohort provides: social proof, safety, witnesses, accountability
- Competition isn't other AI courses—it's avoidance and faking it

### The 4 Habits as Proof
1. Pause before asking
2. Explain context first
3. Change one thing at a time
4. Use AI before decisions

**These habits should be branded and made VISIBLE as graduation evidence.**

---

## Playbook v1 Module Mapping

| v1 Module | Status | v2 Changes |
|-----------|--------|------------|
| 1. Execution Checklist | UPDATE | New timeline, new components |
| 2. Philosophy & Guardrails | PRESERVE + ENHANCE | Add JTBD lens, node architecture |
| 3. 6-Week Cohort Design | MAJOR UPDATE | Zone nodes, new artifact, CIS integration |
| 4. Discord Architecture | UPDATE | Add CIS channels, hybrid model |
| 5. Session Scripts | REWRITE | Trevor-facilitated, node-based |
| 6. Facilitator Training | ELIMINATE | No human facilitators |
| 7. Outreach & Enrollment | MINOR UPDATE | JTBD messaging |
| 8. School Partnership | MINOR UPDATE | New outcomes framing |
| 9. Content Calendar | UPDATE | Align with new launch |
| 10. Templates & Copy | UPDATE | New artifact templates, CIS prompts |
| 11. Operational SOPs | UPDATE | Manual workflow SOPs |
| 12. Measurement & Reporting | UPDATE | New success metrics |
| 13. Timeline & Checklists | UPDATE | New timeline |

---

## Epic Structure (For Sprint Planning)

### Epic 0: Foundation & Decision Lock
**Goal:** Consolidate all decisions, create project structure
**Stories:**
- 0.1: Create this requirements document ✅ DONE
- 0.2: Create sprint-status.yaml tracking file
- 0.3: Set up output folder structure

### Epic 1: Philosophy & Framework (Module 2)
**Goal:** Update philosophy with JTBD lens and node architecture
**Stories:**
- 1.1: Review and preserve core guardrails from v1
- 1.2: Integrate JTBD identity transformation focus
- 1.3: Document node-based learning architecture
- 1.4: Define the 4 Habits branding

### Epic 2: 8-Week Design & Zone Nodes (Module 3)
**Goal:** Complete week-by-week design with node specifications (8 weeks for deeper transformation)
**Stories:**
- 2.1: Define Week 1 (Wonder) complete design + nodes + /frame introduction ✅ COMPLETE
- 2.2: Define Weeks 2-3 (Trust) complete design + nodes
- 2.3: Define Weeks 4-5 (Converse) complete design + nodes + full CIS suite
- 2.4: Define Weeks 6-7 (Direct) complete design + nodes + artifact start
- 2.5: Define Week 8 (Artifact Completion & Showcase) design
- 2.6: Create node content checklist per zone

**8-Week Timeline:**
| Week | Zone Shift | Habit Focus | CIS Agents Available |
|------|-----------|-------------|---------------------|
| 1 | 0→1 (Wonder) | Habit 1: Pause | /frame (practice mode) |
| 2-3 | 1→2 (Trust) | Habit 2: Context | /frame |
| 4-5 | 2→3 (Converse) | Habit 3: Iterate | /frame, /diverge, /challenge |
| 6-7 | 3→4 (Direct) | Habit 4: Think First | All + /synthesize, artifact begins |
| 8 | Consolidation | All 4 Habits | All, artifact completion |

### Epic 3: Session Scripts & Content (Module 5)
**Goal:** Trevor-facilitated session scripts + NotebookLM master prompts
**Stories:**
- 3.1: Create Trevor live session format + scripts
- 3.2: Create NotebookLM master prompt for Zone 0→1
- 3.3: Create NotebookLM master prompt for Zone 1→2
- 3.4: Create NotebookLM master prompt for Zone 2→3
- 3.5: Create NotebookLM master prompt for Zone 3→4
- 3.6: Create daily async prompt library (30 prompts)

### Epic 4: CIS Agent System
**Goal:** Complete CIS agent specifications and prompts
**Stories:**
- 4.1: Define CIS Controller logic
- 4.2: Create The Framer agent prompt
- 4.3: Create The Explorer agent prompt
- 4.4: Create The Challenger agent prompt
- 4.5: Create The Synthesizer agent prompt
- 4.6: Design artifact creation flow (/create-artifact)
- 4.7: Create Discord bot technical specification

### Epic 5: Discord Architecture & Operations (Modules 4, 11)
**Goal:** Updated Discord structure + manual workflow SOPs
**Stories:**
- 5.1: Design new Discord server structure
- 5.2: Define #thinking-lab channel setup
- 5.3: Define #thinking-showcase channel setup
- 5.4: Create Google Forms diagnostic
- 5.5: Create tracking Sheets templates
- 5.6: Write manual workflow SOPs

### Epic 6: Artifact System & Measurement (Modules 10, 12)
**Goal:** New artifact templates + success metrics
**Stories:**
- 6.1: Create Thinking Artifact template
- 6.2: Create artifact showcase format
- 6.3: Define new success metrics (thinking demonstration)
- 6.4: Create shift verification questions for artifact
- 6.5: Design parent reporting format
- 6.6: Create 4 Habits graduation card

### Epic 7: Final Assembly & Validation
**Goal:** Assemble complete Playbook v2
**Stories:**
- 7.1: Assemble all modules into Playbook v2
- 7.2: Cross-reference all decisions are implemented
- 7.3: Validate completeness against this requirements doc
- 7.4: Create quick-start guide for Trevor

---

## Success Criteria

Playbook v2 is COMPLETE when:

1. [ ] All 17+ decisions are implemented in documentation
2. [ ] All 13 modules updated or created
3. [ ] All zone nodes specified
4. [ ] All CIS agent prompts written
5. [ ] All NotebookLM master prompts created
6. [ ] Artifact system fully designed
7. [ ] Discord architecture documented
8. [ ] Manual SOPs written
9. [ ] Trevor can execute Cohort 1 with this playbook alone

---

## Sprint Execution Protocol

**Using BMAD Workflows:**

1. **This document** serves as PRD-equivalent
2. **create-epics-and-stories** workflow creates detailed stories
3. **sprint-planning** workflow creates sprint-status.yaml
4. **dev-story** pattern executes each story
5. Each story produces a **saved artifact**
6. sprint-status.yaml tracks all progress

**Output Location:** `_bmad-output/cohort-design-artifacts/playbook-v2/`

---

## Next Actions

1. Create sprint-status.yaml from this epic structure
2. Begin Epic 1, Story 1.1: Review and preserve core guardrails
3. Execute story by story, saving outputs
4. Update sprint-status.yaml after each story
5. Continue until all epics complete

---

*This document is the single source of truth. All sprint execution references this document. No decisions should be made that contradict this document without explicit update.*
