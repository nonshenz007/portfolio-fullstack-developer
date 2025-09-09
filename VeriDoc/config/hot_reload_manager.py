"""
Hot-Reload Configuration Manager for VeriDoc Universal

This module provides hot-reload capabilities for format configurations,
allowing updates to take effect without application restart.
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Callable, Optional, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
import logging

from rules.format_rule_engine import FormatRuleEngine

logger = logging.getLogger(__name__)


class ConfigurationChangeHandler(FileSystemEventHandler):
    """File system event handler for configuration changes."""
    
    def __init__(self, reload_callback: Callable[[], None]):
        """
        Initialize the change handler.
        
        Args:
            reload_callback: Function to call when configuration changes
        """
        super().__init__()
        self.reload_callback = reload_callback
        self.last_reload_time = 0
        self.reload_debounce_seconds = 1.0  # Prevent rapid reloads
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith('.json'):
            self._trigger_reload(event.src_path, 'modified')
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and event.src_path.endswith('.json'):
            self._trigger_reload(event.src_path, 'created')
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory and event.src_path.endswith('.json'):
            self._trigger_reload(event.src_path, 'deleted')
    
    def _trigger_reload(self, file_path: str, event_type: str):
        """Trigger configuration reload with debouncing."""
        current_time = time.time()
        
        if current_time - self.last_reload_time < self.reload_debounce_seconds:
            return  # Skip rapid successive changes
        
        self.last_reload_time = current_time
        
        logger.info(f"Configuration file {event_type}: {file_path}")
        
        # Use a small delay to ensure file write is complete
        threading.Timer(0.5, self.reload_callback).start()


class HotReloadManager:
    """
    Manager for hot-reloading configuration files without application restart.
    """
    
    def __init__(self, format_engine: FormatRuleEngine, 
                 watch_directories: Optional[List[str]] = None):
        """
        Initialize the Hot-Reload Manager.
        
        Args:
            format_engine: FormatRuleEngine instance to manage
            watch_directories: List of directories to watch for changes
        """
        self.format_engine = format_engine
        self.watch_directories = watch_directories or [
            "config/formats",
            "config"
        ]
        
        self.observer = Observer()
        self.is_watching = False
        self.change_handlers: List[Callable[[str], None]] = []
        self.reload_statistics = {
            'total_reloads': 0,
            'successful_reloads': 0,
            'failed_reloads': 0,
            'last_reload_time': None,
            'last_reload_duration': 0.0
        }
        
        # Ensure watch directories exist (only for relative paths)
        for directory in self.watch_directories:
            try:
                dir_path = Path(directory)
                if not dir_path.is_absolute() or str(dir_path).startswith(str(Path.cwd())):
                    dir_path.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not create watch directory {directory}: {e}")
    
    def start_watching(self) -> bool:
        """
        Start watching configuration directories for changes.
        
        Returns:
            True if watching started successfully
        """
        if self.is_watching:
            logger.warning("Hot-reload manager is already watching")
            return True
        
        try:
            # Set up file system event handler
            event_handler = ConfigurationChangeHandler(self._handle_configuration_change)
            
            # Watch each directory
            for directory in self.watch_directories:
                if Path(directory).exists():
                    self.observer.schedule(event_handler, directory, recursive=True)
                    logger.info(f"Watching directory for changes: {directory}")
                else:
                    logger.warning(f"Watch directory does not exist: {directory}")
            
            # Start the observer
            self.observer.start()
            self.is_watching = True
            
            logger.info("Hot-reload manager started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start hot-reload manager: {e}")
            return False
    
    def stop_watching(self) -> bool:
        """
        Stop watching configuration directories.
        
        Returns:
            True if watching stopped successfully
        """
        if not self.is_watching:
            return True
        
        try:
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.is_watching = False
            
            logger.info("Hot-reload manager stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop hot-reload manager: {e}")
            return False
    
    def add_change_handler(self, handler: Callable[[str], None]) -> None:
        """
        Add a callback function to be called when configuration changes.
        
        Args:
            handler: Function that takes a change description string
        """
        self.change_handlers.append(handler)
    
    def remove_change_handler(self, handler: Callable[[str], None]) -> None:
        """
        Remove a change handler.
        
        Args:
            handler: Handler function to remove
        """
        if handler in self.change_handlers:
            self.change_handlers.remove(handler)
    
    def force_reload(self) -> bool:
        """
        Force a configuration reload regardless of file changes.
        
        Returns:
            True if reload was successful
        """
        return self._handle_configuration_change()
    
    def _handle_configuration_change(self) -> bool:
        """Handle configuration change event."""
        start_time = time.time()
        self.reload_statistics['total_reloads'] += 1
        
        try:
            logger.info("Reloading configuration due to file changes...")
            
            # Reload the format engine configuration
            success = self.format_engine.reload_configuration()
            
            if success:
                self.reload_statistics['successful_reloads'] += 1
                duration = time.time() - start_time
                self.reload_statistics['last_reload_duration'] = duration
                self.reload_statistics['last_reload_time'] = time.time()
                
                change_message = f"Configuration reloaded successfully in {duration:.2f}s"
                logger.info(change_message)
                
                # Notify change handlers
                for handler in self.change_handlers:
                    try:
                        handler(change_message)
                    except Exception as e:
                        logger.error(f"Error in change handler: {e}")
                
                return True
            else:
                self.reload_statistics['failed_reloads'] += 1
                error_message = "Configuration reload failed"
                logger.error(error_message)
                
                # Notify change handlers of failure
                for handler in self.change_handlers:
                    try:
                        handler(error_message)
                    except Exception as e:
                        logger.error(f"Error in change handler: {e}")
                
                return False
                
        except Exception as e:
            self.reload_statistics['failed_reloads'] += 1
            error_message = f"Configuration reload error: {e}"
            logger.error(error_message)
            
            # Notify change handlers of error
            for handler in self.change_handlers:
                try:
                    handler(error_message)
                except Exception as e:
                    logger.error(f"Error in change handler: {e}")
            
            return False
    
    def get_reload_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about configuration reloads.
        
        Returns:
            Dictionary with reload statistics
        """
        stats = self.reload_statistics.copy()
        
        # Add success rate
        if stats['total_reloads'] > 0:
            stats['success_rate'] = stats['successful_reloads'] / stats['total_reloads']
        else:
            stats['success_rate'] = 0.0
        
        # Add status
        stats['is_watching'] = self.is_watching
        stats['watch_directories'] = self.watch_directories.copy()
        stats['active_handlers'] = len(self.change_handlers)
        
        return stats
    
    def validate_configuration_integrity(self) -> Dict[str, Any]:
        """
        Validate the integrity of all configuration files.
        
        Returns:
            Validation report
        """
        report = {
            'valid': True,
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': 0,
            'errors': [],
            'warnings': []
        }
        
        for directory in self.watch_directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                report['warnings'].append(f"Watch directory does not exist: {directory}")
                continue
            
            # Check all JSON files in the directory
            for json_file in dir_path.glob("**/*.json"):
                report['total_files'] += 1
                
                try:
                    import json
                    with open(json_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # Basic validation
                    if isinstance(config_data, dict):
                        report['valid_files'] += 1
                    else:
                        report['invalid_files'] += 1
                        report['errors'].append(f"Invalid JSON structure in {json_file}")
                        report['valid'] = False
                
                except json.JSONDecodeError as e:
                    report['invalid_files'] += 1
                    report['errors'].append(f"JSON decode error in {json_file}: {e}")
                    report['valid'] = False
                
                except Exception as e:
                    report['invalid_files'] += 1
                    report['errors'].append(f"Error reading {json_file}: {e}")
                    report['valid'] = False
        
        return report
    
    def backup_configuration(self, backup_directory: str) -> bool:
        """
        Create a backup of all configuration files.
        
        Args:
            backup_directory: Directory to store backup files
            
        Returns:
            True if backup was successful
        """
        try:
            backup_path = Path(backup_directory)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Create timestamp-based backup folder
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_folder = backup_path / f"config_backup_{timestamp}"
            backup_folder.mkdir(exist_ok=True)
            
            files_backed_up = 0
            
            for directory in self.watch_directories:
                dir_path = Path(directory)
                if not dir_path.exists():
                    continue
                
                # Create corresponding directory structure in backup
                try:
                    if dir_path.is_absolute():
                        # For absolute paths, try to make them relative to current working directory
                        try:
                            relative_dir = dir_path.relative_to(Path.cwd())
                        except ValueError:
                            # If path is not under current directory, use just the directory name
                            relative_dir = Path(dir_path.name)
                    else:
                        relative_dir = dir_path
                    
                    backup_subdir = backup_folder / relative_dir
                    backup_subdir.mkdir(parents=True, exist_ok=True)
                except (OSError, ValueError) as e:
                    logger.warning(f"Could not create backup subdirectory for {dir_path}: {e}")
                    backup_subdir = backup_folder / dir_path.name
                    backup_subdir.mkdir(parents=True, exist_ok=True)
                
                # Copy all JSON files
                for json_file in dir_path.glob("**/*.json"):
                    relative_file = json_file.relative_to(dir_path)
                    backup_file = backup_subdir / relative_file
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    import shutil
                    shutil.copy2(json_file, backup_file)
                    files_backed_up += 1
            
            logger.info(f"Configuration backup created: {backup_folder} ({files_backed_up} files)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create configuration backup: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_watching()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_watching()


# Convenience function for easy setup
def setup_hot_reload(format_engine: FormatRuleEngine, 
                    watch_directories: Optional[List[str]] = None,
                    auto_start: bool = True) -> HotReloadManager:
    """
    Set up hot-reload manager with sensible defaults.
    
    Args:
        format_engine: FormatRuleEngine instance
        watch_directories: Optional list of directories to watch
        auto_start: Whether to start watching immediately
        
    Returns:
        Configured HotReloadManager instance
    """
    manager = HotReloadManager(format_engine, watch_directories)
    
    if auto_start:
        manager.start_watching()
    
    return manager