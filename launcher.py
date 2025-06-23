#!/usr/bin/env python3
"""
Google Pay TWIN App Launcher
This script checks dependencies and launches the Streamlit app.
"""

import sys
import subprocess
import importlib
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = {
        'streamlit': 'streamlit>=1.28.0',
        'pandas': 'pandas>=1.5.0',
        'numpy': 'numpy>=1.21.0',
        'plotly': 'plotly>=5.0.0',
        'sklearn': 'scikit-learn>=1.1.0',
        'streamlit_option_menu': 'streamlit-option-menu>=0.3.6',
        'streamlit_webrtc': 'streamlit-webrtc>=0.45.0',
        'PIL': 'Pillow>=9.0.0',
        'matplotlib': 'matplotlib>=3.5.0',
        'seaborn': 'seaborn>=0.11.0'
    }
    
    missing_packages = []
    
    print("\nChecking dependencies...")
    for module, package in required_packages.items():
        try:
            importlib.import_module(module)
            print(f"✓ {module} is available")
        except ImportError:
            print(f"✗ {module} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nInstalling {len(missing_packages)} missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            if not install_package(package):
                print(f"Failed to install {package}")
                return False
        print("✓ All dependencies installed successfully")
    else:
        print("✓ All dependencies are already installed")
    
    return True

def run_streamlit_app():
    """Run the Streamlit app"""
    try:
        print("\n" + "="*50)
        print("Starting Google Pay TWIN Application...")
        print("App will open in your browser at http://localhost:8501")
        print("Press Ctrl+C to stop the application")
        print("="*50 + "\n")
        
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user.")
    except Exception as e:
        print(f"Error running the application: {e}")
        return False
    return True

def main():
    """Main function"""
    print("Google Pay TWIN App Launcher")
    print("="*30)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("Error: app.py not found in current directory")
        print("Please run this script from the Google Pay TWIN project directory")
        input("Press Enter to exit...")
        return
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("Failed to install dependencies")
        input("Press Enter to exit...")
        return
    
    # Run the app
    run_streamlit_app()
    
    print("\nThank you for using Google Pay TWIN!")

if __name__ == "__main__":
    main()