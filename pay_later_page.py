def pay_later_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    from datetime import datetime, timedelta
    import uuid
    import matplotlib.pyplot as plt
    import numpy as np
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Pay Later</h1>", unsafe_allow_html=True)
    
    # Load user data
    def load_users():
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(users):
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
    
    # Load pay later data
    def load_pay_later():
        if os.path.exists('pay_later.json'):
            with open('pay_later.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_pay_later(pay_later_data):
        with open('pay_later.json', 'w') as f:
            json.dump(pay_later_data, f, indent=4)
    
    # Load transactions
    def load_transactions():
        data_dir = "data"
        transaction_file = os.path.join(data_dir, "transactions.json")
        if os.path.exists(transaction_file):
            with open(transaction_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_transactions(transactions):
        data_dir = "data"
        transaction_file = os.path.join(data_dir, "transactions.json")
        with open(transaction_file, 'w') as f:
            json.dump(transactions, f, indent=4)
    
    # Add transaction function
    def add_transaction(sender, recipient, amount, transaction_type, note="", category="Pay Later"):
        users = load_users()
        
        # Check if sender exists and has sufficient balance for non-pay-later transactions
        if transaction_type != 'pay_later' and sender != "Pay Later" and (sender not in users or users[sender]['balance'] < amount):
            return False, "Insufficient balance or invalid sender"
        
        # Check if recipient exists
        if recipient != "Pay Later" and recipient not in users:
            return False, "Invalid recipient"
        
        # Update balances for non-pay-later transactions
        if transaction_type != 'pay_later' and sender != "Pay Later":
            users[sender]['balance'] -= amount
        
        if recipient != "Pay Later" and transaction_type != 'pay_later_repayment':
            users[recipient]['balance'] += amount
        
        # Save updated user data
        save_users(users)
        
        # Create transaction record
        transactions = load_transactions()
        transaction = {
            'id': str(uuid.uuid4()),
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'type': transaction_type,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note': note,
            'category': category
        }
        transactions.append(transaction)
        save_transactions(transactions)
        
        return True, "Transaction successful"
    
    # Initialize pay later data if not exists
    if 'pay_later' not in st.session_state:
        pay_later_data = load_pay_later()
        if st.session_state.current_user not in pay_later_data:
            pay_later_data[st.session_state.current_user] = {
                "credit_limit": 5000,  # Default credit limit
                "available_credit": 5000,
                "total_due": 0,
                "transactions": []
            }
        st.session_state.pay_later = pay_later_data
    
    # Get user's pay later data
    user_pay_later = st.session_state.pay_later.get(st.session_state.current_user, {})
    
    # Calculate credit score based on transaction history
    def calculate_credit_score(username):
        transactions = load_transactions()
        user_transactions = [t for t in transactions if t['sender'] == username or t['recipient'] == username]
        
        # Base score
        score = 650
        
        if len(user_transactions) < 5:
            return score  # Not enough transaction history
        
        # Factors affecting score
        
        # 1. Payment history (on-time payments for pay later)
        pay_later_transactions = [t for t in user_transactions if t['type'] == 'pay_later']
        repayment_transactions = [t for t in user_transactions if t['type'] == 'pay_later_repayment']
        
        if pay_later_transactions:
            # Check if repayments were made on time
            on_time_payments = 0
            late_payments = 0
            
            for pl_tx in pay_later_transactions:
                # Find corresponding repayment
                repaid = False
                for rep_tx in repayment_transactions:
                    if pl_tx['id'] in rep_tx.get('note', ''):
                        # Check if repayment was within 30 days
                        pl_date = datetime.strptime(pl_tx['date'], '%Y-%m-%d %H:%M:%S')
                        rep_date = datetime.strptime(rep_tx['date'], '%Y-%m-%d %H:%M:%S')
                        
                        if (rep_date - pl_date).days <= 30:
                            on_time_payments += 1
                        else:
                            late_payments += 1
                        
                        repaid = True
                        break
                
                if not repaid and (datetime.now() - datetime.strptime(pl_tx['date'], '%Y-%m-%d %H:%M:%S')).days > 30:
                    late_payments += 1
            
            # Adjust score based on payment history
            if on_time_payments + late_payments > 0:
                payment_ratio = on_time_payments / (on_time_payments + late_payments)
                score += int(payment_ratio * 100)  # Up to 100 points for perfect payment history
                score -= late_payments * 30  # Penalty for late payments
        
        # 2. Credit utilization
        if user_pay_later.get("credit_limit", 0) > 0:
            utilization = user_pay_later.get("total_due", 0) / user_pay_later.get("credit_limit", 1) * 100
            
            if utilization <= 30:
                score += 50  # Good utilization (under 30%)
            elif utilization <= 50:
                score += 25  # Moderate utilization
            elif utilization <= 75:
                score -= 25  # High utilization
            else:
                score -= 50  # Very high utilization
        
        # 3. Length of credit history
        if pay_later_transactions:
            first_tx_date = min([datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S') for t in pay_later_transactions])
            history_months = (datetime.now() - first_tx_date).days / 30
            
            if history_months >= 12:
                score += 50  # 1+ year of history
            elif history_months >= 6:
                score += 25  # 6+ months of history
        
        # 4. Overall transaction volume
        total_transactions = len(user_transactions)
        if total_transactions >= 50:
            score += 50  # Very active user
        elif total_transactions >= 25:
            score += 25  # Moderately active user
        
        # Ensure score is within reasonable bounds
        score = max(300, min(score, 850))
        
        return score
    
    # Calculate user's credit score
    credit_score = calculate_credit_score(st.session_state.current_user)
    
    # Tabs for Pay Later options
    tab1, tab2, tab3 = st.tabs(["Make a Payment", "View & Repay", "Credit Overview"])
    
    with tab1:
        st.markdown("### Pay Now, Pay Later")
        
        # Display available credit
        st.markdown(f"**Available Credit:** ₹{user_pay_later.get('available_credit', 0):.2f}")
        st.markdown(f"**Total Due:** ₹{user_pay_later.get('total_due', 0):.2f}")
        
        # Form for making a pay later payment
        with st.form("pay_later_form"):
            # Get all users for recipient selection
            users = load_users()
            recipient_options = [user for user in users.keys() if user != st.session_state.current_user]
            
            recipient = st.selectbox("Recipient", recipient_options)
            amount = st.number_input("Amount (₹)", min_value=1.0, max_value=float(user_pay_later.get('available_credit', 0)), value=100.0)
            
            # Payment categories
            categories = [
                "Shopping", "Food & Dining", "Entertainment", "Travel", 
                "Utilities", "Education", "Health", "Other"
            ]
            category = st.selectbox("Category", categories)
            
            note = st.text_input("Note (optional)", placeholder="What's this payment for?")
            
            # Repayment options
            st.markdown("### Repayment Plan")
            repayment_options = ["Pay in 15 days", "Pay in 30 days", "Pay in 3 installments"]
            repayment_plan = st.selectbox("How would you like to repay?", repayment_options)
            
            # Calculate repayment details
            if repayment_plan == "Pay in 15 days":
                due_date = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
                installment_amount = amount
                installments = 1
            elif repayment_plan == "Pay in 30 days":
                due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                installment_amount = amount
                installments = 1
            else:  # 3 installments
                due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                installment_amount = amount / 3
                installments = 3
            
            st.markdown(f"**Due Date:** {due_date}")
            if installments > 1:
                st.markdown(f"**Installment Amount:** ₹{installment_amount:.2f} x {installments} installments")
            
            # Terms and conditions
            agree = st.checkbox("I agree to the terms and conditions of Pay Later service")
            
            submit_button = st.form_submit_button("Make Payment")
            
            if submit_button:
                if not agree:
                    st.error("Please agree to the terms and conditions")
                elif amount <= 0:
                    st.error("Please enter a valid amount")
                elif amount > user_pay_later.get('available_credit', 0):
                    st.error("Amount exceeds available credit")
                else:
                    # Process pay later transaction
                    success, message = add_transaction(
                        "Pay Later",
                        recipient,
                        amount,
                        "pay_later",
                        note,
                        category
                    )
                    
                    if success:
                        # Update pay later data
                        user_pay_later['available_credit'] -= amount
                        user_pay_later['total_due'] += amount
                        
                        # Add transaction to pay later records
                        pay_later_tx = {
                            "id": str(uuid.uuid4()),
                            "recipient": recipient,
                            "amount": amount,
                            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "due_date": due_date,
                            "category": category,
                            "note": note,
                            "repayment_plan": repayment_plan,
                            "installments": installments,
                            "installment_amount": installment_amount,
                            "installments_paid": 0,
                            "status": "pending"
                        }
                        
                        user_pay_later['transactions'].append(pay_later_tx)
                        
                        # Save updated pay later data
                        st.session_state.pay_later[st.session_state.current_user] = user_pay_later
                        save_pay_later(st.session_state.pay_later)
                        
                        st.success(f"Pay Later payment of ₹{amount:.2f} to {recipient} successful!")
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab2:
        st.markdown("### Your Pay Later Transactions")
        
        # Get user's pay later transactions
        pay_later_transactions = user_pay_later.get('transactions', [])
        
        if not pay_later_transactions:
            st.info("You don't have any Pay Later transactions yet.")
        else:
            # Filter options
            status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])
            
            # Filter transactions based on status
            if status_filter == "Pending":
                filtered_transactions = [t for t in pay_later_transactions if t['status'] == "pending"]
            elif status_filter == "Completed":
                filtered_transactions = [t for t in pay_later_transactions if t['status'] == "completed"]
            else:
                filtered_transactions = pay_later_transactions
            
            if not filtered_transactions:
                st.info(f"No {status_filter.lower()} Pay Later transactions found.")
            else:
                # Sort transactions by date (newest first)
                sorted_transactions = sorted(
                    filtered_transactions,
                    key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S'),
                    reverse=True
                )
                
                # Display transactions as cards
                for i, transaction in enumerate(sorted_transactions):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # Status indicator
                            status = "🟢 Completed" if transaction['status'] == "completed" else "🟠 Pending"
                            
                            # Calculate days until due
                            due_date = datetime.strptime(transaction['due_date'], '%Y-%m-%d').date()
                            days_until_due = (due_date - datetime.now().date()).days
                            
                            # Display transaction info
                            st.markdown(f"### Payment to {transaction['recipient']} {status}")
                            st.markdown(f"**Amount:** ₹{transaction['amount']:.2f} ({transaction['category']})")
                            st.markdown(f"**Date:** {transaction['date']}")
                            
                            if transaction['status'] == "pending":
                                if days_until_due < 0:
                                    st.markdown(f"**Due Date:** {transaction['due_date']} (Overdue by {abs(days_until_due)} days)")
                                else:
                                    st.markdown(f"**Due Date:** {transaction['due_date']} ({days_until_due} days remaining)")
                            
                            # Show repayment plan
                            if transaction['installments'] > 1:
                                st.markdown(f"**Repayment Plan:** ₹{transaction['installment_amount']:.2f} x {transaction['installments']} installments")
                                st.markdown(f"**Installments Paid:** {transaction['installments_paid']}/{transaction['installments']}")
                            else:
                                st.markdown(f"**Repayment Plan:** {transaction['repayment_plan']}")
                            
                            if transaction['note']:
                                st.markdown(f"**Note:** {transaction['note']}")
                        
                        with col2:
                            # Repay button for pending transactions
                            if transaction['status'] == "pending":
                                if st.button(f"Repay", key=f"repay_{i}"):
                                    st.session_state.selected_transaction = transaction
                                    st.session_state.show_repayment_form = True
                        
                        st.markdown("---")
            
            # Repayment form
            if hasattr(st.session_state, 'show_repayment_form') and st.session_state.show_repayment_form:
                st.markdown("### Repay Pay Later")
                selected_tx = st.session_state.selected_transaction
                
                with st.form("repayment_form"):
                    st.markdown(f"**Payment to:** {selected_tx['recipient']}")
                    st.markdown(f"**Original Amount:** ₹{selected_tx['amount']:.2f}")
                    
                    # Calculate remaining amount
                    if selected_tx['installments'] > 1:
                        remaining_installments = selected_tx['installments'] - selected_tx['installments_paid']
                        remaining_amount = selected_tx['installment_amount'] * remaining_installments
                    else:
                        remaining_amount = selected_tx['amount']
                    
                    st.markdown(f"**Remaining Amount:** ₹{remaining_amount:.2f}")
                    
                    # Get user balance
                    users = load_users()
                    current_user = users[st.session_state.current_user]
                    st.markdown(f"**Your Balance:** ₹{current_user['balance']:.2f}")
                    
                    # Repayment options
                    if selected_tx['installments'] > 1 and remaining_installments > 1:
                        repayment_options = ["Pay one installment", "Pay full amount"]
                        repayment_choice = st.radio("Repayment Option", repayment_options)
                        
                        if repayment_choice == "Pay one installment":
                            repayment_amount = selected_tx['installment_amount']
                        else:
                            repayment_amount = remaining_amount
                    else:
                        repayment_amount = remaining_amount
                    
                    st.markdown(f"**Repayment Amount:** ₹{repayment_amount:.2f}")
                    
                    submit_repayment = st.form_submit_button("Confirm Repayment")
                    
                    if submit_repayment:
                        if repayment_amount <= 0:
                            st.error("Invalid repayment amount")
                        elif repayment_amount > current_user['balance']:
                            st.error("Insufficient balance")
                        else:
                            # Process repayment transaction
                            success, message = add_transaction(
                                st.session_state.current_user,
                                "Pay Later",
                                repayment_amount,
                                "pay_later_repayment",
                                f"Repayment for transaction {selected_tx['id']}"
                            )
                            
                            if success:
                                # Update pay later data
                                for tx in user_pay_later['transactions']:
                                    if tx['id'] == selected_tx['id']:
                                        if tx['installments'] > 1:
                                            if repayment_amount >= remaining_amount:
                                                # Full repayment
                                                tx['installments_paid'] = tx['installments']
                                                tx['status'] = "completed"
                                            else:
                                                # Installment payment
                                                tx['installments_paid'] += 1
                                                if tx['installments_paid'] >= tx['installments']:
                                                    tx['status'] = "completed"
                                        else:
                                            # Single payment repayment
                                            tx['status'] = "completed"
                                        break
                                
                                # Update available credit and total due
                                user_pay_later['available_credit'] += repayment_amount
                                user_pay_later['total_due'] -= repayment_amount
                                
                                # Save updated pay later data
                                st.session_state.pay_later[st.session_state.current_user] = user_pay_later
                                save_pay_later(st.session_state.pay_later)
                                
                                st.success(f"Repayment of ₹{repayment_amount:.2f} successful!")
                                
                                # Reset form state
                                st.session_state.show_repayment_form = False
                                st.rerun()
                            else:
                                st.error(message)
                
                # Cancel button
                if st.button("Cancel"):
                    st.session_state.show_repayment_form = False
                    st.rerun()
    
    with tab3:
        st.markdown("### Your Credit Overview")
        
        # Display credit score
        st.markdown(f"### Credit Score: {credit_score}")
        
        # Credit score gauge
        fig, ax = plt.subplots(figsize=(10, 2))
        
        # Score ranges
        poor = (300, 580)
        fair = (580, 670)
        good = (670, 740)
        very_good = (740, 800)
        excellent = (800, 850)
        
        # Create gauge segments
        ax.barh(0, poor[1] - poor[0], left=poor[0], height=0.5, color='#EA4335')
        ax.barh(0, fair[1] - fair[0], left=fair[0], height=0.5, color='#FBBC05')
        ax.barh(0, good[1] - good[0], left=good[0], height=0.5, color='#34A853')
        ax.barh(0, very_good[1] - very_good[0], left=very_good[0], height=0.5, color='#4285F4')
        ax.barh(0, excellent[1] - excellent[0], left=excellent[0], height=0.5, color='#0F9D58')
        
        # Add score marker
        ax.plot(credit_score, 0, 'v', color='black', markersize=10)
        
        # Add labels
        ax.text(poor[0] + (poor[1] - poor[0])/2, -0.25, 'Poor', ha='center')
        ax.text(fair[0] + (fair[1] - fair[0])/2, -0.25, 'Fair', ha='center')
        ax.text(good[0] + (good[1] - good[0])/2, -0.25, 'Good', ha='center')
        ax.text(very_good[0] + (very_good[1] - very_good[0])/2, -0.25, 'Very Good', ha='center')
        ax.text(excellent[0] + (excellent[1] - excellent[0])/2, -0.25, 'Excellent', ha='center')
        
        # Add score text
        ax.text(credit_score, 0.75, f'{credit_score}', ha='center', fontweight='bold')
        
        # Configure plot
        ax.set_xlim(300, 850)
        ax.set_ylim(-0.5, 1)
        ax.set_yticks([])
        ax.set_xticks([300, 400, 500, 600, 700, 800, 850])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # Credit score interpretation
        if credit_score >= 800:
            st.success("Excellent: You have an exceptional credit score. You're likely to get approved for the best credit products and terms.")
        elif credit_score >= 740:
            st.success("Very Good: You have a very good credit score. You're likely to get approved for most credit products with favorable terms.")
        elif credit_score >= 670:
            st.info("Good: You have a good credit score. You're likely to get approved for most credit products with average terms.")
        elif credit_score >= 580:
            st.warning("Fair: You have a fair credit score. You may face higher interest rates or stricter terms.")
        else:
            st.error("Poor: You have a poor credit score. You may have difficulty getting approved for credit products.")
        
        # Credit limit and usage
        st.markdown("### Credit Limit and Usage")
        
        credit_limit = user_pay_later.get('credit_limit', 0)
        available_credit = user_pay_later.get('available_credit', 0)
        total_due = user_pay_later.get('total_due', 0)
        
        # Calculate utilization percentage
        utilization = (total_due / credit_limit * 100) if credit_limit > 0 else 0
        
        # Create credit usage chart
        fig, ax = plt.subplots(figsize=(10, 2))
        
        # Create bar segments
        ax.barh(0, credit_limit, height=0.5, color='#E8E8E8')
        ax.barh(0, total_due, height=0.5, color='#4285F4')
        
        # Add labels
        ax.text(0, -0.25, '₹0', ha='center')
        ax.text(credit_limit, -0.25, f'₹{credit_limit:.2f}', ha='center')
        ax.text(total_due/2, 0, f'₹{total_due:.2f} ({utilization:.1f}%)', ha='center', color='white' if total_due > credit_limit/3 else 'black')
        
        # Configure plot
        ax.set_xlim(0, credit_limit * 1.05)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        plt.tight_layout()
        
        st.pyplot(fig)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Credit Limit", f"₹{credit_limit:.2f}")
        with col2:
            st.metric("Available Credit", f"₹{available_credit:.2f}")
        with col3:
            st.metric("Total Due", f"₹{total_due:.2f}")
        
        # Credit utilization advice
        if utilization > 70:
            st.warning("Your credit utilization is high. Consider making a repayment to improve your credit score.")
        elif utilization > 30:
            st.info("Your credit utilization is moderate. For the best credit score, try to keep it below 30%.")
        else:
            st.success("Your credit utilization is low, which is good for your credit score.")
        
        # Payment history
        st.markdown("### Payment History")
        
        # Get completed transactions
        completed_transactions = [t for t in user_pay_later.get('transactions', []) if t['status'] == "completed"]
        
        if not completed_transactions:
            st.info("You don't have any completed Pay Later transactions yet.")
        else:
            # Calculate on-time vs late payments
            on_time = 0
            late = 0
            
            for tx in completed_transactions:
                due_date = datetime.strptime(tx['due_date'], '%Y-%m-%d').date()
                # Assuming the completion date is the current date for simplicity
                # In a real app, you would store the actual repayment date
                if datetime.now().date() <= due_date:
                    on_time += 1
                else:
                    late += 1
            
            total = on_time + late
            on_time_pct = (on_time / total * 100) if total > 0 else 0
            
            # Create payment history chart
            fig, ax = plt.subplots(figsize=(8, 4))
            
            labels = ['On-time', 'Late']
            sizes = [on_time, late]
            colors = ['#34A853', '#EA4335']
            explode = (0.1, 0)  # explode the 1st slice (On-time)
            
            wedges, texts, autotexts = ax.pie(
                sizes, 
                explode=explode, 
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                shadow=True
            )
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            plt.title("Payment History")
            
            st.pyplot(fig)
            
            # Payment history interpretation
            if on_time_pct >= 90:
                st.success(f"Excellent payment history! {on_time_pct:.1f}% of your payments were on time.")
            elif on_time_pct >= 80:
                st.info(f"Good payment history. {on_time_pct:.1f}% of your payments were on time.")
            else:
                st.warning(f"Your payment history needs improvement. Only {on_time_pct:.1f}% of your payments were on time.")
        
        # Credit limit increase eligibility
        st.markdown("### Credit Limit Increase")
        
        # Determine eligibility based on credit score and payment history
        eligible_for_increase = credit_score >= 700 and (on_time_pct >= 90 if hasattr(locals(), 'on_time_pct') else False)
        
        if eligible_for_increase:
            st.success("You're eligible for a credit limit increase!")
            
            # Calculate potential new limit
            potential_increase = min(credit_limit * 0.5, 10000)  # 50% increase, max 10,000 increase
            new_limit = credit_limit + potential_increase
            
            st.markdown(f"**Potential New Limit:** ₹{new_limit:.2f} (₹{potential_increase:.2f} increase)")
            
            if st.button("Request Limit Increase", use_container_width=True):
                # Update credit limit
                user_pay_later['credit_limit'] = new_limit
                user_pay_later['available_credit'] += potential_increase
                
                # Save updated pay later data
                st.session_state.pay_later[st.session_state.current_user] = user_pay_later
                save_pay_later(st.session_state.pay_later)
                
                st.success(f"Credit limit increased to ₹{new_limit:.2f}!")
                st.rerun()
        else:
            st.info("Continue building your credit history with on-time payments to become eligible for a credit limit increase.")
    
    # Navigation handled by main app