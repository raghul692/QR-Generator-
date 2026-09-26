"""
QRMaster Pro — ORM Models.

All SQLAlchemy ORM models for the 9 normalized database tables.
Importing this package registers every model on the declarative metadata.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# --------------------------------------------------------------------------- #
#  Timestamp mixin
# --------------------------------------------------------------------------- #
class TimestampMixin:
    """Provides created_at / updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )


# --------------------------------------------------------------------------- #
#  1. qr_categories
# --------------------------------------------------------------------------- #
class QRCategory(Base, TimestampMixin):
    __tablename__ = "qr_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    history_items: Mapped[list["QRHistory"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_categories_slug", "slug"),)


# --------------------------------------------------------------------------- #
#  2. qr_history
# --------------------------------------------------------------------------- #
class QRHistory(Base, TimestampMixin):
    __tablename__ = "qr_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    qr_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    encoded_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preview_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("qr_categories.id", ondelete="SET NULL"), nullable=True
    )
    template_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("qr_templates.id", ondelete="SET NULL"), nullable=True
    )
    customization_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    category: Mapped[Optional["QRCategory"]] = relationship(back_populates="history_items")
    template: Mapped[Optional["QRTemplate"]] = relationship(back_populates="history_items")
    exports: Mapped[list["QRExport"]] = relationship(
        back_populates="qr", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_history_qr_type", "qr_type"),
        Index("idx_history_category", "category_id"),
        Index("idx_history_created", "created_at"),
        Index("idx_history_favorite", "is_favorite"),
    )


# --------------------------------------------------------------------------- #
#  3. qr_templates
# --------------------------------------------------------------------------- #
class QRTemplate(Base, TimestampMixin):
    __tablename__ = "qr_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    history_items: Mapped[list["QRHistory"]] = relationship(back_populates="template")

    __table_args__ = (Index("idx_templates_name", "name"),)


# --------------------------------------------------------------------------- #
#  4. qr_bulk_jobs
# --------------------------------------------------------------------------- #
class QRBulkJob(Base, TimestampMixin):
    __tablename__ = "qr_bulk_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    qr_type: Mapped[str] = mapped_column(String(50), default="url", nullable=False)
    column_mapping: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    zip_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("idx_bulk_status", "status"),)


# --------------------------------------------------------------------------- #
#  5. qr_exports
# --------------------------------------------------------------------------- #
class QRExport(Base, TimestampMixin):
    __tablename__ = "qr_exports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    qr_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("qr_history.id", ondelete="CASCADE"), nullable=True
    )
    export_type: Mapped[str] = mapped_column(String(20), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    qr: Mapped[Optional["QRHistory"]] = relationship(back_populates="exports")

    __table_args__ = (
        Index("idx_exports_qr", "qr_id"),
        Index("idx_exports_format", "format"),
    )


# --------------------------------------------------------------------------- #
#  6. analytics
# --------------------------------------------------------------------------- #
class Analytics(Base, TimestampMixin):
    __tablename__ = "analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_key: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metric_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("metric_type", "metric_key", "metric_date", name="uq_analytics"),
        Index("idx_analytics_type", "metric_type"),
        Index("idx_analytics_date", "metric_date"),
    )


# --------------------------------------------------------------------------- #
#  7. settings
# --------------------------------------------------------------------------- #
class Setting(Base, TimestampMixin):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    data_type: Mapped[str] = mapped_column(String(20), default="string", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("idx_settings_category", "category"),)


# --------------------------------------------------------------------------- #
#  8. activity_logs
# --------------------------------------------------------------------------- #
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    __table_args__ = (
        Index("idx_activity_action", "action"),
        Index("idx_activity_module", "module"),
        Index("idx_activity_created", "created_at"),
    )


# --------------------------------------------------------------------------- #
#  9. backup_logs
# --------------------------------------------------------------------------- #
class BackupLog(Base, TimestampMixin):
    __tablename__ = "backup_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    backup_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="success", nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (Index("idx_backup_type", "backup_type"),)


# --------------------------------------------------------------------------- #
#  10. dynamic_qrs
# --------------------------------------------------------------------------- #
class DynamicQR(Base, TimestampMixin):
    __tablename__ = "dynamic_qrs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    target_url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    qr_history_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("qr_history.id", ondelete="CASCADE"), nullable=True
    )
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scan_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ios_target_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    android_target_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    scan_logs: Mapped[list["ScanLog"]] = relationship(
        back_populates="dynamic_qr", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_dynamic_short_code", "short_code"),
        Index("idx_dynamic_history_id", "qr_history_id"),
    )


# --------------------------------------------------------------------------- #
#  11. scan_logs
# --------------------------------------------------------------------------- #
class ScanLog(Base):
    __tablename__ = "scan_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dynamic_qr_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dynamic_qrs.id", ondelete="CASCADE"), nullable=False
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    browser: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    dynamic_qr: Mapped["DynamicQR"] = relationship(back_populates="scan_logs")

    __table_args__ = (
        Index("idx_scan_dynamic_id", "dynamic_qr_id"),
        Index("idx_scan_scanned_at", "scanned_at"),
    )


# --------------------------------------------------------------------------- #
#  12. api_keys
# --------------------------------------------------------------------------- #
class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (Index("idx_api_keys_hash", "key_hash"),)


__all__ = [
    "Base",
    "TimestampMixin",
    "QRCategory",
    "QRHistory",
    "QRTemplate",
    "QRBulkJob",
    "QRExport",
    "Analytics",
    "Setting",
    "ActivityLog",
    "BackupLog",
    "DynamicQR",
    "ScanLog",
    "APIKey",
]