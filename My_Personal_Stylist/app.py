import os
from flask import Flask, render_template, request, redirect, url_for, flash
from auth import auth
from weather_api import get_weather
from image_analysis import analyze_outfit
from wardrobe import add_item, get_wardrobe
from PIL import Image

# Initialize Flask App
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')  

# ---------------------- ADD ITEM ROUTE ----------------------
@app.route('/add_item', methods=['GET', 'POST'])
def add_item_page():
    if request.method == 'POST':
        category = request.form['category']
        color = request.form['color']
        image = request.files['image']

        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            add_item(user_id=1, category=category, color=color, image_path=image_path)
        
        return redirect(url_for('auth.wardrobe'))

    return render_template('add_item.html')

# ---------------------- WARDROBE ROUTE ----------------------
@app.route('/wardrobe')
def wardrobe():
    items = get_wardrobe(user_id=1)
    return render_template('wardrobe.html', items=items)

# ---------------------- OUTFIT SUGGESTION FUNCTION ----------------------
def suggest_outfit(temp, description):
    if temp < 10:
        return "Wear warm clothes like a jacket, sweater, and boots."
    elif temp < 20:
        return "A light jacket or a hoodie would be perfect."
    elif temp < 30:
        return "Go for casual wear like t-shirts and jeans."
    else:
        return "Light and breathable fabrics are best. Try shorts and a sleeveless top."

# ---------------------- HOME ROUTE (WEATHER & IMAGE UPLOAD) ----------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    weather_info, outfit_suggestion, uploaded_image = None, None, None

    if request.method == 'POST':
        # Weather Data Handling
        if 'city' in request.form:
            city = request.form['city']
            temp, description = get_weather(city)
            if temp is not None:
                weather_info = f"Current Weather in {city}: {temp}°C, {description}"
                outfit_suggestion = suggest_outfit(temp, description)
            else:
                weather_info = f"Sorry, weather data for '{city}' not found."

        # Image Upload Handling
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(image_path)
                uploaded_image = image_path

                # Outfit suggestion based on image analysis
                outfit_suggestion = analyze_outfit(image_path)

    return render_template('index.html', 
                           weather_info=weather_info, 
                           outfit_suggestion=outfit_suggestion,
                           uploaded_image=uploaded_image)

# ---------------------- SIGNUP PAGE ROUTE ----------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # For now, just print (Later you can connect it to a database)
        print(f"New User Registered: {username}")

        flash("Account created successfully!", "success")
        return redirect(url_for('auth.wardrobe'))

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
