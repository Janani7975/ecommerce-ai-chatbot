# 🛍️ AI-Powered eCommerce Chatbot

An intelligent eCommerce chatbot built using Python, NLP, and Machine Learning — similar to chatbots used by Zepto, Nykaa, and Flipkart.

## 🚀 Live Features
- 🤖 ML Intent Classification (LinearSVC + TF-IDF)
- 🔤 NLP Pipeline (NLTK — tokenization, stemming)
- 🎤 Voice Input Support
- 🔍 Real-time Search Suggestions
- 🌙 Dark Mode Toggle
- 🆚 Product Comparison in Chat
- 🇮🇳 Hindi Language Support
- 😊 Sentiment Detection
- 🧠 Conversation Memory
- 🔁 Related Product Suggestions
- 📱 Mobile Responsive UI
- 📦 Order Tracking
- 💳 Payment & EMI Information

## 🛠️ Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ML Algorithm | LinearSVC (SVM) |
| NLP | NLTK, TF-IDF Vectorizer |
| Database | SQLite3 |
| Frontend | HTML5, CSS3, JavaScript |
| Model Storage | Pickle (.pkl) |

## 📊 ML Model Performance
- Algorithm: Linear Support Vector Machine
- Training Data: 284 labeled sentences
- Intent Classes: 12
- Test Accuracy: 82.5%
- No paid API required

## ⚙️ Setup & Run

### 1. Clone repository
git clone https://github.com/Janani7975/ecommerce-ai-chatbot.git

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
| User Input | Bot Response |
|---|---|
| "show me phones" | Shows phone products with prices |
| "phones under 15000" | Price filtered results |
| "ORD-1001" | Live order status |
| "compare iPhone Samsung" | Side by side comparison |
| "mujhe laptop chahiye" | Hindi language support |
| "any discount coupons" | Current offers & codes |
| "terrible service" | Empathetic response |

## 📁 Project Structure
ecommerce-ai-chatbot/

├── app.py                 ← Flask web server

├── ai_engine.py           ← ML-powered response engine

├── setup_database.py      ← Database setup & seeding

├── requirements.txt       ← Python dependencies

├── ml_models/

│   ├── train_model.py     ← ML model training script

│   ├── training_data.py   ← 284 labeled training sentences

│   └── model.pkl          ← Trained model (auto-generated)

└── templates/

└── index.html         ← Chat UI
