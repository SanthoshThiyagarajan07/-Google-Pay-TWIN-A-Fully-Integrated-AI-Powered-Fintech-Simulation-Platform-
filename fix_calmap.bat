@echo off
echo ========================================
echo Calmap Installation Fix Script
echo ========================================
echo.
echo This script will attempt to fix calmap installation issues.
echo Please wait while we check and fix the installation...
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Run the fix script
echo Running calmap fix script...
python fix_calmap.py

echo.
echo ========================================
echo Fix script completed!
echo ========================================
echo.
echo You can now run the main application:
echo   python app.py
echo.
echo Or use the launcher:
echo   python launcher.py
echo.
pause