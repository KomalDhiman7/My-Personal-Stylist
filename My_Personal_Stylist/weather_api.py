import requests

API_KEY = '56c845eb908d61f92aebecf35d8b7802'
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    try:
        params = {
            'q': city + ',IN',  # Adding country code for accuracy
            'appid': API_KEY,
            'units': 'metric'
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description'].capitalize()  # Capitalizing description
            return temp, description
        else:
            print("API Error:", data.get("message", "Unknown error"))
            return None, None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None, None

# Example usage
city = "Jalandhar"
temp, description = get_weather(city)

if temp is not None:
    print(f"Current Weather in {city}: {temp}°C, {description}")
else:
    print(f"Sorry, weather data for '{city}' not found.")
