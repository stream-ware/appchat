# Oferta dla Retail & Sieci Handlowych
## Streamware Voice Shell - Analityka wideo dla sklepów

---

## 🎯 Dla kogo jest ta oferta?

**Sieci handlowe i sklepy** które:
- Chcą mierzyć ruch klientów bez drogich systemów (Milestone, Genetec)
- Mają już kamery CCTV ale nie wykorzystują ich potencjału
- Szukają danych do optymalizacji layoutu i obsady
- Potrzebują alertów o kolejkach i zdarzeniach

---

## ❌ Problemy które rozwiązujemy

### 1. "Nie wiemy ile osób wchodzi do sklepu"
Masz kamerę nad wejściem, ale nikt nie liczy. Decyzje o obsadzie podejmujesz "na oko".

### 2. "System analytics kosztuje fortunę"
Milestone + BriefCam = 200+ PLN za kamerę + wdrożenie enterprise.
Dla 10 sklepów po 5 kamer = 100k PLN/rok minimum.

### 3. "Kolejki rosną, a my nie wiemy"
Klient czeka 10 minut, wychodzi, wystawia negatywną opinię. Kierownik dowiaduje się z Google Reviews.

### 4. "Nie mamy IT do obsługi"
Systemy enterprise wymagają certyfikowanych partnerów i dedykowanego IT.

---

## ✅ Rozwiązanie: Streamware dla Retail

### Jak to działa?

```
Twoja istniejąca kamera CCTV
          ↓
    Stream RTSP do Streamware
          ↓
    AI analizuje w real-time:
    - Ile osób weszło/wyszło
    - Gdzie się zatrzymują
    - Jak długo czekają w kolejce
          ↓
    Dashboard + Alerty na telefon
```

### Screenshot z panelu:

![Voice Shell Dashboard](panel-screenshot.png)

**Co widzisz:**
- `Person entering from left` - detekcja wejścia
- `Person on left detected` - śledzenie pozycji
- Timestampy każdego zdarzenia
- Historia do analizy wzorców

---

## 🚀 Funkcje dla Retail

### 1. Footfall Counting (liczenie klientów)
```
📊 Raport dzienny:
- Wejścia: 847
- Wyjścia: 832
- Peak hours: 11:00-13:00, 17:00-19:00
- Konwersja: 23% (kupujących vs odwiedzających)
```

### 2. Queue Detection (alerty kolejek)
```bash
# Konfiguracja:
sq watch --detect queue --threshold 5 --notify slack

# Gdy kolejka > 5 osób:
🔔 "Alert: Kolejka przy kasie 2 - 7 osób, czas oczekiwania ~8 min"
```

### 3. Heatmapy ruchu
```
Gdzie klienci spędzają najwięcej czasu?
→ Dane do optymalizacji layoutu
→ Lepsze rozmieszczenie produktów
→ Identyfikacja "martwych stref"
```

### 4. Voice Alerts dla kierowników
```
🔊 "Uwaga: duży ruch przy wejściu głównym"
🔊 "Kolejka rośnie - potrzebna dodatkowa kasa"
🔊 "Strefa promocyjna pusta od 30 minut"
```

---

## 📊 ROI dla Retail

### Scenariusz: Sieć 10 sklepów, 5 kamer/sklep

| Metryka | Wartość |
|---------|---------|
| Średni basket | 85 PLN |
| Footfall dzienny | 500 osób/sklep |
| Konwersja przed | 20% |
| **Konwersja po optymalizacji** | **23%** (+3pp) |
| Dodatkowe transakcje/dzień | 15/sklep |
| Dodatkowy przychód/dzień | 1,275 PLN/sklep |
| **Dodatkowy przychód/rok** | **4.6M PLN** (10 sklepów) |

### Koszt Streamware vs zysk:

| Pozycja | Koszt roczny |
|---------|--------------|
| Streamware Pro (50 kamer) | 60,000 PLN |
| Potencjalny wzrost przychodu | 4,600,000 PLN |
| **ROI** | **7,567%** |

*Nawet przy 10% realizacji potencjału = 460k PLN dodatkowego przychodu*

---

## 💰 Cennik Retail

### Starter (pojedynczy sklep)
**400 PLN/miesiąc** (4,800 PLN/rok)
- Do 3 kamer
- Footfall counting
- Raporty dzienne/tygodniowe
- Email alerty
- Dashboard web

### Pro (mała sieć)
**1,000 PLN/miesiąc** (12,000 PLN/rok)
- Do 10 kamer
- + Queue detection
- + Heatmapy
- + Slack/Teams alerty
- + Voice alerts (TTS)
- + API do integracji z POS

### Business (sieć handlowa)
**2,000 PLN/miesiąc** (24,000 PLN/rok)
- Do 25 kamer
- + Multi-location dashboard
- + Custom KPIs
- + Dedicated account manager
- + Integracja z systemem kasowym
- + SLA 99.5%

### Enterprise (duża sieć)
**Wycena indywidualna**
- 50+ kamer
- On-premise option
- Custom development
- White-label możliwy

---

## 🎁 Oferta pilotażowa

### 14-dniowy pilot GRATIS + 30 dni za 2,500 PLN

**Faza 1 (14 dni - bezpłatna):**
- Podłączenie 1 kamery
- Footfall counting
- Raport z danymi

**Faza 2 (30 dni - 2,500 PLN):**
- Do 3 kamer
- Pełna funkcjonalność Pro
- Szkolenie personelu (2h)
- Raport ROI z rekomendacjami

**Warunki:**
- Potrzebujemy dostęp do streamu RTSP z kamery
- Support przez cały okres
- 100% kredyt na roczną licencję przy zakupie

---

## 🏆 Streamware vs Konkurencja

| Cecha | Streamware | Milestone + BriefCam | Hikvision |
|-------|------------|----------------------|-----------|
| Cena/kamera/rok | 400-800 PLN | 2,000-4,000 PLN | 500-1,500 PLN |
| Wymaga nowych kamer | ❌ Nie | Często tak | Tak (własne) |
| Setup time | 2 godziny | 1-2 tygodnie | 3-5 dni |
| Voice control | ✅ Tak | ❌ Nie | ❌ Nie |
| Polski support | ✅ Tak | Przez partnera | Ograniczony |
| Dane w EU | ✅ Tak | Opcjonalnie | ❌ Chiny |
| RODO compliance | ✅ Native | Wymaga konfiguracji | Wątpliwe |

---

## 📱 Przykładowe alerty

### Slack/Teams:
```
🔔 [Sklep Warszawa Centrum] 12:34
Kolejka przy kasach: 8 osób
Szacowany czas oczekiwania: 12 min
Rekomendacja: Otwórz kasę 3

[Pokaż kamery] [Ignoruj] [Eskaluj]
```

### Email dzienny:
```
📊 Raport dzienny: Sklep Kraków Galeria

Footfall: 623 osób (+12% vs wczoraj)
Peak: 12:00-14:00 (189 osób)
Konwersja: 24.1%
Średni czas w sklepie: 8.4 min

Top strefy:
1. Strefa promocji - 45% klientów
2. Kasy - 31% klientów
3. Wejście - 24% klientów

Alerty: 3 (kolejki > 5 osób)
```

---

## 🔒 RODO & Bezpieczeństwo

### Gwarancje:
- ✅ Dane przetwarzane tylko w Polsce (OVH Warszawa)
- ✅ Brak rozpoznawania twarzy (tylko detekcja osoby)
- ✅ Automatyczne usuwanie nagrań po X dniach (konfigurowalne)
- ✅ DPA (Data Processing Agreement) dostępna
- ✅ Audit log wszystkich dostępów

### Dokumentacja:
- Szablon DPIA dla video analytics
- Klauzula informacyjna dla klientów sklepu
- Polityka retencji danych

---

## 📞 Następne kroki

### Opcja A: Bezpłatny test (14 dni)
Podłączymy 1 kamerę i pokażemy dane.
→ [Formularz: streamware.pl/retail-test]

### Opcja B: Demo online (30 min)
Pokażemy system na żywo na przykładowych danych retail.
→ [Kalendarz: calendly.com/streamware/retail-demo]

### Opcja C: Wizyta w sklepie
Przyjedziemy, ocenimy kamery, zaproponujemy rozwiązanie.
→ Email: retail@streamware.pl

---

## 📋 FAQ

**Q: Czy moje obecne kamery się nadają?**
A: Jeśli masz dostęp do streamu RTSP (większość kamer IP) - tak. Sprawdzimy bezpłatnie.

**Q: Ile to obciąży mój internet?**
A: Minimalne - przetwarzamy lokalnie lub w chmurze, nie przesyłamy pełnego video.

**Q: Czy klienci muszą być informowani?**
A: Tak, standardowa tabliczka "Obiekt monitorowany" wystarczy. Nie identyfikujemy osób.

**Q: Mogę integrować z moim systemem kasowym?**
A: Tak, mamy API REST. Integracje z Comarch, Subiekt, własne systemy.

**Q: A co z RODO?**
A: Nie stosujemy rozpoznawania twarzy. Dane anonimowe. DPA do podpisu.

---

## 🏪 Case Study: Sieć X (10 sklepów)

**Wyzwanie:**
- Brak danych o ruchu klientów
- Decyzje o obsadzie "na oko"
- Reklamacje na kolejki

**Rozwiązanie:**
- Streamware na 3 kamerach/sklep
- Queue detection + alerty Slack
- Dashboard dla kierowników regionalnych

**Wyniki po 3 miesiącach:**
- 📈 Konwersja: +2.8pp (z 19.2% do 22%)
- ⏱️ Średni czas kolejki: -34%
- 💰 Dodatkowy przychód: 180k PLN/miesiąc
- ⭐ NPS: +12 punktów

---

## 📧 Kontakt

**Streamware - Analityka dla Retail**

📧 Email: retail@streamware.pl
📱 Tel: +48 XXX XXX XXX
🌐 Web: streamware.pl/retail
💼 LinkedIn: linkedin.com/company/streamware

---

*Oferta ważna do: [data + 30 dni]*
*Ceny netto, +23% VAT*
*Minimalna umowa: 12 miesięcy*
