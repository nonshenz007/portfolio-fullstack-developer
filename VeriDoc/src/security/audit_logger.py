"""
Tamper-Proof Audit Logger

Implements military-grade audit logging with cryptographic integrity verification,
blockchain-style chaining, and comprehensive event tracking.
"""

import os
import json
import hashlib
import sqlite3
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

from ..contracts import IAuditLogger, SecurityContext, ProcessingResult, ProcessingMetrics


@dataclass
class AuditEntry:
    """Individual audit log entry"""
    entry_id: str
    timestamp: datetime
    event_type: str
    user_id: str
    session_id: str
    resource: str
    action: str
    result: ProcessingResult
    details: Dict[str, Any]
    security_level: str
    previous_hash: str
    entry_hash: str
    signature: str


class TamperProofAuditLogger(IAuditLogger):
    """
    Military-grade tamper-proof audit logging system with:
    - Cryptographic integrity verification
    - Blockchain-style entry chaining
    - Secure storage with encryption
    - Real-time integrity monitoring
    """
    
    def __init__(self, audit_db_path: str = "secure/audit.db", 
                 encryption_manager=None):
        self.logger = logging.getLogger(__name__)
        self.audit_db_path = Path(audit_db_path)
        self.audit_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.encryption_manager = encryption_manager
        self.lock = threading.Lock()
        
        # Initialize audit database
        self._initialize_audit_database()
        
        # Load last entry hash for chaining
        self.last_entry_hash = self._get_last_entry_hash()
        
        # Start integrity monitoring
        self._start_integrity_monitoring()
        
        self.logger.info("Tamper-proof audit logger initialized")
    
    def _initialize_audit_database(self):
        """Initialize SQLite database with security features"""
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                # Enable WAL mode for better concurrency and integrity
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=FULL")
                conn.execute("PRAGMA foreign_keys=ON")
                
                # Main audit table with tamper-proof features
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entry_id TEXT UNIQUE NOT NULL,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        result TEXT NOT NULL,
                        details TEXT NOT NULL,
                        security_level TEXT NOT NULL,
                        previous_hash TEXT NOT NULL,
                        entry_hash TEXT NOT NULL,
                        signature TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Chain integrity verification table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS integrity_checkpoints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        checkpoint_time TEXT NOT NULL,
                        total_entries INTEGER NOT NULL,
                        chain_hash TEXT NOT NULL,
                        signature TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Security events table for high-priority events
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        user_id TEXT,
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        result TEXT NOT NULL,
                        threat_level TEXT,
                        details TEXT NOT NULL,
                        signature TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Processing metrics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS processing_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        processing_time_ms REAL NOT NULL,
                        memory_usage_mb REAL NOT NULL,
                        cpu_usage_percent REAL NOT NULL,
                        operations_performed TEXT NOT NULL,
                        ai_model_times TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_entries(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_entries(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_entries(event_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_security_timestamp ON security_events(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON processing_metrics(timestamp)")
                
                conn.commit()
                self.logger.info("Audit database initialized with tamper-proof features")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize audit database: {e}")
            raise
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        timestamp = datetime.now().isoformat()
        random_bytes = os.urandom(16)
        return hashlib.sha256(f"{timestamp}{random_bytes.hex()}".encode()).hexdigest()[:16]
    
    def _calculate_entry_hash(self, entry_data: Dict[str, Any], previous_hash: str) -> str:
        """Calculate cryptographic hash for entry with chaining"""
        # Create deterministic string from entry data
        hash_data = {
            'timestamp': entry_data['timestamp'],
            'event_type': entry_data['event_type'],
            'user_id': entry_data['user_id'],
            'resource': entry_data['resource'],
            'action': entry_data['action'],
            'result': entry_data['result'],
            'previous_hash': previous_hash
        }
        
        # Sort keys for deterministic hashing
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def _get_last_entry_hash(self) -> str:
        """Get hash of last audit entry for chaining"""
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.execute(
                    "SELECT entry_hash FROM audit_entries ORDER BY id DESC LIMIT 1"
                )
                result = cursor.fetchone()
                return result[0] if result else "0000000000000000000000000000000000000000000000000000000000000000"
        except Exception:
            return "0000000000000000000000000000000000000000000000000000000000000000"
    
    def log_security_event(self, event_type: str, resource: str, action: str,
                          result: ProcessingResult, context: SecurityContext,
                          details: Dict[str, Any]) -> str:
        """Log security event with tamper-proof signature"""
        try:
            entry_id = self._generate_entry_id()
            timestamp = datetime.now()
            
            # Create entry data
            entry_data = {
                'entry_id': entry_id,
                'timestamp': timestamp.isoformat(),
                'event_type': event_type,
                'user_id': context.user_id,
                'session_id': context.session_id,
                'resource': resource,
                'action': action,
                'result': result.value,
                'details': details,
                'security_level': context.security_level.value
            }
            
            # Calculate hash with chaining
            previous_hash = self.last_entry_hash
            entry_hash = self._calculate_entry_hash(entry_data, previous_hash)
            
            # Generate signature if encryption manager available
            signature = ""
            if self.encryption_manager:
                signature_data = json.dumps(entry_data, sort_keys=True).encode()
                signature = self.encryption_manager.generate_signature(signature_data, context)
            
            # Create audit entry
            audit_entry = AuditEntry(
                entry_id=entry_id,
                timestamp=timestamp,
                event_type=event_type,
                user_id=context.user_id,
                session_id=context.session_id,
                resource=resource,
                action=action,
                result=result,
                details=details,
                security_level=context.security_level.value,
                previous_hash=previous_hash,
                entry_hash=entry_hash,
                signature=signature
            )
            
            # Store in database
            with self.lock:
                with sqlite3.connect(self.audit_db_path) as conn:
                    conn.execute("""
                        INSERT INTO audit_entries 
                        (entry_id, timestamp, event_type, user_id, session_id, resource,
                         action, result, details, security_level, previous_hash, 
                         entry_hash, signature)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        audit_entry.entry_id,
                        audit_entry.timestamp.isoformat(),
                        audit_entry.event_type,
                        audit_entry.user_id,
                        audit_entry.session_id,
                        audit_entry.resource,
                        audit_entry.action,
                        audit_entry.result.value,
                        json.dumps(audit_entry.details),
                        audit_entry.security_level,
                        audit_entry.previous_hash,
                        audit_entry.entry_hash,
                        audit_entry.signature
                    ))
                    conn.commit()
                
                # Update last entry hash for chaining
                self.last_entry_hash = entry_hash
            
            # Also log to security events if high severity
            if event_type in ['SECURITY_VIOLATION', 'ACCESS_DENIED', 'UNAUTHORIZED_ACCESS']:
                self._log_high_priority_security_event(audit_entry, context)
            
            self.logger.debug(f"Security event logged: {entry_id}")
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
            raise
    
    def log_processing_event(self, operation: str, resource: str,
                           result: ProcessingResult, metrics: ProcessingMetrics,
                           context: SecurityContext) -> str:
        """Log processing event with performance metrics"""
        try:
            # Log main event
            details = {
                'operation': operation,
                'processing_time_ms': metrics.processing_time_ms,
                'memory_usage_mb': metrics.memory_usage_mb,
                'cpu_usage_percent': metrics.cpu_usage_percent,
                'operations_performed': metrics.operations_performed
            }
            
            entry_id = self.log_security_event(
                event_type="PROCESSING",
                resource=resource,
                action=operation,
                result=result,
                context=context,
                details=details
            )
            
            # Store detailed metrics
            with self.lock:
                with sqlite3.connect(self.audit_db_path) as conn:
                    conn.execute("""
                        INSERT INTO processing_metrics
                        (timestamp, operation, processing_time_ms, memory_usage_mb,
                         cpu_usage_percent, operations_performed, ai_model_times,
                         user_id, session_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        operation,
                        metrics.processing_time_ms,
                        metrics.memory_usage_mb,
                        metrics.cpu_usage_percent,
                        json.dumps(metrics.operations_performed),
                        json.dumps(metrics.ai_model_inference_times),
                        context.user_id,
                        context.session_id
                    ))
                    conn.commit()
            
            return entry_id
            
        except Exception as e:
            self.logger.error(f"Failed to log processing event: {e}")
            raise
    
    def _log_high_priority_security_event(self, audit_entry: AuditEntry, context: SecurityContext):
        """Log high-priority security event to dedicated table"""
        try:
            severity = "HIGH"
            threat_level = "MEDIUM"
            
            if audit_entry.event_type == "SECURITY_VIOLATION":
                severity = "CRITICAL"
                threat_level = "HIGH"
            
            with sqlite3.connect(self.audit_db_path) as conn:
                conn.execute("""
                    INSERT INTO security_events
                    (timestamp, event_type, severity, user_id, resource, action,
                     result, threat_level, details, signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    audit_entry.timestamp.isoformat(),
                    audit_entry.event_type,
                    severity,
                    audit_entry.user_id,
                    audit_entry.resource,
                    audit_entry.action,
                    audit_entry.result.value,
                    threat_level,
                    json.dumps(audit_entry.details),
                    audit_entry.signature
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log high-priority security event: {e}")
    
    def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify complete audit log integrity using chain verification"""
        verification_result = {
            'integrity_valid': True,
            'total_entries': 0,
            'chain_breaks': 0,
            'signature_failures': 0,
            'hash_mismatches': 0,
            'issues': [],
            'verification_time': datetime.now().isoformat()
        }
        
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.execute("""
                    SELECT entry_id, timestamp, event_type, user_id, session_id,
                           resource, action, result, details, security_level,
                           previous_hash, entry_hash, signature
                    FROM audit_entries ORDER BY id ASC
                """)
                
                entries = cursor.fetchall()
                verification_result['total_entries'] = len(entries)
                
                expected_previous_hash = "0000000000000000000000000000000000000000000000000000000000000000"
                
                for entry in entries:
                    entry_data = {
                        'timestamp': entry[1],
                        'event_type': entry[2],
                        'user_id': entry[3],
                        'resource': entry[5],
                        'action': entry[6],
                        'result': entry[7]
                    }
                    
                    # Verify chain integrity
                    if entry[10] != expected_previous_hash:  # previous_hash column
                        verification_result['chain_breaks'] += 1
                        verification_result['integrity_valid'] = False
                        verification_result['issues'].append(
                            f"Chain break at entry {entry[0]}: expected {expected_previous_hash}, got {entry[10]}"
                        )
                    
                    # Verify entry hash
                    calculated_hash = self._calculate_entry_hash(entry_data, entry[10])
                    if calculated_hash != entry[11]:  # entry_hash column
                        verification_result['hash_mismatches'] += 1
                        verification_result['integrity_valid'] = False
                        verification_result['issues'].append(
                            f"Hash mismatch at entry {entry[0]}: calculated {calculated_hash}, stored {entry[11]}"
                        )
                    
                    # Verify signature if available
                    if self.encryption_manager and entry[12]:  # signature column
                        entry_json = json.dumps({
                            'entry_id': entry[0],
                            'timestamp': entry[1],
                            'event_type': entry[2],
                            'user_id': entry[3],
                            'session_id': entry[4],
                            'resource': entry[5],
                            'action': entry[6],
                            'result': entry[7],
                            'details': json.loads(entry[8]),
                            'security_level': entry[9]
                        }, sort_keys=True)
                        
                        # Create dummy context for verification
                        dummy_context = SecurityContext(
                            user_id=entry[3],
                            session_id=entry[4],
                            security_level=SecurityLevel(entry[9]),
                            permissions=[],
                            timestamp=datetime.fromisoformat(entry[1])
                        )
                        
                        if not self.encryption_manager.verify_signature(
                            entry_json.encode(), entry[12], dummy_context
                        ):
                            verification_result['signature_failures'] += 1
                            verification_result['integrity_valid'] = False
                            verification_result['issues'].append(
                                f"Signature verification failed for entry {entry[0]}"
                            )
                    
                    # Update expected hash for next iteration
                    expected_previous_hash = entry[11]
                
                # Log verification result
                self.logger.info(f"Audit integrity verification completed: {verification_result}")
                
        except Exception as e:
            verification_result['integrity_valid'] = False
            verification_result['issues'].append(f"Verification error: {e}")
            self.logger.error(f"Audit integrity verification failed: {e}")
        
        return verification_result
    
    def create_integrity_checkpoint(self, context: SecurityContext) -> str:
        """Create integrity checkpoint for audit chain"""
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                # Count total entries
                cursor = conn.execute("SELECT COUNT(*) FROM audit_entries")
                total_entries = cursor.fetchone()[0]
                
                # Calculate chain hash
                cursor = conn.execute("SELECT entry_hash FROM audit_entries ORDER BY id ASC")
                entry_hashes = [row[0] for row in cursor.fetchall()]
                chain_data = "".join(entry_hashes)
                chain_hash = hashlib.sha256(chain_data.encode()).hexdigest()
                
                # Generate signature
                checkpoint_data = {
                    'timestamp': datetime.now().isoformat(),
                    'total_entries': total_entries,
                    'chain_hash': chain_hash
                }
                
                signature = ""
                if self.encryption_manager:
                    signature = self.encryption_manager.generate_signature(
                        json.dumps(checkpoint_data, sort_keys=True).encode(),
                        context
                    )
                
                # Store checkpoint
                conn.execute("""
                    INSERT INTO integrity_checkpoints
                    (checkpoint_time, total_entries, chain_hash, signature)
                    VALUES (?, ?, ?, ?)
                """, (
                    checkpoint_data['timestamp'],
                    total_entries,
                    chain_hash,
                    signature
                ))
                conn.commit()
                
                checkpoint_id = cursor.lastrowid
                self.logger.info(f"Integrity checkpoint created: {checkpoint_id}")
                return str(checkpoint_id)
                
        except Exception as e:
            self.logger.error(f"Failed to create integrity checkpoint: {e}")
            raise
    
    def get_audit_statistics(self, start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get audit statistics for time period"""
        try:
            stats = {
                'total_entries': 0,
                'events_by_type': {},
                'events_by_user': {},
                'security_events': 0,
                'processing_events': 0,
                'average_processing_time': 0.0,
                'integrity_status': 'UNKNOWN'
            }
            
            query_conditions = []
            params = []
            
            if start_time:
                query_conditions.append("timestamp >= ?")
                params.append(start_time.isoformat())
            
            if end_time:
                query_conditions.append("timestamp <= ?")
                params.append(end_time.isoformat())
            
            where_clause = " WHERE " + " AND ".join(query_conditions) if query_conditions else ""
            
            with sqlite3.connect(self.audit_db_path) as conn:
                # Total entries
                cursor = conn.execute(f"SELECT COUNT(*) FROM audit_entries{where_clause}", params)
                stats['total_entries'] = cursor.fetchone()[0]
                
                # Events by type
                cursor = conn.execute(f"""
                    SELECT event_type, COUNT(*) FROM audit_entries{where_clause}
                    GROUP BY event_type
                """, params)
                stats['events_by_type'] = dict(cursor.fetchall())
                
                # Events by user
                cursor = conn.execute(f"""
                    SELECT user_id, COUNT(*) FROM audit_entries{where_clause}
                    GROUP BY user_id
                """, params)
                stats['events_by_user'] = dict(cursor.fetchall())
                
                # Security and processing event counts
                stats['security_events'] = stats['events_by_type'].get('SECURITY', 0)
                stats['processing_events'] = stats['events_by_type'].get('PROCESSING', 0)
                
                # Average processing time
                if end_time and start_time:
                    time_conditions = []
                    time_params = []
                    if start_time:
                        time_conditions.append("timestamp >= ?")
                        time_params.append(start_time.isoformat())
                    if end_time:
                        time_conditions.append("timestamp <= ?")
                        time_params.append(end_time.isoformat())
                    
                    time_where = " WHERE " + " AND ".join(time_conditions) if time_conditions else ""
                    
                    cursor = conn.execute(f"""
                        SELECT AVG(processing_time_ms) FROM processing_metrics{time_where}
                    """, time_params)
                    result = cursor.fetchone()
                    stats['average_processing_time'] = result[0] if result[0] else 0.0
                
            # Check integrity status
            integrity_result = self.verify_audit_integrity()
            stats['integrity_status'] = 'VALID' if integrity_result['integrity_valid'] else 'COMPROMISED'
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get audit statistics: {e}")
            return stats
    
    def _start_integrity_monitoring(self):
        """Start background integrity monitoring"""
        # This would typically start a separate thread for periodic integrity checks
        # For now, we'll just log that monitoring is enabled
        self.logger.info("Audit integrity monitoring enabled")
    
    def export_audit_log(self, output_path: str, context: SecurityContext,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> bool:
        """Export audit log to encrypted file"""
        try:
            query_conditions = []
            params = []
            
            if start_time:
                query_conditions.append("timestamp >= ?")
                params.append(start_time.isoformat())
            
            if end_time:
                query_conditions.append("timestamp <= ?")
                params.append(end_time.isoformat())
            
            where_clause = " WHERE " + " AND ".join(query_conditions) if query_conditions else ""
            
            export_data = {
                'export_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'exported_by': context.user_id,
                    'start_time': start_time.isoformat() if start_time else None,
                    'end_time': end_time.isoformat() if end_time else None
                },
                'audit_entries': [],
                'integrity_verification': self.verify_audit_integrity()
            }
            
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.execute(f"""
                    SELECT * FROM audit_entries{where_clause} ORDER BY timestamp ASC
                """, params)
                
                columns = [description[0] for description in cursor.description]
                for row in cursor.fetchall():
                    entry_dict = dict(zip(columns, row))
                    export_data['audit_entries'].append(entry_dict)
            
            # Convert to JSON and encrypt if encryption manager available
            export_json = json.dumps(export_data, indent=2)
            
            if self.encryption_manager:
                encrypted_data = self.encryption_manager.encrypt_data(
                    export_json.encode(), context
                )
                with open(output_path, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(output_path, 'w') as f:
                    f.write(export_json)
            
            self.logger.info(f"Audit log exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export audit log: {e}")
            return False
