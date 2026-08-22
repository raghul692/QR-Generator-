"""
QRMaster Pro — QR Scanner Engine.

Decodes QR codes from uploaded images using pyzbar (with opencv fallback).
Returns the decoded text, QR type, and raw byte data.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import List, Optional

from PIL import Image

from app.utils.logger import logger

# Try to import pyzbar; fall back gracefully if unavailable
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    _HAS_PYZBAR = True
except Exception:  # noqa: BLE001
    _HAS_PYZBAR = False
    logger.warning("pyzbar not available; scanner will use opencv only")

# Try to import opencv QR detector
try:
    import cv2
    import numpy as np
    _HAS_CV2 = True
except Exception:  # noqa: BLE001
    _HAS_CV2 = False


class ScanResult:
    """Represents a single decoded QR code."""

    def __init__(self, data: str, qr_type: str = "unknown", raw: Optional[bytes] = None):
        self.data = data
        self.qr_type = qr_type
        self.raw = raw

    def to_dict(self) -> dict:
        return {"data": self.data, "qr_type": self.qr_type}

    def __repr__(self) -> str:
        return f"ScanResult(data={self.data!r}, type={self.qr_type})"


class QRScanner:
    """Scans and decodes QR codes from images."""

    def scan_image(self, image_path: Path) -> List[ScanResult]:
        """Decode all QR codes found in an image file."""
        logger.debug(f"Scanning image: {image_path}")
        img = Image.open(image_path).convert("RGB")
        return self._scan_pil(img)

    def scan_bytes(self, image_bytes: bytes) -> List[ScanResult]:
        """Decode QR codes from raw image bytes."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return self._scan_pil(img)

    def _scan_pil(self, img: Image.Image) -> List[ScanResult]:
        results: List[ScanResult] = []

        # Primary: pyzbar
        if _HAS_PYZBAR:
            try:
                decoded = pyzbar_decode(img)
                for d in decoded:
                    data = d.data.decode("utf-8", errors="replace")
                    results.append(ScanResult(data=data, qr_type=d.type, raw=d.data))
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"pyzbar decode failed: {exc}")

        # Fallback: opencv
        if not results and _HAS_CV2:
            try:
                arr = np.array(img)
                gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                detector = cv2.QRCodeDetector()
                data, points, _ = detector.detectAndDecode(gray)
                if data:
                    results.append(ScanResult(data=data, qr_type="QRCODE"))
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"opencv decode failed: {exc}")

        if not results:
            logger.info("No QR codes found in image.")

        return results

    @staticmethod
    def classify(data: str) -> str:
        """Classify a decoded string into a human-readable QR type."""
        d = data.strip().lower()
        if d.startswith("http"):
            return "url"
        if d.startswith("mailto:"):
            return "email"
        if d.startswith("tel:"):
            return "phone"
        if d.startswith("smsto:"):
            return "sms"
        if d.startswith("wifi:"):
            return "wifi"
        if d.startswith("begin:vcard"):
            return "vcard"
        if d.startswith("geo:"):
            return "geo"
        if d.startswith("upi://"):
            return "upi"
        if d.startswith("bitcoin:"):
            return "bitcoin"
        if d.startswith("ethereum:"):
            return "ethereum"
        if d.startswith("begin:vevent"):
            return "event"
        return "text"


# Singleton scanner
scanner = QRScanner()