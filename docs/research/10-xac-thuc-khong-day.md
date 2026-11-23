# 10 — Xác thực không dây: cắm 1 lần, dùng N lần (BLE / WiFi)

> Ngày: 2026-11-23. Loại: nghiên cứu khả thi, chưa phải quyết định làm.
> Câu hỏi gốc: có cách nào giữ kết nối BLE hoặc hotspot để lần đầu cắm cáp
> ghép đôi, các lần sau chỉ cần cấp nguồn cho ESP là xác thực được, hai đầu
> mã hóa bằng khóa riêng — cắm hay không cắm đều dùng được?

## 1. Yêu cầu (diễn giải)

- Lần đầu: cắm cáp C-to-C laptop/điện thoại ↔ ESP, đồng thời nối BLE và WiFi
  hotspot của ESP → nghi thức ghép đôi/xác thực ban đầu.
- Lần sau: chỉ cấp nguồn cho ESP (sạc dự phòng, ổ điện — không cáp dữ liệu)
  → ESP tự nối lại WiFi/BLE → truyền xác thực tới thiết bị nhận.
- Hai đầu mã hóa kênh bằng khóa riêng (không tin mù vào sóng radio).
- Mục tiêu: cắm hay không cắm đều dùng được, an toàn không thua bản USB.

## 2. Chuẩn FIDO nói gì về không dây

- CTAP2 định nghĩa 3 transport: **USB, NFC, BLE** — và **không có WiFi**.
  Trình duyệt/dịch vụ chỉ nói WebAuthn qua 3 đường đó.
- CTAP-BLE bắt buộc **ghép đôi (pairing) trước khi gọi bất kỳ thao tác FIDO
  nào**; BLE chậm hơn USB (kết nối có thể rớt/nối lại giữa các thao tác).
- ESP32-S3 **không có NFC** → NFC bị loại ngay từ đầu.
- WiFi chỉ làm được kênh **tự định nghĩa** (app companion của ta): TOTP,
  backup mã hóa, OTA, quản trị — không bao giờ thay được WebAuthn trình
  duyệt (đã kết luận ở `research/08-web-tren-esp.md`).
- Cách "không cắm" của ngành cho platform key là **hybrid/caBLE**: điện
  thoại làm passkey cho laptop qua quét QR + kiểm tra gần bằng BLE + relay
  đám mây. Với roaming key tự build thì không tái dùng trực tiếp (cần hạ
  tầng relay + client hỗ trợ), nhưng là mẫu tham khảo cho luồng ghép đôi.

## 3. Tiền lệ: ai đã làm key không dây

- **Feitian** bán key FIDO2 đa giao diện USB-C + NFC + **Bluetooth**
  (MultiPass K32/K33): BLE cho FIDO là chuyện thương mại bình thường, đã có
  hàng certified ngoài chợ.
- **Google Titan BLE (2019)**: Google phải công bố lỗi Bluetooth trên key
  Titan và thay key cho người dùng — bằng chứng BLE mở mặt tấn công thật,
  không phải rủi ro lý thuyết.
- **Zephyr FIDO2** (mã nguồn mở, chạy được trên **ESP32-S3** cho USB):
  mẫu authenticator CTAP2.1 qua USB HID + **BLE tùy chọn** (BLE mới kiểm
  trên board nRF). Hai lưu ý vàng từ tài liệu của họ: (1) client phải ghép
  đôi trước khi dùng FIDO; (2) bản mẫu để ESP phát hiện/ghép đôi suốt, còn
  **bản dùng thật phải giới hạn ghép đôi trong chế độ do người dùng chủ
  động bật** — đúng nguyên tắc ta sẽ áp.
- **OpenSK** (Google, Rust, nRF52840): bản CTAP2.0 từng được FIDO chứng
  nhận, nhưng dự án tự nhận là proof-of-concept/nghiên cứu, không cho dùng
  hàng ngày. Tham khảo kiến trúc, không lấy làm nền sản phẩm.
- **pico-fido** (firmware ta dùng): chỉ USB. Muốn BLE đúng chuẩn thì phải
  đổi firmware (Zephyr/port mới) — hệ quả kiến trúc lớn, xem mục 5.

## 4. Phân tích đe dọa kênh không dây

Mô hình hiện tại (`docs/06-bao-mat.md`) giả định kẻ tấn công phải chạm vật
lý vào USB. Thêm radio là thêm cả chương mới:

- **Relay thời gian thực**: kẻ khuếch đại sóng BLE để điều khiển phiên đăng
  nhập thật từ xa. FIDO chống phishing theo origin nhưng không chống relay.
  Biện pháp: bắt buộc **nhấn nút vật lý mỗi lần ký**, giới hạn thời gian
  phiên, không tin RSSI tuyệt đối.
- **Bắt cóc ghép đôi / BLE giả mạo**: kẻ gần giành ghép đôi trước user hoặc
  dựng thiết bị BLE tên giống key. Biện pháp: chỉ ghép đôi khi **giữ nút
  vật lý** (đúng khuyến nghị Zephyr); lần ghép đầu tiên **qua cáp USB**
  (đúng ý tưởng của đề bài) rồi mới bật radio.
- **Nghe lén/giải mã**: cấm BLE legacy pairing (bẻ được); bắt buộc BLE
  Secure Connections (ECDH) **cộng** mã hóa lớp ứng dụng (AES-GCM, khóa
  phiên từ ECDH + PIN). PIN/seed không bao giờ đi thô trên sóng.
- **WiFi giả mạo (evil twin) + ép rớt mạng (deauth)**: AP của ESP bị nhái
  tên, client bị đá khỏi mạng thật. Biện pháp: AP ẩn + mật khẩu mạnh, hai
  đầu **xác thực lẫn nhau bằng khóa đã ghép** (không tin SSID), mọi API cần
  phiên mã hóa + PIN + presence.
- **Mất cắp key đang phát sóng**: kẻ nhặt được key vẫn bật radio sẽ thử kết
  nối. Biện pháp: radio **TẮT mặc định**, chỉ bật N phút sau khi nhấn nút;
  thao tác nhạy cảm nào cũng cần chạm nút; hết timeout tự ngủ sâu.
- **Quyền riêng tư sóng**: tên BLE/MAC bị theo dõi vị trí. Biện pháp: địa
  chỉ riêng tư quay vòng (RPA), tên chung khi phát hiện, ngừng phát khi
  không ở chế độ ghép.
- **Chạy 24/7 khi cắm điện**: ESP cắm sạc là bề mặt tấn công liên tục.
  Biện pháp: ngủ sâu mặc định, chỉ thức khi có nút nhấn hoặc kết nối từ
  thiết bị **đã ghép**; ghép thiết bị mới và factory reset **chỉ qua USB**.

## 5. Kiến trúc đề xuất: cắm 1 lần, dùng N lần

### G0 — Nghi thức cắm cáp lần đầu (provisioning, làm được ngay)

Cắm C-to-C → tool PC đọc attestation/AAGUID qua CTAP để chắc đúng key →
user đặt PIN → ESP sinh cặp khóa thiết bị (Ed25519/X25519, khóa riêng không
rời chip) + laptop/điện thoại sinh cặp khóa app → **trao khóa CÔNG KHAI qua
USB** (kênh tin cậy vì chạm vật lý) → hai đầu lưu trust store + đặt tên key.
Đây chính là "xác thực ban đầu" của đề bài. Không cần radio, viết bằng
`keymgr` mở rộng là xong.

### G1 — Kênh BLE (đường không dây chính)

Hai phương án, phải chọn một:

- **PA-1 BLE chuẩn (CTAP-BLE đúng spec)**: trình duyệt/dịch vụ dùng key qua
  BLE như key Feitian — tương thích cao nhất. Giá: firmware BLE mới
  (đánh giá Zephyr/OpenSK trên S3 hoặc port), vì pico-fido không có BLE.
  Khó, dài, nhưng là đáp án duy nhất cho "passkey web mà không cắm".
- **PA-2 BLE riêng (GATT tự định nghĩa)**: kênh Noise_XX/X25519+AES-GCM,
  xác thực lẫn nhau bằng khóa đã ghép ở G0 + PIN + nhấn nút mỗi phiên. Nhẹ,
  làm được trên ESP-IDF/Arduino hiện tại — nhưng **chỉ app companion của
  ta dùng được** (xem TOTP, ký phụ, quản trị), trình duyệt không hiểu.

### G2 — Kênh WiFi hotspot (bổ trợ, không phải FIDO)

ESP phát AP (cô lập, an toàn hơn join WiFi nhà) → app companion nối vào →
TLS-PSK/cert từ khóa G0 → việc nặng: backup mã hóa, OTA có ký, xem TOTP
(nối tiếp `research/08` PA1). Lưu ý vật lý: BLE+WiFi chung một radio S3 —
chạy cùng lúc được nhưng chậm/tốn pin, nên mặc định **một thời điểm một
radio**, ưu tiên BLE.

### G3 — Chế độ "chỉ cắm điện" (đúng yêu cầu đề bài)

ESP cắm sạc dự phòng/ổ điện (không cáp dữ liệu) → boot → chỉ phát BLE
riêng tư (RPA) cho thiết bị **đã ghép** → thiết bị nhận thấy key quen →
mở phiên mã hóa → **user chạm nút trên ESP** (hoặc nhập PIN trên app) →
truyền assertion/mã. Không có nút nhấn thì không ký — nhặt được key đang
chạy cũng không dùng từ xa được. Hết timeout tự ngủ sâu.

### Ma trận cắm / không cắm

| Thao tác | USB cắm cáp | BLE đã ghép | WiFi đã ghép |
|----------|-------------|-------------|--------------|
| Passkey web (trình duyệt) | có | có (chỉ PA-1) | không (ngoài chuẩn) |
| Xem mã TOTP (app ta) | có | có (PA-2 + app) | có (app) |
| Backup mã hóa / OTA có ký | có | không (quá chậm) | có |
| Ghép thiết bị mới | có (duy nhất) | không | không |
| Factory reset | có + nút (duy nhất) | không | không |

## 6. Mã hóa khóa riêng (thiết kế kênh, áp cho cả BLE lẫn WiFi)

- Mỗi đầu giữ khóa riêng trong kho an toàn của nền tảng: ESP dùng
  efuse/OTP + flash mã hóa; laptop dùng OS keychain/TPM; điện thoại dùng
  keystore/TEE. Khóa riêng không bao giờ rời thiết bị chủ.
- Bắt tay mỗi phiên: ECDH X25519 (radio BLE thêm lớp Secure Connections) →
  HKDF ra khóa phiên + nonce ngẫu nhiên mỗi chiều → **AES-256-GCM** cho mọi
  bản tin + số thứ tự chống phát lại + timestamp chống thu-ghi-lại.
- Xác thực lẫn nhau: thách-đáp Ed25519 bằng khóa đã ghép ở G0 **trước khi**
  mở phiên; thao tác nhạy cảm cộng thêm PIN (giới hạn lần thử + khóa tạm)
  và nhấn nút vật lý.
- Forward secrecy: xóa khóa phiên sau mỗi phiên; mất/thay thiết bị thì thu
  hồi trust và ghép lại từ G0 qua USB.
- Không tự chế crypto: dùng primitive chuẩn (mbedTLS có sẵn trên ESP-IDF),
  chỉ ráp theo mẫu đã chứng minh (Noise), tuân thủ ranh giới an toàn của
  `docs/02-kien-truc.md`.

## 7. Lộ trình và khuyến nghị

- R0: chốt phạm vi — **khuyến nghị PA-2 (BLE riêng) trước** vì khả thi trên
  nền hiện tại; PA-1 (BLE chuẩn) là dự án firmware mới, chỉ làm khi cần
  tương thích trình duyệt không dây.
- R1 (vài ngày–2 tuần): G0 provisioning qua USB (`keymgr`: sinh keypair,
  trao khóa công khai, trust store). Không cần radio, làm được ngay.
- R2 (2–6 tuần): PA-2 BLE GATT + app companion tối thiểu (CLI desktop trước,
  Android sau) + PIN + presence + RPA + ngủ sâu.
- R3 (2–4 tuần): G2 WiFi AP + TLS-PSK cho backup/OTA (kế thừa research/08).
- R4 (2–3 tháng): PA-1 CTAP-BLE chuẩn (đánh giá Zephyr/OpenSK trên S3).
- Mỗi giai đoạn cập nhật threat model `docs/06-bao-mat.md` và kiểm thử bảo
  mật trước khi gộp; radio luôn TẮT mặc định, bật bằng nút vật lý, tự tắt;
  key dùng thật giữ song song bản USB thuần.

## 8. Kết luận

Ý tưởng "cắm 1 lần, dùng N lần" khả thi và khớp đúng thực tiễn ngành: ghép
đôi có chạm vật lý lần đầu (USB + nút nhấn), các lần sau dùng BLE đã ghép
với mã hóa khóa riêng + xác nhận chạm nút mỗi phiên. WiFi chỉ nên làm kênh
bổ trợ cho app riêng, không bao giờ là đường FIDO. Giới hạn lớn nhất: muốn
trình duyệt hiểu key qua BLE thì phải đổi firmware (pico-fido không có BLE).
Câu hỏi chốt trước khi viết code: **PA-1 (BLE chuẩn, tương thích trình
duyệt, dự án lớn) hay PA-2 (BLE riêng cho app ta, khả thi nhanh)?**

## Nguồn

- CTAP spec (transports USB/NFC/BLE, pairing):
  <https://fidoalliance.org/specs/fido-v2.3-ps-20260226/fido-client-to-authenticator-protocol-v2.3-ps-20260226.html>
- Zephyr FIDO2 (BLE tùy chọn, phải ghép đôi trước, production giới hạn
  pairing mode, chạy được ESP32-S3 cho USB):
  <https://docs.zephyrproject.org/latest/samples/subsys/authentication/fido2/README.html>
- FIDO2 protocol stack (WebAuthn + CTAP2/CBOR qua USB/NFC/BLE):
  <https://www.anvilsecure.com/blog/demystifying-passkeys-under-the-hood-the-protocol.html>
- Feitian key FIDO2 USB-C + NFC + Bluetooth (tiền lệ thương mại):
  <https://ftsafe.us/products/feitian-allinpass-fido2-fido-u2f-nfc-ble-usb-biometric-fingerprint-security-key-k33>
- Google Titan BLE advisory 2019 (tiền lệ rủi ro BLE):
  <https://security.googleblog.com/2019/05/titan-keys-update.html>
- OpenSK (CTAP2.0 từng certified, tự nhận là nghiên cứu/POC):
  <https://github.com/google/OpenSK>
- Tài liệu nội bộ: `docs/02-kien-truc.md`, `docs/06-bao-mat.md`,
  `docs/08-100-nang-cap.md` (U058), `docs/research/08-web-tren-esp.md`.
