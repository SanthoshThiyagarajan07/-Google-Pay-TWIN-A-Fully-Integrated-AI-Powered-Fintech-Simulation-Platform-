#!/usr/bin/env python3
"""
Test script to verify the Google Pay TWIN application works properly
after fixing the navigation conflicts.
"""

import sys
import os
import subprocess
import time

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from streamlit_option_menu import option_menu
        print("✅ streamlit_option_menu imported successfully")
    except ImportError as e:
        print(f"❌ streamlit_option_menu import failed: {e}")
        return False
    
    try:
        import pandas as pd
        import numpy as np
        print("✅ pandas and numpy imported successfully")
    except ImportError as e:
        print(f"❌ pandas/numpy import failed: {e}")
        return False
    
    return True

def test_page_modules():
    """Test if page modules can be imported"""
    print("\n🔍 Testing page module imports...")
    
    modules_to_test = [
        'auth_page',
        'qr_code_page', 
        'bill_split_page',
        'cashback_page',
        'voice_pay_page',
        'budget_alerts_page',
        'savings_goals_page',
        'subscriptions_page',
        'financial_health_page',
        'pay_later_page'
    ]
    
    success_count = 0
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
    
    print(f"\n📊 Module import results: {success_count}/{len(modules_to_test)} successful")
    return success_count == len(modules_to_test)

def test_app_structure():
    """Test if app.py has the correct structure"""
    print("\n🔍 Testing app.py structure...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key functions
        required_functions = [
            'def main():',
            'def show_main_app():',
            'def dashboard_page():',
            'def send_money_page():',
            'def add_money_page():'
        ]
        
        for func in required_functions:
            if func in content:
                print(f"✅ Found {func}")
            else:
                print(f"❌ Missing {func}")
                return False
        
        # Check for navigation conflicts (should not exist)
        if 'st.session_state.page =' in content:
            print("⚠️ Warning: Found old session state navigation - this may cause conflicts")
        
        return True
        
    except FileNotFoundError:
        print("❌ app.py not found")
        return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def run_syntax_check():
    """Run a syntax check on the main app file"""
    print("\n🔍 Running syntax check...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', 'app.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ app.py syntax is valid")
            return True
        else:
            print(f"❌ Syntax errors found: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Syntax check timed out")
        return False
    except Exception as e:
        print(f"❌ Error during syntax check: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Google Pay TWIN - Application Test Suite")
    print("=" * 50)
    
    # Change to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    print(f"📁 Working directory: {app_dir}")
    
    tests = [
        ("Import Test", test_imports),
        ("Page Modules Test", test_page_modules),
        ("App Structure Test", test_app_structure),
        ("Syntax Check", run_syntax_check)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work properly.")
        print("\n💡 To run the app, use one of these commands:")
        print("   • python app.py")
        print("   • python -m streamlit run app.py")
        print("   • .\\install_and_run.bat")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        print("\n💡 Try running: python -m pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)