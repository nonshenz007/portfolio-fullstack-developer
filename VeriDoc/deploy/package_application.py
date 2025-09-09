"""
Application Packaging and Deployment Script

Comprehensive script for packaging VeriDoc Universal for deployment
including dependency management, resource optimization, and distribution preparation.
"""

import os
import sys
import shutil
import subprocess
import json
import zipfile
import tarfile
from pathlib import Path
from typing import List, Dict, Any
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ApplicationPackager:
    """
    Comprehensive application packager for VeriDoc Universal.
    
    Handles dependency management, resource optimization, and
    distribution preparation for various deployment targets.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize the packager.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
        # Ensure directories exist
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized packager for project: {self.project_root}")
    
    def clean_build_directories(self):
        """Clean build and distribution directories."""
        logger.info("Cleaning build directories...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        logger.info("✓ Build directories cleaned")
    
    def validate_dependencies(self) -> bool:
        """
        Validate that all required dependencies are available.
        
        Returns:
            True if all dependencies are valid, False otherwise
        """
        logger.info("Validating dependencies...")
        
        required_files = [
            "requirements.txt",
            "main_integrated.py",
            "core/__init__.py",
            "ai/__init__.py",
            "validation/__init__.py",
            "autofix/__init__.py",
            "export/__init__.py",
            "ui/__init__.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False
        
        # Check Python dependencies
        try:
            import cv2
            import numpy
            import PyQt5
            logger.info("✓ Core dependencies available")
        except ImportError as e:
            logger.error(f"Missing Python dependency: {e}")
            return False
        
        logger.info("✓ All dependencies validated")
        return True
    
    def optimize_resources(self):
        """Optimize resources for deployment."""
        logger.info("Optimizing resources...")
        
        # Create optimized resource directory
        resources_dir = self.build_dir / "resources"
        resources_dir.mkdir(exist_ok=True)
        
        # Copy and optimize configuration files
        config_source = self.project_root / "config"
        config_dest = resources_dir / "config"
        if config_source.exists():
            shutil.copytree(config_source, config_dest)
            logger.info("✓ Configuration files copied")
        
        # Copy models directory (if exists)
        models_source = self.project_root / "models"
        models_dest = resources_dir / "models"
        if models_source.exists():
            shutil.copytree(models_source, models_dest)
            logger.info("✓ Model files copied")
        
        # Create logs directory
        logs_dest = resources_dir / "logs"
        logs_dest.mkdir(exist_ok=True)
        
        # Copy UI resources
        ui_source = self.project_root / "ui"
        ui_dest = resources_dir / "ui"
        if ui_source.exists():
            shutil.copytree(ui_source, ui_dest)
            logger.info("✓ UI resources copied")
        
        logger.info("✓ Resources optimized")
    
    def create_application_bundle(self, bundle_type: str = "standard") -> str:
        """
        Create application bundle for deployment.
        
        Args:
            bundle_type: Type of bundle ("standard", "minimal", "government")
            
        Returns:
            Path to created bundle
        """
        logger.info(f"Creating {bundle_type} application bundle...")
        
        bundle_dir = self.build_dir / f"veridoc_universal_{bundle_type}"
        bundle_dir.mkdir(exist_ok=True)
        
        # Copy core application files
        core_files = [
            "main_integrated.py",
            "core/",
            "ai/",
            "validation/",
            "autofix/",
            "export/",
            "utils/",
            "rules/",
            "quality/",
            "cli/"
        ]
        
        for file_path in core_files:
            source = self.project_root / file_path
            dest = bundle_dir / file_path
            
            if source.is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
            elif source.is_dir():
                shutil.copytree(source, dest, dirs_exist_ok=True)
        
        # Copy UI files based on bundle type
        if bundle_type in ["standard", "government"]:
            ui_source = self.project_root / "ui"
            ui_dest = bundle_dir / "ui"
            if ui_source.exists():
                shutil.copytree(ui_source, ui_dest)
        
        # Copy configuration
        config_source = self.project_root / "config"
        config_dest = bundle_dir / "config"
        if config_source.exists():
            shutil.copytree(config_source, config_dest)
        
        # Create requirements file for bundle
        self._create_bundle_requirements(bundle_dir, bundle_type)
        
        # Create startup scripts
        self._create_startup_scripts(bundle_dir, bundle_type)
        
        # Create documentation
        self._create_bundle_documentation(bundle_dir, bundle_type)
        
        logger.info(f"✓ {bundle_type} bundle created at: {bundle_dir}")
        return str(bundle_dir)
    
    def _create_bundle_requirements(self, bundle_dir: Path, bundle_type: str):
        """Create requirements.txt for the bundle."""
        requirements_file = bundle_dir / "requirements.txt"
        
        base_requirements = [
            "opencv-python>=4.8.0",
            "numpy>=1.21.0",
            "Pillow>=9.0.0",
            "PyQt5>=5.15.0",
            "psutil>=5.8.0",
            "ultralytics>=8.0.0"
        ]
        
        if bundle_type == "government":
            # Government bundle - minimal dependencies
            requirements = base_requirements[:4]  # Only core dependencies
        elif bundle_type == "minimal":
            # Minimal bundle - no UI
            requirements = [req for req in base_requirements if "PyQt5" not in req]
        else:
            # Standard bundle - all dependencies
            requirements = base_requirements + [
                "mediapipe>=0.10.0",
                "scikit-image>=0.19.0",
                "matplotlib>=3.5.0"
            ]
        
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        logger.info(f"✓ Requirements file created for {bundle_type} bundle")
    
    def _create_startup_scripts(self, bundle_dir: Path, bundle_type: str):
        """Create startup scripts for different platforms."""
        
        # Windows batch script
        windows_script = bundle_dir / "start_veridoc.bat"
        with open(windows_script, 'w') as f:
            f.write("""@echo off
echo Starting VeriDoc Universal...
python main_integrated.py %*
if errorlevel 1 (
    echo Error occurred. Press any key to exit.
    pause >nul
)
""")
        
        # Linux/Mac shell script
        unix_script = bundle_dir / "start_veridoc.sh"
        with open(unix_script, 'w') as f:
            f.write("""#!/bin/bash
echo "Starting VeriDoc Universal..."
python3 main_integrated.py "$@"
""")
        
        # Make shell script executable
        os.chmod(unix_script, 0o755)
        
        # Python launcher script
        launcher_script = bundle_dir / "launch.py"
        with open(launcher_script, 'w') as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
VeriDoc Universal Launcher
\"\"\"
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main application
from main_integrated import main

if __name__ == '__main__':
    sys.exit(main())
""")
        
        logger.info("✓ Startup scripts created")
    
    def _create_bundle_documentation(self, bundle_dir: Path, bundle_type: str):
        """Create documentation for the bundle."""
        docs_dir = bundle_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # README file
        readme_file = docs_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(f"""# VeriDoc Universal - {bundle_type.title()} Bundle

## Overview
VeriDoc Universal is an AI-powered photo verification system that validates
passport and visa photos against ICAO standards.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   - GUI mode: `python main_integrated.py`
   - CLI mode: `python main_integrated.py <image_path>`

## Usage

### GUI Mode
Launch the application without arguments to start the graphical interface:
```
python main_integrated.py
```

### CLI Mode
Process a single image:
```
python main_integrated.py image.jpg --format ICS-UAE
```

Process a batch of images:
```
python main_integrated.py /path/to/images --batch --auto-fix
```

### Available Formats
- ICS-UAE: UAE Immigration and Checkpoints Authority
- US-Visa: United States Visa Application
- Schengen-Visa: European Schengen Visa
- Base-ICAO: Standard ICAO Photo Requirements

## Features
- AI-powered face detection and analysis
- ICAO compliance validation
- Intelligent auto-correction
- Batch processing capabilities
- Comprehensive reporting
- Offline operation
- Security compliance

## Support
For technical support and documentation, please refer to the user manual
or contact the development team.

## Version
Bundle Type: {bundle_type.title()}
Version: 2.0.0
Build Date: {self._get_build_date()}
""")
        
        # Installation guide
        install_guide = docs_dir / "INSTALLATION.md"
        with open(install_guide, 'w') as f:
            f.write("""# Installation Guide

## System Requirements
- Operating System: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- Python: 3.8 or higher
- RAM: 4GB minimum, 8GB recommended
- Storage: 2GB free space
- Graphics: OpenGL 2.1 support

## Step-by-Step Installation

### 1. Python Installation
Ensure Python 3.8+ is installed on your system.

### 2. Dependency Installation
```bash
pip install -r requirements.txt
```

### 3. Model Download
The application will automatically download required AI models on first run.

### 4. Configuration
Default configuration files are included. Customize as needed for your environment.

### 5. Testing
Run a test to verify installation:
```bash
python main_integrated.py --status
```

## Troubleshooting
- If GUI doesn't start, ensure PyQt5 is properly installed
- For model download issues, check internet connectivity
- For performance issues, ensure adequate system resources
""")
        
        logger.info("✓ Documentation created")
    
    def _get_build_date(self) -> str:
        """Get current build date."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_distribution_packages(self, bundle_path: str) -> List[str]:
        """
        Create distribution packages from bundle.
        
        Args:
            bundle_path: Path to application bundle
            
        Returns:
            List of created package paths
        """
        logger.info("Creating distribution packages...")
        
        bundle_dir = Path(bundle_path)
        bundle_name = bundle_dir.name
        
        packages = []
        
        # Create ZIP package
        zip_path = self.dist_dir / f"{bundle_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in bundle_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(bundle_dir.parent)
                    zipf.write(file_path, arcname)
        
        packages.append(str(zip_path))
        logger.info(f"✓ ZIP package created: {zip_path}")
        
        # Create TAR.GZ package (for Unix systems)
        tar_path = self.dist_dir / f"{bundle_name}.tar.gz"
        with tarfile.open(tar_path, 'w:gz') as tarf:
            tarf.add(bundle_dir, arcname=bundle_name)
        
        packages.append(str(tar_path))
        logger.info(f"✓ TAR.GZ package created: {tar_path}")
        
        return packages
    
    def create_installer_scripts(self, bundle_path: str):
        """Create installer scripts for the application."""
        logger.info("Creating installer scripts...")
        
        bundle_dir = Path(bundle_path)
        
        # Windows installer script
        windows_installer = self.dist_dir / "install_windows.bat"
        with open(windows_installer, 'w') as f:
            f.write("""@echo off
echo VeriDoc Universal Installer
echo ===========================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Installation complete!
echo Run 'start_veridoc.bat' to launch the application
pause
""")
        
        # Unix installer script
        unix_installer = self.dist_dir / "install_unix.sh"
        with open(unix_installer, 'w') as f:
            f.write("""#!/bin/bash
echo "VeriDoc Universal Installer"
echo "==========================="

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using your system package manager"
    exit 1
fi

echo "Installing dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "Making scripts executable..."
chmod +x start_veridoc.sh

echo "Installation complete!"
echo "Run './start_veridoc.sh' to launch the application"
""")
        
        # Make Unix installer executable
        os.chmod(unix_installer, 0o755)
        
        logger.info("✓ Installer scripts created")
    
    def generate_deployment_report(self, packages: List[str]) -> str:
        """
        Generate deployment report.
        
        Args:
            packages: List of created package paths
            
        Returns:
            Path to deployment report
        """
        logger.info("Generating deployment report...")
        
        report_path = self.dist_dir / "deployment_report.json"
        
        report_data = {
            "build_info": {
                "timestamp": self._get_build_date(),
                "project_root": str(self.project_root),
                "build_directory": str(self.build_dir),
                "distribution_directory": str(self.dist_dir)
            },
            "packages": [
                {
                    "path": pkg,
                    "size_mb": round(Path(pkg).stat().st_size / (1024 * 1024), 2),
                    "type": Path(pkg).suffix[1:]
                }
                for pkg in packages
            ],
            "validation": {
                "dependencies_validated": True,
                "resources_optimized": True,
                "documentation_included": True,
                "startup_scripts_created": True
            },
            "deployment_notes": [
                "All packages include complete application bundle",
                "Dependencies must be installed separately",
                "AI models will be downloaded on first run",
                "Offline operation supported after initial setup"
            ]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"✓ Deployment report created: {report_path}")
        return str(report_path)
    
    def package_complete_application(self, bundle_types: List[str] = None) -> Dict[str, Any]:
        """
        Complete application packaging workflow.
        
        Args:
            bundle_types: List of bundle types to create
            
        Returns:
            Packaging results summary
        """
        if bundle_types is None:
            bundle_types = ["standard", "minimal", "government"]
        
        logger.info("Starting complete application packaging...")
        
        # Step 1: Clean and validate
        self.clean_build_directories()
        if not self.validate_dependencies():
            raise RuntimeError("Dependency validation failed")
        
        # Step 2: Optimize resources
        self.optimize_resources()
        
        # Step 3: Create bundles and packages
        results = {
            "bundles": {},
            "packages": [],
            "installers_created": True,
            "deployment_report": None
        }
        
        for bundle_type in bundle_types:
            logger.info(f"Processing {bundle_type} bundle...")
            
            # Create bundle
            bundle_path = self.create_application_bundle(bundle_type)
            results["bundles"][bundle_type] = bundle_path
            
            # Create distribution packages
            packages = self.create_distribution_packages(bundle_path)
            results["packages"].extend(packages)
            
            # Create installer scripts
            self.create_installer_scripts(bundle_path)
        
        # Step 4: Generate deployment report
        results["deployment_report"] = self.generate_deployment_report(results["packages"])
        
        logger.info("✓ Complete application packaging finished")
        return results


def main():
    """Main entry point for packaging script."""
    parser = argparse.ArgumentParser(description="VeriDoc Universal Application Packager")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--bundle-types", nargs="+", 
                       choices=["standard", "minimal", "government"],
                       default=["standard", "minimal", "government"],
                       help="Bundle types to create")
    parser.add_argument("--clean-only", action="store_true", help="Only clean build directories")
    parser.add_argument("--validate-only", action="store_true", help="Only validate dependencies")
    
    args = parser.parse_args()
    
    try:
        packager = ApplicationPackager(args.project_root)
        
        if args.clean_only:
            packager.clean_build_directories()
            logger.info("✓ Clean completed")
            return 0
        
        if args.validate_only:
            if packager.validate_dependencies():
                logger.info("✓ Validation passed")
                return 0
            else:
                logger.error("✗ Validation failed")
                return 1
        
        # Full packaging
        results = packager.package_complete_application(args.bundle_types)
        
        # Print summary
        print("\n" + "="*50)
        print("PACKAGING SUMMARY")
        print("="*50)
        print(f"Bundles created: {len(results['bundles'])}")
        for bundle_type, path in results['bundles'].items():
            print(f"  - {bundle_type}: {path}")
        
        print(f"\nPackages created: {len(results['packages'])}")
        for package in results['packages']:
            size_mb = Path(package).stat().st_size / (1024 * 1024)
            print(f"  - {Path(package).name}: {size_mb:.1f} MB")
        
        print(f"\nDeployment report: {results['deployment_report']}")
        print("\n✓ Packaging completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Packaging failed: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())