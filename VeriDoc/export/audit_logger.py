"""
Audit Logger for comprehensive tracking of all processing and export activities.
Provides detailed audit trails with timestamps and activity logging.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
from dataclasses import dataclass, asdict


@dataclass
class AuditEvent:
    """Represents a single audit event."""
    timestamp: datetime
    event_type: str
    event_category: str
    image_path: Optional[str]
    user_id: Optional[str]
    session_id: str
    details: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None


class AuditLogger:
    """
    Comprehensive audit logging system for tracking all processing activities.
    Maintains detailed logs with timestamps, user actions, and system events.
    """
    
    def __init__(self, log_directory: str = "logs", db_path: Optional[str] = None):
        """Initialize audit logger with database and file logging."""
        self.logger = logging.getLogger(__name__)
        self.log_directory = log_directory
        self.session_id = self._generate_session_id()
        
        # Create logs directory
        os.makedirs(log_directory, exist_ok=True)
        
        # Initialize database
        self.db_path = db_path or os.path.join(log_directory, "audit_log.db")
        self._init_database()
        
        # Thread lock for database operations
        self._db_lock = threading.Lock()
        
        # In-memory cache for current session
        self._session_events = []
        
        # Statistics cache
        self._stats_cache = {}
        self._stats_cache_time = None
        
        self.logger.info(f"Audit logger initialized with session ID: {self.session_id}")
    
    def log_processing_start(self, image_path: str, format_name: str, 
                           options: Dict[str, Any] = None) -> str:
        """Log the start of image processing."""
        event_id = self._generate_event_id()
        
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="processing_start",
            event_category="processing",
            image_path=image_path,
            user_id=None,  # Could be extended for multi-user systems
            session_id=self.session_id,
            details={
                "event_id": event_id,
                "format_name": format_name,
                "processing_options": options or {},
                "image_size": self._get_file_size(image_path)
            },
            success=True
        )
        
        self._log_event(event)
        return event_id
    
    def log_processing_complete(self, image_path: str, event_id: str,
                              processing_result: Dict[str, Any]) -> None:
        """Log successful completion of image processing."""
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="processing_complete",
            event_category="processing",
            image_path=image_path,
            user_id=None,
            session_id=self.session_id,
            details={
                "event_id": event_id,
                "overall_compliance": processing_result.get("overall_compliance", 0),
                "passes_requirements": processing_result.get("passes_requirements", False),
                "processing_time": processing_result.get("processing_time", 0),
                "validation_results": self._sanitize_for_logging(
                    processing_result.get("validation_results", {})
                )
            },
            success=True
        )
        
        self._log_event(event)
    
    def log_processing_error(self, image_path: str, event_id: str, 
                           error_message: str, error_details: Dict[str, Any] = None) -> None:
        """Log processing error."""
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="processing_error",
            event_category="processing",
            image_path=image_path,
            user_id=None,
            session_id=self.session_id,
            details={
                "event_id": event_id,
                "error_details": error_details or {},
                "stack_trace": error_details.get("stack_trace") if error_details else None
            },
            success=False,
            error_message=error_message
        )
        
        self._log_event(event)
    
    def log_export_start(self, image_path: str, export_directory: str) -> str:
        """Log the start of export operation."""
        event_id = self._generate_event_id()
        
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="export_start",
            event_category="export",
            image_path=image_path,
            user_id=None,
            session_id=self.session_id,
            details={
                "event_id": event_id,
                "export_directory": export_directory
            },
            success=True
        )
        
        self._log_event(event)
        return event_id
    
    def log_export_complete(self, image_path: str, export_directory: str,
                          generated_files: List[str]) -> str:
        """Log successful completion of export operation."""
        audit_log_path = os.path.join(export_directory, "audit_log.json")
        
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="export_complete",
            event_category="export",
            image_path=image_path,
            user_id=None,
            session_id=self.session_id,
            details={
                "export_directory": export_directory,
                "generated_files": generated_files,
                "file_count": len(generated_files)
            },
            success=True
        )
        
        self._log_event(event)
        
        # Create export-specific audit log
        self._create_export_audit_log(image_path, export_directory, audit_log_path)
        
        return audit_log_path
    
    def log_export_error(self, image_path: str, error_message: str) -> None:
        """Log export error."""
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="export_error",
            event_category="export",
            image_path=image_path,
            user_id=None,
            session_id=self.session_id,
            details={},
            success=False,
            error_message=error_message
        )
        
        self._log_event(event)
    
    def log_batch_processing_start(self, image_paths: List[str], 
                                 format_name: str) -> str:
        """Log the start of batch processing."""
        event_id = self._generate_event_id()
        
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="batch_processing_start",
            event_category="batch_processing",
            image_path=None,
            user_id=None,
            session_id=self.session_id,
            details={
                "event_id": event_id,
                "image_count": len(image_paths),
                "format_name": format_name,
                "image_paths": image_paths[:10]  # Log first 10 paths to avoid huge logs
            },
            success=True
        )
        
        self._log_event(event)
        return event_id
    
    def log_batch_processing_complete(self, event_id: str, 
                                    batch_results: Dict[str, Any]) -> None:
        """Log completion of batch processing."""
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="batch_processing_complete",
            event_category="batch_processing",
            image_path=None,
            user_id=None,
            session_id=self.session_id,
            details={
                "event_id": event_id,
                "total_images": batch_results.get("total_images", 0),
                "successful_images": batch_results.get("successful_images", 0),
                "failed_images": batch_results.get("failed_images", 0),
                "average_compliance": batch_results.get("average_compliance", 0),
                "processing_time": batch_results.get("total_processing_time", 0)
            },
            success=True
        )
        
        self._log_event(event)
    
    def log_batch_export_start(self, export_directory: str, image_count: int) -> str:
        """Log the start of batch export operation."""
        event_id = self._generate_event_id()
        
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="batch_export_start",
            event_category="batch_export",
            image_path=None,
            user_id=None,
            session_id=self.session_id,
            details={
                "event_id": event_id,
                "export_directory": export_directory,
                "image_count": image_count
            },
            success=True
        )
        
        self._log_event(event)
        return event_id
    
    def log_batch_export_complete(self, export_directory: str, 
                                generated_files: List[str],
                                batch_analysis: Dict[str, Any]) -> str:
        """Log completion of batch export operation."""
        audit_log_path = os.path.join(export_directory, "batch_audit_log.json")
        
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="batch_export_complete",
            event_category="batch_export",
            image_path=None,
            user_id=None,
            session_id=self.session_id,
            details={
                "export_directory": export_directory,
                "generated_files_count": len(generated_files),
                "batch_summary": self._sanitize_for_logging(batch_analysis)
            },
            success=True
        )
        
        self._log_event(event)
        
        # Create batch export audit log
        self._create_batch_export_audit_log(export_directory, batch_analysis, audit_log_path)
        
        return audit_log_path
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None) -> None:
        """Log user interface actions."""
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type="user_action",
            event_category="ui",
            image_path=details.get("image_path") if details else None,
            user_id=None,
            session_id=self.session_id,
            details={
                "action": action,
                "action_details": details or {}
            },
            success=True
        )
        
        self._log_event(event)
    
    def log_system_event(self, event_type: str, details: Dict[str, Any] = None) -> None:
        """Log system-level events."""
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            event_category="system",
            image_path=None,
            user_id=None,
            session_id=self.session_id,
            details=details or {},
            success=True
        )
        
        self._log_event(event)
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get comprehensive export operation statistics."""
        if (self._stats_cache_time and 
            datetime.now() - self._stats_cache_time < timedelta(minutes=5)):
            return self._stats_cache
        
        try:
            with self._db_lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get export statistics
                stats = {}
                
                # Total exports
                cursor.execute("""
                    SELECT COUNT(*) as total_exports 
                    FROM audit_events 
                    WHERE event_type = 'export_complete'
                """)
                stats['total_exports'] = cursor.fetchone()['total_exports']
                
                # Exports by date (last 30 days)
                cursor.execute("""
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM audit_events 
                    WHERE event_type = 'export_complete' 
                    AND timestamp >= datetime('now', '-30 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """)
                stats['exports_by_date'] = [dict(row) for row in cursor.fetchall()]
                
                # Export success rate
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                        COUNT(*) as total
                    FROM audit_events 
                    WHERE event_category = 'export'
                """)
                result = cursor.fetchone()
                if result['total'] > 0:
                    stats['export_success_rate'] = (result['successful'] / result['total']) * 100
                else:
                    stats['export_success_rate'] = 0
                
                # Processing statistics
                cursor.execute("""
                    SELECT 
                        AVG(CAST(json_extract(details, '$.processing_time') AS REAL)) as avg_processing_time,
                        AVG(CAST(json_extract(details, '$.overall_compliance') AS REAL)) as avg_compliance
                    FROM audit_events 
                    WHERE event_type = 'processing_complete'
                    AND json_extract(details, '$.processing_time') IS NOT NULL
                """)
                processing_stats = cursor.fetchone()
                stats['average_processing_time'] = processing_stats['avg_processing_time'] or 0
                stats['average_compliance_score'] = processing_stats['avg_compliance'] or 0
                
                conn.close()
                
                # Cache results
                self._stats_cache = stats
                self._stats_cache_time = datetime.now()
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get export statistics: {str(e)}")
            return {}
    
    def get_audit_trail(self, image_path: Optional[str] = None, 
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       event_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get filtered audit trail."""
        try:
            with self._db_lock:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Build query
                query = "SELECT * FROM audit_events WHERE 1=1"
                params = []
                
                if image_path:
                    query += " AND image_path = ?"
                    params.append(image_path)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                if event_types:
                    placeholders = ','.join(['?' for _ in event_types])
                    query += f" AND event_type IN ({placeholders})"
                    params.extend(event_types)
                
                query += " ORDER BY timestamp DESC LIMIT 1000"
                
                cursor.execute(query, params)
                events = []
                
                for row in cursor.fetchall():
                    event_dict = dict(row)
                    # Parse JSON details
                    if event_dict['details']:
                        try:
                            event_dict['details'] = json.loads(event_dict['details'])
                        except json.JSONDecodeError:
                            event_dict['details'] = {}
                    events.append(event_dict)
                
                conn.close()
                return events
                
        except Exception as e:
            self.logger.error(f"Failed to get audit trail: {str(e)}")
            return []
    
    def cleanup_old_logs(self, days_old: int = 90) -> int:
        """Clean up audit logs older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with self._db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM audit_events 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                self.logger.info(f"Cleaned up {deleted_count} old audit log entries")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {str(e)}")
            return 0
    
    def _init_database(self) -> None:
        """Initialize SQLite database for audit logging."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_category TEXT NOT NULL,
                    image_path TEXT,
                    user_id TEXT,
                    session_id TEXT NOT NULL,
                    details TEXT,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON audit_events(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type 
                ON audit_events(event_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_image_path 
                ON audit_events(image_path)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON audit_events(session_id)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audit database: {str(e)}")
            raise
    
    def _log_event(self, event: AuditEvent) -> None:
        """Log event to database and session cache."""
        try:
            # Add to session cache
            self._session_events.append(event)
            
            # Log to database
            with self._db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO audit_events 
                    (timestamp, event_type, event_category, image_path, user_id, 
                     session_id, details, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.timestamp.isoformat(),
                    event.event_type,
                    event.event_category,
                    event.image_path,
                    event.user_id,
                    event.session_id,
                    json.dumps(event.details, default=str),
                    event.success,
                    event.error_message
                ))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {str(e)}")
    
    def _create_export_audit_log(self, image_path: str, export_directory: str, 
                               audit_log_path: str) -> None:
        """Create export-specific audit log file."""
        try:
            # Get relevant events for this image
            image_events = [
                asdict(event) for event in self._session_events 
                if event.image_path == image_path
            ]
            
            audit_data = {
                "export_metadata": {
                    "image_path": image_path,
                    "export_directory": export_directory,
                    "generated_at": datetime.now().isoformat(),
                    "session_id": self.session_id
                },
                "processing_events": image_events,
                "export_summary": {
                    "total_events": len(image_events),
                    "processing_events": len([e for e in image_events if e['event_category'] == 'processing']),
                    "export_events": len([e for e in image_events if e['event_category'] == 'export'])
                }
            }
            
            with open(audit_log_path, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to create export audit log: {str(e)}")
    
    def _create_batch_export_audit_log(self, export_directory: str, 
                                     batch_analysis: Dict[str, Any],
                                     audit_log_path: str) -> None:
        """Create batch export audit log file."""
        try:
            # Get batch-related events
            batch_events = [
                asdict(event) for event in self._session_events 
                if event.event_category in ['batch_processing', 'batch_export']
            ]
            
            audit_data = {
                "batch_export_metadata": {
                    "export_directory": export_directory,
                    "generated_at": datetime.now().isoformat(),
                    "session_id": self.session_id
                },
                "batch_analysis": batch_analysis,
                "batch_events": batch_events,
                "export_summary": {
                    "total_batch_events": len(batch_events),
                    "images_processed": batch_analysis.get('summary_statistics', {}).get('total_images', 0),
                    "success_rate": batch_analysis.get('summary_statistics', {}).get('success_rate', 0)
                }
            }
            
            with open(audit_log_path, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to create batch export audit log: {str(e)}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        return f"event_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size safely."""
        try:
            return os.path.getsize(file_path)
        except (OSError, FileNotFoundError):
            return 0
    
    def _sanitize_for_logging(self, data: Any) -> Any:
        """Sanitize data for logging (remove sensitive information)."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Skip potentially large or sensitive data
                if key in ['raw_image_data', 'image_array', 'binary_data']:
                    sanitized[key] = f"<{type(value).__name__} data excluded>"
                else:
                    sanitized[key] = self._sanitize_for_logging(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_for_logging(item) for item in data[:100]]  # Limit list size
        else:
            return data