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
N16R8="$ROOT/config/sdkconfig.esp32s3-n16r8"
[ -f "$N16R8" ] || { echo "Thiếu $N16R8."; exit 1; }
PICO_DEFAULTS="$PICO/pico-keys-sdk/config/esp32/sdkconfig.defaults"
if [ "$VARIANT" = "hardened" ]; then
  [ -f "$ROOT/keys/secure-boot-signing.key" ] || { echo "Thiếu keys/secure-boot-signing.key. Chạy python tools/gen_sign_key.py trước."; exit 1; }
  [ -f "$ROOT/config/sdkconfig.hardened" ] || { echo "Thiếu config/sdkconfig.hardened."; exit 1; }
  export SDKCONFIG_DEFAULTS="$PICO_DEFAULTS;$N16R8;$ROOT/config/sdkconfig.hardened"
  echo "Build bản ký (hardened)."
else
  export SDKCONFIG_DEFAULTS="$PICO_DEFAULTS;$N16R8"
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
# flash_args của bản secure-boot KHÔNG có bootloader -> tự thêm vào đầu.
grep -v bootloader flash_args | grep -v '^[[:space:]]*$' > flash_args_no_bl || true
grep '^[[:space:]]*-' flash_args_no_bl > flash_args_full || true
echo '0x0 bootloader/bootloader.bin' >> flash_args_full
grep -v '^[[:space:]]*-' flash_args_no_bl >> flash_args_full
merge_out=$(esptool.py --chip ESP32-S3 merge_bin -o ../release/pico_fido_esp32-s3.bin @flash_args_full 2>&1)
echo "$merge_out" | tail -3
echo "$merge_out" | grep -qiE 'overlap|error' && { echo 'Gộp bin đáng ngờ, dừng lại.'; exit 1; }
python3 -c "import sys;d=open('../release/pico_fido_esp32-s3.bin','rb').read(4);sys.exit(0 if d[:1]==b'\xe9' else 1)" || { echo 'Bin gộp thiếu bootloader.'; exit 1; }
cd "$ROOT"
OUT="$ROOT/web/firmware/pico-fido-v8.2"
mkdir -p "$OUT"
cp "$PICO/release/pico_fido_esp32-s3.bin" "$OUT/pico_fido_esp32-s3-$VARIANT.bin"
python3 tools/web_firmware.py
python3 tools/web_firmware.py --check
echo "Xong bản $VARIANT."
