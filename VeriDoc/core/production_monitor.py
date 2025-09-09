"""
Production Monitoring System

This module provides comprehensive monitoring for production deployment,
including performance tracking, error monitoring, and system health checks.
"""

import time
import json
import threading
import psutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
from collections import deque, defaultdict

from core.config_manager import ConfigManager
from utils.logger import Logger


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: float
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    disk_usage_percent: float
    gpu_usage_percent: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    
    @property
    def health_score(self) -> float:
        """Calculate overall system health score (0-1)"""
        cpu_score = max(0, 1.0 - (self.cpu_usage_percent / 100.0))
        memory_score = max(0, 1.0 - (self.memory_usage_percent / 100.0))
        disk_score = max(0, 1.0 - (self.disk_usage_percent / 100.0))
        
        return (cpu_score + memory_score + disk_score) / 3.0


@dataclass
class ProcessingMetrics:
    """Processing performance metrics"""
    timestamp: float
    image_id: str
    processing_time_seconds: float
    memory_peak_mb: float
    success: bool
    error_message: Optional[str] = None
    validation_score: Optional[float] = None
    auto_fix_applied: bool = False
    
    @property
    def performance_score(self) -> float:
        """Calculate processing performance score (0-1)"""
        if not self.success:
            return 0.0
        
        # Target: 3 seconds processing time
        time_score = max(0, 1.0 - (self.processing_time_seconds / 6.0))
        
        # Target: 1GB memory usage
        memory_score = max(0, 1.0 - (self.memory_peak_mb / 2000.0))
        
        return (time_score + memory_score) / 2.0


@dataclass
class AlertThresholds:
    """Alert threshold configuration"""
    cpu_usage_percent: float = 80.0
    memory_usage_percent: float = 85.0
    disk_usage_percent: float = 90.0
    processing_time_seconds: float = 10.0
    error_rate_percent: float = 5.0
    queue_size: int = 100
    response_time_seconds: float = 30.0


class ProductionMonitor:
    """Comprehensive production monitoring system"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = Logger(__name__)
        
        # Monitoring configuration
        self.monitoring_enabled = True
        self.monitoring_interval = 5.0  # seconds
        self.metrics_retention_hours = 24
        
        # Alert configuration
        self.alert_thresholds = AlertThresholds()
        self.alert_callbacks: List[Callable] = []
        
        # Metrics storage
        self.system_metrics = deque(maxlen=1000)
        self.processing_metrics = deque(maxlen=5000)
        self.error_counts = defaultdict(int)
        self.alert_history = deque(maxlen=100)
        
        # Database for persistent storage
        self.db_path = Path("logs/monitoring.db")
        self._init_database()
        
        # Monitoring threads
        self.system_monitor_thread = None
        self.alert_monitor_thread = None
        self.monitoring_lock = threading.Lock()
        
        # Performance tracking
        self.start_time = time.time()
        self.total_images_processed = 0
        self.total_processing_time = 0.0
        self.current_processing_queue = 0
        
        # Health status
        self.system_health = "healthy"
        self.last_health_check = time.time()
    
    def _init_database(self):
        """Initialize monitoring database"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    timestamp REAL PRIMARY KEY,
                    cpu_usage REAL,
                    memory_usage_mb REAL,
                    memory_usage_percent REAL,
                    disk_usage_percent REAL,
                    gpu_usage REAL,
                    gpu_memory_mb REAL,
                    health_score REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_metrics (
                    timestamp REAL,
                    image_id TEXT,
                    processing_time REAL,
                    memory_peak_mb REAL,
                    success INTEGER,
                    error_message TEXT,
                    validation_score REAL,
                    auto_fix_applied INTEGER,
                    performance_score REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    timestamp REAL,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    resolved INTEGER DEFAULT 0
                )
            """)
            
            conn.commit()
    
    def start_monitoring(self):
        """Start production monitoring"""
        if not self.monitoring_enabled:
            return
        
        self.logger.info("🔍 Starting production monitoring...")
        
        # Start system monitoring thread
        self.system_monitor_thread = threading.Thread(
            target=self._system_monitoring_loop,
            daemon=True
        )
        self.system_monitor_thread.start()
        
        # Start alert monitoring thread
        self.alert_monitor_thread = threading.Thread(
            target=self._alert_monitoring_loop,
            daemon=True
        )
        self.alert_monitor_thread.start()
        
        self.logger.info("✅ Production monitoring started")
    
    def stop_monitoring(self):
        """Stop production monitoring"""
        self.monitoring_enabled = False
        
        if self.system_monitor_thread:
            self.system_monitor_thread.join(timeout=5.0)
        
        if self.alert_monitor_thread:
            self.alert_monitor_thread.join(timeout=5.0)
        
        self.logger.info("🛑 Production monitoring stopped")
    
    def _system_monitoring_loop(self):
        """Main system monitoring loop"""
        while self.monitoring_enabled:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                with self.monitoring_lock:
                    self.system_metrics.append(metrics)
                
                # Store in database
                self._store_system_metrics(metrics)
                
                # Check for alerts
                self._check_system_alerts(metrics)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in system monitoring: {str(e)}")
                time.sleep(self.monitoring_interval)
    
    def _alert_monitoring_loop(self):
        """Alert monitoring and notification loop"""
        while self.monitoring_enabled:
            try:
                # Check processing queue
                self._check_processing_queue_alerts()
                
                # Check error rates
                self._check_error_rate_alerts()
                
                # Check system health
                self._check_system_health()
                
                # Clean old metrics
                self._cleanup_old_metrics()
                
                time.sleep(30.0)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in alert monitoring: {str(e)}")
                time.sleep(30.0)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1.0)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage_mb = (memory.total - memory.available) / (1024 * 1024)
        memory_usage_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        
        # GPU usage (if available)
        gpu_usage = None
        gpu_memory = None
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_usage = gpu.load * 100
                gpu_memory = gpu.memoryUsed
        except ImportError:
            pass
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_usage_mb,
            memory_usage_percent=memory_usage_percent,
            disk_usage_percent=disk_usage_percent,
            gpu_usage_percent=gpu_usage,
            gpu_memory_mb=gpu_memory
        )
    
    def _store_system_metrics(self, metrics: SystemMetrics):
        """Store system metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO system_metrics 
                    (timestamp, cpu_usage, memory_usage_mb, memory_usage_percent, 
                     disk_usage_percent, gpu_usage, gpu_memory_mb, health_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.timestamp,
                    metrics.cpu_usage_percent,
                    metrics.memory_usage_mb,
                    metrics.memory_usage_percent,
                    metrics.disk_usage_percent,
                    metrics.gpu_usage_percent,
                    metrics.gpu_memory_mb,
                    metrics.health_score
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing system metrics: {str(e)}")
    
    def record_processing_metrics(self, image_id: str, processing_time: float, 
                                memory_peak: float, success: bool, 
                                error_message: Optional[str] = None,
                                validation_score: Optional[float] = None,
                                auto_fix_applied: bool = False):
        """Record processing metrics for an image"""
        metrics = ProcessingMetrics(
            timestamp=time.time(),
            image_id=image_id,
            processing_time_seconds=processing_time,
            memory_peak_mb=memory_peak,
            success=success,
            error_message=error_message,
            validation_score=validation_score,
            auto_fix_applied=auto_fix_applied
        )
        
        with self.monitoring_lock:
            self.processing_metrics.append(metrics)
            self.total_images_processed += 1
            self.total_processing_time += processing_time
            
            if not success and error_message:
                self.error_counts[error_message] += 1
        
        # Store in database
        self._store_processing_metrics(metrics)
        
        # Check for processing alerts
        self._check_processing_alerts(metrics)
    
    def _store_processing_metrics(self, metrics: ProcessingMetrics):
        """Store processing metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO processing_metrics 
                    (timestamp, image_id, processing_time, memory_peak_mb, success,
                     error_message, validation_score, auto_fix_applied, performance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.timestamp,
                    metrics.image_id,
                    metrics.processing_time_seconds,
                    metrics.memory_peak_mb,
                    1 if metrics.success else 0,
                    metrics.error_message,
                    metrics.validation_score,
                    1 if metrics.auto_fix_applied else 0,
                    metrics.performance_score
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing processing metrics: {str(e)}")
    
    def _check_system_alerts(self, metrics: SystemMetrics):
        """Check system metrics for alert conditions"""
        alerts = []
        
        if metrics.cpu_usage_percent > self.alert_thresholds.cpu_usage_percent:
            alerts.append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'message': f'High CPU usage: {metrics.cpu_usage_percent:.1f}%'
            })
        
        if metrics.memory_usage_percent > self.alert_thresholds.memory_usage_percent:
            alerts.append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'message': f'High memory usage: {metrics.memory_usage_percent:.1f}%'
            })
        
        if metrics.disk_usage_percent > self.alert_thresholds.disk_usage_percent:
            alerts.append({
                'type': 'high_disk_usage',
                'severity': 'critical',
                'message': f'High disk usage: {metrics.disk_usage_percent:.1f}%'
            })
        
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _check_processing_alerts(self, metrics: ProcessingMetrics):
        """Check processing metrics for alert conditions"""
        alerts = []
        
        if metrics.processing_time_seconds > self.alert_thresholds.processing_time_seconds:
            alerts.append({
                'type': 'slow_processing',
                'severity': 'warning',
                'message': f'Slow processing: {metrics.processing_time_seconds:.1f}s for {metrics.image_id}'
            })
        
        if not metrics.success:
            alerts.append({
                'type': 'processing_error',
                'severity': 'error',
                'message': f'Processing failed for {metrics.image_id}: {metrics.error_message}'
            })
        
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _check_processing_queue_alerts(self):
        """Check processing queue for alerts"""
        if self.current_processing_queue > self.alert_thresholds.queue_size:
            self._trigger_alert({
                'type': 'high_queue_size',
                'severity': 'warning',
                'message': f'High processing queue size: {self.current_processing_queue}'
            })
    
    def _check_error_rate_alerts(self):
        """Check error rates for alerts"""
        if len(self.processing_metrics) < 10:
            return
        
        # Calculate error rate for last 100 processed images
        recent_metrics = list(self.processing_metrics)[-100:]
        error_count = sum(1 for m in recent_metrics if not m.success)
        error_rate = (error_count / len(recent_metrics)) * 100
        
        if error_rate > self.alert_thresholds.error_rate_percent:
            self._trigger_alert({
                'type': 'high_error_rate',
                'severity': 'critical',
                'message': f'High error rate: {error_rate:.1f}% ({error_count}/{len(recent_metrics)})'
            })
    
    def _check_system_health(self):
        """Check overall system health"""
        current_time = time.time()
        
        # Get recent system metrics
        recent_metrics = [m for m in self.system_metrics 
                         if current_time - m.timestamp < 300]  # Last 5 minutes
        
        if not recent_metrics:
            self.system_health = "unknown"
            return
        
        # Calculate average health score
        avg_health = sum(m.health_score for m in recent_metrics) / len(recent_metrics)
        
        # Determine health status
        if avg_health >= 0.8:
            new_health = "healthy"
        elif avg_health >= 0.6:
            new_health = "degraded"
        else:
            new_health = "unhealthy"
        
        # Alert on health status change
        if new_health != self.system_health:
            self._trigger_alert({
                'type': 'health_status_change',
                'severity': 'info' if new_health == 'healthy' else 'warning',
                'message': f'System health changed from {self.system_health} to {new_health}'
            })
            
            self.system_health = new_health
        
        self.last_health_check = current_time
    
    def _trigger_alert(self, alert: Dict[str, Any]):
        """Trigger an alert"""
        alert['timestamp'] = time.time()
        
        with self.monitoring_lock:
            self.alert_history.append(alert)
        
        # Store in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO alerts (timestamp, alert_type, severity, message)
                    VALUES (?, ?, ?, ?)
                """, (
                    alert['timestamp'],
                    alert['type'],
                    alert['severity'],
                    alert['message']
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing alert: {str(e)}")
        
        # Log alert
        log_level = {
            'info': self.logger.info,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }.get(alert['severity'], self.logger.info)
        
        log_level(f"ALERT [{alert['type']}]: {alert['message']}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {str(e)}")
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory issues"""
        current_time = time.time()
        cutoff_time = current_time - (self.metrics_retention_hours * 3600)
        
        # Clean database
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM system_metrics WHERE timestamp < ?", (cutoff_time,))
                conn.execute("DELETE FROM processing_metrics WHERE timestamp < ?", (cutoff_time,))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error cleaning old metrics: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Get latest system metrics
        latest_system = self.system_metrics[-1] if self.system_metrics else None
        
        # Calculate processing statistics
        avg_processing_time = (
            self.total_processing_time / max(self.total_images_processed, 1)
        )
        
        # Get recent error rate
        recent_metrics = [m for m in self.processing_metrics 
                         if current_time - m.timestamp < 3600]  # Last hour
        error_rate = 0.0
        if recent_metrics:
            error_count = sum(1 for m in recent_metrics if not m.success)
            error_rate = (error_count / len(recent_metrics)) * 100
        
        return {
            'system_health': self.system_health,
            'uptime_seconds': uptime,
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'total_images_processed': self.total_images_processed,
            'average_processing_time': avg_processing_time,
            'current_queue_size': self.current_processing_queue,
            'error_rate_percent': error_rate,
            'system_metrics': asdict(latest_system) if latest_system else None,
            'recent_alerts': len([a for a in self.alert_history 
                                if current_time - a['timestamp'] < 3600]),
            'monitoring_enabled': self.monitoring_enabled,
            'last_health_check': self.last_health_check
        }
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate performance report for specified time period"""
        current_time = time.time()
        cutoff_time = current_time - (hours * 3600)
        
        # Get metrics from database
        try:
            with sqlite3.connect(self.db_path) as conn:
                # System metrics
                system_cursor = conn.execute("""
                    SELECT * FROM system_metrics 
                    WHERE timestamp > ? 
                    ORDER BY timestamp
                """, (cutoff_time,))
                system_data = system_cursor.fetchall()
                
                # Processing metrics
                processing_cursor = conn.execute("""
                    SELECT * FROM processing_metrics 
                    WHERE timestamp > ? 
                    ORDER BY timestamp
                """, (cutoff_time,))
                processing_data = processing_cursor.fetchall()
                
                # Alerts
                alerts_cursor = conn.execute("""
                    SELECT * FROM alerts 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC
                """, (cutoff_time,))
                alerts_data = alerts_cursor.fetchall()
        
        except Exception as e:
            self.logger.error(f"Error generating performance report: {str(e)}")
            return {'error': str(e)}
        
        # Analyze system performance
        system_analysis = self._analyze_system_performance(system_data)
        
        # Analyze processing performance
        processing_analysis = self._analyze_processing_performance(processing_data)
        
        # Analyze alerts
        alerts_analysis = self._analyze_alerts(alerts_data)
        
        return {
            'report_period_hours': hours,
            'report_generated': current_time,
            'system_performance': system_analysis,
            'processing_performance': processing_analysis,
            'alerts_summary': alerts_analysis,
            'recommendations': self._generate_recommendations(
                system_analysis, processing_analysis, alerts_analysis
            )
        }
    
    def _analyze_system_performance(self, data: List) -> Dict[str, Any]:
        """Analyze system performance data"""
        if not data:
            return {'error': 'No system data available'}
        
        cpu_values = [row[1] for row in data if row[1] is not None]
        memory_values = [row[3] for row in data if row[3] is not None]
        health_values = [row[7] for row in data if row[7] is not None]
        
        return {
            'cpu_usage': {
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'peak': max(cpu_values) if cpu_values else 0,
                'minimum': min(cpu_values) if cpu_values else 0
            },
            'memory_usage': {
                'average': sum(memory_values) / len(memory_values) if memory_values else 0,
                'peak': max(memory_values) if memory_values else 0,
                'minimum': min(memory_values) if memory_values else 0
            },
            'health_score': {
                'average': sum(health_values) / len(health_values) if health_values else 0,
                'minimum': min(health_values) if health_values else 0
            },
            'data_points': len(data)
        }
    
    def _analyze_processing_performance(self, data: List) -> Dict[str, Any]:
        """Analyze processing performance data"""
        if not data:
            return {'error': 'No processing data available'}
        
        processing_times = [row[2] for row in data if row[2] is not None]
        success_count = sum(1 for row in data if row[4] == 1)
        total_count = len(data)
        
        return {
            'total_processed': total_count,
            'success_rate': (success_count / total_count) * 100 if total_count > 0 else 0,
            'processing_time': {
                'average': sum(processing_times) / len(processing_times) if processing_times else 0,
                'peak': max(processing_times) if processing_times else 0,
                'minimum': min(processing_times) if processing_times else 0
            },
            'throughput_per_hour': total_count if total_count > 0 else 0
        }
    
    def _analyze_alerts(self, data: List) -> Dict[str, Any]:
        """Analyze alerts data"""
        if not data:
            return {'total_alerts': 0, 'by_type': {}, 'by_severity': {}}
        
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        
        for row in data:
            alert_type = row[1]
            severity = row[2]
            by_type[alert_type] += 1
            by_severity[severity] += 1
        
        return {
            'total_alerts': len(data),
            'by_type': dict(by_type),
            'by_severity': dict(by_severity),
            'recent_alerts': data[:10]  # Last 10 alerts
        }
    
    def _generate_recommendations(self, system_analysis: Dict, 
                                processing_analysis: Dict, 
                                alerts_analysis: Dict) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # System performance recommendations
        if 'cpu_usage' in system_analysis:
            avg_cpu = system_analysis['cpu_usage']['average']
            if avg_cpu > 80:
                recommendations.append(
                    f"High average CPU usage ({avg_cpu:.1f}%). Consider upgrading CPU or optimizing processing."
                )
        
        if 'memory_usage' in system_analysis:
            avg_memory = system_analysis['memory_usage']['average']
            if avg_memory > 85:
                recommendations.append(
                    f"High average memory usage ({avg_memory:.1f}%). Consider adding more RAM or optimizing memory usage."
                )
        
        # Processing performance recommendations
        if 'processing_time' in processing_analysis:
            avg_time = processing_analysis['processing_time']['average']
            if avg_time > 5.0:
                recommendations.append(
                    f"Slow average processing time ({avg_time:.1f}s). Consider GPU acceleration or model optimization."
                )
        
        if 'success_rate' in processing_analysis:
            success_rate = processing_analysis['success_rate']
            if success_rate < 95:
                recommendations.append(
                    f"Low success rate ({success_rate:.1f}%). Review error patterns and improve error handling."
                )
        
        # Alert-based recommendations
        if alerts_analysis['total_alerts'] > 50:
            recommendations.append(
                f"High number of alerts ({alerts_analysis['total_alerts']}). Review alert thresholds and system stability."
            )
        
        if not recommendations:
            recommendations.append("System performance is within acceptable parameters.")
        
        return recommendations
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)
    
    def set_queue_size(self, size: int):
        """Update current processing queue size"""
        self.current_processing_queue = size
    
    def configure_alert_thresholds(self, **kwargs):
        """Configure alert thresholds"""
        for key, value in kwargs.items():
            if hasattr(self.alert_thresholds, key):
                setattr(self.alert_thresholds, key, value)


if __name__ == "__main__":
    # Example usage
    from core.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    monitor = ProductionMonitor(config_manager)
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Simulate some processing
    import random
    for i in range(10):
        processing_time = random.uniform(1.0, 8.0)
        memory_peak = random.uniform(500, 1500)
        success = random.random() > 0.1
        
        monitor.record_processing_metrics(
            image_id=f"test_image_{i:03d}.jpg",
            processing_time=processing_time,
            memory_peak=memory_peak,
            success=success,
            validation_score=random.uniform(0.7, 1.0) if success else None
        )
        
        time.sleep(1)
    
    # Get status
    status = monitor.get_system_status()
    print("System Status:")
    print(json.dumps(status, indent=2))
    
    # Generate report
    report = monitor.get_performance_report(hours=1)
    print("\nPerformance Report:")
    print(json.dumps(report, indent=2))
    
    # Stop monitoring
    monitor.stop_monitoring()