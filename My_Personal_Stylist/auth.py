from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3

auth = Blueprint('auth', __name__)

# Database setup
DB_PATH = "database.db"

# Create database and table
def create_user_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL
                        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS wardrobe (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT,
                            item_name TEXT,
                            image_path TEXT
                        )''')

create_user_table()

# Signup route
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Check if user exists
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if user:
                session['username'] = username
                return redirect(url_for('wardrobe'))

            # Add new user
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()

            session['username'] = username
            return redirect(url_for('wardrobe'))

    return render_template('signup.html')

# Wardrobe route
@auth.route('/wardrobe', methods=['GET'])
def wardrobe():
    username = session.get('username')
    if not username:
        return redirect(url_for('auth.signup'))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wardrobe WHERE username=?", (username,))
        wardrobe_items = cursor.fetchall()

    return render_template('wardrobe.html', username=username, wardrobe_items=wardrobe_items)

# Add Item route
@auth.route('/add_item', methods=['POST'])
def add_item():
    username = session.get('username')
    if not username:
        return redirect(url_for('auth.signup'))

    item_name = request.form['item_name']
    image = request.files['image']

    if image.filename != '':
        image_path = f"static/images/{image.filename}"
        image.save(image_path)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO wardrobe (username, item_name, image_path) VALUES (?, ?, ?)",
                           (username, item_name, image_path))
            conn.commit()

    return redirect(url_for('auth.wardrobe'))
