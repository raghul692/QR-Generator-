# QRMaster Pro — Next-Generation Upgrade Roadmap & Implementation Plan

**Document Version:** 1.0.0  
**Status:** Engineering Execution Roadmap  
**Author:** REI Chief Systems Architect & Lead Product Manager  
**Planning Horizon:** 4 Strategic Phases (v1.1 through v2.5)  

---

## 1. Roadmap Overview & Strategic Horizon

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                        QRMASTER PRO EVOLUTION                          │
  └────────────────────────────────────────────────────────────────────────┘
       │
       ├─► [Phase 1: v1.1 - Performance, Security & Usability Polish]
       │     • Bundle code splitting (1.28MB -> 165KB)
       │     • Dynamic OS routing (iOS / Android / Web)
       │     • Eye/Pupil custom styling & Branded CTA frames
       │     • Async bulk generation with SSE progress bar
       │
       ├─► [Phase 2: v1.2 - Micro-Landing Pages & Marketing Attribution]
       │     • vCard Plus & Link-in-Bio mobile page builder
       │     • UTM parameter builder & forwarding engine
       │     • Retargeting pixel script injection (Meta, GTM)
       │     • Scannability pre-flight gauge & contrast checker
       │
       ├─► [Phase 3: v2.0 - SaaS Multi-Tenancy & Team Workspaces]
       │     • Supabase Auth (JWT) & Row-Level Security
       │     • Multi-organization workspaces & RBAC
       │     • Custom CNAME branded domains (qr.client.com)
       │     • Automated data retention & GDPR IP anonymization
       │
       └─► [Phase 4: v2.5 - Developer Platform & Enterprise Automation]
             • Public Webhooks on scan events
             • Granular scoped API keys & Swagger SDK generation
             • Geo-fencing & time-of-day scheduled routing
             • Enterprise SSO & audit trail compliance
```

---

## 2. Phase 1 (v1.1) — Immediate High-Value Engineering Polish

**Goal:** Elevate QRMaster Pro from a basic generator to a high-performance marketing tool.

### Feature 1.1: Frontend Route Code-Splitting & Lazy Loading
- **User Story:** As a mobile user on 4G, I want the web app to load instantaneously (<1s) without downloading unused charting or spreadsheet libraries.
- **Technical Implementation:**
  - Wrap all routes in `src/App.jsx` with `React.lazy()` and `Suspense`.
  - Configure manual chunking in `vite.config.js` (`vendor-charts`, `vendor-excel`, `vendor-scanner`).
- **Target Metrics:** Initial JS payload < 180 KB; LCP < 1.1s.
- **Complexity:** 2 Story Points (Low). No database migrations.

### Feature 1.2: Dynamic OS Smart Routing (iOS / Android / Desktop)
- **User Story:** As an app developer, I want a single dynamic QR code that sends iPhone users to the App Store, Android users to Google Play, and desktop users to my website.
- **Technical Implementation:**
  - Extend `dynamic_qrs` table with `ios_target_url` (VARCHAR), `android_target_url` (VARCHAR).
  - Update `backend/app/api/v1/endpoints/redirect.py`: inspect `user_agents.parse(ua_string).os.family`.
  - If iOS and `ios_target_url` is present, redirect to iOS URL; if Android, redirect to Android URL; else fallback to `target_url`.
- **Database Migration:**
  ```sql
  ALTER TABLE dynamic_qrs 
  ADD COLUMN IF NOT EXISTS ios_target_url VARCHAR(2048),
  ADD COLUMN IF NOT EXISTS android_target_url VARCHAR(2048);
  ```
- **Complexity:** 3 Story Points (Medium).

### Feature 1.3: Independent Eye / Pupil Styling & Branded CTA Frames
- **User Story:** As a marketing designer, I want to style the corner eyes with distinct colors and shapes, and wrap the QR code in a "SCAN ME" frame.
- **Technical Implementation:**
  - Extend `qr_service.py` with finder pattern masks.
  - Implement 4 frame templates: `top-banner`, `bottom-pill`, `polaroid`, `balloon`.
  - Expose UI controls in `DesignTab.jsx`.
- **Complexity:** 5 Story Points (Medium).

### Feature 1.4: Asynchronous Bulk Generation with Server-Sent Events (SSE)
- **User Story:** As an operations manager, I want to upload a CSV of 500 items and see a live progress bar without HTTP timeouts.
- **Technical Implementation:**
  - `POST /api/v1/bulk/jobs`: accepts CSV, validates schema, creates `qr_bulk_jobs` record, returns `job_id`.
  - Spawns background worker via FastAPI `BackgroundTasks`.
  - `GET /api/v1/bulk/jobs/{job_id}/stream`: SSE endpoint streaming `{processed: 45, total: 500}`.
- **Complexity:** 5 Story Points (Medium).

---

## 3. Phase 2 (v1.2) — Micro-Landing Pages & Marketing Attribution

### Feature 2.1: No-Code Mobile Micro-Landing Page Builder
- **User Story:** As a professional or restaurant owner without a website, I want the QR code to open a sleek mobile landing page for my digital business card or food menu.
- **Technical Implementation:**
  - New table: `landing_pages` (`id`, `slug`, `page_type`, `theme_config`, `content_json`, `created_at`).
  - Page Types: `vcard_plus`, `menu`, `link_in_bio`, `event`.
  - New frontend route: `/p/:slug` rendered with mobile-first viewport.
- **Complexity:** 8 Story Points (High).

### Feature 2.2: Marketing Attribution & Retargeting Script Injection
- **User Story:** As a performance marketer, I want dynamic QRs to fire my Meta Pixel and Google Tag Manager before redirecting, and preserve UTM parameters.
- **Technical Implementation:**
  - Add fields `meta_pixel_id`, `gtm_id`, `utm_params` to `dynamic_qrs`.
  - If pixel IDs exist, the redirect endpoint returns an ultra-fast HTML page with async pixel snippet and client-side `window.location.replace()`.
- **Complexity:** 5 Story Points (Medium).

---

## 4. Phase 3 (v2.0) — SaaS Multi-Tenancy & Workspaces

### Feature 3.1: Supabase Auth & Multi-Tenant Data Isolation
- **User Story:** As an enterprise user, I want secure user accounts with email/password and Google login, ensuring my QRs and analytics are private to my company.
- **Technical Implementation:**
  - Integrate `@supabase/supabase-js` auth in React frontend.
  - FastAPI middleware validates Supabase JWT token via JWKS.
  - Add `tenant_id` / `user_id` to all 12 tables.
  - Enable Supabase Row-Level Security (RLS) policies.
- **Complexity:** 8 Story Points (High).

### Feature 3.2: Custom CNAME Branded Domains (`qr.brand.com`)
- **User Story:** As an enterprise client, I want my dynamic short links to appear as `qr.mybrand.com/r/xyz` instead of Render's default domain.
- **Technical Implementation:**
  - Custom domain verification via DNS TXT records.
  - Vercel Domains API or Caddy / Cloudflare custom SSL termination.
- **Complexity:** 8 Story Points (High).

---

## 5. Phase 4 (v2.5) — Enterprise Automation & Developer Ecosystem

### Feature 4.1: Real-Time Webhooks on Scan Events
- **User Story:** As a logistics engineer, I want an immediate HTTP POST webhook sent to my webhook endpoint whenever a QR code is scanned.
- **Technical Implementation:**
  - New table: `webhooks` (`id`, `tenant_id`, `url`, `secret`, `events`, `is_active`).
  - Background async delivery with exponential backoff retry.
- **Complexity:** 5 Story Points (Medium).

---

## 6. Implementation Timeline & Effort Allocation

| Phase | Duration | Engineering Roles Required | Primary Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1 (v1.1)** | 2 Weeks | Senior Frontend, FastAPI Backend | Bundle splitting, OS routing, CTA frames, Async bulk SSE |
| **Phase 2 (v1.2)** | 3 Weeks | UI/UX Designer, Full-Stack Engineer | Micro-landing pages, Retargeting pixels, UTM engine |
| **Phase 3 (v2.0)** | 4 Weeks | Principal Architect, Security Lead | Supabase Auth, Multi-tenancy, RBAC, Custom CNAME domains |
| **Phase 4 (v2.5)** | 3 Weeks | Backend & DevOps Engineer | Webhook engine, Scoped API keys, Geo-fencing |
