# QRMaster Pro — Security, Privacy & Compliance Audit (STRIDE & OWASP)

**Document Version:** 1.0.0  
**Status:** Complete Security Posture Assessment  
**Author:** REI Application Security Auditor & DevSecOps Lead  
**Methodologies:** STRIDE Threat Modeling, OWASP Top 10 (2021), GDPR/CCPA Privacy Standards  

---

## 1. Executive Security Assessment

A rigorous application security audit was conducted across QRMaster Pro's frontend interfaces, FastAPI backend endpoints, Supabase PostgreSQL configuration, and deployment topology.

### Security Posture Verdict:
- **Core Strengths:**
  - Secure parameterized queries through SQLAlchemy 2.0 ORM (Zero SQL Injection vulnerabilities detected).
  - Production database credentials properly externalized in environment variables (`DATABASE_URL`).
  - Isolated database role (`qrmaster_app`) restricting access to only application tables.
  - CORS middleware enabled with explicit origins allowed.
- **Identified Critical & High Risks:**
  - **Open Redirect Risk:** Unrestricted target destinations allow phishing attacks using trusted domain.
  - **Denial of Service (DoS):** Unbounded QR matrix dimensions and unthrottled generation endpoints.
  - **CSV Formula Injection:** User-supplied inputs exported to CSV without sanitization (`=cmd|...`).
  - **GDPR / Privacy Exposure:** Full client IP addresses stored unmasked in plain text.
  - **Missing Authentication & Authorization:** Multi-tenant isolation absent; administrative actions unauthenticated.

---

## 2. STRIDE Threat Model Analysis

| Threat Category | Description in QRMaster Pro Context | Current Vulnerability Severity | Existing Defense | Recommended Remediation |
| :--- | :--- | :---: | :--- | :--- |
| **S**poofing | Attacker creates dynamic QRs pretending to be a verified brand or manipulates API keys | **Medium** | API key hashing (Argon2 / SHA256) | Implement Supabase JWT authentication and verified domain ownership checks |
| **T**ampering | Modifying existing dynamic QR destination URLs or tampering with bulk CSV payloads | **High** | None on unauthenticated routes | Enforce user-owned row permissions; validate CSV cells against malicious formula prefixes |
| **R**epudiation | Unauthorized modifications or deletions with no attributable user record | **Medium** | Basic `activity_logs` table | Bind all mutations to authenticated `user_id` and audit log IP/timestamp |
| **I**nformation Disclosure | Raw client IP addresses stored in `scan_logs`; detailed SQLAlchemy stack traces on 500 errors | **High** | Error handlers present in some routes | Mask IP addresses (zero out last octet); configure global FastAPI exception handler to suppress internal tracebacks |
| **D**enial of Service | Submitting massive QR size requests (e.g., `size=10000`) or flooding bulk generation | **High** | Pydantic validation has default size | Enforce strict Pydantic bounds (`gt=100, le=2000`) and slowapi rate limiting per IP/API key |
| **E**levation of Privilege | Normal user gaining access to system settings or API key management | **Critical** | Single shared database role | Introduce Role-Based Access Control (RBAC): `viewer`, `editor`, `admin`, `superadmin` |

---

## 3. In-Depth Vulnerability Analysis & Hardening Solutions

### 3.1 Open Redirect Vulnerability in Dynamic QR Routing (`CWE-601`)
- **Vulnerability Description:** The dynamic QR redirect handler (`backend/app/api/v1/endpoints/redirect.py`) accepts any arbitrary `target_url` provided during creation and redirects visitors via HTTP 307. Phishers frequently exploit dynamic QR services by generating a short code on a legitimate trusted domain (e.g. `qr-generator-2-8sv7.onrender.com/r/xyz`) that silently redirects victims to a credential-harvesting phishing site.
- **Remediation Strategy:**
  1. **Google Safe Browsing API Integration:** Validate destination URLs against Google Safe Browsing / Web Risk API before saving.
  2. **Domain Reputation & Scheme Whitelisting:** Strictly require `http://` or `https://` (disallow `javascript:`, `data:`, `file:`).
  3. **Interim Advisory Warning (Optional Flag):** For newly registered or unverified accounts, show an interim interstitial: *"You are being redirected to external site `example.com`. Continue?"*

### 3.2 CSV Formula Injection / Formula Injection (`CWE-1236`)
- **Vulnerability Description:** In `backend/app/api/v1/endpoints/analytics.py` and export endpoints, when users export scan logs or QR lists to CSV/Excel, cell values originating from client inputs (e.g., User-Agent strings, referer headers, QR titles) are written directly. If a string starts with `=`, `+`, `-`, or `@`, spreadsheet software (Microsoft Excel, LibreOffice) executes it as an active formula or shell command when opened.
- **Remediation:** Prefix any string beginning with `=`, `+`, `-`, `@`, or tab with a single quote (`'`):
  ```python
  def sanitize_csv_cell(value: str) -> str:
      if isinstance(value, str) and value.startswith(('=', '+', '-', '@', '\t', '\r')):
          return f"'{value}"
      return value
  ```

### 3.3 Server-Side Request Forgery (SSRF) in Logo URL Fetching (`CWE-918`)
- **Vulnerability Description:** If logo upload is extended to accept a remote URL (`logo_url`), an attacker could input internal loopback or cloud metadata endpoints (`http://169.254.169.254/latest/meta-data/` or `http://localhost:8000/internal`).
- **Remediation:** Strictly disallow internal/private IP ranges (RFC 1918, link-local, loopback). Require direct client file uploads via multipart form data with image MIME and magic byte verification.

### 3.4 Denial of Service (Memory Exhaustion & Rate Limiting)
- **Vulnerability Description:** Generating a vector or raster QR image of 8000×8000px requires over 250MB of RAM per image. A concurrent flood of 10 requests can trigger an Out-Of-Memory (OOM) crash on Render's 512MB RAM instance.
- **Remediation:**
  1. Enforce strict Pydantic constraints:
     ```python
     size: int = Field(default=400, ge=120, le=2048, description="QR code dimension in pixels")
     ```
  2. Implement `slowapi` rate limiting on generation endpoints:
     ```python
     @router.post("/generate")
     @limiter.limit("30/minute")
     async def generate_qr(...)
     ```

---

## 4. Privacy & Compliance Roadmap (GDPR & CCPA)

### 4.1 Client IP Anonymization
- **Requirement:** Under GDPR Article 4(1), IP addresses are classified as Personal Identifiable Information (PII). Storing raw IP addresses in `scan_logs` without user consent violates EU regulations.
- **Compliance Implementation:**
  - Anonymize IPv4 addresses by setting the last octet to zero before storage:
    - Example: `192.168.1.142` -> `192.168.1.0`.
  - Anonymize IPv6 addresses by masking the last 80 bits.
  - Or store an irreversible HMAC-SHA256 hash using a rotating daily server secret salt if unique visitor counting is required:
    ```python
    import hashlib
    
    def hash_ip(ip: str, salt: str) -> str:
        return hashlib.sha256(f"{ip}:{salt}".encode()).hexdigest()[:16]
    ```

### 4.2 Data Retention & Auto-Purge Lifecycle
- Add an automated data retention policy setting in `settings` table:
  - Default: Retain granular `scan_logs` for 90 days.
  - After 90 days, aggregate counts into `mv_daily_scans` and purge raw log records.

---

## 5. Security Action Checklist

| Priority | Vulnerability / Control | Status | Target Milestone |
| :---: | :--- | :---: | :---: |
| **P0** | Enforce max dimension limits (size <= 2048px) | ⚠️ Urgent | Immediate Patch |
| **P0** | Sanitize CSV export against formula injection | ⚠️ Urgent | Immediate Patch |
| **P1** | Implement IP masking / truncation for GDPR | ⚠️ Required | Next Minor Release |
| **P1** | Add rate limiting via `slowapi` (30 req/min for free) | ⚠️ Required | Next Minor Release |
| **P2** | Google Safe Browsing URL validation on dynamic targets | 📋 Roadmap | v1.2 Release |
| **P2** | Supabase Auth JWT token authentication on API routes | 📋 Roadmap | v2.0 SaaS Release |
