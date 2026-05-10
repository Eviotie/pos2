import csv #our bootleg database
import tkinter as tk #the big tk that allows us to display stuff
from tkinter import ttk, messagebox, filedialog  #ttk is for the notebook (tabs) and treeview, messagebox is for popups, filediaolg for selecting business
from datetime import datetime #allows to timestamp stuff
import os # file miniplation



data_path = 'data.csv'
sales_path = 'sales.csv'

#Opens csv and rows into lsit
def read(file_path, headers):
    try:
        with open(file_path, mode='r', newline='') as file:
            return [row for row in csv.reader(file)]
    except FileNotFoundError:
        return [headers]


#Copys the current table data to the data csv file
def save():
    global data_path
    with open(data_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Quantity", "Sell price", "buy price"])
        for row_id in table.get_children():
            writer.writerow(table.item(row_id)['values'])

def save_sale_to_history(cart_items): #cart items is a list of items in the cart ex: [["Apple", "0.5"], ["Orange", "0.75"], ["Apple", "0.5"]]
    if not cart_items:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M") #timespamp for the sale
    total = sum(float(item[1]) for item in cart_items) # total by suming everything in cart

    # Count # of each item ex:{'Apple': 2, 'Orange': 1}
    itemsseenonce = {}
    for item in cart_items:
        if item[0] not in itemsseenonce:
            itemsseenonce[item[0]] = 1
        else:
            itemsseenonce[item[0]] += 1

    #gets item cost for each item {'Apple': 0.5, 'Orange': 0.75}
    item_prices = {}
    for item in cart_items:
        if item[0] not in item_prices:
            item_prices[item[0]] = item[1]

    #formats the string and combines it
    formatted_items = []
    for name, count in itemsseenonce.items():
        price = item_prices.get(name, 0) # gets the price key
        formatted_items.append(f"{name} x{count} (${price})")
    
    #creates the final line pizza x2 ($20) | bread x1 ($10)
    items_str = " | ".join(formatted_items)
    
    #add sales
    global sales_path
    with open(sales_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, items_str, f"{total:.2f}"]) #:.2f rounds floats to 2 decimal places

    #adds to history table
    if 'history_table' in globals():
        history_table.insert("", "0", values=[timestamp, items_str, f"${total:.2f}"])


#grabs all the value from the 4 texts boxes, ands a new row to the table, then runs save() to update the csv 
def add_product():
    vals = (entry_name.get(), entry_stock.get(), entry_sell_price.get(), entry_price.get())
    if all(vals):
        table.insert("", "end", values=vals)
        save()
        for ent in [entry_name, entry_stock, entry_sell_price, entry_price]:
            ent.delete(0, tk.END)

#user clicks on row then enter # of stock to add, then updates the table and csv with new stock value
def add_stock():
    selected = table.selection()
    if not selected: 
        return messagebox.showwarning("Selection", "Select a product first.")

    item_data = table.item(selected[0])['values']
    additional = entry_stock.get()
    if bool(additional):
        value = int(item_data[1]) + int(additional)
        table.item(selected[0], values=(item_data[0], str(value), item_data[2], item_data[3]))
        save()
        entry_stock.delete(0, tk.END)

#Waits for user to select a row then checks if there is enough stock, if there is it adds to the cart_table, and upades total
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
    label_total_val.config(text=f"{new_total:.2f}")  #updates total price isntalty

#When user clicks checkout, it checks if there is items in the cart, if there is it updates the inventory table and csv, adds the sale to the history csv and table, then clears the cart and resets total
def checkout():
    if not cart_table.get_children():
        return

    cart_items = []
    for cart_item in cart_table.get_children():
        p_name, p_price = cart_table.item(cart_item)['values']
        cart_items.append([p_name, p_price])

        for inv_item in table.get_children():
            inv_row = table.item(inv_item)['values']
            if str(inv_row[0]) == str(p_name):
                table.set(inv_item, column="col1", value=int(inv_row[1]) - 1)
                break

        cart_table.delete(cart_item)

    save_sale_to_history(cart_items)
    save()
    label_total_val.config(text="0.00")
    messagebox.showinfo("Success", "Sale Completed and Recorded")


#bootleg data base, reads the inventory and sales csv files, then calculates daily revenue, cost, and quantity sold, then updates the data analysis table with the results
def analyze_data():
    # creates a look up dictionary for items so u can find the Buy/sell price for any item
    fresh_inventory = read(data_path, ["Name", "Quantity", "Sell price", "buy price"])
    inventory = {}
    for row in fresh_inventory[1:]: #data.csv skiping header
        if len(row) >= 4:
            inventory[row[0]] = {
                'sell_price': float(row[2]),
                'buy_price': float(row[3].strip())
            }

    daily_stats = {} #daily total
    sales_data = read(sales_path, ["Timestamp", "Items", "Total"])

    # Iterate through sales records to group revenue and items by date
    # Changed to process all rows if the first row looks like data (starts with a digit)
    first_char = sales_data[0][0][0]
    if first_char.isdigit():
        start_index = 0
    else:
        start_index = 1
    
    for row in sales_data[start_index:]:
        if len(row) < 3:
            continue

        day = row[0].split(" ")[0]
        items_str = row[1]
        
        # Strip potential currency symbols before converting to float
        revenue_str = row[2].replace('$', '').replace(',', '')
        total_revenue = float(revenue_str)

        if day not in daily_stats:
            daily_stats[day] = {'revenue': 0.0, 'cost': 0.0, 'quantity': 0}

        daily_stats[day]['revenue'] += total_revenue

        #parsing spliting up strings to find total cost of goods
        items_list = items_str.split(" | ") #breaks the items apart 
        for item in items_list:
            item = item.strip()
            if " x" in item:
                # breaks "item x4 ($10)" -> ["item", "4 ($10)"]
                parts = item.split(" x")
                name = parts[0].strip()
                
                #breaks "4 ($10)" -> ["4", "($10)"]
                remainder = parts[1].strip()
                qty_str = remainder.split(" ")[0]
                
                #gets rid of any non digit characters, just in case
                qty_str = "".join(filter(str.isdigit, qty_str))
                
                if qty_str:
                    qty = int(qty_str)
                    daily_stats[day]['quantity'] += qty

                    if name in inventory:
                        buy_price = inventory[name]['buy_price']
                        daily_stats[day]['cost'] += (buy_price * qty)
    
    #saves data / refreshes table
    for item in data_table.get_children():
        data_table.delete(item)

    for day in sorted(daily_stats.keys()):
        stats = daily_stats[day]
        data_table.insert("", "end", values=[
            day,
            f"${stats['revenue']:.2f}", 
            f"${stats['cost']:.2f}",
            stats['quantity']
        ])

# allows to run analyze data when user clicks on the data analysis tab
def on_tab_changed(event):
    if event.widget.nametowidget(event.widget.select()) == tab_data:
        analyze_data()
def indeptanalysis():
    selected = data_table.selection()
    if not selected: 
        return messagebox.showwarning("Selection", "Select a day first.")
    
    day = data_table.item(selected[0])['values'][0]
    revenue = {}
    current_history = read(sales_path, ["Timestamp", "Items", "Total"])

    for row in current_history:
        if len(row) >= 3 and row[0][:10] == day:
            hour = row[0][11:13]
            total = float(row[2].replace('$', ''))
            revenue[hour] = revenue.get(hour, 0) + total
    
    # 0s
    for i in range(24):
        h = f"{i:02d}"
        if h not in revenue:
            revenue[h] = 0.0
    # Simple bar chart in new window
    win = tk.Toplevel(root)
    win.title(day)
    win.geometry("820x450")
    canvas = tk.Canvas(win, width=800, height=400, bg='white')
    canvas.pack()
    
    canvas.create_line(50, 350, 750, 350, width=2)   #x axis (x1, y1, x2,y2)
    canvas.create_line(50, 350, 50, 50, width=2) #y axis
    max_revenue = max(revenue.values()) 
    #side numbers and the lines with them
    canvas.create_text(20, 50, text=f"${max_revenue:.2f}", anchor="center") 
    canvas.create_line(50,50,750,50, dash=(1,4))
    canvas.create_text(20, 300*.75+50, text=f"${max_revenue*.25:.2f}", anchor="center") 
    canvas.create_line(50,300*.75+50,750,300*.75+50, dash=(1,4))
    canvas.create_text(20, 300/2+50, text=f"${max_revenue/2:.2f}", anchor="center")
    canvas.create_line(50,300/2+50,750,300/2+50, dash=(1,4))
    canvas.create_text(20, 300*.25+50, text=f"${max_revenue*.75:.2f}", anchor="center") 
    canvas.create_line(50,300*.25+50,750,300*.25+50, dash=(1,4))


    # the bar meathod
    for i in range(24):
        h = f"{i:02d}" #i but 2 digit
        rev = revenue[f"{i:02d}"] 
        if max_revenue > 0:
            bar_height = (rev / max_revenue) * 300
        else:
            bar_height = 0
        canvas.create_rectangle(50 + i*30, 350 - bar_height, 80 + i*30, 350, fill='blue')
        canvas.create_text(65 + i*30, 360, text=h)




    #print(revenue)

def refresh_all_tables():
    # Clear every table to start fresh
    for t in [table, history_table, data_table, cart_table]:
        for item in t.get_children():
            t.delete(item)

    # Reload Inventory Table
    inv_rows = read(data_path, ["Name", "Quantity", "Sell price", "buy price"])
    for row in inv_rows[1:]: 
        table.insert("", "end", values=row)

    # Reload Sales History
    sales_rows = read(sales_path, ["Timestamp", "Items", "Total"])
    if sales_rows and len(sales_rows) > 0:
        # Determine if we skip header: check if first char of first col is a digit
        start = 0 if sales_rows[0][0][0].isdigit() else 1
        for row in sales_rows[start:]:
            if len(row) >= 3:
                history_table.insert("", "end", values=row)

    # Reset checkout total
    label_total_val.config(text="0.00")

def select():
    global data_path, sales_path
    file_dir = filedialog.askdirectory()
    if not file_dir:
        return

    expected_data = os.path.join(file_dir, 'data.csv')
    expected_sales = os.path.join(file_dir, 'sales.csv')

    if os.path.isfile(expected_data) and os.path.isfile(expected_sales):
        data_path = expected_data
        sales_path = expected_sales
        refresh_all_tables()
    else:
        tk.messagebox.showinfo("Error", "The folder you selected doesn't contain both data.csv and sales.csv")

def create_business():
    global data_path, sales_path
    name = entry_new_biz.get().strip()
    if not name:
        return messagebox.showwarning("Input Error", "Please enter a business name.")
    
    os.makedirs("Data")
    new_path = os.path.join("Data", name)
    
    if os.path.exists(new_path):
        return messagebox.showerror("Error", "A business with this name already exists!")
    
    # Create directory and empty CSVs with headers
    os.makedirs(new_path)
    with open(os.path.join(new_path, 'data.csv'), 'w', newline='') as f:
        csv.writer(f).writerow(["Name", "Quantity", "Sell price", "buy price"])

    
    # Automatically switch to the new business
    data_path = os.path.join(new_path, 'data.csv')
    sales_path = os.path.join(new_path, 'sales.csv')
    refresh_all_tables()
    entry_new_biz.delete(0, tk.END)
    messagebox.showinfo("Success", f"Created and Loaded: {name}")

        

data = read(data_path, ["Name", "Quantity", "Sell price", "buy price"])
history_data = read(sales_path, ["Timestamp", "Items", "Total"])

root = tk.Tk()
root.title("Inventory / Sales system")
root.geometry("1000x750")

style = ttk.Style()
style.theme_use('clam') 
style.configure('TButton', background='white', font=('Helvetica', 12))

nb = ttk.Notebook(root)
nb.pack(fill="both", expand=True)

tab_inventory = ttk.Frame(nb)
tab_sales = ttk.Frame(nb)
tab_history = ttk.Frame(nb)
tab_data = ttk.Frame(nb)
tab_select = ttk.Frame(nb)

nb.add(tab_inventory, text="Product Inventory")
nb.add(tab_sales, text="Checkout")
nb.add(tab_history, text="Sales History")
nb.add(tab_data, text="Data Analysis")
nb.add(tab_select, text="Select Business")

# INVENTORY
input_frame = tk.Frame(tab_inventory)
input_frame.pack(pady=10)
tk.Label(input_frame, text="Name:").grid(row=0, column=0)
entry_name = tk.Entry(input_frame)
entry_name.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="Quantity:").grid(row=0, column=2)
entry_stock = tk.Entry(input_frame)
entry_stock.grid(row=0, column=3, padx=5)

tk.Label(input_frame, text="Sell Price:").grid(row=0, column=4)
entry_sell_price = tk.Entry(input_frame)
entry_sell_price.grid(row=0, column=5, padx=5)

tk.Label(input_frame, text="Buy Price:").grid(row=0, column=6)
entry_price = tk.Entry(input_frame)
entry_price.grid(row=0, column=7, padx=5)
tk.Button(input_frame, text="Add New Product", command=add_product).grid(row=1, column=0, columnspan=8, pady=10)
tk.Button(input_frame, text="Add Additional Stock", command=add_stock).grid(row=2, column=0, columnspan=8, pady=10)

inv_frame = tk.Frame(tab_inventory)
inv_frame.pack(fill="both", expand=True, padx=20)
sb_inv = ttk.Scrollbar(inv_frame)
sb_inv.pack(side="right", fill="y")
table = ttk.Treeview(inv_frame, columns=("col0","col1","col2","col3"), show="headings", yscrollcommand=sb_inv.set)
for i, h in enumerate(data[0]):
    table.heading(f"col{i}", text=h)
    table.column(f"col{i}", width=120)

for row in data[1:]:
    table.insert("", "end", values=row)
table.pack(fill="both", expand=True)
sb_inv.config(command=table.yview)
tk.Button(tab_inventory, text="ADD SELECTED TO CART", bg="green", command=add_to_cart).pack(pady=10)

# CHECKOUT
sales_frame = tk.Frame(tab_sales)
sales_frame.pack(fill="both", expand=True, padx=20, pady=20)
cart_table = ttk.Treeview(sales_frame, columns=("Name", "Price"), show="headings")
cart_table.heading("Name", text="Product")
cart_table.heading("Price", text="Price")
cart_table.pack(fill="both", expand=True)
label_total_val = tk.Label(sales_frame, text="0.00", font=("Arial", 14, "bold"))
label_total_val.pack(pady=10)
tk.Button(sales_frame, text="COMPLETE SALE", bg="green", command=checkout).pack()

# HISTORY
hist_frame = tk.Frame(tab_history)
hist_frame.pack(fill="both", expand=True, padx=20, pady=20)
sb_hist = ttk.Scrollbar(hist_frame)
sb_hist.pack(side="right", fill="y")
history_table = ttk.Treeview(hist_frame, columns=("Time", "Items", "Total"), show="headings", yscrollcommand=sb_hist.set)
history_table.heading("Time", text="Time of Sale")
history_table.heading("Items", text="Items")
history_table.heading("Total", text="Total")
history_table.column("Time", width=120)
history_table.column("Items", width=500)
history_table.column("Total", width=100)

history_table.pack(fill="both", expand=True)

#refreshs history table firt time
for row in history_data:
    if len(row) >= 3:
        history_table.insert("", "end", values=row)



sb_hist.config(command=history_table.yview)

# DATA ANALYSIS
data_frame = tk.Frame(tab_data)

data_frame.pack(fill="both", expand=True, padx=20, pady=20)
dt_hist = ttk.Scrollbar(tab_data)
dt_hist.pack(side="right", fill="y")
data_table = ttk.Treeview(data_frame, columns=("Day", "In", "Out", "#of items"), show="headings", yscrollcommand=dt_hist.set)
data_table.heading("Day", text="Day")
data_table.heading("In", text="In")
data_table.heading("Out", text="Out")
data_table.heading("#of items", text="# of Items")

data_table.pack(fill="both", expand=True)
dt_hist.config(command=data_table.yview)
tk.Button(tab_data, text="More Info", command=indeptanalysis).pack()


#choose your buinesss

select_frame = tk.Frame(tab_select)
#select_frame.pack(fill="both", expand=True, padx=20, pady=20)
tk.Label(tab_select, text="CREATE NEW BUSINESS", font=("Arial", 12, "bold")).pack(pady=(20,5))
entry_new_biz = tk.Entry(tab_select, font=("Arial", 12), width=30)
entry_new_biz.pack(pady=5)
tk.Button(tab_select, bg="blue", fg="white", text="Create Business", command=create_business).pack(pady=5)

tk.Label(tab_select, text="OR", font=("Arial", 10)).pack(pady=10)

tk.Button(tab_select, bg="green", fg="white", text="Select Existing Business Folder", command=select).pack(pady=5)
tk.Button(tab_select, text="Refresh All Data", command=refresh_all_tables).pack(pady=20)
nb.bind("<<NotebookTabChanged>>", on_tab_changed) #makes the bummy datta analsys tab run a function
root.mainloop()