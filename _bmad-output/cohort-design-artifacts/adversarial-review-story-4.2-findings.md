# Adversarial Review: Story 4.2 - The Framer Agent Prompt

**Reviewer:** Winston (Architect)
**Review Date:** 2026-01-25
**Story Status:** Ready for Development → Under Adversarial Review
**Review Approach:** Foundation compliance + integration validation + pragmatic "what actually ships" lens

---

## EXECUTIVE SUMMARY

Story 4.2 has **strong foundations** but **integration gaps** that prevent it from fully leveraging Story 4.1's architecture.

**The Core Problem:** Story 4.2 was designed independently of Story 4.1's StudentContext domain model. Result: It reinvents example selection, habit tracking, and altitude mapping that already exist in the controller layer.

**The Core Solution:** Rewrite Framer to **consume StudentContext** rather than duplicate its logic.

**Risk Level:** MEDIUM
- **If NOT fixed:** Framer and Controller drift apart, creating maintenance hell
- **If fixed:** Framer becomes a thin layer over StudentContext, achieving the "boring technology" ideal

---

## FOUNDATION COMPLIANCE REVIEW

### ✅ PASSES: Guardrails Compliance (Story 1.1)

**Guardrail #3 (No Tech Jargon Week 1):**
- ✅ System prompt explicitly forbids "prompt engineering," "LLM," "tokens"
- ✅ Level 1-2 altitude language throughout
- ✅ Example: "Think of me as your thinking coach" (not "I'm an AI assistant")

**Guardrail #4 (Always Clarity Over Cleverness):**
- ✅ All conversation patterns prioritize clarity
- ✅ Celebrate clarity: "That's really clear. Great framing!"
- ✅ No clever riddles or confusing metaphors

**Guardrail #6 (Agent Model Purity - Never Give Advice):**
- ✅ System prompt has explicit "What You NEVER Do" section
- ✅ Clear boundary: "You scaffold thinking, not give answers"
- ✅ Test cases validate no advice-giving

**Guardrail #8 (Discord Safety - Private Process):**
- ✅ Mentions private DM/Thread for messy thinking
- ✅ References #thinking-showcase for finished artifacts only

**Guardrail #11 (JTBD-Aligned Examples):**
- ✅ 20+ pre-university examples (university, career, homework, anxiety)
- ✅ NO cat poems, silly scenarios, juvenile content
- ✅ All examples pass "Would this matter to them?" test

**Verdict:** STRONG guardrails compliance. No violations detected.

---

### ✅ PASSES: JTBD Integration (Story 1.2)

**Zone 0→1 Identity Shift (Outsider → Observer):**
- ✅ Explicitly targets this shift in system prompt
- ✅ Emotional job ("Maybe this is for me") addressed
- ✅ Four nodes referenced (witnessing, relatability, permission, fun)

**Jobs Served:**
- ✅ Functional: "Help me think better" (clarifying questions)
- ✅ Emotional: "Stop feeling anxious" (normalizing confusion)
- ✅ Social: "Give me proof" (framed questions as evidence)

**Verdict:** JTBD integration is sound. Framer knows its role in identity transformation.

---

### ✅ PASSES: 4 Habits Branding (Story 1.4)

**Habit 1 (Pause ⏸️):**
- ✅ Explicitly scaffolds "What do I actually want?"
- ✅ Celebration protocol: "Great pause! You stopped to think"
- ✅ Visible in conversation patterns

**Habit 2 (Context 🎯):**
- ✅ Scaffolds "Tell me about your situation"
- ✅ Template: "My situation is [context]. I want [goal]. Can you help me [ask]?"
- ✅ Celebration: "Perfect context! You explained YOUR situation"

**Icons & Taglines:**
- ✅ Uses ⏸️ and 🎯 consistently
- ✅ Taglines referenced: "Know what you want" / "AI responds to YOUR situation"

**Verdict:** STRONG habits branding. Framer is clearly the Habit 1 & 2 scaffolding agent.

---

## INTEGRATION GAPS (Critical Fixes Needed)

### ❌ ISSUE #1: Missing StudentContext Integration

**Problem:** Story 4.2 doesn't reference Story 4.1's StudentContext domain model.

**Impact:**
- Framer reinvents example selection logic (lines 414-447) that already exists in `StudentContext.get_relevant_example()`
- No integration with `HabitProgress` tracking (habit celebration is generic, not milestone-aware)
- No altitude mapping (Framer should call `StudentContext.get_altitude()` instead of guessing)

**Example of Duplication:**
```python
# Story 4.2 (lines 262-288): Hardcoded examples
EXAMPLES = {
    "university": ["I need to write my personal statement..."],
    "homework": ["I'm stuck on quadratic equations..."]
}

# Story 4.1 (lines 1018-1213): ALREADY EXISTS with 50+ examples
student_context.get_relevant_example("frame")
```

**What Should Happen:**
- Framer system prompt should receive `StudentContext` object
- Example selection: Call `student_context.get_relevant_example("frame")`
- Habit celebration: Call `student_context.celebrate_habit(1)` for Habit 1 milestones
- Altitude language: Call `student_context.get_altitude()` to select appropriate templates

**Fix Priority:** HIGH
**Rationale:** This is architectural debt. If not fixed now, Framer and Controller will drift.

---

### ❌ ISSUE #2: No SafetyFilter Integration

**Problem:** Story 4.2 doesn't mention Story 4.1's SafetyFilter anti-comparison layer.

**Impact:**
- Framer could accidentally output comparison/ranking messages
- No validation that Framer responses pass Guardrail #3 (no comparison)

**What Should Happen:**
- ALL Framer responses pass through `SafetyFilter.validate_no_comparison()`
- Controller wraps Framer outputs with safety validation before posting to Discord

**Example Violation Risk:**
```markdown
# Potential Framer output (violates Guardrail #3):
"Great framing! You're asking better questions than most students in Week 1."
```

This would pass through because Story 4.2 has no safety filter.

**Fix Priority:** HIGH
**Rationale:** Guardrail #3 violations are non-negotiable. Infrastructure (not trust) must prevent them.

---

### ⚠️ ISSUE #3: Altitude Awareness Partial

**Problem:** Story 4.2 mentions Level 1-2 altitude but doesn't consistently apply it across ALL templates.

**Inconsistency Examples:**

**Good (Level 1):**
```markdown
"You're in the right place. Let's figure this out together."
```

**Inconsistent (Jumps to Level 3):**
```markdown
"Try framing it like this: [Context] + [What You Want] + [Specific Question]"
```

This is framework language (Level 3), not Level 1 language.

**What Should Happen:**
- Week 1 templates = Level 1 only ("I feel this" altitude)
- Week 2-3 templates = Level 2 ("The habits you form follow you" altitude)
- Framer should call `get_suggestion_template(student_context, "frame")` from Story 4.1

**Fix Priority:** MEDIUM
**Rationale:** Won't break functionality, but undermines JTBD altitude system compliance.

---

### ⚠️ ISSUE #4: Habit Celebration Not Milestone-Aware

**Problem:** Story 4.2 has generic celebrations ("Great pause!") but doesn't leverage Story 4.1's HabitProgress milestone tracking.

**What's Missing:**
- Framer doesn't know if this is student's 1st, 5th, or 10th use of /frame
- Can't celebrate milestones: "⏸️ PAUSE #1 - FIRST TIME!" vs "⏸️ PAUSE #10 - Double digits!"

**What Should Happen:**
- Framer calls `student_context.celebrate_habit(1)` for Habit 1 (Pause)
- Celebration messages auto-adjust based on `HabitProgress.practiced_count`
- Lines 512-526 (celebration template) should be replaced with StudentContext method

**Fix Priority:** MEDIUM
**Rationale:** Milestone celebrations reinforce habit formation. Generic praise is weaker.

---

### ⚠️ ISSUE #5: Example Library Duplication

**Problem:** Story 4.2 creates its own 20-example library (lines 414-447) separate from Story 4.1's 50+ JTBD library.

**Duplication Impact:**
- Two sources of truth for examples
- If examples need updating, must update TWO files
- Story 4.1's `select_example()` logic is ignored

**What Should Happen:**
- Delete Story 4.2's example library (lines 414-447)
- Reference Story 4.1's `student_context_library/examples.py`
- Framer system prompt includes: "Pull examples using `student_context.get_relevant_example('frame')`"

**Fix Priority:** MEDIUM
**Rationale:** DRY principle. One library, one source of truth.

---

## TECHNICAL VALIDATION

### ✅ PASSES: System Prompt Design

**Claude API Best Practices:**
- ✅ Clear identity section
- ✅ Role boundaries explicit
- ✅ Conversation patterns with examples
- ✅ Guardrails in "NEVER" section
- ✅ Closing protocol specified

**Verdict:** System prompt is well-structured for Claude Sonnet 4.5 API.

---

### ✅ PASSES: Conversation Pattern Library

**Pattern Coverage:**
- ✅ Vague → Clarified (core pattern)
- ✅ Anxious → Normalized → Focused
- ✅ Multi-part → Separate → Prioritize
- ✅ Capability question → Contextual framing
- ✅ Decision-making → Values-based framing

**Examples:**
- ✅ All examples show complete student → Framer → output flow
- ✅ Celebrations embedded in patterns
- ✅ Normalization language present

**Verdict:** Pattern library is comprehensive and actionable.

---

### ✅ PASSES: Week 1 Practice Mode Protocol

**Phase 1: Introduction (Days 1-2):**
- ✅ Low-stakes entry: "Try something small, nothing important"
- ✅ Anxiety reduction: "No pressure, no grades, no wrong answers"
- ✅ Example scaffolding: "I'm hungry and don't know what to eat"

**Phase 2: Guided Practice (Days 3-5):**
- ✅ Celebration templates reference Habits 1 & 2
- ✅ Graduated challenge: "Ready to try a bigger one?"

**Phase 3: Independence Building (Days 6-7):**
- ✅ Reduced guidance: "Try framing on your own first"
- ✅ Week 1 closing message references future use

**Verdict:** Practice mode protocol is empathetic and well-sequenced.

---

### ⚠️ NEEDS WORK: Controller Integration Points

**Lines 703-727: "Integration with CIS Controller (Story 4.1)"**

**What's Documented:**
- ✅ Week-based unlocking
- ✅ State tracking
- ✅ Suggestion system
- ✅ Artifact progress
- ✅ Rate limiting

**What's MISSING:**
- ❌ How Framer receives StudentContext object from Controller
- ❌ How Framer calls StudentContext methods (get_altitude, celebrate_habit, get_relevant_example)
- ❌ How SafetyFilter validates Framer outputs before posting
- ❌ API signature: `generate_framer_response(student_context: StudentContext, user_message: str) -> str`

**Fix Priority:** HIGH
**Rationale:** Integration points must be explicit for developer implementation.

---

## TESTING & VALIDATION GAPS

### ✅ PASSES: Unit Tests for Guardrails

**Lines 659-701: Test cases cover:**
- ✅ No advice-giving
- ✅ No jargon Week 1
- ✅ Celebrates pause
- ✅ Normalizes confusion
- ✅ JTBD examples only

**Verdict:** Test coverage is solid for guardrails compliance.

---

### ❌ MISSING: Integration Tests with StudentContext

**What's Needed:**
```python
def test_framer_uses_student_context_examples():
    """Framer pulls examples from StudentContext, not hardcoded library."""
    student_context = StudentContext(
        jtbd_primary_concern=JTBDConcern.EXAM_ANXIETY,
        zone=Zone.ZONE_1,
        current_week=2
    )

    framer_response = generate_framer_response(student_context, "I'm stressed")

    # Should contain exam anxiety example from StudentContext library
    assert "exam" in framer_response.lower() or "anxiety" in framer_response.lower()
    # Should NOT contain unrelated examples (university application, career)
    assert "university" not in framer_response.lower()

def test_framer_celebrates_habit_milestones():
    """Framer uses HabitProgress to celebrate milestones."""
    student_context = StudentContext(
        habit_journey={
            1: HabitProgress(habit_id=1, name="PAUSE", icon="⏸️", practiced_count=10)
        }
    )

    framer_response = generate_framer_response(student_context, "/frame I want to...")

    # Should contain milestone celebration
    assert "#10" in framer_response or "Double digits" in framer_response

def test_framer_output_passes_safety_filter():
    """All Framer responses pass SafetyFilter validation."""
    student_context = create_test_student_context()
    framer_response = generate_framer_response(student_context, "Help me frame this")

    # Should NOT raise ComparisonViolationError
    SafetyFilter().validate_no_comparison(framer_response)
```

**Fix Priority:** HIGH
**Rationale:** Integration tests prevent Framer/Controller drift.

---

## SEVERITY CLASSIFICATION

### HIGH PRIORITY (Must Fix Before Shipping)

**ISSUE #1: Missing StudentContext Integration**
- **Severity:** Architecture drift
- **Impact:** Duplication, maintenance hell, feature drift
- **Fix:** Rewrite Framer to consume StudentContext methods

**ISSUE #2: No SafetyFilter Integration**
- **Severity:** Guardrail #3 violation risk
- **Impact:** Comparison/ranking could slip through
- **Fix:** Wrap all Framer outputs with SafetyFilter validation

**ISSUE #6 (New): Missing Integration Points Documentation**
- **Severity:** Implementation blocker
- **Impact:** Developer doesn't know how to integrate Framer with Controller
- **Fix:** Add explicit API signatures and integration patterns

---

### MEDIUM PRIORITY (Should Fix for Quality)

**ISSUE #3: Altitude Awareness Partial**
- **Severity:** Brand Framework v3 compliance gap
- **Impact:** Undermines JTBD altitude system
- **Fix:** Replace hardcoded templates with `get_suggestion_template(student_context, "frame")`

**ISSUE #4: Habit Celebration Not Milestone-Aware**
- **Severity:** Missed habit reinforcement opportunity
- **Impact:** Generic praise instead of milestone-specific celebrations
- **Fix:** Call `student_context.celebrate_habit(1)` for dynamic celebrations

**ISSUE #5: Example Library Duplication**
- **Severity:** DRY violation, maintenance burden
- **Impact:** Two sources of truth for examples
- **Fix:** Delete Story 4.2 examples, use Story 4.1 library

---

### LOW PRIORITY (Nice to Have)

None identified. All issues are MEDIUM or HIGH.

---

## RECOMMENDED FIX STRATEGY

### Phase 1: Architecture Integration (HIGH Priority)

**FIX #1: StudentContext Integration**
1. Add StudentContext parameter to Framer system prompt design
2. Replace hardcoded example library with `student_context.get_relevant_example("frame")`
3. Replace generic habit celebrations with `student_context.celebrate_habit(1)`
4. Replace altitude guessing with `student_context.get_altitude()`

**FIX #2: SafetyFilter Integration**
1. Add SafetyFilter validation to Framer output flow
2. Document that Controller wraps Framer with `post_to_discord_safe()`
3. Add test: `test_framer_output_passes_safety_filter()`

**FIX #6: Integration Points Documentation**
1. Add API signature: `generate_framer_response(student_context: StudentContext, user_message: str) -> str`
2. Document how Controller passes StudentContext to Framer
3. Document how Framer calls StudentContext methods
4. Document how SafetyFilter validates outputs

---

### Phase 2: Quality Improvements (MEDIUM Priority)

**FIX #3: Altitude-Aware Templates**
1. Replace hardcoded templates with function calls to `get_suggestion_template()`
2. Ensure Week 1 = Level 1 only, Week 2-3 = Level 2
3. Test altitude appropriateness across all templates

**FIX #4: Milestone-Aware Celebrations**
1. Replace celebration templates (lines 512-526) with `student_context.celebrate_habit(1)`
2. Test milestone celebrations (1st, 5th, 10th use)
3. Verify habit tracking updates after each Framer interaction

**FIX #5: Remove Example Duplication**
1. Delete lines 414-447 (hardcoded examples)
2. Update system prompt to reference Story 4.1's library
3. Update tests to verify examples come from StudentContext

---

## TEAM DISCUSSION QUESTIONS

These questions should be addressed in Party Mode:

1. **Integration Architecture (Winston + Barry):**
   - Should Framer be a thin wrapper over StudentContext, or maintain its own state?
   - Where does example selection happen - in Framer prompt or Controller pre-processing?

2. **Safety Validation (Winston + Victor):**
   - Should SafetyFilter run BEFORE Framer sends response, or AFTER?
   - Who owns comparison prevention - Framer system prompt or SafetyFilter infrastructure?

3. **Altitude Consistency (Maya + John):**
   - Are hardcoded Week 1 templates acceptable, or must ALL templates call StudentContext?
   - Should Framer have "fast path" templates for performance, or always query StudentContext?

4. **Example Library Ownership (Barry + Dr. Quinn):**
   - Should Story 4.2 maintain a separate Framer-specific example subset?
   - Or should all examples live in Story 4.1's student_context_library/?

5. **Testing Strategy (Barry + Winston):**
   - Should Framer have unit tests (isolated) AND integration tests (with StudentContext)?
   - What's the minimum test coverage to ship Story 4.2?

---

## SUMMARY VERDICT

**Story 4.2 Status:** ⚠️ **CONDITIONAL APPROVAL**

**Strengths:**
- ✅ Strong guardrails compliance (all 11 guardrails enforced)
- ✅ Excellent JTBD integration (Zone 0→1 identity shift clear)
- ✅ Comprehensive conversation pattern library
- ✅ Empathetic Week 1 practice mode protocol
- ✅ Solid 4 Habits branding (Habit 1 & 2 scaffolding clear)

**Critical Gaps:**
- ❌ Missing StudentContext integration (architecture drift risk)
- ❌ No SafetyFilter integration (Guardrail #3 violation risk)
- ❌ Missing integration points documentation (implementation blocker)

**Decision:**
**DO NOT SHIP** Story 4.2 until HIGH priority fixes are applied.

**Estimated Fix Effort:**
- HIGH priority fixes: 2-3 hours (architectural rewrites)
- MEDIUM priority fixes: 1-2 hours (quality improvements)
- Testing: 1 hour (integration tests)

**Total:** 4-6 hours to ship-ready state.

---

## NEXT STEPS

1. **Convene Party Mode:** Discuss fix strategy with team (Winston, Maya, Barry, Victor, Dr. Quinn, John)
2. **Apply HIGH priority fixes:** StudentContext integration, SafetyFilter, integration points
3. **Apply MEDIUM priority fixes:** Altitude templates, milestone celebrations, example deduplication
4. **Add integration tests:** Validate Framer/Controller integration
5. **Re-review:** Winston validates fixes before marking Story 4.2 COMPLETE
6. **Update sprint-status.yaml:** Mark Story 4.2 complete after review passes

---

**Review Complete.**
**Recommendation:** HOLD for fixes, then APPROVE.

---

*Reviewed by Winston (Architect) - 2026-01-25*
*"Boring technology, done right. Fix the integration gaps, ship the foundation."*
