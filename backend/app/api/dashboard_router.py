"""
QRMaster Pro — Dashboard & Analytics API Router.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_workspace
from app.database.session import get_db
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/stats", summary="Get dashboard statistics")
def get_stats(
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    return analytics_service.get_dashboard_stats(db, workspace_id=workspace_id)


@router.get("/charts", summary="Get dashboard chart data")
def get_charts(
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    return analytics_service.get_dashboard_charts(db, workspace_id=workspace_id)


@router.get("/analytics", summary="Get full analytics report")
def get_analytics(
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    return analytics_service.get_analytics(db, workspace_id=workspace_id)
