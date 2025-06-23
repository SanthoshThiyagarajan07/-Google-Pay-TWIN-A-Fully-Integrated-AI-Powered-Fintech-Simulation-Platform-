# Running Google Pay TWIN Without Virtual Environment

This guide explains how to run the Google Pay TWIN application directly using your system Python installation, without requiring virtual environments.

## 🚀 Quick Start Options

### Option 1: Using the Python Launcher (Recommended)
```bash
python launcher.py
```
This will automatically check dependencies, install missing packages, and launch the app.

### Option 2: Using Batch File (Windows)
```bash
install_and_run.bat
```
Double-click the batch file or run it from command prompt.

### Option 3: Using PowerShell
```powershell
.\run_app.ps1
```
Run the PowerShell script for a more detailed installation process.

### Option 4: Manual Installation
```bash
# Install dependencies
python -m pip install -r requirements.txt

# Run the app
python -m streamlit run app.py
```

## 📋 Prerequisites

### Python Installation
1. **Install Python 3.7 or higher** from:
   - [Official Python Website](https://python.org/downloads/)
   - Microsoft Store (search for "Python")

2. **During installation, make sure to:**
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"

3. **Verify installation:**
   ```bash
   python --version
   pip --version
   ```

### Fix "Python was not found" Error

If you get the error: `Python was not found; run without arguments to install from the Microsoft Store`

**Solution 1: Add Python to PATH**
1. Find your Python installation directory (usually `C:\Users\[Username]\AppData\Local\Programs\Python\Python3x`)
2. Add both Python directory and Scripts subdirectory to your PATH environment variable
3. Restart command prompt/PowerShell

**Solution 2: Use Python from Microsoft Store**
1. Type `python` in command prompt
2. It will open Microsoft Store
3. Install Python from there

**Solution 3: Disable App Execution Aliases**
1. Go to Settings > Apps > Advanced app settings > App execution aliases
2. Turn off "App Installer" for python.exe and python3.exe

## 🔧 Dependency Management

### Core Dependencies
The app requires these essential packages:
- `streamlit` - Web framework
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `plotly` - Interactive charts
- `scikit-learn` - Machine learning
- `streamlit-option-menu` - Navigation
- `streamlit-webrtc` - Video/audio features

### Installing Dependencies

**Automatic Installation:**
All launcher scripts will automatically install missing dependencies.

**Manual Installation:**
```bash
# Install all dependencies
python -m pip install -r requirements.txt

# Install specific missing packages
python -m pip install streamlit-webrtc streamlit-option-menu

# Upgrade pip if needed
python -m pip install --upgrade pip
```

### Fix "ModuleNotFoundError"

If you get errors like `ModuleNotFoundError: No module named 'streamlit_webrtc'`:

1. **Install the specific module:**
   ```bash
   python -m pip install streamlit-webrtc
   ```

2. **Reinstall all dependencies:**
   ```bash
   python -m pip install -r requirements.txt --force-reinstall
   ```

3. **Check if module is installed:**
   ```bash
   python -c "import streamlit_webrtc; print('Module found!')"
   ```

## 🎯 Running the Application

### Method 1: Python Launcher (Easiest)
```bash
python launcher.py
```
**Features:**
- ✅ Automatic dependency checking
- ✅ Automatic installation of missing packages
- ✅ Python version verification
- ✅ Error handling and user-friendly messages

### Method 2: Direct Streamlit
```bash
python -m streamlit run app.py
```
**Note:** Make sure all dependencies are installed first.

### Method 3: Batch File
```bash
install_and_run.bat
```
**Features:**
- ✅ Windows-optimized
- ✅ Automatic dependency installation
- ✅ Error checking

## 🌐 Accessing the Application

Once started, the app will be available at:
- **Local URL:** http://localhost:8501
- **Network URL:** http://[your-ip]:8501

The app will automatically open in your default web browser.

## 🛠️ Troubleshooting

### Common Issues and Solutions

**1. Python not found**
```
Solution: Install Python and add to PATH (see Prerequisites section)
```

**2. Module not found errors**
```bash
# Install missing module
python -m pip install [module-name]

# Or reinstall all dependencies
python -m pip install -r requirements.txt
```

**3. Permission errors during installation**
```bash
# Install with user flag
python -m pip install --user -r requirements.txt

# Or run as administrator
```

**4. Streamlit command not found**
```bash
# Use full module path
python -m streamlit run app.py
```

**5. Port already in use**
```bash
# Use different port
python -m streamlit run app.py --server.port 8502
```

### Getting Help

1. **Check Python installation:**
   ```bash
   python --version
   python -m pip --version
   ```

2. **Test basic imports:**
   ```bash
   python -c "import streamlit; print('Streamlit OK')"
   python -c "import pandas; print('Pandas OK')"
   ```

3. **Run the test script:**
   ```bash
   python test_app.py
   ```

## 📱 Application Features

Once running, you'll have access to 30+ features including:

### Core Features
- 💸 Send/Receive Money
- 💰 Add Money to Wallet
- 📱 QR Code Payments
- 🧾 Bill Splitting
- 🎁 Cashback System

### Advanced Features
- 🤖 AI Fraud Detection
- 📊 Expense Prediction
- 💡 Financial Health Score
- 🎯 Budget Alerts
- 💎 Savings Goals
- 📈 Investment Tracking
- 🗣️ Voice Payments
- 📄 Receipt Scanning

### Analytics & Insights
- 📊 Spending Analytics
- 🔥 Spending Heatmaps
- 😊 Emotion-based Insights
- 🏆 Spending Challenges
- 📅 Subscription Management

## 🔒 Security Features

- 🔐 User Authentication
- 📱 OTP Verification
- 🛡️ Fraud Detection
- 🔒 Secure Transactions
- 👤 User Session Management

## 💡 Tips for Best Experience

1. **Use latest Python version** (3.9+ recommended)
2. **Keep dependencies updated** regularly
3. **Use a stable internet connection** for real-time features
4. **Allow browser notifications** for alerts
5. **Use Chrome/Firefox** for best compatibility

---

**🎉 Enjoy using Google Pay TWIN!**

For issues or questions, check the troubleshooting section above or run the diagnostic scripts provided.