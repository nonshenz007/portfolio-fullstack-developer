#!/usr/bin/env python3
"""
VeriDoc Professional Launcher
Quick launcher for the new unified, visually stunning UI.
"""

import os
import sys
from pathlib import Path

def main():
    """Launch VeriDoc Professional with proper setup."""
    
    print("🚀 VeriDoc Professional Launcher")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if virtual environment exists
    venv_paths = ['venv', '.venv', 'venv_new']
    venv_found = None
    
    for venv_path in venv_paths:
        if Path(venv_path).exists():
            venv_found = venv_path
            break
    
    if venv_found:
        print(f"✅ Found virtual environment: {venv_found}")
        
        # Try to activate and launch
        if sys.platform == "win32":
            activate_script = Path(venv_found) / "Scripts" / "activate.bat"
            python_exe = Path(venv_found) / "Scripts" / "python.exe"
        else:
            activate_script = Path(venv_found) / "bin" / "activate"
            python_exe = Path(venv_found) / "bin" / "python"
        
        if python_exe.exists():
            print("🔧 Launching VeriDoc Professional...")
            print("🛡️  Government-grade security enabled")
            print("📊 Real-time ICAO validation active")
            print("🎨 Modern professional interface loading...")
            print()
            
            # Launch the application
            os.system(f'"{python_exe}" main.py')
        else:
            print(f"❌ Python executable not found in {venv_found}")
            print("💡 Try: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
    else:
        print("⚠️  No virtual environment found")
        print("💡 Creating virtual environment...")
        
        # Try to create venv and install requirements
        os.system("python3 -m venv venv")
        os.system("source venv/bin/activate && pip install -r requirements.txt")
        
        print("✅ Virtual environment created")
        print("🚀 Launching VeriDoc Professional...")
        os.system("source venv/bin/activate && python main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 VeriDoc Professional closed")
    except Exception as e:
        print(f"\n❌ Launch error: {e}")
        print("💡 Try running: python main.py")
