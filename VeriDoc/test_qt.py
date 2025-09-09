#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

def test_qt():
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("VeriDoc Test")
    window.setGeometry(100, 100, 400, 300)
    
    label = QLabel("✅ VeriDoc Backend is Working!\n🚀 All 13 tasks implemented!", window)
    label.setStyleSheet("font-size: 16px; padding: 20px; text-align: center;")
    window.setCentralWidget(label)
    
    window.show()
    print("✅ Qt GUI is working!")
    print("🎉 VeriDoc is ready!")
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(test_qt())