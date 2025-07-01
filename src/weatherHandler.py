from dotenv import load_dotenv
import os
import requests
import json
import time
import logging
from datetime import datetime, timedelta, timezone

load_dotenv('.env')

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
        "exclude": "minutely",
        "units": "metric",
        "appid": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    
    from datetime import datetime, timedelta

    # Assume `data` is your API response JSON
    timezone_offset = response["timezone_offset"]
    hourly_data = response["hourly"]

    # Get the local date for now
    now_local = datetime.now(timezone.utc) + timedelta(seconds=timezone_offset)
    today = now_local.date()

    # Collect hourly temps for today only
    today_hourly_data = [
        h for h in hourly_data
        if (datetime.fromtimestamp(h['dt'], tz=timezone.utc) + timedelta(seconds=timezone_offset)).date() == today
    ]

    
    if response.status_code == 200:
        data = response.json()
        data['today_hourly_data'] = today_hourly_data
        # Cache the response with a timestamp
        with open(CACHE_FILE, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
        return data
    else:
        logger.debug("Error:", response.status_code, response.text)
        return None
    
print(get_weekly_weather()['today_hourly_data'])