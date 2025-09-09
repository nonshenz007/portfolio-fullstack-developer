import sys
import pytest
from PySide6.QtWidgets import QApplication
from ui.main_window_pyside import MainWindow

@pytest.fixture
def app(qtbot):
    """Create a QApplication instance."""
    test_app = QApplication.instance() or QApplication(sys.argv)
    yield test_app

def test_app_launch(app, qtbot):
    """Test if the main application window launches."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    assert window.isVisible()
    assert window.windowTitle() == "VeriDoc"
