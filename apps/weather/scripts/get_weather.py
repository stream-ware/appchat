#!/usr/bin/env python3
"""
Weather App - Get Current Weather
Streamware Modular App System
"""

import os
import sys
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load app .env
APP_DIR = Path(__file__).parent.parent
load_dotenv(APP_DIR / ".env")

# Cities coordinates
CITIES = {
    "warsaw": {"lat": 52.2297, "lon": 21.0122, "name": "Warszawa"},
    "warszawa": {"lat": 52.2297, "lon": 21.0122, "name": "Warszawa"},
    "krakow": {"lat": 50.0647, "lon": 19.9450, "name": "Kraków"},
    "kraków": {"lat": 50.0647, "lon": 19.9450, "name": "Kraków"},
    "gdansk": {"lat": 54.3520, "lon": 18.6466, "name": "Gdańsk"},
    "gdańsk": {"lat": 54.3520, "lon": 18.6466, "name": "Gdańsk"},
    "wroclaw": {"lat": 51.1079, "lon": 17.0385, "name": "Wrocław"},
    "wrocław": {"lat": 51.1079, "lon": 17.0385, "name": "Wrocław"},
    "poznan": {"lat": 52.4064, "lon": 16.9252, "name": "Poznań"},
    "poznań": {"lat": 52.4064, "lon": 16.9252, "name": "Poznań"},
}

def get_weather(city: str = None) -> dict:
    """Get current weather for city"""
    
    # Default city from env
    if not city:
        city = os.getenv("DEFAULT_CITY", "Warsaw")
    
    city_lower = city.lower()
    city_data = CITIES.get(city_lower, CITIES.get("warsaw"))
    
    api_url = os.getenv("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")
    timeout = int(os.getenv("WEATHER_TIMEOUT", "10"))
    
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(api_url, params={
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
            
            return {
                "success": True,
                "city": city_data["name"],
                "temperature": current.get("temperature"),
                "windspeed": current.get("windspeed"),
                "winddirection": current.get("winddirection"),
                "weathercode": current.get("weathercode"),
                "time": current.get("time"),
                "description": _weather_description(current.get("weathercode", 0))
            }
            
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
    """Convert WMO weather code to description"""
    codes = {
        0: "Bezchmurnie",
        1: "Przeważnie bezchmurnie",
        2: "Częściowe zachmurzenie",
        3: "Pochmurno",
        45: "Mgła",
        48: "Szadź",
        51: "Lekka mżawka",
        53: "Umiarkowana mżawka",
        55: "Intensywna mżawka",
        61: "Lekki deszcz",
        63: "Umiarkowany deszcz",
        65: "Intensywny deszcz",
        71: "Lekki śnieg",
        73: "Umiarkowany śnieg",
        75: "Intensywny śnieg",
        80: "Przelotne opady",
        81: "Umiarkowane opady",
        82: "Silne opady",
        95: "Burza",
        96: "Burza z gradem",
        99: "Silna burza z gradem",
    }
    return codes.get(code, "Nieznane")

if __name__ == "__main__":
    city = sys.argv[1] if len(sys.argv) > 1 else None
    result = get_weather(city)
    print(json.dumps(result, ensure_ascii=False, indent=2))
