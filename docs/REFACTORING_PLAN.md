# Streamware - Plan Refaktoryzacji

**Data:** 2024-12-13  
**Wersja docelowa:** 1.0.0

---

## 📊 Obecny stan projektu

### Moduły backend (9):
| Moduł | LOC | Stan | Priorytet refaktora |
|-------|-----|------|---------------------|
| `main.py` | ~3100 | ⚠️ Za duży | 🔴 Wysoki |
| `database.py` | ~280 | ✅ OK | 🟢 Niski |
| `config.py` | ~230 | ✅ OK | 🟢 Niski |
| `llm_manager.py` | ~260 | ✅ OK | 🟢 Niski |
| `app_registry.py` | ~625 | ⚠️ Do podziału | 🟡 Średni |
| `makefile_converter.py` | ~400 | ✅ OK | 🟢 Niski |
| `registry_manager.py` | ~400 | ✅ OK | 🟢 Niski |
| `language_manager.py` | ~300 | ✅ OK | 🟢 Niski |
| `app_generator.py` | ~550 | ✅ OK | 🟢 Niski |

### Problemy do rozwiązania:
1. **main.py** - zbyt duży, wymaga podziału na router modules
2. **VoiceCommandProcessor** - hardcoded, przenieść do apps/
3. **ViewGenerator** - przenieść do apps/
4. **Brak testów** - 0% coverage
5. **Brak walidacji** - Pydantic models incomplete

---

## 🎯 Faza 1: Podział main.py (Tydzień 1-2)

### Nowa struktura:
```
backend/
├── main.py              # Entry point only (~100 LOC)
├── routers/
│   ├── __init__.py
│   ├── apps.py          # /api/apps/* endpoints
│   ├── config.py        # /api/config/* endpoints
│   ├── llm.py           # /api/llm/* endpoints
│   ├── language.py      # /api/language/* endpoints
│   ├── generator.py     # /api/generator/* endpoints
│   ├── registries.py    # /api/registries/* endpoints
│   ├── commands.py      # /api/command/* endpoints
│   └── integrations.py  # /api/weather, /api/crypto, etc.
├── models/
│   ├── __init__.py
│   ├── requests.py      # Pydantic request models
│   └── responses.py     # Pydantic response models
├── services/
│   ├── __init__.py
│   ├── voice_processor.py  # VoiceCommandProcessor
│   ├── view_generator.py   # ViewGenerator
│   └── response_generator.py
└── core/
    ├── __init__.py
    ├── database.py
    ├── config.py
    └── logging.py
```

### Zadania:
- [ ] Utworzyć `backend/routers/` z FastAPI APIRouter
- [ ] Przenieść endpoints do odpowiednich routerów
- [ ] Utworzyć `backend/models/` z Pydantic
- [ ] Utworzyć `backend/services/` z logiką biznesową
- [ ] Zmniejszyć main.py do ~100 LOC

---

## 🎯 Faza 2: Modularyzacja komend (Tydzień 3-4)

### Cel: Przenieść VoiceCommandProcessor do apps/

### Nowa struktura apps/:
```
apps/
├── _core/                    # Systemowe apps
│   ├── commands/             # Voice command processing
│   │   ├── manifest.toml
│   │   ├── intents.toml      # Command patterns
│   │   └── Makefile.*
│   ├── views/                # View generation
│   │   ├── manifest.toml
│   │   └── templates/
│   └── system/               # System management
│       ├── manifest.toml
│       └── Makefile.*
├── weather/
├── documents/
├── registry/
└── services/                 # NEW: System services
```

### Zadania:
- [ ] Utworzyć `apps/_core/commands/`
- [ ] Przenieść INTENTS do `intents.toml`
- [ ] Przenieść ViewGenerator do `apps/_core/views/`
- [ ] Każda app definiuje własne komendy w manifest.toml

---

## 🎯 Faza 3: System Services App (Tydzień 5)

### Nowa app: `apps/services/`

```
apps/services/
├── manifest.toml
├── .env
├── Makefile
├── Makefile.run
├── Makefile.user
├── Makefile.admin
├── scripts/
│   ├── list_services.py
│   ├── service_control.py
│   └── analyze_service.py
└── logs/
```

### Funkcje:
- Lista usług systemowych (systemctl)
- Start/stop/restart usług
- Analiza logów usług
- Monitorowanie statusu
- Integracja z Docker containers

---

## 🎯 Faza 4: Testy i dokumentacja (Tydzień 6)

### Testy:
```
tests/
├── __init__.py
├── conftest.py
├── test_api/
│   ├── test_apps.py
│   ├── test_config.py
│   └── test_commands.py
├── test_services/
│   ├── test_voice_processor.py
│   └── test_makefile_converter.py
└── test_apps/
    ├── test_weather.py
    └── test_registry.py
```

### Dokumentacja:
```
docs/
├── README.md             # Index
├── ARCHITECTURE.md       # Architektura
├── API.md                # API reference
├── APPS.md               # Tworzenie apps
├── REFACTORING_PLAN.md   # Ten dokument
├── CHANGELOG.md          # Historia zmian
└── tutorials/
    ├── getting-started.md
    ├── create-app.md
    └── text2makefile.md
```

---

## 🎯 Faza 5: Optymalizacja (Tydzień 7-8)

### Performance:
- [ ] Async database operations
- [ ] Connection pooling
- [ ] Response caching (Redis)
- [ ] Lazy loading apps

### Security:
- [ ] JWT authentication
- [ ] Rate limiting per endpoint
- [ ] Input sanitization
- [ ] CORS hardening

### DevOps:
- [ ] Docker multi-stage build
- [ ] Health check endpoints
- [ ] Prometheus metrics
- [ ] Structured logging (JSON)

---

## 📅 Timeline

| Tydzień | Faza | Deliverables |
|---------|------|--------------|
| 1-2 | Podział main.py | Routers, models |
| 3-4 | Modularyzacja | apps/_core/ |
| 5 | Services app | System management |
| 6 | Testy | 70%+ coverage |
| 7-8 | Optymalizacja | Production ready |

---

## 🔗 Powiązane dokumenty

- [README.md](../README.md) - Główna dokumentacja
- [ARCHITECTURE_PLAN.md](./ARCHITECTURE_PLAN.md) - Plan architektury
- [PROJECT_ANALYSIS.md](./PROJECT_ANALYSIS.md) - Analiza projektu
- [API.md](./API.md) - Dokumentacja API
- [APPS.md](./APPS.md) - Tworzenie aplikacji

---

## ✅ Kryteria sukcesu

1. **main.py < 200 LOC**
2. **Test coverage > 70%**
3. **Wszystkie komendy w apps/**
4. **Dokumentacja kompletna**
5. **Zero hardcoded values**

---

*Dokument: REFACTORING_PLAN.md*
