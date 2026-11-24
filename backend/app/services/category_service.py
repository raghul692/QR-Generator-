"""
QRMaster Pro — Category Service.

Business logic for managing QR categories with safe category counts, deletions,
and workspace-level tenant isolation.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import QRCategory, QRHistory
from app.utils.logger import logger


def _slugify(name: str) -> str:
    """Convert a name into a URL-safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    return slug.strip("-")


class CategoryService:
    """Service for QR category management with tenant isolation."""

    def list(self, db: Session, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = db.query(QRCategory)
        if workspace_id and workspace_id != "ws_legacy_default":
            query = query.filter(
                or_(
                    QRCategory.is_default == True,
                    QRCategory.workspace_id == workspace_id,
                )
            )
        cats = query.order_by(QRCategory.id).all()
        result = []
        for c in cats:
            count = db.query(QRHistory).filter(QRHistory.category_id == c.id).count()
            result.append(self._serialize(c, count))
        return result

    def get(self, db: Session, category_id: int) -> Optional[Dict[str, Any]]:
        c = db.query(QRCategory).filter(QRCategory.id == category_id).first()
        if not c:
            return None
        count = db.query(QRHistory).filter(QRHistory.category_id == c.id).count()
        return self._serialize(c, count)

    def create(
        self,
        db: Session,
        name: str,
        description: str = "",
        icon: str = "",
        color: str = "",
        workspace_id: str = "ws_legacy_default",
    ) -> Dict[str, Any]:
        slug = _slugify(name)
        existing = db.query(QRCategory).filter(QRCategory.slug == slug).first()
        if existing:
            slug = f"{slug}-{db.query(QRCategory).count() + 1}"
        cat = QRCategory(
            workspace_id=workspace_id,
            name=name.strip(),
            slug=slug,
            description=description.strip() if description else None,
            icon=icon.strip() if icon else None,
            color=color.strip() if color else None,
            is_default=False,
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
        logger.info(f"Created category id={cat.id}, name={name}, workspace={workspace_id}")
        return self._serialize(cat, 0)

    def update(
        self,
        db: Session,
        category_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        c = db.query(QRCategory).filter(QRCategory.id == category_id).first()
        if not c:
            return None
        if c.is_default:
            raise ValueError("Default system categories cannot be modified.")
        if workspace_id and workspace_id != "ws_legacy_default" and c.workspace_id != workspace_id:
            return None

        if name:
            new_name = name.strip()
            c.name = new_name
            new_slug = _slugify(new_name)
            existing = (
                db.query(QRCategory)
                .filter(QRCategory.slug == new_slug, QRCategory.id != category_id)
                .first()
            )
            if existing:
                new_slug = f"{new_slug}-{category_id}"
            c.slug = new_slug
        if description is not None:
            c.description = description.strip() if description else None
        if icon is not None:
            c.icon = icon.strip() if icon else None
        if color is not None:
            c.color = color.strip() if color else None
        db.commit()
        db.refresh(c)
        count = db.query(QRHistory).filter(QRHistory.category_id == c.id).count()
        return self._serialize(c, count)

    def delete(self, db: Session, category_id: int, workspace_id: Optional[str] = None) -> bool:
        c = db.query(QRCategory).filter(QRCategory.id == category_id).first()
        if not c:
            return False
        if c.is_default:
            raise ValueError("Default system categories cannot be deleted")
        if workspace_id and workspace_id != "ws_legacy_default" and c.workspace_id != workspace_id:
            return False

        # Safely detach QR history items without deleting them
        db.query(QRHistory).filter(QRHistory.category_id == category_id).update(
            {QRHistory.category_id: None}, synchronize_session=False
        )
        db.delete(c)
        db.commit()
        logger.info(f"Deleted category id={category_id}")
        return True

    def _serialize(self, c: QRCategory, qr_count: int = 0) -> Dict[str, Any]:
        return {
            "id": c.id,
            "workspace_id": c.workspace_id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "icon": c.icon,
            "color": c.color,
            "is_default": c.is_default,
            "qr_count": qr_count,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }


# Singleton
category_service = CategoryService()
