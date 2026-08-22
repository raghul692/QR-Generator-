"""
QRMaster Pro — Backup & Restore Service.

Creates backups of the database (SQL dump) and QR images (ZIP), and
records each backup in backup_logs. Supports listing and restoring.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models import BackupLog
from app.utils.logger import logger


class BackupService:
    """Service for backup and restore operations."""

    def list_backups(self, db: Session) -> List[Dict[str, Any]]:
        logs = db.query(BackupLog).order_by(BackupLog.created_at.desc()).all()
        return [self._serialize(l) for l in logs]

    def create_backup(self, db: Session, backup_type: str = "full") -> Dict[str, Any]:
        """Create a backup. Types: full (db+images), db, images."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = settings.backup_path / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        details_parts: List[str] = []
        total_size = 0.0
        status = "success"

        try:
            if backup_type in ("full", "db"):
                sql_path = backup_dir / "database.sql"
                self._dump_database(sql_path)
                total_size += sql_path.stat().st_size
                details_parts.append(f"DB dump: {sql_path.name}")

            if backup_type in ("full", "images"):
                images_zip = backup_dir / "qr_images.zip"
                self._zip_directory(settings.generated_qr_path, images_zip)
                total_size += images_zip.stat().st_size
                details_parts.append(f"Images: {images_zip.name}")

            # Zip the whole backup dir
            final_zip = settings.backup_path / f"backup_{timestamp}.zip"
            self._zip_directory(backup_dir, final_zip)
            # Clean up the intermediate dir
            shutil.rmtree(backup_dir, ignore_errors=True)

            total_size += final_zip.stat().st_size
            file_path = str(final_zip)
            logger.info(f"Backup created: {final_zip} ({total_size} bytes)")
        except Exception as exc:
            status = "failed"
            file_path = None
            total_size = 0.0
            details_parts.append(f"Error: {exc}")
            logger.error(f"Backup failed: {exc}")

        # Record in DB (always persist log)
        log = BackupLog(
            backup_type=backup_type,
            file_path=file_path,
            file_size=total_size,
            status=status,
            details="; ".join(details_parts),
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        if status == "failed":
            raise RuntimeError(f"Backup failed: {'; '.join(details_parts)}")

        return self._serialize(log)

    def restore_backup(self, db: Session, backup_id: int) -> Dict[str, Any]:
        """Restore from a backup ZIP (database + images)."""
        log = db.query(BackupLog).filter(BackupLog.id == backup_id).first()
        if not log or not log.file_path:
            raise ValueError(f"Backup {backup_id} not found or has no file")

        zip_path = Path(log.file_path)
        if not zip_path.exists():
            raise ValueError(f"Backup file not found: {zip_path}")

        extract_dir = settings.backup_path / f"restore_{backup_id}"
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            # Restore database
            sql_file = extract_dir / "database.sql"
            if sql_file.exists():
                self._restore_database(sql_file)

            # Restore images
            images_zip = extract_dir / "qr_images.zip"
            if images_zip.exists():
                with zipfile.ZipFile(images_zip, "r") as zf:
                    zf.extractall(settings.generated_qr_path)

            shutil.rmtree(extract_dir, ignore_errors=True)
            logger.info(f"Restored backup {backup_id}")
            return {"success": True, "message": f"Backup {backup_id} restored successfully"}
        except Exception as exc:
            logger.error(f"Restore failed: {exc}")
            raise

    def _dump_database(self, path: Path) -> None:
        """Dump MySQL database to SQL file using mysqldump or Python fallback."""
        if shutil.which("mysqldump"):
            cmd = [
                "mysqldump",
                f"--host={settings.DB_HOST}",
                f"--port={settings.DB_PORT}",
                f"--user={settings.DB_USER}",
            ]
            if settings.DB_PASSWORD:
                cmd.append(f"--password={settings.DB_PASSWORD}")
            cmd.extend(["--single-transaction", "--routines", "--triggers", settings.DB_NAME])

            with open(path, "w", encoding="utf-8") as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return

        # Python fallback for database dump if mysqldump is missing or failed
        logger.info("Using Python database dump fallback...")
        from sqlalchemy import text
        from app.database.base import Base
        from app.database.session import SessionLocal

        db = SessionLocal()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"-- QRMaster Pro Database Dump (Python Fallback)\n-- Date: {datetime.now()}\n\n")
                f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
                for table in Base.metadata.sorted_tables:
                    rows = db.execute(text(f"SELECT * FROM `{table.name}`")).mappings().all()
                    if rows:
                        cols = ", ".join([f"`{c}`" for c in rows[0].keys()])
                        for row in rows:
                            vals = []
                            for v in row.values():
                                if v is None:
                                    vals.append("NULL")
                                elif isinstance(v, (int, float)):
                                    vals.append(str(v))
                                elif isinstance(v, bool):
                                    vals.append("1" if v else "0")
                                elif isinstance(v, datetime):
                                    vals.append(f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'")
                                else:
                                    escaped = str(v).replace("\\", "\\\\").replace("'", "''")
                                    vals.append(f"'{escaped}'")
                            val_str = ", ".join(vals)
                            f.write(f"INSERT INTO `{table.name}` ({cols}) VALUES ({val_str});\n")
                        f.write("\n")
                f.write("SET FOREIGN_KEY_CHECKS=1;\n")
        finally:
            db.close()

    def _restore_database(self, sql_file: Path) -> None:
        """Restore MySQL database from SQL file using mysql CLI or Python fallback."""
        if shutil.which("mysql"):
            cmd = [
                "mysql",
                f"--host={settings.DB_HOST}",
                f"--port={settings.DB_PORT}",
                f"--user={settings.DB_USER}",
            ]
            if settings.DB_PASSWORD:
                cmd.append(f"--password={settings.DB_PASSWORD}")
            cmd.append(settings.DB_NAME)

            with open(sql_file, "r", encoding="utf-8") as f:
                result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return

        # Python fallback for restore
        logger.info("Using Python database restore fallback...")
        from sqlalchemy import text
        from app.database.session import engine

        sql_content = sql_file.read_text(encoding="utf-8")
        statements = [s.strip() for s in sql_content.split(";") if s.strip()]
        with engine.connect() as conn:
            for stmt in statements:
                if stmt and not stmt.startswith("--"):
                    conn.execute(text(stmt))
            conn.commit()

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