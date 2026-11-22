#!/usr/bin/env bash
# Script flash mẫu cho Linux. ĐÂY LÀ MẪU, đọc kỹ từng lệnh trước khi chạy.
# Sai cổng serial là flash nhầm thiết bị. Không chạy mù.
set -euo pipefail

# --- Sửa các biến này trước khi chạy ---
PICO_FIDO_DIR="$HOME/pico-fido"
PICO_FIDO_COMMIT="15b848d821b4995eb1b29a5c2a4c24c25d1a768e"  # tag v8.2, xem docs/04-firmware.md
SERIAL_PORT="/dev/ttyACM0"
# ---------------------------------------

if [ ! -e "$SERIAL_PORT" ]; then
  echo "Không thấy $SERIAL_PORT. Kiểm tra cổng UART của board."
  exit 1
fi

if [ ! -d "$PICO_FIDO_DIR" ]; then
  echo "Không thấy $PICO_FIDO_DIR. Clone trước: git clone https://github.com/polhenarejos/pico-fido"
  exit 1
fi

cd "$PICO_FIDO_DIR"
git fetch --all --tags
git checkout "$PICO_FIDO_COMMIT"
HEAD_SHA="$(git rev-parse HEAD)"
if [ "$HEAD_SHA" != "$PICO_FIDO_COMMIT" ]; then
  echo "SHA sau checkout không khớp commit đã ghim. Dừng lại kiểm tra."
  exit 1
fi
git submodule update --init --recursive

echo "Đã về đúng commit v8.2. Các bước tiếp theo (đọc docs/04-firmware.md trước khi chạy):"
echo "  1. . ./export.sh (ESP-IDF v5.5.1); idf.py set-target esp32s3; idf.py all"
echo "  2. esptool.py --chip ESP32-S3 merge_bin -o release/pico_fido_esp32-s3.bin @flash_args"
echo "  3. esptool.py --chip ESP32-S3 -p $SERIAL_PORT write_flash 0x0 release/pico_fido_esp32-s3.bin"
echo "Flash xong thì rút ra, cắm lại bằng cổng USB OTG native rồi chạy tools/fido_check.py."
