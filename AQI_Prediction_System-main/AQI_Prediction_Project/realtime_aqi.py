import requests
import os

API_KEY = "24a818d2037d1cab6775201ce6c34f77"   

def get_live_aqi(city):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        geo_res = requests.get(geo_url).json()

        if not geo_res:
            return None, "City not found"

        lat = geo_res[0]["lat"]
        lon = geo_res[0]["lon"]

        api_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        data = requests.get(api_url).json()

        aqi_index = data["list"][0]["main"]["aqi"]  # 1 to 5

        # Convert OpenWeather AQI Scale to Standard AQI
        mapping = {
            1: ("Good", 50),
            2: ("Fair", 100),
            3: ("Moderate", 200),
            4: ("Poor", 300),
            5: ("Very Poor", 400)
        }

        status, approx_aqi = mapping.get(aqi_index)
        return approx_aqi, status

    except Exception as e:
        return None, str(e)
