"""
QRMaster Pro — QR Generation API Router.

Endpoints for QR type metadata, preview, generate, regenerate, and download.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas import (
    MessageResponse,
    QRGenerateRequest,
    QRGenerateResponse,
    QRPreviewRequest,
    QRPreviewResponse,
)
from app.services.qr_service import qr_service
from app.utils.logger import logger

router = APIRouter(prefix="/qr", tags=["QR Generation"])


@router.get("/types", summary="List all supported QR types")
def list_qr_types():
    """Return metadata for all supported QR types (for dynamic form rendering)."""
    return qr_service.list_types()


@router.get("/types/{qr_type}", summary="Get metadata for a specific QR type")
def get_qr_type(qr_type: str):
    try:
        return qr_service.get_type(qr_type)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/preview", response_model=QRPreviewResponse, summary="Preview a QR code")
def preview_qr(req: QRPreviewRequest):
    """Generate a QR preview without saving to history."""
    try:
        encoded, b64 = qr_service.preview(req.qr_type, req.data, req.customization)
        return QRPreviewResponse(encoded_data=encoded, preview_base64=b64)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Preview error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to generate preview")


@router.post("/generate", response_model=QRGenerateResponse, summary="Generate and save a QR code")
def generate_qr(req: QRGenerateRequest, db: Session = Depends(get_db)):
    """Generate a QR code and optionally save it to history."""
    try:
        result = qr_service.generate(
            db=db,
            title=req.title,
            qr_type=req.qr_type,
            data=req.data,
            category_id=req.category_id,
            customization=req.customization,
            save_to_history=req.save_to_history,
        )
        if req.is_dynamic and result.get("id"):
            from app.services.dynamic_qr_service import dynamic_qr_service
            target = req.data.get("url") or result.get("content") or "https://qrmaster.pro"
            dynamic_qr_service.create_dynamic_qr(
                db=db,
                title=req.title,
                target_url=target,
                qr_history_id=result.get("id"),
                password=req.password,
                expires_at=req.expires_at,
                ios_target_url=req.ios_target_url,
                android_target_url=req.android_target_url,
            )
        return QRGenerateResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Generate error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to generate QR code")


@router.post("/regenerate/{history_id}", response_model=QRGenerateResponse,
             summary="Regenerate a QR from history")
def regenerate_qr(history_id: int, db: Session = Depends(get_db)):
    """Regenerate a QR code from an existing history record."""
    try:
        result = qr_service.regenerate(db, history_id)
        return QRGenerateResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error(f"Regenerate error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to regenerate QR code")


@router.get("/download/{history_id}", summary="Download a QR code in a specific format")
def download_qr(
    history_id: int,
    fmt: str = Query(default="png", description="png|jpg|svg|pdf"),
    db: Session = Depends(get_db),
):
    """Download a QR code in the requested format. Increments download count."""
    try:
        data, filename, media_type = qr_service.download(db, history_id, fmt)
        return Response(
            content=data,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error(f"Download error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to download QR code")