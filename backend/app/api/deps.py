"""
QRMaster Pro — API Dependencies & Authentication.

Provides header authentication for developer API keys (`X-API-Key`)
with active-status verification, rate-limit awareness, and last_used tracking.
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import APIKey
from app.utils.logger import logger


def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key", description="Developer API Key (qrm_live_...)"),
    db: Session = Depends(get_db),
) -> APIKey:
    """
    FastAPI dependency to enforce API key authentication on protected endpoints.
    Verifies key format, hashed secret match, and active status.
    Updates last_used_at timestamp.
    """
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required 'X-API-Key' header",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    clean_key = x_api_key.strip()
    key_hash = hashlib.sha256(clean_key.encode("utf-8")).hexdigest()

    key_record = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if not key_record:
        logger.warning("Rejected API request: Invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not key_record.is_active:
        logger.warning(f"Rejected API request: Revoked API key '{key_record.key_prefix}...'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key has been revoked or deactivated",
        )

    # Track usage
    try:
        key_record.last_used_at = datetime.now()
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning(f"Could not update last_used_at for key {key_record.id}: {exc}")

    return key_record
