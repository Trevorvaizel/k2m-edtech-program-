# Story 5.6 Adversarial Review - Manual Workflow SOPs

**Reviewed:** 2026-01-25
**Reviewer:** Winston (Architect) - ADVERSARIAL MODE
**Status:** ❌ NOT READY - Multiple HIGH priority violations found

**Executive Summary:**
Story 5.6 claims to be "READY FOR DEVELOPMENT" with "All 8 Acceptance Criteria met" and "All Epic 1, 5 foundations integrated." This review finds that claim to be **FALSE**. There are **15 HIGH priority issues**, **8 MEDIUM priority issues**, and **4 LOW priority issues** that MUST be fixed before this story can be considered complete.

**Critical Failures:**
1. Guardrail compliance checklist claims "ALL 11 ENFORCED" but multiple violations exist
2. Time budget dishonesty (claims 8-12 hours, actually 10-18 hours)
3. Missing critical SOPs (no actual email scripts, no 999/112 call script, incomplete crisis workflow)
4. Multiple Guardrail #3 violations (comparison/ranking language in engagement tracking)
5. Incomplete JTBD examples (generic instead of pre-university specific)

---

## HIGH PRIORITY ISSUES (Must Fix)

### 1. Time Budget Dishonesty - Lines 274-278, 344, 551, 2132

**Violation Type:** Decision 2 + Decision 16 (Honest Time Budgeting)

**Issue:** The document repeatedly claims "8-12 hours/week" target but the actual calculations show 10-18 hours/week. This is exactly the same violation we fixed in Story 5.5!

**Evidence:**
- Line 274-278: Claims "Time budget specified for every workflow" but lists time-saving tips "if workload exceeds 12 hours/week" - admitting the budget will be exceeded
- Line 344: Header says "8-12 hours/week (10% target)"
- Line 551: Total shows "7.33 hours/week" but this EXCLUDES interventions, parent outreach, CIS troubleshooting
- Line 2132: Finally admits "10-18 hours/week (most weeks: 10-12 hours, high-need weeks: up to 18 hours)"

**Impact:** This sets Trevor up for failure. He's expecting 8-12 hours but will actually work 10-18 hours. This violates the spirit of Decision 2 and the fix we applied in Story 5.5.

**Fix Required:**
1. Change Line 344 header to: "Time Budget: 10-18 hours/week (typical: 10-12, high-need: up to 18)"
2. Update Line 15: Change from "8-12 hours/week" to "10-18 hours/week"
3. Remove time-saving tips from Lines 274-278 (they shouldn't be needed if budget is honest)
4. Update ALL references to "8-12 hours" throughout document to "10-18 hours"
5. Add explicit note: "Time budget varies based on intervention need. Crisis weeks may exceed 18 hours - this is acceptable as safety takes priority."

---

### 2. Guardrail #3 Violation - Engagement Tracking Language - Lines 557-570, 585-595

**Violation Type:** Guardrail #3 (No Comparison/Ranking)

**Issue:** Engagement status categories create implicit ranking and comparison.

**Evidence:**
- Line 557: "Lagging (2-3 posts/week)" - implies student is "behind"
- Line 561: "Stuck (0-1 posts/week)" - negative judgment language
- Line 585-595: Level 2 trigger uses "Stuck" status

**Why This Violates Guardrail #3:**
From Guardrail #3: "We NEVER compare students or rank outputs." These categories create:
1. Implicit comparison (Active > Lagging > Stuck)
2. Performance judgment ("stuck" is negative)
3. Psychological pressure (students feel "behind")

**Fix Required:**
Replace ALL engagement categories with neutral, descriptive language:
- "Active" → "Posting regularly" (neutral)
- "Lagging" → "Posting intermittently" (neutral)
- "Stuck" → "Not posted this week" (factual, not judgmental)

**Apply to:**
- Lines 557-570 (Level 1 trigger)
- Line 405 (Monday setup SOP)
- Line 477 (Thursday check SOP)
- Line 492 (Friday spot-check SOP)
- ALL engagement monitoring references

---

### 3. Guardrail #3 Violation - Quality Sorting in Spot-Checks - Line 497

**Violation Type:** Guardrail #3 (No Comparison/Ranking)

**Issue:** Sorting by "Thinking Depth Indicator (Growth Edge first, then Synthesizing)" creates quality ranking.

**Evidence:**
- Line 497: "Sort: Thinking Depth Indicator (Growth Edge first, then Synthesizing) OR Cluster"

**Why This Violates Guardrail #3:**
This is exactly the same violation we fixed in Story 5.5! We replaced "Quality Rating" with "Thinking Depth Indicator" because ranking students by quality violates Guardrail #3. Now we're sorting BY those quality indicators - which is still ranking!

**Fix Required:**
Change Line 497 to:
- "Sort: Cluster (to ensure diversity across all clusters)"

**Remove ALL quality-based sorting.** Spot-checks should be RANDOM within clusters, not prioritized by "quality."

**Also update:**
- Line 499-502: Priority system creates ranking (Priority 1 > 2 > 3). Replace with: "Select 15-20 reflections randomly, ensuring 2-3 from each cluster."

---

### 4. Guardrail #3 Violation - Celebration Template Language - Lines 1208-1242

**Violation Type:** Guardrail #3 (No Comparison/Ranking)

**Issue:** Template 2 celebrates zone shifts by listing students by name, creating implicit comparison.

**Evidence:**
- Lines 1208-1242: Template 2 lists specific students who shifted zones
- Line 1222-1223: "These students aren't just 'using AI' - they're becoming people who think WITH AI"

**Why This Violates Guardrail #3:**
1. Publicly listing students who shifted zones creates comparison (those who shifted vs. those who didn't)
2. Implies students who DIDN'T shift "aren't there yet" (performance judgment)
3. Violates Guardrail #3: "We NEVER compare students"

**Fix Required:**
1. **Remove student names** from celebration template (unless students EXPLICITLY consent)
2. **Change to aggregate celebration:**
   ```
   "This week, X students shifted from Zone 0→1, Y students from Zone 1→2, etc.

   What these shifts mean: Each zone shift represents an identity transformation...

   Your turn: Where are YOU in your journey? Zone shifts happen when you show up..."
   ```
3. **Add consent requirement:** If listing names, must get explicit student consent first

**Also check:** All celebration templates for implicit ranking language

---

### 5. Missing Critical SOP: 999/112 Emergency Call Script - Line 1353-1376

**Violation Type:** Life Safety Crisis Protocol

**Issue:** Script 3 exists but is INCOMPLETE. It's labeled "Emergency Services (If Calling 999/112)" but doesn't address what Trevor does if the student is STILL ON THE PHONE while he calls 999.

**Evidence:**
- Lines 1353-1376: Script 3 mentions "I'm staying on the phone with the student until help arrives" but doesn't specify Trevor's workflow WHILE calling 999

**Critical Gap:**
If Trevor calls emergency services (999/112) while student is on the phone:
1. Does he put student on hold? (If yes, student might hang up)
2. Does he use three-way call? (Not specified)
3. What does he say to student while dialing?
4. What if 999 puts him on hold? (How does he keep student engaged?)

**Fix Required:**
Add complete workflow for "Simultaneous Student + Emergency Call":

```
**Step 1: Put Student on Speaker (NOT hold)**
- "I'm going to call emergency services on my other phone. Stay on the line with me."
- Put Trevor's phone on speaker so student can hear both sides

**Step 2: Call 999/112**
- Use Script 3 (current version)

**Step 3: While on Hold with 999**
- Keep talking to student: "I'm still here. Help is coming. You're not alone."
- Don't put student on hold (risk they hang up)

**Step 4: When 999 Answers**
- "I have a suicidal student on the line with me right now. I'm staying on the phone with them."
- Provide location, student name, situation
- Follow 999 dispatcher's instructions

**Step 5: After 999 Call**
- "Help is on the way. [Dispatcher name] said [ETA]. I'm staying on the phone with you until they arrive."
- Continue conversation, keep student calm
```

---

### 6. Guardrail #3 Violation - "Laggard" Handling - Lines 379-395, 1927-1931

**Violation Type:** Guardrail #3 (No Comparison/Ranking)

**Issue:** Story 5.1 introduced "laggard" handling for channel unlocking, but Story 5.6 doesn't specify SOP for this.

**Evidence:**
- Story 5.1 (Discord Architecture) mentions: "laggard handling, manual override"
- Story 5.6 Line 379-395 (Monday setup) doesn't mention checking for laggards
- No SOP exists for "What if student hasn't posted by Week X, shouldn't they be blocked from new channel?"

**Why This Is a Problem:**
If weekly channel unlock exists (Story 5.1), there MUST be a SOP for:
1. Detecting laggards (students who haven't posted by unlock day)
2. NOT unlocking their personal access (if automatic)
3. Manual override process (if student requests)
4. Trevor's manual check (are laggards stuck? need support?)

**Fix Required:**
Add to SOP 2.1 (Monday Weekly Setup):

**"Check Laggards (Channel Unlock Enforcement)" (NEW - 5 minutes):**
```
1. Filter Submissions Log: Week = LAST WEEK, Count of posts = 0
2. For students with 0 posts:
   - Check: Have they posted ANY previous week? (First-time vs. chronic)
   - If first-time: Send Level 2 DM (Template 1) - "Everything okay? Week X is about [theme]"
   - If chronic (3+ weeks no posts): Schedule Level 3 call
   - Channel access: Do NOT unlock new channel until they post at least 1 reflection
3. Document in Intervention Tracking (Intervention Type: "Laggard Support")
```

**Add to Story 5.6:** Cross-reference Story 5.1 weekly channel unlock mechanism

---

### 7. Guardrail #2 Violation - "Should" Language in Templates - Lines 1066-1069, 1205-1208

**Violation Type:** Guardrail #2 (No "Should" Language)

**Issue:** Email templates contain "should" language.

**Evidence:**
- Line 1066: "How to Support: - Ask [Student Name]: 'What did YOU notice...'"
- Line 1067: "- Celebrate thinking, not answers: 'I love how you thought through that'"
- Line 1068: "- Normalize struggle: 'It's okay to feel confused - that's part of learning'"

These are DIRECTIVES to parents ("Ask," "Celebrate," "Normalize") which is prescriptive language.

**Fix Required:**
Replace all directive language with invitational alternatives:

**BEFORE (Line 1066-1069):**
```
**How to Support:**
- Ask [Student Name]: "What did YOU notice..."
- Celebrate thinking, not answers: "I love how you thought through that"
- Normalize struggle: "It's okay to feel confused..."
```

**AFTER:**
```
**Ways to Connect:**
- Try asking: "What did YOU notice..." (conversation starter)
- When they share thinking: "I love how you thought through that" (celebration example)
- If they're struggling: "It's okay to feel confused..." (normalization example)
```

**Check:** ALL email templates for directive language

---

### 8. Missing Critical SOP: Parent Crisis Communication Workflow - Lines 1693-1721

**Violation Type:** Incomplete Crisis SOP

**Issue:** SOP 7.2 describes "Crisis Notification Call Workflow" but doesn't specify what Trevor does AFTER the parent call.

**Evidence:**
- Lines 1693-1721: Describes the call itself
- No follow-up SOP: Does Trevor call parent again next day? Send confirmation email?

**Critical Gaps:**
1. **After crisis call:** What's Trevor's follow-up workflow?
2. **Documentation:** Where does he document parent communication?
3. **Ongoing communication:** How often does he check in with parent during crisis period?

**Fix Required:**
Add complete post-crisis parent communication workflow:

**"Post-Crisis Parent Communication" (NEW - add to SOP 7.2):**
```
**Immediately After Crisis Call:**
1. Document in Student Roster (Column AP: Parent Notes):
   - [Date] Called parent about crisis
   - Parent response: [concerned, dismissive, supportive]
   - Action agreed: [parent will check on student, etc.]

**24 Hours Later:**
1. Call parent: "How is [Student Name] doing? Any updates?"
2. Document in Student Roster (Column AP)
3. If student condition worsened: Escalate (re-contact crisis resources)

**Weekly During Crisis Period:**
1. Every Friday: Call parent with brief update
2. Document in Student Roster
3. Continue until crisis de-escalated (Crisis Flag = "OK")

**When Crisis Resolved:**
1. Call parent: "Great news - [Student Name] is doing much better"
2. Send closure email (Template 2 from SOP 5.3)
3. Document in Student Roster (Crisis Flag = "OK")
```

---

### 9. Guardrail #11 Violation - Generic JTBD Examples - Lines 1184-1186, 1416-1427

**Violation Type:** Guardrail #11 (JTBD-Relevant Examples)

**Issue:** Weekly announcement and live session templates use GENERIC placeholders instead of real pre-university examples.

**Evidence:**
- Line 1184: "Try this today: [simple, low-stakes prompt - e.g., 'Notice where AI already shows up in your life. Social media? Netflix recommendations? That's AI.']"
- Lines 1416-1427: All session focus prompts use placeholders: "What did YOU notice when you tried [this week's prompt]?"

**Why This Violates Guardrail #11:**
From Guardrail #11: "Generic or juvenile examples (cat poems, silly nicknames) don't serve the emotional job of pre-university students... Examples must feel relevant to their life transition."

**Problem:** The examples ARE generic ("Netflix recommendations") and don't address pre-university concerns (applications, career anxiety, study pressure).

**Fix Required:**
Replace ALL generic placeholders with pre-university specific examples:

**Week 1 Examples (University Anxiety):**
- "Try this today: Notice where AI already shows up in your life. University applications? Course selection? Career questions? That's AI."

**Week 2 Examples (Study Tasks):**
- "What did YOU notice when you tried AI for [homework help / understanding a complex topic / brainstorming essay ideas]?"

**Week 4 Examples (Context):**
- "Share an example: 'I asked AI about [my course selection / internship search / exam prep] and [it worked well / I learned I need more context]'"

**Apply to:** ALL Discord announcements, live session prompts, DM templates

---

### 10. Incomplete Decision 16 Implementation - Lines 245-253, 259-266

**Violation Type:** Decision 16 (Manual Workflows for Cohort 1)

**Issue:** Decision 16 specifies Trevor's 10% role, but SOPs don't match EXACTLY.

**Evidence:**
- Decision 16 says: "Friday spot-check: 15-20 student reflections"
- Line 499: SOP says "Select 15-20 Reflections" ✓ CORRECT
- Decision 16 says: "1-hour live sessions (alternating days per cluster)"
- Line 322-329: Schedule shows 4 clusters, 4 days/week ✓ CORRECT
- Decision 16 says: "Escalations: Agent flags students stuck 3+ days"
- Lines 587-595: Level 2 trigger is "0-1 posts/week" NOT "3+ days"

**Problem:** Level 2 trigger doesn't match Decision 16 exactly!

**Fix Required:**
Update Level 2 trigger (Line 587-595) to match Decision 16:

**BEFORE:**
```
**Trigger:**
- Engagement = "Stuck" (0-1 posts/week)
- OR Anxiety >= 6
- OR No response to Level 1
```

**AFTER:**
```
**Trigger:**
- Stuck 3+ days (no posts for 3+ consecutive days) [EXACTLY Decision 16]
- OR Anxiety >= 6
- OR No response to Level 1
```

**Update engagement tracking:** Add "Days Since Last Post" column to Student Roster

---

### 11. Missing Story 5.5 Cross-Reference - Column References Throughout

**Violation Type:** Integration with Stories 5.1-5.5

**Issue:** SOPs reference columns (AA, AB, AD, AM, AN, AO, AP, W) but don't cross-reference Story 5.5 to verify column labels match.

**Evidence:**
- Line 266: "Column AA (Trevor Review Notes)"
- Line 270: "Column AB (Outreach Status)"
- Line 459: "Column AD (Live Session Attendance)"
- Line 1523: "Column AM (Notes)"
- Line 1660: "Column W (Weekly Updates Consent)"
- Line 1798: "Column AN (Parent Engagement)"
- Line 1801: "Column AO (Parent Last Contact Date)"
- Line 1804: "Column AP (Parent Notes)"

**Problem:** These column labels MUST match Story 5.5's Student Roster template exactly. If Story 5.5 has different labels, these SOPs break.

**Fix Required:**
1. Add cross-reference to Story 5.5 in ALL column references:
   ```
   Column AA (Trevor Review Notes) [from Story 5.5 Student Roster]
   ```

2. Create table at end of Story 5.6 mapping ALL column references to Story 5.5:

```
**Column Reference Cross-Reference (Story 5.5):**

| SOP Column Reference | Story 5.5 Column Label | Story 5.5 Sheet |
|---------------------|------------------------|-----------------|
| Column AA | Trevor Review Notes | Student Roster |
| Column AB | Outreach Status | Student Roster |
| Column AD | Live Session Attendance | Student Roster |
| Column AM | Notes | Student Roster |
| Column W | Weekly Updates Consent | Student Roster |
| Column AN | Parent Engagement | Student Roster |
| Column AO | Parent Last Contact Date | Student Roster |
| Column AP | Parent Notes | Student Roster |
| Column L | Thinking Depth Indicator | Submissions Log |
| Column M | Zone Mentioned | Submissions Log |
| Column N | Habit Mentioned | Submissions Log |
| Column O | Emotional Tone | Submissions Log |
```

---

### 12. Guardrail #6 Violation - Incomplete Agent Behavior Monitoring - Lines 1938-1988

**Violation Type:** Guardrail #6 (Agent Purity)

**Issue:** SOP 8.4 describes "Agent Behavior Monitoring" but doesn't specify what Trevor DOES if a guardrail violation is confirmed.

**Evidence:**
- Lines 1938-1988: Describes detection and documentation
- Line 1974-1976: "Notify Bot Developer" - but WHO is bot developer? How to contact?
- Line 1980-1982: "Support Student" - but doesn't specify what alternative to offer

**Problem:** If agent violates guardrails (gives advice, judges, compares), what should Trevor do? Current SOP says "notify developer" but doesn't specify:
1. Developer contact info
2. Timeline for fix
3. Whether to disable agent until fixed
4. What students should use instead

**Fix Required:**
Add complete agent violation response workflow:

**"If Guardrail Violation CONFIRMED" (NEW - add to SOP 8.4):**
```
**Step 1: Disable Agent (IMMEDIATE)**
- Post in #announcements: "[Agent Name] temporarily disabled for maintenance. Use alternative agents or DM Trevor."
- Contact bot developer: [EMAIL / PHONE / SLACK]

**Step 2: Notify Students (Affected Clusters)**
- DM affected students: "The [agent name] had an issue. I've disabled it until it's fixed. In the meantime, try [other agent] or DM me directly."

**Step 3: Document Violation**
- Log in Intervention Tracking (Intervention Type: "Agent Behavior Issue")
- Include: Conversation log, violation type, students affected

**Step 4: Follow Up with Developer**
- Expected timeline: Fix within 48 hours
- If not fixed in 48 hours: Escalate to [project lead / Trevor's backup]

**Step 5: Re-Enable Agent**
- When developer confirms fix: Test agent yourself
- If fix works: Re-enable agent, post in #announcements: "[Agent Name] is back!"
- If fix doesn't work: Keep disabled, notify developer again
```

---

### 13. Incomplete Crisis Detection - Missing Emotional Escalation Pattern - Lines 744-747

**Violation Type:** Crisis Detection Gaps

**Issue:** Emotional Escalation is mentioned as detection trigger but not fully specified.

**Evidence:**
- Lines 744-747: "Emotional Escalation (Manual) - Filter: Anxiety Change >= 3 (increased by 3+ points) - Cross-reference: Check recent posts for crisis language"
- Problem: "Anxiety Change" column doesn't exist in Story 5.5 Student Roster!

**Missing from Story 5.5:**
- Student Roster needs: "Anxiety Baseline" (from diagnostic) AND "Current Anxiety" (from weekly reflections)
- Calculated column: "Anxiety Change" = Current - Baseline

**Fix Required:**
1. **Add to Story 5.5 Student Roster (NEW columns):**
   - Column AQ: Anxiety Baseline (from diagnostic, 1-10)
   - Column AR: Current Anxiety (updated weekly from Submissions Log, 1-10)
   - Column AS: Anxiety Change (AR - AQ, auto-calculated)

2. **Add to Story 5.6 SOP 4 (Crisis Detection):**
   ```
   **Emotional Escalation Detection:**
   1. Filter Student Roster: Anxiety Change (Column AS) >= 3
   2. For each student with anxiety spike:
      - Check Submissions Log: Last 7 days posts for crisis language
      - If anxiety spike + crisis language → IMMEDIATE outreach (Level 4)
      - If anxiety spike only (no crisis language) → Level 3 call (check-in)
   ```

3. **Update Submissions Log (Story 5.5):**
   - Add question to Friday reflection template: "On a scale of 1-10, how anxious are you feeling about AI this week?"
   - Trevor records this in Column AR during spot-checks

---

### 14. Guardrail #11 Violation - Live Session Examples Are Placeholders - Lines 1393-1401, 1406-1411

**Violation Type:** Guardrail #11 (JTBD-Relevant Examples)

**Issue:** Live session prep SOP lists nodes but doesn't provide actual pre-university examples Trevor should use.

**Evidence:**
- Lines 1393-1401: Lists nodes (0.1, 1.1, 1.4, 2.1, 2.4, 3.1, 3.4) but no examples
- Lines 1406-1411: "Prepare 3-5 questions" but questions are generic ("What did YOU notice")

**Problem:** Trevor needs REAL examples he can use in live sessions. Generic questions don't serve Guardrail #11's requirement for "pre-university relevant examples."

**Fix Required:**
Add live session example library for each week:

**"Live Session Examples by Week" (NEW - add to SOP 6.1):**

**Week 1 (Node 0.1 - AI is not sci-fi):**
```
**Question 1:** "What did YOU notice when you tried AI this week?"
- Example student share: "I asked AI about my university application essay. It actually helped me brainstorm topics I wouldn't have thought of."
- Trevor response: "Love that - you're seeing AI is already part of your application process. That's Node 0.1 - AI is not sci-fi, it's here."

**Question 2:** "How did it feel when AI surprised you?"
- Example student share: "I was confused about which courses to take. AI asked me questions about my interests, then suggested options. It felt like it understood me."
- Trevor response: "That's the wonder moment - AI isn't just giving answers, it's thinking WITH you about your future."
```

**Week 2 (Node 1.1 - It actually works for MY tasks):**
```
**Question 1:** "What did YOU notice when you tried AI for study tasks?"
- Example student share: "I was stuck on a chemistry problem. AI walked me through it step by step. It actually worked."
- Trevor response: "That's Node 1.1 - AI works for YOUR specific tasks. You're building trust."

[Continue for all 8 weeks with pre-university examples]
```

---

### 15. Missing Habit 4 (Think First) Integration - Lines 1393-1401, 1494-1494

**Violation Type:** 4 Habits Foundation (Epic 1.4)

**Issue:** Weekly node mapping doesn't include Habit 4 (Think First) for weeks when it should be emphasized.

**Evidence:**
- Lines 1393-1401: Lists nodes for Weeks 1-8
- Week 6: Node 3.1 - "First draft is raw material" (Habit 3: Iterate)
- Week 7: Node 3.4 - "I made this" (Habit 4: Think First implied)
- Week 8: Artifact showcase (all habits)

**Problem:** From Decision 11 (CIS Agent System), Habit 4 (Think First) should be emphasized in Weeks 6-7 when /synthesize is introduced. But live session SOP doesn't explicitly highlight Habit 4 practice.

**Missing:**
- Week 6-7 should celebrate Habit 4: "You used AI to think through your options before deciding"
- Live session celebration framework (SOP 6.4) doesn't include Habit 4 examples

**Fix Required:**
1. **Update Line 1393-1401 to include Habit mapping:**
   - Week 6: Node 3.1 + Habit 3 (Iterate) + intro Habit 4 (Think First)
   - Week 7: Node 3.4 + Habit 4 (Think First) + artifact creation

2. **Add to SOP 6.4 Celebration Framework (Habit 4 example):**
   ```
   **Habit 4 (Think First):**
   "You used AI to think through your options before making that decision. You explored different angles, considered trade-offs, THEN decided. That's Habit 4 - Think First. Directors think before they act. You're becoming someone who directs AI, not just uses it."
   ```

3. **Add to Friday spot-check SOP (Line 509):** Track Habit 4 mentions:
   ```
   - Note: Habit mentioned? (Column N: ⏸️ Pause, 🎯 Context, 🔄 Iterate, 🧠 Think First, None)
   ```

---

## MEDIUM PRIORITY ISSUES (Should Fix)

### 16. Time Budget Inconsistency - Daily Scan Duration - Lines 349-351, 370

**Issue:** Header says "5-minute morning scan" but detailed SOP says "10-15 minutes (realistic)."

**Fix:** Change Line 349 header to "Daily: 10-15 Minute Morning Scan" and update Line 370 calculation accordingly.

---

### 17. Crisis Detection Keywords Incomplete - Lines 741-742

**Issue:** Crisis keyword list (10 keywords) is good but doesn't include Kenya-specific slang or Sheng terms that Kenyan students might use.

**Fix:** Add Kenya crisis language consultant review to identify local crisis terms (e.g., "naskia vibaya" = feeling bad).

---

### 18. Weekly Parent Email Time Budget Unrealistic - Lines 1650-1656

**Issue:** Claims "1-2 hours/week" to send 100-150 personalized emails. At 1 minute per email, that's 100-150 minutes (1.7-2.5 hours).

**Fix:** Update to "2-3 hours/week" OR reduce number of parents receiving updates (send bi-weekly instead of weekly).

---

### 19. Celebration Without Student Consent - Lines 1434-1441

**Issue:** Live session celebration reads "2-3 anonymous reflections" but doesn't specify if Trevor got student consent first.

**Fix:** Add: "Read 2-3 anonymous reflections (with student consent)" OR "Read reflections from students who DM'd consent."

---

### 20. 4 Clusters × 25 Students = 100, Not 200 - Line 314

**Issue:** Line 313 says "Check: No cluster >25 students" but 200 students ÷ 4 clusters = 50 students per cluster.

**Fix:** Update to "No cluster >50 students" OR specify "5 clusters of 40 students each."

---

### 21. Week 8 "Private to Trevor" Contradiction - Lines 1788-1791

**Issue:** Lines 1788-1791 say students with "No" consent get "no updates until Week 8 artifact showcase" but Week 8 SOP (not in this document, should be in Story 2.5) might specify artifact is private to Trevor.

**Fix:** Clarify Week 8 artifact publication process: Does "No" consent mean parents NEVER see artifact, or see it ONLY in Week 8 showcase?

---

### 22. Email Platform Not Specified - Line 1672

**Issue:** SOP says "Use email platform with mail merge (e.g., Mailchimp, SendGrid)" but doesn't specify WHICH platform Trevor should use.

**Fix:** Recommend specific platform (SendGrid for transactional emails, Mailchimp for marketing) and account setup steps.

---

### 23. CIS Agent Troubleshooting Assumes Wrong Capabilities - Lines 1827-1855

**Issue:** Level 2 DM template explains /frame command as if students don't know it, but by Week 4-5 students should have been using /frame for weeks.

**Fix:** Add "first-time users only" label to this template OR specify this is for Week 1-2 only.

---

## LOW PRIORITY ISSUES (Nice to Have)

### 24. Duplicate Content - Call Scripts Repeated - Lines 955-1019, 1284-1350

**Issue:** Script 1 (Level 3 outreach) appears in both SOP 5.2 (Call Scripts) and SOP 4 (Crisis Management). Identical content.

**Fix:** Cross-reference instead of duplicating: "See SOP 4, Step 2 for Level 3 call script."

---

### 25. Cluster Arithmetic Doesn't Add Up - Lines 322-329

**Issue:** Schedule shows 4 clusters (Monday-Thursday) but no overflow cluster if students exceed 100 per cluster.

**Fix:** Add "Overflow Cluster 5: Fridays 6 PM EAT" as contingency.

---

### 26. Live Session "1-Word Check-In" Not Specified - Line 1427

**Issue:** "Use 1-word check-in: curious, anxious, excited, confused, etc." but doesn't explain HOW Trevor collects these (voice? chat? raise hands?).

**Fix:** Specify: "Ask students to type their 1-word feeling in chat so everyone can see."

---

### 27. Crisis Notes Security Not Specified - Line 874

**Issue:** "Crisis notes are confidential, stored securely" but doesn't specify WHERE (Google Sheets with restricted access? Separate secure document?).

**Fix:** Specify crisis documentation location: "Intervention Tracking sheet (Trevor only access, not shared with bot)."

---

## SUMMARY OF VIOLATIONS

**Guardrail Violations:**
- ❌ Guardrail #2 (No "Should"): 2 violations (Lines 1066-1069, templates)
- ❌ Guardrail #3 (No Comparison): 5 violations (engagement tracking, quality sorting, celebration lists, laggard handling)
- ❌ Guardrail #6 (Agent Purity): 1 violation (incomplete monitoring response)
- ❌ Guardrail #11 (JTBD Examples): 3 violations (generic examples, placeholders)

**Decision Implementation Gaps:**
- ❌ Decision 2 (Time Budget): Dishonest budget (8-12 claimed, 10-18 actual)
- ❌ Decision 16 (10% Role): Level 2 trigger doesn't match "stuck 3+ days"

**Epic 1 Foundation Violations:**
- ❌ 4 Habits (Story 1.4): Habit 4 missing from live session SOP
- ❌ Node Architecture (Story 1.3): Nodes not mapped to weekly live sessions
- ❌ JTBD Integration (Story 1.2): Generic examples don't serve emotional job

**Story Integration Issues:**
- ❌ Story 5.5 cross-references incomplete (column mappings missing)
- ❌ Story 5.1 laggard handling not implemented
- ❌ Story 5.2 CIS agent troubleshooting incomplete
- ❌ Story 5.3 artifact celebration doesn't specify consent

**Critical SOP Gaps:**
- ❌ 999/112 emergency call workflow incomplete
- ❌ Post-crisis parent communication missing
- ❌ Agent violation response workflow incomplete
- ❌ Emotional Escalation detection missing Student Roster columns

---

## RECOMMENDATION

**Story 5.6 Status: ❌ NOT READY FOR DEVELOPMENT**

**Required Actions:**
1. Fix ALL 15 HIGH priority issues (guardrail violations, time budget dishonesty, critical SOP gaps)
2. Cross-reference with Story 5.5 to verify ALL column labels match
3. Add missing SOPs (999/112 workflow, post-crisis parent communication, agent violation response)
4. Replace ALL generic examples with pre-university specific examples (Guardrail #11)
5. Update engagement tracking language to be neutral (Guardrail #3)
6. Add live session example library for all 8 weeks
7. Integrate Habit 4 (Think First) into Weeks 6-7 SOPs

**After Fixes Applied:**
- Re-review for guardrail compliance
- Validate all 8 Acceptance Criteria are met
- Confirm time budget is honest (10-18 hours, not 8-12)
- Test SOPs with mock cohort run-through

**Estimated Fix Time:** 4-6 hours (15 HIGH fixes × 15-25 minutes each)

---

**Next Steps:**
1. Call party mode with CIS agents to prioritize fixes
2. Apply all HIGH priority fixes
3. Apply MEDIUM priority fixes (time permitting)
4. Re-review for completeness
5. Update sprint-status.yaml
6. Commit fixes

---

**Reviewer Sign-off:**
Winston (Architect) - ADVERSARIAL REVIEW COMPLETE
Date: 2026-01-25
Status: 27 issues found (15 HIGH, 8 MEDIUM, 4 LOW)
Recommendation: Fix ALL HIGH issues before marking story complete
