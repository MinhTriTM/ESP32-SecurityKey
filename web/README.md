# Siêu web nạp ESP32-S3

Nạp firmware trực tiếp vào ESP32-S3 từ trình duyệt, không cần cài esptool.

## Cách mở (khuyên dùng)

Windows:

```
powershell -ExecutionPolicy Bypass -File scripts/web_flasher.ps1
```

Linux:

```
bash scripts/web_flasher.sh
```

Script dựng server tại `http://localhost:8000` và tự mở trình duyệt.
Mở qua localhost thì web mới tải được firmware có sẵn trong `web/firmware`.

## Yêu cầu

- Chrome hoặc Edge bản mới trên máy tính (cần WebSerial).
- Mạng ở lần đầu để tải esptool-js từ CDN (unpkg, dự phòng jsdelivr).
- Cáp USB tốt, cắm vào cổng USB-UART của board khi nạp.

## Có gì trong web

1. Kết nối cổng serial, đọc tên chip và MAC.
2. Chọn gói có sẵn (hwtest OTG/HWCDC, có kiểm tra SHA-256) hoặc thêm file `.bin` tự chọn với địa chỉ tùy ý.
3. Nạp, xóa toàn bộ flash, reset board, thanh tiến trình theo từng file.
4. Serial Monitor 115200 để xem log hwtest ngay sau khi nạp.

## Build lại firmware có sẵn

```
$env:PATH = "C:\Windows\System32\WindowsPowerShell\v1.0;$env:PATH"
$env:ARDUINO_DIRECTORIES_DATA = "$PWD\.tooling/data"
.tooling/arduino-cli/arduino-cli.exe compile --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default' --output-dir web/firmware/hwtest-otg firmware/hwtest
.tooling/arduino-cli/arduino-cli.exe compile --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc' --output-dir web/firmware/hwtest-hwcdc firmware/hwtest
python tools/web_firmware.py
```

Lệnh cuối sinh lại `web/firmware/firmware.json` (kích thước + SHA-256).
