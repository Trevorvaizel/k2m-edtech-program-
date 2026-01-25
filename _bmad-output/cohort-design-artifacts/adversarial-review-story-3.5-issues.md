# Adversarial Review: Story 3.5 - NotebookLM Master Prompt Zone 3→4

**Reviewed:** 2026-01-25
**Reviewer:** Maya (Design Thinking Maestro)
**Status:** ISSUES FOUND - FIXES REQUIRED

---

## Executive Summary

Story 3.5 is **80% strong** but has **3 critical issues** and **2 medium-priority issues** that must be fixed before this can be marked production-ready.

**Overall Assessment:** The document demonstrates deep integration with foundational documents, BUT has language inconsistencies and one incomplete section that violate foundational requirements.

---

## Critical Issues (MUST FIX)

### Issue 1: Zone 3→4 Identity Shift Language Incorrect

**Severity:** CRITICAL - Violates Epic 1.3 Node Architecture

**Location:** Lines 38-42, 121-123, and throughout master prompt

**The Problem:**
The document uses the identity shift:
> FROM: "AI helps me do things"
> TO: "I direct AI to create what I want"

**What Epic 1.3 Actually Says (lines 146-150):**
> **Theme:** From collaborator to director
> **Zone 3→4 Nodes (Direct):**
> These nodes target the identity shift from collaborator to director.

**For EACH specific node (lines 152-174):**
- Node 3.1: "AI's output is final" → "AI's output is starting point"
- Node 3.2: "AI decides quality" → "I decide quality"
- Node 3.3: "I hope AI understands" → "I know how to direct AI"
- Node 3.4: "AI created this" → "I made this (with AI's help)"

**Why This Matters:**
The master prompt language ("AI helps me do things") doesn't match the node-specific shifts documented in Epic 1.3. This creates confusion for Trevor when generating podcasts - which identity shift should he emphasize?

**Required Fix:**
1. Change line 38-40 to: "This week is about DIRECTORSHIP. Moving from 'AI collaborates with me' to 'I direct AI with intention.'"
2. Change lines 121-123 to align with Epic 1.3's zone-level theme: "From collaborator to director"
3. Keep all 4 node-specific shifts intact (they're correct)
4. Add a clarifying note explaining the zone-level shift vs. node-level shifts

---

### Issue 2: Emotional Job Language Inconsistent with Epic 1.2

**Severity:** CRITICAL - Violates JTBD Integration requirements

**Location:** Lines 42, 148, 197, 242, 285

**The Problem:**
The document uses the emotional job: **"Ownership"**

**What Epic 1.2 Actually Says (line 148):**
> **Zone 3→4 Nodes (Direct) - Weeks 6-7, Artifact in Week 8**
> **Emotional Job:** Ownership ("I have opinions about quality")

The emotional job text should be: **"I have opinions about quality"** (not just "Ownership")

**Why This Matters:**
The emotional job is a specific psychological state that must be precisely targeted. "Ownership" is the category, but "I have opinions about quality" is the exact emotional experience students should have after these nodes.

**Evidence from the document:**
- Line 42: "Create OWNERSHIP, not dependency" ✓ (correct category)
- Line 78: Emotional safety signals mention "Do I really have opinions about AI output quality?" ✓ (correct specific emotion)
- But line 148: "KEY MESSAGE: 'You know what 'good' looks like. Trust your judgment.'" ✗ (doesn't explicitly state the emotional job)

**Required Fix:**
1. Keep "Ownership" as the category when describing the zone
2. BUT explicitly state the emotional job as: **"I have opinions about quality"**
3. Update lines 42, 197, 242, 285 to include the full emotional job language
4. Example fix for line 42: "Create the feeling: 'I have opinions about quality' (Ownership), not dependency"

---

### Issue 3: Incomplete Section - "What Trevor Should Upload to NotebookLM" Missing

**Severity:** CRITICAL - Production blocker for Trevor

**Location:** Lines 324-357

**The Problem:**
The section "Source Material Requirements" lists WHAT Trevor should upload (lines 324-357), but there's no clear step-by-step workflow for HOW to prepare and upload the source material.

**What's Missing:**
1. A simple "Step 1: Combine these documents" workflow
2. Clear file paths or links to each source document
3. A checklist Trevor can use before uploading
4. A "pre-flight check" to ensure all sources are ready

**Why This Matters:**
Trevor needs to generate 4 podcasts from this document. If he doesn't know EXACTLY which documents to combine and upload, he'll waste time searching or miss critical sources.

**Required Fix:**
Add a new section after line 357:
```markdown
### Trevor's Pre-Upload Checklist

Before opening NotebookLM, gather these files:

[ ] 1. Cartographer's Manifesto Zone 3→4 sections
     File: `docs/cartographers_manifesto/zone-3-and-4.md` (or similar)
     Check: Does it explain Zone 3 (collaborator) and Zone 4 (director)?

[ ] 2. Node Architecture - Zone 3→4 section
     File: `playbook-v2/01-philosophy/node-architecture.md` lines 146-175
     Check: Are all 4 nodes listed with identity shifts?

[ ] 3. JTBD Integration - Ownership section
     File: `playbook-v2/01-philosophy/jtbd-integration.md`
     Check: Does it mention "I have opinions about quality"?

[ ] 4. 4 Habits - Habit 4 definition
     File: `playbook-v2/01-philosophy/four-habits-brand.md` lines 107-132
     Check: Does it show the 🧠 icon and tagline?

[ ] 5. Brand Framework v3
     File: `_bmad-output/k2m-edtech-brand-artifacts/k2m-brand-conversion-framework-v3.md`
     Check: Level 3-4 language examples

[ ] 6. Weeks 6-7 Design
     File: `playbook-v2/02-weekly-design/weeks-6-7-direct.md`
     Check: All 4 node specifications present?

[ ] 7. Artifact Requirements (for context)
     File: Referenced in requirements doc Decision 13
     Check: Do you understand what students will create in Week 8?

**Upload Method:**
Option A: Combine all 7 documents into one PDF
Option B: Upload all 7 documents separately to NotebookLM

**Estimated Prep Time:** 20 minutes
```

---

## Medium-Priority Issues (SHOULD FIX)

### Issue 4: Habit 4 Dual Pillars Mapping Slightly Confusing

**Severity:** MEDIUM - Could mislead Trevor about brand philosophy

**Location:** Lines 44-58, 157-158, 200-201, 244-245, 288-289

**The Problem:**
Each node section mentions "Dual Pillars Connection" and states that Habit 4 connects to BOTH pillars:
- Line 46: "Students are gaining BOTH pillars this week - but the focus is on Democratized Expertise through Habit 4"
- Line 157: "This node demonstrates Democratized Intelligence"
- Line 288: "This node brings both pillars together as directorship"

**What Epic 1.4 Actually Says (lines 111, 179-184):**
- **Habit 4 Dual Pillar:** "Democratized Expertise (better knowledge access)"
- **Pillar 1 (Intelligence):** Habits 1 & 2 = Better Thinking
- **Pillar 2 (Expertise):** Habits 3 & 4 = Better Knowledge Access
- **The Unifying Skill:** "Thinking WITH AI = Both pillars together"

**The Confusion:**
The document suggests Habit 4 demonstrates Democratized Intelligence (line 157), but Epic 1.4 clearly maps Habit 4 to Democratized Expertise.

**Why This Matters:**
Brand consistency. If Trevor mentions in a podcast that "Habit 4 shows Democratized Intelligence," he's contradicting the official brand framework.

**Required Fix:**
1. Update line 46 to: "Students are engaging with BOTH pillars this week. Habit 4 is officially part of Democratized Expertise (Pillar 2), but directorship involves clearer judgment (Pillar 1) AND better knowledge access (Pillar 2)."

2. Update node-specific sections:
   - Node 3.1 (line 157): Change to "This node primarily uses Democratized Expertise (accessing knowledge through AI drafts) while developing judgment (Pillar 1)."
   - Node 3.2 (line 200): Keep as is (developing taste = judgment = Pillar 1)
   - Node 3.3 (line 244): Keep as is (both pillars)
   - Node 3.4 (line 288): Keep as is (brings both together)

3. Add a clarifying note: "While Habit 4 is officially part of Pillar 2 (Expertise), directorship naturally involves both pillars. When students 'decide with AI,' they're accessing knowledge (Pillar 2) AND thinking clearly (Pillar 1). That's the unifying skill: Thinking WITH AI."

---

### Issue 5: Zone 3→4 Rock Climbing Metaphor Could Be More Specific

**Severity:** LOW - Nice-to-have strengthening

**Location:** Lines 61-69, 161, 204, 248, 292

**The Problem:**
The rock climbing metaphor is present (good!) but could reference the specific "holds" (nodes) students are grabbing this week.

**What's There:**
- Line 62: "This week you're grabbing 4 more holds on the AI territory wall"
- Line 292: "You've filled 4 nodes this week. You're now at Zone 4 - the summit. You've climbed 16 holds in your lattice."

**What Could Be Better:**
Explicitly name the 4 holds as the nodes:
1. "First draft is raw material" hold
2. "I have opinions about quality" hold
3. "Direction techniques work" hold
4. "I made this" hold

**Why This Matters:**
Strengthens the mental lattice metaphor. Helps students visualize EXACTLY which concepts they're adding to their climbing route.

**Required Fix (Optional but Recommended):**
Add to each node section:
- Node 3.1: "This is the first hold you're grabbing this week: 'First draft is raw material.'"
- Node 3.2: "This is the second hold: 'I have opinions about quality.'"
- Node 3.3: "This is the third hold: 'Direction techniques work.'"
- Node 3.4: "This is the fourth hold: 'I made this.' You've now reached Zone 4 - the summit!"

---

## What the Document Does Well (Strengths to Preserve)

✅ **Habit 4 branding is perfect:** Tagline "Think with AI before you decide" 🧠 appears consistently
✅ **CIS agents all mentioned:** All four agents (/frame, /diverge, /challenge, /synthesize) integrated
✅ **JTBD-aligned examples:** All examples from approved list, no prohibited content
✅ **Emotional safety signals:** Strong "you might be feeling..." language throughout
✅ **Live session bridges:** Each node connects to Trevor's sessions
✅ **Node-specific variations:** All 4 nodes have distinct, accurate content
✅ **Quality checklist:** Comprehensive review process for Trevor
✅ **Guardrails compliance:** No technical jargon, no impressive demos, no fear-based language
✅ **Tone and style:** Conversational, peer-to-peer, empowerment-focused
✅ **Production workflow:** Clear step-by-step for Trevor (except for source prep)

---

## Recommended Fix Order

1. **Fix Issue 3 first** (add pre-upload checklist) - unblocks Trevor immediately
2. **Fix Issue 1 second** (correct identity shift language) - aligns with Epic 1.3
3. **Fix Issue 2 third** (correct emotional job language) - aligns with Epic 1.2
4. **Fix Issue 4 fourth** (clarify Dual Pillars mapping) - brand consistency
5. **Fix Issue 5 last** (strengthen rock climbing metaphor) - optional polish

---

## Final Verdict

**Status:** NEEDS REVISION

**Cannot be marked production-ready until:**
- Issue 1 is fixed (identity shift language)
- Issue 2 is fixed (emotional job language)
- Issue 3 is fixed (missing pre-upload checklist)

**Estimated Fix Time:** 30-45 minutes

**After fixes:** This will be a production-ready, comprehensive master prompt that deeply integrates with all foundational documents and serves Trevor's workflow perfectly.

---

**Next Steps:**
1. Maya calls Party Mode with CIS agents to discuss these issues
2. Team reaches consensus on fixes
3. Apply all fixes to the document
4. Re-review to ensure all foundational documents are properly aligned
5. Mark Story 3.5 as production-ready
6. Update sprint-status.yaml
7. Commit with clear summary of fixes applied

---

*Adversarial Review conducted by Maya (Design Thinking Maestro)*
*Framework: BMAD Design Thinking workflow - Empathize, Define, Ideate stages*
*Focus: User experience (Trevor) and foundational alignment*
