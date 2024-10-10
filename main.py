import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import calendar

# Connect to the database
conn = sqlite3.connect('haushaltsbuch.db')
cursor = conn.cursor()

# Create the tables if not already present
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS income (
    income_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    recurring BOOLEAN NOT NULL,
    frequency TEXT,
    category TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS expense (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    recurring BOOLEAN NOT NULL,
    frequency TEXT,
    category TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL
)
''')

conn.commit()

# Styling
def apply_minimal_style(widget):
    widget.config(font=("Helvetica", 12), relief=tk.FLAT, bd=0)  # Removed padx and pady
    widget.configure(highlightbackground="#d3d3d3", highlightcolor="#d3d3d3", borderwidth=0)

# Custom styling for rounded buttons and entry fields
def apply_curved_style(widget, bg_color, fg_color):
    widget.config(
        font=("Helvetica", 12), 
        bg=bg_color, fg=fg_color,
        relief=tk.FLAT, bd=0,
        highlightbackground=bg_color, 
        highlightcolor=bg_color
    )

# Create main window
root = tk.Tk()
root.geometry("800x480")
root.title("Haushaltsbuch")

# Function to enter user
def enter_user():
    user_name = entry_name.get().strip().capitalize()
    if not user_name:
        messagebox.showerror("Empty Field", "Please enter your name")
        return
    cursor.execute("SELECT user_id FROM user WHERE name = ?", (user_name,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO user (name) VALUES (?)", (user_name,))
        conn.commit()
    show_options(user_name)

# Function to show income/expense options
def show_options(user_name):
    for widget in root.winfo_children():
        widget.destroy()
    
    tk.Label(root, text=f"Willkommen, {user_name}!", font=("Helvetica", 14)).pack(pady=10)

    options_frame = tk.Frame(root)
    options_frame.pack(pady=20)

    income_button = tk.Button(options_frame, text="Income", command=lambda: show_transaction_form("income", user_name), width=20, bg="#28a745", fg="white")
    apply_curved_style(income_button, "#28a745", "white")
    income_button.pack(side=tk.LEFT, padx=20)

    expense_button = tk.Button(options_frame, text="Expenses", command=lambda: show_transaction_form("expense", user_name), width=20, bg="#dc3545", fg="white")
    apply_curved_style(expense_button, "#dc3545", "white")
    expense_button.pack(side=tk.LEFT, padx=20)

    # Create a frame for month and year selection
    selection_frame = tk.Frame(root)
    selection_frame.pack(pady=(10, 10))

    # Month selection
    month_label = tk.Label(selection_frame, text="Select Month:")
    month_label.pack(side=tk.LEFT, padx=(0, 5))  # Add some padding to the right

    month_combobox = ttk.Combobox(selection_frame, values=[f"{i:02d}" for i in range(1, 13)])  # Months from 01 to 12
    month_combobox.set(datetime.today().strftime('%m'))  # Set default to current month
    month_combobox.pack(side=tk.LEFT, padx=(0, 10))  # Add some padding to the right

    # Year selection
    year_label = tk.Label(selection_frame, text="Select Year:")
    year_label.pack(side=tk.LEFT, padx=(10, 5))  # Add padding on the left and right

    year_combobox = ttk.Combobox(selection_frame, values=[str(year) for year in range(2020, datetime.today().year + 1)])  # Years from 2020 to current year
    year_combobox.set(datetime.today().strftime('%Y'))  # Set default to current year
    year_combobox.pack(side=tk.LEFT, padx=(0, 10))  # Add some padding to the right

    # Refresh button
    refresh_button = tk.Button(selection_frame, text="Update", command=lambda: update_ledger(user_name))
    apply_curved_style(refresh_button, "lightgray", "black")
    refresh_button.pack(side=tk.LEFT, padx=(10, 0))  # Add padding to the left



    # Function to update the ledger
    def update_ledger(user_name):
        # Clear current entries in the tree
        for item in tree.get_children():
            tree.delete(item)
        
        selected_month = month_combobox.get()
        selected_year = year_combobox.get()

        total_income = 0.0
        total_expenses = 0.0

        cursor.execute(
            '''SELECT u.name, i.date, i.amount, NULL, i.category 
               FROM income i 
               JOIN user u ON i.user_id = u.user_id 
               WHERE strftime('%m', i.date) = ? AND strftime('%Y', i.date) = ?''',
            (selected_month, selected_year)
        )
        income_transactions = cursor.fetchall()

        cursor.execute(
            '''SELECT u.name, e.date, NULL, e.amount, e.category 
               FROM expense e 
               JOIN user u ON e.user_id = u.user_id 
               WHERE strftime('%m', e.date) = ? AND strftime('%Y', e.date) = ?''',
            (selected_month, selected_year)
        )
        expense_transactions = cursor.fetchall()

        for transaction in income_transactions:
            total_income += transaction[2]
            tree.insert("", "end", values=(transaction[0], transaction[1], f"{transaction[2]:.2f}", "", transaction[4]))

        for transaction in expense_transactions:
            total_expenses += transaction[3]
            tree.insert("", "end", values=(transaction[0], transaction[1], "", f"{transaction[3]:.2f}", transaction[4]))

        total_tree.item(total_tree.get_children()[0], values=("Total", "", f"{total_income:.2f}", f"{total_expenses:.2f}", f"{total_income - total_expenses:.2f}"))



    # Create a frame for the ledger
    ledger_frame = tk.Frame(root)
    ledger_frame.pack(pady=(20, 0), padx=10, fill=tk.BOTH, expand=True)

    # Create a frame to hold the Treeview and scrollbars
    tree_frame = tk.Frame(ledger_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    # Create Treeview for transactions
    columns = ("Name", "Date", "Income", "Expenses", "Category")
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c))

    # Add vertical scrollbar
    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=v_scrollbar.set)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Add horizontal scrollbar (shared for both trees)
    shared_h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=lambda *args: [tree.xview(*args), total_tree.xview(*args)])
    tree.configure(xscroll=shared_h_scrollbar.set)
    shared_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Get current month and year
    current_month = datetime.today().month
    current_year = datetime.today().year

    # Initialize total variables
    total_income = 0.0
    total_expenses = 0.0

    # Fetch all income transactions for the current month
    cursor.execute('''
        SELECT u.name, i.date, i.amount, NULL, i.category 
        FROM income i 
        JOIN user u ON i.user_id = u.user_id 
        WHERE strftime('%m', i.date) = ? AND strftime('%Y', i.date) = ?
    ''', (f'{current_month:02d}', str(current_year)))
    income_transactions = cursor.fetchall()

    # Fetch all expense transactions for the current month
    cursor.execute('''
        SELECT u.name, e.date, NULL, e.amount, e.category 
        FROM expense e 
        JOIN user u ON e.user_id = u.user_id 
        WHERE strftime('%m', e.date) = ? AND strftime('%Y', e.date) = ?
    ''', (f'{current_month:02d}', str(current_year)))
    expense_transactions = cursor.fetchall()

    # Insert income transactions
    for transaction in income_transactions:
        total_income += transaction[2]  # Add to total income
        tree.insert("", "end", values=(transaction[0], transaction[1], f"{transaction[2]:.2f}", "", transaction[4]))

    # Insert expense transactions
    for transaction in expense_transactions:
        total_expenses += transaction[3]  # Add to total expenses
        tree.insert("", "end", values=(transaction[0], transaction[1], "", f"{transaction[3]:.2f}", transaction[4]))

    # Create a separate frame for totals
    total_frame = tk.Frame(root)
    total_frame.pack(pady=(0, 20), padx=10)  # Ensure no padding here

    total_columns = ("Total","", "Income", "Expenses", "Balance")
    total_tree = ttk.Treeview(total_frame, columns=total_columns, show='', height=1)  # No header

    total_balance = total_income - total_expenses
    total_tree.insert("", "end", values=("Total","", f"{total_income:.2f}", f"{total_expenses:.2f}", f"{total_balance:.2f}"))

    total_tree.configure(xscroll=shared_h_scrollbar.set)
    total_tree.pack(fill=tk.X, padx=0, pady=0)

    total_tree.item(total_tree.get_children()[0], tags=("total_row",))
    total_tree.tag_configure("total_row", background="#e9ecef", font=("Helvetica", 12, "bold"))

    sort_column(tree, "Date")



def sort_column(tree, col):
    # Create a list of data for sorting
    data_list = [(tree.set(k, col), k) for k in tree.get_children('')]
    # Sort the data
    data_list.sort()
    # Rearrange the items in the treeview
    for index, (val, k) in enumerate(data_list):
        tree.move(k, '', index)




# Function to add a new category
def add_new_category():
    def save_category():
        new_category = category_entry.get().strip().capitalize()
        if new_category:
            cursor.execute("SELECT category_name FROM category WHERE category_name = ?", (new_category.capitalize(),))
            if cursor.fetchone():
                messagebox.showerror("Duplicate", "This category already exists.")
            else:
                cursor.execute("INSERT INTO category (category_name) VALUES (?)", (new_category,))
                conn.commit()
                messagebox.showinfo("Success", "Category added successfully!")
                popup.destroy()
                update_category_dropdown()  # Update the dropdown with the new category

    popup = tk.Toplevel(root)
    popup.title("Add New Category")
    popup.geometry("240x120")

    tk.Label(popup, text="Category Name:").pack(pady=10)
    category_entry = tk.Entry(popup)
    category_entry.pack(pady=10)

    save_button = tk.Button(popup, text="Save", command=save_category)
    apply_curved_style(save_button, "#28a745", "white")
    save_button.pack(pady=10)

# Function to update category dropdown
def update_category_dropdown():
    cursor.execute("SELECT DISTINCT category_name FROM category")
    categories = [row[0] for row in cursor.fetchall()]
    # Clear the existing values and update with new unique categories
    category_combobox['values'] = categories + ["Add New Category..."]

# Function to show form for income/expenses
def show_transaction_form(transaction_type, user_name):
    for widget in root.winfo_children():
        widget.destroy()

    # Set up grid layout
    form_frame = tk.Frame(root)
    form_frame.pack(pady=20)

    # Label for Transaction type
    tk.Label(form_frame, text=f"Add {transaction_type.capitalize()}", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=2, pady=10)

    # Amount field
    tk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky=tk.W)
    amount_entry = tk.Entry(form_frame)
    apply_curved_style(amount_entry, "white", "black")
    amount_entry.grid(row=1, column=1, padx=10, pady=5)  # Added padding to grid

    # Date field with default to current date
    tk.Label(form_frame, text="Date (DD-MM-YYYY):").grid(row=2, column=0, sticky=tk.W)
    date_entry = tk.Entry(form_frame)
    apply_curved_style(date_entry, "white", "black")
    date_entry.insert(0, datetime.today().strftime('%d-%m-%Y'))  # Set the default date
    date_entry.grid(row=2, column=1, padx=10, pady=5)  # Added padding to grid

    # Description field
    tk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky=tk.W)
    description_entry = tk.Entry(form_frame)
    apply_curved_style(description_entry, "white", "black")
    description_entry.grid(row=3, column=1, padx=10, pady=5)  # Added padding to grid

    # Category dropdown field
    tk.Label(form_frame, text="Category:").grid(row=4, column=0, sticky=tk.W)
    global category_combobox
    category_combobox = ttk.Combobox(form_frame)
    update_category_dropdown()
    category_combobox.grid(row=4, column=1, padx=10, pady=5)
    category_combobox.bind("<<ComboboxSelected>>", lambda e: add_new_category() if category_combobox.get() == "Add New Category..." else None)

    # Recurring field as radio buttons
    tk.Label(form_frame, text="Repeat Transaction:").grid(row=5, column=0, sticky=tk.W)
    recurring_var = tk.StringVar(value="No")
    radio_frame = tk.Frame(form_frame)
    tk.Radiobutton(radio_frame, text="Yes", variable=recurring_var, value="Yes").pack(side=tk.LEFT)
    tk.Radiobutton(radio_frame, text="No", variable=recurring_var, value="No").pack(side=tk.LEFT)
    radio_frame.grid(row=5, column=1, sticky=tk.W)

    # Frequency field as a dropdown
    tk.Label(form_frame, text="Frequency:").grid(row=6, column=0, sticky=tk.W)
    frequency_combobox = ttk.Combobox(form_frame, values=["Annual", "Monthly", "Weekly"], state="disabled")
    frequency_combobox.grid(row=6, column=1, padx=10, pady=5)

    # Toggle frequency dropdown based on recurring radio button
    def toggle_frequency():
        if recurring_var.get() == "Yes":
            frequency_combobox.config(state="normal")
        else:
            frequency_combobox.config(state="disabled")

    recurring_var.trace_add('write', lambda *args: toggle_frequency())


    def submit_transaction():
        amount = amount_entry.get().strip()
        date = date_entry.get().strip()
        description = description_entry.get().strip()
        category = category_combobox.get().strip()
        recurring = recurring_var.get() == "Yes"
        frequency = frequency_combobox.get().strip()

        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid positive number for amount.")
            return

        # Validate date format
        try:
            transaction_date = datetime.strptime(date, '%d-%m-%Y').date()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter the date in the format DD-MM-YYYY.")
            return

        if recurring:
            # Determine how many occurrences to add
            time_last = 0
            if frequency == "Weekly":
                time_last = 4  # For the next 4 weeks
                delta = timedelta(weeks=1)
            elif frequency == "Monthly":
                time_last = 3  # For the next 3 months
                delta = timedelta(days=30)  # Roughly approximates one month
            elif frequency == "Annual":
                time_last = 1  # For the next year
                delta = timedelta(days=365)  # Roughly approximates one year

            for i in range(time_last):
                next_date = transaction_date + (delta * i)
                if transaction_type == "income":
                    cursor.execute('''INSERT INTO income (amount, date, description, recurring, frequency, category, user_id)
                                    VALUES (?, ?, ?, ?, ?, ?, (SELECT user_id FROM user WHERE name = ?))''',
                                (amount, next_date.strftime('%Y-%m-%d'), description, recurring, frequency, category, user_name))
                else:
                    cursor.execute('''INSERT INTO expense (amount, date, description, recurring, frequency, category, user_id)
                                    VALUES (?, ?, ?, ?, ?, ?, (SELECT user_id FROM user WHERE name = ?))''',
                                (amount, next_date.strftime('%Y-%m-%d'), description, recurring, frequency, category, user_name))

        else:
            # If not recurring, just add the transaction once
            if transaction_type == "income":
                cursor.execute('''INSERT INTO income (amount, date, description, recurring, frequency, category, user_id)
                                VALUES (?, ?, ?, ?, ?, ?, (SELECT user_id FROM user WHERE name = ?))''',
                            (amount, transaction_date.strftime('%Y-%m-%d'), description, recurring, frequency, category, user_name))
            else:
                cursor.execute('''INSERT INTO expense (amount, date, description, recurring, frequency, category, user_id)
                                VALUES (?, ?, ?, ?, ?, ?, (SELECT user_id FROM user WHERE name = ?))''',
                            (amount, transaction_date.strftime('%Y-%m-%d'), description, recurring, frequency, category, user_name))

        conn.commit()
        messagebox.showinfo("Success", f"{transaction_type.capitalize()} added successfully!")
        show_options(user_name)


    # Submit and Back buttons
    submit_button = tk.Button(form_frame, text="Submit", command=submit_transaction)
    apply_curved_style(submit_button, "#28a745", "white")
    submit_button.grid(row=7, column=0, pady=20)

    back_button = tk.Button(form_frame, text="Back", command=lambda: show_options(user_name))
    apply_curved_style(back_button, "#007bff", "white")
    back_button.grid(row=7, column=1, pady=20)

# Initial Screen to enter the user's name
label_name = tk.Label(root, text="Enter Your Name:", font=("Helvetica", 14))
label_name.pack(pady=20)

entry_name = tk.Entry(root)
apply_minimal_style(entry_name)
entry_name.pack(pady=10)

button_enter = tk.Button(root, text="Enter", command=enter_user)
apply_curved_style(button_enter, "gray", "white")
button_enter.pack(pady=10)

# Bind the Enter key for submitting the name
root.bind('<Return>', lambda event: enter_user())

root.mainloop()












