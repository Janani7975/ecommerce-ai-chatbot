"""
Tina Chatbot Brain — No external AI needed
Pure Python rule-based + keyword matching engine
"""

import sqlite3
import re

DB_PATH = "shop.db"

# ═══════════════════════════════════════════
# FAQ DATABASE — All common questions answered
# ═══════════════════════════════════════════
FAQ_DATA = {
    # SHIPPING
    "shipping": {
        "keywords": ["shipping", "delivery", "deliver", "ship", "arrive", "when will", "how long"],
        "answer": "🚚 <b>Shipping Policy:</b><br>• Free shipping on orders above ₹499<br>• Standard delivery: 3-5 business days<br>• Express delivery: 1-2 business days (₹99 extra)<br>• Same-day delivery available in select cities<br><br>You'll get a tracking link via SMS & email once your order is shipped!"
    },
    # RETURNS
    "returns": {
        "keywords": ["return", "refund", "exchange", "replace", "money back", "cancel order", "wrong item"],
        "answer": "↩️ <b>Return & Refund Policy:</b><br>• Easy 30-day returns on all products<br>• Refund processed in 5-7 business days<br>• For electronics: 7-day replacement policy<br>• Damaged/wrong items: Instant replacement<br><br>To initiate a return, share your order number and I'll help you right away!"
    },
    # PAYMENT
    "payment": {
        "keywords": ["payment", "pay", "upi", "card", "credit", "debit", "net banking", "emi", "cash on delivery", "cod", "wallet", "gpay", "phonepe", "paytm"],
        "answer": "💳 <b>Payment Options:</b><br>• UPI: GPay, PhonePe, Paytm, BHIM<br>• Credit/Debit Cards (Visa, Mastercard, RuPay)<br>• Net Banking (all major banks)<br>• Cash on Delivery (COD) available<br>• No-Cost EMI on orders above ₹3,000<br>• ShopSphere Wallet<br><br>All payments are 100% secure & encrypted! 🔒"
    },
    # COUPON
    "coupon": {
        "keywords": ["coupon", "discount", "offer", "promo", "code", "deal", "sale", "off", "voucher"],
        "answer": "🎁 <b>Current Offers & Coupons:</b><br>• <b>WELCOME10</b> — 10% off on first order<br>• <b>SAVE200</b> — ₹200 off on orders above ₹999<br>• <b>FREESHIP</b> — Free express delivery<br>• <b>UPIBONUS</b> — Extra 5% off on UPI payments<br><br>Apply coupon at checkout. Valid for limited time!"
    },
    # TRACK ORDER
    "track": {
        "keywords": ["track", "tracking", "status", "where is my order", "order status", "shipped"],
        "answer": "📦 <b>Track Your Order:</b><br>Please share your <b>Order ID</b> (format: ORD-1001) and I'll look it up for you instantly!<br><br>You can also track via:<br>• SMS link sent to your registered mobile<br>• Email confirmation<br>• My Orders section in the app"
    },
    # ACCOUNT
    "account": {
        "keywords": ["account", "login", "password", "forgot", "sign in", "register", "profile", "otp"],
        "answer": "👤 <b>Account Help:</b><br>• Forgot password? Click 'Forgot Password' on login page<br>• OTP not received? Check spam or retry after 30 seconds<br>• Change mobile number: Go to Profile → Edit Profile<br>• Delete account: Contact support at help@shopsphere.in<br><br>Need more help? Tell me your specific issue!"
    },
    # WARRANTY
    "warranty": {
        "keywords": ["warranty", "guarantee", "repair", "service center", "brand warranty", "damage"],
        "answer": "🛡️ <b>Warranty Information:</b><br>• All electronics come with manufacturer warranty<br>• Mobiles: 1 year brand warranty<br>• Laptops: 1-3 years brand warranty<br>• Accessories: 6 months warranty<br><br>For warranty claims, keep your invoice handy and visit the nearest service center or contact us!"
    },
    # EMI
    "emi": {
        "keywords": ["emi", "no cost emi", "installment", "monthly", "finance"],
        "answer": "💰 <b>No-Cost EMI Options:</b><br>• Available on orders above ₹3,000<br>• 3, 6, 9, 12 month options<br>• Available on HDFC, ICICI, SBI, Axis cards<br>• Bajaj Finserv card accepted<br>• Zero processing fee on select products<br><br>Choose EMI option at checkout!"
    },
    # CANCEL
    "cancel": {
        "keywords": ["cancel", "cancellation", "stop order", "don't want"],
        "answer": "❌ <b>Order Cancellation:</b><br>• Orders can be cancelled before dispatch<br>• Go to My Orders → Select Order → Cancel<br>• Refund within 5-7 business days<br>• Prepaid orders: Refund to original payment method<br>• COD orders: No charge if cancelled before delivery<br><br>Share your Order ID if you need help cancelling!"
    },
    # GIFT CARD
    "giftcard": {
        "keywords": ["gift card", "gift voucher", "gift", "gifting"],
        "answer": "🎀 <b>Gift Cards:</b><br>• Available in ₹500, ₹1000, ₹2000, ₹5000 denominations<br>• Valid for 1 year from purchase date<br>• Can be used across all categories<br>• Send directly to recipient's email/phone<br>• No expiry on balance<br><br>Perfect for birthdays & occasions! 🎂"
    }
}

# ═══════════════════════════════════════════
# QUICK REPLY MENUS — Like Zepto/Nykaa buttons
# ═══════════════════════════════════════════
MAIN_MENU = {
    "text": "👋 Hi! I'm <b>Tina</b>, your ShopSphere assistant!<br>How can I help you today?",
    "buttons": [
        {"label": "🛍️ Browse Products", "value": "browse_products"},
        {"label": "📦 Track My Order", "value": "track_order"},
        {"label": "↩️ Returns & Refunds", "value": "returns"},
        {"label": "💳 Payment Help", "value": "payment"},
        {"label": "🎁 Offers & Coupons", "value": "coupon"},
        {"label": "❓ More Help", "value": "more_help"}
    ]
}

BROWSE_MENU = {
    "text": "🛍️ What are you looking for?",
    "buttons": [
        {"label": "📱 Phones", "value": "search_phones"},
        {"label": "💻 Laptops", "value": "search_laptops"},
        {"label": "🎧 Headphones", "value": "search_headphones"},
        {"label": "⌚ Smartwatches", "value": "search_smartwatch"},
        {"label": "📺 Electronics", "value": "search_electronics"},
        {"label": "🏠 Home & Kitchen", "value": "search_home"},
        {"label": "🔙 Main Menu", "value": "main_menu"}
    ]
}

MORE_HELP_MENU = {
    "text": "❓ What do you need help with?",
    "buttons": [
        {"label": "🚚 Shipping Info", "value": "shipping"},
        {"label": "🛡️ Warranty", "value": "warranty"},
        {"label": "💰 EMI Options", "value": "emi"},
        {"label": "👤 My Account", "value": "account"},
        {"label": "🎀 Gift Cards", "value": "giftcard"},
        {"label": "❌ Cancel Order", "value": "cancel"},
        {"label": "🔙 Main Menu", "value": "main_menu"}
    ]
}

# ═══════════════════════════════════════════
# DATABASE FUNCTIONS
# ═══════════════════════════════════════════
def search_products(keyword, max_price=None, limit=5):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    like = f"%{keyword.lower()}%"
    if max_price:
        c.execute("""SELECT * FROM products
                     WHERE (LOWER(name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(description) LIKE ?)
                     AND price <= ? AND stock > 0
                     ORDER BY rating DESC LIMIT ?""",
                  (like, like, like, max_price, limit))
    else:
        c.execute("""SELECT * FROM products
                     WHERE (LOWER(name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(description) LIKE ?)
                     AND stock > 0
                     ORDER BY rating DESC LIMIT ?""",
                  (like, like, like, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_products_by_category(category, limit=6):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE LOWER(category)=? AND stock>0 ORDER BY rating DESC LIMIT ?",
              (category.lower(), limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_order(order_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE LOWER(order_id)=?", (order_id.lower(),))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_products_under_price(max_price, limit=6):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE price<=? AND stock>0 ORDER BY rating DESC LIMIT ?",
              (max_price, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ═══════════════════════════════════════════
# FORMAT PRODUCT CARDS
# ═══════════════════════════════════════════
def format_products(products, title=""):
    if not products:
        return {"text": "😔 No products found in this category right now. Check back soon!", "buttons": [
            {"label": "🔙 Browse More", "value": "browse_products"},
            {"label": "🏠 Main Menu", "value": "main_menu"}
        ]}
    cards = []
    for p in products:
        cards.append({
            "name": p["name"],
            "price": f"₹{p['price']:,.0f}",
            "rating": f"⭐ {p['rating']}",
            "category": p["category"],
            "description": p.get("description", ""),
            "stock": "In Stock ✅" if p["stock"] > 0 else "Out of Stock ❌"
        })
    return {
        "text": f"🛍️ <b>{title}</b>" if title else "🛍️ Here's what I found:",
        "products": cards,
        "buttons": [
            {"label": "🔍 Search More", "value": "browse_products"},
            {"label": "🏠 Main Menu", "value": "main_menu"}
        ]
    }

# ═══════════════════════════════════════════
# MAIN RESPONSE ENGINE
# ═══════════════════════════════════════════
def get_response(user_input, session_state=None):
    """
    Main function. Returns dict with:
    - text: response message (HTML allowed)
    - buttons: list of {label, value} quick reply buttons (optional)
    - products: list of product cards (optional)
    """
    msg = user_input.strip().lower()

    # ── BUTTON CLICKS (predefined values) ──
    button_actions = {
        "main_menu": lambda: MAIN_MENU,
        "browse_products": lambda: BROWSE_MENU,
        "more_help": lambda: MORE_HELP_MENU,
        "track_order": lambda: {
            "text": "📦 <b>Track Your Order</b><br>Please type your Order ID below.<br>Example: <b>ORD-1001</b>",
            "buttons": [{"label": "🔙 Main Menu", "value": "main_menu"}]
        },
        "returns": lambda: {"text": FAQ_DATA["returns"]["answer"], "buttons": [
            {"label": "Start a Return", "value": "start_return"},
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "payment": lambda: {"text": FAQ_DATA["payment"]["answer"], "buttons": [
            {"label": "EMI Options", "value": "emi"},
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "coupon": lambda: {"text": FAQ_DATA["coupon"]["answer"], "buttons": [
            {"label": "🛍️ Shop Now", "value": "browse_products"},
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "shipping": lambda: {"text": FAQ_DATA["shipping"]["answer"], "buttons": [
            {"label": "Track Order", "value": "track_order"},
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "warranty": lambda: {"text": FAQ_DATA["warranty"]["answer"], "buttons": [
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "emi": lambda: {"text": FAQ_DATA["emi"]["answer"], "buttons": [
            {"label": "🛍️ Browse Products", "value": "browse_products"},
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "account": lambda: {"text": FAQ_DATA["account"]["answer"], "buttons": [
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "giftcard": lambda: {"text": FAQ_DATA["giftcard"]["answer"], "buttons": [
            {"label": "🛍️ Buy Gift Card", "value": "browse_products"},
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "cancel": lambda: {"text": FAQ_DATA["cancel"]["answer"], "buttons": [
            {"label": "Track Order", "value": "track_order"},
            {"label": "🔙 Main Menu", "value": "main_menu"}
        ]},
        "start_return": lambda: {
            "text": "↩️ To start a return, please share your <b>Order ID</b> (e.g. ORD-1001) and reason for return.",
            "buttons": [{"label": "🔙 Main Menu", "value": "main_menu"}]
        },
        # Category searches
        "search_phones": lambda: format_products(get_products_by_category("phones"), "Phones"),
        "search_laptops": lambda: format_products(get_products_by_category("laptops"), "Laptops"),
        "search_headphones": lambda: format_products(
            search_products("headphone") + search_products("earbuds"), "Headphones & Earbuds"),
        "search_smartwatch": lambda: format_products(
            search_products("smartwatch") + search_products("watch"), "Smartwatches"),
        "search_electronics": lambda: format_products(get_products_by_category("electronics"), "Electronics"),
        "search_home": lambda: format_products(
            get_products_by_category("kitchen") + get_products_by_category("home"), "Home & Kitchen"),
    }

    if msg in button_actions:
        return button_actions[msg]()

    # ── ORDER TRACKING ──
    order_match = re.search(r"ord[-\s]?(\d+)", msg)
    if order_match:
        order_id = f"ORD-{order_match.group(1)}"
        order = get_order(order_id)
        if order:
            status_emoji = {"Processing": "⏳", "Shipped": "🚚", "Out for Delivery": "📦",
                            "Delivered": "✅", "Cancelled": "❌"}.get(order["status"], "📦")
            return {
                "text": f"📦 <b>Order Found!</b><br><br>"
                        f"🆔 Order ID: <b>{order['order_id']}</b><br>"
                        f"👤 Customer: {order['customer_name']}<br>"
                        f"🛍️ Product: {order['product_name']}<br>"
                        f"{status_emoji} Status: <b>{order['status']}</b><br><br>"
                        f"Need anything else?",
                "buttons": [
                    {"label": "↩️ Return This Order", "value": "returns"},
                    {"label": "🏠 Main Menu", "value": "main_menu"}
                ]
            }
        else:
            return {
                "text": f"😔 I couldn't find order <b>{order_id}</b>.<br>"
                        f"Please check the order ID and try again, or contact our support team.",
                "buttons": [
                    {"label": "🏠 Main Menu", "value": "main_menu"}
                ]
            }

    # ── PRICE SEARCH ──
    price_match = re.search(
        r"under\s*₹?\s*(\d+)|below\s*₹?\s*(\d+)|less\s*than\s*₹?\s*(\d+)|(\d+)\s*(?:rs|rupees|₹)",
        msg
    )
    if price_match:
        raw = float(next(x for x in price_match.groups() if x))
        price = raw if raw > 500 else raw * 83
        products = get_products_under_price(price)
        return format_products(products, f"Products under ₹{price:,.0f}")

    # ── KEYWORD PRODUCT SEARCH ──
    product_keywords = {
        "phone": "phones", "mobile": "phones", "smartphone": "phones",
        "laptop": "laptops", "computer": "laptops", "notebook": "laptops",
        "headphone": None, "earphone": None, "earbuds": None, "earbud": None,
        "watch": None, "smartwatch": None,
        "tablet": None, "ipad": None,
        "speaker": None, "bluetooth": None,
        "camera": None,
        "keyboard": None, "mouse": None,
        "charger": None, "cable": None,
    }
    for kw, category in product_keywords.items():
        if kw in msg:
            if category:
                results = get_products_by_category(category)
            else:
                results = search_products(kw)
            if results:
                return format_products(results, f"Results for '{kw}'")

    # ── GREETINGS ──
    greetings = ["hi", "hello", "hey", "hii", "helo", "namaste", "good morning",
                 "good evening", "good afternoon", "sup", "howdy"]
    if any(g in msg for g in greetings):
        return MAIN_MENU

    # ── FAQ KEYWORD MATCHING ──
    for topic, data in FAQ_DATA.items():
        if any(kw in msg for kw in data["keywords"]):
            return {
                "text": data["answer"],
                "buttons": [
                    {"label": "🏠 Main Menu", "value": "main_menu"},
                    {"label": "🛍️ Browse Products", "value": "browse_products"}
                ]
            }

    # ── THANKS ──
    if any(w in msg for w in ["thank", "thanks", "ok thanks", "okay", "great", "perfect"]):
        return {
            "text": "😊 You're welcome! Happy shopping at ShopSphere!<br>Is there anything else I can help you with?",
            "buttons": [
                {"label": "🛍️ Browse Products", "value": "browse_products"},
                {"label": "🏠 Main Menu", "value": "main_menu"}
            ]
        }

    # ── FALLBACK ──
    return {
        "text": "🤔 I'm not sure about that. Let me show you what I can help with!",
        "buttons": MAIN_MENU["buttons"]
    }
