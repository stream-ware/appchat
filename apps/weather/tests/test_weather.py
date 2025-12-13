#!/usr/bin/env python3
"""Weather App Tests"""

import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def test_weather_api():
    """Test weather API fetch"""
    from get_weather import get_weather
    
    result = get_weather("Warsaw")
    
    assert "success" in result, "Missing success field"
    
    if result["success"]:
        assert "temperature" in result, "Missing temperature"
        assert "city" in result, "Missing city"
        assert result["city"] == "Warszawa", f"Wrong city: {result['city']}"
        print(f"✅ API test passed: {result['temperature']}°C")
    else:
        print(f"⚠️ API unavailable: {result.get('error')}")
    
    return result["success"]

def test_city_mapping():
    """Test city name mapping"""
    from get_weather import CITIES
    
    assert "warsaw" in CITIES, "Missing Warsaw"
    assert "kraków" in CITIES, "Missing Kraków"
    assert CITIES["warsaw"]["lat"] == 52.2297, "Wrong Warsaw lat"
    
    print("✅ City mapping test passed")
    return True

def test_weather_codes():
    """Test weather code descriptions"""
    from get_weather import _weather_description
    
    assert _weather_description(0) == "Bezchmurnie", "Wrong code 0"
    assert _weather_description(61) == "Lekki deszcz", "Wrong code 61"
    assert _weather_description(999) == "Nieznane", "Wrong unknown code"
    
    print("✅ Weather codes test passed")
    return True

def run_all_tests():
    """Run all tests"""
    results = {
        "city_mapping": test_city_mapping(),
        "weather_codes": test_weather_codes(),
        "api": test_weather_api()
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n{'='*40}")
    print(f"Tests: {passed}/{total} passed")
    print(json.dumps({"passed": passed, "total": total, "results": results}))
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
