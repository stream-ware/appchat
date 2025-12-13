# Streamware - Tworzenie Aplikacji

**Wersja:** 0.5.0

---

## 📑 Spis treści

- [Struktura aplikacji](#struktura-aplikacji)
- [manifest.toml](#manifesttoml)
- [3-poziomowy Makefile](#3-poziomowy-makefile)
- [Skrypty](#skrypty)
- [Logowanie](#logowanie)
- [text2makefile](#text2makefile)
- [Przykłady](#przykłady)

---

## Struktura aplikacji

Każda aplikacja znajduje się w `apps/{app_id}/`:

```
apps/myapp/
├── manifest.toml       # Definicja aplikacji (wymagany)
├── .env                # Konfiguracja (wymagany)
├── Makefile            # Entry point
├── Makefile.run        # System/DevOps commands
├── Makefile.user       # User commands
├── Makefile.admin      # Admin commands
├── scripts/            # Skrypty wykonywalne
│   ├── main.py
│   └── helpers.sh
├── logs/               # Auto-generated logs
│   ├── app.log
│   ├── app.yaml
│   └── errors.log
└── README.md           # Dokumentacja
```

---

## manifest.toml

```toml
[app]
id = "myapp"
name = "📦 My App"
version = "1.0.0"
description = "Opis aplikacji"
language = "python"
author = "Your Name"

[app.permissions]
required = ["internet"]
optional = ["storage"]

[service]
type = "internal"  # internal, api, docker
health_check = "/api/health"

[commands]
# pattern = [app_type, action]
"pokaż dane" = ["myapp", "show"]
"status" = ["myapp", "status"]

[commands.keywords]
myapp = ["dane", "moje", "aplikacja"]

[error_handling]
on_timeout = "Serwis nie odpowiada"
on_no_data = "Brak danych"
fallback_response = "Wystąpił błąd"

[scripts]
main = "scripts/main.py"
status = "scripts/status.sh"

[ui]
icon = "📦"
color = "#6366f1"
dashboard_widget = true
```

---

## 3-poziomowy Makefile

### Makefile (Entry point)

```makefile
.PHONY: help run user admin

help:
	@echo "📦 My App"
	@echo "  make run   - System commands"
	@echo "  make user  - User commands"
	@echo "  make admin - Admin commands"

run:
	@make -f Makefile.run help

user:
	@make -f Makefile.user help

admin:
	@make -f Makefile.admin help

run-%:
	@make -f Makefile.run $*

user-%:
	@make -f Makefile.user $*

admin-%:
	@make -f Makefile.admin $*
```

### Makefile.run (System)

```makefile
.PHONY: help start stop health install

# @text start: "Uruchom aplikację"
# @text stop: "Zatrzymaj aplikację"
# @text health: "Sprawdź zdrowie"

help:
	@echo "🔧 System Commands"
	@echo "  start  - Start service"
	@echo "  stop   - Stop service"
	@echo "  health - Health check"

start:
	@echo '{"status": "started"}'

stop:
	@echo '{"status": "stopped"}'

health:
	@echo '{"status": "healthy"}'

install:
	@pip install -r requirements.txt
```

### Makefile.user (Daily use)

```makefile
.PHONY: help show status

# @text show: "Pokaż dane"
# @text status: "Sprawdź status"

help:
	@echo "📦 User Commands"
	@echo "  show   - Show data"
	@echo "  status - Check status"

show:
	@python3 scripts/main.py show

status:
	@python3 scripts/main.py status
```

### Makefile.admin (Configuration)

```makefile
.PHONY: help config enable disable backup

# @text config: "Pokaż konfigurację"
# @text enable: "Włącz aplikację"
# @text disable: "Wyłącz aplikację"

help:
	@echo "⚙️ Admin Commands"

config:
	@cat .env

enable:
	@sed -i 's/APP_ENABLED=.*/APP_ENABLED=true/' .env

disable:
	@sed -i 's/APP_ENABLED=.*/APP_ENABLED=false/' .env

backup:
	@mkdir -p backups && cp .env backups/.env.$(date +%Y%m%d)
```

---

## Skrypty

### Python script template

```python
#!/usr/bin/env python3
"""My App Script"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load app config
APP_DIR = Path(__file__).parent.parent
load_dotenv(APP_DIR / ".env")

def show():
    """Show data"""
    return {"data": "example", "status": "ok"}

def status():
    """Check status"""
    return {"status": "running", "app": os.getenv("APP_ID")}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    commands = {"show": show, "status": status}
    
    if cmd in commands:
        result = commands[cmd]()
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({"error": f"Unknown: {cmd}"}))
```

---

## Logowanie

Każda app ma automatyczne logi w `logs/`:

| Plik | Format | Opis |
|------|--------|------|
| `app.log` | text | Plain text logs |
| `app.yaml` | YAML | Structured (dla LLM) |
| `errors.log` | text | Tylko błędy |

### Format YAML log:
```yaml
- 2024-12-13 15:00:00:
    app: myapp
    level: INFO
    message: "SCRIPT: main (123ms)"
    type: script
    success: true
```

---

## text2makefile

Dodaj `@text` annotations do Makefile:

```makefile
# @text show: "Pokaż dane"
# @text config: "Pokaż konfigurację"
```

System automatycznie mapuje:
- "pokaż dane" → `make -f Makefile.user show`
- "pokaż konfigurację" → `make -f Makefile.admin config`

---

## Przykłady

### Minimalna aplikacja

```bash
# Utwórz strukturę
mkdir -p apps/hello/{scripts,logs}

# manifest.toml
cat > apps/hello/manifest.toml << 'EOF'
[app]
id = "hello"
name = "👋 Hello"
version = "1.0.0"
description = "Simple hello app"
language = "bash"

[commands]
"hello" = ["hello", "greet"]

[ui]
icon = "👋"
EOF

# .env
echo "APP_ID=hello
APP_ENABLED=true" > apps/hello/.env

# Makefile.user
cat > apps/hello/Makefile.user << 'EOF'
.PHONY: greet
# @text greet: "Say hello"
greet:
	@echo '{"message": "Hello, World!"}'
EOF
```

### Generowanie przez API

```bash
# Z pakietu npm
curl -X POST http://localhost:8002/api/generator/from-package \
  -H "Content-Type: application/json" \
  -d '{"registry": "npm", "package": "cowsay"}'

# Z API docs
curl -X POST http://localhost:8002/api/generator/from-api-docs \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.example.com/docs"}'
```

---

## 🔗 Powiązane dokumenty

- [README.md](../README.md)
- [API.md](./API.md) - API Reference
- [REFACTORING_PLAN.md](./REFACTORING_PLAN.md)
- [ARCHITECTURE_PLAN.md](./ARCHITECTURE_PLAN.md)
