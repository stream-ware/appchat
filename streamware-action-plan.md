# Streamware Voice Shell: Plan Działania i Komunikacji

## 📋 PODSUMOWANIE STRATEGII

### Cel: Pierwsza płatna sprzedaż w 45 dni

**Sekwencja działań:**
1. **Tydzień 1-2**: Hackerspaces (darmowy pilot, feedback)
2. **Tydzień 3-4**: Warsztaty samochodowe (płatny pilot 500 PLN/mies)
3. **Tydzień 5-8**: Skalowanie do magazynów/kuchni

---

## 🎯 KONKRETNE KONTAKTY I ROZMOWY

### FAZA 1: HACKERSPACES (Tydzień 1-2)

#### 1. Warsaw Hackerspace
| Dane | Wartość |
|------|---------|
| **Email ogólny** | kontakt@hackerspace.pl |
| **Prezes Zarządu** | Kacper Mikołajczyk |
| **Adres** | ul. Żelazna 103A, Warszawa |
| **Składka** | 100 PLN/mies (50 PLN studenci) |
| **Spotkania** | Codziennie wieczorem |
| **Komunikacja** | IRC, Matrix, email |

**Co mają:**
- Ploter laserowy, frezarka CNC, tokarka, spawarki
- Warsztat elektroniczny z oscyloskopami, stacjami lutowniczymi
- ~80+ członków

**Propozycja wartości:**
- Voice assistant do dokumentacji technicznej podczas lutowania
- Timer głosowy podczas prac z żywicą epoksydową
- Szybkie lookup specyfikacji komponentów

---

#### 2. Hackerspace Kraków
| Dane | Wartość |
|------|---------|
| **Email ogólny** | info@hackerspace-krk.pl |
| **Zarząd** | |
| - Wiktor Przybylski | wiktor@hackerspace-krk.pl |
| - Szymon Reiter | szymon@hackerspace-krk.pl |
| - Michał Zagórski | m.zagorski@hackerspace-krk.pl |
| **Adres** | ul. Limanowskiego 46/LU1, Kraków |
| **Spotkania** | Piątkowe nighthacki |
| **Komunikacja** | Telegram, IRC |

**Co mają:**
- Status OPP (od 2024)
- Warsztaty, prezentacje, kursy
- Aktywna społeczność

---

#### 3. Hackerspace Wrocław
| Dane | Wartość |
|------|---------|
| **Email** | kontakt@hswro.org |
| **Telefon** | +48 71 707 24 57 |
| **Adres** | Dawna zajezdnia tramwajowa |
| **Spotkania** | Środy od 19:00 |
| **Komunikacja** | Telegram, Matrix, IRC |

---

#### 4. Hackerspace Silesia (Katowice)
| Dane | Wartość |
|------|---------|
| **Strona** | hs-silesia.pl |
| **Adres** | ul. Ondraszka 17, Katowice |
| **Składka** | 32/64/128 PLN (pay what you want) |
| **Sponsorzy** | Future Processing, Rspective |

---

### FAZA 2: WARSZTATY SAMOCHODOWE (Tydzień 3-4)

#### Strategia pozyskania:
1. **OLX/Allegro Lokalnie** - szukaj ogłoszeń warsztatów
2. **Google Maps** - "warsztat samochodowy [miasto]"
3. **Facebook grupy** - "Mechanicy samochodowi Polska"
4. **Polecenia** - zapytaj znajomych o ich mechaników

#### Profil idealnego klienta:
- 2-5 stanowisk
- Właściciel = mechanik (decyduje sam)
- Obsługuje różne marki (potrzebuje dokumentacji)
- Nie ma komputera przy każdym stanowisku

---

## 📧 SZABLONY EMAIL

### Email 1: Hackerspace - Prośba o pilot

**Temat:** Darmowy voice assistant dla warsztatu - szukamy beta testerów

**Treść:**
```
Cześć,

Buduję Streamware - asystenta głosowego dla ludzi z zajętymi rękami. 
Myślę że hackerspace to idealne miejsce do testów: lutowanie, CNC, 
spawanie - wszędzie gdzie ręce są zajęte a trzeba sprawdzić dokumentację.

Co robi:
- "Jaka temperatura lutownicy na SMD 0805?" → odpowiedź głosowa
- "Timer 5 minut na żywicę" → odmierza czas
- "Specyfikacja ESP32-WROOM" → czyta datasheet

Propozycja:
- Daję wam system za darmo na 3 miesiące
- Koszt: Raspberry Pi 4 + mikrofon USB (~250 PLN) - mogę pożyczyć
- W zamian: szczery feedback i możliwość iteracji

Czy mogę wpaść na najbliższe spotkanie i pokazać demo? 
Zajmie 15 minut.

Pozdrawiam,
[Imię]
[Telefon]
streamware.pl
```

---

### Email 2: Hackerspace Kraków - Personalizowany

**Temat:** Voice assistant dla nighthacków - darmowy pilot

**Do:** wiktor@hackerspace-krk.pl

**Treść:**
```
Cześć Wiktor,

Widziałem że Hackerspace Kraków ma status OPP od 2024 - gratulacje!

Buduję Streamware - asystenta głosowego dla warsztatów. Pomyślałem 
że piątkowe nighthacki to świetna okazja do testów. Gdy masz ręce 
w lutownicy albo przy CNC, voice control ma sens.

Przykłady:
- "Schemat pinout ATmega328" → pokazuje na ekranie
- "Przelicz 3.3V na dzielnik z 10k" → oblicza
- "Jaki moment na M8 stal" → odpowiada

Chętnie przyjadę na piątkowy nighthack z działającym demo.
Pilot byłby darmowy - szukam feedbacku od ludzi którzy 
naprawdę używają narzędzi.

Kiedy mogę wpaść?

[Imię]
[Telefon]
```

---

### Email 3: Warsztat samochodowy - Cold outreach

**Temat:** Asystent głosowy dla mechaników - 10 min oszczędności na każdej naprawie

**Treść:**
```
Dzień dobry,

Jestem [Imię] z firmy Streamware. Tworzymy asystenta głosowego 
dla mechaników - żeby nie musieć odkładać narzędzi i myć rąk 
za każdym razem gdy trzeba sprawdzić specyfikację.

Jak to działa:
- Mówisz: "Moment dokręcenia koła Golf 7"
- Słyszysz: "120 niutonometrów"
- Ręce zostają przy pracy

Firmy w USA (Ortho) pokazują oszczędność 10 minut na naprawie.
Przy 10 naprawach dziennie to prawie 2 godziny.

Propozycja pilotażu:
- Koszt: 500 PLN/miesiąc (bez zobowiązań)
- Sprzęt: tablet + słuchawka bluetooth (dostarczamy)
- Czas: 2 miesiące testu

Czy mogę zadzwonić w tym tygodniu i opowiedzieć więcej?
Zajmie 10 minut.

Pozdrawiam,
[Imię]
[Telefon]
streamware.pl
```

---

### Email 4: Follow-up (3 dni po pierwszym)

**Temat:** Re: Asystent głosowy - krótkie pytanie

**Treść:**
```
Dzień dobry,

Piszę w nawiązaniu do mojej poprzedniej wiadomości o asystencie 
głosowym dla warsztatu.

Chciałem tylko zapytać - czy temat w ogóle was interesuje?
Jeśli nie pasuje, nie ma problemu - powiem szczerze i nie 
będę zawracał głowy.

Jeśli tak - kiedy mogę zadzwonić na 10 minut?

Pozdrawiam,
[Imię]
```

---

### Email 5: Follow-up (7 dni - ostatni)

**Temat:** Zamykam temat - ostatnia wiadomość

**Treść:**
```
Dzień dobry,

Nie chcę spamować - to moja ostatnia wiadomość.

Jeśli kiedykolwiek zainteresuje was asystent głosowy 
do warsztatu (hands-free lookup specyfikacji), 
dajcie znać: [email] lub [telefon].

Powodzenia!
[Imię]
```

---

## 🗣️ SKRYPTY ROZMÓW

### Rozmowa 1: Wizyta w Hackerspaceie

**Cel:** Umówić darmowy pilot

**Otwarcie (max 30 sekund):**
```
"Cześć, jestem [Imię]. Buduję voice assistanta dla ludzi 
z zajętymi rękami - lutowanie, CNC, takie rzeczy. 
Pomyślałem że hackerspace to idealne miejsce do testów.
Mogę pokazać 2-minutowe demo?"
```

**Demo (2 minuty):**
```
[Włącz system]
"Hej Streamware, jaka temperatura lutownicy na SMD 0603?"
[System odpowiada]
"Hej Streamware, timer 90 sekund"
[System odmierza]
"Hej Streamware, pinout ESP32 GPIO"
[System pokazuje/czyta]
```

**Pytania do zbadania:**
```
"Jakie sytuacje macie gdzie ręce są zajęte a trzeba 
sprawdzić coś w dokumentacji?"

"Jak często sięgacie do telefonu podczas pracy 
przy stanowisku?"

"Co byłoby najbardziej przydatne - timer, specyfikacje, 
przeliczniki, coś innego?"
```

**Zamknięcie:**
```
"Chciałbym zostawić tu system na 3 miesiące za darmo.
Jedyne co potrzebuję to szczery feedback - co działa, 
co nie, czego brakuje. Deal?"
```

---

### Rozmowa 2: Telefon do warsztatu

**Cel:** Umówić spotkanie

**Otwarcie:**
```
"Dzień dobry, czy rozmawiam z właścicielem warsztatu?
[Tak]
Dzień dobry, [Imię] z firmy Streamware. Dzwonię 
bo mamy asystenta głosowego dla mechaników - żeby 
nie trzeba było odkładać narzędzi żeby sprawdzić 
specyfikację. Czy ma pan minutę?"
```

**Jeśli TAK:**
```
"Krótko: mówi pan 'moment dokręcenia Golf 7 koło' 
i system odpowiada '120 niutonometrów'. Bez mycia rąk, 
bez odkładania narzędzi.

Firmy w Stanach mówią że oszczędza 10 minut na naprawie.

Chciałbym przyjechać na 15 minut, pokazać jak to działa 
i zobaczyć czy ma to sens w pana warsztacie. 
Kiedy mogę wpaść?"
```

**Jeśli NIE MA CZASU:**
```
"Rozumiem. Kiedy byłby lepszy moment na 2-minutową rozmowę?"
```

**Obiekcje:**

*"Nie potrzebuję"*
```
"Jasne, rozumiem. Tylko jedno pytanie - jak często 
pan lub pracownicy musicie przerywać pracę żeby 
sprawdzić coś w telefonie lub komputerze?"
```

*"Ile to kosztuje?"*
```
"Pilot to 500 złotych miesięcznie, bez zobowiązań. 
Ale najpierw chciałbym pokazać czy to w ogóle 
ma sens w pana warsztacie. Mogę przyjechać?"
```

*"Muszę się zastanowić"*
```
"Jasne. A co by pomogło w podjęciu decyzji? 
Mogę przyjechać z działającym systemem i pokazać 
na miejscu."
```

---

### Rozmowa 3: Demo w warsztacie

**Cel:** Podpisać pilot

**Setup (przed wizytą):**
- Tablet z aplikacją
- Słuchawka bluetooth
- Lista komend dla marek które obsługują
- Umowa pilotażu (1 strona)

**Przebieg:**
```
1. "Pokażę na przykładzie. Jakie auto macie teraz na podnośniku?"
   [np. Audi A4]

2. "Hej Streamware, moment dokręcenia koła Audi A4 B8"
   [System odpowiada]

3. "Hej Streamware, ile oleju do silnika 2.0 TDI"
   [System odpowiada]

4. "Teraz pan spróbuje - proszę zapytać o cokolwiek 
   związane z tym autem"
   [Klient próbuje]

5. "Widzę że działa/nie działa [X]. 
   W pilocie doszlifowalibyśmy to pod pana potrzeby.
   500 zł miesięcznie, możemy zacząć od jutra?"
```

---

## 📊 TRACKING ROZMÓW

### Tabela CRM (Excel/Notion)

| Data | Firma | Kontakt | Email/Tel | Status | Next Action | Notes |
|------|-------|---------|-----------|--------|-------------|-------|
| 12.12 | HS Warszawa | kontakt@ | email wysłany | Waiting | Follow-up 15.12 | |
| 12.12 | HS Kraków | Wiktor | email wysłany | Waiting | Follow-up 15.12 | |
| | Warsztat X | Jan Kowalski | 500-xxx-xxx | Do kontaktu | Zadzwonić 13.12 | Z OLX |

### Metryki do śledzenia

| Metryka | Target | Tydzień 1 | Tydzień 2 | Tydzień 3 | Tydzień 4 |
|---------|--------|-----------|-----------|-----------|-----------|
| Emaile wysłane | 20 | | | | |
| Odpowiedzi | 5 (25%) | | | | |
| Telefony | 15 | | | | |
| Rozmowy | 10 | | | | |
| Demo umówione | 5 | | | | |
| Demo wykonane | 4 | | | | |
| Piloty podpisane | 2 | | | | |

---

## 🔄 HARMONOGRAM TYGODNIOWY

### Tydzień 1
| Dzień | Działanie |
|-------|-----------|
| Pon | Email do Warsaw HS + Kraków HS + Wrocław HS |
| Wto | Email do Silesia HS + research warsztatów |
| Śro | Wizyta w Warsaw HS (jeśli odpowiedź) |
| Czw | Telefony do 5 warsztatów (cold call) |
| Pią | Follow-up emaile do HS + nighthack Kraków? |

### Tydzień 2
| Dzień | Działanie |
|-------|-----------|
| Pon | Follow-up telefony do warsztatów |
| Wto | Demo w hackerspaceie (jeśli umówione) |
| Śro | Kolejne 5 telefonów do warsztatów |
| Czw | Spotkania z zainteresowanymi warsztatami |
| Pią | Podsumowanie, planowanie tygodnia 3 |

---

## 📝 DOKUMENTY DO PRZYGOTOWANIA

### 1. Umowa pilotażu (1 strona)
- Czas trwania: 2 miesiące
- Koszt: [X] PLN/miesiąc
- Sprzęt: użyczenie (tablet + słuchawka)
- Wypowiedzenie: 7 dni
- Co jest wliczone: support, aktualizacje
- Dane kontaktowe obu stron

### 2. One-pager produktowy
- Problem (3 zdania)
- Rozwiązanie (3 zdania)
- Jak działa (screenshot + 3 przykłady)
- Cennik (tabela)
- Kontakt

### 3. FAQ dla sprzedaży
- "Czy działa offline?" → Tak/Nie, dlaczego
- "Jakie marki obsługujecie?" → Lista
- "Co jeśli nie rozumie?" → Fallback
- "Czy nagrywacie rozmowy?" → RODO

---

## ✅ CHECKLIST PRZED STARTEM

- [ ] Landing page streamware.pl aktywna
- [ ] Email firmowy (kontakt@streamware.pl)
- [ ] Telefon firmowy lub dedykowany numer
- [ ] Demo działające i przetestowane
- [ ] Tablet + słuchawka do demo
- [ ] Umowa pilotażu gotowa
- [ ] One-pager PDF gotowy
- [ ] CRM/Excel do trackingu
- [ ] Kalendarz na spotkania (Calendly?)
- [ ] Konto bankowe firmowe (do faktur)

---

*Plan utworzony: Grudzień 2024*
*Dla: Streamware Voice Shell*
