-- ==============================================================================
-- QRMaster Pro v1.1 — High Performance Compound Indexes
-- Production Safe: Uses CREATE INDEX CONCURRENTLY IF NOT EXISTS (zero-downtime)
-- ==============================================================================

-- 1. Optimize history queries filtered by category and sorted by creation date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_history_category_created
ON qr_history (category_id, created_at DESC);

-- 2. Optimize history queries filtered by QR type and sorted by creation date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_history_type_created
ON qr_history (qr_type, created_at DESC);

-- 3. Optimize analytics scan logs filtered by dynamic QR ID and sorted by scan timestamp
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_logs_dynamic_created
ON scan_logs (dynamic_qr_id, scanned_at DESC);

-- 4. Optimize unique scan calculations (distinct IP per dynamic QR)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scan_logs_ip_dynamic
ON scan_logs (ip_address, dynamic_qr_id);

-- 5. Optimize bulk queue worker queries finding pending/processing jobs by status and heartbeat
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bulk_status_heartbeat
ON qr_bulk_jobs (status, heartbeat_at);

-- 6. Optimize public short-code redirect lookup checking is_active
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_dynamic_short_active
ON dynamic_qrs (short_code, is_active);
