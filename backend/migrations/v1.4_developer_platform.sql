-- ==============================================================================
-- QRMaster Pro — Migration v1.4: Developer Platform, Webhooks & Smart Routing
-- ==============================================================================
-- Target: Supabase PostgreSQL (portfolio-DB / ap-south-1)
-- Description:
--   1. Adds `scopes` column to `api_keys` for granular REST permissioning.
--   2. Adds `geo_routing_json` and `schedule_*` columns to `dynamic_qrs`.
--   3. Creates `webhook_subscriptions` table for event notifications.
--   4. Creates `webhook_delivery_logs` table for delivery audit trials.
--   5. Configures Supabase Row Level Security (RLS) policies.
-- ==============================================================================

BEGIN;

-- 1. Add scopes to api_keys table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'api_keys' AND column_name = 'scopes') THEN
        ALTER TABLE api_keys ADD COLUMN scopes VARCHAR(255) DEFAULT 'qr:read,qr:write,analytics:read' NOT NULL;
    END IF;
END $$;

-- 2. Add Geo-Fencing & Scheduling to dynamic_qrs table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dynamic_qrs' AND column_name = 'geo_routing_json') THEN
        ALTER TABLE dynamic_qrs ADD COLUMN geo_routing_json TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dynamic_qrs' AND column_name = 'schedule_start_time') THEN
        ALTER TABLE dynamic_qrs ADD COLUMN schedule_start_time VARCHAR(5);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dynamic_qrs' AND column_name = 'schedule_end_time') THEN
        ALTER TABLE dynamic_qrs ADD COLUMN schedule_end_time VARCHAR(5);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dynamic_qrs' AND column_name = 'schedule_timezone') THEN
        ALTER TABLE dynamic_qrs ADD COLUMN schedule_timezone VARCHAR(50);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dynamic_qrs' AND column_name = 'schedule_fallback_url') THEN
        ALTER TABLE dynamic_qrs ADD COLUMN schedule_fallback_url VARCHAR(2048);
    END IF;
END $$;

-- 3. Create Webhook Subscriptions Table
CREATE TABLE IF NOT EXISTS webhook_subscriptions (
    id SERIAL PRIMARY KEY,
    workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL,
    target_url VARCHAR(2048) NOT NULL,
    secret VARCHAR(64) NOT NULL,
    events VARCHAR(255) DEFAULT 'scan.created,qr.expired,qr.limit_reached' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    failure_count INTEGER DEFAULT 0 NOT NULL,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    last_status_code INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_webhook_workspace ON webhook_subscriptions (workspace_id);

-- 4. Create Webhook Delivery Logs Table
CREATE TABLE IF NOT EXISTS webhook_delivery_logs (
    id SERIAL PRIMARY KEY,
    webhook_id INTEGER NOT NULL REFERENCES webhook_subscriptions(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    payload_json TEXT NOT NULL,
    response_status INTEGER,
    response_body TEXT,
    execution_duration_ms DOUBLE PRECISION,
    delivered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_delivery_webhook ON webhook_delivery_logs (webhook_id);
CREATE INDEX IF NOT EXISTS idx_delivery_created ON webhook_delivery_logs (delivered_at);

-- 5. Row Level Security Policies
ALTER TABLE webhook_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_delivery_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS webhook_subscriptions_policy ON webhook_subscriptions;
CREATE POLICY webhook_subscriptions_policy ON webhook_subscriptions
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR workspace_id = 'ws_legacy_default'
        OR user_in_workspace(workspace_id)
    );

DROP POLICY IF EXISTS webhook_delivery_logs_policy ON webhook_delivery_logs;
CREATE POLICY webhook_delivery_logs_policy ON webhook_delivery_logs
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR EXISTS (
            SELECT 1 FROM webhook_subscriptions s
            WHERE s.id = webhook_delivery_logs.webhook_id
              AND (s.workspace_id = 'ws_legacy_default' OR user_in_workspace(s.workspace_id))
        )
    );

COMMIT;
