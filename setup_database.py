import sqlite3

def setup_database():
    conn = sqlite3.connect("shop.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price REAL,
        stock INTEGER DEFAULT 0,
        description TEXT,
        rating REAL DEFAULT 4.0
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT UNIQUE,
        customer_name TEXT,
        product_name TEXT,
        status TEXT DEFAULT 'Processing',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    products = [
        # PHONES
        ("iPhone 16 Pro 256GB",          "phones",      134900, 18, "Apple flagship titanium design, A18 Pro chip",     4.8),
        ("Samsung Galaxy S25 Ultra",      "phones",       124999, 12, "200MP camera, Snapdragon 8 Elite, S-Pen",          4.8),
        ("OnePlus 13 256GB",              "phones",        69999, 30, "Hasselblad camera, Snapdragon 8 Elite, 100W charge",4.7),
        ("Samsung Galaxy A55 5G",         "phones",        34999, 45, "50MP camera, 5G, IP67 water resistant",            4.5),
        ("Redmi Note 13 Pro+ 5G",         "phones",        29999, 50, "200MP camera, 120W fast charging, 5G",             4.6),
        ("Redmi Note 13 5G",              "phones",        17999, 60, "Snapdragon 7s Gen 2, 108MP camera",                4.5),
        ("Realme Narzo 70 Pro 5G",        "phones",        19999, 55, "50MP Sony camera, 67W fast charge, 5G",            4.4),
        ("Poco X6 Pro 5G",                "phones",        22999, 40, "Dimensity 8300-Ultra, 67W charging",               4.5),
        ("Poco M6 Pro 5G",                "phones",        13999, 70, "Snapdragon 4s Gen 2, 5G support",                  4.3),
        ("Itel P55 5G",                   "phones",         8999, 80, "5G, 5000mAh battery, 50MP camera",                 4.1),
        ("Lava Blaze Curve 5G",           "phones",         9999, 75, "Curved display, 5G, 50MP camera",                  4.1),

        # LAPTOPS
        ("Apple MacBook Air M3 8GB",      "laptops",      114900,  8, "13.6 inch Retina, M3 chip, 18hr battery",          4.9),
        ("Apple MacBook Pro M3 Pro",      "laptops",      199900,  5, "14 inch, M3 Pro chip, 18hr battery",               4.9),
        ("Dell XPS 15 Core i7",           "laptops",       74900,  6, "15.6 inch OLED, Intel i7, 64GB RAM",               4.6),
        ("HP Spectre x360 14",            "laptops",       59990,  8, "2-in-1 laptop, Intel Evo, OLED touch",             4.6),
        ("Lenovo ThinkPad E14 Gen 5",     "laptops",       52990, 10, "AMD Ryzen 7, 16GB RAM, business laptop",           4.5),
        ("ASUS VivoBook 16X",             "laptops",       47990, 12, "Intel i5 12th Gen, 16GB, 512GB SSD",               4.4),
        ("HP Pavilion 15 Ryzen 5",        "laptops",       45990, 15, "AMD Ryzen 5 7520U, 16GB, 512GB SSD",               4.3),
        ("Lenovo IdeaPad Slim 3",         "laptops",       32990, 20, "Intel i3 12th Gen, 8GB, 512GB, thin & light",      4.2),
        ("Acer Aspire Lite Ryzen 3",      "laptops",       27990, 18, "AMD Ryzen 3, 8GB RAM, 512GB SSD",                  4.1),
        ("HP 14s Intel i3",               "laptops",       31990, 22, "Intel i3 12th Gen, 8GB, 256GB SSD, 14 inch",       4.2),

        # HEADPHONES
        ("Sony WH-1000XM5",               "electronics",  23999, 15, "Industry best noise cancelling, 30hr battery",     4.8),
        ("Apple AirPods Pro 2",           "electronics",  19900, 20, "H2 chip, ANC, Transparency mode, MagSafe",         4.8),
        ("Samsung Galaxy Buds3 Pro",      "electronics",  14999, 18, "ANC, Hi-Fi audio, IPX7 waterproof",                4.7),
        ("boAt Rockerz 550 BT",           "electronics",   1499, 80, "40hr playback, deep bass, foldable",               4.3),
        ("boAt Airdopes 141",             "electronics",    899, 100,"42hr total playback, IPX4, instant connect",        4.2),
        ("JBL Tune 770NC",                "electronics",   4999, 40, "ANC, 70hr battery, JBL Pure Bass",                 4.5),
        ("Noise Buds VS104",              "electronics",    999, 90, "50hr total playback, quad mic, low latency",        4.2),
        ("Skullcandy Hesh ANC",           "electronics",   3499, 35, "Active noise cancelling, 22hr battery",            4.4),
        ("OneOdio Monitor 60",            "electronics",   2799, 25, "Professional wired headphones, studio quality",     4.5),

        # SMARTWATCHES & FITNESS
        ("Apple Watch Series 10",         "wearables",    41900, 10, "Largest display, sleep apnea detection, GPS",      4.8),
        ("Samsung Galaxy Watch 7",        "wearables",    26999, 15, "Advanced health tracking, sleep coaching",         4.7),
        ("Garmin Venu 3",                 "wearables",    39999,  8, "AMOLED, sleep coaching, up to 14 days battery",    4.7),
        ("Noise ColorFit Ultra 3",        "wearables",    2499, 100,"1.96 inch AMOLED, BT calling, 100+ sports modes",   4.3),
        ("boAt Wave Call 2",              "wearables",    1499, 120,"BT calling, 1.83 inch display, health suite",       4.2),
        ("Fitbit Charge 6",               "wearables",   12999, 25, "Google integration, ECG, GPS",                     4.5),
        ("Mi Smart Band 8 Pro",           "wearables",    4999, 60, "1.74 inch AMOLED, 14-day battery, GPS",            4.4),

        # TABLETS
        ("Apple iPad Air M2 11 inch",     "tablets",     59900,  8, "M2 chip, 11 inch Liquid Retina, 5G optional",      4.8),
        ("Samsung Galaxy Tab S9 FE",      "tablets",     26999, 12, "10.9 inch, IP68, S-Pen included",                  4.6),
        ("Redmi Pad Pro 5G",              "tablets",     26999, 15, "12.1 inch, Snapdragon 7s Gen 2, 5G",               4.5),
        ("Realme Pad 2",                  "tablets",     15999, 20, "11.5 inch, 8300mAh, Dolby Atmos",                  4.3),

        # SMART HOME
        ("Amazon Echo Dot 5th Gen",       "smart-home",   4499, 50, "Compact smart speaker with Alexa",                 4.5),
        ("Amazon Echo Show 8",            "smart-home",  11999, 20, "8 inch screen, Alexa, video calling",              4.6),
        ("Mi Smart Plug 16A",             "smart-home",    799,150, "WiFi smart plug, energy monitoring, voice control", 4.3),
        ("Philips Hue Smart Bulb",        "smart-home",   1599, 80, "16 million colors, voice/app control",             4.5),

        # KITCHEN
        ("Instant Pot Duo 7-in-1 5.7L",  "kitchen",     7499, 40, "Pressure cooker, slow cooker, rice cooker",         4.8),
        ("Philips Air Fryer HD9200",      "kitchen",     4999, 35, "4.1L, rapid air technology, 80% less fat",         4.6),
        ("Prestige Electric Kettle",      "kitchen",     1299, 60, "1.5L, auto shut-off, boil dry protection",          4.4),
        ("Morphy Richards OTG 28L",       "kitchen",     3499, 30, "28L, 6 heating modes, rotisserie",                  4.5),

        # HOME
        ("Dyson V15 Detect Absolute",     "home",        54900,  7, "Laser dust detection, 60min battery, LCD screen",  4.8),
        ("Eureka Forbes Trendy Zip",      "home",        4999, 25, "1400W, 2L dust bag, HEPA filter",                  4.3),
        ("Atomberg Renesa Ceiling Fan",   "home",        3499, 40, "BLDC motor, remote, 5 star rated, saves 65% power", 4.7),

        # GADGETS
        ("Kindle Paperwhite 16GB",        "gadgets",    13999, 30, "6.8 inch, 300ppi, adjustable warm light, IPX8",     4.7),
        ("JBL Go 4 Bluetooth Speaker",    "gadgets",    2699, 60, "Portable, IP67, 7hr battery, bold JBL Pro Sound",   4.5),
        ("Anker PowerBank 26800mAh",      "gadgets",    3999, 40, "26800mAh, dual USB-C, fast charging",               4.6),
        ("GoPro Hero 13 Black",           "gadgets",   39999, 10, "5.3K video, HyperSmooth 6.0, waterproof 10m",       4.7),
    ]

    c.execute("DELETE FROM products")
    c.executemany(
        "INSERT INTO products (name, category, price, stock, description, rating) VALUES (?,?,?,?,?,?)",
        products
    )

    orders = [
        ("ORD-1001", "Rahul Kumar",   "Sony WH-1000XM5",            "Shipped"),
        ("ORD-1002", "Priya Patel",   "iPhone 16 Pro 256GB",         "Out for Delivery"),
        ("ORD-1003", "Amit Sharma",   "Apple MacBook Air M3 8GB",    "Delivered"),
        ("ORD-1004", "Sneha Rao",     "Redmi Note 13 Pro+ 5G",       "Processing"),
        ("ORD-1005", "Vikram Singh",  "boAt Airdopes 141",           "Shipped"),
        ("ORD-1006", "Anjali Mehta",  "Noise ColorFit Ultra 3",      "Processing"),
        ("ORD-1007", "Kiran Reddy",   "Samsung Galaxy Tab S9 FE",    "Delivered"),
        ("ORD-1008", "Ravi Verma",    "Philips Air Fryer HD9200",    "Out for Delivery"),
    ]
    c.execute("DELETE FROM orders")
    c.executemany(
        "INSERT INTO orders (order_id, customer_name, product_name, status) VALUES (?,?,?,?)",
        orders
    )

    conn.commit()
    conn.close()
    print(f"✅ Database ready! {len(products)} products, {len(orders)} orders loaded.")

if __name__ == "__main__":
    setup_database()
