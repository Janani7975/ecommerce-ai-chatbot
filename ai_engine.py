"""
ai_engine.py — Complete ML-powered chatbot engine
Features: ML intent classification, NLP, sentiment detection,
          product comparison, Hindi support, conversation memory
"""

import re, os, pickle, sqlite3

# ── CONVERSATION MEMORY ──────────────────────────────
conversation_memory = {}

def get_memory(session_id):
    return conversation_memory.get(session_id, {
        "last_intent": None, "last_category": None,
        "last_price": None,  "turn_count": 0
    })

def update_memory(session_id, intent=None, category=None, price=None):
    if session_id not in conversation_memory:
        conversation_memory[session_id] = {
            "last_intent": None, "last_category": None,
            "last_price": None,  "turn_count": 0
        }
    mem = conversation_memory[session_id]
    if intent:   mem["last_intent"]   = intent
    if category: mem["last_category"] = category
    if price:    mem["last_price"]    = price
    mem["turn_count"] += 1

# ── LOAD ML MODEL ────────────────────────────────────
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ml_models", "model.pkl"
)

ml_model = None
preprocessor = None

def load_model():
    global ml_model, preprocessor
    try:
        with open(MODEL_PATH, 'rb') as f:
            data = pickle.load(f)
        ml_model     = data['pipeline']
        print(f"✅ ML Model loaded! Accuracy: {data.get('accuracy',0)*100:.1f}%")
        return True
    except FileNotFoundError:
        print(f"❌ model.pkl not found. Run: cd ml_models && python train_model.py")
        return False
    except Exception as e:
        print(f"❌ Model load error: {e}")
        print("   Run: cd ml_models && python train_model.py")
        return False

model_loaded = load_model()
DB_PATH = "shop.db"

# ── ENTITY EXTRACTOR ─────────────────────────────────
def extract_entities(text):
    entities = {}
    msg = text.lower()
    price_match = re.search(
        r'(?:under|below|less\s*than|upto|up\s*to)\s*₹?\s*(\d+)'
        r'|(\d+)\s*(?:rs|rupees|₹|inr)', msg)
    if price_match:
        entities['max_price'] = float(next(x for x in price_match.groups() if x))
    order_match = re.search(r'ord[-\s]?(\d+)', msg)
    if order_match:
        entities['order_id'] = f"ORD-{order_match.group(1)}"
    product_map = {
        'phone':'phones','mobile':'phones','smartphone':'phones',
        'laptop':'laptops','notebook':'laptops','computer':'laptops',
        'headphone':'electronics','earphone':'electronics',
        'earbud':'electronics','earbuds':'electronics',
        'watch':'wearables','smartwatch':'wearables',
        'tablet':'tablets','ipad':'tablets',
        'speaker':'gadgets','kindle':'gadgets',
        'kitchen':'kitchen','fryer':'kitchen','cooker':'kitchen',
        'vacuum':'home','fan':'home',
        'smart':'smart-home','alexa':'smart-home','bulb':'smart-home',
        'iphone':'iphone','samsung':'samsung','oneplus':'oneplus',
        'redmi':'redmi','realme':'realme','poco':'poco',
        'macbook':'macbook','dell':'dell','hp':'hp',
        'lenovo':'lenovo','asus':'asus','acer':'acer',
        'sony':'sony','boat':'boat','noise':'noise',
        'jbl':'jbl','apple':'apple','airpods':'airpods',
    }
    for kw, ptype in product_map.items():
        if kw in msg:
            entities['product_type'] = ptype
            entities['search_keyword'] = kw
            break
    return entities

# ── DATABASE ─────────────────────────────────────────
def db_search(keyword=None, category=None, max_price=None, limit=6):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if keyword and max_price:
        like = f"%{keyword}%"
        c.execute("""SELECT * FROM products
                     WHERE (LOWER(name) LIKE ? OR LOWER(category) LIKE ?
                     OR LOWER(description) LIKE ?)
                     AND price<=? AND stock>0
                     ORDER BY rating DESC LIMIT ?""",
                  (like,like,like,max_price,limit))
    elif keyword:
        like = f"%{keyword}%"
        c.execute("""SELECT * FROM products
                     WHERE (LOWER(name) LIKE ? OR LOWER(category) LIKE ?
                     OR LOWER(description) LIKE ?)
                     AND stock>0 ORDER BY rating DESC LIMIT ?""",
                  (like,like,like,limit))
    elif category and max_price:
        c.execute("""SELECT * FROM products WHERE LOWER(category)=?
                     AND price<=? AND stock>0
                     ORDER BY rating DESC LIMIT ?""",
                  (category.lower(),max_price,limit))
    elif category:
        c.execute("""SELECT * FROM products WHERE LOWER(category)=?
                     AND stock>0 ORDER BY rating DESC LIMIT ?""",
                  (category.lower(),limit))
    elif max_price:
        c.execute("""SELECT * FROM products WHERE price<=? AND stock>0
                     ORDER BY rating DESC LIMIT ?""", (max_price,limit))
    else:
        c.execute("SELECT * FROM products WHERE stock>0 ORDER BY rating DESC LIMIT ?",
                  (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def db_get_order(order_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE LOWER(order_id)=?", (order_id.lower(),))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_related_products(category, exclude_name="", limit=3):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""SELECT * FROM products
                 WHERE category=? AND name!=? AND stock>0
                 ORDER BY rating DESC LIMIT ?""",
              (category, exclude_name, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ── SENTIMENT DETECTION ──────────────────────────────
def detect_sentiment(text):
    t = text.lower()
    neg = ["terrible","awful","worst","bad","horrible","pathetic","useless",
           "waste","angry","frustrated","disappointed","cheated","fraud",
           "fake","broken","damaged","hate","disgusting","poor","ridiculous"]
    pos = ["great","excellent","amazing","love","best","fantastic","wonderful",
           "happy","thank","thanks","perfect","awesome","brilliant","superb",
           "good","nice"]
    ns = sum(1 for w in neg if w in t)
    ps = sum(1 for w in pos if w in t)
    if ns >= 2:   return "very_negative"
    elif ns == 1: return "negative"
    elif ps >= 1: return "positive"
    return "neutral"

# ── PRODUCT COMPARISON ───────────────────────────────
def compare_products(text):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE stock>0")
    all_p = [dict(r) for r in c.fetchall()]
    conn.close()
    found = []
    tl = text.lower()
    for p in all_p:
        words = p["name"].lower().split()[:2]
        if any(w in tl for w in words):
            found.append(p)
        if len(found) == 2:
            break
    if len(found) < 2:
        return None
    p1, p2 = found[0], found[1]
    return {
        "text": f"🆚 <b>Comparison</b><br><br>"
                f"<table style='width:100%;font-size:12px;border-collapse:collapse'>"
                f"<tr style='background:#f857a6;color:#fff'>"
                f"<th style='padding:6px;text-align:left'>Feature</th>"
                f"<th style='padding:6px'>{p1['name'][:14]}..</th>"
                f"<th style='padding:6px'>{p2['name'][:14]}..</th></tr>"
                f"<tr><td style='padding:6px'>💰 Price</td>"
                f"<td style='text-align:center'>₹{p1['price']:,.0f}</td>"
                f"<td style='text-align:center'>₹{p2['price']:,.0f}</td></tr>"
                f"<tr style='background:#f9f9f9'><td style='padding:6px'>⭐ Rating</td>"
                f"<td style='text-align:center'>{p1['rating']}</td>"
                f"<td style='text-align:center'>{p2['rating']}</td></tr>"
                f"<tr><td style='padding:6px'>🏷️ Brand</td>"
                f"<td style='text-align:center'>{p1.get('brand','N/A')}</td>"
                f"<td style='text-align:center'>{p2.get('brand','N/A')}</td></tr>"
                f"<tr style='background:#f9f9f9'><td style='padding:6px'>📦 Stock</td>"
                f"<td style='text-align:center'>{'✅' if p1['stock']>0 else '❌'}</td>"
                f"<td style='text-align:center'>{'✅' if p2['stock']>0 else '❌'}</td></tr>"
                f"</table>",
        "buttons": [
            {"label":"🛍️ Browse More","value":"browse_products"},
            {"label":"🏠 Main Menu","value":"main_menu"}
        ]
    }

# ── HINDI SUPPORT ────────────────────────────────────
HINDI_MAP = {
    "phone dikhao":"show me phones","mobile dikhao":"show me phones",
    "laptop dikhao":"show me laptops","earphone dikhao":"show me headphones",
    "mujhe phone chahiye":"I want a phone",
    "mujhe laptop chahiye":"I want a laptop",
    "ke andar":"under","se kam":"under","sasta":"cheap",
    "order kahan hai":"where is my order",
    "order track karo":"track my order",
    "wapas karna hai":"I want to return",
    "refund chahiye":"I want refund",
    "cancel karna hai":"cancel my order",
    "delivery kab hogi":"when will delivery happen",
    "offer hai kya":"any offers available",
    "kitna hai":"what is the price",
}

def detect_hindi(text):
    hindi_words = ["mujhe","chahiye","dikhao","karo","hai","nahi","kahan",
                   "kab","kya","kitna","mera","meri","sasta","lena","dena"]
    return any(w in text.lower() for w in hindi_words)

def translate_hindi(text):
    t = text.lower()
    for h, e in HINDI_MAP.items():
        if h in t:
            t = t.replace(h, e)
    return t

# ── RESPONSE TEMPLATES ───────────────────────────────
FAQ = {
    "return_refund": {
        "text": "↩️ <b>Return & Refund Policy:</b><br>• Easy 30-day returns on all products<br>• Refund processed in 5-7 business days<br>• Electronics: 7-day replacement policy<br>• Damaged/wrong items: Instant replacement",
        "buttons": [
            {"label":"↩️ Start a Return","value":"start_return"},
            {"label":"📦 Track Order","value":"track_order_menu"},
            {"label":"🏠 Main Menu","value":"main_menu"}
        ]
    },
    "payment": {
        "text": "💳 <b>Payment Options:</b><br>• UPI: GPay, PhonePe, Paytm, BHIM<br>• Credit/Debit Cards (Visa, Mastercard, RuPay)<br>• Net Banking (all major banks)<br>• Cash on Delivery (COD)<br>• No-Cost EMI above ₹3,000<br>• ShopEase Wallet",
        "buttons": [
            {"label":"💰 EMI Options","value":"emi"},
            {"label":"🏠 Main Menu","value":"main_menu"}
        ]
    },
    "shipping": {
        "text": "🚚 <b>Shipping Policy:</b><br>• Free shipping on orders above ₹499<br>• Standard delivery: 3-5 business days<br>• Express delivery: 1-2 days (₹99 extra)<br>• Same-day delivery in select cities",
        "buttons": [
            {"label":"📦 Track Order","value":"track_order_menu"},
            {"label":"🏠 Main Menu","value":"main_menu"}
        ]
    },
    "offers_coupon": {
        "text": "🎁 <b>Current Offers:</b><br>• <b>WELCOME10</b> — 10% off on first order<br>• <b>SAVE200</b> — ₹200 off above ₹999<br>• <b>FREESHIP</b> — Free express delivery<br>• <b>UPIBONUS</b> — Extra 5% off on UPI",
        "buttons": [
            {"label":"🛍️ Shop Now","value":"browse_products"},
            {"label":"🏠 Main Menu","value":"main_menu"}
        ]
    },
    "emi": {
        "text": "💰 <b>No-Cost EMI:</b><br>• Available on orders above ₹3,000<br>• 3, 6, 9, 12 month options<br>• HDFC, ICICI, SBI, Axis, RBL cards<br>• Bajaj Finserv accepted<br>• Zero processing fee on select items",
        "buttons": [
            {"label":"🛍️ Browse Products","value":"browse_products"},
            {"label":"🏠 Main Menu","value":"main_menu"}
        ]
    },
    "cancel_order": {
        "text": "❌ <b>Order Cancellation:</b><br>• Cancel before dispatch — completely free<br>• Go to My Orders → Cancel Order<br>• Prepaid orders: refund in 5-7 business days<br>• COD orders: no charge if cancelled before delivery",
        "buttons": [
            {"label":"📦 Track Order","value":"track_order_menu"},
            {"label":"🏠 Main Menu","value":"main_menu"}
        ]
    },
    "account": {
        "text": "👤 <b>Account Help:</b><br>• Forgot password? Click 'Forgot Password' on login page<br>• OTP not received? Retry after 30 seconds<br>• Change mobile number: Profile → Edit Profile<br>• Support: help@shopeaseai.in",
        "buttons": [{"label":"🏠 Main Menu","value":"main_menu"}]
    },
    "warranty": {
        "text": "🛡️ <b>Warranty Policy:</b><br>• Mobiles: 1 year brand warranty<br>• Laptops: 1-3 years brand warranty<br>• Accessories: 6 months warranty<br>• Keep your invoice for warranty claims",
        "buttons": [{"label":"🏠 Main Menu","value":"main_menu"}]
    }
}

MAIN_MENU = {
    "text": "👋 Hi! I'm <b>Nova</b>, your ShopEase AI assistant!<br>How can I help you today?",
    "buttons": [
        {"label":"🛍️ Browse Products","value":"browse_products"},
        {"label":"📦 Track My Order","value":"track_order_menu"},
        {"label":"↩️ Returns & Refunds","value":"return_refund"},
        {"label":"💳 Payment Help","value":"payment"},
        {"label":"🎁 Offers & Coupons","value":"offers_coupon"},
        {"label":"❓ More Help","value":"more_help"}
    ]
}

BROWSE_MENU = {
    "text": "🛍️ What are you looking for?",
    "buttons": [
        {"label":"📱 Phones","value":"cat_phones"},
        {"label":"💻 Laptops","value":"cat_laptops"},
        {"label":"🎧 Headphones","value":"cat_headphones"},
        {"label":"⌚ Smartwatches","value":"cat_wearables"},
        {"label":"📱 Tablets","value":"cat_tablets"},
        {"label":"🏠 Home & Kitchen","value":"cat_home"},
        {"label":"🔙 Back","value":"main_menu"}
    ]
}

MORE_HELP_MENU = {
    "text": "❓ Select a topic:",
    "buttons": [
        {"label":"🚚 Shipping Info","value":"shipping"},
        {"label":"💰 EMI Options","value":"emi"},
        {"label":"❌ Cancel Order","value":"cancel_order"},
        {"label":"👤 My Account","value":"account"},
        {"label":"🛡️ Warranty","value":"warranty"},
        {"label":"🔙 Main Menu","value":"main_menu"}
    ]
}

def format_products(products, title=""):
    if not products:
        return {
            "text": "😔 No products found. Try a different search!",
            "buttons": [
                {"label":"🔍 Browse All","value":"browse_products"},
                {"label":"🏠 Main Menu","value":"main_menu"}
            ]
        }
    cards = [{"name":p["name"], "price":f"₹{p['price']:,.0f}",
              "rating":f"⭐ {p['rating']}", "category":p["category"],
              "brand":p.get("brand",""), "stock":"In Stock ✅"}
             for p in products]
    # Related products
    related = []
    if products:
        rp = get_related_products(products[0]["category"], products[0]["name"])
        related = [{"name":p["name"], "price":f"₹{p['price']:,.0f}",
                    "rating":f"⭐ {p['rating']}", "category":p["category"]}
                   for p in rp]
    return {
        "text": f"🛍️ <b>{title}</b>" if title else "🛍️ Here's what I found:",
        "products": cards,
        "related": related,
        "buttons": [
            {"label":"🔍 Search More","value":"browse_products"},
            {"label":"🏠 Main Menu","value":"main_menu"}
        ]
    }

BUTTON_MAP = {
    "main_menu":        lambda: MAIN_MENU,
    "browse_products":  lambda: BROWSE_MENU,
    "more_help":        lambda: MORE_HELP_MENU,
    "track_order_menu": lambda: {
        "text":"📦 Please type your <b>Order ID</b><br>Example: <b>ORD-1001</b>",
        "buttons":[{"label":"🔙 Main Menu","value":"main_menu"}]},
    "start_return": lambda: {
        "text":"↩️ Share your <b>Order ID</b> and reason for return.",
        "buttons":[{"label":"🔙 Main Menu","value":"main_menu"}]},
    "return_refund":  lambda: FAQ["return_refund"],
    "payment":        lambda: FAQ["payment"],
    "shipping":       lambda: FAQ["shipping"],
    "offers_coupon":  lambda: FAQ["offers_coupon"],
    "emi":            lambda: FAQ["emi"],
    "cancel_order":   lambda: FAQ["cancel_order"],
    "account":        lambda: FAQ["account"],
    "warranty":       lambda: FAQ["warranty"],
    "cat_phones":     lambda: format_products(db_search(category="phones"),    "📱 Phones"),
    "cat_laptops":    lambda: format_products(db_search(category="laptops"),   "💻 Laptops"),
    "cat_headphones": lambda: format_products(db_search(keyword="headphone"),  "🎧 Headphones"),
    "cat_wearables":  lambda: format_products(db_search(category="wearables"), "⌚ Smartwatches"),
    "cat_tablets":    lambda: format_products(db_search(category="tablets"),   "📱 Tablets"),
    "cat_home":       lambda: format_products(db_search(keyword="home"),       "🏠 Home & Kitchen"),
}

# ── MAIN RESPONSE FUNCTION ───────────────────────────
def get_response(user_input, session_id=None):
    msg = user_input.strip()
    msg_lower = msg.lower()

    # Step 1 — Translate Hindi
    if detect_hindi(msg):
        msg = translate_hindi(msg)
        msg_lower = msg.lower()

    # Step 2 — Sentiment check
    sentiment = detect_sentiment(msg)
    if sentiment == "very_negative":
        return {
            "text": "😔 I'm really sorry to hear that! I understand your frustration.<br>Let me connect you with the right help immediately.",
            "buttons": [
                {"label":"📦 Track Order","value":"track_order_menu"},
                {"label":"↩️ Return & Refund","value":"return_refund"},
                {"label":"❌ Cancel Order","value":"cancel_order"},
                {"label":"🏠 Main Menu","value":"main_menu"}
            ]
        }
    elif sentiment == "positive":
        return {
            "text": "😊 Thank you so much! We love making you happy!<br>How can I help you today?",
            "buttons": MAIN_MENU["buttons"]
        }

    # Step 3 — Product comparison
    if any(w in msg_lower for w in ["compare","vs","versus","difference between","which is better"]):
        result = compare_products(msg)
        if result:
            return result
        return {
            "text": "🆚 Mention both product names to compare.<br>Example: <b>compare iPhone 16 and Samsung S25</b>",
            "buttons": [{"label":"🛍️ Browse Products","value":"browse_products"}]
        }

    # Step 4 — Button click
    if msg_lower in BUTTON_MAP:
        return BUTTON_MAP[msg_lower]()

    # Step 5 — Order ID
    order_match = re.search(r'ord[-\s]?(\d+)', msg_lower)
    if order_match:
        order_id = f"ORD-{order_match.group(1)}"
        order = db_get_order(order_id)
        if order:
            emoji = {"Processing":"⏳","Shipped":"🚚","Out for Delivery":"📦",
                     "Delivered":"✅","Cancelled":"❌"}.get(order["status"],"📦")
            return {
                "text": f"📦 <b>Order Found!</b><br><br>"
                        f"🆔 Order ID: <b>{order['order_id']}</b><br>"
                        f"👤 Customer: {order['customer_name']}<br>"
                        f"🛍️ Product: {order['product_name']}<br>"
                        f"{emoji} Status: <b>{order['status']}</b>",
                "buttons": [
                    {"label":"↩️ Return This","value":"return_refund"},
                    {"label":"🏠 Main Menu","value":"main_menu"}
                ]
            }
        return {
            "text": f"😔 Order <b>{order_id}</b> not found. Please check the ID.",
            "buttons": [{"label":"🏠 Main Menu","value":"main_menu"}]
        }

    # Step 6 — ML Model prediction
    predicted_intent = "greeting"
    if model_loaded and ml_model:
        try:
            predicted_intent = ml_model.predict([msg])[0]
        except Exception as e:
            print(f"ML prediction error: {e}")
            predicted_intent = "greeting"

    # Step 7 — Extract entities
    entities = extract_entities(msg)

    # Step 8 — Memory
    mem = get_memory(session_id) if session_id else {}

    # Step 9 — Route by intent
    if predicted_intent == "greeting":
        return MAIN_MENU

    elif predicted_intent == "goodbye":
        return {
            "text": "😊 Thank you for shopping with <b>ShopEase</b>!<br>Have a great day! 🛍️",
            "buttons": [
                {"label":"🛍️ Continue Shopping","value":"browse_products"},
                {"label":"🏠 Main Menu","value":"main_menu"}
            ]
        }

    elif predicted_intent == "product_search":
        keyword  = entities.get('search_keyword','')
        category = entities.get('product_type','')
        price    = entities.get('max_price')
        if keyword or category:
            update_memory(session_id, intent="product_search",
                         category=keyword or category)
        cat_map = {
            'phones':'phones','laptops':'laptops',
            'headphones':'electronics','wearables':'wearables',
            'tablets':'tablets','gadgets':'gadgets',
            'kitchen':'kitchen','home':'home','smart-home':'smart-home'
        }
        cat = cat_map.get(category)
        kw  = keyword if keyword else (category if category else None)
        products = db_search(keyword=kw, category=cat, max_price=price)
        return format_products(products,
            f"Results for '{kw}'" if kw else "Top Rated Products")

    elif predicted_intent == "price_search":
        price   = entities.get('max_price')
        keyword = entities.get('search_keyword','')
        if not keyword and mem.get("last_category"):
            keyword = mem["last_category"]
        if price:
            update_memory(session_id, intent="price_search", price=price)
            return format_products(
                db_search(keyword=keyword or None, max_price=price),
                f"{''+keyword.title()+' ' if keyword else ''}Products under ₹{price:,.0f}")
        return BROWSE_MENU

    elif predicted_intent == "track_order":
        return BUTTON_MAP["track_order_menu"]()

    elif predicted_intent in FAQ:
        return FAQ[predicted_intent]

    # Fallback
    return {
        "text": "🤔 I didn't quite understand that. Let me show you what I can help with!",
        "buttons": MAIN_MENU["buttons"]
    }
