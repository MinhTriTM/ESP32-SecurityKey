# esp32s3-hello

Ví dụ chào + chớp LED cho ESP32-S3 (mã `esp32s3`), sinh tự động bằng `new-esp-firmware`.

- Target: `xtensa-esp32s3-none-elf`
- Toolchain: espup (fork Xtensa)
- Trạng thái esp-hal: đầy đủ

## Cài toolchain

Chip Xtensa nên phải cài toolchain fork qua espup trước:

```powershell
cargo install espup
espup install
. $env:USERPROFILE\export-esp.ps1
```

## Build

```powershell
cargo build --release
```

## Nạp và xem log

```powershell
espflash flash --monitor --port COM5 target\xtensa-esp32s3-none-elf\release\esp32s3-hello
```

(Thay `COM5` bằng cổng COM của kit.)
