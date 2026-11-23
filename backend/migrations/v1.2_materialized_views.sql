-- ==============================================================================
-- QRMaster Pro v1.2 — High Volume Analytics Materialized Views
-- PostgreSQL / Supabase Production Safe Aggregation
-- ==============================================================================

-- 1. Create materialized view for daily scan rollups
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_scans AS
SELECT
    dynamic_qr_id,
    DATE(scanned_at) AS scan_date,
    COUNT(id) AS total_scans,
    COUNT(DISTINCT ip_address) AS unique_scans,
    COALESCE(device_type, 'Unknown') AS device_type,
    COALESCE(browser, 'Unknown') AS browser
FROM scan_logs
GROUP BY
    dynamic_qr_id,
    DATE(scanned_at),
    COALESCE(device_type, 'Unknown'),
    COALESCE(browser, 'Unknown');

-- 2. Create unique index for concurrent refresh capability (REFRESH MATERIALIZED VIEW CONCURRENTLY)
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_daily_scans_unique
ON mv_daily_scans (dynamic_qr_id, scan_date, device_type, browser);

-- 3. Create index for fast date-range filtering on dynamic QR analytics
CREATE INDEX IF NOT EXISTS idx_mv_daily_scans_date
ON mv_daily_scans (dynamic_qr_id, scan_date DESC);
