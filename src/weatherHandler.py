from dotenv import load_dotenv
import os
import requests
import json
import time
import logging
from datetime import datetime, timedelta, timezone

load_dotenv('.env')

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("BASE_URL")
API_KEY2 = os.getenv('WEATHER_API_KEY2')
BASE_URL2 = os.getenv('BASE_URL2')
CACHE_FILE_DAILY = "cached_information/weather_cache_daily.json"  # File to store cached data
CACHE_FILE_HOURLY = "cached_information/weather_cache_hourly.json"  # File to store cached data
CACHE_FILE_SUMMARY = "cached_information/weather_cache_summary.json"
CACHE_EXPIRY = 3600  # Cache expires in 1 hour (3600 seconds)
LOCAL_OFFSET_HOURS = int(os.getenv('LOCAL_OFFSET_HOURS'))

logger = logging.getLogger('weather')

def get_hourly_weather():
    lat = os.getenv('LAT')
    lon = os.getenv("LON")
    # Check if cached data exists
    if os.path.exists(CACHE_FILE_HOURLY):
        with open(CACHE_FILE_HOURLY, "r") as f:
            cached_data = json.load(f)
            # Check if cache is still valid
            if time.time() - cached_data["timestamp"] < CACHE_EXPIRY:
                logger.debug("Using cached weather data.")
                return cached_data["data"]
    else:
        logger.debug('weather_cache.json path not found')
    
    logger.debug("Fetching new weather data from API...")
    params = {
        "location":f"{lat},{lon}",
        "timesteps":"1h",
        "units": "metric",
        "apikey": API_KEY2
    }

    response = requests.get(BASE_URL2, params=params)

    
    if response.status_code == 200:
        data = response.json()
        hourly_data = data['timelines']['hourly']
        # Construct the hourly data with a timezone offset
        today_hourly = []

        for hour in hourly_data:
            dt_utc = datetime.fromisoformat(hour["time"].replace("Z", "+00:00"))
            if is_today_local(dt_utc):
                today_hourly.append(hour)
        
        data['today_hourly'] = today_hourly
        
        with open(CACHE_FILE_HOURLY, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
        return data
    else:
        logger.debug("Error:", response.status_code, response.text)
        return None
    
def is_today_local(dt_utc: datetime) -> bool:
    dt_local = dt_utc + timedelta(hours=LOCAL_OFFSET_HOURS)
    now_local = datetime.now(timezone.utc) + timedelta(hours=LOCAL_OFFSET_HOURS)
    return dt_local.date() == now_local.date()

def get_daily_weather():
    lat = os.getenv('LAT')
    lon = os.getenv("LON")
    # Check if cached data exists
    if os.path.exists(CACHE_FILE_DAILY):
        with open(CACHE_FILE_DAILY, "r") as f:
            cached_data = json.load(f)
            # Check if cache is still valid
            if time.time() - cached_data["timestamp"] < CACHE_EXPIRY:
                logger.debug("Using cached weather data.")
                return cached_data["data"]
    else:
        logger.debug('weather_cache.json path not found')
    
    logger.debug("Fetching new weather data from API...")
    params = {
        "location":f"{lat},{lon}",
        "timesteps":"1d",
        "units": "metric",
        "apikey": API_KEY2
    }

    response = requests.get(BASE_URL2, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        with open(CACHE_FILE_DAILY, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
        return data
    else:
        logger.debug("Error:", response.status_code, response.text)
        return None
    
def get_weather_summary():
    lat = os.getenv('LAT')
    lon = os.getenv("LON")
    # Check if cached data exists
    if os.path.exists(CACHE_FILE_SUMMARY):
        with open(CACHE_FILE_SUMMARY, "r") as f:
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
        with open(CACHE_FILE_SUMMARY, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
        return data
    else:
        logger.debug("Error:", response.status_code, response.text)
        return None
