def voice_pay_page():
    import streamlit as st
    try:
        import speech_recognition as sr
    except ImportError:
        sr = None
    try:
        import pyttsx3
    except ImportError:
        pyttsx3 = None
    import re
    from datetime import datetime
    from app import load_users, save_users, add_transaction, calculate_cashback, listen_for_voice_command, process_voice_command
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Voice Pay</h1>", unsafe_allow_html=True)
    
    # Instructions
    st.markdown("### Make payments using voice commands")
    st.markdown("""
    You can use the following voice commands:
    - "Send [amount] rupees to [recipient]" - To send money to someone
    - "Add [amount] rupees" - To add money to your wallet
    - "Check balance" - To check your current balance
    - "Go to [page name]" - To navigate to another page
    """)
    
    # Display current balance
    users = load_users()
    current_user = users[st.session_state.current_user]
    st.markdown(f"<h3>Your Balance: ₹{current_user['balance']:.2f}</h3>", unsafe_allow_html=True)
    
    # Initialize voice command state if not exists
    if 'voice_command' not in st.session_state:
        st.session_state.voice_command = ""
    
    # Voice command section
    st.markdown("### Voice Command")
    
    # Display current command
    if st.session_state.voice_command:
        st.info(f"Detected command: {st.session_state.voice_command}")
    
    # Listen button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Listening", use_container_width=True):
            if sr is None:
                st.error("Speech recognition module not available. Please use manual input.")
            else:
                with st.spinner("Listening..."):
                    command = listen_for_voice_command()
                    if command:
                        st.session_state.voice_command = command
                        st.rerun()
                    else:
                        st.error("Could not detect voice command. Please try again.")
    
    with col2:
        # Manual input option
        manual_command = st.text_input("Or type your command here")
        if st.button("Process Command", use_container_width=True):
            if manual_command:
                st.session_state.voice_command = manual_command
                st.rerun()
            else:
                st.error("Please enter a command")
    
    # Process command if exists
    if st.session_state.voice_command:
        command_type, command_data = process_voice_command(st.session_state.voice_command)
        
        if command_type == "send_money":
            st.markdown("### Send Money Command Detected")
            
            # Extract recipient and amount from command
            amount = command_data.get("amount", 0)
            recipient = command_data.get("recipient", "")
            
            # Display and confirm transaction details
            st.markdown(f"**Amount:** ₹{amount:.2f}")
            st.markdown(f"**Recipient:** {recipient}")
            
            # Check if recipient exists
            recipient_exists = recipient in users
            if not recipient_exists:
                st.error(f"Recipient '{recipient}' not found. Please check the name and try again.")
            else:
                # Confirm transaction
                if st.button("Confirm Payment", use_container_width=True):
                    if amount > 0 and amount <= current_user['balance']:
                        success, message = add_transaction(
                            st.session_state.current_user,
                            recipient,
                            amount,
                            "send_money"
                        )
                        
                        if success:
                            # Calculate cashback
                            points, cashback = calculate_cashback(
                                st.session_state.current_user,
                                amount,
                                "send_money"
                            )
                            st.session_state.cashback_points += points
                            
                            st.success(f"₹{amount:.2f} sent to {recipient} successfully! You earned {points} cashback points.")
                            
                            # Text-to-speech confirmation
                            engine = pyttsx3.init()
                            engine.say(f"Payment of {amount} rupees to {recipient} successful")
                            engine.runAndWait()
                            
                            # Reset command
                            st.session_state.voice_command = ""
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        if amount <= 0:
                            st.error("Invalid amount")
                        else:
                            st.error("Insufficient balance")
        
        elif command_type == "add_money":
            st.markdown("### Add Money Command Detected")
            
            # Extract amount from command
            amount = command_data.get("amount", 0)
            
            # Display and confirm transaction details
            st.markdown(f"**Amount to Add:** ₹{amount:.2f}")
            
            # Confirm transaction
            if st.button("Confirm Add Money", use_container_width=True):
                if amount > 0:
                    success, message = add_transaction(
                        "Bank",
                        st.session_state.current_user,
                        amount,
                        "add_money"
                    )
                    
                    if success:
                        # Calculate cashback
                        points, cashback = calculate_cashback(
                            st.session_state.current_user,
                            amount,
                            "add_money"
                        )
                        st.session_state.cashback_points += points
                        
                        st.success(f"₹{amount:.2f} added to your wallet successfully! You earned {points} cashback points.")
                        
                        # Text-to-speech confirmation
                        if pyttsx3 is not None:
                            try:
                                engine = pyttsx3.init()
                                engine.say(f"{amount} rupees added to your wallet successfully")
                                engine.runAndWait()
                            except:
                                pass  # Silently fail if TTS doesn't work
                        
                        # Reset command
                        st.session_state.voice_command = ""
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Invalid amount")
        
        elif command_type == "check_balance":
            st.markdown("### Balance Check Command Detected")
            
            # Display balance
            st.success(f"Your current balance is ₹{current_user['balance']:.2f}")
            
            # Text-to-speech balance
            if pyttsx3 is not None:
                try:
                    engine = pyttsx3.init()
                    engine.say(f"Your current balance is {current_user['balance']} rupees")
                    engine.runAndWait()
                except:
                    pass  # Silently fail if TTS doesn't work
            
            # Reset command
            if st.button("Clear Command", use_container_width=True):
                st.session_state.voice_command = ""
                st.rerun()
        
        elif command_type == "navigate":
            page = command_data.get("page", "")
            
            if page:
                st.markdown(f"### Navigation Command Detected: Go to {page}")
                
                if st.button(f"Confirm Navigation to {page.title()}", use_container_width=True):
                    st.session_state.page = page
                    st.session_state.voice_command = ""
                    st.rerun()
            else:
                st.error("Invalid navigation command")
        
        elif command_type == False:
            st.error(f"Command not recognized: {command_data}")
            
            # Reset command
            if st.button("Clear Command", use_container_width=True):
                st.session_state.voice_command = ""
                st.rerun()
    
    # Voice command examples
    st.markdown("---")
    st.markdown("### Example Voice Commands")
    st.markdown("""
    - "Send 100 rupees to John"
    - "Add 500 rupees"
    - "Check balance"
    - "Go to dashboard"
    - "Go to transactions"
    """)
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()