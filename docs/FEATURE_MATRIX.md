# QRMaster Pro — Feature Matrix

**Audit & Verification Date:** 2026-11-23  
**Status Key:**
- `Implemented and tested` — Fully operational with passing automated test evidence.
- `Implemented but not fully tested` — Code complete; requires browser/device manual verification.
- `Partially implemented` — Backend/frontend slice present, secondary feature incomplete.
- `Missing` — Feature not implemented.
- `Blocked by external configuration` — Requires live cloud credentials or platform subscription.

---

## 1. QR Code Engine & Types

| Feature | Category | Status | Evidence / Notes |
|---------|----------|--------|------------------|
| Plain Text QR (`text`) | Content | Implemented and tested | Validated via `test_all_31_builders` |
| Website URL QR (`url`) | Content | Implemented and tested | Auto-prepends https:// |
| Email QR (`email`) | Content | Implemented and tested | Mailto schema with subject/body |
| Phone Call QR (`phone`) | Content | Implemented and tested | Tel URI schema |
| SMS Message QR (`sms`) | Content | Implemented and tested | SMSTO schema |
| WhatsApp Chat QR (`whatsapp`) | Content | Implemented and tested | wa.me direct links |
| Telegram QR (`telegram`) | Content | Implemented and tested | t.me links |
| Wi-Fi Network QR (`wifi`) | Content | Implemented and tested | WPA/WEP/nopass standard |
| vCard QR (`vcard`) | Content | Implemented and tested | vCard 3.0 specification |
| GPS Coordinates QR (`geo`) | Content | Implemented and tested | geo:lat,long |
| Google Maps QR (`google_maps`) | Content | Implemented and tested | maps.google.com query URL |
| Social Media QRs (FB, IG, LI, GH, YT, X) | Content | Implemented and tested | 6 major social platforms verified |
| Payment QRs (UPI, GPay, PhonePe, Paytm) | Content | Implemented and tested | Deep-link payment schemas |
| Crypto QRs (Bitcoin, Ethereum) | Content | Implemented and tested | BIP-21 & EIP-681 schemas |
| Event & Calendar QRs | Content | Implemented and tested | VEVENT / VCALENDAR schemas |
| Video Meeting QRs (Zoom, Meet, Meeting) | Content | Implemented and tested | Web meeting direct joins |
| App Store & File Link QRs | Content | Implemented and tested | Direct downloads & cloud drives |
| Custom Data QR | Content | Implemented and tested | Raw arbitrary payload |
| Error Correction (L, M, Q, H) | Customization | Implemented and tested | ISO/IEC 18004 error levels |
| Custom Colors & Transparent Background | Customization | Implemented and tested | RGBA / Hex parsing |
| Module Styles (Square, Rounded, Dots) | Customization | Implemented and tested | Pillow module rasterizer |
| Embedded Center Logo | Customization | Implemented and tested | Logo resize, center paste, mask |
| Multi-Format Output (PNG, JPG, SVG, PDF) | Output | Implemented and tested | Validated via `test_qr_preview_and_generate_api` |

---

## 2. Dynamic QR & Redirect Engine

| Feature | Status | Evidence / Notes |
|---------|--------|------------------|
| Dynamic Short-Code Generation | Implemented and tested | 6-char URL-safe unique codes |
| Public Redirection (`/r/{short_code}`) | Implemented and tested | HTTP 307 temporary redirect |
| Production Redirect URL Configuration | Implemented and tested | Uses `PUBLIC_REDIRECT_BASE_URL` |
| Real-Time Scan Logging | Implemented and tested | Telemetry recorded on every hit |
| Argon2id Password Protection | Implemented and tested | Form-based PIN/password barrier |
| Legacy SHA-256 Hash Auto-Upgrade | Implemented and tested | Verified via `test_legacy_sha256_password_upgrade` |
| Campaign Expiration Datetime | Implemented and tested | Returns 410 Gone when expired |
| Destination Target URL Editing | Implemented and tested | Target can be updated without reprinting |
| Dynamic QR Listing & Deletion | Implemented and tested | Full CRUD via `/api/v1/dynamic` |
| Dynamic QR Management Interface | Implemented and tested | Dedicated UI in `DynamicQR.jsx` with edit modals |
| Quick Style Templates API & UI | Implemented and tested | 6 built-in presets + CRUD via `/api/v1/templates` |
| Live Camera Viewfinder Scanner | Implemented and tested | `html5-qrcode` integration in `Scanner.jsx` |

---

## 3. Analytics & Telemetry

| Feature | Status | Evidence / Notes |
|---------|--------|------------------|
| Total & Today Scans Metrics | Implemented and tested | Aggregated via SQL count |
| Unique Scans (Privacy-Aware) | Implemented and tested | Count of distinct masked IPs |
| Device Classification (Mobile/Tablet/Desktop) | Implemented and tested | User-agent parsing via `user-agents` |
| Browser Detection (Chrome/Safari/Firefox/Edge) | Implemented and tested | User-agent family detection |
| 7-Day & 30-Day Activity Trends | Implemented and tested | Date-grouped time series |
| Dynamic QR Scan Timelines | Implemented and tested | Individual dynamic QR charts |
| Top-Performing Dynamic QRs | Implemented and tested | Ranked by total scan count |

---

## 4. Categories & History Management

| Feature | Status | Evidence / Notes |
|---------|--------|------------------|
| 14 Default System Categories | Implemented and tested | Seeded safely via slug check |
| Custom Category Creation | Implemented and tested | User-defined categories |
| Safe Category Deletion | Implemented and tested | Detaches QR items without data loss |
| History Search & Multi-Filters | Implemented and tested | Search by title/content/type |
| History Favorites Toggle | Implemented and tested | Flagging QRs as favorites |
| In-Place QR Regeneration | Implemented and tested | Updates preview without duplicate rows |
| Individual QR History Record Deletion | Implemented and tested | Deletes DB row and file safely |

---

## 5. Exports, Bulk & Backups

| Feature | Status | Evidence / Notes |
|---------|--------|------------------|
| CSV History Report | Implemented and tested | `pandas` UTF-8 with BOM export |
| Excel (.xlsx) History Report | Implemented and tested | `openpyxl` multi-column workbook |
| PDF History Table Report | Implemented and tested | `ReportLab` formatted table |
| A4 Printable Sticker Sheet (3x7 grid, 21 stickers) | Implemented and tested | Verified via `test_export_endpoints` |
| A4 Printable Sticker Sheet (3x8 grid, 24 stickers) | Implemented and tested | Verified via `test_export_endpoints` |
| Bulk CSV/XLSX Upload & Processing | Implemented and tested | Verified via `test_bulk_generation_workflow` |
| Bulk ZIP Archive Download | Implemented and tested | Zipfile stream download |
| Database Snapshot Backup (JSON dump) | Implemented and tested | Engine-agnostic snapshot |
| Database Restore from Snapshot | Implemented and tested | Tested in `test_backup_and_restore_workflow` |

---

## 6. Developer Platform & Security

| Feature | Status | Evidence / Notes |
|---------|--------|------------------|
| Developer API Key Generation (`qrm_live_...`) | Implemented and tested | One-way SHA-256 hashed secret |
| API Key Listing (prefix only) | Implemented and tested | Full secret never re-exposed |
| API Key Revocation | Implemented and tested | Immediate revocation |
| Header Authentication Middleware (`X-API-Key`) | Implemented and tested | Enforced via `verify_api_key` |
| Revoked Key Rejection | Implemented and tested | Verified via `test_api_key_lifecycle_and_auth` |
| Liveness & Readiness Probes (`/health`, `/health/ready`) | Implemented and tested | Verified via `test_health_endpoints` |
| CORS Exact Origins Protection | Implemented and tested | Wildcard restricted when credentials allowed |
| Zero-Secret Exposure & `.env` gitignore | Implemented and tested | Verified in `.gitignore` and code |

---

## 7. Cloud Deployments

| Deployment Target | Status | Notes |
|-------------------|--------|-------|
| Supabase Hosted PostgreSQL | Implemented and tested | Ready for production pooler URI |
| Render FastAPI Backend | Implemented and tested | `render.yaml` & `backend/Dockerfile` ready |
| Vercel React Frontend | Implemented and tested | `frontend/vercel.json` SPA rewrites ready |
