"""
QRMaster Pro — Bulk QR Generation Service.

Processes CSV/Excel files, generates a QR for each row in chunks (default 25),
maintains heartbeat timestamps, and packages results into a ZIP archive.
Records and tracks jobs in qr_bulk_jobs with a durable state machine.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
import json
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
import zipfile

from sqlalchemy.orm import Session

from app.config import settings
from app.database import session as session_module
from app.models import QRBulkJob
from app.qr_engine.builders import registry
from app.qr_engine.customization import QRCustomization
from app.qr_engine.renderer import renderer
from app.utils.logger import logger


class BulkService:
    """Service for bulk QR generation from CSV/Excel with durable queue state."""

    CHUNK_SIZE = 25

    def list_jobs(self, db: Session) -> List[Dict[str, Any]]:
        jobs = db.query(QRBulkJob).order_by(QRBulkJob.created_at.desc()).all()
        return [self._serialize(j) for j in jobs]

    def get_job(self, db: Session, job_id: int) -> Optional[Dict[str, Any]]:
        j = db.query(QRBulkJob).filter(QRBulkJob.id == job_id).first()
        return self._serialize(j) if j else None

    def cancel_job(self, db: Session, job_id: int) -> Optional[Dict[str, Any]]:
        """Mark an in-progress or pending bulk job as cancelled."""
        job = db.query(QRBulkJob).filter(QRBulkJob.id == job_id).first()
        if not job:
            return None
        if job.status not in ("completed", "failed", "cancelled"):
            job.status = "cancelled"
            job.cancelled_at = datetime.utcnow()
            db.commit()
            db.refresh(job)
            logger.info(f"Bulk job {job_id} cancelled by user request.")
        return self._serialize(job)

    def create_pending_job(
        self,
        db: Session,
        file_path: Path,
        qr_type: str,
        column_mapping: Optional[Dict[str, str]] = None,
        job_name: str = "",
    ) -> Tuple[QRBulkJob, List[Dict[str, Any]]]:
        """Read uploaded file, calculate total rows, and persist pending job."""
        rows = self._read_file(file_path)
        total = len(rows)

        job = QRBulkJob(
            job_name=job_name or file_path.stem,
            source_filename=file_path.name,
            total_rows=total,
            processed_rows=0,
            status="pending",
            qr_type=qr_type,
            chunk_size=self.CHUNK_SIZE,
            column_mapping=json.dumps(column_mapping or {}, ensure_ascii=False),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job, rows

    def execute_job(
        self,
        db: Session,
        job_id: int,
        rows: List[Dict[str, Any]],
        qr_type: str,
        column_mapping: Optional[Dict[str, str]] = None,
        customization: Optional[Dict[str, Any]] = None,
    ) -> QRBulkJob:
        """Run chunked QR processing loop with state machine transitions and heartbeats."""
        job = db.query(QRBulkJob).filter(QRBulkJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.status = "processing"
        job.heartbeat_at = datetime.utcnow()
        db.commit()

        custom = QRCustomization(**customization) if customization else QRCustomization()
        zip_path = settings.exports_path / f"bulk_{job.id}.zip"
        processed = 0
        errors: List[str] = []
        total = len(rows)

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # Process in chunks of CHUNK_SIZE (25)
                for chunk_start in range(0, total, self.CHUNK_SIZE):
                    # Check cancellation signal between chunks
                    db.refresh(job)
                    if job.status == "cancelled" or job.cancelled_at is not None:
                        logger.info(f"Bulk job {job_id} execution aborted due to cancellation.")
                        break

                    chunk_rows = rows[chunk_start : chunk_start + self.CHUNK_SIZE]
                    for idx_in_chunk, row in enumerate(chunk_rows):
                        row_idx = chunk_start + idx_in_chunk + 1
                        try:
                            data = self._map_row(row, column_mapping)
                            encoded = registry.build(qr_type, data)
                            img = renderer.render_image(encoded, custom)
                            img_bytes = renderer.to_bytes(img, fmt="PNG")
                            fname = f"qr_{row_idx:04d}.png"
                            zf.writestr(fname, img_bytes)
                            processed += 1
                        except Exception as row_exc:  # noqa: BLE001
                            errors.append(f"Row {row_idx}: {row_exc}")
                            logger.warning(f"Bulk job {job_id} row {row_idx} failed: {row_exc}")

                    # Commit chunk progress and heartbeat
                    job.processed_rows = processed
                    job.heartbeat_at = datetime.utcnow()
                    db.commit()

            # Finalize status
            db.refresh(job)
            if job.status == "cancelled":
                logger.info(f"Bulk job {job_id} marked as cancelled in finalize stage.")
            else:
                job.processed_rows = processed
                job.zip_path = str(zip_path)
                job.status = "completed" if not errors else "completed_with_errors"
                if errors:
                    job.error_log = "\n".join(errors)
                    job.error_details = json.dumps(errors[:50])
                db.commit()
                logger.info(f"Bulk job {job_id} finished: {processed}/{total} rows.")
        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)
            job.error_details = str(exc)
            db.commit()
            logger.error(f"Bulk job {job_id} failed with error: {exc}")
            raise

        return job

    def process_file(
        self,
        db: Session,
        file_path: Path,
        qr_type: str,
        column_mapping: Optional[Dict[str, str]] = None,
        customization: Optional[Dict[str, Any]] = None,
        job_name: str = "",
    ) -> Dict[str, Any]:
        """Synchronous wrapper for processing a file immediately."""
        job, rows = self.create_pending_job(db, file_path, qr_type, column_mapping, job_name)
        finished_job = self.execute_job(db, job.id, rows, qr_type, column_mapping, customization)
        return self._serialize(finished_job)

    def run_job_bg(
        self,
        job_id: int,
        file_path: Path,
        qr_type: str,
        column_mapping: Optional[Dict[str, str]] = None,
        customization: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Background task entry point with isolated database session."""
        db = session_module.SessionLocal()
        try:
            rows = self._read_file(file_path)
            self.execute_job(db, job_id, rows, qr_type, column_mapping, customization)
        except Exception as exc:
            logger.error(f"Background execution of bulk job {job_id} failed: {exc}")
        finally:
            db.close()

    async def stream_job_events(self, job_id: int) -> AsyncGenerator[str, None]:
        """Yield Server-Sent Events (SSE) representing live job progress."""
        terminal_statuses = {"completed", "completed_with_errors", "failed", "cancelled"}
        max_polls = 1200  # 10 minutes at 0.5s interval

        for _ in range(max_polls):
            db = session_module.SessionLocal()
            try:
                job = db.query(QRBulkJob).filter(QRBulkJob.id == job_id).first()
                if not job:
                    yield f"event: error\ndata: {json.dumps({'error': 'Job not found'})}\n\n"
                    break

                payload = {
                    "id": job.id,
                    "processed": job.processed_rows,
                    "total": job.total_rows,
                    "status": job.status,
                    "heartbeat": job.heartbeat_at.isoformat() if job.heartbeat_at else None,
                    "error_log": job.error_log,
                }
                yield f"data: {json.dumps(payload)}\n\n"

                if job.status in terminal_statuses:
                    break
            finally:
                db.close()

            await asyncio.sleep(0.5)

    def _read_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read CSV or Excel into a list of dict rows."""
        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            import pandas as pd
            df = pd.read_csv(file_path)
        elif suffix in (".xlsx", ".xls"):
            import pandas as pd
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        return df.fillna("").to_dict(orient="records")

    def _map_row(self, row: Dict[str, Any], mapping: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Map row columns to builder data fields."""
        if not mapping:
            return {k: str(v) for k, v in row.items()}
        result = {}
        for field, column in mapping.items():
            if column in row:
                result[field] = str(row[column])
        return result

    def _serialize(self, j: QRBulkJob) -> Dict[str, Any]:
        return {
            "id": j.id,
            "job_name": j.job_name,
            "source_filename": j.source_filename,
            "total_rows": j.total_rows,
            "processed_rows": j.processed_rows,
            "status": j.status,
            "qr_type": j.qr_type,
            "zip_path": j.zip_path,
            "chunk_size": j.chunk_size,
            "heartbeat_at": j.heartbeat_at.isoformat() if j.heartbeat_at else None,
            "cancelled_at": j.cancelled_at.isoformat() if j.cancelled_at else None,
            "retry_count": j.retry_count,
            "error_log": j.error_log,
            "error_details": j.error_details,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "updated_at": j.updated_at.isoformat() if j.updated_at else None,
        }


# Singleton
bulk_service = BulkService()
