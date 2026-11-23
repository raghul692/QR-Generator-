"""
QRMaster Pro — JWT Authentication Utilities.

Pure-Python implementation of HMAC-SHA256 JWT encoding and decoding.
Zero external library dependencies, fully compatible with Supabase Auth JWT tokens.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional


def _base64url_encode(data: bytes) -> str:
    """Encode bytes to a base64url string without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    """Decode a base64url string, restoring missing padding."""
    padding = len(data) % 4
    if padding:
        data += "=" * (4 - padding)
    return base64.urlsafe_b64decode(data.encode("utf-8"))


def create_jwt_token(
    payload: Dict[str, Any],
    secret: str = "qrmaster-default-development-jwt-secret-key-32chars",
    expires_in_seconds: int = 86400,
) -> str:
    """Create a signed HS256 JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    header_b64 = _base64url_encode(header_json)

    token_payload = dict(payload)
    if "exp" not in token_payload:
        token_payload["exp"] = int(time.time()) + expires_in_seconds
    if "iat" not in token_payload:
        token_payload["iat"] = int(time.time())

    payload_json = json.dumps(token_payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = _base64url_encode(payload_json)

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_jwt_token(
    token: str,
    secret: Optional[str] = None,
    verify_signature: bool = True,
    verify_exp: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    Returns payload dictionary if valid, or None if invalid or expired.
    """
    if not token or not isinstance(token, str):
        return None

    parts = token.strip().split(".")
    if len(parts) != 3:
        return None

    header_b64, payload_b64, signature_b64 = parts

    # Decode payload
    try:
        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None

    # Check expiration
    if verify_exp and "exp" in payload:
        try:
            exp = int(payload["exp"])
            if time.time() > exp:
                return None
        except Exception:
            return None

    # Verify signature if requested and secret provided
    if verify_signature and secret:
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
        expected_sig_b64 = _base64url_encode(expected_sig)
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            return None

    return payload
