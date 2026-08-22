"""
QRMaster Pro — QR Customization Schema.

Pydantic model describing all visual customization options for a QR code.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class QRStyle:
    """Allowed QR module shape styles."""
    SQUARE = "square"
    ROUNDED = "rounded"
    CIRCULAR = "circular"
    DOTS = "dots"

    ALL = [SQUARE, ROUNDED, CIRCULAR, DOTS]


class ErrorCorrection:
    """Allowed error correction levels."""
    L = "L"  # ~7%
    M = "M"  # ~15%
    Q = "Q"  # ~25%
    H = "H"  # ~30%

    ALL = [L, M, Q, H]


class LogoPosition:
    """Allowed logo placement positions."""
    CENTER = "center"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"

    ALL = [CENTER, TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT]


class QRCustomization(BaseModel):
    """Visual customization options for a QR code."""

    size: int = Field(default=400, ge=100, le=2000, description="QR size in pixels")
    foreground_color: str = Field(default="#000000", description="Foreground (module) color")
    background_color: str = Field(default="#FFFFFF", description="Background color")
    gradient_enabled: bool = Field(default=False, description="Enable gradient foreground")
    gradient_start: str = Field(default="#6366F1", description="Gradient start color")
    gradient_end: str = Field(default="#8B5CF6", description="Gradient end color")
    transparent_background: bool = Field(default=False, description="Transparent background")
    qr_style: str = Field(default=QRStyle.SQUARE, description="Module shape style")
    margin: int = Field(default=4, ge=0, le=20, description="Quiet zone / margin")
    border_thickness: int = Field(default=0, ge=0, le=20, description="Decorative border thickness")
    border_color: str = Field(default="#000000", description="Decorative border color")
    error_correction: str = Field(default=ErrorCorrection.H, description="Error correction level")
    logo_path: Optional[str] = Field(default=None, description="Path to logo image")
    logo_position: str = Field(default=LogoPosition.CENTER, description="Logo placement")
    logo_size: int = Field(default=20, ge=5, le=40, description="Logo size as % of QR")
    logo_background: bool = Field(default=True, description="Add white bg behind logo")
    frame_style: str = Field(default="none", description="Frame style: none, badge, banner, card")
    frame_text: str = Field(default="SCAN ME", description="Text on frame")
    frame_color: str = Field(default="#4F46E5", description="Frame background color")
    frame_text_color: str = Field(default="#FFFFFF", description="Frame text color")

    @field_validator("qr_style")
    @classmethod
    def validate_style(cls, v: str) -> str:
        if v not in QRStyle.ALL:
            raise ValueError(f"qr_style must be one of {QRStyle.ALL}")
        return v

    @field_validator("error_correction")
    @classmethod
    def validate_ec(cls, v: str) -> str:
        if v not in ErrorCorrection.ALL:
            raise ValueError(f"error_correction must be one of {ErrorCorrection.ALL}")
        return v

    @field_validator("logo_position")
    @classmethod
    def validate_logo_pos(cls, v: str) -> str:
        if v not in LogoPosition.ALL:
            raise ValueError(f"logo_position must be one of {LogoPosition.ALL}")
        return v

    @field_validator("foreground_color", "background_color", "gradient_start",
                     "gradient_end", "border_color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("#") or len(v) not in (7, 9):
            raise ValueError(f"Color must be hex format #RRGGBB, got: {v}")
        return v