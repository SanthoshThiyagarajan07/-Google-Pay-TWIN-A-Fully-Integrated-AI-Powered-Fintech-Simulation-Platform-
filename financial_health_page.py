def financial_health_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.preprocessing import StandardScaler
    import plotly.graph_objects as go
    import plotly.express as px
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Financial Health</h1>", unsafe_allow_html=True)
    
    # Load user data
    def load_users():
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                return json.load(f)
        return {}
    
    # Load transactions
    def load_transactions():
        if os.path.exists('transactions.json'):
            with open('transactions.json', 'r') as f:
                return json.load(f)
        return []
    
    # Load budget alerts
    def load_budget_alerts():
        if os.path.exists('budget_alerts.json'):
            with open('budget_alerts.json', 'r') as f:
                return json.load(f)
        return {}
    
    # Load savings goals
    def load_savings_goals():
        if os.path.exists('savings_goals.json'):
            with open('savings_goals.json', 'r') as f:
                return json.load(f)
        return {}
    
    # Load subscriptions
    def load_subscriptions():
        if os.path.exists('subscriptions.json'):
            with open('subscriptions.json', 'r') as f:
                return json.load(f)
        return {}
    
    # Calculate financial health score
    def calculate_financial_health_score(username):
        users = load_users()
        transactions = load_transactions()
        budget_alerts = load_budget_alerts()
        savings_goals = load_savings_goals()
        subscriptions = load_subscriptions()
        
        # Initialize score components
        savings_score = 0
        spending_score = 0
        budget_score = 0
        income_stability_score = 0
        debt_score = 0
        
        # Get user data
        if username not in users:
            return 0, {}
        
        user = users[username]
        balance = user.get('balance', 0)
        
        # Get user transactions for the last 3 months
        now = datetime.now()
        three_months_ago = now - timedelta(days=90)
        
        user_transactions = [t for t in transactions if 
                            (t['sender'] == username or t['recipient'] == username) and
                            datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S') >= three_months_ago]
        
        # Calculate total income and expenses
        income = sum(t['amount'] for t in user_transactions if t['recipient'] == username and t['type'] != 'cashback_redemption')
        expenses = sum(t['amount'] for t in user_transactions if t['sender'] == username and t['type'] not in ['savings_deposit', 'investment'])
        
        # Calculate savings
        savings_deposits = sum(t['amount'] for t in user_transactions if t['sender'] == username and t['type'] == 'savings_deposit')
        savings_rate = savings_deposits / income if income > 0 else 0
        
        # 1. Savings Score (0-20 points)
        if savings_rate >= 0.2:  # Saving 20% or more of income
            savings_score = 20
        elif savings_rate >= 0.15:
            savings_score = 15
        elif savings_rate >= 0.1:
            savings_score = 10
        elif savings_rate >= 0.05:
            savings_score = 5
        else:
            savings_score = 0
        
        # Check if user has savings goals
        user_goals = savings_goals.get(username, [])
        if user_goals:
            active_goals = [g for g in user_goals if not g.get('completed', False)]
            if active_goals:
                savings_score += 5  # Bonus for having active savings goals
        
        # 2. Spending Score (0-20 points)
        expense_to_income_ratio = expenses / income if income > 0 else 1
        
        if expense_to_income_ratio <= 0.6:  # Spending less than 60% of income
            spending_score = 20
        elif expense_to_income_ratio <= 0.7:
            spending_score = 15
        elif expense_to_income_ratio <= 0.8:
            spending_score = 10
        elif expense_to_income_ratio <= 0.9:
            spending_score = 5
        else:
            spending_score = 0
        
        # 3. Budget Score (0-20 points)
        user_budget_alerts = budget_alerts.get(username, {})
        
        if user_budget_alerts:
            # Calculate how many budget categories are within limits
            categories_within_budget = 0
            total_categories = len(user_budget_alerts)
            
            # Get spending by category
            category_spending = {}
            for t in user_transactions:
                if t['sender'] == username and t.get('category'):
                    category = t.get('category')
                    if category in category_spending:
                        category_spending[category] += t['amount']
                    else:
                        category_spending[category] = t['amount']
            
            # Check each budget category
            for category, alert in user_budget_alerts.items():
                spent = category_spending.get(category, 0)
                if spent <= alert['limit']:
                    categories_within_budget += 1
            
            budget_adherence_rate = categories_within_budget / total_categories if total_categories > 0 else 0
            
            if budget_adherence_rate >= 0.9:  # 90% or more categories within budget
                budget_score = 20
            elif budget_adherence_rate >= 0.75:
                budget_score = 15
            elif budget_adherence_rate >= 0.6:
                budget_score = 10
            elif budget_adherence_rate >= 0.4:
                budget_score = 5
            else:
                budget_score = 0
        else:
            # No budget alerts set
            budget_score = 5  # Neutral score for no budgets
        
        # 4. Income Stability Score (0-20 points)
        # Group transactions by month to check income consistency
        monthly_income = {}
        for t in user_transactions:
            if t['recipient'] == username and t['type'] in ['add_money', 'receive_money']:
                month = datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                if month in monthly_income:
                    monthly_income[month] += t['amount']
                else:
                    monthly_income[month] = t['amount']
        
        # Check income stability across months
        if len(monthly_income) >= 3:  # Have data for at least 3 months
            income_values = list(monthly_income.values())
            income_std = np.std(income_values)
            income_mean = np.mean(income_values)
            income_variation = income_std / income_mean if income_mean > 0 else 1
            
            if income_variation <= 0.1:  # Very stable income (less than 10% variation)
                income_stability_score = 20
            elif income_variation <= 0.2:
                income_stability_score = 15
            elif income_variation <= 0.3:
                income_stability_score = 10
            elif income_variation <= 0.4:
                income_stability_score = 5
            else:
                income_stability_score = 0
        else:
            # Not enough data
            income_stability_score = 10  # Neutral score for insufficient data
        
        # 5. Debt Score (0-20 points)
        # Check for any "pay_later" transactions
        pay_later_transactions = [t for t in user_transactions if t['type'] == 'pay_later']
        total_debt = sum(t['amount'] for t in pay_later_transactions)
        
        # Calculate debt-to-income ratio
        debt_to_income_ratio = total_debt / income if income > 0 else 0
        
        if debt_to_income_ratio == 0:  # No debt
            debt_score = 20
        elif debt_to_income_ratio <= 0.1:  # Debt less than 10% of income
            debt_score = 15
        elif debt_to_income_ratio <= 0.2:
            debt_score = 10
        elif debt_to_income_ratio <= 0.3:
            debt_score = 5
        else:
            debt_score = 0
        
        # Calculate total score (0-100)
        total_score = savings_score + spending_score + budget_score + income_stability_score + debt_score
        
        # Prepare score breakdown
        score_breakdown = {
            "Savings": savings_score,
            "Spending": spending_score,
            "Budget Management": budget_score,
            "Income Stability": income_stability_score,
            "Debt Management": debt_score,
            "Total": total_score
        }
        
        return total_score, score_breakdown
    
    # Get financial insights
    def get_financial_insights(username):
        transactions = load_transactions()
        budget_alerts = load_budget_alerts()
        savings_goals = load_savings_goals()
        subscriptions = load_subscriptions()
        
        # Get user transactions for the last 3 months
        now = datetime.now()
        three_months_ago = now - timedelta(days=90)
        
        user_transactions = [t for t in transactions if 
                            (t['sender'] == username or t['recipient'] == username) and
                            datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S') >= three_months_ago]
        
        insights = []
        
        # 1. Check spending trends
        if len(user_transactions) > 0:
            # Group by category
            category_spending = {}
            for t in user_transactions:
                if t['sender'] == username and t.get('category'):
                    category = t.get('category', 'Other')
                    if category in category_spending:
                        category_spending[category] += t['amount']
                    else:
                        category_spending[category] = t['amount']
            
            # Find top spending categories
            if category_spending:
                sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
                top_category, top_amount = sorted_categories[0]
                
                insights.append({
                    "type": "spending",
                    "message": f"Your highest spending category is {top_category} (₹{top_amount:.2f}).",
                    "action": "Consider setting a budget for this category."
                })
                
                # Check for unusual spending
                if len(sorted_categories) > 1:
                    second_category, second_amount = sorted_categories[1]
                    if top_amount > second_amount * 2:  # Top category is more than double the second
                        insights.append({
                            "type": "alert",
                            "message": f"Your spending on {top_category} is significantly higher than other categories.",
                            "action": "Review your expenses in this category for potential savings."
                        })
        
        # 2. Check budget adherence
        user_budget_alerts = budget_alerts.get(username, {})
        if user_budget_alerts:
            # Get spending by category
            category_spending = {}
            for t in user_transactions:
                if t['sender'] == username and t.get('category'):
                    category = t.get('category')
                    if category in category_spending:
                        category_spending[category] += t['amount']
                    else:
                        category_spending[category] = t['amount']
            
            # Check each budget category
            for category, alert in user_budget_alerts.items():
                spent = category_spending.get(category, 0)
                if spent > alert['limit']:
                    insights.append({
                        "type": "budget",
                        "message": f"You've exceeded your budget for {category} (₹{spent:.2f} vs ₹{alert['limit']:.2f}).",
                        "action": "Review your spending in this category or adjust your budget."
                    })
                elif spent > alert['limit'] * 0.9:  # Close to limit
                    insights.append({
                        "type": "warning",
                        "message": f"You're close to your budget limit for {category} (₹{spent:.2f} of ₹{alert['limit']:.2f}).",
                        "action": "Monitor your spending in this category closely."
                    })
        else:
            insights.append({
                "type": "suggestion",
                "message": "You haven't set any budget alerts yet.",
                "action": "Setting budgets can help you manage your spending better."
            })
        
        # 3. Check savings goals progress
        user_goals = savings_goals.get(username, [])
        if user_goals:
            active_goals = [g for g in user_goals if not g.get('completed', False)]
            if active_goals:
                for goal in active_goals:
                    progress_pct = (goal['current_amount'] / goal['target_amount']) * 100
                    target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d').date()
                    days_remaining = (target_date - now.date()).days
                    
                    if days_remaining <= 0 and progress_pct < 100:  # Overdue goal
                        insights.append({
                            "type": "alert",
                            "message": f"Your savings goal '{goal['name']}' is overdue with only {progress_pct:.1f}% saved.",
                            "action": "Consider extending the deadline or increasing your contributions."
                        })
                    elif days_remaining > 0 and progress_pct < (100 - days_remaining / target_date.day * 100):  # Behind schedule
                        insights.append({
                            "type": "warning",
                            "message": f"You're behind schedule on your '{goal['name']}' savings goal ({progress_pct:.1f}%).",
                            "action": "Consider increasing your regular contributions."
                        })
            else:
                insights.append({
                    "type": "suggestion",
                    "message": "You've completed all your savings goals. Great job!",
                    "action": "Consider setting new savings goals for future financial security."
                })
        else:
            insights.append({
                "type": "suggestion",
                "message": "You haven't set any savings goals yet.",
                "action": "Setting savings goals can help you build financial security."
            })
        
        # 4. Check subscription management
        user_subscriptions = subscriptions.get(username, [])
        if user_subscriptions:
            active_subscriptions = [s for s in user_subscriptions if s.get('active', True)]
            
            # Calculate monthly subscription cost
            monthly_cost = 0
            for sub in active_subscriptions:
                amount = sub['amount']
                if sub['billing_frequency'] == "Quarterly":
                    monthly_cost += amount / 3
                elif sub['billing_frequency'] == "Semi-Annual":
                    monthly_cost += amount / 6
                elif sub['billing_frequency'] == "Annual":
                    monthly_cost += amount / 12
                else:  # Monthly
                    monthly_cost += amount
            
            # Calculate income (approximate monthly)
            monthly_income = 0
            monthly_transactions = {}
            for t in user_transactions:
                if t['recipient'] == username and t['type'] in ['add_money', 'receive_money']:
                    month = datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                    if month in monthly_transactions:
                        monthly_transactions[month] += t['amount']
                    else:
                        monthly_transactions[month] = t['amount']
            
            if monthly_transactions:
                monthly_income = sum(monthly_transactions.values()) / len(monthly_transactions)
            
            # Check if subscriptions are too high relative to income
            if monthly_income > 0 and monthly_cost > monthly_income * 0.1:  # More than 10% of income
                insights.append({
                    "type": "alert",
                    "message": f"Your subscriptions cost ₹{monthly_cost:.2f}/month ({(monthly_cost/monthly_income*100):.1f}% of your income).",
                    "action": "Review your subscriptions and consider canceling unused ones."
                })
            
            # Check for duplicate category subscriptions
            category_counts = {}
            for sub in active_subscriptions:
                category = sub['category']
                if category in category_counts:
                    category_counts[category] += 1
                else:
                    category_counts[category] = 1
            
            # Find categories with multiple subscriptions
            duplicate_categories = {k: v for k, v in category_counts.items() if v > 1}
            if duplicate_categories:
                category, count = max(duplicate_categories.items(), key=lambda x: x[1])
                insights.append({
                    "type": "suggestion",
                    "message": f"You have {count} subscriptions in the {category} category.",
                    "action": "Consider consolidating these subscriptions to save money."
                })
        
        # 5. Check income vs expenses trend
        if len(user_transactions) > 0:
            # Group by month
            monthly_data = {}
            for t in user_transactions:
                month = datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                
                if month not in monthly_data:
                    monthly_data[month] = {"income": 0, "expenses": 0}
                
                if t['recipient'] == username and t['type'] in ['add_money', 'receive_money']:
                    monthly_data[month]["income"] += t['amount']
                elif t['sender'] == username and t['type'] not in ['savings_deposit', 'investment']:
                    monthly_data[month]["expenses"] += t['amount']
            
            # Check for months where expenses exceed income
            for month, data in monthly_data.items():
                if data["expenses"] > data["income"]:
                    month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
                    insights.append({
                        "type": "alert",
                        "message": f"In {month_name}, your expenses (₹{data['expenses']:.2f}) exceeded your income (₹{data['income']:.2f}).",
                        "action": "Review your spending for that month to identify areas for improvement."
                    })
        
        return insights
    
    # Get personalized recommendations
    def get_recommendations(score, insights):
        recommendations = []
        
        # Based on overall score
        if score < 40:
            recommendations.append({
                "category": "General",
                "title": "Improve Your Financial Basics",
                "description": "Your financial health score indicates you need to focus on fundamental financial habits.",
                "actions": [
                    "Create a basic budget to track income and expenses",
                    "Build an emergency fund with at least 1 month of expenses",
                    "Reduce non-essential spending until your income exceeds expenses"
                ]
            })
        elif score < 70:
            recommendations.append({
                "category": "General",
                "title": "Strengthen Your Financial Foundation",
                "description": "You have some good financial habits, but there's room for improvement.",
                "actions": [
                    "Increase your emergency fund to 3-6 months of expenses",
                    "Review and optimize your budget categories",
                    "Set specific savings goals for major expenses"
                ]
            })
        else:
            recommendations.append({
                "category": "General",
                "title": "Optimize Your Financial Strategy",
                "description": "You have strong financial habits. Focus on optimization and growth.",
                "actions": [
                    "Consider investment opportunities for long-term growth",
                    "Optimize tax strategies to maximize your income",
                    "Review insurance coverage to protect your financial assets"
                ]
            })
        
        # Based on insights
        budget_issues = [i for i in insights if i["type"] in ["budget", "warning"] and "budget" in i["message"].lower()]
        if budget_issues:
            recommendations.append({
                "category": "Budgeting",
                "title": "Improve Budget Management",
                "description": "You have some budget categories that need attention.",
                "actions": [
                    "Review and adjust budget limits for problematic categories",
                    "Track expenses more frequently to stay within budget",
                    "Consider using the 50/30/20 rule: 50% needs, 30% wants, 20% savings"
                ]
            })
        
        savings_issues = [i for i in insights if "savings goal" in i["message"].lower()]
        if savings_issues:
            recommendations.append({
                "category": "Savings",
                "title": "Enhance Your Savings Strategy",
                "description": "Your savings goals need attention to stay on track.",
                "actions": [
                    "Set up automatic transfers to your savings goals",
                    "Break large savings goals into smaller milestones",
                    "Consider the 24-hour rule before making large purchases"
                ]
            })
        
        subscription_issues = [i for i in insights if "subscription" in i["message"].lower()]
        if subscription_issues:
            recommendations.append({
                "category": "Subscriptions",
                "title": "Optimize Your Subscriptions",
                "description": "Your subscription costs may be impacting your financial health.",
                "actions": [
                    "Audit all subscriptions and cancel unused or redundant services",
                    "Consider sharing subscription costs with family or friends",
                    "Switch to annual billing for frequently used services to save money"
                ]
            })
        
        income_expense_issues = [i for i in insights if "expenses exceeded your income" in i["message"].lower()]
        if income_expense_issues:
            recommendations.append({
                "category": "Income & Expenses",
                "title": "Balance Your Income and Expenses",
                "description": "You've had periods where expenses exceeded income, which is unsustainable.",
                "actions": [
                    "Identify and reduce non-essential expenses",
                    "Look for additional income sources or side hustles",
                    "Build an emergency fund to cover unexpected expenses"
                ]
            })
        
        # Add general recommendations if specific ones are few
        if len(recommendations) < 3:
            recommendations.append({
                "category": "Financial Education",
                "title": "Enhance Your Financial Knowledge",
                "description": "Continuous learning about personal finance can improve your financial decisions.",
                "actions": [
                    "Read books or follow blogs about personal finance",
                    "Take free online courses on budgeting and investing",
                    "Set specific financial goals with deadlines"
                ]
            })
        
        return recommendations
    
    # Main content
    username = st.session_state.current_user
    
    # Calculate financial health score
    score, score_breakdown = calculate_financial_health_score(username)
    
    # Display score
    st.markdown("### Your Financial Health Score")
    
    # Score gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Financial Health"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': "#EA4335"},  # Red
                {'range': [40, 70], 'color': "#FBBC05"},  # Yellow
                {'range': [70, 100], 'color': "#34A853"}  # Green
            ],
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Score interpretation
    if score < 40:
        st.error("Your financial health needs significant improvement. Focus on building basic financial habits.")
    elif score < 70:
        st.warning("Your financial health is moderate. There are several areas where you can improve.")
    else:
        st.success("Your financial health is good! Continue your positive financial habits and focus on optimization.")
    
    # Score breakdown
    st.markdown("### Score Breakdown")
    
    # Create radar chart for score components
    categories = list(score_breakdown.keys())[:-1]  # Exclude total
    values = [score_breakdown[cat] for cat in categories]
    
    # Add the first value at the end to close the polygon (only if categories is not empty)
    if categories:
        categories.append(categories[0])
        values.append(values[0])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Score',
        line_color='#4285F4',
        fillcolor='rgba(66, 133, 244, 0.3)'
    ))
    
    # Add ideal score (20 in each category)
    ideal_values = [20] * len(categories)
    
    fig.add_trace(go.Scatterpolar(
        r=ideal_values,
        theta=categories,
        fill='toself',
        name='Ideal Score',
        line_color='#34A853',
        fillcolor='rgba(52, 168, 83, 0.1)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 20]
            )),
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display score components
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Component Scores (out of 20)")
        for category, value in list(score_breakdown.items())[:-1]:  # Exclude total
            st.markdown(f"**{category}:** {value}")
    
    with col2:
        st.markdown("#### What These Scores Mean")
        st.markdown("**Savings:** How well you're saving for the future")
        st.markdown("**Spending:** How well you manage your expenses relative to income")
        st.markdown("**Budget Management:** How well you stick to your budgets")
        st.markdown("**Income Stability:** How consistent your income is")
        st.markdown("**Debt Management:** How well you manage and minimize debt")
    
    # Get insights
    insights = get_financial_insights(username)
    
    # Display insights
    st.markdown("### Financial Insights")
    
    if not insights:
        st.info("We don't have enough data to generate insights yet. Continue using the app to get personalized insights.")
    else:
        for i, insight in enumerate(insights):
            with st.container():
                if insight["type"] == "alert":
                    st.error(f"**{insight['message']}**")
                elif insight["type"] == "warning":
                    st.warning(f"**{insight['message']}**")
                elif insight["type"] == "suggestion":
                    st.info(f"**{insight['message']}**")
                else:
                    st.markdown(f"**{insight['message']}**")
                
                st.markdown(f"*Recommendation: {insight['action']}*")
                
                if i < len(insights) - 1:
                    st.markdown("---")
    
    # Get recommendations
    recommendations = get_recommendations(score, insights)
    
    # Display recommendations
    st.markdown("### Personalized Recommendations")
    
    for i, recommendation in enumerate(recommendations):
        with st.expander(f"{recommendation['category']}: {recommendation['title']}"):
            st.markdown(f"**{recommendation['description']}**")
            st.markdown("**Actions to Take:**")
            for action in recommendation['actions']:
                st.markdown(f"- {action}")
    
    # Financial health trends
    st.markdown("### Your Financial Health Trends")
    
    # Get historical transactions
    transactions = load_transactions()
    user_transactions = [t for t in transactions if t['sender'] == username or t['recipient'] == username]
    
    if len(user_transactions) > 10:  # Only show if enough data
        # Group by month
        monthly_data = {}
        for t in user_transactions:
            date = datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S')
            month = date.strftime('%Y-%m')
            
            if month not in monthly_data:
                monthly_data[month] = {
                    "income": 0, 
                    "expenses": 0, 
                    "savings": 0,
                    "balance": 0
                }
            
            if t['recipient'] == username and t['type'] in ['add_money', 'receive_money']:
                monthly_data[month]["income"] += t['amount']
            elif t['sender'] == username:
                if t['type'] == 'savings_deposit':
                    monthly_data[month]["savings"] += t['amount']
                elif t['type'] not in ['investment']:
                    monthly_data[month]["expenses"] += t['amount']
        
        # Sort months
        sorted_months = sorted(monthly_data.keys())
        
        # Calculate running balance
        balance = 0
        for month in sorted_months:
            balance += monthly_data[month]["income"] - monthly_data[month]["expenses"]
            monthly_data[month]["balance"] = balance
        
        # Create dataframe for plotting
        df = pd.DataFrame({
            "Month": [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in sorted_months],
            "Income": [monthly_data[m]["income"] for m in sorted_months],
            "Expenses": [monthly_data[m]["expenses"] for m in sorted_months],
            "Savings": [monthly_data[m]["savings"] for m in sorted_months],
            "Balance": [monthly_data[m]["balance"] for m in sorted_months]
        })
        
        # Income vs Expenses chart
        fig = px.bar(df, x="Month", y=["Income", "Expenses", "Savings"],
                    title="Monthly Income, Expenses, and Savings",
                    labels={"value": "Amount (₹)", "variable": "Category"},
                    color_discrete_map={"Income": "#34A853", "Expenses": "#EA4335", "Savings": "#4285F4"})
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Balance trend
        fig = px.line(df, x="Month", y="Balance", title="Balance Trend",
                    labels={"Balance": "Amount (₹)"}, markers=True)
        fig.update_traces(line_color="#4285F4")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Savings rate
        df["Savings Rate"] = (df["Savings"] / df["Income"]) * 100
        df["Savings Rate"] = df["Savings Rate"].fillna(0)
        
        fig = px.line(df, x="Month", y="Savings Rate", title="Monthly Savings Rate (%)",
                    labels={"Savings Rate": "Percentage (%)"}, markers=True)
        fig.update_traces(line_color="#34A853")
        fig.update_layout(yaxis_range=[0, max(df["Savings Rate"]) * 1.1 if max(df["Savings Rate"]) > 0 else 10])
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Continue using the app to see your financial health trends over time.")
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()