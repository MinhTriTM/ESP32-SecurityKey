# Danh mục chip ESP (kèm hỗ trợ Rust)

Tài liệu nguồn chân lý cho repo `esp-hal-matrix`. Crate `esp-inventory`
mã hóa lại đúng bảng này để các công cụ tra cứu.

Ngày cập nhật: 22/11/2026. Phiên bản tham chiếu: esp-hal 1.2.2,
esp-println 0.18.0, esp-backtrace 0.20.0 (đã tra crates.io).

## 1. Bảng chip (14 chip ESP32 + ESP8266)

| Chip | Nhân / xung | Radio | Đặc điểm chọn chip | esp-hal | Target Rust |
|------|--------------|-------|--------------------|---------|-------------|
| ESP32 | 2x Xtensa LX6 / 240 MHz | WiFi 4 + BT Classic + BLE 4.2 | Quốc dân đời đầu, nhiều GPIO | đầy đủ | `xtensa-esp32-none-elf` |
| ESP32-S2 | 1x Xtensa LX7 / 240 MHz | WiFi 4 (không BT) | USB OTG native, nhiều ADC | đầy đủ | `xtensa-esp32s2-none-elf` |
| ESP32-S3 | 2x Xtensa LX7 / 240 MHz | WiFi 4 + BLE 5.0 | USB OTG, lệnh AI, PSRAM octal; chip khóa FIDO2 | đầy đủ | `xtensa-esp32s3-none-elf` |
| ESP32-S31 | 2x RISC-V / 320 MHz | WiFi 6 + BT 5.4 + 15.4 | Đời mới hướng WiFi 6 | mới/sơ khai | `riscv32imac-esp-espidf` |
| ESP32-C2 (ESP8684) | 1x RISC-V / 120 MHz | WiFi 4 + BLE 5.0 | Rẻ nhất, nâng cấp từ ESP8266 | đầy đủ | `riscv32imc-esp-espidf` |
| ESP32-C3 | 1x RISC-V / 160 MHz | WiFi 4 + BLE 5.0 | RISC-V quốc dân, USB Serial/JTAG | đầy đủ | `riscv32imc-esp-espidf` |
| ESP32-C5 | 1x RISC-V / 240 MHz | WiFi 6 (2.4 + 5 GHz) + BLE + 15.4 | WiFi 5 GHz duy nhất của Espressif | đầy đủ | `riscv32imac-esp-espidf` |
| ESP32-C6 | 1x RISC-V / 160 MHz | WiFi 6 + BLE 5.3 + 15.4 | Matter/Thread/Zigbee | đầy đủ | `riscv32imac-esp-espidf` |
| ESP32-C61 | 1x RISC-V / 160 MHz | WiFi 6 + BLE + 15.4 | Rút gọn chân/flash của C6 | đầy đủ | `riscv32imac-esp-espidf` |
| ESP32-H2 | 1x RISC-V / 96 MHz | BLE 5.3 + 15.4 (không WiFi) | Node Thread/Zigbee tiết kiệm pin | đầy đủ | `riscv32imac-esp-espidf` |
| ESP32-H21 | 1x RISC-V / đang công bố | BLE + 15.4 | Đang lấy mẫu | chưa có | — |
| ESP32-H4 | 1x RISC-V / đang công bố | BLE + 15.4 | Đang lấy mẫu | chưa có | — |
| ESP32-P4 | 2x RISC-V / 400 MHz | Không radio (ghép chip radio) | Mạnh nhất: MIPI, AI, HMI | mới/thiếu HMAC-DS-KeyManager | `riscv32imafc-esp-espidf` |
| ESP32-E22 | Radio đồng xử lý | WiFi 6E | Ghép ESP32-P4 | chưa có | — |
| ESP8266 / ESP8285 | 1x Xtensa L106 / 160 MHz | WiFi 4 | Giá rẻ, esp-rs KHÔNG hỗ trợ | không hỗ trợ | — |

Quy tắc đọc cột esp-hal: "đầy đủ" là dùng được cho sản phẩm;
"mới/thiếu" là đã có feature trong esp-hal nhưng thiếu ngoại vi
(P4 thiếu HMAC/DS/KeyManager; S31 còn sơ khai);
"chưa có" là chưa có esp-hal; "không hỗ trợ" là esp-rs không làm.

## 2. Module phổ biến theo chip

| Module | Chip | Flash / PSRAM | Ghi chú |
|--------|------|---------------|---------|
| ESP-WROOM-32 / ESP32-WROVER | ESP32 | 4–16 MB / 0–8 MB | WROVER có PSRAM |
| ESP32-S2-Saola-1 | ESP32-S2 | 4 MB / 2 MB | Kit tham chiếu S2 |
| ESP32-S3-WROOM-1/1U | ESP32-S3 | 8–16 MB / 0–8 MB | Dự án mẹ dùng bản N16R8 |
| ESP32-S3-WROOM-2 | ESP32-S3 | 16–32 MB / 8 MB | Chân 1.27 mm |
| ESP8684H2 / H4 | ESP32-C2 | 2–4 MB / không | Siêu nhỏ, giá rẻ |
| ESP32-C3-MINI-1 / WROOM-02 | ESP32-C3 | 4 MB / không | Kit RISC-V phổ biến |
| ESP32-C6-WROOM-1 | ESP32-C6 | 8 MB / không | WiFi 6 + Thread |
| ESP32-H2-MINI-1 | ESP32-H2 | 4 MB / không | Node Matter |
| ESP32-P4-Function-EV-Board | ESP32-P4 | 16–32 MB / 16–32 MB | Board đánh giá, chưa module đại trà |

## 3. Quy tắc hậu tố module (N / R / U / H)

Ví dụ đọc tên: `ESP32-S3-WROOM-1-N16R8` = module S3, flash 16 MB, PSRAM 8 MB.

| Hậu tố | Ý nghĩa | Ví dụ |
|--------|---------|-------|
| `N4 / N8 / N16 / N32` | Dung lượng flash SPI trên module WROOM/WROVER: 4/8/16/32 MB | N16R8 của dự án mẹ |
| `R2 / R8 / R16` | Dung lượng PSRAM: 2/8/16 MB (R8 thường là octal) | R8 = 8 MB octal PSRAM |
| `U` (trong `WROOM-1U`) | Biến thể ăng-ten u.FL (gắn ăng-ten ngoài), thay vì ăng-ten PCB | WROOM-1U |
| `H2 / H4 / H8` | Dung lượng flash trên dòng MINI siêu nhỏ (gói chip khác) | MINI-1-H4 = flash 4 MB |

Lưu ý: chữ `R` vắng mặt nghĩa là không có PSRAM.
Luôn đối chiếu datasheet của đúng mã module trước khi đặt hàng,
vì Espressif bổ sung mã mới theo thời gian.

## 4. Toolchain theo dòng chip

- Chip Xtensa (ESP32/S2/S3): bắt buộc toolchain fork qua espup.
  ```powershell
  cargo install espup
  espup install
  . $env:USERPROFILE\export-esp.ps1
  ```
- Chip RISC-V (C2/C3/C5/C6/C61/H2/S31/P4): dùng rustc chuẩn,
  thêm target esp (`rustup target add <target>`); nếu target esp
  chưa có trên kênh đang dùng thì cài qua espup như trên.

## 5. Bảo mật theo lớp (ghi nhớ khi khóa chip)

- Secure Boot v2 + Flash Encryption XTS-AES + chống rollback nằm ở
  bootloader IDF, cấu hình bằng espflash/espefuse; eFuse ghi một chiều.
- esp-hal cung cấp driver AES/SHA/RSA/ECC/HMAC/RNG tùy chip
  (P4 hiện thiếu HMAC/DS/KeyManager).
- ESP32-P4 silicon rev ≤v3.2 lỗi ECDSA ROM: ký Secure Boot bằng RSA-3072.
- Quy trình khóa mẫu: xem `cargo run -p esp-provision -- --chip esp32s3 --dry-run`.
