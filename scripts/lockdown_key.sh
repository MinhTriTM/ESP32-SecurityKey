#!/usr/bin/env bash
# Danh mục khóa chip sau khi flash bản hardened (U002/U015).
# AN TOÀN THEO THIẾT KẾ: script chỉ đọc eFuse và in hướng dẫn từng bước,
# KHÔNG tự đốt fuse nào (fuse một chiều, mỗi lệnh đốt phải gõ tay).
#   bash scripts/lockdown_key.sh /dev/ttyACM0
set -euo pipefail
if [ $# -ne 1 ]; then echo "Dùng: bash scripts/lockdown_key.sh PORT"; exit 2; fi
PORT="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export IDF_TOOLS_PATH="$ROOT/.tooling/esp-tools"
[ -f "$ROOT/.tooling/esp-idf/export.sh" ] || { echo "Thiếu .tooling/esp-idf."; exit 1; }
# shellcheck disable=SC1091
. "$ROOT/.tooling/esp-idf/export.sh" >/dev/null

doc_summary() {
  espefuse.py -p "$PORT" summary | tee "$TMPDIR/espefuse-summary-$1.txt"
  echo "(Đã lưu $TMPDIR/espefuse-summary-$1.txt)"
}
TMPDIR="${TMPDIR:-/tmp}"

echo ""
echo "BƯỚC 1/4: đọc trạng thái eFuse HIỆN TẠI (chỉ đọc, chưa đốt gì)."
doc_summary truoc
echo "Đối chiếu: chip mới thì Secure Boot và Flash Encryption đều CHƯA bật."
read -r -p "Nhấn Enter để tiếp tục. "
echo ""
echo "BƯỚC 2/4: flash bản hardened rồi boot lần đầu."
echo "  1. Mở web nạp, chọn gói pico-fido-v8.2-hardened, nạp qua cổng UART."
echo "  2. Rút ra cắm lại, chờ 30 giây cho lần boot đầu (bootloader tự mã"
echo "     hóa flash và không rút điện giữa chừng)."
read -r -p "Xong bước 2 thì nhấn Enter. "
echo ""
echo "BƯỚC 3/4: đọc lại eFuse, xác nhận đã khóa."
doc_summary sau
echo "Đối chiếu: Secure Boot phải BẬT, bộ đếm mã hóa flash phải LẺ (1, 3...)."
echo "Nếu chưa bật: kiểm tra lại đã nạp đúng file -hardened chưa, rồi boot lại."
read -r -p "Nhấn Enter để tiếp tục. "
echo ""
echo "BƯỚC 4/4 (TÙY CHỌN, MỘT CHIỀU, CẤM LÀM VỘI): khóa hẳn cổng nạp UART."
echo "  Đọc mục 'UART ROM download mode' trong tài liệu ESP-IDF v5.5.1"
echo "  (bản trong .tooling/esp-idf/docs) TRƯỚC KHI gõ bất kỳ lệnh đốt nào."
echo "  Khóa rồi thì không flash lại qua UART nữa — chỉ làm khi có key thứ 2"
echo "  chạy ổn và không còn nhu cầu cập nhật qua cổng này."
echo "Xong danh mục. Giữ lại 2 file summary để đối chiếu sau."
