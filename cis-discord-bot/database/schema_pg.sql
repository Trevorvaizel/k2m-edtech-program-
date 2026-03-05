-- K2M CIS Bot — PostgreSQL Production Schema
-- Task 7.6: Full PostgreSQL migration (promoted from 6.6)
-- Decisions: H-03, H-06, B-01, H-05 + GAP FIX #3
-- Do NOT run against SQLite. Use schema.sql for local/test environments.

-- ============================================================
-- STUDENTS TABLE (with Sprint 7 new columns)
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    discord_id TEXT PRIMARY KEY,
    cohort_id TEXT NOT NULL DEFAULT 'cohort-1',
    start_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    current_week INTEGER DEFAULT 1,
    current_state TEXT DEFAULT 'none',
    zone TEXT DEFAULT 'zone_0',
    jtbd_concern TEXT DEFAULT 'career_direction',
    emotional_state TEXT DEFAULT 'curious',
    unlocked_agents TEXT DEFAULT '["frame"]',
    artifact_progress INTEGER DEFAULT 0,
    interaction_count INTEGER DEFAULT 0,
    last_interaction TEXT,
    cluster_id INTEGER DEFAULT 1,
    last_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Sprint 7 / Decision B-01: unique invite link match key
    invite_code VARCHAR(20),

    -- Sprint 7 / Decision H-05 + GAP FIX #6: onboarding stop tracking
    onboarding_stop INTEGER DEFAULT 0,
    onboarding_stop_0_complete BOOLEAN DEFAULT FALSE,

    -- Sprint 7 / GAP FIX #3: manual override guard for nightly Sheets sync
    manual_override_timestamp TIMESTAMP,

    -- Sprint 7: enrollment fields synced from Google Sheets (Decision H-06)
    enrollment_email TEXT,
    enrollment_name TEXT,
    discord_username TEXT,
    enrollment_status TEXT DEFAULT 'pending',
    payment_status TEXT DEFAULT 'pending'
);

CREATE INDEX IF NOT EXISTS idx_students_cohort ON students(cohort_id);
CREATE INDEX IF NOT EXISTS idx_students_week ON students(current_week);
CREATE INDEX IF NOT EXISTS idx_students_zone ON students(zone);
CREATE INDEX IF NOT EXISTS idx_students_cluster ON students(cluster_id);
CREATE INDEX IF NOT EXISTS idx_students_invite ON students(invite_code);
CREATE INDEX IF NOT EXISTS idx_students_onboarding ON students(onboarding_stop);

-- ============================================================
-- HABIT PRACTICE TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS habit_practice (
    id BIGSERIAL PRIMARY KEY,
    student_id TEXT NOT NULL,
    habit_id INTEGER NOT NULL,
    practiced_count INTEGER DEFAULT 0,
    last_practiced TEXT,
    confidence TEXT DEFAULT 'emerging',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE,
    UNIQUE(student_id, habit_id)
);

CREATE INDEX IF NOT EXISTS idx_habit_student ON habit_practice(student_id);

-- ============================================================
-- CONVERSATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    student_id TEXT NOT NULL,
    agent TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER,
    cost_usd DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conversations_student ON conversations(student_id);
CREATE INDEX IF NOT EXISTS idx_conversations_agent ON conversations(student_id, agent);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);

-- ============================================================
-- ARTIFACT PROGRESS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS artifact_progress (
    student_id TEXT PRIMARY KEY,
    section_1_question TEXT,
    section_2_reframed TEXT,
    section_3_explored TEXT,
    section_4_challenged TEXT,
    section_5_concluded TEXT,
    section_6_reflection TEXT,
    completed_sections TEXT DEFAULT '[]',
    current_section INTEGER DEFAULT 0,
    status TEXT DEFAULT 'not_started',
    started_at TIMESTAMP,
    last_activity TIMESTAMP,
    completed_at TIMESTAMP,
    published_at TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

-- ============================================================
-- API USAGE TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS api_usage (
    id BIGSERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    student_count INTEGER,
    total_interactions INTEGER,
    total_tokens INTEGER,
    total_cost_usd DOUBLE PRECISION,
    cached_tokens INTEGER,
    cached_savings_usd DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- ============================================================
-- OBSERVABILITY EVENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS observability_events (
    id BIGSERIAL PRIMARY KEY,
    student_id_hash TEXT,
    event_type TEXT,
    metadata TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_observability_student ON observability_events(student_id_hash);
CREATE INDEX IF NOT EXISTS idx_observability_type ON observability_events(event_type);
CREATE INDEX IF NOT EXISTS idx_observability_timestamp ON observability_events(timestamp);

-- ============================================================
-- STUDENT CONSENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS student_consents (
    id BIGSERIAL PRIMARY KEY,
    student_id_hash TEXT NOT NULL,
    consent_type TEXT NOT NULL,
    granted_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    source TEXT,
    UNIQUE(student_id_hash, consent_type)
);

CREATE INDEX IF NOT EXISTS idx_consents_lookup ON student_consents(student_id_hash, consent_type);
CREATE INDEX IF NOT EXISTS idx_consents_expiry ON student_consents(expires_at);

-- ============================================================
-- DAILY PARTICIPATION TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS daily_participation (
    id BIGSERIAL PRIMARY KEY,
    discord_id TEXT NOT NULL,
    date TEXT NOT NULL,
    week_number INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    has_posted INTEGER DEFAULT 0,
    first_post_time TEXT,
    post_count INTEGER DEFAULT 0,
    bot_reacted INTEGER DEFAULT 0,
    reaction_time TEXT,
    engagement_score INTEGER DEFAULT 0,
    reflection_quality TEXT,
    flagged_inactive INTEGER DEFAULT 0,
    nudge_sent INTEGER DEFAULT 0,
    nudge_time TEXT,
    FOREIGN KEY (discord_id) REFERENCES students(discord_id) ON DELETE CASCADE,
    UNIQUE(discord_id, date)
);

CREATE INDEX IF NOT EXISTS idx_participation_date ON daily_participation(date);
CREATE INDEX IF NOT EXISTS idx_participation_student ON daily_participation(discord_id);
CREATE INDEX IF NOT EXISTS idx_participation_flagged ON daily_participation(flagged_inactive);
CREATE INDEX IF NOT EXISTS idx_participation_week ON daily_participation(week_number);

-- ============================================================
-- ESCALATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS escalations (
    id BIGSERIAL PRIMARY KEY,
    discord_id TEXT NOT NULL,
    escalation_level INTEGER NOT NULL,
    notes TEXT,
    resolved INTEGER DEFAULT 0,
    resolved_at TEXT,
    resolution_notes TEXT,
    escalated_at TEXT NOT NULL,
    FOREIGN KEY (discord_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_escalations_student ON escalations(discord_id);
CREATE INDEX IF NOT EXISTS idx_escalations_level ON escalations(escalation_level);
CREATE INDEX IF NOT EXISTS idx_escalations_date ON escalations(escalated_at);

-- ============================================================
-- WEEKLY REFLECTIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS weekly_reflections (
    id BIGSERIAL PRIMARY KEY,
    discord_id TEXT NOT NULL,
    week_number INTEGER NOT NULL,
    reflection_content TEXT,
    proof_of_work TEXT,
    submitted INTEGER DEFAULT 0,
    submitted_at TEXT,
    next_week_unlocked INTEGER DEFAULT 0,
    unlocked_at TEXT,
    manually_unlocked INTEGER DEFAULT 0,
    unlocked_by TEXT,
    unlock_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discord_id) REFERENCES students(discord_id) ON DELETE CASCADE,
    UNIQUE(discord_id, week_number)
);

CREATE INDEX IF NOT EXISTS idx_reflections_student ON weekly_reflections(discord_id);
CREATE INDEX IF NOT EXISTS idx_reflections_week ON weekly_reflections(week_number);
CREATE INDEX IF NOT EXISTS idx_reflections_submitted ON weekly_reflections(submitted);
CREATE INDEX IF NOT EXISTS idx_reflections_unlocked ON weekly_reflections(next_week_unlocked);

-- ============================================================
-- AGENT UNLOCK ANNOUNCEMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS agent_unlock_announcements (
    id BIGSERIAL PRIMARY KEY,
    week_number INTEGER NOT NULL,
    agents_unlocked TEXT NOT NULL,
    announced_at TEXT NOT NULL,
    channel_id TEXT,
    UNIQUE(week_number)
);

CREATE INDEX IF NOT EXISTS idx_unlock_announcements_week ON agent_unlock_announcements(week_number);

-- ============================================================
-- SHOWCASE PUBLICATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS showcase_publications (
    id BIGSERIAL PRIMARY KEY,
    student_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    publication_type TEXT NOT NULL,
    visibility_level TEXT NOT NULL,
    celebration_message TEXT NOT NULL,
    habits_demonstrated TEXT,
    nodes_mastered TEXT,
    reactions_count INTEGER DEFAULT 0,
    parent_email_included INTEGER DEFAULT 0,
    artifact_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_showcase_student ON showcase_publications(student_id);
CREATE INDEX IF NOT EXISTS idx_showcase_type ON showcase_publications(publication_type);
CREATE INDEX IF NOT EXISTS idx_showcase_timestamp ON showcase_publications(timestamp);

-- ============================================================
-- STUDENT PUBLICATION PREFERENCES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS student_publication_preferences (
    student_id TEXT PRIMARY KEY,
    default_preference TEXT DEFAULT 'always_ask',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pub_prefs_student ON student_publication_preferences(student_id);

-- ============================================================
-- CLUSTER ASSIGNMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS cluster_assignments (
    id BIGSERIAL PRIMARY KEY,
    discord_id TEXT NOT NULL,
    cluster_id INTEGER NOT NULL,
    last_name TEXT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (discord_id) REFERENCES students(discord_id) ON DELETE CASCADE,
    UNIQUE(discord_id)
);

CREATE INDEX IF NOT EXISTS idx_cluster_student ON cluster_assignments(discord_id);
CREATE INDEX IF NOT EXISTS idx_cluster_id ON cluster_assignments(cluster_id);

-- ============================================================
-- VOICE CHANNELS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS voice_channels (
    id BIGSERIAL PRIMARY KEY,
    cluster_id INTEGER NOT NULL,
    channel_id TEXT NOT NULL,
    channel_name TEXT NOT NULL,
    session_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TEXT,
    is_active INTEGER DEFAULT 1,
    UNIQUE(channel_id)
);

CREATE INDEX IF NOT EXISTS idx_voice_cluster ON voice_channels(cluster_id);
CREATE INDEX IF NOT EXISTS idx_voice_active ON voice_channels(is_active);

-- ============================================================
-- CLUSTER SESSION ATTENDANCE TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS cluster_session_attendance (
    id BIGSERIAL PRIMARY KEY,
    cluster_id INTEGER NOT NULL,
    session_date TEXT NOT NULL,
    attendees TEXT,
    absent_count INTEGER DEFAULT 0,
    total_students INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cluster_id, session_date)
);

CREATE INDEX IF NOT EXISTS idx_attendance_cluster ON cluster_session_attendance(cluster_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON cluster_session_attendance(session_date);

-- ============================================================
-- PARENT ENGAGEMENT TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS parent_engagement (
    student_id TEXT PRIMARY KEY,
    parent_email TEXT NOT NULL,
    consent_preference TEXT NOT NULL,
    consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_email_sent TEXT,
    unsubscribe_token TEXT UNIQUE,
    parent_opted_out INTEGER DEFAULT 0,
    parent_opted_out_at TEXT,
    parent_email_status TEXT DEFAULT 'active',
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_parent_consent ON parent_engagement(consent_preference);
CREATE INDEX IF NOT EXISTS idx_parent_email_sent ON parent_engagement(last_email_sent);
CREATE INDEX IF NOT EXISTS idx_parent_unsubscribe ON parent_engagement(unsubscribe_token);
CREATE INDEX IF NOT EXISTS idx_parent_opted_out ON parent_engagement(parent_opted_out);

-- ============================================================
-- PARENT EMAIL LOG TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS parent_email_log (
    id BIGSERIAL PRIMARY KEY,
    student_id TEXT NOT NULL,
    parent_email TEXT NOT NULL,
    email_type TEXT NOT NULL,
    subject TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    error_message TEXT,
    FOREIGN KEY (student_id) REFERENCES students(discord_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_email_log_student ON parent_email_log(student_id);
CREATE INDEX IF NOT EXISTS idx_email_log_date ON parent_email_log(sent_at);
CREATE INDEX IF NOT EXISTS idx_email_log_status ON parent_email_log(status);
