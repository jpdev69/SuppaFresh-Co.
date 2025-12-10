import tkinter as tk
from tkinter import ttk, messagebox
from inventory_manager import InventoryManager, Product
from optimizer import SupplyChainOptimizer

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SuppaFresh Co. Inventory System (Fixed Inventory Mode)")
        self.root.geometry("1000x700")
        
        # Initialize Logic
        self.manager = InventoryManager()
        self.optimizer = SupplyChainOptimizer()
        
        # Setup Tabs
        self.tab_control = ttk.Notebook(root)
        
        self.tab_inventory = ttk.Frame(self.tab_control)
        self.tab_restock = ttk.Frame(self.tab_control)
        self.tab_optimize = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_inventory, text='Current Inventory')
        self.tab_control.add(self.tab_restock, text='Restock Inventory')
        self.tab_control.add(self.tab_optimize, text='Optimization Report')
        
        self.tab_control.pack(expand=1, fill="both")
        
        self._build_inventory_tab()
        self._build_restock_tab()
        self._build_optimize_tab()

    def _build_inventory_tab(self):
        # Frame for controls
        control_frame = ttk.Frame(self.tab_inventory)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        refresh_btn = ttk.Button(control_frame, text="Refresh List", command=self.refresh_inventory_list)
        refresh_btn.pack(side="left")
        
        # Treeview for Listing
        columns = ("SKU", "Name", "Category", "Size", "Color", "Price", "Cost", "Qty", "Demand")
        self.tree = ttk.Treeview(self.tab_inventory, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Initial Load
        self.refresh_inventory_list()

    def refresh_inventory_list(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        products = self.manager.list_products()
        for p in products:
            # p is a tuple: (sku, name, category, size, color, price, cost, quantity, lead_time, reorder_point, demand)
            display_values = (p[0], p[1], p[2], p[3], p[4], f"${p[5]:.2f}", f"${p[6]:.2f}", p[7], p[10])
            self.tree.insert("", "end", values=display_values)

    def _build_restock_tab(self):
        form_frame = ttk.LabelFrame(self.tab_restock, text="Restock Existing Items")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Refresh SKUs for the dropdown
        existing_products = self.manager.list_products()
        # Create list of "SKU - Name" for readability
        self.sku_options = [f"{p[0]} - {p[1]}" for p in existing_products]
        
        # SKU Selection
        lbl_sku = ttk.Label(form_frame, text="Select Product:")
        lbl_sku.grid(row=0, column=0, padx=10, pady=20, sticky="w")
        
        self.sku_var = tk.StringVar()
        self.sku_combo = ttk.Combobox(form_frame, textvariable=self.sku_var, values=self.sku_options, width=50)
        self.sku_combo.grid(row=0, column=1, padx=10, pady=20)
        
        # Quantity
        lbl_qty = ttk.Label(form_frame, text="Quantity to Add:")
        lbl_qty.grid(row=1, column=0, padx=10, pady=20, sticky="w")
        
        self.qty_var = tk.StringVar(value="0")
        qty_entry = ttk.Entry(form_frame, textvariable=self.qty_var, width=20)
        qty_entry.grid(row=1, column=1, padx=10, pady=20, sticky="w")
        
        # Save Button
        save_btn = ttk.Button(form_frame, text="Update Stock", command=self.perform_restock)
        save_btn.grid(row=2, column=1, pady=30, sticky="w")
        
        # Instructions
        note = ttk.Label(form_frame, text="Note: This will increase the current stock level by the entered amount.", font=("Arial", 8, "italic"))
        note.grid(row=3, column=0, columnspan=2, pady=10)

    def perform_restock(self):
        try:
            selection = self.sku_var.get()
            if not selection:
                messagebox.showerror("Error", "Please select a product.")
                return
                
            qty_str = self.qty_var.get()
            if not qty_str.isdigit():
                 messagebox.showerror("Error", "Quantity must be a positive integer.")
                 return
                 
            qty = int(qty_str)
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0.")
                return
            
            # Extract SKU from "SKU - Name" string
            sku = selection.split(" - ")[0]
            
            self.manager.restock_product(sku, qty)
            messagebox.showinfo("Success", f"Successfully added {qty} units to {sku}.")
            
            # Reset and refresh
            self.qty_var.set("0")
            self.refresh_inventory_list()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _build_optimize_tab(self):
        control_frame = ttk.Frame(self.tab_optimize)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        run_btn = ttk.Button(control_frame, text="Run Optimization Analysis", command=self.run_optimization)
        run_btn.pack(side="left")
        
        columns = ("SKU", "Name", "Curr Qty", "Demand", "EOQ (Order Size)", "New ROP", "Action")
        self.opt_tree = ttk.Treeview(self.tab_optimize, columns=columns, show='headings')
        
        for col in columns:
            self.opt_tree.heading(col, text=col)
            self.opt_tree.column(col, width=120)
            
        self.opt_tree.pack(expand=True, fill="both", padx=10, pady=10)

    def run_optimization(self):
        for item in self.opt_tree.get_children():
            self.opt_tree.delete(item)
            
        products = self.manager.list_products()
        for p in products:
            sku, name, cat, size, color, price, cost, qty, lead_time, current_rop, annual_demand = p
            
            eoq = self.optimizer.calculate_eoq(annual_demand, cost)
            new_rop = self.optimizer.calculate_reorder_point(annual_demand, lead_time)
            
            action = "OK"
            tags = ()
            if qty <= new_rop:
                action = f"ORDER {eoq}"
                tags = ('reorder',)
            
            values = (sku, name, qty, annual_demand, eoq, new_rop, action)
            self.opt_tree.insert("", "end", values=values, tags=tags)
            
        self.opt_tree.tag_configure('reorder', background='#ffcccc')

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
