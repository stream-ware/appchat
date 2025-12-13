# Streamware - Plan Rozwoju Architektury

## Wersja 0.4.0 - Obecna architektura

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (SPA)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Chat UI   │  │  Dashboard  │  │  Config UI  │              │
│  │  (minimal)  │  │   (views)   │  │   (admin)   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │                                       │
│                    WebSocket + REST                              │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API Layer                             │    │
│  │  /api/command  /api/config  /api/llm  /api/db           │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────┼───────────────────────────────┐    │
│  │                  Core Modules                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │VoiceCommand  │  │ ViewGenerator│  │ ResponseGen  │   │    │
│  │  │  Processor   │  │              │  │              │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────┼───────────────────────────────┐    │
│  │                  Services Layer                          │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │ LLM Manager  │  │ Integration  │  │   Database   │   │    │
│  │  │  (Ollama)    │  │   Manager    │  │   (SQLite)   │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                   EXTERNAL SERVICES                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Ollama  │  │ Weather  │  │  Crypto  │  │   MQTT   │        │
│  │  (LLM)   │  │   API    │  │   API    │  │  Broker  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Roadmap wersji

### v0.5.0 - Stabilizacja (Q1 2025)
- [ ] Testy E2E z Playwright
- [ ] Dokumentacja API (OpenAPI/Swagger)
- [ ] Rate limiting i security headers
- [ ] Monitoring (Prometheus metrics)
- [ ] Health checks dla wszystkich serwisów

### v0.6.0 - Multi-tenant (Q2 2025)
- [ ] Wiele organizacji/workspace'ów
- [ ] Zarządzanie użytkownikami (CRUD)
- [ ] Audit log wszystkich akcji
- [ ] Backup/restore bazy danych
- [ ] Import/export konfiguracji

### v0.7.0 - Enterprise Features (Q3 2025)
- [ ] SSO (SAML/OIDC)
- [ ] LDAP/AD integration
- [ ] Custom branding per tenant
- [ ] SLA monitoring
- [ ] Disaster recovery

### v1.0.0 - Production Ready (Q4 2025)
- [ ] High availability setup
- [ ] Horizontal scaling
- [ ] CDN dla statycznych plików
- [ ] Geo-distributed deployment
- [ ] SOC 2 compliance

---

## Integracje planowane

### LLM Providers
| Provider | Status | Priorytet |
|----------|--------|-----------|
| Ollama (local) | ✅ Zaimplementowany | - |
| OpenAI | ✅ Zaimplementowany | - |
| Anthropic Claude | ✅ Zaimplementowany | - |
| Google Gemini | 📋 Planowany | Średni |
| Azure OpenAI | 📋 Planowany | Wysoki |
| Mistral API | 📋 Planowany | Niski |
| Local GGUF models | 📋 Planowany | Średni |

### Integracje zewnętrzne
| Usługa | Status | Typ |
|--------|--------|-----|
| Open-Meteo (pogoda) | ✅ Aktywna | REST API |
| CoinGecko (crypto) | ✅ Aktywna | REST API |
| RSS/Atom feeds | ✅ Aktywna | Feed parser |
| MQTT broker | ✅ Demo | Protocol |
| Email SMTP | ✅ Demo | Protocol |
| Webhooks | ✅ Aktywna | HTTP |
| Slack | 📋 Planowany | REST API |
| Microsoft Teams | 📋 Planowany | REST API |
| Discord | 📋 Planowany | REST API |
| Telegram | 📋 Planowany | REST API |
| Home Assistant | 📋 Planowany | REST/WS |
| Zapier/Make | 📋 Planowany | Webhooks |

### Bazy danych
| DB | Status | Use case |
|----|--------|----------|
| SQLite | ✅ Aktywna | Development, small deployments |
| PostgreSQL | 📋 Planowany | Production |
| Redis | 📋 Planowany | Cache, sessions |
| ClickHouse | 📋 Planowany | Analytics |

---

## Architektura docelowa (v1.0)

```
                            ┌─────────────────┐
                            │   Load Balancer │
                            │    (nginx/HAP)  │
                            └────────┬────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
    │   Streamware #1   │  │   Streamware #2   │  │   Streamware #N   │
    │     (FastAPI)     │  │     (FastAPI)     │  │     (FastAPI)     │
    └─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
┌────────▼────────┐       ┌─────────▼─────────┐       ┌─────────▼─────────┐
│   PostgreSQL    │       │      Redis        │       │     Ollama        │
│   (primary)     │       │   (cache/queue)   │       │   (GPU cluster)   │
└────────┬────────┘       └───────────────────┘       └───────────────────┘
         │
┌────────▼────────┐
│   PostgreSQL    │
│   (replica)     │
└─────────────────┘
```

---

## Moduły systemu

### 1. Voice Command Processor
**Odpowiedzialność:** Przetwarzanie komend głosowych/tekstowych
- Intent recognition (pattern matching + LLM)
- Entity extraction
- Context management
- Multi-language support

### 2. View Generator
**Odpowiedzialność:** Generowanie widoków UI
- Dynamic dashboard generation
- LLM-assisted layouts
- Template system
- Real-time updates

### 3. LLM Manager
**Odpowiedzialność:** Zarządzanie providerami LLM
- Provider registry
- Model switching
- Load balancing
- Fallback handling
- Token counting

### 4. Integration Manager
**Odpowiedzialność:** Integracje zewnętrzne
- API clients (HTTP, MQTT, etc.)
- Webhook management
- Rate limiting
- Error handling

### 5. Database Module
**Odpowiedzialność:** Persystencja danych
- Conversations storage
- Configuration management
- User management
- Audit logging

### 6. Config Module
**Odpowiedzialność:** Konfiguracja systemu
- .env file loading
- Runtime config changes
- Feature flags
- Validation

---

## API Endpoints (aktualne)

### Core
- `POST /api/command` - Execute voice command
- `GET /api/commands` - List all commands
- `WS /ws/{client_id}` - WebSocket connection

### Configuration
- `GET /api/config` - Get all config
- `PUT /api/config/{key}` - Set config value
- `POST /api/config/reload` - Reload from .env

### LLM Management
- `GET /api/llm/providers` - List providers
- `POST /api/llm/active` - Set active LLM
- `GET /api/llm/models` - List available models
- `GET /api/llm/health` - Check health
- `POST /api/llm/chat` - Chat with LLM

### Database
- `GET /api/db/conversations` - Get conversations
- `GET /api/db/sessions` - Get sessions
- `GET /api/db/services` - Get services

### Navigation
- `GET /api/app/{app_type}/options` - Get app options
- `GET /api/breadcrumbs` - Get navigation

---

## Bezpieczeństwo

### Obecne (v0.4)
- Basic authentication
- CORS configuration
- Input validation (Pydantic)

### Planowane
- JWT tokens
- API key management
- Rate limiting (per user/IP)
- Request signing
- Audit logging
- Encryption at rest
- TLS everywhere

---

## Monitoring

### Metryki do zbierania
- Request latency (p50, p95, p99)
- Error rate
- Active sessions
- LLM token usage
- Database query time
- WebSocket connections

### Alerty
- Service down
- High error rate
- Slow responses
- Database full
- LLM provider unavailable

---

## Deployment

### Development
```bash
make dev
# http://localhost:8002
```

### Docker
```bash
docker-compose up
# http://localhost:8000
```

### Production
```bash
docker-compose --profile prod up -d
# Behind nginx reverse proxy
```

### Kubernetes (planowane)
```yaml
# helm install streamware ./charts/streamware
```

---

*Dokument: ARCHITECTURE_PLAN.md*
*Wersja: 0.4.0*
*Data: grudzień 2024*
