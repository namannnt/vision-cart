import sqlite3
from datetime import datetime

class BillingSystem:
    """
    Billing and inventory management system
    """
    
    def __init__(self):
        self.bill = []
        self.added_products = set()  # Track already added products
    
    def add_to_bill(self, product_id, price):
        """
        Add item to bill (only once per session)
        """
        if product_id not in self.added_products:
            self.bill.append({
                'product_id': product_id,
                'price': price,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            self.added_products.add(product_id)
            return True
        return False
    
    def update_stock(self, product_id, db_path="database/visioncart.db"):
        """
        Decrease stock by 1
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE products
            SET stock = stock - 1
            WHERE product_id = ?
        """, (product_id,))
        
        conn.commit()
        conn.close()
    
    def check_low_stock(self, product_id, threshold=3, db_path="database/visioncart.db"):
        """
        Check if stock is low
        Returns: (is_low, current_stock)
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT stock FROM products WHERE product_id=?", (product_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            stock = result[0]
            is_low = stock <= threshold
            return is_low, stock
        
        return False, 0
    
    def get_total(self):
        """
        Calculate total bill amount
        """
        return sum(item['price'] for item in self.bill)
    
    def get_bill_summary(self):
        """
        Get formatted bill summary
        """
        if len(self.bill) == 0:
            return "No items in cart"
        
        summary = "\n" + "="*50 + "\n"
        summary += "BILL SUMMARY\n"
        summary += "="*50 + "\n"
        
        for i, item in enumerate(self.bill, 1):
            summary += f"{i}. {item['product_id']:<20} Rs.{item['price']:>8.2f} ({item['timestamp']})\n"
        
        summary += "="*50 + "\n"
        summary += f"TOTAL: Rs.{self.get_total():.2f}\n"
        summary += "="*50 + "\n"
        
        return summary
    
    def clear_bill(self):
        """
        Clear current bill
        """
        self.bill.clear()
        self.added_products.clear()
