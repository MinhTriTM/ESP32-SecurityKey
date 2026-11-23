// Sketch kiểm tra phần cứng cho ESP32-S3 Security Key.
// Mục đích: xác nhận USB CDC, nút BOOT và LED RGB trước khi flash firmware FIDO.
// Board: ESP32-S3 DevKit. Bật "USB CDC On Boot: Enabled" trong menu Tools.
// Build: Arduino IDE, PlatformIO hoặc arduino-cli với core ESP32 (xem README).

#include <Arduino.h>

// Kiểm tra sau include vì macro CONFIG_* chỉ có khi sdkconfig đã nạp.
#ifndef CONFIG_IDF_TARGET_ESP32S3
#error "Sketch này chỉ dành cho ESP32-S3, kiểm tra lại board đang chọn."
#endif

#if defined(ARDUINO_USB_MODE) && ARDUINO_USB_MODE == 0
#include "USB.h"
#include "USBHID.h"
USBHID HID;

// HID echo kiểm tra đường USB mà FIDO sẽ dùng: vendor page 0xFF00,
// 64 byte IN/OUT, KHÔNG report ID (giống CTAP HID). Lý do: bộ đệm endpoint
// IN của TinyUSB chỉ 64 byte, thêm ID thành 65 là SendReport thất bại ngay.
// Tool tools/hid_echo.py gửi rồi đối chiếu từng byte.
static const uint8_t echo_report_descriptor[] = {
  0x06, 0x00, 0xFF,  // Usage Page (Vendor 0xFF00)
  0x09, 0x01,        // Usage (0x01)
  0xA1, 0x01,        // Collection (Application)
  0x09, 0x02,        //   Usage (IN)
  0x15, 0x00,        //   Logical Minimum (0)
  0x26, 0xFF, 0x00,  //   Logical Maximum (255)
  0x75, 0x08,        //   Report Size (8)
  0x95, 0x40,        //   Report Count (64)
  0x81, 0x02,        //   Input (Data,Var,Abs)
  0x09, 0x03,        //   Usage (OUT)
  0x15, 0x00,        //   Logical Minimum (0)
  0x26, 0xFF, 0x00,  //   Logical Maximum (255)
  0x75, 0x08,        //   Report Size (8)
  0x95, 0x40,        //   Report Count (64)
  0x91, 0x02,        //   Output (Data,Var,Abs)
  0xC0               // End Collection
};

static uint8_t echoBuf[64];
static volatile bool echoPending = false;
static portMUX_TYPE echoMux = portMUX_INITIALIZER_UNLOCKED;

class EchoHIDDevice : public USBHIDDevice {
public:
  EchoHIDDevice() {
    static bool initialized = false;
    if (!initialized) {
      initialized = true;
      HID.addDevice(this, sizeof(echo_report_descriptor));
    }
  }
  void begin() { HID.begin(); }
  uint16_t _onGetDescriptor(uint8_t *buffer) override {
    memcpy(buffer, echo_report_descriptor, sizeof(echo_report_descriptor));
    return sizeof(echo_report_descriptor);
  }
  // Chạy trong ngữ cảnh USB: chỉ chép dữ liệu dưới khóa ngắn để khỏi đua
  // với loop(), việc gửi lại do loop() làm.
  void _onOutput(uint8_t report_id, const uint8_t *buffer, uint16_t len) override {
    (void)report_id;
    uint16_t n = len > sizeof(echoBuf) ? sizeof(echoBuf) : len;
    portENTER_CRITICAL(&echoMux);
    memcpy(echoBuf, buffer, n);
    if (n < sizeof(echoBuf)) {
      memset(echoBuf + n, 0, sizeof(echoBuf) - n);
    }
    echoPending = true;
    portEXIT_CRITICAL(&echoMux);
  }
};

static EchoHIDDevice echoDev;
#endif

#ifndef BOOT_PIN
#define BOOT_PIN 0  // Nút BOOT trên DevKit nối GPIO0, nhấn là mức thấp.
#endif

// In mọi log ra cả USB Serial và UART0 (CH343/COM10) cùng lúc: nếu USB
// chập chờn vẫn đọc được log qua UART. Mọi Serial.* dưới đây đi qua both
// (Serial0 là token khác nên không bị macro chạm tới).
class TeePrint : public Print {
public:
  void begin(unsigned long baud) { Serial.begin(baud); Serial0.begin(baud); }
  operator bool() { return (bool)Serial; }
  size_t write(uint8_t b) override {
    Serial.write(b);
    Serial0.write(b);
    return 1;
  }
};
static TeePrint both;
#define Serial both

static bool lastPressed = false;  // Bản chất là trạng thái "đang nhấn", khởi đầu là thả.
static unsigned long lastPrint = 0;

void printMac() {
  // MAC gốc trong efuse, duy nhất mỗi chip. Chỉ để định danh, KHÔNG phải bí mật.
  uint64_t mac = ESP.getEfuseMac();
  // getEfuseMac gói little-endian: in từ byte thấp lên cao mới khớp thứ tự
  // của esptool và nhãn module (đã đối chiếu: 28:84:85:86:92:74).
  Serial.printf("MAC: %02X:%02X:%02X:%02X:%02X:%02X\n",
                (uint8_t)mac, (uint8_t)(mac >> 8), (uint8_t)(mac >> 16),
                (uint8_t)(mac >> 24), (uint8_t)(mac >> 32), (uint8_t)(mac >> 40));
}

void printChipInfo() {
  Serial.println("=== ESP32-S3 Security Key: hwtest ===");
  Serial.printf("Chip: %s rev %d\n", ESP.getChipModel(), ESP.getChipRevision());
  printMac();
  Serial.printf("CPU: %d MHz, cores: %d\n", ESP.getCpuFreqMHz(), ESP.getChipCores());
  Serial.printf("Flash: %d bytes\n", ESP.getFlashChipSize());
  Serial.printf("PSRAM: %d bytes\n", ESP.getPsramSize());
  Serial.printf("SDK: %s\n", ESP.getSdkVersion());
#ifdef ARDUINO_USB_MODE
  Serial.printf("USB mode: %d (0 la OTG co HID echo, 1 la HWCDC)\n", ARDUINO_USB_MODE);
#endif
  Serial.println("Nhan nut BOOT de test. LED RGB se doi mau.");
  Serial.println("======================================");
}

void setLed(uint8_t r, uint8_t g, uint8_t b) {
#if defined(RGB_BUILTIN)
  neopixelWrite(RGB_BUILTIN, r, g, b);
#elif defined(LED_BUILTIN)
  digitalWrite(LED_BUILTIN, (r || g || b) ? HIGH : LOW);
#else
  (void)r; (void)g; (void)b;
#endif
}

void setup() {
  pinMode(BOOT_PIN, INPUT_PULLUP);
#if defined(LED_BUILTIN) && !defined(RGB_BUILTIN)
  pinMode(LED_BUILTIN, OUTPUT);
#endif

  Serial.begin(115200);
  unsigned long start = millis();
  while (!Serial && millis() - start < 3000) {
    delay(10);
  }
  printChipInfo();
#if defined(ARDUINO_USB_MODE) && ARDUINO_USB_MODE == 0
  echoDev.begin();
  USB.begin();
  Serial.println("HID echo: san sang (vendor page 0xFF00, 64 byte, khong report ID).");
#else
  Serial.println("HID echo: TAT (can USB Mode = USB-OTG).");
#endif
  setLed(0, 32, 0);  // Xanh lá: sẵn sàng.
}

void loop() {
  bool pressed = digitalRead(BOOT_PIN) == LOW;
  if (pressed && !lastPressed) {
    Serial.println("BOOT: nhan");
    setLed(0, 0, 64);  // Xanh dương khi nhấn.
  } else if (!pressed && lastPressed) {
    Serial.println("BOOT: nha");
    setLed(0, 32, 0);
  }
  lastPressed = pressed;

  if (millis() - lastPrint > 5000) {
    lastPrint = millis();
    Serial.printf("Heartbeat: uptime %lu s, heap %d\n",
                  millis() / 1000, ESP.getFreeHeap());
  }
#if defined(ARDUINO_USB_MODE) && ARDUINO_USB_MODE == 0
  if (echoPending && HID.ready()) {
    uint8_t guiDi[64];
    portENTER_CRITICAL(&echoMux);
    memcpy(guiDi, echoBuf, sizeof(guiDi));
    echoPending = false;
    portEXIT_CRITICAL(&echoMux);
    if (HID.SendReport(0, guiDi, sizeof(guiDi))) {
      Serial.println("HID echo: da gui lai 64 byte.");
    } else {
      Serial.println("HID echo: gui that bai, goi tin nay bi bo (ban test se bao mismatch).");
    }
  }
#endif
  delay(20);
}
