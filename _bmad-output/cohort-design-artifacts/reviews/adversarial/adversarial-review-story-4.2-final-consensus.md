# Adversarial Review: Story 4.2 - Final Consensus & Fix Implementation

**Review Date:** 2026-01-25
**Party Mode Team:** Winston, Victor, Maya, Amelia, John, Barry
**Status:** FIXES APPROVED → IMPLEMENTATION IN PROGRESS

---

## TEAM CONSENSUS

**Winston (Architect):** Architecture debt must be fixed now. StudentContext integration + SafetyFilter are non-negotiable.

**Victor (Strategy):** Issue #3 (altitude) is strategic, not just technical. Wrong altitude = failed JTBD emotional job.

**Maya (Design):** Emotional scaffold must be invisible infrastructure (Level 1), not explicit formulas (Level 3). Zone 0 students need empathy, not frameworks.

**Amelia (Dev):** 2-3 hour implementation for HIGH priority. Controller pre-processes StudentContext, Framer stays stateless.

**John (PM):** Acceptance criteria gap identified. Need AC #8: Integration Architecture Document.

**Barry (Ship-It):** Fix HIGH priority (#1, #2, #3) to ship. MEDIUM priority (#4, #5, #6) improves quality—apply all if time permits.

**DECISION:** Apply all 6 fixes (HIGH + MEDIUM) for complete Story 4.2.

---

## FIX IMPLEMENTATION PLAN

### HIGH PRIORITY FIXES (Architecture - Must Ship)

#### FIX #1: StudentContext Integration

**Problem:** Lines 414-447 duplicate Story 4.1's example library. Framer reinvents logic that exists in StudentContext.

**Solution:**
1. **DELETE:** Lines 414-447 (hardcoded JTBD example library)
2. **ADD:** New section "StudentContext Integration" documenting:
   - Controller calls `student_context.get_relevant_example("frame")`
   - Example injected into Framer system prompt as variable
   - Framer references injected example, doesn't maintain its own library
3. **UPDATE:** System prompt to reference `{relevant_example}` variable
4. **ADD:** Integration point documentation showing data flow

**Code Changes:**
```python
# DELETE (Story 4.2 lines 414-447)
EXAMPLES = {
    "university": [...],
    "homework": [...]
}

# REPLACE WITH (Controller integration)
# Controller layer (Story 4.1):
relevant_example = student_context.get_relevant_example("frame")
framer_prompt = FRAMER_SYSTEM_PROMPT.format(relevant_example=relevant_example)

# Framer system prompt:
"When suggesting framing patterns, use this example: {relevant_example}"
```

---

#### FIX #2: SafetyFilter Integration

**Problem:** No validation that Framer outputs are comparison-free. Guardrail #3 violation risk.

**Solution:**
1. **ADD:** Section "SafetyFilter Integration" documenting:
   - All Framer responses pass through `SafetyFilter.validate_no_comparison()`
   - Controller uses `post_to_discord_safe()` wrapper from Story 4.1
   - Comparison violations halt execution and alert Trevor
2. **ADD:** Test case: `test_framer_output_passes_safety_filter()`

**Integration Flow:**
```python
# Controller flow (Story 4.1 integration):
framer_response = generate_framer_response(student_context, user_message)
await post_to_discord_safe(channel, framer_response)  # SafetyFilter runs here
```

---

#### FIX #3: Integration Architecture Documentation

**Problem:** Story 4.2 doesn't specify HOW Framer integrates with Controller. Implementation blocker.

**Solution:**
1. **ADD:** New section "Integration Architecture" with:
   - API signature: `generate_framer_response(student_context: StudentContext, user_message: str) -> str`
   - Data flow diagram: Controller → StudentContext load → Framer → SafetyFilter → Discord
   - State update flow: Framer response → Controller updates `habit_journey[1].practiced_count`
2. **ADD:** New Acceptance Criteria #8: "Integration Architecture Document"

**Architecture Diagram:**
```
┌─────────────────────────────────────────────┐
│  CONTROLLER (Story 4.1)                    │
├─────────────────────────────────────────────┤
│ 1. Load StudentContext from database       │
│ 2. Get relevant example:                   │
│    example = student_context.get_relevant_ │
│              example("frame")               │
│ 3. Get altitude template:                  │
│    template = get_suggestion_template(     │
│              student_context, "frame")      │
│ 4. Call Framer:                             │
│    response = generate_framer_response(    │
│              student_context, message)      │
│ 5. Validate safety:                         │
│    SafetyFilter.validate_no_comparison()   │
│ 6. Post to Discord:                         │
│    await post_to_discord_safe(response)    │
│ 7. Update state:                            │
│    student_context.habit_journey[1].       │
│    practiced_count += 1                     │
│    student_context.celebrate_habit(1)      │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  FRAMER AGENT (Story 4.2)                  │
├─────────────────────────────────────────────┤
│ Input:                                      │
│ - student_context: StudentContext          │
│ - user_message: str                         │
│                                             │
│ Processing:                                 │
│ - Apply system prompt                       │
│ - Use conversation patterns                 │
│ - Reference {relevant_example}              │
│ - Generate empathetic response              │
│                                             │
│ Output:                                     │
│ - response: str (framed question)           │
└─────────────────────────────────────────────┘
```

---

### MEDIUM PRIORITY FIXES (Quality - Ship for Completeness)

#### FIX #4: Altitude-Aware Templates (Maya's Empathy-First Approach)

**Problem:** Some templates jump to Level 3 (framework language) instead of staying Level 1-2 (empathy/concrete).

**Victor's Insight:** "If altitude is wrong, we're not serving the JTBD emotional job."

**Maya's Fix:** "Emotional scaffold must be invisible infrastructure, not explicit formulas."

**Solution:**
1. **UPDATE:** Conversation Pattern #1 (lines 237-241) to remove framework language
2. **REPLACE:** "[Context] + [What You Want] + [Specific Question]" with empathetic mirroring
3. **ADD:** Week-based altitude progression (Week 1 = Level 1 only)

**Before (Level 3 - Framework):**
```markdown
**Framer:** "Try framing it like this: 'My situation is [describe]. I want to [goal]. Can you help me [specific ask]?'"
```

**After (Level 1 - Empathy):**
```markdown
**Week 1 (Level 1 - Empathy):**
**Framer:** "Let me help you get clearer. Tell me: what's your situation with this? And what would help you most right now?"

**Week 2 (Level 1-2 - Pattern):**
**Framer:** "I notice when you explain your situation first, AI understands better. Want to try that?"

**Week 3+ (Level 2-3 - Framework):**
**Framer:** "Here's a structure that works: [Your situation] + [What you want] + [Specific ask]"
```

**Altitude Mapping:**
- Week 1: Level 1 only (concrete, empathetic, "I feel this")
- Week 2-3: Level 1-2 (observable patterns, "The habits you form follow you")
- Week 4+: Level 2-3 okay (framework language acceptable after trust built)

---

#### FIX #5: Milestone-Aware Habit Celebrations

**Problem:** Generic celebrations ("Great pause!") don't leverage Story 4.1's HabitProgress milestone tracking.

**Solution:**
1. **REPLACE:** Lines 512-526 (hardcoded celebration templates) with StudentContext method call
2. **ADD:** Documentation that Controller calls `student_context.celebrate_habit(1)` for dynamic celebrations
3. **UPDATE:** System prompt to reference milestone-aware celebrations

**Before (Generic):**
```markdown
"Great framing! Notice how you paused to think about what you actually want? That's Habit 1 building."
```

**After (Milestone-Aware):**
```python
# Controller calls:
celebration = student_context.celebrate_habit(1)  # Habit 1 (Pause)

# Returns (1st time):
"⏸️ **PAUSE - FIRST TIME!**\n\nYou just practiced Pause. This is how habits start."

# Returns (10th time):
"⏸️ **PAUSE #10!**\n\nDouble digits! This habit is taking root. Keep going."

# Returns (every 10th):
"⏸️ **PAUSE #20!**\n\nReal progress. You're building skills that follow you to university."
```

**Integration:**
- Controller tracks `student_context.habit_journey[1].practiced_count`
- After Framer response, Controller generates milestone celebration
- Celebration appended to Framer response before posting to Discord

---

#### FIX #6: Example Library Deduplication

**Problem:** Story 4.2 maintains separate 20-example library. Story 4.1 has 50+ examples. Two sources of truth.

**Solution:**
1. **DELETE:** Lines 414-447 (Story 4.2's example library)
2. **REFERENCE:** Story 4.1's `student_context_library/examples.py`
3. **UPDATE:** All documentation to reference single source of truth
4. **ADD:** Note that Controller injects examples from StudentContext library

**Before:**
```markdown
## JTBD Example Library (Pre-University Audience)

**Category 1: University & Career (10 Examples)**
1. "I'm trying to decide between computer science and data science..."
[Lines 414-447]
```

**After:**
```markdown
## JTBD Example Integration

The Framer does NOT maintain its own example library. Instead:

1. **Controller calls:** `student_context.get_relevant_example("frame")`
2. **Example selection logic:** Story 4.1 `student_context_library/examples.py`
   - Matches student's JTBD concern (university, career, homework, anxiety, etc.)
   - Matches student's zone (Zone 0-1 for Framer context)
   - 50+ examples organized by concern × zone × agent
3. **Injection:** Controller injects selected example into Framer system prompt
4. **Reference:** `{relevant_example}` variable in system prompt

**Single Source of Truth:** `_bmad-output/cohort-design-artifacts/playbook-v2/04-cis-agents/4-1-cis-controller-logic.md` lines 1018-1213
```

---

## IMPLEMENTATION CHECKLIST

### HIGH Priority (Architecture - Must Complete)

- [ ] **FIX #1:** Delete lines 414-447, add StudentContext integration section
- [ ] **FIX #2:** Add SafetyFilter integration section, document `post_to_discord_safe()` usage
- [ ] **FIX #3:** Add Integration Architecture section with API signature + data flow diagram
- [ ] **NEW AC #8:** Add "Integration Architecture Document specifying Framer/Controller integration"
- [ ] **Test:** Add `test_framer_uses_student_context_examples()`
- [ ] **Test:** Add `test_framer_output_passes_safety_filter()`

### MEDIUM Priority (Quality - Complete for Excellence)

- [ ] **FIX #4:** Update conversation patterns to use altitude-appropriate language (Level 1 for Week 1)
- [ ] **FIX #4:** Add week-based altitude progression (Week 1 = empathy, Week 3+ = framework)
- [ ] **FIX #5:** Replace hardcoded celebrations with `student_context.celebrate_habit(1)` integration
- [ ] **FIX #5:** Document Controller appends milestone celebrations to Framer responses
- [ ] **FIX #6:** Delete duplicate example library, reference Story 4.1's single source
- [ ] **FIX #6:** Update all example references to point to StudentContext library
- [ ] **Test:** Add `test_framer_celebrates_habit_milestones()`

### Documentation Updates

- [ ] Update Story 4.2 Dev Notes with integration architecture
- [ ] Update Acceptance Criteria section with AC #8
- [ ] Update References section to cite Story 4.1 integration points
- [ ] Update File List with integration architecture documentation

---

## VALIDATION CRITERIA

**Story 4.2 is COMPLETE when:**

1. ✅ All 11 guardrails enforced (UNCHANGED - already compliant)
2. ✅ JTBD integration clear (UNCHANGED - already compliant)
3. ✅ 4 Habits branding visible (UNCHANGED - already compliant)
4. ✅ **NEW:** StudentContext integration documented with API signatures
5. ✅ **NEW:** SafetyFilter integration documented with validation flow
6. ✅ **NEW:** Integration Architecture section complete with data flow
7. ✅ **NEW:** Altitude-appropriate templates (Level 1 for Week 1, progressive elevation)
8. ✅ **NEW:** Milestone-aware habit celebrations documented
9. ✅ **NEW:** Single example library (Story 4.1 reference, no duplication)
10. ✅ **NEW:** Integration tests validate Framer/Controller interaction

---

## ESTIMATED EFFORT

**HIGH Priority Fixes:**
- FIX #1 (StudentContext): 45 minutes (delete + document integration)
- FIX #2 (SafetyFilter): 30 minutes (document validation flow)
- FIX #3 (Integration Architecture): 60 minutes (API signatures + data flow diagram)
- **HIGH Total:** 2 hours 15 minutes

**MEDIUM Priority Fixes:**
- FIX #4 (Altitude templates): 30 minutes (rewrite conversation patterns)
- FIX #5 (Milestone celebrations): 20 minutes (document integration)
- FIX #6 (Example deduplication): 15 minutes (delete + reference Story 4.1)
- **MEDIUM Total:** 1 hour 5 minutes

**Testing:**
- Integration tests: 30 minutes
- Validation review: 15 minutes
- **Testing Total:** 45 minutes

**GRAND TOTAL:** 4 hours

---

## NEXT ACTIONS

1. ✅ **COMPLETE:** Adversarial review findings documented
2. ✅ **COMPLETE:** Party mode consensus reached
3. 🔄 **IN PROGRESS:** Apply all fixes to Story 4.2
4. ⏳ **PENDING:** Update sprint-status.yaml (Story 4.2 → COMPLETE)
5. ⏳ **PENDING:** Update sprint-progress-summary with Story 4.2 completion
6. ⏳ **PENDING:** Commit changes with adversarial review summary
7. ⏳ **PENDING:** Mark Story 4.2 validated and ready for Story 4.3

---

**Team Sign-Off:**

- 🏗️ **Winston (Architect):** Architecture fixes approved. Boring technology, done right.
- ⚡ **Victor (Strategy):** JTBD altitude fixes approved. Strategic alignment achieved.
- 🎨 **Maya (Design):** Empathy-first approach approved. Emotional scaffold invisible.
- 💻 **Amelia (Developer):** Implementation plan approved. Stateless Framer, Controller pre-processes.
- 📋 **John (PM):** User value validated. AC #8 added for integration architecture.
- 🚀 **Barry (Ship-It):** All fixes ship-worthy. 4-hour implementation realistic.

---

**Status:** READY FOR IMPLEMENTATION ✅

*Consensus reached: 2026-01-25*
*Implementation: Winston (Architect) applying fixes*
