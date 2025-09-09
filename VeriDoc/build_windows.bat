@echo off
REM VeriDoc - Windows Build Script

echo ========================================
echo VeriDoc - Windows Build
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Download models if not present
if not exist "models\face_detection_yunet_2023mar.onnx" (
    echo Downloading AI models...
    python tools\fetch_models.py
)

REM Build executable
echo Building executable...
pyinstaller --noconfirm --windowed --onefile ^
    --name "VeriDoc" ^
    --distpath ".dist" ^
    --add-data "models;models" ^
    --add-data "config;config" ^
    --add-data "ui;ui" ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    main.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo Executable: .dist\VeriDoc.exe
echo.
pause