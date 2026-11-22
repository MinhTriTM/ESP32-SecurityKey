#!/usr/bin/env bash
# Chạy mọi self-test Python của repo. Thoát mã != 0 nếu có test hỏng.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/.tooling/pylibs"
# pqc cần liboqs native trong .tooling/oqs (xem docstring tools/pqc.py).
export OQS_INSTALL_PATH="$ROOT/.tooling/oqs"
fail=0
for tool in secureio cborx lintsec fido_check hid_echo split_secret mnemonic vault pqc keymgr ml_distinguisher kanzo vien_nhip_tim vien_cong; do
  echo "=== $tool ==="
  python3 "tools/$tool.py" --self-test || fail=1
done
echo "=== web_firmware --check ==="
python3 tools/web_firmware.py --check || fail=1
exit $fail
