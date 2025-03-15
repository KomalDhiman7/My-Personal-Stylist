import sqlite3

def create_tables():
    conn = sqlite3.connect('wardrobe.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Wardrobe table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wardrobe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT NOT NULL,
        color TEXT,
        image_path TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database setup complete!")
