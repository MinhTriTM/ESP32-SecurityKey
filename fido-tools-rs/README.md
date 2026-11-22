# fido-tools-rs

Bản Rust của 5 tool host trong `tools/` của ESP32-SecurityKey: một binary cho mỗi
tool, chạy độc lập không cần cài Python. Định dạng file và giao thức giữ nguyên
để đọc được mọi dữ liệu do bản Python tạo ra.

## Tool

| Binary | Bản Python | Chức năng |
|---|---|---|
| `split-secret` | `split_secret.py` | Chia/ghép Shamir K-trên-N, vẽ QR |
| `vault` | `vault.py` | Két AES-256-GCM + PBKDF2 600k vòng |
| `mnemonic` | `mnemonic.py` | Cụm từ BIP-39, seed, vẽ QR |
| `hid-echo` | `hid_echo.py` | Kiểm tra echo HID của hwtest |
| `fido-check` | `fido_check.py` | Kiểm tra key 3 tầng: HID, PING, CTAP2 |

## Dùng

```sh
cargo build --release
./target/release/split-secret --self-test
./target/release/split-secret split --shares 5 --threshold 3 --out USB1
./target/release/vault encrypt --in recovery.txt --out ket.bin
./target/release/mnemonic new --words 24
./target/release/hid-echo --vid 0x303A
./target/release/fido-check --index 0
```

Mọi tool đều có `--self-test` chạy không cần phần cứng, và mã thoát theo bảng
chuẩn của repo mẹ: 0 ok, 1 lỗi chạy, 2 sai dùng.

## Tương thích và điểm khác bản Python

- File share, két, cụm từ đọc chéo hai chiều Python-Rust. Test `compat` của
  mỗi crate đọc fixture do chính bản Python sinh ra.
- Vá 4 lỗi đã biết mà không đổi định dạng đúng: `parse_share` từ chối index
  ngoài 1..=255 và header thiếu khóa (NCKH-022, NCKH-028); `hid-echo` lọc thêm
  usage/VID/PID và trả lỗi thay vì `assert` (NCKH-016); bộ giải CBOR chặn thân
  cụt, lồng sâu và text không UTF-8 (NCKH-010).
- Mật khẩu, khóa và bí mật trung gian được xóa khỏi RAM (`zeroize`) sau khi dùng.

## Kiểm thử

```sh
cargo test
```

Unit test port toàn bộ self-test của bản Python; test tương thích đọc fixture
trong `crates/*/tests/fixtures/`. Muốn sinh lại fixture, chạy đoạn Python ghi
trong đầu mỗi file `tests/compat.rs`.
