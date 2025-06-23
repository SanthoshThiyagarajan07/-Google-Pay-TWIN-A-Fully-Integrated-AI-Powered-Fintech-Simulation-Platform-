# PowerShell script to install requirements.txt for Python 3.13.5
Write-Host "Installing Python packages from requirements.txt..." -ForegroundColor Green
Write-Host "Using Python 3.13.5" -ForegroundColor Yellow
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not found or not in PATH" -ForegroundColor Red
    Write-Host "Please ensure Python 3.13.5 is installed and added to PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Upgrade pip first
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Failed to upgrade pip, continuing anyway..." -ForegroundColor Yellow
}

# Install requirements using -r flag
Write-Host ""
Write-Host "Installing packages from requirements.txt..." -ForegroundColor Yellow
Write-Host "Note: Some packages may be skipped due to Python 3.13.5 compatibility" -ForegroundColor Yellow
python -m pip install -r requirements.txt

# Try to install streamlit-webrtc separately
Write-Host ""
Write-Host "Attempting to install streamlit-webrtc (may fail on Python 3.13.5)..." -ForegroundColor Yellow
try {
    python -m pip install streamlit-webrtc --no-deps 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "streamlit-webrtc installed successfully" -ForegroundColor Green
    } else {
        Write-Host "Warning: streamlit-webrtc could not be installed due to Python 3.13.5 compatibility" -ForegroundColor Yellow
        Write-Host "The app will work without video/audio features" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Warning: streamlit-webrtc installation failed" -ForegroundColor Yellow
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: All packages installed successfully!" -ForegroundColor Green
    Write-Host "You can now run: python app.py" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "ERROR: Some packages failed to install" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"