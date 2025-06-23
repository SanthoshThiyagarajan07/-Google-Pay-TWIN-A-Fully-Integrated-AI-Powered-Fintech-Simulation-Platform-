#!/usr/bin/env python3
"""
Google Pay TWIN Application Launcher
Runs the app directly in Python with Streamlit streaming
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} detected.")
        print("⚠️  Python 3.7 or higher is required.")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected.")
    return True

def install_package(package_name):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ {package_name} installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}.")
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly',
        'scikit-learn',
        'streamlit-option-menu',
        'streamlit-webrtc',
        'Pillow',
        'matplotlib',
        'seaborn',
        'qrcode',
        'opencv-python',
        'SpeechRecognition',
        'pyttsx3',
        'calmap',
        'calendar'
    ]
    
    print("🔍 Checking dependencies...")
    
    # First try to install from requirements.txt if it exists
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        try:
            print("📋 Installing from requirements.txt...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Requirements installed from requirements.txt.")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to install from requirements.txt, installing packages individually...")
    
    # Check each package individually
    missing_packages = []
    for package in required_packages:
        try:
            # Handle special package names
            import_name = package
            if package == 'streamlit-option-menu':
                import_name = 'streamlit_option_menu'
            elif package == 'streamlit-webrtc':
                import_name = 'streamlit_webrtc'
            elif package == 'opencv-python':
                import_name = 'cv2'
            elif package == 'Pillow':
                import_name = 'PIL'
            elif package == 'scikit-learn':
                import_name = 'sklearn'
            elif package == 'SpeechRecognition':
                import_name = 'speech_recognition'
                
            importlib.import_module(import_name)
            print(f"✅ {package} is available.")
        except ImportError:
            print(f"❌ {package} not found.")
            missing_packages.append(package)
    
    # Install missing packages
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            install_package(package)
    else:
        print("✅ All dependencies are satisfied.")
    
    return True

def run_streamlit_app():
    """Run the Streamlit app"""
    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ app.py not found in current directory.")
        print("📁 Please make sure you're running this script from the project directory.")
        return False
    
    print("\n🚀 Starting Google Pay TWIN Application...")
    print("📱 The app will open in your default web browser.")
    print("🌐 Default URL: http://localhost:8501")
    print("\n⏹️  Press Ctrl+C to stop the application.\n")
    
    try:
        # Run streamlit with the app.py file
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run Streamlit app: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Application stopped by user.")
        return True
    
    return True

def main():
    """Main function to run the application"""
    print("🏦 Google Pay TWIN Application Launcher")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("❌ Failed to install dependencies.")
        input("\nPress Enter to exit...")
        return
    
    # Run the Streamlit app
    if not run_streamlit_app():
        print("❌ Failed to start the application.")
        input("\nPress Enter to exit...")
        return
    
    print("\n✅ Application finished successfully.")

if __name__ == "__main__":
    main()