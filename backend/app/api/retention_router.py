"""
QRMaster Pro — Data Retention & GDPR API Router.

Endpoints for checking scan log retention metrics, triggering manual/cron
90-day retention purges, and executing GDPR workspace data erasure.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import (
    LEGACY_DEFAULT_WORKSPACE,
    get_current_user,
    get_current_workspace,
    require_role,
)
from app.database.session import get_db
from app.services.cleanup_service import cleanup_service

router = APIRouter(prefix="/retention", tags=["Enterprise Retention & GDPR"])


class PurgeScanLogsRequest(BaseModel):
    retention_days: int = Field(default=90, ge=1, le=365)


class PurgeWorkspaceRequest(BaseModel):
    confirm_workspace_id: str = Field(...)


@router.get("/summary")
def get_retention_summary(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve system-wide scan log counts, oldest entries, and retention configuration."""
    return cleanup_service.get_retention_summary(db)


@router.post("/purge-scan-logs")
def trigger_purge_scan_logs(
    payload: PurgeScanLogsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Purge scan logs older than specified retention days (default: 90 days).
    Enforces audit logging and returns count of deleted records.
    """
    result = cleanup_service.purge_expired_scan_logs(db, retention_days=payload.retention_days)
    return result


@router.post("/anonymize-ips")
def trigger_anonymize_ips(
    days: int = Query(30, ge=1, le=365),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Anonymize IP addresses older than specified days (default: 30 days) for GDPR compliance."""
    anonymized_count = cleanup_service.anonymize_stale_ips(db, older_than_days=days)
    return {
        "status": "success",
        "older_than_days": days,
        "anonymized_count": anonymized_count,
    }


@router.post("/purge-workspace")
def trigger_purge_workspace(
    payload: PurgeWorkspaceRequest,
    workspace_id: str = Depends(get_current_workspace),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GDPR Article 17 Right to Erasure: Permanently purge all workspace data.
    Requires workspace owner verification.
    """
    target_ws = payload.confirm_workspace_id.strip()
    if target_ws != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation workspace ID does not match active workspace",
        )

    if target_ws == LEGACY_DEFAULT_WORKSPACE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot purge legacy default workspace",
        )

    result = cleanup_service.purge_workspace_data(db, workspace_id=target_ws)
    return result
