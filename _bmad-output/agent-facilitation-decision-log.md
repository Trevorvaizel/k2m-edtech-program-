# Agent Facilitation Decision Log
**From Claude Conversation | Jan 17, 2026**
**Project: K2M EdTech Cohort System**

---

## THE CORE DECISION

**Question:** Can we replace 8 human facilitators with AI agents?

**Answer:** YES, but it changes success metrics.

---

## TRADEOFF ANALYSIS

### Option A: Human Facilitators (Current Playbook)
- **Success Rate:** 40% reach Zone 4
- **Scalability:** Limited (need 8 new facilitators per cohort)
- **Quality Risk:** HIGH (facilitators drift, give advice, break framework)
- **Sustainability:** LOW (training burden, burnout, coordination overhead)

### Option B: Pure Agent Facilitation
- **Success Rate:** 25% reach Zone 4, 35% reach Zone 2-3
- **Scalability:** Infinite (copy-paste infrastructure)
- **Quality Risk:** ZERO (agents follow templates perfectly)
- **Sustainability:** HIGH (zero training, no burnout)

### Option C: 90/10 Hybrid (Recommended)
- **Success Rate:** 35% reach Zone 4, 40% reach Zone 2-3
- **Scalability:** Infinite (agents scale, you stay constant)
- **Quality Risk:** LOW (you monitor culture, agents execute)
- **Sustainability:** HIGH (2 hours/week vs 14)

**DECISION: Proceed with Option C (90/10 Hybrid)**

---

## KEY ARCHITECTURE DECISIONS

### Decision 1: Replace "Noticing" with "Mechanical Verification"
**Old Model:**
- Student reflects
- Facilitator reads reflection
- Facilitator notices if shift happened
- Facilitator intervenes if needed

**New Model:**
- Student posts evidence (both AI responses)
- Student self-assesses (Clear/Subtle/No difference)
- Agent verifies mechanically (both responses posted?)
- Agent routes based on self-assessment (template interventions)
- You spot-check 5% (15-20 students/week)

**Why:** Mechanical verification scales. Human noticing doesn't.

### Decision 2: Peer Visibility Replaces Individual Feedback
**Old Model:**
- Facilitator gives personalized feedback to each student
- Students learn from individual corrections

**New Model:**
- Students see each other's work (posted publicly in clusters)
- Agent posts weekly pattern summaries ("Here's what I'm seeing...")
- Students learn from collective patterns, not individual feedback

**Why:** Learning through pattern recognition scales. Individual feedback doesn't.

### Decision 3: Self-Assessment with Calibration
**Model:**
- Students select: "Clear difference" / "Subtle difference" / "No difference"
- If "Clear" → Trusted, move forward
- If "Subtle" → Prompt: "What specifically felt different?"
- If "No difference" → Template intervention guiding them to look again

**Why:** Low-stakes self-reporting works (proven by Anki, Duolingo). Students have no incentive to lie.

---

## SUCCESS METRIC REDEFINITION

### OLD Definition (Human Facilitators):
"200 students move from Zone 0→4 with quality shifts"

### NEW Definition (Agent-Augmented):
"200 students experience the framework, with predictable outcomes:
- 25% reach Zone 4 (deep transformation)
- 35% reach Zone 2-3 (partial shift)
- 40% either drop or perform without transformation
- Framework integrity maintained at 100%
- System scales infinitely"

**Acceptance:** This redefinition is ACCEPTABLE.

---

## MODULE SWAP: WHAT REPLACED "NOTICING"

| Old Module | New Module | Mechanism |
|------------|------------|-----------|
| Facilitator notices shift | Self-assessment | Students notice their own shift |
| Facilitator reads 200 reflections | You spot-check 20 | Sampling vs exhaustive |
| Facilitator intervenes individually | Agent broadcasts patterns | One-to-many vs one-to-one |
| Facilitator detects quality issues | Weekly temperature check | Anonymous survey signals |
| Facilitator gives feedback | Peer visibility | Students learn from examples |

**Core Principle:** We replaced INDIVIDUAL attention with STRUCTURAL attention.

---

## THE RISK PROFILE

### Risks We're Accepting:
1. **Lower success rate** (25% vs 40% reach Zone 4)
   - Mitigation: Acceptable tradeoff for scalability + framework integrity

2. **Silent failures** (students confused but not detected)
   - Mitigation: Weekly temperature check + spot-checking + office hours

3. **Performance culture** (students posting to fit in)
   - Mitigation: Peer visibility shows VARIETY, not ranking. Norms pinned everywhere.

4. **Calibration drift** (students can't self-assess accurately)
   - Mitigation: Template interventions guide re-examination. Week 2 won't make sense if Week 1 was fake → self-correcting.

### Risks We've Eliminated:
1. ✅ Facilitator drift (advice-giving)
2. ✅ Quality variance (8 different styles)
3. ✅ Training bottleneck (you teaching 8 people)
4. ✅ Coordination overhead (scheduling, managing)
5. ✅ Burnout (facilitators disappearing Week 3)

---

## IMPLEMENTATION PRIORITY

### Phase 1: MUST HAVE (Before Feb 14)
1. Discord bot infrastructure (MEE6 or custom)
2. n8n workflows for Week 1 (posting + tracking + nudging)
3. Google Sheets tracking system
4. Week 1 prompts (all 5 days written)
5. Template interventions for each self-assessment option
6. Office hour script (optional Wednesday session)

### Phase 2: NICE TO HAVE (Week 2-3)
7. Weeks 2-6 prompt library
8. Weekly temperature check survey
9. Pattern summary automation (agent aggregates examples)
10. Escalation protocols

### Phase 3: OPTIMIZATION (Post-Cohort 1)
11. Calibration feedback loops
12. Peer verification system
13. Advanced analytics (shift detection)

---

## THE FEBRUARY 14TH CHECKLIST

**What Must Be Ready:**
- [ ] Discord server structure built (8 clusters)
- [ ] Bot installed + tested
- [ ] n8n instance running
- [ ] Week 1 prompts loaded
- [ ] Google Sheets template created
- [ ] You trained on spotting vs fixing (don't give advice)
- [ ] Backup plan documented (if bot fails)

**What Can Wait:**
- [ ] Weeks 2-6 prompts (can write during Week 1)
- [ ] Advanced automations (can add incrementally)
- [ ] Perfect calibration (will emerge from real data)

---

## THE NORTH STAR

**We are not maximizing individual transformation.**
**We are maximizing framework integrity at scale.**

If 50 students have deep transformations, 70 have partial shifts, and the system is ready to run 1,000 students next cohort without breaking → **WE WIN.**

---

**Document Owner:** Trevor
**Status:** LIVING DOCUMENT - Will update based on implementation discoveries
**Next Review:** After Week 1 pilot data
