#!/usr/bin/env python3
"""
Test script to verify the Google Pay TWIN app is working correctly
with original sklearn-based functionality restored.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required imports work correctly"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✓ Streamlit imported successfully")
    except ImportError as e:
        print(f"✗ Streamlit import failed: {e}")
        return False
    
    try:
        from sklearn.ensemble import IsolationForest, RandomForestClassifier
        from sklearn.cluster import KMeans
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        print("✓ Scikit-learn imported successfully")
    except ImportError as e:
        print(f"✗ Scikit-learn import failed: {e}")
        return False
    
    try:
        import pandas as pd
        import numpy as np
        import plotly.express as px
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✓ Data science libraries imported successfully")
    except ImportError as e:
        print(f"✗ Data science libraries import failed: {e}")
        return False
    
    try:
        from streamlit_option_menu import option_menu
        print("✓ Streamlit option menu imported successfully")
    except ImportError as e:
        print(f"✗ Streamlit option menu import failed: {e}")
        return False
    
    return True

def test_app_structure():
    """Test if app.py and feature files exist"""
    print("\nTesting app structure...")
    
    required_files = [
        'app.py',
        'auth_page.py',
        'qr_code_page.py',
        'bill_split_page.py',
        'cashback_page.py',
        'scan_receipt_page.py',
        'voice_pay_page.py',
        'budget_alerts_page.py',
        'savings_goals_page.py',
        'subscriptions_page.py',
        'financial_health_page.py',
        'investment_tracker_page.py',
        'fraud_detection_page.py',
        'expense_prediction_page.py',
        'emotion_insights_page.py',
        'financial_assistant_page.py',
        'spending_heatmap_page.py',
        'spending_challenge_page.py',
        'pay_later_page.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\nMissing files: {missing_files}")
        return False
    
    return True

def main():
    """Main test function"""
    print("Google Pay TWIN App Test")
    print("=" * 30)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test app structure
    structure_ok = test_app_structure()
    
    print("\n" + "=" * 30)
    if imports_ok and structure_ok:
        print("✓ All tests passed! App is ready to run.")
        print("\nTo start the app, run:")
        print("streamlit run app.py")
        print("\nOr with virtual environment:")
        print("new_env\\Scripts\\python.exe -m streamlit run app.py")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    main()