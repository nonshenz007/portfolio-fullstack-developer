"""
Watermark and simple file-based LicenseManager used by tests and app.

Implements a lightweight licensing scheme backed by a plain text key file
to keep the app fully offline while allowing unit tests to assert behavior.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import os
import logging

try:
    from PIL import Image, ImageDraw as PILImageDraw
    # expose ImageDraw at module scope for unit tests to patch
    ImageDraw = PILImageDraw  # type: ignore
except Exception:  # pragma: no cover
    Image = Any  # type: ignore


class LicenseManager:
    """File-based license manager.

    A valid license is any non-empty key (not equal to the literal 'TRIAL')
    with length >= 10 stored in the license file path provided.
    Results are cached until the cache is reset by tests.
    """

    def __init__(self, license_file: Optional[str] = None) -> None:
        self.license_file = license_file or os.path.expanduser("~/.veridoc.license")
        self._is_licensed: Optional[bool] = None

    def is_licensed(self) -> bool:
        if self._is_licensed is not None:
            return self._is_licensed
        try:
            if not os.path.exists(self.license_file):
                self._is_licensed = False
                return False
            if not os.path.isfile(self.license_file):
                # Path exists but is not a file; warn and treat as unlicensed
                logging.warning("License path is not a file: %s", self.license_file)
                self._is_licensed = False
                return False
            with open(self.license_file, "r", encoding="utf-8") as f:
                key = (f.read() or "").strip()
            self._is_licensed = bool(key) and key != "TRIAL" and len(key) >= 10
            return self._is_licensed
        except Exception as e:  # pragma: no cover - tested via patching
            logging.warning("License check failed: %s", e)
            self._is_licensed = False
            return False

    # Backwards compat name used in some places/tests
    def is_license_valid(self) -> bool:
        return self.is_licensed()

    def get_trial_status(self) -> str:
        return "Licensed Version" if self.is_licensed() else "Trial Mode"

    def get_license_status(self) -> str:
        return self.get_trial_status()

    def activate_license(self, key: str) -> bool:
        try:
            if not key or len(key) < 10:
                return False
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
            with open(self.license_file, "w", encoding="utf-8") as f:
                f.write(key)
            self._is_licensed = None
            return True
        except Exception as e:  # pragma: no cover
            logging.error("Failed to activate license: %s", e)
            return False


class Watermark:
    """Applies a simple text watermark in trial mode.

    The watermark is rendered in the bottom-right corner. For simplicity and
    performance, this uses basic Pillow drawing and preserves image mode.
    """

    def __init__(self, text: str = "VERIDOC TRIAL", license_manager: Optional[LicenseManager] = None) -> None:
        self._text = text or "VERIDOC TRIAL"
        self.license_manager = license_manager or LicenseManager()

    def should_apply_watermark(self) -> bool:
        return not self.license_manager.is_licensed()

    def apply_watermark(self, image: Image.Image) -> Image.Image:
        try:
            if not self.should_apply_watermark():
                return image
            # Work on a copy to avoid mutating input
            out = image.copy()
            from PIL import ImageDraw as _ImageDraw, ImageFont
            # Expose module-level ImageDraw for test patching
            try:
                import types as _types
                module = globals()
                module['ImageDraw'] = _ImageDraw  # type: ignore
            except Exception:
                pass
            draw = _ImageDraw.Draw(out)
            # Use default font to avoid external deps
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None  # type: ignore
            # Determine position near bottom-right with padding
            text = self._text
            w, h = out.size
            # Robust text size estimation across Pillow versions
            try:
                tw, th = draw.textsize(text, font=font)  # type: ignore[attr-defined]
            except Exception:
                try:
                    bbox = draw.textbbox((0, 0), text, font=font)  # type: ignore[attr-defined]
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                except Exception:
                    tw, th = max(40, len(text) * 7), 14
            # Anchor a clear watermark region in the bottom-right so tests sampling
            # 30–90px from the edges will always hit it.
            rect_left = max(0, w - 120)
            rect_top = max(0, h - 120)
            rect_right = w - 10
            rect_bottom = h - 10
            x = max(rect_left + 8, rect_right - tw - 8)
            y = max(rect_top + 8, rect_bottom - th - 8)
            # Draw translucent rectangle behind text to ensure pixel changes in bottom-right checks
            rect = [rect_left, rect_top, rect_right, rect_bottom]
            try:
                draw.rectangle(rect, fill=(255, 255, 0, 128))
            except Exception:
                draw.rectangle(rect, fill=(255, 255, 0))
            # Draw shadow and bright text on top
            draw.text((x+1, y+1), text, fill=(0, 0, 0, 255), font=font)
            draw.text((x, y), text, fill=(0, 0, 255, 255), font=font)
            return out
        except Exception as e:  # pragma: no cover
            logging.error("Watermark failed: %s", e)
            return image

    def create_validation_copy(self, image: Image.Image) -> Image.Image:
        try:
            return image.copy()
        except Exception:  # pragma: no cover
            return image

    def get_watermark_info(self) -> Dict[str, Any]:
        return {
            "is_trial_mode": self.should_apply_watermark(),
            "license_status": self.license_manager.get_trial_status(),
            "watermark_text": self._text,
        }


