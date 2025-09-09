"""
Unit tests for utils module (Logger and FileManager).

Tests logging functionality, file operations, path validation,
and file type checking capabilities.
"""

import unittest
import tempfile
import shutil
import csv
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from PIL import Image
import io

from utils.logger import Logger, LogLevel, get_logger
from utils.file_manager import FileManager


class TestLogger(unittest.TestCase):
    """Test cases for the Logger class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test_log.csv")
        self.logger = Logger(self.log_file, max_size_mb=0.001, max_backup_files=3)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_initialization(self):
        """Test logger initialization and file creation."""
        self.assertTrue(os.path.exists(self.log_file))
        
        # Check headers are written
        with open(self.log_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected_headers = [
                "timestamp", "level", "operation", "file_name", "format",
                "validation_results", "export_status", "processing_time",
                "error_message", "details"
            ]
            self.assertEqual(headers, expected_headers)
    
    def test_log_activity(self):
        """Test basic log activity functionality."""
        self.logger.log_activity(
            level=LogLevel.INFO,
            operation="TEST_OPERATION",
            file_name="test.jpg",
            format_type="ICS-UAE",
            validation_results="PASS",
            export_status="SUCCESS",
            processing_time=1.5,
            error_message="",
            details={"test": "data"}
        )
        
        # Read and verify log entry
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['level'], 'INFO')
        self.assertEqual(row['operation'], 'TEST_OPERATION')
        self.assertEqual(row['file_name'], 'test.jpg')
        self.assertEqual(row['format'], 'ICS-UAE')
        self.assertEqual(row['validation_results'], 'PASS')
        self.assertEqual(row['export_status'], 'SUCCESS')
        self.assertEqual(row['processing_time'], '1.5')
        self.assertIn('test', row['details'])
    
    def test_log_processing_methods(self):
        """Test specialized logging methods."""
        # Test processing start
        self.logger.log_processing_start("image1.jpg", "India-Passport")
        
        # Test processing complete
        self.logger.log_processing_complete(
            "image1.jpg", "India-Passport", "PASS", "SUCCESS", 2.3
        )
        
        # Test validation result
        self.logger.log_validation_result(
            "image1.jpg", "India-Passport", "PASS", True
        )
        
        # Test error logging
        self.logger.log_error(
            "FACE_DETECTION", "image1.jpg", "No face detected",
            {"confidence": 0.1}
        )
        
        # Test export logging
        self.logger.log_export(
            "image1.jpg", "India-Passport", "/export/image1.jpg", True
        )
        
        # Verify all entries
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        self.assertEqual(len(rows), 5)
        
        # Check operations
        operations = [row['operation'] for row in rows]
        expected_operations = [
            'PROCESSING_START', 'PROCESSING_COMPLETE', 'VALIDATION', 
            'FACE_DETECTION', 'EXPORT'
        ]
        self.assertEqual(operations, expected_operations)
    
    def test_log_rotation(self):
        """Test log rotation functionality."""
        # Write enough data to trigger rotation
        large_details = {"data": "x" * 1000}  # Large details to increase file size
        
        for i in range(20):  # Write multiple entries to exceed size limit
            self.logger.log_activity(
                level=LogLevel.INFO,
                operation=f"TEST_{i}",
                file_name=f"test_{i}.jpg",
                details=large_details
            )
        
        # Check that backup files were created
        backup_files = []
        for i in range(1, 4):  # max_backup_files = 3
            backup_path = Path(self.log_file).with_suffix(f'.{i}.csv')
            if backup_path.exists():
                backup_files.append(backup_path)
        
        # Should have at least one backup file
        self.assertGreater(len(backup_files), 0)
        
        # Main log file should still exist and have headers
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertEqual(len(headers), 10)  # Should have all headers
    
    def test_get_recent_logs(self):
        """Test retrieving recent log entries."""
        # Add some log entries
        for i in range(5):
            self.logger.log_activity(
                level=LogLevel.INFO,
                operation=f"TEST_{i}",
                file_name=f"test_{i}.jpg"
            )
        
        # Get recent logs
        recent_logs = self.logger.get_recent_logs(3)
        self.assertEqual(len(recent_logs), 3)
        
        # Check that we get the most recent entries
        operations = [log['operation'] for log in recent_logs]
        self.assertEqual(operations, ['TEST_2', 'TEST_3', 'TEST_4'])
    
    def test_clear_logs(self):
        """Test clearing all log files."""
        # Add some entries
        self.logger.log_activity(LogLevel.INFO, "TEST", "test.jpg")
        
        # Clear logs
        success = self.logger.clear_logs()
        self.assertTrue(success)
        
        # Check that file exists but only has headers
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 0)
    
    def test_global_logger(self):
        """Test global logger functionality."""
        logger1 = get_logger(self.log_file)
        logger2 = get_logger(self.log_file)
        
        # Should return the same instance
        self.assertIs(logger1, logger2)


class TestFileManager(unittest.TestCase):
    """Test cases for the FileManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager(self.temp_dir)
        
        # Create test files
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("test content")
        
        # Create test image
        self.test_image = os.path.join(self.temp_dir, "test.jpg")
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_image, 'JPEG')
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_path(self):
        """Test path validation functionality."""
        # Valid paths
        valid, msg = self.file_manager.validate_path("test.txt")
        self.assertTrue(valid)
        self.assertEqual(msg, "")
        
        valid, msg = self.file_manager.validate_path("folder/test.txt")
        self.assertTrue(valid)
        
        # Invalid characters
        invalid, msg = self.file_manager.validate_path("test<>.txt")
        self.assertFalse(invalid)
        self.assertIn("invalid characters", msg)
        
        # Very long path
        long_path = "a" * 300 + ".txt"
        invalid, msg = self.file_manager.validate_path(long_path)
        self.assertFalse(invalid)
        self.assertIn("too long", msg)
    
    def test_is_supported_image_file(self):
        """Test image file type detection."""
        # Test with actual image file
        self.assertTrue(self.file_manager.is_supported_image_file(self.test_image))
        
        # Test with text file
        self.assertFalse(self.file_manager.is_supported_image_file(self.test_file))
        
        # Test with non-existent file
        self.assertFalse(self.file_manager.is_supported_image_file("nonexistent.jpg"))
        
        # Test different extensions
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        for ext in supported_extensions:
            # Create temporary image with different extension
            temp_image = os.path.join(self.temp_dir, f"test{ext}")
            img = Image.new('RGB', (50, 50), color='blue')
            img.save(temp_image)
            self.assertTrue(self.file_manager.is_supported_image_file(temp_image))
    
    def test_get_file_info(self):
        """Test file information retrieval."""
        # Test with regular file
        info = self.file_manager.get_file_info(self.test_file)
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'test.txt')
        self.assertEqual(info['stem'], 'test')
        self.assertEqual(info['suffix'], '.txt')
        self.assertTrue(info['is_file'])
        self.assertFalse(info['is_directory'])
        self.assertGreater(info['size_bytes'], 0)
        
        # Test with image file
        info = self.file_manager.get_file_info(self.test_image)
        self.assertIsNotNone(info)
        self.assertTrue(info['is_image'])
        self.assertEqual(info['image_width'], 100)
        self.assertEqual(info['image_height'], 100)
        self.assertEqual(info['image_format'], 'JPEG')
        
        # Test with non-existent file
        info = self.file_manager.get_file_info("nonexistent.txt")
        self.assertIsNone(info)
    
    def test_create_directory(self):
        """Test directory creation."""
        new_dir = os.path.join(self.temp_dir, "new_directory")
        
        success, msg = self.file_manager.create_directory(new_dir)
        self.assertTrue(success)
        self.assertEqual(msg, "")
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
        
        # Test nested directory creation
        nested_dir = os.path.join(self.temp_dir, "level1", "level2", "level3")
        success, msg = self.file_manager.create_directory(nested_dir, parents=True)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(nested_dir))
    
    def test_copy_file(self):
        """Test file copying functionality."""
        destination = os.path.join(self.temp_dir, "copied_test.txt")
        
        success, msg = self.file_manager.copy_file(self.test_file, destination)
        self.assertTrue(success)
        self.assertEqual(msg, "")
        self.assertTrue(os.path.exists(destination))
        
        # Verify content is the same
        with open(destination, 'r') as f:
            content = f.read()
        self.assertEqual(content, "test content")
        
        # Test overwrite protection
        success, msg = self.file_manager.copy_file(self.test_file, destination, overwrite=False)
        self.assertFalse(success)
        self.assertIn("exists", msg)
        
        # Test overwrite allowed
        success, msg = self.file_manager.copy_file(self.test_file, destination, overwrite=True)
        self.assertTrue(success)
    
    def test_move_file(self):
        """Test file moving functionality."""
        # Create a file to move
        source = os.path.join(self.temp_dir, "to_move.txt")
        with open(source, 'w') as f:
            f.write("move me")
        
        destination = os.path.join(self.temp_dir, "moved.txt")
        
        success, msg = self.file_manager.move_file(source, destination)
        self.assertTrue(success)
        self.assertEqual(msg, "")
        self.assertFalse(os.path.exists(source))
        self.assertTrue(os.path.exists(destination))
        
        # Verify content
        with open(destination, 'r') as f:
            content = f.read()
        self.assertEqual(content, "move me")
    
    def test_delete_file(self):
        """Test file deletion."""
        # Create a file to delete
        to_delete = os.path.join(self.temp_dir, "delete_me.txt")
        with open(to_delete, 'w') as f:
            f.write("delete this")
        
        success, msg = self.file_manager.delete_file(to_delete)
        self.assertTrue(success)
        self.assertEqual(msg, "")
        self.assertFalse(os.path.exists(to_delete))
        
        # Test deleting non-existent file
        success, msg = self.file_manager.delete_file("nonexistent.txt")
        self.assertFalse(success)
        self.assertIn("does not exist", msg)
    
    def test_list_files(self):
        """Test file listing functionality."""
        # Create additional test files
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")
        
        # List all files
        files = self.file_manager.list_files(self.temp_dir)
        txt_files = [f for f in files if f.endswith('.txt')]
        self.assertGreaterEqual(len(txt_files), 4)  # Original test.txt + 3 new files
        
        # Test pattern matching
        files = self.file_manager.list_files(self.temp_dir, "file_*.txt")
        self.assertEqual(len(files), 3)
        
        # Test recursive listing
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir)
        sub_file = os.path.join(subdir, "sub.txt")
        with open(sub_file, 'w') as f:
            f.write("sub content")
        
        files = self.file_manager.list_files(self.temp_dir, "*.txt", recursive=True)
        sub_files = [f for f in files if 'sub.txt' in f]
        self.assertEqual(len(sub_files), 1)
    
    def test_list_image_files(self):
        """Test image file listing."""
        # Create additional image files
        for i, ext in enumerate(['.png', '.bmp']):
            img_file = os.path.join(self.temp_dir, f"image_{i}{ext}")
            img = Image.new('RGB', (50, 50), color='green')
            img.save(img_file)
        
        image_files = self.file_manager.list_image_files(self.temp_dir)
        self.assertGreaterEqual(len(image_files), 3)  # Original jpg + png + bmp
        
        # Verify all returned files are actually images
        for img_file in image_files:
            self.assertTrue(self.file_manager.is_supported_image_file(img_file))
    
    def test_get_file_hash(self):
        """Test file hash calculation."""
        # Test MD5 hash
        hash_md5 = self.file_manager.get_file_hash(self.test_file, "md5")
        self.assertIsNotNone(hash_md5)
        self.assertEqual(len(hash_md5), 32)  # MD5 is 32 hex characters
        
        # Test SHA256 hash
        hash_sha256 = self.file_manager.get_file_hash(self.test_file, "sha256")
        self.assertIsNotNone(hash_sha256)
        self.assertEqual(len(hash_sha256), 64)  # SHA256 is 64 hex characters
        
        # Test with non-existent file
        hash_none = self.file_manager.get_file_hash("nonexistent.txt")
        self.assertIsNone(hash_none)
    
    def test_get_safe_filename(self):
        """Test safe filename generation."""
        # Test with invalid characters
        unsafe_name = "file<>name|with?invalid*chars.txt"
        safe_name = self.file_manager.get_safe_filename(unsafe_name)
        self.assertEqual(safe_name, "file__name_with_invalid_chars.txt")
        
        # Test with leading/trailing spaces and dots
        unsafe_name = "  .filename.  "
        safe_name = self.file_manager.get_safe_filename(unsafe_name)
        self.assertEqual(safe_name, "filename")
        
        # Test with empty filename
        safe_name = self.file_manager.get_safe_filename("")
        self.assertEqual(safe_name, "unnamed_file")
    
    def test_get_unique_filename(self):
        """Test unique filename generation."""
        # Test with non-existing file
        unique_name = self.file_manager.get_unique_filename(self.temp_dir, "unique.txt")
        self.assertEqual(unique_name, "unique.txt")
        
        # Create a file and test uniqueness
        existing_file = os.path.join(self.temp_dir, "existing.txt")
        with open(existing_file, 'w') as f:
            f.write("exists")
        
        unique_name = self.file_manager.get_unique_filename(self.temp_dir, "existing.txt")
        self.assertEqual(unique_name, "existing_1.txt")
        
        # Create the _1 version and test again
        existing_file_1 = os.path.join(self.temp_dir, "existing_1.txt")
        with open(existing_file_1, 'w') as f:
            f.write("exists 1")
        
        unique_name = self.file_manager.get_unique_filename(self.temp_dir, "existing.txt")
        self.assertEqual(unique_name, "existing_2.txt")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)