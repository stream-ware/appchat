# 🌤️ Weather App

## Overview
Real-time weather data from Open-Meteo API.

## Commands
| Command | Description |
|---------|-------------|
| `pogoda` | Current weather for default city |
| `pogoda warszawa` | Weather for Warsaw |
| `pogoda kraków` | Weather for Krakow |
| `prognoza` | 3-day forecast |

## Configuration
Edit `.env` file:
```env
DEFAULT_CITY=Warsaw
WEATHER_TIMEOUT=10
```

## Scripts
- `scripts/get_weather.py` - Get current weather
- `scripts/get_forecast.py` - Get forecast

## Makefile Commands
```bash
make health          # Check API status
make get-weather CITY=Warsaw
make get-forecast CITY=Warsaw DAYS=3
make fix-code        # LLM code editing mode
```

## Error Handling
- **Timeout**: Returns fallback message
- **No data**: Shows "Brak danych"
- **API error**: Shows connection error

## API
- URL: `https://api.open-meteo.com/v1/forecast`
- Auth: None (free API)
- Rate limit: None
