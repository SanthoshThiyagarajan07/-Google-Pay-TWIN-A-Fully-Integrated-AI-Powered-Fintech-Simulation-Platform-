# 🚀 Google Pay TWIN - Advanced Digital Payment Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](#license)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](#ai-powered-features)

A comprehensive digital payment platform built with **Streamlit**, featuring advanced **AI-powered recommendations**, **fraud detection**, **payment gateway integration**, and **enhanced security features**. This project demonstrates modern fintech capabilities with a focus on user experience and cutting-edge technology integration.

## ✨ Key Highlights

- 🤖 **AI-Powered Financial Intelligence** - Machine learning for fraud detection, expense prediction, and personalized recommendations
- 🔐 **Multi-Layer Security** - OAuth, OTP, JWT tokens, and advanced session management
- 🎤 **Voice-Enabled Payments** - Hands-free transaction processing with speech recognition
- 📊 **Advanced Analytics** - Real-time insights, spending heatmaps, and financial health scoring
- 💳 **Complete Payment Ecosystem** - QR codes, bill splitting, subscriptions, and investment tracking
- 🌐 **Modern UI/UX** - Responsive design with interactive visualizations

## 🚀 Features

### 🔐 Authentication & Security
- **Multi-Method Authentication**: Username/Password, Phone OTP, and Google OAuth 2.0
- **OTP Verification**: SMS-based OTP system with mock Twilio integration
- **Google OAuth Integration**: Seamless sign-in with Google accounts
- **Advanced Session Management**: Automatic timeout, security monitoring, and JWT tokens
- **Account Protection**: Login attempt tracking, account lockout, and fraud prevention
- **Data Encryption**: Secure password hashing with bcrypt and cryptographic protection

### 💰 Core Payment Features
- **Send Money**: Instant transfers to registered users with real-time validation
- **Add Money**: Secure fund addition with multiple payment gateway simulation
- **QR Code Payments**: Generate and scan QR codes for contactless transactions
- **Voice Payments**: AI-powered voice command processing for hands-free payments
- **Contactless Payments**: Mock UPI flow with enhanced security protocols
- **Payment History**: Comprehensive transaction tracking with advanced filtering

### 📊 Financial Management
- **Smart Budget Alerts**: AI-driven spending limit notifications with category analysis
- **Savings Goals**: Goal creation, progress tracking, and achievement rewards
- **Subscription Management**: Automated tracking of recurring payments and renewals
- **Bill Splitting**: Advanced bill division with friend networks and payment tracking
- **Pay Later**: Credit scoring system with buy-now-pay-later functionality
- **Expense Categories**: Intelligent transaction categorization and analysis

### 🤖 AI-Powered Features
- **Expense Prediction**: Machine learning models for spending forecasts using Random Forest
- **Fraud Detection**: Real-time anomaly detection with Isolation Forest algorithms
- **Financial Assistant**: Conversational AI providing personalized financial advice
- **Emotion-Aware Insights**: Transaction analysis based on spending behavior patterns
- **Smart Recommendations**: Personalized suggestions for savings, investments, and spending
- **Risk Assessment**: Dynamic transaction risk scoring with ML-based evaluation

### 📈 Analytics & Insights
- **Financial Health Score**: Comprehensive wellness assessment with actionable insights
- **Spending Heatmaps**: Interactive calendar-based visualization of spending patterns
- **Investment Portfolio**: Real-time tracking of investment performance and returns
- **Cashback System**: Reward points calculation and redemption tracking
- **Spending Challenges**: Gamified financial goals with progress monitoring
- **Trend Analysis**: Historical data analysis with predictive modeling

### 🔍 Advanced Features
- **Receipt OCR Scanner**: AI-powered text extraction from receipt images using Tesseract
- **Real-time Analytics**: Live dashboard with spending pattern analysis
- **Multi-Currency Support**: International transaction handling and conversion
- **Recurring Payments**: Automated payment scheduling and management
- **Financial Reports**: Detailed monthly/yearly financial summaries
- **Data Export**: CSV/PDF export functionality for financial records

## 🛠️ Technology Stack

### Frontend & UI Framework
- **Streamlit 1.28+**: Modern web interface with real-time interactivity
- **Streamlit-Option-Menu**: Enhanced navigation with custom styling
- **Streamlit-Extras**: Advanced UI components and widgets
- **Plotly**: Interactive 3D charts and dynamic visualizations
- **Matplotlib & Seaborn**: Statistical plotting and data visualization
- **Streamlit-WebRTC**: Real-time audio/video processing capabilities

### Authentication & Security Stack
- **Google OAuth 2.0**: Secure third-party authentication
- **PyJWT**: JSON Web Token implementation for session management
- **Cryptography**: Advanced encryption and secure password hashing
- **Passlib & Bcrypt**: Password security and hashing algorithms
- **PyOTP**: Time-based one-time password generation
- **Twilio API**: SMS OTP delivery (mock implementation)

### Data Processing & Machine Learning
- **Pandas & NumPy**: High-performance data manipulation and analysis
- **Scikit-learn**: ML algorithms (Isolation Forest, Random Forest, SVM)
- **Joblib**: Model serialization and parallel processing
- **Python-dateutil**: Advanced date/time processing
- **JSONSchema**: Data validation and schema enforcement

### Image Processing & OCR
- **PIL (Pillow)**: Image processing and manipulation
- **OpenCV-Python**: Computer vision and image analysis
- **Pytesseract**: Optical Character Recognition for receipt scanning
- **QRCode[PIL]**: QR code generation with PIL integration

### Voice & Audio Processing
- **PyAudio**: Low-level audio I/O for microphone input
- **SpeechRecognition**: Voice command processing and speech-to-text
- **pyttsx3**: Text-to-speech synthesis for voice feedback
- **Advanced Voice Commands**: Natural language processing for payment instructions

### Payment & Integration APIs
- **Stripe**: Payment processing integration (demo mode)
- **Razorpay**: Indian payment gateway simulation
- **PayPal REST SDK**: PayPal payment integration
- **Requests**: HTTP client for API communications

### System & Utilities
- **Python 3.8+**: Core programming language with modern features
- **APScheduler**: Advanced task scheduling and automation
- **Python-dotenv**: Environment variable management
- **Psutil**: System monitoring and resource tracking
- **Watchdog**: File system event monitoring
- **PyTZ**: Timezone handling and date localization

## 📦 Installation & Setup

### 📋 Prerequisites
- **Python 3.8 or higher** (Python 3.11+ recommended)
- **pip** (Python package installer)
- **Git** (for repository cloning)
- **Microphone** (for voice payment features)
- **Camera** (optional, for QR code scanning)

### 🚀 Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/google-pay-twin.git
   cd google-pay-twin
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   **⚠️ PyAudio Installation**: If PyAudio fails to install:
   - **Windows**: Run `install_pyaudio.bat` or see [PyAudio Guide](PYAUDIO_INSTALL_GUIDE.md)
   - **macOS**: `brew install portaudio && pip install PyAudio`
   - **Linux**: Install system dependencies (see [detailed guide](PYAUDIO_INSTALL_GUIDE.md))

4. **Setup Tesseract OCR** (For Receipt Scanning)
   - **Windows**: Download from [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **CentOS/RHEL**: `sudo yum install tesseract`

5. **Configure Google OAuth** (Optional)
   - Create project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google+ API and create OAuth 2.0 credentials
   - Update `auth_page.py` with your client ID and secret

6. **Fix Python 3.13 Compatibility** (If needed)
   ```bash
   # Windows
   fix_calmap.bat
   
   # All platforms
   python fix_calmap.py
   ```

7. **Launch the Application**
   ```bash
   streamlit run app.py
   ```
   
   The application will open in your default browser at `http://localhost:8501`

### 🔧 Alternative Installation Methods

#### Using Batch Scripts (Windows)
```bash
# Complete installation and launch
install_and_run.bat

# Install requirements only
install_requirements.bat

# Fix specific issues
fix_python_windows11.bat
fix_rerun.bat
```

#### Using PowerShell (Windows)
```powershell
# Run installation script
.\install_requirements.ps1

# Launch application
.\run_app.ps1
```

## 🎯 Usage Guide

### 🔑 Getting Started

1. **Choose Authentication Method**:
   - **Traditional**: Register with username/password
   - **Phone**: SMS OTP verification (mock implementation)
   - **Google**: One-click OAuth sign-in

2. **Initial Setup**:
   - Complete profile information
   - Set security preferences
   - Start with ₹1000 demo balance
   - Enable voice features (optional)

### 💳 Core Payment Operations

3. **Making Payments**:
   - **Send Money**: Enter recipient and amount
   - **QR Payments**: Generate/scan QR codes
   - **Voice Commands**: "Send 100 rupees to John"
   - **Bill Splitting**: Divide expenses with groups

4. **Financial Management**:
   - **Budget Setup**: Set category-wise spending limits
   - **Savings Goals**: Create and track financial targets
   - **Subscriptions**: Monitor recurring payments
   - **Investment Tracking**: Add portfolio holdings

### 📊 Analytics & Insights

5. **Dashboard Features**:
   - **Transaction History**: Filter and search payments
   - **Spending Analysis**: Category-wise breakdowns
   - **Financial Health**: Comprehensive scoring system
   - **Trend Visualization**: Interactive charts and graphs

6. **AI-Powered Tools**:
   - **Expense Prediction**: ML-based spending forecasts
   - **Fraud Detection**: Real-time security monitoring
   - **Financial Assistant**: Personalized advice chat
   - **Smart Alerts**: Proactive spending notifications

### 🎤 Voice Features

7. **Voice Commands**:
   - "Send money to [contact]"
   - "Check my balance"
   - "Show recent transactions"
   - "Set budget alert for groceries"

## 🔧 Troubleshooting

### 🚨 Common Issues & Solutions

#### 1. **PyAudio Installation Error**
```bash
# Error: Could not find PyAudio or installation fails

# Solutions:
# Windows: Install Visual C++ Build Tools
install_pyaudio.bat

# macOS: Install portaudio
brew install portaudio
pip install PyAudio

# Linux: Install system dependencies
# Ubuntu/Debian:
sudo apt-get install python3-dev portaudio19-dev
# CentOS/RHEL:
sudo yum install python3-devel portaudio-devel

# Alternative: Use conda
conda install pyaudio

# Fallback: Disable voice features
# Comment out PyAudio in requirements.txt
```

#### 2. **Calmap Installation Error (Python 3.13)**
```bash
# Error: calmap not found or distutils issues

# Solution:
fix_calmap.bat  # Windows
python fix_calmap.py  # All platforms

# Manual fix:
pip install --upgrade setuptools wheel
pip install calmap --no-deps
```

#### 3. **Tesseract OCR Not Found**
```bash
# Error: Receipt scanning doesn't work

# Solutions:
# Windows: Add to PATH after installation
set PATH=%PATH%;C:\Program Files\Tesseract-OCR

# Verify installation:
tesseract --version

# Alternative: Update tesseract path in code
```

#### 4. **Google OAuth Issues**
```bash
# Error: Google sign-in not working

# Solutions:
# 1. Check Google Cloud Console configuration
# 2. Verify OAuth 2.0 credentials
# 3. Ensure correct redirect URIs
# 4. Enable Google+ API
```

#### 5. **Streamlit Experimental Rerun Warning**
```bash
# Warning: st.experimental_rerun is deprecated

# Solution:
fix_experimental_rerun.py
# Or run:
fix_rerun.bat  # Windows
```

#### 6. **Voice Recognition Issues**
```bash
# Error: Voice payments not responding

# Solutions:
# 1. Check microphone permissions
# 2. Ensure PyAudio is installed correctly
# 3. Test microphone with other applications
# 4. Speak clearly and close to microphone
# 5. Check system audio settings
```

### 📚 Additional Resources

- **[PyAudio Installation Guide](PYAUDIO_INSTALL_GUIDE.md)** - Comprehensive PyAudio setup
- **[Installation Guide](INSTALL_GUIDE.md)** - Detailed installation instructions
- **[Quick Start Guide](QUICK_START.md)** - Fast setup for experienced users
- **[Python 3.13 Compatibility](PYTHON_3_13_COMPATIBILITY.md)** - Version-specific fixes
- **[Fixes Applied](FIXES_APPLIED.md)** - Complete list of bug fixes

## 📁 Project Structure

```
google-pay-twin/
├── 📄 Core Application
│   ├── app.py                          # Main Streamlit application
│   ├── launcher.py                     # Application launcher
│   └── stream_app.py                   # Alternative entry point
│
├── 🔐 Authentication & Security
│   ├── auth_page.py                    # Multi-method authentication
│   ├── security.py                     # Security utilities
│   └── payment_gateway.py              # Payment processing
│
├── 💰 Payment Features
│   ├── voice_pay_page.py               # Voice-enabled payments
│   ├── qr_code_page.py                 # QR code generation/scanning
│   ├── bill_split_page.py              # Bill splitting functionality
│   ├── pay_later_page.py               # Credit and pay-later features
│   └── recurring_payments_page.py      # Subscription management
│
├── 📊 Financial Management
│   ├── savings_goals_page.py           # Savings tracking
│   ├── budget_alerts_page.py           # Budget monitoring
│   ├── investment_tracker_page.py      # Portfolio management
│   ├── subscriptions_page.py           # Recurring payments
│   └── cashback_page.py                # Rewards system
│
├── 🤖 AI & Analytics
│   ├── ai_recommendations_page.py      # ML-powered suggestions
│   ├── fraud_detection_page.py         # Anomaly detection
│   ├── expense_prediction_page.py      # Spending forecasts
│   ├── financial_assistant_page.py     # AI chat assistant
│   ├── financial_health_page.py        # Health scoring
│   ├── emotion_insights_page.py        # Behavioral analysis
│   └── spending_heatmap_page.py        # Visual analytics
│
├── 🔍 Advanced Features
│   ├── scan_receipt_page.py            # OCR receipt processing
│   ├── spending_challenge_page.py      # Gamified goals
│   ├── advanced_fraud_detection.py     # Enhanced security
│   └── recurring_payments.py           # Payment automation
│
├── 📊 Data Storage
│   └── data/
│       ├── users.json                  # User accounts
│       ├── transactions.json           # Transaction history
│       ├── savings_goals.json          # Savings data
│       ├── subscriptions.json          # Recurring payments
│       ├── bill_splits.json            # Bill splitting records
│       ├── emotions.json               # Behavioral data
│       ├── investments.json            # Portfolio data
│       └── cashbacks.json              # Rewards tracking
│
├── 🛠️ Installation & Setup
│   ├── requirements.txt                # Python dependencies
│   ├── install_pyaudio.bat            # PyAudio installer (Windows)
│   ├── install_requirements.bat       # Dependency installer
│   ├── install_and_run.bat            # Complete setup script
│   ├── fix_calmap.py                  # Python 3.13 compatibility
│   ├── fix_calmap.bat                 # Calmap fix (Windows)
│   └── run_app.ps1                    # PowerShell launcher
│
└── 📚 Documentation
    ├── README.md                       # This file
    ├── PYAUDIO_INSTALL_GUIDE.md       # PyAudio setup guide
    ├── INSTALL_GUIDE.md               # Installation instructions
    ├── QUICK_START.md                 # Quick setup guide
    ├── PYTHON_3_13_COMPATIBILITY.md   # Version compatibility
    ├── FIXES_APPLIED.md               # Bug fix documentation
    └── RUN_WITHOUT_VENV.md            # Non-virtual environment setup
```

## 🚀 Future Enhancements

### 🔮 Planned Features
- **Blockchain Integration**: Cryptocurrency payment support
- **Biometric Authentication**: Fingerprint and face recognition
- **Real Payment Gateways**: Live Stripe, PayPal, and Razorpay integration
- **Mobile App**: React Native companion application
- **Advanced AI**: Deep learning for enhanced fraud detection
- **Multi-language Support**: Internationalization and localization
- **API Development**: RESTful API for third-party integrations
- **Cloud Deployment**: AWS/Azure hosting with scalability

### 🎯 Technical Roadmap
- **Database Migration**: PostgreSQL/MongoDB integration
- **Microservices Architecture**: Service-oriented design
- **Real-time Notifications**: WebSocket-based alerts
- **Advanced Analytics**: Business intelligence dashboard
- **Security Enhancements**: End-to-end encryption
- **Performance Optimization**: Caching and load balancing

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### 📝 Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed
- Ensure cross-platform compatibility

## 📄 License

This project is licensed under the **Educational License** - see the [LICENSE](LICENSE) file for details.

**Educational Use Only**: This project is designed for learning and demonstration purposes.

## ⚠️ Important Disclaimer

**🚨 DEMO APPLICATION NOTICE 🚨**

This is a **demonstration project** and **NOT intended for actual financial transactions**:

- ❌ **No Real Money**: All transactions are simulated
- ❌ **No Real Banks**: No connection to actual banking systems
- ❌ **No Real Payments**: Payment gateways are in demo/test mode
- ❌ **Educational Only**: Designed for learning and portfolio demonstration
- ✅ **Safe to Use**: No financial risk or real money involved

**Security Note**: While this application implements security best practices, it should not be used as a reference for production financial applications without proper security auditing.

## 🙏 Acknowledgments

- **Streamlit Team** for the amazing framework
- **Scikit-learn** for machine learning capabilities
- **Google** for OAuth integration
- **Open Source Community** for various libraries and tools
- **Contributors** who helped improve this project

## 📞 Support & Contact

For questions, issues, or suggestions:

- 📧 **Email**: [your-email@example.com]
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/google-pay-twin/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/google-pay-twin/discussions)
- 📱 **LinkedIn**: [Your LinkedIn Profile]

---

<div align="center">

**⭐ Star this repository if you found it helpful! ⭐**

**Perfect for showcasing modern fintech development skills on LinkedIn! 🚀💼**

[![GitHub stars](https://img.shields.io/github/stars/your-username/google-pay-twin.svg?style=social&label=Star)](https://github.com/your-username/google-pay-twin)
[![GitHub forks](https://img.shields.io/github/forks/your-username/google-pay-twin.svg?style=social&label=Fork)](https://github.com/your-username/google-pay-twin/fork)

</div>

---

*Last Updated: December 2024 | Version 2.0 | Built with ❤️ and Python*