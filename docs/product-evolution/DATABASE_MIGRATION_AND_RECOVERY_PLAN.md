# QRMaster Pro — Database Migration, Multi-Tenancy & Recovery Blueprint

**Document Version:** 1.0.0  
**Status:** Principal Architect Approved Migration Standard  
**Database Engine:** Supabase PostgreSQL 17 (`portfolio-DB`, region: `ap-south-1` Mumbai)  
**Application Role:** `qrmaster_app` (Restricted Application Role)  

---

## 1. Executive Summary & Safety Principles

This blueprint establishes the exact, non-destructive database evolution protocol for transitioning **QRMaster Pro** from a single-tenant shared schema into an enterprise multi-tenant architecture with PostgreSQL Row-Level Security (RLS).

### Non-Negotiable Database Rules:
1. **Zero Table Locks on Active Tables:** All new indexes on high-throughput tables (`scan_logs`, `dynamic_qrs`) must use `CREATE INDEX CONCURRENTLY`.
2. **Safe Constraint Addition:** Foreign keys and `NOT NULL` constraints must be added with `NOT VALID` and verified in a subsequent transaction (`VALIDATE CONSTRAINT`) to eliminate table-level exclusive locks.
3. **Legacy Data Zero-Loss Guarantee:** All existing production records must be safely assigned to a default legacy workspace (`ws_legacy_default`) before activating tenancy filters.
4. **Deterministic Rollback & Forward-Fix:** Every forward migration script has a verified, non-destructive forward-fix or soft-rollback procedure.

---

## 2. Multi-Tenancy Transition Blueprint (Phase 3 Execution)

### 2.1 Tenancy Topology & Relationships
```
┌────────────────────────────────────────────────────────┐
│                   workspaces (Table)                   │
│  id: 'ws_legacy_default' (Default System Workspace)    │
│  name: 'Default Workspace', slug: 'default'            │
└──────────────────────────┬─────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌───────────────────────────┐    ┌───────────────────────────────────┐
│ workspace_members (Table) │    │  All Application Tables           │
│ user_id: Supabase Auth UID│    │  workspace_id: FK -> workspaces.id│
│ role: owner/admin/editor  │    │  (qr_history, dynamic_qrs, etc.)  │
└───────────────────────────┘    └───────────────────────────────────┘
```

### 2.2 7-Step Controlled Migration Protocol

#### Step 1: Create Core Tenancy Tables
```sql
-- Transaction 1: Create tenancy foundation
BEGIN;

CREATE TABLE IF NOT EXISTS workspaces (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(64) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed Default Legacy Workspace for existing production data
INSERT INTO workspaces (id, name, slug)
VALUES ('ws_legacy_default', 'Default Legacy Workspace', 'legacy-default')
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS workspace_members (
    id SERIAL PRIMARY KEY,
    workspace_id VARCHAR(36) NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL, -- Corresponds to Supabase auth.users.id
    role VARCHAR(20) DEFAULT 'owner' NOT NULL, -- 'owner', 'admin', 'editor', 'viewer'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (workspace_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_workspace_members_user ON workspace_members (user_id);

COMMIT;
```

#### Step 2: Add Nullable `workspace_id` to Existing Tables
```sql
-- Transaction 2: Add column without table lock
BEGIN;

ALTER TABLE qr_history ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36);
ALTER TABLE dynamic_qrs ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36);
ALTER TABLE qr_categories ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36);
ALTER TABLE qr_templates ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36);
ALTER TABLE qr_bulk_jobs ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36);
ALTER TABLE qr_exports ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36);
ALTER TABLE api_keys ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(36);

COMMIT;
```

#### Step 3: Backfill Legacy Workspace ID (Data Migration)
```sql
-- Transaction 3: Safe batch backfill
BEGIN;

UPDATE qr_history SET workspace_id = 'ws_legacy_default' WHERE workspace_id IS NULL;
UPDATE dynamic_qrs SET workspace_id = 'ws_legacy_default' WHERE workspace_id IS NULL;
UPDATE qr_categories SET workspace_id = 'ws_legacy_default' WHERE workspace_id IS NULL;
UPDATE qr_templates SET workspace_id = 'ws_legacy_default' WHERE workspace_id IS NULL;
UPDATE qr_bulk_jobs SET workspace_id = 'ws_legacy_default' WHERE workspace_id IS NULL;
UPDATE qr_exports SET workspace_id = 'ws_legacy_default' WHERE workspace_id IS NULL;
UPDATE api_keys SET workspace_id = 'ws_legacy_default' WHERE workspace_id IS NULL;

COMMIT;
```

#### Step 4: Validate Zero Unassigned Records (Pre-Flight Check)
```sql
-- Diagnostic Assertion: Must return 0 across all checks
SELECT 'qr_history' AS tbl, count(*) FROM qr_history WHERE workspace_id IS NULL
UNION ALL
SELECT 'dynamic_qrs', count(*) FROM dynamic_qrs WHERE workspace_id IS NULL
UNION ALL
SELECT 'api_keys', count(*) FROM api_keys WHERE workspace_id IS NULL;
```

#### Step 5: Add Foreign Keys with `NOT VALID` (Lock-Free)
```sql
-- Transaction 4: Non-locking foreign key creation
BEGIN;

ALTER TABLE qr_history 
ADD CONSTRAINT fk_history_workspace 
FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE NOT VALID;

ALTER TABLE dynamic_qrs 
ADD CONSTRAINT fk_dynamic_workspace 
FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE NOT VALID;

ALTER TABLE api_keys 
ADD CONSTRAINT fk_apikeys_workspace 
FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE NOT VALID;

COMMIT;

-- Validate constraints concurrently (avoids read/write locks)
ALTER TABLE qr_history VALIDATE CONSTRAINT fk_history_workspace;
ALTER TABLE dynamic_qrs VALIDATE CONSTRAINT fk_dynamic_workspace;
ALTER TABLE api_keys VALIDATE CONSTRAINT fk_apikeys_workspace;
```

#### Step 6: Create Tenancy Indexes Concurrently
```sql
-- Run outside transaction block
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_qr_history_workspace ON qr_history (workspace_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dynamic_qrs_workspace ON dynamic_qrs (workspace_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_keys_workspace ON api_keys (workspace_id);
```

#### Step 7: Configure PostgreSQL Row-Level Security (RLS)
```sql
-- Enable RLS on application tables
ALTER TABLE qr_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE dynamic_qrs ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Helper function to extract authenticated workspace claims
CREATE OR REPLACE FUNCTION current_app_workspace() RETURNS VARCHAR(36) AS $$
    SELECT current_setting('request.jwt.claim.workspace_id', true)::VARCHAR(36);
$$ LANGUAGE SQL STABLE;

-- RLS Policy: Users can only select/modify data belonging to their active workspace
CREATE POLICY rls_qr_history_workspace ON qr_history
    FOR ALL
    USING (
        workspace_id = current_app_workspace()
        OR EXISTS (
            SELECT 1 FROM workspace_members 
            WHERE workspace_members.workspace_id = qr_history.workspace_id 
            AND workspace_members.user_id = auth.uid()::text
        )
    );

CREATE POLICY rls_dynamic_qrs_workspace ON dynamic_qrs
    FOR ALL
    USING (
        workspace_id = current_app_workspace()
        OR EXISTS (
            SELECT 1 FROM workspace_members 
            WHERE workspace_members.workspace_id = dynamic_qrs.workspace_id 
            AND workspace_members.user_id = auth.uid()::text
        )
    );
```

---

## 3. Performance Indexes & Concurrent DDL (Phase 1 & 2)

### 3.1 Concurrent Analytics Indexing
```sql
-- Index dynamic QR lookups by active status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dynamic_qrs_lookup 
ON dynamic_qrs (short_code) WHERE is_active = TRUE;

-- Composite index for chronological scan logs per dynamic QR
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_logs_qr_time 
ON scan_logs (dynamic_qr_id, scanned_at DESC);

-- Composite index for geographic and device aggregations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_logs_analytics 
ON scan_logs (scanned_at DESC, country, device_type, os);
```

### 3.2 Materialized View & Concurrent Refresh
```sql
-- Materialized View for Hourly Scan Aggregations
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_scans AS
SELECT 
    DATE(scanned_at) AS scan_date,
    dynamic_qr_id,
    device_type,
    os,
    browser,
    country,
    COUNT(*) AS scan_count
FROM scan_logs
GROUP BY 1, 2, 3, 4, 5, 6;

-- Unique Index required for REFRESH CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS uq_mv_daily_scans 
ON mv_daily_scans (scan_date, dynamic_qr_id, device_type, os, browser, country);

-- Refresh Command (Executed via pg_cron or hourly backend worker)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_scans;
```

---

## 4. Disaster Recovery & Rollback Playbook

### 4.1 Production Database Backup Procedure
Before applying any migration phase on production Supabase:
```bash
# Export schema-only backup
pg_dump --schema-only --no-owner --no-privileges "$DATABASE_URL" > qrmaster_schema_pre_migration.sql

# Export complete application data backup (excluding heavy binary blobs)
pg_dump --data-only --table=qr_history --table=dynamic_qrs --table=scan_logs --table=api_keys "$DATABASE_URL" > qrmaster_data_pre_migration.sql
```

### 4.2 Non-Destructive Rollback Strategies
In the event of an unrecoverable migration failure:

#### Soft Rollback (Disable Tenancy Filters without Data Deletion)
```sql
-- If RLS causes legitimate traffic denial, disable RLS immediately
ALTER TABLE qr_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE dynamic_qrs DISABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys DISABLE ROW LEVEL SECURITY;
```

#### Forward-Fix for Missing Columns
If an endpoint fails due to missing columns, execute forward-fix:
```sql
ALTER TABLE dynamic_qrs ADD COLUMN IF NOT EXISTS ios_target_url VARCHAR(2048);
ALTER TABLE dynamic_qrs ADD COLUMN IF NOT EXISTS android_target_url VARCHAR(2048);
```
