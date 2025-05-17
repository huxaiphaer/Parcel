import os

import requests
from django.core.cache import cache

API_KEY = os.getenv('')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    cache_key = f"weather_{city.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    result = {
        "temp": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }

    cache.set(cache_key, result, timeout=7200)  # Cache for 2 hours
    return result
