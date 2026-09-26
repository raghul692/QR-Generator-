# 🚀 QRMaster Pro — Enterprise QR Code Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=flat&logo=react)](https://reactjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.0-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql)](https://www.mysql.com/)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8.svg?style=flat&logo=pwa)](https://web.dev/progressive-web-apps/)

A production-ready, enterprise-grade **QR Code Generator, Analytics & Management Platform** built with **React 18 + Tailwind CSS (Frontend)**, **FastAPI (Python Backend)**, and **MySQL (Database)**.

---

## ✨ Enterprise Features (2026 Studio Edition)

### 🔹 1. QR Studio 2.0 & Instant 60fps Vector Canvas
- **0ms Real-Time Client Rendering**: Powered by `qr-code-styling` for latency-free design adjustments.
- **Interactive Real-World Mockups**: Preview in 4 contexts: Pure Vector Canvas, Smartphone Notification, Acrylic Table Tent, and Matte Business Card.
- **Scannability & Contrast Health Guard**: Real-time WCAG contrast calculation with confidence score badges to prevent unscannable codes.
- **1-Click Curated Presets**: Obsidian Glow, Emerald Luxe, Sunset Neon, Cyber Cyan, Swiss Clean, and Royal Trust.

### 🔹 2. Dynamic QR Codes & Smart OS Redirection
- **Editable Destination URLs**: Update target URLs anytime without re-printing QR codes.
- **Smart Device Routing**: Intelligent redirection based on user agent (iOS App Store vs. Android Google Play Store vs. Desktop fallback).
- **Short URL Redirect Engine**: Ultra-fast redirection service (`/r/{short_code}`) with automated scan logging.
- **Password Protection**: Secure dynamic links using SHA-256 hashed password verification before redirection.
- **Expiration Controls**: Set custom expiration datetimes for promotional or limited-time QR campaigns.

### 🔹 3. Bento Analytics & Real-Time Telemetry
- **Device & Browser Detection**: Automated User-Agent parsing (Mobile, Tablet, Desktop, Operating Systems).
- **IP & Geo Insights**: Log IP addresses and scan timestamps for each interaction.
- **High-Density Bento Grid**: KPIs, daily/monthly throughput charts, category mix donuts, and reliability telemetry.

### 🔹 3. Enterprise Printable Sticker Sheet Export
- **A4 Grid PDF Generator**: Automated PDF generation via `ReportLab` producing print-ready A4 sticker sheets (3x7 grid, 21 QR stickers per sheet).
- **High-DPI Printing**: Vector SVG/PDF rendering designed for industrial labels and retail packaging.

### 🔹 4. Developer REST API Key Management
- **API Key Provisioning**: Programmatically generate API keys prefixed with `qrm_...` for external integration.
- **Secure Hash Storage**: Stored securely in database using SHA-256 one-way hashing.
- **Header Authentication**: Access protected routes via `X-API-Key: qrm_live_...`.
- **Key Revocation & Audit**: Instantly revoke keys from the Settings dashboard.

### 🔹 5. Progressive Web Application (PWA)
- **Offline First**: Service Worker (`sw.js`) with cache-first static caching strategy.
- **Installable**: Full `manifest.json` with multi-size icon assets and standalone UI mode.

### 🔹 6. QR Customization & Scanner Engine
- **30+ Supported QR Content Types**: Text, URL, WiFi, vCard, Email, SMS, WhatsApp, Location, Event, Crypto (BTC/ETH), Payment Links (UPI/GPay/PhonePe), App Store.
- **Custom Aesthetics**: Modules (Square, Rounded, Circular, Dots), background transparency, gradient overlays, embedded logos, and custom margins.
- **Computer Vision Scanner**: Dual scanning fallback leveraging `pyzbar` and `OpenCV`.

### 🔹 7. Bulk Generation & Export Tooling
- **CSV / Excel Import**: Process batch QR requests in seconds.
- **Multi-Format Export**: Save as PNG, JPG, SVG, PDF, CSV, Excel, or ZIP.
- **Database Backup & Restore**: Full system snapshot creation and restoration.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│           React 18 Frontend (Vite + PWA)               │
│  [Pages] → [TanStack Query / Context] → [Axios Client]  │
└────────────────────────────┬────────────────────────────┘
                             │ REST API / X-API-Key
┌────────────────────────────▼────────────────────────────┐
│                  FastAPI Backend Server                 │
│  [API Routers] → [Services] → [Dynamic QR / Redirect]   │
│   [QR Engine]    [Analytics]   [Sticker Sheet PDF]      │
└────────────────────────────┬────────────────────────────┘
                             │ SQLAlchemy 2.0 ORM
┌────────────────────────────▼────────────────────────────┐
│             MySQL 8.0 (12 Normalized Tables)            │
└─────────────────────────────────────────────────────────┘
```

### Backend Layers (Clean Architecture)
- `api/` — FastAPI endpoint routers (`dynamic_router.py`, `export_router.py`, `settings_router.py`, `api_keys.py`, etc.)
- `services/` — Business logic layer (`dynamic_qr_service.py`, `export_service.py`, `settings_service.py`)
- `qr_engine/` — Strategy-pattern QR generation & image rendering
- `models/` — SQLAlchemy ORM models (`DynamicQR`, `ScanLog`, `APIKey`, `QRHistory`, etc.)
- `schemas/` — Pydantic v2 DTO schemas for strong input/output validation
- `database/` — Engine config, session management, and automated database seeder

---

## 🗄 Database Schema (12 Tables)

| Table | Purpose |
|-------|---------|
| `qr_history` | Stored QR records (content, styling, preview path) |
| `dynamic_qrs` | Dynamic QR metadata (short code, target URL, password hash, expiration) |
| `scan_logs` | Real-time scan activity (IP address, user-agent, device, browser) |
| `api_keys` | Developer API credentials (key prefix, hashed secret, status) |
| `qr_categories` | Category taxonomy (11 default categories + custom) |
| `qr_templates` | Saved user customization presets |
| `qr_bulk_jobs` | Bulk CSV/Excel generation tracking |
| `qr_exports` | System export activity |
| `analytics` | Aggregated metrics |
| `settings` | System-wide configuration key-value storage |
| `activity_logs` | System audit trail |
| `backup_logs` | Automated & manual backup metadata |

---

## 📦 Tech Stack

### Frontend
- **Framework**: React 18 (Vite build tool)
- **Styling**: Vanilla CSS + Tailwind CSS 3
- **State Management**: TanStack Query (React Query v5) + Context API
- **Animations**: Framer Motion
- **Icons & Alerts**: React Icons, React Hot Toast
- **HTTP Client**: Axios

### Backend
- **Framework**: Python 3.10+ & FastAPI
- **Database ORM**: SQLAlchemy 2.0 & PyMySQL
- **Data Validation**: Pydantic v2
- **QR & Graphics**: `qrcode`, `segno`, `Pillow`, `reportlab`
- **Computer Vision**: `opencv-python`, `pyzbar`
- **Analytics & Export**: `pandas`, `openpyxl`, `user-agents`
- **Logging**: `Loguru`

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0+

---

### 1. Backend Setup

```bash
cd backend

# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate  # On Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Database in backend/.env
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_mysql_password
# DB_NAME=qrmaster_pro

# 4. Initialize Database (Creates tables & seeds default categories + settings)
python -m app.database.seed

# 5. Start Backend Server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

---

### 2. Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start Development Server
npm run dev
```

- **Frontend Application**: `http://localhost:5173`

---

## 📡 API Endpoints Overview

All backend endpoints are prefixed under `/api/v1`.

### 🔹 Dynamic QR & Redirection
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/dynamic/create` | Create a new dynamic QR with short code & target URL |
| GET | `/r/{short_code}` | Public redirect route (logs scan analytics) |
| POST | `/r/{short_code}/unlock` | Unlock password-protected dynamic QR |
| PUT | `/dynamic/{id}` | Update dynamic QR target URL or password |
| GET | `/dynamic/{id}/analytics` | Get detailed scan analytics for a dynamic QR |

### 🔹 Enterprise Printing & Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/export/sticker-sheet` | Generate & download A4 PDF Printable Sticker Sheet |
| GET | `/export/history/csv` | Export QR history as CSV |
| GET | `/export/history/excel` | Export QR history as Excel spreadsheet |
| GET | `/export/history/pdf` | Export full QR summary report as PDF |

### 🔹 Developer API Keys
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api-keys/` | List active developer API keys |
| POST | `/api-keys/generate` | Issue a new API key (`qrm_live_...`) |
| DELETE | `/api-keys/{id}` | Revoke an API key |

### 🔹 Settings & Configuration
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/settings/dict` | Get configuration key-value dictionary |
| PUT | `/settings/` | Bulk update system settings |

---

## 🧹 Zero-Data Production Reset Utility

To clean test history and reset the application to a fresh state before production deployment:

```bash
cd backend
python reset_db_and_files.py
```

This utility safely:
- Truncates user data tables (`qr_history`, `dynamic_qrs`, `scan_logs`, `api_keys`, etc.)
- Retains default seeded categories and system settings.
- Wipes temporary storage files from `app/generated_qr/`, `app/exports/`, `app/backups/`, and `app/logs/`.

---

## 📂 Project Structure

```
QR_generator/
├── backend/
│   ├── app/
│   │   ├── api/             # REST Routers (Dynamic, Export, History, Settings, etc.)
│   │   ├── database/        # Session, engine, seed script
│   │   ├── models/          # SQLAlchemy ORM models (12+ tables)
│   │   ├── qr_engine/       # Custom QR generator & renderer
│   │   ├── schemas/         # Pydantic v2 DTOs
│   │   ├── services/        # Service business logic layer
│   │   └── main.py          # FastAPI application entry point
│   ├── reset_db_and_files.py # Production reset script
│   ├── requirements.txt     # Backend dependencies
│   └── .env                 # Environment configuration
│
├── frontend/
│   ├── public/              # PWA manifest, service worker, icons
│   ├── src/
│   │   ├── components/      # UI components & charts
│   │   ├── layouts/         # App shell & layout wrapper
│   │   ├── pages/           # Generator, Scanner, History, Analytics, Settings, etc.
│   │   ├── redux/           # Theme context
│   │   └── services/        # Axios API client bindings
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml       # Docker container setup
└── README.md                # Documentation
```

---

## 🔒 Security & Best Practices

- **Password Hashing**: SHA-256 encryption for dynamic link passwords and API key secrets.
- **Input Sanitization**: Pydantic v2 validation on all API requests.
- **SQL Injection Defense**: 100% parameterized queries via SQLAlchemy ORM.
- **CORS Management**: Configured for local & production origin domain restrictions.

---

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).