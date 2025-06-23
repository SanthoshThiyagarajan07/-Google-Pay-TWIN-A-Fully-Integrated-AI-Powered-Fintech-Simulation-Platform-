def bill_split_page():
    import streamlit as st
    import pandas as pd
    from datetime import datetime
    from app import load_users, save_users, load_transactions, save_transactions, add_transaction, load_bill_splits, save_bill_splits, create_bill_split, pay_bill_split, calculate_cashback
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Bill Split</h1>", unsafe_allow_html=True)
    
    # Create tabs for Create Split and View Splits
    tab1, tab2 = st.tabs(["Create Bill Split", "View Bill Splits"])
    
    with tab1:
        st.markdown("<h3 style='text-align: center;'>Create New Bill Split</h3>", unsafe_allow_html=True)
        
        # Get list of users to split bill with (excluding current user)
        users = load_users()
        user_list = [u for u in users.keys() if u != st.session_state.current_user]
        
        if user_list:
            # Bill split form
            title = st.text_input("Bill Title", placeholder="Dinner, Movie, etc.")
            amount = st.number_input("Total Amount (₹)", min_value=1.0, step=1.0)
            
            # Select participants
            st.markdown("### Select Participants")
            participants = [st.session_state.current_user]  # Current user is always a participant
            
            # Create checkboxes for each user
            selected_users = {}
            for user in user_list:
                selected_users[user] = st.checkbox(user)
            
            # Add selected users to participants list
            for user, selected in selected_users.items():
                if selected:
                    participants.append(user)
            
            # Display participants and amount per person
            if len(participants) > 1:
                amount_per_person = amount / len(participants)
                st.markdown(f"### Amount per person: ₹{amount_per_person:.2f}")
                st.markdown(f"### Total participants: {len(participants)}")
            else:
                st.warning("Please select at least one other participant")
            
            # Create bill split button
            if st.button("Create Bill Split", use_container_width=True):
                if title and amount > 0 and len(participants) > 1:
                    # Create bill split
                    bill_split = create_bill_split(
                        st.session_state.current_user,
                        title,
                        amount,
                        participants
                    )
                    
                    st.success(f"Bill split '{title}' created successfully!")
                    st.markdown(f"### Amount per person: ₹{bill_split['amount_per_person']:.2f}")
                    st.markdown("### Participants:")
                    for participant in participants:
                        if participant == st.session_state.current_user:
                            st.markdown(f"- {participant} (You - Creator)")
                        else:
                            st.markdown(f"- {participant}")
                else:
                    if not title:
                        st.error("Please enter a bill title")
                    if amount <= 0:
                        st.error("Please enter a valid amount")
                    if len(participants) <= 1:
                        st.error("Please select at least one other participant")
        else:
            st.info("No users to split bill with. Ask your friends to register!")
    
    with tab2:
        st.markdown("<h3 style='text-align: center;'>Your Bill Splits</h3>", unsafe_allow_html=True)
        
        # Load bill splits
        bill_splits = load_bill_splits()
        
        # Filter bill splits where current user is involved
        user_bill_splits = []
        for bill in bill_splits:
            if st.session_state.current_user in bill["participants"]:
                user_bill_splits.append(bill)
        
        if user_bill_splits:
            # Create tabs for bills you created and bills to pay
            split_tab1, split_tab2 = st.tabs(["Bills You Created", "Bills to Pay"])
            
            with split_tab1:
                # Filter bills created by current user
                created_bills = [bill for bill in user_bill_splits if bill["creator"] == st.session_state.current_user]
                
                if created_bills:
                    for bill in created_bills:
                        with st.expander(f"{bill['title']} - ₹{bill['amount']:.2f}"):
                            st.markdown(f"**Created at:** {bill['created_at']}")
                            st.markdown(f"**Amount per person:** ₹{bill['amount_per_person']:.2f}")
                            st.markdown("**Participants:**")
                            
                            # Show payment status for each participant
                            for participant in bill["participants"]:
                                if participant == st.session_state.current_user:
                                    st.markdown(f"- {participant} (You - Creator)")
                                else:
                                    status = "Paid" if participant in bill["paid"] and bill["paid"][participant] else "Pending"
                                    st.markdown(f"- {participant}: {status}")
                else:
                    st.info("You haven't created any bill splits yet")
            
            with split_tab2:
                # Filter bills where current user needs to pay
                bills_to_pay = [bill for bill in user_bill_splits 
                               if bill["creator"] != st.session_state.current_user 
                               and st.session_state.current_user in bill["paid"] 
                               and not bill["paid"][st.session_state.current_user]]
                
                if bills_to_pay:
                    for bill in bills_to_pay:
                        with st.expander(f"{bill['title']} - ₹{bill['amount_per_person']:.2f}"):
                            st.markdown(f"**Created by:** {bill['creator']}")
                            st.markdown(f"**Created at:** {bill['created_at']}")
                            st.markdown(f"**Total amount:** ₹{bill['amount']:.2f}")
                            st.markdown(f"**Your share:** ₹{bill['amount_per_person']:.2f}")
                            
                            # Pay button
                            if st.button(f"Pay ₹{bill['amount_per_person']:.2f}", key=f"pay_{bill['id']}"):
                                success, message = pay_bill_split(bill["id"], st.session_state.current_user)
                                
                                if success:
                                    st.success(message)
                                    # Calculate cashback
                                    points, cashback = calculate_cashback(
                                        st.session_state.current_user,
                                        bill['amount_per_person'],
                                        "bill_split"
                                    )
                                    st.session_state.cashback_points += points
                                    st.success(f"You earned {points} cashback points!")
                                    st.rerun()
                                else:
                                    st.error(message)
                else:
                    st.info("You don't have any pending bills to pay")
        else:
            st.info("No bill splits found")
    
    # Navigation handled by main app