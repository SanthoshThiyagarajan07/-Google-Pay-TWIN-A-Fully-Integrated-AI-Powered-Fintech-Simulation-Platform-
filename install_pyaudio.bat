@echo off
echo ========================================
echo PyAudio Installation Script for Windows
echo ========================================
echo.

echo Attempting PyAudio installation...
echo.

echo Method 1: Standard pip installation
python -m pip install PyAudio
if %errorlevel% equ 0 (
    echo SUCCESS: PyAudio installed successfully!
    goto :verify
)

echo.
echo Method 1 failed. Trying Method 2: Using pipwin...
python -m pip install pipwin
if %errorlevel% equ 0 (
    pipwin install pyaudio
    if %errorlevel% equ 0 (
        echo SUCCESS: PyAudio installed via pipwin!
        goto :verify
    )
)

echo.
echo Method 2 failed. Checking for conda...
conda --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Method 3: Using conda...
    conda install -c anaconda pyaudio -y
    if %errorlevel% equ 0 (
        echo SUCCESS: PyAudio installed via conda!
        goto :verify
    )
) else (
    echo Conda not found, skipping Method 3.
)

echo.
echo ========================================
echo ALL METHODS FAILED
echo ========================================
echo.
echo Please try one of these solutions:
echo 1. Install Microsoft Visual C++ Build Tools:
echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo.
echo 2. Use Anaconda/Miniconda and run:
echo    conda install pyaudio
echo.
echo 3. Comment out PyAudio in requirements.txt to disable voice features
echo.
echo See PYAUDIO_INSTALL_GUIDE.md for detailed instructions.
goto :end

:verify
echo.
echo Verifying PyAudio installation...
python -c "import pyaudio; print('PyAudio verification: SUCCESS')" 2>nul
if %errorlevel% equ 0 (
    echo PyAudio is working correctly!
) else (
    echo WARNING: PyAudio installed but verification failed.
)

:end
echo.
echo Press any key to exit...
pause >nul