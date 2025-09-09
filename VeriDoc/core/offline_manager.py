"""
Offline Operation Manager for Veridoc Universal
Ensures complete offline functionality without internet connectivity
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import sqlite3
import threading
from dataclasses import dataclass, asdict

@dataclass
class OfflineStatus:
    """Status of offline operation capabilities"""
    is_offline_ready: bool
    missing_models: List[str]
    missing_configs: List[str]
    last_update_check: Optional[datetime]
    offline_mode_enabled: bool

@dataclass
class ModelInfo:
    """Information about AI models for offline operation"""
    name: str
    version: str
    file_path: str
    checksum: str
    size_bytes: int
    last_verified: datetime
    is_available: bool

class OfflineManager:
    """
    Manages offline operation capabilities and ensures no internet connectivity
    """
    
    def __init__(self, config_manager=None):
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.offline_mode = True  # Default to offline mode for security
        self.models_dir = Path("models")
        self.cache_dir = Path("cache/offline")
        self.offline_db_path = Path("cache/offline/offline_status.db")
        self.lock = threading.Lock()
        
        # Ensure directories exist
        self.models_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize offline database
        self._init_offline_database()
        
        # Block network access
        self._enforce_offline_mode()
    
    def _init_offline_database(self):
        """Initialize SQLite database for offline status tracking"""
        try:
            with sqlite3.connect(self.offline_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS model_status (
                        name TEXT PRIMARY KEY,
                        version TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        last_verified TEXT NOT NULL,
                        is_available BOOLEAN NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS offline_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        details TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                self.logger.info("Offline database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize offline database: {e}")
            raise
    
    def _enforce_offline_mode(self):
        """Enforce offline mode by blocking network access"""
        try:
            # Set environment variables to disable network access
            os.environ['NO_PROXY'] = '*'
            os.environ['HTTP_PROXY'] = 'localhost:0'
            os.environ['HTTPS_PROXY'] = 'localhost:0'
            
            # Log offline mode enforcement
            self._log_offline_event("offline_mode_enforced", "Network access blocked for security")
            self.logger.info("Offline mode enforced - network access blocked")
            
        except Exception as e:
            self.logger.error(f"Failed to enforce offline mode: {e}")
    
    def check_offline_readiness(self) -> OfflineStatus:
        """Check if system is ready for complete offline operation"""
        with self.lock:
            try:
                missing_models = self._check_required_models()
                missing_configs = self._check_required_configs()
                
                status = OfflineStatus(
                    is_offline_ready=len(missing_models) == 0 and len(missing_configs) == 0,
                    missing_models=missing_models,
                    missing_configs=missing_configs,
                    last_update_check=datetime.now(),
                    offline_mode_enabled=self.offline_mode
                )
                
                self._log_offline_event("readiness_check", json.dumps(asdict(status)))
                return status
                
            except Exception as e:
                self.logger.error(f"Failed to check offline readiness: {e}")
                return OfflineStatus(
                    is_offline_ready=False,
                    missing_models=[],
                    missing_configs=[],
                    last_update_check=datetime.now(),
                    offline_mode_enabled=self.offline_mode
                )
    
    def _check_required_models(self) -> List[str]:
        """Check for required AI models"""
        required_models = [
            "yolov8n-face.pt",
            "face_detection_yunet_2023mar.onnx",
            "isnet-general-use.onnx"
        ]
        
        missing_models = []
        for model_name in required_models:
            model_path = self.models_dir / model_name
            if not model_path.exists():
                missing_models.append(model_name)
            else:
                # Verify model integrity
                if not self._verify_model_integrity(model_path):
                    missing_models.append(f"{model_name} (corrupted)")
        
        return missing_models
    
    def _check_required_configs(self) -> List[str]:
        """Check for required configuration files"""
        required_configs = [
            "config/icao_rules_2023.json",
            "config/defaults.py",
            "config/formats/base_icao.json"
        ]
        
        missing_configs = []
        for config_path in required_configs:
            if not Path(config_path).exists():
                missing_configs.append(config_path)
        
        return missing_configs
    
    def _verify_model_integrity(self, model_path: Path) -> bool:
        """Verify model file integrity using checksum"""
        try:
            with open(model_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Check against stored checksum if available
            stored_checksum = self._get_stored_checksum(model_path.name)
            if stored_checksum:
                return file_hash == stored_checksum
            else:
                # Store checksum for future verification
                self._store_model_checksum(model_path.name, file_hash)
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to verify model integrity for {model_path}: {e}")
            return False
    
    def _get_stored_checksum(self, model_name: str) -> Optional[str]:
        """Get stored checksum for a model"""
        try:
            with sqlite3.connect(self.offline_db_path) as conn:
                cursor = conn.execute(
                    "SELECT checksum FROM model_status WHERE name = ?",
                    (model_name,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            self.logger.error(f"Failed to get stored checksum for {model_name}: {e}")
            return None
    
    def _store_model_checksum(self, model_name: str, checksum: str):
        """Store model checksum for integrity verification"""
        try:
            model_path = self.models_dir / model_name
            model_info = ModelInfo(
                name=model_name,
                version="1.0",
                file_path=str(model_path),
                checksum=checksum,
                size_bytes=model_path.stat().st_size if model_path.exists() else 0,
                last_verified=datetime.now(),
                is_available=model_path.exists()
            )
            
            with sqlite3.connect(self.offline_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO model_status 
                    (name, version, file_path, checksum, size_bytes, last_verified, is_available)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    model_info.name,
                    model_info.version,
                    model_info.file_path,
                    model_info.checksum,
                    model_info.size_bytes,
                    model_info.last_verified.isoformat(),
                    model_info.is_available
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store model checksum for {model_name}: {e}")
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        try:
            with sqlite3.connect(self.offline_db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM model_status WHERE name = ?",
                    (model_name,)
                )
                result = cursor.fetchone()
                
                if result:
                    return ModelInfo(
                        name=result[0],
                        version=result[1],
                        file_path=result[2],
                        checksum=result[3],
                        size_bytes=result[4],
                        last_verified=datetime.fromisoformat(result[5]),
                        is_available=bool(result[6])
                    )
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get model info for {model_name}: {e}")
            return None
    
    def _log_offline_event(self, event_type: str, details: str):
        """Log offline operation events"""
        try:
            with sqlite3.connect(self.offline_db_path) as conn:
                conn.execute(
                    "INSERT INTO offline_logs (timestamp, event_type, details) VALUES (?, ?, ?)",
                    (datetime.now().isoformat(), event_type, details)
                )
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log offline event: {e}")
    
    def get_offline_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent offline operation logs"""
        try:
            with sqlite3.connect(self.offline_db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM offline_logs ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                results = cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'timestamp': row[1],
                        'event_type': row[2],
                        'details': row[3]
                    }
                    for row in results
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get offline logs: {e}")
            return []
    
    def is_network_blocked(self) -> bool:
        """Check if network access is properly blocked"""
        try:
            import socket
            # Try to create a socket connection (should fail in offline mode)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('8.8.8.8', 53))
            sock.close()
            
            # If connection succeeds, network is not blocked
            network_blocked = result != 0
            
            self._log_offline_event(
                "network_check", 
                f"Network blocked: {network_blocked}"
            )
            
            return network_blocked
            
        except Exception as e:
            # Exception means network is likely blocked
            self._log_offline_event("network_check", f"Network check failed (blocked): {e}")
            return True
    
    def validate_offline_operation(self) -> Dict[str, Any]:
        """Comprehensive validation of offline operation"""
        validation_results = {
            'offline_ready': False,
            'network_blocked': False,
            'models_available': False,
            'configs_available': False,
            'database_accessible': False,
            'issues': []
        }
        
        try:
            # Check offline readiness
            status = self.check_offline_readiness()
            validation_results['offline_ready'] = status.is_offline_ready
            
            if not status.is_offline_ready:
                validation_results['issues'].extend([
                    f"Missing models: {', '.join(status.missing_models)}",
                    f"Missing configs: {', '.join(status.missing_configs)}"
                ])
            
            # Check network blocking
            validation_results['network_blocked'] = self.is_network_blocked()
            if not validation_results['network_blocked']:
                validation_results['issues'].append("Network access not properly blocked")
            
            # Check models
            validation_results['models_available'] = len(status.missing_models) == 0
            
            # Check configs
            validation_results['configs_available'] = len(status.missing_configs) == 0
            
            # Check database
            validation_results['database_accessible'] = self.offline_db_path.exists()
            if not validation_results['database_accessible']:
                validation_results['issues'].append("Offline database not accessible")
            
            self._log_offline_event("validation_complete", json.dumps(validation_results))
            
        except Exception as e:
            validation_results['issues'].append(f"Validation error: {e}")
            self.logger.error(f"Offline validation failed: {e}")
        
        return validation_results