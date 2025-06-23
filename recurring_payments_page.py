import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
import calendar

# Import the RecurringPaymentManager
from recurring_payments import RecurringPaymentManager, get_payment_templates, get_smart_payment_suggestions

def recurring_payments_page(username):
    st.title("Recurring Payments & Reminders")
    
    # Initialize payment manager
    payment_manager = RecurringPaymentManager()
    
    # Create tabs
    tabs = st.tabs(["My Recurring Payments", "Create Payment", "Upcoming Payments", "Payment History", "Reminders"])
    
    # Tab 1: My Recurring Payments
    with tabs[0]:
        st.header("My Recurring Payments")
        
        # Get user's recurring payments
        payments = payment_manager.load_recurring_payments(username)
        
        if not payments:
            st.info("You don't have any recurring payments set up yet.")
            st.write("Create your first recurring payment in the 'Create Payment' tab.")
        else:
            # Filter options
            status_filter = st.selectbox(
                "Filter by status:", 
                ["All", "Active", "Suspended", "Cancelled", "Completed"],
                index=0
            )
            
            if status_filter != "All":
                payments = [p for p in payments if p.get('status', '').lower() == status_filter.lower()]
            
            # Sort options
            sort_by = st.selectbox(
                "Sort by:",
                ["Next payment date", "Amount (high to low)", "Amount (low to high)", "Recipient"],
                index=0
            )
            
            if sort_by == "Next payment date":
                payments = sorted(payments, key=lambda x: x.get('next_payment_date', '9999-12-31'))
            elif sort_by == "Amount (high to low)":
                payments = sorted(payments, key=lambda x: x.get('amount', 0), reverse=True)
            elif sort_by == "Amount (low to high)":
                payments = sorted(payments, key=lambda x: x.get('amount', 0))
            elif sort_by == "Recipient":
                payments = sorted(payments, key=lambda x: x.get('recipient', '').lower())
            
            # Display payments
            for payment in payments:
                with st.expander(f"**{payment.get('recipient')}** - ${payment.get('amount', 0):.2f} ({payment.get('frequency', 'monthly')})"): 
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Description:** {payment.get('description', 'N/A')}")
                        st.write(f"**Category:** {payment.get('category', 'N/A')}")
                        st.write(f"**Status:** {payment.get('status', 'active').capitalize()}")
                        st.write(f"**Payment method:** {payment.get('payment_method', 'Default')}")
                        st.write(f"**Auto-pay:** {'Enabled' if payment.get('auto_pay') else 'Disabled'}")
                    
                    with col2:
                        next_payment_date = datetime.fromisoformat(payment.get('next_payment_date', datetime.now().isoformat()))
                        days_until = (next_payment_date - datetime.now()).days
                        
                        st.write(f"**Next payment:** {next_payment_date.strftime('%b %d, %Y')}")
                        st.write(f"**Days until next payment:** {days_until}")
                        st.write(f"**Total paid:** ${payment.get('total_paid', 0):.2f}")
                        st.write(f"**Payment count:** {payment.get('payment_count', 0)}")
                        
                        if payment.get('end_date'):
                            end_date = datetime.fromisoformat(payment['end_date'])
                            st.write(f"**End date:** {end_date.strftime('%b %d, %Y')}")
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if payment.get('status') == 'active':
                            if st.button("Pay Now", key=f"pay_{payment['id']}"):
                                result = payment_manager.process_payment(payment['id'], manual=True)
                                if result['success']:
                                    st.success(f"Payment of ${payment['amount']:.2f} to {payment['recipient']} processed successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Payment failed: {result.get('error', 'Unknown error')}")
                    
                    with col2:
                        if payment.get('status') in ['active', 'suspended']:
                            if st.button("Edit", key=f"edit_{payment['id']}"):
                                st.session_state.edit_payment_id = payment['id']
                                st.session_state.active_tab = 1  # Switch to Create Payment tab
                                st.rerun()
                    
                    with col3:
                        if payment.get('status') == 'active':
                            if st.button("Cancel", key=f"cancel_{payment['id']}"):
                                if st.session_state.get(f"confirm_cancel_{payment['id']}"):
                                    result = payment_manager.cancel_recurring_payment(payment['id'])
                                    if result['success']:
                                        st.success("Recurring payment cancelled successfully!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to cancel payment: {result.get('error', 'Unknown error')}")
                                    st.session_state[f"confirm_cancel_{payment['id']}"] = False
                                else:
                                    st.session_state[f"confirm_cancel_{payment['id']}"] = True
                                    st.warning("Are you sure you want to cancel this recurring payment? Click 'Cancel' again to confirm.")
                        elif payment.get('status') == 'suspended':
                            if st.button("Reactivate", key=f"reactivate_{payment['id']}"):
                                result = payment_manager.update_recurring_payment(payment['id'], {'status': 'active', 'failed_attempts': 0})
                                if result['success']:
                                    st.success("Payment reactivated successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to reactivate payment: {result.get('error', 'Unknown error')}")
                    
                    with col4:
                        if st.button("View History", key=f"history_{payment['id']}"):
                            st.session_state.view_payment_history_id = payment['id']
                            st.session_state.active_tab = 3  # Switch to Payment History tab
                            st.rerun()
    
    # Tab 2: Create Payment
    with tabs[1]:
        st.header("Create Recurring Payment")
        
        # Check if we're editing an existing payment
        editing_payment = None
        if st.session_state.get('edit_payment_id'):
            payments = payment_manager.load_recurring_payments(username)
            for payment in payments:
                if payment['id'] == st.session_state.edit_payment_id:
                    editing_payment = payment
                    break
            
            if editing_payment:
                st.subheader(f"Editing payment to {editing_payment['recipient']}")
        
        # Templates for quick setup
        if not editing_payment:
            st.subheader("Quick Setup")
            templates = get_payment_templates()
            template_names = ["Custom Payment"] + [t['name'] for t in templates]
            selected_template = st.selectbox("Select a template or create custom payment:", template_names)
            
            template_data = {}
            if selected_template != "Custom Payment":
                for template in templates:
                    if template['name'] == selected_template:
                        template_data = template
                        break
        
        # Smart suggestions
        if not editing_payment and selected_template == "Custom Payment":
            st.subheader("Smart Suggestions")
            suggestions = get_smart_payment_suggestions(username)
            
            if suggestions:
                for i, suggestion in enumerate(suggestions):
                    with st.expander(f"{suggestion['title']} (Confidence: {suggestion['confidence']*100:.0f}%)"):
                        st.write(suggestion['description'])
                        st.write(f"Suggested amount: ${suggestion['suggested_amount']:.2f}")
                        st.write(f"Suggested frequency: {suggestion['suggested_frequency']}")
                        st.write(f"Category: {suggestion['category']}")
                        
                        if st.button("Use This Suggestion", key=f"use_suggestion_{i}"):
                            template_data = {
                                'description': suggestion['title'],
                                'amount': suggestion['suggested_amount'],
                                'frequency': suggestion['suggested_frequency'],
                                'category': suggestion['category']
                            }
            else:
                st.info("No smart suggestions available yet. Continue using more features to get personalized suggestions.")
        
        # Payment form
        with st.form("recurring_payment_form"):
            st.subheader("Payment Details")
            
            # Basic details
            recipient = st.text_input(
                "Recipient Name", 
                value=editing_payment.get('recipient', '') if editing_payment else template_data.get('recipient', '')
            )
            
            amount = st.number_input(
                "Amount ($)", 
                min_value=0.01, 
                max_value=100000.0, 
                value=float(editing_payment.get('amount', 0)) if editing_payment else float(template_data.get('amount', 0)) or 0.0,
                step=0.01,
                format="%.2f"
            )
            
            description = st.text_input(
                "Description", 
                value=editing_payment.get('description', '') if editing_payment else template_data.get('description', '')
            )
            
            # Category selection
            categories = [
                "Bills & Utilities", "Rent & Mortgage", "Food & Dining", "Shopping", 
                "Entertainment", "Transportation", "Health & Fitness", "Education", 
                "Travel", "Subscriptions", "Insurance", "Investments", "Other"
            ]
            
            category = st.selectbox(
                "Category", 
                categories, 
                index=categories.index(editing_payment.get('category', 'Bills & Utilities')) if editing_payment and editing_payment.get('category') in categories 
                else categories.index(template_data.get('category', 'Bills & Utilities')) if template_data.get('category') in categories 
                else 0
            )
            
            # Frequency and dates
            col1, col2 = st.columns(2)
            
            with col1:
                frequencies = ["daily", "weekly", "bi-weekly", "monthly", "quarterly", "yearly"]
                frequency = st.selectbox(
                    "Frequency", 
                    frequencies, 
                    index=frequencies.index(editing_payment.get('frequency', 'monthly')) if editing_payment and editing_payment.get('frequency') in frequencies 
                    else frequencies.index(template_data.get('frequency', 'monthly')) if template_data.get('frequency') in frequencies 
                    else 3  # Default to monthly
                )
            
            with col2:
                if editing_payment and editing_payment.get('next_payment_date'):
                    default_start = datetime.fromisoformat(editing_payment['next_payment_date'])
                else:
                    default_start = datetime.now() + timedelta(days=1)
                
                start_date = st.date_input(
                    "Start Date", 
                    value=default_start
                )
            
            # End date (optional)
            has_end_date = st.checkbox(
                "Set End Date", 
                value=True if editing_payment and editing_payment.get('end_date') else False
            )
            
            end_date = None
            if has_end_date:
                if editing_payment and editing_payment.get('end_date'):
                    default_end = datetime.fromisoformat(editing_payment['end_date'])
                else:
                    default_end = datetime.now() + timedelta(days=365)
                
                end_date = st.date_input(
                    "End Date", 
                    value=default_end,
                    min_value=start_date
                )
            
            # Payment method
            payment_methods = ["Default", "Credit Card", "Debit Card", "Bank Account", "UPI", "Wallet"]
            payment_method = st.selectbox(
                "Payment Method", 
                payment_methods, 
                index=payment_methods.index(editing_payment.get('payment_method', 'Default')) if editing_payment and editing_payment.get('payment_method') in payment_methods else 0
            )
            
            # Auto-pay and reminders
            col1, col2 = st.columns(2)
            
            with col1:
                auto_pay = st.checkbox(
                    "Enable Auto-Pay", 
                    value=editing_payment.get('auto_pay', False) if editing_payment else False
                )
            
            with col2:
                reminder_options = ["1 day before", "3 days before", "5 days before", "7 days before", "14 days before"]
                default_reminders = []
                
                if editing_payment and editing_payment.get('reminder_days'):
                    for day in editing_payment['reminder_days']:
                        option = f"{day} days before"
                        if option in reminder_options:
                            default_reminders.append(option)
                elif template_data.get('reminder_days'):
                    for day in template_data['reminder_days']:
                        option = f"{day} days before"
                        if option in reminder_options:
                            default_reminders.append(option)
                else:
                    default_reminders = ["3 days before", "1 day before"]
                
                reminders = st.multiselect(
                    "Payment Reminders", 
                    reminder_options,
                    default=default_reminders
                )
            
            # Tags (optional)
            tags = st.text_input(
                "Tags (comma separated)", 
                value=", ".join(editing_payment.get('tags', [])) if editing_payment else ""
            )
            
            # Submit button
            submit_text = "Update Payment" if editing_payment else "Create Payment"
            submitted = st.form_submit_button(submit_text)
            
            if submitted:
                if not recipient:
                    st.error("Recipient name is required")
                elif amount <= 0:
                    st.error("Amount must be greater than 0")
                else:
                    # Process reminder days
                    reminder_days = []
                    for reminder in reminders:
                        days = int(reminder.split(" ")[0])
                        reminder_days.append(days)
                    
                    # Process tags
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    
                    # Create payment data
                    payment_data = {
                        'username': username,
                        'recipient': recipient,
                        'amount': amount,
                        'description': description,
                        'frequency': frequency,
                        'start_date': datetime.combine(start_date, datetime.min.time()).isoformat(),
                        'category': category,
                        'payment_method': payment_method,
                        'auto_pay': auto_pay,
                        'reminder_days': reminder_days,
                        'tags': tag_list
                    }
                    
                    if has_end_date and end_date:
                        payment_data['end_date'] = datetime.combine(end_date, datetime.min.time()).isoformat()
                    
                    if editing_payment:
                        # Update existing payment
                        result = payment_manager.update_recurring_payment(editing_payment['id'], payment_data)
                        if result['success']:
                            st.success("Recurring payment updated successfully!")
                            st.session_state.pop('edit_payment_id', None)
                            st.rerun()
                        else:
                            st.error(f"Failed to update payment: {result.get('error', 'Unknown error')}")
                    else:
                        # Create new payment
                        result = payment_manager.create_recurring_payment(payment_data)
                        if result['success']:
                            st.success(f"Recurring payment created successfully! Next payment date: {datetime.fromisoformat(result['next_payment_date']).strftime('%b %d, %Y')}")
                            st.session_state.active_tab = 0  # Switch to My Recurring Payments tab
                            st.rerun()
                        else:
                            st.error(f"Failed to create payment: {result.get('error', 'Unknown error')}")
        
        # Cancel editing
        if editing_payment and st.button("Cancel Editing"):
            st.session_state.pop('edit_payment_id', None)
            st.rerun()
    
    # Tab 3: Upcoming Payments
    with tabs[2]:
        st.header("Upcoming Payments")
        
        # Time range selection
        days_ahead = st.slider("Show payments for the next", 7, 365, 30)
        
        # Get upcoming payments
        upcoming = payment_manager.get_upcoming_payments(username, days_ahead)
        
        if not upcoming:
            st.info(f"No upcoming payments in the next {days_ahead} days.")
        else:
            # Calendar view
            st.subheader("Calendar View")
            
            # Create a DataFrame for the calendar
            calendar_data = []
            for payment in upcoming:
                next_payment_date = datetime.fromisoformat(payment['next_payment_date'])
                calendar_data.append({
                    'Date': next_payment_date.date(),
                    'Recipient': payment['recipient'],
                    'Amount': payment['amount'],
                    'Description': payment.get('description', ''),
                    'Category': payment.get('category', 'Other')
                })
            
            calendar_df = pd.DataFrame(calendar_data)
            
            if not calendar_df.empty:
                # Group by date
                date_groups = calendar_df.groupby('Date')
                
                # Create a calendar-like display
                today = datetime.now().date()
                start_date = today
                end_date = today + timedelta(days=days_ahead)
                
                # Create month views
                current_date = start_date
                while current_date <= end_date:
                    month_start = current_date.replace(day=1)
                    if month_start.month == 12:
                        month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
                    else:
                        month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
                    
                    if month_end > end_date:
                        month_end = end_date
                    
                    st.subheader(month_start.strftime("%B %Y"))
                    
                    # Create calendar grid
                    month_calendar = calendar.monthcalendar(month_start.year, month_start.month)
                    
                    # Display weekday headers
                    cols = st.columns(7)
                    for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
                        cols[i].markdown(f"**{day}**")
                    
                    # Display calendar days
                    for week in month_calendar:
                        cols = st.columns(7)
                        for i, day in enumerate(week):
                            if day == 0:
                                cols[i].write("")
                            else:
                                date = month_start.replace(day=day)
                                
                                # Check if date is in range
                                if start_date <= date <= end_date:
                                    # Check if there are payments on this date
                                    if date in date_groups.groups:
                                        day_payments = date_groups.get_group(date)
                                        total = day_payments['Amount'].sum()
                                        
                                        # Highlight days with payments
                                        if date == today:
                                            cols[i].markdown(f"**{day}** 🔴 ${total:.2f}")
                                        else:
                                            cols[i].markdown(f"**{day}** 💰 ${total:.2f}")
                                        
                                        # Show payment details in expandable section
                                        with cols[i].expander("Details"):
                                            for _, payment in day_payments.iterrows():
                                                st.write(f"**{payment['Recipient']}**")
                                                st.write(f"${payment['Amount']:.2f} - {payment['Description']}")
                                    else:
                                        # Regular day display
                                        if date == today:
                                            cols[i].markdown(f"**{day}** 🔴")
                                        else:
                                            cols[i].write(str(day))
                                else:
                                    # Date out of range - gray out
                                    cols[i].markdown(f"<span style='color:gray'>{day}</span>", unsafe_allow_html=True)
                    
                    # Move to next month
                    current_date = month_end + timedelta(days=1)
            
            # List view
            st.subheader("List View")
            
            # Group by week
            weeks = {}
            current_date = datetime.now().date()
            for i in range(days_ahead // 7 + 1):
                week_start = current_date + timedelta(days=i*7)
                week_end = week_start + timedelta(days=6)
                if week_end > current_date + timedelta(days=days_ahead):
                    week_end = current_date + timedelta(days=days_ahead)
                
                week_payments = []
                for payment in upcoming:
                    payment_date = datetime.fromisoformat(payment['next_payment_date']).date()
                    if week_start <= payment_date <= week_end:
                        week_payments.append(payment)
                
                if week_payments:
                    weeks[f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}"] = week_payments
            
            # Display weeks
            for week_label, week_payments in weeks.items():
                with st.expander(f"**{week_label}** ({len(week_payments)} payments)"):
                    for payment in sorted(week_payments, key=lambda x: x['next_payment_date']):
                        payment_date = datetime.fromisoformat(payment['next_payment_date'])
                        days_until = (payment_date - datetime.now()).days
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**{payment['recipient']}**")
                            st.write(payment.get('description', ''))
                        
                        with col2:
                            st.write(f"**${payment['amount']:.2f}**")
                            st.write(f"{payment.get('category', 'Other')}")
                        
                        with col3:
                            st.write(f"**{payment_date.strftime('%b %d')}**")
                            if days_until == 0:
                                st.write("Today!")
                            elif days_until == 1:
                                st.write("Tomorrow!")
                            else:
                                st.write(f"In {days_until} days")
                        
                        # Quick action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Pay Now", key=f"list_pay_{payment['id']}"):
                                result = payment_manager.process_payment(payment['id'], manual=True)
                                if result['success']:
                                    st.success(f"Payment of ${payment['amount']:.2f} to {payment['recipient']} processed successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Payment failed: {result.get('error', 'Unknown error')}")
                        
                        with col2:
                            if st.button("Skip Once", key=f"skip_{payment['id']}"):
                                # Calculate next payment date after current one
                                next_date = payment_manager.calculate_next_payment_date(
                                    payment['next_payment_date'],
                                    payment['frequency']
                                )
                                
                                result = payment_manager.update_recurring_payment(
                                    payment['id'], 
                                    {'next_payment_date': next_date}
                                )
                                
                                if result['success']:
                                    st.success(f"Payment skipped. Next payment scheduled for {datetime.fromisoformat(next_date).strftime('%b %d, %Y')}")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to skip payment: {result.get('error', 'Unknown error')}")
                        
                        st.divider()
            
            # Payment statistics
            st.subheader("Payment Statistics")
            stats = payment_manager.get_payment_statistics(username)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Active Payments", stats['active_payments'])
                st.metric("Total Monthly Amount", f"${stats['total_amount_scheduled']:.2f}")
            
            with col2:
                st.metric("Paid This Month", f"${stats['total_paid_this_month']:.2f}")
                st.metric("Successful Payments", stats['successful_payments'])
            
            with col3:
                st.metric("Failed Payments", stats['failed_payments'])
                st.metric("Suspended Payments", stats['suspended_payments'])
            
            # Category breakdown
            if stats['payment_categories']:
                st.subheader("Category Breakdown")
                
                # Create pie chart
                categories = list(stats['payment_categories'].keys())
                amounts = list(stats['payment_categories'].values())
                
                fig = px.pie(
                    values=amounts,
                    names=categories,
                    title="Monthly Payments by Category",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Payment History
    with tabs[3]:
        st.header("Payment History")
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            filter_payment = None
            if st.session_state.get('view_payment_history_id'):
                payments = payment_manager.load_recurring_payments(username)
                for payment in payments:
                    if payment['id'] == st.session_state.view_payment_history_id:
                        filter_payment = payment
                        break
            
            if filter_payment:
                st.info(f"Viewing history for: {filter_payment['recipient']}")
                st.button("Clear Filter", on_click=lambda: st.session_state.pop('view_payment_history_id', None))
        
        with col2:
            status_filter = st.selectbox(
                "Filter by status:",
                ["All", "Completed", "Failed"],
                index=0
            )
        
        # Get payment history
        if filter_payment:
            history = payment_manager.get_payment_history(username, filter_payment['id'])
        else:
            history = payment_manager.get_payment_history(username)
        
        if status_filter != "All":
            history = [h for h in history if h.get('status', '').lower() == status_filter.lower()]
        
        if not history:
            st.info("No payment history found.")
        else:
            # Create DataFrame for easier manipulation
            history_df = pd.DataFrame(history)
            
            # Convert processed_at to datetime
            history_df['processed_at'] = pd.to_datetime(history_df['processed_at'])
            
            # Add month column for grouping
            history_df['month'] = history_df['processed_at'].dt.strftime('%Y-%m')
            
            # Group by month
            months = history_df['month'].unique()
            
            # Payment trends chart
            st.subheader("Payment Trends")
            
            # Prepare data for chart
            monthly_totals = history_df[history_df['status'] == 'completed'].groupby('month')['amount'].sum().reset_index()
            monthly_totals['month_date'] = pd.to_datetime(monthly_totals['month'] + '-01')
            monthly_totals = monthly_totals.sort_values('month_date')
            
            if not monthly_totals.empty:
                fig = px.line(
                    monthly_totals, 
                    x='month_date', 
                    y='amount',
                    title="Monthly Payment Totals",
                    labels={'month_date': 'Month', 'amount': 'Total Amount ($)'},
                    markers=True
                )
                
                fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Total Amount ($)",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Display payment history by month
            st.subheader("Payment Records")
            
            for month in sorted(months, reverse=True):
                month_history = history_df[history_df['month'] == month]
                month_date = pd.to_datetime(month + '-01')
                
                with st.expander(f"**{month_date.strftime('%B %Y')}** ({len(month_history)} payments)"):
                    for _, payment in month_history.iterrows():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**{payment['recipient']}**")
                            st.write(payment.get('description', ''))
                        
                        with col2:
                            amount_color = "green" if payment['status'] == 'completed' else "red"
                            st.markdown(f"<span style='color:{amount_color}'>**${payment['amount']:.2f}**</span>", unsafe_allow_html=True)
                            st.write(f"{payment.get('category', 'Other')}")
                        
                        with col3:
                            processed_at = pd.to_datetime(payment['processed_at'])
                            st.write(f"**{processed_at.strftime('%b %d, %Y')}**")
                            
                            status_color = "green" if payment['status'] == 'completed' else "red"
                            st.markdown(f"<span style='color:{status_color}'>{payment['status'].capitalize()}</span>", unsafe_allow_html=True)
                            
                            if payment['status'] == 'failed' and payment.get('error'):
                                st.write(f"Error: {payment['error']}")
                        
                        st.divider()
    
    # Tab 5: Reminders
    with tabs[4]:
        st.header("Payment Reminders")
        
        # Get reminders
        reminders = payment_manager.get_reminders(username)
        
        # Filter options
        show_read = st.checkbox("Show read reminders", value=False)
        
        if not show_read:
            reminders = [r for r in reminders if not r.get('read', False)]
        
        if not reminders:
            st.info("No reminders to display.")
        else:
            # Group reminders by priority
            high_priority = [r for r in reminders if r.get('priority') == 'high']
            medium_priority = [r for r in reminders if r.get('priority') == 'medium']
            low_priority = [r for r in reminders if r.get('priority') == 'low' or not r.get('priority')]
            
            # Display high priority reminders
            if high_priority:
                st.subheader("High Priority")
                for reminder in high_priority:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{reminder['message']}**")
                            
                            if reminder.get('due_date'):
                                due_date = datetime.fromisoformat(reminder['due_date'])
                                st.write(f"Due: {due_date.strftime('%b %d, %Y')}")
                            
                            created_at = datetime.fromisoformat(reminder['created_at'])
                            st.write(f"Received: {created_at.strftime('%b %d, %Y %H:%M')}")
                        
                        with col2:
                            if reminder.get('payment_id') and reminder.get('type') == 'payment_reminder':
                                if st.button("Pay Now", key=f"reminder_pay_{reminder['id']}"):
                                    # Find the payment
                                    payments = payment_manager.load_recurring_payments(username)
                                    for payment in payments:
                                        if payment['id'] == reminder['payment_id']:
                                            result = payment_manager.process_payment(payment['id'], manual=True)
                                            if result['success']:
                                                st.success(f"Payment of ${payment['amount']:.2f} to {payment['recipient']} processed successfully!")
                                                payment_manager.mark_reminder_read(reminder['id'])
                                                st.rerun()
                                            else:
                                                st.error(f"Payment failed: {result.get('error', 'Unknown error')}")
                                            break
                            
                            if not reminder.get('read'):
                                if st.button("Mark as Read", key=f"read_{reminder['id']}"):
                                    payment_manager.mark_reminder_read(reminder['id'])
                                    st.rerun()
            
            # Display medium priority reminders
            if medium_priority:
                st.subheader("Medium Priority")
                for reminder in medium_priority:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{reminder['message']}**")
                            
                            if reminder.get('due_date'):
                                due_date = datetime.fromisoformat(reminder['due_date'])
                                st.write(f"Due: {due_date.strftime('%b %d, %Y')}")
                            
                            created_at = datetime.fromisoformat(reminder['created_at'])
                            st.write(f"Received: {created_at.strftime('%b %d, %Y %H:%M')}")
                        
                        with col2:
                            if reminder.get('payment_id') and reminder.get('type') == 'payment_reminder':
                                if st.button("Pay Now", key=f"reminder_pay_{reminder['id']}"):
                                    # Find the payment
                                    payments = payment_manager.load_recurring_payments(username)
                                    for payment in payments:
                                        if payment['id'] == reminder['payment_id']:
                                            result = payment_manager.process_payment(payment['id'], manual=True)
                                            if result['success']:
                                                st.success(f"Payment of ${payment['amount']:.2f} to {payment['recipient']} processed successfully!")
                                                payment_manager.mark_reminder_read(reminder['id'])
                                                st.rerun()
                                            else:
                                                st.error(f"Payment failed: {result.get('error', 'Unknown error')}")
                                            break
                            
                            if not reminder.get('read'):
                                if st.button("Mark as Read", key=f"read_{reminder['id']}"):
                                    payment_manager.mark_reminder_read(reminder['id'])
                                    st.rerun()
            
            # Display low priority reminders
            if low_priority:
                st.subheader("Low Priority")
                for reminder in low_priority:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{reminder['message']}**")
                            
                            if reminder.get('due_date'):
                                due_date = datetime.fromisoformat(reminder['due_date'])
                                st.write(f"Due: {due_date.strftime('%b %d, %Y')}")
                            
                            created_at = datetime.fromisoformat(reminder['created_at'])
                            st.write(f"Received: {created_at.strftime('%b %d, %Y %H:%M')}")
                        
                        with col2:
                            if reminder.get('payment_id') and reminder.get('type') == 'payment_reminder':
                                if st.button("Pay Now", key=f"reminder_pay_{reminder['id']}"):
                                    # Find the payment
                                    payments = payment_manager.load_recurring_payments(username)
                                    for payment in payments:
                                        if payment['id'] == reminder['payment_id']:
                                            result = payment_manager.process_payment(payment['id'], manual=True)
                                            if result['success']:
                                                st.success(f"Payment of ${payment['amount']:.2f} to {payment['recipient']} processed successfully!")
                                                payment_manager.mark_reminder_read(reminder['id'])
                                                st.rerun()
                                            else:
                                                st.error(f"Payment failed: {result.get('error', 'Unknown error')}")
                                            break
                            
                            if not reminder.get('read'):
                                if st.button("Mark as Read", key=f"read_{reminder['id']}"):
                                    payment_manager.mark_reminder_read(reminder['id'])
                                    st.rerun()
    
    # Back button
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# For testing the page independently
if __name__ == "__main__":
    st.set_page_config(page_title="Recurring Payments", page_icon="💸", layout="wide")
    recurring_payments_page("testuser")