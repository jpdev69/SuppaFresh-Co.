import math
from inventory_manager import InventoryManager

class SupplyChainOptimizer:
    def __init__(self, db_path: str = "inventory.db", holding_cost_percent: float = 0.20, order_cost: float = 50.0):
        self.manager = InventoryManager(db_path)
        self.holding_cost_percent = holding_cost_percent
        self.order_cost = order_cost

    def calculate_eoq(self, annual_demand: int, unit_cost: float) -> int:
        """
        Calculates Economic Order Quantity (EOQ).
        Formula: sqrt((2 * Demand * OrderCost) / HoldingCost)
        """
        if annual_demand <= 0 or unit_cost <= 0:
            return 0
        
        holding_cost_per_unit = unit_cost * self.holding_cost_percent
        eoq = math.sqrt((2 * annual_demand * self.order_cost) / holding_cost_per_unit)
        return int(round(eoq))

    def calculate_reorder_point(self, annual_demand: int, lead_time_days: int) -> int:
        """
        Calculates Reorder Point (ROP).
        Formula: (Average Daily Demand * Lead Time)
        Note: We are not adding Safety Stock in this basic version.
        """
        if annual_demand <= 0:
            return 0
            
        daily_demand = annual_demand / 365.0
        rop = daily_demand * lead_time_days
        return int(math.ceil(rop))

    def generate_optimization_report(self):
        products = self.manager.list_products()
        # Schema: sku, name, category, size, color, price, cost, quantity, lead_time, reorder_point, annual_demand
        
        print(f"{'SKU':<15} | {'Name':<20} | {'Curr Qty':<8} | {'Demand':<8} | {'EOQ':<5} | {'New ROP':<7} | {'Action'}")
        print("-" * 100)
        
        for p in products:
            sku, name, cat, size, color, price, cost, qty, lead_time, current_rop, annual_demand = p
            
            eoq = self.calculate_eoq(annual_demand, cost)
            new_rop = self.calculate_reorder_point(annual_demand, lead_time)
            
            action = "OK"
            if qty <= new_rop:
                action = f"ORDER {eoq}"
            
            print(f"{sku:<15} | {name:<20} | {qty:<8} | {annual_demand:<8} | {eoq:<5} | {new_rop:<7} | {action}")

if __name__ == "__main__":
    optimizer = SupplyChainOptimizer()
    optimizer.generate_optimization_report()
