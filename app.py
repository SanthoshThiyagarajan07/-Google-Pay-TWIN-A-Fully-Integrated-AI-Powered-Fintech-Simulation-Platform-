import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import hashlib
import time
import random
import string
import qrcode
# import cv2  # Removed due to Windows permission issues
# from pyzbar import pyzbar  # Removed due to DLL dependency issues on Windows Store Python
try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    Image = None
    ImageEnhance = None
    ImageFilter = None
    print("Warning: PIL not installed. Image processing features may not work.")
from qrcode.image.pil import PilImage
import io
import re
import requests
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None
    print("Warning: plotly not installed. Some visualization features may not work.")

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    print("Warning: pyttsx3 not installed. Text-to-speech features may not work.")

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    print("Warning: speech_recognition not installed. Voice recognition features may not work.")
try:
    import pytesseract
except ImportError:
    pytesseract = None
    print("Warning: pytesseract not installed. OCR features may not work.")
from PIL import Image
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
try:
    import calmap
except ImportError:
    calmap = None
    print("Warning: calmap not installed or incompatible with Python 3.13. Calendar heatmap features may not work.")
# Machine Learning imports
try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    IsolationForest = None
    RandomForestClassifier = None
    KMeans = None
    LinearRegression = None
    StandardScaler = None
    train_test_split = None
    accuracy_score = None
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. Some ML features may not work.")
from streamlit_option_menu import option_menu
try:
    from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
    WEBRTC_AVAILABLE = True
except ImportError:
    webrtc_streamer = None
    VideoTransformerBase = None
    WEBRTC_AVAILABLE = False
    print("Warning: streamlit-webrtc not installed. Video/audio features may not work.")
# from streamlit_extras.colored_header import colored_header  # Removed due to Streamlit compatibility issues
# from streamlit_extras.add_vertical_space import add_vertical_space  # Removed due to Streamlit compatibility issues
# from streamlit_extras.metric_cards import style_metric_cards  # Removed due to Streamlit compatibility issues
try:
    from streamlit_lottie import st_lottie
except ImportError:
    st_lottie = None
    print("Warning: streamlit-lottie not installed. Animation features may not work.")

try:
    from streamlit_calendar import calendar
except ImportError:
    calendar = None
    print("Warning: streamlit-calendar not installed. Calendar features may not work.")
# from streamlit_camera_input_live import camera_input_live  # Replaced with st.camera_input
# Import authentication module
from auth_page import show_auth_page, require_auth, logout_user, get_current_user_data
# Import page modules
from qr_code_page import qr_code_page
from bill_split_page import bill_split_page
from cashback_page import cashback_page
# from scan_receipt_page import scan_receipt_page  # Removed to prevent circular import
from voice_pay_page import voice_pay_page
from budget_alerts_page import budget_alerts_page
from savings_goals_page import savings_goals_page
from subscriptions_page import subscriptions_page
from financial_health_page import financial_health_page
from investment_tracker_page import investment_tracker_page
from fraud_detection_page import fraud_detection_page
from expense_prediction_page import expense_prediction_page
from emotion_insights_page import emotion_insights_page
from financial_assistant_page import financial_assistant_page
from spending_heatmap_page import spending_heatmap_page
from spending_challenge_page import spending_challenge_page
from pay_later_page import pay_later_page

# Import new enhanced modules
try:
    from payment_gateway import PaymentGateway
except ImportError:
    PaymentGateway = None
    print("Warning: payment_gateway module not available")

try:
    from security import SecurityManager
except ImportError:
    SecurityManager = None
    print("Warning: security module not available")

try:
    from advanced_fraud_detection import AdvancedFraudDetector
except ImportError:
    AdvancedFraudDetector = None
    print("Warning: advanced_fraud_detection module not available")

try:
    from ai_recommendations_page import ai_recommendations_page as ai_recommendations_page_func
    from ai_recommendations_page import AIRecommendationEngine
except ImportError:
    ai_recommendations_page_func = None
    AIRecommendationEngine = None
    print("Warning: ai_recommendations_page module not available")

try:
    from recurring_payments_page import recurring_payments_page
except ImportError:
    recurring_payments_page = None
    print("Warning: recurring_payments_page module not available")
# Removing TensorFlow imports as they're causing compatibility issues
# import tensorflow as tf
# from tensorflow.keras.models import Sequential, load_model
# from tensorflow.keras.layers import Dense, Dropout

# Set page configuration (only when running as main script)
try:
    st.set_page_config(
        page_title="Google Pay TWIN",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except st.errors.StreamlitAPIException:
    # Page config already set, ignore
    pass

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'otp' not in st.session_state:
    st.session_state.otp = None
if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False
if 'qr_data' not in st.session_state:
    st.session_state.qr_data = None
if 'bill_split' not in st.session_state:
    st.session_state.bill_split = {}
if 'cashback_points' not in st.session_state:
    st.session_state.cashback_points = 0
if 'voice_command' not in st.session_state:
    st.session_state.voice_command = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'budget_alerts' not in st.session_state:
    st.session_state.budget_alerts = {}
if 'savings_goals' not in st.session_state:
    st.session_state.savings_goals = {}
if 'subscriptions' not in st.session_state:
    st.session_state.subscriptions = {}
if 'financial_health_score' not in st.session_state:
    st.session_state.financial_health_score = 0
if 'pay_later_limit' not in st.session_state:
    st.session_state.pay_later_limit = 0
if 'spending_challenge' not in st.session_state:
    st.session_state.spending_challenge = {}

# Create data directories if they don't exist
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
user_data_file = os.path.join(data_dir, "users.json")
transaction_data_file = os.path.join(data_dir, "transactions.json")
bill_split_file = os.path.join(data_dir, "bill_splits.json")
cashback_file = os.path.join(data_dir, "cashbacks.json")
goals_file = os.path.join(data_dir, "savings_goals.json")
subscriptions_file = os.path.join(data_dir, "subscriptions.json")

# Initialize data files if they don't exist
def initialize_data_files():
    if not os.path.exists(user_data_file):
        with open(user_data_file, 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists(transaction_data_file):
        with open(transaction_data_file, 'w') as f:
            json.dump([], f)
            
    if not os.path.exists(bill_split_file):
        with open(bill_split_file, 'w') as f:
            json.dump([], f)
            
    if not os.path.exists(cashback_file):
        with open(cashback_file, 'w') as f:
            json.dump({}, f)
            
    if not os.path.exists(goals_file):
        with open(goals_file, 'w') as f:
            json.dump({}, f)
            
    if not os.path.exists(subscriptions_file):
        with open(subscriptions_file, 'w') as f:
            json.dump({}, f)

initialize_data_files()

# Helper functions for user management
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    try:
        with open(user_data_file, 'r') as f:
            users = json.load(f)
            # Migration: Add missing 'transactions' field to existing users
            for username, user_data in users.items():
                if 'transactions' not in user_data:
                    user_data['transactions'] = []
            return users
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_users(users):
    with open(user_data_file, 'w') as f:
        json.dump(users, f)

def register_user(username, password, email, phone, initial_balance=1000):
    users = load_users()
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "phone": phone,
        "balance": initial_balance,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "transactions": []
    }
    save_users(users)
    return True, "Registration successful"

def authenticate_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Invalid username"
    
    if users[username]["password"] != hash_password(password):
        return False, "Invalid password"
    
    return True, "Login successful"

# Helper functions for OTP authentication
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp(phone):
    # In a real app, this would send an SMS via a service like Twilio
    # For this demo, we'll just generate and store the OTP
    otp = generate_otp()
    st.session_state.otp = otp
    return otp

def verify_otp(entered_otp):
    if entered_otp == st.session_state.otp:
        st.session_state.otp_verified = True
        return True
    return False

# Helper functions for QR code
def generate_qr_code(data):
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL Image to bytes for Streamlit compatibility
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return img_buffer.getvalue()
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

def scan_qr_code(image):
    # Simplified QR code scanning without external DLL dependencies
    try:
        # For demo purposes, we'll simulate QR code scanning
        # In a real implementation, you would use a library that works on your system
        # This is a fallback that allows the app to run without crashes
        
        # Convert to grayscale for processing
        if image.mode != 'L':
            gray_image = image.convert('L')
        else:
            gray_image = image
        
        # Enhance image contrast
        enhancer = ImageEnhance.Contrast(gray_image)
        enhanced_image = enhancer.enhance(2.0)
        
        # For demo: return a mock QR code result if image looks like it might contain a QR code
        # In production, replace this with a working QR library for your system
        width, height = enhanced_image.size
        if width > 100 and height > 100:  # Basic size check
            # Return a demo payment URL
            return "upi://pay?pa=demo@paytm&pn=Demo%20Merchant&am=100&cu=INR"
        
        return None
    except Exception as e:
        print(f"Error scanning QR code: {e}")
        return None

# Helper functions for bill splitting
def load_bill_splits():
    try:
        with open(bill_split_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_bill_splits(bill_splits):
    with open(bill_split_file, 'w') as f:
        json.dump(bill_splits, f)

def create_bill_split(creator, title, amount, participants):
    bill_splits = load_bill_splits()
    
    # Calculate amount per person
    amount_per_person = amount / len(participants)
    
    # Create bill split record
    bill_split = {
        "id": len(bill_splits) + 1,
        "creator": creator,
        "title": title,
        "amount": amount,
        "participants": participants,
        "amount_per_person": amount_per_person,
        "paid": {participant: False for participant in participants if participant != creator},
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    bill_splits.append(bill_split)
    save_bill_splits(bill_splits)
    return bill_split

def pay_bill_split(bill_id, payer):
    bill_splits = load_bill_splits()
    users = load_users()
    
    for bill in bill_splits:
        if bill["id"] == bill_id:
            if payer in bill["paid"] and not bill["paid"][payer]:
                # Check if user has enough balance
                if users[payer]["balance"] >= bill["amount_per_person"]:
                    # Update bill split record
                    bill["paid"][payer] = True
                    
                    # Create transaction
                    add_transaction(payer, bill["creator"], bill["amount_per_person"], "bill_split")
                    
                    save_bill_splits(bill_splits)
                    return True, "Payment successful"
                else:
                    return False, "Insufficient balance"
    
    return False, "Bill not found or already paid"

# Helper functions for cashback system
def load_cashbacks():
    try:
        with open(cashback_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_cashbacks(cashbacks):
    with open(cashback_file, 'w') as f:
        json.dump(cashbacks, f)

def calculate_cashback(username, amount, transaction_type):
    cashbacks = load_cashbacks()
    
    # Initialize user cashback if not exists
    if username not in cashbacks:
        cashbacks[username] = {
            "points": 0,
            "total_cashback": 0,
            "transactions": []
        }
    
    # Calculate cashback based on transaction type and amount
    cashback_rate = 0
    if transaction_type == "send_money":
        cashback_rate = 0.005  # 0.5% cashback on send money
    elif transaction_type == "add_money":
        cashback_rate = 0.01   # 1% cashback on add money
    elif transaction_type == "bill_split":
        cashback_rate = 0.02   # 2% cashback on bill split
    
    cashback_amount = amount * cashback_rate
    points = int(cashback_amount * 10)  # 10 points per rupee of cashback
    
    # Update user cashback
    cashbacks[username]["points"] += points
    cashbacks[username]["total_cashback"] += cashback_amount
    cashbacks[username]["transactions"].append({
        "amount": amount,
        "cashback": cashback_amount,
        "points": points,
        "type": transaction_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    save_cashbacks(cashbacks)
    return points, cashback_amount

def redeem_cashback(username, points):
    cashbacks = load_cashbacks()
    users = load_users()
    
    if username in cashbacks and cashbacks[username]["points"] >= points:
        # Convert points to cashback amount (1 point = 0.1 rupee)
        cashback_amount = points / 10
        
        # Update user cashback
        cashbacks[username]["points"] -= points
        save_cashbacks(cashbacks)
        
        # Add cashback to user balance
        users[username]["balance"] += cashback_amount
        save_users(users)
        
        # Create transaction record
        add_transaction("Cashback", username, cashback_amount, "cashback")
        
        return True, f"Successfully redeemed {points} points for ₹{cashback_amount:.2f}"
    
    return False, "Insufficient points"

# Helper functions for voice commands
def listen_for_voice_command():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.write("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5)
            st.write("Processing...")
            
        command = recognizer.recognize_google(audio)
        return command.lower()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def process_voice_command(command):
    if not command:
        return False, "No command detected"
    
    # Process send money command
    send_pattern = r"send (\d+) (?:rupees|rs) to (\w+)"
    send_match = re.search(send_pattern, command)
    if send_match:
        amount = float(send_match.group(1))
        recipient = send_match.group(2)
        return "send_money", {"amount": amount, "recipient": recipient}
    
    # Process add money command
    add_pattern = r"add (\d+) (?:rupees|rs)"
    add_match = re.search(add_pattern, command)
    if add_match:
        amount = float(add_match.group(1))
        return "add_money", {"amount": amount}
    
    # Process check balance command
    if "balance" in command or "how much" in command:
        return "check_balance", {}
    
    # Process navigation commands
    if "dashboard" in command:
        return "navigate", {"page": "dashboard"}
    elif "send money" in command:
        return "navigate", {"page": "send_money"}
    elif "add money" in command:
        return "navigate", {"page": "add_money"}
    elif "transactions" in command:
        return "navigate", {"page": "transactions"}
    elif "analytics" in command:
        return "navigate", {"page": "analytics"}
    
    return False, "Command not recognized"

# Helper functions for OCR receipt scanning
def scan_receipt(image):
    try:
        # Check if required modules are available
        if pytesseract is None or ImageEnhance is None or ImageFilter is None:
            print("Error: Required modules (pytesseract, PIL) not available. Cannot scan receipt.")
            return {}
        
        # Convert to grayscale for better OCR
        if image.mode != 'L':
            gray_image = image.convert('L')
        else:
            gray_image = image
        
        # Enhance image for better OCR using PIL
        # Increase contrast
        enhancer = ImageEnhance.Contrast(gray_image)
        enhanced_image = enhancer.enhance(2.0)
        
        # Increase sharpness
        sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
        sharp_image = sharpness_enhancer.enhance(2.0)
        
        # Apply a slight blur to reduce noise
        filtered_image = sharp_image.filter(ImageFilter.MedianFilter(size=3))
        
        # Perform OCR
        text = pytesseract.image_to_string(filtered_image)
        
        # Extract information from receipt
        amount_pattern = r"(?:total|amount|amt)\s*(?::|\s)\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d{1,2})?)"
        date_pattern = r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        merchant_pattern = r"(?:merchant|store|shop|restaurant)\s*(?::|\s)\s*([\w\s]+)"
        
        amount_match = re.search(amount_pattern, text.lower())
        date_match = re.search(date_pattern, text)
        merchant_match = re.search(merchant_pattern, text.lower())
        
        result = {}
        if amount_match:
            result["amount"] = float(amount_match.group(1))
        if date_match:
            result["date"] = date_match.group(1)
        if merchant_match:
            result["merchant"] = merchant_match.group(1).strip()
        
        return result
    except Exception as e:
        print(f"Error scanning receipt: {e}")
        return {}

# Helper functions for transaction management
def load_transactions():
    try:
        with open(transaction_data_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_transactions(transactions):
    with open(transaction_data_file, 'w') as f:
        json.dump(transactions, f)

def add_transaction(sender, receiver, amount, transaction_type):
    users = load_users()
    transactions = load_transactions()
    
    # Check if sender has enough balance
    if transaction_type != "add_money" and users[sender]["balance"] < amount:
        return False, "Insufficient balance"
    
    # Update balances
    if transaction_type == "add_money":
        users[sender]["balance"] += amount
    elif transaction_type == "send_money":
        users[sender]["balance"] -= amount
        users[receiver]["balance"] += amount
    
    # Create transaction record
    transaction = {
        "id": len(transactions) + 1,
        "sender": sender,
        "receiver": receiver if transaction_type == "send_money" else sender,
        "amount": amount,
        "type": transaction_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "completed"
    }
    
    # Add transaction to global list and user's personal list
    transactions.append(transaction)
    users[sender]["transactions"].append(transaction["id"])
    if transaction_type == "send_money" and receiver in users:
        users[receiver]["transactions"].append(transaction["id"])
    
    # Save updated data
    save_users(users)
    save_transactions(transactions)
    
    return True, "Transaction successful"

# Fraud detection model
def train_fraud_detection_model():
    transactions = load_transactions()
    if len(transactions) < 10 or not SKLEARN_AVAILABLE:  # Need minimum data to train
        return None
    
    # Extract features
    df = pd.DataFrame(transactions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # Prepare features for ML model
    features = ['amount', 'hour', 'day_of_week']
    X = df[features].values
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest for anomaly detection
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_scaled)
    
    return {
        'model': model,
        'scaler': scaler,
        'features': features
    }

def check_transaction_fraud(transaction, model_data):
    if model_data is None or not SKLEARN_AVAILABLE:
        return False  # Not enough data to detect fraud
    
    # Extract features
    timestamp = datetime.strptime(transaction['timestamp'], "%Y-%m-%d %H:%M:%S")
    features = [
        transaction['amount'],
        timestamp.hour,
        timestamp.weekday()
    ]
    
    # Use trained ML model for fraud detection
    X = np.array(features).reshape(1, -1)
    X_scaled = model_data['scaler'].transform(X)
    
    # Predict anomaly (-1 for outlier, 1 for normal)
    prediction = model_data['model'].predict(X_scaled)
    
    return prediction[0] == -1  # Return True if fraud detected

# Helper functions for AI-powered features

# Enhanced fraud detection model
def train_enhanced_fraud_detection_model(transactions):
    # Extract features for fraud detection
    if not transactions or not SKLEARN_AVAILABLE:
        return None
    
    # Extract features: amount, hour, day of week, transaction type
    features_data = []
    for t in transactions:
        # Basic features
        amount = t["amount"]
        dt = datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day_of_week = dt.weekday()
        
        # Advanced features
        transaction_type_code = {
            "send_money": 0,
            "add_money": 1,
            "bill_split": 2,
            "cashback": 3
        }.get(t["type"], 0)
        
        features_data.append([amount, hour, day_of_week, transaction_type_code])
    
    # Train ML model
    X = np.array(features_data)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Random Forest for enhanced fraud detection
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Create synthetic labels (assuming most transactions are normal)
    y = np.zeros(len(X))  # 0 = normal
    # Mark some high-amount transactions as potentially fraudulent for training
    high_amount_threshold = np.percentile([t["amount"] for t in transactions], 95)
    for i, t in enumerate(transactions):
        if t["amount"] > high_amount_threshold:
            y[i] = 1  # 1 = potentially fraudulent
    
    model.fit(X_scaled, y)
    
    return {
        'model': model,
        'scaler': scaler,
        'feature_names': ['amount', 'hour', 'day_of_week', 'transaction_type']
    }

def check_enhanced_transaction_fraud(transaction, model, user_transactions):
    if model is None or not user_transactions or not SKLEARN_AVAILABLE:
        return False, 0.5  # No model or no transactions, return default
    
    # Extract features
    amount = transaction["amount"]
    dt = datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
    hour = dt.hour
    day_of_week = dt.weekday()
    
    transaction_type_code = {
        "send_money": 0,
        "add_money": 1,
        "bill_split": 2,
        "cashback": 3
    }.get(transaction["type"], 0)
    
    # Prepare features for ML model
    features = [amount, hour, day_of_week, transaction_type_code]
    X = np.array(features).reshape(1, -1)
    X_scaled = model['scaler'].transform(X)
    
    # Get fraud probability from ML model
    fraud_probability = model['model'].predict_proba(X_scaled)[0]
    risk_score = fraud_probability[1] if len(fraud_probability) > 1 else 0.5
    
    # Consider it fraud if risk score is high
    is_fraud = risk_score > 0.7
    
    return is_fraud, risk_score

# Expense prediction model
def train_expense_prediction_model(transactions, days_to_predict=30):
    if not transactions or len(transactions) < 7 or not SKLEARN_AVAILABLE:  # Need at least a week of data
        return None
    
    # Group transactions by date and calculate daily spending
    daily_spending = {}
    for t in transactions:
        if t["sender"] != "Cashback" and t["type"] != "add_money":  # Only count outgoing money
            dt = datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S").date()
            dt_str = dt.strftime("%Y-%m-%d")
            if dt_str not in daily_spending:
                daily_spending[dt_str] = 0
            daily_spending[dt_str] += t["amount"]
    
    # Convert to time series
    dates = sorted(daily_spending.keys())
    amounts = [daily_spending[d] for d in dates]
    
    # If not enough data points, use simple average
    if len(dates) < 14:  # Less than 2 weeks of data
        avg_daily_spending = sum(amounts) / len(amounts)
        predictions = [avg_daily_spending] * days_to_predict
        return predictions
    
    # Prepare data for linear regression
    X = np.array(range(len(amounts))).reshape(-1, 1)  # Day numbers as features
    y = np.array(amounts)  # Daily spending amounts
    
    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict future spending
    future_days = np.array(range(len(amounts), len(amounts) + days_to_predict)).reshape(-1, 1)
    predictions = model.predict(future_days)
    
    # Ensure predictions are non-negative
    predictions = np.maximum(predictions, 0)
    
    return predictions.tolist()

# Financial health score calculation
def calculate_financial_health_score(username):
    users = load_users()
    transactions = load_transactions()
    cashbacks = load_cashbacks()
    
    if username not in users:
        return 0, {}
    
    # Get user data
    user = users[username]
    user_transactions = [t for t in transactions if t["sender"] == username or t["receiver"] == username]
    
    # Initialize score components
    score_components = {
        "balance": 0,
        "spending_pattern": 0,
        "income_stability": 0,
        "cashback_utilization": 0,
        "transaction_frequency": 0
    }
    
    # 1. Balance component (20%)
    balance = user["balance"]
    if balance > 10000:
        score_components["balance"] = 20
    elif balance > 5000:
        score_components["balance"] = 15
    elif balance > 1000:
        score_components["balance"] = 10
    elif balance > 0:
        score_components["balance"] = 5
    
    # 2. Spending pattern (25%)
    if len(user_transactions) > 0:
        # Calculate spending ratio (outgoing/incoming)
        outgoing = sum(t["amount"] for t in user_transactions if t["sender"] == username and t["type"] != "add_money")
        incoming = sum(t["amount"] for t in user_transactions if t["receiver"] == username)
        
        if incoming > 0:
            spending_ratio = outgoing / incoming
            if spending_ratio < 0.5:
                score_components["spending_pattern"] = 25
            elif spending_ratio < 0.7:
                score_components["spending_pattern"] = 20
            elif spending_ratio < 0.9:
                score_components["spending_pattern"] = 15
            elif spending_ratio < 1.0:
                score_components["spending_pattern"] = 10
            else:
                score_components["spending_pattern"] = 5
    
    # 3. Income stability (20%)
    add_money_transactions = [t for t in user_transactions if t["type"] == "add_money" and t["receiver"] == username]
    if len(add_money_transactions) >= 3:
        # Check regularity of income
        add_money_transactions.sort(key=lambda t: t["timestamp"])
        dates = [datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S").date() for t in add_money_transactions]
        
        # Calculate days between transactions
        intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            std_interval = np.std(intervals) if len(intervals) > 1 else 0
            
            # Lower standard deviation means more regular income
            if avg_interval <= 31 and std_interval < 5:  # Regular monthly income
                score_components["income_stability"] = 20
            elif avg_interval <= 31 and std_interval < 10:
                score_components["income_stability"] = 15
            elif avg_interval <= 45:
                score_components["income_stability"] = 10
            else:
                score_components["income_stability"] = 5
    
    # 4. Cashback utilization (15%)
    if username in cashbacks:
        cashback_data = cashbacks[username]
        total_cashback = cashback_data["total_cashback"]
        redeemed_cashback = total_cashback - (cashback_data["points"] / 10)  # Points to cashback conversion
        
        if total_cashback > 0:
            redemption_ratio = redeemed_cashback / total_cashback
            if redemption_ratio > 0.8:
                score_components["cashback_utilization"] = 15
            elif redemption_ratio > 0.5:
                score_components["cashback_utilization"] = 10
            elif redemption_ratio > 0.2:
                score_components["cashback_utilization"] = 5
    
    # 5. Transaction frequency (20%)
    if len(user_transactions) > 0:
        # Calculate transactions per day
        if len(user_transactions) >= 2:
            first_date = datetime.strptime(min(t["timestamp"] for t in user_transactions), "%Y-%m-%d %H:%M:%S").date()
            last_date = datetime.strptime(max(t["timestamp"] for t in user_transactions), "%Y-%m-%d %H:%M:%S").date()
            days = (last_date - first_date).days + 1
            transactions_per_day = len(user_transactions) / max(1, days)
            
            if transactions_per_day > 2:
                score_components["transaction_frequency"] = 20
            elif transactions_per_day > 1:
                score_components["transaction_frequency"] = 15
            elif transactions_per_day > 0.5:  # At least one transaction every 2 days
                score_components["transaction_frequency"] = 10
            else:
                score_components["transaction_frequency"] = 5
    
    # Calculate total score
    total_score = sum(score_components.values())
    
    return total_score, score_components

# Budget alerts system
def load_budget_alerts():
    try:
        with open(os.path.join(data_dir, "budget_alerts.json"), 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_budget_alerts(budget_alerts):
    with open(os.path.join(data_dir, "budget_alerts.json"), 'w') as f:
        json.dump(budget_alerts, f)

def set_budget_alert(username, category, amount, period="monthly"):
    budget_alerts = load_budget_alerts()
    
    if username not in budget_alerts:
        budget_alerts[username] = {}
    
    budget_alerts[username][category] = {
        "amount": amount,
        "period": period,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_budget_alerts(budget_alerts)
    return True

def check_budget_alerts(username, transaction):
    budget_alerts = load_budget_alerts()
    transactions = load_transactions()
    
    if username not in budget_alerts:
        return []
    
    alerts = []
    transaction_type = transaction.get("type", "send_money")
    transaction_amount = transaction.get("amount", 0)
    
    # Check each budget category
    for category, budget in budget_alerts[username].items():
        # Skip if category doesn't match transaction type
        if category != "all" and category != transaction_type:
            continue
        
        # Calculate spending in the current period
        period = budget.get("period", "monthly")
        budget_amount = budget.get("amount", 0)
        
        # Get current date range based on period
        now = datetime.now()
        if period == "daily":
            start_date = datetime(now.year, now.month, now.day)
        elif period == "weekly":
            start_date = now - timedelta(days=now.weekday())
            start_date = datetime(start_date.year, start_date.month, start_date.day)
        elif period == "monthly":
            start_date = datetime(now.year, now.month, 1)
        else:  # yearly
            start_date = datetime(now.year, 1, 1)
        
        # Filter transactions in the current period
        period_transactions = [t for t in transactions 
                              if t["sender"] == username 
                              and (category == "all" or t["type"] == category) 
                              and datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S") >= start_date]
        
        # Calculate total spending in the period
        total_spent = sum(t["amount"] for t in period_transactions)
        
        # Add the current transaction amount
        if transaction_type == category or category == "all":
            total_spent += transaction_amount
        
        # Check if budget is exceeded
        if total_spent > budget_amount:
            alerts.append({
                "category": category,
                "budget": budget_amount,
                "spent": total_spent,
                "period": period,
                "exceeded_by": total_spent - budget_amount
            })
    
    return alerts

# Savings goals system
def load_savings_goals():
    try:
        with open(goals_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_savings_goals(savings_goals):
    with open(goals_file, 'w') as f:
        json.dump(savings_goals, f)

def create_savings_goal(username, title, target_amount, target_date):
    savings_goals = load_savings_goals()
    
    if username not in savings_goals:
        savings_goals[username] = []
    
    # Create new goal
    goal = {
        "id": len(savings_goals[username]) + 1,
        "title": title,
        "target_amount": target_amount,
        "current_amount": 0,
        "target_date": target_date,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed": False
    }
    
    savings_goals[username].append(goal)
    save_savings_goals(savings_goals)
    return goal

def contribute_to_savings_goal(username, goal_id, amount):
    savings_goals = load_savings_goals()
    users = load_users()
    
    if username not in savings_goals or username not in users:
        return False, "User or goal not found"
    
    # Check if user has enough balance
    if users[username]["balance"] < amount:
        return False, "Insufficient balance"
    
    # Find the goal
    goal_found = False
    for goal in savings_goals[username]:
        if goal["id"] == goal_id:
            goal_found = True
            
            # Update goal amount
            goal["current_amount"] += amount
            
            # Check if goal is completed
            if goal["current_amount"] >= goal["target_amount"]:
                goal["completed"] = True
            
            # Update user balance
            users[username]["balance"] -= amount
            
            # Create transaction record
            add_transaction(username, "Savings Goal: " + goal["title"], amount, "savings")
            
            save_savings_goals(savings_goals)
            save_users(users)
            
            return True, f"Successfully contributed ₹{amount:.2f} to {goal['title']}"
    
    if not goal_found:
        return False, "Goal not found"

# Subscription management system
def load_subscriptions():
    try:
        with open(subscriptions_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_subscriptions(subscriptions):
    with open(subscriptions_file, 'w') as f:
        json.dump(subscriptions, f)

def detect_subscription(username, transactions, min_transactions=3):
    # Group transactions by recipient
    recipient_transactions = {}
    for t in transactions:
        if t["sender"] == username:
            recipient = t["receiver"]
            if recipient not in recipient_transactions:
                recipient_transactions[recipient] = []
            recipient_transactions[recipient].append(t)
    
    potential_subscriptions = []
    
    # Check each recipient for subscription patterns
    for recipient, txns in recipient_transactions.items():
        if len(txns) < min_transactions:
            continue
        
        # Sort transactions by timestamp
        txns.sort(key=lambda t: t["timestamp"])
        
        # Check for regular payments of similar amounts
        amounts = [t["amount"] for t in txns]
        avg_amount = sum(amounts) / len(amounts)
        amount_std = np.std(amounts)
        
        # Check if amounts are consistent (low standard deviation)
        if amount_std / avg_amount < 0.1:  # Less than 10% variation
            # Check for regular intervals
            dates = [datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S") for t in txns]
            intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                interval_std = np.std(intervals) if len(intervals) > 1 else 0
                
                # Check if intervals are consistent
                if interval_std / avg_interval < 0.2:  # Less than 20% variation
                    # Determine subscription frequency
                    frequency = "unknown"
                    if 25 <= avg_interval <= 35:  # Monthly
                        frequency = "monthly"
                    elif 6 <= avg_interval <= 8:  # Weekly
                        frequency = "weekly"
                    elif 13 <= avg_interval <= 17:  # Bi-weekly
                        frequency = "bi-weekly"
                    elif 85 <= avg_interval <= 95:  # Quarterly
                        frequency = "quarterly"
                    elif 350 <= avg_interval <= 380:  # Yearly
                        frequency = "yearly"
                    
                    potential_subscriptions.append({
                        "recipient": recipient,
                        "amount": avg_amount,
                        "frequency": frequency,
                        "last_payment": txns[-1]["timestamp"],
                        "next_payment_estimate": (dates[-1] + timedelta(days=avg_interval)).strftime("%Y-%m-%d")
                    })
    
    return potential_subscriptions

def add_subscription(username, recipient, amount, frequency, description):
    subscriptions = load_subscriptions()
    
    if username not in subscriptions:
        subscriptions[username] = []
    
    # Create new subscription
    subscription = {
        "id": len(subscriptions[username]) + 1,
        "recipient": recipient,
        "amount": amount,
        "frequency": frequency,
        "description": description,
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "active": True
    }
    
    subscriptions[username].append(subscription)
    save_subscriptions(subscriptions)
    return subscription

# UI Components
def login_page():
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Google Pay Replica</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        
        # Add login options
        login_method = st.radio("Login Method", ["Username & Password", "OTP Login"], horizontal=True)
        
        if login_method == "Username & Password":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", use_container_width=True, key="login_btn"):
                    if username and password:
                        success, message = authenticate_user(username, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.current_user = username
                            st.session_state.page = 'dashboard'
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please enter both username and password")
        else:  # OTP Login
            phone = st.text_input("Phone Number")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Send OTP", use_container_width=True, key="send_otp_btn"):
                    if phone:
                        # Check if phone exists in users
                        users = load_users()
                        user_found = False
                        for username, user_data in users.items():
                            if user_data.get("phone") == phone:
                                user_found = True
                                st.session_state.otp_username = username
                                break
                        
                        if user_found:
                            otp = send_otp(phone)
                            st.success(f"OTP sent to {phone}. For demo purposes, OTP is: {otp}")
                            st.session_state.otp_sent = True
                        else:
                            st.error("Phone number not registered")
                    else:
                        st.error("Please enter your phone number")
            
            if st.session_state.get("otp_sent", False):
                otp_input = st.text_input("Enter OTP")
                if st.button("Verify OTP", use_container_width=True, key="verify_otp_btn"):
                    if otp_input:
                        if verify_otp(otp_input):
                            st.success("OTP verified successfully")
                            st.session_state.logged_in = True
                            st.session_state.current_user = st.session_state.otp_username
                            st.session_state.page = 'dashboard'
                            st.rerun()
                        else:
                            st.error("Invalid OTP")
                    else:
                        st.error("Please enter OTP")
        
        with col2:
            if st.button("Register", use_container_width=True, key="register_btn_login"):
                st.session_state.page = 'register'
                st.rerun()

def register_page():
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Google Pay Replica</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>Register</h2>", unsafe_allow_html=True)
        
        # Registration steps
        if "register_step" not in st.session_state:
            st.session_state.register_step = 1
        
        if st.session_state.register_step == 1:
            # Step 1: Basic information
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Next", use_container_width=True, key="register_next_btn"):
                    if username and password and confirm_password and email and phone:
                        if password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            # Store registration data in session state
                            st.session_state.register_data = {
                                "username": username,
                                "password": password,
                                "email": email,
                                "phone": phone
                            }
                            # Send OTP for verification
                            otp = send_otp(phone)
                            st.success(f"OTP sent to {phone}. For demo purposes, OTP is: {otp}")
                            st.session_state.register_step = 2
                            st.rerun()
                    else:
                        st.error("Please fill all fields")
            
            with col2:
                if st.button("Back to Login", use_container_width=True, key="back_to_login_btn"):
                    st.session_state.page = 'login'
                    st.rerun()
        
        elif st.session_state.register_step == 2:
            # Step 2: OTP verification
            st.write(f"OTP sent to {st.session_state.register_data['phone']}")
            otp_input = st.text_input("Enter OTP")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Verify & Register", use_container_width=True, key="verify_register_btn"):
                    if otp_input:
                        if verify_otp(otp_input):
                            # Register user with the stored data
                            success, message = register_user(
                                st.session_state.register_data["username"],
                                st.session_state.register_data["password"],
                                st.session_state.register_data["email"],
                                st.session_state.register_data["phone"]
                            )
                            if success:
                                st.success(message)
                                # Reset registration steps
                                st.session_state.register_step = 1
                                # Go to login page
                                st.session_state.page = 'login'
                                st.rerun()
                            else:
                                st.error(message)
                                # Go back to step 1
                                st.session_state.register_step = 1
                                st.rerun()
                        else:
                            st.error("Invalid OTP")
                    else:
                        st.error("Please enter OTP")
            
            with col2:
                if st.button("Resend OTP", use_container_width=True, key="resend_otp_btn"):
                    otp = send_otp(st.session_state.register_data["phone"])
                    st.success(f"OTP resent. For demo purposes, OTP is: {otp}")
                
                if st.button("Back", use_container_width=True, key="back_to_step1_btn"):
                    st.session_state.register_step = 1
                    st.rerun()

def dashboard_page():
    users = load_users()
    current_user = users[st.session_state.current_user]
    
    # Main content
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Dashboard</h1>", unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Balance", f"₹{current_user['balance']:.2f}")
    
    with col2:
        if 'cashback_points' in st.session_state:
            st.metric("Cashback Points", st.session_state.cashback_points)
        else:
            st.metric("Cashback Points", 0)
    
    with col3:
        if 'financial_health_score' in st.session_state:
            st.metric("Financial Health", f"{st.session_state.financial_health_score}/100")
        else:
            st.metric("Financial Health", "0/100")
    
    # Recent transactions
    st.markdown("<h2 style='text-align: center;'>Recent Transactions</h2>", unsafe_allow_html=True)
    
    transactions = load_transactions()
    user_transaction_ids = current_user.get('transactions', [])
    user_transactions = [t for t in transactions if t['id'] in user_transaction_ids]
    user_transactions.sort(key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)
    
    if user_transactions:
        for i, transaction in enumerate(user_transactions[:5]):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if transaction['type'] == 'add_money':
                    st.markdown(f"<h4>Added Money</h4>", unsafe_allow_html=True)
                elif transaction['sender'] == st.session_state.current_user:
                    st.markdown(f"<h4>Sent to {transaction['receiver']}</h4>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h4>Received from {transaction['sender']}</h4>", unsafe_allow_html=True)
            
            with col2:
                if transaction['sender'] == st.session_state.current_user and transaction['type'] == 'send_money':
                    st.markdown(f"<h4 style='color: red;'>-₹{transaction['amount']:.2f}</h4>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h4 style='color: green;'>+₹{transaction['amount']:.2f}</h4>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<h4>{transaction['timestamp']}</h4>", unsafe_allow_html=True)
            
            if i < len(user_transactions[:5]) - 1:
                st.markdown("---")
    else:
        st.info("No transactions yet")

def send_money_page():
    users = load_users()
    current_user = users[st.session_state.current_user]
    
    # Main content
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Send Money</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Get list of users except current user
        receiver_options = [user for user in users.keys() if user != st.session_state.current_user]
        
        if receiver_options:
            receiver = st.selectbox("Select Recipient", receiver_options)
            amount = st.number_input("Amount (₹)", min_value=1.0, max_value=float(current_user['balance']), step=1.0)
            note = st.text_input("Add a note (optional)")
            
            if st.button("Send Money", use_container_width=True, key="send_money_btn_action"):
                if amount > 0:
                    # Train fraud detection model if enough data
                    fraud_model = train_fraud_detection_model()
                    
                    # Create transaction
                    transaction = {
                        "sender": st.session_state.current_user,
                        "receiver": receiver,
                        "amount": amount,
                        "type": "send_money",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    
                    # Check for fraud
                    is_fraud = False
                    if fraud_model is not None:
                        is_fraud = check_transaction_fraud(transaction, fraud_model)
                    
                    if is_fraud:
                        st.error("This transaction appears suspicious and has been blocked. Please try a different amount or contact support.")
                    else:
                        success, message = add_transaction(st.session_state.current_user, receiver, amount, "send_money")
                        if success:
                            st.success(f"Successfully sent ₹{amount:.2f} to {receiver}")
                            # Refresh user data
                            users = load_users()
                            current_user = users[st.session_state.current_user]
                            # Update balance display
                            st.markdown(f"<h4>New Balance: ₹{current_user['balance']:.2f}</h4>", unsafe_allow_html=True)
                        else:
                            st.error(message)
                else:
                    st.error("Please enter a valid amount")
        else:
            st.info("No other users available to send money to. Ask your friends to register!")

def add_money_page():
    users = load_users()
    current_user = users[st.session_state.current_user]
    
    # Main content
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Add Money</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        amount = st.number_input("Amount (₹)", min_value=1.0, step=1.0)
        payment_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "Net Banking", "UPI"])
        
        # Conditional fields based on payment method
        if payment_method in ["Credit Card", "Debit Card"]:
            st.text_input("Card Number")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Expiry Date")
            with col2:
                st.text_input("CVV", type="password")
            st.text_input("Name on Card")
        elif payment_method == "Net Banking":
            st.selectbox("Bank", ["SBI", "HDFC", "ICICI", "Axis", "PNB", "Other"])
        elif payment_method == "UPI":
            st.text_input("UPI ID")
        
        if st.button("Add Money", use_container_width=True, key="add_money_btn_action"):
            if amount > 0:
                # In a real app, we would process the payment here
                # For this demo, we'll just add the money directly
                success, message = add_transaction(st.session_state.current_user, st.session_state.current_user, amount, "add_money")
                if success:
                    st.success(f"Successfully added ₹{amount:.2f} to your account")
                    # Refresh user data
                    users = load_users()
                    current_user = users[st.session_state.current_user]
                    # Update balance display
                    st.markdown(f"<h4>New Balance: ₹{current_user['balance']:.2f}</h4>", unsafe_allow_html=True)
                else:
                    st.error(message)
            else:
                st.error("Please enter a valid amount")

def transactions_page():
    users = load_users()
    current_user = users[st.session_state.current_user]
    
    # Sidebar (same as dashboard)
    with st.sidebar:
        st.markdown(f"<h3>Welcome, {st.session_state.current_user}!</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4>Balance: ₹{current_user['balance']:.2f}</h4>", unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Dashboard", use_container_width=True, key="dashboard_btn_transactions"):
            st.session_state.page = 'dashboard'
            st.rerun()
        if st.button("Send Money", use_container_width=True, key="send_money_btn_transactions"):
            st.session_state.page = 'send_money'
            st.rerun()
        if st.button("Add Money", use_container_width=True, key="add_money_btn_transactions"):
            st.session_state.page = 'add_money'
            st.rerun()
        if st.button("Transaction History", use_container_width=True, key="transactions_btn_transactions"):
            st.session_state.page = 'transactions'
            st.rerun()
        if st.button("Analytics", use_container_width=True, key="analytics_btn_transactions"):
            st.session_state.page = 'analytics'
            st.rerun()
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True, key="logout_btn_transactions"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Main content
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Transaction History</h1>", unsafe_allow_html=True)
    
    transactions = load_transactions()
    user_transaction_ids = current_user.get('transactions', [])
    user_transactions = [t for t in transactions if t['id'] in user_transaction_ids]
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        transaction_type = st.selectbox("Filter by Type", ["All", "Send Money", "Add Money"])
    with col2:
        sort_order = st.selectbox("Sort by", ["Newest First", "Oldest First", "Amount (High to Low)", "Amount (Low to High)"])
    
    # Apply filters
    if transaction_type != "All":
        filter_type = transaction_type.lower().replace(" ", "_")
        user_transactions = [t for t in user_transactions if t['type'] == filter_type]
    
    # Apply sorting
    if sort_order == "Newest First":
        user_transactions.sort(key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)
    elif sort_order == "Oldest First":
        user_transactions.sort(key=lambda x: datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S"))
    elif sort_order == "Amount (High to Low)":
        user_transactions.sort(key=lambda x: x['amount'], reverse=True)
    elif sort_order == "Amount (Low to High)":
        user_transactions.sort(key=lambda x: x['amount'])
    
    if user_transactions:
        for i, transaction in enumerate(user_transactions):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                if transaction['type'] == 'add_money':
                    st.markdown(f"<h4>Added Money</h4>", unsafe_allow_html=True)
                elif transaction['sender'] == st.session_state.current_user:
                    st.markdown(f"<h4>Sent to {transaction['receiver']}</h4>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h4>Received from {transaction['sender']}</h4>", unsafe_allow_html=True)
            
            with col2:
                if transaction['sender'] == st.session_state.current_user and transaction['type'] == 'send_money':
                    st.markdown(f"<h4 style='color: red;'>-₹{transaction['amount']:.2f}</h4>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h4 style='color: green;'>+₹{transaction['amount']:.2f}</h4>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<h4>{transaction['status']}</h4>", unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"<h4>{transaction['timestamp']}</h4>", unsafe_allow_html=True)
            
            if i < len(user_transactions) - 1:
                st.markdown("---")
    else:
        st.info("No transactions found with the selected filters")

def analytics_page():
    users = load_users()
    current_user = users[st.session_state.current_user]
    
    # Sidebar (same as dashboard)
    with st.sidebar:
        st.markdown(f"<h3>Welcome, {st.session_state.current_user}!</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4>Balance: ₹{current_user['balance']:.2f}</h4>", unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Dashboard", use_container_width=True, key="dashboard_btn_analytics"):
            st.session_state.page = 'dashboard'
            st.rerun()
        if st.button("Send Money", use_container_width=True, key="send_money_btn_analytics"):
            st.session_state.page = 'send_money'
            st.rerun()
        if st.button("Add Money", use_container_width=True, key="add_money_btn_analytics"):
            st.session_state.page = 'add_money'
            st.rerun()
        if st.button("Transaction History", use_container_width=True, key="transactions_btn_analytics"):
            st.session_state.page = 'transactions'
            st.rerun()
        if st.button("Analytics", use_container_width=True, key="analytics_btn_analytics"):
            st.session_state.page = 'analytics'
            st.rerun()
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True, key="logout_btn_analytics"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Main content
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Analytics</h1>", unsafe_allow_html=True)
    
    transactions = load_transactions()
    user_transaction_ids = current_user.get('transactions', [])
    user_transactions = [t for t in transactions if t['id'] in user_transaction_ids]
    
    if user_transactions:
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(user_transactions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Add a column for transaction direction
        df['direction'] = df.apply(lambda x: 'outgoing' if x['sender'] == st.session_state.current_user and x['type'] == 'send_money' else 'incoming', axis=1)
        
        # Spending over time
        st.markdown("<h2 style='text-align: center;'>Spending Over Time</h2>", unsafe_allow_html=True)
        
        # Group by date and direction
        daily_amounts = df.groupby(['date', 'direction'])['amount'].sum().unstack().fillna(0)
        if 'outgoing' not in daily_amounts.columns:
            daily_amounts['outgoing'] = 0
        if 'incoming' not in daily_amounts.columns:
            daily_amounts['incoming'] = 0
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        daily_amounts['outgoing'].plot(kind='bar', color='red', ax=ax, position=0, width=0.4, label='Outgoing')
        daily_amounts['incoming'].plot(kind='bar', color='green', ax=ax, position=1, width=0.4, label='Incoming')
        plt.title('Daily Transaction Amounts')
        plt.xlabel('Date')
        plt.ylabel('Amount (₹)')
        plt.legend()
        plt.tight_layout()
        st.pyplot(fig)
        
        # Transaction patterns
        st.markdown("<h2 style='text-align: center;'>Transaction Patterns</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction types pie chart
            st.markdown("<h3 style='text-align: center;'>Transaction Types</h3>", unsafe_allow_html=True)
            type_counts = df['type'].value_counts()
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=90, colors=['#4285F4', '#EA4335'])
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            st.pyplot(fig)
        
        with col2:
            # Transaction by hour of day
            st.markdown("<h3 style='text-align: center;'>Transactions by Hour</h3>", unsafe_allow_html=True)
            df['hour'] = df['timestamp'].dt.hour
            hourly_counts = df['hour'].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.bar(hourly_counts.index, hourly_counts.values, color='#4285F4')
            ax.set_xlabel('Hour of Day')
            ax.set_ylabel('Number of Transactions')
            ax.set_xticks(range(0, 24))
            st.pyplot(fig)
        
        # Spending patterns by recipient
        if 'send_money' in df['type'].values:
            st.markdown("<h2 style='text-align: center;'>Spending by Recipient</h2>", unsafe_allow_html=True)
            
            # Filter for send_money transactions
            send_money_df = df[df['type'] == 'send_money']
            recipient_amounts = send_money_df.groupby('receiver')['amount'].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            recipient_amounts.plot(kind='bar', color='#4285F4', ax=ax)
            plt.title('Total Amount Sent by Recipient')
            plt.xlabel('Recipient')
            plt.ylabel('Amount (₹)')
            plt.tight_layout()
            st.pyplot(fig)
        
        # Spending recommendations based on patterns
        st.markdown("<h2 style='text-align: center;'>Spending Insights</h2>", unsafe_allow_html=True)
        
        # Calculate some basic statistics
        total_spent = df[df['direction'] == 'outgoing']['amount'].sum()
        total_received = df[df['direction'] == 'incoming']['amount'].sum()
        net_flow = total_received - total_spent
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Spent", f"₹{total_spent:.2f}")
        with col2:
            st.metric("Total Received", f"₹{total_received:.2f}")
        with col3:
            st.metric("Net Flow", f"₹{net_flow:.2f}", delta=f"{net_flow:.2f}")
        
        # Simple recommendations based on spending patterns
        st.markdown("<h3 style='text-align: center;'>Recommendations</h3>", unsafe_allow_html=True)
        
        if net_flow < 0:
            st.warning("Your spending exceeds your income. Consider reducing expenses or finding additional sources of income.")
        else:
            st.success("You're maintaining a positive cash flow. Great job!")
        
        # If we have enough data, show more detailed recommendations
        if len(df) >= 5:
            # Find the top spending category (recipient)
            if 'send_money' in df['type'].values and len(send_money_df) > 0:
                top_recipient = recipient_amounts.index[0]
                top_amount = recipient_amounts.iloc[0]
                st.info(f"Your highest spending is with {top_recipient} (₹{top_amount:.2f}). Consider reviewing these transactions for potential savings.")
            
            # Check for unusual spending patterns
            if 'hour' in df.columns and len(df) >= 10:
                unusual_hours = df[(df['hour'] < 6) | (df['hour'] > 22)]
                if len(unusual_hours) > 0:
                    st.warning(f"You have {len(unusual_hours)} transactions during unusual hours (late night/early morning). Be cautious of impulse spending during these times.")
    else:
        st.info("Not enough transaction data to generate analytics. Make some transactions to see insights!")

# Main app logic
def main():
    # Check if user is logged in
    if not st.session_state.get('logged_in', False):
        show_auth_page()
    else:
        # Show main navigation and content
        show_main_app()

def ai_recommendations_page():
    """AI-powered spending recommendations page"""
    st.title("🤖 AI Spending Recommendations")
    
    try:
        from ai_recommendations import AIRecommendationEngine
        
        # Initialize AI engine
        ai_engine = AIRecommendationEngine()
        
        # Load user transactions
        transactions = load_transactions()
        user_transactions = [t for t in transactions if t.get('sender') == st.session_state.current_user or t.get('receiver') == st.session_state.current_user]
        
        if user_transactions:
            # Get comprehensive insights
            insights = ai_engine.get_comprehensive_insights(st.session_state.current_user, user_transactions)
            
            # Display financial health score
            st.metric("Financial Health Score", f"{insights['financial_health_score']:.1f}/100")
            
            # Display recommendations
            st.subheader("📊 Personalized Recommendations")
            for rec in insights['recommendations']:
                if rec['type'] == 'budget':
                    st.info(f"💰 Budget: {rec['message']}")
                elif rec['type'] == 'category':
                    st.warning(f"📈 Category: {rec['message']}")
                elif rec['type'] == 'timing':
                    st.success(f"⏰ Timing: {rec['message']}")
                elif rec['type'] == 'health':
                    st.error(f"🏥 Health: {rec['message']}")
                elif rec['type'] == 'savings':
                    st.info(f"💎 Savings: {rec['message']}")
            
            # Display spending patterns
            st.subheader("📈 Spending Patterns")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top Categories:**")
                for category, amount in insights['spending_patterns']['top_categories'].items():
                    st.write(f"• {category}: ₹{amount:.2f}")
            
            with col2:
                st.write("**Monthly Trends:**")
                for month, amount in insights['spending_patterns']['monthly_trends'].items():
                    st.write(f"• {month}: ₹{amount:.2f}")
            
            # User segment
            st.subheader("👤 Your Profile")
            st.info(f"User Segment: {insights['user_segment']}")
            
        else:
            st.info("No transaction data available for AI analysis. Make some transactions to get personalized recommendations!")
            
    except ImportError:
        st.error("AI Recommendations module not available. Please check installation.")
    except Exception as e:
        st.error(f"Error loading AI recommendations: {str(e)}")

def payment_gateway_page():
    """Payment gateway integration page"""
    st.title("💳 Payment Gateway")
    
    try:
        from payment_gateway import PaymentGateway, get_available_payment_methods
        
        # Initialize payment gateway with default gateway type
        gateway = PaymentGateway('razorpay')  # Default to Razorpay
        
        tab1, tab2, tab3 = st.tabs(["Make Payment", "Payment History", "Settings"])
        
        with tab1:
            st.subheader("💰 Create Payment")
            
            # Payment form
            with st.form("payment_form"):
                amount = st.number_input("Amount (₹)", min_value=1.0, step=1.0)
                currency = st.selectbox("Currency", ["INR", "USD", "EUR"])
                payment_method = st.selectbox("Payment Gateway", ["stripe", "razorpay", "paypal"])
                description = st.text_input("Description", "Payment via Google Pay TWIN")
                
                if st.form_submit_button("Create Payment Intent"):
                    try:
                        # Create payment intent
                        result = gateway.create_payment_intent(
                            amount=amount,
                            currency=currency,
                            description=description
                        )
                        
                        if result['success']:
                            st.success(f"Payment intent created! ID: {result['id']}")
                            st.info(f"Client Secret: {result['client_secret']}")
                            
                            # In a real app, you would redirect to payment page
                            st.warning("In a real application, you would be redirected to the payment gateway.")
                        else:
                            st.error(f"Failed to create payment: {result['error']}")
                    except Exception as e:
                        st.error(f"Error creating payment: {str(e)}")
        
        with tab2:
            st.subheader("📋 Payment History")
            
            # Load payment transactions
            try:
                from payment_gateway import load_payment_transactions
                payments = load_payment_transactions()
                
                if payments:
                    df = pd.DataFrame(payments)
                    st.dataframe(df)
                else:
                    st.info("No payment history available.")
            except Exception as e:
                st.error(f"Error loading payment history: {str(e)}")
        
        with tab3:
            st.subheader("⚙️ Gateway Settings")
            
            # Display available payment methods
            gateway_type = st.selectbox("Select Gateway:", ['razorpay', 'stripe', 'paypal'], index=0)
            methods = get_available_payment_methods(gateway_type)
            st.write("**Available Payment Methods:**")
            for method in methods:
                st.write(f"• {method['icon']} {method['name']}")
            
            # Gateway configuration (mock)
            st.write("**Configuration:**")
            st.info("Payment gateways are configured with test credentials for demo purposes.")
            
    except ImportError:
        st.error("Payment Gateway module not available. Please check installation.")
    except Exception as e:
        st.error(f"Error loading payment gateway: {str(e)}")

def security_settings_page():
    """Enhanced security settings page"""
    st.title("🔒 Security Settings")
    
    try:
        from security import SecurityManager, generate_security_recommendations
        
        # Initialize security manager
        security_manager = SecurityManager()
        
        tab1, tab2, tab3, tab4 = st.tabs(["2FA Setup", "Biometric Auth", "Security Logs", "Recommendations"])
        
        with tab1:
            st.subheader("📱 Two-Factor Authentication")
            
            # Check if 2FA is enabled
            user_data = get_current_user_data()
            tfa_enabled = user_data.get('2fa_enabled', False)
            
            if tfa_enabled:
                st.success("✅ Two-Factor Authentication is enabled")
                if st.button("Disable 2FA"):
                    # In a real app, you would disable 2FA
                    st.warning("2FA disabled (demo)")
            else:
                st.warning("⚠️ Two-Factor Authentication is disabled")
                
                if st.button("Enable 2FA"):
                    # Generate QR code for 2FA setup
                    secret = security_manager.generate_2fa_secret(st.session_state.current_user)
                    qr_code = security_manager.generate_2fa_qr(st.session_state.current_user, secret)
                    
                    st.success("Scan this QR code with your authenticator app:")
                    st.image(qr_code)
                    st.code(f"Manual entry key: {secret}")
                    
                    # Verification
                    verification_code = st.text_input("Enter verification code from your app:")
                    if st.button("Verify and Enable"):
                        if security_manager.verify_2fa_token(secret, verification_code):
                            st.success("2FA enabled successfully!")
                        else:
                            st.error("Invalid verification code")
        
        with tab2:
            st.subheader("👤 Biometric Authentication")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Fingerprint Authentication**")
                if st.button("Setup Fingerprint"):
                    # Mock fingerprint setup
                    with st.spinner("Scanning fingerprint..."):
                        time.sleep(2)
                        result = security_manager.setup_fingerprint(st.session_state.current_user)
                        if result['success']:
                            st.success("Fingerprint registered successfully!")
                        else:
                            st.error("Fingerprint setup failed")
            
            with col2:
                st.write("**Face Recognition**")
                if st.button("Setup Face Recognition"):
                    # Mock face recognition setup
                    with st.spinner("Scanning face..."):
                        time.sleep(2)
                        result = security_manager.setup_face_recognition(st.session_state.current_user)
                        if result['success']:
                            st.success("Face recognition registered successfully!")
                        else:
                            st.error("Face recognition setup failed")
        
        with tab3:
            st.subheader("📊 Security Event Logs")
            
            # Load security logs
            logs = security_manager.get_security_logs(st.session_state.current_user)
            
            if logs:
                df = pd.DataFrame(logs)
                st.dataframe(df)
            else:
                st.info("No security events logged.")
            
            # Login attempts
            st.write("**Recent Login Attempts:**")
            attempts = security_manager.get_login_attempts(st.session_state.current_user)
            for attempt in attempts[-5:]:  # Show last 5 attempts
                status_color = "🟢" if attempt['success'] else "🔴"
                st.write(f"{status_color} {attempt['timestamp']} - {attempt['ip_address']} - {'Success' if attempt['success'] else 'Failed'}")
        
        with tab4:
            st.subheader("💡 Security Recommendations")
            
            # Generate security recommendations
            recommendations = generate_security_recommendations(st.session_state.current_user)
            
            for rec in recommendations:
                if rec['priority'] == 'high':
                    st.error(f"🚨 High Priority: {rec['message']}")
                elif rec['priority'] == 'medium':
                    st.warning(f"⚠️ Medium Priority: {rec['message']}")
                else:
                    st.info(f"ℹ️ Low Priority: {rec['message']}")
            
            # Password strength check
            st.write("**Password Security:**")
            new_password = st.text_input("Test password strength:", type="password")
            if new_password:
                strength = security_manager.check_password_strength(new_password)
                if strength['score'] >= 80:
                    st.success(f"Strong password (Score: {strength['score']}/100)")
                elif strength['score'] >= 60:
                    st.warning(f"Medium strength password (Score: {strength['score']}/100)")
                else:
                    st.error(f"Weak password (Score: {strength['score']}/100)")
                
                st.write("**Suggestions:**")
                for suggestion in strength['suggestions']:
                    st.write(f"• {suggestion}")
                    
    except ImportError:
        st.error("Security module not available. Please check installation.")
    except Exception as e:
        st.error(f"Error loading security settings: {str(e)}")

def show_main_app():
    """Show the main application with navigation"""
    # Sidebar navigation
    with st.sidebar:
        st.title("💰 Google Pay TWIN")
        
        # User info
        user_data = get_current_user_data()
        if user_data:
            st.success(f"Welcome, {user_data.get('username', 'User')}!")
            st.info(f"Balance: ₹{user_data.get('balance', 0):.2f}")
        
        # Navigation menu
        selected = option_menu(
            menu_title="Navigation",
            options=[
                "Dashboard", "Send Money", "Add Money", "Transactions", "Analytics",
                "QR Code", "Bill Split", "Cashback", "Scan Receipt", "Voice Pay",
                "Budget Alerts", "Savings Goals", "Subscriptions", "Financial Health",
                "Pay Later", "Spending Challenge", "Financial Assistant", "Expense Prediction",
                "Fraud Detection", "Spending Heatmap", "Emotion Insights", "Investment Tracker",
                "Recurring Payments", "AI Recommendations", "Payment Gateway", "Security Settings"
            ],
            icons=[
                "house", "send", "plus-circle", "list", "bar-chart",
                "qr-code", "people", "gift", "camera", "mic",
                "exclamation-triangle", "piggy-bank", "calendar", "heart-pulse",
                "clock", "trophy", "robot", "graph-up",
                "shield-check", "calendar-heat", "emoji-smile", "graph-up-arrow",
                "arrow-repeat", "lightbulb", "credit-card", "shield-lock"
            ],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )
        
        # Logout button
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
    
    # Main content area
    if selected == "Dashboard":
        dashboard_page()
    elif selected == "Send Money":
        send_money_page()
    elif selected == "Add Money":
        add_money_page()
    elif selected == "Transactions":
        transactions_page()
    elif selected == "Analytics":
        analytics_page()
    elif selected == "QR Code":
        qr_code_page()
    elif selected == "Bill Split":
        bill_split_page()
    elif selected == "Cashback":
        cashback_page()
    elif selected == "Scan Receipt":
        # Import here to avoid circular dependency
        from scan_receipt_page import scan_receipt_page
        scan_receipt_page()
    elif selected == "Voice Pay":
        voice_pay_page()
    elif selected == "Budget Alerts":
        budget_alerts_page()
    elif selected == "Savings Goals":
        savings_goals_page()
    elif selected == "Subscriptions":
        subscriptions_page()
    elif selected == "Financial Health":
        financial_health_page()
    elif selected == "Pay Later":
        pay_later_page()
    elif selected == "Spending Challenge":
        spending_challenge_page()
    elif selected == "Financial Assistant":
        financial_assistant_page()
    elif selected == "Expense Prediction":
        expense_prediction_page()
    elif selected == "Fraud Detection":
        fraud_detection_page()
    elif selected == "Spending Heatmap":
        spending_heatmap_page()
    elif selected == "Emotion Insights":
        emotion_insights_page()
    elif selected == "Investment Tracker":
        investment_tracker_page()
    elif selected == "Recurring Payments":
        user_data = get_current_user_data()
        if user_data:
            recurring_payments_page(user_data.get('username', 'Unknown'))
    elif selected == "AI Recommendations":
        ai_recommendations_page()
    elif selected == "Payment Gateway":
        payment_gateway_page()
    elif selected == "Security Settings":
        security_settings_page()

def check_and_install_dependencies():
    """Check and install required dependencies"""
    import sys
    import subprocess
    import importlib
    import time
    
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
        'pyttsx3',
        'SpeechRecognition'
    ]
    
    # Handle calmap separately due to Python 3.13 compatibility issues
    optional_packages = ['calmap']
    
    print("🔍 Checking dependencies...")
    
    missing_packages = []
    for package in required_packages:
        try:
            # Handle special package names
            import_name = package
            if package == 'streamlit-option-menu':
                import_name = 'streamlit_option_menu'
            elif package == 'streamlit-webrtc':
                import_name = 'streamlit_webrtc'
            elif package == 'Pillow':
                import_name = 'PIL'
            elif package == 'scikit-learn':
                import_name = 'sklearn'
            elif package == 'SpeechRecognition':
                import_name = 'speech_recognition'
                
            importlib.import_module(import_name)
            print(f"✅ {package} is available.")
        except ImportError:
            print(f"❌ {package} not found. Installing...")
            missing_packages.append(package)
    
    # Install missing packages
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"✅ {package} installed successfully.")
                    break
                except subprocess.CalledProcessError:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Retry {attempt + 1}/{max_retries} for {package}...")
                        time.sleep(2)
                    else:
                        print(f"❌ Failed to install {package} after {max_retries} attempts.")
    
    # Handle optional packages (like calmap) with better error handling
    print("\n🔍 Checking optional dependencies...")
    for package in optional_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} is available.")
        except ImportError:
            print(f"⚠️ {package} not found. Attempting installation...")
            max_retries = 2
            installed = False
            for attempt in range(max_retries):
                try:
                    # Try different installation methods for calmap
                    if package == 'calmap':
                        # First try regular pip install
                        subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"✅ {package} installed successfully.")
                    installed = True
                    break
                except subprocess.CalledProcessError:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Retry {attempt + 1}/{max_retries} for {package}...")
                        time.sleep(1)
                    else:
                        print(f"⚠️ {package} installation failed. Calendar heatmap features will be disabled.")
                        print(f"   This is expected on Python 3.13 due to compatibility issues.")
            
            # Verify installation
            if installed:
                try:
                    importlib.import_module(package)
                    print(f"✅ {package} verification successful.")
                except ImportError:
                    print(f"⚠️ {package} installed but import failed. Features may be limited.")
    
    print("✅ Dependency check completed.")
    return True

def validate_app_functionality():
    """Validate that all critical app functions are working"""
    print("\n🔍 Validating application functionality...")
    
    # Test critical functions
    try:
        # Test data loading/saving
        users = load_users()
        print("✅ User data loading works")
        
        # Test transaction functions
        transactions = load_transactions()
        print("✅ Transaction data loading works")
        
        # Test QR code generation
        test_qr = generate_qr_code("test")
        print("✅ QR code generation works")
        
        # Test voice functions (if available)
        if sr is not None and pyttsx3 is not None:
            print("✅ Voice recognition modules available")
        else:
            print("⚠️  Voice features limited (missing modules)")
        
        # Test ML functions (if available)
        if SKLEARN_AVAILABLE:
            print("✅ Machine learning features available")
        else:
            print("⚠️  ML features limited (sklearn not available)")
        
        # Validate user data structure
        for username, user_data in users.items():
            if 'transactions' not in user_data:
                user_data['transactions'] = []
                print(f"✅ Fixed missing 'transactions' field for user: {username}")
        
        if users:  # Only save if there are users
            save_users(users)
            print("✅ User data validation and fixes applied")
        
        print("✅ Application validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Application validation failed: {e}")
        return False

if __name__ == "__main__":
    print("🏦 Google Pay TWIN Application")
    print("=" * 40)
    
    try:
        # Check and install dependencies
        print("📦 Checking dependencies...")
        check_and_install_dependencies()
        
        # Validate app functionality
        if not validate_app_functionality():
            print("\n❌ Application validation failed. Please check the errors above.")
            input("\nPress Enter to exit...")
            exit(1)
        
        print("\n🚀 All systems ready! Starting application...")
        print("\n" + "=" * 50)
        print("🌟 Welcome to Google Pay TWIN!")
        print("📱 Your complete digital payment solution")
        print("=" * 50)
        
        main()
        
    except KeyboardInterrupt:
        print("\n⏹️  Application stopped by user.")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Run: python -m pip install -r requirements.txt")
        print("   2. Ensure you have Python 3.8+ installed")
        print("   3. Check that all page modules are in the same directory")
        print("   4. Verify data directory permissions")
        input("\nPress Enter to exit...")