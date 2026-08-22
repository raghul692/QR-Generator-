"""
QRMaster Pro — Export API Router.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.export_service import export_service
from app.utils.logger import logger

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/history/csv", summary="Export QR history as CSV")
def export_csv(db: Session = Depends(get_db)):
    try:
        data, filename = export_service.export_history_csv(db)
        return Response(
            content=data,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.error(f"CSV export error: {exc}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/history/excel", summary="Export QR history as Excel")
def export_excel(db: Session = Depends(get_db)):
    try:
        data, filename = export_service.export_history_excel(db)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.error(f"Excel export error: {exc}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/history/pdf", summary="Export QR history as PDF report")
def export_pdf(db: Session = Depends(get_db)):
    try:
        data, filename = export_service.export_history_pdf(db)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.error(f"PDF export error: {exc}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.post("/sticker-sheet", summary="Export printable A4 QR sticker sheet")
def export_sticker_sheet(db: Session = Depends(get_db)):
    try:
        data, filename = export_service.export_sticker_sheet_pdf(db)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.error(f"Sticker sheet export error: {exc}")
        raise HTTPException(status_code=500, detail="Sticker sheet export failed")