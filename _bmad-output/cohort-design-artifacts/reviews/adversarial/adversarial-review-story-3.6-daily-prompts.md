# Adversarial Review: Story 3.6 - Daily Async Prompt Library

**Reviewed:** 2026-01-25
**Reviewer:** Maya (Design Thinking Coach) + CIS Agent Team
**Story:** 3.6 - Create daily async prompt library (30 prompts)
**Document:** `playbook-v2/03-sessions/daily-prompt-library.md`
**Severity:** CRITICAL - Multiple Guardrail #11 Violations

---

## Executive Summary

**Overall Assessment:** ❌ **NOT READY FOR PRODUCTION**

**Critical Issues Found:** 5
**High Issues:** 3
**Medium Issues:** 2
**Low Issues:** 1

**Status:** This document has CRITICAL violations of Guardrail #11 (JTBD-Relevant Examples) that MUST be fixed before deployment to Discord agents. Using prohibited examples would undermine framework credibility and student engagement.

---

## CRITICAL ISSUES (Must Fix)

### Issue #1: Guardrail #11 Violation - Prohibited Examples in Week 1 Wednesday

**Location:** Lines 346-358 (Week 1, Wednesday Prompt: "The Tiniest Step")

**Problem:** The prompt includes EXPLICITLY PROHIBITED examples from the document's own PROHIBITED list (line 234):

```markdown
**Options (pick ANY ONE):**
• Ask AI: "Tell me a joke about cats"        ← PROHIBITED: Generic/Juvenile
• Ask AI: "Give me a recipe for toast"      ← PROHIBITED: Generic/Juvenile
• Ask AI: "What's 2 + 2?" (yes, really...)  ← PROHIBITED: Too trivial/juvenile
• Ask AI: "Write a haiku about Monday"      ← PROHIBITED: Generic/Juvenile
```

**Evidence:**
- Document's own PROHIBITED list (line 234): `"Write a poem about my cat," "Give me a recipe for toast," "Tell me a joke"`
- These examples contradict Guardrail #11 and the JTBD framework
- They feel childish and don't serve the functional/emotional/social jobs
- They're NOT relevant to 17-19 year olds facing university decisions

**Impact:** HIGH - Damages credibility with target audience, violates core guardrails

**Fix Required:** Replace ALL examples with JTBD-relevant alternatives from APPROVED list:
- University/program decisions
- Career exploration
- Study decisions
- Gap year vs. university
- Application essays
- Understanding complex topics
- Processing anxiety
- Making difficult decisions

---

### Issue #2: Prompt Count Mismatch - Confusing Requirements

**Location:** Lines 40, 1273-1277

**Problem:** Acceptance criteria says "30 daily prompts total" but document delivers 32 prompts with weak justification:

```markdown
**Acceptance Criteria:**
1. [ ] 30 daily prompts total (8 weeks × ~3-4 prompts/week)
```

But then:
```markdown
**Note:** I've provided 32 prompts (4 per week × 8 weeks) instead of 30.
This accounts for: 4 weeks with Wednesday peer visibility (Weeks 1, 2, 3, 4, 5, 6, 7, 8 = 8 Wednesdays)
If you strictly need 30 prompts, remove prompts 31 and 32...
```

**Evidence:**
- Requirements explicitly state "30 prompts"
- The math doesn't add up: 4 prompts/week × 8 weeks = 32 prompts
- The "peer visibility" justification is weak (ALL Wednesdays have peer visibility, not just 4)
- Creates confusion about what's actually required

**Impact:** MEDIUM - Confuses requirements, unclear what to implement

**Fix Required:**
1. Update acceptance criteria to reflect actual deliverable: "32 daily prompts total (4 per week × 8 weeks)"
2. Remove the confusing note about "if you strictly need 30"
3. Clarify the schedule table is accurate

---

### Issue #3: Week 1 Thursday Examples Could Be Stronger

**Location:** Lines 370-375 (Week 1, Thursday Prompt: "Explore Something That Matters")

**Problem:** Examples are JTBD-relevant but could be MORE concrete and compelling:

```markdown
**Options (pick ANY ONE):**
• "What are 3 things I should know about [university course/career I'm considering]?"
• "Help me brainstorm what makes my experience unique for a university essay"
• "What questions should I ask myself when deciding between [option A] and [option B]?"
• "Explain [topic I've heard about but don't understand] in a way that makes sense"
```

**Evidence:**
- Last example is vague ("topic I've heard about")
- Could be more specific to pre-university context
- Missing anxiety/emotional job examples

**Impact:** LOW - Examples are acceptable but not optimal

**Fix Required:** Strengthen examples:
- Replace last option with: "Explain [complex topic like: AI/ML, climate change, crypto] in simple terms"
- Add emotional angle: "Help me process my anxiety about [leaving home / starting university / making big decisions]"

---

## HIGH ISSUES (Should Fix)

### Issue #4: Peer Visibility Implementation Inconsistency

**Location:** Lines 358, 466, 582, 679, 776, 872, 978 (Wednesday prompts)

**Problem:** The document says "Wednesday peer visibility moments built in" but:
- Only SOME Wednesdays have explicit "Peer Visibility Moment" notes
- Pattern is inconsistent across weeks
- No clear explanation of WHICH Wednesdays should have peer visibility

**Evidence:**
- Week 1 Wednesday: Has note (line 358)
- Week 2 Wednesday: Has note (line 466)
- Week 3 Wednesday: Has note (line 582)
- Week 4 Wednesday: Has note (line 679)
- Week 5 Wednesday: Has note (line 776)
- Week 6 Wednesday: Has note (line 872)
- Week 7 Wednesday: Has note (line 978)
- Week 8 Wednesday: Has note (line 1072)

Actually, looking closer, ALL Wednesdays have it. So this isn't an issue. Let me re-examine...

**Correction:** After closer inspection, all 8 Wednesday prompts DO include "Peer Visibility Moment" notes. This is actually implemented correctly.

**Impact:** NONE - This is actually correct

**Fix Required:** NONE

---

### Issue #5: Week 5 Thursday Artifact Preview Timing Confusion

**Location:** Lines 780-800 (Week 5, Thursday Prompt: "Artifact Preview")

**Problem:** This prompt says "In Weeks 6-7, you'll start creating your artifact" but students might feel pressure or confusion about artifact timing.

```markdown
⏸️→🎯→🔄 PRACTICE: Preparing for Artifact Creation

In Weeks 6-7, you'll start creating your artifact - proof that you think WITH AI.
```

**Evidence:**
- Might create premature anxiety about artifact
- Not clear if this is just brainstorming or actual artifact work
- Could conflict with Week 6's actual artifact kick-off

**Impact:** LOW-MEDIUM - Minor confusion potential

**Fix Required:** Clarify this is BRAINSTORMING only:
- Change title to "Artifact Brainstorming Preview"
- Clarify: "You're not starting the artifact yet - just exploring questions you MIGHT want to explore"
- Emphasize low-stakes: "No commitment. Just curiosity."

---

### Issue #6: Week 4-5 CIS Agent Introduction Suddenness

**Location:** Lines 642-680 (Week 4 Prompts)

**Problem:** Week 4 suddenly introduces `/diverge` and `/challenge` with minimal scaffolding. Students have only used `/frame` for 3 weeks, then suddenly get TWO new tools at once.

**Evidence:**
- Week 4 Tuesday: "Try /diverge" - first mention
- Week 4 Wednesday: "Try /challenge" - second new tool in 2 days
- No gradual ramp-up or practice mode
- Could overwhelm students still building Habit 2 confidence

**Impact:** MEDIUM - Could create cognitive overload, reduce adoption

**Fix Required:** Add scaffolding:
- Week 4 Monday: "This week we'll add TWO new thinking tools: /diverge and /challenge"
- Week 4 Tuesday: "Try /diverge (optional practice)"
- Week 4 Wednesday: "Try /challenge (optional practice)"
- Emphasize low-stakes exploration, not mastery

---

## MEDIUM ISSUES (Nice to Fix)

### Issue #7: Week 2 Monday Contrast Example Could Be More Concrete

**Location:** Lines 403-407 (Week 2, Monday: "The Vague vs. Rich Experiment")

**Problem:** The "rich context" example is generic:

```markdown
**Step 2:** Ask AI with RICH context:
"I'm a Form 6 leaver considering [specific university/program]. I'm stressed about [specific concern]. Help me understand [specific question]."
```

**Evidence:**
- Template is abstract with bracketed placeholders
- Could include a fully fleshed-out example
- Would make the contrast more obvious

**Impact:** LOW - Example works but could be stronger

**Fix Required:** Add a concrete example:
```markdown
**Example of rich context:**
"I'm a Form 6 leaver considering computer science at UoN vs. Strathmore. I'm stressed about the costs - my family can afford about KES 400k/year. I want to know which program has better job prospects in AI/ML in Kenya."
```

---

### Issue #8: Agent Response Template Could Be More Comprehensive

**Location:** Lines 1097-1176 (Agent Response Templates)

**Problem:** The Python pseudocode is helpful but incomplete:
- Missing scenarios for stuck students
- Missing escalation logic
- Missing habit reinforcement beyond emoji reactions
- No template for Friday reflections

**Evidence:**
- Document says "Agent response templates" but only provides pseudocode
- Trevor's 10% role isn't clearly integrated
- No escalation triggers defined (e.g., student stuck 3+ days)

**Impact:** LOW-MEDIUM - Makes implementation harder for Discord agent setup

**Fix Required:** Expand templates:
- Add escalation scenarios
- Add habit reinforcement scripts
- Add Friday reflection processing template
- Connect to Trevor's 10% interventions

---

## LOW ISSUES (Optional)

### Issue #9: Emotional Job Touchpoints Could Be More Explicit

**Location:** Throughout prompts

**Problem:** While prompts serve the emotional jobs (belonging, confidence, companionship, ownership, pride), the emotional touchpoints aren't always explicit.

**Evidence:**
- Week 1: "You might be wondering: 'Is this really for someone like me?'" - Good
- Other weeks: Emotional jobs are implicit but not explicitly named

**Impact:** LOW - Prompts work but could be more emotionally resonant

**Fix Required:** Add explicit emotional validation (optional enhancement):
- Week 2-3: "You might be feeling: 'Can I actually do this?'"
- Weeks 4-5: "You might be feeling: 'I'm not alone in this.'"
- Weeks 6-7: "You might be feeling: 'I have standards now.'"

---

## Compliance Summary

### Guardrails Compliance

| Guardrail | Status | Notes |
|-----------|--------|-------|
| #1: No Technical Jargon | ✅ PASS | No jargon detected |
| #2: No "Impressive" AI Outputs | ✅ PASS | No impressive demos |
| #3: No Student Comparison | ✅ PASS | Aggregate anonymized only |
| #4: Celebrate Thinking, Not Outputs | ✅ PASS | Focus on process |
| #5: Normalize Confusion/Mistakes | ✅ PASS | Multiple error-friendly prompts |
| #11: JTBD-Relevant Examples | ❌ FAIL | **CRITICAL** - See Issue #1 |

### Architecture Compliance

| Requirement | Status | Notes |
|-------------|--------|-------|
| Node Architecture Connection | ✅ PASS | Nodes referenced correctly |
| 4 Habits Branding | ✅ PASS | All habits reinforced |
| CIS Agent Integration | ✅ PASS | Graduated introduction maintained |
| Emotional Jobs | ✅ PASS | Served across weeks |
| Brand Voice (Revolutionary Hope) | ✅ PASS | Tone consistent |

---

## Recommendations

### Must Fix (Before Production):
1. **Replace Week 1 Wednesday prohibited examples** (Issue #1) - CRITICAL
2. **Clarify prompt count requirements** (Issue #2) - Update acceptance criteria
3. **Strengthen Week 4 CIS introduction scaffolding** (Issue #6) - Reduce cognitive load

### Should Fix (Before Production):
4. **Clarify Week 5 artifact preview timing** (Issue #5) - Reduce confusion
5. **Expand agent response templates** (Issue #8) - Aid implementation

### Nice to Have:
6. **Add concrete contrast example** (Issue #7) - Improve learning
7. **Make emotional jobs more explicit** (Issue #9) - Enhance resonance

---

## Final Verdict

**Status:** ❌ **NEEDS CRITICAL FIXES**

**Blockers:**
- Issue #1 (Guardrail #11 violation) - CANNOT PROCEED

**Recommended Action:**
1. Call party mode with CIS agents to discuss fixes
2. Apply all CRITICAL and HIGH priority fixes
3. Re-review after fixes applied
4. Update sprint status

**Estimated Fix Time:** 30-45 minutes

---

**Next Step:** Party mode discussion with CIS agents to agree on fix approach.
