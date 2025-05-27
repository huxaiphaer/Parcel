import logging
import os

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city):
    cache_key = f"weather_{city.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        # Get coordinates
        geo_params = {"q": city, "limit": 1, "appid": API_KEY}
        geo_response = requests.get(GEOCODE_URL, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            raise ValueError(f"No coordinates found for {city}")

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Get weather using lat/lon
        weather_params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
        }
        weather_response = requests.get(WEATHER_URL, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        result = {
            "temp": weather_data["main"]["temp"],
            "description": weather_data["weather"][0]["description"],
        }

        cache.set(cache_key, result, timeout=7200)
        return result

    except Exception as e:
        logger.error(f"Failed to fetch weather for {city}: {e}")
        return {"temp": None, "description": "Weather not available"}
