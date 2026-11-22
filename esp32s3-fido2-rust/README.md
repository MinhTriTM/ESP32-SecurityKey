# esp32s3-fido2-rust — Khung key FIDO2 bằng Rust cho ESP32-S3

Khung (chưa phải sản phẩm) của một khóa bảo mật FIDO2 chạy trên board
ESP32-S3 DevKit (module N16R8: flash 16MB + PSRAM 8MB), viết bằng Rust,
dựa trên lõi CTAP2 của crate `opensk 0.1.0` (OpenSK dạng thư viện).

Tài liệu, comment và báo cáo trong repo này đều bằng tiếng Việt.
Thuật ngữ kỹ thuật (CTAP2, HID, CBOR...) giữ nguyên tiếng Anh.

## 1. Mục tiêu

- Có một codebase Rust duy nhất cho key FIDO2: lõi logic test được trên
  máy tính (host), firmware flash được lên ESP32-S3.
- Key nói đúng giao thức CTAPHID + CTAP2/CBOR mà script
  `tools/fido_check.py` của repo mẹ kiểm tra (INIT, PING ngắn/dài, GetInfo).
- Tận dụng chân cẳng có sẵn của DevKit: USB OTG native GPIO19/20,
  nút BOOT GPIO0 làm xác nhận hiện diện, LED WS2812 GPIO38/48 báo hiệu.

## 2. Kiến trúc

```text
 May host (kiem tra)              Key ESP32-S3 (firmware s3-fido)
+----------------------+        +----------------------------------+
| tools/fido_check.py  |  USB   |  USB OTG HID (GPIO19/20)         |
|  INIT / PING /       |<======>|   S3Hid: send/recv goi 64 byte   |
|  CTAP2 GetInfo (CBOR)|  HID   +----------------------------------+
+----------------------+        |  opensk::Ctap (crate opensk 0.1) |
                                |   xu ly CTAP2: credential, PIN,  |
                                +----------------------------------+
                                |  S3Env (cai dat opensk::env::Env)|
                                |   Rng        <- rng phan cung   |
                                |   UserPresence <- nut BOOT GPIO0|
                                |   Persist    <- esp-storage     |
                                |   KeyStore   <- Helper opensk   |
                                |   Clock      <- TimerGroup      |
                                |   Crypto     <- software_crypto |
                                |   Write      <- USB-Serial-JTAG |
                                |   Customization <- hang cua ta  |
                                +----------------------------------+

 Khung test tren host (da chay duoc):
+----------------------------------+
| crates/sk-env: trait SkEnv truong|
| tuong (storage/rng/clock/        |
| presence/hid) + FakeEnv RAM      |
|  -> cargo test -p sk-env         |
+----------------------------------+
```

## 3. Bố cục thư mục

- `crates/sk-env/` — thư viện host: trait môi trường trừu tượng của riêng
  ta + `FakeEnv` chạy RAM + unit test. ĐÃ CHẠY ĐƯỢC, xem dưới.
- `firmware/s3-fido/` — firmware mẫu cho ESP32-S3 (KHÔNG thuộc workspace,
  cần toolchain Xtensa). MẪU CHƯA BUILD, mọi hàm là `todo!()`.
- `docs/PORTING.md` — ánh xạ từng thành viên `Env` của opensk sang API
  esp-hal/RustCrypto + rủi ro lớn + thứ tự port.
- `.gitignore` — bỏ qua `target/`.

## 4. Trạng thái trung thực (đọc trước khi tin)

| Phần | Trạng thái |
|------|-----------|
| `sk-env` + test host | CHẠY ĐƯỢC. `cargo test -p sk-env`: 5 test xanh (storage, rng, presence, HID, clock). |
| `firmware/s3-fido` | MẪU CHƯA BUILD. Chưa từng biên dịch vì máy dev chưa có toolchain Xtensa (`espup`). Tên API `esp-hal` trong `main.rs` suy từ tài liệu, có thể lệch. |
| Giao thức CTAPHID/CBOR | Mới ở phía host (`fido_check.py` + `FakeDevice`). Key thật chưa nói được byte nào. |
| Bảo mật | Chưa audit, chưa Secure Boot/mã hóa flash. KHÔNG dùng cho tài khoản thật. |

## 5. Chạy test host

```powershell
cd esp32s3-fido2-rust
cargo test -p sk-env
```

Kết quả mong đợi: `5 passed; 0 failed` (chi tiết xem báo cáo giao đợt).

## 6. Roadmap port firmware

1. Dựng toolchain `espup` + nạp thử mẫu `esp-generate` lên board.
2. Sửa `firmware/s3-fido/src/main.rs` cho khớp API `esp-hal 1.2` thật.
3. Làm `Rng` + `Write` (có log), rồi `Clock` + `UserPresence` (nút + LED).
4. Làm `Persist` trên flash (kèm wear-leveling cho bộ đếm ký).
5. Làm `HidConnection` trên USB OTG + PING echo, kiểm bằng `fido_check.py`.
6. Cắm lõi `opensk::Ctap`, chạy GetInfo thật, rồi MakeCredential/GetAssertion.
7. Tối ưu `Crypto` bằng phần cứng (tùy chọn), khóa Secure Boot + mã hóa
   flash, và audit bảo mật độc lập trước khi dùng thật.

Chi tiết kỹ thuật ở [docs/PORTING.md](docs/PORTING.md).
