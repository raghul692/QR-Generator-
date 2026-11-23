# QRMaster Pro — Technical Debt Register & Remediation Catalog

**Document Version:** 1.0.0  
**Status:** Complete Codebase Hygiene Assessment  
**Author:** REI Senior Systems Architect  
**Scope:** Frontend Codebase, Backend Services, Deployment Configuration, Database  

---

## 1. Executive Summary

This register catalogs architectural inconsistencies, maintainability hazards, and technical debt items identified during the complete inspection of the QRMaster Pro repository.

Resolving these items will reduce developer cognitive load, eliminate silent failure modes, and ensure frictionless scalability.

---

## 2. Technical Debt Catalog

| ID | Domain | Severity | Issue Summary | Root Cause | Business / Technical Impact | Recommended Remediation |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **TD-01** | Frontend Architecture | **Medium** | Directory misnomer: `src/redux/` contains React Context API | Historical migration or scaffold leftover | Confuses developers looking for Redux stores; violates vertical slice conventions | Rename `src/redux/` to `src/context/` and update 6 component import paths |
| **TD-02** | Frontend Performance | **High** | Monolithic 1.28MB bundle chunk | Missing `React.lazy()` route splitting | High mobile memory usage, sluggish First Contentful Paint | Implement React route lazy loading and manual vendor chunks in `vite.config.js` |
| **TD-03** | Backend Architecture | **High** | Synchronous CPU image rendering in ASGI event loop | Pillow and ReportLab calls run in main async thread | Blocks concurrent HTTP requests during complex rendering | Wrap rendering functions in `asyncio.to_thread()` |
| **TD-04** | Cloud Storage | **High** | Ephemeral file storage on Render container | QR image exports and logos saved to local `/uploads/` | Files are wiped every time Render redeploys or restarts | Integrate Supabase Storage buckets for persistent file hosting |
| **TD-05** | API Boundaries | **Medium** | Inconsistent JSON casing (snake_case vs camelCase) | Backend sends snake_case; some frontend hooks expect camelCase | Requires manual mapping boilerplate across frontend state | Standardize on Pydantic `alias_generator` with `camelCase` response serialization |
| **TD-06** | Database Querying | **Medium** | Missing compound indexes on `scan_logs` | Schema only has primary keys and foreign keys | Aggregated analytics queries will slow down as logs exceed 50k rows | Add composite indexes: `(dynamic_qr_id, scanned_at DESC)` and `(scanned_at DESC, country)` |
| **TD-07** | Security / Defense | **High** | No rate limiting on generation and redirect endpoints | Missing `slowapi` or redis limiter | Susceptible to API flooding, resource exhaustion, and DoS | Implement `slowapi` middleware limiting unauthenticated requests to 30/min |
| **TD-08** | QA Automation | **Medium** | Zero frontend automated test coverage | No Vitest, React Testing Library, or Playwright setup | Visual regressions and broken state handlers require manual testing | Setup Vitest for component unit tests and Playwright for core user journeys |
| **TD-09** | Privacy / Compliance | **Medium** | Unmasked IP addresses stored in `scan_logs` | Client IP saved directly from request header | Non-compliant with GDPR Article 4(1) PII requirements | Truncate IPv4 last octet (`192.168.1.0`) and IPv6 last 80 bits before DB write |
| **TD-10** | Error Handling | **Low** | Raw database exceptions could leak in 500 responses | Inconsistent try-except blocks across endpoints | Could disclose database column names and internal paths to attackers | Add a global FastAPI exception handler returning sanitized JSON error envelopes |

---

## 3. Detailed Remediation Guides for Key Debt Items

### TD-01: Directory Misnomer Refactoring
- **Current Structure:**
  - `frontend/src/redux/QrContext.jsx`
  - `frontend/src/redux/ThemeContext.jsx`
- **Issue:** Neither file uses Redux, Redux Toolkit, or RTK Query. They are pure React 18 Context Providers.
- **Remediation Plan:**
  1. Move files to `frontend/src/context/QrContext.jsx` and `frontend/src/context/ThemeContext.jsx`.
  2. Search and replace import paths across `src/App.jsx`, `src/pages/Generator.jsx`, `src/pages/Dashboard.jsx`.
  3. Delete the empty `src/redux/` folder.

### TD-04: Migrating from Ephemeral Disk to Supabase Storage
- **Current Issue:** In `backend/app/services/qr_service.py`, generated QR images and uploaded logos are written to local disk `backend/uploads/`. Because Render uses an ephemeral container filesystem, every automated deploy or container sleep permanently erases these files.
- **Remediation Plan:**
  1. Create a public Supabase Storage bucket named `qr-assets` via Supabase client.
  2. Store images directly to Supabase Storage and save the public HTTPS URL in `qr_history.image_url`.
  3. Eliminates disk usage on Render and provides instant global CDN delivery via Supabase.

### TD-07: API Rate Limiting Implementation
- **Implementation via `slowapi`:**
  ```python
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address
  from slowapi.errors import RateLimitExceeded
  
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
  
  @router.post("/generate")
  @limiter.limit("30/minute")
  async def generate_qr(request: Request, ...):
      ...
  ```

---

## 4. Technical Debt Paydown Priority Matrix

```
       HIGH IMPACT  │ [TD-02 Bundle Splitting]      [TD-04 Supabase Storage]
                    │ [TD-07 Rate Limiting]         [TD-03 Async Worker Threads]
                    │
                    │ [TD-09 GDPR IP Masking]       [TD-06 DB Compound Indexes]
        LOW IMPACT  │ [TD-01 Rename redux dir]      [TD-08 Playwright Setup]
                    └────────────────────────────────────────────────────────
                      LOW EFFORT                     HIGH EFFORT
```
