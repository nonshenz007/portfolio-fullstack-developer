"""
Main Application Window for Veridoc Universal

This module provides the primary PySide6 application window with drag-and-drop
functionality, format selection, and batch processing capabilities.
"""

import os
from typing import List, Optional
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QFileDialog, QMessageBox,
                              QProgressBar, QTextEdit, QSplitter, QGroupBox,
                              QListWidget, QListWidgetItem, QFrame)
from PySide6.QtCore import Qt, Signal, QThread, Slot
from PySide6.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent

from .format_selector import FormatSelector
from .image_preview import ImagePreview
from .validation_checklist import ValidationChecklist
from .batch_processor import BatchProcessor
from engine.veridoc_engine import VeriDocEngine


class MainWindow(QMainWindow):
    """Main application window for Veridoc Universal."""
    
    # Signals for image processing
    images_selected = pyqtSignal(list)  # List of image file paths
    format_changed = pyqtSignal(str, dict)  # format_key, format_rules
    
    def __init__(self, config_manager, parent=None):
        """
        Initialize the main application window.
        
        Args:
            config_manager: ConfigManager instance for loading configuration
            parent: Parent widget
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.selected_images = []
        self.current_format = None
        self.current_format_rules = {}
        
        self._setup_ui()
        self._setup_drag_drop()
        self._connect_signals()
        
    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle("VeriDoc Universal - Professional Photo Verification")
        # Perfect dimensions using mathematical principles
        self.setMinimumSize(1440, 900)
        self.resize(1600, 1000)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background: transparent;")
        
        # Main layout with perfect spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the main container
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QHBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left panel - Format selection and controls
        left_panel = self._create_left_panel()
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(380)
        container_layout.addWidget(left_panel)
        
        # Right panel - Main content area
        right_panel = self._create_right_panel()
        container_layout.addWidget(right_panel, 1)
        
        main_layout.addWidget(container)
        
        # Status bar
        self.statusBar().showMessage("Ready - Select a format and import images")
        
    def _create_left_panel(self) -> QWidget:
        """Create the left control panel."""
        panel = QWidget()
        panel.setObjectName("leftPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Modern Header with Icon
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setSpacing(12)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo and brand container
        brand_container = QHBoxLayout()
        brand_container.setSpacing(12)
        
        # App icon (using emoji for now, can be replaced with actual logo)
        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3B82F6, stop:1 #60A5FA);
                border-radius: 12px;
                padding: 8px;
                min-width: 48px;
                max-width: 48px;
                min-height: 48px;
                max-height: 48px;
            }
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        brand_container.addWidget(icon_label)
        
        # Brand text
        brand_text_container = QVBoxLayout()
        brand_text_container.setSpacing(4)
        
        title_label = QLabel("VeriDoc")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignLeft)
        brand_text_container.addWidget(title_label)
        
        subtitle_label = QLabel("Professional Photo Verification")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignLeft)
        brand_text_container.addWidget(subtitle_label)
        
        brand_container.addLayout(brand_text_container)
        brand_container.addStretch()
        
        header_layout.addLayout(brand_container)
        layout.addWidget(header_container)

        # Modern Drop Zone
        self.drop_zone_container = QFrame()
        self.drop_zone_container.setObjectName("dropZone")
        self.drop_zone_container.setFixedHeight(140)
        dz_layout = QVBoxLayout(self.drop_zone_container)
        dz_layout.setContentsMargins(24, 24, 24, 24)
        dz_layout.setSpacing(12)
        
        # Drop zone icon with modern styling
        dz_icon_container = QWidget()
        dz_icon_container.setFixedSize(56, 56)
        dz_icon_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(59, 130, 246, 0.1), 
                    stop:1 rgba(16, 185, 129, 0.1));
                border-radius: 28px;
                border: 2px dashed rgba(59, 130, 246, 0.3);
            }
        """)
        
        dz_icon_layout = QVBoxLayout(dz_icon_container)
        dz_icon_layout.setContentsMargins(0, 0, 0, 0)
        
        dz_icon = QLabel("📤")
        dz_icon.setAlignment(Qt.AlignCenter)
        dz_icon.setStyleSheet("font-size: 24px; background: transparent; border: none;")
        dz_icon_layout.addWidget(dz_icon)
        
        # Center the icon
        dz_icon_center = QHBoxLayout()
        dz_icon_center.addStretch()
        dz_icon_center.addWidget(dz_icon_container)
        dz_icon_center.addStretch()
        dz_layout.addLayout(dz_icon_center)
        
        dz_label = QLabel("Drag & Drop Images Here")
        dz_label.setAlignment(Qt.AlignCenter)
        dz_label.setStyleSheet("color: #475569; font-size: 16px; font-weight: 600; background: transparent; border: none;")
        dz_layout.addWidget(dz_label)
        
        dz_sublabel = QLabel("or click Import below")
        dz_sublabel.setAlignment(Qt.AlignCenter)
        dz_sublabel.setStyleSheet("color: #64748B; font-size: 14px; background: transparent; border: none;")
        dz_layout.addWidget(dz_sublabel)
        
        layout.addWidget(self.drop_zone_container)
        
        # Format selection section
        format_section = QGroupBox("Select Government Format")
        format_section.setStyleSheet("QGroupBox { font-weight: 600; color: #1E293B; }")
        format_layout = QVBoxLayout(format_section)
        format_layout.setSpacing(12)
        
        format_label = QLabel("Choose the target government format")
        format_label.setStyleSheet("color: #64748B; font-size: 13px; margin-bottom: 4px;")
        format_layout.addWidget(format_label)
        
        self.format_selector = FormatSelector(self.config_manager)
        format_layout.addWidget(self.format_selector)
        
        self.auto_detect_btn = QPushButton("Auto-detect Format")
        self.auto_detect_btn.setEnabled(False)
        format_layout.addWidget(self.auto_detect_btn)
        
        layout.addWidget(format_section)
        
        # Format requirements display
        requirements_section = QGroupBox("Format Requirements")
        requirements_section.setStyleSheet("QGroupBox { font-weight: 600; color: #1E293B; }")
        requirements_layout = QVBoxLayout(requirements_section)
        
        self.requirements_text = QLabel("Select a format to see requirements")
        self.requirements_text.setStyleSheet("color: #64748B; font-size: 12px; line-height: 1.5;")
        self.requirements_text.setWordWrap(True)
        self.requirements_text.setAlignment(Qt.AlignTop)
        requirements_layout.addWidget(self.requirements_text)
        
        layout.addWidget(requirements_section)
        
        # Import section
        import_section = QGroupBox("Import Images")
        import_section.setStyleSheet("QGroupBox { font-weight: 600; color: #1E293B; }")
        import_layout = QVBoxLayout(import_section)
        import_layout.setSpacing(8)
        
        import_desc = QLabel("Drag & drop images or use buttons below")
        import_desc.setStyleSheet("color: #64748B; font-size: 13px; margin-bottom: 8px;")
        import_layout.addWidget(import_desc)
        
        # Import buttons
        self.import_files_btn = QPushButton("Import Files...")
        import_layout.addWidget(self.import_files_btn)
        
        self.import_folder_btn = QPushButton("Import Folder...")
        import_layout.addWidget(self.import_folder_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setEnabled(False)
        self.clear_btn.setStyleSheet("QPushButton { color: #EF4444; }")
        import_layout.addWidget(self.clear_btn)
        
        layout.addWidget(import_section)
        
        # Processing section
        process_section = QGroupBox("Processing")
        process_section.setStyleSheet("QGroupBox { font-weight: 600; color: #1E293B; }")
        process_layout = QVBoxLayout(process_section)
        process_layout.setSpacing(12)
        
        self.process_btn = QPushButton("Process Images")
        self.process_btn.setObjectName("primaryBtn")
        self.process_btn.setMinimumHeight(44)
        self.process_btn.setEnabled(False)
        process_layout.addWidget(self.process_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        process_layout.addWidget(self.progress_bar)
        
        layout.addWidget(process_section)
        
        # Activity log
        log_section = QGroupBox("Activity Log")
        log_section.setStyleSheet("QGroupBox { font-weight: 600; color: #1E293B; }")
        log_layout = QVBoxLayout(log_section)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: 'SF Mono', 'Monaco', 'Consolas', monospace; font-size: 11px;")
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_section)
        
        # Push everything to top
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create the right panel for image preview and validation."""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create premium content container
        content_container = QWidget()
        content_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95), 
                    stop:0.5 rgba(248, 250, 252, 0.98),
                    stop:1 rgba(255, 255, 255, 0.95));
                border-radius: 20px;
                border: 1px solid rgba(226, 232, 240, 0.6);
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
            }
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget with custom styling
        from PyQt5.QtWidgets import QTabWidget
        
        self.tab_widget = QTabWidget()
        
        # Preview tab
        preview_tab = self._create_preview_tab()
        self.tab_widget.addTab(preview_tab, "Preview")
        
        # Batch Processing tab
        self.batch_processor = BatchProcessor(self.config_manager)
        self.tab_widget.addTab(self.batch_processor, "⚙️  Batch Processing")
        
        content_layout.addWidget(self.tab_widget)
        layout.addWidget(content_container)
        
        return panel
    
    def _create_preview_tab(self) -> QWidget:
        """Create the preview and validation tab content."""
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(tab)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Left side - Image content (enhanced width)
        left_side = self._create_preview_panel()
        layout.addWidget(left_side, 3)  # 60% of the space
        
        # Right side - Validation status (enhanced width)
        right_side = self._create_validation_panel()
        layout.addWidget(right_side, 2)  # 40% of the space
        
        return tab
    
    def _create_preview_panel(self) -> QWidget:
        """Create the image preview panel."""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Modern Selected Images section
        images_section = QWidget()
        images_section.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
            }
        """)
        images_layout = QVBoxLayout(images_section)
        images_layout.setSpacing(16)
        images_layout.setContentsMargins(20, 20, 20, 20)
        
        # Modern section header with icon
        images_header = QHBoxLayout()
        images_header.setSpacing(12)
        
        # Header icon
        header_icon = QLabel("📷")
        header_icon.setStyleSheet("""
            QLabel {
                font-size: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(59, 130, 246, 0.1), 
                    stop:1 rgba(16, 185, 129, 0.1));
                border-radius: 8px;
                padding: 8px;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
            }
        """)
        header_icon.setAlignment(Qt.AlignCenter)
        images_header.addWidget(header_icon)
        
        # Header text container
        header_text_container = QVBoxLayout()
        header_text_container.setSpacing(2)
        
        images_title = QLabel("Selected Images")
        images_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        header_text_container.addWidget(images_title)
        
        self.image_count_label = QLabel("No images selected")
        self.image_count_label.setStyleSheet("color: #64748B; font-size: 14px; font-weight: 500;")
        header_text_container.addWidget(self.image_count_label)
        
        images_header.addLayout(header_text_container)
        images_header.addStretch()
        
        images_layout.addLayout(images_header)
        
        # Image list
        self.image_list = QListWidget()
        self.image_list.setMaximumHeight(120)
        self.image_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid rgba(148, 163, 184, 0.1);
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                background: transparent;
                border: 1px solid rgba(148, 163, 184, 0.1);
                border-radius: 6px;
                padding: 8px 12px;
                margin: 2px;
                color: #1E293B;
            }
            QListWidget::item:selected {
                background: rgba(37, 99, 235, 0.1);
                border-color: #2563EB;
                color: #2563EB;
            }
            QListWidget::item:hover {
                background: rgba(148, 163, 184, 0.05);
            }
        """)
        images_layout.addWidget(self.image_list)
        
        layout.addWidget(images_section)
        
        # Modern Image Preview section
        preview_section = QWidget()
        preview_section.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
            }
        """)
        preview_layout = QVBoxLayout(preview_section)
        preview_layout.setSpacing(20)
        preview_layout.setContentsMargins(20, 20, 20, 20)
        
        # Modern preview header with controls
        preview_header = QHBoxLayout()
        preview_header.setSpacing(16)
        
        # Header with icon
        header_container = QHBoxLayout()
        header_container.setSpacing(12)
        
        # Preview icon
        preview_icon = QLabel("🖼️")
        preview_icon.setStyleSheet("""
            QLabel {
                font-size: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(59, 130, 246, 0.1), 
                    stop:1 rgba(16, 185, 129, 0.1));
                border-radius: 8px;
                padding: 8px;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
            }
        """)
        preview_icon.setAlignment(Qt.AlignCenter)
        header_container.addWidget(preview_icon)
        
        preview_title = QLabel("Image Preview")
        preview_title.setStyleSheet("color: #0F172A; font-size: 18px; font-weight: 700;")
        header_container.addWidget(preview_title)
        
        preview_header.addLayout(header_container)
        preview_header.addStretch()
        
        # SPEC core button with modern styling
        self.core_process_btn = QPushButton("⚡ Process with SPEC Core")
        self.core_process_btn.setEnabled(False)
        self.core_process_btn.setObjectName("primaryBtn")
        preview_header.addWidget(self.core_process_btn)
        
        preview_layout.addLayout(preview_header)
        
        # Image preview widget with enhanced styling
        self.image_preview = ImagePreview()
        self.image_preview.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 16px;
                border: 2px solid rgba(226, 232, 240, 0.8);
                min-height: 400px;
            }
        """)
        preview_layout.addWidget(self.image_preview, 1)
        
        # SPEC core result with premium styling
        self.core_result_label = QLabel("")
        self.core_result_label.setWordWrap(True)
        self.core_result_label.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                padding: 16px 20px;
                border: 2px solid rgba(59, 130, 246, 0.2);
                font-size: 14px;
                font-weight: 500;
                line-height: 1.5;
                margin-top: 16px;
            }
        """)
        self.core_result_label.hide()  # Hidden by default
        preview_layout.addWidget(self.core_result_label)
        
        layout.addWidget(preview_section, 1)
        
        return panel
    
    def _create_validation_panel(self) -> QWidget:
        """Create the validation status panel."""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(panel)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Use the existing validation checklist but wrap it
        self.validation_checklist = ValidationChecklist()
        self.validation_checklist.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        layout.addWidget(self.validation_checklist)
        
        return panel
    
    def _setup_drag_drop(self):
        """Enable drag and drop functionality."""
        self.setAcceptDrops(True)
        
        # Make the image list widget accept drops too
        self.image_list.setAcceptDrops(True)
        self.image_list.dragEnterEvent = self.dragEnterEvent
        self.image_list.dropEvent = self.dropEvent
    
    def _connect_signals(self):
        """Connect widget signals to handlers."""
        # Format selector signals
        self.format_selector.format_changed.connect(self._on_format_changed)
        
        # Button signals
        self.import_files_btn.clicked.connect(self._import_files)
        self.import_folder_btn.clicked.connect(self._import_folder)
        self.clear_btn.clicked.connect(self._clear_images)
        self.process_btn.clicked.connect(self._process_images)
        self.auto_detect_btn.clicked.connect(self._auto_detect_format)
        self.core_process_btn.clicked.connect(self._process_current_image_core)
        
        # Image list signals
        self.image_list.itemSelectionChanged.connect(self._on_image_selection_changed)
        
        # Image preview signals
        self.image_preview.image_clicked.connect(self._on_image_clicked)
        
        # Validation checklist signals
        self.validation_checklist.item_clicked.connect(self._on_validation_item_clicked)
        self.validation_checklist.refresh_requested.connect(self._on_validation_refresh)
        
        # Batch processor signals
        self.batch_processor.processing_started.connect(self._on_batch_processing_started)
        self.batch_processor.processing_completed.connect(self._on_batch_processing_completed)
        self.batch_processor.processing_cancelled.connect(self._on_batch_processing_cancelled)
        
        # Initialize core button state
        self._update_core_button_state()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            # Check if any of the URLs are image files
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if self._is_supported_image(file_path):
                        event.acceptProposedAction()
                        return
        event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        if event.mimeData().hasUrls():
            file_paths = []
            urls = event.mimeData().urls()
            
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if os.path.isfile(file_path) and self._is_supported_image(file_path):
                        file_paths.append(file_path)
                    elif os.path.isdir(file_path):
                        # If it's a directory, scan for images
                        dir_images = self._scan_directory_for_images(file_path)
                        file_paths.extend(dir_images)
            
            if file_paths:
                self._add_images(file_paths)
                event.acceptProposedAction()
            else:
                self._show_message("No supported image files found in the dropped items.", 
                                 "Warning", QMessageBox.Warning)
        
        event.ignore()
    
    def _is_supported_image(self, file_path: str) -> bool:
        """Check if a file is a supported image format."""
        try:
            supported_formats = self.config_manager.get_global_setting('supported_input_formats', [])
            
            if not supported_formats:
                supported_formats = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
            
            file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            return file_ext in supported_formats
        except:
            # Fallback to common image formats
            common_formats = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
            file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            return file_ext in common_formats
    
    def _scan_directory_for_images(self, directory: str) -> List[str]:
        """Scan a directory for supported image files."""
        image_files = []
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._is_supported_image(file_path):
                        image_files.append(file_path)
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return image_files
    
    @pyqtSlot(str, dict)
    def _on_format_changed(self, format_key: str, format_rules: dict):
        """Handle format selection change."""
        self.current_format = format_key
        self.current_format_rules = format_rules
        
        # Update status
        display_name = format_rules.get('display_name', format_key)
        self.statusBar().showMessage(f"Format: {display_name} - Ready to process images")
        
        # Update format requirements display
        self._update_format_requirements(format_rules)
        
        # Enable process button if images are selected
        self._update_process_button_state()
        
        # Update validation checklist with new format
        self.validation_checklist.set_format(format_key, format_rules)
        
        # Update batch processor with new format
        if self.selected_images:
            self.batch_processor.set_batch_data(self.selected_images, format_key, format_rules)
        
        # Emit signal for other components
        self.format_changed.emit(format_key, format_rules)
        
        # Log format change
        self._log_message(f"Selected format: {display_name}")
        
        # Re-validate current image if one is selected
        if self.image_preview.get_current_image_path():
            self._validate_current_image()
        # Update core button state
        self._update_core_button_state()
    
    def _update_format_requirements(self, format_rules: dict):
        """Update the format requirements display."""
        if not format_rules:
            self.requirements_text.setText("Select a format to see requirements")
            return
        
        requirements = []
        
        # Dimensions
        dims = format_rules.get('dimensions', {})
        if dims.get('width') and dims.get('height'):
            requirements.append(f"Dimensions: {dims['width']} × {dims['height']} pixels")
        
        # Background
        bg = format_rules.get('background', {})
        if bg.get('color'):
            requirements.append(f"Background: {bg['color'].replace('_', ' ').title()}")
        
        # Face requirements
        face = format_rules.get('face_requirements', {})
        if face.get('height_ratio'):
            min_h, max_h = face['height_ratio']
            requirements.append(f"Face height ratio: {min_h:.0%} - {max_h:.0%}")
        
        # File specs
        specs = format_rules.get('file_specs', {})
        if specs.get('quality'):
            requirements.append(f"JPEG Quality: {specs['quality']}")
        if specs.get('max_size_mb'):
            requirements.append(f"Max file size: {specs['max_size_mb']} MB")
        
        # Quality thresholds
        quality = format_rules.get('quality_thresholds', {})
        if quality.get('min_brightness'):
            requirements.append(f"Brightness: {quality['min_brightness']}-{quality.get('max_brightness', 200)}")
        
        requirements_text = "\n".join(requirements) if requirements else "No specific requirements available"
        self.requirements_text.setText(requirements_text)
    
    def _import_files(self):
        """Open file dialog to import image files."""
        try:
            supported_formats = self.config_manager.get_global_setting('supported_input_formats', [])
            if not supported_formats:
                supported_formats = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        except:
            supported_formats = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        
        # Create file filter string
        filter_parts = []
        for fmt in supported_formats:
            filter_parts.append(f"*.{fmt}")
        
        file_filter = f"Image files ({' '.join(filter_parts)});;All files (*.*)"
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image Files",
            "",
            file_filter
        )
        
        if files:
            self._add_images(files)
    
    def _import_folder(self):
        """Open folder dialog to import all images from a directory."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder Containing Images",
            ""
        )
        
        if folder:
            image_files = self._scan_directory_for_images(folder)
            if image_files:
                self._add_images(image_files)
                self._log_message(f"Imported {len(image_files)} images from folder: {folder}")
            else:
                self._show_message("No supported image files found in the selected folder.", 
                                 "Information", QMessageBox.Information)
    
    def _add_images(self, file_paths: List[str]):
        """Add image files to the selection list."""
        added_count = 0
        
        for file_path in file_paths:
            # Avoid duplicates
            if file_path not in self.selected_images:
                self.selected_images.append(file_path)
                
                # Add to list widget
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.UserRole, file_path)
                item.setToolTip(file_path)
                self.image_list.addItem(item)
                
                added_count += 1
        
        if added_count > 0:
            self._update_image_count()
            self._update_process_button_state()
            self._log_message(f"Added {added_count} new images")
        
        # Update batch processor with new images
        if self.current_format and self.current_format_rules:
            self.batch_processor.set_batch_data(self.selected_images, self.current_format, self.current_format_rules)
        
        # Emit signal
        self.images_selected.emit(self.selected_images.copy())
    
    def _clear_images(self):
        """Clear all selected images."""
        self.selected_images.clear()
        self.image_list.clear()
        self._update_image_count()
        self._update_process_button_state()
        
        # Clear batch processor data
        self.batch_processor.set_batch_data([], self.current_format, self.current_format_rules)
        
        self._log_message("Cleared all images")
    
    def _update_image_count(self):
        """Update the image count label."""
        count = len(self.selected_images)
        if count == 0:
            self.image_count_label.setText("No images selected")
            self.clear_btn.setEnabled(False)
        elif count == 1:
            self.image_count_label.setText("1 image selected")
            self.clear_btn.setEnabled(True)
        else:
            self.image_count_label.setText(f"{count} images selected")
            self.clear_btn.setEnabled(True)
    
    def _update_process_button_state(self):
        """Update the process button enabled state."""
        has_images = len(self.selected_images) > 0
        has_format = self.current_format is not None
        self.process_btn.setEnabled(has_images and has_format)
        self.auto_detect_btn.setEnabled(has_images)
        # Keep core button in sync
        self._update_core_button_state()
    
    def _on_image_selection_changed(self):
        """Handle image list selection change."""
        current_item = self.image_list.currentItem()
        if current_item:
            image_path = current_item.data(Qt.UserRole)
            if image_path and os.path.exists(image_path):
                # Load image in preview
                if self.image_preview.load_image(image_path):
                    self._log_message(f"Loaded image: {os.path.basename(image_path)}")
                    
                    # Perform validation if format is selected
                    if self.current_format and self.current_format_rules:
                        self._validate_current_image()
                    # Update core button state
                    self._update_core_button_state()
                else:
                    self._log_message(f"Failed to load image: {os.path.basename(image_path)}")
        else:
            # Clear preview if no selection
            self.image_preview.clear_image()
            self.validation_checklist.clear_validation()
            # Update core button state
            self._update_core_button_state()
    
    def _process_images(self):
        """Start processing the selected images."""
        if not self.selected_images or not self.current_format:
            return
        
        # Switch to batch processing tab
        self.tab_widget.setCurrentIndex(1)
        
        # Set up batch processor with current data
        self.batch_processor.set_batch_data(
            self.selected_images, 
            self.current_format, 
            self.current_format_rules
        )
        
        # Log the action
        self._log_message(f"Switched to batch processing for {len(self.selected_images)} images with {self.current_format} format")
    
    def _log_message(self, message: str):
        """Add a message to the log display."""
        self.log_text.append(f"[{self._get_timestamp()}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def _show_message(self, message: str, title: str = "Information", 
                     icon: QMessageBox.Icon = QMessageBox.Information):
        """Show a message dialog."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
    
    def get_selected_images(self) -> List[str]:
        """Get the list of selected image file paths."""
        return self.selected_images.copy()
    
    def get_current_format(self) -> Optional[str]:
        """Get the currently selected format."""
        return self.current_format
    
    def get_current_format_rules(self) -> dict:
        """Get the rules for the currently selected format."""
        return self.current_format_rules.copy()
    
    def _validate_current_image(self):
        """Validate the currently selected image."""
        current_image_path = self.image_preview.get_current_image_path()
        if not current_image_path or not self.current_format:
            return
        
        try:
            # Import validation components
            from validation.format_validator import FormatValidator
            
            # Create validator
            validator = FormatValidator(self.config_manager)
            
            # Perform validation
            self._log_message("Running validation...")
            compliance_result, validation_report = validator.validate(current_image_path, self.current_format, return_details=True)
            
            # Update validation checklist
            self.validation_checklist.update_validation_results(validation_report)
            
            # Update image preview with validation overlay
            overlay_data = {
                'compliance_status': {
                    'overall_pass': compliance_result.passes,
                    'score': compliance_result.overall_score
                }
            }
            
            # Add face landmarks if available
            if compliance_result.position_result.face_detected:
                # This would need face landmark data from the face detector
                # For now, we'll skip the overlay
                pass
            
            self.image_preview.set_validation_overlay(overlay_data)
            
            # Log validation result
            status = "PASSED" if compliance_result.passes else "FAILED"
            score = compliance_result.overall_score
            self._log_message(f"Validation {status} - Score: {score:.1f}/100")
            
        except Exception as e:
            self._log_message(f"Validation error: {str(e)}")
            self._show_message(f"Validation failed: {str(e)}", "Error", QMessageBox.Critical)

    def _update_core_button_state(self):
        """Enable SPEC core button only when a current image and format are available."""
        try:
            has_current_image = bool(self.image_preview.get_current_image_path())
        except Exception:
            has_current_image = False
        self.core_process_btn.setEnabled(bool(self.current_format) and has_current_image)

    def _get_core_rules_path(self, format_key: Optional[str]) -> str:
        """Return SPEC core rules file path for the given format."""
        if not format_key:
            return os.path.join("config", "icao_rules.json")
        key = (format_key or "").lower()
        if "ics" in key or "uae" in key:
            return os.path.join("config", "ics_rules.json")
        if "schengen" in key or "icao" in key or "passport" in key:
            return os.path.join("config", "icao_rules.json")
        return os.path.join("config", "icao_rules.json")

    def _process_current_image_core(self):
        """Run SPEC core on the current image and display pass/fail codes inline."""
        img_path = self.image_preview.get_current_image_path()
        if not img_path or not self.current_format:
            return
        try:
            self.core_process_btn.setEnabled(False)
            self.core_result_label.show()
            self.core_result_label.setStyleSheet("""
                QLabel {
                    background: white;
                    border-radius: 6px;
                    padding: 12px;
                    border: 1px solid rgba(148, 163, 184, 0.1);
                    font-size: 13px;
                    line-height: 1.4;
                    color: #475569;
                }
            """)
            self.core_result_label.setText("⏳ Processing with SPEC core…")
            self.statusBar().showMessage("Processing current image with SPEC core…")

            rules_path = self._get_core_rules_path(self.current_format)
            core = VeriDocEngine(rules_path)

            # Prepare output directory under export/<format>/
            export_root = self.config_manager.get_global_setting('export_directory', 'export/')
            out_dir = os.path.join(export_root, self.current_format)
            os.makedirs(out_dir, exist_ok=True)

            base = os.path.splitext(os.path.basename(img_path))[0]
            bgr = core.import_image(img_path)
            lm = core.detect_landmarks(bgr)
            measures = core.measure_geometry(bgr, lm, core.rules)
            fixed = core.autofix(bgr, measures, core.rules)
            report = core.validate(measures, core.rules)
            export_path = core.export(fixed, out_dir, base, core.rules, report)

            passed = len(report.fails) == 0
            if passed:
                codes_text = ", ".join(cr.code for cr in report.passes[:6])
                head = "✅ CORE PASS"
                detail = f"Validation codes: {codes_text}"
                color = "#16a34a"
                bg_color = "rgba(22, 163, 74, 0.1)"
            else:
                codes_text = ", ".join(cr.code for cr in report.fails[:6])
                head = "❌ CORE FAIL"
                detail = f"Failure reasons: {codes_text}"
                color = "#dc2626"
                bg_color = "rgba(220, 38, 38, 0.1)"

            self.core_result_label.setStyleSheet(f"""
                QLabel {{
                    background: {bg_color};
                    border-radius: 6px;
                    padding: 12px;
                    border: 1px solid {color};
                    font-size: 13px;
                    line-height: 1.4;
                    color: {color};
                    font-weight: 600;
                }}
            """)
            
            filename = os.path.basename(export_path)
            self.core_result_label.setText(f"{head}\n{detail}\n📁 Saved: {filename}")

            # Update overlay banner to reflect core result
            self.image_preview.set_validation_overlay({
                'compliance_status': {
                    'overall_pass': passed,
                    'score': 100 if passed else 0
                }
            })

            self._log_message(f"SPEC core processed: {'PASS' if passed else 'FAIL'} — {filename}")
            self.statusBar().showMessage("Ready")
        except Exception as e:
            self.core_result_label.show()
            self.core_result_label.setStyleSheet("""
                QLabel {
                    background: rgba(245, 158, 11, 0.1);
                    border-radius: 6px;
                    padding: 12px;
                    border: 1px solid #F59E0B;
                    font-size: 13px;
                    line-height: 1.4;
                    color: #F59E0B;
                    font-weight: 600;
                }
            """)
            self.core_result_label.setText(f"⚠️ CORE ERROR\n{str(e)}")
            self._log_message(f"SPEC core error: {e}")
            self.statusBar().showMessage("Core processing error")
        finally:
            self._update_core_button_state()
    
    def _on_image_clicked(self, x: int, y: int):
        """Handle click on image preview."""
        self._log_message(f"Image clicked at coordinates: ({x}, {y})")
    
    def _on_validation_item_clicked(self, category: str, item_name: str):
        """Handle click on validation checklist item."""
        self._log_message(f"Validation item clicked: {category} - {item_name}")
        
        # Could show detailed information about the specific validation
        # For now, just log the click
    
    def _on_validation_refresh(self):
        """Handle validation refresh request."""
        if self.image_preview.get_current_image_path():
            self._validate_current_image()
        else:
            self._show_message("No image selected for validation.", "Information", QMessageBox.Information)
    
    def _on_batch_processing_started(self):
        """Handle batch processing started."""
        self._log_message("Batch processing started")
        self.statusBar().showMessage("Batch processing in progress...")
        
        # Disable process button during batch processing
        self.process_btn.setEnabled(False)
    
    def _on_batch_processing_completed(self, result):
        """Handle batch processing completed."""
        self._log_message(f"Batch processing completed - {result.successful_files}/{result.total_files} successful")
        self.statusBar().showMessage(f"Batch processing completed - {result.successful_files} successful, {result.failed_files} failed")
        
        # Re-enable process button
        self._update_process_button_state()
    
    def _on_batch_processing_cancelled(self):
        """Handle batch processing cancelled."""
        self._log_message("Batch processing cancelled by user")
        self.statusBar().showMessage("Batch processing cancelled")
        
        # Re-enable process button
        self._update_process_button_state()

    def _auto_detect_format(self):
        """Automatically detect the format for the selected image."""
        current_item = self.image_list.currentItem()
        if not current_item:
            self._show_message("Please select an image first.", "No Image Selected", QMessageBox.Warning)
            return

        image_path = current_item.data(Qt.UserRole)
        if not image_path:
            return

        try:
            from utils.format_detector import FormatDetector
            detector = FormatDetector(self.config_manager)
            result = detector.detect_format(image_path)

            if result and result.confidence > 0.5:
                self.format_selector.set_format(result.format_name)
                self._log_message(f"Auto-detected format: {result.format_name} with {result.confidence:.2f} confidence.")
                self._show_message(f"Detected format: {result.format_name}", "Format Detected", QMessageBox.Information)
            else:
                self._log_message("Could not auto-detect format with sufficient confidence.")
                self._show_message("Could not automatically detect the format.", "Detection Failed", QMessageBox.Warning)
        except Exception as e:
            self._log_message(f"Error during format detection: {e}")
            self._show_message(f"An error occurred during format detection: {e}", "Error", QMessageBox.Critical)

    def closeEvent(self, event):
        """Handle application close event."""
        # Clean up resources if needed
        self._log_message("Application shutting down")
        
        # Stop any running threads
        if hasattr(self, 'batch_processor') and self.batch_processor.is_processing():
            self.batch_processor.cancel_processing()
        
        super().closeEvent(event)