# Script flash mẫu cho Windows. ĐÂY LÀ MẪU, đọc kỹ từng lệnh trước khi chạy.
# Sai cổng COM là flash nhầm thiết bị. Không chạy mù.

# --- Sửa các biến này trước khi chạy ---
$PicoFidoDir = "$HOME\pico-fido"
$PicoFidoCommit = "15b848d821b4995eb1b29a5c2a4c24c25d1a768e"  # tag v8.2, xem docs/04-firmware.md
$SerialPort = "COM3"
# ---------------------------------------

if (-not (Test-Path $PicoFidoDir)) {
    Write-Output "Khong thay $PicoFidoDir. Clone pico-fido truoc: git clone https://github.com/polhenarejos/pico-fido"
    exit 1
}

Set-Location $PicoFidoDir
git fetch --all --tags
git checkout $PicoFidoCommit
$Head = (git rev-parse HEAD).Trim()
if ($Head -ne $PicoFidoCommit) {
    Write-Output "SHA sau checkout khong khop commit da ghim. Dung lai kiem tra."
    exit 1
}
git submodule update --init --recursive

Write-Output "Da ve dung commit v8.2. Cac buoc tiep theo (doc docs/04-firmware.md truoc khi chay):"
Write-Output "  1. Mo ESP-IDF v5.5.1 PowerShell: idf.py set-target esp32s3; idf.py all"
Write-Output "  2. esptool.py --chip ESP32-S3 merge_bin -o release/pico_fido_esp32-s3.bin @flash_args"
Write-Output "  3. esptool.py --chip ESP32-S3 -p $SerialPort write_flash 0x0 release/pico_fido_esp32-s3.bin"
Write-Output "Flash xong thi cam lai bang cong USB OTG native, chay tools/fido_check.py."
