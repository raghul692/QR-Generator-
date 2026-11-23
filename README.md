# 🚀 QRMaster Pro — Enterprise QR Code Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?style=flat&logo=react)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.17-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1.svg?style=flat&logo=postgresql)](https://supabase.com/)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8.svg?style=flat&logo=pwa)](https://web.dev/progressive-web-apps/)

An enterprise-grade **QR Code Generator, Analytics & Management Platform** built with **React 18 + Tailwind CSS (Vercel Frontend)**, **FastAPI (Render Backend)**, and **Supabase PostgreSQL (Database & Storage)**.

---

## ✨ Enterprise Features

### 🔹 1. Dynamic QR Codes & Short-Code Routing
- **Editable Destination URLs**: Update destination URLs anytime without re-printing physical QR codes.
- **Production Short URL Redirection**: Fast redirection service (`/r/{short_code}`) with automated scan telemetry.
- **Argon2id Password Protection**: Secure dynamic links using Argon2id password verification before redirection, with automatic upgrade for legacy hashes.
- **Campaign Expiration Datetime**: Set expiration limits for promotional or temporary QR codes (returns HTTP 410 when expired).

### 🔹 2. Real-Time Scan Analytics
- **Device & Browser Detection**: Automated User-Agent classification (Mobile, Tablet, Desktop) and browser detection.
- **Privacy-Aware Telemetry**: IP masking and unique scan calculation without exposing raw visitor addresses.
- **Activity & Trends**: 7-day, 14-day, and 30-day time-series activity charts, plus top-performing QR rankings.

### 🔹 3. Enterprise Printable Sticker Sheet Export
- **A4 Grid PDF Generator**: Automated PDF generation via `ReportLab` producing print-ready A4 sticker sheets in **3x7 (21 stickers)** and **3x8 (24 stickers)** grid layouts.
- **High-DPI Printing**: Vector SVG/PDF rendering designed for industrial labels and retail packaging.

### 🔹 4. Developer REST API Key Management
- **API Key Provisioning**: Programmatically generate API keys prefixed with `qrm_live_...`.
- **One-Way Secure Hashing**: Stored securely using SHA-256 one-way hashing; keys are revealed only once upon creation.
- **Header Authentication**: Access protected routes via `X-API-Key: qrm_live_...`.
- **Key Revocation & Audit**: Instantly deactivate keys with active-status checks and last-used tracking.

### 🔹 5. Progressive Web Application (PWA)
- **Offline First**: Service Worker (`sw.js`) caching static assets while bypassing dynamic API requests.
- **Installable**: Full `manifest.json` with multi-size icon assets and standalone UI mode.

### 🔹 6. 31 Supported QR Content Types & Customization
- **Comprehensive Data Types**: Text, URL, Email, Phone, SMS, WhatsApp, Telegram, Wi-Fi, vCard, GPS Coordinates, Google Maps, Facebook, Instagram, LinkedIn, GitHub, YouTube, Twitter/X, UPI, Google Pay, PhonePe, Paytm, Bitcoin, Ethereum, Events, Calendars, Zoom, Google Meet, Meeting Links, App Store Links, File Links, and Custom Payloads.
- **Custom Aesthetics**: Modules (Square, Rounded, Dots), background transparency, gradient overlays, embedded logos, and custom margins.
- **Computer Vision Scanner**: Dual scanning fallback leveraging `pyzbar` and `OpenCV`.

### 🔹 7. Bulk Generation & Database Backups
- **CSV / Excel Import**: Process batch QR requests into a packaged ZIP archive.
- **Multi-Format Export**: Save as PNG, JPG, SVG, PDF, CSV, Excel, or ZIP.
- **Engine-Agnostic Database Backup & Restore**: Structured JSON snapshots of database tables and image archives.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│            React 18 Frontend (Vercel SPA)               │
│  [Pages] → [TanStack Query / Context] → [Axios Client]  │
└────────────────────────────┬────────────────────────────┘
                             │ HTTPS / REST API / X-API-Key
┌────────────────────────────▼────────────────────────────┐
│              FastAPI Backend Server (Render)            │
│  [Health Probes]  [API Routers]  [Dynamic QR Redirect]  │
│   [QR Engine]      [Analytics]    [Sticker Sheet PDF]   │
└────────────────────────────┬────────────────────────────┘
                             │ SQLAlchemy 2.0 (psycopg2)
                             │ Session Mode Connection Pooler (Port 5432)
┌────────────────────────────▼────────────────────────────┐
│             Supabase Hosted PostgreSQL                  │
│       (12 Normalized Tables & Alembic Migrations)       │
└─────────────────────────────────────────────────────────┘
```

---

## 🗄 Database Schema (12 Tables)

| Table | Purpose |
|-------|---------|
| `qr_categories` | 14 default system categories + custom user categories |
| `qr_history` | Stored QR records (content, styling, preview path, favorite) |
| `dynamic_qrs` | Dynamic QR metadata (short code, target URL, Argon2 password hash, expiration) |
| `scan_logs` | Real-time scan telemetry (masked IP, user-agent, device, browser, timestamp) |
| `api_keys` | Developer API credentials (prefix, hashed secret, active status, rate limit) |
| `qr_templates` | Saved user customization presets |
| `qr_bulk_jobs` | Bulk CSV/Excel generation tracking and ZIP packages |
| `qr_exports` | System export activity records |
| `analytics` | Pre-aggregated metric history |
| `settings` | System-wide configuration key-value storage |
| `activity_logs` | System audit trail |
| `backup_logs` | Database snapshot and file backup records |

---

## 🚀 Getting Started (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase Project or local PostgreSQL instance

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
# On Linux/macOS: source venv/bin/activate
# On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python -m alembic upgrade head

# Seed default categories and settings
python -m app.database.seed

# Start backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Running Automated Tests

Run the complete 45-test suite covering all 31 builders, dynamic QR redirection, password protection, and exports:

```bash
cd backend
python -m pytest tests -v
```

Run frontend production build verification:
```bash
cd frontend
npm run build
```

---

## 🚢 Deployment Documentation

- [docs/PRODUCTION_AUDIT.md](docs/PRODUCTION_AUDIT.md) — Comprehensive repository audit findings and remediation records.
- [docs/SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md) — Step-by-step Supabase database configuration, pooler selection, and migrations.
- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) — Production deployment instructions for Render and Vercel.
- [docs/FEATURE_MATRIX.md](docs/FEATURE_MATRIX.md) — Full feature status matrix and test coverage.
- [docs/TEST_REPORT.md](docs/TEST_REPORT.md) — Pytest execution records and build artifacts.
- [docs/PRODUCTION_ENVIRONMENT.md](docs/PRODUCTION_ENVIRONMENT.md) — Production environment variables specification.

---

## 📄 License
MIT License.
