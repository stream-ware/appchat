# Streamware Voice Shell - Pełna lista funkcji v0.3

## 🚀 Nowe funkcje (grudzień 2024)

### System kontroli dostępu (RBAC)
- **5 ról systemowych**: Admin, Manager, Biuro, Ochrona, Gość
- **Logowanie przez chat**: `login admin admin123`
- **Kontrola uprawnień**: każda rola ma dostęp tylko do wybranych modułów
- **Dokumentacja**: `/docs/ACCESS_CONTROL.md`

### TTS/STT (Text-to-Speech / Speech-to-Text)
- **Rozpoznawanie głosu** (Web Speech API) - język polski
- **Synteza mowy** - odpowiedzi czytane głosem
- **Wskaźnik TTS** podczas odtwarzania

### URL Routing i Historia
- **Komendy w URL**: `/?cmd=pogoda&app=internet`
- **Przycisk wstecz** działa poprawnie
- **Historia komend** z możliwością ponownego wykonania
- **LocalStorage** - historia zachowana między sesjami

### YAML Logging
- **Kolorowe logi** w konsoli
- **Plik YAML** ze strukturalnymi logami
- **Szczegółowe informacje**: user, session, command, duration

---

## 📊 Statystyki systemu

| Metryka | Wartość |
|---------|---------|
| **Komendy głosowe** | 94 |
| **Aplikacje/Moduły** | 7 |
| **Role użytkowników** | 5 |
| **Integracje internetowe** | 8 |
| **Testy automatyczne** | 66 |

---

## 🎤 94 Komendy głosowe

### 📄 Dokumenty (12 komend)
| Komenda | Opis |
|---------|------|
| `pokaż faktury` | Lista wszystkich faktur |
| `zeskanuj fakturę` | Skanowanie nowego dokumentu |
| `suma faktur` | Podsumowanie wartości |
| `faktury do zapłaty` | Faktury oczekujące |
| `umowy` | Lista umów |
| `przeterminowane` | Dokumenty po terminie |
| `eksportuj do excel` | Export danych |
| `archiwum` | Dokumenty archiwalne |
| `szukaj dokumentu` | Wyszukiwanie |
| `ostatnie dokumenty` | Ostatnio dodane |
| `statystyki dokumentów` | Podsumowanie |
| `kategorie` | Kategorie dokumentów |

### 🎥 Monitoring (12 komend)
| Komenda | Opis |
|---------|------|
| `pokaż kamery` | Podgląd wszystkich kamer |
| `monitoring` | Dashboard monitoringu |
| `gdzie ruch` | Wykryty ruch |
| `alerty` | Aktywne alerty |
| `nagraj` | Rozpocznij nagrywanie |
| `parking` | Kamery parkingu |
| `wejście` | Kamera wejścia |
| `mapa ciepła` | Heatmapa ruchu |
| `historia nagrań` | Archiwum nagrań |
| `strefa` | Strefy monitoringu |
| `detekcja` | Status detekcji |
| `noc` | Tryb nocny |

### 📊 Sprzedaż (12 komend)
| Komenda | Opis |
|---------|------|
| `pokaż sprzedaż` | Dashboard sprzedaży |
| `raport` | Generuj raport |
| `porównaj regiony` | Porównanie regionów |
| `top produkty` | Najlepsze produkty |
| `kpi` | Wskaźniki KPI |
| `prognoza` | Prognoza sprzedaży |
| `lejek sprzedaży` | Sales funnel |
| `prowizje` | Prowizje sprzedaży |
| `trend` | Trendy sprzedaży |
| `cele` | Cele sprzedażowe |
| `ranking` | Ranking sprzedawców |
| `marża` | Analiza marży |

### 🏠 Smart Home (10 komend)
| Komenda | Opis |
|---------|------|
| `temperatura` | Odczyty temperatury |
| `oświetlenie` | Sterowanie światłem |
| `energia` | Zużycie energii |
| `ogrzewanie` | Sterowanie ogrzewaniem |
| `klimatyzacja` | Sterowanie AC |
| `alarm` | System alarmowy |
| `czujniki` | Status czujników |
| `harmonogram` | Automatyzacje |
| `wilgotność` | Odczyty wilgotności |
| `scenariusze` | Predefiniowane scenariusze |

### 📈 Analityka (8 komend)
| Komenda | Opis |
|---------|------|
| `analiza` | Dashboard analityczny |
| `wykres` | Generuj wykres |
| `raport dzienny` | Raport dzienny |
| `raport tygodniowy` | Raport tygodniowy |
| `raport miesięczny` | Raport miesięczny |
| `anomalie` | Wykryj anomalie |
| `predykcja` | Prognozowanie AI |
| `porównanie` | Porównaj okresy |

### 🌐 Internet (21 komend)
| Komenda | Opis |
|---------|------|
| `pogoda` | Aktualna pogoda |
| `pogoda warszawa` | Pogoda dla Warszawy |
| `pogoda kraków` | Pogoda dla Krakowa |
| `bitcoin` | Kurs Bitcoin |
| `crypto` | Kursy kryptowalut |
| `kryptowaluty` | Kursy kryptowalut |
| `kursy walut` | Kursy walut |
| `rss` | Kanały RSS |
| `kanały rss` | Lista kanałów RSS |
| `news` | Wiadomości |
| `wiadomości` | Wiadomości |
| `email` | Formularz email |
| `wyślij email` | Wysyłka email |
| `mqtt` | IoT messaging |
| `iot` | Status IoT |
| `webhook` | Zarządzanie webhooks |
| `api` | Status API |
| `integracje` | Status integracji |
| `http` | Test HTTP |
| `weather` | Weather (EN) |
| `exchange` | Exchange rates |

### ⚙️ System (13 komend)
| Komenda | Opis |
|---------|------|
| `pomoc` | Lista komend |
| `wyczyść` | Wyczyść widok |
| `status` | Status systemu |
| `ustawienia` | Konfiguracja |
| `historia` | Historia konwersacji |
| `login` | Ekran logowania |
| `zaloguj` | Logowanie |
| `logout` | Wylogowanie |
| `wyloguj` | Wylogowanie |
| `kto` | Aktualny użytkownik |
| `użytkownicy` | Lista użytkowników |
| `start` | Dashboard główny |
| `aplikacje` | Lista aplikacji |

---

## 👥 Role i uprawnienia

| Rola | Dokumenty | Kamery | Sprzedaż | Smart Home | Analityka | Internet | System |
|------|-----------|--------|----------|------------|-----------|----------|--------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manager** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Biuro** | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Ochrona** | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Gość** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## 🔌 Integracje internetowe

| Usługa | Typ | API | Status |
|--------|-----|-----|--------|
| **Pogoda** | REST | Open-Meteo | ✅ Aktywna |
| **Kryptowaluty** | REST | CoinGecko | ✅ Aktywna |
| **Kursy walut** | REST | exchangerate.host | ✅ Aktywna |
| **RSS** | Feed | Ars Technica, BBC, HackerNews | ✅ Aktywna |
| **MQTT** | Protocol | test.mosquitto.org | ✅ Demo |
| **Email** | SMTP | Konfigurowalny | ⚙️ Demo |
| **Webhooks** | HTTP | Custom | ✅ Aktywna |
| **HTTP Proxy** | REST | Dowolne API | ✅ Aktywna |

---

## 🧪 Testy

```bash
# Uruchom wszystkie testy
make test

# Tylko testy backendu
pytest test_backend.py -v

# Tylko testy API
pytest test_api.py -v
```

**66 testów** obejmujących:
- VoiceCommandProcessor
- ViewGenerator
- ResponseGenerator
- UserManager (RBAC)
- SkillRegistry
- Integracje internetowe
- API REST

---

## 🐳 Uruchomienie

```bash
# Development
make dev

# Produkcja
make prod

# Testy
make test

# Docker
docker-compose up
```

---

## 📁 Struktura projektu

```
appchat/
├── backend/
│   └── main.py          # FastAPI + WebSocket
├── frontend/
│   └── index.html       # SPA + TTS/STT
├── docs/
│   └── ACCESS_CONTROL.md
├── oferta/
│   ├── index.php        # Landing page
│   └── *.md             # Dokumentacja oferty
├── logs/
│   ├── streamware.log
│   ├── streamware.yaml
│   └── conversations.yaml
└── tests/
    ├── test_backend.py
    └── test_api.py
```

---

*Aktualizacja: grudzień 2024*
