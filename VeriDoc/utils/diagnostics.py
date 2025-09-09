"""
Advanced diagnostics and system analysis for Veridoc photo verification.
Provides detailed system health monitoring, performance analysis, and debugging tools.
"""

import os
import sys
import time
import json
import psutil
import threading
import traceback
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import logging


@dataclass
class SystemHealth:
    """System health metrics and status."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    gpu_available: bool
    gpu_memory: Optional[float]
    temperature: Optional[float]
    load_average: Optional[List[float]]
    network_status: bool
    timestamp: float


@dataclass
class ProcessingProfile:
    """Processing performance profile."""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_peak: float
    cpu_peak: float
    success: bool
    error_message: Optional[str]
    input_size: Optional[Tuple[int, int]]
    output_size: Optional[Tuple[int, int]]


@dataclass
class DebugSession:
    """Debug session information."""
    session_id: str
    start_time: float
    end_time: Optional[float]
    operations: List[ProcessingProfile]
    artifacts_saved: List[str]
    total_errors: int
    total_warnings: int


class SystemDiagnostics:
    """
    Advanced system diagnostics and monitoring for performance analysis
    and debugging support.
    """
    
    def __init__(self, 
                 monitoring_interval: float = 5.0,
                 max_history_size: int = 1000,
                 enable_gpu_monitoring: bool = True):
        """
        Initialize system diagnostics.
        
        Args:
            monitoring_interval: Seconds between system health checks
            max_history_size: Maximum number of health records to keep
            enable_gpu_monitoring: Whether to monitor GPU if available
        """
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.enable_gpu_monitoring = enable_gpu_monitoring
        
        # Health monitoring
        self.health_history: List[SystemHealth] = []
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Performance profiling
        self.processing_profiles: List[ProcessingProfile] = []
        self.active_operations: Dict[str, float] = {}
        
        # Debug sessions
        self.debug_sessions: Dict[str, DebugSession] = {}
        self.current_session: Optional[str] = None
        
        # Setup logging
        self.logger = logging.getLogger("veridoc_diagnostics")
        
        # Check system capabilities
        self._check_system_capabilities()
    
    def _check_system_capabilities(self):
        """Check and log system capabilities."""
        capabilities = {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'python_version': sys.version,
            'platform': sys.platform,
            'opencv_available': self._check_opencv(),
            'gpu_available': self._check_gpu_availability(),
            'disk_space_gb': psutil.disk_usage('/').total / (1024**3)
        }
        
        self.logger.info(f"System capabilities: {capabilities}")
        return capabilities
    
    def _check_opencv(self) -> bool:
        """Check if OpenCV is available."""
        try:
            import cv2
            return True
        except ImportError:
            return False
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available for processing."""
        if not self.enable_gpu_monitoring:
            return False
        
        try:
            # Try NVIDIA GPU first
            import pynvml
            pynvml.nvmlInit()
            return pynvml.nvmlDeviceGetCount() > 0
        except:
            try:
                # Try AMD GPU
                import pyamdgpuinfo
                return len(pyamdgpuinfo.get_gpu_info()) > 0
            except:
                return False
    
    def start_monitoring(self):
        """Start continuous system health monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system health monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        self.logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                health = self._collect_system_health()
                self.health_history.append(health)
                
                # Trim history if too large
                if len(self.health_history) > self.max_history_size:
                    self.health_history = self.health_history[-self.max_history_size:]
                
                # Check for alerts
                self._check_health_alerts(health)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(self.monitoring_interval * 2)
    
    def _collect_system_health(self) -> SystemHealth:
        """Collect current system health metrics."""
        # Basic system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU metrics
        gpu_available = False
        gpu_memory = None
        try:
            if self.enable_gpu_monitoring:
                gpu_memory = self._get_gpu_memory_usage()
                gpu_available = gpu_memory is not None
        except:
            pass
        
        # Temperature (if available)
        temperature = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Get CPU temperature
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower():
                        temperature = entries[0].current
                        break
        except:
            pass
        
        # Load average (Unix systems)
        load_average = None
        try:
            if hasattr(os, 'getloadavg'):
                load_average = list(os.getloadavg())
        except:
            pass
        
        # Network status (simple check)
        network_status = True
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except:
            network_status = False
        
        return SystemHealth(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            gpu_available=gpu_available,
            gpu_memory=gpu_memory,
            temperature=temperature,
            load_average=load_average,
            network_status=network_status,
            timestamp=time.time()
        )
    
    def _get_gpu_memory_usage(self) -> Optional[float]:
        """Get GPU memory usage percentage."""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            return (info.used / info.total) * 100
        except:
            return None
    
    def _check_health_alerts(self, health: SystemHealth):
        """Check for system health alerts."""
        alerts = []
        
        if health.cpu_usage > 90:
            alerts.append(f"High CPU usage: {health.cpu_usage:.1f}%")
        
        if health.memory_usage > 85:
            alerts.append(f"High memory usage: {health.memory_usage:.1f}%")
        
        if health.disk_usage > 90:
            alerts.append(f"High disk usage: {health.disk_usage:.1f}%")
        
        if health.temperature and health.temperature > 80:
            alerts.append(f"High temperature: {health.temperature:.1f}°C")
        
        if health.gpu_memory and health.gpu_memory > 90:
            alerts.append(f"High GPU memory usage: {health.gpu_memory:.1f}%")
        
        for alert in alerts:
            self.logger.warning(f"System alert: {alert}")
    
    def start_debug_session(self, session_id: Optional[str] = None) -> str:
        """Start a new debug session."""
        if session_id is None:
            session_id = f"debug_{int(time.time())}"
        
        session = DebugSession(
            session_id=session_id,
            start_time=time.time(),
            end_time=None,
            operations=[],
            artifacts_saved=[],
            total_errors=0,
            total_warnings=0
        )
        
        self.debug_sessions[session_id] = session
        self.current_session = session_id
        
        self.logger.info(f"Debug session started: {session_id}")
        return session_id
    
    def end_debug_session(self, session_id: Optional[str] = None) -> Optional[DebugSession]:
        """End a debug session and return session data."""
        if session_id is None:
            session_id = self.current_session
        
        if session_id not in self.debug_sessions:
            return None
        
        session = self.debug_sessions[session_id]
        session.end_time = time.time()
        
        if self.current_session == session_id:
            self.current_session = None
        
        self.logger.info(f"Debug session ended: {session_id}")
        return session
    
    def start_operation_profiling(self, operation_name: str) -> str:
        """Start profiling an operation."""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        self.active_operations[operation_id] = time.time()
        
        return operation_id
    
    def end_operation_profiling(self, 
                              operation_id: str,
                              success: bool = True,
                              error_message: Optional[str] = None,
                              input_size: Optional[Tuple[int, int]] = None,
                              output_size: Optional[Tuple[int, int]] = None) -> ProcessingProfile:
        """End operation profiling and create profile."""
        if operation_id not in self.active_operations:
            raise ValueError(f"Operation {operation_id} not found in active operations")
        
        start_time = self.active_operations.pop(operation_id)
        end_time = time.time()
        
        # Get peak resource usage during operation
        memory_peak = psutil.virtual_memory().percent
        cpu_peak = psutil.cpu_percent()
        
        # Extract operation name from ID
        operation_name = operation_id.rsplit('_', 1)[0]
        
        profile = ProcessingProfile(
            operation_name=operation_name,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            memory_peak=memory_peak,
            cpu_peak=cpu_peak,
            success=success,
            error_message=error_message,
            input_size=input_size,
            output_size=output_size
        )
        
        self.processing_profiles.append(profile)
        
        # Add to current debug session if active
        if self.current_session and self.current_session in self.debug_sessions:
            self.debug_sessions[self.current_session].operations.append(profile)
            if not success:
                self.debug_sessions[self.current_session].total_errors += 1
        
        return profile
    
    def save_debug_artifact(self, 
                          artifact_name: str,
                          artifact_data: Any,
                          artifact_type: str = "json") -> str:
        """Save debug artifact to disk."""
        if not self.current_session:
            raise ValueError("No active debug session")
        
        # Create debug directory
        debug_dir = Path("temp/debug") / self.current_session
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Save artifact
        timestamp = int(time.time() * 1000)
        filename = f"{artifact_name}_{timestamp}.{artifact_type}"
        filepath = debug_dir / filename
        
        try:
            if artifact_type == "json":
                with open(filepath, 'w') as f:
                    json.dump(artifact_data, f, indent=2, default=str)
            elif artifact_type == "npy":
                np.save(filepath, artifact_data)
            elif artifact_type == "jpg" or artifact_type == "png":
                import cv2
                cv2.imwrite(str(filepath), artifact_data)
            else:
                # Generic binary save
                with open(filepath, 'wb') as f:
                    f.write(artifact_data)
            
            # Record in session
            session = self.debug_sessions[self.current_session]
            session.artifacts_saved.append(str(filepath))
            
            self.logger.debug(f"Debug artifact saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save debug artifact {filename}: {e}")
            raise
    
    def get_performance_summary(self, 
                              operation_name: Optional[str] = None,
                              time_window: Optional[float] = None) -> Dict[str, Any]:
        """Get performance summary for operations."""
        profiles = self.processing_profiles
        
        # Filter by operation name
        if operation_name:
            profiles = [p for p in profiles if p.operation_name == operation_name]
        
        # Filter by time window
        if time_window:
            cutoff_time = time.time() - time_window
            profiles = [p for p in profiles if p.start_time >= cutoff_time]
        
        if not profiles:
            return {"message": "No profiles found matching criteria"}
        
        # Calculate statistics
        durations = [p.duration for p in profiles]
        memory_peaks = [p.memory_peak for p in profiles]
        cpu_peaks = [p.cpu_peak for p in profiles]
        success_rate = sum(1 for p in profiles if p.success) / len(profiles)
        
        return {
            "total_operations": len(profiles),
            "success_rate": success_rate,
            "duration_stats": {
                "mean": np.mean(durations),
                "median": np.median(durations),
                "min": np.min(durations),
                "max": np.max(durations),
                "std": np.std(durations)
            },
            "memory_stats": {
                "mean_peak": np.mean(memory_peaks),
                "max_peak": np.max(memory_peaks)
            },
            "cpu_stats": {
                "mean_peak": np.mean(cpu_peaks),
                "max_peak": np.max(cpu_peaks)
            },
            "error_count": sum(1 for p in profiles if not p.success),
            "time_range": {
                "start": min(p.start_time for p in profiles),
                "end": max(p.end_time for p in profiles)
            }
        }
    
    def get_system_health_summary(self, time_window: Optional[float] = None) -> Dict[str, Any]:
        """Get system health summary."""
        health_records = self.health_history
        
        # Filter by time window
        if time_window:
            cutoff_time = time.time() - time_window
            health_records = [h for h in health_records if h.timestamp >= cutoff_time]
        
        if not health_records:
            return {"message": "No health records found"}
        
        # Calculate statistics
        cpu_usage = [h.cpu_usage for h in health_records]
        memory_usage = [h.memory_usage for h in health_records]
        disk_usage = [h.disk_usage for h in health_records]
        
        gpu_usage = [h.gpu_memory for h in health_records if h.gpu_memory is not None]
        temperatures = [h.temperature for h in health_records if h.temperature is not None]
        
        return {
            "record_count": len(health_records),
            "time_range": {
                "start": min(h.timestamp for h in health_records),
                "end": max(h.timestamp for h in health_records)
            },
            "cpu_usage": {
                "mean": np.mean(cpu_usage),
                "max": np.max(cpu_usage),
                "current": health_records[-1].cpu_usage
            },
            "memory_usage": {
                "mean": np.mean(memory_usage),
                "max": np.max(memory_usage),
                "current": health_records[-1].memory_usage
            },
            "disk_usage": {
                "mean": np.mean(disk_usage),
                "max": np.max(disk_usage),
                "current": health_records[-1].disk_usage
            },
            "gpu_usage": {
                "mean": np.mean(gpu_usage) if gpu_usage else None,
                "max": np.max(gpu_usage) if gpu_usage else None,
                "available": health_records[-1].gpu_available
            },
            "temperature": {
                "mean": np.mean(temperatures) if temperatures else None,
                "max": np.max(temperatures) if temperatures else None,
                "current": health_records[-1].temperature
            },
            "network_status": health_records[-1].network_status
        }
    
    def export_debug_session(self, session_id: str, export_path: Optional[str] = None) -> str:
        """Export debug session data to file."""
        if session_id not in self.debug_sessions:
            raise ValueError(f"Debug session {session_id} not found")
        
        session = self.debug_sessions[session_id]
        
        if export_path is None:
            export_path = f"logs/debug_session_{session_id}.json"
        
        # Prepare export data
        export_data = {
            "session_info": asdict(session),
            "system_capabilities": self._check_system_capabilities(),
            "performance_summary": self.get_performance_summary(),
            "health_summary": self.get_system_health_summary(
                time_window=session.end_time - session.start_time if session.end_time else None
            )
        }
        
        # Save to file
        Path(export_path).parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Debug session exported to {export_path}")
        return export_path
    
    def cleanup(self):
        """Cleanup diagnostics resources."""
        self.stop_monitoring()
        
        # Save final summary
        try:
            summary = {
                "performance_summary": self.get_performance_summary(),
                "health_summary": self.get_system_health_summary(),
                "active_sessions": list(self.debug_sessions.keys()),
                "total_profiles": len(self.processing_profiles)
            }
            
            summary_path = f"logs/diagnostics_summary_{int(time.time())}.json"
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            self.logger.info(f"Diagnostics summary saved to {summary_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save diagnostics summary: {e}")


# Convenience functions for easy integration
def profile_operation(diagnostics: SystemDiagnostics, operation_name: str):
    """Decorator for profiling operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            operation_id = diagnostics.start_operation_profiling(operation_name)
            try:
                result = func(*args, **kwargs)
                diagnostics.end_operation_profiling(operation_id, success=True)
                return result
            except Exception as e:
                diagnostics.end_operation_profiling(
                    operation_id, 
                    success=False, 
                    error_message=str(e)
                )
                raise
        return wrapper
    return decorator


def save_debug_image(diagnostics: SystemDiagnostics, 
                    image: np.ndarray, 
                    name: str) -> Optional[str]:
    """Save debug image if debug session is active."""
    try:
        if diagnostics.current_session:
            return diagnostics.save_debug_artifact(name, image, "jpg")
    except Exception as e:
        logging.getLogger("veridoc_diagnostics").warning(f"Failed to save debug image: {e}")
    return None