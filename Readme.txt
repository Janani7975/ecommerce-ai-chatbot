# 🛍️ AI-Powered eCommerce Chatbot

An intelligent eCommerce chatbot built using Python, NLP, and Machine Learning.

## 🚀 Features
- 🤖 ML Intent Classification (LinearSVC + TF-IDF)
- 🔤 NLP Pipeline (NLTK - tokenization, stemming)
- 🎤 Voice Input Support
- 🔍 Real-time Search Suggestions
- 🌙 Dark Mode
- 🆚 Product Comparison
- 🇮🇳 Hindi Language Support
- 😊 Sentiment Detection
- 📱 Mobile Responsive

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **ML:** scikit-learn (LinearSVC)
- **NLP:** NLTK (TF-IDF Vectorizer)
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, JavaScript

## 📊 Model Performance
- Algorithm: Linear Support Vector Machine
- Training Data: 284 labeled sentences
- Intent Classes: 12
- Accuracy: 82.5%

## ⚙️ Setup & Run

### 1. Clone repository
git clone https://github.com/YourUsername/ecommerce-ai-chatbot.git
cd ecommerce-ai-chatbot

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Train ML model
cd ml_models
python train_model.py
cd ..

### 5. Run the application
python app.py

### 6. Open browser
http://127.0.0.1:5000

## 💬 Sample Conversations
- "show me phones" → Shows phone products
- "phones under 15000" → Price filtered results
- "ORD-1001" → Order tracking
- "compare iPhone Samsung" → Side by side comparison
- "mujhe laptop chahiye" → Hindi support
- "any discount coupons" → Shows offers

## 📁 Project Structure
AI-Chatbot/
├── app.py
├── ai_engine.py
├── setup_database.py
├── database.py
├── shop.db
├── requirements.txt
├── ml_models/
│   ├── train_model.py
│   ├── training_data.py
│   └── model.pkl
└── templates/
    └── index.html
