"""
Currency Exchange Integration
Real-time currency rates from free APIs (NBP, exchangerate-api)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger("streamware.currency")

# Cache file for offline access
CACHE_FILE = Path(__file__).parent.parent.parent / "data" / "currency_cache.json"


class CurrencyExchange:
    """
    Real currency exchange rates using free APIs
    Primary: NBP (National Bank of Poland) - free, no API key
    Fallback: exchangerate-api.com free tier
    """
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(hours=1)
        self.last_update: Optional[datetime] = None
        self._load_cache()
    
    def _load_cache(self):
        """Load cached rates from disk"""
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, "r") as f:
                    data = json.load(f)
                    self.cache = data.get("rates", {})
                    if data.get("last_update"):
                        self.last_update = datetime.fromisoformat(data["last_update"])
        except Exception as e:
            logger.warning(f"Failed to load currency cache: {e}")
    
    def _save_cache(self):
        """Save rates to cache file"""
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, "w") as f:
                json.dump({
                    "rates": self.cache,
                    "last_update": self.last_update.isoformat() if self.last_update else None
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save currency cache: {e}")
    
    async def get_rates(self, base: str = "PLN") -> Dict[str, Any]:
        """Get current exchange rates"""
        import httpx
        
        # Check cache
        if self._is_cache_valid():
            return {
                "success": True,
                "source": "cache",
                "base": base,
                "rates": self.cache,
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
        
        # Try NBP API first (Polish National Bank - free, no key required)
        try:
            rates = await self._fetch_nbp_rates()
            if rates:
                self.cache = rates
                self.last_update = datetime.now()
                self._save_cache()
                return {
                    "success": True,
                    "source": "NBP",
                    "base": "PLN",
                    "rates": rates,
                    "last_update": self.last_update.isoformat()
                }
        except Exception as e:
            logger.warning(f"NBP API failed: {e}")
        
        # Fallback to cached data
        if self.cache:
            return {
                "success": True,
                "source": "cache (offline)",
                "base": base,
                "rates": self.cache,
                "last_update": self.last_update.isoformat() if self.last_update else None,
                "warning": "Using cached data - API unavailable"
            }
        
        return {
            "success": False,
            "error": "Unable to fetch exchange rates",
            "rates": {}
        }
    
    async def _fetch_nbp_rates(self) -> Optional[Dict[str, float]]:
        """Fetch rates from NBP API"""
        import httpx
        
        async with httpx.AsyncClient(timeout=10) as client:
            # NBP Table A - main currencies
            response = await client.get(
                "https://api.nbp.pl/api/exchangerates/tables/A/?format=json"
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if not data or len(data) == 0:
                return None
            
            rates = {}
            for rate in data[0].get("rates", []):
                code = rate.get("code")
                mid = rate.get("mid")
                if code and mid:
                    # NBP gives rates as 1 foreign = X PLN
                    # We store as 1 PLN = X foreign
                    rates[code] = round(1 / mid, 4)
            
            # Add PLN = 1
            rates["PLN"] = 1.0
            
            return rates
    
    async def get_rate(self, currency: str) -> Dict[str, Any]:
        """Get rate for specific currency"""
        currency = currency.upper()
        
        result = await self.get_rates()
        if not result.get("success"):
            return result
        
        rates = result.get("rates", {})
        
        if currency not in rates:
            return {
                "success": False,
                "error": f"Currency {currency} not found",
                "available": list(rates.keys())[:10]
            }
        
        # Calculate PLN to currency
        rate = rates[currency]
        pln_rate = 1 / rate if rate > 0 else 0
        
        return {
            "success": True,
            "currency": currency,
            "rate": rate,
            "pln_rate": round(pln_rate, 4),
            "description": f"1 PLN = {rate:.4f} {currency}",
            "reverse": f"1 {currency} = {pln_rate:.4f} PLN",
            "source": result.get("source"),
            "last_update": result.get("last_update")
        }
    
    async def convert(self, amount: float, from_curr: str, to_curr: str) -> Dict[str, Any]:
        """Convert amount between currencies"""
        from_curr = from_curr.upper()
        to_curr = to_curr.upper()
        
        result = await self.get_rates()
        if not result.get("success"):
            return result
        
        rates = result.get("rates", {})
        
        if from_curr not in rates and from_curr != "PLN":
            return {"success": False, "error": f"Currency {from_curr} not found"}
        if to_curr not in rates and to_curr != "PLN":
            return {"success": False, "error": f"Currency {to_curr} not found"}
        
        # Convert through PLN
        if from_curr == "PLN":
            pln_amount = amount
        else:
            # 1 PLN = X from_curr, so amount from_curr = amount / X PLN
            pln_amount = amount / rates.get(from_curr, 1)
        
        if to_curr == "PLN":
            result_amount = pln_amount
        else:
            # 1 PLN = Y to_curr, so pln_amount PLN = pln_amount * Y to_curr
            result_amount = pln_amount * rates.get(to_curr, 1)
        
        return {
            "success": True,
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": round(result_amount, 2),
            "rate": f"1 {from_curr} = {round(result_amount/amount, 4)} {to_curr}" if amount > 0 else None
        }
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.cache or not self.last_update:
            return False
        return datetime.now() - self.last_update < self.cache_ttl
    
    def get_available_currencies(self) -> List[str]:
        """Get list of available currencies"""
        return list(self.cache.keys()) if self.cache else [
            "USD", "EUR", "GBP", "CHF", "JPY", "CZK", "DKK", "NOK", "SEK", "PLN"
        ]


# Singleton
currency_exchange = CurrencyExchange()
