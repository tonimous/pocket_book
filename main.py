import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox


conn = sqlite3.connect('haushaltskasse.db')
c = conn.cursor()

# create user table
c.execute('''CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL)''')

# create expenses table
c.execute('''CREATE TABLE IF NOT EXISTS expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    recurring BOOLEAN NOT NULL,
    frequency TEXT,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
    FOREIGN KEY (category_id) REFERENCES category(category_id))''')

# create income table
c.execute('''CREATE TABLE IF NOT EXISTS income (
    income_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    recurring BOOLEAN NOT NULL,
    frequency TEXT,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
    FOREIGN KEY (category_id) REFERENCES category(category_id))''')

# create category table
c.execute('''CREATE TABLE IF NOT EXISTS category (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL)''')

conn.commit()

# GUI setup
root = tk.Tk()
root.title("Haushaltsbuch")
root.geometry("800x480")

# styling for app
style_bg_color = "#f5f5f7"
style_entry_bg = "#f0f0f5"
style_font = ("Helvetica Neue", 14)
style_button_active = "#005bb5"
style_button_color = "#007aff"
style_text_color = "#1d1d1f"


# add user function

def add_user():
    name = name_entry.get()
    if name:
        c.execute("INSERT INTO user (name) VALUES (?)", (name,))
        conn.commit()
        name_entry.delete(0, tk.END)
        messagebox.showinfo("Erfolg", "Benutzer erfolgreich hinzugefügt")
    else:
        messagebox.showwarning("Fehler", "Bitte gib einen Namen ein")

# styling widgets
def style_widgets(widget, font, bg=style_bg_color, fg=style_text_color):
    widget.configure(font=font, bg=bg, fg=fg)

def style_button(button):
    button.configure(activebackground=style_button_active, activeforeground="white", bg=style_button_color, font=style_font, fg="white", relief="flat", bd=0)

# add user input GUI
name_label = tk.Label(root, text="Benutzername:")
style_widgets(name_label, style_font)
name_label.pack(pady=10)
name_entry = tk.Entry(root, font=style_font, bg="lightgray", fg=style_text_color, relief="flat")
name_entry.pack(pady=10, ipady=5, ipadx=10)
add_button = tk.Button(root, text="Benutzer hinzufügen", command=add_user)
style_button(add_button)
add_button.pack(pady=20)

#mainloop
root.mainloop()

# close connection
conn.close()
