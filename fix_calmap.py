#!/usr/bin/env python3
"""
Calmap Installation Fix Script
This script attempts to fix calmap installation issues on Python 3.13
"""

import sys
import subprocess
import importlib
import os

def check_python_version():
    """Check Python version and warn about compatibility"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️ Warning: Python 3.13+ detected. Calmap may have compatibility issues.")
        return True
    return False

def uninstall_calmap():
    """Uninstall existing calmap installation"""
    print("🗑️ Uninstalling existing calmap...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "calmap", "-y"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Calmap uninstalled successfully.")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Calmap was not installed or uninstall failed.")
        return False

def install_calmap_methods():
    """Try different methods to install calmap"""
    methods = [
        # Method 1: Regular pip install
        ([sys.executable, "-m", "pip", "install", "calmap"], "Regular pip install"),
        
        # Method 2: Force reinstall
        ([sys.executable, "-m", "pip", "install", "--force-reinstall", "calmap"], "Force reinstall"),
        
        # Method 3: No cache
        ([sys.executable, "-m", "pip", "install", "--no-cache-dir", "calmap"], "No cache install"),
        
        # Method 4: Specific version
        ([sys.executable, "-m", "pip", "install", "calmap==0.0.11"], "Specific version install"),
        
        # Method 5: User install
        ([sys.executable, "-m", "pip", "install", "--user", "calmap"], "User install")
    ]
    
    for cmd, description in methods:
        print(f"\n🔄 Trying: {description}")
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {description} successful!")
            
            # Test import
            try:
                importlib.import_module('calmap')
                print("✅ Calmap import test successful!")
                return True
            except ImportError as e:
                print(f"❌ Import failed: {e}")
                continue
                
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed.")
            continue
    
    return False

def test_calmap_functionality():
    """Test basic calmap functionality"""
    print("\n🧪 Testing calmap functionality...")
    try:
        import calmap
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Create test data
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        values = np.random.rand(len(dates)) * 100
        test_series = pd.Series(values, index=dates)
        
        # Test yearplot function
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        calmap.yearplot(test_series, ax=ax)
        plt.close(fig)
        
        print("✅ Calmap functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Calmap functionality test failed: {e}")
        return False

def main():
    """Main function to fix calmap installation"""
    print("🔧 Calmap Installation Fix Script")
    print("=" * 40)
    
    # Check Python version
    is_python_313 = check_python_version()
    
    # Check if calmap is already working
    try:
        import calmap
        print("✅ Calmap is already installed and importable.")
        if test_calmap_functionality():
            print("\n🎉 Calmap is working perfectly! No fix needed.")
            return
        else:
            print("⚠️ Calmap imports but has functionality issues. Attempting fix...")
    except ImportError:
        print("❌ Calmap is not installed or not importable.")
    
    # Uninstall existing installation
    uninstall_calmap()
    
    # Try different installation methods
    print("\n📦 Attempting calmap installation...")
    if install_calmap_methods():
        print("\n🎉 Calmap installation successful!")
        
        # Test functionality
        if test_calmap_functionality():
            print("\n✅ All tests passed! Calmap is ready to use.")
        else:
            print("\n⚠️ Installation successful but functionality test failed.")
            print("   Calendar heatmap features may be limited.")
    else:
        print("\n❌ All installation methods failed.")
        if is_python_313:
            print("\n💡 This is likely due to Python 3.13 compatibility issues.")
            print("   The app will work without calmap, but calendar heatmap features will be disabled.")
            print("\n🔧 Recommended solutions:")
            print("   1. Use Python 3.11 or 3.12 for full compatibility")
            print("   2. Continue without calmap (other features will work)")
        else:
            print("\n💡 Try running this script with administrator privileges.")
            print("   Or check your internet connection and try again.")

if __name__ == "__main__":
    main()