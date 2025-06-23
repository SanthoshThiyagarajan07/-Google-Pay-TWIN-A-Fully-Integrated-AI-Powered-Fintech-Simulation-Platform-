def financial_assistant_page():
    import streamlit as st
    import json
    import os
    import pandas as pd
    from datetime import datetime, timedelta
    import random
    import re
    import matplotlib.pyplot as plt
    import numpy as np
    
    st.markdown("<h1 style='text-align: center; color: #4285F4;'>Financial Assistant</h1>", unsafe_allow_html=True)
    
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
    
    # Initialize chat history if not exists
    if 'financial_assistant_messages' not in st.session_state:
        st.session_state.financial_assistant_messages = [
            {"role": "assistant", "content": "Hello! I'm your financial assistant. How can I help you with your finances today?"}
        ]
    
    # Function to get user's spending by category in a date range
    def get_spending_by_category(username, start_date, end_date):
        transactions = load_transactions()
        
        # Convert dates to datetime objects for comparison
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Filter transactions by user and date range
        user_transactions = []
        for tx in transactions:
            if tx['sender'] == username and tx['type'] in ['send', 'pay_later']:
                tx_date = datetime.strptime(tx['date'].split()[0], '%Y-%m-%d')
                if start_date <= tx_date <= end_date:
                    user_transactions.append(tx)
        
        # Group by category and sum amounts
        spending_by_category = {}
        for tx in user_transactions:
            category = tx.get('category', 'Other')
            if category not in spending_by_category:
                spending_by_category[category] = 0
            spending_by_category[category] += tx['amount']
        
        return spending_by_category
    
    # Function to get total spending in a date range
    def get_total_spending(username, start_date, end_date):
        spending_by_category = get_spending_by_category(username, start_date, end_date)
        return sum(spending_by_category.values())
    
    # Function to get user's income in a date range
    def get_income(username, start_date, end_date):
        transactions = load_transactions()
        
        # Convert dates to datetime objects for comparison
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Filter transactions by user and date range
        income = 0
        for tx in transactions:
            if tx['recipient'] == username and tx['type'] in ['send', 'add']:
                tx_date = datetime.strptime(tx['date'].split()[0], '%Y-%m-%d')
                if start_date <= tx_date <= end_date:
                    income += tx['amount']
        
        return income
    
    # Function to get user's savings rate
    def get_savings_rate(username, start_date, end_date):
        income = get_income(username, start_date, end_date)
        spending = get_total_spending(username, start_date, end_date)
        
        if income == 0:
            return 0
        
        savings = income - spending
        savings_rate = (savings / income) * 100
        
        return max(0, savings_rate)  # Ensure non-negative
    
    # Function to get user's top spending categories
    def get_top_spending_categories(username, start_date, end_date, limit=3):
        spending_by_category = get_spending_by_category(username, start_date, end_date)
        
        # Sort categories by spending amount
        sorted_categories = sorted(
            spending_by_category.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_categories[:limit]
    
    # Function to get user's financial health score
    def calculate_financial_health_score(username):
        # Get data for the last 3 months
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        
        # Calculate savings rate
        savings_rate = get_savings_rate(username, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # Get spending data
        total_spending = get_total_spending(username, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # Get income data
        total_income = get_income(username, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # Get user balance
        users = load_users()
        balance = users.get(username, {}).get('balance', 0)
        
        # Calculate score components
        savings_score = min(100, savings_rate * 2)  # 0-100 points based on savings rate
        
        # Balance to income ratio (higher is better)
        if total_income > 0:
            balance_ratio = min(3, balance / (total_income / 3))  # Aim for 3 months of income as balance
            balance_score = balance_ratio * 33.33  # 0-100 points
        else:
            balance_score = 50  # Default if no income data
        
        # Spending to income ratio (lower is better)
        if total_income > 0:
            spending_ratio = min(1, total_spending / total_income)
            spending_score = 100 - (spending_ratio * 100)  # 0-100 points
        else:
            spending_score = 50  # Default if no income data
        
        # Calculate overall score (weighted average)
        overall_score = (
            savings_score * 0.4 +
            balance_score * 0.3 +
            spending_score * 0.3
        )
        
        return round(overall_score)
    
    # Function to generate financial insights
    def generate_insights(username):
        insights = []
        
        # Get data for different time periods
        today = datetime.now().date()
        last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_month_end = today.replace(day=1) - timedelta(days=1)
        this_month_start = today.replace(day=1)
        
        # Format dates as strings
        last_month_start_str = last_month_start.strftime('%Y-%m-%d')
        last_month_end_str = last_month_end.strftime('%Y-%m-%d')
        this_month_start_str = this_month_start.strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        # Get spending data
        last_month_spending = get_total_spending(username, last_month_start_str, last_month_end_str)
        this_month_spending = get_total_spending(username, this_month_start_str, today_str)
        
        # Get income data
        last_month_income = get_income(username, last_month_start_str, last_month_end_str)
        this_month_income = get_income(username, this_month_start_str, today_str)
        
        # Get top spending categories
        top_categories_last_month = get_top_spending_categories(username, last_month_start_str, last_month_end_str)
        top_categories_this_month = get_top_spending_categories(username, this_month_start_str, today_str)
        
        # Calculate days passed in current month and project monthly spending
        days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).day
        days_passed = today.day
        projected_spending = this_month_spending * (days_in_month / days_passed) if days_passed > 0 else 0
        
        # Generate insights
        
        # 1. Spending trend
        if last_month_spending > 0:
            spending_change_pct = ((projected_spending - last_month_spending) / last_month_spending) * 100
            if spending_change_pct > 10:
                insights.append(f"Your projected spending this month (₹{projected_spending:.2f}) is {spending_change_pct:.1f}% higher than last month. Consider reviewing your expenses.")
            elif spending_change_pct < -10:
                insights.append(f"Great job! Your projected spending this month (₹{projected_spending:.2f}) is {abs(spending_change_pct):.1f}% lower than last month.")
        
        # 2. Income vs. Spending
        if this_month_income > 0:
            income_spending_ratio = this_month_spending / this_month_income
            if income_spending_ratio > 0.9:
                insights.append(f"You've spent {income_spending_ratio:.1%} of your income this month. Try to keep this below 90% to build savings.")
            elif income_spending_ratio < 0.6:
                insights.append(f"You're saving {(1-income_spending_ratio):.1%} of your income this month. Great job maintaining a high savings rate!")
        
        # 3. Top spending category
        if top_categories_this_month:
            top_category, amount = top_categories_this_month[0]
            insights.append(f"Your highest spending category this month is {top_category} (₹{amount:.2f}).")
        
        # 4. Category-specific insights
        for category, amount in top_categories_this_month:
            # Find same category in last month
            last_month_amount = 0
            for cat, amt in top_categories_last_month:
                if cat == category:
                    last_month_amount = amt
                    break
            
            if last_month_amount > 0:
                change_pct = ((amount - last_month_amount) / last_month_amount) * 100
                if change_pct > 20:
                    insights.append(f"Your {category} spending has increased by {change_pct:.1f}% compared to last month.")
        
        # 5. Financial health score
        score = calculate_financial_health_score(username)
        if score >= 80:
            insights.append(f"Your financial health score is {score}/100. You're doing great with your finances!")
        elif score >= 60:
            insights.append(f"Your financial health score is {score}/100. You're on the right track, but there's room for improvement.")
        else:
            insights.append(f"Your financial health score is {score}/100. Let's work on improving your financial health.")
        
        # 6. General advice based on spending patterns
        if top_categories_this_month:
            if top_categories_this_month[0][0] == "Food & Dining" and top_categories_this_month[0][1] > 5000:
                insights.append("Your food spending is relatively high. Consider meal planning or cooking at home more often to save money.")
            elif top_categories_this_month[0][0] == "Shopping" and top_categories_this_month[0][1] > 5000:
                insights.append("Your shopping expenses are significant. Try implementing a 24-hour rule before making non-essential purchases.")
            elif top_categories_this_month[0][0] == "Entertainment" and top_categories_this_month[0][1] > 3000:
                insights.append("Your entertainment spending is notable. Look for free or low-cost alternatives for some activities.")
        
        return insights
    
    # Function to generate responses based on user query
    def generate_response(query, username):
        query = query.lower()
        
        # Get user data
        users = load_users()
        user_data = users.get(username, {})
        
        # Check for balance inquiry
        if re.search(r'(balance|how much (money|cash))', query):
            return f"Your current balance is ₹{user_data.get('balance', 0):.2f}."
        
        # Check for spending inquiries
        elif re.search(r'(spend|spent|spending)', query):
            # Check for time period in query
            if re.search(r'(today|yesterday)', query):
                if 'today' in query:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    spending = get_total_spending(username, date_str, date_str)
                    return f"You've spent ₹{spending:.2f} today."
                else:  # yesterday
                    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                    spending = get_total_spending(username, yesterday, yesterday)
                    return f"You spent ₹{spending:.2f} yesterday."
            
            elif re.search(r'(this|current) month', query):
                today = datetime.now().date()
                first_day = today.replace(day=1).strftime('%Y-%m-%d')
                today_str = today.strftime('%Y-%m-%d')
                spending = get_total_spending(username, first_day, today_str)
                return f"You've spent ₹{spending:.2f} so far this month."
            
            elif re.search(r'last month', query):
                today = datetime.now().date()
                last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')
                last_month_end = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
                spending = get_total_spending(username, last_month_start, last_month_end)
                return f"You spent ₹{spending:.2f} last month."
            
            # Check for category in query
            categories = ["Shopping", "Food & Dining", "Entertainment", "Travel", "Utilities", "Education", "Health", "Other"]
            for category in categories:
                if category.lower() in query or (category == "Food & Dining" and ("food" in query or "dining" in query or "restaurant" in query)):
                    # Check for time period with category
                    if re.search(r'(this|current) month', query):
                        today = datetime.now().date()
                        first_day = today.replace(day=1).strftime('%Y-%m-%d')
                        today_str = today.strftime('%Y-%m-%d')
                        spending = get_spending_by_category(username, first_day, today_str).get(category, 0)
                        return f"You've spent ₹{spending:.2f} on {category} so far this month."
                    
                    elif re.search(r'last month', query):
                        today = datetime.now().date()
                        last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')
                        last_month_end = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
                        spending = get_spending_by_category(username, last_month_start, last_month_end).get(category, 0)
                        return f"You spent ₹{spending:.2f} on {category} last month."
                    
                    else:  # Default to current month
                        today = datetime.now().date()
                        first_day = today.replace(day=1).strftime('%Y-%m-%d')
                        today_str = today.strftime('%Y-%m-%d')
                        spending = get_spending_by_category(username, first_day, today_str).get(category, 0)
                        return f"You've spent ₹{spending:.2f} on {category} so far this month."
            
            # Default spending response
            today = datetime.now().date()
            first_day = today.replace(day=1).strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')
            spending = get_total_spending(username, first_day, today_str)
            return f"You've spent ₹{spending:.2f} so far this month. Would you like to see a breakdown by category?"
        
        # Check for income inquiries
        elif re.search(r'(income|earn|earned|earning)', query):
            if re.search(r'(this|current) month', query):
                today = datetime.now().date()
                first_day = today.replace(day=1).strftime('%Y-%m-%d')
                today_str = today.strftime('%Y-%m-%d')
                income = get_income(username, first_day, today_str)
                return f"You've received ₹{income:.2f} so far this month."
            
            elif re.search(r'last month', query):
                today = datetime.now().date()
                last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')
                last_month_end = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
                income = get_income(username, last_month_start, last_month_end)
                return f"You received ₹{income:.2f} last month."
            
            else:  # Default to current month
                today = datetime.now().date()
                first_day = today.replace(day=1).strftime('%Y-%m-%d')
                today_str = today.strftime('%Y-%m-%d')
                income = get_income(username, first_day, today_str)
                return f"You've received ₹{income:.2f} so far this month."
        
        # Check for savings inquiries
        elif re.search(r'(saving|savings|save)', query):
            today = datetime.now().date()
            first_day = today.replace(day=1).strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')
            income = get_income(username, first_day, today_str)
            spending = get_total_spending(username, first_day, today_str)
            savings = income - spending
            
            if income > 0:
                savings_rate = (savings / income) * 100
                return f"You've saved ₹{savings:.2f} ({savings_rate:.1f}% of your income) so far this month."
            else:
                return f"You've saved ₹{savings:.2f} so far this month."
        
        # Check for financial health inquiries
        elif re.search(r'(financial health|health score|how am i doing)', query):
            score = calculate_financial_health_score(username)
            if score >= 80:
                return f"Your financial health score is {score}/100. You're doing great with your finances! Keep up the good work."
            elif score >= 60:
                return f"Your financial health score is {score}/100. You're on the right track, but there's room for improvement. Focus on increasing your savings rate and reducing unnecessary expenses."
            else:
                return f"Your financial health score is {score}/100. Let's work on improving your financial health. I recommend focusing on building an emergency fund and reducing non-essential spending."
        
        # Check for top spending inquiries
        elif re.search(r'(top spending|spend most|most spend|highest spending)', query):
            if re.search(r'(this|current) month', query):
                today = datetime.now().date()
                first_day = today.replace(day=1).strftime('%Y-%m-%d')
                today_str = today.strftime('%Y-%m-%d')
                top_categories = get_top_spending_categories(username, first_day, today_str)
            else:  # Default to last month for more complete data
                today = datetime.now().date()
                last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d')
                last_month_end = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d')
                top_categories = get_top_spending_categories(username, last_month_start, last_month_end)
            
            if not top_categories:
                return "I don't see any spending data for the selected period."
            
            response = "Your top spending categories are:\n"
            for i, (category, amount) in enumerate(top_categories):
                response += f"{i+1}. {category}: ₹{amount:.2f}\n"
            
            return response
        
        # Check for budget advice
        elif re.search(r'(budget|budgeting|how (much|should) (to|can|should) spend)', query):
            # Get income data for last 3 months
            today = datetime.now().date()
            three_months_ago = (today - timedelta(days=90)).strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')
            income = get_income(username, three_months_ago, today_str)
            
            # Calculate monthly average income
            monthly_income = income / 3
            
            if monthly_income <= 0:
                return "I don't have enough income data to provide personalized budget advice. As a general rule, try to allocate 50% of your income to needs, 30% to wants, and 20% to savings and debt repayment."
            
            # 50/30/20 rule
            needs = monthly_income * 0.5
            wants = monthly_income * 0.3
            savings = monthly_income * 0.2
            
            response = "Based on your average monthly income, here's a suggested budget using the 50/30/20 rule:\n\n"
            response += f"Needs (50%): ₹{needs:.2f} - This includes rent/mortgage, utilities, groceries, transportation, and insurance.\n\n"
            response += f"Wants (30%): ₹{wants:.2f} - This includes dining out, entertainment, shopping, and other non-essential expenses.\n\n"
            response += f"Savings/Debt (20%): ₹{savings:.2f} - This includes savings, investments, and debt repayment.\n\n"
            response += "Would you like more specific advice for any particular category?"
            
            return response
        
        # Check for saving advice
        elif re.search(r'(how to save|saving tips|save money)', query):
            # Get top spending categories to provide targeted advice
            today = datetime.now().date()
            three_months_ago = (today - timedelta(days=90)).strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')
            top_categories = get_top_spending_categories(username, three_months_ago, today_str)
            
            response = "Here are some personalized saving tips based on your spending patterns:\n\n"
            
            # General saving tips
            general_tips = [
                "Track your expenses regularly to identify areas where you can cut back.",
                "Set up automatic transfers to your savings account on payday.",
                "Use the 24-hour rule for non-essential purchases to avoid impulse buying.",
                "Look for cashback and rewards programs when making purchases.",
                "Review and cancel unused subscriptions and memberships.",
                "Consider using cash for discretionary spending to make it more tangible.",
                "Set specific, achievable saving goals to stay motivated.",
                "Shop with a list and avoid impulse purchases.",
                "Compare prices before making significant purchases.",
                "Use the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings."
            ]
            
            # Category-specific tips
            category_tips = {
                "Food & Dining": [
                    "Meal plan and cook at home more often instead of eating out.",
                    "Bring lunch to work instead of buying it.",
                    "Use grocery store loyalty programs and coupons.",
                    "Buy non-perishable items in bulk when they're on sale.",
                    "Reduce food waste by properly storing leftovers and using them for future meals."
                ],
                "Shopping": [
                    "Make a shopping list and stick to it to avoid impulse purchases.",
                    "Wait for sales to buy non-essential items.",
                    "Consider buying second-hand for certain items.",
                    "Unsubscribe from retail marketing emails to reduce temptation.",
                    "Implement a 'one in, one out' rule for clothing and household items."
                ],
                "Entertainment": [
                    "Look for free or low-cost entertainment options in your area.",
                    "Share subscription services with family or friends.",
                    "Use your local library for books, movies, and other media.",
                    "Take advantage of free trial periods, but remember to cancel if you don't want to continue.",
                    "Consider hosting potluck gatherings instead of going out."
                ],
                "Travel": [
                    "Plan trips in advance to get better deals.",
                    "Use price comparison websites for flights and accommodations.",
                    "Consider alternative accommodations like vacation rentals or hostels.",
                    "Travel during off-peak seasons for lower prices.",
                    "Use public transportation instead of taxis or rental cars when possible."
                ],
                "Utilities": [
                    "Reduce energy consumption by turning off lights and unplugging devices when not in use.",
                    "Install energy-efficient appliances and light bulbs.",
                    "Compare service providers annually to ensure you're getting the best rates.",
                    "Consider bundling services for discounts.",
                    "Adjust your thermostat to save on heating and cooling costs."
                ]
            }
            
            # Add category-specific tips based on top spending
            for category, _ in top_categories:
                if category in category_tips:
                    response += f"For {category}:\n"
                    for tip in random.sample(category_tips[category], min(3, len(category_tips[category]))):
                        response += f"- {tip}\n"
                    response += "\n"
            
            # Add general tips
            response += "General saving tips:\n"
            for tip in random.sample(general_tips, min(3, len(general_tips))):
                response += f"- {tip}\n"
            
            return response
        
        # Check for investment advice
        elif re.search(r'(invest|investment|investing)', query):
            response = "Here are some general investment principles to consider:\n\n"
            response += "1. **Emergency Fund First**: Before investing, ensure you have 3-6 months of expenses saved in an emergency fund.\n\n"
            response += "2. **Diversification**: Spread your investments across different asset classes to reduce risk.\n\n"
            response += "3. **Long-term Perspective**: Investing is most effective with a long-term horizon.\n\n"
            response += "4. **Regular Investing**: Consider setting up systematic investment plans (SIPs) for disciplined investing.\n\n"
            response += "5. **Risk Assessment**: Understand your risk tolerance before choosing investment vehicles.\n\n"
            response += "Common investment options include:\n"
            response += "- Mutual Funds\n"
            response += "- Stocks\n"
            response += "- Fixed Deposits\n"
            response += "- Public Provident Fund (PPF)\n"
            response += "- National Pension System (NPS)\n"
            response += "- Real Estate\n\n"
            response += "Would you like more specific information about any of these investment options?"
            
            return response
        
        # Check for debt management advice
        elif re.search(r'(debt|loan|credit|emi)', query):
            response = "Here are some principles for effective debt management:\n\n"
            response += "1. **Know Your Debts**: List all your debts with their interest rates and minimum payments.\n\n"
            response += "2. **Prioritize High-Interest Debt**: Focus on paying off high-interest debt first while making minimum payments on others.\n\n"
            response += "3. **Debt Snowball Method**: Alternatively, pay off smaller debts first for psychological wins.\n\n"
            response += "4. **Avoid New Debt**: While paying off existing debt, avoid taking on new debt.\n\n"
            response += "5. **Consider Refinancing**: Look into options for refinancing high-interest debt at lower rates.\n\n"
            response += "6. **Emergency Fund**: Build a small emergency fund to avoid new debt for unexpected expenses.\n\n"
            response += "Would you like more specific advice on any of these strategies?"
            
            return response
        
        # Check for financial goals
        elif re.search(r'(financial goal|money goal|saving goal)', query):
            response = "Setting SMART financial goals is key to financial success. Here are some common financial goals to consider:\n\n"
            response += "1. **Emergency Fund**: Save 3-6 months of expenses for unexpected situations.\n\n"
            response += "2. **Debt Repayment**: Create a plan to become debt-free.\n\n"
            response += "3. **Retirement Savings**: Start early and contribute regularly.\n\n"
            response += "4. **Major Purchases**: Save for a home, car, or other large expenses.\n\n"
            response += "5. **Education**: Save for your or your children's education.\n\n"
            response += "6. **Lifestyle Goals**: Save for vacations, weddings, or other life experiences.\n\n"
            response += "Would you like help setting up a specific financial goal?"
            
            return response
        
        # Check for insights request
        elif re.search(r'(insight|analyze|analysis|overview)', query):
            insights = generate_insights(username)
            
            if not insights:
                return "I don't have enough data to generate meaningful insights yet. Continue using the app for more personalized analysis."
            
            response = "Here are some insights based on your financial data:\n\n"
            for insight in insights:
                response += f"- {insight}\n\n"
            
            return response
        
        # Check for help request
        elif re.search(r'(help|what can you do|how (can|do) you)', query):
            response = "I'm your financial assistant! Here's how I can help you:\n\n"
            response += "- Check your balance and recent transactions\n"
            response += "- Track your spending by category and time period\n"
            response += "- Monitor your income and savings rate\n"
            response += "- Provide personalized financial insights\n"
            response += "- Offer budgeting and saving tips\n"
            response += "- Give general advice on investments and debt management\n"
            response += "- Help you set and track financial goals\n\n"
            response += "Try asking me questions like:\n"
            response += "- 'What's my balance?'\n"
            response += "- 'How much did I spend on food this month?'\n"
            response += "- 'What's my financial health score?'\n"
            response += "- 'How can I save more money?'\n"
            response += "- 'What are my top spending categories?'"
            
            return response
        
        # Generic greeting
        elif re.search(r'(hi|hello|hey|greetings)', query):
            greetings = [
                f"Hello! How can I help with your finances today?",
                f"Hi there! What would you like to know about your financial situation?",
                f"Hey! I'm here to help you manage your money better. What can I do for you?",
                f"Greetings! How can I assist with your financial questions today?"
            ]
            return random.choice(greetings)
        
        # Thank you response
        elif re.search(r'(thank|thanks)', query):
            responses = [
                "You're welcome! Is there anything else I can help you with?",
                "Happy to help! Let me know if you have any other questions.",
                "Anytime! What else would you like to know about your finances?",
                "My pleasure! Is there anything else you'd like to discuss?"
            ]
            return random.choice(responses)
        
        # Fallback response
        else:
            fallbacks = [
                "I'm not sure I understand. Could you rephrase your question?",
                "I don't have information on that yet. Is there something else I can help you with?",
                "I'm still learning! Could you ask me something about your spending, saving, or financial health?",
                "I don't have enough data to answer that question. Try asking about your balance, spending, or saving."
            ]
            return random.choice(fallbacks)
    
    # Display chat messages
    for message in st.session_state.financial_assistant_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your finances..."):
        # Add user message to chat history
        st.session_state.financial_assistant_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        response = generate_response(prompt, st.session_state.current_user)
        
        # Add assistant response to chat history
        st.session_state.financial_assistant_messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Financial insights section
    with st.expander("Financial Insights"):
        insights = generate_insights(st.session_state.current_user)
        
        if not insights:
            st.info("Continue using the app to generate personalized financial insights.")
        else:
            for insight in insights:
                st.info(insight)
    
    # Financial health score visualization
    with st.expander("Financial Health Score"):
        score = calculate_financial_health_score(st.session_state.current_user)
        
        # Create score gauge
        fig, ax = plt.subplots(figsize=(10, 2))
        
        # Score ranges
        poor = (0, 40)
        fair = (40, 60)
        good = (60, 80)
        excellent = (80, 100)
        
        # Create gauge segments
        ax.barh(0, poor[1] - poor[0], left=poor[0], height=0.5, color='#EA4335')
        ax.barh(0, fair[1] - fair[0], left=fair[0], height=0.5, color='#FBBC05')
        ax.barh(0, good[1] - good[0], left=good[0], height=0.5, color='#34A853')
        ax.barh(0, excellent[1] - excellent[0], left=excellent[0], height=0.5, color='#4285F4')
        
        # Add score marker
        ax.plot(score, 0, 'v', color='black', markersize=10)
        
        # Add labels
        ax.text(poor[0] + (poor[1] - poor[0])/2, -0.25, 'Poor', ha='center')
        ax.text(fair[0] + (fair[1] - fair[0])/2, -0.25, 'Fair', ha='center')
        ax.text(good[0] + (good[1] - good[0])/2, -0.25, 'Good', ha='center')
        ax.text(excellent[0] + (excellent[1] - excellent[0])/2, -0.25, 'Excellent', ha='center')
        
        # Add score text
        ax.text(score, 0.75, f'{score}', ha='center', fontweight='bold')
        
        # Configure plot
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 1)
        ax.set_yticks([])
        ax.set_xticks([0, 20, 40, 60, 80, 100])
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # Score interpretation
        if score >= 80:
            st.success("Excellent: You're managing your finances very well. Keep up the good work!")
        elif score >= 60:
            st.info("Good: You're on the right track with your finances. There's some room for improvement.")
        elif score >= 40:
            st.warning("Fair: Your financial health needs attention. Focus on building savings and reducing debt.")
        else:
            st.error("Poor: Your financial health needs significant improvement. Let's work on a plan to get back on track.")
    
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Check Balance", use_container_width=True):
            # Get user data
            users = load_users()
            user_data = users.get(st.session_state.current_user, {})
            balance = user_data.get('balance', 0)
            
            # Add assistant response to chat history
            response = f"Your current balance is ₹{balance:.2f}."
            st.session_state.financial_assistant_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("Monthly Spending", use_container_width=True):
            # Get monthly spending
            today = datetime.now().date()
            first_day = today.replace(day=1).strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')
            spending = get_total_spending(st.session_state.current_user, first_day, today_str)
            
            # Add assistant response to chat history
            response = f"You've spent ₹{spending:.2f} so far this month."
            st.session_state.financial_assistant_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("Financial Insights", use_container_width=True):
            # Generate insights
            insights = generate_insights(st.session_state.current_user)
            
            if not insights:
                response = "I don't have enough data to generate meaningful insights yet. Continue using the app for more personalized analysis."
            else:
                response = "Here are some insights based on your financial data:\n\n"
                for insight in insights[:3]:  # Limit to top 3 insights
                    response += f"- {insight}\n\n"
            
            # Add assistant response to chat history
            st.session_state.financial_assistant_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Back button
    if st.button("Back to Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()