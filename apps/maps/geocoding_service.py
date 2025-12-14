"""Maps/Geocoding service for Streamware"""

from __future__ import annotations

import json
import ipaddress
import logging
from pathlib import Path
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger("streamware.maps")

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
IP_GEO_API = "https://ipapi.co"


class MapSearchService:
    """Provides global city search via Open-Meteo geocoding API"""

    def __init__(self, data_dir: Optional[Path] = None):
        base_dir = Path(__file__).parent
        self.data_dir = data_dir or base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.data_dir / "cities_cache.json"
        self.cache: Dict[str, Dict] = self._load_cache()
        self.ip_cache_file = self.data_dir / "ip_cache.json"
        self.ip_cache: Dict[str, Dict] = self._load_ip_cache()

    def _load_cache(self) -> Dict[str, Dict]:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("Failed to load map cache: %s", exc)
        return {}

    def _save_cache(self) -> None:
        try:
            self.cache_file.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning("Failed to save map cache: %s", exc)

    def _load_ip_cache(self) -> Dict[str, Dict]:
        if self.ip_cache_file.exists():
            try:
                return json.loads(self.ip_cache_file.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("Failed to load IP geo cache: %s", exc)
        return {}

    def _save_ip_cache(self) -> None:
        try:
            self.ip_cache_file.write_text(json.dumps(self.ip_cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning("Failed to save IP geo cache: %s", exc)

    def geolocate_ip(self, ip: Optional[str]) -> Optional[Dict]:
        ip = (ip or "").strip()
        if ip.startswith("::ffff:"):
            ip = ip.replace("::ffff:", "", 1)
        if "," in ip:
            ip = ip.split(",", 1)[0].strip()

        cache_key = ip or "self"
        cached = self.ip_cache.get(cache_key)
        if isinstance(cached, dict) and cached.get("latitude") is not None and cached.get("longitude") is not None:
            return cached

        target_ip = ip or None
        if target_ip:
            try:
                addr = ipaddress.ip_address(target_ip)
                if not addr.is_global:
                    target_ip = None
            except ValueError:
                target_ip = None

        url = f"{IP_GEO_API}/{target_ip}/json/" if target_ip else f"{IP_GEO_API}/json/"

        try:
            with httpx.Client(timeout=5) as client:
                response = client.get(url)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("IP geolocation failed: %s", exc)
            return None

        lat = payload.get("latitude")
        lon = payload.get("longitude")
        if lat is None or lon is None:
            return None

        data = {
            "ip": payload.get("ip") or ip,
            "latitude": lat,
            "longitude": lon,
            "city": payload.get("city"),
            "region": payload.get("region"),
            "country": payload.get("country"),
        }
        self.ip_cache[cache_key] = data
        self._save_ip_cache()
        return data

    def search(self, query: str, limit: int = 5, language: str = "pl") -> Dict:
        """Search for locations globally"""
        query = (query or "").strip()
        if not query:
            return {"success": False, "error": "empty_query"}

        normalized = query.lower()
        if normalized in self.cache:
            logger.info("🗺️ Maps: cache hit for %s", query)
            return {"success": True, "query": query, "results": self.cache[normalized]["results"]}

        params = {
            "name": query,
            "count": limit,
            "language": language,
            "format": "json",
        }

        payload = None
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(GEOCODING_API, params=params)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("Maps search failed, using fallback: %s", exc)

        results = []
        if payload and payload.get("results"):
            for item in payload.get("results", []):
                results.append(
                    {
                        "name": item.get("name"),
                        "country": item.get("country", item.get("country_code")),
                        "admin": item.get("admin1"),
                        "latitude": item.get("latitude"),
                        "longitude": item.get("longitude"),
                        "population": item.get("population"),
                        "timezone": item.get("timezone"),
                    }
                )

        if not results:
            q = normalized
            fallback = []
            for c in self.get_popular_cities():
                if q in c.get("name", "").lower():
                    fallback.append(
                        {
                            "name": c.get("name"),
                            "country": c.get("country"),
                            "admin": c.get("admin"),
                            "latitude": c.get("latitude"),
                            "longitude": c.get("longitude"),
                            "population": None,
                            "timezone": None,
                        }
                    )
            results = fallback[: max(1, int(limit))]

        data = {"success": True, "query": query, "results": results}
        self.cache[normalized] = data
        self._save_cache()
        return data

    def get_popular_cities(self) -> List[Dict]:
        return [
            {"name": "Warszawa", "country": "PL", "latitude": 52.2297, "longitude": 21.0122},
            {"name": "Kraków", "country": "PL", "latitude": 50.0647, "longitude": 19.945},
            {"name": "Berlin", "country": "DE", "latitude": 52.52, "longitude": 13.405},
            {"name": "New York", "country": "US", "latitude": 40.7128, "longitude": -74.006},
            {"name": "Tokyo", "country": "JP", "latitude": 35.6762, "longitude": 139.6503},
        ]


map_service = MapSearchService()


def search_locations(query: str, limit: int = 5) -> Dict:
    return map_service.search(query, limit=limit)


def get_popular_cities() -> List[Dict]:
    return map_service.get_popular_cities()
