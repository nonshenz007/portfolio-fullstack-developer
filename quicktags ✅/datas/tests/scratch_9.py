# MUST be first imports before anything else
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Set High DPI scaling BEFORE any other Qt code
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# Then proceed with other imports
import sys
import ctypes
import multiprocessing
import subprocess
import platform
import logging
import os
import random
import datetime
import sqlite3
import hashlib
from typing import Dict

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, QDialog,
    QPushButton, QMessageBox, QLineEdit, QFileDialog, QLabel,
    QComboBox, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QStatusBar, QSpinBox, QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt, QSizeF, QRect
from PyQt5.QtGui import QFont, QImage, QPainter, QPixmap
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PIL import Image, ImageDraw, ImageFont
from barcode import get_barcode_class
from barcode.writer import ImageWriter



# Then proceed with other imports



# ------------------------------
# Application Launcher
# ------------------------------ 
def main():
    # Create QApplication instance first
    app = QApplication(sys.argv)

    # Now safe to show Qt dialogs
    global output_dir
    output_dir = load_output_dir()
    
    # Setup output folders after QApplication is created
    setup_output_folders(output_dir)
    
    multiprocessing.freeze_support()  # For PyInstaller support on Windows
    
    if is_already_running():
        print("Another instance is already running. Exiting.")
        sys.exit(1)
    
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app.setStyle('Fusion')  # Modern style
    
    # Set application font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # Show login dialog
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        window = BarcodeGeneratorUI(login.user, login.role)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

# ------------------------------
# Utility Functions
# ------------------------------
def get_system_font_path():
    """Get a system font that's likely to exist."""
    system = platform.system()
    if system == "Windows":
        return "C:\\Windows\\Fonts\\arial.ttf"
    elif system == "Darwin":  # macOS
        return "/System/Library/Fonts/Helvetica.ttc"
    else:  # Linux and others
        # Try some common locations
        for path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]:
            if os.path.exists(path):
                return path
    return None

# ------------------------------
# Single Instance Check (Windows Only)
# ------------------------------
def is_already_running():
    if platform.system() != "Windows":
        return False
    mutex = ctypes.windll.kernel32.CreateMutexW(None, 1, "Global\\ProjectsByShenzC_FullSafeApp")
    return ctypes.GetLastError() == 183

# ------------------------------
# App Data Directory and Global Paths
# ------------------------------
def get_app_data_path():
    base_path = os.path.join(os.environ["APPDATA"], "BarcodeGenerator") if platform.system() == "Windows" else \
                os.path.join(os.path.expanduser("~"), "Library", "Application Support", "BarcodeGenerator") if platform.system() == "Darwin" else \
                os.path.join(os.path.expanduser("~"), ".BarcodeGenerator")
    os.makedirs(base_path, exist_ok=True)
    return base_path

# Default paths
DB_PATH = os.path.join(get_app_data_path(), "barcodes.db")
LOG_PATH = os.path.join(get_app_data_path(), "barcode_app.log")
CONFIG_PATH = os.path.join(get_app_data_path(), "config.ini")

# Load custom output directory from config if it exists
def load_output_dir():
    """Load or prompt for output directory on first run."""
    if not os.path.exists(CONFIG_PATH):
        default_dir = QFileDialog.getExistingDirectory(None, "Select Output Directory")
        if not default_dir:
            logger.error("No output directory selected. Exiting.")
            sys.exit(1)
        
        with open(CONFIG_PATH, 'w') as f:
            f.write(default_dir)
        return default_dir
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            config_dir = f.read().strip()
            if os.path.exists(config_dir):
                return config_dir
            
            new_dir = QFileDialog.getExistingDirectory(
                None, 
                "Previous directory not found. Select new directory:"
            )
            if new_dir:
                with open(CONFIG_PATH, 'w') as f:
                    f.write(new_dir)
                return new_dir
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return QFileDialog.getExistingDirectory(None, "Select Output Directory")


output_dir = None
 
def get_today_folder(base_path: str) -> str:
    """Get today's folder path with proper date formatting"""
    today = datetime.datetime.now().strftime("%d-%m-%y")
    today_path = os.path.join(base_path, today)
    os.makedirs(today_path, exist_ok=True)
    return today_path

def setup_output_folders(base_path: str) -> Dict[str, str]:
    """Setup output folders with proper date-based structure"""
    today = datetime.datetime.now().strftime("%d-%m-%y")
    today_path = get_today_folder(base_path)
    folders = {
        "pdf": os.path.join(today_path, "PDF"),
        "png": os.path.join(today_path, "PNG"),
        "bmp": os.path.join(today_path, "BMP"),
        "excel": os.path.join(today_path, "Excel")
    }
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
    return folders
# Function to update output directory
def update_output_dir(new_dir):
    """Update the global output directory and save to config."""
    global output_dir
    output_dir = new_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to config file
    try:
        with open(CONFIG_PATH, 'w') as f:
            f.write(output_dir)
        logger.info(f"Output directory changed to: {output_dir}")
    except Exception as e:
        logger.error(f"Error saving config: {e}")
    
    return output_dir
# ------------------------------
# Logging Setup
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

TITLE = "Projects \U0001F4C8 by Shenz C (v1.2.5)"

LABEL_SIZES = {
    "Small (60x25 mm)": (60, 25),
    "Medium (100x25 mm)": (100, 25),
    "Large (150x50 mm)": (150, 50),
    "A4 Sheet (210x297 mm)": (210, 297),
    "2 Labels (50 * 25mm)": (100, 25),
    "Custom Size": None
}
# ------------------------------
# Label Rendering Constants and Utilities
# ------------------------------
FONT_CONFIG = {
    "default_font": "Arial",
    "pil": {
        "title_size": 22,
        "normal_size": 16,
        "small_size": 12
    },
    "qt": {
        "title_size": 12,
        "normal_size": 10,
        "small_size": 8
    }
}

SPACING_CONFIG = {
    "padding_top": 10,
    "spacing": 10,
    "margin": 15
}

def calculate_font_size(base_size, dpi=203):
    """Calculate font size based on DPI"""
    return int(base_size * (dpi / 203))  # 203 DPI is our reference

def calculate_barcode_dimensions(width, height):
    """Calculate consistent barcode dimensions"""
    return {
        "width": int(width * 0.7),  # 70% of label width
        "height": int(height * 0.4)  # 40% of label height
    }

def calculate_text_positions(width, height, barcode_height):
    """Calculate standardized text positions"""
    return {
        "title": {
            "y": SPACING_CONFIG["padding_top"],
            "height": 30
        },
        "barcode": {
            "y": SPACING_CONFIG["padding_top"] + 40,
            "height": barcode_height
        },
        "bottom": {
            "y": height - SPACING_CONFIG["margin"] - 25
        }
    }

# ------------------------------
# Database Manager
# ------------------------------
class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.create_tables()
            logger.info("Database connected and tables created/verified.")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            if self.conn:
                self.conn.close()
            raise

    def create_tables(self):
        try:
            c = self.conn.cursor()
            # Barcode history with stock_count
            c.execute('''
                CREATE TABLE IF NOT EXISTS barcode_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT,
                    barcode TEXT,
                    sale_price REAL,
                    purchase_price REAL,
                    company_name TEXT,
                    generation_date TEXT,
                    username TEXT DEFAULT 'admin',
                    stock_count INTEGER DEFAULT 0
                )
            ''')
            # Barcodes table with stock
            c.execute('''
                CREATE TABLE IF NOT EXISTS barcodes (
                    barcode TEXT PRIMARY KEY,
                    item_name TEXT,
                    sale_price REAL,
                    purchase_price REAL,
                    company_name TEXT,
                    quantity INTEGER,
                    stock INTEGER DEFAULT 0
                )
            ''')
            # Users table
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    role TEXT
                )
            ''')
            # Insert default admin if none exist.
            c.execute('SELECT COUNT(*) FROM users')
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                          ("admin", "Kungfukenny", "admin"))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def validate_numeric_inputs(self, *values):
        """Validate all numeric inputs before database operations"""
        try:
            for value in values:
                if value is not None:
                    float(value)  # Will raise ValueError if not numeric
            return True
        except ValueError:
            logger.error("Invalid numeric input detected")
            return False
            
    def add_barcode_history(self, username, item_name, barcode, sale_price, purchase_price, company_name,
                            generation_date, stock_count):
        """Add barcode history with proper error handling and input validation"""
        try:
            # Validate inputs
            if not all([username, item_name, barcode]):
                raise ValueError("Missing required fields")
                
            # Validate numeric inputs
            if not self.validate_numeric_inputs(sale_price, purchase_price, stock_count):
                raise ValueError("Invalid numeric input")
                
            # Calculate sale price if not provided
            if not sale_price and purchase_price:
                profit_percentage = 25  # Default 25% profit
                sale_price = purchase_price * (1 + profit_percentage / 100)
                
            c = self.conn.cursor()
            c.execute('''
                INSERT INTO barcode_history
                (username, item_name, barcode, sale_price, purchase_price, company_name, generation_date, stock_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, item_name, barcode, sale_price, purchase_price, company_name, generation_date, stock_count))
            self.conn.commit()
            logger.info("Barcode history added with calculated sale price.")
        except Exception as e:
            logger.error(f"Failed to add barcode history: {e}")
            raise

    def add_or_update_barcode(self, item_name, barcode, sale_price, purchase_price, company_name, quantity, stock):
        try:
            # Validate numeric inputs
            if not self.validate_numeric_inputs(sale_price, purchase_price, quantity, stock):
                raise ValueError("Invalid numeric input")
                
            # Calculate sale price if not provided
            if not sale_price and purchase_price:
                profit_percentage = 25  # Default 25% profit
                sale_price = purchase_price * (1 + profit_percentage / 100)

            c = self.conn.cursor()
            c.execute('SELECT quantity FROM barcodes WHERE barcode=?', (barcode,))
            result = c.fetchone()
            if result:
                new_quantity = result[0] + quantity
                c.execute('''
                    UPDATE barcodes
                    SET item_name=?, sale_price=?, purchase_price=?, company_name=?, quantity=?, stock=?
                    WHERE barcode=?
                ''', (item_name, sale_price, purchase_price, company_name, new_quantity, stock, barcode))
            else:
                c.execute('''
                    INSERT INTO barcodes
                    (barcode, item_name, sale_price, purchase_price, company_name, quantity, stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (barcode, item_name, sale_price, purchase_price, company_name, quantity, stock))
            self.conn.commit()
            logger.info("Barcode updated/added in database with calculated sale price.")
        except Exception as e:
            logger.error(f"Failed to add/update barcode: {e}")
            raise

    def fetch_history(self, search_text=""):
        try:
            c = self.conn.cursor()
            if search_text:
                search_pattern = f"%{search_text}%"
                c.execute('''
                    SELECT id, username, item_name, barcode, sale_price, purchase_price, company_name, generation_date, stock_count
                    FROM barcode_history
                    WHERE item_name LIKE ? OR barcode LIKE ? OR company_name LIKE ?
                    ORDER BY generation_date DESC
                ''', (search_pattern, search_pattern, search_pattern))
            else:
                c.execute('''
                    SELECT id, username, item_name, barcode, sale_price, purchase_price, company_name, generation_date, stock_count
                    FROM barcode_history
                    ORDER BY generation_date DESC
                ''')
            return c.fetchall()
        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            return []

    def clear_history(self):
        try:
            c = self.conn.cursor()
            c.execute('DELETE FROM barcode_history')
            self.conn.commit()
            logger.info("Barcode history cleared.")
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            raise

    def verify_user(self, username, password):
        try:
            c = self.conn.cursor()
            c.execute('SELECT role FROM users WHERE username=? AND password=?', (username, password))
            result = c.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"User verification failed: {e}")
            return None

    def add_user(self, username, password, role):
        try:
            c = self.conn.cursor()
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                      (username, password, role))
            self.conn.commit()
            logger.info(f"User {username} added with role {role}.")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"User {username} already exists.")
            return False
        except Exception as e:
            logger.error(f"Failed to add user: {e}")
            return False

    def delete_user(self, username):
        try:
            c = self.conn.cursor()
            c.execute('DELETE FROM users WHERE username=?', (username,))
            self.conn.commit()
            logger.info(f"User {username} deleted.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False

    def get_all_users(self):
        try:
            c = self.conn.cursor()
            c.execute('SELECT username, role FROM users')
            return c.fetchall()
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []
    

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
                logger.info("Database connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
# ------------------------------
# Unified Label Rendering Function
# ------------------------------
def render_dual_labels(canvas, item_name, barcode, barcode_path, sale_price, company_name):
    """Render two identical labels side by side on a single canvas."""
    width = 800  # Total width for dual labels
    height = 200  # Standard height
    
    # Render first label
    render_label(canvas, "pil", item_name, barcode, barcode_path, 
                sale_price, company_name, 400, height, 0, 0)
    
    # Render second label
    render_label(canvas, "pil", item_name, barcode, barcode_path, 
                sale_price, company_name, 400, height, 400, 0)

def render_label(canvas, mode, item_name, barcode, barcode_path, sale_price, company_name, width, height, x_offset=0, y_offset=0):
    """Unified label rendering engine for consistent output."""
    try:
        if mode == "pil":
            draw = ImageDraw.Draw(canvas._image)
            font_path = get_system_font_path()
            title_font = ImageFont.truetype(font_path, calculate_font_size(24)) if font_path else ImageFont.load_default()
            normal_font = ImageFont.truetype(font_path, calculate_font_size(16)) if font_path else ImageFont.load_default()
            
            # Item name centered at top (bold)
            draw.text(
                (width // 2 + x_offset, SPACING_CONFIG["padding_top"] + y_offset),
                item_name,
                fill="black",
                font=title_font,
                anchor="mt"
            )

            # Barcode image (70% width, 40% height)
            with Image.open(barcode_path) as barcode_img:
                barcode_height = int(height * 0.4)
                barcode_width = int(width * 0.7)
                
                barcode_img = barcode_img.resize(
                    (barcode_width, barcode_height),
                    Image.LANCZOS
                )
                
                # Center the barcode
                barcode_x = (width - barcode_width) // 2 + x_offset
                barcode_y = height // 2 - barcode_height // 2 + y_offset
                
                canvas._image.paste(barcode_img, (barcode_x, barcode_y))
            
            # Barcode number centered below barcode
            draw.text(
                (width // 2 + x_offset, barcode_y + barcode_height + 5),
                barcode,
                fill="black",
                font=normal_font,
                anchor="mt"
            )

            # Sale price (bottom left) with ₹ symbol
            draw.text(
                (SPACING_CONFIG["margin"] + x_offset, height - SPACING_CONFIG["margin"] + y_offset),
                f"₹{sale_price:.2f}",
                fill="black",
                font=normal_font,
                anchor="ls"
            )

            # Company name (bottom right)
            draw.text(
                (width - SPACING_CONFIG["margin"] + x_offset, height - SPACING_CONFIG["margin"] + y_offset),
                company_name,
                fill="black",
                font=normal_font,
                anchor="rs"
            )
            
            return True
            
        else:
            raise ValueError("Only PIL mode is supported for thermal printing")
            
    except Exception as e:
        logger.error(f"Label rendering failed: {e}")
        raise

# ... existing code ...


def render_pil_label(canvas, item_name, barcode, barcode_path, sale_price, company_name,
                      width, height, dimensions, positions, x_offset, y_offset):
    """Render label using PIL with proper error handling and positioning"""
    try:
        draw = ImageDraw.Draw(canvas._image)
        title_font, normal_font, small_font = _load_pil_fonts()

        # --- Item Name at Top Center ---
        title_y = SPACING_CONFIG["padding_top"] + y_offset
        draw.text(
            (width // 2, title_y),
            item_name,
            fill="black",
            font=title_font,
            anchor="ma"
        )

        # --- Barcode Image in Middle ---
        barcode_y = title_y + 30
        if os.path.exists(barcode_path):
            with Image.open(barcode_path) as barcode_img:
                img_ratio = barcode_img.width / barcode_img.height
                barcode_width = int(dimensions["height"] * img_ratio)
                barcode_img_resized = barcode_img.resize(
                    (barcode_width, dimensions["height"]),
                    Image.LANCZOS
                )
                barcode_x = width // 2 - barcode_img_resized.width // 2 + x_offset
                canvas._image.paste(barcode_img_resized, (barcode_x, barcode_y))

        # --- Barcode Number Centered Below Barcode ---
        barcode_text_y = barcode_y + dimensions["height"] + 2  # slight up
        draw.text(
            (width // 2, barcode_text_y),
            barcode,
            fill="black",
            font=normal_font,
            anchor="ma"
        )

        # --- Sale Price (Left) and Company (Center Bottom) ---
        bottom_y = height - 35 + y_offset

        sale_text = f"Sale Price: ₹{sale_price:.2f}"
        company_text = company_name.upper()

        # Sale price aligned left
        draw.text(
            (SPACING_CONFIG["margin"], bottom_y),
            sale_text,
            fill="black",
            font=small_font,
            anchor="ls"
        )

        # Company name aligned right
        draw.text(
            (width - SPACING_CONFIG["margin"], bottom_y),
            company_text,
            fill="black",
            font=small_font,
            anchor="rs"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to render PIL label: {e}")
        return False

    
def _load_pil_fonts():
    """Load PIL fonts with fallback to default"""
    font_path = get_system_font_path()
    try:
        if not font_path:
            raise ValueError("No system font found")
        title_font = ImageFont.truetype(font_path, FONT_CONFIG["pil"]["title_size"])
        normal_font = ImageFont.truetype(font_path, FONT_CONFIG["pil"]["normal_size"])
        small_font = ImageFont.truetype(font_path, FONT_CONFIG["pil"]["small_size"])
        return title_font, normal_font, small_font
    except Exception as e:
        logger.warning(f"Failed to load custom fonts: {e}, using default")
        default_font = ImageFont.load_default()
        return default_font, default_font, default_font

def draw_pil_barcode(draw, canvas, barcode, barcode_path, font, width, dimensions, y_offset, x_offset, spacing):
    """Draw barcode image and number for PIL mode"""
    if not os.path.exists(barcode_path):
        draw.text((width // 2, y_offset), "[Barcode Missing]", font=font, anchor="mm", fill="red")
        return False
        
    try:
        with Image.open(barcode_path) as barcode_img:
            img_ratio = barcode_img.width / barcode_img.height
            barcode_width = int(dimensions["height"] * img_ratio)
            barcode_img_resized = barcode_img.resize(
                (barcode_width, dimensions["height"]), 
                Image.LANCZOS
            )
            
            barcode_x = width // 2 - barcode_width // 2 + x_offset
            canvas._image.paste(barcode_img_resized, (barcode_x, y_offset))
            
            # Draw barcode number
            barcode_text_y = y_offset + dimensions["height"] + spacing
            barcode_bbox = draw.textbbox((0, 0), barcode, font=font)
            barcode_text_w = barcode_bbox[2] - barcode_bbox[0]
            barcode_text_x = width // 2 - barcode_text_w // 2 + x_offset
            draw.text((barcode_text_x, barcode_text_y), barcode, fill="black", font=font)
            return True
    except Exception as e:
        logger.error(f"Failed to process barcode image: {e}")
        draw.text((width // 2, y_offset), "[Barcode Error]", font=font, anchor="mm", fill="red")
        return False

def draw_pil_bottom_info(draw, sale_price, company_name, font, width, y_offset, x_offset):
    """Draw bottom price and company info for PIL mode"""
    price_text = f"Sale: {sale_price}"
    draw.text((x_offset + SPACING_CONFIG["margin"], y_offset), price_text, fill="black", font=font)
    
    company_bbox = draw.textbbox((0, 0), company_name, font=font)
    company_w = company_bbox[2] - company_bbox[0]
    company_x = width - company_w - SPACING_CONFIG["margin"] + x_offset
    draw.text((company_x, y_offset), company_name, fill="black", font=font)

def render_qt_label(canvas, item_name, barcode, barcode_path, sale_price, company_name,
                    width, height, dimensions, positions, x_offset, y_offset):
    """Helper function for Qt mode rendering"""
    # Setup fonts
    fonts = _setup_qt_fonts()
    title_font, normal_font, small_font = fonts
    
    # Draw item name
    _draw_qt_item_name(canvas, item_name, title_font, width, positions, x_offset, y_offset)
    
    # Draw barcode
    barcode_y = positions["barcode"]["y"] + y_offset
    if not _draw_qt_barcode(canvas, barcode, barcode_path, normal_font, width, height,
                          dimensions, barcode_y, x_offset, SPACING_CONFIG["spacing"]):
        return
    
    # Draw bottom info
    _draw_qt_bottom_info(canvas, sale_price, company_name, small_font, width,
                        positions["bottom"]["y"] + y_offset, x_offset)

def _setup_qt_fonts():
    """Setup Qt fonts with configured sizes"""
    title_font = QFont(FONT_CONFIG["default_font"], FONT_CONFIG["qt"]["title_size"])
    title_font.setBold(True)
    normal_font = QFont(FONT_CONFIG["default_font"], FONT_CONFIG["qt"]["normal_size"])
    small_font = QFont(FONT_CONFIG["default_font"], FONT_CONFIG["qt"]["small_size"])
    return title_font, normal_font, small_font

def _draw_qt_item_name(canvas, item_name, font, width, positions, x_offset, y_offset):
    """Draw item name for Qt mode"""
    canvas.setFont(font)
    canvas.drawText(
        QRect(x_offset, y_offset + positions["title"]["y"], width, positions["title"]["height"]),
        Qt.AlignHCenter | Qt.AlignTop,
        item_name
    )

def _draw_qt_barcode(canvas, barcode, barcode_path, font, width, height, dimensions,
                    y_offset, x_offset, spacing):
    """Draw barcode image and number for Qt mode"""
    if not os.path.exists(barcode_path):
        canvas.setFont(font)
        canvas.drawText(
            QRect(x_offset, y_offset + height//2, width, 30),
            Qt.AlignHCenter | Qt.AlignVCenter,
            "[Barcode Missing]"
        )
        return False
        
    try:
        barcode_pixmap = QPixmap(barcode_path)
        if barcode_pixmap.isNull():
            raise Exception("Failed to load barcode image")
        
        # Resize and center barcode
        barcode_pixmap = barcode_pixmap.scaled(
            dimensions["width"], 
            dimensions["height"],
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        paste_x = x_offset + width//2 - barcode_pixmap.width()//2
        canvas.drawPixmap(paste_x, y_offset, barcode_pixmap)
        
        # Draw barcode number
        canvas.setFont(font)
        barcode_num_y = y_offset + barcode_pixmap.height() + spacing
        canvas.drawText(
            QRect(x_offset, barcode_num_y, width, dimensions["height"]),
            Qt.AlignHCenter | Qt.AlignTop,
            barcode
        )
        return True
    except Exception as e:
        logger.error(f"Failed to load or render barcode image: {e}")
        canvas.setFont(font)
        canvas.drawText(
            QRect(x_offset, y_offset + height//2, width, 30),
            Qt.AlignHCenter | Qt.AlignVCenter,
            "[Barcode Error]"
        )
        return False

def _draw_qt_bottom_info(canvas, sale_price, company_name, font, width, y_offset, x_offset):
    """Draw bottom price and company info for Qt mode"""
    canvas.setFont(font)
    price_text = f"Sale: {sale_price}"
    canvas.drawText(
        x_offset + SPACING_CONFIG["margin"],
        y_offset,
        price_text
    )
    
    company_x = x_offset + width - canvas.fontMetrics().width(company_name) - SPACING_CONFIG["margin"]
    canvas.drawText(
        company_x,
        y_offset,
        company_name
    )


# ------------------------------
# Barcode Generation Functions
# ------------------------------


def generate_label_pdf(pdf_path, width_mm, height_mm, barcode_path, details, dpi=203):
    """
    Generate a PDF with the label(s).
    
    Args:
        pdf_path (str): Path where the PDF will be saved
        width_mm (float): Label width in millimeters
        height_mm (float): Label height in millimeters
        barcode_path (str): Path to the barcode image
        details (dict): Dictionary containing label details (item, barcode, company, sale)
        dpi (int): Resolution for the PDF generation (default: 203)
    
    Returns:
        str: Path to generated PDF if successful, None otherwise
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Create output directory for today
        today = datetime.datetime.now().strftime("%d-%m-%y")
        pdf_dir = os.path.join(output_dir, today, "PDF")
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Update pdf_path to use the new directory
        pdf_path = os.path.join(pdf_dir, os.path.basename(pdf_path))
        
        # Convert mm to points (1 point = 1/72 inch, 1 inch = 25.4 mm)
        width_pt = width_mm * 72 / 25.4
        height_pt = height_mm * 72 / 25.4
        
        # Create canvas with appropriate page size
        c = canvas.Canvas(pdf_path, pagesize=(width_mm*mm, height_mm*mm))
        c.setTitle(f"Barcode Label - {details['item']}")
        
        # Define font sizes
        TITLE_SIZE = 12
        NORMAL_SIZE = 10
        SMALL_SIZE = 8
        
        # Set up font
        font_path = get_system_font_path()
        if font_path:
            font_name = os.path.splitext(os.path.basename(font_path))[0]
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                base_font = font_name
            except Exception as e:
                logger.warning(f"Failed to load custom font: {e}")
                base_font = "Helvetica"
        else:
            base_font = "Helvetica"
            
        # Draw item name at top
        c.setFont(base_font, TITLE_SIZE)
        c.drawCentredString(width_pt/2, height_pt - 20, details['item'])
        
        # Draw barcode image
        if os.path.exists(barcode_path):
            try:
                # Calculate barcode dimensions
                barcode_height = height_pt * 0.4
                barcode_width = width_pt * 0.7
                
                # Center the barcode
                x = (width_pt - barcode_width) / 2
                y = (height_pt - barcode_height) / 2
                
                c.drawImage(barcode_path, x, y, width=barcode_width, 
                          height=barcode_height, preserveAspectRatio=True)
                
                # Draw barcode number below image
                c.setFont(base_font, NORMAL_SIZE)
                c.drawCentredString(width_pt/2, y - 15, details['barcode'])
            except Exception as e:
                logger.error(f"Failed to add barcode image to PDF: {e}")
                c.setFont(base_font, NORMAL_SIZE)
                c.drawCentredString(width_pt/2, height_pt/2, "[Barcode Error]")
        else:
            c.setFont(base_font, NORMAL_SIZE)
            c.drawCentredString(width_pt/2, height_pt/2, "[Barcode Missing]")
        
        # Draw company name and price at bottom with margin
        margin = 10 * mm  # 10mm margin
        c.setFont(base_font, SMALL_SIZE)
        
        # Convert margin to points
        margin_pt = margin * 72 / 25.4
        
        # Draw company name (bottom left with margin)
        c.drawString(margin_pt, margin_pt, details['company'])
        
        # Draw price (bottom right with margin)
        price_text = f"₹{details['sale']}"
        price_width = c.stringWidth(price_text, base_font, SMALL_SIZE)
        c.drawString(width_pt - price_width - margin_pt, margin_pt, price_text)
        
        # Save the PDF
        c.save()
        logger.info(f"PDF generated successfully: {pdf_path}")
        return pdf_path
        
    except ImportError as e:
        logger.error(f"Required library not found: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        return None

def update_excel(barcode, item_name, sale_price, purchase_price, company, generation_date, stock_count):
    """Update Excel sheet with barcode data."""
    try:
        import pandas as pd
        
        # Validate numeric inputs
        db = DatabaseManager()
        if not db.validate_numeric_inputs(sale_price, purchase_price, stock_count):
            logger.error("Invalid numeric inputs for Excel update")
            return False
            
        # Create output directory for today
        today = datetime.datetime.now().strftime("%d-%m-%y")
        excel_dir = os.path.join(output_dir, today, "Excel")
        os.makedirs(excel_dir, exist_ok=True)

        # Excel file paths
        excel_path = os.path.join(excel_dir, f"Stock {today}.xlsx")
        
        # Create backup if file exists
        if os.path.exists(excel_path):
            backup_time = datetime.datetime.now().strftime("%H%M%S")
            backup_path = os.path.join(
                excel_dir, 
                f"Stock {today}_backup_{backup_time}.xlsx"
            )
            import shutil
            shutil.copyfile(excel_path, backup_path)
            logger.info(f"Created Excel backup: {backup_path}")

        # Load or create DataFrame
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            if barcode in df['Barcode'].values:
                idx = df[df['Barcode'] == barcode].index[0]
                df.loc[idx] = [barcode, item_name, sale_price, purchase_price, 
                             company, generation_date, stock_count]
            else:
                new_row = pd.DataFrame([[barcode, item_name, sale_price, purchase_price,
                                       company, generation_date, stock_count]], 
                                     columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = pd.DataFrame({
                'Barcode': [barcode],
                'Item Name': [item_name],
                'Sale Price': [sale_price],
                'Purchase Price': [purchase_price],
                'Company': [company],
                'Generation Date': [generation_date],
                'Opening Stock': [stock_count]
            })

        # Save without opening
        df.to_excel(excel_path, index=False)
        logger.info(f"Excel updated successfully: {excel_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to update Excel: {e}")
        return False


def print_image_via_dialog(parent, image_path):
    """Print an image via print dialog."""
    try:
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageSize(QPrinter.Custom)
        printer.setPaperSize(QSizeF(50, 25), QPrinter.Millimeter)
        printer.setFullPage(True)
        
        dialog = QPrintDialog(printer, parent)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            if not painter.isActive():
                show_error("Failed to initialize printer", parent)
                return False
                
            image = QImage(image_path)
            if image.isNull():
                show_error("Failed to load image for printing", parent)
                painter.end()
                return False
                
            painter.drawImage(QRect(0, 0, printer.width(), printer.height()), image)
            painter.end()
            logger.info(f"Image printed: {image_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to print image: {e}")
        show_error(f"Printing error: {e}", parent)
        return False
# ------------------------------
# UI Message Helpers
# ------------------------------
def show_info(message, parent=None):
    QMessageBox.information(parent, "Information", message)

def show_warning(message, parent=None):
    QMessageBox.warning(parent, "Warning", message)

def show_error(message, parent=None):
    QMessageBox.critical(parent, "Error", message)

# ------------------------------
# Login Dialog
# ------------------------------
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        # In your login UI class __init__ or init_ui method
        self.setMinimumSize(400, 300)
        self.resize(400, 300)
        super().__init__(parent)
        self.db = DatabaseManager()
        self.user = None
        self.role = None
        self.init_ui()

    def init_ui(self):
        super().__init__() 
        self.setWindowTitle("Login - " + TITLE)
        self.setMinimumSize(400, 300)
        self.resize(400, 300)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Username:", self.username)
        form_layout.addRow("Password:", self.password)

        btn_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.reject)
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(exit_btn)

        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            show_warning("Please enter both username and password.", self)
            return

        role = self.db.verify_user(username, password)
        if role:
            self.user = username
            self.role = role
            self.accept()
        else:
            show_error("Invalid username or password.", self)

class UserManagementDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Manage Users")
        self.setFixedSize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["Username", "Role"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.refresh_users()

        add_btn = QPushButton("Add User")
        add_btn.clicked.connect(self.add_user)

        delete_btn = QPushButton("Delete Selected User")
        delete_btn.clicked.connect(self.delete_user)

        layout.addWidget(self.user_table)
        layout.addWidget(add_btn)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def refresh_users(self):
        users = self.db.get_all_users()
        self.user_table.setRowCount(len(users))
        for row, (username, role) in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(username))
            self.user_table.setItem(row, 1, QTableWidgetItem(role))

    def add_user(self, username, password, role):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            c = self.conn.cursor()
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                    (username, hashed_password, role))
            self.conn.commit()
            logger.info(f"User {username} added with role {role}.")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"User {username} already exists.")
            return False
        except Exception as e:
            logger.error(f"Failed to add user: {e}")
            return False
          



    def delete_user(self):
        selected = self.user_table.currentRow()
        if selected < 0:
            show_warning("Please select a user to delete.", self)
            return

        username = self.user_table.item(selected, 0).text()
        if username == "admin":
            show_warning("Cannot delete default admin.", self)
            return

        reply = QMessageBox.question(self, "Delete User", f"Are you sure to delete {username}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_user(username):
                show_info("User deleted.", self)
                self.refresh_users()
            else:
                show_error("Failed to delete user.", self)


    def verify_user(self, username, password):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            c = self.conn.cursor()
            c.execute('SELECT role FROM users WHERE username=? AND password=?', (username, hashed_password))
            result = c.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to verify user: {e}")
            return None
            





def validate_barcode_input(barcode: str, item_name: str, sale_price: float, 
                          purchase_price: float) -> bool:
    """Validate barcode input parameters"""
    if not barcode or not item_name:
        logger.error("Barcode and item name are required")
        return False
    
    if sale_price is not None and sale_price < 0:
        logger.error("Sale price cannot be negative")
        return False
        
    if purchase_price is not None and purchase_price < 0:
        logger.error("Purchase price cannot be negative")
        return False
        
    return True

def validate_barcode_image(image_path):
    """Validate generated barcode image integrity"""
    try:
        with Image.open(image_path) as img:
            # Verify image integrity
            img.verify()
            
            # Check file size
            if os.path.getsize(image_path) == 0:
                raise ValueError("Generated barcode image is empty")
                
            # Verify dimensions
            width, height = img.size
            if width == 0 or height == 0:
                raise ValueError("Invalid image dimensions")
                
            logger.info(f"Image validation successful: {image_path}")
            return True
    except Exception as e:
        logger.error(f"Barcode image validation failed: {e}")
        return False

def handle_file_operation(operation, path, description):
    """Generic file operation handler with proper error messages."""
    try:
        result = operation()
        logger.info(f"Successfully {description}: {path}")
        return result
    except FileNotFoundError:
        error_msg = f"File not found: {path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    except PermissionError:
        error_msg = f"Permission denied accessing: {path}"
        logger.error(error_msg)
        raise PermissionError(error_msg)
    except Exception as e:
        error_msg = f"Error {description}: {e}"
        logger.error(error_msg)
        raise

def generate_barcode_image(barcode_str: str, scale: float = 1.0, dpi: int = 203, font_path: str = None) -> str:
    """
    Generate a barcode image optimized for thermal printers (TVS LP46, 203 DPI).
    Returns path to the generated PNG image.
    """
    try:
        from barcode import get_barcode_class
        from barcode.writer import ImageWriter
        from PIL import Image, ImageDraw, ImageFont

        safe_barcode = barcode_str.strip()
        if not safe_barcode:
            raise ValueError("Empty barcode string provided.")

        today = datetime.datetime.now().strftime("%d-%m-%y")
        base_folder = os.path.join(output_dir, today)
        png_dir = os.path.join(base_folder, "PNG")
        bmp_dir = os.path.join(base_folder, "BMP")
        
        os.makedirs(png_dir, exist_ok=True)
        os.makedirs(bmp_dir, exist_ok=True)

        width_mm, height_mm = 50, 25
        width_px = int((width_mm / 25.4) * dpi)
        height_px = int((height_mm / 25.4) * dpi)

        img = Image.new("RGB", (width_px, height_px), "white")
        draw = ImageDraw.Draw(img)

        font_path = get_system_font_path()
        try:
            font = ImageFont.truetype(font_path, 18) if font_path else ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        # Generate barcode directly without temp save
        Code128 = get_barcode_class('code128')
        barcode_obj = Code128(safe_barcode, writer=ImageWriter())
        barcode_img = barcode_obj.render(writer_options={"module_width": 0.2, "module_height": 15.0})
        barcode_img = barcode_img.convert("RGB")

        barcode_width = int(width_px * 0.8)
        barcode_height = int(height_px * 0.5)
        barcode_img = barcode_img.resize((barcode_width, barcode_height), Image.LANCZOS)

        barcode_x = (width_px - barcode_width) // 2
        barcode_y = int(height_px * 0.15)
        img.paste(barcode_img, (barcode_x, barcode_y))

        barcode_num_y = barcode_y + barcode_height + 5
        draw.text((width_px // 2, barcode_num_y), safe_barcode, fill="black", font=font, anchor="ma")

        final_png = os.path.join(png_dir, safe_barcode + ".png")
        final_bmp = os.path.join(bmp_dir, safe_barcode + ".bmp")

        img.save(final_png, "PNG")
        img.save(final_bmp, "BMP")

        logger.info(f"Barcode images generated at {final_png} and {final_bmp}")
        return final_png

    except Exception as e:
        logger.error(f"Failed to generate barcode image: {e}")
        show_error(f"Barcode generation failed: {e}")
        return None

from PIL import Image

def generate_label_image(item_name, barcode, barcode_path, sale_price, company,
                            width_mm, height_mm, dpi=203, dual_label=False,
                            x_offset=0, y_offset=0):
        """
        Generate a label image (PNG + BMP) with optional dual label layout.
        Returns (png_path, bmp_path)
        """
        try:
            today = datetime.datetime.now().strftime("%d-%m-%y")
            base_folder = os.path.join(output_dir, today)
            png_dir = os.path.join(base_folder, "PNG")
            bmp_dir = os.path.join(base_folder, "BMP")
            os.makedirs(png_dir, exist_ok=True)
            os.makedirs(bmp_dir, exist_ok=True)

            # Calculate pixels
            width_px = int((width_mm / 25.4) * dpi)
            height_px = int((height_mm / 25.4) * dpi)

            # Create canvas
            canvas_width = width_px if not dual_label else width_px * 2
            img = Image.new("RGB", (canvas_width, height_px), "white")

            # Wrap into object for drawing
            class CanvasWrapper:
                def __init__(self, img):
                    self._image = img

            wrapper = CanvasWrapper(img)

            # Draw first label
            render_label(wrapper, "pil", item_name, barcode, barcode_path, sale_price, company,
                        width_px, height_px, x_offset, y_offset)

            # Draw second label if dual layout
            if dual_label:
                render_label(wrapper, "pil", item_name, barcode, barcode_path, sale_price, company,
                            width_px, height_px, x_offset + width_px, y_offset)

            # Save
            filename_base = os.path.join(png_dir, barcode)
            png_path = filename_base + ".png"
            bmp_path = os.path.join(bmp_dir, barcode + ".bmp")

            img.save(png_path, "PNG")
            img.save(bmp_path, "BMP")

            logger.info(f"Label image saved: {png_path}, {bmp_path}")
            return png_path, bmp_path

        except Exception as e:
            logger.error(f"Failed to generate label image: {e}")
            return None, None







# ------------------------------
# User Management Dialog
# ------------------------------
class BarcodeGeneratorUI(QWidget):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.db_manager = DatabaseManager()
        self.last_barcode_png = None
        self.init_ui()

    def toggle_custom_size(self, text):
        """Handle custom size selection in combo box"""
        if text == "Custom Size":
            # Show custom size input dialog
            width, ok = QInputDialog.getDouble(self, "Custom Width", "Enter width (mm):", 100, 10, 1000, 2)
            if ok:
                height, ok = QInputDialog.getDouble(self, "Custom Height", "Enter height (mm):", 50, 10, 1000, 2)
                if ok:
                    # Store custom dimensions
                    LABEL_SIZES["Custom Size"] = (width, height)
        self.update_preview()  # Refresh preview with new size if needed

    def init_ui(self):
        self.setWindowTitle(TITLE)
        self.setGeometry(100, 100, 900, 700)
        
        main_layout = QVBoxLayout()

        # --- Form Layout ---
        form_layout = QFormLayout()

        self.item_name = QLineEdit()
        self.barcode = QLineEdit()
        self.purchase_price = QLineEdit()
        self.sale_price = QLineEdit()
        self.profit_percent = QLineEdit()
        self.company = QLineEdit()
        self.stock = QLineEdit()

        self.size_combo = QComboBox()
        self.size_combo.addItems(LABEL_SIZES.keys())
        self.size_combo.currentTextChanged.connect(self.toggle_custom_size)

        self.custom_width = QLineEdit()
        self.custom_height = QLineEdit()
        self.custom_width.setPlaceholderText("Width (mm)")
        self.custom_height.setPlaceholderText("Height (mm)")
        self.custom_width.setVisible(False)
        self.custom_height.setVisible(False)

        self.label_count = QSpinBox()
        self.label_count.setRange(1, 999)

        form_layout.addRow("Item Name:", self.item_name)
        form_layout.addRow("Barcode (or Auto):", self.barcode)
        form_layout.addRow("Purchase Price:", self.purchase_price)
        form_layout.addRow("Profit %:", self.profit_percent)
        form_layout.addRow("Sale Price:", self.sale_price)
        form_layout.addRow("Company Name:", self.company)
        form_layout.addRow("Opening Stock:", self.stock)
        form_layout.addRow("Label Size:", self.size_combo)
        form_layout.addRow("Custom Width (if selected):", self.custom_width)
        form_layout.addRow("Custom Height (if selected):", self.custom_height)
        form_layout.addRow("Label Count:", self.label_count)

        main_layout.addLayout(form_layout)

        # --- Settings Layout ---
        settings_layout = QHBoxLayout()

        self.dpi_combo = QComboBox()
        self.dpi_combo.addItems(["203", "300", "600"])

        self.dual_label = QCheckBox("2 Labels per Row")
        self.x_offset = QSpinBox()
        self.x_offset.setRange(-100, 100)
        self.x_offset.setPrefix("X:")

        self.y_offset = QSpinBox()
        self.y_offset.setRange(-100, 100)
        self.y_offset.setPrefix("Y:")

        settings_layout.addWidget(QLabel("DPI:"))
        settings_layout.addWidget(self.dpi_combo)
        settings_layout.addWidget(self.dual_label)
        settings_layout.addWidget(self.x_offset)
        settings_layout.addWidget(self.y_offset)

        main_layout.addLayout(settings_layout)

        # --- Buttons ---
        buttons_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Generate Labels")
        self.generate_btn.clicked.connect(self.generate_labels)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_fields)

        self.print_btn = QPushButton("Print Last Label (Direct)")
        self.print_btn.setEnabled(False)
        self.print_btn.clicked.connect(self.print_label_direct)

        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.print_btn)

        main_layout.addLayout(buttons_layout)

        # --- Preview Area ---
        self.preview = QLabel("Preview will appear here after generation")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedHeight(250)
        main_layout.addWidget(self.preview)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

        # --- History Area ---
        history_layout = QVBoxLayout()

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search history...")
        self.search_field.textChanged.connect(self.refresh_history)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Username", "Item Name", "Barcode", 
            "Sale Price", "Purchase Price", "Company", "Date", "Stock"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.doubleClicked.connect(self.reprint_from_history)

        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_history)

        history_layout.addWidget(self.search_field)
        history_layout.addWidget(self.history_table)
        history_layout.addWidget(clear_history_btn)

        main_layout.addLayout(history_layout)
        
        # Initial history refresh
        self.refresh_history()

    # ⬇️ Existing functions stay same: toggle_custom_size, clear_fields, calculate_price, validate_inputs, get_label_size, generate_labels, update_preview, refresh_history, clear_history, reprint_from_history, manage_users, manage_templates
    # Just replacing print_label() with a direct mode one

    def clear_fields(self):
        """Clear all input fields in the form"""
        # Clear all input fields
        self.item_name.clear()
        self.barcode.clear()
        self.purchase_price.clear()
        self.sale_price.clear()
        self.profit_percent.clear()
        self.company.clear()
        self.stock.clear()
        
        # Reset size combo to default
        self.size_combo.setCurrentIndex(0)
        
        # Clear preview if it exists
        if hasattr(self, 'preview'):
            self.preview.clear()
        
        logger.info("All input fields cleared")
        
    def refresh_history(self):
        """Refresh the history table with optional search filter"""
        try:
            search_text = self.search_field.text().strip()
            history = self.db_manager.fetch_history(search_text)
            self.history_table.setRowCount(len(history))
            
            header = self.history_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
            
            for i, row in enumerate(history):
                for j, value in enumerate(row):
                    cell_item = QTableWidgetItem(str(value))
                    cell_item.setTextAlignment(Qt.AlignCenter)
                    self.history_table.setItem(i, j, cell_item)
            
            self.history_table.resizeRowsToContents()
            
        except Exception as e:
            logger.error(f"Error refreshing history: {e}")
            self.status_bar.showMessage(f"Failed to refresh history: {e}", 5000)

    def print_label_direct(self):
        if not self.last_barcode_png or not os.path.exists(self.last_barcode_png):
            show_warning("No label available to print.", self)
            return

        bmp_path = self.last_barcode_png.replace(".png", ".bmp")
        if not os.path.exists(bmp_path):
            show_warning("BMP file missing, cannot direct print.", self)
            return

        if print_bmp_direct(bmp_path):
            self.status_bar.showMessage("Label sent to printer (Direct Mode)", 5000)
        else:
            self.status_bar.showMessage("Direct printing failed", 5000)
    


def print_bmp_direct(bmp_path, printer_name=None):
    """Direct printing using Win32 API for thermal printer"""
    try:
        import win32print
        import win32ui
        from PIL import Image, ImageWin
        
        printer_name = printer_name or win32print.GetDefaultPrinter()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        hDC.StartDoc(bmp_path)
        hDC.StartPage()

        img = Image.open(bmp_path)
        dib = ImageWin.Dib(img)
        dib.draw(hDC.GetHandleOutput(), (0, 0, img.width, img.height))

        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
        logger.info(f"Direct printing successful: {bmp_path}")
        return True
    except Exception as e:
        logger.error(f"Direct print error: {e}")
        return False

def validate_barcode_input(barcode: str, item_name: str, sale_price: float, 
                          purchase_price: float) -> bool:
    """Validate barcode input parameters"""
    if not barcode or not item_name:
        logger.error("Barcode and item name are required")
        return False
    
    if sale_price is not None and sale_price < 0:
        logger.error("Sale price cannot be negative")
        return False
        
    if purchase_price is not None and purchase_price < 0:
        logger.error("Purchase price cannot be negative")
        return False
        
    return True

def validate_barcode_image(image_path):
    """Validate generated barcode image integrity"""
    try:
        with Image.open(image_path) as img:
            # Verify image integrity
            img.verify()
            
            # Check file size
            if os.path.getsize(image_path) == 0:
                raise ValueError("Generated barcode image is empty")
                
            # Verify dimensions
            width, height = img.size
            if width == 0 or height == 0:
                raise ValueError("Invalid image dimensions")
                
            logger.info(f"Image validation successful: {image_path}")
            return True
    except Exception as e:
        logger.error(f"Barcode image validation failed: {e}")
        return False

def print_label_direct(self):
        if not self.last_barcode_png or not os.path.exists(self.last_barcode_png):
            show_warning("No label available to print.", self)
            return

        bmp_path = self.last_barcode_png.replace(".png", ".bmp")
        if not os.path.exists(bmp_path):
            show_warning("BMP file missing, cannot direct print.", self)
            return

        if print_bmp_direct(bmp_path):
            self.status_bar.showMessage("Label sent to printer (Direct Mode)", 5000)
        else:
            self.status_bar.showMessage("Direct printing failed", 5000)
    
   
def generate_labels(self):
    """Generate barcode labels with proper error handling"""
    try:
        # Get input values from UI
        item_name = self.item_name.text().strip()
        barcode = self.barcode.text().strip()
        sale_price = float(self.sale_price.text())
        company_name = self.company.text().strip()
        
        # Validate inputs
        if not all([item_name, barcode, company_name]):
            raise ValueError("All fields are required")
            
        # Generate barcode image
        barcode_class = get_barcode_class('code128')
        barcode_path = os.path.join(output_dir, f"{barcode}.png")
        barcode_class(barcode, writer=ImageWriter()).save(barcode_path)
        
        # Create canvas and render label
        canvas = Image.new('RGB', (800, 200), 'white')
        render_label(canvas, "pil", item_name, barcode, barcode_path, sale_price, company_name, 400, 200)
        
        # Save the generated label
        output_path = os.path.join(output_dir, f"label_{barcode}.png")
        canvas.save(output_path)
        
        # Update database
        with DatabaseManager() as db:
            db.add_barcode_history(
                self.user,
                item_name,
                barcode,
                sale_price,
                None,  # purchase_price
                company_name,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                1  # stock_count
            )
        
        QMessageBox.information(self, "Success", "Label generated successfully!")
        
    except ValueError as e:
        QMessageBox.warning(self, "Input Error", str(e))
    except Exception as e:
        logger.error(f"Label generation failed: {e}")
        QMessageBox.critical(self, "Error", "Failed to generate labels")

def _validate_output_directory(self):
    """Helper method to validate output directory"""
    try:
        if not verify_output_structure():
            show_error("Failed to verify/create output directories", self)
            return False
            
        if not os.path.exists(output_dir):
            new_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if new_folder:
                update_output_dir(new_folder)
            else:
                show_warning("No output folder selected.", self)
                return False
        return True
    except Exception as e:
        logger.error(f"Error checking output directory: {e}")
        show_error(f"Failed to verify output directory: {e}", self)
        return False

def print_bmp_direct(bmp_path, printer_name=None):
    """Direct printing using Win32 API for thermal printer"""
    try:
        import win32print
        import win32ui
        from PIL import Image, ImageWin
        
        printer_name = printer_name or win32print.GetDefaultPrinter()
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        hDC.StartDoc(bmp_path)
        hDC.StartPage()

        img = Image.open(bmp_path)
        dib = ImageWin.Dib(img)
        dib.draw(hDC.GetHandleOutput(), (0, 0, img.width, img.height))

        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
        logger.info(f"Direct printing successful: {bmp_path}")
        return True
    except Exception as e:
        logger.error(f"Direct print error: {e}")
        return False

def validate_barcode_input(barcode: str, item_name: str, sale_price: float, 
                          purchase_price: float) -> bool:
    """Validate barcode input parameters"""
    if not barcode or not item_name:
        logger.error("Barcode and item name are required")
        return False
    
    if sale_price is not None and sale_price < 0:
        logger.error("Sale price cannot be negative")
        return False
        
    if purchase_price is not None and purchase_price < 0:
        logger.error("Purchase price cannot be negative")
        return False
        
    return True

def validate_barcode_image(image_path):
    """Validate generated barcode image integrity"""
    try:
        with Image.open(image_path) as img:
            # Verify image integrity
            img.verify()
            
            # Check file size
            if os.path.getsize(image_path) == 0:
                raise ValueError("Generated barcode image is empty")
                
            # Verify dimensions
            width, height = img.size
            if width == 0 or height == 0:
                raise ValueError("Invalid image dimensions")
                
            logger.info(f"Image validation successful: {image_path}")
            return True
    except Exception as e:
        logger.error(f"Barcode image validation failed: {e}")
        return False

def print_label_direct(self):
        if not self.last_barcode_png or not os.path.exists(self.last_barcode_png):
            show_warning("No label available to print.", self)
            return

        bmp_path = self.last_barcode_png.replace(".png", ".bmp")
        if not os.path.exists(bmp_path):
            show_warning("BMP file missing, cannot direct print.", self)
            return

        if print_bmp_direct(bmp_path):
            self.status_bar.showMessage("Label sent to printer (Direct Mode)", 5000)
        else:
            self.status_bar.showMessage("Direct printing failed", 5000)



if __name__ == "__main__":
    main()
