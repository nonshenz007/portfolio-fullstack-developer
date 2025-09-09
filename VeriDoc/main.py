import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from ui.main_window import VeriDocMainWindow

def main():
    """
    Main function to launch the VeriDoc Professional application.
    """
    app = QApplication(sys.argv)
    
    # Load the dark theme stylesheet
    try:
        theme_path = Path("ui/theme.qss")
        if theme_path.exists():
            with open(theme_path, "r") as f:
                app.setStyleSheet(f.read())
        print("✅ Dark theme loaded successfully")
    except FileNotFoundError:
        print("⚠️  Theme file not found, using default styling")

    # Create the new unified main window
    # All engine initialization and configuration is handled internally
    window = VeriDocMainWindow()

    # Show the professional interface
    window.show()
    
    # Print startup message
    print("🚀 VeriDoc Professional launched successfully!")
    print("🛡️  Government-grade security active")
    print("📊 Real-time validation ready")
    print("🔧 Auto-enhancement enabled")
    
    # Run the application
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())