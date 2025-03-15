import requests

API_KEY = 'YOUR_WEATHER_API_KEY'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

def get_weather(city):
    try:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return temp, description
        else:
            return None, None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None, None
