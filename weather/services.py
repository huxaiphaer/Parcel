import os
import requests
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    cache_key = f"weather_{city.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        if not API_KEY:
            raise ValueError("Weather API key not set")

        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        result = {
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }

        cache.set(cache_key, result, timeout=7200)
        return result

    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {e}", exc_info=True)
        raise

    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing weather API response: {e}", exc_info=True)
        raise
