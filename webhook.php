<?php
/**
 * Streamware - Webhook dla Przelewy24
 * 
 * Ten plik odbiera potwierdzenia płatności z Przelewy24.
 * URL: https://streamware.pl/webhook.php
 */

// Konfiguracja (ta sama co w index.php)
$config = [
    'contact_email' => 'kontakt@streamware.pl',
    'p24_merchant_id' => 'XXXXX',
    'p24_pos_id' => 'XXXXX', 
    'p24_crc' => 'XXXXXXXXXXXXXXXX',
    'p24_api_url' => 'https://sandbox.przelewy24.pl',
];

// Logowanie
function logPayment($message) {
    $log = date('Y-m-d H:i:s') . " | " . $message . "\n";
    file_put_contents('logs/payments.log', $log, FILE_APPEND);
}

// Odbierz dane POST
$p24_session_id = $_POST['p24_session_id'] ?? '';
$p24_order_id = $_POST['p24_order_id'] ?? '';
$p24_amount = $_POST['p24_amount'] ?? 0;
$p24_currency = $_POST['p24_currency'] ?? '';
$p24_sign = $_POST['p24_sign'] ?? '';

logPayment("Otrzymano webhook: session=$p24_session_id, order=$p24_order_id, amount=$p24_amount");

// Weryfikuj podpis
$expected_sign = md5($p24_session_id . '|' . $p24_order_id . '|' . $p24_amount . '|' . $p24_currency . '|' . $config['p24_crc']);

if ($p24_sign !== $expected_sign) {
    logPayment("BŁĄD: Nieprawidłowy podpis dla session=$p24_session_id");
    http_response_code(400);
    exit('Invalid signature');
}

// Załaduj dane sesji
$session_file = "sessions/$p24_session_id.json";
if (!file_exists($session_file)) {
    logPayment("BŁĄD: Nie znaleziono sesji $p24_session_id");
    http_response_code(404);
    exit('Session not found');
}

$session = json_decode(file_get_contents($session_file), true);

// Weryfikuj kwotę
if ($session['amount'] != $p24_amount) {
    logPayment("BŁĄD: Niezgodna kwota dla session=$p24_session_id (oczekiwano {$session['amount']}, otrzymano $p24_amount)");
    http_response_code(400);
    exit('Amount mismatch');
}

// Weryfikuj transakcję w Przelewy24
$verify_data = [
    'p24_merchant_id' => $config['p24_merchant_id'],
    'p24_pos_id' => $config['p24_pos_id'],
    'p24_session_id' => $p24_session_id,
    'p24_order_id' => $p24_order_id,
    'p24_amount' => $p24_amount,
    'p24_currency' => $p24_currency,
    'p24_sign' => md5($p24_session_id . '|' . $p24_order_id . '|' . $p24_amount . '|' . $p24_currency . '|' . $config['p24_crc'])
];

$ch = curl_init($config['p24_api_url'] . '/trnVerify');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($verify_data));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);

// Parsuj odpowiedź
parse_str($response, $result);

if (isset($result['error']) && $result['error'] == '0') {
    // Płatność zweryfikowana!
    logPayment("SUKCES: Płatność zweryfikowana dla session=$p24_session_id, order=$p24_order_id");
    
    // Zaktualizuj sesję
    $session['status'] = 'paid';
    $session['order_id'] = $p24_order_id;
    $session['paid_at'] = date('Y-m-d H:i:s');
    file_put_contents($session_file, json_encode($session, JSON_PRETTY_PRINT));
    
    // Wyślij email z potwierdzeniem
    $to = $session['email'];
    $subject = "Streamware - Potwierdzenie zamówienia #$p24_order_id";
    $body = "Dzień dobry {$session['name']},\n\n";
    $body .= "Dziękujemy za zakup!\n\n";
    $body .= "Zamówienie: {$session['product']}\n";
    $body .= "Kwota: " . number_format($p24_amount / 100, 2) . " PLN\n";
    $body .= "Numer zamówienia: $p24_order_id\n\n";
    $body .= "Skontaktujemy się w ciągu 24h z instrukcjami instalacji.\n\n";
    $body .= "Pozdrawiamy,\nZespół Streamware";
    
    mail($to, $subject, $body, "From: {$config['contact_email']}");
    
    // Powiadom zespół
    $admin_body = "Nowe zamówienie!\n\n";
    $admin_body .= "Klient: {$session['name']}\n";
    $admin_body .= "Email: {$session['email']}\n";
    $admin_body .= "Firma: {$session['company']}\n";
    $admin_body .= "NIP: {$session['nip']}\n";
    $admin_body .= "Produkt: {$session['product']}\n";
    $admin_body .= "Kwota: " . number_format($p24_amount / 100, 2) . " PLN\n";
    $admin_body .= "Order ID: $p24_order_id\n";
    
    mail($config['contact_email'], "💰 Nowe zamówienie #$p24_order_id", $admin_body);
    
    http_response_code(200);
    echo 'OK';
    
} else {
    logPayment("BŁĄD: Weryfikacja nieudana dla session=$p24_session_id: " . print_r($result, true));
    http_response_code(400);
    exit('Verification failed');
}
