# STREAMWARE MARKETPLACE
## Katalog Skills - Gotowe rozwiązania do natychmiastowego wdrożenia

---

## 🛒 CONCEPT

### Czym są Skills?

**Skill** = gotowy pakiet zawierający:
- Predefiniowane **komendy głosowe** (intents)
- **Dashboard** z wizualizacjami
- **Integracje** z zewnętrznymi systemami
- **Logikę biznesową** (workflows)
- **Dokumentację** i przykłady użycia

### Jak to działa?

```bash
# Instalacja
streamware skill install invoice-scanner

# Aktywacja
streamware skill enable invoice-scanner

# Użycie (głosem)
"Zeskanuj fakturę"
"Pokaż ostatnie faktury"
"Ile wydaliśmy na dostawcę X w tym miesiącu?"
```

### Typy Skills:

| Typ | Opis | Przykłady |
|-----|------|-----------|
| **Core** | Podstawowe, wbudowane | voice-base, dashboard-core |
| **Community** | Open source, free | simple-timer, note-taker |
| **Pro** | Premium, płatne | invoice-scanner, security-pro |
| **Enterprise** | Custom, dedykowane | erp-connector-sap |

---

## 📄 KATEGORIA: DOKUMENTY

### 📑 invoice-scanner
**Skanowanie i przetwarzanie faktur głosem**

```
Komendy głosowe:
├── "Zeskanuj fakturę" → OCR + ekstrakcja
├── "Pokaż ostatnie faktury" → Lista dashboard
├── "Ile wydaliśmy na [dostawca]?" → Agregacja
├── "Eksportuj faktury do Excel" → Export
└── "Znajdź fakturę numer [X]" → Search
```

| Cecha | Wartość |
|-------|---------|
| OCR Engine | DocTR / Tesseract |
| Accuracy | 95%+ |
| Formaty | PDF, JPG, PNG, skan |
| Export | Excel, CSV, JSON |
| Integracje | Email (auto-import) |
| **Cena** | **300 PLN** (jednorazowo) |

**Dashboard:**
- Lista faktur z filtrowaniem
- Wykres wydatków per dostawca
- Trend miesięczny
- Alerty: termin płatności

---

### 📋 contract-search
**Wyszukiwanie semantyczne w umowach**

```
Komendy głosowe:
├── "Znajdź umowy z karą umowną" → Semantic search
├── "Które umowy kończą się w [miesiąc]?" → Date filter
├── "Porównaj umowy z [dostawca A] i [B]" → Comparison
├── "Pokaż klauzule o wypowiedzeniu" → Extract
└── "Dodaj nową umowę" → Upload + index
```

| Cecha | Wartość |
|-------|---------|
| Index | Vector embeddings |
| Search | Semantic + keyword |
| Formaty | PDF, DOCX |
| Languages | PL, EN |
| **Cena** | **400 PLN** |

---

### 👤 cv-parser
**Przetwarzanie CV dla rekrutacji**

```
Komendy głosowe:
├── "Zaimportuj CV" → Batch upload
├── "Znajdź kandydatów ze znajomością Python" → Filter
├── "Pokaż top 10 na stanowisko [X]" → Ranking
├── "Porównaj kandydata A z B" → Comparison
└── "Wyślij zaproszenie do [kandydat]" → Action
```

| Cecha | Wartość |
|-------|---------|
| Extraction | Imię, email, skills, experience |
| Matching | Job description → ranking |
| Export | Excel, ATS integration |
| **Cena** | **350 PLN** |

---

## 📊 KATEGORIA: DASHBOARDY

### 📈 sales-dashboard
**Głosowy dashboard sprzedaży**

```
Komendy głosowe:
├── "Jaka była sprzedaż wczoraj?" → KPI
├── "Pokaż trend z ostatniego miesiąca" → Chart
├── "Porównaj regiony" → Comparison
├── "Dlaczego spadek w [region]?" → AI Analysis
├── "Wyślij raport do zespołu" → Email report
└── "Ustaw alert gdy sprzedaż < [X]" → Notification
```

| Cecha | Wartość |
|-------|---------|
| Data sources | CSV, Excel, PostgreSQL, API |
| Visualizations | Line, bar, pie, table |
| Refresh | Real-time lub scheduled |
| AI | Trend analysis, anomaly detection |
| **Cena** | **500 PLN** |

**Dashboard zawiera:**
- KPI cards (dziś, tydzień, miesiąc)
- Trend chart
- Regional breakdown
- Top products/services
- Anomaly alerts

---

### 📋 kpi-monitor
**Uniwersalny monitor KPI**

```
Komendy głosowe:
├── "Jakie są dzisiejsze KPI?" → Summary
├── "Który KPI jest na czerwono?" → Alerts
├── "Pokaż historię [KPI name]" → Trend
├── "Dodaj nowy KPI" → Setup wizard
└── "Zmień próg alertu dla [KPI]" → Config
```

| Cecha | Wartość |
|-------|---------|
| KPIs | Unlimited |
| Thresholds | Green/Yellow/Red |
| Alerts | Slack, Email, Voice |
| Formulas | Custom calculations |
| **Cena** | **400 PLN** |

---

### 📊 excel-voice
**Głosowa kontrola nad Excel/CSV**

```
Komendy głosowe:
├── "Otwórz plik sprzedaż.xlsx" → Load
├── "Pokaż sumę kolumny B" → Calculate
├── "Filtruj gdzie region = Warszawa" → Filter
├── "Posortuj po dacie malejąco" → Sort
├── "Zrób pivot po kategoriach" → Pivot
└── "Zapisz jako nowy plik" → Export
```

| Cecha | Wartość |
|-------|---------|
| Formaty | XLSX, CSV, Google Sheets |
| Operations | Filter, sort, pivot, formulas |
| Size | Do 1M rows |
| **Cena** | **300 PLN** |

---

## 🎥 KATEGORIA: VIDEO

### 🔒 security-monitor
**Inteligentny monitoring z głosową kontrolą**

```
Komendy głosowe:
├── "Pokaż kamerę [nazwa]" → Live view
├── "Obserwuj wejście i powiadom o ruchu" → Watch mode
├── "Nagraj ostatnie 10 minut" → Clip
├── "Ile osób przeszło dzisiaj?" → Count
├── "Pokaż wszystkie wykrycia z nocy" → Review
└── "Wyłącz powiadomienia na godzinę" → Mute
```

| Cecha | Wartość |
|-------|---------|
| Kamery | RTSP, USB, IP |
| Detection | Person, vehicle, animal |
| Tracking | ByteTrack |
| Alerts | Voice, Slack, Email, SMS |
| Storage | Local, S3 |
| **Cena** | **600 PLN** |

**Dashboard:**
- Grid kamer live
- Event timeline
- Heatmap ruchu
- Statistics

---

### 👥 people-counter
**Zliczanie osób z analizą**

```
Komendy głosowe:
├── "Ile osób jest teraz w [lokalizacja]?" → Live count
├── "Jaki był ruch dzisiaj?" → Daily stats
├── "Pokaż peak hours" → Analysis
├── "Porównaj z poprzednim tygodniem" → Comparison
└── "Ustaw alert gdy > 50 osób" → Threshold
```

| Cecha | Wartość |
|-------|---------|
| Accuracy | 95%+ |
| Counting | In/Out/Current |
| Zones | Multiple per camera |
| Export | CSV, API |
| **Cena** | **400 PLN** |

---

### 🚗 parking-watcher
**Monitoring parkingu**

```
Komendy głosowe:
├── "Ile wolnych miejsc?" → Available
├── "Gdzie jest miejsce dla [rejestracja]?" → Search
├── "Pokaż zajętość z ostatniego tygodnia" → Stats
├── "Powiadom gdy miejsce VIP wolne" → Watch
└── "Kto parkuje najdłużej?" → Analysis
```

| Cecha | Wartość |
|-------|---------|
| Detection | Vehicle, plate (ALPR) |
| Zones | Parking spots definition |
| Alerts | Full lot, VIP available |
| **Cena** | **500 PLN** |

---

## 🤖 KATEGORIA: AUTOMATYZACJA

### 📧 email-assistant
**Głosowe zarządzanie emailem**

```
Komendy głosowe:
├── "Mam nowe maile?" → Check inbox
├── "Przeczytaj ostatnie 3" → Read aloud
├── "Odpowiedz: Dziękuję, odezwę się jutro" → Reply
├── "Przekaż do Ani" → Forward
├── "Oznacz jako ważne" → Flag
└── "Szukaj maili od [osoba]" → Search
```

| Cecha | Wartość |
|-------|---------|
| Providers | Gmail, Outlook, IMAP |
| AI | Summarization, smart replies |
| Actions | Read, reply, forward, flag |
| **Cena** | **350 PLN** |

---

### 📅 meeting-scheduler
**Głosowe planowanie spotkań**

```
Komendy głosowe:
├── "Jakie mam dzisiaj spotkania?" → List
├── "Umów spotkanie z Janem na jutro" → Schedule
├── "Przekaż spotkanie o godzinę" → Reschedule
├── "Odwołaj spotkanie z Anią" → Cancel
├── "Znajdź wolny termin dla zespołu X" → Find slot
└── "Przypomnij mi o spotkaniu za 15 minut" → Reminder
```

| Cecha | Wartość |
|-------|---------|
| Calendars | Google, Outlook, CalDAV |
| Features | Scheduling, reminders, conflicts |
| **Cena** | **300 PLN** |

---

### 📝 report-generator
**Automatyczne generowanie raportów**

```
Komendy głosowe:
├── "Wygeneruj raport dzienny" → Generate
├── "Wyślij raport do zespołu" → Email
├── "Pokaż ostatni raport" → Display
├── "Zmień format na PDF" → Config
└── "Zaplanuj raport na każdy poniedziałek" → Schedule
```

| Cecha | Wartość |
|-------|---------|
| Templates | Custom, markdown |
| Data | From other skills |
| Formats | PDF, HTML, DOCX |
| Delivery | Email, Slack, save |
| **Cena** | **400 PLN** |

---

## 🔌 KATEGORIA: INTEGRACJE

### 💬 slack-voice
**Głosowa kontrola Slack**

```
Komendy głosowe:
├── "Wyślij na #general: Spotkanie o 15" → Send
├── "Co nowego na #team?" → Read
├── "Odpowiedz w wątku: OK, zrobione" → Reply
├── "Kto wspomniał mnie dzisiaj?" → Mentions
└── "Ustaw status: Na spotkaniu" → Status
```

| Cecha | Wartość |
|-------|---------|
| Actions | Read, send, reply, status |
| Channels | Multiple workspaces |
| **Cena** | **250 PLN** |

---

### 📊 teams-voice
**Głosowa kontrola Microsoft Teams**

```
Komendy głosowe:
├── "Wyślij do zespołu Marketing: ..." → Send
├── "Jakie mam powiadomienia?" → Notifications
├── "Dołącz do spotkania" → Join meeting
└── "Ustaw status: Nie przeszkadzać" → Status
```

| Cecha | Wartość |
|-------|---------|
| Actions | Chat, meetings, status |
| **Cena** | **250 PLN** |

---

### 🔗 webhook-connector
**Uniwersalny connector do API/Webhook**

```
Komendy głosowe:
├── "Wywołaj webhook [nazwa]" → Trigger
├── "Pobierz dane z API [nazwa]" → GET request
├── "Wyślij dane do [system]" → POST request
└── "Pokaż ostatnie wywołania" → Log
```

| Cecha | Wartość |
|-------|---------|
| Methods | GET, POST, PUT, DELETE |
| Auth | API key, OAuth, Basic |
| Mapping | Response → voice/dashboard |
| **Cena** | **300 PLN** |

---

## 🏭 KATEGORIA: BRANŻOWE (Roadmap Q1 2025)

### 📦 warehouse-voice
**Głosowe zarządzanie magazynem**

```
Komendy głosowe:
├── "Gdzie jest produkt [SKU]?" → Location
├── "Ile na stanie [produkt]?" → Stock level
├── "Przyjmij dostawę: 100 x [produkt]" → Receipt
├── "Wydaj 50 x [produkt] do zamówienia [X]" → Pick
├── "Co trzeba zamówić?" → Reorder report
└── "Inwentaryzacja regału [X]" → Cycle count
```

**Status:** Development
**ETA:** Q1 2025
**Target price:** 800 PLN

---

### 🏥 clinic-assistant
**Asystent głosowy dla przychodni**

```
Komendy głosowe:
├── "Następny pacjent" → Queue management
├── "Pokaż kartę pacjenta [X]" → Patient record
├── "Dodaj notatkę: ..." → Documentation
├── "Umów wizytę kontrolną za miesiąc" → Scheduling
└── "Receptura na [lek]" → Prescription
```

**Status:** Roadmap
**ETA:** Q2 2025

---

### 🛒 retail-analytics
**Analityka dla retail**

```
Komendy głosowe:
├── "Jak idzie sprzedaż dzisiaj?" → Sales KPI
├── "Co się najlepiej sprzedaje?" → Top products
├── "Ile osób weszło do sklepu?" → Footfall
├── "Konwersja z wczoraj?" → Conversion rate
└── "Porównaj z poprzednim tygodniem" → Comparison
```

**Status:** Roadmap
**ETA:** Q1 2025

---

## 🆓 COMMUNITY SKILLS (Free)

### ⏱️ simple-timer
```
"Ustaw timer na 5 minut"
"Ile zostało?"
"Zatrzymaj timer"
```

### 📝 note-taker
```
"Zapisz notatkę: ..."
"Pokaż ostatnie notatki"
"Znajdź notatki o [temat]"
```

### 🧮 voice-calculator
```
"Ile to jest 15% z 1250?"
"Przelicz 100 dolarów na złote"
"Oblicz 17 razy 43"
```

### 🌤️ weather-check
```
"Jaka pogoda dzisiaj?"
"Czy będzie padać?"
"Pogoda na weekend"
```

---

## 📦 BUNDLE PACKAGES

### 📄 Office Starter Bundle
**Skills:** invoice-scanner, email-assistant, meeting-scheduler, note-taker

| Osobno | Bundle | Oszczędność |
|--------|--------|-------------|
| 1,000 PLN | **700 PLN** | 30% |

---

### 🎥 Security Bundle
**Skills:** security-monitor, people-counter, parking-watcher

| Osobno | Bundle | Oszczędność |
|--------|--------|-------------|
| 1,500 PLN | **1,000 PLN** | 33% |

---

### 📊 Analytics Bundle
**Skills:** sales-dashboard, kpi-monitor, excel-voice, report-generator

| Osobno | Bundle | Oszczędność |
|--------|--------|-------------|
| 1,600 PLN | **1,100 PLN** | 31% |

---

### 🏢 Full Business Bundle
**All Pro Skills** (15 skills)

| Osobno | Bundle | Oszczędność |
|--------|--------|-------------|
| 5,500 PLN | **3,500 PLN** | 36% |

---

## 🛠️ CUSTOM SKILL DEVELOPMENT

### Potrzebujesz czegoś specjalnego?

**Co możemy zbudować:**
- Integracja z Twoim ERP/CRM
- Branżowe komendy głosowe
- Custom dashboardy
- Unikalne workflows

**Proces:**
1. Discovery call (free) - 30 min
2. Specification - od 2,000 PLN
3. Development - od 5,000 PLN
4. Testing & deployment - included
5. Maintenance - 500 PLN/mies

**Timeline:** 2-8 tygodni zależnie od złożoności

📧 custom@streamware.pl

---

## 📋 SKILL COMPARISON TABLE

| Skill | Komendy | Dashboard | Integracje | Cena |
|-------|---------|-----------|------------|------|
| invoice-scanner | 5 | ✓ | Email, Export | 300 |
| contract-search | 5 | ✓ | - | 400 |
| cv-parser | 5 | ✓ | ATS, Email | 350 |
| sales-dashboard | 6 | ✓✓ | SQL, API | 500 |
| kpi-monitor | 5 | ✓✓ | Multi | 400 |
| excel-voice | 6 | - | Excel, CSV | 300 |
| security-monitor | 6 | ✓✓ | Slack, Email | 600 |
| people-counter | 5 | ✓ | API | 400 |
| parking-watcher | 5 | ✓ | - | 500 |
| email-assistant | 6 | - | Gmail, Outlook | 350 |
| meeting-scheduler | 6 | - | Cal | 300 |
| report-generator | 5 | - | Email, Slack | 400 |
| slack-voice | 5 | - | Slack | 250 |
| teams-voice | 4 | - | Teams | 250 |
| webhook-connector | 4 | - | Any API | 300 |

---

*Streamware Marketplace*
*Gotowe rozwiązania głosowe dla Twojego biznesu*

marketplace.streamware.pl
