def spending_challenge_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    from datetime import datetime, timedelta
    import uuid
    import matplotlib.pyplot as plt
    import numpy as np
    import random
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Spending Challenge</h1>", unsafe_allow_html=True)
    
    # Load user data
    def load_users():
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(users):
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
    
    # Load transactions
    def load_transactions():
        if os.path.exists('transactions.json'):
            with open('transactions.json', 'r') as f:
                return json.load(f)
        return []
    
    # Load spending challenges
    def load_challenges():
        if os.path.exists('spending_challenges.json'):
            with open('spending_challenges.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_challenges(challenges):
        with open('spending_challenges.json', 'w') as f:
            json.dump(challenges, f, indent=4)
    
    # Initialize challenges if not exists
    if 'spending_challenges' not in st.session_state:
        challenges = load_challenges()
        if st.session_state.current_user not in challenges:
            challenges[st.session_state.current_user] = {
                "active_challenges": [],
                "completed_challenges": [],
                "failed_challenges": []
            }
        st.session_state.spending_challenges = challenges
    
    # Get user's challenges
    user_challenges = st.session_state.spending_challenges.get(st.session_state.current_user, {})
    
    # Function to get user's spending by category in a date range
    def get_spending_by_category(username, start_date, end_date):
        transactions = load_transactions()
        
        # Convert dates to datetime objects for comparison
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Filter transactions by user and date range
        user_transactions = []
        for tx in transactions:
            if tx['sender'] == username and tx['type'] in ['send', 'pay_later']:
                tx_date = datetime.strptime(tx['date'].split()[0], '%Y-%m-%d')
                if start_date <= tx_date <= end_date:
                    user_transactions.append(tx)
        
        # Group by category and sum amounts
        spending_by_category = {}
        for tx in user_transactions:
            category = tx.get('category', 'Other')
            if category not in spending_by_category:
                spending_by_category[category] = 0
            spending_by_category[category] += tx['amount']
        
        return spending_by_category
    
    # Function to get total spending in a date range
    def get_total_spending(username, start_date, end_date):
        spending_by_category = get_spending_by_category(username, start_date, end_date)
        return sum(spending_by_category.values())
    
    # Function to check challenge status
    def check_challenge_status(challenge):
        today = datetime.now().date()
        end_date = datetime.strptime(challenge['end_date'], '%Y-%m-%d').date()
        
        # If challenge has ended, check if it was successful
        if today > end_date:
            if challenge['challenge_type'] == 'category':
                actual_spending = get_spending_by_category(
                    st.session_state.current_user,
                    challenge['start_date'],
                    challenge['end_date']
                ).get(challenge['category'], 0)
            else:  # total spending challenge
                actual_spending = get_total_spending(
                    st.session_state.current_user,
                    challenge['start_date'],
                    challenge['end_date']
                )
            
            if actual_spending <= challenge['target_amount']:
                return "completed", actual_spending
            else:
                return "failed", actual_spending
        
        # If challenge is still active, calculate current spending
        if challenge['challenge_type'] == 'category':
            current_spending = get_spending_by_category(
                st.session_state.current_user,
                challenge['start_date'],
                datetime.now().strftime('%Y-%m-%d')
            ).get(challenge['category'], 0)
        else:  # total spending challenge
            current_spending = get_total_spending(
                st.session_state.current_user,
                challenge['start_date'],
                datetime.now().strftime('%Y-%m-%d')
            )
        
        return "active", current_spending
    
    # Update challenge statuses
    def update_challenge_statuses():
        active_challenges = user_challenges.get('active_challenges', [])
        completed_challenges = user_challenges.get('completed_challenges', [])
        failed_challenges = user_challenges.get('failed_challenges', [])
        
        # Check each active challenge
        updated_active = []
        for challenge in active_challenges:
            status, actual_spending = check_challenge_status(challenge)
            
            if status == "completed":
                challenge['actual_spending'] = actual_spending
                challenge['completion_date'] = datetime.now().strftime('%Y-%m-%d')
                completed_challenges.append(challenge)
                
                # Add reward to user's balance
                users = load_users()
                users[st.session_state.current_user]['balance'] += challenge['reward_amount']
                save_users(users)
            elif status == "failed":
                challenge['actual_spending'] = actual_spending
                challenge['completion_date'] = datetime.now().strftime('%Y-%m-%d')
                failed_challenges.append(challenge)
            else:
                updated_active.append(challenge)
        
        # Update challenges
        user_challenges['active_challenges'] = updated_active
        user_challenges['completed_challenges'] = completed_challenges
        user_challenges['failed_challenges'] = failed_challenges
        
        # Save updated challenges
        st.session_state.spending_challenges[st.session_state.current_user] = user_challenges
        save_challenges(st.session_state.spending_challenges)
    
    # Update challenge statuses on page load
    update_challenge_statuses()
    
    # Tabs for Spending Challenge options
    tab1, tab2, tab3, tab4 = st.tabs(["Active Challenges", "Create Challenge", "Completed Challenges", "Failed Challenges"])
    
    with tab1:
        st.markdown("### Your Active Challenges")
        
        active_challenges = user_challenges.get('active_challenges', [])
        
        if not active_challenges:
            st.info("You don't have any active spending challenges. Create one to get started!")
        else:
            # Sort challenges by end date (soonest first)
            sorted_challenges = sorted(
                active_challenges,
                key=lambda x: datetime.strptime(x['end_date'], '%Y-%m-%d')
            )
            
            for i, challenge in enumerate(sorted_challenges):
                with st.container():
                    # Calculate days remaining
                    end_date = datetime.strptime(challenge['end_date'], '%Y-%m-%d').date()
                    days_remaining = (end_date - datetime.now().date()).days
                    
                    # Get current spending
                    _, current_spending = check_challenge_status(challenge)
                    
                    # Calculate progress percentage
                    progress_pct = min(100, (current_spending / challenge['target_amount']) * 100)
                    
                    # Create card with challenge details
                    st.markdown(f"### {challenge['title']}")
                    
                    # Challenge type and target
                    if challenge['challenge_type'] == 'category':
                        st.markdown(f"**Challenge:** Spend less than ₹{challenge['target_amount']:.2f} on {challenge['category']}")
                    else:
                        st.markdown(f"**Challenge:** Keep total spending under ₹{challenge['target_amount']:.2f}")
                    
                    # Date range
                    st.markdown(f"**Period:** {challenge['start_date']} to {challenge['end_date']} ({days_remaining} days remaining)")
                    
                    # Reward
                    st.markdown(f"**Reward:** ₹{challenge['reward_amount']:.2f} added to your balance")
                    
                    # Progress bar
                    st.progress(progress_pct / 100)
                    
                    # Current spending vs target
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Current Spending:** ₹{current_spending:.2f}")
                    with col2:
                        st.markdown(f"**Target:** ₹{challenge['target_amount']:.2f}")
                    
                    # Status indicator
                    if progress_pct < 50:
                        st.success(f"You're on track! Keep it up!")
                    elif progress_pct < 80:
                        st.info(f"You're at {progress_pct:.1f}% of your limit. Be careful with your spending!")
                    else:
                        st.warning(f"You're at {progress_pct:.1f}% of your limit. You're close to exceeding your challenge target!")
                    
                    st.markdown("---")
    
    with tab2:
        st.markdown("### Create a New Spending Challenge")
        
        with st.form("create_challenge_form"):
            # Challenge title
            title = st.text_input("Challenge Title", placeholder="e.g., Reduce Food Spending")
            
            # Challenge type
            challenge_type = st.radio("Challenge Type", ["Category Spending", "Total Spending"])
            
            # Category selection for category challenges
            category = None
            if challenge_type == "Category Spending":
                categories = [
                    "Shopping", "Food & Dining", "Entertainment", "Travel", 
                    "Utilities", "Education", "Health", "Other"
                ]
                category = st.selectbox("Category", categories)
            
            # Challenge duration
            duration_options = ["1 week", "2 weeks", "1 month", "3 months"]
            duration = st.selectbox("Challenge Duration", duration_options)
            
            # Calculate start and end dates
            start_date = datetime.now().date()
            if duration == "1 week":
                end_date = start_date + timedelta(days=7)
            elif duration == "2 weeks":
                end_date = start_date + timedelta(days=14)
            elif duration == "1 month":
                end_date = start_date + timedelta(days=30)
            else:  # 3 months
                end_date = start_date + timedelta(days=90)
            
            st.markdown(f"**Challenge Period:** {start_date} to {end_date}")
            
            # Get spending history for reference
            if challenge_type == "Category Spending" and category:
                # Calculate lookback period based on challenge duration
                if duration == "1 week":
                    lookback_days = 7
                elif duration == "2 weeks":
                    lookback_days = 14
                elif duration == "1 month":
                    lookback_days = 30
                else:  # 3 months
                    lookback_days = 90
                
                lookback_start = start_date - timedelta(days=lookback_days)
                
                # Get historical spending
                historical_spending = get_spending_by_category(
                    st.session_state.current_user,
                    lookback_start.strftime('%Y-%m-%d'),
                    start_date.strftime('%Y-%m-%d')
                ).get(category, 0)
                
                st.markdown(f"**Your {category} spending in the last {duration}:** ₹{historical_spending:.2f}")
                
                # Suggest target amount (80% of historical spending)
                suggested_target = historical_spending * 0.8
            elif challenge_type == "Total Spending":
                # Calculate lookback period based on challenge duration
                if duration == "1 week":
                    lookback_days = 7
                elif duration == "2 weeks":
                    lookback_days = 14
                elif duration == "1 month":
                    lookback_days = 30
                else:  # 3 months
                    lookback_days = 90
                
                lookback_start = start_date - timedelta(days=lookback_days)
                
                # Get historical total spending
                historical_spending = get_total_spending(
                    st.session_state.current_user,
                    lookback_start.strftime('%Y-%m-%d'),
                    start_date.strftime('%Y-%m-%d')
                )
                
                st.markdown(f"**Your total spending in the last {duration}:** ₹{historical_spending:.2f}")
                
                # Suggest target amount (90% of historical spending)
                suggested_target = historical_spending * 0.9
            else:
                suggested_target = 1000  # Default suggestion
            
            # Target amount
            default_value = max(100.0, float(suggested_target)) if 'suggested_target' in locals() else 1000.0
            target_amount = st.number_input(
                "Target Amount (₹)",
                min_value=100.0,
                value=default_value,
                step=100.0,
                help="Set a realistic spending target that challenges you but is achievable"
            )
            
            # Calculate reward based on challenge difficulty
            if 'historical_spending' in locals() and historical_spending > 0:
                difficulty = target_amount / historical_spending
                if difficulty <= 0.7:  # Very challenging (30%+ reduction)
                    reward_pct = 0.10  # 10% of target as reward
                elif difficulty <= 0.8:  # Challenging (20-30% reduction)
                    reward_pct = 0.07  # 7% of target as reward
                elif difficulty <= 0.9:  # Moderate (10-20% reduction)
                    reward_pct = 0.05  # 5% of target as reward
                else:  # Easy (less than 10% reduction)
                    reward_pct = 0.03  # 3% of target as reward
            else:
                reward_pct = 0.05  # Default 5%
            
            reward_amount = target_amount * reward_pct
            
            st.markdown(f"**Reward:** ₹{reward_amount:.2f} will be added to your balance if you complete this challenge")
            
            # Submit button
            submit_button = st.form_submit_button("Create Challenge")
            
            if submit_button:
                if not title:
                    st.error("Please enter a challenge title")
                elif target_amount <= 0:
                    st.error("Please enter a valid target amount")
                else:
                    # Create new challenge
                    new_challenge = {
                        "id": str(uuid.uuid4()),
                        "title": title,
                        "challenge_type": "category" if challenge_type == "Category Spending" else "total",
                        "category": category if challenge_type == "Category Spending" else None,
                        "target_amount": target_amount,
                        "reward_amount": reward_amount,
                        "start_date": start_date.strftime('%Y-%m-%d'),
                        "end_date": end_date.strftime('%Y-%m-%d'),
                        "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Add to active challenges
                    user_challenges['active_challenges'].append(new_challenge)
                    
                    # Save updated challenges
                    st.session_state.spending_challenges[st.session_state.current_user] = user_challenges
                    save_challenges(st.session_state.spending_challenges)
                    
                    st.success("Challenge created successfully!")
                    st.rerun()
    
    with tab3:
        st.markdown("### Your Completed Challenges")
        
        completed_challenges = user_challenges.get('completed_challenges', [])
        
        if not completed_challenges:
            st.info("You haven't completed any spending challenges yet.")
        else:
            # Sort challenges by completion date (most recent first)
            sorted_challenges = sorted(
                completed_challenges,
                key=lambda x: datetime.strptime(x.get('completion_date', '2000-01-01'), '%Y-%m-%d'),
                reverse=True
            )
            
            # Calculate total rewards earned
            total_rewards = sum(challenge['reward_amount'] for challenge in completed_challenges)
            st.markdown(f"**Total Rewards Earned:** ₹{total_rewards:.2f}")
            
            # Display completed challenges
            for challenge in sorted_challenges:
                with st.container():
                    st.markdown(f"### {challenge['title']} ✅")
                    
                    # Challenge type and target
                    if challenge['challenge_type'] == 'category':
                        st.markdown(f"**Challenge:** Spent less than ₹{challenge['target_amount']:.2f} on {challenge['category']}")
                    else:
                        st.markdown(f"**Challenge:** Kept total spending under ₹{challenge['target_amount']:.2f}")
                    
                    # Date range
                    st.markdown(f"**Period:** {challenge['start_date']} to {challenge['end_date']}")
                    
                    # Actual spending vs target
                    st.markdown(f"**Target:** ₹{challenge['target_amount']:.2f}")
                    st.markdown(f"**Actual Spending:** ₹{challenge.get('actual_spending', 0):.2f}")
                    
                    # Savings
                    savings = challenge['target_amount'] - challenge.get('actual_spending', 0)
                    st.markdown(f"**Savings:** ₹{savings:.2f}")
                    
                    # Reward
                    st.markdown(f"**Reward Earned:** ₹{challenge['reward_amount']:.2f}")
                    
                    # Completion date
                    st.markdown(f"**Completed on:** {challenge.get('completion_date', 'Unknown')}")
                    
                    st.markdown("---")
    
    with tab4:
        st.markdown("### Your Failed Challenges")
        
        failed_challenges = user_challenges.get('failed_challenges', [])
        
        if not failed_challenges:
            st.info("You haven't failed any spending challenges yet. Keep up the good work!")
        else:
            # Sort challenges by completion date (most recent first)
            sorted_challenges = sorted(
                failed_challenges,
                key=lambda x: datetime.strptime(x.get('completion_date', '2000-01-01'), '%Y-%m-%d'),
                reverse=True
            )
            
            # Display failed challenges
            for challenge in sorted_challenges:
                with st.container():
                    st.markdown(f"### {challenge['title']} ❌")
                    
                    # Challenge type and target
                    if challenge['challenge_type'] == 'category':
                        st.markdown(f"**Challenge:** Spend less than ₹{challenge['target_amount']:.2f} on {challenge['category']}")
                    else:
                        st.markdown(f"**Challenge:** Keep total spending under ₹{challenge['target_amount']:.2f}")
                    
                    # Date range
                    st.markdown(f"**Period:** {challenge['start_date']} to {challenge['end_date']}")
                    
                    # Actual spending vs target
                    st.markdown(f"**Target:** ₹{challenge['target_amount']:.2f}")
                    st.markdown(f"**Actual Spending:** ₹{challenge.get('actual_spending', 0):.2f}")
                    
                    # Overspending
                    overspending = challenge.get('actual_spending', 0) - challenge['target_amount']
                    st.markdown(f"**Overspent by:** ₹{overspending:.2f}")
                    
                    # Completion date
                    st.markdown(f"**Failed on:** {challenge.get('completion_date', 'Unknown')}")
                    
                    # Retry button
                    if st.button(f"Try Again", key=f"retry_{challenge['id']}"):
                        # Create a new challenge with the same parameters
                        new_challenge = challenge.copy()
                        new_challenge['id'] = str(uuid.uuid4())
                        new_challenge['start_date'] = datetime.now().strftime('%Y-%m-%d')
                        
                        # Calculate new end date based on original duration
                        original_start = datetime.strptime(challenge['start_date'], '%Y-%m-%d')
                        original_end = datetime.strptime(challenge['end_date'], '%Y-%m-%d')
                        duration_days = (original_end - original_start).days
                        
                        new_challenge['end_date'] = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d')
                        new_challenge['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Remove completion-related fields
                        if 'actual_spending' in new_challenge:
                            del new_challenge['actual_spending']
                        if 'completion_date' in new_challenge:
                            del new_challenge['completion_date']
                        
                        # Add to active challenges
                        user_challenges['active_challenges'].append(new_challenge)
                        
                        # Save updated challenges
                        st.session_state.spending_challenges[st.session_state.current_user] = user_challenges
                        save_challenges(st.session_state.spending_challenges)
                        
                        st.success("Challenge recreated! Good luck this time!")
                        st.rerun()
                    
                    st.markdown("---")
    
    # Challenge tips
    st.markdown("### Tips for Successful Spending Challenges")
    
    tips = [
        "Track your spending daily to stay aware of your progress",
        "Look for alternatives to your usual spending habits",
        "Set realistic targets based on your spending history",
        "Focus on reducing non-essential expenses first",
        "Consider meal planning to reduce food expenses",
        "Use public transportation instead of taxis when possible",
        "Wait 24 hours before making non-essential purchases",
        "Find free or low-cost alternatives for entertainment",
        "Invite friends to join your challenge for accountability",
        "Celebrate small wins along the way to stay motivated"
    ]
    
    # Display random tips
    random.shuffle(tips)
    for i, tip in enumerate(tips[:3]):
        st.info(f"💡 **Tip {i+1}:** {tip}")
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()