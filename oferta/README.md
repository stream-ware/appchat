# Streamware Landing Page - Instrukcja Instalacji

## Wymagania
- PHP 7.4+
- Serwer Apache/Nginx z SSL (HTTPS wymagane dla płatności)
- Funkcja mail() lub SMTP

## Szybka instalacja

### 1. Upload plików
```bash
# Skopiuj pliki na serwer
scp -r streamware-landing/* user@server:/var/www/streamware.pl/
```

### 2. Utwórz katalogi
```bash
mkdir -p /var/www/streamware.pl/sessions
mkdir -p /var/www/streamware.pl/logs
chmod 755 /var/www/streamware.pl/sessions
chmod 755 /var/www/streamware.pl/logs
```

### 3. Skonfiguruj index.php
Edytuj sekcję `$config` w `index.php`:

```php
$config = [
    'site_name' => 'Streamware',
    'site_url' => 'https://streamware.pl',  // Twoja domena
    'contact_email' => 'kontakt@streamware.pl',  // Twój email
    'phone' => '+48 XXX XXX XXX',  // Twój telefon
    
    // Przelewy24 - dane z panelu https://panel.przelewy24.pl
    'p24_merchant_id' => 'XXXXX',  // ID sprzedawcy
    'p24_pos_id' => 'XXXXX',  // ID punktu sprzedaży
    'p24_crc' => 'XXXXXXXXXXXXXXXX',  // Klucz CRC
    'p24_api_url' => 'https://secure.przelewy24.pl',  // Produkcja
    // lub 'https://sandbox.przelewy24.pl' dla testów
];
```

### 4. Skonfiguruj Przelewy24

1. Zarejestruj się na https://www.przelewy24.pl
2. W panelu dodaj nowy punkt sprzedaży
3. Ustaw URL powrotu: `https://streamware.pl/index.php?payment=success`
4. Ustaw URL statusu (webhook): `https://streamware.pl/webhook.php`
5. Skopiuj dane do `$config`

### 5. Testuj lokalnie (opcjonalnie)
```bash
cd streamware-landing
php -S localhost:8000
# Otwórz http://localhost:8000
```

## Konfiguracja serwera (Nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name streamware.pl www.streamware.pl;
    root /var/www/streamware.pl;
    index index.php;
    
    ssl_certificate /etc/letsencrypt/live/streamware.pl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/streamware.pl/privkey.pem;
    
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }
    
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
    
    # Blokuj dostęp do sesji i logów
    location ~ ^/(sessions|logs) {
        deny all;
        return 404;
    }
}

# Redirect HTTP -> HTTPS
server {
    listen 80;
    server_name streamware.pl www.streamware.pl;
    return 301 https://streamware.pl$request_uri;
}
```

## Testowanie płatności

1. Użyj sandbox Przelewy24 (`p24_api_url` = `https://sandbox.przelewy24.pl`)
2. Testowe dane karty: 
   - Numer: 4111 1111 1111 1111
   - Data: dowolna przyszła
   - CVV: 123
3. Sprawdź logi: `tail -f logs/payments.log`

## Customizacja

### Zmiana kolorów
Edytuj zmienne CSS w `<style>`:
```css
:root {
    --primary: #2563eb;      /* Główny kolor */
    --secondary: #10b981;    /* Akcent */
    --dark: #1f2937;         /* Tekst */
}
```

### Dodawanie produktów
Dodaj do `$config['prices']`:
```php
'nowy_produkt' => [
    'name' => 'Nazwa produktu', 
    'price' => 100000,  // W groszach (1000 PLN)
    'display' => '1 000 PLN'
],
```

### SMTP zamiast mail()
Użyj PHPMailer:
```bash
composer require phpmailer/phpmailer
```

## Bezpieczeństwo

- [ ] HTTPS włączone
- [ ] Katalogi sessions/ i logs/ niedostępne publicznie
- [ ] Dane Przelewy24 nie w repozytorium (użyj .env)
- [ ] Regularne backupy

## Wsparcie

Email: kontakt@streamware.pl

---

*Wygenerowano: grudzień 2024*
