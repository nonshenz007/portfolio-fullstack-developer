"""
VeriDoc ICS Professional - Clean, Simple UI
A truly clean and usable interface for ICS (UAE) photo validation.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# PySide6 imports for UI (production-ready, modern Qt)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QProgressBar,
    QFileDialog, QApplication, QMessageBox,
    QListWidget, QListWidgetItem, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, Signal, QSize, QMimeData, QUrl
)
from PySide6.QtGui import (
    QPixmap, QFont, QColor, QPalette, QDragEnterEvent, QDropEvent,
    QIcon, QPainter, QBrush, QLinearGradient, QPen
)

# Import VeriDoc components
sys.path.append(str(Path(__file__).parent.parent))
from engine.veridoc_engine import VeriDocEngine, ProcessingOptions
from config.config_manager import ConfigManager
from validation.format_validator import ValidationReport


class SimpleImageQueue(QWidget):
    """Simple, clean image queue widget."""
    
    image_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_paths = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup simple queue interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Simple header
        header = QLabel("📁 Import Photos")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Import buttons
        button_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("Import Files")
        self.import_btn.setStyleSheet("""
            QPushButton {
                background: #007acc;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover { background: #005a9e; }
        """)
        self.import_btn.clicked.connect(self.import_files)
        button_layout.addWidget(self.import_btn)
        
        self.import_folder_btn = QPushButton("Import Folder")
        self.import_folder_btn.setStyleSheet(self.import_btn.styleSheet())
        self.import_folder_btn.clicked.connect(self.import_folder)
        button_layout.addWidget(self.import_folder_btn)
        
        layout.addLayout(button_layout)
        
        # Simple drag drop area
        self.drop_area = QLabel()
        self.drop_area.setMinimumHeight(120)
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setText("Drag & Drop Photos Here\n\nICS (UAE) Format: 413×531 pixels")
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.05);
                color: #cccccc;
                font-size: 14px;
                padding: 20px;
            }
        """)
        layout.addWidget(self.drop_area)
        
        # Simple file list
        list_header = QLabel("📋 Queue")
        list_header.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff; margin: 15px 0 5px 0;")
        layout.addWidget(list_header)
        
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(150)
        self.file_list.setMaximumHeight(200)
        self.file_list.setStyleSheet("""
            QListWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border: none;
                border-radius: 4px;
                margin: 1px;
            }
            QListWidget::item:selected {
                background: #007acc;
                color: white;
            }
            QListWidget::item:hover {
                background: rgba(0, 122, 204, 0.3);
            }
        """)
        self.file_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.file_list)
        
        # Simple controls
        controls_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #666666;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background: #777777; }
        """)
        self.clear_btn.clicked.connect(self.clear_queue)
        controls_layout.addWidget(self.clear_btn)
        
        controls_layout.addStretch()
        
        self.process_btn = QPushButton("Process All")
        self.process_btn.setStyleSheet("""
            QPushButton {
                background: #00cc6a;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover { background: #00b85e; }
            QPushButton:disabled {
                background: #444444;
                color: #888888;
            }
        """)
        self.process_btn.setEnabled(False)
        controls_layout.addWidget(self.process_btn)
        
        layout.addLayout(controls_layout)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("""
                QLabel {
                    border: 2px dashed #00cc6a;
                    border-radius: 8px;
                    background: rgba(0, 204, 106, 0.1);
                    color: #ffffff;
                    font-size: 14px;
                    padding: 20px;
            }
        """)
            
    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.05);
                color: #cccccc;
                font-size: 14px;
                padding: 20px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        files_to_add = []
        for url in urls:
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if self.is_image_file(file_path):
                    files_to_add.append(file_path)
        if files_to_add:
            self.add_images(files_to_add)
        self.dragLeaveEvent(event)
        event.acceptProposedAction()
        
    def is_image_file(self, file_path: str) -> bool:
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        return Path(file_path).suffix.lower() in extensions
        
    def import_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.tif)"
        )
        if files:
            self.add_images(files)
            
    def import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            files_to_add = []
            for file_path in Path(folder).iterdir():
                if file_path.is_file() and self.is_image_file(str(file_path)):
                    files_to_add.append(str(file_path))
            if files_to_add:
                self.add_images(files_to_add)
                    
    def add_images(self, file_paths: List[str]):
        for file_path in file_paths:
            if file_path not in self.image_paths:
                self.image_paths.append(file_path)
                item = QListWidgetItem(f"📸 {Path(file_path).name}")
                item.setData(Qt.UserRole, file_path)
                self.file_list.addItem(item)
        self.process_btn.setEnabled(len(self.image_paths) > 0)
            
    def clear_queue(self):
        self.image_paths.clear()
        self.file_list.clear()
        self.process_btn.setEnabled(False)
        
    def on_item_clicked(self, item: QListWidgetItem):
        file_path = item.data(Qt.UserRole)
        if file_path:
            self.image_selected.emit(file_path)


class SimplePreviewWidget(QWidget):
    """Simple, clean preview widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.validation_report = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Simple header
        header = QLabel("🖼️ Preview & Validation")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Simple preview area
        self.preview_area = QGraphicsView()
        self.preview_scene = QGraphicsScene()
        self.preview_area.setScene(self.preview_scene)
        self.preview_area.setMinimumHeight(300)
        self.preview_area.setStyleSheet("""
            QGraphicsView {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid #555555;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.preview_area)
        
        # Simple validation info
        self.validation_info = QLabel("Select an image to see validation results")
        self.validation_info.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 15px;
                color: #cccccc;
                font-size: 14px;
            }
        """)
        self.validation_info.setWordWrap(True)
        layout.addWidget(self.validation_info)
        
        # Simple action buttons
        button_layout = QHBoxLayout()
        
        self.auto_fix_btn = QPushButton("Auto Fix")
        self.auto_fix_btn.setStyleSheet("""
            QPushButton {
                background: #ff6b35;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background: #e55a2b; }
        """)
        button_layout.addWidget(self.auto_fix_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: #007acc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background: #005a9e; }
        """)
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
    def load_image(self, image_path: str):
        try:
            self.current_image_path = image_path
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.preview_scene.clear()
                self.preview_scene.addPixmap(scaled_pixmap)
                self.preview_area.fitInView(
                    self.preview_scene.itemsBoundingRect(), Qt.KeepAspectRatio
                )
        except Exception as e:
            print(f"Error loading image: {e}")
            
    def update_validation(self, validation_report: ValidationReport):
        self.validation_report = validation_report
        
        if validation_report:
            score = int(validation_report.score)
            
            if score >= 80:
                color = "#00cc6a"
                status = "✅ PASS"
            elif score >= 60:
                color = "#ffaa00"
                status = "⚠️ NEEDS IMPROVEMENT"
            else:
                color = "#ff4444"
                status = "❌ FAIL"
                
            info_text = f"""
<b>ICS (UAE) Validation Results</b><br><br>
<span style="color: {color}; font-size: 16px; font-weight: bold;">{status} - Score: {score}%</span><br><br>
<b>Target:</b> 413×531 pixels, 300 DPI<br>
<b>Format:</b> ICS (UAE) Government Standard<br><br>
"""
            
            if validation_report.issues:
                info_text += "<b>Issues Found:</b><br>"
                for issue in validation_report.issues[:3]:  # Show first 3 issues
                    icon = "✅" if issue.auto_fixable else "❌"
                    info_text += f"{icon} {issue.message}<br>"
                    
                if len(validation_report.issues) > 3:
                    info_text += f"... and {len(validation_report.issues) - 3} more issues"
            else:
                info_text += "✅ All validation checks passed!"
                
            self.validation_info.setText(info_text)
            self.validation_info.setStyleSheet(f"""
                QLabel {{
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid {color};
                    border-radius: 8px;
                    padding: 15px;
                    color: #ffffff;
                    font-size: 14px;
                }}
            """)
        else:
            self.validation_info.setText("No validation results available")


class VeriDocMainWindow(QMainWindow):
    """
    Clean, simple VeriDoc ICS Professional interface.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize VeriDoc components
        self.config_manager = ConfigManager()
        self.engine = VeriDocEngine()

        # UI state
        self.current_image_path = None
        self.current_format = "ICS-UAE"
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup clean, simple UI."""
        self.setWindowTitle("VeriDoc ICS Professional - UAE Government Standard")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Central widget with simple layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left panel - Image queue (clean)
        self.image_queue = SimpleImageQueue()
        self.image_queue.setFixedWidth(400)
        self.image_queue.setStyleSheet("background: rgba(0, 0, 0, 0.2);")
        main_layout.addWidget(self.image_queue)
        
        # Right panel - Preview (clean)
        self.image_preview = SimplePreviewWidget()
        self.image_preview.setStyleSheet("background: rgba(0, 0, 0, 0.1);")
        main_layout.addWidget(self.image_preview)

        # Simple status bar
        self.setup_status_bar()
        
    def setup_status_bar(self):
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background: #1a1a1a;
                color: #ffffff;
                border-top: 1px solid #333333;
                padding: 5px;
                font-weight: 500;
                }
            """)
        status_bar.showMessage("🇦🇪 VeriDoc ICS Professional Ready - UAE Government Standard")
        
    def setup_connections(self):
        """Setup signal connections."""
        self.image_queue.image_selected.connect(self.on_image_selected)
        self.image_queue.process_btn.clicked.connect(self.process_all_images)
        self.image_preview.auto_fix_btn.clicked.connect(self.auto_fix_current_image)
        self.image_preview.refresh_btn.clicked.connect(self.refresh_validation)

    def on_image_selected(self, image_path: str):
        """Handle image selection."""
        self.current_image_path = image_path
        self.image_preview.load_image(image_path)
        self.validate_current_image()
        self.statusBar().showMessage(f"📸 Loaded: {Path(image_path).name}")
        
    def validate_current_image(self):
        """Validate current image."""
        if not self.current_image_path:
            return
        
        try:
            validation_report = self.engine.validate_image(self.current_image_path, self.current_format)
            self.image_preview.update_validation(validation_report)
            
            score = int(validation_report.score) if validation_report else 0
            self.statusBar().showMessage(f"✅ Validation complete - Score: {score}%")
            
        except Exception as e:
            print(f"Validation error: {e}")
            self.statusBar().showMessage(f"❌ Validation failed: {str(e)}")
            
    def auto_fix_current_image(self):
        """Auto-fix current image using the auto-enhancement system."""
        if not self.current_image_path:
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return
            
        self.statusBar().showMessage("🔧 Auto-fixing image...")
        
        try:
            # Import the auto-enhancement system
            from autofix.auto_enhancer import quick_auto_fix
            from pathlib import Path
            
            # Run auto-fix on the current image
            result = quick_auto_fix(self.current_image_path, "output/auto_fixed")
            
            if result.get('success', False):
                original_score = result.get('original_score', 0)
                final_score = result.get('final_score', 0)
                improvement = result.get('improvement', 0)
                operations = result.get('operations', [])
                output_path = result.get('output_path', '')
                
                # Show results
                ops_text = "\\n".join([f"• {op}" for op in operations]) if operations else "• Background normalization"
                
                message = f"""🎉 Auto-Fix Complete!

📊 Results:
• Original Score: {original_score:.1f}%
• Enhanced Score: {final_score:.1f}%
• Improvement: +{improvement:.1f} points

🔧 Operations Performed:
{ops_text}

📁 Enhanced image saved to:
{Path(output_path).name if output_path else 'auto_fixed folder'}

Would you like to load the enhanced version?"""

                reply = QMessageBox.question(
                    self, "Auto-Fix Results", message,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes and output_path and Path(output_path).exists():
                    # Load the enhanced image
                    self.current_image_path = output_path
                    self.image_preview.load_image(output_path)
                    self.validate_current_image()
                    self.statusBar().showMessage(f"✅ Loaded enhanced image - Score: {final_score:.1f}%")
                else:
                    self.statusBar().showMessage(f"✅ Auto-fix complete - Check output folder")
                    
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                QMessageBox.warning(self, "Auto-Fix Error", f"Auto-fix failed: {error_msg}")
                self.statusBar().showMessage("❌ Auto-fix failed")
                
        except ImportError:
            QMessageBox.information(self, "Auto Fix", "Auto-enhancement system not available.")
            self.statusBar().showMessage("⚠️ Auto-fix system not available")
        except Exception as e:
            QMessageBox.critical(self, "Auto-Fix Error", f"Unexpected error: {str(e)}")
            self.statusBar().showMessage("❌ Auto-fix error")
        
    def refresh_validation(self):
        """Refresh validation."""
        if self.current_image_path:
            self.validate_current_image()
        else:
            QMessageBox.information(self, "No Image", "Please select an image first.")

    def process_all_images(self):
        """Process all images with actual backend processing."""
        if not self.image_queue.image_paths:
            QMessageBox.information(self, "Empty Queue", "Please add images first.")
            return

        # Disable the process button during processing
        self.image_queue.process_btn.setEnabled(False)
        self.image_queue.process_btn.setText("Processing...")
        self.statusBar().showMessage("🔧 Starting batch processing...")

        try:
            # Import required components
            from core.error_handler import get_error_handler, ErrorCategory, ErrorSeverity
            from config.production_config import get_config
            import subprocess
            import platform

            error_handler = get_error_handler()
            config = get_config()

            # Setup processing options
            processing_options = ProcessingOptions(
                auto_enhance=config.processing.auto_fix_enabled,
                normalize_background=True,
                auto_crop_to_face=True,
                validate_before_processing=True,
                validate_after_processing=True,
                output_format="JPEG",
                output_quality=config.processing.output_jpeg_quality,
                output_dpi=config.processing.output_dpi
            )

            # Create output directory
            from pathlib import Path
            output_dir = Path("output/processed")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Process each image
            processed_count = 0
            failed_count = 0
            results = []
            total_images = len(self.image_queue.image_paths)

            self.statusBar().showMessage(f"🔧 Processing {total_images} images...")

            for i, image_path in enumerate(self.image_queue.image_paths, 1):
                try:
                    self.statusBar().showMessage(f"🔧 Processing image {i}/{total_images}: {Path(image_path).name}")

                    # Generate output path
                    input_path = Path(image_path)
                    output_filename = f"{input_path.stem}_processed{input_path.suffix}"
                    output_path = output_dir / output_filename

                    # Process the image
                    result = self.engine.process_single_image(
                        input_path=str(input_path),
                        output_path=str(output_path),
                        format_id=self.current_format,
                        processing_options=processing_options
                    )

                    if result.success:
                        processed_count += 1
                        results.append({
                            'input': str(input_path),
                            'output': str(output_path),
                            'success': True,
                            'processing_time': result.processing_time,
                            'compliance_score': result.validation_report_after.score if result.validation_report_after else 0,
                            'operations': result.operations_performed
                        })
                        print(f"✅ [{i}/{total_images}] Processed: {input_path.name} -> {output_filename} "
                              f"({result.processing_time:.2f}s, Score: {results[-1]['compliance_score']:.1f}%, Ops: {result.operations_performed})")
                    else:
                        failed_count += 1
                        results.append({
                            'input': str(input_path),
                            'output': None,
                            'success': False,
                            'error': result.error_message,
                            'processing_time': result.processing_time
                        })
                        print(f"❌ [{i}/{total_images}] Failed: {input_path.name} - {result.error_message}")

                except Exception as e:
                    failed_count += 1
                    error_handler.handle_error(
                        error_handler.create_error(
                            f"Failed to process image {image_path}: {e}",
                            ErrorCategory.PROCESSING,
                            ErrorSeverity.MEDIUM,
                            "IMAGE_PROCESSING_FAILED"
                        )
                    )
                    results.append({
                        'input': str(image_path),
                        'output': None,
                        'success': False,
                        'error': str(e),
                        'processing_time': 0
                    })
                    print(f"❌ [{i}/{total_images}] Exception: {Path(image_path).name} - {e}")

            # Show results
            success_rate = (processed_count / total_images) * 100

            result_message = f"""🎉 Batch Processing Complete!

✅ Successfully processed: {processed_count} images
❌ Failed: {failed_count} images
📊 Success rate: {success_rate:.1f}%

📁 Output folder: {output_dir.absolute()}

🔧 Operations performed:
"""

            # Add operation summary
            operations_summary = {}
            for result in results:
                if result['success'] and 'operations' in result:
                    for op in result['operations']:
                        operations_summary[op] = operations_summary.get(op, 0) + 1

            for op, count in operations_summary.items():
                result_message += f"   • {op.replace('_', ' ').title()}: {count} images\n"

            result_message += f"\n💡 Tip: Check the output folder to see your processed images!"

            # Show result dialog with option to open folder
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Processing Complete")
            msg_box.setText(result_message)
            msg_box.setIcon(QMessageBox.Information)

            # Add buttons
            open_folder_btn = msg_box.addButton("Open Output Folder", QMessageBox.ActionRole)
            ok_btn = msg_box.addButton("OK", QMessageBox.AcceptRole)
            msg_box.setDefaultButton(ok_btn)

            msg_box.exec()

            # Open output folder if requested
            if msg_box.clickedButton() == open_folder_btn:
                try:
                    if platform.system() == "Windows":
                        os.startfile(str(output_dir))
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", str(output_dir)])
                    else:  # Linux
                        subprocess.run(["xdg-open", str(output_dir)])
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not open output folder: {e}")

            self.statusBar().showMessage(f"✅ Processing complete - {processed_count} successful, {failed_count} failed")

        except Exception as e:
            error_handler = get_error_handler()
            error_handler.handle_error(
                error_handler.create_error(
                    f"Batch processing failed: {e}",
                    ErrorCategory.PROCESSING,
                    ErrorSeverity.HIGH,
                    "BATCH_PROCESSING_FAILED"
                )
            )
            QMessageBox.critical(self, "Processing Error", f"Batch processing failed: {e}")
            self.statusBar().showMessage("❌ Processing failed")

        finally:
            # Re-enable the process button
            self.image_queue.process_btn.setEnabled(True)
            self.image_queue.process_btn.setText("Process All")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Apply clean theme
    try:
        theme_path = Path(__file__).parent / "theme.qss"
        if theme_path.exists():
            with open(theme_path, 'r') as f:
                app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Could not load theme: {e}")
    
    # Create clean main window
    window = VeriDocMainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())