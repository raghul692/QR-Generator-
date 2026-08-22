"""
QRMaster Pro — Export Service.

Generates reports (CSV, Excel, PDF) of QR history with statistics.
Also handles single-QR exports in various formats.
"""
from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models import QRExport, QRHistory
from app.utils.logger import logger


class ExportService:
    """Service for exporting QR data and reports."""

    def export_history_csv(self, db: Session) -> Tuple[bytes, str]:
        """Export all QR history as CSV."""
        import pandas as pd

        records = db.query(QRHistory).order_by(QRHistory.created_at.desc()).all()
        data = []
        for r in records:
            data.append({
                "ID": r.id,
                "Title": r.title,
                "Type": r.qr_type,
                "Content": r.content[:200] if r.content else "",
                "Downloads": r.download_count,
                "Favorite": r.is_favorite,
                "Created At": r.created_at.isoformat() if r.created_at else "",
            })
        df = pd.DataFrame(data)
        buf = io.BytesIO()
        df.to_csv(buf, index=False, encoding="utf-8-sig")
        self._log_export(db, None, "report", "csv")
        return buf.getvalue(), "qr_history_report.csv"

    def export_history_excel(self, db: Session) -> Tuple[bytes, str]:
        """Export all QR history as Excel."""
        import pandas as pd

        records = db.query(QRHistory).order_by(QRHistory.created_at.desc()).all()
        data = []
        for r in records:
            data.append({
                "ID": r.id,
                "Title": r.title,
                "Type": r.qr_type,
                "Content": r.content[:200] if r.content else "",
                "Downloads": r.download_count,
                "Favorite": r.is_favorite,
                "Created At": r.created_at.isoformat() if r.created_at else "",
            })
        df = pd.DataFrame(data)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="QR History")
        self._log_export(db, None, "report", "excel")
        return buf.getvalue(), "qr_history_report.xlsx"

    def export_history_pdf(self, db: Session) -> Tuple[bytes, str]:
        """Export a PDF report of QR history with statistics."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

        records = db.query(QRHistory).order_by(QRHistory.created_at.desc()).limit(100).all()
        total = db.query(QRHistory).count()
        total_dl = db.query(func.sum(QRHistory.download_count)).scalar() or 0

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                                topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        elements: List[Any] = []

        elements.append(Paragraph("QRMaster Pro — QR History Report", styles["Title"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
            f"Total QR: {total} | Total Downloads: {total_dl}",
            styles["Normal"],
        ))
        elements.append(Spacer(1, 18))

        # Table
        header = ["ID", "Title", "Type", "Downloads", "Favorite", "Created"]
        rows_data = [header]
        for r in records:
            rows_data.append([
                str(r.id),
                r.title[:30],
                r.qr_type,
                str(r.download_count),
                "Yes" if r.is_favorite else "No",
                r.created_at.strftime("%Y-%m-%d") if r.created_at else "",
            ])

        table = Table(rows_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366F1")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ]))
        elements.append(table)

        doc.build(elements)
        self._log_export(db, None, "report", "pdf")
        return buf.getvalue(), "qr_history_report.pdf"

    def export_sticker_sheet_pdf(
        self, db: Session, qr_ids: Optional[List[int]] = None, layout: str = "3x8"
    ) -> Tuple[bytes, str]:
        """Export printable A4 QR sticker sheet layout (3x8 grid = 24 stickers)."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors

        if qr_ids:
            records = db.query(QRHistory).filter(QRHistory.id.in_(qr_ids)).all()
        else:
            records = db.query(QRHistory).order_by(QRHistory.created_at.desc()).limit(24).all()

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20
        )
        styles = getSampleStyleSheet()

        # Build grid cells (3 cols x 8 rows)
        cols = 3
        cell_data: List[List[Any]] = []
        row: List[Any] = []

        for r in records:
            # Load preview image or file image
            img_path = r.file_path or r.preview_path
            if img_path and Path(img_path).exists():
                rl_img = RLImage(img_path, width=110, height=110)
            else:
                rl_img = Paragraph("<b>[QR Image]</b>", styles["Normal"])

            title_p = Paragraph(
                f"<font size=8><b>{r.title[:20]}</b><br/>{r.qr_type.upper()}</font>", styles["Normal"]
            )

            cell = [rl_img, title_p]
            row.append(cell)

            if len(row) == cols:
                cell_data.append(row)
                row = []

        if row:
            while len(row) < cols:
                row.append("")
            cell_data.append(row)

        table = Table(cell_data, colWidths=[180, 180, 180])
        table.setStyle(
            TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
            ])
        )

        doc.build([table])
        self._log_export(db, None, "sticker_sheet", "pdf")
        return buf.getvalue(), "qr_sticker_sheet.pdf"

    def _log_export(self, db: Session, qr_id: Optional[int], export_type: str, fmt: str) -> None:
        """Record an export in the qr_exports table."""
        try:
            exp = QRExport(qr_id=qr_id, export_type=export_type, format=fmt, file_path=None)
            db.add(exp)
            db.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Could not log export: {exc}")
            db.rollback()


# Singleton
export_service = ExportService()