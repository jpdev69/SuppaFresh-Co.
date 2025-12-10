import sqlite3
import datetime
from typing import List, Optional

class Product:
    def __init__(self, sku: str, name: str, category: str, size: str, color: str, 
                 price: float, cost: float, quantity: int, 
                 lead_time_days: int = 7, reorder_point: int = 10,
                 estimated_annual_demand: int = 0):
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
        self.estimated_annual_demand = estimated_annual_demand

    def __repr__(self):
        return f"<Product {self.sku} ({self.name})>"

class InventoryManager:
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Note: simplistic schema migration (drop if exists for development speed)
        # In a real app we'd use migrations, but for this proto we'll just check/create
        # or rely on the user to delete the db if schema changes drastically.
        # Adding the column to the create statement:
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
                reorder_point INTEGER DEFAULT 10,
                estimated_annual_demand INTEGER DEFAULT 0
            )
        ''')
        
        # Create Sales Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                revenue REAL NOT NULL,
                FOREIGN KEY(sku) REFERENCES products(sku)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_product(self, product: Product):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO products (sku, name, category, size, color, price, cost, quantity, lead_time_days, reorder_point, estimated_annual_demand)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (product.sku, product.name, product.category, product.size, product.color, 
                  product.price, product.cost, product.quantity, 
                  product.lead_time_days, product.reorder_point,
                  product.estimated_annual_demand))
            conn.commit()
            print(f"Added/Updated product: {product.name} ({product.sku})")
        except sqlite3.IntegrityError:
            print(f"Error: Product with SKU {product.sku} already exists.")
        finally:
            conn.close()

    def restock_product(self, sku: str, amount: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET quantity = quantity + ? WHERE sku = ?', (amount, sku))
        conn.commit()
        conn.close()
        print(f"Restocked SKU {sku} by {amount}")

    def record_sale(self, sku: str, quantity: int) -> bool:
        """
        Records a sale: reduces stock and logs the transaction.
        Returns True if successful, False if insufficient stock.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check stock
        cursor.execute('SELECT quantity, price FROM products WHERE sku = ?', (sku,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError("Product not found")
            
        current_qty, price = row
        if current_qty < quantity:
            conn.close()
            return False
            
        # Deduct stock
        cursor.execute('UPDATE products SET quantity = quantity - ? WHERE sku = ?', (quantity, sku))
        
        # Record sale
        revenue = price * quantity
        cursor.execute('INSERT INTO sales (sku, quantity, revenue) VALUES (?, ?, ?)', (sku, quantity, revenue))
        
        conn.commit()
        conn.close()
        print(f"Sold {quantity} of {sku} for ${revenue:.2f}")
        return True

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
