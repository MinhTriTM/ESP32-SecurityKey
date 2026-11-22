# 01 — Phân tích ý tưởng

## Ý tưởng gốc

Tạo security key bằng ESP32-S3 DevKit 2022 cho Android, Linux, Ubuntu và Windows 11. Chỉ cần cắm cáp USB C-to-C là kết nối được tất cả.

## Vì sao ý tưởng khả thi

ESP32-S3 có USB OTG native full-speed 12 Mbps với chân D- ở GPIO19 và D+ ở GPIO20. Chip này chạy được stack TinyUSB nên giả lập thiết bị USB HID chuẩn. FIDO sống trên USB HID nên trình duyệt và hệ điều hành nhận key mà không cần driver riêng.

Điểm này khác ESP32 đời cũ không có USB native. S3 sinh ra đã hợp làm USB gadget.

## Vì sao chọn FIDO2 + U2F

FIDO là chuẩn mở của FIDO Alliance cho đăng nhập không mật khẩu. U2F (CTAP1) làm bước xác thực thứ hai. FIDO2 (CTAP2 + WebAuthn) làm passkey và đăng nhập chính.

Cả bốn nền tảng mục tiêu đều hỗ trợ WebAuthn qua Chrome hoặc Edge. Một key chuẩn FIDO cắm vào là dùng được ngay cho Google, GitHub, Microsoft và nhiều dịch vụ khác. Không cần app riêng trên Android.

## Phạm vi đã chốt

- Hỗ trợ FIDO2 và U2F trong một firmware.
- Mục tiêu dùng thật, không phải demo học tập.
- Firmware chính dùng pico-fido bản ESP32-S3 đã kiểm chứng.
- Repo này viết thêm sketch kiểm tra phần cứng, tool kiểm tra và toàn bộ tài liệu.

## Rủi ro chính

Tự viết crypto và CTAP2 từ đầu dễ sai và không ai audit. Cách giảm rủi ro là dùng firmware đã kiểm chứng, ghim đúng phiên bản, kiểm tra hash khi tải và giữ hai key dự phòng.

ESP32-S3 không có secure element chuyên dụng như YubiKey. Mức an toàn đạt ngưỡng dùng cá nhân nghiêm túc, chưa tương đương key thương mại đạt chứng nhận FIDO.

## Kết luận

Ý tưởng đúng hướng và làm được với chi phí thấp. Kiến thức chi tiết nằm ở [tài liệu kiến trúc](02-kien-truc.md).
