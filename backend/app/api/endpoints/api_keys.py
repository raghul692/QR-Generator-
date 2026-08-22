"""
QRMaster Pro — Developer API Keys Router.

Provides API key management endpoints for programmatic integration.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import APIKey
from app.utils.logger import logger

router = APIRouter(prefix="/keys", tags=["Developer API Keys"])


class CreateKeyRequest(BaseModel):
    name: str = Field(..., max_length=100, example="Mobile App Integration")
    rate_limit: int = Field(default=100, ge=1, le=10000)


@router.get("", response_model=List[Dict[str, Any]])
def list_api_keys(db: Session = Depends(get_db)):
    """List all registered API keys."""
    keys = db.query(APIKey).order_by(APIKey.created_at.desc()).all()
    return [
        {
            "id": k.id,
            "name": k.name,
            "key_prefix": k.key_prefix,
            "is_active": k.is_active,
            "rate_limit": k.rate_limit,
            "created_at": k.created_at.isoformat() if k.created_at else None,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
        }
        for k in keys
    ]


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_api_key(req: CreateKeyRequest, db: Session = Depends(get_db)):
    """Generate a new developer API key."""
    raw_secret = secrets.token_urlsafe(32)
    prefix = f"qrm_{raw_secret[:4]}"
    full_key = f"qrm_live_{raw_secret}"
    key_hash = hashlib.sha256(full_key.encode("utf-8")).hexdigest()

    key_record = APIKey(
        name=req.name,
        key_prefix=prefix,
        key_hash=key_hash,
        is_active=True,
        rate_limit=req.rate_limit,
    )
    db.add(key_record)
    db.commit()
    db.refresh(key_record)

    logger.info(f"Generated API key '{prefix}...' for '{req.name}'")
    return {
        "id": key_record.id,
        "name": key_record.name,
        "api_key": full_key,  # Returned ONLY ONCE
        "key_prefix": prefix,
        "rate_limit": key_record.rate_limit,
        "created_at": key_record.created_at.isoformat(),
        "warning": "Copy this secret key now. It will not be shown again!",
    }


@router.delete("/{key_id}", response_model=Dict[str, str])
def revoke_api_key(key_id: int, db: Session = Depends(get_db)):
    """Revoke / delete an API key."""
    key_record = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key_record:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(key_record)
    db.commit()
    logger.info(f"Revoked API key ID {key_id}")
    return {"message": f"API key {key_id} revoked successfully"}
