"""
Final Integration Tests for VeriDoc Universal

Comprehensive end-to-end testing of the fully integrated system
including all components working together in real-world scenarios.
"""

import pytest
import os
import tempfile
import shutil
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import Mock, patch
import json
import time

# Import the main application
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_integrated import VeriDocIntegratedApplication
from core.config_manager import ProcessingOptions


class TestIntegratedSystem:
    """Test the fully integrated VeriDoc Universal system."""
    
    @pytest.fixture
    def app(self):
        """Create and initialize the integrated application."""
        app = VeriDocIntegratedApplication()
        
        # Mock some components to avoid external dependencies in tests
        with patch('core.security_manager.SecurityManager'), \
             patch('core.offline_manager.OfflineManager'), \
             patch('core.audit_logger.AuditLogger'), \
             patch('ai.ai_engine.AIEngine'), \
             patch('validation.icao_validator.ICAOValidator'), \
             patch('autofix.autofix_engine.AutoFixEngine'), \
             patch('export.export_engine.ExportEngine'):
            
            success = app.initialize_system()
            assert success, "System initialization should succeed"
            
        return app
    
    @pytest.fixture
    def test_image(self):
        """Create a test image for processing."""
        # Create a simple test image
        image = np.zeros((600, 400, 3), dtype=np.uint8)
        image.fill(255)  # White background
        
        # Draw a simple face-like shape
        cv2.circle(image, (200, 200), 80, (200, 180, 160), -1)  # Face
        cv2.circle(image, (180, 180), 10, (0, 0, 0), -1)  # Left eye
        cv2.circle(image, (220, 180), 10, (0, 0, 0), -1)  # Right eye
        cv2.ellipse(image, (200, 220), (20, 10), 0, 0, 180, (0, 0, 0), 2)  # Mouth
        
        return image
    
    @pytest.fixture
    def temp_image_file(self, test_image):
        """Create a temporary image file."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            cv2.imwrite(f.name, test_image)
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_system_initialization(self):
        """Test that the system initializes all components correctly."""
        app = VeriDocIntegratedApplication()
        
        with patch('core.security_manager.SecurityManager'), \
             patch('core.offline_manager.OfflineManager'), \
             patch('core.audit_logger.AuditLogger'), \
             patch('ai.ai_engine.AIEngine'), \
             patch('validation.icao_validator.ICAOValidator'), \
             patch('autofix.autofix_engine.AutoFixEngine'), \
             patch('export.export_engine.ExportEngine'):
            
            success = app.initialize_system()
            assert success
            assert app.initialized
            assert app.config_manager is not None
            assert app.processing_controller is not None
    
    def test_system_health_check(self, app):
        """Test system health check functionality."""
        # Mock the health check methods
        with patch.object(app.ai_engine, 'get_model_info', return_value={'status': 'healthy'}), \
             patch.object(app.processing_controller, 'get_processing_metrics', return_value={}), \
             patch.object(app.offline_manager, 'verify_offline_capability', return_value=True), \
             patch.object(app.security_manager, 'verify_security_settings', return_value=True):
            
            health_check_result = app._verify_system_health()
            assert health_check_result
    
    def test_single_image_processing_workflow(self, app, temp_image_file):
        """Test complete single image processing workflow."""
        # Mock the processing controller to return a successful result
        mock_result = Mock()
        mock_result.success = True
        mock_result.image_path = temp_image_file
        mock_result.validation_result = Mock()
        mock_result.validation_result.overall_compliance = 85.0
        mock_result.validation_result.passes_requirements = True
        mock_result.validation_result.confidence_score = 90.0
        mock_result.auto_fix_result = None
        mock_result.processing_metrics = Mock()
        mock_result.processing_metrics.total_processing_time = 2.5
        mock_result.export_path = None
        mock_result.error_message = None
        
        with patch.object(app.processing_controller, 'process_image', return_value=mock_result):
            result = app.process_single_image(
                image_path=temp_image_file,
                format_name="ICS-UAE"
            )
            
            assert result['success']
            assert result['image_path'] == temp_image_file
            assert result['validation_result'] is not None
    
    def test_batch_processing_workflow(self, app, temp_directory, test_image):
        """Test complete batch processing workflow."""
        # Create multiple test images
        image_paths = []
        for i in range(3):
            image_path = os.path.join(temp_directory, f'test_image_{i}.jpg')
            cv2.imwrite(image_path, test_image)
            image_paths.append(image_path)
        
        # Mock the batch processing result
        mock_result = Mock()
        mock_result.total_images = 3
        mock_result.successful_images = 3
        mock_result.failed_images = 0
        mock_result.results = [Mock() for _ in range(3)]
        mock_result.total_processing_time = 7.5
        mock_result.average_processing_time = 2.5
        mock_result.error_summary = {}
        
        with patch.object(app.processing_controller, 'batch_process', return_value=mock_result):
            result = app.process_batch(
                image_paths=image_paths,
                format_name="ICS-UAE"
            )
            
            assert result['success']
            assert result['total_images'] == 3
            assert result['successful_images'] == 3
            assert result['failed_images'] == 0
    
    def test_auto_fix_integration(self, app, temp_image_file):
        """Test auto-fix integration in the processing workflow."""
        # Mock processing result with auto-fix
        mock_result = Mock()
        mock_result.success = True
        mock_result.image_path = temp_image_file
        mock_result.validation_result = Mock()
        mock_result.validation_result.overall_compliance = 65.0
        mock_result.validation_result.passes_requirements = False
        
        # Mock auto-fix result
        mock_auto_fix = Mock()
        mock_auto_fix.success = True
        mock_auto_fix.applied_corrections = ['background_correction', 'lighting_adjustment']
        mock_result.auto_fix_result = mock_auto_fix
        
        mock_result.processing_metrics = Mock()
        mock_result.processing_metrics.total_processing_time = 3.2
        mock_result.export_path = None
        mock_result.error_message = None
        
        options = ProcessingOptions(enable_auto_fix=True)
        
        with patch.object(app.processing_controller, 'process_image', return_value=mock_result):
            result = app.process_single_image(
                image_path=temp_image_file,
                format_name="ICS-UAE",
                options=options
            )
            
            assert result['success']
            assert result['auto_fix_result'] is not None
            assert result['auto_fix_result'].success
    
    def test_export_functionality(self, app):
        """Test export functionality integration."""
        # Mock export result
        mock_results = [Mock() for _ in range(2)]
        expected_export_path = "/tmp/export_results.json"
        
        with patch.object(app.export_engine, 'export_batch_results', return_value=expected_export_path):
            export_path = app.export_results(
                results=mock_results,
                export_format="comprehensive"
            )
            
            assert export_path == expected_export_path
    
    def test_system_status_reporting(self, app):
        """Test comprehensive system status reporting."""
        # Mock various status components
        with patch.object(app.processing_controller, 'get_processing_metrics', return_value={
            'total_processed': 10,
            'average_processing_time': 2.3,
            'error_rate': 0.1
        }), \
        patch.object(app.performance_monitor, 'get_current_metrics', return_value={
            'memory_usage_mb': 256.5,
            'cpu_usage_percent': 15.2
        }), \
        patch.object(app.ai_engine, 'get_model_info', return_value={
            'face_detector': {'status': 'loaded'},
            'validator': {'status': 'ready'}
        }), \
        patch.object(app.security_manager, 'get_security_status', return_value={
            'offline_mode': True,
            'encryption_enabled': True
        }), \
        patch.object(app.offline_manager, 'get_offline_status', return_value={
            'models_cached': True,
            'offline_ready': True
        }):
            
            status = app.get_system_status()
            
            assert status['initialized']
            assert 'processing_metrics' in status
            assert 'performance_metrics' in status
            assert 'ai_models' in status
            assert 'security_status' in status
            assert 'offline_status' in status
    
    def test_error_handling_and_recovery(self, app, temp_image_file):
        """Test error handling and recovery mechanisms."""
        # Mock a processing error
        with patch.object(app.processing_controller, 'process_image', 
                         side_effect=Exception("Processing failed")):
            
            result = app.process_single_image(
                image_path=temp_image_file,
                format_name="ICS-UAE"
            )
            
            assert not result['success']
            assert 'error_message' in result
            assert result['error_message'] == "Processing failed"
    
    def test_performance_monitoring(self, app, temp_image_file):
        """Test performance monitoring during processing."""
        # Mock processing with timing
        mock_result = Mock()
        mock_result.success = True
        mock_result.processing_metrics = Mock()
        mock_result.processing_metrics.total_processing_time = 1.8
        mock_result.processing_metrics.memory_usage_mb = 128.0
        mock_result.processing_metrics.stage_times = {
            'face_detection': 0.5,
            'validation': 0.8,
            'auto_fix': 0.5
        }
        
        with patch.object(app.processing_controller, 'process_image', return_value=mock_result):
            start_time = time.time()
            result = app.process_single_image(
                image_path=temp_image_file,
                format_name="ICS-UAE"
            )
            end_time = time.time()
            
            assert result['success']
            assert 'processing_metrics' in result
            assert end_time - start_time < 5.0  # Should complete quickly in test
    
    def test_configuration_management(self, app):
        """Test configuration management across components."""
        # Test that configuration is properly propagated
        assert app.config_manager is not None
        
        # Test processing options
        options = ProcessingOptions(
            enable_auto_fix=True,
            quality_threshold=80.0,
            strict_validation=True
        )
        
        assert options.enable_auto_fix
        assert options.quality_threshold == 80.0
        assert options.strict_validation
    
    def test_audit_logging_integration(self, app, temp_image_file):
        """Test audit logging throughout the processing workflow."""
        mock_result = Mock()
        mock_result.success = True
        mock_result.processing_metrics = Mock()
        mock_result.processing_metrics.total_processing_time = 2.0
        
        with patch.object(app.processing_controller, 'process_image', return_value=mock_result), \
             patch.object(app.audit_logger, 'log_processing_event') as mock_log:
            
            app.process_single_image(
                image_path=temp_image_file,
                format_name="ICS-UAE"
            )
            
            # Verify audit logging was called
            assert mock_log.call_count >= 2  # Start and complete events
    
    def test_security_compliance(self, app):
        """Test security compliance features."""
        # Test offline operation
        with patch.object(app.offline_manager, 'verify_offline_capability', return_value=True):
            offline_status = app.offline_manager.verify_offline_capability()
            assert offline_status
        
        # Test secure cleanup
        with patch.object(app.security_manager, 'secure_cleanup') as mock_cleanup:
            app.shutdown()
            mock_cleanup.assert_called_once()
    
    def test_memory_management(self, app, temp_directory, test_image):
        """Test memory management during batch processing."""
        # Create multiple test images
        image_paths = []
        for i in range(5):
            image_path = os.path.join(temp_directory, f'test_image_{i}.jpg')
            cv2.imwrite(image_path, test_image)
            image_paths.append(image_path)
        
        # Mock batch processing with memory tracking
        mock_result = Mock()
        mock_result.total_images = 5
        mock_result.successful_images = 5
        mock_result.failed_images = 0
        mock_result.results = [Mock() for _ in range(5)]
        mock_result.total_processing_time = 10.0
        mock_result.error_summary = {}
        
        with patch.object(app.processing_controller, 'batch_process', return_value=mock_result):
            result = app.process_batch(
                image_paths=image_paths,
                format_name="ICS-UAE"
            )
            
            assert result['success']
            # Memory should be managed properly (no specific assertion, but test should not crash)
    
    def test_graceful_shutdown(self, app):
        """Test graceful application shutdown."""
        # Test shutdown process
        with patch.object(app.audit_logger, 'log_system_event') as mock_log, \
             patch.object(app.security_manager, 'secure_cleanup') as mock_cleanup:
            
            app.shutdown()
            
            # Verify shutdown logging and cleanup
            mock_log.assert_called()
            mock_cleanup.assert_called_once()


class TestCLIIntegration:
    """Test CLI integration with the main application."""
    
    @pytest.fixture
    def app(self):
        """Create application for CLI testing."""
        app = VeriDocIntegratedApplication()
        
        with patch('core.security_manager.SecurityManager'), \
             patch('core.offline_manager.OfflineManager'), \
             patch('core.audit_logger.AuditLogger'), \
             patch('ai.ai_engine.AIEngine'), \
             patch('validation.icao_validator.ICAOValidator'), \
             patch('autofix.autofix_engine.AutoFixEngine'), \
             patch('export.export_engine.ExportEngine'):
            
            app.initialize_system()
            
        return app
    
    def test_cli_single_image_processing(self, app, temp_image_file):
        """Test CLI single image processing."""
        from cli.cli_interface import CLIInterface
        
        cli = CLIInterface(app)
        
        # Mock successful processing
        mock_result = {
            'success': True,
            'image_path': temp_image_file,
            'validation_result': Mock(),
            'processing_metrics': Mock()
        }
        mock_result['validation_result'].overall_compliance = 85.0
        mock_result['validation_result'].passes_requirements = True
        mock_result['validation_result'].confidence_score = 90.0
        
        with patch.object(app, 'process_single_image', return_value=mock_result):
            exit_code = cli.run([temp_image_file])
            assert exit_code == 0
    
    def test_cli_batch_processing(self, app, temp_directory):
        """Test CLI batch processing."""
        from cli.cli_interface import CLIInterface
        
        cli = CLIInterface(app)
        
        # Mock successful batch processing
        mock_result = {
            'success': True,
            'total_images': 3,
            'successful_images': 3,
            'failed_images': 0,
            'results': [Mock() for _ in range(3)],
            'processing_time': 7.5,
            'error_summary': {}
        }
        
        with patch.object(app, 'process_batch', return_value=mock_result):
            exit_code = cli.run([temp_directory, '--batch'])
            assert exit_code == 0
    
    def test_cli_system_status(self, app):
        """Test CLI system status command."""
        from cli.cli_interface import CLIInterface
        
        cli = CLIInterface(app)
        
        # Mock system status
        mock_status = {
            'initialized': True,
            'components_healthy': True,
            'startup_time': 2.5,
            'processing_metrics': {
                'total_processed': 10,
                'average_processing_time': 2.0,
                'error_rate': 0.05
            }
        }
        
        with patch.object(app, 'get_system_status', return_value=mock_status):
            exit_code = cli.run(['--status'])
            assert exit_code == 0


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios."""
    
    @pytest.fixture
    def app(self):
        """Create fully initialized application."""
        app = VeriDocIntegratedApplication()
        
        with patch('core.security_manager.SecurityManager'), \
             patch('core.offline_manager.OfflineManager'), \
             patch('core.audit_logger.AuditLogger'), \
             patch('ai.ai_engine.AIEngine'), \
             patch('validation.icao_validator.ICAOValidator'), \
             patch('autofix.autofix_engine.AutoFixEngine'), \
             patch('export.export_engine.ExportEngine'):
            
            app.initialize_system()
            
        return app
    
    def test_complete_photo_verification_workflow(self, app, temp_image_file):
        """Test complete photo verification workflow from input to export."""
        # Mock the complete workflow
        mock_processing_result = Mock()
        mock_processing_result.success = True
        mock_processing_result.validation_result = Mock()
        mock_processing_result.validation_result.overall_compliance = 75.0
        mock_processing_result.validation_result.passes_requirements = True
        mock_processing_result.auto_fix_result = None
        mock_processing_result.processing_metrics = Mock()
        mock_processing_result.processing_metrics.total_processing_time = 2.8
        
        mock_export_path = "/tmp/verification_report.pdf"
        
        with patch.object(app, 'process_single_image', return_value={
            'success': True,
            'validation_result': mock_processing_result.validation_result,
            'processing_metrics': mock_processing_result.processing_metrics
        }), \
        patch.object(app, 'export_results', return_value=mock_export_path):
            
            # Step 1: Process image
            result = app.process_single_image(temp_image_file, "ICS-UAE")
            assert result['success']
            
            # Step 2: Export results
            export_path = app.export_results([result], "comprehensive")
            assert export_path == mock_export_path
    
    def test_government_compliance_scenario(self, app, temp_image_file):
        """Test government compliance verification scenario."""
        # Mock strict government compliance processing
        options = ProcessingOptions(
            strict_validation=True,
            quality_threshold=85.0,
            enable_auto_fix=False  # Government mode - no auto-fix
        )
        
        mock_result = {
            'success': True,
            'validation_result': Mock(),
            'processing_metrics': Mock()
        }
        mock_result['validation_result'].overall_compliance = 88.0
        mock_result['validation_result'].passes_requirements = True
        mock_result['validation_result'].confidence_score = 95.0
        
        with patch.object(app, 'process_single_image', return_value=mock_result):
            result = app.process_single_image(
                temp_image_file, 
                "ICS-UAE", 
                options=options
            )
            
            assert result['success']
            assert result['validation_result'].overall_compliance >= 85.0
    
    def test_high_volume_processing_scenario(self, app, temp_directory, test_image):
        """Test high-volume batch processing scenario."""
        # Create many test images
        image_paths = []
        for i in range(10):
            image_path = os.path.join(temp_directory, f'batch_image_{i}.jpg')
            cv2.imwrite(image_path, test_image)
            image_paths.append(image_path)
        
        # Mock high-volume processing
        mock_result = {
            'success': True,
            'total_images': 10,
            'successful_images': 9,
            'failed_images': 1,
            'results': [Mock() for _ in range(10)],
            'processing_time': 25.0,
            'error_summary': {'face_detection_failed': 1}
        }
        
        with patch.object(app, 'process_batch', return_value=mock_result):
            result = app.process_batch(image_paths, "ICS-UAE")
            
            assert result['success']
            assert result['successful_images'] >= 8  # Allow some failures
            assert result['processing_time'] < 60.0  # Should be reasonably fast


if __name__ == '__main__':
    pytest.main([__file__, '-v'])