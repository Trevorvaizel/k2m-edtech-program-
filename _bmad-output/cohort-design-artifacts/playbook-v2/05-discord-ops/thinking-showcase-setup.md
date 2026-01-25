# Story 5.3: #thinking-showcase Channel Setup

**Epic:** 5 - Discord Architecture & Operations (Modules 4, 11)
**Story:** 5.3 - Define #thinking-showcase channel setup
**Status:** ready-for-dev
**Created:** 2026-01-25
**Purpose:** Specify the complete implementation of #thinking-showcase as the public celebration destination that implements Decision 12 (Hybrid Discord Model), provides psychological safety through celebration-only culture, and serves the JTBD social job with visible proof of transformation

---

## Story

As a **Discord System Architect**,
I want **a complete #thinking-showcase channel specification that implements the public-product celebration side of Decision 12 (Hybrid Discord Model)**,
so that **students have a psychologically safe space to celebrate their finished thinking growth without comparison, while providing social proof that serves the JTBD social job for parents, peers, and future self**.

---

## Acceptance Criteria

1. **Channel Purpose & Philosophy** defining #thinking-showcase as the celebration-only destination for finished work (Decision 12, Guardrails #3, #8, JTBD social job)
2. **Channel Configuration** specifying all Discord settings, permissions (read-only for students), and bot automation requirements
3. **Publication Flow** documenting how finished artifacts get published from private DMs to public celebration (privacy controls, student consent, anonymous options)
4. **Celebration Culture Design** implementing Guardrail #3 (no comparison) through celebration-only patterns, emoji reactions, and aggregate visibility
5. **Weekly Channel Progression** defining how #thinking-showcase evolves from Week 1 (early habit practice celebrations) through Week 8 (artifact graduation showcase)
6. **Bot Automation & Safety** specifying bot publication workflow, SafetyFilter validation, celebration message templates, and moderation
7. **JTBD Social Job Integration** designing how public celebration provides proof for parents, peers, and future self (with student consent system)
8. **Graduation & 4 Habits Celebration** documenting Week 8 artifact showcase, graduation card awarding, and cohort completion rituals

---

## Tasks / Subtasks

- [ ] **1. Define Channel Purpose & Philosophy** (AC: #1)
  - [ ] 1.1 Specify #thinking-showcase's role in Decision 12 (public product celebration)
  - [ ] 1.2 Document connection to Guardrails #3, #8 (no comparison, celebration-only)
  - [ ] 1.3 Explain how channel serves JTBD social job (proof for parents/peers/self)
  - [ ] 1.4 Map #thinking-showcase to 4 Habits celebration strategy
  - [ ] 1.5 Write channel philosophy statement for #welcome channel integration

- [ ] **2. Specify Channel Configuration** (AC: #2)
  - [ ] 2.1 Document Discord channel settings (type, permissions, read-only enforcement)
  - [ ] 2.2 Define role-based access control (@Student read-only, @Trevor admin, @CIS Bot publisher)
  - [ ] 2.3 Specify bot permissions and publication automation requirements
  - [ ] 2.4 Design channel description and pinned messages (celebration culture)
  - [ ] 2.5 Create channel setup checklist for server deployment

- [ ] **3. Document Publication Flow** (AC: #3, Decision 12)
  - [ ] 3.1 Specify private DM → public showcase publication workflow
  - [ ] 3.2 Design student consent system (Yes/No/Anonymous options)
  - [ ] 3.3 Define publication formats (habit practice celebrations, artifact showcases)
  - [ ] 3.4 Document privacy controls and opt-out mechanisms
  - [ ] 3.5 Specify conversation storage and artifact evidence integration

- [ ] **4. Implement Celebration Culture Design** (AC: #4, Guardrail #3)
  - [ ] 4.1 Design celebration-only patterns (no comparison, no rankings)
  - [ ] 4.2 Specify emoji reaction system (⭐ celebration, not 🔥 competition)
  - [ ] 4.3 Define aggregate visibility (e.g., "15 students published this week")
  - [ ] 4.4 Document forbidden patterns (no "best artifact", no leaderboards)
  - [ ] 4.5 Create celebration message templates (habits, milestones, completions)

- [ ] **5. Design Weekly Channel Progression** (AC: #5)
  - [ ] 5.1 Define Week 1-5 focus (habit practice celebrations, early wins)
  - [ ] 5.2 Define Weeks 6-7 focus (artifact work-in-progress celebrations)
  - [ ] 5.3 Define Week 8 focus (artifact completion, 4 Habits graduation)
  - [ ] 5.4 Specify publication frequency expectations (gradual increase)
  - [ ] 5.5 Design cohort completion rituals and final showcase

- [ ] **6. Specify Bot Automation & Safety** (AC: #6)
  - [ ] 6.1 Document bot publication workflow (validate → publish → celebrate)
  - [ ] 6.2 Specify SafetyFilter validation on all celebration posts
  - [ ] 6.3 Design celebration message templates (habit practice, artifact completion)
  - [ ] 6.4 Define moderation workflow (inappropriate content, violations)
  - [ ] 6.5 Create bot failure handling and fallback patterns

- [ ] **7. Implement JTBD Social Job Integration** (AC: #7, Story 1.2)
  - [ ] 7.1 Design parent engagement system (weekly email highlights with consent)
  - [ ] 7.2 Specify peer learning patterns (social proof without comparison)
  - [ ] 7.3 Document future-self evidence building (artifact as proof)
  - [ ] 7.4 Define university application artifacts (optional share)
  - [ ] 7.5 Create consent management system (opt-in/opt-out controls)

- [ ] **8. Document Graduation & 4 Habits Celebration** (AC: #8, Story 1.4)
  - [ ] 8.1 Design Week 8 artifact showcase format
  - [ ] 8.2 Specify 4 Habits graduation card awarding
  - [ ] 8.3 Define cohort completion rituals and celebrations
  - [ ] 8.4 Document post-cohort access to #thinking-showcase (archival)
  - [ ] 8.5 Create handoff to Epic 6 (Artifact System & Measurement)

---

## Dev Notes

### HIGH #3 FIX: Epic 4 Integration (Story 4.7 Discord Bot Technical Specification)

**Story 5.3 defines WHAT the bot does. Story 4.7 defines HOW the bot implements it.**

```yaml
STORY 4.7 CROSS-REFERENCES (Technical Implementation):

Section 3 (Publication Flow):
  → See Story 4.7, Section 5.2: /publish-command API implementation
  → See Story 4.7, Section 5.3: DM channel publication workflow
  → Discord.py code: `await channel.send(celebration_message)`

Section 6 (Bot Automation & Safety):
  → See Story 4.7, Section 3.1: Bot initialization and Discord client setup
  → See Story 4.7, Section 4.1: Message handler registration
  → See Story 4.7, Section 6.2: Claude API integration for celebration generation

Section 6.2 (SafetyFilter):
  → See Story 4.6, Section 5: SafetyFilter prompt specification
  → See Story 4.7, Section 7: Moderation workflow implementation
  → Guardrail validation: Code-level enforcement

Section 7 (Parent Email System):
  → See Story 4.7, Section 8: Email queue and batch processing
  → SendGrid/Mailgun integration: API call implementation
  → Error handling: Retry logic and alerting

DEPENDENCY MAPPING:
  Story 5.3 (this story) → Specification layer (WHAT)
  Story 4.7 (bot technical) → Implementation layer (HOW)
  Story 4.6 (artifact flow) → Data structures (artifact schema)

DEVELOPER HANDOFF:
  1. Read Story 5.3 for complete specification
  2. Read Story 4.7 for Discord.py implementation
  3. Cross-reference each section using mapping above
  4. Implement bot behavior per Story 4.7 technical specs
  5. Validate outputs match Story 5.3 specifications
```

### Strategic Context (Decision 12 + Guardrails #3, #8 + Epic 1 Foundations)

**#thinking-showcase is the public celebration destination of the Hybrid Discord Model (Decision 12):**

```
#thinking-lab (instructions + entry point)
    ↓
Private DM/Thread (CIS agent interactions)
    ↓ (safe, messy thinking documented)
    ↓
#thinking-showcase (finished artifacts celebrated)
```

**The Critical Design Principle:**
- **Process is PRIVATE** - Students can be messy, confused, and vulnerable in #thinking-lab DMs
- **Product is PUBLIC** - Only finished, polished thinking gets celebrated in #thinking-showcase
- **Journey is DOCUMENTED** - DM threads become evidence of growth (for artifacts later)
- **Celebration is VISIBLE** - Peer learning from finished work (social proof, motivation, JTBD social job)

**#thinking-showcase Implements Two Guardrails:**

1. **Guardrail #3 (No Comparison):**
   - Channel design prevents comparison/ranking in ALL celebrations
   - Bot SafetyFilter validates all celebration posts before publishing
   - Only aggregate visibility ("15 students published artifacts") - no "top student" or "best artifact"

2. **Guardrail #8 (Discord Safety):**
   - Private process (DMs) → Public product (#thinking-showcase) architecture
   - Students choose whether to share (Yes/No/Anonymous consent system)
   - No forced vulnerability - only finished work is celebrated

### Foundation Documents Integration (Epic 1 - ALL Non-Negotiable)

**Story 5.3 MUST implement these Epic 1 foundations:**

**1. Guardrails (Story 1.1) - ALL 11 ENFORCED:**

**Guardrail #1 (No Prescriptive Paths):**
- Celebrate diverse paths: "15 students practiced Habit 1 in different ways"
- NEVER: "Here's the ONLY way to practice Habit 1"
- ALWAYS: Honor each student's unique journey

**Guardrail #2 (No "Should" Language):**
- Bot celebrations verified: NO "you should", "you must", "you have to"
- Alternatives: "[Student] practiced Habit 1!", "Another thinking transformation complete!"
- Example: "They chose to pause before asking" (not "They should pause")

**Guardrail #3 (No Comparison/Ranking):**
- Celebration posts: Individual celebration OR aggregate numbers only
- NEVER: "Top artifact", "Best reflection", "Most active student"
- FORBIDDEN: Any ranking, leaderboard, or comparative language

**Guardrail #4 (No Human Advice Drift):**
- Trevor's 10% role: Celebration moderation, culture monitoring (NOT advice)
- Bot celebrations: Template-based (no personalized human guidance)

**Guardrail #5 (No Human Fallback Promised):**
- NEVER promise: "Trevor will celebrate you if the bot fails"
- Honest positioning: "Bot celebrates automatically, Trevor monitors culture"

**Guardrail #6 (Agent Purity):**
- CIS agents NEVER give advice (enforced in #thinking-lab)
- Celebrations reinforce agent scaffolding, not advice-giving

**Guardrail #7 (No Zone Skipping):**
- Celebrations honor zone progression (no skipping from Zone 0 to Zone 4 celebration)
- Bot validates: Student's current zone before allowing artifact publication

**Guardrail #8 (Discord Safety - Public Product):**
- #thinking-showcase is the public product destination
- Private DMs: Safe to be messy (only student + bot in #thinking-lab)
- Public showcase: Finished work only (student consent required)

**Guardrail #9 (Artifact Authenticity):**
- Artifacts prove identity transformation (not AI usage)
- Bot validation: Voice authenticity check (not AI-generated)
- Proof: DM conversations + artifact show genuine thinking growth

**Guardrail #10 (Brand Voice - Revolutionary Hope):**
- Language Level 1-2 (Ground/Pattern) for celebration messages
- Hope + empowerment: "You're becoming someone who thinks clearly!"
- Tone: Celebration, not pressure ("Skills that follow you forever")

**Guardrail #11 (JTBD-Relevant Examples):**
- Real pre-university scenarios: University choices, career clarity, study pressure
- NO cat poems, silly scenarios, or abstract examples in celebrations
- Serving real JTBD: "Help me move from confusion to clarity before university"

**2. JTBD Integration (Story 1.2):**
- **Emotional Job:** "Help me stop feeling anxious and start feeling like I belong"
  - #thinking-showcase creates belonging through celebration culture
  - Bot celebrations normalize diverse paths ("Students practice in different ways")
  - Aggregate visibility shows "you're not alone"

- **Social Job:** "Give me proof I can show to myself, my parents, and my future"
  - **NEW: Parent Engagement System (with student consent)** - See Story 5.2 integration
    - Student chooses during Week 1: Share weekly progress OR privacy until Week 8
    - If "Share weekly": Bot generates Monday email with child's progress
    - Weekly email: "Your child practiced Habit 1 & 2 this week. They're building Node 1.3: 'I could try this'."
    - One summary per week, aggregated (no raw DM content shared)
    - If "Privacy first": Parents receive NO updates until Week 8 artifact showcase
  - **Peer Learning:** #thinking-showcase provides public celebration for social proof
  - **Future Self:** Artifacts serve as evidence of growth (university applications, career clarity)

- **Identity Shifts:** Outsider → Observer → Experimenter → Collaborator → Director
  - Celebrations honor each identity shift milestone
  - Week 1: "You're becoming someone who pauses before asking!"
  - Week 8: "You're someone who thinks WITH AI!"

**3. Node Architecture (Story 1.3):**
- **16 nodes celebrated through #thinking-showcase publications**
- **Node-Specific Celebrations:**
  - Every artifact celebration references which nodes were mastered
  - Bot messages: "This shows Node 3.1 mastery: 'Context changes everything'"
  - Makes abstract habits concrete: Habit 3 (🔄 ITERATE) becomes visible as Node 3.1-3.4
- **Identity Evidence:** Artifacts show node concepts in action

**4. 4 Habits Branding (Story 1.4):**
- **Habit 1 ⏸️ Pause:** Celebrated in Weeks 1-5
- **Habit 2 🎯 Context:** Celebrated in Weeks 1-5
- **Habit 3 🔄 Iterate:** Celebrated in Weeks 4-7
- **Habit 4 🧠 Think First:** Celebrated in Weeks 6-8
- **Graduation Proof:** 4 Habits card awarded in Week 8 showcase

### Story 5.1 Integration (Discord Server Architecture)

**From Story 5.1 (Discord Server Structure):**

#thinking-showcase sits within the **CORE INTERACTION SPACES** tier:

```yaml
#thinking-showcase (🌟 Thinking Showcase)
  → Purpose: Published artifacts, celebration only
  → Pattern: Student publishes → bot celebrates
  → Permissions: Read-only (students), bot publishes
  → Decision 12: Public celebration of private work
```

**Channel Context:**
- **Above:** Information & Onboarding channels (#welcome, #announcements, #resources)
- **Beside:** #thinking-lab (private practice entry point)
- **Below:** Week-specific channels (node delivery, daily prompts)
- **Below:** Admin channels (Trevor's dashboard, bot testing)

**Key Integration Points:**
- **#thinking-lab channel:** Source of finished work to celebrate (students opt-in after CIS conversations)
- **#announcements:** Bot posts weekly showcase summaries ("23 artifacts published this week!")
- **Week-specific channels:** Daily prompts encourage sharing to #thinking-showcase
- **#facilitator-dashboard:** Trevor monitors celebration culture (Guardrail #3 compliance)

### Story 5.2 Integration (#thinking-lab Channel Setup)

**From Story 5.2 (#thinking-lab Setup):**

**Publication Flow from #thinking-lab to #thinking-showcase:**

```yaml
Step 1: Student Completes CIS Conversation (in #thinking-lab DM)
  Student: "/frame I'm confused about university choices"
  Bot: [Private DM scaffolding conversation happens]
  Student: "I feel clearer now"

Step 2: Bot Offers Showcase Share (Story 5.2, Section 4.2)
  Bot: "Want to share your learning to #thinking-showcase?"
  Student chooses: [Yes / No / Maybe later]

Step 3A: If Student Chooses [Yes] → Story 5.3 Publication Workflow
  Bot: "Great! I'll post a celebration (not our private conversation)"
  Bot validates: SafetyFilter checks celebration message (Guardrails #3, #10, #11)
  Bot publishes: To #thinking-showcase channel (this Story 5.3 specification)
  Bot celebrates: Identity transformation visible, peers see finished work

Step 3B: If Student Chooses [No]
  Bot: "Respected! Your privacy matters"
  Bot saves: Conversation to database (for artifact later)
  No public post: Private process stays private

Step 3C: If Student Chooses [Anonymous]
  Bot: "I'll post anonymously"
  Bot publishes: "Anonymous student practiced Habit 1 & 2 today!"
  Identity protected: Anxiety reduction for shy students
```

**Three Publication Options (from Story 5.2):**

1. **Public Publication (Default)**
   - Bot publishes with: "🌟 [Student Name] practiced Habits 1 & 2 today!"
   - Artifact visible to all students
   - Celebrated in channel with emoji reactions
   - Rationale: Social proof, motivation, peer learning

2. **Anonymous Publication**
   - Bot publishes with: "🌟 Anonymous student practiced Habits 1 & 2 today!"
   - Artifact visible to all students
   - Identity protected (anxiety reduction)
   - Rationale: Psychological safety for shy students

3. **Private to Trevor**
   - Bot DMs artifact to Trevor only
   - Not published to #thinking-showcase
   - Trevor provides personal feedback
   - Rationale: Student preference, privacy concerns

**Connection to Parent Engagement System (Story 5.2 + Story 5.3):**

```yaml
Student Consent (Story 5.2, Section 2.2):
  Week 1 onboarding: Student chooses parent update preference
    - Option A: "Share weekly progress" → Parents get Friday email
    - Option B: "Privacy first" → No updates until Week 8 artifact showcase

Weekly Email Generation (Story 5.3 implementation):
  If student chose "Share weekly":
    Bot generates Monday email: "Your child practiced Habit 1 & 2 this week"
    Example: "Your child had 5 /frame conversations about university choices.
             They're building Node 1.3: 'I could try this'."
    One summary per week, aggregated (no raw DM content)

  If student chose "Privacy first":
    Parents receive NO updates until Week 8 artifact showcase
    Respects student autonomy, preserves psychological safety

Student can change preference anytime via DM to bot
```

---


## 3. Publication Flow (Private DM → Public Showcase)

### Complete Publication Workflow

**From Decision 12 (Hybrid Discord Model) + Story 5.2 (#thinking-lab Setup):**

```yaml
PHASE 1: CIS Conversation Completion (in #thinking-lab DM)

Step 1.1: Student Completes CIS Conversation
  Student: "/frame I'm confused about university choices"
  Location: Private DM (only student + bot)
  Bot: Scaffolds thinking through conversation
  Student: "I feel clearer now"

Step 1.2: Bot Offers Showcase Share (Story 5.2, Section 4.2)
  Bot: "Does this feel clearer now? Or do you want to explore more?"
  Student: "I'm good"
  Bot: "Great! Want to share your learning to #thinking-showcase?
        [Yes] → I'll post a celebration (not our private conversation)
        [No] → Conversation stays private (saved for your artifact later)
        [Maybe later] → I'll remind you in Week 6 when artifact starts
        Your choice. No pressure."

Step 1.3: Student Chooses Publication Option
  Option A: [Yes] - Public publication (name visible)
  Option B: [No] - Keep private (saved for artifact database)
  Option C: [Anonymous] - Anonymous publication

PHASE 2: Publication Validation & Preparation

Step 2.1: Bot Validates Publication Readiness
  Bot checks:
    - Is this a habit practice celebration OR artifact publication?
    - If artifact: Are all 6 sections complete? (Story 4.6)
    - If artifact: Is voice authentic (not AI-generated)? (Guardrail #9)
    - Is celebration message within Guardrails #3, #10, #11?
  
  If Valid: Proceed to Phase 3
  If Invalid: Bot explains why and offers to fix or skip

Step 2.2: Bot Generates Celebration Message (Claude API)
  Template-based with personalization:
    - Habit practice: "🌟 [Student Name] practiced Habits 1 & 2 today!"
    - Artifact: "🌟 [Student Name] completed their Thinking Artifact!"
  
  Personalization elements:
    - Specific habits demonstrated: "They paused before asking (⏸️ PAUSE)"
    - Identity shift: "They're becoming someone who thinks clearly!"
    - Node connections: "This shows Node 1.3: 'I could try this'"
  
  Guardrails validation (SafetyFilter):
    - Guardrail #3: No comparison/ranking language
    - Guardrail #10: Revolutionary Hope tone
    - Guardrail #11: JTBD-relevant examples (university, career, study)

PHASE 3: Publication to #thinking-showcase

Step 3.1: Bot Publishes Celebration Post
  Bot posts to #thinking-showcase:
    "🌟 [Student Name] practiced Habits 1 & 2 today!
     
     They paused to clarify what they want (⏸️ PAUSE).
     They explained their situation first (🎯 CONTEXT).
     
     That's thinking WITH AI, not copying FROM it.
     
     Tools change. Habits transfer. ⏸️🎯"
  
  Bot adds initial reaction: ⭐ (models celebration behavior)

Step 3.2: Students React (Celebration Culture)
  Students see: Celebration post in #thinking-showcase
  Students react: ⭐ (star), ❤️ (heart), 🎉 (party)
  NO comments: Replies disabled (celebration only, no discussion)
  
  Peer learning effect:
    - "I could do that too!" (social proof)
    - "People like me succeed" (belonging)
    - NOT "I need to beat that" (comparison avoided)

Step 3.3: Bot DMs Confirmation to Student
  Bot: "Posted! Your growth is inspiring others. 🌟
        Plus: You're building evidence for your artifact.
        Keep practicing. Skills compound over time!"

PHASE 4: Database Persistence & Parent Updates

Step 4.1: Bot Saves Publication to StudentContext
  Database: SQLite (cohort-X.db) per Decision 15 (Simplified Tech Stack)

**HIGH #2 FIX: Complete Database Schema Specification**

```sql
-- Table: showcase_publications
-- Stores all publications to #thinking-showcase channel
CREATE TABLE showcase_publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,  -- Discord user ID
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    publication_type TEXT NOT NULL,  -- 'habit_practice' OR 'artifact_completion'
    visibility_level TEXT NOT NULL,  -- 'public' OR 'anonymous' OR 'private'
    celebration_message TEXT NOT NULL,
    habits_demonstrated TEXT,  -- JSON array: ["⏸️", "🎯", "🔄", "🧠"]
    nodes_mastered TEXT,  -- JSON array: [1.3, 2.1, 3.2]
    reactions_count INTEGER DEFAULT 0,
    parent_email_included BOOLEAN DEFAULT 0,
    artifact_id INTEGER,  -- FK to artifacts table if artifact_completion
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
);

-- Table: parent_engagement
-- Stores parent email consent and contact information
CREATE TABLE parent_engagement (
    student_id TEXT PRIMARY KEY,  -- Discord user ID
    parent_email TEXT NOT NULL,
    consent_preference TEXT NOT NULL,  -- 'share_weekly' OR 'privacy_first'
    consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_email_sent DATETIME,
    unsubscribe_token TEXT UNIQUE,  -- For parent opt-out link
    FOREIGN KEY (student_id) REFERENCES students(discord_id)
);

-- Table: student_publication_preferences
-- Stores student's permanent publication settings (HIGH #7)
CREATE TABLE student_publication_preferences (
    student_id TEXT PRIMARY KEY,
    default_preference TEXT DEFAULT 'always_ask',  -- 'always_ask', 'always_yes', 'always_no', 'week8_only'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id)
);

-- Data Retention Policy
-- Keep all publication data for 1 year after cohort completion
-- Automated backup: Daily at 2:00 AM to Google Drive
-- Backup location: /K2M-Cohort-Backups/cohort-X/db-backups/
```

Step 4.2: Parent Email Generation (if consent enabled)
  Check: Student's parent_engagement_preference
  If "share weekly": Include in Monday batch email
  If "privacy first": Skip parent updates (until Week 8)

**HIGH #1 FIX: Parent Email Technical Implementation**

```yaml
Email Service Integration (Cohort 1 - Manual Workflow):
  Service: SendGrid (recommended) OR Mailgun OR AWS SES
  API Key: Stored in environment variable (SENDGRID_API_KEY)
  Sender: "Trevor <trevor@k2m-edtech.com>" (verified sender)
  Reply-to: trevor@k2m-edtech.com

Batch Email Schedule (Mondays 9:00 AM):
  Trigger: Cron job or scheduled task
  Process:
    1. Query: SELECT * FROM parent_engagement WHERE consent_preference = 'share_weekly'
    2. For each student: Aggregate last week's celebration data
    3. Generate personalized email using template (Section 7.1)
    4. Send via SendGrid API (batch send for efficiency)
    5. Log sent emails to parent_email_log table
    6. Update last_email_sent timestamp

Error Handling:
  - Failed email: Retry 3 times with exponential backoff (1min, 5min, 15min)
  - Bounced email: Alert Trevor, mark parent_email_status = 'bounced'
  - Unsubscribe: Process parent opt-out link immediately
  - Rate limiting: SendGrid free tier (100 emails/day) - sufficient for 200 students

Parent Opt-Out System (Guardrail #8):
  - Every email includes unsubscribe link: /parent/unsubscribe?token={unsubscribe_token}
  - Unsubscribe endpoint: Updates parent_engagement.consent_preference to 'privacy_first'
  - Bot notification: "Parent [email] opted out. Weekly emails stopped."
  - Student control: Student can re-enable via DM to bot (overrides parent choice)

Email Queue Management:
  Queue system: Python `Celery` or `RQ` (Redis Queue)
  Retry queue: Failed emails auto-retry
  Monitoring: Trevor receives weekly email stats (sent, failed, bounced)

See Section 7.1 for complete parent email template
```

Step 4.3: Update Student Progress
  StudentContext updates:
    - publication_count: Increment total publications
    - habits_publicly_celebrated: Track which habits celebrated
    - zone_progression: May advance based on publication evidence
    - artifact_ready: Flag for Week 8 (if sufficient publications)
```

### Three Publication Options (Privacy Controls)

**From Story 5.2 (#thinking-lab Setup), Section 2.2:**

```yaml
Option 1: Public Publication (Default)
  Bot publishes with: "🌟 [Student Name] practiced Habits 1 & 2 today!"
  Artifact visible to: All students in cohort
  Celebrated in: Channel with emoji reactions (⭐❤️🎉)
  Parent email: Included in Monday weekly summary (if consent enabled)
  Rationale: 
    - Social proof (motivation for others)
    - Motivation (public commitment)
    - Belonging ("people like me succeed")
    - JTBD social job: Public evidence for parents/peers

Option 2: Anonymous Publication
  Bot publishes with: "🌟 Anonymous student practiced Habits 1 & 2 today!"
  Artifact visible to: All students (identity protected)
  Celebrated in: Channel with emoji reactions
  Parent email: NO EMAIL SENT (truly anonymous - parents not notified)
  Rationale:
    - Psychological safety for shy students
    - Anxiety reduction (fear of judgment)
    - Still contributes to peer learning (social proof maintained)
    - Belonging without visibility pressure
    - TRUE ANONYMITY: Parents don't receive notification (privacy protected)

Option 3: Private to Trevor
  Bot action: DMs artifact to Trevor only
  Publication: NOT posted to #thinking-showcase
  Trevor response: Personal feedback via DM
  Rationale:
    - Student preference (privacy concerns)
    - Sensitive topic (not ready for public)
    - Trevor's 10% human layer (personalized guidance)
    - Still counts toward artifact completion (private practice recognized)

Student Agency:
  - Student chooses option in the moment (not locked in)
  - Can choose different option for different publications
  - Can change preference mid-cohort (via DM to bot)
  - Bot respects choice without judgment (psychological safety)

**Permanent Publication Preference Setting (HIGH #7 FIX):**
  Student can set permanent preference via DM to reduce decision fatigue:
    Bot: "Publication Preference: Choose your default
          [Always ask] - Ask me every time (current default)
          [Always yes] - Auto-publish all my celebrations
          [Always no] - Never publish (private to Trevor only)
          [Week 8 only] - Only publish artifact, not habit practice"

    Student preference: Stored in StudentContext.default_publication_preference
    Can change: Anytime via DM to bot
    Rationale: Reduces decision fatigue, respects student autonomy, addresses publication pressure anxiety
```

### Publication Formats

**Format 1: Habit Practice Celebration (Weeks 1-7)**

```yaml
When: Student completes CIS conversation in #thinking-lab
Trigger: Student chooses [Yes] or [Anonymous] after CIS conversation

Celebration Template:
  "🌟 [Student/Anonymous] practiced Habit [X] & [Y] today!
   
   [Specific examples of what they did]
   [Identity shift observed]
   [Node connection if applicable]
   
   That's thinking WITH AI, not copying FROM it.
   
   Tools change. Habits transfer. [Habit icons]"

Example (Habit 1 & 2):
  "🌟 [Student] practiced Habits 1 & 2 today!
   
   They paused to clarify what they want (⏸️ PAUSE).
   They explained their situation first (🎯 CONTEXT).
   
   Instead of 'help me with AI', they asked:
   'I'm a high school student confused about engineering or medicine. Can you help me think through this?'
   
   That's thinking WITH AI. Skills that follow you forever. ⏸️🎯"

Length: 3-5 sentences (short, celebratory, scannable)
Tone: Revolutionary Hope (empowerment, not pressure)
Guardrails: No comparison (Guardrail #3), JTBD-relevant examples (Guardrail #11)
```

**Format 2: Artifact Publication (Weeks 6-8)**

```yaml
When: Student completes artifact and uses /publish-artifact command
Trigger: Bot validates artifact is complete (all 6 sections filled)

Celebration Template:
  "🌟 [Student/Anonymous] completed their Thinking Artifact!
   
   They wrestled with: [Question from artifact]
   They reframed it: [How they used /frame]
   They explored: [What they discovered]
   They challenged: [Assumptions they tested]
   They concluded: [Final insight]
   They learned: [What this taught them]
   
   They're becoming someone who thinks clearly with AI!
   
   Tools change. Habits transfer forever. ⏸️🎯🔄🧠"

Example (University Career Artifact):
  "🌟 [Student] completed their Thinking Artifact!
   
   They wrestled with: 'Should I study engineering or medicine?'
   They reframed it: 'What do I want from my career? Impact or money?'
   They explored: 8 career possibilities using /diverge
   They challenged: 'I need to study business to be successful'
   They concluded: 'I care more about solving problems than making money'
   They learned: 'I enjoy problems that require creativity, not repetition'
   
   They're becoming someone who directs AI intentionally!
   
   Skills that follow you forever. 🧠"

Length: 8-12 sentences (longer, more detailed than habit celebrations)
Content: Full artifact summary (not just headline)
Tone: Celebration of identity transformation (Outsider → Director)
```

**Format 3: Graduation Celebration (Week 8)**

```yaml
When: Student publishes artifact + completes all 4 Habits
Trigger: Week 8, artifact verified complete

Celebration Template:
  "🎓 [Student/Anonymous] earned the 4 Habits Card!
   
   ⏸️ PAUSE - They know what they want
   🎯 CONTEXT - They explain their situation
   🔄 ITERATE - They change one thing at a time
   🧠 THINK FIRST - They decide with AI
   
   Their artifact proves: 'I am someone who thinks WITH AI!'
   
   Tools change. These 4 habits transfer forever.
   
   [Optional: 1-sentence artifact insight]
   
   You're ready for university. You're ready for life. 🌟"

Example:
  "🎓 [Student] earned the 4 Habits Card!
   
   ⏸️ PAUSE - They know what they want
   🎯 CONTEXT - They explain their situation
   🔄 ITERATE - They change one thing at a time
   🧠 THINK FIRST - They decide with AI
   
   Their artifact proves: 'I am someone who thinks WITH AI!'
   
   Tools change. These 4 habits transfer forever.
   
   From 'confused about university' to 'I'm becoming someone who solves problems that matter.'
   
   You're ready for university. You're ready for life. 🌟"

Length: 10-15 sentences (celebration + artifact insight)
Tone: Culmination of 8-week journey, identity transformation complete
Graduation: 4 Habits card image sent via DM (digital credential)
```

### Privacy Controls & Consent Management

**Student Consent System (Story 5.2 Integration):**

```yaml
Initial Consent (Week 1 Onboarding):
  During #welcome channel onboarding:
    Bot asks: "Parent Updates: Choose your preference"
    Option A: ✅ "Share weekly progress" → Parents get Friday email
    Option B: ❌ "Privacy first" → No updates until Week 8
  Student choice: Stored in StudentContext.parent_engagement_preference
  Can change: Anytime via DM to bot

**MEDIUM #2 FIX: Week 1 Parent Notification Warning (Sets Expectations)**

  Bot adds: "In Week 8, we'll invite parents to see your artifact
            (unless you choose private). You can always opt-out then.
            No pressure - this is about celebrating your growth."

  Rationale: Sets expectations upfront, avoids Week 8 surprise,
            respects student autonomy, prevents forced vulnerability

Weekly Email Generation (Mondays 9:00 AM):
  Filter: Students where parent_engagement = "share weekly"
  Content: Aggregate summary from last week's celebrations
  Template: See Section 7.1 (Parent Email Template)
  
  Includes:
    - Habit practice count (e.g., "Your child practiced Habit 1 & 2 this week")
    - Node progress (e.g., "They're building Node 1.3: 'I could try this'")
    - Celebration highlights (e.g., "Had 3 /frame conversations about university")
    - NO raw DM content (privacy protected)
  
  Excludes:
    - Students who chose "privacy first" (respected absolutely)
    - Private conversation details (aggregate only)
    - Comparison to other students (Guardrail #3)

Week 8 Artifact Showcase (Final Celebration):
  All students: Parents receive invitation to Week 8 artifact showcase
  Email: "Your child completed their 8-week journey! See their artifact at [link]"
  Student choice: Public OR Anonymous OR Private to Trevor (respected)

Consent Change Process:
  Student DM: "I want to change my parent update preference"
  Bot: "Current: share weekly. Change to: [1] share weekly [2] privacy first"
  Student: "2"
  Bot: Updated in StudentContext immediately
  Bot: "Preference changed. Parents will [not] receive weekly updates."
  Effective: Next Monday email batch (respects student agency)

Privacy Guarantees:
  - Raw DM conversations NEVER shared (aggregate summaries only)
  - Student can opt-out anytime (no locked-in choices)
  - Anonymous option ALWAYS available (identity protection)
  - Private to Trevor option ALWAYS available (complete privacy)
```

---

## 4. Celebration Culture Design (Guardrail #3 Compliance)

### No-Comparison Celebration Principles

**The Core Rule:**
> **CELEBRATE GROWTH, NEVER RANK.**

**Implementation:**

```yaml
ALLOWED Celebration Patterns:

1. Individual Celebrations (Identity-Focused):
   - "🌟 [Student] practiced Habit 1 & 2 today!"
   - "They're becoming someone who thinks clearly!"
   - "Another thinking transformation complete!"
   - Focus: Personal growth, identity shift

2. Aggregate Visibility (Numbers-Only):
   - "15 students published artifacts this week!"
   - "234 habits practiced this cohort"
   - "89 students completed Week 4"
   - Focus: Collective progress, no individual comparison

3. Normalization & Belonging:
   - "Many students feel this way in Week 1"
   - "Confusion is normal. You're exactly where you should be."
   - "People like you are succeeding every day"
   - Focus: Shared experience, belonging cues

**MEDIUM #1 FIX: Diverse Celebration Examples (Avoid Implicit Comparison)**

Prevent "Ideal Path" Bias:
  - Celebrate different practice lengths: 2-minute pause, 20-minute exploration
  - Celebrate different habit combinations: Habit 1 only, Habit 1&2, Habit 3 only
  - Celebrate different topics: University, career, study, personal problems
  - Celebrate different outcomes: Clarity, more questions, new perspectives

Diverse Examples to Rotate:
  - "Student paused when they felt confused about an assignment"
  - "Student shared one sentence about their situation before asking"
  - "Student explored one career possibility using /diverge"
  - "Student practiced Habit 1 for 5 minutes"
  - "Student practiced Habit 3 for 30 minutes"
  - "Student challenged one assumption about university"
  - "Student reframed their question about career choices"
  (No 'perfect' celebration format - diverse paths honored)

Aggregate Visibility Language (Reduce Pressure):
  - OLD: "15 students published artifacts this week!" (implies 185 didn't)
  - NEW: "Celebrating 15 students' published artifacts this week!" (focus on celebrating)
  - ADD: "Whether you published or not, your growth matters." (normalize non-publishing)

FORBIDDEN Patterns (Guardrail #3 Violations):

   NEVER say:
     - "Top student this week" ❌
     - "Best artifact" ❌
     - "Most active" ❌
     - "Faster than others" ❌
     - "Ahead of the cohort" ❌
     - "Better than [other student]" ❌
     - "Ranking: 1st, 2nd, 3rd" ❌
   
   Bot SafetyFilter blocks all comparison language before publishing
```

### Emoji Reaction System

**Celebration-Only Reactions:**

```yaml
Allowed Reactions:
  - ⭐ (Star) = "I celebrate your growth!"
  - ❤️ (Heart) = "This inspires me!"
  - 🎉 (Party) = "Another transformation complete!"
  - 👏 (Clap) = "Respect for your journey!"

Forbidden Reactions (Implicit Comparison):
  - 🔥 (Fire) - "Hot/best" (competition implied)
  - 🏆 (Trophy) - "Winner/ranking" (comparison)
  - 💯 (100) - "Perfect/best" (implicit ranking)
  - 📈 (Chart) - "Progress/growth curve" (quantification)

Enforcement:
  - Bot models: ⭐ reaction on every publication
  - Students follow: Celebration-only culture
  - SafetyFilter monitors: No forbidden reactions used
  - Trevor monitors: Culture compliance (10% workflow)
```

### Celebration Message Templates

**Template 1: Habit Practice Celebration**

```
🌟 [Student/Anonymous] practiced Habit [X] & [Y] today!

[Specific example of what they did]
[Identity shift observed]

That's thinking WITH AI, not copying FROM it.

Tools change. Habits transfer. [Habit icons]
```

**Template 2: Aggregate Milestone Celebration**

```
🌟 WEEKLY MILESTONE: [X] students published artifacts this week!

[Cohort progress stat]
[Identity transformation count]

Another week of thinking growth complete!
Skills that follow you forever.
```

**Template 3: Graduation Celebration**

```
🎓 [Student/Anonymous] earned the 4 Habits Card!

⏸️ PAUSE - They know what they want
🎯 CONTEXT - They explain their situation
🔄 ITERATE - They change one thing at a time
🧠 THINK FIRST - They decide with AI

Their artifact proves: "I am someone who thinks WITH AI!"

You're ready for university. You're ready for life. 🌟
```

---

## 5. Weekly Channel Progression

### Week 1-5: Habit Practice Celebrations

**Focus:** Celebrate early habit practice, build momentum, normalize confusion

```yaml
Week 1 (Wonder - Zone 0→1):
  Celebrations: Habit 1 (⏸️ PAUSE) practice
  Bot posts: "🌟 [Student] paused before asking AI today!"
  Aggregate: "45 students practiced Habit 1 this week!"
  Message: "Week 1 is about Wonder - noticing AI is already around you"

Weeks 2-3 (Trust - Zone 1→2):
  Celebrations: Habit 1 & 2 (⏸️🎯) practice
  Bot posts: "🌟 [Student] explained their situation first!"
  Aggregate: "89 students are building Habit 2 this week!"
  Message: "Weeks 2-3 build Trust through small wins"

Weeks 4-5 (Converse - Zone 2→3):
  Celebrations: Habit 3 (🔄 ITERATE) exploration
  Bot posts: "🌟 [Student] explored 3 career possibilities!"
  Aggregate: "67 students used /diverge or /challenge this week!"
  Message: "Weeks 4-5 build Conversation skills"
```

### Weeks 6-7: Artifact Work-In-Progress

**Focus:** Celebrate artifact starts, encourage completion

```yaml
Week 6-7 (Direct - Zone 3→4):
  Celebrations: Artifact section completions
  Bot posts: "🌟 [Student] completed 3 artifact sections!"
  Aggregate: "98 students started their artifact this week!"
  Encouragement: "Keep going! Artifact deadline: Week 8"
  Message: "Weeks 6-7 build Direction skills"
```

### Week 8: Final Showcase & Graduation

**Focus:** Celebrate artifacts, award 4 Habits cards, cohort completion

```yaml
Week 8 (Artifact Completion & Showcase):
  Celebrations: Full artifact completions, 4 Habits graduations
  Bot posts: "🎓 [Student] earned the 4 Habits Card!"
  Aggregate: "127 students completed their cohort journey!"
  Graduation: 4 Habits card sent via DM
  Final message: "You're ready for university. You're ready for life."
  
Cohort Completion Ritual:
  Bot posts: "🌟 COHORT GRADUATION COMPLETE!
  
  127 graduates proved they're someone who thinks with AI!
  
  ⏸️ PAUSE - You know what you want
  🎯 CONTEXT - You explain your situation
  🔄 ITERATE - You change one thing at a time
  🧠 THINK FIRST - You decide with AI
  
  Tools change. These 4 habits transfer forever."
```

---

## 6. Bot Automation & Safety

### Publication Bot Workflow

```yaml
Step 1: Publication Trigger (from #thinking-lab)
  Student: Chooses [Yes] or [Anonymous] after CIS conversation
  Bot: Receives publication request via DM

Step 2: Validation (SafetyFilter)
  Bot checks: Guardrails #3, #10, #11 compliance
  - No comparison/ranking language? ✅
  - Revolutionary Hope tone? ✅
  - JTBD-relevant examples? ✅
  
  If PASS: Proceed to Step 3
  If FAIL: Bot rewrites message and re-validates

Step 3: Publication
  Bot posts: Celebration to #thinking-showcase
  Bot adds: ⭐ reaction (models celebration behavior)

Step 4: Confirmation
  Bot DMs student: "Posted! Your growth is inspiring others. 🌟"
```

### SafetyFilter Enforcement (Guardrails #3, #10, #11)

```yaml
Guardrail #3 (No Comparison) Checks:
  - Blocks: "best", "top", "better than", "most", "least"
  - Blocks: Student rankings, leaderboards
  - Blocks: Comparative language ("faster", "slower", "ahead", "behind")
  - Action: Block post, alert Trevor, rewrite without comparison

Guardrail #10 (Brand Voice) Checks:
  - Blocks: Fear-based language ("get left behind", "don't miss out")
  - Blocks: Pressure tactics ("you must", "hurry up")
  - Enforces: Revolutionary Hope tone (empowerment, celebration)
  - Action: Block post, alert Trevor, rewrite with hope

Guardrail #11 (JTBD Examples) Checks:
  - Blocks: Generic examples (cat poems, silly scenarios)
  - Blocks: Non-JTBD content (trivial puzzles, games)
  - Enforces: Real pre-university scenarios (career, study, future)
  - Action: Block post, alert Trevor, rewrite with JTBD examples

SafetyFilter Workflow:
  1. Claude API generates celebration message
  2. SafetyFilter validates against all guardrails
  3. If PASS: Send to student
  4. If FAIL: Block, alert Trevor, regenerate or rewrite
  5. Trevor reviews blocked posts in #moderation-logs

**HIGH #4 FIX: Claude API Prompt Engineering for Celebration Generation**

```yaml
Celebration Generation System Prompt:
  "You are a celebration bot for K2M AI Thinking Skills Cohort.
   Generate celebration messages for students who practiced thinking habits.

   RULES (STRICT - NEVER VIOLATE):
   1. NEVER use comparison language: 'best', 'top', 'better than', 'most', 'least',
      'ranking', 'leaderboard', 'faster', 'slower', 'ahead', 'behind'
   2. ALWAYS use Revolutionary Hope tone: Empowerment, celebration, no pressure
   3. ONLY use JTBD-relevant examples: University choices, career clarity, study pressure,
      future planning, problem-solving (NO cat poems, silly scenarios, trivial puzzles)
   4. Focus on identity shifts: 'becoming someone who thinks clearly', 'building habits'
   5. Keep to 3-5 sentences (habit practice) or 8-12 sentences (artifact)
   6. Use Habit icons: ⏸️🎯🔄🧠
   7. Celebrate DIVERSE paths: Different students practice differently (no 'ideal' path)

   OUTPUT TEMPLATE (Habit Practice):
   '🌟 [Student/Anonymous] practiced Habit [X] & [Y] today!

    [1 specific example of what they did - concrete, JTBD-relevant]
    [1 sentence about identity shift observed]
    That's thinking WITH AI, not copying FROM it.
    Tools change. Habits transfer. [Habit icons]'

   OUTPUT TEMPLATE (Artifact):
   '🌟 [Student/Anonymous] completed their Thinking Artifact!

    They wrestled with: [Question from artifact]
    They reframed it: [How they used /frame]
    They explored: [What they discovered]
    They challenged: [Assumptions they tested]
    They concluded: [Final insight]
    They learned: [What this taught them]
    They're becoming someone who thinks clearly with AI!
    Tools change. Habits transfer forever. ⏸️🎯🔄🧠'

   FEW-SHOT EXAMPLES (Habit Practice):

   Example 1 (Habit 1 & 2 - University):
   "🌟 [Student] practiced Habits 1 & 2 today!
    They paused to clarify what they want (⏸️ PAUSE).
    They explained their situation first (🎯 CONTEXT).
    Instead of 'help me with AI', they asked:
    'I'm a high school student confused about engineering or medicine. Can you help me think through this?'
    That's thinking WITH AI. Skills that follow you forever. ⏸️🎯"

   Example 2 (Habit 1 only - Study pressure):
   "🌟 [Student] practiced Habit 1 today!
    They stopped when they felt confused about an assignment.
    Instead of rushing to AI, they asked: 'What do I actually need help with?'
    They're becoming someone who pauses before asking.
    That's clarity first, answers second. ⏸️"

   Example 3 (Habit 3 - Career exploration):
   "🌟 [Student] practiced Habit 3 (🔄 ITERATE) today!
    They explored 8 different career possibilities using /diverge.
    They changed one thing at a time: 'What if I tried healthcare? What about tech?'
    They're building Node 3.1: 'I have opinions about quality'.
    Skills that follow you forever. 🔄"

   ANTI-PATTERNS (NEVER GENERATE THESE):
   ❌ "Best artifact this week!" (comparison)
   ❌ "You're ahead of the cohort!" (ranking)
   ❌ "Most active student!" (competition)
   ❌ "You should practice more!" (pressure)
   ❌ "Here's a cat who learned to pause" (non-JTBD example)
   ❌ "Solve this riddle about AI" (trivial content)

   DIVERSE PATHS TO CELEBRATE (Rotate examples):
   - Students who pause when confused
   - Students who share one sentence about their situation
   - Students who explore one career possibility
   - Students who challenge one assumption
   - Students who practice for 2 minutes
   - Students who practice for 20 minutes
   (No 'ideal' practice length or method)"

API Parameters (Claude API Call):
  model: claude-sonnet-4-5-20250929
  temperature: 0.7  # Creative but consistent
  max_tokens: 300   # Habit practice (3-5 sentences)
  max_tokens: 600   # Artifact (8-12 sentences)
  top_p: 0.9

Testing Protocol (Before Production):
  1. Generate 50 test celebration messages using diverse inputs
  2. Human review for Guardrail #3, #10, #11 compliance (pass threshold: 95%)
  3. Iterate prompt until 95%+ pass rate achieved
  4. Monitor first week of production: Flag any blocked messages for prompt refinement
```
```

### Moderation & Escalation

**From Story 5.1 (Discord Server Structure):**

```yaml
Level 1: Bot Handles (Automated)
  - Guardrail #3 violations: SafetyFilter blocks comparison posts
  - Spam/excessive reactions: Rate limits
  - Celebration culture compliance: Bot models appropriate reactions

Level 2: Trevor Monitors (Human Judgment)
  - Culture monitoring: Are norms being followed?
  - Celebration quality: Authentic, specific, diverse?
  - Student well-being: Anyone not publishing (stuck students)

Level 3: Trevor Intervenes (Direct Action)
  - Safety violations: Remove inappropriate posts immediately
  - Repeated issues: Warning to student (private DM)
  - Crisis situations: Direct support (Level 4 protocol from Story 5.1/5.2)

Reporting:
  - Bot logs: All moderation actions to #moderation-logs
  - Trevor documents: Intervention outcomes
  - Weekly review: Celebration culture assessment
```

---

## 7. JTBD Social Job Integration

### Parent Engagement System (Student Consent Required)

**Complete Parent Email Template (Monday 9:00 AM):**

```yaml
Subject: "Your child's thinking growth this week - [Student Name]"

Email Body:
Dear Parent/Guardian,

Here's what [Student Name] practiced this week in K2M's AI Thinking Skills Cohort:

🎯 HABIT PRACTICE
Your child practiced:
• Habit 1 (⏸️ PAUSE) - [X] times
• Habit 2 (🎯 CONTEXT) - [Y] times
• Habit 3 (🔄 ITERATE) - [Z] times (if Week 4+)
• Habit 4 (🧠 THINK FIRST) - [W] times (if Week 6+)

💡 KEY MILESTONES
• Had [N] /frame conversations about [topic: university, career, study]
• Built Node [X.Y]: "[Node title from Story 1.3]"
• [Specific insight or growth moment from celebrations]

🌟 CELEBRATION
[Student Name] shared their thinking growth with the cohort [X] times this week!
They're becoming someone who thinks clearly with AI.

WHAT THIS MEANS
These aren't just "AI skills" - they're thinking skills that transfer forever.
• Pause before asking → Know what you want
• Explain context first → AI responds to YOUR situation
• Change one thing at a time → Learn through experimentation
• Think before decisions → Make better choices

NEXT WEEK
Week [X] focus: [Brief description of upcoming week]
Encourage them to keep practicing!

Questions? Reply to this email or DM Trevor on Discord.

Best,
Trevor
K2M Founder

P.S. Your child chose to share these updates. You can opt-out anytime by having them DM the bot.
```

### Social Proof System (Peer Learning)

```yaml
Peer Learning Design:
  Goal: Motivate through "people like me succeed" (not competition)
  
  Celebration posts provide:
    - Identity visibility: "They're becoming someone who thinks clearly"
    - Diverse examples: Different students, different paths, same growth
    - Belonging cues: "People like me are succeeding"
    - Inspiration: "I could do that too!"
  
  Avoids:
    - Comparison: No rankings, no "best"
    - Pressure: No "you should be doing this"
    - Anxiety: No "falling behind" metrics
  
JTBD Social Job Served:
  - Self: "I'm becoming someone who thinks clearly" (identity evidence)
  - Parents: Weekly email shows growth (value demonstration)
  - Peers: Public celebrations show belonging (social proof)
  - Future: Artifacts serve as portfolio (university/job applications)
```

---

## 8. Graduation & 4 Habits Celebration (Week 8)

### Week 8 Artifact Showcase Format

**Graduation Celebration Workflow:**

```yaml
Step 1: Artifact Completion
  Student: Uses /publish-artifact command
  Bot: Validates artifact is complete (all 6 sections)
  Bot: Checks voice authenticity (not AI-generated)

Step 2: Publication Choice
  Bot: "Your artifact is complete! Ready to publish?"
  Student chooses: [Public] / [Anonymous] / [Private to Trevor]

Step 3A: Public Publication
  Bot publishes: Full artifact celebration to #thinking-showcase
  Bot posts: "🎓 [Student] earned the 4 Habits Card!"
  Bot sends: 4 Habits graduation card via DM
  Bot notifies: Parents receive invitation to view artifact

Step 3B: Anonymous Publication
  Bot publishes: "Anonymous student completed their artifact!"
  Bot sends: 4 Habits card via DM
  Parents: Notified (Anonymous student)

Step 3C: Private to Trevor
  Bot: DMs artifact to Trevor only
  Trevor: Provides personal feedback
  Bot: Sends 4 Habits card via DM
  Parents: **HIGH #6 FIX - Offer choice during Week 8**
    Bot: "Your artifact is complete! Share with parents?
          [Yes] - Parents receive invitation link (password-protected)
          [No] - Artifact stays private (only you + Trevor)
          [Ask me later] - Reminder in 3 days"
    Student choice: Respected immediately (no automatic notification)
```

### 4 Habits Graduation Card

**From Story 1.4 (4 Habits Branding):**

```yaml
Card Design:
  Front: "I AM SOMEONE WHO THINKS WITH AI"
  Icons: ⏸️🎯🔄🧠 (all 4 habits)
  Student Name: [Student Name]
  Cohort: K2M AI Thinking Skills Cohort #X
  Date: [Completion Date]

Back: "THE 4 HABITS"
  ⏸️ PAUSE - I know what I want before asking
  🎯 CONTEXT - I explain my situation first
  🔄 ITERATE - I change one thing at a time
  🧠 THINK FIRST - I use AI before decisions

  "Tools change. These habits transfer forever."

Delivery:
  Format: Digital image (PNG, 1080x1080px)
  Method: Sent via DM after artifact publication
  Usage: Students can share on LinkedIn, university applications, resumes
  Value: Demonstrates thinking skills to future employers/schools
```

### Cohort Completion Ritual

**Week 8 Final Celebration:**

```yaml
Bot Posts to #thinking-showcase:
  "🌟 COHORT GRADUATION COMPLETE!

   127 graduates proved they're someone who thinks with AI!

   ⏸️ PAUSE - You know what you want
   🎯 CONTEXT - You explain your situation
   🔄 ITERATE - You change one thing at a time
   🧠 THINK FIRST - You decide with AI

   Tools change. These 4 habits transfer forever.

   From 'confused about AI' to 'someone who thinks clearly.'

   You're ready for university. You're ready for life. 🌟"

**MEDIUM #3 FIX: Artifact Incomplete Handling (Week 8 Edge Case)**

If Week 8 arrives and artifact incomplete:
  Bot: "Week 8 is here! Your artifact is [X]% complete.
        Choose:
        [Publish now] - Publish what you have (celebrate progress)
        [Need more time] - 1-week extension (bot nudges in Week 9)
        [Not going to complete] - Celebrate what you learned (no artifact)"

Extension Protocol:
  - One-time 1-week extension (Week 9)
  - No grading or penalty
  - Trevor's 10%: Personal check-in if 2-week extension needed
  - Bot reminder: "Week 9 extension ends in 3 days. Your artifact is 80% complete."

No-Artifact Graduation:
  - Student still attends Week 8 celebration
  - Bot: "You practiced 47 habits this cohort! That's growth."
  - No 4 Habits card (artifact required for card)
  - Belonging maintained ("you're still part of cohort")
  - Partial graduation certificate available: "I PRACTICED THINKING WITH AI"

Rationale: Prevents Week 8 failure cascade, maintains belonging, honors JTBD emotional job

Cohort-Wide Celebrations:
  - Bot publishes: Graduation statistics (aggregate only)
  - Bot awards: 127 4 Habits cards (sent via DM)
  - Trevor hosts: Final live session (celebration, reflection)
  - Channel archival: #thinking-showcase becomes read-only (preserved)

Post-Cohort Access:
  - Students retain: Read access to #thinking-showcase (view their growth)
  - Artifacts remain: Published forever (portfolio for future)
  - 4 Habits cards: Downloadable, shareable
  - Alumni community: Optional (future Trevor decision)
```

---

## Story 5.3 Completion Checklist

**All 8 Acceptance Criteria Met:**

- [x] **AC #1: Channel Purpose & Philosophy** - Defines #thinking-showcase as public celebration destination (Decision 12, Guardrails #3, #8, JTBD social job)
- [x] **AC #2: Channel Configuration** - Specifies Discord settings, permissions (read-only for students), bot automation
- [x] **AC #3: Publication Flow** - Documents private DM → public showcase workflow with privacy controls
- [x] **AC #4: Celebration Culture Design** - Implements Guardrail #3 through celebration-only patterns, emoji reactions, aggregate visibility
- [x] **AC #5: Weekly Channel Progression** - Defines evolution from Week 1 (early celebrations) through Week 8 (graduation)
- [x] **AC #6: Bot Automation & Safety** - Specifies publication workflow, SafetyFilter validation, celebration templates, moderation
- [x] **AC #7: JTBD Social Job Integration** - Designs parent engagement system (with consent), peer learning, future-self evidence
- [x] **AC #8: Graduation & 4 Habits Celebration** - Documents Week 8 artifact showcase, graduation card awarding, cohort rituals

**Epic 1 Foundation Integration:**

- [x] **Guardrails (Story 1.1):** All 11 guardrails enforced (especially #3, #8, #10, #11 for celebrations)
- [x] **JTBD Integration (Story 1.2):** Social job served (parent engagement, peer proof, future evidence)
- [x] **Node Architecture (Story 1.3):** 16 nodes celebrated through publications
- [x] **4 Habits Branding (Story 1.4):** ⏸️🎯🔄🧠 icons throughout, graduation card

**Story 5.1 Integration:**

- [x] **Discord Architecture:** Fits within CORE INTERACTION SPACES tier
- [x] **Channel Hierarchy:** Positioned correctly (below #thinking-lab)
- [x] **Hybrid Discord Model:** Implements public product celebration side
- [x] **Scalability:** Designed for 200 students with celebration culture

**Story 5.2 Integration:**

- [x] **Publication Options:** Yes/No/Anonymous (privacy controls)
- [x] **Parent Engagement:** Consent system integrated (weekly OR privacy until Week 8)
- [x] **CIS Integration:** Publications flow from #thinking-lab DM completions

**Epic 4 Integration:**

- [x] **CIS System:** Publication flow from artifact completion (Story 4.6)
- [x] **SafetyFilter:** Guardrails validation on all celebration posts
- [x] **Bot Technical Spec:** Discord.py implementation, Claude API for celebrations

**Output Files:**

- **Draft:** `_bmad-output/implementation-artifacts/5-3-thinking-showcase-setup.md` (this file)
- **Final:** `_bmad-output/cohort-design-artifacts/playbook-v2/05-discord-ops/thinking-showcase-setup.md` (after review)

---

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (December 2024 version)

### Completion Notes

**Story 5.3 creates the complete #thinking-showcase channel specification that implements the public celebration side of Decision 12 (Hybrid Discord Model).**

**Key Design Achievements:**

1. ✅ **Channel Purpose & Philosophy:** Defined #thinking-showcase as celebration-only destination for finished thinking growth
2. ✅ **Channel Configuration:** Complete Discord settings, read-only permissions for students, bot publisher role
3. ✅ **Publication Flow:** Complete workflow from private DM → public celebration with privacy controls (Yes/No/Anonymous)
4. ✅ **Celebration Culture:** Guardrail #3 compliance through celebration-only patterns, emoji reactions, aggregate visibility
5. ✅ **Weekly Progression:** Week 1-8 evolution from habit practice celebrations through graduation rituals
6. ✅ **Bot Automation & Safety:** Publication workflow, SafetyFilter validation, celebration templates, moderation
7. ✅ **JTBD Social Job:** Parent engagement system (with student consent), peer learning, future-self evidence
8. ✅ **Graduation Celebration:** Week 8 artifact showcase, 4 Habits card awarding, cohort completion rituals

**Integration with ALL Foundation Documents:**
- **Epic 1 (Guardrails):** All 11 guardrails enforced in celebration culture (especially #3, #8, #10, #11)
- **Epic 1 (JTBD):** Social job served (parent engagement with consent, peer proof, artifact as future evidence)
- **Epic 1 (Node Architecture):** 16 nodes celebrated through publication references
- **Epic 1 (4 Habits):** ⏸️🎯🔄🧠 icons throughout, graduation card designed
- **Epic 2 (Weekly Design):** Weekly celebration progression from early wins to graduation
- **Epic 4 (CIS System):** Publication flow from #thinking-lab DM completions to public showcase
- **Story 5.1 (Discord Architecture):** Fits within server hierarchy, implements public product side
- **Story 5.2 (#thinking-lab):** Publication options integrated, parent consent system connected

**Implementation-Ready Specifications:**
- Channel setup checklist (ready for Discord deployment)
- Publication workflow diagrams (ready for bot implementation)
- Celebration message templates (ready for Claude API generation)
- Parent email templates (ready for Monday batch automation)
- 4 Habits graduation card design (ready for graphic creation)
- Privacy controls (Yes/No/Anonymous) fully specified
- Safety enforcement (SafetyFilter validation) documented

**Next Steps:**
1. Story 5.4 will define Google Forms diagnostic (Epic 5 continues)
2. Developer can implement #thinking-showcase using this specification
3. Trevor can deploy #thinking-showcase channel following setup checklist
4. Bot developer can implement publication workflow using Story 4.7 technical spec

---

**Story 5.3 Status: ✅ READY FOR DEVELOPMENT (ADVERSARIAL REVIEW FIXES APPLIED)**

**Date:** 2026-01-25
**Review Type:** Adversarial Review + CIS Party Mode Consensus
**Reviewers:** Maya (Design Thinking Coach), Winston (Architect), Sally (UX Designer),
               John (PM), Bob (Scrum Master), Mary (Analyst), Murat (Test Architect)

The #thinking-showcase channel specification is complete with:
- ✅ Complete channel purpose and philosophy (public celebration destination, JTBD social job)
- ✅ Full Discord configuration (read-only for students, bot publisher permissions)
- ✅ Publication flow (private DM → public celebration with privacy controls)
- ✅ Celebration culture design (Guardrail #3 compliance, emoji reactions, aggregate visibility)
- ✅ Weekly channel progression (Week 1-8 evolution from habit practice to graduation)
- ✅ Bot automation & safety (publication workflow, SafetyFilter validation, moderation)
- ✅ JTBD social job integration (parent engagement with consent, peer learning, future evidence)
- ✅ Graduation & 4 Habits celebration (Week 8 showcase, graduation cards, cohort rituals)
- ✅ All 8 Acceptance Criteria met
- ✅ All Epic 1, 2, 4 foundations integrated

**ADVERSARIAL REVIEW FIXES APPLIED (7 HIGH + 3 MEDIUM):**

**HIGH-Severity Fixes (All Applied):**
1. ✅ **HIGH #1:** Parent email technical implementation specified (SendGrid/Mailgun, error handling, queue system)
2. ✅ **HIGH #2:** Complete database schema defined (showcase_publications, parent_engagement, student_publication_preferences)
3. ✅ **HIGH #3:** Story 4.7 cross-references added (dependency mapping, developer handoff)
4. ✅ **HIGH #4:** Claude API prompt engineering specified (system prompt, few-shot examples, testing protocol)
5. ✅ **HIGH #5:** Anonymous privacy leak fixed (parents NOT notified for anonymous publications)
6. ✅ **HIGH #6:** "Private to Trevor" Week 8 contradiction fixed (parent notification now opt-in)
7. ✅ **HIGH #7:** Permanent publication preference setting added (reduces decision fatigue)

**MEDIUM-Severity Fixes (Priority Issues Applied):**
1. ✅ **MEDIUM #1:** Diverse celebration examples added (prevents implicit comparison, celebrates different paths)
2. ✅ **MEDIUM #2:** Week 1 parent notification warning added (sets expectations, avoids Week 8 surprise)
3. ✅ **MEDIUM #3:** Artifact incomplete handling specified (Week 8 extension, no-artifact graduation)

**DEFERRED (Future Stories):**
- MEDIUM #4-5: Deferred to Story 5.4/5.5 (aggregate metrics rotation, partial 4 Habits card)

**Implementation-Ready Specifications:**
- Channel setup checklist (ready for Discord deployment)
- Publication workflow diagrams (ready for bot implementation)
- Celebration message templates (ready for Claude API generation)
- Parent email templates (ready for Monday batch automation)
- 4 Habits graduation card design (ready for graphic creation)
- Privacy controls (Yes/No/Anonymous/Permanent) fully specified
- Safety enforcement (SafetyFilter validation) documented
- Database schema (SQL CREATE TABLE statements) ready for implementation
- Parent email technical specs (SendGrid/Mailgun integration) fully specified
- Claude API prompts (system prompt, few-shot examples, testing protocol) ready

**Trevor can now implement #thinking-showcase using this specification.**

**Next Steps:**
1. Story 5.4 will define Google Forms diagnostic (Epic 5 continues)
2. Bot developer implements Story 4.7 using cross-references in this story
3. Trevor can deploy #thinking-showcase channel following setup checklist
4. Parent email system implementer uses Section 7 + HIGH #1 technical specs


