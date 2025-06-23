import streamlit as st
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AIRecommendationEngine:
    def __init__(self):
        self.user_data = self.load_user_data()
        self.transactions = self.load_transactions()
        self.savings_goals = self.load_savings_goals()
        self.budget_alerts = self.load_budget_alerts()
    
    def load_user_data(self):
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                return json.load(f)
        return {}
    
    def load_transactions(self):
        if os.path.exists('transactions.json'):
            with open('transactions.json', 'r') as f:
                return json.load(f)
        return []
    
    def load_savings_goals(self):
        if os.path.exists('savings_goals.json'):
            with open('savings_goals.json', 'r') as f:
                return json.load(f)
        return {}
    
    def load_budget_alerts(self):
        if os.path.exists('budget_alerts.json'):
            with open('budget_alerts.json', 'r') as f:
                return json.load(f)
        return {}
    
    def get_user_transactions(self, username, days=30):
        """Get user transactions for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        user_transactions = []
        
        for transaction in self.transactions:
            if (transaction.get('sender') == username or transaction.get('recipient') == username):
                try:
                    trans_date = datetime.strptime(transaction['date'], '%Y-%m-%d %H:%M:%S')
                    if trans_date >= cutoff_date:
                        user_transactions.append(transaction)
                except:
                    continue
        
        return user_transactions
    
    def analyze_spending_patterns(self, username):
        """Analyze user's spending patterns"""
        transactions = self.get_user_transactions(username, days=90)
        
        # Calculate spending by category
        spending_by_category = {}
        total_spending = 0
        
        for transaction in transactions:
            if transaction.get('sender') == username and transaction.get('type') not in ['savings_deposit', 'investment']:
                category = transaction.get('category', 'Other')
                amount = transaction.get('amount', 0)
                
                if category in spending_by_category:
                    spending_by_category[category] += amount
                else:
                    spending_by_category[category] = amount
                
                total_spending += amount
        
        return spending_by_category, total_spending
    
    def get_savings_recommendations(self, username):
        """Generate savings recommendations"""
        recommendations = []
        
        # Get user's current balance and spending
        user = self.user_data.get(username, {})
        balance = user.get('balance', 0)
        
        spending_by_category, total_spending = self.analyze_spending_patterns(username)
        
        # Recommendation 1: Emergency Fund
        monthly_expenses = total_spending / 3  # 3 months of data
        emergency_fund_target = monthly_expenses * 6
        
        user_goals = self.savings_goals.get(username, [])
        has_emergency_fund = any(goal.get('category') == 'Emergency Fund' for goal in user_goals)
        
        if not has_emergency_fund and balance < emergency_fund_target:
            recommendations.append({
                'type': 'savings',
                'title': 'Build an Emergency Fund',
                'description': f'Consider saving ₹{emergency_fund_target:.2f} (6 months of expenses) for emergencies.',
                'priority': 'high',
                'action': 'Create a savings goal for emergency fund',
                'potential_savings': emergency_fund_target
            })
        
        # Recommendation 2: Reduce high spending categories
        if spending_by_category:
            highest_category = max(spending_by_category, key=spending_by_category.get)
            highest_amount = spending_by_category[highest_category]
            
            if highest_amount > total_spending * 0.3:  # More than 30% of spending
                potential_reduction = highest_amount * 0.2  # 20% reduction
                recommendations.append({
                    'type': 'spending',
                    'title': f'Reduce {highest_category} Spending',
                    'description': f'You spend ₹{highest_amount:.2f} on {highest_category}. Consider reducing by 20%.',
                    'priority': 'medium',
                    'action': f'Set a budget limit for {highest_category}',
                    'potential_savings': potential_reduction
                })
        
        # Recommendation 3: Increase savings rate
        transactions_30_days = self.get_user_transactions(username, days=30)
        monthly_income = sum(t['amount'] for t in transactions_30_days 
                           if t.get('recipient') == username and t.get('type') in ['add_money', 'receive_money'])
        monthly_spending = sum(t['amount'] for t in transactions_30_days 
                             if t.get('sender') == username and t.get('type') not in ['savings_deposit'])
        
        if monthly_income > 0:
            current_savings_rate = (monthly_income - monthly_spending) / monthly_income
            target_savings_rate = 0.2  # 20%
            
            if current_savings_rate < target_savings_rate:
                additional_savings = monthly_income * (target_savings_rate - current_savings_rate)
                recommendations.append({
                    'type': 'savings',
                    'title': 'Increase Your Savings Rate',
                    'description': f'Try to save {target_savings_rate*100:.0f}% of your income. You could save an additional ₹{additional_savings:.2f} monthly.',
                    'priority': 'medium',
                    'action': 'Set up automatic savings transfers',
                    'potential_savings': additional_savings * 12
                })
        
        return recommendations
    
    def get_investment_recommendations(self, username):
        """Generate investment recommendations"""
        recommendations = []
        
        user = self.user_data.get(username, {})
        balance = user.get('balance', 0)
        
        # Basic investment recommendations based on balance
        if balance > 10000:
            recommendations.append({
                'type': 'investment',
                'title': 'Start SIP Investment',
                'description': 'Consider starting a Systematic Investment Plan (SIP) in mutual funds.',
                'priority': 'medium',
                'action': 'Invest ₹1000-2000 monthly in diversified equity funds',
                'potential_returns': 'Expected 12-15% annual returns'
            })
        
        if balance > 50000:
            recommendations.append({
                'type': 'investment',
                'title': 'Diversify Your Portfolio',
                'description': 'Consider diversifying into different asset classes.',
                'priority': 'medium',
                'action': 'Allocate funds across equity, debt, and gold',
                'potential_returns': 'Balanced risk-return profile'
            })
        
        return recommendations
    
    def get_budget_recommendations(self, username):
        """Generate budget recommendations"""
        recommendations = []
        
        spending_by_category, total_spending = self.analyze_spending_patterns(username)
        user_budgets = self.budget_alerts.get(username, {})
        
        # Recommend budgets for categories without limits
        for category, amount in spending_by_category.items():
            if category not in user_budgets:
                suggested_limit = amount * 1.1  # 10% buffer
                recommendations.append({
                    'type': 'budget',
                    'title': f'Set Budget for {category}',
                    'description': f'You spent ₹{amount:.2f} on {category} recently. Consider setting a budget.',
                    'priority': 'low',
                    'action': f'Set monthly limit of ₹{suggested_limit:.2f} for {category}',
                    'suggested_limit': suggested_limit
                })
        
        return recommendations
    
    def get_comprehensive_insights(self, username):
        """Get comprehensive AI insights and recommendations"""
        insights = {
            'savings_recommendations': self.get_savings_recommendations(username),
            'investment_recommendations': self.get_investment_recommendations(username),
            'budget_recommendations': self.get_budget_recommendations(username),
            'spending_analysis': self.analyze_spending_patterns(username)
        }
        
        return insights

def ai_recommendations_page():
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>AI Recommendations</h1>", unsafe_allow_html=True)
    
    # Initialize AI engine
    ai_engine = AIRecommendationEngine()
    
    try:
        # Get comprehensive insights
        insights = ai_engine.get_comprehensive_insights(st.session_state.current_user)
        
        # Create tabs for different types of recommendations
        tab1, tab2, tab3, tab4 = st.tabs(["💰 Savings", "📈 Investments", "📊 Budget", "🔍 Analysis"])
        
        with tab1:
            st.header("Savings Recommendations")
            savings_recs = insights['savings_recommendations']
            
            if savings_recs:
                for i, rec in enumerate(savings_recs):
                    with st.container():
                        # Priority color coding
                        if rec['priority'] == 'high':
                            st.error(f"🔴 **{rec['title']}**")
                        elif rec['priority'] == 'medium':
                            st.warning(f"🟡 **{rec['title']}**")
                        else:
                            st.info(f"🟢 **{rec['title']}**")
                        
                        st.write(rec['description'])
                        st.write(f"**Recommended Action:** {rec['action']}")
                        
                        if 'potential_savings' in rec:
                            st.write(f"**Potential Annual Savings:** ₹{rec['potential_savings']:.2f}")
                        
                        st.markdown("---")
            else:
                st.success("Great! You're doing well with your savings. Keep it up!")
        
        with tab2:
            st.header("Investment Recommendations")
            investment_recs = insights['investment_recommendations']
            
            if investment_recs:
                for rec in investment_recs:
                    with st.container():
                        st.info(f"📈 **{rec['title']}**")
                        st.write(rec['description'])
                        st.write(f"**Recommended Action:** {rec['action']}")
                        st.write(f"**Expected Returns:** {rec['potential_returns']}")
                        st.markdown("---")
            else:
                st.info("Build up your savings first before considering investments.")
        
        with tab3:
            st.header("Budget Recommendations")
            budget_recs = insights['budget_recommendations']
            
            if budget_recs:
                for rec in budget_recs:
                    with st.container():
                        st.info(f"📊 **{rec['title']}**")
                        st.write(rec['description'])
                        st.write(f"**Recommended Action:** {rec['action']}")
                        
                        if 'suggested_limit' in rec:
                            st.write(f"**Suggested Monthly Limit:** ₹{rec['suggested_limit']:.2f}")
                        
                        st.markdown("---")
            else:
                st.success("You have good budget controls in place!")
        
        with tab4:
            st.header("Spending Analysis")
            spending_by_category, total_spending = insights['spending_analysis']
            
            if spending_by_category:
                # Create pie chart
                fig = px.pie(
                    values=list(spending_by_category.values()),
                    names=list(spending_by_category.keys()),
                    title="Spending by Category (Last 90 Days)"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show spending breakdown
                st.subheader("Category Breakdown")
                for category, amount in sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True):
                    percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
                    st.write(f"**{category}:** ₹{amount:.2f} ({percentage:.1f}%)")
                
                st.write(f"\n**Total Spending (90 days):** ₹{total_spending:.2f}")
                st.write(f"**Average Monthly Spending:** ₹{total_spending/3:.2f}")
            else:
                st.info("No spending data available for analysis.")
    
    except Exception as e:
        st.error(f"Error loading AI recommendations: {str(e)}")
        st.info("Please ensure you have some transaction history to generate recommendations.")
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()

if __name__ == "__main__":
    ai_recommendations_page()