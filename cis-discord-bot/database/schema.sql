-- K2M CIS Bot - Database Schema
-- Story 4.7 Implementation: StudentContext & Database Schema
-- Database: SQLite (Cohort 1), migration path to PostgreSQL (Cohort 2+)

-- ============================================================
-- STUDENTS TABLE
-- Core student data and current state
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    discord_id TEXT PRIMARY KEY,
    cohort_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    current_week INTEGER DEFAULT 1,
    current_state TEXT DEFAULT 'none',  -- framing, exploring, challenging, synthesizing, complete
    zone TEXT DEFAULT 'zone_0',  -- zone_0, zone_1, zone_2, zone_3, zone_4
    jtbd_concern TEXT DEFAULT 'career_direction',  -- university_application, exam_anxiety, etc.
    emotional_state TEXT DEFAULT 'curious',  -- anxious, curious, confident, stuck, excited
    unlocked_agents TEXT DEFAULT '["frame"]',  -- JSON array
    artifact_progress INTEGER DEFAULT 0,  -- 0-100
    interaction_count INTEGER DEFAULT 0,
    last_interaction TEXT,  -- ISO timestamp
    cluster_id INTEGER DEFAULT 1,  -- Task 4.3: Cluster assignment (1-8)
    last_name TEXT,  -- Task 4.3: Last name for cluster assignment
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_students_cohort ON students(cohort_id);
CREATE INDEX IF NOT EXISTS idx_students_week ON students(current_week);
CREATE INDEX IF NOT EXISTS idx_students_zone ON students(zone);
CREATE INDEX IF NOT EXISTS idx_students_cluster ON students(cluster_id);  -- Task 4.3

-- ============================================================
-- HABIT PRACTICE TABLE
-- Track practice of 4 Habits (Pause, Context, Iterate, Think First)
-- ============================================================
CREATE TABLE IF NOT EXISTS habit_practice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    habit_id INTEGER NOT NULL,  -- 1=Pause, 2=Context, 3=Iterate, 4=Think
    practiced_count INTEGER DEFAULT 0,
    last_practiced TEXT,
    confidence TEXT DEFAULT 'emerging',  -- emerging, growing, strong
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE,
    UNIQUE(student_id, habit_id)
);

-- Index for habit tracking queries
CREATE INDEX IF NOT EXISTS idx_habit_student ON habit_practice(student_id);

-- ============================================================
-- CONVERSATIONS TABLE
-- Message history for context window and API tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    agent TEXT NOT NULL,  -- framer, explorer, challenger, synthesizer
    role TEXT NOT NULL,  -- user, assistant
    content TEXT NOT NULL,
    tokens INTEGER,
    cost_usd REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

-- Indexes for conversation history queries
CREATE INDEX IF NOT EXISTS idx_conversations_student ON conversations(student_id);
CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(student_id, agent);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);

-- ============================================================
-- ARTIFACT PROGRESS TABLE
-- Track 6-section artifact creation (Story 4.6)
-- ============================================================
CREATE TABLE IF NOT EXISTS artifact_progress (
    student_id TEXT PRIMARY KEY,
    section_1_question TEXT,
    section_2_reframed TEXT,
    section_3_explored TEXT,
    section_4_challenged TEXT,
    section_5_concluded TEXT,
    section_6_reflection TEXT,
    completed_sections TEXT DEFAULT '[]',  -- JSON array
    current_section INTEGER DEFAULT 0,
    status TEXT DEFAULT 'not_started',  -- not_started, in_progress, completed, published
    started_at TEXT,
    last_activity TEXT,
    completed_at TEXT,
    published_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

-- ============================================================
-- API USAGE TABLE
-- Cost monitoring and budget tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    student_count INTEGER,
    total_interactions INTEGER,
    total_tokens INTEGER,
    total_cost_usd REAL,
    cached_tokens INTEGER,
    cached_savings_usd REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- ============================================================
-- OBSERVABILITY EVENTS TABLE
-- Journey tracking for Trevor dashboard (Task 1.7)
-- ============================================================
CREATE TABLE IF NOT EXISTS observability_events (
    id INTEGER PRIMARY KEY,
    student_id_hash TEXT,  -- Privacy: SHA256[:16] of discord_id — NOT a FK (hashed, can't join)
    event_type TEXT,       -- "agent_used", "stuck_detected", "milestone_reached", "zone_shift"
    metadata TEXT,         -- JSON: {agent: "framer", week: 4, zone: "zone_1"} NOT full messages
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    -- No FK: student_id_hash is hashed for privacy, not equal to students.discord_id
);

-- Indexes for observability queries
CREATE INDEX IF NOT EXISTS idx_observability_student ON observability_events(student_id_hash);
CREATE INDEX IF NOT EXISTS idx_observability_type ON observability_events(event_type);
CREATE INDEX IF NOT EXISTS idx_observability_timestamp ON observability_events(timestamp);

-- ============================================================
-- STUDENT CONSENTS TABLE
-- Guardrail #8 consent gate for private journey inspection
-- ============================================================
CREATE TABLE IF NOT EXISTS student_consents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id_hash TEXT NOT NULL,  -- Privacy: hashed student id
    consent_type TEXT NOT NULL,     -- e.g. journey_inspection
    granted_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    source TEXT,                    -- e.g. student_dm_phrase
    UNIQUE(student_id_hash, consent_type)
);

CREATE INDEX IF NOT EXISTS idx_consents_lookup ON student_consents(student_id_hash, consent_type);
CREATE INDEX IF NOT EXISTS idx_consents_expiry ON student_consents(expires_at);

-- ============================================================
-- DAILY PARTICIPATION TABLE (Task 2.2)
-- Track daily student posting activity and bot reactions
-- ============================================================
CREATE TABLE IF NOT EXISTS daily_participation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    date TEXT NOT NULL,  -- YYYY-MM-DD format
    week_number INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,  -- Monday, Tuesday, Wednesday, Thursday, Friday

    -- Posting activity
    has_posted INTEGER DEFAULT 0,
    first_post_time TEXT,
    post_count INTEGER DEFAULT 0,

    -- Bot reactions
    bot_reacted INTEGER DEFAULT 0,
    reaction_time TEXT,

    -- Engagement depth
    engagement_score INTEGER DEFAULT 0,  -- 1-6 scale based on post quality
    reflection_quality TEXT,  -- high, medium, low (for Friday reflections)

    -- Inactivity tracking
    flagged_inactive INTEGER DEFAULT 0,
    nudge_sent INTEGER DEFAULT 0,
    nudge_time TEXT,

    FOREIGN KEY (discord_id) REFERENCES students(discord_id) ON DELETE CASCADE,
    UNIQUE(discord_id, date)
);

-- Indexes for participation queries
CREATE INDEX IF NOT EXISTS idx_participation_date ON daily_participation(date);
CREATE INDEX IF NOT EXISTS idx_participation_student ON daily_participation(discord_id);
CREATE INDEX IF NOT EXISTS idx_participation_flagged ON daily_participation(flagged_inactive);
CREATE INDEX IF NOT EXISTS idx_participation_week ON daily_participation(week_number);

-- ============================================================
-- ESCALATIONS TABLE (Task 2.4)
-- Track 4-level escalation system for student stuckness patterns
-- ============================================================
CREATE TABLE IF NOT EXISTS escalations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    escalation_level INTEGER NOT NULL,  -- 1=Yellow (bot), 2=Orange (Trevor alert), 3=Red (Trevor DM), 4=Crisis
    notes TEXT,  -- Escalation details: days stuck, crisis type, etc.
    resolved INTEGER DEFAULT 0,  -- 0=active, 1=resolved
    resolved_at TEXT,
    resolution_notes TEXT,
    escalated_at TEXT NOT NULL,
    FOREIGN KEY (discord_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

-- Indexes for escalation queries
CREATE INDEX IF NOT EXISTS idx_escalations_student ON escalations(discord_id);
CREATE INDEX IF NOT EXISTS idx_escalations_level ON escalations(escalation_level);
CREATE INDEX IF NOT EXISTS idx_escalations_date ON escalations(escalated_at);

-- ============================================================
-- WEEKLY REFLECTIONS TABLE (Task 2.5)
-- Track Friday reflections and week unlock gating
-- ============================================================
CREATE TABLE IF NOT EXISTS weekly_reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    week_number INTEGER NOT NULL,

    -- Reflection submission
    reflection_content TEXT,  -- Student's Friday reflection
    proof_of_work TEXT,  -- One sentence showing AI understood them
    submitted INTEGER DEFAULT 0,  -- 0=no, 1=yes
    submitted_at TEXT,

    -- Week unlock tracking
    next_week_unlocked INTEGER DEFAULT 0,  -- 0=locked, 1=unlocked
    unlocked_at TEXT,

    -- Manual override tracking
    manually_unlocked INTEGER DEFAULT 0,  -- 0=no, 1=yes
    unlocked_by TEXT,  -- Trevor's discord_id
    unlock_reason TEXT,  -- illness, emergency, accelerated, etc.

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (discord_id) REFERENCES students(discord_id) ON DELETE CASCADE,
    UNIQUE(discord_id, week_number)
);

-- Indexes for reflection queries
CREATE INDEX IF NOT EXISTS idx_reflections_student ON weekly_reflections(discord_id);
CREATE INDEX IF NOT EXISTS idx_reflections_week ON weekly_reflections(week_number);
CREATE INDEX IF NOT EXISTS idx_reflections_submitted ON weekly_reflections(submitted);
CREATE INDEX IF NOT EXISTS idx_reflections_unlocked ON weekly_reflections(next_week_unlocked);

-- ============================================================
-- AGENT UNLOCK ANNOUNCEMENTS TABLE (Task 3.4)
-- Track graduated agent unlock announcements per Decision 11
-- ============================================================
CREATE TABLE IF NOT EXISTS agent_unlock_announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_number INTEGER NOT NULL,
    agents_unlocked TEXT NOT NULL,  -- JSON array: ["frame", "diverge", "challenge"]
    announced_at TEXT NOT NULL,
    channel_id TEXT,
    UNIQUE(week_number)
);

-- Index for unlock announcement queries
CREATE INDEX IF NOT EXISTS idx_unlock_announcements_week ON agent_unlock_announcements(week_number);

-- ============================================================
-- SHOWCASE PUBLICATIONS TABLE (Task 3.5)
-- Track all publications to #thinking-showcase channel (Decision 12)
-- ============================================================
CREATE TABLE IF NOT EXISTS showcase_publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    publication_type TEXT NOT NULL,  -- 'habit_practice' OR 'artifact_completion'
    visibility_level TEXT NOT NULL,  -- 'public' OR 'anonymous' OR 'private'
    celebration_message TEXT NOT NULL,
    habits_demonstrated TEXT,  -- JSON array: ["⏸️", "🎯", "🔄", "🧠"]
    nodes_mastered TEXT,  -- JSON array: [1.3, 2.1, 3.2]
    reactions_count INTEGER DEFAULT 0,
    parent_email_included INTEGER DEFAULT 0,
    artifact_id INTEGER,  -- FK to artifact_progress if artifact_completion
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

-- Indexes for publication queries
CREATE INDEX IF NOT EXISTS idx_showcase_student ON showcase_publications(student_id);
CREATE INDEX IF NOT EXISTS idx_showcase_type ON showcase_publications(publication_type);
CREATE INDEX IF NOT EXISTS idx_showcase_timestamp ON showcase_publications(timestamp);

-- ============================================================
-- STUDENT PUBLICATION PREFERENCES TABLE (Task 3.5)
-- Store student's permanent publication settings to reduce decision fatigue
-- ============================================================
CREATE TABLE IF NOT EXISTS student_publication_preferences (
    student_id TEXT PRIMARY KEY,
    default_preference TEXT DEFAULT 'always_ask',  -- 'always_ask', 'always_yes', 'always_no', 'week8_only'
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

-- Index for preference queries
CREATE INDEX IF NOT EXISTS idx_pub_prefs_student ON student_publication_preferences(student_id);

-- ============================================================
-- CLUSTER ASSIGNMENT TABLE (Task 4.3)
-- Track cluster assignments and voice channels for live sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS cluster_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT NOT NULL,
    cluster_id INTEGER NOT NULL,  -- 1-8 (A-F, G-L, M-R, S-Z, repeated)
    last_name TEXT,  -- Student's last name for assignment
    assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discord_id) REFERENCES students(discord_id) ON DELETE CASCADE,
    UNIQUE(discord_id)
);

-- Index for cluster queries
CREATE INDEX IF NOT EXISTS idx_cluster_student ON cluster_assignments(discord_id);
CREATE INDEX IF NOT EXISTS idx_cluster_id ON cluster_assignments(cluster_id);

-- ============================================================
-- VOICE CHANNELS TABLE (Task 4.3)
-- Track temporary voice channels for cluster live sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS voice_channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id INTEGER NOT NULL,
    channel_id TEXT NOT NULL,  -- Discord channel ID
    channel_name TEXT NOT NULL,
    session_date TEXT NOT NULL,  -- ISO timestamp of session
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    deleted_at TEXT,
    is_active INTEGER DEFAULT 1,  -- 0=deleted, 1=active
    UNIQUE(channel_id)
);

-- Index for voice channel queries
CREATE INDEX IF NOT EXISTS idx_voice_cluster ON voice_channels(cluster_id);
CREATE INDEX IF NOT EXISTS idx_voice_active ON voice_channels(is_active);

-- ============================================================
-- CLUSTER SESSION ATTENDANCE TABLE (Task 4.3)
-- Track attendance for cluster live sessions
-- ============================================================
CREATE TABLE IF NOT EXISTS cluster_session_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id INTEGER NOT NULL,
    session_date TEXT NOT NULL,  -- ISO timestamp
    attendees TEXT,  -- JSON array of discord_ids
    absent_count INTEGER DEFAULT 0,
    total_students INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cluster_id, session_date)
);

-- Index for attendance queries
CREATE INDEX IF NOT EXISTS idx_attendance_cluster ON cluster_session_attendance(cluster_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON cluster_session_attendance(session_date);

-- ============================================================
-- PARENT ENGAGEMENT TABLE (Task 4.6)
-- Store parent email consent and contact information per Story 5.3
-- ============================================================
CREATE TABLE IF NOT EXISTS parent_engagement (
    student_id TEXT PRIMARY KEY,  -- Discord user ID
    parent_email TEXT NOT NULL,
    consent_preference TEXT NOT NULL,  -- 'share_weekly' OR 'privacy_first'
    consent_date TEXT DEFAULT CURRENT_TIMESTAMP,
    last_email_sent TEXT,
    unsubscribe_token TEXT UNIQUE,  -- For parent opt-out link
    parent_opted_out INTEGER DEFAULT 0,  -- Parent unsubscribed from all future emails
    parent_opted_out_at TEXT,
    parent_email_status TEXT DEFAULT 'active',  -- active, opted_out, bounced
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

-- Indexes for parent engagement queries
CREATE INDEX IF NOT EXISTS idx_parent_consent ON parent_engagement(consent_preference);
CREATE INDEX IF NOT EXISTS idx_parent_email_sent ON parent_engagement(last_email_sent);
CREATE INDEX IF NOT EXISTS idx_parent_unsubscribe ON parent_engagement(unsubscribe_token);
CREATE INDEX IF NOT EXISTS idx_parent_opted_out ON parent_engagement(parent_opted_out);

-- ============================================================
-- PARENT EMAIL LOG TABLE (Task 4.6)
-- Track all parent emails sent for monitoring and debugging
-- ============================================================
CREATE TABLE IF NOT EXISTS parent_email_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    parent_email TEXT NOT NULL,
    email_type TEXT NOT NULL,  -- 'weekly_update', 'week8_showcase', 'artifact_completion'
    subject TEXT NOT NULL,
    sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,  -- 'sent', 'failed', 'bounced', 'skipped'
    error_message TEXT,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

-- Indexes for email log queries
CREATE INDEX IF NOT EXISTS idx_email_log_student ON parent_email_log(student_id);
CREATE INDEX IF NOT EXISTS idx_email_log_date ON parent_email_log(sent_at);
CREATE INDEX IF NOT EXISTS idx_email_log_status ON parent_email_log(status);
