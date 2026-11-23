# QRMaster Pro — Production Environment Variables Specification

This document provides the exact list of environment variables required for deploying QRMaster Pro to **Render** (Backend) and **Vercel** (Frontend), as well as local development configuration.

---

## 1. Render Backend Environment Variables

Configure these in your Render service under **Settings** &rarr; **Environment Variables**.

| Variable | Required | Sensitivity | Description & Example |
|----------|----------|-------------|-----------------------|
| `PYTHON_VERSION` | Yes | Public | `3.10.14` |
| `DEBUG` | Yes | Public | `false` |
| `DATABASE_URL` | Yes | **Confidential** | Supabase Session Mode Pooler URI:<br>`postgresql+psycopg2://postgres.[REF]:[PASS]@[HOST]:5432/postgres?sslmode=require` |
| `FRONTEND_ORIGIN` | Yes | Public | Allowed Vercel domain (e.g. `https://qrmaster-pro.vercel.app`) |
| `CORS_ORIGINS` | Yes | Public | Comma-separated allowed origins (e.g. `https://qrmaster-pro.vercel.app,http://localhost:5173`) |
| `PUBLIC_REDIRECT_BASE_URL` | Yes | Public | Public URL of this Render backend for short links (e.g. `https://qrmaster-pro-api.onrender.com`) |
| `SUPABASE_URL` | Optional | Public | Supabase Project URL (e.g. `https://[PROJECT-REF].supabase.co`) |
| `SUPABASE_SERVICE_ROLE_KEY` | Optional | **Confidential** | Supabase service-role secret for server-side Storage access. |
| `SUPABASE_STORAGE_BUCKET` | Optional | Public | Default storage bucket (`qr-assets`) |

---

## 2. Vercel Frontend Environment Variables

Configure these in the Vercel Dashboard under **Settings** &rarr; **Environment Variables**.

| Variable | Required | Sensitivity | Description & Example |
|----------|----------|-------------|-----------------------|
| `VITE_API_BASE_URL` | Yes | Public | URL of deployed Render backend:<br>`https://qrmaster-pro-api.onrender.com` |

*Note:* Never prefix database secrets or private API keys with `VITE_`. Any variable starting with `VITE_` is bundled into browser-accessible JavaScript.

---

## 3. Local Development (`.env`)

For running locally without Docker:

```ini
# Application
APP_NAME=QRMaster Pro
APP_VERSION=1.0.0
DEBUG=true
API_V1_PREFIX=/api/v1
HOST=127.0.0.1
PORT=8000

# Database (Supabase or Local PostgreSQL)
DATABASE_URL=postgresql+psycopg2://postgres:postgrespassword@localhost:5432/qrmaster_pro

# CORS & Routing
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
PUBLIC_REDIRECT_BASE_URL=http://127.0.0.1:8000
FRONTEND_ORIGIN=http://localhost:5173

# Storage (falls back to local filesystem if blank)
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_STORAGE_BUCKET=qr-assets
```
