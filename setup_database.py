import sqlite3

# Create a connection to the database file (creates it if it doesn't exist)
conn = sqlite3.connect('database/finance.db')  # Make sure 'database' folder exists
cursor = conn.cursor()

# Create users table with id, username, and password
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ Database setup complete.")
