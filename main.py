"""
STREAMWARE MVP - Voice-Controlled Dashboard Platform
Main FastAPI application with WebSocket for real-time voice interaction
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Streamware MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    Simulates intent recognition without actual LLM
    """
    
    INTENTS = {
        # Document commands
        "pokaż faktury": ("documents", "show_all"),
        "zeskanuj fakturę": ("documents", "scan_new"),
        "ile faktur": ("documents", "count"),
        "faktury do zapłaty": ("documents", "filter_unpaid"),
        "suma faktur": ("documents", "sum_total"),
        "znajdź fakturę": ("documents", "search"),
        "dokumenty": ("documents", "show_all"),
        "faktury": ("documents", "show_all"),
        
        # Camera commands
        "pokaż kamery": ("cameras", "show_grid"),
        "monitoring": ("cameras", "show_grid"),
        "kamera": ("cameras", "show_single"),
        "gdzie ruch": ("cameras", "show_motion"),
        "alerty": ("cameras", "show_alerts"),
        "nagraj": ("cameras", "record"),
        "ile osób": ("cameras", "count_people"),
        
        # Sales commands
        "sprzedaż": ("sales", "show_dashboard"),
        "pokaż sprzedaż": ("sales", "show_dashboard"),
        "raport": ("sales", "show_report"),
        "porównaj regiony": ("sales", "compare_regions"),
        "top produkty": ("sales", "top_products"),
        "trend": ("sales", "show_trend"),
        
        # System commands
        "pomoc": ("system", "help"),
        "wyczyść": ("system", "clear"),
        "status": ("system", "status"),
    }
    
    @classmethod
    def process(cls, command: str) -> Dict[str, Any]:
        """Process voice command and return intent + parameters"""
        command_lower = command.lower().strip()
        
        # Find matching intent
        for pattern, (app_type, action) in cls.INTENTS.items():
            if pattern in command_lower:
                return {
                    "recognized": True,
                    "app_type": app_type,
                    "action": action,
                    "original_command": command,
                    "confidence": random.uniform(0.85, 0.99)
                }
        
        # Default - try to guess
        if any(word in command_lower for word in ["faktur", "dokument", "skan"]):
            return {"recognized": True, "app_type": "documents", "action": "show_all", 
                    "original_command": command, "confidence": 0.7}
        if any(word in command_lower for word in ["kamer", "monitor", "wideo", "obraz"]):
            return {"recognized": True, "app_type": "cameras", "action": "show_grid",
                    "original_command": command, "confidence": 0.7}
        if any(word in command_lower for word in ["sprzeda", "raport", "kpi", "wynik"]):
            return {"recognized": True, "app_type": "sales", "action": "show_dashboard",
                    "original_command": command, "confidence": 0.7}
        
        return {
            "recognized": False,
            "app_type": "system",
            "action": "unknown",
            "original_command": command,
            "confidence": 0.0
        }

# ============================================================================
# DYNAMIC VIEW GENERATOR
# ============================================================================

class ViewGenerator:
    """Generates dynamic dashboard views based on app type and action"""
    
    @classmethod
    def generate(cls, app_type: str, action: str, data: Any = None) -> Dict[str, Any]:
        """Generate view configuration for frontend"""
        
        if app_type == "documents":
            return cls._generate_documents_view(action, data)
        elif app_type == "cameras":
            return cls._generate_cameras_view(action, data)
        elif app_type == "sales":
            return cls._generate_sales_view(action, data)
        elif app_type == "system":
            return cls._generate_system_view(action)
        else:
            return cls._generate_empty_view()
    
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
    def _generate_system_view(cls, action: str) -> Dict:
        if action == "help":
            return {
                "type": "system",
                "view": "help",
                "title": "❓ Pomoc - Dostępne komendy",
                "commands": [
                    {"category": "Dokumenty", "commands": [
                        "pokaż faktury", "zeskanuj fakturę", "ile faktur", "suma faktur"
                    ]},
                    {"category": "Kamery", "commands": [
                        "pokaż kamery", "monitoring", "gdzie ruch", "alerty"
                    ]},
                    {"category": "Sprzedaż", "commands": [
                        "pokaż sprzedaż", "raport", "porównaj regiony", "trend"
                    ]},
                    {"category": "System", "commands": [
                        "pomoc", "wyczyść", "status"
                    ]},
                ]
            }
        else:
            return cls._generate_empty_view()
    
    @classmethod
    def _generate_empty_view(cls) -> Dict:
        return {
            "type": "empty",
            "view": "welcome",
            "title": "👋 Witaj w Streamware",
            "message": "Powiedz komendę głosową lub wpisz w chat, np.:\n• 'Pokaż faktury'\n• 'Monitoring kamer'\n• 'Sprzedaż w tym miesiącu'"
        }

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
        }
        return responses.get(action, f"Wyświetlam dokumenty. Znaleziono {stats.get('Dokumentów', 0)} pozycji.")
    
    @classmethod
    def _cameras_response(cls, action: str, view: Dict) -> str:
        stats = {s["label"]: s["value"] for s in view.get("stats", [])}
        
        responses = {
            "show_grid": f"Wyświetlam podgląd kamer. {stats.get('Kamery online', '0/0')} online. Wykryto {stats.get('Wykryte obiekty', 0)} obiektów. {stats.get('Aktywne alerty', 0)} aktywnych alertów.",
            "show_motion": f"Ostatni ruch wykryty o {stats.get('Ostatni ruch', '-')}. Aktualnie wykrytych obiektów: {stats.get('Wykryte obiekty', 0)}.",
            "show_alerts": f"Masz {stats.get('Aktywne alerty', 0)} aktywnych alertów.",
        }
        return responses.get(action, "Wyświetlam monitoring kamer.")
    
    @classmethod
    def _sales_response(cls, action: str, view: Dict) -> str:
        stats = {s["label"]: s["value"] for s in view.get("stats", [])}
        
        responses = {
            "show_dashboard": f"Wyświetlam dashboard sprzedaży. Suma sprzedaży wynosi {stats.get('Suma sprzedaży', '0 PLN')}. Zrealizowano {stats.get('Transakcji', 0)} transakcji. Średni wzrost: {stats.get('Śr. wzrost', '0%')}.",
            "compare_regions": f"Porównuję {stats.get('Regionów', 0)} regionów. Najlepszy wynik ma Warszawa.",
        }
        return responses.get(action, "Wyświetlam dane sprzedażowe.")
    
    @classmethod
    def _system_response(cls, action: str) -> str:
        responses = {
            "help": "Wyświetlam dostępne komendy. Możesz sterować dokumentami, kamerami i dashboardem sprzedaży.",
            "clear": "Czyszczę widok.",
            "status": "System działa prawidłowo. Wszystkie komponenty aktywne.",
        }
        return responses.get(action, "OK.")

# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """Manages user sessions and state"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, session_id: str) -> Dict:
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "current_app": None,
            "history": [],
            "data_cache": {}
        }
        return self.sessions[session_id]
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, app_type: str, command: str):
        if session_id in self.sessions:
            self.sessions[session_id]["current_app"] = app_type
            self.sessions[session_id]["history"].append({
                "command": command,
                "app": app_type,
                "timestamp": datetime.now().isoformat()
            })
    
    def remove_session(self, session_id: str):
        self.sessions.pop(session_id, None)

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
                command = data.get("text", "")
                
                # Process command
                intent = VoiceCommandProcessor.process(command)
                
                # Generate view
                view_data = ViewGenerator.generate(
                    intent["app_type"],
                    intent["action"]
                )
                
                # Generate response
                response_text = ResponseGenerator.generate(intent, view_data)
                
                # Update session
                session_manager.update_session(client_id, intent["app_type"], command)
                
                # Send response
                await manager.send_message(client_id, {
                    "type": "response",
                    "intent": intent,
                    "response_text": response_text,
                    "view": view_data,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data.get("type") == "action":
                # Handle button actions
                action_id = data.get("action_id")
                app_type = data.get("app_type")
                
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
    intent = VoiceCommandProcessor.process(text)
    view_data = ViewGenerator.generate(intent["app_type"], intent["action"])
    response_text = ResponseGenerator.generate(intent, view_data)
    
    return {
        "intent": intent,
        "response": response_text,
        "view": view_data
    }

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
