# QRMaster Pro — Production Deployment Guide

This guide details the complete production deployment procedures for deploying QRMaster Pro to **Vercel** (React Frontend) and **Render** (FastAPI Backend) connected to **Supabase** (PostgreSQL Database).

---

## Architecture Overview

```
                      ┌─────────────────────────────────┐
                      │    Vercel Production Domain     │
                      │     (React 18 SPA + Vite)       │
                      └────────────────┬────────────────┘
                                       │ HTTPS (REST API)
                                       │ CORS-Protected
                      ┌────────────────▼────────────────┐
                      │     Render Production Backend   │
                      │      (FastAPI + Uvicorn)        │
                      └────────────────┬────────────────┘
                                       │ TLS / Port 5432
                                       │ Session Mode Pooler
                      ┌────────────────▼────────────────┐
                      │   Supabase Hosted PostgreSQL    │
                      │      (12 Schema Tables)         │
                      └─────────────────────────────────┘
```

---

## 1. Supabase PostgreSQL Deployment (Phase 1)

1. **Create Supabase Project:**
   - Follow instructions in `docs/SUPABASE_SETUP.md`.
2. **Retrieve Connection String:**
   - In Supabase Dashboard, go to **Project Settings** &rarr; **Database** &rarr; **Connection string**.
   - Copy URI (Session Mode Pooler recommended for Render):
     ```
     postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require
     ```
3. **Execute Baseline Migration:**
   ```bash
   cd backend
   export DATABASE_URL="postgresql+psycopg2://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require"
   python -m alembic upgrade head
   ```
4. **Seed Reference Taxonomy & Configuration:**
   ```bash
   python -m app.database.seed
   ```

---

## 2. Render Backend Deployment (Phase 2)

### Automated Blueprint Deployment:
1. Push your repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com), click **New** &rarr; **Blueprint**.
3. Select your GitHub repository containing `render.yaml`.
4. Render will parse `render.yaml` and configure the web service automatically.

### Manual Web Service Configuration (Alternative):
If configuring manually in the Render UI:
- **Type:** Web Service
- **Environment:** Python 3
- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Pre-Deploy Command:** `python -m alembic upgrade head`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health/ready`

### Render Environment Variables:
Configure the following in **Environment** tab:

| Variable Name | Sample / Purpose | Sensitive |
|---------------|------------------|-----------|
| `PYTHON_VERSION` | `3.10.14` | No |
| `DEBUG` | `false` | No |
| `DATABASE_URL` | `postgresql+psycopg2://postgres.[REF]:[PASS]@[HOST]:5432/postgres?sslmode=require` | **YES** |
| `CORS_ORIGINS` | `https://qrmaster-pro.vercel.app` (your Vercel production domain) | No |
| `FRONTEND_ORIGIN` | `https://qrmaster-pro.vercel.app` | No |
| `PUBLIC_REDIRECT_BASE_URL` | `https://qrmaster-pro-api.onrender.com` (your Render backend URL) | No |
| `SUPABASE_URL` | `https://[PROJECT-REF].supabase.co` | No |
| `SUPABASE_SERVICE_ROLE_KEY`| `eyJh...` (Supabase server-side secret) | **YES** |

---

## 3. Vercel Frontend Deployment (Phase 3)

1. Sign in to [Vercel](https://vercel.com/dashboard).
2. Click **Add New...** &rarr; **Project**.
3. Import your GitHub repository.
4. Configure Project Settings:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Configure Environment Variables:

| Variable Name | Value | Purpose |
|---------------|-------|---------|
| `VITE_API_BASE_URL` | `https://qrmaster-pro-api.onrender.com` | Base URL of deployed Render backend |

6. Click **Deploy**.
7. Vercel automatically applies SPA rewrites and security headers from `frontend/vercel.json`.

---

## 4. Post-Deployment Verification Checklist

- [ ] Visit `https://qrmaster-pro-api.onrender.com/health` &rarr; Returns `{"status": "ok", ...}`
- [ ] Visit `https://qrmaster-pro-api.onrender.com/health/ready` &rarr; Returns `{"status": "ready", "database": "connected"}`
- [ ] Open OpenAPI Docs `https://qrmaster-pro-api.onrender.com/docs`
- [ ] Visit Vercel Frontend `https://qrmaster-pro.vercel.app`
- [ ] Generate a static QR code &rarr; Verify preview and download PNG
- [ ] Generate a dynamic QR code &rarr; Scan short link &rarr; Verify redirection and scan analytics increment
- [ ] Check Network tab: confirm all calls target Render backend domain without CORS errors
