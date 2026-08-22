"""
QRMaster Pro — Bulk QR Generation API Router.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.services.bulk_service import bulk_service
from app.utils.logger import logger

router = APIRouter(prefix="/bulk", tags=["Bulk QR Generation"])


@router.get("/", summary="List bulk jobs")
def list_bulk_jobs(db: Session = Depends(get_db)):
    return bulk_service.list_jobs(db)


@router.get("/{job_id}", summary="Get a bulk job")
def get_bulk_job(job_id: int, db: Session = Depends(get_db)):
    result = bulk_service.get_job(db, job_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Bulk job {job_id} not found")
    return result


@router.post("/upload", summary="Upload CSV/Excel and generate QR codes in bulk")
async def upload_bulk(
    file: UploadFile = File(...),
    qr_type: str = Form(default="url"),
    column_mapping: str = Form(default=""),
    customization: str = Form(default=""),
    job_name: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Upload a CSV/Excel file and generate a QR for each row."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Save uploaded file
    upload_path = settings.uploads_path / file.filename
    with open(upload_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    # Parse optional JSON params
    mapping = json.loads(column_mapping) if column_mapping else None
    custom = json.loads(customization) if customization else None

    try:
        result = bulk_service.process_file(
            db=db,
            file_path=upload_path,
            qr_type=qr_type,
            column_mapping=mapping,
            customization=custom,
            job_name=job_name,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Bulk upload error: {exc}")
        raise HTTPException(status_code=500, detail="Bulk generation failed")


@router.get("/{job_id}/download", summary="Download the ZIP of a bulk job")
def download_bulk_zip(job_id: int, db: Session = Depends(get_db)):
    job = bulk_service.get_job(db, job_id)
    if not job or not job.get("zip_path"):
        raise HTTPException(status_code=404, detail=f"ZIP for job {job_id} not found")
    zip_path = Path(job["zip_path"])
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="ZIP file not found on disk")
    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=f"bulk_qr_{job_id}.zip",
    )