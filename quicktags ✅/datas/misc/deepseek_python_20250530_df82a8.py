import os
import sys
import sqlite3
import datetime
import random
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget,
                            QTableWidgetItem, QHeaderView, QGroupBox, QFrame, QSpacerItem,
                            QGridLayout)
from PyQt5.QtGui import QFont, QIcon, QFontDatabase
from PyQt5.QtCore import Qt, QTimer

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
        
        # Initialize database and load data
        self.setup_database()
        self.load_item_history()
        
        # Load fonts with error handling
        self.load_fonts()

    def create_sidebar(self):
        """Create the modern left sidebar"""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(15)
        
        # Title section
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
                color: #64748b;
                margin-bottom: 30px;
            }
        """)
        
        # Navigation buttons
        self.add_button = self.create_nav_button("➕ Add Item", self.add_item)
        self.preview_button = self.create_nav_button("👁 Preview", self.preview_barcode)
        self.print_button = self.create_nav_button("🖨 Print", self.print_barcode)
        self.export_button = self.create_nav_button("📁 Export Excel", self.export_to_excel)
        
        # Spacer and success label
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        self.success_label = QLabel("✓ Item added")
        self.success_label.setAlignment(Qt.AlignCenter)
        self.success_label.setStyleSheet("""
            QLabel {
                background-color: #e6f7ec;
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

    def create_nav_button(self, text, callback):
        """Create styled navigation buttons"""
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
                color: #334155;
                border-radius: 8px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        button.clicked.connect(callback)
        return button

    def create_main_content(self):
        """Create the main content area"""
        content = QWidget()
        content.setStyleSheet("background-color: #f9fafb;")
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Create form
        self.create_product_form(content_layout)
        
        # Create history table
        self.create_history_table(content_layout)
        
        self.main_layout.addWidget(content)

    def create_product_form(self, parent_layout):
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
                color: #1e293b;
                font-size: 16px;
            }
        """)
        
        # Use grid layout for 2-column form
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Input fields
        self.item_name_input = self.create_form_input("Item Name (required)")
        self.purchase_price_input = self.create_form_input("Purchase Price (default: 1)", "1")
        self.profit_percent_input = self.create_form_input("Profit % (optional, overrides %)", "100")
        self.sale_price_input = self.create_form_input("Sale Price (default: 1)", "1")
        
        # Add fields to grid
        form_layout.addWidget(self.item_name_input, 0, 0)
        form_layout.addWidget(self.profit_percent_input, 0, 1)
        form_layout.addWidget(self.purchase_price_input, 1, 0)
        form_layout.addWidget(self.sale_price_input, 1, 1)
        
        # Add button
        add_btn = QPushButton("Add Item")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        add_btn.clicked.connect(self.add_item)
        
        # Add button to layout spanning 2 columns
        form_layout.addWidget(add_btn, 2, 0, 1, 2)
        
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
                color: #1e293b;
                font-size: 16px;
                margin-bottom: 5px;
            }
        """)
        
        self.history_table = QTableWidget(0, 6)  # 6 columns (name, date, price, stock, edit, delete)
        self.history_table.setHorizontalHeaderLabels(["Item Name", "Date Added", "Sale Price", "Stock", "", ""])
        
        # Table styling
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                gridline-color: #e2e8f0;
                font-size: 14px;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #4b5563;
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
        self.history_table.setColumnWidth(0, 250)  # Item Name
        self.history_table.setColumnWidth(1, 150)  # Date Added
        self.history_table.setColumnWidth(2, 100)  # Sale Price
        self.history_table.setColumnWidth(3, 80)   # Stock
        self.history_table.setColumnWidth(4, 80)   # Edit
        self.history_table.setColumnWidth(5, 80)   # Delete
        
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
        edit_btn = self.create_table_button("✏️ Edit", "#10b981", self.edit_item, item_name)
        delete_btn = self.create_table_button("🗑 Delete", "#ef4444", self.delete_item, item_name)
        reprint_btn = self.create_table_button("🔁 Reprint", "#3b82f6", self.reprint_item, item_name)
        
        # Create container for buttons
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(5)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(reprint_btn)
        
        # Add buttons to last two columns (spanning both)
        self.history_table.setCellWidget(row_position, 4, btn_container)
        self.history_table.setSpan(row_position, 4, 1, 2)

    def create_table_button(self, text, color, callback, item_name):
        """Helper to create styled action buttons for table"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px 8px;
                border-radius: 6px;
                font-size: 13px;
                min-width: 30px;
            }}
            QPushButton:hover {{
                background-color: {'#0d9488' if color == '#10b981' else 
                                 '#dc2626' if color == '#ef4444' else 
                                 '#2563eb'};
            }}
        """)
        btn.clicked.connect(lambda: callback(item_name))
        return btn

    # ====== Core Functionality (unchanged from original) ======
    
    def setup_database(self):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect('quicktag.db')
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
        """Load fonts with error handling for EXE compatibility"""
        try:
            if getattr(sys, 'frozen', False):
                # Running in EXE mode - use system fonts
                self.font_bold = QFont("Arial", 12, QFont.Bold)
                self.font_regular = QFont("Arial", 11)
            else:
                # Development mode - try to load custom font
                font_id = QFontDatabase.addApplicationFont("arial.ttf")
                if font_id != -1:
                    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                    self.font_bold = QFont(font_family, 12, QFont.Bold)
                    self.font_regular = QFont(font_family, 11)
                else:
                    self.font_bold = QFont("Arial", 12, QFont.Bold)
                    self.font_regular = QFont("Arial", 11)
        except Exception as e:
            self.font_bold = QFont("Arial", 12, QFont.Bold)
            self.font_regular = QFont("Arial", 11)

    def add_item(self):
        """Add new item to database"""
        item_name = self.item_name_input.text().strip()
        if not item_name:
            QMessageBox.warning(self, "Error", "Item Name is required!")
            return
            
        try:
            # Generate barcode
            barcode_value = str(random.randint(100000000000, 999999999999))
            
            # Get other values
            purchase_price = int(float(self.purchase_price_input.text() or 1))
            profit_percent = int(float(self.profit_percent_input.text() or 100))
            stock_quantity = int(self.stock_quantity_input.text() or 1)
            
            # Calculate sale price
            sale_price_input = self.sale_price_input.text().strip()
            if sale_price_input:
                sale_price = int(float(sale_price_input))
            else:
                sale_price = int(purchase_price + (purchase_price * profit_percent / 100))
                
            # Add to database
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO items 
                (item_name, barcode, purchase_price, profit_percent, sale_price, stock_quantity, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (item_name, barcode_value, purchase_price, profit_percent, sale_price, stock_quantity, created_at))
            self.conn.commit()
            
            # Add to table and show success
            self.add_item_to_table(item_name, created_at, sale_price, stock_quantity)
            self.success_label.show()
            QTimer.singleShot(3000, self.success_label.hide)
            
            # Clear inputs
            self.item_name_input.clear()
            self.purchase_price_input.setText("1")
            self.profit_percent_input.setText("100")
            self.sale_price_input.setText("1")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            QMessageBox.warning(self, "Database Error", f"Failed to add item: {str(e)}")
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {str(e)}")

    def edit_item(self, item_name):
        """Edit existing item"""
        try:
            self.cursor.execute(
                "SELECT item_name, barcode, purchase_price, profit_percent, sale_price, stock_quantity FROM items WHERE item_name=?", 
                (item_name,)
            )
            item_data = self.cursor.fetchone()
            
            if not item_data:
                QMessageBox.warning(self, "Error", f"Item '{item_name}' not found!")
                return
                
            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit {item_name}")
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
            
            # Add buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            
            # Add to layout
            layout.addLayout(form_layout)
            layout.addWidget(button_box)
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                # Validate inputs
                new_name = item_name_input.text().strip()
                new_barcode = barcode_input.text().strip()
                new_purchase_price = int(float(purchase_price_input.text()))
                new_profit_percent = int(float(profit_percent_input.text()))
                new_sale_price = int(float(sale_price_input.text()))
                new_stock_quantity = int(stock_quantity_input.text())
                
                # Update database
                self.cursor.execute('''
                    UPDATE items SET 
                    item_name=?, barcode=?, purchase_price=?, profit_percent=?, 
                    sale_price=?, stock_quantity=?
                    WHERE item_name=?
                ''', (new_name, new_barcode, new_purchase_price, new_profit_percent,
                     new_sale_price, new_stock_quantity, item_name))
                self.conn.commit()
                
                # Refresh table
                self.load_item_history()
                QMessageBox.information(self, "Success", "Item updated successfully!")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit item: {str(e)}")

    def delete_item(self, item_name):
        """Delete item from database"""
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
                QMessageBox.information(self, "Success", "Item deleted successfully!")
            except sqlite3.Error as e:
                self.conn.rollback()
                QMessageBox.warning(self, "Error", f"Failed to delete item: {str(e)}")

    def reprint_item(self, item_name):
        """Reprint item label"""
        try:
            self.cursor.execute(
                "SELECT item_name, barcode, sale_price FROM items WHERE item_name=?", 
                (item_name,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                QMessageBox.warning(self, "Error", f"Item '{item_name}' not found!")
                return
                
            name, barcode, price = result
            
            # Ask for print quantity
            count, ok = QInputDialog.getInt(
                self, "Reprint", "Number of labels to print (Max 2):", 1, 1, 2
            )
            if not ok:
                return
                
            # Here you would implement your actual printing logic
            QMessageBox.information(
                self, 
                "Reprint", 
                f"Would print {count} label(s) for:\n\nItem: {name}\nBarcode: {barcode}\nPrice: Rs. {price}"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to reprint: {str(e)}")

    def preview_barcode(self):
        """Preview barcode label"""
        item_name = self.item_name_input.text().strip()
        if not item_name:
            QMessageBox.warning(self, "Error", "Please enter an item name first!")
            return
            
        QMessageBox.information(
            self, 
            "Preview", 
            f"Would show preview for:\n\nItem: {item_name}\nGenerated barcode"
        )

    def print_barcode(self):
        """Print barcode label"""
        item_name = self.item_name_input.text().strip()
        if not item_name:
            QMessageBox.warning(self, "Error", "Please enter an item name first!")
            return
            
        QMessageBox.information(
            self, 
            "Print", 
            f"Would print label for:\n\nItem: {item_name}\nGenerated barcode"
        )

    def export_to_excel(self):
        """Export data to Excel"""
        try:
            # Here you would implement your actual Excel export logic
            QMessageBox.information(
                self, 
                "Export", 
                "Would export current data to Excel file"
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export: {str(e)}")

    def load_item_history(self):
        """Load items from database into table"""
        self.history_table.setRowCount(0)
        try:
            self.cursor.execute("SELECT item_name, created_at, sale_price, stock_quantity FROM items")
            for item in self.cursor.fetchall():
                self.add_item_to_table(*item)
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Error", f"Failed to load items: {str(e)}")

    def closeEvent(self, event):
        """Clean up on window close"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuickTagApp()
    window.show()
    sys.exit(app.exec_())