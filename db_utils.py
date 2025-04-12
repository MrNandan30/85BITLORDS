import sqlite3 
from pathlib import Path

DB_PATH = "bills.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Bills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                date TEXT,
                amount REAL,
                provider TEXT,
                category TEXT,
                year INTEGER,
                month INTEGER,
                needs_review BOOLEAN
            )
        """)
        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY
            )
        """)
        # Custom fields per category
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                field_name TEXT,
                field_type TEXT DEFAULT 'text',
                FOREIGN KEY (category) REFERENCES categories(name)
            )
        """)
        # Manual field value suggestions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manual_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT,
                field_value TEXT,
                UNIQUE(field_name, field_value)
            )
        """)
        conn.commit()

def insert_bill(data):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO bills (filename, date, amount, provider, category, year, month, needs_review)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['filename'], data['date'], data['amount'], data['provider'],
                data['category'], data['year'], data['month'], data['needs_review']
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"[SKIP] Duplicate file skipped: {data['filename']}")
            return False

def get_bills_by_category(category=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT * FROM bills WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM bills")
        return cursor.fetchall()

def insert_category(name):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
        conn.commit()

def get_all_categories():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories")
        return [row[0] for row in cursor.fetchall()]

def delete_category(name):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE name = ?", (name,))
        cursor.execute("DELETE FROM bills WHERE category = ?", (name,))
        conn.commit()

def delete_bill(bill_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
        conn.commit()

def save_manual_entry(field_name, field_value):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO manual_entries (field_name, field_value) VALUES (?, ?)",
                (field_name, field_value)
            )
            conn.commit()
        except Exception as e:
            print("Failed to save manual entry:", e)

def get_manual_suggestions(field_name):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT field_value FROM manual_entries WHERE field_name = ?", (field_name,))
        return [row[0] for row in cursor.fetchall()]

def get_db_connection():
    return sqlite3.connect(DB_PATH)