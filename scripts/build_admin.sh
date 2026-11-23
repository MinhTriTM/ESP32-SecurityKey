#!/usr/bin/env bash
# Biên dịch sketch cổng quản trị rồi đưa file gộp vào siêu web nạp.
# arduino-cli đã tự sinh admin_portal.ino.merged.bin (nạp ở 0x0).
#   bash scripts/build_admin.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export ARDUINO_DIRECTORIES_DATA="$ROOT/.tooling/data"
BUILD="$ROOT/.tooling/build-admin"

"$ROOT/.tooling/arduino-cli/arduino-cli" compile \
  --fqbn 'esp32:esp32:esp32s3:CDCOnBoot=cdc,USBMode=default,FlashMode=dio,PSRAM=opi' \
  --build-path "$BUILD" "$ROOT/firmware/admin_portal"

MERGED="$BUILD/admin_portal.ino.merged.bin"
[ -f "$MERGED" ] || { echo "Thiếu file gộp, dừng lại."; exit 1; }
python3 -c "import sys;d=open('$MERGED','rb').read(4);sys.exit(0 if d[:1]==b'\xe9' else 1)" \
  || { echo "Bin gộp thiếu bootloader (byte đầu không phải 0xE9)."; exit 1; }

OUT="$ROOT/web/firmware/admin-portal"
mkdir -p "$OUT"
cp "$MERGED" "$OUT/admin_portal.ino.merged.bin"
python3 "$ROOT/tools/web_firmware.py"
python3 "$ROOT/tools/web_firmware.py" --check
echo "Xong cổng quản trị."
