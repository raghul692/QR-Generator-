# QRMaster Pro — Implementation Phase Matrix & Task Registry

**Document Version:** 1.0.0  
**Status:** Approved Delivery Lifecycle Structure  
**Author:** REI Lead Product Engineer & Systems Architect  
**Planning Horizon:** 4 Strategic Phases (v1.1 to v2.5)  

---

## 1. Lifecycle Overview & Phase Boundaries

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DELIVERY LIFECYCLE GATES                        │
├─────────────────┬──────────────────┬─────────────────┬─────────────────┤
│  Phase 1 (v1.1) │  Phase 2 (v1.2)  │  Phase 3 (v2.0) │  Phase 4 (v2.5) │
│  Usability &    │  Micro-Landing   │  SaaS Multi-    │  Developer API  │
│  Visual Engine  │  Pages & Tracking│  Tenancy & RBAC │  & Webhooks     │
├─────────────────┼──────────────────┼─────────────────┼─────────────────┤
│ 10 Tasks        │ 7 Tasks          │ 5 Tasks         │ 3 Tasks         │
│ Non-breaking    │ New mobile pages │ Tenancy schema  │ Developer tier  │
│ 2 Weeks         │ 3 Weeks          │ 4 Weeks         │ 3 Weeks         │
└─────────────────┴──────────────────┴─────────────────┴─────────────────┘
```

---

## 2. Phase 1: High-Performance Usability & Visual Engine (v1.1)

### Objectives:
1. Eliminate the monolithic 1.28MB frontend bundle (target <180KB initial core JS).
2. Implement Dynamic OS Smart Routing (iOS App Store vs Android Google Play vs Web).
3. Introduce independent Eye/Pupil styling and 4 branded Call-To-Action (CTA) frames.
4. Replace synchronous bulk rendering with a durable DB-backed job queue and live SSE progress streaming.
5. Migrate file storage from ephemeral Render disk to Supabase Cloud Storage (`qr-assets`).
6. Enforce security hardening (CSV formula sanitization, dimension bounding, IP anonymization).

### Phase 1 Task Registry:

| Task ID | Task Name | Mapped Req IDs | Modified Files | New Files | Complexity | Risk | Verification Suite | Exit Criteria |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **P1-01** | Route Code-Splitting & Directory Hygiene | `UIUX-001`, `PERF-001`, `DEBT-001` | `frontend/src/App.jsx`<br>`frontend/vite.config.js` | None (`src/redux/` moved to `src/context/`) | 2 SP | Low | `npm run build` | Initial JS < 180KB; chunks separated (`vendor-charts`, `vendor-excel`); zero build errors |
| **P1-02** | Dynamic OS Smart Routing | `FEAT-001`, `AUDIT-001` | `backend/app/models/__init__.py`<br>`backend/app/api/endpoints/redirect.py`<br>`frontend/src/pages/DynamicQR.jsx` | None | 3 SP | Low | Simulated iPhone/Android curls | HTTP 307 routes correctly based on User-Agent header |
| **P1-03** | Eye/Pupil Styling & 4 CTA Frames | `FEAT-002`, `FEAT-003`, `FEAT-012` | `backend/app/services/qr_service.py`<br>`frontend/src/pages/Generator.jsx` | Frame mask templates | 5 SP | Medium | Automated decode verification | Renders custom corner shapes and CTA text; maintains scannability |
| **P1-04** | Durable Async Bulk Queue with SSE | `FEAT-004`, `PERF-002`, `GAP-001` | `backend/app/api/bulk_router.py`<br>`backend/app/services/bulk_service.py`<br>`frontend/src/pages/BulkGenerator.jsx` | None | 5 SP | Medium | 500-row batch test & kill sweeper | Background processing with persistent heartbeat; SSE progress updates |
| **P1-05** | Security & Privacy Hardening | `SEC-001`..`SEC-006` | `backend/app/api/endpoints/redirect.py`<br>`backend/app/api/export_router.py`<br>`backend/app/schemas/qr.py` | None | 3 SP | Low | Security test suite | Formula injection escaped; size bounded <= 2048; IPv4 `/24` zeroed |
| **P1-06** | Supabase Cloud Storage Migration | `AUDIT-004`, `GAP-002` | `backend/app/services/qr_service.py`<br>`backend/app/config.py` | Storage helper module | 3 SP | Medium | Container restart drill | Public images and private export files persist across restarts |
| **P1-07** | Scannability Gauge & QA Studio | `UIUX-004`, `GAP-003` | `frontend/src/pages/Generator.jsx`<br>`frontend/src/pages/Scanner.jsx` | None | 3 SP | Low | Diagnostic test set | Live contrast gauge alerts users on low contrast (<4.5:1) |
| **P1-08** | 10-State Components & 5 Viewports | `UIUX-001`..`UIUX-007` | `frontend/src/components/*`<br>`frontend/src/pages/*` | None | 3 SP | Low | 5-viewport emulation | Complete focus rings; touch targets >= 44px; no horizontal overflow |
| **P1-09** | Composite Indexing & Supavisor | `PERF-003`, `PERF-005` | `backend/app/config.py` | Migration SQL | 2 SP | Low | `EXPLAIN ANALYZE` | Composite indexes active; connection pooler active on port 6543 |
| **P1-10** | Frontend Vitest Test Setup | `DEBT-002` | `frontend/vite.config.js`<br>`frontend/package.json` | `frontend/src/tests/*` | 3 SP | Low | `npm test` | Core component unit tests passing automated execution |

---

## 3. Phase 2: Micro-Landing Pages & Marketing Attribution (v1.2)

### Phase 2 Task Registry:

| Task ID | Task Name | Mapped Req IDs | Modified Files | New Files | Complexity | Risk | Verification Suite | Exit Criteria |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **P2-01** | Landing Page Builder & Renderer | `FEAT-005`, `GAP-004` | `frontend/src/App.jsx` | `LandingPages.jsx`<br>`landing_page_router.py` | 8 SP | Medium | End-to-end publishing test | Custom `/p/:slug` page renders with sub-50KB styling |
| **P2-02** | vCard Plus Digital Business Card | `GAP-005` | None | `VCardPlus.jsx`<br>`vcard_service.py` | 5 SP | Low | VCF download on iOS/Android | RFC 6350 `.vcf` downloads directly into phone contacts |
| **P2-03** | Restaurant & Hospitality Menu | `GAP-006` | None | `MenuBuilder.jsx`<br>`menu_router.py` | 5 SP | Low | Mobile device inspection | Menu categories, allergen badges, and sold-out states active |
| **P2-04** | Link-in-Bio Curated Page | `GAP-007` | None | `LinkInBio.jsx` | 3 SP | Low | Link click counter test | Social icons and link clicks correctly tracked |
| **P2-05** | Marketing Attribution (UTM & Pixels) | `FEAT-006`, `GAP-008` | `redirect.py`<br>`DynamicQR.jsx` | Tracking interstitial page | 5 SP | Medium | Pixel trigger test with DNT | Pixels fire asynchronously; UTM parameters pass to destination |
| **P2-06** | Materialized Daily Scan Rollups | `PERF-004` | `dashboard_router.py` | SQL Migration | 3 SP | Low | Benchmark 100k rows | Analytics queries execute in <25ms using materialized view |
| **P2-07** | Password Challenge & Max Scans | `FEAT-009`, `FEAT-010` | `redirect.py` | PIN challenge template | 3 SP | Low | Expiration & PIN tests | Enforces password challenge and deactivates after max scans |

---

## 4. Phase 3: SaaS Multi-Tenancy & Governance (v2.0)

### Phase 3 Task Registry:

| Task ID | Task Name | Mapped Req IDs | Modified Files | New Files | Complexity | Risk | Verification Suite | Exit Criteria |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **P3-01** | Supabase Auth (JWT) Integration | `GAP-009`, `SEC-006` | `frontend/src/App.jsx`<br>`backend/app/api/deps.py` | `AuthContext.jsx`<br>`auth_middleware.py` | 8 SP | High | JWT auth penetration test | Validates Supabase JWT JWKS; blocks unauthenticated API calls |
| **P3-02** | Multi-Tenant Legacy Data Migration | `GAP-010` | None | Tenancy SQL Migration | 8 SP | Critical | Pre/post backfill count check | All legacy rows backfilled to `ws_legacy_default`; zero data loss |
| **P3-03** | Workspaces & RBAC | `GAP-011` | `Header.jsx`<br>`api_key_router.py` | `Workspaces.jsx`<br>`workspace_router.py` | 5 SP | High | Multi-role permission tests | Enforces Owner/Admin/Editor/Viewer access boundaries |
| **P3-04** | Custom Branded Domains (CNAME) | `GAP-012`, `VISION-001` | `redirect.py` | `domains_router.py` | 8 SP | High | CNAME DNS resolution test | Custom domains route short codes via automated SSL proxy |
| **P3-05** | 90-Day Retention & GDPR Purge | `SEC-007`, `GAP-016` | `settings_router.py` | `cleanup_service.py` | 3 SP | Medium | Data export/delete drill | Machine-readable JSON export & cascading user deletion active |

---

## 5. Phase 4: Developer Platform & Enterprise Automation (v2.5)

### Phase 4 Task Registry:

| Task ID | Task Name | Mapped Req IDs | Modified Files | New Files | Complexity | Risk | Verification Suite | Exit Criteria |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **P4-01** | Scoped Developer REST API | `GAP-013` | `api_key_router.py`<br>`main.py` | OpenAPI documentation | 5 SP | Low | Scoped token test | Granular scopes (`qr:read`, `qr:write`) enforced on endpoints |
| **P4-02** | Scan Event Webhooks with HMAC | `FEAT-007`, `GAP-014` | `models/__init__.py`<br>`redirect.py` | `webhook_service.py` | 8 SP | Medium | Webhook receiver mock test | Signed HMAC-SHA256 payloads dispatched with exponential backoff |
| **P4-03** | Geo-Fencing & Time Routing | `FEAT-008`, `GAP-015` | `models/__init__.py`<br>`redirect.py` | Geo routing evaluator | 5 SP | Medium | Mock country header test | Routes based on visitor country and time-of-day schedule rules |
