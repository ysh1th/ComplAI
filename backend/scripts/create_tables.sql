-- ComplAI Supabase Schema Migration
-- Run this in the Supabase SQL Editor to create all tables

-- 1. profiles
CREATE TABLE IF NOT EXISTS profiles (
    user_id TEXT PRIMARY KEY,
    age INTEGER NOT NULL,
    country TEXT NOT NULL,
    full_name TEXT NOT NULL,
    income_level TEXT NOT NULL CHECK (income_level IN ('low', 'medium', 'high')),
    occupation TEXT NOT NULL,
    kyc_status TEXT NOT NULL CHECK (kyc_status IN ('verified', 'pending')),
    risk_profile TEXT NOT NULL CHECK (risk_profile IN ('low', 'medium', 'high')),
    historical_countries TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. baselines
CREATE TABLE IF NOT EXISTS baselines (
    user_id TEXT PRIMARY KEY REFERENCES profiles(user_id) ON DELETE CASCADE,
    avg_tx_amount_usd DOUBLE PRECISION NOT NULL DEFAULT 100.0,
    avg_daily_total_usd DOUBLE PRECISION NOT NULL DEFAULT 300.0,
    avg_tx_per_day INTEGER NOT NULL DEFAULT 3,
    std_dev_amount DOUBLE PRECISION NOT NULL DEFAULT 30.0,
    normal_hour_range INTEGER[] NOT NULL DEFAULT '{9,18}',
    excluded_anomalies_count INTEGER NOT NULL DEFAULT 0,
    min_tx_amount_usd DOUBLE PRECISION DEFAULT 0.0,
    max_tx_amount_usd DOUBLE PRECISION DEFAULT 0.0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. risk_state
CREATE TABLE IF NOT EXISTS risk_state (
    user_id TEXT PRIMARY KEY REFERENCES profiles(user_id) ON DELETE CASCADE,
    risk_score INTEGER NOT NULL DEFAULT 0,
    risk_band TEXT NOT NULL DEFAULT 'CLEAN' CHECK (risk_band IN ('HIGH', 'MEDIUM', 'LOW', 'CLEAN')),
    risk_profile TEXT NOT NULL DEFAULT 'low' CHECK (risk_profile IN ('low', 'medium', 'high')),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. transactions
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    batch_id TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    transaction_amount_usd DOUBLE PRECISION NOT NULL,
    transaction_currency TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    transaction_country TEXT NOT NULL,
    transaction_city TEXT NOT NULL,
    hour_of_day INTEGER,
    time_since_last_sec INTEGER,
    previous_country TEXT,
    previous_timestamp TEXT,
    distance_km DOUBLE PRECISION,
    actual_travel_hours DOUBLE PRECISION,
    daily_total_usd DOUBLE PRECISION,
    tx_count_per_day INTEGER,
    is_new_country BOOLEAN,
    is_preprocessed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_batch_id ON transactions(batch_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC);

-- 5. compliance_state
CREATE TABLE IF NOT EXISTS compliance_state (
    jurisdiction_code TEXT PRIMARY KEY,
    jurisdiction TEXT NOT NULL,
    current_version TEXT NOT NULL DEFAULT 'v1',
    old_regulations JSONB NOT NULL DEFAULT '[]',
    new_regulations JSONB NOT NULL DEFAULT '[]',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. rulebooks (versioned)
CREATE TABLE IF NOT EXISTS rulebooks (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_code TEXT NOT NULL,
    version TEXT NOT NULL,
    rulebook JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(jurisdiction_code, version)
);

CREATE INDEX IF NOT EXISTS idx_rulebooks_active ON rulebooks(jurisdiction_code, is_active) WHERE is_active = TRUE;

-- 7. new_regulations (available to push)
CREATE TABLE IF NOT EXISTS new_regulations (
    id BIGSERIAL PRIMARY KEY,
    jurisdiction_code TEXT NOT NULL,
    regulation_update_id TEXT NOT NULL UNIQUE,
    update_title TEXT NOT NULL,
    summary TEXT NOT NULL,
    date_effective TEXT NOT NULL,
    is_pushed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_new_regulations_jurisdiction ON new_regulations(jurisdiction_code);

-- 8. agent_traces
CREATE TABLE IF NOT EXISTS agent_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_type TEXT NOT NULL CHECK (trace_type IN ('transaction_analysis', 'compliance_push')),
    user_id TEXT REFERENCES profiles(user_id),
    jurisdiction_code TEXT,
    status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    result JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_agent_traces_user ON agent_traces(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_traces_status ON agent_traces(status);

-- 9. agent_steps
CREATE TABLE IF NOT EXISTS agent_steps (
    id BIGSERIAL PRIMARY KEY,
    trace_id UUID NOT NULL REFERENCES agent_traces(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    agent TEXT NOT NULL,
    icon TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    duration_ms INTEGER NOT NULL,
    retry_count INTEGER DEFAULT 0,
    retry_type TEXT CHECK (retry_type IN ('technical', 'logical', NULL)),
    output JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_steps_trace ON agent_steps(trace_id, step_order);

-- 10. compliance_drafts (HITL)
CREATE TABLE IF NOT EXISTS compliance_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jurisdiction_code TEXT NOT NULL,
    proposed_version TEXT NOT NULL,
    rulebook JSONB NOT NULL,
    previous_rulebook JSONB,
    changes_description TEXT,
    summary TEXT,
    comparison_points JSONB,
    impact_analysis TEXT,
    agent_chain JSONB,
    regulation_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_compliance_drafts_status ON compliance_drafts(jurisdiction_code, status);

-- Enable Realtime for key tables
ALTER PUBLICATION supabase_realtime ADD TABLE agent_traces;
ALTER PUBLICATION supabase_realtime ADD TABLE agent_steps;
ALTER PUBLICATION supabase_realtime ADD TABLE risk_state;
ALTER PUBLICATION supabase_realtime ADD TABLE compliance_drafts;
