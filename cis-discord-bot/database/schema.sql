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
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_students_cohort ON students(cohort_id);
CREATE INDEX IF NOT EXISTS idx_students_week ON students(current_week);
CREATE INDEX IF NOT EXISTS idx_students_zone ON students(zone);

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
    student_id_hash TEXT,  -- Privacy: hashed student Discord ID
    event_type TEXT,       -- "agent_used", "stuck_detected", "milestone_reached", "zone_shift"
    metadata TEXT,         -- JSON: {agent: "framer", week: 4, zone: "zone_1"} NOT full messages
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id_hash) REFERENCES students(discord_id)
);

-- Indexes for observability queries
CREATE INDEX IF NOT EXISTS idx_observability_student ON observability_events(student_id_hash);
CREATE INDEX IF NOT EXISTS idx_observability_type ON observability_events(event_type);
CREATE INDEX IF NOT EXISTS idx_observability_timestamp ON observability_events(timestamp);
