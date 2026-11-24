"""
QRMaster Pro — QR History Service.

Business logic for listing, searching, filtering, updating, and deleting
QR history records with pagination, sorting, tenant isolation, archiving, and duplication.
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
    """Service for QR history CRUD + search/filter + multi-tenant isolation."""

    def _apply_workspace_filter(self, query, workspace_id: Optional[str]):
        """Filter query by tenant workspace. Legacy workspace has access to legacy records."""
        if not workspace_id:
            return query
        if workspace_id == "ws_legacy_default":
            return query.filter(
                or_(
                    QRHistory.workspace_id == "ws_legacy_default",
                    QRHistory.workspace_id.is_(None),
                )
            )
        return query.filter(QRHistory.workspace_id == workspace_id)

    def _get_record(self, db: Session, history_id: int, workspace_id: Optional[str] = None) -> Optional[QRHistory]:
        query = db.query(QRHistory).filter(QRHistory.id == history_id)
        query = self._apply_workspace_filter(query, workspace_id)
        return query.first()

    def list_history(
        self,
        db: Session,
        search: Optional[str] = None,
        qr_type: Optional[str] = None,
        category_id: Optional[int] = None,
        is_favorite: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 10,
        workspace_id: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int, int]:
        """Return (items, total, total_pages) scoped to workspace."""
        query = db.query(QRHistory)
        query = self._apply_workspace_filter(query, workspace_id)

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

        # Archive filter applied at query or serialization level
        all_records = query.all()
        filtered_records = []
        for r in all_records:
            custom = {}
            if r.customization_json:
                try:
                    custom = json.loads(r.customization_json)
                except Exception:
                    custom = {}
            archived = bool(custom.get("is_archived", False))
            if is_archived is not None and archived != is_archived:
                continue
            filtered_records.append(r)

        total = len(filtered_records)
        total_pages = (total + page_size - 1) // page_size if page_size else 1
        offset = (page - 1) * page_size
        records = filtered_records[offset : offset + page_size]

        items = [self._serialize(db, r) for r in records]
        return items, total, total_pages

    def get(self, db: Session, history_id: int, workspace_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        record = self._get_record(db, history_id, workspace_id)
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
        tags: Optional[List[str]] = None,
        is_archived: Optional[bool] = None,
        workspace_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        record = self._get_record(db, history_id, workspace_id)
        if not record:
            return None
        if title is not None:
            record.title = title
        if category_id is not None:
            record.category_id = category_id
        if is_favorite is not None:
            record.is_favorite = is_favorite
        if tags is not None or is_archived is not None:
            custom = {}
            if record.customization_json:
                try:
                    custom = json.loads(record.customization_json)
                except Exception:
                    custom = {}
            if tags is not None:
                custom["tags"] = tags
            if is_archived is not None:
                custom["is_archived"] = is_archived
            record.customization_json = json.dumps(custom, ensure_ascii=False)

        db.commit()
        db.refresh(record)
        logger.info(f"Updated QR history id={history_id}")
        return self._serialize(db, record)

    def delete(self, db: Session, history_id: int, workspace_id: Optional[str] = None) -> bool:
        record = self._get_record(db, history_id, workspace_id)
        if not record:
            return False
        # Delete the image file if present locally
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

    def toggle_favorite(self, db: Session, history_id: int, workspace_id: Optional[str] = None) -> Optional[bool]:
        record = self._get_record(db, history_id, workspace_id)
        if not record:
            return None
        record.is_favorite = not record.is_favorite
        db.commit()
        db.refresh(record)
        return record.is_favorite

    def duplicate(self, db: Session, history_id: int, workspace_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Duplicate a QR code history item."""
        record = self._get_record(db, history_id, workspace_id)
        if not record:
            return None
        target_ws = workspace_id or record.workspace_id or "ws_legacy_default"
        new_record = QRHistory(
            workspace_id=target_ws,
            title=f"{record.title} (Copy)",
            qr_type=record.qr_type,
            content=record.content,
            encoded_data=record.encoded_data,
            preview_path=record.preview_path,
            file_path=record.file_path,
            category_id=record.category_id,
            template_id=record.template_id,
            customization_json=record.customization_json,
            download_count=0,
            is_favorite=False,
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        logger.info(f"Duplicated QR history id={history_id} -> new_id={new_record.id}")
        return self._serialize(db, new_record)

    def toggle_archive(self, db: Session, history_id: int, workspace_id: Optional[str] = None) -> Optional[bool]:
        """Toggle archived state in customization_json."""
        record = self._get_record(db, history_id, workspace_id)
        if not record:
            return None
        custom = {}
        if record.customization_json:
            try:
                custom = json.loads(record.customization_json)
            except Exception:
                custom = {}
        curr = bool(custom.get("is_archived", False))
        custom["is_archived"] = not curr
        record.customization_json = json.dumps(custom, ensure_ascii=False)
        db.commit()
        db.refresh(record)
        logger.info(f"Toggled archive QR history id={history_id} -> is_archived={not curr}")
        return not curr

    def _serialize(self, db: Session, record: QRHistory) -> Dict[str, Any]:
        category_name = None
        if record.category:
            category_name = record.category.name
        elif record.category_id:
            cat = db.query(QRCategory).filter(QRCategory.id == record.category_id).first()
            if cat:
                category_name = cat.name
        custom = {}
        if record.customization_json:
            try:
                custom = json.loads(record.customization_json)
            except Exception:
                custom = {}
        return {
            "id": record.id,
            "workspace_id": record.workspace_id,
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
            "is_archived": bool(custom.get("is_archived", False)),
            "tags": custom.get("tags", []),
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }


# Singleton
history_service = HistoryService()
