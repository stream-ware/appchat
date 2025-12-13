# Oferta dla Firm Ochroniarskich & Centrów Monitoringu
## Streamware Voice Shell - Inteligentny monitoring CCTV z AI

---

## 🎯 Dla kogo jest ta oferta?

**Firmy ochroniarskie i centra monitoringu** które:
- Monitorują dziesiątki/setki kamer 24/7
- Mają problem z koncentracją operatorów (zmęczenie, przegapione zdarzenia)
- Szukają sposobu na redukcję kosztów personelu bez utraty jakości
- Chcą oferować klientom "smart monitoring" jako usługę premium

---

## ❌ Problemy które rozwiązujemy

### 1. "Operator traci koncentrację po 22 minutach"
To nie opinia - to potwierdzone badania. Przy 50 ekranach, po 20 minutach operator widzi już tylko 5% zdarzeń.

### 2. "Monitoring 24/7 = 9-12 osób"
```
3 zmiany × 3-4 operatorów = 9-12 FTE
Koszt: 50-70k PLN/osobę/rok
Suma: 450-840k PLN/rok
```

### 3. "Klienci chcą dowodów, że monitorujemy"
Jak udowodnić, że operator naprawdę oglądał kamery o 3:00 w nocy?

### 4. "Przegapione zdarzenia = roszczenia"
Jedno przegapione włamanie = utrata klienta + potencjalny pozew.

---

## ✅ Rozwiązanie: Streamware dla Security

### Jak to działa?

```
50 kamer RTSP
      ↓
Streamware AI analizuje WSZYSTKIE jednocześnie
      ↓
Wykrywa zdarzenia:
- Ruch w strefie zakazanej
- Osoba w nietypowym miejscu
- Pojazd na terenie
- Zostawiony obiekt
      ↓
Alert do operatora:
🔊 "Osoba wykryta przy magazynie B, kamera 23"
      ↓
Operator weryfikuje i reaguje
```

### Screenshot z panelu Voice Shell:

![Voice Shell Dashboard](panel-screenshot.png)

**Co widzisz:**
- `Person entering from left` - automatyczna detekcja
- `Person on left detected` - ciągłe śledzenie
- Historia z timestampami - pełny audit trail
- Voice control: "Track person", "Stop", "Status"

---

## 🚀 Kluczowe funkcje dla Security

### 1. Automatyczna detekcja 24/7
```bash
# Konfiguracja strefy:
sq watch --zone "parking" --detect person,vehicle --after 22:00 --before 06:00

# System automatycznie:
# - Monitoruje strefę po godzinach
# - Ignoruje ruch w godzinach pracy
# - Alarmuje tylko gdy trzeba
```

### 2. Voice Alerts (TTS) dla operatorów
```
Zamiast patrzeć na 50 ekranów:

🔊 "Kamera 12: Osoba przy ogrodzeniu wschodnim"
🔊 "Kamera 7: Pojazd wjeżdża na parking"
🔊 "Kamera 34: Ruch w strefie zakazanej"

Operator skupia się tylko na weryfikowanych zdarzeniach.
```

### 3. Multi-channel alerty
```
Zdarzenie wykryte
      ↓
├── 🔊 TTS dla operatora w centrum
├── 📱 Push notification do patrolu
├── 📧 Email do kierownika zmiany
├── 💬 Slack/Teams dla zarządu
└── 📞 Webhook do systemu alarmowego
```

### 4. Pełny Audit Trail
```
Każde zdarzenie logowane:
- timestamp dokładny do ms
- kamera i strefa
- typ detekcji
- confidence score
- reakcja operatora (jeśli była)
- screenshot/clip jako dowód
```

---

## 📊 ROI dla Centrum Monitoringu

### Scenariusz: 100 kamer, monitoring 24/7

**PRZED Streamware:**
| Pozycja | Ilość | Koszt/rok |
|---------|-------|-----------|
| Operatorzy (12 FTE) | 12 | 720,000 PLN |
| Przegapione zdarzenia | ~5% | Ryzyko reputacyjne |
| Reklamacje klientów | ~10/rok | Utrata klientów |

**PO Streamware:**
| Pozycja | Ilość | Koszt/rok |
|---------|-------|-----------|
| Operatorzy (6 FTE) | 6 | 360,000 PLN |
| Streamware license | 100 kamer | 96,000 PLN |
| Przegapione zdarzenia | ~0.5% | Minimalne |
| **OSZCZĘDNOŚĆ** | | **264,000 PLN/rok** |

### Dodatkowe przychody:
- "Smart Monitoring" jako usługa premium: +20-30% do ceny
- Mniej reklamacji = wyższy retention klientów
- Case studies dla nowych klientów

---

## 💰 Cennik Security

### Starter (mała firma ochroniarska)
**80 PLN/kamera/miesiąc** (960 PLN/kamera/rok)
- Do 10 kamer
- Detekcja: osoba, pojazd, ruch
- Email + Slack alerty
- Dashboard web
- 7-dniowa retencja logów

### Pro (średnie centrum)
**60 PLN/kamera/miesiąc** (720 PLN/kamera/rok)
- 11-50 kamer
- + Voice alerts (TTS)
- + Strefy zakazane
- + Multi-site dashboard
- + 30-dniowa retencja
- + Priority support

### Business (duże centrum)
**45 PLN/kamera/miesiąc** (540 PLN/kamera/rok)
- 51-200 kamer
- + Dedykowany opiekun
- + Integracja z systemami alarmowymi
- + Custom detekcje
- + SLA 99.9%
- + 90-dniowa retencja
- + On-premise option

### Enterprise (operator krajowy)
**Wycena indywidualna**
- 200+ kamer
- Multi-tenant (dla Waszych klientów)
- White-label branding
- 24/7 support
- Custom development

---

## 🎁 Oferta pilotażowa

### 30-dniowy pilot: 3,000 PLN

**Co zawiera:**
1. Podłączenie do 10 kamer
2. Konfiguracja stref i reguł
3. Voice alerts + dashboard
4. Szkolenie operatorów (4h)
5. Support 24/7 przez okres pilotu
6. Raport z analizą zdarzeń

**Sukces mierzymy przez:**
- Ilość wykrytych zdarzeń vs baseline
- Czas reakcji operatora
- False positive rate
- Opinia zespołu

**100% kredyt** na roczną licencję przy zakupie.

---

## 🏆 Streamware vs Konkurencja

| Cecha | Streamware | Milestone + BriefCam | Agent Vi | Kamera z AI (Hikvision) |
|-------|------------|----------------------|----------|-------------------------|
| Cena/kamera/rok | 540-960 PLN | 2,500-4,000 PLN | 1,500-2,500 PLN | Wliczona w sprzęt |
| Voice control | ✅ Tak | ❌ Nie | ❌ Nie | ❌ Nie |
| Działa z każdą kamerą | ✅ Tak | Częściowo | ✅ Tak | ❌ Tylko własne |
| Polski support 24/7 | ✅ Tak | Przez partnera | ❌ Angielski | Ograniczony |
| On-premise | ✅ Tak | ✅ Tak | Cloud tylko | ❌ Nie |
| RODO native | ✅ Tak | Wymaga config | Wymaga config | Wątpliwe |

---

## 🔊 Voice Control w praktyce

### Komendy głosowe (PL):
```
"Śledź osobę" → Tracking osoby na aktywnej kamerze
"Pokaż status" → Przegląd wszystkich aktywnych alertów
"Stop" → Zatrzymaj aktualną akcję
"Wyślij email" → Raport zdarzenia na email
"Przełącz na kamerę 15" → Zmiana widoku
```

### Komendy w panelu:
```
> track person
? Jak chcesz śledzenie osoba?
  1. Śledzenie osoba z głosem (TTS)
  2. Śledzenie osoba cicho
  3. Śledzenie osoba i wyślij mi email
```

---

## 🔒 Bezpieczeństwo & Compliance

### RODO:
- ✅ Dane w Polsce (OVH Warszawa / Google Cloud Warsaw)
- ✅ Brak rozpoznawania twarzy (AI Act compliant)
- ✅ Automatyczna retencja i usuwanie
- ✅ DPA dla każdego klienta
- ✅ Audit log wszystkich dostępów

### Bezpieczeństwo systemu:
- ✅ Szyfrowanie end-to-end (TLS 1.3)
- ✅ MFA dla operatorów
- ✅ Role-based access control
- ✅ IP whitelisting
- ✅ Regularne pentesty

### Certyfikaty (w przygotowaniu):
- ISO 27001 (Q2 2025)
- SOC 2 Type II (Q4 2025)

---

## 💼 Model dla firm ochroniarskich

### Opcja A: Własne użycie
Używasz Streamware w swoim centrum monitoringu.
→ Oszczędność na personelu
→ Wyższa jakość usługi

### Opcja B: Reseller / White-label
Oferujesz "Smart Monitoring" swoim klientom jako usługę premium.
→ Streamware pod Twoim brandem
→ Marża 30-50%
→ Twój support lub nasz

### Opcja C: Hybrid
Część kamer w centrum, część u klientów.
→ Multi-site dashboard
→ Różne poziomy usługi

---

## 📞 Następne kroki

### Opcja A: Demo live (45 min)
Pokażemy system na żywych kamerach testowych.
→ [Kalendarz: calendly.com/streamware/security-demo]

### Opcja B: Pilot na Waszych kamerach (30 dni)
Podłączymy 5-10 kamer i przetestujemy w boju.
→ Email: security@streamware.pl

### Opcja C: Rozmowa partnerska
Jeśli interesuje Cię white-label lub reselling.
→ Email: partners@streamware.pl

---

## 📋 FAQ

**Q: Czy mogę podłączyć kamery różnych producentów?**
A: Tak, każda kamera z RTSP stream (Hikvision, Dahua, Axis, Bosch, ONVIF...).

**Q: Co z fałszywymi alarmami?**
A: Nasz confidence threshold minimalizuje false positives. Dodatkowo możesz tworzyć reguły (np. ignoruj ruch <10 sek).

**Q: Czy system działa offline?**
A: Tak, w wersji on-premise. Cloud wymaga łączności.

**Q: Jak z przepustowością sieci?**
A: Przetwarzamy edge lub w chmurze - nie przesyłamy pełnego video. Typowo <100 Kbps/kamera.

**Q: Czy mogę integrować z moim systemem alarmowym?**
A: Tak, mamy API REST i webhooks. Integracje z SATEL, Paradox, DSC dostępne.

**Q: A jeśli Streamware padnie?**
A: SLA 99.9% z on-premise backup. Kamery nagrywają lokalnie niezależnie.

---

## 🏢 Referencje

> "Streamware pozwolił nam zredukować zespół nocny z 4 do 2 operatorów bez utraty jakości monitoringu. ROI w pierwszym roku."
> — Dyrektor Operacyjny, [Firma Ochroniarska X]

> "Voice alerts to game-changer. Operator nie musi wpatrywać się w ekrany - system mówi mu gdzie patrzeć."
> — Kierownik Centrum Monitoringu, [Firma Y]

---

## 📧 Kontakt

**Streamware - AI dla Security**

📧 Email: security@streamware.pl
📱 Tel: +48 XXX XXX XXX (24/7 dla pilotów)
🌐 Web: streamware.pl/security
💼 LinkedIn: linkedin.com/company/streamware

---

*Oferta ważna do: [data + 30 dni]*
*Ceny netto, +23% VAT*
*Minimalna umowa: 12 miesięcy*
*Rabaty wolumenowe od 50 kamer*
