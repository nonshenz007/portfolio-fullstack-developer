import os
import sys

# Add this before any barcode imports
if getattr(sys, 'frozen', False):
    os.environ['BARCODE_DISABLE_TTF'] = '1'
import sqlite3
import datetime
import random
import shutil
import subprocess
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

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
from PyQt5.QtCore import Qt, QSize, QSizeF, QRectF
import barcode
from barcode.writer import ImageWriter
import openpyxl
from PIL import Image, ImageDraw, ImageFont, ImageWin
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import win32print
import win32ui
import win32con
from io import BytesIO

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
            self.font_bold = QFont("Arial", 16, QFont.Bold)
            self.font_regular = QFont("Arial", 15)
            # Store font sizes as attributes
            self.font_bold_size = 16
            self.font_regular_size = 15
        except:
            # Fallback to system fonts
            font_names = ["Arial", "Helvetica", "San Francisco", ".SF NS Text"]
            self.font_bold = QFont()
            self.font_regular = QFont()
            
            for name in font_names:
                if self.font_bold.exactMatch(): break
                self.font_bold = QFont(name, 16, QFont.Bold)
                self.font_bold_size = 16
                
            for name in font_names:
                if self.font_regular.exactMatch(): break
                self.font_regular = QFont(name, 15)
                self.font_regular_size = 15
        
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
        # Close existing preview window if it exists
        if hasattr(self, 'preview_window'):
            self.preview_window.close()
            del self.preview_window
        
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
            
        # Create new preview window
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
            
            # Convert PIL Image to QPixmap properly
            img_byte_arr = BytesIO()
            dual_label_image.save(img_byte_arr, format='PNG')
            qimage = QImage.fromData(img_byte_arr.getvalue())
            dual_label_pixmap = QPixmap.fromImage(qimage)
            
            label_preview = QLabel()
            label_preview.setPixmap(dual_label_pixmap)
            self.preview_layout.addWidget(label_preview)
            self.preview_layout.addSpacing(20)
            
        scroll.setWidget(container)
        self.preview_window.setCentralWidget(scroll)
        self.preview_window.show()
        
    def generate_dual_label_image(self, items):
        # Create image with exact dimensions (816x200 pixels @ 203 DPI)
        image = Image.new('L', (816, 200), 'white')  # 1-bit grayscale
        draw = ImageDraw.Draw(image)
        
        # Load fonts with increased sizes as requested
        try:
            font_item = ImageFont.truetype("arialbd.ttf", 18)  # Item name (18pt)
            font_price = ImageFont.truetype("arialbd.ttf", 23)  # Increased from 20 to 23pt (15% larger)
            font_company = ImageFont.truetype("arialbd.ttf", 16)  # Company (16pt)
        except:
            # Fallback to system fonts
            font_item = ImageFont.load_default()
            font_barcode = ImageFont.load_default()
            font_price = ImageFont.load_default()
            font_company = ImageFont.load_default()
        
        # Fixed vertical positions with reduced spacing
        positions = {
            'item_name': 5,
            'barcode_image': 22,
            'barcode_text': 80,  # Reduced from 95 to 80 (-15px)
            'price_text': 100,   # Reduced from 115 to 100 (-15px)
            'company_text': 135
        }

        for idx in range(2):
            if idx >= len(items):
                continue
                
            item = items[idx]
            x_offset = idx * 400 + 8  # 8px margin inside each label

            # Fixed positions with centered layout (Option A)
            y_item = 10     # Item name position
            y_barcode_img = 35  # Barcode position (resized to 280x55)
            y_price = 100   # Price position
            y_company = 125  # Company position

            # Draw item name (centered horizontally)
            item_name = item['item_name'].upper()
            text_width = draw.textlength(item_name, font=font_item)
            draw.text((x_offset + (384 - text_width)/2, y_item),
                     item_name, font=font_item, fill='black')

            # Barcode image (resized to 280x55 for better fit)
            barcode_img = self.generate_barcode_image(item['barcode'])
            barcode_img = barcode_img.resize((280, 55), Image.Resampling.NEAREST)
            image.paste(barcode_img, (x_offset + 42, y_barcode_img))

            # Price (barcode number removed)
            price_text = f"Sale Price: ₹{item['sale_price']}"
            text_width = draw.textlength(price_text, font=font_price)
            draw.text((x_offset + (384 - text_width)/2, y_price),
                     price_text, font=font_price, fill='black')

            # Company name
            company_text = "AUTO GEEK"
            text_width = draw.textlength(company_text, font=font_company)
            draw.text((x_offset + (384 - text_width)/2, y_company),
                     company_text, font=font_company, fill='black')
    
        return image
        
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

            # Process labels in pairs
            for i in range(0, len(all_labels), 2):
                items = all_labels[i:i+2]
                dual_label_image = self.generate_dual_label_image(items)
                
                # Save as temporary PNG file
                temp_path = "last_preview.png"
                dual_label_image.save(temp_path, "PNG", dpi=(203, 203))
                self.last_barcode_png = temp_path  # Store for reprinting
                
                # Print using the new method
                self.print_image_via_dialog(temp_path)
                    
            QMessageBox.information(self, "Success", "All labels printed successfully!")
                
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

            # Process labels in pairs
            for i in range(0, len(all_labels), 2):
                items = all_labels[i:i+2]
                dual_label_image = self.generate_dual_label_image(items)
                
                # Save as temporary PNG file
                temp_path = "last_preview.png"
                dual_label_image.save(temp_path, "PNG", dpi=(203, 203))
                self.last_barcode_png = temp_path  # Store for reprinting
                
                # Print using the new method
                self.print_image_via_dialog(temp_path)
                    
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

    def print_image_via_dialog(self, image_path):
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setResolution(203)  # Exact DPI
            printer.setPaperSize(QSizeF(100, 25), QPrinter.Millimeter)  # Dual label size
            printer.setFullPage(True)
            printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)
            
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QDialog.Accepted:
                painter = QPainter(printer)
                
                # Load image with exact dimensions
                img = Image.open(image_path)
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PNG', dpi=(203, 203))
                qimage = QImage.fromData(img_byte_arr.getvalue())
                
                # Draw at exact size (816x200 pixels)
                painter.drawImage(QRect(0, 0, 816, 200), qimage)
                painter.end()
                
                QMessageBox.information(self, "Success", "Label printed successfully")
            else:
                QMessageBox.warning(self, "Cancelled", "Printing was cancelled")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Print failed: {str(e)}")

    def print_image_via_dialog(self, image_path):
        try:
            # Save as BMP first (thermal printers prefer BMP)
            bmp_path = os.path.splitext(image_path)[0] + '.bmp'
            img = Image.open(image_path)
            img.save(bmp_path, 'BMP')
            
            # Get image dimensions as integers
            width, height = img.size
            width = int(width)
            height = int(height)
            
            # Use Windows printing API
            printer_name = win32print.GetDefaultPrinter()
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(printer_name)
            hDC.StartDoc("Label Print")
            hDC.StartPage()
            
            # Load the BMP using ImageWin.Dib
            dib = ImageWin.Dib(img)
            dib.draw(hDC.GetHandleOutput(), (0, 0, width, height))
            
            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()
            
            # Clean up
            if os.path.exists(bmp_path):
                os.remove(bmp_path)
                
            return True
            
        except Exception as ex:
            QMessageBox.warning(self, "Print Error", f"Unable to print:\n{ex}")
            return False
        return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuickTagApp()
    window.show()
    sys.exit(app.exec_())

   