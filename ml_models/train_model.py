"""
train_model.py — The REAL AI/ML part of this project

What this does:
1. Takes 300+ labeled sentences (training data)
2. Preprocesses text (tokenize, stem, clean)
3. Converts text to numerical features (TF-IDF)
4. Trains a machine learning classifier (SVM)
5. Evaluates accuracy
6. Saves trained model as model.pkl

This is genuine Machine Learning — not rule-based!
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pickle
import re
import string
import numpy as np

# ML Libraries
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

# NLP Libraries
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
print("📥 Downloading NLP resources...")
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

from training_data import TRAINING_DATA, INTENTS

# ── NLP PREPROCESSOR ──────────────────────────────────
stemmer = PorterStemmer()

def preprocess(text):
    """
    Full NLP pipeline:
    1. Lowercase
    2. Remove punctuation & special chars
    3. Tokenize (split into words)
    4. Remove stopwords
    5. Stem words (running→run, phones→phone)
    """
    # 1. Lowercase
    text = text.lower().strip()

    # 2. Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', 'NUM', text)  # replace numbers with NUM token

    # 3. Tokenize
    try:
        tokens = word_tokenize(text)
    except:
        tokens = text.split()

    # 4. Remove stopwords (keep domain-specific words)
    keep_words = {'under', 'below', 'above', 'not', 'no', 'free', 'best',
                  'cheap', 'new', 'good', 'bad', 'how', 'what', 'where',
                  'when', 'which', 'why', 'can', 'want', 'need'}
    try:
        stop_words = set(stopwords.words('english')) - keep_words
    except:
        stop_words = set()

    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]

    # 5. Stemming
    tokens = [stemmer.stem(t) for t in tokens]

    return ' '.join(tokens)


# ── PREPARE TRAINING DATA ─────────────────────────────
print("\n🔄 Preparing training data...")
print(f"   Total training examples: {len(TRAINING_DATA)}")

sentences = [item[0] for item in TRAINING_DATA]
labels    = [item[1] for item in TRAINING_DATA]

# Show class distribution
from collections import Counter
dist = Counter(labels)
print("\n📊 Class Distribution:")
for intent, count in sorted(dist.items()):
    bar = "█" * count
    print(f"   {intent:<20} {count:>3} samples  {bar}")


# ── PREPROCESS ALL SENTENCES ──────────────────────────
print("\n🔤 Running NLP preprocessing...")
processed = [preprocess(s) for s in sentences]

# Show example transformations
print("\n✨ Sample NLP transformations:")
examples = [0, 25, 60, 100, 130]
for i in examples:
    if i < len(sentences):
        print(f"   Original : '{sentences[i]}'")
        print(f"   Processed: '{processed[i]}'")
        print()


# ── TRAIN/TEST SPLIT ──────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    processed, labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)
print(f"📚 Training samples : {len(X_train)}")
print(f"🧪 Testing samples  : {len(X_test)}")


# ── BUILD ML PIPELINE ─────────────────────────────────
"""
Pipeline steps:
1. TfidfVectorizer — converts text to numerical matrix
   - Gives higher weight to rare important words
   - ngram_range=(1,2) captures "no cost", "under price" patterns

2. LinearSVC — Support Vector Machine classifier
   - Draws decision boundaries between intents
   - Very effective for text classification
   - Faster than deep learning for small datasets
"""

model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 2),     # unigrams + bigrams
        max_features=5000,      # top 5000 features
        sublinear_tf=True,      # log scaling
        min_df=1,               # minimum document frequency
    )),
    ('clf', LinearSVC(
        C=1.0,                  # regularization
        max_iter=2000,
        dual=True,
        random_state=42
    ))
])

# ── TRAIN THE MODEL ───────────────────────────────────
print("\n🤖 Training ML Model (LinearSVC + TF-IDF)...")
model_pipeline.fit(X_train, y_train)
print("   ✅ Model trained!")


# ── EVALUATE ──────────────────────────────────────────
print("\n📈 Evaluating on test set...")
y_pred = model_pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n🎯 Test Accuracy: {accuracy*100:.1f}%")

# Cross-validation for reliable score
cv_scores = cross_val_score(model_pipeline, processed, labels, cv=5)
print(f"📊 Cross-Validation: {cv_scores.mean()*100:.1f}% ± {cv_scores.std()*100:.1f}%")

print("\n📋 Detailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=sorted(set(labels))))


# ── LIVE DEMO ─────────────────────────────────────────
print("\n🔮 Live Prediction Demo:")
test_sentences = [
    "I want to buy a phone",
    "mujhe laptop chahiye",
    "phones under 15000",
    "where is my order",
    "EMI available?",
    "how to return product",
    "any discount coupons",
    "cancel my order",
    "free shipping?",
]
for s in test_sentences:
    processed_s = preprocess(s)
    pred = model_pipeline.predict([processed_s])[0]
    # Get confidence scores
    decision = model_pipeline.decision_function([processed_s])[0]
    confidence = (np.max(decision) - np.min(decision)) / (np.max(decision) - np.min(decision) + 1) * 100
    print(f"   Input: '{s}'")
    print(f"   → Intent: {pred}")
    print()


# ── SAVE MODEL ────────────────────────────────────────
model_data = {
    'pipeline': model_pipeline,
    'intents': INTENTS,
    'accuracy': accuracy,
    'cv_score': cv_scores.mean()
}

model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"💾 Model saved to: {model_path}")
print(f"\n✅ Training complete!")
print(f"   Accuracy : {accuracy*100:.1f}%")
print(f"   CV Score : {cv_scores.mean()*100:.1f}%")
print(f"   Classes  : {len(INTENTS)} intents")
print(f"   Features : TF-IDF with bigrams")
print(f"   Algorithm: LinearSVC (Support Vector Machine)")
