#!/usr/bin/env python3
"""
Quick check script to verify basic Flask app functionality.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import Flask first
    from flask import Flask
    
    # Import from the root app.py file
    import sys
    import os
    # Add the parent directory to sys.path to import app.py
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Import the Flask app from app.py (not the app package)
    import importlib.util
    app_spec = importlib.util.spec_from_file_location("app_module", os.path.join(parent_dir, "app.py"))
    app_module = importlib.util.module_from_spec(app_spec)
    app_spec.loader.exec_module(app_module)
    app = getattr(app_module, 'app', None)
    
    if app is None:
        raise AttributeError("Flask app not found in app module")
    
    print("✓ Flask app imports successfully")
    
    # Check if app is a Flask instance
    if not isinstance(app, Flask):
        raise TypeError(f"Expected Flask instance, got {type(app)}")
    
    print("✓ App is valid Flask instance")
    
    # Check basic configuration
    if not hasattr(app, 'config'):
        raise AttributeError("App missing config attribute")
    
    print("✓ App has configuration")
    
    # Test basic route registration
    with app.app_context():
        rules = list(app.url_map.iter_rules())
        if not rules:
            raise ValueError("No routes registered")
    
    print(f"✓ App has {len(rules)} routes registered")
    
    # Check templates directory exists
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"Templates directory not found: {template_dir}")
    
    print("✓ Templates directory exists")
    
    print("\n🎉 All basic checks passed!")
    
except Exception as e:
    print(f"❌ Quick check failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)