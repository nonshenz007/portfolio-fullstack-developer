import os
import sys
import pkgutil
import io

# Add this before any barcode imports
if getattr(sys, 'frozen', False):
    os.environ['BARCODE_DISABLE_TTF'] = '1'
import sqlite3
import datetime
import random
import shutil
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QGroupBox,
                            QScrollArea, QSizePolicy, QSpacerItem, QDialog, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QFont, QFontDatabase, QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import QSizeF  # Add this import
import barcode
from barcode.writer import ImageWriter
import openpyxl
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import win32print
import win32ui
import win32con

class QuickTagApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quicktags – AutoGeek Edition by Shenz")
        self.setMinimumSize(600, 400)
   
        # Initialize database first
        self.init_db()
        
        # Then create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        
        # Now you can set layout properties
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Add header title
        self.add_header()
        
        # Create form fields
        self.create_form()
        
        # Remove this line:
        # self.layout.addStretch(1)
        
        # Create buttons
        self.create_buttons()
        
        # Create history table
        self.create_history_table()
        
        # Session list
        # Remove this line:
        # self.session_items = []
        
        # Load existing items from database
        self.load_item_history()
        
        # Load fonts
        self.load_fonts()
        
    def add_header(self):
        header = QLabel("Quicktags – AutoGeek Edition by Shenz")
        header.setFont(QFont("Arial", 18, QFont.Bold))  # Changed from 14 to 18
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("padding: 5px;")
        self.layout.addWidget(header)
        
    def init_db(self):
        try:
            # Get the correct database path for both development and EXE modes
            if getattr(sys, 'frozen', False):
                # Running in EXE mode
                db_path = os.path.join(os.path.dirname(sys.executable), 'quicktag.db')
            else:
                # Running in development mode
                db_path = 'quicktag.db'
                
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
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to initialize database: {str(e)}")
            sys.exit(1)
        
    def load_fonts(self):
        # Try to load from bundled resources first
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'arialbd.ttf')
            self.font_bold = QFont("Arial", 16, QFont.Bold)
            self.font_regular = QFont("Arial", 15)
        except:
            # Fallback to system fonts
            font_names = ["Arial", "Helvetica", "San Francisco", ".SF NS Text"]
            self.font_bold = QFont()
            self.font_regular = QFont()
            
            for name in font_names:
                if self.font_bold.exactMatch(): break
                self.font_bold = QFont(name, 16, QFont.Bold)
                
            for name in font_names:
                if self.font_regular.exactMatch(): break
                self.font_regular = QFont(name, 15)
        
    def create_form(self):
        form_group = QGroupBox("Product Information")
        form_group.setMinimumWidth(400)  # Original width constraint
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)
        
        # Item Name
        self.item_name_label = QLabel("Item Name (required):")
        self.item_name_input = QLineEdit()
        form_layout.addWidget(self.item_name_label)
        form_layout.addWidget(self.item_name_input)
        
        # Purchase Price
        self.purchase_price_label = QLabel("Purchase Price (default: 1):")
        self.purchase_price_input = QLineEdit("1")
        form_layout.addWidget(self.purchase_price_label)
        form_layout.addWidget(self.purchase_price_input)
        
        # Profit %
        self.profit_percent_label = QLabel("Profit % (default: 100):")
        self.profit_percent_input = QLineEdit("100")
        form_layout.addWidget(self.profit_percent_label)
        form_layout.addWidget(self.profit_percent_input)
        
        # Sale Price
        self.sale_price_label = QLabel("Sale Price (optional, overrides %Profit):")
        self.sale_price_input = QLineEdit()
        form_layout.addWidget(self.sale_price_label)
        form_layout.addWidget(self.sale_price_input)
        
        # Stock Quantity
        self.stock_quantity_label = QLabel("Stock Quantity (default: 1):")
        self.stock_quantity_input = QLineEdit("1")
        form_layout.addWidget(self.stock_quantity_label)
        form_layout.addWidget(self.stock_quantity_input)
        
        form_group.setLayout(form_layout)
        self.layout.addWidget(form_group)
        
        # Barcode (hidden override)
        self.barcode_override_label = QLabel("Barcode Override:")
        self.barcode_override_input = QLineEdit()
        self.barcode_override_label.hide()
        self.barcode_override_input.hide()
        form_layout.addWidget(self.barcode_override_label)
        form_layout.addWidget(self.barcode_override_input)

    def create_buttons(self):
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid #ddd;
                background: white;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
            #add_item_button {
                background: #28a745;
                color: white;
                border-color: #218838;
            }
            #preview_button {
                background: #17a2b8;
                color: white;
                border-color: #117a8b;
            }
            #print_button, #print_all_button {
                background: #007bff;
                color: white;
                border-color: #0069d9;
            }
            #export_excel_button {
                background: #6c757d;
                color: white;
                border-color: #5a6268;
            }
            #clear_button {
                background: #dc3545;
                color: white;
                border-color: #c82333;
            }
        """
        
        # Remove button styling
        # button_container.setStyleSheet(button_style)
        
        # Add Item button
        self.add_item_button = QPushButton("➕ Add Item")
        self.add_item_button.setObjectName("add_item_button")
        self.add_item_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_item_button)  # Changed from self.button_layout
        
        # Preview button
        self.preview_button = QPushButton("👁️ Preview")
        self.preview_button.clicked.connect(self.preview_label)
        button_layout.addWidget(self.preview_button)  # Changed from self.button_layout
        
        # Print button
        self.print_button = QPushButton("🖨️ Print")
        self.print_button.clicked.connect(self.print_label)
        button_layout.addWidget(self.print_button)  # Changed from self.button_layout
        
        # Print All button
        self.print_all_button = QPushButton("🧾 Print All")
        self.print_all_button.clicked.connect(self.print_all_labels)
        button_layout.addWidget(self.print_all_button)  # Changed from self.button_layout
        
        # Export Excel button
        self.export_excel_button = QPushButton("📁 Export Excel")
        self.export_excel_button.clicked.connect(self.export_to_excel)
        button_layout.addWidget(self.export_excel_button)  # Changed from self.button_layout
        
        # Add Clear button
        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.clicked.connect(self.clear_items)
        button_layout.addWidget(self.clear_button)
        
        # Add Barcode Toggle button
        self.toggle_barcode_button = QPushButton("🔢 Toggle Barcode")
        self.toggle_barcode_button.clicked.connect(self.toggle_barcode_override)
        button_layout.addWidget(self.toggle_barcode_button)
        
        self.layout.addWidget(button_container)  # Changed from self.central_layout
        
    def create_history_table(self):
        table_group = QGroupBox("Session History")
        table_layout = QVBoxLayout(table_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Item Name", "Date", "Sale Price", "Stock Qty"])
        
        # Revert to original table settings
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionMode(QTableWidget.NoSelection)
        self.history_table.setShowGrid(False)
        self.history_table.setAlternatingRowColors(True)
        
        # Revert to original row height
        self.history_table.verticalHeader().setDefaultSectionSize(40)
        
        # Configure fonts
        # Update font sizes (reduced by ~5%)
        header_font = QFont("Arial", 15, QFont.Bold)  # Reduced from 16 to 15
        cell_font = QFont("Arial", 13)  # Reduced from 14 to 13
        self.history_table.horizontalHeader().setFont(header_font)
        self.history_table.setFont(cell_font)
        
        # Configure column behavior
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        table_layout.addWidget(self.history_table)
        self.layout.addWidget(table_group)

    def add_item_to_table(self, item_name, created_at, price, quantity):
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        try:
            # First try parsing with the expected format
            formatted_date = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
        except ValueError:
            try:
                # If that fails, try parsing as a barcode number (fallback)
                formatted_date = created_at
            except:
                # If all fails, use current date
                formatted_date = datetime.datetime.now().strftime("%d-%m-%Y")
        
        for i, value in enumerate([item_name, formatted_date, f"₹{price}", str(quantity)]):
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, i, item)

    def toggle_barcode_override(self):
        """Toggle visibility of barcode override fields"""
        if self.barcode_override_label.isVisible():
            self.barcode_override_label.hide()
            self.barcode_override_input.hide()
        else:
            self.barcode_override_label.show()
            self.barcode_override_input.show()
            
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
        barcode_value = self.barcode_override_input.text().strip() or self.generate_barcode()
        
        # Check for duplicate barcode
        self.cursor.execute("SELECT COUNT(*) FROM items WHERE barcode=?", (barcode_value,))
        if self.cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Error", "Barcode already exists!")
            return
            
        # Get other values
        try:
            purchase_price = int(float(self.purchase_price_input.text() or 1))  # Convert to int
            if purchase_price <= 0:
                raise ValueError("Purchase price must be positive")
                    
            profit_percent = int(float(self.profit_percent_input.text() or 100))  # Convert to int
            if profit_percent < 0:
                raise ValueError("Profit percent cannot be negative")
                    
            stock_quantity = int(self.stock_quantity_input.text() or 1)
            if stock_quantity <= 0:
                raise ValueError("Stock quantity must be positive")
            
            # Calculate sale price
            sale_price_input = self.sale_price_input.text().strip()
            if sale_price_input:
                sale_price = int(float(sale_price_input))  # Convert to int
            else:
                sale_price = int(purchase_price + (purchase_price * profit_percent / 100))  # Convert to int
                
            # Add to database
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO items 
                (item_name, barcode, purchase_price, profit_percent, sale_price, stock_quantity, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (item_name, barcode_value, purchase_price, profit_percent, sale_price, stock_quantity, created_at))
            self.conn.commit()
            
            # Add to history table
            self.add_item_to_table(item_name, barcode_value, sale_price, stock_quantity)
            
            # Remove session_items logic and just refresh from DB
            self.load_item_history()
            
            QMessageBox.information(self, "Success", "Item added successfully!")
            
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")
            
    def generate_barcode(self):
        while True:
            barcode_value = str(random.randint(100000000000, 999999999999))
            self.cursor.execute("SELECT COUNT(*) FROM items WHERE barcode=?", (barcode_value,))
            if self.cursor.fetchone()[0] == 0:
                return barcode_value
                
    def generate_barcode_image(self, barcode_value):
        temp_filename = None
        try:
            # Disable TTF fonts in EXE mode
            if getattr(sys, 'frozen', False):
                os.environ['BARCODE_DISABLE_TTF'] = '1'
                
            writer = ImageWriter()
            writer.set_options({
                'module_width': 0.2,
                'module_height': 15,
                'font_size': 0,  # Disable text
                'text_distance': 0,  # Remove text
                'quiet_zone': 6  # Add quiet zone
            })
            
            ean = barcode.get('ean13', barcode_value, writer=writer)
            temp_filename = ean.save('temp_barcode')
            barcode_img = Image.open(temp_filename)
            barcode_img.close()
            return Image.open(temp_filename)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate barcode: {str(e)}")
            return Image.new('RGB', (300, 100), 'white')
        finally:
            if temp_filename and os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except PermissionError:
                    pass

    def preview_label(self):
        if hasattr(self, 'preview_window'):
            self.preview_window.close()
            
        self.cursor.execute("SELECT item_name, barcode, sale_price, stock_quantity FROM items")
        items = [{
            'item_name': row[0],
            'barcode': row[1],
            'sale_price': row[2],
            'stock_quantity': row[3]
        } for row in self.cursor.fetchall()]
        
        if not items:
            QMessageBox.warning(self, "Error", "No items in database to preview!")
            return
            
        # Create preview window
        self.preview_window = QMainWindow()
        self.preview_window.setWindowTitle("Label Preview")
        self.preview_window.setMinimumSize(800, 600)
        
        # Create scroll area for multiple labels
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Create container widget
        container = QWidget()
        self.preview_layout = QVBoxLayout(container)
        self.preview_layout.setAlignment(Qt.AlignTop)
        
        # Generate all labels considering stock quantities
        all_labels = []
        for item in items:
            all_labels.extend([item] * item['stock_quantity'])
            
        # Process labels in pairs
        for i in range(0, len(all_labels), 2):
            items = all_labels[i:i+2]
            dual_label_image = self.generate_dual_label_image(items)
            dual_label_pixmap = QPixmap.fromImage(dual_label_image)
            label_preview = QLabel()
            label_preview.setPixmap(dual_label_pixmap)
            self.preview_layout.addWidget(label_preview)
            self.preview_layout.addSpacing(20)
            
        scroll.setWidget(container)
        self.preview_window.setCentralWidget(scroll)
        self.preview_window.show()
        
    def generate_dual_label_image(self, items):
        # Create image with gap between labels (816x200 pixels for dual 50x25mm @ 203 DPI with 16px gap)
        label_gap_px = 16  # 2mm gap at 203 DPI
        label_width_px = 400  # 50mm at 203 DPI
        dual_label_width = label_width_px * 2 + label_gap_px
        image = Image.new('RGB', (dual_label_width, 200), 'white')
        draw = ImageDraw.Draw(image)
        
        # Load fonts with proper error handling
        try:
            font_bold = ImageFont.truetype(get_embedded_font_path("arialbd.ttf"), 16)
            font_regular = ImageFont.truetype(get_embedded_font_path("arial.ttf"), 12)
            font_large = ImageFont.truetype(get_embedded_font_path("arialbd.ttf"), 14)
        except Exception as e:
            print(f"Font load error: {e}")
            try:
                # Fallback to system fonts
                font_bold = ImageFont.truetype("Helvetica-Bold", 16)
                font_regular = ImageFont.truetype("Helvetica", 12)
                font_large = ImageFont.truetype("Helvetica-Bold", 14)
            except:
                # Final fallback to default font
                font_bold = ImageFont.load_default()
                font_regular = ImageFont.load_default()
                font_large = ImageFont.load_default()
        
        for idx in range(2):
            # Calculate x_offset with gap for second label
            x_offset = idx * label_width_px + (label_gap_px if idx == 1 else 0)
            
            if idx >= len(items):
                continue
                
            item = items[idx]
            
            # Draw item name (top, bold, centered, uppercase)
            item_name = item['item_name'].upper()
            text_width = draw.textlength(item_name, font=font_bold)
            draw.text((x_offset + (400 - text_width) / 2, 10), item_name, font=font_bold, fill='black')
            
            # Generate barcode image (300x80)
            barcode_value = item['barcode']
            barcode_img = self.generate_barcode_image(barcode_value)
            barcode_img = barcode_img.resize((300, 80))
            
            # Paste barcode image (centered)
            barcode_x = x_offset + (400 - 300) // 2
            image.paste(barcode_img, (barcode_x, 50))
            
            # Draw barcode number (below barcode)
            text_width = draw.textlength(barcode_value, font=font_regular)
            draw.text((x_offset + (400 - text_width) / 2, 130), barcode_value, font=font_regular, fill='black')
            
            # Draw sale price
            sale_price = f"Sale Price: ₹{int(item['sale_price'])}"
            text_width = draw.textlength(sale_price, font=font_regular)
            draw.text((x_offset + (400 - text_width) / 2, 150), sale_price, font=font_regular, fill='black')
            
            # Draw company name (bottom, bold)
            company_name = "AUTO GEEK"
            text_width = draw.textlength(company_name, font=font_large)
            draw.text((x_offset + (400 - text_width) / 2, 170), company_name, font=font_large, fill='black')
        
        # Convert to QImage with consistent DPI settings
        image = image.convert("RGBA")
        data = image.tobytes("raw", "RGBA")
        qimage = QImage(data, image.size[0], image.size[1], QImage.Format_RGBA8888)
        qimage.setDotsPerMeterX(int(203 * 39.37))  # 203 DPI
        qimage.setDotsPerMeterY(int(203 * 39.37))
        return qimage
        
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
                dual_label_image = self.generate_dual_label_image(item_pair)
                
                # Save files with counter for duplicates
                base_name = f"{item_pair[0]['item_name']}_{i//2}"
                bmp_path = os.path.join(folders['bmp'], f"{base_name}.bmp")
                png_path = os.path.join(folders['png'], f"{base_name}.png")
                pdf_path = os.path.join(folders['pdf'], f"{base_name}.pdf")
                
                dual_label_image.save(bmp_path, "BMP", dpi=(203, 203))
                dual_label_image.save(png_path, "PNG", dpi=(203, 203))
                
                # PDF needs special handling
                image = Image.open(png_path)
                image.save(pdf_path, "PDF", resolution=203.0)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save label files: {str(e)}")
            return False
        return True
        
    def print_label(self):
        try:
            self.cursor.execute("SELECT item_name, barcode, sale_price, stock_quantity FROM items")
            items = [{
                'item_name': row[0],
                'barcode': row[1],
                'sale_price': row[2],
                'stock_quantity': row[3]
            } for row in self.cursor.fetchall()]
            
            if not items:
                QMessageBox.warning(self, "Error", "No items in database to print!")
                return

            # Generate all labels considering stock quantities
            all_labels = []
            for item in items:
                all_labels.extend([item] * item['stock_quantity'])

            # Create printer with correct settings
            printer = QPrinter(QPrinter.HighResolution)
            printer.setResolution(203)
            printer.setPageSize(QPrinter.Custom)
            printer.setPaperSize(QSizeF(100, 25), QPrinter.Millimeter)  # 100x25mm paper size
            printer.setFullPage(True)
            printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)
            
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter()
                painter.begin(printer)
                
                for i in range(0, len(all_labels), 2):
                    items = all_labels[i:i+2]
                    dual_label_image = self.generate_dual_label_image(items)
                    # Draw at exact 1:1 pixel match (816x200)
                    painter.drawImage(QRectF(0, 0, 816, 200), dual_label_image)
                    if i < len(all_labels) - 2:
                        printer.newPage()
                
                painter.end()
                QMessageBox.information(self, "Success", "Labels printed successfully!")
                self.load_item_history()  # Refresh history after print
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to print labels: {str(e)}")

    def print_all_labels(self):
        try:
            self.cursor.execute("SELECT item_name, barcode, sale_price, stock_quantity FROM items")
            items = [{
                'item_name': row[0],
                'barcode': row[1],
                'sale_price': row[2],
                'stock_quantity': row[3]
            } for row in self.cursor.fetchall()]
            
            if not items:
                QMessageBox.warning(self, "Error", "No items in database to print!")
                return

            # Generate all labels considering stock quantities
            all_labels = []
            for item in items:
                all_labels.extend([item] * item['stock_quantity'])

            # Create printer and dialog
            printer = QPrinter(QPrinter.HighResolution)
            printer.setResolution(203)
            printer.setPageSize(QPrinter.Custom)
            printer.setPaperSize(QSizeF(50, 25), QPrinter.Millimeter)  # Changed to millimeters
            
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter()
                painter.begin(printer)
                
                for i in range(0, len(all_labels), 2):
                    items = all_labels[i:i+2]
                    dual_label_image = self.generate_dual_label_image(items)
                    painter.drawImage(0, 0, dual_label_image)
                    if i < len(all_labels) - 2:
                        printer.newPage()
                
                painter.end()
                QMessageBox.information(self, "Success", "All labels printed successfully!")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to print labels: {str(e)}")

    def get_save_location(self):
        config_file = os.path.expanduser('~/.quicktag_config')
        try:
            with open(config_file, 'r') as f:
                return f.read().strip()
        except:
            # First time - prompt user and save location
            save_dir = QFileDialog.getExistingDirectory(
                self, "Select Default Save Location", 
                os.path.expanduser("~/Documents")
            )
            if save_dir:
                with open(config_file, 'w') as f:
                    f.write(save_dir)
                return save_dir
            return os.path.expanduser("~/Documents")  # Fallback
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
            
    def clear_items(self):
        reply = QMessageBox.question(
            self, 
            "Confirm Clear", 
            "This will permanently delete ALL items from the database. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM items")
                self.conn.commit()
                self.history_table.setRowCount(0)
                self.load_item_history()  # Explicit refresh
                QMessageBox.information(self, "Cleared", "All items have been cleared from the database.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to clear items: {str(e)}")

    def closeEvent(self, event):
        if hasattr(self, 'conn'):
            self.conn.close()
        if hasattr(self, 'preview_window'):
            self.preview_window.close()
        event.accept()

    def load_item_history(self):
        self.history_table.setRowCount(0)
        self.cursor.execute("SELECT item_name, created_at, sale_price, stock_quantity FROM items")
        for item in self.cursor.fetchall():
            self.add_item_to_table(*item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuickTagApp()
    window.show()
    sys.exit(app.exec_())

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_embedded_font(name, size):
    """Load font from embedded resources with fallback support"""
    try:
        # Try loading from PyInstaller resources first
        if getattr(sys, 'frozen', False):
            font_path = os.path.join(sys._MEIPASS, "fonts", name)
            return ImageFont.truetype(font_path, size)
        
        # Try loading from package resources
        font_bytes = pkgutil.get_data(__name__, f"fonts/{name}")
        if font_bytes:
            return ImageFont.truetype(BytesIO(font_bytes), size)
            
        # Fallback to direct file access
        return ImageFont.truetype(f"fonts/{name}", size)
        
    except Exception as e:
        print(f"Error loading font {name}: {e}")
        try:
            # Try system fonts as fallback
            return ImageFont.truetype(name, size)
        except:
            # Final fallback to default font
            return ImageFont.load_default()

def get_embedded_font_path(filename):
    """Resolves font path for both development and PyInstaller bundle"""
    try:
        if getattr(sys, 'frozen', False):
            # PyInstaller bundle mode
            base_path = sys._MEIPASS
            font_path = os.path.join(base_path, 'fonts', filename)
            if not os.path.exists(font_path):
                raise FileNotFoundError(f"Font not found in bundle: {font_path}")
        else:
            # Development mode
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', filename)
            if not os.path.exists(font_path):
                raise FileNotFoundError(f"Font not found in development: {font_path}")
        return font_path
    except Exception as e:
        print(f"Font path resolution error: {e}")
        return filename  # Fallback to system font search

   