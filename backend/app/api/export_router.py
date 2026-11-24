"""
QRMaster Pro — Export API Router.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_workspace
from app.database.session import get_db
from app.services.export_service import export_service
from app.utils.logger import logger

router = APIRouter(prefix="/export", tags=["Export"])


class StickerSheetRequest(BaseModel):
    qr_ids: Optional[List[int]] = None
    layout: str = "3x7"


@router.get("/history/csv", summary="Export QR history as CSV")
def export_csv(
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    try:
        data, filename = export_service.export_history_csv(db, workspace_id=workspace_id)
        return Response(
            content=data,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.error(f"CSV export error: {exc}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/history/excel", summary="Export QR history as Excel")
def export_excel(
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    try:
        data, filename = export_service.export_history_excel(db, workspace_id=workspace_id)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.error(f"Excel export error: {exc}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/history/pdf", summary="Export QR history as PDF report")
def export_pdf(
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    try:
        data, filename = export_service.export_history_pdf(db, workspace_id=workspace_id)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.error(f"PDF export error: {exc}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.post("/sticker-sheet", summary="Export printable A4 QR sticker sheet")
def export_sticker_sheet(
    layout: str = Query(default="3x7"),
    req: Optional[StickerSheetRequest] = None,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    try:
        qr_ids = req.qr_ids if req else None
        effective_layout = req.layout if (req and req.layout) else layout
        data, filename = export_service.export_sticker_sheet_pdf(
            db, qr_ids=qr_ids, layout=effective_layout, workspace_id=workspace_id
        )
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        logger.error(f"Sticker sheet export error: {exc}")
        raise HTTPException(status_code=500, detail="Sticker sheet generation failed")
