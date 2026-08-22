"""
QRMaster Pro — Bulk QR Generation Service.

Processes CSV/Excel files, generates a QR for each row, and packages
them into a ZIP archive. Records the job in qr_bulk_jobs.
"""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.models import QRBulkJob
from app.qr_engine.builders import registry
from app.qr_engine.customization import QRCustomization
from app.qr_engine.renderer import renderer
from app.utils.logger import logger


class BulkService:
    """Service for bulk QR generation from CSV/Excel."""

    def list_jobs(self, db: Session) -> List[Dict[str, Any]]:
        jobs = db.query(QRBulkJob).order_by(QRBulkJob.created_at.desc()).all()
        return [self._serialize(j) for j in jobs]

    def get_job(self, db: Session, job_id: int) -> Optional[Dict[str, Any]]:
        j = db.query(QRBulkJob).filter(QRBulkJob.id == job_id).first()
        return self._serialize(j) if j else None

    def process_file(
        self,
        db: Session,
        file_path: Path,
        qr_type: str,
        column_mapping: Optional[Dict[str, str]] = None,
        customization: Optional[Dict[str, Any]] = None,
        job_name: str = "",
    ) -> Dict[str, Any]:
        """Process an uploaded CSV/Excel file and generate QR codes in bulk."""
        # 1. Read rows
        rows = self._read_file(file_path)
        total = len(rows)
        logger.info(f"Bulk job '{job_name}': {total} rows, type={qr_type}")

        # 2. Create job record
        job = QRBulkJob(
            job_name=job_name or file_path.stem,
            source_filename=file_path.name,
            total_rows=total,
            processed_rows=0,
            status="processing",
            qr_type=qr_type,
            column_mapping=json.dumps(column_mapping or {}, ensure_ascii=False),
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # 3. Generate QR for each row
        custom = QRCustomization(**customization) if customization else QRCustomization()
        zip_path = settings.exports_path / f"bulk_{job.id}.zip"
        processed = 0
        errors: List[str] = []

        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for idx, row in enumerate(rows):
                    try:
                        # Map columns to builder data
                        data = self._map_row(row, column_mapping)
                        encoded = registry.build(qr_type, data)
                        img = renderer.render_image(encoded, custom)
                        img_bytes = renderer.to_bytes(img, fmt="PNG")
                        fname = f"qr_{idx + 1:04d}.png"
                        zf.writestr(fname, img_bytes)
                        processed += 1
                        # Update progress periodically
                        if (idx + 1) % 10 == 0:
                            job.processed_rows = processed
                            db.commit()
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"Row {idx + 1}: {exc}")
                        logger.warning(f"Bulk row {idx + 1} failed: {exc}")

            job.processed_rows = processed
            job.zip_path = str(zip_path)
            job.status = "completed" if not errors else "completed_with_errors"
            job.error_log = "\n".join(errors) if errors else None
            db.commit()
            logger.info(f"Bulk job {job.id} completed: {processed}/{total}")
        except Exception as exc:
            job.status = "failed"
            job.error_log = str(exc)
            db.commit()
            logger.error(f"Bulk job {job.id} failed: {exc}")
            raise

        return self._serialize(job)

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
            # Default: use column names as field names
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
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }


# Singleton
bulk_service = BulkService()