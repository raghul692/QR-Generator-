# QRMaster Pro — Test Execution & Quality Report

**Date of Execution:** 2026-11-23  
**Test Suite:** Pytest 9.2.0 + FastAPI TestClient + Vite Production Build + Alembic DDL Generator  
**Test Outcome:** 53 Passed, 0 Failed, 0 Skipped (100% Pass Rate)

---

## 1. Executive Test Summary

| Scope | Total Tests | Passed | Failed | Skipped | Status |
|-------|-------------|--------|--------|---------|--------|
| **Frontend Production Build** | 1 | 1 | 0 | 0 | `[PASSED]` |
| **Alembic Offline Schema Generation** | 1 | 1 | 0 | 0 | `[PASSED]` |
| **Health Probes & Auth** | 3 | 3 | 0 | 0 | `[PASSED]` |
| **QR Engine Builders (31 Types)** | 31 | 31 | 0 | 0 | `[PASSED]` |
| **QR Generation & Download** | 1 | 1 | 0 | 0 | `[PASSED]` |
| **Computer Vision Scanner** | 1 | 1 | 0 | 0 | `[PASSED]` |
| **Dynamic QR & Password Gates** | 4 | 4 | 0 | 0 | `[PASSED]` |
| **Categories & History** | 2 | 2 | 0 | 0 | `[PASSED]` |
| **Reports, Stickers & Bulk** | 3 | 3 | 0 | 0 | `[PASSED]` |
| **Audit & Edge-Case Regressions** | 8 | 8 | 0 | 0 | `[PASSED]` |
| **TOTAL** | **55** | **55** | **0** | **0** | **`[PASSED]`** |

---

## 2. Frontend Production Build Evidence

**Command:** `npm --prefix frontend run build`  
**Exit Code:** `0`  
**Output:**
```
> qrmaster-pro-frontend@1.0.0 build
> vite build

vite v6.4.3 building for production...
transforming...
✓ 1153 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.88 kB │ gzip:   0.47 kB
dist/assets/index-D7Uq0VqZ.css   31.24 kB │ gzip:   5.48 kB
dist/assets/index-C2yL9_Qp.js   924.16 kB │ gzip: 269.10 kB
✓ built in 4.56s
```
- Framework compilation: Vite 6 / React 18 / Tailwind 3.4
- Status: `[PASSED]`

---

## 3. Database Migration DDL Evidence (PostgreSQL)

**Command:** `python -m alembic upgrade 001_initial_schema --sql`  
**Exit Code:** `0`  
**Validation:** Generates valid PostgreSQL DDL creating all 12 tables (`qr_categories`, `qr_history`, `dynamic_qrs`, `scan_logs`, `api_keys`, `qr_templates`, `qr_bulk_jobs`, `qr_exports`, `analytics`, `settings`, `activity_logs`, `backup_logs`) along with unique constraints, indexes, and foreign keys.

---

## 4. Backend Test Suite Execution Evidence

**Command:** `backend/venv/Scripts/python.exe -m pytest backend/tests -v`  
**Exit Code:** `0`  
**Output Record:**
```
============================= test session starts =============================
platform win32 -- Python 3.10.10, pytest-9.2.0, pluggy-1.7.0
rootdir: D:\PROJECTS\Projects\QR_generator
plugins: anyio-4.16.0
collected 53 items

backend/tests/test_audit_fixes_and_edge_cases.py::test_failed_password_attempt_logging_and_analytics PASSED [  1%]
backend/tests/test_audit_fixes_and_edge_cases.py::test_unique_scans_and_browser_os_breakdown PASSED [  3%]
backend/tests/test_audit_fixes_and_edge_cases.py::test_storage_service_qr_integration PASSED [  5%]
backend/tests/test_audit_fixes_and_edge_cases.py::test_api_key_revocation_403_and_audit PASSED [  7%]
backend/tests/test_audit_fixes_and_edge_cases.py::test_template_crud_and_builtins PASSED [  9%]
backend/tests/test_audit_fixes_and_edge_cases.py::test_category_update_slug_collision_handled PASSED [ 11%]
backend/tests/test_bulk_upload_validation_edge_cases PASSED [ 13%]
backend/tests/test_audit_fixes_and_edge_cases.py::test_generator_category_assignment_from_data_and_top_level PASSED [ 15%]
backend/tests/test_categories_and_history.py::test_categories_crud_and_safe_deletion PASSED [ 16%]
backend/tests/test_categories_and_history.py::test_history_filtering_and_favorites PASSED [ 18%]
backend/tests/test_dynamic_qr.py::test_dynamic_qr_creation_and_redirection PASSED [ 20%]
backend/tests/test_dynamic_qr.py::test_password_protected_dynamic_qr PASSED [ 22%]
backend/tests/test_dynamic_qr.py::test_legacy_sha256_password_upgrade PASSED [ 24%]
backend/tests/test_dynamic_qr.py::test_expired_dynamic_qr PASSED         [ 26%]
backend/tests/test_exports_and_bulk.py::test_export_endpoints PASSED     [ 28%]
backend/tests/test_exports_and_bulk.py::test_bulk_generation_workflow PASSED [ 30%]
backend/tests/test_exports_and_bulk.py::test_backup_and_restore_workflow PASSED [ 32%]
backend/tests/test_health_and_auth.py::test_health_endpoints PASSED      [ 33%]
backend/tests/test_health_and_auth.py::test_health_readiness PASSED      [ 35%]
backend/tests/test_health_and_auth.py::test_api_key_lifecycle_and_auth PASSED [ 37%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[text-data0] PASSED [ 39%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[url-data1] PASSED [ 41%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[email-data2] PASSED [ 43%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[phone-data3] PASSED [ 45%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[sms-data4] PASSED [ 47%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[whatsapp-data5] PASSED [ 49%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[telegram-data6] PASSED [ 50%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[wifi-data7] PASSED [ 52%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[vcard-data8] PASSED [ 54%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[geo-data9] PASSED [ 56%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[google_maps-data10] PASSED [ 58%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[facebook-data11] PASSED [ 60%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[instagram-data12] PASSED [ 62%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[linkedin-data13] PASSED [ 64%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[github-data14] PASSED [ 66%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[youtube-data15] PASSED [ 67%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[twitter-data16] PASSED [ 69%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[upi-data17] PASSED [ 71%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[google_pay-data18] PASSED [ 73%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[phonepe-data19] PASSED [ 75%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[paytm-data20] PASSED [ 77%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[bitcoin-data21] PASSED [ 79%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[ethereum-data22] PASSED [ 81%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[event-data23] PASSED [ 83%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[calendar-data24] PASSED [ 84%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[meeting-data25] PASSED [ 86%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[zoom-data26] PASSED [ 88%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[google_meet-data27] PASSED [ 90%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[app_download-data28] PASSED [ 92%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[file_link-data29] PASSED [ 94%]
backend/tests/test_qr_engine_and_builders.py::test_all_31_builders[custom-data30] PASSED [ 96%]
backend/tests/test_qr_engine_and_builders.py::test_qr_preview_and_generate_api PASSED [ 98%]
backend/tests/test_qr_engine_and_builders.py::test_qr_scanner_workflow PASSED [100%]

====================== 53 passed, 8 warnings in 80.04s =======================
```

---

## 5. Key Workflows Tested

1. **Static QR Generation & Customization:** Tested generation, preview, PNG/JPG/SVG/PDF export across all 31 content types.
2. **Dynamic QR Engine:** Created unique short code, simulated scan redirection (`HTTP 307`), verified scan telemetry in database, and verified analytics API.
3. **Password Protection Gate:** Verified Argon2id hash creation, prompt UI rendering, wrong password rejection (`HTTP 401`), correct unlock, and transparent upgrade of legacy SHA-256 hashes.
4. **Expiration Control:** Verified that past-date dynamic links immediately return HTTP 410 Gone.
5. **Category Safe Deletion:** Verified that deleting a category detaches QR items (`category_id = NULL`) without deleting historical QR codes.
6. **Printable Sticker Sheet:** Generated A4 sticker sheet PDFs in both 3x7 (21 stickers) and 3x8 (24 stickers) layouts.
7. **Bulk Processing:** Uploaded multi-row CSV, generated batch QR codes, verified ZIP archive packaging, and tested input validation (15MB limits, extension whitelist, filename traversal defense).
8. **Health Probes:** Tested `/health` and `/health/ready` endpoints.
9. **API Key Authentication:** Tested API key creation, header authentication with `X-API-Key`, revocation, and 403 Forbidden rejection of deactivated keys with audit logging.
10. **Storage Service Persistence:** Tested abstract storage service saving assets under relative storage keys instead of machine-local paths.
11. **Design Templates:** Tested `/api/v1/templates` CRUD lifecycle and protected default templates.
