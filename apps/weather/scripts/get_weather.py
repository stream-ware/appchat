#!/usr/bin/env python3
"""
Weather App - Get Current Weather
Streamware Modular App System
Open geocoding system - accepts ANY city name via API
"""

import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load app .env
APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
load_dotenv(APP_DIR / ".env")

# API endpoints
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

def load_data():
    """Load weather codes from JSON data file"""
    data_file = DATA_DIR / "cities.json"
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"cities": {}, "weather_codes": {}, "defaults": {}}

# Load data from external JSON
_DATA = load_data()
CITIES_CACHE = _DATA.get("cities", {})  # Used as cache only
WEATHER_CODES = _DATA.get("weather_codes", {})
DEFAULTS = _DATA.get("defaults", {})

def geocode_city(city_name: str) -> dict:
    """
    Geocode any city name using Open-Meteo Geocoding API
    Returns: {"lat": float, "lon": float, "name": str} or None
    """
    # First check cache for known cities
    city_lower = city_name.lower().strip()
    if city_lower in CITIES_CACHE:
        cached = CITIES_CACHE[city_lower]
        return {"lat": cached["lat"], "lon": cached["lon"], "name": cached["name"]}
    
    # Use geocoding API for unknown cities
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(GEOCODING_API, params={
                "name": city_name,
                "count": 1,
                "language": "pl",
                "format": "json"
            })
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    loc = results[0]
                    return {
                        "lat": loc["latitude"],
                        "lon": loc["longitude"],
                        "name": loc.get("name", city_name),
                        "country": loc.get("country_code", ""),
                        "admin": loc.get("admin1", "")
                    }
    except Exception as e:
        pass  # Fall through to default
    
    return None

def get_weather(city: str = None) -> dict:
    """
    Get current weather for ANY city using open geocoding
    City name is passed directly to geocoding API - no hardcoded limits
    """
    
    # Default city from env
    if not city:
        city = os.getenv("DEFAULT_CITY", "Warsaw")
    
    # Use geocoding API to resolve ANY city name
    city_data = geocode_city(city)
    
    if not city_data:
        return {
            "success": False,
            "error": f"City not found: {city}",
            "fallback": f"Nie znaleziono miasta: {city}"
        }
    
    timeout = int(os.getenv("WEATHER_TIMEOUT", "10"))
    
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(WEATHER_API, params={
                "latitude": city_data["lat"],
                "longitude": city_data["lon"],
                "current_weather": True,
                "timezone": "Europe/Warsaw"
            })
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API error: HTTP {response.status_code}",
                    "fallback": os.getenv("FALLBACK_MESSAGE", "Dane niedostępne")
                }
            
            data = response.json()
            current = data.get("current_weather", {})
            
            # Build response with geocoded city info
            result = {
                "success": True,
                "city": city_data["name"],
                "requested_city": city,  # Original request
                "latitude": city_data["lat"],
                "longitude": city_data["lon"],
                "temperature": current.get("temperature"),
                "windspeed": current.get("windspeed"),
                "winddirection": current.get("winddirection"),
                "weathercode": current.get("weathercode"),
                "time": current.get("time"),
                "description": _weather_description(current.get("weathercode", 0))
            }
            
            # Add admin region if available
            if city_data.get("admin"):
                result["region"] = city_data["admin"]
            if city_data.get("country"):
                result["country"] = city_data["country"]
            
            return result
            
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "timeout",
            "fallback": "Serwis pogodowy nie odpowiada. Spróbuj ponownie za chwilę."
        }
    except httpx.ConnectError:
        return {
            "success": False,
            "error": "connection",
            "fallback": "Brak połączenia z serwisem pogodowym."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback": os.getenv("FALLBACK_MESSAGE", "Dane niedostępne")
        }

def _weather_description(code: int) -> str:
    """Convert WMO weather code to description - loaded from data/cities.json"""
    return WEATHER_CODES.get(str(code), "Nieznane")

if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else None
    result = get_weather(city)
    print(json.dumps(result, ensure_ascii=False, indent=2))
