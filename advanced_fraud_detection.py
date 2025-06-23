import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
# Fixed sklearn import
try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. ML features will be limited.")
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Try to import deep learning libraries (Python 3.11.9 Compatible)
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    # Suppress TensorFlow warnings
    tf.get_logger().setLevel('ERROR')
    import warnings
    warnings.filterwarnings('ignore', category=FutureWarning)
    TENSORFLOW_AVAILABLE = True
    print(f"✅ TensorFlow {tf.__version__} loaded successfully")
except ImportError as e:
    TENSORFLOW_AVAILABLE = False
    print(f"Warning: TensorFlow not available ({e}). Deep learning features will be limited.")
except Exception as e:
    TENSORFLOW_AVAILABLE = False
    print(f"Warning: TensorFlow error ({e}). Using basic ML models only.")

class AdvancedFraudDetector:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_path = 'data/fraud_models/'
        self.ensure_model_directory()
        
    def ensure_model_directory(self):
        """Ensure model directory exists"""
        os.makedirs(self.model_path, exist_ok=True)
        
    def load_transaction_data(self) -> pd.DataFrame:
        """Load and prepare transaction data for fraud detection"""
        try:
            # Load transactions from multiple sources
            transactions_file = 'data/transactions.json'
            payment_transactions_file = 'data/payment_transactions.json'
            
            transactions = []
            
            # Load regular transactions
            if os.path.exists(transactions_file):
                with open(transactions_file, 'r') as f:
                    regular_transactions = json.load(f)
                    transactions.extend(regular_transactions)
            
            # Load payment gateway transactions
            if os.path.exists(payment_transactions_file):
                with open(payment_transactions_file, 'r') as f:
                    payment_transactions = json.load(f)
                    transactions.extend(payment_transactions)
            
            if not transactions:
                # Generate synthetic data for demonstration
                return self.generate_synthetic_data()
            
            df = pd.DataFrame(transactions)
            return self.preprocess_transaction_data(df)
            
        except Exception as e:
            st.error(f"Error loading transaction data: {e}")
            return self.generate_synthetic_data()
    
    def generate_synthetic_data(self, n_samples: int = 10000) -> pd.DataFrame:
        """Generate synthetic transaction data for fraud detection training"""
        np.random.seed(42)
        
        # Generate normal transactions (90%)
        n_normal = int(n_samples * 0.9)
        normal_data = {
            'amount': np.random.lognormal(3, 1, n_normal),
            'hour': np.random.choice(range(6, 23), n_normal, p=self._get_hour_probabilities()),
            'day_of_week': np.random.choice(range(7), n_normal),
            'merchant_category': np.random.choice(['grocery', 'restaurant', 'gas', 'retail', 'online'], n_normal),
            'location_risk': np.random.beta(2, 8, n_normal),
            'user_age_days': np.random.normal(365, 200, n_normal),
            'avg_transaction_amount': np.random.lognormal(3, 0.5, n_normal),
            'transaction_frequency': np.random.poisson(5, n_normal),
            'is_weekend': np.random.choice([0, 1], n_normal, p=[0.7, 0.3]),
            'is_fraud': np.zeros(n_normal)
        }
        
        # Generate fraudulent transactions (10%)
        n_fraud = n_samples - n_normal
        fraud_data = {
            'amount': np.random.lognormal(4, 1.5, n_fraud),  # Higher amounts
            'hour': np.random.choice(range(24), n_fraud),  # Any time
            'day_of_week': np.random.choice(range(7), n_fraud),
            'merchant_category': np.random.choice(['online', 'atm', 'unknown'], n_fraud),
            'location_risk': np.random.beta(8, 2, n_fraud),  # Higher risk locations
            'user_age_days': np.random.normal(100, 50, n_fraud),  # Newer accounts
            'avg_transaction_amount': np.random.lognormal(2, 0.8, n_fraud),
            'transaction_frequency': np.random.poisson(15, n_fraud),  # Higher frequency
            'is_weekend': np.random.choice([0, 1], n_fraud, p=[0.5, 0.5]),
            'is_fraud': np.ones(n_fraud)
        }
        
        # Combine data
        all_data = {}
        for key in normal_data.keys():
            all_data[key] = np.concatenate([normal_data[key], fraud_data[key]])
        
        df = pd.DataFrame(all_data)
        
        # Add derived features
        df['amount_zscore'] = (df['amount'] - df['amount'].mean()) / df['amount'].std()
        df['is_high_amount'] = (df['amount'] > df['amount'].quantile(0.95)).astype(int)
        df['is_night_transaction'] = ((df['hour'] < 6) | (df['hour'] > 22)).astype(int)
        df['amount_vs_avg_ratio'] = df['amount'] / df['avg_transaction_amount']
        
        # Add timestamp
        base_time = datetime.now() - timedelta(days=30)
        df['timestamp'] = [base_time + timedelta(minutes=i*5) for i in range(len(df))]
        
        return df.sample(frac=1).reset_index(drop=True)  # Shuffle
    
    def _get_hour_probabilities(self) -> np.ndarray:
        """Get realistic hour probabilities for normal transactions"""
        # Higher probability during business hours
        probs = np.array([0.01, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0-5
                         0.05, 0.08, 0.10, 0.12, 0.10, 0.08,  # 6-11
                         0.06, 0.08, 0.10, 0.08, 0.06, 0.04,  # 12-17
                         0.03, 0.02, 0.02, 0.01, 0.01, 0.01])  # 18-23
        return probs / probs.sum()
    
    def preprocess_transaction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess transaction data for fraud detection"""
        # Convert timestamp if string
        if 'timestamp' in df.columns and df['timestamp'].dtype == 'object':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract time features
        if 'timestamp' in df.columns:
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col] = df[col].fillna('unknown')
        
        return df
    
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract advanced features for fraud detection"""
        feature_df = df.copy()
        
        # Amount-based features
        if 'amount' in feature_df.columns:
            feature_df['amount_log'] = np.log1p(feature_df['amount'])
            feature_df['amount_zscore'] = (feature_df['amount'] - feature_df['amount'].mean()) / feature_df['amount'].std()
            feature_df['is_high_amount'] = (feature_df['amount'] > feature_df['amount'].quantile(0.95)).astype(int)
        
        # Time-based features
        if 'hour' in feature_df.columns:
            feature_df['is_night_transaction'] = ((feature_df['hour'] < 6) | (feature_df['hour'] > 22)).astype(int)
            feature_df['is_business_hours'] = ((feature_df['hour'] >= 9) & (feature_df['hour'] <= 17)).astype(int)
        
        # User behavior features
        if 'user_id' in feature_df.columns or 'username' in feature_df.columns:
            user_col = 'user_id' if 'user_id' in feature_df.columns else 'username'
            
            # Transaction frequency
            user_stats = feature_df.groupby(user_col).agg({
                'amount': ['count', 'mean', 'std', 'min', 'max'],
                'timestamp': ['min', 'max'] if 'timestamp' in feature_df.columns else ['count']
            }).reset_index()
            
            user_stats.columns = [f'{col[0]}_{col[1]}' if col[1] else col[0] for col in user_stats.columns]
            feature_df = feature_df.merge(user_stats, on=user_col, how='left')
        
        # Velocity features (transactions in last hour/day)
        if 'timestamp' in feature_df.columns:
            feature_df = feature_df.sort_values('timestamp')
            feature_df['transactions_last_hour'] = 0
            feature_df['transactions_last_day'] = 0
            
            for i, row in feature_df.iterrows():
                current_time = row['timestamp']
                hour_ago = current_time - timedelta(hours=1)
                day_ago = current_time - timedelta(days=1)
                
                feature_df.loc[i, 'transactions_last_hour'] = len(
                    feature_df[(feature_df['timestamp'] >= hour_ago) & 
                              (feature_df['timestamp'] < current_time)]
                )
                feature_df.loc[i, 'transactions_last_day'] = len(
                    feature_df[(feature_df['timestamp'] >= day_ago) & 
                              (feature_df['timestamp'] < current_time)]
                )
        
        return feature_df
    
    def train_isolation_forest(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train Isolation Forest for anomaly detection"""
        # Select features for training
        feature_columns = ['amount', 'hour', 'day_of_week', 'is_weekend', 
                          'location_risk', 'transaction_frequency']
        
        # Filter available columns
        available_features = [col for col in feature_columns if col in df.columns]
        
        if not available_features:
            raise ValueError("No suitable features found for training")
        
        X = df[available_features].copy()
        
        # Handle categorical variables
        for col in X.columns:
            if X[col].dtype == 'object':
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    X[col] = self.encoders[col].fit_transform(X[col].astype(str))
                else:
                    X[col] = self.encoders[col].transform(X[col].astype(str))
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train Isolation Forest
        iso_forest = IsolationForest(
            contamination=0.1,  # Expected fraud rate
            random_state=42,
            n_estimators=100
        )
        
        iso_forest.fit(X_scaled)
        
        # Save model and scaler
        self.models['isolation_forest'] = iso_forest
        self.scalers['isolation_forest'] = scaler
        
        # Save to disk
        joblib.dump(iso_forest, os.path.join(self.model_path, 'isolation_forest.pkl'))
        joblib.dump(scaler, os.path.join(self.model_path, 'isolation_forest_scaler.pkl'))
        
        # Evaluate on training data
        anomaly_scores = iso_forest.decision_function(X_scaled)
        predictions = iso_forest.predict(X_scaled)
        
        return {
            'model': iso_forest,
            'scaler': scaler,
            'feature_columns': available_features,
            'anomaly_scores': anomaly_scores,
            'predictions': predictions
        }
    
    def train_random_forest(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train Random Forest classifier for fraud detection"""
        if 'is_fraud' not in df.columns:
            raise ValueError("Target variable 'is_fraud' not found in data")
        
        # Select features
        feature_columns = ['amount', 'hour', 'day_of_week', 'is_weekend',
                          'location_risk', 'transaction_frequency', 'amount_zscore']
        
        available_features = [col for col in feature_columns if col in df.columns]
        
        X = df[available_features].copy()
        y = df['is_fraud']
        
        # Handle categorical variables
        for col in X.columns:
            if X[col].dtype == 'object':
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    X[col] = self.encoders[col].fit_transform(X[col].astype(str))
                else:
                    X[col] = self.encoders[col].transform(X[col].astype(str))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = rf_model.score(X_train_scaled, y_train)
        test_score = rf_model.score(X_test_scaled, y_test)
        
        y_pred = rf_model.predict(X_test_scaled)
        y_pred_proba = rf_model.predict_proba(X_test_scaled)[:, 1]
        
        # Save model and scaler
        self.models['random_forest'] = rf_model
        self.scalers['random_forest'] = scaler
        
        joblib.dump(rf_model, os.path.join(self.model_path, 'random_forest.pkl'))
        joblib.dump(scaler, os.path.join(self.model_path, 'random_forest_scaler.pkl'))
        
        return {
            'model': rf_model,
            'scaler': scaler,
            'feature_columns': available_features,
            'train_score': train_score,
            'test_score': test_score,
            'predictions': y_pred,
            'probabilities': y_pred_proba,
            'feature_importance': dict(zip(available_features, rf_model.feature_importances_))
        }
    
    def train_deep_learning_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train deep learning model for fraud detection"""
        if not DEEP_LEARNING_AVAILABLE:
            raise ValueError("Deep learning libraries not available")
        
        if 'is_fraud' not in df.columns:
            raise ValueError("Target variable 'is_fraud' not found in data")
        
        # Prepare features
        feature_columns = ['amount', 'hour', 'day_of_week', 'is_weekend',
                          'location_risk', 'transaction_frequency', 'amount_zscore',
                          'is_high_amount', 'is_night_transaction']
        
        available_features = [col for col in feature_columns if col in df.columns]
        
        X = df[available_features].copy()
        y = df['is_fraud']
        
        # Handle categorical variables
        for col in X.columns:
            if X[col].dtype == 'object':
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    X[col] = self.encoders[col].fit_transform(X[col].astype(str))
                else:
                    X[col] = self.encoders[col].transform(X[col].astype(str))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Build neural network
        model = Sequential([
            Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(32, activation='relu'),
            Dropout(0.2),
            
            Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        # Train model
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        history = model.fit(
            X_train_scaled, y_train,
            epochs=100,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stopping],
            verbose=0
        )
        
        # Evaluate
        test_loss, test_accuracy, test_precision, test_recall = model.evaluate(
            X_test_scaled, y_test, verbose=0
        )
        
        y_pred_proba = model.predict(X_test_scaled).flatten()
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Save model and scaler
        self.models['deep_learning'] = model
        self.scalers['deep_learning'] = scaler
        
        model.save(os.path.join(self.model_path, 'deep_learning_model.h5'))
        joblib.dump(scaler, os.path.join(self.model_path, 'deep_learning_scaler.pkl'))
        
        return {
            'model': model,
            'scaler': scaler,
            'feature_columns': available_features,
            'history': history.history,
            'test_accuracy': test_accuracy,
            'test_precision': test_precision,
            'test_recall': test_recall,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
    
    def predict_fraud_probability(self, transaction_data: Dict[str, Any], 
                                 model_type: str = 'random_forest') -> Dict[str, Any]:
        """Predict fraud probability for a single transaction"""
        
        # Load model if not in memory
        if model_type not in self.models:
            self.load_model(model_type)
        
        model = self.models[model_type]
        scaler = self.scalers[model_type]
        
        # Prepare features
        feature_columns = ['amount', 'hour', 'day_of_week', 'is_weekend',
                          'location_risk', 'transaction_frequency']
        
        # Extract features from transaction data
        features = []
        for col in feature_columns:
            if col in transaction_data:
                features.append(transaction_data[col])
            else:
                # Use default values for missing features
                default_values = {
                    'amount': 100.0,
                    'hour': 12,
                    'day_of_week': 1,
                    'is_weekend': 0,
                    'location_risk': 0.1,
                    'transaction_frequency': 5
                }
                features.append(default_values.get(col, 0))
        
        # Scale features
        features_scaled = scaler.transform([features])
        
        # Make prediction
        if model_type == 'isolation_forest':
            anomaly_score = model.decision_function(features_scaled)[0]
            is_anomaly = model.predict(features_scaled)[0] == -1
            fraud_probability = max(0, min(1, (0.5 - anomaly_score) * 2))
        elif model_type == 'deep_learning' and DEEP_LEARNING_AVAILABLE:
            fraud_probability = model.predict(features_scaled)[0][0]
            is_anomaly = fraud_probability > 0.5
        else:  # random_forest
            fraud_probability = model.predict_proba(features_scaled)[0][1]
            is_anomaly = fraud_probability > 0.5
        
        # Determine risk level
        if fraud_probability > 0.8:
            risk_level = 'HIGH'
        elif fraud_probability > 0.5:
            risk_level = 'MEDIUM'
        elif fraud_probability > 0.2:
            risk_level = 'LOW'
        else:
            risk_level = 'VERY_LOW'
        
        return {
            'fraud_probability': float(fraud_probability),
            'is_suspicious': is_anomaly,
            'risk_level': risk_level,
            'model_used': model_type,
            'confidence': abs(fraud_probability - 0.5) * 2  # Distance from decision boundary
        }
    
    def load_model(self, model_type: str):
        """Load trained model from disk"""
        try:
            if model_type == 'deep_learning' and DEEP_LEARNING_AVAILABLE:
                model_path = os.path.join(self.model_path, 'deep_learning_model.h5')
                scaler_path = os.path.join(self.model_path, 'deep_learning_scaler.pkl')
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[model_type] = load_model(model_path)
                    self.scalers[model_type] = joblib.load(scaler_path)
            else:
                model_path = os.path.join(self.model_path, f'{model_type}.pkl')
                scaler_path = os.path.join(self.model_path, f'{model_type}_scaler.pkl')
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[model_type] = joblib.load(model_path)
                    self.scalers[model_type] = joblib.load(scaler_path)
        except Exception as e:
            st.error(f"Error loading {model_type} model: {e}")
    
    def get_fraud_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate fraud detection insights and statistics"""
        insights = {}
        
        if 'is_fraud' in df.columns:
            fraud_rate = df['is_fraud'].mean()
            insights['fraud_rate'] = fraud_rate
            insights['total_transactions'] = len(df)
            insights['fraud_transactions'] = df['is_fraud'].sum()
            
            # Fraud by time patterns
            if 'hour' in df.columns:
                fraud_by_hour = df.groupby('hour')['is_fraud'].agg(['count', 'sum', 'mean'])
                insights['fraud_by_hour'] = fraud_by_hour.to_dict()
            
            # Fraud by amount ranges
            if 'amount' in df.columns:
                df['amount_range'] = pd.cut(df['amount'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
                fraud_by_amount = df.groupby('amount_range')['is_fraud'].agg(['count', 'sum', 'mean'])
                insights['fraud_by_amount'] = fraud_by_amount.to_dict()
        
        return insights
    
    def create_fraud_visualizations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create visualizations for fraud detection analysis"""
        figs = {}
        
        if 'is_fraud' in df.columns:
            # Fraud distribution by hour
            if 'hour' in df.columns:
                fraud_by_hour = df.groupby(['hour', 'is_fraud']).size().unstack(fill_value=0)
                
                fig_hour = go.Figure()
                fig_hour.add_trace(go.Bar(
                    x=fraud_by_hour.index,
                    y=fraud_by_hour[0] if 0 in fraud_by_hour.columns else [],
                    name='Normal',
                    marker_color='lightblue'
                ))
                fig_hour.add_trace(go.Bar(
                    x=fraud_by_hour.index,
                    y=fraud_by_hour[1] if 1 in fraud_by_hour.columns else [],
                    name='Fraud',
                    marker_color='red'
                ))
                
                fig_hour.update_layout(
                    title='Transaction Distribution by Hour',
                    xaxis_title='Hour of Day',
                    yaxis_title='Number of Transactions',
                    barmode='stack'
                )
                
                figs['fraud_by_hour'] = fig_hour
            
            # Amount distribution
            if 'amount' in df.columns:
                fig_amount = px.histogram(
                    df, x='amount', color='is_fraud',
                    title='Transaction Amount Distribution',
                    nbins=50,
                    color_discrete_map={0: 'lightblue', 1: 'red'}
                )
                figs['amount_distribution'] = fig_amount
            
            # Correlation heatmap
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                
                fig_corr = px.imshow(
                    corr_matrix,
                    title='Feature Correlation Matrix',
                    color_continuous_scale='RdBu_r',
                    aspect='auto'
                )
                figs['correlation_matrix'] = fig_corr
        
        return figs

def real_time_fraud_monitoring(transaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Real-time fraud monitoring for incoming transactions"""
    detector = AdvancedFraudDetector()
    
    # Get fraud prediction
    prediction = detector.predict_fraud_probability(transaction_data)
    
    # Additional real-time checks
    alerts = []
    
    # High amount alert
    if transaction_data.get('amount', 0) > 10000:
        alerts.append({
            'type': 'HIGH_AMOUNT',
            'message': 'Transaction amount exceeds threshold',
            'severity': 'HIGH'
        })
    
    # Unusual time alert
    hour = transaction_data.get('hour', 12)
    if hour < 6 or hour > 22:
        alerts.append({
            'type': 'UNUSUAL_TIME',
            'message': 'Transaction at unusual hour',
            'severity': 'MEDIUM'
        })
    
    # High frequency alert
    frequency = transaction_data.get('transaction_frequency', 0)
    if frequency > 20:
        alerts.append({
            'type': 'HIGH_FREQUENCY',
            'message': 'High transaction frequency detected',
            'severity': 'HIGH'
        })
    
    return {
        'prediction': prediction,
        'alerts': alerts,
        'timestamp': datetime.now().isoformat(),
        'requires_review': prediction['fraud_probability'] > 0.7 or len(alerts) > 0
    }

def save_fraud_detection_result(transaction_id: str, result: Dict[str, Any]):
    """Save fraud detection result for audit trail"""
    results_file = 'data/fraud_detection_results.json'
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        results = []
    
    result_data = {
        'transaction_id': transaction_id,
        'timestamp': datetime.now().isoformat(),
        'fraud_probability': result['prediction']['fraud_probability'],
        'risk_level': result['prediction']['risk_level'],
        'alerts': result['alerts'],
        'requires_review': result['requires_review']
    }
    
    results.append(result_data)
    
    # Keep only last 10000 results
    results = results[-10000:]
    
    os.makedirs('data', exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

def get_fraud_statistics() -> Dict[str, Any]:
    """Get fraud detection statistics"""
    results_file = 'data/fraud_detection_results.json'
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'total_checks': 0, 'high_risk_transactions': 0, 'fraud_rate': 0}
    
    if not results:
        return {'total_checks': 0, 'high_risk_transactions': 0, 'fraud_rate': 0}
    
    df = pd.DataFrame(results)
    
    stats = {
        'total_checks': len(results),
        'high_risk_transactions': len(df[df['risk_level'] == 'HIGH']),
        'medium_risk_transactions': len(df[df['risk_level'] == 'MEDIUM']),
        'low_risk_transactions': len(df[df['risk_level'] == 'LOW']),
        'avg_fraud_probability': df['fraud_probability'].mean(),
        'transactions_requiring_review': len(df[df['requires_review'] == True]),
        'recent_checks': len(df[pd.to_datetime(df['timestamp']) > datetime.now() - timedelta(hours=24)])
    }
    
    return stats