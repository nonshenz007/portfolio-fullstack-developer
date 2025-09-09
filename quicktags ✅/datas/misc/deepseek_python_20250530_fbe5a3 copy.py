import os
import sys
import time
import sqlite3
import datetime
import random
import warnings
import logging
import traceback
warnings.filterwarnings("ignore", category=DeprecationWarning)
from EmbeddedFont import get_embedded_font
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QGroupBox,
                            QScrollArea, QSizePolicy, QSpacerItem, QDialog, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QFormLayout, QDialogButtonBox, QFrame)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QFont, QFontDatabase, QIcon, QColor
from PyQt5.QtCore import Qt, QSize, QSizeF, QRectF, QTimer
import barcode
from barcode.writer import ImageWriter
import openpyxl
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import subprocess

class QuickTagApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickTags – AutoGeek Edition by Shenz")
        self.setMinimumSize(1000, 700)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Setup logging and database
        self.setup_logger()
        self.init_db()
        self.load_item_history()
        self.load_fonts()

    def create_sidebar(self):
        """Create the left sidebar with navigation buttons"""
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-right: 1px solid #e2e8f0;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(20)
        
        # Title
        title = QLabel("QuickTags")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #1a365d;
                margin-bottom: 5px;
            }
        """)
        
        subtitle = QLabel("AutoGeek Edition by Shenz")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #718096;
                margin-bottom: 30px;
            }
        """)
        
        # Buttons
        self.add_button = self.create_sidebar_button("➕ Add Item", "#3b82f6")
        self.preview_button = self.create_sidebar_button("👁 Preview", "#6b7280")
        self.print_button = self.create_sidebar_button("🖨 Print", "#6b7280")
        self.export_button = self.create_sidebar_button("📤 Export Excel", "#6b7280")
        
        # Spacer and success label
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        self.success_label = QLabel("✓ Item added")
        self.success_label.setStyleSheet("""
            QLabel {
                background-color: #d1fae5;
                color: #065f46;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        self.success_label.hide()
        
        # Add widgets to sidebar
        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addWidget(self.add_button)
        sidebar_layout.addWidget(self.preview_button)
        sidebar_layout.addWidget(self.print_button)
        sidebar_layout.addWidget(self.export_button)
        sidebar_layout.addItem(spacer)
        sidebar_layout.addWidget(self.success_label)
        
        self.main_layout.addWidget(sidebar)

    def create_sidebar_button(self, text, color):
        """Helper to create styled sidebar buttons"""
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 10px 15px;
                font-size: 15px;
                color: {color};
                border-radius: 8px;
                background-color: white;
            }}
            QPushButton:hover {{
                background-color: #f8fafc;
            }}
        """)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def create_main_content(self):
        """Create the main content area with form and history"""
        content = QWidget()
        content.setStyleSheet("background-color: #f8fafc;")
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)
        
        # Create form
        self.create_form(content_layout)
        
        # Create history table
        self.create_history_table(content_layout)
        
        self.main_layout.addWidget(content)

    def create_form(self, parent_layout):
        """Create the product information form"""
        form_group = QGroupBox("Product Information")
        form_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 25px;
                margin-top: 0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                font-weight: bold;
                color: #4a5568;
                font-size: 16px;
            }
        """)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Input fields
        self.item_name_input = self.create_form_input("Item Name (required)")
        self.purchase_price_input = self.create_form_input("Purchase Price (default: 1)", "1")
        self.profit_percent_input = self.create_form_input("Profit % (optional, overrides %)", "100")
        self.sale_price_input = self.create_form_input("Sale Price (default: 1)", "1")
        
        # Add button
        add_btn = QPushButton("Add Item")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_item)
        
        form_layout.addWidget(self.item_name_input)
        form_layout.addWidget(self.purchase_price_input)
        form_layout.addWidget(self.profit_percent_input)
        form_layout.addWidget(self.sale_price_input)
        form_layout.addWidget(add_btn)
        
        form_group.setLayout(form_layout)
        parent_layout.addWidget(form_group)

    def create_form_input(self, placeholder, default_text=""):
        """Helper to create styled form inputs"""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setText(default_text)
        input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #93c5fd;
                outline: none;
            }
        """)
        return input_field

    def create_history_table(self, parent_layout):
        """Create the session history table"""
        history_label = QLabel("Session History")
        history_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #4a5568;
                font-size: 16px;
                margin-bottom: 5px;
            }
        """)
        
        self.history_table = QTableWidget(0, 6)  # 6 columns (no separate edit column)
        self.history_table.setHorizontalHeaderLabels(["Item Name", "Date Added", "Sale Price", "Stock", "", ""])
        
        # Table styling
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #e2e8f0;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #4a5568;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        # Table configuration
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.history_table.setColumnWidth(0, 250)
        self.history_table.setColumnWidth(1, 150)
        self.history_table.setColumnWidth(2, 100)
        self.history_table.setColumnWidth(3, 80)
        self.history_table.setColumnWidth(4, 80)
        self.history_table.setColumnWidth(5, 80)
        
        parent_layout.addWidget(history_label)
        parent_layout.addWidget(self.history_table)

    def add_item_to_table(self, item_name, created_at, sale_price, stock_quantity):
        """Add item to history table with action buttons"""
        row_position = self.history_table.rowCount()
        self.history_table.insertRow(row_position)
        
        # Format date
        try:
            date_obj = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%d-%m-%Y %H:%M")
        except:
            formatted_date = created_at
            
        # Add data cells
        self.history_table.setItem(row_position, 0, QTableWidgetItem(item_name))
        self.history_table.setItem(row_position, 1, QTableWidgetItem(formatted_date))
        self.history_table.setItem(row_position, 2, QTableWidgetItem(f"Rs. {sale_price}"))
        self.history_table.setItem(row_position, 3, QTableWidgetItem(str(stock_quantity)))
        
        # Add action buttons
        self.add_table_button(row_position, 4, "Edit", "#10b981", self.edit_item, item_name)
        self.add_table_button(row_position, 5, "Delete", "#ef4444", self.delete_item, item_name)
        # Reprint button is now in the same cell as Delete with an icon

    def add_table_button(self, row, col, text, color, callback, item_name):
        """Helper to add styled action buttons to table"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px;
                border-radius: 6px;
                font-size: 13px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {'#0d9488' if color == '#10b981' else '#dc2626'};
            }}
        """)
        btn.clicked.connect(lambda: callback(item_name))
        self.history_table.setCellWidget(row, col, btn)

    # ====== Core Functionality (unchanged from original) ======
    
    def setup_logger(self):
        """Set up logging with file and console output"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(os.path.expanduser('~'), 'quicktag_log.txt')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('QuickTags')
        
    def init_db(self):
        try:
            # Get the correct database path for both development and EXE modes
            if getattr(sys, 'frozen', False):
                # Running in EXE mode
                app_dir = os.path.dirname(sys.executable)
                self.logger.info(f"App directory: {app_dir}")
                db_path = os.path.join(app_dir, 'quicktag.db')
                self.logger.info(f"Trying database path: {db_path}")
                
                # Check if app directory is writable
                test_file = os.path.join(app_dir, 'test_write.tmp')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    self.logger.info("App directory is writable")
                except (IOError, PermissionError):
                    # App directory is not writable, use user's home directory instead
                    user_data_dir = os.path.join(os.path.expanduser('~'), '.quicktag')
                    os.makedirs(user_data_dir, exist_ok=True)
                    db_path = os.path.join(user_data_dir, 'quicktag.db')
                    self.logger.info(f"Using alternate database path: {db_path}")
                    
                    # Try to copy the original database if it doesn't exist
                    if not os.path.exists(db_path):
                        try:
                            import shutil
                            shutil.copy2(os.path.join(app_dir, 'quicktag.db'), db_path)
                            self.logger.info("Copied database to user directory")
                        except Exception as copy_error:
                            self.logger.error(f"Could not copy database: {copy_error}")
                    
                    QMessageBox.information(self, "Database Location", 
                                          f"Using database at: {db_path}\n(Application directory is not writable)")
            else:
                # Running in development mode
                db_path = 'quicktag.db'
                self.logger.info(f"Using development database path: {db_path}")
                
            self.logger.info(f"Connecting to database at: {db_path}")
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT UNIQUE,
                    barcode TEXT UNIQUE,
                    purchase_price INTEGER,
                    profit_percent INTEGER,
                    sale_price INTEGER,
                    stock_quantity INTEGER,
                    created_at TEXT
                )
            ''')
            self.conn.commit()
            self.logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {str(e)}")
            sys.exit(1)
            
    def load_fonts(self):
        """Load fonts with better error handling for EXE mode"""
        try:
            font_path = self.get_font_path()
            if font_path:
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                    self.font_bold = QFont(font_family, 16, QFont.Bold)
                    self.font_regular = QFont(font_family, 15)
                    return
        
            # Fallback to system fonts if embedded fonts not found
            self.font_bold = QFont("Arial", 16, QFont.Bold)
            self.font_regular = QFont("Arial", 15)
            
        except Exception as e:
            self.logger.error(f"Error loading fonts: {str(e)}")
            # Final fallback
            self.font_bold = QFont()
            self.font_regular = QFont()

    def get_font_path(self):
        """Get font path with multiple fallbacks for EXE compatibility"""
        possible_paths = []
        
        # EXE mode paths
        if getattr(sys, 'frozen', False):
            possible_paths.extend([
                os.path.join(sys._MEIPASS, 'assets', 'arialbd.ttf'),
                os.path.join(sys._MEIPASS, 'arialbd.ttf'),
                os.path.join(os.path.dirname(sys.executable), 'assets', 'arialbd.ttf'),
                os.path.join(os.path.dirname(sys.executable), 'arialbd.ttf')
            ])
        # Development mode paths
        else:
            possible_paths.extend([
                os.path.join(os.path.dirname(__file__), 'assets', 'arialbd.ttf'),
                os.path.join(os.path.dirname(__file__), 'arialbd.ttf'),
                os.path.join('assets', 'arialbd.ttf'),
                'arialbd.ttf'
            ])
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found font at: {path}")
                return path
                
        # Fallback to system fonts
        system_paths = [
            '/System/Library/Fonts/Arial Bold.ttf',  # macOS
            'C:\\Windows\\Fonts\\arialbd.ttf',  # Windows
            '/usr/share/fonts/truetype/msttcorefonts/arialbd.ttf'  # Linux
        ]
        
        for path in system_paths:
            if os.path.exists(path):
                self.logger.info(f"Found system font at: {path}")
                return path
                
        self.logger.warning("No suitable font found")
        return None

    def add_item(self):
        item_name = self.item_name_input.text().strip()
        if not item_name:
            QMessageBox.warning(self, "Error", "Item Name is required!")
            return
            
        # Check for duplicate item name
        self.cursor.execute("SELECT COUNT(*) FROM items WHERE item_name=?", (item_name,))
        if self.cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Error", "Item Name already exists!")
            return
            
        # Generate or use override barcode
        barcode_value = self.generate_barcode()
        
        # Check for duplicate barcode
        self.cursor.execute("SELECT COUNT(*) FROM items WHERE barcode=?", (barcode_value,))
        if self.cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Error", "Barcode already exists!")
            return
            
        # Get other values
        try:
            purchase_price = int(float(self.purchase_price_input.text() or 1))
            if purchase_price <= 0:
                raise ValueError("Purchase price must be positive")
                    
            profit_percent = int(float(self.profit_percent_input.text() or 100))
            if profit_percent < 0:
                raise ValueError("Profit percent cannot be negative")
                    
            stock_quantity = int(self.stock_quantity_input.text() or 1)
            if stock_quantity <= 0:
                raise ValueError("Stock quantity must be positive")
            
            # Calculate sale price
            sale_price_input = self.sale_price_input.text().strip()
            if sale_price_input:
                sale_price = int(float(sale_price_input))
            else:
                sale_price = int(purchase_price + (purchase_price * profit_percent / 100))
                
            # Add to database with transaction handling
            try:
                created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute('''
                    INSERT INTO items 
                    (item_name, barcode, purchase_price, profit_percent, sale_price, stock_quantity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (item_name, barcode_value, purchase_price, profit_percent, sale_price, stock_quantity, created_at))
                self.conn.commit()
                
                # Add to history table
                self.add_item_to_table(item_name, created_at, sale_price, stock_quantity)
                
                # Show success message
                self.success_label.show()
                QTimer.singleShot(3000, self.success_label.hide)
                
                # Clear inputs
                self.item_name_input.clear()
                self.purchase_price_input.setText("1")
                self.profit_percent_input.setText("100")
                self.sale_price_input.setText("1")
                
            except sqlite3.Error as e:
                self.conn.rollback()
                QMessageBox.warning(self, "Database Error", f"Operation failed: {str(e)}")
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")
            
    def generate_barcode(self, force_new=False):
        """Generate a unique barcode or retrieve from database if item name exists"""
        # Check if we already have a barcode for this item in the database
        if not force_new and self.item_name_input.text().strip():
            item_name = self.item_name_input.text().strip()
            self.cursor.execute("SELECT barcode FROM items WHERE item_name=?", (item_name,))
            result = self.cursor.fetchone()
            if result:
                return result[0]  # Return existing barcode
                
        # Generate a new unique barcode
        while True:
            barcode_value = str(random.randint(100000000000, 999999999999))
            self.cursor.execute("SELECT COUNT(*) FROM items WHERE barcode=?", (barcode_value,))
            if self.cursor.fetchone()[0] == 0:
                return barcode_value
                
    def generate_barcode_image(self, barcode_value):
        """Generate ultra-sharp 1-bit barcode image of fixed 280x70 size for clean layout."""
        try:
            from barcode import EAN13
            from barcode.writer import ImageWriter

            writer = ImageWriter()
            font_path = self.get_font_path()

            writer.set_options({
                'module_width': 0.32,           # Precisely tuned for ~280px
                'module_height': 70,
                'quiet_zone': 4,
                'font_size': 14,
                'text_distance': 1,
                'write_text': True,
                'background': 'white',
                'foreground': 'black',
                'font_path': font_path if font_path else None
            })

            buffer = BytesIO()
            ean = EAN13(barcode_value, writer=writer)
            ean.write(buffer)
            buffer.seek(0)

            # Enforce layout-safe size (280x70) with high quality
            img = Image.open(buffer).convert("L")
            img = img.resize((280, 70), Image.BOX)
            return img.convert("1")  # Force black/white

        except Exception as e:
            self.logger.error(f"Error generating barcode: {str(e)}")
            return Image.new('1', (280, 70), 1)  # Fallback white image
    
    def generate_row_label_image(self, items, output_path):
        """Generate multi-row 800px wide BMP with 2 labels per row"""
        from math import ceil
        try:
            rows = ceil(len(items) / 2)
            img_height = rows * 200
            img = Image.new("1", (800, img_height), 1)  # 1-bit image
            draw = ImageDraw.Draw(img)

            # Use embedded fonts
            title_font = get_embedded_font(16)
            price_font = get_embedded_font(16)
            brand_font = get_embedded_font(16)

            for index, item in enumerate(items):
                row = index // 2
                col = index % 2
                x_offset = col * 400
                y_offset = row * 200

                # Draw item name (centered in 400px block)
                text_width = draw.textlength(item['item_name'], font=title_font)
                draw.text(
                    (x_offset + (400 - text_width)/2, y_offset + 10),
                    item['item_name'],
                    font=title_font,
                    fill=0  # 0=black in 1-bit mode
                )
                
                # Draw barcode (fixed position within 400px block)
                barcode_img = self.generate_barcode_image(item['barcode'])
                barcode_img = self.generate_barcode_image(item['barcode']).convert("1")
                img.paste(barcode_img, (x_offset + 60, y_offset + 35))
                
                # Draw price (centered in 400px block) - Format matches the image
                price_text = f"Sale Price: {item['sale_price']}"
                text_width = draw.textlength(price_text, font=price_font)
                draw.text(
                    (x_offset + (400 - text_width)/2, y_offset + 115),
                    price_text,
                    font=price_font,
                    fill=0  # 0=black in 1-bit mode
                )
                
                # Draw brand name (centered in 400px block)
                text_width = draw.textlength("AUTO GEEK", font=brand_font)
                draw.text(
                    (x_offset + (400 - text_width)/2, y_offset + 155),
                    "AUTO GEEK",
                    font=brand_font,
                    fill=0  # 0=black in 1-bit mode
                )

            # Save as 1-bit BMP at 203 DPI (thermal printer standard)
            img.save(output_path, "BMP", dpi=(203, 203))
            return True
        except Exception as e:
            QMessageBox.warning(self, "Image Error", f"Failed to generate row labels: {str(e)}")
            return False
     
    def save_label_files(self, items):
        try:
            # Create date-based folders
            today = datetime.datetime.now().strftime("%d-%m-%y")
            folders = {
                'bmp': os.path.join("barcodes", today, "BMP"),
                'png': os.path.join("barcodes", today, "PNG"),
                'pdf': os.path.join("barcodes", today, "PDF")
            }
            
            for folder in folders.values():
                os.makedirs(folder, exist_ok=True)
                
            # Generate all labels considering stock quantities
            all_labels = []
            for item in items:
                all_labels.extend([item] * item['stock_quantity'])
                
            temp_path = os.path.join("temp_print", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
            os.makedirs(temp_path, exist_ok=True)
            
            # Process labels in pairs
            for i in range(0, len(all_labels), 2):
                item_pair = all_labels[i:i+2]
                # Save files with counter for duplicates
                base_name = f"{item_pair[0]['item_name']}_{i//2}"
                bmp_path = os.path.join(folders['bmp'], f"{base_name}.bmp")
                png_path = os.path.join(folders['png'], f"{base_name}.png")
                pdf_path = os.path.join(folders['pdf'], f"{base_name}.pdf")
                
                self.generate_row_label_image(item_pair, bmp_path)
                
                # Just save PNG and PDF versions
                image = Image.open(bmp_path)
                image.save(png_path, "PNG", dpi=(203, 203))
                image.save(pdf_path, "PDF", resolution=203.0)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save label files: {str(e)}")
            return False
        return True
        
    def handle_reprint(self, barcode, name, price):
        """Handle reprint requests from history table"""
        try:
            # Fetch item details from DB
            self.cursor.execute("SELECT item_name, barcode, sale_price FROM items WHERE item_name=?", (name,))
            result = self.cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Reprint Error", f"Item '{name}' not found in database!")
                return

            count, ok = QInputDialog.getInt(
                self, "Reprint Label",
                "Number of labels to reprint (Max 2):",
                2, 1, 2
            )
            if not ok:
                return

            items = [{
                'item_name': name,
                'barcode': barcode,
                'sale_price': price,
                'stock_quantity': 1
            } for _ in range(count)]

            temp_dir = self.ensure_temp_dir("quicktag_reprints")
            bmp_path = os.path.join(temp_dir, f"reprint_{barcode}.bmp")
            self.generate_row_label_image(items, bmp_path)

            if sys.platform == 'win32':
                os.startfile(bmp_path)
            else:
                subprocess.run(['open', bmp_path])

        except Exception as e:
            QMessageBox.critical(self, "Reprint Failed", f"Error: {str(e)}")
            
    def preview_barcode(self):
        """Preview the label in a PyQt window instead of system viewer"""
        try:
            import copy
            item_name = self.item_name_input.text().strip()
            if not item_name:
                QMessageBox.warning(self, "Error", "Item Name is required!")
                return

            # Get current item details
            barcode_value = self.generate_barcode()
            sale_price = self.calculate_current_price()
            stock_qty = min(int(self.stock_quantity_input.text() or 1), 2)  # Limit to 2 for preview

            # Create full item list based on stock (limited to 2 for preview)
            item = {
                'item_name': item_name,
                'barcode': barcode_value,
                'sale_price': sale_price,
                'stock_quantity': stock_qty
            }
            items = [copy.deepcopy(item) for _ in range(min(stock_qty, 2))]

            # Create temp directory
            temp_dir = self.ensure_temp_dir("quicktag_temp")
            temp_bmp = os.path.join(temp_dir, 'quicktag_preview.bmp')

            # Generate row image with proper layout
            if self.generate_row_label_image(items, temp_bmp):
                # Create preview window instead of opening in system viewer
                if not hasattr(self, 'preview_window') or not self.preview_window.isVisible():
                    self.preview_window = QDialog(self)
                    self.preview_window.setWindowTitle("Label Preview")
                    self.preview_window.setMinimumSize(820, 220)
                    layout = QVBoxLayout()
                    self.preview_label_widget = QLabel()
                    self.preview_label_widget.setAlignment(Qt.AlignCenter)
                    layout.addWidget(self.preview_label_widget)
                    self.preview_window.setLayout(layout)
                
                # Load the image into the preview window
                pixmap = QPixmap(temp_bmp)
                self.preview_label_widget.setPixmap(pixmap)
                self.preview_window.show()
                    
        except Exception as e:
            self.logger.error(f"Preview generation failed: {str(e)}")
            QMessageBox.warning(self, "Preview Error", f"Failed to generate preview: {str(e)}")

    def print_barcode(self):
        """Print current label with smart handling of stock quantities"""
        try:
            item_name = self.item_name_input.text().strip()
            if not item_name:
                QMessageBox.warning(self, "Error", "Item Name is required!")
                return
                
            # Get current item details
            barcode_value = self.generate_barcode()
            sale_price = self.calculate_current_price()
            stock_qty = int(self.stock_quantity_input.text() or 1)
            
            # Create item data
            item = {
                'item_name': item_name,
                'barcode': barcode_value,
                'sale_price': sale_price,
                'stock_quantity': stock_qty  # Store full quantity in database
            }
            
            # For printing, limit to 2 labels per row (thermal printer limitation)
            print_items = [item.copy() for _ in range(min(stock_qty, 2))]

            # Create temp directory
            output_dir = self.ensure_temp_dir("quicktag_single")
            label_path = os.path.join(output_dir, "label_print.bmp")

            # Always use the 2-per-row format for thermal printers
            self.generate_row_label_image(print_items, label_path)

            # Open in system viewer for printing
            if sys.platform == 'win32':
                os.startfile(label_path)  # Uses Photos App
            else:
                subprocess.run(['open', label_path])
            QMessageBox.information(self, "Ready", "Label ready for printing.")
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Print failed: {str(e)}")

    def print_all_barcodes(self):
        """Generate BMP files per 2-label row for all items in DB and open folder for batch printing"""
        try:
            output_dir = self.ensure_temp_dir("quicktag_batch")

            self.cursor.execute("SELECT item_name, barcode, sale_price, stock_quantity FROM items")
            records = self.cursor.fetchall()

            if not records:
                QMessageBox.information(self, "No Items", "No items found in database.")
                return

            from math import ceil

            # Generate label row images (800x200) per every 2 stock
            all_label_blocks = []
            for (item_name, barcode, sale_price, stock_qty) in records:
                item_data = {
                    'item_name': item_name,
                    'barcode': barcode,
                    'sale_price': sale_price
                }
                duplicates = [item_data.copy() for _ in range(stock_qty)]
                all_label_blocks.extend(duplicates)

            for i in range(0, len(all_label_blocks), 2):
                pair = all_label_blocks[i:i+2]
                bmp_path = os.path.join(output_dir, f"label_{i//2}.bmp")
                self.generate_row_label_image(pair, bmp_path)

            # Open folder for Ctrl+P printing
            if sys.platform == 'win32':
                os.startfile(output_dir)
                QMessageBox.information(self, "Batch Ready", "Labels ready.\nOpened folder.\nSelect all and press Ctrl+P in Photos.")
            else:
                subprocess.run(['open', output_dir])
        except Exception as e:
            self.logger.error(f"Print all failed: {str(e)}")
            QMessageBox.critical(self, "Print All Error", f"Failed to generate batch labels: {str(e)}")

    def export_to_excel(self):
        try:
            today = datetime.datetime.now().strftime("%d-%m-%y")
            excel_folder = os.path.join("excel", today)
            os.makedirs(excel_folder, exist_ok=True)
            
            excel_path = os.path.join(excel_folder, f"Stock {today}.xlsx")
            
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["Item Name", "Barcode", "Purchase Price", "Sale Price", "Opening Stock"])
            
            self.cursor.execute("SELECT item_name, barcode, purchase_price, sale_price, stock_quantity FROM items")
            for row in self.cursor.fetchall():
                sheet.append([
                    row[0],  # item_name
                    row[1],  # barcode
                    row[2],  # purchase_price
                    row[3],  # sale_price
                    row[4]   # stock_quantity
                ])
                
            workbook.save(excel_path)
            QMessageBox.information(self, "Success", f"Excel exported to:\n{excel_path}")
            self.load_item_history()  # Refresh history after export
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export Excel: {str(e)}")
            
    def edit_item(self, item_name):
        """Open dialog to edit an existing item"""
        try:
            # Get current item data from database
            self.cursor.execute(
                "SELECT item_name, barcode, purchase_price, profit_percent, sale_price, stock_quantity FROM items WHERE item_name=?", 
                (item_name,)
            )
            item_data = self.cursor.fetchone()
            
            if not item_data:
                QMessageBox.warning(self, "Error", f"Item '{item_name}' not found in database!")
                return
                
            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit Item: {item_name}")
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout()
            form_layout = QFormLayout()
            
            # Create input fields with current values
            item_name_input = QLineEdit(item_data[0])
            barcode_input = QLineEdit(item_data[1])
            purchase_price_input = QLineEdit(str(item_data[2]))
            profit_percent_input = QLineEdit(str(item_data[3]))
            sale_price_input = QLineEdit(str(item_data[4]))
            stock_quantity_input = QLineEdit(str(item_data[5]))
            
            # Add fields to form
            form_layout.addRow("Item Name:", item_name_input)
            form_layout.addRow("Barcode:", barcode_input)
            form_layout.addRow("Purchase Price:", purchase_price_input)
            form_layout.addRow("Profit %:", profit_percent_input)
            form_layout.addRow("Sale Price:", sale_price_input)
            form_layout.addRow("Stock Quantity:", stock_quantity_input)
            
            # Add form to layout
            layout.addLayout(form_layout)
            
            # Add buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            
            # Show dialog and process result
            if dialog.exec_() == QDialog.Accepted:
                # Validate inputs
                try:
                    new_name = item_name_input.text().strip()
                    new_barcode = barcode_input.text().strip()
                    new_purchase_price = int(float(purchase_price_input.text()))
                    new_profit_percent = int(float(profit_percent_input.text()))
                    new_sale_price = int(float(sale_price_input.text()))
                    new_stock_quantity = int(stock_quantity_input.text())
                    
                    if not new_name:
                        raise ValueError("Item name cannot be empty")
                        
                    if not new_barcode or len(new_barcode) != 12:
                        raise ValueError("Barcode must be 12 digits")
                        
                    if new_purchase_price <= 0:
                        raise ValueError("Purchase price must be positive")
                        
                    if new_profit_percent < 0:
                        raise ValueError("Profit percent cannot be negative")
                        
                    if new_sale_price <= 0:
                        raise ValueError("Sale price must be positive")
                        
                    if new_stock_quantity <= 0:
                        raise ValueError("Stock quantity must be positive")
                        
                    # Check for duplicate name if name changed
                    if new_name != item_name:
                        self.cursor.execute("SELECT COUNT(*) FROM items WHERE item_name=?", (new_name,))
                        if self.cursor.fetchone()[0] > 0:
                            raise ValueError(f"Item name '{new_name}' already exists!")
                    
                    # Check for duplicate barcode if barcode changed
                    if new_barcode != item_data[1]:
                        self.cursor.execute("SELECT COUNT(*) FROM items WHERE barcode=?", (new_barcode,))
                        if self.cursor.fetchone()[0] > 0:
                            raise ValueError(f"Barcode '{new_barcode}' already exists!")
                    
                    # Update database with transaction handling
                    try:
                        self.cursor.execute(
                            """UPDATE items SET 
                                item_name=?, barcode=?, purchase_price=?, profit_percent=?, 
                                sale_price=?, stock_quantity=? 
                               WHERE item_name=?""", 
                            (new_name, new_barcode, new_purchase_price, new_profit_percent, 
                             new_sale_price, new_stock_quantity, item_name)
                        )
                        self.conn.commit()
                        
                        # Refresh table
                        self.load_item_history()
                        
                        QMessageBox.information(self, "Success", f"Item '{new_name}' updated successfully!")
                    except sqlite3.Error as e:
                        self.conn.rollback()
                        QMessageBox.warning(self, "Database Error", f"Operation failed: {str(e)}")
                    
                except ValueError as e:
                    QMessageBox.warning(self, "Input Error", str(e))
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to update item: {str(e)}")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit item: {str(e)}")

    def delete_item(self, item_name):
        """Delete an item from the database"""
        try:
            reply = QMessageBox.question(
                self, 
                "Confirm Delete", 
                f"Are you sure you want to delete '{item_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    self.cursor.execute("DELETE FROM items WHERE item_name=?", (item_name,))
                    self.conn.commit()
                    self.load_item_history()
                    QMessageBox.information(self, "Success", f"Item '{item_name}' deleted successfully!")
                except sqlite3.Error as e:
                    self.conn.rollback()
                    QMessageBox.warning(self, "Database Error", f"Operation failed: {str(e)}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete item: {str(e)}")

    def reprint_item(self, item_name):
        try:
            # Fetch item details from DB
            self.cursor.execute("SELECT item_name, barcode, sale_price FROM items WHERE item_name=?", (item_name,))
            result = self.cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Reprint Error", f"Item '{item_name}' not found in database!")
                return

            name, barcode, price = result

            # Ask how many labels to print (max 2)
            count, ok = QInputDialog.getInt(
                self, "Reprint Label",
                "Number of labels to reprint (Max 2):",
                2, 1, 2
            )
            if not ok:
                return

            # Build item list
            items = [{
                'item_name': name,
                'barcode': barcode,
                'sale_price': price,
                'stock_quantity': 1
            } for _ in range(count)]

            temp_dir = self.ensure_temp_dir("quicktag_reprints")
            bmp_path = os.path.join(temp_dir, f"reprint_{barcode}.bmp")
            self.generate_row_label_image(items, bmp_path)

            if sys.platform == 'win32':
                os.startfile(bmp_path)
            else:
                subprocess.run(['open', bmp_path])

        except Exception as e:
            QMessageBox.critical(self, "Reprint Failed", f"Error: {str(e)}")

    def calculate_current_price(self):
        """Calculate the current price based on inputs"""
        try:
            purchase_price = int(float(self.purchase_price_input.text() or 1))
            profit_percent = int(float(self.profit_percent_input.text() or 100))
            sale_price_input = self.sale_price_input.text().strip()
            
            if sale_price_input:
                return int(float(sale_price_input))
            else:
                return int(purchase_price + (purchase_price * profit_percent / 100))
        except:
            return 0
            
    def ensure_temp_dir(self, dir_name):
        """Ensure temporary directory exists with proper error handling"""
        try:
            temp_dir = os.path.join(os.path.expanduser('~'), dir_name)
            os.makedirs(temp_dir, exist_ok=True)
            self.logger.info(f"Created temporary directory: {temp_dir}")
            return temp_dir
        except Exception as e:
            self.logger.error(f"Error creating directory {dir_name}: {str(e)}")
            # Try fallback to current directory
            try:
                fallback_dir = os.path.join(os.getcwd(), dir_name)
                os.makedirs(fallback_dir, exist_ok=True)
                self.logger.info(f"Created fallback directory: {fallback_dir}")
                return fallback_dir
            except Exception as fallback_error:
                self.logger.error(f"Error creating fallback directory: {str(fallback_error)}")
                # Last resort - just use current directory
                return os.getcwd()
                
    def load_item_history(self):
        self.history_table.setRowCount(0)
        self.cursor.execute("SELECT item_name, created_at, sale_price, stock_quantity FROM items")
        for item in self.cursor.fetchall():
            self.add_item_to_table(*item)

    def closeEvent(self, event):
        """Properly close database connection when application exits"""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
                self.logger.info("Database connection closed properly")
            if hasattr(self, 'preview_window'):
                self.preview_window.close()
        except Exception as e:
            self.logger.error(f"Error closing database: {str(e)}")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuickTagApp()
    window.show()
    sys.exit(app.exec_())