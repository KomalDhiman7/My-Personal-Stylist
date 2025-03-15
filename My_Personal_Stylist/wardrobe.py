# wardrobe.py

import sqlite3

DB_PATH = "database.db"

def add_item(user_id, category, color, image_path):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wardrobe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT,
                color TEXT,
                image_path TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO wardrobe (user_id, category, color, image_path)
            VALUES (?, ?, ?, ?)
        """, (user_id, category, color, image_path))
        conn.commit()

def get_wardrobe(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wardrobe WHERE user_id=?", (user_id,))
        return cursor.fetchall()
