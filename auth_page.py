import streamlit as st
import json
import hashlib
import random
import string
import time
from datetime import datetime, timedelta
import requests
import os

# Mock Google OAuth configuration
GOOGLE_CLIENT_ID = "mock_google_client_id"
GOOGLE_CLIENT_SECRET = "mock_google_client_secret"
GOOGLE_REDIRECT_URI = "http://localhost:8501/auth/google/callback"

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    try:
        with open('data/users.json', 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_users(users):
    """Save users to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=2)

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_mock(phone_number):
    """Mock OTP sending function"""
    otp = generate_otp()
    # In real implementation, this would send SMS via Twilio or similar service
    st.session_state.current_otp = otp
    st.session_state.otp_sent_time = time.time()
    return otp

def verify_otp(entered_otp):
    """Verify entered OTP"""
    if 'current_otp' not in st.session_state:
        return False, "No OTP sent"
    
    # Check if OTP is expired (5 minutes)
    if time.time() - st.session_state.get('otp_sent_time', 0) > 300:
        return False, "OTP expired"
    
    if entered_otp == st.session_state.current_otp:
        return True, "OTP verified successfully"
    else:
        return False, "Invalid OTP"

def mock_google_oauth():
    """Mock Google OAuth flow"""
    # In real implementation, this would redirect to Google OAuth
    mock_user_data = {
        "id": "mock_google_user_123",
        "email": "user@gmail.com",
        "name": "John Doe",
        "picture": "https://via.placeholder.com/150"
    }
    return mock_user_data

def register_user(username, email, phone, password, auth_method="password", google_data=None):
    """Register a new user"""
    users = load_users()
    
    # Check if user already exists
    if username in users:
        return False, "Username already exists"
    
    # Check if email already exists
    for user_data in users.values():
        if user_data.get('email') == email:
            return False, "Email already registered"
    
    # Create user data
    user_data = {
        "username": username,
        "email": email,
        "phone": phone,
        "balance": 1000.0,  # Starting balance
        "created_at": datetime.now().isoformat(),
        "auth_method": auth_method,
        "is_verified": False,
        "login_attempts": 0,
        "last_login": None
    }
    
    if auth_method == "password":
        user_data["password"] = hash_password(password)
    elif auth_method == "google" and google_data:
        user_data["google_id"] = google_data["id"]
        user_data["name"] = google_data["name"]
        user_data["picture"] = google_data["picture"]
        user_data["is_verified"] = True
    
    users[username] = user_data
    save_users(users)
    return True, "Registration successful"

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    user_data = users[username]
    
    # Check if account is locked due to too many failed attempts
    if user_data.get('login_attempts', 0) >= 5:
        last_attempt = user_data.get('last_failed_login')
        if last_attempt:
            last_attempt_time = datetime.fromisoformat(last_attempt)
            if datetime.now() - last_attempt_time < timedelta(minutes=30):
                return False, "Account locked due to too many failed attempts. Try again in 30 minutes."
            else:
                # Reset login attempts after 30 minutes
                user_data['login_attempts'] = 0
    
    # Verify password
    if user_data.get('password') == hash_password(password):
        # Reset login attempts on successful login
        user_data['login_attempts'] = 0
        user_data['last_login'] = datetime.now().isoformat()
        users[username] = user_data
        save_users(users)
        return True, "Login successful"
    else:
        # Increment login attempts
        user_data['login_attempts'] = user_data.get('login_attempts', 0) + 1
        user_data['last_failed_login'] = datetime.now().isoformat()
        users[username] = user_data
        save_users(users)
        return False, "Invalid password"

def show_auth_page():
    """Display authentication page"""
    st.title("🔐 Google Pay TWIN - Authentication")
    
    # Initialize session state
    if 'auth_step' not in st.session_state:
        st.session_state.auth_step = 'login'
    if 'otp_verified' not in st.session_state:
        st.session_state.otp_verified = False
    
    # Create tabs for Login and Register
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_register_form()

def show_login_form():
    """Display login form"""
    st.header("Login to Your Account")
    
    # Login method selection
    login_method = st.radio(
        "Choose login method:",
        ["Username & Password", "Phone & OTP", "Google OAuth"],
        horizontal=True
    )
    
    if login_method == "Username & Password":
        show_password_login()
    elif login_method == "Phone & OTP":
        show_otp_login()
    elif login_method == "Google OAuth":
        show_google_login()

def show_password_login():
    """Display password-based login form"""
    with st.form("password_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember me")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)
        with col2:
            forgot_password = st.form_submit_button("Forgot Password?", use_container_width=True)
        
        if login_button:
            if username and password:
                success, message = authenticate_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.session_state.auth_method = "password"
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please enter both username and password")
        
        if forgot_password:
            st.info("Password reset functionality would be implemented here")

def show_otp_login():
    """Display OTP-based login form"""
    if st.session_state.auth_step == 'login':
        with st.form("otp_request_form"):
            phone = st.text_input("Phone Number", placeholder="+91XXXXXXXXXX")
            send_otp_button = st.form_submit_button("Send OTP", use_container_width=True)
            
            if send_otp_button:
                if phone:
                    # Validate phone number format
                    if len(phone) >= 10:
                        otp = send_otp_mock(phone)
                        st.session_state.auth_step = 'verify_otp'
                        st.session_state.login_phone = phone
                        st.success(f"OTP sent to {phone}")
                        st.info(f"**Demo OTP: {otp}** (In production, this would be sent via SMS)")
                        st.rerun()
                    else:
                        st.error("Please enter a valid phone number")
                else:
                    st.error("Please enter your phone number")
    
    elif st.session_state.auth_step == 'verify_otp':
        st.info(f"OTP sent to {st.session_state.login_phone}")
        
        with st.form("otp_verify_form"):
            entered_otp = st.text_input("Enter OTP", max_chars=6)
            
            col1, col2 = st.columns(2)
            with col1:
                verify_button = st.form_submit_button("Verify OTP", use_container_width=True)
            with col2:
                resend_button = st.form_submit_button("Resend OTP", use_container_width=True)
            
            if verify_button:
                if entered_otp:
                    success, message = verify_otp(entered_otp)
                    if success:
                        # Find user by phone number
                        users = load_users()
                        user_found = None
                        for username, user_data in users.items():
                            if user_data.get('phone') == st.session_state.login_phone:
                                user_found = username
                                break
                        
                        if user_found:
                            st.session_state.logged_in = True
                            st.session_state.current_user = user_found
                            st.session_state.auth_method = "otp"
                            st.session_state.otp_verified = True
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("No account found with this phone number")
                    else:
                        st.error(message)
                else:
                    st.error("Please enter the OTP")
            
            if resend_button:
                otp = send_otp_mock(st.session_state.login_phone)
                st.success("OTP resent successfully")
                st.info(f"**Demo OTP: {otp}**")
        
        if st.button("← Back to phone entry"):
            st.session_state.auth_step = 'login'
            st.rerun()

def show_google_login():
    """Display Google OAuth login"""
    st.info("🚀 **Google OAuth Integration**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔗 Continue with Google", use_container_width=True, type="primary"):
            # Mock Google OAuth flow
            with st.spinner("Authenticating with Google..."):
                time.sleep(2)  # Simulate API call
                google_data = mock_google_oauth()
                
                # Check if user exists
                users = load_users()
                user_found = None
                for username, user_data in users.items():
                    if user_data.get('email') == google_data['email']:
                        user_found = username
                        break
                
                if user_found:
                    # Existing user login
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_found
                    st.session_state.auth_method = "google"
                    st.success(f"Welcome back, {google_data['name']}!")
                    st.rerun()
                else:
                    # New user registration
                    username = google_data['email'].split('@')[0]
                    success, message = register_user(
                        username=username,
                        email=google_data['email'],
                        phone="",  # Will be asked later if needed
                        password="",
                        auth_method="google",
                        google_data=google_data
                    )
                    
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.current_user = username
                        st.session_state.auth_method = "google"
                        st.success(f"Welcome to Google Pay TWIN, {google_data['name']}!")
                        st.rerun()
                    else:
                        st.error(message)
    
    st.markdown("---")
    st.caption("**Note:** This is a demo implementation. In production, this would redirect to Google's OAuth servers.")

def show_register_form():
    """Display registration form"""
    st.header("Create New Account")
    
    # Registration method selection
    reg_method = st.radio(
        "Choose registration method:",
        ["Email & Password", "Google OAuth"],
        horizontal=True
    )
    
    if reg_method == "Email & Password":
        show_email_registration()
    elif reg_method == "Google OAuth":
        show_google_registration()

def show_email_registration():
    """Display email-based registration form"""
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*")
            email = st.text_input("Email*")
        
        with col2:
            phone = st.text_input("Phone Number*", placeholder="+91XXXXXXXXXX")
            password = st.text_input("Password*", type="password")
        
        confirm_password = st.text_input("Confirm Password*", type="password")
        
        # Terms and conditions
        terms_accepted = st.checkbox("I agree to the Terms and Conditions and Privacy Policy")
        
        register_button = st.form_submit_button("Create Account", use_container_width=True)
        
        if register_button:
            # Validation
            if not all([username, email, phone, password, confirm_password]):
                st.error("Please fill in all required fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            elif not terms_accepted:
                st.error("Please accept the terms and conditions")
            else:
                success, message = register_user(username, email, phone, password)
                if success:
                    st.success(message)
                    st.info("Please login with your credentials")
                else:
                    st.error(message)

def show_google_registration():
    """Display Google OAuth registration"""
    st.info("🚀 **Quick Registration with Google**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔗 Sign up with Google", use_container_width=True, type="primary"):
            # This would trigger the same Google OAuth flow as login
            show_google_login()
    
    st.markdown("---")
    st.caption("**Benefits of Google Sign-up:**")
    st.caption("• Quick and secure registration")
    st.caption("• No need to remember passwords")
    st.caption("• Automatic profile setup")

def logout_user():
    """Logout current user"""
    # Clear session state
    keys_to_clear = [
        'logged_in', 'current_user', 'auth_method', 'auth_step',
        'otp_verified', 'current_otp', 'otp_sent_time', 'login_phone'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Logged out successfully")
    st.rerun()

def get_current_user_data():
    """Get current user's data"""
    if not st.session_state.get('logged_in') or not st.session_state.get('current_user'):
        return None
    
    users = load_users()
    return users.get(st.session_state.current_user)

def update_user_data(user_data):
    """Update current user's data"""
    if not st.session_state.get('logged_in') or not st.session_state.get('current_user'):
        return False
    
    users = load_users()
    users[st.session_state.current_user] = user_data
    save_users(users)
    return True

# Security features
def check_session_timeout():
    """Check if user session has timed out"""
    if 'last_activity' in st.session_state:
        last_activity = datetime.fromisoformat(st.session_state.last_activity)
        if datetime.now() - last_activity > timedelta(hours=2):  # 2 hour timeout
            logout_user()
            st.warning("Session expired. Please login again.")
            return False
    
    st.session_state.last_activity = datetime.now().isoformat()
    return True

def require_auth():
    """Decorator function to require authentication"""
    if not st.session_state.get('logged_in'):
        st.warning("Please login to access this feature")
        show_auth_page()
        return False
    
    return check_session_timeout()

if __name__ == "__main__":
    show_auth_page()