"""
Unit tests for VeriDoc Core project structure.

Tests that the new clean project structure is properly set up
and that basic components can be imported and initialized.
"""

import pytest
import os
from pathlib import Path
import importlib
import sys


class TestProjectStructure:
    """Test the basic project structure setup."""
    
    def test_core_directories_exist(self):
        """Test that all required core directories exist."""
        required_dirs = ['core', 'detection', 'validation', 'autofix', 'quality']
        
        for dir_name in required_dirs:
            assert os.path.exists(dir_name), f"Directory {dir_name} should exist"
            assert os.path.isdir(dir_name), f"{dir_name} should be a directory"
    
    def test_init_files_exist(self):
        """Test that all __init__.py files exist in core modules."""
        required_modules = ['core', 'detection', 'validation', 'autofix', 'quality']
        
        for module_name in required_modules:
            init_file = Path(module_name) / "__init__.py"
            assert init_file.exists(), f"__init__.py should exist in {module_name}"
    
    def test_config_directory_structure(self):
        """Test that configuration directory and files exist."""
        assert os.path.exists("config"), "Config directory should exist"
        assert os.path.exists("config/formats.json"), "formats.json should exist"
        assert os.path.exists("config/settings.yaml"), "settings.yaml should exist"
    
    def test_backup_directory_created(self):
        """Test that old system components were backed up."""
        assert os.path.exists("backup_old_system"), "Backup directory should exist"
        
        # Check that old conflicting components were moved
        old_components = ['engine', 'validation', 'rules', 'ai', 'autofix', 'quality']
        for component in old_components:
            backup_path = Path("backup_old_system") / component
            assert backup_path.exists(), f"Old {component} should be backed up"
    
    def test_core_module_imports(self):
        """Test that core modules can be imported."""
        try:
            from core import ConfigManager, ProcessingController
            assert ConfigManager is not None
            assert ProcessingController is not None
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")
    
    def test_module_init_imports(self):
        """Test that module __init__.py files have correct imports."""
        # Test core module
        try:
            import core
            assert hasattr(core, 'ConfigManager')
            assert hasattr(core, 'ProcessingController')
        except (ImportError, AttributeError) as e:
            pytest.fail(f"Core module import issue: {e}")
        
        # Test other modules can be imported (implementation files will be added in later tasks)
        modules_to_test = ['detection', 'validation', 'autofix', 'quality']
        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                assert module is not None, f"{module_name} module should be importable"
                # Check that module has __all__ attribute (even if empty for now)
                assert hasattr(module, '__all__'), f"{module_name} should have __all__ attribute"
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")


class TestConfigManager:
    """Test the ConfigManager functionality."""
    
    def test_config_manager_initialization(self):
        """Test that ConfigManager can be initialized."""
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        assert config_manager is not None
        assert hasattr(config_manager, 'formats')
        assert hasattr(config_manager, 'settings')
    
    def test_format_loading(self):
        """Test that format configurations are loaded correctly."""
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        formats = config_manager.get_available_formats()
        
        assert isinstance(formats, dict)
        assert len(formats) > 0, "Should have at least one format loaded"
        
        # Check for expected formats
        expected_formats = ['ICS-UAE', 'US-Visa', 'ICAO-Standard']
        for format_name in expected_formats:
            assert format_name in formats, f"Format {format_name} should be available"
    
    def test_format_config_structure(self):
        """Test that format configurations have required structure."""
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # Test ICS-UAE format
        ics_config = config_manager.get_format_config('ICS-UAE')
        assert ics_config is not None, "ICS-UAE config should exist"
        
        required_sections = ['dimensions', 'face_requirements', 'background', 'quality']
        for section in required_sections:
            assert section in ics_config, f"ICS-UAE config should have {section} section"
        
        # Test dimensions section
        dims = ics_config['dimensions']
        required_dim_keys = ['width', 'height', 'dpi']
        for key in required_dim_keys:
            assert key in dims, f"Dimensions should have {key}"
            assert isinstance(dims[key], (int, float)), f"{key} should be numeric"
    
    def test_settings_loading(self):
        """Test that system settings are loaded correctly."""
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # Test getting settings
        max_size = config_manager.get_setting('processing.max_image_size')
        assert max_size is not None, "Should have max_image_size setting"
        assert isinstance(max_size, int), "max_image_size should be integer"
        
        log_level = config_manager.get_setting('logging.level')
        assert log_level is not None, "Should have logging level setting"
        assert isinstance(log_level, str), "log_level should be string"
    
    def test_format_validation(self):
        """Test format configuration validation."""
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # Test valid format
        assert config_manager.validate_format_config('ICS-UAE'), "ICS-UAE should be valid"
        assert config_manager.validate_format_config('US-Visa'), "US-Visa should be valid"
        
        # Test invalid format
        assert not config_manager.validate_format_config('NonExistent'), "NonExistent format should be invalid"


class TestProcessingController:
    """Test the ProcessingController functionality."""
    
    def test_processing_controller_initialization(self):
        """Test that ProcessingController can be initialized."""
        from core.processing_controller import ProcessingController
        
        controller = ProcessingController()
        assert controller is not None
        assert hasattr(controller, 'config_manager')
        assert controller.config_manager is not None
    
    def test_get_available_formats(self):
        """Test getting available formats from controller."""
        from core.processing_controller import ProcessingController
        
        controller = ProcessingController()
        formats = controller.get_available_formats()
        
        assert isinstance(formats, dict)
        assert len(formats) > 0, "Should have available formats"
    
    def test_get_format_requirements(self):
        """Test getting format requirements."""
        from core.processing_controller import ProcessingController
        
        controller = ProcessingController()
        requirements = controller.get_format_requirements('ICS-UAE')
        
        assert requirements is not None, "Should get requirements for ICS-UAE"
        assert isinstance(requirements, dict), "Requirements should be a dictionary"
    
    def test_process_image_invalid_file(self):
        """Test processing with invalid file path."""
        from core.processing_controller import ProcessingController
        
        controller = ProcessingController()
        result = controller.process_image('nonexistent_file.jpg', 'ICS-UAE')
        
        assert not result.success, "Should fail for nonexistent file"
        assert "not found" in result.error_message.lower(), "Should indicate file not found"
    
    def test_process_image_invalid_format(self):
        """Test processing with invalid format."""
        from core.processing_controller import ProcessingController
        
        controller = ProcessingController()
        
        # Create a temporary test file
        test_file = Path("test_temp.txt")
        test_file.write_text("test")
        
        try:
            result = controller.process_image(str(test_file), 'InvalidFormat')
            assert not result.success, "Should fail for invalid format"
            assert "format" in result.error_message.lower(), "Should indicate invalid format"
        finally:
            if test_file.exists():
                test_file.unlink()


class TestRequirements:
    """Test that requirements.txt is properly configured."""
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        assert os.path.exists("requirements.txt"), "requirements.txt should exist"
    
    def test_essential_dependencies(self):
        """Test that essential dependencies are in requirements.txt."""
        with open("requirements.txt", 'r') as f:
            content = f.read()
        
        essential_deps = ['numpy', 'opencv-python', 'Pillow', 'PyQt5']
        for dep in essential_deps:
            assert dep in content, f"Essential dependency {dep} should be in requirements.txt"
    
    def test_no_heavy_dependencies(self):
        """Test that heavy/unnecessary dependencies are removed."""
        with open("requirements.txt", 'r') as f:
            content = f.read()
        
        # These should not be in the simplified requirements
        heavy_deps = ['torch', 'torchvision', 'ultralytics', 'segment-anything']
        for dep in heavy_deps:
            assert dep not in content, f"Heavy dependency {dep} should not be in simplified requirements.txt"


if __name__ == "__main__":
    pytest.main([__file__])