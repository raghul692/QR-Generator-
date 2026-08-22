"""
QRMaster Pro — Backup & Restore API Router.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas import BackupCreateRequest, MessageResponse
from app.services.backup_service import backup_service
from app.utils.logger import logger

router = APIRouter(prefix="/backup", tags=["Backup & Restore"])


@router.get("/", summary="List all backups")
def list_backups(db: Session = Depends(get_db)):
    return backup_service.list_backups(db)


@router.post("/", summary="Create a backup")
def create_backup(req: BackupCreateRequest, db: Session = Depends(get_db)):
    try:
        return backup_service.create_backup(db, backup_type=req.backup_type)
    except Exception as exc:
        logger.error(f"Backup creation error: {exc}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {exc}")


@router.post("/{backup_id}/restore", response_model=MessageResponse,
             summary="Restore from a backup")
def restore_backup(backup_id: int, db: Session = Depends(get_db)):
    try:
        result = backup_service.restore_backup(db, backup_id)
        return MessageResponse(message=result["message"], success=True)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error(f"Restore error: {exc}")
        raise HTTPException(status_code=500, detail=f"Restore failed: {exc}")


@router.get("/{backup_id}/download", summary="Download a backup ZIP")
def download_backup(backup_id: int, db: Session = Depends(get_db)):
    logs = backup_service.list_backups(db)
    log = next((l for l in logs if l["id"] == backup_id), None)
    if not log or not log.get("file_path"):
        raise HTTPException(status_code=404, detail=f"Backup {backup_id} not found")
    zip_path = Path(log["file_path"])
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Backup file not found on disk")
    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=f"backup_{backup_id}.zip",
    )