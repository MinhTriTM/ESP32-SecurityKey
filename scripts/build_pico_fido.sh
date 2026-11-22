#!/usr/bin/env bash
# Build pico-fido v8.2 cho ESP32-S3 rồi gộp binary (U001).
#   bash scripts/build_pico_fido.sh [plain|hardened]
set -euo pipefail
VARIANT="${1:-plain}"
if [ "$VARIANT" != "plain" ] && [ "$VARIANT" != "hardened" ]; then
  echo "Variant phải là plain hoặc hardened."
  exit 2
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IDF="$ROOT/.tooling/esp-idf"
PICO="$ROOT/.tooling/pico-fido"
export IDF_TOOLS_PATH="$ROOT/.tooling/esp-tools"
PINNED="15b848d821b4995eb1b29a5c2a4c24c25d1a768e"  # tag v8.2

[ -f "$IDF/export.sh" ] || { echo "Thiếu $IDF. Cài ESP-IDF v5.5.1 vào .tooling/esp-idf trước."; exit 1; }
[ -d "$PICO" ] || { echo "Thiếu $PICO. Clone pico-fido vào .tooling/pico-fido trước."; exit 1; }
HEAD_SHA="$(git -C "$PICO" rev-parse HEAD)"
[ "$HEAD_SHA" = "$PINNED" ] || { echo "pico-fido không đúng commit v8.2 ($HEAD_SHA). Dừng để kiểm tra."; exit 1; }
if [ "$VARIANT" = "hardened" ]; then
  [ -f "$ROOT/keys/secure-boot-signing.key" ] || { echo "Thiếu keys/secure-boot-signing.key. Chạy python tools/gen_sign_key.py trước."; exit 1; }
  [ -f "$ROOT/config/sdkconfig.hardened" ] || { echo "Thiếu config/sdkconfig.hardened."; exit 1; }
  export SDKCONFIG_DEFAULTS="$PICO/pico-keys-sdk/config/esp32/sdkconfig.defaults;$ROOT/config/sdkconfig.hardened"
  echo "Build bản ký (hardened)."
else
  echo "Build bản thử (plain, không ký)."
fi

# shellcheck disable=SC1091
. "$IDF/export.sh"
cd "$PICO"
if [ "$VARIANT" = "hardened" ]; then idf.py fullclean; fi  # đổi sdkconfig phải sạch
idf.py set-target esp32s3
idf.py all
mkdir -p release
cd build
esptool.py --chip ESP32-S3 merge_bin -o ../release/pico_fido_esp32-s3.bin @flash_args
cd "$ROOT"
OUT="$ROOT/web/firmware/pico-fido-v8.2"
mkdir -p "$OUT"
cp "$PICO/release/pico_fido_esp32-s3.bin" "$OUT/pico_fido_esp32-s3-$VARIANT.bin"
python3 tools/web_firmware.py
python3 tools/web_firmware.py --check
echo "Xong bản $VARIANT."
