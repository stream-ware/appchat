"""
STREAMWARE MVP - Voice-Controlled Dashboard Platform
Main FastAPI application with WebSocket for real-time voice interaction
Includes Internet integrations: HTTP, MQTT, Email, RSS, Weather API, Webhooks
Database: SQLite for conversations, config, and system data
"""

import asyncio
import json
import random
import uuid
import logging
import os
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import httpx
import aiohttp
import feedparser

# Local modules
from backend.database import db, Database
from backend.config import config, get_config, reload_config
from backend.llm_manager import llm_manager, LLMManager
from backend.app_registry import app_registry, AppRegistry
from backend.makefile_converter import makefile_converter, MakefileConverter
from backend.registry_manager import registry_manager, RegistryManager
from backend.language_manager import language_manager, LanguageManager
from backend.app_generator import app_generator, AppGenerator
from backend.data_loader import data_loader, DataLoader
try:
    import aiomqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
try:
    import aiosmtplib
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# ============================================================================
# LOGGING CONFIGURATION - YAML FORMAT
# ============================================================================

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

class YAMLFormatter(logging.Formatter):
    """Custom YAML-style log formatter for better readability"""
    
    def format(self, record):
        log_data = {
            'time': self.formatTime(record, '%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add extra fields if present
        if hasattr(record, 'user'):
            log_data['user'] = record.user
        if hasattr(record, 'session'):
            log_data['session'] = record.session
        if hasattr(record, 'command'):
            log_data['command'] = record.command
        if hasattr(record, 'app_type'):
            log_data['app_type'] = record.app_type
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'url'):
            log_data['url'] = record.url
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        
        # Format as YAML-like output
        lines = [f"- {log_data['time']}:"]
        lines.append(f"    level: {log_data['level']}")
        lines.append(f"    logger: {log_data['logger']}")
        lines.append(f"    message: \"{log_data['message']}\"")
        
        for key in ['user', 'session', 'command', 'app_type', 'action', 'url', 'duration_ms']:
            if key in log_data:
                lines.append(f"    {key}: {log_data[key]}")
        
        return '\n'.join(lines)

class ConsoleYAMLFormatter(logging.Formatter):
    """Compact YAML formatter for console with colors"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        time_str = self.formatTime(record, '%H:%M:%S')
        
        # Build compact YAML line
        line = f"{color}[{time_str}] {record.levelname:<8}{self.RESET} | {record.name}: {record.getMessage()}"
        
        # Add extra context on same line if present
        extras = []
        if hasattr(record, 'user'):
            extras.append(f"user={record.user}")
        if hasattr(record, 'session'):
            extras.append(f"session={record.session[:8]}...")
        if hasattr(record, 'command'):
            extras.append(f"cmd=\"{record.command}\"")
        if hasattr(record, 'app_type'):
            extras.append(f"app={record.app_type}")
        if hasattr(record, 'url'):
            extras.append(f"url={record.url}")
        
        if extras:
            line += f" {{ {', '.join(extras)} }}"
        
        return line

# Setup loggers
logger = logging.getLogger("streamware")
logger.setLevel(logging.DEBUG)

# Console handler with colored YAML format
console_handler = logging.StreamHandler()
console_handler.setFormatter(ConsoleYAMLFormatter())
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

# File handler with full YAML format
file_handler = logging.FileHandler(LOGS_DIR / "streamware.log", encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'))
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# YAML file handler for structured logs
yaml_handler = logging.FileHandler(LOGS_DIR / "streamware.yaml", encoding='utf-8')
yaml_handler.setFormatter(YAMLFormatter())
yaml_handler.setLevel(logging.INFO)
logger.addHandler(yaml_handler)

# Conversation logger with YAML format
conv_logger = logging.getLogger("conversations")
conv_handler = logging.FileHandler(LOGS_DIR / "conversations.log", encoding='utf-8')
conv_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
conv_logger.addHandler(conv_handler)
conv_yaml_handler = logging.FileHandler(LOGS_DIR / "conversations.yaml", encoding='utf-8')
conv_yaml_handler.setFormatter(YAMLFormatter())
conv_logger.addHandler(conv_yaml_handler)
conv_logger.setLevel(logging.INFO)

# Prevent propagation to root logger
logger.propagate = False
conv_logger.propagate = False

app = FastAPI(title="Streamware MVP", version="0.2.0", description="Voice-Controlled Dashboard Platform with Dynamic LLM-based Views")

logger.info("="*60)
logger.info("🚀 STREAMWARE MVP v0.2.0 Starting...")
logger.info("="*60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INTERNET INTEGRATIONS MODULE
# ============================================================================

class IntegrationManager:
    """Manages all internet integrations: HTTP, MQTT, Email, RSS, Weather, Webhooks"""
    
    def __init__(self):
        self.http_client: Optional[httpx.AsyncClient] = None
        self.webhooks: Dict[str, List[str]] = {}  # event -> [urls]
        self.mqtt_client = None
        self.rss_feeds: Dict[str, str] = {}  # name -> url
        self.cached_data: Dict[str, Any] = {}
        self.last_fetch: Dict[str, datetime] = {}
        logger.info("🌐 IntegrationManager initialized")
    
    async def start(self):
        """Initialize async clients"""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        logger.info("🔗 HTTP client started")
    
    async def stop(self):
        """Cleanup async clients"""
        if self.http_client:
            await self.http_client.aclose()
        logger.info("🔌 IntegrationManager stopped")
    
    # ==================== HTTP/REST API ====================
    
    async def http_get(self, url: str, headers: Dict = None) -> Dict:
        """Make HTTP GET request"""
        try:
            logger.info(f"🌐 HTTP GET: {url}")
            response = await self.http_client.get(url, headers=headers or {})
            response.raise_for_status()
            return {"success": True, "status": response.status_code, "data": response.json()}
        except Exception as e:
            logger.error(f"❌ HTTP GET failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def http_post(self, url: str, data: Dict, headers: Dict = None) -> Dict:
        """Make HTTP POST request"""
        try:
            logger.info(f"🌐 HTTP POST: {url}")
            response = await self.http_client.post(url, json=data, headers=headers or {})
            response.raise_for_status()
            return {"success": True, "status": response.status_code, "data": response.json()}
        except Exception as e:
            logger.error(f"❌ HTTP POST failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== WEBHOOKS ====================
    
    def register_webhook(self, event: str, url: str):
        """Register webhook URL for an event"""
        if event not in self.webhooks:
            self.webhooks[event] = []
        self.webhooks[event].append(url)
        logger.info(f"🪝 Webhook registered: {event} -> {url}")
    
    def unregister_webhook(self, event: str, url: str):
        """Remove webhook URL"""
        if event in self.webhooks and url in self.webhooks[event]:
            self.webhooks[event].remove(url)
            logger.info(f"🪝 Webhook removed: {event} -> {url}")
    
    async def trigger_webhook(self, event: str, payload: Dict):
        """Trigger all webhooks for an event"""
        if event not in self.webhooks:
            return []
        
        results = []
        for url in self.webhooks[event]:
            try:
                logger.info(f"🪝 Triggering webhook: {event} -> {url}")
                response = await self.http_client.post(url, json={
                    "event": event,
                    "timestamp": datetime.now().isoformat(),
                    "payload": payload
                })
                results.append({"url": url, "status": response.status_code})
            except Exception as e:
                logger.error(f"❌ Webhook failed: {url} - {e}")
                results.append({"url": url, "error": str(e)})
        return results
    
    # ==================== WEATHER API ====================
    
    async def get_weather(self, city: str = "Warsaw") -> Dict:
        """Get weather data from Open-Meteo API (free, no key required)"""
        try:
            # Geocoding first
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geo_resp = await self.http_client.get(geo_url)
            geo_data = geo_resp.json()
            
            if not geo_data.get("results"):
                return {"success": False, "error": f"City not found: {city}"}
            
            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            
            # Weather data
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto"
            weather_resp = await self.http_client.get(weather_url)
            weather_data = weather_resp.json()
            
            current = weather_data.get("current", {})
            logger.info(f"🌤️ Weather fetched for {city}: {current.get('temperature_2m')}°C")
            
            return {
                "success": True,
                "city": city,
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "weather_code": current.get("weather_code"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Weather fetch failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== RSS FEEDS ====================
    
    def add_rss_feed(self, name: str, url: str):
        """Add RSS feed to monitor"""
        self.rss_feeds[name] = url
        logger.info(f"📰 RSS feed added: {name} -> {url}")
    
    async def fetch_rss(self, name: str = None) -> Dict:
        """Fetch RSS feed(s)"""
        results = {}
        feeds_to_fetch = {name: self.rss_feeds[name]} if name else self.rss_feeds
        
        for feed_name, url in feeds_to_fetch.items():
            try:
                logger.info(f"📰 Fetching RSS: {feed_name}")
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        entries = []
                        for entry in feed.entries[:10]:  # Last 10 entries
                            entries.append({
                                "title": entry.get("title", ""),
                                "link": entry.get("link", ""),
                                "published": entry.get("published", ""),
                                "summary": entry.get("summary", "")[:200]
                            })
                        
                        results[feed_name] = {
                            "title": feed.feed.get("title", feed_name),
                            "entries": entries,
                            "fetched_at": datetime.now().isoformat()
                        }
            except Exception as e:
                logger.error(f"❌ RSS fetch failed for {feed_name}: {e}")
                results[feed_name] = {"error": str(e)}
        
        return results
    
    # ==================== EMAIL (SMTP) ====================
    
    async def send_email(self, to: str, subject: str, body: str, 
                        smtp_host: str = "smtp.gmail.com", smtp_port: int = 587,
                        username: str = None, password: str = None) -> Dict:
        """Send email via SMTP"""
        if not EMAIL_AVAILABLE:
            return {"success": False, "error": "aiosmtplib not installed"}
        
        try:
            from email.message import EmailMessage
            
            msg = EmailMessage()
            msg["From"] = username or "streamware@example.com"
            msg["To"] = to
            msg["Subject"] = subject
            msg.set_content(body)
            
            logger.info(f"📧 Sending email to: {to}")
            
            if username and password:
                await aiosmtplib.send(
                    msg,
                    hostname=smtp_host,
                    port=smtp_port,
                    username=username,
                    password=password,
                    start_tls=True
                )
            else:
                # Simulate sending for demo
                logger.info(f"📧 [DEMO] Email would be sent to: {to}")
                return {"success": True, "demo": True, "to": to, "subject": subject}
            
            logger.info(f"✅ Email sent to: {to}")
            return {"success": True, "to": to, "subject": subject}
        except Exception as e:
            logger.error(f"❌ Email send failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== MQTT (IoT) ====================
    
    async def mqtt_publish(self, topic: str, payload: Dict,
                          broker: str = "test.mosquitto.org", port: int = 1883) -> Dict:
        """Publish message to MQTT broker"""
        if not MQTT_AVAILABLE:
            return {"success": False, "error": "aiomqtt not installed"}
        
        try:
            logger.info(f"📡 MQTT publish: {topic} -> {broker}")
            async with aiomqtt.Client(broker, port) as client:
                await client.publish(topic, json.dumps(payload))
            logger.info(f"✅ MQTT published to: {topic}")
            return {"success": True, "topic": topic, "broker": broker}
        except Exception as e:
            logger.error(f"❌ MQTT publish failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ==================== EXTERNAL APIs ====================
    
    async def fetch_crypto_price(self, symbol: str = "bitcoin") -> Dict:
        """Fetch cryptocurrency price from CoinGecko (free API)"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd,eur,pln"
            response = await self.http_client.get(url)
            data = response.json()
            
            if symbol in data:
                logger.info(f"💰 Crypto price fetched: {symbol}")
                return {"success": True, "symbol": symbol, "prices": data[symbol]}
            return {"success": False, "error": "Symbol not found"}
        except Exception as e:
            logger.error(f"❌ Crypto fetch failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def fetch_exchange_rates(self, base: str = "EUR") -> Dict:
        """Fetch exchange rates from exchangerate.host (free API)"""
        try:
            url = f"https://api.exchangerate.host/latest?base={base}"
            response = await self.http_client.get(url)
            data = response.json()
            
            if data.get("success", True):
                logger.info(f"💱 Exchange rates fetched for: {base}")
                rates = data.get("rates", {})
                return {
                    "success": True,
                    "base": base,
                    "rates": {k: rates.get(k) for k in ["USD", "PLN", "GBP", "CHF"] if k in rates},
                    "timestamp": datetime.now().isoformat()
                }
            return {"success": False, "error": "API error"}
        except Exception as e:
            logger.error(f"❌ Exchange rates fetch failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def fetch_news(self, query: str = "technology") -> Dict:
        """Fetch news headlines (simulated - real API would need key)"""
        # Simulated news for demo
        headlines = [
            {"title": f"Breaking: {query.title()} sector sees major growth", "source": "TechNews"},
            {"title": f"New developments in {query} industry", "source": "BusinessDaily"},
            {"title": f"Experts predict {query} trends for 2025", "source": "FutureWatch"},
            {"title": f"Investment opportunities in {query}", "source": "FinanceToday"},
            {"title": f"How {query} is changing the world", "source": "GlobalReport"},
        ]
        logger.info(f"📰 News fetched for: {query}")
        return {"success": True, "query": query, "headlines": headlines}
    
    def get_status(self) -> Dict:
        """Get integration status"""
        return {
            "http_client": "active" if self.http_client else "inactive",
            "mqtt_available": MQTT_AVAILABLE,
            "email_available": EMAIL_AVAILABLE,
            "webhooks_count": sum(len(urls) for urls in self.webhooks.values()),
            "rss_feeds_count": len(self.rss_feeds),
            "cached_items": len(self.cached_data)
        }

# Global integration manager
integrations = IntegrationManager()

# Default RSS feeds
integrations.add_rss_feed("tech", "https://feeds.arstechnica.com/arstechnica/technology-lab")
integrations.add_rss_feed("security", "https://feeds.feedburner.com/TheHackersNews")
integrations.add_rss_feed("business", "https://feeds.bbci.co.uk/news/business/rss.xml")

# ============================================================================
# USER & ACCESS CONTROL SYSTEM
# ============================================================================

@dataclass
class User:
    username: str
    password: str  # In production, use hashed passwords
    role: str
    display_name: str
    permissions: List[str]

class UserManager:
    """Manages users, authentication, and role-based access control"""
    
    # Predefined roles with permissions
    ROLES = {
        "admin": {
            "display": "Administrator",
            "permissions": ["*"],  # All permissions
            "description": "Pełny dostęp do wszystkich funkcji systemu"
        },
        "office": {
            "display": "Pracownik biurowy",
            "permissions": ["documents", "sales", "analytics", "system"],
            "description": "Dostęp do dokumentów, sprzedaży i analityki"
        },
        "security": {
            "display": "Ochrona",
            "permissions": ["cameras", "home", "system"],
            "description": "Dostęp do monitoringu i systemów bezpieczeństwa"
        },
        "manager": {
            "display": "Manager",
            "permissions": ["documents", "sales", "analytics", "cameras", "system"],
            "description": "Dostęp do biura i monitoringu"
        },
        "guest": {
            "display": "Gość",
            "permissions": ["system"],
            "description": "Tylko podstawowe funkcje systemu"
        }
    }
    
    # Predefined users
    USERS = {
        "admin": User("admin", "admin123", "admin", "Administrator", ["*"]),
        "kowalski": User("kowalski", "biuro123", "office", "Jan Kowalski", ["documents", "sales", "analytics", "system"]),
        "dozorca": User("dozorca", "ochrona123", "security", "Tomasz Nowak", ["cameras", "home", "system"]),
        "manager": User("manager", "manager123", "manager", "Anna Wiśniewska", ["documents", "sales", "analytics", "cameras", "system"]),
        "gosc": User("gosc", "gosc123", "guest", "Gość", ["system"]),
    }
    
    def __init__(self):
        self.logged_in_users: Dict[str, User] = {}  # session_id -> User
        logger.info("👥 UserManager initialized")
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.USERS.get(username.lower())
        if user and user.password == password:
            logger.info(f"✅ User authenticated: {username}")
            return user
        logger.warning(f"❌ Authentication failed for: {username}")
        return None
    
    def login(self, session_id: str, username: str, password: str) -> Dict:
        """Login user to session"""
        user = self.authenticate(username, password)
        if user:
            self.logged_in_users[session_id] = user
            return {
                "success": True,
                "user": user.display_name,
                "role": self.ROLES[user.role]["display"],
                "permissions": user.permissions
            }
        return {"success": False, "error": "Nieprawidłowy login lub hasło"}
    
    def logout(self, session_id: str) -> bool:
        """Logout user from session"""
        if session_id in self.logged_in_users:
            user = self.logged_in_users.pop(session_id)
            logger.info(f"👋 User logged out: {user.username}")
            return True
        return False
    
    def get_user(self, session_id: str) -> Optional[User]:
        """Get logged in user for session"""
        return self.logged_in_users.get(session_id)
    
    def has_permission(self, session_id: str, app_type: str) -> bool:
        """Check if user has permission for app_type"""
        user = self.get_user(session_id)
        if not user:
            return False
        if "*" in user.permissions:
            return True
        return app_type in user.permissions
    
    def get_allowed_apps(self, session_id: str) -> List[str]:
        """Get list of apps user has access to"""
        user = self.get_user(session_id)
        if not user:
            return []
        if "*" in user.permissions:
            return ["documents", "cameras", "sales", "home", "analytics", "internet", "system"]
        return user.permissions
    
    def get_users_list(self) -> List[Dict]:
        """Get list of all users (for admin)"""
        return [
            {
                "username": u.username,
                "display_name": u.display_name,
                "role": u.role,
                "role_display": self.ROLES[u.role]["display"]
            }
            for u in self.USERS.values()
        ]

# Global user manager
user_manager = UserManager()

# ============================================================================
# SKILLS & FEATURES REGISTRY
# ============================================================================

class SkillRegistry:
    """Registry of all available skills/features with metadata
    Data loaded from: data/apps_config.json
    """
    
    @classmethod
    def _get_apps_from_config(cls) -> Dict:
        """Load apps from external JSON config"""
        return data_loader.get_apps()
    
    @classmethod
    def get_all_apps(cls) -> Dict:
        """Get all registered apps including modular apps from registry"""
        apps = dict(cls._get_apps_from_config())
        
        # Add modular apps from app_registry
        for app_id, app in app_registry.apps.items():
            if app_id not in apps:
                # Build skills from manifest commands
                skills = []
                for cmd_text, cmd_info in app.commands.items():
                    skills.append({
                        "cmd": cmd_text,
                        "name": cmd_text[:20],
                        "desc": f"{app.name} command"
                    })
                
                apps[app_id] = {
                    "name": app.name,
                    "description": app.description,
                    "icon": app.ui.get("icon", "📦"),
                    "color": app.ui.get("color", "#6366f1"),
                    "skills": skills[:8],  # Limit to 8 skills
                    "modular": True  # Mark as modular app
                }
        
        return apps
    
    @classmethod
    def get_apps_for_user(cls, permissions: List[str]) -> Dict:
        """Get apps filtered by user permissions"""
        all_apps = cls.get_all_apps()
        if "*" in permissions:
            return all_apps
        return {k: v for k, v in all_apps.items() if k in permissions}
    
    @classmethod
    def get_app(cls, app_type: str) -> Optional[Dict]:
        """Get single app by type"""
        return cls.APPS.get(app_type)
    
    @classmethod
    def get_all_commands(cls) -> List[Dict]:
        """Get flat list of all commands"""
        commands = []
        for app_type, app in cls.APPS.items():
            for skill in app["skills"]:
                commands.append({
                    "app": app_type,
                    "app_name": app["name"],
                    "command": skill["cmd"],
                    "name": skill["name"],
                    "description": skill["desc"]
                })
        return commands

# ============================================================================
# DATA MODELS
# ============================================================================

class AppType(str, Enum):
    DOCUMENTS = "documents"
    CAMERAS = "cameras"
    SALES = "sales"
    EMPTY = "empty"

class ViewType(str, Enum):
    TABLE = "table"
    GRID = "grid"
    CHART = "chart"
    CARDS = "cards"
    MATRIX = "matrix"

@dataclass
class Document:
    id: str
    filename: str
    vendor: str
    nip: str
    amount_net: float
    amount_vat: float
    amount_gross: float
    date: str
    due_date: str
    status: str
    scanned_at: str

@dataclass
class CameraFeed:
    id: str
    name: str
    location: str
    status: str
    objects_detected: int
    last_motion: str
    stream_url: str
    alerts: List[str]

@dataclass 
class SalesData:
    region: str
    amount: float
    transactions: int
    growth: float
    top_product: str

# ============================================================================
# SIMULATED DATA GENERATORS
# ============================================================================

class DataSimulator:
    """Generates realistic simulated data for demos"""
    
    VENDORS = [
        ("ABC Sp. z o.o.", "1234567890"),
        ("XYZ S.A.", "9876543210"),
        ("Tech Solutions", "5551234567"),
        ("Office Plus", "1112223334"),
        ("Digital Services", "9998887776"),
    ]
    
    CAMERA_LOCATIONS = [
        ("Wejście główne", "entrance"),
        ("Parking A", "parking_a"),
        ("Magazyn", "warehouse"),
        ("Korytarz 1", "corridor_1"),
        ("Recepcja", "reception"),
        ("Wyjście awaryjne", "emergency_exit"),
    ]
    
    REGIONS = ["Warszawa", "Kraków", "Wrocław", "Poznań", "Gdańsk", "Łódź"]
    PRODUCTS = ["Produkt A", "Produkt B", "Usługa Premium", "Pakiet Standard", "Licencja Pro"]
    
    @classmethod
    def generate_documents(cls, count: int = 10) -> List[Document]:
        docs = []
        for i in range(count):
            vendor, nip = random.choice(cls.VENDORS)
            amount_net = round(random.uniform(500, 15000), 2)
            vat_rate = random.choice([0.23, 0.08, 0.05])
            amount_vat = round(amount_net * vat_rate, 2)
            
            date = datetime.now() - timedelta(days=random.randint(1, 30))
            due_date = date + timedelta(days=random.choice([14, 21, 30, 60]))
            
            docs.append(Document(
                id=str(uuid.uuid4())[:8],
                filename=f"FV_{date.strftime('%Y%m%d')}_{i+1:03d}.pdf",
                vendor=vendor,
                nip=nip,
                amount_net=amount_net,
                amount_vat=amount_vat,
                amount_gross=round(amount_net + amount_vat, 2),
                date=date.strftime("%Y-%m-%d"),
                due_date=due_date.strftime("%Y-%m-%d"),
                status=random.choice(["Nowa", "Zweryfikowana", "Do zapłaty", "Zapłacona"]),
                scanned_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        return docs
    
    @classmethod
    def generate_cameras(cls, count: int = 4) -> List[CameraFeed]:
        cameras = []
        locations = random.sample(cls.CAMERA_LOCATIONS, min(count, len(cls.CAMERA_LOCATIONS)))
        
        for i, (name, loc_id) in enumerate(locations):
            objects = random.randint(0, 5)
            last_motion = datetime.now() - timedelta(minutes=random.randint(0, 60))
            
            alerts = []
            if random.random() > 0.7:
                alerts.append(f"Ruch wykryty {random.randint(1,10)} min temu")
            if random.random() > 0.9:
                alerts.append("Osoba w strefie zastrzeżonej")
            
            cameras.append(CameraFeed(
                id=f"cam_{i+1}",
                name=name,
                location=loc_id,
                status=random.choice(["online", "online", "online", "offline"]),
                objects_detected=objects,
                last_motion=last_motion.strftime("%H:%M:%S"),
                stream_url=f"/api/stream/{loc_id}",
                alerts=alerts
            ))
        return cameras
    
    @classmethod
    def generate_sales(cls) -> List[SalesData]:
        return [
            SalesData(
                region=region,
                amount=round(random.uniform(50000, 200000), 2),
                transactions=random.randint(50, 300),
                growth=round(random.uniform(-15, 35), 1),
                top_product=random.choice(cls.PRODUCTS)
            )
            for region in cls.REGIONS
        ]

# ============================================================================
# VOICE COMMAND PROCESSOR
# ============================================================================

class VoiceCommandProcessor:
    """
    Processes voice commands and determines appropriate response/view
    Data loaded from: data/apps_config.json
    """
    
    _intents_cache = None
    _keywords_cache = None
    
    @classmethod
    def _get_intents(cls) -> Dict:
        """Load intents from external JSON config"""
        if cls._intents_cache is None:
            cls._intents_cache = data_loader.get_intents()
        return cls._intents_cache
    
    @classmethod
    def _get_keywords(cls) -> Dict:
        """Load keywords from external JSON config"""
        if cls._keywords_cache is None:
            cls._keywords_cache = data_loader.get_keywords()
        return cls._keywords_cache
    
    # Parameter extraction patterns
    PARAM_PATTERNS = {
        "internet": {
            "weather": {"param": "city", "keywords": ["pogoda", "weather"], "extract_after": True},
        },
        "services": {
            "start": {"param": "name", "keywords": ["uruchom usługę", "start service"], "extract_after": True},
            "stop": {"param": "name", "keywords": ["zatrzymaj usługę", "stop service"], "extract_after": True},
            "restart": {"param": "name", "keywords": ["restartuj usługę", "restart service"], "extract_after": True},
        },
        "home": {
            "temperature": {"param": "room", "keywords": ["temperatura"], "extract_after": True},
        }
    }
    
    @classmethod
    def _extract_params(cls, command: str, app_type: str, action: str) -> Dict[str, str]:
        """Extract parameters from command based on app/action patterns"""
        params = {}
        command_lower = command.lower().strip()
        
        # Get pattern for this app/action
        app_patterns = cls.PARAM_PATTERNS.get(app_type, {})
        action_pattern = app_patterns.get(action, {})
        
        if action_pattern and action_pattern.get("extract_after"):
            param_name = action_pattern.get("param", "value")
            keywords = action_pattern.get("keywords", [])
            
            for kw in keywords:
                if kw in command_lower:
                    # Extract text after the keyword
                    idx = command_lower.find(kw)
                    after_text = command[idx + len(kw):].strip()
                    if after_text:
                        params[param_name] = after_text
                        break
        
        # Generic parameter extraction for weather (city names)
        if app_type == "internet" and "weather" in action:
            # Common Polish cities
            cities = ["warszawa", "kraków", "krakow", "gdańsk", "gdansk", "wrocław", "wroclaw", 
                     "poznań", "poznan", "łódź", "lodz", "katowice", "szczecin", "lublin",
                     "wejherowo", "sopot", "gdynia", "zakopane", "toruń", "bydgoszcz"]
            
            words = command_lower.split()
            for word in words:
                # Check if word is a city (not a command keyword)
                if word not in ["pogoda", "weather", "pokaż", "sprawdź", "jaka"]:
                    if word in cities or len(word) > 3:
                        # Likely a city name
                        params["city"] = command.split()[-1] if len(words) > 1 else None
                        break
            
            # If still no city, check for text after "pogoda" or "weather"
            for kw in ["pogoda ", "weather "]:
                if kw in command_lower:
                    after = command_lower.split(kw)[-1].strip()
                    if after and after not in ["w", "dla", "in", "for"]:
                        params["city"] = after.split()[0].capitalize()
                        break
        
        return params
    
    @classmethod
    def process(cls, command: str) -> Dict[str, Any]:
        """Process voice command and return intent + parameters"""
        command_lower = command.lower().strip()
        logger.info(f"📝 Processing command: '{command}'")
        
        # Find matching intent
        for pattern, (app_type, action) in cls._get_intents().items():
            if pattern in command_lower:
                # Extract parameters from command
                params = cls._extract_params(command, app_type, action)
                
                logger.info(f"✅ Matched intent: {app_type}/{action} (pattern: '{pattern}'), params: {params}")
                return {
                    "recognized": True,
                    "app_type": app_type,
                    "action": action,
                    "original_command": command,
                    "params": params,
                    "confidence": random.uniform(0.85, 0.99)
                }
        
        # Fuzzy matching using keywords
        for app_type, keywords in cls._get_keywords().items():
            if any(word in command_lower for word in keywords):
                action = "show_all"
                # For weather, detect city in fuzzy match too
                if app_type == "internet" and any(w in command_lower for w in ["pogod", "weather"]):
                    action = "weather"
                
                params = cls._extract_params(command, app_type, action)
                logger.info(f"🔍 Fuzzy match: {app_type}/{action}, params: {params}")
                return {
                    "recognized": True, 
                    "app_type": app_type, 
                    "action": action,
                    "original_command": command,
                    "params": params,
                    "confidence": 0.7
                }
        
        logger.warning(f"❓ Unrecognized command: '{command}'")
        return {
            "recognized": False,
            "app_type": "system",
            "action": "unknown",
            "original_command": command,
            "params": {},
            "confidence": 0.0
        }

# ============================================================================
# DYNAMIC VIEW GENERATOR
# ============================================================================

class ViewGenerator:
    """Generates dynamic dashboard views based on app type and action - LLM-ready"""
    
    @classmethod
    def generate(cls, app_type: str, action: str, data: Any = None) -> Dict[str, Any]:
        """Generate view configuration for frontend - supports dynamic LLM generation"""
        logger.debug(f"🎨 Generating view: {app_type}/{action}")
        
        if app_type == "documents":
            return cls._generate_documents_view(action, data)
        elif app_type == "cameras":
            return cls._generate_cameras_view(action, data)
        elif app_type == "sales":
            return cls._generate_sales_view(action, data)
        elif app_type == "home":
            return cls._generate_home_view(action, data)
        elif app_type == "analytics":
            return cls._generate_analytics_view(action, data)
        elif app_type == "internet":
            return cls._generate_internet_view(action, data)
        elif app_type == "system":
            return cls._generate_system_view(action)
        elif app_type in ["services", "monitoring", "backup", "registry", "notifications"]:
            return cls._generate_modular_app_view(app_type, action, data)
        else:
            return cls._generate_empty_view()
    
    @classmethod
    def _generate_modular_app_view(cls, app_type: str, action: str, data: Any = None) -> Dict:
        """Generate view for modular apps using app_registry"""
        app = app_registry.get_app(app_type)
        if not app:
            return cls._generate_empty_view()
        
        # Map action to makefile target
        target_map = {
            "list": "list", "overview": "overview", "systemd": "systemd",
            "docker": "docker", "cpu": "cpu", "memory": "memory",
            "disk": "disk", "processes": "processes", "create": "create",
            "start": "start", "stop": "stop", "restart": "restart"
        }
        target = target_map.get(action, action)
        
        # Try to execute via Makefile
        result = app_registry.run_make(app_type, f"user-{target}")
        
        output = result.get("output", {})
        if isinstance(output, str):
            try:
                import json
                output = json.loads(output)
            except:
                output = {"raw": output}
        
        return {
            "type": app_type,
            "view": "data",
            "title": f"{app.name}",
            "subtitle": f"Action: {action}",
            "data": output,
            "stats": [
                {"label": "App", "value": app_type, "icon": app.ui.get("icon", "📦")},
                {"label": "Status", "value": "OK" if result.get("success") else "Error", "icon": "✅" if result.get("success") else "❌"},
            ],
            "actions": [
                {"id": f"refresh_{app_type}", "label": "Odśwież", "icon": "🔄"},
            ]
        }
    
    @classmethod
    async def generate_async(cls, app_type: str, action: str, data: Any = None, params: Dict = None) -> Dict[str, Any]:
        """Async version for internet integrations that need API calls"""
        params = params or {}
        if app_type == "internet":
            return await cls._generate_internet_view_async(action, data, params)
        return cls.generate(app_type, action, data)
    
    @classmethod
    def _generate_documents_view(cls, action: str, data: List[Document] = None) -> Dict:
        if data is None:
            data = DataSimulator.generate_documents(8)
        
        docs_data = [asdict(d) for d in data]
        total_gross = sum(d.amount_gross for d in data)
        unpaid = len([d for d in data if d.status != "Zapłacona"])
        
        return {
            "type": "documents",
            "view": "table",
            "title": "📄 Zeskanowane dokumenty",
            "subtitle": f"{len(data)} dokumentów | Suma: {total_gross:,.2f} PLN | Do zapłaty: {unpaid}",
            "columns": [
                {"key": "filename", "label": "Plik", "width": "15%"},
                {"key": "vendor", "label": "Dostawca", "width": "20%"},
                {"key": "nip", "label": "NIP", "width": "12%"},
                {"key": "amount_gross", "label": "Kwota brutto", "width": "12%", "format": "currency"},
                {"key": "date", "label": "Data", "width": "10%"},
                {"key": "due_date", "label": "Termin", "width": "10%"},
                {"key": "status", "label": "Status", "width": "10%", "format": "badge"},
            ],
            "data": docs_data,
            "stats": [
                {"label": "Dokumentów", "value": len(data), "icon": "📄"},
                {"label": "Suma brutto", "value": f"{total_gross:,.2f} PLN", "icon": "💰"},
                {"label": "Do zapłaty", "value": unpaid, "icon": "⏰"},
                {"label": "Dostawców", "value": len(set(d.vendor for d in data)), "icon": "🏢"},
            ],
            "actions": [
                {"id": "scan", "label": "Skanuj nową", "icon": "📷"},
                {"id": "export", "label": "Eksportuj", "icon": "📥"},
                {"id": "filter", "label": "Filtruj", "icon": "🔍"},
            ]
        }
    
    @classmethod
    def _generate_cameras_view(cls, action: str, data: List[CameraFeed] = None) -> Dict:
        if data is None:
            data = DataSimulator.generate_cameras(4)
        
        cameras_data = [asdict(c) for c in data]
        online = len([c for c in data if c.status == "online"])
        total_objects = sum(c.objects_detected for c in data)
        alerts_count = sum(len(c.alerts) for c in data)
        
        return {
            "type": "cameras",
            "view": "matrix",
            "title": "🎥 Monitoring - Podgląd kamer",
            "subtitle": f"{online}/{len(data)} online | Wykryto obiektów: {total_objects} | Alerty: {alerts_count}",
            "grid": {
                "columns": 2,
                "rows": 2
            },
            "cameras": cameras_data,
            "stats": [
                {"label": "Kamery online", "value": f"{online}/{len(data)}", "icon": "🟢"},
                {"label": "Wykryte obiekty", "value": total_objects, "icon": "👤"},
                {"label": "Aktywne alerty", "value": alerts_count, "icon": "🚨"},
                {"label": "Ostatni ruch", "value": data[0].last_motion if data else "-", "icon": "⏱️"},
            ],
            "actions": [
                {"id": "fullscreen", "label": "Pełny ekran", "icon": "🖥️"},
                {"id": "record", "label": "Nagrywaj", "icon": "⏺️"},
                {"id": "alerts", "label": "Alerty", "icon": "🔔"},
            ]
        }
    
    @classmethod
    def _generate_sales_view(cls, action: str, data: List[SalesData] = None) -> Dict:
        if data is None:
            data = DataSimulator.generate_sales()
        
        sales_data = [asdict(s) for s in data]
        total_amount = sum(s.amount for s in data)
        total_transactions = sum(s.transactions for s in data)
        avg_growth = sum(s.growth for s in data) / len(data)
        
        # Sort for chart
        sorted_data = sorted(data, key=lambda x: x.amount, reverse=True)
        
        return {
            "type": "sales",
            "view": "dashboard",
            "title": "📊 Dashboard sprzedaży",
            "subtitle": f"Suma: {total_amount:,.2f} PLN | Transakcji: {total_transactions} | Wzrost: {avg_growth:+.1f}%",
            "chart": {
                "type": "bar",
                "labels": [s.region for s in sorted_data],
                "datasets": [{
                    "label": "Sprzedaż (PLN)",
                    "data": [s.amount for s in sorted_data],
                    "backgroundColor": ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
                }]
            },
            "table": {
                "columns": [
                    {"key": "region", "label": "Region"},
                    {"key": "amount", "label": "Sprzedaż", "format": "currency"},
                    {"key": "transactions", "label": "Transakcje"},
                    {"key": "growth", "label": "Wzrost", "format": "percent"},
                    {"key": "top_product", "label": "Top produkt"},
                ],
                "data": sales_data
            },
            "stats": [
                {"label": "Suma sprzedaży", "value": f"{total_amount:,.0f} PLN", "icon": "💰"},
                {"label": "Transakcji", "value": total_transactions, "icon": "🛒"},
                {"label": "Śr. wzrost", "value": f"{avg_growth:+.1f}%", "icon": "📈"},
                {"label": "Regionów", "value": len(data), "icon": "🗺️"},
            ],
            "actions": [
                {"id": "export", "label": "Eksportuj PDF", "icon": "📄"},
                {"id": "compare", "label": "Porównaj", "icon": "⚖️"},
                {"id": "details", "label": "Szczegóły", "icon": "🔍"},
            ]
        }
    
    @classmethod
    def _generate_home_view(cls, action: str, data: Any = None) -> Dict:
        """Generate smart home dashboard"""
        rooms = ["Salon", "Sypialnia", "Kuchnia", "Łazienka", "Biuro"]
        
        sensors_data = []
        for room in rooms:
            sensors_data.append({
                "room": room,
                "temperature": round(random.uniform(18, 26), 1),
                "humidity": random.randint(30, 70),
                "light_on": random.choice([True, False]),
                "motion": random.choice([True, False, False, False]),
            })
        
        total_power = round(random.uniform(1.5, 8.5), 2)
        
        return {
            "type": "home",
            "view": "smart_home",
            "title": "🏠 Smart Home Dashboard",
            "subtitle": f"Temperatura średnia: {sum(s['temperature'] for s in sensors_data)/len(sensors_data):.1f}°C | Zużycie: {total_power} kW",
            "rooms": sensors_data,
            "stats": [
                {"label": "Śr. temperatura", "value": f"{sum(s['temperature'] for s in sensors_data)/len(sensors_data):.1f}°C", "icon": "🌡️"},
                {"label": "Zużycie energii", "value": f"{total_power} kW", "icon": "⚡"},
                {"label": "Światła włączone", "value": sum(1 for s in sensors_data if s['light_on']), "icon": "💡"},
                {"label": "Wykryty ruch", "value": sum(1 for s in sensors_data if s['motion']), "icon": "🚶"},
            ],
            "actions": [
                {"id": "all_lights_off", "label": "Wyłącz światła", "icon": "🌙"},
                {"id": "eco_mode", "label": "Tryb eco", "icon": "🌿"},
                {"id": "schedule", "label": "Harmonogram", "icon": "📅"},
            ]
        }
    
    @classmethod
    def _generate_analytics_view(cls, action: str, data: Any = None) -> Dict:
        """Generate analytics dashboard"""
        days = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Ndz"]
        weekly_data = [random.randint(50, 200) for _ in days]
        
        return {
            "type": "analytics",
            "view": "analytics_dashboard",
            "title": "📈 Analityka i Raporty",
            "subtitle": f"Ostatnie 7 dni | Suma: {sum(weekly_data)} zdarzeń",
            "chart": {
                "type": "line",
                "labels": days,
                "datasets": [{
                    "label": "Aktywność",
                    "data": weekly_data,
                    "borderColor": "#3b82f6",
                    "fill": True
                }]
            },
            "metrics": [
                {"name": "Konwersja", "value": f"{random.uniform(2, 8):.1f}%", "change": f"+{random.uniform(0.1, 1.5):.1f}%"},
                {"name": "Czas sesji", "value": f"{random.randint(2, 8)}m {random.randint(0, 59)}s", "change": f"+{random.randint(5, 30)}s"},
                {"name": "Bounce rate", "value": f"{random.uniform(20, 50):.1f}%", "change": f"-{random.uniform(1, 5):.1f}%"},
            ],
            "stats": [
                {"label": "Suma zdarzeń", "value": sum(weekly_data), "icon": "📊"},
                {"label": "Średnia dzienna", "value": round(sum(weekly_data)/7), "icon": "📈"},
                {"label": "Max", "value": max(weekly_data), "icon": "🔝"},
                {"label": "Min", "value": min(weekly_data), "icon": "🔻"},
            ],
            "actions": [
                {"id": "export_report", "label": "Eksportuj raport", "icon": "📄"},
                {"id": "set_alerts", "label": "Ustaw alerty", "icon": "🔔"},
                {"id": "compare", "label": "Porównaj okresy", "icon": "⚖️"},
            ]
        }
    
    @classmethod
    def _generate_internet_view(cls, action: str, data: Any = None) -> Dict:
        """Generate internet integration view (sync version with cached/simulated data)"""
        status = integrations.get_status()
        
        if action in ["weather", "weather_warsaw", "weather_krakow"]:
            city = "Kraków" if "krakow" in action else "Warszawa"
            return {
                "type": "internet",
                "view": "weather",
                "title": f"🌤️ Pogoda - {city}",
                "subtitle": "Dane z Open-Meteo API",
                "loading": True,
                "message": f"Pobieranie danych pogodowych dla {city}...",
                "stats": [
                    {"label": "Miasto", "value": city, "icon": "📍"},
                    {"label": "Status", "value": "Ładowanie...", "icon": "⏳"},
                ],
                "actions": [
                    {"id": "refresh_weather", "label": "Odśwież", "icon": "🔄"},
                ]
            }
        
        elif action == "crypto":
            return {
                "type": "internet",
                "view": "crypto",
                "title": "💰 Kryptowaluty",
                "subtitle": "Dane z CoinGecko API",
                "loading": True,
                "message": "Pobieranie kursów kryptowalut...",
                "stats": [
                    {"label": "Bitcoin", "value": "Ładowanie...", "icon": "₿"},
                    {"label": "Ethereum", "value": "Ładowanie...", "icon": "Ξ"},
                ],
                "actions": [
                    {"id": "refresh_crypto", "label": "Odśwież", "icon": "🔄"},
                ]
            }
        
        elif action == "exchange":
            return {
                "type": "internet",
                "view": "exchange",
                "title": "💱 Kursy walut",
                "subtitle": "Dane z Exchange Rate API",
                "loading": True,
                "message": "Pobieranie kursów walut...",
                "stats": [
                    {"label": "EUR/PLN", "value": "Ładowanie...", "icon": "💶"},
                    {"label": "USD/PLN", "value": "Ładowanie...", "icon": "💵"},
                ],
                "actions": [
                    {"id": "refresh_exchange", "label": "Odśwież", "icon": "🔄"},
                ]
            }
        
        elif action == "rss":
            return {
                "type": "internet",
                "view": "rss",
                "title": "📰 Kanały RSS",
                "subtitle": f"{status['rss_feeds_count']} skonfigurowanych kanałów",
                "feeds": list(integrations.rss_feeds.keys()),
                "loading": True,
                "message": "Pobieranie wiadomości RSS...",
                "actions": [
                    {"id": "refresh_rss", "label": "Odśwież", "icon": "🔄"},
                    {"id": "add_feed", "label": "Dodaj kanał", "icon": "➕"},
                ]
            }
        
        elif action == "news":
            return {
                "type": "internet",
                "view": "news",
                "title": "📰 Wiadomości",
                "subtitle": "Najnowsze nagłówki",
                "loading": True,
                "message": "Pobieranie wiadomości...",
                "actions": [
                    {"id": "refresh_news", "label": "Odśwież", "icon": "🔄"},
                ]
            }
        
        elif action == "send_email":
            return {
                "type": "internet",
                "view": "email",
                "title": "📧 Wyślij Email",
                "subtitle": f"SMTP: {'Dostępny' if EMAIL_AVAILABLE else 'Niedostępny'}",
                "form": {
                    "fields": [
                        {"name": "to", "label": "Do", "type": "email"},
                        {"name": "subject", "label": "Temat", "type": "text"},
                        {"name": "body", "label": "Treść", "type": "textarea"},
                    ]
                },
                "stats": [
                    {"label": "SMTP", "value": "Gotowy" if EMAIL_AVAILABLE else "Brak", "icon": "📧"},
                ],
                "actions": [
                    {"id": "send_email", "label": "Wyślij", "icon": "📤"},
                ]
            }
        
        elif action == "mqtt":
            return {
                "type": "internet",
                "view": "mqtt",
                "title": "📡 MQTT / IoT",
                "subtitle": f"Protokół: {'Dostępny' if MQTT_AVAILABLE else 'Niedostępny'}",
                "broker": "test.mosquitto.org",
                "stats": [
                    {"label": "MQTT", "value": "Gotowy" if MQTT_AVAILABLE else "Brak", "icon": "📡"},
                    {"label": "Broker", "value": "test.mosquitto.org", "icon": "🌐"},
                ],
                "actions": [
                    {"id": "mqtt_publish", "label": "Publikuj", "icon": "📤"},
                    {"id": "mqtt_subscribe", "label": "Subskrybuj", "icon": "📥"},
                ]
            }
        
        elif action == "webhook":
            return {
                "type": "internet",
                "view": "webhooks",
                "title": "🪝 Webhooks",
                "subtitle": f"{status['webhooks_count']} zarejestrowanych webhooków",
                "webhooks": integrations.webhooks,
                "stats": [
                    {"label": "Webhooks", "value": status['webhooks_count'], "icon": "🪝"},
                ],
                "actions": [
                    {"id": "add_webhook", "label": "Dodaj webhook", "icon": "➕"},
                    {"id": "test_webhook", "label": "Testuj", "icon": "🧪"},
                ]
            }
        
        elif action in ["integrations", "api_status"]:
            return {
                "type": "internet",
                "view": "integrations",
                "title": "🌐 Integracje internetowe",
                "subtitle": "Status wszystkich usług",
                "services": [
                    {"name": "HTTP Client", "status": status['http_client'], "icon": "🌐"},
                    {"name": "MQTT", "status": "active" if MQTT_AVAILABLE else "unavailable", "icon": "📡"},
                    {"name": "Email SMTP", "status": "active" if EMAIL_AVAILABLE else "unavailable", "icon": "📧"},
                    {"name": "RSS Feeds", "status": f"{status['rss_feeds_count']} feeds", "icon": "📰"},
                    {"name": "Webhooks", "status": f"{status['webhooks_count']} registered", "icon": "🪝"},
                    {"name": "Weather API", "status": "active", "icon": "🌤️"},
                    {"name": "Crypto API", "status": "active", "icon": "💰"},
                    {"name": "Exchange API", "status": "active", "icon": "💱"},
                ],
                "stats": [
                    {"label": "HTTP", "value": status['http_client'], "icon": "🌐"},
                    {"label": "MQTT", "value": "✓" if MQTT_AVAILABLE else "✗", "icon": "📡"},
                    {"label": "Email", "value": "✓" if EMAIL_AVAILABLE else "✗", "icon": "📧"},
                    {"label": "RSS", "value": status['rss_feeds_count'], "icon": "📰"},
                ],
                "actions": [
                    {"id": "test_all", "label": "Testuj wszystko", "icon": "🧪"},
                    {"id": "refresh_status", "label": "Odśwież", "icon": "🔄"},
                ]
            }
        
        else:
            return {
                "type": "internet",
                "view": "overview",
                "title": "🌐 Internet & Integracje",
                "subtitle": "Protokoły i usługi zewnętrzne",
                "protocols": ["HTTP/REST", "WebSocket", "MQTT", "SMTP", "RSS/Atom"],
                "apis": ["Weather", "Crypto", "Exchange Rates", "News"],
                "stats": [
                    {"label": "Protokoły", "value": 5, "icon": "🔌"},
                    {"label": "API", "value": 4, "icon": "🌐"},
                    {"label": "Webhooks", "value": status['webhooks_count'], "icon": "🪝"},
                ],
                "actions": [
                    {"id": "show_integrations", "label": "Pokaż integracje", "icon": "📋"},
                ]
            }
    
    @classmethod
    async def _generate_internet_view_async(cls, action: str, data: Any = None, params: Dict = None) -> Dict:
        """Generate internet view with real API data - uses modular apps"""
        params = params or {}
        
        if action in ["weather", "weather_warsaw", "weather_krakow"]:
            # Use city from params if provided, otherwise default based on action
            city = params.get("city")
            if not city:
                city = "Kraków" if "krakow" in action else "Warszawa"
            
            logger.info(f"🌤️ Weather request for city: {city}")
            
            # Use modular weather app instead of hardcoded integrations
            result = app_registry.run_script("weather", "get_weather", city)
            
            if result.get("success") and result.get("output", {}).get("success"):
                weather = result["output"]
                return {
                    "type": "internet",
                    "view": "weather",
                    "title": f"🌤️ Pogoda - {weather.get('city', city)}",
                    "subtitle": f"Aktualizacja: {weather.get('time', '')[:16]}",
                    "data": weather,
                    "stats": [
                        {"label": "Temperatura", "value": f"{weather.get('temperature')}°C", "icon": "🌡️"},
                        {"label": "Opis", "value": weather.get('description', 'N/A'), "icon": "☁️"},
                        {"label": "Wiatr", "value": f"{weather.get('windspeed')} km/h", "icon": "💨"},
                        {"label": "Miasto", "value": weather.get('city', city), "icon": "📍"},
                    ],
                    "actions": [
                        {"id": "refresh_weather", "label": "Odśwież", "icon": "🔄"},
                    ]
                }
            else:
                # Fallback to integrations if app fails
                weather = await integrations.get_weather(city)
                if weather.get("success"):
                    return {
                        "type": "internet",
                        "view": "weather",
                        "title": f"🌤️ Pogoda - {city}",
                        "subtitle": f"Aktualizacja: {weather.get('timestamp', '')[:19]}",
                        "data": weather,
                        "stats": [
                            {"label": "Temperatura", "value": f"{weather.get('temperature')}°C", "icon": "🌡️"},
                            {"label": "Wilgotność", "value": f"{weather.get('humidity')}%", "icon": "💧"},
                            {"label": "Wiatr", "value": f"{weather.get('wind_speed')} km/h", "icon": "💨"},
                            {"label": "Miasto", "value": city, "icon": "📍"},
                        ],
                        "actions": [
                            {"id": "refresh_weather", "label": "Odśwież", "icon": "🔄"},
                        ]
                    }
                return cls._generate_internet_view(action, data)
        
        elif action == "crypto":
            btc = await integrations.fetch_crypto_price("bitcoin")
            eth = await integrations.fetch_crypto_price("ethereum")
            
            return {
                "type": "internet",
                "view": "crypto",
                "title": "💰 Kryptowaluty",
                "subtitle": f"Aktualizacja: {datetime.now().strftime('%H:%M:%S')}",
                "data": {"bitcoin": btc, "ethereum": eth},
                "stats": [
                    {"label": "Bitcoin (USD)", "value": f"${btc.get('prices', {}).get('usd', 'N/A'):,}" if btc.get('success') else "Błąd", "icon": "₿"},
                    {"label": "Bitcoin (PLN)", "value": f"{btc.get('prices', {}).get('pln', 'N/A'):,} PLN" if btc.get('success') else "Błąd", "icon": "₿"},
                    {"label": "Ethereum (USD)", "value": f"${eth.get('prices', {}).get('usd', 'N/A'):,}" if eth.get('success') else "Błąd", "icon": "Ξ"},
                    {"label": "Ethereum (PLN)", "value": f"{eth.get('prices', {}).get('pln', 'N/A'):,} PLN" if eth.get('success') else "Błąd", "icon": "Ξ"},
                ],
                "actions": [
                    {"id": "refresh_crypto", "label": "Odśwież", "icon": "🔄"},
                ]
            }
        
        elif action == "rss":
            feeds = await integrations.fetch_rss()
            
            return {
                "type": "internet",
                "view": "rss",
                "title": "📰 Kanały RSS",
                "subtitle": f"{len(feeds)} kanałów załadowanych",
                "feeds": feeds,
                "stats": [
                    {"label": "Kanały", "value": len(feeds), "icon": "📰"},
                    {"label": "Artykuły", "value": sum(len(f.get('entries', [])) for f in feeds.values()), "icon": "📄"},
                ],
                "actions": [
                    {"id": "refresh_rss", "label": "Odśwież", "icon": "🔄"},
                ]
            }
        
        elif action == "news":
            news = await integrations.fetch_news("technology")
            
            return {
                "type": "internet",
                "view": "news",
                "title": "📰 Wiadomości",
                "subtitle": "Najnowsze nagłówki",
                "headlines": news.get("headlines", []),
                "stats": [
                    {"label": "Artykuły", "value": len(news.get("headlines", [])), "icon": "📰"},
                ],
                "actions": [
                    {"id": "refresh_news", "label": "Odśwież", "icon": "🔄"},
                ]
            }
        
        return cls._generate_internet_view(action, data)
    
    @classmethod
    def _generate_system_view(cls, action: str) -> Dict:
        if action == "help":
            return {
                "type": "system",
                "view": "help",
                "title": "❓ Pomoc - 85+ dostępnych komend",
                "commands": [
                    {"category": "📄 Dokumenty (15)", "commands": [
                        "pokaż faktury", "zeskanuj fakturę", "ile faktur", "suma faktur",
                        "umowy", "przeterminowane", "eksportuj do excel", "archiwum"
                    ]},
                    {"category": "🎥 Monitoring (15)", "commands": [
                        "pokaż kamery", "monitoring", "gdzie ruch", "alerty",
                        "parking", "magazyn", "mapa ciepła", "historia nagrań"
                    ]},
                    {"category": "📊 Sprzedaż (12)", "commands": [
                        "pokaż sprzedaż", "raport", "porównaj regiony", "trend",
                        "kpi", "prognoza", "lejek sprzedaży", "prowizje"
                    ]},
                    {"category": "🏠 Smart Home (10)", "commands": [
                        "temperatura", "oświetlenie", "energia", "zużycie prądu",
                        "ogrzewanie", "klimatyzacja", "alarm", "czujniki"
                    ]},
                    {"category": "📈 Analityka (8)", "commands": [
                        "analiza", "wykres", "raport dzienny", "raport tygodniowy",
                        "anomalie", "predykcja", "porównanie"
                    ]},
                    {"category": "🌐 Internet (20)", "commands": [
                        "pogoda", "weather", "bitcoin", "crypto", "kursy walut",
                        "rss", "news", "email", "mqtt", "webhook", "integracje"
                    ]},
                    {"category": "⚙️ System (5)", "commands": [
                        "pomoc", "wyczyść", "status", "ustawienia", "historia"
                    ]},
                ]
            }
        elif action == "history":
            return {
                "type": "system",
                "view": "history",
                "title": "📜 Historia konwersacji",
                "message": "Historia jest zapisywana w logs/conversations.log"
            }
        elif action == "login":
            return {
                "type": "system",
                "view": "login",
                "title": "🔐 Logowanie",
                "subtitle": "Wprowadź dane logowania",
                "message": "Wpisz: login [użytkownik] [hasło]\n\nDostępni użytkownicy demo:\n• admin / admin123 - pełny dostęp\n• kowalski / biuro123 - biuro\n• dozorca / ochrona123 - ochrona\n• manager / manager123 - manager\n• gosc / gosc123 - gość",
                "users": user_manager.get_users_list()
            }
        elif action == "logout":
            return {
                "type": "system",
                "view": "logout",
                "title": "👋 Wylogowano",
                "message": "Zostałeś wylogowany. Wpisz 'login' aby zalogować się ponownie."
            }
        elif action == "whoami":
            return {
                "type": "system",
                "view": "whoami",
                "title": "👤 Aktualny użytkownik",
                "message": "Sprawdzanie użytkownika..."
            }
        elif action == "users":
            return {
                "type": "system",
                "view": "users",
                "title": "👥 Lista użytkowników",
                "users": user_manager.get_users_list(),
                "roles": user_manager.ROLES
            }
        elif action == "welcome":
            return cls._generate_welcome_view()
        else:
            return cls._generate_welcome_view()
    
    @classmethod
    def _generate_welcome_view(cls, user_permissions: List[str] = None) -> Dict:
        """Generate welcome dashboard with all apps and skills"""
        if user_permissions is None:
            user_permissions = ["*"]  # Show all by default
        
        apps = SkillRegistry.get_apps_for_user(user_permissions)
        
        return {
            "type": "welcome",
            "view": "dashboard",
            "title": "🚀 Streamware Dashboard",
            "subtitle": "Wybierz aplikację lub wpisz komendę",
            "apps": apps,
            "total_skills": sum(len(app["skills"]) for app in apps.values()),
            "message": "Kliknij aplikację aby zobaczyć dostępne komendy lub wpisz polecenie w chat.",
            "quick_commands": [
                {"cmd": "pomoc", "label": "📋 Pomoc"},
                {"cmd": "login", "label": "🔐 Zaloguj"},
                {"cmd": "status", "label": "⚙️ Status"},
            ]
        }
    
    @classmethod
    def _generate_empty_view(cls) -> Dict:
        return cls._generate_welcome_view()

# ============================================================================
# RESPONSE GENERATOR (Simulates TTS responses)
# ============================================================================

class ResponseGenerator:
    """Generates voice-like text responses"""
    
    @classmethod
    def generate(cls, intent: Dict, view_data: Dict) -> str:
        app_type = intent.get("app_type")
        action = intent.get("action")
        
        if not intent.get("recognized"):
            return "Nie rozumiem polecenia. Powiedz 'pomoc' aby zobaczyć dostępne komendy."
        
        if app_type == "documents":
            return cls._documents_response(action, view_data)
        elif app_type == "cameras":
            return cls._cameras_response(action, view_data)
        elif app_type == "sales":
            return cls._sales_response(action, view_data)
        elif app_type == "home":
            return cls._home_response(action, view_data)
        elif app_type == "analytics":
            return cls._analytics_response(action, view_data)
        elif app_type == "internet":
            return cls._internet_response(action, view_data)
        elif app_type == "system":
            return cls._system_response(action)
        
        return "OK, wyświetlam."
    
    @classmethod
    def _documents_response(cls, action: str, view: Dict) -> str:
        stats = {s["label"]: s["value"] for s in view.get("stats", [])}
        
        responses = {
            "show_all": f"Wyświetlam {stats.get('Dokumentów', 0)} dokumentów. Suma brutto wynosi {stats.get('Suma brutto', '0 PLN')}. {stats.get('Do zapłaty', 0)} faktur oczekuje na płatność.",
            "scan_new": "Aktywuję skanowanie. Połóż dokument i powiedz 'zeskanuj' gdy będziesz gotowy.",
            "count": f"Masz {stats.get('Dokumentów', 0)} zeskanowanych dokumentów od {stats.get('Dostawców', 0)} dostawców.",
            "sum_total": f"Łączna suma dokumentów to {stats.get('Suma brutto', '0 PLN')}.",
            "contracts": "Wyświetlam umowy i kontrakty.",
            "overdue": "Wyświetlam przeterminowane dokumenty.",
            "export_excel": "Eksportuję dokumenty do Excel.",
        }
        return responses.get(action, f"Wyświetlam dokumenty. Znaleziono {stats.get('Dokumentów', 0)} pozycji.")
    
    @classmethod
    def _cameras_response(cls, action: str, view: Dict) -> str:
        stats = {s["label"]: s["value"] for s in view.get("stats", [])}
        
        responses = {
            "show_grid": f"Wyświetlam podgląd kamer. {stats.get('Kamery online', '0/0')} online. Wykryto {stats.get('Wykryte obiekty', 0)} obiektów. {stats.get('Aktywne alerty', 0)} aktywnych alertów.",
            "show_motion": f"Ostatni ruch wykryty o {stats.get('Ostatni ruch', '-')}. Aktualnie wykrytych obiektów: {stats.get('Wykryte obiekty', 0)}.",
            "show_alerts": f"Masz {stats.get('Aktywne alerty', 0)} aktywnych alertów.",
            "parking": "Wyświetlam kamery parkingu.",
            "entrance": "Wyświetlam kamerę wejścia głównego.",
            "warehouse": "Wyświetlam kamery magazynu.",
            "heatmap": "Generuję mapę ciepła ruchu.",
            "recordings": "Wyświetlam historię nagrań.",
        }
        return responses.get(action, "Wyświetlam monitoring kamer.")
    
    @classmethod
    def _sales_response(cls, action: str, view: Dict) -> str:
        stats = {s["label"]: s["value"] for s in view.get("stats", [])}
        
        responses = {
            "show_dashboard": f"Wyświetlam dashboard sprzedaży. Suma sprzedaży wynosi {stats.get('Suma sprzedaży', '0 PLN')}. Zrealizowano {stats.get('Transakcji', 0)} transakcji. Średni wzrost: {stats.get('Śr. wzrost', '0%')}.",
            "compare_regions": f"Porównuję {stats.get('Regionów', 0)} regionów. Najlepszy wynik ma Warszawa.",
            "kpi_dashboard": "Wyświetlam dashboard KPI.",
            "forecast": "Generuję prognozę sprzedaży.",
            "funnel": "Wyświetlam lejek sprzedażowy.",
        }
        return responses.get(action, "Wyświetlam dane sprzedażowe.")
    
    @classmethod
    def _home_response(cls, action: str, view: Dict) -> str:
        stats = {s["label"]: s["value"] for s in view.get("stats", [])}
        
        responses = {
            "temperature": f"Temperatura w domu: {stats.get('Śr. temperatura', '21°C')}.",
            "lighting": f"Włączonych świateł: {stats.get('Światła włączone', 0)}.",
            "energy": f"Aktualne zużycie energii: {stats.get('Zużycie energii', '0 kW')}.",
            "power_usage": f"Zużycie prądu: {stats.get('Zużycie energii', '0 kW')}.",
            "show_all": f"Smart Home: temperatura {stats.get('Śr. temperatura', '21°C')}, zużycie {stats.get('Zużycie energii', '0 kW')}.",
        }
        return responses.get(action, f"Wyświetlam dashboard Smart Home. Temperatura: {stats.get('Śr. temperatura', '21°C')}.")
    
    @classmethod
    def _analytics_response(cls, action: str, view: Dict) -> str:
        stats = {s["label"]: s["value"] for s in view.get("stats", [])}
        
        responses = {
            "overview": f"Wyświetlam analitykę. Suma zdarzeń: {stats.get('Suma zdarzeń', 0)}, średnia dzienna: {stats.get('Średnia dzienna', 0)}.",
            "daily_report": "Generuję raport dzienny.",
            "weekly_report": "Generuję raport tygodniowy.",
            "monthly_report": "Generuję raport miesięczny.",
            "anomalies": "Analizuję anomalie w danych.",
            "prediction": "Generuję predykcję na podstawie danych historycznych.",
            "show_all": f"Analityka: {stats.get('Suma zdarzeń', 0)} zdarzeń w ostatnim tygodniu.",
        }
        return responses.get(action, f"Wyświetlam dashboard analityczny. Suma zdarzeń: {stats.get('Suma zdarzeń', 0)}.")
    
    @classmethod
    def _internet_response(cls, action: str, view: Dict) -> str:
        stats = {s["label"]: s["value"] for s in view.get("stats", [])}
        
        responses = {
            "weather": f"Pobieram dane pogodowe. Temperatura: {stats.get('Temperatura', 'ładowanie...')}.",
            "weather_warsaw": "Pobieram pogodę dla Warszawy.",
            "weather_krakow": "Pobieram pogodę dla Krakowa.",
            "crypto": f"Wyświetlam kursy kryptowalut. Bitcoin: {stats.get('Bitcoin (USD)', 'ładowanie...')}.",
            "exchange": "Pobieram kursy walut.",
            "rss": f"Wyświetlam kanały RSS. Załadowano {stats.get('Kanały', 0)} kanałów.",
            "news": "Pobieram najnowsze wiadomości.",
            "send_email": "Otwieram formularz wysyłki email.",
            "mqtt": f"MQTT broker: {stats.get('Broker', 'test.mosquitto.org')}. Gotowy do publikacji.",
            "webhook": f"Wyświetlam webhooks. Zarejestrowanych: {stats.get('Webhooks', 0)}.",
            "integrations": "Wyświetlam status wszystkich integracji internetowych.",
            "api_status": "Sprawdzam status API i usług zewnętrznych.",
        }
        return responses.get(action, "Wyświetlam integracje internetowe.")
    
    @classmethod
    def _system_response(cls, action: str) -> str:
        responses = {
            "help": "Wyświetlam 90+ dostępnych komend. Obsługuję dokumenty, kamery, sprzedaż, smart home, analitykę i integracje internetowe.",
            "clear": "Czyszczę widok.",
            "status": "System działa prawidłowo. Wszystkie komponenty aktywne.",
            "history": "Wyświetlam historię konwersacji.",
            "settings": "Otwieram ustawienia systemu.",
            "login": "Wyświetlam ekran logowania. Wpisz: login [użytkownik] [hasło]",
            "logout": "Wylogowano pomyślnie.",
            "whoami": "Sprawdzam aktualnego użytkownika.",
            "users": "Wyświetlam listę użytkowników systemu.",
            "welcome": "Wyświetlam dashboard z dostępnymi aplikacjami.",
        }
        return responses.get(action, "OK.")

# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """Manages user sessions, conversation history, and logging"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        logger.info("📋 SessionManager initialized")
    
    def create_session(self, session_id: str) -> Dict:
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "current_app": None,
            "history": [],
            "conversation": [],  # Full conversation log
            "data_cache": {}
        }
        logger.info(f"🆕 Session created: {session_id[:8]}...")
        conv_logger.info(f"SESSION_START | {session_id}")
        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, app_type: str, command: str, response: str = ""):
        if session_id in self.sessions:
            self.sessions[session_id]["current_app"] = app_type
            
            entry = {
                "command": command,
                "response": response,
                "app": app_type,
                "timestamp": datetime.now().isoformat()
            }
            self.sessions[session_id]["history"].append(entry)
            self.sessions[session_id]["conversation"].append(entry)
            
            # Log conversation
            conv_logger.info(f"USER | {session_id[:8]} | {command}")
            conv_logger.info(f"BOT  | {session_id[:8]} | {response[:100]}...")
            logger.debug(f"💬 Session {session_id[:8]}: {app_type}/{command[:30]}...")
    
    def get_conversation(self, session_id: str) -> List[Dict]:
        """Get full conversation history for a session"""
        if session_id in self.sessions:
            return self.sessions[session_id].get("conversation", [])
        return []
    
    def export_conversation(self, session_id: str) -> str:
        """Export conversation as formatted text"""
        conv = self.get_conversation(session_id)
        if not conv:
            return "Brak historii konwersacji."
        
        lines = [f"=== Konwersacja {session_id[:8]} ===\n"]
        for entry in conv:
            lines.append(f"[{entry['timestamp']}]")
            lines.append(f"👤 User: {entry['command']}")
            lines.append(f"🤖 Bot: {entry['response']}\n")
        return "\n".join(lines)
    
    def remove_session(self, session_id: str):
        if session_id in self.sessions:
            conv_logger.info(f"SESSION_END | {session_id} | {len(self.sessions[session_id].get('history', []))} messages")
            logger.info(f"🔚 Session ended: {session_id[:8]}...")
        self.sessions.pop(session_id, None)
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        return {
            "active_sessions": len(self.sessions),
            "total_messages": sum(len(s.get("history", [])) for s in self.sessions.values()),
            "sessions": [
                {
                    "id": sid[:8],
                    "messages": len(s.get("history", [])),
                    "current_app": s.get("current_app"),
                    "created_at": s.get("created_at")
                }
                for sid, s in self.sessions.items()
            ]
        }

session_manager = SessionManager()

# ============================================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        session_manager.create_session(client_id)
    
    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        session_manager.remove_session(client_id)
    
    async def send_message(self, client_id: str, message: Dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: Dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("frontend/index.html")

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    # Send welcome message
    welcome_view = ViewGenerator.generate("system", "welcome")
    await manager.send_message(client_id, {
        "type": "welcome",
        "message": "Połączono z Streamware. Powiedz komendę lub wpisz w chat.",
        "view": welcome_view
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "voice_command":
                command = data.get("text", "").strip()
                
                # Check for login command: "login username password"
                if command.lower().startswith("login "):
                    parts = command.split()
                    if len(parts) >= 3:
                        username = parts[1]
                        password = parts[2]
                        result = user_manager.login(client_id, username, password)
                        
                        if result["success"]:
                            user = user_manager.get_user(client_id)
                            permissions = user.permissions if user else []
                            view_data = ViewGenerator._generate_welcome_view(permissions)
                            response_text = f"Zalogowano jako {result['user']} ({result['role']}). Masz dostęp do: {', '.join(user_manager.get_allowed_apps(client_id))}"
                            await manager.send_message(client_id, {
                                "type": "login_success",
                                "user": result,
                                "response_text": response_text,
                                "view": view_data,
                                "timestamp": datetime.now().isoformat()
                            })
                        else:
                            await manager.send_message(client_id, {
                                "type": "login_failed",
                                "error": result["error"],
                                "response_text": result["error"],
                                "timestamp": datetime.now().isoformat()
                            })
                        continue
                
                # Check for logout command
                if command.lower() in ["logout", "wyloguj"]:
                    user_manager.logout(client_id)
                    view_data = ViewGenerator._generate_welcome_view()
                    await manager.send_message(client_id, {
                        "type": "logout",
                        "response_text": "Wylogowano pomyślnie.",
                        "view": view_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                # Check for whoami command
                if command.lower() in ["kto", "whoami"]:
                    user = user_manager.get_user(client_id)
                    if user:
                        response_text = f"Jesteś zalogowany jako: {user.display_name} (rola: {user_manager.ROLES[user.role]['display']})"
                        permissions = user.permissions
                    else:
                        response_text = "Nie jesteś zalogowany. Wpisz 'login' aby się zalogować."
                        permissions = ["system"]
                    
                    await manager.send_message(client_id, {
                        "type": "response",
                        "response_text": response_text,
                        "view": {"type": "system", "view": "whoami", "title": "👤 Użytkownik", "message": response_text},
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                # Process command
                intent = VoiceCommandProcessor.process(command)
                
                # Check permissions
                user = user_manager.get_user(client_id)
                app_type = intent["app_type"]
                
                if user and not user_manager.has_permission(client_id, app_type):
                    await manager.send_message(client_id, {
                        "type": "access_denied",
                        "response_text": f"🚫 Brak dostępu do: {app_type}. Twoja rola ({user_manager.ROLES[user.role]['display']}) nie ma uprawnień do tej funkcji.",
                        "view": ViewGenerator._generate_welcome_view(user.permissions),
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                # Generate view (use async for internet/weather to fetch real data)
                params = intent.get("params", {})
                if intent["app_type"] == "internet":
                    view_data = await ViewGenerator.generate_async(
                        intent["app_type"],
                        intent["action"],
                        params=params
                    )
                else:
                    view_data = ViewGenerator.generate(
                        intent["app_type"],
                        intent["action"]
                    )
                
                # Generate response
                response_text = ResponseGenerator.generate(intent, view_data)
                
                # Update session with response
                session_manager.update_session(client_id, intent["app_type"], command, response_text)
                
                # Send response
                await manager.send_message(client_id, {
                    "type": "response",
                    "intent": intent,
                    "response_text": response_text,
                    "view": view_data,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data.get("type") == "set_language":
                # Handle language change
                new_lang = data.get("language", "pl")
                language_manager.set_language(new_lang, client_id)
                lang_config = language_manager.get_language_for_llm(client_id)
                
                await manager.send_message(client_id, {
                    "type": "language_changed",
                    "language": new_lang,
                    "config": lang_config,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data.get("type") == "action":
                # Handle button actions (clicking on app/skill)
                action_id = data.get("action_id")
                app_type = data.get("app_type")
                cmd = data.get("command")  # Direct command from clicking skill
                
                if cmd:
                    # Execute the command directly
                    intent = VoiceCommandProcessor.process(cmd)
                    params = intent.get("params", {})
                    if intent["app_type"] == "internet":
                        view_data = await ViewGenerator.generate_async(intent["app_type"], intent["action"], params=params)
                    else:
                        view_data = ViewGenerator.generate(intent["app_type"], intent["action"])
                    response_text = ResponseGenerator.generate(intent, view_data)
                    
                    await manager.send_message(client_id, {
                        "type": "response",
                        "intent": intent,
                        "response_text": response_text,
                        "view": view_data,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    # Regenerate view with fresh data
                    view_data = ViewGenerator.generate(app_type, action_id)
                    
                    await manager.send_message(client_id, {
                        "type": "view_update",
                        "view": view_data,
                        "timestamp": datetime.now().isoformat()
                    })
            
            elif data.get("type") == "refresh":
                # Refresh current view with new data
                session = session_manager.get_session(client_id)
                if session and session.get("current_app"):
                    view_data = ViewGenerator.generate(session["current_app"], "refresh")
                    await manager.send_message(client_id, {
                        "type": "view_update", 
                        "view": view_data,
                        "timestamp": datetime.now().isoformat()
                    })
    
    except WebSocketDisconnect:
        user_manager.logout(client_id)
        manager.disconnect(client_id)

# Simulate camera stream endpoint
@app.get("/api/stream/{camera_id}")
async def camera_stream(camera_id: str):
    return {
        "camera_id": camera_id,
        "stream_type": "simulated",
        "message": "W prawdziwej implementacji tutaj byłby stream RTSP/MJPEG"
    }

# REST endpoint for testing
@app.post("/api/command")
async def process_command(command: Dict):
    text = command.get("text", "")
    logger.info(f"📨 REST command: {text}")
    intent = VoiceCommandProcessor.process(text)
    view_data = ViewGenerator.generate(intent["app_type"], intent["action"])
    response_text = ResponseGenerator.generate(intent, view_data)
    
    return {
        "intent": intent,
        "response": response_text,
        "view": view_data
    }

# Session and conversation endpoints
@app.get("/api/sessions")
async def get_sessions():
    """Get all active sessions and statistics"""
    return session_manager.get_stats()

@app.get("/api/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session"""
    conv = session_manager.get_conversation(session_id)
    return {"session_id": session_id, "conversation": conv}

@app.get("/api/conversation/{session_id}/export")
async def export_conversation(session_id: str):
    """Export conversation as text"""
    text = session_manager.export_conversation(session_id)
    return {"session_id": session_id, "export": text}

@app.get("/api/commands")
async def list_commands():
    """List all available commands (85+)"""
    intents = VoiceCommandProcessor._get_intents()
    return {
        "total_commands": len(intents),
        "categories": {
            "office": [k for k, v in intents.items() if v[0] == "documents"],
            "security": [k for k, v in intents.items() if v[0] == "cameras"],
            "sales": [k for k, v in intents.items() if v[0] == "sales"],
            "home": [k for k, v in intents.items() if v[0] == "home"],
            "analytics": [k for k, v in intents.items() if v[0] == "analytics"],
            "internet": [k for k, v in intents.items() if v[0] == "internet"],
            "system": [k for k, v in intents.items() if v[0] == "system"],
        }
    }

@app.get("/api/logs")
async def get_logs():
    """Get recent log entries"""
    log_file = LOGS_DIR / "streamware.log"
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-50:]  # Last 50 lines
        return {"logs": lines}
    return {"logs": []}

# ============================================================================
# INTERNET INTEGRATION API ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize integrations on startup"""
    await integrations.start()
    await llm_manager.start()
    
    # Register LLM providers from database
    for provider in db.get_llm_providers():
        llm_manager.register_provider(provider["id"], provider)
    
    # Set active LLM from config
    active_llm = db.get_active_llm()
    if active_llm:
        llm_manager.set_active(active_llm["id"], active_llm["default_model"])
    
    # Check service health
    await llm_manager.check_service_health()
    
    # Scan and load modular apps
    loaded_apps = app_registry.scan_apps()
    
    logger.info("🌐 Internet integrations started")
    logger.info("🤖 LLM manager started")
    logger.info(f"💾 Database: {db.db_path}")
    logger.info(f"📦 Apps loaded: {len(loaded_apps)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await integrations.stop()
    await llm_manager.stop()
    logger.info("🔌 Internet integrations stopped")
    logger.info("🤖 LLM manager stopped")

@app.get("/api/integrations/status")
async def integrations_status():
    """Get status of all internet integrations"""
    return integrations.get_status()

@app.get("/api/weather/{city}")
async def get_weather(city: str = "Warsaw"):
    """Get weather for a city"""
    return await integrations.get_weather(city)

@app.get("/api/crypto/{symbol}")
async def get_crypto(symbol: str = "bitcoin"):
    """Get cryptocurrency price"""
    return await integrations.fetch_crypto_price(symbol)

@app.get("/api/exchange/{base}")
async def get_exchange_rates(base: str = "EUR"):
    """Get exchange rates"""
    return await integrations.fetch_exchange_rates(base)

@app.get("/api/rss")
async def get_rss_feeds():
    """Get all RSS feeds"""
    return await integrations.fetch_rss()

@app.get("/api/rss/{feed_name}")
async def get_rss_feed(feed_name: str):
    """Get specific RSS feed"""
    if feed_name not in integrations.rss_feeds:
        raise HTTPException(status_code=404, detail=f"Feed '{feed_name}' not found")
    return await integrations.fetch_rss(feed_name)

@app.post("/api/rss")
async def add_rss_feed(feed: Dict):
    """Add new RSS feed"""
    name = feed.get("name")
    url = feed.get("url")
    if not name or not url:
        raise HTTPException(status_code=400, detail="Name and URL required")
    integrations.add_rss_feed(name, url)
    return {"success": True, "message": f"Feed '{name}' added"}

@app.get("/api/news/{query}")
async def get_news(query: str = "technology"):
    """Get news headlines"""
    return await integrations.fetch_news(query)

@app.post("/api/email")
async def send_email(email_data: Dict):
    """Send email (demo mode without credentials)"""
    to = email_data.get("to")
    subject = email_data.get("subject", "Streamware Notification")
    body = email_data.get("body", "")
    if not to:
        raise HTTPException(status_code=400, detail="Recipient email required")
    return await integrations.send_email(to, subject, body)

@app.post("/api/mqtt/publish")
async def mqtt_publish(mqtt_data: Dict):
    """Publish MQTT message"""
    topic = mqtt_data.get("topic", "streamware/test")
    payload = mqtt_data.get("payload", {})
    broker = mqtt_data.get("broker", "test.mosquitto.org")
    return await integrations.mqtt_publish(topic, payload, broker)

@app.post("/api/webhooks")
async def register_webhook(webhook: Dict):
    """Register a webhook"""
    event = webhook.get("event")
    url = webhook.get("url")
    if not event or not url:
        raise HTTPException(status_code=400, detail="Event and URL required")
    integrations.register_webhook(event, url)
    return {"success": True, "message": f"Webhook registered for '{event}'"}

@app.delete("/api/webhooks")
async def unregister_webhook(webhook: Dict):
    """Unregister a webhook"""
    event = webhook.get("event")
    url = webhook.get("url")
    if not event or not url:
        raise HTTPException(status_code=400, detail="Event and URL required")
    integrations.unregister_webhook(event, url)
    return {"success": True, "message": f"Webhook removed for '{event}'"}

@app.get("/api/webhooks")
async def list_webhooks():
    """List all registered webhooks"""
    return {"webhooks": integrations.webhooks}

@app.post("/api/webhooks/trigger/{event}")
async def trigger_webhook(event: str, payload: Dict):
    """Manually trigger webhooks for an event"""
    results = await integrations.trigger_webhook(event, payload)
    return {"event": event, "results": results}

@app.get("/api/http/test")
async def http_test():
    """Test HTTP client with a simple request"""
    result = await integrations.http_get("https://httpbin.org/get")
    return result

@app.post("/api/http/get")
async def http_get_proxy(request_data: Dict):
    """Make HTTP GET request to specified URL"""
    url = request_data.get("url")
    headers = request_data.get("headers", {})
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    return await integrations.http_get(url, headers)

@app.post("/api/http/post")
async def http_post_proxy(request_data: Dict):
    """Make HTTP POST request to specified URL"""
    url = request_data.get("url")
    data = request_data.get("data", {})
    headers = request_data.get("headers", {})
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
    return await integrations.http_post(url, data, headers)

# ============================================================================
# CONFIGURATION & ADMIN API ENDPOINTS
# ============================================================================

@app.get("/api/config")
async def get_all_config():
    """Get all configuration values"""
    return {
        "config": db.get_all_config(),
        "env": config.to_dict()
    }

@app.get("/api/config/{key}")
async def get_config_value(key: str):
    """Get specific configuration value"""
    value = db.get_config(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Config key '{key}' not found")
    return {"key": key, "value": value}

@app.put("/api/config/{key}")
async def set_config_value(key: str, data: Dict):
    """Set configuration value"""
    value = data.get("value")
    type_ = data.get("type", "string")
    description = data.get("description")
    db.set_config(key, value, type_, description)
    return {"success": True, "key": key, "value": value}

@app.post("/api/config/reload")
async def reload_configuration():
    """Reload configuration from .env file"""
    reload_config()
    return {"success": True, "message": "Configuration reloaded"}

# ============================================================================
# LLM MANAGEMENT API ENDPOINTS
# ============================================================================

@app.get("/api/llm/providers")
async def get_llm_providers():
    """Get all LLM providers"""
    return {
        "providers": llm_manager.get_providers_info(),
        "active": llm_manager.get_active()
    }

@app.get("/api/llm/active")
async def get_active_llm():
    """Get active LLM provider"""
    return llm_manager.get_active()

@app.post("/api/llm/active")
async def set_active_llm(data: Dict):
    """Set active LLM provider"""
    provider_id = data.get("provider")
    model = data.get("model")
    
    if not provider_id:
        raise HTTPException(status_code=400, detail="Provider ID required")
    
    success = llm_manager.set_active(provider_id, model)
    if success:
        db.set_active_llm(provider_id, model)
        return {"success": True, "provider": provider_id, "model": model}
    
    raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")

@app.get("/api/llm/models")
async def get_available_models():
    """Get available models for all providers"""
    return await llm_manager.get_available_models()

@app.get("/api/llm/models/{provider_id}")
async def get_provider_models(provider_id: str):
    """Get available models for specific provider"""
    models = await llm_manager.get_available_models(provider_id)
    return {"provider": provider_id, "models": models.get(provider_id, [])}

@app.get("/api/llm/health")
async def check_llm_health():
    """Check health of all LLM services"""
    return await llm_manager.check_service_health()

@app.post("/api/llm/chat")
async def llm_chat(data: Dict):
    """Send chat message to LLM"""
    message = data.get("message", "")
    system_prompt = data.get("system_prompt")
    history = data.get("history", [])
    
    if not message:
        raise HTTPException(status_code=400, detail="Message required")
    
    response = await llm_manager.chat(message, system_prompt, history)
    return {
        "content": response.content,
        "model": response.model,
        "provider": response.provider,
        "tokens_used": response.tokens_used,
        "error": response.error
    }

@app.put("/api/llm/providers/{provider_id}")
async def update_llm_provider(provider_id: str, data: Dict):
    """Update LLM provider configuration"""
    db.update_llm_provider(provider_id, **data)
    
    # Re-register provider
    providers = db.get_llm_providers()
    for p in providers:
        if p["id"] == provider_id:
            llm_manager.register_provider(provider_id, p)
            break
    
    return {"success": True, "provider": provider_id}

# ============================================================================
# DATABASE / CONVERSATIONS API ENDPOINTS
# ============================================================================

@app.get("/api/db/conversations")
async def get_conversations(limit: int = 100, offset: int = 0):
    """Get all conversations (admin)"""
    return {"conversations": db.get_all_conversations(limit, offset)}

@app.get("/api/db/conversations/{session_id}")
async def get_session_conversations(session_id: str, limit: int = 50):
    """Get conversation history for session"""
    return {"history": db.get_conversation_history(session_id, limit)}

@app.get("/api/db/sessions")
async def get_active_sessions():
    """Get all active sessions"""
    return {"sessions": db.get_active_sessions()}

@app.get("/api/db/services")
async def get_services():
    """Get all registered services"""
    return {"services": db.get_services()}

@app.post("/api/db/services/{service_id}/check")
async def check_service(service_id: str):
    """Check service health and update status"""
    service = db.get_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found")
    
    # Check based on service type
    if service["type"] == "llm":
        health = await llm_manager.check_service_health(service_id)
        status = health.get(service_id, {}).get("status", "unknown")
        error = health.get(service_id, {}).get("error")
    else:
        # Simple HTTP check for other services
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(service["url"])
                status = "healthy" if response.status_code < 400 else "error"
                error = None if status == "healthy" else f"HTTP {response.status_code}"
        except Exception as e:
            status = "offline"
            error = str(e)
    
    db.update_service_status(service_id, status, error)
    return {"service": service_id, "status": status, "error": error}

# ============================================================================
# SIMPLIFIED INTERFACE - PREDEFINED OPTIONS PER APP
# ============================================================================

@app.get("/api/app/{app_type}/options")
async def get_app_options(app_type: str):
    """Get predefined options/commands for specific app"""
    app_data = SkillRegistry.get_app(app_type)
    if not app_data:
        raise HTTPException(status_code=404, detail=f"App '{app_type}' not found")
    
    return {
        "app": app_type,
        "name": app_data["name"],
        "description": app_data["description"],
        "options": app_data["skills"],
        "quick_actions": [s["cmd"] for s in app_data["skills"][:4]]
    }

@app.get("/api/breadcrumbs")
async def get_breadcrumbs(app_type: str = "welcome", action: str = None):
    """Get breadcrumb navigation data"""
    breadcrumbs = [{"label": "🏠 Home", "cmd": "start", "app": "welcome"}]
    
    if app_type != "welcome":
        app_data = SkillRegistry.get_app(app_type)
        if app_data:
            breadcrumbs.append({
                "label": app_data["name"],
                "cmd": app_data["skills"][0]["cmd"] if app_data["skills"] else "",
                "app": app_type
            })
    
    if action:
        breadcrumbs.append({"label": action, "cmd": "", "app": app_type})
    
    return {"breadcrumbs": breadcrumbs, "current_app": app_type}

# ============================================================================
# MODULAR APPS API ENDPOINTS
# ============================================================================

@app.get("/api/apps")
async def get_all_apps():
    """Get all loaded modular apps"""
    return {"apps": app_registry.get_apps_summary()}

@app.get("/api/apps/{app_id}")
async def get_app_details(app_id: str):
    """Get details for specific app"""
    app = app_registry.get_app(app_id)
    if not app:
        raise HTTPException(status_code=404, detail=f"App not found: {app_id}")
    return {
        "id": app.id,
        "name": app.name,
        "version": app.version,
        "description": app.description,
        "language": app.language,
        "commands": app.commands,
        "scripts": app.scripts,
        "error_handling": app.error_handling,
        "ui": app.ui,
        "status": app.status
    }

@app.post("/api/apps/{app_id}/run/{script_name}")
async def run_app_script(app_id: str, script_name: str, args: Dict = None):
    """Run app script"""
    script_args = args.get("args", []) if args else []
    result = app_registry.run_script(app_id, script_name, *script_args)
    return result

@app.post("/api/apps/{app_id}/make/{target}")
async def run_app_make(app_id: str, target: str, params: Dict = None):
    """Run Makefile target for app"""
    kwargs = params or {}
    result = app_registry.run_make(app_id, target, **kwargs)
    return result

@app.get("/api/apps/{app_id}/health")
async def check_app_health(app_id: str):
    """Check app health"""
    return app_registry.check_app_health(app_id)

@app.post("/api/apps/{app_id}/reload")
async def reload_app(app_id: str):
    """Reload app manifest"""
    success = app_registry.reload_app(app_id)
    return {"success": success, "app": app_id}

@app.post("/api/apps/scan")
async def scan_apps():
    """Rescan apps folder"""
    loaded = app_registry.scan_apps()
    return {"loaded": loaded, "count": len(loaded)}

# ============================================================================
# LLM CODE EDITING API ENDPOINTS
# ============================================================================

@app.get("/api/apps/{app_id}/files")
async def get_app_files(app_id: str):
    """Get list of files in app for LLM editing"""
    files = app_registry.get_app_files(app_id)
    if not files:
        raise HTTPException(status_code=404, detail=f"App not found: {app_id}")
    return {"app": app_id, "files": files}

@app.get("/api/apps/{app_id}/files/{file_path:path}")
async def read_app_file(app_id: str, file_path: str):
    """Read file content from app"""
    content = app_registry.read_app_file(app_id, file_path)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    return {"app": app_id, "file": file_path, "content": content}

@app.put("/api/apps/{app_id}/files/{file_path:path}")
async def write_app_file(app_id: str, file_path: str, data: Dict):
    """Write file content to app (LLM editing)"""
    content = data.get("content", "")
    success = app_registry.write_app_file(app_id, file_path, content)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to write file")
    return {"success": True, "app": app_id, "file": file_path}

@app.post("/api/apps/{app_id}/fix")
async def llm_fix_app_code(app_id: str, data: Dict):
    """Let LLM analyze and fix app code"""
    file_path = data.get("file")
    issue = data.get("issue", "")
    
    # Read current file
    content = app_registry.read_app_file(app_id, file_path)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Ask LLM to fix
    prompt = f"""Analyze and fix this code. Issue: {issue}

File: {file_path}
```
{content}
```

Return ONLY the fixed code, no explanations."""
    
    response = await llm_manager.chat(prompt, system_prompt="You are a code fixer. Return only fixed code.")
    
    if response.error:
        return {"success": False, "error": response.error}
    
    # Write fixed code
    fixed_content = response.content.strip()
    if fixed_content.startswith("```"):
        # Remove markdown code blocks
        lines = fixed_content.split("\n")
        fixed_content = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])
    
    success = app_registry.write_app_file(app_id, file_path, fixed_content)
    
    return {
        "success": success,
        "app": app_id,
        "file": file_path,
        "fixed_by": response.model
    }

# ============================================================================
# APP LOGS API ENDPOINTS
# ============================================================================

@app.get("/api/apps/{app_id}/logs")
async def get_app_logs(app_id: str, lines: int = 50):
    """Get recent logs for an app"""
    return app_registry.get_app_logs(app_id, lines)

@app.get("/api/apps/{app_id}/logs/yaml")
async def get_app_yaml_logs(app_id: str):
    """Get YAML formatted logs for LLM context"""
    yaml_logs = app_registry.get_app_yaml_logs(app_id)
    return {"app": app_id, "yaml_logs": yaml_logs}

@app.get("/api/apps/{app_id}/logs/errors")
async def get_app_errors(app_id: str, lines: int = 20):
    """Get recent errors for an app"""
    errors = app_registry.get_app_errors(app_id, lines)
    return {"app": app_id, "errors": errors}

@app.get("/api/apps/{app_id}/context")
async def get_app_context(app_id: str):
    """Get full app context for LLM debugging/fixing"""
    return app_registry.get_app_context_for_llm(app_id)

@app.post("/api/apps/{app_id}/debug")
async def llm_debug_app(app_id: str, data: Dict = None):
    """Let LLM analyze app logs and suggest fixes"""
    context = app_registry.get_app_context_for_llm(app_id)
    
    if "error" in context:
        raise HTTPException(status_code=404, detail=context["error"])
    
    issue = data.get("issue", "") if data else ""
    
    # Build prompt with app context
    prompt = f"""Analyze this app and its logs. Suggest fixes if there are errors.

App: {context['app_id']} ({context['name']})
Language: {context['language']}
Status: {context['status']}
Last Error: {context.get('last_error', 'None')}

Recent Errors:
{chr(10).join(context['recent_errors'][-5:]) if context['recent_errors'] else 'No errors'}

Recent Logs:
{chr(10).join(context['recent_logs'][-10:]) if context['recent_logs'] else 'No logs'}

Issue reported: {issue}

Provide:
1. Analysis of the problem
2. Suggested fix (if applicable)
3. Commands to run to fix it
"""
    
    response = await llm_manager.chat(prompt, system_prompt="You are an app debugger. Analyze logs and suggest fixes.")
    
    return {
        "app": app_id,
        "analysis": response.content,
        "model": response.model,
        "context_used": {
            "logs_count": len(context['recent_logs']),
            "errors_count": len(context['recent_errors'])
        }
    }

# ============================================================================
# TEXT2MAKEFILE / MAKEFILE2TEXT API ENDPOINTS
# ============================================================================

@app.post("/api/text2makefile")
async def text_to_makefile(data: Dict):
    """Convert natural language to Makefile command"""
    text = data.get("text", "")
    app_id = data.get("app_id")
    role = data.get("role", "user")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text required")
    
    return makefile_converter.text2makefile(text, app_id, role)

@app.post("/api/makefile2text")
async def makefile_to_text(data: Dict):
    """Convert Makefile command to natural language"""
    command = data.get("command", "")
    app_id = data.get("app_id")
    
    if not command:
        raise HTTPException(status_code=400, detail="Command required")
    
    return makefile_converter.makefile2text(command, app_id)

@app.get("/api/apps/{app_id}/makefiles")
async def get_app_makefiles(app_id: str):
    """Get all Makefile commands organized by role"""
    return {
        "app": app_id,
        "commands": makefile_converter.get_all_commands(app_id)
    }

@app.get("/api/apps/{app_id}/makefiles/{role}")
async def get_app_makefile_by_role(app_id: str, role: str):
    """Get Makefile commands for specific role (user/admin/system)"""
    all_commands = makefile_converter.get_all_commands(app_id)
    
    if role not in all_commands:
        raise HTTPException(status_code=404, detail=f"Role '{role}' not found")
    
    return {
        "app": app_id,
        "role": role,
        "commands": all_commands[role]
    }

@app.post("/api/apps/{app_id}/execute")
async def execute_app_command(app_id: str, data: Dict):
    """Execute command (text or make) for an app"""
    text_or_command = data.get("command") or data.get("text", "")
    is_text = data.get("is_text", True)
    
    if not text_or_command:
        raise HTTPException(status_code=400, detail="Command or text required")
    
    # Log to app
    app_registry.log_app_command(app_id, text_or_command, {"type": "execute"})
    
    result = makefile_converter.execute(app_id, text_or_command, is_text)
    
    return result

@app.get("/api/apps/{app_id}/suggestions")
async def get_command_suggestions(app_id: str, role: str = "user"):
    """Get command suggestions for an app"""
    suggestions = makefile_converter.get_suggestions(app_id, role)
    return {"app": app_id, "role": role, "suggestions": suggestions}

# ============================================================================
# REGISTRY MANAGER API ENDPOINTS
# ============================================================================

@app.get("/api/registries")
async def get_all_registries():
    """Get all configured registries"""
    return {"registries": registry_manager.get_all_registries()}

@app.post("/api/registries")
async def add_registry(data: Dict):
    """Add new external registry"""
    success = registry_manager.add_registry(data)
    return {"success": success}

@app.get("/api/registries/{registry_id}")
async def get_registry(registry_id: str):
    """Get registry details"""
    reg = registry_manager.get_registry(registry_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registry not found")
    return {"registry": vars(reg)}

@app.put("/api/registries/{registry_id}")
async def update_registry(registry_id: str, data: Dict):
    """Update registry settings"""
    success = registry_manager.update_registry(registry_id, data)
    return {"success": success}

@app.delete("/api/registries/{registry_id}")
async def delete_registry(registry_id: str):
    """Remove registry"""
    success = registry_manager.remove_registry(registry_id)
    return {"success": success}

@app.post("/api/registries/{registry_id}/sync")
async def sync_registry(registry_id: str):
    """Sync apps from registry"""
    result = await registry_manager.sync_registry(registry_id)
    return result

@app.post("/api/registries/sync-all")
async def sync_all_registries():
    """Sync all enabled registries"""
    results = {}
    for reg_id, reg in registry_manager.registries.items():
        if reg.enabled:
            results[reg_id] = await registry_manager.sync_registry(reg_id)
    return {"results": results}

@app.get("/api/external-apps")
async def get_external_apps(registry: str = None):
    """Get external apps, optionally filtered by registry"""
    return {"apps": registry_manager.get_external_apps(registry)}

@app.post("/api/external-apps")
async def add_external_app(data: Dict):
    """Add external app to system"""
    success = registry_manager.add_external_app(data)
    return {"success": success}

@app.delete("/api/external-apps/{app_id}")
async def remove_external_app(app_id: str):
    """Remove external app"""
    success = registry_manager.remove_external_app(app_id)
    return {"success": success}

@app.post("/api/external-apps/{app_id}/install")
async def install_external_app(app_id: str):
    """Install external app"""
    return registry_manager.install_external_app(app_id)

@app.post("/api/external-apps/{app_id}/access")
async def manage_external_app_access(app_id: str, data: Dict):
    """Grant or revoke access to external app"""
    role = data.get("role")
    user = data.get("user")
    grant = data.get("grant", True)
    
    if role:
        if grant:
            success = registry_manager.grant_access(app_id, role, is_role=True)
        else:
            success = registry_manager.revoke_access(app_id, role, is_role=True)
    elif user:
        if grant:
            success = registry_manager.grant_access(app_id, user, is_role=False)
        else:
            success = registry_manager.revoke_access(app_id, user, is_role=False)
    else:
        raise HTTPException(status_code=400, detail="Role or user required")
    
    return {"success": success}

# ============================================================================
# UNIFIED APP COMMAND EXECUTION (text2makefile integration)
# ============================================================================

@app.post("/api/command/execute")
async def execute_unified_command(data: Dict):
    """
    Execute command via text2makefile
    Unified entry point for all app commands
    """
    text = data.get("text", "")
    app_id = data.get("app_id")
    role = data.get("role", "user")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text required")
    
    # Convert text to makefile command
    conversion = makefile_converter.text2makefile(text, app_id, role)
    
    if not conversion["success"]:
        return conversion
    
    # Execute if app_id provided
    if app_id:
        result = makefile_converter.execute(app_id, conversion["command"], is_text=False)
        result["conversion"] = conversion
        
        # Log to app
        app_registry.log_app_command(app_id, text, result)
        
        return result
    
    return conversion

# ============================================================================
# LANGUAGE MANAGEMENT API ENDPOINTS
# ============================================================================

@app.get("/api/languages")
async def get_available_languages():
    """Get available languages"""
    return {"languages": language_manager.get_available_languages()}

@app.get("/api/language")
async def get_current_language(session_id: str = None):
    """Get current language"""
    lang = language_manager.get_language(session_id)
    return {
        "language": lang,
        "tts": language_manager.get_tts_config(session_id),
        "stt": language_manager.get_stt_config(session_id)
    }

@app.post("/api/language")
async def set_language(data: Dict):
    """Set language for session or globally"""
    lang = data.get("language")
    session_id = data.get("session_id")
    
    if not lang:
        raise HTTPException(status_code=400, detail="Language required")
    
    success = language_manager.set_language(lang, session_id)
    return {"success": success, "language": lang}

@app.get("/api/translations")
async def get_translations(session_id: str = None):
    """Get all translations for current language"""
    return {
        "language": language_manager.get_language(session_id),
        "translations": language_manager.get_all_translations(session_id)
    }

@app.get("/api/tts/config")
async def get_tts_config(session_id: str = None):
    """Get TTS configuration for current language"""
    return language_manager.get_tts_config(session_id)

@app.get("/api/stt/config")
async def get_stt_config(session_id: str = None):
    """Get STT configuration for current language"""
    return language_manager.get_stt_config(session_id)

# ============================================================================
# APP GENERATOR API ENDPOINTS
# ============================================================================

@app.get("/api/generator/registries")
async def get_library_registries():
    """Get available library registries (npm, pypi, docker, etc.)"""
    return {"registries": app_generator.get_available_registries()}

@app.post("/api/generator/search")
async def search_library_registry(data: Dict):
    """Search library registry"""
    registry_id = data.get("registry")
    query = data.get("query")
    
    if not registry_id or not query:
        raise HTTPException(status_code=400, detail="Registry and query required")
    
    results = await app_generator.search_registry(registry_id, query)
    return {"registry": registry_id, "query": query, "results": results}

@app.post("/api/generator/from-package")
async def generate_app_from_package(data: Dict):
    """Generate app from package (npm, pypi, docker)"""
    registry_id = data.get("registry")
    package_name = data.get("package")
    app_id = data.get("app_id")
    description = data.get("description", "")
    
    if not registry_id or not package_name:
        raise HTTPException(status_code=400, detail="Registry and package required")
    
    result = await app_generator.generate_app_from_package(
        registry_id, package_name, app_id, description
    )
    
    # Reload apps after generation
    if result.get("success"):
        app_registry.scan_apps()
    
    return result

@app.post("/api/generator/from-api-docs")
async def generate_app_from_api_docs(data: Dict):
    """Generate app from API documentation URL"""
    api_docs_url = data.get("url")
    app_id = data.get("app_id")
    app_name = data.get("app_name")
    
    if not api_docs_url:
        raise HTTPException(status_code=400, detail="API docs URL required")
    
    # Inject LLM manager
    app_generator.llm_manager = llm_manager
    
    result = await app_generator.generate_app_from_api_docs(
        api_docs_url, app_id, app_name
    )
    
    # Reload apps after generation
    if result.get("success"):
        app_registry.scan_apps()
    
    return result

@app.post("/api/generator/makefiles")
async def generate_makefiles_for_repo(data: Dict):
    """Generate Makefiles for repository without them"""
    repo_path = data.get("path")
    app_id = data.get("app_id")
    
    if not repo_path:
        raise HTTPException(status_code=400, detail="Repository path required")
    
    from pathlib import Path
    repo_path = Path(repo_path)
    
    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository path not found")
    
    # Inject LLM manager
    app_generator.llm_manager = llm_manager
    
    result = await app_generator.generate_makefiles_for_repo(repo_path, app_id)
    
    # Reload apps after generation
    if result.get("success"):
        app_registry.scan_apps()
    
    return result

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

logger.info("✅ All API endpoints registered")
logger.info(f"📊 Available commands: {len(VoiceCommandProcessor._get_intents())}")
logger.info("🌐 Internet integration endpoints ready")
logger.info("🤖 LLM management endpoints ready")
logger.info("⚙️ Configuration endpoints ready")
logger.info("📦 Modular apps endpoints ready")

if __name__ == "__main__":
    logger.info(f"🌐 Starting server on http://0.0.0.0:{config.server.port}")
    uvicorn.run(app, host=config.server.host, port=config.server.port)
