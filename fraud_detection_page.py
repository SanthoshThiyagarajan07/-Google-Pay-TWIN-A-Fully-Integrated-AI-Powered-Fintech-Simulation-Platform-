def fraud_detection_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Fraud Detection</h1>", unsafe_allow_html=True)
    
    # Load transactions
    def load_transactions():
        if os.path.exists('transactions.json'):
            with open('transactions.json', 'r') as f:
                return json.load(f)
        return []
    
    # Function to prepare transaction data for analysis
    def prepare_transaction_data(username):
        transactions = load_transactions()
        
        # Filter transactions for the current user
        user_transactions = []
        for tx in transactions:
            if tx['sender'] == username or tx['receiver'] == username:
                user_transactions.append(tx)
        
        if not user_transactions:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(user_transactions)
        
        # Convert date strings to datetime objects
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract date components
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['hour'] = df['date'].dt.hour
        df['dayofweek'] = df['date'].dt.dayofweek  # Monday=0, Sunday=6
        
        # Add transaction direction (sent or received)
        df['direction'] = df.apply(lambda row: 'sent' if row['sender'] == username else 'received', axis=1)
        
        # Ensure category is present
        if 'category' not in df.columns:
            df['category'] = 'Other'
        
        # Fill missing categories
        df['category'] = df['category'].fillna('Other')
        
        return df
    
    # Function to detect anomalies using Isolation Forest
    def detect_anomalies(df, contamination=0.05):
        if df is None or len(df) < 10:  # Need at least 10 transactions for meaningful anomaly detection
            return None, None
        
        # Select features for anomaly detection
        features = ['amount']
        
        # Add time-based features if available
        if 'hour' in df.columns:
            features.append('hour')
        if 'dayofweek' in df.columns:
            features.append('dayofweek')
        
        # Extract features
        X = df[features].copy()
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train Isolation Forest model
        model = IsolationForest(contamination=contamination, random_state=42)
        df['anomaly'] = model.fit_predict(X_scaled)
        
        # Convert predictions: -1 for anomalies, 1 for normal points
        df['anomaly'] = df['anomaly'].map({1: 0, -1: 1})  # 0 for normal, 1 for anomaly
        
        # Calculate anomaly score (higher score = more anomalous)
        df['anomaly_score'] = -model.decision_function(X_scaled)
        
        # Get anomalies
        anomalies = df[df['anomaly'] == 1].copy()
        
        return df, anomalies
    
    # Function to analyze transaction patterns
    def analyze_transaction_patterns(df):
        if df is None or len(df) < 5:  # Need at least 5 transactions for meaningful analysis
            return None
        
        # Analyze transaction amounts
        amount_stats = {
            'mean': df['amount'].mean(),
            'median': df['amount'].median(),
            'std': df['amount'].std(),
            'min': df['amount'].min(),
            'max': df['amount'].max(),
            'q1': df['amount'].quantile(0.25),
            'q3': df['amount'].quantile(0.75)
        }
        
        # Analyze transaction frequency
        if 'date' in df.columns:
            # Group by date and count transactions
            daily_counts = df.groupby(df['date'].dt.date).size().reset_index(name='count')
            frequency_stats = {
                'mean_daily': daily_counts['count'].mean(),
                'max_daily': daily_counts['count'].max(),
                'total_days': len(daily_counts),
                'total_transactions': len(df)
            }
        else:
            frequency_stats = None
        
        # Analyze transaction categories if available
        if 'category' in df.columns:
            category_counts = df['category'].value_counts().to_dict()
        else:
            category_counts = None
        
        # Analyze transaction directions if available
        if 'direction' in df.columns:
            direction_counts = df['direction'].value_counts().to_dict()
        else:
            direction_counts = None
        
        return {
            'amount_stats': amount_stats,
            'frequency_stats': frequency_stats,
            'category_counts': category_counts,
            'direction_counts': direction_counts
        }
    
    # Function to generate security tips based on transaction patterns
    def generate_security_tips(df, anomalies):
        tips = [
            "Regularly monitor your transaction history for any unauthorized activity.",
            "Never share your OTP or password with anyone, including bank representatives.",
            "Use strong, unique passwords for your financial accounts.",
            "Enable two-factor authentication for added security.",
            "Be cautious of phishing attempts via email, SMS, or phone calls."
        ]
        
        # Add specific tips based on transaction patterns
        if df is not None and len(df) > 0:
            # Check for large transactions
            large_txns = df[df['amount'] > df['amount'].quantile(0.95)]
            if len(large_txns) > 0:
                tips.append("Consider setting up alerts for large transactions above ₹" + 
                           str(int(df['amount'].quantile(0.95))) + ".")
            
            # Check for unusual times if hour data is available
            if 'hour' in df.columns:
                night_txns = df[(df['hour'] >= 22) | (df['hour'] <= 5)]
                if len(night_txns) > 0:
                    tips.append("Be extra vigilant about transactions made during late night hours (10 PM - 5 AM).")
            
            # Check for frequent small transactions
            small_txns = df[df['amount'] < df['amount'].quantile(0.1)]
            if len(small_txns) > 10:
                tips.append("Watch out for multiple small transactions, which could be test transactions before a larger fraud attempt.")
        
        # Add specific tips based on detected anomalies
        if anomalies is not None and len(anomalies) > 0:
            tips.append("Review the flagged suspicious transactions and report any unauthorized activity immediately.")
            
            # Check for anomalies with very high amounts
            high_amount_anomalies = anomalies[anomalies['amount'] > anomalies['amount'].median() * 2]
            if len(high_amount_anomalies) > 0:
                tips.append("Consider setting a transaction limit for your account to prevent large unauthorized transfers.")
        
        return tips
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Fraud Detection", "Transaction Analysis", "Security Tips"])
    
    with tab1:
        st.markdown("### Detect Suspicious Transactions")
        st.write("Our AI-powered fraud detection system analyzes your transaction patterns to identify potentially suspicious activities.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 10:  # Need at least 10 transactions for meaningful anomaly detection
            st.warning("You need at least 10 transactions for fraud detection. Please continue using the app to generate more transaction data.")
        else:
            # Let user adjust sensitivity
            sensitivity = st.slider("Detection Sensitivity", min_value=0.01, max_value=0.20, value=0.05, step=0.01,
                                  help="Higher values will flag more transactions as suspicious. Lower values will be more selective.")
            
            # Detect anomalies
            df_with_anomalies, anomalies = detect_anomalies(df, contamination=sensitivity)
            
            if anomalies is None or len(anomalies) == 0:
                st.success("No suspicious transactions detected with current sensitivity settings.")
            else:
                # Display summary
                st.warning(f"Detected {len(anomalies)} potentially suspicious transactions out of {len(df)} total transactions.")
                
                # Display anomalies
                st.markdown("### Suspicious Transactions")
                
                # Format anomalies for display
                display_anomalies = anomalies.copy()
                display_anomalies['date'] = display_anomalies['date'].dt.strftime('%Y-%m-%d %H:%M')
                display_anomalies['amount'] = display_anomalies['amount'].apply(lambda x: f"₹{x:.2f}")
                display_anomalies['anomaly_score'] = display_anomalies['anomaly_score'].apply(lambda x: f"{x:.2f}")
                
                # Select columns to display
                display_cols = ['date', 'sender', 'receiver', 'amount', 'category', 'direction', 'anomaly_score']
                display_cols = [col for col in display_cols if col in display_anomalies.columns]
                
                # Rename columns for better display
                column_rename = {
                    'date': 'Date & Time',
                    'sender': 'Sender',
                    'receiver': 'Receiver',
                    'amount': 'Amount',
                    'category': 'Category',
                    'direction': 'Direction',
                    'anomaly_score': 'Risk Score'
                }
                
                display_anomalies = display_anomalies[display_cols].rename(columns=column_rename)
                
                # Sort by anomaly score (descending)
                display_anomalies = display_anomalies.sort_values(by='Risk Score', ascending=False)
                
                st.dataframe(display_anomalies, use_container_width=True)
                
                # Visualize anomalies
                st.markdown("### Visualization of Suspicious Transactions")
                
                # Create a scatter plot of amount vs. date with anomalies highlighted
                fig = px.scatter(df_with_anomalies, x='date', y='amount', color='anomaly',
                                color_discrete_map={0: '#4285F4', 1: '#EA4335'},
                                labels={'date': 'Date', 'amount': 'Amount (₹)', 'anomaly': 'Suspicious'},
                                title='Transaction Amount Over Time',
                                hover_data=['sender', 'receiver', 'category', 'anomaly_score'])
                
                # Update hover template
                fig.update_traces(hovertemplate='<b>Date:</b> %{x}<br><b>Amount:</b> ₹%{y:.2f}<br><b>Sender:</b> %{customdata[0]}<br><b>Receiver:</b> %{customdata[1]}<br><b>Category:</b> %{customdata[2]}<br><b>Risk Score:</b> %{customdata[3]:.2f}')
                
                # Update layout
                fig.update_layout(
                    legend_title_text='Suspicious',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    xaxis_title="Date",
                    yaxis_title="Amount (₹)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add explanation
                st.info("The chart above shows all your transactions over time. Suspicious transactions are highlighted in red. The higher the risk score, the more unusual the transaction is compared to your normal patterns.")
                
                # Add action buttons
                st.markdown("### Actions")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Report Suspicious Activity", use_container_width=True):
                        st.session_state.show_report_form = True
                with col2:
                    if st.button("Mark All as Reviewed", use_container_width=True):
                        st.success("All transactions marked as reviewed.")
                
                # Show report form if button was clicked
                if st.session_state.get('show_report_form', False):
                    st.markdown("### Report Suspicious Activity")
                    with st.form("report_form"):
                        # Select transaction to report
                        transaction_options = [f"{row['Date & Time']} - {row['Amount']} ({row['Sender']} → {row['Receiver']})" 
                                              for _, row in display_anomalies.iterrows()]
                        selected_transaction = st.selectbox("Select Transaction to Report", transaction_options)
                        
                        # Report details
                        report_reason = st.selectbox("Reason for Report", [
                            "I did not make this transaction",
                            "The amount is incorrect",
                            "I don't recognize the recipient",
                            "Duplicate transaction",
                            "Other (please specify)"
                        ])
                        
                        # Additional details if "Other" is selected
                        if report_reason == "Other (please specify)":
                            report_details = st.text_area("Please provide details")
                        
                        # Contact information
                        contact_preference = st.radio("Preferred contact method", ["Email", "Phone", "In-app notification"])
                        
                        # Submit button
                        submitted = st.form_submit_button("Submit Report")
                        
                        if submitted:
                            st.success("Your report has been submitted. Our security team will review it and contact you within 24 hours.")
                            st.session_state.show_report_form = False
    
    with tab2:
        st.markdown("### Transaction Pattern Analysis")
        st.write("Understand your transaction patterns to better identify unusual activities.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 5:  # Need at least 5 transactions for meaningful analysis
            st.warning("You need at least 5 transactions for pattern analysis. Please continue using the app to generate more transaction data.")
        else:
            # Analyze transaction patterns
            patterns = analyze_transaction_patterns(df)
            
            if patterns is None:
                st.error("Failed to analyze transaction patterns. Please try again later.")
            else:
                # Display transaction amount statistics
                st.markdown("### Transaction Amount Statistics")
                
                # Create metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Transaction", f"₹{patterns['amount_stats']['mean']:.2f}")
                with col2:
                    st.metric("Median Transaction", f"₹{patterns['amount_stats']['median']:.2f}")
                with col3:
                    st.metric("Largest Transaction", f"₹{patterns['amount_stats']['max']:.2f}")
                
                # Create a histogram of transaction amounts
                fig = px.histogram(df, x='amount', nbins=20, title='Distribution of Transaction Amounts',
                                 labels={'amount': 'Amount (₹)', 'count': 'Number of Transactions'})
                
                # Add a vertical line for the mean
                fig.add_vline(x=patterns['amount_stats']['mean'], line_dash="dash", line_color="red",
                            annotation_text=f"Mean: ₹{patterns['amount_stats']['mean']:.2f}",
                            annotation_position="top right")
                
                # Add a vertical line for the median
                fig.add_vline(x=patterns['amount_stats']['median'], line_dash="dash", line_color="green",
                            annotation_text=f"Median: ₹{patterns['amount_stats']['median']:.2f}",
                            annotation_position="top left")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display transaction frequency statistics if available
                if patterns['frequency_stats'] is not None:
                    st.markdown("### Transaction Frequency")
                    
                    # Create metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Daily Transactions", f"{patterns['frequency_stats']['mean_daily']:.1f}")
                    with col2:
                        st.metric("Maximum Daily Transactions", f"{patterns['frequency_stats']['max_daily']}")
                    with col3:
                        st.metric("Total Transactions", f"{patterns['frequency_stats']['total_transactions']}")
                    
                    # Create a bar chart of daily transaction counts
                    daily_counts = df.groupby(df['date'].dt.date).size().reset_index(name='count')
                    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
                    
                    fig = px.bar(daily_counts, x='date', y='count', title='Daily Transaction Counts',
                               labels={'date': 'Date', 'count': 'Number of Transactions'})
                    
                    # Add a horizontal line for the mean
                    fig.add_hline(y=patterns['frequency_stats']['mean_daily'], line_dash="dash", line_color="red",
                                annotation_text=f"Mean: {patterns['frequency_stats']['mean_daily']:.1f}",
                                annotation_position="top right")
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display transaction categories if available
                if patterns['category_counts'] is not None and len(patterns['category_counts']) > 0:
                    st.markdown("### Transaction Categories")
                    
                    # Create a pie chart of transaction categories
                    category_df = pd.DataFrame({
                        'category': list(patterns['category_counts'].keys()),
                        'count': list(patterns['category_counts'].values())
                    })
                    
                    fig = px.pie(category_df, values='count', names='category', title='Transaction Categories',
                               hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display transaction directions if available
                if patterns['direction_counts'] is not None and len(patterns['direction_counts']) > 0:
                    st.markdown("### Transaction Directions")
                    
                    # Create a pie chart of transaction directions
                    direction_df = pd.DataFrame({
                        'direction': list(patterns['direction_counts'].keys()),
                        'count': list(patterns['direction_counts'].values())
                    })
                    
                    # Map direction names for better display
                    direction_map = {'sent': 'Sent', 'received': 'Received'}
                    direction_df['direction'] = direction_df['direction'].map(direction_map)
                    
                    fig = px.pie(direction_df, values='count', names='direction', title='Transaction Directions',
                               hole=0.4, color_discrete_sequence=['#4285F4', '#34A853'])
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display transaction time patterns if hour data is available
                if 'hour' in df.columns:
                    st.markdown("### Transaction Time Patterns")
                    
                    # Create a histogram of transaction hours
                    hour_counts = df['hour'].value_counts().reset_index()
                    hour_counts.columns = ['hour', 'count']
                    hour_counts = hour_counts.sort_values('hour')
                    
                    fig = px.bar(hour_counts, x='hour', y='count', title='Transactions by Hour of Day',
                               labels={'hour': 'Hour of Day (24h)', 'count': 'Number of Transactions'})
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Highlight unusual patterns
                    night_txns = df[(df['hour'] >= 22) | (df['hour'] <= 5)]
                    if len(night_txns) > 0:
                        st.warning(f"You have {len(night_txns)} transactions during late night hours (10 PM - 5 AM). These are more likely to be flagged as suspicious.")
                
                # Display transaction day of week patterns if dayofweek data is available
                if 'dayofweek' in df.columns:
                    # Create a histogram of transaction days of week
                    dow_counts = df['dayofweek'].value_counts().reset_index()
                    dow_counts.columns = ['dayofweek', 'count']
                    dow_counts = dow_counts.sort_values('dayofweek')
                    
                    # Map day of week numbers to names
                    day_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
                    dow_counts['day_name'] = dow_counts['dayofweek'].map(day_map)
                    
                    fig = px.bar(dow_counts, x='day_name', y='count', title='Transactions by Day of Week',
                               labels={'day_name': 'Day of Week', 'count': 'Number of Transactions'},
                               category_orders={"day_name": list(day_map.values())})
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Security Tips & Recommendations")
        st.write("Stay safe with these personalized security recommendations based on your transaction patterns.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 5:  # Need at least 5 transactions for meaningful analysis
            st.warning("You need at least 5 transactions for personalized security tips. Please continue using the app to generate more transaction data.")
            
            # Display generic security tips
            st.markdown("### General Security Tips")
            generic_tips = [
                "Never share your OTP or password with anyone, including bank representatives.",
                "Use strong, unique passwords for your financial accounts.",
                "Enable two-factor authentication for added security.",
                "Be cautious of phishing attempts via email, SMS, or phone calls.",
                "Regularly monitor your transaction history for any unauthorized activity.",
                "Avoid using public Wi-Fi for financial transactions.",
                "Keep your app and device updated with the latest security patches.",
                "Set up transaction alerts to be notified of all account activities.",
                "Be wary of unsolicited calls or messages asking for your financial information.",
                "Report suspicious activities immediately to prevent further fraud."
            ]
            
            for i, tip in enumerate(generic_tips, 1):
                st.markdown(f"**{i}. {tip}**")
        else:
            # Detect anomalies with default sensitivity
            df_with_anomalies, anomalies = detect_anomalies(df, contamination=0.05)
            
            # Generate security tips based on transaction patterns
            tips = generate_security_tips(df, anomalies)
            
            # Display personalized security tips
            st.markdown("### Personalized Security Recommendations")
            
            for i, tip in enumerate(tips, 1):
                st.markdown(f"**{i}. {tip}**")
            
            # Display security score
            st.markdown("### Your Security Score")
            
            # Calculate a simple security score based on transaction patterns
            security_score = 100  # Start with perfect score
            
            # Deduct points for anomalies
            if anomalies is not None and len(anomalies) > 0:
                security_score -= min(30, len(anomalies) * 5)  # Deduct 5 points per anomaly, up to 30 points
            
            # Deduct points for large transactions
            large_txns = df[df['amount'] > df['amount'].quantile(0.95)]
            if len(large_txns) > 0:
                security_score -= min(10, len(large_txns) * 2)  # Deduct 2 points per large transaction, up to 10 points
            
            # Deduct points for night transactions if hour data is available
            if 'hour' in df.columns:
                night_txns = df[(df['hour'] >= 22) | (df['hour'] <= 5)]
                if len(night_txns) > 0:
                    security_score -= min(10, len(night_txns) * 2)  # Deduct 2 points per night transaction, up to 10 points
            
            # Ensure score is between 0 and 100
            security_score = max(0, min(100, security_score))
            
            # Determine score category
            if security_score >= 90:
                score_category = "Excellent"
                score_color = "#34A853"  # Green
            elif security_score >= 70:
                score_category = "Good"
                score_color = "#FBBC05"  # Yellow
            elif security_score >= 50:
                score_category = "Fair"
                score_color = "#FA7B17"  # Orange
            else:
                score_category = "Poor"
                score_color = "#EA4335"  # Red
            
            # Display score with gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=security_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Security Score: {score_category}"},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': score_color},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 50], 'color': "#EA4335"},  # Red
                        {'range': [50, 70], 'color': "#FA7B17"},  # Orange
                        {'range': [70, 90], 'color': "#FBBC05"},  # Yellow
                        {'range': [90, 100], 'color': "#34A853"}  # Green
                    ],
                }
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=50, b=20),
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display score explanation
            st.markdown("### Score Explanation")
            
            score_explanation = [
                f"Your security score is **{security_score}/100** ({score_category}).",
                "This score is based on an analysis of your transaction patterns and potential security risks.",
                "Factors that affect your score include:"
            ]
            
            st.markdown("\n".join(score_explanation))
            
            # List factors affecting score
            factors = []
            
            if anomalies is not None and len(anomalies) > 0:
                factors.append(f"- **Suspicious transactions:** {len(anomalies)} potentially unusual transactions detected")
            
            if 'hour' in df.columns:
                night_txns = df[(df['hour'] >= 22) | (df['hour'] <= 5)]
                if len(night_txns) > 0:
                    factors.append(f"- **Late night activity:** {len(night_txns)} transactions during late night hours (10 PM - 5 AM)")
            
            large_txns = df[df['amount'] > df['amount'].quantile(0.95)]
            if len(large_txns) > 0:
                factors.append(f"- **Large transactions:** {len(large_txns)} unusually large transactions")
            
            if not factors:
                factors.append("- Your transaction patterns appear normal and secure")
            
            for factor in factors:
                st.markdown(factor)
            
            # Display security improvement suggestions
            st.markdown("### How to Improve Your Score")
            
            improvements = []
            
            if security_score < 100:
                if anomalies is not None and len(anomalies) > 0:
                    improvements.append("- Review and report any suspicious transactions you don't recognize")
                
                if 'hour' in df.columns and len(night_txns) > 0:
                    improvements.append("- Avoid making transactions during late night hours when possible")
                
                if len(large_txns) > 0:
                    improvements.append("- Set up transaction limits and alerts for large transactions")
                
                improvements.append("- Enable two-factor authentication for added security")
                improvements.append("- Regularly update your password with a strong, unique combination")
            else:
                improvements.append("- Your security practices are excellent! Continue monitoring your account regularly.")
            
            for improvement in improvements:
                st.markdown(improvement)
    
    # Initialize session state variables if not already set
    if 'show_report_form' not in st.session_state:
        st.session_state.show_report_form = False
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()