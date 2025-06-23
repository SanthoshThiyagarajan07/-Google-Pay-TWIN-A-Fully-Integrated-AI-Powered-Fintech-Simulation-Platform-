def expense_prediction_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Expense Prediction</h1>", unsafe_allow_html=True)
    
    # Load transactions
    def load_transactions():
        data_dir = "data"
        transaction_file = os.path.join(data_dir, "transactions.json")
        if os.path.exists(transaction_file):
            with open(transaction_file, 'r') as f:
                return json.load(f)
        return []
    
    # Function to prepare transaction data for analysis
    def prepare_transaction_data(username):
        transactions = load_transactions()
        
        # Filter transactions for the current user
        user_transactions = []
        for tx in transactions:
            if tx['sender'] == username and tx['type'] in ['send', 'pay_later']:
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
        df['dayofweek'] = df['date'].dt.dayofweek  # Monday=0, Sunday=6
        df['week'] = df['date'].dt.isocalendar().week
        
        # Ensure category is present
        if 'category' not in df.columns:
            df['category'] = 'Other'
        
        # Fill missing categories
        df['category'] = df['category'].fillna('Other')
        
        return df
    
    # Function to aggregate transactions by time period
    def aggregate_by_period(df, period='daily'):
        if df is None or len(df) == 0:
            return None
        
        if period == 'daily':
            # Group by date
            df['date_only'] = df['date'].dt.date
            grouped = df.groupby('date_only').agg({'amount': 'sum'}).reset_index()
            grouped.rename(columns={'date_only': 'period'}, inplace=True)
            
        elif period == 'weekly':
            # Group by year and week
            df['year_week'] = df['date'].dt.strftime('%Y-%U')
            grouped = df.groupby('year_week').agg({'amount': 'sum'}).reset_index()
            grouped.rename(columns={'year_week': 'period'}, inplace=True)
            
        elif period == 'monthly':
            # Group by year and month
            df['year_month'] = df['date'].dt.strftime('%Y-%m')
            grouped = df.groupby('year_month').agg({'amount': 'sum'}).reset_index()
            grouped.rename(columns={'year_month': 'period'}, inplace=True)
            
        elif period == 'category':
            # Group by category
            grouped = df.groupby('category').agg({'amount': 'sum'}).reset_index()
            grouped.rename(columns={'category': 'period'}, inplace=True)
        
        return grouped
    
    # Function to prepare features for prediction
    def prepare_features_for_prediction(df, prediction_type='total'):
        if df is None or len(df) == 0:
            return None, None
        
        # For total spending prediction
        if prediction_type == 'total':
            # Group by date
            daily_spending = df.groupby(['year', 'month', 'day']).agg({'amount': 'sum'}).reset_index()
            
            # Create features: previous days' spending
            X = []
            y = []
            
            # Use last 7 days to predict next day
            for i in range(7, len(daily_spending)):
                features = []
                for j in range(1, 8):  # Last 7 days
                    features.append(daily_spending.iloc[i-j]['amount'])
                
                # Add day of week as a feature
                date = datetime(int(daily_spending.iloc[i]['year']), 
                               int(daily_spending.iloc[i]['month']), 
                               int(daily_spending.iloc[i]['day']))
                features.append(date.weekday())  # Monday=0, Sunday=6
                
                X.append(features)
                y.append(daily_spending.iloc[i]['amount'])
            
            if not X or not y:
                return None, None
            
            return np.array(X), np.array(y)
        
        # For category-based prediction
        elif prediction_type == 'category':
            # Get unique categories
            categories = df['category'].unique()
            
            # Group by date and category
            daily_category_spending = df.groupby(['year', 'month', 'day', 'category']).agg({'amount': 'sum'}).reset_index()
            
            # Create a complete date range
            start_date = df['date'].min().date()
            end_date = df['date'].max().date()
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Create a complete date-category grid
            date_category_grid = []
            for date in date_range:
                for category in categories:
                    date_category_grid.append({
                        'year': date.year,
                        'month': date.month,
                        'day': date.day,
                        'category': category
                    })
            
            # Convert to DataFrame
            grid_df = pd.DataFrame(date_category_grid)
            
            # Merge with actual spending data
            merged_df = pd.merge(
                grid_df,
                daily_category_spending,
                on=['year', 'month', 'day', 'category'],
                how='left'
            )
            
            # Fill missing values with 0
            merged_df['amount'] = merged_df['amount'].fillna(0)
            
            # Create features for each category
            X_dict = {}
            y_dict = {}
            
            for category in categories:
                category_df = merged_df[merged_df['category'] == category].sort_values(by=['year', 'month', 'day'])
                
                X_category = []
                y_category = []
                
                # Use last 7 days to predict next day
                for i in range(7, len(category_df)):
                    features = []
                    for j in range(1, 8):  # Last 7 days
                        features.append(category_df.iloc[i-j]['amount'])
                    
                    # Add day of week as a feature
                    date = datetime(int(category_df.iloc[i]['year']), 
                                   int(category_df.iloc[i]['month']), 
                                   int(category_df.iloc[i]['day']))
                    features.append(date.weekday())  # Monday=0, Sunday=6
                    
                    X_category.append(features)
                    y_category.append(category_df.iloc[i]['amount'])
                
                if X_category and y_category:
                    X_dict[category] = np.array(X_category)
                    y_dict[category] = np.array(y_category)
            
            return X_dict, y_dict
    
    # Function to train prediction model
    def train_prediction_model(X, y, model_type='linear'):
        if X is None or y is None or len(X) == 0 or len(y) == 0:
            return None
        
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        if model_type == 'linear':
            model = LinearRegression()
        else:  # random forest
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        return {
            'model': model,
            'scaler': scaler,
            'train_score': train_score,
            'test_score': test_score
        }
    
    # Function to make predictions
    def predict_expenses(model_dict, recent_data, prediction_days=30, prediction_type='total'):
        if model_dict is None or recent_data is None:
            return None
        
        model = model_dict['model']
        scaler = model_dict['scaler']
        
        # For total spending prediction
        if prediction_type == 'total':
            # Start with the most recent 7 days of data
            recent_amounts = recent_data[-7:]
            
            predictions = []
            dates = []
            
            current_date = datetime.now().date()
            
            for i in range(prediction_days):
                # Prepare features for prediction
                features = list(recent_amounts)
                
                # Add day of week
                prediction_date = current_date + timedelta(days=i+1)
                features.append(prediction_date.weekday())
                
                # Scale features
                features_scaled = scaler.transform([features])
                
                # Make prediction
                prediction = model.predict(features_scaled)[0]
                
                # Ensure prediction is non-negative
                prediction = max(0, prediction)
                
                # Add to predictions
                predictions.append(prediction)
                dates.append(prediction_date)
                
                # Update recent amounts for next prediction
                recent_amounts = recent_amounts[1:] + [prediction]
            
            return pd.DataFrame({'date': dates, 'predicted_amount': predictions})
        
        # For category-based prediction
        elif prediction_type == 'category':
            all_predictions = {}
            
            for category, category_dict in model_dict.items():
                if 'recent_data' not in category_dict or len(category_dict['recent_data']) < 7:
                    continue
                
                model = category_dict['model']
                scaler = category_dict['scaler']
                
                # Start with the most recent 7 days of data
                recent_amounts = category_dict['recent_data'][-7:]
                
                predictions = []
                dates = []
                
                current_date = datetime.now().date()
                
                for i in range(prediction_days):
                    # Prepare features for prediction
                    features = list(recent_amounts)
                    
                    # Add day of week
                    prediction_date = current_date + timedelta(days=i+1)
                    features.append(prediction_date.weekday())
                    
                    # Scale features
                    features_scaled = scaler.transform([features])
                    
                    # Make prediction
                    prediction = model.predict(features_scaled)[0]
                    
                    # Ensure prediction is non-negative
                    prediction = max(0, prediction)
                    
                    # Add to predictions
                    predictions.append(prediction)
                    dates.append(prediction_date)
                    
                    # Update recent amounts for next prediction
                    recent_amounts = recent_amounts[1:] + [prediction]
                
                all_predictions[category] = pd.DataFrame({'date': dates, 'predicted_amount': predictions})
            
            return all_predictions
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Total Expense Prediction", "Category Prediction", "Monthly Forecast"])
    
    with tab1:
        st.markdown("### Predict Your Future Expenses")
        st.write("This tool uses machine learning to predict your future expenses based on your spending history.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 14:  # Need at least 14 days of data (7 for features, 7 for training)
            st.warning("You need at least 14 days of transaction history for predictions. Please continue using the app to generate more data.")
        else:
            # Train model
            X, y = prepare_features_for_prediction(df, prediction_type='total')
            
            if X is None or y is None or len(X) == 0 or len(y) == 0:
                st.warning("Not enough data to train the prediction model. Please continue using the app to generate more data.")
            else:
                # Let user choose model type
                model_type = st.radio("Select prediction model", ["Linear Regression", "Random Forest"], horizontal=True)
                model_key = 'linear' if model_type == "Linear Regression" else 'random_forest'
                
                # Train model
                model_dict = train_prediction_model(X, y, model_key)
                
                if model_dict is None:
                    st.error("Failed to train the prediction model. Please try again later.")
                else:
                    # Display model performance
                    st.write(f"Model training score: {model_dict['train_score']:.2f}")
                    st.write(f"Model testing score: {model_dict['test_score']:.2f}")
                    
                    # Get recent data for prediction
                    daily_spending = df.groupby(['year', 'month', 'day']).agg({'amount': 'sum'}).reset_index()
                    recent_data = daily_spending['amount'].values[-7:]
                    
                    # Let user choose prediction period
                    prediction_days = st.slider("Number of days to predict", min_value=7, max_value=90, value=30, step=1)
                    
                    # Make predictions
                    predictions_df = predict_expenses(model_dict, recent_data, prediction_days, 'total')
                    
                    if predictions_df is None:
                        st.error("Failed to make predictions. Please try again later.")
                    else:
                        # Display predictions
                        st.markdown("### Predicted Daily Expenses")
                        
                        # Plot predictions
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(predictions_df['date'], predictions_df['predicted_amount'], marker='o', linestyle='-')
                        ax.set_xlabel('Date')
                        ax.set_ylabel('Predicted Amount (₹)')
                        ax.set_title('Predicted Daily Expenses')
                        ax.grid(True, alpha=0.3)
                        
                        # Format x-axis dates
                        fig.autofmt_xdate()
                        
                        # Add average line
                        avg_prediction = predictions_df['predicted_amount'].mean()
                        ax.axhline(y=avg_prediction, color='r', linestyle='--', alpha=0.7)
                        ax.text(predictions_df['date'].iloc[0], avg_prediction, f'Avg: ₹{avg_prediction:.2f}', 
                                verticalalignment='bottom', horizontalalignment='left', color='r')
                        
                        st.pyplot(fig)
                        
                        # Display summary statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Average Daily Expense", f"₹{predictions_df['predicted_amount'].mean():.2f}")
                        with col2:
                            st.metric("Total Predicted Expense", f"₹{predictions_df['predicted_amount'].sum():.2f}")
                        with col3:
                            st.metric("Max Daily Expense", f"₹{predictions_df['predicted_amount'].max():.2f}")
                        
                        # Display predictions table
                        with st.expander("View Detailed Predictions"):
                            # Format the date and amount columns
                            formatted_df = predictions_df.copy()
                            formatted_df['date'] = formatted_df['date'].dt.strftime('%Y-%m-%d') if hasattr(formatted_df['date'], 'dt') else formatted_df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
                            formatted_df['predicted_amount'] = formatted_df['predicted_amount'].apply(lambda x: f"₹{x:.2f}")
                            formatted_df.columns = ['Date', 'Predicted Amount']
                            
                            st.dataframe(formatted_df, use_container_width=True)
    
    with tab2:
        st.markdown("### Category-wise Expense Prediction")
        st.write("Predict your future expenses for each spending category.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 14:  # Need at least 14 days of data
            st.warning("You need at least 14 days of transaction history for category predictions. Please continue using the app to generate more data.")
        else:
            # Get unique categories with sufficient data
            category_counts = df['category'].value_counts()
            valid_categories = category_counts[category_counts >= 10].index.tolist()
            
            if not valid_categories:
                st.warning("Not enough data in any category for predictions. Please continue using the app to generate more category-specific data.")
            else:
                # Let user select category
                selected_category = st.selectbox("Select category to predict", valid_categories)
                
                # Filter data for selected category
                category_df = df[df['category'] == selected_category]
                
                # Prepare features for the selected category
                X_dict, y_dict = prepare_features_for_prediction(df, prediction_type='category')
                
                if X_dict is None or y_dict is None or selected_category not in X_dict:
                    st.warning(f"Not enough data for {selected_category} category. Please select another category or continue using the app.")
                else:
                    X_category = X_dict[selected_category]
                    y_category = y_dict[selected_category]
                    
                    # Let user choose model type
                    model_type = st.radio("Select prediction model", ["Linear Regression", "Random Forest"], horizontal=True, key="cat_model")
                    model_key = 'linear' if model_type == "Linear Regression" else 'random_forest'
                    
                    # Train model
                    model_dict = train_prediction_model(X_category, y_category, model_key)
                    
                    if model_dict is None:
                        st.error("Failed to train the prediction model. Please try again later.")
                    else:
                        # Display model performance
                        st.write(f"Model training score: {model_dict['train_score']:.2f}")
                        st.write(f"Model testing score: {model_dict['test_score']:.2f}")
                        
                        # Get recent data for prediction
                        # Group by date and category
                        daily_category_spending = df.groupby(['year', 'month', 'day', 'category']).agg({'amount': 'sum'}).reset_index()
                        category_data = daily_category_spending[daily_category_spending['category'] == selected_category]
                        recent_data = category_data['amount'].values[-7:] if len(category_data) >= 7 else np.zeros(7)
                        
                        # Let user choose prediction period
                        prediction_days = st.slider("Number of days to predict", min_value=7, max_value=90, value=30, step=1, key="cat_days")
                        
                        # Create a dictionary with the model and recent data
                        category_model_dict = {
                            'model': model_dict['model'],
                            'scaler': model_dict['scaler'],
                            'recent_data': recent_data
                        }
                        
                        # Make predictions
                        predictions_df = predict_expenses({'model': model_dict['model'], 'scaler': model_dict['scaler']}, recent_data, prediction_days, 'total')
                        
                        if predictions_df is None:
                            st.error("Failed to make predictions. Please try again later.")
                        else:
                            # Display predictions
                            st.markdown(f"### Predicted Daily Expenses for {selected_category}")
                            
                            # Plot predictions
                            fig, ax = plt.subplots(figsize=(10, 6))
                            ax.plot(predictions_df['date'], predictions_df['predicted_amount'], marker='o', linestyle='-')
                            ax.set_xlabel('Date')
                            ax.set_ylabel('Predicted Amount (₹)')
                            ax.set_title(f'Predicted Daily Expenses for {selected_category}')
                            ax.grid(True, alpha=0.3)
                            
                            # Format x-axis dates
                            fig.autofmt_xdate()
                            
                            # Add average line
                            avg_prediction = predictions_df['predicted_amount'].mean()
                            ax.axhline(y=avg_prediction, color='r', linestyle='--', alpha=0.7)
                            ax.text(predictions_df['date'].iloc[0], avg_prediction, f'Avg: ₹{avg_prediction:.2f}', 
                                    verticalalignment='bottom', horizontalalignment='left', color='r')
                            
                            st.pyplot(fig)
                            
                            # Display summary statistics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric(f"Average Daily {selected_category}", f"₹{predictions_df['predicted_amount'].mean():.2f}")
                            with col2:
                                st.metric(f"Total Predicted {selected_category}", f"₹{predictions_df['predicted_amount'].sum():.2f}")
                            with col3:
                                st.metric(f"Max Daily {selected_category}", f"₹{predictions_df['predicted_amount'].max():.2f}")
                            
                            # Display predictions table
                            with st.expander("View Detailed Predictions"):
                                # Format the date and amount columns
                                formatted_df = predictions_df.copy()
                                formatted_df['date'] = formatted_df['date'].dt.strftime('%Y-%m-%d') if hasattr(formatted_df['date'], 'dt') else formatted_df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
                                formatted_df['predicted_amount'] = formatted_df['predicted_amount'].apply(lambda x: f"₹{x:.2f}")
                                formatted_df.columns = ['Date', 'Predicted Amount']
                                
                                st.dataframe(formatted_df, use_container_width=True)
    
    with tab3:
        st.markdown("### Monthly Expense Forecast")
        st.write("Get a forecast of your total monthly expenses for the next few months.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 60:  # Need at least 60 days (2 months) of data
            st.warning("You need at least 2 months of transaction history for monthly forecasts. Please continue using the app to generate more data.")
        else:
            # Aggregate data by month
            df['year_month'] = df['date'].dt.strftime('%Y-%m')
            monthly_spending = df.groupby('year_month').agg({'amount': 'sum'}).reset_index()
            
            if len(monthly_spending) < 3:  # Need at least 3 months for meaningful forecast
                st.warning("You need at least 3 months of transaction history for monthly forecasts. Please continue using the app to generate more data.")
            else:
                # Display historical monthly spending
                st.markdown("### Historical Monthly Spending")
                
                # Plot historical data
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(monthly_spending['year_month'], monthly_spending['amount'])
                ax.set_xlabel('Month')
                ax.set_ylabel('Total Spending (₹)')
                ax.set_title('Historical Monthly Spending')
                ax.grid(True, alpha=0.3, axis='y')
                
                # Format x-axis labels
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                st.pyplot(fig)
                
                # Simple forecast using moving average
                st.markdown("### Monthly Forecast")
                
                # Let user choose forecast method
                forecast_method = st.radio("Select forecast method", ["Moving Average", "Linear Trend"], horizontal=True)
                
                # Let user choose number of months to forecast
                forecast_months = st.slider("Number of months to forecast", min_value=1, max_value=12, value=3, step=1)
                
                # Get historical amounts
                historical_amounts = monthly_spending['amount'].values
                
                # Generate month labels for forecast
                last_month = datetime.strptime(monthly_spending['year_month'].iloc[-1], '%Y-%m')
                forecast_labels = []
                for i in range(1, forecast_months + 1):
                    next_month = last_month + pd.DateOffset(months=i)
                    forecast_labels.append(next_month.strftime('%Y-%m'))
                
                # Make forecast
                if forecast_method == "Moving Average":
                    # Use last 3 months (or all if less than 3) for moving average
                    window_size = min(3, len(historical_amounts))
                    forecast_amounts = [np.mean(historical_amounts[-window_size:])] * forecast_months
                else:  # Linear Trend
                    # Fit linear regression to historical data
                    X = np.arange(len(historical_amounts)).reshape(-1, 1)
                    y = historical_amounts
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    # Predict next months
                    X_forecast = np.arange(len(historical_amounts), len(historical_amounts) + forecast_months).reshape(-1, 1)
                    forecast_amounts = model.predict(X_forecast)
                    
                    # Ensure non-negative predictions
                    forecast_amounts = np.maximum(forecast_amounts, 0)
                
                # Combine historical and forecast data for plotting
                all_months = list(monthly_spending['year_month']) + forecast_labels
                all_amounts = list(historical_amounts) + list(forecast_amounts)
                
                # Create DataFrame for display
                forecast_df = pd.DataFrame({
                    'Month': forecast_labels,
                    'Forecasted Amount': forecast_amounts
                })
                
                # Plot combined data
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # Plot historical data as bars
                ax.bar(monthly_spending['year_month'], monthly_spending['amount'], color='#4285F4', alpha=0.7, label='Historical')
                
                # Plot forecast data as bars with different color
                ax.bar(forecast_labels, forecast_amounts, color='#EA4335', alpha=0.7, label='Forecast')
                
                # Add trend line if using linear trend
                if forecast_method == "Linear Trend":
                    X_all = np.arange(len(all_months)).reshape(-1, 1)
                    y_trend = model.predict(X_all)
                    ax.plot(all_months, y_trend, 'k--', alpha=0.7, label='Trend Line')
                
                ax.set_xlabel('Month')
                ax.set_ylabel('Total Spending (₹)')
                ax.set_title('Monthly Spending Forecast')
                ax.grid(True, alpha=0.3, axis='y')
                ax.legend()
                
                # Format x-axis labels
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                st.pyplot(fig)
                
                # Display forecast table
                st.markdown("### Forecast Details")
                
                # Format the amount column
                forecast_df['Forecasted Amount'] = forecast_df['Forecasted Amount'].apply(lambda x: f"₹{x:.2f}")
                
                st.dataframe(forecast_df, use_container_width=True)
                
                # Calculate and display summary statistics
                historical_avg = np.mean(historical_amounts)
                forecast_avg = np.mean(forecast_amounts)
                percent_change = ((forecast_avg - historical_avg) / historical_avg) * 100 if historical_avg > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Historical Monthly Average", f"₹{historical_avg:.2f}")
                with col2:
                    st.metric("Forecasted Monthly Average", f"₹{forecast_avg:.2f}")
                with col3:
                    st.metric("Percent Change", f"{percent_change:.1f}%", 
                             delta=f"{percent_change:.1f}%", 
                             delta_color="inverse")
                
                # Provide insights based on forecast
                st.markdown("### Forecast Insights")
                
                if percent_change > 10:
                    st.warning(f"Your monthly expenses are forecasted to increase by {percent_change:.1f}%. Consider reviewing your spending habits and creating a budget to control expenses.")
                elif percent_change < -10:
                    st.success(f"Your monthly expenses are forecasted to decrease by {abs(percent_change):.1f}%. Great job managing your finances!")
                else:
                    st.info(f"Your monthly expenses are forecasted to remain relatively stable (change of {percent_change:.1f}%).")
                
                # Additional insights
                if len(historical_amounts) >= 3:
                    # Check for seasonality or patterns
                    if np.std(historical_amounts) > 0.2 * np.mean(historical_amounts):
                        st.info("Your monthly spending shows significant variation. Consider setting up a budget to help stabilize your expenses.")
                    
                    # Check for trend
                    if forecast_method == "Linear Trend" and model.coef_[0] > 0:
                        st.warning(f"Your spending shows an upward trend of approximately ₹{model.coef_[0]:.2f} per month. Consider strategies to reduce expenses if this doesn't align with your financial goals.")
                    elif forecast_method == "Linear Trend" and model.coef_[0] < 0:
                        st.success(f"Your spending shows a downward trend of approximately ₹{abs(model.coef_[0]):.2f} per month. Keep up the good work!")
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()