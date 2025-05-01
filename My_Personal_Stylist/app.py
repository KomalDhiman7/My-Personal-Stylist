import os
import sqlite3
from random import choice
from flask import Flask, render_template, request, redirect, url_for, flash, session
from auth import auth
from weather_api import get_weather
from image_analysis import analyze_outfit
from PIL import Image
from datetime import timedelta
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# ---------------------- Flask Config ----------------------

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.permanent_session_lifetime = timedelta(days=30)

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            # Save the file in the uploads folder
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            uploaded_image = file_path  # Or process as required
            return render_template('upload.html', uploaded_image=uploaded_image)
        else:
            return "No file selected", 400
    return render_template('upload.html')

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

# ---------------------- Home Route (Homepage with Navbar) ----------------------
@app.route('/')
def homepage():
    return render_template('home.html')



@app.route('/profile')
def profile():
    # Example: Assuming the profile page needs user info from session
    if 'username' in session:
        username = session['username']
        return render_template('profile.html', username=username)
    else:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # Update username and email
        session['username'] = request.form['username']
        session['email'] = request.form['email']
        
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                # Secure the filename to avoid security risks
                filename = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filename)
                session['profile_pic'] = filename  # Store the file path in session

        return redirect(url_for('profile'))

    return render_template('edit_profile.html')




# ---------------------- Suggestion Route (Weather + Outfit) ----------------------
@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
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
