import os
import sqlite3
from random import choice
from flask import Flask, render_template, request, redirect, url_for, flash, session
from auth import auth
from weather_api import get_weather
from image_analysis import analyze_outfit
from PIL import Image
from datetime import timedelta


# ---------------------- Flask Config ----------------------

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.permanent_session_lifetime = timedelta(days=30)


# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')

# ---------------------- Helper: Get Random Wardrobe Item ----------------------
def get_random_wardrobe_item(username):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, image_path FROM wardrobe WHERE username=?", (username,))
        items = cursor.fetchall()
        if items:
            return choice(items)
    return None

# ---------------------- Add Item Route (via /add_item.html) ----------------------
@app.route('/add_item', methods=['GET', 'POST'])
def add_item_page():
    if request.method == 'POST':
        category = request.form.get('category')
        color = request.form.get('color')
        image = request.files['image']

        if image and image.filename != '':
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image.save(image_path)

            # Save to database using the correct session user
            username = session.get('username', 'guest')
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO wardrobe (username, item_name, image_path) VALUES (?, ?, ?)",
                               (username, category, image_path))
                conn.commit()

        return redirect('/')

    return render_template('add_item.html')

# ---------------------- Suggest Outfit Based on Temperature ----------------------
def suggest_outfit(temp, description):
    if temp < 10:
        return "Wear warm clothes like a jacket, sweater, and boots."
    elif temp < 20:
        return "A light jacket or a hoodie would be perfect."
    elif temp < 30:
        return "Go for casual wear like t-shirts and jeans."
    else:
        return "Light and breathable fabrics are best. Try shorts and a sleeveless top."

# ---------------------- Home Route (Weather + Outfit) ----------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    weather_info, outfit_suggestion, uploaded_image, today_outfit = None, None, None, None
    username = session.get('username')

    if request.method == 'POST':
        # Weather
        if 'city' in request.form:
            city = request.form['city']
            temp, description = get_weather(city)
            if temp is not None:
                weather_info = f"Current Weather in {city}: {temp}°C, {description}"
                outfit_suggestion = suggest_outfit(temp, description)
                if username:
                    today_outfit = get_random_wardrobe_item(username)

        # Outfit Image Upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                image.save(image_path)
                uploaded_image = image_path
                outfit_suggestion = analyze_outfit(image_path)

    return render_template('index.html',
                           weather_info=weather_info,
                           outfit_suggestion=outfit_suggestion,
                           uploaded_image=uploaded_image,
                           today_outfit=today_outfit)



# ---------------------- Start App ----------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
