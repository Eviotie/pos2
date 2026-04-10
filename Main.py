import csv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


#Can be used for either csv
def read(file_path, headers):
    try:
        with open(file_path, mode='r', newline='') as file:
            return [row for row in csv.reader(file)]
    except FileNotFoundError:
        return [headers]

def save():
    with open('data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Quantity", "Sell price", "buy price"])
        for row_id in table.get_children():
            writer.writerow(table.item(row_id)['values'])


#Adds sale to history and updates ui
def save_sale_to_history(product_name, price):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    sale_data = [timestamp, product_name, price]
    
    with open('sales.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(sale_data)
    
    history_table.insert("", "0", values=sale_data)


#allows you to add products to invetory
def add_product():
    vals = (entry_name.get(), entry_stock.get(), entry_sell_price.get(), entry_price.get())
    if all(vals):
        table.insert("", "end", values=vals)
        save()
        for ent in [entry_name, entry_stock, entry_sell_price, entry_price]: ent.delete(0, tk.END)

def add_to_cart():
    selected = table.selection()
    if not selected: 
        return messagebox.showwarning("Selection", "Select a product first.")
    
    item_data = table.item(selected[0])['values']
    name, qty, sell_price = item_data[0], int(item_data[1]), item_data[2]
    
    if qty <= 0: 
        return messagebox.showerror("Out of Stock", f"{name} is out of stock!")

    cart_table.insert("", "end", values=(name, sell_price))
    new_total = float(label_total_val.cget("text")) + float(sell_price)
    label_total_val.config(text=f"{new_total:.2f}")

#checkouts includes saving to history clearing cart and updating inventory
def checkout():
    if not cart_table.get_children(): 
        return

    for cart_item in cart_table.get_children():
        p_name, p_price = cart_table.item(cart_item)['values']
        
        for inv_item in table.get_children():
            inv_row = table.item(inv_item)['values']
            if str(inv_row[0]) == str(p_name):
                table.set(inv_item, column="col1", value=int(inv_row[1]) - 1)
                break
        
        save_sale_to_history(p_name, p_price)
        cart_table.delete(cart_item)
    
    save()
    label_total_val.config(text="0.00")
    messagebox.showinfo("Success", "Sale Completed and Recorded")




# Setup Data
data = read('data.csv', ["Name", "Quantity", "Sell price", "buy price"])
history_data = read('sales.csv', ["Timestamp", "Product", "Price"])

root = tk.Tk()
root.title("Inventory / Sales system")
root.geometry("1000x750")

nb = ttk.Notebook(root)
nb.pack(fill="both", expand=True)

tab_inventory = ttk.Frame(nb)
tab_sales = ttk.Frame(nb)
tab_history = ttk.Frame(nb)
nb.add(tab_inventory, text="Product Inventory")
nb.add(tab_sales, text="Checkout")
nb.add(tab_history, text="Sales History")






#INVENTORY
input_frame = tk.Frame(tab_inventory)
input_frame.pack(pady=10)
tk.Label(input_frame, text="Name:").grid(row=0, column=0)
entry_name = tk.Entry(input_frame); entry_name.grid(row=0, column=1, padx=5)
tk.Label(input_frame, text="Quantity:").grid(row=0, column=2)
entry_stock = tk.Entry(input_frame); entry_stock.grid(row=0, column=3, padx=5)
tk.Label(input_frame, text="Sell Price:").grid(row=0, column=4)
entry_sell_price = tk.Entry(input_frame); entry_sell_price.grid(row=0, column=5, padx=5)
tk.Label(input_frame, text="Buy Price:").grid(row=0, column=6)
entry_price = tk.Entry(input_frame); entry_price.grid(row=0, column=7, padx=5)
tk.Button(input_frame, text="Add Product", command=add_product).grid(row=1, column=0, columnspan=8, pady=10)

inv_frame = tk.Frame(tab_inventory)
inv_frame.pack(fill="both", expand=True, padx=20)
sb_inv = ttk.Scrollbar(inv_frame)
sb_inv.pack(side="right", fill="y")
table = ttk.Treeview(inv_frame, columns=("col0","col1","col2","col3"), show="headings", yscrollcommand=sb_inv.set)
for i, h in enumerate(data[0]):
    table.heading(f"col{i}", text=h)
    table.column(f"col{i}", width=120)
for row in data[1:]: table.insert("", "end", values=row)
table.pack(fill="both", expand=True)
sb_inv.config(command=table.yview)
tk.Button(tab_inventory, text="ADD SELECTED TO CART", bg="green", command=add_to_cart).pack(pady=10)




#CHECKOUT
sales_frame = tk.Frame(tab_sales)
sales_frame.pack(fill="both", expand=True, padx=20, pady=20)
cart_table = ttk.Treeview(sales_frame, columns=("Name", "Price"), show="headings")
cart_table.heading("Name", text="Product"); cart_table.heading("Price", text="Price")
cart_table.pack(fill="both", expand=True)
label_total_val = tk.Label(sales_frame, text="0.00", font=("Arial", 14, "bold"))
label_total_val.pack(pady=10)
tk.Button(sales_frame, text="COMPLETE SALE", bg="green", command=checkout).pack()



#HISTORY
hist_frame = tk.Frame(tab_history)
hist_frame.pack(fill="both", expand=True, padx=20, pady=20)
sb_hist = ttk.Scrollbar(hist_frame)
sb_hist.pack(side="right", fill="y")
history_table = ttk.Treeview(hist_frame, columns=("Time", "Prod", "Price"), show="headings", yscrollcommand=sb_hist.set)
history_table.heading("Time", text="Time of Sale")
history_table.heading("Prod", text="Product")
history_table.heading("Price", text="Amount")
history_table.column("Time", width=200)
for row in history_data[1:]: history_table.insert("", "0", values=row)
history_table.pack(fill="both", expand=True)
sb_hist.config(command=history_table.yview)

root.mainloop()