"""
UI package bootstrap for VeriDoc.

Adds best-effort runtime enhancements:
- Apply subtle drop shadows to key widgets
- Attach quick image analysis to preview overlay

Safe on failure; no impact on startup.
"""

from typing import Any

try:  # optional
    from .visual_enhance import apply_visual_enhancements, attach_preview_analysis, prewarm_ai_models  # type: ignore
except Exception:  # pragma: no cover
    apply_visual_enhancements = None  # type: ignore
    attach_preview_analysis = None  # type: ignore
    prewarm_ai_models = None  # type: ignore


def _patch_main_window() -> None:  # pragma: no cover
    try:
        from . import main_window as _mw  # type: ignore
        MainWindow = getattr(_mw, "MainWindow", None)
        if MainWindow is None:
            return

        original_init = getattr(MainWindow, "__init__", None)
        if not callable(original_init):
            return

        def _wrapped_init(self: Any, *args: Any, **kwargs: Any) -> None:
            original_init(self, *args, **kwargs)
            try:
                if apply_visual_enhancements:
                    apply_visual_enhancements(self)  # type: ignore[misc]
                if attach_preview_analysis:
                    attach_preview_analysis(self)  # type: ignore[misc]
                # Always prewarm AI (rembg) in the background so first use is instant
                if prewarm_ai_models:
                    prewarm_ai_models()  # type: ignore[misc]
            except Exception:
                pass

        # Avoid double wrapping
        if getattr(original_init, "__name__", "") != "_wrapped_init":
            MainWindow.__init__ = _wrapped_init  # type: ignore[assignment]
    except Exception:
        pass


_patch_main_window()



