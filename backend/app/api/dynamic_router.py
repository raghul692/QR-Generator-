"""
QRMaster Pro — Dynamic QR API Router.

Endpoints for managing dynamic QR targets, password/expiry settings,
and retrieving real-time scan analytics.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.dynamic_qr_service import dynamic_qr_service

router = APIRouter(prefix="/dynamic", tags=["Dynamic QR Codes"])


class CreateDynamicQRRequest(BaseModel):
    title: str = Field(..., max_length=255)
    target_url: str = Field(...)
    qr_history_id: Optional[int] = None
    password: Optional[str] = None
    expires_at: Optional[datetime] = None


class UpdateDynamicQRRequest(BaseModel):
    title: Optional[str] = None
    target_url: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    expires_at: Optional[datetime] = None


@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_dynamic_qr(req: CreateDynamicQRRequest, db: Session = Depends(get_db)):
    """Create a new dynamic QR record."""
    dyn = dynamic_qr_service.create_dynamic_qr(
        db=db,
        title=req.title,
        target_url=req.target_url,
        qr_history_id=req.qr_history_id,
        password=req.password,
        expires_at=req.expires_at,
    )
    return {
        "id": dyn.id,
        "short_code": dyn.short_code,
        "redirect_url": f"http://127.0.0.1:8000/r/{dyn.short_code}",
        "target_url": dyn.target_url,
        "title": dyn.title,
        "is_active": dyn.is_active,
        "created_at": dyn.created_at.isoformat(),
    }


@router.get("/{dynamic_id}/analytics", response_model=Dict[str, Any])
def get_dynamic_analytics(dynamic_id: int, db: Session = Depends(get_db)):
    """Get real-time scan analytics for a dynamic QR code."""
    try:
        return dynamic_qr_service.get_analytics(db, dynamic_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/{dynamic_id}", response_model=Dict[str, Any])
def update_dynamic_qr(
    dynamic_id: int, req: UpdateDynamicQRRequest, db: Session = Depends(get_db)
):
    """Update destination URL, title, password, or expiration of a dynamic QR."""
    try:
        dyn = dynamic_qr_service.update_dynamic_qr(
            db=db,
            dynamic_id=dynamic_id,
            target_url=req.target_url,
            title=req.title,
            is_active=req.is_active,
            password=req.password,
            expires_at=req.expires_at,
        )
        return {
            "id": dyn.id,
            "short_code": dyn.short_code,
            "target_url": dyn.target_url,
            "title": dyn.title,
            "is_active": dyn.is_active,
            "has_password": bool(dyn.password_hash),
            "expires_at": dyn.expires_at.isoformat() if dyn.expires_at else None,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
