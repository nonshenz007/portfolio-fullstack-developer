
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from PIL import Image


from config.config_manager import ConfigManager, FormatRule
from utils.file_manager import FileManager


class TestFormatDetector:
    """Test cases for FormatDetector class."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager with test formats."""
        config_manager = Mock(spec=ConfigManager)
        test_formats = {
            'ICS-UAE': FormatRule(
                display_name='ICS (UAE)',
                dimensions={'width': 945, 'height': 1417, 'unit': 'pixels'},
                face_requirements={'height_ratio': [0.70, 0.80]},
                background={'color': 'white', 'rgb_values': [255, 255, 255]},
                file_specs={'format': 'JPEG', 'max_size_mb': 2}
            ),
            'US-Visa': FormatRule(
                display_name='US Visa',
                dimensions={'width': 600, 'height': 600, 'unit': 'pixels'},
                face_requirements={'height_ratio': [0.69, 0.80]},
                background={'color': 'white', 'rgb_values': [255, 255, 255]},
                file_specs={'format': 'JPEG', 'max_size_mb': 10}
            ),
            'India-Passport': FormatRule(
                display_name='India Passport',
                dimensions={'width': 213, 'height': 213, 'unit': 'pixels'},
                face_requirements={'height_inches': [1.0, 1.375]},
                background={'color': 'white', 'rgb_values': [255, 255, 255]},
                file_specs={'format': 'JPEG', 'max_size_mb': 1}
            )
        }
        config_manager.get_available_formats.return_value = list(test_formats.keys())
        config_manager.get_format_rules.side_effect = lambda x: test_formats.get(x)
        return config_manager
    
    @pytest.fixture
    def format_detector(self, mock_config_manager):
        """Create a FormatDetector instance."""
        return FormatDetector(mock_config_manager)
    
    @pytest.fixture
    def temp_image_dir(self):
        """Create a temporary directory with test images."""
        temp_dir = tempfile.mkdtemp()
        
        # Create test images with different dimensions
        test_images = [
            ('ics_uae_exact.jpg', 945, 1417),
            ('ics_uae_close.jpg', 950, 1420),
            ('us_visa_exact.jpg', 600, 600),
            ('us_visa_close.jpg', 605, 595),
            ('india_passport_exact.jpg', 213, 213),
            ('random_size.jpg', 800, 1200),
            ('square_medium.jpg', 500, 500)
        ]
        
        for filename, width, height in test_images:
            img = Image.new('RGB', (width, height), color='white')
            img.save(os.path.join(temp_dir, filename))
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_detect_format_exact_match(self, format_detector, temp_image_dir):
        """Test format detection with exact dimension matches."""
        # Test ICS-UAE exact match
        ics_path = os.path.join(temp_image_dir, 'ics_uae_exact.jpg')
        result = format_detector.detect_format(ics_path)
        
        assert result is not None
        assert result.format_name == 'ICS-UAE'
        assert result.confidence >= 0.9
        assert result.score > 0.9
        assert any('dimension match' in reason.lower() for reason in result.reasons)
    
    def test_detect_format_close_match(self, format_detector, temp_image_dir):
        """Test format detection with close dimension matches."""
        # Test ICS-UAE close match
        ics_path = os.path.join(temp_image_dir, 'ics_uae_close.jpg')
        result = format_detector.detect_format(ics_path)
        
        assert result is not None
        assert result.format_name == 'ICS-UAE'
        assert result.confidence >= 0.6
        assert result.score > 0.6
    
    def test_detect_format_square_images(self, format_detector, temp_image_dir):
        """Test format detection for square images."""
        # Test US Visa (square format)
        us_visa_path = os.path.join(temp_image_dir, 'us_visa_exact.jpg')
        result = format_detector.detect_format(us_visa_path)
        
        assert result is not None
        assert result.format_name == 'US-Visa'
        assert result.confidence >= 0.9
        
        # Test India Passport (also square)
        india_path = os.path.join(temp_image_dir, 'india_passport_exact.jpg')
        result = format_detector.detect_format(india_path)
        
        assert result is not None
        assert result.format_name == 'India-Passport'
        assert result.confidence >= 0.9
    
    def test_detect_format_no_good_match(self, format_detector, temp_image_dir):
        """Test format detection when no format matches well."""
        # Test with random dimensions that don't match any format well
        random_path = os.path.join(temp_image_dir, 'random_size.jpg')
        result = format_detector.detect_format(random_path)
        
        # Should return None if confidence is below threshold
        if result is not None:
            assert result.confidence < 0.8  # Should have low confidence
    
    def test_get_all_format_scores(self, format_detector, temp_image_dir):
        """Test getting scores for all formats."""
        ics_path = os.path.join(temp_image_dir, 'ics_uae_exact.jpg')
        scores = format_detector.get_all_format_scores(ics_path)
        
        assert len(scores) == 3  # Should have scores for all 3 formats
        assert all(isinstance(score, FormatScore) for score in scores)
        assert scores[0].score >= scores[1].score >= scores[2].score  # Should be sorted
        assert scores[0].format_name == 'ICS-UAE'  # Best match should be first
    
    def test_calculate_dimension_score(self, format_detector):
        """Test dimension score calculation."""
        # Test exact match
        score, reasons = format_detector._calculate_dimension_score(945, 1417, 945, 1417)
        assert score == 1.0
        assert any('exact' in reason.lower() for reason in reasons)
        
        # Test close match
        score, reasons = format_detector._calculate_dimension_score(950, 1420, 945, 1417)
        assert 0.7 <= score < 1.0
        assert any('close' in reason.lower() for reason in reasons)
        
        # Test poor match
        score, reasons = format_detector._calculate_dimension_score(500, 500, 945, 1417)
        assert score < 0.5
        assert any('mismatch' in reason.lower() for reason in reasons)
    
    def test_calculate_aspect_ratio_score(self, format_detector):
        """Test aspect ratio score calculation."""
        # Test perfect aspect ratio match
        score, reasons = format_detector._calculate_aspect_ratio_score(945, 1417, 945, 1417)
        assert score == 1.0
        assert any('perfect' in reason.lower() for reason in reasons)
        
        # Test good aspect ratio match (different size, same ratio)
        score, reasons = format_detector._calculate_aspect_ratio_score(472, 708, 945, 1417)
        assert score >= 0.9
        assert any('match' in reason.lower() for reason in reasons)
        
        # Test poor aspect ratio match
        score, reasons = format_detector._calculate_aspect_ratio_score(600, 600, 945, 1417)
        assert score < 0.8
        assert any('mismatch' in reason.lower() for reason in reasons)
    
    def test_detect_format_invalid_image(self, format_detector, temp_image_dir):
        """Test format detection with invalid image file."""
        # Create a non-image file
        invalid_path = os.path.join(temp_image_dir, 'invalid.txt')
        with open(invalid_path, 'w') as f:
            f.write('This is not an image')
        
        result = format_detector.detect_format(invalid_path)
        assert result is None
    
    def test_detect_format_nonexistent_file(self, format_detector):
        """Test format detection with nonexistent file."""
        result = format_detector.detect_format('nonexistent.jpg')
        assert result is None



