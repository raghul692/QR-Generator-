"""
QRMaster Pro — Database Initialization & Idempotent Seed Data.

Populates default categories and system settings safely.
Existing records and user customizations are preserved.
Run via:  python -m app.database.seed
"""
from __future__ import annotations

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import (
    QRCategory,
    Setting,
    QRHistory,
    QRTemplate,
    QRBulkJob,
    QRExport,
    Analytics,
    ActivityLog,
    BackupLog,
    DynamicQR,
    ScanLog,
    APIKey,
)
from app.utils.logger import logger


# --------------------------------------------------------------------------- #
#  Default categories covering all supported QR content types
# --------------------------------------------------------------------------- #
DEFAULT_CATEGORIES: List[Dict[str, Any]] = [
    {
        "name": "Website & URLs",
        "slug": "websites",
        "icon": "BsGlobe",
        "color": "#2563EB",
        "description": "Website URLs, landing pages, and web destinations",
    },
    {
        "name": "Text & Information",
        "slug": "text-info",
        "icon": "BsFileText",
        "color": "#4B5563",
        "description": "Plain text, notices, documents, and instructions",
    },
    {
        "name": "WiFi & Networks",
        "slug": "wifi-networks",
        "icon": "BsWifi",
        "color": "#0D9488",
        "description": "Wireless network access credentials and configurations",
    },
    {
        "name": "Contact & vCard",
        "slug": "contact-vcard",
        "icon": "BsPersonVcard",
        "color": "#10B981",
        "description": "vCard contact cards and professional profiles",
    },
    {
        "name": "Email & Communication",
        "slug": "email-communication",
        "icon": "BsEnvelope",
        "color": "#6366F1",
        "description": "Email drafts, customer inquiries, and mailto links",
    },
    {
        "name": "SMS & WhatsApp",
        "slug": "sms-whatsapp",
        "icon": "BsChatDots",
        "color": "#22C55E",
        "description": "Direct SMS messages and WhatsApp chat links",
    },
    {
        "name": "Social Media",
        "slug": "social-media",
        "icon": "BsShare",
        "color": "#EC4899",
        "description": "Social media channels, profiles, and follower links",
    },
    {
        "name": "Business & Marketing",
        "slug": "business-marketing",
        "icon": "BsBriefcase",
        "color": "#3B82F6",
        "description": "Marketing promotions, flyers, menus, and branding",
    },
    {
        "name": "Location & Maps",
        "slug": "location-maps",
        "icon": "BsGeoAlt",
        "color": "#84CC16",
        "description": "GPS coordinates and Google Maps navigation links",
    },
    {
        "name": "Events & Invitations",
        "slug": "events-invitations",
        "icon": "BsCalendarEvent",
        "color": "#06B6D4",
        "description": "Calendar invites, appointments, and video meeting links",
    },
    {
        "name": "Payments & UPI",
        "slug": "payments-upi",
        "icon": "BsCurrencyRupee",
        "color": "#EF4444",
        "description": "UPI, Google Pay, PhonePe, Paytm, and payment gateways",
    },
    {
        "name": "App Downloads",
        "slug": "app-downloads",
        "icon": "BsDownload",
        "color": "#8B5CF6",
        "description": "App Store, Google Play, and direct download links",
    },
    {
        "name": "Digital Assets",
        "slug": "digital-assets",
        "icon": "BsCurrencyBitcoin",
        "color": "#F59E0B",
        "description": "Bitcoin, Ethereum, and crypto wallet addresses",
    },
    {
        "name": "Custom",
        "slug": "custom",
        "icon": "BsGear",
        "color": "#64748B",
        "description": "Custom payloads and miscellaneous QR codes",
    },
]


# --------------------------------------------------------------------------- #
#  Default system settings
# --------------------------------------------------------------------------- #
DEFAULT_SETTINGS: List[Dict[str, Any]] = [
    {"key": "default_qr_size", "value": "400", "category": "qr", "data_type": "int", "description": "Default QR code size in pixels"},
    {"key": "default_error_correction", "value": "H", "category": "qr", "data_type": "string", "description": "Default error correction level (L/M/Q/H)"},
    {"key": "default_foreground_color", "value": "#000000", "category": "qr", "data_type": "string", "description": "Default QR foreground color"},
    {"key": "default_background_color", "value": "#FFFFFF", "category": "qr", "data_type": "string", "description": "Default QR background color"},
    {"key": "default_margin", "value": "4", "category": "qr", "data_type": "int", "description": "Default QR margin (quiet zone)"},
    {"key": "default_border_thickness", "value": "0", "category": "qr", "data_type": "int", "description": "Default border thickness"},
    {"key": "default_qr_style", "value": "square", "category": "qr", "data_type": "string", "description": "Default QR module style"},
    {"key": "theme", "value": "light", "category": "ui", "data_type": "string", "description": "Application theme (light/dark)"},
    {"key": "language", "value": "en", "category": "ui", "data_type": "string", "description": "Application language"},
    {"key": "export_format", "value": "png", "category": "export", "data_type": "string", "description": "Default export format"},
    {"key": "auto_backup_enabled", "value": "false", "category": "backup", "data_type": "bool", "description": "Enable automatic backups"},
    {"key": "auto_backup_frequency", "value": "weekly", "category": "backup", "data_type": "string", "description": "Auto backup frequency"},
    {"key": "image_compression", "value": "true", "category": "performance", "data_type": "bool", "description": "Enable image compression"},
    {"key": "sticker_sheet_layout", "value": "3x7", "category": "export", "data_type": "string", "description": "Default sticker sheet grid layout (3x7 or 3x8)"},
]


def seed_categories(db: Session) -> int:
    """Insert missing default categories without modifying existing ones."""
    inserted = 0
    for cat_data in DEFAULT_CATEGORIES:
        exists = db.query(QRCategory).filter(QRCategory.slug == cat_data["slug"]).first()
        if not exists:
            cat = QRCategory(**cat_data, is_default=True)
            db.add(cat)
            inserted += 1
    if inserted > 0:
        db.commit()
    return inserted


def seed_settings(db: Session) -> int:
    """Insert missing default settings without overwriting user customizations."""
    inserted = 0
    for set_data in DEFAULT_SETTINGS:
        exists = db.query(Setting).filter(Setting.key == set_data["key"]).first()
        if not exists:
            setting = Setting(**set_data)
            db.add(setting)
            inserted += 1
    if inserted > 0:
        db.commit()
    return inserted


def init_database(create_tables: bool = False) -> None:
    """
    Initialize seed data safely.
    create_tables is optional (for local testing/fallback); production uses Alembic migrations.
    """
    if create_tables:
        logger.info("[DB INIT] Ensuring tables exist via metadata...")
        Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        cats_added = seed_categories(db)
        settings_added = seed_settings(db)
        logger.info(f"[SEED] Seed complete. Added {cats_added} categories, {settings_added} settings.")
    except Exception as exc:
        db.rollback()
        logger.error(f"[SEED ERROR] Failed to seed database: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database(create_tables=True)
