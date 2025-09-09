"""
Basic application stylesheet for VeriDoc UI.

Provides a clean, modern dark-on-light theme compatible with
`ui.production_window.ProductionMainWindow`.
"""

from __future__ import annotations


def app_stylesheet() -> str:
    return """
    /* Base */
    QWidget { font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }
    QMainWindow { background: #F8FAFC; }

    /* Buttons */
    QPushButton#primaryBtn {
        background: #3B82F6;
        color: white;
        padding: 10px 16px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }
    QPushButton#primaryBtn:hover { background: #2563EB; }
    QPushButton#primaryBtn:disabled { background: #93C5FD; color: #E5E7EB; }

    QPushButton#secondaryBtn {
        background: #FFFFFF;
        color: #1F2937;
        padding: 8px 14px;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        font-weight: 500;
    }
    QPushButton#secondaryBtn:hover { background: #F3F4F6; }

    /* Cards */
    QFrame#modernCard, QFrame#dropZoneV2 {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
    }

    /* Header */
    QFrame#appHeader {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0F172A, stop:1 #1E293B);
        border-bottom: 1px solid #334155;
    }

    /* Lists */
    QListWidget { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; }
    QListWidget::item { padding: 8px 12px; border-radius: 6px; }
    QListWidget::item:hover { background: #F1F5F9; }
    QListWidget::item:selected { background: #3B82F6; color: #FFFFFF; }
    """

"""
Mathematical Theme System
Perfect styling using golden ratio, Fibonacci sequences, and mathematical constants
"""

# Mathematical constants for perfect design
PHI = 1.618033988749  # Golden Ratio
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

# Modern premium color palette
COLORS = {
    'primary': '#0F172A',
    'primary_light': '#1E293B',
    'secondary': '#3B82F6',
    'secondary_light': '#60A5FA',
    'accent': '#06B6D4',
    'success': '#10B981',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'gray_50': '#F8FAFC',
    'gray_100': '#F1F5F9',
    'gray_200': '#E2E8F0',
    'gray_300': '#CBD5E1',
    'gray_400': '#94A3B8',
    'gray_500': '#64748B',
    'gray_600': '#475569',
    'gray_700': '#334155',
    'gray_800': '#1E293B',
    'gray_900': '#0F172A',
    'white': '#FFFFFF',
    'black': '#000000',
}

def app_stylesheet():
    """Generate the modern premium application stylesheet."""
    
    return f"""
    /* Modern Premium Theme */
    
    QApplication {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
        font-size: 14px;
        color: {COLORS['gray_900']};
    }}
    
    QMainWindow {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {COLORS['gray_50']}, 
            stop:0.5 {COLORS['gray_100']}, 
            stop:1 {COLORS['gray_200']});
        color: {COLORS['gray_900']};
    }}
    
    /* Modern Cards with Glass Morphism */
    QFrame[objectName="modernCard"] {{
        background: rgba(255, 255, 255, 0.96);
        border-radius: 20px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        padding: 0px;
    }}
    
    QFrame[objectName="card"] {{
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        padding: 24px;
    }}
    
    /* Modern Button System */
    QPushButton {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['gray_300']};
        border-radius: 14px;
        color: {COLORS['gray_700']};
        font-weight: 500;
        font-size: 14px;
        padding: 12px 20px;
        min-height: 44px;
    }}
    
    QPushButton:hover {{
        background: {COLORS['gray_50']};
        border-color: {COLORS['gray_400']};
    }}
    
    QPushButton:pressed {{
        background: {COLORS['gray_100']};
    }}
    
    QPushButton:disabled {{
        background: {COLORS['gray_100']};
        color: {COLORS['gray_400']};
        border-color: {COLORS['gray_200']};
    }}
    
    /* Primary Button */
    QPushButton[objectName="primaryBtn"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['secondary']}, 
            stop:1 {COLORS['secondary_light']});
        border: none;
        color: {COLORS['white']};
        font-weight: 600;
        font-size: 15px;
        padding-top: 14px; padding-bottom: 14px;
        border-radius: 16px;
    }}
    
    QPushButton[objectName="primaryBtn"]:hover {{
        background: {COLORS['secondary']};
    }}
    
    /* Secondary Button */
    QPushButton[objectName="secondaryBtn"] {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['gray_300']};
        color: {COLORS['gray_700']};
        font-weight: 500;
        font-size: 14px;
        border-radius: 14px;
    }}
    
    QPushButton[objectName="secondaryBtn"]:hover {{
        background: {COLORS['gray_50']};
        border-color: {COLORS['secondary']};
        color: {COLORS['secondary']};
    }}
    
    QPushButton[objectName="secondaryBtn"]:pressed {{
        background: {COLORS['gray_100']};
    }}
    
    /* Subtle primary ghost button variant */
    QPushButton[objectName="ghostPrimary"] {{
        background: rgba(59,130,246,0.06);
        border: 1px dashed rgba(59,130,246,0.35);
        color: {COLORS['secondary']};
        font-weight: 600;
    }}
    QPushButton[objectName="ghostPrimary"]:hover {{
        background: rgba(59,130,246,0.12);
        border-color: {COLORS['secondary']};
    }}
    
    
    /* Modern ComboBox */
    QComboBox {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['gray_300']};
        border-radius: 12px;
        padding: 12px 16px;
        color: {COLORS['gray_900']};
        min-height: 44px;
        font-size: 14px;
        font-weight: 500;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['secondary']};
        background: {COLORS['gray_50']};
    }}
    
    QComboBox:focus {{
        border-color: {COLORS['secondary']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 40px;
        background: transparent;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {COLORS['gray_500']};
        margin-right: 12px;
    }}
    
    QComboBox QAbstractItemView {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['gray_200']};
        border-radius: 12px;
        padding: 8px;
    }}
    
    QComboBox QAbstractItemView::item {{
        background: transparent;
        padding: 12px 16px;
        border-radius: 8px;
        color: {COLORS['gray_900']};
        min-height: 24px;
    }}
    
    QComboBox QAbstractItemView::item:selected {{
        background: {COLORS['secondary']};
        color: {COLORS['white']};
    }}
    
    QComboBox QAbstractItemView::item:hover {{
        background: {COLORS['gray_100']};
    }}
    
    /* Modern Lists */
    QListWidget {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['gray_200']};
        border-radius: 12px;
        padding: 8px;
        font-size: 14px;
    }}
    
    QListWidget::item {{
        background: transparent;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 2px;
        color: {COLORS['gray_900']};
        min-height: 20px;
    }}
    
    QListWidget::item:selected {{
        background: {COLORS['secondary']};
        color: {COLORS['white']};
    }}
    
    QListWidget::item:hover {{
        background: {COLORS['gray_100']};
    }}
    
    /* Modern Text Areas */
    QTextEdit {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['gray_200']};
        border-radius: 12px;
        padding: 16px;
        font-family: 'Menlo', 'Monaco', 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        color: {COLORS['gray_900']};
        line-height: 1.6;
    }}
    
    QTextEdit:focus {{
        border-color: {COLORS['secondary']};
    }}
    
    /* Modern Progress Bars */
    QProgressBar {{
        background: {COLORS['gray_200']};
        border: none;
        border-radius: 8px;
        height: 16px;
        text-align: center;
        font-size: 12px;
        font-weight: 600;
        color: {COLORS['gray_700']};
    }}
    
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['secondary']}, 
            stop:1 {COLORS['secondary_light']});
        border-radius: 8px;
    }}
    
    /* Modern Scroll Bars */
    QScrollBar:vertical {{
        background: {COLORS['gray_100']};
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background: {COLORS['gray_400']};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['gray_500']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}
    
    /* Modern Group Boxes */
    QGroupBox {{
        font-weight: 600;
        font-size: 16px;
        border: none;
        margin-top: 12px;
        padding-top: 16px;
        color: {COLORS['gray_900']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 8px;
        color: {COLORS['gray_900']};
        font-size: 16px;
        font-weight: 600;
    }}
    
    /* Modern Labels */
    QLabel {{
        color: {COLORS['gray_900']};
        font-size: 14px;
    }}
    
    QLabel[objectName="title"] {{
        font-size: 28px;
        font-weight: 700;
        color: {COLORS['primary']};
    }}
    
    QLabel[objectName="subtitle"] {{
        font-size: 16px;
        font-weight: 400;
        color: {COLORS['gray_600']};
    }}
    
    /* Modern Status Bar */
    QStatusBar {{
        background: rgba(255, 255, 255, 0.95);
        border-top: 1px solid {COLORS['gray_200']};
        color: {COLORS['gray_600']};
        font-size: 13px;
        padding: 8px 16px;
    }}
    
    /* Modern Menu Bar */
    QMenuBar {{
        background: rgba(255, 255, 255, 0.95);
        border-bottom: 1px solid {COLORS['gray_200']};
        color: {COLORS['gray_900']};
        font-size: 14px;
        padding: 4px 0;
    }}
    
    QMenuBar::item {{
        padding: 8px 16px;
        background: transparent;
        border-radius: 8px;
        margin: 0 4px;
    }}
    
    QMenuBar::item:selected {{
        background: {COLORS['gray_100']};
        color: {COLORS['secondary']};
    }}
    
    /* Modern Premium Tabs */
    QTabWidget::pane {{
        border: none;
        background: transparent;
        margin-top: 0px;
    }}
    
    QTabWidget::tab-bar {{
        alignment: left;
    }}
    
    QTabBar {{
        background: rgba(255, 255, 255, 0.9);
        border-bottom: 1px solid {COLORS['gray_200']};
        margin: 0px 24px;
        border-radius: 12px 12px 0 0;
    }}
    
    QTabBar::tab {{
        background: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        padding: 20px 32px;
        margin: 0px 4px;
        font-size: 16px;
        font-weight: 700;
        color: {COLORS['gray_500']};
        min-width: 140px;
        border-radius: 8px 8px 0 0;
    }}
    
    QTabBar::tab:selected {{
        color: {COLORS['secondary']};
        border-bottom: 3px solid {COLORS['secondary']};
        background: rgba(59, 130, 246, 0.08);
        font-weight: 800;
    }}
    
    QTabBar::tab:hover:!selected {{
        color: {COLORS['secondary']};
        background: rgba(59, 130, 246, 0.04);
    }}
    
    QTabBar::tab:first {{
        margin-left: 16px;
    }}
    
    QTabBar::tab:last {{
        margin-right: 16px;
    }}
    
    /* Legacy drop zone (kept for older widgets) */
    QFrame[objectName="dropZone"] {{
        /* Use a flat background to avoid faint artifact lines on some platforms */
        background: rgba(248, 250, 252, 0.95);
        border: 2px dashed {COLORS['gray_300']};
        border-radius: 16px;
        min-height: 200px;
    }}

    /* New drop zone v2: clean card, no dashed border */
    QFrame[objectName="dropZoneV2"] {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(255,255,255,0.96), stop:1 rgba(239,246,255,0.96));
        border: none;
        border-radius: 16px;
        min-height: 220px;
    }}
    QFrame[objectName="dropZoneV2"]:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(245,249,255,0.98), stop:1 rgba(226,240,255,0.98));
    }}
    QFrame[objectName="dropZoneV2"][dragHover="true"] {{
        background: rgba(59,130,246,0.08);
        border: 2px solid {COLORS['secondary']};
    }}
    
    QFrame[objectName="dropZone"]:hover {{
        background: rgba(239, 246, 255, 0.95);
        border-color: {COLORS['secondary']};
        border-style: solid;
    }}
    
    QFrame[objectName="dropZone"][dragHover="true"] {{
        background: rgba(219, 234, 254, 0.95);
        border-color: {COLORS['secondary']};
        border-style: solid;
        border-width: 3px;
    }}
    
    /* Image Preview canvas */
    QLabel#imageLabel {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #ffffff,
            stop:1 #f7fafc);
        border: 2px solid rgba(226, 232, 240, 0.9);
        border-radius: 16px;
        padding: 6px;
        min-height: 400px;
    }}
    
    QLabel#overlayLabel {{
        background: rgba(59, 130, 246, 0.08);
        color: {COLORS['secondary']};
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 8px;
        padding: 8px 12px;
        font-weight: 600;
    }}
    
    /* Modern Sidebar */
    QWidget[objectName="sidebar"] {{
        background: rgba(255, 255, 255, 0.8);
        border-right: 1px solid {COLORS['gray_200']};
    }}
    
    /* Modern Left Panel */
    QWidget[objectName="leftPanel"] {{
        background: rgba(255, 255, 255, 0.9);
        border-right: 1px solid {COLORS['gray_200']};
        min-width: 380px;
        max-width: 380px;
    }}
    
    /* Input Fields */
    QLineEdit {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['gray_300']};
        border-radius: 12px;
        padding: 12px 16px;
        color: {COLORS['gray_900']};
        font-size: 14px;
        min-height: 20px;
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['secondary']};
    }}
    
    QLineEdit:hover {{
        border-color: {COLORS['gray_400']};
    }}
    
    /* Checkboxes */
    QCheckBox {{
        spacing: 8px;
        color: {COLORS['gray_900']};
        font-size: 14px;
        font-weight: 500;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {COLORS['gray_300']};
        background: {COLORS['white']};
    }}
    
    QCheckBox::indicator:checked {{
        background: {COLORS['secondary']};
        border-color: {COLORS['secondary']};
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0IDdsNy03IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS['secondary']};
    }}
    
    /* Sliders */
    QSlider::groove:horizontal {{
        background: {COLORS['gray_200']};
        height: 6px;
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background: {COLORS['secondary']};
        border: 2px solid {COLORS['white']};
        width: 20px;
        height: 20px;
        border-radius: 10px;
        margin: -7px 0;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {COLORS['secondary_light']};
    }}
    """

def get_perfect_dimensions():
    """Get perfect dimensions based on golden ratio."""
    return {
        'sidebar_width': 380,
        'button_height': 44,
        'card_padding': 24,
        'spacing': 20,
        'border_radius': 12,
        'font_size_small': 12,
        'font_size_normal': 14,
        'font_size_large': 16,
        'font_size_title': 28,
    }

def get_perfect_colors():
    """Get the perfect color palette."""
    return COLORS.copy()