"""
QRMaster Pro — QR Image Renderer.

Takes an encoded string + customization options and produces a styled QR
image (PNG/JPG) or SVG using the `qrcode` + `Pillow` libraries. Supports
colors, gradients, module shapes, logo embedding, borders, and transparency.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Optional, Tuple

import qrcode
from PIL import Image, ImageDraw, ImageFilter
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    CircleModuleDrawer,
    GappedSquareModuleDrawer,
    RoundedModuleDrawer,
    SquareModuleDrawer,
)

from app.qr_engine.customization import (
    ErrorCorrection,
    LogoPosition,
    QRCustomization,
    QRStyle,
)
from app.utils.logger import logger


# Map error correction strings to qrcode constants
_EC_MAP = {
    ErrorCorrection.L: ERROR_CORRECT_L,
    ErrorCorrection.M: ERROR_CORRECT_M,
    ErrorCorrection.Q: ERROR_CORRECT_Q,
    ErrorCorrection.H: ERROR_CORRECT_H,
}

# Map style strings to module drawers
_DRAWER_MAP = {
    QRStyle.SQUARE: SquareModuleDrawer,
    QRStyle.ROUNDED: RoundedModuleDrawer,
    QRStyle.CIRCULAR: CircleModuleDrawer,
    QRStyle.DOTS: GappedSquareModuleDrawer,
}


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert #RRGGBB to (R, G, B) tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _make_gradient(size: int, start: str, end: str) -> Image.Image:
    """Create a vertical gradient image of the given size."""
    top = _hex_to_rgb(start)
    bottom = _hex_to_rgb(end)
    base = Image.new("RGB", (size, size))
    px = base.load()
    for y in range(size):
        ratio = y / max(size - 1, 1)
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        for x in range(size):
            px[x, y] = (r, g, b)
    return base


class QRRenderer:
    """Renders QR codes with full customization support."""

    def render_image(
        self,
        data: str,
        customization: QRCustomization,
    ) -> Image.Image:
        """Render a QR code and return a PIL Image."""
        logger.debug(f"Rendering QR: size={customization.size}, style={customization.qr_style}")

        qr = qrcode.QRCode(
            version=None,
            error_correction=_EC_MAP[customization.error_correction],
            box_size=10,
            border=customization.margin,
        )
        qr.add_data(data)
        qr.make(fit=True)

        drawer_cls = _DRAWER_MAP.get(customization.qr_style, SquareModuleDrawer)

        # Background color (or transparent)
        if customization.transparent_background:
            bg_color = None  # styledpil supports fill_color/bg_color
        else:
            bg_color = _hex_to_rgb(customization.background_color)

        # Foreground: solid or gradient
        if customization.gradient_enabled:
            # Render in black first, then apply gradient mask
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=drawer_cls(),
                fill_color="black",
                back_color=bg_color if bg_color else "white",
            ).get_image()
            img = self._apply_gradient(img, customization)
        else:
            fg = _hex_to_rgb(customization.foreground_color)
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=drawer_cls(),
                fill_color=fg,
                back_color=bg_color if bg_color else "white",
            ).get_image()

        # Convert to RGBA for compositing
        img = img.convert("RGBA")

        # Transparent background
        if customization.transparent_background:
            bg_rgb = _hex_to_rgb(customization.background_color)
            datas = img.getdata()
            new_data = []
            for item in datas:
                # Replace near-white/background pixels with transparent
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            img.putdata(new_data)

        # Logo embedding
        if customization.logo_path and Path(customization.logo_path).exists():
            img = self._embed_logo(img, customization)

        # Decorative border
        if customization.border_thickness > 0:
            img = self._add_border(img, customization)

        # Decorative Frame with callout text
        if customization.frame_style and customization.frame_style != "none":
            img = self._add_frame(img, customization)

        return img

    def _apply_gradient(self, img: Image.Image, c: QRCustomization) -> Image.Image:
        """Apply a gradient to the dark (module) pixels of the QR."""
        img = img.convert("RGBA")
        w, h = img.size
        gradient = _make_gradient(max(w, h), c.gradient_start, c.gradient_end).resize((w, h))
        gradient = gradient.convert("RGBA")

        # Create mask from dark pixels
        gray = img.convert("L")
        mask = gray.point(lambda p: 255 if p < 128 else 0)
        # Composite gradient onto a transparent layer using mask
        gradient_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gradient_layer.paste(gradient, (0, 0), mask)
        # Combine: keep background from original, modules from gradient
        result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        result.paste(img, (0, 0))
        result = Image.alpha_composite(result, gradient_layer)
        return result

    def _embed_logo(self, img: Image.Image, c: QRCustomization) -> Image.Image:
        """Embed a logo onto the QR image at the specified position."""
        try:
            logo = Image.open(c.logo_path).convert("RGBA")
        except Exception as exc:
            logger.warning(f"Could not open logo {c.logo_path}: {exc}")
            return img

        w, h = img.size
        logo_max = int(min(w, h) * (c.logo_size / 100.0))
        # Scale logo maintaining aspect ratio
        logo.thumbnail((logo_max, logo_max), Image.Resampling.LANCZOS)
        lw, lh = logo.size

        # Optional white background behind logo
        if c.logo_background:
            pad = max(8, int(lw * 0.1))
            bg = Image.new("RGBA", (lw + pad * 2, lh + pad * 2), (255, 255, 255, 230))
            bg.paste(logo, (pad, pad), logo)
            logo = bg
            lw, lh = logo.size

        # Position
        positions = {
            LogoPosition.CENTER: ((w - lw) // 2, (h - lh) // 2),
            LogoPosition.TOP_LEFT: (10, 10),
            LogoPosition.TOP_RIGHT: (w - lw - 10, 10),
            LogoPosition.BOTTOM_LEFT: (10, h - lh - 10),
            LogoPosition.BOTTOM_RIGHT: (w - lw - 10, h - lh - 10),
        }
        x, y = positions.get(c.logo_position, positions[LogoPosition.CENTER])
        img.paste(logo, (x, y), logo)
        return img

    def _add_border(self, img: Image.Image, c: QRCustomization) -> Image.Image:
        """Add a decorative border around the QR."""
        border = c.border_thickness
        color = _hex_to_rgb(c.border_color) + (255,)
        w, h = img.size
        new = Image.new("RGBA", (w + border * 2, h + border * 2), color)
        new.paste(img, (border, border), img)
        return new

    def _add_frame(self, img: Image.Image, c: QRCustomization) -> Image.Image:
        """Add decorative frame with text around QR."""
        if not c.frame_style or c.frame_style == "none":
            return img

        w, h = img.size
        header_height = 36 if c.frame_style in ("badge", "banner") else 0
        footer_height = 46
        padding = 16

        frame_w = w + padding * 2
        frame_h = h + padding * 2 + header_height + footer_height

        frame_bg = _hex_to_rgb(c.frame_color) + (255,)
        text_color = _hex_to_rgb(c.frame_text_color) + (255,)

        canvas = Image.new("RGBA", (frame_w, frame_h), frame_bg)
        canvas.paste(img, (padding, padding + header_height), img)

        draw = ImageDraw.Draw(canvas)
        text = (c.frame_text or "SCAN ME").upper()

        footer_y = frame_h - footer_height // 2
        draw.text((frame_w // 2, footer_y), text, fill=text_color, anchor="mm")

        if c.frame_style == "badge":
            draw.text((frame_w // 2, header_height // 2 + 4), "QR MASTER", fill=text_color, anchor="mm")

        return canvas

    # ------------------------------------------------------------------ #
    #  Export helpers
    # ------------------------------------------------------------------ #
    def save_png(self, img: Image.Image, path: Path) -> Path:
        img.save(path, format="PNG", optimize=True)
        return path

    def save_jpg(self, img: Image.Image, path: Path) -> Path:
        # Flatten alpha onto white for JPG
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        bg.save(path, format="JPEG", quality=95)
        return path

    def save_svg(self, data: str, customization: QRCustomization, path: Path) -> Path:
        """Generate an SVG QR (via segno for clean vector output)."""
        import segno

        ec_map = {"L": "l", "M": "m", "Q": "q", "H": "h"}
        q = segno.make(data, error=ec_map.get(customization.error_correction, "h"))
        color = customization.foreground_color
        bg = None if customization.transparent_background else customization.background_color
        q.save(str(path), svgclass="qrmaster-qr", xmldecl=False, svgns=True,
               dark=color, light=bg, border=customization.margin)
        return path

    def to_bytes(self, img: Image.Image, fmt: str = "PNG") -> bytes:
        """Convert image to bytes (for in-memory / base64 responses)."""
        buf = io.BytesIO()
        if fmt.upper() == "JPEG":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
            bg.save(buf, format="JPEG", quality=95)
        else:
            img.save(buf, format=fmt.upper(), optimize=True)
        return buf.getvalue()


# Singleton renderer
renderer = QRRenderer()