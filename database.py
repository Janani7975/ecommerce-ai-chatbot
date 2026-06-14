import sqlite3

DB_PATH = "shop.db"

def search_products(query: str, max_results: int = 5) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Extract meaningful keywords, remove common words
    stop_words = ["show", "me", "find", "i", "want", "need", 
                  "please", "can", "you", "get", "a", "the"]
    keywords = [w for w in query.lower().split() if w not in stop_words]
    
    results = []
    for keyword in keywords:
        like = f"%{keyword}%"
        c.execute("""
            SELECT * FROM products
            WHERE (LOWER(name) LIKE ? 
               OR LOWER(category) LIKE ? 
               OR LOWER(description) LIKE ?)
            AND stock > 0
            ORDER BY rating DESC LIMIT ?
        """, (like, like, like, max_results))
        for row in c.fetchall():
            item = dict(row)
            if item not in results:
                results.append(item)
    
    conn.close()
    return results[:max_results]

def search_by_price(max_price: float) -> list:
    """Get products under a price limit"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE price <= ? AND stock > 0 ORDER BY price ASC LIMIT 6", (max_price,))
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return results

def get_order(order_id: str) -> dict:
    """Look up an order by its ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE order_id = ?", (order_id.upper(),))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_categories() -> list:
    """Return list of all product categories"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM products")
    cats = [r[0] for r in c.fetchall()]
    conn.close()
    return cats
