@echo off
echo Installing Python packages from requirements.txt...
echo Using Python 3.13.5
echo.

REM Check if Python is available
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not found or not in PATH
    echo Please ensure Python 3.13.5 is installed and added to PATH
    pause
    exit /b 1
)

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements using -r flag
echo.
echo Installing packages from requirements.txt...
echo Note: Some packages may be skipped due to Python 3.13.5 compatibility
python -m pip install -r requirements.txt

REM Try to install streamlit-webrtc separately with --no-deps if main install fails
echo.
echo Attempting to install streamlit-webrtc (may fail on Python 3.13.5)...
python -m pip install streamlit-webrtc --no-deps 2>nul
if %errorlevel% neq 0 (
    echo Warning: streamlit-webrtc could not be installed due to Python 3.13.5 compatibility
    echo The app will work without video/audio features
)

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: All packages installed successfully!
    echo You can now run: python app.py
) else (
    echo.
    echo ERROR: Some packages failed to install
    echo Please check the error messages above
)

echo.
echo Press any key to exit...
pause >nul