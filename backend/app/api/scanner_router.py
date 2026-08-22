"""
QRMaster Pro — Scanner API Router.

Endpoints for decoding QR codes from uploaded images.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.qr_engine.scanner import scanner
from app.schemas import ScanResponse
from app.utils.logger import logger

router = APIRouter(prefix="/scanner", tags=["QR Scanner"])


@router.post("/scan", response_model=ScanResponse, summary="Scan an uploaded image for QR codes")
async def scan_image(file: UploadFile = File(...)):
    """Decode QR code(s) from an uploaded image file."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        contents = await file.read()
        results = scanner.scan_bytes(contents)
        return ScanResponse(
            results=[r.to_dict() for r in results],
            count=len(results),
        )
    except Exception as exc:
        logger.error(f"Scan error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to scan image")