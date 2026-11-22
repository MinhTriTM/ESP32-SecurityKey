# 08 — Web do ESP phát ra (ESP-hosted web UI)

> Ngày: 2026-11-22. Loại: nghiên cứu khả thi, chưa phải quyết định làm.
> Câu hỏi gốc: ngoài web nạp chạy trên PC, ESP32-S3 có thể tự phát ra web
> (bắt WiFi là thấy trang) với những chức năng gì? Có nên làm không?

## 1. Phân biệt hai loại "web"

| # | Loại | Chạy ở đâu | Nói với ESP qua | Hiện trạng |
|---|------|-----------|----------------|-----------|
| A | Web nạp trên PC | Trình duyệt máy tính | USB/WebSerial | Đã có: `web/index.html` |
| B | Web do ESP phát ra | Chính con ESP32-S3 | WiFi (ESP mở AP + web server) | Nghiên cứu trong file này |

Hai loại bổ sung cho nhau, không thay thế nhau. Web loại A nạp firmware qua
cổng USB-UART. Web loại B là trang quản trị/bổ trợ mà ESP tự phục vụ khi bật
WiFi — điện thoại bắt WiFi của key là mở được, không cần cài app.

## 2. Nền tảng kỹ thuật: cái gì khả thi

- ESP32-S3 có WiFi + BLE 5. Board N16R8 (16 MB flash, 8 MB PSRAM) đủ chỗ chứa
  web UI vài trăm KB trên LittleFS cộng TLS mbedTLS.
- Chế độ AP + captive portal: ESP mở điểm phát WiFi, chặn DNS để trình duyệt
  tự bật trang chào — mẫu chuẩn cho trang cấu hình không cần app. Thư viện
  có sẵn: ESP32WiFiManager, IotWebConf.
- Web server trên ESP: ESP-IDF httpd, Arduino WebServer, ESPAsyncWebServer.
  Cập nhật firmware qua web: ElegantOTA / AsyncOTA / AsyncElegantOTA (upload
  file `.bin` trên trang web là flash vào OTA slot).
- HTTPS khả thi về mặt kỹ thuật nhưng chứng chỉ tự ký bị trình duyệt báo đỏ;
  Let's Encrypt không cấp cho IP nội bộ/AP. Thực tế các portal ESP dùng HTTP
  trên mạng AP cô lập + xác thực ở tầng ứng dụng (PIN).
- Giới hạn chuẩn quan trọng nhất: CTAP định nghĩa transport USB, NFC, BLE —
  **không có WiFi** (xem bài so sánh của UMA Technology dưới mục 7). Nghĩa là
  không thể "dùng passkey qua WiFi" theo chuẩn: web trên ESP chỉ làm
  quản trị/bổ trợ, đường FIDO dùng thật vẫn phải là USB.

## 3. Khảo sát: người khác làm gì

- **pico-fido** (firmware ta dùng): toàn bộ tính năng qua USB — CTAP 2.3/U2F,
  OATH/TOTP/HOTP tương thích Yubico Authenticator và YKMAN, Pico Vault
  xuất/nhập credential có xác thực, quản trị bằng PicoKey App qua USB.
  **Không WiFi, không web.** Quản trị từ xa duy nhất của hãng là web nạp
  ESP32 Flasher chạy trên PC — đúng hướng loại A của ta.
- **Key thương mại** (YubiKey, SoloKeys, Nitrokey, OnlyKey): quản trị qua app
  desktop/CLI + USB/NFC. Không hãng nào mở WiFi hay web server trên key.
  Đây là tín hiệu mạnh: ai cũng tránh phơi mặt tấn công radio lên đúng thiết
  bị giữ khóa.
- **Hệ sinh thái web-trên-ESP**: WiFiManager (portal cấu hình WiFi), ESPUI /
  ESP-DASH (dashboard điều khiển), ElegantOTA (OTA qua web). Toàn bộ sinh ra
  cho IoT (đèn, cảm biến, máy in 3D) — lĩnh vực mà tiện ích thắng bảo mật.
  Chưa có tiền lệ "security key phát web".
- **Kết luận khảo sát**: ý tưởng làm được về kỹ thuật nhưng không có tiền lệ
  trong giới key bảo mật. Nếu làm, ta tự chịu trách nhiệm threat model —
  giống kết luận DIY-vs-certified: hàng tự build thì người build chịu trách
  nhiệm cấu hình an toàn, không có chứng nhận nào đỡ lưng.

## 4. Danh sách chức năng khả thi

Cỡ việc: S (dưới 1 giờ–1 ngày) · M (vài ngày–2 tuần) · L (trên 2 tuần).

### Nhóm A — Trạng thái chỉ đọc (rủi ro thấp nhất)

- Xem model, phiên bản firmware, AAGUID, số resident key đã lưu, PIN đã đặt
  chưa, bộ đếm chữ ký, uptime, MAC. Giá trị: kiểm tra key bằng điện thoại
  không cần PC. Cỡ S–M.

### Nhóm B — Xem mã TOTP (giá trị cao nhất)

- Hiện mã TOTP 6 số + vòng đếm 30 giây cho từng account OATH. pico-fido đã
  hỗ trợ OATH qua USB; web chỉ là mặt hiển thị khác, thay app Yubico khi chỉ
  có điện thoại. Rủi ro trung bình: ai bắt được WiFi AP đều thấy mã nên bắt
  buộc PIN + nhấn nút vật lý mới hiện, tự ẩn sau 30–60 giây. Cỡ M.

### Nhóm C — Quản trị credential (khó tích hợp)

- Liệt kê, đổi tên, xóa resident key/passkey. Giá trị cao nhưng pico-fido là
  firmware ngoài: muốn web làm việc này phải fork firmware hoặc viết IPC giữa
  hai firmware — cả hai đều tốn công và đi ngược ranh giới an toàn của
  `docs/02-kien-truc.md` (không tự đụng vào CTAP/crypto). Cỡ L, rủi ro cao.

### Nhóm D — Sao lưu và khôi phục (rủi ro rất cao)

- Tải file Pico Vault đã mã hóa, hiển thị 24 từ khôi phục. Giá trị cao nhưng
  24 từ hiện qua sóng radio là ác mộng: chỉ chấp nhận được trong nghi thức
  khởi tạo có kiểm soát (phòng kín, AP tạm thời, xong là tắt). Cỡ M.

### Nhóm E — Cập nhật firmware OTA qua web (đúng U010)

- Upload `.bin` trên trang web, ESP kiểm tra chữ ký + version chống rollback
  rồi flash vào OTA slot (Secure Boot V2). Giá trị cao vì U015 khóa cổng UART
  xong thì OTA là đường update duy nhất. Sai một dòng là thành cửa hậu. Cỡ L.

### Nhóm F — Tiện ích vận hành

- Cấu hình WiFi STA, đổi mật khẩu AP, xem log hệ thống, self-test phần cứng,
  factory reset an toàn (xóa credential nhưng giữ attestation — đúng U011).
  Cỡ S–M, rủi ro trung bình nếu thiếu PIN/presence.

### Nhóm G — Cấm làm

- Xuất private key/seed dạng thô qua bất kỳ API nào.
- "Passkey qua WiFi": ngoài chuẩn CTAP, trình duyệt và dịch vụ không hỗ trợ.
- WebAuthn trực tiếp với trang của ESP: điện thoại mở web AP của ESP thì
  không có đường USB tới ESP để làm authenticator; trên PC vừa cắm USB vừa mở
  web AP thì được nhưng vô nghĩa.

## 5. Phân tích bảo mật

Mô hình đe dọa hiện tại (`docs/06-bao-mat.md`) giả định kẻ tấn công phải chạm
vật lý vào cổng USB. Bật WiFi là thêm cả chương mới: AP bị dò tìm và dò mật
khẩu, lưu lượng HTTP trong AP bị nghe lén, lỗ hổng httpd, CSRF/XSS lên trang
quản trị, AP giả (evil twin) lừa người dùng, gói deauth ép ngắt kết nối.
Tiền lệ trong repo: U058 đã yêu cầu đánh giá riêng đường Bluetooth khi chuyển
share — WiFi trên key cũng cần đối xử tương tự, ở mức nghiêm hơn vì nó nằm
ngay trên thiết bị giữ khóa.

Nếu làm, tám quy tắc bắt buộc:

1. WiFi TẮT mặc định; chỉ bật bằng hành động vật lý (giữ BOOT 5 giây lúc cấp
   nguồn) vào chế độ quản trị tạm thời, tự tắt sau 5–10 phút không dùng.
2. Không bao giờ chạy FIDO và AP cùng lúc (tránh relay và nhầm lẫn vai trò).
3. Mọi API ghi và API đọc nhạy cảm đều cần PIN + nhấn nút vật lý
   (user presence) + giới hạn lần thử + khóa tạm thời khi sai liên tiếp.
4. Không xuất khóa thô; bản sao lưu luôn mã hóa (AES-GCM, khóa suy từ PIN +
   salt qua PBKDF2 như `tools/vault.py`).
5. AP cô lập client, mật khẩu mạnh sinh ngẫu nhiên cho từng key (in QR kèm
   theo key), cân nhắc ẩn SSID.
6. OTA chỉ nhận firmware ký đúng khóa và version không tụt (U010 + Secure
   Boot V2 + eFuse chống rollback).
7. Tách build: bản "key thuần USB" để dùng thật (không chứa code WiFi) và bản
   "key + web quản trị" gắn nhãn rủi ro rõ ràng.
8. Trang web có mục kiểm toán (lần mở AP gần nhất, thao tác đã làm) và mục
   hiển thị trạng thái Secure Boot / Flash Encryption đọc từ eFuse.

## 6. Ba phương án kiến trúc

- **PA1 — Chế độ quản trị tách biệt (khuyên dùng nếu làm).** Firmware admin
  riêng viết bằng Arduino, chỉ chạy khi giữ BOOT lúc cấp nguồn: AP + captive
  portal + web (trạng thái, xem TOTP, OTA có ký, sao lưu mã hóa, factory
  reset). Hết timeout tự reboot về pico-fido. Hai firmware không bao giờ chạy
  cùng lúc, chuyển đổi luôn cần nút vật lý. Triển khai bằng 2 OTA slot hoặc
  nạp tay từng bản; phân vùng NVS dùng chung phải mã hóa.
- **PA2 — Nhúng web admin vào pico-fido (không khuyến nghị).** Fork firmware
  bảo mật của người khác rồi tự gánh audit crypto/CTAP — đi ngược ranh giới
  an toàn của dự án.
- **PA3 — Không làm web-trên-ESP, mở rộng đường USB.** Nâng web loại A
  (`web/`) và tool `keymgr` (U036): quản trị qua USB bằng CTAP đầy đủ. Lưu ý:
  API WebAuthn của trình duyệt không cho liệt kê/xóa credential tùy ý; muốn
  đủ quyền thì dùng WebHID + tự dựng CTAPHID (đúng hướng `tools/fido_check.py`
  đã đi) hoặc app desktop như PicoKey App.

## 7. Lộ trình gợi ý nếu chốt PA1

- G0: chốt phạm vi + cập nhật threat model `docs/06-bao-mat.md` (đúng U049).
- G1 (S, 1–3 ngày): AP + captive portal + trang trạng thái chỉ đọc.
- G2 (M, 1–2 tuần): + PIN + presence + xem TOTP + giới hạn lần thử.
- G3 (L, 2–4 tuần): + OTA có ký + sao lưu mã hóa + factory reset an toàn.
- Mỗi giai đoạn kèm kiểm thử bảo mật và review theo checklist trước khi gộp.

## 8. Kết luận

Web do ESP phát ra làm được nhiều thứ hay — đáng giá nhất là xem mã TOTP,
OTA có ký và trang trạng thái. Nhưng nó không thể thay đường USB FIDO (ngoài
chuẩn CTAP) và nó mở mặt tấn công WiFi lên đúng thiết bị cần an toàn nhất,
trong khi không hãng key nào dám làm vậy. Khuyến nghị: key dùng thật giữ
đường USB thuần (PA3); chỉ làm PA1 như dự án phụ/nghiên cứu có gắn nhãn rủi
ro. Chờ quyết định trước khi viết code.

## Nguồn

- pico-fido (tính năng, PicoKey App, ESP32 Flasher):
  <https://github.com/polhenarejos/pico-fido>
- PicoKeys ESP32 Flasher: <https://www.picokeys.com/esp32-flasher/>
- ESP32 Security Key vs Certified FIDO2 Key (transport CTAP, DIY tự chịu
  cấu hình, Secure Boot): <https://umatechnology.org/what-an-esp32-security-key-can-and-cant-do-compared-with-a-certified-fido2-key/>
- FIDO2 overview (FIDO Alliance): <https://fidoalliance.org/fido2/>
- ESP32 WiFiManager (captive portal): <https://github.com/Hraph/ESP32WiFiManager>
- AsyncOTA (OTA qua web): <https://github.com/MarikTik/AsyncOTA>
- Hướng dẫn AsyncElegantOTA:
  <https://microcontrollerslab.com/esp32-ota-over-the-air-updates-asyncelegantota-library-arduino/>
- Tài liệu nội bộ: `docs/02-kien-truc.md`, `docs/06-bao-mat.md`,
  `docs/08-100-nang-cap.md` (U010, U011, U036, U049, U058).
