def investment_tracker_page():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import json
    import os
    from datetime import datetime, timedelta
    import plotly.express as px
    import plotly.graph_objects as go
    import matplotlib.pyplot as plt
    import seaborn as sns
    from PIL import Image
    import io
    import base64
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Investment Tracker</h1>", unsafe_allow_html=True)
    
    # Load investments data
    def load_investments():
        if os.path.exists('investments.json'):
            with open('investments.json', 'r') as f:
                return json.load(f)
        return []
    
    # Save investments data
    def save_investments(investments_data):
        with open('investments.json', 'w') as f:
            json.dump(investments_data, f, indent=4)
    
    # Load transactions data
    def load_transactions():
        if os.path.exists('transactions.json'):
            with open('transactions.json', 'r') as f:
                return json.load(f)
        return []
    
    # Save transactions data
    def save_transactions(transactions_data):
        with open('transactions.json', 'w') as f:
            json.dump(transactions_data, f, indent=4)
    
    # Function to calculate investment returns
    def calculate_returns(initial_amount, current_amount, start_date, end_date=None):
        if end_date is None:
            end_date = datetime.now().date()
        else:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        # Calculate time period in years
        days_diff = (end_date - start_date).days
        years = days_diff / 365.25
        
        if years < 0.01:  # Less than ~3-4 days
            return {
                "absolute_return": current_amount - initial_amount,
                "percentage_return": ((current_amount - initial_amount) / initial_amount) * 100 if initial_amount > 0 else 0,
                "annualized_return": 0,  # Not meaningful for very short periods
                "years": years,
                "days": days_diff
            }
        
        # Calculate absolute return
        absolute_return = current_amount - initial_amount
        
        # Calculate percentage return
        percentage_return = (absolute_return / initial_amount) * 100 if initial_amount > 0 else 0
        
        # Calculate annualized return (CAGR)
        if years > 0 and initial_amount > 0 and current_amount > 0:
            annualized_return = (((current_amount / initial_amount) ** (1 / years)) - 1) * 100
        else:
            annualized_return = 0
        
        return {
            "absolute_return": absolute_return,
            "percentage_return": percentage_return,
            "annualized_return": annualized_return,
            "years": years,
            "days": days_diff
        }
    
    # Function to get investment data for the current user
    def get_user_investments(username):
        investments = load_investments()
        return [inv for inv in investments if inv.get('username') == username]
    
    # Function to prepare investment data for analysis
    def prepare_investment_data(username):
        user_investments = get_user_investments(username)
        
        if not user_investments:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(user_investments)
        
        # Convert date strings to datetime objects
        if 'purchase_date' in df.columns:
            df['purchase_date'] = pd.to_datetime(df['purchase_date'])
        
        if 'last_updated' in df.columns:
            df['last_updated'] = pd.to_datetime(df['last_updated'])
        
        # Ensure numeric columns are numeric
        numeric_cols = ['initial_amount', 'current_amount', 'units', 'purchase_price', 'current_price']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate returns for each investment
        if 'initial_amount' in df.columns and 'current_amount' in df.columns and 'purchase_date' in df.columns:
            returns_data = []
            for _, inv in df.iterrows():
                returns = calculate_returns(
                    inv['initial_amount'], 
                    inv['current_amount'], 
                    inv['purchase_date'],
                    inv.get('last_updated', datetime.now().strftime("%Y-%m-%d"))
                )
                returns_data.append(returns)
            
            # Add returns data to DataFrame
            returns_df = pd.DataFrame(returns_data)
            df = pd.concat([df, returns_df], axis=1)
        
        return df
    
    # Function to generate investment insights
    def generate_investment_insights(investment_df):
        if investment_df is None or len(investment_df) == 0:
            return []
        
        insights = []
        
        # Total portfolio value
        total_current = investment_df['current_amount'].sum()
        total_initial = investment_df['initial_amount'].sum()
        total_return = total_current - total_initial
        total_return_pct = (total_return / total_initial) * 100 if total_initial > 0 else 0
        
        insights.append(f"Your total investment portfolio is worth **₹{total_current:,.2f}**, with a total return of **₹{total_return:,.2f}** ({total_return_pct:.2f}%).")
        
        # Best and worst performing investments
        if len(investment_df) > 1:
            best_inv = investment_df.loc[investment_df['percentage_return'].idxmax()]
            worst_inv = investment_df.loc[investment_df['percentage_return'].idxmin()]
            
            insights.append(f"Your best performing investment is **{best_inv['name']}** ({best_inv['type']}) with a return of **{best_inv['percentage_return']:.2f}%**.")
            insights.append(f"Your worst performing investment is **{worst_inv['name']}** ({worst_inv['type']}) with a return of **{worst_inv['percentage_return']:.2f}%**.")
        
        # Asset allocation insights
        type_allocation = investment_df.groupby('type')['current_amount'].sum()
        top_type = type_allocation.idxmax()
        top_type_pct = (type_allocation[top_type] / total_current) * 100
        
        insights.append(f"Your portfolio is heavily weighted towards **{top_type}** ({top_type_pct:.2f}% of total).")
        
        # Diversification check
        if len(type_allocation) < 3:
            insights.append("Consider diversifying your portfolio across more asset types to reduce risk.")
        
        # Long-term investments
        long_term = investment_df[investment_df['years'] >= 1]
        if len(long_term) > 0:
            avg_long_return = long_term['annualized_return'].mean()
            insights.append(f"Your long-term investments (1+ years) have an average annualized return of **{avg_long_return:.2f}%**.")
        
        # Recent investments
        recent = investment_df[investment_df['days'] <= 90]  # Last 3 months
        if len(recent) > 0:
            recent_total = recent['initial_amount'].sum()
            insights.append(f"You've invested **₹{recent_total:,.2f}** in the last 3 months.")
        
        return insights
    
    # Function to generate investment recommendations
    def generate_investment_recommendations(investment_df):
        if investment_df is None or len(investment_df) == 0:
            return []
        
        recommendations = []
        
        # Check asset allocation
        if 'type' in investment_df.columns:
            type_allocation = investment_df.groupby('type')['current_amount'].sum()
            total_value = investment_df['current_amount'].sum()
            
            # Check for over-concentration
            for asset_type, amount in type_allocation.items():
                allocation_pct = (amount / total_value) * 100
                if allocation_pct > 50:
                    recommendations.append(f"Consider reducing your exposure to **{asset_type}** (currently {allocation_pct:.2f}% of your portfolio) to improve diversification.")
            
            # Check for missing major asset classes
            major_asset_classes = {'Stocks', 'Mutual Funds', 'Fixed Deposits', 'Bonds', 'Gold'}
            missing_classes = major_asset_classes - set(type_allocation.index)
            if missing_classes:
                recommendations.append(f"Consider adding these asset classes to your portfolio for better diversification: **{', '.join(missing_classes)}**.")
        
        # Check for underperforming investments
        if 'percentage_return' in investment_df.columns and len(investment_df) > 0:
            underperforming = investment_df[(investment_df['percentage_return'] < 0) & (investment_df['days'] > 180)]
            if len(underperforming) > 0:
                for _, inv in underperforming.iterrows():
                    recommendations.append(f"Consider reviewing your investment in **{inv['name']}** which has a negative return of {inv['percentage_return']:.2f}% over {inv['days']} days.")
        
        # Check for regular investment pattern
        purchase_dates = pd.to_datetime(investment_df['purchase_date'])
        date_diffs = purchase_dates.sort_values().diff().dt.days
        if len(date_diffs) > 3:
            if date_diffs.std() > 45:  # High variability in investment timing
                recommendations.append("Consider setting up a systematic investment plan (SIP) for more disciplined and regular investing.")
        
        # General recommendations
        recommendations.append("Review your investment portfolio at least quarterly to ensure it aligns with your financial goals.")
        recommendations.append("Consider increasing your investments as your income grows to build long-term wealth.")
        
        return recommendations
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Overview", "Add Investment", "Update Investments", "Analysis & Insights"])
    
    with tab1:
        st.markdown("### Your Investment Portfolio")
        
        # Get user investments
        user_investments = get_user_investments(st.session_state.current_user)
        
        if not user_investments:
            st.info("You don't have any investments yet. Add your first investment in the 'Add Investment' tab.")
        else:
            # Prepare investment data
            investment_df = prepare_investment_data(st.session_state.current_user)
            
            # Calculate portfolio summary
            total_invested = investment_df['initial_amount'].sum()
            current_value = investment_df['current_amount'].sum()
            total_return = current_value - total_invested
            return_percentage = (total_return / total_invested) * 100 if total_invested > 0 else 0
            
            # Display portfolio summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Invested", f"₹{total_invested:,.2f}")
            with col2:
                st.metric("Current Value", f"₹{current_value:,.2f}")
            with col3:
                st.metric("Total Return", f"₹{total_return:,.2f}", f"{return_percentage:.2f}%")
            
            # Display investments table
            st.markdown("#### Your Investments")
            
            # Prepare display DataFrame
            display_df = investment_df[['name', 'type', 'initial_amount', 'current_amount', 'percentage_return', 'purchase_date']].copy()
            display_df['purchase_date'] = display_df['purchase_date'].dt.strftime('%Y-%m-%d')
            display_df['initial_amount'] = display_df['initial_amount'].apply(lambda x: f"₹{x:,.2f}")
            display_df['current_amount'] = display_df['current_amount'].apply(lambda x: f"₹{x:,.2f}")
            display_df['percentage_return'] = display_df['percentage_return'].apply(lambda x: f"{x:.2f}%")
            display_df.columns = ['Investment Name', 'Type', 'Amount Invested', 'Current Value', 'Return', 'Purchase Date']
            
            st.dataframe(display_df, use_container_width=True)
            
            # Display asset allocation
            st.markdown("#### Asset Allocation")
            
            # Create pie chart of asset allocation
            type_allocation = investment_df.groupby('type')['current_amount'].sum().reset_index()
            type_allocation.columns = ['Asset Type', 'Value']
            
            fig = px.pie(type_allocation, values='Value', names='Asset Type',
                       title='Asset Allocation by Type',
                       color_discrete_sequence=px.colors.qualitative.Set3)
            
            # Update traces
            fig.update_traces(textinfo='percent+label', textposition='inside')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display returns by investment type
            st.markdown("#### Returns by Investment Type")
            
            # Calculate average returns by type
            type_returns = investment_df.groupby('type')['percentage_return'].mean().reset_index()
            type_returns.columns = ['Asset Type', 'Average Return (%)']  # Fixed extra bracket
            
            # Create bar chart
            fig = px.bar(type_returns, x='Asset Type', y='Average Return (%)',
                       title='Average Returns by Investment Type',
                       color='Asset Type',
                       color_discrete_sequence=px.colors.qualitative.Set3)
            
            # Update layout
            fig.update_layout(
                xaxis_title="Asset Type",
                yaxis_title="Average Return (%)",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Add New Investment")
        st.write("Add details of your investments to track their performance over time.")
        
        # Investment form
        with st.form("add_investment_form"):
            # Investment name
            investment_name = st.text_input("Investment Name", placeholder="e.g., HDFC Bank Shares, PPF Account")
            
            # Investment type
            investment_types = [
                "Stocks", "Mutual Funds", "Fixed Deposits", "Recurring Deposits", 
                "PPF", "EPF", "NPS", "Bonds", "Gold", "Real Estate", "Cryptocurrency", "Other"
            ]
            investment_type = st.selectbox("Investment Type", investment_types)
            
            # Investment details
            col1, col2 = st.columns(2)
            with col1:
                # Amount invested
                amount = st.number_input("Amount Invested (₹)", min_value=0.0, step=1000.0)
                
                # Purchase date
                purchase_date = st.date_input("Purchase Date", value=datetime.now().date())
            
            with col2:
                # Current value
                current_value = st.number_input("Current Value (₹)", min_value=0.0, step=1000.0, value=amount)
                
                # Last updated date
                last_updated = st.date_input("Last Updated", value=datetime.now().date())
            
            # Additional details based on investment type
            if investment_type in ["Stocks", "Mutual Funds", "Cryptocurrency"]:
                col1, col2 = st.columns(2)
                with col1:
                    units = st.number_input("Number of Units/Shares", min_value=0.0, step=0.01)
                with col2:
                    purchase_price = st.number_input("Purchase Price per Unit (₹)", min_value=0.0, step=0.01)
                    current_price = st.number_input("Current Price per Unit (₹)", min_value=0.0, step=0.01, value=purchase_price)
            else:
                units = 1.0
                purchase_price = amount
                current_price = current_value
            
            # Notes
            notes = st.text_area("Notes (Optional)", placeholder="Any additional details about this investment...")
            
            # Submit button
            submitted = st.form_submit_button("Add Investment")
            
            if submitted:
                if not investment_name:
                    st.error("Please enter an investment name.")
                elif amount <= 0:
                    st.error("Please enter a valid investment amount.")
                else:
                    # Load existing investments
                    investments = load_investments()
                    
                    # Create new investment entry
                    new_investment = {
                        "username": st.session_state.current_user,
                        "name": investment_name,
                        "type": investment_type,
                        "initial_amount": amount,
                        "current_amount": current_value,
                        "units": units,
                        "purchase_price": purchase_price,
                        "current_price": current_price,
                        "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                        "last_updated": last_updated.strftime("%Y-%m-%d"),
                        "notes": notes
                    }
                    
                    # Add to investments list
                    investments.append(new_investment)
                    
                    # Save updated investments
                    save_investments(investments)
                    
                    # Also record as a transaction
                    transactions = load_transactions()
                    
                    # Create transaction entry
                    new_transaction = {
                        "sender": st.session_state.current_user,
                        "receiver": f"Investment: {investment_name}",
                        "amount": amount,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "investment",
                        "category": "Investment",
                        "note": f"Investment in {investment_type}: {investment_name}"
                    }
                    
                    # Add to transactions list
                    transactions.append(new_transaction)
                    
                    # Save updated transactions
                    save_transactions(transactions)
                    
                    st.success(f"Investment '{investment_name}' added successfully!")
    
    with tab3:
        st.markdown("### Update Investments")
        st.write("Update the current value of your investments to track their performance accurately.")
        
        # Get user investments
        user_investments = get_user_investments(st.session_state.current_user)
        
        if not user_investments:
            st.info("You don't have any investments to update. Add your first investment in the 'Add Investment' tab.")
        else:
            # Create a selectbox to choose which investment to update
            investment_names = [inv['name'] for inv in user_investments]
            selected_investment = st.selectbox("Select Investment to Update", investment_names)
            
            # Find the selected investment
            selected_inv = None
            for inv in user_investments:
                if inv['name'] == selected_investment:
                    selected_inv = inv
                    break
            
            if selected_inv:
                # Display current details
                st.markdown(f"#### Current Details for: {selected_inv['name']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Type:** {selected_inv['type']}")
                    st.markdown(f"**Initial Amount:** ₹{selected_inv['initial_amount']:,.2f}")
                    st.markdown(f"**Purchase Date:** {selected_inv['purchase_date']}")
                with col2:
                    st.markdown(f"**Current Value:** ₹{selected_inv['current_amount']:,.2f}")
                    st.markdown(f"**Last Updated:** {selected_inv.get('last_updated', selected_inv['purchase_date'])}")
                
                # Calculate returns
                returns = calculate_returns(
                    selected_inv['initial_amount'],
                    selected_inv['current_amount'],
                    selected_inv['purchase_date'],
                    selected_inv.get('last_updated', datetime.now().strftime("%Y-%m-%d"))
                )
                
                st.markdown(f"**Current Return:** ₹{returns['absolute_return']:,.2f} ({returns['percentage_return']:.2f}%)")
                
                # Update form
                with st.form("update_investment_form"):
                    st.markdown("#### Update Investment Value")
                    
                    # New current value
                    new_value = st.number_input("New Current Value (₹)", 
                                              min_value=0.0, 
                                              value=float(selected_inv['current_amount']),
                                              step=1000.0)
                    
                    # If it has units, allow updating current price
                    if selected_inv['type'] in ["Stocks", "Mutual Funds", "Cryptocurrency"] and 'units' in selected_inv and selected_inv['units'] > 0:
                        new_price = st.number_input("New Price per Unit (₹)", 
                                                  min_value=0.0, 
                                                  value=float(selected_inv['current_price']),
                                                  step=0.01)
                        
                        # Auto-calculate value based on units and price
                        calculated_value = new_price * selected_inv['units']
                        if abs(calculated_value - new_value) > 1:  # If there's a discrepancy
                            st.warning(f"The calculated value (₹{calculated_value:,.2f}) based on {selected_inv['units']} units at ₹{new_price:.2f} per unit doesn't match the entered value. The calculated value will be used.")
                            new_value = calculated_value
                    else:
                        new_price = new_value
                    
                    # Notes about the update
                    update_notes = st.text_area("Update Notes (Optional)", 
                                              placeholder="Any notes about this update (e.g., dividend received, additional investment)...")
                    
                    # Submit button
                    submitted = st.form_submit_button("Update Investment")
                    
                    if submitted:
                        # Load all investments
                        all_investments = load_investments()
                        
                        # Find and update the selected investment
                        for i, inv in enumerate(all_investments):
                            if inv.get('username') == st.session_state.current_user and inv.get('name') == selected_investment:
                                # Update values
                                all_investments[i]['current_amount'] = new_value
                                all_investments[i]['current_price'] = new_price
                                all_investments[i]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                                
                                # Add update notes if provided
                                if update_notes:
                                    if 'update_history' not in all_investments[i]:
                                        all_investments[i]['update_history'] = []
                                    
                                    all_investments[i]['update_history'].append({
                                        "date": datetime.now().strftime("%Y-%m-%d"),
                                        "old_value": selected_inv['current_amount'],
                                        "new_value": new_value,
                                        "notes": update_notes
                                    })
                                
                                break
                        
                        # Save updated investments
                        save_investments(all_investments)
                        
                        st.success(f"Investment '{selected_investment}' updated successfully!")
                        st.rerun()  # Refresh the page to show updated values
    
    with tab4:
        st.markdown("### Investment Analysis & Insights")
        
        # Get user investments
        user_investments = get_user_investments(st.session_state.current_user)
        
        if not user_investments:
            st.info("You don't have any investments yet. Add your first investment in the 'Add Investment' tab.")
        else:
            # Prepare investment data
            investment_df = prepare_investment_data(st.session_state.current_user)
            
            # Display performance metrics
            st.markdown("#### Performance Metrics")
            
            # Calculate overall metrics
            total_invested = investment_df['initial_amount'].sum()
            current_value = investment_df['current_amount'].sum()
            total_return = current_value - total_invested
            return_percentage = (total_return / total_invested) * 100 if total_invested > 0 else 0
            
            # Calculate weighted average annualized return
            weighted_return = np.average(
                investment_df['annualized_return'], 
                weights=investment_df['initial_amount']
            ) if len(investment_df) > 0 else 0
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Return", f"₹{total_return:,.2f}", f"{return_percentage:.2f}%")
            with col2:
                st.metric("Weighted Avg. Annual Return", f"{weighted_return:.2f}%")
            with col3:
                # Calculate portfolio XIRR (simplified)
                oldest_investment = investment_df['purchase_date'].min()
                days_invested = (datetime.now().date() - oldest_investment.date()).days
                years_invested = days_invested / 365.25
                if years_invested > 0:
                    portfolio_cagr = (((current_value / total_invested) ** (1 / years_invested)) - 1) * 100
                    st.metric("Portfolio CAGR", f"{portfolio_cagr:.2f}%")
                else:
                    st.metric("Portfolio CAGR", "N/A")
            
            # Display performance by investment
            st.markdown("#### Performance by Investment")
            
            # Create bar chart of returns by investment
            performance_df = investment_df[['name', 'type', 'percentage_return']].copy()
            performance_df = performance_df.sort_values('percentage_return', ascending=False)
            
            fig = px.bar(performance_df, x='name', y='percentage_return',
                       color='type',
                       labels={'name': 'Investment', 'percentage_return': 'Return (%)', 'type': 'Type'},
                       title='Investment Returns',
                       color_discrete_sequence=px.colors.qualitative.Set3)
            
            # Update layout
            fig.update_layout(
                xaxis_title="Investment",
                yaxis_title="Return (%)",
                xaxis={'categoryorder':'total descending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display investment growth over time
            st.markdown("#### Investment Growth Over Time")
            
            # Create a timeline of investments
            timeline_data = []
            for _, inv in investment_df.iterrows():
                # Initial investment point
                timeline_data.append({
                    'date': inv['purchase_date'],
                    'amount': inv['initial_amount'],
                    'type': 'Initial Investment',
                    'name': inv['name']
                })
                
                # Current value point
                timeline_data.append({
                    'date': pd.to_datetime(inv.get('last_updated', datetime.now().strftime("%Y-%m-%d"))),
                    'amount': inv['current_amount'],
                    'type': 'Current Value',
                    'name': inv['name']
                })
                
                # Add update history points if available
                if 'update_history' in inv and isinstance(inv['update_history'], list):
                    for update in inv['update_history']:
                        timeline_data.append({
                            'date': pd.to_datetime(update['date']),
                            'amount': update['new_value'],
                            'type': 'Value Update',
                            'name': inv['name']
                        })
            
            # Convert to DataFrame and sort by date
            timeline_df = pd.DataFrame(timeline_data)
            timeline_df = timeline_df.sort_values('date')
            
            # Create line chart of investment growth
            fig = px.line(timeline_df, x='date', y='amount', color='name',
                         labels={'date': 'Date', 'amount': 'Amount (₹)', 'name': 'Investment'},
                         title='Investment Growth Over Time',
                         markers=True)
            
            # Update layout
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Amount (₹)",
                legend_title="Investment"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display cumulative investment growth
            st.markdown("#### Cumulative Portfolio Growth")
            
            # Create a cumulative timeline
            # Group by date and calculate total invested and total value
            date_range = pd.date_range(start=timeline_df['date'].min(), end=datetime.now(), freq='M')
            cumulative_data = []
            
            for date in date_range:
                # Filter investments that exist by this date
                existing_investments = investment_df[investment_df['purchase_date'] <= date]
                
                if len(existing_investments) > 0:
                    # Calculate total invested by this date
                    total_invested = existing_investments['initial_amount'].sum()
                    
                    # Estimate current value at this date (simplified)
                    # This is a simplification - in reality, you'd need historical price data
                    total_value = 0
                    for _, inv in existing_investments.iterrows():
                        days_held = (date.date() - inv['purchase_date'].date()).days
                        total_days = (datetime.now().date() - inv['purchase_date'].date()).days
                        
                        if total_days > 0:
                            # Linear interpolation between initial and current value
                            value_at_date = inv['initial_amount'] + (inv['current_amount'] - inv['initial_amount']) * (days_held / total_days)
                            total_value += value_at_date
                        else:
                            total_value += inv['initial_amount']
                    
                    cumulative_data.append({
                        'date': date,
                        'total_invested': total_invested,
                        'total_value': total_value
                    })
            
            # Convert to DataFrame
            cumulative_df = pd.DataFrame(cumulative_data)
            
            if len(cumulative_df) > 0:
                # Create line chart of cumulative growth
                fig = go.Figure()
                
                # Add total invested line
                fig.add_trace(go.Scatter(
                    x=cumulative_df['date'],
                    y=cumulative_df['total_invested'],
                    mode='lines',
                    name='Total Invested',
                    line=dict(color='#34A853', width=2)
                ))
                
                # Add total value line
                fig.add_trace(go.Scatter(
                    x=cumulative_df['date'],
                    y=cumulative_df['total_value'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='#4285F4', width=2)
                ))
                
                # Add area between curves to highlight returns
                fig.add_trace(go.Scatter(
                    x=cumulative_df['date'],
                    y=cumulative_df['total_value'],
                    mode='none',
                    fill='tonexty',
                    fillcolor='rgba(66, 133, 244, 0.2)',
                    name='Returns'
                ))
                
                # Update layout
                fig.update_layout(
                    title='Cumulative Portfolio Growth',
                    xaxis_title='Date',
                    yaxis_title='Amount (₹)',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Display insights and recommendations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Investment Insights")
                insights = generate_investment_insights(investment_df)
                
                if not insights:
                    st.info("Not enough data to generate insights yet. Continue adding and updating your investments.")
                else:
                    for i, insight in enumerate(insights, 1):
                        st.markdown(f"{i}. {insight}")
            
            with col2:
                st.markdown("#### Recommendations")
                recommendations = generate_investment_recommendations(investment_df)
                
                if not recommendations:
                    st.info("Not enough data to generate recommendations yet. Continue adding and updating your investments.")
                else:
                    for i, recommendation in enumerate(recommendations, 1):
                        st.markdown(f"{i}. {recommendation}")
    
    # Initialize session state for investments.json if it doesn't exist
    if not os.path.exists('investments.json'):
        with open('investments.json', 'w') as f:
            json.dump([], f)
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()