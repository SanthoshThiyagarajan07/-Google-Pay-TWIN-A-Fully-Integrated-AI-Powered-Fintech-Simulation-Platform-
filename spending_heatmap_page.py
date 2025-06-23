def spending_heatmap_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import matplotlib.pyplot as plt
    import seaborn as sns
    try:
        import calmap
    except ImportError:
        calmap = None
        print("Warning: calmap not installed or incompatible with Python 3.13. Calendar heatmap features may not work.")
    import plotly.express as px
    import plotly.graph_objects as go
    from matplotlib.colors import LinearSegmentedColormap
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Spending Heatmap</h1>", unsafe_allow_html=True)
    
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
        df['date_only'] = df['date'].dt.date
        
        # Ensure category is present
        if 'category' not in df.columns:
            df['category'] = 'Other'
        
        # Fill missing categories
        df['category'] = df['category'].fillna('Other')
        
        return df
    
    # Function to create daily spending data
    def create_daily_spending(df):
        if df is None or len(df) == 0:
            return None
        
        # Group by date and sum amounts
        daily_spending = df.groupby('date_only')['amount'].sum().reset_index()
        daily_spending['date'] = pd.to_datetime(daily_spending['date_only'])
        daily_spending.set_index('date', inplace=True)
        
        # Create a date range from the first to the last transaction date
        date_range = pd.date_range(start=daily_spending.index.min(), end=daily_spending.index.max(), freq='D')
        
        # Reindex to include all dates in the range
        daily_spending = daily_spending['amount'].reindex(date_range, fill_value=0)
        
        return daily_spending
    
    # Function to create monthly spending data
    def create_monthly_spending(df):
        if df is None or len(df) == 0:
            return None
        
        # Group by year and month and sum amounts
        df['year_month'] = df['date'].dt.to_period('M')
        monthly_spending = df.groupby('year_month')['amount'].sum().reset_index()
        monthly_spending['year_month_str'] = monthly_spending['year_month'].astype(str)
        
        return monthly_spending
    
    # Function to create category spending data
    def create_category_spending(df):
        if df is None or len(df) == 0 or 'category' not in df.columns:
            return None
        
        # Group by category and sum amounts
        category_spending = df.groupby('category')['amount'].sum().reset_index()
        
        return category_spending
    
    # Function to create weekday spending data
    def create_weekday_spending(df):
        if df is None or len(df) == 0 or 'dayofweek' not in df.columns:
            return None
        
        # Group by day of week and sum amounts
        weekday_spending = df.groupby('dayofweek')['amount'].sum().reset_index()
        
        # Map day of week numbers to names
        day_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        weekday_spending['day_name'] = weekday_spending['dayofweek'].map(day_map)
        
        return weekday_spending
    
    # Function to create hourly spending data
    def create_hourly_spending(df):
        if df is None or len(df) == 0 or 'date' not in df.columns:
            return None
        
        # Extract hour from date
        df['hour'] = df['date'].dt.hour
        
        # Group by hour and sum amounts
        hourly_spending = df.groupby('hour')['amount'].sum().reset_index()
        
        return hourly_spending
    
    # Function to create category by day heatmap data
    def create_category_day_heatmap(df):
        if df is None or len(df) == 0 or 'category' not in df.columns or 'dayofweek' not in df.columns:
            return None
        
        # Group by category and day of week and sum amounts
        heatmap_data = df.groupby(['category', 'dayofweek'])['amount'].sum().reset_index()
        
        # Pivot the data for heatmap
        pivot_data = heatmap_data.pivot(index='category', columns='dayofweek', values='amount')
        
        # Map day of week numbers to names
        day_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        pivot_data = pivot_data.rename(columns=day_map)
        
        return pivot_data
    
    # Function to create category by month heatmap data
    def create_category_month_heatmap(df):
        if df is None or len(df) == 0 or 'category' not in df.columns or 'month' not in df.columns:
            return None
        
        # Group by category and month and sum amounts
        heatmap_data = df.groupby(['category', 'month'])['amount'].sum().reset_index()
        
        # Pivot the data for heatmap
        pivot_data = heatmap_data.pivot(index='category', columns='month', values='amount')
        
        # Map month numbers to names
        month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        pivot_data = pivot_data.rename(columns=month_map)
        
        return pivot_data
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["Calendar Heatmap", "Category Heatmap", "Time Patterns", "Insights"])
    
    with tab1:
        st.markdown("### Spending Calendar Heatmap")
        st.write("Visualize your spending patterns over time with this calendar heatmap.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 5:  # Need at least 5 transactions for meaningful visualization
            st.warning("You need at least 5 transactions for the heatmap visualization. Please continue using the app to generate more transaction data.")
        else:
            # Create daily spending data
            daily_spending = create_daily_spending(df)
            
            if daily_spending is None:
                st.error("Failed to create daily spending data. Please try again later.")
            else:
                # Let user select time period
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=daily_spending.index.min().date())
                with col2:
                    end_date = st.date_input("End Date", value=daily_spending.index.max().date())
                
                # Filter data by selected date range
                filtered_data = daily_spending.loc[pd.to_datetime(start_date):pd.to_datetime(end_date)]
                
                # Create calendar heatmap
                st.markdown("#### Daily Spending Calendar")
                
                # Create a custom colormap (Google Pay blue to red)
                colors = ['#E8F0FE', '#4285F4', '#EA4335']
                cmap = LinearSegmentedColormap.from_list('google_cmap', colors)
                
                # Create figure and axis
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Plot calendar heatmap
                if calmap is not None:
                    calmap.yearplot(filtered_data, year=None, ax=ax, cmap=cmap, fillcolor='whitesmoke',
                                  linewidth=1, linecolor='white', daylabels='MTWTFSS')
                    
                    # Set title and labels
                    ax.set_title('Daily Spending Heatmap', fontsize=14)
                    ax.set_ylabel('')
                    
                    # Add colorbar
                    cbar = fig.colorbar(ax.get_children()[0], ax=ax, orientation='vertical', pad=0.02)
                    cbar.set_label('Amount (₹)', rotation=270, labelpad=15)
                    
                    st.pyplot(fig)
                else:
                    st.error("Calendar heatmap is not available due to calmap compatibility issues with Python 3.13. Please use the other visualization options below.")
                    plt.close(fig)  # Close the unused figure
                
                # Add explanation
                st.info("The calendar heatmap shows your spending patterns over time. Darker colors indicate higher spending on that day. Hover over a day to see the exact amount spent.")
                
                # Display monthly spending bar chart
                st.markdown("#### Monthly Spending Trends")
                
                # Create monthly spending data
                monthly_spending = create_monthly_spending(df)
                
                if monthly_spending is not None and len(monthly_spending) > 0:
                    # Create bar chart
                    fig = px.bar(monthly_spending, x='year_month_str', y='amount',
                               labels={'year_month_str': 'Month', 'amount': 'Amount (₹)'},
                               title='Monthly Spending',
                               color='amount',
                               color_continuous_scale=['#4285F4', '#EA4335'])
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Month",
                        yaxis_title="Amount (₹)",
                        coloraxis_showscale=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate month-over-month change
                    if len(monthly_spending) > 1:
                        monthly_spending['prev_month_amount'] = monthly_spending['amount'].shift(1)
                        monthly_spending['mom_change'] = (monthly_spending['amount'] - monthly_spending['prev_month_amount']) / monthly_spending['prev_month_amount'] * 100
                        monthly_spending['mom_change'] = monthly_spending['mom_change'].fillna(0)
                        
                        # Display month-over-month change for the latest month
                        latest_month = monthly_spending.iloc[-1]
                        mom_change = latest_month['mom_change']
                        
                        st.metric(
                            f"Month-over-Month Change ({latest_month['year_month_str']})",
                            f"{latest_month['amount']:.2f} ₹",
                            f"{mom_change:.1f}%",
                            delta_color="inverse"
                        )
                
                # Display spending statistics
                st.markdown("#### Spending Statistics")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Daily Spending", f"₹{filtered_data.mean():.2f}")
                with col2:
                    st.metric("Total Spending", f"₹{filtered_data.sum():.2f}")
                with col3:
                    st.metric("Highest Daily Spending", f"₹{filtered_data.max():.2f}")
                
                # Display spending distribution
                st.markdown("#### Spending Distribution")
                
                # Create histogram
                fig = px.histogram(filtered_data.reset_index(), x=0, nbins=20,
                               labels={0: 'Amount (₹)'},
                               title='Distribution of Daily Spending',
                               color_discrete_sequence=['#4285F4'])
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Amount (₹)",
                    yaxis_title="Number of Days"
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Category Heatmap")
        st.write("Explore your spending patterns across different categories and time periods.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 5 or 'category' not in df.columns:  # Need at least 5 transactions with categories
            st.warning("You need at least 5 categorized transactions for the category heatmap. Please continue using the app to generate more transaction data.")
        else:
            # Create category spending data
            category_spending = create_category_spending(df)
            
            if category_spending is None or len(category_spending) == 0:
                st.error("Failed to create category spending data. Please try again later.")
            else:
                # Display category spending bar chart
                st.markdown("#### Spending by Category")
                
                # Sort by amount descending
                category_spending = category_spending.sort_values('amount', ascending=False)
                
                # Create bar chart
                fig = px.bar(category_spending, x='category', y='amount',
                           labels={'category': 'Category', 'amount': 'Amount (₹)'},
                           title='Total Spending by Category',
                           color='amount',
                           color_continuous_scale=['#4285F4', '#EA4335'])
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Category",
                    yaxis_title="Amount (₹)",
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Create category by day heatmap
                st.markdown("#### Category by Day of Week Heatmap")
                
                # Create category by day heatmap data
                category_day_heatmap = create_category_day_heatmap(df)
                
                if category_day_heatmap is not None and not category_day_heatmap.empty:
                    # Create heatmap
                    fig = px.imshow(category_day_heatmap,
                                  labels=dict(x="Day of Week", y="Category", color="Amount (₹)"),
                                  x=category_day_heatmap.columns,
                                  y=category_day_heatmap.index,
                                  color_continuous_scale=['#E8F0FE', '#4285F4', '#EA4335'],
                                  title='Spending by Category and Day of Week')
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Day of Week",
                        yaxis_title="Category"
                    )
                    
                    # Add text annotations
                    fig.update_traces(text=category_day_heatmap.values.round(2), texttemplate="₹%{text}")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Find the highest spending category-day combination
                    max_value = category_day_heatmap.max().max()
                    max_category = category_day_heatmap.max(axis=1).idxmax()
                    max_day = category_day_heatmap.loc[max_category].idxmax()
                    
                    st.info(f"Your highest spending is on **{max_day}s** for **{max_category}** (₹{max_value:.2f}).")
                else:
                    st.warning("Not enough data to create category by day heatmap. Please continue using the app to generate more transaction data.")
                
                # Create category by month heatmap
                st.markdown("#### Category by Month Heatmap")
                
                # Create category by month heatmap data
                category_month_heatmap = create_category_month_heatmap(df)
                
                if category_month_heatmap is not None and not category_month_heatmap.empty:
                    # Create heatmap
                    fig = px.imshow(category_month_heatmap,
                                  labels=dict(x="Month", y="Category", color="Amount (₹)"),
                                  x=category_month_heatmap.columns,
                                  y=category_month_heatmap.index,
                                  color_continuous_scale=['#E8F0FE', '#4285F4', '#EA4335'],
                                  title='Spending by Category and Month')
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Month",
                        yaxis_title="Category"
                    )
                    
                    # Add text annotations
                    fig.update_traces(text=category_month_heatmap.values.round(2), texttemplate="₹%{text}")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Find the highest spending category-month combination
                    max_value = category_month_heatmap.max().max()
                    max_category = category_month_heatmap.max(axis=1).idxmax()
                    max_month = category_month_heatmap.loc[max_category].idxmax()
                    
                    st.info(f"Your highest spending is in **{max_month}** for **{max_category}** (₹{max_value:.2f}).")
                else:
                    st.warning("Not enough data to create category by month heatmap. Please continue using the app to generate more transaction data.")
    
    with tab3:
        st.markdown("### Time-based Spending Patterns")
        st.write("Analyze your spending patterns by day of week, time of day, and more.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 5:  # Need at least 5 transactions for meaningful visualization
            st.warning("You need at least 5 transactions for time-based pattern analysis. Please continue using the app to generate more transaction data.")
        else:
            # Create weekday spending data
            weekday_spending = create_weekday_spending(df)
            
            if weekday_spending is not None and len(weekday_spending) > 0:
                # Display weekday spending bar chart
                st.markdown("#### Spending by Day of Week")
                
                # Sort by day of week
                weekday_spending = weekday_spending.sort_values('dayofweek')
                
                # Create bar chart
                fig = px.bar(weekday_spending, x='day_name', y='amount',
                           labels={'day_name': 'Day of Week', 'amount': 'Amount (₹)'},
                           title='Total Spending by Day of Week',
                           color='amount',
                           color_continuous_scale=['#4285F4', '#EA4335'],
                           category_orders={"day_name": ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']})
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Day of Week",
                    yaxis_title="Amount (₹)",
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Find the highest and lowest spending days
                max_day = weekday_spending.loc[weekday_spending['amount'].idxmax()]
                min_day = weekday_spending.loc[weekday_spending['amount'].idxmin()]
                
                st.info(f"Your highest spending day is **{max_day['day_name']}** (₹{max_day['amount']:.2f}) and your lowest spending day is **{min_day['day_name']}** (₹{min_day['amount']:.2f}).")
            
            # Create hourly spending data
            hourly_spending = create_hourly_spending(df)
            
            if hourly_spending is not None and len(hourly_spending) > 0:
                # Display hourly spending bar chart
                st.markdown("#### Spending by Time of Day")
                
                # Create bar chart
                fig = px.bar(hourly_spending, x='hour', y='amount',
                           labels={'hour': 'Hour of Day (24h)', 'amount': 'Amount (₹)'},
                           title='Total Spending by Hour of Day',
                           color='amount',
                           color_continuous_scale=['#4285F4', '#EA4335'])
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Hour of Day (24h)",
                    yaxis_title="Amount (₹)",
                    coloraxis_showscale=False,
                    xaxis=dict(tickmode='linear', tick0=0, dtick=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Group hours into time periods
                hourly_spending['time_period'] = pd.cut(
                    hourly_spending['hour'],
                    bins=[0, 6, 12, 18, 24],
                    labels=['Night (0-6)', 'Morning (6-12)', 'Afternoon (12-18)', 'Evening (18-24)'],
                    right=False
                )
                
                # Group by time period and sum amounts
                time_period_spending = hourly_spending.groupby('time_period')['amount'].sum().reset_index()
                
                # Display time period spending pie chart
                st.markdown("#### Spending by Time Period")
                
                # Create pie chart
                fig = px.pie(time_period_spending, values='amount', names='time_period',
                           title='Spending Distribution by Time Period',
                           color_discrete_sequence=px.colors.sequential.Blues_r)
                
                # Update layout
                fig.update_layout(
                    legend_title="Time Period"
                )
                
                # Update traces
                fig.update_traces(textinfo='percent+label+value', texttemplate="%{label}<br>%{percent}<br>₹%{value:.2f}")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Find the highest spending time period
                max_period = time_period_spending.loc[time_period_spending['amount'].idxmax()]
                
                st.info(f"Your highest spending time period is **{max_period['time_period']}** (₹{max_period['amount']:.2f}).")
            
            # Create weekly spending data
            df['year_week'] = df['date'].dt.strftime('%Y-%U')
            weekly_spending = df.groupby('year_week')['amount'].sum().reset_index()
            
            if len(weekly_spending) > 1:
                # Display weekly spending line chart
                st.markdown("#### Weekly Spending Trends")
                
                # Create line chart
                fig = px.line(weekly_spending, x='year_week', y='amount',
                            labels={'year_week': 'Week', 'amount': 'Amount (₹)'},
                            title='Weekly Spending Trends',
                            markers=True)
                
                # Update layout
                fig.update_layout(
                    xaxis_title="Week",
                    yaxis_title="Amount (₹)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate week-over-week change
                weekly_spending['prev_week_amount'] = weekly_spending['amount'].shift(1)
                weekly_spending['wow_change'] = (weekly_spending['amount'] - weekly_spending['prev_week_amount']) / weekly_spending['prev_week_amount'] * 100
                weekly_spending['wow_change'] = weekly_spending['wow_change'].fillna(0)
                
                # Display week-over-week change for the latest week
                latest_week = weekly_spending.iloc[-1]
                wow_change = latest_week['wow_change']
                
                st.metric(
                    f"Week-over-Week Change ({latest_week['year_week']})",
                    f"{latest_week['amount']:.2f} ₹",
                    f"{wow_change:.1f}%",
                    delta_color="inverse"
                )
    
    with tab4:
        st.markdown("### Spending Insights")
        st.write("Get personalized insights about your spending patterns and habits.")
        
        # Prepare data
        df = prepare_transaction_data(st.session_state.current_user)
        
        if df is None or len(df) < 10:  # Need at least 10 transactions for meaningful insights
            st.warning("You need at least 10 transactions for spending insights. Please continue using the app to generate more transaction data.")
        else:
            # Generate insights
            insights = []
            
            # Insight 1: Highest spending category
            if 'category' in df.columns:
                category_spending = create_category_spending(df)
                if category_spending is not None and len(category_spending) > 0:
                    top_category = category_spending.sort_values('amount', ascending=False).iloc[0]
                    insights.append(f"Your highest spending category is **{top_category['category']}** (₹{top_category['amount']:.2f}).")
            
            # Insight 2: Highest spending day of week
            if 'dayofweek' in df.columns:
                weekday_spending = create_weekday_spending(df)
                if weekday_spending is not None and len(weekday_spending) > 0:
                    top_day = weekday_spending.sort_values('amount', ascending=False).iloc[0]
                    insights.append(f"You tend to spend the most on **{top_day['day_name']}s** (₹{top_day['amount']:.2f}).")
            
            # Insight 3: Spending trend
            df['year_month'] = df['date'].dt.to_period('M')
            monthly_spending = df.groupby('year_month')['amount'].sum()
            if len(monthly_spending) > 1:
                last_month = monthly_spending.iloc[-1]
                prev_month = monthly_spending.iloc[-2]
                percent_change = ((last_month - prev_month) / prev_month) * 100
                
                if percent_change > 10:
                    insights.append(f"Your spending increased by **{percent_change:.1f}%** compared to the previous month.")
                elif percent_change < -10:
                    insights.append(f"Your spending decreased by **{abs(percent_change):.1f}%** compared to the previous month.")
                else:
                    insights.append(f"Your spending remained relatively stable compared to the previous month (change of {percent_change:.1f}%).")
            
            # Insight 4: Spending variability
            daily_spending = create_daily_spending(df)
            if daily_spending is not None and len(daily_spending) > 0:
                # Calculate coefficient of variation (CV) to measure spending variability
                cv = daily_spending.std() / daily_spending.mean() if daily_spending.mean() > 0 else 0
                
                if cv > 1.5:
                    insights.append("Your spending shows **high variability**, with significant differences between high and low spending days.")
                elif cv > 0.5:
                    insights.append("Your spending shows **moderate variability** from day to day.")
                else:
                    insights.append("Your spending is **relatively consistent** from day to day.")
            
            # Insight 5: Weekend vs. weekday spending
            if 'dayofweek' in df.columns:
                weekday_mask = (df['dayofweek'] < 5)  # Monday to Friday
                weekend_mask = (df['dayofweek'] >= 5)  # Saturday and Sunday
                
                weekday_total = df[weekday_mask]['amount'].sum()
                weekend_total = df[weekend_mask]['amount'].sum()
                
                weekday_days = weekday_mask.sum()
                weekend_days = weekend_mask.sum()
                
                if weekday_days > 0 and weekend_days > 0:
                    weekday_avg = weekday_total / weekday_days
                    weekend_avg = weekend_total / weekend_days
                    
                    if weekend_avg > weekday_avg * 1.5:
                        insights.append(f"You spend **{weekend_avg/weekday_avg:.1f}x more** on weekends compared to weekdays.")
                    elif weekday_avg > weekend_avg * 1.5:
                        insights.append(f"You spend **{weekday_avg/weekend_avg:.1f}x more** on weekdays compared to weekends.")
            
            # Insight 6: Time of day spending pattern
            hourly_spending = create_hourly_spending(df)
            if hourly_spending is not None and len(hourly_spending) > 0:
                # Group hours into time periods
                hourly_spending['time_period'] = pd.cut(
                    hourly_spending['hour'],
                    bins=[0, 6, 12, 18, 24],
                    labels=['Night (0-6)', 'Morning (6-12)', 'Afternoon (12-18)', 'Evening (18-24)'],
                    right=False
                )
                
                # Group by time period and sum amounts
                time_period_spending = hourly_spending.groupby('time_period')['amount'].sum().reset_index()
                
                if len(time_period_spending) > 0:
                    top_period = time_period_spending.sort_values('amount', ascending=False).iloc[0]
                    insights.append(f"You tend to spend the most during the **{top_period['time_period']}** hours.")
            
            # Insight 7: Large transactions
            if len(df) > 0:
                # Define large transactions as those above 95th percentile
                large_threshold = df['amount'].quantile(0.95)
                large_txns = df[df['amount'] > large_threshold]
                
                if len(large_txns) > 0:
                    insights.append(f"You have made **{len(large_txns)}** large transactions (above ₹{large_threshold:.2f}), which account for **{large_txns['amount'].sum() / df['amount'].sum() * 100:.1f}%** of your total spending.")
            
            # Insight 8: Category diversity
            if 'category' in df.columns:
                category_count = df['category'].nunique()
                if category_count > 5:
                    insights.append(f"Your spending is **diverse**, spread across **{category_count}** different categories.")
                elif category_count > 1:
                    insights.append(f"Your spending is **moderately diverse**, spread across **{category_count}** different categories.")
                else:
                    insights.append("Your spending is **concentrated** in a single category.")
            
            # Display insights
            st.markdown("#### Your Personalized Spending Insights")
            
            for i, insight in enumerate(insights, 1):
                st.markdown(f"**{i}. {insight}**")
            
            # Display spending summary
            st.markdown("#### Spending Summary")
            
            # Calculate summary statistics
            total_spent = df['amount'].sum()
            avg_daily = daily_spending.mean() if daily_spending is not None else 0
            transaction_count = len(df)
            avg_transaction = df['amount'].mean()
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Spent", f"₹{total_spent:.2f}")
                st.metric("Average Daily Spending", f"₹{avg_daily:.2f}")
            with col2:
                st.metric("Total Transactions", f"{transaction_count}")
                st.metric("Average Transaction", f"₹{avg_transaction:.2f}")
            
            # Display spending recommendations
            st.markdown("#### Recommendations")
            
            recommendations = []
            
            # Recommendation 1: Based on highest spending category
            if 'category' in df.columns:
                category_spending = create_category_spending(df)
                if category_spending is not None and len(category_spending) > 1:
                    top_category = category_spending.sort_values('amount', ascending=False).iloc[0]
                    recommendations.append(f"Consider setting a budget for your highest spending category (**{top_category['category']}**) to control expenses.")
            
            # Recommendation 2: Based on spending variability
            if daily_spending is not None and len(daily_spending) > 0:
                cv = daily_spending.std() / daily_spending.mean() if daily_spending.mean() > 0 else 0
                if cv > 1.0:
                    recommendations.append("Try to make your spending more consistent to avoid financial stress during high-spending days.")
            
            # Recommendation 3: Based on weekend vs. weekday spending
            if 'dayofweek' in df.columns:
                weekday_mask = (df['dayofweek'] < 5)  # Monday to Friday
                weekend_mask = (df['dayofweek'] >= 5)  # Saturday and Sunday
                
                weekday_total = df[weekday_mask]['amount'].sum()
                weekend_total = df[weekend_mask]['amount'].sum()
                
                weekday_days = weekday_mask.sum()
                weekend_days = weekend_mask.sum()
                
                if weekday_days > 0 and weekend_days > 0:
                    weekday_avg = weekday_total / weekday_days
                    weekend_avg = weekend_total / weekend_days
                    
                    if weekend_avg > weekday_avg * 2:
                        recommendations.append("Consider planning more affordable weekend activities to reduce your weekend spending.")
            
            # Recommendation 4: Based on spending trend
            if len(monthly_spending) > 1:
                last_month = monthly_spending.iloc[-1]
                prev_month = monthly_spending.iloc[-2]
                percent_change = ((last_month - prev_month) / prev_month) * 100
                
                if percent_change > 20:
                    recommendations.append("Your spending has increased significantly. Review your recent expenses to identify areas where you can cut back.")
            
            # Recommendation 5: General recommendation
            recommendations.append("Use the Budget Alerts feature to set spending limits for different categories and receive notifications when you approach your limits.")
            
            # Display recommendations
            for i, recommendation in enumerate(recommendations, 1):
                st.markdown(f"**{i}. {recommendation}**")
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()