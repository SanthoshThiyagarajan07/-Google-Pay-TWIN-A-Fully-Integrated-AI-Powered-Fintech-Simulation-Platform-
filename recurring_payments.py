import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid
from dateutil.relativedelta import relativedelta
import calendar

# Try to import scheduling libraries
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    st.warning("APScheduler not available. Using basic scheduling simulation.")

class RecurringPaymentManager:
    def __init__(self):
        self.payments_file = 'data/recurring_payments.json'
        self.reminders_file = 'data/payment_reminders.json'
        self.payment_history_file = 'data/recurring_payment_history.json'
        self.ensure_data_files()
        
        if SCHEDULER_AVAILABLE:
            self.scheduler = BackgroundScheduler()
            self.scheduler.start()
        else:
            self.scheduler = None
    
    def ensure_data_files(self):
        """Ensure data files exist"""
        os.makedirs('data', exist_ok=True)
        
        for file_path in [self.payments_file, self.reminders_file, self.payment_history_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def create_recurring_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new recurring payment"""
        # Generate unique ID
        payment_id = str(uuid.uuid4())
        
        # Validate payment data
        validation_result = self.validate_payment_data(payment_data)
        if not validation_result['valid']:
            return {'success': False, 'error': validation_result['errors']}
        
        # Create payment record
        recurring_payment = {
            'id': payment_id,
            'username': payment_data['username'],
            'recipient': payment_data['recipient'],
            'amount': float(payment_data['amount']),
            'description': payment_data.get('description', ''),
            'frequency': payment_data['frequency'],  # daily, weekly, monthly, yearly
            'start_date': payment_data['start_date'],
            'end_date': payment_data.get('end_date'),
            'next_payment_date': self.calculate_next_payment_date(
                payment_data['start_date'], 
                payment_data['frequency']
            ),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'payment_method': payment_data.get('payment_method', 'default'),
            'auto_pay': payment_data.get('auto_pay', False),
            'reminder_days': payment_data.get('reminder_days', [1, 3]),  # Days before payment
            'category': payment_data.get('category', 'Bills & Utilities'),
            'tags': payment_data.get('tags', []),
            'payment_count': 0,
            'total_paid': 0.0,
            'last_payment_date': None,
            'failed_attempts': 0
        }
        
        # Save to file
        payments = self.load_recurring_payments()
        payments.append(recurring_payment)
        self.save_recurring_payments(payments)
        
        # Schedule reminders
        self.schedule_payment_reminders(recurring_payment)
        
        # Schedule automatic payment if enabled
        if recurring_payment['auto_pay']:
            self.schedule_automatic_payment(recurring_payment)
        
        return {
            'success': True, 
            'payment_id': payment_id,
            'next_payment_date': recurring_payment['next_payment_date']
        }
    
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate recurring payment data"""
        errors = []
        
        # Required fields
        required_fields = ['username', 'recipient', 'amount', 'frequency', 'start_date']
        for field in required_fields:
            if field not in payment_data or not payment_data[field]:
                errors.append(f"{field} is required")
        
        # Validate amount
        try:
            amount = float(payment_data.get('amount', 0))
            if amount <= 0:
                errors.append("Amount must be greater than 0")
            elif amount > 100000:
                errors.append("Amount cannot exceed $100,000")
        except (ValueError, TypeError):
            errors.append("Invalid amount format")
        
        # Validate frequency
        valid_frequencies = ['daily', 'weekly', 'bi-weekly', 'monthly', 'quarterly', 'yearly']
        if payment_data.get('frequency') not in valid_frequencies:
            errors.append(f"Frequency must be one of: {', '.join(valid_frequencies)}")
        
        # Validate dates
        try:
            start_date = datetime.fromisoformat(payment_data['start_date'])
            if start_date < datetime.now() - timedelta(days=1):
                errors.append("Start date cannot be in the past")
            
            if payment_data.get('end_date'):
                end_date = datetime.fromisoformat(payment_data['end_date'])
                if end_date <= start_date:
                    errors.append("End date must be after start date")
        except (ValueError, TypeError):
            errors.append("Invalid date format")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def calculate_next_payment_date(self, current_date: str, frequency: str) -> str:
        """Calculate the next payment date based on frequency"""
        current = datetime.fromisoformat(current_date)
        
        if frequency == 'daily':
            next_date = current + timedelta(days=1)
        elif frequency == 'weekly':
            next_date = current + timedelta(weeks=1)
        elif frequency == 'bi-weekly':
            next_date = current + timedelta(weeks=2)
        elif frequency == 'monthly':
            next_date = current + relativedelta(months=1)
        elif frequency == 'quarterly':
            next_date = current + relativedelta(months=3)
        elif frequency == 'yearly':
            next_date = current + relativedelta(years=1)
        else:
            next_date = current + timedelta(days=30)  # Default to monthly
        
        return next_date.isoformat()
    
    def load_recurring_payments(self, username: str = None) -> List[Dict[str, Any]]:
        """Load recurring payments from file"""
        try:
            with open(self.payments_file, 'r') as f:
                payments = json.load(f)
            
            if username:
                payments = [p for p in payments if p.get('username') == username]
            
            return payments
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_recurring_payments(self, payments: List[Dict[str, Any]]):
        """Save recurring payments to file"""
        with open(self.payments_file, 'w') as f:
            json.dump(payments, f, indent=2)
    
    def update_recurring_payment(self, payment_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing recurring payment"""
        payments = self.load_recurring_payments()
        
        for i, payment in enumerate(payments):
            if payment['id'] == payment_id:
                # Update fields
                for key, value in updates.items():
                    if key in payment:
                        payment[key] = value
                
                payment['updated_at'] = datetime.now().isoformat()
                
                # Recalculate next payment date if frequency changed
                if 'frequency' in updates:
                    payment['next_payment_date'] = self.calculate_next_payment_date(
                        payment['last_payment_date'] or payment['start_date'],
                        payment['frequency']
                    )
                
                payments[i] = payment
                self.save_recurring_payments(payments)
                
                # Reschedule reminders and auto-payments
                self.schedule_payment_reminders(payment)
                if payment.get('auto_pay'):
                    self.schedule_automatic_payment(payment)
                
                return {'success': True, 'payment': payment}
        
        return {'success': False, 'error': 'Payment not found'}
    
    def cancel_recurring_payment(self, payment_id: str) -> Dict[str, Any]:
        """Cancel a recurring payment"""
        payments = self.load_recurring_payments()
        
        for i, payment in enumerate(payments):
            if payment['id'] == payment_id:
                payment['status'] = 'cancelled'
                payment['cancelled_at'] = datetime.now().isoformat()
                
                payments[i] = payment
                self.save_recurring_payments(payments)
                
                # Remove scheduled jobs
                if self.scheduler:
                    try:
                        self.scheduler.remove_job(f"payment_{payment_id}")
                        self.scheduler.remove_job(f"reminder_{payment_id}")
                    except:
                        pass
                
                return {'success': True, 'message': 'Payment cancelled successfully'}
        
        return {'success': False, 'error': 'Payment not found'}
    
    def process_payment(self, payment_id: str, manual: bool = False) -> Dict[str, Any]:
        """Process a recurring payment"""
        payments = self.load_recurring_payments()
        
        for i, payment in enumerate(payments):
            if payment['id'] == payment_id:
                # Check if payment is due
                next_payment = datetime.fromisoformat(payment['next_payment_date'])
                if not manual and next_payment > datetime.now():
                    return {'success': False, 'error': 'Payment not yet due'}
                
                # Simulate payment processing
                payment_result = self.simulate_payment_processing(payment)
                
                if payment_result['success']:
                    # Update payment record
                    payment['payment_count'] += 1
                    payment['total_paid'] += payment['amount']
                    payment['last_payment_date'] = datetime.now().isoformat()
                    payment['failed_attempts'] = 0
                    
                    # Calculate next payment date
                    payment['next_payment_date'] = self.calculate_next_payment_date(
                        payment['last_payment_date'],
                        payment['frequency']
                    )
                    
                    # Check if payment should end
                    if payment.get('end_date'):
                        end_date = datetime.fromisoformat(payment['end_date'])
                        if datetime.fromisoformat(payment['next_payment_date']) > end_date:
                            payment['status'] = 'completed'
                    
                    payments[i] = payment
                    self.save_recurring_payments(payments)
                    
                    # Record payment history
                    self.record_payment_history(payment, payment_result)
                    
                    # Schedule next reminders
                    if payment['status'] == 'active':
                        self.schedule_payment_reminders(payment)
                        if payment.get('auto_pay'):
                            self.schedule_automatic_payment(payment)
                    
                    return {
                        'success': True,
                        'transaction_id': payment_result['transaction_id'],
                        'next_payment_date': payment['next_payment_date']
                    }
                else:
                    # Handle failed payment
                    payment['failed_attempts'] += 1
                    
                    if payment['failed_attempts'] >= 3:
                        payment['status'] = 'suspended'
                        self.create_reminder({
                            'username': payment['username'],
                            'type': 'payment_suspended',
                            'message': f"Recurring payment to {payment['recipient']} has been suspended due to multiple failures",
                            'payment_id': payment_id,
                            'priority': 'high'
                        })
                    
                    payments[i] = payment
                    self.save_recurring_payments(payments)
                    
                    return {
                        'success': False,
                        'error': payment_result['error'],
                        'failed_attempts': payment['failed_attempts']
                    }
        
        return {'success': False, 'error': 'Payment not found'}
    
    def simulate_payment_processing(self, payment: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate payment processing (replace with actual payment gateway integration)"""
        import random
        
        # Simulate 95% success rate
        if random.random() < 0.95:
            transaction_id = f"txn_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
            return {
                'success': True,
                'transaction_id': transaction_id,
                'amount': payment['amount'],
                'timestamp': datetime.now().isoformat()
            }
        else:
            error_messages = [
                'Insufficient funds',
                'Payment method expired',
                'Network error',
                'Recipient account not found'
            ]
            return {
                'success': False,
                'error': random.choice(error_messages)
            }
    
    def record_payment_history(self, payment: Dict[str, Any], result: Dict[str, Any]):
        """Record payment in history"""
        history_record = {
            'payment_id': payment['id'],
            'username': payment['username'],
            'recipient': payment['recipient'],
            'amount': payment['amount'],
            'description': payment['description'],
            'category': payment['category'],
            'transaction_id': result.get('transaction_id'),
            'status': 'completed' if result['success'] else 'failed',
            'error': result.get('error'),
            'processed_at': datetime.now().isoformat(),
            'payment_count': payment['payment_count']
        }
        
        try:
            with open(self.payment_history_file, 'r') as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []
        
        history.append(history_record)
        
        # Keep only last 1000 records
        history = history[-1000:]
        
        with open(self.payment_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_payment_history(self, username: str = None, payment_id: str = None) -> List[Dict[str, Any]]:
        """Get payment history"""
        try:
            with open(self.payment_history_file, 'r') as f:
                history = json.load(f)
            
            if username:
                history = [h for h in history if h.get('username') == username]
            
            if payment_id:
                history = [h for h in history if h.get('payment_id') == payment_id]
            
            return sorted(history, key=lambda x: x['processed_at'], reverse=True)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def create_reminder(self, reminder_data: Dict[str, Any]) -> str:
        """Create a payment reminder"""
        reminder_id = str(uuid.uuid4())
        
        reminder = {
            'id': reminder_id,
            'username': reminder_data['username'],
            'type': reminder_data.get('type', 'payment_due'),
            'message': reminder_data['message'],
            'payment_id': reminder_data.get('payment_id'),
            'due_date': reminder_data.get('due_date'),
            'priority': reminder_data.get('priority', 'medium'),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'read': False,
            'action_taken': False
        }
        
        try:
            with open(self.reminders_file, 'r') as f:
                reminders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            reminders = []
        
        reminders.append(reminder)
        
        with open(self.reminders_file, 'w') as f:
            json.dump(reminders, f, indent=2)
        
        return reminder_id
    
    def get_reminders(self, username: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get reminders for a user"""
        try:
            with open(self.reminders_file, 'r') as f:
                reminders = json.load(f)
            
            user_reminders = [r for r in reminders if r.get('username') == username]
            
            if unread_only:
                user_reminders = [r for r in user_reminders if not r.get('read', False)]
            
            return sorted(user_reminders, key=lambda x: x['created_at'], reverse=True)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def mark_reminder_read(self, reminder_id: str) -> bool:
        """Mark a reminder as read"""
        try:
            with open(self.reminders_file, 'r') as f:
                reminders = json.load(f)
            
            for reminder in reminders:
                if reminder['id'] == reminder_id:
                    reminder['read'] = True
                    reminder['read_at'] = datetime.now().isoformat()
                    break
            
            with open(self.reminders_file, 'w') as f:
                json.dump(reminders, f, indent=2)
            
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False
    
    def schedule_payment_reminders(self, payment: Dict[str, Any]):
        """Schedule reminders for a payment"""
        if not SCHEDULER_AVAILABLE:
            return
        
        next_payment = datetime.fromisoformat(payment['next_payment_date'])
        reminder_days = payment.get('reminder_days', [1, 3])
        
        for days_before in reminder_days:
            reminder_date = next_payment - timedelta(days=days_before)
            
            if reminder_date > datetime.now():
                job_id = f"reminder_{payment['id']}_{days_before}d"
                
                try:
                    self.scheduler.add_job(
                        func=self.send_payment_reminder,
                        trigger='date',
                        run_date=reminder_date,
                        args=[payment['id'], days_before],
                        id=job_id,
                        replace_existing=True
                    )
                except Exception as e:
                    st.error(f"Error scheduling reminder: {e}")
    
    def schedule_automatic_payment(self, payment: Dict[str, Any]):
        """Schedule automatic payment"""
        if not SCHEDULER_AVAILABLE or not payment.get('auto_pay'):
            return
        
        next_payment = datetime.fromisoformat(payment['next_payment_date'])
        
        if next_payment > datetime.now():
            job_id = f"payment_{payment['id']}"
            
            try:
                self.scheduler.add_job(
                    func=self.process_payment,
                    trigger='date',
                    run_date=next_payment,
                    args=[payment['id']],
                    id=job_id,
                    replace_existing=True
                )
            except Exception as e:
                st.error(f"Error scheduling automatic payment: {e}")
    
    def send_payment_reminder(self, payment_id: str, days_before: int):
        """Send payment reminder"""
        payments = self.load_recurring_payments()
        
        for payment in payments:
            if payment['id'] == payment_id:
                message = f"Reminder: Your recurring payment of ${payment['amount']:.2f} to {payment['recipient']} is due in {days_before} day(s)"
                
                self.create_reminder({
                    'username': payment['username'],
                    'type': 'payment_reminder',
                    'message': message,
                    'payment_id': payment_id,
                    'due_date': payment['next_payment_date'],
                    'priority': 'medium' if days_before > 1 else 'high'
                })
                break
    
    def get_upcoming_payments(self, username: str, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming payments for a user"""
        payments = self.load_recurring_payments(username)
        upcoming = []
        
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        for payment in payments:
            if payment['status'] == 'active':
                next_payment = datetime.fromisoformat(payment['next_payment_date'])
                if next_payment <= cutoff_date:
                    payment['days_until_due'] = (next_payment - datetime.now()).days
                    upcoming.append(payment)
        
        return sorted(upcoming, key=lambda x: x['next_payment_date'])
    
    def get_payment_statistics(self, username: str) -> Dict[str, Any]:
        """Get payment statistics for a user"""
        payments = self.load_recurring_payments(username)
        history = self.get_payment_history(username)
        
        stats = {
            'total_recurring_payments': len(payments),
            'active_payments': len([p for p in payments if p['status'] == 'active']),
            'suspended_payments': len([p for p in payments if p['status'] == 'suspended']),
            'completed_payments': len([p for p in payments if p['status'] == 'completed']),
            'total_amount_scheduled': sum(p['amount'] for p in payments if p['status'] == 'active'),
            'total_paid_this_month': 0,
            'successful_payments': len([h for h in history if h['status'] == 'completed']),
            'failed_payments': len([h for h in history if h['status'] == 'failed']),
            'payment_categories': {}
        }
        
        # Calculate monthly payments
        current_month = datetime.now().replace(day=1)
        monthly_history = [
            h for h in history 
            if datetime.fromisoformat(h['processed_at']) >= current_month
        ]
        stats['total_paid_this_month'] = sum(
            h['amount'] for h in monthly_history if h['status'] == 'completed'
        )
        
        # Category breakdown
        category_amounts = {}
        for payment in payments:
            if payment['status'] == 'active':
                category = payment.get('category', 'Other')
                category_amounts[category] = category_amounts.get(category, 0) + payment['amount']
        stats['payment_categories'] = category_amounts
        
        return stats
    
    def export_payment_data(self, username: str, format: str = 'json') -> Dict[str, Any]:
        """Export payment data for a user"""
        payments = self.load_recurring_payments(username)
        history = self.get_payment_history(username)
        
        export_data = {
            'recurring_payments': payments,
            'payment_history': history,
            'export_date': datetime.now().isoformat(),
            'username': username
        }
        
        if format == 'csv':
            # Convert to CSV format
            payments_df = pd.DataFrame(payments)
            history_df = pd.DataFrame(history)
            
            return {
                'payments_csv': payments_df.to_csv(index=False),
                'history_csv': history_df.to_csv(index=False)
            }
        
        return export_data
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """Clean up old payment data"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean up payment history
        try:
            with open(self.payment_history_file, 'r') as f:
                history = json.load(f)
            
            filtered_history = [
                h for h in history 
                if datetime.fromisoformat(h['processed_at']) > cutoff_date
            ]
            
            with open(self.payment_history_file, 'w') as f:
                json.dump(filtered_history, f, indent=2)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Clean up old reminders
        try:
            with open(self.reminders_file, 'r') as f:
                reminders = json.load(f)
            
            filtered_reminders = [
                r for r in reminders 
                if datetime.fromisoformat(r['created_at']) > cutoff_date
            ]
            
            with open(self.reminders_file, 'w') as f:
                json.dump(filtered_reminders, f, indent=2)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

def get_payment_templates() -> List[Dict[str, Any]]:
    """Get common payment templates"""
    return [
        {
            'name': 'Monthly Rent',
            'category': 'Bills & Utilities',
            'frequency': 'monthly',
            'description': 'Monthly rent payment',
            'reminder_days': [3, 1]
        },
        {
            'name': 'Electricity Bill',
            'category': 'Bills & Utilities',
            'frequency': 'monthly',
            'description': 'Monthly electricity bill',
            'reminder_days': [5, 2]
        },
        {
            'name': 'Internet Bill',
            'category': 'Bills & Utilities',
            'frequency': 'monthly',
            'description': 'Monthly internet service',
            'reminder_days': [3, 1]
        },
        {
            'name': 'Car Insurance',
            'category': 'Transportation',
            'frequency': 'monthly',
            'description': 'Monthly car insurance premium',
            'reminder_days': [7, 3, 1]
        },
        {
            'name': 'Gym Membership',
            'category': 'Health & Fitness',
            'frequency': 'monthly',
            'description': 'Monthly gym membership fee',
            'reminder_days': [2]
        },
        {
            'name': 'Netflix Subscription',
            'category': 'Entertainment',
            'frequency': 'monthly',
            'description': 'Monthly Netflix subscription',
            'reminder_days': [1]
        },
        {
            'name': 'Loan Payment',
            'category': 'Bills & Utilities',
            'frequency': 'monthly',
            'description': 'Monthly loan payment',
            'reminder_days': [5, 3, 1]
        }
    ]

def simulate_payment_processing_for_demo():
    """Simulate payment processing for demonstration"""
    manager = RecurringPaymentManager()
    
    # Process any due payments
    all_payments = manager.load_recurring_payments()
    
    for payment in all_payments:
        if payment['status'] == 'active':
            next_payment = datetime.fromisoformat(payment['next_payment_date'])
            if next_payment <= datetime.now():
                result = manager.process_payment(payment['id'])
                if result['success']:
                    st.success(f"Processed payment: ${payment['amount']:.2f} to {payment['recipient']}")
                else:
                    st.error(f"Failed to process payment to {payment['recipient']}: {result['error']}")

def get_smart_payment_suggestions(username: str) -> List[Dict[str, Any]]:
    """Get smart suggestions for recurring payments based on transaction history"""
    # This would analyze transaction history to suggest recurring payments
    # For now, return some common suggestions
    
    suggestions = [
        {
            'type': 'detected_pattern',
            'title': 'Recurring Grocery Spending',
            'description': 'You spend approximately $150 weekly on groceries. Consider setting up a budget alert.',
            'suggested_amount': 150,
            'suggested_frequency': 'weekly',
            'category': 'Groceries',
            'confidence': 0.85
        },
        {
            'type': 'bill_reminder',
            'title': 'Utility Bill Pattern',
            'description': 'Set up automatic reminders for your monthly utility bills.',
            'suggested_amount': 120,
            'suggested_frequency': 'monthly',
            'category': 'Bills & Utilities',
            'confidence': 0.75
        }
    ]
    
    return suggestions