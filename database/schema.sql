-- Virtual Client Database Schema
-- SQLite implementation

-- Client Profiles Table
CREATE TABLE IF NOT EXISTS client_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    race TEXT,
    gender TEXT,
    socioeconomic_status TEXT,
    issues TEXT,  -- JSON array
    background_story TEXT,
    personality_traits TEXT,  -- JSON array
    communication_style TEXT,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Evaluation Rubrics Table
CREATE TABLE IF NOT EXISTS evaluation_rubrics (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    criteria TEXT NOT NULL,  -- JSON array of criteria objects
    total_weight REAL DEFAULT 1.0,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    client_profile_id TEXT NOT NULL,
    rubric_id TEXT NOT NULL,
    messages TEXT DEFAULT '[]',  -- JSON array of messages
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    evaluation_result_id TEXT,
    session_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_profile_id) REFERENCES client_profiles(id),
    FOREIGN KEY (rubric_id) REFERENCES evaluation_rubrics(id)
);

-- Evaluations Table
CREATE TABLE IF NOT EXISTS evaluations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    rubric_id TEXT NOT NULL,
    overall_score REAL NOT NULL,
    total_possible REAL NOT NULL,
    percentage_score REAL NOT NULL,
    criteria_scores TEXT NOT NULL,  -- JSON array of criterion scores
    feedback TEXT,
    strengths TEXT,  -- JSON array
    improvements TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id),
    FOREIGN KEY (rubric_id) REFERENCES evaluation_rubrics(id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sessions_student ON sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_client ON sessions(client_profile_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_evaluations_student ON evaluations(student_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_session ON evaluations(session_id);
CREATE INDEX IF NOT EXISTS idx_client_profiles_creator ON client_profiles(created_by);
CREATE INDEX IF NOT EXISTS idx_rubrics_creator ON evaluation_rubrics(created_by);
