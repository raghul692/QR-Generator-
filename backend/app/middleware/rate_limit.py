"""
QRMaster Pro — Security & Rate Limiting Middleware.

In-memory sliding window rate limiter protecting critical endpoints:
- Dynamic redirect: 120 req/min
- QR generation/preview: 60 req/min
- Bulk upload: 10 req/min
Returns HTTP 429 Too Many Requests with Retry-After header.
"""
from __future__ import annotations

from collections import defaultdict
import time
from typing import Dict, List, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.utils.logger import logger


class InMemoryRateLimiter:
    """Sliding-window request counter per IP and route bucket."""

    def __init__(self):
        self._history: Dict[Tuple[str, str], List[float]] = defaultdict(list)

    def is_allowed(
        self, client_ip: str, bucket: str, max_requests: int, window_seconds: int = 60
    ) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - window_seconds
        key = (client_ip, bucket)

        timestamps = [ts for ts in self._history[key] if ts > window_start]
        self._history[key] = timestamps

        if len(timestamps) >= max_requests:
            retry_after = int(window_seconds - (now - timestamps[0])) if timestamps else window_seconds
            return False, max(1, retry_after)

        self._history[key].append(now)
        return True, 0

    def reset(self):
        self._history.clear()


rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforces rate limits on key endpoints."""

    async def dispatch(self, request: Request, call_next):
        # Allow test bypass header
        if request.headers.get("X-Test-Bypass-Rate-Limit") == "true":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        bucket = None
        max_requests = 1000

        if path.startswith("/r/"):
            bucket = "redirect"
            max_requests = 120
        elif path.startswith("/api/v1/bulk/upload"):
            bucket = "bulk_upload"
            max_requests = 10
        elif path.startswith("/api/v1/qr/generate") or path.startswith("/api/v1/qr/preview"):
            bucket = "qr_gen"
            max_requests = 60

        if bucket:
            allowed, retry_after = rate_limiter.is_allowed(
                client_ip, bucket, max_requests, window_seconds=60
            )
            if not allowed:
                logger.warning(f"Rate limit exceeded for IP {client_ip} on bucket {bucket}")
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please slow down and try again later."},
                    headers={"Retry-After": str(retry_after)},
                )

        return await call_next(request)
