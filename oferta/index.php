<?php
/**
 * Streamware Voice Shell - Landing Page
 * 
 * Konfiguracja:
 * 1. Ustaw zmienne $config poniżej
 * 2. Skonfiguruj SMTP lub użyj mail()
 * 3. Dla płatności: zarejestruj się w Przelewy24 lub Stripe
 */

// ============================================
// KONFIGURACJA
// ============================================
$config = [
    'site_name' => 'Streamware',
    'site_url' => 'https://streamware.pl',
    'contact_email' => 'kontakt@streamware.pl',
    'phone' => '+48 XXX XXX XXX',
    
    // Przelewy24 (sandbox/produkcja)
    'p24_merchant_id' => 'XXXXX',
    'p24_pos_id' => 'XXXXX', 
    'p24_crc' => 'XXXXXXXXXXXXXXXX',
    'p24_api_url' => 'https://sandbox.przelewy24.pl', // lub https://secure.przelewy24.pl
    
    // Ceny (w groszach dla Przelewy24)
    'prices' => [
        'pilot_warsztat' => ['name' => 'Pilot Warsztat (2 mies)', 'price' => 100000, 'display' => '1 000 PLN'],
        'pilot_magazyn' => ['name' => 'Pilot Magazyn (2 mies)', 'price' => 200000, 'display' => '2 000 PLN'],
        'starter_roczny' => ['name' => 'Starter Roczny', 'price' => 480000, 'display' => '4 800 PLN'],
        'pro_roczny' => ['name' => 'Pro Roczny', 'price' => 1200000, 'display' => '12 000 PLN'],
    ]
];

// ============================================
// OBSŁUGA FORMULARZA
// ============================================
$message = '';
$message_type = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    
    // Formularz kontaktowy
    if (isset($_POST['action']) && $_POST['action'] === 'contact') {
        $name = htmlspecialchars(trim($_POST['name'] ?? ''));
        $email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);
        $company = htmlspecialchars(trim($_POST['company'] ?? ''));
        $phone = htmlspecialchars(trim($_POST['phone'] ?? ''));
        $segment = htmlspecialchars(trim($_POST['segment'] ?? ''));
        $msg = htmlspecialchars(trim($_POST['message'] ?? ''));
        
        if ($name && $email && $msg) {
            $to = $config['contact_email'];
            $subject = "[Streamware] Nowe zapytanie od: $name";
            $body = "Imię: $name\n";
            $body .= "Email: $email\n";
            $body .= "Firma: $company\n";
            $body .= "Telefon: $phone\n";
            $body .= "Segment: $segment\n";
            $body .= "---\n$msg";
            $headers = "From: $email\r\nReply-To: $email";
            
            if (mail($to, $subject, $body, $headers)) {
                $message = 'Dziękujemy! Odpowiemy w ciągu 24h.';
                $message_type = 'success';
            } else {
                $message = 'Błąd wysyłki. Zadzwoń: ' . $config['phone'];
                $message_type = 'error';
            }
        } else {
            $message = 'Wypełnij wszystkie wymagane pola.';
            $message_type = 'error';
        }
    }
    
    // Inicjacja płatności
    if (isset($_POST['action']) && $_POST['action'] === 'purchase') {
        $product_id = $_POST['product'] ?? '';
        $buyer_email = filter_var($_POST['buyer_email'] ?? '', FILTER_VALIDATE_EMAIL);
        $buyer_name = htmlspecialchars(trim($_POST['buyer_name'] ?? ''));
        $buyer_company = htmlspecialchars(trim($_POST['buyer_company'] ?? ''));
        $buyer_nip = htmlspecialchars(trim($_POST['buyer_nip'] ?? ''));
        
        if (isset($config['prices'][$product_id]) && $buyer_email && $buyer_name) {
            $product = $config['prices'][$product_id];
            $session_id = uniqid('SW_', true);
            
            // Zapisz sesję do pliku/bazy (uproszczone)
            $session_data = [
                'session_id' => $session_id,
                'product' => $product_id,
                'amount' => $product['price'],
                'email' => $buyer_email,
                'name' => $buyer_name,
                'company' => $buyer_company,
                'nip' => $buyer_nip,
                'created' => date('Y-m-d H:i:s')
            ];
            file_put_contents("sessions/$session_id.json", json_encode($session_data));
            
            // Przygotuj dane dla Przelewy24
            $p24_data = [
                'p24_merchant_id' => $config['p24_merchant_id'],
                'p24_pos_id' => $config['p24_pos_id'],
                'p24_session_id' => $session_id,
                'p24_amount' => $product['price'],
                'p24_currency' => 'PLN',
                'p24_description' => $product['name'],
                'p24_email' => $buyer_email,
                'p24_country' => 'PL',
                'p24_url_return' => $config['site_url'] . '/index.php?payment=success',
                'p24_url_status' => $config['site_url'] . '/webhook.php',
                'p24_api_version' => '3.2',
                'p24_encoding' => 'UTF-8',
            ];
            
            // Oblicz CRC
            $crc_string = $session_id . '|' . $config['p24_merchant_id'] . '|' . 
                         $product['price'] . '|PLN|' . $config['p24_crc'];
            $p24_data['p24_sign'] = md5($crc_string);
            
            // Redirect do Przelewy24
            $redirect_url = $config['p24_api_url'] . '/trnRequest/' . 
                           $config['p24_merchant_id'] . '?' . http_build_query($p24_data);
            
            // W produkcji: header("Location: $redirect_url"); exit;
            $message = "Demo: Przekierowanie do płatności dla: {$product['name']} ({$product['display']})";
            $message_type = 'info';
        }
    }
}

// Sprawdź powrót z płatności
if (isset($_GET['payment']) && $_GET['payment'] === 'success') {
    $message = 'Dziękujemy za płatność! Skontaktujemy się w ciągu 24h z instrukcjami instalacji.';
    $message_type = 'success';
}
?>
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streamware - Asystent Głosowy dla Przemysłu</title>
    <meta name="description" content="Voice assistant hands-free dla warsztatów, magazynów i produkcji. Mów zamiast klikać - ręce zostają przy pracy.">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #10b981;
            --dark: #1f2937;
            --light: #f3f4f6;
            --white: #ffffff;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: var(--dark);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        header {
            background: var(--white);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 100;
        }
        
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary);
            text-decoration: none;
        }
        
        .nav-links {
            display: flex;
            gap: 30px;
            list-style: none;
        }
        
        .nav-links a {
            color: var(--dark);
            text-decoration: none;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: var(--primary);
        }
        
        .btn {
            display: inline-block;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            font-size: 1rem;
        }
        
        .btn-primary {
            background: var(--primary);
            color: var(--white);
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
        }
        
        .btn-secondary {
            background: var(--secondary);
            color: var(--white);
        }
        
        .btn-outline {
            background: transparent;
            border: 2px solid var(--primary);
            color: var(--primary);
        }
        
        /* Hero */
        .hero {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: var(--white);
            padding: 150px 0 100px;
            text-align: center;
        }
        
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 20px;
        }
        
        .hero p {
            font-size: 1.25rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto 30px;
        }
        
        .hero-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        /* Features */
        .features {
            padding: 80px 0;
            background: var(--light);
        }
        
        .section-title {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .section-title h2 {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }
        
        .feature-card {
            background: var(--white);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .feature-card h3 {
            margin-bottom: 15px;
            color: var(--primary);
        }
        
        /* Use Cases */
        .use-cases {
            padding: 80px 0;
        }
        
        .use-case-item {
            display: flex;
            align-items: center;
            gap: 50px;
            margin-bottom: 60px;
        }
        
        .use-case-item:nth-child(even) {
            flex-direction: row-reverse;
        }
        
        .use-case-content {
            flex: 1;
        }
        
        .use-case-visual {
            flex: 1;
            background: var(--light);
            padding: 40px;
            border-radius: 12px;
            text-align: center;
        }
        
        .voice-example {
            background: var(--dark);
            color: var(--white);
            padding: 20px;
            border-radius: 8px;
            font-family: monospace;
            margin: 15px 0;
        }
        
        .voice-example .user {
            color: var(--secondary);
        }
        
        .voice-example .system {
            color: #60a5fa;
        }
        
        /* Pricing */
        .pricing {
            padding: 80px 0;
            background: var(--light);
        }
        
        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        .price-card {
            background: var(--white);
            padding: 40px 30px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            position: relative;
        }
        
        .price-card.featured {
            border: 3px solid var(--primary);
            transform: scale(1.05);
        }
        
        .price-card.featured::before {
            content: 'Najpopularniejszy';
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary);
            color: var(--white);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        
        .price-card h3 {
            margin-bottom: 10px;
        }
        
        .price {
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--primary);
            margin: 20px 0;
        }
        
        .price span {
            font-size: 1rem;
            color: var(--dark);
        }
        
        .price-features {
            list-style: none;
            margin: 20px 0 30px;
            text-align: left;
        }
        
        .price-features li {
            padding: 10px 0;
            border-bottom: 1px solid var(--light);
        }
        
        .price-features li::before {
            content: '✓';
            color: var(--secondary);
            margin-right: 10px;
        }
        
        /* Contact Form */
        .contact {
            padding: 80px 0;
        }
        
        .contact-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 50px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid var(--light);
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .contact-info h3 {
            margin-bottom: 20px;
        }
        
        .contact-item {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding: 15px;
            background: var(--light);
            border-radius: 8px;
        }
        
        /* Purchase Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: var(--white);
            padding: 40px;
            border-radius: 12px;
            max-width: 500px;
            width: 90%;
            position: relative;
        }
        
        .modal-close {
            position: absolute;
            top: 15px;
            right: 15px;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        /* Messages */
        .message {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .message.success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .message.error {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .message.info {
            background: #dbeafe;
            color: #1e40af;
        }
        
        /* Footer */
        footer {
            background: var(--dark);
            color: var(--white);
            padding: 40px 0;
            text-align: center;
        }
        
        footer a {
            color: var(--white);
            opacity: 0.8;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .nav-links {
                display: none;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .use-case-item {
                flex-direction: column !important;
            }
            
            .contact-grid {
                grid-template-columns: 1fr;
            }
            
            .price-card.featured {
                transform: none;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <nav>
                <a href="#" class="logo">🎤 Streamware</a>
                <ul class="nav-links">
                    <li><a href="#features">Funkcje</a></li>
                    <li><a href="#use-cases">Zastosowania</a></li>
                    <li><a href="#pricing">Cennik</a></li>
                    <li><a href="#contact">Kontakt</a></li>
                </ul>
                <a href="#contact" class="btn btn-primary">Umów demo</a>
            </nav>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>Asystent głosowy dla przemysłu</h1>
            <p>Mów zamiast klikać. Ręce zostają przy pracy. Voice control dla warsztatów, magazynów i produkcji.</p>
            <div class="hero-buttons">
                <a href="#contact" class="btn btn-secondary">Zamów demo</a>
                <a href="#pricing" class="btn btn-outline" style="color: white; border-color: white;">Zobacz cennik</a>
            </div>
        </div>
    </section>

    <?php if ($message): ?>
    <div class="container" style="padding-top: 20px;">
        <div class="message <?= $message_type ?>"><?= $message ?></div>
    </div>
    <?php endif; ?>

    <section id="features" class="features">
        <div class="container">
            <div class="section-title">
                <h2>Dlaczego Streamware?</h2>
                <p>Jedyne rozwiązanie łączące video analytics + voice control + automatyzację</p>
            </div>
            <div class="features-grid">
                <div class="feature-card">
                    <h3>🎤 Voice Control</h3>
                    <p>Mów naturalnym językiem. System rozumie polskie komendy i odpowiada głosowo. Bez szkoleń, bez nauki komend.</p>
                </div>
                <div class="feature-card">
                    <h3>🔧 Hands-Free</h3>
                    <p>Idealne gdy ręce są zajęte lub brudne: lutowanie, spawanie, mechanika, magazyn, kuchnia.</p>
                </div>
                <div class="feature-card">
                    <h3>📊 Dokumentacja</h3>
                    <p>Natychmiastowy dostęp do specyfikacji, momentów dokręcania, schematów. Bez przerywania pracy.</p>
                </div>
                <div class="feature-card">
                    <h3>⏱️ Timery i alerty</h3>
                    <p>Głosowe timery, przypomnienia, alerty. "Timer 5 minut na utwardzanie" - proste.</p>
                </div>
                <div class="feature-card">
                    <h3>🔒 Dane w Polsce</h3>
                    <p>Serwery w Polsce, RODO-compliant. Twoje dane nie wędrują za ocean.</p>
                </div>
                <div class="feature-card">
                    <h3>💰 70% taniej</h3>
                    <p>Konkurencja (Vocollect, Honeywell) = 20-30k PLN. My = od 4 800 PLN/rok.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="use-cases" class="use-cases">
        <div class="container">
            <div class="section-title">
                <h2>Zastosowania</h2>
            </div>
            
            <div class="use-case-item">
                <div class="use-case-content">
                    <h3>🔧 Warsztaty samochodowe</h3>
                    <p>Ręce w oleju? Nie ma problemu. Zapytaj głosowo o moment dokręcania, schemat, ilość oleju.</p>
                    <p><strong>Oszczędność:</strong> 10 minut na naprawie = 2 godziny dziennie</p>
                </div>
                <div class="use-case-visual">
                    <div class="voice-example">
                        <p class="user">"Moment dokręcenia koła Golf 7"</p>
                        <p class="system">→ "120 niutonometrów"</p>
                    </div>
                    <div class="voice-example">
                        <p class="user">"Ile oleju do 2.0 TDI Audi A4"</p>
                        <p class="system">→ "4.2 litra z filtrem"</p>
                    </div>
                </div>
            </div>
            
            <div class="use-case-item">
                <div class="use-case-content">
                    <h3>❄️ Magazyny i mroźnie</h3>
                    <p>Rękawice termiczne uniemożliwiają dotyk ekranu. Voice picking rozwiązuje problem.</p>
                    <p><strong>Oszczędność:</strong> 30% szybsza kompletacja, 90% mniej błędów</p>
                </div>
                <div class="use-case-visual">
                    <div class="voice-example">
                        <p class="user">"Następna pozycja"</p>
                        <p class="system">→ "Alejka B, półka 3, SKU 12847, ilość 5"</p>
                    </div>
                    <div class="voice-example">
                        <p class="user">"Potwierdź"</p>
                        <p class="system">→ "Zapisano. Pozostało 12 pozycji"</p>
                    </div>
                </div>
            </div>
            
            <div class="use-case-item">
                <div class="use-case-content">
                    <h3>🔌 Elektronika / Hackerspace</h3>
                    <p>Lutowanie, CNC, spawanie - wszędzie gdzie obie ręce są zajęte.</p>
                    <p><strong>Funkcje:</strong> Dokumentacja, pinouty, przeliczniki, timery</p>
                </div>
                <div class="use-case-visual">
                    <div class="voice-example">
                        <p class="user">"Temperatura lutownicy SMD 0603"</p>
                        <p class="system">→ "300-320 stopni Celsjusza"</p>
                    </div>
                    <div class="voice-example">
                        <p class="user">"Timer 90 sekund"</p>
                        <p class="system">→ [odmierza i sygnalizuje]</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="pricing" class="pricing">
        <div class="container">
            <div class="section-title">
                <h2>Cennik</h2>
                <p>Bez ukrytych kosztów. Pilot = 100% zaliczany na roczną licencję.</p>
            </div>
            <div class="pricing-grid">
                <div class="price-card">
                    <h3>Pilot</h3>
                    <div class="price">1 000 PLN<span>/2 mies</span></div>
                    <ul class="price-features">
                        <li>2 miesiące testów</li>
                        <li>1 stanowisko</li>
                        <li>Sprzęt w użyczeniu</li>
                        <li>Pełne wsparcie</li>
                        <li>100% zaliczane na roczną</li>
                    </ul>
                    <button class="btn btn-primary" onclick="openPurchase('pilot_warsztat')">Zamów pilot</button>
                </div>
                <div class="price-card featured">
                    <h3>Starter Roczny</h3>
                    <div class="price">4 800 PLN<span>/rok</span></div>
                    <ul class="price-features">
                        <li>Do 3 stanowisk</li>
                        <li>Dokumentacja techniczna</li>
                        <li>Voice control PL/EN</li>
                        <li>Email support</li>
                        <li>Aktualizacje w cenie</li>
                    </ul>
                    <button class="btn btn-primary" onclick="openPurchase('starter_roczny')">Wybierz</button>
                </div>
                <div class="price-card">
                    <h3>Pro Roczny</h3>
                    <div class="price">12 000 PLN<span>/rok</span></div>
                    <ul class="price-features">
                        <li>Do 10 stanowisk</li>
                        <li>Wszystko ze Starter</li>
                        <li>Integracja z WMS/ERP</li>
                        <li>Priorytetowe wsparcie</li>
                        <li>Custom komendy</li>
                    </ul>
                    <button class="btn btn-primary" onclick="openPurchase('pro_roczny')">Wybierz</button>
                </div>
            </div>
        </div>
    </section>

    <section id="contact" class="contact">
        <div class="container">
            <div class="section-title">
                <h2>Umów demo</h2>
                <p>Pokażemy działający system w 15 minut. Bez zobowiązań.</p>
            </div>
            <div class="contact-grid">
                <form method="POST">
                    <input type="hidden" name="action" value="contact">
                    <div class="form-group">
                        <label>Imię i nazwisko *</label>
                        <input type="text" name="name" required>
                    </div>
                    <div class="form-group">
                        <label>Email *</label>
                        <input type="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>Firma</label>
                        <input type="text" name="company">
                    </div>
                    <div class="form-group">
                        <label>Telefon</label>
                        <input type="tel" name="phone">
                    </div>
                    <div class="form-group">
                        <label>Branża</label>
                        <select name="segment">
                            <option value="">Wybierz...</option>
                            <option value="warsztat">Warsztat samochodowy</option>
                            <option value="magazyn">Magazyn / Logistyka</option>
                            <option value="produkcja">Produkcja</option>
                            <option value="elektronika">Elektronika / Hackerspace</option>
                            <option value="gastronomia">Gastronomia</option>
                            <option value="inne">Inne</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Wiadomość *</label>
                        <textarea name="message" rows="4" required placeholder="Opisz krótko swoje potrzeby..."></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Wyślij zapytanie</button>
                </form>
                <div class="contact-info">
                    <h3>Kontakt bezpośredni</h3>
                    <div class="contact-item">
                        <span>📧</span>
                        <div>
                            <strong>Email</strong><br>
                            <?= $config['contact_email'] ?>
                        </div>
                    </div>
                    <div class="contact-item">
                        <span>📞</span>
                        <div>
                            <strong>Telefon</strong><br>
                            <?= $config['phone'] ?>
                        </div>
                    </div>
                    <div class="contact-item">
                        <span>⏰</span>
                        <div>
                            <strong>Odpowiadamy</strong><br>
                            W ciągu 24 godzin (dni robocze)
                        </div>
                    </div>
                    <div style="margin-top: 30px; padding: 20px; background: var(--light); border-radius: 8px;">
                        <h4>🎁 Darmowy pilot dla Hackerspaces</h4>
                        <p style="margin-top: 10px;">Jesteś z hackerspace? Dajemy system za darmo na 3 miesiące w zamian za feedback. <a href="mailto:<?= $config['contact_email'] ?>?subject=Pilot%20Hackerspace">Napisz do nas!</a></p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Modal zakupu -->
    <div class="modal" id="purchaseModal">
        <div class="modal-content">
            <button class="modal-close" onclick="closeModal()">&times;</button>
            <h2>Zamówienie</h2>
            <p id="purchaseProduct" style="margin: 15px 0; font-size: 1.2rem; color: var(--primary);"></p>
            <form method="POST">
                <input type="hidden" name="action" value="purchase">
                <input type="hidden" name="product" id="purchaseProductId">
                <div class="form-group">
                    <label>Imię i nazwisko *</label>
                    <input type="text" name="buyer_name" required>
                </div>
                <div class="form-group">
                    <label>Email *</label>
                    <input type="email" name="buyer_email" required>
                </div>
                <div class="form-group">
                    <label>Firma (do faktury)</label>
                    <input type="text" name="buyer_company">
                </div>
                <div class="form-group">
                    <label>NIP (do faktury)</label>
                    <input type="text" name="buyer_nip" pattern="[0-9]{10}" placeholder="1234567890">
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Przejdź do płatności</button>
                <p style="margin-top: 15px; font-size: 0.9rem; opacity: 0.7;">
                    Płatność obsługiwana przez Przelewy24. Po płatności otrzymasz fakturę i instrukcje instalacji.
                </p>
            </form>
        </div>
    </div>

    <footer>
        <div class="container">
            <p>&copy; <?= date('Y') ?> Streamware | <a href="mailto:<?= $config['contact_email'] ?>"><?= $config['contact_email'] ?></a></p>
            <p style="margin-top: 10px; opacity: 0.7;">
                <a href="/regulamin.html">Regulamin</a> | 
                <a href="/polityka-prywatnosci.html">Polityka prywatności</a>
            </p>
        </div>
    </footer>

    <script>
        const prices = <?= json_encode($config['prices']) ?>;
        
        function openPurchase(productId) {
            const product = prices[productId];
            document.getElementById('purchaseProduct').textContent = product.name + ' - ' + product.display;
            document.getElementById('purchaseProductId').value = productId;
            document.getElementById('purchaseModal').classList.add('active');
        }
        
        function closeModal() {
            document.getElementById('purchaseModal').classList.remove('active');
        }
        
        // Zamknij modal klikając poza
        document.getElementById('purchaseModal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
        
        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    </script>
</body>
</html>
