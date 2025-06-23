import streamlit as st
import json
import os
from datetime import datetime
import hashlib
import hmac
import base64
import requests
from typing import Dict, Any, Tuple

# Mock payment gateway configurations
PAYMENT_GATEWAYS = {
    'stripe': {
        'api_key': 'sk_test_mock_stripe_key',
        'publishable_key': 'pk_test_mock_stripe_key',
        'webhook_secret': 'whsec_mock_stripe_webhook'
    },
    'razorpay': {
        'key_id': 'rzp_test_mock_key_id',
        'key_secret': 'mock_razorpay_secret'
    },
    'paypal': {
        'client_id': 'mock_paypal_client_id',
        'client_secret': 'mock_paypal_client_secret',
        'mode': 'sandbox'  # sandbox or live
    }
}

class PaymentGateway:
    def __init__(self, gateway_type: str):
        self.gateway_type = gateway_type
        self.config = PAYMENT_GATEWAYS.get(gateway_type, {})
        
    def create_payment_intent(self, amount: float, currency: str = 'INR', 
                            customer_id: str = None, description: str = None) -> Dict[str, Any]:
        """Create a payment intent with the selected gateway"""
        
        if self.gateway_type == 'stripe':
            return self._create_stripe_payment_intent(amount, currency, customer_id, description)
        elif self.gateway_type == 'razorpay':
            return self._create_razorpay_order(amount, currency, customer_id, description)
        elif self.gateway_type == 'paypal':
            return self._create_paypal_order(amount, currency, customer_id, description)
        else:
            raise ValueError(f"Unsupported gateway: {self.gateway_type}")
    
    def _create_stripe_payment_intent(self, amount: float, currency: str, 
                                    customer_id: str, description: str) -> Dict[str, Any]:
        """Mock Stripe payment intent creation"""
        # In real implementation, use stripe.PaymentIntent.create()
        payment_intent = {
            'id': f'pi_mock_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'amount': int(amount * 100),  # Stripe uses cents
            'currency': currency.lower(),
            'status': 'requires_payment_method',
            'client_secret': f'pi_mock_secret_{datetime.now().timestamp()}',
            'gateway': 'stripe'
        }
        return {'success': True, 'data': payment_intent}
    
    def _create_razorpay_order(self, amount: float, currency: str, 
                             customer_id: str, description: str) -> Dict[str, Any]:
        """Mock Razorpay order creation"""
        # In real implementation, use razorpay.Order.create()
        order = {
            'id': f'order_mock_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'amount': int(amount * 100),  # Razorpay uses paise
            'currency': currency,
            'status': 'created',
            'gateway': 'razorpay'
        }
        return {'success': True, 'data': order}
    
    def _create_paypal_order(self, amount: float, currency: str, 
                           customer_id: str, description: str) -> Dict[str, Any]:
        """Mock PayPal order creation"""
        # In real implementation, use PayPal REST API
        order = {
            'id': f'paypal_mock_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'amount': amount,
            'currency': currency,
            'status': 'CREATED',
            'approval_url': f'https://www.sandbox.paypal.com/checkoutnow?token=mock_token_{datetime.now().timestamp()}',
            'gateway': 'paypal'
        }
        return {'success': True, 'data': order}
    
    def confirm_payment(self, payment_id: str, payment_method: str = None) -> Dict[str, Any]:
        """Confirm payment with the selected gateway"""
        
        if self.gateway_type == 'stripe':
            return self._confirm_stripe_payment(payment_id, payment_method)
        elif self.gateway_type == 'razorpay':
            return self._verify_razorpay_payment(payment_id)
        elif self.gateway_type == 'paypal':
            return self._capture_paypal_order(payment_id)
        else:
            raise ValueError(f"Unsupported gateway: {self.gateway_type}")
    
    def _confirm_stripe_payment(self, payment_intent_id: str, payment_method: str) -> Dict[str, Any]:
        """Mock Stripe payment confirmation"""
        # In real implementation, use stripe.PaymentIntent.confirm()
        # Simulate successful payment
        result = {
            'id': payment_intent_id,
            'status': 'succeeded',
            'amount_received': 10000,  # Mock amount
            'gateway': 'stripe',
            'transaction_id': f'txn_mock_{datetime.now().timestamp()}'
        }
        return {'success': True, 'data': result}
    
    def _verify_razorpay_payment(self, payment_id: str) -> Dict[str, Any]:
        """Mock Razorpay payment verification"""
        # In real implementation, verify payment signature
        result = {
            'id': payment_id,
            'status': 'captured',
            'amount': 10000,  # Mock amount
            'gateway': 'razorpay',
            'transaction_id': f'pay_mock_{datetime.now().timestamp()}'
        }
        return {'success': True, 'data': result}
    
    def _capture_paypal_order(self, order_id: str) -> Dict[str, Any]:
        """Mock PayPal order capture"""
        # In real implementation, capture the PayPal order
        result = {
            'id': order_id,
            'status': 'COMPLETED',
            'amount': 100.00,  # Mock amount
            'gateway': 'paypal',
            'transaction_id': f'paypal_txn_{datetime.now().timestamp()}'
        }
        return {'success': True, 'data': result}
    
    def refund_payment(self, payment_id: str, amount: float = None) -> Dict[str, Any]:
        """Process refund for a payment"""
        
        if self.gateway_type == 'stripe':
            return self._create_stripe_refund(payment_id, amount)
        elif self.gateway_type == 'razorpay':
            return self._create_razorpay_refund(payment_id, amount)
        elif self.gateway_type == 'paypal':
            return self._create_paypal_refund(payment_id, amount)
        else:
            raise ValueError(f"Unsupported gateway: {self.gateway_type}")
    
    def _create_stripe_refund(self, payment_intent_id: str, amount: float) -> Dict[str, Any]:
        """Mock Stripe refund creation"""
        refund = {
            'id': f're_mock_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'payment_intent': payment_intent_id,
            'amount': int(amount * 100) if amount else None,
            'status': 'succeeded',
            'gateway': 'stripe'
        }
        return {'success': True, 'data': refund}
    
    def _create_razorpay_refund(self, payment_id: str, amount: float) -> Dict[str, Any]:
        """Mock Razorpay refund creation"""
        refund = {
            'id': f'rfnd_mock_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'payment_id': payment_id,
            'amount': int(amount * 100) if amount else None,
            'status': 'processed',
            'gateway': 'razorpay'
        }
        return {'success': True, 'data': refund}
    
    def _create_paypal_refund(self, capture_id: str, amount: float) -> Dict[str, Any]:
        """Mock PayPal refund creation"""
        refund = {
            'id': f'paypal_refund_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'capture_id': capture_id,
            'amount': amount,
            'status': 'COMPLETED',
            'gateway': 'paypal'
        }
        return {'success': True, 'data': refund}

def get_available_payment_methods(gateway_type: str) -> list:
    """Get available payment methods for a gateway"""
    
    methods = {
        'stripe': [
            {'id': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
            {'id': 'upi', 'name': 'UPI', 'icon': '📱'},
            {'id': 'netbanking', 'name': 'Net Banking', 'icon': '🏦'},
            {'id': 'wallet', 'name': 'Digital Wallet', 'icon': '👛'}
        ],
        'razorpay': [
            {'id': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'},
            {'id': 'upi', 'name': 'UPI', 'icon': '📱'},
            {'id': 'netbanking', 'name': 'Net Banking', 'icon': '🏦'},
            {'id': 'wallet', 'name': 'Digital Wallet', 'icon': '👛'},
            {'id': 'emi', 'name': 'EMI', 'icon': '📊'}
        ],
        'paypal': [
            {'id': 'paypal', 'name': 'PayPal Account', 'icon': '🅿️'},
            {'id': 'card', 'name': 'Credit/Debit Card', 'icon': '💳'}
        ]
    }
    
    return methods.get(gateway_type, [])

def save_payment_transaction(transaction_data: Dict[str, Any]):
    """Save payment transaction to file"""
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Load existing transactions
    transactions_file = 'data/payment_transactions.json'
    try:
        with open(transactions_file, 'r') as f:
            transactions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        transactions = []
    
    # Add new transaction
    transaction_data['created_at'] = datetime.now().isoformat()
    transactions.append(transaction_data)
    
    # Save updated transactions
    with open(transactions_file, 'w') as f:
        json.dump(transactions, f, indent=2)

def load_payment_transactions() -> list:
    """Load payment transactions from file"""
    
    transactions_file = 'data/payment_transactions.json'
    try:
        with open(transactions_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def verify_webhook_signature(payload: str, signature: str, secret: str, gateway_type: str) -> bool:
    """Verify webhook signature from payment gateway"""
    
    if gateway_type == 'stripe':
        # Stripe webhook verification
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f'sha256={expected_signature}', signature)
    
    elif gateway_type == 'razorpay':
        # Razorpay webhook verification
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)
    
    elif gateway_type == 'paypal':
        # PayPal webhook verification (simplified)
        # In real implementation, verify with PayPal's certificate
        return True  # Mock verification
    
    return False

def process_webhook_event(event_data: Dict[str, Any], gateway_type: str):
    """Process webhook event from payment gateway"""
    
    event_type = event_data.get('type') or event_data.get('event')
    
    if gateway_type == 'stripe':
        if event_type == 'payment_intent.succeeded':
            # Handle successful payment
            payment_intent = event_data['data']['object']
            # Update transaction status in database
            pass
        elif event_type == 'payment_intent.payment_failed':
            # Handle failed payment
            payment_intent = event_data['data']['object']
            # Update transaction status in database
            pass
    
    elif gateway_type == 'razorpay':
        if event_type == 'payment.captured':
            # Handle successful payment
            payment = event_data['payload']['payment']['entity']
            # Update transaction status in database
            pass
        elif event_type == 'payment.failed':
            # Handle failed payment
            payment = event_data['payload']['payment']['entity']
            # Update transaction status in database
            pass
    
    elif gateway_type == 'paypal':
        if event_type == 'PAYMENT.CAPTURE.COMPLETED':
            # Handle successful payment
            capture = event_data['resource']
            # Update transaction status in database
            pass
        elif event_type == 'PAYMENT.CAPTURE.DENIED':
            # Handle failed payment
            capture = event_data['resource']
            # Update transaction status in database
            pass

def get_payment_gateway_fees(gateway_type: str, amount: float) -> Dict[str, float]:
    """Calculate payment gateway fees"""
    
    fee_structures = {
        'stripe': {
            'percentage': 2.9,
            'fixed': 0.30,
            'currency': 'USD'
        },
        'razorpay': {
            'percentage': 2.0,
            'fixed': 0.0,
            'currency': 'INR'
        },
        'paypal': {
            'percentage': 3.49,
            'fixed': 0.49,
            'currency': 'USD'
        }
    }
    
    fee_structure = fee_structures.get(gateway_type, {'percentage': 2.0, 'fixed': 0.0})
    
    percentage_fee = (amount * fee_structure['percentage']) / 100
    fixed_fee = fee_structure['fixed']
    total_fee = percentage_fee + fixed_fee
    
    return {
        'percentage_fee': percentage_fee,
        'fixed_fee': fixed_fee,
        'total_fee': total_fee,
        'net_amount': amount - total_fee
    }

def create_payment_link(gateway_type: str, amount: float, description: str, 
                       customer_email: str = None) -> Dict[str, Any]:
    """Create a payment link for sharing"""
    
    gateway = PaymentGateway(gateway_type)
    payment_intent = gateway.create_payment_intent(amount, 'INR', description=description)
    
    if payment_intent['success']:
        payment_data = payment_intent['data']
        
        # Create a shareable payment link
        payment_link = {
            'id': f'link_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'payment_id': payment_data['id'],
            'amount': amount,
            'description': description,
            'gateway': gateway_type,
            'status': 'active',
            'expires_at': (datetime.now().timestamp() + 3600),  # 1 hour expiry
            'url': f'https://pay.googlepay-twin.com/link/{payment_data["id"]}'
        }
        
        # Save payment link
        save_payment_link(payment_link)
        
        return {'success': True, 'data': payment_link}
    
    return payment_intent

def save_payment_link(link_data: Dict[str, Any]):
    """Save payment link to file"""
    
    os.makedirs('data', exist_ok=True)
    
    links_file = 'data/payment_links.json'
    try:
        with open(links_file, 'r') as f:
            links = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        links = []
    
    links.append(link_data)
    
    with open(links_file, 'w') as f:
        json.dump(links, f, indent=2)

def load_payment_links() -> list:
    """Load payment links from file"""
    
    links_file = 'data/payment_links.json'
    try:
        with open(links_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []