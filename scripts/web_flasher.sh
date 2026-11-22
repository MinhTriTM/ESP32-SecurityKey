#!/usr/bin/env bash
# Mở siêu web nạp ESP32-S3: dựng server localhost rồi mở trình duyệt.
# Chạy từ thư mục gốc repo:  bash scripts/web_flasher.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ ! -f "$ROOT/web/index.html" ]; then
  echo "Không thấy web/index.html. Hãy chạy từ thư mục gốc repo."
  exit 1
fi
URL="http://localhost:8000/index.html"
echo "Mở $URL ..."
(xdg-open "$URL" 2>/dev/null || open "$URL" 2>/dev/null || echo "Hãy tự mở $URL bằng Chrome/Edge.") &
echo "Server chạy tại http://localhost:8000 (nhấn Ctrl+C để dừng)."
cd "$ROOT/web"
python3 -m http.server 8000
