"""
QRMaster Pro — Dynamic QR API Router.

Endpoints for managing dynamic QR targets, password/expiry settings,
listing dynamic QR campaigns, and retrieving real-time scan analytics.
Uses PUBLIC_REDIRECT_BASE_URL for production-safe redirect links.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.models import DynamicQR
from app.services.dynamic_qr_service import dynamic_qr_service

router = APIRouter(prefix="/dynamic", tags=["Dynamic QR Codes"])


class CreateDynamicQRRequest(BaseModel):
    title: str = Field(..., max_length=255)
    target_url: str = Field(...)
    qr_history_id: Optional[int] = None
    password: Optional[str] = None
    expires_at: Optional[datetime] = None
    ios_target_url: Optional[str] = None
    android_target_url: Optional[str] = None
    max_scans: Optional[int] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    meta_pixel_id: Optional[str] = None
    google_tag_id: Optional[str] = None
    geo_routing_json: Optional[str] = None
    schedule_start_time: Optional[str] = None
    schedule_end_time: Optional[str] = None
    schedule_timezone: Optional[str] = None
    schedule_fallback_url: Optional[str] = None


class UpdateDynamicQRRequest(BaseModel):
    title: Optional[str] = None
    target_url: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    expires_at: Optional[datetime] = None
    ios_target_url: Optional[str] = None
    android_target_url: Optional[str] = None
    max_scans: Optional[int] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    meta_pixel_id: Optional[str] = None
    google_tag_id: Optional[str] = None
    geo_routing_json: Optional[str] = None
    schedule_start_time: Optional[str] = None
    schedule_end_time: Optional[str] = None
    schedule_timezone: Optional[str] = None
    schedule_fallback_url: Optional[str] = None


@router.get("", response_model=List[Dict[str, Any]])
def list_dynamic_qrs(db: Session = Depends(get_db)):
    """List all dynamic QR codes with scan counts and status."""
    records = db.query(DynamicQR).order_by(DynamicQR.created_at.desc()).all()
    base_url = settings.public_redirect_url
    return [
        {
            "id": r.id,
            "short_code": r.short_code,
            "title": r.title,
            "target_url": r.target_url,
            "ios_target_url": r.ios_target_url,
            "android_target_url": r.android_target_url,
            "redirect_url": f"{base_url}/r/{r.short_code}",
            "scan_count": r.scan_count,
            "max_scans": r.max_scans,
            "utm_source": r.utm_source,
            "utm_medium": r.utm_medium,
            "utm_campaign": r.utm_campaign,
            "meta_pixel_id": r.meta_pixel_id,
            "google_tag_id": r.google_tag_id,
            "geo_routing_json": r.geo_routing_json,
            "schedule_start_time": r.schedule_start_time,
            "schedule_end_time": r.schedule_end_time,
            "schedule_timezone": r.schedule_timezone,
            "schedule_fallback_url": r.schedule_fallback_url,
            "is_active": r.is_active,
            "is_expired": dynamic_qr_service.is_expired(r),
            "has_password": bool(r.password_hash),
            "expires_at": r.expires_at.isoformat() if r.expires_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


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
        ios_target_url=req.ios_target_url,
        android_target_url=req.android_target_url,
        max_scans=req.max_scans,
        utm_source=req.utm_source,
        utm_medium=req.utm_medium,
        utm_campaign=req.utm_campaign,
        meta_pixel_id=req.meta_pixel_id,
        google_tag_id=req.google_tag_id,
        geo_routing_json=req.geo_routing_json,
        schedule_start_time=req.schedule_start_time,
        schedule_end_time=req.schedule_end_time,
        schedule_timezone=req.schedule_timezone,
        schedule_fallback_url=req.schedule_fallback_url,
    )
    base_url = settings.public_redirect_url
    return {
        "id": dyn.id,
        "short_code": dyn.short_code,
        "redirect_url": f"{base_url}/r/{dyn.short_code}",
        "target_url": dyn.target_url,
        "ios_target_url": dyn.ios_target_url,
        "android_target_url": dyn.android_target_url,
        "max_scans": dyn.max_scans,
        "utm_source": dyn.utm_source,
        "utm_medium": dyn.utm_medium,
        "utm_campaign": dyn.utm_campaign,
        "meta_pixel_id": dyn.meta_pixel_id,
        "google_tag_id": dyn.google_tag_id,
        "geo_routing_json": dyn.geo_routing_json,
        "schedule_start_time": dyn.schedule_start_time,
        "schedule_end_time": dyn.schedule_end_time,
        "schedule_timezone": dyn.schedule_timezone,
        "schedule_fallback_url": dyn.schedule_fallback_url,
        "title": dyn.title,
        "is_active": dyn.is_active,
        "has_password": bool(dyn.password_hash),
        "created_at": dyn.created_at.isoformat() if dyn.created_at else None,
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
    """Update destination URL, title, password, attribution, limits, or expiration of a dynamic QR."""
    try:
        dyn = dynamic_qr_service.update_dynamic_qr(
            db=db,
            dynamic_id=dynamic_id,
            target_url=req.target_url,
            title=req.title,
            is_active=req.is_active,
            password=req.password,
            expires_at=req.expires_at,
            ios_target_url=req.ios_target_url,
            android_target_url=req.android_target_url,
            max_scans=req.max_scans,
            utm_source=req.utm_source,
            utm_medium=req.utm_medium,
            utm_campaign=req.utm_campaign,
            meta_pixel_id=req.meta_pixel_id,
            google_tag_id=req.google_tag_id,
            geo_routing_json=req.geo_routing_json,
            schedule_start_time=req.schedule_start_time,
            schedule_end_time=req.schedule_end_time,
            schedule_timezone=req.schedule_timezone,
            schedule_fallback_url=req.schedule_fallback_url,
        )
        base_url = settings.public_redirect_url
        return {
            "id": dyn.id,
            "short_code": dyn.short_code,
            "target_url": dyn.target_url,
            "ios_target_url": dyn.ios_target_url,
            "android_target_url": dyn.android_target_url,
            "max_scans": dyn.max_scans,
            "utm_source": dyn.utm_source,
            "utm_medium": dyn.utm_medium,
            "utm_campaign": dyn.utm_campaign,
            "meta_pixel_id": dyn.meta_pixel_id,
            "google_tag_id": dyn.google_tag_id,
            "geo_routing_json": dyn.geo_routing_json,
            "schedule_start_time": dyn.schedule_start_time,
            "schedule_end_time": dyn.schedule_end_time,
            "schedule_timezone": dyn.schedule_timezone,
            "schedule_fallback_url": dyn.schedule_fallback_url,
            "redirect_url": f"{base_url}/r/{dyn.short_code}",
            "title": dyn.title,
            "is_active": dyn.is_active,
            "has_password": bool(dyn.password_hash),
            "expires_at": dyn.expires_at.isoformat() if dyn.expires_at else None,
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{dynamic_id}", status_code=status.HTTP_200_OK)
def delete_dynamic_qr(dynamic_id: int, db: Session = Depends(get_db)):
    """Delete a dynamic QR code and associated scan logs."""
    dyn = db.query(DynamicQR).filter(DynamicQR.id == dynamic_id).first()
    if not dyn:
        raise HTTPException(status_code=404, detail=f"Dynamic QR {dynamic_id} not found")
    db.delete(dyn)
    db.commit()
    return {"message": f"Dynamic QR {dynamic_id} deleted successfully", "success": True}
