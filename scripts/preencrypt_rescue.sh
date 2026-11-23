#!/usr/bin/env bash
# Mã hóa trước ảnh hardened bằng khóa FE của đúng board để nạp lại chip đã khóa.
# Chip SB+FE+secure-download chỉ boot được ảnh vừa ký RSA vừa mã hóa đúng khóa
# FE (bài học key-01). Script chỉ mã hóa (an toàn) rồi IN RA lệnh nạp để người
# chạy tự kiểm tra. Xem hardware/provision-runbook.md mục 7.
#   bash scripts/preencrypt_rescue.sh keys/fe-key-02.bin [anh-vao] [anh-ra]
set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo "Dùng: bash scripts/preencrypt_rescue.sh <khoa-fe> [anh-vao] [anh-ra]"
  exit 2
fi
FEKEY="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IN="${2:-$ROOT/web/firmware/pico-fido-v8.2/pico_fido_esp32-s3-hardened.bin}"
OUT="${3:-${TMPDIR:-/tmp}/rescue-$(date +%Y%m%d-%H%M%S).bin}"
IDF="$ROOT/.tooling/esp-idf"
export IDF_TOOLS_PATH="$ROOT/.tooling/esp-tools"

[ -f "$FEKEY" ] || { echo "Không thấy khóa FE: $FEKEY"; exit 1; }
KEYLEN="$(wc -c < "$FEKEY")"
[ "$KEYLEN" = "32" ] || [ "$KEYLEN" = "64" ] || { echo "Khóa FE phải 32 hoặc 64 byte, thấy $KEYLEN."; exit 1; }
[ -f "$IN" ] || { echo "Không thấy ảnh vào: $IN"; exit 1; }
FIRST="$(xxd -p -l 1 "$IN")"
[ "$FIRST" = "e9" ] || { echo "Ảnh vào thiếu bootloader (byte đầu không phải 0xE9). Dừng."; exit 1; }
[ -f "$IDF/export.sh" ] || { echo "Thiếu $IDF. Cài ESP-IDF v5.5.1 vào .tooling/esp-idf trước."; exit 1; }

# shellcheck disable=SC1091
. "$IDF/export.sh" > /dev/null
espsecure.py encrypt_flash_data --aes_xts --keyfile "$FEKEY" --address 0x0 --output "$OUT" "$IN"
echo "Đã mã hóa: $OUT ($(wc -c < "$OUT") byte)."
echo ""
echo "Chạy tay lệnh nạp (thay PORT bằng cổng thật, KHÔNG rút cáp giữa chừng):"
echo "esptool.py --chip ESP32-S3 -p PORT -b 115200 --no-stub write_flash --force --flash_mode dio --flash_freq 80m --flash_size keep 0x0 $OUT"
