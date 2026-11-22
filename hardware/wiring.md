# Sơ đồ đấu nối

Board DevKit đã nối sẵn mọi thứ cần thiết. Không cần hàn thêm linh kiện cho bản cơ bản.

## USB OTG native (cổng FIDO)

| Tín hiệu | Chân ESP32-S3 | Ghi chú |
|----------|---------------|---------|
| D- | GPIO19 | Ra đầu USB-C OTG |
| D+ | GPIO20 | Ra đầu USB-C OTG |
| 5V | 5V | Cấp nguồn từ host |
| GND | GND | Mass chung |

## Nút xác nhận

| Tín hiệu | Chân | Ghi chú |
|----------|------|---------|
| BOOT | GPIO0 | Nhấn kéo xuống GND, mạch DevKit có sẵn |

Nhấn giữ BOOT rồi nhấn RST để vào chế độ nạp firmware khi flash lần đầu.

## LED RGB

| Bản board | Chân LED | Ghi chú |
|-----------|----------|---------|
| DevKit v1 | GPIO38 | WS2812 đơn |
| DevKit v2 | GPIO48 | WS2812 đơn |

Sketch hwtest dùng hằng RGB_BUILTIN của Arduino core nên tự khớp đúng chân theo board đã chọn. Nếu LED không sáng thì kiểm tra lại tên board trong menu Tools.

## Cổng UART để flash

| Tín hiệu | Ghi chú |
|----------|---------|
| TX | Ra chip cầu nối USB-UART trên board |
| RX | Ra chip cầu nối USB-UART trên board |

Flash firmware qua cổng UART này. Sau khi flash xong thì chuyển sang cổng OTG native để dùng FIDO.

Về bảo mật, cổng UART là đường nạp code nên sau khi flash bản cuối thì che kín nó trong vỏ key, chỉ chừa cổng OTG. Chi tiết ở [tài liệu bảo mật](../docs/06-bao-mat.md).
