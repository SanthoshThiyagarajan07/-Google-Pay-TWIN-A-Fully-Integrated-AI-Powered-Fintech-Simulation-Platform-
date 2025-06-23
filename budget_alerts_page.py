def budget_alerts_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    from datetime import datetime
    import matplotlib.pyplot as plt
    import numpy as np
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Budget Alerts</h1>", unsafe_allow_html=True)
    
    # Load user data
    def load_users():
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(users):
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
    
    # Load budget alerts
    def load_budget_alerts():
        if os.path.exists('budget_alerts.json'):
            with open('budget_alerts.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_budget_alerts(alerts):
        with open('budget_alerts.json', 'w') as f:
            json.dump(alerts, f, indent=4)
    
    # Load transactions
    def load_transactions():
        if os.path.exists('transactions.json'):
            with open('transactions.json', 'r') as f:
                return json.load(f)
        return []
    
    # Get spending by category for current month
    def get_monthly_spending_by_category(username):
        transactions = load_transactions()
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Filter transactions for current user and current month
        user_transactions = [t for t in transactions if t['sender'] == username and 
                            datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S').month == current_month and
                            datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S').year == current_year]
        
        # Group by category
        categories = {}
        for t in user_transactions:
            category = t.get('category', 'Other')
            if category in categories:
                categories[category] += t['amount']
            else:
                categories[category] = t['amount']
        
        return categories
    
    # Initialize budget alerts if not exists
    if 'budget_alerts' not in st.session_state:
        budget_alerts = load_budget_alerts()
        if st.session_state.current_user not in budget_alerts:
            budget_alerts[st.session_state.current_user] = {}
        st.session_state.budget_alerts = budget_alerts
    
    # Get available categories
    available_categories = [
        "Food & Dining", "Shopping", "Entertainment", "Transportation", 
        "Utilities", "Health", "Education", "Travel", "Groceries", "Other"
    ]
    
    # Tabs for Set Alerts and View Alerts
    tab1, tab2 = st.tabs(["Set Budget Alerts", "View & Manage Alerts"])
    
    with tab1:
        st.markdown("### Set New Budget Alert")
        
        # Form for setting new budget alert
        with st.form("budget_alert_form"):
            category = st.selectbox("Select Category", available_categories)
            limit = st.number_input("Monthly Budget Limit (₹)", min_value=1, value=1000)
            alert_percentage = st.slider("Alert when reached (%)", min_value=50, max_value=100, value=80, step=5)
            
            submit_button = st.form_submit_button("Set Budget Alert")
            
            if submit_button:
                user_alerts = st.session_state.budget_alerts.get(st.session_state.current_user, {})
                
                # Create or update alert
                user_alerts[category] = {
                    "limit": limit,
                    "alert_percentage": alert_percentage,
                    "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Save to session state and file
                st.session_state.budget_alerts[st.session_state.current_user] = user_alerts
                save_budget_alerts(st.session_state.budget_alerts)
                
                st.success(f"Budget alert set for {category}: ₹{limit} (Alert at {alert_percentage}%)")
    
    with tab2:
        st.markdown("### Your Budget Alerts")
        
        # Get user's alerts
        if isinstance(st.session_state.budget_alerts, dict):
            user_alerts = st.session_state.budget_alerts.get(st.session_state.current_user, {})
        else:
            user_alerts = {}
        
        if not user_alerts:
            st.info("You haven't set any budget alerts yet. Go to 'Set Budget Alerts' tab to create one.")
        else:
            # Get current spending by category
            current_spending = get_monthly_spending_by_category(st.session_state.current_user)
            
            # Create data for display
            alert_data = []
            for category, alert in user_alerts.items():
                spent = current_spending.get(category, 0)
                percentage_used = (spent / alert['limit']) * 100 if alert['limit'] > 0 else 0
                status = "🔴 Exceeded" if percentage_used > 100 else "🟠 Warning" if percentage_used >= alert['alert_percentage'] else "🟢 Good"
                
                alert_data.append({
                    "Category": category,
                    "Budget Limit": f"₹{alert['limit']:.2f}",
                    "Spent": f"₹{spent:.2f}",
                    "Used %": f"{percentage_used:.1f}%",
                    "Status": status,
                    "Alert At": f"{alert['alert_percentage']}%"
                })
            
            # Display as table
            if alert_data:
                df = pd.DataFrame(alert_data)
                st.dataframe(df, use_container_width=True)
                
                # Visualization
                st.markdown("### Budget Usage Visualization")
                
                # Prepare data for chart
                categories = [a["Category"] for a in alert_data]
                limits = [float(a["Budget Limit"].replace("₹", "")) for a in alert_data]
                spent = [float(a["Spent"].replace("₹", "")) for a in alert_data]
                
                # Create bar chart
                fig, ax = plt.subplots(figsize=(10, 6))
                x = np.arange(len(categories))
                width = 0.35
                
                ax.bar(x - width/2, limits, width, label='Budget Limit', color='#4285F4')
                ax.bar(x + width/2, spent, width, label='Spent', color='#EA4335')
                
                ax.set_xticks(x)
                ax.set_xticklabels(categories, rotation=45, ha='right')
                ax.legend()
                
                ax.set_ylabel('Amount (₹)')
                ax.set_title('Budget vs. Actual Spending by Category')
                
                plt.tight_layout()
                st.pyplot(fig)
                
                # Delete alert option
                st.markdown("### Remove Budget Alert")
                delete_category = st.selectbox("Select category to remove", list(user_alerts.keys()))
                if st.button("Delete Alert", use_container_width=True):
                    del st.session_state.budget_alerts[st.session_state.current_user][delete_category]
                    save_budget_alerts(st.session_state.budget_alerts)
                    st.success(f"Budget alert for {delete_category} removed successfully!")
                    st.rerun()
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()