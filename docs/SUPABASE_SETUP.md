# QRMaster Pro — Supabase PostgreSQL Setup & Deployment Guide

This document provides exact, step-by-step instructions for provisioning, configuring, and connecting the hosted Supabase PostgreSQL database to QRMaster Pro on Render and Vercel.

---

## 1. Supabase Project Provisioning

1. Sign in to your [Supabase Dashboard](https://supabase.com/dashboard).
2. Click **New project**.
3. Configure project details:
   - **Name:** `qrmaster-pro` (or preferred name)
   - **Database Password:** Generate and store a strong, high-entropy password in your password manager.
   - **Region:** Select the region closest to your Render backend deployment (e.g., `us-west-1` / Oregon for Render Oregon).
   - **Pricing Plan:** Free or Pro.
4. Click **Create new project** and wait for database initialization (typically 1–2 minutes).

---

## 2. Obtaining Connection Credentials

1. Navigate to **Project Settings** (gear icon) &rarr; **Database**.
2. Scroll to the **Connection string** section.
3. Select the **URI** tab.

### Connection Mode Selection:
- **Direct Connection (IPv6):**
  - Use if the hosting platform (e.g., Render paid instances with IPv6 or AWS/GCP) supports direct IPv6:
    ```
    postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres?sslmode=require
    ```
- **Supabase Shared Pooler (Session Mode) — Recommended for Render:**
  - In the Supabase Dashboard, toggle **Connection Pooling** &rarr; select **Session Mode** on port `5432` (or Transaction Mode on port `6543` if short-lived):
    ```
    postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require
    ```
  - *Note:* Do not guess the host or region; copy the exact host from your Supabase Connect dashboard.

---

## 3. Storage Bucket Configuration (Supabase Storage)

QRMaster Pro uses object storage for generated QR images, exports, and templates.

1. In Supabase Dashboard, click **Storage** in the left sidebar.
2. Click **New bucket**.
3. Create the required buckets:
   - `qr-assets` (Default bucket for generated QR codes and logo assets; set to **Private** for data privacy).
   - `qr-exports` (For generated PDF sticker sheets, CSVs, and Excel reports).
4. Retrieve your **Project URL** and **Service Role Secret**:
   - Go to **Project Settings** &rarr; **API**.
   - Copy **Project URL** &rarr; `SUPABASE_URL`.
   - Copy **`service_role` secret** &rarr; `SUPABASE_SERVICE_ROLE_KEY`.
   - *Security Warning:* Never expose `SUPABASE_SERVICE_ROLE_KEY` to frontend or commit to Git.

---

## 4. Applying Schema Migrations

Run database migrations via Alembic from your local machine (connected to Supabase) or via the Render pre-deploy command:

### Local Migration Execution:
```bash
# Set your Supabase connection string
export DATABASE_URL="postgresql+psycopg2://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require"

# Navigate to backend directory
cd backend

# Run migrations to head
python -m alembic upgrade head

# Verify current revision
python -m alembic current
# Expected: 001_initial_schema (head)
```

### Windows PowerShell:
```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres?sslmode=require"
cd backend
.\venv\Scripts\python.exe -m alembic upgrade head
```

---

## 5. Seeding Default Reference Data

Populate the 14 default categories and system configuration settings:

```bash
cd backend
python -m app.database.seed
```

This script is **100% idempotent**:
- It checks each category by `slug` and each setting by `key`.
- It will never duplicate records or overwrite custom user configurations.

---

## 6. Architecture & Data Flow Security

```
┌─────────────────────────────────┐
│     Vercel React Frontend       │
└────────────────┬────────────────┘
                 │ HTTPS (REST API)
┌────────────────▼────────────────┐
│      Render FastAPI Backend     │
│   (Holds DATABASE_URL & Secrets) │
└────────────────┬────────────────┘
                 │ TLS / SSL (Port 5432)
┌────────────────▼────────────────┐
│   Supabase Hosted PostgreSQL    │
│     (12 Normalized Tables)      │
└─────────────────────────────────┘
```

**Security Rules:**
1. Frontend (Vercel) NEVER connects directly to PostgreSQL.
2. Backend (Render) is the sole privileged client.
3. No `.env` credentials are ever committed to source control.
4. All connections require `sslmode=require`.

---

## 7. Troubleshooting

| Symptom | Root Cause | Resolution |
|---------|------------|------------|
| `OperationalError: could not translate host name` | Incorrect pooler host or typo in `DATABASE_URL` | Copy the exact URI from Supabase Connect dashboard. |
| `password authentication failed for user "postgres"` | Special characters in password not URL-encoded | URL-encode special characters in password (e.g., `#` &rarr; `%23`, `@` &rarr; `%40`). |
| `SSL connection has been closed unexpectedly` | Transaction mode used instead of Session mode | Switch pooler port from `6543` to `5432` (Session Mode) in connection string. |
| `OperationalError: connection refused / timeout` | IPv6 direct connection attempted on IPv4-only host | Switch from direct connection to Supabase Connection Pooler URI. |
