# BOM — Những thứ đã dùng

| Tên | Chi tiết | Ghi chú |
|-----|----------|---------|
| Board | ESP32-S3 DevKit 2022, module ESP32-S3-WROOM-1-N16R8 | Chốt: flash 16 MB + PSRAM 8 MB (Octal SPI). Mã "N26R8" cũ là ghi nhầm, không tồn tại trong tài liệu Espressif |
| Board dự phòng | Thêm 1 board cùng loại | Mỗi tài khoản quan trọng cần 2 key |
| Cáp | USB C-to-C có dây dữ liệu | Không dùng cáp sạc thuần |
| Cáp OTG | Đầu chuyển OTG nếu máy Android kén host | Thử trước khi mua thêm |
| Vỏ | Hộp in 3D chừa nút BOOT và LED | Che mạch trần khi dùng thật |
| Máy build | Windows 11 hoặc Ubuntu | Cài ESP-IDF, Python 3, Git |

## Những thứ phần mềm đã dùng

- Firmware pico-fido bản ESP32-S3 cho tầng dùng thật.
- Arduino IDE hoặc PlatformIO cho sketch hwtest.
- Python 3 và thư viện hidapi cho tool kiểm tra.
- ESP-IDF đúng phiên bản theo yêu cầu của pico-fido.

## Đối chiếu mã module N16R8 (chốt ngày 2026-11-21, NCKH-027 Trần Bình)

- Quy ước mã Espressif: N\<flash MB\>R\<PSRAM MB\> nên N16R8 = flash 16 MB + PSRAM 8 MB. "N26R8" không khớp quy ước (không có flash 26 MB) và không xuất hiện trong bất kỳ tài liệu hay ảnh nào của repo.
- Ảnh `docs/assets/62256.jpg` (chụp đúng loại board này) chú thích module: "ESP32-S3-WROOM-1 N8R2/N8R8/N16R8 module" — dải mã hợp lệ, không có N26R8.
- Tài liệu Espressif `docs/reference/ESP32-S3-DEVKITC-1-N16R8V_Espressif_Systems.pdf`, trang 53, nguyên văn: "ESP32-S3-WROOM-1-N16R8 is a generic Wi-Fi + Bluetooth LE MCU module ... integrated with 16 MB flash and 8 MB PSRAM." Trang 51 cũng ghi "ESP32-S3-WROOM-1 module with 16 MB flash and 8 MB PSRAM".
- Tài liệu `docs/reference/ESP32-S3-N16R8_User_Guide.pdf`: board N16R8 dùng module ESP32-S3-WROOM-1, flash/PSRAM chạy SPI 8-line (Octal), GPIO35/36/37 bận nội bộ cho flash/PSRAM, không dùng ngoài được.
- Kết luận: build pico-fido và mọi cấu hình flash chọn profile 16 MB flash + 8 MB PSRAM (Octal).
- Việc còn lại cho người cầm board thật: đọc chữ in trên nắp shield kim loại để xác nhận vật lý dòng chữ "ESP32-S3-WROOM-1-N16R8" rồi đánh dấu đã kiểm ở đây.

## Kiểm tra khi nhận board

Đọc mã module trên nắp shield và đối chiếu với dòng Board đã chốt ở trên (N16R8: flash 16 MB, PSRAM 8 MB). Xác định cổng USB-C nào là OTG native và cổng nào là UART. Nạp sketch hwtest trước khi flash firmware chính.
