def subscriptions_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    from datetime import datetime, timedelta
    import matplotlib.pyplot as plt
    import numpy as np
    import uuid
    import calendar
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Subscriptions Manager</h1>", unsafe_allow_html=True)
    
    # Load user data
    def load_users():
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                return json.load(f)
        return {}
    
    # Load subscriptions
    def load_subscriptions():
        if os.path.exists('subscriptions.json'):
            with open('subscriptions.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_subscriptions(subscriptions):
        with open('subscriptions.json', 'w') as f:
            json.dump(subscriptions, f, indent=4)
    
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
    def add_transaction(sender, recipient, amount, transaction_type, note="", category="Subscription"):
        users = load_users()
        
        # Check if sender exists and has sufficient balance
        if sender not in users or users[sender]['balance'] < amount:
            return False, "Insufficient balance or invalid sender"
        
        # Check if recipient exists
        if recipient not in users and recipient != "Subscription":
            return False, "Invalid recipient"
        
        # Update balances
        users[sender]['balance'] -= amount
        
        if recipient in users:
            users[recipient]['balance'] += amount
        
        # Save updated user data
        data_dir = "data"
        users_file = os.path.join(data_dir, "users.json")
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=4)
        
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
    
    # Initialize subscriptions if not exists
    if 'subscriptions' not in st.session_state:
        subscriptions = load_subscriptions()
        if st.session_state.current_user not in subscriptions:
            subscriptions[st.session_state.current_user] = []
        st.session_state.subscriptions = subscriptions
    
    # Get subscription categories
    subscription_categories = [
        "Streaming", "Music", "Gaming", "Cloud Storage", "Software", 
        "News & Magazines", "Fitness", "Food Delivery", "Utilities", "Other"
    ]
    
    # Get billing frequencies
    billing_frequencies = [
        "Monthly", "Quarterly", "Semi-Annual", "Annual"
    ]
    
    # Tabs for Add Subscription and View Subscriptions
    tab1, tab2, tab3 = st.tabs(["Add Subscription", "View Subscriptions", "Subscription Insights"])
    
    with tab1:
        st.markdown("### Add New Subscription")
        
        # Form for adding new subscription
        with st.form("subscription_form"):
            subscription_name = st.text_input("Subscription Name", placeholder="e.g., Netflix, Spotify, Amazon Prime")
            subscription_amount = st.number_input("Amount (₹)", min_value=1.0, value=199.0)
            subscription_category = st.selectbox("Category", subscription_categories)
            billing_frequency = st.selectbox("Billing Frequency", billing_frequencies)
            
            # Calculate next billing date
            today = datetime.now().date()
            next_billing_date = st.date_input("Next Billing Date", min_value=today, value=today + timedelta(days=30))
            
            # Auto-pay option
            auto_pay = st.checkbox("Enable Auto-Pay", value=True)
            
            # Reminder days
            reminder_days = st.slider("Remind me before (days)", min_value=1, max_value=7, value=3)
            
            submit_button = st.form_submit_button("Add Subscription")
            
            if submit_button:
                if not subscription_name:
                    st.error("Please enter a subscription name")
                else:
                    # Create new subscription
                    new_subscription = {
                        "id": str(uuid.uuid4()),
                        "name": subscription_name,
                        "amount": subscription_amount,
                        "category": subscription_category,
                        "billing_frequency": billing_frequency,
                        "next_billing_date": next_billing_date.strftime('%Y-%m-%d'),
                        "auto_pay": auto_pay,
                        "reminder_days": reminder_days,
                        "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "active": True
                    }
                    
                    # Add to user's subscriptions
                    user_subscriptions = st.session_state.subscriptions.get(st.session_state.current_user, [])
                    user_subscriptions.append(new_subscription)
                    st.session_state.subscriptions[st.session_state.current_user] = user_subscriptions
                    save_subscriptions(st.session_state.subscriptions)
                    
                    st.success(f"Subscription '{subscription_name}' added successfully!")
                    st.rerun()
    
    with tab2:
        st.markdown("### Your Subscriptions")
        
        # Get user's subscriptions
        user_subscriptions = st.session_state.subscriptions.get(st.session_state.current_user, [])
        
        if not user_subscriptions:
            st.info("You haven't added any subscriptions yet. Go to 'Add Subscription' tab to get started.")
        else:
            # Filter options
            show_inactive = st.checkbox("Show inactive subscriptions", value=False)
            
            # Filter subscriptions based on active status
            filtered_subscriptions = [s for s in user_subscriptions if s['active'] or show_inactive]
            
            if not filtered_subscriptions:
                st.info("No subscriptions found with the current filter settings.")
            else:
                # Calculate total monthly cost
                monthly_cost = 0
                for sub in filtered_subscriptions:
                    if sub['active']:
                        amount = sub['amount']
                        if sub['billing_frequency'] == "Quarterly":
                            monthly_cost += amount / 3
                        elif sub['billing_frequency'] == "Semi-Annual":
                            monthly_cost += amount / 6
                        elif sub['billing_frequency'] == "Annual":
                            monthly_cost += amount / 12
                        else:  # Monthly
                            monthly_cost += amount
                
                st.markdown(f"### Total Monthly Cost: ₹{monthly_cost:.2f}")
                
                # Display subscriptions as cards
                for i, subscription in enumerate(filtered_subscriptions):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # Status indicator
                            status = "🟢 Active" if subscription['active'] else "⚪ Inactive"
                            
                            # Calculate days until next billing
                            next_billing = datetime.strptime(subscription['next_billing_date'], '%Y-%m-%d').date()
                            days_until_billing = (next_billing - datetime.now().date()).days
                            
                            # Display subscription info
                            st.markdown(f"### {subscription['name']} ({subscription['category']}) {status}")
                            st.markdown(f"**Amount:** ₹{subscription['amount']:.2f} ({subscription['billing_frequency']})")
                            
                            if days_until_billing <= 0:
                                st.markdown(f"**Next Billing:** {subscription['next_billing_date']} (Due today!)")
                            else:
                                st.markdown(f"**Next Billing:** {subscription['next_billing_date']} ({days_until_billing} days)")
                            
                            # Show reminder and auto-pay status
                            st.markdown(f"**Reminder:** {subscription['reminder_days']} days before billing")
                            st.markdown(f"**Auto-Pay:** {'Enabled' if subscription['auto_pay'] else 'Disabled'}")
                        
                        with col2:
                            # Pay now button
                            if subscription['active']:
                                if st.button(f"Pay Now", key=f"pay_{i}"):
                                    # Get user balance
                                    users = load_users()
                                    current_user = users[st.session_state.current_user]
                                    
                                    if current_user['balance'] >= subscription['amount']:
                                        # Process payment
                                        success, message = add_transaction(
                                            st.session_state.current_user,
                                            "Subscription",
                                            subscription['amount'],
                                            "subscription_payment",
                                            f"Payment for {subscription['name']}",
                                            subscription['category']
                                        )
                                        
                                        if success:
                                            # Update next billing date based on frequency
                                            next_date = next_billing
                                            if subscription['billing_frequency'] == "Monthly":
                                                next_date = next_date + timedelta(days=30)
                                            elif subscription['billing_frequency'] == "Quarterly":
                                                next_date = next_date + timedelta(days=90)
                                            elif subscription['billing_frequency'] == "Semi-Annual":
                                                next_date = next_date + timedelta(days=182)
                                            else:  # Annual
                                                next_date = next_date + timedelta(days=365)
                                            
                                            # Update subscription
                                            for sub in user_subscriptions:
                                                if sub['id'] == subscription['id']:
                                                    sub['next_billing_date'] = next_date.strftime('%Y-%m-%d')
                                                    break
                                            
                                            # Save updated subscriptions
                                            st.session_state.subscriptions[st.session_state.current_user] = user_subscriptions
                                            save_subscriptions(st.session_state.subscriptions)
                                            
                                            st.success(f"Payment of ₹{subscription['amount']:.2f} for {subscription['name']} successful!")
                                            st.rerun()
                                        else:
                                            st.error(message)
                                    else:
                                        st.error("Insufficient balance")
                            
                            # Toggle active status button
                            button_text = "Deactivate" if subscription['active'] else "Activate"
                            if st.button(button_text, key=f"toggle_{i}"):
                                # Update subscription status
                                for sub in user_subscriptions:
                                    if sub['id'] == subscription['id']:
                                        sub['active'] = not sub['active']
                                        break
                                
                                # Save updated subscriptions
                                st.session_state.subscriptions[st.session_state.current_user] = user_subscriptions
                                save_subscriptions(st.session_state.subscriptions)
                                
                                status_text = "deactivated" if subscription['active'] else "activated"
                                st.success(f"Subscription '{subscription['name']}' {status_text} successfully!")
                                st.rerun()
                            
                            # Delete subscription button
                            if st.button(f"Delete", key=f"delete_{i}"):
                                # Remove subscription
                                updated_subscriptions = [s for s in user_subscriptions if s['id'] != subscription['id']]
                                st.session_state.subscriptions[st.session_state.current_user] = updated_subscriptions
                                save_subscriptions(st.session_state.subscriptions)
                                
                                st.success(f"Subscription '{subscription['name']}' deleted successfully!")
                                st.rerun()
                        
                        st.markdown("---")
    
    with tab3:
        st.markdown("### Subscription Insights")
        
        # Get user's active subscriptions
        user_subscriptions = st.session_state.subscriptions.get(st.session_state.current_user, [])
        active_subscriptions = [s for s in user_subscriptions if s['active']]
        
        if not active_subscriptions:
            st.info("You don't have any active subscriptions to analyze.")
        else:
            # Calculate monthly costs by category
            category_costs = {}
            for sub in active_subscriptions:
                category = sub['category']
                amount = sub['amount']
                
                # Convert to monthly amount
                if sub['billing_frequency'] == "Quarterly":
                    monthly_amount = amount / 3
                elif sub['billing_frequency'] == "Semi-Annual":
                    monthly_amount = amount / 6
                elif sub['billing_frequency'] == "Annual":
                    monthly_amount = amount / 12
                else:  # Monthly
                    monthly_amount = amount
                
                if category in category_costs:
                    category_costs[category] += monthly_amount
                else:
                    category_costs[category] = monthly_amount
            
            # Create pie chart of subscription costs by category
            fig, ax = plt.subplots(figsize=(10, 6))
            
            categories = list(category_costs.keys())
            costs = list(category_costs.values())
            
            # Color map
            colors = plt.cm.tab10(np.arange(len(categories)) % 10)
            
            wedges, texts, autotexts = ax.pie(
                costs, 
                labels=categories,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            ax.axis('equal')
            plt.setp(autotexts, size=10, weight="bold")
            plt.setp(texts, size=12)
            plt.title("Monthly Subscription Costs by Category", size=16)
            
            st.pyplot(fig)
            
            # Monthly subscription calendar
            st.markdown("### Upcoming Subscription Payments")
            
            # Get current month and year
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Create calendar data
            cal_data = {}
            for day in range(1, 32):  # Max days in a month
                try:
                    # Check if this is a valid day in the current month
                    date_obj = datetime(current_year, current_month, day).date()
                    cal_data[date_obj] = []
                except ValueError:
                    # Skip invalid dates (e.g., Feb 30)
                    continue
            
            # Add subscriptions to calendar
            for sub in active_subscriptions:
                next_billing = datetime.strptime(sub['next_billing_date'], '%Y-%m-%d').date()
                
                # Only show payments in current month
                if next_billing.month == current_month and next_billing.year == current_year:
                    if next_billing in cal_data:
                        cal_data[next_billing].append({
                            "name": sub['name'],
                            "amount": sub['amount']
                        })
            
            # Display calendar
            month_name = calendar.month_name[current_month]
            st.markdown(f"#### {month_name} {current_year}")
            
            # Create calendar grid
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            
            # Get the first day of the month and the number of days
            first_day = datetime(current_year, current_month, 1)
            first_weekday = first_day.weekday()  # 0 is Monday, 6 is Sunday
            _, num_days = calendar.monthrange(current_year, current_month)
            
            # Create calendar rows
            rows = []
            week = [None] * first_weekday + list(range(1, 8 - first_weekday))
            rows.append(week)
            
            day = week[-1] + 1
            while day <= num_days:
                week = []
                for _ in range(7):
                    if day <= num_days:
                        week.append(day)
                        day += 1
                    else:
                        week.append(None)
                rows.append(week)
            
            # Display calendar
            st.markdown("<style>\n.calendar-day {\n    border: 1px solid #ddd;\n    padding: 10px;\n    min-height: 80px;\n    background-color: #f9f9f9;\n}\n.calendar-day.today {\n    background-color: #e6f7ff;\n    border: 2px solid #1890ff;\n}\n.calendar-day.has-payments {\n    background-color: #f6ffed;\n}\n.payment-item {\n    margin-bottom: 5px;\n    font-size: 12px;\n}\n</style>", unsafe_allow_html=True)
            
            # Display day headers
            cols = st.columns(7)
            for i, day_name in enumerate(days):
                with cols[i]:
                    st.markdown(f"<div style='text-align: center; font-weight: bold;'>{day_name}</div>", unsafe_allow_html=True)
            
            # Display calendar days
            today = datetime.now().date()
            
            for week in rows:
                cols = st.columns(7)
                for i, day in enumerate(week):
                    with cols[i]:
                        if day is not None:
                            date_obj = datetime(current_year, current_month, day).date()
                            payments = cal_data.get(date_obj, [])
                            
                            # Determine cell class
                            cell_class = "calendar-day"
                            if date_obj == today:
                                cell_class += " today"
                            if payments:
                                cell_class += " has-payments"
                            
                            # Start cell div
                            st.markdown(f"<div class='{cell_class}'>", unsafe_allow_html=True)
                            
                            # Day number
                            st.markdown(f"<div style='font-weight: bold;'>{day}</div>", unsafe_allow_html=True)
                            
                            # Payments for this day
                            for payment in payments:
                                st.markdown(f"<div class='payment-item'>{payment['name']}: ₹{payment['amount']:.2f}</div>", unsafe_allow_html=True)
                            
                            # End cell div
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            # Empty cell
                            st.markdown("<div class='calendar-day'></div>", unsafe_allow_html=True)
            
            # Monthly and annual totals
            total_monthly = sum(category_costs.values())
            total_annual = total_monthly * 12
            
            st.markdown("---")
            st.markdown(f"**Total Monthly Subscription Cost:** ₹{total_monthly:.2f}")
            st.markdown(f"**Projected Annual Subscription Cost:** ₹{total_annual:.2f}")
            
            # Subscription optimization suggestions
            st.markdown("### Optimization Suggestions")
            
            # Check for similar category subscriptions
            category_counts = {}
            for sub in active_subscriptions:
                category = sub['category']
                if category in category_counts:
                    category_counts[category] += 1
                else:
                    category_counts[category] = 1
            
            # Find categories with multiple subscriptions
            duplicate_categories = {k: v for k, v in category_counts.items() if v > 1}
            
            if duplicate_categories:
                st.markdown("#### Potential Duplicate Subscriptions")
                for category, count in duplicate_categories.items():
                    category_subs = [s for s in active_subscriptions if s['category'] == category]
                    st.markdown(f"**{category}** ({count} subscriptions):")
                    for sub in category_subs:
                        st.markdown(f"- {sub['name']}: ₹{sub['amount']:.2f} ({sub['billing_frequency']})")
                    st.markdown("Consider consolidating these subscriptions to save money.")
            
            # Check for annual savings opportunities
            st.markdown("#### Annual Payment Savings Opportunities")
            monthly_subs = [s for s in active_subscriptions if s['billing_frequency'] == "Monthly" and s['amount'] >= 100]
            
            if monthly_subs:
                st.markdown("The following subscriptions might offer discounts if paid annually:")
                for sub in monthly_subs:
                    monthly_cost = sub['amount']
                    annual_cost = monthly_cost * 12
                    potential_annual_cost = annual_cost * 0.8  # Assuming 20% discount
                    potential_savings = annual_cost - potential_annual_cost
                    
                    st.markdown(f"- **{sub['name']}**: Current monthly cost: ₹{monthly_cost:.2f}")
                    st.markdown(f"  Potential annual savings: ₹{potential_savings:.2f} (if annual plan offers 20% discount)")
            else:
                st.markdown("No significant monthly subscriptions found that might benefit from annual payment.")
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()