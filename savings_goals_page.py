def savings_goals_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    from datetime import datetime, timedelta
    import matplotlib.pyplot as plt
    import numpy as np
    import uuid
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Savings Goals</h1>", unsafe_allow_html=True)
    
    # Load user data
    def load_users():
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(users):
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
    
    # Load savings goals
    def load_savings_goals():
        if os.path.exists('savings_goals.json'):
            with open('savings_goals.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_savings_goals(goals):
        with open('savings_goals.json', 'w') as f:
            json.dump(goals, f, indent=4)
    
    # Load transactions
    def load_transactions():
        if os.path.exists('transactions.json'):
            with open('transactions.json', 'r') as f:
                return json.load(f)
        return []
    
    def save_transactions(transactions):
        with open('transactions.json', 'w') as f:
            json.dump(transactions, f, indent=4)
    
    # Add transaction function
    def add_transaction(sender, recipient, amount, transaction_type, note="", category="Savings"):
        users = load_users()
        
        # Check if sender exists and has sufficient balance
        if sender != "Savings Goal" and (sender not in users or users[sender]['balance'] < amount):
            return False, "Insufficient balance or invalid sender"
        
        # Check if recipient exists
        if recipient != "Savings Goal" and recipient not in users:
            return False, "Invalid recipient"
        
        # Update balances
        if sender != "Savings Goal":
            users[sender]['balance'] -= amount
        
        if recipient != "Savings Goal":
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
    
    # Initialize savings goals if not exists
    if 'savings_goals' not in st.session_state:
        savings_goals = load_savings_goals()
        if st.session_state.current_user not in savings_goals:
            savings_goals[st.session_state.current_user] = []
        st.session_state.savings_goals = savings_goals
    
    # Tabs for Create Goal and View Goals
    tab1, tab2 = st.tabs(["Create Savings Goal", "View & Manage Goals"])
    
    with tab1:
        st.markdown("### Create New Savings Goal")
        
        # Form for creating new savings goal
        with st.form("savings_goal_form"):
            goal_name = st.text_input("Goal Name", placeholder="e.g., New Laptop, Vacation, Emergency Fund")
            target_amount = st.number_input("Target Amount (₹)", min_value=100, value=10000)
            
            # Date selection
            today = datetime.now().date()
            min_date = today + timedelta(days=1)
            max_date = today + timedelta(days=365*5)  # 5 years max
            target_date = st.date_input("Target Date", min_value=min_date, max_value=max_date, value=today + timedelta(days=90))
            
            # Initial contribution
            initial_amount = st.number_input("Initial Contribution (₹)", min_value=0, max_value=target_amount, value=0)
            
            # Goal icon/category
            goal_categories = [
                "Travel", "Education", "Electronics", "Vehicle", "Home", 
                "Emergency Fund", "Retirement", "Wedding", "Gift", "Other"
            ]
            goal_category = st.selectbox("Goal Category", goal_categories)
            
            submit_button = st.form_submit_button("Create Savings Goal")
            
            if submit_button:
                if not goal_name:
                    st.error("Please enter a goal name")
                elif target_date <= today:
                    st.error("Target date must be in the future")
                else:
                    # Check if user has enough balance for initial contribution
                    users = load_users()
                    current_user = users[st.session_state.current_user]
                    
                    if initial_amount > current_user['balance']:
                        st.error("Insufficient balance for initial contribution")
                    else:
                        # Create new goal
                        new_goal = {
                            "id": str(uuid.uuid4()),
                            "name": goal_name,
                            "target_amount": target_amount,
                            "current_amount": initial_amount,
                            "target_date": target_date.strftime('%Y-%m-%d'),
                            "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "category": goal_category,
                            "completed": False
                        }
                        
                        # Add to user's goals
                        user_goals = st.session_state.savings_goals.get(st.session_state.current_user, [])
                        user_goals.append(new_goal)
                        st.session_state.savings_goals[st.session_state.current_user] = user_goals
                        save_savings_goals(st.session_state.savings_goals)
                        
                        # Create transaction for initial contribution if > 0
                        if initial_amount > 0:
                            success, message = add_transaction(
                                st.session_state.current_user,
                                "Savings Goal",
                                initial_amount,
                                "savings_deposit",
                                f"Initial deposit for {goal_name}",
                                "Savings"
                            )
                            
                            if not success:
                                st.error(f"Error creating initial deposit: {message}")
                        
                        st.success(f"Savings goal '{goal_name}' created successfully!")
                        st.rerun()
    
    with tab2:
        st.markdown("### Your Savings Goals")
        
        # Get user's goals
        user_goals = st.session_state.savings_goals.get(st.session_state.current_user, [])
        
        if not user_goals:
            st.info("You haven't created any savings goals yet. Go to 'Create Savings Goal' tab to get started.")
        else:
            # Filter options
            show_completed = st.checkbox("Show completed goals", value=False)
            
            # Filter goals based on completion status
            filtered_goals = [g for g in user_goals if g['completed'] == show_completed]
            
            if not filtered_goals:
                if show_completed:
                    st.info("You don't have any completed savings goals yet.")
                else:
                    st.info("You don't have any active savings goals. Go to 'Create Savings Goal' tab to get started.")
            else:
                # Display goals as cards
                for i, goal in enumerate(filtered_goals):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # Calculate progress percentage
                            progress_pct = (goal['current_amount'] / goal['target_amount']) * 100
                            
                            # Calculate days remaining
                            target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d').date()
                            days_remaining = (target_date - datetime.now().date()).days
                            
                            # Display goal info
                            st.markdown(f"### {goal['name']} ({goal['category']})")
                            st.progress(min(progress_pct / 100, 1.0))
                            st.markdown(f"**Progress:** ₹{goal['current_amount']:.2f} of ₹{goal['target_amount']:.2f} ({progress_pct:.1f}%)")
                            
                            if days_remaining > 0:
                                st.markdown(f"**Target Date:** {goal['target_date']} ({days_remaining} days remaining)")
                            else:
                                st.markdown(f"**Target Date:** {goal['target_date']} (Overdue by {abs(days_remaining)} days)")
                            
                            # Calculate required daily/monthly savings
                            if days_remaining > 0 and progress_pct < 100:
                                remaining_amount = goal['target_amount'] - goal['current_amount']
                                daily_required = remaining_amount / days_remaining
                                monthly_required = daily_required * 30 if days_remaining >= 30 else remaining_amount
                                
                                st.markdown(f"**Required Savings:** ₹{daily_required:.2f}/day or ₹{monthly_required:.2f}/month")
                        
                        with col2:
                            # Add contribution button
                            if not goal['completed']:
                                if st.button(f"Add Funds", key=f"add_{i}"):
                                    st.session_state.selected_goal = goal
                                    st.session_state.show_contribution_form = True
                            
                            # Complete goal button
                            if progress_pct >= 100 and not goal['completed']:
                                if st.button(f"Mark Complete", key=f"complete_{i}"):
                                    # Update goal status
                                    for g in user_goals:
                                        if g['id'] == goal['id']:
                                            g['completed'] = True
                                            break
                                    
                                    # Save updated goals
                                    st.session_state.savings_goals[st.session_state.current_user] = user_goals
                                    save_savings_goals(st.session_state.savings_goals)
                                    
                                    st.success(f"Goal '{goal['name']}' marked as completed!")
                                    st.rerun()
                            
                            # Delete goal button
                            if st.button(f"Delete", key=f"delete_{i}"):
                                # If goal has funds, ask for confirmation
                                if goal['current_amount'] > 0:
                                    st.session_state.confirm_delete_goal = goal
                                    st.session_state.show_delete_confirmation = True
                                else:
                                    # Remove goal
                                    updated_goals = [g for g in user_goals if g['id'] != goal['id']]
                                    st.session_state.savings_goals[st.session_state.current_user] = updated_goals
                                    save_savings_goals(st.session_state.savings_goals)
                                    
                                    st.success(f"Goal '{goal['name']}' deleted successfully!")
                                    st.rerun()
                        
                        st.markdown("---")
            
            # Contribution form
            if hasattr(st.session_state, 'show_contribution_form') and st.session_state.show_contribution_form:
                st.markdown("### Add Contribution")
                selected_goal = st.session_state.selected_goal
                
                with st.form("contribution_form"):
                    st.markdown(f"**Goal:** {selected_goal['name']}")
                    
                    # Get user balance
                    users = load_users()
                    current_user = users[st.session_state.current_user]
                    st.markdown(f"**Your Balance:** ₹{current_user['balance']:.2f}")
                    
                    # Amount input
                    max_contribution = max(1.0, float(current_user['balance']))
                    default_contribution = max(1.0, min(100.0, float(current_user['balance'])))
                    
                    contribution_amount = st.number_input(
                        "Contribution Amount (₹)", 
                        min_value=1.0, 
                        max_value=max_contribution,
                        value=default_contribution
                    )
                    
                    submit_contribution = st.form_submit_button("Add Contribution")
                    
                    if submit_contribution:
                        if contribution_amount <= 0:
                            st.error("Please enter a valid amount")
                        elif contribution_amount > current_user['balance']:
                            st.error("Insufficient balance")
                        else:
                            # Process transaction
                            success, message = add_transaction(
                                st.session_state.current_user,
                                "Savings Goal",
                                contribution_amount,
                                "savings_deposit",
                                f"Contribution to {selected_goal['name']}",
                                "Savings"
                            )
                            
                            if success:
                                # Update goal amount
                                for goal in user_goals:
                                    if goal['id'] == selected_goal['id']:
                                        goal['current_amount'] += contribution_amount
                                        break
                                
                                # Save updated goals
                                st.session_state.savings_goals[st.session_state.current_user] = user_goals
                                save_savings_goals(st.session_state.savings_goals)
                                
                                st.success(f"Added ₹{contribution_amount:.2f} to '{selected_goal['name']}'!")
                                
                                # Reset form state
                                st.session_state.show_contribution_form = False
                                st.rerun()
                            else:
                                st.error(message)
                
                # Cancel button
                if st.button("Cancel"):
                    st.session_state.show_contribution_form = False
                    st.rerun()
            
            # Delete confirmation
            if hasattr(st.session_state, 'show_delete_confirmation') and st.session_state.show_delete_confirmation:
                st.markdown("### Confirm Delete Goal")
                goal = st.session_state.confirm_delete_goal
                
                st.warning(f"Goal '{goal['name']}' has ₹{goal['current_amount']:.2f} in it. What would you like to do with these funds?")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Return to Wallet", use_container_width=True):
                        # Process transaction to return funds
                        success, message = add_transaction(
                            "Savings Goal",
                            st.session_state.current_user,
                            goal['current_amount'],
                            "savings_withdrawal",
                            f"Funds returned from deleted goal: {goal['name']}",
                            "Savings"
                        )
                        
                        if success:
                            # Remove goal
                            updated_goals = [g for g in user_goals if g['id'] != goal['id']]
                            st.session_state.savings_goals[st.session_state.current_user] = updated_goals
                            save_savings_goals(st.session_state.savings_goals)
                            
                            st.success(f"Goal deleted and ₹{goal['current_amount']:.2f} returned to your wallet!")
                            
                            # Reset confirmation state
                            st.session_state.show_delete_confirmation = False
                            st.rerun()
                        else:
                            st.error(message)
                
                with col2:
                    if st.button("Forfeit Funds", use_container_width=True):
                        # Remove goal without returning funds
                        updated_goals = [g for g in user_goals if g['id'] != goal['id']]
                        st.session_state.savings_goals[st.session_state.current_user] = updated_goals
                        save_savings_goals(st.session_state.savings_goals)
                        
                        st.success(f"Goal '{goal['name']}' deleted and funds forfeited.")
                        
                        # Reset confirmation state
                        st.session_state.show_delete_confirmation = False
                        st.rerun()
                
                # Cancel button
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_delete_confirmation = False
                    st.rerun()
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()