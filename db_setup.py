import sqlite3
import os

# Make sure the 'database' folder exists
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect("database/finance.db")
cursor = conn.cursor()

# Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Categories table
cursor.execute('''
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('income', 'expense')) NOT NULL
)
''')

# Transactions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL NOT NULL,
    category_id INTEGER,
    date TEXT NOT NULL,
    note TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
)
''')

# Add default categories if empty
cursor.execute("SELECT COUNT(*) FROM categories")
if cursor.fetchone()[0] == 0:
    categories = [
        ('Salary', 'income'),
        ('Gift', 'income'),
        ('Food', 'expense'),
        ('Rent', 'expense'),
        ('Transport', 'expense')
    ]
    cursor.executemany("INSERT INTO categories (name, type) VALUES (?, ?)", categories)

conn.commit()
conn.close()
print("✅ Database setup complete.")
