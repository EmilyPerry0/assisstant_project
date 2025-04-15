from dotenv import load_dotenv
import os
import requests
import json
import time
import logging

load_dotenv('../.env')

API_KEY = os.getenv('WEATHER_API_KEY')
BASE_URL = os.getenv('BASE_URL')
CACHE_FILE = "cached_information/weather_cache.json"  # File to store cached data
CACHE_EXPIRY = 3600  # Cache expires in 1 hour (3600 seconds)

logger = logging.getLogger('weather')

def get_weekly_weather():
    lat = os.getenv('LAT')
    lon = os.getenv("LON")
    # Check if cached data exists
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cached_data = json.load(f)
            # Check if cache is still valid
            if time.time() - cached_data["timestamp"] < CACHE_EXPIRY:
                logger.debug("Using cached weather data.")
                return cached_data["data"]
    else:
        logger.debug('weather_cache.json path not found')
    
    logger.debug("Fetching new weather data from API...")
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "minutely,hourly",
        "units": "metric",
        "appid": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # Cache the response with a timestamp
        with open(CACHE_FILE, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
        return data
    else:
        logger.debug("Error:", response.status_code, response.text)
        return None
    