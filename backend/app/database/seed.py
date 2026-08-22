"""
QRMaster Pro — Database Initialization & Seed Data.

Creates all tables and populates default categories and settings.
Run via:  python -m app.database.seed
"""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import (
    QRCategory, Setting, QRHistory, QRTemplate, QRBulkJob, QRExport,
    Analytics, ActivityLog, BackupLog, DynamicQR, ScanLog, APIKey
)


# --------------------------------------------------------------------------- #
#  Default categories
# --------------------------------------------------------------------------- #
DEFAULT_CATEGORIES = [
    {"name": "Business", "slug": "business", "icon": "BsBriefcase", "color": "#3B82F6", "description": "Business cards, contacts, company links"},
    {"name": "Education", "slug": "education", "icon": "BsBook", "color": "#8B5CF6", "description": "Educational resources and materials"},
    {"name": "Personal", "slug": "personal", "icon": "BsPerson", "color": "#10B981", "description": "Personal QR codes"},
    {"name": "Marketing", "slug": "marketing", "icon": "BsMegaphone", "color": "#F59E0B", "description": "Marketing campaigns and promotions"},
    {"name": "Payments", "slug": "payments", "icon": "BsCreditCard", "color": "#EF4444", "description": "UPI and payment QR codes"},
    {"name": "Social Media", "slug": "social-media", "icon": "BsShare", "color": "#EC4899", "description": "Social media profile links"},
    {"name": "Events", "slug": "events", "icon": "BsCalendarEvent", "color": "#06B6D4", "description": "Events and calendar entries"},
    {"name": "Files", "slug": "files", "icon": "BsFolder", "color": "#6366F1", "description": "File download links"},
    {"name": "Location", "slug": "location", "icon": "BsGeoAlt", "color": "#84CC16", "description": "Maps and GPS locations"},
    {"name": "Custom", "slug": "custom", "icon": "BsGear", "color": "#64748B", "description": "Custom QR codes"},
]


# --------------------------------------------------------------------------- #
#  Default settings
# --------------------------------------------------------------------------- #
DEFAULT_SETTINGS = [
    {"key": "default_qr_size", "value": "400", "category": "qr", "data_type": "int", "description": "Default QR code size in pixels"},
    {"key": "default_error_correction", "value": "H", "category": "qr", "data_type": "string", "description": "Default error correction level (L/M/Q/H)"},
    {"key": "default_foreground_color", "value": "#000000", "category": "qr", "data_type": "string", "description": "Default QR foreground color"},
    {"key": "default_background_color", "value": "#FFFFFF", "category": "qr", "data_type": "string", "description": "Default QR background color"},
    {"key": "default_margin", "value": "4", "category": "qr", "data_type": "int", "description": "Default QR margin (quiet zone)"},
    {"key": "default_border_thickness", "value": "4", "category": "qr", "data_type": "int", "description": "Default border thickness"},
    {"key": "default_qr_style", "value": "square", "category": "qr", "data_type": "string", "description": "Default QR module style"},
    {"key": "theme", "value": "light", "category": "ui", "data_type": "string", "description": "Application theme (light/dark)"},
    {"key": "language", "value": "en", "category": "ui", "data_type": "string", "description": "Application language"},
    {"key": "export_format", "value": "png", "category": "export", "data_type": "string", "description": "Default export format"},
    {"key": "auto_backup_enabled", "value": "false", "category": "backup", "data_type": "bool", "description": "Enable automatic backups"},
    {"key": "auto_backup_frequency", "value": "weekly", "category": "backup", "data_type": "string", "description": "Auto backup frequency"},
    {"key": "image_compression", "value": "true", "category": "performance", "data_type": "bool", "description": "Enable image compression"},
]


def init_database() -> None:
    """Create all tables and seed default data."""
    print("[SEED] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("[SEED] Tables created successfully.")

    db: Session = SessionLocal()
    try:
        # --- Seed categories ---
        existing_cats = db.query(QRCategory).count()
        if existing_cats == 0:
            print("[SEED] Seeding default categories...")
            for cat_data in DEFAULT_CATEGORIES:
                cat = QRCategory(**cat_data, is_default=True)
                db.add(cat)
            db.commit()
            print(f"[SEED] Inserted {len(DEFAULT_CATEGORIES)} categories.")
        else:
            print(f"[SEED] Categories already exist ({existing_cats}). Skipping.")

        # --- Seed settings ---
        existing_settings = db.query(Setting).count()
        if existing_settings == 0:
            print("[SEED] Seeding default settings...")
            for set_data in DEFAULT_SETTINGS:
                setting = Setting(**set_data)
                db.add(setting)
            db.commit()
            print(f"[SEED] Inserted {len(DEFAULT_SETTINGS)} settings.")
        else:
            print(f"[SEED] Settings already exist ({existing_settings}). Skipping.")

        print("[SEED] Database initialization complete.")
    except Exception as exc:
        db.rollback()
        print(f"[SEED ERROR] {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()