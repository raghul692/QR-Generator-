"""
QRMaster Pro — QR History Service.

Business logic for listing, searching, filtering, updating, and deleting
QR history records with pagination and sorting.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import QRCategory, QRHistory
from app.utils.logger import logger


class HistoryService:
    """Service for QR history CRUD + search/filter."""

    def list_history(
        self,
        db: Session,
        search: Optional[str] = None,
        qr_type: Optional[str] = None,
        category_id: Optional[int] = None,
        is_favorite: Optional[bool] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Dict[str, Any]], int, int]:
        """Return (items, total, total_pages)."""
        query = db.query(QRHistory)

        # Search
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    QRHistory.title.ilike(like),
                    QRHistory.qr_type.ilike(like),
                    QRHistory.content.ilike(like),
                    QRHistory.encoded_data.ilike(like),
                )
            )

        # Filters
        if qr_type:
            query = query.filter(QRHistory.qr_type == qr_type)
        if category_id:
            query = query.filter(QRHistory.category_id == category_id)
        if is_favorite is not None:
            query = query.filter(QRHistory.is_favorite == is_favorite)
        if date_from:
            try:
                dt_from = datetime.fromisoformat(date_from)
                query = query.filter(QRHistory.created_at >= dt_from)
            except ValueError:
                pass
        if date_to:
            try:
                dt_to = datetime.fromisoformat(date_to)
                query = query.filter(QRHistory.created_at <= dt_to)
            except ValueError:
                pass

        # Sorting
        sort_col = getattr(QRHistory, sort_by, QRHistory.created_at)
        query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

        # Pagination
        total = query.count()
        total_pages = (total + page_size - 1) // page_size if page_size else 1
        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()

        items = [self._serialize(db, r) for r in records]
        return items, total, total_pages

    def get(self, db: Session, history_id: int) -> Optional[Dict[str, Any]]:
        record = db.query(QRHistory).filter(QRHistory.id == history_id).first()
        if not record:
            return None
        return self._serialize(db, record)

    def update(
        self,
        db: Session,
        history_id: int,
        title: Optional[str] = None,
        category_id: Optional[int] = None,
        is_favorite: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        record = db.query(QRHistory).filter(QRHistory.id == history_id).first()
        if not record:
            return None
        if title is not None:
            record.title = title
        if category_id is not None:
            record.category_id = category_id
        if is_favorite is not None:
            record.is_favorite = is_favorite
        db.commit()
        db.refresh(record)
        logger.info(f"Updated QR history id={history_id}")
        return self._serialize(db, record)

    def delete(self, db: Session, history_id: int) -> bool:
        record = db.query(QRHistory).filter(QRHistory.id == history_id).first()
        if not record:
            return False
        # Optionally delete the image file
        if record.file_path:
            try:
                from pathlib import Path
                p = Path(record.file_path)
                if p.exists():
                    p.unlink()
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Could not delete file {record.file_path}: {exc}")
        db.delete(record)
        db.commit()
        logger.info(f"Deleted QR history id={history_id}")
        return True

    def toggle_favorite(self, db: Session, history_id: int) -> Optional[bool]:
        record = db.query(QRHistory).filter(QRHistory.id == history_id).first()
        if not record:
            return None
        record.is_favorite = not record.is_favorite
        db.commit()
        db.refresh(record)
        return record.is_favorite

    def _serialize(self, db: Session, record: QRHistory) -> Dict[str, Any]:
        category_name = None
        if record.category_id:
            cat = db.query(QRCategory).filter(QRCategory.id == record.category_id).first()
            if cat:
                category_name = cat.name
        return {
            "id": record.id,
            "title": record.title,
            "qr_type": record.qr_type,
            "content": record.content,
            "encoded_data": record.encoded_data,
            "preview_path": record.preview_path,
            "file_path": record.file_path,
            "category_id": record.category_id,
            "category_name": category_name,
            "customization_json": record.customization_json,
            "download_count": record.download_count,
            "is_favorite": record.is_favorite,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }


# Singleton
history_service = HistoryService()