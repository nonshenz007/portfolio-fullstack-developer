"""
Offline Update Manager for Veridoc Universal
Handles offline update packages and system updates without internet connectivity
"""

import os
import json
import zipfile
import hashlib
import logging
import shutil
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import sqlite3
import tempfile

@dataclass
class UpdatePackage:
    """Information about an update package"""
    package_id: str
    version: str
    package_type: str  # 'models', 'configs', 'system', 'security'
    file_path: str
    checksum: str
    size_bytes: int
    created_at: datetime
    description: str
    dependencies: List[str]
    is_verified: bool

@dataclass
class UpdateResult:
    """Result of an update operation"""
    success: bool
    package_id: str
    installed_version: str
    previous_version: Optional[str]
    files_updated: List[str]
    backup_path: Optional[str]
    error_message: Optional[str]
    rollback_available: bool

class UpdateManager:
    """
    Manages offline update packages for models, configurations, and system components
    """
    
    def __init__(self, updates_dir: str = "updates", backup_dir: str = "backups"):
        self.logger = logging.getLogger(__name__)
        self.updates_dir = Path(updates_dir)
        self.backup_dir = Path(backup_dir)
        self.update_db_path = Path("cache/updates/update_history.db")
        
        # Ensure directories exist
        self.updates_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.update_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize update database
        self._init_update_database()
        
        self.logger.info("Update Manager initialized for offline operation")
    
    def _init_update_database(self):
        """Initialize SQLite database for update tracking"""
        try:
            with sqlite3.connect(self.update_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS update_packages (
                        package_id TEXT PRIMARY KEY,
                        version TEXT NOT NULL,
                        package_type TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        description TEXT NOT NULL,
                        dependencies TEXT NOT NULL,
                        is_verified BOOLEAN NOT NULL,
                        status TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS update_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        package_id TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        result TEXT NOT NULL,
                        previous_version TEXT,
                        new_version TEXT,
                        files_affected TEXT,
                        backup_path TEXT,
                        error_details TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS system_versions (
                        component TEXT PRIMARY KEY,
                        current_version TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        update_source TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                self.logger.info("Update database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize update database: {e}")
            raise
    
    def validate_update_package(self, package_path: Union[str, Path]) -> Tuple[bool, Optional[UpdatePackage]]:
        """Validate an offline update package"""
        package_path = Path(package_path)
        
        try:
            if not package_path.exists():
                self.logger.error(f"Update package not found: {package_path}")
                return False, None
            
            # Calculate package checksum
            package_checksum = self._calculate_file_checksum(package_path)
            
            # Extract and validate package metadata
            with zipfile.ZipFile(package_path, 'r') as zip_file:
                # Check for required metadata file
                if 'update_manifest.json' not in zip_file.namelist():
                    self.logger.error("Update package missing manifest file")
                    return False, None
                
                # Read manifest
                with zip_file.open('update_manifest.json') as manifest_file:
                    manifest = json.load(manifest_file)
                
                # Validate manifest structure
                required_fields = ['package_id', 'version', 'package_type', 'description', 'files']
                for field in required_fields:
                    if field not in manifest:
                        self.logger.error(f"Update manifest missing required field: {field}")
                        return False, None
                
                # Validate package integrity
                if 'checksum' in manifest and manifest['checksum'] != package_checksum:
                    self.logger.error("Update package checksum mismatch")
                    return False, None
                
                # Create UpdatePackage object
                update_package = UpdatePackage(
                    package_id=manifest['package_id'],
                    version=manifest['version'],
                    package_type=manifest['package_type'],
                    file_path=str(package_path),
                    checksum=package_checksum,
                    size_bytes=package_path.stat().st_size,
                    created_at=datetime.now(),
                    description=manifest['description'],
                    dependencies=manifest.get('dependencies', []),
                    is_verified=True
                )
                
                self.logger.info(f"Update package validated: {update_package.package_id} v{update_package.version}")
                return True, update_package
                
        except Exception as e:
            self.logger.error(f"Failed to validate update package {package_path}: {e}")
            return False, None
    
    def install_update_package(self, package_path: Union[str, Path], force: bool = False) -> UpdateResult:
        """Install an offline update package"""
        package_path = Path(package_path)
        
        try:
            # Validate package first
            is_valid, update_package = self.validate_update_package(package_path)
            if not is_valid or not update_package:
                return UpdateResult(
                    success=False,
                    package_id="unknown",
                    installed_version="",
                    error_message="Package validation failed",
                    files_updated=[],
                    backup_path=None,
                    rollback_available=False
                )
            
            # Check if package is already installed
            current_version = self._get_current_version(update_package.package_type)
            if current_version == update_package.version and not force:
                return UpdateResult(
                    success=True,
                    package_id=update_package.package_id,
                    installed_version=update_package.version,
                    previous_version=current_version,
                    files_updated=[],
                    backup_path=None,
                    error_message="Package already installed",
                    rollback_available=False
                )
            
            # Create backup before installation
            backup_path = self._create_backup(update_package.package_type)
            
            # Extract and install package
            files_updated = []
            with zipfile.ZipFile(package_path, 'r') as zip_file:
                with zip_file.open('update_manifest.json') as manifest_file:
                    manifest = json.load(manifest_file)
                
                # Install files according to manifest
                for file_info in manifest['files']:
                    source_path = file_info['source']
                    target_path = Path(file_info['target'])
                    
                    # Ensure target directory exists
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Extract file
                    with zip_file.open(source_path) as source_file:
                        with open(target_path, 'wb') as target_file:
                            shutil.copyfileobj(source_file, target_file)
                    
                    files_updated.append(str(target_path))
                    self.logger.info(f"Updated file: {target_path}")
            
            # Update version tracking
            self._update_system_version(
                update_package.package_type,
                update_package.version,
                update_package.package_id
            )
            
            # Record installation in database
            self._record_update_operation(
                package_id=update_package.package_id,
                operation="install",
                result="success",
                previous_version=current_version,
                new_version=update_package.version,
                files_affected=files_updated,
                backup_path=str(backup_path) if backup_path else None
            )
            
            # Store package info
            self._store_package_info(update_package, "installed")
            
            result = UpdateResult(
                success=True,
                package_id=update_package.package_id,
                installed_version=update_package.version,
                previous_version=current_version,
                files_updated=files_updated,
                backup_path=str(backup_path) if backup_path else None,
                error_message=None,
                rollback_available=backup_path is not None
            )
            
            self.logger.info(f"Successfully installed update package: {update_package.package_id}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to install update package: {e}"
            self.logger.error(error_msg)
            
            # Record failed installation
            self._record_update_operation(
                package_id=update_package.package_id if 'update_package' in locals() else "unknown",
                operation="install",
                result="failure",
                error_details=str(e)
            )
            
            return UpdateResult(
                success=False,
                package_id=update_package.package_id if 'update_package' in locals() else "unknown",
                installed_version="",
                error_message=error_msg,
                files_updated=[],
                backup_path=None,
                rollback_available=False
            )
    
    def rollback_update(self, package_id: str) -> UpdateResult:
        """Rollback a previously installed update"""
        try:
            # Find the most recent installation of this package
            with sqlite3.connect(self.update_db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM update_history 
                    WHERE package_id = ? AND operation = 'install' AND result = 'success'
                    ORDER BY timestamp DESC LIMIT 1
                """, (package_id,))
                
                result = cursor.fetchone()
                if not result:
                    return UpdateResult(
                        success=False,
                        package_id=package_id,
                        installed_version="",
                        error_message="No successful installation found for rollback",
                        files_updated=[],
                        backup_path=None,
                        rollback_available=False
                    )
                
                backup_path = result[8]  # backup_path column
                if not backup_path or not Path(backup_path).exists():
                    return UpdateResult(
                        success=False,
                        package_id=package_id,
                        installed_version="",
                        error_message="Backup not available for rollback",
                        files_updated=[],
                        backup_path=None,
                        rollback_available=False
                    )
            
            # Restore from backup
            files_restored = self._restore_from_backup(backup_path)
            
            # Record rollback operation
            self._record_update_operation(
                package_id=package_id,
                operation="rollback",
                result="success",
                files_affected=files_restored,
                backup_path=backup_path
            )
            
            self.logger.info(f"Successfully rolled back update: {package_id}")
            
            return UpdateResult(
                success=True,
                package_id=package_id,
                installed_version="rolled_back",
                files_updated=files_restored,
                backup_path=backup_path,
                error_message=None,
                rollback_available=False
            )
            
        except Exception as e:
            error_msg = f"Failed to rollback update {package_id}: {e}"
            self.logger.error(error_msg)
            
            self._record_update_operation(
                package_id=package_id,
                operation="rollback",
                result="failure",
                error_details=str(e)
            )
            
            return UpdateResult(
                success=False,
                package_id=package_id,
                installed_version="",
                error_message=error_msg,
                files_updated=[],
                backup_path=None,
                rollback_available=False
            )
    
    def _create_backup(self, component_type: str) -> Optional[Path]:
        """Create backup of current system state"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{component_type}_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Define backup targets based on component type
            backup_targets = {
                'models': ['models/'],
                'configs': ['config/'],
                'system': ['core/', 'ai/', 'validation/', 'quality/', 'autofix/', 'rules/'],
                'security': ['core/security_manager.py', 'core/offline_manager.py']
            }
            
            targets = backup_targets.get(component_type, [])
            backed_up_files = []
            
            for target in targets:
                target_path = Path(target)
                if target_path.exists():
                    if target_path.is_file():
                        # Backup single file
                        backup_file_path = backup_path / target_path.name
                        shutil.copy2(target_path, backup_file_path)
                        backed_up_files.append(str(target_path))
                    else:
                        # Backup directory
                        backup_dir_path = backup_path / target_path.name
                        shutil.copytree(target_path, backup_dir_path, dirs_exist_ok=True)
                        backed_up_files.extend([str(p) for p in target_path.rglob('*') if p.is_file()])
            
            # Create backup manifest
            backup_manifest = {
                'component_type': component_type,
                'timestamp': timestamp,
                'files': backed_up_files,
                'backup_path': str(backup_path)
            }
            
            with open(backup_path / 'backup_manifest.json', 'w') as f:
                json.dump(backup_manifest, f, indent=2)
            
            self.logger.info(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {component_type}: {e}")
            return None
    
    def _restore_from_backup(self, backup_path: str) -> List[str]:
        """Restore system from backup"""
        backup_path = Path(backup_path)
        restored_files = []
        
        try:
            # Read backup manifest
            manifest_path = backup_path / 'backup_manifest.json'
            if not manifest_path.exists():
                raise Exception("Backup manifest not found")
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Restore files
            for backup_item in backup_path.iterdir():
                if backup_item.name == 'backup_manifest.json':
                    continue
                
                if backup_item.is_file():
                    # Restore single file
                    target_path = Path(backup_item.name)
                    shutil.copy2(backup_item, target_path)
                    restored_files.append(str(target_path))
                else:
                    # Restore directory
                    target_path = Path(backup_item.name)
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(backup_item, target_path)
                    restored_files.extend([str(p) for p in target_path.rglob('*') if p.is_file()])
            
            self.logger.info(f"Restored {len(restored_files)} files from backup")
            return restored_files
            
        except Exception as e:
            self.logger.error(f"Failed to restore from backup {backup_path}: {e}")
            return []
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def _get_current_version(self, component_type: str) -> Optional[str]:
        """Get current version of a component"""
        try:
            with sqlite3.connect(self.update_db_path) as conn:
                cursor = conn.execute(
                    "SELECT current_version FROM system_versions WHERE component = ?",
                    (component_type,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            self.logger.error(f"Failed to get current version for {component_type}: {e}")
            return None
    
    def _update_system_version(self, component_type: str, version: str, update_source: str):
        """Update system version tracking"""
        try:
            with sqlite3.connect(self.update_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO system_versions 
                    (component, current_version, last_updated, update_source)
                    VALUES (?, ?, ?, ?)
                """, (component_type, version, datetime.now().isoformat(), update_source))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to update system version: {e}")
    
    def _store_package_info(self, package: UpdatePackage, status: str):
        """Store package information in database"""
        try:
            with sqlite3.connect(self.update_db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO update_packages 
                    (package_id, version, package_type, file_path, checksum, size_bytes,
                     created_at, description, dependencies, is_verified, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    package.package_id,
                    package.version,
                    package.package_type,
                    package.file_path,
                    package.checksum,
                    package.size_bytes,
                    package.created_at.isoformat(),
                    package.description,
                    json.dumps(package.dependencies),
                    package.is_verified,
                    status
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to store package info: {e}")
    
    def _record_update_operation(self, package_id: str, operation: str, result: str,
                                previous_version: Optional[str] = None,
                                new_version: Optional[str] = None,
                                files_affected: Optional[List[str]] = None,
                                backup_path: Optional[str] = None,
                                error_details: Optional[str] = None):
        """Record update operation in history"""
        try:
            with sqlite3.connect(self.update_db_path) as conn:
                conn.execute("""
                    INSERT INTO update_history 
                    (timestamp, package_id, operation, result, previous_version, new_version,
                     files_affected, backup_path, error_details)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    package_id,
                    operation,
                    result,
                    previous_version,
                    new_version,
                    json.dumps(files_affected) if files_affected else None,
                    backup_path,
                    error_details
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to record update operation: {e}")
    
    def get_update_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get update history"""
        try:
            with sqlite3.connect(self.update_db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM update_history ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                results = cursor.fetchall()
                
                return [
                    {
                        'id': row[0],
                        'timestamp': row[1],
                        'package_id': row[2],
                        'operation': row[3],
                        'result': row[4],
                        'previous_version': row[5],
                        'new_version': row[6],
                        'files_affected': json.loads(row[7]) if row[7] else [],
                        'backup_path': row[8],
                        'error_details': row[9]
                    }
                    for row in results
                ]
        except Exception as e:
            self.logger.error(f"Failed to get update history: {e}")
            return []
    
    def get_installed_packages(self) -> List[Dict[str, Any]]:
        """Get list of installed packages"""
        try:
            with sqlite3.connect(self.update_db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM update_packages WHERE status = 'installed'"
                )
                results = cursor.fetchall()
                
                return [
                    {
                        'package_id': row[0],
                        'version': row[1],
                        'package_type': row[2],
                        'file_path': row[3],
                        'checksum': row[4],
                        'size_bytes': row[5],
                        'created_at': row[6],
                        'description': row[7],
                        'dependencies': json.loads(row[8]),
                        'is_verified': bool(row[9]),
                        'status': row[10]
                    }
                    for row in results
                ]
        except Exception as e:
            self.logger.error(f"Failed to get installed packages: {e}")
            return []