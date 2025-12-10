from inventory_manager import InventoryManager, Product

def seed_data():
    manager = InventoryManager()
    
    # Define the initial product list based on user requirements
    # Categories: Casual Tops, Layering/Outerwear, Formal
    
    products_to_add = [
        # Casual Tops
        Product("SL-SH-M-BLK", "Sleeveless Shirt", "Casual Tops", "M", "Black", 25.00, 10.00, 50, estimated_annual_demand=500),
        Product("TS-SH-L-WHT", "Basic T-Shirt", "Casual Tops", "L", "White", 20.00, 5.00, 100, estimated_annual_demand=1200),
        Product("VN-SH-M-GRY", "V-Neck Shirt", "Casual Tops", "M", "Grey", 22.00, 6.00, 80, estimated_annual_demand=800),
        Product("PL-SH-L-NVY", "Classic Polo", "Casual Tops", "L", "Navy", 35.00, 12.00, 60, estimated_annual_demand=600),
        Product("JS-SP-XL-RED", "Sport Jersey", "Casual Tops", "XL", "Red", 45.00, 15.00, 40, estimated_annual_demand=300),
        
        # Layering / Outerwear
        Product("TN-LS-M-BLK", "Cotton Turtleneck", "Outerwear", "M", "Black", 40.00, 18.00, 30, estimated_annual_demand=200),
        Product("HD-ZK-L-GRY", "Zip-Up Hoody", "Outerwear", "L", "Grey", 55.00, 25.00, 45, estimated_annual_demand=400),
        Product("JK-LT-L-BRN", "Leather Jacket", "Outerwear", "L", "Brown", 150.00, 80.00, 15, lead_time_days=14, estimated_annual_demand=100),
        Product("SW-CR-M-BLU", "Crewneck Sweatshirt", "Outerwear", "M", "Blue", 45.00, 20.00, 50, estimated_annual_demand=350),
        
        # Formal
        Product("TX-CL-L-BLK", "Classic Tuxedo", "Formal", "L", "Black", 250.00, 120.00, 10, lead_time_days=21, reorder_point=5, estimated_annual_demand=50)
    ]

    print("Seeding database...")
    for p in products_to_add:
        manager.add_product(p)
    
    print("\n--- Current Inventory ---")
    all_items = manager.list_products()
    for item in all_items:
        # item is a tuple, index 0 is sku, 1 is name, 7 is quantity
        print(f"SKU: {item[0]} | Name: {item[1]} | Qty: {item[7]}")

if __name__ == "__main__":
    seed_data()
