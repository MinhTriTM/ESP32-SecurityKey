# s3-fido — firmware mẫu cho ESP32-S3 (chưa build được)

Khung firmware key FIDO2 viết bằng Rust: lõi CTAP2 lấy từ crate `opensk 0.1`,
driver phần cứng dùng `esp-hal 1.2`. Hiện tại mọi hàm trong `src/main.rs`
đều là `todo!()` — đây là khung để port, KHÔNG phải firmware chạy được.

Board đích: ESP32-S3 DevKit, module N16R8 (flash 16MB + PSRAM 8MB),
USB OTG native GPIO19/20, nút BOOT GPIO0, LED WS2812 GPIO38/48
(chi tiết chân cẳng xem `hardware/wiring.md` ở repo mẹ).

## Cần gì để build

1. Cài Rust qua `espup` (toolchain Xtensa cho ESP32-S3), làm theo
   hướng dẫn chính thức của dự án esp-rs (kho `espup` trên GitHub).
2. Cài `espflash` (nạp firmware) và `cargo-generate` nếu muốn đối chiếu
   với template chuẩn `esp-generate` cho ESP32-S3.
3. Cắm board bằng cổng UART (cổng nạp), KHÔNG phải cổng OTG.

## Build và nạp (khi đã cài đủ tool)

```powershell
# Trong thư mục firmware/s3-fido, sau khi đã export môi trường espup:
cargo build --release
espflash flash --monitor target/xtensa-esp32s3-none-elf/release/s3-fido
```

Lần flash đầu nếu không tự vào chế độ nạp: nhấn giữ BOOT (GPIO0),
nhấn RST, thả RST rồi thả BOOT.

## Vì sao chưa build trên máy dev hiện tại

Máy Windows hiện tại chỉ có cargo thường (target host), chưa có
toolchain `xtensa-esp32s3-none-elf` của espup. Crate này cố tình
KHÔNG nằm trong workspace của repo (xem `exclude` ở `Cargo.toml` gốc)
để `cargo test` ở crate host (`crates/sk-env`) không bị vạ lây.

## Thứ tự port (tóm tắt, chi tiết ở `docs/PORTING.md`)

1. Đối chiếu tên API `esp-hal 1.2` trong `src/main.rs` với docs.rs rồi sửa.
2. Làm `S3Rng` + `S3Write` trước (dễ, có log là debug được).
3. Làm `S3Clock` + `S3Presence` (nút BOOT + LED).
4. Làm `S3Persist` trên flash (cần wear-leveling cho bộ đếm ký).
5. Làm `S3Hid` trên USB OTG — việc khó nhất, quyết định key có nói
   được CTAPHID với `tools/fido_check.py` hay không.
6. Chọn `S3Crypto` (phần cứng hay `software_crypto` của opensk),
   rồi chạy self-test của `tools/fido_check.py` với key thật.
