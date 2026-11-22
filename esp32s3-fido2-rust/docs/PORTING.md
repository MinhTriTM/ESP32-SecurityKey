# PORTING — Ánh xạ opensk sang ESP32-S3

Tài liệu port lõi `opensk 0.1.0` lên board ESP32-S3 DevKit (module N16R8:
flash 16MB + PSRAM 8MB). Mọi mục đều ghi rõ nguồn tra cứu để người port
kiểm tra lại, vì firmware mẫu trong `firmware/s3-fido` chưa từng biên dịch.

## 1. Nguồn đã tra

- `docs.rs/opensk` (crate `opensk 0.1.0`): trait `env::Env` với 10 kiểu
  liên kết (`Rng`, `UserPresence`, `Persist`, `KeyStore`, `Write`,
  `Customization`, `HidConnection`, `Clock`, `Crypto`, `Fingerprint`) và
  các hàm `rng()`, `user_presence()`, `persist()`, `key_store()`,
  `clock()`, `fingerprint()`, `write()`, `customization()`,
  `hid_connection()`, `boots_after_soft_reset()`, cộng `firmware_version()`
  và `process_vendor_command()` có sẵn bản mặc định.
- Mã nguồn `google/OpenSK` (nhánh master, thư mục `libraries/opensk/src`):
  chi tiết từng trait con trong `api/` (`rng.rs`, `user_presence.rs`,
  `persist.rs`, `key_store.rs`, `connection.rs`, `clock.rs`,
  `customization.rs`, `crypto/mod.rs`, `fingerprint.rs`) và `env/mod.rs`.
- `crates.io/api`: `esp-hal` bản mới nhất 1.2.2 (có feature chip `esp32s3`
  và đường USB OTG qua `embassy-usb-driver` + `embassy-usb-synopsys-otg`),
  `esp-storage` 0.10.0 (feature `esp32s3`, cần `esp-hal/unstable`),
  `esp-println` 0.18.0, `esp-backtrace` 0.20.0.
- Phần cứng repo mẹ: `hardware/wiring.md` (OTG GPIO19/20, BOOT GPIO0,
  WS2812 GPIO38/48), `firmware/hwtest` (log chip, nút BOOT, HID echo),
  `tools/fido_check.py` (framing CTAPHID/CBOR phía host mà key phải nói đúng).

## 2. Bảng ánh xạ tổng quan

| # | Thành viên `Env` | opensk cần gì | Dự kiến trên ESP32-S3 | Độ khó |
|---|------------------|---------------|------------------------|--------|
| 1 | `Rng` | `rand_core::{CryptoRng, Rng}` + `gen_uniform_u8x32` | `esp_hal::rng::Rng` (RNG phần cứng) | Dễ |
| 2 | `Write` | `core::fmt::Write` (log debug) | `esp-println` qua USB-Serial-JTAG | Dễ |
| 3 | `Clock` | `Timer: Default` (mặc định = đã hết hạn), `make_timer(ms)`, `is_elapsed` | TimerGroup (`timg`) của esp-hal | Dễ |
| 4 | `Customization` | ~20 hằng cấu hình + bất biến | Struct hằng của ta, copy `DEFAULT_CUSTOMIZATION` rồi chỉnh | Dễ |
| 5 | `UserPresence` | `check_init`, `wait_with_timeout`, `check_complete` | Nút BOOT GPIO0 (`Input` + pull-up) + LED WS2812 báo hiệu | Trung bình |
| 6 | `Persist` | `find`/`insert`/`remove`/`iter` (key 0..4096, value ≤ 1023 byte) | `esp-storage` + lớp key-value (cần wear-leveling) | Trung bình |
| 7 | `KeyStore` | bọc/mở credential 241 byte, PIN, CredRandom | Dùng `Helper` có sẵn của opensk nếu được, hoặc tự cài | Trung bình |
| 8 | `Crypto` | AES-256, ECDH, ECDSA, SHA-256, HMAC-256, HKDF-256 (+ Ed25519 tùy chọn) | `software_crypto` của opensk trước, dần thay bằng tăng tốc phần cứng | Trung bình |
| 9 | `Fingerprint` | đăng ký/chụp/kiểm tra vân tay | Board KHÔNG có cảm biến → tắt feature `fingerprint` | Không làm |
| 10 | `HidConnection` | `send`/`recv` gói 64 byte, endpoint `MainHid` | USB OTG + stack HID (embassy-usb hoặc tự viết) | KHÓ NHẤT |

Ngoài ra còn 2 hàm của `Env`: `boots_after_soft_reset()` (đọc lý do
reset từ RTC) và `firmware_version()` (trả bản firmware cho GetInfo).

## 3. Chi tiết từng thành viên

### 3.1. Rng — sinh số ngẫu nhiên

- opensk định nghĩa lại từ `rand_core`: kiểu cài đặt phải là
  `CryptoRng + Rng`, có sẵn hàm tiện ích `gen_uniform_u8x32()`.
- Port: bọc `esp_hal::rng::Rng` (RNG phần cứng của S3) và cài đặt
  `rand_core::RngCore` + `CryptoRng` cho nó.
- Chú ý: kiểm tra bản `rand_core` mà `opensk 0.1` re-export trong
  `api::rng` để khai báo đúng bản trong `Cargo.toml`, tránh lệch minor.

### 3.2. Write — log debug

- opensk chỉ cần `core::fmt::Write`; hàm `Env::write()` trả về giá trị
  (không phải tham chiếu) để `drop` có thể flush.
- Port: bọc `esp_println::Printer` qua cổng USB-Serial-JTAG. Log này
  khác cổng OTG chạy FIDO nên không ảnh hưởng giao thức.
- Cấm in bí mật (master key, PIN hash) ra log ở bản release.

### 3.3. Clock — đồng hồ và hẹn giờ

- opensk cần kiểu `Timer: Default` trong đó timer mặc định phải coi như
  đã hết hạn, `make_timer(ms)` tạo hẹn giờ, `is_elapsed` kiểm tra
  (một khi đã hết hạn thì mãi mãi hết hạn).
- Port: dùng TimerGroup của esp-hal, lưu deadline theo mili-giây từ boot.
- Feature `debug_ctap` còn cần `timestamp_us()` — chỉ bật khi debug.

### 3.4. Customization — cấu hình hãng

- opensk liệt kê ~20 núm: cho phép PIN protocol v1 không, `credProtect`
  mặc định, độ dài PIN tối thiểu (4..63), có ép `alwaysUv` không,
  `max_msg_size` (1024..7609), số lần sai PIN tối đa (≤ 8),
  bật attestation lô hay không, có dùng bộ đếm ký không, số resident key...
  File mẫu đã điền giá trị khởi đầu an toàn: PIN tối thiểu 6,
  `max_msg_size` 1024, tắt attestation lô/doanh nghiệp, bật bộ đếm ký.
- Port: chạy `is_valid()` của opensk (feature `std`, trên host) để
  kiểm tra bất biến trước khi flash. Hai luật dễ vi phạm nhất:
  attestation lô và attestation doanh nghiệp không được bật cùng lúc,
  và số resident key phải khớp công thức hao mòn flash
  `I = (P*4084 - 5107 - K*S)/8 * C` (ghi trong docs của opensk).

### 3.5. UserPresence — nút BOOT + LED

- opensk gọi theo trình tự `check_init` → `wait_with_timeout` (có thể
  nhiều lần) → `check_complete`. Hàm chờ nhận thêm bộ đệm gói 64 byte
  để vừa chờ người dùng vừa nhận gói USB (không được làm kẹt kênh),
  trả `Approved` / `Declined` / `Timeout` hoặc `Canceled`.
- Port: đọc GPIO0 qua `esp_hal::gpio::Input` với pull-up nội
  (nhấn = mức thấp, khớp `hwtest.ino`). LED WS2812 (GPIO38 hoặc GPIO48
  tùy bản DevKit) đổi màu báo trạng thái: xanh lá chờ, xanh dương khi
  nhấn — giữ đúng quy ước màu của `hwtest` để người dùng quen.
  Điều khiển WS2812 cần xung đơn dây chính xác, dự kiến dùng RMT của S3.
- Chú ý chống dội phím (debounce) cho nút BOOT trong `wait_with_timeout`.

### 3.6. Persist — lưu trữ bền vững

- opensk chỉ bắt 4 hàm key-value (`find`, `insert`, `remove`, `iter`);
  mọi thứ khác (credential, bộ đếm ký toàn cục, PIN hash, large blob,
  chính sách PIN...) đã có bản mặc định xây trên 4 hàm đó. Giả định:
  key 0..4096, value tối đa 1023 byte.
- Port: đọc/ghi flash trong qua `esp-storage 0.10` (feature `esp32s3`).
  Việc khó là flash NOR chỉ xóa theo sector và chịu số lần xóa hữu hạn,
  trong khi bộ đếm ký tăng mỗi lần xác thực. BẮT BUỘC có wear-leveling
  (luân chuyển vùng ghi) cho bộ đếm, nếu không key chết sớm hoặc kẹt.
  Tham khảo cách OpenSK bản C lưu store (trang 4KB, ghi nối tiếp).
- Vùng flash cho FIDO phải tách khỏi vùng OTA/firmware, và nên bật
  mã hóa flash của S3 khi làm bản cuối (xem rủi ro ở mục 4).

### 3.7. KeyStore — kho khóa

- opensk cần: `init`, `wrap_credential` / `unwrap_credential`
  (credential ID dài đúng 241 byte: 1 byte bản + 16 byte IV + 192 byte
  mã hóa + 32 byte HMAC), `cred_random`, `has_pin`,
  `verify_pin_hash` (so sánh hằng thời gian), `store_pin`, `reset`.
- Tin vui: opensk có trait `Helper` cài đặt sẵn toàn bộ `KeyStore`
  cho mọi `Env` (dùng `rng()` + `persist()` của chính môi trường đó).
  Port nên dùng `Helper` trước, chỉ tự cài khi cần nhét master key
  vào efuse hoặc tối ưu riêng.

### 3.8. Crypto — thuật toán mật mã

- opensk cần 6 họ: AES-256, ECDH (P-256), ECDSA (P-256), SHA-256,
  HMAC-256, HKDF-256; tùy chọn Ed25519 (feature `ed25519`).
- Đường ngắn nhất: bật feature `software_crypto` của opensk, dùng các
  kiểu `Software*` có sẵn (dựng trên RustCrypto: `p256`, `sha2`, `hmac`,
  `hkdf`, `aes`, `cbc`). Chạy được ngay, không phụ thuộc driver.
- Đường tối ưu sau: thay từng họ bằng tăng tốc phần cứng của S3 qua
  esp-hal (theo mô tả nhiệm vụ, esp-hal 1.2 có AES/SHA/RSA/ECC —
  CẦN đối chiếu lại docs vì người viết chưa kiểm chứng trực tiếp).
  Ưu tiên thay SHA/AES trước (dùng nhiều nhất cho HMAC và bọc credential).
- Dù chọn đường nào cũng phải chạy test vector của opensk
  (`api::crypto::test`) trên host trước khi tin.

### 3.9. Fingerprint — vân tay (không làm)

- Board đích không có cảm biến vân tay. Port sẽ tắt feature
  `fingerprint` của opensk; struct `S3Fingerprint` trong file mẫu chỉ là
  stub để giữ chỗ, mọi hàm báo chưa hỗ trợ.

### 3.10. HidConnection — USB HID (RỦI RO LỚN NHẤT)

- opensk cần đúng 2 hàm trên gói 64 byte: `send(buf, endpoint)` và
  `recv(buf, timeout) -> RecvStatus::{Timeout, Received(endpoint)}`,
  endpoint chính là `MainHid = 1` (endpoint 2 chỉ khi bật `vendor_hid`).
- Phía host, `tools/fido_check.py` kiểm tra đúng 3 tầng: INIT (cấp CID),
  PING ngắn + PING dài 100 byte (gói nối tiếp), và CTAP2 GetInfo qua CBOR.
  Key phải đóng gói đúng từng byte: gói mở đầu 7 byte header
  (CID 4 + CMD|0x80 + độ dài 2), gói nối (CID 4 + seq + 59 byte),
  report ID 0 ở đầu mỗi report HID 64 byte.
- Phần cứng S3 có USB OTG native (GPIO19/20), và `esp-hal 1.2` có đường
  OTG qua `embassy-usb-driver` + `embassy-usb-synopsys-otg`. Nhưng hiện
  mô tả thiết bị (descriptor) FIDO chuẩn — usage page `0xF1D0`, report
  64 byte IN/OUT — chưa có sẵn, phải tự viết theo đặc tả CTAPHID.
  (Lưu ý: `hwtest.ino` dùng usage page vendor `0xFF00` để echo test,
  KHÁC với `0xF1D0` của FIDO — không được copy nguyên descriptor đó.)
- Đây là việc khó nhất của cả port: sai một byte descriptor hoặc thứ tự
  gói là host không nhận key. Nên làm HID echo FIDO (`PING` trả đúng
  payload như `FakeDevice` trong `fido_check.py`) trước khi cắm opensk vào.

## 4. Rủi ro lớn

1. **Stack USB HID chưa có.** esp-hal cho vay driver OTG thô, nhưng tầng
   HID + CTAPHID (ghép/cắt gói, quản CID, timeout, kênh bận) phải tự viết
   và tự test từng byte với `tools/fido_check.py`. Ước tính đây là hơn
   nửa công sức port.
2. **Thiếu secure element.** Mọi khóa nằm trong flash trong của S3, không
   có chip bảo mật riêng. Kẻ có vật lý key + biết khai thác có thể đọc
   flash. Giảm nhẹ: bật Secure Boot + mã hóa flash + khóa efuse JTAG/UART
   ở bản cuối, nhưng vẫn yếu hơn key có secure element thật.
3. **Chưa audit.** opensk là code của Google nhưng bản crate `0.1.0` mới
   phát hành (2026-10-22); lớp port của ta (nhất là Persist, HID, mã PIN)
   chưa ai review bảo mật. TUYỆT ĐỐI không dùng key này cho tài khoản thật
   trước khi có audit độc lập.
4. **Hao mòn flash.** Bộ đếm ký ghi mỗi lần xác thực; không có
   wear-leveling thì sector flash chết sau vài chục nghìn lần ký.
5. **Efuse/unstable API.** `esp-storage` cho S3 đòi `esp-hal/unstable`,
   nghĩa là API có thể đổi giữa các bản vá — phải ghim bản (`Cargo.lock`)
   và đọc changelog khi nâng cấp.
6. **Nhầm chân LED.** DevKit v1 LED ở GPIO38, v2 ở GPIO48. Firmware phải
   chọn đúng (tốt nhất là detect lúc build qua feature `board-v1/v2`).

## 5. Thứ tự port gợi ý

1. Dựng toolchain `espup` + flash thử mẫu esp-generate để chắc đường nạp.
2. Sửa `src/main.rs` cho khớp tên API `esp-hal 1.2` thật, `cargo build`
   cho qua (vẫn còn `todo!()` cũng được).
3. Làm `Rng` + `Write` (có log là debug được mọi thứ sau).
4. Làm `Clock` + `UserPresence` (nút + LED, test bằng mắt).
5. Làm `Persist` + chạy test `sk-env` logic trên host trước.
6. Làm `HidConnection` + PING echo, kiểm bằng
   `python tools/fido_check.py --self-test` rồi với key thật.
7. Cắm opensk (`Ctap::new` + vòng lặp gói), chạy GetInfo thật.
8. Làm `Crypto` phần cứng (tùy chọn), đo tốc độ ký.
9. Khóa bảo mật (Secure Boot, mã hóa flash) + audit.
