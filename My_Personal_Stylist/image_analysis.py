from PIL import Image
import numpy as np

def analyze_outfit(image_path):
    img = Image.open(image_path).resize((224, 224)).convert('RGB')
    img_array = np.array(img)

    # Calculate average RGB color
    avg_color = img_array.mean(axis=(0, 1))
    r, g, b = avg_color.astype(int)

    # Logic based on average color
    if r > g and r > b:
        return "This outfit has dominant red tones. Try pairing with beige or black accessories."
    elif g > r and g > b:
        return "Green outfit vibes! Earthy or neutral tones will complement well."
    elif b > r and b > g:
        return "Blue tones detected. Consider pairing with whites or greys."
    elif r < 80 and g < 80 and b < 80:
        return "Dark outfit spotted. Add contrast with lighter accessories or bright shoes."
    else:
        return "Neutral tones — feel free to style boldly with statement pieces!"
