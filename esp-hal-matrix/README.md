# esp-hal-matrix

Ma trận Rust (esp-hal) cho mọi chip ESP, trọng tâm bảo mật.
Repo con của dự án khóa FIDO2 trên board ESP32-S3 DevKit N16R8.

## Mục đích

- Một chỗ tra cứu: chip nào có esp-hal, target nào, toolchain nào.
- Sinh nhanh crate firmware mẫu theo mã chip (`new-esp-firmware`).
- Dựng lệnh khóa chip (Secure Boot v2 + Flash Encryption) có kiểm soát
  rủi ro eFuse (`esp-provision`).
- Hai firmware mẫu esp-hal 1.2 để CI build kiểm chứng.

## Cấu trúc

```text
esp-hal-matrix/
├── Cargo.toml                  # workspace 3 crate host (firmware KHÔNG ở đây)
├── README.md
├── .gitignore
├── docs/
│   └── DANH-MUC-ESP.md         # bảng chip + module + hậu tố N/R/U/H + bảo mật
├── crates/
│   ├── inventory/              # lib esp_inventory: struct Chip, ALL_CHIPS, lookup
│   ├── gen-template/           # lib esp_gen_template + bin new-esp-firmware
│   └── provision/              # lib esp_provision + bin esp-provision
├── firmware/
│   ├── esp32s3-hello/          # mẫu Xtensa (ngoài workspace)
│   └── esp32c6-hello/          # mẫu RISC-V (ngoài workspace)
└── .github/workflows/matrix.yml
```

## Cách build firmware từng chip

### 1. Chip Xtensa: ESP32 / ESP32-S2 / ESP32-S3

```powershell
cargo install espup
espup install
. $env:USERPROFILE\export-esp.ps1
cd firmware/esp32s3-hello
cargo build --release
espflash flash --monitor --port COM5 target/xtensa-esp32s3-none-elf/release/esp32s3-hello
```

### 2. Chip RISC-V: C2 / C3 / C5 / C6 / C61 / H2 / S31 / P4

```powershell
rustup target add riscv32imac-esp-espidf   # C5/C6/C61/H2/S31 (C2/C3 dùng riscv32imc-...)
cd firmware/esp32c6-hello
cargo build --release
espflash flash --monitor --port COM5 target/riscv32imac-esp-espidf/release/esp32c6-hello
```

(Nếu target esp chưa có trên kênh rustup đang dùng, cài qua espup
như mục chip Xtensa.)

### 3. Chip chưa/không hỗ trợ

H21/H4/E22 chưa có esp-hal nên chưa build được; ESP8266 không được
esp-rs hỗ trợ (không có kế hoạch hỗ trợ).

## Công cụ host

```powershell
# Sinh firmware mới từ mẫu
cargo run -p esp-gen-template --bin new-esp-firmware -- --chip esp32c6 --ten dem-led --o firmware/dem-led

# Xem kế hoạch khóa chip (chỉ in lệnh, an toàn)
cargo run -p esp-provision -- --chip esp32s3 --port COM5 --dry-run

# Chạy test host
cargo test
```

Lệnh khóa thật (ghi eFuse một chiều) bắt buộc đủ 3 điều kiện:
`--thuc-thi --toi-hieu-rui-ro --ma-doc-ve <mã đọc từ board-info khớp chip khai báo>`.

## Trạng thái kiểm chứng (trung thực, ngày 22/11/2026)

| Hạng mục | Kết quả |
|----------|---------|
| `cargo test` 3 crate host | ✅ 22/22 test pass (inventory 9, gen-template 4, provision 9), 0 fail |
| Binary `esp-provision --dry-run` | ✅ chạy thử thật, in đúng 8 bước cho S3 |
| Binary `new-esp-firmware` | ✅ chạy thử thật, sinh đủ 5 file; 2 firmware mẫu do chính nó sinh ra |
| Build firmware S3/C6 trên máy này | ❌ CHƯA build (thiếu toolchain espup Xtensa + target RISC-V esp); không bịa kết quả |
| API mẫu esp-hal 1.2 | ⚠️ chép theo mã nguồn esp-hal 1.2.2 + esp-backtrace 0.20 + esp-println 0.18 trong cache crates.io; chờ CI build xác nhận |
| Quy trình khóa espefuse | ⚠️ câu lệnh dựng theo quy ước IDF 5.x; tên bit eFuse phải đối chiếu `espefuse --help` trước khi chạy thật |

CI (`.github/workflows/matrix.yml`) cài espup rồi build cả 2 firmware
mẫu trên Ubuntu; trạng thái CI sẽ là kiểm chứng build thật đầu tiên.
