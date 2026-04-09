import sqlite3

conn = sqlite3.connect("database/visioncart.db")
cursor = conn.cursor()

# Main products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT UNIQUE NOT NULL,
    parent_id TEXT DEFAULT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    embedding BLOB NOT NULL,
    color_hist BLOB,
    shape_feat BLOB,
    real_diameter_mm REAL DEFAULT 0.0,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Sales history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    price_per_unit REAL NOT NULL,
    total_amount REAL NOT NULL,
    sold_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Migrate existing DB — add missing columns if not present
try:
    cursor.execute("ALTER TABLE products ADD COLUMN color_hist BLOB")
except Exception:
    pass
try:
    cursor.execute("ALTER TABLE products ADD COLUMN shape_feat BLOB")
except Exception:
    pass
try:
    cursor.execute("ALTER TABLE products ADD COLUMN real_diameter_mm REAL DEFAULT 0.0")
except Exception:
    pass

conn.commit()
conn.close()

print("✅ Database ready (products + sales tables)")

try:
    cursor.execute("ALTER TABLE products ADD COLUMN parent_id TEXT DEFAULT NULL")
    print("✅ Added parent_id column")
except Exception:
    pass
