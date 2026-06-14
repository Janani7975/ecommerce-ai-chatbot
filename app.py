from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3, os
from ai_engine import get_response
from setup_database import setup_database

app = Flask(__name__)
CORS(app)
setup_database()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message"}), 400
    msg = data["message"].strip()
    if not msg:
        return jsonify({"error": "Empty"}), 400
    response = get_response(msg)
    return jsonify(response)

@app.route("/suggestions")
def suggestions():
    q = request.args.get("q", "").strip().lower()
    if len(q) < 2:
        return jsonify([])
    conn = sqlite3.connect("shop.db")
    c = conn.cursor()
    c.execute("""SELECT DISTINCT name FROM products
                 WHERE LOWER(name) LIKE ? AND stock>0
                 LIMIT 5""", (f"%{q}%",))
    results = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(results)

@app.route("/health")
def health():
    return jsonify({"status": "running", "bot": "ShopEase AI"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
