"""
Unit tests for dependency loading and availability.

Tests that all required dependencies can be imported and are
available for use in the application.
"""

import unittest
import sys
import importlib
import subprocess
from pathlib import Path


class TestDependencyLoading(unittest.TestCase):
    """Test that all required dependencies can be loaded."""
    
    def setUp(self):
        """Set up test environment."""
        self.required_dependencies = [
            # Core dependencies
            'numpy',
            'cv2',  # opencv-python
            'PIL',  # Pillow
            'PyQt6',
            
            # AI and Computer Vision
            'ultralytics',
            'mediapipe',
            'torch',
            'torchvision',
            'onnxruntime',
            'skimage',  # scikit-image
            
            # Background processing
            'rembg',
            
            # Data processing
            'scipy',
            'pandas',
            'pydantic',
            'requests',
            'tqdm',
            
            # Configuration
            'yaml',
            'jsonschema',
            
            # Testing
            'pytest'
        ]
        
        self.optional_dependencies = [
            'segment_anything',  # May not be available
            'black',
            'flake8',
            'mypy',
            'watchdog'  # For config file watching
        ]
    
    def test_core_dependencies_import(self):
        """Test that core dependencies can be imported."""
        for dep in self.required_dependencies:
            with self.subTest(dependency=dep):
                try:
                    if dep == 'cv2':
                        import cv2
                        # Test basic OpenCV functionality
                        self.assertTrue(hasattr(cv2, 'imread'))
                        self.assertTrue(hasattr(cv2, 'imwrite'))
                    elif dep == 'PIL':
                        from PIL import Image
                        self.assertTrue(hasattr(Image, 'open'))
                    elif dep == 'PyQt6':
                        from PyQt6.QtWidgets import QApplication
                        self.assertTrue(hasattr(QApplication, 'instance'))
                    elif dep == 'skimage':
                        import skimage
                        from skimage import measure
                        self.assertTrue(hasattr(measure, 'label'))
                    elif dep == 'yaml':
                        import yaml
                        self.assertTrue(hasattr(yaml, 'safe_load'))
                    else:
                        importlib.import_module(dep)
                        
                except ImportError as e:
                    self.fail(f"Required dependency {dep} could not be imported: {e}")
    
    def test_ai_dependencies_functionality(self):
        """Test AI dependencies have expected functionality."""
        
        # Test NumPy
        try:
            import numpy as np
            arr = np.array([1, 2, 3])
            self.assertEqual(arr.shape, (3,))
        except ImportError:
            self.fail("NumPy not available")
        
        # Test OpenCV
        try:
            import cv2
            # Test that we can create a basic image
            img = cv2.imread('non_existent.jpg')  # Should return None, not crash
            self.assertIsNone(img)
            
            # Test basic image operations
            test_img = np.zeros((100, 100, 3), dtype=np.uint8)
            gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
            self.assertEqual(gray.shape, (100, 100))
            
        except ImportError:
            self.fail("OpenCV not available")
        except Exception as e:
            self.fail(f"OpenCV functionality test failed: {e}")
        
        # Test PyTorch
        try:
            import torch
            tensor = torch.tensor([1.0, 2.0, 3.0])
            self.assertEqual(tensor.shape, (3,))
            
            # Check if CUDA is available (optional)
            cuda_available = torch.cuda.is_available()
            print(f"CUDA available: {cuda_available}")
            
        except ImportError:
            self.fail("PyTorch not available")
        
        # Test Ultralytics (YOLOv8)
        try:
            from ultralytics import YOLO
            # Don't actually load a model in tests, just check import
            self.assertTrue(hasattr(YOLO, '__init__'))
        except ImportError:
            self.fail("Ultralytics (YOLOv8) not available")
        
        # Test MediaPipe
        try:
            import mediapipe as mp
            self.assertTrue(hasattr(mp.solutions, 'face_mesh'))
        except ImportError:
            self.fail("MediaPipe not available")
    
    def test_optional_dependencies(self):
        """Test optional dependencies (should not fail if missing)."""
        for dep in self.optional_dependencies:
            with self.subTest(dependency=dep):
                try:
                    importlib.import_module(dep)
                    print(f"Optional dependency {dep} is available")
                except ImportError:
                    print(f"Optional dependency {dep} is not available (OK)")
    
    def test_version_compatibility(self):
        """Test that dependencies meet minimum version requirements."""
        version_requirements = {
            'numpy': '1.24.0',
            'opencv-python': '4.8.0',  # Will check cv2.__version__
            'torch': '2.0.0',
            'mediapipe': '0.10.0'
        }
        
        for package, min_version in version_requirements.items():
            with self.subTest(package=package):
                try:
                    if package == 'opencv-python':
                        import cv2
                        version = cv2.__version__
                    else:
                        module = importlib.import_module(package)
                        version = getattr(module, '__version__', '0.0.0')
                    
                    # Simple version comparison (works for most cases)
                    version_parts = [int(x) for x in version.split('.')]
                    min_parts = [int(x) for x in min_version.split('.')]
                    
                    # Pad shorter version with zeros
                    max_len = max(len(version_parts), len(min_parts))
                    version_parts.extend([0] * (max_len - len(version_parts)))
                    min_parts.extend([0] * (max_len - len(min_parts)))
                    
                    self.assertGreaterEqual(
                        version_parts, 
                        min_parts,
                        f"{package} version {version} is below minimum {min_version}"
                    )
                    
                except ImportError:
                    self.skipTest(f"{package} not available for version check")
                except (AttributeError, ValueError) as e:
                    print(f"Could not check version for {package}: {e}")
    
    def test_gpu_availability(self):
        """Test GPU availability for AI processing (informational)."""
        gpu_info = {}
        
        # Check PyTorch CUDA
        try:
            import torch
            gpu_info['pytorch_cuda'] = torch.cuda.is_available()
            if torch.cuda.is_available():
                gpu_info['pytorch_gpu_count'] = torch.cuda.device_count()
                gpu_info['pytorch_gpu_name'] = torch.cuda.get_device_name(0)
        except ImportError:
            gpu_info['pytorch_cuda'] = False
        
        # Check OpenCV GPU support
        try:
            import cv2
            gpu_info['opencv_gpu'] = cv2.cuda.getCudaEnabledDeviceCount() > 0
        except (ImportError, AttributeError):
            gpu_info['opencv_gpu'] = False
        
        print(f"GPU availability: {gpu_info}")
        
        # This is informational, not a failure condition
        self.assertIsInstance(gpu_info, dict)
    
    def test_model_download_capability(self):
        """Test that we can download models (without actually downloading)."""
        try:
            import requests
            
            # Test that we can make HTTP requests
            response = requests.get('https://httpbin.org/status/200', timeout=5)
            self.assertEqual(response.status_code, 200)
            
        except ImportError:
            self.fail("Requests library not available for model downloads")
        except requests.exceptions.RequestException:
            print("Network not available for model download test (OK)")
    
    def test_file_format_support(self):
        """Test that we can handle required file formats."""
        try:
            from PIL import Image
            import io
            
            # Test basic image format support
            formats_to_test = ['JPEG', 'PNG', 'BMP']
            
            for fmt in formats_to_test:
                with self.subTest(format=fmt):
                    # Create a small test image
                    img = Image.new('RGB', (10, 10), color='red')
                    
                    # Test saving to memory
                    buffer = io.BytesIO()
                    img.save(buffer, format=fmt)
                    buffer.seek(0)
                    
                    # Test loading from memory
                    loaded_img = Image.open(buffer)
                    self.assertEqual(loaded_img.size, (10, 10))
                    
        except ImportError:
            self.fail("PIL not available for image format testing")
        except Exception as e:
            self.fail(f"Image format support test failed: {e}")


class TestConfigurationDependencies(unittest.TestCase):
    """Test configuration and file handling dependencies."""
    
    def test_yaml_functionality(self):
        """Test YAML configuration file handling."""
        try:
            import yaml
            
            test_config = {
                'processing': {
                    'quality_threshold': 0.7,
                    'use_gpu': True
                },
                'models': {
                    'face_detection': 'yolov8n-face'
                }
            }
            
            # Test YAML serialization
            yaml_str = yaml.dump(test_config)
            self.assertIsInstance(yaml_str, str)
            
            # Test YAML deserialization
            loaded_config = yaml.safe_load(yaml_str)
            self.assertEqual(loaded_config, test_config)
            
        except ImportError:
            self.fail("YAML library not available")
    
    def test_json_schema_validation(self):
        """Test JSON schema validation capability."""
        try:
            import jsonschema
            
            schema = {
                "type": "object",
                "properties": {
                    "quality_threshold": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["quality_threshold"]
            }
            
            valid_data = {"quality_threshold": 0.7}
            invalid_data = {"quality_threshold": 1.5}
            
            # Should not raise exception
            jsonschema.validate(valid_data, schema)
            
            # Should raise exception
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(invalid_data, schema)
                
        except ImportError:
            self.fail("JSON Schema library not available")


if __name__ == '__main__':
    # Run with verbose output to see GPU info and optional dependencies
    unittest.main(verbosity=2)