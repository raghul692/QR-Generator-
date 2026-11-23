-- ==============================================================================
-- QRMaster Pro — Migration v1.3: Multi-Tenancy, Team Workspaces, RBAC & RLS
-- ==============================================================================
-- Target: Supabase PostgreSQL (portfolio-DB / ap-south-1)
-- Description:
--   1. Creates `workspaces` table for enterprise tenant isolation.
--   2. Creates `workspace_members` table for RBAC (Owner, Admin, Editor, Viewer).
--   3. Creates `custom_domains` table for CNAME white-label branded routing.
--   4. Idempotently adds `workspace_id` column to all 8 tenant-scoped tables.
--   5. Backfills existing data to legacy tenant 'ws_legacy_default'.
--   6. Configures high-performance multi-column and foreign key indexes.
--   7. Configures Supabase Row Level Security (RLS) policies with service_role bypass.
-- ==============================================================================

BEGIN;

-- 1. Create Workspaces Table
CREATE TABLE IF NOT EXISTS workspaces (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    owner_id VARCHAR(100) NOT NULL,
    plan VARCHAR(50) DEFAULT 'enterprise' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces (slug);
CREATE INDEX IF NOT EXISTS idx_workspaces_owner ON workspaces (owner_id);

-- 2. Create Workspace Members Table (RBAC)
CREATE TABLE IF NOT EXISTS workspace_members (
    id SERIAL PRIMARY KEY,
    workspace_id VARCHAR(64) NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(20) DEFAULT 'member' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_workspace_member UNIQUE (workspace_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_member_workspace ON workspace_members (workspace_id);
CREATE INDEX IF NOT EXISTS idx_member_user ON workspace_members (user_id);

-- 3. Create Custom Branded Domains Table
CREATE TABLE IF NOT EXISTS custom_domains (
    id SERIAL PRIMARY KEY,
    workspace_id VARCHAR(64) NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    verification_token VARCHAR(64) NOT NULL,
    ssl_status VARCHAR(20) DEFAULT 'provisioning' NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_domains_workspace ON custom_domains (workspace_id);
CREATE INDEX IF NOT EXISTS idx_domains_domain ON custom_domains (domain);

-- 4. Seed Legacy Default Tenant Idempotently
INSERT INTO workspaces (id, name, slug, owner_id, plan, is_active)
VALUES ('ws_legacy_default', 'Default Workspace', 'default-workspace', 'usr_legacy_default', 'enterprise', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO workspace_members (workspace_id, user_id, email, role)
VALUES ('ws_legacy_default', 'usr_legacy_default', 'admin@qrmaster.local', 'owner')
ON CONFLICT (workspace_id, user_id) DO NOTHING;

-- 5. Add workspace_id columns and indexes to existing tenant tables
DO $$
BEGIN
    -- qr_categories
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'qr_categories' AND column_name = 'workspace_id') THEN
        ALTER TABLE qr_categories ADD COLUMN workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL;
    END IF;

    -- qr_history
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'qr_history' AND column_name = 'workspace_id') THEN
        ALTER TABLE qr_history ADD COLUMN workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL;
    END IF;

    -- qr_templates
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'qr_templates' AND column_name = 'workspace_id') THEN
        ALTER TABLE qr_templates ADD COLUMN workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL;
    END IF;

    -- qr_bulk_jobs
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'qr_bulk_jobs' AND column_name = 'workspace_id') THEN
        ALTER TABLE qr_bulk_jobs ADD COLUMN workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL;
    END IF;

    -- dynamic_qrs
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dynamic_qrs' AND column_name = 'workspace_id') THEN
        ALTER TABLE dynamic_qrs ADD COLUMN workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL;
    END IF;

    -- api_keys
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'api_keys' AND column_name = 'workspace_id') THEN
        ALTER TABLE api_keys ADD COLUMN workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL;
    END IF;

    -- landing_pages
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'landing_pages' AND column_name = 'workspace_id') THEN
        ALTER TABLE landing_pages ADD COLUMN workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL;
    END IF;

    -- digital_menus
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'digital_menus' AND column_name = 'workspace_id') THEN
        ALTER TABLE digital_menus ADD COLUMN workspace_id VARCHAR(64) DEFAULT 'ws_legacy_default' NOT NULL;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_categories_workspace ON qr_categories (workspace_id);
CREATE INDEX IF NOT EXISTS idx_history_workspace ON qr_history (workspace_id);
CREATE INDEX IF NOT EXISTS idx_templates_workspace ON qr_templates (workspace_id);
CREATE INDEX IF NOT EXISTS idx_bulk_workspace ON qr_bulk_jobs (workspace_id);
CREATE INDEX IF NOT EXISTS idx_dynamic_workspace ON dynamic_qrs (workspace_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_workspace ON api_keys (workspace_id);
CREATE INDEX IF NOT EXISTS idx_landing_workspace ON landing_pages (workspace_id);
CREATE INDEX IF NOT EXISTS idx_menus_workspace ON digital_menus (workspace_id);

-- 6. Configure Supabase Row Level Security (RLS)
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE qr_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE dynamic_qrs ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE digital_menus ENABLE ROW LEVEL SECURITY;

-- Helper security function: Check workspace membership
CREATE OR REPLACE FUNCTION user_in_workspace(target_ws_id VARCHAR)
RETURNS BOOLEAN LANGUAGE sql SECURITY DEFINER STABLE AS $$
    SELECT EXISTS (
        SELECT 1 FROM workspace_members
        WHERE workspace_id = target_ws_id
          AND user_id = auth.uid()::text
    );
$$;

-- RLS Policies for Workspaces
DROP POLICY IF EXISTS workspace_access_policy ON workspaces;
CREATE POLICY workspace_access_policy ON workspaces
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR owner_id = auth.uid()::text
        OR user_in_workspace(id)
    );

-- RLS Policies for Workspace Members
DROP POLICY IF EXISTS workspace_members_policy ON workspace_members;
CREATE POLICY workspace_members_policy ON workspace_members
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR user_id = auth.uid()::text
        OR user_in_workspace(workspace_id)
    );

-- RLS Policies for Tenant Content
DROP POLICY IF EXISTS qr_history_tenant_policy ON qr_history;
CREATE POLICY qr_history_tenant_policy ON qr_history
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR workspace_id = 'ws_legacy_default'
        OR user_in_workspace(workspace_id)
    );

DROP POLICY IF EXISTS dynamic_qrs_tenant_policy ON dynamic_qrs;
CREATE POLICY dynamic_qrs_tenant_policy ON dynamic_qrs
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR workspace_id = 'ws_legacy_default'
        OR user_in_workspace(workspace_id)
    );

DROP POLICY IF EXISTS landing_pages_tenant_policy ON landing_pages;
CREATE POLICY landing_pages_tenant_policy ON landing_pages
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR workspace_id = 'ws_legacy_default'
        OR user_in_workspace(workspace_id)
    );

DROP POLICY IF EXISTS digital_menus_tenant_policy ON digital_menus;
CREATE POLICY digital_menus_tenant_policy ON digital_menus
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR workspace_id = 'ws_legacy_default'
        OR user_in_workspace(workspace_id)
    );

DROP POLICY IF EXISTS custom_domains_tenant_policy ON custom_domains;
CREATE POLICY custom_domains_tenant_policy ON custom_domains
    FOR ALL
    USING (
        auth.role() = 'service_role'
        OR user_in_workspace(workspace_id)
    );

COMMIT;
