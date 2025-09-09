@echo off
REM Windows Launcher for Clara

REM Change directory to the script's location, then up one level, then into Core
cd /d %~dp0..\Core

REM Check for python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    pause
    exit /b
)

REM Launch the main application
python cortex.py
