# Nghiên cứu 02 — USB trên ESP32-S3 và TinyUSB

## Hai cổng USB của ESP32-S3

ESP32-S3 có USB OTG full-speed 12 Mbps qua GPIO19 (D-) và GPIO20 (D+). Đây là cổng duy nhất chạy được HID FIDO. Ngoài ra chip còn có USB Serial JTAG dùng nạp firmware và log, không dùng cho FIDO.

Trên board DevKit hai cổng này có thể ra hai đầu USB-C vật lý khác nhau. Tài liệu phần cứng đã dặn dùng đúng cổng OTG native. Xem [đúng cổng USB](../03-phan-cung.md).

## TinyUSB

TinyUSB là stack USB nguồn mở cho vi điều khiển, hỗ trợ device class HID, CDC, MSC và nhiều class khác. ESP-IDF tích hợp TinyUSB cho S3. Arduino-ESP32 cũng mở sẵn CDC và HID qua TinyUSB trên S3.

Firmware FIDO hiện hình là composite HID: một interface FIDO (usage page 0xF1D0) và có thể thêm CDC để cấu hình. Hệ điều hành nhận HID generic nên không cần driver.

## Điểm cần nhớ khi build

- Flash đúng target esp32s3, sai target là USB không lên.
- USB CDC và JTAG tranh nhau đường log. Khi debug qua JTAG thì tắt CDC log.
- Chế độ USB mode của Arduino IDE phải để Harware CDC and JTAG hoặc đúng theo hướng dẫn của firmware.
- Cáp phải có dây dữ liệu. Cáp sạc thuần làm mất cả buổi debug vô ích.

## Nguồn chính

- Ghi chú kiến trúc S3 và C3: [ESP32-S3 and C3 Notes](https://sempervent.github.io/best-practices/esp32/esp32-s3-and-c3-architecture-notes/).
- Thực hành HID macro pad trên S3: [ElectricalFlux](https://electricalflux.com/mcu-projects/esp32s3-projects-native-usb-hid-macro-pad).
- So sánh USB các dòng ESP32: [CircuitLabs](https://circuitlabs.net/usb-implementation-in-esp32-series/).
