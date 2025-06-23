def qr_code_page():
    import streamlit as st
    import json
    import io
    from PIL import Image
    from datetime import datetime
    from app import load_users, save_users, load_transactions, save_transactions, add_transaction, calculate_cashback, generate_qr_code, scan_qr_code
    
    # Try to import enhanced modules
    try:
        from payment_gateway import PaymentGateway, create_payment_link
        from security import SecurityManager
        from advanced_fraud_detection import AdvancedFraudDetector
        payment_gateway_available = True
    except ImportError:
        payment_gateway_available = False
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>QR Code</h1>", unsafe_allow_html=True)
    
    # Create tabs for Generate QR and Scan QR
    tab1, tab2 = st.tabs(["Generate QR Code", "Scan QR Code"])
    
    with tab1:
        st.markdown("<h3 style='text-align: center;'>Generate Payment QR Code</h3>", unsafe_allow_html=True)
        
        # Get current user's information
        users = load_users()
        current_user = users[st.session_state.current_user]
        
        # Display current balance
        st.markdown(f"<h4>Your Balance: ₹{current_user['balance']:.2f}</h4>", unsafe_allow_html=True)
        
        # Options for QR code generation
        amount = st.number_input("Amount (₹)", min_value=1.0, step=1.0)
        note = st.text_input("Add a Note (Optional)")
        
        # Payment method selection
        if payment_gateway_available:
            payment_method = st.selectbox("Payment Method", ["Direct Transfer", "Stripe", "Razorpay", "PayPal"])
        else:
            payment_method = "Direct Transfer"
            
        # Security options
        if payment_gateway_available:
            require_2fa = st.checkbox("Require 2FA for payment", value=False)
            expiry_time = st.selectbox("QR Code Expiry", ["5 minutes", "15 minutes", "1 hour", "24 hours"], index=1)
        
        # Generate QR code button
        if st.button("Generate QR Code", use_container_width=True):
            # Create enhanced QR code data
            qr_data = {
                "username": st.session_state.current_user,
                "amount": amount,
                "note": note,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "payment_method": payment_method,
                "qr_id": f"qr_{st.session_state.current_user}_{int(datetime.now().timestamp())}"
            }
            
            # Add security features if available
            if payment_gateway_available:
                qr_data["require_2fa"] = require_2fa
                qr_data["expiry_time"] = expiry_time
                
                # Create payment link for gateway payments
                if payment_method != "Direct Transfer":
                    try:
                        gateway = PaymentGateway('razorpay')  # Default to Razorpay
                        payment_link = create_payment_link(
                            amount=amount,
                            currency="INR",
                            description=f"Payment to {st.session_state.current_user}: {note}",
                            gateway=payment_method.lower()
                        )
                        qr_data["payment_link"] = payment_link
                    except Exception as e:
                        st.warning(f"Could not create payment link: {str(e)}")
            
            # Convert to JSON string
            qr_json = json.dumps(qr_data)
            
            # Generate QR code
            qr_img = generate_qr_code(qr_json)
            
            # Save QR code to session state
            st.session_state.qr_data = qr_data
            
            # Display QR code
            st.image(qr_img, caption=f"Payment QR Code for ₹{amount:.2f}", width=300)
            
            # Display QR code details
            col1, col2 = st.columns(2)
            with col1:
                st.success("QR Code generated successfully!")
                st.info(f"Payment Method: {payment_method}")
                if payment_gateway_available and require_2fa:
                    st.warning("🔒 2FA Required for payment")
            
            with col2:
                if payment_gateway_available:
                    st.info(f"Expires in: {expiry_time}")
                    st.info(f"QR ID: {qr_data['qr_id']}")
            
            # Download button
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            st.download_button(
                label="Download QR Code",
                data=buf.getvalue(),
                file_name=f"payment_qr_{st.session_state.current_user}_{amount}.png",
                mime="image/png"
            )
    
    with tab2:
        st.markdown("<h3 style='text-align: center;'>Scan QR Code</h3>", unsafe_allow_html=True)
        
        # Option to upload QR code image
        uploaded_file = st.file_uploader("Upload QR Code Image", type=["jpg", "jpeg", "png"])
        
        # Option to use camera
        st.markdown("### Or Use Camera")
        camera_image = st.camera_input("Scan QR code with camera")
        
        # Process uploaded image
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded QR Code", width=300)
            
            if st.button("Scan Uploaded QR Code", use_container_width=True):
                # Scan QR code
                qr_data = scan_qr_code(image)
                
                if qr_data:
                    try:
                        # Parse QR data
                        payment_data = json.loads(qr_data)
                        
                        # Check if QR code has expired (if expiry info is available)
                        qr_expired = False
                        if payment_gateway_available and 'expiry_time' in payment_data and 'timestamp' in payment_data:
                            try:
                                qr_time = datetime.strptime(payment_data['timestamp'], "%Y-%m-%d %H:%M:%S")
                                expiry_minutes = {"5 minutes": 5, "15 minutes": 15, "1 hour": 60, "24 hours": 1440}
                                expiry_mins = expiry_minutes.get(payment_data['expiry_time'], 15)
                                if (datetime.now() - qr_time).total_seconds() > expiry_mins * 60:
                                    qr_expired = True
                            except:
                                pass
                        
                        if qr_expired:
                            st.error("⏰ This QR code has expired. Please request a new one.")
                        else:
                            # Display payment information
                            st.success("QR Code scanned successfully!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**From:** {payment_data['username']}")
                                st.markdown(f"**Amount:** ₹{payment_data['amount']:.2f}")
                                if payment_data.get('note'):
                                    st.markdown(f"**Note:** {payment_data['note']}")
                                st.markdown(f"**Generated at:** {payment_data['timestamp']}")
                            
                            with col2:
                                payment_method = payment_data.get('payment_method', 'Direct Transfer')
                                st.markdown(f"**Payment Method:** {payment_method}")
                                if payment_data.get('qr_id'):
                                    st.markdown(f"**QR ID:** {payment_data['qr_id']}")
                                if payment_data.get('require_2fa'):
                                    st.warning("🔒 2FA Required")
                            
                            # Fraud detection check
                            if payment_gateway_available:
                                try:
                                    fraud_detector = AdvancedFraudDetector()
                                    transaction_data = {
                                        'amount': payment_data['amount'],
                                        'sender': st.session_state.current_user,
                                        'receiver': payment_data['username'],
                                        'timestamp': datetime.now(),
                                        'type': 'qr_payment'
                                    }
                                    fraud_score = fraud_detector.predict_fraud_probability(transaction_data)
                                    
                                    if fraud_score > 0.7:
                                        st.error(f"⚠️ High fraud risk detected (Score: {fraud_score:.2f}). Transaction blocked.")
                                        return
                                    elif fraud_score > 0.5:
                                        st.warning(f"⚠️ Medium fraud risk detected (Score: {fraud_score:.2f}). Please verify the transaction.")
                                except:
                                    pass
                            
                            # 2FA verification if required
                            proceed_with_payment = True
                            if payment_data.get('require_2fa') and payment_gateway_available:
                                st.subheader("🔒 Two-Factor Authentication Required")
                                auth_code = st.text_input("Enter your 2FA code:", type="password")
                                if not auth_code:
                                    proceed_with_payment = False
                                else:
                                    try:
                                        security_manager = SecurityManager()
                                        if not security_manager.verify_2fa_token("user_secret", auth_code):
                                            st.error("Invalid 2FA code")
                                            proceed_with_payment = False
                                        else:
                                            st.success("2FA verified successfully!")
                                    except:
                                        st.warning("2FA verification unavailable, proceeding with payment")
                            
                            # Confirm payment button
                            if proceed_with_payment and st.button("Make Payment", use_container_width=True):
                                payment_method = payment_data.get('payment_method', 'Direct Transfer')
                                
                                if payment_method == 'Direct Transfer':
                                    # Process direct transfer
                                    success, message = add_transaction(
                                        st.session_state.current_user,
                                        payment_data['username'],
                                        payment_data['amount'],
                                        "send_money"
                                    )
                                    
                                    if success:
                                        # Calculate cashback
                                        points, cashback = calculate_cashback(
                                            st.session_state.current_user,
                                            payment_data['amount'],
                                            "send_money"
                                        )
                                        st.session_state.cashback_points += points
                                        
                                        st.success(f"Payment of ₹{payment_data['amount']:.2f} to {payment_data['username']} successful! You earned {points} cashback points.")
                                    else:
                                        st.error(message)
                                
                                elif payment_gateway_available and 'payment_link' in payment_data:
                                    # Redirect to payment gateway
                                    st.info(f"Redirecting to {payment_method} payment gateway...")
                                    st.markdown(f"[Complete Payment]({payment_data['payment_link']})", unsafe_allow_html=True)
                                    
                                    # In a real app, you would handle the payment gateway response
                                    if st.button("Simulate Payment Success"):
                                        success, message = add_transaction(
                                            st.session_state.current_user,
                                            payment_data['username'],
                                            payment_data['amount'],
                                            f"{payment_method.lower()}_payment"
                                        )
                                        
                                        if success:
                                            points, cashback = calculate_cashback(
                                                st.session_state.current_user,
                                                payment_data['amount'],
                                                f"{payment_method.lower()}_payment"
                                            )
                                            st.session_state.cashback_points += points
                                            st.success(f"Payment via {payment_method} successful! You earned {points} cashback points.")
                                        else:
                                            st.error(message)
                                
                                else:
                                    st.error(f"Payment method {payment_method} not supported or payment link unavailable")
                    except json.JSONDecodeError:
                        st.error("Invalid QR Code format")
                else:
                    st.error("Could not detect QR Code in the image")
        
        # Process camera image
        elif camera_image is not None:
            # Convert camera image to PIL Image
            image = Image.fromarray(camera_image)
            
            # Scan QR code
            qr_data = scan_qr_code(image)
            
            if qr_data:
                try:
                    # Parse QR data
                    payment_data = json.loads(qr_data)
                    
                    # Display payment information
                    st.success("QR Code scanned successfully!")
                    st.markdown(f"**From:** {payment_data['username']}")
                    st.markdown(f"**Amount:** ₹{payment_data['amount']:.2f}")
                    if payment_data['note']:
                        st.markdown(f"**Note:** {payment_data['note']}")
                    st.markdown(f"**Generated at:** {payment_data['timestamp']}")
                    
                    # Confirm payment button
                    if st.button("Make Payment", use_container_width=True, key="camera_payment"):
                        # Process payment
                        success, message = add_transaction(
                            st.session_state.current_user,
                            payment_data['username'],
                            payment_data['amount'],
                            "send_money"
                        )
                        
                        if success:
                            # Calculate cashback
                            points, cashback = calculate_cashback(
                                st.session_state.current_user,
                                payment_data['amount'],
                                "send_money"
                            )
                            st.session_state.cashback_points += points
                            
                            st.success(f"Payment of ₹{payment_data['amount']:.2f} to {payment_data['username']} successful! You earned {points} cashback points.")
                        else:
                            st.error(message)
                except json.JSONDecodeError:
                    st.error("Invalid QR Code format")
            else:
                st.info("No QR Code detected. Please try again.")
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()