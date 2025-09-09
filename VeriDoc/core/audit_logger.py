"""
Comprehensive Audit Logger for Veridoc Universal
Provides detailed audit logging for security compliance and offline operation tracking
"""

import os
import json
import logging
import sqlite3
import threading
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import psutil

class AuditLevel(Enum):
    """Audit logging levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"

class AuditCategory(Enum):
    """Audit event categories"""
    SYSTEM = "SYSTEM"
    FILE_ACCESS = "FILE_ACCESS"
    IMAGE_PROCESSING = "IMAGE_PROCESSING"
    VALIDATION = "VALIDATION"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    USER_ACTION = "USER_ACTION"
    NETWORK = "NETWORK"
    UPDATE = "UPDATE"

@dataclass
class AuditEvent:
    """Audit event structure"""
    timestamp: datetime
    level: AuditLevel
    category: AuditCategory
    event_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    component: str
    action: str
    resource: str
    result: str
    details: Dict[str, Any]
    duration_ms: Optional[float]
    system_info: Dict[str, Any]

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    process_count: int
    timestamp: datetime

class AuditLogger:
    """
    Comprehensive audit logging system for security compliance and operational tracking
    """
    
    def __init__(self, audit_db_path: str = "logs/audit_log.db", 
                 max_log_size_mb: int = 100, retention_days: int = 365):
        self.logger = logging.getLogger(__name__)
        self.audit_db_path = Path(audit_db_path)
        self.audit_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_log_size_mb = max_log_size_mb
        self.retention_days = retention_days
        self.lock = threading.Lock()
        self.session_id = self._generate_session_id()
        
        # Initialize audit database
        self._init_audit_database()
        
        # Log audit system initialization
        self._log_system_event(
            level=AuditLevel.INFO,
            category=AuditCategory.SYSTEM,
            action="audit_system_init",
            resource="audit_logger",
            result="success",
            details={"session_id": self.session_id, "retention_days": retention_days}
        )
    
    def _init_audit_database(self):
        """Initialize SQLite database for audit logging"""
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                # Main audit events table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        level TEXT NOT NULL,
                        category TEXT NOT NULL,
                        event_id TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        component TEXT NOT NULL,
                        action TEXT NOT NULL,
                        resource TEXT NOT NULL,
                        result TEXT NOT NULL,
                        details TEXT NOT NULL,
                        duration_ms REAL,
                        system_info TEXT NOT NULL,
                        checksum TEXT NOT NULL
                    )
                """)
                
                # System metrics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        cpu_percent REAL NOT NULL,
                        memory_percent REAL NOT NULL,
                        disk_usage_percent REAL NOT NULL,
                        process_count INTEGER NOT NULL,
                        session_id TEXT NOT NULL
                    )
                """)
                
                # Security events table (separate for high-priority events)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS security_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        source_ip TEXT,
                        user_id TEXT,
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        result TEXT NOT NULL,
                        threat_level TEXT,
                        details TEXT NOT NULL,
                        checksum TEXT NOT NULL
                    )
                """)
                
                # File access tracking
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS file_access_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        file_hash TEXT,
                        file_size INTEGER,
                        result TEXT NOT NULL,
                        details TEXT
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_events(category)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_level ON audit_events(level)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_security_timestamp ON security_events(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_file_access_timestamp ON file_access_log(timestamp)")
                
                conn.commit()
                self.logger.info("Audit database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize audit database: {e}")
            raise
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        process_id = os.getpid()
        return hashlib.sha256(f"{timestamp}_{process_id}".encode()).hexdigest()[:16]
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'process_count': len(psutil.pids()),
                'platform': os.name,
                'pid': os.getpid()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {'error': str(e)}
    
    def _calculate_event_checksum(self, event: AuditEvent) -> str:
        """Calculate checksum for audit event integrity"""
        event_data = f"{event.timestamp.isoformat()}{event.level.value}{event.category.value}{event.action}{event.resource}{event.result}"
        return hashlib.sha256(event_data.encode()).hexdigest()
    
    def log_event(self, level: AuditLevel, category: AuditCategory, component: str,
                  action: str, resource: str, result: str, details: Dict[str, Any],
                  user_id: Optional[str] = None, duration_ms: Optional[float] = None):
        """Log an audit event"""
        try:
            event = AuditEvent(
                timestamp=datetime.now(),
                level=level,
                category=category,
                event_id=self._generate_event_id(),
                user_id=user_id,
                session_id=self.session_id,
                component=component,
                action=action,
                resource=resource,
                result=result,
                details=details,
                duration_ms=duration_ms,
                system_info=self._get_system_info()
            )
            
            checksum = self._calculate_event_checksum(event)
            
            with self.lock:
                with sqlite3.connect(self.audit_db_path) as conn:
                    conn.execute("""
                        INSERT INTO audit_events 
                        (timestamp, level, category, event_id, user_id, session_id, component,
                         action, resource, result, details, duration_ms, system_info, checksum)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event.timestamp.isoformat(),
                        event.level.value,
                        event.category.value,
                        event.event_id,
                        event.user_id,
                        event.session_id,
                        event.component,
                        event.action,
                        event.resource,
                        event.result,
                        json.dumps(event.details),
                        event.duration_ms,
                        json.dumps(event.system_info),
                        checksum
                    ))
                    conn.commit()
            
            # Log to standard logger as well for immediate visibility
            log_message = f"[{event.category.value}] {event.component}.{event.action} on {event.resource}: {event.result}"
            if event.level == AuditLevel.ERROR or event.level == AuditLevel.CRITICAL:
                self.logger.error(log_message)
            elif event.level == AuditLevel.WARNING:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
                
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
    
    def log_security_event(self, event_type: str, severity: str, resource: str,
                          action: str, result: str, details: Dict[str, Any],
                          user_id: Optional[str] = None, source_ip: Optional[str] = None,
                          threat_level: Optional[str] = None):
        """Log a security-specific event"""
        try:
            timestamp = datetime.now()
            event_data = f"{timestamp.isoformat()}{event_type}{resource}{action}{result}"
            checksum = hashlib.sha256(event_data.encode()).hexdigest()
            
            with self.lock:
                with sqlite3.connect(self.audit_db_path) as conn:
                    conn.execute("""
                        INSERT INTO security_events 
                        (timestamp, event_type, severity, source_ip, user_id, resource,
                         action, result, threat_level, details, checksum)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        timestamp.isoformat(),
                        event_type,
                        severity,
                        source_ip,
                        user_id,
                        resource,
                        action,
                        result,
                        threat_level,
                        json.dumps(details),
                        checksum
                    ))
                    conn.commit()
            
            # Also log as regular audit event
            self.log_event(
                level=AuditLevel.SECURITY,
                category=AuditCategory.SECURITY,
                component="security_monitor",
                action=action,
                resource=resource,
                result=result,
                details={**details, 'event_type': event_type, 'severity': severity},
                user_id=user_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")
    
    def log_file_access(self, file_path: Union[str, Path], operation: str, result: str,
                       user_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log file access operations"""
        file_path = Path(file_path)
        
        try:
            # Calculate file hash if file exists and operation is read
            file_hash = None
            file_size = None
            
            if file_path.exists() and operation in ['read', 'load']:
                try:
                    file_size = file_path.stat().st_size
                    if file_size < 10 * 1024 * 1024:  # Only hash files smaller than 10MB
                        hash_sha256 = hashlib.sha256()
                        with open(file_path, "rb") as f:
                            for chunk in iter(lambda: f.read(4096), b""):
                                hash_sha256.update(chunk)
                        file_hash = hash_sha256.hexdigest()
                except Exception:
                    pass  # Continue without hash if calculation fails
            
            with self.lock:
                with sqlite3.connect(self.audit_db_path) as conn:
                    conn.execute("""
                        INSERT INTO file_access_log 
                        (timestamp, file_path, operation, user_id, session_id, 
                         file_hash, file_size, result, details)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        str(file_path),
                        operation,
                        user_id,
                        self.session_id,
                        file_hash,
                        file_size,
                        result,
                        json.dumps(details) if details else None
                    ))
                    conn.commit()
            
            # Also log as regular audit event
            self.log_event(
                level=AuditLevel.INFO,
                category=AuditCategory.FILE_ACCESS,
                component="file_manager",
                action=operation,
                resource=str(file_path),
                result=result,
                details=details or {},
                user_id=user_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log file access: {e}")
    
    def log_image_processing(self, image_path: str, operation: str, result: str,
                           processing_time_ms: float, details: Dict[str, Any],
                           user_id: Optional[str] = None):
        """Log image processing operations"""
        self.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.IMAGE_PROCESSING,
            component="image_processor",
            action=operation,
            resource=image_path,
            result=result,
            details=details,
            user_id=user_id,
            duration_ms=processing_time_ms
        )
    
    def log_validation_event(self, image_path: str, validation_type: str, result: str,
                           compliance_score: float, issues: List[str],
                           processing_time_ms: float, user_id: Optional[str] = None):
        """Log validation operations"""
        self.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.VALIDATION,
            component="validator",
            action=validation_type,
            resource=image_path,
            result=result,
            details={
                'compliance_score': compliance_score,
                'issues': issues,
                'validation_type': validation_type
            },
            user_id=user_id,
            duration_ms=processing_time_ms
        )
    
    def log_system_metrics(self):
        """Log current system performance metrics"""
        try:
            metrics = SystemMetrics(
                cpu_percent=psutil.cpu_percent(),
                memory_percent=psutil.virtual_memory().percent,
                disk_usage_percent=psutil.disk_usage('/').percent,
                process_count=len(psutil.pids()),
                timestamp=datetime.now()
            )
            
            with self.lock:
                with sqlite3.connect(self.audit_db_path) as conn:
                    conn.execute("""
                        INSERT INTO system_metrics 
                        (timestamp, cpu_percent, memory_percent, disk_usage_percent, 
                         process_count, session_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        metrics.timestamp.isoformat(),
                        metrics.cpu_percent,
                        metrics.memory_percent,
                        metrics.disk_usage_percent,
                        metrics.process_count,
                        self.session_id
                    ))
                    conn.commit()
                    
        except Exception as e:
            self.logger.error(f"Failed to log system metrics: {e}")
    
    def _log_system_event(self, level: AuditLevel, category: AuditCategory,
                         action: str, resource: str, result: str, details: Dict[str, Any]):
        """Log system-level events"""
        self.log_event(
            level=level,
            category=category,
            component="system",
            action=action,
            resource=resource,
            result=result,
            details=details
        )
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.sha256(f"{timestamp}_{self.session_id}".encode()).hexdigest()[:12]
    
    def get_audit_events(self, limit: int = 100, category: Optional[AuditCategory] = None,
                        level: Optional[AuditLevel] = None, 
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve audit events with filtering"""
        try:
            query = "SELECT * FROM audit_events WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category.value)
            
            if level:
                query += " AND level = ?"
                params.append(level.value)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'timestamp': row[1],
                        'level': row[2],
                        'category': row[3],
                        'event_id': row[4],
                        'user_id': row[5],
                        'session_id': row[6],
                        'component': row[7],
                        'action': row[8],
                        'resource': row[9],
                        'result': row[10],
                        'details': json.loads(row[11]) if row[11] else {},
                        'duration_ms': row[12],
                        'system_info': json.loads(row[13]) if row[13] else {},
                        'checksum': row[14]
                    }
                    for row in results
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get audit events: {e}")
            return []
    
    def get_security_events(self, limit: int = 50, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve security events"""
        try:
            query = "SELECT * FROM security_events WHERE 1=1"
            params = []
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'timestamp': row[1],
                        'event_type': row[2],
                        'severity': row[3],
                        'source_ip': row[4],
                        'user_id': row[5],
                        'resource': row[6],
                        'action': row[7],
                        'result': row[8],
                        'threat_level': row[9],
                        'details': json.loads(row[10]) if row[10] else {},
                        'checksum': row[11]
                    }
                    for row in results
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get security events: {e}")
            return []
    
    def get_file_access_log(self, limit: int = 100, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve file access log"""
        try:
            query = "SELECT * FROM file_access_log WHERE 1=1"
            params = []
            
            if file_path:
                query += " AND file_path LIKE ?"
                params.append(f"%{file_path}%")
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'timestamp': row[1],
                        'file_path': row[2],
                        'operation': row[3],
                        'user_id': row[4],
                        'session_id': row[5],
                        'file_hash': row[6],
                        'file_size': row[7],
                        'result': row[8],
                        'details': json.loads(row[9]) if row[9] else {}
                    }
                    for row in results
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get file access log: {e}")
            return []
    
    def cleanup_old_logs(self):
        """Clean up old audit logs based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            with self.lock:
                with sqlite3.connect(self.audit_db_path) as conn:
                    # Count records to be deleted
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM audit_events WHERE timestamp < ?",
                        (cutoff_date.isoformat(),)
                    )
                    audit_count = cursor.fetchone()[0]
                    
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM system_metrics WHERE timestamp < ?",
                        (cutoff_date.isoformat(),)
                    )
                    metrics_count = cursor.fetchone()[0]
                    
                    # Delete old records
                    conn.execute(
                        "DELETE FROM audit_events WHERE timestamp < ?",
                        (cutoff_date.isoformat(),)
                    )
                    
                    conn.execute(
                        "DELETE FROM system_metrics WHERE timestamp < ?",
                        (cutoff_date.isoformat(),)
                    )
                    
                    conn.execute(
                        "DELETE FROM file_access_log WHERE timestamp < ?",
                        (cutoff_date.isoformat(),)
                    )
                    
                    conn.commit()
                    
                    # Vacuum database to reclaim space
                    conn.execute("VACUUM")
                    
                    self._log_system_event(
                        level=AuditLevel.INFO,
                        category=AuditCategory.SYSTEM,
                        action="cleanup_logs",
                        resource="audit_database",
                        result="success",
                        details={
                            'audit_events_deleted': audit_count,
                            'metrics_deleted': metrics_count,
                            'retention_days': self.retention_days
                        }
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")
    
    def validate_audit_integrity(self) -> Dict[str, Any]:
        """Validate integrity of audit logs"""
        validation_results = {
            'integrity_valid': True,
            'total_events': 0,
            'corrupted_events': 0,
            'missing_checksums': 0,
            'issues': []
        }
        
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.execute("SELECT * FROM audit_events")
                events = cursor.fetchall()
                
                validation_results['total_events'] = len(events)
                
                for event in events:
                    if not event[14]:  # checksum column
                        validation_results['missing_checksums'] += 1
                        continue
                    
                    # Recreate event object for checksum validation
                    temp_event = AuditEvent(
                        timestamp=datetime.fromisoformat(event[1]),
                        level=AuditLevel(event[2]),
                        category=AuditCategory(event[3]),
                        event_id=event[4],
                        user_id=event[5],
                        session_id=event[6],
                        component=event[7],
                        action=event[8],
                        resource=event[9],
                        result=event[10],
                        details={},
                        duration_ms=event[12],
                        system_info={}
                    )
                    
                    expected_checksum = self._calculate_event_checksum(temp_event)
                    
                    if event[14] != expected_checksum:
                        validation_results['corrupted_events'] += 1
                        validation_results['integrity_valid'] = False
                        validation_results['issues'].append(f"Event ID {event[0]} has invalid checksum")
                
                if validation_results['missing_checksums'] > 0:
                    validation_results['issues'].append(f"{validation_results['missing_checksums']} events missing checksums")
                
        except Exception as e:
            validation_results['integrity_valid'] = False
            validation_results['issues'].append(f"Validation error: {e}")
            self.logger.error(f"Failed to validate audit integrity: {e}")
        
        return validation_results
    
    def generate_audit_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive audit report for a time period"""
        try:
            report = {
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'summary': {},
                'events_by_category': {},
                'events_by_level': {},
                'security_events': [],
                'file_access_summary': {},
                'system_performance': {},
                'integrity_check': {}
            }
            
            # Get events for the period
            events = self.get_audit_events(
                limit=10000,  # Large limit to get all events in period
                start_time=start_time,
                end_time=end_time
            )
            
            report['summary']['total_events'] = len(events)
            
            # Categorize events
            for event in events:
                category = event['category']
                level = event['level']
                
                report['events_by_category'][category] = report['events_by_category'].get(category, 0) + 1
                report['events_by_level'][level] = report['events_by_level'].get(level, 0) + 1
            
            # Get security events
            report['security_events'] = self.get_security_events(limit=100)
            
            # File access summary
            file_access_events = self.get_file_access_log(limit=1000)
            report['file_access_summary'] = {
                'total_file_operations': len(file_access_events),
                'operations_by_type': {}
            }
            
            for file_event in file_access_events:
                op_type = file_event['operation']
                report['file_access_summary']['operations_by_type'][op_type] = \
                    report['file_access_summary']['operations_by_type'].get(op_type, 0) + 1
            
            # Integrity check
            report['integrity_check'] = self.validate_audit_integrity()
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate audit report: {e}")
            return {'error': str(e)}