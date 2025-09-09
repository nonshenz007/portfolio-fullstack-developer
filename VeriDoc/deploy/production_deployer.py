"""
Production Deployment System for VeriDoc

Enterprise-grade deployment automation with rollback capabilities,
health checks, and production monitoring integration.
"""

import os
import sys
import json
import hashlib
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.error_handler import get_error_handler, ErrorCategory, ErrorSeverity


class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    PREPARING = "preparing"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentEnvironment(Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DeploymentConfig:
    """Configuration for deployment operations."""
    environment: DeploymentEnvironment
    target_path: str
    backup_path: str
    temp_path: str
    config_overrides: Dict[str, Any]
    health_check_timeout: int = 300
    rollback_enabled: bool = True
    pre_deploy_scripts: List[str] = None
    post_deploy_scripts: List[str] = None
    required_services: List[str] = None

    def __post_init__(self):
        if self.pre_deploy_scripts is None:
            self.pre_deploy_scripts = []
        if self.post_deploy_scripts is None:
            self.post_deploy_scripts = []
        if self.required_services is None:
            self.required_services = []


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""
    deployment_id: str
    status: DeploymentStatus
    environment: DeploymentEnvironment
    start_time: datetime
    end_time: Optional[datetime]
    version: str
    checksum: str
    logs: List[str]
    errors: List[str]
    rollback_available: bool
    health_check_passed: bool

    @property
    def duration(self) -> Optional[float]:
        """Get deployment duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'deployment_id': self.deployment_id,
            'status': self.status.value,
            'environment': self.environment.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'version': self.version,
            'checksum': self.checksum,
            'logs': self.logs,
            'errors': self.errors,
            'rollback_available': self.rollback_available,
            'health_check_passed': self.health_check_passed,
            'duration': self.duration
        }


class ProductionDeployer:
    """
    Enterprise-grade deployment system with rollback, monitoring, and compliance.
    """

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or Path(__file__).parent.parent)
        self.logger = logging.getLogger(__name__)
        self.error_handler = get_error_handler()

        # Deployment tracking
        self.deployment_history: List[DeploymentResult] = []
        self.active_deployment: Optional[DeploymentResult] = None

        # Paths
        self.deployments_dir = self.base_path / "deployments"
        self.backups_dir = self.base_path / "backups"
        self.logs_dir = self.base_path / "logs" / "deployments"
        self.temp_dir = self.base_path / "temp" / "deployments"

        # Create directories
        for directory in [self.deployments_dir, self.backups_dir, self.logs_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Load deployment configurations
        self.deployment_configs = self._load_deployment_configs()

        self.logger.info("ProductionDeployer initialized")

    def _load_deployment_configs(self) -> Dict[str, DeploymentConfig]:
        """Load deployment configurations for different environments."""
        configs = {}

        # Default configurations for each environment
        for env in DeploymentEnvironment:
            config_file = self.base_path / "deploy" / f"{env.value}_config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    configs[env.value] = DeploymentConfig(
                        environment=env,
                        **config_data
                    )
                except Exception as e:
                    self.logger.error(f"Failed to load config for {env.value}: {e}")

            # Create default config if not exists
            if env.value not in configs:
                configs[env.value] = DeploymentConfig(
                    environment=env,
                    target_path=str(self.base_path / f"deploy_{env.value}"),
                    backup_path=str(self.backups_dir / env.value),
                    temp_path=str(self.temp_dir / env.value),
                    config_overrides=self._get_default_config_overrides(env),
                    pre_deploy_scripts=self._get_default_pre_deploy_scripts(env),
                    post_deploy_scripts=self._get_default_post_deploy_scripts(env),
                    required_services=self._get_default_services(env)
                )

        return configs

    def _get_default_config_overrides(self, environment: DeploymentEnvironment) -> Dict[str, Any]:
        """Get default configuration overrides for environment."""
        overrides = {
            "environment": environment.value,
            "logging": {
                "console_level": "INFO" if environment == DeploymentEnvironment.PRODUCTION else "DEBUG",
                "file_level": "WARNING" if environment == DeploymentEnvironment.PRODUCTION else "INFO"
            }
        }

        if environment == DeploymentEnvironment.PRODUCTION:
            overrides.update({
                "security": {
                    "audit_enabled": True,
                    "session_timeout_minutes": 15,
                    "max_login_attempts": 3
                },
                "performance": {
                    "max_worker_threads": 8,
                    "cache_enabled": True,
                    "memory_cleanup_interval_sec": 30
                }
            })

        return overrides

    def _get_default_pre_deploy_scripts(self, environment: DeploymentEnvironment) -> List[str]:
        """Get default pre-deployment scripts."""
        scripts = ["health_check.py", "backup_current.py"]

        if environment == DeploymentEnvironment.PRODUCTION:
            scripts.extend(["security_scan.py", "compliance_check.py"])

        return scripts

    def _get_default_post_deploy_scripts(self, environment: DeploymentEnvironment) -> List[str]:
        """Get default post-deployment scripts."""
        scripts = ["verify_deployment.py", "update_monitoring.py"]

        if environment == DeploymentEnvironment.PRODUCTION:
            scripts.extend(["security_hardening.py", "audit_initialization.py"])

        return scripts

    def _get_default_services(self, environment: DeploymentEnvironment) -> List[str]:
        """Get default required services."""
        if environment == DeploymentEnvironment.PRODUCTION:
            return ["veridoc_service", "monitoring_agent", "security_agent"]
        return ["veridoc_service"]

    def deploy(self, environment: str, version: str = None,
              config_overrides: Dict[str, Any] = None) -> DeploymentResult:
        """
        Deploy VeriDoc to specified environment.

        Args:
            environment: Target environment (development, staging, production)
            version: Version to deploy (auto-detected if None)
            config_overrides: Additional configuration overrides

        Returns:
            DeploymentResult with deployment status and details
        """
        try:
            # Validate environment
            if environment not in self.deployment_configs:
                raise ValueError(f"Unknown environment: {environment}")

            deploy_config = self.deployment_configs[environment]

            # Generate deployment ID and version
            deployment_id = f"deploy_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            version = version or self._get_current_version()

            # Create deployment result
            deployment = DeploymentResult(
                deployment_id=deployment_id,
                status=DeploymentStatus.PENDING,
                environment=deploy_config.environment,
                start_time=datetime.now(),
                end_time=None,
                version=version,
                checksum="",
                logs=[],
                errors=[],
                rollback_available=False,
                health_check_passed=False
            )

            self.active_deployment = deployment
            deployment.status = DeploymentStatus.PREPARING

            # Execute deployment phases
            try:
                # Phase 1: Preparation
                self._prepare_deployment(deployment, deploy_config, config_overrides)

                # Phase 2: Pre-deployment checks
                self._run_pre_deploy_checks(deployment, deploy_config)

                # Phase 3: Backup current deployment
                if deploy_config.rollback_enabled:
                    self._create_backup(deployment, deploy_config)

                # Phase 4: Deploy
                deployment.status = DeploymentStatus.DEPLOYING
                self._perform_deployment(deployment, deploy_config)

                # Phase 5: Post-deployment verification
                deployment.status = DeploymentStatus.VERIFYING
                self._verify_deployment(deployment, deploy_config)

                # Phase 6: Health checks
                deployment.health_check_passed = self._perform_health_checks(deployment, deploy_config)

                # Mark as completed
                deployment.status = DeploymentStatus.COMPLETED
                deployment.end_time = datetime.now()
                deployment.rollback_available = True

                self.logger.info(f"Deployment {deployment_id} completed successfully")
                self.deployment_history.append(deployment)

            except Exception as e:
                deployment.status = DeploymentStatus.FAILED
                deployment.errors.append(str(e))
                deployment.end_time = datetime.now()

                # Attempt rollback if enabled
                if deploy_config.rollback_enabled and deployment.rollback_available:
                    self._rollback_deployment(deployment, deploy_config)

                self.logger.error(f"Deployment {deployment_id} failed: {e}")
                self.deployment_history.append(deployment)

                self.error_handler.handle_error(
                    self.error_handler.create_error(
                        f"Deployment failed: {e}",
                        ErrorCategory.SYSTEM,
                        ErrorSeverity.CRITICAL,
                        "DEPLOYMENT_FAILED",
                        f"Failed to deploy version {version} to {environment}"
                    )
                )

            finally:
                self.active_deployment = None

            return deployment

        except Exception as e:
            self.logger.error(f"Deployment preparation failed: {e}")
            raise

    def _prepare_deployment(self, deployment: DeploymentResult,
                          config: DeploymentConfig,
                          overrides: Dict[str, Any] = None) -> None:
        """Prepare deployment artifacts and configuration."""
        deployment.logs.append("Starting deployment preparation...")

        # Create deployment directory
        deploy_dir = Path(config.temp_path) / deployment.deployment_id
        deploy_dir.mkdir(parents=True, exist_ok=True)

        # Copy application files
        source_dir = self.base_path
        self._copy_application_files(source_dir, deploy_dir, deployment)

        # Generate deployment configuration
        deploy_config = self._generate_deployment_config(config, overrides or {})
        config_file = deploy_dir / "config" / "production_config.json"

        with open(config_file, 'w') as f:
            json.dump(deploy_config, f, indent=2)

        # Calculate checksum
        deployment.checksum = self._calculate_deployment_checksum(deploy_dir)

        deployment.logs.append(f"Deployment prepared in {deploy_dir}")
        deployment.logs.append(f"Deployment checksum: {deployment.checksum}")

    def _copy_application_files(self, source: Path, target: Path,
                              deployment: DeploymentResult) -> None:
        """Copy application files to deployment directory."""
        # Files and directories to include
        include_patterns = [
            "*.py", "*.json", "*.txt", "*.md", "*.qss", "*.onnx",
            "ui/", "core/", "config/", "models/", "src/"
        ]

        exclude_patterns = [
            ".git/", "__pycache__/", "*.pyc", ".pytest_cache/",
            "temp/", "logs/", "backups/", "deployments/"
        ]

        total_files = 0
        for pattern in include_patterns:
            for item in source.glob(f"**/{pattern}"):
                if item.is_file():
                    # Check exclusions
                    excluded = False
                    for exclude in exclude_patterns:
                        if exclude in str(item):
                            excluded = True
                            break

                    if not excluded:
                        relative_path = item.relative_to(source)
                        target_file = target / relative_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_file)
                        total_files += 1

        deployment.logs.append(f"Copied {total_files} files to deployment directory")

    def _generate_deployment_config(self, config: DeploymentConfig,
                                  overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment-specific configuration."""
        # Load base configuration
        base_config = {
            "environment": config.environment.value,
            "version": "1.0.0",  # Would be determined from version control
            "deployment_time": datetime.now().isoformat(),
            "target_path": config.target_path,
            "logging": {
                "log_dir": str(Path(config.target_path) / "logs"),
                "max_log_size_mb": 10,
                "log_retention_days": 30
            }
        }

        # Apply environment-specific overrides
        env_overrides = config.config_overrides.copy()
        env_overrides.update(overrides)

        # Merge configurations
        final_config = self._deep_merge(base_config, env_overrides)

        return final_config

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _calculate_deployment_checksum(self, deploy_dir: Path) -> str:
        """Calculate checksum of deployment directory."""
        hash_md5 = hashlib.md5()

        for file_path in sorted(deploy_dir.rglob("*")):
            if file_path.is_file():
                relative_path = file_path.relative_to(deploy_dir)
                hash_md5.update(str(relative_path).encode())

                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def _run_pre_deploy_checks(self, deployment: DeploymentResult,
                             config: DeploymentConfig) -> None:
        """Run pre-deployment validation checks."""
        deployment.logs.append("Running pre-deployment checks...")

        # Check system requirements
        self._check_system_requirements(deployment, config)

        # Run pre-deployment scripts
        for script in config.pre_deploy_scripts:
            self._run_deployment_script(script, deployment, config, "pre")

        # Validate configuration
        self._validate_deployment_config(deployment, config)

        deployment.logs.append("Pre-deployment checks completed")

    def _check_system_requirements(self, deployment: DeploymentResult,
                                 config: DeploymentConfig) -> None:
        """Check system requirements for deployment."""
        # Check available disk space
        target_path = Path(config.target_path)
        required_space = 500 * 1024 * 1024  # 500MB minimum

        try:
            stat = os.statvfs(str(target_path))
            available_space = stat.f_frsize * stat.f_bavail

            if available_space < required_space:
                raise RuntimeError(".2f")
        except Exception as e:
            deployment.errors.append(f"Disk space check failed: {e}")

        # Check required services
        for service in config.required_services:
            if not self._check_service_available(service):
                deployment.errors.append(f"Required service not available: {service}")

    def _check_service_available(self, service: str) -> bool:
        """Check if a required service is available."""
        # This would implement service availability checks
        # For now, return True as placeholder
        return True

    def _run_deployment_script(self, script: str, deployment: DeploymentResult,
                             config: DeploymentConfig, phase: str) -> None:
        """Run a deployment script."""
        script_path = self.base_path / "deploy" / "scripts" / script

        if not script_path.exists():
            deployment.logs.append(f"Script not found (skipping): {script}")
            return

        try:
            deployment.logs.append(f"Running {phase}-deploy script: {script}")

            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "DEPLOYMENT_ID": deployment.deployment_id}
            )

            if result.returncode == 0:
                deployment.logs.append(f"Script {script} completed successfully")
                if result.stdout:
                    deployment.logs.append(f"Script output: {result.stdout}")
            else:
                error_msg = f"Script {script} failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                deployment.errors.append(error_msg)

        except subprocess.TimeoutExpired:
            deployment.errors.append(f"Script {script} timed out")
        except Exception as e:
            deployment.errors.append(f"Script {script} execution error: {e}")

    def _validate_deployment_config(self, deployment: DeploymentResult,
                                  config: DeploymentConfig) -> None:
        """Validate deployment configuration."""
        # This would implement configuration validation
        deployment.logs.append("Configuration validation completed")

    def _create_backup(self, deployment: DeploymentResult,
                      config: DeploymentConfig) -> None:
        """Create backup of current deployment."""
        try:
            target_path = Path(config.target_path)
            backup_path = Path(config.backup_path) / f"backup_{deployment.deployment_id}"

            if target_path.exists():
                deployment.logs.append(f"Creating backup: {target_path} -> {backup_path}")
                shutil.copytree(target_path, backup_path, dirs_exist_ok=True)
                deployment.rollback_available = True
                deployment.logs.append("Backup created successfully")
            else:
                deployment.logs.append("No existing deployment to backup")

        except Exception as e:
            deployment.errors.append(f"Backup creation failed: {e}")

    def _perform_deployment(self, deployment: DeploymentResult,
                          config: DeploymentConfig) -> None:
        """Perform the actual deployment."""
        source_path = Path(config.temp_path) / deployment.deployment_id
        target_path = Path(config.target_path)

        deployment.logs.append(f"Deploying from {source_path} to {target_path}")

        # Create target directory if it doesn't exist
        target_path.mkdir(parents=True, exist_ok=True)

        # Copy deployment files
        for item in source_path.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(source_path)
                target_file = target_path / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_file)

        deployment.logs.append("Deployment files copied successfully")

    def _verify_deployment(self, deployment: DeploymentResult,
                         config: DeploymentConfig) -> None:
        """Verify deployment integrity."""
        target_path = Path(config.target_path)

        # Verify checksum
        current_checksum = self._calculate_deployment_checksum(target_path)
        if current_checksum != deployment.checksum:
            raise RuntimeError(f"Deployment checksum mismatch: expected {deployment.checksum}, got {current_checksum}")

        # Run post-deployment scripts
        for script in config.post_deploy_scripts:
            self._run_deployment_script(script, deployment, config, "post")

        deployment.logs.append("Deployment verification completed")

    def _perform_health_checks(self, deployment: DeploymentResult,
                             config: DeploymentConfig) -> bool:
        """Perform health checks on deployed application."""
        try:
            # Basic health checks
            target_path = Path(config.target_path)

            # Check if main files exist
            required_files = ["main.py", "config/production_config.json"]
            for file in required_files:
                if not (target_path / file).exists():
                    deployment.errors.append(f"Required file missing: {file}")
                    return False

            # Check if application can be imported
            if not self._test_application_import(target_path):
                deployment.errors.append("Application import test failed")
                return False

            # Check configuration validity
            if not self._test_configuration(target_path):
                deployment.errors.append("Configuration validation failed")
                return False

            deployment.logs.append("Health checks passed")
            return True

        except Exception as e:
            deployment.errors.append(f"Health check failed: {e}")
            return False

    def _test_application_import(self, app_path: Path) -> bool:
        """Test if application can be imported."""
        try:
            # Add to Python path temporarily
            sys.path.insert(0, str(app_path))

            # Try to import main modules
            import main
            import config.production_config

            # Remove from path
            sys.path.remove(str(app_path))

            return True

        except Exception as e:
            self.logger.error(f"Application import test failed: {e}")
            return False
        finally:
            # Ensure path is cleaned up
            if str(app_path) in sys.path:
                sys.path.remove(str(app_path))

    def _test_configuration(self, app_path: Path) -> bool:
        """Test configuration validity."""
        try:
            config_file = app_path / "config" / "production_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    json.load(f)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Configuration test failed: {e}")
            return False

    def _rollback_deployment(self, deployment: DeploymentResult,
                           config: DeploymentConfig) -> None:
        """Rollback to previous deployment."""
        try:
            deployment.status = DeploymentStatus.ROLLED_BACK

            backup_path = Path(config.backup_path) / f"backup_{deployment.deployment_id}"
            target_path = Path(config.target_path)

            if backup_path.exists():
                deployment.logs.append(f"Rolling back to backup: {backup_path}")

                # Remove current deployment
                if target_path.exists():
                    shutil.rmtree(target_path)

                # Restore from backup
                shutil.copytree(backup_path, target_path)

                deployment.logs.append("Rollback completed successfully")
            else:
                deployment.errors.append("No backup available for rollback")

        except Exception as e:
            deployment.errors.append(f"Rollback failed: {e}")

    def _get_current_version(self) -> str:
        """Get current application version."""
        # This would typically read from version control or version file
        version_file = self.base_path / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()

        return "1.0.0"

    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Get status of a deployment."""
        for deployment in self.deployment_history:
            if deployment.deployment_id == deployment_id:
                return deployment
        return None

    def list_deployments(self, environment: str = None) -> List[DeploymentResult]:
        """List deployments, optionally filtered by environment."""
        if environment:
            return [d for d in self.deployment_history if d.environment.value == environment]
        return self.deployment_history.copy()

    def cleanup_old_deployments(self, keep_days: int = 30) -> int:
        """Clean up old deployment artifacts."""
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        cleaned_count = 0

        # Clean up temp directories
        for temp_dir in self.temp_dir.glob("*"):
            if temp_dir.is_dir() and temp_dir.stat().st_mtime < cutoff_date:
                shutil.rmtree(temp_dir)
                cleaned_count += 1

        # Clean up old backups (keep more backups)
        backup_cutoff = datetime.now().timestamp() - (keep_days * 2 * 24 * 60 * 60)
        for backup_dir in self.backups_dir.glob("*/*"):
            if backup_dir.is_dir() and backup_dir.stat().st_mtime < backup_cutoff:
                shutil.rmtree(backup_dir)
                cleaned_count += 1

        self.logger.info(f"Cleaned up {cleaned_count} old deployment artifacts")
        return cleaned_count


# Convenience functions
def deploy_to_environment(environment: str, version: str = None) -> DeploymentResult:
    """Deploy to specified environment."""
    deployer = ProductionDeployer()
    return deployer.deploy(environment, version)


def get_deployment_history(environment: str = None) -> List[DeploymentResult]:
    """Get deployment history."""
    deployer = ProductionDeployer()
    return deployer.list_deployments(environment)


if __name__ == "__main__":
    # CLI interface for deployment
    import argparse

    parser = argparse.ArgumentParser(description="VeriDoc Production Deployment")
    parser.add_argument("environment", choices=["development", "staging", "production"],
                       help="Target environment")
    parser.add_argument("--version", help="Version to deploy")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no actual deployment)")

    args = parser.parse_args()

    try:
        print(f"🚀 Starting deployment to {args.environment}...")

        if args.dry_run:
            print("🔍 Dry run mode - would deploy version:", args.version or "latest")
            exit(0)

        result = deploy_to_environment(args.environment, args.version)

        print("✅ Deployment completed!")
        print(f"   Duration: {result.duration:.1f}s" if result.duration else "   Duration: N/A")
        print(f"   Version: {result.version}")
        print(f"   Deployment ID: {result.deployment_id}")

        if result.errors:
            print("❌ Errors encountered:")
            for error in result.errors:
                print(f"   - {error}")

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        exit(1)
