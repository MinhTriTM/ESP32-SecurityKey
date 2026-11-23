# 02 — Kiến trúc

## Tổng quan luồng

Trình duyệt gọi WebAuthn. Hệ điều hành chuyển request thành message CTAPHID qua USB. Firmware trên ESP32-S3 xử lý, chờ người dùng chạm nút xác nhận rồi ký và trả về. Private key không bao giờ rời khỏi chip.

Luồng tóm tắt:

Browser (WebAuthn) → OS (CTAPHID/USB HID) → ESP32-S3 (pico-fido) → nút xác nhận → ký → trả về

Sơ đồ chi tiết từng bước (đóng góp bởi Đỗ An, NCKH-011):

```
Browser (WebAuthn API)       OS (CTAPHID / USB HID)            ESP32-S3 (pico-fido)                 Nguoi dung
        |                               |                               |                               |
        |  1. navigator.credentials     |                               |                               |
        |     .get() / .create()        |                               |                               |
        | ----------------------------> |                               |                               |
        |                               |  2. CTAPHID_INIT / MSG /      |                               |
        |                               |     CBOR qua USB HID report   |                               |
        |                               | ----------------------------> |                               |
        |                               |                               | 3. Parse CTAPHID, xu ly       |
        |                               |                               |    CTAP2 / U2F                |
        |                               |                               | 4. LED bao cho, doi cham      |
        |                               |                               |    nut BOOT (User Presence)   |
        |                               |                               |    (doi nguoi dung cham nut)  |
        |                               |                               | ----------------------------> |
        |                               |                               | <---------------------------- |
        |                               |                               | 5. Ky bang private key trong  |
        |                               |                               |    flash (key khong bao gio   |
        |                               |                               |    roi khoi chip)             |
        |                               |  6. HID report (response)     |                               |
        |                               | <---------------------------- |                               |
        |  7. assertion / credential    |                               |                               |
        | <---------------------------- |                               |                               |
```

Giải thích các bước:

1. Ứng dụng web gọi `navigator.credentials.get()` (xác thực) hoặc `.create()` (đăng ký) qua API WebAuthn của trình duyệt.
2. Hệ điều hành (WebAuthn client + driver HID) gói request thành message CTAPHID (INIT/MSG/CBOR) gửi qua USB HID report.
3. Firmware pico-fido trên ESP32-S3 parse CTAPHID, xử lý theo CTAP2/U2F.
4. LED báo chờ; firmware đợi người dùng chạm nút BOOT (kiểm tra User Presence).
5. Sau khi chạm nút, chip ký bằng private key lưu trong flash nội — key không bao giờ rời khỏi chip.
6. Response được gói thành HID report gửi ngược về hệ điều hành.
7. Trình duyệt nhận assertion/credential và trả cho ứng dụng web.

## Thành phần

- Phần cứng: ESP32-S3 DevKit với cổng USB-C native (cổng USB_OTG, không phải cổng UART). Nút BOOT làm nút xác nhận chạm. LED RGB báo trạng thái.
- Firmware chính: pico-fido bản ESP32-S3. Nhận USB HID, xử lý U2F và CTAP2, lưu credential vào flash.
- Sketch hwtest: firmware Arduino tối giản để kiểm tra USB CDC, nút và LED trước khi flash firmware chính.
- Tool kiểm tra: script Python gửi CTAPHID_INIT và CTAPHID_PING để xác nhận key trả lời đúng.
- Quy tắc hệ thống: file udev rules cho Linux để trình duyệt được quyền mở thiết bị HID.

## Vì sao cắm C-to-C là chạy

Key hiện hình là USB HID chuẩn với usage page FIDO. Windows 11, Linux và Android đều có driver HID generic. Chrome và Edge đều có WebAuthn. Không có tầng driver hay app độc quyền nào ở giữa.

Trên Android cần cáp OTG đúng chuẩn hoặc cổng C hỗ trợ host. Hầu hết máy Android mới đều đủ điều kiện.

## Lưu trữ key

Credential và vật liệu khóa nằm trong flash nội của ESP32-S3. Bật Secure Boot V2 khi build bản dùng thật (KHÔNG bật Flash Encryption — pico-fido v8.2 hỏng kho khi bật FE, xem [04-firmware](04-firmware.md)). Mỗi key vật lý là một bản sao duy nhất nên phải đăng ký ít nhất hai key cho mỗi tài khoản quan trọng.

## Ranh giới an toàn

Repo này không tự viết thuật toán chữ ký hay giao thức CTAP. Mọi xử lý crypto nằm trong firmware pico-fido và thư viện mbedTLS của nó. Code tự viết chỉ làm kiểm tra phần cứng và kiểm tra giao tiếp, không chạm vào private key.
