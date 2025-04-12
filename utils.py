import sqlite3

def extract_year(date_str):
    try:
        return int(date_str.split('/')[-1])
    except:
        return None

def extract_month(date_str):
    try:
        return int(date_str.split('/')[1])
    except:
        return None

def guess_category(data):
    provider = data.provider.lower()

    with sqlite3.connect("bills.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories")
        categories = [row[0].lower() for row in cursor.fetchall()]

    for cat in categories:
        if cat in provider:
            return cat
    return "misc"