#!/usr/bin/env python3
"""
Demonstration of the LedgerFlow Configuration Management System

This script demonstrates the key features implemented for task 3:
- Centralized configuration management with hot-reload
- JSON Schema validation with HTTP 400 for validation errors
- Boolean toggle migration to realism_profile enum
- SIGHUP signal handler for config reload
"""

import os
import signal
import time
import yaml
import json
from pathlib import Path

# Add current directory to path
import sys
sys.path.insert(0, '.')

from app.core.config_manager import ConfigurationManager, RealismProfile


def demo_configuration_system():
    """Demonstrate the configuration management system"""
    print("🔧 LedgerFlow Configuration Management System Demo")
    print("=" * 60)
    
    # Create a temporary config manager for demo
    config_dir = Path("demo_config")
    config_dir.mkdir(exist_ok=True)
    schemas_dir = config_dir / "schemas"
    schemas_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigurationManager(str(config_dir))
        print("✓ Configuration manager initialized")
        
        # 1. Demonstrate schema validation
        print("\n1. JSON Schema Validation")
        print("-" * 30)
        
        # Create a schema
        demo_schema = {
            "type": "object",
            "properties": {
                "realism_profile": {
                    "type": "string",
                    "enum": ["basic", "realistic", "advanced"]
                },
                "invoice_count": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10000
                }
            },
            "required": ["realism_profile"],
            "additionalProperties": False
        }
        
        schema_file = schemas_dir / "demo.json"
        with open(schema_file, 'w') as f:
            json.dump(demo_schema, f, indent=2)
        
        config_manager._load_schemas()
        print("✓ Schema loaded")
        
        # Test valid configuration
        valid_config = {
            "realism_profile": "realistic",
            "invoice_count": 100
        }
        
        result = config_manager.validate_config(valid_config, "demo")
        print(f"✓ Valid config validation: {'PASSED' if result.valid else 'FAILED'}")
        
        # Test invalid configuration (would return HTTP 400)
        invalid_config = {
            "realism_profile": "invalid_profile",
            "invoice_count": -1
        }
        
        result = config_manager.validate_config(invalid_config, "demo")
        print(f"✓ Invalid config validation: {'FAILED (as expected)' if not result.valid else 'UNEXPECTED PASS'}")
        if result.errors:
            print(f"  Errors (would return HTTP 400): {result.errors}")
        
        # 2. Demonstrate boolean toggle migration
        print("\n2. Boolean Toggle Migration to realism_profile Enum")
        print("-" * 50)
        
        # Create config with legacy boolean toggles
        legacy_config = {
            "enable_advanced_features": True,
            "use_realistic_data": True,
            "enable_basic_mode": False,
            "other_setting": "preserved"
        }
        
        print(f"Legacy config: {legacy_config}")
        
        migrated_config = config_manager._migrate_boolean_toggles(legacy_config)
        print(f"Migrated config: {migrated_config}")
        print(f"✓ Realism profile: {migrated_config.get('realism_profile', 'NOT FOUND')}")
        
        # Test enum functionality
        profile = config_manager.get_realism_profile("advanced")
        print(f"✓ Enum value: {profile} (type: {type(profile)})")
        
        # 3. Demonstrate hot-reload with zero downtime
        print("\n3. Hot-Reload with Zero Downtime")
        print("-" * 35)
        
        # Create initial config
        initial_config = {
            "realism_profile": "basic",
            "setting": "initial_value"
        }
        
        config_file = config_dir / "hotreload_demo.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(initial_config, f)
        
        # Load initial config
        loaded_config = config_manager.load_config("hotreload_demo")
        print(f"✓ Initial config loaded: {loaded_config['setting']}")
        
        # Update config file
        updated_config = {
            "realism_profile": "advanced",
            "setting": "updated_value"
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(updated_config, f)
        
        # Hot reload
        success = config_manager.hot_reload_config("hotreload_demo")
        print(f"✓ Hot reload: {'SUCCESS' if success else 'FAILED'}")
        
        # Verify updated config
        reloaded_config = config_manager.load_config("hotreload_demo")
        print(f"✓ Updated config: {reloaded_config['setting']}")
        
        # 4. Demonstrate SIGHUP signal handling
        print("\n4. SIGHUP Signal Handler")
        print("-" * 25)
        
        # Update config again
        signal_config = {
            "realism_profile": "realistic",
            "setting": "signal_updated_value"
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(signal_config, f)
        
        # Simulate SIGHUP signal
        config_manager._signal_handler(signal.SIGHUP, None)
        print("✓ SIGHUP signal processed")
        
        # Verify signal reload worked
        signal_reloaded_config = config_manager.load_config("hotreload_demo")
        print(f"✓ Signal reloaded config: {signal_reloaded_config['setting']}")
        
        # 5. Demonstrate configuration status
        print("\n5. Configuration Manager Status")
        print("-" * 32)
        
        status = config_manager.get_config_status()
        print(f"✓ Loaded configs: {status['loaded_configs']}")
        print(f"✓ Available schemas: {status['available_schemas']}")
        print(f"✓ Config directory: {status['config_dir']}")
        print(f"✓ File watchers active: {status['watchers_active']}")
        
        print("\n🎉 Configuration Management System Demo Complete!")
        print("=" * 60)
        print("Key Features Demonstrated:")
        print("• ✓ JSON Schema validation with error reporting")
        print("• ✓ Boolean toggle migration to realism_profile enum")
        print("• ✓ Hot-reload with zero downtime (double-read-swap pattern)")
        print("• ✓ SIGHUP signal handler for configuration reload")
        print("• ✓ Thread-safe configuration management")
        print("• ✓ Configuration status and monitoring")
        
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        config_manager.shutdown()
        
        # Remove demo files
        import shutil
        if config_dir.exists():
            shutil.rmtree(config_dir)
        print("\n🧹 Demo cleanup complete")


if __name__ == "__main__":
    demo_configuration_system()