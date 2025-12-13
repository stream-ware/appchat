# STREAMWARE VOICE REFERENCE
## Komendy głosowe - Jak rozmawiać z systemem

---

## 🎤 PODSTAWY

### Jak to działa?

```
     🎤 TY MÓWISZ              🧠 SYSTEM ROZUMIE           📱 SYSTEM WYKONUJE
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ "Pokaż sprzedaż     │ →  │ Intent: show_data   │ →  │ • Query database    │
│  z ostatniego       │    │ Entity: sales       │    │ • Generate chart    │
│  tygodnia"          │    │ Time: last_week     │    │ • Display dashboard │
│                     │    │                     │    │ • Speak summary     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                                              ↓
                                                      🔊 ODPOWIEDŹ GŁOSOWA
                                                    "Sprzedaż z ostatniego
                                                     tygodnia wyniosła 
                                                     145 tysięcy złotych,
                                                     wzrost o 12% vs
                                                     poprzedni tydzień"
```

### Nie musisz mówić dokładnie tak samo

System rozumie **intencję**, nie słowa kluczowe:

```
✓ "Pokaż sprzedaż z ostatniego tygodnia"
✓ "Jaka była sprzedaż przez ostatni tydzień?"
✓ "Ile sprzedaliśmy w zeszłym tygodniu?"
✓ "Sprzedaż - last week"
✓ "Sales ostatnie 7 dni"

→ Wszystkie = ten sam wynik
```

### Wake word (opcjonalnie)

```
Domyślnie: Zawsze słucha (push-to-talk lub voice activity)

Z wake word:
"Hej Streamware" → [system aktywny]
"Pokaż kamery" → [wykonuje]

Konfigurowalne:
- "Hej Streamware"
- "OK Streamware" 
- "Asystent"
- Custom wake word
```

---

## 📊 KOMENDY: DASHBOARDY I DANE

### Podstawowe zapytania

| Mówisz | System robi |
|--------|-------------|
| "Jaka sprzedaż dzisiaj?" | Pokazuje KPI + mówi wartość |
| "Pokaż trend z miesiąca" | Wyświetla wykres liniowy |
| "Porównaj z poprzednim rokiem" | Side-by-side comparison |
| "Top 10 produktów" | Ranking + wykres |
| "Kto sprzedał najwięcej?" | Ranking sprzedawców |

### Filtry i agregacje

```
Przykłady:

"Pokaż sprzedaż w Warszawie"
→ Filter: region = Warszawa

"Sprzedaż kategorii elektronika w Q4"
→ Filter: category = elektronika, time = Q4

"Porównaj Warszawę z Krakowem"
→ Side-by-side: Warszawa vs Kraków

"Średnia sprzedaż na sprzedawcę"
→ Aggregation: AVG by salesperson

"Suma zamówień powyżej 10 tysięcy"
→ Filter: order_value > 10000, Aggregation: SUM
```

### Drill-down

```
[Dashboard pokazuje spadek w regionie Śląsk]

Ty: "Dlaczego spadek na Śląsku?"

System: "Analizuję... Główne przyczyny spadku to:
         1. Odejście kluczowego klienta ABC - minus 35 tysięcy
         2. Sezonowość - spadek vs rok wcześniej o 15%
         3. Brak kampanii promocyjnej vs inne regiony
         
         Pokazuję szczegóły na ekranie."

Ty: "Kto to jest klient ABC?"

System: "Klient ABC Sp. z o.o., NIP 123456789.
         Współpraca od 2019 roku.
         Ostatnie zamówienie: 15 października.
         Kontakt: Jan Kowalski, jan@abc.pl
         
         Chcesz zadzwonić lub napisać?"
```

### Eksport i raportowanie

```
"Eksportuj to do Excela"
→ Generuje XLSX, link do pobrania

"Wyślij raport do szefa"
→ Generuje PDF, wysyła na zdefiniowany email

"Zaplanuj ten raport na każdy poniedziałek"
→ Scheduled report, email delivery

"Zrób screenshot dashboardu"
→ PNG saved + link
```

---

## 🎥 KOMENDY: VIDEO I MONITORING

### Podgląd kamer

| Mówisz | System robi |
|--------|-------------|
| "Pokaż kamery" | Grid wszystkich kamer |
| "Pokaż kamerę przy wejściu" | Pojedynczy widok live |
| "Pełny ekran" | Fullscreen mode |
| "Następna kamera" | Przełącz widok |
| "Wróć do gridu" | Multi-view |

### Monitoring aktywny

```
"Obserwuj wejście i powiadom gdy ktoś przyjdzie"
→ System: "OK, obserwuję wejście. Powiadomię głosowo i wyślę alert."

[5 minut później]
System: "Uwaga - wykryto osobę przy wejściu głównym."

Ty: "Pokaż"
→ Live feed na ekranie

Ty: "Nagraj ostatnie 2 minuty"
→ Clip zapisany

Ty: "Wyślij do ochrony"
→ Clip wysłany na email/Slack
```

### Zliczanie i analiza

```
"Ile osób przeszło dzisiaj?"
→ "Dzisiaj przeszło 247 osób. 
    Wejścia: 128, Wyjścia: 119.
    Aktualnie w budynku: około 35 osób."

"Kiedy było największe natężenie?"
→ "Peak był między 12:00 a 13:00 - 45 osób.
    Pokazuję wykres na ekranie."

"Porównaj z wczoraj"
→ Side-by-side comparison + trend
```

### Detekcja specyficzna

```
"Powiadom gdy pojawi się samochód"
→ Monitoring: vehicle detection active

"Obserwuj czy ktoś podchodzi do drzwi"
→ Zone monitoring: entrance area

"Śledź osobę w czerwonej kurtce"
→ Object tracking initiated

"Pokaż wszystkie wykrycia z nocy"
→ Event timeline: night hours filter
```

### Kontrola nagrywania

```
"Zacznij nagrywać"
→ Recording started

"Zatrzymaj nagrywanie"
→ Recording stopped, saved

"Nagraj następne 30 minut"
→ Timed recording

"Pokaż nagranie z wczoraj godzina 15"
→ Playback: yesterday 15:00
```

---

## 📄 KOMENDY: DOKUMENTY

### Faktury

```
"Zeskanuj fakturę"
→ System aktywuje kamerę/upload
→ OCR + ekstrakcja
→ "Faktura od ABC Sp. z o.o., 
    kwota 12,500 złotych brutto,
    termin płatności: 15 grudnia.
    Zapisać?"

Ty: "Tak"
→ Saved + indexed

Ty: "Dodaj do rozliczeń z ABC"
→ Categorized
```

### Wyszukiwanie dokumentów

```
"Znajdź umowę z Kowalski S.A."
→ Lista dokumentów z tym podmiotem

"Pokaż wszystkie faktury z listopada"
→ Filtered list

"Ile wydaliśmy na IT w tym roku?"
→ Aggregation by category

"Znajdź umowy kończące się w Q1"
→ Date-based search

"Czy mamy podpisane NDA z ABC?"
→ Yes/No + document link if exists
```

### Analiza dokumentów

```
"Co jest w tej umowie?"
→ AI summary: kluczowe punkty

"Jakie kary umowne?"
→ Extract specific clause

"Porównaj z poprzednią wersją"
→ Diff view

"Czy ta umowa jest standardowa?"
→ Comparison vs template
```

---

## 🤖 KOMENDY: AUTOMATYZACJA

### Email

```
"Mam nowe maile?"
→ "Masz 5 nowych wiadomości.
    3 od klientów, 1 newsletter, 1 spam."

"Przeczytaj pierwszy"
→ [czyta na głos]

"Odpowiedz: Dziękuję, odezwę się jutro"
→ "Wysłać odpowiedź?"

"Tak, wyślij"
→ Sent

"Przekaż do Ani"
→ Forwarded

"Oznacz spam"
→ Moved to spam + filter created
```

### Kalendarz

```
"Jakie mam dzisiaj spotkania?"
→ "Masz 3 spotkania:
    9:00 - Sync z zespołem
    14:00 - Call z klientem XYZ
    16:30 - Review projektu"

"Przesuń sync o godzinę"
→ "Przesunąć na 10:00?"

"Tak"
→ Rescheduled + notifications sent

"Umów spotkanie z Janem na jutro"
→ "O której godzinie?"

"Po południu, znajdź wolny slot"
→ "Macie obaj wolne 14:00-15:00. Umówić?"
```

### Przypomnienia i taski

```
"Przypomnij mi o raporcie jutro o 9"
→ Reminder set

"Dodaj task: przygotować prezentację"
→ Task created

"Jakie mam taski na dziś?"
→ List

"Oznacz prezentację jako done"
→ Completed
```

### Komunikacja

```
"Wyślij na Slacka do #team: spotkanie o 15"
→ Message sent to #team

"Co nowego na #general?"
→ [czyta ostatnie messages]

"Zadzwoń do Jana"
→ Initiating call...

"Wyślij SMS do Ani: Będę 10 minut później"
→ SMS sent
```

---

## 🔧 KOMENDY: SYSTEM

### Status

```
"Status systemu"
→ "System działa normalnie.
    Aktywne: 3 kamery, 2 dashboardy, monitoring wejścia.
    Pamięć: 45% wykorzystane.
    Ostatni alert: 2 godziny temu."

"Jakie mam aktywne monitoringi?"
→ List of active watchers

"Pokaż logi z ostatniej godziny"
→ Event log
```

### Konfiguracja głosem

```
"Zmień głośność na 70%"
→ Volume adjusted

"Mów wolniej"
→ TTS speed decreased

"Zmień głos na kobiecy"
→ TTS voice changed

"Włącz wake word"
→ Wake word activated

"Nie powiadamiaj o ruchu w nocy"
→ Notification schedule updated
```

### Skills management

```
"Jakie mam zainstalowane skills?"
→ List of active skills

"Zainstaluj invoice-scanner"
→ Installation wizard

"Wyłącz weather na tydzień"
→ Skill disabled

"Zaktualizuj wszystkie skills"
→ Updates check + install
```

---

## 🔄 KONWERSACJE WIELOETAPOWE

### Przykład: Analiza sprzedaży

```
Ty: "Jak idzie sprzedaż?"

System: "Sprzedaż w tym miesiącu wynosi 234 tysiące złotych.
         To 8% więcej niż miesiąc temu.
         Wyświetlam dashboard."

Ty: "A rok temu?"

System: "Rok temu w tym samym miesiącu: 198 tysięcy.
         Wzrost rok do roku: 18%."

Ty: "Co się najlepiej sprzedaje?"

System: "Top 3 produkty:
         1. Produkt A - 45 tysięcy
         2. Produkt B - 38 tysięcy
         3. Produkt C - 29 tysięcy"

Ty: "Kto sprzedał najwięcej produktu A?"

System: "Jan Kowalski - 15 transakcji, 23 tysiące.
         Następny: Anna Nowak - 12 transakcji, 18 tysięcy."

Ty: "Wyślij podsumowanie do zespołu"

System: "Generuję raport...
         Wysłać na #sales-team na Slacku?"

Ty: "Tak, i mailem do szefa"

System: "Wysłano na Slack i email do jan.szef@firma.pl.
         Coś jeszcze?"
```

### Przykład: Incydent security

```
System: "Uwaga - wykryto ruch przy magazynie. 
         Jest 22:47, poza godzinami pracy."

Ty: "Pokaż"

System: [Wyświetla kamerę]
        "Widoczna jedna osoba, porusza się w kierunku drzwi."

Ty: "Nagraj i powiadom ochronę"

System: "Nagrywanie rozpoczęte.
         Wysłać alert do ochrony z klipem?"

Ty: "Tak"

System: "Alert wysłany do ochrony.
         Kontynuować nagrywanie?"

Ty: "Tak, do odwołania"

System: "OK, nagrywam. Powiadomię o zmianach."

[2 minuty później]
System: "Osoba wyszła z kadru. 
         Brak ruchu od 60 sekund.
         Zatrzymać nagrywanie?"

Ty: "Nagraj jeszcze 5 minut i zatrzymaj"

System: "OK, zatrzymam automatycznie o 22:54."
```

---

## 🌍 WIELOJĘZYCZNOŚĆ

### Polski (native)

```
"Pokaż sprzedaż z ostatniego tygodnia"
"Ile osób przeszło dzisiaj?"
"Znajdź fakturę od ABC"
```

### English (supported)

```
"Show sales from last week"
"How many people passed today?"
"Find invoice from ABC"
```

### Mixed (understood)

```
"Show sprzedaż from last week"
"Pokaż sales z ostatniego tygodnia"
"Ile było people today?"
```

### Konfiguracja

```
"Mów po angielsku"
→ TTS switches to English

"Rozumiej polski i angielski"
→ Multilingual mode

"Tylko polski"
→ Polish-only mode
```

---

## ⚡ SKRÓTY I POWER USER

### Aliasy (konfigurowalne)

```
Zamiast: "Pokaż dashboard sprzedaży z filtr region Warszawa"
Zdefiniuj: "Warszawa" → pełna komenda

Teraz wystarczy:
"Warszawa" → Dashboard sprzedaży Warszawa
```

### Makra głosowe

```
Zdefiniuj "Poranny raport":
  1. Pokaż dashboard KPI
  2. Przeczytaj alerty
  3. Wylistuj spotkania
  4. Sprawdź maile

Teraz:
"Poranny raport" → wykonuje wszystko po kolei
```

### Batch operations

```
"Zeskanuj wszystkie faktury z folderu Inbox"
→ Batch OCR

"Wyślij raport do Jana, Ani i Piotra"
→ Multiple recipients

"Eksportuj wszystkie dashboardy do PDF"
→ Batch export
```

---

## 🔒 BEZPIECZEŃSTWO GŁOSOWE

### Komendy chronione

```
"Usuń wszystkie dane"
→ "Ta operacja wymaga potwierdzenia hasłem.
    Podaj hasło głosowo lub wpisz."

"Wyłącz system"
→ "Jesteś pewien? Powiedz 'potwierdź wyłączenie'"
```

### Rozpoznawanie mówcy (opcjonalne)

```
Konfiguracja:
- Voice ID: tylko zarejestrowane głosy
- Admin commands: tylko admin voice
- Guest mode: ograniczone komendy
```

### Audit log

Każda komenda głosowa logowana:
- Timestamp
- User (voice ID if enabled)
- Command (transcript)
- Intent (recognized)
- Result (success/fail)

---

## ❓ TROUBLESHOOTING

### "System nie rozumie"

```
Spróbuj:
1. Mów wyraźniej / wolniej
2. Użyj prostszych słów
3. Podziel na części

"Pokaż sprzedaż produktu A w regionie Śląsk 
 z filtrem powyżej 1000 złotych z ostatniego kwartału"

→ Podziel:
   "Pokaż sprzedaż produktu A"
   "Filtruj region Śląsk"  
   "Tylko powyżej 1000"
   "Ostatni kwartał"
```

### "Źle zrozumiał"

```
"Anuluj" → Cofnij ostatnią akcję
"Nie to" → Odrzuć i słuchaj ponownie
"Powtórz" → Wykonaj ostatnią komendę ponownie
```

### Debug mode

```
"Włącz debug"
→ System pokazuje:
   - Rozpoznany tekst (STT)
   - Wykryty intent
   - Parametry
   - Wykonana akcja
```

---

*Streamware Voice Reference*
*Głos to Twój interfejs*

docs.streamware.pl/voice
