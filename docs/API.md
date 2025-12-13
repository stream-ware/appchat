# Streamware API Reference

**Wersja:** 0.5.0  
**Base URL:** `http://localhost:8002`

---

## 📑 Spis treści

- [Apps](#apps)
- [Commands](#commands)
- [Configuration](#configuration)
- [LLM](#llm)
- [Language](#language)
- [Registries](#registries)
- [Generator](#generator)
- [Integrations](#integrations)

---

## Apps

### GET /api/apps
Lista wszystkich załadowanych aplikacji.

**Response:**
```json
{
  "apps": [
    {"id": "weather", "name": "🌤️ Pogoda", "status": "healthy", "commands_count": 5}
  ]
}
```

### GET /api/apps/{app_id}
Szczegóły aplikacji.

### POST /api/apps/{app_id}/run/{script_name}
Uruchom skrypt aplikacji.

**Request:**
```json
{"args": ["arg1", "arg2"]}
```

### POST /api/apps/{app_id}/make/{target}
Uruchom target Makefile.

**Request:**
```json
{"CITY": "Warsaw", "DAYS": "3"}
```

### GET /api/apps/{app_id}/makefiles
Lista wszystkich komend Makefile.

### GET /api/apps/{app_id}/makefiles/{role}
Komendy dla roli (user/admin/system).

### GET /api/apps/{app_id}/logs
Ostatnie logi aplikacji.

### GET /api/apps/{app_id}/context
Pełny kontekst dla LLM debugging.

### POST /api/apps/{app_id}/fix
LLM naprawia kod aplikacji.

**Request:**
```json
{"file": "scripts/main.py", "issue": "timeout error"}
```

→ Zobacz: [APPS.md](./APPS.md)

---

## Commands

### POST /api/command
Wykonaj komendę głosową.

**Request:**
```json
{"command": "pokaż pogodę", "session_id": "abc123"}
```

### POST /api/command/execute
Unified command execution via text2makefile.

**Request:**
```json
{"text": "ustaw timeout 30", "app_id": "weather", "role": "user"}
```

### POST /api/text2makefile
Konwertuj tekst na komendę Makefile.

**Request:**
```json
{"text": "pokaż pogodę", "app_id": "weather"}
```

**Response:**
```json
{
  "success": true,
  "command": "make -f Makefile.user pogoda",
  "target": "pogoda",
  "makefile": "Makefile.user"
}
```

### POST /api/makefile2text
Konwertuj Makefile na tekst.

**Request:**
```json
{"command": "make -f Makefile.admin set-timeout SEC=30"}
```

---

## Configuration

### GET /api/config
Cała konfiguracja systemu.

### GET /api/config/{key}
Wartość klucza konfiguracji.

### PUT /api/config/{key}
Ustaw wartość konfiguracji.

**Request:**
```json
{"value": "new_value"}
```

### POST /api/config/reload
Przeładuj konfigurację z .env.

→ Zobacz: [.env](../.env)

---

## LLM

### GET /api/llm/providers
Lista providerów LLM.

### GET /api/llm/active
Aktywny provider.

### POST /api/llm/active
Zmień aktywny provider.

**Request:**
```json
{"provider": "ollama", "model": "llama2"}
```

### GET /api/llm/models
Dostępne modele.

### GET /api/llm/health
Status wszystkich providerów.

### POST /api/llm/chat
Chat z LLM.

**Request:**
```json
{"message": "Hello", "system_prompt": "You are helpful"}
```

---

## Language

### GET /api/languages
Lista dostępnych języków.

**Response:**
```json
{
  "languages": [
    {"code": "pl", "name": "Polish", "native_name": "Polski"},
    {"code": "en", "name": "English", "native_name": "English"}
  ]
}
```

### GET /api/language
Aktualny język.

### POST /api/language
Zmień język (runtime).

**Request:**
```json
{"language": "en", "session_id": "abc123"}
```

### GET /api/translations
Tłumaczenia UI.

### GET /api/tts/config
Konfiguracja TTS dla języka.

### GET /api/stt/config
Konfiguracja STT dla języka.

---

## Registries

### GET /api/registries
Lista rejestrów zewnętrznych.

### POST /api/registries
Dodaj rejestr.

**Request:**
```json
{
  "id": "myrepo",
  "name": "My Repository",
  "type": "git",
  "url": "https://github.com/user/repo"
}
```

### POST /api/registries/{id}/sync
Synchronizuj rejestr.

### GET /api/external-apps
Lista zewnętrznych aplikacji.

### POST /api/external-apps/{id}/access
Zarządzaj dostępem.

**Request:**
```json
{"role": "user", "grant": true}
```

---

## Generator

### GET /api/generator/registries
Lista rejestrów bibliotek (npm, pypi, docker).

### POST /api/generator/search
Szukaj w rejestrze.

**Request:**
```json
{"registry": "npm", "query": "express"}
```

### POST /api/generator/from-package
Generuj app z pakietu.

**Request:**
```json
{"registry": "docker", "package": "nginx"}
```

### POST /api/generator/from-api-docs
Generuj app z API docs.

**Request:**
```json
{"url": "https://api.example.com/docs"}
```

### POST /api/generator/makefiles
Generuj Makefiles przez LLM.

**Request:**
```json
{"path": "/path/to/repo", "app_id": "myapp"}
```

→ Zobacz: [Tworzenie aplikacji](./APPS.md)

---

## Integrations

### GET /api/weather/{city}
Pogoda dla miasta.

### GET /api/crypto/{symbol}
Cena kryptowaluty.

### GET /api/rss
Kanały RSS.

### GET /api/integrations/status
Status integracji.

---

## WebSocket

### WS /ws/{client_id}
Real-time komunikacja.

**Messages:**
```json
{"type": "command", "command": "pogoda"}
{"type": "response", "view": {...}, "response": "..."}
```

---

## 🔗 Powiązane dokumenty

- [README.md](../README.md)
- [APPS.md](./APPS.md)
- [ARCHITECTURE_PLAN.md](./ARCHITECTURE_PLAN.md)
- [REFACTORING_PLAN.md](./REFACTORING_PLAN.md)
