#!/usr/bin/env python3
"""Sinh khóa Flash Encryption riêng cho từng key (chạy 1 lần cho mỗi board).

Tạo keys/fe-key-<ten>.bin (32 byte ngẫu nhiên = khóa 256-bit cho AES-128-XTS,
đúng default CONFIG_SECURE_FLASH_ENCRYPTION_KEYSIZE của bản hardened). Mỗi
board dùng một khóa riêng theo khuyến cáo ESP-IDF. Đốt khóa vào eFuse TRƯỚC
lần boot mã hóa đầu tiên (xem runbook hardware/provision-runbook.md); nếu để
chip tự sinh thì khóa bị giấu vĩnh viễn và mất đường nạp lại (bài học key-01,
xem docs/research/11-cuu-key-01.md). Từ chối ghi đè khóa đã có.
"""
import argparse
import hashlib
import secrets
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".tooling" / "pylibs"))
sys.path.insert(0, str(ROOT / "tools"))
import secureio  # noqa: E402

KEY_BYTES = 32


def key_path(name: str) -> Path:
    safe = "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip("-_")
    if not safe or safe != name:
        raise ValueError("tên chỉ gồm chữ/số/gạch ngang/gạch dưới")
    return ROOT / "keys" / f"fe-key-{safe}.bin"


def generate(path: Path) -> str:
    if path.exists():
        raise FileExistsError(f"đã có {path}, không ghi đè")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = secrets.token_bytes(KEY_BYTES)
    secureio.write_secret_file(path, raw)
    return hashlib.sha256(raw).hexdigest()


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "fe-key-t.bin"
        fp1 = generate(p)
        if len(p.read_bytes()) != KEY_BYTES:
            print("self-test hỏng: sai độ dài khóa")
            return 1
        fp2 = hashlib.sha256(p.read_bytes()).hexdigest()
        if fp1 != fp2:
            print("self-test hỏng: vân tay không khớp")
            return 1
        try:
            generate(p)
        except FileExistsError:
            pass
        else:
            print("self-test hỏng: ghi đè được khóa đã có")
            return 1
        try:
            key_path("../x")
        except ValueError:
            pass
        else:
            print("self-test hỏng: lọt tên bẩn")
            return 1
    print("self-test ok: sinh 32 byte, vân tay khớp, chặn ghi đè và tên bẩn.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Sinh khóa flash encryption mỗi board một chiếc.")
    ap.add_argument("--name", help="tên key, ví dụ key-02")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.name:
        ap.print_usage()
        return 2
    try:
        path = key_path(args.name)
    except ValueError as exc:
        print(f"Tên không hợp lệ: {exc}")
        return 2
    try:
        fp = generate(path)
    except FileExistsError as exc:
        print(exc)
        return 1
    except OSError as exc:
        print(f"Không ghi được khóa: {exc}")
        return 1
    print(f"Đã tạo {path} (32 byte, AES-128-XTS).")
    print(f"Vân tay khóa (SHA-256): {fp}")
    print("BACKUP NGAY bằng vault + Shamir theo keys/README.md, rồi mới đốt vào eFuse.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
