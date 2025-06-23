def emotion_insights_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.express as px
    import plotly.graph_objects as go
    from sklearn.cluster import KMeans
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Emotion Insights</h1>", unsafe_allow_html=True)
    
    # Load transactions
    def load_transactions():
        data_dir = "data"
        transaction_file = os.path.join(data_dir, "transactions.json")
        if os.path.exists(transaction_file):
            with open(transaction_file, 'r') as f:
                return json.load(f)
        return []
    
    # Load emotions data
    def load_emotions():
        data_dir = "data"
        emotions_file = os.path.join(data_dir, "emotions.json")
        if os.path.exists(emotions_file):
            with open(emotions_file, 'r') as f:
                return json.load(f)
        return []
    
    # Save emotions data
    def save_emotions(emotions_data):
        data_dir = "data"
        emotions_file = os.path.join(data_dir, "emotions.json")
        with open(emotions_file, 'w') as f:
            json.dump(emotions_data, f, indent=4)
    
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
        df['date_only'] = df['date'].dt.date
        
        # Ensure category is present
        if 'category' not in df.columns:
            df['category'] = 'Other'
        
        # Fill missing categories
        df['category'] = df['category'].fillna('Other')
        
        return df
    
    # Function to prepare emotions data
    def prepare_emotions_data(username):
        emotions_data = load_emotions()
        
        # Filter emotions for the current user
        user_emotions = []
        for emotion in emotions_data:
            if emotion['username'] == username:
                user_emotions.append(emotion)
        
        if not user_emotions:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(user_emotions)
        
        # Convert date strings to datetime objects
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract date components
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['dayofweek'] = df['date'].dt.dayofweek  # Monday=0, Sunday=6
        df['date_only'] = df['date'].dt.date
        
        return df
    
    # Function to merge transaction and emotion data
    def merge_transaction_emotion_data(tx_df, emotion_df):
        if tx_df is None or emotion_df is None:
            return None
        
        # Convert date columns to string for merging
        tx_df['date_str'] = tx_df['date_only'].astype(str)
        emotion_df['date_str'] = emotion_df['date_only'].astype(str)
        
        # Merge on date
        merged_df = pd.merge(tx_df, emotion_df[['date_str', 'emotion', 'intensity']], on='date_str', how='left')
        
        # Fill missing emotions with 'Unknown'
        merged_df['emotion'] = merged_df['emotion'].fillna('Unknown')
        merged_df['intensity'] = merged_df['intensity'].fillna(0)
        
        return merged_df
    
    # Function to analyze spending by emotion
    def analyze_spending_by_emotion(merged_df):
        if merged_df is None or 'emotion' not in merged_df.columns:
            return None
        
        # Group by emotion and calculate statistics
        emotion_stats = merged_df.groupby('emotion').agg({
            'amount': ['sum', 'mean', 'count'],
            'intensity': 'mean'
        }).reset_index()
        
        # Flatten multi-level columns
        emotion_stats.columns = ['emotion', 'total_amount', 'avg_amount', 'transaction_count', 'avg_intensity']
        
        return emotion_stats
    
    # Function to analyze category spending by emotion
    def analyze_category_by_emotion(merged_df):
        if merged_df is None or 'emotion' not in merged_df.columns or 'category' not in merged_df.columns:
            return None
        
        # Group by emotion and category
        category_emotion = merged_df.groupby(['emotion', 'category'])['amount'].sum().reset_index()
        
        return category_emotion
    
    # Function to detect spending patterns using clustering
    def detect_spending_patterns(merged_df):
        if merged_df is None or len(merged_df) < 10:  # Need at least 10 transactions for meaningful clustering
            return None
        
        # Select features for clustering
        features = ['amount', 'intensity', 'dayofweek']
        
        # Ensure all features are available
        available_features = [f for f in features if f in merged_df.columns]
        if len(available_features) < 2:  # Need at least 2 features for clustering
            return None
        
        # Extract features
        X = merged_df[available_features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Scale features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Determine optimal number of clusters (2-5)
        from sklearn.metrics import silhouette_score
        silhouette_scores = []
        for n_clusters in range(2, 6):
            # Skip if not enough samples
            if len(X) <= n_clusters:
                continue
                
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            # Skip if only one cluster is assigned
            if len(np.unique(cluster_labels)) < 2:
                continue
                
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append((n_clusters, silhouette_avg))
        
        # If no valid clustering found
        if not silhouette_scores:
            return None
        
        # Select best number of clusters
        best_n_clusters = max(silhouette_scores, key=lambda x: x[1])[0]
        
        # Perform final clustering
        kmeans = KMeans(n_clusters=best_n_clusters, random_state=42, n_init=10)
        merged_df['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Analyze clusters
        cluster_stats = merged_df.groupby('cluster').agg({
            'amount': ['mean', 'sum', 'count'],
            'emotion': lambda x: x.value_counts().index[0] if len(x.value_counts()) > 0 else 'Unknown',
            'intensity': 'mean',
            'category': lambda x: x.value_counts().index[0] if len(x.value_counts()) > 0 else 'Unknown'
        }).reset_index()
        
        # Flatten multi-level columns
        cluster_stats.columns = ['cluster', 'avg_amount', 'total_amount', 'transaction_count', 'dominant_emotion', 'avg_intensity', 'dominant_category']
        
        return {
            'clustered_data': merged_df,
            'cluster_stats': cluster_stats,
            'features_used': available_features
        }
    
    # Function to generate insights based on emotion-spending analysis
    def generate_emotion_insights(emotion_stats, category_emotion, patterns):
        insights = []
        
        # Insights from emotion stats
        if emotion_stats is not None and len(emotion_stats) > 0:
            # Find emotion with highest average spending
            highest_avg = emotion_stats.loc[emotion_stats['avg_amount'].idxmax()]
            if highest_avg['emotion'] != 'Unknown':
                insights.append(f"When you're feeling **{highest_avg['emotion']}**, you spend an average of **₹{highest_avg['avg_amount']:.2f}** per transaction.")
            
            # Find emotion with highest total spending
            highest_total = emotion_stats.loc[emotion_stats['total_amount'].idxmax()]
            if highest_total['emotion'] != 'Unknown' and len(emotion_stats) > 1:
                insights.append(f"You've spent the most (**₹{highest_total['total_amount']:.2f}**) while feeling **{highest_total['emotion']}**.")
            
            # Find emotion with most transactions
            most_txns = emotion_stats.loc[emotion_stats['transaction_count'].idxmax()]
            if most_txns['emotion'] != 'Unknown' and len(emotion_stats) > 1:
                insights.append(f"You make the most transactions ({most_txns['transaction_count']}) when you're feeling **{most_txns['emotion']}**.")
        
        # Insights from category by emotion
        if category_emotion is not None and len(category_emotion) > 0:
            # For each emotion, find the top spending category
            for emotion in category_emotion['emotion'].unique():
                if emotion == 'Unknown':
                    continue
                    
                emotion_df = category_emotion[category_emotion['emotion'] == emotion]
                if len(emotion_df) > 0:
                    top_category = emotion_df.loc[emotion_df['amount'].idxmax()]
                    insights.append(f"When you're feeling **{emotion}**, you spend the most on **{top_category['category']}** (₹{top_category['amount']:.2f}).")
        
        # Insights from spending patterns
        if patterns is not None and 'cluster_stats' in patterns and len(patterns['cluster_stats']) > 0:
            cluster_stats = patterns['cluster_stats']
            
            # Find cluster with highest average spending
            highest_cluster = cluster_stats.loc[cluster_stats['avg_amount'].idxmax()]
            if highest_cluster['dominant_emotion'] != 'Unknown':
                insights.append(f"Your highest spending pattern is associated with feeling **{highest_cluster['dominant_emotion']}** and spending on **{highest_cluster['dominant_category']}**.")
            
            # Find cluster with lowest average spending
            lowest_cluster = cluster_stats.loc[cluster_stats['avg_amount'].idxmin()]
            if lowest_cluster['dominant_emotion'] != 'Unknown':
                insights.append(f"Your lowest spending pattern is associated with feeling **{lowest_cluster['dominant_emotion']}** and spending on **{lowest_cluster['dominant_category']}**.")
        
        return insights
    
    # Function to generate recommendations based on emotion-spending analysis
    def generate_recommendations(emotion_stats, category_emotion, patterns):
        recommendations = []
        
        # Recommendations from emotion stats
        if emotion_stats is not None and len(emotion_stats) > 0:
            # Find emotion with highest average spending
            highest_avg = emotion_stats.loc[emotion_stats['avg_amount'].idxmax()]
            if highest_avg['emotion'] != 'Unknown':
                recommendations.append(f"Consider setting a spending limit when you're feeling **{highest_avg['emotion']}** to avoid impulse purchases.")
            
            # Find emotion with highest total spending
            highest_total = emotion_stats.loc[emotion_stats['total_amount'].idxmax()]
            if highest_total['emotion'] != 'Unknown' and len(emotion_stats) > 1:
                recommendations.append(f"Try to be more mindful of your spending when you're feeling **{highest_total['emotion']}**.")
        
        # Recommendations from category by emotion
        if category_emotion is not None and len(category_emotion) > 0:
            # Find emotion-category combinations with high spending
            top_combos = category_emotion.sort_values('amount', ascending=False).head(3)
            for _, combo in top_combos.iterrows():
                if combo['emotion'] != 'Unknown':
                    recommendations.append(f"Be aware of your tendency to spend on **{combo['category']}** when you're feeling **{combo['emotion']}**.")
        
        # General recommendations
        recommendations.append("Track your emotions before making large purchases to identify potential emotional spending triggers.")
        recommendations.append("Consider waiting 24 hours before making non-essential purchases when experiencing strong emotions.")
        recommendations.append("Create a budget specifically for 'emotional spending' to allow yourself some flexibility while maintaining control.")
        
        return recommendations
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["Track Emotions", "Spending by Emotion", "Patterns & Insights", "Recommendations"])
    
    with tab1:
        st.markdown("### Track Your Emotions")
        st.write("Record your emotional state to help analyze how your feelings affect your spending habits.")
        
        # Emotion tracking form
        with st.form("emotion_form"):
            # Date selection (default to today)
            emotion_date = st.date_input("Date", value=datetime.now().date())
            
            # Emotion selection
            emotion_options = [
                "Happy", "Excited", "Content", "Relaxed", "Neutral", 
                "Stressed", "Anxious", "Sad", "Frustrated", "Bored"
            ]
            selected_emotion = st.selectbox("How are you feeling today?", emotion_options)
            
            # Intensity slider
            intensity = st.slider("Intensity", min_value=1, max_value=10, value=5, 
                               help="1 = Very mild, 10 = Very intense")
            
            # Notes
            notes = st.text_area("Notes (optional)", 
                              placeholder="Any additional thoughts about how you're feeling...")
            
            # Submit button
            submitted = st.form_submit_button("Save Emotion")
            
            if submitted:
                # Load existing emotions data
                emotions_data = load_emotions()
                
                # Create new emotion entry
                new_emotion = {
                    "username": st.session_state.current_user,
                    "date": emotion_date.strftime("%Y-%m-%d"),
                    "emotion": selected_emotion,
                    "intensity": intensity,
                    "notes": notes
                }
                
                # Check if an entry already exists for this date and user
                existing_entry = False
                for i, emotion in enumerate(emotions_data):
                    if emotion.get("username") == st.session_state.current_user and emotion.get("date") == emotion_date.strftime("%Y-%m-%d"):
                        # Update existing entry
                        emotions_data[i] = new_emotion
                        existing_entry = True
                        break
                
                # If no existing entry, add new one
                if not existing_entry:
                    emotions_data.append(new_emotion)
                
                # Save updated emotions data
                save_emotions(emotions_data)
                
                st.success(f"Emotion tracked for {emotion_date.strftime('%Y-%m-%d')}!")
        
        # Display emotion history
        st.markdown("### Your Emotion History")
        
        # Prepare emotions data
        emotions_df = prepare_emotions_data(st.session_state.current_user)
        
        if emotions_df is None or len(emotions_df) == 0:
            st.info("You haven't tracked any emotions yet. Start tracking above to see your history.")
        else:
            # Sort by date (most recent first)
            emotions_df = emotions_df.sort_values('date', ascending=False)
            
            # Display as table
            display_df = emotions_df[['date', 'emotion', 'intensity', 'notes']].copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df.columns = ['Date', 'Emotion', 'Intensity', 'Notes']
            
            st.dataframe(display_df, use_container_width=True)
            
            # Visualize emotion history
            st.markdown("### Emotion Trends")
            
            # Create line chart of emotion intensity over time
            fig = px.line(emotions_df.sort_values('date'), x='date', y='intensity', color='emotion',
                         labels={'date': 'Date', 'intensity': 'Intensity', 'emotion': 'Emotion'},
                         title='Emotion Intensity Over Time',
                         markers=True)
            
            # Update layout
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Intensity (1-10)",
                legend_title="Emotion"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create pie chart of emotion distribution
            emotion_counts = emotions_df['emotion'].value_counts().reset_index()
            emotion_counts.columns = ['emotion', 'count']
            
            fig = px.pie(emotion_counts, values='count', names='emotion',
                       title='Emotion Distribution',
                       color_discrete_sequence=px.colors.qualitative.Set3)
            
            # Update traces
            fig.update_traces(textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Spending by Emotion")
        st.write("Analyze how your emotional state affects your spending patterns.")
        
        # Prepare transaction data
        tx_df = prepare_transaction_data(st.session_state.current_user)
        
        # Prepare emotions data
        emotions_df = prepare_emotions_data(st.session_state.current_user)
        
        if tx_df is None or len(tx_df) == 0:
            st.warning("You don't have any transaction data yet. Make some transactions to see spending by emotion.")
        elif emotions_df is None or len(emotions_df) == 0:
            st.warning("You haven't tracked any emotions yet. Track your emotions in the 'Track Emotions' tab to see spending by emotion.")
        else:
            # Merge transaction and emotion data
            merged_df = merge_transaction_emotion_data(tx_df, emotions_df)
            
            if merged_df is None:
                st.error("Failed to merge transaction and emotion data. Please try again later.")
            else:
                # Analyze spending by emotion
                emotion_stats = analyze_spending_by_emotion(merged_df)
                
                if emotion_stats is None or len(emotion_stats) == 0:
                    st.warning("Not enough data to analyze spending by emotion. Please continue tracking emotions and making transactions.")
                else:
                    # Display spending by emotion
                    st.markdown("#### Total Spending by Emotion")
                    
                    # Sort by total amount descending
                    emotion_stats = emotion_stats.sort_values('total_amount', ascending=False)
                    
                    # Create bar chart
                    fig = px.bar(emotion_stats, x='emotion', y='total_amount',
                               labels={'emotion': 'Emotion', 'total_amount': 'Total Amount (₹)'},
                               title='Total Spending by Emotion',
                               color='emotion',
                               color_discrete_sequence=px.colors.qualitative.Set3)
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Emotion",
                        yaxis_title="Total Amount (₹)",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display average spending by emotion
                    st.markdown("#### Average Transaction Amount by Emotion")
                    
                    # Sort by average amount descending
                    emotion_stats_avg = emotion_stats.sort_values('avg_amount', ascending=False)
                    
                    # Create bar chart
                    fig = px.bar(emotion_stats_avg, x='emotion', y='avg_amount',
                               labels={'emotion': 'Emotion', 'avg_amount': 'Average Amount (₹)'},
                               title='Average Transaction Amount by Emotion',
                               color='emotion',
                               color_discrete_sequence=px.colors.qualitative.Set3)
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Emotion",
                        yaxis_title="Average Amount (₹)",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display transaction count by emotion
                    st.markdown("#### Number of Transactions by Emotion")
                    
                    # Sort by transaction count descending
                    emotion_stats_count = emotion_stats.sort_values('transaction_count', ascending=False)
                    
                    # Create bar chart
                    fig = px.bar(emotion_stats_count, x='emotion', y='transaction_count',
                               labels={'emotion': 'Emotion', 'transaction_count': 'Number of Transactions'},
                               title='Number of Transactions by Emotion',
                               color='emotion',
                               color_discrete_sequence=px.colors.qualitative.Set3)
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Emotion",
                        yaxis_title="Number of Transactions",
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display spending by category and emotion
                    st.markdown("#### Spending by Category and Emotion")
                    
                    # Analyze category spending by emotion
                    category_emotion = analyze_category_by_emotion(merged_df)
                    
                    if category_emotion is not None and len(category_emotion) > 0:
                        # Create grouped bar chart
                        fig = px.bar(category_emotion, x='category', y='amount', color='emotion',
                                   labels={'category': 'Category', 'amount': 'Amount (₹)', 'emotion': 'Emotion'},
                                   title='Spending by Category and Emotion',
                                   barmode='group',
                                   color_discrete_sequence=px.colors.qualitative.Set3)
                        
                        # Update layout
                        fig.update_layout(
                            xaxis_title="Category",
                            yaxis_title="Amount (₹)",
                            legend_title="Emotion"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Create heatmap of category by emotion
                        pivot_data = category_emotion.pivot_table(index='emotion', columns='category', values='amount', aggfunc='sum')
                        
                        # Fill NaN values with 0
                        pivot_data = pivot_data.fillna(0)
                        
                        # Create heatmap
                        fig = px.imshow(pivot_data,
                                      labels=dict(x="Category", y="Emotion", color="Amount (₹)"),
                                      x=pivot_data.columns,
                                      y=pivot_data.index,
                                      color_continuous_scale=['#E8F0FE', '#4285F4', '#EA4335'],
                                      title='Heatmap of Spending by Category and Emotion')
                        
                        # Update layout
                        fig.update_layout(
                            xaxis_title="Category",
                            yaxis_title="Emotion"
                        )
                        
                        # Add text annotations
                        fig.update_traces(text=pivot_data.values.round(2), texttemplate="₹%{text}")
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Not enough data to analyze spending by category and emotion.")
                    
                    # Display correlation between emotion intensity and spending
                    st.markdown("#### Emotion Intensity vs. Spending")
                    
                    # Create scatter plot
                    fig = px.scatter(merged_df, x='intensity', y='amount', color='emotion',
                                   labels={'intensity': 'Emotion Intensity', 'amount': 'Transaction Amount (₹)', 'emotion': 'Emotion'},
                                   title='Emotion Intensity vs. Transaction Amount',
                                   trendline='ols',  # Add trend line
                                   color_discrete_sequence=px.colors.qualitative.Set3)
                    
                    # Update layout
                    fig.update_layout(
                        xaxis_title="Emotion Intensity (1-10)",
                        yaxis_title="Transaction Amount (₹)",
                        legend_title="Emotion"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate correlation
                    correlation = merged_df['intensity'].corr(merged_df['amount'])
                    
                    if correlation > 0.3:
                        st.info(f"There appears to be a **positive correlation** ({correlation:.2f}) between emotion intensity and spending amount. This suggests you tend to spend more when your emotions are stronger.")
                    elif correlation < -0.3:
                        st.info(f"There appears to be a **negative correlation** ({correlation:.2f}) between emotion intensity and spending amount. This suggests you tend to spend less when your emotions are stronger.")
                    else:
                        st.info(f"There doesn't appear to be a strong correlation ({correlation:.2f}) between emotion intensity and spending amount.")
    
    with tab3:
        st.markdown("### Spending Patterns & Insights")
        st.write("Discover patterns in your emotional spending and get personalized insights.")
        
        # Prepare transaction data
        tx_df = prepare_transaction_data(st.session_state.current_user)
        
        # Prepare emotions data
        emotions_df = prepare_emotions_data(st.session_state.current_user)
        
        if tx_df is None or len(tx_df) < 10:
            st.warning("You need at least 10 transactions for pattern analysis. Please continue using the app to generate more transaction data.")
        elif emotions_df is None or len(emotions_df) == 0:
            st.warning("You haven't tracked any emotions yet. Track your emotions in the 'Track Emotions' tab to see spending patterns.")
        else:
            # Merge transaction and emotion data
            merged_df = merge_transaction_emotion_data(tx_df, emotions_df)
            
            if merged_df is None:
                st.error("Failed to merge transaction and emotion data. Please try again later.")
            else:
                # Analyze spending by emotion
                emotion_stats = analyze_spending_by_emotion(merged_df)
                
                # Analyze category spending by emotion
                category_emotion = analyze_category_by_emotion(merged_df)
                
                # Detect spending patterns
                patterns = detect_spending_patterns(merged_df)
                
                if patterns is None:
                    st.warning("Not enough data to detect spending patterns. Please continue tracking emotions and making transactions.")
                else:
                    # Display spending patterns
                    st.markdown("#### Detected Spending Patterns")
                    
                    # Display cluster statistics
                    cluster_stats = patterns['cluster_stats']
                    
                    # Format for display
                    display_clusters = cluster_stats.copy()
                    display_clusters['avg_amount'] = display_clusters['avg_amount'].apply(lambda x: f"₹{x:.2f}")
                    display_clusters['total_amount'] = display_clusters['total_amount'].apply(lambda x: f"₹{x:.2f}")
                    display_clusters.columns = ['Pattern', 'Average Amount', 'Total Amount', 'Transactions', 'Dominant Emotion', 'Emotion Intensity', 'Dominant Category']
                    
                    st.dataframe(display_clusters, use_container_width=True)
                    
                    # Visualize clusters
                    st.markdown("#### Visualization of Spending Patterns")
                    
                    # Get clustered data
                    clustered_data = patterns['clustered_data']
                    
                    # Select features for visualization
                    features_used = patterns['features_used']
                    
                    if len(features_used) >= 2:
                        # Create scatter plot of first two features
                        fig = px.scatter(clustered_data, x=features_used[0], y=features_used[1], color='cluster',
                                       labels={features_used[0]: features_used[0].capitalize(), features_used[1]: features_used[1].capitalize(), 'cluster': 'Pattern'},
                                       title=f'Spending Patterns: {features_used[0].capitalize()} vs. {features_used[1].capitalize()}',
                                       hover_data=['emotion', 'category', 'amount'],
                                       color_discrete_sequence=px.colors.qualitative.Set1)
                        
                        # Update layout
                        fig.update_layout(
                            xaxis_title=features_used[0].capitalize(),
                            yaxis_title=features_used[1].capitalize(),
                            legend_title="Pattern"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Generate insights
                    insights = generate_emotion_insights(emotion_stats, category_emotion, patterns)
                    
                    # Display insights
                    st.markdown("#### Your Personalized Insights")
                    
                    if not insights:
                        st.info("Not enough data to generate personalized insights yet. Please continue tracking emotions and making transactions.")
                    else:
                        for i, insight in enumerate(insights, 1):
                            st.markdown(f"**{i}. {insight}**")
                    
                    # Display emotion spending summary
                    st.markdown("#### Emotion Spending Summary")
                    
                    # Calculate summary statistics
                    if emotion_stats is not None and len(emotion_stats) > 0:
                        # Exclude 'Unknown' emotion
                        known_emotions = emotion_stats[emotion_stats['emotion'] != 'Unknown']
                        
                        if len(known_emotions) > 0:
                            # Highest spending emotion
                            highest_emotion = known_emotions.loc[known_emotions['total_amount'].idxmax()]
                            
                            # Lowest spending emotion
                            lowest_emotion = known_emotions.loc[known_emotions['total_amount'].idxmin()]
                            
                            # Highest average transaction
                            highest_avg = known_emotions.loc[known_emotions['avg_amount'].idxmax()]
                            
                            # Display metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Highest Spending Emotion", highest_emotion['emotion'], f"₹{highest_emotion['total_amount']:.2f}")
                                st.metric("Highest Avg. Transaction", highest_avg['emotion'], f"₹{highest_avg['avg_amount']:.2f}")
                            with col2:
                                st.metric("Lowest Spending Emotion", lowest_emotion['emotion'], f"₹{lowest_emotion['total_amount']:.2f}")
                                st.metric("Spending Difference", "", f"₹{highest_emotion['total_amount'] - lowest_emotion['total_amount']:.2f}")
    
    with tab4:
        st.markdown("### Recommendations")
        st.write("Get personalized recommendations to help you manage emotional spending.")
        
        # Prepare transaction data
        tx_df = prepare_transaction_data(st.session_state.current_user)
        
        # Prepare emotions data
        emotions_df = prepare_emotions_data(st.session_state.current_user)
        
        if tx_df is None or len(tx_df) < 5:
            st.warning("You need at least 5 transactions for recommendations. Please continue using the app to generate more transaction data.")
        elif emotions_df is None or len(emotions_df) == 0:
            st.warning("You haven't tracked any emotions yet. Track your emotions in the 'Track Emotions' tab to get personalized recommendations.")
        else:
            # Merge transaction and emotion data
            merged_df = merge_transaction_emotion_data(tx_df, emotions_df)
            
            if merged_df is None:
                st.error("Failed to merge transaction and emotion data. Please try again later.")
            else:
                # Analyze spending by emotion
                emotion_stats = analyze_spending_by_emotion(merged_df)
                
                # Analyze category spending by emotion
                category_emotion = analyze_category_by_emotion(merged_df)
                
                # Detect spending patterns
                patterns = detect_spending_patterns(merged_df)
                
                # Generate recommendations
                recommendations = generate_recommendations(emotion_stats, category_emotion, patterns)
                
                # Display recommendations
                st.markdown("#### Your Personalized Recommendations")
                
                if not recommendations:
                    st.info("Not enough data to generate personalized recommendations yet. Please continue tracking emotions and making transactions.")
                else:
                    for i, recommendation in enumerate(recommendations, 1):
                        st.markdown(f"**{i}. {recommendation}**")
                
                # Display emotional spending strategies
                st.markdown("#### Strategies to Manage Emotional Spending")
                
                strategies = [
                    "**24-Hour Rule**: Wait 24 hours before making non-essential purchases when experiencing strong emotions.",
                    "**Emotion Journal**: Keep a journal of your emotions and spending to identify patterns and triggers.",
                    "**Budget for Emotional Spending**: Set aside a small amount each month specifically for 'emotional spending'.",
                    "**Find Free Alternatives**: Create a list of free activities that can provide emotional relief instead of shopping.",
                    "**Accountability Partner**: Share your financial goals with a trusted friend who can help keep you accountable.",
                    "**Mindfulness Practices**: Practice mindfulness or meditation to help manage strong emotions without spending.",
                    "**Unsubscribe from Shopping Emails**: Reduce temptation by unsubscribing from retailer emails and newsletters.",
                    "**Delete Shopping Apps**: Remove shopping apps from your phone to reduce impulse purchases.",
                    "**Set Specific Goals**: Create specific financial goals to focus on when you feel the urge to spend.",
                    "**Reward System**: Create a non-monetary reward system for achieving financial goals."
                ]
                
                for strategy in strategies:
                    st.markdown(strategy)
                
                # Create a personalized action plan
                st.markdown("#### Your Personalized Action Plan")
                
                # Determine which emotions to focus on
                focus_emotions = []
                if emotion_stats is not None and len(emotion_stats) > 0:
                    # Exclude 'Unknown' emotion and sort by average amount
                    known_emotions = emotion_stats[emotion_stats['emotion'] != 'Unknown'].sort_values('avg_amount', ascending=False)
                    
                    if len(known_emotions) > 0:
                        # Take top 2 emotions with highest average spending
                        focus_emotions = known_emotions.head(2)['emotion'].tolist()
                
                if not focus_emotions:
                    st.info("Continue tracking your emotions to receive a personalized action plan.")
                else:
                    st.markdown("Based on your spending patterns, here's a personalized action plan to help you manage emotional spending:")
                    
                    # Create action plan steps
                    action_plan = []
                    
                    # Step 1: Awareness
                    action_plan.append(f"**1. Increase Awareness**: Pay special attention to your spending triggers when feeling **{' or '.join(focus_emotions)}**.")
                    
                    # Step 2: Create a waiting period
                    action_plan.append(f"**2. Implement a Waiting Period**: When feeling **{' or '.join(focus_emotions)}**, wait at least 24 hours before making any non-essential purchase over ₹500.")
                    
                    # Step 3: Find alternatives
                    action_plan.append(f"**3. Develop Alternatives**: Create a list of 3-5 free or low-cost activities you enjoy that can help manage these emotions without spending.")
                    
                    # Step 4: Set a budget
                    action_plan.append("**4. Set an Emotional Spending Budget**: Allocate a small monthly amount specifically for emotional spending to allow flexibility while maintaining control.")
                    
                    # Step 5: Track progress
                    action_plan.append("**5. Track Your Progress**: Continue recording your emotions and reviewing your spending patterns weekly to see improvements.")
                    
                    # Display action plan
                    for step in action_plan:
                        st.markdown(step)
                    
                    # Add a call to action
                    st.info("💡 **Tip**: Review this action plan weekly and adjust as needed based on your progress.")
    
    # Initialize session state for emotions.json if it doesn't exist
    if not os.path.exists('emotions.json'):
        with open('emotions.json', 'w') as f:
            json.dump([], f)
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()