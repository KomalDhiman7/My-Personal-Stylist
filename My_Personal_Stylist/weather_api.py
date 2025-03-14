import requests

API_KEY = "YOUR_OPENWEATHER_API_KEY"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get('main'):
        return data['main']['temp'], data['weather'][0]['description']
    else:
        return None, "City not found"
