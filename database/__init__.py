"""
Database management for VisionCart
"""
import sqlite3
import json
from pathlib import Path

class VisionCartDB:
    def __init__(self, db_path="database/visioncart.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_product(self, product_id, price, stock, embedding, image_path=None):
        """Add product to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO products (product_id, price, stock, embedding, image_path) VALUES (?, ?, ?, ?, ?)",
            (product_id, price, stock, embedding.tobytes(), image_path)
        )
        
        conn.commit()
        conn.close()
    
    def get_all_products(self):
        """Retrieve all products"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        
        conn.close()
        return products
    
    def get_all_embeddings(self):
        """Get all embeddings for similarity matching"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT product_id, embedding FROM products")
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def product_exists(self, product_id):
        """Check if product already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE product_id = ?", (product_id,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
