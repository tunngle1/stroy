<?php
/**
 * СтройАутсорс — приём заявок с форм сайта.
 * Отправляет письмо на info@stroyautsors.ru и пишет запись в журнал согласий.
 * Требования: PHP 7.4+, функция mail() (настраивается в панели Timeweb).
 */
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

const TO_EMAIL   = 'info@stroyautsors.ru';
const FROM_EMAIL = 'noreply@stroyautsors.ru'; // доменная почта Яндекс 360 — не ломать, только From-заголовок
const CONSENT_VERSION = '2026-11-19';
const LOG_DIR   = __DIR__ . '/data';

function respond(bool $ok, ?string $error = null): void {
    http_response_code($ok ? 200 : 400);
    echo json_encode(['ok' => $ok, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    respond(false, 'method');
}

$raw = file_get_contents('php://input');
$data = json_decode($raw ?: '', true);
if (!is_array($data)) {
    // fallback: обычная form-urlencoded отправка
    $data = $_POST;
}

// Honeypot: боты заполняют скрытое поле website
if (!empty($data['website'])) {
    respond(true); // молча «принимаем», чтобы не подсказывать
}

// Антиспам по времени: форма отправлена быстрее чем за 2 секунды
if (isset($data['ts'])) {
    $ts = strtotime((string)$data['ts']);
    if ($ts && (time() - $ts) < 2) {
        respond(true);
    }
}

$phone = preg_replace('/\D+/', '', (string)($data['phone'] ?? ''));
if (strlen($phone) === 11 && $phone[0] === '8') $phone = '7' . substr($phone, 1);
if (strlen($phone) === 10) $phone = '7' . $phone;
if (!preg_match('/^7\d{10}$/', $phone)) {
    respond(false, 'phone');
}

// Обязательное согласие: должно быть явно передано и не пустым
if (empty($data['consent'])) {
    respond(false, 'consent');
}

// Поля формы (белый список)
$allowed = ['form_type','customer_type','task','workers','when','name','address','comment','page','consent_version','ts','phone_norm'];
$fields = [];
foreach ($allowed as $k) {
    if (isset($data[$k]) && is_scalar($data[$k])) {
        $fields[$k] = trim(mb_substr((string)$data[$k], 0, 2000));
    }
}
$fields['phone'] = '+7 (' . substr($phone, 1, 3) . ') ' . substr($phone, 4, 3) . '-' . substr($phone, 7, 2) . '-' . substr($phone, 9, 2);
$fields['consent'] = '1';
$fields['consent_version'] = CONSENT_VERSION;

$id = 'lead-' . date('YmdHis') . '-' . bin2hex(random_bytes(3));
$ip  = $_SERVER['REMOTE_ADDR'] ?? '';
$userAgent = mb_substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 300);

// Журнал согласий и заявок (защищённая директория, доступ только локально)
if (!is_dir(LOG_DIR)) { @mkdir(LOG_DIR, 0750, true); }
@file_put_contents(LOG_DIR . '/.htaccess', "Require all denied\nDeny from all\n");
$record = [
    'id' => $id,
    'ts' => gmdate('c'),
    'form_type' => $fields['form_type'] ?? 'lead',
    'page' => $fields['page'] ?? '',
    'fields' => $fields,
    'consent' => ['version' => CONSENT_VERSION, 'checked' => true],
    'ip' => $ip,
    'user_agent' => $userAgent,
];
@file_put_contents(LOG_DIR . '/leads.jsonl', json_encode($record, JSON_UNESCAPED_UNICODE) . "\n", FILE_APPEND | LOCK_EX);

// Письмо на info@stroyautsors.ru
$labels = [
    'form_type' => 'Тип формы', 'customer_type' => 'Тип заказчика', 'task' => 'Что нужно',
    'workers' => 'Сколько рабочих', 'when' => 'Когда нужны', 'name' => 'Имя',
    'address' => 'Адрес/район', 'comment' => 'Комментарий', 'page' => 'Страница',
    'phone' => 'Телефон', 'consent_version' => 'Версия согласия',
];
$body = "Новая заявка со сайта stroyautsors.ru\n\n";
foreach ($labels as $k => $label) {
    if (!empty($fields[$k])) {
        $body .= $label . ': ' . $fields[$k] . "\n";
    }
}
$body .= "\nID заявки: {$id}\nВремя: " . date('d.m.Y H:i') . " МСК\nIP: {$ip}\n";
$body .= "Согласие: отмечено (версия " . CONSENT_VERSION . ")\n";

$subject = '=?UTF-8?B?' . base64_encode('Заявка с сайта: ' . ($fields['phone'])) . '?=';
$headers = implode("\r\n", [
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'From: ' . FROM_EMAIL,
    'Reply-To: ' . $fields['phone'],
    'X-Mailer: PHP/' . phpversion(),
]);

$sent = @mail(TO_EMAIL, $subject, $body, $headers);

// Если почта не ушла — заявка всё равно сохранена в журнале; сообщаем об ошибке
respond((bool)$sent, $sent ? null : 'mail');
