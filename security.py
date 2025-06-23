import streamlit as st
import hashlib
import hmac
import secrets
import pyotp
import qrcode
import io
import base64
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import jwt
from cryptography.fernet import Fernet
import time
import re

# Security configuration
SECURITY_CONFIG = {
    'jwt_secret': 'your-super-secret-jwt-key-change-in-production',
    'jwt_algorithm': 'HS256',
    'jwt_expiry_hours': 24,
    'session_timeout_minutes': 30,
    'max_login_attempts': 5,
    'lockout_duration_minutes': 15,
    'password_min_length': 8,
    'require_special_chars': True,
    'require_numbers': True,
    'require_uppercase': True
}

class SecurityManager:
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = 'data/encryption.key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Create new key
            os.makedirs('data', exist_ok=True)
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 for password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return base64.b64encode(password_hash).decode(), salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash"""
        password_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(password_hash, hashed_password)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        
        if len(password) < SECURITY_CONFIG['password_min_length']:
            errors.append(f"Password must be at least {SECURITY_CONFIG['password_min_length']} characters long")
        
        if SECURITY_CONFIG['require_uppercase'] and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if SECURITY_CONFIG['require_numbers'] and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if SECURITY_CONFIG['require_special_chars'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common patterns
        if password.lower() in ['password', '123456', 'qwerty', 'admin']:
            errors.append("Password is too common")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'strength_score': self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> int:
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length bonus
        score += min(25, len(password) * 2)
        
        # Character variety bonus
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 15
        if re.search(r'\d', password):
            score += 15
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 20
        
        # Uniqueness bonus
        unique_chars = len(set(password))
        score += min(15, unique_chars)
        
        return min(100, score)
    
    def generate_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT token for user session"""
        payload = {
            'user_id': user_data.get('username'),
            'email': user_data.get('email'),
            'exp': datetime.utcnow() + timedelta(hours=SECURITY_CONFIG['jwt_expiry_hours']),
            'iat': datetime.utcnow(),
            'jti': secrets.token_hex(16)  # JWT ID for token revocation
        }
        
        return jwt.encode(
            payload,
            SECURITY_CONFIG['jwt_secret'],
            algorithm=SECURITY_CONFIG['jwt_algorithm']
        )
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                SECURITY_CONFIG['jwt_secret'],
                algorithms=[SECURITY_CONFIG['jwt_algorithm']]
            )
            return {'valid': True, 'payload': payload}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
    
    def check_session_timeout(self, last_activity: datetime) -> bool:
        """Check if session has timed out"""
        timeout_duration = timedelta(minutes=SECURITY_CONFIG['session_timeout_minutes'])
        return datetime.now() - last_activity > timeout_duration

class TwoFactorAuth:
    def __init__(self):
        self.security_manager = SecurityManager()
    
    def generate_totp_secret(self, username: str) -> str:
        """Generate TOTP secret for user"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, username: str, secret: str, issuer: str = "GooglePay Twin") -> str:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for display
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 1 window tolerance
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """Generate backup codes for 2FA"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    def send_sms_code(self, phone_number: str) -> str:
        """Send SMS verification code (mock implementation)"""
        # In real implementation, integrate with SMS service like Twilio
        code = str(secrets.randbelow(900000) + 100000)  # 6-digit code
        
        # Store code temporarily (in real app, use Redis or database)
        if 'sms_codes' not in st.session_state:
            st.session_state.sms_codes = {}
        
        st.session_state.sms_codes[phone_number] = {
            'code': code,
            'expires_at': datetime.now() + timedelta(minutes=5)
        }
        
        # Mock SMS sending
        st.info(f"SMS sent to {phone_number}: {code} (Mock - in production this would be sent via SMS)")
        
        return code
    
    def verify_sms_code(self, phone_number: str, code: str) -> bool:
        """Verify SMS code"""
        if 'sms_codes' not in st.session_state:
            return False
        
        stored_data = st.session_state.sms_codes.get(phone_number)
        if not stored_data:
            return False
        
        # Check expiry
        if datetime.now() > stored_data['expires_at']:
            del st.session_state.sms_codes[phone_number]
            return False
        
        # Verify code
        if stored_data['code'] == code:
            del st.session_state.sms_codes[phone_number]
            return True
        
        return False

class BiometricAuth:
    def __init__(self):
        self.security_manager = SecurityManager()
    
    def simulate_fingerprint_scan(self) -> Dict[str, Any]:
        """Simulate fingerprint scanning (mock implementation)"""
        # In real implementation, integrate with device fingerprint scanner
        import random
        
        # Simulate scanning process
        time.sleep(2)  # Simulate scan time
        
        # Mock success/failure
        success = random.choice([True, True, True, False])  # 75% success rate
        
        if success:
            fingerprint_hash = hashlib.sha256(
                f"fingerprint_{datetime.now().timestamp()}".encode()
            ).hexdigest()[:16]
            
            return {
                'success': True,
                'fingerprint_id': fingerprint_hash,
                'confidence': random.uniform(0.85, 0.99)
            }
        else:
            return {
                'success': False,
                'error': 'Fingerprint not recognized or scan failed'
            }
    
    def simulate_face_recognition(self) -> Dict[str, Any]:
        """Simulate face recognition (mock implementation)"""
        # In real implementation, integrate with camera and face recognition library
        import random
        
        # Simulate recognition process
        time.sleep(3)  # Simulate processing time
        
        # Mock success/failure
        success = random.choice([True, True, False])  # 67% success rate
        
        if success:
            face_hash = hashlib.sha256(
                f"face_{datetime.now().timestamp()}".encode()
            ).hexdigest()[:16]
            
            return {
                'success': True,
                'face_id': face_hash,
                'confidence': random.uniform(0.80, 0.95)
            }
        else:
            return {
                'success': False,
                'error': 'Face not recognized or poor lighting conditions'
            }
    
    def register_biometric(self, user_id: str, biometric_type: str, biometric_data: str) -> bool:
        """Register biometric data for user"""
        # Encrypt biometric data
        encrypted_data = self.security_manager.encrypt_data(biometric_data)
        
        # Load existing biometric data
        biometrics_file = 'data/biometrics.json'
        try:
            with open(biometrics_file, 'r') as f:
                biometrics = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            biometrics = {}
        
        # Store biometric data
        if user_id not in biometrics:
            biometrics[user_id] = {}
        
        biometrics[user_id][biometric_type] = {
            'data': encrypted_data,
            'registered_at': datetime.now().isoformat()
        }
        
        # Save updated biometrics
        os.makedirs('data', exist_ok=True)
        with open(biometrics_file, 'w') as f:
            json.dump(biometrics, f, indent=2)
        
        return True
    
    def verify_biometric(self, user_id: str, biometric_type: str, biometric_data: str) -> bool:
        """Verify biometric data for user"""
        # Load biometric data
        biometrics_file = 'data/biometrics.json'
        try:
            with open(biometrics_file, 'r') as f:
                biometrics = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False
        
        # Check if user has registered biometric
        user_biometrics = biometrics.get(user_id, {})
        stored_biometric = user_biometrics.get(biometric_type)
        
        if not stored_biometric:
            return False
        
        # Decrypt and compare
        try:
            stored_data = self.security_manager.decrypt_data(stored_biometric['data'])
            return stored_data == biometric_data
        except:
            return False

class LoginAttemptTracker:
    def __init__(self):
        self.attempts_file = 'data/login_attempts.json'
    
    def record_attempt(self, username: str, success: bool, ip_address: str = None):
        """Record login attempt"""
        # Load existing attempts
        try:
            with open(self.attempts_file, 'r') as f:
                attempts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            attempts = {}
        
        # Initialize user attempts if not exists
        if username not in attempts:
            attempts[username] = {
                'failed_attempts': 0,
                'last_attempt': None,
                'locked_until': None,
                'attempt_history': []
            }
        
        # Record attempt
        attempt_data = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'ip_address': ip_address
        }
        
        attempts[username]['attempt_history'].append(attempt_data)
        attempts[username]['last_attempt'] = datetime.now().isoformat()
        
        if success:
            # Reset failed attempts on successful login
            attempts[username]['failed_attempts'] = 0
            attempts[username]['locked_until'] = None
        else:
            # Increment failed attempts
            attempts[username]['failed_attempts'] += 1
            
            # Lock account if max attempts reached
            if attempts[username]['failed_attempts'] >= SECURITY_CONFIG['max_login_attempts']:
                lockout_until = datetime.now() + timedelta(
                    minutes=SECURITY_CONFIG['lockout_duration_minutes']
                )
                attempts[username]['locked_until'] = lockout_until.isoformat()
        
        # Save updated attempts
        os.makedirs('data', exist_ok=True)
        with open(self.attempts_file, 'w') as f:
            json.dump(attempts, f, indent=2)
    
    def is_account_locked(self, username: str) -> Tuple[bool, Optional[datetime]]:
        """Check if account is locked"""
        try:
            with open(self.attempts_file, 'r') as f:
                attempts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False, None
        
        user_attempts = attempts.get(username, {})
        locked_until_str = user_attempts.get('locked_until')
        
        if not locked_until_str:
            return False, None
        
        locked_until = datetime.fromisoformat(locked_until_str)
        
        if datetime.now() < locked_until:
            return True, locked_until
        else:
            # Unlock account
            user_attempts['locked_until'] = None
            user_attempts['failed_attempts'] = 0
            
            with open(self.attempts_file, 'w') as f:
                json.dump(attempts, f, indent=2)
            
            return False, None
    
    def get_failed_attempts(self, username: str) -> int:
        """Get number of failed attempts for user"""
        try:
            with open(self.attempts_file, 'r') as f:
                attempts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0
        
        return attempts.get(username, {}).get('failed_attempts', 0)

def generate_secure_session_id() -> str:
    """Generate secure session ID"""
    return secrets.token_urlsafe(32)

def validate_session_security(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate session security"""
    security_manager = SecurityManager()
    
    # Check session timeout
    last_activity = datetime.fromisoformat(session_data.get('last_activity', datetime.now().isoformat()))
    
    if security_manager.check_session_timeout(last_activity):
        return {
            'valid': False,
            'reason': 'Session timeout',
            'action': 'redirect_to_login'
        }
    
    # Verify JWT token if present
    jwt_token = session_data.get('jwt_token')
    if jwt_token:
        token_result = security_manager.verify_jwt_token(jwt_token)
        if not token_result['valid']:
            return {
                'valid': False,
                'reason': token_result['error'],
                'action': 'redirect_to_login'
            }
    
    return {'valid': True}

def log_security_event(event_type: str, user_id: str, details: Dict[str, Any]):
    """Log security events for monitoring"""
    event_data = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'details': details
    }
    
    # Load existing logs
    logs_file = 'data/security_logs.json'
    try:
        with open(logs_file, 'r') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    
    # Add new log
    logs.append(event_data)
    
    # Keep only last 1000 logs
    logs = logs[-1000:]
    
    # Save updated logs
    os.makedirs('data', exist_ok=True)
    with open(logs_file, 'w') as f:
        json.dump(logs, f, indent=2)

def get_security_recommendations(user_data: Dict[str, Any]) -> list:
    """Get personalized security recommendations"""
    recommendations = []
    
    # Check if 2FA is enabled
    if not user_data.get('two_factor_enabled'):
        recommendations.append({
            'type': 'critical',
            'title': 'Enable Two-Factor Authentication',
            'description': 'Add an extra layer of security to your account',
            'action': 'setup_2fa'
        })
    
    # Check password age
    password_changed = user_data.get('password_changed_at')
    if password_changed:
        password_age = datetime.now() - datetime.fromisoformat(password_changed)
        if password_age.days > 90:
            recommendations.append({
                'type': 'warning',
                'title': 'Update Your Password',
                'description': 'Your password is over 90 days old',
                'action': 'change_password'
            })
    
    # Check biometric setup
    if not user_data.get('biometric_enabled'):
        recommendations.append({
            'type': 'info',
            'title': 'Set Up Biometric Authentication',
            'description': 'Use fingerprint or face recognition for quick access',
            'action': 'setup_biometric'
        })
    
    return recommendations