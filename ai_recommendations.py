import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Try to import advanced ML libraries with error handling (Python 3.11.9 Compatible)
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    import joblib
    SKLEARN_AVAILABLE = True
    ML_AVAILABLE = True
    print("✅ Scikit-learn loaded successfully")
except ImportError as e:
    SKLEARN_AVAILABLE = False
    ML_AVAILABLE = False
    print(f"Warning: scikit-learn not available ({e}). AI recommendations will use basic analytics.")

# Try to import TensorFlow for advanced AI features
try:
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    TENSORFLOW_AVAILABLE = True
    print(f"✅ TensorFlow {tf.__version__} available for advanced AI")
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Info: TensorFlow not available. Using scikit-learn models only.")

class AIRecommendationEngine:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.user_profiles = {}
        self.spending_categories = [
            'Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities',
            'Entertainment', 'Health & Fitness', 'Travel', 'Education',
            'Groceries', 'Gas', 'ATM', 'Online', 'Other'
        ]
        
    def load_user_transactions(self, username: str) -> pd.DataFrame:
        """Load and process user transactions"""
        try:
            # Load transactions
            transactions_file = 'data/transactions.json'
            if os.path.exists(transactions_file):
                with open(transactions_file, 'r') as f:
                    all_transactions = json.load(f)
                
                # Filter user transactions
                user_transactions = [
                    t for t in all_transactions 
                    if t.get('username') == username or t.get('user_id') == username
                ]
                
                if user_transactions:
                    df = pd.DataFrame(user_transactions)
                    return self.preprocess_transactions(df)
            
            # Generate sample data if no transactions found
            return self.generate_sample_transactions(username)
            
        except Exception as e:
            st.error(f"Error loading transactions: {e}")
            return self.generate_sample_transactions(username)
    
    def generate_sample_transactions(self, username: str, n_transactions: int = 100) -> pd.DataFrame:
        """Generate sample transactions for demonstration"""
        np.random.seed(hash(username) % 2**32)
        
        # Generate realistic transaction data
        base_date = datetime.now() - timedelta(days=90)
        
        transactions = []
        for i in range(n_transactions):
            # Random date in last 90 days
            days_ago = np.random.randint(0, 90)
            transaction_date = base_date + timedelta(days=days_ago)
            
            # Category-based amount generation
            category = np.random.choice(self.spending_categories)
            
            if category in ['Food & Dining', 'Groceries']:
                amount = np.random.lognormal(3, 0.5)  # $20-200
            elif category in ['Shopping', 'Entertainment']:
                amount = np.random.lognormal(4, 0.8)  # $50-500
            elif category in ['Bills & Utilities', 'Transportation']:
                amount = np.random.lognormal(4.5, 0.3)  # $80-150
            elif category == 'Travel':
                amount = np.random.lognormal(6, 1)  # $400-4000
            else:
                amount = np.random.lognormal(3.5, 0.7)  # $30-300
            
            transactions.append({
                'username': username,
                'amount': round(amount, 2),
                'category': category,
                'timestamp': transaction_date.isoformat(),
                'description': f"{category} transaction",
                'type': 'debit'
            })
        
        return pd.DataFrame(transactions)
    
    def preprocess_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess transaction data"""
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract time features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Categorize transactions if not already categorized
        if 'category' not in df.columns:
            df['category'] = self.categorize_transactions(df)
        
        # Add derived features
        df['amount_log'] = np.log1p(df['amount'])
        
        return df.sort_values('timestamp')
    
    def categorize_transactions(self, df: pd.DataFrame) -> List[str]:
        """Auto-categorize transactions based on description"""
        categories = []
        
        for _, row in df.iterrows():
            description = str(row.get('description', '')).lower()
            
            if any(word in description for word in ['restaurant', 'food', 'cafe', 'pizza', 'burger']):
                categories.append('Food & Dining')
            elif any(word in description for word in ['grocery', 'supermarket', 'walmart', 'target']):
                categories.append('Groceries')
            elif any(word in description for word in ['gas', 'fuel', 'petrol', 'uber', 'taxi']):
                categories.append('Transportation')
            elif any(word in description for word in ['electric', 'water', 'internet', 'phone', 'bill']):
                categories.append('Bills & Utilities')
            elif any(word in description for word in ['movie', 'netflix', 'spotify', 'game']):
                categories.append('Entertainment')
            elif any(word in description for word in ['amazon', 'shop', 'store', 'mall']):
                categories.append('Shopping')
            elif any(word in description for word in ['hospital', 'doctor', 'pharmacy', 'gym']):
                categories.append('Health & Fitness')
            elif any(word in description for word in ['hotel', 'flight', 'travel', 'booking']):
                categories.append('Travel')
            elif any(word in description for word in ['school', 'course', 'book', 'education']):
                categories.append('Education')
            elif any(word in description for word in ['atm', 'cash']):
                categories.append('ATM')
            else:
                categories.append('Other')
        
        return categories
    
    def analyze_spending_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze user spending patterns"""
        analysis = {}
        
        # Basic statistics
        analysis['total_spent'] = df['amount'].sum()
        analysis['avg_transaction'] = df['amount'].mean()
        analysis['transaction_count'] = len(df)
        analysis['spending_days'] = df['timestamp'].dt.date.nunique()
        
        # Category analysis
        category_spending = df.groupby('category')['amount'].agg(['sum', 'mean', 'count'])
        analysis['category_breakdown'] = category_spending.to_dict()
        
        # Time-based patterns
        analysis['spending_by_hour'] = df.groupby('hour')['amount'].sum().to_dict()
        analysis['spending_by_day'] = df.groupby('day_of_week')['amount'].sum().to_dict()
        analysis['spending_by_month'] = df.groupby('month')['amount'].sum().to_dict()
        
        # Trends
        df['date'] = df['timestamp'].dt.date
        daily_spending = df.groupby('date')['amount'].sum()
        analysis['daily_trend'] = daily_spending.to_dict()
        
        # Weekly patterns
        analysis['weekend_vs_weekday'] = {
            'weekend': df[df['is_weekend'] == 1]['amount'].sum(),
            'weekday': df[df['is_weekend'] == 0]['amount'].sum()
        }
        
        return analysis
    
    def create_user_profile(self, username: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Create comprehensive user spending profile"""
        profile = {
            'username': username,
            'created_at': datetime.now().isoformat(),
            'analysis_period': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat(),
                'days': (df['timestamp'].max() - df['timestamp'].min()).days
            }
        }
        
        # Spending analysis
        spending_analysis = self.analyze_spending_patterns(df)
        profile['spending_analysis'] = spending_analysis
        
        # User behavior clustering
        profile['user_segment'] = self.classify_user_segment(spending_analysis)
        
        # Financial health score
        profile['financial_health_score'] = self.calculate_financial_health_score(spending_analysis)
        
        # Spending habits
        profile['spending_habits'] = self.identify_spending_habits(df)
        
        # Save profile
        self.user_profiles[username] = profile
        self.save_user_profile(username, profile)
        
        return profile
    
    def classify_user_segment(self, spending_analysis: Dict[str, Any]) -> str:
        """Classify user into spending segments"""
        avg_transaction = spending_analysis['avg_transaction']
        total_spent = spending_analysis['total_spent']
        transaction_count = spending_analysis['transaction_count']
        
        # Calculate spending frequency (transactions per day)
        spending_days = spending_analysis['spending_days']
        frequency = transaction_count / max(spending_days, 1)
        
        if avg_transaction > 500 and total_spent > 10000:
            return 'High Spender'
        elif frequency > 3 and avg_transaction < 100:
            return 'Frequent Small Spender'
        elif avg_transaction > 200 and frequency < 1:
            return 'Occasional Big Spender'
        elif total_spent < 1000:
            return 'Conservative Spender'
        else:
            return 'Moderate Spender'
    
    def calculate_financial_health_score(self, spending_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial health score (0-100)"""
        score = 100
        factors = []
        
        # Category diversity (good to have balanced spending)
        category_counts = len([v for v in spending_analysis['category_breakdown']['count'].values() if v > 0])
        if category_counts > 5:
            diversity_bonus = 10
            factors.append({'factor': 'Category Diversity', 'impact': diversity_bonus, 'description': 'Good spending diversity'})
        else:
            diversity_penalty = -5
            score += diversity_penalty
            factors.append({'factor': 'Limited Diversity', 'impact': diversity_penalty, 'description': 'Consider diversifying spending'})
        
        # Regular spending pattern (consistency is good)
        spending_days = spending_analysis['spending_days']
        transaction_count = spending_analysis['transaction_count']
        regularity = transaction_count / max(spending_days, 1)
        
        if 1 <= regularity <= 3:
            regularity_bonus = 15
            score += regularity_bonus
            factors.append({'factor': 'Regular Spending', 'impact': regularity_bonus, 'description': 'Consistent spending pattern'})
        elif regularity > 5:
            regularity_penalty = -10
            score += regularity_penalty
            factors.append({'factor': 'High Frequency', 'impact': regularity_penalty, 'description': 'Very frequent transactions'})
        
        # Weekend vs weekday balance
        weekend_ratio = spending_analysis['weekend_vs_weekday']['weekend'] / max(spending_analysis['total_spent'], 1)
        if 0.2 <= weekend_ratio <= 0.4:
            balance_bonus = 10
            score += balance_bonus
            factors.append({'factor': 'Work-Life Balance', 'impact': balance_bonus, 'description': 'Good weekend spending balance'})
        
        # Essential vs non-essential spending
        essential_categories = ['Groceries', 'Bills & Utilities', 'Transportation', 'Health & Fitness']
        essential_spending = sum([
            spending_analysis['category_breakdown']['sum'].get(cat, 0) 
            for cat in essential_categories
        ])
        essential_ratio = essential_spending / max(spending_analysis['total_spent'], 1)
        
        if essential_ratio > 0.6:
            essential_bonus = 20
            score += essential_bonus
            factors.append({'factor': 'Essential Focus', 'impact': essential_bonus, 'description': 'Good focus on essential spending'})
        elif essential_ratio < 0.3:
            essential_penalty = -15
            score += essential_penalty
            factors.append({'factor': 'High Discretionary', 'impact': essential_penalty, 'description': 'High discretionary spending'})
        
        return {
            'score': max(0, min(100, score)),
            'factors': factors,
            'grade': self.get_health_grade(score)
        }
    
    def get_health_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def identify_spending_habits(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify user spending habits and patterns"""
        habits = {}
        
        # Peak spending hours
        hourly_spending = df.groupby('hour')['amount'].sum()
        peak_hour = hourly_spending.idxmax()
        habits['peak_spending_hour'] = {
            'hour': peak_hour,
            'amount': hourly_spending[peak_hour],
            'description': self.get_hour_description(peak_hour)
        }
        
        # Favorite categories
        category_spending = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        habits['top_categories'] = category_spending.head(3).to_dict()
        
        # Spending streaks
        df['date'] = df['timestamp'].dt.date
        spending_dates = df['date'].unique()
        habits['spending_streak'] = self.calculate_spending_streak(spending_dates)
        
        # Average transaction by day of week
        dow_avg = df.groupby('day_of_week')['amount'].mean()
        habits['day_patterns'] = {
            'highest_avg_day': dow_avg.idxmax(),
            'lowest_avg_day': dow_avg.idxmin(),
            'weekend_preference': df[df['is_weekend'] == 1]['amount'].mean() > df[df['is_weekend'] == 0]['amount'].mean()
        }
        
        return habits
    
    def get_hour_description(self, hour: int) -> str:
        """Get description for spending hour"""
        if 6 <= hour < 12:
            return 'Morning spender'
        elif 12 <= hour < 17:
            return 'Afternoon spender'
        elif 17 <= hour < 22:
            return 'Evening spender'
        else:
            return 'Night owl spender'
    
    def calculate_spending_streak(self, spending_dates: np.ndarray) -> Dict[str, Any]:
        """Calculate longest spending streak"""
        if len(spending_dates) == 0:
            return {'longest_streak': 0, 'current_streak': 0}
        
        spending_dates = sorted(spending_dates)
        longest_streak = 1
        current_streak = 1
        
        for i in range(1, len(spending_dates)):
            if (spending_dates[i] - spending_dates[i-1]).days == 1:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        
        # Check if current streak is ongoing
        last_spending_date = spending_dates[-1]
        today = datetime.now().date()
        is_current_ongoing = (today - last_spending_date).days <= 1
        
        return {
            'longest_streak': longest_streak,
            'current_streak': current_streak if is_current_ongoing else 0
        }
    
    def generate_personalized_recommendations(self, username: str) -> List[Dict[str, Any]]:
        """Generate personalized spending recommendations"""
        # Load user profile
        profile = self.user_profiles.get(username)
        if not profile:
            df = self.load_user_transactions(username)
            profile = self.create_user_profile(username, df)
        
        recommendations = []
        spending_analysis = profile['spending_analysis']
        financial_health = profile['financial_health_score']
        habits = profile['spending_habits']
        
        # Budget recommendations
        recommendations.extend(self.get_budget_recommendations(spending_analysis))
        
        # Category-specific recommendations
        recommendations.extend(self.get_category_recommendations(spending_analysis))
        
        # Timing recommendations
        recommendations.extend(self.get_timing_recommendations(habits))
        
        # Financial health improvements
        recommendations.extend(self.get_health_improvement_recommendations(financial_health))
        
        # Savings opportunities
        recommendations.extend(self.get_savings_recommendations(spending_analysis))
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.get('priority', 5))
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def get_budget_recommendations(self, spending_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate budget-related recommendations"""
        recommendations = []
        
        total_spent = spending_analysis['total_spent']
        spending_days = spending_analysis['spending_days']
        daily_avg = total_spent / max(spending_days, 1)
        
        # Daily budget recommendation
        recommended_daily_budget = daily_avg * 0.9  # 10% reduction
        recommendations.append({
            'type': 'budget',
            'title': 'Set Daily Spending Limit',
            'description': f'Consider setting a daily budget of ${recommended_daily_budget:.2f} to reduce spending by 10%',
            'action': 'set_daily_budget',
            'value': recommended_daily_budget,
            'priority': 2,
            'potential_savings': daily_avg * 0.1 * 30  # Monthly savings
        })
        
        # Category budget recommendations
        category_spending = spending_analysis['category_breakdown']['sum']
        for category, amount in category_spending.items():
            if amount > total_spent * 0.3:  # If category is >30% of total spending
                recommendations.append({
                    'type': 'category_budget',
                    'title': f'Monitor {category} Spending',
                    'description': f'{category} represents a large portion of your spending. Consider setting a monthly limit.',
                    'action': 'set_category_budget',
                    'category': category,
                    'current_amount': amount,
                    'recommended_limit': amount * 0.85,
                    'priority': 3
                })
        
        return recommendations
    
    def get_category_recommendations(self, spending_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate category-specific recommendations"""
        recommendations = []
        
        category_spending = spending_analysis['category_breakdown']['sum']
        total_spent = spending_analysis['total_spent']
        
        # Food & Dining recommendations
        food_spending = category_spending.get('Food & Dining', 0)
        if food_spending > total_spent * 0.25:
            recommendations.append({
                'type': 'category_optimization',
                'title': 'Optimize Food Spending',
                'description': 'Consider meal planning and cooking at home to reduce dining expenses',
                'action': 'meal_planning',
                'category': 'Food & Dining',
                'current_spending': food_spending,
                'potential_savings': food_spending * 0.2,
                'priority': 2
            })
        
        # Shopping recommendations
        shopping_spending = category_spending.get('Shopping', 0)
        if shopping_spending > total_spent * 0.2:
            recommendations.append({
                'type': 'category_optimization',
                'title': 'Smart Shopping Strategy',
                'description': 'Use price comparison apps and wait for sales before making purchases',
                'action': 'smart_shopping',
                'category': 'Shopping',
                'current_spending': shopping_spending,
                'potential_savings': shopping_spending * 0.15,
                'priority': 3
            })
        
        # Entertainment recommendations
        entertainment_spending = category_spending.get('Entertainment', 0)
        if entertainment_spending > total_spent * 0.15:
            recommendations.append({
                'type': 'category_optimization',
                'title': 'Entertainment Budget',
                'description': 'Look for free or low-cost entertainment alternatives',
                'action': 'entertainment_alternatives',
                'category': 'Entertainment',
                'current_spending': entertainment_spending,
                'potential_savings': entertainment_spending * 0.25,
                'priority': 4
            })
        
        return recommendations
    
    def get_timing_recommendations(self, habits: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate timing-based recommendations"""
        recommendations = []
        
        # Peak spending hour recommendation
        peak_hour = habits['peak_spending_hour']['hour']
        if peak_hour in [22, 23, 0, 1, 2]:  # Late night spending
            recommendations.append({
                'type': 'timing',
                'title': 'Avoid Late Night Spending',
                'description': 'You tend to spend more late at night. Consider setting spending restrictions during these hours.',
                'action': 'set_time_restrictions',
                'peak_hour': peak_hour,
                'priority': 3
            })
        
        # Weekend spending pattern
        if habits['day_patterns']['weekend_preference']:
            recommendations.append({
                'type': 'timing',
                'title': 'Weekend Spending Awareness',
                'description': 'You spend more on weekends. Plan weekend activities in advance to control spending.',
                'action': 'weekend_planning',
                'priority': 4
            })
        
        return recommendations
    
    def get_health_improvement_recommendations(self, financial_health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations to improve financial health score"""
        recommendations = []
        
        for factor in financial_health['factors']:
            if factor['impact'] < 0:  # Negative impact factors
                if factor['factor'] == 'Limited Diversity':
                    recommendations.append({
                        'type': 'health_improvement',
                        'title': 'Diversify Your Spending',
                        'description': 'Try to balance your spending across different categories for better financial health',
                        'action': 'diversify_spending',
                        'priority': 3
                    })
                elif factor['factor'] == 'High Frequency':
                    recommendations.append({
                        'type': 'health_improvement',
                        'title': 'Reduce Transaction Frequency',
                        'description': 'Consider consolidating purchases to reduce impulse spending',
                        'action': 'consolidate_purchases',
                        'priority': 2
                    })
                elif factor['factor'] == 'High Discretionary':
                    recommendations.append({
                        'type': 'health_improvement',
                        'title': 'Focus on Essentials',
                        'description': 'Increase spending on essential categories like groceries and utilities',
                        'action': 'prioritize_essentials',
                        'priority': 1
                    })
        
        return recommendations
    
    def get_savings_recommendations(self, spending_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate savings opportunity recommendations"""
        recommendations = []
        
        total_spent = spending_analysis['total_spent']
        spending_days = spending_analysis['spending_days']
        monthly_spending = total_spent * (30 / max(spending_days, 1))
        
        # Automatic savings recommendation
        recommended_savings = monthly_spending * 0.1  # 10% of monthly spending
        recommendations.append({
            'type': 'savings',
            'title': 'Set Up Automatic Savings',
            'description': f'Save ${recommended_savings:.2f} monthly by setting up automatic transfers',
            'action': 'setup_auto_savings',
            'amount': recommended_savings,
            'priority': 2
        })
        
        # Round-up savings
        avg_transaction = spending_analysis['avg_transaction']
        estimated_roundup = spending_analysis['transaction_count'] * 0.5  # Average 50 cents per transaction
        recommendations.append({
            'type': 'savings',
            'title': 'Enable Round-up Savings',
            'description': f'Save approximately ${estimated_roundup:.2f} monthly by rounding up transactions',
            'action': 'enable_roundup',
            'estimated_savings': estimated_roundup,
            'priority': 4
        })
        
        return recommendations
    
    def save_user_profile(self, username: str, profile: Dict[str, Any]):
        """Save user profile to file"""
        profiles_dir = 'data/user_profiles'
        os.makedirs(profiles_dir, exist_ok=True)
        
        profile_file = os.path.join(profiles_dir, f'{username}_profile.json')
        with open(profile_file, 'w') as f:
            json.dump(profile, f, indent=2, default=str)
    
    def load_user_profile(self, username: str) -> Dict[str, Any]:
        """Load user profile from file"""
        profiles_dir = 'data/user_profiles'
        profile_file = os.path.join(profiles_dir, f'{username}_profile.json')
        
        try:
            with open(profile_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def create_spending_visualizations(self, username: str) -> Dict[str, Any]:
        """Create visualizations for spending analysis"""
        df = self.load_user_transactions(username)
        figs = {}
        
        # Category spending pie chart
        category_spending = df.groupby('category')['amount'].sum()
        fig_pie = px.pie(
            values=category_spending.values,
            names=category_spending.index,
            title='Spending by Category'
        )
        figs['category_pie'] = fig_pie
        
        # Daily spending trend
        df['date'] = df['timestamp'].dt.date
        daily_spending = df.groupby('date')['amount'].sum().reset_index()
        fig_trend = px.line(
            daily_spending, x='date', y='amount',
            title='Daily Spending Trend'
        )
        figs['daily_trend'] = fig_trend
        
        # Hourly spending pattern
        hourly_spending = df.groupby('hour')['amount'].sum().reset_index()
        fig_hourly = px.bar(
            hourly_spending, x='hour', y='amount',
            title='Spending by Hour of Day'
        )
        figs['hourly_pattern'] = fig_hourly
        
        # Monthly comparison
        df['month_year'] = df['timestamp'].dt.to_period('M')
        monthly_spending = df.groupby('month_year')['amount'].sum().reset_index()
        monthly_spending['month_year'] = monthly_spending['month_year'].astype(str)
        fig_monthly = px.bar(
            monthly_spending, x='month_year', y='amount',
            title='Monthly Spending Comparison'
        )
        figs['monthly_comparison'] = fig_monthly
        
        return figs
    
    def predict_future_spending(self, username: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict future spending patterns"""
        df = self.load_user_transactions(username)
        
        if len(df) < 10:
            return {'error': 'Insufficient data for prediction'}
        
        # Prepare data for prediction
        df['date'] = df['timestamp'].dt.date
        daily_spending = df.groupby('date')['amount'].sum().reset_index()
        daily_spending['days_since_start'] = (daily_spending['date'] - daily_spending['date'].min()).dt.days
        
        # Simple linear regression for trend
        if ML_AVAILABLE and SKLEARN_AVAILABLE:
            X = daily_spending[['days_since_start']]
            y = daily_spending['amount']
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict future days
            future_days = np.arange(
                daily_spending['days_since_start'].max() + 1,
                daily_spending['days_since_start'].max() + days_ahead + 1
            ).reshape(-1, 1)
            
            predictions = model.predict(future_days)
            
            # Calculate confidence intervals (simplified)
            residuals = y - model.predict(X)
            std_error = np.std(residuals)
            
            return {
                'predictions': predictions.tolist(),
                'confidence_interval': std_error * 1.96,  # 95% confidence
                'trend': 'increasing' if model.coef_[0] > 0 else 'decreasing',
                'daily_average': predictions.mean(),
                'monthly_estimate': predictions.sum() * (30 / days_ahead)
            }
        else:
            # Simple average-based prediction
            avg_daily = daily_spending['amount'].mean()
            return {
                'predictions': [avg_daily] * days_ahead,
                'trend': 'stable',
                'daily_average': avg_daily,
                'monthly_estimate': avg_daily * 30
            }

def get_spending_insights(username: str) -> Dict[str, Any]:
    """Get comprehensive spending insights for a user"""
    engine = AIRecommendationEngine()
    
    # Load transactions and create profile
    df = engine.load_user_transactions(username)
    profile = engine.create_user_profile(username, df)
    
    # Generate recommendations
    recommendations = engine.generate_personalized_recommendations(username)
    
    # Create visualizations
    visualizations = engine.create_spending_visualizations(username)
    
    # Predict future spending
    predictions = engine.predict_future_spending(username)
    
    return {
        'profile': profile,
        'recommendations': recommendations,
        'visualizations': visualizations,
        'predictions': predictions
    }

def save_user_feedback(username: str, recommendation_id: str, feedback: str, rating: int):
    """Save user feedback on recommendations"""
    feedback_data = {
        'username': username,
        'recommendation_id': recommendation_id,
        'feedback': feedback,
        'rating': rating,
        'timestamp': datetime.now().isoformat()
    }
    
    feedback_file = 'data/recommendation_feedback.json'
    try:
        with open(feedback_file, 'r') as f:
            feedbacks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        feedbacks = []
    
    feedbacks.append(feedback_data)
    
    os.makedirs('data', exist_ok=True)
    with open(feedback_file, 'w') as f:
        json.dump(feedbacks, f, indent=2)

def get_recommendation_effectiveness() -> Dict[str, Any]:
    """Analyze recommendation effectiveness based on user feedback"""
    feedback_file = 'data/recommendation_feedback.json'
    
    try:
        with open(feedback_file, 'r') as f:
            feedbacks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'total_feedback': 0, 'average_rating': 0}
    
    if not feedbacks:
        return {'total_feedback': 0, 'average_rating': 0}
    
    df = pd.DataFrame(feedbacks)
    
    return {
        'total_feedback': len(feedbacks),
        'average_rating': df['rating'].mean(),
        'rating_distribution': df['rating'].value_counts().to_dict(),
        'recent_feedback': len(df[pd.to_datetime(df['timestamp']) > datetime.now() - timedelta(days=7)])
    }