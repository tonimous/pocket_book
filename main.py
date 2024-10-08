import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

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
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
)
''')

conn.commit()

# Styling
def apply_minimal_style(widget):
    widget.config(font=("Helvetica", 12), padx=10, pady=5)

# Create main window
root = tk.Tk()
root.geometry("800x480")
root.title("Household Budget")

# Function to enter user
def enter_user():
    user_name = entry_name.get().strip()
    if not user_name:
        messagebox.showerror("Error", "Please enter your name")
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

    tk.Label(root, text=f"Welcome, {user_name}!", font=("Helvetica", 14)).pack(pady=10)

    # Buttons for Income and Expense
    def show_income_form():
        show_transaction_form("income", user_name)
    
    def show_expense_form():
        show_transaction_form("expense", user_name)

    tk.Button(root, text="Income", command=show_income_form, width=20).place(x=100, y=150)
    tk.Button(root, text="Expenses", command=show_expense_form, width=20).place(x=500, y=150)

# Function to show form for income/expenses
def show_transaction_form(transaction_type, user_name):
    for widget in root.winfo_children():
        widget.destroy()

    # Label for Transaction type
    tk.Label(root, text=f"Add {transaction_type.capitalize()}", font=("Helvetica", 14)).pack(pady=10)

    # Amount field
    tk.Label(root, text="Amount:").pack()
    amount_entry = tk.Entry(root)
    amount_entry.pack()

    # Date field
    tk.Label(root, text="Date (YYYY-MM-DD):").pack()
    date_entry = tk.Entry(root)
    date_entry.pack()

    # Description field
    tk.Label(root, text="Description:").pack()
    description_entry = tk.Entry(root)
    description_entry.pack()

    # Recurring field
    tk.Label(root, text="Recurring (Yes/No):").pack()
    recurring_entry = tk.Entry(root)
    recurring_entry.pack()

    # Frequency field as a dropdown
    tk.Label(root, text="Frequency:").pack()
    frequency_combobox = ttk.Combobox(root, values=["Annual", "Monthly", "Weekly"])
    frequency_combobox.pack()

    def submit_transaction():
        amount = amount_entry.get().strip()
        date = date_entry.get().strip()
        description = description_entry.get().strip()
        recurring = recurring_entry.get().strip().lower() == "yes"
        frequency = frequency_combobox.get().strip()

        if not amount or not date:
            messagebox.showerror("Error", "Amount and Date are required")
            return

        cursor.execute("SELECT user_id FROM user WHERE name = ?", (user_name,))
        user_id = cursor.fetchone()[0]

        if transaction_type == "income":
            cursor.execute('''
                INSERT INTO income (amount, date, description, recurring, frequency, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (amount, date, description, recurring, frequency, user_id))
        else:
            cursor.execute('''
                INSERT INTO expense (amount, date, description, recurring, frequency, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (amount, date, description, recurring, frequency, user_id))

        conn.commit()
        messagebox.showinfo("Success", f"{transaction_type.capitalize()} added successfully!")
        show_options(user_name)

    tk.Button(root, text="Submit", command=submit_transaction).pack(pady=10)

# User entry screen
tk.Label(root, text="Enter your name:", font=("Helvetica", 14)).pack(pady=10)
entry_name = tk.Entry(root)
entry_name.pack()
tk.Button(root, text="Submit", command=enter_user).pack(pady=10)

root.mainloop()






