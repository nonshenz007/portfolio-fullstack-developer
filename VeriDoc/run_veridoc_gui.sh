#!/bin/bash
# VeriDoc GUI Launcher with Qt Fix
# This script properly sets up the Qt environment and launches VeriDoc

echo "🚀 VeriDoc Processing Pipeline (PPP) Launcher"
echo "=============================================="

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Set up Qt environment properly
echo "🎨 Setting up Qt environment..."
export QT_QPA_PLATFORM_PLUGIN_PATH="$(pwd)/venv/lib/python3.13/site-packages/PyQt5/Qt5/plugins"
export QT_QPA_PLATFORM=cocoa
export DYLD_LIBRARY_PATH="$(pwd)/venv/lib/python3.13/site-packages/PyQt5/Qt5/lib:$DYLD_LIBRARY_PATH"

# Check if Qt plugins exist
if [ ! -f "venv/lib/python3.13/site-packages/PyQt5/Qt5/plugins/platforms/libqcocoa.dylib" ]; then
    echo "❌ Qt cocoa plugin not found. Reinstalling PyQt5..."
    pip uninstall PyQt5 -y
    pip install PyQt5
fi

echo "🛡️  Government-grade security enabled"
echo "📊 Real-time ICAO validation active"  
echo "🎨 Modern professional interface loading..."
echo ""

# Launch the application
echo "🚀 Launching VeriDoc Professional..."
python main.py

echo ""
echo "👋 VeriDoc session ended"
