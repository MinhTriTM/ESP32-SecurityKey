// Cổng quản trị qua WiFi cho key (PA1-G1 theo docs/research/08-web-tren-esp.md).
// Firmware RIÊNG, nạp thay pico-fido khi cần quản trị rồi nạp lại pico để dùng.
// Chức năng G1: phát hotspot + captive portal + trang trạng thái CHỈ ĐỌC.
// KHÔNG xem/sửa credential (nằm trong kho mã hóa của pico, firmware khác
// không đọc được — đúng ranh giới an toàn). Chưa test trên board thật.
//
// Quy tắc an toàn áp dụng: AP có mật khẩu (đổi mỗi key), không chạy cùng
// FIDO bao giờ, tự tắt WiFi sau thời gian không dùng, mọi thao tác ghi log.
#include <DNSServer.h>
#include <WebServer.h>
#include <WiFi.h>
#include <esp_flash_encrypt.h>
#include <esp_secure_boot.h>

// --- Cấu hình (đổi mật khẩu mỗi key, in QR kèm theo key) ---
static const char *AP_PASS = "Doi-Mat-Khau-Moi-Key-07";
static const uint8_t AP_CHANNEL = 6;
static const uint8_t AP_MAX_CLIENT = 2;
static const unsigned long IDLE_OFF_MS = 10UL * 60UL * 1000UL; // 10 phút
static const char *ADMIN_VERSION = "admin-portal G1 (2026-11-23)";

static const IPAddress AP_IP(192, 168, 4, 1);
static DNSServer dnsServer;
static WebServer webServer(80);

// --- Nhật ký kiểm toán trong RAM (vòng tròn, mất khi mất điện) ---
static const int AUDIT_N = 20;
static String auditLog[AUDIT_N];
static int auditHead = 0;
static void audit(const String &msg) {
  char buf[96];
  snprintf(buf, sizeof(buf), "[+%lus] %s", millis() / 1000, msg.c_str());
  auditLog[auditHead] = String(buf);
  auditHead = (auditHead + 1) % AUDIT_N;
}

static String macSuffix() {
  uint64_t mac = ESP.getEfuseMac();
  char buf[8];
  snprintf(buf, sizeof(buf), "%02X%02X%02X", (uint8_t)(mac >> 16),
           (uint8_t)(mac >> 8), (uint8_t)mac);
  return String(buf);
}

static String macFull() {
  uint64_t mac = ESP.getEfuseMac();
  char buf[18];
  snprintf(buf, sizeof(buf), "%02X:%02X:%02X:%02X:%02X:%02X",
           (uint8_t)(mac >> 40), (uint8_t)(mac >> 32), (uint8_t)(mac >> 24),
           (uint8_t)(mac >> 16), (uint8_t)(mac >> 8), (uint8_t)mac);
  return String(buf);
}

static const char *resetName(esp_reset_reason_t r) {
  switch (r) {
  case ESP_RST_POWERON: return "mất điện/cắm lại";
  case ESP_RST_SW: return "phần mềm";
  case ESP_RST_PANIC: return "treo (panic)";
  case ESP_RST_INT_WDT:
  case ESP_RST_TASK_WDT:
  case ESP_RST_WDT: return "watchdog";
  case ESP_RST_DEEPSLEEP: return "ngủ sâu";
  case ESP_RST_BROWNOUT: return "sụt nguồn";
  case ESP_RST_SDIO: return "SDIO";
  default: return "không rõ";
  }
}

static String pageHeader(const String &title) {
  return "<!DOCTYPE html><html lang=vi><head><meta charset=utf-8>"
         "<meta name=viewport content='width=device-width,initial-scale=1'>"
         "<title>" + title + "</title>"
         "<style>body{font-family:sans-serif;margin:1em;max-width:40em}"
         "table{border-collapse:collapse;width:100%}"
         "td{border:1px solid #999;padding:.3em .5em}"
         "td:first-child{font-weight:bold;width:40%}"
         ".ok{color:#0a0}.off{color:#a00}</style></head><body><h2>" + title +
         "</h2>";
}

static void handleRoot() {
  audit("mở trang trạng thái");
  bool sb = esp_secure_boot_enabled();
  bool fe = esp_flash_encryption_enabled();
  String h = pageHeader("Trạng thái key " + macSuffix());
  h += "<table>";
  h += "<tr><td>Phiên bản cổng quản trị</td><td>" + String(ADMIN_VERSION) + "</td></tr>";
  h += "<tr><td>Chip</td><td>" + String(ESP.getChipModel()) + " rev " +
       String(ESP.getChipRevision()) + ", " + String(ESP.getChipCores()) +
       " nhân @" + String(ESP.getCpuFreqMHz()) + " MHz</td></tr>";
  h += "<tr><td>MAC</td><td>" + macFull() + "</td></tr>";
  h += "<tr><td>Flash / PSRAM</td><td>" +
       String((unsigned long)(ESP.getFlashChipSize() / 1048576)) + " MB / " +
       String((unsigned long)(ESP.getPsramSize() / 1048576)) + " MB</td></tr>";
  h += "<tr><td>Secure Boot</td><td class=" + String(sb ? "ok>ĐANG BẬT" : "off>TẮT") + "</td></tr>";
  h += "<tr><td>Mã hóa flash</td><td class=" + String(fe ? "ok>ĐANG BẬT" : "off>TẮT") + "</td></tr>";
  h += "<tr><td>Uptime</td><td>" + String((unsigned long)(millis() / 1000)) + " giây</td></tr>";
  h += "<tr><td>RAM trống</td><td>" + String((unsigned long)esp_get_free_heap_size()) + " byte</td></tr>";
  h += "<tr><td>Lý do khởi động</td><td>" + String(resetName(esp_reset_reason())) + "</td></tr>";
  h += "<tr><td>Máy đang bắt WiFi</td><td>" + String(WiFi.softAPgetStationNum()) + "</td></tr>";
  h += "</table><p><a href=/audit>Kiểm toán</a> · <a href=/health>JSON máy đọc</a></p>";
  h += "<p><small>Cổng quản trị tự tắt WiFi sau 10 phút không ai dùng. "
       "Muốn dùng FIDO thì nạp lại pico-fido.</small></p></body></html>";
  webServer.send(200, "text/html; charset=utf-8", h);
}

static void handleAudit() {
  audit("mở trang kiểm toán");
  String h = pageHeader("Kiểm toán (mất khi mất điện)");
  h += "<ol>";
  for (int i = 0; i < AUDIT_N; i++) {
    int k = (auditHead + i) % AUDIT_N;
    if (auditLog[k].length()) h += "<li>" + auditLog[k] + "</li>";
  }
  h += "</ol><p><a href=/>Về trạng thái</a></p></body></html>";
  webServer.send(200, "text/html; charset=utf-8", h);
}

static void handleHealth() {
  char buf[256];
  snprintf(buf, sizeof(buf),
           "{\"admin\":\"%s\",\"mac\":\"%s\",\"sb\":%s,\"fe\":%s,"
           "\"uptime_s\":%lu,\"heap\":%lu,\"clients\":%u}",
           ADMIN_VERSION, macFull().c_str(),
           esp_secure_boot_enabled() ? "true" : "false",
           esp_flash_encryption_enabled() ? "true" : "false",
           (unsigned long)(millis() / 1000),
           (unsigned long)esp_get_free_heap_size(),
           WiFi.softAPgetStationNum());
  webServer.send(200, "application/json", buf);
}

static void handleCaptive() {
  // Mọi đường lạ đều về trang chính để trình duyệt tự bật portal.
  webServer.sendHeader("Location", "http://192.168.4.1/", true);
  webServer.send(302, "text/plain", "");
}

static unsigned long lastSeen = 0;

void setup() {
  Serial.begin(115200);
  delay(400);
  Serial.println("\n[admin] cổng quản trị G1 khởi động");
  String ssid = "ESP32-Key-" + macSuffix();
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(AP_IP, AP_IP, IPAddress(255, 255, 255, 0));
  bool ok = WiFi.softAP(ssid.c_str(), AP_PASS, AP_CHANNEL, false, AP_MAX_CLIENT);
  Serial.printf("[admin] AP %s: %s @ %s\n", ssid.c_str(),
                ok ? "mở" : "MỞ HỎNG", AP_IP.toString().c_str());
  dnsServer.start(53, "*", AP_IP); // chặn DNS -> captive portal
  webServer.on("/", handleRoot);
  webServer.on("/audit", handleAudit);
  webServer.on("/health", handleHealth);
  webServer.onNotFound(handleCaptive);
  webServer.begin();
  audit("AP mở, cổng quản trị sẵn sàng");
  lastSeen = millis();
  Serial.println("[admin] xong. Bắt WiFi key rồi mở trình duyệt.");
}

void loop() {
  dnsServer.processNextRequest();
  webServer.handleClient();
  if (WiFi.softAPgetStationNum() > 0) lastSeen = millis();
  if (millis() - lastSeen > IDLE_OFF_MS) {
    Serial.println("[admin] hết 10 phút không ai dùng: tắt WiFi.");
    audit("tự tắt WiFi vì hết timeout");
    WiFi.softAPdisconnect(true);
    WiFi.mode(WIFI_OFF);
    for (;;) delay(60000); // dừng hẳn, rút cắm lại để mở tiếp
  }
}
