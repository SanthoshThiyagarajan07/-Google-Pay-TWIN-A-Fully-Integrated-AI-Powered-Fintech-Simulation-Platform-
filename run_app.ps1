# PowerShell script to install dependencies and run Google Pay TWIN app
Write-Host "Installing dependencies and running Google Pay TWIN app..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found in system PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://python.org or Microsoft Store" -ForegroundColor Yellow
    Write-Host "Make sure to add Python to PATH during installation." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing/updating dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "Checking if streamlit-webrtc is installed..." -ForegroundColor Yellow
try {
    python -c "import streamlit_webrtc; print('streamlit-webrtc is installed successfully')"
} catch {
    Write-Host "Installing streamlit-webrtc specifically..." -ForegroundColor Yellow
    python -m pip install streamlit-webrtc>=0.45.0
}

Write-Host ""
Write-Host "Checking if all required modules are available..." -ForegroundColor Yellow
try {
    python -c "import streamlit, pandas, numpy, plotly, sklearn, streamlit_option_menu; print('All core modules are available')"
} catch {
    Write-Host "Some modules are missing. Installing core dependencies..." -ForegroundColor Yellow
    python -m pip install streamlit pandas numpy plotly scikit-learn streamlit-option-menu
}

Write-Host ""
Write-Host "Starting Google Pay TWIN application..." -ForegroundColor Green
Write-Host "App will open in your default browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

python -m streamlit run app.py

Write-Host ""
Write-Host "Application stopped." -ForegroundColor Green
Read-Host "Press Enter to exit"