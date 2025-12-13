# Streamware - System Layers Architecture

**Dokumentacja przepływu danych od LLM do wykonania**

---

## 📊 Warstwy systemu

```
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 1: USER INPUT                         │
│   Voice/Text → "ustaw timeout na 30 sekund"                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 2: LANGUAGE                           │
│   LanguageManager → detect language, normalize command          │
│   PL: "ustaw timeout 30" → EN: "set timeout 30"                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 3: TEXT2MAKEFILE                      │
│   MakefileConverter.text2makefile()                             │
│   "ustaw timeout 30" → "make -f Makefile.admin set-timeout SEC=30"
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 4: APP REGISTRY                       │
│   AppRegistry.run_make("weather", "set-timeout", SEC=30)        │
│   → Find app → Validate permissions → Execute                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 5: MAKEFILE EXECUTION                 │
│   subprocess.run(["make", "-f", "Makefile.admin", "set-timeout"])
│   → apps/weather/Makefile.admin:set-timeout                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 6: SCRIPT/COMMAND                     │
│   Makefile target executes script or shell command              │
│   → sed -i 's/TIMEOUT=.*/TIMEOUT=30/' .env                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 7: APP LOGGING                        │
│   AppLogger → logs/app.log, logs/app.yaml, logs/errors.log     │
│   → {"success": true, "key": "TIMEOUT", "value": "30"}         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 8: MAKEFILE2TEXT                      │
│   MakefileConverter.makefile2text()                             │
│   → "Ustawiono timeout na 30 sekund"                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LAYER 9: RESPONSE                           │
│   ResponseGenerator → TTS/Text response to user                 │
│   → 🔊 "Ustawiono timeout na 30 sekund"                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Przykład 1: Pogoda (User Layer)

### Input:
```
User: "pokaż pogodę w Krakowie"
```

### Layer 1-2: Input + Language
```python
# LanguageManager
text = "pokaż pogodę w Krakowie"
lang = language_manager.detect_command_language(text)  # → "pl"
```

### Layer 3: text2makefile
```python
# MakefileConverter
result = makefile_converter.text2makefile("pokaż pogodę w Krakowie", "weather")
# → {
#     "success": True,
#     "command": "make -f Makefile.user city CITY=krakowie",
#     "target": "city",
#     "params": {"CITY": "krakowie"},
#     "makefile": "Makefile.user"
# }
```

### Layer 4: AppRegistry
```python
# AppRegistry finds weather app
app = app_registry.get_app("weather")
# → AppManifest(id="weather", name="🌤️ Pogoda", ...)
```

### Layer 5: Makefile Execution
```bash
# apps/weather/Makefile.user
city:
    @python3 $(SCRIPTS)/get_weather.py $(CITY)
```

### Layer 6: Script Execution
```python
# apps/weather/scripts/get_weather.py
result = get_weather("Kraków")
# → {"success": True, "city": "Kraków", "temperature": 5.2, ...}
```

### Layer 7: Logging
```yaml
# apps/weather/logs/app.yaml
- 2024-12-13 15:20:00:
    app: weather
    level: INFO
    message: "SCRIPT: get_weather (234ms)"
    type: script
    success: true
```

### Layer 8: makefile2text
```python
result = makefile_converter.makefile2text("make -f Makefile.user city CITY=Kraków")
# → {"text": "Sprawdź pogodę dla Kraków", "role": "user"}
```

### Layer 9: Response
```
Bot: "Pogoda w Krakowie: 5.2°C, pochmurno"
🔊 TTS: "Pogoda w Krakowie: pięć przecinek dwa stopnia, pochmurno"
```

---

## 🔧 Przykład 2: Konfiguracja (Admin Layer)

### Input:
```
Admin: "ustaw domyślne miasto Gdańsk"
```

### Layer 3: text2makefile
```python
result = makefile_converter.text2makefile("ustaw domyślne miasto Gdańsk", "weather")
# → {
#     "command": "make -f Makefile.admin set-default-city CITY=Gdańsk",
#     "makefile_type": "admin"
# }
```

### Layer 5: Makefile Execution
```makefile
# apps/weather/Makefile.admin
set-default-city:
    @sed -i 's|DEFAULT_CITY=.*|DEFAULT_CITY=$(CITY)|' $(ENV_FILE)
    @echo '{"success": true, "key": "DEFAULT_CITY", "value": "$(CITY)"}'
```

### Layer 6: File Modification
```bash
# apps/weather/.env (before)
DEFAULT_CITY=Warsaw

# apps/weather/.env (after)
DEFAULT_CITY=Gdańsk
```

### Output:
```json
{"success": true, "key": "DEFAULT_CITY", "value": "Gdańsk"}
```

---

## 🔧 Przykład 3: System Service (System Layer)

### Input:
```
DevOps: "restartuj nginx"
```

### Layer 3: text2makefile
```python
result = makefile_converter.text2makefile("restartuj nginx", "services")
# → {
#     "command": "make -f Makefile.admin restart NAME=nginx",
#     "makefile_type": "admin"
# }
```

### Layer 5-6: Execution
```makefile
# apps/services/Makefile.admin
restart:
    @python3 $(SCRIPTS)/service_control.py restart $(NAME)
```

```python
# apps/services/scripts/service_control.py
subprocess.run(["sudo", "systemctl", "restart", "nginx"])
```

### Output:
```json
{"success": true, "service": "nginx", "action": "restart", "status": "active"}
```

---

## 📁 Struktura App

```
apps/{app_id}/
├── manifest.toml           # App definition
├── .env                    # Configuration
├── Makefile                # Entry point
├── Makefile.run            # System layer (DevOps)
├── Makefile.user           # User layer (daily use)
├── Makefile.admin          # Admin layer (config)
├── scripts/                # Executable scripts
│   └── main.py
├── tests/                  # Test files
│   └── test_app.py
├── logs/                   # Per-app logs
│   ├── app.log
│   ├── app.yaml
│   └── errors.log
└── dashboard/              # Web dashboard
    └── index.html
```

---

## 🎯 Role i dostęp

| Makefile | Rola | Przykłady komend |
|----------|------|------------------|
| `Makefile.run` | System/DevOps | start, stop, health, test, logs |
| `Makefile.user` | User | pogoda, status, show |
| `Makefile.admin` | Admin/Manager | config, enable, disable, backup |

---

## 🔌 API Endpoints per Layer

| Layer | Endpoint | Opis |
|-------|----------|------|
| Input | `POST /api/command` | Raw command |
| text2makefile | `POST /api/text2makefile` | Convert text → make |
| Execute | `POST /api/command/execute` | Full pipeline |
| App Run | `POST /api/apps/{id}/run/{script}` | Direct script |
| App Make | `POST /api/apps/{id}/make/{target}` | Direct make |
| Logs | `GET /api/apps/{id}/logs` | App logs |

---

## 🔗 Powiązane dokumenty

- [README.md](../README.md)
- [API.md](./API.md)
- [APPS.md](./APPS.md)
- [REFACTORING_PLAN.md](./REFACTORING_PLAN.md)
