"""
QRMaster Pro — QR Generation Service.

Business logic for generating, previewing, and persisting QR codes.
Coordinates the builder registry, renderer, and database history.
"""
from __future__ import annotations

import base64
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from PIL import Image

from app.config import settings
from app.models import QRHistory
from app.qr_engine.builders import registry
from app.qr_engine.customization import QRCustomization
from app.qr_engine.renderer import renderer
from app.qr_engine.types_meta import get_all_types, get_type_meta
from app.utils.logger import logger


class QRService:
    """Service for QR code generation and management."""

    # ------------------------------------------------------------------ #
    #  Type metadata
    # ------------------------------------------------------------------ #
    def list_types(self) -> list:
        """Return metadata for all supported QR types."""
        return get_all_types()

    def get_type(self, qr_type: str) -> Dict[str, Any]:
        return get_type_meta(qr_type)

    # ------------------------------------------------------------------ #
    #  Preview (no DB save)
    # ------------------------------------------------------------------ #
    def preview(
        self,
        qr_type: str,
        data: Dict[str, Any],
        customization: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str]:
        """Generate a preview QR. Returns (encoded_data, base64_image)."""
        encoded = registry.build(qr_type, data)
        custom = self._build_customization(customization)
        img = renderer.render_image(encoded, custom)
        img_bytes = renderer.to_bytes(img, fmt="PNG")
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        return encoded, f"data:image/png;base64,{b64}"

    # ------------------------------------------------------------------ #
    #  Generate + save
    # ------------------------------------------------------------------ #
    def generate(
        self,
        db: Session,
        title: str,
        qr_type: str,
        data: Dict[str, Any],
        category_id: Optional[int] = None,
        customization: Optional[Dict[str, Any]] = None,
        save_to_history: bool = True,
    ) -> Dict[str, Any]:
        """Generate a QR code, optionally persist to history, return response."""
        logger.info(f"Generating QR: type={qr_type}, title={title}")

        # 1. Build encoded data
        encoded = registry.build(qr_type, data)
        custom = self._build_customization(customization)

        # 2. Render image
        img = renderer.render_image(encoded, custom)

        # 3. Save PNG file
        filename = f"qr_{qr_type}_{uuid.uuid4().hex[:8]}.png"
        file_path = settings.generated_qr_path / filename
        renderer.save_png(img, file_path)
        logger.debug(f"Saved QR image: {file_path}")

        # 4. Base64 preview
        img_bytes = renderer.to_bytes(img, fmt="PNG")
        b64 = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"

        # 5. Persist to history
        history_id = None
        if save_to_history:
            history = QRHistory(
                title=title,
                qr_type=qr_type,
                content=json.dumps(data, ensure_ascii=False),
                encoded_data=encoded,
                preview_path=str(file_path),
                file_path=str(file_path),
                category_id=category_id,
                customization_json=json.dumps(customization or {}, ensure_ascii=False),
                download_count=0,
                is_favorite=False,
            )
            db.add(history)
            db.commit()
            db.refresh(history)
            history_id = history.id
            logger.info(f"Saved QR history id={history_id}")

        return {
            "id": history_id,
            "title": title,
            "qr_type": qr_type,
            "content": json.dumps(data, ensure_ascii=False),
            "encoded_data": encoded,
            "preview_base64": b64,
            "file_path": str(file_path) if save_to_history else None,
            "category_id": category_id,
        }

    # ------------------------------------------------------------------ #
    #  Regenerate from history
    # ------------------------------------------------------------------ #
    def regenerate(self, db: Session, history_id: int) -> Dict[str, Any]:
        """Regenerate a QR from an existing history record."""
        record = db.query(QRHistory).filter(QRHistory.id == history_id).first()
        if not record:
            raise ValueError(f"QR history {history_id} not found")

        custom_dict = json.loads(record.customization_json) if record.customization_json else {}
        data = json.loads(record.content) if record.content else {}

        return self.generate(
            db=db,
            title=record.title,
            qr_type=record.qr_type,
            data=data,
            category_id=record.category_id,
            customization=custom_dict,
            save_to_history=True,
        )

    # ------------------------------------------------------------------ #
    #  Download (increment count + return file)
    # ------------------------------------------------------------------ #
    def download(
        self,
        db: Session,
        history_id: int,
        fmt: str = "png",
    ) -> Tuple[bytes, str, str]:
        """Return (file_bytes, filename, media_type) and increment download count."""
        record = db.query(QRHistory).filter(QRHistory.id == history_id).first()
        if not record:
            raise ValueError(f"QR history {history_id} not found")

        # Increment download count
        record.download_count = (record.download_count or 0) + 1
        db.commit()

        custom_dict = json.loads(record.customization_json) if record.customization_json else {}
        custom = self._build_customization(custom_dict)

        fmt = fmt.lower()
        base_name = f"qr_{record.qr_type}_{record.id}"

        if fmt == "svg":
            svg_path = settings.exports_path / f"{base_name}.svg"
            renderer.save_svg(record.encoded_data, custom, svg_path)
            data = svg_path.read_bytes()
            return data, f"{base_name}.svg", "image/svg+xml"

        # Re-render for image formats
        img = renderer.render_image(record.encoded_data, custom)

        if fmt == "jpg":
            path = settings.exports_path / f"{base_name}.jpg"
            renderer.save_jpg(img, path)
            return path.read_bytes(), f"{base_name}.jpg", "image/jpeg"
        elif fmt == "pdf":
            return self._to_pdf(img, base_name)
        else:  # png
            data = renderer.to_bytes(img, fmt="PNG")
            return data, f"{base_name}.png", "image/png"

    def _to_pdf(self, img, base_name: str) -> Tuple[bytes, str, str]:
        """Convert QR image to a simple PDF."""
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
        import io as _io

        buf = _io.BytesIO()
        c = canvas.Canvas(buf)
        img_w, img_h = img.size
        c.setPageSize((img_w, img_h))
        # Flatten for PDF
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        img_reader = ImageReader(bg)
        c.drawImage(img_reader, 0, 0, img_w, img_h)
        c.save()
        return buf.getvalue(), f"{base_name}.pdf", "application/pdf"

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    def _build_customization(self, custom_dict: Optional[Dict[str, Any]]) -> QRCustomization:
        """Build a QRCustomization from a dict, applying defaults."""
        if custom_dict:
            return QRCustomization(**custom_dict)
        return QRCustomization()


# Singleton
qr_service = QRService()