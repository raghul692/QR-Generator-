"""
QRMaster Pro — ORM Models.

All SQLAlchemy ORM models for normalized database tables.
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
#  0. workspaces & members (Multi-tenancy & RBAC)
# --------------------------------------------------------------------------- #
class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    owner_id: Mapped[str] = mapped_column(String(100), nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="enterprise", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    members: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )
    custom_domains: Mapped[list["CustomDomain"]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_workspaces_slug", "slug"),
        Index("idx_workspaces_owner", "owner_id"),
    )


class WorkspaceMember(Base, TimestampMixin):
    __tablename__ = "workspace_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="members")

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
        Index("idx_member_workspace", "workspace_id"),
        Index("idx_member_user", "user_id"),
    )


# --------------------------------------------------------------------------- #
#  1. qr_categories
# --------------------------------------------------------------------------- #
class QRCategory(Base, TimestampMixin):
    __tablename__ = "qr_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    history_items: Mapped[list["QRHistory"]] = relationship(
        back_populates="category"
    )

    __table_args__ = (
        Index("idx_categories_slug", "slug"),
        Index("idx_categories_workspace", "workspace_id"),
    )


# --------------------------------------------------------------------------- #
#  2. qr_history
# --------------------------------------------------------------------------- #
class QRHistory(Base, TimestampMixin):
    __tablename__ = "qr_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
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
        Index("idx_history_workspace", "workspace_id"),
        Index("idx_history_qr_type", "qr_type"),
        Index("idx_history_category", "category_id"),
        Index("idx_history_created", "created_at"),
        Index("idx_history_favorite", "is_favorite"),
        Index("idx_history_category_created", "category_id", "created_at"),
        Index("idx_history_type_created", "qr_type", "created_at"),
    )


# --------------------------------------------------------------------------- #
#  3. qr_templates
# --------------------------------------------------------------------------- #
class QRTemplate(Base, TimestampMixin):
    __tablename__ = "qr_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    history_items: Mapped[list["QRHistory"]] = relationship(back_populates="template")

    __table_args__ = (
        Index("idx_templates_name", "name"),
        Index("idx_templates_workspace", "workspace_id"),
    )


# --------------------------------------------------------------------------- #
#  4. qr_bulk_jobs
# --------------------------------------------------------------------------- #
class QRBulkJob(Base, TimestampMixin):
    __tablename__ = "qr_bulk_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    qr_type: Mapped[str] = mapped_column(String(50), default="url", nullable=False)
    column_mapping: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    zip_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    heartbeat_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chunk_size: Mapped[int] = mapped_column(Integer, default=25, nullable=False)

    __table_args__ = (
        Index("idx_bulk_workspace", "workspace_id"),
        Index("idx_bulk_status", "status"),
        Index("idx_bulk_heartbeat", "heartbeat_at"),
    )


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
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
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
    ios_target_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    android_target_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    max_scans: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    meta_pixel_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    google_tag_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    geo_routing_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    schedule_start_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    schedule_end_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    schedule_timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    schedule_fallback_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    # Relationships
    scan_logs: Mapped[list["ScanLog"]] = relationship(
        back_populates="dynamic_qr", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_dynamic_workspace", "workspace_id"),
        Index("idx_dynamic_short_code", "short_code"),
        Index("idx_dynamic_history_id", "qr_history_id"),
        Index("idx_dynamic_short_active", "short_code", "is_active"),
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
        Index("idx_scan_logs_dynamic_created", "dynamic_qr_id", "scanned_at"),
        Index("idx_scan_logs_ip_dynamic", "ip_address", "dynamic_qr_id"),
    )


# --------------------------------------------------------------------------- #
#  12. api_keys
# --------------------------------------------------------------------------- #
class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(10), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    scopes: Mapped[str] = mapped_column(
        String(255), default="qr:read,qr:write,analytics:read", nullable=False
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_api_keys_hash", "key_hash"),
        Index("idx_api_keys_workspace", "workspace_id"),
    )


# --------------------------------------------------------------------------- #
#  13. landing_pages
# --------------------------------------------------------------------------- #
class LandingPage(Base, TimestampMixin):
    __tablename__ = "landing_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    theme: Mapped[str] = mapped_column(String(50), default="default", nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    button_text: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    button_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    social_links_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_landing_pages_slug", "slug"),
        Index("idx_landing_pages_workspace", "workspace_id"),
    )


# --------------------------------------------------------------------------- #
#  14. digital_menus
# --------------------------------------------------------------------------- #
class DigitalMenu(Base, TimestampMixin):
    __tablename__ = "digital_menus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    sections_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_menus_workspace", "workspace_id"),
    )


# --------------------------------------------------------------------------- #
#  15. custom_domains
# --------------------------------------------------------------------------- #
class CustomDomain(Base, TimestampMixin):
    __tablename__ = "custom_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    verification_token: Mapped[str] = mapped_column(String(64), nullable=False)
    ssl_status: Mapped[str] = mapped_column(String(20), default="provisioning", nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="custom_domains")

    __table_args__ = (
        Index("idx_domains_workspace", "workspace_id"),
        Index("idx_domains_domain", "domain"),
    )


# --------------------------------------------------------------------------- #
#  16. webhook_subscriptions & delivery_logs (Phase 4 Developer Platform)
# --------------------------------------------------------------------------- #
class WebhookSubscription(Base, TimestampMixin):
    __tablename__ = "webhook_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(
        String(64), default="ws_legacy_default", nullable=False
    )
    target_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    secret: Mapped[str] = mapped_column(String(64), nullable=False)
    events: Mapped[str] = mapped_column(
        String(255), default="scan.created,qr.expired,qr.limit_reached", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    delivery_logs: Mapped[list["WebhookDeliveryLog"]] = relationship(
        back_populates="webhook", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_webhook_workspace", "workspace_id"),
    )


class WebhookDeliveryLog(Base):
    __tablename__ = "webhook_delivery_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    webhook_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    # Relationships
    webhook: Mapped["WebhookSubscription"] = relationship(back_populates="delivery_logs")

    __table_args__ = (
        Index("idx_delivery_webhook", "webhook_id"),
        Index("idx_delivery_created", "delivered_at"),
    )


__all__ = [
    "Base",
    "TimestampMixin",
    "Workspace",
    "WorkspaceMember",
    "CustomDomain",
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
    "LandingPage",
    "DigitalMenu",
    "WebhookSubscription",
    "WebhookDeliveryLog",
]
