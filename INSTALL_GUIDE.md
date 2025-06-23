# Installation Guide - Google Pay TWIN

## Problem Solved: "You are attempting to install a package literally named 'requirements.txt'"

The error occurs when trying to install `requirements.txt` as a package name instead of using it as a file containing package names.

### ❌ Wrong Command:
```bash
pip install requirements.txt
```

### ✅ Correct Command:
```bash
pip install -r requirements.txt
```

The `-r` flag tells pip to read the package names from the requirements.txt file.

## Installation Methods for Python 3.13.5

### Method 1: Command Line (Recommended)
```bash
# Navigate to project directory
cd "c:\Users\HP\Desktop\project folder\scrrenshots\google pay replica"

# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
python -m pip install -r requirements.txt
```

### Method 2: Batch File (Windows)
Double-click `install_requirements.bat` or run:
```cmd
install_requirements.bat
```

### Method 3: PowerShell Script
Right-click `install_requirements.ps1` → "Run with PowerShell" or:
```powershell
.\install_requirements.ps1
```

### Method 4: Manual Installation
If the above methods fail, install packages individually:
```bash
python -m pip install streamlit>=1.28.0
python -m pip install pandas>=1.5.0
python -m pip install numpy>=1.21.0
python -m pip install plotly>=5.0.0
python -m pip install scikit-learn>=1.1.0
python -m pip install streamlit-option-menu>=0.3.6
python -m pip install streamlit-webrtc>=0.45.0
python -m pip install qrcode[pil]>=7.3.1
python -m pip install opencv-python>=4.6.0
python -m pip install pyttsx3>=2.90
python -m pip install SpeechRecognition>=3.8.1
# ... and so on for other packages
```

## Troubleshooting

### If Python is not found:
1. Ensure Python 3.13.5 is installed
2. Add Python to system PATH
3. Restart command prompt/PowerShell
4. Try `py` instead of `python`

### If PyAudio installation fails:
**PyAudio is required for voice recognition features.**

📋 **See detailed instructions**: [PYAUDIO_INSTALL_GUIDE.md](PYAUDIO_INSTALL_GUIDE.md)

**Quick fixes:**
- **Windows**: Install Microsoft Visual C++ Build Tools or use `conda install pyaudio`
- **macOS**: Run `brew install portaudio` first
- **Linux**: Install system dependencies (see guide for your distribution)

**Alternative**: Comment out PyAudio in requirements.txt to disable voice features

### If specific packages fail:
1. Try installing them individually
2. Use `--user` flag: `python -m pip install --user -r requirements.txt`
3. Update pip: `python -m pip install --upgrade pip`

### For permission errors:
1. Run as Administrator
2. Use virtual environment
3. Use `--user` flag

## Verification
After installation, verify by running:
```bash
python app.py
```

The app should start without import errors.

## Package List (58 total)
The requirements.txt includes:
- **Core**: streamlit, pandas, numpy, matplotlib, seaborn, plotly
- **UI**: streamlit-option-menu, streamlit-webrtc, streamlit-lottie
- **ML**: scikit-learn
- **Utilities**: qrcode, opencv-python, pyttsx3, SpeechRecognition
- **Security**: passlib, bcrypt, PyJWT, pyotp, cryptography
- **Payment**: stripe, razorpay, paypalrestsdk
- **Others**: requests, APScheduler, python-dotenv, psutil, etc.

---
**Note**: Always use the `-r` flag when installing from requirements.txt files!