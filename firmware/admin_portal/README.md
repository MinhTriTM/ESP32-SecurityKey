# Cổng quản trị WiFi (admin portal, G1)

Firmware RIÊNG theo phương án PA1 của
[research/08](../../docs/research/08-web-tren-esp.md): phát hotspot +
captive portal + trang trạng thái chỉ đọc. Nạp thay pico-fido khi cần xem,
nạp lại pico-fido để dùng FIDO. Hai firmware không bao giờ chạy cùng lúc.

## Dùng thế nào (khi có board)

1. Nạp gói `admin-portal` từ siêu web nạp (đã có sẵn, kiểm SHA-256).
2. Bắt WiFi `ESP32-Key-XXXXXX` (6 ký tự cuối MAC), mật khẩu xem trong đầu
   file `.ino` (mặc định `Doi-Mat-Khau-Moi-Key-07` — **đổi mỗi key**).
3. Trình duyệt tự bật trang trạng thái (captive portal). Nếu không tự bật,
   mở tay `http://192.168.4.1/`.
4. Xem xong: không cần làm gì — hết 10 phút không ai dùng là key tự tắt
   WiFi. Muốn dùng FIDO thì nạp lại pico-fido.

## Trang có gì

- `/` — model chip, MAC, flash/PSRAM, Secure Boot + mã hóa flash (đọc từ
  eFuse), uptime, RAM trống, lý do khởi động, số máy đang bắt WiFi.
- `/audit` — nhật ký thao tác trong RAM (mất khi mất điện).
- `/health` — JSON gọn cho tool đọc.

## Giới hạn cố ý (đọc trước khi hỏi "sao không xem được key")

- KHÔNG liệt kê/xóa credential, KHÔNG xem TOTP: các bí mật nằm trong kho
  mã hóa của pico-fido, firmware khác không đọc được — đó là bảo mật đúng.
  Muốn quản trị credential thì đi đường USB (mở rộng web PC bằng WebHID +
  CTAP credentialManagement), không đi đường WiFi.
- Chưa test trên board thật (không còn board sống). Biên dịch sạch
  (arduino-cli, core ESP32 4.0.0, DIO + OPI-PSRAM). Test đầu tiên khi có
  board: nạp, bắt WiFi, mở trang, đối chiếu MAC + trạng thái SB/FE.

## Build lại

```
powershell -ExecutionPolicy Bypass -File scripts/build_admin.ps1   # Windows
bash scripts/build_admin.sh                                        # Linux
```

Xong là gói mới vào manifest web nạp + tự kiểm SHA-256.
