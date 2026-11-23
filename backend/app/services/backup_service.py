"""
QRMaster Pro — Backup & Restore Service.

Creates snapshots of the database (JSON/SQL dump) and QR images (ZIP),
recording each backup event in backup_logs. Designed for PostgreSQL / Supabase
and Render cloud environments with zero local mysqldump dependency.
"""
from __future__ import annotations

import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import ActivityLog, BackupLog
from app.utils.logger import logger


class BackupService:
    """Service for database and file backup/restore operations."""

    def list_backups(self, db: Session) -> List[Dict[str, Any]]:
        """List all historical backup logs."""
        logs = db.query(BackupLog).order_by(BackupLog.created_at.desc()).all()
        return [self._serialize(l) for l in logs]

    def create_backup(self, db: Session, backup_type: str = "full") -> Dict[str, Any]:
        """
        Create a backup snapshot.
        Supported types: 'full' (data + images), 'db' (data only), 'images' (images only).
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = settings.backup_path / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        details_parts: List[str] = []
        total_size = 0.0
        status = "success"

        try:
            if backup_type in ("full", "db"):
                dump_path = backup_dir / "database_dump.json"
                self._dump_database_json(db, dump_path)
                total_size += dump_path.stat().st_size
                details_parts.append(f"DB snapshot: {dump_path.name}")

            if backup_type in ("full", "images"):
                images_zip = backup_dir / "qr_images.zip"
                self._zip_directory(settings.generated_qr_path, images_zip)
                total_size += images_zip.stat().st_size
                details_parts.append(f"Images: {images_zip.name}")

            # Package entire backup into final ZIP archive
            final_zip = settings.backup_path / f"backup_{timestamp}.zip"
            self._zip_directory(backup_dir, final_zip)
            shutil.rmtree(backup_dir, ignore_errors=True)

            total_size = float(final_zip.stat().st_size)
            file_path = str(final_zip)
            logger.info(f"Backup created: {final_zip} ({total_size} bytes)")
        except Exception as exc:
            status = "failed"
            file_path = None
            total_size = 0.0
            details_parts.append(f"Error: {exc}")
            logger.error(f"Backup creation failed: {exc}")

        # Always record in backup_logs and activity_logs
        log = BackupLog(
            backup_type=backup_type,
            file_path=file_path,
            file_size=total_size,
            status=status,
            details="; ".join(details_parts),
        )
        db.add(log)
        activity = ActivityLog(
            action=f"backup_created_{status}",
            module="backup",
            details=f"Type: {backup_type}, Size: {total_size} bytes, File: {file_path}",
        )
        db.add(activity)
        db.commit()
        db.refresh(log)

        if status == "failed":
            raise RuntimeError(f"Backup failed: {'; '.join(details_parts)}")

        return self._serialize(log)

    def restore_backup(self, db: Session, backup_id: int) -> Dict[str, Any]:
        """Restore database and images from a backup archive."""
        log = db.query(BackupLog).filter(BackupLog.id == backup_id).first()
        if not log or not log.file_path:
            raise ValueError(f"Backup {backup_id} not found or has no archive file")

        zip_path = Path(log.file_path)
        if not zip_path.exists():
            raise ValueError(f"Backup file archive not found: {zip_path}")

        extract_dir = settings.backup_path / f"restore_{backup_id}"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            # 1. Restore database if dump is present
            dump_file = extract_dir / "database_dump.json"
            if dump_file.exists():
                self._restore_database_json(db, dump_file)

            # 2. Restore images
            images_zip = extract_dir / "qr_images.zip"
            if images_zip.exists():
                with zipfile.ZipFile(images_zip, "r") as zf:
                    zf.extractall(settings.generated_qr_path)

            shutil.rmtree(extract_dir, ignore_errors=True)
            activity = ActivityLog(
                action="backup_restored",
                module="backup",
                details=f"Restored backup ID {backup_id}",
            )
            db.add(activity)
            db.commit()
            logger.info(f"Successfully restored backup {backup_id}")
            return {"success": True, "message": f"Backup {backup_id} restored successfully"}
        except Exception as exc:
            logger.error(f"Restore failed: {exc}")
            raise

    def _dump_database_json(self, db: Session, path: Path) -> None:
        """Dump all tables into a structured JSON file."""
        data: Dict[str, List[Dict[str, Any]]] = {}
        for table in Base.metadata.sorted_tables:
            query = text(f'SELECT * FROM "{table.name}"')
            rows = db.execute(query).mappings().all()
            table_data = []
            for row in rows:
                item = {}
                for k, v in row.items():
                    if isinstance(v, datetime):
                        item[k] = v.isoformat()
                    else:
                        item[k] = v
                table_data.append(item)
            data[table.name] = table_data

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _restore_database_json(self, db: Session, dump_file: Path) -> None:
        """Restore tables from a structured JSON dump."""
        with open(dump_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Import in order of sorted_tables
        for table in Base.metadata.sorted_tables:
            records = data.get(table.name, [])
            if not records:
                continue
            for rec in records:
                # Convert ISO datetimes back
                for k, v in rec.items():
                    if isinstance(v, str) and ("T" in v or "-" in v) and len(v) >= 19:
                        try:
                            rec[k] = datetime.fromisoformat(v)
                        except ValueError:
                            pass
                # Construct insert
                columns = list(rec.keys())
                col_names = ", ".join([f'"{c}"' for c in columns])
                placeholders = ", ".join([f":{c}" for c in columns])
                stmt = text(f'INSERT INTO "{table.name}" ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING')
                try:
                    db.execute(stmt, rec)
                except Exception:
                    pass
        db.commit()

    def _zip_directory(self, src: Path, dest: Path) -> None:
        """Zip a directory's contents into dest."""
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in src.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(src)
                    zf.write(file_path, arcname)

    def _serialize(self, log: BackupLog) -> Dict[str, Any]:
        return {
            "id": log.id,
            "backup_type": log.backup_type,
            "file_path": log.file_path,
            "file_size": log.file_size,
            "status": log.status,
            "details": log.details,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }


# Singleton
backup_service = BackupService()
