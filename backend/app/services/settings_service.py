"""
QRMaster Pro — Settings Service.

Business logic for reading and updating application settings (key-value store).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Setting
from app.utils.logger import logger


class SettingsService:
    """Service for application settings management."""

    def list_all(self, db: Session) -> List[Dict[str, Any]]:
        settings = db.query(Setting).order_by(Setting.category, Setting.key).all()
        return [self._serialize(s) for s in settings]

    def list_by_category(self, db: Session, category: str) -> List[Dict[str, Any]]:
        settings = (
            db.query(Setting)
            .filter(Setting.category == category)
            .order_by(Setting.key)
            .all()
        )
        return [self._serialize(s) for s in settings]

    def get(self, db: Session, key: str) -> Optional[str]:
        s = db.query(Setting).filter(Setting.key == key).first()
        return s.value if s else None

    def get_as_dict(self, db: Session) -> Dict[str, str]:
        """Return all settings as a key->value dict (useful for frontend)."""
        settings = db.query(Setting).all()
        return {s.key: s.value for s in settings}

    def update(self, db: Session, key: str, value: str) -> Optional[Dict[str, Any]]:
        s = db.query(Setting).filter(Setting.key == key).first()
        if not s:
            return None
        s.value = value
        db.commit()
        db.refresh(s)
        logger.info(f"Updated setting: {key}={value}")
        return self._serialize(s)

    def bulk_update(self, db: Session, settings_map: Dict[str, str]) -> List[Dict[str, Any]]:
        updated = []
        for key, value in settings_map.items():
            s = db.query(Setting).filter(Setting.key == key).first()
            if s:
                s.value = value
                updated.append(self._serialize(s))
        db.commit()
        logger.info(f"Bulk updated {len(updated)} settings")
        return updated

    def _serialize(self, s: Setting) -> Dict[str, Any]:
        return {
            "id": s.id,
            "key": s.key,
            "value": s.value,
            "category": s.category,
            "data_type": s.data_type,
            "description": s.description,
        }


# Singleton
settings_service = SettingsService()