# esp32c6-hello

Ví dụ chào + chớp LED cho ESP32-C6 (mã `esp32c6`), sinh tự động bằng `new-esp-firmware`.

- Target: `riscv32imac-esp-espidf`
- Toolchain: rustc chuẩn + target esp
- Trạng thái esp-hal: đầy đủ

## Cài toolchain

Chip RISC-V dùng rustc chuẩn, chỉ cần thêm target esp:

```powershell
rustup target add {target}
```

(Nếu target esp chưa có trên kênh đang dùng, cài qua espup như chip Xtensa.)

## Build

```powershell
cargo build --release
```

## Nạp và xem log

```powershell
espflash flash --monitor --port COM5 target\riscv32imac-esp-espidf\release\esp32c6-hello
```

(Thay `COM5` bằng cổng COM của kit.)
