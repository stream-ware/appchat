# Streamware - System Kontroli Dostępu (RBAC)

## Przegląd

Streamware implementuje system kontroli dostępu oparty na rolach (Role-Based Access Control - RBAC), który umożliwia zarządzanie uprawnieniami użytkowników do różnych modułów aplikacji.

## Role systemowe

| Rola | Nazwa wyświetlana | Uprawnienia | Opis |
|------|-------------------|-------------|------|
| `admin` | Administrator | `*` (wszystkie) | Pełny dostęp do wszystkich funkcji systemu |
| `office` | Pracownik biurowy | documents, sales, analytics, system | Dostęp do dokumentów, sprzedaży i analityki |
| `security` | Ochrona | cameras, home, system | Dostęp do monitoringu i systemów bezpieczeństwa |
| `manager` | Manager | documents, sales, analytics, cameras, system | Dostęp do biura i monitoringu |
| `guest` | Gość | system | Tylko podstawowe funkcje systemu |

## Użytkownicy demo

| Login | Hasło | Rola | Dostępne moduły |
|-------|-------|------|-----------------|
| `admin` | `admin123` | Administrator | Wszystkie |
| `kowalski` | `biuro123` | Pracownik biurowy | Dokumenty, Sprzedaż, Analityka |
| `dozorca` | `ochrona123` | Ochrona | Kamery, Smart Home |
| `manager` | `manager123` | Manager | Dokumenty, Sprzedaż, Analityka, Kamery |
| `gosc` | `gosc123` | Gość | Tylko system (pomoc, status) |

## Moduły aplikacji

### 📄 Dokumenty (`documents`)
- Zarządzanie fakturami
- Skanowanie dokumentów
- Umowy i kontrakty
- Eksport do Excel

### 🎥 Monitoring (`cameras`)
- Podgląd kamer CCTV
- Wykrywanie ruchu
- Alerty bezpieczeństwa
- Historia nagrań

### 📊 Sprzedaż (`sales`)
- Dashboard KPI
- Raporty sprzedażowe
- Porównanie regionów
- Prognozy

### 🏠 Smart Home (`home`)
- Temperatura i czujniki
- Sterowanie oświetleniem
- Zarządzanie energią
- System alarmowy

### 📈 Analityka (`analytics`)
- Raporty dzienne/tygodniowe
- Wykresy i trendy
- Wykrywanie anomalii
- Predykcje AI

### 🌐 Internet (`internet`)
- Pogoda (Open-Meteo API)
- Kursy kryptowalut (CoinGecko)
- Kanały RSS
- Email, MQTT, Webhooks

### ⚙️ System (`system`)
- Pomoc i dokumentacja
- Status systemu
- Historia konwersacji
- Logowanie/wylogowanie

## Logowanie przez chat

### Komenda logowania
```
login [użytkownik] [hasło]
```

Przykłady:
```
login admin admin123
login kowalski biuro123
login dozorca ochrona123
```

### Komenda wylogowania
```
logout
```
lub
```
wyloguj
```

### Sprawdzenie aktualnego użytkownika
```
kto
```
lub
```
whoami
```

## API Endpoints

### Autentykacja

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

### Lista użytkowników (tylko admin)
```http
GET /api/users
```

### Status użytkownika
```http
GET /api/user/{session_id}
```

## Architektura

### UserManager

Klasa `UserManager` zarządza użytkownikami i autentykacją:

```python
class UserManager:
    ROLES = {...}       # Definicje ról
    USERS = {...}       # Użytkownicy systemu
    
    def authenticate(username, password) -> User
    def login(session_id, username, password) -> Dict
    def logout(session_id) -> bool
    def has_permission(session_id, app_type) -> bool
    def get_allowed_apps(session_id) -> List[str]
```

### SkillRegistry

Klasa `SkillRegistry` przechowuje wszystkie dostępne funkcje:

```python
class SkillRegistry:
    APPS = {
        "documents": {"name": "...", "skills": [...]},
        "cameras": {"name": "...", "skills": [...]},
        ...
    }
    
    def get_apps_for_user(permissions) -> Dict
    def get_all_commands() -> List[Dict]
```

## Przepływ autoryzacji

```
1. Użytkownik łączy się przez WebSocket
2. Otrzymuje widok powitalny (welcome dashboard)
3. Wpisuje: "login kowalski biuro123"
4. System weryfikuje dane logowania
5. Po zalogowaniu dashboard pokazuje tylko dozwolone moduły
6. Przy próbie dostępu do niedozwolonego modułu:
   - Wyświetlany jest komunikat "Brak dostępu"
   - Użytkownik wraca do dashboard
```

## Bezpieczeństwo

### Obecna implementacja (demo)
- Hasła przechowywane jako plain text
- Brak sesji po stronie serwera (tylko w pamięci)
- Brak tokenów JWT

### Zalecenia dla produkcji
- Użyć bcrypt/argon2 do hashowania haseł
- Implementować JWT tokens
- Dodać rate limiting
- Użyć HTTPS
- Przechowywać sesje w Redis
- Dodać 2FA

## Przykłady użycia

### Scenariusz 1: Pracownik biurowy (kowalski)
```
> login kowalski biuro123
✅ Zalogowano jako Jan Kowalski (Pracownik biurowy)

> pokaż faktury
[Wyświetla listę faktur]

> pokaż kamery
🚫 Brak dostępu do: cameras
```

### Scenariusz 2: Ochrona (dozorca)
```
> login dozorca ochrona123
✅ Zalogowano jako Tomasz Nowak (Ochrona)

> pokaż kamery
[Wyświetla podgląd kamer]

> pokaż faktury
🚫 Brak dostępu do: documents
```

### Scenariusz 3: Administrator
```
> login admin admin123
✅ Zalogowano jako Administrator

> [dostęp do wszystkich modułów]
```

## Rozszerzanie systemu

### Dodawanie nowej roli
```python
UserManager.ROLES["custom_role"] = {
    "display": "Nazwa roli",
    "permissions": ["documents", "cameras"],
    "description": "Opis roli"
}
```

### Dodawanie nowego użytkownika
```python
UserManager.USERS["nowy_user"] = User(
    username="nowy_user",
    password="haslo123",
    role="custom_role",
    display_name="Nowy Użytkownik",
    permissions=["documents", "cameras"]
)
```

---

**Wersja:** 0.3.0  
**Ostatnia aktualizacja:** 2024-12-13
