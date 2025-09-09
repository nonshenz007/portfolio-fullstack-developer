"""
Batch Processor Widget for VeriDoc

Provides batch processing capabilities for multiple images with progress tracking
and result reporting.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextEdit, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, pyqtSignal
from engine.veridoc_engine import VeriDocEngine, ProcessingOptions
from config.config_manager import ConfigManager


class BatchProcessingThread(QThread):
    """Thread for batch processing images without blocking the UI."""
    
    progress_updated = pyqtSignal(int)  # Progress percentage
    status_updated = pyqtSignal(str)    # Status message
    image_processed = pyqtSignal(str, bool, str)  # file_path, success, message
    finished_processing = pyqtSignal(dict)  # Results summary
    
    def __init__(self, image_paths: List[str], format_id: str, 
                 processing_options: ProcessingOptions, output_dir: str):
        super().__init__()
        self.image_paths = image_paths
        self.format_id = format_id
        self.processing_options = processing_options
        self.output_dir = Path(output_dir)
        self.engine = VeriDocEngine()
        self.should_stop = False
        
    def run(self):
        """Run the batch processing."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            total_images = len(self.image_paths)
            processed_count = 0
            success_count = 0
            failed_count = 0
            results = []
            
            for i, image_path in enumerate(self.image_paths):
                if self.should_stop:
                    break
                    
                try:
                    self.status_updated.emit(f"Processing {Path(image_path).name}...")
                    
                    # Generate output path
                    input_path = Path(image_path)
                    output_filename = f"{input_path.stem}_processed{input_path.suffix}"
                    output_path = self.output_dir / output_filename
                    
                    # Process the image
                    result = self.engine.process_single_image(
                        input_path=str(input_path),
                        output_path=str(output_path),
                        format_id=self.format_id,
                        processing_options=self.processing_options
                    )
                    
                    if result.success:
                        success_count += 1
                        message = f"Success - Score: {result.validation_report_after.score:.1f}%" if result.validation_report_after else "Success"
                        self.image_processed.emit(str(input_path), True, message)
                    else:
                        failed_count += 1
                        self.image_processed.emit(str(input_path), False, result.error_message or "Processing failed")
                    
                    results.append(result)
                    processed_count += 1
                    
                    # Update progress
                    progress = int((i + 1) / total_images * 100)
                    self.progress_updated.emit(progress)
                    
                except Exception as e:
                    failed_count += 1
                    self.image_processed.emit(str(image_path), False, str(e))
                    processed_count += 1
                    
                    progress = int((i + 1) / total_images * 100)
                    self.progress_updated.emit(progress)
            
            # Emit final results
            summary = {
                'total': total_images,
                'processed': processed_count,
                'success': success_count,
                'failed': failed_count,
                'results': results,
                'output_dir': str(self.output_dir)
            }
            
            self.finished_processing.emit(summary)
            
        except Exception as e:
            self.status_updated.emit(f"Batch processing error: {e}")
    
    def stop(self):
        """Stop the processing thread."""
        self.should_stop = True


class BatchProcessor(QWidget):
    """Widget for batch processing multiple images."""
    
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal(dict)
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.processing_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the batch processor UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Batch Processing")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to process")
        self.status_label.setStyleSheet("color: #666666; font-size: 12px;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("Start Processing")
        self.process_btn.setStyleSheet("""
            QPushButton {
                background: #007acc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background: #005a9e; }
            QPushButton:disabled { background: #cccccc; }
        """)
        self.process_btn.clicked.connect(self.start_processing)
        controls_layout.addWidget(self.process_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover { background: #c82333; }
        """)
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setVisible(False)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Results log
        results_group = QGroupBox("Processing Log")
        results_layout = QVBoxLayout(results_group)
        
        self.results_log = QTextEdit()
        self.results_log.setMaximumHeight(200)
        self.results_log.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        results_layout.addWidget(self.results_log)
        
        layout.addWidget(results_group)
        
    def process_images(self, image_paths: List[str], format_id: str, 
                      processing_options: Optional[ProcessingOptions] = None) -> bool:
        """
        Process a list of images with the specified format and options.
        
        Args:
            image_paths: List of paths to images to process
            format_id: Format ID to use for processing
            processing_options: Processing options (uses defaults if None)
            
        Returns:
            True if processing started successfully, False otherwise
        """
        if not image_paths:
            QMessageBox.warning(self, "No Images", "No images selected for processing.")
            return False
            
        if self.processing_thread and self.processing_thread.isRunning():
            QMessageBox.warning(self, "Processing Active", "Batch processing is already running.")
            return False
        
        # Set default options if not provided
        if processing_options is None:
            processing_options = ProcessingOptions(
                auto_enhance=True,
                normalize_background=True,
                auto_crop_to_face=True,
                validate_before_processing=True,
                validate_after_processing=True,
                output_format="JPEG",
                output_quality=95,
                output_dpi=300
            )
        
        # Set up output directory
        output_dir = Path("output/batch_processed")
        
        # Create and start processing thread
        self.processing_thread = BatchProcessingThread(
            image_paths, format_id, processing_options, str(output_dir)
        )
        
        # Connect signals
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.status_updated.connect(self.update_status)
        self.processing_thread.image_processed.connect(self.log_image_result)
        self.processing_thread.finished_processing.connect(self.on_processing_finished)
        
        # Start processing
        self.processing_thread.start()
        self.processing_started.emit()
        
        # Update UI
        self.process_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.results_log.clear()
        self.results_log.append(f"🚀 Starting batch processing of {len(image_paths)} images...")
        self.results_log.append(f"📁 Output directory: {output_dir}")
        self.results_log.append(f"🎯 Format: {format_id}")
        self.results_log.append("")
        
        return True
    
    def start_processing(self):
        """Start processing (placeholder - should be called from parent)."""
        QMessageBox.information(
            self, 
            "Batch Processing", 
            "Please select images and configure settings first.\n\n"
            "This method should be called by the parent window with proper parameters."
        )
    
    def stop_processing(self):
        """Stop the current processing."""
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.stop()
            self.processing_thread.wait(3000)  # Wait up to 3 seconds
            if self.processing_thread.isRunning():
                self.processing_thread.terminate()
            
            self.update_status("Processing stopped by user")
            self.reset_ui()
    
    def update_progress(self, value: int):
        """Update the progress bar."""
        self.progress_bar.setValue(value)
    
    def update_status(self, message: str):
        """Update the status label."""
        self.status_label.setText(message)
    
    def log_image_result(self, file_path: str, success: bool, message: str):
        """Log the result of processing a single image."""
        filename = Path(file_path).name
        icon = "✅" if success else "❌"
        self.results_log.append(f"{icon} {filename}: {message}")
        
        # Auto-scroll to bottom
        cursor = self.results_log.textCursor()
        cursor.movePosition(cursor.End)
        self.results_log.setTextCursor(cursor)
    
    def on_processing_finished(self, results: Dict[str, Any]):
        """Handle completion of batch processing."""
        self.processing_finished.emit(results)
        
        # Log summary
        self.results_log.append("")
        self.results_log.append("🎉 Batch processing completed!")
        self.results_log.append(f"📊 Total: {results['total']}")
        self.results_log.append(f"✅ Success: {results['success']}")
        self.results_log.append(f"❌ Failed: {results['failed']}")
        self.results_log.append(f"📁 Output: {results['output_dir']}")
        
        # Show completion message
        success_rate = (results['success'] / results['total']) * 100 if results['total'] > 0 else 0
        QMessageBox.information(
            self,
            "Processing Complete",
            f"Batch processing completed!\n\n"
            f"✅ Successfully processed: {results['success']} images\n"
            f"❌ Failed: {results['failed']} images\n"
            f"📊 Success rate: {success_rate:.1f}%\n\n"
            f"📁 Output folder: {results['output_dir']}"
        )
        
        self.reset_ui()
    
    def reset_ui(self):
        """Reset the UI to initial state."""
        self.process_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.update_status("Ready to process")
