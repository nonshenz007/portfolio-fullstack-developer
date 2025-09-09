"""
Unit tests for Hot-Reload Manager

Tests hot-reload functionality, file watching, and configuration
backup/restore capabilities.
"""

import json
import os
import tempfile
import shutil
import time
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from rules.format_rule_engine import FormatRuleEngine
from config.hot_reload_manager import HotReloadManager, setup_hot_reload


class TestHotReloadManager(TestCase):
    """Test cases for HotReloadManager."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.test_config_dir = tempfile.mkdtemp()
        self.test_backup_dir = tempfile.mkdtemp()
        
        # Create format engine and hot-reload manager
        self.engine = FormatRuleEngine(self.test_config_dir)
        self.manager = HotReloadManager(
            self.engine, 
            watch_directories=[self.test_config_dir]
        )
        
        # Create initial test configuration
        self._create_initial_config()
    
    def tearDown(self):
        """Clean up test environment."""
        # Stop watching if active
        if self.manager.is_watching:
            self.manager.stop_watching()
        
        # Clean up directories
        shutil.rmtree(self.test_config_dir, ignore_errors=True)
        shutil.rmtree(self.test_backup_dir, ignore_errors=True)
    
    def _create_initial_config(self):
        """Create initial test configuration."""
        config = {
            "format_id": "test_initial",
            "display_name": "Test Initial Format",
            "dimensions": {"width": 600, "height": 600}
        }
        
        config_path = Path(self.test_config_dir) / "test_initial.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Load initial configuration
        self.engine._load_all_formats()
    
    def test_manager_initialization(self):
        """Test hot-reload manager initialization."""
        self.assertIsNotNone(self.manager.format_engine)
        self.assertEqual(self.manager.watch_directories, [self.test_config_dir])
        self.assertFalse(self.manager.is_watching)
        self.assertEqual(len(self.manager.change_handlers), 0)
    
    def test_start_stop_watching(self):
        """Test starting and stopping file watching."""
        # Test starting
        success = self.manager.start_watching()
        self.assertTrue(success)
        self.assertTrue(self.manager.is_watching)
        
        # Test stopping
        success = self.manager.stop_watching()
        self.assertTrue(success)
        self.assertFalse(self.manager.is_watching)
        
        # Test stopping when not watching
        success = self.manager.stop_watching()
        self.assertTrue(success)
    
    def test_change_handlers(self):
        """Test change handler management."""
        handler_called = []
        
        def test_handler(message):
            handler_called.append(message)
        
        # Add handler
        self.manager.add_change_handler(test_handler)
        self.assertEqual(len(self.manager.change_handlers), 1)
        
        # Test handler is called on reload
        self.manager.force_reload()
        self.assertGreater(len(handler_called), 0)
        
        # Remove handler
        self.manager.remove_change_handler(test_handler)
        self.assertEqual(len(self.manager.change_handlers), 0)
    
    def test_force_reload(self):
        """Test forced configuration reload."""
        initial_stats = self.manager.get_reload_statistics()
        initial_reloads = initial_stats['total_reloads']
        
        success = self.manager.force_reload()
        self.assertTrue(success)
        
        updated_stats = self.manager.get_reload_statistics()
        self.assertEqual(updated_stats['total_reloads'], initial_reloads + 1)
        self.assertEqual(updated_stats['successful_reloads'], initial_reloads + 1)
    
    def test_reload_statistics(self):
        """Test reload statistics tracking."""
        stats = self.manager.get_reload_statistics()
        
        # Check required fields
        required_fields = [
            'total_reloads', 'successful_reloads', 'failed_reloads',
            'last_reload_time', 'last_reload_duration', 'success_rate',
            'is_watching', 'watch_directories', 'active_handlers'
        ]
        
        for field in required_fields:
            self.assertIn(field, stats)
        
        # Test statistics after reload
        self.manager.force_reload()
        updated_stats = self.manager.get_reload_statistics()
        
        self.assertGreater(updated_stats['total_reloads'], 0)
        self.assertGreater(updated_stats['success_rate'], 0)
    
    def test_configuration_validation(self):
        """Test configuration integrity validation."""
        report = self.manager.validate_configuration_integrity()
        
        # Check report structure
        required_fields = [
            'valid', 'total_files', 'valid_files', 'invalid_files',
            'errors', 'warnings'
        ]
        
        for field in required_fields:
            self.assertIn(field, report)
        
        # Should find our test configuration
        self.assertGreater(report['total_files'], 0)
        self.assertGreater(report['valid_files'], 0)
        
        # Create invalid configuration to test error detection
        invalid_config_path = Path(self.test_config_dir) / "invalid.json"
        with open(invalid_config_path, 'w') as f:
            f.write("{ invalid json content")
        
        report = self.manager.validate_configuration_integrity()
        self.assertGreater(report['invalid_files'], 0)
        self.assertGreater(len(report['errors']), 0)
        self.assertFalse(report['valid'])
    
    def test_configuration_backup(self):
        """Test configuration backup functionality."""
        success = self.manager.backup_configuration(self.test_backup_dir)
        self.assertTrue(success)
        
        # Check that backup directory was created
        backup_path = Path(self.test_backup_dir)
        self.assertTrue(backup_path.exists())
        
        # Check that backup contains files
        backup_folders = list(backup_path.glob("config_backup_*"))
        self.assertGreater(len(backup_folders), 0)
        
        # Check that our test file was backed up
        backup_folder = backup_folders[0]
        backed_up_files = list(backup_folder.glob("**/*.json"))
        self.assertGreater(len(backed_up_files), 0)
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with HotReloadManager(self.engine, [self.test_config_dir]) as manager:
            self.assertTrue(manager.is_watching)
        
        # Should stop watching after context exit
        self.assertFalse(manager.is_watching)
    
    @patch('watchdog.observers.Observer')
    def test_file_system_event_handling(self, mock_observer):
        """Test file system event handling with mocked observer."""
        # Mock observer behavior
        mock_observer_instance = MagicMock()
        mock_observer.return_value = mock_observer_instance
        
        manager = HotReloadManager(self.engine, [self.test_config_dir])
        
        # Test starting with mocked observer
        success = manager.start_watching()
        self.assertTrue(success)
        
        # Verify observer methods were called
        mock_observer_instance.schedule.assert_called()
        mock_observer_instance.start.assert_called()
        
        # Test stopping
        success = manager.stop_watching()
        self.assertTrue(success)
        
        mock_observer_instance.stop.assert_called()
        mock_observer_instance.join.assert_called()
    
    def test_setup_hot_reload_convenience_function(self):
        """Test the setup_hot_reload convenience function."""
        manager = setup_hot_reload(
            self.engine,
            watch_directories=[self.test_config_dir],
            auto_start=False
        )
        
        self.assertIsInstance(manager, HotReloadManager)
        self.assertEqual(manager.watch_directories, [self.test_config_dir])
        self.assertFalse(manager.is_watching)  # auto_start=False
        
        # Test with auto_start=True
        manager2 = setup_hot_reload(
            self.engine,
            watch_directories=[self.test_config_dir],
            auto_start=True
        )
        
        self.assertTrue(manager2.is_watching)
        manager2.stop_watching()  # Clean up
    
    def test_error_handling_in_reload(self):
        """Test error handling during configuration reload."""
        # Create a manager with a broken engine
        broken_engine = MagicMock()
        broken_engine.reload_configuration.return_value = False
        
        manager = HotReloadManager(broken_engine, [self.test_config_dir])
        
        # Force reload should handle the error gracefully
        success = manager.force_reload()
        self.assertFalse(success)
        
        # Check statistics reflect the failure
        stats = manager.get_reload_statistics()
        self.assertGreater(stats['failed_reloads'], 0)
        self.assertLess(stats['success_rate'], 1.0)
    
    def test_debouncing_mechanism(self):
        """Test that rapid file changes are debounced."""
        from config.hot_reload_manager import ConfigurationChangeHandler
        
        reload_calls = []
        
        def mock_reload():
            reload_calls.append(time.time())
        
        handler = ConfigurationChangeHandler(mock_reload)
        
        # Simulate rapid file changes
        test_path = str(Path(self.test_config_dir) / "test.json")
        
        # First change should trigger reload
        handler._trigger_reload(test_path, 'modified')
        time.sleep(0.1)  # Small delay
        
        # Rapid subsequent changes should be debounced
        handler._trigger_reload(test_path, 'modified')
        handler._trigger_reload(test_path, 'modified')
        
        # Wait for any delayed reloads
        time.sleep(1.5)
        
        # Should have limited number of reload calls due to debouncing
        self.assertLessEqual(len(reload_calls), 2)
    
    def test_nonexistent_watch_directory(self):
        """Test handling of non-existent watch directories."""
        nonexistent_dir = "/path/that/does/not/exist"
        
        manager = HotReloadManager(self.engine, [nonexistent_dir])
        
        # Should handle gracefully
        success = manager.start_watching()
        # May succeed or fail depending on watchdog behavior
        # The important thing is it doesn't crash
        
        if manager.is_watching:
            manager.stop_watching()
        
        # Validation should report warnings
        report = manager.validate_configuration_integrity()
        self.assertGreater(len(report['warnings']), 0)


if __name__ == '__main__':
    import unittest
    unittest.main()