# QRMaster Pro — Security, Privacy & Threat Model Specification

**Document Version:** 1.0.0  
**Status:** Principal DevSecOps & Security Auditor Approved  
**Methodology:** STRIDE Threat Modeling, OWASP Top 10, CWE / CVE Vulnerability Analysis, GDPR / CCPA Compliance  

---

## 1. Executive Security Architecture

QRMaster Pro operates as a physical-to-digital bridge where untrusted end-user traffic (smartphone camera scans) intersects with enterprise administrative functions (QR design, bulk generation, API keys).

This specification establishes defense-in-depth across six core security boundaries:
1. **Dynamic Redirection & Phishing Defense (`CWE-601`)**
2. **Server-Side Request Forgery & DNS Rebinding (`CWE-918`)**
3. **Spreadsheet Formula Injection (`CWE-1236`)**
4. **Denial of Service & Memory Exhaustion (`CWE-400`)**
5. **Cryptographic Key Management & Webhook Integrity**
6. **GDPR / CCPA Privacy & Data Minimization**

---

## 2. STRIDE Threat Model

| Threat | System Component | Attack Vector | Severity | Hardened Countermeasure |
| :--- | :--- | :--- | :---: | :--- |
| **Spoofing** | API Keys & Redirects | Attacker brute-forces API keys or generates QRs spoofing a legitimate brand | **High** | Argon2id key hashing with prefix indexing; domain ownership verification |
| **Tampering** | Destination URLs | Malicious actor modifies another tenant's dynamic destination URL | **Critical** | Supabase JWT authentication + PostgreSQL Row-Level Security (RLS) |
| **Repudiation** | Administrative Mutations | User deletes QRs or changes settings and denies action | **Medium** | Append-only `activity_logs` recording `user_id`, `ip_address`, and timestamp |
| **Information Disclosure** | Scan Logs & Error Responses | Raw client IP exposed in logs; SQLAlchemy stack traces leak database structure | **High** | IPv4 `/24` masking; global FastAPI exception handler returning sanitized JSON |
| **Denial of Service** | QR Generation & Bulk Queue | Sending 10000×10000px size requests or flooding bulk CSV generation | **Critical** | Pydantic dimension bounds (`size <= 2048`); `slowapi` rate limiting; async worker queues |
| **Elevation of Privilege** | Workspaces & Tenancy | Viewer in workspace attempts to create or delete API keys | **Critical** | Role-Based Access Control (RBAC) enforced in FastAPI dependency injections |

---

## 3. In-Depth Vulnerability Countermeasures

### 3.1 Dynamic Redirect Security & Anti-Phishing (`CWE-601`)
- **Risk:** Phishers exploit dynamic QR short links (`/r/{code}`) to redirect victims to malicious credential-harvesting sites using a reputable domain.
- **Defenses:**
  1. **Strict Scheme Allowlist:** Only `http://` and `https://` permitted. Explicitly reject `javascript:`, `data:`, `file:`, `blob:`, `vbscript:`.
  2. **Loopback & Private Network Filtering:** Block destinations resolving to RFC 1918 private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), or AWS metadata (`169.254.169.254`).
  3. **Loop Detection:** Reject destination URLs pointing back to QRMaster Pro's own redirect routes (`/r/*`) to prevent infinite redirect loops.
  4. **Interim Advisory:** Display an interstitial warning if the target domain was added within the last 24 hours.

### 3.2 Server-Side Request Forgery (SSRF) & Webhook Security (`CWE-918`)
- **Risk:** Outbound Webhooks or remote logo upload URLs could be manipulated to probe internal cloud infrastructure.
- **SSRF Hardening Pipeline:**
  ```python
  import ipaddress
  import socket
  from urllib.parse import urlparse

  def validate_safe_outbound_url(url: str) -> bool:
      parsed = urlparse(url)
      if parsed.scheme not in ("http", "https"):
          return False
      
      hostname = parsed.hostname
      if not hostname:
          return False
          
      # Resolve DNS to IP
      try:
          ip_str = socket.gethostbyname(hostname)
          ip = ipaddress.ip_address(ip_str)
      except Exception:
          return False
          
      # Block private, loopback, link-local, multicast, reserved
      if (
          ip.is_private
          or ip.is_loopback
          or ip.is_link_local
          or ip.is_multicast
          or ip.is_reserved
      ):
          return False
          
      return True
  ```

### 3.3 CSV / Spreadsheet Formula Injection (`CWE-1236`)
- **Risk:** Exporting scan logs or QR title fields containing spreadsheet formulas (`=cmd|' /C calc'!A0`) executes code when opened in Microsoft Excel.
- **Sanitization Rule:** Prefix any cell value starting with `=`, `+`, `-`, `@`, `\t`, or `\r` with a single apostrophe (`'`):
  ```python
  def sanitize_csv_cell(value: str) -> str:
      if isinstance(value, str) and value.startswith(('=', '+', '-', '@', '\t', '\r')):
          return f"'{value}"
      return value
  ```

### 3.4 API Key Cryptographic Storage & Rotation
- **Key Format:** `qrm_{environment}_{prefix}_{secret}` (e.g., `qrm_live_a1b2c3d4_8f9e0a...`).
- **Storage:** Key prefix (`a1b2c3d4`) stored in plain text for fast lookup; full secret hashed with **Argon2id** (`time_cost=3`, `memory_cost=65536`, `parallelism=4`).
- **Rotation:** Supports dual active keys per workspace during 7-day migration windows.

### 3.5 Outbound Webhook Verification & Replay Protection
- **Header:** `X-QRMaster-Signature: t={timestamp},v1={hmac_sha256}`.
- **Replay Window:** Reject payloads where `|current_time - t| > 300 seconds`.
- **Payload Limits:** Maximum payload size 256KB; request timeout strictly bounded at 5.0 seconds.
- **Retry Schedule:** Exponential backoff: 0s, 60s, 300s, 900s, 3600s, 21600s, 86400s (7 total retries).

---

## 4. Privacy Engineering & GDPR / CCPA Compliance

### 4.1 Client IP Anonymization Algorithm
Under GDPR Article 4(1), IP addresses constitute personal identifiable data:
- **IPv4 Masking:** The final octet is zeroed out:
  `192.168.1.142` -> `192.168.1.0/24`.
- **IPv6 Masking:** The last 80 bits are zeroed out, retaining only the first 48 bits (routing prefix):
  `2001:0db8:85a3:0000:0000:8a2e:0370:7334` -> `2001:0db8:85a3::/48`.

### 4.2 Consent Management & Retargeting Privacy
- Dynamic redirects inspect the browser `DNT` (Do Not Track) header (`navigator.doNotTrack === "1"`).
- If DNT is enabled, third-party retargeting pixels (Meta Pixel, Google Tag Manager) are completely omitted from the interstitial, and the visitor is redirected immediately.

### 4.3 Data Retention & Right-to-be-Forgotten
- **Automated Retention:** Granular raw `scan_logs` are purged after 90 days following daily aggregation into `mv_daily_scans`.
- **Data Subject Rights:**
  - `GET /api/v1/user/export`: Generates machine-readable JSON archive of all QRs and logs.
  - `DELETE /api/v1/user/account`: Cascading deletion purging all workspace assets, QRs, and database records.
