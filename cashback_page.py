def cashback_page():
    import streamlit as st
    import pandas as pd
    from datetime import datetime
    from app import load_cashbacks, save_cashbacks, load_users, save_users, load_transactions
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Cashback & Rewards</h1>", unsafe_allow_html=True)
    
    # Load cashback data
    cashbacks = load_cashbacks()
    username = st.session_state.current_user
    
    # Display current points
    if username in cashbacks:
        user_cashback = cashbacks[username]
        points = user_cashback["points"]
        total_cashback = user_cashback["total_cashback"]
        transactions = user_cashback["transactions"]
    else:
        points = 0
        total_cashback = 0
        transactions = []
    
    # Update session state
    st.session_state.cashback_points = points
    
    # Create tabs for Cashback Summary and Redeem Rewards
    tab1, tab2 = st.tabs(["Cashback Summary", "Redeem Rewards"])
    
    with tab1:
        st.markdown("<h3 style='text-align: center;'>Your Cashback Summary</h3>", unsafe_allow_html=True)
        
        # Display cashback metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Available Points", f"{points}")
        with col2:
            st.metric("Total Cashback Earned", f"₹{total_cashback:.2f}")
        
        # Display cashback rate information
        st.markdown("### Cashback Rates")
        rates_data = {
            "Transaction Type": ["Send Money", "Add Money", "Bill Split"],
            "Cashback Rate": ["0.5%", "1%", "2%"],
            "Points per ₹100": ["5 points", "10 points", "20 points"]
        }
        st.dataframe(pd.DataFrame(rates_data), hide_index=True)
        
        # Display cashback history
        st.markdown("### Cashback History")
        if transactions:
            # Convert to DataFrame for better display
            df = pd.DataFrame(transactions)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp", ascending=False)
            
            # Format for display
            df["cashback"] = df["cashback"].apply(lambda x: f"₹{x:.2f}")
            df["amount"] = df["amount"].apply(lambda x: f"₹{x:.2f}")
            df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
            
            # Rename columns for better display
            df.columns = ["Amount", "Cashback", "Points Earned", "Transaction Type", "Date & Time"]
            
            # Display as table
            st.dataframe(df, hide_index=True)
        else:
            st.info("No cashback history yet. Make transactions to earn cashback!")
    
    with tab2:
        st.markdown("<h3 style='text-align: center;'>Redeem Your Rewards</h3>", unsafe_allow_html=True)
        
        # Display available points
        st.markdown(f"### Available Points: {points}")
        st.markdown("### Redemption Options")
        
        # Redemption options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Add to Wallet")
            st.markdown("Convert your points to wallet balance")
            st.markdown("**Rate: 10 points = ₹1**")
            
            # Input for points to redeem
            redeem_points = st.number_input("Points to Redeem", min_value=10, max_value=points if points >= 10 else 10, step=10)
            redeem_value = redeem_points / 10
            st.markdown(f"You will get: ₹{redeem_value:.2f}")
            
            # Redeem button
            if st.button("Redeem to Wallet", use_container_width=True):
                if points >= redeem_points:
                    success, message = redeem_cashback(username, redeem_points)
                    if success:
                        st.success(message)
                        # Update session state
                        st.session_state.cashback_points -= redeem_points
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Insufficient points")
        
        with col2:
            st.markdown("#### Special Offers")
            
            # Mock special offers
            offers = [
                {"name": "₹100 Amazon Voucher", "points": 1000, "description": "Get a ₹100 Amazon gift card"},
                {"name": "₹200 Flipkart Voucher", "points": 2000, "description": "Get a ₹200 Flipkart gift card"},
                {"name": "Movie Ticket", "points": 1500, "description": "Free movie ticket worth ₹150"},
                {"name": "Food Delivery Coupon", "points": 800, "description": "₹80 off on food delivery"}
            ]
            
            # Display offers
            for i, offer in enumerate(offers):
                with st.expander(f"{offer['name']} - {offer['points']} points"):
                    st.markdown(offer["description"])
                    if st.button(f"Redeem Offer", key=f"offer_{i}"):
                        if points >= offer["points"]:
                            # In a real app, this would generate and store a voucher code
                            voucher_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                            st.success(f"Redeemed successfully! Your voucher code is: {voucher_code}")
                            
                            # Update points (mock implementation)
                            success, _ = redeem_cashback(username, offer["points"])
                            if success:
                                # Update session state
                                st.session_state.cashback_points -= offer["points"]
                                st.rerun()
                        else:
                            st.error("Insufficient points")
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()