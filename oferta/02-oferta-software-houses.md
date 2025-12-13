# Oferta dla Software Houses
## Streamware Voice Shell - Automatyzacja testów z AI i głosem

---

## 🎯 Dla kogo jest ta oferta?

**Software houses i zespoły QA** które:
- Tracą dni/tygodnie na testy regresyjne przy każdym RELEASE
- Mają problem z utrzymaniem testów Selenium (zmiany w DOM = zepsute testy)
- Chcą skalować QA bez zatrudniania kolejnych testerów
- Szukają przewagi konkurencyjnej w ofertowaniu

---

## ❌ Problem który rozwiązujemy

### Koszty ukryte testowania manualnego:

| Obszar | Typowy koszt roczny |
|--------|---------------------|
| 2-3 testerów manualnych | 300-450k PLN |
| Utrzymanie testów Selenium | 100-200h/miesiąc |
| Opóźnienia releaseów | 2-5 dni per sprint |
| Przegapione bugi na produkcji | Reputacja + hotfixy |

**Suma: 500k-800k PLN/rok** dla średniego software house.

---

## ✅ Rozwiązanie: Streamware Voice Shell

### Jak to działa?

```
Tester mówi: "Śledź użytkownika przez proces rejestracji"
     ↓
AI rozpoznaje elementy UI wizualnie (nie przez DOM)
     ↓
System wykonuje i nagruje każdy krok
     ↓
Raport: "Test passed" lub "Błąd na kroku 5: button nieaktywny"
```

### Screenshot z panelu (Voice Shell Dashboard):

![Voice Shell](panel-screenshot.png)

**Co widzisz:**
- `> track person` - komenda głosowa
- Historia detekcji z timestampami
- Opcje: "Śledzenie osoba z głosem (TTS)" / "cicho" / "wyślij email"
- Multi-session: wiele testów równolegle

---

## 🚀 Kluczowe funkcje dla QA

### 1. Visual Test Automation
```bash
# Zamiast szukać elementu przez XPath:
sq voice-click "kliknij przycisk Zaloguj"

# AI znajduje przycisk wizualnie - jak człowiek
# Działa nawet gdy zmieni się struktura HTML
```

### 2. Browser Automation z LLM (CurLLM)
```bash
# Natural language → akcje w przeglądarce
sq llm "Wypełnij formularz rejestracji danymi testowymi"

# AI rozumie kontekst i wykonuje sekwencję kroków
```

### 3. Integracja z CI/CD
```bash
# W pipeline GitLab/GitHub Actions:
sq test-suite run --suite regression --notify slack
```

### 4. Voice Control dla testerów
```bash
# Sterowanie głosem (PL/EN/DE):
"Uruchom test logowania"
"Stop"
"Pokaż status"
"Wyślij raport na email"
```

---

## 📊 ROI dla Software House

### Scenariusz: Zespół 20 developerów, 3 testerów, 2 releasy/miesiąc

| Metryka | Przed | Po Streamware | Oszczędność |
|---------|-------|---------------|-------------|
| Czas testów regresyjnych | 3 dni | 4 godziny | **85%** |
| Utrzymanie testów | 80h/mc | 20h/mc | **75%** |
| Testerzy manualni | 3 FTE | 1 FTE | **2 FTE** |
| Time-to-market | +3 dni | +0.5 dnia | **2.5 dni** |

**Roczna oszczędność: ~200-300k PLN**

---

## 💰 Cennik

### Starter (dla małych zespołów)
**500 PLN/miesiąc** (6,000 PLN/rok)
- 1 bot/agent
- Do 1000 testów/miesiąc
- Email support
- Integracja Slack/Teams

### Pro (dla software houses)
**1,200 PLN/miesiąc** (14,400 PLN/rok)
- 3 boty/agenty
- Unlimited testy
- Voice control
- CI/CD integracja
- Priority support
- Custom prompts

### Business (dla większych organizacji)
**1,800 PLN/miesiąc** (21,600 PLN/rok)
- 5 botów/agentów
- Dedicated account manager
- On-premise option
- SLA 99.5%
- Szkolenie zespołu (4h)

---

## 🎁 Oferta pilotażowa

### 30-dniowy pilot: 2,000 PLN

**Co zawiera:**
1. Setup na Waszej infrastrukturze (2h)
2. Konfiguracja 5 testów z Waszej aplikacji
3. Szkolenie zespołu QA (2h)
4. Support przez cały okres pilotu
5. Raport z wynikami i rekomendacjami

**Warunki:**
- Płatność z góry (faktura VAT)
- Kredyt 100% na zakup rocznej licencji przy sukcesie
- Success criteria definiujemy wspólnie przed startem

---

## 🏆 Dlaczego Streamware vs konkurencja?

| Cecha | Streamware | Selenium | UiPath Test Suite |
|-------|------------|----------|-------------------|
| Setup time | 2 godziny | 2-5 dni | 1-2 tygodnie |
| Nauka | Mów po polsku | Kod Python/Java | Low-code + certyfikat |
| Koszt roczny | 6-22k PLN | "Darmowy" (+200h utrzymania) | 40-80k PLN |
| Zmiany w UI | Auto-adaptacja | Zepsute testy | Częściowa adaptacja |
| Voice control | ✅ Tak | ❌ Nie | ❌ Nie |
| Polski support | ✅ Tak | ❌ Community | ❌ Partner |

---

## 📞 Następne kroki

### Opcja A: Bezpłatna konsultacja (30 min)
Porozmawiajmy o Waszych wyzwaniach QA i sprawdźmy czy pasujemy.
→ [Kalendarz: calendly.com/streamware/qa-demo]

### Opcja B: Demo na żywo (45 min)
Pokażemy Voice Shell na przykładzie Waszej aplikacji (potrzebujemy URL).
→ [Formularz: streamware.pl/demo-qa]

### Opcja C: Od razu pilot
Jeśli już wiecie że chcecie spróbować - zaczynamy w 48h.
→ Email: pilot@streamware.pl
→ Temat: "Pilot QA - [Nazwa firmy]"

---

## 📋 FAQ

**Q: Czy działa z naszym VCS/CI (GitLab, GitHub, Azure DevOps)?**
A: Tak, mamy gotowe integracje i CLI które działa w każdym pipeline.

**Q: Czy mogę hostować on-premise?**
A: Tak, w planie Business. Wymaga Docker/Kubernetes.

**Q: Jakie przeglądarki wspieracie?**
A: Chrome, Firefox, Edge. Safari w roadmapie.

**Q: Czy mogę używać własnych modeli LLM?**
A: Tak, wspieramy Ollama (lokalne), OpenAI, Anthropic, Groq.

**Q: Jak z RODO?**
A: Dane przetwarzane w EU (OVH Warszawa lub Google Cloud Warsaw). DPA dostępne.

---

## 📧 Kontakt

**Streamware - Automatyzacja dla software houses**

📧 Email: sales@streamware.pl
📱 Tel: +48 XXX XXX XXX
🌐 Web: streamware.pl/qa
💼 LinkedIn: linkedin.com/company/streamware

---

*Oferta ważna do: [data + 30 dni]*
*Ceny netto, +23% VAT*
