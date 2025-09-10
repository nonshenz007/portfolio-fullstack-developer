@echo off
echo Starting LedgerFlow Invoice Generator...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Try to run the launcher script first (best for Windows)
if exist run_app.py (
    echo Using Windows-optimized launcher...
    python run_app.py
) else (
    echo Using standard launcher...
    python main.py
)

if %errorlevel% neq 0 (
    echo.
    echo Application encountered an error.
    echo Check the console output above for details.
    pause
)

echo.
echo Application finished.
pause 