@echo off
echo Missile Tracking System - Windows Installation
echo ===================================================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo Testing installation...
python test_system.py

echo.
echo Installation complete!
echo.
echo Quick start:
echo   python main.py              # Start with webcam
echo   python run.py --help        # See all options
echo.
pause