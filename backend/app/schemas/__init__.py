"""
QRMaster Pro — Pydantic Schemas (Request/Response DTOs).

All API request and response models for validation and serialization.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
#  Generic
# --------------------------------------------------------------------------- #
class MessageResponse(BaseModel):
    message: str
    success: bool = True
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# --------------------------------------------------------------------------- #
#  QR Generation
# --------------------------------------------------------------------------- #
class QRGenerateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="QR title")
    qr_type: str = Field(..., description="QR type key (e.g. 'url', 'text', 'wifi')")
    data: Dict[str, Any] = Field(default_factory=dict, description="Type-specific input data")
    category_id: Optional[int] = None
    save_to_history: bool = Field(default=True, description="Persist to qr_history")
    customization: Optional[Dict[str, Any]] = Field(default=None, description="Visual options")


class QRGenerateResponse(BaseModel):
    id: Optional[int] = None
    title: str
    qr_type: str
    content: str
    encoded_data: str
    preview_base64: str
    file_path: Optional[str] = None
    category_id: Optional[int] = None


class QRPreviewRequest(BaseModel):
    qr_type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    customization: Optional[Dict[str, Any]] = None


class QRPreviewResponse(BaseModel):
    encoded_data: str
    preview_base64: str


# --------------------------------------------------------------------------- #
#  QR History
# --------------------------------------------------------------------------- #
class QRHistoryOut(BaseModel):
    id: int
    title: str
    qr_type: str
    content: str
    encoded_data: Optional[str] = None
    preview_path: Optional[str] = None
    file_path: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    customization_json: Optional[str] = None
    download_count: int = 0
    is_favorite: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QRHistoryUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    is_favorite: Optional[bool] = None


class QRHistoryFilter(BaseModel):
    search: Optional[str] = None
    qr_type: Optional[str] = None
    category_id: Optional[int] = None
    is_favorite: Optional[bool] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sort_by: Optional[str] = Field(default="created_at", description="created_at|title|download_count")
    sort_order: Optional[str] = Field(default="desc", description="asc|desc")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


# --------------------------------------------------------------------------- #
#  Categories
# --------------------------------------------------------------------------- #
class QRCategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: bool = False
    qr_count: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QRCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


# --------------------------------------------------------------------------- #
#  Bulk
# --------------------------------------------------------------------------- #
class BulkJobOut(BaseModel):
    id: int
    job_name: str
    source_filename: str
    total_rows: int
    processed_rows: int
    status: str
    qr_type: str
    zip_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------- #
#  Dashboard / Analytics
# --------------------------------------------------------------------------- #
class DashboardStats(BaseModel):
    total_qr: int
    today_qr: int
    total_downloads: int
    total_categories: int
    total_bulk_jobs: int
    favorites: int


class ChartDataPoint(BaseModel):
    label: str
    value: int


class DashboardCharts(BaseModel):
    qr_type_distribution: List[ChartDataPoint]
    daily_generation: List[ChartDataPoint]
    category_distribution: List[ChartDataPoint]
    download_trends: List[ChartDataPoint]


class AnalyticsOut(BaseModel):
    most_generated_type: Optional[Dict[str, Any]] = None
    most_downloaded: Optional[Dict[str, Any]] = None
    category_usage: List[ChartDataPoint]
    daily_activity: List[ChartDataPoint]
    weekly_activity: List[ChartDataPoint]
    monthly_activity: List[ChartDataPoint]
    export_stats: List[ChartDataPoint]


# --------------------------------------------------------------------------- #
#  Settings
# --------------------------------------------------------------------------- #
class SettingOut(BaseModel):
    id: int
    key: str
    value: str
    category: str
    data_type: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    value: str


class SettingsBulkUpdate(BaseModel):
    settings: Dict[str, str] = Field(..., description="Map of key -> value")


# --------------------------------------------------------------------------- #
#  Export
# --------------------------------------------------------------------------- #
class ExportRequest(BaseModel):
    qr_id: Optional[int] = None
    format: str = Field(..., description="png|jpg|svg|pdf|csv|excel|zip")
    include_charts: bool = False


# --------------------------------------------------------------------------- #
#  Backup
# --------------------------------------------------------------------------- #
class BackupCreateRequest(BaseModel):
    backup_type: str = Field(default="full", description="full|db|images")


class BackupLogOut(BaseModel):
    id: int
    backup_type: str
    file_path: Optional[str] = None
    file_size: Optional[float] = None
    status: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------- #
#  Activity Logs
# --------------------------------------------------------------------------- #
class ActivityLogOut(BaseModel):
    id: int
    action: str
    module: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --------------------------------------------------------------------------- #
#  Scanner
# --------------------------------------------------------------------------- #
class ScanResponse(BaseModel):
    results: List[Dict[str, str]]
    count: int


# --------------------------------------------------------------------------- #
#  QR Types metadata
# --------------------------------------------------------------------------- #
class QRTypeMeta(BaseModel):
    key: str
    label: str
    fields: List[Dict[str, Any]]