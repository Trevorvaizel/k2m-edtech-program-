# User Testing Protocol for K2M Landing Page

**Document Version:** 1.0
**Last Updated:** 2026-01-15
**Project:** K2M EdTech Awwwards-Level Landing Page
**Purpose:** Comprehensive user testing methodology to validate emotional response and conversion effectiveness

---

## Table of Contents

1. [Testing Protocol Overview](#1-testing-protocol-overview)
2. [Test Task List](#2-test-task-list)
3. [Section-Specific Validation Questions](#3-section-specific-validation-questions)
4. [Issue Flagging Protocol](#4-issue-flagging-protocol)
5. [Testing Schedule and Rounds](#5-testing-schedule-and-rounds)
6. [Test Session Script](#6-test-session-script)
7. [Data Collection Templates](#7-data-collection-templates)
8. [Recruitment Strategy](#8-recruitment-strategy)
9. [Testing Report Format](#9-testing-report-format)
10. [Alignment with Story 0.1 Metrics](#10-alignment-with-story-01-metrics)
11. [Appendix: Templates and Resources](#appendix-templates-and-resources)

---

## 1. Testing Protocol Overview

### 1.1 Testing Objective

**Primary Objective:** Validate that the K2M landing page works **emotionally**, not just technically. We're testing whether users feel "seen," "understood," and "relieved" - not whether buttons work.

**Why This Matters:**
- K2M is selling emotional relief (AI doesn't have to be confusing)
- A technically perfect page that feels wrong won't convert
- User testing is the only way to validate emotional response
- Analytics (Story 0.2) measure WHAT users do; user testing measures WHY they do it

**Key Philosophy:**
> We're not testing the user - we're testing the page. There are no wrong answers. Every hesitation, confusion, or negative reaction is a finding, not a user error.

### 1.2 Target Demographic

**Who We're Testing:**
- **Age:** 18-30 years old (university students and early career)
- **Location:** Kenya (primary focus: Nairobi, Kisumu, Mombasa)
- **Background:** Interested in AI but confused by it
- **Experience:** Have used ChatGPT but don't feel in control
- **Device:** Mobile-first users (Android, budget devices)
- **Language:** English-speaking (Kenya's official language)

**Why This Demographic:**
This is K2M's **actual audience**, not Western tech users. Kenyan students:
- Have different pain points (mobile data costs, device limitations)
- Different cultural context (community-based learning)
- Different AI exposure (newer to AI, more skepticism)
- Different internet reality (slower connections, pay-as-you-go data)

**Exclusion Criteria (Who NOT to test):**
- Professional software developers (too technical)
- People outside Kenya (wrong cultural context)
- People who've never heard of AI (too far behind)
- K2M team members or friends (too biased)

### 1.3 Sample Size

**Target: 5 users per testing round**

**Why 5 Users:**
- **Nielsen Norman Group research:** 5 users finds 85% of usability problems
- **Qualitative patterns:** 3+ users reporting same issue = real pattern, not outlier
- **Time-efficient:** 5 users × 45 minutes = 3.75 hours per round (manageable)
- **Cost-effective:** Incentives for 5 users = 2,500 KES (~$20 USD) per round

**When to Test More:**
- If results are inconsistent (mixed responses, no clear patterns)
- If you have diverse sub-demographics (technical vs non-technical)
- If first 5 users reveal critical issues (test 5 more to validate fixes)

**When 5 Is Enough:**
- Clear patterns emerge (3+ users report same issue)
- Consistent emotional responses across users
- No major disagreements on findings

### 1.4 Testing Method: Remote Screen Share + Think-Aloud Protocol

**What This Means:**
- **Remote:** User participates from their own device/home (Zoom, Google Meet, Teams)
- **Screen Share:** User shares their screen so you see exactly what they see
- **Think-Aloud:** User speaks their thoughts out loud in real-time as they browse

**Why This Method:**

| Method | Pros | Cons | Our Choice |
|--------|------|------|------------|
| **Remote Think-Aloud** (✅ chosen) | • Real-time emotional reactions<br>• See user's actual device<br>• Captures confusion points<br>• Low friction for users | • Requires scheduling<br>• Internet-dependent | **Best for emotional validation** |
| In-Person Lab | • Control environment<br>• See body language | • Expensive<br>• Artificial environment<br>• Travel required | ❌ Not practical |
| Async (Recordings) | • No scheduling needed<br>• Scalable | • No real-time reactions<br>• Can't ask follow-up<br>• Missing context | ❌ Misses emotional nuance |
| Survey Only | • Easy to scale<br>• Quantitative data | • No observation<br>• Self-reported bias<br>• Missing "why" | ❌ Complements, doesn't replace |

**Why Think-Aloud is Critical:**
- Captures **real-time emotional reactions** (sighs, pauses, confusion)
- Reveals **internal monologue** (what they expect vs what they see)
- Shows **decision-making process** (why they clicked/didn't click)
- Uncovers **mental models** (what they think K2M does)

### 1.5 Testing Rounds

**Two Testing Rounds:**

| Round | Timing | What's Tested | Goal |
|-------|--------|---------------|------|
| **Round 1** | After Epic 1 (Hero section only) | Hero section only | Catch emotional issues early before building rest of page |
| **Round 2** | After Epic 3 (Full page: Hero → Map → Discord → CTA) | Complete emotional journey | Final validation before launch |

**Why Two Rounds:**
- **Round 1:** Fail fast on Hero (if opening doesn't work emotionally, fix before investing in Map/Discord)
- **Round 2:** Validate complete journey (emotional arc from confusion → relief → belonging → action)

**Duration per Round:**
- 5 users × 30-45 minutes per session = **2.5-3.75 hours total**
- Plus 1 hour prep (recruitment, scheduling) = **3.5-4.75 hours per round**

---

## 2. Test Task List

### 2.1 Task Overview

Users will complete **5 structured tasks** during the test session. These tasks are designed to:
1. Observe natural behavior (Task 1)
2. Validate self-identification in zones (Task 2)
3. Test value proposition comprehension (Task 3)
4. Measure emotional response (Task 4)
5. Test conversion readiness (Task 5)

### 2.2 Task Instructions (Read Aloud to User)

#### **Task 1: Natural Scroll**
> "I'd like you to scroll through the entire page naturally, from top to bottom. As you go, please tell me what you're thinking out loud - what catches your attention, what confuses you, what you like or don't like. There's no wrong answer. Take your time."

**Purpose:** Observe natural scrolling behavior, identify what draws attention, reveal confusion points

**What to Watch For:**
- Do they scroll steadily or pause at certain sections?
- Do they read everything or skim?
- Do they scroll back up to re-read anything?
- What emotional reactions do you hear? (sighs, laughs, "huh", "oh")

**Success Indicators:**
- Scrolls through entire page (doesn't bounce immediately)
- Spends meaningful time on each section (doesn't race through)
- Comments on content (not just scrolling silently)

**Red Flags:**
- Scrolls past entire page in <10 seconds (not engaged)
- Gets stuck in one section (confusion or over-focus)
- Doesn't scroll to CTA (drop-off before conversion point)

---

#### **Task 2: Territory Map Self-Identification**
> "Looking at the Territory Map section with the zones labeled 0 through 4, which zone do you feel you're in right now? Why do you think that's your zone?"

**Purpose:** Validate that users can clearly identify their current AI journey stage

**What to Watch For:**
- Do they choose a zone confidently or hesitate?
- Do they ask for clarification on what zones mean?
- Do they switch between zones before deciding?
- Can they explain WHY they chose that zone?

**Success Indicators:**
- Chooses a zone within 10 seconds (confident decision)
- Provides clear reasoning ("I've used ChatGPT but don't understand how it works")
- Doesn't ask for clarification (zones are self-explanatory)

**Red Flags:**
- "I don't know, what do you think?" (zones aren't clear)
- "All of them?" (zones aren't distinct enough)
- "None of these" (zones don't cover their experience)
- Takes 30+ seconds to decide (analysis paralysis)

**Follow-Up Questions (if needed):**
- "What made you choose that zone over the others?"
- "Did any other zone feel like it might be you?"
- "What would make you more confident in your choice?"

---

#### **Task 3: Value Proposition Comprehension**
> "In one sentence, tell me what K2M offers. What would you tell a friend about K2M?"

**Purpose:** Test if value proposition is clear and memorable

**What to Watch For:**
- Do they answer immediately or think for a while?
- Is their answer accurate (matches what K2M actually does)?
- Do they use K2M's language or their own words?
- How long is their sentence? (One sentence rule is intentional)

**Success Indicators:**
- Answers within 5 seconds (value prop is clear)
- Mentions key elements: AI training, program, community, diagnostic
- Uses their own words (not parroting the page)
- Keeps it to one sentence (clear mental model)

**Example Good Answers:**
- "K2M is a training program that helps you understand AI better."
- "They teach you how to actually use AI, not just be confused by it."
- "It's a community that helps you get from confused to in control of AI."

**Red Flags:**
- "I don't know" / "I'm not sure" (value prop not clear)
- "It's like ChatGPT?" (confused with AI tools)
- "Something about AI... and maps?" (focused on UI, not value)
- 3+ sentence rambling answer (no clear mental model)

---

#### **Task 4: Emotional Response Rating**
> "I'd like you to rate each section of the page on a scale of 1 to 5. This isn't about whether it looks good - it's about how it made you **feel**. 1 means it made you feel confused or frustrated, 5 means it made you feel understood or relieved. Give me a rating for:
> 1. The Hero section (the opening)
> 2. The Territory Map
> 3. The Discord/community section
> 4. The CTA section at the end"

**Purpose:** Quantify emotional response for each section

**Rating Scale (Show User):**
```
1 - Confused, frustrated, annoyed
2 - Skeptical, unsure, indifferent
3 - Neutral, no strong feeling
4 - Interested, curious, hopeful
5 - Understood, seen, relieved, excited
```

**What to Watch For:**
- Do they rate quickly or deliberate?
- Do they ask for clarification on the scale?
- Do their facial expressions match their rating?
- Do they give reasons for their ratings?

**Success Indicators (Target):**
- Hero: 4+ (feeling seen/validated)
- Map: 4+ (clear identification)
- Discord: 4+ (belonging/community)
- CTA: 4+ (relief, not pressure)

**Red Flags:**
- Any section rated 1-2 (emotional failure)
- All sections rated 3 (emotional flatline - no impact)
- Discord rated 1-2 (community section failing)

**Follow-Up Questions:**
- "What made you give the Hero a 4 instead of a 5?"
- "What would have made the Map section a 5 for you?"
- "How did the CTA section make you feel?"

---

#### **Task 5: Conversion Readiness (CTA Click)**
> "Now I'd like you to click the CTA button - the button that lets you start the diagnostic or join K2M. You don't have to complete the form or actually join - I just want you to click the button and tell me what you're thinking as you do it."

**Purpose:** Test if CTA feels like pressure or invitation

**What to Watch For:**
- Do they click immediately or hesitate?
- Do they hover over the button first?
- Do they ask "What happens if I click this?"
- What do they say as they click? (if anything)
- Do they click confidently or tentatively?

**Success Indicators:**
- Clicks within 5 seconds of reaching CTA section
- Clicks confidently (no hesitation)
- Says something positive ("Okay, let's try it" / "Sure")
- Doesn't ask what will happen (trust established)

**Red Flags:**
- "Do I have to?" (feels pressured)
- Hovers for 15+ seconds (uncertainty/fear)
- "What am I committing to?" (not clear)
- Doesn't click at all (conversion blocked)
- Clicks tentatively (slow, careful mouse movement)

**Post-Click Debrief:**
- "What almost stopped you from clicking that button?"
- "Did it feel like pressure or an invitation?"
- "What would have made you click faster?"

---

### 2.3 Think-Aloud Instructions

**Critical Instruction (Read at Start of Session):**
> "As you go through the page, please **think out loud**. Tell me what you're thinking, what you're looking for, what you expect to happen, what confuses you, what you like. There's no wrong answer - I'm testing the page, not you. If you go silent for a while, I might remind you to keep talking, and that's totally normal."

**Why Think-Aloud Matters:**
- **Real-time processing:** Capture thoughts as they occur, not reconstructed later
- **Emotional leaks:** Users sigh, laugh, or express frustration before they realize it
- **Mental models:** Hear how they think the page works (may differ from reality)
- **Confusion points:** Silence often = confusion (ask "What are you thinking right now?")

**How to Keep User Talking:**
- Gentle reminders: "Keep telling me what you're thinking"
- Specific prompts: "What do you make of that section?"
- Neutral probes: "What caught your attention there?"
- Avoid leading questions: Don't ask "Did that confuse you?" → Ask "What did you think of that?"

---

## 3. Section-Specific Validation Questions

### 3.1 Hero Section: "How does this opening make you feel?"

**Target Emotions:** Relief, seen, understood

**What We're Testing:**
Does the Hero section make users feel:
- "Finally, someone gets it" (seen/understood)
- "I'm not the only one" (relief)
- "This is for me" (belonging)

**Success Indicators:**
- User uses words like: "relieved," "understood," "seen," "finally," "me too"
- User nods or smiles while reading
- User spends time reading (doesn't scroll past immediately)
- Rating: 4-5 on emotional scale

**Follow-Up Questions:**
- "What part of the opening made you feel that way?"
- "Did anything confuse you about the opening?"
- "What would have made you feel even more seen?"

**Red Flag Responses:**
- "I don't know, it's fine" (neutral = emotional failure)
- "It feels like marketing" (skepticism)
- "What is this?" (confusion)
- "Too long" (impatience)

---

### 3.2 Territory Map: "Which zone do you think you're in? Why?"

**Target:** Clear identification without confusion

**What We're Testing:**
Can users:
- Identify their current zone confidently?
- Explain WHY they're in that zone?
- Distinguish between adjacent zones (e.g., Zone 2 vs Zone 3)?

**Success Indicators:**
- User chooses a zone within 10 seconds (confident)
- User provides reasoning that matches zone definition
- User doesn't ask "What do these zones mean?"
- User says "That's definitely me" or "Exactly"

**Follow-Up Questions:**
- "What made you choose Zone X over Zone Y?"
- "Did any other zone feel like it might be you?"
- "What would make you more confident in your choice?"

**Red Flag Responses:**
- "I don't know, what do you think?" (zones unclear)
- "All of them?" (zones not distinct)
- "None of these describe me" (zones don't cover user's experience)
- User switches zones multiple times (indecision)

---

### 3.3 Discord Section: "Would you want to join this community?"

**Target:** Yes, feeling of belonging

**What We're Testing:**
Does the Discord section make users feel:
- "These are my people" (belonging)
- "I could learn from this community" (value)
- "I'd fit in here" (inclusion)

**Success Indicators:**
- User says "yes" or "definitely" (not "maybe")
- User smiles or shows interest while reading
- User spends time on chat bubbles/emojis (engagement)
- User asks questions about the community (curiosity)
- Rating: 4-5 on emotional scale

**Follow-Up Questions:**
- "What makes you want to join (or not want to join)?"
- "Who do you imagine being in this community?"
- "What would you hope to get from this community?"

**Red Flag Responses:**
- "I don't like Discord" (platform objection, not content)
- "I'm not a 'community' person" (not target audience)
- "This feels like other groups I'm in" (no differentiation)
- "I don't see myself here" (exclusion)

---

### 3.4 CTA Section: "Does this feel like pressure or an invitation?"

**Target:** Invitation, not pressure or desperation

**What We're Testing:**
Does the CTA section feel:
- Welcoming and low-pressure? (invitation ✅)
- Urgent and demanding? (pressure ❌)
- Desperate or salesy? (desperation ❌)

**Success Indicators:**
- User says "invitation" or "opportunity" (not "pressure")
- User clicks confidently (no hesitation)
- User says things like "Sure," "Okay," "Let's try it"
- User doesn't ask "What am I committing to?" (trust established)
- Rating: 4-5 on emotional scale

**Follow-Up Questions:**
- "What made it feel like an invitation (vs pressure)?"
- "What almost stopped you from clicking?"
- "Did you feel like you had a choice?"

**Red Flag Responses:**
- "It feels like a sales pitch" (pressure)
- "I don't want to sign up for something" (commitment fear)
- "What if I don't want to give my email?" (friction)
- "Too many buttons" (confusion)

---

## 4. Issue Flagging Protocol

### 4.1 Issue Threshold: When Is It a Real Problem?

**Golden Rule:** If **3+ users** report the same issue, it's a **pattern**, not an outlier.

**Why 3 Users:**
- 1 user: Could be that individual's preference/confusion
- 2 users: Could be coincidence
- 3+ users: **Statistically significant pattern** (85% confidence)

**Examples:**
- User 1: "I didn't understand the zones" → Maybe confused user
- User 2: "The zones were confusing" → Coincidence?
- User 3: "I couldn't tell which zone I'm in" → **PATTERN - Fix zones**

**What Counts As "Same Issue":**
- **Exact words:** 3 users say "zones are confusing" = clear issue
- **Same behavior:** 3 users hover over CTA but don't click = clear issue
- **Same sentiment:** 3 users express skepticism/distrust (different words) = clear issue

**When to Investigate Further:**
- 2 users report issue + 1 user seems to struggle with it (but doesn't say it)
- 1 user reports issue + it's a critical conversion blocker (CTA not working)
- Mixed feedback (some hate it, some love it) = design polarization (needs investigation)

---

### 4.2 Issue Categories

**1. Confusion**
- **Definition:** User doesn't understand something (copy, UI, flow)
- **Examples:** "What does this mean?" / "I don't get it" / "Where do I click?"
- **Severity:** Usually Major (causes drop-off)
- **Typical Fix:** Simplify copy, add explanation, improve visual hierarchy

**2. Frustration**
- **Definition:** User expresses annoyance, anger, or impatience
- **Examples:** Sighs, "Ugh," "This is annoying," eye rolls
- **Severity:** Usually Critical (causes immediate bounce)
- **Typical Fix:** Remove friction, simplify task, fix broken interaction

**3. Disengagement**
- **Definition:** User loses interest, stops paying attention
- **Examples:** Skims content, silent scrolling, "too long," "I'm bored"
- **Severity:** Usually Major (causes drop-off before conversion)
- **Typical Fix:** Shorten content, add visual interest, improve pacing

**4. Misalignment**
- **Definition:** User's understanding doesn't match reality
- **Examples:** "I thought K2M was X" (when it's Y), "This isn't what I expected"
- **Severity:** Usually Major (wrong expectations = wrong users)
- **Typical Fix:** Clarify value proposition, adjust targeting, rewrite positioning

**5. Technical Issue**
- **Definition:** Something doesn't work (broken link, slow load, bug)
- **Examples:** "It's not loading," "I clicked but nothing happened," "This is slow"
- **Severity:** Critical (blocks all conversion)
- **Typical Fix:** Fix bug, optimize performance, improve loading

**6. Trust/Safety Concern**
- **Definition:** User doesn't trust K2M or feels unsafe
- **Examples:** "Is this legit?" / "What will you do with my data?" / "This feels like a scam"
- **Severity:** Critical (zero conversion without trust)
- **Typical Fix:** Add social proof, clarify privacy, improve transparency

---

### 4.3 Severity Levels

**Severity Decision Tree:**
```
Does it block conversion completely?
├─ Yes → CRITICAL
└─ No → Does it cause significant drop-off or confusion?
    ├─ Yes → MAJOR
    └─ No → MINOR
```

---

#### **Critical Severity**
**Definition:** Blocks users from converting completely

**Examples:**
- CTA button doesn't work or isn't visible
- Page doesn't load on user's device
- User can't progress past a section (broken scroll/interaction)
- Major trust barrier ("This feels like a scam")

**Impact:** Zero users can convert (conversion rate = 0%)

**Decision Rule:** **MUST fix before launch**

**Fix Priority:** Drop everything, fix immediately

**Testing After Fix:**
- Re-test with 3+ users to confirm fix works
- If fix fails, launch is blocked

---

#### **Major Severity**
**Definition:** Causes significant drop-off or confusion, but some users still convert

**Examples:**
- 3+ users confused by Territory Map zones
- 3+ users don't understand what K2M offers
- 3+ users feel CTA is pressuring them
- Significant performance issue (page feels slow)

**Impact:** Conversion rate significantly reduced (50%+ drop potential)

**Decision Rule:** **SHOULD fix before launch** (only skip if running out of time and fix is complex)

**Fix Priority:** High priority, fix before minor polish

**Testing After Fix:**
- Re-test with 3+ users if time permits
- If no time for re-test, use best judgment + QA review

---

#### **Minor Severity**
**Definition:** Improvement opportunity, doesn't significantly impact conversion

**Examples:**
- Typo or grammar error
- Small visual inconsistency (padding, font size)
- 1-2 users find something slightly confusing (not a pattern)
- Nice-to-have feature request

**Impact:** Minimal impact on conversion (10% or less)

**Decision Rule:** **Nice to have if time permits**

**Fix Priority:** Low priority, polish after critical/major issues

**Testing After Fix:**
- No re-test needed (use QA review instead)

---

### 4.4 Issue Log Template

**Create a spreadsheet with these columns:**

| Column | Description | Example |
|--------|-------------|---------|
| **Issue ID** | Unique identifier (e.g., ISSUE-001) | ISSUE-001 |
| **Section** | Where issue occurred (Hero, Map, Discord, CTA, General) | Territory Map |
| **Problem** | Brief description of issue | Users confused by Zone 2 vs Zone 3 distinction |
| **# Users** | How many users reported this issue | 3 |
| **Category** | Confusion, Frustration, Disengagement, Misalignment, Technical, Trust | Confusion |
| **Severity** | Critical, Major, Minor | Major |
| **User Quotes** | Verbatim what users said (preserve their words) | "I'm not sure if I'm Zone 2 or Zone 3" / "What's the difference?" |
| **Suggested Fix** | Recommended solution | Add clearer examples for each zone / Merge zones if distinction isn't valuable |
| **Assigned To** | Who will fix (or TBD) | TBD |
| **Status** | Reported, In Progress, Fixed, Verified, Won't Fix | Reported |
| **Notes** | Additional context | Considered in design review - Zone distinction is intentional for personalization |

---

### 4.5 Decision Rules: What to Fix Before Launch

**Pre-Launch Blocking Criteria (Launch If Any Are Unresolved = BAD IDEA):**
- 1+ **Critical** issues unresolved → **BLOCKED**
- 3+ **Major** issues unresolved → **RISKY** (should fix)
- 1-2 **Major** issues unresolved → **PROCEED WITH CAUTION** (document known issues)

**Launch Readiness Checklist:**
```
✅ Zero Critical issues
✅ No more than 2 Major issues (and documented)
✅ All Major issues have workarounds documented
✅ At least 3 users completed all tasks successfully
✅ Average emotional rating ≥ 4.0 for all sections
✅ CTA click rate ≥ 80% (4/5 users clicked)
```

**If Launch Is Blocked:**
1. Fix Critical issues first
2. Re-test with 3+ users
3. If fix works → proceed to Major issues
4. If fix fails → launch blocked until resolved

**If You Must Launch With Known Issues:**
- Document issues in launch notes
- Add analytics tracking to monitor impact (Story 0.2)
- Plan hotfix timeline (e.g., "Known issue X, fixing Week 2 post-launch")
- Consider if issue affects target demographic (if not, may launch anyway)

---

## 5. Testing Schedule and Rounds

### 5.1 Round 1: Hero Section Testing

**Timing:** After Epic 1 (Hero section) is complete

**What's Tested:**
- Hero section only (opening text, value proposition, initial hook)
- Not testing Map, Discord, or CTA (not built yet)

**Why Test Hero First:**
- **Fail Fast:** If opening doesn't work emotionally, fix before investing in Map/Discord
- **Foundation:** Hero sets tone for entire page - if it's off, everything else suffers
- **Efficiency:** Easier to iterate on Hero alone than entire page

**Round 1 Goals:**
1. Validate emotional response: Do users feel "seen/understood"?
2. Test comprehension: Do users understand what K2M offers?
3. Check engagement: Do users read Hero or scroll past immediately?
4. Identify confusion: Any unclear copy or messaging?

**Success Criteria for Round 1:**
- 4/5 users rate Hero 4+ on emotional scale (80% pass rate)
- 4/5 users can explain what K2M offers in one sentence
- 3/5 users mention feeling "seen" or "understood" (60%+)
- Zero Critical issues, no more than 2 Major issues

**If Round 1 Fails:**
- Iterate on Hero (copy, design, messaging)
- Re-test with 3+ users
- Don't proceed to Epic 2 until Hero passes

**Round 1 Timeline:**
- **Prep (Day 1-2):** Recruit 5 users, schedule sessions, prepare script
- **Testing (Day 3-5):** Conduct 5 sessions (1-2 per day, 30-45 min each)
- **Analysis (Day 6):** Review recordings, compile findings, create issue log
- **Decision (Day 7):** Pass (proceed to Epic 2) or Fail (iterate on Hero)

**Total Round 1 Time:** ~1 week

---

### 5.2 Round 2: Full Page Testing

**Timing:** After Epic 3 (Hero + Map + Discord + CTA) is complete

**What's Tested:**
- Complete page: Hero → Map → Discord → CTA
- Full emotional journey: Confusion → Relief → Belonging → Action

**Why Test Full Page:**
- **Journey Validation:** Does emotional arc work end-to-end?
- **Integration Check:** Do sections flow together or feel disjointed?
- **Conversion Test:** Does full experience lead to CTA clicks?

**Round 2 Goals:**
1. Validate complete emotional journey (all sections)
2. Test Territory Map: Can users identify their zone?
3. Test Discord: Do users feel belonging?
4. Test CTA: Does it feel like invitation, not pressure?
5. Measure conversion readiness: Do users click CTA?

**Success Criteria for Round 2:**
- 4/5 users rate ALL sections 4+ on emotional scale (80% pass rate)
- 4/5 users can identify their zone confidently
- 4/5 users say "yes" to joining Discord community
- 4/5 users click CTA confidently (80% conversion readiness)
- Zero Critical issues, no more than 2 Major issues

**If Round 2 Fails:**
- Identify which section(s) failed (Hero? Map? Discord? CTA?)
- Iterate on failed sections
- Re-test with 3+ users
- Don't launch until Round 2 passes

**Round 2 Timeline:**
- **Prep (Day 1-2):** Recruit 5 users (can reuse Round 1 users or new users), schedule sessions
- **Testing (Day 3-5):** Conduct 5 sessions (45-60 min each - longer than Round 1)
- **Analysis (Day 6-7):** Review recordings, compile findings, create issue log
- **Decision (Day 8):** Pass (proceed to launch prep) or Fail (iterate and re-test)

**Total Round 2 Time:** ~1 week

---

### 5.3 Time Allocation per Round

**Per Testing Round:**

| Activity | Time | Notes |
|----------|------|-------|
| **Recruitment** | 2-3 hours | Post in groups, DM candidates, schedule sessions |
| **Session Prep** | 1 hour | Review script, test screen share, prepare spreadsheet |
| **Testing Sessions** | 2.5-3.75 hours | 5 users × 30-45 min each |
| **Data Analysis** | 2-3 hours | Watch recordings, transcribe quotes, compile issues |
| **Report Writing** | 1-2 hours | Create testing report, document findings |
| **TOTAL** | **8.5-12.75 hours** | ~1-1.5 days of focused work per round |

**Total Both Rounds:** 17-25.5 hours (~2-3 days total)

---

### 5.4 Tools Needed

**For Testing Sessions:**
- **Video Conferencing:** Zoom, Google Meet, or Microsoft Teams
  - Must support screen sharing
  - Must support recording (for later analysis)
- **Recording Software:** Built-in recording (Zoom/Meet) or Loom
  - For post-session analysis and quote extraction
- **Note-Taking:** Google Docs / Notion / Excel
  - Real-time notes during sessions
- **Data Collection:** Spreadsheet (see Section 7)

**For Recruitment:**
- **Communication:** WhatsApp, Twitter/X DM, Email
- **Scheduling:** Calendly / Google Calendar / Doodle
- **Incentive Delivery:** M-Pesa / mobile airtime codes

**Optional but Helpful:**
- **Timer:** To track time spent in each section
- **Screen Recording:** OBS or Loom (if platform recording fails)
- **Transcription:** Otter.ai or Rev (for quote extraction)

---

### 5.5 Testing Timeline

**Ideal Timeline (Assumes Epic 1 complete):**

```
Week 1: Epic 1 (Hero) complete
Week 2: Round 1 Testing (Hero only)
  ├─ Mon-Tue: Recruit 5 users, schedule sessions
  ├─ Wed-Fri: Conduct 5 testing sessions (1-2 per day)
  └─ Sat: Analyze results, make decision (Pass/Fail)

Week 3-4: Epic 2 & 3 (Map + Discord + CTA)
Week 5: Round 2 Testing (Full page)
  ├─ Mon-Tue: Recruit 5 users, schedule sessions
  ├─ Wed-Fri: Conduct 5 testing sessions
  └─ Sat: Analyze results, make decision (Pass/Fail)

Week 6: Launch prep / Final iterations (if Round 2 failed)
Week 7: LAUNCH 🚀
```

**Compressed Timeline (If Rushing):**
- Round 1: 3 days (recruit + test + analyze in same week)
- Epic 2-3: Continue as normal
- Round 2: 3 days
- **Total Testing Time:** 6 days (not 2 weeks)

**Note:** Compressed timeline is riskier - less time for recruitment, may not get ideal users, rushed analysis. Only use if deadline-pressed.

---

## 6. Test Session Script

### 6.1 Pre-Session Checklist

**Before Session Starts:**
- [ ] Test screen sharing works
- [ ] Test recording is enabled
- [ ] Have spreadsheet open for notes
- [ ] Have script open (this document)
- [ ] Test internet connection (both sides)
- [ ] Prepare incentive delivery (M-Pesa / airtime code ready)
- [ ] Check user's demographics (age, background) match target
- [ ] Verify user hasn't seen page before (fresh eyes)

---

### 6.2 Introduction (2 Minutes)

**Script (Read Aloud):**

> "Hi [Name]! Thanks so much for taking the time to help me today. I really appreciate it.
>
> **What we're doing:** I'm testing a landing page for K2M, an AI training program. I want to see how the page works for real people - what makes sense, what's confusing, how it makes you feel.
>
> **Important:** I'm testing the **page**, not you. There are no wrong answers. If something is confusing, that's a problem with the page, not you. Your honest feedback is exactly what I need.
>
> **How it works:** I'll share my screen and show you the page. As you look through it, I'd like you to **think out loud** - tell me what you're thinking, what you like, what confuses you, how you feel. If you go silent for a while, I might remind you to keep talking, and that's totally normal.
>
> **Timing:** This should take about 30-45 minutes. I'll ask you to do 5 tasks, and we'll talk through each one.
>
> **Questions:** Does this all make sense? Do you have any questions before we start?"

**What to Watch For:**
- User seems nervous? Reassure them: "Relax, this is low-stakes, just browsing a webpage"
- User asks "What's the right answer?" Remind them: "No right answers - your honest reaction is what I need"

---

### 6.3 Consent and Privacy (1 Minute)

**Script (Read Aloud):**

> "Before we start, a quick note on privacy:
>
> **Recording:** I'm recording this session so I can review it later and take notes on your feedback. Your responses are confidential and will only be used to improve the page.
>
> **Data:** I'm not collecting any personal information - just your thoughts and feedback on the page. Your name won't be associated with your responses in any reports.
>
> **Voluntary:** If at any point you want to stop, just say so and we'll end the session. No questions asked.
>
> **Questions:** Are you comfortable with the recording? Any concerns about privacy?"

**If User Asks Questions:**
- **"Who will see this?"** → Just me and the K2M team for improving the page
- **"Will my name be used?"** → No, your responses are anonymous in reports
- **"What if I say something negative?"** → That's exactly what I need - honest feedback

---

### 6.4 Task Instructions (20-30 Minutes)

**Say Before Tasks:**

> "Alright, let's dive in! I'll share my screen now. As you go through the page, remember to **think out loud** - tell me what you're thinking, what you notice, what you like or don't like. There are no wrong answers.
>
> Ready? Here's your first task:"

[Then read each task from Section 2.2 - Tasks 1 through 5]

**During Tasks:**
- Take notes in spreadsheet (real-time)
- Don't interrupt unless user goes silent for 30+ seconds
- If user goes silent: "Keep telling me what you're thinking"
- Avoid leading questions ("Did that confuse you?" → "What did you think of that?")

---

### 6.5 Debrief Questions (5-10 Minutes)

**After All 5 Tasks, Ask:**

> "Great, you made it through the page! Now I have a few debrief questions:
>
> 1. **What almost stopped you from clicking the CTA button?**
>    (Wait for response)
>
> 2. **What was the most confusing part of the page?**
>    (Wait for response)
>
> 3. **What did you like the most?**
>    (Wait for response)
>
> 4. **If you could change one thing about the page, what would it be?**
>    (Wait for response)
>
> 5. **Would you actually join K2M after seeing this page? Why or why not?**
>    (Wait for response - this is the BIG question)
>
> Thanks for those honest answers - this is super helpful!"

**What to Watch For:**
- User hesitates on Q5? → Maybe not actually convinced
- User says "yes" but unenthusiastically? → Probe deeper: "What would make you more excited?"
- User says "no"? → Critical finding - ask why

---

### 6.6 Closing (2 Minutes)

**Script (Read Aloud):**

> "That's it - we're done! Thanks so much for your help, [Name]. Your feedback is going to make this page way better.
>
> **Next steps:** I'll analyze your feedback along with 4 other users' responses, identify patterns, and make improvements to the page based on what you all said.
>
> **Incentive:** As a thank you, I'll send you [INCENTIVE: 500 KES airtime / free diagnostic access] within the next 24 hours. Look out for a message from [PLATFORM: WhatsApp / Email].
>
> **Contact:** If you have any questions later, feel free to reach out to me at [YOUR CONTACT].
>
> Thanks again - really appreciate your time and honesty!"

**After Session Ends:**
- Send incentive immediately (if possible)
- Send follow-up message with incentive confirmation
- Store recording with user ID (anonymous label: User_01, User_02, etc.)

---

## 7. Data Collection Templates

### 7.1 User Feedback Spreadsheet

**Create a spreadsheet with these tabs:**

**Tab 1: Session Data (One Row Per User)**

| Column | Description | Example |
|--------|-------------|---------|
| **User ID** | Anonymous identifier | User_01 |
| **Date** | Session date | 2026-01-15 |
| **Age** | User's age (18-30) | 22 |
| **Location** | User's city (Nairobi, Kisumu, etc.) | Nairobi |
| **Tech Background** | Technical, Non-technical, Somewhat technical | Somewhat technical |
| **AI Experience** | Never used AI / Used ChatGPT / Used AI tools | Used ChatGPT |
| **Hero Rating** | Emotional scale 1-5 | 5 |
| **Map Zone Selected** | Which zone they chose (0-4) | Zone 2 |
| **Map Confidence** | Confident / Hesitant / Very Hesitant | Confident |
| **Map Rating** | Emotional scale 1-5 | 4 |
| **Discord Join** | Yes / No / Maybe | Yes |
| **Discord Rating** | Emotional scale 1-5 | 5 |
| **CTA Click** | Yes / No | Yes |
| **CTA Time to Click** | Seconds (0-5, 5-10, 10+) | 0-5 seconds |
| **CTA Feeling** | Invitation / Pressure / Neutral / Fear | Invitation |
| **CTA Rating** | Emotional scale 1-5 | 4 |
| **Key Quotes** | Best quotes (preserve user's words) | "Finally, someone gets it" |
| **Issues Identified** | List of issues (comma-separated) | Zone confusion, CTA unclear |
| **Would Join K2M** | Yes / No / Maybe | Yes |
| **Overall Impression** | Free-text summary | "Liked the community aspect" |
| **Notes** | Any additional observations | Very engaged, smiled throughout |

---

**Tab 2: Issue Log (Aggregated Across All Users)**

See template in Section 4.4

---

**Tab 3: Quotes (Emotional Responses)**

| Quote | User ID | Section | Sentiment | Use in Report? |
|-------|---------|---------|-----------|---------------|
| "Finally, someone gets it" | User_01 | Hero | Positive | ✅ Yes |
| "I don't know which zone I'm in" | User_02 | Map | Negative | ✅ Yes |
| "I'd want to join this community" | User_03 | Discord | Positive | ✅ Yes |

**Purpose:**
- Capture authentic user voices
- Use in report to make findings vivid
- Reference when convincing stakeholders to fix issues

---

### 7.2 Issue Log Template

**Create a dedicated issue log spreadsheet:**

See full template in Section 4.4

**Key Fields:**
- Issue ID (e.g., ISSUE-001)
- Section (Hero, Map, Discord, CTA)
- Problem (brief description)
- # Users (how many reported)
- Category (Confusion, Frustration, etc.)
- Severity (Critical, Major, Minor)
- User Quotes (verbatim)
- Suggested Fix
- Status (Reported, In Progress, Fixed, Verified, Won't Fix)

**How to Use:**
1. Add issues as they emerge during testing
2. After all 5 users, review and aggregate
3. Mark patterns (3+ users = pattern)
4. Prioritize by severity
5. Assign to developers or TBD

---

### 7.3 Testing Report Template

**Report Structure (9 Sections):**

---

**# User Testing Report: K2M Landing Page**

**Testing Round:** [Round 1 / Round 2]
**Date Range:** [Start Date] - [End Date]
**Number of Users:** [5]
**Facilitator:** [Your Name]

---

## 1. Executive Summary

**Pass/Fail Status:** [✅ PASS / ❌ FAIL / ⚠️ PASS WITH ISSUES]

**Key Findings:**
- [Finding 1: e.g., "Hero section succeeds - 4/5 users felt 'seen'"]
- [Finding 2: e.g., "Territory Map needs work - 3/5 users confused by zones"]
- [Finding 3: e.g., "Discord section resonates - 5/5 would join community"]

**Recommendation:**
- [If PASS:] "Proceed to next epic / Proceed to launch"
- [If FAIL:] "Iterate on [section] before proceeding"

---

## 2. Methodology

**Testing Method:** Remote screen share + think-aloud protocol

**Users:**
- **Demographic:** Kenyan students interested in AI, ages 18-30
- **Sample Size:** 5 users
- **Recruitment:** [Channels: e.g., University AI clubs, Twitter/X, WhatsApp]
- **Incentive:** 500 KES airtime OR free diagnostic access

**Tasks:**
1. Natural scroll through page
2. Identify Territory Map zone
3. Explain what K2M offers (one sentence)
4. Rate each section emotionally (1-5 scale)
5. Click CTA button

**Duration:** 30-45 minutes per user

---

## 3. Results by Section

### 3.1 Hero Section

**Emotional Rating:** [Average 1-5] / 5
- User 1: [Rating] - "[Quote]"
- User 2: [Rating] - "[Quote]"
- User 3: [Rating] - "[Quote]"
- User 4: [Rating] - "[Quote]"
- User 5: [Rating] - "[Quote]"

**Key Findings:**
- [Finding 1: e.g., "4/5 users used words like 'seen', 'finally', 'relieved'"]
- [Finding 2: e.g., "All users understood what K2M offers"]

**Issues Identified:**
- [Issue 1 (if any)]

**Verdict:** [✅ PASS / ❌ NEEDS WORK]

---

### 3.2 Territory Map

**Zone Selection:**
- Zone 0: [0 users]
- Zone 1: [1 user]
- Zone 2: [3 users]
- Zone 3: [1 user]
- Zone 4: [0 users]

**Confidence Level:**
- Confident: [X/5]
- Hesitant: [X/5]

**Emotional Rating:** [Average 1-5] / 5

**Key Findings:**
- [Finding 1]

**Issues Identified:**
- [Issue 1]

**Verdict:** [✅ PASS / ❌ NEEDS WORK]

---

### 3.3 Discord Section

**Would Join Community:** [X/5] Yes

**Emotional Rating:** [Average 1-5] / 5

**Key Findings:**
- [Finding 1]

**Issues Identified:**
- [Issue 1]

**Verdict:** [✅ PASS / ❌ NEEDS WORK]

---

### 3.4 CTA Section

**Click Rate:** [X/5] clicked ([X%])

**Time to Click:**
- 0-5 seconds: [X/5]
- 5-10 seconds: [X/5]
- 10+ seconds: [X/5]

**Feeling Reported:**
- Invitation: [X/5]
- Pressure: [X/5]
- Neutral: [X/5]
- Fear: [X/5]

**Emotional Rating:** [Average 1-5] / 5

**Key Findings:**
- [Finding 1]

**Issues Identified:**
- [Issue 1]

**Verdict:** [✅ PASS / ❌ NEEDS WORK]

---

## 4. Issue Log

**Critical Issues:** [X]
- [Issue 1]

**Major Issues:** [X]
- [Issue 1]

**Minor Issues:** [X]
- [Issue 1]

**Full Issue Log:** [See attached spreadsheet]

---

## 5. Emotional Response Analysis

**Hero - Target Emotion:** Relief, seen, understood
- **Achieved?** [Yes / No / Partially]
- **Supporting Quotes:**
  - "[Quote 1]"
  - "[Quote 2]"
  - "[Quote 3]"

**Territory Map - Target:** Clear zone identification
- **Achieved?** [Yes / No / Partially]
- **Supporting Quotes:**
  - "[Quote]"

**Discord - Target:** Belonging, community
- **Achieved?** [Yes / No / Partially]
- **Supporting Quotes:**
  - "[Quote]"

**CTA - Target:** Relief, not pressure
- **Achieved?** [Yes / No / Partially]
- **Supporting Quotes:**
  - "[Quote]"

---

## 6. Recommendations

**Before Launch (Critical):**
1. [Fix 1]
2. [Fix 2]

**Before Launch (Major - Should Fix):**
1. [Fix 1]
2. [Fix 2]

**Nice to Have (Minor):**
1. [Fix 1]

**Launch Decision:**
- [If all Critical fixed:] ✅ **PROCEED TO LAUNCH**
- [If Critical unresolved:] ❌ **BLOCKED - Fix Critical issues first**

---

## 7. Appendix

**A. User Demographics**
- [Demographic breakdown]

**B. Raw Data**
- [Link to spreadsheet with all user responses]

**C. Session Recordings**
- [Link to folder with recordings]

**D. Quotes (Full List)**
- [All notable quotes organized by section]

---

## 8. Recruitment Strategy

### 8.1 Target Demographic Details

**Who We Need:**
- **Age:** 18-30 (primary: 20-26, university age)
- **Location:** Kenya (Nairobi, Kisumu, Mombasa, other major cities)
- **Education:** Some university or university degree
- **Background:**
  - Interested in AI / tech
  - Have used ChatGPT or similar AI tools
  - Don't feel in control of AI (confused by it)
  - Want to learn more but don't know where to start
- **Device:** Mobile phone users (Android, budget devices)
- **Internet:** 3G/4G connections (may have limited data)

**Who We DON'T Need:**
- Professional software developers (too technical)
- People outside Kenya (wrong cultural context)
- People who've never heard of AI (too far behind)
- K2M team members, friends, or family (biased)

**Diversity Goals:**
- Mix of technical (CS students) and non-technical (business, arts) backgrounds
- Mix of ages (18-22, 23-26, 27-30)
- Mix of cities (not all Nairobi)
- Gender balance (aim for ~50/50 if possible)

---

### 8.2 Recruitment Channels

**Channel 1: University AI/Tech Clubs (Best Source)**

**Why:**
- Target demographic congregates here
- Students interested in AI join these clubs
- Community trust = higher response rate

**How:**
1. Identify clubs: University of Nairobi AI Club, Strathmore Tech Club, JKUAT Developers, etc.
2. Find contact: Club president, WhatsApp group admin, Twitter/X account
3. Message: "Hi, I'm working on K2M, an AI training program for Kenyan students. We're looking for 5 students to test our landing page and give feedback. 30-45 minutes, remote, 500 KES airtime incentive. Interested?"

**Expected Response:** 5-10 responses per club contacted

---

**Channel 2: Twitter/X Kenyan Tech Community**

**Why:**
- Kenyan tech Twitter is active
- AI discussions happening here
- Direct DMs work well

**How:**
1. Search: "Kenya AI", "Kenyan tech students", "ChatGPT Kenya"
2. Identify users matching demographic (check bio: student, Kenya, AI/tech interest)
3. Follow and DM: "Hi [Name], saw you're interested in AI. I'm building K2M, an AI training program for Kenyan students. Looking for testers for our landing page - 30 min, remote, 500 KES airtime. Interested?"

**Expected Response:** 2-5 responses per 10 DMs

---

**Channel 3: WhatsApp Groups (Students, Tech Communities)**

**Why:**
- High engagement in Kenya
- Students active in WhatsApp groups
- Personal connections help

**How:**
1. Join groups: University class groups, AI/tech WhatsApp groups
2. Post message (with group admin permission): "Hi everyone! Building K2M (AI training program). Looking for 5 students to test our landing page - 30 min, remote, 500 KES airtime. DM if interested!"
3. Respond to interested users directly

**Expected Response:** 3-7 responses per group post

**Note:** Always ask group admin permission first (don't spam)

---

**Channel 4: Referrals (Snowball Sampling)**

**Why:**
- Trust-based recruitment = higher quality
- Friends refer friends with similar interests

**How:**
1. After first 1-2 users tested, ask: "Do you know anyone else who might be interested in this? We need 2-3 more testers."
2. Provide referral message they can forward: "Hey, testing this AI training landing page - 30 min, 500 KES airtime. Want in?"
3. Respond to referrals directly

**Expected Response:** 1-3 referrals per user

---

### 8.3 Incentive Structure

**Option 1: 500 KES Mobile Airtime (Recommended)**

**Why:**
- Immediate value (user can use right away)
- Universal appeal (everyone uses mobile airtime)
- Easy to deliver (M-Pesa, SMS)
- Low friction (no bank account needed)

**How to Deliver:**
- Safaricom: Buy airtime via M-Pesa (MPESA → Buy Airtime → Enter Number)
- Airtel/Telkom: Buy via respective platforms or resellers
- Send confirmation message: "Hi [Name], thanks for testing! 500 KES airtime sent to [phone number]. Check your balance and confirm received?"

**Cost:** 500 KES × 5 users = 2,500 KES (~$20 USD) per round

**Pros:** ✅ Immediate, ✅ Universal, ✅ Easy to deliver
**Cons:** ❌ Recurring cost if testing multiple rounds

---

**Option 2: Free Diagnostic Access (Value-Based)**

**Why:**
- No direct cost (giving away product access)
- Aligned with K2M value proposition
- Converts testers to potential users

**How to Deliver:**
- Create unique code for each tester: `K2M-TEST-USER01`
- Send message: "Hi [Name], thanks for testing! Here's your free access to K2M diagnostic. Use code [CODE] at [URL]. Let me know if you have questions!"
- Track code usage in analytics

**Cost:** 0 KES direct cost (opportunity cost of giving away product)

**Pros:** ✅ No direct cost, ✅ Converts testers to users
**Cons:** ❌ Not immediate value (user has to complete diagnostic), ❌ Only valuable if user actually wants diagnostic

---

**Option 3: 500 KES Airtime OR Free Diagnostic (Let User Choose)**

**Why:**
- Gives user agency
- Covers both motivation types (immediate vs long-term value)

**How to Deliver:**
- Ask during scheduling: "As a thank you, I can offer you 500 KES airtime OR free access to K2M diagnostic (worth [VALUE]). Which would you prefer?"
- Deliver chosen incentive

**Cost:** Variable (some choose airtime, some choose diagnostic)

**Pros:** ✅ User choice, ✅ Covers both motivations
**Cons:** ❌ Slightly more complex logistics

---

**Recommendation:** Use **Option 1 (500 KES airtime)** for simplicity and immediate value. If budget is tight, use **Option 3 (let user choose)** to convert some testers to users without direct cost.

---

### 8.4 Screening Questions

**Before Confirming User, Ask:**

1. **"Are you interested in learning about AI?"**
   - Yes → ✅ Continue
   - No → ❌ Not target demographic

2. **"Have you used ChatGPT or similar AI tools before?"**
   - Yes → ✅ Continue
   - No → ❌ Too early in journey (not target demographic)

3. **"Do you feel confused by AI or like you don't fully understand how it works?"**
   - Yes → ✅ Perfect fit (target emotional state)
   - No → ❌ Too advanced (not target demographic)

4. **"Are you a professional software developer or AI engineer?"**
   - Yes → ❌ Too technical (not target demographic)
   - No → ✅ Continue

5. **"Can you commit 30-45 minutes for a remote session on [date/time]?"**
   - Yes → ✅ Schedule session
   - No → ❌ Find different time or different user

6. **"Do you have a laptop/phone with internet and can you share your screen on Zoom/Google Meet?"**
   - Yes → ✅ Confirm session
   - No → ❌ Can't complete test (need screen share)

**If User Passes All Screens:**
- Schedule session via Calendly or Google Calendar
- Send calendar invite with Zoom/Meet link
- Send reminder 24 hours before and 1 hour before

---

### 8.5 Recruitment Email/DM Templates

**Template 1: Initial Outreach (Twitter/X DM)**

```
Hi [Name]! 👋

Saw you're interested in AI / tech. I'm building K2M, an AI training program for Kenyan students, and we're looking for 5 people to test our landing page.

**What:** 30-45 minute session - you'll browse the page and give feedback
**Where:** Remote (Zoom/Google Meet) - from your phone/laptop
**When:** [Date range] - flexible scheduling
**Incentive:** 500 KES airtime as a thank you 🎁

**Who we're looking for:**
- Kenyan students (ages 18-30)
- Interested in AI but confused by it
- Have used ChatGPT but want to understand it better

Interested? Reply "YES" and I'll send scheduling info!

Thanks!
[Your Name]
```

---

**Template 2: WhatsApp Group Post (With Admin Permission)**

```
Hey everyone! 👋

Quick favor: I'm building K2M (an AI training program for Kenyan students) and looking for 5 people to test our landing page.

**The deal:**
- 30-45 minutes
- Remote (Zoom/Google Meet)
- You browse the page, tell us what you think
- 500 KES airtime as thank you 🎁

**Looking for:**
- Kenyan students (18-30)
- Interested in AI but confused by it
- Used ChatGPT before

Interested? DM me and I'll share scheduling info!

Thanks! 🙏
[Your Name]
```

---

**Template 3: University Club Outreach (Email/DM to Club President)**

```
Hi [Name],

Hope you're doing well! I'm [Your Name], building K2M - an AI training program for Kenyan students.

I'm looking for 5 students to test our landing page and give feedback. 30-45 minutes, remote, 500 KES airtime incentive.

Would you be open to sharing this opportunity with your club members? I can provide a flyer/message you can post in your WhatsApp group or social media.

Let me know if that works! Happy to answer any questions about K2M.

Best,
[Your Name]
```

---

**Template 4: Scheduling Confirmation**

```
Hi [Name],

Great, you're in! 🎉

**Session Details:**
- Date: [Date]
- Time: [Time] (EAT)
- Platform: [Zoom/Google Meet]
- Link: [Link]

**Before the session:**
- Test your screen sharing works
- Find a quiet spot (30-45 minutes)
- Bring your honest feedback (no wrong answers!)

**Incentive:** 500 KES airtime sent after session 🎁

See you then! Let me know if you need to reschedule.

Thanks!
[Your Name]
```

---

**Template 5: Reminder (24 Hours Before)**

```
Hi [Name],

Just a reminder - our session is tomorrow at [Time] EAT!

Link: [Zoom/Google Meet Link]

Looking forward to your feedback. See you then! 👋

[Your Name]
```

---

## 9. Testing Report Format

### 9.1 Report Purpose

**Who Is This Report For?**
- **Primary:** K2M product owner / stakeholders (decide launch/iterate)
- **Secondary:** Development team (know what to fix)
- **Tertiary:** Archive for future reference (what worked, what didn't)

**What Should It Achieve?**
1. **Clear pass/fail decision** (can we launch or not?)
2. **Actionable recommendations** (what to fix, in what order)
3. **Evidence-backed findings** (user quotes, data)
4. **Emotional impact assessment** (not just technical bugs)

---

### 9.2 Report Structure (9 Sections)

**See full template in Section 7.3**

**Key Sections Overview:**

1. **Executive Summary:** Pass/fail, key findings, recommendation (1 page)
2. **Methodology:** How we tested, who we tested, tasks (1 page)
3. **Results by Section:** Hero, Map, Discord, CTA - ratings, findings, verdict (2-3 pages)
4. **Issue Log:** Critical, Major, Minor issues with priority (1 page)
5. **Emotional Response Analysis:** Did we achieve target emotions? (1 page)
6. **Recommendations:** What to fix before launch (1 page)
7. **Appendix:** Demographics, raw data, recordings link (1 page)

**Total Length:** 8-10 pages (comprehensive but scannable)

---

### 9.3 Writing the Report

**Step 1: Compile Data (1-2 hours)**

After all 5 sessions completed:
1. Review all session recordings
2. Fill in User Feedback Spreadsheet (Section 7.1)
3. Aggregate Issue Log (Section 7.2)
4. Extract best quotes for each section
5. Calculate averages (emotional ratings, click rates)

---

**Step 2: Write Executive Summary (30 minutes)**

**Template:**

```
# Executive Summary

**Testing Round:** [Round 1 / Round 2]
**Date:** [Date]
**Users:** [5]
**Status:** [✅ PASS / ❌ FAIL / ⚠️ PASS WITH ISSUES]

## Key Findings

1. [Section] succeeded - [key stat]
   Example: "Hero section succeeded - 4/5 users felt 'seen' or 'understood'"

2. [Section] needs work - [key stat]
   Example: "Territory Map needs work - 3/5 users confused by zones"

3. [Section] succeeded - [key stat]
   Example: "Discord section resonates - 5/5 would join community"

## Recommendation

[If all sections pass:] "✅ Proceed to [next epic / launch] - all emotional criteria met"

[If 1+ sections fail:] "❌ Iterate on [failed section] before proceeding. [X/5] users reported [key issue], which blocks conversion."

[If mixed results:] "⚠️ Proceed with caution - [section] needs work but isn't blocking. Address [X] major issues before launch."

## Launch Readiness

- Emotional targets met: [X/4] sections
- Critical issues: [X] (must be 0 to launch)
- Major issues: [X] (should be ≤2 to launch)
- CTA click rate: [X%] (target: 80%+)
```

---

**Step 3: Write Results by Section (1-2 hours)**

**For each section (Hero, Map, Discord, CTA), include:**

1. **Emotional Ratings:** Table of user ratings
2. **Key Quotes:** 2-3 best quotes (preserve user's words)
3. **Findings:** 3-5 bullet points of patterns
4. **Issues:** Any issues identified (if none, say "No issues")
5. **Verdict:** ✅ PASS or ❌ NEEDS WORK

**Example (Hero Section):**

```
### 3.1 Hero Section

**Emotional Rating:** 4.6 / 5

| User | Rating | Quote |
|------|--------|-------|
| User_01 | 5 | "Finally, someone gets it" |
| User_02 | 5 | "I feel seen" |
| User_03 | 4 | "This is exactly how I feel" |
| User_04 | 5 | "Relieved to know I'm not the only one" |
| User_05 | 4 | "Interesting, I want to keep reading" |

**Key Findings:**
- 4/5 users used words like "seen", "finally", "relieved" ✅
- All users understood what K2M offers ✅
- Users spent meaningful time on Hero (didn't scroll past) ✅
- No confusion reported ✅

**Issues Identified:** None

**Verdict:** ✅ PASS
```

---

**Step 4: Write Emotional Response Analysis (30 minutes)**

**For each section, answer:**
1. Target emotion (what we wanted)
2. Achieved? (Yes/No/Partially)
3. Supporting quotes (evidence)

**Example:**

```
## 5. Emotional Response Analysis

### Hero - Target Emotion: Relief, Seen, Understood

**Achieved?** ✅ Yes

**Evidence:**
- User_01: "Finally, someone gets it"
- User_02: "I feel seen"
- User_04: "Relieved to know I'm not the only one"
- 4/5 users explicitly mentioned feeling "seen" or "understood"

### Territory Map - Target: Clear Zone Identification

**Achieved?** ⚠️ Partially

**Evidence:**
- 3/5 users identified zone confidently ✅
- 2/5 users hesitated between Zone 2 and Zone 3 ❌
- User_03: "I'm not sure if I'm Zone 2 or Zone 3"
- User_05: "What's the difference between Zone 1 and Zone 2?"

**Verdict:** Zone distinction unclear - needs work
```

---

**Step 5: Write Recommendations (30 minutes)**

**Organize by severity:**

```
## 6. Recommendations

### Before Launch (Critical - Must Fix)

None ✅

### Before Launch (Major - Should Fix)

1. **Territory Map: Clarify Zone Distinctions**
   - **Issue:** 2/5 users confused by Zone 2 vs Zone 3
   - **Fix:** Add concrete examples for each zone (e.g., "Zone 2: Used ChatGPT for homework but don't understand how it works")
   - **Impact:** Will improve self-identification confidence from 60% to 80%+

2. **CTA: Clarify What Happens After Click**
   - **Issue:** 1/5 user asked "What am I committing to?"
   - **Fix:** Add microcopy under CTA: "No commitment - just start the diagnostic"
   - **Impact:** Will reduce conversion friction

### Nice to Have (Minor - Polish If Time)

1. **Hero: Shorten Opening Sentence**
   - **Issue:** 1/5 user mentioned "a bit long"
   - **Fix:** Cut 3-4 words from opening sentence
   - **Impact:** Minor improvement, not blocking

## Launch Decision

✅ **PROCEED TO LAUNCH**

**Rationale:**
- All emotional targets met (Hero ✅, Map ⚠️, Discord ✅, CTA ✅)
- Zero Critical issues
- 2 Major issues identified (both fixable in <1 day)
- CTA click rate: 80% (4/5 users - meets target)
- Overall emotional rating: 4.4/5 (exceeds 4.0 target)

**Condition:** Address 2 Major issues before launch (estimated 2-4 hours work)
```

---

**Step 6: Review and Refine (30 minutes)**

Before finalizing report:
1. **Check for bias:** Are you over-emphasizing negative feedback? Balance with positive.
2. **Verify quotes:** Are quotes accurate? Don't misrepresent users.
3. **Check clarity:** Would a non-technical stakeholder understand this?
4. **Confirm recommendations:** Are recommendations actionable? (Not "fix UX" → "add copy under CTA")

**Peer Review (Optional):**
- Send report to colleague for sanity check
- Ask: "Does this make sense? Am I missing anything?"

---

**Step 7: Distribute Report**

**Send To:**
- K2M product owner / stakeholder
- Development team
- Project manager / Scrum master

**Format:**
- PDF (for reading)
- Google Doc (for comments/collaboration)
- Appendix: Link to spreadsheet + recordings (for deep dive)

**Follow-Up:**
- Schedule meeting to discuss findings
- Present executive summary (5 minutes)
- Discuss recommendations and next steps
- Decide: Launch / Iterate / Hold

---

## 10. Alignment with Story 0.1 Metrics

### 10.1 Story 0.1 Emotional Success Criteria

**From Story 0.1 (conversion-metrics.md Section 4):**

| Section | Target Emotion | How to Measure |
|---------|---------------|----------------|
| **Hero** | Relief, seen, understood | User says "finally", "seen", "relieved" |
| **Territory Map** | Clear zone identification | User identifies zone confidently in <10 sec |
| **Discord** | Belonging, community | User says "yes" to joining |
| **CTA** | Relief, not pressure | User clicks confidently, says "invitation" |

**This User Testing Protocol (Story 0.3) validates exactly these emotional criteria.**

---

### 10.2 Mapping Story 0.1 to Test Questions

**Story 0.1 Criterion:** "Hero section: User reports feeling 'seen' or 'validated'"

**Story 0.3 Test Validation:**
- **Task 4 (Emotional Rating):** User rates Hero 1-5 on emotional scale
- **Target:** 4+ rating (includes "seen", "understood", "relieved")
- **Follow-Up Question:** "How does this opening make you feel?"
- **Success:** User uses words like "seen", "finally", "relieved", "me too"

---

**Story 0.1 Criterion:** "Territory Map: User can identify their current zone (0-4)"

**Story 0.3 Test Validation:**
- **Task 2 (Map Zone Selection):** "Which zone do you feel you're in right now? Why?"
- **Target:** Chooses zone within 10 seconds (confident)
- **Follow-Up:** Can explain why they chose that zone
- **Success:** Clear identification without asking for clarification

---

**Story 0.1 Criterion:** "Discord section: User feels 'belonging' or 'community'"

**Story 0.3 Test Validation:**
- **Task 4 (Emotional Rating):** User rates Discord 1-5
- **Target:** 4+ rating (includes "belonging", "community")
- **Follow-Up Question:** "Would you want to join this community?"
- **Success:** User says "yes" or "definitely"

---

**Story 0.1 Criterion:** "CTA section: User feels 'relief' not 'pressure'"

**Story 0.3 Test Validation:**
- **Task 4 (Emotional Rating):** User rates CTA 1-5
- **Target:** 4+ rating (includes "relief", "invitation")
- **Task 5 (CTA Click):** Clicks CTA confidently
- **Follow-Up Question:** "Does this feel like pressure or an invitation?"
- **Success:** User says "invitation", clicks confidently (no hesitation)

---

### 10.3 Ensuring Complete Coverage

**Checklist: All Story 0.1 Emotional Criteria Have Test Questions**

- [x] Hero: "seen/validated" → Task 4 rating + "How does this make you feel?"
- [x] Map: "identify zone" → Task 2 zone selection + confidence level
- [x] Discord: "belonging" → Task 4 rating + "Would you join?"
- [x] CTA: "relief not pressure" → Task 4 rating + Task 5 click + "pressure or invitation?"

**Verification:** ✅ All 4 Story 0.1 emotional criteria are validated by Story 0.3 test questions.

---

### 10.4 Quantitative vs Qualitative Validation

**Story 0.1 (conversion-metrics.md):**
- Defines WHAT success looks like (emotional criteria)
- Sets targets (e.g., 4/5 users feel "seen")

**Story 0.2 (analytics-setup.md):**
- Measures QUANTITATIVE behavior (scroll depth, clicks, time on page)
- Complements qualitative testing with hard data

**Story 0.3 (user-testing-protocol.md):**
- Measures QUALITATIVE response (emotions, confusion, reactions)
- Validates the emotional criteria from Story 0.1

**Together:**
- Story 0.1: Defines success
- Story 0.2: Measures behavior (what users do)
- Story 0.3: Measures emotions (why users do it)

**Example:**
- Story 0.1: "CTA should feel like relief, not pressure"
- Story 0.2: Analytics tracks CTA clicks (quantitative: 80% clicked)
- Story 0.3: User testing asks "pressure or invitation?" (qualitative: 4/5 said "invitation")

**Both are needed:**
- High CTA click rate (Story 0.2) + "invitation" feeling (Story 0.3) = ✅ Success
- High CTA click rate (Story 0.2) + "pressure" feeling (Story 0.3) = ⚠️ Concern (users converting under pressure = churn risk)

---

## Appendix: Templates and Resources

### A.1 User Feedback Spreadsheet Template

**Downloadable template structure (see Section 7.1 for full details):**

**Tab 1: Session Data**
- Columns: User ID, Date, Age, Location, Tech Background, AI Experience, Hero Rating, Map Zone, Map Confidence, Map Rating, Discord Join, Discord Rating, CTA Click, CTA Time to Click, CTA Feeling, CTA Rating, Key Quotes, Issues, Would Join K2M, Overall Impression, Notes

**Tab 2: Issue Log**
- Columns: Issue ID, Section, Problem, # Users, Category, Severity, User Quotes, Suggested Fix, Assigned To, Status, Notes

**Tab 3: Quotes**
- Columns: Quote, User ID, Section, Sentiment, Use in Report?

**Format:** Google Sheets or Excel

---

### A.2 Issue Log Template

**See Section 4.4 for full template**

**Columns:**
- Issue ID
- Section
- Problem
- # Users
- Category (Confusion, Frustration, Disengagement, Misalignment, Technical, Trust)
- Severity (Critical, Major, Minor)
- User Quotes
- Suggested Fix
- Assigned To
- Status

**Format:** Google Sheets or Excel

---

### A.3 Testing Report Template

**See Section 7.3 for full template**

**Sections:**
1. Executive Summary
2. Methodology
3. Results by Section (Hero, Map, Discord, CTA)
4. Issue Log
5. Emotional Response Analysis
6. Recommendations
7. Appendix

**Format:** Google Doc or Markdown

---

### A.4 Recruitment Message Templates

**See Section 8.5 for templates:**

1. Initial outreach (Twitter/X DM)
2. WhatsApp group post
3. University club outreach
4. Scheduling confirmation
5. Reminder (24 hours before)

**Format:** Copy-paste ready

---

### A.5 Test Session Script

**See Section 6 for full script:**

- Introduction (2 min)
- Consent and privacy (1 min)
- Task instructions (20-30 min)
- Debrief questions (5-10 min)
- Closing (2 min)

**Format:** Read-aloud script

---

### A.6 Screening Questions

**See Section 8.4 for full list:**

1. Interested in AI?
2. Used ChatGPT before?
3. Feel confused by AI?
4. NOT a professional developer?
5. Can commit 30-45 min?
6. Can share screen?

**Format:** Ask during recruitment call/DM

---

### A.7 Emotional Rating Scale (Show User)

**Print or screen-share during Task 4:**

```
1 - Confused, frustrated, annoyed
2 - Skeptical, unsure, indifferent
3 - Neutral, no strong feeling
4 - Interested, curious, hopeful
5 - Understood, seen, relieved, excited
```

**Format:** Show on screen during session

---

### A.8 Testing Checklist

**Before Testing Round:**
- [ ] Test script reviewed
- [ ] Spreadsheet templates created
- [ ] Recruitment messages sent
- [ ] 5 users recruited and scheduled
- [ ] Incentives prepared (M-Pesa ready, airtime codes purchased)
- [ ] Screen sharing tested
- [ ] Recording tested
- [ ] Zoom/Meet links created

**During Testing Sessions:**
- [ ] Introduction script read
- [ ] Consent obtained
- [ ] Tasks 1-5 completed
- [ ] Notes taken in real-time
- [ ] Debrief questions asked
- [ ] Recording saved
- [ ] Incentive sent

**After Testing Round:**
- [ ] All 5 sessions completed
- [ ] Spreadsheet filled out
- [ ] Issue log aggregated
- [ ] Quotes extracted
- [ ] Report written
- [ ] Findings presented to stakeholders
- [ ] Decision made (Pass/Fail)
- [ ] Next steps planned

---

## Conclusion

**This user testing protocol provides:**

✅ **Clear methodology** for validating emotional response
✅ **Structured tasks** to observe natural user behavior
✅ **Section-specific validation** to test each emotional target
✅ **Issue flagging protocol** to prioritize fixes (3+ users = pattern)
✅ **Two testing rounds** to fail fast (Hero) and validate journey (full page)
✅ **Session script** for consistent facilitation
✅ **Data collection templates** for organized analysis
✅ **Recruitment strategy** to find target demographic (Kenyan students)
✅ **Testing report format** to communicate findings clearly
✅ **Alignment with Story 0.1** to validate emotional success criteria

**Next Steps:**
1. Use this protocol for Round 1 (after Epic 1)
2. Use this protocol for Round 2 (after Epic 3)
3. Combine findings with Story 0.2 analytics data
4. Make launch decision based on emotional + quantitative data

**Remember:** We're not building a technically perfect page - we're building an emotionally resonant experience. User testing is the only way to validate emotional response. Analytics shows WHAT users do; user testing shows WHY they do it. Both are needed for success.

---

**Document End**

**For questions or clarifications, refer to:**
- Story 0.1: conversion-metrics.md (defines emotional success criteria)
- Story 0.2: analytics-setup.md (defines quantitative tracking)
- Story 0.3: user-testing-protocol.md (this document - validates emotional response)
- epics.md: lines 225-262 (source of Story 0.3 requirements)

**Last Updated:** 2026-01-15
**Version:** 1.0
**Status:** Ready for Round 1 testing (after Epic 1)
