# Adversarial Review: Story 4.7 - Discord Bot Technical Specification

**Reviewed:** 2026-01-25
**Reviewer:** Winston (Architect) - Adversarial Mode
**Story:** 4.7 - Create Discord Bot Technical Specification
**Status:** READY-FOR-DEV → REQUIRES FIXES

---

## Executive Summary

**Overall Assessment:** Story 4.7 is a STRONG foundation with 75% of requirements met, but has CRITICAL gaps that prevent production readiness.

**Verdict:** ❌ **NOT READY FOR DEVELOPMENT** - Requires fixes to HIGH priority issues before developers can implement.

**Score:** 18/24 Acceptance Criteria fully met (75%)

---

## Critical Findings Summary

| Priority | Count | Status |
|----------|-------|--------|
| **HIGH** | 5 | Blockers to production readiness |
| **MEDIUM** | 8 | Important for quality and completeness |
| **LOW** | 3 | Nice-to-have improvements |

---

## HIGH Priority Issues (Blockers)

### HIGH-1: Missing Three CIS Agent System Prompts (AC3 Partial)
**Location:** Lines 726-849
**Issue:** Only Framer agent has complete system prompt. Explorer, Challenger, Synthesizer are referenced but not fully specified.

**Impact:** Developer cannot implement three of four CIS agents without referring to separate story files. Creates dependency risk.

**Evidence:**
```python
# Line 730-792: Complete FRAMER_SYSTEM_PROMPT provided ✅

# Line 793+: Missing:
# - EXPLORER_SYSTEM_PROMPT
# - CHALLENGER_SYSTEM_PROMPT
# - SYNTHESIZER_SYSTEM_PROMPT
```

**Acceptance Criteria Impact:**
- AC3: "Four CIS Agent Integration Specifications" - PARTIAL (1/4 complete)

**Required Fix:**
- Extract complete system prompts from Stories 4.3, 4.4, 4.5
- Include all four prompts in agents/ directory with `get_system_prompt()` functions
- Ensure each prompt includes: Identity, Purpose, Patterns, Safety rules, Templates

---

### HIGH-2: Guardrail Coverage Incomplete (Guardrails #4, #7, #9 Missing)
**Location:** Lines 124-151 (Dev Notes)
**Issue:** Only Guardrails #3, #6, #8, #10, #11 mentioned. Missing critical guardrails.

**Missing Guardrails:**
- **Guardrail #4:** "AI is a thinking tool, not a thinking solution"
- **Guardrail #7:** "Never use comparison, even implicitly"
- **Guardrail #9:** "Student examples must be JTBD-matched"

**Impact:** Bot implementation may violate framework purity, creating facilitator drift risk.

**Evidence:**
```yaml
# Line 127-132: Only 5 of 11 guardrails referenced
Guardrails mentioned: #3, #6, #8, #10, #11
Guardrails missing: #1, #2, #4, #5, #7, #9
```

**Required Fix:**
1. Add guardrail compliance matrix showing how bot enforces all 11 guardrails
2. Update SafetyFilter to include Guardrails #4, #7, #9 validation
3. Add `validate_framework_purity()` function to check Guardrail #4 violations

---

### HIGH-3: Node Architecture Integration Missing (Epic 1, Story 1.3)
**Location:** Line 141-143 (mentioned but not implemented)
**Issue:** Nodes mentioned as foundation requirement but no integration in bot architecture.

**Impact:** CIS agents won't reinforce nodes through conversation, missing key learning mechanism.

**Evidence:**
```yaml
# Line 141-143:
"3. Node Architecture (Story 1.3):
- 16 nodes across 4 zone transitions
- CIS agents reinforce nodes through conversation
- Artifact creation proves node completion"
```

**But nowhere in bot specification:**
- How do agents know which node a student is working on?
- Where is node progress tracked in StudentContext?
- How are nodes reinforced in agent responses?

**Required Fix:**
1. Add `current_node` field to StudentContext (e.g., "node_1_3" = Zone 0→1, Node 3)
2. Add node completion tracking to habit_practice table
3. Specify node reinforcement patterns in each agent's system prompt
4. Add `get_node_example()` function to StudentContext helpers

---

### HIGH-4: Cost Analysis Lacks Per-Agent Breakdown (Decision 3 Risk)
**Location:** Lines 1519-1522
**Issue:** Total cost provided ($5-33/week) but no per-agent cost distribution.

**Impact:** Cannot validate if 90/10 hybrid model (Decision 2) is achievable within budget.

**Evidence:**
```yaml
# Line 1519-1522:
"Budget: $100/week conservative, actual $5-33 with prompt caching"
```

**Missing:**
- How many interactions per agent per week?
- What's average cost per /frame vs /synthesize?
- How does prompt caching affect each agent differently?

**Required Fix:**
1. Add cost model table:
   ```
   Agent      | Interactions/Week | Avg Cost/Interaction | Weekly Cost
   /frame     | 200              | $0.02               | $4.00
   /diverge   | 50               | $0.03               | $1.50
   /challenge | 50               | $0.03               | $1.50
   /synthesize| 30               | $0.05               | $1.50
   Total                                                 $8.50
   ```
2. Show calculation with/without prompt caching
3. Validate against Decision 2's 2 hours/week Trevor time target

---

### HIGH-5: Error Handling Strategy Incomplete (Lines 594-607)
**Location:** cis_controller/llm_integration.py
**Issue:** Generic exception handling, no student-facing graceful degradation.

**Impact:** API failures leave students stranded with technical error messages.

**Evidence:**
```python
# Line 594-607:
except Exception as e:
    print(f"ERROR calling {agent} agent: {str(e)}")
    await notify_trevor(f"🚨 CIS Agent Error: {agent} failed")
    raise  # Student sees Discord bot error
```

**Missing:**
- What does student see when Claude API is down?
- Is there offline fallback (e.g., "Practice Habit 1 on your own: Ask yourself 'What do I actually want?'")?
- How do we retry failed requests?

**Required Fix:**
1. Add `student_facing_error_message()` function for each agent
2. Implement exponential backoff retry logic (3 attempts)
3. Cache common responses for offline mode
4. Add monitoring dashboard for error rate tracking

---

## MEDIUM Priority Issues (Quality)

### MEDIUM-1: Story 4.6 Integration Path Unclear (AC4)
**Location:** Lines 851-1006
**Issue:** Artifact creation flow references Story 4.6 but doesn't show how to import/use it.

**Evidence:**
```python
# Line 862:
"Entry point for artifact creation flow (Week 6+ only).
Story 4.6 specification implementation."
```

**Missing:** How does developer integrate Story 4.6's artifact flow into this bot?

**Required Fix:**
- Add import statement: `from artifact_flow import create_artifact_workflow`
- Show how Story 4.6's 6-section map to this command handler
- Cross-reference section to Story 4.6 line numbers

---

### MEDIUM-2: JTBD Emotional State Not Utilized in Responses (Epic 1, Story 1.2)
**Location:** database/models.py (line 1256)
**Issue:** StudentContext has `emotional_state` field but agents don't use it.

**Impact:** Missed opportunity for empathetic, emotionally-aware responses.

**Evidence:**
```python
# Line 1256:
emotional_state: str  # "anxious", "curious", "confident", "stuck", "excited"

# But not used in any agent prompt or response logic
```

**Required Fix:**
- Add emotional state awareness to agent system prompts
- Example: "If student is 'anxious', prioritize normalization: 'Many students feel this way'"
- Add `get_empathy_template(emotional_state)` helper

---

### MEDIUM-3: Natural Language Fallback Underspecified (Lines 431-432)
**Location:** cis_controller/router.py
**Issue:** `suggest_explicit_command()` mentioned but not implemented.

**Impact:** Students who type natural language instead of commands get no helpful guidance.

**Evidence:**
```python
# Line 431-432:
await suggest_explicit_command(message, student)
# Function never defined in spec
```

**Required Fix:**
1. Implement `suggest_explicit_command()` function
2. Use lightweight LLM call (Haiku) for intent classification
3. Return: "Did you mean /frame [your question]?"

---

### MEDIUM-4: Week-Based Agent Unlocking Lacks "Why" Explanation (Line 467-491)
**Location:** cis_controller/router.py
**Issue:** Lockout message explains sequence but doesn't connect to identity transformation.

**Impact:** Students see restrictions as arbitrary rules rather than pedagogical scaffolding.

**Evidence:**
```python
# Line 487-491:
"Each agent builds on the 4 Habits you're learning.
The {agent.capitalize()} will make more sense after practicing the earlier ones."
```

**Missing:** Connection to JTBD identity shifts (outsider → observer → experimenter → collaborator → director)

**Required Fix:**
- Update lockout message to include identity shift context
- Example: "/synthesize unlocks Week 6 because you'll have practiced Habits 1-3 and be ready to direct your own thinking (Zone 3→4: collaborator → director)"

---

### MEDIUM-5: Database Migration Strategy Missing (AC6, Task 4.4)
**Location:** Lines 1104-1333 (database schema)
**Issue:** SQLite → PostgreSQL migration mentioned but no execution plan.

**Impact:** Cohort 2 scaling will be chaotic.

**Required Fix:**
1. Add migration script example:
   ```bash
   # Export SQLite to SQL
   sqlite3 cohort1.db .dump > cohort1.sql
   # Import to PostgreSQL
   psql cohort2_db < cohort1.sql
   ```
2. Document schema changes needed for PostgreSQL (indexes, foreign keys)
3. Specify migration timing (e.g., "When students > 300")

---

### MEDIUM-6: SafetyFilter Aggregate Validation Weak (Lines 680-698)
**Location:** cis_controller/safety_filter.py
**Issue:** Only checks "names + action verbs", missing implicit comparison patterns.

**Impact:** Guardrail #7 violations can slip through.

**Evidence:**
```python
# Line 692-697:
if any(keyword in message_text.lower() for keyword in ["practiced", "completed", "used"]):
    raise ComparisonViolationError(...)
```

**Missing Patterns:**
- "Three students shared..." (implies ranking)
- "Congratulations to our most active..." (superlative = comparison)
- "Special shoutout to..." (implicit ranking)

**Required Fix:**
- Add regex patterns for superlatives: "most", "-est" endings
- Add pattern for "congratulations to [name]" without broader context

---

### MEDIUM-7: 4 Habits Celebration Not Fully Specified (Lines 830-843)
**Location:** commands/frame.py
**Issue:** `celebrate_habit()` function called but not defined.

**Impact:** Inconsistent habit reinforcement across agents.

**Required Fix:**
1. Define `celebrate_habit(student, habit_id)` function
2. Specify celebration messages:
   ```
   Habit 1 (5th practice): "You've paused before asking 5 times! That's Habit 1 becoming automatic. ⏸️"
   Habit 2 (10th practice): "You've explained your context 10 times. AI now responds to YOUR situation. 🎯"
   Habit 3 (15th practice): "You've iterated 15 times. You're thinking in 'change one thing' mode. 🔄"
   Habit 4 (20th practice): "You've used AI before decisions 20 times. You're thinking first. 🧠"
   ```
3. Add habit milestone tracking to state machine

---

### MEDIUM-8: Monitoring Dashboard Not Visualized (AC8, Task 8.3)
**Location:** Lines 1400-1443
**Issue:** Monitoring code exists but no dashboard mockup or UI spec.

**Impact:** Trevor has no clear view of cohort health.

**Required Fix:**
1. Add dashboard mockup (ASCII art or description):
   ```
   K2M CIS Bot Dashboard - Week 3
   ┌────────────────────────────────────┐
   │ Students Active: 187/200           │
   │ /frame Usage: 342 interactions     │
   │ API Cost Today: $6.23 / $10 alert  │
   │ Errors: 2 (API timeout)            │
   │ Habit 1 Practice: 156 students     │
   │ Habit 2 Practice: 89 students      │
   └────────────────────────────────────┘
   ```
2. Specify update frequency (real-time vs hourly)
3. Define alert thresholds

---

## LOW Priority Issues (Nice-to-Have)

### LOW-1: Testing Section Light on Edge Cases (Lines 1445-1482)
**Issue:** Only 2 test examples provided. Missing edge cases.

**Suggested Additions:**
- Student reaches daily interaction limit
- Claude API rate limit exceeded
- Database connection fails mid-conversation
- Student tries to access locked agent (Week 1 tries /synthesize)

---

### LOW-2: Deployment Process Assumes Railway (Lines 1371-1398)
**Issue:** No alternative deployment options (Heroku, AWS, self-hosted).

**Impact:** Trevor locked into Railway if changes needed.

**Suggested Addition:**
- Add Heroku deployment alternative
- Add Docker container for self-hosting

---

### LOW-3: Example Selector Function Referenced But Not Defined (Line 1283-1289)
**Location:** database/models.py
**Issue:** `select_example()` function called but implementation missing.

**Evidence:**
```python
# Line 1283-1289:
from cis_controller.examples import select_example
return select_example(
    concern=self.jtbd_primary_concern,
    zone=self.zone,
    agent=agent,
    week=self.current_week
)
```

**Required Fix:**
- Define `select_example()` function
- Show example library structure (JSON file vs database)
- Provide 3 example outputs per concern/zone/agent combination

---

## Acceptance Criteria Status Matrix

| AC | Description | Status | Issues |
|----|-------------|--------|--------|
| **AC1** | Complete Discord Bot Architecture Document | ✅ PASS | Complete system architecture |
| **AC2** | CIS Controller Implementation Specification | ✅ PASS | Full 3-layer design with code examples |
| **AC3** | Four CIS Agent Integration Specifications | ⚠️ PARTIAL | Only Framer complete (HIGH-1) |
| **AC4** | Artifact Creation Flow Implementation | ⚠️ PASS* | Flow complete, integration unclear (MEDIUM-1) |
| **AC5** | Discord Server Channel Architecture | ✅ PASS | Full channel spec with permissions |
| **AC6** | StudentContext & Database Schema | ⚠️ PASS* | Schema complete, migration missing (MEDIUM-5) |
| **AC7** | SafetyFilter Implementation Specification | ⚠️ PARTIAL | Baseline complete, gaps in validation (MEDIUM-6, HIGH-2) |
| **AC8** | Deployment & Operations Guide | ⚠️ PARTIAL | Deployment complete, monitoring weak (MEDIUM-8) |

**Overall:** 5/8 FULL PASS, 3/8 PARTIAL PASS

---

## Foundation Compliance Check

### Epic 1 Foundations (Stories 1.1-1.4)

| Foundation | Status | Gap |
|------------|--------|-----|
| **Guardrails (Story 1.1)** | ⚠️ PARTIAL | Missing #4, #7, #9 (HIGH-2) |
| **JTBD Integration (Story 1.2)** | ⚠️ PARTIAL | Identity shifts mentioned but not used (MEDIUM-2, MEDIUM-4) |
| **Node Architecture (Story 1.3)** | ❌ MISSING | No node tracking or reinforcement (HIGH-3) |
| **4 Habits Branding (Story 1.4)** | ⚠️ PARTIAL | Habits tracked, celebrations incomplete (MEDIUM-7) |

### Epic 4 Integration (Stories 4.1-4.6)

| Story | Integration Status | Notes |
|-------|-------------------|-------|
| **4.1 (Controller)** | ✅ STRONG | Router, state machine, LLM integration fully integrated |
| **4.2 (Framer)** | ✅ COMPLETE | Full system prompt + handler |
| **4.3 (Explorer)** | ⚠️ REFERENCE ONLY | System prompt not extracted (HIGH-1) |
| **4.4 (Challenger)** | ⚠️ REFERENCE ONLY | System prompt not extracted (HIGH-1) |
| **4.5 (Synthesizer)** | ⚠️ REFERENCE ONLY | System prompt not extracted (HIGH-1) |
| **4.6 (Artifact)** | ⚠️ INTEGRATED | Flow implemented, import path unclear (MEDIUM-1) |

---

## Positive Findings (What's Working Well)

1. ✅ **Strong System Architecture:** 3-layer design (Intent → State → Agent) is solid and scalable
2. ✅ **Comprehensive Code Examples:** router.py, llm_integration.py, safety_filter.py provide complete implementation starting point
3. ✅ **Database Schema Well-Designed:** StudentContext, habit_practice, artifact_progress tables cover all requirements
4. ✅ **Cost Awareness:** Prompt caching strategy and budget controls show operational maturity
5. ✅ **Temporal Awareness:** Week-based agent unlocking (Decision 11) properly implemented
6. ✅ **Guardrail #3 Compliance:** SafetyFilter provides strong anti-comparison infrastructure
7. ✅ **Async/Await Patterns:** Proper concurrent operation handling for 100+ students

---

## Recommended Fix Priority Order

**Phase 1: Critical Blockers (Must Fix Before Dev)**
1. HIGH-1: Extract three missing CIS agent system prompts (Stories 4.3, 4.4, 4.5)
2. HIGH-2: Add missing guardrails compliance (#4, #7, #9)
3. HIGH-3: Integrate node architecture tracking and reinforcement

**Phase 2: Important Quality (Should Fix Before Epic 5)**
4. HIGH-4: Add per-agent cost breakdown
5. HIGH-5: Improve error handling with student-facing messages
6. MEDIUM-1: Clarify Story 4.6 integration path
7. MEDIUM-2: Utilize JTBD emotional state in agent responses

**Phase 3: Nice-to-Have (Can Fix During Dev)**
8. All remaining MEDIUM issues
9. All LOW issues

---

## Final Verdict

**Story 4.7 is 75% complete and has strong foundations, but requires fixes to 5 HIGH priority issues before being ready for development.**

**Recommended Action:**
1. Call party mode with CIS suite agents to validate findings
2. Apply Phase 1 fixes (HIGH-1, HIGH-2, HIGH-3)
3. Re-review to validate fixes
4. Mark Story 4.7 as "ready-for-dev" only after all HIGH fixes applied

---

**Next Review:** After party mode consensus and fix application
**Estimated Fix Time:** 2-3 hours for Phase 1 fixes
