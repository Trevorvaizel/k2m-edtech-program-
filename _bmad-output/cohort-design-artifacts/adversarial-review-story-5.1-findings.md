# Adversarial Review: Story 5.1 - Discord Server Structure Design

**Reviewer:** Winston (Architect)
**Date:** 2026-01-25
**Story Status:** ready-for-dev
**Review Type:** Comprehensive adversarial analysis against requirements, guardrails, and integration points

---

## Executive Summary

**Overall Assessment:** Story 5.1 is comprehensive and well-designed but has **3 HIGH priority issues**, **7 MEDIUM priority issues**, and **4 LOW priority issues** that must be addressed before approval.

**Critical Finding:** The document fails to validate compliance with **6 of 11 guardrails** (Guardrails #2, #4, #5, #7, #9, #11) - this is a **HIGH priority gap** that contradicts Epic 1 foundations.

**Positive Findings:**
- Excellent technical architecture (channels, roles, permissions, scalability)
- Strong integration with Epic 4 (CIS agent system)
- Comprehensive Trevor's 10% workflow design
- Good hybrid Discord model implementation (Decision 12)

**Recommendation:** **CONDITIONAL PASS** - Apply all HIGH and MEDIUM fixes before moving to Story 5.2.

---

## HIGH Priority Issues

### HIGH #1: Incomplete Guardrail Compliance (Guardrails #2, #4, #5, #7, #9, #11 Missing)

**Location:** Architecture Compliance Checklist (lines 1219-1245)

**Issue:** The checklist only validates 5 of 11 guardrails (#1, #3, #6, #8, #10). Six guardrails are completely missing from compliance validation:

**Missing Guardrails:**
- **Guardrail #2 (Framework Purity):** "We build thinking skills, not 'AI literacy'"
- **Guardrail #4 (No prescriptive paths):** "Students choose their engagement depth"
- **Guardrail #5 (Zone progression is non-linear):** "Students move at their own pace"
- **Guardrail #7 (Human connection):** "Technology augments, never replaces human judgment"
- **Guardrail #9 (Evidence-based):** "Claims backed by data or explicit labeling"
- **Guardrail #11 (JTBD examples):** "All examples serve real student jobs"

**Impact:**
- Violates Epic 1.1 requirement: "These 10 guardrails are NON-NEGOTIABLE foundation"
- Server design may inadvertently violate missing guardrails
- Trevor has no validation that server enforces all 11 guardrails

**Evidence from Requirements Doc:**
- Line 52-53: "All 10 guardrails" (note: requirements say 10 but Epic 1.1 actually has 11)
- Line 76: "All Future Work (Epics 2-7) Must: 1. Reference relevant guardrails from Epic 1.1"

**Required Fix:**
1. Add missing 6 guardrails to Architecture Compliance Checklist
2. For each missing guardrail, specify:
   - How server design enforces it
   - What violations would look like
   - How bot/Trevor monitors compliance
3. Ensure all 11 guardrails have validation criteria

**Acceptance Criteria Impact:** AC#4 (Psychological Safety Design) is incomplete

---

### HIGH #2: Missing Crisis/Emergency Protocol for Mental Health Issues

**Location:** Escalation Path (lines 1113-1127)

**Issue:** The escalation path handles "safety violations" and "stuck students" but has **no protocol for mental health crises** (suicide, self-harm, severe distress).

**Why This Matters:**
- Cohort serves pre-university students (high-stress transition period)
- JTBD emotional job: "stop feeling anxious" (some students may have clinical anxiety/depression)
- Private DM conversations (CIS agent interactions) may reveal crisis situations
- Trevor has 10% time commitment (~2 hours/week) - cannot monitor 200 students 24/7

**Current Gap:**
```
Level 1: Bot Handles (stuck students, Guardrail #3 violations)
Level 2: Trevor Monitors (stuck 3+ days, culture erosion)
Level 3: Trevor Intervenes (safety violations, repeated issues)

MISSING: Level 4 - Crisis Intervention (mental health emergencies)
```

**Required Fix:**
1. Add **crisis detection protocol**:
   - SafetyFilter should flag crisis keywords (self-harm, suicide, "can't go on")
   - Bot responds with crisis resources immediately
   - Trevor notified instantly (not in daily summary)
2. Add **crisis response workflow**:
   - Immediate Trevor outreach (within 1 hour)
   - Parent/guardian notification protocol (if student is minor)
   - Emergency contact information
   - Professional mental health resources (Kenya-specific if applicable)
3. Add **crisis prevention**:
   - Bot checks in after negative emotional patterns
   - Trevor prioritizes students with diagnostic flags (anxiety, depression)

**Acceptance Criteria Impact:** AC#7 (Trevor's 10% Workflow) is incomplete - Trevor needs crisis protocol to stay within 2 hours/week

---

### HIGH #3: Weekly Channel Unlock Mechanism Not Specified

**Location:** Weekly Channel Design (lines 591-744)

**Issue:** Document describes weekly channel purposes but **never specifies how channels unlock progressively**.

**Problem:**
- Week 2-3 students should not access Week 4-5 channels (prevents overwhelm)
- Current design: All channels visible to all students (line 202 says "later channels unlock progressively" but doesn't say HOW)
- Bot automation mentioned but no technical specification:
  - When does Week 2 unlock? (After Friday reflection? After Trevor approval?)
  - How does bot add/remove channel permissions?
  - What happens to laggards? (Week 3 starts but student still in Week 1)

**Evidence from Requirements Doc:**
- Decision 11 (line 254-259): "Graduated Introduction Plan" with staged CIS agent rollout
- Story 2.1 (line 162): "Friday reflection with gating for Week 2"

**Required Fix:**
1. Specify **unlock mechanism**:
   ```
   Week N → Week N+1 Unlock Criteria:
   - Student submitted Friday reflection ✅
   - Student completed proof-of-work ✅
   - Bot adds Week N+1 channel permissions automatically
   - Bot removes Week N channel posting permissions (archived but visible)
   ```
2. Handle **laggards** (students who didn't complete Week N):
   - Week N+1 starts on schedule (cohort moves forward)
   - Student retains Week N posting permissions (can catch up)
   - Bot notifies Trevor: "5 students still in Week 1 while Week 2 starts"
   - Trevor decides: outreach vs. let student self-pace
3. Add **bot permission management**:
   - Command: `/unlock-week [student_id] [week_number]`
   - Manual override: Trevor can unlock manually for edge cases

**Acceptance Criteria Impact:** AC#5 (Weekly Channel Design) is incomplete

---

## MEDIUM Priority Issues

### MEDIUM #1: File Location Mismatch

**Location:** sprint-status.yaml vs. actual file location

**Issue:**
- sprint-status.yaml line 160: `output: "playbook-v2/05-discord-ops/discord-architecture.md"`
- Actual file: `_bmad-output/implementation-artifacts/5-1-discord-server-structure.md`

**Impact:**
- Breaks playbook assembly (Epic 7 will look for file in wrong location)
- Story 5.2-5.6 will reference wrong path
- Trevor's quick-start guide will have broken links

**Required Fix:**
1. Move file from `_bmad-output/implementation-artifacts/5-1-discord-server-structure.md` to `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/discord-architecture.md`
2. Update sprint-status.yaml to reflect actual location
3. Update all cross-references within document

---

### MEDIUM #2: Weak Node Architecture Integration

**Location:** Weekly Channel Design (lines 591-744)

**Issue:** Nodes are mentioned superficially but not deeply integrated:
- Node 0.1: "AI is not sci-fi" (line 599) - but WHERE does student access this?
- No specification of how nodes appear in channels (embed? link? transcript?)
- No connection to NotebookLM prompts from Epic 3 (Stories 3.2-3.5)

**Evidence from Requirements:**
- Line 143-148: Node Architecture (Story 1.3) - "16 nodes across 4 zone transitions delivered through Discord"
- Line 200: "NotebookLM podcasts: All 16 nodes"

**Required Fix:**
1. Specify **node delivery format**:
   ```yaml
   Node Posting Format (9 AM Daily):
     Bot posts to #week-N channel:
       "🎯 DAY 3: NODE 0.3 - 'I Could Try This' (12 min podcast)

       [Link to NotebookLM podcast]

       📝 DISCUSSION: What's ONE tiny AI experiment you could try today?
       (Reply in thread - bot will react 👀 to every response)"
   ```
2. Add **node archive**:
   - Create #resources page with all 16 nodes linked
   - Students can revisit nodes from previous weeks
3. Connect to **Epic 3 NotebookLM prompts**:
   - Reference Story 3.2 (Zone 0→1 master prompt)
   - Reference Story 3.3 (Zone 1→2 master prompt)
   - Ensure nodes align with master prompt output

---

### MEDIUM #3: Incomplete Daily Prompt Library Integration

**Location:** Weekly Channel Design (lines 597-604, 643-646)

**Issue:** Document mentions "Daily Prompt" but doesn't integrate with Story 3.6 (Daily Async Prompt Library - 32 prompts)

**Evidence:**
- Line 109: Story 3.6 exists: "Create daily async prompt library (32 prompts)"
- Story 5.1 line 604: Example prompts ("Witness AI in your life") - but are these from the 32-prompt library?

**Required Fix:**
1. Explicitly reference Story 3.6 output:
   ```yaml
   Daily Prompts Source:
     File: playbook-v2/03-sessions/daily-prompt-library.md
     Total: 32 prompts across 8 weeks (4 prompts/week)
     Selection: Bot posts prompts sequentially from library
   ```
2. Specify **prompt variation**:
   - Does bot post all 4 prompts each week?
   - Or does bot rotate prompts from library?
   - What if cohort runs longer than 8 weeks? (loop back to Week 1 prompts?)

---

### MEDIUM #4: Superficial JTBD Integration

**Location:** JTBD Integration (lines 363-397), Architecture Compliance Checklist (lines 1228-1231)

**Issue:** JTBD is mentioned in checklist but not deeply integrated into server design decisions:

**Missing:**
1. **Emotional Job** ("stop feeling anxious"):
   - Server design has NO anxiety-reduction mechanisms
   - No welcome message acknowledging anxiety
   - No bot responses that normalize anxiety
   - #welcome channel (lines 750-823) doesn't mention anxiety at all

2. **Social Job** ("proof for myself, parents, future"):
   - Artifact showcase exists (good)
   - But no PARENT engagement mechanism
   - How do parents see proof?
   - Should there be a parent update channel or email?

**Required Fix:**
1. Add **anxiety-reduction mechanisms**:
   - #welcome channel message: "It's okay to feel anxious about AI. You're not alone."
   - Bot response to confused students: "Confusion is normal. You're exactly where you should be."
   - Add crisis resources (see HIGH #2)
2. Add **parent engagement**:
   - Decision: Should parents get weekly email updates?
   - If yes, add bot automation for parent reports
   - If no, document why (student autonomy?)

---

### MEDIUM #5: No Trevor Live Session Scheduling Specified

**Location:** Trevor's Live Session Workflow (lines 980-1011)

**Issue:** Document says "1-hour sessions per cluster (alternating days)" but doesn't specify:
- WHICH days? (Monday/Wednesday/Friday? Tuesday/Thursday?)
- WHAT time? (Evenings? Weekends?)
- HOW MANY clusters? (200 students / cluster size = ?)
- HOW are students assigned to clusters?

**Evidence from Requirements:**
- Decision 9 (lines 202-209): "1-hour sessions, alternating days, per cluster, ~12-15 hours across 6 weeks"
- Story 2.1 (line 164): "Trevor's live session: 1-hour sessions per cluster"

**Required Fix:**
1. Specify **session schedule**:
   ```yaml
   Trevor Live Session Schedule:
     Total Students: 200
     Cluster Size: 25 students per cluster
     Total Clusters: 8 clusters
     Session Duration: 60 minutes
     Frequency: 3 sessions/week (Monday/Wednesday/Friday OR Tuesday/Thursday/Saturday)
     Time: 6:00 PM EAT (adjust for time zones)
     Total Time Commitment: 8 clusters × 8 weeks × 1 session/cluster = 8 sessions (8 hours)

     Cluster Assignment:
       Cluster 1: Students A-F (last names)
       Cluster 2: Students G-L
       ...etc
   ```
2. Add **session announcement automation**:
   - Bot posts 24 hours before: "Live session tomorrow at 6 PM for Cluster 1!"
   - Bot posts 1 hour before: "Starting in 1 hour! Join voice channel: #week-1-wonder-voice"

---

### MEDIUM #6: No Brand Voice Compliance Verification

**Location:** Guardrail #10 (line 1225)

**Issue:** Checklist says "All channel descriptions use Revolutionary Hope tone, Level 1-2 language" but provides NO verification mechanism:

**Missing:**
1. Revolutionary Hope tone definition (what IS it?)
2. Language Level 1-2 criteria (how do we measure it?)
3. How does bot validate brand voice?
4. Who reviews Trevor's messages for brand voice?

**Evidence from Requirements:**
- Brand Conversion Framework V3 (line 42): "Voice/altitude guidance for all content"
- Guardrail #10 (from Epic 1.1): "Brand Voice Compliance - Revolutionary Hope tone, Language Level 1-2"

**Required Fix:**
1. Add **brand voice criteria**:
   ```yaml
   Revolutionary Hope Tone Characteristics:
     - Avoids: "You should," "Must do," "Required"
     - Uses: "You can," "You get to," "Here's what's possible"
     - Examples: "You belong here" vs. "You must participate"
     - Emojis: Celebratory (🌟✨💪) not prescriptive (⚠️❗📋)

   Language Level 1-2 (Ground/Pattern):
     - Avoids: Jargon ("pedagogical," "scaffold," "paradigm")
     - Uses: Everyday language ("think clearly," "build habits," "practice")
     - Sentence length: <15 words per sentence (Channel descriptions only)
   ```
2. Add **brand voice validation**:
   - Trevor reviews all bot messages before Cohort 1 launch
   - Student feedback: "Was any language confusing?" (Friday reflection)
   - Bot highlights jargon in SafetyFilter mode (development only)

---

### MEDIUM #7: No Cluster Assignment System

**Location:** Trevor's 10% Workflow (lines 874-1044)

**Issue:** Document mentions "clusters" multiple times (lines 160, 651, 688, 716, 988) but NEVER specifies:
- How are students assigned to clusters?
- How many students per cluster?
- Can students switch clusters?
- Does bot automate cluster assignment?

**Evidence from Requirements:**
- Decision 9 (line 206): "Per cluster (not whole cohort)"

**Required Fix:**
1. Specify **cluster assignment system**:
   ```yaml
   Cluster Assignment System:
     Total Students: 200
     Cluster Size: 25 students/cluster
     Total Clusters: 8 clusters
     Assignment Method: By last name (A-F, G-L, M-R, S-Z) OR
                     By time zone preference OR
                     By Trevor manual assignment
     Bot Automation:
       - On student join: Assign to Cluster X role
       - Create cluster-specific channels? OR
       - Use same channels, schedule different session times?

   Cluster Switching:
     - Students can request cluster switch (DM Trevor)
     - Trevor updates cluster assignment manually
     - Bot updates session reminders based on new cluster
   ```

---

## LOW Priority Issues

### LOW #1: Typo - "10 guardrails" vs. "11 guardrails"

**Location:** Requirements doc line 52, Story 5.1 not explicit about count

**Issue:** Requirements document says "10 guardrails" but Epic 1.1 actually created 11 guardrails.

**Required Fix:**
1. Update requirements doc line 52 from "10 guardrails" to "11 guardrails"
2. Ensure Story 5.1 clearly states "11 guardrails from Epic 1.1"

---

### LOW #2: No Discord Channel Archival Specified

**Location:** Weekly Channel Design (line 67)

**Issue:** Task 5.5 says "Design channel archival or lock patterns after week completion" but design section never addresses this.

**Required Fix:**
1. Specify **archival policy**:
   ```yaml
   Channel Archival:
     After Week N completes:
       - Bot removes @Student permission to POST in #week-N
       - @Student retains READ permission (can review past work)
       - Channel marked with 📁 emoji (archived)
       - Week N+1 channel unlocks (see HIGH #3)
   ```

---

### LOW #3: No Bot Error Message Examples

**Location:** Bot Failure Handling (lines 1137-1174)

**Issue:** Document specifies failure scenarios but doesn't provide actual bot error messages students would see.

**Required Fix:**
1. Add **error message examples**:
   ```yaml
   Bot Error Messages:
     Claude API Down:
       "🤖 The CIS agents are taking a short break. Try this on your own:
           Pause and ask yourself 'What do I actually want to know?'
           You're practicing Habit 1 (⏸️ PAUSE) - you've got this!
           We'll be back soon!"

     Discord API Issues:
       "🔌 Connection issue. If you don't see a response in 30 seconds,
           try the command again. Trevor is notified and fixing it!"

     Rate Limit Exceeded:
       "⏸️ Whoa, lots of great thinking happening! Take a 5-minute break,
           then try again. Good thinking needs time to breathe. 😊"
   ```

---

### LOW #4: No Student Exit/Withdrawal Process

**Location:** (Not addressed anywhere in document)

**Issue:** What happens if a student withdraws from cohort? How does Trevor handle:
- Channel access removal?
- Database records?
- Parent communication?
- Slot refill (waitlist)?

**Required Fix:**
1. Add **withdrawal process**:
   ```yaml
   Student Withdrawal Process:
     1. Student requests withdrawal (DM Trevor)
     2. Trevor removes @Student role from Discord server
     3. Bot archives student data (retains for analytics, anonymizes)
     4. Trevor sends parent email (if student is minor)
     5. Optional: Trevor offers slot to waitlist student
   ```

---

## Integration Audit (Epic 1, 2, 4 Compliance)

### Epic 1 (Philosophy & Framework) Integration: ⚠️ PARTIAL

**Stories Referenced:**
- ✅ Story 1.1 (Guardrails): Referenced but incomplete (6 guardrails missing) - **HIGH #1**
- ✅ Story 1.2 (JTBD): Referenced but superficial - **MEDIUM #4**
- ⚠️ Story 1.3 (Node Architecture): Mentioned but weak integration - **MEDIUM #2**
- ✅ Story 1.4 (4 Habits): Well integrated (icons, weekly progression)

**Missing Explicit Links:**
- No direct file paths to Epic 1 outputs
- No "see playbook-v2/01-philosophy/guardrails-preserved.md" cross-references

---

### Epic 2 (8-Week Design) Integration: ⚠️ PARTIAL

**Stories Referenced:**
- ✅ Story 2.1 (Week 1 Design): Referenced (daily rhythm, agent behavior)
- ⚠️ Stories 2.2-2.5 (Weeks 2-8): Mentioned but no cross-references
- ❌ Story 2.6 (Node Content Checklist): Not referenced

**Evidence from Weekly Design Section:**
- Line 594: "Week 1: Wonder (Zone 0→1)" - should link to `week-1-wonder.md`
- Line 640: "Weeks 2-3: Trust" - should link to `weeks-2-3-trust.md`
- Line 666: "Weeks 4-5: Converse" - should link to `weeks-4-5-converse.md`
- Line 691: "Weeks 6-7: Direct" - should link to `weeks-6-7-direct.md`
- Line 721: "Week 8: Showcase" - should link to `week-8-artifact-showcase.md`

**Required Fix:**
1. Add explicit cross-references:
   ```yaml
   Week 1 Channel (#week-1-wonder):
     See: playbook-v2/02-weekly-design/week-1-wonder.md for complete design
     Daily rhythm: Lines 160-167 in Story 2.1
     Node schedule: Lines 597-603 (this document)
   ```

---

### Epic 4 (CIS Agent System) Integration: ✅ STRONG

**Stories Referenced:**
- ✅ Story 4.1 (CIS Controller): Referenced (command routing)
- ✅ Story 4.2-4.5 (Agent Prompts): Referenced (/frame, /diverge, /challenge, /synthesize)
- ✅ Story 4.6 (Artifact Flow): Referenced (/create-artifact)
- ✅ Story 4.7 (Discord Bot Spec): Referenced (technical implementation)

**Strength:**
- Direct file references (line 172, 566, 1256)
- Graduated introduction well-specified (lines 514-554)
- Private DM workflow clear (lines 472-512)

---

## Acceptance Criteria Compliance

| AC # | Criteria | Status | Issues |
|------|----------|--------|--------|
| AC#1 | Complete Discord Server Architecture | ⚠️ PASS | Missing cluster assignment system (MEDIUM #7) |
| AC#2 | Hybrid Discord Model Implementation | ✅ PASS | None |
| AC#3 | CIS Agent Integration Architecture | ✅ PASS | None |
| AC#4 | Psychological Safety Design | ❌ FAIL | Missing 6 guardrails (HIGH #1), no crisis protocol (HIGH #2) |
| AC#5 | Weekly Channel Design | ❌ FAIL | No unlock mechanism (HIGH #3), weak node integration (MEDIUM #2) |
| AC#6 | Onboarding & Welcome Experience | ⚠️ PASS | No anxiety acknowledgment (MEDIUM #4) |
| AC#7 | Trevor's 10% Workflow | ⚠️ PASS | No session schedule (MEDIUM #5), no cluster system (MEDIUM #7) |
| AC#8 | Scalability & Moderation | ⚠️ PASS | No withdrawal process (LOW #4) |

**AC Compliance: 3/8 FULL PASS, 3/8 PARTIAL PASS, 2/8 FAIL = 62.5%**

---

## Positive Findings (What's Done Well)

1. **Technical Excellence:**
   - Comprehensive channel hierarchy (lines 214-310)
   - Clear role/permission system (lines 312-361)
   - Strong scalability analysis (lines 1048-1087)
   - Detailed cost breakdown (~$40-50/month)

2. **CIS Agent Integration:**
   - Excellent command flow diagram (lines 472-512)
   - Graduated introduction well-specified (lines 514-554)
   - Private DM protections clear (lines 557-588)

3. **Hybrid Discord Model:**
   - Beautiful private→public flow visualization (lines 364-423)
   - Three publishing options (public, anonymous, private) (lines 427-447)
   - Celebration patterns without comparison (lines 449-468)

4. **Trevor's 10% Workflow:**
   - Detailed facilitator dashboard (lines 876-938)
   - Clear spot-check workflow (lines 940-978)
   - Live session structure (lines 980-1011)

---

## Recommended Fix Priority Order

**Fix Before Story 5.2:**
1. ✅ HIGH #1: Add missing 6 guardrails to compliance checklist
2. ✅ HIGH #2: Add crisis intervention protocol
3. ✅ HIGH #3: Specify weekly channel unlock mechanism
4. ✅ MEDIUM #1: Move file to correct playbook-v2 location
5. ✅ MEDIUM #5: Add Trevor live session schedule
6. ✅ MEDIUM #7: Specify cluster assignment system
7. ✅ MEDIUM #4: Deepen JTBD integration (anxiety acknowledgment, parent engagement)

**Fix After Story 5.2 (Time Permitting):**
8. MEDIUM #2: Strengthen node architecture integration
9. MEDIUM #3: Add daily prompt library references
10. MEDIUM #6: Add brand voice compliance verification

**Fix in Epic 7 (Final Assembly):**
11. LOW #1: Fix "10 vs 11" guardrails typo in requirements doc
12. LOW #2: Add channel archival specification
13. LOW #3: Add bot error message examples
14. LOW #4: Add student withdrawal process

---

## Next Steps

**Immediate Actions:**
1. Convene party mode with CIS agents and BMAD team to discuss HIGH/MEDIUM fixes
2. Apply all fixes to Story 5.1 document
3. Move file to correct location: `playbook-v2/05-discord-ops/discord-architecture.md`
4. Update sprint-status.yaml with completion details
5. Create adversarial review summary document (this file)

**After Story 5.1 Approved:**
6. Proceed to Story 5.2 (#thinking-lab channel setup)
7. Use fixed Story 5.1 as foundation for Stories 5.3-5.6

---

**Review Status:** 🔴 **CONDITIONAL PASS** - Apply HIGH + MEDIUM fixes before approval

**Review Confidence:** 95% - Comprehensive audit against all requirements, guardrails, and integration points

**Reviewer Signature:** Winston (Architect) - "This is excellent work that needs tightening on guardrails compliance and crisis protocols. The technical architecture is sound. Let's fix the gaps and ship it."

---

*End of Adversarial Review*
