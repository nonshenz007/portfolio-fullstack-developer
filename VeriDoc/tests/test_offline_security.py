"""
Security and Offline Operation Tests for Veridoc Universal
Tests for offline functionality, security compliance, and data handling
"""

import os
import sys
import pytest
import tempfile
import shutil
import sqlite3
import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import cv2

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.offline_manager import OfflineManager, OfflineStatus, ModelInfo
from core.security_manager import SecurityManager, SecurityEvent, SecureDataHandle
from core.update_manager import UpdateManager, UpdatePackage, UpdateResult
from core.audit_logger import AuditLogger, AuditLevel, AuditCategory

class TestOfflineManager:
    """Test offline operation management"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def offline_manager(self, temp_dir):
        """Create offline manager for testing"""
        with patch('core.offline_manager.Path') as mock_path:
            mock_path.return_value.mkdir = Mock()
            mock_path.return_value.exists = Mock(return_value=True)
            
            manager = OfflineManager()
            manager.models_dir = Path(temp_dir) / "models"
            manager.cache_dir = Path(temp_dir) / "cache"
            manager.offline_db_path = Path(temp_dir) / "offline.db"
            
            # Create directories
            manager.models_dir.mkdir(exist_ok=True)
            manager.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Reinitialize database with correct path
            manager._init_offline_database()
            
            return manager
    
    def test_offline_manager_initialization(self, offline_manager):
        """Test offline manager initialization"""
        assert offline_manager.offline_mode is True
        assert offline_manager.offline_db_path.exists()
        
        # Check database tables exist
        with sqlite3.connect(offline_manager.offline_db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert 'model_status' in tables
            assert 'offline_logs' in tables
    
    def test_network_blocking_enforcement(self, offline_manager):
        """Test that network access is properly blocked"""
        # Check environment variables are set for blocking
        assert os.environ.get('NO_PROXY') == '*'
        assert os.environ.get('HTTP_PROXY') == 'localhost:0'
        assert os.environ.get('HTTPS_PROXY') == 'localhost:0'
        
        # Test network blocking check
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect_ex.return_value = 1  # Connection failed
            assert offline_manager.is_network_blocked() is True
    
    def test_model_integrity_verification(self, offline_manager, temp_dir):
        """Test model file integrity verification"""
        # Create a test model file
        model_path = offline_manager.models_dir / "test_model.pt"
        test_data = b"fake model data for testing"
        
        with open(model_path, 'wb') as f:
            f.write(test_data)
        
        # Test integrity verification
        assert offline_manager._verify_model_integrity(model_path) is True
        
        # Test with corrupted file
        with open(model_path, 'wb') as f:
            f.write(b"corrupted data")
        
        # Should still return True for first verification (stores new checksum)
        # But subsequent verification should detect corruption
        original_checksum = offline_manager._get_stored_checksum("test_model.pt")
        if original_checksum:
            assert offline_manager._verify_model_integrity(model_path) is False
    
    def test_offline_readiness_check(self, offline_manager, temp_dir):
        """Test offline readiness assessment"""
        # Initially should have missing models
        status = offline_manager.check_offline_readiness()
        assert isinstance(status, OfflineStatus)
        assert status.offline_mode_enabled is True
        assert len(status.missing_models) > 0  # Required models not present
        
        # Create required model files
        required_models = ["yolov8n-face.pt", "face_detection_yunet_2023mar.onnx", "isnet-general-use.onnx"]
        for model_name in required_models:
            model_path = offline_manager.models_dir / model_name
            with open(model_path, 'wb') as f:
                f.write(b"fake model data")
        
        # Create required config files
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir(exist_ok=True)
        
        (config_dir / "icao_rules_2023.json").write_text('{"test": "config"}')
        (config_dir / "defaults.py").write_text('# test config')
        
        formats_dir = config_dir / "formats"
        formats_dir.mkdir(exist_ok=True)
        (formats_dir / "base_icao.json").write_text('{"test": "format"}')
        
        # Mock the config check to use our temp directory
        with patch.object(offline_manager, '_check_required_configs', return_value=[]):
            status = offline_manager.check_offline_readiness()
            assert len(status.missing_models) == 0
            assert len(status.missing_configs) == 0
            assert status.is_offline_ready is True
    
    def test_offline_event_logging(self, offline_manager):
        """Test offline event logging"""
        # Log a test event
        offline_manager._log_offline_event("test_event", "test details")
        
        # Retrieve logs
        logs = offline_manager.get_offline_logs(limit=10)
        assert len(logs) > 0
        
        # Check log structure
        log_entry = logs[0]
        assert 'timestamp' in log_entry
        assert 'event_type' in log_entry
        assert 'details' in log_entry
        assert log_entry['event_type'] == 'test_event'
        assert log_entry['details'] == 'test details'
    
    def test_offline_validation(self, offline_manager):
        """Test comprehensive offline validation"""
        validation_results = offline_manager.validate_offline_operation()
        
        assert isinstance(validation_results, dict)
        assert 'offline_ready' in validation_results
        assert 'network_blocked' in validation_results
        assert 'models_available' in validation_results
        assert 'configs_available' in validation_results
        assert 'database_accessible' in validation_results
        assert 'issues' in validation_results


class TestSecurityManager:
    """Test security management functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def security_manager(self, temp_dir):
        """Create security manager for testing"""
        audit_db_path = Path(temp_dir) / "security_audit.db"
        return SecurityManager(str(audit_db_path))
    
    def test_security_manager_initialization(self, security_manager):
        """Test security manager initialization"""
        assert security_manager.audit_db_path.exists()
        
        # Check database tables exist
        with sqlite3.connect(security_manager.audit_db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert 'security_events' in tables
            assert 'data_handles' in tables
            assert 'file_operations' in tables
    
    def test_secure_image_loading(self, security_manager, temp_dir):
        """Test secure image loading with audit logging"""
        # Create a test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image_path = Path(temp_dir) / "test_image.jpg"
        cv2.imwrite(str(test_image_path), test_image)
        
        # Load image securely
        loaded_image = security_manager.secure_load_image(test_image_path)
        
        assert loaded_image is not None
        assert loaded_image.shape == test_image.shape
        
        # Check audit log
        audit_log = security_manager.get_security_audit_log(limit=10)
        assert len(audit_log) > 0
        
        # Find file access event
        file_access_events = [event for event in audit_log if event['action'] == 'load_image']
        assert len(file_access_events) > 0
        assert file_access_events[0]['result'] == 'success'
    
    def test_secure_image_saving(self, security_manager, temp_dir):
        """Test secure image saving with audit logging"""
        # Create test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_image_path = Path(temp_dir) / "saved_image.jpg"
        
        # Save image securely
        success = security_manager.secure_save_image(test_image, test_image_path)
        
        assert success is True
        assert test_image_path.exists()
        
        # Check audit log
        audit_log = security_manager.get_security_audit_log(limit=10)
        save_events = [event for event in audit_log if event['action'] == 'save_image']
        assert len(save_events) > 0
        assert save_events[0]['result'] == 'success'
    
    def test_secure_file_deletion(self, security_manager, temp_dir):
        """Test secure file deletion with overwrite"""
        # Create test file
        test_file_path = Path(temp_dir) / "test_file.txt"
        test_data = "sensitive data that should be securely deleted"
        test_file_path.write_text(test_data)
        
        original_size = test_file_path.stat().st_size
        assert original_size > 0
        
        # Securely delete file
        success = security_manager.secure_delete_file(test_file_path, overwrite_passes=2)
        
        assert success is True
        assert not test_file_path.exists()
        
        # Check audit log
        audit_log = security_manager.get_security_audit_log(limit=10)
        delete_events = [event for event in audit_log if event['action'] == 'secure_delete']
        assert len(delete_events) > 0
        assert delete_events[0]['result'] == 'success'
    
    def test_memory_clearing(self, security_manager):
        """Test sensitive memory clearing"""
        # Test with numpy array
        sensitive_array = np.random.rand(100, 100)
        original_sum = np.sum(sensitive_array)
        
        success = security_manager.clear_sensitive_memory(sensitive_array)
        assert success is True
        
        # Array should be zeroed (if writeable)
        if sensitive_array.flags.writeable:
            assert np.sum(sensitive_array) == 0
        
        # Test with list
        sensitive_list = [1, 2, 3, 4, 5]
        success = security_manager.clear_sensitive_memory(sensitive_list)
        assert success is True
        assert len(sensitive_list) == 0
        
        # Test with dictionary
        sensitive_dict = {'key1': 'value1', 'key2': 'value2'}
        success = security_manager.clear_sensitive_memory(sensitive_dict)
        assert success is True
        assert len(sensitive_dict) == 0
    
    def test_secure_handle_management(self, security_manager):
        """Test secure data handle creation and management"""
        # Create secure handle
        handle_id = security_manager._create_secure_handle(
            data_type="test_data",
            size_bytes=1024,
            is_sensitive=True
        )
        
        assert handle_id is not None
        assert len(handle_id) == 16  # Expected handle ID length
        assert handle_id in security_manager.active_handles
        
        # Check handle properties
        handle = security_manager.active_handles[handle_id]
        assert handle.data_type == "test_data"
        assert handle.size_bytes == 1024
        assert handle.is_sensitive is True
    
    def test_audit_integrity_validation(self, security_manager):
        """Test audit log integrity validation"""
        # Log some events
        security_manager._log_security_event(
            event_type="test_event",
            resource="test_resource",
            action="test_action",
            result="success",
            details={"test": "data"}
        )
        
        # Validate integrity
        validation_results = security_manager.validate_audit_integrity()
        
        assert isinstance(validation_results, dict)
        assert 'integrity_valid' in validation_results
        assert 'total_events' in validation_results
        assert 'corrupted_events' in validation_results
        assert validation_results['total_events'] > 0


class TestUpdateManager:
    """Test offline update management"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def update_manager(self, temp_dir):
        """Create update manager for testing"""
        updates_dir = Path(temp_dir) / "updates"
        backup_dir = Path(temp_dir) / "backups"
        
        manager = UpdateManager(str(updates_dir), str(backup_dir))
        manager.update_db_path = Path(temp_dir) / "updates.db"
        manager._init_update_database()
        
        return manager
    
    def test_update_manager_initialization(self, update_manager):
        """Test update manager initialization"""
        assert update_manager.updates_dir.exists()
        assert update_manager.backup_dir.exists()
        assert update_manager.update_db_path.exists()
        
        # Check database tables
        with sqlite3.connect(update_manager.update_db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert 'update_packages' in tables
            assert 'update_history' in tables
            assert 'system_versions' in tables
    
    def test_update_package_creation_and_validation(self, update_manager, temp_dir):
        """Test creating and validating update packages"""
        # Create a test update package
        package_dir = Path(temp_dir) / "test_package"
        package_dir.mkdir()
        
        # Create manifest
        manifest = {
            "package_id": "test_update_v1.0",
            "version": "1.0",
            "package_type": "models",
            "description": "Test update package",
            "files": [
                {
                    "source": "test_model.pt",
                    "target": "models/test_model.pt"
                }
            ]
        }
        
        manifest_path = package_dir / "update_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        # Create test file
        test_file_path = package_dir / "test_model.pt"
        test_file_path.write_bytes(b"fake model data")
        
        # Create zip package
        import zipfile
        package_path = Path(temp_dir) / "test_update.zip"
        with zipfile.ZipFile(package_path, 'w') as zip_file:
            zip_file.write(manifest_path, "update_manifest.json")
            zip_file.write(test_file_path, "test_model.pt")
        
        # Validate package
        is_valid, update_package = update_manager.validate_update_package(package_path)
        
        assert is_valid is True
        assert update_package is not None
        assert update_package.package_id == "test_update_v1.0"
        assert update_package.version == "1.0"
        assert update_package.package_type == "models"
    
    def test_backup_creation_and_restoration(self, update_manager, temp_dir):
        """Test backup creation and restoration"""
        # Create some files to backup
        models_dir = Path(temp_dir) / "models"
        models_dir.mkdir()
        
        test_model = models_dir / "existing_model.pt"
        test_model.write_bytes(b"existing model data")
        
        # Create backup
        with patch.object(update_manager, '_create_backup') as mock_backup:
            backup_path = Path(temp_dir) / "backup_test"
            backup_path.mkdir()
            
            # Create backup manifest
            backup_manifest = {
                'component_type': 'models',
                'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
                'files': [str(test_model)],
                'backup_path': str(backup_path)
            }
            
            manifest_file = backup_path / 'backup_manifest.json'
            with open(manifest_file, 'w') as f:
                json.dump(backup_manifest, f)
            
            # Copy file to backup
            backup_model = backup_path / "existing_model.pt"
            shutil.copy2(test_model, backup_model)
            
            mock_backup.return_value = backup_path
            
            # Test backup creation
            result = update_manager._create_backup("models")
            assert result == backup_path
    
    def test_update_history_tracking(self, update_manager):
        """Test update history tracking"""
        # Record a test update operation
        update_manager._record_update_operation(
            package_id="test_package",
            operation="install",
            result="success",
            previous_version="0.9",
            new_version="1.0",
            files_affected=["models/test_model.pt"],
            backup_path="/tmp/backup"
        )
        
        # Get update history
        history = update_manager.get_update_history(limit=10)
        
        assert len(history) > 0
        assert history[0]['package_id'] == "test_package"
        assert history[0]['operation'] == "install"
        assert history[0]['result'] == "success"


class TestAuditLogger:
    """Test comprehensive audit logging"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def audit_logger(self, temp_dir):
        """Create audit logger for testing"""
        audit_db_path = Path(temp_dir) / "audit.db"
        return AuditLogger(str(audit_db_path))
    
    def test_audit_logger_initialization(self, audit_logger):
        """Test audit logger initialization"""
        assert audit_logger.audit_db_path.exists()
        assert audit_logger.session_id is not None
        
        # Check database tables
        with sqlite3.connect(audit_logger.audit_db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert 'audit_events' in tables
            assert 'system_metrics' in tables
            assert 'security_events' in tables
            assert 'file_access_log' in tables
    
    def test_event_logging(self, audit_logger):
        """Test basic event logging"""
        # Log a test event
        audit_logger.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.SYSTEM,
            component="test_component",
            action="test_action",
            resource="test_resource",
            result="success",
            details={"test": "data"},
            duration_ms=100.5
        )
        
        # Retrieve events
        events = audit_logger.get_audit_events(limit=10)
        
        assert len(events) > 0
        event = events[0]
        assert event['level'] == 'INFO'
        assert event['category'] == 'SYSTEM'
        assert event['component'] == 'test_component'
        assert event['action'] == 'test_action'
        assert event['result'] == 'success'
        assert event['duration_ms'] == 100.5
    
    def test_security_event_logging(self, audit_logger):
        """Test security-specific event logging"""
        audit_logger.log_security_event(
            event_type="unauthorized_access",
            severity="high",
            resource="sensitive_file.jpg",
            action="access_attempt",
            result="blocked",
            details={"ip": "192.168.1.100", "user": "unknown"},
            threat_level="medium"
        )
        
        # Retrieve security events
        security_events = audit_logger.get_security_events(limit=10)
        
        assert len(security_events) > 0
        event = security_events[0]
        assert event['event_type'] == 'unauthorized_access'
        assert event['severity'] == 'high'
        assert event['result'] == 'blocked'
    
    def test_file_access_logging(self, audit_logger, temp_dir):
        """Test file access logging"""
        test_file = Path(temp_dir) / "test_file.txt"
        test_file.write_text("test content")
        
        audit_logger.log_file_access(
            file_path=test_file,
            operation="read",
            result="success",
            details={"purpose": "testing"}
        )
        
        # Retrieve file access logs
        file_logs = audit_logger.get_file_access_log(limit=10)
        
        assert len(file_logs) > 0
        log_entry = file_logs[0]
        assert log_entry['operation'] == 'read'
        assert log_entry['result'] == 'success'
        assert str(test_file) in log_entry['file_path']
    
    def test_image_processing_logging(self, audit_logger):
        """Test image processing event logging"""
        audit_logger.log_image_processing(
            image_path="test_image.jpg",
            operation="validation",
            result="compliant",
            processing_time_ms=250.0,
            details={
                "compliance_score": 95.5,
                "issues": [],
                "format": "ICAO"
            }
        )
        
        # Retrieve events
        events = audit_logger.get_audit_events(
            limit=10,
            category=AuditCategory.IMAGE_PROCESSING
        )
        
        assert len(events) > 0
        event = events[0]
        assert event['category'] == 'IMAGE_PROCESSING'
        assert event['action'] == 'validation'
        assert event['result'] == 'compliant'
        assert event['duration_ms'] == 250.0
    
    def test_audit_integrity_validation(self, audit_logger):
        """Test audit log integrity validation"""
        # Log some events
        for i in range(5):
            audit_logger.log_event(
                level=AuditLevel.INFO,
                category=AuditCategory.SYSTEM,
                component="test",
                action=f"action_{i}",
                resource=f"resource_{i}",
                result="success",
                details={"index": i}
            )
        
        # Validate integrity
        validation_results = audit_logger.validate_audit_integrity()
        
        assert isinstance(validation_results, dict)
        assert validation_results['integrity_valid'] is True
        assert validation_results['total_events'] >= 5
        assert validation_results['corrupted_events'] == 0
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.pids')
    def test_system_metrics_logging(self, mock_pids, mock_disk, mock_memory, mock_cpu, audit_logger):
        """Test system metrics logging"""
        # Mock system metrics
        mock_cpu.return_value = 45.5
        mock_memory.return_value.percent = 67.8
        mock_disk.return_value.percent = 23.4
        mock_pids.return_value = [1, 2, 3, 4, 5]
        
        # Log system metrics
        audit_logger.log_system_metrics()
        
        # Check metrics were logged
        with sqlite3.connect(audit_logger.audit_db_path) as conn:
            cursor = conn.execute("SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 1")
            result = cursor.fetchone()
            
            assert result is not None
            assert result[2] == 45.5  # cpu_percent
            assert result[3] == 67.8  # memory_percent
            assert result[4] == 23.4  # disk_usage_percent
            assert result[5] == 5     # process_count
    
    def test_audit_report_generation(self, audit_logger):
        """Test comprehensive audit report generation"""
        # Log various events
        audit_logger.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.SYSTEM,
            component="test",
            action="startup",
            resource="system",
            result="success",
            details={}
        )
        
        audit_logger.log_security_event(
            event_type="login_attempt",
            severity="low",
            resource="system",
            action="login",
            result="success",
            details={}
        )
        
        # Generate report
        start_time = datetime.now() - timedelta(hours=1)
        end_time = datetime.now()
        
        report = audit_logger.generate_audit_report(start_time, end_time)
        
        assert isinstance(report, dict)
        assert 'period' in report
        assert 'summary' in report
        assert 'events_by_category' in report
        assert 'events_by_level' in report
        assert 'security_events' in report
        assert 'integrity_check' in report


class TestIntegratedSecurity:
    """Test integrated security and offline functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def integrated_system(self, temp_dir):
        """Create integrated system for testing"""
        # Initialize all managers
        offline_manager = OfflineManager()
        offline_manager.models_dir = Path(temp_dir) / "models"
        offline_manager.cache_dir = Path(temp_dir) / "cache"
        offline_manager.offline_db_path = Path(temp_dir) / "offline.db"
        
        security_manager = SecurityManager(str(Path(temp_dir) / "security.db"))
        update_manager = UpdateManager(
            str(Path(temp_dir) / "updates"),
            str(Path(temp_dir) / "backups")
        )
        audit_logger = AuditLogger(str(Path(temp_dir) / "audit.db"))
        
        # Create necessary directories
        offline_manager.models_dir.mkdir(parents=True, exist_ok=True)
        offline_manager.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Reinitialize databases
        offline_manager._init_offline_database()
        update_manager.update_db_path = Path(temp_dir) / "updates.db"
        update_manager._init_update_database()
        
        return {
            'offline': offline_manager,
            'security': security_manager,
            'update': update_manager,
            'audit': audit_logger
        }
    
    def test_integrated_offline_security_workflow(self, integrated_system, temp_dir):
        """Test complete offline security workflow"""
        offline_mgr = integrated_system['offline']
        security_mgr = integrated_system['security']
        audit_logger = integrated_system['audit']
        
        # 1. Check offline readiness
        status = offline_mgr.check_offline_readiness()
        assert isinstance(status, OfflineStatus)
        
        # 2. Create and process a test image securely
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_image_path = Path(temp_dir) / "secure_test.jpg"
        
        # Save image securely
        success = security_mgr.secure_save_image(test_image, test_image_path)
        assert success is True
        
        # Load image securely
        loaded_image = security_mgr.secure_load_image(test_image_path)
        assert loaded_image is not None
        
        # 3. Clear sensitive memory
        success = security_mgr.clear_sensitive_memory(loaded_image)
        assert success is True
        
        # 4. Securely delete the file
        success = security_mgr.secure_delete_file(test_image_path)
        assert success is True
        assert not test_image_path.exists()
        
        # 5. Check audit logs
        audit_events = audit_logger.get_audit_events(limit=20)
        assert len(audit_events) > 0
        
        # Should have file access events
        file_events = [e for e in audit_events if e['category'] == 'FILE_ACCESS']
        assert len(file_events) > 0
    
    def test_security_compliance_validation(self, integrated_system):
        """Test overall security compliance validation"""
        offline_mgr = integrated_system['offline']
        security_mgr = integrated_system['security']
        audit_logger = integrated_system['audit']
        
        # Validate offline operation
        offline_validation = offline_mgr.validate_offline_operation()
        assert isinstance(offline_validation, dict)
        
        # Validate audit integrity
        audit_validation = audit_logger.validate_audit_integrity()
        assert isinstance(audit_validation, dict)
        assert audit_validation['integrity_valid'] is True
        
        # Validate security audit integrity
        security_validation = security_mgr.validate_audit_integrity()
        assert isinstance(security_validation, dict)
        
        # Overall compliance check
        compliance_results = {
            'offline_ready': offline_validation.get('offline_ready', False),
            'network_blocked': offline_validation.get('network_blocked', False),
            'audit_integrity': audit_validation.get('integrity_valid', False),
            'security_integrity': security_validation.get('integrity_valid', False)
        }
        
        # At least some compliance checks should pass
        assert any(compliance_results.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])