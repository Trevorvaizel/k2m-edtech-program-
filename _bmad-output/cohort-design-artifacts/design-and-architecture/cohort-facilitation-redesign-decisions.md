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

## Jobs To Be Done (JTBD) Analysis

**Assessment Date:** 2026-01-20
**Assessor:** Maya (Design Thinking Coach)
**Lens:** Applying Clayton Christensen's JTBD framework to the K2M cohort system

---

### The Core Insight: You're Not Selling AI Education

Through the JTBD lens, the question is: *"What job is the student hiring this program to do?"*

The documents reveal—students are **not hiring K2M to learn AI skills**. The invisible barriers in the Territory Map tell the real story:

| Zone Shift | The Barrier | The REAL Job Being Hired |
|------------|-------------|-------------------------|
| 0→1 | "I'm not a tech person" | **Help me belong** |
| 1→2 | "What if it's wrong?" | **Help me feel safe to try** |
| 2→3 | "I don't know how to explain" | **Help me feel articulate** |
| 3→4 | "Iteration feels like failure" | **Help me be okay with messiness** |

**The job is IDENTITY TRANSFORMATION, not skill acquisition.**

The Playbook already intuits this: *"Prioritize confidence over competence."* JTBD makes it explicit—**confidence IS the product. Skills are just the evidence.**

---

### Three Customers With Different Jobs

#### Students hire K2M to:
- Feel like they belong in "the AI conversation"
- Not look stupid in front of peers
- Feel ready for university (anxiety reduction)
- Have proof of transformation for parents/interviewers

#### Schools hire K2M to:
- Appear progressive to parents and boards
- Feel less anxious about something they don't understand
- Tick a "future-ready" box
- Have cover if AI goes wrong ("we trained them properly")

#### Parents hire K2M to:
- Feel like good parents investing in their child's future
- Reduce their own fear about their kid's future
- Have *proof* their 3,500 KES investment worked
- Have talking points for their friends

**Gap Identified:** The current Playbook focuses heavily on students. Schools and parents have DIFFERENT jobs that aren't explicitly served.

---

### The Cohort IS The Product (Not The Delivery Mechanism)

In JTBD, we ask: *"What alternatives could the customer hire instead?"*

If the job is "learn AI skills," students could hire:
- YouTube (free)
- Coursera (cheap)
- ChatGPT itself (free, and it teaches you!)

But if the job is **"feel like I belong + have witnesses to my transformation"**, then:
- YouTube can't do that
- Coursera can't do that
- Only a COHORT can do that

**The 200 students learning together aren't a feature—they ARE the product.** The cohort provides:
- Social proof ("others like me are doing this")
- Safety through shared vulnerability
- Witnesses to the identity shift
- Peer accountability

**Strategic Implication:** K2M's competition isn't other AI courses. The competition is **avoidance and faking it.**

---

### The 4 Habits Are Your "Proof of Purchase"

JTBD emphasizes outcomes the customer can *demonstrate.* The 4 core habits:

1. Pause before asking
2. Explain context first
3. Change one thing at a time
4. Use AI before decisions

These ARE the deliverable. Not skills. Not certificates. **Observable behavioral proof** that the student has transformed.

**Gap Identified:** These habits should be branded and made VISIBLE. Students need to be able to *show* these habits to parents, to university interviewers, to employers. Currently they're buried in facilitator training docs.

**Potential Solution:**
- "4 Habits Card" graduation artifact
- Each habit demonstrated with a real example from the student's work
- Shareable, LinkedIn-ready, parent-understandable

---

### Zone 5 Branches = Different Jobs

The Territory Map splits at Zone 5 into:
- **Maker** ("I create with AI")
- **Integrator** ("I connect AI to systems")
- **Analyst** ("I think with AI")

Through JTBD, these aren't skill tracks—they're **different aspirational identities:**
- Maker = *"Help me be someone who builds things"*
- Integrator = *"Help me be someone who makes systems work"*
- Analyst = *"Help me be someone who understands complex things"*

**Future Opportunity:** Segmentation for advanced cohorts. Not everyone wants the same transformation.

---

### Gaps & Tensions Identified

#### 1. Parent Job is Underserved
Parents are paying 3,500 KES. What job does the parent get done?

**Current:** "How I Work With AI Now" artifact helps, but parents might need more.

**Potential Solutions:**
- Progress updates that *parents* understand (not student-facing)
- Talking points for parents to share with friends ("my kid is in this program that...")
- Parent mini-education (so they understand what their kid learned)
- "Parent Report Card" at end of cohort

#### 2. School Job is Institutional-Political
Schools don't just want "students to learn AI." They want:
- Something to show the board
- Talking points for enrollment marketing
- Cover if AI goes wrong ("we trained them properly")
- Metrics they can report

**Question:** Are we packaging these outcomes for B2B sales?

#### 3. Measurement Mismatch
- Schools want to measure outcomes (grades, completion rates)
- But the real job (identity shift) is hard to measure
- This creates tension between what schools want to see vs. what actually matters

**Potential Solution:** Design "proxy metrics" that satisfy school reporting while actually measuring perception shift (the Zone verification questions in the Playbook are a start)

#### 4. Marketing vs. Delivery Tension
- Marketing likely needs to mention "AI skills" to get attention
- But delivery is about identity transformation
- This can create expectation misalignment

**Potential Solution:** Marketing leads with BELONGING and OUTCOME ("In 6 weeks, you'll go from 'AI isn't for me' to 'This is how I think now'—with 200 people who'll witness your transformation"), then explains skills as evidence

#### 5. Zone 7 is Absent—But Might Be The Real Differentiator
The cohort goes Z0→Z4. But for post-high school students facing existential questions about their future...

**Zone 7 (Philosopher)** might be the unspoken job:
- *"What does AI mean for MY career?"*
- *"What does AI mean for MY future?"*
- *"What does AI mean for MY generation?"*

That's a more profound job than "learn to use AI." Almost NO ONE is serving it.

**Question for Trevor:** Is there a Week 6 moment where we surface the Zone 7 question? Even a 5-minute reflection: "What does this shift mean for who you're becoming?"

#### 6. Facilitator as Secret Weapon (Now Agent as Secret Weapon)
The Playbook emphasized facilitator quality heavily. The new Agent-Facilitated model removes human facilitators, but the JTBD insight remains:

**The real "product" is the facilitation experience, not the content.**

The agent must deliver:
- Psychological safety (non-judgmental responses)
- Appropriate pacing (forcing functions, not rushing)
- Personalized context (the Context Engine)
- Pattern recognition (peer visibility)

If the agent fails at these, the content alone won't deliver the job.

---

### JTBD Reframe: What We Actually Sell

| What Marketing Might Say | What JTBD Says We Actually Sell |
|--------------------------|----------------------------------|
| AI skills | Identity transformation |
| A course | A cohort experience |
| Learning | Belonging |
| Competence | Confidence |
| Knowledge | Proof (for themselves and others) |
| Certificate | Witnesses to transformation |

---

### Recommended Actions

#### Immediate (Before Feb 14)
1. **Brand the 4 Habits** - Give them a name, make them visible, make them the graduation artifact
2. **Add Parent Touchpoint** - Week 3 and Week 6 progress update designed FOR parents
3. **Refine Marketing Copy** - Lead with belonging/identity, not skills

#### Near-Term (Cohort 1 Iteration)
4. **Design School Reporting Package** - Metrics that satisfy institutional needs while measuring real outcomes
5. **Test Zone 7 Moment** - Week 6 reflection on meaning/future

#### Future Cohorts
6. **Segment by Zone 5 Branch** - Advanced cohorts for Makers vs. Integrators vs. Analysts
7. **Parent Mini-Curriculum** - 3 × 10-minute videos so parents understand what their kid learned

---

### JTBD Summary Statement

**The job K2M is hired to do:**

> "Help me become the kind of person who can engage with AI confidently—and give me proof I can show to myself, my parents, and my future."

This is an **identity transformation job**, not a skill acquisition job. The cohort, the habits, and the witnesses are the product. The AI skills are just the evidence.

---

## JTBD Needs Framework Analysis (ODI Deep Dive)

**Assessment Date:** 2026-01-20
**Assessors:** Victor (Innovation Strategist) + Maya (Design Thinking Coach)
**Source:** NotebookLM synthesis of Cartographer's Manifesto, AI Territory Map, Curriculum Framework, and Cohort Playbook
**Lens:** Outcome-Driven Innovation (ODI) and JTBD Needs Framework

---

### Strategic Position: Dominant Strategy

According to the Jobs-to-be-Done Growth Strategy Matrix, K2M occupies the **Dominant Strategy** quadrant—the most dangerous position for competitors to defend against.

| Strategy | Gets Job Done | Price | K2M Position |
|----------|--------------|-------|--------------|
| **Dominant** | Significantly BETTER | Significantly LESS | ✅ **THIS IS K2M** |
| Differentiated | Better | Same/More | — |
| Discrete | Same | Less | — |
| Disruptive | Worse (then better) | Much less | — |

**Why K2M is Dominant:**

1. **Gets the Job Done BETTER:**
   - Targets perceptual shifts and emotional/social jobs (anxiety relief, belonging) that competitors ignore
   - Competitors focus only on functional job (teaching tools/prompts)
   - Time compression: 8-12 weeks → 6 weeks through diagnostic-driven personalization
   - Durable habits over fragile skills

2. **Charges Significantly LESS:**
   - 3,500 KES (~$27 USD) vs. $1,000+ for comparable high-touch cohort experiences
   - Even basic online AI courses are $50-200 USD
   - Mass-market pricing enables scale

**Strategic Implication:** Incumbents cannot defend against this position without cannibalizing their own business models. This is "Blue Ocean Strategy"—uncontested market space created by redefining value as *confidence over curriculum*.

---

### The Six Types of JTBD Needs: Complete Mapping

| Need Type | Definition | How K2M Addresses It | Status |
|-----------|------------|---------------------|--------|
| **Core Functional Job** | The primary task the user is trying to accomplish | "Move from confusion to clarity in AI" → "Get AI skills and build confidence before university starts" | ✅ Fully designed |
| **Desired Outcomes** | Metrics customers use to measure success | Minimize time to competence, minimize randomness, maximize connection density in "learning lattice" | ✅ Built into weekly progression |
| **Emotional Jobs** | How customers want to feel | "Stop feeling anxious about AI", "Feel like I belong in the AI conversation", "Remove shame of feeling behind" | ✅ Cohort structure delivers |
| **Social Jobs** | How customers want to be perceived | "Show peers I am forward-thinking", "Prove to parents I can adapt", "Signal readiness to employers/universities" | ⚠️ Artifact exists but 4 Habits not branded |
| **Consumption Chain Jobs** | Tasks around purchasing/using the product | Purchase (M-Pesa), Onboarding (SOP 0), Support (Discord + facilitator ratio) | ⚠️ Designed but not fully automated |
| **Financial Outcomes** | Metrics buyers use to judge value | "Minimize cost of signaling commitment to child's future", "Maximize ROI of transition period" | ⚠️ Price set, parent reporting weak |

---

### SOP 0 Diagnostic as Outcome-Based Segmentation

**Critical Insight:** The SOP 0 Diagnostic is not a "test"—it is an **Outcome-Based Segmentation Engine**.

Traditional market segmentation uses demographics or psychographics ("phantom targets").
ODI segmentation uses **jobs + barriers** ("real targets").

**What SOP 0 Identifies Per Student:**

| Data Point | Purpose | How It's Used |
|------------|---------|---------------|
| **Current Zone (0-4)** | Starting perceptual state | Determines which cluster, which journey |
| **Barrier Type** | What psychologically blocks progress | Enables targeted interventions |
| **Language Patterns** | Vague vs. specific intent language | Validates zone assessment |
| **Motivation/Aspiration** | Why they're here, how far they want to go | Shapes facilitator approach |
| **Felt Tension** | The emotional trigger ("I'm falling behind") | Enables empathetic framing |

**Effect of Individual Diagnostic:**

1. **Eliminates Educational Inefficiency** - No teaching concepts already mastered or perceived
2. **Enables Journey Compression** - 8-12 weeks → 6 weeks by focusing only on relevant shifts
3. **Prevents Intimidation** - Similar zones grouped together
4. **Allows Targeted Barrier Removal** - Facilitator knows exact psychological block
5. **Provides Baseline for Measuring Growth** - Language shifts become proof, not grades

---

### Clustering by Jobs-to-be-Done

**Strategic Design:** Students are assigned to clusters of 25 based on their **job variation**, determined by starting zone + barrier type.

#### Cluster Assignment Logic:

| Cluster Type | Zone Range | Primary Job | Facilitation Focus |
|--------------|-----------|-------------|-------------------|
| **Wonder Clusters** | Zone 0-1 | "Help me feel like I belong" | Permission to experiment, low-stakes play, identity safety |
| **Trust Clusters** | Zone 1-2 | "Help me feel safe to try" | Reliability proof, small wins, anxiety reduction |
| **Converse Clusters** | Zone 2-3 | "Help me feel articulate" | Context provision, collaborative thinking |
| **Direct Clusters** | Zone 3-4 | "Help me be okay with messiness" | Iteration techniques, ownership strategies |

#### Barrier-Type Distribution Within Clusters:

While zones are grouped, the diagnostic recommends **diversity of barrier types** within each cluster:
- ~30% Identity barriers
- ~25% Trust barriers
- ~25% Skill barriers
- ~20% Patience/Vision barriers

This prevents facilitators from being overloaded by a single type of psychological struggle.

#### Strategic Modeling:

Place 2 students from the next-higher zone in each cluster to model success without overwhelming beginners.

---

### Organizational Transformation: Building Innovation Competency

Per ODI theory, transforming K2M into an "outcome-driven organization" does not require training everyone. It requires:

1. **A Small Group of Practitioners** - The agent system + Trevor become the "Innovation Centre of Excellence"
2. **A Common Language** - The Zone framework, barrier types, and job terminology unite all stakeholders
3. **Data-Driven Decisions** - SOP 0 diagnostic replaces intuition with segmentation data

#### The Three-Phased ODI Roadmap Applied to K2M:

| Phase | ODI Definition | K2M Application | Status |
|-------|----------------|-----------------|--------|
| **Phase I: Understand JTBD** | Align team on customer, job, success metrics | Territory Map + Curriculum Framework created | ✅ Complete |
| **Phase II: Discover Opportunities** | Identify underserved/overserved segments through quantitative research | SOP 0 Diagnostic identifies individual needs; Cohort 1 data will reveal segment patterns | ⚠️ Designed, not yet executed |
| **Phase III: Use Insights** | Teach organization to use insights for strategy | Agent-facilitated model applies diagnostic data through Context Engine | ⚠️ Architecture designed, not built |

---

### Product Gaps Through JTBD Lens

| Need Type | Gap Identified | Recommended Action | Priority |
|-----------|----------------|-------------------|----------|
| **Social Jobs** | 4 Habits exist but aren't branded or visible | Create "K2M Habits Card" as graduation artifact; LinkedIn-shareable proof | 🔴 Before Feb 14 |
| **Consumption Chain** | Parent "purchase job" has no follow-through reporting | Design Week 3 + Week 6 parent progress updates | 🟡 Cohort 1 iteration |
| **Financial Outcomes** | Parents can't articulate ROI to peers | Create parent talking points / "bragging rights" template | 🟡 Cohort 1 iteration |
| **Emotional Jobs** | Zone 7 (Philosopher) not addressed | Add Week 6 reflection: "What does this shift mean for who you're becoming?" | 🟢 Future cohorts |

---

### Success Metrics: ODI vs. Traditional

| Metric | Traditional Innovation | ODI / K2M Approach |
|--------|----------------------|-------------------|
| **Success Rate** | 17% (ideas-first) | 86% (needs-first) |
| **What's Measured** | Features shipped, skills taught | Perception shifts, jobs completed |
| **Segmentation** | Demographics/psychographics | Jobs + Barriers |
| **Decision Making** | Loudest voice, intuition | Statistically valid customer data |
| **Language** | Company-centric ("our product") | Customer-centric ("their job") |

---

### Strategic Recommendations from JTBD Analysis

#### Immediate (Before Feb 14):
1. **Brand the 4 Habits** as "K2M AI Thinking Habits" — make them the visible proof of transformation
2. **Finalize SOP 0 Diagnostic** — ensure it captures zone + barrier + motivation for every student
3. **Design Cluster Assignment Logic** — document how diagnostic data maps to cluster placement

#### Near-Term (Cohort 1):
4. **Collect Segment Data** — after Cohort 1, analyze which job/barrier combinations are most common
5. **Build Parent Reporting** — Week 3 midpoint + Week 6 completion updates
6. **Measure Language Shifts** — track "AI gave me this" → "I directed this with AI" as proof

#### Future Cohorts:
7. **Refine Segmentation** — use Cohort 1 data to create sharper cluster definitions
8. **Advanced Cohorts** — segment by Zone 5 branch (Maker vs. Integrator vs. Analyst)
9. **Zone 7 Offering** — "What does AI mean for my generation?" philosophical cohort for graduates

---

### JTBD Summary: The Job K2M is Hired To Do

**Functional Job:**
> "Help me move from confusion to clarity in AI before university starts."

**Emotional Job:**
> "Help me stop feeling anxious and start feeling like I belong."

**Social Job:**
> "Give me proof I can show to myself, my parents, and my future."

**The Dominant Strategy Position:**
> K2M gets these jobs done significantly better (perception shifts + emotional safety) for significantly less ($27 vs. $1,000+), creating uncontested market space that incumbents cannot defend.

---

## Appendix: NotebookLM JTBD Synthesis Log

**Date:** 2026-01-20
**Source:** NotebookLM conversation analyzing Cartographer's Manifesto, AI Territory Map, AI Curriculum Framework, and Cohort Playbook through JTBD lens
**Purpose:** Raw insights that informed the JTBD Needs Framework Analysis above

---

### Topic 1: Organizational Transformation in JTBD Context

**Key Insight:** Organisational transformation in the context of Jobs-to-be-Done (JTBD) theory is not about a broad, company-wide cultural change, but rather about building a specific, data-driven competency in innovation. This transformation shifts innovation from an unpredictable "art" into a predictable "science".

**Focused Responsibility vs. Broad Change:**
The author argues that building an innovation competency does not require training thousands of employees. Instead, the responsibility for innovation should reside with a small group of people who inform those deciding which markets to enter and which products to develop. The rest of the organisation continues to validate, design, and launch products as they always have, but they are now guided by the right insights.

**The Three-Phased Roadmap to Transformation:**

| Phase | Description |
|-------|-------------|
| **Phase I: Understand Your Customer's Job-to-be-Done** | Uses intensive workshops to help a product team see their market through a JTBD lens. Aligns the team on who the customer is, what they are trying to accomplish (the Job-to-be-Done), and the metrics they use to measure success. |
| **Phase II: Discover Hidden Opportunities in Your Market** | Involves shifting to quantitative research to identify underserved and overserved segments. By using "Outcome-Based Segmentation", the company moves away from "phantom targets" based on demographics or psychographics and focuses on groups with unique sets of unmet needs. |
| **Phase III: Use New Customer Insights to Drive Growth** | Teaches employees across the organisation—from marketing to R&D—how to use these insights to formulate strategies and make data-driven business decisions. |

**Establishing an Innovation Centre of Excellence:**
A critical component of this transformation is the creation of a team of internal ODI (Outcome-Driven Innovation) practitioners who form an Innovation Centre of Excellence. These practitioners act as "change agents" or "mavericks". They are responsible for applying the 84-step ODI process to selected markets, ensuring that Jobs Theory and ODI become part of the company's "DNA and organisational fabric".

**A Common Language of Innovation:**
Transformation is supported by adopting a common language based on the customer's perspective. This unites the organisation by providing a shared lexicon (e.g., "job map", "desired outcome", "opportunity score") for discussing complex topics and making them tangible.

**Shifting the Decision-Making Culture:**
- From technology-driven to customer-needs-driven
- From intuition to facts
- Alignment across functions

By following this approach, organisations can increase innovation success rate to 86%, compared to the 17% industry average for traditional, ideas-first methods.

---

### Topic 2: K2M Ecosystem Through JTBD Needs Framework

**The Foundational Chain:**
The Cartographer's Manifesto → AI Proficiency Territory Map → AI Curriculum Framework → AI Confidence Cohort

**1. The Core Functional Job-to-be-Done:**
The foundational theory (The Cartographer's Manifesto) and the subsequent AI proficiency territory address a high-level Core Functional Job: "Move from confusion to clarity in a new field".
- The Manifesto acts as the universal map for this job, identifying the "Invisible" first principles that govern how humans build expertise.
- The AI Proficiency Territory narrows this job to the specific domain of artificial intelligence, where the job is to "reimagine what is possible when intelligence is cheap".
- The Cohort executes the tactical job for students: "Get AI skills and build confidence before university starts".

**2. Desired Outcomes (Performance Metrics):**
- For the Learner: "minimize the time it takes to reach basic competence" and "minimize the likelihood that AI feels random"
- For the AI Framework: "maximize the density of connections" in a student's "learning lattice"
- For the Cohort: "Shift from watching to participation" and moving from seeing AI as "tasks" to a "thinking partner"

**3. Emotional and Social Jobs:**
- Emotional Jobs: "Stop feeling anxious about AI" and "Feel like I belong in the AI conversation". Addresses the "felt tension" of feeling behind everyone else.
- Social Jobs: The "Artifact System" in Week 6 serves the social job of "Show peers I am forward-thinking" and "Prove to family/parents that I can adapt".

**4. Consumption Chain Jobs:**
- Buying/Enrollment: 2-minute application and M-Pesa instructions reduce friction
- Onboarding (Setup): SOP 0 (Pre-Cohort Diagnostic) ensures students are not placed in a "one-size-fits-all" environment
- Support: Discord architecture and 1:25 moderator ratio manage the job of "obtaining emotional and technical support"

**5. Financial Desired Outcomes:**
- 3,500 KES positioned to meet "minimizing the cost of signaling commitment to a child's future"
- Addresses buyer's need to "maximize the ROI of the transition period between high school and university"

**6. Related Jobs:**
While mastering AI, students are often trying to get Related Jobs done:
- "Planning a university semester"
- "Getting something tangible for a CV"

---

### Topic 3: Growth Strategy Matrix Position

**Question:** Where does K2M fall on the Growth Strategy Matrix?

**Answer:** The AI Confidence Cohort project primarily falls into the **Dominant Strategy** quadrant.

A Dominant Strategy is pursued when a company targets all consumers in a market with an offering that gets the job done significantly better and for significantly less money.

**Getting the Job Done "Better":**
- Perceptual Shift vs. Skills: While competitors focus on functional tools and prompts, K2M targets perceptual zones and emotional/social jobs—such as reducing anxiety and building belonging—which competitors often miss.
- Time Compression: The program guides learners through four major perceptual shifts in just six weeks, a journey that typically takes 8–12 weeks.
- Durable Habits: Focus on installing durable thinking habits and identity shifts rather than fragile technical skills that decay.

**Charging "Significantly Less":**
- Price Point: 3,500 KES (~$27 USD)
- Competitor Comparison: Traditional cohort-based learning models typically exceed $1,000 USD. Even indirect technical bootcamps are positioned at 50–200 USD for basic online versions.
- Market Positioning: "Low enough for mass adoption" while still high enough to signal commitment.

**Implications of a Dominant Strategy:**
A dominant strategy is the most appealing approach for a new market entrant because incumbents find it nearly impossible to defend against.
- Winning All Types of Customers: Appeals to both underserved and overserved customers simultaneously.
- Competitive Advantage: By addressing unmet emotional needs (anxiety relief) through a low-friction platform like Discord, K2M occupies a "Strategic White Space" where traditional competitors cannot effectively play.

This creates "Blue Ocean Strategy"—uncontested market space by redefining the value proposition as confidence over curriculum.

---

### Topic 4: SOP 0 Diagnostic Design

**Question:** Should the SOP diagnostic test for jobs to be done from every student or use generic testing?

**Answer:** The SOP 0 Diagnostic should NOT be a "generic test" (such as a quiz on AI facts or technical skills). It is a highly structured tool designed to uncover the specific starting point and "Invisible Barriers" for every individual student.

**What SOP 0 Identifies:**

| Data Point | Purpose |
|------------|---------|
| Current Perceptual Zone (0-4) | Where they start—Zone 0 ("AI is sci-fi") vs. Zone 2 ("AI does tasks for me") |
| Barrier Type | Identity, Trust, Skill, Patience, or Vision |
| Language Patterns | Vague vs. specific intent language validates zone assessment |
| Motivation/Aspiration | Why they're here, how far they want to go |
| Felt Tension | The emotional trigger ("I'm falling behind and university is coming") |

**Why Individual Diagnostic Matters:**

1. **Eliminates Educational Inefficiency** - No teaching concepts already mastered or perceived
2. **Enables Journey Compression** - 8-12 weeks → 6 weeks by focusing only on relevant shifts
3. **Prevents Intimidation** - Similar zones grouped together
4. **Allows Targeted Barrier Removal** - Facilitator knows exact psychological block (Identity barrier gets "Wonder and belonging" vs. Trust barrier gets "Low-Stakes Wins")
5. **Provides Baseline for Measuring Growth** - Language shifts ("AI gave me this" → "I directed this with AI") become proof, not grades

**Diagnostic as Needs-First Approach:**
The diagnostic ensures the facilitator understands the individual's "felt tension" rather than just checking off a list of skills.

---

### Topic 5: Clustering by Jobs-to-be-Done

**Question:** Does designing for a cohort mean students will be in clusters based on the job they need done?

**Answer:** Yes. Designing for this cohort involves assigning students to clusters of 25 based on the specific "job" variation they need to accomplish, determined by their starting point and psychological barriers.

**Clustering by Perceptual Zone (Starting Point):**
Similar-zone students are grouped together to ensure instruction and social environment match the specific "job" they face:
- Zone 0–1 students are in a "Wonder" phase; their job is to overcome an Identity barrier and feel like they belong
- Zone 2–3 students are in a "Converse" phase; their job is to move from simple commands to collaborative thinking
- Clustering prevents intimidation: More advanced students (Zone 3) don't dominate the conversation or intimidate Zone 0 beginners

**Balancing by "Invisible Barriers":**
While zones are grouped together, ensure diversity of barrier types within each cluster:
- Prevents facilitators from being overloaded by a single "type" of struggle
- Example mix: 30% Identity barriers, 25% Trust barriers, etc.

**Effect: Eliminating "One-Size-Fits-All":**
- Journey Compression: Know the specific "job" each cluster needs done → compress 8-12 weeks into 6 weeks
- Targeted Activation: Zone 0 cluster needs "permission to experiment and wonder"; Zone 3 cluster needs "iteration techniques and ownership strategies"

**Strategic Modeling within Clusters:**
Place a very small number (e.g., two) of higher-zone students in a lower-zone cluster to model success without overwhelming the group.

**Result:** The clusters transform the cohort from a generic course into a data-driven innovation competency, where the "product" is a precisely calibrated identity shift tailored to the individual learner.

---

### Topic 6: Uncovering the Jobs to be Done

**Question:** Uncover the jobs to be done with this cohort.

**Answer (Full JTBD Mapping):**

**1. The Core Functional Job-to-be-Done:**
"Get AI skills and build confidence before university starts"
- Subset of universal job: "Move from confusion to clarity in a new field"
- Targets students in "high-stake, emotional transition point"
- Move from Zone 0 ("AI is science fiction") to Zone 4 ("directing AI with intent")

**2. Emotional and Social Jobs:**
The "product" being sold is actually psychological safety and identity clarity during uncertainty.

*Emotional Jobs:*
- "Stop feeling anxious about AI"
- "Reduce uncertainty about my future"
- "Feel like I belong in the AI conversation"
- "Remove shame" associated with feeling behind peers

*Social Jobs:*
- "Show peers I am forward-thinking"
- "Prove to family/parents that I can adapt"
- Artifact System ("How I Work With AI Now") provides "shareable proof of change"

**3. Desired Outcomes (Success Metrics):**
- Speed of Competence: "Minimize the time it takes to reach basic competence"
- Predictability: "Minimize the likelihood that AI feels random"
- Cognitive Integration: "Maximize the density of connections" in mental "learning lattice"
- Agency: Shift from "AI gave me this" to "I directed this with AI"

**4. Consumption Chain Jobs:**
- The Purchase Job (Parent): "Minimize the cost of signaling commitment to a child's future" (3,500 KES price point)
- The Diagnostic Job (Onboarding): "Minimize the likelihood of being placed in a one-size-fits-all environment"
- The Support Job: "Obtain technical and emotional support" without friction of traditional LMS—using Discord they already use for socializing

**5. Related Jobs:**
- "Planning a university semester"
- "Networking with others going through the same transition"
- "Getting something tangible for a CV/resume"

**Summary of Strategic White Space:**
Most competitors only focus on the functional job (teaching tools). K2M wins by uniquely addressing underserved emotional and social jobs—specifically the need for relief from AI anxiety and a validated identity shift.

---

## Document History

| Date | Action | Participants |
|------|--------|--------------|
| 2026-01-19 | Initial decision document created | Trevor + BMAD Panel |
| 2026-01-19 | Added Decision 6: The Explainer (validated altitude moment) | Trevor + BMAD Panel |
| 2026-01-19 | Added Gap Analysis: February 14 Launch Readiness (Maya + BMAD Panel) | Trevor + BMAD Panel |
| 2026-01-19 | Added Automation Architecture Analysis: n8n vs Hybrid Ecosystem (Winston) | Trevor + BMAD Panel |
| 2026-01-20 | Added JTBD Analysis: Identity transformation lens on cohort design (Maya) | Trevor + Maya |
| 2026-01-20 | Added JTBD Needs Framework Analysis: ODI deep dive with Growth Strategy Matrix positioning (Victor + Maya) | Trevor + Victor + Maya |
| 2026-01-20 | Added Appendix: NotebookLM JTBD Synthesis Log (raw conversation insights) | Trevor |

---

*This document captures decisions from the Party Mode review session. Phase 2 will flesh out the complete system design.*
