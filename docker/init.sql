-- ECO-SYNC V2X — PostgreSQL Schema
-- Persistent storage: sessions, bus telemetry, V2X messages, decisions, metrics

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Simulation sessions ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at    TIMESTAMPTZ,
    mode        VARCHAR(16) NOT NULL DEFAULT 'agentic', -- agentic | static
    num_buses   SMALLINT NOT NULL DEFAULT 6,
    route_id    VARCHAR(32) DEFAULT 'MF-378',
    status      VARCHAR(16) DEFAULT 'running'           -- running | stopped
);

-- ── Bus telemetry snapshots (sampled every 5 ticks) ─────────────────────────
CREATE TABLE IF NOT EXISTS bus_telemetry (
    id              BIGSERIAL PRIMARY KEY,
    session_id      UUID REFERENCES sessions(id) ON DELETE CASCADE,
    ts              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    bus_id          VARCHAR(16) NOT NULL,
    lat             DOUBLE PRECISION NOT NULL,
    lng             DOUBLE PRECISION NOT NULL,
    path_index      INT NOT NULL,
    passengers      SMALLINT,
    speed_kmh       FLOAT,
    action          VARCHAR(16),           -- PROCEED | HOLD | SKIP_STOP
    headway_ahead_s INT,
    headway_behind_s INT
);
CREATE INDEX idx_tel_session ON bus_telemetry(session_id, ts DESC);

-- ── V2X messages (BSM, TIM, DEBATE) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS v2x_log (
    id          BIGSERIAL PRIMARY KEY,
    session_id  UUID REFERENCES sessions(id) ON DELETE CASCADE,
    ts          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    msg_type    VARCHAR(16) NOT NULL,  -- BSM | TIM | DEBATE | ATIS | DECISION
    topic       VARCHAR(128),
    sender      VARCHAR(32),
    receiver    VARCHAR(32),           -- NULL = broadcast
    payload     JSONB NOT NULL
);
CREATE INDEX idx_v2x_session ON v2x_log(session_id, ts DESC);
CREATE INDEX idx_v2x_type ON v2x_log(msg_type);

-- ── Agent decisions ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS decisions (
    id              BIGSERIAL PRIMARY KEY,
    session_id      UUID REFERENCES sessions(id) ON DELETE CASCADE,
    ts              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    stop_name       VARCHAR(64),
    bus_1_id        VARCHAR(16),
    bus_2_id        VARCHAR(16),
    bus_1_action    VARCHAR(16),
    bus_2_action    VARCHAR(16),
    reasoning       TEXT,
    llm_model       VARCHAR(64),
    latency_ms      INT,
    headway_before  INT,
    headway_after   INT
);

-- ── Traffic events ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS traffic_events (
    id          BIGSERIAL PRIMARY KEY,
    session_id  UUID REFERENCES sessions(id) ON DELETE CASCADE,
    ts          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    location    VARCHAR(64),
    severity    VARCHAR(16),
    description TEXT,
    duration_s  INT
);

-- ── Per-minute metrics snapshots ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS metrics (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          UUID REFERENCES sessions(id) ON DELETE CASCADE,
    ts                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tick                INT,
    mode                VARCHAR(16),
    avg_headway_s       FLOAT,
    headway_variance    FLOAT,
    bunching_count      INT DEFAULT 0,
    total_decisions     INT DEFAULT 0,
    holds               INT DEFAULT 0,
    skips               INT DEFAULT 0,
    proceeds            INT DEFAULT 0,
    passengers_served   INT DEFAULT 0
);
CREATE INDEX idx_metrics_session ON metrics(session_id, ts DESC);
