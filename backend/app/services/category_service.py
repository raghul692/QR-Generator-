"""
QRMaster Pro — Category Service.

Business logic for managing QR categories.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import QRCategory, QRHistory
from app.utils.logger import logger


def _slugify(name: str) -> str:
    """Convert a name into a URL-safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
    return slug.strip("-")


class CategoryService:
    """Service for QR category management."""

    def list(self, db: Session) -> List[Dict[str, Any]]:
        cats = db.query(QRCategory).order_by(QRCategory.id).all()
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

    def create(self, db: Session, name: str, description: str = "",
               icon: str = "", color: str = "") -> Dict[str, Any]:
        slug = _slugify(name)
        # Ensure unique slug
        existing = db.query(QRCategory).filter(QRCategory.slug == slug).first()
        if existing:
            slug = f"{slug}-{db.query(QRCategory).count()}"
        cat = QRCategory(
            name=name, slug=slug, description=description or None,
            icon=icon or None, color=color or None, is_default=False,
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
        logger.info(f"Created category id={cat.id}, name={name}")
        return self._serialize(cat, 0)

    def update(self, db: Session, category_id: int, name: Optional[str] = None,
               description: Optional[str] = None, icon: Optional[str] = None,
               color: Optional[str] = None) -> Optional[Dict[str, Any]]:
        c = db.query(QRCategory).filter(QRCategory.id == category_id).first()
        if not c:
            return None
        if name:
            c.name = name
            c.slug = _slugify(name)
        if description is not None:
            c.description = description
        if icon is not None:
            c.icon = icon
        if color is not None:
            c.color = color
        db.commit()
        db.refresh(c)
        return self._serialize(c, 0)

    def delete(self, db: Session, category_id: int) -> bool:
        c = db.query(QRCategory).filter(QRCategory.id == category_id).first()
        if not c:
            return False
        if c.is_default:
            raise ValueError("Default categories cannot be deleted")
        db.delete(c)
        db.commit()
        logger.info(f"Deleted category id={category_id}")
        return True

    def _serialize(self, c: QRCategory, qr_count: int) -> Dict[str, Any]:
        return {
            "id": c.id,
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