# firmware — Firmware tự viết

Chỉ chứa sketch kiểm tra phần cứng. Firmware FIDO dùng thật (pico-fido) là
dự án ngoài, build trong `.tooling/pico-fido` (không commit), xem
[docs/04-firmware.md](../docs/04-firmware.md).

## hwtest

Sketch Arduino kiểm tra board trước khi flash firmware chính: USB CDC, nút
BOOT, LED RGB và HID echo 64 byte (bản OTG). Chi tiết và cách nạp tay trong
[hwtest/README.md](hwtest/README.md).

Build 2 biến thể bằng một lệnh (Windows):

```
$env:PATH = "C:\Windows\System32\WindowsPowerShell\v1.0;$env:PATH"
$env:ARDUINO_DIRECTORIES_DATA = "$PWD\.tooling/data"
.tooling/arduino-cli/arduino-cli.exe compile --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default' --output-dir web/firmware/hwtest-otg firmware/hwtest
.tooling/arduino-cli/arduino-cli.exe compile --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=hwcdc' --output-dir web/firmware/hwtest-hwcdc firmware/hwtest
python tools/web_firmware.py
```

Kết quả đạt: log in đúng chip ESP32-S3, nhấn BOOT thì log hiện nhấn/nhả, LED
xanh lá khi chờ và xanh dương khi nhấn, `hid_echo.py` báo 60 byte khớp.
