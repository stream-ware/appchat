# 🎤 Streamware appchat - Voice-Controlled Dashboard Platform

**Głosowa platforma AI do generowania kontekstowych aplikacji w locie**

> "Mów co chcesz - system wykonuje"

## 📋 Spis treści

- [Opis](#-opis)
- [Architektura](#-architektura)
- [Quick Start](#-quick-start)
- [Funkcjonalności](#-funkcjonalności)
- [API Reference](#-api-reference)
- [Komendy głosowe](#-komendy-głosowe)
- [Development](#-development)

---

## 📖 Opis

Streamware MVP to proof-of-concept głosowej platformy do sterowania dashboardami i generowania kontekstowych widoków w czasie rzeczywistym.

### Kluczowe cechy:

- **Voice-first interface** - STT/TTS jako primary input/output
- **Dynamic view generation** - widoki generowane w locie na podstawie komendy
- **80/20 layout** - 80% app view, 20% chat interface
- **3 zastosowania demo:**
  - 📄 **Documents** - tabela zeskanowanych faktur
  - 🎥 **Cameras** - grid 2x2 monitoringu
  - 📊 **Sales** - dashboard z wykresami

### Tech Stack:

- **Backend:** Python 3.11 + FastAPI + WebSocket
- **Frontend:** Vanilla HTML/CSS/JS (zero dependencies)
- **Deployment:** Docker + Docker Compose

---

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BROWSER (Client)                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │               80% APP VIEW               │  20% CHAT        │   │
│  │  ┌─────────────────────────────────┐    │  ┌─────────────┐ │   │
│  │  │  Dynamic Content:               │    │  │ Voice Input │ │   │
│  │  │  • Tables (documents)           │    │  │ Chat Msgs   │ │   │
│  │  │  • Grid (cameras)               │    │  │ Text Input  │ │   │
│  │  │  • Charts (sales)               │    │  └─────────────┘ │   │
│  │  │  • Stats cards                  │    │                  │   │
│  │  └─────────────────────────────────┘    │                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                      WebSocket Connection                           │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        FASTAPI SERVER                                │
│                                                                      │
│   ┌────────────────┐    ┌────────────────┐    ┌────────────────┐    │
│   │ Voice Command  │───▶│ Intent Parser  │───▶│ View Generator │    │
│   │ Processor      │    │                │    │                │    │
│   └────────────────┘    └────────────────┘    └────────────────┘    │
│          │                                            │              │
│          │              ┌────────────────┐            │              │
│          └─────────────▶│ Response       │◀───────────┘              │
│                         │ Generator      │                           │
│                         │ (TTS Text)     │                           │
│                         └────────────────┘                           │
│                                                                      │
│   Data Simulators:                                                   │
│   • DocumentSimulator  →  Faktury, NIP, kwoty                       │
│   • CameraSimulator    →  Feeds, detekcje, alerty                   │
│   • SalesSimulator     →  Regiony, KPI, trendy                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Flow przetwarzania komendy:

```
User Voice/Text
      │
      ▼
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│ STT         │────▶│ Intent       │────▶│ View           │
│ (browser)   │     │ Recognition  │     │ Generator      │
└─────────────┘     └──────────────┘     └────────────────┘
                           │                     │
                           ▼                     ▼
                    ┌─────────────┐       ┌─────────────┐
                    │ App Type    │       │ View Config │
                    │ + Action    │       │ + Data      │
                    └─────────────┘       └─────────────┘
                           │                     │
                           └──────────┬──────────┘
                                      ▼
                           ┌─────────────────┐
                           │ Response        │
                           │ (TTS + View)    │
                           └─────────────────┘
                                      │
                                      ▼
                           ┌─────────────────┐
                           │ Browser renders │
                           │ + speaks        │
                           └─────────────────┘
```

---

## 🚀 Quick Start

### Wymagania:

- Docker 20.10+
- Docker Compose 2.0+

### Start:

```bash
# Clone or navigate to directory
cd streamware-mvp

# Make start script executable
chmod +x start.sh

# Start in production mode
./start.sh prod

# Or start in development mode (hot reload)
./start.sh dev
```

### Bez Dockera:

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
cd streamware-mvp
python -m uvicorn backend.main:app --reload --port 8000

# Open browser
open http://localhost:8000
```

### Test:

```bash
# Run automated tests
./start.sh test

# Or manually
python scripts/test_demo.py
```

---

## 🎯 Funkcjonalności

### 1. 📄 Document Scanner View

**Komenda:** `"Pokaż faktury"` / `"Dokumenty"` / `"Zeskanuj fakturę"`

**Widok:**
- Stats: liczba dokumentów, suma brutto, do zapłaty, dostawcy
- Tabela: plik, dostawca, NIP, kwota, data, status
- Actions: Skanuj, Eksportuj, Filtruj

```
┌────────────────────────────────────────────────────────┐
│ 📄 8 docs │ 💰 45,230 PLN │ ⏰ 3 unpaid │ 🏢 5 vendors │
├────────────────────────────────────────────────────────┤
│ File          │ Vendor      │ Amount    │ Status      │
│ FV_001.pdf    │ ABC Sp.     │ 12,300 PLN│ ✓ Paid      │
│ FV_002.pdf    │ XYZ S.A.    │ 8,500 PLN │ ⏰ Due      │
│ ...           │ ...         │ ...       │ ...         │
└────────────────────────────────────────────────────────┘
```

### 2. 🎥 Camera Monitoring View

**Komenda:** `"Pokaż kamery"` / `"Monitoring"` / `"Gdzie ruch"`

**Widok:**
- Stats: kamery online, wykryte obiekty, alerty, ostatni ruch
- Grid 2x2: symulowane feedy z kamer
- Indicators: status, detekcje, alerts

```
┌─────────────────────┬─────────────────────┐
│ 📹 Wejście główne   │ 📹 Parking A        │
│ ● Online            │ ● Online            │
│ 👤 2 detected       │ 🚗 1 detected       │
├─────────────────────┼─────────────────────┤
│ 📹 Magazyn          │ 📵 Korytarz 1       │
│ ● Online            │ ○ Offline           │
│ 👤 0 detected       │                     │
└─────────────────────┴─────────────────────┘
```

### 3. 📊 Sales Dashboard View

**Komenda:** `"Pokaż sprzedaż"` / `"Raport"` / `"KPI"`

**Widok:**
- Stats: suma sprzedaży, transakcje, wzrost, regiony
- Bar chart: sprzedaż per region
- Tabela: region, kwota, transakcje, wzrost, top produkt

```
┌────────────────────────────────────────────────────────┐
│ 💰 534,000 PLN │ 🛒 847 trans │ 📈 +12% │ 🗺️ 6 regions │
├────────────────────────────────────────────────────────┤
│ Chart: [████████████] Warszawa                        │
│        [█████████  ] Kraków                           │
│        [████████   ] Wrocław                          │
│        ...                                            │
├────────────────────────────────────────────────────────┤
│ Region    │ Amount      │ Trans │ Growth │ Top       │
│ Warszawa  │ 156,000 PLN │ 234   │ +15%   │ Produkt A │
│ Kraków    │ 98,000 PLN  │ 156   │ +8%    │ Produkt B │
└────────────────────────────────────────────────────────┘
```

---

## 📡 API Reference

### REST Endpoints

#### Health Check
```
GET /api/health
Response: {"status": "healthy", "timestamp": "..."}
```

#### Process Command
```
POST /api/command
Body: {"text": "Pokaż faktury"}
Response: {
  "intent": {"app_type": "documents", "action": "show_all", ...},
  "response": "Wyświetlam 8 dokumentów...",
  "view": {...}
}
```

### WebSocket

#### Connect
```
WS /ws/{client_id}
```

#### Send Command
```json
{
  "type": "voice_command",
  "text": "Pokaż kamery"
}
```

#### Receive Response
```json
{
  "type": "response",
  "intent": {"app_type": "cameras", "action": "show_grid"},
  "response_text": "Wyświetlam podgląd kamer...",
  "view": {
    "type": "cameras",
    "view": "matrix",
    "cameras": [...],
    "stats": [...]
  }
}
```

---

## 🎤 Komendy głosowe

### Dokumenty
| Komenda | Akcja |
|---------|-------|
| `pokaż faktury` | Wyświetl wszystkie dokumenty |
| `zeskanuj fakturę` | Tryb skanowania |
| `ile faktur` | Policz dokumenty |
| `faktury do zapłaty` | Filtruj niezapłacone |
| `suma faktur` | Pokaż sumę |

### Kamery
| Komenda | Akcja |
|---------|-------|
| `pokaż kamery` | Grid 2x2 kamer |
| `monitoring` | To samo |
| `gdzie ruch` | Pokaż detekcje ruchu |
| `alerty` | Pokaż aktywne alerty |
| `ile osób` | Policz wykryte osoby |

### Sprzedaż
| Komenda | Akcja |
|---------|-------|
| `pokaż sprzedaż` | Dashboard KPI |
| `raport` | To samo |
| `porównaj regiony` | Comparison view |
| `top produkty` | Najlepiej sprzedające |
| `trend` | Wykres trendu |

### System
| Komenda | Akcja |
|---------|-------|
| `pomoc` | Lista komend |
| `wyczyść` | Clear view |
| `status` | Status systemu |

---

## 🔧 Development

### Struktura projektu

```
streamware-mvp/
├── backend/
│   └── main.py          # FastAPI app, WebSocket, logic
├── frontend/
│   └── index.html       # Single-file frontend
├── scripts/
│   └── test_demo.py     # Test and demo script
├── data/
│   ├── documents/       # Simulated documents
│   └── cameras/         # Simulated camera data
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── start.sh
└── README.md
```

### Dodawanie nowego typu aplikacji

1. Dodaj nową kategorię w `VoiceCommandProcessor.INTENTS`:
```python
INTENTS = {
    ...
    "nowa komenda": ("new_app_type", "action"),
}
```

2. Dodaj generator widoku w `ViewGenerator`:
```python
@classmethod
def _generate_newtype_view(cls, action: str, data=None) -> Dict:
    return {
        "type": "new_app_type",
        "view": "custom",
        "title": "...",
        ...
    }
```

3. Dodaj renderer w `index.html`:
```javascript
function renderNewTypeView(view) {
    // Return HTML string
}
```

4. Dodaj case w `renderView()`:
```javascript
if (view.type === 'new_app_type') {
    contentEl.innerHTML = renderNewTypeView(view);
}
```

### Hot Reload (Development)

```bash
./start.sh dev
# Server runs on port 8001 with auto-reload
```

### Running Tests

```bash
# Via Docker
./start.sh test

# Locally
python scripts/test_demo.py
```

---

## 📊 View Schemas

### Documents View
```json
{
  "type": "documents",
  "view": "table",
  "title": "📄 Zeskanowane dokumenty",
  "subtitle": "8 dokumentów | Suma: 45,230 PLN",
  "columns": [
    {"key": "filename", "label": "Plik", "width": "15%"},
    {"key": "vendor", "label": "Dostawca", "width": "20%"},
    {"key": "amount_gross", "label": "Kwota", "format": "currency"},
    {"key": "status", "label": "Status", "format": "badge"}
  ],
  "data": [...],
  "stats": [
    {"label": "Dokumentów", "value": 8, "icon": "📄"},
    {"label": "Suma brutto", "value": "45,230 PLN", "icon": "💰"}
  ],
  "actions": [
    {"id": "scan", "label": "Skanuj", "icon": "📷"}
  ]
}
```

### Cameras View
```json
{
  "type": "cameras",
  "view": "matrix",
  "grid": {"columns": 2, "rows": 2},
  "cameras": [
    {
      "id": "cam_1",
      "name": "Wejście główne",
      "status": "online",
      "objects_detected": 2,
      "last_motion": "14:32:15",
      "alerts": ["Ruch wykryty 5 min temu"]
    }
  ],
  "stats": [...]
}
```

### Sales View
```json
{
  "type": "sales",
  "view": "dashboard",
  "chart": {
    "type": "bar",
    "labels": ["Warszawa", "Kraków", ...],
    "datasets": [{
      "label": "Sprzedaż",
      "data": [156000, 98000, ...]
    }]
  },
  "table": {
    "columns": [...],
    "data": [...]
  },
  "stats": [...]
}
```

---

## 🚀 Next Steps (Roadmap)

- [ ] **Real STT/TTS** - Integrate Whisper + Coqui TTS
- [ ] **Real Video** - RTSP camera streams
- [ ] **Real Data** - PostgreSQL + file storage
- [ ] **LLM Integration** - GPT/Claude for natural language
- [ ] **Skills System** - Pluggable modules
- [ ] **Authentication** - User management
- [ ] **Multi-tenant** - Team workspaces

---

## 📄 License

MIT License - See LICENSE file

---

**Streamware MVP** - *"Mów co chcesz - system wykonuje"*
