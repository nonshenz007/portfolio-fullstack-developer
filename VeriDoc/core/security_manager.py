"""
Security Manager for Veridoc Universal
Handles secure data operations, memory clearing, and audit logging
"""

import os
import gc
import mmap
import ctypes
import hashlib
import logging
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import numpy as np
import cv2

@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    resource: str
    action: str
    result: str
    details: Dict[str, Any]

@dataclass
class SecureDataHandle:
    """Handle for securely managed data"""
    handle_id: str
    data_type: str
    size_bytes: int
    created_at: datetime
    last_accessed: datetime
    is_sensitive: bool

class SecurityManager:
    """
    Manages security operations including secure deletion, memory clearing,
    and comprehensive audit logging
    """
    
    def __init__(self, audit_db_path: str = "logs/security_audit.db"):
        self.logger = logging.getLogger(__name__)
        self.audit_db_path = Path(audit_db_path)
        self.audit_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.active_handles: Dict[str, SecureDataHandle] = {}
        
        # Initialize security audit database
        self._init_security_database()
        
        # Log security manager initialization
        self._log_security_event(
            event_type="system_init",
            resource="security_manager",
            action="initialize",
            result="success",
            details={"audit_db": str(self.audit_db_path)}
        )
    
    def _init_security_database(self):
        """Initialize SQLite database for security audit logging"""
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        user_id TEXT,
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        result TEXT NOT NULL,
                        details TEXT NOT NULL,
                        checksum TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS data_handles (
                        handle_id TEXT PRIMARY KEY,
                        data_type TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        last_accessed TEXT NOT NULL,
                        is_sensitive BOOLEAN NOT NULL,
                        status TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS file_operations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        file_hash TEXT,
                        size_bytes INTEGER,
                        result TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                self.logger.info("Security audit database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize security database: {e}")
            raise
    
    def _log_security_event(self, event_type: str, resource: str, action: str, 
                           result: str, details: Dict[str, Any], user_id: Optional[str] = None):
        """Log security event to audit database"""
        try:
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type=event_type,
                user_id=user_id,
                resource=resource,
                action=action,
                result=result,
                details=details
            )
            
            # Create checksum for integrity
            event_data = f"{event.timestamp.isoformat()}{event_type}{resource}{action}{result}"
            checksum = hashlib.sha256(event_data.encode()).hexdigest()
            
            with sqlite3.connect(self.audit_db_path) as conn:
                conn.execute("""
                    INSERT INTO security_events 
                    (timestamp, event_type, user_id, resource, action, result, details, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.timestamp.isoformat(),
                    event.event_type,
                    event.user_id,
                    event.resource,
                    event.action,
                    event.result,
                    str(details),
                    checksum
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
    
    def secure_load_image(self, file_path: Union[str, Path]) -> Optional[np.ndarray]:
        """Securely load image with audit logging"""
        file_path = Path(file_path)
        
        try:
            # Log file access attempt
            self._log_security_event(
                event_type="file_access",
                resource=str(file_path),
                action="load_image",
                result="attempt",
                details={"file_exists": file_path.exists()}
            )
            
            if not file_path.exists():
                self._log_security_event(
                    event_type="file_access",
                    resource=str(file_path),
                    action="load_image",
                    result="failure",
                    details={"error": "file_not_found"}
                )
                return None
            
            # Calculate file hash for integrity
            file_hash = self._calculate_file_hash(file_path)
            file_size = file_path.stat().st_size
            
            # Load image securely
            image = cv2.imread(str(file_path))
            
            if image is not None:
                # Create secure handle for the image data
                handle_id = self._create_secure_handle(
                    data_type="image",
                    size_bytes=image.nbytes,
                    is_sensitive=True
                )
                
                # Log successful load
                self._log_security_event(
                    event_type="file_access",
                    resource=str(file_path),
                    action="load_image",
                    result="success",
                    details={
                        "file_hash": file_hash,
                        "file_size": file_size,
                        "image_shape": image.shape,
                        "handle_id": handle_id
                    }
                )
                
                # Log file operation
                self._log_file_operation(file_path, "read", file_hash, file_size, "success")
                
                return image
            else:
                self._log_security_event(
                    event_type="file_access",
                    resource=str(file_path),
                    action="load_image",
                    result="failure",
                    details={"error": "invalid_image_format"}
                )
                return None
                
        except Exception as e:
            self._log_security_event(
                event_type="file_access",
                resource=str(file_path),
                action="load_image",
                result="error",
                details={"error": str(e)}
            )
            self.logger.error(f"Failed to securely load image {file_path}: {e}")
            return None
    
    def secure_save_image(self, image: np.ndarray, file_path: Union[str, Path], 
                         overwrite_existing: bool = False) -> bool:
        """Securely save image with audit logging"""
        file_path = Path(file_path)
        
        try:
            # Check if file exists and handle overwrite
            if file_path.exists() and not overwrite_existing:
                self._log_security_event(
                    event_type="file_access",
                    resource=str(file_path),
                    action="save_image",
                    result="blocked",
                    details={"reason": "file_exists_no_overwrite"}
                )
                return False
            
            # Create secure handle for the image data
            handle_id = self._create_secure_handle(
                data_type="image",
                size_bytes=image.nbytes,
                is_sensitive=True
            )
            
            # Save image
            success = cv2.imwrite(str(file_path), image)
            
            if success:
                # Calculate hash of saved file
                file_hash = self._calculate_file_hash(file_path)
                file_size = file_path.stat().st_size
                
                self._log_security_event(
                    event_type="file_access",
                    resource=str(file_path),
                    action="save_image",
                    result="success",
                    details={
                        "file_hash": file_hash,
                        "file_size": file_size,
                        "image_shape": image.shape,
                        "handle_id": handle_id,
                        "overwrite": overwrite_existing
                    }
                )
                
                self._log_file_operation(file_path, "write", file_hash, file_size, "success")
                return True
            else:
                self._log_security_event(
                    event_type="file_access",
                    resource=str(file_path),
                    action="save_image",
                    result="failure",
                    details={"error": "write_failed"}
                )
                return False
                
        except Exception as e:
            self._log_security_event(
                event_type="file_access",
                resource=str(file_path),
                action="save_image",
                result="error",
                details={"error": str(e)}
            )
            self.logger.error(f"Failed to securely save image {file_path}: {e}")
            return False
    
    def secure_delete_file(self, file_path: Union[str, Path], overwrite_passes: int = 3) -> bool:
        """Securely delete file with multiple overwrite passes"""
        file_path = Path(file_path)
        
        try:
            if not file_path.exists():
                self._log_security_event(
                    event_type="file_deletion",
                    resource=str(file_path),
                    action="secure_delete",
                    result="skipped",
                    details={"reason": "file_not_found"}
                )
                return True
            
            # Get file info before deletion
            file_size = file_path.stat().st_size
            original_hash = self._calculate_file_hash(file_path)
            
            # Perform secure overwrite
            with open(file_path, 'r+b') as f:
                for pass_num in range(overwrite_passes):
                    f.seek(0)
                    # Overwrite with random data
                    random_data = os.urandom(file_size)
                    f.write(random_data)
                    f.flush()
                    os.fsync(f.fileno())
                    
                    self._log_security_event(
                        event_type="file_deletion",
                        resource=str(file_path),
                        action="overwrite_pass",
                        result="success",
                        details={"pass_number": pass_num + 1, "bytes_written": file_size}
                    )
            
            # Delete the file
            file_path.unlink()
            
            self._log_security_event(
                event_type="file_deletion",
                resource=str(file_path),
                action="secure_delete",
                result="success",
                details={
                    "original_hash": original_hash,
                    "file_size": file_size,
                    "overwrite_passes": overwrite_passes
                }
            )
            
            self._log_file_operation(file_path, "secure_delete", original_hash, file_size, "success")
            return True
            
        except Exception as e:
            self._log_security_event(
                event_type="file_deletion",
                resource=str(file_path),
                action="secure_delete",
                result="error",
                details={"error": str(e)}
            )
            self.logger.error(f"Failed to securely delete file {file_path}: {e}")
            return False
    
    def clear_sensitive_memory(self, data: Union[np.ndarray, List, Dict, Any]) -> bool:
        """Clear sensitive data from memory"""
        try:
            cleared_items = 0
            
            if isinstance(data, np.ndarray):
                # Zero out numpy array
                if data.flags.writeable:
                    data.fill(0)
                    cleared_items = data.size
                else:
                    # Create a copy and clear it
                    temp = data.copy()
                    temp.fill(0)
                    del temp
                    cleared_items = data.size
            
            elif isinstance(data, list):
                # Clear list contents
                for i in range(len(data)):
                    if hasattr(data[i], 'fill'):
                        data[i].fill(0)
                    data[i] = None
                data.clear()
                cleared_items = len(data)
            
            elif isinstance(data, dict):
                # Clear dictionary contents
                for key in list(data.keys()):
                    if hasattr(data[key], 'fill'):
                        data[key].fill(0)
                    data[key] = None
                data.clear()
                cleared_items = len(data)
            
            # Force garbage collection
            gc.collect()
            
            self._log_security_event(
                event_type="memory_management",
                resource="sensitive_data",
                action="clear_memory",
                result="success",
                details={
                    "data_type": type(data).__name__,
                    "cleared_items": cleared_items
                }
            )
            
            return True
            
        except Exception as e:
            self._log_security_event(
                event_type="memory_management",
                resource="sensitive_data",
                action="clear_memory",
                result="error",
                details={"error": str(e)}
            )
            self.logger.error(f"Failed to clear sensitive memory: {e}")
            return False
    
    def _create_secure_handle(self, data_type: str, size_bytes: int, is_sensitive: bool) -> str:
        """Create a secure handle for tracking data"""
        handle_id = hashlib.sha256(f"{datetime.now().isoformat()}{data_type}{size_bytes}".encode()).hexdigest()[:16]
        
        handle = SecureDataHandle(
            handle_id=handle_id,
            data_type=data_type,
            size_bytes=size_bytes,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            is_sensitive=is_sensitive
        )
        
        with self.lock:
            self.active_handles[handle_id] = handle
        
        # Store in database
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                conn.execute("""
                    INSERT INTO data_handles 
                    (handle_id, data_type, size_bytes, created_at, last_accessed, is_sensitive, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    handle.handle_id,
                    handle.data_type,
                    handle.size_bytes,
                    handle.created_at.isoformat(),
                    handle.last_accessed.isoformat(),
                    handle.is_sensitive,
                    "active"
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to store secure handle: {e}")
        
        return handle_id
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate file hash for {file_path}: {e}")
            return ""
    
    def _log_file_operation(self, file_path: Path, operation: str, file_hash: str, 
                           size_bytes: int, result: str):
        """Log file operation to database"""
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                conn.execute("""
                    INSERT INTO file_operations 
                    (timestamp, file_path, operation, file_hash, size_bytes, result)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    str(file_path),
                    operation,
                    file_hash,
                    size_bytes,
                    result
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to log file operation: {e}")
    
    def get_security_audit_log(self, limit: int = 100, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get security audit log entries"""
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                if event_type:
                    cursor = conn.execute(
                        "SELECT * FROM security_events WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?",
                        (event_type, limit)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM security_events ORDER BY timestamp DESC LIMIT ?",
                        (limit,)
                    )
                
                results = cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'timestamp': row[1],
                        'event_type': row[2],
                        'user_id': row[3],
                        'resource': row[4],
                        'action': row[5],
                        'result': row[6],
                        'details': row[7],
                        'checksum': row[8]
                    }
                    for row in results
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get security audit log: {e}")
            return []
    
    def validate_audit_integrity(self) -> Dict[str, Any]:
        """Validate integrity of audit log"""
        validation_results = {
            'integrity_valid': True,
            'total_events': 0,
            'corrupted_events': 0,
            'issues': []
        }
        
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.execute("SELECT * FROM security_events")
                events = cursor.fetchall()
                
                validation_results['total_events'] = len(events)
                
                for event in events:
                    # Verify checksum
                    event_data = f"{event[1]}{event[2]}{event[4]}{event[5]}{event[6]}"
                    expected_checksum = hashlib.sha256(event_data.encode()).hexdigest()
                    
                    if event[8] != expected_checksum:
                        validation_results['corrupted_events'] += 1
                        validation_results['integrity_valid'] = False
                        validation_results['issues'].append(f"Event ID {event[0]} has invalid checksum")
                
        except Exception as e:
            validation_results['integrity_valid'] = False
            validation_results['issues'].append(f"Validation error: {e}")
            self.logger.error(f"Failed to validate audit integrity: {e}")
        
        return validation_results
    
    def cleanup_expired_handles(self, max_age_hours: int = 24):
        """Clean up expired secure handles"""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            expired_handles = []
            
            with self.lock:
                for handle_id, handle in list(self.active_handles.items()):
                    if handle.created_at.timestamp() < cutoff_time:
                        expired_handles.append(handle_id)
                        del self.active_handles[handle_id]
            
            # Update database
            with sqlite3.connect(self.audit_db_path) as conn:
                for handle_id in expired_handles:
                    conn.execute(
                        "UPDATE data_handles SET status = 'expired' WHERE handle_id = ?",
                        (handle_id,)
                    )
                conn.commit()
            
            self._log_security_event(
                event_type="maintenance",
                resource="secure_handles",
                action="cleanup_expired",
                result="success",
                details={"expired_count": len(expired_handles)}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired handles: {e}")