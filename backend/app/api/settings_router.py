"""
QRMaster Pro — Settings API Router.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas import SettingUpdate, SettingsBulkUpdate
from app.services.settings_service import settings_service

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/", summary="List all settings")
def list_settings(db: Session = Depends(get_db)):
    return settings_service.list_all(db)


@router.get("/dict", summary="Get all settings as key-value dict")
def get_settings_dict(db: Session = Depends(get_db)):
    return settings_service.get_as_dict(db)


@router.get("/{category}", summary="List settings by category")
def list_settings_by_category(category: str, db: Session = Depends(get_db)):
    return settings_service.list_by_category(db, category)


@router.put("/{key}", summary="Update a single setting")
def update_setting(key: str, req: SettingUpdate, db: Session = Depends(get_db)):
    result = settings_service.update(db, key, req.value)
    if not result:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return result


@router.put("/", summary="Bulk update settings")
def bulk_update_settings(req: SettingsBulkUpdate, db: Session = Depends(get_db)):
    return settings_service.bulk_update(db, req.settings)