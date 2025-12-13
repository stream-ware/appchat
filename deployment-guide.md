# STREAMWARE DEPLOYMENT GUIDE
## Od Desktop po Enterprise Cluster

---

## 🏗️ TRYBY DEPLOYMENT

```
┌────────────────────────────────────────────────────────────────────────┐
│                      STREAMWARE PLATFORM                                │
├──────────────────┬──────────────────┬──────────────────────────────────┤
│  🖥️ DESKTOP APP  │  🌐 WEB SERVICE  │  ☁️ ENTERPRISE CLUSTER           │
├──────────────────┼──────────────────┼──────────────────────────────────┤
│ 1 user           │ 5-50 users       │ Unlimited users                  │
│ Local only       │ Self-hosted/Cloud│ Multi-site                       │
│ Offline capable  │ API access       │ High availability                │
│ Privacy first    │ Team features    │ Custom integrations              │
│                  │                  │                                  │
│ 500 PLN/mies     │ 2-5k PLN/mies    │ 10k+ PLN/mies                   │
└──────────────────┴──────────────────┴──────────────────────────────────┘
```

---

## 🖥️ DESKTOP APP

### Dla kogo?

- Pojedynczy użytkownik
- Freelancer / solopreneur
- Prywatność priorytetem
- Offline capability needed
- Niski budżet na start

### Architektura

```
┌─────────────────────────────────────────────────┐
│              TAURI DESKTOP APP                   │
│  ┌─────────────────────────────────────────┐    │
│  │           VOICE SHELL UI (Web)          │    │
│  │  ┌─────────────┐  ┌─────────────────┐   │    │
│  │  │  Dashboard  │  │  Voice Control  │   │    │
│  │  │  Widgets    │  │  Push-to-talk   │   │    │
│  │  └─────────────┘  └─────────────────┘   │    │
│  └─────────────────────────────────────────┘    │
│                      │                          │
│  ┌───────────────────┴───────────────────┐     │
│  │          STREAMWARE CORE (Rust/Python) │     │
│  │  ┌──────────┐  ┌────────┐  ┌───────┐  │     │
│  │  │ STT/TTS  │  │  LLM   │  │ YOLO  │  │     │
│  │  │ Whisper  │  │ Ollama │  │       │  │     │
│  │  └──────────┘  └────────┘  └───────┘  │     │
│  │  ┌──────────┐  ┌────────┐  ┌───────┐  │     │
│  │  │ Skills   │  │ SQLite │  │ Media │  │     │
│  │  │ Manager  │  │ Store  │  │ Proc. │  │     │
│  │  └──────────┘  └────────┘  └───────┘  │     │
│  └───────────────────────────────────────┘     │
│                                                │
│        [Tauri Backend - Native OS Access]      │
└─────────────────────────────────────────────────┘
           │                    │
     ┌─────┴─────┐        ┌─────┴─────┐
     │ USB/RTSP  │        │ Local LLM │
     │  Camera   │        │  Ollama   │
     └───────────┘        └───────────┘
```

### Instalacja

**Windows:**
```powershell
# Download installer
winget install Streamware.VoiceShell

# Or manual download
https://streamware.pl/download/windows
```

**macOS:**
```bash
# Homebrew
brew install --cask streamware

# Or manual download
https://streamware.pl/download/macos
```

**Linux:**
```bash
# Snap
sudo snap install streamware

# AppImage
wget https://streamware.pl/download/Streamware-latest.AppImage
chmod +x Streamware-latest.AppImage
./Streamware-latest.AppImage

# Flatpak
flatpak install flathub pl.streamware.VoiceShell
```

### Konfiguracja

**Pierwszy start:**
```
1. Launch app
2. "Witaj w Streamware. Skonfigurujmy system."
3. Wybierz mikrofon
4. Test STT: "Powiedz: Hej Streamware"
5. Wybierz LLM:
   - Ollama (local, privacy)
   - OpenAI (cloud, powerful)
   - Anthropic (cloud)
6. Dodaj źródła video (opcjonalnie)
7. Zainstaluj pierwsze skills
8. "Gotowe! Powiedz: Pomoc"
```

**config.yaml (advanced):**
```yaml
# ~/.streamware/config.yaml

voice:
  stt_engine: whisper
  tts_engine: coqui
  language: pl
  wake_word: "hej streamware"
  wake_word_enabled: false
  
llm:
  provider: ollama
  model: bielik-7b
  # Or cloud:
  # provider: openai
  # model: gpt-4o-mini
  # api_key: ${OPENAI_API_KEY}

video:
  sources:
    - name: Webcam
      uri: /dev/video0
    - name: IP Camera
      uri: rtsp://192.168.1.100:554/stream

storage:
  database: sqlite
  path: ~/.streamware/data.db
  
skills:
  installed:
    - voice-base
    - simple-timer
    - note-taker
```

### Wymagania systemowe

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10, macOS 11, Ubuntu 20.04 | Latest |
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16 GB |
| Storage | 10 GB | 50 GB (for local LLM) |
| GPU | Integrated | NVIDIA 8GB+ (for YOLO) |
| Microphone | USB | High-quality USB |

### Offline Mode

```
Desktop może działać w pełni offline:

STT: Whisper local
TTS: Coqui TTS local
LLM: Ollama (Bielik, Llama, Mistral)
Video: YOLO local

Wymagania dodatkowe:
- GPU z CUDA (NVIDIA) lub ROCm (AMD)
- ~20GB storage na modele
- 16GB+ RAM
```

### Cena

| Plan | Cena | Zawiera |
|------|------|---------|
| **Desktop Basic** | 500 PLN/mies | App + 3 skills |
| **Desktop Pro** | 800 PLN/mies | App + 10 skills + priority support |
| **Desktop Yearly** | 5,000 PLN/rok | Pro features, 2 miesiące gratis |

---

## 🌐 WEB SERVICE

### Dla kogo?

- Zespoły 5-50 osób
- Shared dashboards potrzebne
- API integration required
- Multi-device access
- Centralne zarządzanie

### Architektura

```
                            ┌─────────────────┐
                            │    Browser      │
                            │  (Voice UI)     │
                            └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │   NGINX/CDN     │
                            │  (SSL, Static)  │
                            └────────┬────────┘
                                     │
┌────────────────────────────────────┴────────────────────────────────────┐
│                          STREAMWARE WEB SERVICE                         │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │  Voice Shell    │  │   REST API      │  │   WebSocket     │        │
│  │  Server         │  │   Server        │  │   Server        │        │
│  │  (Web UI)       │  │   (Integrations)│  │   (Real-time)   │        │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘        │
│           └────────────────────┼────────────────────┘                  │
│                                │                                       │
│                       ┌────────▼────────┐                              │
│                       │  STREAMWARE     │                              │
│                       │  CORE           │                              │
│                       │                 │                              │
│                       │  ┌───────────┐  │                              │
│                       │  │ STT/TTS   │  │                              │
│                       │  │ LLM       │  │                              │
│                       │  │ YOLO      │  │                              │
│                       │  │ Skills    │  │                              │
│                       │  └───────────┘  │                              │
│                       └────────┬────────┘                              │
│                                │                                       │
│  ┌─────────────────┐  ┌───────┴───────┐  ┌─────────────────┐         │
│  │   PostgreSQL    │  │    Redis      │  │   MinIO/S3      │         │
│  │   (Data)        │  │   (Cache)     │  │   (Files)       │         │
│  └─────────────────┘  └───────────────┘  └─────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                     │                    │
              ┌──────┴──────┐      ┌──────┴──────┐
              │  Cameras    │      │   LLM API   │
              │  RTSP/USB   │      │   OpenAI    │
              └─────────────┘      └─────────────┘
```

### Deployment Options

**Option A: Self-hosted (Docker)**

```bash
# Clone
git clone https://github.com/streamware/streamware.git
cd streamware

# Configure
cp .env.example .env
nano .env

# Start
docker-compose up -d

# Access
open http://localhost:8080
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  streamware:
    image: streamware/voice-platform:latest
    ports:
      - "8080:8080"
      - "8443:8443"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/streamware
      - REDIS_URL=redis://redis:6379
      - LLM_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./skills:/app/skills
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=streamware
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  # Optional: Local LLM
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

volumes:
  postgres_data:
  redis_data:
  ollama_data:
```

**Option B: Cloud Hosted (Streamware Cloud)**

```
1. Sign up: cloud.streamware.pl
2. Create workspace
3. Configure team members
4. Add integrations
5. Start using

Managed by us:
- Backups
- Updates
- Scaling
- Support
```

### API Access

**REST API:**
```bash
# Get dashboard data
curl -X GET https://api.streamware.pl/v1/dashboard/sales \
  -H "Authorization: Bearer ${API_KEY}"

# Execute voice command programmatically
curl -X POST https://api.streamware.pl/v1/voice/command \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"text": "Pokaż sprzedaż z ostatniego tygodnia"}'

# Trigger skill
curl -X POST https://api.streamware.pl/v1/skills/invoice-scanner/scan \
  -H "Authorization: Bearer ${API_KEY}" \
  -F "file=@invoice.pdf"
```

**WebSocket (real-time):**
```javascript
const ws = new WebSocket('wss://api.streamware.pl/v1/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'alerts'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time alert
  console.log('Alert:', data);
};
```

### Multi-user Features

```
┌────────────────────────────────────────────────────────────┐
│                    TEAM WORKSPACE                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  USERS                    SHARED RESOURCES                 │
│  ┌─────────┐              ┌─────────────────────┐         │
│  │ Admin   │──manages────▶│  Dashboards        │         │
│  │ Jan K.  │              │  - Sales KPI       │         │
│  └─────────┘              │  - Operations      │         │
│  ┌─────────┐              │  - Custom...       │         │
│  │ User    │──views───────▶                    │         │
│  │ Anna N. │              ├─────────────────────┤         │
│  └─────────┘              │  Skills            │         │
│  ┌─────────┐              │  - Invoice Scanner │         │
│  │ User    │──uses────────▶ - Email Assistant │         │
│  │ Piotr W.│              │  - Security Mon.   │         │
│  └─────────┘              └─────────────────────┘         │
│                                                            │
│  ROLES:                   FEATURES:                        │
│  - Admin: Full control    - Shared dashboards              │
│  - Manager: Team view     - Individual voice profiles      │
│  - User: Own data         - Role-based access              │
│  - Viewer: Read-only      - Activity audit log             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Cena

| Plan | Users | Cena | Features |
|------|-------|------|----------|
| **Team Starter** | 5 | 1,200 PLN/mies | Basic web, 5 skills |
| **Team Pro** | 20 | 2,000 PLN/mies | Full API, 10 skills |
| **Team Business** | 50 | 4,000 PLN/mies | Unlimited skills, priority |
| **Add-on: User** | +1 | +100 PLN/mies | Per additional user |

---

## ☁️ ENTERPRISE CLUSTER

### Dla kogo?

- Duże organizacje (100+ users)
- Wiele lokalizacji
- High availability wymagane
- Custom integrations
- Compliance requirements
- On-premise mandatory

### Architektura

```
                            ┌─────────────────────────────┐
                            │      LOAD BALANCER          │
                            │    (HAProxy / AWS ALB)      │
                            └──────────────┬──────────────┘
                                           │
          ┌────────────────────────────────┼────────────────────────────────┐
          │                                │                                │
┌─────────▼─────────┐          ┌──────────▼──────────┐          ┌──────────▼──────────┐
│   SITE A (HQ)     │          │   SITE B (Branch)   │          │   SITE C (Branch)   │
│                   │          │                     │          │                     │
│ ┌───────────────┐ │          │ ┌───────────────┐   │          │ ┌───────────────┐   │
│ │ Streamware    │ │   Sync   │ │ Streamware    │   │   Sync   │ │ Streamware    │   │
│ │ Node 1       │◀──────────▶│ │ Node          │◀──────────▶│ │ Node          │   │
│ │              │ │          │ │               │   │          │ │               │   │
│ │ Streamware   │ │          │ └───────────────┘   │          │ └───────────────┘   │
│ │ Node 2       │ │          │                     │          │                     │
│ │              │ │          │ ┌───────────────┐   │          │ ┌───────────────┐   │
│ │ Streamware   │ │          │ │ Local DB      │   │          │ │ Local DB      │   │
│ │ Node 3       │ │          │ │ (Read replica)│   │          │ │ (Read replica)│   │
│ └───────────────┘ │          │ └───────────────┘   │          │ └───────────────┘   │
│                   │          │                     │          │                     │
│ ┌───────────────┐ │          │ ┌───────────────┐   │          │ ┌───────────────┐   │
│ │ PostgreSQL    │ │          │ │ Local Cameras │   │          │ │ Local Cameras │   │
│ │ Primary       │ │          │ │ Processing    │   │          │ │ Processing    │   │
│ └───────────────┘ │          │ └───────────────┘   │          │ └───────────────┘   │
│                   │          │                     │          │                     │
│ ┌───────────────┐ │          └─────────────────────┘          └─────────────────────┘
│ │ Redis Cluster │ │
│ └───────────────┘ │
│                   │
│ ┌───────────────┐ │
│ │ Kafka Cluster │ │
│ │ (Events)      │ │
│ └───────────────┘ │
│                   │
│ ┌───────────────┐ │
│ │ S3/MinIO      │ │
│ │ (Storage)     │ │
│ └───────────────┘ │
└───────────────────┘
```

### Kubernetes Deployment

**Helm Chart:**
```bash
# Add repo
helm repo add streamware https://charts.streamware.pl

# Install
helm install streamware streamware/voice-platform \
  --namespace streamware \
  --set global.replicas=3 \
  --set postgresql.enabled=true \
  --set redis.enabled=true \
  --set kafka.enabled=true \
  -f custom-values.yaml
```

**custom-values.yaml:**
```yaml
global:
  replicas: 3
  domain: streamware.company.com

image:
  repository: streamware/voice-platform
  tag: enterprise-latest

resources:
  requests:
    cpu: 2000m
    memory: 4Gi
  limits:
    cpu: 4000m
    memory: 8Gi

llm:
  provider: azure-openai
  endpoint: https://company.openai.azure.com/
  
postgresql:
  enabled: true
  replication:
    enabled: true
    readReplicas: 2

redis:
  enabled: true
  sentinel:
    enabled: true

kafka:
  enabled: true
  replicaCount: 3

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - streamware.company.com
  tls:
    - secretName: streamware-tls
      hosts:
        - streamware.company.com

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true

backup:
  enabled: true
  schedule: "0 2 * * *"
  retention: 30d
```

### High Availability

```
                    ┌─────────────┐
                    │   Health    │
                    │   Checks    │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐
   │  Node 1   │     │  Node 2   │     │  Node 3   │
   │  Active   │     │  Active   │     │  Active   │
   └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
         │                 │                 │
         └────────────┬────┴─────────────────┘
                      │
              ┌───────▼───────┐
              │   Shared      │
              │   State       │
              │   (Redis)     │
              └───────────────┘

Failover:
- Node failure → automatic redirect
- DB failure → failover to replica  
- Site failure → redirect to other site
- RTO: < 30 seconds
- RPO: < 1 minute
```

### Multi-tenant

```
┌─────────────────────────────────────────────────────────────┐
│                  MULTI-TENANT CLUSTER                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   TENANT A      │  │   TENANT B      │  │   TENANT C  │ │
│  │   (Company X)   │  │   (Company Y)   │  │   (Dept. Z) │ │
│  │                 │  │                 │  │             │ │
│  │ Users: 50       │  │ Users: 200      │  │ Users: 30   │ │
│  │ Skills: 10      │  │ Skills: 25      │  │ Skills: 5   │ │
│  │ Cameras: 5      │  │ Cameras: 50     │  │ Cameras: 2  │ │
│  │                 │  │                 │  │             │ │
│  │ Isolated:       │  │ Isolated:       │  │ Isolated:   │ │
│  │ - Data          │  │ - Data          │  │ - Data      │ │
│  │ - Config        │  │ - Config        │  │ - Config    │ │
│  │ - Skills        │  │ - Skills        │  │ - Skills    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                             │
│  Shared Infrastructure:                                     │
│  - Compute nodes                                            │
│  - Database cluster                                         │
│  - LLM endpoints                                            │
│  - Network/Security                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Enterprise Features

| Feature | Description |
|---------|-------------|
| **SSO/SAML** | Integration with Okta, Azure AD, Google Workspace |
| **RBAC** | Fine-grained role-based access control |
| **Audit Log** | Complete audit trail, SIEM integration |
| **Data Residency** | Choose where data is stored (EU, US, local) |
| **Custom LLM** | Use your own fine-tuned models |
| **Dedicated Support** | Named account manager, 24/7 support |
| **SLA** | 99.9% uptime guarantee |
| **On-site Training** | In-person deployment and training |
| **Custom Development** | Dedicated engineering for custom skills |

### Cena Enterprise

| Component | Cena |
|-----------|------|
| **Base Platform** | od 10,000 PLN/mies |
| **Per User (>100)** | 50 PLN/user/mies |
| **Per Camera** | 100 PLN/camera/mies |
| **Custom Skills Dev** | od 5,000 PLN/skill |
| **On-site Training** | 3,000 PLN/dzień |
| **Premium Support** | +20% base |
| **Dedicated Instance** | +50% base |

**Przykład wyceny:**
```
Enterprise - 200 users, 30 kamer, 5 lokalizacji:

Base platform:           10,000 PLN
Users (200 × 50):        10,000 PLN
Cameras (30 × 100):       3,000 PLN
Premium Support:          4,600 PLN
────────────────────────────────────
Total:                   27,600 PLN/mies
                       = 331,200 PLN/rok
```

---

## 🔄 MIGRATION PATH

```
Desktop → Team → Enterprise

Krok 1: Desktop (500 PLN/mies)
        ↓
        [Grow to 5+ users]
        ↓
Krok 2: Team (2,000 PLN/mies)
        ↓
        [Grow to 50+ users]
        ↓
Krok 3: Enterprise (10,000+ PLN/mies)

Data migration: Included
Config migration: Included
Skills: Compatible across tiers
```

---

## 📞 CONTACT

**Sales:**
- Enterprise: enterprise@streamware.pl
- Team: sales@streamware.pl
- Desktop: support@streamware.pl

**Demo:**
- calendly.com/streamware/demo

**Support:**
- docs.streamware.pl
- support.streamware.pl
- Slack community

---

*Streamware Deployment Guide*
*Scale from one user to enterprise*

docs.streamware.pl/deployment
