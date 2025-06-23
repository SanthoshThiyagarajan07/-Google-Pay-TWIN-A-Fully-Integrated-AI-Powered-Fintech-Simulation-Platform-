@echo off
echo Installing dependencies and running Google Pay TWIN app...
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in system PATH.
    echo Please install Python from https://python.org or Microsoft Store
    echo Make sure to add Python to PATH during installation.
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

echo.
echo Installing/updating dependencies from requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Checking if streamlit-webrtc is installed...
python -c "import streamlit_webrtc; print('streamlit-webrtc is installed successfully')"
if errorlevel 1 (
    echo Installing streamlit-webrtc specifically...
    python -m pip install streamlit-webrtc>=0.45.0
)

echo.
echo Checking if all required modules are available...
python -c "import streamlit, pandas, numpy, plotly, sklearn, streamlit_option_menu; print('All core modules are available')"
if errorlevel 1 (
    echo Some modules are missing. Installing core dependencies...
    python -m pip install streamlit pandas numpy plotly scikit-learn streamlit-option-menu
)

echo.
echo Starting Google Pay TWIN application...
echo App will open in your default browser at http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

python -m streamlit run app.py

echo.
echo Application stopped.
pause