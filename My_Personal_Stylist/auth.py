from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

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
    if session.get('username'):
        return redirect(url_for('auth.wardrobe'))

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if user:
                return render_template('signup.html', error="Username already exists")

            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()

        session['username'] = username
        return redirect(url_for('auth.wardrobe'))

    return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('auth.wardrobe'))

    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):  # user[2] = hashed password
                session['username'] = username
                if remember:
                    session.permanent = True
                return redirect(url_for('auth.wardrobe'))
            else:
                error = "Invalid credentials. Please try again."

    return render_template('login.html', error=error)




@auth.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))




# Wardrobe route
@auth.route('/wardrobe', methods=['GET'])
def wardrobe():
    username = session.get('username')
    if not username:
        return redirect(url_for('auth.signup'))

    filter_type = request.args.get('filter_type')
    filter_value = request.args.get('filter_value')

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if filter_type and filter_value:
            query = f"SELECT * FROM wardrobe WHERE username=? AND {filter_type} LIKE ?"
            cursor.execute(query, (username, f"%{filter_value}%"))
        else:
            cursor.execute("SELECT * FROM wardrobe WHERE username=?", (username,))
        wardrobe_items = cursor.fetchall()

    return render_template('wardrobe.html', username=username, wardrobe_items=wardrobe_items)

@auth.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('auth.login'))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wardrobe WHERE id=? AND username=?", (item_id, username))
        conn.commit()

    return redirect(url_for('auth.wardrobe'))

@auth.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('auth.login'))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        if request.method == 'POST':
            new_name = request.form['item_name']
            cursor.execute("UPDATE wardrobe SET item_name=? WHERE id=? AND username=?", (new_name, item_id, username))
            conn.commit()
            return redirect(url_for('auth.wardrobe'))

        cursor.execute("SELECT * FROM wardrobe WHERE id=? AND username=?", (item_id, username))
        item = cursor.fetchone()
        if not item:
            return "Item not found or unauthorized."

    return render_template('edit_item.html', item=item)


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
