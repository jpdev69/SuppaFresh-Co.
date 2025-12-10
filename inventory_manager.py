import sqlite3
import datetime
from typing import List, Optional

class Product:
    def __init__(self, sku: str, name: str, category: str, size: str, color: str, 
                 price: float, cost: float, quantity: int, 
                 lead_time_days: int = 7, reorder_point: int = 10):
        self.sku = sku
        self.name = name
        self.category = category
        self.size = size
        self.color = color
        self.price = price
        self.cost = cost
        self.quantity = quantity
        self.lead_time_days = lead_time_days
        self.reorder_point = reorder_point

    def __repr__(self):
        return f"<Product {self.sku} ({self.name})>"

class InventoryManager:
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                size TEXT NOT NULL,
                color TEXT NOT NULL,
                price REAL NOT NULL,
                cost REAL NOT NULL,
                quantity INTEGER NOT NULL,
                lead_time_days INTEGER DEFAULT 7,
                reorder_point INTEGER DEFAULT 10
            )
        ''')
        conn.commit()
        conn.close()

    def add_product(self, product: Product):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (sku, name, category, size, color, price, cost, quantity, lead_time_days, reorder_point)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (product.sku, product.name, product.category, product.size, product.color, 
                  product.price, product.cost, product.quantity, 
                  product.lead_time_days, product.reorder_point))
            conn.commit()
            print(f"Added product: {product.name} ({product.sku})")
        except sqlite3.IntegrityError:
            print(f"Error: Product with SKU {product.sku} already exists.")
        finally:
            conn.close()

    def list_products(self) -> List[tuple]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_low_stock_items(self) -> List[tuple]:
        """Identifies items that are at or below their reorder point."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE quantity <= reorder_point')
        rows = cursor.fetchall()
        conn.close()
        return rows

if __name__ == "__main__":
    # Simple test
    manager = InventoryManager()
    print("Database initialized.")
