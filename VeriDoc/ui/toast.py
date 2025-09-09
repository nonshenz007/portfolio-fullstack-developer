from typing import Optional

from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PySide6.QtWidgets import QLabel, QWidget


class Toast(QLabel):
    """
    Lightweight toast notification that overlays a parent window.

    Usage:
        Toast(parent, "Saved!", "success").show_at_bottom()
    """

    KIND_TO_STYLE = {
        "info": ("#0ea5e9", "rgba(14,165,233,0.12)", "#0369a1"),
        "success": ("#16a34a", "rgba(22,163,74,0.12)", "#065f46"),
        "warning": ("#d97706", "rgba(217,119,6,0.14)", "#92400e"),
        "error": ("#dc2626", "rgba(220,38,38,0.14)", "#7f1d1d"),
    }

    def __init__(self, parent: Optional[QWidget], message: str, kind: str = "info") -> None:
        super().__init__(parent)
        self.setText(message)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setWordWrap(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("toast")

        # Style based on kind
        color, bg, border = self.KIND_TO_STYLE.get(kind, self.KIND_TO_STYLE["info"])
        self.setStyleSheet(
            f"""
            QLabel#toast {{
                background: {bg};
                color: {color};
                border: 1px solid {color};
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: 600;
            }}
            """
        )

        # Auto-hide timer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)

        self._anim: Optional[QPropertyAnimation] = None

    def show_at_bottom(self, ms: int = 2200) -> None:
        parent = self.parentWidget()
        if parent is None:
            self.show()
            return

        # Place above status bar with margins
        parent_rect = parent.rect()
        width = min(parent_rect.width() - 40, 520)
        height = 44
        x = parent_rect.left() + (parent_rect.width() - width) // 2
        y = parent_rect.bottom() - height - 28
        self.setGeometry(QRect(x, y + 20, width, height))
        self.setWindowFlags(Qt.ToolTip)
        self.setVisible(True)

        # Slide in animation
        self._anim = QPropertyAnimation(self, b"geometry", self)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(QRect(x, y + 20, width, height))
        self._anim.setEndValue(QRect(x, y, width, height))
        self._anim.start()

        self._timer.start(ms)

    def _fade_out(self) -> None:
        if not self.isVisible():
            return
        self._anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim.setDuration(260)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._anim.finished.connect(self.hide)
        self._anim.start()

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont


class Toast(QWidget):
    def __init__(self, parent=None, message: str = "", kind: str = "info", ms: int = 2200):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Arial", 10))
        colors = {
            "info": ("#4ea1ff", "#1e1f22"),
            "success": ("#27ae60", "#1e1f22"),
            "warn": ("#f1c40f", "#1e1f22"),
            "error": ("#e74c3c", "#1e1f22"),
        }
        fg, bg = colors.get(kind, colors["info"])
        self.label.setStyleSheet(f"background:{bg}; color:{fg}; padding:8px 12px; border-radius:8px; border:1px solid {fg}66;")
        self.adjustSize()
        QTimer.singleShot(ms, self.close)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def show_at_bottom(self):
        if not self.parent():
            return self.show()
        pw = self.parent().width()
        ph = self.parent().height()
        w = self.width()
        h = self.height()
        self.move(int((pw - w) / 2), ph - h - 24)
        self.show()
        self.anim.start()


