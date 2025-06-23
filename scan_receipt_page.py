import streamlit as st
import numpy as np
# OCR functionality
try:
    import pytesseract
except ImportError:
    pytesseract = None
import re
from PIL import Image, ImageEnhance, ImageFilter
from datetime import datetime
import os
import json
import hashlib

# Import functions from app.py to avoid duplication
try:
    from app import (
        load_users, save_users, load_transactions, save_transactions,
        load_cashbacks, save_cashbacks, scan_receipt, add_transaction,
        calculate_cashback
    )
except ImportError:
    # Fallback functions if app.py import fails
    data_dir = "data"
    user_data_file = os.path.join(data_dir, "users.json")
    transaction_data_file = os.path.join(data_dir, "transactions.json")
    cashback_file = os.path.join(data_dir, "cashbacks.json")
    
    def load_users():
        try:
            with open(user_data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_users(users):
        with open(user_data_file, 'w') as f:
            json.dump(users, f)
    
    def load_transactions():
        try:
            with open(transaction_data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_transactions(transactions):
        with open(transaction_data_file, 'w') as f:
            json.dump(transactions, f)
    
    def load_cashbacks():
        try:
            with open(cashback_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_cashbacks(cashbacks):
        with open(cashback_file, 'w') as f:
            json.dump(cashbacks, f)
    
    def scan_receipt(image):
        try:
            if pytesseract is None or ImageEnhance is None or ImageFilter is None:
                print("Error: Required modules (pytesseract, PIL) not available. Cannot scan receipt.")
                return {}
            
            if image.mode != 'L':
                gray_image = image.convert('L')
            else:
                gray_image = image
            
            enhancer = ImageEnhance.Contrast(gray_image)
            enhanced_image = enhancer.enhance(2.0)
            
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
            sharp_image = sharpness_enhancer.enhance(2.0)
            
            filtered_image = sharp_image.filter(ImageFilter.MedianFilter(size=3))
            text = pytesseract.image_to_string(filtered_image)
            
            amount_pattern = r"(?:total|amount|amt)\s*(?::|\s)\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d{1,2})?)"
            date_pattern = r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            merchant_pattern = r"(?:merchant|store|shop|restaurant)\s*(?::|\s)\s*([\w\s]+)"
            
            amount_match = re.search(amount_pattern, text.lower())
            date_match = re.search(date_pattern, text)
            merchant_match = re.search(merchant_pattern, text.lower())
            
            result = {}
            if amount_match:
                result["amount"] = float(amount_match.group(1))
            if date_match:
                result["date"] = date_match.group(1)
            if merchant_match:
                result["merchant"] = merchant_match.group(1).strip()
            
            return result
        except Exception as e:
            print(f"Error scanning receipt: {e}")
            return {}
    
    def add_transaction(sender, receiver, amount, transaction_type):
        users = load_users()
        transactions = load_transactions()
        
        if transaction_type != "add_money" and users[sender]["balance"] < amount:
            return False, "Insufficient balance"
        
        if transaction_type == "add_money":
            users[sender]["balance"] += amount
        elif transaction_type == "send_money":
            users[sender]["balance"] -= amount
            if receiver in users:
                users[receiver]["balance"] += amount
        
        transaction = {
            "id": len(transactions) + 1,
            "sender": sender,
            "receiver": receiver if transaction_type == "send_money" else sender,
            "amount": amount,
            "type": transaction_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "completed"
        }
        
        transactions.append(transaction)
        if "transactions" not in users[sender]:
            users[sender]["transactions"] = []
        users[sender]["transactions"].append(transaction["id"])
        if transaction_type == "send_money" and receiver in users:
            if "transactions" not in users[receiver]:
                users[receiver]["transactions"] = []
            users[receiver]["transactions"].append(transaction["id"])
        
        save_users(users)
        save_transactions(transactions)
        
        return True, "Transaction successful"
    
    def calculate_cashback(username, amount, transaction_type):
        cashbacks = load_cashbacks()
        
        cashback_rates = {
            "shopping": 0.02, "food": 0.05, "travel": 0.03,
            "bill_payment": 0.01, "send_money": 0.005, "other": 0.01
        }
        
        rate = cashback_rates.get(transaction_type, 0.01)
        points = int(amount * rate * 100)
        cashback_amount = amount * rate
        
        if username not in cashbacks:
            cashbacks[username] = {
                "total_points": 0, "total_cashback": 0, "transactions": []
            }
        
        cashbacks[username]["total_points"] += points
        cashbacks[username]["total_cashback"] += cashback_amount
        cashbacks[username]["transactions"].append({
            "amount": amount, "type": transaction_type, "points": points,
            "cashback": cashback_amount, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        save_cashbacks(cashbacks)
        return points, cashback_amount

def scan_receipt_page():
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Scan Receipt</h1>", unsafe_allow_html=True)
    
    # Instructions
    st.markdown("### Scan your receipt to extract payment information")
    st.markdown("Upload a clear image of your receipt or use your camera to capture it. The system will extract the amount, date, and merchant information.")
    
    # Create tabs for Upload and Camera
    tab1, tab2 = st.tabs(["Upload Receipt", "Use Camera"])
    
    with tab1:
        # Upload receipt image
        uploaded_file = st.file_uploader("Upload Receipt Image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Receipt", width=400)
            
            # Scan button
            if st.button("Scan Receipt", use_container_width=True):
                if pytesseract is None:
                    st.error("OCR functionality not available. Please install pytesseract to use receipt scanning.")
                else:
                    with st.spinner("Scanning receipt..."):
                        # Process receipt
                        receipt_data = scan_receipt(image)
                        
                        if receipt_data and "amount" in receipt_data:
                            st.success("Receipt scanned successfully!")
                        
                            # Display extracted information
                            st.markdown("### Extracted Information")
                            st.markdown(f"**Amount:** ₹{receipt_data.get('amount', 0):.2f}")
                            if "date" in receipt_data:
                                st.markdown(f"**Date:** {receipt_data['date']}")
                            if "merchant" in receipt_data:
                                st.markdown(f"**Merchant:** {receipt_data['merchant']}")
                            
                            # Create transaction form
                            st.markdown("### Create Transaction")
                            
                            # Pre-fill amount if available
                            amount = st.number_input("Amount (₹)", 
                                                   value=float(receipt_data.get('amount', 0)), 
                                                   min_value=1.0, 
                                                   step=1.0)
                            
                            # Pre-fill merchant as recipient if available
                            if "merchant" in receipt_data:
                                recipient = st.text_input("Recipient/Merchant", value=receipt_data['merchant'])
                            else:
                                recipient = st.text_input("Recipient/Merchant")
                            
                            # Transaction type
                            transaction_type = st.selectbox("Transaction Type", 
                                                          ["send_money", "bill_payment", "shopping", "food", "travel", "entertainment", "other"])
                            
                            # Create transaction button
                            if st.button("Create Transaction", use_container_width=True):
                                if amount > 0 and recipient:
                                    # In a real app, we would verify if the recipient exists in the system
                                    # For this demo, we'll just create the transaction with the current user as sender
                                    success, message = add_transaction(
                                        st.session_state.current_user,
                                        recipient,
                                        amount,
                                        transaction_type
                                    )
                                    
                                    if success:
                                        # Calculate cashback
                                        points, cashback = calculate_cashback(
                                            st.session_state.current_user,
                                            amount,
                                            transaction_type
                                        )
                                        st.session_state.cashback_points += points
                                        
                                        st.success(f"Transaction of ₹{amount:.2f} to {recipient} created successfully! You earned {points} cashback points.")
                                    else:
                                        st.error(message)
                                else:
                                    if amount <= 0:
                                        st.error("Please enter a valid amount")
                                    if not recipient:
                                        st.error("Please enter a recipient/merchant")
                        else:
                            st.error("Could not extract payment information from the receipt. Please try again with a clearer image.")
    
    with tab2:
        # Use camera to capture receipt
        st.markdown("### Capture Receipt with Camera")
        camera_image = st.camera_input("Take a picture of your receipt")
        
        if camera_image is not None:
            # Convert camera image to PIL Image
            image = Image.open(camera_image)
            
            # Scan button
            if st.button("Scan Captured Receipt", use_container_width=True):
                if pytesseract is None:
                    st.error("OCR functionality not available. Please install pytesseract to use receipt scanning.")
                else:
                    with st.spinner("Scanning receipt..."):
                        # Process receipt
                        receipt_data = scan_receipt(image)
                        
                        if receipt_data and "amount" in receipt_data:
                            st.success("Receipt scanned successfully!")
                        
                            # Display extracted information
                            st.markdown("### Extracted Information")
                            st.markdown(f"**Amount:** ₹{receipt_data.get('amount', 0):.2f}")
                            if "date" in receipt_data:
                                st.markdown(f"**Date:** {receipt_data['date']}")
                            if "merchant" in receipt_data:
                                st.markdown(f"**Merchant:** {receipt_data['merchant']}")
                            
                            # Create transaction form
                            st.markdown("### Create Transaction")
                            
                            # Pre-fill amount if available
                            amount = st.number_input("Amount (₹)", 
                                                   value=float(receipt_data.get('amount', 0)), 
                                                   min_value=1.0, 
                                                   step=1.0,
                                                   key="camera_amount")
                            
                            # Pre-fill merchant as recipient if available
                            if "merchant" in receipt_data:
                                recipient = st.text_input("Recipient/Merchant", 
                                                        value=receipt_data['merchant'],
                                                        key="camera_recipient")
                            else:
                                recipient = st.text_input("Recipient/Merchant", key="camera_recipient")
                            
                            # Transaction type
                            transaction_type = st.selectbox("Transaction Type", 
                                                          ["send_money", "bill_payment", "shopping", "food", "travel", "entertainment", "other"],
                                                          key="camera_type")
                            
                            # Create transaction button
                            if st.button("Create Transaction", use_container_width=True, key="camera_create_transaction"):
                                if amount > 0 and recipient:
                                    # In a real app, we would verify if the recipient exists in the system
                                    # For this demo, we'll just create the transaction with the current user as sender
                                    success, message = add_transaction(
                                        st.session_state.current_user,
                                        recipient,
                                        amount,
                                        transaction_type
                                    )
                                    
                                    if success:
                                        # Calculate cashback
                                        points, cashback = calculate_cashback(
                                            st.session_state.current_user,
                                            amount,
                                            transaction_type
                                        )
                                        st.session_state.cashback_points += points
                                        
                                        st.success(f"Transaction of ₹{amount:.2f} to {recipient} created successfully! You earned {points} cashback points.")
                                    else:
                                        st.error(message)
                                else:
                                    if amount <= 0:
                                        st.error("Please enter a valid amount")
                                    if not recipient:
                                        st.error("Please enter a recipient/merchant")
                        else:
                            st.error("Could not extract payment information from the receipt. Please try again with a clearer image.")
    
    # OCR Tips
    st.markdown("---")
    st.markdown("### Tips for Better OCR Results")
    st.markdown("""
    1. Ensure good lighting when capturing the receipt
    2. Keep the receipt flat and avoid wrinkles
    3. Make sure the text is clearly visible and in focus
    4. Align the receipt properly within the frame
    5. Crop out unnecessary background elements
    """)
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()