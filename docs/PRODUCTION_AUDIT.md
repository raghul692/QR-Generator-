# QRMaster Pro — Production Engineering Audit

**Date:** 2026-11-23  
**Project:** QRMaster Pro — Enterprise QR Code Generator, Analytics & Management Platform  
**Target Environment:** Frontend: Vercel | Backend: Render | Database: Supabase PostgreSQL  
**Audit Scope:** Full codebase (root, backend, frontend, dependencies, deployment configs, security, schemas, and models)

---

## 1. Executive Summary

An exhaustive inspection of the entire QRMaster Pro codebase was performed. The platform contains a robust core feature set (31 QR content types, dynamic QR redirection engine, sticker sheet generator, bulk CSV/Excel processor, analytics charts), but was previously constrained by local MySQL dependencies, hardcoded `localhost:8000` URLs across frontend and backend, missing Python dependencies (`user-agents`, `psycopg2-binary`, `argon2-cffi`), lack of Alembic migration infrastructure, absence of `X-API-Key` authentication middleware, and missing cloud deployment configurations (`vercel.json`, `render.yaml`).

This audit details all findings, inventory status, and remediation pathways.

---

## 2. Inventory of Existing Pages & Status

| Page | File Path | Route | Status | Notes / Issues |
|------|-----------|-------|--------|----------------|
| **Dashboard** | `frontend/src/pages/Dashboard.jsx` | `/` | Operational | Charts and stats wired to API. Needs dynamic QR scan integration. |
| **QR Generator** | `frontend/src/pages/Generator.jsx` | `/generator` | Operational | Supports 31 types, live preview, color and style customization. |
| **QR Scanner** | `frontend/src/pages/Scanner.jsx` | `/scanner` | Operational | Image upload scanning. Backend returns raw type; needs content classification. |
| **History** | `frontend/src/pages/History.jsx` | `/history` | Operational | Table with search, type/category filters, favorites, regenerate, printable sticker sheet download. |
| **Categories** | `frontend/src/pages/Categories.jsx` | `/categories` | Operational | List, create, edit, delete categories. Contained cascade bug in ORM. |
| **Bulk Generator** | `frontend/src/pages/BulkGenerator.jsx` | `/bulk` | Operational | Upload CSV/Excel, column mapping, background job execution, ZIP download. |
| **Analytics** | `frontend/src/pages/Analytics.jsx` | `/analytics` | Operational | Generation trends and category charts. Needs scan log & dynamic QR analytics. |
| **Export** | `frontend/src/pages/Export.jsx` | `/export` | Operational | CSV, Excel, PDF history exports, plus A4 sticker sheet. |
| **Backup & Restore** | `frontend/src/pages/Backup.jsx` | `/backup` | Partial | Relied on `mysqldump` and MySQL syntax; needs PostgreSQL-compatible dump/restore. |
| **Settings** | `frontend/src/pages/Settings.jsx` | `/settings` | Operational | UI/QR settings configuration and Developer API key generation/revocation. |
| **Not Found / 404** | Missing | `*` | Missing | No catch-all 404 page in frontend router. |

---

## 3. Inventory of API Endpoints & Status

| Router | Prefix | Endpoint | Method | Status | Notes |
|--------|--------|----------|--------|--------|-------|
| **Core** | `/` | `/` | GET | Operational | Root status endpoint. |
| **Health** | `/` | `/health`, `/health/live`, `/health/ready` | GET | Missing | Required for Render and Kubernetes liveness/readiness probes. |
| **Redirect** | `/r` | `/r/{short_code}` | GET | Operational | Dynamic QR redirection, password gate HTML, scan logging. |
| **Redirect** | `/r` | `/r/{short_code}/unlock` | POST | Operational | Password unlock for protected dynamic links. |
| **QR** | `/api/v1/qr` | `/types` | GET | Operational | Returns all 31 supported QR types metadata. |
| **QR** | `/api/v1/qr` | `/types/{qr_type}` | GET | Operational | Returns field schema for given type. |
| **QR** | `/api/v1/qr` | `/preview` | POST | Operational | Generates base64 preview without saving to DB. |
| **QR** | `/api/v1/qr` | `/generate` | POST | Operational | Generates QR, renders image, saves to history. |
| **QR** | `/api/v1/qr` | `/regenerate/{id}` | POST | Operational | Re-renders QR from history record. |
| **QR** | `/api/v1/qr` | `/download/{id}` | GET | Operational | Downloads PNG, JPG, SVG, or PDF. |
| **History** | `/api/v1/history` | `/` | GET | Operational | Paginated search, type/category filters, sorting. |
| **History** | `/api/v1/history` | `/{id}` | GET | Operational | Single QR history record. |
| **History** | `/api/v1/history` | `/{id}` | PATCH | Operational | Update title, category, favorite status. |
| **History** | `/api/v1/history` | `/{id}` | DELETE | Operational | Deletes history record and image file. |
| **History** | `/api/v1/history` | `/{id}/favorite` | POST | Operational | Toggles favorite flag. |
| **Categories** | `/api/v1/categories` | `/` | GET | Operational | List categories with QR count. |
| **Categories** | `/api/v1/categories` | `/{id}` | GET | Operational | Single category details. |
| **Categories** | `/api/v1/categories` | `/` | POST | Operational | Create custom category. |
| **Categories** | `/api/v1/categories` | `/{id}` | PUT | Operational | Update category. |
| **Categories** | `/api/v1/categories` | `/{id}` | DELETE | Operational | Delete custom category (prevents default deletion). |
| **Scanner** | `/api/v1/scanner` | `/scan` | POST | Operational | Pyzbar + OpenCV fallback image decoder. |
| **Dashboard** | `/api/v1/dashboard` | `/stats` | GET | Operational | Summary metrics. |
| **Dashboard** | `/api/v1/dashboard` | `/charts` | GET | Operational | Chart series data. |
| **Dashboard** | `/api/v1/dashboard` | `/analytics` | GET | Operational | Aggregated analytics. |
| **Bulk** | `/api/v1/bulk` | `/` | GET | Operational | List bulk generation jobs. |
| **Bulk** | `/api/v1/bulk` | `/{id}` | GET | Operational | Bulk job status. |
| **Bulk** | `/api/v1/bulk` | `/upload` | POST | Operational | CSV/XLSX file upload & processing. |
| **Bulk** | `/api/v1/bulk` | `/{id}/download`| GET | Operational | Download generated ZIP package. |
| **Export** | `/api/v1/export` | `/history/csv` | GET | Operational | CSV export of QR records. |
| **Export** | `/api/v1/export` | `/history/excel` | GET | Operational | Excel (.xlsx) export. |
| **Export** | `/api/v1/export` | `/history/pdf` | GET | Operational | Formatted PDF table report. |
| **Export** | `/api/v1/export` | `/sticker-sheet` | POST | Operational | Printable A4 PDF sticker sheet (3x7 and 3x8 grid). |
| **Backup** | `/api/v1/backup` | `/` | GET | Operational | List backup records. |
| **Backup** | `/api/v1/backup` | `/` | POST | Partial | Relied on `mysqldump`. Needs PostgreSQL compatibility. |
| **Backup** | `/api/v1/backup` | `/{id}/restore` | POST | Partial | Relied on `mysql` client. |
| **Backup** | `/api/v1/backup` | `/{id}/download`| GET | Operational | Download backup ZIP. |
| **Settings** | `/api/v1/settings`| `/` | GET | Operational | List settings list. |
| **Settings** | `/api/v1/settings`| `/dict` | GET | Operational | Settings as key-value dictionary. |
| **Settings** | `/api/v1/settings`| `/{key}` | PUT | Operational | Update single setting. |
| **Settings** | `/api/v1/settings`| `/` | PUT | Operational | Bulk update settings. |
| **Dynamic** | `/api/v1/dynamic` | `/` | POST | Partial | Hardcoded redirect URL to localhost:8000. |
| **Dynamic** | `/api/v1/dynamic` | `/{id}/analytics`| GET | Operational | Scan analytics for dynamic QR. |
| **Dynamic** | `/api/v1/dynamic` | `/{id}` | PUT | Operational | Update target URL, title, password, expiry. |
| **API Keys** | `/api/v1/keys` | `/` | GET | Operational | List API keys (prefix, rate limit, created). |
| **API Keys** | `/api/v1/keys` | `/` | POST | Operational | Create API key (returns secret once). |
| **API Keys** | `/api/v1/keys` | `/{id}` | DELETE | Operational | Revoke API key. |
| **API Auth** | Protected routes | `X-API-Key` | Header | Missing | Authentication dependency was not wired into endpoints. |

---

## 4. Database Tables and Relationships (12 Normalized Tables)

1. `qr_categories`: Taxonomy metadata (id, name, slug, description, icon, color, is_default, timestamps).
2. `qr_history`: Core QR records (id, title, qr_type, content, encoded_data, preview_path, file_path, category_id [FK], template_id [FK], customization_json, download_count, is_favorite, timestamps).
3. `qr_templates`: Presets for customization (id, name, description, config_json, is_builtin, timestamps).
4. `qr_bulk_jobs`: Batch jobs (id, job_name, source_filename, total_rows, processed_rows, status, qr_type, column_mapping, zip_path, error_log, timestamps).
5. `qr_exports`: Log of system exports (id, qr_id [FK], export_type, format, file_path, file_size, timestamps).
6. `analytics`: Pre-aggregated daily metrics (id, metric_type, metric_key, metric_value, metric_date, timestamps).
7. `settings`: Application configuration (id, key [unique], value, category, data_type, description, timestamps).
8. `activity_logs`: Audit trail (id, action, module, details, ip_address, created_at).
9. `backup_logs`: Backup snapshots (id, backup_type, file_path, file_size, status, details, timestamps).
10. `dynamic_qrs`: Dynamic routing (id, short_code [unique], target_url, title, qr_history_id [FK], password_hash, expires_at, is_active, scan_count, timestamps).
11. `scan_logs`: Individual scan telemetry (id, dynamic_qr_id [FK], ip_address, user_agent, device_type, browser, referer, scanned_at).
12. `api_keys`: Developer credentials (id, name, key_prefix, key_hash [unique], is_active, rate_limit, last_used_at, timestamps).

---

## 5. Supported QR Content Types (31 Total)

| Key | Label | Category | Validation / Builders |
|-----|-------|----------|-----------------------|
| `text` | Plain Text | general | Non-empty text |
| `url` | Website URL | general | Prepends https:// if missing |
| `email` | Email | communication | mailto: schema with subject & body |
| `phone` | Phone Number | communication | tel: schema |
| `sms` | SMS | communication | SMSTO: schema |
| `whatsapp` | WhatsApp Message | communication | wa.me direct link |
| `telegram` | Telegram | social | t.me direct link |
| `wifi` | Wi-Fi | general | WIFI:T:WPA;S:ssid;P:pass;; |
| `vcard` | vCard | business | BEGIN:VCARD v3.0 standard |
| `geo` | GPS Coordinates | location | geo:lat,long |
| `google_maps` | Google Maps | location | maps.google.com query link |
| `facebook` | Facebook | social | facebook.com profile/page link |
| `instagram` | Instagram | social | instagram.com profile link |
| `linkedin` | LinkedIn | social | linkedin.com profile link |
| `github` | GitHub | social | github.com user link |
| `youtube` | YouTube | social | youtube.com link |
| `twitter` | X (Twitter) | social | twitter.com/x.com handle |
| `upi` | UPI Payment | payments | upi://pay?pa=...&pn=...&am=... |
| `google_pay` | Google Pay | payments | UPI deep-link formatted |
| `phonepe` | PhonePe | payments | UPI deep-link formatted |
| `paytm` | Paytm | payments | UPI deep-link formatted |
| `bitcoin` | Bitcoin | payments | bitcoin:address?amount=... |
| `ethereum` | Ethereum | payments | ethereum:address?value=... |
| `event` | Event | events | BEGIN:VEVENT calendar standard |
| `calendar` | Calendar Event | events | BEGIN:VCALENDAR standard |
| `meeting` | Meeting Link | events | Direct URL validation |
| `zoom` | Zoom | events | Zoom meeting join link |
| `google_meet` | Google Meet | events | Meet direct join link |
| `app_download` | App Download | files | App Store / Play Store URL |
| `file_link` | File Link | files | Cloud storage file link |
| `custom` | Custom Data | general | Raw data pass-through |

---

## 6. Critical Defects & Issues Identified

1. **MySQL Hardcoding & Import Failure:**
   - `backend/app/database/session.py` ran `_create_database_if_not_exists()` on module import using MySQL-only SQL syntax (`CREATE DATABASE IF NOT EXISTS ... COLLATE utf8mb4_unicode_ci`).
   - Failed immediately on developer machines without MySQL and broke Supabase PostgreSQL connectivity.
2. **Missing Backend Dependencies:**
   - `user-agents` was imported in `dynamic_qr_service.py` but absent from `requirements.txt`.
   - `psycopg2-binary` was missing.
   - `argon2-cffi` was missing.
3. **Hardcoded URLs in Frontend & Backend:**
   - `frontend/src/services/api.js` hardcoded `http://127.0.0.1:8000/api/v1`.
   - `backend/app/api/dynamic_router.py` hardcoded `http://127.0.0.1:8000/r/{short_code}`.
4. **Missing Production Deployment Configs:**
   - No `vercel.json` for SPA routing on Vercel.
   - No `render.yaml` for Render FastAPI service.
5. **No Alembic Migration Setup:**
   - Reliance on `Base.metadata.create_all()` in `main.py` lifespan on every startup.
6. **Cascade Deletion Bug:**
   - `QRCategory.history_items` used `cascade="all, delete-orphan"`, which would wipe all historical QR records if a user deleted a category.
7. **Missing Health Probes:**
   - No `/health`, `/health/live`, or `/health/ready` endpoints verifying DB connectivity.
8. **Missing API Key Header Authentication:**
   - Key generation was implemented, but FastAPI dependency `get_api_key` for `X-API-Key` headers was not enforced on protected endpoints.
9. **Password Hashing:**
   - Dynamic QR and API key passwords used plain SHA-256 without salt or work factors.

---

## 7. Remediation Plan

- Phase 2: Switch to `psycopg2-binary`, update `config.py` for Supabase PostgreSQL with connection pooling and SSL, implement Alembic migrations, update seed script.
- Phase 3: Implement persistent storage adapter supporting local and cloud object storage.
- Phase 4: Implement health check endpoints (`/health`, `/health/live`, `/health/ready`), Argon2id password hashing, `X-API-Key` authentication dependency, privacy-preserving IP hashing for scan telemetry.
- Phase 5: Expand categories, fix cascade deletion bug, test all 31 content types, support 3x7 and 3x8 sticker sheets.
- Phase 6: Update frontend `api.js` to dynamic `VITE_API_BASE_URL`, add 404 page, verify responsive views.
- Phase 7–11: Add `vercel.json`, `render.yaml`, `docker-compose.yml` for PostgreSQL, write comprehensive documentation.
- Phase 12–15: Execute end-to-end test suite and produce final verification report.
