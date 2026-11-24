"""
QRMaster Pro — Bulk QR Generation API Router.
Supports chunked processing, background job dispatch, SSE progress streaming, and cancellation.
"""
from __future__ import annotations

import json
from pathlib import Path
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_workspace
from app.config import settings
from app.database.session import get_db
from app.services.bulk_service import bulk_service
from app.utils.logger import logger

router = APIRouter(prefix="/bulk", tags=["Bulk QR Generation"])


@router.get("/", summary="List bulk jobs")
def list_bulk_jobs(
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    return bulk_service.list_jobs(db, workspace_id=workspace_id)


@router.get("/{job_id}", summary="Get a bulk job")
def get_bulk_job(
    job_id: int,
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    result = bulk_service.get_job(db, job_id, workspace_id=workspace_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Bulk job {job_id} not found")
    return result


@router.post("/upload", summary="Upload CSV/Excel and generate QR codes in bulk")
async def upload_bulk(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    qr_type: str = Form(default="url"),
    column_mapping: str = Form(default=""),
    customization: str = Form(default=""),
    job_name: str = Form(default=""),
    async_mode: bool = Form(default=False),
    workspace_id: str = Depends(get_current_workspace),
    db: Session = Depends(get_db),
):
    """Upload a CSV/Excel file and generate a QR for each row."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Sanitize filename and validate extension against directory traversal
    safe_filename = Path(file.filename).name
    ext = Path(safe_filename).suffix.lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        raise HTTPException(
            status_code=400,
            detail=f"File extension '{ext}' is not supported for bulk import. Allowed: .csv, .xlsx, .xls",
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 15 MB.")

    # Save uploaded file with unique prefix
    upload_path = settings.uploads_path / f"bulk_{uuid.uuid4().hex[:8]}_{safe_filename}"
    upload_path.write_bytes(contents)

    # Parse optional JSON params
    mapping = json.loads(column_mapping) if column_mapping else None
    custom = json.loads(customization) if customization else None

    try:
        if async_mode:
            job, _ = bulk_service.create_pending_job(
                db=db,
                file_path=upload_path,
                qr_type=qr_type,
                column_mapping=mapping,
                job_name=job_name,
                workspace_id=workspace_id,
            )
            background_tasks.add_task(
                bulk_service.run_job_bg,
                job_id=job.id,
                file_path=upload_path,
                qr_type=qr_type,
                column_mapping=mapping,
                customization=custom,
            )
            return bulk_service._serialize(job)

        # Synchronous execution for backward compatibility
        result = bulk_service.process_file(
            db=db,
            file_path=upload_path,
            qr_type=qr_type,
            column_mapping=mapping,
            customization=custom,
            job_name=job_name,
            workspace_id=workspace_id,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Bulk upload error: {exc}")
        raise HTTPException(status_code=500, detail="Bulk generation failed")


@router.get("/{job_id}/stream", summary="Stream live bulk job progress events (SSE)")
async def stream_bulk_job_progress(job_id: int):
    """Server-Sent Events endpoint streaming job status, heartbeats, and progress."""
    return StreamingResponse(
        bulk_service.stream_job_events(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{job_id}/cancel", summary="Cancel an active bulk job")
def cancel_bulk_job(job_id: int, db: Session = Depends(get_db)):
    """Cancel a running or pending bulk job."""
    result = bulk_service.cancel_job(db, job_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Bulk job {job_id} not found")
    return result


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
