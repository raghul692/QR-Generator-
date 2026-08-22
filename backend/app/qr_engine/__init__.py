"""
QRMaster Pro — QR Engine Package.

Combines the data builders (strategy pattern), customization schema, and
image renderer into a single cohesive QR generation engine.
"""
from __future__ import annotations

from app.qr_engine.builders import QRBuilderBase, QRBuilderRegistry, registry
from app.qr_engine.customization import (
    ErrorCorrection,
    LogoPosition,
    QRCustomization,
    QRStyle,
)
from app.qr_engine.renderer import QRRenderer, renderer

__all__ = [
    "QRBuilderBase",
    "QRBuilderRegistry",
    "registry",
    "QRCustomization",
    "QRStyle",
    "ErrorCorrection",
    "LogoPosition",
    "QRRenderer",
    "renderer",
]