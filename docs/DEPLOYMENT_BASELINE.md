# QRMASTER PRO — PRODUCTION DEPLOYMENT BASELINE

**Audit & Discovery Date**: 2026-11-23  
**Target Architecture**: React 18 (Vercel) → FastAPI (Render) → PostgreSQL (Supabase)  
**Target Repository**: `https://github.com/raghul692/QR-Generator-.git` (`raghul692/QR-Generator-`)  
**Production Branch**: `main`

---

## 1. Starting State & Remote Divergence

### Local Repository State
- **Previous HEAD**: Built on top of clean application source with 53 passing automated tests and clean Vite build.
- **PostgreSQL Readiness**: Full migration from PyMySQL to `psycopg2-binary`, Alembic revision `001_initial_schema` with normalized PostgreSQL DDL.
- **Frontend State**: Vite build generates production bundle without compilation errors.
- **Security Hardening**: Bulk upload limits (15MB, extension whitelist), API key soft revocation (HTTP 403 Forbidden), IP masking, abstract storage keys.

### Remote `origin/main` State
- **Commit History**:
  - `ee582de`: Initial file upload
  - `109f10e`: Add Python version specification (`.python-version: 3.13`)
  - `5fb3d29`: Add user-agents package to requirements.txt (`user-agents==2.2.0`)
  - `e3be7fa`: Update API base URL to production endpoint (`https://qr-generator-2-8sv7.onrender.com`)
- **Divergence Resolution**: Successfully rebased local production engineering commits on top of `origin/main` without modifying remote history.

---

## 2. Infrastructure & Hosting Discovery

### Frontend (Vercel)
- **Project ID**: `prj_QQWkCzTAQRjSr49qNwJdGM3geFGD`
- **Project Name**: `qr-generator`
- **Account / Team**: `team_BeEtoz4v6nuZDXZEOflqeQgJ` (`raghulraja2006-7822s-projects`)
- **Framework**: `vite`
- **Existing Production URL**: [https://qr-generator-beta-fawn.vercel.app/](https://qr-generator-beta-fawn.vercel.app/)
- **Associated Domains**:
  - `qr-generator-beta-fawn.vercel.app`
  - `qr-generator-raghulraja2006-7822s-projects.vercel.app`
  - `qr-generator-git-main-raghulraja2006-7822s-projects.vercel.app`
- **Status**: Live, but currently missing `VITE_API_BASE_URL` in production environment variables.

### Backend (Render)
- **Active Service ID**: `srv-da4j1ljl550s7382ukg0`
- **Service Name**: `QR-Generator-2`
- **Status**: `not_suspended` (Active)
- **Production URL**: `https://qr-generator-2-8sv7.onrender.com`
- **Runtime**: Python 3.10+
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Current Environment State**: Still retains legacy MySQL configuration (`DB_PORT=3306`, `DB_HOST=localhost`, `DB_USER=root`). Needs update with Supabase `DATABASE_URL` and CORS origins.

### Database (Supabase)
- **Organization ID**: `jtwepgndyhfehhkdaclu` (`raghul692's Org`)
- **Existing Projects**:
  1. `portfolio-DB` (`brmafvpjvdgieelcgivi`) — Region: `ap-south-1` (Mumbai) — Status: `ACTIVE_HEALTHY`
  2. `Linkedin` (`avbrugzxrcpogfthyotv`) — Region: `ap-southeast-1` (Singapore) — Status: `ACTIVE_HEALTHY`
  3. `omniedu-db` (`rjzkpnqonxszejnvuuft`) — Region: `us-east-1` (N. Virginia) — Status: `INACTIVE`
- **Quota Block**: Creation of `qrmaster-pro-production` was blocked due to Supabase Free Tier limit (maximum 2 active free projects per user).

---

## 3. Risks & Remediation Plan

| Risk | Impact | Remediation |
|---|---|---|
| Supabase 2-active project limit | Blocks automated creation of `qrmaster-pro-production` | Request user authorization to pause/delete an inactive or non-critical project, or use an existing DB with a dedicated schema |
| Render database disconnect | Backend restarts with connection refused if pointing to legacy localhost MySQL | Configure Supabase Session Pooler `DATABASE_URL` and `pool_pre_ping=True` |
| Vercel missing API URL | Frontend makes calls to localhost in production | Add `VITE_API_BASE_URL=https://qr-generator-2-8sv7.onrender.com/api/v1` to Vercel environment variables |
| Public redirect URL mismatch | Dynamic QR codes encode localhost URLs | Configure `PUBLIC_REDIRECT_BASE_URL=https://qr-generator-2-8sv7.onrender.com` in Render environment |
