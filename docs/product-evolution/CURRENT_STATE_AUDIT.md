# QRMaster Pro — Current State Engineering Audit

**Audit Date:** 2026-11-23  
**Status:** Live Production Verified  
**Current Architecture:** React 18 (Vite 6) + FastAPI 0.115 + SQLAlchemy 2.0 + Supabase PostgreSQL (ap-south-1 Mumbai) + Vercel + Render  
**Repository Branch:** `main` (Commit `ded60e9`)

---

## 1. Executive Summary & System Topology

QRMaster Pro is an enterprise QR code generation, management, and analytics platform. The application is deployed in a modern, decoupled production topology:
- **Client Tier:** Static SPA served via global edge CDN on **Vercel** (`https://qr-generator-beta-fawn.vercel.app/`).
- **Application Tier:** Containerized Python FastAPI REST API running on **Render** (`https://qr-generator-2-8sv7.onrender.com`).
- **Database Tier:** Managed PostgreSQL 17 on **Supabase** in `ap-south-1` (Mumbai) connected via a persistent Session Mode pooler on port 5432 with `pool_pre_ping=True`.
- **CI/CD Tier:** GitHub Actions (`.github/workflows/ci.yml`) automating 53 backend pytest validations and Vite production bundle builds.

```
+-----------------------------------------------------------------------------------+
|                                  USER CLIENT                                      |
|                       (Desktop / Tablet / Mobile Browser)                         |
+-----------------------------------------------------------------------------------+
                                   |                       |
       HTTPS (Vite React 18 SPA)   |                       | HTTPS (Short Code Redirect)
                                   v                       v
+--------------------------------------+       +------------------------------------+
|            VERCEL CDN                |       |       RENDER FASTAPI BACKEND       |
|  qr-generator-beta-fawn.vercel.app   | ----> |   qr-generator-2-8sv7.onrender.com |
|  - 11 Dynamic SPA Routes             |  API  |   - 13 REST Routers                |
|  - Theme Context & Tailwind          | Calls |   - QR Generation & Rendering      |
|  - TanStack React Query v5           |       |   - Telemetry & IP Masking         |
+--------------------------------------+       +------------------------------------+
                                                               |
                                            SQLAlchemy 2.0 / Pooler (Port 5432)
                                                               v
                                               +------------------------------------+
                                               |     SUPABASE POSTGRESQL 17         |
                                               |     Region: ap-south-1 (Mumbai)    |
                                               |     - 12 Normalized Tables         |
                                               |     - Dedicated qrmaster_app Role  |
                                               |     - Versioned Alembic Migrations |
                                               +------------------------------------+
```

---

## 2. Component & Architecture Inventory

### 2.1 Frontend Architecture (`frontend/src/`)

| File / Component | Primary Responsibility | State & Dependencies | Current Implementation Status |
|---|---|---|---|
| `App.jsx` | Top-level routing and SPA navigation | `react-router-dom` v6, registers 11 views + 404 + `/r/:shortCode` fallback | **Verified Production Ready** |
| `layouts/MainLayout.jsx` | Application shell, collapsible sidebar, navbar, dark mode toggle | `ThemeContext`, `framer-motion`, responsive mobile drawer | **Verified Production Ready** |
| `pages/Dashboard.jsx` | High-level metrics, usage charts, recent scan activity | TanStack Query (`/dashboard/stats`, `/dashboard/charts`), Recharts | **Verified Production Ready** |
| `pages/Generator.jsx` | QR code authoring workspace with live preview and customization | Form state, debounce preview mutation, template selector | **Verified Production Ready** |
| `pages/DynamicQR.jsx` | Dynamic QR link management, destination editor, password/expiry modals | Table listing, TanStack Query mutations (`/api/v1/dynamic`) | **Verified Production Ready** |
| `pages/Scanner.jsx` | Dual-mode QR decoding: live device camera + image upload | `html5-qrcode` library, software decoder fallback (`/scanner/decode`) | **Verified Production Ready** |
| `pages/History.jsx` | Saved QR history table, search, category filter, preview modal | TanStack Query (`/history/`), pagination, delete actions | **Verified Production Ready** |
| `pages/Categories.jsx` | Category management taxonomy, color picker, item counts | TanStack Query (`/categories/`), CRUD modals | **Verified Production Ready** |
| `pages/BulkGenerator.jsx` | Spreadsheet upload (.csv, .xlsx) and batch ZIP download | `FormData` upload mutation (`/bulk/upload`), job tracking | **Verified Production Ready** |
| `pages/Analytics.jsx` | Platform-wide scan trends, device, browser, and OS breakdowns | Recharts (`/dashboard/analytics`), date-range metrics | **Verified Production Ready** |
| `pages/Export.jsx` | Batch export hub (CSV, XLSX, PDF, 3x7 A4 sticker sheets) | File blob download handler (`/exports/`), layout picker | **Verified Production Ready** |
| `pages/Backup.jsx` | System snapshot creation, download, and database restore | Backup mutations (`/backup/`), JSON/ZIP download | **Verified Production Ready** |
| `pages/Settings.jsx` | Global platform preferences and Developer API Key management | Key generation, soft revocation toggle, system config | **Verified Production Ready** |
| `services/api.js` | Centralized Axios client with `VITE_API_BASE_URL` | Axios interceptors, centralized endpoint methods | **Verified Production Ready** |
| `redux/ThemeContext.jsx` | Light/Dark theme provider with local storage persistence | React Context API (Misleadingly placed in `/redux/` folder) | **Functional / Tech Debt** |

### 2.2 Backend Architecture (`backend/app/`)

| Module / Router | Endpoint Prefix | Purpose | Handlers & Services |
|---|---|---|---|
| `api/qr_router.py` | `/api/v1/qr` | QR generation, preview, types metadata | `QRRenderer`, `qr_service` |
| `api/dynamic_router.py` | `/api/v1/dynamic` | Dynamic QR link CRUD, destination updates | `dynamic_qr_service` |
| `api/endpoints/redirect.py` | `/r` | Public short code redirect, password unlock | `dynamic_qr_service`, `ScanLog` |
| `api/dashboard_router.py` | `/api/v1/dashboard` | Dashboard stats, chart series, aggregations | `analytics_service` |
| `api/history_router.py` | `/api/v1/history` | Paginated QR history, search, favorites | `history_service` |
| `api/category_router.py` | `/api/v1/categories` | Category taxonomy, slug checks, counts | `category_service` |
| `api/template_router.py` | `/api/v1/templates` | Design style presets CRUD | `template_router` |
| `api/bulk_router.py` | `/api/v1/bulk` | File validation, CSV/XLSX batch generation | `bulk_service` |
| `api/scanner_router.py` | `/api/v1/scanner` | Image upload decode via Pyzbar / OpenCV | `scanner.py` |
| `api/export_router.py` | `/api/v1/exports` | CSV, Excel, PDF, and sticker sheet exports | `export_service` |
| `api/api_key_router.py` | `/api/v1/keys` | Developer API key creation, listing, revocation | `api_keys.py` |
| `api/backup_router.py` | `/api/v1/backup` | System state dump and restore | `backup_service` |
| `api/settings_router.py` | `/api/v1/settings` | Key-value application settings | `settings_service` |
| `api/endpoints/health.py` | `/health` | Liveness (`/health/live`) and DB readiness (`/health/ready`) | Direct PostgreSQL probe (`SELECT 1`) |

---

## 3. Database Schema & Relational Integrity

The database is deployed on PostgreSQL 17 in Supabase (`portfolio-DB`, `ap-south-1`). All 12 tables and their relationships are normalized and indexed:

```
+------------------+         +--------------------+         +-------------------+
|  qr_categories   | 1     * |     qr_history     | 1     * |    qr_exports     |
|------------------|---------|--------------------|---------|-------------------|
| id (PK)          |         | id (PK)            |         | id (PK)           |
| name             |         | title              |         | qr_id (FK)        |
| slug (UNIQUE)    |         | qr_type            |         | export_type       |
| icon, color      |         | content            |         | format            |
| is_default       |         | category_id (FK)   |         | file_path         |
+------------------+         | template_id (FK)   |         +-------------------+
                             | file_path          |
+------------------+         | download_count     | 1
|   qr_templates   | 1     * | is_favorite        |
|------------------|---------+--------------------+
| id (PK)          |                   | 1
| name (UNIQUE)    |                   |
| config_json      |                   | 0..1
| is_builtin       |         +--------------------+         +-------------------+
+------------------+         |    dynamic_qrs     | 1     * |     scan_logs     |
                             |--------------------|---------|-------------------|
+------------------+         | id (PK)            |         | id (PK)           |
|     api_keys     |         | short_code (UNIQUE)|---------| dynamic_qr_id (FK)|
|------------------|         | target_url         |         | ip_address (MASK) |
| id (PK)          |         | password_hash      |         | user_agent        |
| key_prefix       |         | expires_at         |         | device_type       |
| key_hash (UNIQUE)|         | is_active          |         | browser, os       |
| is_active        |         | scan_count         |         | referer           |
+------------------+         +--------------------+         +-------------------+
```

### Table Catalog:
1. `qr_categories`: 14 default system categories + custom user categories. Unique index on `slug`.
2. `qr_history`: Primary store for generated QR codes. Foreign keys to `qr_categories` (SET NULL) and `qr_templates` (SET NULL).
3. `dynamic_qrs`: Dynamic routing table. Unique index on `short_code`. Foreign key to `qr_history` (CASCADE).
4. `scan_logs`: Telemetry event log. Foreign key to `dynamic_qrs` (CASCADE). Indexed on `scanned_at` and `dynamic_qr_id`.
5. `api_keys`: Developer API credentials. Unique index on `key_hash`. Soft-revocation via `is_active` boolean.
6. `qr_templates`: Visual design presets stored as JSON configs.
7. `qr_bulk_jobs`: Batch generation jobs tracking row counts, processing status, and ZIP output paths.
8. `qr_exports`: History of generated export bundles and PDF sticker sheets.
9. `analytics`: Periodic metric snapshots. Unique composite constraint on `(metric_type, metric_key, metric_date)`.
10. `settings`: Key-value application configurations with category and data type metadata.
11. `activity_logs`: Audit trail for security actions (backup creation, restore, password unlock failures, API key revocation).
12. `backup_logs`: Metadata for backup archive generations.

---

## 4. Current QR Engine Capabilities & Technical Boundaries

### What Works Reliably Today:
1. **Content Type Encoding:** 31 supported QR types defined in `types_meta.py` and validated via builders in `builders.py` (URL, WiFi, vCard, Email, SMS, WhatsApp, Phone, Geo, Google Maps, Social Links, Zoom, Crypto, UPI/Payments, App Links).
2. **Visual Styling:**
   - Error Correction levels: `L` (~7%), `M` (~15%), `Q` (~25%), `H` (~30%).
   - Module Drawers: `SquareModuleDrawer`, `RoundedModuleDrawer`, `CircleModuleDrawer`, `GappedSquareModuleDrawer` (dots).
   - Custom Foreground and Background hex colors.
   - Vertical two-color linear gradient interpolation.
   - Logo insertion: Centered image embedding with background box and sizing bounds.
3. **Export Formats:**
   - Raster: PNG, JPG (Pillow).
   - Vector: SVG (via `segno` library).
   - Tabular: CSV, Excel (Pandas + OpenPyXL).
   - Print Layout: 3x7 A4 Printable Sticker Sheet PDF (21 labels per page with cut-grid lines via ReportLab).
4. **Dynamic Redirection Pipeline:**
   - Public short-code resolution via `/r/{short_code}` returning HTTP 307 Temporary Redirect.
   - Argon2id password protection with failure throttling and activity audit logging.
   - Expiration date verification returning HTTP 410 Gone when past timestamp.
   - Real-time telemetry extraction (device type, operating system, browser name via `user-agents`).

### Verified Technical Limitations in Current Implementation:
1. **Synchronous Image Rendering:** QR code rasterization occurs synchronously on the FastAPI request thread. Generating a high-resolution 2000px image with gradients and logo embedding blocks the Python worker thread for 120–250ms.
2. **Gradient Geometry:** Only vertical linear gradients (`top-to-bottom`) are implemented. Radial gradients, diagonal gradients, and multicolor stops are unsupported.
3. **Eye/Marker Customization:** Module styles apply globally to the entire matrix. Eye outer frames and pupil inner markers cannot be styled with separate shapes or distinct colors from the data matrix.
4. **Custom Frames & CTA Labels:** No "Scan Me", phone mockup, or polaroid card frames around the generated QR code.
5. **No Direct CMYK Print Support:** PDF and PNG exports use RGB color space exclusively, which may shift colors when printed by professional offset printing services.
6. **Local Storage Fallback:** `storage_service.py` saves files to local disk (`backend/app/generated_qr/`) with relative keys in PostgreSQL. On Render's ephemeral container filesystem, these files are lost on cold redeployments unless backed by Supabase Storage or an S3 bucket.
