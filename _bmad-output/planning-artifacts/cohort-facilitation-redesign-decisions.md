# Cohort Facilitation Redesign: Decision Document

**Date:** 2026-01-19
**Participants:** Trevor + BMAD Agent Panel (Mary, Winston, Victor, Maya, Sophia, Murat)
**Status:** Decisions Captured - Ready for Phase 2 (System Fleshing Out)

---

## Executive Summary

Through collaborative review of the Complete Cohort Operational Playbook, AI Curriculum Framework, and Cartographer's Manifesto, combined with synthesis from prior research into working educational systems, we have decided to pursue an **Agent-Facilitated Cohort Model** that replaces 8 human moderators with structured automation + peer visibility + self-assessment.

---

## The Problem Identified

### Original Design (Playbook)
- 8 human facilitators/moderators for 200 students (1:25 ratio)
- 15-20 min/day per facilitator = 14+ hours/week total
- Facilitators responsible for: posting prompts, tracking engagement, nudging silent students, detecting shifts, enforcing norms

### Problems with Human Facilitators
1. **Training Bottleneck** - Trevor becomes bottleneck for training 8 people
2. **Quality Drift** - Facilitators start giving advice (breaks framework)
3. **The Advice Trap** - Human instinct to "help" undermines self-discovery
4. **Scaling Constraint** - Need 8 new facilitators per cohort
5. **Detection Limitation** - Facilitators can't deeply know 25 students each

### The Core Insight
> "Context matters a lot for every student. This is what makes it truly scalable."

The Playbook already gathers context (SOP 0 Diagnostic) but doesn't have a mechanism to APPLY that context systematically. Human facilitators were meant to bridge this gap, but they introduce more problems than they solve.

---

## The Synthesis: What We're Building

### Research Foundation
The synthesis draws from proven patterns in:
- **freeCodeCamp** - Mechanical verification (tests, not human judgment)
- **Anki** - Self-assessment that works when low-stakes
- **Recurse Center** - Peer visibility and anti-advice culture
- **Khan Academy** - Mastery thresholds and iterative attempts
- **Learning Circles (P2PU)** - Peer learning without expert facilitators

### The Core Replacement
Human "noticing" is replaced by:
1. **Self-assessment** - Students notice their own shift
2. **Peer visibility** - Pattern emerges from collective examples
3. **Mechanical verification** - Agent checks completion, not quality
4. **Forcing functions** - Can't skip steps, gates progression
5. **Template interventions** - Adaptive support without humans

### Week 1 Design (Template)

**Pre-Week (Sunday):**
- Agent posts welcome message with expectations
- No technical knowledge required framing

**Monday - The Contrast Experience:**
- Student picks a REAL task they'll do this week
- Round 1: Ask AI without explanation
- Round 2: Ask AI with situation explained
- Post BOTH responses
- Self-assess: Clear difference / Subtle difference / No difference

**Agent Routing Based on Self-Assessment:**
- "Clear difference" → Move forward
- "Subtle difference" → Prompt to identify specific part
- "No difference" → Template intervention with guidance

**Wednesday - Peer Visibility Moment:**
- Agent posts anonymized patterns from submissions
- Shows 3 example contrasts
- Students learn from collective, not facilitator

**Thursday - Optional Office Hours:**
- Trevor (human) available 30 min in voice channel
- Not required, just available
- Models the framework (asks "what did YOU notice?")

**Friday - Consolidation:**
- Reflection prompt: What changed? When might this matter?
- Gating: Must complete to unlock Week 2

**Mechanical Verification System:**
```
Level 1: Completion Check
- Did student post? (Yes/No)
- Both responses present? (Yes/No)
- Self-assessment selected? (Yes/No)

Level 2: Self-Assessment Routing
- Routes to appropriate template intervention

Level 3: Reflection Quality (Light Touch)
- Posted? (Yes/No)
- >15 words? (Yes/No)
```

---

## Decisions Made

### Decision 1: Adopt Agent-Facilitated Model
**Approved.** We will replace 8 human facilitators with agent automation.

**Rationale:**
- Preserves framework purity (no advice-giving drift)
- Scales infinitely (copy-paste for future cohorts)
- Reduces Trevor's time from 14+ hours/week to ~2 hours/week
- Trade-off accepted: Lower per-cohort shift rate, but higher total impact through scale

### Decision 2: Accept the 90/10 Hybrid Model
**Approved.** Agents handle 90%, Trevor handles 10%.

**Agent handles (90%):**
- All mechanical tasks (prompts, tracking, nudges, reactions)
- All template interventions
- All gating/progression
- Peer visibility aggregation

**Trevor handles (10%):**
- Friday spot-check: 15-20 student reflections
- Wednesday office hours: 30 min optional
- Escalations: Agent flags students stuck 3+ days
- Culture monitoring: Are norms being followed?

**Time commitment:** ~2 hours/week

### Decision 3: Accept Shift Rate Trade-off
**Acknowledged.** Expected outcomes:

| Metric | With 8 Facilitators | With Agent System |
|--------|---------------------|-------------------|
| Reach Zone 4 | 40% (80 students) | 25-35% (50-70 students) |
| Reach Zone 2-3 | 30% (60 students) | 35-40% (70-80 students) |
| Drop/Perform | 30% (60 students) | 25-40% (50-80 students) |
| Your time/week | 14+ hours | 2 hours |
| Scalability | Limited (need 8 more) | Infinite |

**Strategic rationale (Victor's math):**
- 1 cohort × 70% shift × 200 = 140 shifted students
- 4 cohorts × 45% shift × 200 = 360 shifted students
- Scale wins even at lower per-cohort rates

### Decision 4: Zone 2-3 is a Valid Outcome
**Affirmed.** Per existing Playbook philosophy:
> "If 50% reach Zone 4 and 50% reach solid Zone 3, that's better than 100% reaching shaky Zone 4."

Journey A completion (Zone 0→2) is a valid stopping point.

### Decision 5: Add Proof-of-Work to Self-Assessment
**Approved.** Murat's recommendation:

After self-assessment, require:
> "Paste ONE sentence from Response 2 that shows AI understood YOUR specific situation."

**Rationale:**
- Easy for genuine shifters (they have the sentence)
- Hard for performers (they'd have to fake it)
- Agent can mechanically verify: Did they paste something?
- Raises the bar without adding human labor

### Decision 6: The Explainer (Altitude Moment)
**Approved.** Validated technique that transforms unconscious shift into conscious navigation.

**The Discovery Pattern:**
Students experience two realizations:
1. **First Realization** (Zone 0→1 or 1→2): "AI can actually help me"
   - Immediate, visceral understanding from experience
   - Still mostly mechanical/surface understanding

2. **Second Realization** (Zone 1→2 or 2→3): "Wait, this is about how I see, not what I know"
   - Deeper perception shift
   - Recognition that the barrier was never technical
   - **This is when they're ready for the meta-framework**

**Why Post-Second-Realization Timing:**
- **Earned Context:** They've lived through at least one perception shift
- **Pattern Recognition:** They can now see the invisible forces at work
- **Identity Readiness:** They've already shifted identity once; ready to understand identity as malleable
- **Grounded Understanding:** The framework won't be abstract theory—it'll explain their own experience

**The Explainer Design:**

| Element | Specification |
|---------|---------------|
| **Format** | Audio/Video (voice carries emotional resonance text can't) |
| **Length** | ~10 minutes total |
| **Trigger** | End of Week 2 (time-based) |
| **Delivery** | Discord post in dedicated channel or DM |
| **Tone** | Conversational, intimate—like a guide waiting for them at this exact spot |

**Structure (4 Acts):**

**Act 1: "You Just Crossed an Invisible Line" (2-3 min)**
- Mirror back what just happened to them
- Name the two realizations they've experienced
- *"The first time, AI became real. The second time, you became different."*

**Act 2: "The Map You've Been Walking" (3-4 min)**
- Reveal the Zone framework
- Show them: "You started here, you're here now"
- Explain the barriers they crossed (identity, then skill/trust)
- Key moment: *"Notice how you didn't learn more facts. You started seeing differently."*

**Act 3: "What This Means Going Forward" (2-3 min)**
- The next barriers are predictable
- You can design your own shifts now
- Perception → Skills (never the reverse)
- The invitation: *"Want to see the whole map?"*

**Act 4: "The Identity Question" (2 min)**
- The deepest pattern: every barrier is identity
- *"I'm not a tech person" → "I'm not a builder" → "I'm not a systems thinker"*
- The unlock: Identity is a story you're telling. You can change the story.

**Core Principle:**
> *"The explainer doesn't teach. It reveals what they already experienced and names it."*

**Strategic Power:**
- **Validation:** "You're not crazy. This is a real pattern."
- **Acceleration:** Conscious navigation instead of stumbling
- **Meta-skill:** Learning how to learn (transferable beyond AI)
- **Community:** "Others have walked this path. Here's the territory."

**Post-Explainer Pulse Check:**
```
"You just watched The Explainer.

Which statement feels most true right now?

[ ] I recognized myself in what was described
[ ] Some of it fit, some didn't
[ ] I'm not sure I've experienced what they described
[ ] I want to rewatch and think about it
```

**Pulse Check Routing:**
- "Recognized myself" → Shift confirmed, proceed
- "Some fit" → Partial shift, may need support
- "Not sure" → May not have shifted yet, flag for attention
- "Want to rewatch" → Engaged and processing, good sign

**Validation Status:** Trevor has already validated this technique works.

---

## Alignment with Foundational Documents

### Cartographer's Manifesto Alignment
| Force | How Synthesis Honors It |
|-------|------------------------|
| Force 1: Asymmetric Leverage | Focus on the contrast experience (the 20% that matters) |
| Force 4: Beginner's Mind | Students discover, not told; agents don't add "expertise noise" |
| Force 6: Context Spectrum | Context gathered once, applied throughout |
| Force 7: Failure Gradients | "No difference" → try again (iteration built in) |
| **The Four Layers** | The Explainer reveals Layer 3-4 (principles, invisible) AFTER students experience Layer 1-2 |
| **Satellite View** | The Explainer provides the "whole map" after they've walked part of the territory |
| **Creed 2: Self-Discovery** | "I cannot give you expertise. I can only show you the path." - Explainer names what they discovered |

### AI Curriculum Framework Alignment
| Journey Element | How Synthesis Delivers |
|-----------------|----------------------|
| Zone 0→1 (Wonder) | Contrast experience creates "wow" |
| Zone 1→2 (Trust) | Low-stakes practice builds confidence |
| Zone 2→3 (Converse) | The Explainer enables conscious navigation |
| Diagnostic | SOP 0 still applies, context feeds system |
| Facilitation | Peer visibility replaces facilitator noticing |
| **Journey A→B Transition** | The Explainer marks the threshold between Journey A completion and Journey B readiness |

### Playbook Alignment
| Playbook Element | Status |
|------------------|--------|
| Philosophy & Guardrails | Preserved - no comparing, no grading, confidence over competence |
| 6-Week Structure | Preserved - same progression |
| SOP 0 Diagnostic | Enhanced - context now flows through system |
| Facilitator Training | Eliminated - agents replace moderators |
| Discord Architecture | Modified - agent-driven channels |
| Session Scripts | Adapted - template-based, agent-posted |

---

## Gap Identified (For Phase 2)

### Resistance-Type Routing
The synthesis has ONE template intervention for "no difference" students.

The AI Curriculum Framework identifies 4 resistance types:
- Skeptic
- Overwhelmed
- Perfectionist
- Dismissive

**Decision:** Defer to Phase 2. Explore whether template interventions need to differentiate by resistance type, or if the simpler approach is sufficient for MVP.

---

## Gap Analysis: February 14 Launch Readiness

**Assessment Date:** 2026-01-19
**Assessor:** Maya (Design Thinking Coach) + BMAD Panel
**Status:** Strong strategy, thin on execution. 47-66 hours of build work identified.

### 🔴 CRITICAL GAPS (Block Launch Without These)

#### Gap 1: The Explainer Script - NOT WRITTEN
**Current State:** Concept fully designed (4 acts, structure, timing), but NO SCRIPT exists
**Risk:** Week 2 arrives, nothing to deliver
**Missing Components:**
- [ ] Act 1 script (2-3 min): "You Just Crossed an Invisible Line"
- [ ] Act 2 script (3-4 min): "The Map You've Been Walking"
- [ ] Act 3 script (2-3 min): "What This Means Going Forward"
- [ ] Act 4 script (2 min): "The Identity Question"
- [ ] Format decision: Trevor's voice vs. AI voice vs. professional voice actor
- [ ] Production plan: Recording, editing, file hosting
- [ ] Delivery mechanism: Discord DM? Channel post? Email?

**Time Estimate:** 6-9 hours (write + produce)

#### Gap 2: Week 2-6 Prompt Library - ONLY WEEK 1 DESIGNED
**Current State:** Week 1 fully designed, template pattern established, but ZERO content for Weeks 2-6
**Risk:** Week 1 ends, no content for Week 2
**Missing Components:**
- [ ] Week 2: 5 daily prompts (theme: "Small Changes, Big Differences")
- [ ] Week 3: 5 daily prompts (theme: "AI as Thinking Partner")
- [ ] Week 4: 5 daily prompts (theme: "Quality Through Iteration")
- [ ] Week 5: 5 daily prompts (theme: "Noticing the Shift")
- [ ] Week 6: 5 daily prompts (theme: "Consolidation + Artifact")
- [ ] Total: 30 prompts to design from scratch

**Time Estimate:** 12-15 hours

#### Gap 3: Technical Implementation Specifications - ARCHITECTURE ONLY
**Current State:** We know WHAT agents should do, but not HOW to build it
**Risk:** Feb 13 arrives, nothing works
**Missing Components:**

**Discord Bot:**
- [ ] Platform decision: MEE6? Custom Discord.py? Carl-bot?
- [ ] Permissions matrix
- [ ] Scheduled posting mechanism
- [ ] DM automation
- [ ] Emoji reaction system
- [ ] Rule violation detection (keyword scanning)
- [ ] Error handling procedures

**n8n Workflows (8 workflows needed):**
- [ ] Workflow 1: Daily prompt posting
- [ ] Workflow 2: Engagement tracking (Google Sheets)
- [ ] Workflow 3: Day 3/7 nudge automation
- [ ] Workflow 4: Self-assessment routing
- [ ] Workflow 5: Reflection quality check
- [ ] Workflow 6: Week gating (unlock mechanism)
- [ ] Workflow 7: Peer visibility aggregation
- [ ] Workflow 8: Daily dashboard generation

**Google Sheets:**
- [ ] Student roster template
- [ ] Submissions tracking table
- [ ] Interventions log
- [ ] Culture metrics
- [ ] API configuration

**Time Estimate:** 15-20 hours

### 🟡 HIGH PRIORITY GAPS (Degraded Experience Without These)

#### Gap 4: Context Application Engine - CONCEPT ONLY
**Current State:** "Context flows through system" - but no mechanism designed
**Risk:** SOP 0 diagnostic data collected but not used. Personalization opportunity lost.
**Missing Components:**
- [ ] Data model: What context fields? How stored?
- [ ] Application logic: How does context change prompts/interventions?
- [ ] Example logic: "Teacher" gets teacher examples, "Marketer" gets marketer examples
- [ ] Integration: How does n8n access and use context?
- [ ] Privacy: How is student context protected?

**Time Estimate:** 6-8 hours

#### Gap 5: Fallback Procedures - NOT DOCUMENTED
**Current State:** No plan for tech failure
**Risk:** Bot crashes → chaos → cohort disruption
**Missing Components:**
- [ ] Bot failure detection: How do you know it's down?
- [ ] Alert system: Who gets notified?
- [ ] Manual posting procedure: Trevor's backup guide
- [ ] Communication plan: How to tell students "bot down, wait"?
- [ ] Backup bot: Hot standby?
- [ ] Alternative channel: WhatsApp for critical comms?

**Time Estimate:** 3-4 hours

#### Gap 6: Testing & Validation Plan - NOT DEFINED
**Current State:** Feb 14 is go-live. When do we TEST this?
**Risk:** Launch day → nothing works → 200 students waiting
**Missing Components:**
- [ ] Beta cohort: 5-10 students, 1-week test
- [ ] Test script: What exactly to test?
- [ ] Success criteria: What = "ready to launch"?
- [ ] Fix window: Time between beta and launch
- [ ] Rollback plan: What if launch fails?

**Time Estimate:** 8-10 hours (including beta test execution)

### 🟢 MEDIUM PRIORITY GAPS (Can Launch Without, Should Address Soon)

#### Gap 7: Resistance-Type Routing - DEFERRED
**Current State:** Identified as gap, deferred to Phase 2
**Risk:** One template for all resistance types; some get generic help
**Decision Point:** Keep simple (MVP) or differentiate (better experience)?
**If Differentiate:**
- [ ] 4 intervention templates (Skeptic, Overwhelmed, Perfectionist, Dismissive)
- [ ] Detection logic: How does agent identify type?
- [ ] Routing logic: Which intervention to which type?

**Time Estimate:** 4-6 hours (if we proceed)

#### Gap 8: Success Metrics Dashboard - NOT DESIGNED
**Current State:** How will we KNOW if this worked?
**Risk:** Week 6 ends, no data, can't prove success/failure
**Missing Components:**
- [ ] Daily metrics: Engagement, completion, self-assessment distribution
- [ ] Weekly metrics: Shift verification, culture health, violations
- [ ] Final metrics: Zone 4 reach, Zone 2-3 reach, dropout
- [ ] Comparison: Agent vs. human facilitator benchmarks
- [ ] Data export: Post-cohort analysis

**Time Estimate:** 4-5 hours

#### Gap 9: Onboarding Sequences - NOT DESIGNED
**Current State:** Student joins Discord → what happens?
**Risk:** Confusion, bad first impression
**Missing Components:**
- [ ] Welcome DM flow when joining
- [ ] Channel walk-through: Where to go, what first
- [ ] Expectation setting: "How this works"
- [ ] Tech help: ChatGPT/Claude access
- [ ] Norms intro: "We share experiences, not advice"

**Time Estimate:** 3-4 hours

### 🔵 LOW PRIORITY GAPS (Nice to Have, Can Iterate Post-Launch)

#### Gap 10: The Explainer Pulse Check - CONCEPT ONLY
**Time Estimate:** 2-3 hours

#### Gap 11: Post-Cohort Handoff - NOT DEFINED
**Time Estimate:** 2-3 hours

---

## Time Budget Summary

| Priority Category | Total Time Estimate | Must-Have Before Launch |
|-------------------|---------------------|------------------------|
| 🔴 Critical Gaps | 47-66 hours | ALL |
| 🟡 High Priority | 17-22 hours | Context Engine (can defer), Fallback (must), Testing (must) |
| 🟢 Medium Priority | 11-15 hours | None (can defer post-launch) |
| 🔵 Low Priority | 4-6 hours | None (can defer post-launch) |
| **MINIMUM VIABLE LAUNCH** | **68-84 hours** | **~8-10 days of focused work** |

**Realistic Assessment:** Trevor has ~26 days until Feb 14. If dedicating 3-4 hours/day = feasible. If sporadic availability = high risk.

**Recommendation:**
1. **Simplify Week 2-6 prompts** - Reduce from 12-15 hours to 6-8 hours (functional vs. polished)
2. **Defer Context Engine** - Launch without personalization, iterate later
3. **Defer The Explainer** - Launch without it, add Week 3 instead of Week 2
4. **Reduce Tech Scope** - Manual posting Week 1, automate Week 2+

**Question for Trevor:** What's the MVP scope that hits Feb 14 with 80% of the value?

---

## Automation Architecture Analysis

**Assessment Date:** 2026-01-19
**Assessor:** Winston (Architect)
**Question:** Must we use n8n? What are the ecosystem trade-offs?

### The Challenge

We need automation for:
1. Discord bot operations (post, track, DM)
2. Self-assessment routing logic
3. Google Sheets integration
4. Context data application (personalization engine)
5. Scheduled posting
6. Rule enforcement
7. Error handling

Original assumption: n8n for everything.
**Trevor's Question:** Are there better options in different ecosystems?

---

## Ecosystem Comparison

### Option 1: n8n (Self-Hosted Workflow Automation)

**✅ Pros:**
- Cost: FREE (self-hosted)
- Power: Complex logic (if/then/else, loops, branching)
- Discord Integration: Native Discord node
- Data Privacy: All data stays on your server
- Flexibility: JavaScript/Python code within workflows
- Context Engine: Can build sophisticated routing

**❌ Cons:**
- Setup Complexity: Must host (VPS, Docker, local)
- Maintenance: You own updates, backups, uptime
- Technical: DevOps knowledge required
- Learning Curve: Workflow design takes time

**Setup Time:** 4-6 hours + ongoing maintenance

---

### Option 2: Zapier (Cloud Automation)

**✅ Pros:**
- Ease of Use: Beginner-friendly visual builder
- Discord Integration: Official app, well-documented
- Reliability: 99.9% uptime hosted
- Templates: Pre-built Zaps

**❌ Cons:**
- **COST PROHIBITIVE:**
  - 200 students × 5 actions/day = 1,000 tasks/day
  - Professional plan: $19.99/mo (750 tasks/day) = NOT ENOUGH
  - Team plan: $299/mo = UNAFFORDABLE
- Logic Limits: Complex routing requires Pro plan
- Data Privacy: Student data flows through Zapier servers

**Verdict:** NOT VIABLE for production

---

### Option 3: Make.com (formerly Integromat)

**✅ Pros:**
- Visual Builder: More intuitive than Zapier
- Pricing: Better than Zapier ($29/mo for 10K operations)
- Error Handling: Built-in
- Discord Integration: Official app

**❌ Cons:**
- Cost: $29-59/mo ongoing
- Data Privacy: Student data in cloud
- Learning Curve: More complex than Zapier

**Cost Estimate:** $29-59/mo ongoing

**Verdict:** Viable but expensive over time

---

### Option 4: Discord.py (Custom Python Bot)

**✅ Pros:**
- Complete Control: Own every line of code
- No Limits: Anything Discord API allows
- Cost: FREE (just hosting)
- Performance: Faster than workflow tools
- Context Engine: Sophisticated in-code implementation
- Data Privacy: Complete control

**❌ Cons:**
- Development Time: 40-60 hours to build everything
- Technical Skill: Requires Python knowledge
- Maintenance: You own bugs, updates, API changes

**Verdict:** Most powerful but highest development cost

---

### Option 5: Google AppSheet + Apps Script

**✅ Pros:**
- Google Native: Perfect Sheets integration
- Context Engine: AppSheet UI for context data
- No-Code: Visual builder
- Cost: Included in Google Workspace ($6/user/mo)

**❌ Cons:**
- **NO NATIVE DISCORD INTEGRATION** (dealbreaker)
- Workaround: Webhooks + custom code = complexity
- Complex Logic: Harder than n8n
- Limited Scheduling: Apps Script triggers limited

**Verdict:** Not ideal for Discord-heavy use case

---

### Option 6: Pipedream (Workflow Automation)

**✅ Pros:**
- **Generous Free Tier:** 5,000 tasks/month (might cover your needs)
- Developer-Friendly: Node.js/JavaScript
- Discord Integration: Native app
- Error Handling: Built-in
- Speed: Faster than n8n

**❌ Cons:**
- Less Visual: More code-centric
- Younger Platform: Smaller community
- Learning Curve: Requires JavaScript comfort

**Cost Estimate:** FREE (free tier) or $10/mo

**Verdict:** Strong contender - free tier might work

---

## Comparison Matrix

| Dimension | n8n | Zapier | Make.com | Discord.py | AppSheet | Pipedream |
|-----------|-----|--------|----------|------------|----------|-----------|
| **Cost (Monthly)** | FREE | $50-100 | $29-59 | FREE | $6 | FREE-$10 |
| **Setup Complexity** | Medium | Low | Medium | HIGH | Medium | Medium |
| **Discord Native** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Google Sheets** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Native | ✅ Yes |
| **Complex Routing** | ✅ Excellent | ⚠️ Pro only | ✅ Good | ✅ Unlimited | ⚠️ Limited | ✅ Good |
| **Context Engine** | ✅ Easy | ⚠️ Possible | ⚠️ Possible | ✅ Powerful | ✅ Built-in | ✅ Good |
| **Data Privacy** | ✅ Self-hosted | ❌ Cloud | ❌ Cloud | ✅ Self-hosted | ✅ Google | ❌ Cloud |
| **Maintenance** | You own it | Zapier owns it | Make owns it | You own it | Google owns it | Pipedream owns it |
| **Setup Time** | 4-6 hours | 1-2 hours | 2-3 hours | 40-60 hours | 6-8 hours | 3-4 hours |
| **Learning Curve** | Medium | Low | Medium | HIGH | Medium | Medium |
| **Scalability** | ✅ Unlimited | ❌ Expensive | ⚠️ Limited | ✅ Unlimited | ⚠️ Limited | ✅ Good |

---

## RECOMMENDATION: Hybrid Architecture

**The Question:** Can the context engine work in a Google ecosystem without n8n?

**The Answer:** YES - and it's MORE powerful than n8n alone for this use case.

### Proposed Hybrid: Discord.py + Pipedream + Apps Script + Google Sheets

#### Component Responsibilities:

**Discord.py (Custom Bot):**
- High-volume operations: Post prompts, emoji reactions
- Rule enforcement (keyword scanning)
- Scheduled messages (cron jobs)
- **Why:** Speed and reliability for simple, high-volume tasks

**Google Sheets (Database):**
- Student roster + context data
- Example library (tagged by profession)
- Intervention library (tagged by barrier type)
- Submissions tracking log
- **Why:** Native database, editable UI, instant queries

**Apps Script (Query Layer):**
- `getStudentContext(studentId)` - Retrieve profile
- `getExamplesByProfession(profession)` - Get relevant examples
- `getIntervention(barrierType)` - Get targeted template
- Expose functions as webhooks
- **Why:** Native Google performance, custom JavaScript logic

**Pipedream (Orchestration):**
- Complex routing: If "no difference" → get barrier type → send intervention
- Day 3/7 nudges with logic
- Dashboard aggregation
- **Why:** Free tier (5K tasks/month), visual builder for complex logic

#### Architecture Diagram:

```
┌─────────────────────────────────────────┐
│  Discord.py Bot (Custom)                │
│  • High-volume: Post prompts, reactions  │
│  • Rule enforcement                     │
│  • Scheduled messages                   │
└──────────────┬──────────────────────────┘
               │
        ┌──────▼────────────────┐
        │  Google Sheets        │
        │  • Student roster     │
        │  • Context data       │
        │  • Example library    │
        │  • Interventions       │
        └──────┬────────────────┘
               │
        ┌──────▼────────────────┐
        │  Apps Script          │
        │  • Context queries    │
        │  • Example filtering  │
        │  • Intervention logic  │
        │  (Exposed as webhooks) │
        └──────┬────────────────┘
               │
        ┌──────▼────────────────┐
        │  Pipedream            │
        │  • Complex routing    │
        │  • Day 3/7 nudges     │
        │  • Dashboard          │
        └───────────────────────┘
```

---

## How The Context Engine Works in Hybrid

### Example: Sarah (Teacher, Identity Barrier)

**Step 1: SOP 0 Diagnostic Data Stored (Google Sheets)**
```
Student_Context Sheet:
| student_id | name  | zone | barrier  | profession | situation         |
| discord_123 | Sarah | 1    | identity | teacher    | lesson planning  |
```

**Step 2: Monday Prompt Posts with Teacher Examples**

**Discord.py Flow:**
```python
# Get cluster students
students = get_cluster_students(cluster_id=1)

# Query context via Apps Script
professions = [get_context(s)['profession'] for s in students]
common_profession = mode(professions)  # "teacher"

# Get teacher examples via Apps Script
examples = get_examples_by_profession('teacher')
# Returns: 3 teacher-specific examples

# Post prompt with RELEVANT examples
prompt = f"""
WEEK 1 PRACTICE

📌 EXAMPLES FROM OTHER TEACHERS:
{examples[0]} - Lesson planning with AI
{examples[1]} - Parent email communication
{examples[2]} - Grading workflow support

Post BOTH responses...
"""

discord_bot.post(prompt)
```

**What Sarah Sees:** Examples from teachers doing her work, not generic "write an email"

**Step 3: Sarah Posts "No Difference" → Gets Identity-Barrier Intervention**

**Pipedream Workflow:**
```yaml
Trigger: Discord message
Condition: self_assessment === "No difference"

Step 1: Apps Script webhook → get_student_context(student_id)
Returns: {barrier: "identity", profession: "teacher"}

Step 2: Apps Script webhook → get_intervention("identity")
Returns: "You mentioned feeling 'not technical.' AI doesn't require technical expertise..."

Step 3: Discord DM → Send personalized intervention
Target: Sarah
Content: References her specific identity barrier
```

**What Sarah Receives (DM):**
> "Hey Sarah!
>
> You mentioned feeling 'not technical.' That's a common barrier for teachers.
>
> Here's the thing: AI doesn't require technical expertise. It responds to clear thinking about YOUR situation.
>
> Try this: Find one sentence in Response 2 that sounds like it understands your situation as a teacher (your classroom, your students)."

**Key:** The intervention REFERENCES her specific barrier and profession.

---

### Why Hybrid Beats n8n for Context Engine

**Advantage 1: Google Sheets as Native Database**
- n8n: External connector, latency
- Apps Script: Native to Sheets, instant (<100ms vs 500ms-2s)
- Editing: You can edit context directly in Sheets UI

**Advantage 2: Context Query Flexibility**
```javascript
// Apps Script - Custom logic
function getTeachersWithIdentityBarrier() {
  return students.filter(s =>
    s.profession === 'teacher' && s.barrier === 'identity'
  );
}

// n8n: Requires complex workflow construction
```

**Advantage 3: Iteration Speed**
- Add context field? Add column to Sheet (done)
- Change query logic? Edit Apps Script function (done)
- No workflow redraw, no node reconfiguration

**Advantage 4: Cost**
- Discord.py: FREE (hosting only)
- Google Sheets/Apps Script: FREE (included in Workspace)
- Pipedream: FREE tier (5K tasks/month might cover it)
- Total: $0-10/mo vs n8n's self-hosting maintenance

---

## Implementation Timeline: Hybrid Approach

### Phase 1: Context Database (2 hours)
- [ ] Create Google Sheet with 3 tabs
- [ ] Add 10 example records per profession
- [ ] Add intervention templates per barrier type
- [ ] Test manual data entry

### Phase 2: Apps Script Layer (2 hours)
- [ ] Write `getStudentContext()` function
- [ ] Write `getExamplesByProfession()` function
- [ ] Write `getIntervention()` function
- [ ] Deploy as web app
- [ ] Test webhook URLs

### Phase 3: Discord.py Core (6-8 hours)
- [ ] Bot setup + authentication
- [ ] Scheduled posting function
- [ ] Emoji reactions
- [ ] Rule violation detection
- [ ] Apps Script integration (context queries)

### Phase 4: Pipedream Routing (2-3 hours)
- [ ] Account setup + Discord connection
- [ ] Workflow: "No difference" intervention
- [ ] Workflow: Day 3/7 nudges
- [ ] Workflow: Dashboard aggregation
- [ ] Error handling setup

### Phase 5: Testing (3-4 hours)
- [ ] Beta test with 5 students
- [ ] Verify context queries work
- [ ] Test personalization is applied
- [ ] Validate routing logic

**Total Time:** 15-19 hours (vs 40-60 hours for pure Discord.py, vs 4-6 hours n8n setup + maintenance)

---

## Final Recommendation

**Use Hybrid Architecture:**

1. **Discord.py** for raw bot operations (speed, reliability)
2. **Google Sheets** as context database (native, editable)
3. **Apps Script** for query layer (instant, flexible)
4. **Pipedream** for complex routing (free tier, visual builder)

**Why This Wins:**
- ✅ Zero monthly cost (or $10/mo)
- ✅ Better context engine than n8n
- ✅ More maintainable than pure Discord.py
- ✅ Native Google ecosystem for Sheets
- ✅ Free tier handles significant volume
- ✅ Each tool does what it's best at

**Trade-off:** More moving parts than n8n-only. But each part is replaceable and best-in-class.

**Decision Status:** DOCUMENTED - Ready for Trevor's approval

---

## Next Phase: System Fleshing Out

### Phase 2 Scope
1. **Complete Week 1-6 Design** - Apply this template pattern to all 6 weeks
2. **Agent Architecture** - Specify exact Discord bot + n8n workflows
3. **Context Application Engine** - How diagnostic data flows to personalized nudges/examples
4. **Resistance-Type Routing** - Determine if differentiation needed
5. **The Explainer Production** - Script, format, and delivery mechanism
6. **Build Plan** - Technical implementation before Feb 14

### Phase 2 Deliverables
- [ ] Week 2-6 experience designs (same template pattern)
- [ ] Discord server structure (channels, roles, permissions)
- [ ] n8n workflow specifications
- [ ] Agent intervention templates (full library)
- [ ] Context schema (what data, how stored, how applied)
- [ ] **The Explainer script** (4 acts, ~10 minutes)
- [ ] **Explainer format decision** (Trevor voice vs. AI voice vs. video)
- [ ] **Post-Explainer pulse check integration**
- [ ] Testing plan (beta cohort before launch)

### Phase 2 Timeline
- Target: Complete before Feb 14, 2026 cohort launch
- Estimate: 15-25 hours of design + build work

---

## Document History

| Date | Action | Participants |
|------|--------|--------------|
| 2026-01-19 | Initial decision document created | Trevor + BMAD Panel |
| 2026-01-19 | Added Decision 6: The Explainer (validated altitude moment) | Trevor + BMAD Panel |
| 2026-01-19 | Added Gap Analysis: February 14 Launch Readiness (Maya + BMAD Panel) | Trevor + BMAD Panel |
| 2026-01-19 | Added Automation Architecture Analysis: n8n vs Hybrid Ecosystem (Winston) | Trevor + BMAD Panel |

---

*This document captures decisions from the Party Mode review session. Phase 2 will flesh out the complete system design.*
