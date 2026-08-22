"""
QRMaster Pro — Dashboard & Analytics API Router.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@router.get("/stats", summary="Get dashboard statistics")
def get_stats(db: Session = Depends(get_db)):
    return analytics_service.get_dashboard_stats(db)


@router.get("/charts", summary="Get dashboard chart data")
def get_charts(db: Session = Depends(get_db)):
    return analytics_service.get_dashboard_charts(db)


@router.get("/analytics", summary="Get full analytics report")
def get_analytics(db: Session = Depends(get_db)):
    return analytics_service.get_analytics(db)